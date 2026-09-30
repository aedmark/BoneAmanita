"""REM reflection (Gordon, 2026-09-29): what a memory felt like is recorded when it is kept (R1), a sleep
reflects on what was kept (R2), dreams from it (R3), and the dream is shown on waking (R4)."""

from unittest.mock import MagicMock

from engine.constants import Prisma
from engine.gate.feeling import describe, reading
from engine.gate.report import why_report
from tests.base import BoneTestCase

REST = {"DOP": 0.5, "OXY": 0.1, "COR": 0.0, "SER": 0.5, "ADR": 0.0, "MEL": 0.0}


class TheFeeling(BoneTestCase):
    def test_at_rest_it_was_calm_and_with_no_record_nothing(self):
        self.assertEqual(reading(REST), ["calm"])
        self.assertEqual((reading(None), reading({}), describe(None)), ([], [], ""))

    def test_what_stood_out_is_named_strongest_first(self):
        chem = {**REST, "COR": 0.6, "OXY": 0.45}
        self.assertEqual(reading(chem), ["tense", "close"])
        self.assertEqual(describe(chem), "tense, close (OXY 0.45, COR 0.60)")
        self.assertEqual(reading({**REST, "DOP": 0.1, "SER": 0.2}), ["flat", "low"])  # 0.2 past its margin, 0.1 past
        self.assertEqual(reading({**REST, "COR": 0.35, "OXY": 0.9}), ["close", "tense"])

    def test_why_says_how_it_felt(self):
        state = {"self": {"memory": {"sister_name": "Odalys"}}, "world": {}}
        meta = {"sister_name": {"mode": "CONVERSATION", "kept_at": 0.0, "kept_by": "keeper", "receipt_id": "r",
                                "feeling": {**REST, "OXY": 0.5}}}
        lines = why_report("sister_name", state, meta, {}, lambda r: None, now=60.0)
        self.assertIn("  Felt: close (OXY 0.50).", lines)


