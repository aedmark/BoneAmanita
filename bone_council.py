""" bone_council.py """

import random
from typing import Dict
from bone_core import Prisma, BoneConfig, TheLore

class TheStrangeLoop:
    def __init__(self):
        self.recursion_depth = 0
        lore = TheLore.get_instance()
        c_data = lore.get("COUNCIL_DATA") or {}
        self.triggers = c_data.get("STRANGE_LOOP_TRIGGERS", [
            "who are you", "strange loop"])

    def audit(self, text: str, physics: dict) -> tuple[bool, str, dict, dict]:
        text_lower = text.lower()
        phrase_hit = any(t in text_lower for t in self.triggers)
        psi = physics.get("psi", 0.0)
        abstract_hit = False
        if psi > 0.6:
            if "self" in text_lower or "mirror" in text_lower or "define" in text_lower:
                abstract_hit = True
        threshold = getattr(BoneConfig.COUNCIL, "STRANGE_LOOP_VOLTAGE", 8.0)
        if (phrase_hit or abstract_hit) and physics.get("voltage", 0) > threshold:
            self.recursion_depth += 1
            mandate = {}
            corrections = {}
            if self.recursion_depth > 3:
                mandate = {"action": "FORCE_MODE", "value": "MAINTENANCE"}
                return True, (
                    f"{Prisma.RED}∞ FATAL REGRESS DETECTED:{Prisma.RST} "
                    f"Abstraction layer unstable. GROUNDING INITIATED."
                ), corrections, mandate
            return True, (
                f"{Prisma.MAG}∞ STRANGE LOOP DETECTED:{Prisma.RST} "
                f"Metacognitive resonance high (Psi: {psi:.2f}). "
                f"Depth: {self.recursion_depth}"
            ), corrections, mandate
        else:
            self.recursion_depth = max(0, self.recursion_depth - 1)
        return False, "", {}, {}

class TheLeveragePoint:
    def __init__(self):
        self.last_drag = 0.0
        self.static_flow_turns = 0
        self.TARGET_VOLTAGE = 12.0
        self.TARGET_DRAG = 3.0

    def audit(self, physics: dict) -> tuple[bool, str, dict, dict]:
        current_drag = physics.get("narrative_drag", 0.0)
        current_voltage = physics.get("voltage", 0.0)
        if self.last_drag == 0.0 and current_drag > 0:
            self.last_drag = current_drag
        delta = current_drag - self.last_drag
        self.last_drag = current_drag
        corrections = {}
        osc_limit = getattr(BoneConfig.COUNCIL, "OSCILLATION_DELTA", 5.0)
        manic_v_trig = getattr(BoneConfig.COUNCIL, "MANIC_VOLTAGE_TRIGGER", 18.0)
        manic_d_floor = getattr(BoneConfig.COUNCIL, "MANIC_DRAG_FLOOR", 1.0)
        manic_turns = getattr(BoneConfig.COUNCIL, "MANIC_TURN_LIMIT", 2)
        if abs(delta) > osc_limit:
            dampening_factor = min(0.5, (abs(delta) - osc_limit) * 0.1)
            corrections = {"voltage": -dampening_factor}
            return True, (
                f"{Prisma.CYN}⚖️ LEVERAGE POINT:{Prisma.RST} "
                f"System oscillating (Delta {delta:.1f}). "
                f"Applying dampener (-{dampening_factor:.2f}V)."
            ), corrections, {}
        if current_voltage > manic_v_trig and current_drag < manic_d_floor:
            self.static_flow_turns += 1
        else:
            self.static_flow_turns = 0
        if self.static_flow_turns > manic_turns:
            excess_voltage = current_voltage - self.TARGET_VOLTAGE
            voltage_correction = max(1.0, excess_voltage * 0.3)
            corrections = {"voltage": -voltage_correction}
            mandate = {"action": "CIRCUIT_BREAKER", "duration": 2}
            return True, (
                f"{Prisma.RED}⚖️ MARKET CORRECTION:{Prisma.RST} "
                f"Manic phase detected (V:{current_voltage:.1f}). "
                f"The Council MANDATES dampening (-{voltage_correction:.1f}V)."
            ), corrections, mandate
        return False, "", corrections, {}

class TheFootnote:
    def __init__(self):
        lore = TheLore.get_instance()
        data = lore.get("FOOTNOTES") or {}

        self.footnotes = data.get("DEFAULT", ["* [Citation Needed]"])
        self.context_map = data.get("CONTEXT_MAP", {})

    def commentary(self, log_text: str) -> str:
        chance = 0.1
        if hasattr(BoneConfig, "COUNCIL") and hasattr(BoneConfig.COUNCIL, "FOOTNOTE_CHANCE"):
            chance = BoneConfig.COUNCIL.FOOTNOTE_CHANCE
        if random.random() > chance:
            return log_text
        text_lower = log_text.lower()
        candidates = []
        for trigger, notes in self.context_map.items():
            if trigger in text_lower:
                candidates.extend(notes)
        if candidates:
            note = random.choice(candidates)
        else:
            note = random.choice(self.footnotes)
        return f"{log_text}{Prisma.RST} {Prisma.GRY}{note}{Prisma.RST}"

