"""Voltage flavours how the engine speaks; it never replaces the mode's rules or labels the engine's state.

Two things were found on 2026-09-24. Above VOLTAGE_HIGH the composer swapped the conversation's
directives and style guide for a "METABOLIC OVERRIDE PROTOCOL" ("NO CONVERSATION: You are not
talking to anyone... physical... raw, brutal fact"). And below VOLTAGE_LOW, which is where every
conversation runs, the prompt ended "[SYSTEM EXHAUSTED. LOW ENERGY PROSE.]" on 29 of 29 turns.
"""

from tests.base import BoneTestCase

BANNERS = ("SYSTEM EXHAUSTED", "RAW CORTEX STREAM", "VOLTAGE SURGE", "HIGH VOLTAGE DETECTED")
OLD_PROTOCOL = ("You are not talking to anyone", "METABOLIC OVERRIDE", "raw, brutal fact", "bleeding data",
                "INCOMING SHOCKWAVE", "RECENT THOUGHTS", "memory streams strained")


class VoltageKeepsTheConversation(BoneTestCase):
    def compose(self, voltage: float) -> str:
        composer = self.engine.cortex.composer
        composer.load_template(self.engine.prompt_library["CONVERSATION"])
        state = {
            "meta": {"active_mode": "CONVERSATION"},
            "physics": {"voltage": voltage},
            "mind": {"role": "The Conversationalist"},
            "bio": {},
        }
        return composer.compose(state, "I found one good memory for the toast.")

    def test_every_voltage_keeps_the_rules_and_names_no_state(self):
        for voltage in (3.0, 30.0, 90.0):
            prompt = self.compose(voltage)
            self.assertIn("RESPOND, DO NOT NARRATE", prompt, voltage)
            self.assertIn("computer program", prompt, voltage)
            self.assertIn("=== PARTNER INPUT ===", prompt, voltage)
            for banner in BANNERS + OLD_PROTOCOL:
                self.assertNotIn(banner, prompt, (voltage, banner))

    def test_high_voltage_adds_its_overlay_only_when_high(self):
        self.assertNotIn("HIGH VOLTAGE", self.compose(30.0))
        hot = self.compose(90.0)
        self.assertIn("=== HIGH VOLTAGE (adds to the rules above) ===", hot)
        self.assertIn("You are still talking to the same person", hot)
        self.assertLess(hot.index("RESPOND, DO NOT NARRATE"), hot.index("=== HIGH VOLTAGE"))
