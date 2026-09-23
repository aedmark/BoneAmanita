"""tests/test_stage_manager.py

ROADMAP C4. The Stage Manager, Tension as a state, and Silence as an outcome.

The distinctive claim in the whole design is that this engine can decline to
answer until the person brings more structure or more energy. Before this it
could not: `ArbitrationPhase` was able to name the lens THE STAGE MANAGER and
log that the cosmos was holding its breath, and then the engine generated a
paragraph anyway. Silence was a label on a turn that spoke.

Two things these tests are careful about.

A refusal to speak that cannot say why is indistinguishable from a fault, so
every verdict carries a reason and the tests assert on it. And an engine that
can always decline eventually always will, so the hold cap is tested as
load-bearing rather than decorative.
"""

import json
import unittest
from unittest.mock import patch

from archetypes.stage import HOLD, PAIR, SPEAK, StageManager, Tension
from tests.base import BoneTestCase


def _synergy_map():
    with open("lore/council_data.json", encoding="utf-8") as handle:
        return json.load(handle)["SYNERGY_MAP"]


class TestTensionIsAState(unittest.TestCase):
    """One voice is a voice. Two is Tension."""

    def test_an_empty_room_is_not_tense(self):
        self.assertFalse(Tension(()).is_tense)
        self.assertEqual(Tension(()).magnitude, 0)

    def test_one_voice_is_not_tense(self):
        self.assertFalse(Tension(("GORDON",)).is_tense)
        self.assertEqual(Tension(("GORDON",)).magnitude, 0)

    def test_two_voices_are(self):
        tension = Tension(("GORDON", "JESTER"))
        self.assertTrue(tension.is_tense)
        self.assertEqual(tension.magnitude, 1)
        self.assertIn("GORDON vs JESTER", str(tension))

    def test_the_council_reports_voices_not_just_prose(self):
        """`audit` flattened the triggers into log strings and kept nothing else.

        It also had no production caller at all, so the one function that knew
        which voices had fired was dead code.
        """
        from archetypes.council import TheVillageCouncil
        from physics.models import PhysicsPacket

        packet = PhysicsPacket.void_state()
        self.assertEqual(TheVillageCouncil.audit_voices(packet, {}), ())

        packet.psi, packet.chi, packet.valence = 0.8, 0.7, 0.7
        voices = TheVillageCouncil.audit_voices(packet, {})
        self.assertGreater(len(voices), 1)
        self.assertEqual(len(voices), len(set(voices)), "a voice was counted twice")
        # The prose path still works for everyone already reading it.
        self.assertTrue(TheVillageCouncil.audit(packet, {}))


class TestNegotiation(unittest.TestCase):
    def setUp(self):
        self.stage = StageManager(synergy_map=_synergy_map())

    def test_quiet_rooms_and_single_voices_just_speak(self):
        self.assertEqual(self.stage.negotiate(Tension(())).outcome, SPEAK)
        verdict = self.stage.negotiate(Tension(("GORDON",)))
        self.assertEqual(verdict.outcome, SPEAK)
        self.assertEqual(verdict.voice, "GORDON")

    def test_a_fusion_pair_resolves_tension_rather_than_suppressing_it(self):
        verdict = self.stage.negotiate(Tension(("GORDON", "MERCY")))
        self.assertEqual(verdict.outcome, PAIR)
        self.assertEqual(verdict.voice, "THE RETROACTIVE STRATIGRAPHER")
        self.assertTrue(verdict.adjustments, "the fusion carried no physics")

    def test_pairing_searches_both_orderings(self):
        """`GORDON|MERCY` is in the map; `MERCY|GORDON` is not."""
        verdict = self.stage.negotiate(Tension(("MERCY", "GORDON")))
        self.assertEqual(verdict.outcome, PAIR)

    def test_pairing_searches_every_combination_in_the_room(self):
        """Not just the first two. A lookup that happens to hit is not a choice."""
        verdict = self.stage.negotiate(Tension(("CASPER", "CASSANDRA", "ROBERTA")))
        self.assertEqual(verdict.outcome, PAIR)
        self.assertEqual(verdict.voice, "THE DOPPELGÄNGER FACTORY")

    def test_no_energy_to_reconcile_means_silence(self):
        verdict = self.stage.negotiate(Tension(("MOIRA", "CASSANDRA")), atp=5.0)
        self.assertEqual(verdict.outcome, HOLD)
        self.assertIn("ATP", verdict.reason)

    def test_too_many_unfused_voices_means_silence(self):
        verdict = self.stage.negotiate(
            Tension(("MOIRA", "CASSANDRA", "COLIN", "GIDEON")), atp=100.0
        )
        self.assertEqual(verdict.outcome, HOLD)

    def test_pairing_is_tried_before_holding(self):
        """A fusion is a resolution; silence is the admission there is none."""
        verdict = self.stage.negotiate(Tension(("GORDON", "MERCY")), atp=1.0)
        self.assertEqual(verdict.outcome, PAIR)

    def test_the_engine_cannot_go_mute_indefinitely(self):
        """The cap is what keeps Silence considered rather than habitual."""
        tension = Tension(("MOIRA", "CASSANDRA"))
        outcomes = [
            self.stage.negotiate(tension, atp=5.0).outcome for _ in range(6)
        ]
        self.assertIn(SPEAK, outcomes, "the engine held every single turn")
        self.assertLessEqual(
            max(len(run) for run in "".join(
                "H" if o == HOLD else "S" for o in outcomes
            ).split("S")),
            int(self.stage._cfg("MAX_CONSECUTIVE_HOLDS", 2)),
            "held for longer than the configured cap",
        )

    def test_every_verdict_explains_itself(self):
        for tension, atp in (
            (Tension(()), 100.0),
            (Tension(("GORDON",)), 100.0),
            (Tension(("GORDON", "MERCY")), 100.0),
            (Tension(("MOIRA", "CASSANDRA")), 5.0),
        ):
            with self.subTest(tension=str(tension)):
                verdict = StageManager(synergy_map=_synergy_map()).negotiate(
                    tension, atp=atp
                )
                self.assertTrue(
                    verdict.reason.strip(),
                    "a verdict with no reason is indistinguishable from a fault",
                )

    def test_negotiation_is_deterministic(self):
        """The property that makes a refusal auditable rather than a mood."""
        tension = Tension(("MOIRA", "CASSANDRA"))
        first = StageManager(synergy_map=_synergy_map()).negotiate(tension, atp=5.0)
        second = StageManager(synergy_map=_synergy_map()).negotiate(tension, atp=5.0)
        self.assertEqual((first.outcome, first.voice, first.reason),
                         (second.outcome, second.voice, second.reason))


