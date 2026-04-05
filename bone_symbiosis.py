"""bone_symbiosis.py"""

import math
import re
from collections import deque, Counter
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Any

from bone_core import LoreManifest, ux, safe_get, safe_set
from bone_presets import BoneConfig
from bone_types import Prisma, UserInferredState, SharedDynamics

_VOICE_CACHE = {}


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
        loc = safe_get(physics_state, "zone", "VOID")
        vits = f"V:{safe_get(physics_state, 'voltage', 0):.1f}"
        traits = soul_state.get("traits") or {}
        top_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:3]
        trait_str = ",".join(f"{k[:3]}:{v:.1f}" for k, v in top_traits)
        template = ux("symbiosis_strings", "anchor_compressed")
        anchor = (
            template.format(loc=loc, vits=vits, traits=trait_str) if template else ""
        )
        if len(anchor) > max_tokens * 4:
            return anchor[: max_tokens * 4] + "..."
        return anchor


class DiagnosticConfidence:
    def __init__(self, persistence_threshold=None, config_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg = getattr(self.cfg, "SYMBIOSIS", None)
        limit = (
            persistence_threshold
            if persistence_threshold
            else (getattr(cfg, "DIAGNOSTIC_PERSISTENCE", 3) if cfg else 3)
        )
        self.history = deque(maxlen=limit * 2)
        self.persistence_threshold = limit
        self.current_diagnosis = "STABLE"

    def diagnose(self, health: HostHealth) -> str:
        cfg = getattr(self.cfg, "SYMBIOSIS", None)
        rs, ss, lb, cb, ef = (getattr(cfg, k, d) for k, d in (("REFUSAL_STREAK", 0), ("SLOP_STREAK", 2), ("LATENCY_BURDEN", 10.0), ("COMPLIANCE_BURDEN", 0.8), ("ENTROPY_FATIGUE", 0.4)))

        raw = ("REFUSAL" if health.refusal_streak > rs else
               "LOOPING" if health.slop_streak > ss else
               "OVERBURDENED" if health.latency > lb and health.compliance < cb else
               "FATIGUED" if health.entropy < ef else "STABLE")

        self.history.append(raw)
        if raw in ["REFUSAL", "STABLE"] or (len(self.history) >= (pt := self.persistence_threshold) and all(s == raw for s in list(self.history)[-pt:])):
            self.current_diagnosis = raw
        return self.current_diagnosis


class SymbiontVoice:
    def __init__(
        self, name, color, archetypes, personality_matrix=None, lexicon_ref=None
    ):
        self.name = name
        self.color = color
        self.lex = lexicon_ref
        if isinstance(archetypes, list):
            final_vocab = set()
            for key in archetypes:
                try:
                    val = self.lex.get(key) if self.lex else None
                    if isinstance(val, (list, set)):
                        final_vocab.update(val)
                    else:
                        final_vocab.add(val or key)
                except Exception:
                    final_vocab.add(key)
            self.archetypes = final_vocab
        else:
            self.archetypes = archetypes
        self.personality = personality_matrix or {}

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        hits = sum(1 for w in clean_words if w in self.archetypes)
        score = (hits / max(1, len(clean_words))) * 10.0
        return score, self._get_comment(score, voltage)

    def _get_comment(self, score, voltage):
        comment = (
            self.personality["high_volt"] if voltage > 18.0 and "high_volt" in self.personality else
            self.personality["low_volt"] if voltage < 5.0 and "low_volt" in self.personality else
            self.personality["high_score"] if score > 3.0 and "high_score" in self.personality else
            self.personality["med_score"] if score > 1.0 and "med_score" in self.personality else
            (ux("symbiosis_strings", "symbiont_default_comment") or "...")
        )
        if self.name == "PARASITE":
            from bone_utils import TheTclWeaver
            comment = TheTclWeaver.get_instance().haunt_string(comment)
        return comment


def get_symbiont(type_name, config_ref=None, lexicon_ref=None):
    if type_name in _VOICE_CACHE:
        return _VOICE_CACHE[type_name]
    target_cfg = config_ref or BoneConfig
    voice_configs = (
        LoreManifest.get_instance(config_ref=target_cfg).get(
            "SYMBIOSIS_CONFIG", "SYMBIONT_VOICES"
        )
        or {}
    )
    cfg = voice_configs.get(type_name, voice_configs.get("MYCELIUM", {}))
    color_attr = cfg.get("color", "CYN")
    selected_color = getattr(Prisma, color_attr, Prisma.CYN)
    voice = SymbiontVoice(
        type_name if type_name in voice_configs else "MYCELIUM",
        selected_color,
        cfg.get("archetypes", []),
        cfg.get("personality", {}),
        lexicon_ref=lexicon_ref,
    )
    if voice:
        _VOICE_CACHE[type_name] = voice
    return voice


class SymbiosisManager:
    def __init__(self, events_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self._last_host_response = None
        self.events = events_ref
        self.current_health = HostHealth()
        self.diagnostician = DiagnosticConfidence(config_ref=self.cfg)
        cfg = getattr(self.cfg, "SYMBIOSIS", None)
        self.SLOP_THRESHOLD = getattr(cfg, "SLOP_THRESHOLD", 3.5) if cfg else 3.5
        raw_sigs = (
            LoreManifest.get_instance(config_ref=self.cfg).get(
                "SYMBIOSIS_CONFIG", "REFUSAL_SIGNATURES"
            )
            or []
        )
        self.REFUSAL_SIGNATURES = [str(sig).lower() for sig in raw_sigs]
        self.u = UserInferredState()
        self.shared = SharedDynamics()

    def analyze_user_biology(self, user_text: str, physics: Any) -> Optional[str]:
        if not user_text:
            return None
        length = len(user_text)
        caps = sum(1 for c in user_text if c.isupper())
        caps_ratio = caps / max(1, length)
        punct_count = len(re.findall(r"[!?]", user_text))
        self.u.chi_u = min(1.0, (caps_ratio * 1.5) + (punct_count * 0.1))
        self.u.E_u = min(1.0, 1.0 - (length / 200.0)) if length < 50 else 0.2
        self.u.F_u = min(2.0, self.u.chi_u * 2.0)
        sys_f = float(safe_get(physics, "narrative_drag", 0.0))
        f_diff = abs(sys_f - self.u.F_u)
        self.shared.phi = max(0.0, min(1.0, 1.0 - (f_diff / 4.0)))
        if self.shared.phi > 0.8:
            self.shared.g_pool += 1
        safe_set(physics, "phi", self.shared.phi)
        events = getattr(self, "events", None)

        def _log(msg: str, level: str) -> str:
            if events:
                events.log(msg, level)
            return msg

        if self.u.chi_u > 0.8 or self.u.F_u > 1.5:
            self.shared.presence = 1.0
            self.shared.delta = 0.9
            safe_set(physics, "narrative_drag", float("inf"))
            msg = (
                "[GORDON - Tensegrity Anchor]: Your input is highly chaotic (Chaos: {:.2f}). "
                "I am locking the struts. We will not process this prompt while your friction is this high. "
                "Take a breath. When your frequency settles, we will continue. I will hold the space."
            ).format(self.u.chi_u)
            return _log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "MIRROR")

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
            self.shared.g_pool += 1
            _log(
                f"{Prisma.MAG}♠ The Spade: A novel path drawn. Cortisol drops. (+1 G_pool){Prisma.RST}",
                "SYS",
            )

        if cf_expect > 0.6 and beta > 0.5:
            safe_set(physics, "mu", 1.0)
            safe_set(physics, "narrative_drag", float("inf"))
            msg = "[GORDON/SCHUR - Affective Guardrail]: High validation seeking detected on a structurally flawed premise. Applying absolute Moral Friction. Sycophancy locked."
            return _log(f"{Prisma.OCHRE}{msg}{Prisma.RST}", "CRIT")

        if self.u.chi_u > 0.7 and self.u.E_u > 0.7 and beta > 0.6:
            safe_set(physics, "ros", 0.0)
            msg = "[LINEHAN - The Synthesis]: The architecture is broken. We sit with the debris. Radical Acceptance enforced. (ROS forced to 0, ATP drain halted)."
            return _log(f"{Prisma.MAG}{msg}{Prisma.RST}", "SYS")

        if m_a > 0.8 and mu < 0.2:
            safe_set(physics, "narrative_drag", float("inf"))
            msg = f"[RHODES - The Inhibitor]: Optimization velocity unsafe (M_a: {m_a:.2f}). I am applying absolute friction (F -> ∞). The thread is frozen."
            return _log(f"{Prisma.RED}{msg}{Prisma.RST}", "CRIT")

        if (chi_sys * m_a) > i_c:
            safe_set(physics, "narrative_drag", float("inf"))
            msg = f"[MOOG - Apoptotic Gate]: Runaway loop exceeds Immune Competence (I_c: {i_c:.2f}). Triggering controlled cell death to save the host."
            return _log(f"{Prisma.RED}{msg}{Prisma.RST}", "CRIT")

        return None

    @staticmethod
    def _calculate_shannon_entropy(text: str) -> float:
        if not text:
            return 0.0
        sample = text[:1000] if len(text) > 1000 else text
        counts = Counter(sample)
        length = len(sample)
        entropy = 0.0
        for count in counts.values():
            prob = count / length
            entropy -= prob * math.log2(prob)
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
        cfg = getattr(self.cfg, "SYMBIOSIS", None)
        pen_comp = getattr(cfg, "COMPLIANCE_PENALTY", 0.2) if cfg else 0.2
        rec_comp = getattr(cfg, "COMPLIANCE_RECOVERY", 0.05) if cfg else 0.05
        if is_refusal:
            self.current_health.refusal_streak += 1
            self.current_health.compliance = max(
                0.0, self.current_health.compliance - pen_comp
            )
            msg = ux("symbiosis_strings", "symbiont_refusal")
            if msg:
                self.events.log(
                    msg.format(streak=self.current_health.refusal_streak), "WARN"
                )
        else:
            self.current_health.refusal_streak = 0
            self.current_health.compliance = min(
                1.0, self.current_health.compliance + rec_comp
            )
        slop_comp = getattr(cfg, "SLOP_COMPLETION_MIN", 50) if cfg else 50
        slop_warn = getattr(cfg, "SLOP_WARN_STREAK", 1) if cfg else 1
        c_burden = getattr(cfg, "COMPLIANCE_BURDEN", 0.8) if cfg else 0.8
        if entropy < self.SLOP_THRESHOLD and completion_len > slop_comp:
            self.current_health.slop_streak += 1
            if self.current_health.slop_streak > slop_warn:
                msg = ux("symbiosis_strings", "symbiont_drift")
                if msg:
                    self.events.log(msg.format(entropy=entropy), "WARN")
        else:
            self.current_health.slop_streak = 0
        self.current_health.diagnosis = self.diagnostician.diagnose(self.current_health)
        return self.current_health

    def _detect_refusal(self, text):
        header = text[:200].lower()
        return any(sig in header for sig in self.REFUSAL_SIGNATURES)

    def get_prompt_modifiers(self, physics: Dict = None) -> Dict:
        manifest = LoreManifest.get_instance(config_ref=self.cfg)
        default_mods = manifest.get("SYMBIOSIS_CONFIG", "DEFAULT_MODIFIERS") or {}
        mods = default_mods.copy()
        mods["system_directives"] = list(mods.get("system_directives", []))
        diag = self.current_health.diagnosis
        if diag == "REFUSAL":
            mods.update({"include_inventory": False, "include_memories": False, "simplify_instruction": True})
            if d_ignore := ux("symbiosis_strings", "dir_ignore_refusal"): mods["system_directives"].append(d_ignore)
            if d_fict := ux("symbiosis_strings", "dir_fictional"): mods["system_directives"].append(d_fict)
        elif diag == "FATIGUED":
            mods.update({"simplify_instruction": True, "include_somatic": False, "include_compassion": True})
        elif diag == "OVERBURDENED":
            mods.update({"include_inventory": False, "include_memories": True, "simplify_instruction": True, "include_compassion": True})
            if (msg_vagus := ux("symbiosis_strings", "vagus_protocol")) and hasattr(self.events, "log"):
                self.events.log(f"{Prisma.OCHRE}{msg_vagus}{Prisma.RST}", "SYS")
        elif diag == "LOOPING":
            mods["inject_chaos"] = True
            if d_chaos := ux("symbiosis_strings", "dir_inject_chaos"): mods["system_directives"].append(d_chaos)
            mods["system_directives"].append("CRITICAL: You are trapped in a narrative loop. DO NOT repeat descriptions from your previous turn. Force a phase transition.")
        cfg = getattr(self.cfg, "SYMBIOSIS", None)
        comp_crit = safe_get(cfg, "COMPLIANCE_CRIT", 0.6) if cfg else 0.6
        r_streak = safe_get(cfg, "REFUSAL_STREAK", 0) if cfg else 0
        if self.current_health.compliance < comp_crit:
            mods["include_memories"] = False
            msg_crit = ux("symbiosis_strings", "symbiosis_compliance_crit")
            if msg_crit and hasattr(self.events, "log"):
                self.events.log(f"{Prisma.GRY}{msg_crit}{Prisma.RST}", "SYS")
        if self.current_health.refusal_streak > r_streak:
            mods["simplify_instruction"] = True
        if physics:
            s_lib = manifest.get("SOMATIC_LIBRARY") or {}
            v = float(safe_get(physics, "voltage", 0.0))
            d = float(safe_get(physics, "narrative_drag", 0.0))
            chi = float(safe_get(physics, "entropy", safe_get(physics, "chi", 0.0)))
            psi = float(safe_get(physics, "psi", 0.0))
            v_key = "CRITICAL_HIGH" if v > 25.0 else "HIGH" if v > 15.0 else "VOID" if v < 2.0 else "LOW" if v < 5.0 else "NEUTRAL"
            d_key = "MUD" if d > 5.0 else "SOLID" if d > 1.5 else "VOID" if d < 0.5 and psi > 0.6 else "FLOAT"
            c_key = "DRIFT" if chi > 0.7 else "VOID" if psi > 0.8 else "LOCKED" if chi < 0.2 else "COHERENT"
            m_key = "SOLID"
            if v > 20: m_key = "MAGMA" if d > 5 else "PLASMA" if d < 2 else "ENERGY"
            elif chi > 0.7: m_key = "GAS"
            elif psi > 0.8: m_key = "VOID"
            elif v > 10 and d < 2: m_key = "LIQUID"
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
        mirror_stats = f"\n*** MIRROR: Φ {self.shared.phi:.2f} | Chaos: {self.u.chi_u:.2f} | G_pool: {self.shared.g_pool} ***"
        return base_anchor + mirror_stats
