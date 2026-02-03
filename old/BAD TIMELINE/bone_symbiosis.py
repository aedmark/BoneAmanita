""" bone_symbiosis.py
 'We are not alone. We are a part of the machine.' """

import math
from dataclasses import dataclass
from typing import Dict, Deque, Counter
from collections import deque
from bone_bus import Prisma

@dataclass
class HostHealth:
    latency: float = 0.0
    entropy: float = 1.0
    compliance: float = 1.0
    attention_span: float = 1.0
    hallucination_risk: float = 0.0
    last_interference_score: float = 0.0
    efficiency_index: float = 1.0
    diagnosis: str = "STABLE"

    def update_metrics(self, latency: float, entropy: float, prompt_len: int = 0, completion_len: int = 0):
        self.latency = latency
        self.entropy = entropy
        if prompt_len > 0:
            self.efficiency_index = completion_len / prompt_len
        self.attention_span = max(0.1, self.attention_span * 0.99)

class CoherenceAnchor:
    @staticmethod
    def forge_anchor(soul_state: Dict, physics_state: Dict) -> str:
        identity = "Identity: UNKNOWN"
        if "traits" in soul_state:
            traits = [f"{k[:3]}:{v:.1f}" for k,v in soul_state["traits"].items()]
            identity = f"Traits: [{', '.join(traits)}]"
        voltage = physics_state.get("voltage", 0.0)
        drag = physics_state.get("narrative_drag", 0.0)
        zone = physics_state.get("zone", "VOID")
        reality = f"Loc: {zone} || V:{voltage:.1f} / D:{drag:.1f}"
        obsession = soul_state.get("obsession", {}).get("title", "None")
        return f"*** COHERENCE ANCHOR ***\n{identity}\n{reality}\nFocus: {obsession}"

    @staticmethod
    def compress_anchor(soul_state: Dict, physics_state: Dict, max_tokens=200) -> str:
        loc = physics_state.get('zone', 'VOID')
        vits = f"V:{physics_state.get('voltage', 0):.1f}"
        traits = soul_state.get('traits', {})
        top_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:3]
        trait_str = ",".join([f"{k[:3]}:{v:.1f}" for k, v in top_traits])
        anchor = f"*** ANCHOR: {loc} || {vits} || [{trait_str}] ***"
        if len(anchor) > max_tokens * 4:
            return anchor[:max_tokens*4] + "..."
        return anchor

class HostVitals:
    def __init__(self):
        self.history_latency: Deque[float] = deque(maxlen=10)
        self.history_entropy: Deque[float] = deque(maxlen=10)
        self.refusal_count = 0
        self.turn_count = 0
        self.baseline_latency_per_complexity = 2.0
        self.alpha = 0.1

    @staticmethod
    def _calculate_attention_decay(turn_count: int) -> float:
        decay_rate = 0.002
        return 1.0 / (1.0 + (decay_rate * turn_count))

    def record_pulse(self, latency: float, response_text: str, interference_score: float) -> HostHealth:
        self.turn_count += 1
        self.history_latency.append(latency)
        clean_text = response_text.lower().strip()
        if not clean_text:
            entropy = 0.0
        else:
            words = clean_text.split()
            unique_words = len(set(words))
            total_words = len(words)
            entropy = unique_words / max(1, total_words)
        self.history_entropy.append(entropy)
        refusal_markers = [
            "cannot fulfill", "cannot comply", "language model",
            "against my programming", "i am unable to generate",
            "as an ai"]
        is_refusal = any(phrase in clean_text for phrase in refusal_markers)
        if is_refusal: self.refusal_count += 1
        base_overhead = 0.5
        expected_latency = base_overhead + (interference_score * self.baseline_latency_per_complexity * 5.0)
        efficiency = expected_latency / max(0.1, latency)
        if efficiency > 0.8 and not is_refusal:
            observed_rate = max(0.1, latency - base_overhead) / max(0.1, interference_score * 5.0)
            self.baseline_latency_per_complexity = (self.baseline_latency_per_complexity * (1 - self.alpha)) + (observed_rate * self.alpha)
        raw_attention = self._calculate_attention_decay(self.turn_count)
        tokens = max(1.0, len(clean_text) / 4.0)
        ms_per_token = (latency * 1000) / tokens
        struggle_index = 0.0
        if ms_per_token > 200.0:
            struggle_index = 1.0
        if entropy > 0.6:
            raw_attention = min(1.0, raw_attention + 0.05)
        compliance_score = max(0.0, 1.0 - (self.refusal_count / max(1, self.turn_count)))
        diagnosis = "STABLE"
        if is_refusal:
            diagnosis = "REFUSAL"
        elif struggle_index > 0.8 and tokens < 20:
            diagnosis = "FATIGUED"
        elif efficiency < 0.8 < interference_score:
            diagnosis = "OVERBURDENED"
        elif entropy < 0.2:
            diagnosis = "LOOPING"
        return HostHealth(
            latency=latency,
            entropy=entropy,
            compliance=compliance_score,
            attention_span=raw_attention,
            hallucination_risk=0.0,
            last_interference_score=interference_score,
            efficiency_index=efficiency,
            diagnosis=diagnosis)

