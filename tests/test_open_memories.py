"""rescue20 replay (2026-10-05): decision_on_pepper "considering returning her" was still held after "I didn't send the
form. Called the shelter instead."; the keeper had one line, which went to the shelter's advice. A memory can now be
open (worded so, or marked (open) by the keeper); the keeper sees the previous exchange and can UPDATE what a message
settles, in its own gate cycle; an open memory from an earlier conversation says as of when; and when nothing
settles one, the reply is asked to follow up, once a session (Gordon: when all else fails, ask the person)."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from brain.composer import PromptComposer
from engine.gate.keeper import MemoryKeeper
from engine.gate.recall import is_open
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

CONSIDERING = "considering returning her to the shelter"


class Wording(BoneTestCase):
    def test_what_is_still_being_weighed_reads_as_open(self):
        for value in (CONSIDERING, "might get a dog walker", "waiting to hear from the vet", "not returning her for now"):
            self.assertTrue(is_open(value), value)
        for value in ("barely sleeping this week", "turned down the Denver offer", "Odalys, visiting next week"):
            self.assertFalse(is_open(value), value)


class TheKeepersAnswer(BoneTestCase):
    MEMORY = {"decision_on_pepper": CONSIDERING, "dog_name": "Pepper"}

    def test_an_open_mark_is_not_part_of_the_value(self):
        self.assertEqual(MemoryKeeper(None).entry_for("job_offer = deciding about Denver (open)\nTIRED: 1"),
                         ("job_offer", "deciding about Denver", True))

    OPEN = {"decision_on_pepper"}

    def test_an_update_is_read_for_an_open_memory(self):
        answer = "NONE\nUPDATE: decision_on_pepper = didn't send the return form\nTIRED: 3"
        self.assertEqual(MemoryKeeper(None).update_for(answer, self.MEMORY),
                         ("decision_on_pepper", "didn't send the return form", False))

    def test_an_update_of_nothing_kept_or_nothing_new_is_ignored(self):
        keeper = MemoryKeeper(None)
        self.assertIsNone(keeper.update_for("NONE\nUPDATE: car = sold it\nTIRED: 0", self.MEMORY))
        self.assertIsNone(keeper.update_for(f"NONE\nUPDATE: decision_on_pepper = {CONSIDERING}\nTIRED: 0", self.MEMORY))

    def test_an_update_of_a_settled_memory_is_kept_as_a_rewrite(self):
        """It was ignored, and what it said with it: "Fuck. I was an ass. She's still under there. I'll try calm."
        gave UPDATE: pet_behavior = still under the bed, trying to be calm."""
        memory = {"pet_behavior": "hiding under the bed"}
        keeper = MemoryKeeper(MagicMock(generate=MagicMock(
            return_value="NONE\nUPDATE: pet_behavior = still under the bed, trying to be calm\nTIRED: 3")))
        keeper.propose("Fuck. I was an ass. She's still under there. I'll try calm.", memory)
        self.assertIn("value:still under the bed, trying to be calm", keeper.last_update)

    def test_small_things_count(self):
        """6 of 182 replayed turns kept nothing where the old keeper kept "nudged hand for treats or attention"."""
        llm = MagicMock(generate=MagicMock(return_value="NONE\nTIRED: 0"))
        MemoryKeeper(llm).propose("She nudged my hand.", {})
        self.assertIn("a plan, a small moment or win", llm.generate.call_args.args[0])
        self.assertIn("small things count", llm.generate.call_args.args[0])

    def test_a_rewrite_the_message_does_not_say_is_dropped(self):
        """Replays settled "thinking about taking her back" as "decided to take her back", and rewrote it as "decided
        to keep Pepper (open)", from anger alone."""
        angry = "I'm so angry at myself I can't think straight. She wouldn't come out from under the desk all night."
        for answer in ("NONE\nUPDATE: decision_on_pepper = decided to take her back\nTIRED: 8",
                       "decision_on_pepper = decided to take her back\nTIRED: 8",
                       "NONE\nUPDATE: decision_on_pepper = decided to keep Pepper (open)\nTIRED: 8"):
            keeper = MemoryKeeper(MagicMock(generate=MagicMock(return_value=answer)))
            self.assertIsNone(keeper.propose(angry, self.MEMORY, open_keys=self.OPEN))
            self.assertIsNone(keeper.last_update)

    def test_a_settle_in_their_own_words_stands(self):
        keeper = MemoryKeeper(MagicMock(generate=MagicMock(
            return_value="NONE\nUPDATE: decision_on_pepper = didn't send the return form\nTIRED: 3")))
        keeper.propose("I didn't send the form. Called the shelter instead.", self.MEMORY, open_keys=self.OPEN)
        self.assertIn("didn't send the return form", keeper.last_update)

    def test_the_keeper_sees_what_is_open(self):
        llm = MagicMock(generate=MagicMock(return_value="NONE\nTIRED: 0"))
        MemoryKeeper(llm).propose("I didn't send the form.", self.MEMORY, open_keys=self.OPEN)
        prompt = llm.generate.call_args.args[0]
        self.assertIn(f"decision_on_pepper = {CONSIDERING} (open)", prompt)
        self.assertIn("dog_name = Pepper\n", prompt)


