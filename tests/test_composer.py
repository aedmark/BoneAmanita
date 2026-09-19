"""tests/test_composer.py"""

import unittest
from unittest.mock import MagicMock

from brain.composer import LLMInterface, PromptComposer, ResponseValidator
from constants import Prisma
from tests.base import BoneTestCase


class TestComposerLogging(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.mock_events = MagicMock()
        self.llm = LLMInterface(events_ref=self.mock_events, provider="mock")
        self.llm.failure_count = 2
        self.llm.circuit_state = "CLOSED"

    def test_mock_generation_dream_diagnostic_logging(self):
        mock_prompt = (
            "SYSTEM BOOT SEQUENCE\n"
            "[MODE: ADVENTURE]\n"
            "Voltage=85.5\n"
            "Exhaustion=0.9\n"
            "Chaos=0.75\n"
            "Void=0.4\n"
            "Current Biology: HYPOXIA\n"
            "End of prompt."
        )
        self.llm.mock_generation(prompt=mock_prompt, reason="STRESS_TEST")
        expected_log = (
            "DREAM DIAGNOSTIC | Mode: ADVENTURE | V: 85.5 | E: 0.9 | "
            "Chi: 0.75 | Psi: 0.4 | Resp: HYPOXIA | "
            "Failures: 2 | Circuit: CLOSED | Trigger: STRESS_TEST"
        )
        self.mock_events.log.assert_any_call(
            f"{Prisma.GRY}{expected_log}{Prisma.RST}", "DEBUG"
        )

    def test_mock_generation_handles_missing_data(self):
        hollow_prompt = "Just a completely normal prompt with no telemetry."
        self.llm.mock_generation(prompt=hollow_prompt, reason="SIMULATION")
        expected_log = (
            "DREAM DIAGNOSTIC | Mode: UNKNOWN | V: N/A | E: N/A | "
            "Chi: N/A | Psi: N/A | Resp: N/A | "
            "Failures: 2 | Circuit: CLOSED | Trigger: SIMULATION"
        )
        self.mock_events.log.assert_any_call(
            f"{Prisma.GRY}{expected_log}{Prisma.RST}", "DEBUG"
        )


class TestResponseValidator(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.mock_lore = MagicMock()
        self.mock_lore.get.return_value = {}
        self.validator = ResponseValidator(lore_ref=self.mock_lore)

    def test_universally_strips_think_tags(self):
        raw_response = (
            "<think>\nI am calculating the matrix.\n</think>\nHere is the matrix."
        )
        state = {"meta": {"active_mode": "TECHNICAL"}}
        result = self.validator.validate(raw_response, state)
        self.assertTrue(result.get("valid", False))
        self.assertEqual(result.get("content", "").strip(), "Here is the matrix.")
        self.assertNotIn("<think>", result.get("content", ""))

    def test_universally_strips_system_telemetry_tags(self):
        raw_response = (
            "<system_telemetry>V: 90 E: 1.0</system_telemetry>\nThe world burns."
        )
        state = {"meta": {"active_mode": "CONVERSATION"}}
        result = self.validator.validate(raw_response, state)
        self.assertTrue(result.get("valid", False))
        self.assertEqual(result.get("content", "").strip(), "The world burns.")

    def test_technical_mode_does_not_require_think_tag(self):
        raw_response = "def calculate_matrix(): pass"
        state = {"meta": {"active_mode": "TECHNICAL"}}
        result = self.validator.validate(raw_response, state)
        self.assertTrue(result.get("valid", False))
        self.assertNotIn(
            "CRITICAL: You failed to include the <think>...</think> block",
            result.get("feedback_instruction") or "",
        )


class TestNegativeComparisonDetection(BoneTestCase):
    """The Lexical Firewall's antithesis rule only caught 'not X, but Y'
    linked by a comma or dash inside one sentence. A live census turn slipped
    three separate antithesis constructions past it, split across sentences
    and semicolons instead: 'it isn't a monument. It's a transition. You
    aren't building a shrine; you're honoring him...'. Widened to also catch
    the negation and its contrastive echo split across a sentence boundary or
    a semicolon."""

    def setUp(self):
        super().setUp()
        self.validator = self.engine.cortex.validator

    def _feedback(self, text: str) -> dict:
        return self.validator.validate(text, {"meta": {"active_mode": "CONVERSATION"}})

    def test_same_sentence_comma_form_is_still_caught(self):
        result = self._feedback("It's not merely a boat, but a memory of him.")
        self.assertFalse(result["valid"])

    def test_cross_sentence_form_is_now_caught(self):
        result = self._feedback(
            "It isn't a monument. It's a transition, built one plank at a time."
        )
        self.assertFalse(result["valid"])

    def test_semicolon_linked_form_is_now_caught(self):
        result = self._feedback(
            "Adding reinforcement isn't an admission of failure; it's insurance."
        )
        self.assertFalse(result["valid"])

    def test_plain_negation_is_not_flagged(self):
        """A pure negative statement, with no contrastive echo, is not antithesis."""
        result = self._feedback("It isn't clear yet what you'll decide, and that's fine.")
        self.assertTrue(result["valid"])


class TestPromptComposer(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.mock_lore = MagicMock()
        self.mock_lore.get.return_value = {}
        self.composer = PromptComposer(lore_ref=self.mock_lore)

    def test_composer_respects_active_mode_exits_rule(self):
        mind_state = {"role": "The Architect"}
        adv_block = self.composer._build_persona_block(
            mind=mind_state,
            bio={},
            mood_override="",
            mode_data={},
            global_data={},
            high_voltage_data={},
            vsl_state={},
            active_mode_name="ADVENTURE",
        )
        adv_text = "\n".join(adv_block)
        self.assertIn("CRITICAL FORMATTING AXIOM", adv_text)
        self.assertIn("**Exits:**", adv_text)
        conv_block = self.composer._build_persona_block(
            mind=mind_state,
            bio={},
            mood_override="",
            mode_data={},
            global_data={},
            high_voltage_data={},
            vsl_state={},
            active_mode_name="CONVERSATION",
        )
        conv_text = "\n".join(conv_block)
        self.assertNotIn("CRITICAL FORMATTING AXIOM", conv_text)
        self.assertNotIn("**Exits:**", conv_text)


if __name__ == "__main__":
    unittest.main()
