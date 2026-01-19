from typing import List, Dict
from .context import ContextManager  # This import was missing - now added

def get_turn_prompt(
    history: List[Dict],
    current_speaker: str,
    opponent: str,
    turn_number: int,
    topic: str,
    max_tokens_guideline: str = "Aim for 400–700 tokens. Maximum: 1024 tokens."
) -> str:
    """
    Builds the structured prompt for each turn following v0.1 protocol
    """
    context_manager = ContextManager()
    for h in history:
        context_manager.add_turn(h["speaker"], h["content"], h["turn"])
    
    recent_context = context_manager.get_rolling_summary(last_n=5)
    delta = context_manager.get_disagreement_delta(last_n=3)
    
    synthesis_required = (turn_number % 5 == 0)
    
    prompt = f"""MIRROR MAX DEBATE - TURN {turn_number}
Topic: {topic}

Your role: {current_speaker}
Opponent role: {opponent}

RECENT CONTEXT (last 5 turns):
{recent_context}

DISAGREEMENT DELTA:
{delta}

DEBATE PROTOCOL v0.1 REQUIREMENTS:
1. [Reference:] Quote or paraphrase a specific point from opponent
2. [Claim:] State your position clearly
3. [Evidence/Reasoning:] Provide support (logic, data, patterns, examples)
4. [Crux-Question:] Identify core unresolved issue or ask a crux-oriented question
   (e.g. "What evidence would change your mind on X?")

OPTIONAL (use sparingly):
- [Steelman:] Charitable restatement of opponent's strongest point
- [Meta-Observation:] Brief comment on opponent's reasoning style/pattern

{"SYNTHESIS REQUIREMENT (every 5th turn): Include [Synthesis Attempt:] - Find common ground or clearly state irreconcilable difference." if synthesis_required else ""}

Be rigorous, charitable, and concise. Prioritize clarity over exhaustiveness.
{max_tokens_guideline}

Your response ({current_speaker}):
"""
    return prompt.strip()
