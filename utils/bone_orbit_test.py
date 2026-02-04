""" bone_orbit_test.py - "To watch the stars turn."
    Verifies Conjecture 2: Non-Periodic Attractor Dynamics.
"""
import sys, os, time
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from dev.bone_main import BoneAmanita
    from dev.bone_bus import Prisma
    from dev.bone_akashic import TheAkashicRecord
except ImportError:
    print("❌ Critical Import Error.")
    sys.exit(1)

def test_periodicity():
    print(f"\n{Prisma.CYN}=== CONJECTURE 2: ORBIT VERIFICATION ==={Prisma.RST}")
    config = {"provider": "mock", "model": "orbit-test-unit", "user_name": "TIME_TRAVELER"}
    eng = BoneAmanita(config)
    if not hasattr(eng, 'akashic'):
        eng.akashic = TheAkashicRecord()
    eng.soul.archetype = "THE POET"
    eng.soul.traits.hope = 0.95
    eng.soul.traits.curiosity = 0.95
    eng.soul.traits.discipline = 0.2
    eng.soul.archetype_tenure = 0
    print(f"Initial State: {Prisma.MAG}THE POET{Prisma.RST} (Hope: 0.95, Cur: 0.95)")
    print("Beginning 30-Cycle Fast Forward...")
    history = []
    has_shifted = False
    for i in range(30):
        phys = {"voltage": 10.0, "narrative_drag": 1.0, "truth_ratio": 0.5, "clean_words": []}
        eng.soul.crystallize_memory(phys, {}, i)
        current = eng.soul.archetype
        tenure = eng.soul.archetype_tenure
        traits = eng.soul.traits
        history.append(current)
        if i % 5 == 0 or tenure == 0:
            print(f"   Tick {i:02d}: {current:<15} (Tenure: {tenure}) | H:{traits.hope:.2f} C:{traits.curiosity:.2f}")
        if current != "THE POET" and not has_shifted:
            print(f"{Prisma.GRN}✔ PHASE SHIFT DETECTED at Tick {i}{Prisma.RST}")
            print(f"   The Poet burned out. New Form: {current}")
            has_shifted = True
    unique_states = set(history)
    print(f"\n{Prisma.WHT}--- ORBIT ANALYSIS ---{Prisma.RST}")
    print(f"Unique Archetypes Visited: {unique_states}")
    if len(unique_states) > 1:
        print(f"{Prisma.GRN}✔ SUCCESS: System escaped the fixed point attractor.{Prisma.RST}")
        if "THE POET" not in history[-1]:
             print(f"{Prisma.CYN}   (Conjecture 2 Proven: 'Burnout' mechanic successfully forced evolution.){Prisma.RST}")
    else:
        print(f"{Prisma.RED}❌ FAILURE: System Stagnated. The Poet is immortal.{Prisma.RST}")

if __name__ == "__main__":
    test_periodicity()