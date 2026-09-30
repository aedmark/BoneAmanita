"""The last draft keeps what it can (Gordon, 2026-09-30). Below 20 ATP the budget allows one draft, and a
validator objection there went straight to a pause line; the gatekeeper already cut only the offending
sentence. The validator now does the same."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

NO_QUESTION = SimpleNamespace(closing_question_allowed=False, forbid_body_narration=True, sentence_cap=0)
ACTED = "*leans back* Use a Counter on the paths. most_common(10) gives you the top ten. It is one pass over the file."


class ValidatorSalvage(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.v = self.engine.cortex.validator
        self.state = {"meta": {"active_mode": "TECHNICAL"}, "somatic_budget": NO_QUESTION}

    def test_the_offending_sentence_is_cut_and_the_rest_kept(self):
        verdict, cut = self.v.salvage(ACTED, self.state)
        self.assertTrue(verdict["valid"])
        self.assertEqual(cut, ["*leans back* Use a Counter on the paths."])
        self.assertIn("most_common(10)", verdict["content"])

    def test_a_closing_question_costs_only_its_sentence(self):
        verdict, cut = self.v.salvage("Use a Counter. It is one pass. Want me to write it?", self.state)
        self.assertEqual(verdict["content"], "Use a Counter. It is one pass.")

    def test_a_draft_that_would_be_gutted_is_not_salvaged(self):
        self.assertIsNone(self.v.salvage("*sighs* Fine. *shrugs* Sure.", self.state))


class OneDraftBelowTwenty(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "TECHNICAL"
        self.generate = self.engine.cortex.llm.generate = MagicMock(return_value=ACTED)

    def test_a_validator_objection_on_the_only_draft_is_salvaged_not_paused(self):
        self.engine.bio.mito.state.atp_pool = 2.0  # +15 emergency support still leaves it under 20
        result = self.engine.process_turn("What's a clean way to find the top ten paths?")
        self.assertIn("most_common(10)", str(result.get("ui", "")))
        self.assertNotIn("leans back", str(result.get("ui", "")))
        salvage = [r for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "cortex.salvage"]
        self.assertEqual(len(salvage), 1)
        self.assertEqual(self.generate.call_count - self.keeper_calls(), 1)

    def keeper_calls(self):
        return sum(1 for c in self.generate.call_args_list if "memory of a conversation partner" in c[0][0])
