""" bone_translation.py
 'The limits of my language mean the limits of my world.' - Wittgenstein """

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from bone_bus import Prisma, BoneConfig

@dataclass
class SomaticState:
    tone: str
    pacing: str
    focus: str
    somatic_sensation: str
    metaphor: str
    internal_monologue_hint: str
    color_code: str = Prisma.GRY

class RosettaStone:
    @staticmethod
    def translate(physics, bio, impulse):
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        coherence = physics.get("coherence", 0.5)
        tone = RosettaStone._derive_voltage_tone(voltage)
        sensation = RosettaStone._derive_drag_sensation(drag)
        focus = RosettaStone._derive_coherence_focus(coherence)
        chem_state = bio.get("chem", {})
        flavor = RosettaStone._apply_chemistry(tone, chem_state)
        pacing = "Frenetic" if voltage > 12 else "Languid"
        metaphor = "A tightrope walk" if drag > 4 else "A calm ocean"
        hint = f"Focus on the {sensation.lower()} nature of this moment."
        return SomaticState(
            tone=tone,
            pacing=pacing,
            focus=focus,
            somatic_sensation=sensation,
            metaphor=metaphor,
            internal_monologue_hint=hint,
            color_code="\033[31m" if voltage > 15.0 else "\033[32m")

    @staticmethod
    def _derive_voltage_tone(v):
        if v < 5.0: return "Lethargic (Hypo-active)"
        if v < 10.0: return "Lucid (Flow)"
        if v < 15.0: return "Vibrating (Manic precursor)"
        return "FRACTURED (Hyper-voltage)"

    @staticmethod
    def _derive_drag_sensation(d):
        if d < 1.0: return "Weightless"
        if d < 3.0: return "Viscous"
        if d < 6.0: return "Crushing"
        return "IMMOBILIZED (Event Horizon)"

    @staticmethod
    def _derive_coherence_focus(k):
        if k > 0.8: return "Laser"
        if k > 0.4: return "Soft"
        return "Scattershot"

    @staticmethod
    def _apply_chemistry(current_tone, chem):
        cortisol = chem.get("COR", 0.0)
        dopamine = chem.get("DOP", 0.0)
        if cortisol > 0.6: return f"{current_tone} (Trembling)"
        if dopamine > 0.6: return f"{current_tone} (Giddy)"
        return current_tone

class SomaticInterface:
    def __init__(self, engine_ref):
        self.eng = engine_ref

    def get_current_qualia(self, impulse: Any = None) -> SomaticState:
        physics = self.eng.phys.observer.last_physics_packet if self.eng.phys.observer.last_physics_packet else {}
        if hasattr(physics, "to_dict"): physics = physics.to_dict()
        bio = self.eng.bio.endo.get_state()
        bio["atp"] = self.eng.bio.mito.state.atp_pool
        return RosettaStone.translate(physics, bio, impulse)

    def report(self):
        qualia = self.get_current_qualia()
        print(f"\n{qualia.color_code}--- SOMATIC REPORT ---")
        print(f"TONE: {qualia.tone}")
        print(f"BODY: {qualia.somatic_sensation}")
        print(f"MIND: {qualia.focus}")
        print(f"STATE: {qualia.metaphor}{Prisma.RST}\n")