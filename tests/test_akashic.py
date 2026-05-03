"""tests/test_akashic.py"""

import os
import json
import tempfile
from unittest.mock import MagicMock
from tests.base import BoneTestCase
from brain.akashic import TheAkashicRecord
from core import LoreManifest

class AkashicContinuityTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        # Create an isolated temporary directory for save data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.save_dir = self.temp_dir.name

        # Mock LoreManifest so we don't pollute real game data
        self.mock_lore = LoreManifest()
        self.mock_lore.data = {"SYSTEM_PROMPTS": {"GLOBAL_BASELINE": {}}}

        # Initialize Akashic Record wrapped in the temp directory
        self.akashic = TheAkashicRecord(lore_manifest=self.mock_lore)
        self.akashic.save_dir = self.save_dir
        self.akashic.state_path = os.path.join(self.save_dir, "akashic_state.json")

    def tearDown(self):
        self.temp_dir.cleanup()
        super().tearDown()

    def test_epigenetic_load_balance(self):
        """
        The Pinker & Schur Test: Ensures both trauma (scars) AND success (boons)
        are loaded into the system prompts. Prevents the 'Trauma Bias' regression.
        """
        # 1. Manually write mock scars and boons to the temp save directory
        scars_path = os.path.join(self.save_dir, "akashic_scars.json")
        boons_path = os.path.join(self.save_dir, "akashic_boons.json")

        with open(scars_path, "w") as f:
            json.dump(["SCAR TISSUE [FIRE]: Do not touch the stove."], f)

        with open(boons_path, "w") as f:
            json.dump(["STRUCTURAL SUCCESS [WATER]: Hydration is optimal."], f)

        # 2. Trigger the load
        self.akashic._load_mythos_state()

        # 3. Assert both exist in the lore manifest
        prompts = self.mock_lore.get("SYSTEM_PROMPTS").get("GLOBAL_BASELINE", {})
        self.assertIn("EPIGENETIC_SCARS", prompts, "[FAIL] Scars failed to load into memory.")
        self.assertIn("EPIGENETIC_BOONS", prompts, "[FAIL] Boons failed to load! The system forgot how to succeed.")
        self.assertEqual(len(prompts["EPIGENETIC_SCARS"]), 1)
        self.assertEqual(len(prompts["EPIGENETIC_BOONS"]), 1)

    def test_recipe_amnesia_prevention(self):
        """
        The Fuller Test: Ensures uncompleted recipe candidates survive a system reboot.
        """
        # 1. Inject a partial recipe
        test_recipe = ("Iron", "Fire")
        self.akashic.recipe_candidates[test_recipe] = {"Molten Iron": 2}

        # 2. Save the state
        self.akashic._save_user_state()

        # 3. Create a totally fresh Akashic instance pointing to the same save dir
        rebooted_akashic = TheAkashicRecord(lore_manifest=self.mock_lore)
        rebooted_akashic.save_dir = self.save_dir
        rebooted_akashic.state_path = os.path.join(self.save_dir, "akashic_state.json")

        # 4. Load the state
        rebooted_akashic._load_mythos_state()

        # 5. Assert the partial recipe survived the reboot
        self.assertIn(test_recipe, rebooted_akashic.recipe_candidates,
                      "[FAIL] Recipe candidates evaporated during reboot. Amnesic crafting detected.")
        self.assertEqual(rebooted_akashic.recipe_candidates[test_recipe]["Molten Iron"], 2)

    def test_atomic_write_integrity(self):
        """
        The Meadows Test: Verifies that save_to_disk does not leave lingering .tmp files,
        confirming the atomic write swap completed cleanly without stranding partial data.
        """
        category = "test_atomic"
        dummy_data = {"key": "value"}

        # 1. Trigger the save
        self.akashic.save_to_disk(category, dummy_data)

        # 2. Verify final file exists and tmp file was deleted
        final_path = os.path.join(self.save_dir, f"akashic_{category}.json")
        tmp_path = f"{final_path}.tmp"

        self.assertTrue(os.path.exists(final_path), "[FAIL] Final file was not created.")
        self.assertFalse(os.path.exists(tmp_path), "[FAIL] Temporary .tmp file was left behind! Atomic swap failed.")