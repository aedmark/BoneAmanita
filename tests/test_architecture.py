"""tests/test_architecture.py"""
import os
import ast
from unittest.mock import patch
from physics.models import PhysicsPacket
from tests.base import BoneTestCase
from main import BoneAmanita
from presets import BoneConfig


class ArchitectureTests(BoneTestCase):
    def test_arch_type_agnostic_physics(self):
        """Ensures biological functions don't starve or crash when physics changes types."""
        print("\n--- ARCH 1: Type-Agnostic Physics ---")
        phys_obj = PhysicsPacket(chi=0.85, voltage=45.0)
        phys_obj.clean_words = ["structured", "prose", "kinetic", "heavy"]
        phys_dict = {"chi": 0.85, "voltage": 45.0, "clean_words": ["structured", "prose", "kinetic", "heavy"]}
        track = self.engine.soma.digestive
        _, yield_obj, _ = track.harvest(phys_obj, [])
        _, yield_dict, _ = track.harvest(phys_dict, [])
        self.assertGreater(yield_obj, 0.0, "[FAIL] Digestive track starved when fed a PhysicsPacket object.")
        self.assertGreater(yield_dict, 0.0, "[FAIL] Digestive track starved when fed a serialized dictionary.")
        self.assertEqual(yield_obj, yield_dict, "[FAIL] Metabolic yield differs based on data type!")
        print("  [SUCCESS] System metabolizes objects and dictionaries equally.")

    def test_immune_evaluation_with_object_physics(self):
        """Ensures pre-flight checks use safe attribute retrieval and do not eagerly evaluate dictionary methods on Objects."""

        class MockPhysicsPacket:
            def __init__(self):
                self.mu = 0.5
                self.i_c = 0.8
                self.entropy = 0.9

        engine = BoneAmanita({})
        mock_packet = MockPhysicsPacket()
        try:
            result = engine._evaluate_immune_response(user_message="test", active_phys=mock_packet,
                                                      halt_func=lambda msg: None)
            self.assertIsNone(result)
        except AttributeError as e:
            self.fail(f"Immune evaluation failed to safely parse an Object (Eager Evaluation Trap triggered): {e}")

    def test_arch_small_model_scaffolding(self):
        """Ensures the engine lowers cognitive complexity for sub-15B models."""
        print("\n--- ARCH 8: Lightweight Model Scaffolding ---")
        from main import BoneAmanita
        from unittest.mock import MagicMock
        config = {
            "model": "llama3-8b-instruct",
            "boot_mode": "CREATIVE",
            "provider": "mock"
        }
        test_engine = BoneAmanita(config)
        test_engine._load_system_prompts = MagicMock()
        test_engine.prompt_library = {"CREATIVE_LITE": "Lightweight Prompt Data"}
        test_engine._apply_boot_mode()
        if hasattr(test_engine.cortex, "dspy_critic"):
            self.assertFalse(test_engine.cortex.dspy_critic.enabled,
                             "[FAIL] Engine failed to disable the DSPy Affective Critic for an 8B model!")
        expected_key = test_engine.mode_settings.get("prompt_key")
        self.assertEqual(expected_key, "CREATIVE_LITE",
                         "[FAIL] Engine failed to append the _LITE suffix for the small model prompt!")
        print("  [SUCCESS] System automatically degraded cognitive load for the small model.")

    def test_multiplex_partial_hydration_safety(self):
        """Ensures the engine does not crash when a multiplex lattice exists, but the user state is unhydrated (None)."""
        engine = BoneAmanita({})

        class MockLattice:
            def __init__(self):
                self.u = None
                self.shared = {}

        engine.shared_lattice = MockLattice()
        safe_phys = {"exhaustion": 0.2, "mu": 0.1, "i_c": 1.0}
        try:
            engine._evaluate_immune_response(user_message="test", active_phys=safe_phys, halt_func=lambda msg: None)
            self.assertTrue(True)
        except AttributeError as e:
            self.fail(f"Engine crashed when encountering a partially hydrated multiplex lattice: {e}")

    def test_arch_eventbus_ghost_prevention(self):
        """Ensures temporary EventBus listeners can cleanly detach."""
        print("\n--- ARCH 7: EventBus Outflow (Memory Leak Check) ---")
        execution_count = {"hits": 0}

        def dummy_listener(data):
            execution_count["hits"] += 1

        self.engine.events.subscribe("TEMP_EVENT", dummy_listener)
        self.engine.events.publish("TEMP_EVENT", {"data": "test"})
        self.assertEqual(execution_count["hits"], 1, "[FAIL] Listener failed to attach.")
        self.engine.events.unsubscribe("TEMP_EVENT", dummy_listener)
        self.engine.events.publish("TEMP_EVENT", {"data": "ghost"})
        self.assertEqual(execution_count["hits"], 1,
                         "[FAIL] Ghost listener detected! Unsubscribe failed to detach the callback.")
        print("  [SUCCESS] EventBus cleanly severed the connection. No memory leaks detected.")

    def test_arch_unqualified_imports(self):
        """Scans the AST to physically block unqualified local imports (e.g., 'from tools')."""
        print("\n--- ARCH 2: Syntactic Import Scanner ---")
        restricted_modules = {"tools", "gui", "lexicon", "commands", "inventory"}
        violations = []
        target_dirs = ["body", "brain", "archetypes", "mechanics", "physics"]
        base_path = os.path.dirname(os.path.dirname(__file__))
        for d in target_dirs:
            dir_path = os.path.join(base_path, d)
            if not os.path.exists(dir_path): continue
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
                                                f"{file}: 'from {node.module}' (Should be 'from mechanics.{node.module}')")
                                    elif isinstance(node, ast.Import):
                                        for alias in node.names:
                                            if alias.name in restricted_modules:
                                                violations.append(f"{file}: 'import {alias.name}' (Unqualified)")
                            except Exception:
                                pass
        if violations:
            self.fail(
                f"[FAIL] Found {len(violations)} unqualified local imports. This causes fatal ModuleNotFoundErrors:\n" + "\n".join(
                    violations))
        print("  [SUCCESS] All local imports are strictly anchored to their parent modules.")

    def test_arch_narrative_bleed(self):
        """Ensures the system prompt doesn't inject 'None' if a localization string is missing."""
        print("\n--- ARCH 3: Narrative Bleed (The Lexical Fallback) ---")
        with patch('brain.mind.ux', return_value=None):
            directive = self.engine.cortex.modulator.get_mood_directive()
            self.assertNotEqual(str(directive).strip().lower(), "none",
                                "[FAIL] Narrative bleed detected! Missing ux() string resulted in 'None' being injected into the system.")
            self.assertIsInstance(directive, str, "[FAIL] Directive must strictly return a string.")
        print("  [SUCCESS] Structural fallbacks successfully prevented 'None' from bleeding into the LLM context.")

    def test_arch_lexical_firewall_cliche_tax(self):
        """Ensures Semantic Antigens yield 0 ATP and spike Cortisol."""
        print("\n--- ARCH 4: The Lexical Firewall (Cliché Tax) ---")
        from unittest.mock import MagicMock, patch
        track = self.engine.soma.digestive
        track.lex = MagicMock()
        mock_data = {
            "antigen": {"delve", "tapestry", "testament", "myriad", "nuance"},
            "kinetic": {"execute", "shatter"}
        }
        track.lex.get.side_effect = lambda k: mock_data.get(k)
        track.lex.get_current_category.return_value = "NONE"
        phys_slop = PhysicsPacket(
            clean_words=["delve", "into", "the", "rich", "tapestry", "of", "myriad", "testament", "and", "nuance"])
        initial_cortisol = self.engine.bio.endo.cortisol
        logs = []
        with patch('body.metabolism.ux', return_value="cliche tax applied: {tax}"):
            dominant_enzyme, yield_atp, hits = track.harvest(phys_slop, logs)
        self.assertEqual(yield_atp, 0.0,
                         f"[FAIL] Lexical Firewall breached! System gained {yield_atp} ATP from reading sycophantic slop.")
        self.assertGreater(self.engine.bio.endo.cortisol, initial_cortisol,
                           "[FAIL] Cortisol did not spike after digesting Semantic Antigens.")
        self.assertTrue(any("cliche" in log.lower() for log in logs),
                        "[FAIL] Cliché Tax was not recorded in the systemic logs.")
        print("  [SUCCESS] Lexical Firewall successfully rejected semantic antigens and levied the Cliché Tax.")

    def test_arch_panic_room_serotonin_retention(self):
        """Ensures the Panic Room preserves baseline Serotonin while dropping all other chemistry."""
        print("\n--- ARCH 5: Panic Room State Retention ---")
        from machine.panic import PanicRoom
        toxic_prev_state = {
            "chem": {"SER": 0.85, "COR": 1.0, "DOP": 0.9, "ADR": 1.0}
        }
        safe_bio = PanicRoom.get_safe_bio(previous_state=toxic_prev_state)
        self.assertEqual(safe_bio["chem"]["COR"], 0.0, "[FAIL] Panic Room failed to purge Cortisol.")
        self.assertEqual(safe_bio["chem"]["ADR"], 0.0, "[FAIL] Panic Room failed to purge Adrenaline.")
        self.assertEqual(safe_bio["chem"]["SER"], 0.85, "[FAIL] Panic Room incorrectly wiped retained Serotonin.")
        low_ser_state = {"chem": {"SER": 0.05, "COR": 1.0}}
        clamped_bio = PanicRoom.get_safe_bio(previous_state=low_ser_state)
        self.assertEqual(clamped_bio["chem"]["SER"], 0.2,
                         "[FAIL] Panic Room failed to apply the 0.2 Serotonin survival floor.")
        print("  [SUCCESS] Panic Room cleanly purged stress chemistry while retaining necessary structural Serotonin.")

    @patch("cycle.CongruenceValidator.__init__", return_value=None)
    def test_arch_hot_loop_validator_singleton(self, mock_validator_init):
        """Ensures the CongruenceValidator is not instantiated during the hot loop."""
        print("\n--- ARCH 6: Hot-Loop Instantiation Leak Check ---")
        self.engine.orchestrator.run_headless_turn("Testing the loop.")
        self.assertEqual(
            mock_validator_init.call_count, 0,
            "[FAIL] CongruenceValidator was instantiated during the cycle hot-loop! This causes a memory leak."
        )
        self.assertTrue(
            hasattr(self.engine.orchestrator, "congruence_validator"),
            "[FAIL] GeodesicOrchestrator is missing the single-instance congruence_validator."
        )
        print("  [SUCCESS] CongruenceValidator is safely anchored as a singleton outside the hot loop.")
