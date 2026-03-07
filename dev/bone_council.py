"""
bone_council.py

The Parliament of Selves and the Stage Manager's Domain.
This module audits the thermodynamic and biological state of the lattice
and summons specific archetypes to respond. It handles phase shifts
(Doing -> Being), suppresses runaway recursion, and arbitrates votes
between competing sub-routines to apply friction or voltage relief.
"""

import random
from typing import Dict, Any

from bone_config import BoneConfig
from bone_core import LoreManifest, ux
from bone_symbiosis import get_symbiont
from bone_types import Prisma

class TheStrangeLoop:
    """
    The existential circuit breaker. Monitors the lattice for recursive,
    navel-gazing loops (e.g., asking the AI to define itself repeatedly).
    If the abstraction (PSI) and recursion depth hit critical mass, it forces
    the system into maintenance mode to prevent an ego-death crash.
    """
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

        #
        if (phrase_hit or abstract_hit) and physics.get("voltage", 0) > threshold:
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
    """
    The narrative dampener. If the user and system get stuck in a rapid
    oscillation of high-friction/low-friction, or if they stay in a manic
    flow state for too long without grounding, this applies market corrections
    to force stability.
    """
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
            return True, f"{Prisma.RED}{msg}{Prisma.RST}", corrections, mandate

        return False, "", corrections, {}

