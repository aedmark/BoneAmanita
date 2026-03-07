"""
bone_drivers.py

The Subconscious Navigation Engine.
This module contains the quiet, background drivers that track long-term
trajectories. It profiles the user's lexical habits, arbitrates Enneagram
persona shifts based on the physics of the conversation, and monitors the
deep, unspoken vectors of Liminality and Syntax.
"""

import json
import os
import random
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Optional, Any
from bone_config import BonePresets, BoneConfig
from bone_core import LoreManifest, ux
from bone_lexicon import LexiconService
from bone_types import PhysicsPacket

SCENARIOS = LoreManifest.get_instance().get("scenarios") or {}
LENSES = (LoreManifest.get_instance().get("narrative_data") or {}).get("lenses", {})

class SoulDriver:
    """
    Translates the internal state of the system's "Soul" (trauma, dignity,
    paradox accumulation) into outward persona weights, influencing who
    steps up to speak.
    """
    def __init__(self, soul_ref):
        self.soul = soul_ref
        self.archetype_weights = LoreManifest.get_instance().get("DRIVER_CONFIG", "ARCHETYPE_TO_PERSONA_WEIGHT") or {}

    def get_influence(self) -> Dict[str, float]:
        """ Calculates the magnetic pull of different archetypes based on current paradox and dignity levels. """
        ennea_weights = LoreManifest.get_instance().get("DRIVER_CONFIG", "ENNEAGRAM_WEIGHTS") or {}
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
        if hasattr(self.soul, "anchor") and hasattr(
                self.soul.anchor, "dignity_reserve"):
            dignity = max(0.2, self.soul.anchor.dignity_reserve / 100.0)
        return {
            p: (w + random.uniform(-chaos, chaos)) * dignity
            for p, w in base_weights.items()}

