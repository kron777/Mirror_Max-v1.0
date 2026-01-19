# backend/core/analyzer.py
import re
from typing import List, Dict

class DebateAnalyzer:
    """Tools for calculating disagreement energy and extracting insights"""
    
    @staticmethod
    def calculate_disagreement_energy(turn_content: str, previous_turns: List[Dict]) -> float:
        """
        Simple heuristic-based disagreement energy (0.0–1.0)
        Higher = more productive tension
        """
        energy = 0.45  # neutral baseline
        
        text_lower = turn_content.lower()
        
        # Bonuses for active engagement
        counter_markers = ['however', 'but', 'although', 'disagree', 'challenge', 'counter', 'however', 'yet', 'on the other hand']
        for marker in counter_markers:
            if marker in text_lower:
                energy += 0.08
        
        if '[steelman]' in text_lower:
            energy += 0.06
        
        if '[meta-observation]' in text_lower:
            energy += 0.04
        
        # Bonus for explicit crux
        if '[crux-question]' in text_lower:
            energy += 0.07
        
        # Penalty for excessive agreement without substance
        agreement_markers = ['i agree', 'exactly', 'correct', 'you are right', 'indeed']
        for marker in agreement_markers:
            if marker in text_lower:
                energy -= 0.04
        
        # Cap
        return max(0.0, min(1.0, energy))
    
    @staticmethod
    def extract_crux_questions(content: str) -> List[str]:
        """Extract all [Crux-Question:] blocks"""
        pattern = r'\[Crux-Question:\]\s*(.*?)(?=\[|$|\n\s*\n)'
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        return [m.strip() for m in matches if m.strip()]
