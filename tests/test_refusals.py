"""Refusals the model hears (from bone-iris's imagination loop, which feeds the rejection back): when the
gate refuses a nomination, the next prompt says what and why, once, and a halcyon.refusal receipt says it
was handed back. The person sees the reason in TECHNICAL or on the DEEP HUD."""

from unittest.mock import MagicMock, patch

from engine.gate.report import refusal
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

KEY = "sk-proj-abcdEFGH1234ijklMNOP5678"
PROSE = "The river runs east past the mill."


class TheNote(BoneTestCase):
    def test_nothing_refused_is_no_note(self):
        for decision in ("ACCEPT", "NOOP"):
            self.assertIsNone(refusal({"decision": decision, "decision_basis": [["schema", "PASS", "ok"]]}, "", "model"))

    def test_a_failed_effect_is_a_refusal_too(self):
        receipt = {"decision": "ACCEPT", "decision_basis": [["execute", "ERROR", "KeyError: 'x'"]]}
        text = f"{PROSE}\nNOMINATE what=world/node/x verb=create args=type:city; name:x"
        self.assertEqual(refusal(receipt, text, "model"),
                         {"verb": "create", "what": "world/node/x", "why": "KeyError: 'x'", "by": "model", "confidential": False})


class TheModelHearsWhy(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "CONVERSATION"
        self.prompts, self.keeps, self.reply = [], "NONE", "Noted."

        def generate(prompt, *a, **k):
            if prompt.startswith("You keep the memory"):
                return self.keeps
            self.prompts.append(prompt)
            return self.reply

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)

    def turn(self, message, keeps="NONE", reply="Noted."):
        self.keeps, self.reply = keeps, reply
        self.engine.process_turn(message)
        return self.prompts[-1]

    def test_the_keepers_refusal_reaches_the_next_prompt_once(self):
        self.turn(f"My key is {KEY}", keeps=f"openai_api_key = {KEY}")
        prompt = self.turn("Did you save it?")
        self.assertIn("Last turn the memory keeper asked the gate to keep self/memory/openai_api_key, and the gate "
                      "refused: no_secrets -- the memory is named as a credential; confidential things are never kept. Nothing "
                      "was kept. Only that was refused; what they tell you about themselves is still kept.", prompt)
        self.assertNotIn(KEY, prompt.split("=== HALCYON GATE GOVERNANCE ===", 1)[1])
        handed = ReceiptLedger.get_instance().for_subsystem("halcyon.refusal")
        self.assertEqual([(r.effect, r.inputs["by"]) for r in handed], [("HANDED_BACK", "keeper")])
        self.assertNotIn("Last turn", self.turn("Anyway."))

    def test_the_models_own_refusal_says_to_fix_it_only_if_it_matters(self):
        self.turn("Who are you?", reply=f"{PROSE}\nNOMINATE what=self/identity verb=remember args=key:name; value:Iris")
        prompt = self.turn("Go on.")
        self.assertNotIn("Only that was refused", prompt)
        self.assertIn("Last turn your NOMINATE line (remember self/identity) was refused: 'self/identity' is outside "
                      "the declared state scope. Nothing was kept. Nominate it again, fixed, only if it still matters.", prompt)

    def test_a_kept_memory_leaves_no_note(self):
        self.turn("My sister is Odalys.", keeps="sister_name = Odalys")
        self.assertNotIn("Last turn", self.turn("Go on."))
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("halcyon.refusal"), [])

    def test_the_story_is_told_where_its_memories_go(self):
        self.assertNotIn("self/memory/story.", self.turn("Hello."))
        self.engine.cortex.active_mode = "ADVENTURE"
        self.assertIn("keep what it establishes under self/memory/story.<name>", self.turn("Look around."))

    def test_a_reason_that_quotes_the_nomination_withholds_its_secret(self):
        # A malformed arg is quoted back verbatim in the gate's reason.
        self.turn("Store it.", reply=f"{PROSE}\nNOMINATE what=self/memory/openai verb=remember args={KEY}")
        self.assertIn("malformed arg '[withheld: an API key]', expected key:value", self.turn("Go on."))

    def test_the_note_is_handed_back_once_even_when_the_gate_sits_a_turn_out(self):
        self.turn(f"My key is {KEY}", keeps=f"openai_api_key = {KEY}")
        with patch("engine.gate.kernel.Gate.adjudicate", side_effect=RuntimeError("down")):  # a turn the gate misses
            self.assertIn("Last turn the memory keeper", self.turn("Did you save it?"))
        self.assertNotIn("Last turn", self.turn("Anyway."))

    def test_the_gate_block_says_what_is_personal_and_what_is_confidential(self):
        prompt = self.turn("Hello.")
        self.assertIn("Personal things (names, family, health, preferences, their life and work) are kept", prompt)
        self.assertIn("Confidential things (passwords, keys, tokens, card, bank and ID numbers) are never kept", prompt)
