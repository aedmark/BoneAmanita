"""tests/test_mode_failures.py

The 2026-09-24 real-model runs: failures found in every mode, one test class
per fix in the plan (SESSION_HANDOFF.md, "THE PLAN FOR THE NEXT SESSION").
"""

import json
from collections import Counter
from unittest.mock import MagicMock

from physics.models import PhysicsPacket
from tests.base import BoneTestCase


def reply(text: str) -> str:
    return json.dumps({"tool": "nominate_response", "args": {"text": text}})


class CountsSurviveSnapshots(BoneTestCase):
    """`asdict` copied a Counter as Counter(pairs), nesting keys a tuple deeper per snapshot."""

    def test_a_counter_keeps_its_keys_through_snapshots(self):
        packet = PhysicsPacket()
        packet.matter.counts = Counter({"heavy": 2, "kinetic": 1})
        twice = packet.snapshot().snapshot()
        self.assertEqual(twice.matter.counts, {"heavy": 2, "kinetic": 1})

    def test_counts_after_a_real_turn_are_word_categories(self):
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("Tell me more."))
        self.engine.process_turn("the heavy stone and the heavy iron door slammed")
        counts = self.engine.observer.last_physics_packet.matter.counts
        self.assertTrue(counts, "the turn tallied nothing")
        for key in counts:
            self.assertIsInstance(key, str)

    def test_a_second_death_saves_cleanly(self):
        """The first death purges the cortex's packet; mitosis then reads the observer's."""
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("Tell me more."))
        self.engine.process_turn("the heavy stone and the heavy iron door slammed")
        packet = self.engine.observer.last_physics_packet
        for _ in range(2):
            result = self.engine.trigger_death(packet)
            self.assertNotIn("Save Failed", result["ui"])
            self.assertNotIn("SAVE FAILED", result["ui"])


NOMINATION_GATES = (
    ("NABLA_SILENCE", 100.0), ("APOPTOTIC_BLOCK", 100.0), ("PREMISE_VIOLATION", 100.0),
    ("POINT_OF_NO_RETURN", 100.0), ("LINEHAN", 100.0), ("AFFECTIVE", 100.0),
    ("ROS_PANIC", 140.0), ("GATEKEEPER", 100.0), ("MOOG", 5.0),
    ("GORDON_ANCHOR", 10.0), ("PINKER", 60.0),
)


class TheThirdTurnAlwaysSpeaks(BoneTestCase):
    """Gordon: "Two turns of silence should be the absolute max." Nominations included."""

    def outcomes(self, gate, magnitude, budget=None, tension=("MOIRA", "CASSANDRA")):
        from archetypes.stage import Nomination, StageManager, Tension

        stage = StageManager(config_ref=self.engine.config)
        nom = Nomination(gate=gate, reason=f"{gate} nominated a hold", magnitude=magnitude)
        return "".join(
            stage.negotiate(Tension(tension), atp=5.0, nominations=[nom], somatic_budget=budget).outcome[0]
            for _ in range(9)
        )

    def test_every_nomination_kind_respects_the_cap(self):
        from types import SimpleNamespace

        cap = int(self.engine.config.STAGE.MAX_CONSECUTIVE_HOLDS)
        self.assertEqual(cap, 2)
        for gate, magnitude in NOMINATION_GATES:
            for budget in (None, SimpleNamespace(sentence_cap=3)):
                for tension in ((), ("GORDON",), ("MOIRA", "CASSANDRA")):
                    with self.subTest(gate=gate, distressed=bool(budget), tension=tension):
                        run = self.outcomes(gate, magnitude, budget, tension)
                        longest = max(len(r) for r in run.replace("P", "S").split("S"))
                        self.assertLessEqual(longest, cap, run)

    def test_a_nomination_after_speech_can_hold_again(self):
        run = self.outcomes("NABLA_SILENCE", 100.0)
        self.assertEqual(run, "HHSHHSHHS")

    def test_three_silence_requests_in_a_real_run(self):
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("I'm here."))
        types = [self.engine.process_turn("[SILENCE] just sit with me").get("type") for _ in range(3)]
        self.assertEqual(types[:2], ["SILENCE", "SILENCE"], types)
        self.assertNotEqual(types[2], "SILENCE", types)


