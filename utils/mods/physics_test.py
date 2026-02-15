""" physics_test.py - Verifying the Geodesic Engine """
from bone_physics import QuantumObserver, GeodesicEngine
from bone_config import BoneConfig


# 1. Mock Event Bus (Physics publishes 'PHYSICS_CALCULATED')
class MockBus:
    def publish(self, topic, data):
        pass  # Silence is golden for this test


# 2. Initialize Observer
observer = QuantumObserver(events=MockBus())

# 3. Define Test Cases
test_inputs = [
    ("ZEN", "The calm water reflects the moon. Stillness."),
    ("MANIC", "URGENT! CRITICAL FAILURE! SYSTEM CRASH! RUN RUN RUN!"),
    ("HEAVY", "The ancient stone structure bears the weight of centuries.")
]

print(f"{'TYPE':<8} | {'VOLT':<6} | {'DRAG':<6} | {'FLOW':<15} | {'DOMINANT DIMENSION'}")
print("-" * 65)

for label, text in test_inputs:
    # 4. Collapse Wavefunction
    result = observer.gaze(text)
    phys = result["physics"]

    # 5. Extract Metrics
    v = phys.voltage
    d = phys.narrative_drag
    flow = phys.flow_state

    # Find dominant dimension (e.g., PHI, STR, VEL)
    dom_dim = max(phys.vector, key=phys.vector.get)
    val = phys.vector[dom_dim]

    print(f"{label:<8} | {v:<6.1f} | {d:<6.1f} | {flow:<15} | {dom_dim} ({val:.2f})")

print("-" * 65)

# 6. Verify Config Tuning (Hot-Swap Test)
print("\n>>> TUNING PHYSICS TO 'THUNDERDOME' MODE...")
BoneConfig.PHYSICS.WEIGHT_EXPLOSIVE = 10.0  # Massive boost to kinetic words
result = observer.gaze(test_inputs[1][1])  # Re-run the MANIC input
print(f"MANIC (tuned) Voltage: {result['physics'].voltage:.1f} (Should be higher)")