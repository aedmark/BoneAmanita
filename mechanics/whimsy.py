"""The Ministry's asides: terminal chrome only, never in a reply, a prompt or a snapshot.

An aside is only ever about the engine's own drafts, never about the person, and
never names a reason it does not know. It goes silent unless the person reads as
steady (the threshold /status uses). MAX_SARCASM_LEVEL caps how dry it may get;
the engine's own ROS sets how dry it wants to be. ABSURDITY_CONSTANT is the turn
interval for one line from the absurd pool.
"""

from typing import Optional

from engine.struts import safe_get

# /status reads the person as tiring above this.
STEADY_MAX_EXHAUSTION = 0.4
BANDS = ((8, "withering"), (4, "dry"), (1, "mild"))


def sarcasm_level(ros: float, cap) -> int:
    """ROS 0-100 as a dryness of 0-11, never past the cap."""
    return int(min(float(cap or 0), round(11 * max(0.0, min(100.0, float(ros))) / 100)))


def aside(turn: int, ros: float, exhaustion: float, redrafted: bool, whimsy, lines: dict) -> Optional[str]:
    if exhaustion > STEADY_MAX_EXHAUSTION or not lines:
        return None
    constant = int(safe_get(whimsy, "ABSURDITY_CONSTANT", 0) or 0)
    if constant > 0 and turn > 0 and turn % constant == 0:
        pool = lines.get("absurd") or []
    elif redrafted:
        level = sarcasm_level(ros, safe_get(whimsy, "MAX_SARCASM_LEVEL", 0))
        band = next((name for floor, name in BANDS if level >= floor), None)
        pool = (lines.get(band) or []) if band else []
    else:
        return None
    dept = safe_get(whimsy, "DEPARTMENT_NAME", "") or "The Ministry"
    return pool[turn % len(pool)].format(dept=dept) if pool else None


def ministry_aside(eng, turn: int) -> Optional[str]:
    """This turn's aside, from the engine's receipts, ROS and person model."""
    from engine.core import LoreManifest
    from engine.receipts import ReceiptLedger

    redrafted = any(
        r.subsystem == "cortex.somatic" and r.effect in ("re-asked", "failed")
        for r in ReceiptLedger.get_instance().for_turn()
    )
    u = getattr(getattr(eng, "shared_lattice", None), "u", None)
    exhaustion = float(getattr(u, "E_u", 0.0)) if u is not None else 0.0
    ros = float(eng.bio.mito.state.ros_buildup)
    lines = LoreManifest.get_instance().get("ux_strings", "whimsy_asides") or {}
    return aside(turn, ros, exhaustion, redrafted, safe_get(eng.config, "WHIMSY", {}), lines)
