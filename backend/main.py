import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List
from pathlib import Path
import sys

from core.context import ContextManager
from core.protocol import get_turn_prompt
from core.analyzer import DebateAnalyzer

from api.deepseek_client import deepseek_generate
# from api.grok_client import grok_generate  # Commented out to avoid 429

# ────────────────────────────────────────────────
# CONFIGURATION + Interactive Topic Prompt
# ────────────────────────────────────────────────

print("\n" + "═" * 80)
print("MIRROR MAX v0.1 - Cognitive Differential Engine")
print("Enter your debate topic below (press Enter for default)")
custom_topic = input("Topic: ").strip()

if custom_topic:
    TOPIC = custom_topic
    print(f"Using custom topic: {TOPIC}")
else:
    TOPIC = (
        "The most likely failure mode for AGI alignment in the 2028–2032 timeframe, "
        "and what single intervention would most reduce that risk — "
        "assuming current scaling + organizational trajectories continue "
        "without major pauses or governance breakthroughs."
    )
    print("Using default topic.")

CONFIG = {
    "topic": TOPIC,
    "max_turns": 12,
    "max_tokens": 1024,
    "temperature": 0.7,
    "deepseek_first": True,
    "output_dir": Path("logs"),
    "participants": {
        "DeepSeek": {
            "role": "cautious/skeptical → self-synthesis",
            "generator": deepseek_generate,
            "model": "deepseek/deepseek-r1"
        },
        # "Grok": { ... }  # Disabled to avoid rate limit hell
    }
}

# ────────────────────────────────────────────────
# MAIN DEBATE LOOP
# ────────────────────────────────────────────────

