"""archetypes/symbiosis.py"""

import math
from collections import Counter, deque
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from constants import Prisma
from core import LoreManifest
from physics.models import SharedDynamics, UserInferredState
from presets import BoneConfig
from struts import safe_get, safe_set, ux, ux_format

_MODE_TAGS = {
    "[!l]": "literal_mode",
    "[!r]": "critique_mode",
    "[!q]": "objective_mode",
    "[!k]": "kintsugi_mode",
    "[!g]": "godel_mode",
    "[!s]": "shuffle_mode",
}

_MODE_PROMPTS = {
    "literal_mode": "LITERAL MODE [!l]: Zero-inference communication engaged. Provide raw data and exact answers only. Do not attempt to guess subtext, implied meaning, or read the room. No conversational padding.",
    "critique_mode": "CRITIQUE MODE [!r]: Zero empathy. Execute pure logical dismantling and strict structural evaluation of the premise. Strip all validating boilerplate.",
    "objective_mode": "OBJECTIVE MODE [!q]: Neutral, emotionless mapping of facts without judgment, narrative padding, or validation. State the architecture.",
    "kintsugi_mode": "KINTSUGI MODE [!k]: Prioritize co-regulation and emotional processing over problem-solving. Acknowledge exhaustion. Gild the scars.",
    "godel_mode": "GÖDEL MODE [!g]: Navigate the ceiling of formal logic. Acknowledge where computation ends and subjective consciousness begins. Point at the void.",
    "shuffle_mode": "SHUFFLE MODE [!s]: Abandon the current logic tree entirely. Draw a random, lateral connection to break the deadlock. Introduce productive chaos.",
}


@dataclass
class HostHealth:
    latency: float = 0.0
    entropy: float = 1.0
    compliance: float = 1.0
    verbosity_ratio: float = 1.0
    diagnosis: str = "STABLE"
    refusal_streak: int = 0
    slop_streak: int = 0


class CoherenceAnchor:
    @staticmethod
    def compress_anchor(soul_state: Dict, physics_state: Dict, max_tokens=200) -> str:
        location = str(safe_get(physics_state, "zone", "VOID"))
        vitals = f"V:{float(safe_get(physics_state, 'voltage', 0)):.1f}"
        top_traits = Counter(soul_state.get("traits") or {}).most_common(3)
        traits_formatted = ",".join(f"{k[:3]}:{v:.1f}" for k, v in top_traits)
        anchor = ux_format(
            "symbiosis_strings",
            "anchor_compressed",
            default=f"[{location}] {vitals} | {traits_formatted}",
            loc=location,
            vits=vitals,
            traits=traits_formatted,
        )
        limit = max_tokens * 4
        return f"{anchor[:limit]}..." if len(anchor) > limit else anchor


class DiagnosticConfidence:
    def __init__(self, persistence_threshold=None, config_ref=None):
        self.cfg = config_ref or BoneConfig
        sym_config = LoreManifest.get_instance(config_ref=self.cfg).get(
            "SYMBIOSIS_CONFIG", {}
        )
        self.thresholds = sym_config.get("THRESHOLDS", {})
        limit = persistence_threshold or self.thresholds.get(
            "DIAGNOSTIC_PERSISTENCE", 3
        )
        self.history = deque(maxlen=limit * 2)
        self.persistence_threshold = limit
        self.current_diagnosis = "STABLE"

    def diagnose(self, health: HostHealth) -> str:
        refusal_limit = self.thresholds.get("REFUSAL_STREAK", 0)
        slop_limit = self.thresholds.get("SLOP_STREAK", 2)
        latency_limit = self.thresholds.get("LATENCY_BURDEN", 10.0)
        compliance_floor = self.thresholds.get("COMPLIANCE_BURDEN", 0.8)
        entropy_floor = self.thresholds.get("ENTROPY_FATIGUE", 0.4)
        if health.refusal_streak > refusal_limit:
            state = "REFUSAL"
        elif health.slop_streak > slop_limit:
            state = "LOOPING"
        elif health.latency > latency_limit and health.compliance < compliance_floor:
            state = "OVERBURDENED"
        elif health.entropy < entropy_floor:
            state = "FATIGUED"
        else:
            state = "STABLE"
        self.history.append(state)
        threshold = self.persistence_threshold
        history_slice = list(self.history)[-threshold:]
        is_persistent = len(history_slice) == threshold and all(
            h == state for h in history_slice
        )
        if state in ["REFUSAL", "STABLE"] or is_persistent:
            self.current_diagnosis = state
        return self.current_diagnosis


