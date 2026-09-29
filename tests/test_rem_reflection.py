"""REM reflection (Gordon, 2026-09-29): what a memory felt like is recorded when it is kept (R1), a sleep
reflects on what was kept (R2), dreams from it (R3), and the dream is shown on waking (R4)."""

from unittest.mock import MagicMock

from engine.constants import Prisma
from engine.gate.feeling import describe, reading
from engine.gate.report import why_report
from tests.base import BoneTestCase

REST = {"DOP": 0.5, "OXY": 0.1, "COR": 0.0, "SER": 0.5, "ADR": 0.0, "MEL": 0.0}


class TheFeeling(BoneTestCase):
    def test_at_rest_it_was_calm_and_with_no_record_nothing(self):
        self.assertEqual(reading(REST), ["calm"])
        self.assertEqual((reading(None), reading({}), describe(None)), ([], [], ""))

    def test_what_stood_out_is_named_strongest_first(self):
        chem = {**REST, "COR": 0.6, "OXY": 0.45}
        self.assertEqual(reading(chem), ["tense", "close"])
        self.assertEqual(describe(chem), "tense, close (OXY 0.45, COR 0.60)")
        self.assertEqual(reading({**REST, "DOP": 0.1, "SER": 0.2}), ["flat", "low"])  # 0.2 past its margin, 0.1 past
        self.assertEqual(reading({**REST, "COR": 0.35, "OXY": 0.9}), ["close", "tense"])

    def test_why_says_how_it_felt(self):
        state = {"self": {"memory": {"sister_name": "Odalys"}}, "world": {}}
        meta = {"sister_name": {"mode": "CONVERSATION", "kept_at": 0.0, "kept_by": "keeper", "receipt_id": "r",
                                "feeling": {**REST, "OXY": 0.5}}}
        lines = why_report("sister_name", state, meta, {}, lambda r: None, now=60.0)
        self.assertIn("  Felt: close (OXY 0.50).", lines)


class KeptWithItsFeeling(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode, self.engine.ui_mode = "TECHNICAL", "WARM"
        self.engine.cortex.llm.generate = MagicMock(
            side_effect=lambda prompt, *a, **k: "sister_name = Odalys" if prompt.startswith("You keep the memory") else "Noted.")

    def test_a_kept_memory_carries_the_endocrine_state(self):
        self.engine.process_turn("My sister is Odalys.")
        feeling = self.engine.store.memory_meta()["sister_name"]["feeling"]
        self.assertEqual(set(feeling), set(REST))
        self.engine.cmd.interface.log = log = MagicMock()
        self.engine.cmd.execute("/memory why sister_name")
        self.assertIn("  Felt: ", Prisma.strip("\n".join(str(c.args[0]) for c in log.call_args_list)))

    def test_a_stand_in_body_records_no_feeling(self):
        self.engine.bio.endo.get_state = MagicMock(return_value="not a state")
        self.engine.process_turn("My sister is Odalys.")
        self.assertIsNone(self.engine.store.memory_meta()["sister_name"]["feeling"])
