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

@dataclass
class Qualia:
    color_code: str
    somatic_sensation: str
    tone: str
    internal_monologue_hint: str

class SynestheticCortex:
    SENSITIVITY = 0.1

    def __init__(self, bio_ref):
        self.bio = bio_ref
        self.last_reflex = None

    def _normalize_physics(self, physics) -> Dict:
        if isinstance(physics, dict): return physics
        if hasattr(physics, "to_dict"): return physics.to_dict()
        return getattr(physics, "__dict__", {})

    def perceive(self, physics: Dict, text: str = "") -> BiologicalImpulse:
        physics = self._normalize_physics(physics)
        impulse = BiologicalImpulse()
        valence = physics.get("valence", 0.0)
        clean_words = physics.get("clean_words", [])
        counts = physics.get("counts", {})
        is_toxic = False
        if valence < -0.5:
            impulse.cortisol_delta += abs(valence) * self.SENSITIVITY
        if counts.get("antigen", 0) > 0:
            raw_tox = counts["antigen"] * 0.2
            impulse.cortisol_delta += min(0.4, raw_tox)
            impulse.somatic_reflex = "Shiver (Rejection)"
            is_toxic = True
        if physics.get("narrative_drag", 0) > 8.0:
            impulse.cortisol_delta += 0.05
            impulse.stamina_impact -= 2.0
        if not is_toxic:
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
        self.last_reflex = impulse.somatic_reflex
        return impulse

    def _derive_reflex(self, physics: Dict, impulse: BiologicalImpulse) -> str:
        high_adr = impulse.adrenaline_delta > 0.1
        high_cort = impulse.cortisol_delta > 0.1
        high_dop = impulse.dopamine_delta > 0.1
        high_oxy = impulse.oxytocin_delta > 0.1
        if high_adr and high_cort:
            return "Trembling (Fight or Flight)."
        if high_adr and high_dop:
            return "Electric Vibration."
        if high_oxy and high_dop:
            return "Golden Glow."
        if high_adr: return "Pupils Dilating."
        if high_cort: return "Gut Tightening."
        if high_oxy: return "Chest Softening."
        if high_dop: return "Synaptic Spark."
        vol = physics.get("voltage", 0)
        if vol > 15.0: return "Electrical Arcing."
        if vol < 2.0: return "Metabolic Dimming."
        drag = physics.get("narrative_drag", 0)
        if drag > 5.0: return "Shoulders Sagging."
        if self.last_reflex == "Steady Pulse.":
            return "..."
        return "Steady Pulse."

    def get_current_qualia(self, impulse: BiologicalImpulse) -> Qualia:
        if not impulse:
            return Qualia(Prisma.GRY, "Numbness", "Neutral", "The body is silent.")
        color = Prisma.GRY
        if impulse.cortisol_delta > 0.1: color = Prisma.OCHRE
        elif impulse.dopamine_delta > 0.1: color = Prisma.MAG
        elif impulse.oxytocin_delta > 0.1: color = Prisma.GRN
        elif impulse.adrenaline_delta > 0.1: color = Prisma.RED
        tone = "Steady"
        if impulse.adrenaline_delta > 0.2: tone = "Urgent"
        elif impulse.dopamine_delta > 0.2: tone = "Vibrating"
        elif impulse.cortisol_delta > 0.2: tone = "Strained"
        elif impulse.oxytocin_delta > 0.2: tone = "Resonant"
        hint = "Observe."
        if impulse.cortisol_delta > 0.05:
            hint = "Something is wrong. Be guarded."
        elif impulse.adrenaline_delta > 0.05:
            hint = "Move fast. Don't overthink."
        elif impulse.oxytocin_delta > 0.05:
            hint = "Connect. Be vulnerable."
        elif impulse.dopamine_delta > 0.05:
            hint = "Explore. Find the pattern."
        return Qualia(
            color_code=color,
            somatic_sensation=impulse.somatic_reflex or "Steady Pulse.",
            tone=tone,
            internal_monologue_hint=hint)

    def apply_impulse(self, impulse: BiologicalImpulse) -> float:
        if not self.bio:
            return 0.0
        endo = self.bio.endo
        endo.cortisol = max(0.0, min(1.0, endo.cortisol + impulse.cortisol_delta))
        endo.oxytocin = max(0.0, min(1.0, endo.oxytocin + impulse.oxytocin_delta))
        endo.dopamine = max(0.0, min(1.0, endo.dopamine + impulse.dopamine_delta))
        endo.adrenaline = max(0.0, min(1.0, endo.adrenaline + impulse.adrenaline_delta))
        return impulse.stamina_impact