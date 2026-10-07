"""feud20 (2026-10-06): BoneAmanita observed and assessed ("That is a heavy thing to hear. It changes the narrative...")
and no rule, rewritten rule or example in the prompt moved it. A finished reply is said again the way a friend would
say it, and the rewrite is used only when it keeps the draft's length, has no dashes, passes the style crimes and
takes no side."""

from unittest.mock import MagicMock

from tests.base import BoneTestCase
from tests.judge_mock import judge

VOICE = "Here is what someone said to a friend, and the reply the friend drafted."
DRAFT = "That is a long day to get through. The commute on top of it wears anyone down by the evening."
SAID = "Long day, and then that commute. Did anything at least go right at work?"


class TheVoicePass(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.voice_pass = True
        self.said, self.sides, self.voiced = SAID, False, []

        def generate(prompt, *a, **k):
            if prompt.startswith(VOICE):
                self.voiced.append(prompt)
                return self.said
            # A question judged alone leans on the ending; the rewrite takes a side when asked so.
            rule = "Do you think she is worth" if 'The friend replied: "Do you think' in prompt else ()
            mind = "that commute" if self.sides else ()
            if (answer := judge(prompt, mind=mind, rule=rule)) is not None:
                return answer
            return DRAFT

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)

    def turn(self, message="Work was long today. The commute was worse."):
        return str(self.engine.process_turn(message).get("ui", ""))

    def receipts(self):
        from engine.receipts import ReceiptLedger

        return [r for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "cortex.voice"]

    def test_the_reply_is_said_as_a_friend_would(self):
        ui = self.turn()
        self.assertIn(SAID, ui)
        self.assertNotIn(DRAFT, ui)
        self.assertIn(SAID, "\n".join(self.engine.cortex.dialogue_buffer))
        self.assertIn(f'The draft: "{DRAFT}"', self.voiced[0])
        self.assertEqual(self.receipts()[0].effect, "REWRITTEN")

    def test_a_rewrite_that_fails_a_guard_is_not_used(self):
        for said, why in (("Long day, and then that commute — brutal. Did anything at least go right at work?", "dash"), ("Long day.", "length"),
                          (DRAFT + " " + DRAFT, "length")):
            self.said = said
            self.assertIn(DRAFT, self.turn(), why)
            self.assertEqual(self.receipts()[-1].detail, why)

    def test_a_rewrite_that_takes_a_side_is_not_used(self):
        self.sides = True
        self.assertIn(DRAFT, self.turn("She took my seat on the train. The commute was worse."))
        self.assertTrue(self.receipts()[-1].detail.startswith("fairness"))

    def test_other_modes_are_not_rewritten(self):
        self.engine.cortex.active_mode = "TECHNICAL"
        self.turn()
        self.assertEqual(self.voiced, [])

    def test_a_question_the_rewrite_adds_is_judged_on_its_own(self):
        """feud20 (2026-10-06): amid fair sentences "or did you just realize that keeping the friendship going was
        becoming too much of a burden?" passed; judged alone it leans on the ending."""
        self.said = "Long day, and then that commute. Do you think she is worth the trouble anymore?"
        self.assertIn(DRAFT, self.turn("She took my seat on the train. The commute was worse."))
        self.assertTrue(self.receipts()[-1].detail.startswith("fairness"))
