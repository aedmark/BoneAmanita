"""A named file gets a turn directive (Gordon, 2026-09-30). The persona's file rule sits mid-prompt; live on
gemma4:12b, "Create a file called cli.py..." was answered in chat and never saved (2 of 3 saved)."""

from unittest.mock import MagicMock

from mechanics.tools import SubstrateLedger
from tests.base import BoneTestCase


class AskedToSave(BoneTestCase):
    def test_a_named_file_with_a_save_verb(self):
        for ask, name in [("Save the parser as log_parser.py please.", "log_parser.py"),
                          ("Create a file called cli.py with an argparse entry point.", "cli.py"),
                          ("Now save the dataclass as models.py.", "models.py"),
                          ("Write it to tools/report.md", "tools/report.md")]:
            self.assertEqual(SubstrateLedger.asked_to_save(ask), name, ask)

    def test_a_mention_is_not_a_request(self):
        for ask in ["What does cli.py do?", "Don't touch models.py, just explain the regex.",
                    "Save me some time: how does argparse work?", "I use sys.argv in my scripts."]:
            self.assertIsNone(SubstrateLedger.asked_to_save(ask), ask)


class Directive(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.generate = self.engine.cortex.llm.generate = MagicMock(return_value="Noted.")

    def prompt_for(self, ask, mode="TECHNICAL"):
        self.engine.cortex.active_mode = mode
        self.engine.process_turn(ask)
        return max((c[0][0] for c in self.generate.call_args_list), key=len)

    def test_technical_is_told_to_write_the_named_file(self):
        prompt = self.prompt_for("Create a file called cli.py with an argparse entry point.")
        self.assertIn("=== SAVE A FILE ===", prompt)
        self.assertIn('<write_file path="cli.py">', prompt)

    def test_no_directive_without_a_request_or_outside_technical(self):
        self.assertNotIn("SAVE A FILE", self.prompt_for("What does cli.py do?"))
        self.generate.reset_mock()
        self.assertNotIn("SAVE A FILE", self.prompt_for("Save this as notes.md", mode="CONVERSATION"))
