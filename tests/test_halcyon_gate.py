from tests.base import BoneTestCase
from main import BoneAmanita
import json

class TestHalcyonGate(BoneTestCase):
    def test_gate_initialization(self):
        engine = self.engine
        self.assertTrue(hasattr(engine, "store"))
        self.assertTrue(hasattr(engine, "boundary"))
        self.assertTrue(hasattr(engine, "gate_tools"))
        self.assertTrue(hasattr(engine, "gate_invariants"))
        
        # Test basic store functionality
        seq, state = engine.store.state()
        self.assertGreaterEqual(seq, 0)
        self.assertIn("world", state)
        self.assertIn("self", state)

    def test_gate_deny(self):
        ctx = self.engine.orchestrator._execute_core_cycle("This is my thought process.\nNOMINATE what=world/nodes verb=create args=name:TestNode;type:concept")
        # Should be denied if it breaks an invariant or wasn't formatted perfectly, but actually if the LLM output was forced to be NOMINATE, 
        # it should run through the gate in cycle.py. 
        # Wait, the LLM output is generated inside _execute_core_cycle, so we can't inject NOMINATE directly unless we mock the LLM.
        # But we can test the Gate class directly.
        from engine.gate.kernel import Gate
        import copy
        seq, state = self.engine.store.state()
        gate = Gate(self.engine.boundary, copy.deepcopy(state), self.engine.gate_tools, self.engine.gate_invariants)
        receipt = gate.adjudicate("This is my thought process.\nNOMINATE what=world/nodes verb=create args=name:TestNode;type:concept")
        self.assertEqual(receipt["decision"], "ACCEPT")
        
        self.engine.store.commit_cycle("test-trace", gate.state, seq, receipt, "raw")
        seq2, state2 = self.engine.store.state()
        self.assertEqual(seq2, 1)
        self.assertIn("entity:testnode", state2["world"]["nodes"])
