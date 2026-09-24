"""tests/test_whimsy.py

The Ministry's asides are terminal chrome: they may be dry about the engine's
own drafts, never about the person, and never while the person is struggling.
"""

import unittest
from types import SimpleNamespace

from engine.receipts import ReceiptLedger, issue
from main import BoneAmanita
from mechanics.whimsy import aside, ministry_aside, sarcasm_level
from tests.base import BoneTestCase

LINES = {"mild": ["mild {dept}"], "dry": ["dry {dept}"], "withering": ["withering {dept}"], "absurd": ["absurd {dept}"]}
WHIMSY = SimpleNamespace(ABSURDITY_CONSTANT=42, MAX_SARCASM_LEVEL=11, DEPARTMENT_NAME="The Ministry of Tests")


class Asides(unittest.TestCase):
    def test_dryness_follows_ros_and_stops_at_the_cap(self):
        self.assertEqual(sarcasm_level(0, 11), 0)
        self.assertEqual(sarcasm_level(90, 11), 10)
        self.assertEqual(sarcasm_level(90, 3), 3)
        self.assertEqual(sarcasm_level(250, 11), 11)

    def test_a_rejected_draft_earns_an_aside_in_its_band(self):
        self.assertEqual(aside(5, 10, 0.1, True, WHIMSY, LINES), "mild The Ministry of Tests")
        self.assertEqual(aside(5, 50, 0.1, True, WHIMSY, LINES), "dry The Ministry of Tests")
        self.assertEqual(aside(5, 90, 0.1, True, WHIMSY, LINES), "withering The Ministry of Tests")

    def test_no_rejected_draft_means_nothing_to_say(self):
        self.assertIsNone(aside(5, 90, 0.1, False, WHIMSY, LINES))

    def test_a_cap_of_zero_keeps_every_draft_aside_quiet(self):
        whimsy = SimpleNamespace(**{**vars(WHIMSY), "MAX_SARCASM_LEVEL": 0})
        self.assertIsNone(aside(5, 90, 0.1, True, whimsy, LINES))

    def test_the_absurd_line_comes_every_absurdity_constant_turns(self):
        self.assertEqual(aside(42, 0, 0.1, False, WHIMSY, LINES), "absurd The Ministry of Tests")
        self.assertEqual(aside(84, 0, 0.1, False, WHIMSY, LINES), "absurd The Ministry of Tests")
        self.assertIsNone(aside(43, 0, 0.1, False, WHIMSY, LINES))

    def test_a_tiring_or_flagging_person_gets_no_whimsy_at_all(self):
        self.assertIsNone(aside(5, 90, 0.5, True, WHIMSY, LINES))
        self.assertIsNone(aside(42, 0, 0.8, False, WHIMSY, LINES))


class ShippedLines(unittest.TestCase):
    def test_every_pool_exists_and_formats(self):
        from engine.core import LoreManifest

        lines = LoreManifest.get_instance().get("ux_strings", "whimsy_asides")
        for pool in ("mild", "dry", "withering", "absurd"):
            self.assertTrue(lines[pool], pool)
            for line in lines[pool]:
                line.format(dept="X")


class RealEngine(BoneTestCase):
    def test_a_real_re_asked_receipt_reaches_the_terminal_line(self):
        engine = BoneAmanita({})
        engine.bio.mito.state.ros_buildup = 50.0
        engine.shared_lattice.u.E_u = 0.1
        ReceiptLedger.get_instance().begin_turn()
        issue("cortex.somatic", effect="re-asked", result_count=40)
        self.assertIsNotNone(ministry_aside(engine, 5))
        engine.shared_lattice.u.E_u = 0.9
        self.assertIsNone(ministry_aside(engine, 5))


if __name__ == "__main__":
    unittest.main()
