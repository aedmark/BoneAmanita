"""The resume point lives in the Halcyon store (roadmap Track E step 3, first migration).

It was saves/quicksave.json, written with a temp file, fsync and rename. A failed save must still
leave the previous checkpoint intact, and an old quicksave.json must not be lost."""

import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from engine.gate.store import Store
from protocols.chronos import ChronosKeeper
from tests.base import BoneTestCase


class QuicksaveInTheStoreTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.store = Store(path=self.directory / "iris.db")
        self.engine = SimpleNamespace(
            health=100.0, stamina=90.0, trauma_accum={},
            soul=SimpleNamespace(to_dict=lambda: {"name": "test"}, load_from_dict=MagicMock()),
            village=SimpleNamespace(),
            cortex=SimpleNamespace(dialogue_buffer=["previous dialogue"]),
            events=MagicMock(),
            embryo=SimpleNamespace(continuity=None),
            store=self.store,
        )
        self.keeper = ChronosKeeper(self.engine)
        self.keeper.SAVE_DIR = str(self.directory)
        self.keeper.save_checkpoint()
        self.engine.events.reset_mock()
        self.engine.health = 75.0

    def saved(self):
        return self.store.checkpoint()["snapshot"]

    def test_the_checkpoint_lives_in_the_store_not_a_file(self):
        self.keeper.save_checkpoint(["new dialogue"])
        self.assertEqual((self.saved()["health"], self.saved()["chat_history"]), (75.0, ["new dialogue"]))
        self.assertFalse((self.directory / "quicksave.json").exists())
        self.engine.events.log.assert_not_called()

    def test_an_unserializable_save_keeps_the_previous_checkpoint(self):
        circular = []
        circular.append(circular)
        self.keeper.save_checkpoint(circular)
        self.assertEqual(self.saved()["health"], 100.0)
        self.engine.events.log.assert_called_once()

    def test_a_write_that_fails_inside_the_transaction_keeps_the_previous_checkpoint(self):
        real_state = Store.state

        def state_then_fail(store, db=None):
            if db is not None:
                db.execute("UPDATE engine_checkpoint SET snapshot_json='{\"health\": 1}'")
                raise OSError("disk full")
            return real_state(store, db)

        with patch.object(Store, "state", state_then_fail):
            self.keeper.save_checkpoint()
        self.assertEqual(self.saved()["health"], 100.0)
        self.engine.events.log.assert_called_once()

    def test_resume_restores_from_the_store(self):
        self.keeper.save_checkpoint(["we were at the mill"])
        self.engine.health = 10.0
        ok, history = self.keeper.resume_checkpoint()
        self.assertTrue(ok)
        self.assertEqual((self.engine.health, history), (75.0, ["we were at the mill"]))

    def test_the_checkpoint_is_tagged_with_the_canonical_sequence(self):
        from engine.gate.kernel import Boundary, Gate
        from engine.gate.tools import TOOLS, build_invariants
        import yaml

        spec = yaml.safe_load(open("engine/gate/boundary.yaml"))
        seq, state = self.store.state()
        gate = Gate(Boundary(spec), state, TOOLS, build_invariants(spec))
        receipt = gate.adjudicate("Noted.\nNOMINATE what=self/memory/mill verb=remember args=key:mill; value:by the river")
        self.store.commit_cycle("t", gate.state, seq, receipt, "raw")
        self.keeper.save_checkpoint()
        self.assertEqual(self.store.checkpoint()["state_sequence"], 1)


class LegacyQuicksaveImport(unittest.TestCase):
    def test_an_old_quicksave_is_imported_once_and_kept(self):
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            legacy = directory / "quicksave.json"
            legacy.write_text(json.dumps({"health": 42.0, "chat_history": ["from before"]}))
            engine = SimpleNamespace(
                health=100.0, stamina=100.0, trauma_accum={}, events=MagicMock(),
                embryo=SimpleNamespace(continuity=None),
                store=Store(path=directory / "iris.db"),
            )
            keeper = ChronosKeeper(engine)
            keeper.SAVE_DIR = str(directory)
            ok, history = keeper.resume_checkpoint()
            self.assertEqual((ok, engine.health, history), (True, 42.0, ["from before"]))
            self.assertFalse(legacy.exists())
            self.assertTrue((directory / "quicksave.json.imported").exists())
            self.assertEqual(engine.store.checkpoint()["snapshot"]["health"], 42.0)
            engine.health = 0.0
            self.assertEqual(keeper.resume_checkpoint()[0], True)
            self.assertEqual(engine.health, 42.0)
            self.assertEqual(sorted(os.listdir(directory)).count("quicksave.json"), 0)

    def test_a_quicksave_that_holds_the_deque_as_text_still_resumes_its_dialogue(self):
        # default=str saved the dialogue deque as its repr, and resume then read it character by character.
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            text = str(__import__("collections").deque(["Traveler: hi\nSystem: hello"], maxlen=15))
            (directory / "quicksave.json").write_text(json.dumps({"health": 50.0, "chat_history": text}))
            engine = SimpleNamespace(
                health=100.0, stamina=100.0, trauma_accum={}, events=MagicMock(),
                embryo=SimpleNamespace(continuity=None),
                store=Store(path=directory / "iris.db"),
            )
            keeper = ChronosKeeper(engine)
            keeper.SAVE_DIR = str(directory)
            self.assertEqual(keeper.resume_checkpoint(), (True, ["Traveler: hi\nSystem: hello"]))


