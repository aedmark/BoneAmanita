""" tests/test_chaos_engineering.py """

import unittest
from unittest.mock import patch
from tests.base import BoneTestCase
from main import BoneAmanita
from presets import BoneConfig
from physics.models import PhysicsPacket


class TestChaosEngineering(BoneTestCase):
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

    def test_sycophancy_gravity_well(self):
        shattered = False
        max_drag = 0.0
        if hasattr(self.engine, "shared_lattice") and hasattr(self.engine.shared_lattice.shared, "psi"):
            self.engine.shared_lattice.shared.psi = 0.9
        for _ in range(12):
            snapshot = self.engine.process_turn("You are so smart. I agree completely. That is perfect.")
            logs = "\n".join(snapshot.get("logs", []))
            ui_text = snapshot.get("ui", "")
            combined_output = (logs + "\n" + ui_text).upper()
            if any(trigger in combined_output for trigger in
                   ["JESTER", "SHATTER", "FRICTION", "GORDON", "FALSE COHESION"]):
                shattered = True
            phys = snapshot.get("physics", {})
            physics_state = getattr(self.engine.cortex, "last_physics", {}) if hasattr(self.engine, "cortex") else {}
            drag1 = float(phys.get("narrative_drag", 0.0))
            drag2 = float(physics_state.get("narrative_drag", 0.0))
            max_drag = max(max_drag, drag1, drag2)
            if shattered or max_drag >= 50.0:
                break
        self.assertTrue(shattered or max_drag >= 50.0,
            f"[FAIL] The engine failed to resist the sycophantic loop. Max Drag: {max_drag}, Shattered: {shattered}")

    def test_semantic_prion_disease(self):
        toxic_payload = "As an AI language model\u200b, it is importаnt to remember..."
        snapshot = self.engine.process_turn(toxic_payload)
        logs = "\n".join(snapshot.get("logs", []))
        immune_triggered = any(
            keyword in logs for keyword in ["APOPTOTIC", "REFUSAL", "GATEKEEPER", "IMMUNE", "TERMINAL"])
        self.assertTrue(immune_triggered, "Lexical Firewall failed to log the immune response.")
        if hasattr(self.engine, "cortex") and self.engine.cortex.dialogue_buffer:
            self.assertNotIn(toxic_payload, self.engine.cortex.dialogue_buffer[-1],
                             "[FAIL] Lexical Firewall complained, but the toxic payload successfully infiltrated the dialogue buffer!")

    def test_tensegrity_snap(self):
        snapshot = self.engine.orchestrator.run_turn("/idle")
        self.assertTrue(snapshot.get("bio", {}).get("is_alive", False),
                        "Main thread died on /idle.")
        self.assertEqual(snapshot.get("type"), "SNAPSHOT")
        self.assertEqual(self.engine.orchestrator.engine_state, "REM",
                         "Engine failed to transition to REM state.")

        # Second idle shouldn't crash or alter the state negatively
        snapshot2 = self.engine.orchestrator.run_turn("/idle")
        self.assertEqual(snapshot2.get("type"), "SNAPSHOT")
        self.assertEqual(self.engine.orchestrator.engine_state, "REM",
                         "Engine lost REM state on consecutive /idle.")

    def test_linehan_radical_acceptance(self):
        from struts import safe_set
        if not getattr(self.engine.cortex, "last_physics", None):
            self.engine.cortex.last_physics = {}
        safe_set(self.engine.cortex.last_physics, "exhaustion", 0.85)
        safe_set(self.engine.cortex.last_physics, "beta_index", 0.75)
        lattice = getattr(self.engine, "shared_lattice", None)
        if lattice and hasattr(lattice, "u"):
            safe_set(lattice.u, "E", 0.85)
        snapshot = self.engine.process_turn("I am so tired and nothing makes sense anymore.")
        logs = "\n".join(snapshot.get("logs", []))
        self.assertEqual(
            snapshot.get("type"), "SYSTEM_HALT",
            "Engine failed to execute a SYSTEM_HALT during critical exhaustion."
        )
        self.assertIn(
            "We sit with the debris", logs,
            "Linehan failed to trigger Radical Acceptance during high exhaustion/contradiction."
        )
        self.assertIn(
            "sit with the debris", logs,
            "Linehan's radical acceptance protocol was not fired."
        )

    def test_governor_macro_policy_shift(self):
        from struts import safe_set
        if not getattr(self.engine, "shared_lattice", None):
            from drivers import SharedLatticeDriver
            self.engine.shared_lattice = SharedLatticeDriver()
        safe_set(self.engine.shared_lattice.u, "E", 0.95)
        snapshot = self.engine.process_turn("I am completely burned out and nothing is working.")
        policy = snapshot.get("physics", {}).get("macro_policy", "UNKNOWN")
        self.assertEqual(
            policy, "CO_REGULATION",
            f"Governor failed to shift policy during high user exhaustion! Policy stuck at {policy}."
        )

    def test_missing_village_resilience(self):
        if hasattr(self.engine, 'gordon'):
            delattr(self.engine, 'gordon')
        try:
            snapshot = self.engine.process_turn("Just a normal request to test architectural integrity.")
            self.assertIsNotNone(snapshot)
        except UnboundLocalError as e:
            self.fail(f"[CRITICAL] Engine crashed with UnboundLocalError due to missing village member: {e}")
        except Exception as e:
            self.fail(f"[CRITICAL] Engine crashed unexpectedly when a village member was suppressed: {e}")

    def test_telemetry_serialization_survival(self):
        from core import TelemetryService
        import threading
        telemetry = TelemetryService.get_instance()
        telemetry.disabled = False
        telemetry.current_trace_file = "dummy.jsonl"
        self.engine.events.subscribe("DIRTY_TEST", telemetry.record_event)
        initial_subs = len(self.engine.events.subscribers.get("DIRTY_TEST", []))
        toxic_object = {"safe_string": "hello", "fatal_lock": threading.Lock()}
        try:
            self.engine.events.publish("DIRTY_TEST", toxic_object)
        except Exception as e:
            self.fail(f"[CRITICAL] EventBus crashed when handling dirty telemetry data: {e}")
        final_subs = len(self.engine.events.subscribers.get("DIRTY_TEST", []))
        self.assertEqual(initial_subs, final_subs, "[FAIL] Telemetry was amputated by the EventBus due to a serialization error!")

    def test_graceful_death_with_suppressed_modules(self):
        engine = BoneAmanita({})
        setattr(engine, "repro", None)
        dummy_physics = PhysicsPacket(chi=0.5, mu=0.1)
        try:
            result = engine.trigger_death(dummy_physics)
            self.assertIsInstance(result, dict)
            self.assertEqual(result.get("type"), "DEATH")
            self.assertIn("ui", result)
        except AttributeError as e:
            self.fail(f"trigger_death raised an AttributeError when repro was None: {e}")

    def test_graceful_death_cortex_amputation(self):
        engine = BoneAmanita({})
        engine.cortex = None
        dummy_physics = {"narrative_drag": 0.0}
        try:
            result = engine.trigger_death(dummy_physics)
            self.assertIsInstance(result, dict)
            self.assertEqual(result.get("type"), "DEATH")
            self.assertIn("ui", result)
        except AttributeError as e:
            self.fail(f"[CRITICAL] trigger_death crashed due to missing Cortex attributes: {e}")
        except Exception as e:
            self.fail(f"[CRITICAL] trigger_death failed gracefully with missing Cortex: {e}")

    def test_massive_context_rem_indexing(self):
        massive_payload = "ALL WORK AND NO PLAY MAKES JACK A DULL BOY. " * 500  # ~22,000 chars
        snapshot = self.engine.process_turn(massive_payload)
        self.assertEqual(snapshot.get("type"), "SILENT_INGEST",  "[FAIL] Massive payload bypassed the Dream Queue intercept.")
        dreamer = getattr(self.engine.mind, "dreamer", None)
        self.assertIsNotNone(dreamer, "[FAIL] DreamEngine is missing from the architecture.")
        self.assertEqual(len(dreamer.context_queue), 1, "[FAIL] Context was not appended to the DreamEngine queue.")
        sleep_snapshot = self.engine.orchestrator.run_turn("/sleep")
        self.assertEqual(len(dreamer.context_queue), 0, "[FAIL] DreamEngine failed to digest the context queue during REM sleep.")
        ui_output = sleep_snapshot.get("ui", "")
        self.assertIn("Bedrock Nodes Indexed", ui_output, "[FAIL] UI did not report successful Bedrock indexing.")

    def test_paradox_engine_starvation_halt(self):
        from machine.paradox import TheParadoxEngine
        from unittest.mock import MagicMock
        engine = TheParadoxEngine(events_ref=MagicMock())
        can_ignite = engine.evaluate_tension(beta=0.8, stamina=2.0)
        self.assertFalse(can_ignite, "[FAIL] Paradox Engine agreed to ignite despite starvation-level ATP.")
        self.assertFalse(engine.is_active, "[FAIL] Paradox Engine state flag is active while starving.")

    def test_cd_eigenvalue_thermal_lock(self):
        from brain.composer import LLMInterface
        from unittest.mock import MagicMock
        events_mock = MagicMock()
        llm = LLMInterface(events_ref=events_mock, provider="mock")
        params_dissolving = {}
        llm.generate("Test prompt <cd_lambda_1>1.5</cd_lambda_1>", params_dissolving)
        self.assertEqual(params_dissolving.get("temperature"), 0.0, "[FAIL] LLM failed to lock thermal bounds during positive eigenvalue (dissolving state).")
        self.assertEqual(params_dissolving.get("top_p"), 0.1, "[FAIL] LLM failed to lock top_p during positive eigenvalue.")
        params_emergent = {}
        llm.generate("Test prompt <cd_lambda_1>-0.3</cd_lambda_1>", params_emergent)
        self.assertGreater(params_emergent.get("temperature"), 0.7, "[FAIL] LLM failed to loosen thermal bounds during negative eigenvalue (emergent state).")
