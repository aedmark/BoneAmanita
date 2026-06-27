"""tests/test_macro.py"""

import os
import unittest
from unittest.mock import patch

from main import BoneAmanita
from presets import BoneConfig
from tests.base import BoneTestCase


class MacroLifecycleTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.chronos_patcher.stop()
        self.config = {
            "boot_mode": "ADVENTURE",
            "config": BoneConfig,
            "mode_settings": {"village_suppression": []},
        }
        self.engine = BoneAmanita(self.config)
        self.test_save_dir = "tests/temp_saves"
        self.test_lore_dir = "tests/temp_lore"
        os.makedirs(self.test_save_dir, exist_ok=True)
        os.makedirs(self.test_lore_dir, exist_ok=True)
        if hasattr(self.engine, "akashic"):
            self.engine.akashic.save_dir = self.test_save_dir
            self.engine.akashic.data_dir = self.test_lore_dir
        if hasattr(self.engine, "chronos"):
            self.engine.chronos.SAVE_DIR = self.test_save_dir

    def tearDown(self):
        for d in [self.test_save_dir, self.test_lore_dir]:
            if os.path.exists(d):
                for f in os.listdir(d):
                    os.remove(os.path.join(d, f))
                os.rmdir(d)

        self.chronos_patcher.start()
        super().tearDown()

    def test_chronos_graceful_shutdown_and_hydration(self):
        self.engine.village.bureau.stamp_count = 99
        self.engine.health = 42.0
        save_msg = self.engine.chronos.save_checkpoint([])
        self.assertIn(
            "quicksave.json", save_msg, "Chronos failed to write the save file."
        )
        self.engine.health = 100.0
        self.engine.village.bureau.stamp_count = 0
        success, _ = self.engine.chronos.resume_checkpoint()
        self.assertTrue(success, "Chronos failed to hydrate the quicksave.")
        self.assertEqual(
            self.engine.health, 42.0, "State variable (Health) failed to re-hydrate."
        )
        self.assertEqual(
            self.engine.village.bureau.stamp_count,
            99,
            "Village SimpleNamespace failed to re-hydrate.",
        )

    @patch("core.LoreManifest.save")
    def test_akashic_glimmer_pipeline(self, mock_save):
        import time
        import uuid

        test_concept = f"EPIPHANY_{uuid.uuid4().hex[:6].upper()}"
        self.engine.events.publish(
            "GLIMMER_FORMED",
            {"concept": test_concept, "paradigm": "A structural truth was found."},
        )
        time.sleep(0.5)
        self.assertTrue(
            mock_save.called,
            "Akashic Record failed to intercept the GLIMMER_FORMED event.",
        )
        args, _ = mock_save.call_args
        category = args[0]
        self.assertEqual(
            category, "SYSTEM_PROMPTS", "Event routed to the wrong save category."
        )
        prompts = self.engine.akashic.lore.get("SYSTEM_PROMPTS") or {}
        boons = prompts.get("GLOBAL_BASELINE", {}).get("EPIGENETIC_BOONS", [])
        self.assertTrue(
            any(test_concept in item for item in boons),
            "The trigger word was missing from the Akashic payload.",
        )

    def test_autophagy_structural_survival(self):
        mem_core = self.engine.embryo.mind.mem.memory_core
        mem_core.graph.clear()
        mem_core.graph["LoadBearingWall"] = {
            "last_tick": 5,
            "edges": {"a": 10, "b": 10, "c": 10, "d": 20},
        }
        mem_core.graph["useless_typo"] = {"last_tick": 104, "edges": {}}
        target, _ = mem_core.cannibalize(current_tick=105)
        self.assertEqual(
            target,
            "useless_typo",
            "FATAL: Autophagy ate the load-bearing wall instead of the useless recency node!",
        )


if __name__ == "__main__":
    unittest.main()