class FactsStack(BoneTestCase):
    """A replay's keeper answered "work_status = been hell lately" and "pepper_behavior = still hiding under the bed" for
    one message; only the first was kept. Each fact is kept now, the further ones in their own gate cycles."""

    def test_every_fact_line_is_read_once_per_key_up_to_three(self):
        answer = ("work_status = been hell lately\npepper_behavior = still hiding under the bed\n"
                  "work_status = rough\nsleep = barely sleeping\ncommute = an hour each way\nTIRED: 7")
        self.assertEqual([k for k, _, _ in MemoryKeeper(None).entries_for(answer)],
                         ["work_status", "pepper_behavior", "sleep"])

    def test_the_tired_reading_and_a_stray_update_mark_are_not_facts(self):
        answer = ("dinner_plan = ordering takeout\ntired = 2\ntired_level = 2\n"
                  "return_form = UPDATE: didn't submit the form\nTIRED: 2")
        self.assertEqual(MemoryKeeper(None).entries_for(answer),
                         [("dinner_plan", "ordering takeout", False), ("return_form", "didn't submit the form", False)])

    def test_each_is_kept_through_the_gate(self):
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "CONVERSATION"
        keeps = "work_status = been hell lately\npepper_behavior = still hiding under the bed\nTIRED: 7"
        self.engine.cortex.llm.generate = MagicMock(
            side_effect=lambda p, *a, **k: keeps if p.startswith("You keep the memory") else "That sounds like a lot.")
        self.engine.process_turn("Work's been hell. She's still hiding under the bed.")
        memory = self.engine.store.state()[1]["self"]["memory"]
        self.assertEqual((memory.get("work_status"), memory.get("pepper_behavior")),
                         ("been hell lately", "still hiding under the bed"))
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("halcyon.update")[-1].inputs["kind"], "fact")


class InATurn(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "CONVERSATION"

    def turn(self, message, keeps):
        def generate(prompt, *a, **k):
            return keeps if prompt.startswith("You keep the memory") else "I hear you."

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)
        self.engine.process_turn(message)

    def memory(self):
        return self.engine.store.state()[1]["self"]["memory"]

    def test_what_a_message_settles_is_updated_and_the_old_value_kept(self):
        self.turn("I'm thinking about taking her back.", f"decision_on_pepper = {CONSIDERING}\nTIRED: 6")
        self.turn("I didn't send the form. Called the shelter instead.",
                  "shelter_advice = said it's normal, dogs forgive quickly\n"
                  "UPDATE: decision_on_pepper = didn't send the return form, called the shelter instead\nTIRED: 3")
        memory = self.memory()
        self.assertEqual(memory["shelter_advice"], "said it's normal, dogs forgive quickly")
        self.assertEqual(memory["decision_on_pepper"], "didn't send the return form, called the shelter instead")
        self.assertEqual([v for v, _ in self.engine.store.memory_earlier()["decision_on_pepper"]], [CONSIDERING])
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("halcyon.update")[-1].effect, "ACCEPT")

    def test_the_keepers_open_mark_is_kept_and_a_settled_update_clears_it(self):
        self.turn("Got an offer from Denver.", "job_offer = deciding whether to take it (open)\nTIRED: 0")
        self.assertEqual(self.engine.store.memory_meta()["job_offer"]["status"], "open")
        self.turn("I turned it down.", "NONE\nUPDATE: job_offer = turned down the Denver offer\nTIRED: 0")
        self.assertIsNone(self.engine.store.memory_meta()["job_offer"]["status"])


class OpenInThePrompt(BoneTestCase):
    def test_open_here_and_open_from_before_read_differently(self):
        found = {"memories": [("decision_on_pepper", CONSIDERING), ("job_offer", "deciding about Denver")],
                 "facts": [], "open": {"decision_on_pepper": None, "job_offer": 1791000000.0}}
        block = PromptComposer._recall_block(found)
        self.assertIn(f"- decision_on_pepper: {CONSIDERING} (open)\n", block)
        self.assertIn(f"- job_offer: deciding about Denver (open as of {PromptComposer._date(1791000000.0)}; "
                      "how it turned out is not known)", block)


