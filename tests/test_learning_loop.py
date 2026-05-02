"""tests/test_learning_loop.py"""

import unittest
from unittest.mock import MagicMock, patch
from core import EventBus
from machine.consolidator import TheConsolidator
from brain.akashic import TheAkashicRecord
from presets import BoneConfig


class TestLearningLoop(unittest.TestCase):
    def setUp(self):
        """Set up the mock environment and instantiate the Consolidator."""
        self.events = EventBus()

        # Mock the deep storage layers
        self.memory = MagicMock()
        self.memory.memory_core = MagicMock()
        self.akashic = MagicMock()

        # Wire up the Consolidator just like genesis.py does
        self.consolidator = TheConsolidator(self.events, self.memory, self.akashic)

    def test_shadow_engagement_reinforcement(self):
        """
        Tests that when the Cortex publishes a SHADOW_ENGAGED event,
        the Consolidator catches it and physically strengthens the synaptic link.
        """
        # 1. Fire the event that cortex.py would emit when a user engages a shadow concept
        self.events.publish("SHADOW_ENGAGED", {
            "source": "quantum_mechanics",
            "target": "string_theory",
            "user_input": "tell me more about string_theory"
        })

        # 2. Verify the Consolidator caught it and told memory.py to reinforce the link
        self.memory.memory_core.strengthen_link.assert_called_once_with(
            source="quantum_mechanics",
            target="string_theory",
            rate=2.0,
            decay=0.85
        )

    def test_epigenetic_boon_recording(self):
        """
        Tests that when the system achieves profound resonance,
        it writes an Epigenetic Boon to the Akashic Record.
        """
        # 1. Fire the resonance event from the mythology update loop
        self.events.publish("RESONANCE_ACHIEVED", {
            "result": "Dialectical Synthesis",
            "msg": "The user successfully merged two opposing architectural forces."
        })

        # 2. Verify the Consolidator instructed Akashic to record the glimmer
        self.akashic.record_glimmer.assert_called_once_with(
            concept="Dialectical Synthesis",
            paradigm="The user successfully merged two opposing architectural forces."
        )

    @patch('brain.akashic.BoneConfig')
    @patch('brain.akashic.LoreManifest')
    def test_composting_autophagy(self, MockLore, MockConfig):
        """
        Tests the modified Autophagy logic. Higher mass memories should
        yield more ATP and permanently increase engine efficiency.
        """
        # 1. Setup a REAL Akashic record for this specific test
        real_akashic = TheAkashicRecord(lore_manifest=MockLore.get_instance(), events_ref=self.events)

        # 2. Mock the starting biological depth tax
        MockConfig.BIO.DEPTH_TAX_MULT = 2.0

        # 3. Bury a memory with a specific mass (e.g., Mass = 6.0)
        real_akashic.subconscious_strata.append({
            "concept": "obsolete_syntax",
            "data": {"mass": 6.0}
        })

        # 4. Trigger Autophagy
        yield_val, msg = real_akashic.trigger_autophagy()

        # 5. Verify the Dynamic Math: min(50.0, 10.0 + (6.0 * 2.5)) = 25.0 ATP
        self.assertEqual(yield_val, 25.0)
        self.assertIn("obsolete_syntax", msg)
        self.assertIn("Recovered 25.0 ATP", msg)

        # 6. Verify systemic efficiency improved (DEPTH_TAX_MULT went down by 0.02)
        self.assertEqual(MockConfig.BIO.DEPTH_TAX_MULT, 1.98)


if __name__ == '__main__':
    unittest.main()