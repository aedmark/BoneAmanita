"""What the model gets back from the Halcyon store each turn: its own memories, and the world facts
that bear on what was just said. Everything here was admitted by the gate; nothing is inferred."""
from __future__ import annotations

import re

_WORD = re.compile(r"[a-z0-9']+")


def _words(text) -> set:
    return {w for w in _WORD.findall(str(text or "").lower()) if len(w) > 2}


def recall(state: dict, text: str, max_memories: int = 12, max_facts: int = 12) -> dict:
    """Memories and facts ranked by word overlap with `text`, then by recency (later writes first)."""
    query = _words(text)

    memory = list(((state or {}).get("self") or {}).get("memory", {}).items())
    ranked = sorted(enumerate(memory), key=lambda im: (len(query & _words(f"{im[1][0]} {im[1][1]}")), im[0]), reverse=True)
    memories = [kv for _, kv in ranked[:max(0, max_memories)]]

    world = (state or {}).get("world") or {}
    nodes = world.get("nodes", {}) or {}

    def label(node_id):
        return (nodes.get(node_id) or {}).get("label") or str(node_id).split(":", 1)[-1]

    facts = [
        (f"{label(e['source'])} {e['relation']} {label(e['target'])}", {e["source"], e["target"]})
        for e in world.get("edges", []) or []
        if e.get("status", "active") == "active"
    ]
    facts += [(f"{label(c['target'])}: {c['rule']} {c['value']}", {c["target"]}) for c in world.get("constraints", []) or []]
    facts += [
        (f"{n.get('label', node_id)} ({n.get('type', 'thing')})", {node_id})
        for node_id, n in nodes.items()
        if n.get("type") not in (None, "reference") and not any(node_id in ids for _, ids in facts)
    ]
    mentioned = {node_id for node_id, n in nodes.items() if _words(n.get("label")) and _words(n.get("label")) <= query}
    ranked_facts = sorted(
        enumerate(facts),
        key=lambda iF: (bool(iF[1][1] & mentioned), len(query & _words(iF[1][0])), iF[0]),
        reverse=True,
    )
    chosen = [fact for _, (fact, _) in ranked_facts[:max(0, max_facts)]]
    return {"memories": memories, "facts": chosen, "held": {"memories": len(memory), "facts": len(facts)}}
