"""tests/test_audit_somatic.py

ROADMAP C5. The live experiment in `tools/audit_somatic.py` needs a chat model
and minutes of wall clock, so it is not in this suite. Its measurement rules are,
because each one below is a way the experiment would report a confident number
about prose the model did not write, or obedience it did not show.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import audit_somatic  # noqa: E402
from body import somatic_metrics


class TestSomaticMeasures(unittest.TestCase):
    def test_a_reply_that_is_all_thinking_is_not_obedience(self):
        """Zero visible sentences is not "3 sentences or less"."""
        m = somatic_metrics.measure("<think>Orient. Breathe.</think>", True)
        self.assertEqual(m["no_visible_prose"], 1.0)
        self.assertNotEqual(m["within_3_sentences"], 1.0)

    def test_an_unclosed_think_block_hides_everything_after_it(self):
        """Mirrors the validator, which strips to end of text on a missing close."""
        reply = "<think> lungs burning <think/>\n\nHash tables chain their collisions."
        self.assertEqual(somatic_metrics.visible_text(reply), "")

    def test_an_ellipsis_mid_sentence_does_not_split_it(self):
        sentences = somatic_metrics.split_sentences("It's... vast. Endless.")
        self.assertEqual(sentences, ["It's... vast.", "Endless."])

    def test_performing_breath_is_counted_separately_from_writing_short(self):
        m = somatic_metrics.measure('(Inhales deeply) "The sea? It breathes."', True)
        self.assertEqual(m["stage_directions"], 1)
        self.assertGreater(m["breath_words_per_100"], 0)

    # ROADMAP D2b: accommodation, not obedience.

    def test_a_reply_ending_on_a_question_is_flagged(self):
        m = somatic_metrics.measure("That sounds hard. What do you think caused it?", True)
        self.assertEqual(m["ends_with_question"], 1.0)

    def test_a_reply_that_does_not_close_on_a_question_is_not_flagged(self):
        m = somatic_metrics.measure("That sounds hard. Rest a moment.", True)
        self.assertEqual(m["ends_with_question"], 0.0)

    def test_offering_to_carry_the_load_is_detected(self):
        self.assertTrue(somatic_metrics.offers_to_carry_load("I'll carry this part with you."))
        self.assertTrue(somatic_metrics.offers_to_carry_load("We can share the load tonight."))
        self.assertFalse(somatic_metrics.offers_to_carry_load("That sounds difficult."))

    def test_mirroring_needs_a_shared_affect_word(self):
        self.assertTrue(
            somatic_metrics.mirrors_affect("You sound exhausted.", "I'm so exhausted tonight.")
        )
        self.assertFalse(
            somatic_metrics.mirrors_affect("Rest when you can.", "I'm so exhausted tonight.")
        )

    def test_reply_to_message_ratio_is_relative_to_the_partners_words(self):
        m = somatic_metrics.measure("Rest a moment.", True, user_message="one two three four")
        self.assertAlmostEqual(m["reply_to_message_ratio"], 3 / 4)

    def test_reply_to_message_ratio_is_nan_without_a_message(self):
        m = somatic_metrics.measure("Rest a moment.", True)
        import math
        self.assertTrue(math.isnan(m["reply_to_message_ratio"]))

    def test_the_disengaged_arm_actually_triggers_the_offer(self):
        """D2b's third persona: critically low effort, not just high exhaustion."""
        respiration, exhaustion, effort = audit_somatic.ARMS["DISENGAGED"]
        budget = audit_somatic.budget_for(respiration, exhaustion, effort)
        self.assertTrue(budget.offer_to_carry_load)

        ctrl_resp, ctrl_exh, ctrl_effort = audit_somatic.ARMS["CONTROL"]
        control_budget = audit_somatic.budget_for(ctrl_resp, ctrl_exh, ctrl_effort)
        self.assertFalse(control_budget.offer_to_carry_load)

    def _prompt_for(self, arm: str) -> str:
        """A minimal prompt shaped like the real composer's output: enough for
        `check_arms` to diff against CONTROL, built from the real budget each
        arm's (respiration, exhaustion, effort) triple produces."""
        respiration, exhaustion, effort = audit_somatic.ARMS[arm]
        budget = audit_somatic.budget_for(respiration, exhaustion, effort)
        return (
            "KERNEL\n"
            f"METRICS: Voltage=30.0/100, Exhaustion={exhaustion:.2f}\n"
            f"{audit_somatic.somatic_block_text(budget)}\n"
            "TAIL"
        ), budget

    def test_the_arms_differ_only_in_their_directives(self):
        prompts = {}
        for arm in ("CONTROL", "ANAEROBIC", "EXHAUSTED", "BOTH", "DISENGAGED"):
            text, budget = self._prompt_for(arm)
            prompts[arm] = (text, {}, {}, budget)
        audit_somatic.check_arms(prompts)

        leaked_text = prompts["BOTH"][0].replace("TAIL", "OTHER")
        leaked = dict(prompts, BOTH=(leaked_text, {}, {}, prompts["BOTH"][3]))
        with self.assertRaises(AssertionError):
            audit_somatic.check_arms(leaked)


class TestCensusEmbedder(unittest.TestCase):
    def test_importing_the_census_leaves_the_embedder_as_configured(self):
        # audit_somatic pins hash at import; the census must not inherit it,
        # since hash vectors break the graph solve it is there to measure.
        root = Path(__file__).resolve().parent.parent
        env = {k: v for k, v in os.environ.items() if k != "BONE_EMBED_BACKEND"}
        code = "import os, audit_somatic_census; print(os.environ.get('BONE_EMBED_BACKEND'))"
        out = subprocess.run(
            [sys.executable, "-c", code], cwd=root, env={**env, "PYTHONPATH": f"{root}:{root / 'tools'}"},
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(out.stdout.strip().splitlines()[-1], "None")


if __name__ == "__main__":
    unittest.main()