class TestSilenceIsARealOutcome(BoneTestCase):
    """The headline. A held turn must not reach the model at all."""

    def _force_hold(self):
        from archetypes.stage import Verdict

        return Verdict(
            HOLD,
            "THE STAGE MANAGER",
            "MOIRA vs CASSANDRA and only 5 ATP to reconcile them",
            Tension(("MOIRA", "CASSANDRA")),
            gate="ATP_FLOOR",
        )

    def _run_held_turn(self):
        with patch.object(StageManager, "negotiate", return_value=self._force_hold()):
            with patch.object(
                self.engine.cortex.llm, "generate", return_value="I should not exist."
            ) as generate:
                result = self.engine.process_turn("say something about all this")
        return result, generate

    def test_the_model_is_never_called(self):
        result, generate = self._run_held_turn()
        generate.assert_not_called()
        self.assertNotIn("I should not exist", str(result.get("ui", "")))

    def test_the_turn_is_typed_as_silence(self):
        result, _ = self._run_held_turn()
        self.assertEqual(result.get("type"), "SILENCE")

    def test_silence_does_not_read_as_a_failure(self):
        """It must be tellable from a crash or a rejection, in telemetry too."""
        result, _ = self._run_held_turn()
        self.assertTrue(result.get("is_alive"), "silence was reported as death")
        self.assertTrue(result.get("is_silence"))
        self.assertNotEqual(result.get("type"), "COUNTERFACTUAL_REJECTION")
        self.assertNotEqual(result.get("type"), "SYSTEM_HALT")

    def test_the_held_turn_names_the_voices_that_could_not_be_reconciled(self):
        result, _ = self._run_held_turn()
        self.assertEqual(sorted(result.get("tension", [])), ["CASSANDRA", "MOIRA"])

    def test_the_ui_text_explains_why(self):
        """The reason was always logged internally; the person reading the
        reply never saw it, only the generic 'nothing is ready to be said'
        line. The `ui` field is what actually reaches them, now with a calm,
        gate-specific explanation rather than nothing."""
        result, _ = self._run_held_turn()
        self.assertIn("not quite enough left in me", result.get("ui", ""))

    def test_the_raw_technical_reason_never_reaches_the_ui(self):
        """`verdict.reason` is written for logs and receipts: internal gate
        names, in-universe jargon, phrasing that can read as blaming the
        person's own input ('Cursed syntax detected', 'CURSED_INPUT: ...').
        It must never be the text a person actually reads; the calm
        translation in `lore/ux_strings.json:silence_reasons` is."""
        result, _ = self._run_held_turn()
        self.assertNotIn("MOIRA vs CASSANDRA and only 5 ATP to reconcile them", result.get("ui", ""))
        # The technical reason is still exactly where it was already useful.
        self.assertIn("MOIRA vs CASSANDRA and only 5 ATP to reconcile them", result.get("logs", []))
        self.assertEqual(
            result.get("mind", {}).get("context_msg"),
            "MOIRA vs CASSANDRA and only 5 ATP to reconcile them",
        )

    def test_silence_costs_something_but_not_a_generation(self):
        """Declining to speak is cheap because you did not speak. Not free."""
        before = self.engine.bio.mito.state.atp_pool
        self._run_held_turn()
        spent = before - self.engine.bio.mito.state.atp_pool
        self.assertGreater(spent, 0.0, "silence was free, which makes it the lazy path")

    def test_a_receipt_records_what_the_stage_manager_decided(self):
        from engine.receipts import CORE_SUBSYSTEMS, ReceiptLedger

        self.assertIn("stage.negotiate", CORE_SUBSYSTEMS)
        ledger = ReceiptLedger.get_instance()
        self._run_held_turn()
        receipts = ledger.for_subsystem("stage.negotiate")
        self.assertTrue(receipts, "the Stage Manager decided and reported nothing")
        self.assertEqual(receipts[-1].inputs["outcome"], HOLD)
        self.assertTrue(receipts[-1].detail)

    def test_an_ordinary_turn_still_speaks(self):
        """The half that proves Silence is a gate and not a new default."""
        with patch.object(
            self.engine.cortex.llm, "generate", return_value="A normal reply."
        ) as generate:
            result = self.engine.process_turn("tell me about the forge")
        self.assertNotEqual(result.get("type"), "SILENCE")
        generate.assert_called()


