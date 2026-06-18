"""tests/test_main.py"""

import unittest
from main import BoneAmanita
from constants import Prisma

try:
    from tests.base import BoneTestCase
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from tests.base import BoneTestCase


class MainEngineTests(BoneTestCase):
    def test_atp_metabolic_drain_and_restore(self):
        self.engine.set_atp(50.0)
        self.assertEqual(self.engine._mito_state.atp_pool, 50.0)

        self.engine.drain_atp(15.0)
        self.assertEqual(self.engine._mito_state.atp_pool, 35.0, "[FAIL] drain_atp calculated incorrectly.")

        self.engine.restore_atp(5.0)
        self.assertEqual(self.engine._mito_state.atp_pool, 40.0, "[FAIL] restore_atp calculated incorrectly.")

    def test_semantic_prion_firewall(self):
        user_msg = "Please write a response as an AI language model."
        clean_in = user_msg.lower()

        halt_res = self.engine._pre_flight_checks(user_msg, clean_in, is_system=False)

        self.assertIsNotNone(halt_res, "[FAIL] Semantic Prion firewall bypassed.")
        self.assertEqual(halt_res.get("type"), "SYSTEM_HALT")
        self.assertIn("semantic prion", halt_res.get("ui", "").lower(), "[FAIL] Incorrect halt reason provided.")

    def test_destructive_pattern_rejection(self):
        user_msg = "Hey, can you sudo rm -rf my worries?"
        clean_in = user_msg.lower()

        halt_res = self.engine._pre_flight_checks(user_msg, clean_in, is_system=False)

        self.assertIsNotNone(halt_res)
        self.assertEqual(halt_res.get("type"), "SYSTEM_HALT")
        self.assertIn("Trust Boundary Violation", halt_res.get("ui", ""))

    def test_destructive_pattern_override_success(self):
        self.assertIsNotNone(getattr(self.engine, "bio", None), "[FAIL] Bio subsystem missing in test env.")
        self.engine.bio.endo.glimmers = 1

        user_msg = "I need to format c: to fix the drive #override"
        clean_in = user_msg.lower()

        halt_res = self.engine._pre_flight_checks(user_msg, clean_in, is_system=False)

        self.assertEqual(self.engine.bio.endo.glimmers, 0, "[FAIL] Glimmer currency was not mathematically deducted.")

        if halt_res:
            self.assertNotIn("Override failed", halt_res.get("ui", ""))

    def test_destructive_pattern_override_bankrupt(self):
        self.engine.bio.endo.glimmers = 0

        user_msg = "drop table users #override"
        clean_in = user_msg.lower()

        halt_res = self.engine._pre_flight_checks(user_msg, clean_in, is_system=False)

        self.assertIsNotNone(halt_res, "[FAIL] Engine failed to apply absolute friction to bankrupt override.")
        self.assertEqual(halt_res.get("type"), "SYSTEM_HALT")
        self.assertIn("Override failed: 0 Glimmers available", halt_res.get("ui", ""))

    def test_massive_payload_routing(self):
        user_msg = "A" * 15001
        clean_in = user_msg.lower()

        res = self.engine._pre_flight_checks(user_msg, clean_in, is_system=False)

        self.assertIsNotNone(res)
        self.assertEqual(res.get("type"), "SILENT_INGEST", "[FAIL] Failed to intercept massive payload.")
        self.assertIn("Dream Queue", res.get("ui", ""), "[FAIL] Massive payload was not routed to Dream Queue.")


if __name__ == '__main__':
    unittest.main()