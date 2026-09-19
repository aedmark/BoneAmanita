"""tests/test_somatic_budget.py

ROADMAP D1: `SomaticBudget.evaluate()`'s thresholds used to be hardcoded in
Python, in violation of A1's rule that config constants live in `BoneConfig`
so tuning them does something. These tests pin the behaviour against real
config, and prove it is actually read (not just declared) by mutating a
threshold and checking the decision moves with it, the same discipline A4
uses for the composer's own gates.
"""

from body.somatic_budget import SomaticBudget
from tests.base import BoneTestCase


class SomaticBudgetReadsItsConfig(BoneTestCase):
    def test_default_config_ref_falls_back_to_boneconfig(self):
        budget = SomaticBudget.evaluate({}, {})
        self.assertEqual(budget.reason, "Nominal")
        self.assertEqual(budget.sentence_cap, 10)

    def test_flagging_threshold_is_read_from_config_not_hardcoded(self):
        cfg = self.engine.config
        exhaustion = 0.5
        # Below the shipped 0.6 flagging threshold: not flagging yet.
        baseline = SomaticBudget.evaluate(
            {"exhaustion": exhaustion}, {}, config_ref=cfg
        )
        self.assertNotIn("flagging", baseline.reason)

        cfg.SOMATIC_BUDGET.E_U_FLAGGING = 0.3
        moved = SomaticBudget.evaluate({"exhaustion": exhaustion}, {}, config_ref=cfg)
        self.assertIn("flagging", moved.reason)
        self.assertEqual(moved.sentence_cap, 3)
        self.assertFalse(moved.closing_question_allowed)

    def test_atp_depleted_threshold_is_read_from_config_not_hardcoded(self):
        cfg = self.engine.config
        atp = 15.0
        baseline = SomaticBudget.evaluate({}, {"atp_pool": atp}, config_ref=cfg)
        self.assertIn("depleted", baseline.reason)

        cfg.SOMATIC_BUDGET.ATP_DEPLETED = 5.0
        moved = SomaticBudget.evaluate({}, {"atp_pool": atp}, config_ref=cfg)
        self.assertNotIn("depleted", moved.reason)
        # 15 ATP still sits below ATP_MODERATE (40), so the milder tier applies.
        self.assertEqual(moved.retry_allowance, cfg.SOMATIC_BUDGET.RETRY_ALLOWANCE_ATP_MODERATE)

    def test_anaerobic_respiration_tightens_the_cap_independent_of_atp(self):
        """A single costly turn (respiration) is a different signal from the
        ATP pool's cumulative level: it should tighten the cap even when the
        pool itself is healthy."""
        cfg = self.engine.config
        healthy = SomaticBudget.evaluate(
            {}, {"atp_pool": 100.0, "respiration": "RESPIRING"}, config_ref=cfg
        )
        self.assertEqual(healthy.reason, "Nominal")

        anaerobic = SomaticBudget.evaluate(
            {}, {"atp_pool": 100.0, "respiration": "ANAEROBIC"}, config_ref=cfg
        )
        self.assertIn("anaerobic", anaerobic.reason)
        self.assertEqual(anaerobic.sentence_cap, cfg.SOMATIC_BUDGET.SENTENCE_CAP_ANAEROBIC)

    def test_anaerobic_threshold_is_read_from_config_not_hardcoded(self):
        cfg = self.engine.config
        cfg.SOMATIC_BUDGET.SENTENCE_CAP_ANAEROBIC = 1
        budget = SomaticBudget.evaluate(
            {}, {"atp_pool": 100.0, "respiration": "ANAEROBIC"}, config_ref=cfg
        )
        self.assertEqual(budget.sentence_cap, 1)

    def test_ros_turbulence_narrows_the_temperature_band_from_config(self):
        cfg = self.engine.config
        cfg.SOMATIC_BUDGET.TEMP_BAND_ROS_TURBULENT = [0.1, 0.2]
        budget = SomaticBudget.evaluate({}, {"ros": 999.0}, config_ref=cfg)
        self.assertEqual(budget.temperature_band, (0.1, 0.2))

    def test_reasons_stack_when_multiple_conditions_hold(self):
        budget = SomaticBudget.evaluate(
            {"exhaustion": 0.9, "effort": 5.0},
            {"atp_pool": 5.0, "ros": 999.0},
        )
        for expected in ("flagging", "critically low", "depleted", "turbulence"):
            with self.subTest(expected=expected):
                self.assertIn(expected, budget.reason)

    def test_body_narration_is_forbidden_outside_adventure(self):
        budget = SomaticBudget.evaluate({}, {}, active_mode="CONVERSATION")
        self.assertTrue(budget.forbid_body_narration)

    def test_adventure_mode_permits_narration_for_room_templates(self):
        budget = SomaticBudget.evaluate({}, {}, active_mode="ADVENTURE")
        self.assertFalse(budget.forbid_body_narration)
