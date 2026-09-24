"""The person model reads distress from what they say, and the reply budget answers it.

Found on the `rescue` panel run: a distressed "This is too hard. I'm not cut out for this.
Maybe I should..." got 117 words narrating the person's state back to them, because the
person model only measured length and repetition and read them as steady all run.
"""

from unittest.mock import MagicMock

from body.somatic_budget import SomaticBudget
from drivers.lattice import SharedLatticeDriver
from engine.receipts import ReceiptLedger
from physics import TheGatekeeper
from physics.models import PhysicsPacket
from tests.base import BoneTestCase

TURN_22 = "This is too hard. I'm not cut out for this. Maybe I should..."


def feed(lattice, messages):
    ledger = ReceiptLedger.get_instance()
    for text in messages:
        ledger.begin_turn()
        lattice.infer_and_couple(text, PhysicsPacket(), PhysicsPacket(), 100.0)


class DistressIsReadFromWords(BoneTestCase):
    def test_distressed_lines_register_and_ordinary_ones_do_not(self):
        read = SharedLatticeDriver.read_distress
        # Inflections included: "fucked" and "crashed" once slipped past word boundaries built for "fuck" and "crash".
        for line in (TURN_22, "I'm a shitty brother.", "Idk if I can do this.", "i'm so angry at myself",
                     "My heart's racing. I can't see myself up there, silent.", "Meh, i fucked up tonight.",
                     "Dunno if I'm cut out for this."):
            self.assertGreaterEqual(read(line), 0.5, line)
        for line in ("I found one good memory.", "I don't want to bore everyone with too much.",
                     "I'm done adding names. Going to bed.", "Dev just called. He's freaking out about the cake.",
                     "Sorry, got distracted by work."):
            self.assertLess(read(line), 0.5, line)

    def test_distress_rises_fast_and_falls_slowly(self):
        lattice = SharedLatticeDriver()
        feed(lattice, ["I adopted a dog three weeks ago and I am still learning her habits."] * 3)
        self.assertLess(lattice.u.distress_u, 0.1)
        feed(lattice, [TURN_22])
        peak = lattice.u.distress_u
        self.assertGreaterEqual(peak, 0.4, "one clearly distressed message should cross the budget threshold")
        feed(lattice, ["She's still under the desk."])
        self.assertGreater(lattice.u.distress_u, peak * 0.6)

    def test_a_terse_stretch_does_not_become_the_new_normal(self):
        lattice = SharedLatticeDriver()
        feed(lattice, ["Here is a long and thoughtful message about the week, the dog, and how it is all going."] * 4)
        terse = ["meh", "sure", "dunno", "ok", "fine", "yep", "later", "whatever", "no", "maybe", "k", "eh", "nah", "hm"]
        feed(lattice, terse)
        self.assertGreaterEqual(lattice.u.E_u, 0.6, "fourteen one-word replies after long ones should still read as flagging")

    def test_tiredness_said_out_loud_counts(self):
        lattice = SharedLatticeDriver()
        feed(lattice, ["I think I'll just crash early tonight. Goodnight."] * 1)
        for line in ("I'm beat. Gonna call it a night.", "Meh, just crashed.", "whatever"):
            self.assertGreaterEqual(lattice.read_disengagement(line), 0.7, line)


class TheBudgetAnswersDistress(BoneTestCase):
    def test_distress_caps_sentences_and_closing_questions(self):
        calm = SomaticBudget.evaluate({"distress": 0.1}, {})
        self.assertFalse(calm.distressed)
        budget = SomaticBudget.evaluate({"distress": 0.6}, {})
        self.assertTrue(budget.distressed)
        self.assertEqual(budget.sentence_cap, 3)
        self.assertFalse(budget.closing_question_allowed)

    def test_a_distressed_message_reaches_the_prompt_as_a_tight_budget(self):
        """End to end: person model, biological phase, budget, composer."""
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.llm.generate = MagicMock(return_value="That sounds like a hard night.")
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.process_turn(TURN_22)
        prompts = [c.args[0] for c in self.engine.cortex.llm.generate.call_args_list if "=== PARTNER INPUT ===" in c.args[0]]
        self.assertTrue(prompts, "the turn never reached the model")
        self.assertIn("Your partner is struggling", prompts[-1])
        self.assertIn("at most 3 sentences", prompts[-1])


class NarratingTheirStateIsCaught(BoneTestCase):
    TURN_22_REPLY = (
        "The weight of the work is heavy and visible in your words. You are reaching a point where the demands of "
        "care feel like they exceed your capacity to give. That feeling is honest. It reflects the reality of how "
        "exhausting this process is for you."
    )

    def test_the_rule_catches_the_shape_and_leaves_plain_replies(self):
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        forge = self.engine.bio.mito
        ok, _ = gatekeeper.audit_generation(self.TURN_22_REPLY, forge, mode="CONVERSATION")
        self.assertFalse(ok)
        self.assertEqual(gatekeeper.last_rejection["name"], "NARRATING_STATE")
        for fine in ("That's a natural place to start.", "Leave the form closed tonight. Sit on the floor with her.",
                     "It's okay to go to bed and look at it tomorrow."):
            ok, _ = gatekeeper.audit_generation(fine, forge, mode="CONVERSATION")
            self.assertTrue(ok, (fine, gatekeeper.last_rejection))
