"""tests/test_phases.py"""

import unittest
from unittest.mock import patch
from phases.biological import MetabolismPhase, SensationPhase, IntrusionPhase
from phases.environmental import SanctuaryPhase
from phases.cognitive import CognitionPhase
from core import CycleContext
from physics.models import PhysicsPacket

try:
    from tests.base import BoneTestCase
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
        with patch.object(self.engine.bio.governor, 'assess', return_value=(True, 0.0)):
            phase.run(self.ctx)
        self.assertLess(self.engine.trauma_accum.get("abandonment", 5.0), 5.0)

    def test_cognitive_double_hit_removed(self):
        phase = CognitionPhase(self.engine)
        self.engine.stamina = 100.0
        self.ctx.clean_words = ["death", "failure", "collapse"]
        self.ctx.physics.voltage = 100.0
        phase.run(self.ctx)
        self.assertTrue(self.engine.stamina in (100.0, 95.0), f"Stamina dropped to {self.engine.stamina}. Double hit or unhandled decay detected.")

if __name__ == '__main__':
    unittest.main()