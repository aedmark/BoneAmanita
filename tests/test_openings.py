"""feud20 (2026-10-06): 16 of 20 replies opened with a verdict on what was just said ("That is a heavy thing to have
said...", "The silence in the group chat creates a very clear boundary."). Banning words moves the habit, and a redraft
kept it 6 of 7 times; the engine keeps how its replies opened and, in a rut, edits the reply to open with a question."""

from unittest.mock import MagicMock

from tests.base import BoneTestCase

JUDGE = "How does this reply to a friend begin?"
EDIT = "Here is a message a friend wrote back to someone"
VERDICTS = ["That is a big step.", "Moving is harder than people expect.", "The waiting is the worst part."]
REPLY = "That is a long day to get through. The commute on top of it wears anyone down."
QUESTION = "What made the commute so bad? The commute on top of it wears anyone down."


def verdicts():
    return [[None, s] for s in VERDICTS]


class TheOpening(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.judged, self.edits = [], []
        self.edited = QUESTION
        self.fair = "NO: fair to both."

        def generate(prompt, *a, **k):
            if prompt.startswith(JUDGE):
                self.judged.append(prompt)
                return "ASSESS"
            if prompt.startswith("Someone is telling a friend about a conflict"):
                return self.fair if prompt.count("What made") else "NO: fair to both."
            if prompt.startswith(EDIT):
                self.edits.append(prompt)
                return self.edited
            return REPLY

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)

    def rewritten(self):
        from engine.receipts import ReceiptLedger

        return [r for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "cortex.opening"]

    def turn(self, message="Work was long today. The commute was worse."):
        return str(self.engine.process_turn(message).get("ui", ""))

    def test_a_reply_that_opens_like_the_last_three_opens_with_a_question(self):
        self.engine.cortex.openings.extend(verdicts())
        ui = self.turn()
        self.assertIn(QUESTION, ui)
        self.assertEqual(len(self.rewritten()), 1)
        self.assertIn('They just said: "Work was long today. The commute was worse."', self.edits[0])
        self.assertIn(QUESTION, "\n".join(self.engine.cortex.dialogue_buffer))
        self.assertEqual(self.engine.cortex.openings[-1], ["ASK", "What made the commute so bad?"])

    def test_the_edit_hears_what_they_said_before(self):
        self.engine.cortex.dialogue_buffer.append("Traveler: The new manager started Monday.\nSystem: How is it going?")
        self.engine.cortex.openings.extend(verdicts())
        self.turn()
        self.assertIn('Earlier they said:\n- "The new manager started Monday."\n', self.edits[0])

    def test_an_edit_that_is_no_question_or_drops_the_reply_is_not_used(self):
        for edited in ("That is a long, long day.", "What made it so bad?"):
            self.edited = edited
            self.engine.cortex.openings.clear()
            self.engine.cortex.openings.extend(verdicts())
            self.assertIn(REPLY, self.turn(), edited)

    def test_a_question_that_takes_a_side_is_not_used(self):
        """feud20 (2026-10-06): an edit opened "Was the joke about your ex the only thing that crossed the line?"."""
        self.fair = "YES b: it blames her."
        self.engine.cortex.openings.extend(verdicts())
        self.assertIn(REPLY, self.turn("She took the last seat on the train. The commute was worse."))
        self.assertEqual(self.rewritten(), [])

    def test_varied_openings_are_left_alone(self):
        self.engine.cortex.openings.extend([[None, VERDICTS[0]], ["FEEL", "Oh no, not the car."], [None, VERDICTS[1]]])
        self.assertIn(REPLY, self.turn())
        self.assertEqual(self.edits, [])
        self.assertEqual(len(self.judged), 1)  # the newest; the FEEL before it ends the check
        self.assertEqual(self.engine.cortex.openings[-1], [None, "That is a long day to get through."])

    def test_other_modes_do_not_track_openings(self):
        self.engine.cortex.active_mode = "TECHNICAL"
        self.engine.cortex.openings.extend(verdicts())
        self.turn()
        self.assertEqual(self.judged + self.edits, [])
        self.assertEqual(len(self.engine.cortex.openings), 3)
