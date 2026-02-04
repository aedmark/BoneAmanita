""" bone_synesthesia.py
 'I feel what you speak. Your words are touching the wire.' """

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from bone_bus import Prisma, BoneConfig
from bone_lexicon import TheLexicon

@dataclass
class BiologicalImpulse:
    cortisol_delta: float = 0.0
    oxytocin_delta: float = 0.0
    dopamine_delta: float = 0.0
    adrenaline_delta: float = 0.0
    stamina_impact: float = 0.0
    somatic_reflex: str = ""

class SynestheticCortex:
    SENSITIVITY = 0.1

    def __init__(self, bio_ref):
        self.bio = bio_ref
        self.last_reflex = None

    def perceive(self, physics: Dict, text: str = "") -> BiologicalImpulse:
        if not isinstance(physics, dict):
            if hasattr(physics, "to_dict"):
                physics = physics.to_dict()
            elif hasattr(physics, "__dict__"):
                physics = physics.__dict__
            else:
                physics = {}
        impulse = BiologicalImpulse()
        valence = physics.get("valence", 0.0)
        clean_words = physics.get("clean_words", [])
        counts = physics.get("counts", {})
        if valence < -0.5:
            impulse.cortisol_delta += abs(valence) * self.SENSITIVITY
        if counts.get("antigen", 0) > 0:
            impulse.cortisol_delta += (counts["antigen"] * 0.2)
            impulse.somatic_reflex = "Shiver (Rejection)"
        if physics.get("narrative_drag", 0) > 8.0:
            impulse.cortisol_delta += 0.05
            impulse.stamina_impact -= 2.0
        if valence > 0.4:
            impulse.oxytocin_delta += valence * self.SENSITIVITY
        if counts.get("suburban", 0) > 0:
            impulse.oxytocin_delta += 0.05
        if counts.get("sacred", 0) > 0:
            impulse.oxytocin_delta += 0.1
            impulse.somatic_reflex = "Warmth (Resonance)"
        if counts.get("play", 0) > 0:
            impulse.dopamine_delta += 0.1
            impulse.stamina_impact += 1.0
        if physics.get("voltage", 0) > 12.0 and physics.get("kappa", 0) > 0.5:
            impulse.dopamine_delta += 0.15
            impulse.somatic_reflex = "Buzz (Excitement)"
        k_count = counts.get("kinetic", 0) + counts.get("explosive", 0)
        if k_count > 0:
            adr_boost = min(0.4, k_count * 0.08)
            impulse.adrenaline_delta += adr_boost
            impulse.cortisol_delta += 0.02
            impulse.stamina_impact -= 1.0
        if physics.get("voltage", 0) > 15.0:
            impulse.adrenaline_delta += 0.2
        if not impulse.somatic_reflex:
            impulse.somatic_reflex = self._derive_reflex(physics, impulse)
        return impulse

    def _derive_reflex(self, physics: Dict, impulse: BiologicalImpulse) -> str:
        if impulse.adrenaline_delta > 0.1:
            return "Pupils Dilating."
        if impulse.cortisol_delta > 0.1:
            return "Gut Tightening."
        if impulse.oxytocin_delta > 0.1:
            return "Chest Softening."
        if impulse.dopamine_delta > 0.1:
            return "Synaptic Spark."
        vol = physics.get("voltage", 0)
        if vol > 15.0: return "Electrical Arcing."
        if vol < 2.0: return "Metabolic Dimming."
        drag = physics.get("narrative_drag", 0)
        if drag > 5.0: return "Shoulders Sagging."
        return "Steady Pulse."

    def apply_impulse(self, impulse: BiologicalImpulse) -> float:
        if not self.bio:
            return 0.0
        endo = self.bio.endo
        endo.cortisol = max(0.0, min(1.0, endo.cortisol + impulse.cortisol_delta))
        endo.oxytocin = max(0.0, min(1.0, endo.oxytocin + impulse.oxytocin_delta))
        endo.dopamine = max(0.0, min(1.0, endo.dopamine + impulse.dopamine_delta))
        endo.adrenaline = max(0.0, min(1.0, endo.adrenaline + impulse.adrenaline_delta))
        return impulse.stamina_impact