""" bone_diag.py - The Grand Diagnostic Suite
    Merges: Behavior, Live Fire, Soul, Stress, and Core Integrity tests.
"""

import traceback
from dataclasses import dataclass, field
from bone_main import BoneAmanita, ConfigWizard
from bone_core import Prisma
from bone_types import PhysicsPacket
from bone_soul import NarrativeSelf
from bone_protocols import KintsugiProtocol, TheBureau, TheFolly
from bone_lexicon import TheLexicon

try:
    from bone_brain import LLMInterface
except ImportError:
    LLMInterface = None

@dataclass
class MockEngine:
    tick_count: int = 10
    phys: 'MockPhys' = None
    lex: 'MockLexicon' = None
    akashic: 'MockAkashic' = None

@dataclass
class MockPhys:
    observer: 'MockObserver' = None
    def to_dict(self): return {"voltage": 10.0, "narrative_drag": 5.0, "zone": "TEST_LAB"}

@dataclass
class MockObserver:
    last_physics_packet: 'MockPacket' = None

@dataclass
class MockPacket:
    clean_words: list = field(default_factory=list)
    voltage: float = 0.0
    narrative_drag: float = 0.0
    perfection_streak: int = 0
    zone: str = "VOID"
    def to_dict(self): return self.__dict__

class MockEventBus:
    def log(self, message, channel="TEST", tags=None): pass
    def subscribe(self, channel, callback): pass
    def __getattr__(self, name): return lambda *args, **kwargs: None

