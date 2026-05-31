"""tests/test_lexicon.py"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from mechanics.lexicon import LexiconStore, LinguisticAnalyzer, LexiconService, SemanticField
from tests.base import BoneTestCase


class TestLexicon(BoneTestCase):
    def setUp(self):
        super().setUp()

        # Mock the LoreManifest data specifically for the Lexicon
        self.mock_manifest_data = {
            "LEXICON": {
                "solvents": ["the", "a", "an", "is", "are"],
                "antigen_replacements": {"actually": "", "basically": "", "literally": "figuratively"},
                "heavy": ["monolith", "iron", "gravity"],
                "kinetic": ["sprint", "strike", "dash"],
                "sentiment_pos": ["radiant", "good", "perfect"],
                "sentiment_neg": ["broken", "bad", "ruined"],
                "sentiment_negators": ["not", "never", "hardly"]
            },
            "LINGUISTICS": {
                "PHONETICS": {"PLOSIVE": ["p", "t", "k", "b", "d", "g"], "VOWELS": ["a", "e", "i", "o", "u"]},
                "ROOTS": {"heavy": ["lith", "grav", "ferr"]},
                "THRESHOLDS": {"heavy_density": 0.55, "play_vitality": 0.6, "kinetic_flow": 0.6},
                "BIASES": {"heavy": 1.0, "play": 1.0, "kinetic": 1.0},
                "DIMENSION_MAP": {"heavy": "STR", "kinetic": "VEL"}
            }
        }

        # Patch the LoreManifest singleton to return our controlled test data
        self.patcher = patch("mechanics.lexicon.LoreManifest.get_instance")
        self.mock_manifest = self.patcher.start()
        self.mock_manifest.return_value.get.side_effect = lambda *args: self.mock_manifest_data.get(args[0])

        self.store = LexiconStore()
        self.store.load_vocabulary()
        self.analyzer = LinguisticAnalyzer(self.store)

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    # --- STORE TESTS ---

    def test_store_harvest_punctuation_stripping(self):
        text = "The monolith, it stands! Sprint... fast."
        harvested = self.store.harvest(text)
        self.assertIn("heavy", harvested, "[FAIL] Failed to harvest 'heavy' category.")
        self.assertIn("monolith", harvested["heavy"], "[FAIL] Failed to strip punctuation from 'monolith,'.")
        self.assertIn("sprint", harvested.get("kinetic", []), "[FAIL] Failed to strip punctuation and match exactly.")

    def test_store_harvest_type_coercion(self):
        # [Brutalist Test]: Ensure harvest doesn't crash on non-string inputs
        result = self.store.harvest(404)
        self.assertEqual(result, {}, "[FAIL] Harvest crashed or returned invalid data when fed an integer.")
        result_none = self.store.harvest(None)
        self.assertEqual(result_none, {}, "[FAIL] Harvest crashed when fed None.")

    def test_store_teach_limit_enforcement(self):
        category = "custom_cat"
        # Teach 1005 words to trigger the 1000 word limit pruning
        for i in range(1005):
            self.store.teach(f"word_{i}", category, tick=i)

        learned = self.store.LEARNED_VOCAB.get(category, {})
        self.assertEqual(len(learned), 1000, "[FAIL] LexiconStore failed to prune oldest words when limit was reached.")
        self.assertNotIn("word_0", learned, "[FAIL] LexiconStore pruned the wrong word. The oldest word survived.")

    # --- ANALYZER TESTS ---

    def test_analyzer_sanitize_type_coercion(self):
        # [Pinker Test]: Ensure the sanitize method coerces loosely typed objects safely
        bad_payload = SimpleNamespace(text="broken")
        result = self.analyzer.sanitize(bad_payload)
        self.assertTrue(isinstance(result, list), "[FAIL] Sanitize failed to return a list for a namespace object.")

        number_payload = 12345
        result_num = self.analyzer.sanitize(number_payload)
        self.assertIn("12345", result_num, "[FAIL] Sanitize failed to coerce and parse an integer.")

    def test_analyzer_antigen_purge(self):
        dirty_text = "Basically, it is literally a monolith."
        clean_text = self.analyzer.sanitize(dirty_text)
        self.assertNotIn("basically", clean_text, "[FAIL] Antigen 'basically' survived sanitization.")
        self.assertIn("figuratively", clean_text, "[FAIL] Antigen 'literally' was not replaced with 'figuratively'.")

    def test_analyzer_valence_negation(self):
        pos_words = ["radiant", "perfect"]
        neg_words = ["broken", "ruined"]
        negated_words = ["not", "perfect"]

        self.assertGreater(self.analyzer.measure_valence(pos_words), 0.0, "[FAIL] Positive words scored <= 0.")
        self.assertLess(self.analyzer.measure_valence(neg_words), 0.0, "[FAIL] Negative words scored >= 0.")

        negated_score = self.analyzer.measure_valence(negated_words)
        self.assertLess(negated_score, 0.0, "[FAIL] The negator 'not' failed to invert the positive valence of 'perfect'.")

    def test_analyzer_turbulence_bounds(self):
        turb_single = self.analyzer.get_turbulence(["word"])
        self.assertEqual(turb_single, 0.0, "[FAIL] Turbulence for a single word should be exactly 0.0.")

        turb_wild = self.analyzer.get_turbulence(["a", "supercalifragilisticexpialidocious", "is", "wild"])
        self.assertGreater(turb_wild, 0.5, "[FAIL] High variance in word lengths failed to generate significant turbulence.")

    # --- SERVICE TESTS ---

    def test_service_event_bus_loose_payload(self):
        # [Meadows Test]: Ensure the LexiconService can parse loosely typed EventBus payloads
        mock_events = MagicMock()
        service = LexiconService(events_ref=mock_events)

        # 1. Test standard dictionary payload
        dict_payload = {"word": "gestalt", "category": "heavy"}
        service._on_mythology_update(dict_payload)
        self.assertIn("heavy", service.get_categories_for_word("gestalt"), "[FAIL] Service failed to learn from dict payload.")

        # 2. Test dynamic Namespace payload (The fix we just applied)
        ns_payload = SimpleNamespace(word="synapse", category="kinetic")
        service._on_mythology_update(ns_payload)
        self.assertIn("kinetic", service.get_categories_for_word("synapse"), "[FAIL] Service failed to learn from Namespace payload.")

    def test_semantic_field_momentum(self):
        field = SemanticField(self.analyzer)

        # Initial burst
        vec1 = field.update("sprint strike dash")
        self.assertEqual(field.momentum, 0.0, "[FAIL] Initial momentum should be 0.0.")
        self.assertIn("VEL", vec1, "[FAIL] Field failed to map 'kinetic' to 'VEL' dimension.")

        # Shift in momentum
        field.update("monolith iron gravity")
        self.assertGreater(field.momentum, 0.0, "[FAIL] Massive semantic shift failed to generate momentum/flux.")


if __name__ == "__main__":
    unittest.main()