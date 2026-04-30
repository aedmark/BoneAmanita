"""struts.py"""

from typing import Any

from constants import Prisma

# =============================================================================
# LINGUISTIC & STRUCTURAL UTILITIES
# =============================================================================

def ux(section: str, key: str, default: Any = "") -> Any:
    """
    Retrieves localized, user-facing strings from the Lore cache.
    Decouples narrative text from hardcoded logic to prevent semantic rot.
    """
    from core import LoreManifest
    data = LoreManifest.get_instance().get("ux_strings", section)
    return data.get(key, default) if isinstance(data, dict) else default


def ux_format(section: str, key: str, default: str = "", **kwargs) -> str:
    """
    Retrieves and safely formats a UX string.
    Fails gracefully to the raw string if the payload arguments mismatch the template.
    """
    msg = ux(section, key, default) or default
    if not msg:
        return ""
    try:
        return msg.format(**kwargs)
    except (KeyError, ValueError, IndexError) as e:
        # Pinker note: We log the grammatical failure but do not crash the engine.
        print(f"{Prisma.GRY}[UX] Formatting mismatch ({e}) in {section}.{key}. Falling back to raw string.{Prisma.RST}")
        return msg


def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Agnostic retriever for dictionaries or class attributes."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        val = obj.get(key, default)
    else:
        val = getattr(obj, key, default)
    return default if val is None else val


def safe_set(obj: Any, key: str, value: Any) -> None:
    """
    Agnostic setter. Includes a physical structural warning.
    Writing to a Void (None) is a symptom of architectural decay.
    """
    if obj is None:
        print(f"{Prisma.RED}[STRUCTURAL ROT] safe_set swallowed a write to '{key}'. Target object is None.{Prisma.RST}")
        return
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)