class KeptWithItsFeeling(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode, self.engine.ui_mode = "TECHNICAL", "WARM"
        self.engine.cortex.llm.generate = MagicMock(
            side_effect=lambda prompt, *a, **k: "sister_name = Odalys" if prompt.startswith("You keep the memory") else "Noted.")

    def test_a_kept_memory_carries_the_endocrine_state(self):
        self.engine.process_turn("My sister is Odalys.")
        feeling = self.engine.store.memory_meta()["sister_name"]["feeling"]
        self.assertEqual(set(feeling), set(REST))
        self.engine.cmd.interface.log = log = MagicMock()
        self.engine.cmd.execute("/memory why sister_name")
        self.assertIn("  Felt: ", Prisma.strip("\n".join(str(c.args[0]) for c in log.call_args_list)))

    def test_a_stand_in_body_records_no_feeling(self):
        self.engine.bio.endo.get_state = MagicMock(return_value="not a state")
        self.engine.process_turn("My sister is Odalys.")
        self.assertIsNone(self.engine.store.memory_meta()["sister_name"]["feeling"])


class TheReflector(BoneTestCase):
    def test_a_reflection_feels_like_what_it_came_from(self):
        from engine.gate.reflector import mean_feeling

        feeling = mean_feeling([{**REST, "OXY": 0.5}, {**REST, "OXY": 0.1, "COR": 0.4}, None])
        self.assertEqual((feeling["OXY"], feeling["COR"], feeling["DOP"]), (0.3, 0.2, 0.5))
        self.assertIsNone(mean_feeling([None]))

    def test_none_first_means_none(self):
        from engine.gate.reflector import MemoryReflector

        self.assertIsNone(MemoryReflector(None).line_for("NONE\nbusy_week = something anyway", ["a", "b"]))


class TheReflectVerb(BoneTestCase):
    def gate(self, memory):
        import yaml

        from engine.gate.kernel import Boundary, Gate
        from engine.gate.tools import TOOLS, build_invariants

        spec = yaml.safe_load(open("engine/gate/boundary.yaml"))
        state = {"world": {"schema_version": 2, "sources": {}, "nodes": {}, "edges": [], "constraints": []},
                 "self": {"memory": dict(memory)}}
        return Gate(Boundary(spec), state, TOOLS, build_invariants(spec))

    def test_it_writes_beside_the_memories_it_names(self):
        gate = self.gate({"a": "1", "b": "2"})
        receipt = gate.adjudicate("(Reflecting)\nNOMINATE what=self/memory/reflection.ab verb=reflect "
                                  "args=key:reflection.ab; value:a and b; from:a | b | gone")
        self.assertEqual(receipt["result"], {"reflected": "reflection.ab", "from": ["a", "b"]})
        self.assertEqual(gate.state["self"]["memory"]["reflection.ab"], "a and b")

    def test_with_none_of_its_memories_held_it_changes_nothing(self):
        gate = self.gate({})
        receipt = gate.adjudicate("(Reflecting)\nNOMINATE what=self/memory/reflection.x verb=reflect "
                                  "args=key:reflection.x; value:x; from:gone")
        self.assertIn("noop", receipt["result"])

    def test_the_model_is_not_offered_it(self):
        import yaml

        from engine.gate.tools import grammar_text

        self.assertNotIn("verb=reflect", grammar_text(yaml.safe_load(open("engine/gate/boundary.yaml"))))


class _Sleeper(BoneTestCase):
    """A test engine whose keeper, reflector and dreamer answer on cue."""

    MEANING = "busy_week = your sister visits while a release is due, and you care about both"

    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.memory_reflector.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.keeps, self.reflects, self.reflections = "NONE", self.MEANING, []
        self.dreams, self.dream_prompts = "A plane lands on a mountain trail. Odalys hands you the release notes.", []

        def generate(prompt, *a, **k):
            if prompt.startswith("You keep the memory"):
                return self.keeps
            if prompt.startswith("You are dreaming"):
                self.dream_prompts.append(prompt)
                if isinstance(self.dreams, Exception):
                    raise self.dreams
                return self.dreams
            if prompt.startswith("You are reflecting"):
                self.reflections.append(prompt)
                if isinstance(self.reflects, Exception):
                    raise self.reflects
                return self.reflects
            return "Noted."

        self.engine.cortex.llm.generate = MagicMock(side_effect=generate)

    def keep(self, mode, message, keeps):
        self.engine.cortex.active_mode, self.keeps = mode, keeps
        self.engine.process_turn(message)

    def memory(self):
        return self.engine.store.state()[1]["self"]["memory"]

    def reflect_receipts(self):
        from engine.receipts import ReceiptLedger

        return ReceiptLedger.get_instance().for_subsystem("halcyon.reflect")


class ReflectingInREM(_Sleeper):
    def test_a_sleep_reflects_on_what_was_kept_through_the_gate(self):
        self.keep("CONVERSATION", "My sister Odalys visits next week.", "sister_name = Odalys, visiting next week")
        self.keep("TECHNICAL", "The release is due Thursday.", "release_due = Thursday")
        self.engine.cortex.active_mode = "ADVENTURE"  # it sleeps in a story; the reflection is still the person's
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(self.memory()["reflection.busy_week"],
                         "your sister visits while a release is due, and you care about both")
        meta = self.engine.store.memory_meta()["reflection.busy_week"]
        self.assertEqual((meta["kept_by"], meta["mode"]), ("reflection", "TECHNICAL"))
        self.assertEqual(set(meta["feeling"]), set(REST))
        self.assertIn("- sister_name = Odalys, visiting next week (felt ", self.reflections[0])
        (receipt,) = self.reflect_receipts()
        self.assertEqual((receipt.effect, receipt.result_count), ("ACCEPT", 1))

    def test_once_per_sleep_and_only_what_is_new(self):
        self.keep("CONVERSATION", "My sister Odalys visits next week.", "sister_name = Odalys")
        self.keep("CONVERSATION", "I'm allergic to cashews.", "allergy = cashews")
        self.engine.orchestrator._process_rem_tick()
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(len(self.reflections), 1)
        self.keep("CONVERSATION", "My dog is Brisket.", "pet_name = Brisket")
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(len(self.reflections), 1)  # one new memory waits for company
        self.keep("CONVERSATION", "I work nights.", "work_hours = nights")
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(len(self.reflections), 2)
        self.assertIn("pet_name", self.reflections[1])
        self.assertNotIn("sister_name", self.reflections[1])
        self.assertNotIn("- reflection.", self.reflections[1])  # a reflection is not reflected on

    def test_a_storys_day_is_reflected_on_in_the_story(self):
        self.keep("ADVENTURE", "The vault opens at midnight.", "vault = opens at midnight")
        self.keep("ADVENTURE", "The guard sleeps at eleven.", "guard = sleeps at eleven")
        self.reflects = "the_heist = the guard sleeps an hour before the vault opens"
        self.engine.orchestrator._process_rem_tick()
        self.assertIn("story.reflection.the_heist", self.memory())
        self.assertEqual(self.engine.store.memory_meta()["story.reflection.the_heist"]["mode"], "ADVENTURE")
        self.assertIn("- vault = opens at midnight", self.reflections[0])

    def test_nothing_to_say_moves_on_and_a_failure_tries_again(self):
        self.keep("CONVERSATION", "My sister Odalys visits next week.", "sister_name = Odalys")
        self.keep("CONVERSATION", "I'm allergic to cashews.", "allergy = cashews")
        self.reflects = RuntimeError("down")
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(self.reflect_receipts()[-1].effect, "FAILED")
        self.reflects = "NONE"
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(len(self.reflections), 2)  # the failure was retried
        self.assertEqual(self.reflect_receipts()[-1].effect, "NONE")
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(len(self.reflections), 2)  # NONE moved the mark
        self.assertNotIn("reflection.", " ".join(self.memory()))

    def test_why_traces_a_reflection_to_its_memories(self):
        self.keep("CONVERSATION", "My sister Odalys visits next week.", "sister_name = Odalys")
        self.keep("TECHNICAL", "The release is due Thursday.", "release_due = Thursday")
        self.engine.orchestrator._process_rem_tick()
        self.engine.cortex.active_mode = "TECHNICAL"
        self.engine.cmd.interface.log = log = MagicMock()
        self.engine.cmd.execute("/memory why reflection.busy_week")
        out = Prisma.strip("\n".join(str(c.args[0]) for c in log.call_args_list))
        self.assertIn("by reflection in REM", out)
        self.assertIn("    From: sister_name, release_due.", out)


class DreamingFromIt(_Sleeper):
    """R3: the dream is built from what the sleep reflected on, not from lore templates."""

    def setUp(self):
        super().setUp()
        self.engine.mind.dreamer.hallucinate = MagicMock(return_value=("a template dream", 0.2))
        self.engine.orchestrator.dream_log.clear()

    def two(self, mode="CONVERSATION"):
        self.keep(mode, "My sister Odalys visits next week.", "sister_name = Odalys, visiting next week")
        self.keep(mode, "The release is due Thursday.", "release_due = Thursday")

    def dream_receipts(self):
        from engine.receipts import ReceiptLedger

        return ReceiptLedger.get_instance().for_subsystem("halcyon.dream")

    def test_a_sleep_dreams_from_what_it_reflected_on(self):
        self.two()
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(list(self.engine.orchestrator.dream_log), [f"  • {self.dreams}"])
        self.assertIn("- your sister visits while a release is due, and you care about both (felt ", self.dream_prompts[0])
        self.assertNotIn("heavy trauma", self.dream_prompts[0])
        self.assertNotIn("Odalys, visiting next week", self.dream_prompts[0])  # the meaning, not the raw memories
        self.assertEqual(self.engine.store.record("rem.last_dream")["text"], self.dreams)
        self.assertEqual(self.dream_receipts()[-1].effect, "DREAMT")
        self.engine.mind.dreamer.hallucinate.assert_not_called()

    def test_nothing_new_means_no_dream(self):
        self.two()
        self.engine.orchestrator._process_rem_tick()
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual((len(self.dream_prompts), len(self.engine.orchestrator.dream_log)), (1, 1))

    def test_heavy_trauma_turns_it_into_a_fever_dream(self):
        self.two()
        self.engine.trauma_accum = {"SEPTIC": 0.8}
        self.engine.orchestrator._process_rem_tick()
        self.assertIn("let the dream turn strange and unsettled", self.dream_prompts[0])
        self.assertEqual(list(self.engine.orchestrator.dream_log), [f"  • Fever Dream: {self.dreams}"])
        self.assertEqual(self.dream_receipts()[-1].effect, "FEVER")

    def test_its_voice_keeps_the_firewall(self):
        self.dreams = "The trail climbs \u2014 the notes blow away."
        self.two()
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(self.engine.store.record("rem.last_dream")["text"], "The trail climbs, the notes blow away.")

    def test_the_story_is_dreamt_only_in_the_story(self):
        self.two("ADVENTURE")
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(self.dream_prompts, [])
        self.engine.cortex.active_mode = "ADVENTURE"
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(len(self.dream_prompts), 1)

    def test_a_failed_dream_tries_again(self):
        self.two()
        self.dreams = RuntimeError("down")
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(self.dream_receipts()[-1].effect, "FAILED")
        self.dreams = "The trail again."
        self.engine.orchestrator._process_rem_tick()
        self.assertEqual(list(self.engine.orchestrator.dream_log), ["  • The trail again."])

    def test_sleep_and_idle_show_the_dream_now(self):
        self.two()
        out = self.engine.orchestrator.run_turn("/sleep")["ui"]
        self.assertIn(self.dreams, out)
        self.keep("CONVERSATION", "I'm allergic to cashews.", "allergy = cashews")
        self.keep("CONVERSATION", "My dog is Brisket.", "pet_name = Brisket")
        self.reflects = "care_list = cashews to avoid, and Brisket to walk"
        self.dreams = "The mountain folds into a calendar."
        self.engine.cmd.interface.log = log = MagicMock()
        self.engine.cmd.execute("/idle")
        self.assertIn("The mountain folds into a calendar.", "\n".join(str(c.args[0]) for c in log.call_args_list))