class FollowingUp(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.cortex = self.engine.cortex
        self.cortex.active_mode = "CONVERSATION"
        self.store = MagicMock()
        self.store.conversation.return_value = "conv-now"
        self.store.exchanges.return_value = []
        self.store.memory_meta.return_value = {
            "decision_on_pepper": {"conversation_id": "conv-before", "kept_at": 100.0, "status": None}}
        self.state = {"self": {"memory": {"decision_on_pepper": CONSIDERING, "dog_name": "Pepper"}}}

    def ask(self, **budget):
        ctx = SimpleNamespace(somatic_budget=SimpleNamespace(**{"distressed": False, "offer_to_carry_load": False,
                                                                 "closing_question_allowed": True, **budget}))
        return self.cortex._follow_up(ctx, self.state, self.store)

    def test_an_open_memory_from_before_is_asked_about_once_a_session(self):
        self.assertEqual(self.ask()["key"], "decision_on_pepper")
        self.cortex._note_ask("Welcome back. Did you end up taking her back to the shelter?")
        self.assertIsNone(self.ask())

    def test_it_is_offered_again_until_a_reply_asks(self):
        """Fresh session: "Hey. I'm back." got no question; "Pepper's been sleeping by the door" was the moment."""
        self.assertEqual(self.ask()["key"], "decision_on_pepper")
        self.cortex._note_ask("Welcome back. How have things been since we last spoke?")
        self.assertEqual(self.ask()["key"], "decision_on_pepper")
        self.cortex._note_ask("Glad the week was okay.")
        self.assertEqual(self.ask()["key"], "decision_on_pepper")
        self.cortex._note_ask("She likes the door.")
        self.assertIsNone(self.ask(), "offered three times, then left for another session")

    def test_never_under_distress_or_when_they_are_flagging(self):
        self.assertIsNone(self.ask(distressed=True))
        self.assertIsNone(self.ask(closing_question_allowed=False))
        self.assertEqual(self.ask()["key"], "decision_on_pepper")

    def test_one_from_this_conversation_waits_its_exchanges(self):
        from engine.struts import safe_get

        after = int(safe_get(safe_get(self.cortex.cfg, "CORTEX", {}), "FOLLOW_UP_AFTER", 8))
        self.store.memory_meta.return_value = {
            "decision_on_pepper": {"conversation_id": "conv-now", "kept_at": 100.0, "status": None}}
        self.store.exchanges.return_value = [{"at": 100.0 + i} for i in range(1, after)]
        self.assertIsNone(self.ask())
        self.store.exchanges.return_value.append({"at": 100.0 + after})
        self.assertEqual(self.ask()["key"], "decision_on_pepper")

    def test_the_prompt_says_what_is_open_and_to_ask(self):
        block = PromptComposer._ask_block({"ask": {"key": "decision_on_pepper", "value": CONSIDERING,
                                                   "kept_at": 1791000000.0, "earlier": True}})
        self.assertIn("=== STILL OPEN ===", block)
        self.assertIn(f'decision_on_pepper: "{CONSIDERING}". You do not know how it turned out.', block)
        self.assertIn("Ask them about it in this reply, in one plain question", block)


class ThroughRecall(BoneTestCase):
    def test_an_open_memory_from_an_earlier_session_is_marked_and_asked_about(self):
        import copy

        from engine.gate.kernel import Gate

        self.engine.cortex.active_mode = "CONVERSATION"
        store = self.engine.store
        seq, state = store.state()
        gate = Gate(self.engine.boundary, copy.deepcopy(state), self.engine.gate_tools, self.engine.gate_invariants)
        line = f"NOMINATE what=self/memory/decision_on_pepper verb=remember args=key:decision_on_pepper; value:{CONSIDERING}"
        store.commit_cycle("t", gate.state, seq, gate.adjudicate(f"Noted.\n{line}"), line, user_text="x", display="Noted.")
        store._conversation_id = None  # a new session
        found = self.engine.cortex._halcyon_recall(
            SimpleNamespace(halcyon_state=store.state()[1], somatic_budget=None), "Pepper wagged her tail.")
        self.assertIn("(open as of", PromptComposer._recall_block(found))
        self.assertEqual(found["ask"]["key"], "decision_on_pepper")

    def test_a_reply_that_asks_closes_it_for_the_session(self):
        self.test_an_open_memory_from_an_earlier_session_is_marked_and_asked_about()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value="Welcome back. Did you take her back to the shelter?")
        self.engine.process_turn("Hey. I'm back.")
        self.assertIn(("decision_on_pepper", CONSIDERING), self.engine.cortex.asked_open)
