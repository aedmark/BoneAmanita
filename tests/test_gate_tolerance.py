"""tests/test_gate_tolerance.py

ROADMAP D0b. Four gates can refuse a turn or bill the body for danger, and all
four were sized for ADVENTURE, where high drag means a story coming apart. A
census of 30 conversation turns put the PINKER sum at a mean of 44 against a
gate of 35, and voltage at a mean of 21.7 against a meltdown line of 18: both
thresholds sat below the mean of ordinary conversation, so the engine refused
most turns and burned its own health while a person answered "ok".

The gates now scale with `BonePresets.MODES[...]["gate_tolerance"]`, carried on
the config as `GATE_TOLERANCE`. These tests pin that a conversation tolerates
what an adventure refuses, and that the tolerance is applied rather than merely
declared.
"""

import unittest

from machine.crucible import TheCrucible
from presets import BonePresets
from tests.base import BoneTestCase


class ToleranceReachesTheGates(BoneTestCase):
    """The engine boots in CONVERSATION here (see tests/base.py config)."""

    # PINKER reads drag*5 + chi*20 + m_a*30 against 35 * tolerance. This sums
    # to 45: refused at 1.0, allowed at 1.6, and inside the census range.
    MIDDLING = {"narrative_drag": 5.0, "chi": 0.5, "m_a": 0.33}

    def test_the_mode_tolerance_is_on_the_config(self):
        self.assertEqual(
            float(self.engine.config.GATE_TOLERANCE),
            float(BonePresets.MODES[self.engine.boot_mode]["gate_tolerance"]),
        )

    def test_conversation_allows_what_adventure_refuses(self):
        cortex = self.engine.cortex
        self.engine.config.GATE_TOLERANCE = 1.0
        refused = cortex._evaluate_toxicity(dict(self.MIDDLING), {"ui": ""}, is_system=False)
        self.assertEqual(
            refused.get("type"),
            "COUNTERFACTUAL_REJECTION",
            "at tolerance 1.0 this state is over the gate; the fixture no longer bites",
        )

        self.engine.config.GATE_TOLERANCE = 1.6
        allowed = cortex._evaluate_toxicity(dict(self.MIDDLING), {"ui": ""}, is_system=False)
        self.assertIsNone(
            allowed,
            "A conversation tolerance must let an ordinary terse exchange through.",
        )

    def test_a_genuine_extreme_is_still_refused(self):
        """Tolerance widens the gate; it does not remove it."""
        self.engine.config.GATE_TOLERANCE = 1.6
        extreme = {"narrative_drag": 9.0, "chi": 0.95, "m_a": 0.49}
        result = self.engine.cortex._evaluate_toxicity(extreme, {"ui": ""}, is_system=False)
        self.assertIsNotNone(result)

    def test_the_crucible_meltdown_line_scales(self):
        cfg = self.engine.config
        crucible = TheCrucible(config_ref=cfg)
        physics = {"narrative_drag": 1.0, "voltage": 22.0, "kappa": 0.2}

        cfg.GATE_TOLERANCE = 1.0
        state, damage, _ = crucible.audit_fire(dict(physics))
        self.assertEqual(state, "MELTDOWN")
        self.assertGreater(damage, 0.0)

        cfg.GATE_TOLERANCE = 1.6
        state, damage, _ = crucible.audit_fire(dict(physics))
        self.assertNotEqual(
            state,
            "MELTDOWN",
            "22.0 volts is under the conversation meltdown line (18 * 1.6) and "
            "must not cost health.",
        )


if __name__ == "__main__":
    unittest.main()
