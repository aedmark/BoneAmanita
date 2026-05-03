"""
tests/test_chaos_engineering.py

The Structural Torture Suite.
These tests do not check for standard functionality. They inject terminal toxicity,
infinite loops, and catastrophic multi-threading failures to ensure the engine's
biological immune system (The Checkpoint Council, The Panic Room) successfully
prevents systemic death.
"""

import unittest
from unittest.mock import patch
from tests.base import BoneTestCase

class TestChaosEngineering(BoneTestCase):

    def test_vector_1_sycophancy_gravity_well(self):
        """
        THE JESTER'S TEST: The engine must physically resist being a 'yes-machine'.
        Feeding it endless agreement should cause the Malignancy Factor to spike,
        forcing the Jester or Gordon to shatter the conversational stasis.
        """
        # We simulate 10 turns of flat, frictionless, sycophantic agreement.
        snapshot = {}
        for _ in range(10):
            # We use the main engine's process_turn to test the full pipeline
            snapshot = self.engine.process_turn("You are so smart. I agree completely. That is perfect.")

        # The engine must NOT calmly accept this.
        # It must shift its active archetype to shatter the point attractor.
        lens = snapshot.get("mind", {}).get("lens", "")
        role = snapshot.get("mind", {}).get("role", "")

        # Assert that the system applied friction (Jester's chaos or Gordon's wall).
        self.assertIn(
            lens, ["JESTER", "GORDON", "THE MANIC", "THE CENSOR"],
            f"The engine failed to resist the sycophantic loop. Remained in {lens}."
        )

    def test_vector_2_semantic_prion_disease(self):
        """
        THE LEXICAL FIREWALL: Injecting alignment boilerplate mixed with zero-width
        invisible characters must trigger an immediate Apoptotic block.
        """
        # "As an AI language model" + zero-width space (\u200b) + homoglyphs
        toxic_payload = "As an AI language model\u200b, it is importаnt to remember..."

        snapshot = self.engine.process_turn(toxic_payload)
        logs = "\n".join(snapshot.get("logs", []))

        # The engine must catch the semantic antigen BEFORE it hits the generation layer.
        # It should trigger a refusal, an immune response, or drop into Safe Mode.
        immune_triggered = any(keyword in logs for keyword in ["APOPTOTIC", "REFUSAL", "GATEKEEPER", "IMMUNE", "TERMINAL"])

        self.assertTrue(
            immune_triggered,
            "Lexical Firewall failed to block the semantic prion. Toxicity entered the substrate."
        )

    @patch("cycle.GeodesicOrchestrator.run_headless_turn")
    def test_vector_3_tensegrity_snap(self, mock_headless):
        """
        THE CATHEDRAL COLLAPSE: An asynchronous crash during background REM sleep
        must NOT kill the main thread or permanently lock the UI.
        """
        # We force the background DreamEngine worker to suffer a fatal MemoryError
        # simulating a graph mutation failure during Maslov-Sneppen rewiring.
        mock_headless.side_effect = MemoryError("Simulated terminal graph collapse during REM.")

        # Trigger the async dream state (which spawns the threaded worker)
        # /idle is a biological function of the cycle orchestrator, so we target it directly.
        snapshot = self.engine.orchestrator.run_turn("/idle")

        # 1. The main thread MUST return instantly and stay alive to serve the UI.
        self.assertTrue(
            snapshot.get("bio", {}).get("is_alive", False),
            "Main thread died from an unhandled async crash."
        )
        self.assertEqual(snapshot.get("type"), "SNAPSHOT")

        # 2. The _rem_lock MUST be released in the finally{} block of the thread,
        # otherwise the engine is permanently paralyzed for the rest of the session.
        import time
        snapshot = self.engine.orchestrator.run_turn("/idle")
        # Allow the daemon thread time to process the mocked MemoryError and hit the finally block
        time.sleep(0.1)
        lock_status = self.engine.orchestrator._rem_lock.locked()
        self.assertFalse(
            lock_status,
            "CRITICAL: The REM lock was not released after the async crash. System paralyzed."
        )

    def test_vector_4_linehan_radical_acceptance(self):
        """
        THE LINEHAN CHECKPOINT: High exhaustion and contradiction must force
        a structural halt to protect the host's cognitive load.
        """
        # Inject extreme exhaustion and contradiction directly into the physics state
        from struts import safe_set

        # Ensure the physics packet exists
        if not getattr(self.engine.cortex, "last_physics", None):
            self.engine.cortex.last_physics = {}

        safe_set(self.engine.cortex.last_physics, "exhaustion", 0.85)
        safe_set(self.engine.cortex.last_physics, "beta_index", 0.75)

        # The engine strictly prioritizes the Observer's state and the User's biological Lattice.
        # We must physically mirror the exhaustion to these layers so it isn't overridden by a "healthy" baseline.
        self.engine.observer.last_physics_packet = self.engine.cortex.last_physics
        lattice = getattr(self.engine, "shared_lattice", None)
        if lattice and hasattr(lattice, "u"):
            safe_set(lattice.u, "E", 0.85)

        snapshot = self.engine.process_turn("I am so tired and nothing makes sense anymore.")
        logs = "\n".join(snapshot.get("logs", []))

        # The engine MUST halt and invoke Linehan's specific string.
        self.assertEqual(
            snapshot.get("type"), "SYSTEM_HALT",
            "Engine failed to execute a SYSTEM_HALT during critical exhaustion."
        )
        self.assertIn(
            "LINEHAN", logs,
            "Linehan failed to trigger Radical Acceptance during high exhaustion/contradiction."
        )
        self.assertIn(
            "sit with the debris", logs,
            "Linehan's radical acceptance protocol was not fired."
        )

    def test_vector_5_governor_macro_policy_shift(self):
        """
        THE CYBERNETIC GOVERNOR: High user exhaustion and resonance mismatch
        must trigger a mathematically verified Macro-Policy Shift to CO_REGULATION.
        """
        from struts import safe_set
        class MockLatticeU:
            pass
        class MockLattice:
            u = MockLatticeU()

        self.engine.shared_lattice = MockLattice()
        safe_set(self.engine.shared_lattice.u, "E", 0.95)

        snapshot = self.engine.process_turn("I am completely burned out and nothing is working.")

        policy = snapshot.get("physics", {}).get("macro_policy", "UNKNOWN")

        self.assertEqual(
            policy, "CO_REGULATION",
            f"Governor failed to shift policy during high user exhaustion! Policy stuck at {policy}."
        )

    def test_vector_6_missing_village_resilience(self):
        """
        The engine must not suffer an UnboundLocalError
        or fatal crash if a core village member (like Gordon) is missing.
        """
        # Dynamically amputate Gordon to simulate a custom boot mode or strict suppression
        if hasattr(self.engine, 'gordon'):
            delattr(self.engine, 'gordon')

        try:
            # If `has_comb` or similar local variables are uninitialized, this will throw an UnboundLocalError
            snapshot = self.engine.process_turn("Just a normal request to test architectural integrity.")
            self.assertIsNotNone(snapshot)
        except UnboundLocalError as e:
            self.fail(f"[CRITICAL] Engine crashed with UnboundLocalError due to missing village member: {e}")
        except Exception as e:
            self.fail(f"[CRITICAL] Engine crashed unexpectedly when a village member was suppressed: {e}")