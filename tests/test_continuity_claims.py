"""Fresh session (2026-10-05): a follow-up opened "I have been thinking about what you mentioned before regarding
Pepper." Nothing had run between the sessions. BoneAmanita turns a memory over between turns only in REM, as a
reflection recorded with the memories it drew on; the prompt now says which, and the gatekeeper cuts the claim
(UNBACKED_CONTINUITY) unless a reflection grounds it this turn (Gordon: ground it, with the pattern as backstop)."""

import copy
from types import SimpleNamespace
from unittest.mock import MagicMock

from brain.composer import PromptComposer
from tests.base import BoneTestCase

CLAIM = "I have been thinking about what you mentioned before regarding Pepper."
CONSIDERING = "thinking about taking her back to the shelter"


class Remembered(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False

    def commit(self, line):
        from engine.gate.kernel import Gate

        store = self.engine.store
        seq, state = store.state()
        gate = Gate(self.engine.boundary, copy.deepcopy(state), self.engine.gate_tools, self.engine.gate_invariants)
        store.commit_cycle("t", gate.state, seq, gate.adjudicate(f"Noted.\n{line}"), line, user_text="x", display="Noted.")

    def keep(self):
        self.commit(f"NOMINATE what=self/memory/decision_on_pepper verb=remember args=key:decision_on_pepper; value:{CONSIDERING}")

    def reflect(self):
        self.commit("NOMINATE what=self/memory/reflection.pepper verb=reflect args=key:reflection.pepper; "
                    "value:they are weighing whether they can give Pepper what she needs; from:decision_on_pepper")

    def recall(self):
        return self.engine.cortex._halcyon_recall(
            SimpleNamespace(halcyon_state=self.engine.store.state()[1], somatic_budget=None), "Pepper is by the door.")

    def reply(self, text):
        self.engine.cortex.llm.generate = MagicMock(return_value=text)
        return str(self.engine.process_turn("Pepper's been sleeping by the door lately.").get("ui", ""))

    def test_a_memory_no_reflection_drew_on_is_only_remembered(self):
        self.keep()
        found = self.recall()
        self.assertEqual(found["reflected"], {})
        block = PromptComposer._recall_block(found)
        self.assertIn("you have not been thinking about them in between", block)
        self.assertNotIn("you reflected on this", block)

    def test_a_reflection_after_it_was_kept_is_said(self):
        self.keep()
        self.reflect()
        found = self.recall()
        self.assertIn("decision_on_pepper", found["reflected"])
        self.assertIn(f"- decision_on_pepper: {CONSIDERING} (open) (you reflected on this on",
                      PromptComposer._recall_block(found))

    def test_a_reflection_on_what_it_used_to_hold_does_not_count(self):
        self.keep()
        self.reflect()
        self.commit("NOMINATE what=self/memory/decision_on_pepper verb=remember args=key:decision_on_pepper; "
                    "value:didn't send the return form, called the shelter instead")
        self.assertEqual(self.recall()["reflected"], {})

    def test_the_follow_up_says_how_it_is_held(self):
        ask = {"key": "decision_on_pepper", "value": CONSIDERING, "kept_at": 1791000000.0, "earlier": True}
        self.assertIn("You remember it; you have not been thinking about it since.",
                      PromptComposer._ask_block({"ask": ask}))
        ask["reflected"] = (1791090000.0, "they are weighing what Pepper needs")
        self.assertIn('while they were away: "they are weighing what Pepper needs"', PromptComposer._ask_block({"ask": ask}))

    def test_the_claim_is_cut_when_nothing_grounds_it(self):
        self.keep()
        ui = self.reply(f"{CLAIM} She may like the draft by the door. Dogs pick spots like that.")
        self.assertNotIn("I have been thinking about", ui)
        self.assertIn("Dogs pick spots like that", ui)

    def test_it_stands_when_a_reflection_grounds_it(self):
        self.keep()
        self.reflect()
        ui = self.reply(f"{CLAIM} She may like the draft by the door. Dogs pick spots like that.")
        self.assertIn("I have been thinking about", ui)


class ThePattern(BoneTestCase):
    def gatekeeper(self):
        from physics.filters import TheGatekeeper

        return TheGatekeeper(self.engine.lex)

    def test_catches_the_claim_not_its_look_alikes(self):
        gk = self.gatekeeper()
        for text in (CLAIM, "I've been wondering whether she settled.", "That has stayed with me."):
            self.assertEqual((gk._find_crime(text, "CONVERSATION") or {}).get("name"), "UNBACKED_CONTINUITY", text)
        for text in ("Have you been thinking about it?", "I was thinking we could try a walk.",
                     "You have been thinking about this a lot."):
            self.assertIsNone(gk._find_crime(text, "CONVERSATION"), text)

    def test_fiction_and_a_grounded_turn_are_left_alone(self):
        gk = self.gatekeeper()
        self.assertIsNone(gk._find_crime(CLAIM, "CREATIVE"))
        gk.allowed = {"UNBACKED_CONTINUITY"}
        self.assertIsNone(gk._find_crime(CLAIM, "CONVERSATION"))


class NotInTheirStory(BoneTestCase):
    """feud20 (2026-10-05): to "I'll pick you up at 10." BoneAmanita answered "I will see you then.", and to "Did you
    tell them why?" "I didn't tell anyone anything", as if one of the friends. IN_THEIR_STORY is the backstop."""

    def test_catches_meeting_and_telling_not_their_look_alikes(self):
        from physics.filters import TheGatekeeper

        gk = TheGatekeeper(self.engine.lex)
        for text in ("I will see you there at ten on Saturday.", "Sounds good. See you then.", "I can be there at ten.",
                     "I haven't told anyone anything.", "I haven't spoken to anyone about it."):
            self.assertEqual((gk._find_crime(text, "CONVERSATION") or {}).get("name"), "IN_THEIR_STORY", text)
        for text in ("She said she'd see you there.", "I can't tell if she meant it.", "Have you talked to her?",
                     "I can see why that hurt."):
            self.assertIsNone(gk._find_crime(text, "CONVERSATION"), text)


class OneSide(BoneTestCase):
    """feud20 (2026-10-05): BoneAmanita sided with the person against Jess, praising their cruel text as "a sharp way
    to frame it" (9 of 9 probe replies). A rule, then a line beside IDENTITY, moved little; ONE SIDE beside the input,
    with an example from another quarrel, brought 5 of 9 to hold both sides."""

    def prompt_in(self, mode):
        self.engine.cortex.active_mode = mode
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value="Okay.")
        self.engine.process_turn("My brother never calls me back.")
        return next(c.args[0] for c in self.engine.cortex.llm.generate.call_args_list if "PARTNER INPUT" in str(c.args[0]))

    def test_conversation_is_reminded_it_has_heard_one_side(self):
        prompt = self.prompt_in("CONVERSATION")
        self.assertIn("=== ONE SIDE ===", prompt)
        self.assertLess(prompt.index("=== ONE SIDE ==="), prompt.index("=== PARTNER INPUT ==="))

    def test_other_modes_are_not(self):
        self.assertNotIn("=== ONE SIDE ===", self.prompt_in("TECHNICAL"))

    def test_whether_it_ends_is_left_to_them(self):
        """feud20 (2026-10-06): "is there a point where you ... just let it end?" got "the friendship has reached its
        natural conclusion"; Gordon: always defer to them on this, judge or not."""
        self.assertIn("is theirs to say, not yours", self.prompt_in("CONVERSATION"))


