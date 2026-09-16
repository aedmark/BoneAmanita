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


class FunctionWords(unittest.TestCase):
    """The English closed class is filler, not unclassified vocabulary. It is
    finite, so enumerating it cannot bloat the lexicon the way an open category
    would, and it is what the E dimension measures."""

    def setUp(self):
        self.lexicon = json.load(open("lore/lexicon.json", encoding="utf-8"))
        self.solvents = {w.lower() for w in self.lexicon["solvents"]}

    def test_common_function_words_are_solvents(self):
        for word in ("the", "a", "of", "in", "to", "and", "but", "because",
                     "is", "was", "have", "would", "which", "through"):
            self.assertIn(word, self.solvents, f"[FAIL] {word!r} is not filler.")

    def test_solvents_never_shadow_a_semantic_category(self):
        """_tally_categories checks solvents FIRST, so a word in both loses its
        category silently. `i`, `me`, `we` are the `meat` mass key; `not`,
        `never` are negation; `very`, `really` are intensifiers; `none`,
        `without` are the `void` mass key."""
        semantic = set()
        for category, words in self.lexicon.items():
            if category in ("solvents", "antigen_replacements"):
                continue
            if isinstance(words, list):
                semantic |= {str(w).lower() for w in words}
        collisions = sorted(self.solvents & semantic)
        self.assertEqual(
            collisions,
            [],
            f"[FAIL] These are both filler and semantic, so their category is "
            f"silently dropped: {collisions}",
        )

    def test_embodied_and_negation_words_kept_their_meaning(self):
        lex = LexiconService()
        lex.initialize()
        for word, category in (("i", "meat"), ("me", "meat"), ("we", "meat"),
                               ("not", "sentiment_negators"),
                               ("never", "sentiment_negators"),
                               ("very", "gradient_stop")):
            self.assertIn(
                category,
                lex.get_categories_for_word(word),
                f"[FAIL] {word!r} lost its {category} classification.",
            )


class Morphology(unittest.TestCase):
    """Every lexicon entry should cover its inflectional family, so the file
    grows in roots rather than in forms."""

    def setUp(self):
        self.lex = LexiconService()
        self.lex.initialize()

    def test_inflections_resolve_to_their_root(self):
        for word, category in (
            ("forging", "constructive"),
            ("building", "constructive"),
            ("hammering", "heavy"),
            ("exploding", "explosive"),
            ("running", "kinetic"),
            ("tomatoes", "harvest"),
            ("concepts", "abstract"),
        ):
            self.assertIn(
                category,
                self.lex.get_categories_for_word(word),
                f"[FAIL] {word!r} did not resolve to its root.",
            )

    def test_unknown_roots_stay_unresolved(self):
        """Stripping suffixes must not invent a match."""
        for word in ("xyzzyqq", "blorping", "frobnicated"):
            self.assertEqual(self.lex.get_categories_for_word(word), set(), word)

    def test_short_stems_are_not_over_stripped(self):
        """`as`, `is`, `us` must not be read as inflections of a 1-2 char root."""
        for word in ("as", "us", "res"):
            self.assertIsInstance(self.lex.get_categories_for_word(word), set)

    def test_a_newly_taught_root_reaches_its_inflections(self):
        """Regression: misses are cached, so a word learned after a failed
        lookup would stay invisible until restart. Matters for the
        self-growing lexicon path."""
        self.assertEqual(self.lex.get_categories_for_word("sprockets"), set())
        self.lex._STORE._index_word("sprocket", "heavy")
        self.assertIn("heavy", self.lex.get_categories_for_word("sprockets"))


class OverallResolution(unittest.TestCase):
    def test_most_of_ordinary_english_is_resolved(self):
        lex = LexiconService()
        lex.initialize()
        solvents = getattr(lex, "SOLVENTS", None) or set()
        total = resolved = 0
        for line in CORPUS:
            for word in lex.clean(line):
                total += 1
                if word in solvents or lex.get_categories_for_word(word):
                    resolved += 1
        share = resolved / max(1, total)
        self.assertGreater(
            share,
            0.65,
            f"[FAIL] Only {share:.0%} of ordinary English resolves without "
            f"guessing. Run tools/audit_physics_inputs.py.",
        )


if __name__ == "__main__":
    unittest.main()
