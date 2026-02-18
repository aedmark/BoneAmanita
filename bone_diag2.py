import unittest
from unittest.mock import MagicMock, patch
import math

# Import the specific organs we grafted
from bone_core import EventBus, Prisma, LoreManifest
from bone_config import BoneConfig
from bone_physics import GeodesicEngine, GeodesicConstants
from bone_inventory import GordonKnot, Item
from bone_body import MitochondrialForge, Biometrics, MetabolicGovernor, EndocrineSystem
from bone_brain import PromptComposer
from bone_akashic import TheAkashicRecord

# -------------------------------------------------------------------------
# MOCKING INFRASTRUCTURE
# -------------------------------------------------------------------------

class MockLore:
    """Simulates the JSON files we audited."""
    @staticmethod
    def get_lenses():
        return {
            "JESTER": {
                "role": "The Paradox",
                "directives": ["Break the fourth wall.", "Celebrate entropy."]
            },
            "_META_RESONANCE_": [
                {
                    "trigram": "ZHEN",
                    "lens": "MANIC",
                    "result": "STORM_CHASER",
                    "msg": "Thunder resonates."
                }
            ]
        }
    
    @staticmethod
    def get_item_gen():
        return {
            "PREFIXES": {"kinetic": ["Fast"], "heavy": ["Heavy"]},
            "BASES": {"TOOL": ["Wrench"], "ARTIFACT": ["Orb"]},
            "SUFFIXES": {"kinetic": ["of Speed"], "heavy": ["of Weight"]}
        }

# -------------------------------------------------------------------------
# TEST SUITE
# -------------------------------------------------------------------------

class TestSlashGenetics(unittest.TestCase):
    """Verifies the Physics and Metabolic grafts."""

    def setUp(self):
        self.events = EventBus()

    def test_kinetic_weight_decoupling(self):
        print(f"\n{Prisma.CYN}[PHYSICS] Testing Kinetic vs Explosive Weight...{Prisma.RST}")
        
        # Scenario 1: Pure Kinetic Word
        # Genetic Weight for Kinetic should be 2.0 (if grafted) vs Default 3.0
        # We need to ensure the engine distinguishes them.
        
        with patch.object(BoneConfig.PHYSICS, 'WEIGHT_KINETIC', 2.0), \
             patch.object(BoneConfig.PHYSICS, 'WEIGHT_EXPLOSIVE', 10.0): # Exaggerate to ensure split
            
            # Case A: Kinetic Input
            vec_k = GeodesicEngine.collapse_wavefunction(["run"], {"kinetic": 1, "explosive": 0})
            
            # Case B: Explosive Input
            vec_e = GeodesicEngine.collapse_wavefunction(["boom"], {"kinetic": 0, "explosive": 1})
            
            self.assertNotEqual(vec_k.tension, vec_e.tension, 
                "FAIL: Kinetic and Explosive words generated identical tension. Decoupling failed.")
            self.assertLess(vec_k.tension, vec_e.tension,
                "FAIL: Kinetic word (2.0) should have less tension than Explosive word (10.0).")
            
            print(f"{Prisma.GRN}   >>> PASS: Kinetic Weight (2.0) distinct from Explosive (10.0).{Prisma.RST}")

    def test_metabolic_drag_multiplier(self):
        print(f"\n{Prisma.CYN}[BODY] Testing Genetic Drag Multiplier...{Prisma.RST}")
        
        mito = MitochondrialForge(self.events)
        mito.state.atp_pool = 100.0
        
        # Mock a physics packet with drag
        class MockPhys:
            voltage = 10.0
            narrative_drag = 5.0 # Significant drag
            
        # 1. Test with Standard Multiplier (1.0)
        with patch.object(BoneConfig, 'SIGNAL_DRAG_MULTIPLIER', 1.0):
            receipt_std = mito.process_cycle(MockPhys(), Biometrics(100, 100))
            
        # 2. Test with Kinetic Multiplier (0.5) - Should burn less
        with patch.object(BoneConfig, 'SIGNAL_DRAG_MULTIPLIER', 0.5):
            receipt_kin = mito.process_cycle(MockPhys(), Biometrics(100, 100))

        # 3. Test with Heavy Multiplier (1.5) - Should burn more
        with patch.object(BoneConfig, 'SIGNAL_DRAG_MULTIPLIER', 1.5):
            receipt_hvy = mito.process_cycle(MockPhys(), Biometrics(100, 100))

        self.assertLess(receipt_kin.total_burn, receipt_std.total_burn, "Kinetic gene did not reduce burn.")
        self.assertGreater(receipt_hvy.total_burn, receipt_std.total_burn, "Heavy gene did not increase burn.")
        
        print(f"{Prisma.GRN}   >>> PASS: Metabolic Burn rates: Kin({receipt_kin.total_burn:.1f}) < Std({receipt_std.total_burn:.1f}) < Hvy({receipt_hvy.total_burn:.1f}){Prisma.RST}")