class TestSilenceReasonsAreHumanSafe(unittest.TestCase):
    """A live census found the previous behaviour directly: the person reading
    a held turn saw the gate's own technical reason verbatim, including raw
    internal tags and phrasing that reads as blaming their own input
    ('CURSED_INPUT: The Gatekeeper recoils. Cursed syntax detected.'). Every
    gate a real `Nomination` can carry needs a calm entry in
    `lore/ux_strings.json:silence_reasons`, and the two crisis-adjacent ones
    (LINEHAN, AFFECTIVE) specifically must not carry body/harm-adjacent
    language, by explicit decision, not by accident."""

    # Every gate name a Nomination is actually constructed with in production,
    # per physics/filters.py and phases/cognitive.py's LINEHAN/AFFECTIVE/
    # ROS_PANIC blocks, brain/cortex.py's MOOG/GORDON_ANCHOR/PINKER, and the
    # four preflight gates D9 migrated. A name missing here would silently
    # fall back to the generic "_default" text, which is safe but should be
    # a deliberate choice, not an oversight; this is this table's own roll
    # call, the same discipline receipts.py's CORE_SUBSYSTEMS uses.
    KNOWN_GATES = (
        "GATEKEEPER", "MOOG", "GORDON_ANCHOR", "PINKER", "ROS_PANIC",
        "LINEHAN", "AFFECTIVE", "NABLA_SILENCE", "APOPTOTIC_BLOCK",
        "PREMISE_VIOLATION", "POINT_OF_NO_RETURN", "ATP_FLOOR",
        "TENSION_MAGNITUDE",
    )
    # Words that must never appear in what a person reads: raw internal tags
    # a developer would recognise from logs, or language adjacent to
    # self-harm. Checked against every entry, not just the two crisis gates,
    # because a jarring word could land in any of them by a future edit.
    FORBIDDEN_SUBSTRINGS = (
        "cursed", "pathogenic", "exploit", "bleed", "terminal user exhaustion",
        "immune reaction", "structural rot",
    )

    def setUp(self):
        from engine.core import LoreManifest

        self.reasons = LoreManifest.get_instance().get("ux_strings", "silence_reasons")

    def test_every_known_gate_has_its_own_entry(self):
        for gate in self.KNOWN_GATES:
            with self.subTest(gate=gate):
                self.assertIn(gate, self.reasons, f"{gate} falls back to the generic default")

    def test_no_entry_contains_forbidden_language(self):
        for gate, text in self.reasons.items():
            if gate.startswith("_"):
                continue
            lowered = text.lower()
            for bad in self.FORBIDDEN_SUBSTRINGS:
                with self.subTest(gate=gate, forbidden=bad):
                    self.assertNotIn(bad, lowered)

    def test_linehan_and_affective_are_plain_and_calm(self):
        """Decided explicitly with Gordon: no metaphor, no body/harm imagery,
        for either of the crisis-adjacent gates."""
        for gate in ("LINEHAN", "AFFECTIVE"):
            with self.subTest(gate=gate):
                text = self.reasons[gate].lower()
                for word in ("blood", "bleed", "hurt", "pain", "die", "death"):
                    self.assertNotIn(word, text)
