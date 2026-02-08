""" bone_diag.py - Post-Surgical System Integrity Check """
import sys
import traceback
from bone_core import Prisma

def log(msg, status="INFO"):
    colors = {"INFO": Prisma.CYN, "OK": Prisma.GRN, "FAIL": Prisma.RED, "WARN": Prisma.OCHRE}
    print(f"{colors.get(status, Prisma.WHT)}[{status}] {msg}{Prisma.RST}")

def run_diagnostics():
    print(f"\n{Prisma.paint('♦ BONEAMANITA DIAGNOSTICS', 'M')}")
    print("==========================================")
    try:
        log("Testing bone_spores refactor...", "INFO")
        import bone_spores
        if hasattr(bone_spores, "BioParasite") and hasattr(bone_spores, "ImmuneMycelium"):
            log("New agents (BioParasite, ImmuneMycelium) detected.", "OK")
        else:
            log("Missing renamed agents in bone_spores!", "FAIL")
        if hasattr(bone_spores, "HyphalInterface"):
            log("Tumor (HyphalInterface) still detected!", "FAIL")
        else:
            log("Tumor (HyphalInterface) successfully excised.", "OK")
    except ImportError as e:
        log(f"bone_spores import failed: {e}", "FAIL")
        return
    try:
        log("Testing bone_architect wiring...", "INFO")
        import bone_architect
        log("bone_architect imported successfully.", "OK")
    except ImportError as e:
        log(f"bone_architect failed. Likely a 'bone_body' import error: {e}", "FAIL")
        print(f"{Prisma.OCHRE}>>> HINT: Check imports in 'bone_body.py'. It may still reference 'ParasiticSymbiont' or 'HyphalInterface'.{Prisma.RST}")
        return
    try:
        log("Testing bone_cycle integration...", "INFO")
        import bone_cycle
        log("bone_cycle imported successfully.", "OK")
    except ImportError as e:
        log(f"bone_cycle import failed: {e}", "FAIL")
        return
    try:
        log("Attempting Cold Boot...", "INFO")
        from bone_main import BoneAmanita, ConfigWizard
        dummy_config = {"provider": "mock", "model": "test", "user_name": "DIAGNOSTIC"}
        engine = BoneAmanita(dummy_config)
        if engine.health > 0:
            log(f"System Alive. Integrity: {engine.health}%", "OK")
            pipeline_name = engine.cycle_controller.simulator.pipeline[0].name
            log(f"Cycle Phase: {pipeline_name}", "OK")
        else:
            log("System booted but reports 0 Health.", "WARN")
    except Exception as e:
        log(f"Cold Boot Failed: {e}", "FAIL")
        traceback.print_exc()
        return
    print("==========================================")
    log("DIAGNOSTICS COMPLETE. SYSTEM STABLE.", "OK")

if __name__ == "__main__":
    run_diagnostics()