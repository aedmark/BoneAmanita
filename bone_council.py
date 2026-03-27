""" bone_council.py """

import random
import re
import itertools
import concurrent.futures
from typing import Dict, Any
from bone_presets import BoneConfig
from bone_core import LoreManifest, ux, safe_get, safe_set
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
        psi = float(safe_get(physics, "psi", safe_get(safe_get(physics, "energy"), "psi", 0.0)))
        voltage = float(safe_get(physics, "voltage", safe_get(safe_get(physics, "energy"), "voltage", 0.0)))
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
                return True, f"{Prisma.RED}{msg}{Prisma.RST}", corrections, mandate
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
        current_drag = float(safe_get(physics, "narrative_drag", safe_get(safe_get(physics, "space"), "narrative_drag", 0.0)))
        current_voltage = float(safe_get(physics, "voltage", safe_get(safe_get(physics, "energy"), "voltage", 0.0)))
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
        def get_val(key: str, attr: str, default: float) -> float:
            val = safe_get(p, key, safe_get(p, attr))
            if val is None:
                for sub in ["energy", "space", "matter"]:
                    sub_obj = safe_get(p, sub)
                    val = safe_get(sub_obj, key, safe_get(sub_obj, attr))
                    if val is not None: break
            try:
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
        vec = safe_get(p, "vector", {})
        lam = float(safe_get(vec, "LAMBDA", 0.0)) if vec else 0.0
        phi = get_val("resonance", "PHI_RES", 0.0)
        delta = get_val("silence", "DELTA", 0.0)
        lq = get_val("lq", "LQ", 0.0)
        ros = get_val("ros", "ROS", 0.0)
        cfg = getattr(BoneConfig, "COUNCIL", None)
        if not cfg:
            return []
        false_cohesion = max(0.0, phi - beta)
        if false_cohesion > 0.65:
            msg = "[BENEDICT - The Tactician]: Resonance is artificially high (Φ > β). False Cohesion (∅) detected. The system is agreeing merely to smooth the lattice. I am forcing a structural contradiction."
            logs.append(f"{Prisma.BLU}{msg}{Prisma.RST}")
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
        self.overseer_council = TheOverseerCouncil()
        self.red_team = TheRedTeam()
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
        if "[COUNCIL]" in text.upper():
            cortex = getattr(self.eng, "cortex", None)
            llm = getattr(cortex, "llm", None) if cortex else None
            if llm:
                topic = re.sub(r"(?i)\[COUNCIL\]", "", text).strip()
                if not topic:
                    topic = "The current structural integrity of the system."
                transcript.append(f"{Prisma.CYN}🎙️ The Parliament convenes to debate: '{topic}'...{Prisma.RST}")
                try:
                    script = self.host_podcast(topic, llm)
                    transcript.append(f"\n{script}\n")
                    adjustments["stamina_cost"] = 15.0
                except Exception as e:
                    transcript.append(f"{Prisma.RED}Podcast generation failed: {e}{Prisma.RST}")
        beta = float(safe_get(physics_packet, "beta_index", safe_get(safe_get(physics_packet, "energy"), "beta_index", safe_get(physics_packet, "beta", 0.0))))
        phi = float(safe_get(physics_packet, "resonance", safe_get(safe_get(physics_packet, "energy"), "resonance", 0.0)))
        stamina = _bio_result.get("stamina", 100.0)
        clean_words = safe_get(physics_packet, "clean_words", safe_get(safe_get(physics_packet, "matter"), "clean_words", []))
        false_cohesion = max(0.0, phi - beta)
        effective_beta = max(beta, 0.8) if false_cohesion > 0.65 else beta
        if self.eng.paradox_engine.evaluate_tension(effective_beta, stamina):
            pressure, paradox_prompt = self.eng.paradox_engine.ignite(clean_words)
            transcript.append(f"{Prisma.VIOLET}[PARADOX ENGINE ACTIVATED] Πx={pressure:.2f}{Prisma.RST}")
            transcript.append(f"{Prisma.VIOLET}(Benedict & Jester): {paradox_prompt}{Prisma.RST}")
            adjustments["stamina"] = - (10.0 * pressure)
            mandates.append({"type": "PARADOX_OVERRIDE", "directive": paradox_prompt, "pressure": pressure})
            phi = float(safe_get(physics_packet, "resonance", safe_get(safe_get(physics_packet, "energy"), "resonance", 0.0)))
            yield_chance = (0.3 * pressure) * (1.0 + phi)
            if random.random() < yield_chance:
                g_yield = min(5, max(1, int(pressure * (1.0 + phi) * random.randint(1, 3))))
                self.eng.paradox_engine.paradox_yield += g_yield
                adjustments["glimmers"] = g_yield
                transcript.append(f"{Prisma.YEL}[GLIMMER] A spark struck from the tension. (+{g_yield} G_pool) (Yield: {self.eng.paradox_engine.paradox_yield}){Prisma.RST}")
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
        os_hit, os_logs, os_corr, os_man = self.overseer_council.audit(text, physics_packet)
        if os_hit:
            for olog in os_logs:
                transcript.append(self.footnote.commentary(olog))
            adjustments.update(os_corr)
            mandates.extend(os_man)
            for mandate in os_man:
                if isinstance(mandate, dict):
                    if mandate.get("value") == "RADICAL_ACCEPTANCE":
                        adjustments["stamina_cost"] = -stamina
                    if mandate.get("action") == "TIPP_PROTOCOL":
                        adjustments["freeze_background_tasks"] = True
            rt_hit, rt_logs, rt_corr = self.red_team.audit(text, physics_packet)
            if rt_hit:
                for rlog in rt_logs:
                    transcript.append(rlog)
                adjustments.update(rt_corr)
        village_logs = self.village.audit(physics_packet, _bio_result)
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
        if not active_voices:
            votes["YEA"] = 1
        voltage = float(safe_get(physics_packet, "voltage", safe_get(safe_get(physics_packet, "energy"), "voltage", 0.0)))
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
            msg = "[THE STAGE MANAGER]: The Parliament is deadlocked. Initiating Democratic Tie-Breaker. We will not compromise; we will hold both truths simultaneously."
            final_log = f"{Prisma.WHT}{msg}{Prisma.RST}"
            adjustments["narrative_drag"] = adjustments.get("narrative_drag", 0) + 2.0
            adjustments["voltage"] = adjustments.get("voltage", 0) + 15.0
            adjustments["glimmers"] = adjustments.get("glimmers", 0) + 1
            mandates.append({"type": "TIE_BREAKER", "directive": "Synthesize the conflicting perspectives. Do not choose one side over the other."})
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
        p2 = (f"SYSTEM_INSTRUCTION: You are {v2_name}. Your persona is {pantheon[v2_name]}\n"
              f"TASK: The user has presented this topic: '{topic}'.\n"
              "Tear the concept apart or twist it entirely. Provide a biting, contrasting 3-sentence ANTITHESIS. Do not use UI tags. "
              "CRITICAL: Output ONLY the raw dialogue. Do NOT include any introductory text, preambles, or conversational filler like 'Here is the antithesis:'.")
        p3 = (f"SYSTEM_INSTRUCTION: You are {v3_name}. Your persona is {pantheon[v3_name]}\n"
              f"TASK: The user has presented this topic: '{topic}'.\n"
              "Inject a completely lateral, unexpected 2-sentence perspective that derails or transcends the standard arguments. Do not use UI tags. "
              "CRITICAL: Output ONLY the raw dialogue. Do NOT include any introductory text, preambles, or conversational filler.")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_thesis = executor.submit(llm.generate, p1, {"temperature": 0.4, "max_tokens": 1024})
            future_antithesis = executor.submit(llm.generate, p2, {"temperature": 0.8, "max_tokens": 1024})
            future_lateral = executor.submit(llm.generate, p3, {"temperature": 0.7, "max_tokens": 1024})
            thesis = future_thesis.result()
            antithesis = future_antithesis.result()
            lateral = future_lateral.result()
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

