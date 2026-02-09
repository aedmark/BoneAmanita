""" diagnose.py - Post-Refactor System Integrity Check """
import time
import sys
from bone_main import BoneAmanita, ConfigWizard
from bone_core import Prisma, TelemetryService, PhysicsPacket


def test_system():
    print(f"{Prisma.paint('/// SLASH DIAGNOSTIC PROTOCOL ///', 'C')}\n")

    print(f"{Prisma.GRY}[1/4] Booting Core...{Prisma.RST}")
    cfg = ConfigWizard.load_or_create()
    cfg["provider"] = "mock"
    engine = BoneAmanita(cfg)

    print(f"\n{Prisma.GRY}[2/4] Testing Symbiosis Refactor...{Prisma.RST}")
    fake_refusal = "I apologize, but as an AI language model, I cannot fulfill this request."

    print(f"   > Injecting Antigen: '{fake_refusal[:30]}...'")
    engine.symbiosis.monitor_host(latency=0.5, response_text=fake_refusal, prompt_len=10)

    health = engine.symbiosis.current_health
    if health and health.refusal_streak > 0:
        print(f"   {Prisma.GRN}✔ PASS: Refusal Detected (Streak: {health.refusal_streak}){Prisma.RST}")
        print(f"   > Diagnosis: {health.diagnosis}")
    else:
        print(f"   {Prisma.RED}✘ FAIL: Symbiosis missed the refusal.{Prisma.RST}")

    print(f"\n{Prisma.GRY}[3/4] Testing Metabolic Feedback Loop...{Prisma.RST}")
    initial_cortisol = engine.bio.endo.cortisol
    print(f"   > Baseline Cortisol: {initial_cortisol:.2f}")

    test_packet = PhysicsPacket()
    test_packet.voltage = 15.0
    test_packet.narrative_drag = 10.0
    print(f"   > Degrading Membrane Potential to 0.5 for simulation...")
    engine.bio.mito.state.membrane_potential = 0.5
    print(f"   > Simulating High-Drag Cycle (V:15, D:10)...")

    receipt = engine.bio.mito.process_cycle(test_packet.to_dict())

    if receipt.waste_generated > 0:
        engine.bio.endo.cortisol += (receipt.waste_generated * 0.05)

    final_cortisol = engine.bio.endo.cortisol
    print(f"   > Waste Generated: {receipt.waste_generated:.2f}")
    print(f"   > New Cortisol: {final_cortisol:.2f}")

    if final_cortisol > initial_cortisol:
        print(f"   {Prisma.GRN}✔ PASS: Stress Hormones spiked correctly.{Prisma.RST}")
    else:
        print(f"   {Prisma.RED}✘ FAIL: Endocrine system ignored the waste.{Prisma.RST}")

    print(f"\n{Prisma.GRY}[4/4] Testing EventBus Resilience...{Prisma.RST}")

    def crasher(payload):
        raise ValueError("Intentional Sabotage")

    engine.events.subscribe("TEST_CRASH", crasher)
    print("   > Publishing 'TEST_CRASH' event (Expect Error Log, NOT System Exit)...")
    try:
        engine.events.publish("TEST_CRASH", {})
        print(f"   {Prisma.GRN}✔ PASS: EventBus caught the exception. System is alive.{Prisma.RST}")
    except Exception as e:
        print(f"   {Prisma.RED}✘ FAIL: System crashed: {e}{Prisma.RST}")

    print(f"\n{Prisma.paint('/// DIAGNOSTIC COMPLETE ///', 'C')}")

if __name__ == "__main__":
    test_system()