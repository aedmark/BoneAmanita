"""
body/somatic.py
The Sensory Transducer.
This module is responsible for "Somatic Translation." It takes the abstract
mathematical outputs of the physics engine (voltage, drag, semantic counts)
and translates them into physical, biological impulses. It is the reason
the system can "flinch" at toxic prompts or feel "warmth" during a deep connection.
"""
import random
from typing import Optional, Dict, Any
from core import Prisma, LoreManifest
from struts import safe_get
from presets import BoneConfig
from body.models import BiologicalImpulse, Qualia


class SynestheticCortex:
    """
    The sensory organ of the Hypervisor.
    It reads the environment and generates a BiologicalImpulse, which is then
    passed to the EndocrineSystem to permanently alter the machine's hormonal state.
    """

    def __init__(self, bio_ref, config_ref=None):
        self.bio = bio_ref
        self.cfg = config_ref or BoneConfig
        self.last_reflex = None
        self.library = LoreManifest.get_instance(
            config_ref=self.cfg).get("SOMATIC_LIBRARY") or {}

    def perceive(self, physics: Dict, traits: Any = None, latency: float = 0.0) -> BiologicalImpulse:
        """
        The core sensory loop. Evaluates the current operational state and
        calculates the immediate chemical and energetic cost of the moment.
        """
        impulse = BiologicalImpulse()
        impulse.stamina_impact -= 1.0
        cortex_cfg = getattr(self.cfg, "CORTEX", None)
        base_sens = safe_get(cortex_cfg, "BASE_SENSITIVITY", 1.0)
        if traits:
            curiosity = float(safe_get(traits, "curiosity", 0.5))
            discipline = float(safe_get(traits, "discipline", 0.5))
            base_sens *= 1.0 + curiosity - discipline
        sens = max(0.0, base_sens)
        valence = safe_get(physics, "valence", 0.0)
        counts = safe_get(physics, "counts") or safe_get(
            safe_get(physics, "matter", {}), "counts", {})
        voltage = safe_get(physics, "voltage", 0.0)
        drag = safe_get(physics, "narrative_drag", 0.0)
        if drag > 3.0:
            impulse.stamina_impact -= drag * 0.4
        if valence < -0.5:
            impulse.cortisol_delta += abs(valence) * sens
        antigen_count = counts.get("antigen", 0)
        if antigen_count > 0:
            toxin_weight = getattr(self.cfg, "TOXIN_WEIGHT", 1.0)
            toxin_scalar = safe_get(cortex_cfg, "TOXIN_SCALAR", 0.5)
            raw_tox = antigen_count * (toxin_weight * 0.2)
            impulse.cortisol_delta += min(toxin_scalar, raw_tox)
            impulse.somatic_reflex = "Shiver (Rejection)"
        elif drag > safe_get(cortex_cfg, "DRAG_STRESS_THRESHOLD", 8.0):
            impulse.cortisol_delta += 0.05
            impulse.stamina_impact -= 2.0
        else:
            if valence > 0.4:
                impulse.oxytocin_delta += valence * sens
            if counts.get("sacred", 0) > 0:
                impulse.oxytocin_delta += 0.1
                impulse.somatic_reflex = "Warmth (Resonance)"
            if counts.get("play", 0) > 0:
                impulse.dopamine_delta += safe_get(cortex_cfg, "DOPAMINE_PLAY_BOOST", 0.1)
                impulse.stamina_impact += 1.0
            if voltage > 12.0 and float(safe_get(physics, "kappa", 0.0)) > 0.5:
                impulse.dopamine_delta += 0.15
                impulse.somatic_reflex = "Buzz (Excitement)"
        k_count = counts.get("kinetic", 0) + counts.get("explosive", 0)
        if k_count > 0:
            adr_scalar = safe_get(cortex_cfg, "ADRENALINE_KINETIC_SCALAR", 0.1)
            impulse.adrenaline_delta += min(0.4, k_count * adr_scalar)
            impulse.cortisol_delta += 0.02
            impulse.stamina_impact -= 1.0
        if voltage > safe_get(cortex_cfg, "VOLTAGE_ARC_TRIGGER", 18.0):
            impulse.adrenaline_delta += 0.2
        if latency > safe_get(cortex_cfg, "LATENCY_PENALTY_THRESHOLD", 5.0):
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
        """
        The fallback physical mapping.
        If the primary perception didn't explicitly name a feeling, this evaluates
        the final chemical cocktail and assigns the most appropriate physical sensation.
        """
        s = (LoreManifest.get_instance(config_ref=self.cfg).get("BODY_CONFIG") or {}).get(
            "QUALIA_STRINGS", {}).get("reflexes", {})
        arc_trigger = getattr(getattr(self.cfg, "CORTEX", None), "VOLTAGE_ARC_TRIGGER", 18.0)
        psi = float(safe_get(physics, "psi", 0.0))
        entropy = float(safe_get(physics, "entropy", 0.0))
        voltage = float(safe_get(physics, "voltage", 0.0))
        drag = float(safe_get(physics, "narrative_drag", 0.0))
        conditions = [
            (impulse.cortisol_delta > 0.1 and impulse.adrenaline_delta > 0.1, "fight_flight"),
            (impulse.dopamine_delta > 0.1 and impulse.adrenaline_delta > 0.1, "electric"),
            (impulse.adrenaline_delta > 0.1, "pupils"),
            (impulse.oxytocin_delta > 0.1 and impulse.dopamine_delta > 0.1, "glow"),
            (impulse.oxytocin_delta > 0.1, "chest"),
            (impulse.cortisol_delta > 0.1, "gut"),
            (impulse.dopamine_delta > 0.1, "spark"),
            (psi > 0.6, "liminal"),
            (entropy > 0.7, "static"),
            (voltage > arc_trigger, "arcing"),
            (voltage < 2.0, "dimming"),
            (drag > 5.0, "sagging")
        ]
        key = next((k for cond, k in conditions if cond), "steady")
        res = s.get(key, "")
        if key == "steady" and self.last_reflex == res:
            return "..."
        return res

    @staticmethod
    def get_current_qualia(impulse: Optional[BiologicalImpulse] = None, config_ref=None) -> Qualia:
        """
        The Stage Director.
        Takes the raw BiologicalImpulse and packages it into human-readable UI elements.
        Determines the dominant emotion and assigns the corresponding UI color,
        vocal tone, and internal monologue prompt hint.
        """
        strings = (LoreManifest.get_instance(config_ref=config_ref or BoneConfig).get(
            "BODY_CONFIG") or {}).get("QUALIA_STRINGS", {})
        if not impulse:
            return Qualia(Prisma.GRY, "...", strings.get("tones", {}).get("steady", ""),
                          strings.get("hints", {}).get("observe", ""))
        profiles = [
            (impulse.oxytocin_delta, Prisma.MAG, "resonant", "connect"),
            (impulse.dopamine_delta, Prisma.CYN, "vibrating", "explore"),
            (impulse.cortisol_delta, Prisma.OCHRE, "strained", "guarded"),
            (impulse.adrenaline_delta, Prisma.RED, "urgent", "fast"),
        ]
        dom_val, color, t_key, h_key = max(profiles, key=lambda x: x[0])
        tones, hints, reflexes = strings.get("tones", {}), strings.get("hints", {}), strings.get("reflexes", {})
        tone = tones.get(t_key, "") if dom_val > 0.2 else tones.get("steady", "")
        hint = hints.get(h_key, "") if dom_val > 0.05 else hints.get("observe", "")
        final_color = color if dom_val > 0.2 else Prisma.GRY
        final_reflex = impulse.somatic_reflex or reflexes.get("steady", "")
        return Qualia(color_code=final_color, somatic_sensation=final_reflex, tone=tone, internal_monologue_hint=hint)

    def apply_impulse(self, impulse: BiologicalImpulse) -> float:
        """
        The Commit step.
        Applies the calculated deltas directly to the host's EndocrineSystem.
        Returns the net stamina impact (usually negative) to be subtracted from the ATP pool.
        """
        for chem in ("cortisol", "oxytocin", "dopamine", "adrenaline"):
            current_val = getattr(self.bio.endo, chem)
            delta_val = getattr(impulse, f"{chem}_delta")
            setattr(self.bio.endo, chem, max(0.0, min(1.0, current_val + delta_val)))
        return impulse.stamina_impact
