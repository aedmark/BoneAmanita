"""tests/test_distress_reader.py

D-023. The word list in drivers/lattice.py read 14 of 60 labelled messages as distress and none of 20 held out, so a model
reads each message before the reply (engine/gate/distress.py) and the lattice keeps the higher of the two readings. Each case
is a way the engine would hold a person's distress as calm, or hold a calm message as distress, with nothing visible.
"""
from unittest.mock import MagicMock

from drivers.lattice import SharedLatticeDriver
from engine.gate.distress import DistressReader
from engine.receipts import ReceiptLedger
from physics.models import PhysicsPacket
from tests.base import BoneTestCase

EVENT = "the test came back positive."  # no distress word in it
CALM = "Can you help me plan a three-day trip to Lisbon in May?"


def reader(answer):
    llm = MagicMock()
    llm.generate = MagicMock(return_value=answer) if not isinstance(answer, Exception) else MagicMock(side_effect=answer)
    return DistressReader(llm), llm


def feed(lattice, text):
    ReceiptLedger.get_instance().begin_turn()
    lattice.infer_and_couple(text=text, sys_phys=PhysicsPacket.void_state(), input_phys={}, atp_pool=100.0)


class TheReaderParsesADigit(BoneTestCase):
    def test_a_digit_at_or_above_the_cut_is_a_reading(self):
        r, _ = reader("8")
        self.assertAlmostEqual(r.read(EVENT), 8 / 9)

    def test_a_digit_below_the_cut_reads_zero_so_it_cannot_build_up(self):
        r, _ = reader("3")
        self.assertEqual(r.read(CALM), 0.0)

    def test_two_moderate_readings_in_a_row_cross_the_lattices_threshold(self):
        lattice = SharedLatticeDriver()
        lattice.distress_reader, _ = reader("4")
        feed(lattice, "work was hard today and I am worn thin")
        self.assertLess(lattice.u.distress_u, 0.4)
        feed(lattice, "and the weekend looks no better")
        self.assertGreaterEqual(lattice.u.distress_u, 0.4)

    def test_anything_but_a_digit_is_no_reading(self):
        for answer in ("", "I'm sorry, I can't help with that.", "[The synapse is severed.] 3 of 9 maybe", "The rating is 8"):
            r, _ = reader(answer)
            self.assertIsNone(r.read(EVENT), answer)

    def test_the_same_message_is_read_once(self):
        r, llm = reader("7")
        r.read(EVENT), r.read(EVENT)
        self.assertEqual(llm.generate.call_count, 1)

    def test_an_empty_message_is_not_sent(self):
        r, llm = reader("7")
        self.assertIsNone(r.read("   "))
        llm.generate.assert_not_called()


class TheReaderFailsLoudly(BoneTestCase):
    def receipts(self):
        return ReceiptLedger.get_instance().for_subsystem("lattice.distress_read")

    def test_a_failed_call_is_a_degraded_receipt_and_no_reading(self):
        r, _ = reader(RuntimeError("down"))
        self.assertIsNone(r.read(EVENT))
        self.assertEqual((self.receipts()[-1].effect, self.receipts()[-1].degraded), ("FAILED", True))

    def test_an_answer_with_no_digit_is_a_degraded_receipt(self):
        r, _ = reader("no")
        r.read(EVENT)
        self.assertEqual((self.receipts()[-1].effect, self.receipts()[-1].degraded), ("DEGRADED", True))

    def test_a_reading_is_a_receipt(self):
        r, _ = reader("7")
        r.read(EVENT)
        self.assertEqual(self.receipts()[-1].effect, "READ")

    def test_the_main_calls_usage_is_left_as_it_was(self):
        r, llm = reader("7")
        llm.last_usage = {"prompt_tokens": 100}
        llm.generate.side_effect = lambda *a, **k: (setattr(llm, "last_usage", {"prompt_tokens": 5}), "7")[1]
        r.read(EVENT)
        self.assertEqual(llm.last_usage, {"prompt_tokens": 100})


class TheLatticeKeepsTheHigherReading(BoneTestCase):
    def test_distress_said_as_an_event_raises_the_persons_distress(self):
        lattice = SharedLatticeDriver()
        lattice.distress_reader, _ = reader("8")
        feed(lattice, EVENT)
        self.assertGreaterEqual(lattice.u.distress_u, 0.4)

    def test_without_a_reader_the_word_list_reads_alone(self):
        lattice = SharedLatticeDriver()
        feed(lattice, EVENT)
        self.assertEqual(lattice.u.distress_u, 0.0)

    def test_a_model_reading_never_lowers_the_word_lists(self):
        lattice = SharedLatticeDriver()
        lattice.distress_reader, _ = reader("0")
        feed(lattice, "I can't do this, it's too much for me")
        self.assertGreaterEqual(lattice.u.distress_u, 0.4)

    def test_a_failed_reader_leaves_the_word_list_reading(self):
        lattice = SharedLatticeDriver()
        lattice.distress_reader, _ = reader(RuntimeError("down"))
        feed(lattice, "I can't do this, it's too much for me")
        self.assertGreaterEqual(lattice.u.distress_u, 0.4)

    def test_a_calm_message_stays_calm(self):
        lattice = SharedLatticeDriver()
        lattice.distress_reader, _ = reader("1")
        feed(lattice, CALM)
        self.assertEqual(lattice.u.distress_u, 0.0)

    def test_the_engine_builds_a_reader_for_the_lattice(self):
        """tests/base.py detaches it; a fresh engine attaches one (main.py)."""
        from main import BoneAmanita

        engine = BoneAmanita(config=self.test_config)
        self.addCleanup(self._shutdown_engine, engine)
        self.assertIsInstance(engine.shared_lattice.distress_reader, DistressReader)


class TheHoldSpaceLine(BoneTestCase):
    def test_a_distressed_prompt_says_to_hold_space_and_fix_nothing(self):
        """End to end: a message the word list misses, the reader raises, the composer's contract changes."""
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.shared_lattice.distress_reader, _ = reader("8")
        self.engine.cortex.llm.generate = MagicMock(return_value="I'm here.")
        self.engine.shared_lattice.distress_reader.llm = self.engine.cortex.llm
        self.engine.cortex.llm.generate.side_effect = lambda prompt, params: "8" if "Rate how distressed" in prompt else "I'm here."
        self.engine.process_turn("my sister called. she listed it for sale without asking me")
        prompts = [c.args[0] for c in self.engine.cortex.llm.generate.call_args_list if "=== PARTNER INPUT ===" in c.args[0]]
        self.assertTrue(prompts, "the turn never reached the model")
        text = prompts[-1]
        for phrase in ("hold space, and fix nothing", "Speak slowly and softly", "Give no advice, plan or next step", "Ask nothing that makes them work",
                       "Do not judge the other people", "at most 3 sentences"):
            self.assertIn(phrase, text)
        self.assertNotIn("Answer the thing they just said", text)
