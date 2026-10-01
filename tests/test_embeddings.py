"""tests/test_embeddings.py"""

import math
import os
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
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


    def test_the_rem_tick_checks_a_lost_backend(self):
        from tests.base import BoneTestCase

        class Case(BoneTestCase):
            def runTest(self):
                with patch.object(SemanticEmbedder, "reprobe") as reprobe:
                    self.engine.orchestrator._process_rem_tick()
                reprobe.assert_called_once_with()

        result = unittest.TextTestRunner(stream=open(os.devnull, "w")).run(Case())
        self.assertTrue(result.wasSuccessful(), result.failures + result.errors)
