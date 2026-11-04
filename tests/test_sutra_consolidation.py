"""Sūtra consolidation tests (Vedas Path C): tests the extraction, density constraints,
gate adjudication, and command inspection of crystallized invariant sūtras."""

from unittest.mock import MagicMock

from engine.gate.sutra import SutraConsolidator, SUTRA_PREFIX
from tests.base import BoneTestCase


class TheSutraConsolidator(BoneTestCase):
    def test_line_for_valid_sutra(self):
        c = SutraConsolidator(None)
        lines = c.line_for("working_style = concise and direct, no fluff", ["m1", "m2"])
        self.assertEqual(len(lines), 1)
        self.assertIn("NOMINATE what=self/memory/sutra.working_style verb=reflect", lines[0])
        self.assertIn("key:sutra.working_style", lines[0])
        self.assertIn("value:concise and direct, no fluff", lines[0])
        self.assertIn("from:m1 | m2", lines[0])

    def test_line_for_none_returns_empty(self):
        c = SutraConsolidator(None)
        self.assertEqual(c.line_for("NONE", ["m1"]), [])
        self.assertEqual(c.line_for("none\nsomething = else", ["m1"]), [])
        self.assertEqual(c.line_for("", ["m1"]), [])

    def test_line_for_enforces_word_cap(self):
        c = SutraConsolidator(None)
        # 30 words (over 25 word cap)
        long_val = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twentyone twentytwo twentythree twentyfour twentyfive twentysix twentyseven"
        self.assertEqual(c.line_for(f"tool_rule = {long_val}", ["m1"]), [])

    def test_line_for_replaces_em_dashes(self):
        c = SutraConsolidator(None)
        lines = c.line_for("style = short sentences \u2014 never rambles", ["m1"])
        self.assertEqual(len(lines), 1)
        self.assertIn("value:short sentences, never rambles", lines[0])

    def test_consolidate_filters_existing_sutras(self):
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "NONE"
        c = SutraConsolidator(mock_llm, least=2)
        # If all candidates are existing sutras, none should be passed to prompt
        mems = {"sutra.old": "invariant", "sutra.prior": "rule"}
        lines = c.consolidate(mems)
        self.assertEqual(lines, [])
        mock_llm.generate.assert_not_called()


class SutraGateIntegration(BoneTestCase):
    def test_gate_adjudicates_sutra_nomination(self):
        import yaml
        from engine.gate.kernel import Boundary, Gate
        from engine.gate.tools import TOOLS, build_invariants

        spec = yaml.safe_load(open("engine/gate/boundary.yaml"))
        state = {
            "world": {"schema_version": 2, "sources": {}, "nodes": {}, "edges": [], "constraints": []},
            "self": {"memory": {"note_a": "first note", "note_b": "second note"}},
        }
        gate = Gate(Boundary(spec), state, TOOLS, build_invariants(spec))
        nomination = (
            "NOMINATE what=self/memory/sutra.craft verb=reflect "
            "args=key:sutra.craft; value:zero external dependencies; from:note_a | note_b"
        )
        receipt = gate.adjudicate(f"(Sūtra consolidation in REM on 2 memories.)\n{nomination}")
        self.assertEqual(receipt["decision"], "ACCEPT")
        self.assertEqual(receipt["result"], {"reflected": "sutra.craft", "from": ["note_a", "note_b"]})
        self.assertEqual(gate.state["self"]["memory"]["sutra.craft"], "zero external dependencies")


class SutraCycleAndCommand(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.sutra_consolidator.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.keeps = "NONE"
        self.sutras = "core_pattern = works in small reviewable steps"

        def generate(prompt, *a, **k):
            if prompt.startswith("You keep the memory"):
                return self.keeps
            if prompt.startswith("You are crystallizing"):
                return self.sutras
            return "Noted."

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)

    def keep(self, mode, message, keeps):
        self.engine.cortex.active_mode, self.keeps = mode, keeps
        self.engine.process_turn(message)

    def test_consolidate_sutras_and_cmd_sutra(self):
        self.keep("CONVERSATION", "I prefer concise reviews.", "pref_review = concise reviews")
        self.keep("CONVERSATION", "I work in small steps.", "work_cadence = small steps")

        written = self.engine.orchestrator.consolidate_sutras("test-sutra-trace")
        self.assertEqual(written, ["sutra.core_pattern"])

        # Check memory has the sutra
        _, state = self.engine.store.state()
        self.assertEqual(state["self"]["memory"]["sutra.core_pattern"], "works in small reviewable steps")

        # Test /sutra command
        self.engine.cmd.interface.log = log = MagicMock()
        self.engine.cmd.execute("/sutra")
        output = " ".join(str(c.args[0]) for c in log.call_args_list)
        self.assertIn("sutra.core_pattern", output)
        self.assertIn("works in small reviewable steps", output)
