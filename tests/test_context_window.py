"""The composer fits the prompt to the context window itself, cutting the least important blocks first.

Left to Ollama, an oversized prompt is cut from the top, which is the system kernel and persona.
ROADMAP A8: the code sweep goes first, then the oldest dialogue; the kernel, persona, rules and the
person's message are never cut, and the receipt says what went.
"""

from unittest.mock import patch

from engine.receipts import ReceiptLedger
from engine.struts import safe_get
from tests.base import BoneTestCase

SWEEP = "CRITICAL STRUCTURAL CONTEXT (Linear Sweep):\n" + "[metabolism.py_L1] x = 1\n" * 300


class PromptFitsTheWindow(BoneTestCase):
    def compose(self, num_ctx: int) -> str:
        composer = self.engine.cortex.composer
        composer.load_template(self.engine.prompt_library["CONVERSATION"])
        history = [f"User: message {i} " + "words " * 60 + f"\nSystem: reply {i}" for i in range(40)]
        state = {
            "meta": {"active_mode": "CONVERSATION"},
            "physics": {"voltage": 10.0},
            "mind": {"role": "The Conversationalist", "style_directives": [SWEEP]},
            "bio": {},
            "dialogue_history": history,
        }
        cortex_cfg = safe_get(composer.cfg, "CORTEX", {})
        window = patch.dict(cortex_cfg, {"NUM_CTX": num_ctx}) if isinstance(cortex_cfg, dict) \
            else patch.object(cortex_cfg, "NUM_CTX", num_ctx)
        ReceiptLedger.get_instance().begin_turn()
        with window:
            return composer.compose(state, "I found one good memory for the toast.")

    def receipt(self):
        return [r for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "composer.compose"][-1]

    def test_a_roomy_window_keeps_everything(self):
        prompt = self.compose(16384)
        self.assertIn("CRITICAL STRUCTURAL CONTEXT", prompt)
        self.assertEqual(self.receipt().inputs["trimmed"], [])

    def test_a_tight_window_cuts_the_sweep_then_the_oldest_dialogue_never_the_kernel(self):
        prompt = self.compose(4096)
        for keep in ("=== SYSTEM KERNEL ===", "computer program", "RESPOND, DO NOT NARRATE",
                     "=== PARTNER INPUT ===", "I found one good memory for the toast.", "reply 39"):
            self.assertIn(keep, prompt)
        self.assertNotIn("CRITICAL STRUCTURAL CONTEXT", prompt)
        self.assertNotIn("reply 30\n", prompt, "the oldest kept dialogue should have gone first")
        trimmed = self.receipt().inputs["trimmed"]
        self.assertEqual(trimmed[0], "code sweep")
        self.assertTrue(any("oldest dialogue" in t for t in trimmed), trimmed)
        self.assertLessEqual(len(prompt) / 2.5, 4096 - 1024)
