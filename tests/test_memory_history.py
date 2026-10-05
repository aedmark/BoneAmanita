"""rescue20 replay (2026-10-05): the keeper wrote pepper_fear_trigger "postman", then "squirrel" under the same key,
and pepper_behavior "still anxious and barks at everything", then "hid behind couch today"; each write erased the
last. A key written again now keeps what it held, and WHAT YOU REMEMBER shows it (Gordon's call: the engine keeps the
history, the keeper is not asked to judge)."""

import copy
from types import SimpleNamespace

from brain.composer import PromptComposer
from tests.base import BoneTestCase


class MemoryHistory(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.active_mode = "CONVERSATION"  # kept in the person's zone, not the story's

    def commit(self, line):
        from engine.gate.kernel import Gate

        store = self.engine.store
        seq, state = store.state()
        gate = Gate(self.engine.boundary, copy.deepcopy(state), self.engine.gate_tools, self.engine.gate_invariants)
        store.commit_cycle("t", gate.state, seq, gate.adjudicate(f"Noted.\n{line}"), line, user_text="x", display="Noted.")

    def remember(self, value, key="pepper_fear_trigger"):
        self.commit(f"NOMINATE what=self/memory/{key} verb=remember args=key:{key}; value:{value}")

    def test_a_key_written_again_keeps_what_it_held(self):
        self.remember("postman")
        self.remember("squirrel")
        self.assertEqual(self.engine.store.state()[1]["self"]["memory"]["pepper_fear_trigger"], "squirrel")
        self.assertEqual([v for v, _ in self.engine.store.memory_earlier()["pepper_fear_trigger"]], ["postman"])

    def test_the_same_value_again_is_not_history(self):
        self.remember("postman")
        self.remember("postman")
        self.assertEqual(self.engine.store.memory_earlier(), {})

    def test_forgetting_a_memory_forgets_its_history(self):
        self.remember("postman")
        self.remember("squirrel")
        self.commit("NOMINATE what=self/memory/consolidation verb=forget args=keys:pepper_fear_trigger")
        self.assertEqual(self.engine.store.memory_earlier(), {})

    def test_the_reply_prompt_shows_the_earlier_values(self):
        self.remember("postman")
        self.remember("squirrel")
        found = self.engine.cortex._halcyon_recall(SimpleNamespace(halcyon_state=self.engine.store.state()[1]),
                                                   "She bolted again.")
        self.assertIn("- pepper_fear_trigger: squirrel (earlier: postman)", PromptComposer._recall_block(found))
