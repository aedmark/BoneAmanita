from bone_types import PhysicsPacket
from bone_body import BioSystem, MitochondrialState, MitochondrialForge, EndocrineSystem, MetabolicGovernor, SomaticLoop

# 1. Setup Dummy Bio
mito_state = MitochondrialState()
events_dummy = None # Or a mock class
bio = BioSystem(
    mito=MitochondrialForge(mito_state, events_dummy),
    endo=EndocrineSystem(),
    governor=MetabolicGovernor()
)

# 2. Setup Loop
soma = SomaticLoop(bio, events_ref=events_dummy)

# 3. Create a Proper Packet (Strict Mode)
phys_packet = PhysicsPacket(
    voltage=10.0, 
    narrative_drag=1.5, 
    clean_words=["test", "system", "online"]
)

# 4. Run Cycle
result = soma.digest_cycle(
    text="System check.",
    physics_data=phys_packet, # Passing the OBJECT, not a dict
    feedback={},
    health=100.0,
    stamina=100.0,
    stress_modifier=1.0
)

print(f"Status: {result['respiration']}") # Should be "RESPIRING"
print(f"ATP: {result['atp']}")           # Should be < 60.0 (burned some fuel)