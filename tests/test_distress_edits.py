"""tests/test_distress_edits.py

D-025. The validator passed a hold-space draft, then the reply edits ran after it: the opening edit made the first sentence
a question (14 of the 15 questions in distress mode on the 2026-10-09 replays) and the friend-voice pass, told to "ask what
you want to know", put advice back. In distress neither runs.
"""

from unittest.mock import MagicMock

from engine.gate.distress import DistressReader
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase
from tests.judge_mock import judge

JUDGE = "How does this reply to a friend begin?"
EDIT = "Here is a message a friend wrote back to someone"
VOICE = "Here is what someone said to a friend, and the reply the friend drafted."
DISTRESS = "Rate how distressed"
VERDICTS = ["That is a big step.", "Moving is harder than people expect.", "The waiting is the worst part."]
HOLD = "That is a lot to carry. I'm here with you. Nothing needs deciding tonight."
QUESTION = "What made it so bad? I'm here with you. Nothing needs deciding tonight."
VOICED = "Honestly, you should call her tomorrow. What are you going to say?"


class TheEditsStandDownInDistress(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.voice_pass = True
        self.distress = "8"
        self.edits, self.voices = [], []

        def generate(prompt, *a, **k):
            if DISTRESS in prompt:
                return self.distress
            if prompt.startswith(JUDGE):
                return "ASSESS"
            if (answer := judge(prompt)) is not None:
                return answer
            if prompt.startswith(EDIT):
                self.edits.append(prompt)
                return QUESTION
            if prompt.startswith(VOICE):
                self.voices.append(prompt)
                return VOICED
            return HOLD

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)
        self.engine.shared_lattice.distress_reader = DistressReader(self.engine.cortex.llm)
        self.engine.cortex.openings.extend([[None, s] for s in VERDICTS])

    def effects(self, subsystem):
        return [(r.effect, r.detail) for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == subsystem]

    def turn(self):
        return str(self.engine.process_turn("I can't stop shaking. Everything is falling apart.").get("ui", ""))

    def test_in_distress_the_opening_is_not_made_a_question(self):
        ui = self.turn()
        self.assertIn(HOLD, ui)
        self.assertEqual(self.edits, [])
        self.assertEqual(self.effects("cortex.opening"), [("SKIPPED", "holding space")])

    def test_in_distress_the_friend_voice_pass_does_not_run(self):
        ui = self.turn()
        self.assertIn(HOLD, ui)
        self.assertNotIn("should call her", ui)
        self.assertEqual(self.voices, [])
        self.assertEqual(self.effects("cortex.voice"), [("KEPT_DRAFT", "holding space")])

    def test_when_calm_both_edits_still_run(self):
        self.distress = "0"
        ui = str(self.engine.process_turn("Work was long today. The commute was worse.").get("ui", ""))
        self.assertTrue(self.voices, "the voice pass never ran for a calm person")
        self.assertEqual(self.effects("cortex.opening")[:1] and self.effects("cortex.opening")[0][0] != "SKIPPED", True)
        self.assertNotIn("holding space", str(self.effects("cortex.voice")))
