"""What `/memory` shows (memory phase 6): what the model keeps, how often recall handed it back, what the
world graph holds, and the gate's latest decisions. Plain lines; the command colours them."""
from __future__ import annotations

import json
import time


def refusal(receipt: dict, text: str, by: str) -> dict | None:
    """What the gate refused and why, for the next prompt and the screen; None when nothing was refused.
    `by` is "keeper" or "model"; the reason never carries a secret."""
    from .secrets import redact
    from .store import proposal_from

    basis = receipt.get("decision_basis") or []
    if not basis or (receipt["decision"] != "DENY" and not any(c[1] == "ERROR" for c in basis)):
        return None
    nominated = proposal_from(text, receipt) or {}
    return {"verb": nominated.get("verb") or "?", "what": nominated.get("what_path") or "?",
            "why": redact(basis[-1][2]), "by": by, "confidential": basis[-1][0] == "screen"}


def refusal_line(r: dict) -> str:
    return f"the gate refused {r['verb']} {r['what']}: {r['why']}"


def _age(ts: float, now: float) -> str:
    secs = max(0, int(now - ts))
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60)):
        if secs >= size:
            return f"{secs // size}{unit} ago"
    return f"{secs}s ago"


def memory_report(state: dict, stats: dict, decisions: list, cap: int, embedder: str,
                  needle: str = "", limit: int = 30, now: float | None = None) -> list[str]:
    now = time.time() if now is None else now
    memory = ((state or {}).get("self") or {}).get("memory", {}) or {}
    world = (state or {}).get("world") or {}
    nodes = world.get("nodes", {}) or {}
    active = [e for e in world.get("edges", []) or [] if e.get("status", "active") == "active"]
    lines = [f"MEMORY: {len(memory)} kept of {cap} (forgetting starts at {int(cap * 0.9)}). Embedder: {embedder}."]

    shown = [(k, v) for k, v in reversed(list(memory.items()))
             if not needle or needle.lower() in f"{k} {v}".lower()]
    if needle:
        lines.append(f"Matching '{needle}': {len(shown)}.")
    for key, value in shown[:limit]:
        count, last = stats.get(key, (0, 0.0))
        heard = f"recalled {count}x, last {_age(last, now)}" if count else "never recalled"
        lines.append(f"  {key}: {value}  ({heard})")
    if len(shown) > limit:
        lines.append(f"  ...and {len(shown) - limit} more (newest first; /memory <word> to filter).")
    if not memory:
        lines.append("  Nothing kept yet.")

    rooms = sum(1 for n in nodes.values() if n.get("type") == "room")
    lines.append(f"WORLD: {len(nodes)} nodes ({rooms} charted rooms), {len(active)} active links, "
                 f"{len(world.get('constraints', []) or [])} constraints.")

    lines.append("RECENT GATE DECISIONS:" if decisions else "RECENT GATE DECISIONS: none yet.")
    for d in decisions:
        basis = json.loads(d.get("decision_basis_json") or "[]")
        why = f": {basis[-1][2]}" if d["decision"] != "ACCEPT" and basis else ""
        result = json.loads(d.get("result_json") or "null") or {}
        noop = " (no change)" if isinstance(result, dict) and "noop" in result else ""
        lines.append(f"  {_age(d['created_at'], now):>8}  {d['decision']:<6} {d.get('verb') or '?'} "
                     f"{d.get('what_path') or ''}{noop}{why}")
    return lines
