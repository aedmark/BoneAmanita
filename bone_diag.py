""" bone_diagnostic.py - "The unexamined code is not worth executing."
    v2.1: Deep System Analysis (Patched for Tangibility)
"""

import sys, os, time, json, random
from dataclasses import asdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from dev.bone_bus import Prisma, BoneConfig
    from dev.bone_main import BoneAmanita
    from dev.bone_lexicon import TheLexicon
    from dev.bone_architect import PanicRoom
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
        BoneConfig.VERBOSE_LOGGING = False
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
        self.log("\n--- TEST 1: Lexicon Wiring ---")
        try:
            heavy_check = TheLexicon.classify("stone")
            kinetic_check = TheLexicon.classify("run")
            if heavy_check[0] == "heavy":
                self.log(f"Lexicon correctly identifies 'stone' as 'heavy' ({heavy_check[1]})", "PASS")
            else:
                self.log(f"Lexicon failed to identify 'stone'. Got: {heavy_check}", "FAIL")
            if kinetic_check[0] in ["kinetic", "explosive", "kinetic"]:
                self.log(f"Lexicon correctly identifies 'run' as '{kinetic_check[0]}'", "PASS")
            else:
                self.log(f"Lexicon failed to identify 'run'. Got: {kinetic_check}", "FAIL")
        except Exception as e:
            self.log(f"Lexicon Access Error: {e}", "FAIL")

    def test_physics_reaction(self):
        self.log("\n--- TEST 2: Physics Engine (Voltage/Drag) ---")
        self.log("Injecting High-Voltage Stimulus: 'Flash fire run explode speed'")
        self.engine.process_turn("Flash fire run explode speed")
        packet_a = self.engine.phys.observer.last_physics_packet
        if packet_a.voltage > 12.0:
            self.log(f"System registered Voltage spike ({packet_a.voltage:.1f}v)", "PASS")
        else:
            self.log(f"System failed to react to energy. Voltage: {packet_a.voltage:.1f}v", "FAIL")
        self.log("Injecting High-Drag Stimulus: 'Heavy lead stone weight anchor'")
        self.engine.process_turn("Heavy lead stone weight anchor")
        packet_b = self.engine.phys.observer.last_physics_packet
        if packet_b.narrative_drag > 2.0:
            self.log(f"System registered Mass/Drag increase ({packet_b.narrative_drag:.1f})", "PASS")
        else:
            self.log(f"System failed to register mass. Drag: {packet_b.narrative_drag:.1f}", "FAIL")

    def test_metabolism(self):
        self.log("\n--- TEST 3: Biological Systems (ATP/Metabolism) ---")
        self.engine.bio.mito.state.atp_pool = 100.0
        initial_atp = self.engine.bio.mito.state.atp_pool
        self.engine.process_turn("Thinking deeply about complex structures")
        final_atp = self.engine.bio.mito.state.atp_pool
        self.log(f"ATP Delta: {initial_atp} -> {final_atp}")
        if final_atp < initial_atp:
            self.log("Metabolic Tax applied correctly (ATP decreased)", "PASS")
        else:
            self.log("System is creating free energy (ATP did not decrease)", "FAIL")

    def test_memory_encoding(self):
        self.log("\n--- TEST 4: Mycelial Memory Encoding ---")
        unique_token = f"test_marker_{int(time.time())}"
        self.log(f"Injecting unique memory token: '{unique_token}'")
        result = self.engine.process_turn(f"I am placing a heavy lead stone {unique_token} in the garden.")
        if unique_token in self.engine.mind.mem.graph:
            self.log(f"Memory successfully encoded '{unique_token}' into Graph.", "PASS")
        else:
            self.log(f"Memory failed to encode '{unique_token}'.", "FAIL")
            if "logs" in result:
                print(f"{Prisma.GRY}   Last Logs: {result['logs'][-2:]}{Prisma.RST}")

    def test_inventory_mechanics(self):
        self.log("\n--- TEST 5: Gordon Knot (Inventory) ---")
        test_item = "OLD_KEY"
        msg = self.engine.gordon.acquire(test_item)
        if test_item in self.engine.gordon.inventory:
            self.log(f"GordonKnot accepted item: {test_item}", "PASS")
        else:
            self.log(f"GordonKnot failed to acquire item.", "FAIL")
        self.log("Simulating tool use audit...")
        self.engine.tinkerer.audit_tool_use(self.engine.phys.observer.last_physics_packet, self.engine.gordon.inventory)
        if test_item in self.engine.tinkerer.tool_confidence:
            self.log("Tinkerer is tracking tool confidence.", "PASS")
        else:
            self.log("Tinkerer ignored the inventory.", "WARN")

    def test_dream_engine(self):
        self.log("\n--- TEST 6: Oneiric Cycles (Dreaming) ---")
        try:
            dream_packet = self.engine.mind.dreamer.enter_rem_cycle(self.engine.mind.mem)
            if dream_packet and "text" in dream_packet:
                self.log(f"REM Cycle Successful. Dream: '{dream_packet['text']}'", "PASS")
            else:
                self.log("REM Cycle returned empty void.", "FAIL")
        except Exception as e:
            self.log(f"Dream Engine Crash: {e}", "FAIL")

    def test_resilience(self):
        self.log("\n--- TEST 7: Panic Protocols (Resilience) ---")
        safe_phys = PanicRoom.get_safe_physics()
        if safe_phys.zone == "PANIC_ROOM":
            self.log("PanicRoom correctly generating Safe Physics.", "PASS")
        else:
            self.log("PanicRoom generating unsafe physics.", "FAIL")
        if self.engine.system_health.physics_online:
            self.log("System Health Monitor is Online.", "PASS")
        else:
            self.log("System Health reports offline (Unexpected).", "WARN")

    def run_all(self):
        print(f"\n{Prisma.CYN}=== BONEAMANITA v2.1 DIAGNOSTIC SUITE ==={Prisma.RST}")
        self.setup_engine()
        self.test_lexicon_connectivity()
        self.test_physics_reaction()
        self.test_metabolism()
        self.test_memory_encoding()
        self.test_inventory_mechanics()
        self.test_dream_engine()
        self.test_resilience()
        print(f"\n{Prisma.CYN}=== DIAGNOSTIC COMPLETE ==={Prisma.RST}")
        print(f"PASSED: {self.results['PASS']}")
        print(f"FAILED: {self.results['FAIL']}")
        print(f"WARNINGS: {self.results['WARN']}")
        if self.results['FAIL'] > 0:
            print(f"{Prisma.RED}❌ SYSTEM UNSTABLE{Prisma.RST}")
            sys.exit(1)
        else:
            print(f"{Prisma.GRN}✔ SYSTEM STABLE{Prisma.RST}")
            sys.exit(0)

if __name__ == "__main__":
    tool = DiagnosticTool()
    tool.run_all()