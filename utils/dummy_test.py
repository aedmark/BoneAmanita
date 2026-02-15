from bone_types import PhysicsPacket
from bone_body import BioSystem, MitochondrialState, MitochondrialForge, EndocrineSystem, MetabolicGovernor, \
    SomaticLoop, Biometrics


# [FIX] A Mock class to handle log calls
class MockEventBus:
    def log(self, message, channel):
        print(f"   [LOG::{channel}] {message}")

    def publish(self, event_type, payload):
        print(f"   [EVENT::{event_type}] {payload}")

    def subscribe(self, event_type, callback):
        pass


# 1. Setup Dummy Bio with Mock Events
mito_state = MitochondrialState()
events_dummy = MockEventBus()

bio = BioSystem(
    mito=MitochondrialForge(mito_state, events_dummy),
    endo=EndocrineSystem(),
    governor=MetabolicGovernor(),
    biometrics=Biometrics(health=100.0, stamina=100.0)
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
print(">>> INJECTING CYCLE...")
result = soma.digest_cycle(
    text="System check.",
    physics_data=phys_packet,
    feedback={},
    health=100.0,
    stamina=100.0,
    stress_modifier=1.0
)

print(f"\n>>> RESULT:")
print(f"Status: {result['respiration']}")
print(f"ATP:    {result['atp']:.2f}")