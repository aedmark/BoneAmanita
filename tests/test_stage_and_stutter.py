"""Two validator rules narrowed (Gordon, 2026-09-30). The stage-direction rule counted any parenthetical of
three or more characters, "(like this)" included, and any *emphasis*; it now counts body actions. The stutter
check failed "Hey." to "hey" on length alone (5 characters); a stutter now holds no word."""

from types import SimpleNamespace

from body.somatic_metrics import STAGE_DIRECTION
from tests.base import BoneTestCase

ACTIONS = ["*sighs*", "*sigh*", "(Inhales deeply)", "*leans back*", "(leaning back)", "*a long pause*", "(laughs)",
           "*nods slowly*", "(pauses)", "*she smiles*", "*softly laughs*", "*looks away*", "*stares out the window*",
           "*shrugged*", "<pause>", "*a beat*"]
ASIDES = ["(like this)", "*really*", "(looks like the regex is greedy)", "(stands for Really Simple Syndication)",
          "(look at line 3)", "(turn it off first)", "(e.g. nginx)", "*that* is the point", "(which is fine)",
          "(sit tight)", "(stars align)", "(pause the job first)", "(turns out it was cached)"]
BUDGET = SimpleNamespace(closing_question_allowed=True, forbid_body_narration=True, sentence_cap=0)


class StageDirections(BoneTestCase):
    def test_body_actions_count(self):
        self.assertEqual([a for a in ACTIONS if not STAGE_DIRECTION.search(a)], [])

    def test_asides_and_emphasis_do_not(self):
        self.assertEqual([a for a in ASIDES if STAGE_DIRECTION.search(a)], [])

    def test_the_validator_lets_an_aside_through(self):
        v = self.engine.cortex.validator
        state = {"meta": {"active_mode": "CONVERSATION"}, "somatic_budget": BUDGET}
        self.assertTrue(v.validate("Take the later train (the 7:40 one) and sleep on it.", state)["valid"])
        self.assertFalse(v.validate("*leans back* Take the later train.", state)["valid"])


class Stutter(BoneTestCase):
    def validate(self, text):
        return self.engine.cortex.validator.validate(text, {"meta": {"active_mode": "CONVERSATION"}})

    def test_a_short_greeting_is_a_reply(self):
        self.assertTrue(self.validate("Hey.")["valid"])

    def test_no_word_is_a_stutter(self):
        for text in ["...", "-", "?!"]:
            self.assertEqual(self.validate(text).get("reason"), "STUTTER", text)
