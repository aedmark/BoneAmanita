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

    def test_autophagy_prompt_injection(self):
            composer = PromptComposer(self.engine.prompt_library)
            state = self.engine.cortex.gather_state({"physics": {"voltage": 30.0}})
            state["recent_logs"] = [
                "[AUTOPHAGY: Consumed memory of 'User's favorite color' to survive.]"
            ]
            prompt = composer.compose(state, "What was my favorite color?")
            self.assertIn(
                "[AUTOPHAGY:",
                prompt,
                "The PromptComposer failed to inject the Autophagy footnote into the LLM's context window.",
            )
            self.assertIn(
                "favorite color",
                prompt,
                "The specific consumed memory was not communicated to the LLM.",
            )

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
        self.assertAlmostEqual(edges.get("original_context"), 9.5, places=2,
                               msg="Memory failed to decay its original edges by 5% during recall.", )
        self.assertEqual(
            edges.get("core_strut"),
            10.0,
            "Diamond node incorrectly decayed during reconstructive memory drift.",
        )
        new_keys = set(edges.keys()) - {"original_context", "core_strut"}
        self.assertTrue(
            len(new_keys) > 0,
            "Memory failed to reconstruct with new emotional context.",
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