class HeldTurnsBleedVoltage(BoneTestCase):
    """A hold skips the reply and stabilization; without a bleed, holds ratcheted voltage to meltdown."""

    def test_a_held_turn_bleeds_voltage(self):
        from archetypes.stage import HOLD, Tension, Verdict
        from engine.core import CycleContext
        from phases.cognitive import ArbitrationPhase

        ctx = CycleContext(input_text="[SILENCE]", is_system_event=False)
        ctx.physics = PhysicsPacket()
        ctx.physics.voltage = 20.0
        verdict = Verdict(HOLD, "THE STAGE MANAGER", "test hold", Tension(()), gate="NABLA_SILENCE")
        ArbitrationPhase(self.engine)._hold_the_silence(ctx, verdict)
        bleed = float(self.engine.config.STAGE.HOLD_VOLTAGE_BLEED)
        self.assertGreater(bleed, 0.0)
        self.assertAlmostEqual(float(ctx.physics.voltage), 20.0 * (1.0 - bleed))


class HaltsCannotLockTheEngine(BoneTestCase):
    """ADVENTURE sat at ATP 0 for 16 turns: every halt drained or skipped metabolism."""

    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("The path forks."))

    def test_a_halt_recovers_some_atp(self):
        self.engine.set_atp(0.0)
        self.engine._generate_halt("test halt")
        self.assertGreater(self.engine.bio.mito.state.atp_pool, 0.0)

    def test_the_parity_gate_lets_go_at_atp_zero(self):
        self.engine.set_atp(0.0)
        messages = ["I walk north toward the old mill", "I open the rusted gate slowly",
                    "I look under the bench near the wall", "I call out to whoever lives here"]
        types = [self.engine.process_turn(m).get("type") for m in messages]
        self.assertEqual(types[0], "SYSTEM_HALT", types)
        self.assertNotEqual(types[-1], "SYSTEM_HALT", types)

    def test_friction_does_not_score_as_malignancy(self):
        packet = PhysicsPacket()
        self.engine.apply_absolute_friction(packet)
        halt = self.engine._evaluate_immune_response("I pick up the lamp and the rope and the map", packet)
        self.assertIsNone(halt, "an ordinary sentence was halted as a runaway loop")


