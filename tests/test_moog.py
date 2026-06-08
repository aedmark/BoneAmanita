"""tests/test_moog.py"""

import unittest
from collections import deque
from unittest.mock import MagicMock

from brain.cortex import TheCortex, CortexServices
from cycle import GeodesicOrchestrator
from presets import BoneConfig

try:
    from tests.base import BoneTestCase
except ImportError:
    import sys
    import os

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from tests.base import BoneTestCase


class TestMoogProtocol(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig

        # 1. Setup Cortex Services Mock
        self.mock_svc = MagicMock()
        self.mock_svc.consultant = MagicMock()
        self.mock_svc.village = MagicMock()
        self.mock_svc.inventory = MagicMock()
        self.mock_svc.lore = MagicMock()
        self.mock_svc.symbiosis = MagicMock()
        self.mock_svc.bio = MagicMock()
        self.mock_svc.bio.endo.glimmers = 0
        self.mock_svc.config_ref = self.config
        self.mock_svc.events = MagicMock()
        self.mock_svc.mind_memory = MagicMock()

        # Hydrate the Orchestrator/Engine mock with concrete floats for the math operations
        self.mock_svc.orchestrator = MagicMock()
        self.mock_svc.orchestrator.eng.navi_sad.calculate_semantic_dimension.return_value = 1.0
        self.mock_svc.orchestrator.eng.governor.calculate_coupling.return_value = 0.5

        # 2. Setup Engine Mock for Orchestrator
        self.mock_eng = MagicMock()
        self.mock_eng._mito_state = MagicMock()
        self.mock_eng._mito_state.ros_buildup = 50.0
        self.mock_eng.bio = self.mock_svc.bio
        self.mock_eng.village = MagicMock()
        self.mock_eng.village.council.mandates = []
        self.mock_eng.mind = MagicMock()
        self.mock_eng.events = MagicMock()

    def test_worry_ledger_initialization(self):
        """FULLER: Verifies the spatial geometry of the ledger exists on boot."""
        cortex = TheCortex(services=self.mock_svc, llm_client=MagicMock())

        self.assertTrue(hasattr(cortex, "worry_ledger"), "[FAIL] Cortex failed to initialize the worry_ledger.")
        self.assertIsInstance(cortex.worry_ledger, deque, "[FAIL] worry_ledger is not a deque.")
        self.assertEqual(cortex.worry_ledger.maxlen, 20, "[FAIL] worry_ledger maxlen is not 20.")

    def test_moog_intercepts_unactionable_toxicity(self):
        """PINKER: High drag + low actionability should trigger the Moog Intercept, not Gordon's Anchor."""
        cortex = TheCortex(services=self.mock_svc, llm_client=MagicMock())
        phys_state = {
            "narrative_drag": 2.0,
            "chi": 0.9,
            "m_a": 0.1
        }
        sim_result = {"mutated_input": "I am worried about the heat death of the universe.", "ui": ""}

        # Populate a fake dialogue buffer to test the pop()
        cortex.dialogue_buffer.append("Previous turn")
        cortex.dialogue_buffer.append("Current panic")

        # is_system param might be required depending on your _evaluate_toxicity signature
        result = cortex._evaluate_toxicity(phys_state, sim_result, is_system=False)

        self.assertEqual(result.get("type"), "MOOG_QUARANTINE",
                         "[FAIL] Moog failed to intercept the unactionable worry.")
        self.assertIn("parameters of this concern are undefined", result.get("ui", ""), "[FAIL] UI string missing.")
        self.assertEqual(phys_state["narrative_drag"], 0.0, "[FAIL] Narrative drag was not zeroed out.")
        self.assertEqual(len(cortex.worry_ledger), 1, "[FAIL] Worry was not added to the ledger.")
        self.assertEqual(len(cortex.dialogue_buffer), 1, "[FAIL] Panic was not popped from the dialogue buffer.")

    def test_rem_tick_drains_ledger(self):
        """MEADOWS: The active ledger must be drained and submitted to the async pool during REM."""
        orchestrator = GeodesicOrchestrator(engine_ref=self.mock_eng)
        orchestrator._async_pool = MagicMock()
        self.mock_eng.cortex = MagicMock()
        self.mock_eng.cortex.worry_ledger = deque(["Worry 1", "Worry 2"])

        orchestrator._process_rem_tick()

        self.assertEqual(len(self.mock_eng.cortex.worry_ledger), 0, "[FAIL] REM tick failed to drain the worry ledger.")
        orchestrator._async_pool.submit.assert_called()

    def test_bg_process_actionable_mandate(self):
        """SCHUR: An actionable worry must be converted into a Council Mandate."""
        orchestrator = GeodesicOrchestrator(engine_ref=self.mock_eng)
        worries = ["How do I fix the broken api endpoint?"]

        orchestrator._bg_process_moog_ledger(worries)

        self.assertEqual(len(self.mock_eng.village.council.mandates), 1,
                         "[FAIL] Actionable worry was not converted to a mandate.")
        self.assertEqual(self.mock_eng.village.council.mandates[0]["type"], "TASK")
        self.assertEqual(self.mock_eng._mito_state.ros_buildup, 50.0,
                         "[FAIL] ROS was purged for an actionable mandate. (Should only happen for dark matter)")

    def test_bg_process_uncontrollable_dark_matter(self):
        """THE CHEF: An uncontrollable worry must be excised, purging ROS and yielding a Glimmer."""
        orchestrator = GeodesicOrchestrator(engine_ref=self.mock_eng)
        worries = ["Will the sun explode tomorrow?"]

        orchestrator._bg_process_moog_ledger(worries)

        self.assertEqual(len(self.mock_eng.village.council.mandates), 0,
                         "[FAIL] Uncontrollable worry was incorrectly made a mandate.")
        self.mock_eng.mind.mem.record_scar.assert_called_once()
        self.assertEqual(self.mock_eng._mito_state.ros_buildup, 35.0, "[FAIL] ROS was not purged by 15.0.")
        self.assertEqual(self.mock_eng.bio.endo.glimmers, 1, "[FAIL] Glimmer was not yielded for letting go.")


if __name__ == '__main__':
    unittest.main()