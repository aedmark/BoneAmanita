"""struts.py"""

from typing import Any

from constants import Prisma


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
        import logging
        logging.getLogger("bone").warning(
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
        import logging
        logging.getLogger("bone").debug(f"Ignored safe_set for '{key}'; target object is None.")
        return
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)
