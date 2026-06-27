"""tests/test_spores.py"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from presets import BoneConfig
from spores.biome import BioLichen, BioParasite
from spores.genetics import LiteraryReproduction
from spores.io import LocalFileSporeLoader
from spores.memory import MemoryCore
from tests.base import BoneTestCase


class SporeEcosystemTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_local_loader_roundtrip(self):
        self.spore_patcher.stop()
        try:
            loader = LocalFileSporeLoader(directory=self.test_dir)
            test_filename = "session_test_spore.json"
            test_data = {
                "session_id": "test_spore",
                "core_graph": {"node_a": {"edges": {"node_b": 5.0}}},
                "trauma_vector": {"ENT": 0.8},
            }

            saved_path = loader.save_spore(test_filename, test_data)
            self.assertIsNotNone(
                saved_path, "[FAIL] LocalFileSporeLoader failed to return a saved path."
            )
            self.assertTrue(
                os.path.exists(saved_path),
                "[FAIL] Spore file was not actually written to disk.",
            )

            loaded_data = loader.load_spore(saved_path)
            self.assertIsNotNone(
                loaded_data, "[FAIL] LocalFileSporeLoader failed to load the spore."
            )
            self.assertEqual(
                loaded_data.get("session_id"),
                "test_spore",
                "[FAIL] Loaded spore data is corrupted or mismatched.",
            )
        finally:
            self.spore_patcher.start()

    def test_memory_core_synapse_pruning(self):
        mock_events = MagicMock()
        mock_subconscious = MagicMock()
        core = MemoryCore(
            events_ref=mock_events,
            subconscious_ref=mock_subconscious,
            config_ref=self.config,
        )

        core.graph = {
            "strong_node": {
                "edges": {"target_a": 9.0, "weak_target": 0.6},
                "is_diamond": False,
            },
            "weak_node": {"edges": {"target_b": 0.4}, "is_diamond": False},
            "diamond_node": {"edges": {"target_c": 0.1}, "is_diamond": True},
        }

        core.prune_synapses(scaling_factor=0.85, prune_threshold=0.5)

        self.assertIn(
            "strong_node",
            core.graph,
            "[FAIL] MemoryCore pruned a node with strong edges.",
        )
        self.assertNotIn(
            "weak_node", core.graph, "[FAIL] MemoryCore failed to prune a dead node."
        )
        self.assertIn(
            "diamond_node",
            core.graph,
            "[FAIL] MemoryCore improperly pruned a diamond node.",
        )
        self.assertNotIn(
            "target_c",
            core.graph["diamond_node"]["edges"],
            "[FAIL] Diamond node edge was not pruned.",
        )

    def test_biolichen_photosynthesis(self):
        mock_lexicon = MagicMock()
        lichen = BioLichen(lexicon_ref=mock_lexicon)

        phys_high_drag = {"counts": {"photo": 2}, "narrative_drag": 5.0}
        sugar_fail, msg_fail = lichen.photosynthesize(
            phys_high_drag, clean_words=["bloom"], tick_count=1
        )
        self.assertEqual(
            sugar_fail,
            0.0,
            "[FAIL] BioLichen generated sugar despite high narrative drag.",
        )

        phys_good = {"counts": {"photo": 3}, "narrative_drag": 1.0}
        sugar_success, msg_success = lichen.photosynthesize(
            phys_good, clean_words=["bloom"], tick_count=2
        )
        self.assertTrue(
            sugar_success > 0.0,
            "[FAIL] BioLichen failed to photosynthesize under ideal conditions.",
        )
        self.assertIsNotNone(
            msg_success, "[FAIL] BioLichen failed to generate a log message on success."
        )

    def test_bioparasite_infection_bounds(self):
        mock_mem = MagicMock()
        mock_lex = MagicMock()
        parasite = BioParasite(
            memory_ref=mock_mem, lexicon_ref=mock_lex, config_ref=self.config
        )
        phys_safe = {"psi": 0.1}
        success_safe, _ = parasite.infect(phys_safe, stamina=90.0)
        self.assertFalse(success_safe, "[FAIL] BioParasite bypassed stamina defenses.")
        parasite.spores_deployed = parasite.MAX_SPORES
        phys_vuln = {"psi": 0.9}
        success_max, _ = parasite.infect(phys_vuln, stamina=10.0)
        self.assertFalse(success_max, "[FAIL] BioParasite exceeded MAX_SPORES limit.")

    def test_autonomic_governor_policy_shifts(self):
        """Ensures the MycelialNetwork dynamically mutates physics constraints based on metabolic state."""
        from spores.network import MycelialNetwork
        from unittest.mock import MagicMock

        # Initialize biological state
        if not hasattr(self.config, "BIO"):
            self.config.BIO = {}
        if not hasattr(self.config, "PHYSICS"):
            self.config.PHYSICS = {}

        net = MycelialNetwork(events=MagicMock(), config_ref=self.config)

        # Test 1: Defensive Posture (High Toxicity)
        action_defensive = net.evaluate_system_state(stamina=100.0, trauma_vector={"panic": 0.9})
        self.assertEqual(
            action_defensive, "DEFENSIVE", "[FAIL] Governor did not shift to DEFENSIVE under high toxicity."
        )

        # Test 2: Throttle Down (High Exhaustion)
        action_throttle = net.evaluate_system_state(stamina=10.0, trauma_vector={"panic": 0.1})
        self.assertEqual(
            action_throttle, "THROTTLE_DOWN", "[FAIL] Governor did not shift to THROTTLE_DOWN under exhaustion."
        )

        # Test 3: Open Floodgates (Healthy Baseline)
        action_flood = net.evaluate_system_state(stamina=100.0, trauma_vector={"panic": 0.1})
        self.assertEqual(
            action_flood, "OPEN_FLOODGATES", "[FAIL] Governor did not shift to OPEN_FLOODGATES when healthy."
        )

    def test_cordyceps_bloom_and_antidote(self):
        """Ensures the Cordyceps blooms under trauma and Lichen cures it."""
        from spores.biome import BioCordyceps, BioLichen
        if not hasattr(self.config, "BIO"):
            self.config.BIO = {}
        cordyceps = BioCordyceps(config_ref=self.config)
        cordyceps.incubate(150.0)
        bloom_msg = cordyceps.incubate(150.0)
        self.assertIsNotNone(bloom_msg, "[FAIL] Cordyceps failed to bloom under critical trauma.")
        is_blooming = (
            self.config.BIO.get("CORDYCEPS_BLOOMING")
            if isinstance(self.config.BIO, dict)
            else getattr(self.config.BIO, "CORDYCEPS_BLOOMING", False)
        )
        self.assertTrue(is_blooming, "[FAIL] Global bloom flag was not set.")
        mock_lex = MagicMock()
        mock_lex.get.return_value = {"play", "photo"}
        lichen = BioLichen(lexicon_ref=mock_lex, config_ref=self.config)
        sugar, msg = lichen.photosynthesize(
            phys={"narrative_drag": 10.0, "counts": {"photo": 2}}, clean_words=["play", "photo"], tick_count=1
        )
        self.assertTrue(sugar >= 20.0, "[FAIL] Lichen failed to synthesize the high-yield antidote sugar.")
        self.assertIn("ANTIDOTE SYNTHESIZED", msg, "[FAIL] Antidote message was not generated.")
        is_blooming_after = (
            self.config.BIO.get("CORDYCEPS_BLOOMING")
            if isinstance(self.config.BIO, dict)
            else getattr(self.config.BIO, "CORDYCEPS_BLOOMING", True)
        )
        self.assertFalse(is_blooming_after, "[FAIL] Antidote failed to clear the Cordyceps flag.")

    def test_literary_reproduction_mutations(self):
        repro = LiteraryReproduction(config_ref=self.config)
        with patch("random.random", return_value=0.0):
            mutated_config = repro.mutate_config(self.config)
            self.assertIn(
                "MAX_HEALTH",
                mutated_config,
                "[FAIL] Mutation table failed to trigger on MAX_HEALTH.",
            )
            self.assertTrue(
                50.0 <= mutated_config["MAX_HEALTH"] <= 500.0,
                "[FAIL] Mutated value fell outside designated clamping bounds.",
            )


if __name__ == "__main__":
    unittest.main()
