"""Memory phase 5: before the self graph's cap starts denying writes, consolidation forgets near-duplicate
memories and the least recalled, through the gate, in REM and in a turn at the high-water mark."""

import copy
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import yaml

from engine.gate.forgetting import plan
from engine.gate.kernel import Boundary, Gate
from engine.gate.recall import memory_hash
from engine.gate.tools import TOOLS, build_invariants, grammar_text
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

MODEL = "fake:concepts"


def notes(n):
    return {f"note{i}": f"an ordinary detail number {i}" for i in range(n)}


class ThePlan(BoneTestCase):
    def test_under_the_high_water_mark_nothing_goes(self):
        self.assertEqual(plan(notes(8), {}, None, MODEL, cap=10), {})

    def test_at_the_mark_the_least_recalled_go_first_down_to_the_low_mark(self):
        stats = {"note0": (4, 10.0), "note1": (1, 5.0), "note2": (1, 9.0)}
        gone = plan(notes(9), stats, None, MODEL, cap=10)
        # Never recalled go first, oldest written first; then the least recently recalled.
        self.assertEqual(list(gone), ["note3"])
        gone = plan(notes(10), stats, None, MODEL, cap=10)
        self.assertEqual(list(gone), ["note3", "note4"])
        self.assertEqual(set(gone.values()), {"least recalled"})
        # From the high-water mark down to the low one, not just under the cap.
        self.assertEqual(len(plan(notes(18), {}, None, MODEL, cap=20)), 2)

    def test_a_near_duplicate_goes_and_the_stronger_copy_stays(self):
        memory = {"dog_name": "Brisket", "pet_name": "Brisket, a dog", "allergy": "cashews"}
        vec = {"dog_name": [1.0, 0.0], "pet_name": [0.99, 0.05], "allergy": [0.0, 1.0]}
        vectors = {k: (memory_hash(k, memory[k]), MODEL, v) for k, v in vec.items()}
        gone = plan(memory, {"pet_name": (3, 1.0)}, vectors, MODEL, cap=500)
        self.assertEqual(gone, {"dog_name": "near-duplicate of pet_name"})

    def test_stale_vectors_never_merge(self):
        memory = {"dog_name": "Brisket", "pet_name": "Brisket, a dog"}
        same = [1.0, 0.0]
        other_model = {k: (memory_hash(k, memory[k]), "other:model", same) for k in memory}
        old_text = {k: ("0" * 16, MODEL, same) for k in memory}
        self.assertEqual(plan(memory, {}, other_model, MODEL, cap=500), {})
        self.assertEqual(plan(memory, {}, old_text, MODEL, cap=500), {})


class TheForgetVerb(BoneTestCase):
    def gate(self, memory):
        spec = yaml.safe_load(open("engine/gate/boundary.yaml"))
        state = {"world": {"schema_version": 2, "sources": {}, "nodes": {}, "edges": [], "constraints": []},
                 "self": {"memory": dict(memory)}}
        return Gate(Boundary(spec), state, TOOLS, build_invariants(spec))

    def test_it_forgets_only_what_is_held(self):
        gate = self.gate({"a": "1", "b": "2"})
        receipt = gate.adjudicate("(Forgetting)\nNOMINATE what=self/memory/consolidation verb=forget args=keys:a | zzz")
        self.assertEqual((receipt["decision"], gate.state["self"]["memory"]), ("ACCEPT", {"b": "2"}))
        self.assertEqual(receipt["result"], {"forgot": ["a"]})

    def test_the_model_is_not_offered_it(self):
        self.assertNotIn("verb=forget", grammar_text(yaml.safe_load(open("engine/gate/boundary.yaml"))))


class ForgettingInTheEngine(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value="Noted.")
        self.engine.boundary.spec = copy.deepcopy(self.engine.boundary.spec)
        self.engine.boundary.spec["limits"]["self_max_memories"] = 10

    def seed(self, memory):
        store = self.engine.store
        for key, value in memory.items():
            seq, state = store.state()
            gate = Gate(self.engine.boundary, state, self.engine.gate_tools, self.engine.gate_invariants)
            receipt = gate.adjudicate(f"Kept.\nNOMINATE what=self/memory/{key} verb=remember args=key:{key}; value:{value}")
            store.commit_cycle("seed", gate.state, seq, receipt, "raw")

    def memory(self):
        return self.engine.store.state()[1]["self"]["memory"]

    def forgets(self):
        return ReceiptLedger.get_instance().for_subsystem("halcyon.forget")

    def test_recall_counts_what_it_hands_back(self):
        self.seed({"river": "runs east past the mill"})
        self.engine.process_turn("Which way does the river run?")
        self.assertEqual(self.engine.store.memory_stats()["river"][0], 1)

    def test_a_turn_at_the_high_water_mark_forgets_through_the_gate(self):
        self.seed(notes(9))
        self.engine.store.note_recalled(["note0"])
        self.engine.process_turn("Tell me something.")
        self.assertEqual(len(self.memory()), 8)
        self.assertIn("note0", self.memory())
        self.assertNotIn("note1", self.memory())
        (receipt,) = self.forgets()
        self.assertEqual((receipt.effect, receipt.result_count), ("ACCEPT", 1))
        self.assertIn("forget", [p["verb"] for p in self.engine.store.audit("proposals")])

    def test_below_the_mark_a_turn_forgets_nothing(self):
        self.seed(notes(3))
        turns = len(self.engine.store.audit("turns"))
        self.engine.process_turn("Tell me something.")
        self.assertEqual(self.forgets(), [])
        self.assertEqual(len(self.engine.store.audit("turns")), turns + 1)

    def test_rem_merges_near_duplicates(self):
        memory = {"dog_name": "Brisket", "pet_name": "Brisket, a dog", "allergy": "cashews"}
        self.seed(memory)
        vec = {"dog_name": [1.0, 0.0], "pet_name": [0.99, 0.05], "allergy": [0.0, 1.0]}
        self.engine.store.save_memory_vectors(
            [(k, memory_hash(k, memory[k]), MODEL, v) for k, v in vec.items()], keep=set(memory))
        self.engine.store.note_recalled(["pet_name"])
        embedder = SimpleNamespace(degraded=False, backend="fake", model="concepts")
        with patch("spores.embeddings.SemanticEmbedder.get_instance", return_value=embedder):
            self.engine.orchestrator._process_rem_tick()
        self.assertEqual(set(self.memory()), {"pet_name", "allergy"})
        self.assertNotIn("dog_name", self.engine.store.memory_vectors())
        self.assertEqual(self.forgets()[-1].inputs["merged"], 1)

    def test_a_turn_below_the_mark_leaves_merging_to_rem(self):
        memory = {"dog_name": "Brisket", "pet_name": "Brisket, a dog"}
        self.seed(memory)
        self.engine.store.save_memory_vectors(
            [(k, memory_hash(k, memory[k]), MODEL, [1.0, 0.0]) for k in memory], keep=set(memory))
        embedder = SimpleNamespace(degraded=False, backend="fake", model="concepts")
        with patch("spores.embeddings.SemanticEmbedder.get_instance", return_value=embedder):
            self.engine.orchestrator.consolidate_memory("t", "memory near its cap", only_near_cap=True)
        self.assertEqual(set(self.memory()), set(memory))
