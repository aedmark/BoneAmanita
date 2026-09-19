from typing import List

from spores.embeddings import LEGACY_HASH_DIM, SemanticEmbedder, _hash_to_vector


def _word_to_vector(word: str, dim: int = 0) -> List[float]:
    if dim:
        return _hash_to_vector(word, dim)
    return SemanticEmbedder.get_instance().embed(word)

def _words_to_matrix(words) -> List[List[float]]:
    return SemanticEmbedder.get_instance().embed_batch(list(words))

def _vector_dimension() -> int:
    return SemanticEmbedder.get_instance().dimension

__all__ = [
    "_word_to_vector",
    "_words_to_matrix",
    "_vector_dimension",
    "LEGACY_HASH_DIM",
]
