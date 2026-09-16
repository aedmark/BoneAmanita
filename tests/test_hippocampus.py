"""tests/test_hippocampus.py

Short-term memory, end to end.

HippocampalCache shipped with wired readers and no writer: REM consolidation
drained it, cycle.py graphed it, and apply_stress_blindness amputated it, but
nothing ever put a node in. Every reader therefore saw an empty cache forever,
and two further faults hid behind that emptiness -- get_graph() returns an
adjacency dict while all three consumers asked for a `.adj` attribute, and the
0.75 edge threshold was calibrated for hash vectors and sits above every
similarity real embeddings produce.
"""

import unittest

from brain.ann import HippocampalCache
from cycle import _native_freeze_graph
from tests.base import BoneTestCase


def _engram(text, room, significance=50.0):
    return {
        "trigger": text.split()[:3],
        "context": "GEODESIC",
        "significance": significance,
        "wing_id": "GLOBAL",
        "room_id": room,
        "raw_verbatim_text": text,
        "timestamp": 0.0,
    }


class WritePath(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.mem = self.engine.mind.mem
        self.hip = self.mem.hippocampus

    def _encode(self, text, voltage=50.0):
        physics = {"raw_text": text, "voltage": voltage}
        return self.mem.encode(text.split(), physics, "GEODESIC")

    def test_significant_engrams_reach_the_cache(self):
        self.assertEqual(len(self.hip.nodes), 0)
        self._encode("the greenhouse behind the old house")
        self.assertEqual(
            len(self.hip.nodes),
            1,
            "[FAIL] encode() did not write to the hippocampus.",
        )

    def test_insignificant_engrams_are_not_cached(self):
        """Below the consolidation threshold nothing should be stored."""
        self._encode("a passing thought", voltage=0.0)
        self.assertEqual(len(self.hip.nodes), 0)

    def test_cached_node_carries_its_text_and_a_vector(self):
        self._encode("my grandmother kept every letter she received")
        node = next(iter(self.hip.nodes.values()))
        self.assertIn("grandmother", node["meta"]["raw_verbatim_text"])
        self.assertEqual(len(node["vector"]), self.engine.mind.mem.cortex.dimension)

    def test_rem_can_now_consolidate(self):
        """extract_for_consolidation used to always return []."""
        for text in ("first distinct memory here", "second distinct memory here"):
            self._encode(text)
        pending = self.hip.extract_for_consolidation(limit=10)
        self.assertEqual(len(pending), 2)
        self.assertEqual(
            len(self.hip.nodes), 0, "[FAIL] Consolidation did not drain the cache."
        )


class GraphContract(unittest.TestCase):
    """get_graph() returns Dict[str, set]; consumers must not ask for `.adj`."""

    def setUp(self):
        self.cache = HippocampalCache(max_capacity=10, edge_threshold=0.5)

    def _add(self, node_id, vector):
        self.cache.encode(node_id, vector, {"id": node_id})

    def test_returns_a_plain_adjacency_dict(self):
        self._add("a", [1.0, 0.0])
        graph = self.cache.get_graph()
        self.assertIsInstance(graph, dict)
        self.assertIsNone(
            getattr(graph, "adj", None),
            "[FAIL] Consumers guard on `.adj`; a dict never has one.",
        )

    def test_similar_nodes_are_adjacent(self):
        self._add("a", [1.0, 0.0])
        self._add("b", [0.95, 0.31])
        self._add("c", [0.0, 1.0])
        graph = self.cache.get_graph()
        self.assertIn("b", graph["a"])
        self.assertNotIn("c", graph["a"])

    def test_threshold_is_honoured(self):
        strict = HippocampalCache(max_capacity=10, edge_threshold=0.99)
        for node_id, vec in (("a", [1.0, 0.0]), ("b", [0.95, 0.31])):
            strict.encode(node_id, vec, {"id": node_id})
        self.assertEqual(strict.get_graph()["a"], set())

    def test_graph_freezes_into_a_godel_scar(self):
        """cycle.py passes this straight to _native_freeze_graph."""
        self._add("a", [1.0, 0.0])
        self._add("b", [0.95, 0.31])
        frozen = _native_freeze_graph(self.cache.get_graph())
        self.assertIsInstance(frozen, tuple)
        self.assertEqual(len(frozen), 2)

    def test_default_threshold_admits_real_embedding_similarity(self):
        """Regression: 0.75 was a hash-vector constant and sat above every
        similarity that nomic-embed-text actually produces for related prose."""
        self.assertLessEqual(HippocampalCache.DEFAULT_EDGE_THRESHOLD, 0.6)


class StressBlindness(BoneTestCase):
    def test_cortisol_amputates_a_full_cache(self):
        mem = self.engine.mind.mem
        hip = mem.hippocampus
        for i in range(80):
            mem.encode([f"n{i}"], {"raw_text": f"memory {i}", "voltage": 50.0}, "GEO")
        before = len(hip.nodes)
        self.assertGreater(before, 50)
        shed = mem.apply_stress_blindness(0.9)
        self.assertGreater(shed, 0, "[FAIL] High cortisol shed nothing.")
        self.assertLess(len(hip.nodes), before)

    def test_calm_state_does_not_amputate(self):
        mem = self.engine.mind.mem
        for i in range(20):
            mem.encode([f"n{i}"], {"raw_text": f"memory {i}", "voltage": 50.0}, "GEO")
        before = len(mem.hippocampus.nodes)
        self.assertEqual(mem.apply_stress_blindness(0.1), 0)
        self.assertEqual(len(mem.hippocampus.nodes), before)


class RetrievalWiring(BoneTestCase):
    """retrieve_semantic had no production caller, so retrieve_exact was
    reachable only through dead code. Both paths are now live via
    TheCortex._recall."""

    def setUp(self):
        super().setUp()
        self.mem = self.engine.mind.mem

    def _remember(self, text):
        self.mem.encode(
            self.engine.lex.clean(text), {"raw_text": text, "voltage": 50.0}, "GEODESIC"
        )

    def test_room_key_is_shared_by_write_and_read(self):
        """If these drift, the cache is written and never hit."""
        words = self.engine.lex.clean("greenhouse tomatoes ripening in the heat")
        self._remember("greenhouse tomatoes ripening in the heat")
        self.assertIn(self.mem.room_key(words), self.mem.hippocampus.nodes)

    def test_exact_recall_hits_on_a_revisited_room(self):
        self._remember("greenhouse tomatoes ripening in the summer heat")
        words = self.engine.lex.clean("greenhouse tomatoes were everywhere that year")
        hits = self.mem.retrieve_semantic(
            trigger_word=self.mem.room_key(words),
            query_vector=self.mem.cortex.embed("greenhouse tomatoes again"),
            scope=0.2,
        )
        self.assertTrue(hits, "[FAIL] Exact recall returned nothing.")
        self.assertEqual(hits[0]["source"], "hippocampus")

    def test_exact_recall_misses_a_different_room(self):
        self._remember("greenhouse tomatoes ripening in the summer heat")
        words = self.engine.lex.clean("compiler errors in the build system")
        hits = self.mem.retrieve_semantic(
            trigger_word=self.mem.room_key(words),
            query_vector=self.mem.cortex.embed("compiler errors"),
            scope=0.2,
        )
        self.assertFalse(
            [h for h in hits if h["source"] == "hippocampus"],
            "[FAIL] Exact recall fired on an unrelated room.",
        )

    def test_cortex_recall_unwraps_into_shadow_nodes(self):
        """_recall must flatten retrieve_semantic's tagged wrappers."""
        self.engine.mind.dreamer.context_queue = [
            "my grandmother kept every letter she ever received in a shoebox"
        ]
        self.engine.mind.dreamer.enter_rem_cycle(
            {}, {"mito": {"atp": 100.0}, "chem": {"cortisol": 0.1}}
        )
        nodes = self.engine.cortex._recall(
            "thinking about my grandmother and what she saved",
            {"matter": {"clean_words": ["grandmother", "saved"]}},
            scope_val=0.9,
            omega_r=0.5,
            cortex_mem=self.mem.cortex,
        )
        self.assertTrue(nodes, "[FAIL] _recall returned nothing.")
        for node in nodes:
            self.assertIsInstance(node, dict)
            self.assertNotIn(
                "source", node, "[FAIL] Wrapper leaked instead of being unwrapped."
            )

    def test_recall_survives_a_memory_without_retrieve_semantic(self):
        """Older/duck-typed memory objects must still work."""
        class Bare:
            pass

        original = self.engine.cortex.svc.mind_memory
        try:
            self.engine.cortex.svc.mind_memory = Bare()
            nodes = self.engine.cortex._recall(
                "anything at all", {}, 0.9, 0.5, self.mem.cortex
            )
            self.assertIsInstance(nodes, list)
        finally:
            self.engine.cortex.svc.mind_memory = original


if __name__ == "__main__":
    unittest.main()