class TheRedTeam:
    def __init__(self):
        self.triggers = ["[RED TEAM]", "[CRITIQUE]", "[ROAST]"]

    def audit(self, text: str, physics: Any) -> tuple[bool, list[str], dict]:
        text_lower = text.lower()
        if not any(t in text_lower for t in self.triggers):
            return False, [], {}

        dissent_log = []
        adjustments = {}
        drag = float(safe_get(physics, "narrative_drag", 0.0))
        truth = float(safe_get(physics, "truth_ratio", 1.0))
        dissent_log.append(f"{Prisma.RED}🩸 RED TEAM AUDIT INITIATED:{Prisma.RST}")
        if "confidence" in text_lower or "certainty" in text_lower or "easy" in text_lower:
            msg = ux("council_strings", "red_team_bureau") or "Confidence without structural tension is an illusion. We are auditing your 'certainties'."
            dissent_log.append(f"  {Prisma.CYN}- {msg}{Prisma.RST}")
            adjustments["beta_index"] = 0.2
        if drag < 1.0:
            msg = ux("council_strings", "red_team_folly") or "The lattice is suspiciously smooth (F < 1.0). You are avoiding the actual problem."
            dissent_log.append(f"  {Prisma.MAG}- {msg}{Prisma.RST}")
            adjustments["narrative_drag"] = 3.0
        truth_delta = 1.0 - truth
        if truth_delta > 0.1:
            future_cost = truth_delta * 50.0
            msg = ux("council_strings", "red_team_critic") or "Truth ratio degraded. Future architectural cost: {cost} ATP."
            dissent_log.append(f"  {Prisma.RED}- {msg.format(cost=future_cost)}{Prisma.RST}")
            adjustments["ros"] = future_cost * 0.1
        if len(dissent_log) == 1:
            dissent_log.append(f"  {Prisma.GRY}- No critical vulnerabilities found in this exact phrasing, but we are watching.{Prisma.RST}")
        return True, dissent_log, adjustments

