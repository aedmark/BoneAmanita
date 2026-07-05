"""spores/spore_utils.py"""

import hashlib


def _word_to_vector(word: str, dim: int = 8) -> list:
    h = hashlib.shake_256(word.encode("utf-8")).digest(dim)
    return [(b / 127.5) - 1.0 for b in h]
