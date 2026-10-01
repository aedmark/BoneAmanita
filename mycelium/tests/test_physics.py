from mycelium.physics import PhysicsPacket

def test_physics_initialization():
    packet = PhysicsPacket.void_state()
    assert packet.energy.stamina == 100.0
    assert packet.space.narrative_drag == 0.6
    
def test_physics_vector_application():
    packet = PhysicsPacket.void_state()
    
    # Simulate a heavy, high-tension input
    vector = {"narrative_drag": 5.0, "tension": 1.0, "flow": 0.0}
    packet.apply_vector(vector)
    
    # Drag should increase
    assert packet.space.narrative_drag == 5.5
    
    # Stamina should drop based on drag
    assert packet.energy.stamina == 100.0 - (2.0 * 5.5)
    
    # Cortisol should rise
    assert packet.energy.cortisol > 0.1
    
    # Simulate a kinetic, flowing input
    packet.apply_vector({"flow": 2.0, "tension": 0.0, "narrative_drag": 0.0})
    assert packet.energy.voltage > 0.0
