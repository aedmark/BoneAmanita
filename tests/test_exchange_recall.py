"""rescue20 (2026-10-05): the reply prompt holds the last 4096 characters of dialogue, about seven exchanges, and
the keeper's one fact a turn; what was said before that was gone. Each exchange is now embedded, and the closest
ones the recent dialogue no longer shows are handed back (EARLIER IN THIS CONVERSATION)."""

import copy
from unittest.mock import MagicMock, patch

from brain.composer import PromptComposer
from tests.base import BoneTestCase
from tests.test_halcyon_gate import ConceptEmbedder

TALK = [
    ("The lamp in the hall keeps flickering.", "Could be the bulb, or the switch."),
    ("We baked bread this morning.", "Fresh out of the oven is the best way to have it."),
    ("The river was high after the rain.", "The bridge must have been close to the water."),
]


class Exchanges(BoneTestCase):
    def commit(self, said, answered):
        from engine.gate.kernel import Gate

        seq, state = self.engine.store.state()
        gate = Gate(self.engine.boundary, copy.deepcopy(state), self.engine.gate_tools, self.engine.gate_invariants)
        self.engine.store.commit_cycle("t", gate.state, seq, gate.adjudicate(answered), answered,
                                       user_text=said, display=answered)

    def test_are_ranked_by_meaning_and_embedded_once(self):
        from engine.gate.recall import exchange_scores

        for said, answered in TALK:
            self.commit(said, answered)
        embedder = ConceptEmbedder()
        ranked = exchange_scores("Is it hungry? It hasn't eaten.", self.engine.store, embedder)
        self.assertEqual(ranked[0][1]["said"], "We baked bread this morning.")
        self.assertEqual(len(embedder.batches[-1]), 1 + len(TALK))
        exchange_scores("Which bridge?", self.engine.store, embedder)
        self.assertEqual(embedder.batches[-1], ["Which bridge?"])

    def test_none_on_the_hash_fallback(self):
        from engine.gate.recall import exchange_scores

        self.commit(*TALK[0])
        self.assertIsNone(exchange_scores("the lamp", self.engine.store, MagicMock(degraded=True)))


class TheEarlierBlock(BoneTestCase):
    FOUND = {"next_n": 10, "exchanges": [
        {"n": 8, "said": "In view.", "answered": "Seen.", "score": 0.9},
        {"n": 2, "said": "How long before you give up on a dog?", "answered": "There is no set time.", "score": 0.7},
    ]}

    def test_holds_only_what_the_recent_dialogue_does_not(self):
        block = PromptComposer._earlier_block(self.FOUND, ["Traveler: In view.\nSystem: Seen."])
        self.assertIn('8 turns ago, they said: "How long before you give up on a dog?"', block)
        self.assertIn("There is no set time.", block)
        self.assertNotIn("In view.", block)

    def test_is_empty_when_everything_is_in_view(self):
        found = {"next_n": 10, "exchanges": self.FOUND["exchanges"][:1]}
        self.assertEqual(PromptComposer._earlier_block(found, ["Traveler: In view.\nSystem: Seen."]), "")


class InTheReplyPrompt(BoneTestCase):
    def test_an_old_exchange_reaches_the_prompt(self):
        cortex = self.engine.cortex
        cortex.active_mode = "CONVERSATION"
        cortex.dspy_critic.enabled = False
        cortex.llm.generate = MagicMock(return_value="That sounds right.")
        with patch.object(type(cortex), "_recall_embedder", staticmethod(lambda: ConceptEmbedder())):
            cortex.llm.generate.return_value = "Fresh out of the oven is the best way to have it."
            self.engine.process_turn("We baked bread this morning.")
            cortex.llm.generate.return_value = "Could be the bulb."
            for i in range(3):  # the 4096-character window no longer holds the bread
                self.engine.process_turn(f"Lamp {i}: " + "The lamp in the hall keeps flickering. " * 40)
            self.engine.process_turn("Is it hungry? It has not eaten the bread.")
        prompt = [c.args[0] for c in cortex.llm.generate.call_args_list if "PARTNER INPUT" in str(c.args[0])][-1]
        self.assertIn("Is it hungry?", prompt.split("=== PARTNER INPUT ===")[1])
        self.assertIn("=== EARLIER IN THIS CONVERSATION ===", prompt)
        self.assertIn("We baked bread this morning.", prompt.split("=== RECENT DIALOGUE ===")[0])
