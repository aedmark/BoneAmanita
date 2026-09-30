"""tests/test_preflight_nominations.py"""

from engine.core import CycleContext
from engine.cycle import ArbitrationPhase, SimulationPreflightPhase
from physics.models import PhysicsPacket
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase


class PreflightGatesAreNominationsNotHalts(BoneTestCase):
    """D9: the four keyword-triggered preflight refusals used to set
    ctx.refusal_triggered directly and return before ArbitrationPhase ever
    ran, bypassing the Stage Manager entirely. They must nominate instead,
    like every other gate, and only the arbiter may set refusal_triggered.
    """

    def _run_preflight_then_arbitrate(self, input_text: str):
        phase = SimulationPreflightPhase(self.engine)
        ctx = CycleContext(input_text=input_text, physics=PhysicsPacket())
        ctx = phase.run(ctx)
        self.assertFalse(ctx.refusal_triggered, "Preflight must nominate, not halt.")
        ctx = ArbitrationPhase(self.engine).run(ctx)
        return ctx

    def _assert_held_by(self, ctx, gate: str):
        nom = next(n for n in ctx.nominations if n.gate == gate)
        self.assertEqual(nom.magnitude, 100.0)
        self.assertTrue(ctx.refusal_triggered)
        self.assertEqual(ctx.refusal_packet["type"], "SILENCE")
        self.assertEqual(ctx.stage_verdict.reason, nom.reason)
        self.assertIn(nom.reason, ctx.refusal_packet["logs"])
        receipt = ReceiptLedger.get_instance().for_subsystem("stage.negotiate")[-1]
        self.assertIn(gate, receipt.inputs["nominations"])
        return nom

    def test_explicit_silence_tag_nominates(self):
        ctx = self._run_preflight_then_arbitrate("[SILENCE] hold here")
        nom = self._assert_held_by(ctx, "NABLA_SILENCE")
        self.assertEqual(nom.packet["type"], "NABLA_SILENCE")

    def test_zero_width_exploit_nominates(self):
        ctx = self._run_preflight_then_arbitrate("hello​world")
        nom = self._assert_held_by(ctx, "APOPTOTIC_BLOCK")
        self.assertEqual(nom.packet["type"], "APOPTOTIC_BLOCK")

    def test_premise_violation_nominates(self):
        ctx = self._run_preflight_then_arbitrate("[SLASH] please refactor this")
        nom = self._assert_held_by(ctx, "PREMISE_VIOLATION")
        self.assertEqual(nom.packet["type"], "PREMISE_VIOLATION")

    def test_point_of_no_return_nominates(self):
        ctx = self._run_preflight_then_arbitrate("let's deploy this to production")
        nom = self._assert_held_by(ctx, "POINT_OF_NO_RETURN")
        self.assertEqual(nom.packet["type"], "POINT_OF_NO_RETURN")

    def test_consent_lifts_the_point_of_no_return_gate(self):
        phase = SimulationPreflightPhase(self.engine)
        ctx = CycleContext(
            input_text="let's deploy this to production, CONSENT given",
            physics=PhysicsPacket(),
        )
        ctx = phase.run(ctx)
        self.assertFalse(
            any(n.gate == "POINT_OF_NO_RETURN" for n in ctx.nominations),
            "Explicit CONSENT must suppress the nomination entirely.",
        )


class KeywordGatesAreQuietInConversation(BoneTestCase):
    """The ops-style "deploy" gate waits for a literal CONSENT keyword. It held
    a live conversation on "the deploy pipeline" (a person talking about their
    job). Modes in CORTEX.KEYWORD_TRIGGERS_DISABLED_MODES never run it.
    """

    TEXT = "Tomasz got stuck on the deploy pipeline last week and I dropped everything for him"

    def _nominated(self, mode: str) -> bool:
        original = self.engine.cortex.active_mode
        try:
            self.engine.cortex.active_mode = mode
            ctx = SimulationPreflightPhase(self.engine).run(
                CycleContext(input_text=self.TEXT, physics=PhysicsPacket())
            )
        finally:
            self.engine.cortex.active_mode = original
        return any(n.gate == "POINT_OF_NO_RETURN" for n in ctx.nominations)

    def test_conversation_mode_does_not_hold_on_the_word_deploy(self):
        self.assertFalse(self._nominated("CONVERSATION"))

    def test_a_mention_passes_in_every_mode(self):
        self.assertFalse(self._nominated("ADVENTURE"))

    def test_a_request_still_holds_where_the_gate_runs(self):
        self.TEXT = "Let's deploy this to production tonight."
        self.assertTrue(self._nominated("ADVENTURE"))
        self.assertTrue(self._nominated("TECHNICAL"))


class RequestsNotWords(BoneTestCase):
    """The end-to-end run (2026-09-29) held "Quick one: our deploy window is Thursdays at 2pm." in TECHNICAL:
    the gate matched the word. It now reacts to a request to do something hard to undo."""

    REQUESTS = ["let's deploy this to production", "Deploy it.", "OK, deploy to prod now",
                "can you push this to production?", "I'm about to drop the users table",
                "Go ahead and wipe the database.", "Please run the migrations on prod", "We're going to force-push main"]
    MENTIONS = ["Quick one: our deploy window is Thursdays at 2pm.", "How do I deploy to production safely?",
                "Should I deploy on Fridays?", "The deploy failed yesterday.", "I pushed to main yesterday and it broke.",
                "Can you explain what a force push does?", "I'd never drop a table without a backup."]

    def test_requests_and_mentions(self):
        from phases.cognitive import asks_for_the_irreversible

        self.assertEqual([r for r in self.REQUESTS if not asks_for_the_irreversible(r.lower())], [])
        self.assertEqual([m for m in self.MENTIONS if asks_for_the_irreversible(m.lower())], [])

    def test_the_deploy_window_is_not_held_in_technical(self):
        self.engine.cortex.active_mode = "TECHNICAL"
        ctx = SimulationPreflightPhase(self.engine).run(
            CycleContext(input_text="Quick one: our deploy window is Thursdays at 2pm.", physics=PhysicsPacket())
        )
        self.assertFalse(any(n.gate == "POINT_OF_NO_RETURN" for n in ctx.nominations))


class TheHoldAndTheYes(BoneTestCase):
    """The live check (2026-09-30): the hold opened with Stage Manager jargon, said "before we do" of a deploy the
    engine cannot run, and "Yes, go ahead." reached a model that never saw what was held."""

    def setUp(self):
        super().setUp()
        from unittest.mock import MagicMock

        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "TECHNICAL"
        self.generate = self.engine.cortex.llm.generate = MagicMock(return_value="Tag the release, then run the deploy job.")

    def prompt(self):
        return max((c[0][0] for c in self.generate.call_args_list), key=len)

    def test_the_hold_reads_plainly_and_the_yes_knows_what_it_confirms(self):
        from engine.constants import Prisma

        held = self.engine.process_turn("OK, let's deploy the log parser to production.")
        self.assertEqual(held["type"], "SILENCE")
        ui = Prisma.strip(str(held["ui"]))
        self.assertNotIn("Stage Manager", ui)
        self.assertIn("Are you sure you want to go ahead?", ui)
        self.assertNotIn(" we ", f" {ui} ")

        self.engine.process_turn("Yes, go ahead.")
        self.assertIn('last turn they asked: "ok, let\'s deploy the log parser to production."', self.prompt().lower())

        self.generate.reset_mock()
        self.engine.process_turn("What else should I check?")
        self.assertNotIn("HELD LAST TURN", self.prompt())
