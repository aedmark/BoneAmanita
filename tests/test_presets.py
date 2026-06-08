"""tests/test_presets.py"""

import unittest
import sys
import os

# Hard-wire the path directly instead of using a try/except.
# This guarantees test runners like Pytest/Unittest discover the Base class correctly.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.base import BoneTestCase
from presets import BoneConfig


class PresetsAndConfigTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig()

    def test_load_preset_dot_notation(self):
        # Simulate loading the ZEN preset which has nested dicts,
        # as well as injecting a flat dot-notation override.
        preset_dict = {
            "PHYSICS.VOLTAGE_MAX": 42.0,
            "BIO": {"METABOLISM_RATE": 0.5}
        }
        logs = self.config.load_preset(preset_dict)

        self.assertEqual(self.config.PHYSICS.VOLTAGE_MAX, 42.0, "[FAIL] load_preset failed to parse dot notation.")
        self.assertEqual(self.config.BIO.METABOLISM_RATE, 0.5, "[FAIL] load_preset failed to parse nested dictionary.")

    def test_validate_integrity_repairs_inversions(self):
        # Intentionally break the configuration boundaries
        self.config.PHYSICS.VOLTAGE_MAX = 10.0
        self.config.PHYSICS.VOLTAGE_FLOOR = 50.0  # Floor > Max
        self.config.BIO.METABOLISM_RATE = -1.0    # Cannot be negative

        errors = self.config.validate_integrity()

        self.assertTrue(len(errors) > 0, "[FAIL] validate_integrity did not return error logs for broken state.")
        self.assertEqual(self.config.PHYSICS.VOLTAGE_FLOOR, 10.0, "[FAIL] validate_integrity failed to clamp VOLTAGE_FLOOR to VOLTAGE_MAX.")
        self.assertEqual(self.config.BIO.METABOLISM_RATE, 0.0, "[FAIL] validate_integrity failed to clamp negative metabolism to 0.0.")

    def test_reconcile_state_clamps_physics(self):
        # Set strict configuration limits
        self.config.PHYSICS.VOLTAGE_FLOOR = 5.0
        self.config.PHYSICS.VOLTAGE_MAX = 20.0
        self.config.PHYSICS.DRAG_FLOOR = 1.0
        self.config.PHYSICS.DRAG_HALT = 5.0

        # Provide a physics dict that is wildly out of bounds
        raw_physics = {
            "voltage": 999.0,         # Way over max
            "narrative_drag": 0.1     # Way under floor
        }

        reconciled = self.config.reconcile_state(raw_physics)

        self.assertEqual(reconciled["voltage"], 20.0, "[FAIL] reconcile_state failed to clamp over-voltage.")
        self.assertEqual(reconciled["narrative_drag"], 1.0, "[FAIL] reconcile_state failed to clamp under-drag.")

    def test_tune_type_validation(self):
        # Ensure we cannot tune a float parameter with a string
        original_voltage = getattr(self.config.PHYSICS, "VOLTAGE_MAX", 100.0)

        response = self.config.tune("PHYSICS", "VOLTAGE_MAX", "HIGH")

        # FIX: Lowercase the response so we aren't tripped up by capitalization changes in LoreManifest UX strings.
        self.assertIn("type mismatch", response.lower(), "[FAIL] tune() failed to catch type mismatch.")
        self.assertEqual(self.config.PHYSICS.VOLTAGE_MAX, original_voltage, "[FAIL] tune() mutated the value despite type mismatch.")

    def test_tune_successful_application(self):
        response = self.config.tune("PHYSICS", "BASE_DRAG", 2.5)

        # FIX: Lowercase the response.
        self.assertIn("tuned", response.lower(), "[FAIL] tune() did not return success string.")
        self.assertEqual(self.config.PHYSICS.BASE_DRAG, 2.5, "[FAIL] tune() failed to apply the new value.")


if __name__ == '__main__':
    unittest.main()