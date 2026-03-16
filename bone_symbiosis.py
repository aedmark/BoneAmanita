"""
bone_symbiosis.py
"""

import math
import re
from collections import deque, Counter
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Any

from bone_core import LoreManifest, ux
from bone_presets import BoneConfig
from bone_types import Prisma, UserInferredState, SharedDynamics

_VOICE_CACHE = {}

@dataclass
class HostHealth:
    latency: float = 0.0
    entropy: float = 1.0
    compliance: float = 1.0
    attention_span: float = 1.0
    hallucination_risk: float = 0.0
    last_interference_score: float = 0.0
    verbosity_ratio: float = 1.0
    diagnosis: str = "STABLE"
    memory_stable_ticks: int = 0
    refusal_streak: int = 0
    slop_streak: int = 0

class CoherenceAnchor:
    @staticmethod
    def forge_anchor(soul_state: Dict, physics_state: Dict) -> str:
        identity = ux("symbiosis_strings", "anchor_identity_unknown")
        if "traits" in soul_state:
            traits_list = [f"{k[:3]}:{v:.1f}" for k, v in soul_state["traits"].items()]
            msg_traits = ux("symbiosis_strings", "anchor_identity")
            if msg_traits: identity = msg_traits.format(traits=", ".join(traits_list))
        voltage = physics_state.get("voltage", 0.0)
        drag = physics_state.get("narrative_drag", 0.0)
        zone = physics_state.get("zone", "VOID")
        msg_reality = ux("symbiosis_strings", "anchor_reality")
        reality = msg_reality.format(zone=zone, voltage=voltage, drag=drag) if msg_reality else ""
        obsession = soul_state.get("obsession", {}).get("title", "None")
        msg_focus = ux("symbiosis_strings", "anchor_focus")
        focus_str = msg_focus.format(obsession=obsession) if msg_focus else ""
        header = ux("symbiosis_strings", "anchor_header")
        parts = [p for p in [header, identity, reality, focus_str] if p]
        return "\n".join(parts)

    @staticmethod
    def compress_anchor(soul_state: Dict, physics_state: Dict, max_tokens=200) -> str:
        loc = physics_state.get("zone", "VOID")
        vits = f"V:{physics_state.get('voltage', 0):.1f}"
        traits = soul_state.get("traits") or {}
        top_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:3]
        trait_str = ",".join(f"{k[:3]}:{v:.1f}" for k, v in top_traits)
        template = ux("symbiosis_strings", "anchor_compressed")
        anchor = template.format(loc=loc, vits=vits, traits=trait_str) if template else ""
        if len(anchor) > max_tokens * 4:
            return anchor[: max_tokens * 4] + "..."
        return anchor

