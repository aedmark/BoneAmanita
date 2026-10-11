"""tests/test_distress_silence.py

D-029. Two gemma replays met a person in distress with the Stage Manager's silence ("my chest has been tight since about three"),
and the line shown was about the engine ("not quite enough left in me"). A person in distress is answered; the engine's own load
(ATP floor, tension between voices) does not hold the turn, and when something still must (a survival gate), the line is warm.
"""

from archetypes.stage import HOLD, SPEAK, Nomination, StageManager, Tension
from archetypes.stage import Verdict
from body.somatic_budget import SomaticBudget
from engine.core import CycleContext, LoreManifest
from phases.cognitive import ArbitrationPhase
from tests.base import BoneTestCase
from physics.models import PhysicsPacket


def budget(distress: float):
    return SomaticBudget.evaluate(
        {"exhaustion": 0.0, "effort": 100.0, "distress": distress}, {"atp_pool": 80.0, "ros": 0.0, "respiration": ""}, "CONVERSATION"
    )


class TheEngineLoadDoesNotSilenceADistressedPerson(BoneTestCase):
    def verdict(self, distress, atp=80.0, voices=("A", "B"), nominations=()):
        return StageManager().negotiate(Tension(voices), None, atp=atp, nominations=list(nominations), somatic_budget=budget(distress))

    def test_a_low_atp_floor_does_not_hold_a_distressed_person(self):
        got = self.verdict(0.78, atp=10.0)
        self.assertEqual(got.outcome, SPEAK)

    def test_tension_between_many_voices_does_not_hold_a_distressed_person(self):
        got = self.verdict(0.78, voices=("A", "B", "C", "D"))
        self.assertEqual(got.outcome, SPEAK)

    def test_a_calm_person_is_still_held_by_the_same_load(self):
        self.assertEqual(self.verdict(0.0, atp=10.0).gate, "ATP_FLOOR")
        self.assertEqual(self.verdict(0.0, voices=("A", "B", "C", "D")).gate, "TENSION_MAGNITUDE")

    def test_the_survival_gate_still_holds(self):
        got = self.verdict(0.78, nominations=[Nomination("ROS_PANIC", "x", 120.0, {})])
        self.assertEqual(got.outcome, HOLD)


class WhatAHeldDistressedPersonReads(BoneTestCase):
    def shown(self, distress, gate):
        ctx = CycleContext(input_text="my chest is tight", is_system_event=False)
        ctx.physics = PhysicsPacket()
        ctx.somatic_budget = budget(distress)
        ArbitrationPhase(self.engine)._hold_the_silence(ctx, Verdict(HOLD, "THE STAGE MANAGER", "technical", Tension(()), gate=gate))
        return ctx.refusal_packet["ui"]

    def test_a_distressed_person_is_told_the_engine_is_here(self):
        reasons = LoreManifest.get_instance().get("ux_strings", "silence_reasons")
        self.assertIn(reasons["_distressed"], self.shown(0.78, "ROS_PANIC"))
        self.assertNotIn("unstable", self.shown(0.78, "ROS_PANIC"))

    def test_a_calm_person_still_reads_the_gate_line(self):
        reasons = LoreManifest.get_instance().get("ux_strings", "silence_reasons")
        self.assertIn(reasons["ROS_PANIC"], self.shown(0.0, "ROS_PANIC"))

    def test_the_persons_own_request_for_silence_keeps_its_line(self):
        reasons = LoreManifest.get_instance().get("ux_strings", "silence_reasons")
        self.assertIn(reasons["NABLA_SILENCE"], self.shown(0.78, "NABLA_SILENCE"))
