"""physics/math.py"""

import math
from collections import Counter, deque
from typing import List, Tuple

def _native_ordinal_pattern(window: List[float]) -> Tuple[int, ...]:
    return tuple(i for i, v in sorted(enumerate(window), key=lambda x: x[1]))

def _native_detect_false_cohesion(history: List[float], window_size: int = 3) -> bool:
    if len(history) < window_size * 2:
        return False
    return _native_ordinal_pattern(history[-window_size:]) == _native_ordinal_pattern(
        history[-(window_size * 2) : -window_size]
    )

def _native_permutation_entropy(time_series: List[float], window_size: int = 3) -> float:
    if len(time_series) < window_size:
        return 1.0
    patterns = [
        _native_ordinal_pattern(time_series[i : i + window_size]) for i in range(len(time_series) - window_size + 1)
    ]
    counts = Counter(patterns)
    total_patterns = len(patterns)
    entropy = -sum((c / total_patterns) * math.log2(c / total_patterns) for c in counts.values())
    max_e = math.log2(math.factorial(window_size))
    return entropy / max_e if max_e > 0 else 0.0

def _native_coincidence_length(orbit_a: List[float], orbit_b: List[float], tol: float = 0.01) -> int:
    for i, (a, b) in enumerate(zip(orbit_a, orbit_b)):
        if abs(a - b) > tol: return i
    return min(len(orbit_a), len(orbit_b))

class CreativeDeterminantEngine:
    """
    Mathematical integration of the Creative Determinant (CD) framework.
    Original CD equations and field theory authored by Nelson Spence (Project Navi LLC).
    Licensed under Apache 2.0.
    """

    def __init__(self, lambda_base=1.0, eta=0.1, rho=0.05, p=2.0, c=1.5):
        self.coherence_debt = 0.0
        self.lambda_base = lambda_base
        self.eta = eta
        self.rho = rho
        self.p = p
        self.c = c

    def calculate_viability(self, kappa: float, gamma: float, mu: float) -> float:
        lambda_eff = self.lambda_base * (1.0 + self.coherence_debt)
        return (kappa * gamma) - (lambda_eff * mu)

    def update_coherence_debt(self, actual_coherence: float, sustainable_capacity: float) -> float:
        overcapacity = max(0.0, actual_coherence - sustainable_capacity)
        delta_d = (self.eta * overcapacity) - (self.rho * self.coherence_debt)
        self.coherence_debt = max(0.0, self.coherence_debt + delta_d)
        return self.coherence_debt

    def execute_metabolic_tick(self, viability_potential: float) -> tuple[float, float]:
        """
        Applies the L_infty algebraic bound derived from the Lean 4 PDE formalization.
        """
        b = viability_potential
        if b > 0:
            max_regen_capacity = math.pow(b / self.c, 1.0 / (self.p - 1.0))
            delta_atp = min(max_regen_capacity, 5.0)
            delta_ros = -(b * 0.5)
        else:
            delta_atp = b * 2.0
            delta_ros = abs(b) * 1.5
        return delta_atp, delta_ros

class NaviSADProtocol:
    """
    Calculates Semantic Fractal Dimensions, Spectral Attention Divergence, and Point Attractors.
    """
    def __init__(self, history_size: int = 10):
        self.history_size = history_size
        self.attention_proxy_history = deque(maxlen=history_size)

    def calculate_semantic_dimension(self, efficiency_index: float, novelty: float) -> float:
        u = max(1.1, 1.1 + (efficiency_index * 5.0))
        return math.log(u + max(0.0, novelty * 10.0)) / math.log(u)

    def calculate_malignancy_factor(self, current_text: str, current_drag: float) -> float:
        words = current_text.lower().split() if current_text else []
        if len(words) < 5:
            return 0.0
        repetition_ratio = 1.0 - (len(set(words)) / len(words))
        self.attention_proxy_history.append(repetition_ratio * (current_drag / 3.0))
        history_avg = sum(self.attention_proxy_history) / len(self.attention_proxy_history)
        return max(0.0, min(1.0, history_avg))

    def execute_nudge_test(self, engine_ref, prompt: str = "") -> bool:
        obs = getattr(engine_ref, "observer", None)
        packet = getattr(obs, "last_physics_packet", None)
        if isinstance(packet, dict):
            energy = packet.get("energy")
        else:
            energy = getattr(packet, "energy", None)
        return getattr(energy, "i_c", 1.0) < 0.4

    def detect_point_attractor(self) -> bool:
        if len(self.attention_proxy_history) < self.history_size: return False
        recent = list(self.attention_proxy_history)
        mean = sum(recent) / len(recent)
        return (sum((x - mean) ** 2 for x in recent) / len(recent)) < 0.01 and recent[-1] > 0.0