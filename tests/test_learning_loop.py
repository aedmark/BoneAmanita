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
        self.memory = MagicMock()
        self.memory.memory_core = MagicMock()
        self.akashic = MagicMock()
        self.consolidator = TheConsolidator(self.events, self.memory, self.akashic)

    def test_shadow_engagement_reinforcement(self):
        """
        Tests that when the Cortex publishes a SHADOW_ENGAGED event,
        the Consolidator catches it and physically strengthens the synaptic link.
        """
        self.events.publish("SHADOW_ENGAGED", {
            "source": "quantum_mechanics",
            "target": "string_theory",
            "user_input": "tell me more about string_theory"
        })
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
        self.events.publish("RESONANCE_ACHIEVED", {
            "result": "Dialectical Synthesis",
            "msg": "The user successfully merged two opposing architectural forces."
        })
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
        real_akashic = TheAkashicRecord(lore_manifest=MockLore.get_instance(), events_ref=self.events)
        MockConfig.BIO.DEPTH_TAX_MULT = 2.0
        real_akashic.subconscious_strata.append({
            "concept": "obsolete_syntax",
            "data": {"mass": 6.0}
        })
        yield_val, msg = real_akashic.trigger_autophagy()
        self.assertEqual(yield_val, 25.0)
        self.assertIn("obsolete_syntax", msg)
        self.assertIn("Recovered 25.0 ATP", msg)
        self.assertEqual(MockConfig.BIO.DEPTH_TAX_MULT, 1.98)


if __name__ == '__main__':
    unittest.main()
