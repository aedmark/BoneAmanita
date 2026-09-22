"""tests/test_judge_controls.py

The blind judge is only worth reading if its controls are sound, and the
simulated person is only worth reading if it cannot quietly become a script
again. These cover the parts that decide that without a live model.
"""

import json
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import audit_somatic_blind_judge as bj  # noqa: E402
import somatic_sim_user as sim  # noqa: E402


class RankingParsing(unittest.TestCase):
    def test_two_way_ranking_parses(self):
        self.assertEqual(bj.parse_ranking("RANKING: B > A\nREASON: x", 2), ["B", "A"])
        self.assertEqual(bj.parse_ranking("**RANKING: B > A**", 2), ["B", "A"])

    def test_a_partial_ranking_is_dropped_not_guessed(self):
        self.assertIsNone(bj.parse_ranking("RANKING: B > A", 3))


class ControlConstruction(unittest.TestCase):
    def _runs(self):
        return {
            "BONEAMANITA": {t: {"reply": f"bone {t}", "message": f"m{t}"} for t in range(10)},
            "PROMPTED": {t: {"reply": f"friend {t}", "message": f"m{t}"} for t in range(10)},
        }

    def test_null_control_is_one_reply_under_three_labels(self):
        got = bj.candidate_replies("null", 4, self._runs(), {})
        self.assertEqual(set(got), set(bj.SLOTS["null"]))
        self.assertEqual(set(got.values()), {"bone 4"})

    def test_mismatch_control_uses_another_turns_reply_for_the_decoy(self):
        got = bj.candidate_replies("mismatch", 2, self._runs(), {2: 8})
        self.assertEqual(got["MISMATCH"], "friend 8")
        self.assertEqual(got["PROMPTED"], "friend 2")

    def test_decoys_are_never_the_same_turn_and_prefer_distance(self):
        turns = list(range(10))
        decoys = bj.pick_decoys(turns, turns, random.Random(1))
        for t, d in decoys.items():
            self.assertNotEqual(t, d)
            self.assertGreaterEqual(abs(t - d), 3)

    def test_decoys_come_from_another_phase_when_one_exists(self):
        turns = list(range(10))
        phases = {t: "engaged" if t < 5 else "distressed" for t in turns}
        decoys = bj.pick_decoys(turns, turns, random.Random(1), phases)
        for t, d in decoys.items():
            self.assertNotEqual(phases[t], phases[d])

    def test_decoys_fall_back_to_distance_when_every_turn_shares_a_phase(self):
        turns = list(range(10))
        decoys = bj.pick_decoys(turns, turns, random.Random(1), {t: "engaged" for t in turns})
        for t, d in decoys.items():
            self.assertGreaterEqual(abs(t - d), 3)

    def test_decoys_still_exist_when_only_near_turns_are_available(self):
        decoys = bj.pick_decoys([1, 2], [1, 2], random.Random(1))
        self.assertEqual(decoys, {1: 2, 2: 1})


class RunSelection(unittest.TestCase):
    def _cache(self, tmp):
        path = Path(tmp) / "c.jsonl"
        rows = [{"run": r, "topic": "t", "turn": 0, "reply": f"run {r}"} for r in ("a", "b", "c")]
        rows.append({"run": "z", "topic": "other", "turn": 0, "reply": "elsewhere"})
        path.write_text("\n".join(json.dumps(r) for r in rows))
        return path

    def test_back_steps_to_earlier_runs_of_the_same_topic(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._cache(tmp)
            self.assertEqual(bj.load_latest(path, "t")[0]["reply"], "run c")
            self.assertEqual(bj.load_latest(path, "t", back=2)[0]["reply"], "run a")

    def test_asking_for_more_runs_than_exist_finds_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(bj.load_latest(self._cache(tmp), "t", back=3), {})


class Delivery(unittest.TestCase):
    def test_a_silence_snapshot_is_not_a_delivered_reply(self):
        self.assertFalse(bj.is_delivered({"reply": "x", "snapshot_type": "SILENCE"}))
        self.assertTrue(bj.is_delivered({"reply": "x", "snapshot_type": "GEODESIC_FRAME"}))

    def test_an_explicit_delivered_flag_wins_over_the_snapshot_type(self):
        self.assertFalse(bj.is_delivered({"reply": "x", "delivered": False, "snapshot_type": None}))

    def test_no_reply_is_not_delivered(self):
        self.assertFalse(bj.is_delivered({"reply": None}))
        self.assertFalse(bj.is_delivered({}))


class Statistics(unittest.TestCase):
    def test_even_positions_show_no_lean(self):
        self.assertAlmostEqual(bj.chi_square_p_df2([10, 10, 10]), 1.0)

    def test_a_strong_lean_is_unlikely_by_chance(self):
        self.assertLess(bj.chi_square_p_df2([30, 5, 5]), 0.001)

    def test_binomial_tail_is_exact_for_a_small_case(self):
        self.assertAlmostEqual(bj.binom_tail(2, 2, 0.5), 0.25)
        self.assertAlmostEqual(bj.binom_tail(0, 5, 0.3), 1.0)


class HumanAgreement(unittest.TestCase):
    PICKS = "T — my picks\nBoneAmanita 1 | Prompted 1 | Vanilla 0 | no pick 1\n#01 engaged: BoneAmanita\n#02 tiring: Prompted\n#03 flagging: no pick"

    def test_panel_export_parses_and_drops_no_pick_lines(self):
        self.assertEqual(bj.parse_human(self.PICKS), {1: "BONEAMANITA", 2: "PROMPTED"})

    def test_agreement_counts_first_place_matches_per_vote(self):
        results = [
            {"turn": 1, "ranked": ["BONEAMANITA", "PROMPTED", "VANILLA"]},
            {"turn": 1, "ranked": ["PROMPTED", "BONEAMANITA", "VANILLA"]},
            {"turn": 2, "ranked": ["PROMPTED", "VANILLA", "BONEAMANITA"]},
        ]
        got = bj.human_agreement(results, {1: "BONEAMANITA", 2: "PROMPTED"})
        self.assertEqual((got["votes"], got["first_matches_pick"], got["turns"]), (3, 2, 2))
        self.assertAlmostEqual(got["pick_mean_rank"], (1 + 2 + 1) / 3, places=2)

    def test_turns_without_a_pick_are_ignored(self):
        got = bj.human_agreement([{"turn": 9, "ranked": ["A", "B", "C"]}], {1: "A"})
        self.assertEqual(got["votes"], 0)


class ResponsivePrompt(unittest.TestCase):
    def test_each_conversation_shows_its_own_context_and_hides_who_wrote_it(self):
        views = [
            {"context": [("hi", "hello there")], "message": "tired", "reply": "rest"},
            {"context": [("hi", "(no reply came back)")], "message": "ok", "reply": "sure"},
        ]
        text = bj.build_prompt_responsive(views)
        self.assertIn("Conversation A\nMe: hi\nFriend: hello there\nMe: tired\nFriend (newest reply): rest", text)
        self.assertIn("Conversation B", text)
        self.assertIn("There are 2; use only A and B.", text)


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
