"""drivers/souldriver.py"""
import random
from typing import Dict
from core import LoreManifest
from presets import BoneConfig


class SoulDriver:
    """
    The SoulDriver acts as the 'Identity Intercept'.
    It translates the user's permanent psychological profile (The Soul) into
    biases that affect the Enneagram's persona selection. It ensures the machine
    resonates with the user's specific archetype and current state of 'dignity'.
    """

    def __init__(self, soul_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.soul = soul_ref
        self.archetype_weights = (LoreManifest.get_instance(config_ref=self.cfg).get(
            "DRIVER_CONFIG", "ARCHETYPE_TO_PERSONA_WEIGHT") or {})

    def get_influence(self) -> Dict[str, float]:
        """
        Calculates the weight modification for each persona based on the Soul's stats.
        Returns a dictionary of persona names and their calculated influence multipliers.
        """
        ennea_weights = (LoreManifest.get_instance(config_ref=self.cfg).get(
            "DRIVER_CONFIG", "ENNEAGRAM_WEIGHTS") or {})
        base_weights = {persona: 0.0 for persona in ennea_weights.keys()}
        if not self.soul:
            return base_weights
        archetype = getattr(self.soul, "archetype", "THE OBSERVER")
        mapping = self.archetype_weights.get(archetype, {"NARRATOR": 1.0})
        for persona, weight in mapping.items():
            if persona in base_weights:
                base_weights[persona] += weight
        paradox = getattr(self.soul, "paradox_accum", 0.0)
        chaos = min(0.5, (paradox - 5.0) * 0.05) if paradox > 5.0 else 0.0
        anchor = getattr(self.soul, "anchor", None)
        dignity = max(0.2, getattr(anchor, "dignity_reserve", 100.0) / 100.0) if anchor else 1.0
        return {p: (w + random.uniform(-chaos, chaos)) * dignity
                for p, w in base_weights.items()}
