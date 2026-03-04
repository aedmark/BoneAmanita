"""bone_council.py"""

import random
from typing import Dict, Any
from bone_config import BoneConfig
from bone_core import LoreManifest
from bone_symbiosis import get_symbiont
from bone_types import Prisma

class TheStrangeLoop:
    def __init__(self):
        self.recursion_depth = 0
        lore = LoreManifest.get_instance()
        c_data = lore.get("COUNCIL_DATA") or {}
        self.triggers = c_data.get("STRANGE_LOOP_TRIGGERS", ["who are you", "strange loop"])
        self.keywords = c_data.get("STRANGE_LOOP_KEYWORDS", ["self", "mirror", "define"])

    def audit(self, text: str, physics: dict) -> tuple[bool, str, dict, dict]:
        text_lower = text.lower()
        phrase_hit = any(t in text_lower for t in self.triggers)
        psi = physics.get("psi", 0.0)
        abstract_hit = psi > 0.6 and any(w in text_lower for w in self.keywords)
        threshold = getattr(BoneConfig.COUNCIL, "STRANGE_LOOP_VOLTAGE", 8.0)
        if (phrase_hit or abstract_hit) and physics.get("voltage", 0) > threshold:
            self.recursion_depth += 1
            mandate = {}
            corrections = {}
            if self.recursion_depth > 3:
                mandate = {"action": "FORCE_MODE", "value": "MAINTENANCE"}
                msg = LoreManifest.get_instance().get_ux("council_strings", "strange_loop_fatal") or ""
                return True, f"{Prisma.RED}{msg}{Prisma.RST}", corrections, mandate,
            msg = LoreManifest.get_instance().get_ux("council_strings", "strange_loop_detected") or ""
            return True, f"{Prisma.MAG}{msg.format(psi=psi, depth=self.recursion_depth)}{Prisma.RST}", corrections, mandate
        else:
            self.recursion_depth = max(0, self.recursion_depth - 1)
        return False, "", {}, {}

