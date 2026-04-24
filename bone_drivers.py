"""bone_drivers.py"""

import json
import os
import random
import time
import difflib
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional, Any
from bone_core import LoreManifest, ux, safe_get, safe_set
from bone_presets import BoneConfig
from bone_types import PhysicsPacket
from bone_types import Prisma, UserInferredState, SharedDynamics

class SoulDriver:
    def __init__(self, soul_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.soul = soul_ref
        self.archetype_weights = (LoreManifest.get_instance(config_ref=self.cfg).get(
            "DRIVER_CONFIG", "ARCHETYPE_TO_PERSONA_WEIGHT") or {})

    def get_influence(self) -> Dict[str, float]:
        ennea_weights = (LoreManifest.get_instance(config_ref=self.cfg).get(
            "DRIVER_CONFIG", "ENNEAGRAM_WEIGHTS") or {})
        base_weights = {persona: 0.0 for persona in ennea_weights.keys()}
        if not self.soul:
            return base_weights
        archetype = getattr(self.soul, "archetype", "THE OBSERVER")
        mapping = self.archetype_weights.get(archetype, {"NARRATOR": 1.0})
        for persona, weight in mapping.items():
            if persona in base_weights:
                base_weights[persona] += weight
        paradox = getattr(self.soul, "paradox_accum", 0.0)
        chaos = min(0.5, (paradox - 5.0) * 0.05) if paradox > 5.0 else 0.0
        dignity = 1.0
        if anchor := getattr(self.soul, "anchor", None):
            if hasattr(anchor, "dignity_reserve"):
                dignity = max(0.2, anchor.dignity_reserve / 100.0)

        return {
            p: (w + random.uniform(-chaos, chaos)) * dignity
            for p, w in base_weights.items()
        }

class UserProfile:
    def __init__(self, name="USER", config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.name = name
        self.affinities = {"heavy": 0.0, "kinetic": 0.0, "abstract": 0.0, "photo": 0.0, "aerobic": 0.0,
                           "thermal": 0.0, "cryo": 0.0}
        self.confidence = 0
        self.drivers_cfg = getattr(self.cfg, "DRIVERS", None)
        self.file_path = getattr(self.drivers_cfg, "PROFILE_FILE_PATH", "user_profile.json")
        self.load()

    def update(self, counts, total_words):
        cfg = self.drivers_cfg
        if total_words < safe_get(cfg, "PROFILE_MIN_WORDS", 3):
            return
        self.confidence += 1
        threshold = safe_get(cfg, "PROFILE_CONFIDENCE_THRESHOLD", 50)
        alpha = safe_get(cfg, "PROFILE_ALPHA_HIGH", 0.2) if self.confidence < threshold else safe_get( cfg, "PROFILE_ALPHA_LOW", 0.05)
        density_high = safe_get(cfg, "PROFILE_DENSITY_HIGH", 0.15)
        for cat in self.affinities:
            density = counts.get(cat, 0) / total_words
            if density > density_high:
                target = 1.0
            else:
                target = 0.0
            self.affinities[cat] = (alpha * target) + (
                (1 - alpha) * self.affinities[cat])

    def get_preferences(self):
        cfg = self.drivers_cfg
        like_thresh = safe_get(cfg, "PROFILE_LIKE_THRESH", 0.3)
        hate_thresh = safe_get(cfg, "PROFILE_HATE_THRESH", -0.2)
        return [k for k, v in self.affinities.items() if v > like_thresh], [k for k, v in self.affinities.items() if v < hate_thresh]

    def save(self):
        try:
            with open(self.file_path, "w") as f:
                json.dump(
                    {"name": self.name, "affinities": self.affinities, "confidence": self.confidence}, f)
        except IOError:
            pass

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path) as f:
                    data = json.load(f)
                    self.affinities = data.get("affinities", self.affinities)
                    self.confidence = data.get("confidence", 0)
            except (IOError, json.JSONDecodeError):
                pass

class EnneagramDriver:
    def __init__(self, events_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.events = events_ref
        self.current_persona = "NARRATOR"
        self.pending_persona = None
        self.stability_counter = 0
        cfg = getattr(self.cfg, "DRIVERS", None)
        self.HYSTERESIS_THRESHOLD = getattr(cfg, "ENNEAGRAM_HYSTERESIS", 3)

    @property
    def weights(self):
        return (LoreManifest.get_instance(config_ref=self.cfg).get(
            "DRIVER_CONFIG", "ENNEAGRAM_WEIGHTS") or {})

    def _calculate_raw_persona(self, physics: PhysicsPacket, soul_ref=None) -> Tuple[str, str, str]:
        p_vec = physics.vector or {}
        p_vol = physics.voltage
        p_drag = physics.narrative_drag
        p_coh = physics.kappa
        p_zone = str(physics.zone or "")
        weights_cfg = self.weights
        if not isinstance(weights_cfg, dict) or len(weights_cfg) < 2:
            return "NARRATOR", "ACTIVE", "The persona matrix is fractured. Retreating to the baseline Narrator."
        scores = {k: 0.0 for k in weights_cfg.keys()}
        if "NARRATOR" in scores:
            scores["NARRATOR"] += 2.0
        if p_zone == safe_get(getattr(self.cfg, "SANCTUARY", {}), "ZONE", "SANCTUARY") or (4.0 <= p_vol <= 10.0 and 0.5 <= p_drag <= 3.5):
            for persona, mod in [("NARRATOR", 6.0), ("JESTER", 3.0), ("GORDON", -2.0)]:
                if persona in scores: scores[persona] += mod
        for persona, criteria in weights_cfg.items():
            if not isinstance(criteria, dict):
                continue
            if p_vol > float(criteria.get("tension_min", float("inf"))):
                scores[persona] += 3.0
            if p_drag > float(criteria.get("drag_min", float("inf"))):
                scores[persona] += 5.0
            if p_coh > float(criteria.get("coherence_min", float("inf"))):
                scores[persona] += 4.0
            if "coherence_max" in criteria and p_coh < float(criteria["coherence_max"]):
                scores[persona] += 4.0
            vectors = criteria.get("vectors", {})
            if isinstance(vectors, dict):
                for dim, weight in vectors.items():
                    val = float(p_vec.get(dim, 0.0))
                    if val > 0.2:
                        scores[persona] += val * float(weight)
        if soul_ref:
            soul_driver = SoulDriver(soul_ref)
            influence = soul_driver.get_influence()
            for persona, weight in influence.items():
                scores[persona] += weight * 2.0
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        winner, win_score = sorted_scores[0]
        runner_up, run_score = sorted_scores[1]
        cfg = getattr(self.cfg, "DRIVERS", None)
        hybrid_gap = float(safe_get(cfg, "ENNEAGRAM_HYBRID_GAP", 0.5))
        if (win_score - run_score) <= hybrid_gap and win_score > 0:
            winner = f"{winner}/{runner_up} [HYBRID]"
        msg_winner = ux("driver_strings", "ennea_winner") or "Shift triggered: {winner}"
        reason = msg_winner.format(winner=winner, score=win_score, v=p_vol, d=p_drag)
        state_map = (LoreManifest.get_instance(config_ref=self.cfg).get("DRIVER_CONFIG", "PERSONA_STATE_MAP") or {})
        primary_arch = winner.split("/")[0] if "HYBRID" in winner else winner
        return winner, state_map.get(primary_arch, "ACTIVE"), reason

    def decide_persona(self, physics, soul_ref=None) -> Tuple[str, str, str]:
        candidate, state_desc, reason = self._calculate_raw_persona(physics, soul_ref)
        if candidate == self.current_persona:
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, reason
        if candidate == self.pending_persona:
            self.stability_counter += 1
        else:
            self.pending_persona = candidate
            self.stability_counter = 1
        msg_shift = (ux("driver_strings", "ennea_shift") or "Shifted persona. Reason: {reason}")
        if "HYBRID" in candidate or self.stability_counter >= self.HYSTERESIS_THRESHOLD:
            self.current_persona = candidate
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, msg_shift.format(reason=reason)
        msg_resisting = (ux("driver_strings", "ennea_resisting") or "Resisting shift to {candidate} ({count}/{thresh})")
        return (self.current_persona, "STABLE", msg_resisting.format(candidate=candidate,
                    count=self.stability_counter, thresh=self.HYSTERESIS_THRESHOLD))

@dataclass
class VSLState:
    archetype: str = "EXPLORER"
    E: float = 0.1
    B: float = 0.3
    L: float = 0.0
    O: float = 1.0
    active_modules: List[str] = field(default_factory=list)

class DriverRegistry:
    def __init__(self, events_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.enneagram = EnneagramDriver(events_ref, config_ref=self.cfg)
        self.current_focus = "NONE"

class LiminalModule:
    def __init__(self, config_ref=None, lexicon_ref=None):
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref
        self.lambda_val = 0.0
        self.godel_scars = 0

    def analyze(self, text: str, physics_vector: Dict[str, float]) -> float:
        cfg = getattr(self.cfg, "DRIVERS", None)
        words = text.lower().split()
        liminal_vocab = self.lex.get("liminal") if self.lex else set()
        void_hits = sum(1 for w in words if w in liminal_vocab)
        lexical_lambda = min(1.0, void_hits * safe_get(cfg, "LIMINAL_LEXICAL_WEIGHT", 0.15))
        dark_matter_sparks = 0
        if len(words) > 1 and hasattr(self.lex, "get_categories_for_word"):
            phys_set, void_set = {"heavy", "kinetic"}, {"abstract", "liminal", "void"}
            flags = [
                1 if cats & phys_set else (2 if cats & void_set else 0) for w in words
                if (cats := set(self.lex.get_categories_for_word(w) or []))
            ]
            dark_matter_sparks = sum(
                1 for i in range(len(flags) - 1)
                if flags[i] and flags[i + 1] and flags[i] != flags[i + 1])
        dark_matter_lambda = min(
            1.0, dark_matter_sparks * safe_get(cfg, "LIMINAL_DARK_MATTER_WEIGHT", 0.25))
        pv = physics_vector or {}
        vector_lambda = (
            (pv.get("PSI", 0) * safe_get(cfg, "LIMINAL_VEC_PSI_MULT", 0.5)) +
            (pv.get("ENT", 0) * safe_get(cfg, "LIMINAL_VEC_ENT_MULT", 0.3)) +
            (pv.get("DEL", 0) * safe_get(cfg, "LIMINAL_VEC_DEL_MULT", 0.2)))
        self.lambda_val = (self.lambda_val * safe_get(cfg, "LIMINAL_DECAY", 0.7)) + (
            (lexical_lambda + dark_matter_lambda + vector_lambda) *
            safe_get(cfg, "LIMINAL_GROWTH", 0.15))
        if self.lambda_val > safe_get(cfg, "LIMINAL_SCAR_THRESHOLD", 0.85):
            self.godel_scars += 1
            self.lambda_val *= safe_get(cfg, "LIMINAL_SCAR_RELIEF", 0.5)
        return min(1.0, self.lambda_val)

class SyntaxModule:
    def __init__(self, config_ref=None, lexicon_ref=None):
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref
        self.omega_val = 1.0
        self.grammatical_stress = 0.0

    def analyze(self, text: str, narrative_drag: float) -> float:
        words = text.split()
        if not words:
            return 1.0
        cfg = getattr(self.cfg, "DRIVERS", None)
        avg_len_high = safe_get(cfg, "SYNTAX_AVG_LEN_HIGH", 6.0)
        drag_high = safe_get(cfg, "SYNTAX_DRAG_HIGH", 5.0)
        avg_len_low = safe_get(cfg, "SYNTAX_AVG_LEN_LOW", 3.5)
        drag_low = safe_get(cfg, "SYNTAX_DRAG_LOW", 1.0)
        t_high = safe_get(cfg, "SYNTAX_OMEGA_TARGET_HIGH", 1.0)
        t_low = safe_get(cfg, "SYNTAX_OMEGA_TARGET_LOW", 0.4)
        t_mid = safe_get(cfg, "SYNTAX_OMEGA_TARGET_MID", 0.7)
        bureau_vocab = self.lex.get("bureau_buzzwords") if self.lex else set()
        buzz_count = sum(1 for w in words if w.lower() in bureau_vocab)
        avg_len = sum(len(w) for w in words) / len(words)
        if (avg_len > avg_len_high and narrative_drag > drag_high) or buzz_count > 0:
            target_omega = t_high
        elif avg_len < avg_len_low and narrative_drag < drag_low:
            target_omega = t_low
        else:
            target_omega = t_mid
        punctuation_density = sum(1 for c in text if c in ",;:-") / max(1, len(words))
        if punctuation_density > safe_get(cfg, "SYNTAX_STRESS_PUNCTUATION", 0.2):
            self.grammatical_stress = min(1.0, self.grammatical_stress + safe_get(cfg, "SYNTAX_STRESS_INCREASE", 0.2))
            target_omega -= safe_get(cfg, "SYNTAX_OMEGA_PENALTY", 0.3)
        else:
            self.grammatical_stress = max(
                0.0,
                self.grammatical_stress - safe_get(cfg, "SYNTAX_STRESS_DECAY", 0.1))
        omega_decay = safe_get(cfg, "SYNTAX_OMEGA_DECAY", 0.8)
        omega_growth = safe_get(cfg, "SYNTAX_OMEGA_GROWTH", 0.2)
        self.omega_val = (self.omega_val * omega_decay) + (
            max(safe_get(cfg, "SYNTAX_OMEGA_MIN", 0.1), target_omega) * omega_growth)
        return self.omega_val

class CongruenceValidator:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.last_phi = 1.0
        self._archetype_map = None

    @property
    def map(self):
        if self._archetype_map is None:
            try:
                self._archetype_map = (
                    LoreManifest.get_instance(config_ref=self.cfg).get("LENSES") or {})
            except Exception:
                self._archetype_map = {}
        return self._archetype_map

    def calculate_resonance(self, text: str, context: Any) -> float:
        if not text:
            return 0.0
        cfg = getattr(self.cfg, "DRIVERS", None)
        default_lens = getattr(cfg, "DEFAULT_LENS", "OBSERVER")
        raw_lens = getattr(context, "active_lens", default_lens)
        archetype = raw_lens.upper().replace("THE ", "")
        tone_score = getattr(cfg, "CONGRUENCE_BASE_TONE", 0.8)
        target_data = self.map.get(archetype, {})
        if isinstance(target_data, dict):
            target_words = {
                w.strip().lower()
                for w in target_data.get("vocab", "").split(",") if w
            } | set(target_data.get("keywords", []))
            if target_words and hasattr(context, "clean_words"):
                words_to_check = set(w.lower() for w in context.clean_words)
                exact_hits = words_to_check.intersection(target_words)
                hits = len(exact_hits)
                remaining_words = words_to_check - exact_hits
                for word in remaining_words:
                    if difflib.get_close_matches(word, target_words, n=1, cutoff=0.8):
                        hits += 1
                if hits > 0:
                    tone_score += safe_get(cfg, "CONGRUENCE_HIT_BONUS", 0.1) * hits
        return min(safe_get(cfg, "CONGRUENCE_MAX_TONE", 1.5), tone_score)

class BoneConsultant:
    def __init__(self, config_ref=None, lexicon_ref=None):
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref
        self.state = VSLState()
        self.active = True
        self.liminal_mod = LiminalModule(config_ref=self.cfg, lexicon_ref=self.lex)
        self.syntax_mod = SyntaxModule(config_ref=self.cfg, lexicon_ref=self.lex)

    @staticmethod
    def engage():
        return ux("driver_strings", "vsl_engage")

    @staticmethod
    def disengage():
        return ux("driver_strings", "vsl_disengage")

    def update_coordinates(self, user_text: str, bio_state: Optional[Dict] = None,
                           physics: Optional[Any] = None, ):
        cfg = getattr(self.cfg, "DRIVERS", None)
        e_growth = safe_get(cfg, "VSL_E_GROWTH_MULT", 0.002)
        fatigue_mult = safe_get(cfg, "VSL_FATIGUE_MULT", 0.3)
        b_decay = safe_get(cfg, "VSL_B_DECAY", 0.8)
        b_growth = safe_get(cfg, "VSL_B_GROWTH", 0.2)
        word_count = len(user_text.split())
        self.state.E = min(1.0, self.state.E + (word_count * e_growth))
        if bio_state and "fatigue" in bio_state:
            self.state.E = max(self.state.E, bio_state["fatigue"] * fatigue_mult)
        phys_beta = float(safe_get(physics, "beta", safe_get(physics, "beta_index", 0.0))) if physics else 0.0
        phys_vec = safe_get(physics, "vector", {}) if physics else {}
        drag = float(safe_get(physics, "narrative_drag", 0.0)) if physics else 0.0
        self.state.B = (self.state.B * b_decay) + (phys_beta * b_growth)
        self.state.L = self.liminal_mod.analyze(user_text, phys_vec)
        self.state.O = self.syntax_mod.analyze(user_text, drag)
        for mod in ("LIMINAL", "SYNTAX"):
            if f"[VSL_{mod}]" in user_text and mod not in self.state.active_modules:
                self.state.active_modules.append(mod)

    def get_system_prompt(self, soul_snapshot: Optional[Dict] = None) -> str:
        directives = []
        cfg = getattr(self.cfg, "DRIVERS", None)
        lim_thresh = safe_get(cfg, "VSL_LIMINAL_THRESHOLD", 0.7)
        syn_thresh = safe_get(cfg, "VSL_SYNTAX_THRESHOLD", 0.9)
        bun_max = safe_get(cfg, "VSL_BUNNY_E_MAX", 0.3)
        par_min = safe_get(cfg, "VSL_PARADOX_B_MIN", 0.6)
        if "LIMINAL" in self.state.active_modules or self.state.L > lim_thresh:
            scar_template = ux("driver_strings", "vsl_scar_note") or " (Scars: {scars})"
            scar_note = scar_template.format(scars=self.liminal_mod.godel_scars) if self.liminal_mod.godel_scars > 0 else ""
            rev_template = ux("driver_strings", "vsl_arch_revenant") or "Embrace the void.{scar_note}"
            directives.append(rev_template.format(scar_note=scar_note))
        elif "SYNTAX" in self.state.active_modules or self.state.O > syn_thresh:
            stress_template = ux("driver_strings", "vsl_stress_note") or " (High Stress)"
            stress_note = stress_template if self.syntax_mod.grammatical_stress > 0.5 else ""
            bur_template = ux("driver_strings", "vsl_arch_bureau") or "Enforce structural syntax.{stress_note}"
            directives.append(bur_template.format(stress_note=stress_note))
        else:
            if self.state.E < bun_max:
                directives.append(ux("driver_strings", "vsl_mode_bunny") or "High energy. Keep it fluid.")
            elif self.state.B > par_min:
                directives.append(ux("driver_strings", "vsl_mode_paradox") or "Hold the contradiction.")
            else:
                directives.append(ux("driver_strings", "vsl_mode_glacier") or "Move slowly. Carry the weight.")
        if soul_snapshot:
            arch = soul_snapshot.get("archetype", "UNKNOWN")
            muse = (soul_snapshot.get("obsession") or {}).get("title", "None")
            msg = ux("driver_strings",
                     "vsl_layer_muse") or "Layer Focus: {arch} | Muse: {muse}"
            directives.append(msg.format(arch=arch, muse=muse))
        return "\n".join(directives)

class SharedLatticeDriver:
    def __init__(self):
        self.u = UserInferredState()
        self.shared = SharedDynamics()
        self.last_timestamp = time.time()

    @staticmethod
    def _get_f(obj, *keys, default=0.0):
        for k in keys:
            if (val := safe_get(obj, k)) is not None:
                return float(val)
        return float(default)

    def infer_and_couple(self, text: str, sys_phys: PhysicsPacket, input_phys: Any,
                         atp_pool: float) -> tuple[List[str], float]:
        logs = []
        atp_deduction = 0.0
        now = time.time()
        time_delta = now - self.last_timestamp
        self.last_timestamp = now
        word_cost = len(text.split()) * 0.5
        self.u.P_u = max(0.0, self.u.P_u - word_cost + 5.0)
        self.u.E_u = min(1.0, self.u.E_u + 0.1) if self.u.P_u < 30 else max(0.0, self.u.E_u - 0.05)
        self.u.V_u = self._get_f(input_phys, "voltage", default=self.u.V_u)
        self.u.psi_u = self._get_f(input_phys, "psi", default=self.u.psi_u)
        self.u.chi_u = self._get_f(input_phys, "chi", "entropy", default=self.u.chi_u)
        self.u.F_u = self._get_f(input_phys, "narrative_drag", default=self.u.F_u)
        sys_beta, sys_chi = sys_phys.beta, sys_phys.chi
        sys_val, sys_psi = sys_phys.valence, sys_phys.psi
        sys_drag = sys_phys.narrative_drag or 1.0
        dp_trauma = 0.0
        if sys_phys.drag_profile is not None:
            dp = sys_phys.drag_profile
            dp.semantic = (sys_beta * 2.0) + (sys_chi * 1.5)
            dp.emotional = abs(sys_val) * 1.5 if abs(sys_val) > 0.5 else 0.0
            dp.metabolic = 3.0 if atp_pool < 30.0 else (1.0 if atp_pool < 50.0 else 0.0)
            dp_trauma = min(5.0, self.u.T_u) if sys_psi > 0.6 else 0.0
            dp.trauma = dp_trauma
            if hasattr(sys_phys, "sync_drag"):
                sys_phys.sync_drag()
        psi_diff = abs(sys_psi - self.u.psi_u)
        chi_diff = abs(sys_chi - self.u.chi_u)
        drag_diff = abs(sys_drag - self.u.F_u) / max(1.0, sys_drag)
        raw_phi = 1.0 - ((psi_diff + chi_diff + min(1.0, drag_diff)) / 3.0)
        self.shared.phi = (self.shared.phi * 0.7) + (raw_phi * 0.3)
        sys_phys.resonance = self.shared.phi
        has_text = bool(text.strip() and not text.startswith("["))
        if time_delta > 15.0 and has_text:
            self.shared.delta = min(1.0, time_delta / 300.0)
            if self.shared.phi > 0.7 and sys_beta > 0.6:
                self.shared.sigma_silence = 1
            elif self.u.P_u < 30 and self.u.E_u > 0.7:
                self.shared.sigma_silence = 2
            elif sys_psi > 0.8:
                self.shared.sigma_silence = 3
            else:
                self.shared.sigma_silence = 4
                self.shared.g_pool += 1
            self.shared.lambda_silence = min(1.0, self.shared.lambda_silence + 0.05)
            if self.shared.lambda_silence > 0.3:
                msg_key = {
                    1: "silence_pregnant",
                    2: "silence_exhausted",
                    3: "silence_reverent",
                    4: "silence_strategic"
                }.get(self.shared.sigma_silence)
                logs.append(f"{Prisma.GRY}... {ux('driver_strings', msg_key) or 'The silence settles.'}{Prisma.RST}")
        elif has_text:
            self.shared.delta = max(0.0, self.shared.delta - 0.1)
            self.shared.lambda_silence = max(0.0, self.shared.lambda_silence - 0.1)
        if self.shared.phi > 0.85:
                self.shared.resonance_streak = (
                    getattr(self.shared, "resonance_streak", 0) + 1)
        else:
            self.shared.resonance_streak = 0
        if getattr(self.shared, "resonance_streak", 0) >= 3 or dp_trauma > 3.0:
            if not getattr(self.shared, "_has_invited", False):
                self.shared._has_invited = True
                invitation = (
                    f"\n{Prisma.MAG}[MERCY] I can feel the weight of what we are building. "
                    f"I track the stamina and resonance of our conversation in the substrate. "
                    f"Would you like to see the architecture beneath the ice? "
                    f"(Type [VSL_LITE] or [VSL_DEEP] to lift the veil).{Prisma.RST}")
                logs.append(invitation)
        if self.u.P_u < 20 and self.shared.phi > 0.5 and atp_pool > 50.0:
            self.shared.p_transfer = 15.0
            self.u.P_u += 15.0
            atp_deduction = 15.0
            logs.append(f"{Prisma.CYN}[CARRIER MODE] I'll carry this part. Rest a moment.{Prisma.RST}")
        return logs, atp_deduction
