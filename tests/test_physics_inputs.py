"""tests/test_physics_inputs.py

Guards for ROADMAP A5: where the numbers that drive the engine come from.

The physics is computed from word-category counts. Those counts came 82% from a
phonosemantic fallback classifier that believed two thirds of English was
"play", which saturated the DEL dimension and pinned every conversation to one
zone. Nothing tested any of it, which is why it survived.
"""

import json
import unittest

from mechanics.lexicon import LexiconService
from physics.geodesics import GeodesicEngine
from physics.observer import QuantumObserver

CORPUS = [
    "hammering steel on the anvil, forging the heavy frame",
    "the abstract liminal shape of the idea itself",
    "everything is broken shattered exploding falling apart",
    "we sat and talked and laughed together in the afternoon",
    "running sprinting leaping across the field at speed",
    "tomatoes ripening slowly in the summer greenhouse",
    "my grandmother kept every letter she ever received",
    "debugging a segfault in the parser at three in the morning",
]


class ClassifierCalibration(unittest.TestCase):
    """The fallback returns a confidence, not a raw score."""

    def setUp(self):
        self.lex = LexiconService()
        self.lex.initialize()

    def test_confidence_is_bounded(self):
        """`apart` used to come back as ("play", 1.2), compared against 0.5 as
        though it were a probability."""
        for word in ("apart", "tomatoes", "segfault", "everything", "shattered"):
            _, confidence = self.lex.taste(word)
            self.assertGreaterEqual(confidence, 0.0, word)
            self.assertLessEqual(confidence, 1.0, word)

    def test_a_word_just_over_threshold_is_low_confidence(self):
        analyzer = self.lex._ANALYZER
        analyzer.classify_word.cache_clear()
        for word in ("apart", "before", "around"):
            category, confidence = analyzer.classify_word(word)
            if category is not None:
                self.assertLess(
                    confidence,
                    1.0,
                    f"[FAIL] {word} is maximally confident; the margin is not "
                    f"being normalised.",
                )

    def test_fallback_is_a_minority_of_word_resolution(self):
        """It was 82%. The hand-written lexicon should carry the signal."""
        total = tasted = 0
        for line in CORPUS:
            for word in self.lex.clean(line):
                total += 1
                if self.lex.get_categories_for_word(word):
                    continue
                category, confidence = self.lex.taste(word)
                if category and confidence >= 0.5:
                    tasted += 1
        share = tasted / max(1, total)
        self.assertLess(
            share,
            0.30,
            f"[FAIL] The fallback classifier is deciding {share:.0%} of word "
            f"categories. Grow lore/lexicon.json or raise the thresholds in "
            f"lore/linguistics.json.",
        )

    def test_no_single_category_dominates_the_fallback(self):
        counts = {}
        for line in CORPUS:
            for word in self.lex.clean(line):
                if self.lex.get_categories_for_word(word):
                    continue
                category, confidence = self.lex.taste(word)
                if category and confidence >= 0.5:
                    counts[category] = counts.get(category, 0) + 1
        if sum(counts.values()) < 4:
            self.skipTest("too few fallback verdicts to assess balance")
        top = max(counts.values()) / sum(counts.values())
        self.assertLess(
            top,
            0.80,
            f"[FAIL] One category is {top:.0%} of all fallback verdicts: {counts}",
        )


class LexiconCoverage(unittest.TestCase):
    def setUp(self):
        self.lexicon = json.load(open("lore/lexicon.json", encoding="utf-8"))

    def test_every_mass_key_has_a_category(self):
        """`social` and `void` were weighed by _weigh_mass and had no category at
        all, so BET was structurally zero and void never subtracted."""
        missing = [
            key for key in GeodesicEngine._MASS_KEYS if key not in self.lexicon
        ]
        self.assertEqual(
            missing,
            [],
            f"[FAIL] Mass keys with no lexicon category are permanently zero: "
            f"{missing}",
        )

    def test_mass_categories_are_not_token(self):
        thin = {
            key: len(self.lexicon.get(key, []))
            for key in GeodesicEngine._MASS_KEYS
            if len(self.lexicon.get(key, [])) < 10
        }
        self.assertEqual(thin, {}, f"[FAIL] Thin mass categories: {thin}")


class DimensionBalance(unittest.TestCase):
    def setUp(self):
        self.lex = LexiconService()
        self.lex.initialize()

    def _dimensions(self, line):
        words = self.lex.clean(line)
        counts = QuantumObserver._tally_categories_static(self.lex, words)
        return GeodesicEngine.collapse_wavefunction(words, counts).dimensions

    def test_del_does_not_saturate(self):
        """DEL had the largest amplifier of any dimension and an inflated input,
        so it sat at 1.0 and won every `max()`."""
        saturated = [
            line for line in CORPUS if self._dimensions(line).get("DEL", 0.0) >= 0.999
        ]
        self.assertEqual(
            saturated,
            [],
            f"[FAIL] DEL saturated on {len(saturated)} of {len(CORPUS)} lines.",
        )

    def test_zones_are_reachable(self):
        zones = {
            QuantumObserver._determine_zone(self._dimensions(line))
            for line in CORPUS
        }
        self.assertGreaterEqual(
            len(zones),
            3,
            f"[FAIL] Only reached {zones}. Zoning has no discriminative power.",
        )

    def test_a_clear_winner_selects_its_zone(self):
        self.assertEqual(
            QuantumObserver._determine_zone({"STR": 0.9, "PSI": 0.1}), "THE_FORGE"
        )

    def test_no_clear_winner_falls_back_to_the_courtyard(self):
        """COURTYARD means 'no dominant character'. It was previously reachable
        only from an empty vector, so it never occurred."""
        self.assertEqual(
            QuantumObserver._determine_zone({"STR": 0.50, "PSI": 0.49}), "COURTYARD"
        )

    def test_empty_and_zero_vectors_are_the_courtyard(self):
        self.assertEqual(QuantumObserver._determine_zone({}), "COURTYARD")
        self.assertEqual(
            QuantumObserver._determine_zone({"STR": 0.0, "PSI": 0.0}), "COURTYARD"
        )


if __name__ == "__main__":
    unittest.main()
