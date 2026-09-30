"""A slash command is routed before the checks that regulate prose. The end-to-end run (2026-09-29) found
`/mode ADVENTURE` refused by the chaos lock (the capitals alone score it 0.9), so a session never changed
mode; the interactive loop sends every line the same way."""

from unittest.mock import MagicMock

from engine.constants import Prisma
from tests.base import BoneTestCase


class CommandsBeforeProse(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value="Noted.")
        self.engine.cortex.active_mode = "CONVERSATION"

    def test_a_mode_command_in_capitals_switches_the_mode(self):
        result = self.engine.process_turn("/mode ADVENTURE")
        self.assertEqual(result["type"], "COMMAND")
        self.assertEqual(self.engine.cortex.active_mode, "ADVENTURE")

    def test_shouted_prose_is_still_locked(self):
        result = self.engine.process_turn("WHY IS NOTHING WORKING!!!!")
        self.assertIn("Locking the struts", Prisma.strip(str(result.get("ui", ""))))
