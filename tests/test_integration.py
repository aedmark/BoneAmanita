"""tests/test_integration.py"""

import unittest
from unittest.mock import MagicMock
from tests.base import BoneTestCase


class EngineConnectivityTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        if not getattr(self.engine, "shared_lattice", None):
            from drivers import SharedLatticeDriver
            self.engine.shared_lattice = SharedLatticeDriver()
        if not hasattr(self.engine.shared_lattice.u, "E"):
            setattr(self.engine.shared_lattice.u, "E", 0.0)
        for attr in ["phi", "resonance_delta"]:
            if not hasattr(self.engine.shared_lattice.shared, attr):
                setattr(self.engine.shared_lattice.shared, attr, 0.0)

    def test_orchestrator_cortex_umbilical(self):
        original_process = self.engine.cortex.process_context
        mock_process = MagicMock(side_effect=original_process)
        self.engine.cortex.process_context = mock_process
        snapshot = self.engine.process_turn("This is a structural integration test.")
        self.assertTrue(
            mock_process.called,
            "[FAIL] THE GREAT DISCONNECT: GeodesicOrchestrator bypassed The Cortex entirely."
        )
        self.assertIn(
            "ui", snapshot,
            "[FAIL] GeodesicOrchestrator failed to package the Cortex's UI payload."
        )
        self.engine.cortex.process_context = original_process

    def test_phase_pipeline_accumulation(self):
        original_gather = self.engine.cortex.gather_state

        def tracer_gather(sim_res):
            if "physics" in sim_res:
                sim_res["physics"]["tracer_particle"] = 84.0
            return original_gather(sim_res)

        self.engine.cortex.gather_state = tracer_gather
        snapshot = self.engine.process_turn("Trace this packet through the cycle.")
        phys_packet = snapshot.get("physics", {})
        self.assertIn(
            "tracer_particle", phys_packet,
            "[FAIL] STRUCTURAL ROT: The phase pipeline dropped dynamic attributes during phase handoff."
        )
        self.assertEqual(
            phys_packet["tracer_particle"], 84.0,
            "[FAIL] The phase pipeline mutated a locked attribute without authorization."
        )
        self.engine.cortex.gather_state = original_gather

    def test_cross_layer_event_propagation(self):
        initial_atp = self.engine.bio.mito.state.atp_pool
        memory_core = getattr(self.engine.mind, "mem", None)
        if memory_core:
            memory_core.graph["Sacrificial Node"] = {"edges": {}, "last_tick": 0}
            memory_core.trigger_autophagy()
            new_atp = self.engine.bio.mito.state.atp_pool
            self.assertGreater(
                new_atp, initial_atp,
                "[FAIL] SEVERED NERVE: Memory layer failed to propagate ATP refund to the Mitochondrial layer."
            )

    def test_benign_full_cycle_integration(self):
        self.engine.active_physics["contextual_anchor"] = "TEST_SURVIVOR"
        snapshot = self.engine.process_turn("Hello. This is a clean, benign integration test.")
        self.assertNotIn(
            snapshot.get("type"),
            ["SYSTEM_HALT", "DEATH", "CRASH"],
            f"[FAIL] The engine halted or crashed on a benign input. Type: {snapshot.get('type')}"
        )
        self.assertIn("ui", snapshot, "[FAIL] The orchestrator failed to return a UI payload.")
        self.assertIn("physics", snapshot, "[FAIL] The orchestrator stripped the physics payload.")
        surviving_physics = snapshot.get("physics", {})
        self.assertEqual(
            surviving_physics.get("contextual_anchor"),
            "TEST_SURVIVOR",
            "[FAIL] Physics Amnesia detected. The cycle daemon wiped the running physics context."
        )