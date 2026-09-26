"""The verbs — the only code that touches canonical state, one function per verb.

Five imagination verbs (create / relate / constrain / occur / name) that grow the
world graph, living behind the gate instead of after a permissive prose extractor.
Plus `remember`, the sole writer of the SELF graph.

Each returns a small result dict describing what changed (or a noop). A repeat
is a noop, not an error — the gate still receipts it.
"""
from __future__ import annotations

from .graph import edge_id, normalize_world, slug


# ── imagination: writes world/* ────────────────────────────────────────────

def _create(state, what, a):
    w = state["world"] = normalize_world(state["world"])
    node_id = f"entity:{slug(a['name'])}"
    if node_id in w["nodes"]:
        return {"noop": f"node {a['name']!r} already exists"}
    w["nodes"][node_id] = {"id": node_id, "label": a["name"], "type": a["type"], "visibility": "standard", "properties": {}, "sources": []}
    return {"created": node_id, "label": a["name"], "type": a["type"]}


def _relate(state, what, a):
    w = state["world"] = normalize_world(state["world"])
    source, target = f"entity:{slug(a['subject'])}", f"entity:{slug(a['object'])}"
    for node_id, label in ((source, a["subject"]), (target, a["object"])):
        w["nodes"].setdefault(node_id, {"id": node_id, "label": label, "type": "reference", "visibility": "standard", "properties": {}, "sources": []})
    e = {"id": edge_id(source, a["relation"], target), "source": source, "relation": a["relation"], "target": target,
         "assertion": "model_proposed", "confidence": None, "visibility": "standard", "sources": [], "status": "active"}
    if any(item["id"] == e["id"] for item in w["edges"]):
        return {"noop": "edge already exists"}
    w["edges"].append(e)
    return {"related": e}


def _constrain(state, what, a):
    w = state["world"] = normalize_world(state["world"])
    target = f"entity:{slug(a['target'])}"
    w["nodes"].setdefault(target, {"id": target, "label": a["target"], "type": "reference", "visibility": "standard", "properties": {}, "sources": []})
    c = {"id": edge_id(target, a["rule"], a["value"]), "target": target, "rule": a["rule"], "value": a["value"], "visibility": "standard", "sources": []}
    if any(item["id"] == c["id"] for item in w["constraints"]):
        return {"noop": "constraint already exists"}
    w["constraints"].append(c)
    return {"constrained": c}


def _occur(state, what, a):
    # Events are nodes, never mutations. Nothing is retracted.
    w = state["world"] = normalize_world(state["world"])
    event, participant = f"entity:{slug(a['event'])}", f"entity:{slug(a['participant'])}"
    w["nodes"].setdefault(event, {"id": event, "label": a["event"], "type": "event", "visibility": "standard", "properties": {}, "sources": []})
    w["nodes"].setdefault(participant, {"id": participant, "label": a["participant"], "type": "reference", "visibility": "standard", "properties": {}, "sources": []})
    e = {"id": edge_id(event, "involves", participant), "source": event, "relation": "involves", "target": participant,
         "assertion": "model_proposed", "confidence": None, "visibility": "standard", "sources": [], "status": "active"}
    if any(item["id"] == e["id"] for item in w["edges"]): return {"noop": "event link already exists"}
    w["edges"].append(e); return {"occurred": e}


def _name(state, what, a):
    return _relate(state, what, {"subject": a["target"], "relation": "known as", "object": a["alias"]})


# ── selfhood: writes self/* (the ONLY writer of the self graph) ────────────

def _remember(state, what, a):
    state["self"].setdefault("memory", {})[a["key"]] = a["value"]
    return {"remembered": a["key"], "value": a["value"]}


TOOLS = {
    "create": _create, "relate": _relate, "constrain": _constrain,
    "occur": _occur, "name": _name, "remember": _remember,
}


# ── invariants: pure checks over a candidate (trial) state ─────────────────
# Built from the declaration so the numbers live in the boundary file, not here.

def build_invariants(spec: dict) -> dict:
    limits = spec.get("limits", {})
    world_cap = limits.get("world_max_elements", 100_000)
    self_cap = limits.get("self_max_memories", 10_000)

    def world_within_budget(state):
        w = state["world"]
        n = len(w["nodes"]) + len(w["edges"]) + len(w["constraints"])
        if n > world_cap:
            return f"world would hold {n} elements, over the declared {world_cap}"
        return None

    def self_within_budget(state):
        n = len(state["self"].get("memory", {}))
        if n > self_cap:
            return f"self would hold {n} memories, over the declared {self_cap}"
        return None

    return {"world_within_budget": world_within_budget,
            "self_within_budget": self_within_budget}
