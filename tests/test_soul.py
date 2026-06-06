"""tests/test_soul.py"""

import unittest
from unittest.mock import MagicMock, patch
from soul.traitvector import TraitVector
from soul.narrativeself import NarrativeSelf, CoreMemory
from soul.oroboros import TheOroboros
from presets import BoneConfig

try:
    from tests.base import BoneTestCase
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from tests.base import BaseTest as BoneTestCase

class SoulSubstrateTests(BoneTestCase):
    def test_trait_vector_dynamic_normalization(self):
        tv = TraitVector()
        tv.curiosity = 1.0
        tv.cynicism = 0.0
        tv.wisdom = 0.5
        tv.normalize(0.5)
        self.assertAlmostEqual(tv.curiosity, 0.75, msg="Curiosity failed to normalize dynamically.")
        self.assertAlmostEqual(tv.cynicism, 0.25, msg="Cynicism failed to normalize dynamically.")
        self.assertAlmostEqual(tv.wisdom, 0.3, msg="Wisdom failed to respect its unique dynamic target of 0.1.")

    @patch('soul.narrativeself.ux_format', return_value=None)
    @patch('soul.narrativeself.ux', return_value=None)
    def test_narrative_self_ux_safety(self, mock_ux, mock_ux_format):
        events_mock = MagicMock()
        memory_mock = MagicMock()
        soul = NarrativeSelf(engine_ref=MagicMock(), events_ref=events_mock, memory_ref=memory_mock)
        try:
            soul.force_mutation("THE ARCHITECT")
        except AttributeError as e:
            self.fail(f"[CRITICAL] force_mutation crashed with missing UX strings: {e}")
        self.assertEqual(soul.archetype, "THE ARCHITECT")
        try:
            soul.current_obsession = None
            state_str = soul.get_soul_state()
            self.assertIsInstance(state_str, str)
        except AttributeError as e:
            self.fail(f"[CRITICAL] get_soul_state crashed with missing UX strings: {e}")

    @patch('soul.oroboros.ux_format', return_value=None)
    @patch('soul.oroboros.ux', return_value=None)
    def test_oroboros_missing_lore_safety(self, mock_ux, mock_ux_format):
        oro = TheOroboros(config_ref=BoneConfig)
        soul_mock = MagicMock()
        soul_mock.eng.trauma_accum = {"abandonment": 15.0}
        soul_mock.core_memories = [CoreMemory(timestamp=0, trigger_words=["void"], emotional_flavor="LUCID", lesson="The void stares back.",
                       impact_voltage=10.0)]
        try:
            oro.crystallize("TOXICITY", soul_mock)
        except AttributeError as e:
            self.fail(f"[CRITICAL] Oroboros crystallize crashed with missing UX strings: {e}")
        try:
            oro.apply_legacy({}, {})
        except AttributeError as e:
            self.fail(f"[CRITICAL] Oroboros apply_legacy crashed with missing UX strings: {e}")

if __name__ == '__main__':
    unittest.main()