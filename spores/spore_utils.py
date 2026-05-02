"""spores/spore_utils.py

This module contains the lowest-level mathematical and structural primitives of the engine.
It is pure, stateless geometry. These functions form the bedrock that allows the
Subconscious Matrices (M_t and Q_n) in memory.py to rotate, decay, and store semantic
meaning as multi-dimensional coordinates.
"""

import hashlib

def _word_to_vector(word: str, dim: int = 8) -> list:
    """
    Synergetic Coordinate Mapping.
    Converts any arbitrary word into a deterministic, normalized vector in N-dimensional space.
    Uses SHAKE-256 (an Extendable-Output Function) to guarantee exactly `dim` bytes,
    preventing structural collapse if the matrix is ever scaled beyond 16 dimensions.

    The resulting coordinates are normalized to sit between -1.0 and 1.0.
    """
    # Fuller: Generate exactly 'dim' bytes dynamically to support infinite dimensional scaling.
    h = hashlib.shake_256(word.encode("utf-8")).digest(dim)
    return [(b / 127.5) - 1.0 for b in h]

def _identity(n=8):
    """
    Generates an NxN Identity Matrix (1s on the diagonal, 0s elsewhere).
    This represents a "blank slate" narrative trajectory before any memories warp it.
    """
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

def _mat_mul(A, B):
    """
    Standard matrix multiplication (A * B).
    Written in pure Python list comprehensions to avoid heavy external dependencies.
    """
    # Zip(*B) transposes matrix B, making it much faster to iterate over its columns.
    B_cols = list(zip(*B))
    return [[sum(a * b for a, b in zip(row, col)) for col in B_cols] for row in A]

def _reorthogonalize(M):
    """
    Systems Dynamic: Entropy Correction (The Gram-Schmidt Process).
    When you multiply matrices thousands of times (like we do when burying memories),
    floating-point rounding errors accumulate. Eventually, an orthogonal matrix will
    deform and collapse, completely destroying the mathematical memory structure.

    This function forces the matrix back into a state of perfect structural tensegrity,
    ensuring the engine's long-term memory remains mathematically viable forever.
    """
    n = len(M)
    out = [[0.0] * n for _ in range(n)]

    for j in range(n):
        # Extract the j-th column
        v = [M[i][j] for i in range(n)]

        # Subtract the projections of all previously processed columns
        for k in range(j):
            u = [out[i][k] for i in range(n)]
            proj = sum(v[idx] * u[idx] for idx in range(n))
            v = [v[i] - proj * u[i] for i in range(n)]

        # Normalize the resulting vector so its magnitude is exactly 1.0
        norm = max(1e-10, sum(x * x for x in v)**0.5)
        for i in range(n):
            out[i][j] = v[i] / norm

    return out

def _householder(v):
    """
    Generates a Householder Reflection Matrix.
    Used in `network.py` when a "Scar" is recorded. If the system encounters a
    traumatic paradox, this function acts as a mathematical flinch—it reflects
    the entire cognitive coordinate space away from that specific concept vector.
    """
    mag_sq = sum(x * x for x in v)

    # If the vector is perfectly zero (empty void), do nothing; return the identity.
    if mag_sq == 0:
        return _identity(len(v))

    n = len(v)
    out = []

    # Construct the reflection matrix: I - 2 * (v * v^T) / ||v||^2
    for i in range(n):
        row_scalar = 2.0 * v[i] / mag_sq
        out.append([(1.0 if i == j else 0.0) - row_scalar * v[j] for j in range(n)])

    return out

def _access_config_path(root, path, value=None, set_mode=False):
    """
    Language Clarity: A dot-notation accessor for deeply nested dictionaries or objects.
    Allows the Genetics module to say "PHYSICS.VOLTAGE_MAX" and mutate it,
    without needing to write recursive try/except blocks everywhere.
    """
    target = root
    parts = path.split(".")

    try:
        # Traverse the tree up to the final leaf node
        for part in parts[:-1]:
            target = (target.get(part) if isinstance(target, dict) else getattr(
                target, part))
            if target is None:
                return None

        # Handle the actual mutation or retrieval on the final leaf
        leaf = parts[-1]
        is_dict = isinstance(target, dict)

        if set_mode:
            curr = target.get(leaf) if is_dict else getattr(target, leaf, None)

            # Meadows & Pinker: Python considers 'bool' a subclass of 'int'.
            # We must explicitly exclude booleans to prevent genetic drift from turning flags into floats.
            if isinstance(curr, (int, float)) and not isinstance(curr, bool):
                if is_dict:
                    target[leaf] = value
                else:
                    setattr(target, leaf, value)
                return True
            return False

        # Just return the value
        return target.get(leaf) if is_dict else getattr(target, leaf, None)

    except (AttributeError, KeyError, TypeError):
        # Fail gracefully with consistent return types if the path doesn't exist
        return False if set_mode else None