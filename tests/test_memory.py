"""tests/test_memory.py"""

import unittest
import tempfile
import os
import json
from unittest.mock import MagicMock
from spores.memory import SubconsciousStrata, MemoryCore

try:
    import numpy as np
except ImportError:
    np = None

class TestSubconsciousStrata(unittest.TestCase):
    def setUp(self):
        # Create an isolated file system for the memory bank
        self.temp_dir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.temp_dir.name, "subconscious.jsonl")
        self.strata = SubconsciousStrata(filename=self.filepath)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialization(self):
        """Verify the strata boots with clean, empty rank banks."""
        self.assertEqual(len(self.strata.index), 0)
        self.assertEqual(len(self.strata.metadata_log), 0)
        self.assertIsNone(self.strata.rank_bank)

    @unittest.skipIf(np is None, "NumPy is not installed; skipping mathematical rank verification.")
    def test_rank_transform(self):
        """
        Verify Nelson's double-argsort logic.
        It must convert absolute floats into relative ordinal integer-floats.
        """
        # Vector with distinct magnitudes
        v = [10.5, 2.1, 8.8, -1.0]

        # Expected rank order (lowest to highest):
        # -1.0 is rank 0
        #  2.1 is rank 1
        #  8.8 is rank 2
        # 10.5 is rank 3
        # So the result should be [3., 1., 2., 0.]

        rank_v = self.strata._rank_transform(v)

        self.assertIsNotNone(rank_v)
        self.assertEqual(list(rank_v), [3.0, 1.0, 2.0, 0.0])

    @unittest.skipIf(np is None, "NumPy is not installed; skipping ordinal burial tests.")
    def test_ordinal_burial_and_stacking(self):
        """Verify that burying a memory safely appends it to the native rank_bank matrix."""
        # Bury first memory
        fossil_1 = {"word": "ghost", "mass": 5.0}
        success = self.strata.bury(fossil_1)

        self.assertTrue(success)
        self.assertIsNotNone(self.strata.rank_bank)
        self.assertEqual(self.strata.rank_bank.shape[0], 1) # 1 row

        # Bury second memory
        fossil_2 = {"word": "machine", "mass": 8.0}
        self.strata.bury(fossil_2)

        self.assertEqual(self.strata.rank_bank.shape[0], 2) # 2 rows stacked

    @unittest.skipIf(np is None, "NumPy is not installed; skipping rank-cosine search.")
    def test_dredge_vibe_rank_cosine_search(self):
        """Verify the matrix dot product returns the correct structural format."""
        self.strata.bury({"word": "echo", "mass": 2.0})
        self.strata.bury({"word": "silence", "mass": 10.0})
        self.strata.bury({"word": "void", "mass": 7.0})

        # Search for "silence" - it should rank highly against itself or similar topology
        results = self.strata.dredge_vibe("silence", k=2)

        # Verify the new dictionary output structure
        self.assertEqual(len(results), 2)
        top_result = results[0]

        self.assertIn("word", top_result)
        self.assertIn("score", top_result)
        self.assertIn("data", top_result)
        self.assertIsInstance(top_result["score"], float)

    def test_graceful_degradation(self):
        """Ensure the system doesn't panic if numpy goes missing in a strict environment."""
        original_np = np
        try:
            # Force simulate missing numpy
            import spores.memory
            spores.memory.np = None

            # Should safely bury without crashing
            self.strata.bury({"word": "safe_mode", "mass": 1.0})

            # Should safely return empty list without crashing
            results = self.strata.dredge_vibe("safe_mode")
            self.assertEqual(results, [])

        finally:
            spores.memory.np = original_np

class TestMemoryCore(unittest.TestCase):
    def setUp(self):
        self.mock_events = MagicMock()
        self.mock_subconscious = MagicMock()
        self.mock_lexicon = MagicMock()

        # Provide a dummy config dictionary to bypass config file reads
        dummy_config = {"CORTEX": {"EPIGENETIC_PRUNE_THRESHOLD": 10}}

        self.core = MemoryCore(
            events_ref=self.mock_events,
            subconscious_ref=self.mock_subconscious,
            lexicon_ref=self.mock_lexicon,
            config_ref=dummy_config
        )

    def test_graph_initialization(self):
        self.assertEqual(len(self.core.graph), 0)
        self.assertEqual(len(self.core.cortical_stack), 0)

    def test_calculate_mass(self):
        self.core.graph["test_node"] = {"edges": {"a": 2.0, "b": 3.0}}
        mass = self.core.calculate_mass("test_node")
        self.assertEqual(mass, 5.0)

if __name__ == "__main__":
    unittest.main()