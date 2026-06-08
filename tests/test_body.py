"""tests/test_body.py"""

import unittest
from unittest.mock import MagicMock
import sys
import os

# Guarantee test runners discover the Base class correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.base import BoneTestCase
from presets import BoneConfig
from body.system import BioSystem
from body.models import Biometrics, MitochondrialState, BiologicalImpulse
from body.metabolism import MitochondrialForge, DigestiveTrack
from body.endocrine import EndocrineSystem
from body.regulation import PIDController, MetabolicGovernor, BioFeedback
from body.somatic import SynestheticCortex


class BiologyArchitectureTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig()

        # Instantiate raw dependencies to prevent MagicMock math errors
        self.state = MitochondrialState(atp_pool=50.0, ros_buildup=0.0)
        self.mito = MitochondrialForge(self.state, events_ref=MagicMock(), config_ref=self.config)
        self.endo = EndocrineSystem(config_ref=self.config)
        self.governor = MetabolicGovernor(config_ref=self.config)
        self.biometrics = Biometrics(health=50.0, stamina=50.0)

        # Build the full BioSystem
        self.bio = BioSystem(
            mito=self.mito,
            endo=self.endo,
            governor=self.governor,
            biometrics=self.biometrics,
            events=MagicMock(),
            config_ref=self.config
        )

    def test_bio_system_rest_recovery(self):
        # Resting should recover health, recover stamina, boost serotonin, and drop cortisol
        self.bio.endo.serotonin = 0.5
        self.bio.endo.cortisol = 0.5

        self.bio.rest(factor=1.0)

        self.assertTrue(self.bio.biometrics.health > 50.0, "[FAIL] Health did not recover during rest.")
        self.assertTrue(self.bio.biometrics.stamina > 50.0, "[FAIL] Stamina did not recover during rest.")
        self.assertTrue(self.bio.endo.serotonin > 0.5, "[FAIL] Serotonin did not boost during rest.")
        self.assertTrue(self.bio.endo.cortisol < 0.5, "[FAIL] Cortisol did not drop during rest.")

    def test_mitochondrial_anaerobic_bypass(self):
        # Provide a physics packet that creates a massive ATP demand (High voltage, high depth)
        phys_packet = {
            "voltage": 999.0,
            "depth": 10.0,
            "connectivity": 10.0,
            "entropy": 0.0
        }

        receipt = self.mito.process_cycle(phys_packet)

        # Exceeding the ANAEROBIC_THRESHOLD should trigger the bypass
        self.assertEqual(receipt.status, "ANAEROBIC", "[FAIL] Extreme metabolic load failed to trigger Anaerobic Bypass.")
        self.assertEqual(receipt.total_burn, 20.0, "[FAIL] Anaerobic Bypass did not apply the hardcoded 20.0 HP burn.")
        self.assertTrue(self.mito.state.ros_buildup > 0.0, "[FAIL] Anaerobic Bypass failed to generate ROS waste.")

    def test_digestive_cliche_tax(self):
        # Mock a lexicon with an antigen
        mock_lexicon = MagicMock()
        mock_lexicon.get.side_effect = lambda key: {"literally"} if key == "antigen" else set()

        digestive = DigestiveTrack(self.bio, lexicon_ref=mock_lexicon, config_ref=self.config)

        # Digest words, including the toxic cliche
        words = ["literally", "literally", "fascinating", "connection"]
        atp_yield, enzymes, tax, hits = digestive._digest_words(words)

        self.assertTrue(tax > 0.0, "[FAIL] DigestiveTrack failed to apply the Cliche Tax to antigens.")
        self.assertTrue(hits > 0, "[FAIL] DigestiveTrack failed to register valid hits for non-antigen words.")

    def test_pid_controller_math(self):
        # Clean mathematical test of the proportional response
        pid = PIDController(kp=0.5, ki=0.0, kd=0.0, setpoint=10.0, output_limits=(-10.0, 10.0))

        # Measurement is 5.0. Target is 10.0. Error = 5.0.
        # P-out = 0.5 * 5.0 = 2.5
        output = pid.update(measurement=5.0, dt=1.0)

        self.assertEqual(output, 2.5, "[FAIL] PID Controller proportional math is incorrect.")

    def test_biofeedback_autophagy(self):
        feedback = BioFeedback(self.bio, config_ref=self.config)

        # Set stamina to 0 but keep health high enough to survive Autophagy
        self.bio.biometrics.stamina = 0.0
        self.bio.biometrics.health = 50.0

        dummy_phys = {"voltage": 10.0, "entropy": 0.5, "m_a": 0.1}
        logs = []

        status = feedback.check_vital_signs(dummy_phys, stamina=0.0, logs=logs)

        self.assertEqual(status, "AUTOPHAGY", "[FAIL] BioFeedback failed to trigger Autophagy on 0 stamina.")
        self.assertTrue(self.bio.biometrics.health < 50.0, "[FAIL] Autophagy did not burn health to restore stamina.")

    def test_synesthetic_cortex_high_drag(self):
        cortex = SynestheticCortex(self.bio, config_ref=self.config)

        # Simulate extreme narrative drag
        phys = {
            "narrative_drag": 10.0,
            "voltage": 5.0,
            "valence": 0.0,
            "counts": {}
        }

        impulse = cortex.perceive(phys)

        self.assertTrue(impulse.stamina_impact < -1.0, "[FAIL] Synesthetic Cortex failed to penalize stamina under high drag.")
        self.assertTrue(impulse.cortisol_delta > 0.0, "[FAIL] Synesthetic Cortex failed to raise cortisol under high drag.")

    def test_endocrine_metabolize_clamp(self):
        # Force endocrine values out of bounds
        self.endo.dopamine = 5.0
        self.endo.cortisol = -2.0

        # Process a blank cycle
        self.endo.metabolize(feedback={}, health=100.0, stamina=100.0)

        self.assertTrue(self.endo.dopamine <= 1.0, "[FAIL] Endocrine regulator failed to clamp upper bounds.")
        self.assertTrue(self.endo.cortisol >= 0.0, "[FAIL] Endocrine regulator failed to clamp lower bounds.")


if __name__ == '__main__':
    unittest.main()