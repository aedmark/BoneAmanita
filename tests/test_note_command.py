"""tests/test_note_command.py

The /note command saves the last exchange with the person's own verdict, so the engine is judged by the person it talks to
(D-011) without a panel. notes/ is the person's: reset.sh must leave it alone.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase


class NotesKeepTheLastExchange(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "notes.jsonl"
        patcher = patch.dict(os.environ, {"BONE_NOTES": str(self.path)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.engine.cortex.dialogue_buffer.append("Traveler: I can't stop shaking.\nSystem: That is a lot. I'm here.")
        ReceiptLedger.get_instance().begin_turn()
        ReceiptLedger.get_instance().issue("cortex.holding", "HELD", result_count=1)

    def rows(self):
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines()]

    def test_good_saves_the_exchange_and_its_receipts(self):
        self.engine.cmd.execute("/note good")
        (row,) = self.rows()
        self.assertEqual((row["tag"], row["comment"]), ("good", ""))
        self.assertEqual(row["user"], "I can't stop shaking.")
        self.assertEqual(row["reply"], "That is a lot. I'm here.")
        self.assertIn(["cortex.holding", "HELD"], row["receipts"])

    def test_off_keeps_the_reason(self):
        self.engine.cmd.execute("/note off it told me what to do")
        (row,) = self.rows()
        self.assertEqual((row["tag"], row["comment"]), ("off", "it told me what to do"))

    def test_free_words_are_a_plain_note(self):
        self.engine.cmd.execute("/note I liked the second sentence")
        (row,) = self.rows()
        self.assertEqual((row["tag"], row["comment"]), ("note", "I liked the second sentence"))

    def test_notes_append(self):
        self.engine.cmd.execute("/note good")
        self.engine.cmd.execute("/note off no")
        self.assertEqual([r["tag"] for r in self.rows()], ["good", "off"])

    def test_nothing_to_note_before_anything_was_said(self):
        self.engine.cortex.dialogue_buffer.clear()
        self.engine.cmd.execute("/note good")
        self.assertFalse(self.path.exists())

    def test_an_unwritable_path_is_reported_not_swallowed(self):
        with patch.dict(os.environ, {"BONE_NOTES": "/proc/no/such/dir/notes.jsonl"}):
            with self.assertLogs("bone", level="DEBUG") as seen:
                self.engine.cmd.execute("/note good")
        self.assertTrue(any("Note not saved" in line for line in seen.output))
