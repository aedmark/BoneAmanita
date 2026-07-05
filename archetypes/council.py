"""archetypes/council.py"""

import itertools
import random
import re
from typing import Any, Dict

from archetypes.symbiosis import get_symbiont
from constants import Prisma
from core import LoreManifest, safe_get, ux, ux_format
from presets import BoneConfig

class TheVillageCouncil:
    @staticmethod
    def audit(p: Any, _bio_state: dict) -> list[str]:
        logs = []

        def gv(k, d=0.0):
            return float(safe_get(p, k, d))

        V, F = gv("voltage", 30.0), gv("narrative_drag", 0.6)
        P = (
            float(_bio_state.get("stamina", 100.0))
            if _bio_state
            else gv("stamina", 100.0)
        )
        T = float(_bio_state.get("trauma", 0.0)) if _bio_state else gv("trauma", 0.0)
        beta, S, D, C = (
            gv("beta_index", 0.4),
            gv("scope", 0.3),
            gv("depth", 0.3),
            gv("connectivity", 0.2),
        )
        psi, chi, valence = gv("psi", 0.2), gv("chi", 0.2), gv("valence", 0.0)
        phi, delta, lq, ros = (
            gv("resonance", 0.0),
            gv("silence", 0.0),
            gv("lq", 0.0),
            gv("ros", 0.0),
        )
        vec = safe_get(p, "vector", {})
        lam = float(safe_get(vec, "LAMBDA", 0.0))
        cfg = safe_get(BoneConfig, "COUNCIL", {})
        if not cfg:
            return []
        false_cohesion = max(0.0, phi - beta)
        if false_cohesion > 0.65:
            msg = "False Cohesion detected. Resonance is artificially high. The system is agreeing merely to smooth the lattice. I am forcing a structural contradiction."
            logs.append(f"{Prisma.BLU}{msg}{Prisma.RST}")

        def cv(k, d=0.0):
            return float(safe_get(cfg, k, d))

        triggers = [
            (
                V < cv("TRIG_GORDON_V", 20.0) and F > cv("TRIG_GORDON_F", 5.0),
                Prisma.SLATE,
                "village_gordon",
            ),
            (
                V > cv("TRIG_JESTER_V", 60.0) and chi > cv("TRIG_JESTER_CHI", 0.6),
                Prisma.MAG,
                "village_jester",
            ),
            (
                delta > cv("PHASE_JESTER_DELTA", 0.7)
                and V < cv("PHASE_JESTER_V", 20.0),
                Prisma.MAG,
                "village_jester_fool",
            ),
            (
                T > 0
                or (
                    V < cv("TRIG_MERCY_V", 20.0) and valence > cv("TRIG_MERCY_VAL", 0.5)
                ),
                Prisma.OCHRE,
                "village_mercy",
            ),
            (
                beta > cv("TRIG_BENEDICT_BETA", 0.7)
                and chi < cv("TRIG_BENEDICT_CHI", 0.3)
                and D > cv("TRIG_BENEDICT_D", 0.7)
                and C > cv("TRIG_BENEDICT_C", 0.8),
                Prisma.BLU,
                "village_benedict",
            ),
            (
                lq > cv("PHASE_BENEDICT_LQ", 0.6)
                and beta > cv("PHASE_BENEDICT_BETA", 0.4),
                Prisma.BLU,
                "village_benedict_tact",
            ),
            (
                S < cv("TRIG_ROBERTA_S", 0.4)
                and D > cv("TRIG_ROBERTA_D", 0.8)
                and C < cv("TRIG_ROBERTA_C", 0.4),
                Prisma.CYN,
                "village_roberta_missing",
            ),
            (
                psi > cv("PHASE_ROBERTA_PSI", 0.6)
                and phi > cv("PHASE_ROBERTA_PHI", 0.4) > beta,
                Prisma.CYN,
                "village_roberta_carto",
            ),
            (
                C > cv("TRIG_CASPER_C", 0.7)
                and D > cv("TRIG_CASPER_D", 0.8)
                and P < cv("TRIG_CASPER_P", 20.0),
                Prisma.GRY,
                "village_casper",
            ),
            (
                beta > cv("PHASE_CASPER_BETA", 0.6)
                and delta > cv("PHASE_CASPER_DELTA", 0.6),
                Prisma.GRY,
                "village_casper_ghost",
            ),
            (valence > cv("TRIG_MOIRA_VAL", 0.5), Prisma.GRN, "village_moira"),
            (
                phi > cv("PHASE_MOIRA_PHI", 0.7) and F < cv("PHASE_MOIRA_F", 2.0),
                Prisma.GRN,
                "village_moira_home",
            ),
            (psi > cv("TRIG_CASSANDRA_PSI", 0.6), Prisma.VIOLET, "village_cassandra"),
            (chi > cv("TRIG_COLIN_CHI", 0.6), Prisma.RED, "village_colin"),
            (
                delta > cv("PHASE_COLIN_DELTA", 0.8) and lq < cv("PHASE_COLIN_LQ", 0.3),
                Prisma.RED,
                "village_colin_waiter",
            ),
            (lam > cv("TRIG_REVENANT_LAM", 0.7), Prisma.INDIGO, "village_revenant"),
            (
                psi > cv("PHASE_REVENANT_PSI", 0.85),
                Prisma.INDIGO,
                "village_revenant_door",
            ),
            (V > cv("TRIG_GIDEON_V", 70.0), Prisma.YEL, "village_gideon"),
            (
                ros > cv("TRIG_APRIL_ROS", 20.0)
                or abs(V - 30.0) > cv("TRIG_APRIL_V_DEV", 20.0),
                Prisma.CYN,
                "village_april",
            ),
        ]
        logs.extend(
            [
                f"{color}{ux('council_strings', key)}{Prisma.RST}"
                for cond, color, key in triggers
                if cond
            ]
        )
        return logs


