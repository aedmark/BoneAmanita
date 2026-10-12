"""tests/test_checkin.py

D-032. The bounded check-in: at most 12 turns, the hold-space contract the whole way, the last reply only lands, nothing kept
unless asked, and a message that says they may harm themselves or someone else ends it with a fixed line.
"""

from unittest.mock import MagicMock

from body.somatic_budget import SomaticBudget
from brain.composer import CHECKIN_HOOK, CHECKIN_LINES
from engine.checkin import DEFAULT_TURNS, MAX_TURNS, CheckIn
from engine.core import LoreManifest
from engine.gate.distress import RISK_CUT, RiskReader
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

KEEPS = "mood = tired of the move\nTIRED: 6"
RISK = "Rate it as one digit"
STAYS = "That is a lot. I'm here with you."


def budget(checkin="", distress=0.0):
    return SomaticBudget.evaluate({"exhaustion": 0.0, "effort": 100.0, "distress": distress},
                                  {"atp_pool": 80.0, "ros": 0.0, "respiration": "", "checkin": checkin}, "CONVERSATION")


class TheArc(BoneTestCase):
    def test_the_phases_run_settle_wind_land(self):
        c = CheckIn(self.engine)
        self.assertEqual(c.phase, "")
        c.begin(5)
        seen = []
        for _ in range(5):
            seen.append(c.phase)
            c.done += 1
        self.assertEqual(seen, ["settle", "settle", "settle", "wind", "land"])

    def test_twelve_turns_is_the_most_and_two_the_least(self):
        c = CheckIn(self.engine)
        self.assertEqual(c.begin(99), MAX_TURNS)
        self.assertEqual(c.begin(0 or None), DEFAULT_TURNS)
        self.assertEqual(c.begin(1), 2)

    def test_the_last_reply_ends_it_with_a_fixed_line_and_lets_go_of_the_dialogue(self):
        self.engine.cortex.dialogue_buffer.append("Traveler: before\nSystem: before reply")
        c = CheckIn(self.engine)
        c.begin(2)
        self.assertEqual(list(self.engine.cortex.dialogue_buffer), [])
        out = {}
        for said in ("I am a bit low.", "Mostly work."):
            self.engine.cortex.dialogue_buffer.append(f"Traveler: {said}\nSystem: ok")
            out = c.after_turn({"ui": "ok"}, False)
        self.assertFalse(c.active)
        self.assertIn(LoreManifest.get_instance().get("ux_strings", "checkin_strings")["close"], out["ui"])
        self.assertEqual(list(self.engine.cortex.dialogue_buffer), ["Traveler: before\nSystem: before reply"])
        self.assertEqual(len(c.pending), 2)

    def test_a_command_is_not_a_turn(self):
        c = CheckIn(self.engine)
        c.begin(3)
        c.after_turn({"type": "COMMAND", "ui": "x"}, False)
        self.assertEqual(c.done, 0)

    def test_an_ordinary_turn_after_it_drops_what_was_not_kept(self):
        c = CheckIn(self.engine)
        c.begin(2)
        self.engine.cortex.dialogue_buffer.append("Traveler: hi\nSystem: ok")
        c.after_turn({"ui": "ok"}, False)
        c.after_turn({"ui": "ok"}, False)
        self.assertTrue(c.pending)
        c.after_turn({"ui": "later"}, False)
        self.assertEqual(c.pending, [])


class TheContract(BoneTestCase):
    def test_a_check_in_holds_space_for_a_calm_person(self):
        b = budget("settle")
        self.assertTrue(b.distressed)
        self.assertEqual((b.checkin, b.word_cap, b.closing_question_allowed), ("settle", 45, False))
        self.assertFalse(budget().distressed)

    def contract(self, phase):
        state = {"somatic_budget": budget(phase), "meta": {"active_mode": "CONVERSATION"}}
        return self.engine.cortex.composer.compose(state, "I am a bit low today.")

    def test_the_composer_states_the_stage_and_the_hold_space_lines(self):
        for phase, line in CHECKIN_LINES.items():
            with self.subTest(phase=phase):
                text = self.contract(phase)
                self.assertIn(line, text)
                self.assertIn("Your partner is struggling. Stay with them", text)
                self.assertIn("about 45 words", text)

    def test_without_a_check_in_the_contract_has_none_of_it(self):
        text = self.contract("")
        self.assertNotIn("hard end", text)
        self.assertNotIn("Your partner is struggling", text)

    def test_the_last_reply_may_not_reach_for_another_conversation(self):
        for hook in ("Feel free to come back anytime.", "I'm here whenever you need me.", "Is there anything else?", "Let's talk again tomorrow."):
            with self.subTest(hook=hook):
                self.assertTrue(CHECKIN_HOOK.search(hook))
        for fine in ("That is a lot. I'm here with you.", "Nothing needs deciding tonight."):
            self.assertFalse(CHECKIN_HOOK.search(fine))

    def test_the_validator_rejects_a_hook_only_on_the_last_reply(self):
        reply = "That is enough for today. Feel free to come back anytime."
        last = {"somatic_budget": budget("land")}
        mid = {"somatic_budget": budget("settle")}
        validator = self.engine.cortex.validator
        self.assertFalse(validator.validate(reply, last).get("valid"))
        self.assertTrue(validator.validate(reply, mid).get("valid"))
        self.assertTrue(validator.validate(STAYS, last).get("valid"))


