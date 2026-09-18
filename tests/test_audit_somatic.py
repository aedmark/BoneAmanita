"""tests/test_audit_somatic.py

ROADMAP C5. The live experiment in `tools/audit_somatic.py` needs a chat model
and minutes of wall clock, so it is not in this suite. Its measurement rules are,
because each one below is a way the experiment would report a confident number
about prose the model did not write, or obedience it did not show.
"""

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

    def test_the_arms_differ_only_in_their_directives(self):
        base = "KERNEL\nCurrent Biology: Neutral.\nMETRICS: Voltage=30.0/100, Exhaustion=0.79\nTAIL"
        prompts = {
            "CONTROL": (base, {}),
            "ANAEROBIC": (base.replace("Neutral.", audit_somatic.ANAEROBIC_DIRECTIVE), {}),
            "EXHAUSTED": (
                base.replace("0.79", "0.81")
                + "\nCRITICAL: You are exhausted. "
                + audit_somatic.EXHAUSTION_DIRECTIVE
                + ".",
                {},
            ),
        }
        prompts["BOTH"] = (
            prompts["EXHAUSTED"][0].replace("Neutral.", audit_somatic.ANAEROBIC_DIRECTIVE),
            {},
        )
        audit_somatic.check_arms(prompts)

        leaked = dict(prompts, BOTH=(prompts["BOTH"][0].replace("TAIL", "OTHER"), {}))
        with self.assertRaises(AssertionError):
            audit_somatic.check_arms(leaked)


if __name__ == "__main__":
    unittest.main()