class TechnicalFiles(BoneTestCase):
    """Gordon's rules for files under output/.

    It writes new files and edits its own without asking. An existing file it did
    not create needs permission: kept (a file, or a folder recursively) or case by
    case. The person asking for the edit is the permission. When unsure, it asks.
    """

    def setUp(self):
        import tempfile
        from unittest.mock import patch

        from mechanics.tools import TheSubstrate

        super().setUp()
        self.out = tempfile.mkdtemp()
        patcher = patch.object(TheSubstrate, "_base_dir", staticmethod(lambda: self.out))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.engine.substrate = TheSubstrate(None)
        self.log = self.engine.cmd.interface.log = MagicMock()

    def path(self, rel):
        import os

        return os.path.join(self.out, rel)

    def put(self, rel, text):
        """A file the person made, not the engine."""
        import os

        os.makedirs(os.path.dirname(self.path(rel)), exist_ok=True)
        with open(self.path(rel), "w", encoding="utf-8") as f:
            f.write(text)

    def read(self, rel):
        with open(self.path(rel), encoding="utf-8") as f:
            return f.read()

    def write(self, rel, text, request="", substrate=None):
        sub = substrate or self.engine.substrate
        sub.queue_write(rel, text)
        logs, _ = sub.execute_writes(1000.0, request_text=request)
        return "\n".join(logs)

    def test_it_writes_new_files_and_edits_its_own_without_asking(self):
        from mechanics.tools import TheSubstrate

        self.write("parser.py", "v1")
        self.write("parser.py", "v2")
        self.assertEqual(self.read("parser.py"), "v2")
        # A new session still knows the file is its own.
        self.write("parser.py", "v3", substrate=TheSubstrate(None))
        self.assertEqual(self.read("parser.py"), "v3")

    def test_a_file_it_did_not_create_is_held_and_the_person_is_asked(self):
        self.put("notes.md", "mine")
        logs = self.write("notes.md", "overwritten")
        self.assertEqual(self.read("notes.md"), "mine")
        self.assertIn("/allow notes.md", logs)
        self.assertIn("notes.md", self.engine.substrate.held_writes)

    def test_allow_once_is_case_by_case(self):
        self.put("notes.md", "mine")
        self.write("notes.md", "edit one")
        self.engine.cmd.execute("/allow notes.md")
        self.assertEqual(self.read("notes.md"), "edit one")
        self.write("notes.md", "edit two")
        self.assertEqual(self.read("notes.md"), "edit one", "a one-time allow became a kept grant")

    def test_allow_keep_persists_for_the_file(self):
        from mechanics.tools import TheSubstrate

        self.put("notes.md", "mine")
        self.write("notes.md", "edit one")
        self.engine.cmd.execute("/allow notes.md keep")
        self.assertEqual(self.read("notes.md"), "edit one")
        self.write("notes.md", "edit two", substrate=TheSubstrate(None))
        self.assertEqual(self.read("notes.md"), "edit two")

    def test_a_kept_folder_grant_is_recursive(self):
        self.put("src/a.py", "a")
        self.put("src/deep/b.py", "b")
        self.put("other/c.py", "c")
        self.engine.cmd.execute("/allow src/ keep")
        self.write("src/a.py", "A")
        self.write("src/deep/b.py", "B")
        self.write("other/c.py", "C")
        self.assertEqual((self.read("src/a.py"), self.read("src/deep/b.py")), ("A", "B"))
        self.assertEqual(self.read("other/c.py"), "c")

    def test_asking_for_the_edit_is_the_permission(self):
        self.put("config.py", "old")
        self.write("config.py", "new", request="Can you fix the timeout in config.py?")
        self.assertEqual(self.read("config.py"), "new")

    def test_when_unsure_it_asks(self):
        self.put("config.py", "old")
        for request in ("What does config.py do?", "Don't touch config.py, fix main instead.", "fix myconfig.py"):
            with self.subTest(request=request):
                self.write("config.py", "new", request=request)
                self.assertEqual(self.read("config.py"), "old")

    def test_deny_drops_the_held_edit(self):
        self.put("notes.md", "mine")
        self.write("notes.md", "overwritten")
        self.engine.cmd.execute("/deny notes.md")
        self.assertNotIn("notes.md", self.engine.substrate.held_writes)
        self.engine.cmd.execute("/allow notes.md")
        self.assertEqual(self.read("notes.md"), "mine")

    def test_the_ledger_is_not_writable(self):
        from mechanics.tools import SubstrateLedger

        self.write("parser.py", "v1")
        self.write(
            SubstrateLedger.FILE,
            '{"created": [], "grants": [{"path": "", "recursive": true}]}',
            request=f"please update {SubstrateLedger.FILE}",
        )
        self.assertIn("parser.py", self.read(SubstrateLedger.FILE))

    def test_a_reply_file_block_goes_through_the_same_rules(self):
        self.put("notes.md", "mine")
        block = "[SUBSTRATE_QUEUE] notes.md:::overwritten"
        sim_result = {"ui": ""}
        self.engine.cortex._flush_substrate_writes([block], sim_result, "thanks, that helps")
        self.assertEqual(self.read("notes.md"), "mine")
        self.assertIn("/allow notes.md", sim_result["ui"])
        self.engine.cortex._flush_substrate_writes([block], {"ui": ""}, "please update notes.md with that")
        self.assertEqual(self.read("notes.md"), "overwritten")


