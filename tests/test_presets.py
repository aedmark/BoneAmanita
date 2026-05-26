"""tests/test_presets.py"""

from tests.base import BoneTestCase
from genesis import BoneGenesis
from unittest.mock import patch, MagicMock

class PresetsBoundaryTests(BoneTestCase):
    def test_absolute_zero_reconciliation(self):
        self.engine.config.PHYSICS.VOLTAGE_FLOOR = 0.0
        self.engine.config.PHYSICS.DRAG_FLOOR = 0.0
        packet = {"voltage": 0.0, "narrative_drag": 0.0}
        reconciled = self.engine.config.reconcile_state(packet)
        self.assertEqual(reconciled["voltage"], 0.0, "[FAIL] Phantom energy injected! Voltage bounced off 0.0.")
        self.assertEqual(reconciled["narrative_drag"], 0.0, "[FAIL] Phantom drag injected! Drag bounced off 0.0.")

    def test_oroboros_negative_drag_clamp(self):
        with patch('soul.TheOroboros.apply_legacy') as mock_oroboros:

            def side_effect(dummy_phys, bio_proxy):
                setattr(dummy_phys, "narrative_drag", -5.0)
                return ["Massive Boon"]

            mock_oroboros.side_effect = side_effect
            config_dict = {"config": self.engine.config}
            anatomy = BoneGenesis.ignite(config_dict, lexicon_ref=MagicMock(), events_ref=MagicMock())
            final_drag = getattr(anatomy["embryo"].physics, "narrative_drag", 99.0)
            self.assertGreaterEqual(final_drag, 0.0, f"[FAIL] Oroboros boon caused a mathematical underflow! Drag: {final_drag}")
            self.assertEqual(final_drag, 0.0, "[FAIL] Drag did not clamp exactly to the 0.0 floor.")

    def test_missing_json_keys(self):
        if hasattr(self.engine.config.PHYSICS, "DRAG_HALT"):
            delattr(self.engine.config.PHYSICS, "DRAG_HALT")
        try:
            errors = self.engine.config.validate_integrity()
            self.assertIsInstance(errors, list)
        except AttributeError as e:
            self.fail(f"[FAIL] Missing key caused a fatal boot crash: {e}")

    def test_inverted_boundaries(self):
        self.engine.config.PHYSICS.VOLTAGE_MAX = 0.0
        self.engine.config.PHYSICS.VOLTAGE_FLOOR = 10.0
        errors = self.engine.config.validate_integrity()
        self.assertEqual(self.engine.config.PHYSICS.VOLTAGE_FLOOR, 0.0,"[FAIL] Inverted boundary did not clamp to exactly the ceiling.")
        self.assertTrue(len(errors) > 0,  "[FAIL] System failed to log the boundary repair.")
