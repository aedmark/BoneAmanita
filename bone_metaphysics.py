""" bone_metaphysics.py - The Unwritten Core & Cognitive Instrumentation """

from typing import Dict, Any, List, Optional
from bone_bus import Prisma, BoneConfig, RealityLayer

class CongruenceValidator:
    def __init__(self):
        self.last_phi = 1.0

    def calculate_resonance(self, text: str, context: Any) -> float:
        if not text: return 0.0
        archetype = getattr(context, "active_lens", "OBSERVER").upper()
        tone_score = self._check_tone_alignment(text, archetype)
        bio_conflict = self._check_bio_conflict(text, context)
        layer_confusion = self._check_layer_confusion(text, context.reality_stack.current_depth)
        phi = 1.0 - (abs(tone_score - 1.0) + bio_conflict + layer_confusion)
        self.last_phi = max(0.0, min(1.0, phi))
        return self.last_phi

    def _check_tone_alignment(self, text: str, archetype: str) -> float:
        text_lower = text.lower()
        keywords = {
            "POET": ["light", "dark", "soul", "dream", "fade", "echo"],
            "ENGINEER": ["system", "voltage", "drag", "efficiency", "structure"],
            "NIHILIST": ["void", "pointless", "entropy", "end", "silence"],
            "CRITIC": ["derivative", "pacing", "structure", "flawed"],}
        target_words = keywords.get(archetype.replace("THE ", ""), [])
        if not target_words: return 1.0
        hit_count = sum(1 for w in target_words if w in text_lower)
        if hit_count > 0: return 1.0
        return 0.8

    def _check_bio_conflict(self, text: str, context: Any) -> float:
        if hasattr(context, "bio_result"):
            cortisol = context.bio_result.get("chemistry", {}).get("cortisol", 0.0)
            if cortisol > 0.8 and any(w in text.lower() for w in ["calm", "peace", "steady"]):
                return 0.3
        return 0.0

    def _check_layer_confusion(self, text: str, depth: int) -> float:
        is_code = "{" in text and "}" in text and ":" in text
        if depth == RealityLayer.SIMULATION and is_code:
            return 0.5
        return 0.0