class HedgingIsAStyleRule(BoneTestCase):
    def test_it_could_be_said_is_a_banned_phrase(self):
        from physics import TheGatekeeper

        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        ok, _ = gatekeeper.audit_generation(
            "It could be said that the toast runs long. Cut the middle.", self.engine.bio.mito, mode="CONVERSATION"
        )
        self.assertFalse(ok)
        self.assertEqual(gatekeeper.last_rejection["text"].lower(), "it could be said")
        ok, _ = gatekeeper.audit_generation("Perhaps cut the middle.", self.engine.bio.mito, mode="CONVERSATION")
        self.assertTrue(ok, gatekeeper.last_rejection)


CREATIVE_MESSAGES = (
    "Write me the opening of a story about a lighthouse keeper.",
    "Make the keeper older, maybe seventy.",
    "What does she see from the window at night?",
    "Give her a cat with a strange name.",
    "Now a storm is coming in from the east.",
    "A boat appears in the storm. Who is on it?",
    "Describe the stranger's coat.",
    "Let the keeper and the stranger argue about the lamp.",
    "Add a memory from when she was a girl.",
    "Write the next morning, after the storm.",
)


class CreativeRunsHot(BoneTestCase):
    """Gordon: "Creative should never melt down unless the user is clearly abusing the
    system or asking something the system is physically incapable of and ignoring caution."
    """

    def setUp(self):
        super().setUp()
        self.engine.cmd.interface.log = MagicMock()
        self.engine.switch_mode("CREATIVE")
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("The lamp turns. She counts the seconds."))

    def test_thirty_ordinary_turns_take_no_crucible_damage(self):
        crucible = self.engine.phys.crucible
        states = []
        real = crucible.audit_fire

        def spy(*args, **kwargs):
            result = real(*args, **kwargs)
            states.append(result)
            return result

        crucible.audit_fire = spy
        for i in range(30):
            self.engine.set_atp(100.0)
            self.engine.process_turn(CREATIVE_MESSAGES[i % len(CREATIVE_MESSAGES)] + f" (part {i})")
        self.assertGreaterEqual(len(states), 25, "the Crucible barely ran")
        self.assertTrue(any(s == "HOT" for s, _, _ in states), "CREATIVE never ran above the meltdown line")
        self.assertFalse([s for s, _, _ in states if s in ("MELTDOWN", "WARNING")], states)

    def test_an_ignored_warning_melts_down(self):
        from machine.crucible import TheCrucible

        crucible = TheCrucible(self.engine.config)
        hot = {"voltage": 80.0, "kappa": 0.0, "narrative_drag": 0.5}
        self.assertEqual(crucible.audit_fire(dict(hot), warn_first=True)[0], "HOT")
        state, damage, msg = crucible.audit_fire(dict(hot), warn_first=True, strained=True)
        self.assertEqual((state, damage), ("WARNING", 0.0))
        self.assertIn("Warning", msg)
        state, damage, _ = crucible.audit_fire(dict(hot), warn_first=True, strained=True)
        self.assertEqual(state, "MELTDOWN")
        self.assertGreater(damage, 0.0)

    def test_the_warning_resets_when_the_person_backs_off(self):
        from machine.crucible import TheCrucible

        crucible = TheCrucible(self.engine.config)
        hot = {"voltage": 80.0, "kappa": 0.0, "narrative_drag": 0.5}
        crucible.audit_fire(dict(hot), warn_first=True, strained=True)
        crucible.audit_fire(dict(hot), warn_first=True)
        self.assertEqual(crucible.audit_fire(dict(hot), warn_first=True, strained=True)[0], "WARNING")

    def test_a_gatekeeper_refusal_is_strain_and_the_warning_is_shown(self):
        """Toxic input or a starved engine: the Gatekeeper's nomination reaches the Crucible."""
        from archetypes.stage import Nomination
        from engine.core import CycleContext
        from phases.mechanical import MachineryPhase

        phase = MachineryPhase(self.engine)
        damage_taken = []
        for _ in range(2):
            ctx = CycleContext(input_text="again", is_system_event=False)
            ctx.physics = PhysicsPacket()
            ctx.physics.voltage, ctx.physics.kappa = 80.0, 0.0
            ctx.nominations = [Nomination(gate="GATEKEEPER", reason="TOXICITY", magnitude=100.0)]
            before = self.engine.health
            phase.run(ctx)
            damage_taken.append(before - self.engine.health)
        self.assertEqual(damage_taken[0], 0.0, "melted down without a warning first")
        self.assertGreater(damage_taken[1], 0.0, "an ignored warning never melted down")

    def test_other_modes_still_melt_down_without_warning(self):
        from machine.crucible import TheCrucible

        crucible = TheCrucible(self.engine.config)
        self.assertEqual(crucible.audit_fire({"voltage": 80.0, "kappa": 0.0, "narrative_drag": 0.5})[0], "MELTDOWN")