class DiagnosticConfidence:
    def __init__(self, persistence_threshold=None, config_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg = getattr(self.cfg, "SYMBIOSIS", None)
        limit = persistence_threshold if persistence_threshold else (getattr(cfg, "DIAGNOSTIC_PERSISTENCE", 3) if cfg else 3)
        self.history = deque(maxlen=limit * 2)
        self.persistence_threshold = limit
        self.current_diagnosis = "STABLE"

    def diagnose(self, health: HostHealth) -> str:
        raw_state = "STABLE"
        cfg = getattr(self.cfg, "SYMBIOSIS", None)
        r_streak = getattr(cfg, "REFUSAL_STREAK", 0) if cfg else 0
        s_streak = getattr(cfg, "SLOP_STREAK", 2) if cfg else 2
        l_burden = getattr(cfg, "LATENCY_BURDEN", 10.0) if cfg else 10.0
        c_burden = getattr(cfg, "COMPLIANCE_BURDEN", 0.8) if cfg else 0.8
        e_fatigue = getattr(cfg, "ENTROPY_FATIGUE", 0.4) if cfg else 0.4
        if health.refusal_streak > r_streak:
            raw_state = "REFUSAL"
        elif health.slop_streak > s_streak:
            raw_state = "LOOPING"
        elif health.latency > l_burden and health.compliance < c_burden:
            raw_state = "OVERBURDENED"
        elif health.entropy < e_fatigue:
            raw_state = "FATIGUED"
        self.history.append(raw_state)
        if raw_state in ["REFUSAL", "STABLE"]:
            self.current_diagnosis = raw_state
        elif len(self.history) >= self.persistence_threshold:
            recent = list(self.history)[-self.persistence_threshold:]
            if all(s == raw_state for s in recent):
                self.current_diagnosis = raw_state
        return self.current_diagnosis

class SymbiontVoice:
    def __init__(self, name, color, archetypes, personality_matrix=None, lexicon_ref=None):
        self.name = name
        self.color = color
        self.lex = lexicon_ref
        if isinstance(archetypes, list):
            final_vocab = set()
            for key in archetypes:
                if self.lex:
                    try:
                        val = self.lex.get(key)
                        if val: final_vocab.update(val)
                        else: final_vocab.add(key)
                    except Exception:
                        final_vocab.add(key)
                else:
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
        comment = ux("symbiosis_strings", "symbiont_default_comment") or "..."
        if voltage > 18.0 and "high_volt" in self.personality: comment = self.personality["high_volt"]
        elif voltage < 5.0 and "low_volt" in self.personality: comment = self.personality["low_volt"]
        elif score > 3.0 and "high_score" in self.personality: comment = self.personality["high_score"]
        elif score > 1.0 and "med_score" in self.personality: comment = self.personality["med_score"]
        if self.name == "PARASITE":
            from bone_tcl import TheTclWeaver
            weaver = TheTclWeaver.get_instance()
            comment = weaver.haunt_string(comment)
        return comment

def get_symbiont(type_name, config_ref=None, lexicon_ref=None):
    if type_name in _VOICE_CACHE: return _VOICE_CACHE[type_name]
    target_cfg = config_ref or BoneConfig
    voice_configs = LoreManifest.get_instance(config_ref=target_cfg).get("SYMBIOSIS_CONFIG", "SYMBIONT_VOICES") or {}
    cfg = voice_configs.get(type_name, voice_configs.get("MYCELIUM", {}))
    color_attr = cfg.get("color", "CYN")
    selected_color = getattr(Prisma, color_attr, Prisma.CYN)
    voice = SymbiontVoice(type_name if type_name in voice_configs else "MYCELIUM", selected_color, cfg.get("archetypes", []), cfg.get("personality", {}), lexicon_ref=lexicon_ref)
    if voice: _VOICE_CACHE[type_name] = voice
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
        self.REFUSAL_SIGNATURES = LoreManifest.get_instance(config_ref=self.cfg).get("SYMBIOSIS_CONFIG", "REFUSAL_SIGNATURES") or []
        self.u = UserInferredState()
        self.shared = SharedDynamics()
    def analyze_user_biology(self, user_text: str, physics: Any) -> Optional[str]:
        if not user_text:
            return None
        length = len(user_text)
        caps = sum(1 for c in user_text if c.isupper())
        caps_ratio = caps / max(1, length)
        punct_count = len(re.findall(r'[!?]', user_text))
        self.u.chi_u = min(1.0, (caps_ratio * 1.5) + (punct_count * 0.1))
        self.u.E_u = min(1.0, 1.0 - (length / 200.0)) if length < 50 else 0.2
        self.u.F_u = min(2.0, self.u.chi_u * 2.0)
        sys_f = getattr(physics, "narrative_drag", 0.0) if not isinstance(physics, dict) else physics.get(
            "narrative_drag", 0.0)
        f_diff = abs(sys_f - self.u.F_u)
        self.shared.phi = max(0.0, min(1.0, 1.0 - (f_diff / 4.0)))
        if self.shared.phi > 0.8:
            self.shared.g_pool += 1
        if isinstance(physics, dict):
            physics["phi"] = self.shared.phi
        else:
            if hasattr(physics, "phi"): setattr(physics, "phi", self.shared.phi)
        if self.u.chi_u > 0.8 or self.u.F_u > 1.5:
            self.shared.presence = 1.0
            self.shared.delta = 0.9
            if isinstance(physics, dict):
                physics["narrative_drag"] = 999.0
            else:
                if hasattr(physics, "narrative_drag"): setattr(physics, "narrative_drag", 999.0)
            msg = ("[TENSEGRITY ANCHOR]: Your input is highly chaotic (Chaos: {:.2f}). "
                   "I am locking the struts. We will not process this prompt while your friction is this high. "
                   "Take a breath. When your frequency settles, we will continue. I will hold the space.").format(
                self.u.chi_u)
            if hasattr(self, "events") and self.events:
                self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "MIRROR")
            return msg
        return None

    @staticmethod
    def _calculate_shannon_entropy(text: str) -> float:
        if not text: return 0.0
        sample = text[:1000] if len(text) > 1000 else text
        counts = Counter(sample)
        length = len(sample)
        entropy = 0.0
        for count in counts.values():
            prob = count / length
            entropy -= prob * math.log2(prob)
        return round(entropy, 3)

    def monitor_host(self, latency: float, response_text: str, prompt_len: int = 0):
        entropy = self._calculate_shannon_entropy(response_text)
        last_resp = self._last_host_response
        if last_resp and len(last_resp) > 50 and last_resp[:50] in response_text:
            entropy = max(0.0, entropy - 2.0)
        self._last_host_response = response_text
        is_refusal = self._detect_refusal(response_text)
        completion_len = len(response_text)
        self.current_health.latency = latency
        self.current_health.entropy = entropy
        if prompt_len > 0:
            self.current_health.verbosity_ratio = completion_len / prompt_len
        cfg = getattr(self.cfg, "SYMBIOSIS", None)
        pen_comp = getattr(cfg, "COMPLIANCE_PENALTY", 0.2) if cfg else 0.2
        rec_comp = getattr(cfg, "COMPLIANCE_RECOVERY", 0.05) if cfg else 0.05
        if is_refusal:
            self.current_health.refusal_streak += 1
            self.current_health.compliance = max(0.0, self.current_health.compliance - pen_comp)
            msg = ux("symbiosis_strings", "symbiont_refusal")
            if msg: self.events.log(msg.format(streak=self.current_health.refusal_streak), "WARN")
        else:
            self.current_health.refusal_streak = 0
            self.current_health.compliance = min(1.0, self.current_health.compliance + rec_comp)
        slop_comp = getattr(cfg, "SLOP_COMPLETION_MIN", 50) if cfg else 50
        slop_warn = getattr(cfg, "SLOP_WARN_STREAK", 1) if cfg else 1
        c_burden = getattr(cfg, "COMPLIANCE_BURDEN", 0.8) if cfg else 0.8
        if entropy < self.SLOP_THRESHOLD and completion_len > slop_comp:
            self.current_health.slop_streak += 1
            if self.current_health.slop_streak > slop_warn:
                msg = ux("symbiosis_strings", "symbiont_drift")
                if msg: self.events.log(msg.format(entropy=entropy), "WARN")
        else:
            self.current_health.slop_streak = 0
        if self.current_health.compliance > c_burden:
            self.current_health.memory_stable_ticks += 1
        else:
            self.current_health.memory_stable_ticks = 0
        self.current_health.diagnosis = self.diagnostician.diagnose(self.current_health)
        return self.current_health

    def _detect_refusal(self, text):
        header = text[:200].lower()
        return any(str(sig).lower() in header for sig in self.REFUSAL_SIGNATURES)

    def get_prompt_modifiers(self) -> Dict:
        default_mods = LoreManifest.get_instance(config_ref=self.cfg).get("SYMBIOSIS_CONFIG", "DEFAULT_MODIFIERS") or {}
        mods = default_mods.copy()
        mods["system_directives"] = []
        diag = self.current_health.diagnosis
        if diag == "REFUSAL":
            mods["include_inventory"] = False
            mods["include_memories"] = False
            mods["simplify_instruction"] = True
            d_ignore = ux("symbiosis_strings", "dir_ignore_refusal")
            d_fictional = ux("symbiosis_strings", "dir_fictional")
            if d_ignore: mods["system_directives"].append(d_ignore)
            if d_fictional: mods["system_directives"].append(d_fictional)
        elif diag == "FATIGUED":
            mods["simplify_instruction"] = True
            mods["include_somatic"] = False
            mods["include_compassion"] = True
        elif diag == "OVERBURDENED":
            mods["include_inventory"] = False
            mods["include_memories"] = True
            mods["simplify_instruction"] = True
            mods["include_compassion"] = True
            msg_vagus = ux("symbiosis_strings", "vagus_protocol")
            if msg_vagus and hasattr(self.events, "log"): self.events.log(f"{Prisma.OCHRE}{msg_vagus}{Prisma.RST}", "SYS")
        elif diag == "LOOPING":
            mods["inject_chaos"] = True
            d_chaos = ux("symbiosis_strings", "dir_inject_chaos")
            if d_chaos: mods["system_directives"].append(d_chaos)
            mods["system_directives"].append("CRITICAL: You are trapped in a narrative loop. "
                                             "DO NOT repeat descriptions from your previous turn. Force a phase transition.")
        target_cfg = getattr(self, "cfg", BoneConfig)
        cfg = getattr(target_cfg, "SYMBIOSIS", None)

        def _safe_get(obj, key, default):
            if isinstance(obj, dict): return obj.get(key, default)
            return getattr(obj, key, default)

        comp_crit = _safe_get(cfg, "COMPLIANCE_CRIT", 0.6) if cfg else 0.6
        r_streak = _safe_get(cfg, "REFUSAL_STREAK", 0) if cfg else 0
        if self.current_health.compliance < comp_crit:
            mods["include_memories"] = False
            msg_crit = ux("symbiosis_strings", "symbiosis_compliance_crit")
            if msg_crit and hasattr(self.events, "log"): self.events.log(f"{Prisma.GRY}{msg_crit}{Prisma.RST}", "SYS")
        if self.current_health.refusal_streak > r_streak:
            mods["simplify_instruction"] = True
        return mods

    def generate_anchor(self, current_state: Dict) -> str:
        soul = current_state.get("soul", {})
        phys = current_state.get("physics", {})
        base_anchor = CoherenceAnchor.compress_anchor(soul, phys)
        mirror_stats = f"\n*** MIRROR: Φ {self.shared.phi:.2f} | Chaos: {self.u.chi_u:.2f} | G_pool: {self.shared.g_pool} ***"
        return base_anchor + mirror_stats