"""A long reply under tension (end-to-end run, 2026-09-30). The heuristic audit refuses a reply over 150 words
when beta is over 0.8, and it counted code as words: "Can you review the whole design so far for problems?"
(278 words) and a packaging question (196) were refused on both drafts and shown a pause line. It now counts
prose only, and a too-long last draft keeps the sentences that fit."""

from unittest.mock import MagicMock, patch

from body.somatic_metrics import trim_to_word_cap
from brain.cortex import TheCortex
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

CODE = "```python\n" + "\n".join(f"def step_{i}(line):\n    return line.split()[{i}]" for i in range(40)) + "\n```"
LONG_PROSE = " ".join(f"Point {i} is worth checking before the release goes out." for i in range(30))


class TrimToWords(BoneTestCase):
    def test_whole_sentences_within_the_cap(self):
        self.assertEqual(trim_to_word_cap("One two three. Four five six. Seven eight.", 6), "One two three. Four five six.")

    def test_code_costs_nothing_and_is_never_cut(self):
        reply = f"Split each line.\n\n{CODE}\n\nThat is all of it. More words here to go over."
        cut = trim_to_word_cap(reply, 8)
        self.assertIn(CODE, cut)
        self.assertTrue(cut.endswith("That is all of it."))


class TheAudit(BoneTestCase):
    def test_code_is_not_counted_as_weight(self):
        ok, _ = self.engine.cortex._run_heuristic_audit("review it", f"Two fixes.\n\n{CODE}", 0.0, 0.9)
        self.assertTrue(ok)

    def test_long_prose_still_is(self):
        ok, _ = self.engine.cortex._run_heuristic_audit("review it", LONG_PROSE, 0.0, 0.9)
        self.assertFalse(ok)
        self.assertEqual(self.engine.cortex.heavy_cap, 150)


class LastDraftUnderTension(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "TECHNICAL"
        self.generate = self.engine.cortex.llm.generate = MagicMock(return_value=LONG_PROSE)
        real = TheCortex.gather_state

        def tense(cortex, sim_result):
            state = real(cortex, sim_result)
            state["physics"]["beta_index"] = 0.95
            return state

        patcher = patch.object(TheCortex, "gather_state", tense)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_too_long_last_draft_is_trimmed_not_paused(self):
        result = self.engine.process_turn("Can you review the whole design so far for problems?")
        ui = str(result.get("ui", ""))
        self.assertIn("Point 0 is worth checking", ui)
        self.assertNotIn("Point 29 is worth checking", ui)
        redrafts = [r for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "cortex.redraft"]
        self.assertTrue(all(r.effect == "heuristic_audit" for r in redrafts) and redrafts)
