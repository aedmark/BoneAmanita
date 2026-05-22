"""tests/test_edge_branches.py"""

import unittest
from unittest.mock import patch, MagicMock
from drivers.validator import CongruenceValidator
from protocols.therapy import TherapyProtocol
from soul.oroboros import TheOroboros

class EdgeBranchCoverageTests(unittest.TestCase):
    @patch("drivers.validator.LoreManifest")
    def test_congruence_validator_bonus_branch(self, MockLore):
        mock_lore_instance = MagicMock()
        mock_lore_instance.get.return_value = {
            "OBSERVER": {
                "vocab": "tensegrity, structure",
                "keywords": ["manifold"]
            }
        }
        MockLore.get_instance.return_value = mock_lore_instance
        validator = CongruenceValidator()

        class MockContext:
            active_lens = "THE OBSERVER"
            clean_words = ["tensegrity", "manifold", "noise"]

        score = validator.calculate_resonance("tensegrity manifold noise", MockContext())
        self.assertGreater(score, 0.8, "Validator failed to execute the resonance bonus branch.")

    @patch("soul.oroboros.LoreManifest")
    def test_oroboros_malformed_legacy_data(self, MockLore):
        mock_lore_instance = MagicMock()
        mock_lore_instance.get.return_value = {
            "TOXICITY": ["Fragmented Scar", "voltage"]
        }
        MockLore.get_instance.return_value = mock_lore_instance
        oroboros = TheOroboros()
        dummy_soul = MagicMock()
        dummy_soul.eng.trauma_accum = {}
        dummy_soul.core_memories = []
        msg = oroboros.crystallize("TOXICITY", dummy_soul)
        self.assertIsNotNone(msg, "Oroboros failed to parse malformed legacy data.")
        self.assertTrue(any("Fragmented" in s.name for s in oroboros.scars), "Scar failed to generate from malformed data.")

    def test_therapy_healing_threshold_branch(self):
        therapy = TherapyProtocol()
        therapy.HEALING_THRESHOLD = 2
        phys_fixture = {
            "matter": {"counts": {"toxin": 0}, "vector": {"STR": 0.5}}
        }
        trauma_accum = {"SEPTIC": 10.0}
        healed = therapy.check_progress(phys_fixture, 100.0, trauma_accum)
        self.assertEqual(len(healed), 0, "Therapy executed the healing branch too early.")
        healed = therapy.check_progress(phys_fixture, 100.0, trauma_accum)
        self.assertIn("SEPTIC", healed, "Therapy failed to execute the healing branch.")
        self.assertLess(trauma_accum["SEPTIC"], 10.0, "Trauma was not successfully reduced.")

if __name__ == "__main__":
    unittest.main()