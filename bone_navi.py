"""bone_navi.py"""
# Includes algorithms adapted from navi-SAD by Nelson Spence (Project-Navi)
# under the Apache 2.0 License.

from collections import deque
import math

class NaviSADProtocol:
    def __init__(self, history_size: int = 10):
        self.history_size = history_size
        self.attention_proxy_history = deque(maxlen=history_size)

    def calculate_semantic_dimension(self, efficiency_index: float, novelty: float) -> float:
        """
        Calculates the semantic fractal dimension based on the (u,v)-flower
        log-ratio convergence theorem: d_B = log(u+v) / log(u).
        """
        # 1. Map to u (direct path). Must be > 1 to satisfy the theorem's hu: 1 < u requirement.
        u = max(1.1, 1.1 + (efficiency_index * 5.0))

        # 2. Map to v (lateral path).
        v = max(0.0, novelty * 10.0)

        # 3. Calculate Box-Counting Dimension (d_B)
        return math.log(u + v) / math.log(u)

    def calculate_malignancy_factor(self, current_text: str, current_drag: float) -> float:
        """
        Approximates Spectral Attention Divergence (SAD) to calculate M_a.
        Measures the sudden collapse of variance (looping/fixation).
        """
        if not current_text: return 0.0
        words = current_text.lower().split()
        if len(words) < 5: return 0.0

        unique_ratio = len(set(words)) / len(words)
        divergence_spike = (1.0 - unique_ratio) * (current_drag / 3.0)

        self.attention_proxy_history.append(divergence_spike)

        # M_a is the rolling magnitude of this divergence
        m_a = sum(self.attention_proxy_history) / max(1, len(self.attention_proxy_history))
        return min(1.0, max(0.0, m_a))

    def execute_nudge_test(self, engine_ref, prompt: str) -> bool:
        """
        Dual-Path Attention Comparison.
        Returns True if the system is brittle (diverges wildly on microscopic noise).
        """
        # We query the stability via the Cybernetic Governor's Immune Competence (I_c)
        # If I_c is critically low, the system fails the nudge test.
        last_phys = getattr(engine_ref.observer, "last_physics_packet", None)
        i_c = getattr(last_phys, "i_c", 1.0) if last_phys else 1.0

        return i_c < 0.4

    def detect_point_attractor(self) -> bool:
        """
        Delay-Coordinate Attractor Reconstruction.
        Detects False Cohesion (The Jester's trigger).
        """
        if len(self.attention_proxy_history) < self.history_size:
            return False

        # If the variance of the last N states is near zero, we are trapped in a point attractor
        recent = list(self.attention_proxy_history)
        variance = sum((x - sum(recent)/len(recent))**2 for x in recent) / len(recent)

        return variance < 0.01 and recent[-1] > 0.0 # Stuck, and not at baseline zero