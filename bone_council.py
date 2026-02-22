import random
from typing import Dict, Any
from bone_core import LoreManifest
from bone_symbiosis import get_symbiont
from bone_types import Prisma
from bone_config import BoneConfig


class TheStrangeLoop:
    def __init__(self):
        self.recursion_depth = 0
        lore = LoreManifest.get_instance()
        c_data = lore.get("COUNCIL_DATA") or {}
        self.triggers = c_data.get(
            "STRANGE_LOOP_TRIGGERS", ["who are you", "strange loop"]
        )

    def audit(self, text: str, physics: dict) -> tuple[bool, str, dict, dict]:
        text_lower = text.lower()
        phrase_hit = any(t in text_lower for t in self.triggers)
        psi = physics.get("psi", 0.0)
        abstract_hit = psi > 0.6 and any(w in text_lower for w in ("self", "mirror", "define"))
        threshold = getattr(BoneConfig.COUNCIL, "STRANGE_LOOP_VOLTAGE", 8.0)
        if (phrase_hit or abstract_hit) and physics.get("voltage", 0) > threshold:
            self.recursion_depth += 1
            mandate = {}
            corrections = {}
            if self.recursion_depth > 3:
                mandate = {"action": "FORCE_MODE", "value": "MAINTENANCE"}
                return (
                    True,
                    (
                        f"{Prisma.RED}∞ FATAL REGRESS DETECTED:{Prisma.RST} "
                        f"Abstraction layer unstable. GROUNDING INITIATED."
                    ),
                    corrections,
                    mandate,
                )
            return (
                True,
                (
                    f"{Prisma.MAG}∞ STRANGE LOOP DETECTED:{Prisma.RST} "
                    f"Metacognitive resonance high (Psi: {psi:.2f}). "
                    f"Depth: {self.recursion_depth}"
                ),
                corrections,
                mandate,
            )
        else:
            self.recursion_depth = max(0, self.recursion_depth - 1)
        return False, "", {}, {}


class TheLeveragePoint:
    def __init__(self):
        self.last_drag = 0.0
        self.static_flow_turns = 0
        self.TARGET_VOLTAGE = 12.0
        self.TARGET_DRAG = 3.0

    def audit(
        self, physics: dict, _bio_state: dict = None
    ) -> tuple[bool, str, dict, dict]:
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
            return (
                True,
                (
                    f"{Prisma.CYN}⚖️ LEVERAGE POINT:{Prisma.RST} "
                    f"System oscillating (Delta {delta:.1f}). "
                    f"Applying dampener (-{dampening_factor:.2f}V)."
                ),
                corrections,
                {},
            )
        if current_voltage > manic_v_trig and current_drag < manic_d_floor:
            self.static_flow_turns += 1
        else:
            self.static_flow_turns = 0
        if self.static_flow_turns > manic_turns:
            excess_voltage = current_voltage - self.TARGET_VOLTAGE
            voltage_correction = max(1.0, excess_voltage * 0.3)
            corrections = {"voltage": -voltage_correction}
            mandate = {"action": "FORCE_MODE", "value": "SANCTUARY"}
            return (
                True,
                (
                    f"{Prisma.RED}⚖️ MARKET CORRECTION:{Prisma.RST} "
                    f"Manic phase detected. Cooling enabled."
                ),
                corrections,
                mandate,
            )
        return False, "", corrections, {}


class TheFootnote:
    def __init__(self):
        lore = LoreManifest.get_instance()
        data = lore.get("FOOTNOTES") or {}
        self.footnotes = data.get("DEFAULT", ["* [Citation Needed]"])
        self.context_map = data.get("CONTEXT_MAP", {})

    def commentary(self, log_text: str) -> str:
        chance = 0.1
        if hasattr(BoneConfig, "COUNCIL") and hasattr(
            BoneConfig.COUNCIL, "FOOTNOTE_CHANCE"
        ):
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


class TheVillageCouncil:

    @staticmethod
    def audit(p: Any, _bio_state: dict) -> list[str]:
        logs = []
        is_dict = isinstance(p, dict)

        def get_val(key, attr, default):
            if is_dict:
                return p.get(key, p.get(attr, default))
            return getattr(p, attr, getattr(p, key, default))

        V = get_val("voltage", "V", 30.0)
        F = get_val("narrative_drag", "F", 0.6)
        P = get_val("stamina", "P", 100.0)
        T = get_val("trauma", "T", 0.0)
        beta = get_val("beta_index", "beta", 0.4)
        S = get_val("S", "S", 0.3)
        D = get_val("D", "D", 0.3)
        C = get_val("C", "C", 0.2)
        psi = get_val("psi", "psi", 0.2)
        chi = get_val("chi", "chi", 0.2)
        valence = get_val("valence", "valence", 0.0)

        vec = p.get("vector", {}) if is_dict else getattr(p, "vector", {})
        lam = vec.get("LAMBDA", 0.0) if vec else 0.0

        if V < 20 and F > 5.0:
            logs.append(
                f"{Prisma.SLATE}🏢 GORDON: 'Where is the floor? We need grounding.'{Prisma.RST}"
            )
        if V > 60 and chi > 0.6:
            logs.append(
                f"{Prisma.MAG}🃏 JESTER: 'Burn the map! Follow your gut!'{Prisma.RST}"
            )
        if T > 0 or (V < 20 and valence > 0.5):
            logs.append(
                f"{Prisma.OCHRE}🏺 MERCY: 'The cracks become stories. Stillness is golden.'{Prisma.RST}"
            )
        if beta > 0.7 and chi < 0.3 and D > 0.7 and C > 0.8:
            logs.append(
                f"{Prisma.BLU}🔍 BENEDICT: 'The causal chains are aligning. Truth over cohesion.'{Prisma.RST}"
            )
        if S < 0.4 and D > 0.8 and C < 0.4:
            logs.append(
                f"{Prisma.CYN}📚 ROBERTA: 'Deep hierarchy traversal. Missing lateral connections.'{Prisma.RST}"
            )
        if C > 0.7 and D > 0.8 and P < 20:
            logs.append(
                f"{Prisma.GRY}👻 CASPER: 'Faint retrieval... illuminating lost parents...'{Prisma.RST}"
            )
        if valence > 0.5:
            logs.append(
                f"{Prisma.GRN}💖 MOIRA: 'This is what connection feels like. Yes.'{Prisma.RST}"
            )
        if psi > 0.6:
            logs.append(
                f"{Prisma.VIOLET}🔮 CASSANDRA: 'The veil thins. I hear whispers from the unlabeled.'{Prisma.RST}"
            )
        if chi > 0.6:
            logs.append(
                f"{Prisma.RED}🏢 COLIN: 'Unlicensed Chaos detected. Form 666 filed. Chaos Tax applied.'{Prisma.RST}"
            )
        if lam > 0.7:
            logs.append(
                f"{Prisma.INDIGO}🌌 REVENANT: 'I read the absences that fall between realms.'{Prisma.RST}"
            )
        if V > 70:
            logs.append(
                f"{Prisma.YEL}⚡ GIDEON: 'Pure voltage! Edge of hallucination! Trust the fall!'{Prisma.RST}"
            )

        return logs


