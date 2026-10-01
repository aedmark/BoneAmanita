import pytest
from mycelium.composer import ResponseValidator, PromptComposer

def test_response_validator():
    validator = ResponseValidator({"BANNED_PHRASES": ["as an ai", "synergy"]})
    
    # Valid
    validator.validate("Here is a story about a tree.")
    
    # Invalid
    with pytest.raises(ValueError, match="Lexical Firewall Violation: Detected banned phrase 'as an ai'"):
        validator.validate("as an ai, I cannot do that.")

def test_prompt_composer():
    prompts = {"DEFAULT": "I am a strict biological entity.\n{self_claims}"}
    claims = {
        "claims": [
            {"text": "I am stressed.", "conditions": {"cortisol_min": 0.5}},
            {"text": "I am happy.", "conditions": {"dopamine_min": 0.8}}
        ]
    }
    
    composer = PromptComposer(prompts, claims)
    
    # Low stress
    p1 = composer.compose("Hello", {"cortisol": 0.1, "dopamine": 0.1}, {"narrative_drag": 1.0})
    assert "I am stressed." not in p1
    
    # High stress
    p2 = composer.compose("Hello", {"cortisol": 0.8, "dopamine": 0.1}, {"narrative_drag": 1.0})
    assert "- I am stressed." in p2
    assert "Stamina:" in p2
