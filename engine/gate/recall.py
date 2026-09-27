"""What the model gets back from the Halcyon store each turn: its own memories, and the world facts
that bear on what was just said. Everything here was admitted by the gate; nothing is inferred."""
from __future__ import annotations

import hashlib
import math
import re

_WORD = re.compile(r"[a-z0-9']+")


def _words(text) -> set:
    return {w for w in _WORD.findall(str(text or "").lower()) if len(w) > 2}


def _cosine(a, b) -> float:
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return sum(x * y for x, y in zip(a, b)) / norm if norm > 1e-12 else 0.0


def meaning_scores(state: dict, text: str, store, embedder):
    """Each memory's similarity to `text`. A memory is embedded once per content and model, and kept in
    the store. None when the embedder is on its hash fallback, whose vectors carry no meaning."""
    memory = ((state or {}).get("self") or {}).get("memory", {}) or {}
    if not memory or embedder is None or embedder.degraded:
        return None
    model = f"{embedder.backend}:{embedder.model}"
    kept = store.memory_vectors()
    texts = {k: f"{k}: {v}" for k, v in memory.items()}
    hashes = {k: hashlib.sha256(t.encode("utf-8")).hexdigest()[:16] for k, t in texts.items()}
    missing = [k for k in memory if kept.get(k, (None, None))[:2] != (hashes[k], model)]
    vectors = embedder.embed_batch([text] + [texts[k] for k in missing])
    if embedder.degraded:
        return None
    fresh = dict(zip(missing, vectors[1:]))
    if fresh or set(kept) - set(memory):
        store.save_memory_vectors([(k, hashes[k], model, v) for k, v in fresh.items()], keep=set(memory))
    return {k: _cosine(vectors[0], fresh[k] if k in fresh else kept[k][2]) for k in memory}


def recall(state: dict, text: str, max_memories: int = 12, max_facts: int = 12, scores: dict | None = None) -> dict:
    """Memories ranked by meaning when `scores` are given, else by word overlap with `text`; facts by word
    overlap. Ties go to recency (later writes first)."""
    query = _words(text)

    memory = list(((state or {}).get("self") or {}).get("memory", {}).items())
    if scores is not None:
        rank = lambda im: (scores.get(im[1][0], -1.0), im[0])
    else:
        rank = lambda im: (len(query & _words(f"{im[1][0]} {im[1][1]}")), im[0])
    ranked = sorted(enumerate(memory), key=rank, reverse=True)
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
    return {
        "memories": memories,
        "facts": chosen,
        "held": {"memories": len(memory), "facts": len(facts)},
        "ranked_by": "meaning" if scores is not None else "words",
    }
