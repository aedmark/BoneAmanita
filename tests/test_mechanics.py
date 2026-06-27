"""tests/test_mechanics.py"""

from tests.base import BoneTestCase


from unittest.mock import patch

class MechanicsTests(BoneTestCase):
    @patch("builtins.input")
    @patch("mechanics.setup.typewriter")
    @patch("mechanics.setup.subprocess.run")
    def test_setup_compute_profile_apu(self, mock_subprocess, mock_tw, mock_input):
        """Tests that selecting the Edge/APU profile properly assigns throttled metrics."""
        import os
        from mechanics.setup import ConfigWizard

        mock_input.side_effect = ["Traveler", "1", "4", "1", "4"]

        config = ConfigWizard._run_setup()

        self.assertIn("CORTEX", config, "[FAIL] Setup did not generate a CORTEX block for the compute profile.")
        self.assertEqual(config["CORTEX"]["TOPOLOGY_FREQ"], 10, "[FAIL] APU Topology Frequency not assigned correctly.")
        self.assertEqual(config["CORTEX"]["WLS_FREQ"], 10, "[FAIL] APU WLS Frequency not assigned correctly.")
        self.assertEqual(config["CORTEX"]["COGNITIVE_RETRY_LIMIT"], 1, "[FAIL] APU Cognitive Retry Limit not assigned correctly.")

        if os.path.exists(ConfigWizard.CONFIG_FILE):
            os.remove(ConfigWizard.CONFIG_FILE)

    def test_session_guardian_crash_immersion(self):
        import io
        import sys
        from unittest.mock import MagicMock

        from mechanics.terminal import SessionGuardian

        mock_engine = MagicMock()
        mock_engine.boot_mode = "NARRATIVE"
        guardian = SessionGuardian(engine_ref=mock_engine)
        captured_output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        try:
            guardian.__exit__(ValueError, ValueError("A simulated fatal crash."), None)
        finally:
            sys.stdout = old_stdout
        output = captured_output.getvalue()
        self.assertNotIn(
            "Traceback (most recent call last):",
            output,
            "[FAIL] Raw stack trace leaked to the terminal in NARRATIVE mode!",
        )
        self.assertIn(
            "collapsed",
            output.lower(),
            "[FAIL] SessionGuardian failed to print the graceful narrative crash message.",
        )

    def test_protocol_pragmatist_membrane(self):
        from mechanics.pragmatics import ThePragmatist

        pragmatist = ThePragmatist()
        phys_state = {"narrative_drag": 0.0, "entropy": 0.0}
        bad_draft = (
            "As an AI language model, I don't have feelings, but the sky is blue."
        )
        mutated, needs_rewrite = pragmatist.enforce_maxims(
            bad_draft, "How are you?", phys_state, stamina=100.0
        )
        self.assertFalse(
            needs_rewrite,
            "[FAIL] Quality breach should not trigger an LLM rewrite; it should mutate the text instantly.",
        )
        self.assertIn(
            "...",
            mutated,
            "[FAIL] Pragmatist failed to execute the Trope Breach. Slop leaked through.",
        )
        phys_state = {"narrative_drag": 10.0, "entropy": 0.0}
        bloated_draft = "Word " * 50
        mutated, needs_rewrite = pragmatist.enforce_maxims(
            bloated_draft, "Tell me a story", phys_state, stamina=20.0
        )
        self.assertTrue(
            needs_rewrite,
            "[FAIL] Pragmatist failed to trigger a rewrite on exhausted bloat. Cognitive overload imminent.",
        )
        phys_state = {"narrative_drag": 0.0, "entropy": 0.1}
        hedging_draft = "Perhaps it could be said that the sky is blue."
        mutated, needs_rewrite = pragmatist.enforce_maxims(
            hedging_draft, "What color is the sky?", phys_state, stamina=100.0
        )
        self.assertNotIn(
            "Perhaps", mutated, "[FAIL] Pragmatist failed to strip 'Perhaps'."
        )
        self.assertNotIn(
            "it could be said that",
            mutated,
            "[FAIL] Pragmatist failed to strip 'it could be said that'.",
        )
        self.assertIn(
            "the sky is blue.",
            mutated,
            "[FAIL] Pragmatist stripped too much and destroyed the bedrock logic.",
        )
