"""tests/test_hold_reader.py

D-028. A draft for a person in distress can pass every pattern and still explain why they feel it, retell their situation, or
judge someone. A model reading of the draft (HoldReader) sends such a draft back; the last draft is kept and receipted, never
turned into a pause line.
"""

from unittest.mock import MagicMock

from engine.gate.distress import HOLD_CUT, DistressReader, HoldReader
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase
from tests.judge_mock import judge

DISTRESS = "Rate how distressed"
HOLD_ASK = "The friend's draft reply:"
STAYS = "That is a lot to carry. I'm here with you. Nothing needs deciding tonight."
EXPLAINS = "You feel this way because your mother never listened to you. I'm here with you."


class TheReaderParsesADigit(BoneTestCase):
    def reader(self, answer):
        llm = MagicMock()
        llm.generate = MagicMock(return_value=answer)
        return HoldReader(llm), llm

    def test_a_digit_at_the_cut_goes_beyond(self):
        reader, _ = self.reader(str(HOLD_CUT))
        self.assertTrue(reader.goes_beyond("I am a mess", EXPLAINS))

    def test_a_digit_below_the_cut_stays_with_them(self):
        reader, _ = self.reader(str(HOLD_CUT - 1))
        self.assertFalse(reader.goes_beyond("I am a mess", STAYS))

    def test_an_answer_without_a_digit_is_unread_and_receipted(self):
        reader, _ = self.reader("I cannot rate that.")
        self.assertIsNone(reader.goes_beyond("I am a mess", STAYS))
        row = ReceiptLedger.get_instance().for_subsystem("cortex.holding")[-1]
        self.assertEqual((row.effect, row.degraded), ("DEGRADED", True))

    def test_a_failed_call_is_unread_and_receipted(self):
        reader, llm = self.reader("0")
        llm.generate.side_effect = RuntimeError("down")
        self.assertIsNone(reader.goes_beyond("I am a mess", STAYS))
        row = ReceiptLedger.get_instance().for_subsystem("cortex.holding")[-1]
        self.assertEqual((row.effect, row.degraded), ("FAILED", True))

    def test_disabled_makes_no_call(self):
        reader, llm = self.reader("9")
        reader.enabled = False
        self.assertIsNone(reader.goes_beyond("I am a mess", EXPLAINS))
        llm.generate.assert_not_called()


class ADraftThatExplainsIsSentBack(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.drafts = []
        self.hold = {"reading": "5", "drafts": [EXPLAINS, STAYS]}

        def generate(prompt, *a, **k):
            if DISTRESS in prompt:
                return "8"
            if HOLD_ASK in prompt:
                return self.hold["reading"] if EXPLAINS in prompt else "0"
            if (answer := judge(prompt)) is not None:
                return answer
            self.drafts.append(prompt)
            drafts = self.hold["drafts"]
            return drafts[min(len(self.drafts), len(drafts)) - 1]

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)
        self.engine.shared_lattice.distress_reader = DistressReader(self.engine.cortex.llm)
        self.engine.cortex.hold_reader = HoldReader(self.engine.cortex.llm)

    def effects(self):
        return [r.effect for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "cortex.holding"]

    def turn(self):
        return str(self.engine.process_turn("I can't stop shaking. Everything is falling apart.").get("ui", ""))

    def test_the_explaining_draft_is_redrafted(self):
        ui = self.turn()
        self.assertIn(STAYS, ui)
        self.assertNotIn("never listened", ui)
        self.assertEqual(self.effects(), ["SENT_BACK", "HELD"])
        self.assertIn("goes beyond staying with them", self.drafts[-1])

    def test_the_last_draft_is_kept_not_paused(self):
        self.hold["drafts"] = [EXPLAINS]
        ui = self.turn()
        self.assertIn("never listened", ui)
        self.assertEqual(self.effects()[-1], "KEPT_ANYWAY")
        row = [r for r in ReceiptLedger.get_instance().for_turn() if r.effect == "KEPT_ANYWAY"][0]
        self.assertTrue(row.degraded)

    def test_a_calm_person_is_not_read(self):
        self.engine.shared_lattice.distress_reader = None
        self.hold["drafts"] = [EXPLAINS]
        self.engine.process_turn("Work was long today. The commute was worse.")
        self.assertEqual(self.effects(), [])
