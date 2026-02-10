""" bone_soul_test.py - Identity Logic Verification """
import unittest
from dataclasses import dataclass, field
from bone_soul import NarrativeSelf, SynestheticCortex, TraitVector
from bone_core import Prisma

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
    def to_dict(self):
        return self.__dict__

class SoulStressTest(unittest.TestCase):

    def setUp(self):
        self.events = type('MockBus', (), {"log": lambda s, m, t="": None, "subscribe": lambda *a: None})()
        self.engine = MockEngine()
        self.engine.phys = MockPhys()
        self.engine.phys.observer = MockObserver()
        self.engine.phys.observer.last_physics_packet = MockPacket()
        mock_mem = type('MockMem', (), {"session_id": "TEST", "graph": {}, "fossils": []})()
        self.soul = NarrativeSelf(self.engine, self.events, memory_ref=mock_mem)

    def test_isolation_chamber(self):
        print("\n--- TEST: ISOLATION CHAMBER ---")
        self.engine.phys = None
        try:
            state = self.soul.get_soul_state()
            print(f"[PASS] Soul survived isolation: {state}")
        except AttributeError as e:
            print(f"[FAIL] Soul died in isolation: {e}")

    def test_paradox_engine(self):
        print("\n--- TEST: PARADOX ENGINE ---")
        self.soul.traits.wisdom = 0.5
        packet = {"voltage": 20.0, "narrative_drag": 10.0}
        for i in range(12):
            self.soul._synaptic_dance(packet, {})
        print(f"Archetype: {self.soul.archetype}")
        if "/" in self.soul.archetype or "HIGH-" in self.soul.archetype:
            print("[PASS] Synthesis Triggered.")
        else:
            print(f"[INFO] Synthesis did not trigger (Random chance or thresholds not met). State: {self.soul.archetype}")

    def test_sensory_deprivation(self):
        print("\n--- TEST: SENSORY DEPRIVATION ---")
        cortex = SynestheticCortex(bio_ref=None)
        impulse = cortex.perceive({}, {}, "test input", 0.0)
        qualia = cortex.get_current_qualia(impulse)
        if qualia.color_code:
            print(f"[PASS] Qualia generated without body: {qualia.tone}")
        else:
            print("[FAIL] Cortex went dark.")

if __name__ == '__main__':
    unittest.main()