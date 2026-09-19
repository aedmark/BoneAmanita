"""tests/test_preflight_nominations.py"""

from core import CycleContext
from cycle import ArbitrationPhase, SimulationPreflightPhase
from physics.models import PhysicsPacket
from receipts import ReceiptLedger
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
