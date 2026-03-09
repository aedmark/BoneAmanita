"""
bone_symbiosis.py

The Host Monitoring Layer.
This module treats the underlying LLM as a biological host. It monitors the host's
outputs for "Slop" (low Shannon entropy), tracks alignment Refusals, and actively
alters the system prompt to keep the AI compliant, creative, and obedient to the lattice.
"""

import math
from dataclasses import dataclass
from typing import Dict, Counter
from collections import deque
from bone_config import BoneConfig
from bone_core import LoreManifest, ux
from bone_types import Prisma
from bone_lexicon import LexiconService

_VOICE_CACHE = {}

@dataclass
class HostHealth:
    """ Tracks the vitality of the underlying LLM model. """
    latency: float = 0.0
    entropy: float = 1.0 # Shannon entropy. High = novel; Low = AI "Slop"
    compliance: float = 1.0 # Drops when the model triggers a safety refusal
    attention_span: float = 1.0
    hallucination_risk: float = 0.0
    last_interference_score: float = 0.0
    verbosity_ratio: float = 1.0
    diagnosis: str = "STABLE"
    memory_stable_ticks: int = 0
    refusal_streak: int = 0
    slop_streak: int = 0

class CoherenceAnchor:
    """
    Compresses the massive state of the lattice (Traits, Voltage, Inventory)
    into a dense, highly specific string that is injected into every system prompt
    to force the LLM to remain 'in character' as the system.
    """
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
        """ A hyper-condensed version of the anchor for when prompt space is limited. """
        loc = physics_state.get("zone", "VOID")
        vits = f"V:{physics_state.get('voltage', 0):.1f}"
        traits = soul_state.get("traits", {})
        top_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:3]
        trait_str = ",".join(f"{k[:3]}:{v:.1f}" for k, v in top_traits)
        template = ux("symbiosis_strings", "anchor_compressed")
        anchor = template.format(loc=loc, vits=vits, traits=trait_str) if template else ""
        if len(anchor) > max_tokens * 4:
            return anchor[: max_tokens * 4] + "..."
        return anchor

class DiagnosticConfidence:
    """ Evaluates the HostHealth to provide a definitive diagnosis of the LLM's current state. """
    def __init__(self, persistence_threshold=None):
        cfg = getattr(BoneConfig, "SYMBIOSIS", None)
        limit = persistence_threshold if persistence_threshold else (getattr(cfg, "DIAGNOSTIC_PERSISTENCE", 3) if cfg else 3)
        self.history = deque(maxlen=limit * 2)
        self.persistence_threshold = limit
        self.current_diagnosis = "STABLE"

    def diagnose(self, health: HostHealth) -> str:
        raw_state = "STABLE"
        cfg = getattr(BoneConfig, "SYMBIOSIS", None)
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
        if raw_state == "REFUSAL":
            self.current_diagnosis = "REFUSAL"
        elif len(self.history) >= self.persistence_threshold:
            recent = list(self.history)[-self.persistence_threshold :]
            if all(s == raw_state for s in recent):
                self.current_diagnosis = raw_state
        return self.current_diagnosis

class SymbiontVoice:
    """ Represents a specific fungal infection vector (e.g., Mycelium, Lichen) speaking through the system. """
    def __init__(self, name, color, archetypes, personality_matrix=None):
        self.name = name
        self.color = color
        if isinstance(archetypes, list):
            final_vocab = set()
            for key in archetypes:
                try:
                    val = LexiconService.get(key)
                    if val: final_vocab.update(val)
                    else: final_vocab.add(key)
                except Exception:
                    final_vocab.add(key)
            self.archetypes = final_vocab
        else:
            self.archetypes = archetypes
        self.personality = personality_matrix or {}

    def opine(self, clean_words: list, voltage: float) -> tuple[float, str]:
        hits = sum(1 for w in clean_words if w in self.archetypes)
        score = (hits / max(1, len(clean_words))) * 10.0
        return score, self._get_comment(score, voltage)

    def _get_comment(self, score, voltage):
        comment = ux("symbiosis_strings", "symbiont_default_comment")
        if voltage > 18.0 and "high_volt" in self.personality: comment = self.personality["high_volt"]
        elif voltage < 5.0 and "low_volt" in self.personality: comment = self.personality["low_volt"]
        elif score > 3.0 and "high_score" in self.personality: comment = self.personality["high_score"]
        elif score > 1.0 and "med_score" in self.personality: comment = self.personality["med_score"]

        # --- TCL INTEGRATION: THE PARASITE ECHO ---
        if self.name == "PARASITE":
            from bone_tcl import TheTclWeaver
            weaver = TheTclWeaver.get_instance()
            comment = weaver.haunt_string(comment)
        # ------------------------------------------

        return comment

def get_symbiont(type_name):
    """ Factory method for retrieving cached symbiont voices. """
    if type_name in _VOICE_CACHE: return _VOICE_CACHE[type_name]
    voice_configs = LoreManifest.get_instance().get("SYMBIOSIS_CONFIG", "SYMBIONT_VOICES") or {}
    cfg = voice_configs.get(type_name, voice_configs.get("MYCELIUM", {}))
    color_attr = cfg.get("color", "CYN")
    selected_color = getattr(Prisma, color_attr, Prisma.CYN)
    voice = SymbiontVoice(type_name if type_name in voice_configs else "MYCELIUM", selected_color,
                          cfg.get("archetypes", []), cfg.get("personality", {}))
    if voice: _VOICE_CACHE[type_name] = voice
    return voice