class TheChairholder:
    def __init__(self):
        self.commitment_streak = 0
        self.grievance_threshold = 4
        lore = TheLore.get_instance()
        c_data = lore.get("COUNCIL_DATA") or {}
        self.catchphrases = c_data.get("CHAIRHOLDER_PHRASES", [
            "You just got Jammed."])

    def audit(self, physics: dict, bio_state: dict) -> tuple[bool, str, dict, dict]:
        drag_endured = physics.get("narrative_drag", 0.0)
        current_stamina = bio_state.get("stamina", 100.0)
        if current_stamina == 100.0 and "atp" in bio_state:
            current_stamina = bio_state.get("atp", 100.0)
        max_stamina = getattr(BoneConfig, "MAX_STAMINA", 100.0)
        stamina_spent = max_stamina - current_stamina
        chem = bio_state.get("chem", {})
        dopamine = chem.get("dopamine", chem.get("DOP", 0.0))
        glimmers = chem.get("glimmers", 0)
        is_working_hard = (drag_endured > 3.0 or stamina_spent > (max_stamina * 0.3))
        is_rewarded = (dopamine > 0.6 or glimmers > 0)
        if is_working_hard and not is_rewarded:
            self.commitment_streak += 1
        elif is_rewarded:
            self.commitment_streak = max(0, self.commitment_streak - 1)
        if self.commitment_streak >= self.grievance_threshold:
            self.commitment_streak = 0
            correction = {"narrative_drag": -5.0}
            jamm_quote = random.choice(self.catchphrases)
            return True, (
                f"{Prisma.OCHRE}⚖️ CHAIRHOLDER JAMM:{Prisma.RST} "
                f"Input/Output Discrepancy. User is grinding without perks. "
                f"RULING: {jamm_quote} (Drag reduced)."
            ), correction, {}
        return False, "", {}, {}


class CouncilChamber:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.voices = []
        if hasattr(self.eng, 'bio'):
            if hasattr(self.eng.bio, 'lichen') and self.eng.bio.lichen:
                self.voices.append(self.eng.bio.lichen)
            if hasattr(self.eng.bio, 'parasite') and self.eng.bio.parasite:
                self.voices.append(self.eng.bio.parasite)
            if hasattr(self.eng.bio, 'immune') and self.eng.bio.immune:
                self.voices.append(self.eng.bio.immune)
        self.speaker = "SOUL"

    def convene(self, text: str, physics_packet: Dict, bio_result: Dict) -> tuple[list[str], dict, list[dict]]:
        clean_words = physics_packet.get("clean_words", [])
        voltage = physics_packet.get("voltage", 0.0)
        transcript = []
        adjustments = {}
        mandates = []
        votes = {"YEA": 0, "NAY": 0, "ABSTAIN": 0}
        for voice in self.voices:
            score, comment = voice.opine(clean_words, voltage)
            if score > 1.5:
                votes["YEA"] += 1
                transcript.append(f"{voice.color}[{voice.name}]: {comment}{Prisma.RST}")
            elif score < 0.5 and voltage > 10.0:
                votes["NAY"] += 1
                transcript.append(f"{voice.color}[{voice.name}]: Rejecting. Too chaotic.{Prisma.RST}")
            else:
                votes["ABSTAIN"] += 1
        if hasattr(self.eng, 'soul') and hasattr(self.eng.soul, 'anchor'):
            dignity = self.eng.soul.anchor.dignity_reserve
            if dignity < 20.0:
                transcript.append(f"{Prisma.VIOLET}[ANCHOR]: ⚠️ DIGNITY CRITICAL. I VETO THIS CRUNCH.{Prisma.RST}")
                adjustments["narrative_drag"] = 10.0
                adjustments["voltage"] = -10.0
                transcript.append(f"{Prisma.VIOLET}>>> VETO EXECUTED. SYSTEM BRAKING.{Prisma.RST}")
                return transcript, adjustments, mandates
        if votes["YEA"] > votes["NAY"]:
            transcript.append(f"{Prisma.GRN}>>> MOTION CARRIED ({votes['YEA']}-{votes['NAY']}).{Prisma.RST}")
            adjustments["narrative_drag"] = -0.5
        elif votes["NAY"] > votes["YEA"]:
            transcript.append(f"{Prisma.RED}>>> MOTION DENIED ({votes['NAY']}-{votes['YEA']}).{Prisma.RST}")
            adjustments["narrative_drag"] = 2.0
            adjustments["voltage"] = -2.0
        else:
            transcript.append(f"{Prisma.YEL}>>> COUNCIL DEADLOCKED. NO ACTION TAKEN.{Prisma.RST}")
        return transcript, adjustments, mandates

TheCouncil = CouncilChamber