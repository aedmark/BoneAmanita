"""/tune (ROADMAP A7): one config value changed at runtime, on both config objects, and an honest word on when it
takes effect. The risk is a knob that reports success and changes nothing: six modules read the BoneConfig class,
the engine reads its instance, many subsystems copy a value at boot, and /mode rewrites GATE_TOLERANCE."""

import json
import os
from typing import Any, Dict, Optional, Tuple

from engine.gate.secrets import credential_key
from engine.presets import BoneConfig

# Proven live by a test that tunes each and sees the behaviour change (tests/test_tune.py); grow one key at a time.
LIVE = frozenset({
    "WHIMSY.LUDICROUS_SPEED",
    "BIO.DECAY_RATE",
    "CORTEX.VALIDATOR_STUTTER_LENGTH",
    "SOMATIC_BUDGET.ATP_DEPLETED",
    "ROOT.GATE_TOLERANCE",
})
RESET_BY_MODE = frozenset({"ROOT.GATE_TOLERANCE"})
SAVED = "TUNED"  # config.json's block for saved tunings, applied at boot
_BOOLS = {"true": True, "on": True, "yes": True, "false": False, "off": False, "no": False}


def parse(raw: str, current: Any) -> Optional[Any]:
    """raw read as current's type (bools take true/false/on/off/yes/no); None if it does not fit."""
    if isinstance(current, bool):
        return _BOOLS.get(str(raw).lower())
    for kind in (int, float):
        if isinstance(current, kind):
            try:
                return kind(raw)
            except (TypeError, ValueError):
                return None
    return str(raw) if isinstance(current, str) else None


def sector_names(config) -> list:
    return ["ROOT"] + sorted(k for k in getattr(BoneConfig, "_TEMPLATE_DATA", {}) if hasattr(config, k))


def _holder(config, sector: str):
    return config if sector == "ROOT" else getattr(config, sector, None)


def settings(config, sector: str) -> Dict[str, Any]:
    """The scalar values a sector holds (never a credential); dicts and lists are not tunable from a command."""
    holder = _holder(config, sector)
    if holder is None:
        return {}
    names = (k for k in dir(holder) if k.isupper()) if sector == "ROOT" else vars(holder)
    found = {k: getattr(holder, k) for k in names}
    return {k: v for k, v in sorted(found.items())
            if isinstance(v, (bool, int, float, str)) and not credential_key(k)}


def when(key: str) -> str:
    if key in RESET_BY_MODE:
        return "now; the next /mode resets it"
    return "now" if key in LIVE else "at the next start (it is read once at start-up)"


def apply(engine, sector: str, name: str, raw: Any, by: str = "/tune") -> Tuple[bool, str]:
    """Set sector.name on the engine's config and the BoneConfig class. (ok, what to tell the person)."""
    sector, name = sector.upper(), name.upper()
    config = engine.config
    here = settings(config, sector)
    if name not in here:
        return False, f"{sector}.{name} is not a setting /tune can change."
    old = here[name]
    value = parse(str(raw), old)  # a command sends text, config.json sends JSON; both are read as old's type
    if value is None:
        return False, f"{sector}.{name} takes a {type(old).__name__}; got {raw!r}."
    holders = [h for h in (_holder(config, sector), _holder(BoneConfig, sector)) if h is not None]
    for holder in holders:
        setattr(holder, name, value)
    if errors := config.validate_integrity():
        for holder in holders:
            setattr(holder, name, old)
        return False, f"{sector}.{name} was left at {old}: " + " | ".join(errors)
    key = f"{sector}.{name}"
    tuned = engine.__dict__.setdefault("tuned", {})
    stock = tuned.get(key, {}).get("stock", old)
    tuned[key] = {"stock": stock, "value": value, "live": key in LIVE}
    from engine.receipts import issue

    issue("config.tune", "live" if key in LIVE else "at next start", result_count=1,
          inputs={"key": key, "from": old, "to": value, "by": by})
    return True, f"{key}: {old} -> {value}. Takes effect {when(key)}."


def save(path: str, sector: str, name: str, value: Any) -> str:
    """Keep a tuning in the person's own config.json (gitignored), never in lore/; it is applied at boot."""
    data = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    data.setdefault(SAVED, {})[f"{sector.upper()}.{name.upper()}"] = value
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def apply_saved(engine, sys_config: dict) -> list:
    """The tunings config.json keeps, applied at boot the same way /tune applies them."""
    lines = []
    for key, value in (sys_config.get(SAVED) or {}).items():
        sector, _, name = str(key).partition(".")
        _, line = apply(engine, sector, name, value, by="config.json")
        lines.append(line)
    return lines
