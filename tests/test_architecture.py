"""tests/test_architecture.py"""

import ast
import os
from unittest.mock import patch

from main import BoneAmanita
from physics.models import PhysicsPacket
from tests.base import BoneTestCase


class ArchitectureTests(BoneTestCase):
    def test_arch_type_agnostic_physics(self):
        phys_obj = PhysicsPacket(chi=0.85, voltage=45.0)
        phys_obj.clean_words = ["structured", "prose", "kinetic", "heavy"]
        phys_dict = {
            "chi": 0.85,
            "voltage": 45.0,
            "clean_words": ["structured", "prose", "kinetic", "heavy"],
        }
        track = self.engine.soma.digestive
        _, yield_obj, _ = track.harvest(phys_obj, [])
        _, yield_dict, _ = track.harvest(phys_dict, [])
        self.assertGreater(
            yield_obj,
            0.0,
            "[FAIL] Digestive track starved when fed a PhysicsPacket object.",
        )
        self.assertGreater(
            yield_dict,
            0.0,
            "[FAIL] Digestive track starved when fed a serialized dictionary.",
        )
        self.assertEqual(
            yield_obj, yield_dict, "[FAIL] Metabolic yield differs based on data type!"
        )

    def test_cortex_gordon_and_toxicity_rejection(self):
        from unittest.mock import MagicMock

        from brain.cortex import TheCortex
        from core import CycleContext

        mock_svc = MagicMock()
        mock_svc.config_ref = None
        mock_svc.bio.mito.state.ros_buildup = 0.0
        mock_svc.host_stats.latency = 0.0
        mock_svc.lore.get.return_value = []
        del mock_svc.mind_memory.nodes
        mock_svc.orchestrator.eng.navi_sad.calculate_semantic_dimension.return_value = (
            1.0
        )
        mock_svc.orchestrator.eng.shared_lattice = None
        mock_svc.orchestrator.eng.governor.calculate_coupling.return_value = 0.5
        mock_svc.orchestrator.eng.governor.get_policy_shift.return_value = "EFFICIENCY"
        mock_svc.inventory.process_loot_tags.return_value = ("Normal response.", [])
        mock_svc.orchestrator.eng.gatekeeper.audit_generation.return_value = (
            True,
            "Normal response.",
        )
        mock_svc.orchestrator.eng.substrate = None
        mock_svc.orchestrator.eng.tick_count = 3
        cortex = TheCortex(services=mock_svc, llm_client=MagicMock())
        cortex.active_mode = "ADVENTURE"
        cortex.pragmatist = MagicMock()
        cortex.pragmatist.enforce_maxims.return_value = ("Normal response.", False)
        ctx_gordon = CycleContext(
            input_text="Testing Gordon.",
            physics={"narrative_drag": 2.0, "chi": 0.5, "m_a": 0.4},
        )
        res_gordon = cortex.process_context(ctx_gordon)
        self.assertEqual(
            res_gordon.get("type"),
            "SYSTEM_HALT",
            "[FAIL] Gordon failed to lock the architecture under high narrative drag.",
        )
        self.assertIn(
            "Tensegrity Anchor engaged",
            res_gordon.get("ui", ""),
            "[FAIL] Missing Gordon UI rejection message.",
        )
        ctx_toxic = CycleContext(
            input_text="Testing Toxicity.",
            physics={"narrative_drag": 1.0, "chi": 0.5, "m_a": 1.0},
        )
        res_toxic = cortex.process_context(ctx_toxic)
        self.assertEqual(
            res_toxic.get("type"),
            "COUNTERFACTUAL_REJECTION",
            "[FAIL] Cortex failed to detect Counterfactual Toxicity.",
        )
        self.assertTrue(
            mock_svc.mind_memory.record_scar.called,
            "[FAIL] Cortex failed to record a trauma scar upon toxicity rejection.",
        )
        self.assertEqual(
            mock_svc.bio.mito.adjust_atp.call_args[0][0],
            -10.0,
            "[FAIL] Toxicity did not accurately tax the ATP pool.",
        )

    def test_cortex_jester_false_cohesion_break(self):
        from unittest.mock import MagicMock

        from brain.cortex import TheCortex
        from core import CycleContext

        mock_svc = MagicMock()
        mock_svc.config_ref = None
        mock_svc.bio.endo.get_state.return_value = {}
        mock_svc.host_stats.latency = 0.0
        mock_svc.village = None
        mock_svc.inventory = None
        mock_svc.consultant = None
        mock_svc.lore.get.return_value = {}
        mock_svc.symbiosis.get_prompt_modifiers.return_value = {}
        mock_svc.mind_memory.ann = None
        mock_svc.mind_memory.graph = {}
        del mock_svc.mind_memory.nodes
        mock_eng = mock_svc.orchestrator.eng
        mock_eng.tick_count = 3
        mock_eng.navi_sad.detect_point_attractor.return_value = True
        mock_eng.navi_sad.calculate_semantic_dimension.return_value = 1.0
        mock_eng.shared_lattice = None
        mock_eng.substrate = None
        mock_eng.governor.calculate_coupling.return_value = 0.5
        mock_eng.governor.get_policy_shift.return_value = "EFFICIENCY"
        mock_eng.gatekeeper.audit_generation.return_value = (True, "Normal response.")
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Normal response."
        cortex = TheCortex(services=mock_svc, llm_client=mock_llm)
        cortex.active_mode = "ADVENTURE"
        cortex.validator = MagicMock()
        cortex.validator.validate.return_value = {
            "valid": True,
            "content": "Normal response.",
        }
        cortex.pragmatist.enforce_maxims = MagicMock(
            return_value=("Normal response.", False)
        )
        cortex.dspy_critic.enabled = False
        ctx = CycleContext(
            input_text="Hello",
            is_system_event=False,
            physics={"repetition": 0.9, "voltage": 50.0},
        )
        res = cortex.process_context(ctx)
        self.assertTrue(
            mock_eng.drain_atp.called,
            "[FAIL] Jester failed to drain ATP during False Cohesion.",
        )
        self.assertEqual(
            res["physics"]["entropy"],
            0.99,
            "[FAIL] Jester failed to violently spike entropy to 0.99.",
        )
        mock_eng.soul.force_mutation.assert_called_with("JESTER")
        self.assertEqual(
            res["mind"]["lens"],
            "JESTER",
            "[FAIL] The localized sim_result mind lens was not successfully overridden by JESTER.",
        )

    def test_immune_evaluation_with_object_physics(self):
        class MockPhysicsPacket:
            def __init__(self):
                self.mu = 0.5
                self.i_c = 0.8
                self.entropy = 0.9

        engine = BoneAmanita({})
        mock_packet = MockPhysicsPacket()
        try:
            result = engine._evaluate_immune_response(
                user_message="test", active_phys=mock_packet
            )
            self.assertIsNone(result)
        except AttributeError as e:
            self.fail(
                f"Immune evaluation failed to safely parse an Object (Eager Evaluation Trap triggered): {e}"
            )

    def test_immune_system_malformed_physics_resilience(self):
        engine = BoneAmanita({})
        fractured_phys = {"random_key": 42, "string_val": "broken"}
        try:
            result = engine._evaluate_immune_response(
                user_message="test", active_phys=fractured_phys
            )
            self.assertIsNone(
                result,
                "[FAIL] Immune system falsely flagged fractured physics as an anomaly.",
            )
        except Exception as e:
            self.fail(
                f"Engine crashed when immune system encountered malformed physics data: {e}"
            )

    def test_arch_eventbus_ghost_prevention(self):
        execution_count = {"hits": 0}

        def dummy_listener(data):
            execution_count["hits"] += 1

        self.engine.events.subscribe("TEMP_EVENT", dummy_listener)
        self.engine.events.publish("TEMP_EVENT", {"data": "test"})
        self.assertEqual(
            execution_count["hits"], 1, "[FAIL] Listener failed to attach."
        )
        self.engine.events.unsubscribe("TEMP_EVENT", dummy_listener)
        self.engine.events.publish("TEMP_EVENT", {"data": "ghost"})
        self.assertEqual(
            execution_count["hits"],
            1,
            "[FAIL] Ghost listener detected! Unsubscribe failed to detach the callback.",
        )

    def test_arch_unqualified_imports(self):
        restricted_modules = {"tools", "gui", "lexicon", "commands", "inventory"}
        violations = []
        target_dirs = ["body", "brain", "archetypes", "mechanics", "physics"]
        base_path = os.path.dirname(os.path.dirname(__file__))
        for d in target_dirs:
            dir_path = os.path.join(base_path, d)
            if not os.path.exists(dir_path):
                continue
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            try:
                                tree = ast.parse(f.read(), filename=file)
                                for node in ast.walk(tree):
                                    if isinstance(node, ast.ImportFrom):
                                        if node.module in restricted_modules:
                                            violations.append(
                                                f"{file}: 'from {node.module}' (Should be 'from mechanics.{node.module}')"
                                            )
                                    elif isinstance(node, ast.Import):
                                        for alias in node.names:
                                            if alias.name in restricted_modules:
                                                violations.append(
                                                    f"{file}: 'import {alias.name}' (Unqualified)"
                                                )
                            except Exception:
                                pass

        def test_telemetry_anchoring(self):
            from core import TelemetryService

            telemetry = TelemetryService(self.test_config)
            telemetry.kernel_hash = "SESSION_77"
            telemetry.current_trace_file = "dummy_path.json"
            telemetry.start_cycle("test_turn")
            self.assertEqual(
                telemetry.active_crystal.kernel_hash,
                "SESSION_77",
                "[FAIL] DecisionCrystal failed to inherit the kernel hash.",
            )
            telemetry.record_event({"action": "jump"})
            last_write = telemetry.write_buffer[-1]
            self.assertIn(
                '"kernel_hash": "SESSION_77"',
                last_write,
                "[FAIL] Telemetry failed to stamp the kernel hash onto the raw event log.",
            )

    def test_arch_narrative_bleed(self):
        with patch("brain.mind.ux", return_value=None):
            directive = self.engine.cortex.modulator.get_mood_directive()
            self.assertNotEqual(
                str(directive).strip().lower(),
                "none",
                "[FAIL] Narrative bleed detected! Missing ux() string resulted in 'None' being injected into the system.",
            )
            self.assertIsInstance(
                directive, str, "[FAIL] Directive must strictly return a string."
            )

    def test_arch_panic_room_serotonin_retention(self):
        from machine.panic import PanicRoom

        toxic_prev_state = {"chem": {"SER": 0.85, "COR": 1.0, "DOP": 0.9, "ADR": 1.0}}
        safe_bio = PanicRoom.get_safe_bio(previous_state=toxic_prev_state)
        self.assertEqual(
            safe_bio["chem"]["COR"], 0.0, "[FAIL] Panic Room failed to purge Cortisol."
        )
        self.assertEqual(
            safe_bio["chem"]["ADR"],
            0.0,
            "[FAIL] Panic Room failed to purge Adrenaline.",
        )
        self.assertEqual(
            safe_bio["chem"]["SER"],
            0.85,
            "[FAIL] Panic Room incorrectly wiped retained Serotonin.",
        )
        low_ser_state = {"chem": {"SER": 0.05, "COR": 1.0}}
        clamped_bio = PanicRoom.get_safe_bio(previous_state=low_ser_state)
        self.assertEqual(
            clamped_bio["chem"]["SER"],
            0.2,
            "[FAIL] Panic Room failed to apply the 0.2 Serotonin survival floor.",
        )

    @patch("cycle.CongruenceValidator.__init__", return_value=None)
    def test_arch_hot_loop_validator_singleton(self, mock_validator_init):
        self.engine.orchestrator.run_headless_turn("Testing the loop.")
        self.assertEqual(
            mock_validator_init.call_count,
            0,
            "[FAIL] CongruenceValidator was instantiated during the cycle hot-loop! This causes a memory leak.",
        )
        self.assertTrue(
            hasattr(self.engine.orchestrator, "congruence_validator"),
            "[FAIL] GeodesicOrchestrator is missing the single-instance congruence_validator.",
        )