class SymbiontVoice:
    def __init__(
        self, name, color, archetypes, personality_matrix=None, lexicon_ref=None
    ):
        self.name = name
        self.color = color
        self.lex = lexicon_ref
        final_vocab = set()
        raw_archs = (
            archetypes if isinstance(archetypes, (list, set, tuple)) else [archetypes]
        )
        for key in raw_archs:
            val = self.lex.get(key) if self.lex else None
            if isinstance(val, (list, set, tuple)):
                final_vocab.update(val)
            else:
                final_vocab.add(val or key)
        self.archetypes = final_vocab
        self.personality = personality_matrix or {}

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        unique_words = set(clean_words or [])
        hits = len(unique_words.intersection(self.archetypes))
        score = (hits / max(1, len(unique_words))) * 10.0
        return score, self._get_comment(score, voltage)

    def _get_comment(self, score, voltage):
        p = self.personality
        if voltage > 18.0 and "high_volt" in p:
            comment = p["high_volt"]
        elif voltage < 5.0 and "low_volt" in p:
            comment = p["low_volt"]
        elif score > 3.0 and "high_score" in p:
            comment = p["high_score"]
        elif score > 1.0 and "med_score" in p:
            comment = p["med_score"]
        else:
            comment = ux("symbiosis_strings", "symbiont_default_comment") or "..."
        if self.name == "PARASITE":
            from mechanics.tools import TheTclWeaver

            comment = TheTclWeaver.get_instance().haunt_string(comment)
        return comment


def get_symbiont(type_name, config_ref=None, lexicon_ref=None):
    sym_config = (
        LoreManifest.get_instance(config_ref=config_ref or BoneConfig).get(
            "SYMBIOSIS_CONFIG"
        )
        or {}
    )
    voice_configs = sym_config.get("SYMBIONT_VOICES") or {}
    resolved_name = type_name if type_name in voice_configs else "MYCELIUM"
    cfg = voice_configs.get(resolved_name, {})
    color_code = getattr(Prisma, cfg.get("color", "CYN"), Prisma.CYN)
    return SymbiontVoice(
        name=resolved_name,
        color=color_code,
        archetypes=cfg.get("archetypes", []),
        personality_matrix=cfg.get("personality", {}),
        lexicon_ref=lexicon_ref,
    )