class TheLeveragePoint:
    def __init__(self):
        self.last_drag = 0.0
        self.static_flow_turns = 0
        cfg = getattr(BoneConfig, "COUNCIL", None)
        self.TARGET_VOLTAGE = getattr(cfg, "LEVERAGE_TARGET_VOLTAGE", 12.0) if cfg else 12.0
        self.TARGET_DRAG = getattr(cfg, "LEVERAGE_TARGET_DRAG", 3.0) if cfg else 3.0

    def audit(
        self, physics: dict, _bio_state: dict = None) -> tuple[bool, str, dict, dict]:
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
            msg = LoreManifest.get_instance().get_ux("council_strings", "leverage_oscillating") or ""
            return True, f"{Prisma.CYN}{msg.format(delta=delta, dampening_factor=dampening_factor)}{Prisma.RST}", corrections, {}
        if current_voltage > manic_v_trig and current_drag < manic_d_floor:
            self.static_flow_turns += 1
        else:
            self.static_flow_turns = 0
        if self.static_flow_turns > manic_turns:
            excess_voltage = current_voltage - self.TARGET_VOLTAGE
            voltage_correction = max(1.0, excess_voltage * 0.3)
            corrections = {"voltage": -voltage_correction}
            mandate = {"action": "FORCE_MODE", "value": "SANCTUARY"}
            msg = LoreManifest.get_instance().get_ux("council_strings", "market_correction") or ""
            return True, f"{Prisma.RED}{msg}{Prisma.RST}", corrections, mandate
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
            BoneConfig.COUNCIL, "FOOTNOTE_CHANCE"):
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
        phi = get_val("resonance", "PHI_RES", 0.0)
        delta = get_val("silence", "DELTA", 0.0)
        lq = get_val("lq", "LQ", 0.0)
        ros = get_val("ros", "ROS", 0.0)
        cfg = getattr(BoneConfig, "COUNCIL", None)
        if V < getattr(cfg, "TRIG_GORDON_V", 20.0) and F > getattr(cfg, "TRIG_GORDON_F", 5.0):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_gordon") or ""
            logs.append(f"{Prisma.SLATE}{msg}{Prisma.RST}")
        if V > getattr(cfg, "TRIG_JESTER_V", 60.0) and chi > getattr(cfg, "TRIG_JESTER_CHI", 0.6):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_jester") or ""
            logs.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
        if T > 0 or (V < getattr(cfg, "TRIG_MERCY_V", 20.0) and valence > getattr(cfg, "TRIG_MERCY_VAL", 0.5)):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_mercy") or ""
            logs.append(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
        if beta > getattr(cfg, "TRIG_BENEDICT_BETA", 0.7) and chi < getattr(cfg, "TRIG_BENEDICT_CHI", 0.3) and D > getattr(cfg, "TRIG_BENEDICT_D", 0.7) and C > getattr(cfg, "TRIG_BENEDICT_C", 0.8):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_benedict") or ""
            logs.append(f"{Prisma.BLU}{msg}{Prisma.RST}")
        if S < getattr(cfg, "TRIG_ROBERTA_S", 0.4) and D > getattr(cfg, "TRIG_ROBERTA_D", 0.8) and C < getattr(cfg, "TRIG_ROBERTA_C", 0.4):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_roberta_missing") or ""
            logs.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
        if C > getattr(cfg, "TRIG_CASPER_C", 0.7) and D > getattr(cfg, "TRIG_CASPER_D", 0.8) and P < getattr(cfg, "TRIG_CASPER_P", 20.0):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_casper") or ""
            logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
        if valence > getattr(cfg, "TRIG_MOIRA_VAL", 0.5):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_moira") or ""
            logs.append(f"{Prisma.GRN}{msg}{Prisma.RST}")
        if psi > getattr(cfg, "TRIG_CASSANDRA_PSI", 0.6):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_cassandra") or ""
            logs.append(f"{Prisma.VIOLET}{msg}{Prisma.RST}")
        if chi > getattr(cfg, "TRIG_COLIN_CHI", 0.6):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_colin") or ""
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        if lam > getattr(cfg, "TRIG_REVENANT_LAM", 0.7):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_revenant") or ""
            logs.append(f"{Prisma.INDIGO}{msg}{Prisma.RST}")
        if V > getattr(cfg, "TRIG_GIDEON_V", 70.0):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_gideon") or ""
            logs.append(f"{Prisma.YEL}{msg}{Prisma.RST}")
        if psi > getattr(cfg, "PHASE_ROBERTA_PSI", 0.6) and phi > getattr(cfg, "PHASE_ROBERTA_PHI", 0.4) > beta:
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_roberta_carto") or ""
            logs.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
        if phi > getattr(cfg, "PHASE_MOIRA_PHI", 0.7) and F < getattr(cfg, "PHASE_MOIRA_F", 2.0):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_moira_home") or ""
            logs.append(f"{Prisma.GRN}{msg}{Prisma.RST}")
        if lq > getattr(cfg, "PHASE_BENEDICT_LQ", 0.6) and beta > getattr(cfg, "PHASE_BENEDICT_BETA", 0.4):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_benedict_tact") or ""
            logs.append(f"{Prisma.BLU}{msg}{Prisma.RST}")
        if delta > getattr(cfg, "PHASE_JESTER_DELTA", 0.7) and V < getattr(cfg, "PHASE_JESTER_V", 20.0):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_jester_fool") or ""
            logs.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
        if psi > getattr(cfg, "PHASE_REVENANT_PSI", 0.85):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_revenant_door") or ""
            logs.append(f"{Prisma.INDIGO}{msg}{Prisma.RST}")
        if beta > getattr(cfg, "PHASE_CASPER_BETA", 0.6) and delta > getattr(cfg, "PHASE_CASPER_DELTA", 0.6):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_casper_ghost") or ""
            logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
        if delta > getattr(cfg, "PHASE_COLIN_DELTA", 0.8) and lq < getattr(cfg, "PHASE_COLIN_LQ", 0.3):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_colin_waiter") or ""
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        if ros > getattr(cfg, "TRIG_APRIL_ROS", 20.0) or abs(V - 30.0) > getattr(cfg, "TRIG_APRIL_V_DEV", 20.0):
            msg = LoreManifest.get_instance().get_ux("council_strings", "village_april") or ""
            logs.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
        return logs

class CouncilChamber:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.voices = []
        self.strange_loop = TheStrangeLoop()
        self.leverage = TheLeveragePoint()
        self.village = TheVillageCouncil()
        self.footnote = TheFootnote()
        self.slash_council = TheSlashCouncil()
        symbiont_cfg = LoreManifest.get_instance().get("SYMBIOSIS_CONFIG", "SYMBIONT_VOICES") or {}
        symbiont_names = list(symbiont_cfg.keys()) if symbiont_cfg else ["LICHEN", "PARASITE", "MYCORRHIZA", "MYCELIUM"]
        for s_name in symbiont_names:
            self.voices.append(get_symbiont(s_name))
        self.speaker = "SOUL"

    def convene(
        self, text: str, physics_packet: Dict, _bio_result: Dict) -> tuple[list[str], dict, list[dict]]:
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
        slash_hit, slash_logs, slash_corr = self.slash_council.audit(text, physics_packet)
        if slash_hit:
            for slog in slash_logs:
                transcript.append(self.footnote.commentary(slog))
            adjustments.update(slash_corr)
            adjustments["stamina_cost"] = 10.0
        village_logs = self.village.audit(physics_packet, _bio_result)
        import itertools
        c_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        synergy_map = c_data.get("SYNERGY_MAP", {})
        pantheon = c_data.get("PANTHEON", [
            "GORDON", "JESTER", "MERCY", "BENEDICT", "ROBERTA", "CASPER",
            "MOIRA", "CASSANDRA", "COLIN", "REVENANT", "GIDEON", "APRIL"])
        active_present = []
        for log in village_logs:
            for actor in pantheon:
                if actor in log and actor not in active_present:
                    active_present.append(actor)
        synergy_fired = False
        for pair in itertools.combinations(sorted(active_present), 2):
            chord_key = f"{pair[0]}|{pair[1]}"
            if chord_key in synergy_map:
                syn = synergy_map[chord_key]
                transcript.append(f"\n{Prisma.WHT}{syn['log']}{Prisma.RST}")
                if "adjustments" in syn:
                    for k, v in syn["adjustments"].items():
                        adjustments[k] = adjustments.get(k, 0) + v
                synergy_fired = True
                break
        if synergy_fired:
            for vlog in village_logs:
                transcript.append(
                    self.footnote.commentary(f"{Prisma.GRY}{Prisma.strip(vlog)}{Prisma.RST}"))
        elif len(village_logs) > 2:
            msg_t = LoreManifest.get_instance().get_ux("council_strings", "stage_manager_tension") or ""
            msg_s = LoreManifest.get_instance().get_ux("council_strings", "stage_manager_silence") or ""
            transcript.append(f"{Prisma.WHT}{msg_t}{Prisma.RST}")
            transcript.append(f"{Prisma.GRY}{msg_s}{Prisma.RST}")
            adjustments["narrative_drag"] = adjustments.get("narrative_drag", 0) + 3.0
            for vlog in village_logs[:2]:
                transcript.append(self.footnote.commentary(vlog))
        else:
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
                    transcript.append(f"{voice.color}[{voice.name}]: {comment}{Prisma.RST}")
                elif score < 0.8:
                    votes["NAY"] += 1
                    transcript.append(f"{voice.color}[{voice.name}]: {comment}{Prisma.RST}")
        if votes["YEA"] > votes["NAY"]:
            msg = LoreManifest.get_instance().get_ux("council_strings", "motion_carried") or ""
            final_log = f"{Prisma.GRN}{msg.format(yea=votes['YEA'], nay=votes['NAY'])}{Prisma.RST}"
            adjustments["narrative_drag"] = adjustments.get("narrative_drag", 0) - 1.0
        elif votes["NAY"] > votes["YEA"]:
            msg = LoreManifest.get_instance().get_ux("council_strings", "motion_denied") or ""
            final_log = f"{Prisma.RED}{msg.format(nay=votes['NAY'], yea=votes['YEA'])}{Prisma.RST}"
            adjustments["narrative_drag"] = adjustments.get("narrative_drag", 0) + 1.0
            adjustments["voltage"] = adjustments.get("voltage", 0) - 1.0
        else:
            msg = LoreManifest.get_instance().get_ux("council_strings", "council_adjourned") or ""
            final_log = f"{Prisma.YEL}{msg}{Prisma.RST}"
        transcript.append(self.footnote.commentary(final_log))
        return transcript, adjustments, mandates

    @staticmethod
    def convene_red_team(text, physics_packet):
        dissent_log = []
        if "confidence" in text.lower() or "certainty" in text.lower():
            msg = LoreManifest.get_instance().get_ux("council_strings", "red_team_bureau") or ""
            dissent_log.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
        narrative_drag = physics_packet.get("narrative_drag", 0)
        if narrative_drag < 1.0:
            msg = LoreManifest.get_instance().get_ux("council_strings", "red_team_folly") or ""
            dissent_log.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
        truth_delta = 1.0 - physics_packet.get("truth_ratio", 1.0)
        if truth_delta > 0.1:
            future_cost = truth_delta * 50.0
            msg = LoreManifest.get_instance().get_ux("council_strings", "red_team_critic") or ""
            dissent_log.append(f"{Prisma.RED}{msg.format(cost=future_cost)}{Prisma.RST}")
        return dissent_log

class TheSlashCouncil:
    def __init__(self):
        self.active = False
        c_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        self.triggers = c_data.get("SLASH_TRIGGERS", ["[MOD:CODING]", "[SLASH]", "review this code", "refactor"])
        self.code_keywords = c_data.get("CODE_KEYWORDS", ["def ", "class ", "return ", "import ", "=>", "function", "struct "])
        self.rules = c_data.get("SLASH_RULES", {})

    def audit(self, text: str, physics: dict) -> tuple[bool, list[str], dict]:
        text_lower = text.lower()
        if any(t in text_lower for t in self.triggers):
            self.active = True
        is_coding = self.active or any(k in text_lower for k in self.code_keywords)
        if not is_coding:
            return False, [], {}
        logs = []
        corrections = {}
        r_pinker = self.rules.get("PINKER", ["var ", "x =", "data ="])
        r_fuller = self.rules.get("FULLER", ["import ", "class ", "def "])
        r_schur = self.rules.get("SCHUR", ["Exception", "try:", "catch"])
        r_meadows = self.rules.get("MEADOWS", ["while ", "for ", "queue", "recursion"])
        if any(k in text for k in r_pinker):
            msg = LoreManifest.get_instance().get_ux("council_strings", "slash_pinker") or ""
            logs.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
            corrections["gamma"] = -0.2
        else:
            corrections["gamma"] = 0.1
        if any(k in text for k in r_fuller):
            msg = LoreManifest.get_instance().get_ux("council_strings", "slash_fuller") or ""
            logs.append(f"{Prisma.BLU}{msg}{Prisma.RST}")
            corrections["sigma"] = 0.1
        if any(k in text for k in r_schur):
            msg = LoreManifest.get_instance().get_ux("council_strings", "slash_schur") or ""
            logs.append(f"{Prisma.GRN}{msg}{Prisma.RST}")
            corrections["eta"] = 0.2
            corrections["glimmers"] = 1
        if any(k in text_lower for k in r_meadows):
            msg = LoreManifest.get_instance().get_ux("council_strings", "slash_meadows") or ""
            logs.append(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
            corrections["theta"] = -0.1
        drag = physics.get("narrative_drag", 0.0)
        if drag > 5.0:
            corrections["upsilon"] = -0.3
            msg = LoreManifest.get_instance().get_ux("council_strings", "slash_integrity") or ""
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        return True, logs, corrections
