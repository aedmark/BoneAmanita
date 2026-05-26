"""tests/test_memory.py"""

import os
import random
import tempfile
from brain.ann import MemoryConsolidator
from brain.composer import PromptComposer
from core import EventBus
from presets import BoneConfig
from spores import MycelialNetwork, SubconsciousStrata
from physics.models import PhysicsPacket
from tests.base import BoneTestCase

class MemoryTests(BoneTestCase):
    def generate_mock_memories(self, count=50, dim=8):
        return [(f"node_{i}", [random.uniform(-1.0, 1.0) for _ in range(dim)], {
            "concept": f"ghost_node_{i}",
            "mass": random.uniform(1.0, 10.0)
        }) for i in range(count)]

    def test_autophagy_memory_cannibalization(self):
        memory_graph = self.engine.mind.mem.graph if hasattr(
            self.engine.mind, "mem") else self.engine.akashic.graph
        memory_graph["User's favorite color"] = {"edges": {"blue": 1.0}, "last_tick": 0}
        self.engine.bio.mito.state.atp_pool = 0.0
        atp_gain, msg = self.engine.mind.mem.trigger_autophagy()
        self.engine.bio.mito.state.atp_pool += atp_gain
        self.assertNotIn(
            "User's favorite color",
            memory_graph,
            "System consumed the wrong node or failed to delete the target memory.",
        )
        self.assertGreater(
            self.engine.bio.mito.state.atp_pool,
            0.0,
            "Autophagy failed to refund ATP to the Mitochondrial Forge.",
        )

    def test_autophagy_phantom_generation(self):
        from spores.memory import MemoryCore, SubconsciousStrata
        from unittest.mock import MagicMock
        import os
        import tempfile
        temp_dir = tempfile.TemporaryDirectory()
        sub = SubconsciousStrata(filename=os.path.join(temp_dir.name, "subconscious.jsonl"))
        core = MemoryCore(events_ref=MagicMock(), subconscious_ref=sub)
        core.graph["node_0"] = {"edges": {"node_1": 1.0}, "last_tick": 1}
        core.graph["node_1"] = {"edges": {"node_0": 5.0}, "last_tick": 10}
        victim, msg = core.cannibalize(current_tick=20)
        self.assertEqual(victim, "node_0", "[FAIL] Autophagy targeted the wrong node.")
        self.assertNotIn("node_0", core.graph, "[FAIL] Cannibalized node remained in active RAM.")
        self.assertNotIn("node_0", core.graph["node_1"]["edges"],
                         "[FAIL] Edges pointing to the dead node were not pruned.")
        self.assertIn("node_0", sub.index, "[FAIL] Memory was destroyed without being buried in the deep strata!")
        temp_dir.cleanup()

    def test_dream_defragmentation_pruning(self):
        from brain.mind import DreamEngine
        class MockMemorySystem:
            def __init__(self):
                self.graph = {
                    "Weak Node": {
                        "edges": {
                            "trivial": 1.0
                        }
                    },
                    "Core Strut": {
                        "edges": {
                            "vital": 10.0,
                            "crucial": 5.0
                        }
                    },
                }

        mock_mem = MockMemorySystem()
        report = DreamEngine.run_defragmentation(mock_mem, limit=1)
        self.assertNotIn(
            "Weak Node",
            mock_mem.graph,
            "DreamEngine failed to prune the weak memory node.",
        )
        self.assertIn(
            "Core Strut",
            mock_mem.graph,
            "DreamEngine accidentally pruned a load-bearing memory strut.",
        )
        self.assertIn(
            "Weak Node",
            report,
            "DreamEngine did not report the pruned node in its return string.",
        )

    def test_billy_mitchell_protocol_sanitization(self):
        from spores.memory import _billy_mitchell_protocol

        dirty_data = {
            "word": "phantom\u200B",
            "edges": {"echo\uFEFF": 1.0},
            "tags": ["\u202Acorrupt\u202C", "clean"]
        }
        clean_data = _billy_mitchell_protocol(dirty_data)
        self.assertEqual(clean_data["word"], "phantom")
        self.assertEqual(clean_data["edges"].get("echo", 0.0), 1.0)
        self.assertNotIn("echo\uFEFF", clean_data["edges"])
        self.assertEqual(clean_data["tags"][0], "corrupt")
        self.assertEqual(clean_data["tags"][1], "clean")

    def test_bonus_round_multiplicative_resonance(self):
        from spores.memory import MemoryCore
        from unittest.mock import MagicMock
        core = MemoryCore(events_ref=MagicMock(), subconscious_ref=MagicMock())
        core.graph = {
            "load_bearing_strut": {"edges": {"a": 2.0, "b": 3.0, "c": 5.0}}
        }
        linear_results = core.illuminate({"ENT": 0.2})
        bonus_results = core.illuminate({"ENT": 0.8})
        self.assertTrue(len(linear_results) > 0)
        self.assertTrue(len(bonus_results) > 0)

    def test_orchestrator_queue_blocking(self):
        from cycle import GeodesicOrchestrator
        from unittest.mock import MagicMock
        import queue
        orch = GeodesicOrchestrator(engine_ref=MagicMock())
        orch.output_queue = queue.Queue()
        orch.output_queue.put({"type": "SNAPSHOT", "ui": "Test passed."})
        snapshot = orch.output_queue.get(timeout=1.0)
        self.assertEqual(snapshot["ui"], "Test passed.")

    def test_subconscious_matrix_absorption(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = os.path.join(temp_dir, "test_strata.jsonl")
            strata = SubconsciousStrata(filename=tmp_path)
            initial_vibe = strata.dredge_vibe("oblivion")
            self.assertEqual(sum(initial_vibe), 0.0, "Initial matrix should yield a completely zeroed vibe.")
            strata.bury({"word": "oblivion", "mass": 10.0})
            new_vibe = strata.dredge_vibe("oblivion")
            self.assertNotEqual(sum(new_vibe), 0.0, "Matrix failed to absorb the K*V weights of the buried word.")
            self.assertEqual(len(new_vibe), 8, "Vibe vector must be exactly 8-dimensional.")

    def test_ghost_physics_haunting(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = os.path.join(temp_dir, "test_ghost.jsonl")
            bus = EventBus()
            network = MycelialNetwork(events=bus)
            network.subconscious.filepath = tmp_path
            network.subconscious.matrix_filepath = os.path.join(temp_dir, "test_m_t2.json")
            network.subconscious.bury({"word": "echo", "mass": 10.0})
            physics = PhysicsPacket(voltage=10.0, narrative_drag=1.0)
            physics.clean_words = ["echo", "hello"]
            log = network._poll_ghosts(physics.clean_words, physics)
            self.assertIsNotNone(log, "Ghost poll failed to detect the buried word.")
            self.assertNotEqual(physics.voltage, 10.0, "The ghost failed to mutate the system Voltage.")
            self.assertNotEqual(physics.narrative_drag, 1.0, "The ghost failed to mutate the system Drag.")
            self.assertIn("ECHO", log, "The log string did not identify the haunting word.")

    def test_reconstructive_memory_drift(self):
        mem_core = self.engine.mind.mem.memory_core
        mem_core.graph["ECHO_NODE"] = {
            "edges": {
                "original_context": 10.0,
                "core_strut": 10.0
            },
            "last_tick": 0,
        }
        mem_core.graph["core_strut"] = {"is_diamond": True, "edges": {}, "last_tick": 0}
        vector = {"PSI": 0.9}
        mem_core.illuminate(vector, limit=1)
        edges = mem_core.graph["ECHO_NODE"]["edges"]
        self.assertAlmostEqual(edges.get("original_context"), 9.5, places=2, msg="Memory failed to decay its original edges by 5% during recall.", )
        self.assertEqual(edges.get("core_strut"), 10.0,
                         "Diamond node incorrectly decayed during reconstructive memory drift.", )
        new_keys = set(edges.keys()) - {"original_context", "core_strut"}
        self.assertTrue(len(new_keys) > 0, "Memory failed to reconstruct with new emotional context.", )

    def test_vectorized_graph_edge_cases(self):
        import numpy as np
        from brain.ann import HippocampalCache
        cache = HippocampalCache(max_capacity=500)
        graph_0 = cache.get_graph()
        self.assertEqual(graph_0, {}, "[FAIL] Vectorized graph crashed on empty cache.")
        cache.nodes = {"lone_node": {"vector": np.array([0.5] * 8)}}
        graph_1 = cache.get_graph()
        self.assertEqual(graph_1, {"lone_node": set()}, "[FAIL] Vectorized graph crashed on single-node cache.")

    def test_shadow_retrieval_geometry(self):
        self.engine.mind.mem.graph["core_concept"] = {"data": "Explicit answer", "mass": 5.0}
        self.engine.mind.mem.graph["adjacent_risk"] = {"data": "Hidden systemic cost", "mass": 2.0}

        sim_res = {
            "physics": {"scope": 0.9, "depth": 0.1, "voltage": 10.0, "chi": 0.0},
            "bio": {}, "mind": {}, "world": {}, "soul": {},
            "logs": [], "council_mandates": []
        }
        _ = self.engine.cortex.gather_state(sim_res)
        shadow_nodes = getattr(self.engine.cortex, "last_shadow_nodes", [])
        self.assertTrue(
            len(shadow_nodes) > 0,
            "[FAIL] Shadow Retrieval failed to execute the lateral Shadow Cast."
        )

    def test_memory_encoding(self):
        events = EventBus()
        network = MycelialNetwork(events, config_ref=BoneConfig)
        memories = self.generate_mock_memories(50)
        network.hippocampus.max_capacity = 100
        for node_id, vector, meta in memories:
            network.hippocampus.encode(node_id, vector, meta)
        available_atp = 5000.0
        consolidator = MemoryConsolidator(network.hippocampus, network.cortex, events)
        nodes_moved, atp_cost = consolidator.trigger_rem_consolidation(available_atp)
        query_vector = [random.uniform(-1.0, 1.0) for _ in range(8)]
        results = network.retrieve_semantic("trigger_word", query_vector, scope=0.9, resonance=0.5)
        self.assertEqual(nodes_moved, 50, "Consolidator failed to move all 50 nodes.")
