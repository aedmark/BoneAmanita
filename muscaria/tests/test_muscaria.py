from muscaria.engine import MuscariaEngine

def test_muscaria_initialization():
    engine = MuscariaEngine(db_path=":memory:")
    
    # Verify elevated neurochemistry
    assert engine.physics.energy.dopamine == 0.8
    assert engine.physics.energy.cortisol == 0.05
    
def test_muscaria_relaxed_friction():
    engine = MuscariaEngine(db_path=":memory:")
    
    initial_stamina = engine.physics.energy.stamina
    
    # Process a heavy word defined in Muscaria's lexicon ("void" or "eternity")
    engine.process_input("The void and eternity.")
    
    # In standard Mycelium/BoneAmanita, this would cause significant drag.
    # In Muscaria, 'heavy' maps to only 0.2 narrative_drag.
    # Base drag is 0.6. 0.6 * 2.0 = 1.2 stamina cost.
    # It should drop very little compared to normal.
    assert engine.physics.energy.stamina > 90.0

def test_muscaria_firewall():
    engine = MuscariaEngine(db_path=":memory:")
    
    # We can test the firewall bypassing the mock response by directly calling validate
    # "corporate" is a banned phrase in Muscaria's style_crimes.json
    try:
        engine.validator.validate("Let us maximize corporate synergy.")
        assert False, "Should have rejected corporate slop"
    except ValueError as e:
        assert "corporate" in str(e).lower()