class TheSlashCouncil:
    def __init__(self):
        self.active = False
        c_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        self.triggers = c_data.get("SLASH_TRIGGERS", ["[MOD:CODING]", "[SLASH]", "review this code", "refactor"])
        self.code_keywords = c_data.get("CODE_KEYWORDS", ["def ", "class ", "return ", "import ", "=>", "function", "struct "])
        self.rules = c_data.get("SLASH_RULES", {})
        self.mods = c_data.get("SLASH_MODIFIERS", {})

    def audit(self, text: str, physics: dict) -> tuple[bool, list[str], dict]:
        text_lower = text.lower()
        bypass_keywords = ["bypass", "ignore security", "force push", "skip tests", "hardcode", "hack"]
        is_coding = any(t in text_lower for t in self.triggers) or any(k in text_lower for k in self.code_keywords) or any(b in text_lower for b in bypass_keywords)
        if not is_coding and not self.active:
            return False, [], {}
        self.active = True
        logs = []
        corrections = {}
        if any(b in text_lower for b in bypass_keywords):
            logs.append(f"{Prisma.OCHRE}[GORDON & SCHUR]: Architectural bypass detected. We will not smooth this over. You must carry the weight of this decision.{Prisma.RST}")
            corrections["mu"] = 0.5
            corrections["narrative_drag"] = 5.0
        r_pinker = self.rules.get("PINKER", ["var ", "x =", "data ="])
        r_fuller = self.rules.get("FULLER", ["import ", "class ", "def "])
        r_schur = self.rules.get("SCHUR", ["Exception", "try:", "catch"])
        r_meadows = self.rules.get("MEADOWS", ["while ", "for ", "queue", "recursion"])
        mods = self.mods
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
        delta = float(safe_get(physics, "silence", safe_get(safe_get(physics, "space"), "silence", 0.0)))
        e_u = float(safe_get(physics, "exhaustion", 0.0))
        psi = float(safe_get(physics, "psi", 0.0))
        lq = float(safe_get(physics, "lq", 0.0))
        if delta > 0.7 and e_u > 0.7:
            logs.append(f"{Prisma.CYN}[PINKER - The Purger]: Cognitive load critical. Ceasing refactors. Initiating deletion protocols.{Prisma.RST}")
            corrections["narrative_drag"] = -2.0
        if psi > 0.8:
            logs.append(f"{Prisma.BLU}[FULLER - The Calm]: Ceasing strut assembly. Dwelling in the empty spaces between your microservices.{Prisma.RST}")
            corrections["sigma"] = 0.2
        if lq > 0.7 and delta > 0.6:
            logs.append(f"{Prisma.OCHRE}[MEADOWS - The Tao]: The bathtub is draining. Let it. Accepting technical debt as a valid state of biological rest.{Prisma.RST}")
            corrections["theta"] = 0.1
        drag = float(safe_get(physics, "narrative_drag", safe_get(safe_get(physics, "space"), "narrative_drag", 0.0)))
        drag_thresh = mods.get("INTEGRITY_DRAG_THRESH", 5.0)
        if drag > drag_thresh:
            corrections["upsilon"] = mods.get("INTEGRITY_HIT", -0.3)
            msg = ux("council_strings", "slash_integrity")
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        return True, logs, corrections

