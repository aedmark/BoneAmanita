"""A failed checkpoint must leave the previous checkpoint intact."""

import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from protocols.chronos import ChronosKeeper


class AtomicQuicksaveTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.path = self.directory / "quicksave.json"
        self.engine = SimpleNamespace(
            health=100.0, stamina=90.0, trauma_accum={},
            soul=SimpleNamespace(to_dict=lambda: {"name": "test"}),
            village=SimpleNamespace(),
            cortex=SimpleNamespace(dialogue_buffer=["previous dialogue"]),
            events=MagicMock(),
        )
        self.keeper = ChronosKeeper(self.engine)
        self.keeper.SAVE_DIR = str(self.directory)
        self.keeper.save_checkpoint()
        self.previous = self.path.read_bytes()
        self.assertEqual(json.loads(self.previous)["health"], 100.0)
        self.engine.events.reset_mock()
        self.engine.health = 75.0

    def assert_preserved(self):
        self.assertEqual(self.path.read_bytes(), self.previous)
        self.assertEqual(list(self.directory.iterdir()), [self.path])
        self.engine.events.log.assert_called_once()

    def test_partial_write_failure_preserves_previous_checkpoint(self):
        def fail_dump(data, stream, **kwargs):
            stream.write('{"health":')
            raise OSError("disk full")

        with patch("protocols.chronos.json.dump", side_effect=fail_dump):
            self.keeper.save_checkpoint()
        self.assert_preserved()

    def test_serialization_failure_preserves_previous_checkpoint(self):
        circular = []
        circular.append(circular)
        self.keeper.save_checkpoint(circular)
        self.assert_preserved()

    def test_fsync_and_replace_failures_preserve_previous_checkpoint(self):
        for operation in ("fsync", "replace"):
            with self.subTest(operation=operation):
                self.engine.events.reset_mock()
                with patch(f"protocols.chronos.os.{operation}", side_effect=OSError(operation)):
                    self.keeper.save_checkpoint()
                self.assert_preserved()

    def test_failed_first_save_leaves_no_checkpoint_or_temporary_file(self):
        self.path.unlink()
        circular = []
        circular.append(circular)
        self.keeper.save_checkpoint(circular)
        self.assertEqual(list(self.directory.iterdir()), [])
        self.engine.events.log.assert_called_once()

    def test_replace_publishes_complete_flushed_json(self):
        real_replace = os.replace
        real_fsync = os.fsync
        synced = []

        def fsync(fd):
            real_fsync(fd)
            synced.append(fd)

        def replace(source, destination):
            self.assertTrue(synced)
            self.assertEqual(Path(source).parent, self.directory)
            self.assertEqual(self.path.read_bytes(), self.previous)
            self.assertEqual(json.loads(Path(source).read_text())["health"], 75.0)
            real_replace(source, destination)

        with patch("protocols.chronos.os.fsync", side_effect=fsync), patch(
            "protocols.chronos.os.replace", side_effect=replace
        ) as publish:
            self.keeper.save_checkpoint(["new dialogue"])
        publish.assert_called_once()
        saved = json.loads(self.path.read_text())
        self.assertEqual(saved["health"], 75.0)
        self.assertEqual(saved["chat_history"], ["new dialogue"])
        self.assertEqual(list(self.directory.iterdir()), [self.path])
        self.engine.events.log.assert_not_called()