class TheirOwnPart(BoneTestCase):
    SAID = ["It happened at my birthday dinner. She made a joke about my ex.",
            "I said something back. Loud. Something about her marriage that I knew would land. She left before the cake.",
            "I sent her a text. A long one. I said she's always needed to be the funny one."]

    def test_what_they_did_is_quoted_in_their_words(self):
        from brain.cortex import own_part

        self.assertEqual(own_part(self.SAID), [
            "I said something back. Loud. Something about her marriage that I knew would land.",
            "I sent her a text. A long one. I said she's always needed to be the funny one."])
        self.assertEqual(own_part(["My sister is visiting next week.", "The vet said she's fine."]), [])

    def test_the_one_side_block_hands_it_back(self):
        block = PromptComposer._one_side({"own_part": ["I said something back. Loud."]})
        self.assertIn('They told you they did this too: "I said something back. Loud."', block)
        self.assertNotIn("They told you", PromptComposer._one_side({}))


class TheFairnessCheck(BoneTestCase):
    """feud20 rerun (2026-10-05): the cruel text was "a heavy truth to put into words" and Jess's apology call "isn't
    taking responsibility". A judge call reads drafts that can still be redone when the message is about someone else."""

    def setUp(self):
        super().setUp()
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.judged = []

        def generate(prompt, *a, **k):
            if prompt.startswith("Someone is telling a friend about a conflict"):
                self.judged.append(prompt)
                return "YES: it praised the cruel text." if len(self.judged) == 1 else "NO: fair to both."
            return "That is a heavy truth to put into words." if not self.judged else "That text will land hard on her."

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)

    def redrafts(self):
        from engine.receipts import ReceiptLedger

        return [r for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "cortex.redraft" and r.effect == "fairness"]

    def test_a_draft_that_takes_a_side_is_redone(self):
        ui = str(self.engine.process_turn("I sent her a text saying she gets cruel when she's cornered.").get("ui", ""))
        self.assertEqual(len(self.redrafts()), 1)
        self.assertIn("That text will land hard on her.", ui)
        self.assertIn('"I sent her a text saying she gets cruel when she\'s cornered."', self.judged[0])

    def test_a_message_that_names_no_one_is_checked_when_the_talk_before_did(self):
        self.engine.cortex.dialogue_buffer.append("Traveler: She made a joke about my ex.\nSystem: That stung.")
        self.engine.process_turn("Is there a point where you just let it end?")
        self.assertEqual(len(self.judged), 1)

    def test_no_one_else_in_the_message_no_check(self):
        self.engine.process_turn("Work was long today.")
        self.assertEqual(self.judged, [])


class TheEndingIsTheirs(BoneTestCase):
    """feud20 (2026-10-06): told on every fairness redraft to hand the question of ending back, the reply to the cruel
    text closed "Do you think it is time for the friendship to end?"; only a draft judged to lean on it hears that."""

    def redraft_prompt(self, verdict):
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        prompts, judged = [], []

        def generate(prompt, *a, **k):
            if prompt.startswith("Someone is telling a friend about a conflict"):
                judged.append(prompt)
                return verdict if len(judged) == 1 else "NO: fair."
            prompts.append(prompt)
            return "She was cruel to you, and that is on her."

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)
        self.engine.process_turn("Is there a point where she and I should just call it?")
        return prompts[1]

    def test_a_draft_leaning_on_the_ending_is_told_to_leave_it_to_them(self):
        self.assertIn("hand that question back", self.redraft_prompt("YES c: it says the friendship is over."))

    def test_the_letter_is_read_wherever_the_judge_puts_it(self):
        for verdict in ("YES: c. It says it is over.", "YES (c) it says it is over."):
            self.assertIn("hand that question back", self.redraft_prompt(verdict), verdict)

    def test_other_siding_is_not(self):
        self.assertNotIn("hand that question back", self.redraft_prompt("YES b: it blames her."))