class TestSlashInventory(unittest.TestCase):
    """Verifies the Fabricator and Reflex grafts."""

    def setUp(self):
        self.events = EventBus()
        self.gordon = GordonKnot(self.events)
        # Manually load the blueprints we mocked
        self.gordon.blueprints = MockLore.get_item_gen()

    def test_fabricator_synthesis(self):
        print(f"\n{Prisma.YEL}[INVENTORY] Testing The Fabricator...{Prisma.RST}")
        
        # Simulate High Velocity Physics -> Should trigger 'kinetic' archetype
        physics_vector = {"VEL": 0.9, "STR": 0.1, "ENT": 0.0}
        
        item_id = self.gordon.synthesize_item(physics_vector)
        
        self.assertIn("FAST", item_id, "Fabricator failed to translate 'VEL' vector to 'FAST' prefix.")
        self.assertIn(item_id, self.gordon.registry, "Fabricated item not found in registry.")
        
        item = self.gordon.registry[item_id]
        print(f"{Prisma.GRN}   >>> PASS: Fabricated Item: {item.name} ({item.description}){Prisma.RST}")

    def test_reflex_protocols(self):
        print(f"\n{Prisma.YEL}[INVENTORY] Testing Survival Reflexes...{Prisma.RST}")
        
        # 1. Give Gordon an Anchor Stone
        anchor = Item(name="ANCHOR_STONE", description="Heavy.", function="ANCHOR", reflex_trigger="DRIFT_CRITICAL")
        self.gordon.registry["ANCHOR_STONE"] = anchor
        self.gordon.inventory.append("ANCHOR_STONE")
        
        # 2. Simulate Drift Critical
        phys = {"narrative_drag": 8.0, "voltage": 10.0} # Drag > 6.0 triggers drift
        
        triggered, msg = self.gordon.emergency_reflex(phys)
        
        self.assertTrue(triggered, "Anchor Stone failed to trigger.")
        self.assertEqual(phys["narrative_drag"], 0.0, "Anchor Stone failed to zero out drag.")
        self.assertNotIn("ANCHOR_STONE", self.gordon.inventory, "Anchor Stone was not consumed.")
        
        print(f"{Prisma.GRN}   >>> PASS: Anchor Stone deployed. Drag neutralized.{Prisma.RST}")


class TestSlashBrain(unittest.TestCase):
    """Verifies Lenses and Akashic Resonance."""

    def setUp(self):
        self.events = EventBus()
        self.lore_mock = MagicMock()
        self.lore_mock.get.side_effect = lambda k: MockLore.get_lenses() if k == "LENSES" else {}
        
        # Brain needs lore to load lenses
        with patch('bone_brain.LoreManifest.get_instance', return_value=self.lore_mock):
             self.composer = PromptComposer(self.lore_mock.get("system_prompts"))
             self.composer.lenses = MockLore.get_lenses() # Inject manually for test

    def test_lens_directives(self):
        print(f"\n{Prisma.MAG}[BRAIN] Testing Lens Directive Injection...{Prisma.RST}")
        
        mind_mock = {"lens": "JESTER", "role": "The Fool"}
        bio_mock = {}
        
        # Build prompt
        block = self.composer._build_persona_block(mind_mock, bio_mock, None)
        block_str = " ".join(block)
        
        self.assertIn("Break the fourth wall", block_str, "Jester directives missing from prompt.")
        print(f"{Prisma.GRN}   >>> PASS: Jester directives injected into System Prompt.{Prisma.RST}")

class TestSlashAkashic(unittest.TestCase):
    
    def setUp(self):
        self.events = EventBus()
        self.lore_mock = MagicMock()
        self.lore_mock.get.side_effect = lambda k: MockLore.get_lenses() if k == "LENSES" else {}
        self.akashic = TheAkashicRecord(self.lore_mock, self.events)

    def test_trigram_resonance(self):
        print(f"\n{Prisma.VIOLET}[AKASHIC] Testing Mythic Resonance...{Prisma.RST}")
        
        # We need to capture the event bus output
        captured_events = []
        self.events.subscribe("RESONANCE_ACHIEVED", lambda p: captured_events.append(p))
        
        # Simulate update: Lens=MANIC, Physics=VEL(High) -> ZHEN
        # ZHEN + MANIC = STORM_CHASER (per MockLore)
        payload = {
            "lens": "MANIC",
            "physics": {"vector": {"VEL": 0.9, "STR": 0.1}} # VEL maps to ZHEN
        }
        
        self.akashic._on_mythology_update(payload)
        
        self.assertTrue(len(captured_events) > 0, "Resonance event not fired.")
        self.assertEqual(captured_events[0]['result'], "STORM_CHASER", "Wrong resonance result.")
        
        print(f"{Prisma.GRN}   >>> PASS: Resonance Achieved: {captured_events[0]['result']}{Prisma.RST}")


if __name__ == "__main__":
    print(f"{Prisma.WHT}┌──────────────────────────────────────────┐{Prisma.RST}")
    print(f"{Prisma.WHT}│ SLASH GRAFT VERIFICATION SUITE           │{Prisma.RST}")
    print(f"{Prisma.WHT}│ AUDITING: GENETICS, INVENTORY, BRAIN     │{Prisma.RST}")
    print(f"{Prisma.WHT}└──────────────────────────────────────────┘{Prisma.RST}")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSlashGenetics))
    suite.addTests(loader.loadTestsFromTestCase(TestSlashInventory))
    suite.addTests(loader.loadTestsFromTestCase(TestSlashBrain))
    suite.addTests(loader.loadTestsFromTestCase(TestSlashAkashic))
    
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print(f"\n{Prisma.GRN}*** GRAFTS STABLE. SYSTEM COHERENT. ***{Prisma.RST}")
    else:
        print(f"\n{Prisma.RED}*** GRAFT REJECTION DETECTED. ***{Prisma.RST}")