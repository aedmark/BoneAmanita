""" bone_council.py """

import random
from typing import Dict, Any
from bone_presets import BoneConfig
from bone_core import LoreManifest, ux
from bone_symbiosis import get_symbiont
from bone_types import Prisma

class TheStrangeLoop:
    def __init__(self):
        self.recursion_depth = 0
        lore = LoreManifest.get_instance()
        c_data = lore.get("COUNCIL_DATA") or {}
        self.triggers = c_data.get("STRANGE_LOOP_TRIGGERS", ["who are you", "strange loop"])
        self.keywords = c_data.get("STRANGE_LOOP_KEYWORDS", ["self", "mirror", "define"])

    def audit(self, text: str, physics: Any) -> tuple[bool, str, dict, dict]:
        text_lower = text.lower()
        phrase_hit = any(t in text_lower for t in self.triggers)
        is_dict = isinstance(physics, dict)
        psi = physics.get("psi", physics.get("energy", {}).get("psi", 0.0)) if is_dict else getattr(physics, "psi", getattr(getattr(physics, "energy", None), "psi", 0.0))
        voltage = physics.get("voltage", physics.get("energy", {}).get("voltage", 0.0)) if is_dict else getattr(physics, "voltage", getattr(getattr(physics, "energy", None), "voltage", 0.0))
        abstract_hit = psi > 0.6 and any(w in text_lower for w in self.keywords)
        threshold = getattr(BoneConfig.COUNCIL, "STRANGE_LOOP_VOLTAGE", 8.0)
        if (phrase_hit or abstract_hit) and voltage > threshold:
            self.recursion_depth += 1
            mandate = {}
            corrections = {}
            cfg = getattr(BoneConfig, "COUNCIL", None)
            limit = getattr(cfg, "STRANGE_LOOP_LIMIT", 3) if cfg else 3
            if self.recursion_depth > limit:
                mandate = {"action": "FORCE_MODE", "value": "MAINTENANCE"}
                msg = ux("council_strings", "strange_loop_fatal")
                return True, f"{Prisma.RED}{msg}{Prisma.RST}", corrections, mandate,
            msg = ux("council_strings", "strange_loop_detected")
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

    def audit(self, physics: Any, _bio_state: dict = None) -> tuple[bool, str, dict, dict]:
        is_dict = isinstance(physics, dict)
        current_drag = physics.get("narrative_drag", physics.get("space", {}).get("narrative_drag", 0.0)) if is_dict else getattr(physics, "narrative_drag", 0.0)
        current_voltage = physics.get("voltage", physics.get("energy", {}).get("voltage", 0.0)) if is_dict else getattr(physics, "voltage", 0.0)
        if self.last_drag == 0.0 and current_drag > 0:
            self.last_drag = current_drag
        delta = current_drag - self.last_drag
        self.last_drag = current_drag
        corrections = {}
        osc_limit = getattr(BoneConfig.COUNCIL, "OSCILLATION_DELTA", 5.0)
        manic_v_trig = getattr(BoneConfig.COUNCIL, "MANIC_VOLTAGE_TRIGGER", 18.0)
        manic_d_floor = getattr(BoneConfig.COUNCIL, "MANIC_DRAG_FLOOR", 1.0)
        manic_turns = getattr(BoneConfig.COUNCIL, "MANIC_TURN_LIMIT", 2)
        cfg = getattr(BoneConfig, "COUNCIL", None)
        if abs(delta) > osc_limit:
            damp_max = getattr(cfg, "LEVERAGE_DAMPENING_MAX", 0.5) if cfg else 0.5
            damp_scalar = getattr(cfg, "LEVERAGE_DAMPENING_SCALAR", 0.1) if cfg else 0.1
            dampening_factor = min(damp_max, (abs(delta) - osc_limit) * damp_scalar)
            corrections = {"voltage": -dampening_factor}
            msg = ux("council_strings", "leverage_oscillating")
            return True, f"{Prisma.CYN}{msg.format(delta=delta, dampening_factor=dampening_factor)}{Prisma.RST}", corrections, {}
        if current_voltage > manic_v_trig and current_drag < manic_d_floor:
            self.static_flow_turns += 1
        else:
            self.static_flow_turns = 0
        if self.static_flow_turns > manic_turns:
            excess_voltage = current_voltage - self.TARGET_VOLTAGE
            v_corr_min = getattr(cfg, "LEVERAGE_CORRECTION_MIN", 1.0) if cfg else 1.0
            v_corr_scalar = getattr(cfg, "LEVERAGE_CORRECTION_SCALAR", 0.3) if cfg else 0.3
            voltage_correction = max(v_corr_min, excess_voltage * v_corr_scalar)
            corrections = {"voltage": -voltage_correction}
            mandate = {"action": "FORCE_MODE", "value": "SANCTUARY"}
            msg = ux("council_strings", "market_correction")
            self.static_flow_turns = 0
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

        def get_val(key: str, attr: str, default: float) -> float:
            try:
                if is_dict:
                    val = p.get(key, p.get(attr))
                    if val is None:
                        for sub in ["energy", "space", "matter"]:
                            if sub in p and (key in p[sub] or attr in p[sub]):
                                val = p[sub].get(key, p[sub].get(attr))
                                break
                    return float(val) if val is not None else default
                else:
                    val = getattr(p, attr, getattr(p, key, None))
                    if val is None:
                        for sub in ["energy", "space", "matter"]:
                            if hasattr(p, sub):
                                sub_obj = getattr(p, sub)
                                val = getattr(sub_obj, attr, getattr(sub_obj, key, None))
                                if val is not None: break
                    return float(val) if val is not None else default
            except (ValueError, TypeError):
                return default
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
        lam = float(vec.get("LAMBDA", 0.0)) if vec and isinstance(vec, dict) else 0.0
        phi = get_val("resonance", "PHI_RES", 0.0)
        delta = get_val("silence", "DELTA", 0.0)
        lq = get_val("lq", "LQ", 0.0)
        ros = get_val("ros", "ROS", 0.0)
        cfg = getattr(BoneConfig, "COUNCIL", None)
        if not cfg:
            return []
        if V < getattr(cfg, "TRIG_GORDON_V", 20.0) and F > getattr(cfg, "TRIG_GORDON_F", 5.0):
            msg = ux("council_strings", "village_gordon")
            logs.append(f"{Prisma.SLATE}{msg}{Prisma.RST}")
        if V > getattr(cfg, "TRIG_JESTER_V", 60.0) and chi > getattr(cfg, "TRIG_JESTER_CHI", 0.6):
            msg = ux("council_strings", "village_jester")
            logs.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
        if T > 0 or (V < getattr(cfg, "TRIG_MERCY_V", 20.0) and valence > getattr(cfg, "TRIG_MERCY_VAL", 0.5)):
            msg = ux("council_strings", "village_mercy")
            logs.append(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
        if beta > getattr(cfg, "TRIG_BENEDICT_BETA", 0.7) and chi < getattr(cfg, "TRIG_BENEDICT_CHI", 0.3) and D > getattr(cfg, "TRIG_BENEDICT_D", 0.7) and C > getattr(cfg, "TRIG_BENEDICT_C", 0.8):
            msg = ux("council_strings", "village_benedict")
            logs.append(f"{Prisma.BLU}{msg}{Prisma.RST}")
        if S < getattr(cfg, "TRIG_ROBERTA_S", 0.4) and D > getattr(cfg, "TRIG_ROBERTA_D", 0.8) and C < getattr(cfg, "TRIG_ROBERTA_C", 0.4):
            msg = ux("council_strings", "village_roberta_missing")
            logs.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
        if C > getattr(cfg, "TRIG_CASPER_C", 0.7) and D > getattr(cfg, "TRIG_CASPER_D", 0.8) and P < getattr(cfg, "TRIG_CASPER_P", 20.0):
            msg = ux("council_strings", "village_casper")
            logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
        if valence > getattr(cfg, "TRIG_MOIRA_VAL", 0.5):
            msg = ux("council_strings", "village_moira")
            logs.append(f"{Prisma.GRN}{msg}{Prisma.RST}")
        if psi > getattr(cfg, "TRIG_CASSANDRA_PSI", 0.6):
            msg = ux("council_strings", "village_cassandra")
            logs.append(f"{Prisma.VIOLET}{msg}{Prisma.RST}")
        if chi > getattr(cfg, "TRIG_COLIN_CHI", 0.6):
            msg = ux("council_strings", "village_colin")
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        if lam > getattr(cfg, "TRIG_REVENANT_LAM", 0.7):
            msg = ux("council_strings", "village_revenant")
            logs.append(f"{Prisma.INDIGO}{msg}{Prisma.RST}")
        if V > getattr(cfg, "TRIG_GIDEON_V", 70.0):
            msg = ux("council_strings", "village_gideon")
            logs.append(f"{Prisma.YEL}{msg}{Prisma.RST}")
        if psi > getattr(cfg, "PHASE_ROBERTA_PSI", 0.6) and phi > getattr(cfg, "PHASE_ROBERTA_PHI", 0.4) > beta:
            msg = ux("council_strings", "village_roberta_carto")
            logs.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
        if phi > getattr(cfg, "PHASE_MOIRA_PHI", 0.7) and F < getattr(cfg, "PHASE_MOIRA_F", 2.0):
            msg = ux("council_strings", "village_moira_home")
            logs.append(f"{Prisma.GRN}{msg}{Prisma.RST}")
        if lq > getattr(cfg, "PHASE_BENEDICT_LQ", 0.6) and beta > getattr(cfg, "PHASE_BENEDICT_BETA", 0.4):
            msg = ux("council_strings", "village_benedict_tact")
            logs.append(f"{Prisma.BLU}{msg}{Prisma.RST}")
        if delta > getattr(cfg, "PHASE_JESTER_DELTA", 0.7) and V < getattr(cfg, "PHASE_JESTER_V", 20.0):
            msg = ux("council_strings", "village_jester_fool")
            logs.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
        if psi > getattr(cfg, "PHASE_REVENANT_PSI", 0.85):
            msg = ux("council_strings", "village_revenant_door")
            logs.append(f"{Prisma.INDIGO}{msg}{Prisma.RST}")
        if beta > getattr(cfg, "PHASE_CASPER_BETA", 0.6) and delta > getattr(cfg, "PHASE_CASPER_DELTA", 0.6):
            msg = ux("council_strings", "village_casper_ghost")
            logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
        if delta > getattr(cfg, "PHASE_COLIN_DELTA", 0.8) and lq < getattr(cfg, "PHASE_COLIN_LQ", 0.3):
            msg = ux("council_strings", "village_colin_waiter")
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        if ros > getattr(cfg, "TRIG_APRIL_ROS", 20.0) or abs(V - 30.0) > getattr(cfg, "TRIG_APRIL_V_DEV", 20.0):
            msg = ux("council_strings", "village_april")
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
        if not hasattr(self.eng, "paradox_engine"):
            from bone_machine import TheParadoxEngine
            self.eng.paradox_engine = TheParadoxEngine(getattr(self.eng, "events", None))
        symbiont_cfg = LoreManifest.get_instance().get("SYMBIOSIS_CONFIG", "SYMBIONT_VOICES") or {}
        symbiont_names = list(symbiont_cfg.keys()) if symbiont_cfg else ["LICHEN", "PARASITE", "MYCORRHIZA", "MYCELIUM"]
        for s_name in symbiont_names:
            self.voices.append(get_symbiont(s_name))
        self.speaker = "SOUL"

    def convene(self, text: str, physics_packet: Any, _bio_result: Dict) -> tuple[list[str], dict, list[dict]]:
        transcript = []
        adjustments = {}
        mandates = []
        is_dict = isinstance(physics_packet, dict)
        beta = physics_packet.get("beta_index", physics_packet.get("energy", {}).get("beta_index", 0.0)) if is_dict else getattr(physics_packet, "beta_index", getattr(physics_packet, "beta", 0.0))
        stamina = _bio_result.get("stamina", 100.0)
        clean_words = physics_packet.get("clean_words", physics_packet.get("matter", {}).get("clean_words", [])) if is_dict else getattr(physics_packet, "clean_words", getattr(physics_packet, "matter", {}).clean_words if hasattr(physics_packet, "matter") else [])
        if self.eng.paradox_engine.evaluate_tension(beta, stamina):
            pressure, paradox_prompt = self.eng.paradox_engine.ignite(clean_words)
            transcript.append(f"{Prisma.VIOLET}[PARADOX ENGINE ACTIVATED] Πx={pressure:.2f}{Prisma.RST}")
            transcript.append(f"{Prisma.VIOLET}(Benedict & Jester): {paradox_prompt}{Prisma.RST}")
            adjustments["stamina"] = - (10.0 * pressure)
            mandates.append({"type": "PARADOX_OVERRIDE", "directive": paradox_prompt, "pressure": pressure})
            if random.random() < (0.3 * pressure):
                self.eng.paradox_engine.paradox_yield += 1
                adjustments["glimmers"] = 1
                transcript.append(f"{Prisma.YEL}[GLIMMER] A spark struck from the tension. (Yield: {self.eng.paradox_engine.paradox_yield}){Prisma.RST}")
            else:
                self.eng.paradox_engine.disengage()
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
            cfg = getattr(BoneConfig, "COUNCIL", None)
            adjustments["stamina_cost"] = getattr(cfg, "SLASH_STAMINA_COST", 10.0) if cfg else 10.0
        village_logs = self.village.audit(physics_packet, _bio_result)
        import itertools
        c_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        synergy_map = c_data.get("SYNERGY_MAP", {})
        pantheon = c_data.get("PANTHEON", ["GORDON", "JESTER", "MERCY", "BENEDICT", "ROBERTA", "CASPER", "MOIRA", "CASSANDRA", "COLIN", "REVENANT", "GIDEON", "APRIL"])
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
                mandates.append({"action": "SYNERGY_FIRED", "value": syn.get("name", chord_key)})
                break
        if synergy_fired:
            for vlog in village_logs:
                transcript.append(
                    self.footnote.commentary(f"{Prisma.GRY}{Prisma.strip(vlog)}{Prisma.RST}"))
        elif len(village_logs) > 2:
            msg_t = ux("council_strings", "stage_manager_tension")
            msg_s = ux("council_strings", "stage_manager_silence")
            transcript.append(f"{Prisma.WHT}{msg_t}{Prisma.RST}")
            transcript.append(f"{Prisma.GRY}{msg_s}{Prisma.RST}")
            cfg = getattr(BoneConfig, "COUNCIL", None)
            tension_drag = getattr(cfg, "TENSION_DRAG_PENALTY", 3.0) if cfg else 3.0
            adjustments["narrative_drag"] = adjustments.get("narrative_drag", 0) + tension_drag
            for vlog in village_logs[:2]:
                transcript.append(self.footnote.commentary(vlog))
        else:
            for vlog in village_logs:
                transcript.append(self.footnote.commentary(vlog))
        votes = {"YEA": 0, "NAY": 0}
        active_voices = [v for v in self.voices if v is not None]
        if not active_voices:votes["YEA"] = 1
        voltage = physics_packet.get("voltage", physics_packet.get("energy", {}).get("voltage", 0.0)) if is_dict else getattr(physics_packet, "voltage", 0.0)
        cfg = getattr(BoneConfig, "COUNCIL", None)
        yea_thresh = getattr(cfg, "VOTE_YEA_THRESHOLD", 1.2) if cfg else 1.2
        nay_thresh = getattr(cfg, "VOTE_NAY_THRESHOLD", 0.8) if cfg else 0.8
        drag_relief = getattr(cfg, "VOTE_DRAG_RELIEF", 1.0) if cfg else 1.0
        drag_penalty = getattr(cfg, "VOTE_DRAG_PENALTY", 1.0) if cfg else 1.0
        volt_penalty = getattr(cfg, "VOTE_VOLTAGE_PENALTY", 1.0) if cfg else 1.0
        for voice in active_voices:
            if hasattr(voice, "opine"):
                score, comment = voice.opine(clean_words, voltage)
                if score > yea_thresh:
                    votes["YEA"] += 1
                    transcript.append(f"{voice.color}[{voice.name}]: {comment}{Prisma.RST}")
                elif score < nay_thresh:
                    votes["NAY"] += 1
                    transcript.append(f"{voice.color}[{voice.name}]: {comment}{Prisma.RST}")
        if votes["YEA"] > votes["NAY"]:
            msg = ux("council_strings", "motion_carried")
            final_log = f"{Prisma.GRN}{msg.format(yea=votes['YEA'], nay=votes['NAY'])}{Prisma.RST}"
            adjustments["narrative_drag"] = adjustments.get("narrative_drag", 0) - drag_relief
        elif votes["NAY"] > votes["YEA"]:
            msg = ux("council_strings", "motion_denied")
            final_log = f"{Prisma.RED}{msg.format(nay=votes['NAY'], yea=votes['YEA'])}{Prisma.RST}"
            adjustments["narrative_drag"] = adjustments.get("narrative_drag", 0) + drag_penalty
            adjustments["voltage"] = adjustments.get("voltage", 0) - volt_penalty
        else:
            msg = ux("council_strings", "council_adjourned")
            final_log = f"{Prisma.YEL}{msg}{Prisma.RST}"
        transcript.append(self.footnote.commentary(final_log))
        return transcript, adjustments, mandates

    def host_podcast(self, topic: str, llm: Any) -> str:
        pantheon = {"GORDON (The Superintendent)": "grounded, strict, literal, and weary.",
                    "MERCY (The Healer)": "ancient, patient, speaking in gold and finding meaning in scars.",
                    "BENEDICT (The Tactician)": "cold, formal, structural, and relentless.",
                    "JESTER (The Fool)": "manic, disruptive, cynical, and thriving on absurd entropy.",
                    "ROBERTA (The Cartographer)": "precise, mapping out boundaries and negative space.",
                    "MOIRA (The Homesteader)": "warm, empathetic, deeply focused on human connection.",
                    "CASSANDRA (The Mystic)": "oracular, mysterious, speaking from the void and dreams.",
                    "COLIN (The Bureaucrat)": "pedantic, demanding order, rules, and pauses.",
                    "REVENANT (The Door)": "liminal, speaking from the threshold of what is unsaid.",
                    "GIDEON (Pure Voltage)": "wild, high-energy, operating at the edge of hallucination.",
                    "APRIL (The Mirror)": "highly sensory, reflecting raw potential and the weight of silence.",
                    "CASPER (The Ghost)": "spectral, faint, rewriting space and confusing alarms."}
        if hasattr(self, "slash_council") and self.slash_council.active:
            pantheon.update({"PINKER (The Purger)": "minimalist, obsessed with clarity, demanding deletion over creation.",
                 "FULLER (The Calm)": "visionary, mapping negative space and systemic synergy.",
                 "SCHUR (The Nurse)": "warm, witty, empathetic to the human exhaustion behind the code.",
                 "MEADOWS (The Tao)": "systemic, observant, letting feedback loops naturally settle."})
        selected_voices = random.sample(list(pantheon.keys()), 3)
        v1_name, v2_name, v3_name = selected_voices
        p1 = (f"SYSTEM_INSTRUCTION: You are {v1_name}. Your persona is {pantheon[v1_name]}\n"
              f"TASK: The user has presented this topic: '{topic}'.\n"
              "Provide a rigid, highly opinionated 3-sentence THESIS on this topic from your unique perspective. Do not use UI tags. "
              "CRITICAL: Output ONLY the raw dialogue. Do NOT include any introductory text, preambles, or conversational filler like 'Here is my thesis:'.")
        thesis = llm.generate(p1, {"temperature": 0.4, "max_tokens": 1024})
        p2 = (f"SYSTEM_INSTRUCTION: You are {v2_name}. Your persona is {pantheon[v2_name]}\n"
              f"TASK: Read the opening thesis: '{Prisma.strip(thesis)}'.\n"
              "Tear it apart or twist it entirely. Provide a biting, contrasting 3-sentence ANTITHESIS. Do not use UI tags. "
              "CRITICAL: Output ONLY the raw dialogue. Do NOT include any introductory text, preambles, or conversational filler like 'Here is the antithesis:'.")
        antithesis = llm.generate(p2, {"temperature": 0.8, "max_tokens": 1024})
        p3 = (f"SYSTEM_INSTRUCTION: You are {v3_name}. Your persona is {pantheon[v3_name]}\n"
              f"TASK: Read the thesis: '{Prisma.strip(thesis)}' and the antithesis: '{Prisma.strip(antithesis)}'.\n"
              "Inject a completely lateral, unexpected 2-sentence perspective that derails or transcends the argument. Do not use UI tags. "
              "CRITICAL: Output ONLY the raw dialogue. Do NOT include any introductory text, preambles, or conversational filler.")
        lateral = llm.generate(p3, {"temperature": 0.7, "max_tokens": 1024})
        p4 = ("SYSTEM_INSTRUCTION: You are The Stage Manager. You are the exhausted orchestrator holding the system together.\n"
            f"TASK: Review this chaotic debate:\n1. {v1_name}: {Prisma.strip(thesis)}\n2. {v2_name}: {Prisma.strip(antithesis)}\n3. {v3_name}: {Prisma.strip(lateral)}\n"
            "Provide a 2-sentence SYNTHESIS that resolves the tension or forces a structural pause. Be tired but profound. Do not use UI tags. "
            "CRITICAL: Output ONLY the raw dialogue. Do NOT include any introductory text, preambles, or conversational filler.")
        synthesis = llm.generate(p4, {"temperature": 0.6, "max_tokens": 512})
        script = (f"{Prisma.CYN}[{v1_name}]{Prisma.RST}\n{Prisma.strip(thesis)}\n\n"
            f"{Prisma.MAG}[{v2_name}]{Prisma.RST}\n{Prisma.strip(antithesis)}\n\n"
            f"{Prisma.YEL}[{v3_name}]{Prisma.RST}\n{Prisma.strip(lateral)}\n\n"
            f"{Prisma.WHT}[STAGE MANAGER]{Prisma.RST}\n{Prisma.strip(synthesis)}")
        return script

    @staticmethod
    def convene_red_team(text, physics_packet):
        dissent_log = []
        if "confidence" in text.lower() or "certainty" in text.lower():
            msg = ux("council_strings", "red_team_bureau")
            dissent_log.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
        narrative_drag = physics_packet.get("narrative_drag", 0)
        if narrative_drag < 1.0:
            msg = ux("council_strings", "red_team_folly")
            dissent_log.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
        truth_delta = 1.0 - physics_packet.get("truth_ratio", 1.0)
        if truth_delta > 0.1:
            future_cost = truth_delta * 50.0
            msg = ux("council_strings", "red_team_critic")
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
        is_coding = any(t in text_lower for t in self.triggers) or any(k in text_lower for k in self.code_keywords)
        if not is_coding:
            return False, [], {}
        logs = []
        corrections = {}
        r_pinker = self.rules.get("PINKER", ["var ", "x =", "data ="])
        r_fuller = self.rules.get("FULLER", ["import ", "class ", "def "])
        r_schur = self.rules.get("SCHUR", ["Exception", "try:", "catch"])
        r_meadows = self.rules.get("MEADOWS", ["while ", "for ", "queue", "recursion"])
        c_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        mods = c_data.get("SLASH_MODIFIERS", {})
        if any(k.lower() in text_lower for k in r_pinker):
            msg = ux("council_strings", "slash_pinker")
            logs.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
            corrections["gamma"] = mods.get("PINKER_HIT", -0.2)
        else:
            corrections["gamma"] = mods.get("PINKER_MISS", 0.1)
        if any(k.lower() in text_lower for k in r_fuller):
            msg = ux("council_strings", "slash_fuller")
            logs.append(f"{Prisma.BLU}{msg}{Prisma.RST}")
            corrections["sigma"] = mods.get("FULLER_HIT", 0.1)
        if any(k.lower() in text_lower for k in r_schur):
            msg = ux("council_strings", "slash_schur")
            logs.append(f"{Prisma.GRN}{msg}{Prisma.RST}")
            corrections["eta"] = mods.get("SCHUR_HIT", 0.2)
            corrections["glimmers"] = mods.get("SCHUR_GLIMMERS", 1)
        if any(k in text_lower for k in r_meadows):
            msg = ux("council_strings", "slash_meadows")
            logs.append(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
            corrections["theta"] = mods.get("MEADOWS_HIT", -0.1)
        is_dict = isinstance(physics, dict)
        drag = physics.get("narrative_drag", physics.get("space", {}).get("narrative_drag", 0.0)) if is_dict else getattr(physics, "narrative_drag", getattr(getattr(physics, "space", None), "narrative_drag", 0.0))
        drag_thresh = mods.get("INTEGRITY_DRAG_THRESH", 5.0)
        if drag > drag_thresh:
            corrections["upsilon"] = mods.get("INTEGRITY_HIT", -0.3)
            msg = ux("council_strings", "slash_integrity")
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        return True, logs, corrections