"""tests/test_resonance.py

Semantic classification of unknown words (ROADMAP A5 step 3).

Words the curated lexicon does not know used to fall through to a
phonosemantic classifier, which scores spelling rather than meaning. They are
now resolved against embedding centroids built from the curated categories, and
a confident verdict is taught into the separate LEARNED_VOCAB hive.

Most tests here run offline: the suite pins the hash embedding backend, where
the classifier correctly refuses to build because hash vectors carry no meaning.
The quality assertions are gated behind BONE_EMBED_LIVE_TEST=1.
"""

import json
import os
import unittest

from mechanics.lexicon import LexiconService
from mechanics.resonance import RESONANT_CATEGORIES, ResonanceClassifier
from spores.embeddings import SemanticEmbedder


class DegradedBackend(unittest.TestCase):
    """With no real embedder, this must decline rather than guess."""

    def setUp(self):
        SemanticEmbedder.reset()
        self._env = dict(os.environ)
        os.environ["BONE_EMBED_BACKEND"] = "hash"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        SemanticEmbedder.reset()

    def test_refuses_to_build_on_hash_vectors(self):
        classifier = ResonanceClassifier()
        vocab = json.load(open("lore/lexicon.json", encoding="utf-8"))
        self.assertFalse(classifier.build(vocab))
        self.assertFalse(classifier.ready)
        self.assertIn("degraded", classifier.detail)

    def test_classify_is_inert_when_not_ready(self):
        self.assertEqual(ResonanceClassifier().classify("glacier"), (None, 0.0))

    def test_resolution_still_works_without_an_embedder(self):
        """The curated lexicon and morphology need no server."""
        lex = LexiconService()
        lex.initialize()
        self.assertIn("constructive", lex.get_categories_for_word("forging"))
        self.assertEqual(lex.resolve_unknown("glacieresque"), set())


class Configuration(unittest.TestCase):
    def test_resonant_categories_all_exist(self):
        vocab = json.load(open("lore/lexicon.json", encoding="utf-8"))
        missing = [c for c in RESONANT_CATEGORIES if c not in vocab]
        self.assertEqual(missing, [], f"[FAIL] Unknown categories: {missing}")

    def test_centroids_exclude_multi_word_phrases(self):
        """Categories legitimately contain phrases ("black hole" is heavy), but
        embedding them into a single-word centroid would blur it. The builder
        filters them; this pins that it keeps doing so."""
        vocab = json.load(open("lore/lexicon.json", encoding="utf-8"))
        with_phrases = {
            category: [w for w in vocab.get(category, []) if " " in str(w)]
            for category in RESONANT_CATEGORIES
        }
        if not any(with_phrases.values()):
            self.skipTest("no phrase entries in any resonant category")
        captured = {}

        class Recorder:
            def embed_batch(self, words):
                captured["words"] = list(words)
                return [[0.0, 0.0] for _ in words]

            degraded = False

        import mechanics.resonance as resonance_module
        import spores.embeddings as embeddings_module

        original = embeddings_module.SemanticEmbedder.get_instance
        embeddings_module.SemanticEmbedder.get_instance = staticmethod(
            lambda *a, **k: Recorder()
        )
        try:
            ResonanceClassifier().build(vocab)
        finally:
            embeddings_module.SemanticEmbedder.get_instance = original
        offenders = [w for w in captured.get("words", []) if " " in w]
        self.assertEqual(
            offenders, [], f"[FAIL] Phrases reached the centroid: {offenders[:3]}"
        )


class LiveClassification(unittest.TestCase):
    """Opt-in. Needs a real embedding backend."""

    @classmethod
    def setUpClass(cls):
        if os.environ.get("BONE_EMBED_LIVE_TEST") != "1":
            raise unittest.SkipTest("set BONE_EMBED_LIVE_TEST=1 to run")

    def setUp(self):
        SemanticEmbedder.reset()
        os.environ.pop("BONE_EMBED_BACKEND", None)
        self.classifier = ResonanceClassifier()
        vocab = json.load(open("lore/lexicon.json", encoding="utf-8"))
        if not self.classifier.build(vocab):
            self.skipTest(f"no live backend: {self.classifier.detail}")

    def tearDown(self):
        SemanticEmbedder.reset()

    def test_clear_words_classify_correctly(self):
        for word, expected in (
            ("glacier", "cryo"),
            ("cathedral", "sacred"),
            ("shovel", "heavy"),
        ):
            category, margin = self.classifier.classify(word)
            self.assertEqual(category, expected, f"{word} -> {category} ({margin})")

    def test_ambiguous_words_are_declined(self):
        """`letter` really does sit between social and sacred. Declining is the
        correct answer, not a failure."""
        for word in ("letter", "laughter"):
            category, _ = self.classifier.classify(word)
            self.assertIsNone(category, f"[FAIL] {word} should be ambiguous.")

    def test_nonsense_is_declined(self):
        self.assertIsNone(self.classifier.classify("xyzzyqq")[0])

    def test_mean_centring_produces_usable_margins(self):
        """The load-bearing detail: raw centroids rank correctly and separate
        uselessly (mean margin ~0.03). Centring lifts that enough for a margin
        gate to discriminate at all."""
        margins = [
            self.classifier.classify(w)[1]
            for w in ("glacier", "cathedral", "shovel", "night")
        ]
        self.assertGreater(
            sum(margins) / len(margins),
            0.10,
            f"[FAIL] Margins collapsed to {margins}; centring is not working.",
        )


class LearningDestination(unittest.TestCase):
    """Machine guesses must not contaminate the hand-curated lexicon."""

    def test_curated_lexicon_is_not_written_by_classification(self):
        before = open("lore/lexicon.json", encoding="utf-8").read()
        lex = LexiconService()
        lex.initialize()
        lex.resolve_unknown("someunlikelyword")
        self.assertEqual(
            before,
            open("lore/lexicon.json", encoding="utf-8").read(),
            "[FAIL] resolve_unknown wrote to the curated lexicon. Learned words "
            "belong in LEARNED_VOCAB, which is capped, evictable and revertable.",
        )

    def test_teaching_indexes_for_future_lookups(self):
        """The embedding cost is paid once per word, not per occurrence."""
        lex = LexiconService()
        lex.initialize()
        lex._STORE.teach("quernstone", "heavy", 0)
        self.assertIn("heavy", lex.get_categories_for_word("quernstone"))


if __name__ == "__main__":
    unittest.main()
