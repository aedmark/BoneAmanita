"""tests/test_genesis_continuity.py"""

import json
import os
from unittest.mock import MagicMock, patch

from soul.oroboros import Scar, TheOroboros
from tests.base import BoneTestCase


class GenesisContinuityTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.test_legacy_file = "test_legacy_temp.json"
        self.patcher = patch(
            "soul.oroboros.TheOroboros.LEGACY_FILE", self.test_legacy_file
        )
        self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()
        if os.path.exists(self.test_legacy_file):
            os.remove(self.test_legacy_file)

    def test_crystallize_existential_dread(self):
        oro = TheOroboros(config_ref=self.test_config)
        oro.attach_store(self.engine.store)
        mock_soul = MagicMock()
        mock_soul.eng.trauma_accum = {"THERMAL": 8.0, "SEPTIC": 5.0}
        mock_soul.core_memories = []
        with patch("engine.core.LoreManifest.get", return_value={}):
            oro.crystallize("STARVATION", mock_soul)
        dread_scar = next((s for s in oro.scars if s.name == "Existential Dread"), None)
        self.assertIsNotNone(
            dread_scar,
            "[FAIL] Oroboros failed to translate > 10.0 trauma into Existential Dread.",
        )
        self.assertEqual(dread_scar.stat_affected, "trauma_baseline")
        self.assertGreater(dread_scar.value, 0.0)
        lineage = self.engine.store.record("oroboros.lineage")
        self.assertEqual(lineage["generation"], 1)
        self.assertIn("Existential Dread", [s["name"] for s in lineage["scars"]])
        self.assertFalse(os.path.exists(self.test_legacy_file))

    def test_apply_legacy_karma(self):
        oro = TheOroboros(config_ref=self.test_config)
        oro.scars = [
            Scar("Heavy Burden", "narrative_drag", 3.0, "Drag increase."),
            Scar("Exhaustion", "voltage_cap", 5.0, "Voltage penalty."),
        ]
        fresh_physics = {"voltage": 20.0, "narrative_drag": 1.0}
        fresh_bio = {"trauma_vector": {}}
        oro.apply_legacy(fresh_physics, fresh_bio)
        self.assertEqual(
            fresh_physics["narrative_drag"],
            4.0,
            "[FAIL] Generational narrative drag was not applied to the new physics state.",
        )
        self.assertEqual(
            fresh_physics["voltage"],
            15.0,
            "[FAIL] Starting voltage was not penalized! The karma engine failed to enforce exhaustion.",
        )

    def test_apply_legacy_empty_state(self):
        oro = TheOroboros(config_ref=self.test_config)
        oro.scars = []
        fresh_physics = {}
        logs = oro.apply_legacy(fresh_physics, {})
        self.assertEqual(
            len(logs),
            0,
            "[FAIL] Oroboros generated logs for an empty legacy application.",
        )
        self.assertEqual(
            fresh_physics,
            {},
            "[FAIL] Oroboros mutated an empty physics packet unexpectedly.",
        )


