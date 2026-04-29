"""spores/spore_utils.py"""

import hashlib

def _word_to_vector(word: str, dim: int = 8) -> list:
    h = hashlib.md5(word.encode("utf-8")).digest()
    return [(b / 127.5) - 1.0 for b in h[:dim]]

def _identity(n=8):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

def _mat_mul(A, B):
    B_cols = list(zip(*B))
    return [[sum(a * b for a, b in zip(row, col)) for col in B_cols] for row in A]

def _reorthogonalize(M):
    n = len(M)
    out = [[0.0] * n for _ in range(n)]
    for j in range(n):
        v = [M[i][j] for i in range(n)]
        for k in range(j):
            u = [out[i][k] for i in range(n)]
            proj = sum(v[idx] * u[idx] for idx in range(n))
            v = [v[i] - proj * u[i] for i in range(n)]
        norm = max(1e-10, sum(x * x for x in v)**0.5)
        for i in range(n):
            out[i][j] = v[i] / norm
    return out

def _householder(v):
    mag_sq = sum(x * x for x in v)
    if mag_sq == 0:
        return _identity(len(v))
    n = len(v)
    out = []
    for i in range(n):
        row_scalar = 2.0 * v[i] / mag_sq
        out.append([(1.0 if i == j else 0.0) - row_scalar * v[j] for j in range(n)])
    return out

def _access_config_path(root, path, value=None, set_mode=False):
    target = root
    parts = path.split(".")
    try:
        for part in parts[:-1]:
            target = (target.get(part) if isinstance(target, dict) else getattr(
                target, part))
            if target is None:
                return None
        leaf = parts[-1]
        is_dict = isinstance(target, dict)
        if set_mode:
            curr = target.get(leaf) if is_dict else getattr(target, leaf)
            if isinstance(curr, (int, float)):
                if is_dict:
                    target[leaf] = value
                else:
                    setattr(target, leaf, value)
                return True
            return False
        return target.get(leaf) if is_dict else getattr(target, leaf, None)
    except (AttributeError, KeyError, TypeError):
        return None