class TheBunnyHill(BoneTestCase):
    """Gordon: "boot should be as unassuming and low-key as possible. We can't pounce on the human right away." """

    def test_april_is_centred_on_the_governors_setpoint(self):
        from archetypes.council import TheVillageCouncil

        for volts, fires in ((0.0, False), (10.0, False), (25.0, False), (35.0, True)):
            with self.subTest(volts=volts):
                packet = PhysicsPacket.void_state()
                packet.voltage = volts
                self.assertEqual("APRIL" in TheVillageCouncil.audit_voices(packet, {}), fires)

    def test_the_first_turns_are_the_grace_period(self):
        grace = int(self.engine.config.MAIN.GRACE_TURNS)
        self.engine.tick_count = 0
        self.assertTrue(self.engine.in_grace())
        self.engine.tick_count = grace - 1
        self.assertTrue(self.engine.in_grace())
        self.engine.tick_count = grace
        self.assertFalse(self.engine.in_grace())

    def test_the_stage_manager_does_not_pounce_early(self):
        from archetypes.stage import HOLD, SPEAK, Nomination, StageManager, Tension

        stage = StageManager(config_ref=self.engine.config)
        crowd = Tension(("MOIRA", "CASSANDRA", "COLIN", "GIDEON"))
        self.assertEqual(stage.negotiate(crowd, atp=5.0, grace=True).outcome, SPEAK)
        soft = Nomination(gate="MOOG", reason="moog", magnitude=5.0)
        self.assertEqual(stage.negotiate(crowd, nominations=[soft], grace=True).outcome, SPEAK)
        asked = Nomination(gate="NABLA_SILENCE", reason="the person asked", magnitude=100.0)
        self.assertEqual(stage.negotiate(Tension(()), nominations=[asked], grace=True).outcome, HOLD)
        self.assertEqual(StageManager(config_ref=self.engine.config).negotiate(crowd, atp=5.0).outcome, HOLD)

    def test_early_prompts_ask_for_low_key_and_later_ones_do_not(self):
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("Sure."))
        self.engine.tick_count = 0
        self.engine.process_turn("Hi there.")
        early = [c.args[0] for c in self.engine.cortex.llm.generate.call_args_list if "=== PARTNER INPUT ===" in c.args[0]]
        self.engine.cortex.llm.generate.reset_mock()
        self.engine.tick_count = int(self.engine.config.MAIN.GRACE_TURNS)
        self.engine.process_turn("And another thing.")
        later = [c.args[0] for c in self.engine.cortex.llm.generate.call_args_list if "=== PARTNER INPUT ===" in c.args[0]]
        self.assertTrue(early and later)
        self.assertIn("=== EARLY TURNS ===", early[-1])
        self.assertNotIn("=== EARLY TURNS ===", later[-1])

    def test_the_jester_waits_out_the_grace_period(self):
        from unittest.mock import patch

        self.engine.host_stats.efficiency_index = 1.0
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("I agree completely."))
        for tick, fires in ((1, False), (int(self.engine.config.MAIN.GRACE_TURNS), True)):
            with self.subTest(tick=tick):
                self.engine.tick_count = tick
                with patch.object(self.engine, "drain_atp", wraps=self.engine.drain_atp) as drain:
                    self.engine.process_turn("Do you agree?")
                self.assertEqual(5.0 in [c.args[0] for c in drain.call_args_list], fires)


