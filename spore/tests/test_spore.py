from spore.engine import SporeEngine

def test_spore_initialization():
    engine = SporeEngine(db_path=":memory:")
    assert engine.physics.energy.dopamine == 0.1
    assert engine.physics.energy.cortisol == 0.1
    
def test_spore_code_friction():
    engine = SporeEngine(db_path=":memory:")
    
    # Test that code keywords ("def", "class", "return") act as solvents
    # and don't cause massive drag like conversational words do.
    code_input = "def my_func():\n    return True"
    engine.process_input(code_input, "def output(): pass")
    
    # Base drag is ~0.6, solvents make it stay low. Stamina shouldn't drop much.
    assert engine.physics.energy.stamina > 95.0

def test_spore_firewall_retry():
    engine = SporeEngine(db_path=":memory:")
    
    # Give it a slop response. It should log the rejection and return the clean code
    # because the mock logic simulates a "clean" output on retry 2.
    bad_llm_response = "Certainly! I hope this helps. Here is the code: def foo(): pass"
    final_output = engine.process_input("Write a function.", bad_llm_response)
    
    # It should not return the bad response, it should return the retried response
    assert "Certainly" not in final_output
    assert "def optimized_function():" in final_output
