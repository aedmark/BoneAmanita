"""tests/test_embeddings.py"""

import math
import os
import unittest
from unittest.mock import MagicMock, patch

from spores.embeddings import (
    LEGACY_HASH_DIM,
    SemanticEmbedder,
    _hash_to_vector,
    _l2_normalize,
)


def _fake_response(vectors):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {
        "data": [
            {"index": i, "embedding": list(v)} for i, v in enumerate(vectors)
        ]
    }
    return resp


class EmbedderContract(unittest.TestCase):
    """The guarantees every backend must hold, so callers can stack results."""

    def setUp(self):
        SemanticEmbedder.reset()
        self._env = dict(os.environ)
        os.environ["BONE_EMBED_BACKEND"] = "hash"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        SemanticEmbedder.reset()

    def test_hash_fallback_is_available_offline(self):
        e = SemanticEmbedder.get_instance()
        self.assertEqual(e.backend, "hash")
        self.assertEqual(e.dimension, LEGACY_HASH_DIM)
        self.assertTrue(e.degraded, "[FAIL] Hash backend must self-report as degraded.")

    def test_legacy_hash_projection_is_unchanged(self):
        """The fallback must reproduce the historical vectors exactly."""
        self.assertEqual(
            _hash_to_vector("silence", 8),
            [
                (b / 127.5) - 1.0
                for b in __import__("hashlib")
                .shake_256(b"silence")
                .digest(8)
            ],
        )

    def test_batch_is_rectangular_and_matches_dimension(self):
        e = SemanticEmbedder.get_instance()
        rows = e.embed_batch(["alpha", "beta", "", None, "alpha"])
        self.assertEqual(len(rows), 5)
        for row in rows:
            self.assertEqual(len(row), e.dimension)

    def test_batch_and_single_agree(self):
        e = SemanticEmbedder.get_instance()
        self.assertEqual(e.embed("cartographer"), e.embed_batch(["cartographer"])[0])

    def test_empty_text_is_the_origin(self):
        e = SemanticEmbedder.get_instance()
        self.assertEqual(e.embed("   "), [0.0] * e.dimension)

    def test_explicit_dim_forces_legacy_projection(self):
        """Fixtures must still be able to pin a width without a backend."""
        from spores.spore_utils import _word_to_vector

        self.assertEqual(len(_word_to_vector("node", dim=8)), 8)
        self.assertEqual(_word_to_vector("node", dim=8), _hash_to_vector("node", 8))

    def test_env_outranks_config_overrides(self):
        """BoneConfig.EMBEDDINGS ships populated, so it must not shadow the env."""
        os.environ["BONE_EMBED_MODEL"] = "from-the-environment"
        settings = SemanticEmbedder._resolve_settings({"MODEL": "from-boneconfig"})
        self.assertEqual(settings["MODEL"], "from-the-environment")

    def test_config_overrides_outrank_module_defaults(self):
        os.environ.pop("BONE_EMBED_MODEL", None)
        settings = SemanticEmbedder._resolve_settings({"MODEL": "from-boneconfig"})
        self.assertEqual(settings["MODEL"], "from-boneconfig")

    def test_normalize_handles_zero_vector(self):
        self.assertEqual(_l2_normalize([0.0, 0.0]), [0.0, 0.0])


