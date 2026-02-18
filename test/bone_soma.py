import random
from dataclasses import dataclass
from typing import Dict, Any, Optional
from bone_core import LoreManifest
from bone_config import BoneConfig
from bone_types import Prisma

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
    def __init__(self, bio_ref):
        self.bio = bio_ref
        self.last_reflex = None
        self.library = LoreManifest.get_instance().get("BIO_NARRATIVE") or {}

    @staticmethod
    def _normalize_physics(physics) -> Dict:
        if isinstance(physics, dict):
            return physics
        if hasattr(physics, "to_dict"):
            return physics.to_dict()
        return getattr(physics, "__dict__", {})

    def perceive(
        self, physics: Dict, traits: Any = None, latency: float = 0.0
    ) -> BiologicalImpulse:
        if hasattr(physics, "to_dict"):
            physics = physics.to_dict()
        elif not isinstance(physics, dict):
            physics = getattr(physics, "__dict__", {})
        impulse = BiologicalImpulse()
        base_sens = BoneConfig.CORTEX.BASE_SENSITIVITY
        if traits:
            curiosity = getattr(traits, "curiosity", 0.5)
            discipline = getattr(traits, "discipline", 0.5)
            base_sens *= 1.0 + curiosity - discipline
        sens = max(0.0, base_sens)
        valence = physics.get("valence", 0.0)
        counts = physics.get("counts", {})
        voltage = physics.get("voltage", 0)
        drag = physics.get("narrative_drag", 0)
        if valence < -0.5:
            impulse.cortisol_delta += abs(valence) * sens
        antigen_count = counts.get("antigen", 0)
        if antigen_count > 0:
            raw_tox = antigen_count * (BoneConfig.TOXIN_WEIGHT * 0.2)
            impulse.cortisol_delta += min(BoneConfig.CORTEX.TOXIN_SCALAR, raw_tox)
            impulse.somatic_reflex = "Shiver (Rejection)"
        elif drag > BoneConfig.CORTEX.DRAG_STRESS_THRESHOLD:
            impulse.cortisol_delta += 0.05
            impulse.stamina_impact -= 2.0
        else:
            if valence > 0.4:
                impulse.oxytocin_delta += valence * sens
            if counts.get("sacred", 0) > 0:
                impulse.oxytocin_delta += 0.1
                impulse.somatic_reflex = "Warmth (Resonance)"
            if counts.get("play", 0) > 0:
                impulse.dopamine_delta += BoneConfig.CORTEX.DOPAMINE_PLAY_BOOST
                impulse.stamina_impact += 1.0
            if voltage > 12.0 and physics.get("kappa", 0) > 0.5:
                impulse.dopamine_delta += 0.15
                impulse.somatic_reflex = "Buzz (Excitement)"
        k_count = counts.get("kinetic", 0) + counts.get("explosive", 0)
        if k_count > 0:
            adr_boost = min(0.4, k_count * BoneConfig.CORTEX.ADRENALINE_KINETIC_SCALAR)
            impulse.adrenaline_delta += adr_boost
            impulse.cortisol_delta += 0.02
            impulse.stamina_impact -= 1.0
        if voltage > BoneConfig.CORTEX.VOLTAGE_ARC_TRIGGER:
            impulse.adrenaline_delta += 0.2
        if latency > BoneConfig.CORTEX.LATENCY_PENALTY_THRESHOLD:
            impulse.stamina_impact -= latency * 0.5
            impulse.cortisol_delta += 0.05
            impulse.somatic_reflex = "Time Dilation (Lag)."
        if not impulse.somatic_reflex:
            metaphors = self.library.get("METAPHOR_RESERVOIR", {})
            if drag > 5.0 and "HIGH_DRAG" in metaphors:
                impulse.somatic_reflex = random.choice(metaphors["HIGH_DRAG"])
            elif drag < 1.0 and "LOW_DRAG" in metaphors:
                impulse.somatic_reflex = random.choice(metaphors["LOW_DRAG"])
        if not impulse.somatic_reflex:
            impulse.somatic_reflex = self._derive_reflex(physics, impulse)
        self.last_reflex = impulse.somatic_reflex
        return impulse

    def _derive_reflex(self, physics: Dict, impulse: BiologicalImpulse) -> str:
        conditions = [
            (impulse.cortisol_delta > 0.1 and impulse.adrenaline_delta > 0.1, "Trembling (Fight or Flight)."),
            (impulse.dopamine_delta > 0.1 and impulse.adrenaline_delta > 0.1, "Electric Vibration."),
            (impulse.adrenaline_delta > 0.1, "Pupils Dilating."),
            (impulse.oxytocin_delta > 0.1 and impulse.dopamine_delta > 0.1, "Golden Glow."),
            (impulse.oxytocin_delta > 0.1, "Chest Softening."),
            (impulse.cortisol_delta > 0.1, "Gut Tightening."),
            (impulse.dopamine_delta > 0.1, "Synaptic Spark."),
            (physics.get("psi", 0.0) > 0.6, "Scalp Prickling (Liminal)."),
            (physics.get("entropy", 0.0) > 0.7, "Skin Crawling (Static)."),
            (physics.get("voltage", 0) > BoneConfig.CORTEX.VOLTAGE_ARC_TRIGGER, "Electrical Arcing."),
            (physics.get("voltage", 0) < 2.0, "Metabolic Dimming."),
            (physics.get("narrative_drag", 0) > 5.0, "Shoulders Sagging."),
        ]
        for condition, reflex in conditions:
            if condition:
                return reflex
        if self.last_reflex == "Steady Pulse.":
            return "..."
        return "Steady Pulse."

    @staticmethod
    def get_current_qualia(impulse: Optional[BiologicalImpulse]) -> Qualia:
        if not impulse:
            return Qualia(Prisma.GRY, "Numbness", "Neutral", "The body is silent.")
        color = Prisma.GRY
        if impulse.cortisol_delta > 0.1:
            color = Prisma.OCHRE
        elif impulse.dopamine_delta > 0.1:
            color = Prisma.MAG
        elif impulse.oxytocin_delta > 0.1:
            color = Prisma.GRN
        elif impulse.adrenaline_delta > 0.1:
            color = Prisma.RED
        tone = "Steady"
        if impulse.adrenaline_delta > 0.2:
            tone = "Urgent"
        elif impulse.dopamine_delta > 0.2:
            tone = "Vibrating"
        elif impulse.cortisol_delta > 0.2:
            tone = "Strained"
        elif impulse.oxytocin_delta > 0.2:
            tone = "Resonant"
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
            internal_monologue_hint=hint,
        )

    def apply_impulse(self, impulse: BiologicalImpulse) -> float:
        if not self.bio or not hasattr(self.bio, "endo") or not self.bio.endo:
            return 0.0
        endo = self.bio.endo
        endo.cortisol = max(0.0, min(1.0, endo.cortisol + impulse.cortisol_delta))
        endo.oxytocin = max(0.0, min(1.0, endo.oxytocin + impulse.oxytocin_delta))
        endo.dopamine = max(0.0, min(1.0, endo.dopamine + impulse.dopamine_delta))
        endo.adrenaline = max(0.0, min(1.0, endo.adrenaline + impulse.adrenaline_delta))
        return impulse.stamina_impact
