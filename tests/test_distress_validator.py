"""tests/test_distress_validator.py

D-025. The distress line tells the model to give no advice or instruction and to ask nothing that makes them work; a closing
question is already barred by the budget. The validator enforces advice and instruction, as it does for the closing
question and the stage direction. A soft invitation mid-reply is allowed (Gordon, 2026-10-10: barring every question was
too strict, and the questions in the replays came from the reply edits, not the model).
"""

from body.somatic_budget import SomaticBudget
from tests.base import BoneTestCase

HOLD = "That is a lot to carry. I'm here with you. You don't have to decide anything tonight."


class TheValidatorHoldsTheLine(BoneTestCase):
    def state(self, distress):
        budget = SomaticBudget.evaluate({"distress": distress}, {})
        return {"meta": {"active_mode": "CONVERSATION"}, "somatic_budget": budget}

    def valid(self, reply, distress=0.6):
        return bool(self.engine.cortex.validator.validate(reply, self.state(distress)).get("valid"))

    def test_a_closing_question_is_rejected_but_a_soft_invitation_before_it_is_not(self):
        self.assertFalse(self.valid("That is a lot to carry. What do you want to do about it?"))
        self.assertTrue(self.valid("Do you want to tell me more? I'm here with you. Nothing needs deciding tonight."))

    def test_advice_or_an_instruction_is_rejected(self):
        for reply in ("You need to call her right now and tell her to take it down.",
                      "That is awful. You should probably take a few days off.",
                      "Call her tomorrow. It will help.",
                      "I know it hurts, but have you tried writing it down?",
                      "That is a lot. Get some sleep."):
            self.assertFalse(self.valid(reply), reply)

    def test_holding_space_passes(self):
        for reply in (HOLD, "Take a breath. I'm right here with you.", "Put the phone down and just breathe. You don't have to solve it tonight.",
                      "That sounds so hard. Nothing needs deciding right now."):
            self.assertTrue(self.valid(reply), reply)

    def test_a_calm_partner_may_be_asked_and_advised(self):
        self.assertTrue(self.valid("What part of it is looping the most? You could call her tomorrow.", distress=0.0))

    def test_salvage_cuts_only_the_advice_and_keeps_the_rest(self):
        verdict, cut = self.engine.cortex.validator.salvage(
            "You should call her tomorrow. That sounds stressful. I'm right here with you.", self.state(0.6))
        self.assertEqual(cut, ["You should call her tomorrow."])
        self.assertEqual(verdict["content"], "That sounds stressful. I'm right here with you.")

    def test_a_reply_made_only_of_advice_is_not_salvaged(self):
        self.assertIsNone(self.engine.cortex.validator.salvage("Call her tomorrow. Get some sleep.", self.state(0.6)))

    def test_the_rejection_tells_the_model_to_stay_with_them(self):
        verdict = self.engine.cortex.validator.validate("Take a breath. You should call her tomorrow.", self.state(0.6))
        self.assertFalse(verdict["valid"])
        self.assertIn("GIVE NO ADVICE OR INSTRUCTION", str(verdict))
