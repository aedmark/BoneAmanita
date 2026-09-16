"""struts.py"""

import logging
from typing import Any
from constants import Prisma

logger = logging.getLogger("bone")

def _word_to_vector(word: str, dim: int = 0) -> list:
    """Project a word or passage into the active semantic space.

    Delegates to the single embedder in `spores.embeddings` so that `struts` and
    `spores.spore_utils` can never drift into two different coordinate systems.
    The import is deferred: `spores.embeddings` lives inside the `spores`
    package, so importing it at module scope would execute `spores/__init__`,
    which imports modules that import `struts`.
    """
    from spores.embeddings import SemanticEmbedder, _hash_to_vector

    if dim:
        return _hash_to_vector(word, dim)
    return SemanticEmbedder.get_instance().embed(word)

class ConfigError(KeyError):
    """A config constant the engine needs is absent. Always a bug, never state."""


def require_cfg(obj: Any, key: str, *, where: str) -> Any:
    """Read a config constant that MUST exist. Raises rather than defaulting.

    `safe_get` conflates two different operations: reading a config constant,
    where a miss means the config is wrong, and reading runtime state, where a
    field may legitimately be absent mid-cycle. Only the second deserves a
    default. Conflating them let ten constants sit absent from every config file
    for the life of the project while their subsystems ran on inline fallbacks,
    with no way for anyone tuning the engine to discover it.

    Use this for constants read once at __init__ (which conventions.md requires
    anyway), not inside hot loops.
    """
    value = obj.get(key) if isinstance(obj, dict) else getattr(obj, key, None)
    if value is None:
        raise ConfigError(f"{where}: missing required config key {key!r}")
    return value


def audit_cfg(manifest: dict, resolver) -> list:
    """Check a {block: [keys]} manifest against config. Returns missing paths.

    Reports every miss at once rather than failing on the first, so a bad config
    takes one boot to diagnose instead of ten.
    """
    missing = []
    for block, keys in manifest.items():
        scope = resolver(block)
        for key in keys:
            present = (
                scope.get(key) if isinstance(scope, dict) else getattr(scope, key, None)
            )
            if present is None:
                missing.append(f"{block}.{key}")
    return missing


def ux(section: str, key: str, default: Any = "") -> Any:
    from core import LoreManifest
    data = LoreManifest.get_instance().get("ux_strings", section)
    return data.get(key, default) if isinstance(data, dict) else default

def ux_format(section: str, key: str, default: str = "", **kwargs) -> str:
    msg = ux(section, key, default) or default
    if not msg:
        return ""
    try:
        return str(msg).format(**kwargs)
    except (KeyError, ValueError, IndexError, AttributeError, TypeError) as e:
        logger.warning(
            f"{Prisma.GRY}[UX] Formatting mismatch ({e}) in {section}.{key}. Falling back to raw string.{Prisma.RST}"
        )
        return str(msg)

def safe_get(obj: Any, key: Any, default: Any = None) -> Any:
    if obj is None:
        return default
    keys = key if isinstance(key, (list, tuple)) else (key,)
    is_dict = isinstance(obj, dict)
    for k in keys:
        val = obj.get(k) if is_dict else getattr(obj, k, None)
        if val is not None:
            return val
    return default

def dump_state(obj: Any) -> dict:
    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return obj
    try:
        return vars(obj)
    except TypeError:
        return {k: getattr(obj, k) for k in getattr(obj, "__slots__", []) if hasattr(obj, k)}

def safe_set(obj: Any, key: str, value: Any) -> None:
    if obj is None:
        logger.debug(f"Ignored safe_set for '{key}'; target object is None.")
        return
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)
