"""tests/test_cycle.py"""

import unittest
from cycle import _native_wls, _native_permutation_entropy, CycleSimulator

try:
    from tests.base import BoneTestCase
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from tests.base import BoneTestCase


class CycleNativeMathTests(BoneTestCase):
    def test_native_wls_perfect_fit(self):
        # Perfect linear scaling
        log_r = [1.0, 2.0, 3.0]
        log_m = [2.0, 4.0, 6.0]
        weights = [1.0, 1.0, 1.0]

        slope = _native_wls(log_r, log_m, weights)
        self.assertAlmostEqual(slope, 2.0, places=2, msg="[FAIL] WLS failed to calculate accurate slope on clean data.")

    def test_native_wls_hallucination_bypass(self):
        # Garbage structural data (non-linear hallucination)
        log_r = [1.0, 2.0, 3.0]
        log_m = [10.0, -5.0, 20.0]
        weights = [1.0, 1.0, 1.0]

        slope = _native_wls(log_r, log_m, weights, r2_threshold=0.90)
        self.assertEqual(slope, 0.0, "[FAIL] Quality Gate failed. WLS returned a dimension for a complete hallucination.")

    def test_native_permutation_entropy(self):
        # A perfectly repeating series should have low PE
        time_series_ordered = [1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 1.0, 2.0, 3.0]
        pe_low = _native_permutation_entropy(time_series_ordered, m=3, tau=1)

        # A chaotic series should approach 1.0
        time_series_chaos = [1.4, 0.1, 9.9, 3.2, 5.5, 0.4, 8.8, 2.1, 7.6]
        pe_high = _native_permutation_entropy(time_series_chaos, m=3, tau=1)

        self.assertTrue(pe_low < pe_high, "[FAIL] Permutation Entropy failed to distinguish order from chaos.")

    def test_circuit_breaker(self):
        # Uses the integrated engine from BoneTestCase
        sim = CycleSimulator(self.engine)

        # Manually crash the physics pipeline
        self.engine.system_health.physics_online = False

        self.assertFalse(sim.check_circuit_breaker("OBSERVE"), "[FAIL] Circuit Breaker allowed OBSERVE despite dead Physics.")
        self.assertTrue(sim.check_circuit_breaker("UNKNOWN_PHASE"), "[FAIL] Circuit Breaker blocked an unmapped safe phase.")


if __name__ == '__main__':
    unittest.main()