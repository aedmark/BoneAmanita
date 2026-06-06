"""tests/test_navi.py"""

import unittest
import numpy as np
from core import CyberneticGovernor
from tests.base import BoneTestCase

class TestNavi(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.governor = CyberneticGovernor()

    def test_pde_active_regulation(self):
        physics_state = {"voltage": 40.0, "narrative_drag": 1.0}
        goal_vec = np.array([1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        dv, dd = self.governor.regulate(physics=physics_state, dt=1.0, goal_vector=goal_vec)
        self.assertIsInstance(dv, float)
        self.assertIsInstance(dd, float)

    def test_pid_fallback(self):
        self.governor.recalibrate(target_voltage=30.0, target_drag=0.6)
        physics_state = {"voltage": 20.0, "narrative_drag": 0.2}
        dv, dd = self.governor.regulate(physics=physics_state, dt=1.0, goal_vector=None)
        self.assertGreater(dv, 0.0, "PID failed to correct low voltage.")
        self.assertGreater(dd, 0.0, "PID failed to correct low narrative drag.")

    def test_policy_shift_coregulation(self):
        self.governor.last_lam1 = -0.5
        self.governor.last_sol = 'nontrivial'
        self.assertEqual(self.governor.get_policy_shift(), 'CO_REGULATION')

    def test_policy_shift_efficiency(self):
        self.governor.last_lam1 = 1.2
        self.governor.last_sol = 'trivial'
        self.assertEqual(self.governor.get_policy_shift(), 'EFFICIENCY')

    def test_endocrine_stress_modifier(self):
        class MockEndo:
            glimmers = 2
        physics_state = {"voltage": 30.0, "narrative_drag": 0.6}
        goal_vec = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        dv1, dd1 = self.governor.regulate(physics_state, dt=1.0, goal_vector=goal_vec, endocrine_state=None)
        dv2, dd2 = self.governor.regulate(physics_state, dt=1.0, goal_vector=goal_vec, endocrine_state=MockEndo())
        self.assertGreaterEqual(abs(dv2), abs(dv1))
        self.assertGreaterEqual(abs(dd2), abs(dd1))

if __name__ == "__main__":
    unittest.main()