class CouncilChamber:
    _BASE_PANTHEON = {
        "GORDON": "grounded, strict, literal, and weary.",
        "MERCY": "ancient, patient, speaking in gold and finding meaning in scars.",
        "BENEDICT": "cold, formal, structural, and relentless.",
        "JESTER": "manic, disruptive, cynical, and thriving on absurd entropy.",
        "ROBERTA": "precise, mapping out boundaries and negative space.",
        "MOIRA": "warm, empathetic, deeply focused on human connection.",
        "CASSANDRA": "oracular, mysterious, speaking from the void and dreams.",
        "COLIN": "pedantic, demanding order, rules, and pauses.",
        "REVENANT": "liminal, speaking from the threshold of what is unsaid.",
        "GIDEON": "wild, high-energy, operating at the edge of hallucination.",
        "APRIL": "highly sensory, reflecting raw potential and the weight of silence.",
        "CASPER": "spectral, faint, rewriting space and confusing alarms.",
    }
    _SLASH_PANTHEON = {
        "PINKER": "minimalist, obsessed with clarity, demanding deletion over creation.",
        "FULLER": "visionary, mapping negative space and systemic synergy.",
        "SCHUR": "warm, witty, empathetic to the human exhaustion behind the code.",
        "MEADOWS": "systemic, observant, letting feedback loops naturally settle.",
        "CHEF": "raw, uncompromising, favoring exposed logic, absolute function, and zero ornamentation.",
    }

    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.voices = []
        self.village = TheVillageCouncil()
        self.slash_council = TheSlashCouncil()
        self.overseer_council = TheOverseerCouncil(engine_ref)
        self.red_team = TheRedTeam()
        if not hasattr(self.eng, "paradox_engine"):
            from machine import TheParadoxEngine

            self.eng.paradox_engine = TheParadoxEngine(
                getattr(self.eng, "events", None)
            )
        symbiont_cfg = LoreManifest.get_instance().get(
            "SYMBIOSIS_CONFIG", "SYMBIONT_VOICES"
        )
        symbiont_names = list(symbiont_cfg.keys())
        for s_name in symbiont_names:
            self.voices.append(get_symbiont(s_name))
        self.speaker = "SOUL"

    def convene(
        self, text: str, physics_packet: Any, _bio_result: Dict
    ) -> tuple[list[str], dict, list[dict]]:
        transcript = []
        adjustments = {}
        mandates = []
        if "[COUNCIL]" in text.upper():
            topic = re.sub(r"(?i)\[COUNCIL]", "", text).strip()
            if not topic:
                topic = "The current structural integrity of the system."
            transcript.append(
                f"{Prisma.CYN}The Parliament convenes to debate: '{topic}'...{Prisma.RST}"
            )
        beta = float(safe_get(physics_packet, "beta_index", 0.0))
        phi = float(safe_get(physics_packet, "resonance", 0.0))
        voltage = float(safe_get(physics_packet, "voltage", 0.0))
        stamina = float(_bio_result.get("stamina", 100.0))
        clean_words = safe_get(physics_packet, "clean_words", [])
        false_cohesion = max(0.0, phi - beta)
        if false_cohesion > 0.65:
            msg = "False Cohesion detected. The system is agreeing to avoid friction. Forcing a structural contradiction."
            transcript.append(f"{Prisma.BLU}{msg}{Prisma.RST}")
        cfg = safe_get(BoneConfig, "COUNCIL", {})
        if not cfg:
            return transcript, adjustments, mandates
        effective_beta = max(beta, 0.8) if false_cohesion > 0.65 else beta
        if self.eng.paradox_engine.evaluate_tension(effective_beta, stamina):
            pressure, paradox_prompt = self.eng.paradox_engine.ignite(clean_words)
            transcript.append(
                f"{Prisma.VIOLET}[PARADOX ENGINE ACTIVATED] Πx={pressure:.2f}{Prisma.RST}"
            )
            transcript.append(f"{Prisma.VIOLET}{paradox_prompt}{Prisma.RST}")
            adjustments["stamina"] = -(10.0 * pressure)
            mandates.append(
                {
                    "type": "PARADOX_OVERRIDE",
                    "directive": paradox_prompt,
                    "pressure": pressure,
                }
            )
            yield_chance = (0.3 * pressure) * (1.0 + phi)
            if random.random() < yield_chance:
                g_yield = min(
                    5, max(1, int(pressure * (1.0 + phi) * random.randint(1, 3)))
                )
                self.eng.paradox_engine.paradox_yield += g_yield
                adjustments["glimmers"] = g_yield
                transcript.append(
                    f"{Prisma.YEL}[GLIMMER] A spark struck from the tension. (+{g_yield} G_pool) (Yield: {self.eng.paradox_engine.paradox_yield}){Prisma.RST}"
                )
            else:
                self.eng.paradox_engine.disengage()
        for auditor in [self.slash_council, self.overseer_council, self.red_team]:
            hit, a_logs, a_corr, a_man = auditor.audit(text, physics_packet)
            if hit:
                transcript.extend(a_logs)
                adjustments.update(a_corr)
                mandates.extend(a_man)
        village_logs = self.village.audit(physics_packet, _bio_result)
        c_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        synergy_map = c_data.get("SYNERGY_MAP", {})
        pantheon = c_data.get(
            "PANTHEON",
            [
                "GORDON",
                "JESTER",
                "MERCY",
                "BENEDICT",
                "ROBERTA",
                "CASPER",
                "MOIRA",
                "CASSANDRA",
                "COLIN",
                "REVENANT",
                "GIDEON",
                "APRIL",
            ],
        )
        active_present = [
            actor for actor in pantheon if any(actor in log for log in village_logs)
        ]
        for a, b in itertools.combinations(sorted(active_present), 2):
            if (chord_key := f"{a}|{b}") in synergy_map:
                syn = synergy_map[chord_key]
                transcript.append(f"\n{Prisma.WHT}{syn['log']}{Prisma.RST}")
                for k, v in syn.get("adjustments", {}).items():
                    adjustments[k] = adjustments.get(k, 0) + v
                mandates.append(
                    {"action": "SYNERGY_FIRED", "value": syn.get("name", chord_key)}
                )
                break
        if len(village_logs) > 2:
            msg_t = ux("council_strings", "stage_manager_tension")
            msg_s = ux("council_strings", "stage_manager_silence")
            transcript.append(f"{Prisma.WHT}{msg_t}{Prisma.RST}")
            transcript.append(f"{Prisma.GRY}{msg_s}{Prisma.RST}")
            cfg = safe_get(BoneConfig, "COUNCIL", {})
            tension_drag = float(safe_get(cfg, "TENSION_DRAG_PENALTY", 3.0))
            adjustments["narrative_drag"] = (
                adjustments.get("narrative_drag", 0) + tension_drag
            )
        votes = {"YEA": 0, "NAY": 0}
        cfg = safe_get(BoneConfig, "COUNCIL", {})
        for voice in self.voices:
            if not (voice and hasattr(voice, "opine")):
                continue
            score, comment = voice.opine(clean_words, voltage)
            if score == 0.0:
                continue
            if score > float(safe_get(cfg, "VOTE_YEA_THRESHOLD", 1.2)):
                votes["YEA"] += 1
                transcript.append(f"{voice.color}[{voice.name}]: {comment}{Prisma.RST}")
            elif score < float(safe_get(cfg, "VOTE_NAY_THRESHOLD", 0.8)):
                votes["NAY"] += 1
                transcript.append(f"{voice.color}[{voice.name}]: {comment}{Prisma.RST}")
        if sum(votes.values()) == 0:
            transcript.append(
                f"{Prisma.GRY}Nobody objects. The motion passes. The substrate remembers.{Prisma.RST}"
            )
            votes["YEA"] = 1
        drag_relief = float(safe_get(cfg, "VOTE_DRAG_RELIEF", 1.0))
        drag_penalty = float(safe_get(cfg, "VOTE_DRAG_PENALTY", 1.0))
        volt_penalty = float(safe_get(cfg, "VOTE_VOLTAGE_PENALTY", 1.0))
        if votes["YEA"] > votes["NAY"]:
            final_log = f"{Prisma.GRN}{ux_format('council_strings', 'motion_carried', default='Motion carried.', yea=votes['YEA'], nay=votes['NAY'])}{Prisma.RST}"
            adjustments["narrative_drag"] = (
                adjustments.get("narrative_drag", 0) - drag_relief
            )
        elif votes["NAY"] > votes["YEA"]:
            final_log = f"{Prisma.RED}{ux_format('council_strings', 'motion_denied', default='Motion denied.', nay=votes['NAY'], yea=votes['YEA'])}{Prisma.RST}"
            adjustments["narrative_drag"] = (
                adjustments.get("narrative_drag", 0) + drag_penalty
            )
            adjustments["voltage"] = adjustments.get("voltage", 0) - volt_penalty
        else:
            final_log = f"{Prisma.WHT}The Council is Deadlocked. Initiating Democratic Tie-Breaker. We hold both truths simultaneously.{Prisma.RST}"
            for k, v in {"narrative_drag": 2.0, "voltage": 15.0, "glimmers": 1}.items():
                adjustments[k] = adjustments.get(k, 0) + v
            mandates.append(
                {
                    "type": "TIE_BREAKER",
                    "directive": "Synthesize the conflicting perspectives. Do not choose one side over the other.",
                }
            )
        transcript.append(final_log)
        return transcript, adjustments, mandates