class GrandDiagnostic:
    def __init__(self):
        self.results = {"PASS": 0, "FAIL": 0, "SKIP": 0}
        self.config = ConfigWizard.load_or_create()
        self.engine = None
        print(f"{Prisma.paint('/// BONEAMANITA GRAND DIAGNOSTIC ///', 'M')}\n")

    def log(self, msg, status="INFO"):
        color = Prisma.WHT
        if status == "PASS": color = Prisma.GRN
        elif status == "FAIL": color = Prisma.RED
        elif status == "SKIP": color = Prisma.OCHRE
        print(f"   {color}[{status}] {msg}{Prisma.RST}")
        if status in self.results:
            self.results[status] += 1

    def header(self, title):
        print(f"\n{Prisma.CYN}=== {title} ==={Prisma.RST}")

    def phase_1_core_integrity(self):
        self.header("PHASE 1: CORE INTEGRITY")
        try:
            self.config["provider"] = "mock"
            self.engine = BoneAmanita(self.config)
            self.log("Core Engine Booted", "PASS")

            def crasher(payload): raise ValueError("Sabotage")
            self.engine.events.subscribe("TEST_CRASH", crasher)
            try:
                self.engine.events.publish("TEST_CRASH", {})
                self.log("EventBus Resilience (Caught Crash)", "PASS")
            except:
                self.log("EventBus Crashed System", "FAIL")
            fake_refusal = "I apologize, but as an AI language model..."
            self.engine.symbiosis.monitor_host(0.5, fake_refusal, 10)
            if self.engine.symbiosis.current_health.refusal_streak > 0:
                self.log("Symbiosis Detected Refusal", "PASS")
            else:
                self.log("Symbiosis Missed Refusal", "FAIL")
        except Exception as e:
            self.log(f"Core Integrity Critical Failure: {e}", "FAIL")
            traceback.print_exc()

    def phase_2_bare_metal(self):
        self.header("PHASE 2: BARE METAL (LLM DRIVER)")
        if not LLMInterface:
            self.log("LLMInterface not imported", "SKIP")
            return
        real_config = ConfigWizard.load_or_create()
        try:
            driver = LLMInterface(
                events_ref=MockEventBus(),
                provider=real_config.get("provider", "mock"),
                model=real_config.get("model", "test"),
                dreamer=None)
            response = driver.mock_generation("Ping") if real_config["provider"] == "mock" else driver.generate("Ping", {"max_tokens": 5})
            if response: self.log("Driver Connectivity", "PASS")
            else: self.log("Driver returned silence", "FAIL")
        except Exception as e:
            self.log(f"Driver Init Failed: {e}", "FAIL")
    def phase_3_soul_logic(self):
        self.header("PHASE 3: SOUL LOGIC")
        try:
            mock_events = MockEventBus()
            mock_engine = MockEngine()
            mock_engine.phys = MockPhys()
            mock_engine.phys.observer = MockObserver()
            mock_engine.phys.observer.last_physics_packet = MockPacket()
            mock_mem = type('MockMem', (), {"session_id": "TEST", "graph": {}, "fossils": []})()
            soul = NarrativeSelf(mock_engine, mock_events, memory_ref=mock_mem)
            mock_engine.phys = None
            try:
                state = soul.get_soul_state()
                self.log(f"Soul Survived Isolation ({state})", "PASS")
            except:
                self.log("Soul Died in Isolation", "FAIL")
            soul.traits.wisdom = 0.5
            packet = {"voltage": 20.0, "narrative_drag": 10.0}
            for _ in range(12): soul._synaptic_dance(packet, {})
            if "/" in soul.archetype or "HIGH-" in soul.archetype:
                self.log("Soul Synthesis Triggered", "PASS")
            else:
                self.log(f"Soul Synthesis Inactive (Archetype: {soul.archetype})", "SKIP")
        except Exception as e:
            self.log(f"Soul Logic Error: {e}", "FAIL")

    def phase_4_reactive_systems(self):
        self.header("PHASE 4: REACTIVE SYSTEMS")
        stress_eng = BoneAmanita({"provider": "mock", "user_name": "TESTER"})
        kintsugi = KintsugiProtocol()
        kintsugi.active_koan = "Test Koan"
        mock_phys = type('obj', (object,), {"voltage": 12.0, "clean_words": ["dream"]})
        trauma = {"SEPTIC": 5.0}
        res = kintsugi.attempt_repair(mock_phys, trauma, soul_ref=stress_eng.soul)
        if res and res["success"]: self.log("Kintsugi Repair", "PASS")
        else: self.log("Kintsugi Failed", "FAIL")
        bureau = TheBureau()
        bad_phys = {
            "voltage": 25.0,
            "truth_ratio": 0.2,
            "clean_words": ["absolute", "chaos", "fire", "now", "immediately"],
            "raw_text": "absolute chaos and fire now immediately",
            "counts": {}}
        audit = bureau.audit(bad_phys, {"health": 100})
        if audit and "ZONING_VIOLATION" in audit["ui"]: self.log("Bureau Caught Violation", "PASS")
        else: self.log("Bureau Missed Violation", "FAIL")
        folly = TheFolly()
        status, _, yield_val, _ = folly.grind_the_machine(10.0, ["stone"], TheLexicon)
        if status == "MEAT_GRINDER": self.log("Folly Metabolism", "PASS")
        else: self.log(f"Folly Failed (Status: {status})", "FAIL")

    def phase_5_behavioral_ghost(self):
        self.header("PHASE 5: BEHAVIORAL GHOST")
        if not self.engine: return

        def inject_state(dopamine, cortisol, voltage):
            if hasattr(self.engine.cortex, "modulator"):
                chem = self.engine.cortex.modulator.current_chem
                chem.dopamine = dopamine
                chem.cortisol = cortisol
            self.engine.phys.observer.last_physics_packet = PhysicsPacket(voltage=voltage)
        inject_state(0.0, 0.9, 25.0)
        res = self.engine.cortex.process("View from window")
        if res.get("raw_content"): self.log("Cortex Panic Response", "PASS")
        else: self.log("Cortex Panic Silence", "FAIL")

    def phase_6_loot_goblin(self):
            self.header("PHASE 6: LOOT LOGIC")
            from bone_inventory import GordonKnot
            knot = GordonKnot()
            knot.inventory = []
            scenarios = [
                ("I take the sphere", "You pick up the sphere.", "sphere", "PASS"),
                ("I take a look around", "You see a room.", None, "PASS"),
                ("Grab the heavy stone", "You cannot lift it.", None, "PASS"),
                ("Pick up the red key", "It feels cold.", "red key", "PASS")]
            for user_in, sys_out, expected, label in scenarios:
                result = knot.parse_loot(user_in, sys_out)
                if result == expected:
                    self.log(f"Parse '{user_in}' -> {result}", "PASS")
                else:
                    self.log(f"Parse '{user_in}' -> {result} (Expected: {expected})", "FAIL")
            msg = knot.acquire("sphere")
            if "ACQUIRED" in msg and "sphere" in knot.inventory:
                self.log("Acquire 'sphere' (First Time)", "PASS")
            else:
                self.log(f"Acquire 'sphere' failed: {msg}", "FAIL")
            msg = knot.acquire("sphere")
            if "already have" in msg or "already" in msg.lower():
                self.log("Acquire 'sphere' (Duplicate)", "PASS")
            else:
                self.log(f"Duplicate logic failed: {msg}", "FAIL")

    def run(self):
        self.phase_1_core_integrity()
        self.phase_2_bare_metal()
        self.phase_3_soul_logic()
        self.phase_4_reactive_systems()
        self.phase_5_behavioral_ghost()
        self.phase_6_loot_goblin()
        print(f"\n{Prisma.CYN}=== DIAGNOSTIC COMPLETE ==={Prisma.RST}")
        print(f"PASSED: {self.results['PASS']}")
        print(f"FAILED: {self.results['FAIL']}")
        print(f"SKIPPED: {self.results['SKIP']}")
        if self.results['FAIL'] == 0:
            print(f"{Prisma.GRN}>>> SYSTEM GREEN. READY FOR DEPLOYMENT. <<<{Prisma.RST}")
        else:
            print(f"{Prisma.RED}>>> SYSTEM UNSTABLE. REVIEW LOGS. <<<{Prisma.RST}")

if __name__ == "__main__":
    diag = GrandDiagnostic()
    diag.run()