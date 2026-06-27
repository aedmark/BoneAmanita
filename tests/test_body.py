"""tests/test_body.py"""

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from body.endocrine import EndocrineSystem
from body.metabolism import DigestiveTrack, MitochondrialForge
from body.models import BiologicalImpulse, Biometrics, MitochondrialState
from body.regulation import BioFeedback, MetabolicGovernor, PIDController
from body.somatic import SynestheticCortex
from body.system import BioSystem
from presets import BoneConfig
from tests.base import BoneTestCase


class BiologyArchitectureTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig()
        self.state = MitochondrialState(atp_pool=50.0, ros_buildup=0.0)
        self.mito = MitochondrialForge(
            self.state, events_ref=MagicMock(), config_ref=self.config
        )
        self.endo = EndocrineSystem(config_ref=self.config)
        self.governor = MetabolicGovernor(config_ref=self.config)
        self.biometrics = Biometrics(health=50.0, stamina=50.0)
        self.bio = BioSystem(
            mito=self.mito,
            endo=self.endo,
            governor=self.governor,
            biometrics=self.biometrics,
            events=MagicMock(),
            config_ref=self.config,
        )

    def test_bio_system_rest_recovery(self):
        self.bio.endo.serotonin = 0.5
        self.bio.endo.cortisol = 0.5

        self.bio.rest(factor=1.0)

        self.assertTrue(
            self.bio.biometrics.health > 50.0,
            "[FAIL] Health did not recover during rest.",
        )
        self.assertTrue(
            self.bio.biometrics.stamina > 50.0,
            "[FAIL] Stamina did not recover during rest.",
        )
        self.assertTrue(
            self.bio.endo.serotonin > 0.5, "[FAIL] Serotonin did not boost during rest."
        )
        self.assertTrue(
            self.bio.endo.cortisol < 0.5, "[FAIL] Cortisol did not drop during rest."
        )

    def test_mitochondrial_anaerobic_bypass(self):
        phys_packet = {
            "voltage": 999.0,
            "depth": 10.0,
            "connectivity": 10.0,
            "entropy": 0.0,
        }

        receipt = self.mito.process_cycle(phys_packet)

        self.assertEqual(
            receipt.status,
            "ANAEROBIC",
            "[FAIL] Extreme metabolic load failed to trigger Anaerobic Bypass.",
        )
        self.assertEqual(
            receipt.total_burn,
            20.0,
            "[FAIL] Anaerobic Bypass did not apply the hardcoded 20.0 HP burn.",
        )
        self.assertTrue(
            self.mito.state.ros_buildup > 0.0,
            "[FAIL] Anaerobic Bypass failed to generate ROS waste.",
        )

    def test_digestive_cliche_tax(self):
        mock_lexicon = MagicMock()
        mock_lexicon.get.side_effect = lambda key: (
            {"literally"} if key == "antigen" else set()
        )

        digestive = DigestiveTrack(
            self.bio, lexicon_ref=mock_lexicon, config_ref=self.config
        )

        words = ["literally", "literally", "fascinating", "connection"]
        atp_yield, enzymes, tax, hits = digestive._digest_words(words)

        self.assertTrue(
            tax > 0.0,
            "[FAIL] DigestiveTrack failed to apply the Cliche Tax to antigens.",
        )
        self.assertTrue(
            hits > 0,
            "[FAIL] DigestiveTrack failed to register valid hits for non-antigen words.",
        )

    def test_pid_controller_math(self):
        pid = PIDController(
            kp=0.5, ki=0.0, kd=0.0, setpoint=10.0, output_limits=(-10.0, 10.0)
        )

        output = pid.update(measurement=5.0, dt=1.0)

        self.assertEqual(
            output, 2.5, "[FAIL] PID Controller proportional math is incorrect."
        )

    def test_biofeedback_autophagy(self):
        feedback = BioFeedback(self.bio, config_ref=self.config)

        self.bio.biometrics.stamina = 0.0
        self.bio.biometrics.health = 50.0

        dummy_phys = {"voltage": 10.0, "entropy": 0.5, "m_a": 0.1}
        logs = []

        status = feedback.check_vital_signs(dummy_phys, stamina=0.0, logs=logs)

        self.assertEqual(
            status,
            "AUTOPHAGY",
            "[FAIL] BioFeedback failed to trigger Autophagy on 0 stamina.",
        )
        self.assertTrue(
            self.bio.biometrics.health < 50.0,
            "[FAIL] Autophagy did not burn health to restore stamina.",
        )

    def test_synesthetic_cortex_high_drag(self):
        cortex = SynestheticCortex(self.bio, config_ref=self.config)
        phys = {"narrative_drag": 10.0, "voltage": 5.0, "valence": 0.0, "counts": {}}
        impulse = cortex.perceive(phys)
        self.assertTrue(
            impulse.stamina_impact < -1.0, "[FAIL] Synesthetic Cortex failed to penalize stamina under high drag."
        )
        self.assertTrue(
            impulse.cortisol_delta > 0.0, "[FAIL] Synesthetic Cortex failed to raise cortisol under high drag."
        )

    def test_synesthetic_cortex_cordyceps_load(self):
        """Ensures the body is physically suffocated by the Cordyceps bloom."""
        cortex = SynestheticCortex(self.bio, config_ref=self.config)
        if not hasattr(self.config, "BIO"):
            self.config.BIO = {}
        if isinstance(self.config.BIO, dict):
            self.config.BIO["CORDYCEPS_BLOOMING"] = True
        else:
            setattr(self.config.BIO, "CORDYCEPS_BLOOMING", True)
        phys = {"narrative_drag": 0.0, "voltage": 5.0, "valence": 0.0, "counts": {}}
        impulse = cortex.perceive(phys)
        self.assertLessEqual(impulse.stamina_impact, -5.0, "[FAIL] Cordyceps failed to drain stamina.")
        self.assertGreaterEqual(impulse.cortisol_delta, 0.2, "[FAIL] Cordyceps failed to spike cortisol.")
        self.assertEqual(
            impulse.somatic_reflex, "Suffocating (Fungal Load)", "[FAIL] Somatic reflex was not overridden."
        )

    def test_endocrine_metabolize_clamp(self):
        self.endo.dopamine = 5.0
        self.endo.cortisol = -2.0

        self.endo.metabolize(feedback={}, health=100.0, stamina=100.0)

        self.assertTrue(
            self.endo.dopamine <= 1.0,
            "[FAIL] Endocrine regulator failed to clamp upper bounds.",
        )
        self.assertTrue(
            self.endo.cortisol >= 0.0,
            "[FAIL] Endocrine regulator failed to clamp lower bounds.",
        )


if __name__ == "__main__":
    unittest.main()