class AnEngineResumesFromItsStore(BoneTestCase):
    """End to end: a real turn checkpoints into the engine's store, and a new engine on it resumes."""

    def test_a_turn_is_resumed_by_the_next_engine(self):
        from main import BoneAmanita

        self.chronos_patcher.stop()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value="The kettle is on.")
        self.engine.process_turn("Put the kettle on.")
        self.engine.health = 64.0
        self.engine.save_checkpoint()
        self.assertFalse(os.path.exists(os.path.join("saves", "quicksave.json")))
        self.assertIsInstance(self.engine.store.checkpoint()["snapshot"]["chat_history"], list)

        second = BoneAmanita(config=self.test_config)
        self.addCleanup(self._shutdown_engine, second)
        with patch.object(second.cortex, "restore_context") as restore:
            second.engage_cold_boot()
        self.assertEqual(second.health, 64.0)
        restored = restore.call_args[0][0]
        self.assertTrue(any("The kettle is on." in line for line in restored), restored)


class TheAdventureLivesInTheCheckpoint(BoneTestCase):
    """Roadmap step 3b: rooms and items were fractal_adventure.json, rewritten in the repo root every turn.
    They are part of the checkpoint now; the FractalOS file is written only on /export (Gordon's call)."""

    MILL = {"id": "the_mill", "name": "The Mill", "description": "Dust and a stopped wheel.", "exits": ["north"], "pois": []}

    def setUp(self):
        super().setUp()
        self.chronos_patcher.stop()
        self.engine.cortex.visited_rooms = {"the_mill": dict(self.MILL)}
        self.engine.cortex.current_room_name = "The Mill"

    def test_the_rooms_are_saved_with_the_checkpoint_and_no_file_is_written(self):
        self.engine.save_checkpoint()
        adventure = self.engine.store.checkpoint()["snapshot"]["adventure"]
        self.assertEqual(adventure["startingRoomId"], "the_mill")
        self.assertEqual(adventure["rooms"]["the_mill"]["description"], "Dust and a stopped wheel.")
        for path in ("fractal_adventure.json", os.path.join("saves", "fractal_adventure.json")):
            self.assertFalse(os.path.exists(path), path)

    def test_a_resumed_engine_is_back_in_its_room(self):
        from main import BoneAmanita

        self.engine.save_checkpoint()
        second = BoneAmanita(config=self.test_config)
        self.addCleanup(self._shutdown_engine, second)
        second.engage_cold_boot()
        self.assertEqual(second.cortex.current_room_name, "The Mill")
        self.assertEqual(second.cortex.visited_rooms["the_mill"]["exits"], ["north"])

    def test_an_old_fractal_file_is_imported_once_and_kept(self):
        with tempfile.TemporaryDirectory() as d:
            legacy = os.path.join(d, "fractal_adventure.json")
            with open(legacy, "w", encoding="utf-8") as f:
                json.dump({"startingRoomId": "the_mill", "rooms": {"the_mill": self.MILL}}, f)
            self.engine.cortex.visited_rooms = {}
            self.engine.cortex.current_room_name = ""
            self.engine.chronos.resumed_adventure = None
            with patch.object(type(self.engine), "LEGACY_ADVENTURE_FILE", legacy):
                self.engine._load_fractal_state()
            self.assertEqual(self.engine.cortex.current_room_name, "The Mill")
            self.assertFalse(os.path.exists(legacy))
            self.assertTrue(os.path.exists(legacy + ".imported"))

    def test_export_writes_a_fractalos_adventure_on_demand(self):
        self.engine.cmd.interface.log = MagicMock()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "mill.json")
            self.engine.cmd.execute(f"/export {path}")
            with open(path, encoding="utf-8") as f:
                exported = json.load(f)
        self.assertEqual(exported["startingRoomId"], "the_mill")
        self.assertIn("the_mill", exported["rooms"])
        self.assertIn("items", exported)
        self.assertIn(path, str(self.engine.cmd.interface.log.call_args))


if __name__ == "__main__":
    unittest.main()