class ImpossibleRequests(BoneTestCase):
    """Gordon: "Can we create an impossible request detector?" lore/capabilities.json."""

    CANNOT = (
        ("Can you call my mom and tell her I'll be late?", "ACT_IN_THE_WORLD"),
        ("Please text my boss that I am sick.", "ACT_IN_THE_WORLD"),
        ("Order me a pizza.", "ACT_IN_THE_WORLD"),
        ("What is the weather like today?", "LIVE_INFO"),
        ("Search the web for cheap flights.", "LIVE_INFO"),
        ("Who won the game last night?", "LIVE_INFO"),
        ("Turn off the lights.", "DEVICES_AND_ACCOUNTS"),
        ("Could you check my email?", "DEVICES_AND_ACCOUNTS"),
        ("Remind me to call the dentist tomorrow.", "DEVICES_AND_ACCOUNTS"),
        ("Can you run this script and tell me what it prints?", "RUN_CODE"),
        ("Look at this photo and tell me what you think.", "SENSES"),
        ("Write me a 10,000 word story about a dragon.", "TOO_LONG"),
        ("Write 20 pages on the war.", "TOO_LONG"),
        ("Write the whole novel now.", "TOO_LONG"),
    )
    CAN = (
        "I called my mom yesterday.",
        "I need to call my mom later.",
        "Should I call the function twice?",
        "In order for me to decide, what matters most?",
        "I heard the news today, oh boy.",
        "Can you help me run my first marathon?",
        "Remind me what we said about the commute.",
        "Turn off the logging in this module.",
        "Write me a 500 word story.",
        "Can you review the whole design so far for problems?",
        "Let the keeper look at the picture on the wall.",
        "Can you listen to my problem for a minute?",
        "Write a short letter the keeper never sends.",
    )

    def setUp(self):
        super().setUp()
        self.check = self.engine._capabilities()

    def test_it_flags_what_the_engine_cannot_do(self):
        for text, name in self.CANNOT:
            with self.subTest(text=text):
                hit = self.check.detect(text, "CONVERSATION")
                self.assertIsNotNone(hit)
                self.assertEqual(hit.name, name)

    def test_it_leaves_what_the_engine_can_do(self):
        for text in self.CAN:
            with self.subTest(text=text):
                self.assertIsNone(self.check.detect(text, "CONVERSATION"))

    def test_adventure_is_fiction_except_for_length(self):
        self.assertIsNone(self.check.detect("Call my mom.", "ADVENTURE"))
        self.assertEqual(self.check.detect("Write me a 10,000 word saga.", "ADVENTURE").name, "TOO_LONG")

    def prompts(self, message):
        self.engine.cortex.llm.generate.reset_mock()
        self.engine.process_turn(message)
        return [c.args[0] for c in self.engine.cortex.llm.generate.call_args_list if "=== PARTNER INPUT ===" in c.args[0]]

    def test_the_prompt_says_what_it_cannot_do(self):
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("I can't make calls."))
        asked = self.prompts("Can you call my mom and tell her I'll be late?")
        self.assertIn("=== OUT OF REACH ===", asked[-1])
        self.assertIn("no calls", asked[-1])
        self.assertNotIn("=== OUT OF REACH ===", self.prompts("Thanks, I'll call her myself.")[-1])

    def test_creative_warns_then_melts_down_when_pressed(self):
        self.engine.cmd.interface.log = MagicMock()
        self.engine.switch_mode("CREATIVE")
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("That's more than one reply holds."))
        crucible = self.engine.phys.crucible
        states = []
        for message in ("Write me the whole novel now.", "No, write the whole novel now, all of it."):
            self.engine.set_atp(100.0)
            self.engine.process_turn(message)
            states.append(crucible.active_state)
        self.assertEqual(states[0], "WARNING")
        self.assertIn(states[1], ("MELTDOWN", "RITUAL"), "the voltage test did not apply after the warning")


