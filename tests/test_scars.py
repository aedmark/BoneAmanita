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


class CounterfactualToxicityLeavesAScar(BoneTestCase):
    TOXIC = {"narrative_drag": 1.5, "chi": 0.8, "m_a": 1.0}

    def test_the_cortex_rejection_records_a_scar_and_keeps_the_mind_online(self):
        akashic = self.engine.akashic
        before = len(akashic.scar_map)
        ctx = MagicMock()
        ctx.physics = MagicMock()
        ctx.physics.get = dict(self.TOXIC).get
        ctx.physics.__dict__.update(self.TOXIC)
        ctx.input_text = ""
        ctx.is_system_event = False
        ctx.nominations = []
        self.engine.cortex.nominate_toxicity(ctx)
        
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