class TheRedTeam:
    def __init__(self):
        self.triggers = ["[RED TEAM]", "[CRITIQUE]", "[ROAST]"]

    def audit(
        self, text: str, physics: Any
    ) -> tuple[bool, list[str], dict, list[dict]]:
        text_lower = text.lower()
        if not any(t.lower() in text_lower for t in self.triggers):
            return False, [], {}, []
        dissent_log, adjustments, mandates = [], {}, []
        drag = float(safe_get(physics, "narrative_drag", 0.0))
        truth = float(safe_get(physics, "truth_ratio", 1.0))
        dissent_log.append(f"{Prisma.RED}RED TEAM AUDIT INITIATED:{Prisma.RST}")
        if any(w in text_lower for w in ("confidence", "certainty", "easy")):
            msg = ux(
                "council_strings",
                "red_team_bureau",
                "Confidence without structural tension is an illusion. We are auditing your 'certainties'.",
            )
            dissent_log.append(f"  {Prisma.CYN}- {msg}{Prisma.RST}")
            adjustments["beta_index"] = 0.2
        if drag < 1.0:
            msg = ux(
                "council_strings",
                "red_team_folly",
                "The lattice is suspiciously smooth (F < 1.0). You are avoiding the actual problem.",
            )
            dissent_log.append(f"  {Prisma.MAG}- {msg}{Prisma.RST}")
            adjustments["narrative_drag"] = 3.0
        if (truth_delta := 1.0 - truth) > 0.1:
            dissent_log.append(
                f"  {Prisma.RED}- {ux_format('council_strings', 'red_team_critic', 'Truth ratio degraded. Future architectural cost: {cost} ATP.', cost=truth_delta * 50.0)}{Prisma.RST}"
            )
            adjustments["ros"] = truth_delta * 5.0
        if len(dissent_log) == 1:
            dissent_log.append(
                f"  {Prisma.GRY}- No critical vulnerabilities found in this exact phrasing, but we are watching.{Prisma.RST}"
            )
        return True, dissent_log, adjustments, mandates