class TheLineageLivesInTheStore(BoneTestCase):
    """Roadmap step 3g: what each death leaves the next generation was legacy.json in the repo root."""

    def die(self, oro):
        soul = MagicMock()
        soul.eng.trauma_accum = {"THERMAL": 8.0, "SEPTIC": 5.0}
        memory = MagicMock(impact_voltage=9.0, trigger_words=["lantern"], lesson="Keep a light by the door.")
        soul.core_memories = [memory]
        with patch("engine.core.LoreManifest.get", return_value={}):
            oro.crystallize("STARVATION", soul)

    def test_the_next_engine_inherits_the_scars_and_myths(self):
        from main import BoneAmanita

        self.die(self.engine.oroboros)
        second = BoneAmanita(config=self.test_config)
        self.addCleanup(self._shutdown_engine, second)
        self.assertEqual(second.oroboros.generation_count, 1)
        self.assertIn("Existential Dread", [s.name for s in second.oroboros.scars])
        self.assertEqual([m.trigger for m in second.oroboros.myths], ["lantern"])

    def test_a_death_with_no_store_attached_writes_no_file(self):
        oro = TheOroboros(config_ref=self.test_config)
        self.die(oro)
        self.assertFalse(os.path.exists(TheOroboros.LEGACY_FILE))

    def test_an_old_legacy_file_is_imported_once_and_kept(self):
        import tempfile
        from pathlib import Path

        from engine.gate.store import Store

        with tempfile.TemporaryDirectory() as d:
            legacy = os.path.join(d, "legacy.json")
            with open(legacy, "w", encoding="utf-8") as f:
                json.dump({"generation": 3, "scars": [], "myths": [
                    {"title": "The Legend of Rust", "lesson": "Oil the hinge.", "trigger": "rust"}]}, f)
            store = Store(path=Path(d) / "iris.db", state_dir=d)
            with patch.object(TheOroboros, "LEGACY_FILE", legacy):
                oro = TheOroboros(config_ref=self.test_config)
                oro.attach_store(store)
            self.assertEqual((oro.generation_count, oro.myths[0].trigger), (3, "rust"))
            self.assertEqual(store.record("oroboros.lineage")["generation"], 3)
            self.assertFalse(os.path.exists(legacy))
            self.assertTrue(os.path.exists(legacy + ".imported"))


class TheScarsAreInheritedAgain(BoneTestCase):
    """20.5.0 dropped the apply_legacy call at boot, so scars were saved and loaded but never applied.
    Gordon: restore them. Physics starts fresh each boot, so scars mark it every time; trauma rides in the
    checkpoint, so a generation's scars add to it once."""

    def seed_lineage(self, generation=1, inherited=0):
        self.chronos_patcher.stop()
        self.engine.store.put_record("oroboros.lineage", {
            "generation": generation, "inherited": inherited, "myths": [],
            "scars": [{"name": "Existential Dread", "stat_affected": "trauma_baseline", "value": 4.0, "description": "d"},
                      {"name": "Heavy Burden", "stat_affected": "narrative_drag", "value": 3.0, "description": "d"}],
        })

    def boot(self):
        from main import BoneAmanita

        engine = BoneAmanita(config=self.test_config)
        self.addCleanup(self._shutdown_engine, engine)
        engine.cortex.dspy_critic.enabled = False
        engine.cortex.llm.generate = MagicMock(return_value="A quiet room.")
        real, self.starting_drag = engine.process_turn, []

        def first_turn(*args, **kwargs):
            self.starting_drag.append(float(getattr(engine.active_physics, "narrative_drag", 0.0) or 0.0))
            return real(*args, **kwargs)

        engine.process_turn = first_turn
        engine.events.log = MagicMock(wraps=engine.events.log)
        engine.engage_cold_boot()
        return engine

    def test_a_new_generation_starts_scarred(self):
        self.seed_lineage()
        engine = self.boot()
        self.assertEqual(engine.trauma_accum.get("EXISTENTIAL"), 4.0)
        # The boot turn starts from the scarred packet (a void one holds 0.6).
        self.assertGreaterEqual(self.starting_drag[0], 3.0)
        self.assertEqual(self.engine.store.record("oroboros.lineage")["inherited"], 1)
        scar_lines = [c.args[0] for c in engine.events.log.call_args_list if c.args[1:2] == ("OROBOROS",)]
        self.assertTrue(any("Heavy Burden" in line for line in scar_lines), scar_lines)

    def test_the_trauma_is_added_once_per_generation(self):
        self.seed_lineage()
        first = self.boot()
        first.save_checkpoint()
        second = self.boot()
        self.assertEqual(second.trauma_accum.get("EXISTENTIAL"), 4.0)

    def test_an_already_inherited_generation_adds_no_trauma(self):
        self.seed_lineage(generation=2, inherited=2)
        engine = self.boot()
        self.assertNotIn("EXISTENTIAL", engine.trauma_accum)
