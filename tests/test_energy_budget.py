"""The engine's energy (Gordon, 2026-09-29). The end-to-end run drained TECHNICAL to 0 ATP by turn 6: a file
was charged twice, at 0.02 ATP a character, and then the parity gate refused four of the person's questions.
A file now costs one fixed action (its text is already paid for as generated tokens), and a spent engine
answers briefly and asks for rest instead of refusing."""

import tempfile
from unittest.mock import MagicMock, patch

from mechanics.tools import TheSubstrate
from tests.base import BoneTestCase

SHORT = "x = 1\n"
LONG = "def parse(line):\n    return line.split()\n" * 60


class FileCost(BoneTestCase):
    def setUp(self):
        super().setUp()
        out = tempfile.mkdtemp()
        patcher = patch.object(TheSubstrate, "_base_dir", staticmethod(lambda: out))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.engine.substrate = TheSubstrate(self.engine.events)
        self.mito = self.engine.cortex.svc.bio.mito

    def cost_of(self, name, text):
        self.mito.state.atp_pool = 80.0
        sim = {"ui": ""}
        self.engine.cortex._flush_substrate_writes([f"[SUBSTRATE_QUEUE] {name}:::{text}"], sim)
        self.assertIn("Physically forged", sim["ui"])
        return 80.0 - self.mito.state.atp_pool

    def test_a_file_costs_one_fixed_action_charged_once(self):
        self.assertAlmostEqual(self.cost_of("a.py", SHORT), 1.0, places=6)

    def test_the_cost_does_not_grow_with_length(self):
        self.assertAlmostEqual(self.cost_of("b.py", LONG), self.cost_of("c.py", SHORT), places=6)


class RunningOnEmpty(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "TECHNICAL"
        self.generate = self.engine.cortex.llm.generate = MagicMock(return_value="Use a Counter and most_common(10).")

    def ask(self, atp):
        self.engine.bio.mito.state.atp_pool = atp
        return self.engine.process_turn("What's a clean way to find the top ten paths?")

    def test_a_spent_engine_answers_briefly_and_asks_for_rest(self):
        result = self.ask(0.0)
        self.assertNotEqual(result.get("type"), "SYSTEM_HALT")
        self.assertNotIn("PARITY GATE", str(result.get("ui", "")))
        prompt, params = self.generate.call_args[0]
        self.assertIn("RUNNING ON EMPTY", prompt)
        self.assertIn("rest", prompt.split("RUNNING ON EMPTY")[1][:300])
        self.assertLessEqual(params["max_tokens"], self.engine.cortex.EMPTY_MAX_TOKENS)

    def test_a_rested_engine_is_not_told_so(self):
        self.ask(80.0)
        prompt, params = self.generate.call_args[0]
        self.assertNotIn("RUNNING ON EMPTY", prompt)
        self.assertGreater(params.get("max_tokens", 4096), self.engine.cortex.EMPTY_MAX_TOKENS)