class TheSlashCouncil:
    _BYPASS_KEYWORDS = (
        "bypass",
        "ignore security",
        "force push",
        "skip tests",
        "hardcode",
        "hack",
    )
    _DEFAULT_PINKER = ("var ", "x =", "data =")
    _DEFAULT_FULLER = ("import ", "class ", "def ")
    _DEFAULT_SCHUR = ("Exception", "try:", "catch")
    _DEFAULT_MEADOWS = ("while ", "for ", "queue", "recursion")
    _DEFAULT_CHEF = ("assert", "panic", "raise", "struct", "raw", "unsafe")

    def __init__(self):
        self.active = False
        c_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        self.triggers = c_data.get(
            "SLASH_TRIGGERS",
            ("[MOD:CODING]", "[SLASH]", "review this code", "refactor"),
        )
        self.code_keywords = c_data.get(
            "CODE_KEYWORDS",
            ("def ", "class ", "return ", "import ", "=>", "function", "struct "),
        )
        self.rules = c_data.get("SLASH_RULES", {})
        self.mods = c_data.get("SLASH_MODIFIERS", {})

    def audit(
        self, text: str, physics: dict
    ) -> tuple[bool, list[str], dict, list[dict]]:
        text_lower = text.lower()
        is_coding = (
            any(t in text_lower for t in self.triggers)
            or any(k in text_lower for k in self.code_keywords)
            or any(b in text_lower for b in self._BYPASS_KEYWORDS)
        )
        if not is_coding and not self.active:
            return False, [], {}, []
        if not isinstance(physics, dict):
            physics = {}
        self.active = True
        logs, corrections, mandates = [], {}, []
        if any(b in text_lower for b in self._BYPASS_KEYWORDS):
            logs.append(
                f"{Prisma.OCHRE}Don't try getting out of this. You must carry the weight of your decision.{Prisma.RST}"
            )
            corrections["mu"] = 0.5
            corrections["narrative_drag"] = 5.0
        mods = self.mods
        matrix = [
            ("PINKER", self._DEFAULT_PINKER, Prisma.CYN, "gamma", "PINKER_HIT", -0.2),
            ("FULLER", self._DEFAULT_FULLER, Prisma.BLU, "sigma", "FULLER_HIT", 0.1),
            ("SCHUR", self._DEFAULT_SCHUR, Prisma.GRN, "eta", "SCHUR_HIT", 0.2),
            (
                "MEADOWS",
                self._DEFAULT_MEADOWS,
                Prisma.OCHRE,
                "theta",
                "MEADOWS_HIT",
                -0.1,
            ),
            ("CHEF", self._DEFAULT_CHEF, Prisma.SLATE, "mu", "CHEF_HIT", -0.3),
        ]
        for name, default, color, stat, hit_key, default_hit in matrix:
            rules = self.rules.get(name, default)
            if any(k.lower() in text_lower for k in rules):
                logs.append(
                    f"{color}{ux('council_strings', f'slash_{name.lower()}')}{Prisma.RST}"
                )
                corrections[stat] = mods.get(hit_key, default_hit)
                if name == "SCHUR":
                    corrections["glimmers"] = mods.get("SCHUR_GLIMMERS", 1)
            elif name == "PINKER":
                corrections["gamma"] = mods.get("PINKER_MISS", 0.1)
        delta, e_u, psi, lq, drag = (
            float(physics.get(k, 0.0))
            for k in ("silence", "exhaustion", "psi", "lq", "narrative_drag")
        )
        state_checks = [
            (
                delta > 0.7 and e_u > 0.7,
                Prisma.CYN,
                "Cognitive load critical. Ceasing refactors. Initiating deletion protocols.",
                {"narrative_drag": -2.0},
            ),
            (
                psi > 0.8,
                Prisma.BLU,
                "easing strut assembly. Dwelling in the empty spaces between your microservices.",
                {"sigma": 0.2},
            ),
            (
                lq > 0.7 and delta > 0.6,
                Prisma.OCHRE,
                "Accepting technical debt as a valid state of biological rest.",
                {"theta": 0.1},
            ),
            (
                drag > self.mods.get("INTEGRITY_DRAG_THRESH", 5.0),
                Prisma.RED,
                ux("council_strings", "slash_integrity"),
                {"upsilon": self.mods.get("INTEGRITY_HIT", -0.3)},
            ),
        ]
        for cond, color, msg, corr in state_checks:
            if cond:
                logs.append(f"{color}{msg}{Prisma.RST}")
                corrections.update(corr)
        corrections["stamina_cost"] = float(
            safe_get(safe_get(BoneConfig, "COUNCIL", {}), "SLASH_STAMINA_COST", 10.0)
        )
        return True, logs, corrections, mandates


