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

    def test_arch_lexical_firewall_cliche_tax(self):
        """The Pinker Test: Ensures Semantic Antigens yield 0 ATP and spike Cortisol."""
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

        # We explicitly mock ux() to ensure the log message is written regardless of localization files
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
        """The Meadows Test: Ensures the Panic Room preserves baseline Serotonin while dropping all other chemistry."""
        print("\n--- ARCH 5: Panic Room State Retention ---")
        from machine.panic import PanicRoom

        # Simulate a highly toxic, stressed out previous state
        toxic_prev_state = {
            "chem": {"SER": 0.85, "COR": 1.0, "DOP": 0.9, "ADR": 1.0}
        }

        safe_bio = PanicRoom.get_safe_bio(previous_state=toxic_prev_state)

        # Assert Cortisol and Adrenaline were successfully purged
        self.assertEqual(safe_bio["chem"]["COR"], 0.0, "[FAIL] Panic Room failed to purge Cortisol.")
        self.assertEqual(safe_bio["chem"]["ADR"], 0.0, "[FAIL] Panic Room failed to purge Adrenaline.")

        # Assert Serotonin was retained for systemic stabilization
        self.assertEqual(safe_bio["chem"]["SER"], 0.85, "[FAIL] Panic Room incorrectly wiped retained Serotonin.")

        # Test the baseline floor (should clamp to 0.2 if previous was lower)
        low_ser_state = {"chem": {"SER": 0.05, "COR": 1.0}}
        clamped_bio = PanicRoom.get_safe_bio(previous_state=low_ser_state)
        self.assertEqual(clamped_bio["chem"]["SER"], 0.2,
                         "[FAIL] Panic Room failed to apply the 0.2 Serotonin survival floor.")

        print("  [SUCCESS] Panic Room cleanly purged stress chemistry while retaining necessary structural Serotonin.")