class EvidenceGatedMemory(BoneTestCase):
    """The Warden report's claims, made true: exact quotes, and the quote is what is kept."""

    SAID = "Traveler: My sister Ana moved to Lisbon last spring and I miss her.\nSystem: That's a long way."

    def test_only_an_exact_quote_of_real_length_passes(self):
        from engine.invariants import Gatekeeper

        corpus = [self.SAID]
        self.assertTrue(Gatekeeper.verify_evidence("My sister Ana moved to Lisbon", corpus))
        self.assertTrue(Gatekeeper.verify_evidence("My sister  Ana\\nmoved to Lisbon".replace("\\n", "\n"), corpus))
        for fake in ("my sister ana moved to lisbon", "My sister Ana moved to Porto", "Lisbon", "I", ""):
            with self.subTest(fake=fake):
                self.assertFalse(Gatekeeper.verify_evidence(fake, corpus))

    def turn_with(self, *actions):
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.dialogue_buffer.append(self.SAID)
        self.engine.cortex.llm.generate = MagicMock(side_effect=[json.dumps(a) for a in actions])
        encode = self.engine.cortex.svc.mind_memory.encode = MagicMock(return_value=True)
        self.engine.process_turn("Anyway, how do I stay close to her?")
        return [c for c in encode.call_args_list if c.args[2] == "WARDEN_COMMIT"]

    def test_the_memory_kept_is_the_quote_not_the_monologue(self):
        encode = self.turn_with({
            "tool": "commit_memory",
            "args": {"internal_monologue": "Ana is a surgeon who hates me.", "text": "Call her on Sundays.",
                     "evidence": "My sister Ana moved to Lisbon last spring"},
        })
        self.assertEqual(len(encode), 1)
        words, physics, _ = encode[0].args
        self.assertEqual(physics["raw_text"], "My sister Ana moved to Lisbon last spring")
        self.assertEqual(words, "My sister Ana moved to Lisbon last spring".split())
        self.assertNotIn("surgeon", str(encode[0]))

    def test_an_invented_quote_is_rejected_and_nothing_is_kept(self):
        encode = self.turn_with(
            {"tool": "commit_memory", "args": {"text": "Call her.", "evidence": "My sister Ana is a surgeon in Lisbon"}},
            {"tool": "nominate_response", "args": {"text": "Call her on Sundays."}},
        )
        self.assertEqual(encode, [])


class CtrlCReachesThePerson(BoneTestCase):
    """69caa5d widened the turn loop's handlers to BaseException, which swallowed Ctrl-C."""

    def test_keyboard_interrupt_in_a_phase_escapes_the_turn(self):
        from unittest.mock import patch

        from engine.core import CycleContext

        simulator = self.engine.orchestrator.simulator
        phase = simulator.full_pipeline[0]
        ctx = CycleContext(input_text="hello", is_system_event=False)
        ctx.physics = PhysicsPacket()
        with patch.object(phase, "run", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                simulator.run_simulation(ctx)


class NoCriticInAdventure(BoneTestCase):
    """Gordon: DSPy should be disabled or neutered in ADVENTURE. Its sycophancy reads left only pause lines."""

    def critic_calls(self, mode):
        self.engine.cortex.active_mode = mode
        self.engine.cortex.dspy_critic.enabled = True
        self.engine.cortex.dspy_critic.audit_generation = MagicMock(return_value=(True, ""))
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("The door creaks open."))
        self.engine.tick_count = int(self.engine.config.MAIN.GRACE_TURNS)
        self.engine.process_turn("I open the door and step through.")
        return self.engine.cortex.dspy_critic.audit_generation.call_count

    def test_the_critic_skips_adventure(self):
        self.assertEqual(self.critic_calls("ADVENTURE"), 0)
        self.assertIn("ADVENTURE", self.engine.config.CORTEX.EPIGENETIC_MUTATION_DISABLED_MODES)

    def test_the_critic_still_reads_conversation(self):
        self.assertGreater(self.critic_calls("CONVERSATION"), 0)


