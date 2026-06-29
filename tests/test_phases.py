"""tests/test_phases.py"""

import unittest
from unittest.mock import patch

from core import CycleContext
from phases.biological import IntrusionPhase, MetabolismPhase, SensationPhase
from phases.cognitive import CognitionPhase
from phases.environmental import SanctuaryPhase
from physics.models import PhysicsPacket

try:
    from tests.base import BoneTestCase
except ImportError:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tests.base import BaseTest as BoneTestCase

class PhaseBoundaryTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.ctx = CycleContext(input_text="The void stares back.")
        self.ctx.physics = PhysicsPacket.void_state()
        self.engine.stamina = 100.0
        self.engine.health = 100.0
        self.engine.set_atp(100.0)

    def test_metabolism_clamping(self):
        phase = MetabolismPhase(self.engine)
        self.engine.bio.biometrics.stamina = -50.0
        self.engine.bio.biometrics.health = -99.0
        self.engine.bio.mito.state.atp_pool = -10.0
        phase.run(self.ctx)
        self.assertGreaterEqual(self.engine.stamina, 0.0, "Stamina failed to clamp to 0.")
        self.assertGreaterEqual(self.engine.health, 0.0, "Health failed to clamp to 0.")
        self.assertGreaterEqual(self.engine._mito_state.atp_pool, 0.0, "ATP failed to clamp to 0.")

    def test_metabolism_homeostasis_reward(self):
        if not hasattr(self.engine.config, "Q_MATRIX_REWARD"):
            self.engine.config.Q_MATRIX_REWARD = 0.0
        phase = MetabolismPhase(self.engine)
        self.ctx.physics.resonance = 0.8
        self.engine.trauma_accum = {"fear": 5.0}
        self.engine.bio.mito.state.atp_pool = 50.0
        self.engine.stamina = 50.0
        phase._calculate_homeostasis_reward(self.ctx)
        self.assertEqual(
            self.engine.config.Q_MATRIX_REWARD, 1.0, "[FAIL] Positive reward was not applied for healthy homeostasis."
        )
        self.ctx.physics.resonance = 0.0
        self.engine.bio.mito.state.atp_pool = 1.0
        phase._calculate_homeostasis_reward(self.ctx)
        self.assertEqual(
            self.engine.config.Q_MATRIX_REWARD,
            0.0,
            "[FAIL] Negative penalty was not applied to subtract from the reward pool.",
        )

    def test_sensation_stamina_impact(self):
        phase = SensationPhase(self.engine)
        self.engine.stamina = 50.0
        self.ctx.physics.narrative_drag = 10.0
        self.ctx.physics.voltage = 90.0
        phase.run(self.ctx)
        self.assertGreaterEqual(self.engine.stamina, 0.0)
        self.assertLessEqual(self.engine.stamina, 100.0)

    def test_intrusion_hallucination_drain(self):
        phase = IntrusionPhase(self.engine)
        self.engine.stamina = 10.0
        self.ctx.physics.psi = 0.95
        phase.run(self.ctx)
        self.assertGreaterEqual(self.engine.stamina, 0.0)

    def test_sanctuary_healing(self):
        phase = SanctuaryPhase(self.engine, self.engine.bio.governor)
        self.engine.health = 40.0
        self.engine.set_atp(20.0)
        self.engine.trauma_accum = {"abandonment": 5.0}
        self.engine.bio.governor.mode = "SANCTUARY"
        self.ctx.physics.zone = "SANCTUARY"
        with patch.object(self.engine.bio.governor, "assess", return_value=(True, 0.0)):
            phase.run(self.ctx)
        self.assertLess(self.engine.trauma_accum.get("abandonment", 5.0), 5.0)

    def test_cognitive_double_hit_removed(self):
        phase = CognitionPhase(self.engine)
        self.engine.stamina = 100.0
        self.ctx.clean_words = ["death", "failure", "collapse"]
        self.ctx.physics.voltage = 100.0
        phase.run(self.ctx)
        self.assertTrue(
            self.engine.stamina in (100.0, 95.0),
            f"Stamina dropped to {self.engine.stamina}. Double hit or unhandled decay detected.",
        )

    def test_cognition_nonetype_input_safeguard(self):
        phase = CognitionPhase(self.engine)
        self.ctx.input_text = None
        self.ctx.is_bureaucratic = False
        try:
            phase.run(self.ctx)
        except AttributeError as e:
            self.fail(f"[FAIL] CognitionPhase crashed on NoneType input: {e}")

    def test_cognition_sycophancy_spiral_break(self):
        phase = CognitionPhase(self.engine)
        self.engine.sycophancy_streak = 3
        self.ctx.input_text = "I completely agree with everything you say."
        self.ctx.physics.resonance = 0.95
        phase.run(self.ctx)
        self.assertEqual(
            self.engine.sycophancy_streak,
            0,
            "[FAIL] The Jester triggered, but the streak didn't reset. Infinite loop risk!",
        )

    def test_cognition_liminal_tax_organ_check(self):
        from unittest.mock import MagicMock
        phase = CognitionPhase(self.engine)
        self.ctx.input_text = "Drifting into liminal space."
        self.engine.consultant = MagicMock()
        self.engine.consultant.state.active_modules = ["LIMINAL"]
        self.engine.consultant.state.L = 0.5
        self.engine.bio = None
        try:
            phase.run(self.ctx)
        except AttributeError as e:
            self.fail(
                f"[FAIL] CognitionPhase crashed trying to tax non-existent biology: {e}"
            )

    def test_cognition_dream_leak_concatenation(self):
        phase = CognitionPhase(self.engine)
        self.ctx.input_text = "Waking up..."
        self.ctx.clean_words = None  # Simulate an uninitialized context state
        self.ctx.last_dream = {"log": "A vivid dream about fractal geometry."}
        try:
            phase.run(self.ctx)
        except TypeError as e:
            self.fail(
                f"[FAIL] CognitionPhase crashed concatenating dream words with NoneType: {e}"
            )
        self.assertIsNotNone(self.ctx.clean_words, "[FAIL] clean_words remained None.")
        self.assertTrue(
            len(self.ctx.clean_words) > 0, "[FAIL] Ghost words were not appended."
        )

if __name__ == "__main__":
    unittest.main()
