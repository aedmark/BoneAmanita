"""tests/test_struts.py"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from struts import safe_get, safe_set, ux, ux_format
from tests.base import BoneTestCase


class DummyObject:
    def __init__(self):
        self.health = 100.0


class StrutsUtilityTests(BoneTestCase):
    @patch("core.LoreManifest")
    def test_ux_retrieval(self, mock_manifest_class):
        mock_instance = MagicMock()
        mock_instance.get.return_value = {
            "welcome": "Hello Traveler",
            "error": "System Crash",
        }
        mock_manifest_class.get_instance.return_value = mock_instance

        result = ux("main_strings", "welcome")
        self.assertEqual(
            result,
            "Hello Traveler",
            "[FAIL] ux() did not retrieve the correct string from LoreManifest.",
        )

        result_miss = ux("main_strings", "missing_key", default="Fallback")
        self.assertEqual(
            result_miss,
            "Fallback",
            "[FAIL] ux() failed to return the default value on a missing key.",
        )

    @patch("core.LoreManifest")
    def test_ux_format_degradation(self, mock_manifest_class):
        mock_instance = MagicMock()
        mock_instance.get.return_value = {"greet": "Hello {name}!"}
        mock_manifest_class.get_instance.return_value = mock_instance

        formatted = ux_format("main_strings", "greet", name="SLASH")
        self.assertEqual(
            formatted,
            "Hello SLASH!",
            "[FAIL] ux_format() failed to interpolate kwargs.",
        )

        degraded = ux_format("main_strings", "greet")
        self.assertEqual(
            degraded,
            "Hello {name}!",
            "[FAIL] ux_format() did not gracefully degrade to the raw string on KeyError.",
        )

    def test_safe_get_and_set_dict(self):
        target = {"voltage": 12.0}

        self.assertEqual(
            safe_get(target, "voltage"), 12.0, "[FAIL] safe_get failed on dict."
        )
        self.assertEqual(
            safe_get(target, "missing", default=0.0),
            0.0,
            "[FAIL] safe_get default failed on dict.",
        )

        safe_set(target, "voltage", 50.0)
        self.assertEqual(
            target["voltage"], 50.0, "[FAIL] safe_set failed to mutate dict."
        )

    def test_safe_get_and_set_object(self):
        target = DummyObject()

        self.assertEqual(
            safe_get(target, "health"),
            100.0,
            "[FAIL] safe_get failed on object attribute.",
        )
        self.assertEqual(
            safe_get(target, "stamina", default=50.0),
            50.0,
            "[FAIL] safe_get default failed on object.",
        )

        safe_set(target, "health", 20.0)
        self.assertEqual(
            target.health, 20.0, "[FAIL] safe_set failed to mutate object attribute."
        )

    def test_safe_set_none_rejection(self):
        with self.assertRaises(
            ValueError,
            msg="[FAIL] safe_set failed to raise ValueError when targeting None.",
        ):
            safe_set(None, "voltage", 10.0)


if __name__ == "__main__":
    unittest.main()
