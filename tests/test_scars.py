"""tests/test_scars.py

Scars live on the Akashic Record. Four call sites asked `mind.mem` (the
MycelialNetwork) for `record_scar`, which it has never had. Three were guarded by
`hasattr` and silently recorded nothing; the cortex's was not, so the first
counterfactual rejection of a live session raised, SystemHealth took MIND
offline, and every later turn skipped cognition without a word until a REM
cycle rebooted it.

This travels the real engine, because the unit tests mocked the network loosely
enough to accept a method it does not have.
"""

import unittest

from tests.base import BoneTestCase
from engine.core import CycleContext
from physics.models import PhysicsPacket, EnergyState


class CounterfactualToxicityLeavesAScar(BoneTestCase):
    TOXIC = {"narrative_drag": 1.5, "chi": 0.8, "m_a": 1.0}

    def test_the_cortex_rejection_records_a_scar_and_keeps_the_mind_online(self):
        self.engine.config.GATE_TOLERANCE = 1.0
        akashic = self.engine.akashic
        before = len(akashic.scar_map)
        ctx = CycleContext(
            input_text="test",
            physics=PhysicsPacket(
                narrative_drag=self.TOXIC["narrative_drag"],
                energy=EnergyState(chi=self.TOXIC["chi"], m_a=self.TOXIC["m_a"]),
            ),
        )
        self.engine.cortex.nominate_toxicity(ctx)
        self.assertFalse(ctx.refusal_triggered)
        
        self.assertEqual(ctx.nominations[0].packet.get("type"), "COUNTERFACTUAL_REJECTION")
        self.assertEqual(len(akashic.scar_map), before + 1)
        self.assertTrue(self.engine.system_health.components_online["mind"])

    def test_every_scar_writer_reaches_the_akashic_record(self):
        """No call site may go back to the memory network."""
        self.assertFalse(hasattr(self.engine.mind.mem, "record_scar"))
        self.assertTrue(callable(getattr(self.engine.akashic, "record_scar", None)))
        self.assertIs(self.engine.cortex.svc.akashic, self.engine.akashic)


if __name__ == "__main__":
    unittest.main()
