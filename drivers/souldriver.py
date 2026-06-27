import random
from typing import Dict, Union

from core import LoreManifest
from presets import BoneConfig


class SoulDriver:
    def __init__(self, soul_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.soul = soul_ref
        manifest = LoreManifest.get_instance(config_ref=self.cfg)
        driver_cfg = manifest.get("DRIVER_CONFIG") or {}
        self.archetype_weights = driver_cfg.get("ARCHETYPE_TO_PERSONA_WEIGHT", {})
        self.ennea_weights = driver_cfg.get("ENNEAGRAM_WEIGHTS", {})

    def get_influence(self) -> Dict[str, Union[float, int]]:
        base_weights: Dict[str, Union[float, int]] = {
            str(persona): 0.0 for persona in self.ennea_weights.keys()
        }
        if not self.soul:
            return base_weights
        archetype = getattr(self.soul, "archetype", "THE OBSERVER")
        mapping = self.archetype_weights.get(archetype, {"NARRATOR": 1.0})
        for persona, weight in mapping.items():
            str_persona = str(persona)
            if str_persona in base_weights:
                base_weights[str_persona] += float(weight)
        paradox = getattr(self.soul, "paradox_accum", 0.0)
        chaos = min(0.5, (paradox - 5.0) * 0.05) if paradox > 5.0 else 0.0
        anchor = getattr(self.soul, "anchor", None)
        dignity = (
            max(0.2, getattr(anchor, "dignity_reserve", 100.0) / 100.0)
            if anchor
            else 1.0
        )
        return {
            p: (float(w) + random.uniform(-chaos, chaos)) * dignity
            for p, w in base_weights.items()
        }
