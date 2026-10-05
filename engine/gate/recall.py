"""What the model gets back from the Halcyon store each turn: its own memories, and the world facts
that bear on what was just said. Everything here was admitted by the gate; nothing is inferred."""
from __future__ import annotations

import hashlib
import math
import re

_WORD = re.compile(r"[a-z0-9']+")
# The keeper's prefix for what ADVENTURE keeps, so a story's "user_name" never overwrites the person's.
STORY = "story."


def zone(mode) -> str:
    """ADVENTURE is the story; the other modes share what the person told them (Gordon, 2026-09-28)."""
    return "story" if mode == "ADVENTURE" else "real"


def zone_of(key: str, modes: dict) -> str:
    """A memory's zone, by the mode it was kept in; one with no recorded mode goes by its key."""
    return zone(modes[key]) if key in modes else ("story" if key.startswith(STORY) else "real")


def zoned(state: dict, modes: dict, mode) -> dict:
    """`state` with only the memories of `mode`'s zone."""
    memory = ((state or {}).get("self") or {}).get("memory", {}) or {}
    here = {k: v for k, v in memory.items() if zone_of(k, modes) == zone(mode)}
    return {**state, "self": {**(state.get("self") or {}), "memory": here}}


# A value still being weighed, planned or waited on; the keeper can also mark one "(open)" (Gordon, 2026-10-05).
_OPEN = re.compile(r"\b(?:consider(?:s|ing)?|thinking (?:about|of)|plan(?:s|ning)? to|deciding|undecided|unsure|not sure|"
                   r"waiting (?:for|on|to)|hoping|might|maybe|about to|going to|for now|not yet|"
                   r"(?:has|have)(?:n['’]t| not) (?:decided|heard|chosen))\b", re.I)


def is_open(value) -> bool:
    """Whether a memory's wording says it is not settled yet ("considering returning her")."""
    return bool(_OPEN.search(str(value or "")))


def open_keys(memory: dict, meta: dict) -> set:
    """The memories still open: marked so by the keeper, or worded so."""
    return {k for k, v in (memory or {}).items() if (meta.get(k) or {}).get("status") == "open" or is_open(v)}


def _words(text) -> set:
    return {w for w in _WORD.findall(str(text or "").lower()) if len(w) > 2}


def _cosine(a, b) -> float:
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return sum(x * y for x, y in zip(a, b)) / norm if norm > 1e-12 else 0.0


def memory_hash(key, value) -> str:
    """Identifies a memory's content, so its embedding is redone only when the text changes."""
    return hashlib.sha256(f"{key}: {value}".encode("utf-8")).hexdigest()[:16]


def meaning_scores(state: dict, text: str, store, embedder, held: set | None = None):
    """Each memory's similarity to `text`. A memory is embedded once per content and model, and kept in
    the store. None when the embedder is on its hash fallback, whose vectors carry no meaning.
    `held` is every key still kept (default: those in `state`); vectors of the rest are dropped."""
    memory = ((state or {}).get("self") or {}).get("memory", {}) or {}
    if not memory or embedder is None or embedder.degraded:
        return None
    model = f"{embedder.backend}:{embedder.model}"
    kept = store.memory_vectors()
    texts = {k: f"{k}: {v}" for k, v in memory.items()}
    hashes = {k: memory_hash(k, v) for k, v in memory.items()}
    missing = [k for k in memory if kept.get(k, (None, None))[:2] != (hashes[k], model)]
    vectors = embedder.embed_batch([text] + [texts[k] for k in missing])
    if embedder.degraded:
        return None
    fresh = dict(zip(missing, vectors[1:]))
    if fresh or set(kept) - (set(memory) if held is None else held):
        store.save_memory_vectors([(k, hashes[k], model, v) for k, v in fresh.items()],
                                  keep=set(memory) if held is None else held)
    return {k: _cosine(vectors[0], fresh[k] if k in fresh else kept[k][2]) for k in memory}


def _exchange_text(said: str, answered: str) -> str:
    return f"They said: {said}\nYou answered: {answered}"


def exchange_scores(text: str, store, embedder) -> list | None:
    """This conversation's earlier exchanges by similarity to `text`, best first, as (score, exchange). Each is
    embedded once and kept in the store. None on the hash fallback."""
    exchanges = store.exchanges()
    if not exchanges or embedder is None or embedder.degraded:
        return None if embedder is None or embedder.degraded else []
    model = f"{embedder.backend}:{embedder.model}"
    # nomic-embed-text is trained with these task prefixes; it ranks better with them.
    doc, query = ("search_document: ", "search_query: ") if "nomic" in model else ("", "")
    missing = [e for e in exchanges if not e["vector"] or e["vector"][0] != model]
    vectors = embedder.embed_batch([query + text] + [doc + _exchange_text(e["said"], e["answered"]) for e in missing])
    if embedder.degraded:
        return None
    fresh = {e["turn_id"]: v for e, v in zip(missing, vectors[1:])}
    if fresh:
        store.save_exchange_vectors([(t, model, v) for t, v in fresh.items()])
    scored = [(_cosine(vectors[0], fresh.get(e["turn_id"]) or e["vector"][1]), e) for e in exchanges]
    return sorted(scored, key=lambda se: se[0], reverse=True)


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

    # Charted rooms, exits and things reach the prompt as SHARED REALITY, not as facts here.
    facts = [
        (f"{label(e['source'])} {e['relation']} {label(e['target'])}", {e["source"], e["target"]})
        for e in world.get("edges", []) or []
        if e.get("status", "active") == "active" and e.get("assertion") != "engine_charted"
    ]
    facts += [(f"{label(c['target'])}: {c['rule']} {c['value']}", {c["target"]}) for c in world.get("constraints", []) or []]
    facts += [
        (f"{n.get('label', node_id)} ({n.get('type', 'thing')})", {node_id})
        for node_id, n in nodes.items()
        if n.get("type") not in (None, "reference", "room", "item") and not any(node_id in ids for _, ids in facts)
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