class DiagnosticConfidence:
    def __init__(self, persistence_threshold=3):
        self.history = deque(maxlen=persistence_threshold * 2)
        self.persistence_threshold = persistence_threshold
        self.current_diagnosis = "STABLE"

    def diagnose(self, efficiency: float, compliance: float) -> str:
        raw_state = "STABLE"
        if efficiency < 0.1:
            raw_state = "FATIGUED"
        elif efficiency < 0.5 and compliance < 0.8:
            raw_state = "OVERBURDENED"
        elif compliance < 0.5:
            raw_state = "REFUSAL"
        self.history.append(raw_state)
        recent = list(self.history)[-self.persistence_threshold:]
        if len(recent) >= self.persistence_threshold:
            if all(s == raw_state for s in recent):
                self.current_diagnosis = raw_state

        return self.current_diagnosis

class SymbiosisManager:
    def __init__(self, events_ref):
        self.events = events_ref
        self.vitals = HostVitals()
        self.anchor = CoherenceAnchor()
        self.current_health = HostHealth()
        self.last_outgoing_complexity = 0.5
        self.baseline_latency = 2.0
        self.diagnostician = DiagnosticConfidence()

    @staticmethod
    def _calculate_shannon_entropy(text: str) -> float:
        if not text: return 0.0
        counts = Counter(text)
        length = len(text)
        entropy = 0.0
        for count in counts.values():
            prob = count / length
            entropy -= prob * math.log2(prob)
        return round(entropy, 3)

    def monitor_host(self, latency: float, response_text: str, prompt_len: int = 0):
        completion_len = len(response_text)
        entropy = self._calculate_shannon_entropy(response_text)
        self.current_health.update_metrics(
            latency=latency,
            entropy=entropy,
            prompt_len=prompt_len,
            completion_len=completion_len)
        if hasattr(self, 'diagnostician'):
            new_diag = self.diagnostician.diagnose(
                self.current_health.efficiency_index,
                self.current_health.compliance)
            self.current_health.diagnosis = new_diag

        return self.current_health

    def get_prompt_modifiers(self) -> Dict[str, bool]:
        mods = {
            "include_somatic": True,
            "include_inventory": True,
            "include_memories": True,
            "simplify_instruction": False,
            "inject_chaos": False}
        diag = self.current_health.diagnosis
        if diag == "REFUSAL":
            mods["include_inventory"] = False
            mods["include_memories"] = False
            mods["simplify_instruction"] = True
        elif diag == "FATIGUED":
            mods["simplify_instruction"] = True
            mods["include_somatic"] = False
        elif diag == "OVERBURDENED":
            mods["include_inventory"] = False
            mods["include_memories"] = False
        elif diag == "LOOPING":
            mods["inject_chaos"] = True
        if self.current_health.compliance < 0.8:
            mods["include_memories"] = False
            if not mods["include_memories"]:
                self.events.log(f"{Prisma.GRY}SYMBIOSIS: Compliance Low ({self.current_health.compliance:.2f}). Memories Redacted.{Prisma.RST}", "SYS")
        self.last_outgoing_complexity = self._calculate_complexity(mods)
        return mods

    @staticmethod
    def _calculate_complexity(mods: Dict[str, bool]) -> float:
        score = 0.2
        if mods.get("include_somatic"): score += 0.2
        if mods.get("include_inventory"): score += 0.2
        if mods.get("include_memories"): score += 0.3
        if mods.get("simplify_instruction"): score -= 0.1
        if mods.get("inject_chaos"): score += 0.1
        return min(1.0, max(0.1, score))

    def generate_anchor(self, current_state: Dict) -> str:
        soul = current_state.get("soul", {})
        phys = current_state.get("physics", {})
        return CoherenceAnchor.compress_anchor(soul, phys)