"""tests/test_distress_length.py

D-027. The distress budget capped sentences and not words, so on qwen3.5:9b three long sentences passed: 72 words in distress
mode against gemma4:12b's 26. A person in distress now gets a word cap (WORD_CAP_DISTRESSED, 45): it is in the contract, it
bounds max_tokens, and a longer draft is sent back with the cap named; the last draft keeps the sentences that fit.
"""

from unittest.mock import MagicMock

from body.somatic_budget import SomaticBudget
from engine.gate.distress import DistressReader
from tests.base import BoneTestCase

LONG = ("She is crying because she lost her job, and you stayed on the phone with her for two hours while she needed someone, "
        "so that part makes sense without any extra words to explain why you did it. You don't owe anyone a feeling about "
        "that, and the way you handled it says something steady about the kind of friend you are right now.")
LONG_ONE = ("She is crying because she lost her job, and you stayed on the phone with her for two hours while she needed someone, "
            "so that part makes sense without any extra words to explain why you did it and why it was not a mistake at all in the end.")
SHORT = "That was a lot to hold for two hours. I'm here with you."
MESSAGE = "I can't stop shaking. Everything is falling apart."


def words(text):
    return len(text.split())


class TheBudgetHasAWordCap(BoneTestCase):
    def test_distress_caps_words(self):
        self.assertIsNone(SomaticBudget.evaluate({"distress": 0.1}, {}).word_cap)
        self.assertEqual(SomaticBudget.evaluate({"distress": 0.6}, {}).word_cap, 45)

    def test_the_lower_cap_wins_when_the_person_is_flagging_too(self):
        budget = SomaticBudget.evaluate({"distress": 0.6, "exhaustion": 0.9}, {})
        self.assertEqual(budget.word_cap, 45)

    def test_the_contract_says_it_only_in_distress(self):
        self.assertIn("about 45 words", self.contract(0.6))
        self.assertNotIn("about 45 words", self.contract(0.1))

    def contract(self, distress):
        budget = SomaticBudget.evaluate({"distress": distress, "exhaustion": 0.1}, {"atp_pool": 100.0})
        state = {"somatic_budget": budget, "meta": {"active_mode": "CONVERSATION"}}
        return self.engine.cortex.composer.compose(state, MESSAGE)


class TheReplyKeepsToIt(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.distress, self.replies, self.prompts = "8", [LONG, SHORT], []

        def generate(prompt, *a, **k):
            if "Rate how distressed" in prompt:
                return self.distress
            if "=== PARTNER INPUT ===" in prompt:
                self.prompts.append(prompt)
                return self.replies[min(len(self.prompts) - 1, len(self.replies) - 1)]
            return "ASSESS"

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)
        self.engine.shared_lattice.distress_reader = DistressReader(self.engine.cortex.llm)

    def ui(self):
        return str(self.engine.process_turn(MESSAGE).get("ui", ""))

    def test_a_long_draft_in_distress_is_cut_to_whole_sentences_with_no_redraft(self):
        ui = self.ui()
        self.assertIn("She is crying because she lost her job", ui.split("You don't owe")[0])
        self.assertNotIn("You don't owe anyone a feeling", ui)
        self.assertEqual(len(self.prompts), 1, "a draft that can be trimmed is not redone")
        from engine.receipts import ReceiptLedger

        cuts = [r for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "cortex.salvage"]
        self.assertTrue(any("word cap" in r.detail for r in cuts))

    def test_a_first_sentence_that_is_itself_too_long_goes_back_with_the_cap_named(self):
        self.replies = [LONG_ONE, SHORT]
        ui = self.ui()
        self.assertIn(SHORT, ui)
        self.assertGreaterEqual(len(self.prompts), 2)
        self.assertIn("about 45 words", self.prompts[1])
        self.assertIn("for someone in distress", self.prompts[1])

    def test_when_the_only_sentence_is_too_long_the_last_draft_keeps_it_whole(self):
        self.replies = [LONG_ONE]
        self.assertIn("She is crying because", self.ui())

    def test_a_calm_person_gets_the_long_reply(self):
        self.distress = "0"
        self.replies = [LONG]
        self.assertIn("You don't owe anyone a feeling", str(self.engine.process_turn("Tell me about that day.").get("ui", "")))