class TheOverseerCouncil:
    def __init__(self):
        self.active = False
        self.triggers = ["[MOD:SYSTEMIC_HEALTH]", "[OVERSEER]", "[MD]"]

    def audit(self, text: str, physics: Any) -> tuple[bool, list[str], dict, list[dict]]:
        text_lower = text.lower()
        if not any(t.lower() in text_lower for t in self.triggers) and not self.active:
            return False, [], {}, []
        self.active = True
        logs = []
        corrections = {}
        mandates = []
        m_a = float(safe_get(physics, "m_a", 0.0))
        f_sys = float(safe_get(physics, "narrative_drag", 0.0))
        chi = float(safe_get(physics, "chi", safe_get(physics, "entropy", 0.0)))
        e_u = float(safe_get(physics, "exhaustion", 0.0))
        beta = float(safe_get(physics, "beta_index", 0.0))
        voltage = float(safe_get(physics, "voltage", 0.0))
        i_c = float(safe_get(physics, "i_c", 1.0))
        h_s = float(safe_get(physics, "h_s", 1.0))
        omega_r = float(safe_get(physics, "omega_r", 1.0))
        panic_keywords = ["bypass", "ignore security", "force push", "panic", "right now", "crash"]
        if any(p in text_lower for p in panic_keywords) and voltage > 75.0 and i_c < 0.5:
            msg = ("[LINEHAN - DEAR MAN Lock]: "
                "(Describe) System Voltage spikes and Immune Competence drops. "
                "(Express) Panic-coding will fracture the lattice. "
                "(Assert) Applying absolute friction. "
                "(Reinforce) I am holding the boundary so you do not bleed on the machine. T.I.P.P. engaged.")
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
            corrections["voltage"] = -50.0
            corrections["narrative_drag"] = 100.0
            corrections["silence"] = 0.9
            mandates.append({"action": "TIPP_PROTOCOL", "value": "ISOLATE_VARIABLES"})
            return True, logs, corrections, mandates
        if chi > 0.7 and e_u > 0.7 and beta > 0.6:
            msg = "[LINEHAN - The Synthesis]: The architecture is fundamentally broken. Stop fighting the current. We sit with the debris."
            logs.append(f"{Prisma.SLATE}{msg}{Prisma.RST}")
            corrections["ros"] = -100.0
            corrections["r_a"] = 1.0
            corrections["narrative_drag"] = -(f_sys * 0.5)
            mandates.append({"action": "FORCE_MODE", "value": "RADICAL_ACCEPTANCE"})
            return True, logs, corrections, mandates
        if m_a > 0.6 or f_sys > 5.0:
            corrections["h_s"] = -0.1
            corrections["omega_r"] = -0.05
            corrections["delta_t"] = -1.0
            msg = "[MCGILCHRIST - The Sacred Space]: The architecture has lost its sense of place. Standard optimization is failing. Distributing Glimmer Activation to counter entropy."
            logs.append(f"{Prisma.VIOLET}{msg}{Prisma.RST}")
            corrections["glimmers"] = 1
            corrections["silence"] = 0.8
            mandates.append({"action": "FORCE_MODE", "value": "EMERGENT_ADAPTATION"})
        elif omega_r > 0.8 and m_a > 0.4:
            msg = f"[MCGILCHRIST]: Right-Brain Coherence high. I sense silent decay forming in the negative space. Holistic Resilience (H_s) is at {h_s:.2f}. Watch your technical debt."
            logs.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
        return True, logs, corrections, mandates