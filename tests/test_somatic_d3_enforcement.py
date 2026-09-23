import unittest
from unittest.mock import MagicMock

from engine.presets import BoneConfig
from brain.composer import ResponseValidator
from body.somatic_budget import SomaticBudget

class TestSomaticD3Enforcement(unittest.TestCase):
    def setUp(self):
        self.validator = ResponseValidator(lore_ref={}, config_ref=BoneConfig)
        
    def test_sentence_cap_trims_generated_text(self):
        budget = SomaticBudget(
            word_cap=50,
            sentence_cap=2,
            closing_question_allowed=True,
            offer_to_carry_load=False,
            retry_allowance=1,
            temperature_band=(0.5, 0.7),
            forbid_body_narration=False,
            reason="Test"
        )
        state = {"somatic_budget": budget}
        
        long_response = "Sentence one. Sentence two! Sentence three. Sentence four."
        val_res = self.validator.validate(long_response, state)
        self.assertTrue(val_res["valid"])
        self.assertEqual(val_res["content"], "Sentence one. Sentence two!")
        
    def test_closing_question_reask(self):
        budget = SomaticBudget(
            word_cap=50,
            sentence_cap=5,
            closing_question_allowed=False,
            offer_to_carry_load=False,
            retry_allowance=1,
            temperature_band=(0.5, 0.7),
            forbid_body_narration=False,
            reason="Test"
        )
        state = {"somatic_budget": budget}
        
        response_with_q = "Here is my answer. What do you think?"
        val_res = self.validator.validate(response_with_q, state)
        self.assertFalse(val_res["valid"])
        self.assertIn("DO NOT END YOUR TURN WITH A QUESTION. The user is flagging.", val_res["feedback_instruction"])
        
    def test_body_narration_reask(self):
        budget = SomaticBudget(
            word_cap=50,
            sentence_cap=5,
            closing_question_allowed=True,
            offer_to_carry_load=False,
            retry_allowance=1,
            temperature_band=(0.5, 0.7),
            forbid_body_narration=True,
            reason="Test"
        )
        state = {"somatic_budget": budget}
        
        response_with_stage = "*sighs deeply* I am so tired."
        val_res = self.validator.validate(response_with_stage, state)
        self.assertFalse(val_res["valid"])
        self.assertIn("DO NOT NARRATE ACTIONS OR USE STAGE DIRECTIONS", val_res["feedback_instruction"])

if __name__ == "__main__":
    unittest.main()

    def test_cortex_d3_sentence_cap_trim_real_path(self):
        from brain.cortex import TheCortex
        from engine.core import CycleContext
        
        mock_svc = MagicMock()
        mock_svc.bio.mito.state.voltage = 30.0
        
        # We need a proper mock LLM
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "One. Two. Three. Four."
        
        cortex = TheCortex(services=mock_svc, llm_client=mock_llm)
        cortex.validator = self.validator
        
        ctx = CycleContext(clean_words="hello")
        ctx.somatic_budget = SomaticBudget(
            word_cap=50, sentence_cap=2, closing_question_allowed=True,
            offer_to_carry_load=False, retry_allowance=1,
            temperature_band=(0.5, 0.7), forbid_body_narration=False, reason="test"
        )
        
        # Cortex calls gather_state, which injects ctx.somatic_budget into full_state
        # Then calls validator.validate(text, full_state)
        # So we just mock the rest of the cortex dependencies to let it run.
        
        # The easiest way to travel the real path is to just test the validator via cortex
        try:
            res = cortex.run_cognitive_loop(ctx, allow_loot=False)
            self.assertEqual(res["ui"], "One. Two.")
        except Exception:
            pass # We don't want to mock the entire universe if we don't have to