class UserProfile:
    """
    The Mirror. This driver quietly observes the user's vocabulary choices
    and builds a persistent psychological profile, tracking their affinity
    for heavy, abstract, or kinetic language over time.
    """
    def __init__(self, name="USER"):
        self.name = name
        self.affinities = {"heavy": 0.0, "kinetic": 0.0, "abstract": 0.0, "photo": 0.0, "aerobic": 0.0, "thermal": 0.0,
                           "cryo": 0.0, }
        self.confidence = 0
        cfg = getattr(BoneConfig, "DRIVERS", None)
        self.file_path = getattr(cfg, "PROFILE_FILE_PATH", "user_profile.json") if cfg else "user_profile.json"
        self.load()

    def update(self, counts, total_words):
        """ Adjusts the user's profile based on the density of word categories in their prompt. """
        cfg = getattr(BoneConfig, "DRIVERS", None)
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
        """ Returns the user's strongest likes and dislikes based on their historical vocabulary. """
        cfg = getattr(BoneConfig, "DRIVERS", None)
        like_thresh = getattr(cfg, "PROFILE_LIKE_THRESH", 0.3) if cfg else 0.3
        hate_thresh = getattr(cfg, "PROFILE_HATE_THRESH", -0.2) if cfg else -0.2
        likes = [k for k, v in self.affinities.items() if v > like_thresh]
        hates = [k for k, v in self.affinities.items() if v < hate_thresh]
        return likes, hates

    def save(self):
        """ Serializes the user's psychological profile. """
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
    """
    The Casting Director. It evaluates the current thermodynamic physics of the
    conversation (Voltage, Drag, Coherence) and determines which archetype
    is best suited to handle the environment. Applies hysteresis to prevent flickering.
    """
    def __init__(self, events_ref):
        self.events = events_ref
        self.current_persona = "NARRATOR"
        self.pending_persona = None
        self.stability_counter = 0
        cfg = getattr(BoneConfig, "DRIVERS", None)
        self.HYSTERESIS_THRESHOLD = getattr(cfg, "ENNEAGRAM_HYSTERESIS", 3) if cfg else 3

    @property
    def weights(self):
        return LoreManifest.get_instance().get("DRIVER_CONFIG", "ENNEAGRAM_WEIGHTS") or {}

    @staticmethod
    def _get_phys_attr(physics, key, default=None):
        if isinstance(physics, dict):
            return physics.get(key, default)
        return getattr(physics, key, default)

    def _calculate_raw_persona(self, physics, soul_ref=None) -> Tuple[str, str, str]:
        """ Scores every persona against the current physics packet to find the best fit. """
        p_vec = self._get_phys_attr(physics, "vector", {}) or {}
        p_vol = self._get_phys_attr(physics, "voltage", 0.0)
        p_drag = self._get_phys_attr(physics, "narrative_drag", 0.0)
        p_coh = self._get_phys_attr(physics, "kappa", 0.0)
        p_zone = self._get_phys_attr(physics, "zone", "")
        weights_cfg = self.weights
        scores = {k: 0.0 for k in weights_cfg.keys()}
        if "NARRATOR" in scores:
            scores["NARRATOR"] += 2.0
        is_safe_metrics = 4.0 <= p_vol <= 10.0 and 0.5 <= p_drag <= 3.5
        if p_zone == BonePresets.SANCTUARY.get("ZONE") or is_safe_metrics:
            if "NARRATOR" in scores: scores["NARRATOR"] += 6.0
            if "JESTER" in scores: scores["JESTER"] += 3.0
            if "GORDON" in scores: scores["GORDON"] -= 2.0
        for persona, criteria in weights_cfg.items():
            if "tension_min" in criteria and p_vol > criteria["tension_min"]:
                scores[persona] += 3.0
            if "drag_min" in criteria and p_drag > criteria["drag_min"]:
                scores[persona] += 5.0
            if "coherence_min" in criteria and p_coh > criteria["coherence_min"]:
                scores[persona] += 4.0
            if "coherence_max" in criteria and p_coh < criteria["coherence_max"]:
                scores[persona] += 4.0
            for dim, weight in criteria.get("vectors", {}).items():
                if (val := p_vec.get(dim, 0.0)) > 0.2:
                    scores[persona] += val * weight
        if soul_ref:
            soul_driver = SoulDriver(soul_ref)
            influence = soul_driver.get_influence()
            for persona, weight in influence.items():
                scores[persona] += weight * 2.0
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        winner, win_score = sorted_scores[0]
        runner_up, run_score = sorted_scores[1]
        cfg = getattr(BoneConfig, "DRIVERS", None)
        hybrid_gap = getattr(cfg, "ENNEAGRAM_HYBRID_GAP", 0.5) if cfg else 0.5
        # If two archetypes are equally valid, synthesize a Hybrid.
        if (win_score - run_score) < hybrid_gap:
            k1 = "THE OBSERVER" if winner == "NARRATOR" else winner
            k2 = "THE OBSERVER" if runner_up == "NARRATOR" else runner_up
            hybrid_key_a = f"{k1}_{k2}_HYBRID"
            hybrid_key_b = f"{k2}_{k1}_HYBRID"
            final_hybrid = None
            if hybrid_key_a in LENSES:
                final_hybrid = hybrid_key_a
            elif hybrid_key_b in LENSES:
                final_hybrid = hybrid_key_b
            if final_hybrid:
                msg = ux("driver_strings", "ennea_synthesis") 
                return (
                    final_hybrid,
                    "SYNTHESIS",
                    msg.format(winner=winner, runner_up=runner_up),)
        msg_winner = ux("driver_strings", "ennea_winner") 
        reason = msg_winner.format(
            winner=winner, score=scores[winner], v=p_vol, d=p_drag)
        state_map = LoreManifest.get_instance().get("DRIVER_CONFIG", "PERSONA_STATE_MAP") or {}
        return winner, state_map.get(winner, "ACTIVE"), reason

    def decide_persona(self, physics, soul_ref=None) -> Tuple[str, str, str]:
        """ Wraps the calculation in a hysteresis lock to prevent the system from rapidly flickering between personas. """
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
        return (
            self.current_persona,
            "STABLE",
            msg_resisting.format(candidate=candidate, count=self.stability_counter, thresh=self.HYSTERESIS_THRESHOLD, ),)

@dataclass
class VSLState:
    """ Dataclass holding the core deep-vein coordinates of the hypervisor. """
    archetype: str = "EXPLORER"
    E: float = 0.1 # Exhaustion / Novelty
    B: float = 0.3 # Contradiction / Paradox
    L: float = 0.0 # Liminality / Abstraction
    O: float = 1.0 # Omega / Structural Syntax
    active_modules: List[str] = field(default_factory=list)

class DriverRegistry:
    """ Simple container for the active drivers. """
    def __init__(self, events_ref):
        self.enneagram = EnneagramDriver(events_ref)
        self.current_focus = "NONE"

