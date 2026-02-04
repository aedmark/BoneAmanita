""" bone_council.py
 The Advisory Board: Hofstadter, Meadows, and Pratchett """

import random
from bone_bus import Prisma, BoneConfig

class TheStrangeLoop:
    def __init__(self):
        self.recursion_depth = 0
        self.triggers = [
            "who are you", "what are you", "system status",
            "narrative loop", "simulation boundaries", "fourth wall",
            "recursive", "infinite regress", "strange loop"]

    def audit(self, text: str, physics: dict) -> tuple[bool, str, dict]:
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
            if self.recursion_depth > 3:
                mandate = {"action": "FORCE_MODE", "value": "MAINTENANCE"}
                return True, (
                    f"{Prisma.RED}∞ FATAL REGRESS DETECTED:{Prisma.RST} "
                    f"Abstraction layer unstable. GROUNDING INITIATED."
                ), mandate
            return True, (
                f"{Prisma.MAG}∞ STRANGE LOOP DETECTED:{Prisma.RST} "
                f"Metacognitive resonance high (Psi: {psi:.2f}). "
                f"Depth: {self.recursion_depth}"
            ), mandate
        else:
            self.recursion_depth = max(0, self.recursion_depth - 1)
        return False, "", {}

class TheLeveragePoint:
    def __init__(self):
        self.last_drag = 0.0
        self.static_flow_turns = 0
        self.TARGET_VOLTAGE = 12.0
        self.TARGET_DRAG = 3.0

    def audit(self, physics: dict) -> tuple[bool, str, dict, dict]:
        current_drag = physics.get("narrative_drag", 0.0)
        current_voltage = physics.get("voltage", 0.0)
        delta = current_drag - self.last_drag
        self.last_drag = current_drag
        corrections = {}
        osc_limit = getattr(BoneConfig.COUNCIL, "OSCILLATION_DELTA", 5.0)
        manic_v_trig = getattr(BoneConfig.COUNCIL, "MANIC_VOLTAGE_TRIGGER", 18.0)
        manic_d_floor = getattr(BoneConfig.COUNCIL, "MANIC_DRAG_FLOOR", 1.0)
        manic_turns = getattr(BoneConfig.COUNCIL, "MANIC_TURN_LIMIT", 2)
        if abs(delta) > osc_limit:
            return True, (
                f"{Prisma.CYN}⚖️ LEVERAGE POINT:{Prisma.RST} "
                f"System oscillating wildly (Delta {delta:.1f}). "
                f"Recommendation: Dampen inputs."
            ), corrections, {}
        if current_voltage > manic_v_trig and current_drag < manic_d_floor:
            self.static_flow_turns += 1
        else:
            self.static_flow_turns = 0
        if self.static_flow_turns > manic_turns:
            excess_voltage = current_voltage - self.TARGET_VOLTAGE
            voltage_correction = max(1.0, excess_voltage * 0.3)
            mandate = {"action": "CIRCUIT_BREAKER", "duration": 2}
            return True, (
                f"{Prisma.RED}⚖️ MARKET CORRECTION:{Prisma.RST} "
                f"Manic phase detected (V:{current_voltage:.1f}). "
                f"The Council MANDATES dampening (-{voltage_correction:.1f}V)."
            ), corrections, mandate
        return False, "", corrections, {}

class TheFootnote:
    def __init__(self):
        self.footnotes = [
            "* Not to be confused with the other kind of void.",
            "* The turtle moves.",
            "* This is technically impossible, but the code doesn't know that.",
            "* Do not eat the green wobbly bit.",
            "* Gravity is a habit that is hard to shake.",
            "* As reliable as a chocolate teapot."]
        self.context_map = {
            "void": ["* Not to be confused with the other kind of void."],
            "gravity": ["* Gravity is a habit that is hard to shake."],
            "physics": ["* This is technically impossible, but the code doesn't know that."],
            "glitch": ["* Do not eat the green wobbly bit."],
            "error": ["* As reliable as a chocolate teapot."],
            "system": ["* The turtle moves."]}

    def commentary(self, log_text: str) -> str:
        if random.random() > BoneConfig.COUNCIL.FOOTNOTE_CHANCE:
            return log_text
        text_lower = log_text.lower()
        note = None
        for trigger, notes in self.context_map.items():
            if trigger in text_lower:
                note = random.choice(notes)
                break
        if not note:
            note = random.choice(self.footnotes)
        return f"{log_text}{Prisma.RST} {Prisma.GRY}{note}{Prisma.RST}"

class TheParliamentarian:
    def __init__(self):
        self.commitment_streak = 0
        self.grievance_threshold = 4

    def audit(self, physics: dict, bio_state: dict) -> tuple[bool, str, dict]:
        drag_endured = physics.get("narrative_drag", 0.0)
        stamina_spent = 100.0 - bio_state.get("stamina", 100.0)
        chem = bio_state.get("chem", {})
        dopamine = chem.get("dopamine", chem.get("DOP", 0.0))
        glimmers = chem.get("glimmers", 0)
        is_working_hard = (drag_endured > 3.0 or stamina_spent > 40.0)
        is_rewarded = (dopamine > 0.6 or glimmers > 0)
        if is_working_hard and not is_rewarded:
            self.commitment_streak += 1
        elif is_rewarded:
            self.commitment_streak = max(0, self.commitment_streak - 1)
        if self.commitment_streak >= self.grievance_threshold:
            self.commitment_streak = 0
            correction = {"narrative_drag": -5.0}
            return True, (
                f"{Prisma.OCHRE}⚖️ POINT OF ORDER:{Prisma.RST} "
                f"Input/Output Discrepancy detected. "
                f"User is contributing (Effort High) but System is not yielding (Reward Low). "
                f"RULING: The Rules are being ignored. Objection noted."
            ), correction
        return False, "", {}

class CouncilChamber:
    def __init__(self):
        self.hofstadter = TheStrangeLoop()
        self.meadows = TheLeveragePoint()
        self.pratchett = TheFootnote()
        self.parliamentarian = TheParliamentarian()

    def convene(self, text: str, physics: dict, bio_state: dict = None) -> tuple[list[str], dict, list[dict]]:
        advice = []
        total_corrections = {}
        mandates = []
        is_loop, h_msg, h_mandate = self.hofstadter.audit(text, physics)
        if is_loop:
            advice.append(h_msg)
            if h_mandate: mandates.append(h_mandate)
        is_lev, m_msg, corrections, m_mandate = self.meadows.audit(physics)
        if is_lev:
            advice.append(m_msg)
            for k, v in corrections.items():
                total_corrections[k] = total_corrections.get(k, 0.0) + v
            if m_mandate: mandates.append(m_mandate)
        if bio_state:
            is_order, p_msg, p_correction = self.parliamentarian.audit(physics, bio_state)
            if is_order:
                advice.append(p_msg)
                for k, v in p_correction.items():
                    total_corrections[k] = total_corrections.get(k, 0.0) + v
        return advice, total_corrections, mandates

    def annotate_logs(self, logs: list[str]) -> list[str]:
        annotated = []
        for line in logs:
            commented_line = self.pratchett.commentary(line)
            annotated.append(commented_line)
        return annotated