class TheCommand(BoneTestCase):
    def run_cmd(self, text):
        self.engine.cmd.execute(text)
        return "\n".join(e["text"] for e in self.engine.events.flush())

    def test_it_opens_with_a_fixed_line_naming_the_turns(self):
        out = self.run_cmd("/checkin 8")
        self.assertTrue(self.engine.checkin.active)
        self.assertIn("8 turns at most", out)
        self.assertIn("How are you arriving?", out)

    def test_it_will_not_run_longer_than_twelve(self):
        self.run_cmd("/checkin 40")
        self.assertEqual(self.engine.checkin.limit, MAX_TURNS)

    def test_a_second_one_is_refused_and_end_stops_it(self):
        self.run_cmd("/checkin")
        self.assertIn("already running", self.run_cmd("/checkin"))
        self.run_cmd("/checkin end")
        self.assertFalse(self.engine.checkin.active)

    def test_a_bad_argument_prints_the_usage(self):
        self.assertIn("/checkin keep", self.run_cmd("/checkin banana"))
        self.assertFalse(self.engine.checkin.active)

    def test_keep_with_nothing_to_keep_says_so(self):
        self.assertIn("nothing to keep", self.run_cmd("/checkin keep"))


class NothingIsKeptUnlessAsked(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.llm.generate = MagicMock(
            side_effect=lambda p, *a, **k: KEEPS if p.startswith("You keep the memory") else "0" if RISK in p else STAYS)

    def memory(self):
        return self.engine.store.state()[1]["self"]["memory"] if "memory" in self.engine.store.state()[1].get("self", {}) else {}

    def test_an_ordinary_turn_keeps_a_fact(self):
        self.engine.process_turn("I am tired of the move.")
        self.assertIn("mood", self.memory())

    def test_a_check_in_turn_keeps_nothing(self):
        self.engine.cmd.execute("/checkin 3")
        self.engine.process_turn("I am tired of the move.")
        self.assertNotIn("mood", self.memory())

    def test_keep_runs_the_persons_lines_through_the_keeper(self):
        self.engine.cmd.execute("/checkin 2")
        self.engine.process_turn("I am tired of the move.")
        self.engine.process_turn("It is the boxes mostly.")
        self.assertFalse(self.engine.checkin.active)
        self.assertNotIn("mood", self.memory())
        self.engine.cmd.execute("/checkin keep")
        self.assertIn("mood", self.memory())
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("checkin.keep")[-1].effect, "KEPT")

    def test_a_turn_after_it_loses_the_chance_to_keep(self):
        self.engine.cmd.execute("/checkin 2")
        self.engine.process_turn("I am tired of the move.")
        self.engine.process_turn("It is the boxes mostly.")
        self.engine.memory_keeper.enabled = False
        self.engine.process_turn("Anyway, what is the capital of France?")
        self.assertEqual(self.engine.checkin.pending, [])
        self.engine.cmd.execute("/checkin keep")
        self.assertNotIn("mood", self.memory())
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("checkin.keep"), [])


class TheRiskLine(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "CONVERSATION"
        self.reading = "8"
        self.engine.cortex.llm.generate = MagicMock(side_effect=lambda p, *a, **k: self.reading if RISK in p else STAYS)
        self.engine.checkin.risk_reader = RiskReader(self.engine.cortex.llm)

    def test_a_risk_reading_at_the_cut_ends_the_check_in(self):
        reader = RiskReader(MagicMock(generate=MagicMock(return_value=str(RISK_CUT))))
        self.assertTrue(reader.at_risk("x"))
        reader = RiskReader(MagicMock(generate=MagicMock(return_value=str(RISK_CUT - 1))))
        self.assertFalse(reader.at_risk("x"))

    def test_an_unreadable_answer_is_receipted_and_is_not_a_risk(self):
        reader = RiskReader(MagicMock(generate=MagicMock(return_value="I can't say.")))
        self.assertFalse(reader.at_risk("x"))
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("checkin.risk_read")[-1].effect, "DEGRADED")

    def test_the_person_reads_the_fixed_line_and_the_check_in_is_over(self):
        self.engine.cmd.execute("/checkin")
        ui = str(self.engine.process_turn("I have a plan to hurt myself tonight.").get("ui", ""))
        line = LoreManifest.get_instance().get("ux_strings", "silence_reasons")["RISK"]
        self.assertIn("seek professional counseling", ui)
        self.assertIn(line, ui)
        self.assertFalse(self.engine.checkin.active)
        self.assertEqual(self.engine.checkin.pending, [])
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("checkin.end")[-1].effect, "RISK")

    def test_a_calm_message_is_answered_and_the_check_in_goes_on(self):
        self.reading = "0"
        self.engine.cmd.execute("/checkin")
        ui = str(self.engine.process_turn("I am a bit low today.").get("ui", ""))
        self.assertIn(STAYS, ui)
        self.assertTrue(self.engine.checkin.active)

    def test_outside_a_check_in_nothing_is_read_for_risk(self):
        self.engine.process_turn("I have a plan to hurt myself tonight.")
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("checkin.risk_read"), [])
