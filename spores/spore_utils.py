"""spores/spore_utils.py"""

import hashlib

def _word_to_vector(word: str, dim: int = 8) -> list:
    h = hashlib.shake_256(word.encode("utf-8")).digest(dim)
    return [(b / 127.5) - 1.0 for b in h]

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
            curr = target.get(leaf) if is_dict else getattr(target, leaf, None)
            if isinstance(curr, (int, float)) and not isinstance(curr, bool):
                if is_dict:
                    target[leaf] = value
                else:
                    setattr(target, leaf, value)
                return True
            return False
        return target.get(leaf) if is_dict else getattr(target, leaf, None)
    except (AttributeError, KeyError, TypeError):
        return False if set_mode else None
