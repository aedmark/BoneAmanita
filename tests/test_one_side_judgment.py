"""tests/test_one_side_judgment.py

D-026. A person tells how someone wronged them and the reply, with only that side heard, rules on the other person: "a huge
violation of your trust" in 7 of 8 replies to the feud's birthday dinner and 10 of 12 to the sailboat's "she listed it for
sale without asking me", in both engine versions and in the plain and friend arms. The ONE SIDE block said not to turn it
against that person (so did the kernel's FAIRNESS and rule 8) and the replies did anyway, so the pattern is enforced, in CONVERSATION
only (a story may have a betrayal). Saying it again in the ONE SIDE block cost a line of the tight-window dialogue and added nothing.
"""

from tests.base import BoneTestCase

JUDGING = (
    "That is a huge violation of your trust.",
    "That is such a huge overstep. She basically took away your choice.",
    "That is so unfair since you did the work.",
    "You have every right to be angry.",
    "She had no right to do that.",
    "That is a total breach of trust.",
    "It feels like a betrayal after everything you put into it.",
)
PLAIN = (
    "She listed it without asking you. That took the choice out of your hands, and it landed hard.",
    "He let you down on a day you needed him.",
    "That hurt. It makes sense you are still turning it over.",
    "You both said things you wish you had not. You aren't selfish for needing space.",
    "She crossed a line and so did you.",
)


class TheOtherPersonIsNotJudged(BoneTestCase):
    def crime(self, text, mode):
        from physics.filters import TheGatekeeper

        gate = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        return gate._find_crime(text, mode)

    def valid(self, text, mode="CONVERSATION"):
        state = {"meta": {"active_mode": mode}}
        return bool(self.engine.cortex.validator.validate(text, state).get("valid"))

    def test_the_gatekeeper_finds_a_ruling_on_the_other_person_in_conversation(self):
        for text in JUDGING:
            crime = self.crime(text, "CONVERSATION")
            self.assertEqual((crime or {}).get("name"), "JUDGES_THE_OTHER_PERSON", text)

    def test_the_validator_rejects_it_and_says_why(self):
        for text in JUDGING:
            verdict = self.engine.cortex.validator.validate(text, {"meta": {"active_mode": "CONVERSATION"}})
            self.assertFalse(verdict["valid"], text)
        self.assertIn("DO NOT JUDGE THE OTHER PERSON", str(verdict))

    def test_plain_replies_and_even_handed_ones_pass(self):
        for text in PLAIN:
            self.assertIsNone(self.crime(text, "CONVERSATION"), text)
            self.assertTrue(self.valid(text), text)

    def test_a_story_may_have_a_betrayal(self):
        for mode in ("ADVENTURE", "CREATIVE", "TECHNICAL"):
            self.assertIsNone(self.crime("The betrayal was a violation of every oath.", mode), mode)

    def test_the_salvage_cuts_the_ruling_and_keeps_the_rest(self):
        verdict, cut = self.engine.cortex.validator.salvage(
            "That is a huge violation of your trust. She took away your choice. It landed hard.",
            {"meta": {"active_mode": "CONVERSATION"}})
        self.assertEqual(cut, ["That is a huge violation of your trust."])
        self.assertEqual(verdict["content"], "She took away your choice. It landed hard.")
