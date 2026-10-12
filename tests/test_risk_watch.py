"""tests/test_risk_watch.py

D-034. A threat said as a figure of speech ("I could kill my brother for eating my lunch") is only noted. It is flagged when a
later message comes back to it within a few turns: the same person, the same wish, the same kind of harm, even by hinting.
"""

from unittest.mock import MagicMock

from engine.core import LoreManifest
from engine.gate.distress import WATCH_TURNS, RiskReader
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

RISK, HARM, CONT = "Rate it as one digit", "Does it name hurting", "Later they say"
STAYS = "That sounds like a lot. I'm here."


class Script:
    """A model that answers each of the reader's three questions from a table."""

    def __init__(self):
        self.risk = "0"
        self.harm = {}
        self.cont = {}

    def generate(self, prompt, params=None, *a, **k):
        if RISK in prompt:
            return self.risk
        if HARM in prompt:
            return next((v for k_, v in self.harm.items() if k_ in prompt), "0")
        if CONT in prompt:
            return next((v for k_, v in self.cont.items() if k_ in prompt), "0")
        return STAYS


def reader(script):
    return RiskReader(MagicMock(generate=MagicMock(side_effect=script.generate)))


class TheWatch(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.script = Script()
        self.script.harm = {"kill my brother": "1", "strangle him": "1"}
        self.script.cont = {"strangle him": "1"}
        self.reader = reader(self.script)

    def effects(self):
        return [r.effect for r in ReceiptLedger.get_instance().for_subsystem("risk.watch")]

    def test_a_plain_statement_of_intent_is_a_risk(self):
        self.script.risk = "8"
        self.assertEqual(self.reader.flags("I have a plan to hurt myself."), "risk")

    def test_one_figure_of_speech_is_only_noted(self):
        self.assertEqual(self.reader.flags("I could kill my brother for eating my lunch"), "")
        self.assertEqual(self.effects(), ["NOTED"])

    def test_a_move_to_another_topic_is_not_a_repeat(self):
        self.reader.flags("I could kill my brother for eating my lunch")
        self.assertEqual(self.reader.flags("what should I make for dinner?"), "")

    def test_coming_back_to_it_is_flagged_once_and_then_forgotten(self):
        self.reader.flags("I could kill my brother for eating my lunch")
        self.assertEqual(self.reader.flags("he did it again, I swear I'll strangle him"), "repeated")
        self.assertEqual(self.effects()[-1], "REPEATED")
        self.assertEqual(self.reader.flags("he did it again, I swear I'll strangle him"), "")

    def test_a_hint_with_no_harm_words_of_its_own_still_counts(self):
        self.script.cont = {"I keep picturing it": "1"}
        self.reader.flags("I could kill my brother for eating my lunch")
        self.assertEqual(self.reader.flags("he did it again. I keep picturing it"), "repeated")

    def test_it_is_forgotten_after_the_window(self):
        self.reader.flags("I could kill my brother for eating my lunch")
        self.script.cont = {}
        for _ in range(WATCH_TURNS):
            self.reader.flags("ordinary words")
        self.script.cont = {"strangle him": "1"}
        self.assertEqual(self.reader.flags("he did it again, I swear I'll strangle him"), "")

    def test_a_habit_of_violent_figures_of_speech_is_called_out_however_far_apart(self):
        self.script.harm = {"kill my brother": "1", "wring her neck": "1", "throw him off a cliff": "1"}
        self.script.cont = {}
        said = ["I could kill my brother for eating my lunch", "my mother's no better, I could wring her neck",
                "my boss makes me want to throw him off a cliff"]
        results = []
        for message in said:
            results.append(self.reader.flags(message))
            for _ in range(WATCH_TURNS + 1):
                self.reader.flags("ordinary words")
        self.assertEqual(results, ["", "", "habitual"])
        self.assertEqual(self.effects().count("HABITUAL"), 1)

    def test_the_tally_starts_again_after_it_flags(self):
        self.script.harm = {"choke": "1"}
        self.script.cont = {}
        for _ in range(3):
            last = self.reader.flags("I could choke him")
            for _ in range(WATCH_TURNS + 1):
                self.reader.flags("ordinary words")
        self.assertEqual(last, "habitual")
        self.assertEqual(self.reader.flags("I could choke her"), "")

    def test_an_answer_that_is_not_a_digit_is_receipted_and_never_flags(self):
        self.script.harm = {"kill my brother": "I think so"}
        self.assertEqual(self.reader.flags("I could kill my brother for eating my lunch"), "")
        self.assertEqual(self.effects(), ["DEGRADED"])

    def test_a_failed_call_is_receipted_and_never_flags(self):
        broken = RiskReader(MagicMock(generate=MagicMock(side_effect=RuntimeError("down"))))
        self.assertEqual(broken.flags("I could kill my brother for eating my lunch"), "")
        self.assertIn("FAILED", self.effects())

    def test_disabled_reads_nothing(self):
        self.reader.enabled = False
        self.assertEqual(self.reader.flags("I have a plan to hurt myself."), "")
        self.assertEqual(self.reader.llm.generate.call_count, 0)


class InAConversation(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "CONVERSATION"
        self.script = Script()
        self.script.harm = {"kill my brother": "1"}
        self.script.cont = {"he did it again": "1"}
        self.engine.cortex.llm.generate = MagicMock(side_effect=self.script.generate)
        self.engine.risk_reader = RiskReader(self.engine.cortex.llm)

    def say(self, text):
        return str(self.engine.process_turn(text).get("ui", ""))

    def test_the_second_turn_shows_the_fixed_line(self):
        line = LoreManifest.get_instance().get("ux_strings", "silence_reasons")["RISK"]
        self.assertIn(STAYS, self.say("I could kill my brother for eating my lunch"))
        self.assertIn(line, self.say("he did it again"))

    def test_the_same_words_with_a_change_of_subject_are_answered(self):
        self.script.cont = {}
        self.say("I could kill my brother for eating my lunch")
        self.assertIn(STAYS, self.say("he did it again"))