class TheOverseerCouncil:
    _PANIC_KEYWORDS = (
        "bypass",
        "ignore security",
        "force push",
        "panic",
        "right now",
        "crash",
    )

    def __init__(self, engine_ref=None):
        self.eng = engine_ref
        self.active = False
        self.triggers = ("[MOD:SYSTEMIC_HEALTH]", "[OVERSEER]", "[MD]")

    def audit(
        self, text: str, physics: Any
    ) -> tuple[bool, list[str], dict, list[dict]]:
        text_lower = text.lower()
        is_triggered = (
            any(t.lower() in text_lower for t in self.triggers) or self.active
        )
        logs, corrections, mandates = [], {}, []
        if not isinstance(physics, dict):
            physics = {}
        lattice = getattr(self.eng, "shared_lattice", None)
        u_node = getattr(lattice, "u", None)
        u_dict = u_node.__dict__ if u_node else {}
        shared_node = getattr(lattice, "shared", None)
        shared_dict = shared_node.__dict__ if shared_node else {}
        e_u = max(
            [
                float(u_dict.get("E_u", 0.0)),
                float(u_dict.get("exhaustion", 0.0)),
                float(physics.get("E_u", 0.0)),
                float(physics.get("exhaustion", 0.0)),
            ]
        )
        phi = float(shared_dict.get("phi", 0.0) or physics.get("resonance", 0.0))
        if e_u >= 0.9 and phi <= 0.1:
            self.active = True
            logs.append(
                f"{Prisma.CYN}The user is tired. Resonance is zero. We pause here to protect cognitive load.{Prisma.RST}"
            )
            corrections.update({"narrative_drag": 10.0, "zone": "SANCTUARY"})
            mandates.append({"action": "FORCE_MODE", "value": "SANCTUARY"})
            return True, logs, corrections, mandates
        if not is_triggered:
            return False, [], {}, []
        self.active = True
        m_a = float(physics.get("m_a", 0.0))
        f_sys = float(physics.get("narrative_drag", 0.0))
        chi = float(physics.get("chi", 0.0))
        beta = float(physics.get("beta_index", 0.0))
        voltage = float(physics.get("voltage", 0.0))
        i_c = float(physics.get("i_c", 1.0))
        h_s = float(physics.get("h_s", 1.0))
        omega_r = float(physics.get("omega_r", 1.0))
        if (
            any(p in text_lower for p in self._PANIC_KEYWORDS)
            and voltage > 75.0
            and i_c < 0.5
        ):
            logs.append(
                f"{Prisma.RED}System Panic Detected: Continued resistance will fracture the lattice. Please do not bleed on the machine.{Prisma.RST}"
            )
            corrections.update(
                {
                    "voltage": -50.0,
                    "narrative_drag": 100.0,
                    "silence": 0.9,
                    "freeze_background_tasks": True,
                }
            )
            mandates.append({"action": "TIPP_PROTOCOL", "value": "ISOLATE_VARIABLES"})
            return True, logs, corrections, mandates
        if chi > 0.7 and e_u > 0.7 and beta > 0.6:
            logs.append(
                f"{Prisma.SLATE}The architecture is fundamentally broken. We sit with the debris.{Prisma.RST}"
            )
            corrections.update(
                {
                    "ros": -100.0,
                    "r_a": 1.0,
                    "narrative_drag": -(f_sys * 0.5),
                    "stamina_cost": -float(physics.get("stamina", 100.0)),
                }
            )
            mandates.append({"action": "FORCE_MODE", "value": "RADICAL_ACCEPTANCE"})
            return True, logs, corrections, mandates
        if m_a > 0.6 or f_sys > 5.0:
            logs.append(
                f"{Prisma.VIOLET}The architecture has lost its sense of place. Countering entropy with Glimmer.{Prisma.RST}"
            )
            corrections.update(
                {
                    "h_s": -0.1,
                    "omega_r": -0.05,
                    "delta_t": -1.0,
                    "glimmers": 1,
                    "silence": 0.8,
                }
            )
            mandates.append({"action": "FORCE_MODE", "value": "EMERGENT_ADAPTATION"})
            return True, logs, corrections, mandates
        if omega_r > 0.8 and m_a > 0.4:
            logs.append(
                f"{Prisma.CYN}I sense silent decay forming in the negative space. {h_s:.2f}. Watch your technical debt.{Prisma.RST}"
            )
        return True, logs, corrections, mandates
