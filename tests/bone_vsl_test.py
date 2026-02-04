""" bone_vsl_test.py - "To see the curvature of the dream."
    Verifies Conjecture 3: Coupled Meta-Control and Manifold Deformation.
"""
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from dev.bone_main import BoneAmanita
    from dev.bone_bus import Prisma
    from dev.bone_akashic import TheAkashicRecord
    from dev.bone_soul import MEMORY_VOLTAGE_THRESHOLD
except ImportError:
    print("❌ Critical Import Error. Ensure you are running this from the project root.")
    sys.exit(1)

def test_vsl_mechanics():
    print(f"\n{Prisma.CYN}=== VSL PROTOCOL VERIFICATION (DEPTH 3) ==={Prisma.RST}")
    config = {"provider": "mock", "model": "vsl-test-unit", "user_name": "TRAVELER"}
    eng = BoneAmanita(config)
    if not hasattr(eng, 'akashic'):
        print(f"{Prisma.OCHRE}⚠️  Wiring Akashic manually for isolation test...{Prisma.RST}")
        eng.akashic = TheAkashicRecord()
        eng.akashic.setup_listeners(eng.events)
    soul = eng.soul
    akashic = eng.akashic
    soul.archetype = "THE POET"
    print(f"Identity Set: {Prisma.MAG}{soul.archetype}{Prisma.RST}")
    soul.traits.discipline = 0.8
    soul.traits.hope = 0.9
    soul.traits.curiosity = 0.5
    print(f"Traits Set:   Tension={soul.traits.discipline}, Vitality={soul.traits.hope}")
    print(f"\n{Prisma.WHT}--- TEST 1: MATHEMATICAL CONGRUENCE ---{Prisma.RST}")
    delta = akashic.calculate_manifold_shift(soul.archetype, soul.traits.to_dict())
    v_bias = delta.get('voltage_bias', 0.0)
    print(f"Calculated Manifold Shift (Delta): {delta}")

    if v_bias > 3.0:
        print(f"{Prisma.GRN}✔ Voltage Bias is correctly amplified ({v_bias:.2f}){Prisma.RST}")
    else:
        print(f"{Prisma.RED}❌ Voltage Bias too low (Math Failure).{Prisma.RST}")
    print(f"\n{Prisma.WHT}--- TEST 2: REALITY DEFORMATION ---{Prisma.RST}")
    raw_voltage = 13.0
    physics_packet = {
        "voltage": raw_voltage,
        "narrative_drag": 2.0,
        "truth_ratio": 0.9,
        "clean_words": ["echo", "shadow", "signal"]}
    print(f"Input Physics: {raw_voltage}v (Below Threshold of {MEMORY_VOLTAGE_THRESHOLD}v)")
    lesson = soul.crystallize_memory(physics_packet, {}, 0)
    if lesson:
        print(f"{Prisma.GRN}✔ Memory Crystallized: '{lesson}'{Prisma.RST}")
        recorded_mem = soul.core_memories[-1]
        final_voltage = recorded_mem.impact_voltage
        print(f"   Recorded Voltage: {Prisma.CYN}{final_voltage:.2f}v{Prisma.RST}")
        if final_voltage > raw_voltage:
             print(f"{Prisma.GRN}✔ SUCCESS: The Soul successfully warped reality (+{final_voltage - raw_voltage:.2f}v).{Prisma.RST}")
             print(f"{Prisma.GRY}   (Conjecture 1 Proven: System created its own attractor basin){Prisma.RST}")
        else:
             print(f"{Prisma.RED}❌ FAILURE: Physics remained static. The ghost is silent.{Prisma.RST}")
    else:
        print(f"{Prisma.RED}❌ FAILURE: No memory formed. The VSL Bias did not bridge the gap.{Prisma.RST}")

if __name__ == "__main__":
    test_vsl_mechanics()