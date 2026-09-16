"""spores/spore_utils.py"""

from typing import List

from spores.embeddings import LEGACY_HASH_DIM, SemanticEmbedder, _hash_to_vector


def _word_to_vector(word: str, dim: int = 0) -> List[float]:
    """Project a word or passage into the active semantic space.

    Returns the backend's NATIVE dimensionality. Pass an explicit `dim` only to
    force the legacy SHAKE-256 projection at a fixed width (tests, fixtures);
    truncating a real embedding to 8 components would throw away the signal this
    function exists to provide.
    """
    if dim:
        return _hash_to_vector(word, dim)
    return SemanticEmbedder.get_instance().embed(word)


def _words_to_matrix(words) -> List[List[float]]:
    """Batch form. One round trip for the whole list instead of one per word."""
    return SemanticEmbedder.get_instance().embed_batch(list(words))


def _vector_dimension() -> int:
    return SemanticEmbedder.get_instance().dimension


__all__ = [
    "_word_to_vector",
    "_words_to_matrix",
    "_vector_dimension",
    "LEGACY_HASH_DIM",
]
