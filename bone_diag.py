""" bone_diagnostic.py
 "The unexamined code is not worth executing."
 A structural stress-test for the BoneAmanita Engine.
"""

import sys
import os
import time
import json
from dataclasses import asdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from dev.bone_bus import Prisma, BoneConfig
    from dev.bone_main import BoneAmanita
    from dev.bone_lexicon import TheLexicon
except ImportError:
    print("❌ CRITICAL: Could not import 'dev' modules. Run this from the project root.")
    sys.exit(1)

class DiagnosticTool:
    def __init__(self):
        self.results = {"PASS": 0, "FAIL": 0, "WARN": 0}
        self.engine = None

    def log(self, msg, status="INFO"):
        color = Prisma.WHT
        if status == "PASS": color = Prisma.GRN
        elif status == "FAIL": color = Prisma.RED
        elif status == "WARN": color = Prisma.OCHRE
        print(f"{color}[{status}] {msg}{Prisma.RST}")
        if status in self.results:
            self.results[status] += 1

    def setup_engine(self):
        self.log("Initializing BoneAmanita (Mock Mode)...")
        mock_config = {
            "provider": "mock",
            "model": "diagnostic-unit",
            "user_name": "TEST_PILOT"}
        try:
            self.engine = BoneAmanita(mock_config)
            self.engine.engage_cold_boot()
            self.log("Engine Cold Boot Successful", "PASS")
        except Exception as e:
            self.log(f"Engine Boot Failed: {e}", "FAIL")
            sys.exit(1)

    def test_lexicon_connectivity(self):
        self.log("--- TEST 1: Lexicon Wiring ---")
        try:
            heavy_check = TheLexicon.classify("stone")
            kinetic_check = TheLexicon.classify("run")
            if heavy_check[0] == "heavy":
                self.log(f"Lexicon correctly identifies 'stone' as 'heavy' ({heavy_check[1]})", "PASS")
            else:
                self.log(f"Lexicon failed to identify 'stone'. Got: {heavy_check}", "FAIL")
            if kinetic_check[0] in ["kinetic", "explosive"]:
                self.log(f"Lexicon correctly identifies 'run' as '{kinetic_check[0]}' ({kinetic_check[1]})", "PASS")
            else:
                self.log(f"Lexicon failed to identify 'run'. Got: {kinetic_check}", "FAIL")
        except Exception as e:
            self.log(f"Lexicon Access Error: {e}", "FAIL")

    def test_physics_reaction(self):
        self.log("--- TEST 2: Physics Engine (Voltage/Drag) ---")
        self.log("Injecting High-Voltage Stimulus: 'Flash fire run explode speed'")
        packet_a = self.engine.process_turn("Flash fire run explode speed")
        volts_a = self.engine.phys.dynamics.voltage_history[-1]
        if volts_a > 12.0:
            self.log(f"System registered Voltage spike ({volts_a:.1f}v)", "PASS")
        else:
            self.log(f"System failed to react to energy. Voltage: {volts_a:.1f}v", "FAIL")
        self.log("Injecting High-Drag Stimulus: 'Heavy lead stone weight anchor'")
        self.engine.process_turn("Heavy lead stone weight anchor")
        last_phys = self.engine.phys.observer.last_physics_packet
        drag_b = last_phys.narrative_drag
        if drag_b > 2.0:
            self.log(f"System registered Mass/Drag increase ({drag_b:.1f})", "PASS")
        else:
            self.log(f"System failed to register mass. Drag: {drag_b:.1f}", "FAIL")

    def test_metabolism(self):
        self.log("--- TEST 3: Biological Systems (ATP/Metabolism) ---")
        self.engine.bio.mito.state.atp_pool = 100.0
        initial_atp = self.engine.bio.mito.state.atp_pool
        self.log(f"Initial ATP: {initial_atp}")
        for i in range(3):
            self.engine.process_turn(f"Processing cycle {i}")
        final_atp = self.engine.bio.mito.state.atp_pool
        self.log(f"Final ATP: {final_atp}")
        if final_atp < initial_atp:
            self.log("Metabolic Tax applied correctly (ATP decreased)", "PASS")
        else:
            self.log("System is creating free energy (ATP did not decrease)", "FAIL")

    def test_telemetry(self):
        self.log("--- TEST 4: Telemetry & Narrative Generation ---")
        # Check if logs are generating
        summary = self.engine.telemetry.generate_session_summary()
        if "thoughts processed" in summary.lower() or "duration" in summary.lower():
            self.log("Session Summary generated successfully", "PASS")
            print(f"   Sample Output: {summary.strip().splitlines()[0]}...")
        else:
            self.log(f"Session Summary malformed: {summary}", "FAIL")

    def run_all(self):
        print(f"\n{Prisma.CYN}=== BONEAMANITA DIAGNOSTIC SUITE ==={Prisma.RST}")
        self.setup_engine()
        self.test_lexicon_connectivity()
        self.test_physics_reaction()
        self.test_metabolism()
        self.test_telemetry()
        print(f"\n{Prisma.CYN}=== DIAGNOSTIC COMPLETE ==={Prisma.RST}")
        print(f"PASSED: {self.results['PASS']}")
        print(f"FAILED: {self.results['FAIL']}")
        print(f"WARNINGS: {self.results['WARN']}")

if __name__ == "__main__":
    tool = DiagnosticTool()
    tool.run_all()