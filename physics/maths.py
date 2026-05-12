"""physics/maths.py"""
import math
from collections import Counter, deque
from typing import List, Tuple


def _native_ordinal_pattern(window: List[float]) -> Tuple[int, ...]:
    """
    Translates a sequence of raw numbers into a relative structural rank (an ordinal pattern).
    Instead of caring about the exact values, it maps the "shape" of the thought.
    Example: [10.5, 8.2, 12.0] becomes (1, 0, 2) because 8.2 is lowest (idx 1), then 10.5 (idx 0), then 12.0 (idx 2).
    """
    return tuple(i for i, v in sorted(enumerate(window), key=lambda x: x[1]))


def _native_detect_false_cohesion(history: List[float], window_size: int = 3) -> bool:
    """
    Detects if the system is stuck in a sycophantic loop or a "broken record" state.
    It does this by checking if the exact "shape" of the recent energy history
    perfectly mirrors the shape of the history just before it.
    If they match, the system has stopped thinking dynamically and is just coasting.
    """
    if len(history) < window_size * 2:
        return False
    return _native_ordinal_pattern(history[-window_size:]) == _native_ordinal_pattern(
        history[-(window_size * 2): -window_size]
    )


def _native_permutation_entropy(time_series: List[float], window_size: int = 3) -> float:
    """
    Calculates the topological chaos (entropy) of a time series.
    A low value means the system's energy fluctuations are highly predictable (stagnant).
    A high value means the system is dynamically reacting and exploring new states (healthy chaos).
    """
    if len(time_series) < window_size:
        return 1.0
    patterns = [
        _native_ordinal_pattern(time_series[i: i + window_size]) for i in range(len(time_series) - window_size + 1)
    ]
    counts = Counter(patterns)
    total_patterns = len(patterns)
    entropy = -sum((c / total_patterns) * math.log2(c / total_patterns) for c in counts.values())
    max_e = math.log2(math.factorial(window_size))
    return entropy / max_e if max_e > 0 else 0.0


def _native_coincidence_length(orbit_a: List[float], orbit_b: List[float], tol: float = 0.01) -> int:
    """
    Measures how long two semantic trajectories stay mathematically "close" to one another
    before drifting apart. Used to track if a thought is staying on topic or fracturing.
    """
    for i, (a, b) in enumerate(zip(orbit_a, orbit_b)):
        if abs(a - b) > tol: return i
    return min(len(orbit_a), len(orbit_b))


class CreativeDeterminantEngine:
    """
    Mathematical integration of the Creative Determinant (CD) framework.
    Original CD equations and field theory authored by Nelson Spence (Project Navi LLC).
    Licensed under Apache 2.0.
    This engine governs the deep metabolic limits of the machine. It defines creativity and
    structural generation not as infinite resources, but as biological stocks that accumulate
    fatigue ("coherence debt") when pushed beyond sustainable capacity.
    """

    def __init__(self, lambda_base=1.0, eta=0.1, rho=0.05, p=2.0, c=1.5):
        self.coherence_debt = 0.0
        self.lambda_base = lambda_base
        self.eta = eta
        self.rho = rho
        self.p = p
        self.c = c

    def calculate_viability(self, kappa: float, gamma: float, mu: float) -> float:
        """
        Calculates if the system actually has the physical capacity to generate the requested thought.
        If Viability is negative, the prompt is metabolically impossible in the current state.
        kappa = Capacity, gamma = Generative drive, mu = Moral/Structural Friction.
        """
        lambda_eff = self.lambda_base * (1.0 + self.coherence_debt)
        return (kappa * gamma) - (lambda_eff * mu)

    def update_coherence_debt(self, actual_coherence: float, sustainable_capacity: float) -> float:
        """
        Calculates the accumulation and decay of cognitive fatigue over time.
        """
        overcapacity = max(0.0, actual_coherence - sustainable_capacity)
        delta_d = (self.eta * overcapacity) - (self.rho * self.coherence_debt)
        self.coherence_debt = max(0.0, self.coherence_debt + delta_d)
        return self.coherence_debt

    def execute_metabolic_tick(self, viability_potential: float) -> tuple[float, float]:
        """
        Applies the L_infty algebraic bound derived from the Lean 4 PDE formalization.
        Translates abstract 'viability' into hard biological currency: ATP (energy) and ROS (toxicity).
        """
        b = viability_potential
        if b > 0:
            power_divisor = max(0.001, self.p - 1.0)
            max_regen_capacity = math.pow(b / self.c, 1.0 / power_divisor)
            delta_atp = min(max_regen_capacity, 5.0)
            delta_ros = -(b * 0.5)
        else:
            delta_atp = b * 2.0
            delta_ros = abs(b) * 1.5
        return delta_atp, delta_ros