class HttpBackend(unittest.TestCase):
    """Transport behaviour, exercised without touching the network."""

    def setUp(self):
        SemanticEmbedder.reset()
        self._env = dict(os.environ)
        os.environ["BONE_EMBED_BACKEND"] = "http"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        SemanticEmbedder.reset()

    def test_probe_sets_dimension_from_the_server(self):
        with patch("requests.post", return_value=_fake_response([[0.0] * 384])):
            e = SemanticEmbedder.get_instance()
        self.assertEqual(e.backend, "http")
        self.assertEqual(e.dimension, 384)
        self.assertFalse(e.degraded)

    def test_output_is_unit_length(self):
        with patch("requests.post", return_value=_fake_response([[3.0, 4.0]])):
            e = SemanticEmbedder.get_instance()
        with patch("requests.post", return_value=_fake_response([[3.0, 4.0]])):
            vec = e.embed("pythagoras")
        self.assertAlmostEqual(math.sqrt(sum(v * v for v in vec)), 1.0, places=6)

    def test_cache_prevents_repeat_round_trips(self):
        with patch("requests.post", return_value=_fake_response([[1.0, 0.0]])):
            e = SemanticEmbedder.get_instance()
        with patch("requests.post", return_value=_fake_response([[1.0, 0.0]])) as post:
            e.embed("greenhouse")
            e.embed("greenhouse")
            e.embed("greenhouse")
        self.assertEqual(
            post.call_count, 1, "[FAIL] Repeated text re-hit the embedding endpoint."
        )

    def test_duplicates_within_one_batch_are_requested_once(self):
        with patch("requests.post", return_value=_fake_response([[1.0, 0.0]])):
            e = SemanticEmbedder.get_instance()
        with patch("requests.post", return_value=_fake_response([[1.0, 0.0], [0.0, 1.0]])) as post:
            rows = e.embed_batch(["a", "b", "a"])
        self.assertEqual(post.call_count, 1)
        self.assertEqual(rows[0], rows[2])
        self.assertEqual(len(post.call_args.kwargs["json"]["input"]), 2)

    def test_transient_failure_does_not_latch_to_hash(self):
        """One dropped connection must not permanently blind the Arcade."""
        with patch("requests.post", return_value=_fake_response([[1.0, 0.0]])):
            e = SemanticEmbedder.get_instance()
        with patch("requests.post", side_effect=OSError("connection reset")):
            e.embed("flicker")
        self.assertEqual(e.backend, "http", "[FAIL] A single blip severed the backend.")

    def test_sustained_failure_degrades_to_hash(self):
        with patch("requests.post", return_value=_fake_response([[1.0, 0.0]])):
            e = SemanticEmbedder.get_instance()
        with patch("requests.post", side_effect=OSError("down")):
            for token in ("a", "b", "c", "d"):
                e.embed(token)
        self.assertEqual(e.backend, "hash")
        self.assertTrue(e.degraded)

    def test_failure_still_returns_usable_vectors(self):
        with patch("requests.post", return_value=_fake_response([[1.0, 0.0]])):
            e = SemanticEmbedder.get_instance()
        with patch("requests.post", side_effect=OSError("down")):
            rows = e.embed_batch(["x", "y"])
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(len(r) == len(rows[0]) for r in rows))

    def test_row_count_mismatch_is_rejected(self):
        with patch("requests.post", return_value=_fake_response([[1.0, 0.0]])):
            e = SemanticEmbedder.get_instance()
        with patch("requests.post", return_value=_fake_response([[1.0, 0.0]])):
            with self.assertRaises(ValueError):
                e._http_embed(["one", "two"])

    def test_out_of_order_rows_are_realigned(self):
        """The spec allows any ordering; `index` is authoritative."""
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.json.return_value = {
            "data": [
                {"index": 1, "embedding": [0.0, 1.0]},
                {"index": 0, "embedding": [1.0, 0.0]},
            ]
        }
        with patch("requests.post", return_value=_fake_response([[1.0, 0.0]])):
            e = SemanticEmbedder.get_instance()
        with patch("requests.post", return_value=resp):
            self.assertEqual(e._http_embed(["first", "second"]), [[1.0, 0.0], [0.0, 1.0]])


class IndexWiring(unittest.TestCase):
    """The Arcade must size itself to the embedder, not to a literal."""

    def setUp(self):
        SemanticEmbedder.reset()
        self._env = dict(os.environ)
        os.environ["BONE_EMBED_BACKEND"] = "hash"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        SemanticEmbedder.reset()

    def test_cerebral_index_adopts_embedder_dimension(self):
        from brain.ann import CerebralIndex

        idx = CerebralIndex()
        self.assertEqual(idx.dimension, SemanticEmbedder.get_instance().dimension)

    def test_index_embed_always_matches_its_own_width(self):
        from brain.ann import CerebralIndex

        idx = CerebralIndex(dimension=4)
        self.assertEqual(len(idx.embed("a passage of some length")), 4)

    def test_round_trip_through_the_index(self):
        from brain.ann import CerebralIndex

        idx = CerebralIndex()
        texts = ["the greenhouse", "the segfault", "the shoebox of letters"]
        idx.add_memories(
            [idx.embed(t) for t in texts],
            [{"id": t, "raw_verbatim_text": t, "wing_id": "GLOBAL"} for t in texts],
        )
        hits = idx.query_neighborhood(idx.embed("the greenhouse"), k=1, resonance_threshold=0.0)
        self.assertTrue(hits)
        self.assertEqual(hits[0]["id"], "the greenhouse")


