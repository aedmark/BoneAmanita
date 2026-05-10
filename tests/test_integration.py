"""tests/test_integration.py"""

import unittest
from unittest.mock import MagicMock
from tests.base import BoneTestCase

class EngineConnectivityTests(BoneTestCase):
    """
    S.L.A.S.H. V3 Umbilical Tests.
    These tests do not mock the internal engine structures. They verify the physical
    connectivity of the Geodesic Orchestrator, The Cortex, and the Biological Substrate.
    """

    def test_orchestrator_cortex_umbilical(self):
        """
        Proves that the GeodesicOrchestrator is actively routing execution
        through TheCortex during the CognitionPhase.
        Prevents 'The Great Disconnect' where the engine runs without the LLM.
        """
        # Spy on the actual context processor without blocking it
        original_process = self.engine.cortex.process_context
        mock_process = MagicMock(side_effect=original_process)
        self.engine.cortex.process_context = mock_process

        # Run a turn natively
        snapshot = self.engine.process_turn("This is a structural integration test.")

        # Assert the umbilical cord is attached and the Cortex was invoked
        self.assertTrue(
            mock_process.called,
            "[FAIL] THE GREAT DISCONNECT: GeodesicOrchestrator bypassed The Cortex entirely."
        )
        self.assertIn(
            "ui", snapshot,
            "[FAIL] GeodesicOrchestrator failed to package the Cortex's UI payload."
        )

        # Restore the engine
        self.engine.cortex.process_context = original_process

    def test_phase_pipeline_accumulation(self):
        """
        Proves that physics, bio, and mind states are preserved and not flattened
        or overwritten as they pass through the Geodesic phase transitions.
        """
        # Inject a tracer particle into the raw context BEFORE it hits the pipeline
        original_gather = self.engine.cortex.gather_state

        def tracer_gather(sim_res):
            if "physics" in sim_res:
                sim_res["physics"]["tracer_particle"] = 84.0
            return original_gather(sim_res)

        self.engine.cortex.gather_state = tracer_gather

        snapshot = self.engine.process_turn("Trace this packet through the cycle.")

        # The tracer must survive the entire cycle, the Cortex, and the snapshot serialization
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
        """
        Proves that an event triggered deep in the memory layer (Mind)
        successfully ripples down to mutate the metabolic layer (Bio).
        """
        initial_atp = self.engine.bio.mito.state.atp_pool

        # Manually inject a sacrificial memory node
        memory_core = getattr(self.engine.mind, "mem", None)
        if memory_core:
            memory_core.graph["Sacrificial Node"] = {"edges": {}, "last_tick": 0}

            # Trigger Autophagy directly
            memory_core.trigger_autophagy()

            # Assert the biological layer heard the memory layer's scream and refunded ATP
            new_atp = self.engine.bio.mito.state.atp_pool
            self.assertGreater(
                new_atp, initial_atp,
                "[FAIL] SEVERED NERVE: Memory layer failed to propagate ATP refund to the Mitochondrial layer."
            )