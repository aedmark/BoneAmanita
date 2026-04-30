"""tests/test_architecture.py"""

import os
import ast
from unittest.mock import patch
from physics.models import PhysicsPacket
from tests.base import BoneTestCase

class ArchitectureTests(BoneTestCase):

    def test_arch_type_agnostic_physics(self):
        """The Meadows Test: Ensures biological functions don't starve or crash when physics changes types."""
        print("\n--- ARCH 1: Type-Agnostic Physics ---")

        # Scenario A: Physics loaded natively from the engine
        phys_obj = PhysicsPacket(chi=0.85, voltage=45.0)
        phys_obj.clean_words = ["structured", "prose", "kinetic", "heavy"]

        # Scenario B: Physics loaded from a JSON stasis checkpoint
        phys_dict = {"chi": 0.85, "voltage": 45.0, "clean_words": ["structured", "prose", "kinetic", "heavy"]}

        # We test DigestiveTrack.harvest to ensure it yields > 0 ATP for both
        track = self.engine.soma.digestive

        _, yield_obj, _ = track.harvest(phys_obj, [])
        _, yield_dict, _ = track.harvest(phys_dict, [])

        self.assertGreater(yield_obj, 0.0, "[FAIL] Digestive track starved when fed a PhysicsPacket object.")
        self.assertGreater(yield_dict, 0.0, "[FAIL] Digestive track starved when fed a serialized dictionary.")
        self.assertEqual(yield_obj, yield_dict, "[FAIL] Metabolic yield differs based on data type!")
        print("  [SUCCESS] System metabolizes objects and dictionaries equally.")

    def test_arch_unqualified_imports(self):
        """The Pinker Test: Scans the AST to physically block unqualified local imports (e.g., 'from tools')."""
        print("\n--- ARCH 2: Syntactic Import Scanner ---")

        restricted_modules = {"tools", "gui", "lexicon", "commands", "inventory"}
        violations = []

        # Walk the core directories
        target_dirs = ["body", "brain", "archetypes", "mechanics", "physics"]
        base_path = os.path.dirname(os.path.dirname(__file__)) # Go up from tests/

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
                                            violations.append(f"{file}: 'from {node.module}' (Should be 'from mechanics.{node.module}')")
                                    elif isinstance(node, ast.Import):
                                        for alias in node.names:
                                            if alias.name in restricted_modules:
                                                violations.append(f"{file}: 'import {alias.name}' (Unqualified)")
                            except Exception:
                                pass # Skip files with syntax errors for this test

        if violations:
            self.fail(f"[FAIL] Found {len(violations)} unqualified local imports. This causes fatal ModuleNotFoundErrors:\n" + "\n".join(violations))

        print("  [SUCCESS] All local imports are strictly anchored to their parent modules.")

    def test_arch_narrative_bleed(self):
        """The Schur Test: Ensures the system prompt doesn't inject 'None' if a localization string is missing."""
        print("\n--- ARCH 3: Narrative Bleed (The Lexical Fallback) ---")

        # We forcefully mock ux() to simulate a broken or missing localization file
        with patch('brain.mind.ux', return_value=None):
            # If fallbacks are missing, this will return "None"
            directive = self.engine.cortex.modulator.get_mood_directive()

            # We assert that the literal string "None" did not bleed into the output
            self.assertNotEqual(str(directive).strip().lower(), "none",
                                "[FAIL] Narrative bleed detected! Missing ux() string resulted in 'None' being injected into the system.")
            self.assertIsInstance(directive, str, "[FAIL] Directive must strictly return a string.")

        print("  [SUCCESS] Structural fallbacks successfully prevented 'None' from bleeding into the LLM context.")