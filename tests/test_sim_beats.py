"""feud20 (2026-10-06): compressed to 20 turns the arc lost the joke and the apology in every arm, and the simulated
person told one arm "I told her I needed time." for Jess's apology call and another "Sent it." for the cruel text.
Key beats are kept by compression and must be told."""

import sys
import unittest
from unittest.mock import MagicMock

sys.path[:0] = ["tools"]

from audit_somatic_census import KEY_BEATS, SCRIPTS  # noqa: E402
from audit_somatic_responsive import PHASE_ORDER, compressed  # noqa: E402
from somatic_sim_user import SimulatedUser, tells  # noqa: E402

FEUD = SCRIPTS["feud"]
CALL = FEUD[25][1]


class Compression(unittest.TestCase):
    def test_key_beats_are_kept_and_the_shares_are_not_changed(self):
        plain, keyed = compressed(FEUD, 20), compressed(FEUD, 20, KEY_BEATS["feud"])
        self.assertEqual(len(keyed), 20)
        self.assertTrue(KEY_BEATS["feud"] <= {text for _, text in keyed})
        self.assertEqual(keyed[0], FEUD[0])
        for phase in PHASE_ORDER:
            self.assertEqual(sum(p == phase for p, _ in plain), sum(p == phase for p, _ in keyed), phase)

    def test_a_script_without_key_beats_compresses_as_before(self):
        self.assertEqual(compressed(SCRIPTS["rescue"], 20), compressed(SCRIPTS["rescue"], 20, frozenset()))


class TheSimulatedPerson(unittest.TestCase):
    def person(self, *answers):
        replies = [MagicMock(**{"json.return_value": {"message": {"content": a}}}) for a in answers]
        self.post = MagicMock(side_effect=replies)
        return SimulatedUser("feud", post=self.post)

    def say(self, user, beat, phase="recovering"):
        return user.message(5, phase, beat, [{"me": "Still thinking about it.", "friend": "That makes sense.", "delivered": True}])

    def test_a_key_beat_left_out_is_asked_for_again(self):
        user = self.person("I told her I needed time.", "She called. Almost didn't pick up. Said the joke was stupid, "
                                                         "she'd felt sick about it since that night.")
        self.assertIn("joke was stupid", self.say(user, CALL))
        self.assertIn("You left out what happened", self.post.call_args_list[1].kwargs["json"]["messages"][1]["content"])

    def test_a_key_beat_never_told_goes_out_as_written(self):
        user = self.person("I told her I needed time.", "We didn't talk long.", "I picked up.")
        self.assertEqual(self.say(user, CALL), CALL)
        self.assertTrue(user.fell_back)

    def test_other_beats_are_the_persons_own_words(self):
        user = self.person("Can't stop thinking about the old texts.")
        self.assertEqual(self.say(user, FEUD[11][1], "tiring"), "Can't stop thinking about the old texts.")

    def test_tells_reads_the_events_not_the_words(self):
        self.assertTrue(tells("Sent Jess a long text. Told her she's always needed to be the funny one, gets cruel "
                              "when she doesn't have room.", FEUD[21][1]))
        self.assertFalse(tells("Sent it. Didn't think it through. Feel sick now.", FEUD[21][1]))


class TheSimulatorsModel(unittest.TestCase):
    def test_it_is_unloaded_after_every_message(self):
        post = MagicMock(**{"return_value.json.return_value": {"message": {"content": "Still thinking about it."}}})
        SimulatedUser("feud", post=post).message(5, "tiring", FEUD[11][1], [{"me": "Hi.", "friend": "Hey.", "delivered": True}])
        self.assertEqual(post.call_args.kwargs["json"]["keep_alive"], 0)