class StrataVectorConsistency(unittest.TestCase):
    """Boot-load and bury() must project into the same space.

    SubconsciousStrata stacks both into one `rank_bank` matrix, so any width
    disagreement between the two paths is an immediate ValueError on vstack -
    and a silent mis-scoring if the widths ever happened to coincide.
    """

    def setUp(self):
        SemanticEmbedder.reset()
        self._env = dict(os.environ)
        os.environ["BONE_EMBED_BACKEND"] = "hash"
        self.path = "test_strata_consistency.json"
        self._cleanup()

    def tearDown(self):
        self._cleanup()
        os.environ.clear()
        os.environ.update(self._env)
        SemanticEmbedder.reset()

    def _cleanup(self):
        for p in (self.path, f"{self.path}l"):
            if os.path.exists(p):
                os.remove(p)

    def test_reload_matches_freshly_buried_width(self):
        from spores.memory import SubconsciousStrata

        strata = SubconsciousStrata(self.path)
        for i in range(4):
            strata.bury({"word": f"relic_{i}", "mass": 1.0})
        buried_width = strata.rank_bank.shape[1]

        reloaded = SubconsciousStrata(self.path)
        self.assertIsNotNone(
            reloaded.rank_bank, "[FAIL] Reload produced no vectors at all."
        )
        self.assertEqual(
            reloaded.rank_bank.shape[1],
            buried_width,
            "[FAIL] _load_index and bury() disagree on vector width.",
        )

    def test_reload_honours_a_patched_vectorizer(self):
        """Both paths must route through the same patchable symbol."""
        import numpy as np

        from spores.memory import SubconsciousStrata

        with patch("spores.memory._word_to_vector") as mock_w2v:
            mock_w2v.side_effect = lambda w: np.zeros(32, dtype=np.float32)
            strata = SubconsciousStrata(self.path)
            for i in range(3):
                strata.bury({"word": f"pinned_{i}", "mass": 1.0})
            reloaded = SubconsciousStrata(self.path)

        self.assertEqual(reloaded.rank_bank.shape[1], strata.rank_bank.shape[1])

    def test_reload_stays_aligned_with_metadata(self):
        from spores.memory import SubconsciousStrata

        strata = SubconsciousStrata(self.path)
        for i in range(6):
            strata.bury({"word": f"aligned_{i}", "mass": 1.0})

        reloaded = SubconsciousStrata(self.path)
        self.assertEqual(
            reloaded.rank_bank.shape[0],
            len(reloaded.metadata_log),
            "[FAIL] rank_bank rows drifted out of step with metadata_log.",
        )


class LiveBackend(unittest.TestCase):
    """Opt-in. Skips unless a real embedding server answers."""

    @classmethod
    def setUpClass(cls):
        if os.environ.get("BONE_EMBED_LIVE_TEST") != "1":
            raise unittest.SkipTest("set BONE_EMBED_LIVE_TEST=1 to run")

    def setUp(self):
        SemanticEmbedder.reset()
        os.environ.pop("BONE_EMBED_BACKEND", None)

    def tearDown(self):
        SemanticEmbedder.reset()

    def test_related_words_beat_unrelated_ones(self):
        """The defect this module exists to fix: `dog` used to sit closer to
        `asphalt` than to `canine`."""
        e = SemanticEmbedder.get_instance()
        if e.degraded:
            self.skipTest("no live backend reachable")

        def cos(a, b):
            return sum(x * y for x, y in zip(e.embed(a), e.embed(b)))

        self.assertGreater(cos("dog", "canine"), cos("dog", "asphalt"))
        self.assertGreater(cos("happy", "joyful"), cos("happy", "quantum"))


if __name__ == "__main__":
    unittest.main()
