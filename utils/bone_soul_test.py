""" dev/bone_soul_test.py """
import unittest
from dataclasses import dataclass
from bone_soul import NarrativeSelf, SynestheticCortex, TraitVector


@dataclass
class MockEngine:
    tick_count: int = 10
    phys: 'MockPhys' = None
    lex: 'MockLexicon' = None
    akashic: 'MockAkashic' = None

@dataclass
class MockPhys:
    observer: 'MockObserver' = None
    def to_dict(self): return {"voltage": 10.0}

@dataclass
class MockObserver:
    last_physics_packet: 'MockPacket' = None

@dataclass
class MockPacket:
    clean_words: list
    voltage: float = 0.0
    narrative_drag: float = 0.0
    perfection_streak: int = 0

class SoulStressTest(unittest.TestCase):

    def setUp(self):
        self.events = type('MockBus', (), {"log": lambda s, m, t="": print(f"[{t}] {m}"), "subscribe": lambda *a: None})()
        self.engine = MockEngine()
        self.soul = NarrativeSelf(self.engine, self.events)

    def test_isolation_chamber(self):
        """ Fracture 1: Can the Soul think if the Physics engine is dead? """
        print("\n--- TEST: ISOLATION CHAMBER ---")
        self.engine.phys = None

        try:
            state = self.soul.get_soul_state()
            print(f"[PASS] Soul survived isolation: {state}")
        except AttributeError as e:
            print(f"[FAIL] Soul died in isolation: {e}")

    def test_paradox_engine(self):
        """ Fracture 3: Does Synthesis actually do anything? """
        print("\n--- TEST: PARADOX ENGINE ---")
        self.soul.traits.wisdom = 0.5

        packet = {"voltage": 20.0, "narrative_drag": 10.0}

        for i in range(12):
            self.soul._synaptic_dance(packet, {})

        print(f"Archetype: {self.soul.archetype}")
        if "/" in self.soul.archetype or "HIGH-" in self.soul.archetype:
            print("[PASS] Synthesis Triggered.")
        else:
            print("[FAIL] Synthesis failed to trigger.")

    def test_sensory_deprivation(self):
        """ Fracture 2 & General Safety """
        print("\n--- TEST: SENSORY DEPRIVATION ---")
        cortex = SynestheticCortex(bio_ref=None)
        impulse = cortex.perceive({})
        qualia = cortex.get_current_qualia(impulse)

        if qualia.color_code:
            print(f"[PASS] Qualia generated without body: {qualia.tone}")
        else:
            print("[FAIL] Cortex went dark.")

if __name__ == '__main__':
    unittest.main()