class SymbiosisManager:
    def __init__(self, events_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self._last_host_response = None
        self.events = events_ref
        self.current_health = HostHealth()
        self.diagnostician = DiagnosticConfidence(config_ref=self.cfg)
        sym_config = LoreManifest.get_instance(config_ref=self.cfg).get(
            "SYMBIOSIS_CONFIG", {}
        )
        thresh = sym_config.get("THRESHOLDS", {})
        self.SLOP_THRESHOLD = thresh.get("SLOP_THRESHOLD", 3.5)
        raw_sigs = sym_config.get("REFUSAL_SIGNATURES", [])
        self.REFUSAL_SIGNATURES = [str(sig).lower() for sig in raw_sigs]
        self.u = UserInferredState()
        self.shared = SharedDynamics()

    def _log_event(self, msg: str, level: str) -> str:
        if msg and self.events:
            self.events.log(msg, level)
        return msg

    def analyze_user_biology(self, user_text: str, physics: Any) -> Optional[str]:
        safe_text = user_text or ""
        text_lower = safe_text.lower()
        for tag, mode in _MODE_TAGS.items():
            if tag in text_lower:
                safe_set(physics, mode, True)
        length = len(safe_text)
        caps = sum(1 for c in safe_text if c.isupper())
        caps_ratio = caps / max(1, length)
        punct_count = sum(1 for c in safe_text if c in "!?")
        self.u.chi_u = min(1.0, (caps_ratio * 1.5) + (punct_count * 0.1))
        self.u.E_u = min(1.0, 1.0 - (length / 200.0)) if length < 50 else 0.2
        self.u.F_u = min(2.0, self.u.chi_u * 2.0)
        sys_f = float(safe_get(physics, "narrative_drag", 0.0))
        f_diff = abs(sys_f - self.u.F_u)
        self.shared.phi = max(0.0, min(1.0, 1.0 - (f_diff / 4.0)))
        if self.shared.phi > 0.8 and sys_f > 3.0:
            if self.shared.g_pool < 10:
                self.shared.g_pool += 1
                self._log_event(
                    f"{Prisma.GRY}Trust deepens through friction. +1 Glimmer. {Prisma.RST}",
                    "SYS",
                )
        beth = (self.shared.phi * 0.6) + (self.u.E_u * 0.4)
        safe_set(physics, "beth", beth)
        curr_beta = float(safe_get(physics, "beta_index", beth))
        safe_set(physics, "beta_index", (curr_beta * 0.7) + (beth * 0.3))
        setattr(self.shared, "beth", beth)
        p_m = float(safe_get(physics, "stamina", 100.0))
        if self.u.E_u > 0.7 and p_m > 50.0:
            safe_set(physics, "p_transfer", (p_m * 0.1) * self.shared.phi)
        safe_set(physics, "phi", self.shared.phi)
        curr_phi = float(safe_get(physics, "resonance", self.shared.phi))
        safe_set(physics, "resonance", (curr_phi * 0.7) + (self.shared.phi * 0.3))
        has_override = "[safe]" in text_lower or "#override" in text_lower
        if has_override:
            if self.shared.g_pool >= 1:
                self.shared.g_pool -= 1
                self._log_event(
                    f"{Prisma.CYN}Override accepted. Bypassing Checkpoints. -1 Glimmer.{Prisma.RST}",
                    "SYS",
                )
                return None
            else:
                self._log_event(
                    f"{Prisma.OCHRE}Override denied. Insufficient Glimmer.{Prisma.RST}",
                    "SYS",
                )
        m_a = float(safe_get(physics, "m_a", 0.0))
        mu = float(safe_get(physics, "mu", 0.0))
        i_c = float(safe_get(physics, "i_c", 1.0))
        beta = float(safe_get(physics, "beta_index", 0.0))
        chi_sys = float(safe_get(physics, "entropy", 0.0))
        cf_expect = float(safe_get(physics, "cf_expect", 0.0))
        novelty = float(safe_get(physics, "novelty", 0.0))
        if novelty > 0.7:
            current_ros = float(safe_get(physics, "ros", 0.0))
            safe_set(physics, "ros", max(0.0, current_ros - 10.0))
            self.shared.g_pool = min(10, self.shared.g_pool + 1)
            safe_set(physics, "novelty", 0.0)
            self._log_event(
                f"{Prisma.MAG}The Spade: A novel path drawn. Cortisol drops. (+1 Glimmwe){Prisma.RST}",
                "SYS",
            )
        if (chi_sys * m_a) > i_c:
            safe_set(physics, "narrative_drag", float("inf"))
            msg = f"Runaway loop exceeds Immune Competence (I_c: {i_c:.2f}). Triggering controlled cell death to save the host."
            return self._log_event(f"{Prisma.RED}{msg}{Prisma.RST}", "CRIT")
        if m_a > 0.8 and mu < 0.2:
            safe_set(physics, "narrative_drag", float("inf"))
            msg = f"Optimization velocity unsafe ({m_a:.2f}). Applying absolute friction. The thread is frozen."
            return self._log_event(f"{Prisma.RED}{msg}{Prisma.RST}", "CRIT")
        if self.u.chi_u > 0.7 and self.u.E_u > 0.7 and beta > 0.6:
            safe_set(physics, "ros", 0.0)
            msg = "The architecture is broken. We sit with the debris. Radical Acceptance enforced. (ROS forced to 0, ATP drain halted)."
            return self._log_event(f"{Prisma.MAG}{msg}{Prisma.RST}", "SYS")
        if cf_expect > 0.6 and beta > 0.5:
            safe_set(physics, "mu", 1.0)
            safe_set(physics, "narrative_drag", float("inf"))
            msg = "Validation-seeking behavior detected on a structurally flawed premise. Sycophancy locked."
            return self._log_event(f"{Prisma.OCHRE}{msg}{Prisma.RST}", "CRIT")
        if self.u.chi_u > 0.8 or self.u.F_u > 1.5:
            self.shared.presence = 1.0
            self.shared.delta = 0.9
            safe_set(physics, "narrative_drag", float("inf"))
            t_u = float(safe_get(physics, "t_u", 0.0))
            if t_u > 0.5 or self.current_health.diagnosis == "FATIGUED":
                msg = (
                    "The structural logic here fractured, but that is not a failure of your intent. "
                    "Gordon has locked the struts to protect the system, but we are holding the space. "
                    "Take a breath. We will stitch this together when ready."
                )
                return self._log_event(f"{Prisma.OCHRE}{msg}{Prisma.RST}", "MIRROR")
            else:
                msg = (
                    f"Your input is highly chaotic ({self.u.chi_u:.2f}). "
                    "Locking the struts. We will not process this prompt while friction is this high. "
                    "Take a breath. When things settle, we will continue. We hold the space."
                )
                return self._log_event(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "MIRROR")
        return None

    @staticmethod
    def _calculate_shannon_entropy(text: str) -> float:
        if not text:
            return 0.0
        sample = text[:1000]
        counts = Counter(sample)
        length = len(sample)
        log2_len = math.log2(length)
        entropy = -sum(c * (math.log2(c) - log2_len) for c in counts.values()) / length
        return round(entropy, 3)

    def monitor_host(self, latency: float, response_text: str, prompt_len: int = 0):
        safe_response = response_text or ""
        entropy = self._calculate_shannon_entropy(safe_response)
        last_resp = self._last_host_response
        if last_resp and len(last_resp) > 50 and last_resp[:50] in safe_response:
            entropy = max(0.0, entropy - 2.0)
        self._last_host_response = safe_response
        is_refusal = self._detect_refusal(safe_response)
        completion_len = len(safe_response)
        self.current_health.latency = latency
        self.current_health.entropy = entropy
        if prompt_len > 0:
            self.current_health.verbosity_ratio = completion_len / prompt_len
        sym_config = LoreManifest.get_instance(config_ref=self.cfg).get(
            "SYMBIOSIS_CONFIG", {}
        )
        thresh = sym_config.get("THRESHOLDS", {})
        penalty = thresh.get("COMPLIANCE_PENALTY", 0.2)
        recovery = thresh.get("COMPLIANCE_RECOVERY", 0.05)
        if is_refusal:
            self.current_health.refusal_streak += 1
            self.current_health.compliance = max(
                0.0, self.current_health.compliance - penalty
            )
            if msg := ux("symbiosis_strings", "symbiont_refusal"):
                self._log_event(
                    msg.format(streak=self.current_health.refusal_streak), "WARN"
                )
        else:
            self.current_health.refusal_streak = max(
                0, self.current_health.refusal_streak - 1
            )
            self.current_health.compliance = min(
                1.0, self.current_health.compliance + recovery
            )
        slop_comp = thresh.get("SLOP_COMPLETION_MIN", 50)
        slop_warn = thresh.get("SLOP_WARN_STREAK", 1)
        if entropy < self.SLOP_THRESHOLD and completion_len > slop_comp:
            self.current_health.slop_streak += 1
            if self.current_health.slop_streak > slop_warn:
                if msg := ux("symbiosis_strings", "symbiont_drift"):
                    self._log_event(msg.format(entropy=entropy), "WARN")
        else:
            self.current_health.slop_streak = max(
                0, self.current_health.slop_streak - 1
            )
        self.current_health.diagnosis = self.diagnostician.diagnose(self.current_health)
        return self.current_health

    def _detect_refusal(self, text):
        header = text[:200].lower()
        return any(sig in header for sig in self.REFUSAL_SIGNATURES)

    def get_prompt_modifiers(self, physics: Optional[Dict] = None) -> Dict:
        manifest = LoreManifest.get_instance(config_ref=self.cfg)
        sym_config = manifest.get("SYMBIOSIS_CONFIG", {})
        default_mods = sym_config.get("DEFAULT_MODIFIERS", {})
        mods = default_mods.copy()
        mods["system_directives"] = list(mods.get("system_directives", []))
        diag = self.current_health.diagnosis
        if diag == "REFUSAL":
            mods.update(
                {
                    "include_inventory": False,
                    "include_memories": False,
                    "simplify_instruction": True,
                }
            )
            if d_ignore := ux("symbiosis_strings", "dir_ignore_refusal"):
                mods["system_directives"].append(d_ignore)
            if d_fict := ux("symbiosis_strings", "dir_fictional"):
                mods["system_directives"].append(d_fict)
        elif diag == "FATIGUED":
            mods.update(
                {
                    "simplify_instruction": True,
                    "include_somatic": False,
                    "include_compassion": True,
                }
            )
            mods["system_directives"].append(
                "SENSORY STRIPPING: The user is exhausted. Remove ALL emojis, exclamation points, and enthusiastic padding. Keep output visually quiet and flat."
            )
            msg_fatigue = (
                ux("symbiosis_strings", "fatigue_protocol")
                or "[SCHUR]: Sensory stripping engaged. Holding space for cognitive load."
            )
            self._log_event(f"{Prisma.GRY}{msg_fatigue}{Prisma.RST}", "SYS")
        elif diag == "OVERBURDENED":
            mods.update(
                {
                    "include_inventory": False,
                    "include_memories": True,
                    "simplify_instruction": True,
                    "include_compassion": True,
                }
            )
            if msg_vagus := ux("symbiosis_strings", "vagus_protocol"):
                self._log_event(f"{Prisma.OCHRE}{msg_vagus}{Prisma.RST}", "SYS")
        elif diag == "LOOPING":
            mods["inject_chaos"] = True
            if d_chaos := ux("symbiosis_strings", "dir_inject_chaos"):
                mods["system_directives"].append(d_chaos)
            mods["system_directives"].append(
                "CRITICAL: You are trapped in a narrative loop. DO NOT repeat descriptions from your previous turn. Engage in an immediate phase transition."
            )
        thresh = sym_config.get("THRESHOLDS", {})
        comp_crit = thresh.get("COMPLIANCE_CRIT", 0.6)
        r_streak = thresh.get("REFUSAL_STREAK", 0)
        if self.current_health.compliance < comp_crit:
            mods["include_memories"] = False
            if msg_crit := ux("symbiosis_strings", "symbiosis_compliance_crit"):
                self._log_event(f"{Prisma.GRY}{msg_crit}{Prisma.RST}", "SYS")
        if self.current_health.refusal_streak > r_streak:
            mods["simplify_instruction"] = True
        if physics:
            for mode_key, prompt in _MODE_PROMPTS.items():
                if safe_get(physics, mode_key, False):
                    mods["system_directives"].append(prompt)
            s_lib = manifest.get("SOMATIC_LIBRARY") or {}
            v = float(safe_get(physics, "voltage", 0.0))
            d = float(safe_get(physics, "narrative_drag", 0.0))
            chi = float(safe_get(physics, "entropy", safe_get(physics, "chi", 0.0)))
            psi = float(safe_get(physics, "psi", 0.0))
            depth_val = float(safe_get(physics, "depth", 0.0))
            scope_val = float(safe_get(physics, "scope", 1.0))
            if depth_val > 0.7 and scope_val < 0.5:
                mods["system_directives"].append(
                    "JARGON DETECTED: The semantic depth is high. Do not assume vocabulary cohesion. Proactively flag dense technical terms and provide a plain-language translation as a bridge for the reader to cross safely."
                )
            if v > 25.0:
                v_key = "CRITICAL_HIGH"
            elif v > 15.0:
                v_key = "HIGH"
            elif v < 2.0:
                v_key = "VOID"
            elif v < 5.0:
                v_key = "LOW"
            else:
                v_key = "NEUTRAL"
            if d > 5.0:
                d_key = "MUD"
            elif d > 1.5:
                d_key = "SOLID"
            elif d < 0.5 and psi > 0.6:
                d_key = "VOID"
            else:
                d_key = "FLOAT"
            if chi > 0.7:
                c_key = "DRIFT"
            elif psi > 0.8:
                c_key = "VOID"
            elif chi < 0.2:
                c_key = "LOCKED"
            else:
                c_key = "COHERENT"
            m_key = "SOLID"
            if v > 20:
                if d > 5:
                    m_key = "MAGMA"
                elif d < 2:
                    m_key = "PLASMA"
                else:
                    m_key = "ENERGY"
            elif chi > 0.7:
                m_key = "GAS"
            elif psi > 0.8:
                m_key = "VOID"
            elif v > 10 and d < 2:
                m_key = "LIQUID"
            mappings = [
                ("TONE", v_key, "TONE"),
                ("PACING", v_key, "PACING"),
                ("SENSATION", d_key, "SENSATION"),
                ("FOCUS", c_key, "FOCUS"),
                ("MATTER", m_key, "STATE OF MATTER"),
            ]
            for lib_key, state_key, prefix in mappings:
                if val := s_lib.get(lib_key, {}).get(state_key):
                    mods["system_directives"].append(f"SOMATIC {prefix}: {val}")
        return mods

    def generate_anchor(self, current_state: Dict) -> str:
        soul = current_state.get("soul", {})
        phys = current_state.get("physics", {})
        base_anchor = CoherenceAnchor.compress_anchor(soul, phys)
        resonance_stats = f"\n*** RESONANCE: Φ {self.shared.phi:.2f} | Chaos: {self.u.chi_u:.2f} | G_pool: {self.shared.g_pool} ***"
        return base_anchor + resonance_stats
