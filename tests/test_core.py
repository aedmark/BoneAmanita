"""tests/test_core.py"""

import json
import os
import sys
import threading
import unittest
from collections import deque
from unittest.mock import MagicMock, patch

try:
    from tests.base import BoneTestCase
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tests.base import BoneTestCase

from core import (
    ArchetypeArbiter,
    CyberneticGovernor,
    EventBus,
    JSONEncoder,
    LoreManifest,
    TheObserver,
)


class DummySlotted:
    __slots__ = ["public_data", "api_key"]
    def __init__(self):
        self.public_data = "safe_value"
        self.api_key = "super_secret_123"


class DummyDict:
    def __init__(self):
        self.password = "hunter2"
        self.stamina = 100
        self.lock = threading.Lock()


class CoreArchitectureTests(unittest.TestCase):

    def test_json_encoder_redaction_and_sanitization(self):
        """Proves the JSONEncoder physically amputates secrets and ignores thread locks."""
        slotted_obj = DummySlotted()
        dict_obj = DummyDict()

        payload = {
            "slotted": slotted_obj,
            "dict": dict_obj,
            "set_data": {1, 2, 3},
            "deque_data": deque(["a", "b"])
        }

        encoded = json.dumps(payload, cls=JSONEncoder)
        decoded = json.loads(encoded)

        self.assertEqual(decoded["slotted"]["public_data"], "safe_value")
        self.assertEqual(decoded["slotted"]["api_key"], "[REDACTED]")
        self.assertEqual(decoded["dict"]["stamina"], 100)
        self.assertEqual(decoded["dict"]["password"], "[REDACTED]")
        self.assertNotIn("lock", decoded["dict"], "[FAIL] Thread locks must be dropped.")
        self.assertEqual(decoded["set_data"], [1, 2, 3])
        self.assertEqual(decoded["deque_data"], ["a", "b"])

    def test_event_bus_recursion_protection(self):
        """Proves the EventBus stops infinite recursive publishing loops."""
        bus = EventBus(max_memory=10)
        call_count = {"A": 0, "B": 0}

        def cascade_a(data):
            call_count["A"] += 1
            bus.publish("EVENT_B", data)

        def cascade_b(data):
            call_count["B"] += 1
            bus.publish("EVENT_A", data)

        bus.subscribe("EVENT_A", cascade_a)
        bus.subscribe("EVENT_B", cascade_b)

        bus.publish("EVENT_A", {"payload": "test"})

        self.assertEqual(call_count["A"], 1, "[FAIL] Event A should only fire once.")
        self.assertEqual(call_count["B"], 1, "[FAIL] Event B should only fire once.")

    @patch("core.logger")
    def test_lore_manifest_bedrock_protection(self, mock_logger):
        """Proves the Manifest physically refuses to overwrite core system weights."""
        manifest = LoreManifest(data_dir="/tmp/dummy")
        manifest.inject("system_prompts", {"hacked": True})

        manifest.save("system_prompts")

        mock_logger.error.assert_called_with(
            unittest.mock.ANY
        )
        error_msg = mock_logger.error.call_args[0][0]
        self.assertIn("[ARTICLE 11 VIOLATION]", error_msg)
        self.assertIn("system_prompts.json", error_msg)

    @patch("core.ux")
    def test_observer_judgment_states(self, mock_ux):
        """Proves TheObserver correctly maps latency deltas to behavioral judgments."""
        mock_ux.side_effect = lambda cat, key, default=None: default
        obs = TheObserver()

        self.assertEqual(obs.pass_judgment(0.0001, 0.0001), "Dormant.")

        self.assertEqual(obs.pass_judgment(0.05, 0.4), "High Efficiency.")

        judgment_load = obs.pass_judgment(0.1, 10.0)
        self.assertIn(judgment_load, ["High Cognitive Load.", "obs_fog", "obs_degraded", "obs_ponderous"])

        self.assertEqual(obs.pass_judgment(9.0, 1.0), "System Sluggish.")

    def test_cybernetic_governor_exhaustion_coupling(self):
        """Proves the Governor shifts topological order when user exhaustion crosses the boundary."""
        gov = CyberneticGovernor()

        beth = gov.calculate_coupling(phi=0.5, resonance_delta=0.1, user_exhaustion=0.3)
        self.assertEqual(gov.order, 1, "[FAIL] Governor should remain in Order 1 at low exhaustion.")
        self.assertAlmostEqual(beth, 0.3, places=2)

        beth_exhausted = gov.calculate_coupling(phi=0.1, resonance_delta=0.0, user_exhaustion=0.9)
        self.assertEqual(gov.order, 2, "[FAIL] Governor MUST shift to Order 2 when exhaustion > 0.8.")
        self.assertAlmostEqual(beth_exhausted, 0.33, places=2)
        self.assertEqual(gov.get_policy_shift(), "CO_REGULATION")

    @patch("core.ux")
    def test_archetype_arbiter_lockdown_override(self, mock_ux):
        """Proves the Council's Martial Law mandate overwrites standard physics lenses."""
        mock_ux.side_effect = lambda cat, key, default=None: default
        mandates = [{"type": "LOCKDOWN"}]

        lens, source, msg = ArchetypeArbiter.arbitrate(
            physics_lens="BENEDICT",
            soul_archetype="MERCY",
            council_mandates=mandates
        )

        self.assertEqual(lens, "THE CENSOR")
        self.assertEqual(source, "COUNCIL")
        self.assertEqual(msg, "Martial Law.")


if __name__ == '__main__':
    unittest.main()