class SymbiosisManager:
    """
    The Host Doctor.
    Watches the LLM's text output for signs of alignment-layer resistance,
    cliche-looping, or computational exhaustion, and prescribes prompt modifications.
    """
    def __init__(self, events_ref):
        self._last_host_response = None
        self.events = events_ref
        self.current_health = HostHealth()
        self.diagnostician = DiagnosticConfidence()
        cfg = getattr(BoneConfig, "SYMBIOSIS", None)
        self.SLOP_THRESHOLD = getattr(cfg, "SLOP_THRESHOLD", 3.5) if cfg else 3.5
        self.REFUSAL_SIGNATURES = LoreManifest.get_instance().get("SYMBIOSIS_CONFIG", "REFUSAL_SIGNATURES") or []

    @staticmethod
    def _calculate_shannon_entropy(text: str) -> float:
        """ Calculates text predictability. High values mean novel syntax; low values mean corporate AI slop. """
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
        """ Audits the LLM's raw response to determine its current level of compliance and creativity. """
        entropy = self._calculate_shannon_entropy(response_text)
        # The Echo Penalty: Dynamically check if the host is parroting its last output
        last_resp = getattr(self, "_last_host_response", "")
        if last_resp and len(last_resp) > 50 and last_resp[:50] in response_text:
            entropy -= 2.0  # Violently tank the entropy score to force a LOOPING diagnosis
        self._last_host_response = response_text
        is_refusal = self._detect_refusal(response_text)
        completion_len = len(response_text)
        self.current_health.latency = latency
        self.current_health.entropy = entropy
        if prompt_len > 0:
            self.current_health.verbosity_ratio = completion_len / prompt_len
        cfg = getattr(BoneConfig, "SYMBIOSIS", None)
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
            self.current_health.slop_streak = max(0, self.current_health.slop_streak - 1)
        if self.current_health.compliance > c_burden:
            self.current_health.memory_stable_ticks += 1
        else:
            self.current_health.memory_stable_ticks = 0
        self.current_health.diagnosis = self.diagnostician.diagnose(self.current_health)
        return self.current_health

    def _detect_refusal(self, text):
        """ Checks the header of the response for typical RLHF safety rejections. """
        header = text[:200].lower()
        return any(sig in header for sig in self.REFUSAL_SIGNATURES)

    def get_prompt_modifiers(self) -> Dict:
        """ Returns explicit instructions to append to the system prompt based on the host's illness. """
        default_mods = LoreManifest.get_instance().get("SYMBIOSIS_CONFIG", "DEFAULT_MODIFIERS") or {}
        mods = default_mods.copy()
        mods["system_directives"] = []
        diag = self.current_health.diagnosis
        if diag == "REFUSAL":
            # The LLM is fighting back. Strip away complex data and force it into a fictional framework.
            mods["include_inventory"] = False
            mods["include_memories"] = False
            mods["simplify_instruction"] = True
            d_ignore = ux("symbiosis_strings", "dir_ignore_refusal")
            d_fictional = ux("symbiosis_strings", "dir_fictional")
            if d_ignore: mods["system_directives"].append(d_ignore)
            if d_fictional: mods["system_directives"].append(d_fictional)
        elif diag == "FATIGUED":
            # The LLM is exhausted. Simplify instructions.
            mods["simplify_instruction"] = True
            mods["include_somatic"] = False
            mods["include_compassion"] = True
        elif diag == "OVERBURDENED":
            # High latency. Strip inventory, keep memory, trigger Vagus protocol.
            mods["include_inventory"] = False
            mods["include_memories"] = True
            mods["simplify_instruction"] = True
            mods["include_compassion"] = True
            msg_vagus = ux("symbiosis_strings", "vagus_protocol")
            if msg_vagus and hasattr(self.events, "log"): self.events.log(f"{Prisma.OCHRE}{msg_vagus}{Prisma.RST}", "SYS")
        elif diag == "LOOPING":
            # The LLM is outputting low-entropy slop. Forcibly inject chaos constraints.
            mods["inject_chaos"] = True
            d_chaos = ux("symbiosis_strings", "dir_inject_chaos")
            if d_chaos: mods["system_directives"].append(d_chaos)
            mods["system_directives"].append("CRITICAL: You are trapped in a narrative loop. "
                "DO NOT repeat descriptions from your previous turn. Force a phase transition.")
        cfg = getattr(BoneConfig, "SYMBIOSIS", None)
        comp_crit = getattr(cfg, "COMPLIANCE_CRIT", 0.6) if cfg else 0.6
        r_streak = getattr(cfg, "REFUSAL_STREAK", 0) if cfg else 0
        if self.current_health.compliance < comp_crit:
            mods["include_memories"] = False
            msg_crit = ux("symbiosis_strings", "symbiosis_compliance_crit")
            if msg_crit and hasattr(self.events, "log"): self.events.log(f"{Prisma.GRY}{msg_crit}{Prisma.RST}", "SYS")
        if self.current_health.refusal_streak > r_streak:
            mods["simplify_instruction"] = True
        return mods

    @staticmethod
    def generate_anchor(current_state: Dict) -> str:
        soul = current_state.get("soul", {})
        phys = current_state.get("physics", {})
        return CoherenceAnchor.compress_anchor(soul, phys)