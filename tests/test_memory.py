"""tests/test_memory.py"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from spores.memory import SubconsciousStrata, MemoryCore

try:
    import numpy as np
except ImportError:
    np = None

class TestSubconsciousStrata(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.temp_dir.name, "subconscious.jsonl")
        self.strata = SubconsciousStrata(filename=self.filepath)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialization(self):
        self.assertEqual(len(self.strata.index), 0)
        self.assertEqual(len(self.strata.metadata_log), 0)
        self.assertIsNone(self.strata.rank_bank)

    @unittest.skipIf(np is None, "NumPy is not installed; skipping mathematical rank verification.")
    def test_rank_transform(self):
        v = [10.5, 2.1, 8.8, -1.0]
        rank_v = self.strata._rank_transform(v)
        self.assertIsNotNone(rank_v)
        self.assertEqual(rank_v.dtype, np.uint16)
        self.assertEqual(list(rank_v), [3, 1, 2, 0])

    @unittest.skipIf(np is None, "NumPy is not installed; skipping ordinal burial tests.")
    def test_ordinal_burial_and_stacking(self):
        fossil_1 = {"word": "ghost", "mass": 5.0}
        success = self.strata.bury(fossil_1)
        self.assertTrue(success)
        self.assertIsNotNone(self.strata.rank_bank)
        self.assertEqual(self.strata.rank_bank.shape[0], 1)
        fossil_2 = {"word": "machine", "mass": 8.0}
        self.strata.bury(fossil_2)
        self.assertEqual(self.strata.rank_bank.shape[0], 2)

    @unittest.skipIf(np is None, "NumPy is not installed; skipping rank-cosine search.")
    def test_dredge_vibe_rank_cosine_search(self):
        self.strata.bury({"word": "echo", "mass": 2.0})
        self.strata.bury({"word": "silence", "mass": 10.0})
        self.strata.bury({"word": "void", "mass": 7.0})
        results = self.strata.dredge_vibe("silence", k=2)
        self.assertEqual(len(results), 2)
        top_result = results[0]
        self.assertIn("word", top_result)
        self.assertIn("score", top_result)
        self.assertIn("data", top_result)
        self.assertIsInstance(top_result["score"], float)
        self.assertTrue(-1.001 <= top_result["score"] <= 1.001, f"Score {top_result['score']} breached mathematical cosine bounds.")

    def test_graceful_degradation(self):
        original_np = np
        try:
            import spores.memory
            spores.memory.np = None
            self.strata.bury({"word": "safe_mode", "mass": 1.0})
            results = self.strata.dredge_vibe("safe_mode")
            self.assertEqual(results, [])
        finally:
            spores.memory.np = original_np

class TestMemoryCore(unittest.TestCase):
    def setUp(self):
        self.mock_events = MagicMock()
        self.mock_subconscious = MagicMock()
        self.mock_lexicon = MagicMock()
        dummy_config = {"CORTEX": {"EPIGENETIC_PRUNE_THRESHOLD": 10}}
        self.core = MemoryCore(events_ref=self.mock_events, subconscious_ref=self.mock_subconscious,
                               lexicon_ref=self.mock_lexicon, config_ref=dummy_config)

    def test_graph_initialization(self):
        self.assertEqual(len(self.core.graph), 0)
        self.assertEqual(len(self.core.cortical_stack), 0)

    def test_calculate_mass(self):
        self.core.graph["test_node"] = {"edges": {"a": 2.0, "b": 3.0}}
        mass = self.core.calculate_mass("test_node")
        self.assertEqual(mass, 5.0)

    def test_illuminate_resonance_and_batching(self):
        """Verify isdisjoint lexical matching and batched I/O burial."""
        self.core.graph = {"monolith": {"edges": {"a": 5.0}, "is_diamond": False}, "whisper": {"edges": {"b": 1.0}, "is_diamond": False}}
        self.mock_lexicon.get_categories_for_word.side_effect = lambda w: {"heavy", "constructive"} if w == "monolith" else {"social"}
        results = self.core.illuminate({"STR": 0.9, "BET": 0.1}, limit=5)
        self.assertTrue(any("MONOLITH" in res for res in results))

    @unittest.skipIf(np is None, "NumPy is not installed; skipping centroid math.")
    @patch('spores.memory._word_to_vector')
    def test_hebbian_wiring_and_deep_dredge(self, mock_w2v):
        mock_w2v.side_effect = lambda w: [1.0, 0.0] if w == "node_a" else [0.0, 1.0]
        self.core.graph = {"node_a": {"edges": {}, "is_diamond": False}, "node_b": {"edges": {}, "is_diamond": False}}
        self.mock_lexicon.get_categories_for_word.return_value = {"heavy"}
        self.mock_subconscious.dredge_vibe_by_vector.return_value = [
            {"word": "phantom_memory", "score": 0.88, "data": {}}]
        self.core.illuminate({"STR": 1.0}, limit=5)
        self.assertIn("node_b", self.core.graph["node_a"]["edges"], "Hebbian wiring failed on node_a.")
        self.assertIn("node_a", self.core.graph["node_b"]["edges"], "Hebbian wiring failed on node_b.")
        self.assertEqual(self.core.graph["node_a"]["edges"]["node_b"], 0.5)
        self.assertTrue(self.mock_subconscious.dredge_vibe_by_vector.called, "The Deep Dredge was never triggered.")
        self.assertIn("phantom_memory", self.core.graph, "Phantom memory was not injected into the graph.")
        self.assertIn("phantom_memory", self.core.graph["node_a"]["edges"])
        self.assertIn("phantom_memory", self.core.graph["node_b"]["edges"])
        self.assertIn("node_a", self.core.graph["phantom_memory"]["edges"])
        self.assertIn("node_b", self.core.graph["phantom_memory"]["edges"])

    def test_prune_synapses_two_pass(self):
        self.core.graph = {"strong_node": {"edges": {"weak_node": 10.0}, "is_diamond": False}, "weak_node": {"edges": {"strong_node": 0.1}, "is_diamond": False}, "diamond_node": {"edges": {}, "is_diamond": True}}
        self.core.prune_synapses(scaling_factor=0.1, prune_threshold=0.5)
        self.assertNotIn("weak_node", self.core.graph)
        self.assertIn("strong_node", self.core.graph)
        self.assertIn("diamond_node", self.core.graph)
        self.assertNotIn("weak_node", self.core.graph["strong_node"]["edges"])

if __name__ == "__main__":
    unittest.main()