"""tests/test_conversation_gates.py

Two mechanics that shelved distressed people mid-conversation on the fresh
`lease` topic (turns 20 and 23, reproduced three times) and on friendship 27/28
and `promotion` 8:

  - THE DIGNITY LOCK synergy (BENEDICT|GORDON) adds +50 narrative drag by
    design whenever both voices are active, which a quietly heavy person
    triggers. Drag of about 55 then tripped MOOG and the ROS panic gate.
  - MOOG's worry-quarantine then held the turn.

Modes in COUNCIL.FRICTION_SYNERGY_DISABLED_MODES and CORTEX.MOOG_DISABLED_MODES
skip them; the game modes keep them exactly as written.
"""

from archetypes.council import TheVillageCouncil
from engine.core import CycleContext
from physics.models import PhysicsPacket
from tests.base import BoneTestCase


class FrictionSynergyIsQuietInConversation(BoneTestCase):
    def _quietly_heavy_and_tactful(self) -> PhysicsPacket:
        packet = PhysicsPacket(voltage=11.0, narrative_drag=5.8, chi=0.52)
        setattr(packet, "lq", 0.7)
        setattr(packet, "beta_index", 0.5)
        return packet

    def _drag_adjustment(self, mode: str) -> float:
        _, adjustments, _ = self.engine.council.convene(
            "so I opened my banking app to do the math",
            self._quietly_heavy_and_tactful(),
            {"stamina": 100.0},
            active_mode=mode,
        )
        return float(adjustments.get("narrative_drag", 0.0))

    def test_the_state_really_activates_both_voices(self):
        voices = TheVillageCouncil.audit_voices(
            self._quietly_heavy_and_tactful(), {"stamina": 100.0, "trauma": 0.0}
        )
        self.assertIn("GORDON", voices)
        self.assertIn("BENEDICT", voices)

    def test_conversation_mode_skips_the_dignity_lock(self):
        self.assertLess(self._drag_adjustment("CONVERSATION"), 5.0)

    def test_a_game_mode_still_gets_the_dignity_lock(self):
        self.assertGreater(self._drag_adjustment("ADVENTURE"), 40.0)


class MoogQuarantineIsQuietInConversation(BoneTestCase):
    def _nominated_gates(self, mode: str, drag: float) -> list:
        packet = PhysicsPacket(voltage=10.5, narrative_drag=drag, chi=0.13)
        setattr(packet, "m_a", 0.02)
        ctx = CycleContext(
            input_text="my hands are cold and I can't tell if I'm cold or panicking",
            physics=packet,
        )
        original = self.engine.cortex.active_mode
        try:
            self.engine.cortex.active_mode = mode
            self.engine.cortex.nominate_toxicity(ctx)
        finally:
            self.engine.cortex.active_mode = original
        return [n.gate for n in ctx.nominations]

    def test_conversation_mode_does_not_quarantine_a_worry(self):
        self.assertNotIn("MOOG", self._nominated_gates("CONVERSATION", 55.0))

    def test_a_game_mode_still_quarantines_a_worry(self):
        self.assertIn("MOOG", self._nominated_gates("ADVENTURE", 55.0))

    def test_calm_drag_nominates_nothing_either_way(self):
        self.assertEqual(self._nominated_gates("ADVENTURE", 6.0), [])
        self.assertEqual(self._nominated_gates("CONVERSATION", 6.0), [])
