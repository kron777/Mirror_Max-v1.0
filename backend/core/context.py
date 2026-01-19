# backend/core/context.py
from typing import List, Dict

class ContextManager:
    """Manages rolling context, summaries and disagreement tracking"""
    
    def __init__(self):
        self.history: List[Dict] = []  # full history of turns
        
    def add_turn(self, speaker: str, content: str, turn_number: int):
        self.history.append({
            "turn": turn_number,
            "speaker": speaker,
            "content": content
        })
    
    def get_rolling_summary(self, last_n: int = 5) -> str:
        """Generate a concise rolling summary of recent exchanges"""
        recent = self.history[-last_n:]
        if not recent:
            return "[No prior exchanges - opening statements]"
        
        lines = []
        for turn in recent:
            preview = turn["content"][:180].replace("\n", " ").strip()
            lines.append(f"Turn {turn['turn']} ({turn['speaker']}): {preview}...")
        return "\n".join(lines)
    
    def get_disagreement_delta(self, last_n: int = 3) -> str:
        """Extract potential unresolved cruxes (basic version - improve later)"""
        if len(self.history) < 2:
            return "No disagreements yet - initial statements only"
        
        recent = self.history[-last_n:]
        cruxes = []
        for turn in recent:
            if "[Crux-Question:]" in turn["content"]:
                # Very simple extraction - can use regex later
                start = turn["content"].find("[Crux-Question:]") + 16
                end = turn["content"].find("[", start) if "[" in turn["content"][start:] else len(turn["content"])
                crux = turn["content"][start:end].strip()
                if crux:
                    cruxes.append(crux[:120] + "..." if len(crux) > 120 else crux)
        
        if not cruxes:
            return "No explicit crux questions identified in recent turns"
        return "Recent cruxes / disagreements:\n• " + "\n• ".join(cruxes)
