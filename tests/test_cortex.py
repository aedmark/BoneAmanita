"""tests/test_cortex.py"""

import unittest
from unittest.mock import MagicMock
from brain.cortex import TheCortex, CortexServices
from presets import BoneConfig

try:
    from tests.base import BoneTestCase
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from tests.base import BoneTestCase


class CortexArchitectTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig()

        self.mock_services = CortexServices(
            events=MagicMock(),
            lore={},
            lexicon=MagicMock(),
            inventory=MagicMock(),
            consultant=MagicMock(),
            orchestrator=MagicMock(),
            symbiosis=MagicMock(),
            mind_memory=MagicMock(),
            bio=MagicMock(),
            config_ref=self.config
        )

        # _evaluate_toxicity inspects the orchestrator's engine to calculate limits.
        # By default, MagicMock returns other MagicMocks, which crash during math (min, float, division).
        # We explicitly supply safe float values for these deeply nested calculations.
        mock_eng = self.mock_services.orchestrator.eng
        mock_eng.navi_sad.calculate_semantic_dimension.return_value = 1.0
        mock_eng.shared_lattice.u.E = 0.5
        mock_eng.governor.calculate_coupling.return_value = 1.0

        self.cortex = TheCortex(self.mock_services, llm_client=MagicMock())

    def test_apply_boot_overlay_adventure(self):
        state = {"mind": {}}
        self.cortex.active_mode = "ADVENTURE"
        self.cortex._apply_boot_overlay(state, "SYSTEM_BOOT: A dark forest")

        self.assertIn("world", state, "[FAIL] Boot overlay failed to initialize world state.")
        self.assertIn("A dark forest", state["world"].get("orbit", []), "[FAIL] Thought seed not injected into orbit.")
        self.assertEqual(state["mind"].get("role"), "The Architect", "[FAIL] Incorrect role mapped for ADVENTURE mode.")

    def test_evaluate_toxicity_system_halt(self):
        # Trigger toxicity via extremely high narrative drag and moderate malignancy
        # (m_a >= 0.3 avoids the Moog Quarantine intercept)
        phys_state = {"narrative_drag": 2.5, "chi": 0.5, "m_a": 0.5}
        sim_result = {"ui": "Standard interface output."}

        halt_res = self.cortex._evaluate_toxicity(phys_state, sim_result, is_system=False)

        self.assertIsNotNone(halt_res, "[FAIL] Cortex failed to halt on toxic narrative parameters.")
        self.assertEqual(halt_res.get("type"), "SYSTEM_HALT", "[FAIL] Expected SYSTEM_HALT for high friction.")
        self.assertIn("Tensegrity Anchor engaged", halt_res.get("ui", ""), "[FAIL] Missing Gordon anchor warning.")

    def test_evaluate_toxicity_counterfactual_rejection(self):
        # Trigger severe structural rot via high malignancy and borderline friction
        # (f_drag <= 1.5 and chi <= 0.8 bypasses SYSTEM_HALT, but spike in m_a drives ROS > 35.0)
        phys_state = {"narrative_drag": 1.5, "chi": 0.8, "m_a": 1.0}
        sim_result = {"ui": ""}
        self.mock_services.bio.mito.state.ros_buildup = 0.0

        halt_res = self.cortex._evaluate_toxicity(phys_state, sim_result, is_system=False)

        self.assertIsNotNone(halt_res)
        self.assertEqual(halt_res.get("type"), "COUNTERFACTUAL_REJECTION", "[FAIL] Failed to trigger Counterfactual Rejection.")
        self.assertIn("Structural rot critical", halt_res.get("ui", ""), "[FAIL] Missing Pinker gate rejection log.")


if __name__ == '__main__':
    unittest.main()