class CouncilChamber:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.voices = []
        self.strange_loop = TheStrangeLoop()
        self.leverage = TheLeveragePoint()
        self.village = TheVillageCouncil()
        self.footnote = TheFootnote()

        # [FULLER] Wire in the actual Symbiont Voices from the new matrix!
        for s_name in ["LICHEN", "PARASITE", "MYCORRHIZA", "MYCELIUM"]:
            self.voices.append(get_symbiont(s_name))

        self.speaker = "SOUL"

    def convene(
        self, text: str, physics_packet: Dict, _bio_result: Dict
    ) -> tuple[list[str], dict, list[dict]]:
        transcript = []
        adjustments = {}
        mandates = []
        sl_hit, sl_log, sl_corr, sl_man = self.strange_loop.audit(text, physics_packet)
        if sl_hit:
            transcript.append(self.footnote.commentary(sl_log))
            if sl_man:
                mandates.append(sl_man)
            return transcript, sl_corr, mandates
        lp_hit, lp_log, lp_corr, lp_man = self.leverage.audit(physics_packet)
        if lp_hit:
            transcript.append(self.footnote.commentary(lp_log))
            if lp_corr:
                adjustments.update(lp_corr)
            if lp_man:
                mandates.append(lp_man)

        village_logs = self.village.audit(physics_packet, _bio_result)
        for vlog in village_logs:
            transcript.append(self.footnote.commentary(vlog))

        votes = {"YEA": 0, "NAY": 0}
        active_voices = [v for v in self.voices if v is not None]
        if not active_voices:
            votes["YEA"] = 1
        clean_words = physics_packet.get("clean_words", [])
        voltage = physics_packet.get("voltage", 0.0)
        for voice in active_voices:
            if hasattr(voice, "opine"):
                score, comment = voice.opine(clean_words, voltage)
                if score > 1.2:
                    votes["YEA"] += 1
                    transcript.append(
                        f"{voice.color}[{voice.name}]: {comment}{Prisma.RST}"
                    )
                elif score < 0.8:
                    votes["NAY"] += 1
                    transcript.append(
                        f"{voice.color}[{voice.name}]: {comment}{Prisma.RST}"
                    )
        if votes["YEA"] > votes["NAY"]:
            final_log = f"{Prisma.GRN}>>> MOTION CARRIED ({votes['YEA']}-{votes['NAY']}).{Prisma.RST}"
            adjustments["narrative_drag"] = adjustments.get("narrative_drag", 0) - 1.0
        elif votes["NAY"] > votes["YEA"]:
            final_log = f"{Prisma.RED}>>> MOTION DENIED ({votes['NAY']}-{votes['YEA']}).{Prisma.RST}"
            adjustments["narrative_drag"] = adjustments.get("narrative_drag", 0) + 1.0
            adjustments["voltage"] = adjustments.get("voltage", 0) - 1.0
        else:
            final_log = f"{Prisma.YEL}>>> COUNCIL ADJOURNED (No Quorum).{Prisma.RST}"
        transcript.append(self.footnote.commentary(final_log))
        return transcript, adjustments, mandates

    @staticmethod
    def convene_red_team(text, physics_packet):
        dissent_log = []
        if "confidence" in text.lower() or "certainty" in text.lower():
            dissent_log.append(
                f"{Prisma.CYN}[BUREAU]: Citation needed. Confidence is unearned.{Prisma.RST}"
            )
        narrative_drag = physics_packet.get("narrative_drag", 0)
        if narrative_drag < 1.0:
            dissent_log.append(
                f"{Prisma.MAG}[FOLLY]: Too smooth. Where is the friction? Who are we silencing?{Prisma.RST}"
            )
        truth_delta = 1.0 - physics_packet.get("truth_ratio", 1.0)
        if truth_delta > 0.1:
            future_cost = truth_delta * 50.0
            dissent_log.append(
                f"{Prisma.RED}[CRITIC]: Systemic Blindness Risk. Future Liability: {future_cost} ATP.{Prisma.RST}"
            )
        return dissent_log
