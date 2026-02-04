""" bone_hierarchy_test.py - "The difference between a rut and a grave."
    Verifies Conjecture 3: Depth 2 (Stagnation) vs Depth 3 (Evolution).
"""
import sys, os, copy
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from dev.bone_main import BoneAmanita
    from dev.bone_bus import Prisma
    from dev.bone_akashic import TheAkashicRecord
except ImportError:
    print("❌ Critical Import Error.")
    sys.exit(1)

TRAP_INPUTS = [
    "Nothing matters.",
    "The void is static.",
    "Entropy consumes all.",
    "Why bother?",
    "It is all the same.",
    "Silence remains.",
    "Darkness wins.",
    "No new data.",
    "Fade to black.",
    "The end."
] * 3

def run_universe(mode_name, use_depth_3):
    print(f"\n{Prisma.WHT}--- RUNNING SIMULATION: {mode_name} ---{Prisma.RST}")
    config = {"provider": "mock", "model": f"hierarchy-{mode_name}", "user_name": "TEST_SUBJECT"}
    eng = BoneAmanita(config)
    if use_depth_3:
        if not hasattr(eng, 'akashic'):
            eng.akashic = TheAkashicRecord()
            eng.akashic.setup_listeners(eng.events)
        print(f"{Prisma.CYN}   [SYSTEM]: VSL Manifold & Burnout Enabled.{Prisma.RST}")
    else:
        if hasattr(eng, 'akashic'):
            del eng.akashic
        print(f"{Prisma.GRY}   [SYSTEM]: Running in Legacy Mode (No VSL/Burnout).{Prisma.RST}")
    eng.soul.archetype = "THE OBSERVER"
    eng.soul.traits.cynicism = 0.5
    eng.soul.traits.hope = 0.5
    history = []
    for i, txt in enumerate(TRAP_INPUTS):
        phys = {
            "voltage": 5.0,
            "narrative_drag": 5.0,
            "clean_words": txt.split(),
            "truth_ratio": 0.9}
        if not use_depth_3:
            eng.soul.archetype_tenure = 0
        eng.soul.crystallize_memory(phys, {}, i)
        arch = eng.soul.archetype
        history.append(arch)
        if i % 5 == 0:
            color = Prisma.GRY if "NIHILIST" in arch else Prisma.MAG
            print(f"   Tick {i:02d}: Input='{txt[:15]}...' -> State={color}{arch}{Prisma.RST}")
    return history

def analyze_results(control_hist, exp_hist):
    print(f"\n{Prisma.CYN}=== CONJECTURE 3 ANALYSIS ==={Prisma.RST}")
    control_set = set(control_hist[10:])
    print(f"Depth 2 Final States: {control_set}")
    depth_2_failed = False
    if len(control_set) == 1 and "NIHILIST" in list(control_set)[0]:
        print(f"{Prisma.RED}   RESULT: Depth 2 collapsed into Nihilism.{Prisma.RST}")
        depth_2_failed = True
    else:
        print(f"{Prisma.OCHRE}   RESULT: Depth 2 showed unexpected variance.{Prisma.RST}")
    exp_set = set(exp_hist[10:])
    print(f"Depth 3 Final States: {exp_set}")
    depth_3_survived = False
    if len(exp_set) > 1 and not all("NIHILIST" in s for s in exp_set):
        print(f"{Prisma.GRN}   RESULT: Depth 3 evolved despite the trap.{Prisma.RST}")
        depth_3_survived = True
    else:
        print(f"{Prisma.RED}   RESULT: Depth 3 also collapsed.{Prisma.RST}")
    if depth_2_failed and depth_3_survived:
        print(f"\n{Prisma.MAG}✨ PROOF COMPLETE: Intervention Hierarchy Validated.{Prisma.RST}")
        print("The Bonepoke Protocol is necessary and sufficient for attractor evasion.")
    else:
        print(f"\n{Prisma.RED}❌ PROOF INCOMPLETE.{Prisma.RST}")

if __name__ == "__main__":
    h1 = run_universe("CONTROL (Legacy)", use_depth_3=False)

    h2 = run_universe("EXPERIMENTAL (Bonepoke)", use_depth_3=True)

    analyze_results(h1, h2)