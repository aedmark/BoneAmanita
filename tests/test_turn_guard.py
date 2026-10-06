"""feud20 probes (2026-10-05): a turn past the cognitive loop limit kept running after the person was shown the
timeout, wrote its unseen reply into the history, ran the keeper and held up the next turn behind it."""

import time
from unittest.mock import MagicMock, patch

from tests.base import BoneTestCase


class ATimedOutTurn(BoneTestCase):
    SLOW = "reply"

    def setUp(self):
        super().setUp()
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.memory_keeper.enabled = True
        self.prompts = []
        self.slow = True

        def generate(prompt, *a, **k):
            self.prompts.append(str(prompt))
            keeper = str(prompt).startswith("You keep the memory")
            if self.slow and (keeper or self.SLOW == "reply"):
                self.slow = False
                time.sleep(2.0)
                return "dog_damage = chewed the couch" if keeper else "The reply nobody saw."
            return "dog_damage = chewed the couch" if keeper else "The reply nobody saw." if self.slow else "Long days wear on you."

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)
        timeout = patch.object(self.engine.config, "ORCHESTRATOR_TIMEOUT", 0.5, create=True)
        timeout.start()
        self.addCleanup(timeout.stop)

    def test_writes_nothing_and_the_next_turn_runs(self):
        first = self.engine.process_turn("My dog chewed the couch.")
        self.assertIn("Cognitive Loop Timeout", str(first.get("ui", "")))
        self.assertTrue(self.engine.orchestrator.idle.wait(10.0))
        if self.SLOW == "reply":
            self.assertEqual([p for p in self.prompts if p.startswith("You keep the memory")], [])
        self.assertNotIn("dog_damage", str(self.engine.store.state()[1]))

        self.engine.process_turn("Work was long today.")
        history = "\n".join(self.engine.cortex.dialogue_buffer)
        self.assertNotIn("The reply nobody saw.", history)
        self.assertNotIn("My dog chewed the couch.", history)
        self.assertIn("Work was long today.", history)


class ATurnTimedOutInTheKeeper(ATimedOutTurn):
    """Past the reply, the keeper's answer is not committed and the reply leaves the history."""
    SLOW = "keeper"
