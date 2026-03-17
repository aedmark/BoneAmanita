""" bone_drivers.py """

import json
import os
import random
import time
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional, Any
from bone_core import LoreManifest, ux
from bone_presets import BoneConfig
from bone_types import PhysicsPacket

class SoulDriver:
    def __init__(self, soul_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.soul = soul_ref
        self.archetype_weights = LoreManifest.get_instance(config_ref=self.cfg).get("DRIVER_CONFIG", "ARCHETYPE_TO_PERSONA_WEIGHT") or {}

    def get_influence(self) -> Dict[str, float]:
        ennea_weights = LoreManifest.get_instance(config_ref=self.cfg).get("DRIVER_CONFIG", "ENNEAGRAM_WEIGHTS") or {}
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
        if hasattr(self.soul, "anchor") and hasattr(self.soul.anchor, "dignity_reserve"):
            dignity = max(0.2, self.soul.anchor.dignity_reserve / 100.0)
        return {p: (w + random.uniform(-chaos, chaos)) * dignity
            for p, w in base_weights.items()}

class UserProfile:
    def __init__(self, name="USER", config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.name = name
        self.affinities = {"heavy": 0.0, "kinetic": 0.0, "abstract": 0.0, "photo": 0.0, "aerobic": 0.0, "thermal": 0.0,
                           "cryo": 0.0, }
        self.confidence = 0
        cfg = getattr(self.cfg, "DRIVERS", None)
        self.file_path = getattr(cfg, "PROFILE_FILE_PATH", "user_profile.json") if cfg else "user_profile.json"
        self.load()

    def update(self, counts, total_words):
        cfg = getattr(self.cfg, "DRIVERS", None)
        min_words = getattr(cfg, "PROFILE_MIN_WORDS", 3) if cfg else 3
        if total_words < min_words:
            return
        self.confidence += 1
        conf_thresh = getattr(cfg, "PROFILE_CONFIDENCE_THRESHOLD", 50) if cfg else 50
        alpha_high = getattr(cfg, "PROFILE_ALPHA_HIGH", 0.2) if cfg else 0.2
        alpha_low = getattr(cfg, "PROFILE_ALPHA_LOW", 0.05) if cfg else 0.05
        density_high = getattr(cfg, "PROFILE_DENSITY_HIGH", 0.15) if cfg else 0.15
        alpha = alpha_high if self.confidence < conf_thresh else alpha_low
        for cat in self.affinities:
            density = counts.get(cat, 0) / total_words
            target = 1.0 if density > density_high else (-0.5 if density == 0 else 0.0)
            self.affinities[cat] = (alpha * target) + (
                    (1 - alpha) * self.affinities[cat])

    def get_preferences(self):
        cfg = getattr(self.cfg, "DRIVERS", None)
        like_thresh = getattr(cfg, "PROFILE_LIKE_THRESH", 0.3) if cfg else 0.3
        hate_thresh = getattr(cfg, "PROFILE_HATE_THRESH", -0.2) if cfg else -0.2
        likes = [k for k, v in self.affinities.items() if v > like_thresh]
        hates = [k for k, v in self.affinities.items() if v < hate_thresh]
        return likes, hates

    def save(self):
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.__dict__, f)
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
        self.HYSTERESIS_THRESHOLD = getattr(cfg, "ENNEAGRAM_HYSTERESIS", 3) if cfg else 3

    @property
    def weights(self):
        return LoreManifest.get_instance(config_ref=self.cfg).get("DRIVER_CONFIG", "ENNEAGRAM_WEIGHTS") or {}

    @staticmethod
    def _get_phys_attr(physics, key, default=None):
        if isinstance(physics, dict):
            val = physics.get(key)
            if val is None:
                for sub in ["energy", "space", "matter"]:
                    if sub in physics and key in physics[sub]:
                        return physics[sub][key]
            return default if val is None else val
        else:
            val = getattr(physics, key, None)
            if val is None:
                for sub in ["energy", "space", "matter"]:
                    if hasattr(physics, sub):
                        sub_obj = getattr(physics, sub)
                        val = getattr(sub_obj, key, None)
                        if val is not None: return val
            return default if val is None else val

    def _calculate_raw_persona(self, physics, soul_ref=None) -> Tuple[str, str, str]:
        raw_vec = self._get_phys_attr(physics, "vector", {})
        p_vec = raw_vec if isinstance(raw_vec, dict) else {}
        def safe_float(val, default=0.0):
            try:
                return float(val)
            except (ValueError, TypeError):
                return default
        p_vol = safe_float(self._get_phys_attr(physics, "voltage", 0.0))
        p_drag = safe_float(self._get_phys_attr(physics, "narrative_drag", 0.0))
        p_coh = safe_float(self._get_phys_attr(physics, "kappa", 0.0))
        p_zone = str(self._get_phys_attr(physics, "zone", ""))
        weights_cfg = self.weights
        if not isinstance(weights_cfg, dict):
            return "NARRATOR", "ACTIVE", "Config Error"
        scores = {k: 0.0 for k in weights_cfg.keys()}
        if "NARRATOR" in scores:
            scores["NARRATOR"] += 2.0
        is_safe_metrics = 4.0 <= p_vol <= 10.0 and 0.5 <= p_drag <= 3.5
        sanctuary_zone = getattr(self.cfg, "SANCTUARY", {}).get("ZONE") if hasattr(self.cfg, "SANCTUARY") else "SANCTUARY"
        if p_zone == sanctuary_zone or is_safe_metrics:
            if "NARRATOR" in scores: scores["NARRATOR"] += 6.0
            if "JESTER" in scores: scores["JESTER"] += 3.0
            if "GORDON" in scores: scores["GORDON"] -= 2.0
        for persona, criteria in weights_cfg.items():
            if not isinstance(criteria, dict):
                continue
            if "tension_min" in criteria and p_vol > safe_float(criteria.get("tension_min", 0.0)):
                scores[persona] += 3.0
            if "drag_min" in criteria and p_drag > safe_float(criteria.get("drag_min", 0.0)):
                scores[persona] += 5.0
            if "coherence_min" in criteria and p_coh > safe_float(criteria.get("coherence_min", 0.0)):
                scores[persona] += 4.0
            if "coherence_max" in criteria and p_coh < safe_float(criteria.get("coherence_max", 0.0)):
                scores[persona] += 4.0
            vectors = criteria.get("vectors", {})
            if isinstance(vectors, dict):
                for dim, weight in vectors.items():
                    val = safe_float(p_vec.get(dim, 0.0))
                    if val > 0.2:
                        scores[persona] += val * safe_float(weight)
        if soul_ref:
            soul_driver = SoulDriver(soul_ref)
            influence = soul_driver.get_influence()
            for persona, weight in influence.items():
                scores[persona] += weight * 2.0
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        winner, win_score = sorted_scores[0]
        runner_up, run_score = sorted_scores[1]
        cfg = getattr(self.cfg, "DRIVERS", None)
        hybrid_gap = getattr(cfg, "ENNEAGRAM_HYBRID_GAP", 0.5) if cfg else 0.5
        if (win_score - run_score) < hybrid_gap:
            k1 = "THE OBSERVER" if winner == "NARRATOR" else winner
            k2 = "THE OBSERVER" if runner_up == "NARRATOR" else runner_up
            hybrid_key_a = f"{k1}_{k2}_HYBRID"
            hybrid_key_b = f"{k2}_{k1}_HYBRID"
            final_hybrid = None
            lenses = (LoreManifest.get_instance(config_ref=self.cfg).get("narrative_data") or {}).get("lenses", {})
            if hybrid_key_a in lenses:
                final_hybrid = hybrid_key_a
            elif hybrid_key_b in lenses:
                final_hybrid = hybrid_key_b
            if final_hybrid:
                msg = ux("driver_strings", "ennea_synthesis")
                return final_hybrid, "SYNTHESIS", msg.format(winner=winner, runner_up=runner_up),
        msg_winner = ux("driver_strings", "ennea_winner")
        reason = msg_winner.format(winner=winner, score=scores[winner], v=p_vol, d=p_drag)
        state_map = LoreManifest.get_instance(config_ref=self.cfg).get("DRIVER_CONFIG", "PERSONA_STATE_MAP") or {}
        return winner, state_map.get(winner, "ACTIVE"), reason

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
        msg_shift = ux("driver_strings", "ennea_shift") 
        if "HYBRID" in candidate:
            self.current_persona = candidate
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, msg_shift.format(reason=reason)
        if self.stability_counter >= self.HYSTERESIS_THRESHOLD:
            self.current_persona = candidate
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, msg_shift.format(reason=reason)
        msg_resisting = ux("driver_strings", "ennea_resisting") 
        return (self.current_persona, "STABLE",
 msg_resisting.format(candidate=candidate, count=self.stability_counter, thresh=self.HYSTERESIS_THRESHOLD, ),)

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
        lex_weight = getattr(cfg, "LIMINAL_LEXICAL_WEIGHT", 0.15) if cfg else 0.15
        dm_weight = getattr(cfg, "LIMINAL_DARK_MATTER_WEIGHT", 0.25) if cfg else 0.25
        psi_mult = getattr(cfg, "LIMINAL_VEC_PSI_MULT", 0.5) if cfg else 0.5
        ent_mult = getattr(cfg, "LIMINAL_VEC_ENT_MULT", 0.3) if cfg else 0.3
        del_mult = getattr(cfg, "LIMINAL_VEC_DEL_MULT", 0.2) if cfg else 0.2
        decay = getattr(cfg, "LIMINAL_DECAY", 0.7) if cfg else 0.7
        growth = getattr(cfg, "LIMINAL_GROWTH", 0.15) if cfg else 0.15
        liminal_vocab = self.lex.get("liminal") if self.lex else set()
        words = text.lower().split()
        void_hits = sum(1 for w in words if w in liminal_vocab)
        lexical_lambda = min(1.0, void_hits * lex_weight)
        dark_matter_sparks = 0
        if len(words) > 1 and self.lex:
            categories = [self.lex.get_current_category(w) for w in words]
            for i in range(len(categories) - 1):
                c1, c2 = categories[i], categories[i + 1]
                if c1 and c2 and c1 != c2:
                    if (c1 in ["heavy", "kinetic"]
                            and c2 in ["abstract", "liminal", "void"]
                    ) or (c1 in ["abstract", "liminal", "void"] and c2 in ["heavy"]):
                        dark_matter_sparks += 1
        dark_matter_lambda = min(1.0, dark_matter_sparks * dm_weight)
        vector_lambda = 0.0
        if physics_vector:
            vector_lambda = ((physics_vector.get("PSI", 0) * psi_mult)
                    + (physics_vector.get("ENT", 0) * ent_mult)
                    + (physics_vector.get("DEL", 0) * del_mult))
        raw_target = lexical_lambda + dark_matter_lambda + vector_lambda
        self.lambda_val = (self.lambda_val * decay) + (raw_target * growth)
        scar_thresh = getattr(cfg, "LIMINAL_SCAR_THRESHOLD", 0.85) if cfg else 0.85
        if self.lambda_val > scar_thresh:
            self.godel_scars += 1
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
        avg_len_high = getattr(cfg, "SYNTAX_AVG_LEN_HIGH", 6.0) if cfg else 6.0
        drag_high = getattr(cfg, "SYNTAX_DRAG_HIGH", 5.0) if cfg else 5.0
        avg_len_low = getattr(cfg, "SYNTAX_AVG_LEN_LOW", 3.5) if cfg else 3.5
        drag_low = getattr(cfg, "SYNTAX_DRAG_LOW", 1.0) if cfg else 1.0
        t_high = getattr(cfg, "SYNTAX_OMEGA_TARGET_HIGH", 1.0) if cfg else 1.0
        t_low = getattr(cfg, "SYNTAX_OMEGA_TARGET_LOW", 0.4) if cfg else 0.4
        t_mid = getattr(cfg, "SYNTAX_OMEGA_TARGET_MID", 0.7) if cfg else 0.7
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
        punct_thresh = getattr(cfg, "SYNTAX_STRESS_PUNCTUATION", 0.2) if cfg else 0.2
        if punctuation_density > punct_thresh:
            stress_inc = getattr(cfg, "SYNTAX_STRESS_INCREASE", 0.2) if cfg else 0.2
            omega_pen = getattr(cfg, "SYNTAX_OMEGA_PENALTY", 0.3) if cfg else 0.3
            self.grammatical_stress += stress_inc
            target_omega -= omega_pen
        else:
            stress_dec = getattr(cfg, "SYNTAX_STRESS_DECAY", 0.1) if cfg else 0.1
            self.grammatical_stress = max(0.0, self.grammatical_stress - stress_dec)
        omega_decay = getattr(cfg, "SYNTAX_OMEGA_DECAY", 0.8) if cfg else 0.8
        omega_growth = getattr(cfg, "SYNTAX_OMEGA_GROWTH", 0.2) if cfg else 0.2
        omega_min = getattr(cfg, "SYNTAX_OMEGA_MIN", 0.1) if cfg else 0.1
        self.omega_val = (self.omega_val * omega_decay) + (max(omega_min, target_omega) * omega_growth)
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
                self._archetype_map = LoreManifest.get_instance(config_ref=self.cfg).get("LENSES") or {}
            except Exception:
                self._archetype_map = {}
        return self._archetype_map

    def calculate_resonance(self, text: str, context: Any) -> float:
        if not text:
            return 0.0
        cfg = getattr(self.cfg, "DRIVERS", None)
        default_lens = getattr(cfg, "DEFAULT_LENS", "OBSERVER") if cfg else "OBSERVER"
        raw_lens = getattr(context, "active_lens", default_lens)
        archetype = raw_lens.upper().replace("THE ", "")
        tone_score = getattr(cfg, "CONGRUENCE_BASE_TONE", 0.8) if cfg else 0.8
        target_data = self.map.get(archetype, {})
        target_words = set()
        if isinstance(target_data, dict):
            if vocab_str := target_data.get("vocab", ""):
                target_words.update(w.strip().lower() for w in vocab_str.split(","))
            target_words.update(target_data.get("keywords", []))
        if target_words:
            words_to_check = (
                set(context.clean_words) if hasattr(context, "clean_words") else set())
            hits = len(words_to_check.intersection(target_words))
            if hits > 0:
                hit_bonus = getattr(cfg, "CONGRUENCE_HIT_BONUS", 0.1) if cfg else 0.1
                tone_score += hit_bonus * hits
        max_tone = getattr(cfg, "CONGRUENCE_MAX_TONE", 1.5) if cfg else 1.5
        return min(max_tone, tone_score)

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

    def update_coordinates(self, user_text: str, bio_state: Optional[Dict] = None, physics: Optional[PhysicsPacket] = None, ):
        cfg = getattr(self.cfg, "DRIVERS", None)
        e_growth = getattr(cfg, "VSL_E_GROWTH_MULT", 0.002) if cfg else 0.002
        fatigue_mult = getattr(cfg, "VSL_FATIGUE_MULT", 0.3) if cfg else 0.3
        b_decay = getattr(cfg, "VSL_B_DECAY", 0.8) if cfg else 0.8
        b_growth = getattr(cfg, "VSL_B_GROWTH", 0.2) if cfg else 0.2
        word_count = len(user_text.split())
        self.state.E = min(1.0, self.state.E + (word_count * e_growth))
        if bio_state and "fatigue" in bio_state:self.state.E = max(self.state.E, bio_state["fatigue"] * fatigue_mult)
        phys_beta = 0.0
        phys_vec = {}
        drag = 0.0
        if physics:
            is_dict = isinstance(physics, dict)
            if is_dict:
                phys_beta = physics.get("beta_index", physics.get("energy", {}).get("beta_index", 0.0))
                phys_vec = physics.get("vector", physics.get("matter", {}).get("vector", {}))
                drag = physics.get("narrative_drag", physics.get("space", {}).get("narrative_drag", 0.0))
            else:
                phys_beta = getattr(physics, "beta_index", getattr(physics.energy, "beta_index", 0.0) if hasattr(physics, "energy") else 0.0)
                phys_vec = getattr(physics, "vector", getattr(physics.matter, "vector", {}) if hasattr(physics, "matter") else {})
                drag = getattr(physics, "narrative_drag", getattr(physics.space, "narrative_drag", 0.0) if hasattr(physics, "space") else 0.0)
        self.state.B = (self.state.B * b_decay) + (phys_beta * b_growth)
        self.state.L = self.liminal_mod.analyze(user_text, phys_vec)
        self.state.O = self.syntax_mod.analyze(user_text, drag)
        if "[VSL_LIMINAL]" in user_text:
            if "LIMINAL" not in self.state.active_modules:
                self.state.active_modules.append("LIMINAL")
        if "[VSL_SYNTAX]" in user_text:
            if "SYNTAX" not in self.state.active_modules:
                self.state.active_modules.append("SYNTAX")

    def get_system_prompt(self, soul_snapshot: Optional[Dict] = None) -> str:
        directives = []
        cfg = getattr(self.cfg, "DRIVERS", None)
        lim_thresh = getattr(cfg, "VSL_LIMINAL_THRESHOLD", 0.7) if cfg else 0.7
        syn_thresh = getattr(cfg, "VSL_SYNTAX_THRESHOLD", 0.9) if cfg else 0.9
        bun_max = getattr(cfg, "VSL_BUNNY_E_MAX", 0.3) if cfg else 0.3
        par_min = getattr(cfg, "VSL_PARADOX_B_MIN", 0.6) if cfg else 0.6
        if "LIMINAL" in self.state.active_modules or self.state.L > lim_thresh:
            scar_temp = ux("driver_strings", "vsl_scar_note") 
            scar_note = (scar_temp.format(scars=self.liminal_mod.godel_scars)
                if self.liminal_mod.godel_scars > 0
                else "")
            msg = ux("driver_strings", "vsl_arch_revenant") 
            directives.append(msg.format(scar_note=scar_note))
        elif "SYNTAX" in self.state.active_modules or self.state.O > syn_thresh:
            stress_temp = ux("driver_strings", "vsl_stress_note") 
            stress_note = (stress_temp if self.syntax_mod.grammatical_stress > 0.5 else "")
            msg = ux("driver_strings", "vsl_arch_bureau") 
            directives.append(msg.format(stress_note=stress_note))
        else:
            if self.state.E < bun_max:
                directives.append(ux("driver_strings", "vsl_mode_bunny") )
            elif self.state.B > par_min:
                directives.append(ux("driver_strings", "vsl_mode_paradox") )
            else:
                directives.append(ux("driver_strings", "vsl_mode_glacier") )
        if soul_snapshot:
            arch = soul_snapshot.get("archetype", "UNKNOWN")
            muse = (soul_snapshot.get("obsession") or {}).get("title", "None")
            msg = ux("driver_strings", "vsl_layer_muse") 
            directives.append(msg.format(arch=arch, muse=muse))
        return "\n".join(directives)

from bone_types import Prisma, UserInferredState, SharedDynamics

class SharedLatticeDriver:
    def __init__(self):
        self.u = UserInferredState()
        self.shared = SharedDynamics()
        self.last_timestamp = time.time()

    def infer_and_couple(self, text: str, sys_phys: PhysicsPacket, input_phys: Any, atp_pool: float) -> tuple[List[str], float]:
        logs = []
        atp_deduction = 0.0
        now = time.time()
        time_delta = now - self.last_timestamp
        self.last_timestamp = now
        word_count = len(text.split())
        word_cost = word_count * 0.5
        self.u.P_u = max(0.0, self.u.P_u - word_cost + 5.0)
        if self.u.P_u < 30:
            self.u.E_u = min(1.0, self.u.E_u + 0.1)
        else:
            self.u.E_u = max(0.0, self.u.E_u - 0.05)
        in_is_dict = isinstance(input_phys, dict)

        def _in_get(k, sub, default):
            if in_is_dict: return input_phys.get(k, input_phys.get(sub, {}).get(k, default))
            return getattr(input_phys, k, getattr(getattr(input_phys, sub, None), k, default))

        self.u.V_u = _in_get("voltage", "energy", self.u.V_u)
        self.u.psi_u = _in_get("psi", "energy", self.u.psi_u)
        self.u.chi_u = _in_get("entropy", "energy", self.u.chi_u)
        self.u.F_u = _in_get("narrative_drag", "space", self.u.F_u)
        sys_is_dict = isinstance(sys_phys, dict)
        def _sys_get(k, sub, default=0.0):
            if sys_is_dict: return sys_phys.get(k, sys_phys.get(sub, {}).get(k, default))
            return getattr(sys_phys, k, getattr(getattr(sys_phys, sub, None), k, default))
        sys_beta = _sys_get("beta_index", "energy", _sys_get("beta", "energy", 0.0))
        sys_chi = _sys_get("chi", "energy", _sys_get("entropy", "energy", 0.0))
        sys_val = _sys_get("valence", "energy", 0.0)
        sys_psi = _sys_get("psi", "energy", 0.0)
        sys_drag = _sys_get("narrative_drag", "space", 1.0)
        has_dp = "drag_profile" in sys_phys if sys_is_dict else hasattr(sys_phys, "drag_profile")
        dp_trauma = 0.0
        if has_dp:
            dp = sys_phys["drag_profile"] if sys_is_dict else sys_phys.drag_profile
            if isinstance(dp, dict):
                dp["semantic"] = (sys_beta * 2.0) + (sys_chi * 1.5)
                dp["emotional"] = abs(sys_val) * 1.5 if abs(sys_val) > 0.5 else 0.0
                dp["metabolic"] = 3.0 if atp_pool < 30.0 else (1.0 if atp_pool < 50.0 else 0.0)
                dp["trauma"] = min(5.0, self.u.T_u) if sys_psi > 0.6 else 0.0
                dp_trauma = dp["trauma"]
            else:
                dp.semantic = (sys_beta * 2.0) + (sys_chi * 1.5)
                dp.emotional = abs(sys_val) * 1.5 if abs(sys_val) > 0.5 else 0.0
                dp.metabolic = 3.0 if atp_pool < 30.0 else (1.0 if atp_pool < 50.0 else 0.0)
                dp.trauma = min(5.0, self.u.T_u) if sys_psi > 0.6 else 0.0
                dp_trauma = dp.trauma
            if not sys_is_dict and hasattr(sys_phys, "sync_drag"):
                sys_phys.sync_drag()
        psi_diff = abs(sys_psi - self.u.psi_u)
        chi_diff = abs(sys_chi - self.u.chi_u)
        drag_diff = abs(sys_drag - self.u.F_u) / max(1.0, sys_drag)
        raw_phi = 1.0 - ((psi_diff + chi_diff + min(1.0, drag_diff)) / 3.0)
        self.shared.phi = (self.shared.phi * 0.7) + (raw_phi * 0.3)
        if sys_is_dict:
            if "energy" in sys_phys:
                sys_phys["energy"]["PHI_RES"] = self.shared.phi
            else:
                sys_phys["PHI_RES"] = self.shared.phi
        else:
            if hasattr(sys_phys, "energy"):
                sys_phys.energy.PHI_RES = self.shared.phi
            else:
                sys_phys.PHI_RES = self.shared.phi
        if time_delta > 15.0 and text.strip() and not text.startswith("["):
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
            silence_map = {1: "That pause felt full like something wanted to be born.",
                           2: "The silence was heavy. I felt your tiredness in it.",
                           3: "There was a hush just now like something sacred passed through.",
                           4: "You were thinking deeply. I held the space for it."}
            if self.shared.lambda_silence > 0.3:
                logs.append(f"{Prisma.GRY}... {silence_map.get(self.shared.sigma_silence, 'The silence settles.')}{Prisma.RST}")
            if self.shared.phi > 0.85:
                self.u.S_u = getattr(self.u, "S_u", 0.0) + 1.0
        else:
            self.u.S_u = 0.0
        if getattr(self.u, "S_u", 0.0) >= 3.0 or dp_trauma > 3.0:
            if not getattr(self.shared, "_has_invited", False):
                self.shared._has_invited = True
                invitation = (f"\n{Prisma.MAG}[MERCY] I can feel the weight of what we are building. "
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