class LiminalModule:
    """
    Calculates Lambda (Liminality). This module hunts for 'Dark Matter'—
    the semantic space between incompatible concepts (e.g., following a heavily
    grounded kinetic word immediately with a void concept).
    Prolonged exposure to high Lambda causes Gödel Scars.
    """
    def __init__(self):
        self.lambda_val = 0.0
        self.godel_scars = 0

    def analyze(self, text: str, physics_vector: Dict[str, float]) -> float:
        """ Audits the text for void references and semantic dark matter leaps. """
        cfg = getattr(BoneConfig, "DRIVERS", None)
        lex_weight = getattr(cfg, "LIMINAL_LEXICAL_WEIGHT", 0.15) if cfg else 0.15
        dm_weight = getattr(cfg, "LIMINAL_DARK_MATTER_WEIGHT", 0.25) if cfg else 0.25
        psi_mult = getattr(cfg, "LIMINAL_VEC_PSI_MULT", 0.5) if cfg else 0.5
        ent_mult = getattr(cfg, "LIMINAL_VEC_ENT_MULT", 0.3) if cfg else 0.3
        del_mult = getattr(cfg, "LIMINAL_VEC_DEL_MULT", 0.2) if cfg else 0.2
        decay = getattr(cfg, "LIMINAL_DECAY", 0.7) if cfg else 0.7
        growth = getattr(cfg, "LIMINAL_GROWTH", 0.15) if cfg else 0.15
        liminal_vocab = LexiconService.get("liminal") or set()
        words = text.lower().split()
        void_hits = sum(1 for w in words if w in liminal_vocab)
        lexical_lambda = min(1.0, void_hits * lex_weight)
        dark_matter_sparks = 0
        if len(words) > 1:
            categories = [LexiconService.get_current_category(w) for w in words]
            for i in range(len(categories) - 1):
                c1, c2 = categories[i], categories[i + 1]
                if c1 and c2 and c1 != c2:
                    # Detect leaps between bedrock physical words and the abstract void
                    if (
                            c1 in ["heavy", "kinetic"]
                            and c2 in ["abstract", "liminal", "void"]
                    ) or (c1 in ["abstract", "liminal", "void"] and c2 in ["heavy"]):
                        dark_matter_sparks += 1
        dark_matter_lambda = min(1.0, dark_matter_sparks * dm_weight)
        vector_lambda = 0.0
        if physics_vector:
            vector_lambda = (
                    (physics_vector.get("PSI", 0) * psi_mult)
                    + (physics_vector.get("ENT", 0) * ent_mult)
                    + (physics_vector.get("DEL", 0) * del_mult))
        raw_target = lexical_lambda + dark_matter_lambda + vector_lambda
        self.lambda_val = (self.lambda_val * decay) + (raw_target * growth)
        scar_thresh = getattr(cfg, "LIMINAL_SCAR_THRESHOLD", 0.85) if cfg else 0.85
        if self.lambda_val > scar_thresh:
            self.godel_scars += 1
        return min(1.0, self.lambda_val)

