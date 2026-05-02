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

        # We load the 'Archetype-to-Persona' map.
        # This defines, for example, why a 'Hermit' archetype might
        # naturally summon a 'Gordon' (Boundary) persona more often.
        self.archetype_weights = (LoreManifest.get_instance(config_ref=self.cfg).get(
            "DRIVER_CONFIG", "ARCHETYPE_TO_PERSONA_WEIGHT") or {})

    def get_influence(self) -> Dict[str, float]:
        """
        Calculates the weight modification for each persona based on the Soul's stats.
        Returns a dictionary of persona names and their calculated influence multipliers.
        """
        # 1. Initialize the baseline (Pinker)
        ennea_weights = (LoreManifest.get_instance(config_ref=self.cfg).get(
            "DRIVER_CONFIG", "ENNEAGRAM_WEIGHTS") or {})
        base_weights = {persona: 0.0 for persona in ennea_weights.keys()}

        # If no soul is present, we provide zero influence, allowing the physics
        # engine to have total control.
        if not self.soul:
            return base_weights

        # 2. Archetype Mapping (Fuller)
        # We pull the user's current identity. Defaults to 'THE OBSERVER'.
        archetype = getattr(self.soul, "archetype", "THE OBSERVER")
        mapping = self.archetype_weights.get(archetype, {"NARRATOR": 1.0})

        # Map the Archetype's natural preferences into our baseline weights.
        for persona, weight in mapping.items():
            if persona in base_weights:
                base_weights[persona] += weight

        # 3. Paradox Accumulation & Chaos (Meadows)
        # 'paradox_accum' tracks how many contradictions the user is currently holding.
        # Once it passes a threshold (5.0), it introduces 'Chaos'.
        paradox = getattr(self.soul, "paradox_accum", 0.0)

        # Chaos represents stochastic noise. The more paradox a user holds,
        # the more unpredictable the machine's persona becomes.
        chaos = min(0.5, (paradox - 5.0) * 0.05) if paradox > 5.0 else 0.0

        # 4. Dignity Dampening (Schur)
        # We look at the user's 'dignity_reserve'.
        # If dignity is high, the persona weights are clear.
        # If dignity is low (the user is unregulated), we dampen the weights (min 0.2)
        # to prevent the system from over-reacting to an unstable state.
        anchor = getattr(self.soul, "anchor", None)
        dignity = max(0.2, getattr(anchor, "dignity_reserve", 100.0) / 100.0) if anchor else 1.0

        # 5. Final Synthesis
        # We apply the chaos variance and the dignity multiplier to every weight.
        # This is the 'Heuristic' that keeps the system feeling alive and human.
        return {p: (w + random.uniform(-chaos, chaos)) * dignity
                for p, w in base_weights.items()}
