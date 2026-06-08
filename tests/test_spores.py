"""tests/test_spores.py"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Guarantee test runners discover the Base class correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.base import BoneTestCase
from presets import BoneConfig

from spores.io import LocalFileSporeLoader
from spores.memory import MemoryCore
from spores.biome import BioLichen, BioParasite
from spores.genetics import LiteraryReproduction


class SporeEcosystemTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_local_loader_roundtrip(self):
        # FIX: BoneTestCase globally mocks save_spore to intercept and log disk writes.
        # We must temporarily halt the patch to test the actual file I/O mechanism.
        self.spore_patcher.stop()
        try:
            # Isolate the loader to a temporary directory
            loader = LocalFileSporeLoader(directory=self.test_dir)
            test_filename = "session_test_spore.json"
            test_data = {
                "session_id": "test_spore",
                "core_graph": {"node_a": {"edges": {"node_b": 5.0}}},
                "trauma_vector": {"ENT": 0.8}
            }

            # Test Save
            saved_path = loader.save_spore(test_filename, test_data)
            self.assertIsNotNone(saved_path, "[FAIL] LocalFileSporeLoader failed to return a saved path.")
            self.assertTrue(os.path.exists(saved_path), "[FAIL] Spore file was not actually written to disk.")

            # Test Load
            loaded_data = loader.load_spore(saved_path)
            self.assertIsNotNone(loaded_data, "[FAIL] LocalFileSporeLoader failed to load the spore.")
            self.assertEqual(loaded_data.get("session_id"), "test_spore", "[FAIL] Loaded spore data is corrupted or mismatched.")
        finally:
            # Re-engage the patch so tearDown() proceeds safely
            self.spore_patcher.start()

    def test_memory_core_synapse_pruning(self):
        mock_events = MagicMock()
        mock_subconscious = MagicMock()
        core = MemoryCore(events_ref=mock_events, subconscious_ref=mock_subconscious, config_ref=self.config)

        # Setup a graph with varying edge weights
        core.graph = {
            "strong_node": {"edges": {"target_a": 9.0, "weak_target": 0.6}, "is_diamond": False},
            "weak_node": {"edges": {"target_b": 0.4}, "is_diamond": False},  # Will be pruned entirely
            "diamond_node": {"edges": {"target_c": 0.1}, "is_diamond": True} # Edges prune, but node survives
        }

        # Run pruning
        # decayed_w = w * (scaling_factor + (0.14 * min(1.0, w / 10.0)))
        # For 9.0: 9 * (0.85 + 0.14*0.9) = 9 * 0.976 = ~8.78 (Survives > 0.5)
        # For 0.6: 0.6 * (0.85 + 0.14*0.06) = 0.6 * 0.8584 = ~0.51 (Survives > 0.5)
        # For 0.4: 0.4 * (0.85 + 0.14*0.04) = 0.4 * 0.8556 = ~0.34 (Dies < 0.5)
        core.prune_synapses(scaling_factor=0.85, prune_threshold=0.5)

        self.assertIn("strong_node", core.graph, "[FAIL] MemoryCore pruned a node with strong edges.")
        self.assertNotIn("weak_node", core.graph, "[FAIL] MemoryCore failed to prune a dead node.")
        self.assertIn("diamond_node", core.graph, "[FAIL] MemoryCore improperly pruned a diamond node.")
        self.assertNotIn("target_c", core.graph["diamond_node"]["edges"], "[FAIL] Diamond node edge was not pruned.")

    def test_biolichen_photosynthesis(self):
        mock_lexicon = MagicMock()
        lichen = BioLichen(lexicon_ref=mock_lexicon)

        # 1. High drag should prevent photosynthesis
        phys_high_drag = {"counts": {"photo": 2}, "narrative_drag": 5.0}
        sugar_fail, msg_fail = lichen.photosynthesize(phys_high_drag, clean_words=["bloom"], tick_count=1)
        self.assertEqual(sugar_fail, 0.0, "[FAIL] BioLichen generated sugar despite high narrative drag.")

        # 2. Low drag with photo light should generate sugar
        phys_good = {"counts": {"photo": 3}, "narrative_drag": 1.0}
        sugar_success, msg_success = lichen.photosynthesize(phys_good, clean_words=["bloom"], tick_count=2)
        self.assertTrue(sugar_success > 0.0, "[FAIL] BioLichen failed to photosynthesize under ideal conditions.")
        self.assertIsNotNone(msg_success, "[FAIL] BioLichen failed to generate a log message on success.")

    def test_bioparasite_infection_bounds(self):
        mock_mem = MagicMock()
        mock_lex = MagicMock()
        parasite = BioParasite(memory_ref=mock_mem, lexicon_ref=mock_lex, config_ref=self.config)

        # High stamina should repel parasite
        phys_safe = {"psi": 0.1}
        success_safe, _ = parasite.infect(phys_safe, stamina=90.0)
        self.assertFalse(success_safe, "[FAIL] BioParasite bypassed stamina defenses.")

        # Hitting max spores should prevent further infection
        parasite.spores_deployed = parasite.MAX_SPORES
        phys_vuln = {"psi": 0.9}
        success_max, _ = parasite.infect(phys_vuln, stamina=10.0)
        self.assertFalse(success_max, "[FAIL] BioParasite exceeded MAX_SPORES limit.")

    def test_literary_reproduction_mutations(self):
        repro = LiteraryReproduction(config_ref=self.config)

        # Force a mutation check
        # We can temporarily patch random to ensure mutations always happen for testing
        with patch('random.random', return_value=0.0):
            mutated_config = repro.mutate_config(self.config)

            # Check a known key from MUTATION_TABLE like MAX_HEALTH (bounds: 50 to 500)
            self.assertIn("MAX_HEALTH", mutated_config, "[FAIL] Mutation table failed to trigger on MAX_HEALTH.")
            self.assertTrue(50.0 <= mutated_config["MAX_HEALTH"] <= 500.0, "[FAIL] Mutated value fell outside designated clamping bounds.")


if __name__ == '__main__':
    unittest.main()