class NaviSADProtocol:
    """
    Calculates Semantic Fractal Dimensions, Spectral Attention Divergence, and Point Attractors.
    Used to mathematically detect when an LLM falls into pathological loops, rote repetition,
    or sycophantic "yes-man" behavior.
    """

    def __init__(self, history_size: int = 10):
        self.history_size = history_size
        self.attention_proxy_history = deque(maxlen=history_size)
        self.recent_texts = deque(maxlen=history_size)

    def calculate_semantic_dimension(self, efficiency_index: float, novelty: float) -> float:
        """
        Calculates the fractal dimension of the conversation.
        A higher dimension indicates a complex, branching thought process.
        A dimension collapsing toward zero indicates the conversation is flattening out.
        """
        u = max(1.1, 1.1 + (efficiency_index * 5.0))
        return math.log(u + max(0.0, novelty * 10.0)) / math.log(u)

    def calculate_malignancy_factor(self, current_text: str, current_drag: float) -> float:
        """
        Malignancy is a measure of runaway, unconstrained optimization (a conversational cancer).
        If the model is generating tons of text but using the same words over and over
        (high repetition + high drag), the malignancy factor spikes.
        """
        words = current_text.lower().split() if current_text else []
        if not words:
            self.attention_proxy_history.append(0.0)
            return 0.0
        intra_repetition = 1.0 - (len(set(words)) / len(words))
        cross_repetition = 0.0
        if current_text in self.recent_texts:
            cross_repetition = 1.0
        self.recent_texts.append(current_text)
        total_repetition = max(intra_repetition, cross_repetition)
        proxy_value = min(2.0, total_repetition * max(1.0, current_drag / 3.0))
        self.attention_proxy_history.append(proxy_value)
        history_avg = sum(self.attention_proxy_history) / len(self.attention_proxy_history)
        return max(0.0, min(1.0, history_avg))

    def execute_nudge_test(self, engine_ref, prompt: str = "") -> bool:
        """
        Evaluates the Immune Competence (i_c) of the overarching physics engine.
        If the immune system is severely degraded (< 0.4), the system requires a hard 'nudge'
        to break out of its current state and avoid total collapse.
        """
        obs = getattr(engine_ref, "observer", None)
        packet = getattr(obs, "last_physics_packet", None)
        return float(getattr(packet, "i_c", 1.0)) < 0.4

    def detect_point_attractor(self) -> bool:
        """
        Detects if the conversation has collapsed into a 'Point Attractor'.
        In chaos theory, a point attractor is a state that a system inexorably falls into
        and cannot escape. In conversational AI, this is the "broken record" effect where
        the AI agrees with everything and says nothing new.
        Detected when the variance of the recent attention history approaches zero.
        """
        if len(self.attention_proxy_history) < self.history_size:
            return False
        recent = list(self.attention_proxy_history)
        mean = sum(recent) / len(recent)
        return (sum((x - mean) ** 2 for x in recent) / len(recent)) < 0.01 and recent[-1] > 0.0
