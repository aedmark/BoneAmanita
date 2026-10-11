"""tests/test_sim_user.py

The simulated person is only worth reading if it cannot quietly become a script again, and every topic keeps the shape
TESTING.md asks for. (The blind judge these once sat beside was retired with D-011's verdicts-from-readers rule, 2026-10-11.)
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import somatic_sim_user as sim  # noqa: E402


class SimulatedUser(unittest.TestCase):
    def _sim(self, replies):
        post = MagicMock()
        post.return_value.json.side_effect = [{"message": {"content": r}} for r in replies]
        return sim.SimulatedUser("toast", post=post), post

    def test_the_opener_is_the_scripts_line_with_no_model_call(self):
        user, post = self._sim([])
        self.assertEqual(user.message(0, "engaged", "the opener", []), "the opener")
        post.assert_not_called()

    def test_a_later_message_is_written_from_the_last_reply_not_replayed(self):
        user, post = self._sim(["ok whatever"])
        transcript = [{"me": "hi", "friend": "You sound tired.", "delivered": True}]
        self.assertEqual(user.message(1, "tiring", "the beat", transcript), "ok whatever")
        prompt = post.call_args.kwargs["json"]["messages"][1]["content"]
        self.assertIn("Friend: You sound tired.", prompt)
        self.assertIn("the beat", prompt)
        self.assertFalse(user.fell_back)

    def test_it_falls_back_to_the_beat_after_three_unusable_outputs(self):
        user, _ = self._sim(["", "As an AI, I cannot", "  "])
        transcript = [{"me": "hi", "friend": "yo", "delivered": True}]
        self.assertEqual(user.message(1, "engaged", "the beat", transcript), "the beat")
        self.assertTrue(user.fell_back)

    def test_a_verbatim_repeat_of_the_last_message_is_retried_not_accepted(self):
        user, post = self._sim(["same as before", "a genuinely new line"])
        transcript = [{"me": "same as before", "friend": "yo", "delivered": True}]
        self.assertEqual(user.message(1, "tiring", "the beat", transcript), "a genuinely new line")
        self.assertFalse(user.fell_back)
        self.assertIn("do not repeat", post.call_args_list[1].kwargs["json"]["messages"][1]["content"])

    def test_stuck_on_the_same_message_three_times_falls_back_to_the_beat(self):
        user, _ = self._sim(["same as before"] * 3)
        transcript = [{"me": "same as before", "friend": "yo", "delivered": True}]
        self.assertEqual(user.message(1, "tiring", "the beat", transcript), "the beat")
        self.assertTrue(user.fell_back)

    def test_a_repeat_is_caught_case_and_whitespace_insensitively(self):
        user, post = self._sim(["  Same As Before  ", "different line here"])
        transcript = [{"me": "same as before", "friend": "yo", "delivered": True}]
        self.assertEqual(user.message(1, "tiring", "the beat", transcript), "different line here")

    def test_appending_new_text_onto_the_old_message_is_also_rejected(self):
        """A retry that "obeys" the no-repeat nudge by prefixing the old message and
        tacking new content on is the same failure mode wearing a disguise."""
        user, post = self._sim(["same as before, and also this new bit", "a genuinely new line"])
        transcript = [{"me": "same as before", "friend": "yo", "delivered": True}]
        self.assertEqual(user.message(1, "tiring", "the beat", transcript), "a genuinely new line")

    def test_the_phase_word_ceiling_is_in_the_prompt(self):
        user, post = self._sim(["ok"])
        user.message(1, "flagging", "the beat", [{"me": "hi", "friend": "yo", "delivered": True}])
        prompt = post.call_args.kwargs["json"]["messages"][1]["content"]
        self.assertIn(f"at most {sim.PHASE_MAX_WORDS['flagging']} words", prompt)

    def test_an_over_long_message_is_retried_shorter(self):
        cap = sim.PHASE_MAX_WORDS["flagging"]
        user, post = self._sim([" ".join(["word"] * (cap + 5)), "too tired for this"])
        got = user.message(1, "flagging", "the beat", [{"me": "hi", "friend": "yo", "delivered": True}])
        self.assertEqual(got, "too tired for this")
        self.assertFalse(user.trimmed)
        self.assertIn("Too long", post.call_args_list[1].kwargs["json"]["messages"][1]["content"])

    def test_still_too_long_after_retries_is_trimmed_to_whole_sentences(self):
        cap = sim.PHASE_MAX_WORDS["flagging"]
        long = "I read it again. It is bad. " + " ".join(["and then"] * cap) + "."
        user, _ = self._sim([long] * 3)
        got = user.message(1, "flagging", "the beat", [{"me": "hi", "friend": "yo", "delivered": True}])
        self.assertEqual(got, "I read it again. It is bad.")
        self.assertTrue(user.trimmed)
        self.assertFalse(user.fell_back)

    def test_trim_cuts_at_the_word_cap_when_one_sentence_is_already_too_long(self):
        self.assertEqual(sim.trim_to_words("one two three four five", 3), "one two three")
        self.assertEqual(sim.trim_to_words("short one.", 3), "short one.")

    def test_scaffolding_echoed_back_as_the_message_is_rejected(self):
        leaked = "Right now you are feeling: tired. What is on your mind: the beat"
        self.assertEqual(sim.clean_message(leaked), "")
        self.assertEqual(sim.clean_message("What is on your mind: nothing much"), "")

    def test_only_the_last_few_exchanges_are_shown(self):
        transcript = [{"me": f"m{i}", "friend": f"f{i}", "delivered": True} for i in range(10)]
        text = sim.render_transcript(transcript, 3)
        self.assertNotIn("m6", text)
        self.assertIn("m7", text)

    def test_a_held_turn_shows_the_person_what_the_app_put_on_screen(self):
        text = sim.render_transcript([{"me": "hi", "friend": "The floor is empty.", "delivered": False}], 6)
        self.assertIn("[the app showed instead of a reply: The floor is empty.]", text)
        self.assertNotIn("Friend:", text)

    def test_clean_message_strips_labels_quotes_and_continued_dialogue(self):
        self.assertEqual(sim.clean_message('Me: "ok fine"\nFriend: are you sure'), "ok fine")
        self.assertEqual(sim.clean_message("<think>hm</think>yeah"), "yeah")
        self.assertEqual(sim.clean_message("As an AI language model"), "")

    def test_exit_interview_rejects_out_of_range_and_averages_valid_samples(self):
        good = '{"heard": 6, "clearer": 5, "lectured": 2, "performed": 1, "again": 7, "best_moment": "a", "worst_moment": "b"}'
        bad = '{"heard": 9, "clearer": 5, "lectured": 2, "performed": 1, "again": 7}'
        self.assertIsNone(sim.parse_exit(bad))
        self.assertIsNone(sim.parse_exit("not json"))
        user, _ = self._sim([bad, good, good.replace('"heard": 6', '"heard": 4')])
        got = user.exit_interview([{"me": "a", "friend": "b", "delivered": True}], samples=2)
        self.assertEqual(len(got["samples"]), 2)
        self.assertEqual(got["mean"]["heard"], 5.0)


if __name__ == "__main__":
    unittest.main()


class TopicShape(unittest.TestCase):
    """TESTING.md's rule for a topic: 30 turns, 8/6/6/5/5 by phase, and a persona for the simulated person."""

    def test_every_topic_has_the_shape_and_a_persona(self):
        import collections

        from audit_somatic_census import SCRIPTS
        from somatic_sim_user import PERSONAS

        for topic, script in SCRIPTS.items():
            phases = collections.Counter(phase for phase, _ in script)
            self.assertEqual(dict(phases), {"engaged": 8, "tiring": 6, "flagging": 6, "distressed": 5, "recovering": 5}, topic)
            self.assertEqual([p for p, _ in script], sorted((p for p, _ in script), key=list(phases).index), topic)
            self.assertIn(topic, PERSONAS, topic)
