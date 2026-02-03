# bone_test_unit.py
# "Isolation is the only way to see the signal."

from bone_main import BoneAmanita
from bone_bus import Prisma, CycleContext, PhysicsPacket
from bone_cycle import IntrusionPhase, NavigationPhase, SensationPhase
from bone_village import Manifold

def run_unit_tests():
    print(f"{Prisma.paint('>>> INITIATING WHITE ROOM PROTOCOLS', 'W')}")
    eng = BoneAmanita(user_name="TEST_SUBJECT_01")

    # ==============================================================================
    # TEST 1: THE IMMUNE SYSTEM (IntrusionPhase)
    # Goal: Manually inject a loop into the Graph and see if IntrusionPhase breaks it.
    # ==============================================================================
    print(f"\n{Prisma.paint('--- TEST 1: IMMUNE RESPONSE (ISOLATED) ---', 'Y')}")

    # 1. Prime the Memory Graph manually (Bypassing encoding)
    eng.mind.mem.graph = {
        "void": {"edges": {"nothing": 5}, "last_tick": 0},
        "nothing": {"edges": {"void": 5}, "last_tick": 0} # A tight loop
    }

    # 2. Create a Context with High Drag (Trigger Condition)
    ctx = CycleContext(input_text="void")
    ctx.physics = PhysicsPacket(narrative_drag=10.0, kappa=0.1)
    ctx.clean_words = ["void", "nothing"] # The input that triggers the trace

    # 3. Run ONLY the Intrusion Phase
    phase = IntrusionPhase(eng)
    ctx = phase.run(ctx)

    # 4. Check Logs
    immune_log = next((l for l in ctx.logs if "IMMUNE SYSTEM" in l), None)
    if immune_log:
        print(f"{Prisma.paint('✔ SUCCESS:', 'G')} {immune_log}")
    else:
        print(f"{Prisma.paint('✘ FAILURE:', 'R')} Immune system slept. (Did ViralTracer find the loop?)")

    # ==============================================================================
    # TEST 2: THE NAVIGATOR (NavigationPhase)
    # Goal: Force High Voltage physics and ensure Navigator assigns THE_FORGE.
    # ==============================================================================
    print(f"\n{Prisma.paint('--- TEST 2: SPATIAL MAPPING (ISOLATED) ---', 'Y')}")

    # 1. Create High Energy Physics
    ctx = CycleContext(input_text="burn")
    ctx.physics = PhysicsPacket(
        voltage=15.0,        # High Voltage
        narrative_drag=-1.0, # Negative Drag
        vector={"VEL": 0.9}, # Kinetic
        clean_words=["fire"]
    )

    # 2. Run ONLY the Navigation Phase
    # Note: We must ensure Navigator definitions are loaded.
    phase = NavigationPhase(eng)
    ctx = phase.run(ctx)

    # 3. Check Result
    loc = eng.navigator.current_location
    print(f"Physics Input: 15.0v / -1.0d")
    print(f"Navigator Result: {loc}")

    if loc == "THE_FORGE":
        print(f"{Prisma.paint('✔ SUCCESS:', 'G')} Navigator respected the Physics.")
    else:
        print(f"{Prisma.paint('✘ FAILURE:', 'R')} Navigator drifted to {loc}.")

    # ==============================================================================
    # TEST 3: THE BRIDGE (SensationPhase)
    # Goal: Generate an Impulse and ensure it attaches to the Context.
    # ==============================================================================
    print(f"\n{Prisma.paint('--- TEST 3: SYNESTHESIA (ISOLATED) ---', 'Y')}")

    # 1. Create a High-Adrenaline Context
    ctx = CycleContext(input_text="run")
    ctx.physics = PhysicsPacket(voltage=20.0, valence=-0.8) # Scary High Voltage
    eng.bio.endo.adrenaline = 0.9 # Body is racing

    # 2. Run Sensation Phase
    phase = SensationPhase(eng)
    ctx = phase.run(ctx)

    # 3. Check if Impulse was captured
    impulse = getattr(ctx, "last_impulse", None)

    if impulse:
        reflex = impulse.somatic_reflex
        print(f"Generated Reflex: '{reflex}'")
        if reflex in ["Pupils Dilating.", "Electrical Arcing.", "Gut Tightening."]:
            print(f"{Prisma.paint('✔ SUCCESS:', 'G')} Bridge is active and specific.")
        else:
            print(f"{Prisma.paint('⚠ WARNING:', 'O')} Bridge active but reflex generic: {reflex}")
    else:
        print(f"{Prisma.paint('✘ FAILURE:', 'R')} No Impulse found in Context.")

    print(f"\n{Prisma.paint('>>> DIAGNOSTIC COMPLETE', 'W')}")

if __name__ == "__main__":
    run_unit_tests()