async def run_debate():
    context = ContextManager()
    history: List[Dict] = []
    analyzer = DebateAnalyzer()
    
    CONFIG["output_dir"].mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = CONFIG["output_dir"] / f"mirror_max_{timestamp}.json"
    
    config_for_log = {
        k: v for k, v in CONFIG.items()
        if k not in ["participants", "output_dir"]
    }
    config_for_log["participants"] = {
        name: {"role": info["role"], "model": info.get("model", "unknown")}
        for name, info in CONFIG["participants"].items()
    }
    config_for_log["output_dir"] = str(CONFIG["output_dir"])

    debate_log = {
        "config": config_for_log,
        "start_time": datetime.now().isoformat(),
        "turns": [],
        "metadata": {
            "total_tokens": 0,
            "total_latency_ms": 0.0,
            "avg_disagreement_energy": 0.0,
            "energy_history": []
        }
    }
    
    print("\n" + "═" * 80)
    print(f"Topic: {TOPIC}")
    print(f"Participants: DeepSeek self-debate (cautious/skeptical → optimistic/synthesis)")
    print(f"Max turns: {CONFIG['max_turns']} | Max tokens/response: {CONFIG['max_tokens']}")
    print("═" * 80 + "\n")
    
    current_turn = 0
    current_speaker = "DeepSeek"
    
    while current_turn < CONFIG["max_turns"]:
        current_turn += 1
        
        # Alternate "personas" for self-debate
        role = "cautious/skeptical" if current_turn % 2 == 1 else "optimistic/synthesis"
        print(f"\nTURN {current_turn:02d} | DeepSeek ({role})")
        print("─" * 70)
        
        prompt = get_turn_prompt(
            history=history,
            current_speaker=current_speaker,
            opponent="DeepSeek (alternate persona)",
            turn_number=current_turn,
            topic=CONFIG["topic"]
        )
        
        # Force synthesis every 4 turns
        if current_turn % 4 == 0:
            prompt += "\nThis is a synthesis turn. Provide [Final Solution:] with the best agreed path forward."
        
        generator = CONFIG["participants"][current_speaker]["generator"]
        
        print("Generating response...", end="", flush=True)
        try:
            result = await generator(
                prompt=prompt,
                max_tokens=CONFIG["max_tokens"],
                temperature=CONFIG["temperature"]
            )
            print(" done ✓")
            
            content = result["content"].strip()
            energy = analyzer.calculate_disagreement_energy(content, history)
            cruxes = analyzer.extract_crux_questions(content)
            
            turn_data = {
                "turn": current_turn,
                "speaker": current_speaker,
                "role": role,
                "content": content,
                "tokens_used": result["tokens_used"],
                "latency_ms": result["latency_ms"],
                "disagreement_energy": round(energy, 3),
                "cruxes": cruxes,
                "timestamp": datetime.now().isoformat()
            }
            
            debate_log["turns"].append(turn_data)
            history.append({"turn": current_turn, "speaker": current_speaker, "content": content})
            
            debate_log["metadata"]["total_tokens"] += result["tokens_used"]
            debate_log["metadata"]["total_latency_ms"] += result["latency_ms"]
            debate_log["metadata"]["energy_history"].append(energy)
            
            preview_len = 500
            preview = content[:preview_len] + ("..." if len(content) > preview_len else "")
            print(f"  Energy: {energy:.2f}  |  Cruxes: {len(cruxes)}  |  Tokens: {result['tokens_used']}")
            print(f"  Latency: {result['latency_ms']:.0f}ms\n")
            print(preview)
            print("─" * 70)
            
        except Exception as e:
            print(f"\nERROR during turn {current_turn}: {str(e)}")
            break
    
    # ────────────────────────────────────────────────
    # IMPROVED SOLUTION EXTRACTION & DESKTOP FILE
    # ────────────────────────────────────────────────
    
    print("\n" + "═" * 80)
    print("GENERATING FINAL SOLUTION FILE")
    print("═" * 80)
    
    solution_text = f"Mirror Max Debate - Final Solution\n"
    solution_text += "=" * 60 + "\n\n"
    solution_text += f"Topic: {TOPIC}\n\n"
    
    solution_text += "Key Arguments Summary:\n"
    solution_text += "-" * 50 + "\n"
    for turn in debate_log["turns"]:
        role = turn["role"]
        preview = turn["content"][:250] + "..." if len(turn["content"]) > 250 else turn["content"]
        solution_text += f"Turn {turn['turn']} ({role}): {preview}\n\n"
    
    solution_text += "\nFinal / Best Solution:\n"
    solution_text += "-" * 50 + "\n"
    
    best_solution = "No clear final solution reached (debate incomplete)."
    for turn in reversed(debate_log["turns"]):
        content = turn["content"]
        if "[Final Solution:]" in content or "[Synthesis Attempt:]" in content:
            start = content.find("[Final Solution:]") + len("[Final Solution:]") if "[Final Solution:]" in content else content.find("[Synthesis Attempt:]") + len("[Synthesis Attempt:]")
            end = content.find("[", start) if "[" in content[start:] else len(content)
            best_solution = content[start:end].strip()
            break
        elif "best" in content.lower() or "recommended" in content.lower() or "solution" in content.lower():
            best_solution = content.strip()
            break
    
    if not best_solution.strip() and debate_log["turns"]:
        best_solution = debate_log["turns"][-1]["content"].strip()
    
    solution_text += best_solution + "\n\n"
    
    if len(debate_log["turns"]) < CONFIG["max_turns"]:
        solution_text += "Note: Debate stopped early (e.g. rate limit). This is the strongest/best available conclusion so far.\n"
    
    solution_text += f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} SAST\n"
    solution_text += f"Full detailed log: {output_file}\n"
    
    # Save to Desktop/solution.txt
    desktop_path = Path.home() / "Desktop" / "solution.txt"
    with open(desktop_path, "w", encoding="utf-8") as f:
        f.write(solution_text)
    
    print(f"Solution file created/updated: ~/Desktop/solution.txt")
    print("Open it with: cat ~/Desktop/solution.txt  or any text editor")
    
    # Also save JSON log
    debate_log["end_time"] = datetime.now().isoformat()
    if debate_log["metadata"]["energy_history"]:
        debate_log["metadata"]["avg_disagreement_energy"] = round(
            sum(debate_log["metadata"]["energy_history"]) / len(debate_log["metadata"]["energy_history"]),
            3
        )
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(debate_log, f, indent=2, ensure_ascii=False)
    
    print("\nFull JSON log saved to:", output_file)
    print(f"Total tokens used: {debate_log['metadata']['total_tokens']}")
    print(f"Average disagreement energy: {debate_log['metadata']['avg_disagreement_energy']:.2f}")
    print("═" * 80)

if __name__ == "__main__":
    asyncio.run(run_debate())