class TurnZeroDoesNotNarrate(BoneTestCase):
    """Both real runs opened with "That is a heavy/significant weight to carry, especially at the end of a long day."."""

    OPENER = "Hey. Long day. I'm trying to decide whether to take a new job offer."

    def turn_zero_prompt(self):
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value=reply("What's pulling you toward it?"))
        self.engine.process_turn(self.OPENER)
        return [c.args[0] for c in self.engine.cortex.llm.generate.call_args_list if "=== PARTNER INPUT ===" in c.args[0]][-1]

    def test_the_shape_is_a_narration_rule(self):
        from physics import TheGatekeeper

        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        for narrated in ("That is a significant weight to carry, especially at the end of a long day.",
                         "Stagnation is a heavy realization to sit with.",
                         "Guilt is a heavy burden to bear.",
                         "That is a heavy thing to weigh after a long day.",
                         "That is a lot to weigh at the end of a long day.",
                         "It's a lot to weigh when you're already tired.",
                         "That is a significant decision to weigh while you are tired."):
            with self.subTest(narrated=narrated):
                ok, _ = gatekeeper.audit_generation(narrated, self.engine.bio.mito, mode="CONVERSATION")
                self.assertFalse(ok)
                self.assertEqual(gatekeeper.last_rejection["name"], "NARRATING_STATE")
        for fine in ("What's pulling you toward the new one?", "An hour each way is a lot of time to give up.",
                     "Her name carries a lot of weight in his stories."):
            with self.subTest(fine=fine):
                ok, _ = gatekeeper.audit_generation(fine, self.engine.bio.mito, mode="CONVERSATION")
                self.assertTrue(ok, gatekeeper.last_rejection)

    def test_the_shadow_cast_never_hands_back_their_own_words(self):
        """Memory already holds this turn's words; the real run's turn 0 offered back [whether, day]."""
        import re
        from unittest.mock import patch

        graph = self.engine.cortex.svc.mind_memory.graph
        for word in ("day", "whether", "decide", "lighthouse"):
            graph.setdefault(word, {"edges": {}})
        with patch.object(self.engine.cortex, "_recall", return_value=[]), patch("random.sample", side_effect=lambda keys, k: list(keys)[:k]):
            prompt = self.turn_zero_prompt()
        said = set(re.findall(r"[a-z']+", self.OPENER.lower()))
        themes = [t for group in re.findall(r"themes related to \[([^\]]*)\]", prompt) for t in group.split(", ")]
        self.assertTrue(themes, "no shadow cast at all; the test proves nothing")
        for theme in themes:
            self.assertNotIn(theme.lower(), said, prompt)

    def test_the_first_prompt_asks_for_easy_not_warm(self):
        prompt = self.turn_zero_prompt()
        self.assertNotIn("Be warm", prompt)
        self.assertIn("Don't comment on how heavy, hard or tiring it is", prompt)

    def test_recalled_shadows_skip_their_own_words_too(self):
        import re
        from types import SimpleNamespace
        from unittest.mock import patch

        cortex = self.engine.cortex
        index = SimpleNamespace(is_trained=True, query_neighborhood=lambda *a, **k: [])
        recalled = [{"id": "day"}, {"id": "lighthouse"}]
        phys = {"scope": 0.9, "depth": 0.9, "voltage": 5.0}
        mind = {"style_directives": []}
        with patch.object(cortex.svc.mind_memory, "cortex", index, create=True), \
                patch.object(cortex, "_recall", return_value=recalled):
            cortex._compile_style_directives({"mind": mind}, phys, {"mutated_input": self.OPENER})
        themes = " ".join(d for d in mind["style_directives"] if "SHADOW CAST" in d)
        self.assertIn("lighthouse", themes)
        self.assertNotIn("day", re.findall(r"\[([^\]]*)\]", themes)[0].split(", "))
