"""tests/test_memory.py"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import spores.memory
from body.metabolism import MitochondrialForge
from body.models import MitochondrialState
from brain.linear_cortex import LinearCortexRouter
from spores.memory import MemoryCore, SubconsciousStrata
from tests.base import BoneTestCase

try:
    import numpy as np
except ImportError:
    np = None

try:
    import ordvec
except ImportError:
    ordvec = None


class TestSubconsciousStrata(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.filepath = os.path.join(self.temp_dir.name, "subconscious.jsonl")
        self.strata = SubconsciousStrata(filename=self.filepath)

    def tearDown(self):
        self.temp_dir.cleanup()
        super().tearDown()

    def test_initialization(self):
        self.assertEqual(len(self.strata.index), 0)
        self.assertEqual(len(self.strata.metadata_log), 0)
        self.assertIsNone(self.strata.rank_bank)
        self.assertIsNone(self.strata.bitmap)
        self.assertIsNone(self.strata.quantizer)

    def test_billy_mitchell_key_optimization(self):
        from spores.memory import _billy_mitchell_protocol

        dirty_dict = {"ghost\u200b_key": "toxic\u200d_value"}
        clean_dict = _billy_mitchell_protocol(dirty_dict)
        self.assertIn(
            "ghost_key",
            clean_dict,
            "[FAIL] Zero-width character remained in dictionary key.",
        )
        self.assertEqual(
            clean_dict["ghost_key"],
            "toxic_value",
            "[FAIL] Zero-width character remained in dictionary value.",
        )

    def test_prune_strata_amnesia_prevention(self):
        for i in range(10):
            self.strata.bury({"word": f"mem_{i}", "mass": 1.0})
        self.assertEqual(len(self.strata.metadata_log), 10)
        with open(self.strata.filepath, "w", encoding="utf-8") as f:
            f.write('{"word": "corrupted"}\n')
        self.strata._prune_strata()
        self.assertEqual(
            len(self.strata.metadata_log),
            9,
            "[FAIL] Total Amnesia triggered! Memory arrays were wiped by a file mismatch.",
        )
        if self.strata.rank_bank is not None:
            self.assertEqual(len(self.strata.rank_bank), 9)

    @unittest.skipIf(np is None, "NumPy is not installed; skipping exact math tests.")
    def test_cold_start_burial_and_exact_dredge(self):
        self.strata.bury({"word": "echo", "mass": 2.0})
        self.strata.bury({"word": "silence", "mass": 10.0})
        self.strata.bury({"word": "void", "mass": 7.0})
        self.assertIsNotNone(self.strata.rank_bank)
        self.assertEqual(self.strata.rank_bank.shape[0], 3)
        self.assertTrue(self.strata.rank_bank.flags["C_CONTIGUOUS"])
        self.assertIsNone(self.strata.quantizer)
        results = self.strata.dredge_vibe("silence", k=2)
        self.assertEqual(len(results), 2)
        top_result = results[0]
        self.assertEqual(top_result["word"], "silence")
        self.assertIn("score", top_result)

    @unittest.skipIf(
        ordvec is None or np is None,
        "ordvec 0.5.0 is not installed; skipping Fastscan tests.",
    )
    @patch("spores.memory._word_to_vector")
    def test_fastscan_ignition_and_add(self, mock_w2v):
        rng = np.random.RandomState(42)
        mock_vecs = {}
        for i in range(35):
            v = rng.randn(128).astype(np.float32)
            norm = np.linalg.norm(v)
            if norm > 0:
                v /= norm
            mock_vecs[f"node_{i}"] = v

        mock_w2v.side_effect = lambda w: mock_vecs.get(
            w, rng.randn(128).astype(np.float32)
        )

        for i in range(35):
            self.strata.bury({"word": f"node_{i}", "mass": float(i)})

        self.assertEqual(self.strata.rank_bank.shape[0], 35)

        self.assertIsNotNone(self.strata.bitmap)
        self.assertIsNotNone(self.strata.quantizer)

        results = self.strata.dredge_vibe("node_3", k=2)
        self.assertTrue(len(results) > 0)
        self.assertIn("word", results[0])
        self.assertIn("score", results[0])

    def test_graceful_degradation_fallback(self):
        """Ensures that severed bindings seamlessly fall back to exact math."""
        original_ordvec = spores.memory.ordvec
        try:
            spores.memory.ordvec = None
            for i in range(10):
                self.strata.bury({"word": f"degraded_{i}", "mass": 1.0})
            self.assertIsNone(self.strata.quantizer)
            results = self.strata.dredge_vibe("degraded_5", k=3)
            self.assertTrue(len(results) > 0)
        finally:
            spores.memory.ordvec = original_ordvec


class TestMemoryCore(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.mock_events = MagicMock()
        self.mock_subconscious = MagicMock()
        self.mock_lexicon = MagicMock()
        dummy_config = {"CORTEX": {"EPIGENETIC_PRUNE_THRESHOLD": 10}}
        self.core = MemoryCore(
            events_ref=self.mock_events,
            subconscious_ref=self.mock_subconscious,
            lexicon_ref=self.mock_lexicon,
            config_ref=dummy_config,
        )

    def test_graph_initialization(self):
        self.assertEqual(len(self.core.graph), 0)
        self.assertEqual(len(self.core.cortical_stack), 0)

    def test_calculate_mass(self):
        self.core.graph["test_node"] = {"edges": {"a": 2.0, "b": 3.0}}
        mass = self.core.calculate_mass("test_node")
        self.assertEqual(mass, 5.0)

    def test_illuminate_resonance_and_batching(self):
        self.core.graph = {
            "monolith": {"edges": {"a": 5.0}, "is_diamond": False},
            "whisper": {"edges": {"b": 1.0}, "is_diamond": False},
        }
        self.mock_lexicon.get_categories_for_word.side_effect = lambda w: (
            {"heavy", "constructive"} if w == "monolith" else {"social"}
        )
        results = self.core.illuminate({"STR": 0.9, "BET": 0.1}, limit=5)
        self.assertTrue(any("MONOLITH" in res for res in results))

    @unittest.skipIf(np is None, "NumPy is not installed; skipping centroid math.")
    @patch("spores.memory._word_to_vector")
    def test_hebbian_wiring_and_deep_dredge(self, mock_w2v):
        mock_w2v.side_effect = lambda w: [1.0, 0.0] if w == "node_a" else [0.0, 1.0]
        self.core.graph = {
            "node_a": {"edges": {}, "is_diamond": False},
            "node_b": {"edges": {}, "is_diamond": False},
        }
        self.mock_lexicon.get_categories_for_word.return_value = {"heavy"}
        self.mock_subconscious.dredge_vibe_by_vector.return_value = [
            {"word": "phantom_memory", "score": 0.88, "data": {}}
        ]
        self.core.illuminate({"STR": 1.0}, limit=5)
        self.assertIn(
            "node_b",
            self.core.graph["node_a"]["edges"],
            "Hebbian wiring failed on node_a.",
        )
        self.assertIn(
            "node_a",
            self.core.graph["node_b"]["edges"],
            "Hebbian wiring failed on node_b.",
        )
        self.assertEqual(self.core.graph["node_a"]["edges"]["node_b"], 0.5)
        self.assertTrue(
            self.mock_subconscious.dredge_vibe_by_vector.called,
            "The Deep Dredge was never triggered.",
        )
        self.assertIn(
            "phantom_memory",
            self.core.graph,
            "Phantom memory was not injected into the graph.",
        )
        self.assertIn("phantom_memory", self.core.graph["node_a"]["edges"])
        self.assertIn("phantom_memory", self.core.graph["node_b"]["edges"])
        self.assertIn("node_a", self.core.graph["phantom_memory"]["edges"])
        self.assertIn("node_b", self.core.graph["phantom_memory"]["edges"])

    def test_prune_synapses_two_pass(self):
        self.core.graph = {
            "strong_node": {"edges": {"weak_node": 10.0}, "is_diamond": False},
            "weak_node": {"edges": {"strong_node": 0.1}, "is_diamond": False},
            "diamond_node": {"edges": {}, "is_diamond": True},
        }
        self.core.prune_synapses(scaling_factor=0.1, prune_threshold=0.5)
        self.assertNotIn("weak_node", self.core.graph)
        self.assertIn("strong_node", self.core.graph)
        self.assertIn("diamond_node", self.core.graph)
        self.assertNotIn("weak_node", self.core.graph["strong_node"]["edges"])

    def test_forge_diamond_topology(self):
        """Ensures forge_diamond locks specific edges and bypasses synaptic decay."""
        self.core.graph = {
            "anchor": {"edges": {"fossil": 10.0, "weak": 2.0}, "is_diamond": False},
            "fossil": {"edges": {"anchor": 10.0}, "is_diamond": False},
            "weak": {"edges": {"anchor": 2.0}, "is_diamond": False}
        }
        success = self.core.forge_diamond("anchor", "fossil")
        self.assertTrue(success, "[FAIL] Diamond forge rejected valid nodes.")
        self.assertTrue(self.core.graph["anchor"]["is_diamond"])
        self.assertIn("fossil", self.core.graph["anchor"]["diamond_edges"])
        self.core.prune_synapses(scaling_factor=0.1, prune_threshold=5.0)
        self.assertIn("fossil", self.core.graph["anchor"]["edges"])
        self.assertEqual(self.core.graph["anchor"]["edges"]["fossil"], 10.0, "[FAIL] Diamond edge suffered decay.")
        self.assertNotIn("weak", self.core.graph["anchor"]["edges"], "[FAIL] Standard edge resisted pruning.")

class TestRankQuantAccuracy(unittest.TestCase):
    @patch("spores.memory._word_to_vector")
    def test_fastscan_recall_accuracy(self, mock_w2v):
        """Ensures the 4-bit RankQuant retrieves mathematically accurate results."""
        rng = np.random.RandomState(42)
        total_memories = 500
        dim = 128

        mock_vecs = {}
        base_clusters = [rng.randn(dim).astype(np.float32) for _ in range(5)]

        for i in range(total_memories):
            base = base_clusters[i % 5]
            noise = rng.randn(dim).astype(np.float32) * 0.2
            v = base + noise
            v /= np.linalg.norm(v)
            mock_vecs[f"concept_{i}"] = v

        mock_w2v.side_effect = lambda w: mock_vecs.get(
            w, rng.randn(dim).astype(np.float32)
        )

        strata = SubconsciousStrata("test_strata.json")
        for i in range(total_memories):
            strata.bury({"word": f"concept_{i}", "mass": 1.0})

        self.assertIsNotNone(strata.quantizer, "Quantizer failed to boot.")

        query_word = "concept_99"

        temp_quantizer = strata.quantizer
        strata.quantizer = None

        exact_results = strata.dredge_vibe(query_word, k=15)
        exact_words = {res["word"] for res in exact_results}

        strata.quantizer = temp_quantizer
        fastscan_results = strata.dredge_vibe(query_word, k=15)
        fastscan_words = {res["word"] for res in fastscan_results}

        intersection = exact_words.intersection(fastscan_words)
        recall_rate = len(intersection) / 15.0

        print(f"\n[METRIC] 4-Bit Recall Rate: {recall_rate * 100}%")

        self.assertGreaterEqual(
            recall_rate,
            0.80,
            f"[FAIL] Fastscan Recall degraded heavily! Only {recall_rate * 100}% matched exact math.",
        )


class TestLinearCortexRouter(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.router = LinearCortexRouter(token_budget=50)

    def test_ingest_and_structural_sweep(self):
        codebase = (
            "class Metabolism:\n"
            "    def __init__(self):\n"
            "        self.ATP = 100\n"
            "        self.ROS = 0\n"
            "    def process(self):\n"
            "        print('hello')\n"
        )
        self.router.ingest_artifact("metabolism.py", codebase)

        sparse_mask = self.router.route_attention("How is ATP initialized?")

        self.assertIn("[metabolism.py_L0]", sparse_mask)
        self.assertIn("[metabolism.py_L2]", sparse_mask)
        self.assertNotIn("print('hello')", sparse_mask)

        idx_l0 = sparse_mask.find("metabolism.py_L0")
        idx_l2 = sparse_mask.find("metabolism.py_L2")
        self.assertLess(idx_l0, idx_l2)

    def test_token_budget_enforcement(self):
        codebase = "\n".join([f"line {i} ATP" for i in range(100)])
        self.router.ingest_artifact("big.py", codebase)

        mask = self.router.route_attention("ATP")

        tokens_used = len(mask.split())
        self.assertLessEqual(tokens_used, 55)


class TestMetabolicRouting(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.state = MitochondrialState()
        self.state.atp_pool = 100.0
        self.state.ros_buildup = 0.0
        self.events = MagicMock()
        self.forge = MitochondrialForge(self.state, self.events)

    def test_fast_twitch_vector_cost(self):
        self.forge.process_cognitive_load(2000, "VECTOR_FAST_TWITCH")

        self.assertAlmostEqual(self.state.atp_pool, 99.6)
        self.assertEqual(self.state.ros_buildup, 0.0)

    def test_deep_tissue_linear_cost(self):
        self.forge.process_cognitive_load(10000, "LINEAR_DEEP_TISSUE")

        self.assertAlmostEqual(self.state.atp_pool, 85.0)
        self.assertAlmostEqual(self.state.ros_buildup, 0.8)

    def test_gordon_intervention_exhaustion(self):
        self.state.atp_pool = 12.0

        self.forge.process_cognitive_load(5000, "LINEAR_DEEP_TISSUE")

        self.assertLess(self.state.atp_pool, 10.0)
        self.assertEqual(self.state.retrograde_signal, "HIBERNATING")
        self.events.log.assert_called_with(
            "[GORDON INTERVENTION]: Your query forced a massive structural sweep. The organism's ATP is depleted. Narrow your scope.",
            "BIO_CRIT",
        )


if __name__ == "__main__":
    unittest.main()