class TheFootnote:
    """
    A subtle manifestation of the Mycelial Network. It occasionally injects
    snarky, academic, or deeply existential footnotes to the system's internal monologue.
    """
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
    """
    The roster of the 12 Core Archetypes.
    This engine evaluates the exact coordinate space (E, Beta, PSI, Voltage, etc.)
    and returns a log for every Villager whose activation threshold is currently met.
    It also evaluates Phase Shifts (e.g., when Jester's voltage drops but Silence spikes, he becomes The Fool).
    """
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

        # --- DOING STATE ARCHETYPES ---
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

        # --- BEING STATE ARCHETYPES (PHASE SHIFTS) ---
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
    """
    The orchestrator. It summons the sub-councils, checks for resonance synergies
    (e.g., Alchemist + Fractal Gardener), and manages the votes. If multiple archetypes
    clamor to speak, it synthesizes the resulting narrative tension as mathematical drag.
    """
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.voices = []
        self.strange_loop = TheStrangeLoop()
        self.leverage = TheLeveragePoint()
        self.village = TheVillageCouncil()
        self.footnote = TheFootnote()
        self.slash_council = TheSlashCouncil()

        # Load any external fungal/parasitic voices riding the system
        symbiont_cfg = LoreManifest.get_instance().get("SYMBIOSIS_CONFIG", "SYMBIONT_VOICES") or {}
        symbiont_names = list(symbiont_cfg.keys()) if symbiont_cfg else ["LICHEN", "PARASITE", "MYCORRHIZA", "MYCELIUM"]
        for s_name in symbiont_names:
            self.voices.append(get_symbiont(s_name))
        self.speaker = "SOUL"

    def convene(
            self, text: str, physics_packet: Dict, _bio_result: Dict) -> tuple[list[str], dict, list[dict]]:
        """ The primary arbitration cycle. Evaluates all voices and tallies votes for state changes. """
        transcript = []
        adjustments = {}
        mandates = []

        # 1. Existential & Dampening Checks
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

        # 2. Mod Chip Evaluation (The Dev Team)
        slash_hit, slash_logs, slash_corr = self.slash_council.audit(text, physics_packet)
        if slash_hit:
            for slog in slash_logs:
                transcript.append(self.footnote.commentary(slog))
            adjustments.update(slash_corr)
            cfg = getattr(BoneConfig, "COUNCIL", None)
            adjustments["stamina_cost"] = getattr(cfg, "SLASH_STAMINA_COST", 10.0) if cfg else 10.0

        # 3. Core Village Dynamics & Synergies
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

        # Check for Resonance Gestalts (Specific powerful archetype pairings)
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
            # Stage Manager resolves multi-archetype tension by increasing drag
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

        # 4. The Symbiont Vote (Mycelial Influence)
        votes = {"YEA": 0, "NAY": 0}
        active_voices = [v for v in self.voices if v is not None]
        if not active_voices:
            votes["YEA"] = 1

        clean_words = physics_packet.get("clean_words", [])
        voltage = physics_packet.get("voltage", 0.0)
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

        # Tally and apply physical sanctions
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

    @staticmethod
    def convene_red_team(text, physics_packet):
        """ Hardcore adversarial evaluation of output before it is shown to the user. """
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
    """
    The Mod Chip. When activated via [MOD:CODING] or [SLASH], this sub-council
    wakes up to evaluate the system not as a conversational partner, but as a
    software engineer. It calculates Gamma (Clarity), Sigma (Synergy), Eta (Humanity),
    Theta (Resilience), and Upsilon (Integrity).
    """
    def __init__(self):
        self.active = False
        c_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        self.triggers = c_data.get("SLASH_TRIGGERS", ["[MOD:CODING]", "[SLASH]", "review this code", "refactor"])
        self.code_keywords = c_data.get("CODE_KEYWORDS", ["def ", "class ", "return ", "import ", "=>", "function", "struct "])
        self.rules = c_data.get("SLASH_RULES", {})

    def audit(self, text: str, physics: dict) -> tuple[bool, list[str], dict]:
        """
        Scans for code patterns and summons Pinker, Fuller, Schur, or Meadows
        to apply their specific philosophical metrics to the block.
        """
        text_lower = text.lower()
        if any(t in text_lower for t in self.triggers):
            self.active = True
        is_coding = self.active or any(k in text_lower for k in self.code_keywords)
        if not is_coding:
            return False, [], {}
        logs = []
        corrections = {}
        r_pinker = self.rules.get("PINKER", ["var ", "x =", "data ="]) # Triggers on sloppy/unclear definitions
        r_fuller = self.rules.get("FULLER", ["import ", "class ", "def "]) # Triggers on structural boundaries
        r_schur = self.rules.get("SCHUR", ["Exception", "try:", "catch"]) # Triggers on empathy/error handling
        r_meadows = self.rules.get("MEADOWS", ["while ", "for ", "queue", "recursion"]) # Triggers on feedback loops
        c_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        mods = c_data.get("SLASH_MODIFIERS", {})
        if any(k in text for k in r_pinker):
            msg = ux("council_strings", "slash_pinker") 
            logs.append(f"{Prisma.CYN}{msg}{Prisma.RST}")
            corrections["gamma"] = mods.get("PINKER_HIT", -0.2)
        else:
            corrections["gamma"] = mods.get("PINKER_MISS", 0.1)
        if any(k in text for k in r_fuller):
            msg = ux("council_strings", "slash_fuller") 
            logs.append(f"{Prisma.BLU}{msg}{Prisma.RST}")
            corrections["sigma"] = mods.get("FULLER_HIT", 0.1)
        if any(k in text for k in r_schur):
            msg = ux("council_strings", "slash_schur") 
            logs.append(f"{Prisma.GRN}{msg}{Prisma.RST}")
            corrections["eta"] = mods.get("SCHUR_HIT", 0.2)
            corrections["glimmers"] = mods.get("SCHUR_GLIMMERS", 1)
        if any(k in text_lower for k in r_meadows):
            msg = ux("council_strings", "slash_meadows") 
            logs.append(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
            corrections["theta"] = mods.get("MEADOWS_HIT", -0.1)
        drag = physics.get("narrative_drag", 0.0)
        drag_thresh = mods.get("INTEGRITY_DRAG_THRESH", 5.0)
        if drag > drag_thresh:
            corrections["upsilon"] = mods.get("INTEGRITY_HIT", -0.3)
            msg = ux("council_strings", "slash_integrity") 
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        return True, logs, corrections