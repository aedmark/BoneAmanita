"""tests/test_akashic.py"""

import json
import os
import tempfile
from unittest.mock import MagicMock

from brain.akashic import TheAkashicRecord
from engine.core import LoreManifest
from engine.gate.store import Store
from tests.base import BoneTestCase


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
        self.store = Store(path=os.path.join(self.save_dir, "iris.db"))
        self.akashic.attach_store(self.store)

    def reboot(self):
        rebooted = TheAkashicRecord(lore_manifest=self.mock_lore)
        rebooted.save_dir = rebooted.data_dir = self.save_dir
        rebooted.state_path = os.path.join(self.save_dir, "akashic_state.json")
        rebooted.attach_store(self.store)
        return rebooted

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
        self.assertIn(
            "EPIGENETIC_SCARS", prompts, "[FAIL] Scars failed to load into memory."
        )
        self.assertIn(
            "EPIGENETIC_BOONS",
            prompts,
            "[FAIL] Boons failed to load! The system forgot how to succeed.",
        )
        self.assertEqual(len(prompts["EPIGENETIC_SCARS"]), 1)
        self.assertEqual(len(prompts["EPIGENETIC_BOONS"]), 1)

    def test_recipe_amnesia_prevention(self):
        test_recipe = ("Iron", "Fire")
        self.akashic.recipe_candidates[test_recipe] = {"Molten Iron": 2}
        self.akashic._save_user_state()
        rebooted_akashic = self.reboot()
        self.assertIn(
            test_recipe,
            rebooted_akashic.recipe_candidates,
            "[FAIL] Recipe candidates evaporated during reboot. Amnesic crafting detected.",
        )
        self.assertEqual(
            rebooted_akashic.recipe_candidates[test_recipe]["Molten Iron"], 2
        )

    def test_crystallize_recipe_ux_formatting(self):
        ingredient = "Iron"
        catalyst = "Fire"
        result_payload = {"name": "Ascended_Artifact", "value": 50.0}
        for _ in range(3):
            self.akashic.track_successful_forge(ingredient, catalyst, result_payload)
        gordon_data = self.mock_lore.get("GORDON") or {}
        recipes = gordon_data.get("RECIPES", [])
        self.assertTrue(len(recipes) > 0, "[FAIL] Recipe did not crystallize.")
        crystallized_msg = recipes[-1].get("msg", "")
        self.assertNotIn("{", crystallized_msg, "[FAIL] UX Sludge detected! Raw dictionary leaked into UI string.")
        self.assertIn("Ascended_Artifact", crystallized_msg, "[FAIL] Result name was not properly extracted for the UI.")

    def test_a_category_is_saved_to_the_store_not_a_file(self):
        # Roadmap step 3d: akashic_<category>.json files, some written inside lore/, are store records now.
        self.akashic.save_to_disk("test_atomic", {"key": "value"})
        self.assertEqual(self.store.record("akashic.test_atomic"), {"key": "value"})
        self.assertEqual([f for f in os.listdir(self.save_dir) if f.startswith("akashic_")], [])

    def test_the_scar_map_and_strata_survive_a_restart(self):
        # _save_user_state wrote them, but the load never read them back.
        self.akashic.scar_map = [{"concept": "Overload", "coordinates": {"E": 0.8}, "gilded": True}]
        self.akashic.subconscious_strata = [{"layer": "old tide"}]
        self.akashic._save_user_state()
        rebooted = self.reboot()
        self.assertEqual(rebooted.scar_map[0]["concept"], "Overload")
        self.assertEqual(rebooted.subconscious_strata, [{"layer": "old tide"}])

    def test_discovered_words_come_back_into_the_lexicon(self):
        self.akashic.discovered_words = {"quernstone": "heavy"}
        self.akashic.save_all()
        self.mock_lore.data["LEXICON"] = {}
        self.reboot()
        self.assertIn("quernstone", self.mock_lore.get("LEXICON")["heavy"])

    def test_older_files_are_imported_once_and_kept(self):
        state_path = os.path.join(self.save_dir, "akashic_state.json")
        words_path = os.path.join(self.save_dir, "akashic_discovered_words.json")
        with open(state_path, "w") as f:
            json.dump({"scar_map": [{"concept": "Old Burn", "coordinates": {}, "gilded": True}]}, f)
        with open(words_path, "w") as f:
            json.dump({"quernstone": "heavy"}, f)
        fresh = Store(path=os.path.join(self.save_dir, "fresh.db"))
        rebooted = TheAkashicRecord(lore_manifest=self.mock_lore)
        rebooted.save_dir = rebooted.data_dir = self.save_dir
        rebooted.state_path = state_path
        rebooted.attach_store(fresh)
        self.assertEqual(rebooted.scar_map[0]["concept"], "Old Burn")
        self.assertEqual(rebooted.discovered_words, {"quernstone": "heavy"})
        for path in (state_path, words_path):
            self.assertFalse(os.path.exists(path))
            self.assertTrue(os.path.exists(path + ".imported"))

    def test_targeted_viability_autophagy(self):
        self.akashic.active_memory_core = MagicMock()
        self.akashic.active_memory_core.subconscious.index = {
            "Mem1_Safe": {"kappa": 0.8, "gamma": 0.8, "beta": 0.1},
            "Mem2_Toxic": {"kappa": 0.5, "gamma": 0.2, "beta": 0.9},
            "Mem3_Neutral": {"kappa": 0.5, "gamma": 0.5, "beta": 0.5},
        }
        yield_val, msg = self.akashic.trigger_autophagy()
        index_keys = self.akashic.active_memory_core.subconscious.index.keys()
        self.assertNotIn(
            "Mem2_Toxic",
            index_keys,
            "[FAIL] Autophagy did not consume the memory with the lowest viability potential.",
        )
        self.assertIn(
            "Mem1_Safe", index_keys, "[FAIL] Autophagy consumed a highly viable memory."
        )
        self.assertIn(
            "Mem3_Neutral", index_keys, "[FAIL] Autophagy consumed the wrong memory."
        )

    def test_cognitive_density_bfs(self):
        self.akashic.shadow_stock = [
            {"concept": "A", "links": ["B", "C"]},
            {"concept": "B", "links": ["D", "E"]},
            {"concept": "C", "links": ["F"]},
            {"concept": "D", "links": []},
            {"concept": "E", "links": []},
            {"concept": "F", "links": []},
        ]
        self.akashic.scar_map = []
        density = self.akashic.measure_cognitive_density("A")
        import math

        expected_density = math.log(6) / math.log(2)
        self.assertAlmostEqual(
            density,
            expected_density,
            places=2,
            msg="[FAIL] Cognitive Density BFS miscalculated the mass-radius scaling.",
        )
        point_density = self.akashic.measure_cognitive_density("ISOLATED_NODE")
        self.assertEqual(
            point_density,
            1.0,
            "[FAIL] Isolated node did not return a point-mass density of 1.0.",
        )

    def test_dredge_creative_tension(self):
        self.akashic.shadow_stock = [
            {"concept": "Boring", "coords": {"kappa": 0.1, "gamma": 0.1, "mu": 0.1}},
            {"concept": "Tense", "coords": {"kappa": 0.9, "gamma": 0.9, "mu": 0.9}},
            {
                "concept": "CoherentOnly",
                "coords": {"kappa": 0.9, "gamma": 0.9, "mu": 0.0},
            },
        ]
        best_mem = self.akashic.dredge_creative_tension()
        self.assertIsNotNone(
            best_mem, "[FAIL] Gradient descent RAG failed to return a memory."
        )
        self.assertEqual(
            best_mem["concept"],
            "Tense",
            "[FAIL] Gradient descent RAG did not retrieve the memory with the highest creative drive.",
        )
