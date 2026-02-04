# run_diagnostic.py
# SLASH 9.6.5 Diagnostic Harness
# "Verifying the integrity of the dome."

import sys
import os
import time

# Attempt imports with graceful failure to identify specific broken modules
try:
    from bone_shared import Prisma, BoneConfig
    from ARCHIVED.bone_amanita965 import BoneAmanita
    print(f"{Prisma.GRN}✔ Modules located. Initializing System...{Prisma.RST}")
except ImportError as e:
    print(f"\n❌ CRITICAL IMPORT FAILURE: {e}")
    print("Ensure all bone_*.py files are in the same directory.")
    sys.exit(1)

def run_diagnostics():
    print(f"{Prisma.CYN}--- BONE AMANITA DIAGNOSTIC SUITE ---{Prisma.RST}")

    # 1. INSTANTIATION TEST
    # [Fuller Lens]: Does the system assemble without collapsing?
    try:
        start_time = time.time()
        # Initialize the engine without the interactive SessionGuardian
        engine = BoneAmanita()
        elapsed = time.time() - start_time
        print(f"{Prisma.GRN}✔ Engine instantiated in {elapsed:.4f}s.{Prisma.RST}")
    except Exception as e:
        print(f"{Prisma.RED}❌ INSTANTIATION FAILED: {e}{Prisma.RST}")
        import traceback
        traceback.print_exc()
        return

    # 2. VITAL SIGNS CHECK
    # [Schur Lens]: Is the patient breathing?
    print(f"\n{Prisma.OCHRE}--- VITAL SIGNS ---{Prisma.RST}")
    metrics = engine._get_metrics()
    print(f"   Health:  {metrics['health']}")
    print(f"   Stamina: {metrics['stamina']}")
    print(f"   Tick:    {metrics['tick']}")

    if metrics['health'] > 0:
        print(f"   Status:  {Prisma.GRN}ALIVE{Prisma.RST}")
    else:
        print(f"   Status:  {Prisma.RED}NECROTIC (Check Spore Loader){Prisma.RST}")

    # 3. COMPONENT AUDIT
    # [Pinker Lens]: checking if the sub-modules (Language, Memory, Gordon) are speaking.
    print(f"\n{Prisma.OCHRE}--- COMPONENT AUDIT ---{Prisma.RST}")

    components = [
        ("Lexicon", engine.lex),
        ("Memory (Mycelium)", engine.mind.mem),
        ("Gordon (Inventory)", engine.gordon),
        ("Tension Meter", engine.phys.tension),
        ("Governor", engine.bio.governor)
    ]

    for name, ref in components:
        if ref:
            print(f"   {name}: {Prisma.GRN}ONLINE{Prisma.RST}")
        else:
            print(f"   {name}: {Prisma.RED}OFFLINE{Prisma.RST}")

    # 4. SIMULATION TEST (The "Turn")
    # [Fuller Lens]: Applying force (input) to test tensegrity.
    print(f"\n{Prisma.OCHRE}--- SIMULATION TEST ---{Prisma.RST}")
    test_input = "I pick up the heavy stone and throw it at the glass."
    print(f"   Input: \"{test_input}\"")

    try:
        # Process a single turn headlessly
        result = engine.process_turn(test_input)

        # Validate output structure
        required_keys = ["type", "ui", "logs", "metrics"]
        missing = [k for k in required_keys if k not in result]

        if missing:
            print(f"   {Prisma.RED}❌ STRUCTURE FAILURE: Missing keys {missing}{Prisma.RST}")
        else:
            print(f"   {Prisma.GRN}✔ Cycle Complete.{Prisma.RST}")
            print(f"   Response Type: {result['type']}")

            # Check if physics actually happened
            # We look for 'heavy' in the logs or counts, as our input had "stone"
            # Note: The engine encapsulates metrics; we might need to dig into internal state for verification
            # But the 'ui' usually reflects the change.
            if "stone" in result['ui'].lower() or "glass" in result['ui'].lower():
                print(f"   {Prisma.GRN}✔ Semantic Recognition Verified.{Prisma.RST}")
            else:
                print(f"   {Prisma.YEL}⚠ Semantic Warning: Response seemed generic.{Prisma.RST}")

    except Exception as e:
        print(f"   {Prisma.RED}❌ SIMULATION CRASH: {e}{Prisma.RST}")
        import traceback
        traceback.print_exc()

    # 5. CLEANUP
    # [Fuller Lens]: Leave no trace.
    print(f"\n{Prisma.OCHRE}--- CLEANUP ---{Prisma.RST}")
    session_file = engine.mind.mem.filename
    if os.path.exists(session_file):
        try:
            # We don't want to leave junk session files from tests
            # But we should be careful not to delete real ones if the ID logic changed.
            # For a test, we might normally mock the filesystem, but this is a live integration test.
            # Let's just notify.
            print(f"   Session File Created: {Prisma.GRY}{session_file}{Prisma.RST}")
            print(f"   (You may delete this manually or keep it as a test artifact.)")
        except Exception as e:
            print(f"   Cleanup Warning: {e}")

    print(f"\n{Prisma.CYN}--- DIAGNOSTIC COMPLETE ---{Prisma.RST}")

if __name__ == "__main__":
    run_diagnostics()