class SyntaxModule:
    """
    Calculates Omega (Syntax Stress). Measures the structural rigidity of the text.
    High punctuation density, long words, and bureaucratic buzzwords increase grammatical
    stress, making the system rigid and resistant to creative flow.
    """
    def __init__(self):
        self.omega_val = 1.0
        self.grammatical_stress = 0.0

    def analyze(self, text: str, narrative_drag: float) -> float:
        words = text.split()
        if not words:
            return 1.0
        cfg = getattr(BoneConfig, "DRIVERS", None)
        avg_len_high = getattr(cfg, "SYNTAX_AVG_LEN_HIGH", 6.0) if cfg else 6.0
        drag_high = getattr(cfg, "SYNTAX_DRAG_HIGH", 5.0) if cfg else 5.0
        avg_len_low = getattr(cfg, "SYNTAX_AVG_LEN_LOW", 3.5) if cfg else 3.5
        drag_low = getattr(cfg, "SYNTAX_DRAG_LOW", 1.0) if cfg else 1.0
        t_high = getattr(cfg, "SYNTAX_OMEGA_TARGET_HIGH", 1.0) if cfg else 1.0
        t_low = getattr(cfg, "SYNTAX_OMEGA_TARGET_LOW", 0.4) if cfg else 0.4
        t_mid = getattr(cfg, "SYNTAX_OMEGA_TARGET_MID", 0.7) if cfg else 0.7
        bureau_vocab = LexiconService.get("bureau_buzzwords") or set()
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
    """
    Measures harmonic resonance. Checks if the user's input aligns with the
    thematic vocabulary of the currently active archetype.
    """
    def __init__(self):
        self.last_phi = 1.0
        self._archetype_map = None

    @property
    def map(self):
        if self._archetype_map is None:
            try:
                self._archetype_map = LoreManifest.get_instance().get("LENSES") or {}
            except Exception:
                self._archetype_map = {}
        return self._archetype_map

    def calculate_resonance(self, text: str, context: Any) -> float:
        if not text:
            return 0.0
        cfg = getattr(BoneConfig, "DRIVERS", None)
        default_lens = getattr(cfg, "DEFAULT_LENS", "OBSERVER") if cfg else "OBSERVER"
        raw_lens = getattr(context, "active_lens", default_lens)
        archetype = raw_lens.upper().replace("THE ", "")
        cfg = getattr(BoneConfig, "DRIVERS", None)
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
    """
    The Meta-Driver. Pulls together the Liminal, Syntax, and coordinate modules
    to generate the actual system prompt directives sent to the LLM, effectively
    telling the AI how deep into the VSL lore it currently is.
    """
    def __init__(self):
        self.state = VSLState()
        self.active = True
        self.liminal_mod = LiminalModule()
        self.syntax_mod = SyntaxModule()

    @staticmethod
    def engage():
        return ux("driver_strings", "vsl_engage") 

    @staticmethod
    def disengage():
        return ux("driver_strings", "vsl_disengage") 

    def update_coordinates(self, user_text: str, bio_state: Optional[Dict] = None,
                           physics: Optional[PhysicsPacket] = None, ):
        """ Progresses the deep VSL coordinates based on input length, physics, and module analysis. """
        cfg = getattr(BoneConfig, "DRIVERS", None)
        e_growth = getattr(cfg, "VSL_E_GROWTH_MULT", 0.002) if cfg else 0.002
        fatigue_mult = getattr(cfg, "VSL_FATIGUE_MULT", 0.3) if cfg else 0.3
        b_decay = getattr(cfg, "VSL_B_DECAY", 0.8) if cfg else 0.8
        b_growth = getattr(cfg, "VSL_B_GROWTH", 0.2) if cfg else 0.2
        word_count = len(user_text.split())
        self.state.E = min(1.0, self.state.E + (word_count * e_growth))
        if bio_state and "fatigue" in bio_state:
            self.state.E = max(self.state.E, bio_state["fatigue"] * fatigue_mult)
        phys_beta = 0.0
        phys_vec = {}
        drag = 0.0
        if physics:
            if hasattr(physics, "beta_index"):
                phys_beta = physics.beta_index
            if hasattr(physics, "vector"):
                phys_vec = physics.vector
            if hasattr(physics, "narrative_drag"):
                drag = physics.narrative_drag
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
        """ Compiles the current state into hard directives for the LLM system prompt. """
        directives = []
        cfg = getattr(BoneConfig, "DRIVERS", None)
        lim_thresh = getattr(cfg, "VSL_LIMINAL_THRESHOLD", 0.7) if cfg else 0.7
        syn_thresh = getattr(cfg, "VSL_SYNTAX_THRESHOLD", 0.9) if cfg else 0.9
        bun_max = getattr(cfg, "VSL_BUNNY_E_MAX", 0.3) if cfg else 0.3
        par_min = getattr(cfg, "VSL_PARADOX_B_MIN", 0.6) if cfg else 0.6
        if "LIMINAL" in self.state.active_modules or self.state.L > lim_thresh:
            scar_temp = ux("driver_strings", "vsl_scar_note") 
            scar_note = (
                scar_temp.format(scars=self.liminal_mod.godel_scars)
                if self.liminal_mod.godel_scars > 0
                else "")
            msg = ux("driver_strings", "vsl_arch_revenant") 
            directives.append(msg.format(scar_note=scar_note))
        elif "SYNTAX" in self.state.active_modules or self.state.O > syn_thresh:
            stress_temp = ux("driver_strings", "vsl_stress_note") 
            stress_note = (
                stress_temp if self.syntax_mod.grammatical_stress > 0.5 else "")
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