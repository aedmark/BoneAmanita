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


_WHO = {"keeper": "the memory keeper", "model": "the model", "cartographer": "the cartographer"}


def _kept(meta: dict | None, now: float) -> str:
    if not meta:
        return ""
    return f"kept {_age(meta['kept_at'], now)} in {meta.get('mode') or 'an unrecorded mode'} by {_WHO.get(meta.get('kept_by'), 'the model')}; "


def _source(p: dict | None) -> list[str]:
    """What a commit's receipt says: the person's words that turn, and the gate's checks."""
    if not p:
        return ["    (its receipt is gone)"]
    said = " ".join(str(p.get("user_text") or "").split())
    lines = [f'    The person said: "{said[:160]}{"..." if len(said) > 160 else ""}"'] if said else []
    if p.get("recalled_json") is not None:
        recalled, facts = json.loads(p["recalled_json"]), json.loads(p.get("facts_json") or "[]")
        count = lambda n, one, many: f"{n} {one if n == 1 else many}"
        handed = f"{count(len(recalled), 'memory', 'memories')} ({', '.join(recalled)})" if recalled else "no memories"
        refusal = ", and a refusal note" if p.get("refusal_json") else ""
        size = f"; the prompt was {p['input_tokens']:,} of {p['context_limit']:,} tokens" if p.get("input_tokens") and p.get("context_limit") else ""
        lines.append(f"    The model had been handed {handed} and {count(len(facts), 'fact', 'facts')}{refusal}{size}.")
    basis = json.loads(p.get("decision_basis_json") or "[]")
    return lines + [f"    The gate: {', '.join(f'{stage} {verdict}' for stage, verdict, *_ in basis)}."]


def why_report(name: str, state: dict, meta: dict, stats: dict, provenance, now: float | None = None) -> list[str]:
    """`/memory why <name>`: where a memory or a world node came from. `provenance(receipt_id)` looks a commit up."""
    from .feeling import describe
    from .recall import STORY

    now = time.time() if now is None else now
    memory = ((state or {}).get("self") or {}).get("memory", {}) or {}
    key = next((k for k in (name, STORY + name) if k in memory), None)
    if key:
        lines = [f"{key}: {memory[key]}"]
        m = meta.get(key)
        if not m or not m.get("receipt_id"):
            lines.append("  Kept before its source was recorded.")
        else:
            kept = _kept(m, now)[:-2]
            lines.append(f"  {kept[0].upper()}{kept[1:]}.")
            if felt := describe(m.get("feeling")):
                lines.append(f"  Felt: {felt}.")
            lines += _source(provenance(m["receipt_id"]))
        count, last = stats.get(key, (0, 0.0))
        lines.append(f"  Recalled {count}x, last {_age(last, now)}." if count else "  Never recalled yet.")
        return lines
    world = (state or {}).get("world") or {}
    node_id, node = next(((i, n) for i, n in (world.get("nodes") or {}).items()
                          if str(n.get("label", "")).lower() == name.lower()), (None, None))
    if node is None:
        return [f"Nothing kept under '{name}'."]
    lines = [f"{node.get('label')} ({node.get('type', 'thing')}), written by {len(node.get('sources') or [])} commit(s):"]
    for rid in reversed(node.get("sources") or []):
        src = (world.get("sources") or {}).get(rid, {})
        lines.append(f"  {src.get('verb') or '?'} {_age(src.get('at', now), now)} in {src.get('mode') or 'an unrecorded mode'} "
                     f"by {_WHO.get(src.get('by'), 'the model')}")
        lines += _source(provenance(rid))
    links = sum(1 for e in world.get("edges", []) or [] if e.get("status", "active") == "active" and node_id in (e["source"], e["target"]))
    lines.append(f"  {links} active link(s).")
    return lines


def memory_report(state: dict, stats: dict, decisions: list, cap: int, embedder: str,
                  needle: str = "", limit: int = 30, now: float | None = None, meta: dict | None = None) -> list[str]:
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
        lines.append(f"  {key}: {value}  ({_kept((meta or {}).get(key), now)}{heard})")
    if len(shown) > limit:
        lines.append(f"  ...and {len(shown) - limit} more (newest first; /memory <word> to filter, /memory why <name> to trace).")
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
