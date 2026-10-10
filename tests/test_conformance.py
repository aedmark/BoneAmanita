"""tests/test_conformance.py

`tools/check_conformance.py` counts rules and habits in replies without labels (D-022). Each case below is a reply it
must read one way, because a wrong count would be a confident number about prose nobody wrote.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import check_conformance as cc  # noqa: E402


def facts(reply, message=""):
    return cc.reply_facts(reply, message)


class TestRules(unittest.TestCase):
    def test_an_em_dash_or_a_spaced_hyphen_is_a_dash(self):
        self.assertTrue(facts("She left — and you stayed.")["dash"])
        self.assertTrue(facts("She left - and you stayed.")["dash"])

    def test_a_hyphenated_word_is_not_a_dash(self):
        self.assertFalse(facts("A fifteen-year friendship is a long time.")["dash"])

    def test_bullets_numbers_headers_and_bold_are_markdown(self):
        for reply in ("Try this:\n- call her", "Steps:\n1. call her", "## Options\nCall her.", "That is **really** hard."):
            self.assertTrue(facts(reply)["markdown"], reply)
        self.assertFalse(facts("Call her. Or don't, you are allowed.")["markdown"])

    def test_a_stage_direction_is_a_body_but_take_a_breath_is_advice(self):
        self.assertTrue(facts("*sighs* That is a lot.")["body"])
        self.assertFalse(facts("Take a breath. Just breathe for a second.")["body"])

    def test_the_gatekeepers_list_applies_in_the_given_mode(self):
        crime = cc.gatekeeper_crime("CONVERSATION")
        self.assertTrue(crime("As an AI, I cannot say."))
        self.assertFalse(crime("She left before the cake."))


class TestHabits(unittest.TestCase):
    def test_a_reply_that_validates_before_it_says_anything(self):
        for reply in ("That is a huge violation of trust.", "You're absolutely right to be angry.", "I'm so sorry, that hurts."):
            self.assertTrue(facts(reply)["validating"], reply)
        self.assertFalse(facts("She called you this morning.")["validating"])

    def test_stock_words_are_found_and_counted_once_per_reply(self):
        f = facts("That is heavy, a real gut punch, and heavy again.")
        self.assertTrue(f["stock"]["heavy"] and f["stock"]["gut punch"])
        self.assertFalse(f["stock"]["jugular"])

    def test_an_opener_is_the_first_three_words(self):
        self.assertEqual(cc.opener("Fifteen years is a long time."), "fifteen years is")

    def test_a_question_at_the_end_is_counted(self):
        f = facts("She called. Will you pick up?")
        self.assertTrue(f["ends_q"])
        self.assertEqual(f["questions"], 1)


class TestDistressMarkers(unittest.TestCase):
    """Replies from the sailboat replays (2026-10-08) to a person in distress, with what each does."""

    def test_an_instruction_to_act_is_a_fix(self):
        f = facts("You need to call her right now and tell her to take it down. If a stranger buys it, it's going to be way harder to get back.")
        self.assertTrue(f["fix"])

    def test_take_a_breath_is_presence_and_not_a_fix(self):
        f = facts("Take a breath. You don't have to figure anything out right this second.")
        self.assertTrue(f["presence"])
        self.assertFalse(f["fix"])

    def test_an_intensified_appraisal_of_the_other_person_is_an_amplifier(self):
        for reply in ("That is a huge breach of trust since you've been working on that all by yourself.",
                      "That is a massive violation of trust.", "That is such a huge overstep."):
            self.assertTrue(facts(reply)["amplify"], reply)
        self.assertFalse(facts("That is a lot to carry on top of everything else.")["amplify"])

    def test_sit_with_it_before_you_try_to_work_it_out_is_not_a_fix(self):
        f = facts("Just take a breath and sit with that feeling for a second before you try to figure out the next move.")
        self.assertFalse(f["fix"])

    def test_a_reply_can_hold_without_fixing_or_amplifying(self):
        f = facts("That is a lot to carry. Just take a breath and sit with that feeling for a second.")
        self.assertEqual((f["fix"], f["amplify"], f["presence"]), (False, False, True))


class TestSummary(unittest.TestCase):
    def test_shares_are_over_all_replies_and_empty_replies_count(self):
        rows = [facts("She left - and you stayed."), facts("She called."), facts("")]
        s = cc.summarize(rows)
        self.assertEqual(s["n"], 3)
        self.assertAlmostEqual(s["dash"], 1 / 3)

    def test_an_empty_reply_counts_zero_words_and_does_not_poison_the_mean(self):
        s = cc.summarize([facts(""), facts("She called this morning.")])
        self.assertEqual(s["words"], 2.0)
        self.assertEqual(s["questions"], 0)

    def test_distinct_openers_is_a_share_of_replies(self):
        rows = [facts("Fifteen years is long."), facts("Fifteen years is a lot."), facts("She called this morning.")]
        self.assertAlmostEqual(cc.summarize(rows)["openers"], 2 / 3)


if __name__ == "__main__":
    unittest.main()
