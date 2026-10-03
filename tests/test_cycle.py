"""tests/test_cycle.py"""

import unittest

from engine.cycle import CycleSimulator, _native_permutation_entropy, _native_wls

try:
    from tests.base import BoneTestCase
except ImportError:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tests.base import BoneTestCase


class CycleNativeMathTests(BoneTestCase):
    def test_native_wls_perfect_fit(self):
        log_r = [1.0, 2.0, 3.0]
        log_m = [2.0, 4.0, 6.0]
        weights = [1.0, 1.0, 1.0]

        slope = _native_wls(log_r, log_m, weights)
        self.assertAlmostEqual(
            slope,
            2.0,
            places=2,
            msg="[FAIL] WLS failed to calculate accurate slope on clean data.",
        )

    def test_native_wls_hallucination_bypass(self):
        log_r = [1.0, 2.0, 3.0]
        log_m = [10.0, -5.0, 20.0]
        weights = [1.0, 1.0, 1.0]

        slope = _native_wls(log_r, log_m, weights, r2_threshold=0.90)
        self.assertEqual(
            slope,
            0.0,
            "[FAIL] Quality Gate failed. WLS returned a dimension for a complete hallucination.",
        )

    def test_native_permutation_entropy(self):
        time_series_ordered = [1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 1.0, 2.0, 3.0]
        pe_low = _native_permutation_entropy(time_series_ordered, m=3, tau=1)

        time_series_chaos = [1.4, 0.1, 9.9, 3.2, 5.5, 0.4, 8.8, 2.1, 7.6]
        pe_high = _native_permutation_entropy(time_series_chaos, m=3, tau=1)

        self.assertTrue(
            pe_low < pe_high,
            "[FAIL] Permutation Entropy failed to distinguish order from chaos.",
        )

    def test_circuit_breaker(self):
        sim = CycleSimulator(self.engine)

        self.engine.system_health.physics_online = False

        self.assertFalse(
            sim.check_circuit_breaker("OBSERVE"),
            "[FAIL] Circuit Breaker allowed OBSERVE despite dead Physics.",
        )
        self.assertTrue(
            sim.check_circuit_breaker("UNKNOWN_PHASE"),
            "[FAIL] Circuit Breaker blocked an unmapped safe phase.",
        )


if __name__ == "__main__":
    unittest.main()


class InvariantRollback(unittest.TestCase):
    """A turn that ends with negative ATP is rolled back and refused, not kept."""

    def test_a_breach_restores_the_frozen_state(self):
        from types import SimpleNamespace
        from unittest.mock import MagicMock

        mito = SimpleNamespace(state=SimpleNamespace(atp_pool=40.0))
        eng = SimpleNamespace(health=90.0, stamina=80.0, trauma_accum={"panic": 0.1},
                              bio=SimpleNamespace(mito=mito), events=MagicMock())

        def spend(_sim, ctx):
            eng.health, mito.state.atp_pool = 10.0, -5.0
            return ctx

        sim = CycleSimulator.__new__(CycleSimulator)
        sim.eng, sim.executor = eng, SimpleNamespace(execute_phases=spend)
        ctx = sim.run_simulation(SimpleNamespace(logs=[], refusal_triggered=False))
        self.assertTrue(ctx.refusal_triggered)
        self.assertEqual((eng.health, mito.state.atp_pool), (90.0, 40.0))
        self.assertIn("Invariant Breach", ctx.logs[-1])
