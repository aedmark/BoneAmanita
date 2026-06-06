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
        self.temp_dir = tempfile.TemporaryDirectory()
        self.save_dir = self.temp_dir.name
        self.mock_lore = LoreManifest()
        self.mock_lore.data = {"SYSTEM_PROMPTS": {"GLOBAL_BASELINE": {}}}
        self.akashic = TheAkashicRecord(lore_manifest=self.mock_lore)
        self.akashic.save_dir = self.save_dir
        self.akashic.data_dir = self.save_dir
        self.akashic.state_path = os.path.join(self.save_dir, "akashic_state.json")

    def tearDown(self):
        self.temp_dir.cleanup()
        super().tearDown()

    def test_epigenetic_load_balance(self):
        scars_path = os.path.join(self.akashic.data_dir, "akashic_scars.json")
        boons_path = os.path.join(self.akashic.data_dir, "akashic_boons.json")
        with open(scars_path, "w") as f:
            json.dump(["SCAR TISSUE [FIRE]: Do not touch the stove."], f)
        with open(boons_path, "w") as f:
            json.dump(["STRUCTURAL SUCCESS [WATER]: Hydration is optimal."], f)
        self.akashic._load_mythos_state()
        prompts = self.mock_lore.get("SYSTEM_PROMPTS").get("GLOBAL_BASELINE", {})
        self.assertIn("EPIGENETIC_SCARS", prompts, "[FAIL] Scars failed to load into memory.")
        self.assertIn("EPIGENETIC_BOONS", prompts, "[FAIL] Boons failed to load! The system forgot how to succeed.")
        self.assertEqual(len(prompts["EPIGENETIC_SCARS"]), 1)
        self.assertEqual(len(prompts["EPIGENETIC_BOONS"]), 1)

    def test_recipe_amnesia_prevention(self):
        test_recipe = ("Iron", "Fire")
        self.akashic.recipe_candidates[test_recipe] = {"Molten Iron": 2}
        self.akashic._save_user_state()
        rebooted_akashic = TheAkashicRecord(lore_manifest=self.mock_lore)
        rebooted_akashic.save_dir = self.save_dir
        rebooted_akashic.state_path = os.path.join(self.save_dir, "akashic_state.json")
        rebooted_akashic._load_mythos_state()
        self.assertIn(test_recipe, rebooted_akashic.recipe_candidates, "[FAIL] Recipe candidates evaporated during reboot. Amnesic crafting detected.")
        self.assertEqual(rebooted_akashic.recipe_candidates[test_recipe]["Molten Iron"], 2)

    def test_atomic_write_integrity(self):
        category = "test_atomic"
        dummy_data = {"key": "value"}
        self.akashic.save_to_disk(category, dummy_data)
        final_path = os.path.join(self.save_dir, f"akashic_{category}.json")
        tmp_path = f"{final_path}.tmp"
        self.assertTrue(os.path.exists(final_path), "[FAIL] Final file was not created.")
        self.assertFalse(os.path.exists(tmp_path), "[FAIL] Temporary .tmp file was left behind! Atomic swap failed.")

    def test_targeted_viability_autophagy(self):
        from unittest.mock import MagicMock
        self.akashic.active_memory_core = MagicMock()
        self.akashic.active_memory_core.subconscious.index = {
            "Mem1_Safe": {"kappa": 0.8, "gamma": 0.8, "beta": 0.1},  # b = 0.64 - 0.1 = 0.54
            "Mem2_Toxic": {"kappa": 0.5, "gamma": 0.2, "beta": 0.9},  # b = 0.10 - 0.9 = -0.80  <-- Lowest
            "Mem3_Neutral": {"kappa": 0.5, "gamma": 0.5, "beta": 0.5}  # b = 0.25 - 0.5 = -0.25
        }

        # We let the native dictionary pop() execute and then inspect the debris.
        yield_val, msg = self.akashic.trigger_autophagy()

        index_keys = self.akashic.active_memory_core.subconscious.index.keys()
        self.assertNotIn("Mem2_Toxic", index_keys,
                         "[FAIL] Autophagy did not consume the memory with the lowest viability potential.")
        self.assertIn("Mem1_Safe", index_keys, "[FAIL] Autophagy consumed a highly viable memory.")
        self.assertIn("Mem3_Neutral", index_keys, "[FAIL] Autophagy consumed the wrong memory.")

    def test_cognitive_density_bfs(self):
        self.akashic.shadow_stock = [
            {"concept": "A", "links": ["B", "C"]},
            {"concept": "B", "links": ["D", "E"]},
            {"concept": "C", "links": ["F"]},
            {"concept": "D", "links": []},
            {"concept": "E", "links": []},
            {"concept": "F", "links": []}
        ]
        self.akashic.scar_map = []
        density = self.akashic.measure_cognitive_density("A")
        import math
        expected_density = math.log(6) / math.log(2)
        self.assertAlmostEqual(density, expected_density, places=2, msg="[FAIL] Cognitive Density BFS miscalculated the mass-radius scaling.")
        point_density = self.akashic.measure_cognitive_density("ISOLATED_NODE")
        self.assertEqual(point_density, 1.0, "[FAIL] Isolated node did not return a point-mass density of 1.0.")

    def test_dredge_creative_tension(self):
        self.akashic.shadow_stock = [{"concept": "Boring", "coords": {"kappa": 0.1, "gamma": 0.1, "mu": 0.1}},  # a = 0.001
            {"concept": "Tense", "coords": {"kappa": 0.9, "gamma": 0.9, "mu": 0.9}},  # a = 0.729 <-- Highest
            {"concept": "CoherentOnly", "coords": {"kappa": 0.9, "gamma": 0.9, "mu": 0.0}}  # a = 0.0
]
        best_mem = self.akashic.dredge_creative_tension()
        self.assertIsNotNone(best_mem, "[FAIL] Gradient descent RAG failed to return a memory.")
        self.assertEqual(best_mem["concept"], "Tense", "[FAIL] Gradient descent RAG did not retrieve the memory with the highest creative drive.")
