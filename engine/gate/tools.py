"""The verbs — the only code that touches canonical state, one function per verb.

Five imagination verbs (create / relate / constrain / occur / name) that grow the
world graph, living behind the gate instead of after a permissive prose extractor.
Plus `remember`, `reflect` and `forget`, the only writers of the SELF graph.

Each returns a small result dict describing what changed (or a noop). A repeat
is a noop, not an error — the gate still receipts it.
"""
from __future__ import annotations

import re

from .graph import edge_id, normalize_world, slug
from .secrets import screen


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


def _node(w, label, type_):
    node_id = f"entity:{slug(label)}"
    node = w["nodes"].setdefault(node_id, {"id": node_id, "label": label, "type": type_, "visibility": "standard", "properties": {}, "sources": []})
    if node["type"] == "reference":
        node["type"] = type_
    return node_id


def _chart(state, what, a):
    """A room as the narrator last described it: its description, exits (`Direction to Place`) and items,
    `|`-separated. What the room no longer lists is retired, and an item seen here leaves wherever it was."""
    w = state["world"] = normalize_world(state["world"])
    room = _node(w, a["room"], "room")
    props = w["nodes"][room].setdefault("properties", {})
    changed = []
    if a["description"] and props.get("description") != a["description"]:
        props["description"] = a["description"]
        changed.append("description")
    wanted = []
    for entry in (e.strip() for e in a["exits"].split("|")):
        direction, sep, place = entry.rpartition(" to ")
        direction = re.sub(r"\s*\([^)]*\)", "", direction).strip().lower()  # "North (via Iron Door)"
        if sep and direction and place.strip():
            wanted.append((room, f"exit {direction}", _node(w, place.strip(), "room")))
    items = [i.strip() for i in a["items"].split("|") if i.strip()]
    wanted += [(_node(w, item, "item"), "is in", room) for item in items]
    wanted_ids = {edge_id(s, r, t) for s, r, t in wanted}
    item_ids = {f"entity:{slug(i)}" for i in items}
    for e in w["edges"]:
        if e.get("status", "active") != "active" or e["id"] in wanted_ids:
            continue
        stale_exit = e["source"] == room and e["relation"].startswith("exit ")
        stale_item = e["relation"] == "is in" and (e["target"] == room or e["source"] in item_ids)
        if stale_exit or stale_item:
            e["status"] = "retired"
            changed.append(f"retired {e['relation']}")
    by_id = {e["id"]: e for e in w["edges"]}
    for s_, r, t in wanted:
        eid = edge_id(s_, r, t)
        if eid in by_id:
            if by_id[eid].get("status") != "active":
                by_id[eid]["status"] = "active"
                changed.append(r)
            continue
        w["edges"].append({"id": eid, "source": s_, "relation": r, "target": t, "assertion": "engine_charted",
                           "confidence": None, "visibility": "standard", "sources": [], "status": "active"})
        changed.append(r)
    if not changed:
        return {"noop": f"room {a['room']!r} already charted as described"}
    return {"charted": room, "changes": changed}


# ── selfhood: writes self/* (remember and forget are the ONLY writers of the self graph) ──

def _remember(state, what, a):
    state["self"].setdefault("memory", {})[a["key"]] = a["value"]
    return {"remembered": a["key"], "value": a["value"]}


def _reflect(state, what, a):
    """What memories mean together (REM plan R2), written beside them; `from` names them, `|`-separated."""
    memory = state["self"].setdefault("memory", {})
    held = [k for k in dict.fromkeys(k.strip() for k in a["from"].split("|")) if k in memory]
    if not held:
        return {"noop": "none of its memories are held"}
    memory[a["key"]] = a["value"]
    return {"reflected": a["key"], "from": held}


def _forget(state, what, a):
    memory = state["self"].setdefault("memory", {})
    gone = [k for k in dict.fromkeys(k.strip() for k in a["keys"].split("|")) if k in memory]
    for key in gone:
        del memory[key]
    return {"forgot": gone} if gone else {"noop": "none of those memories are held"}


TOOLS = {
    "create": _create, "relate": _relate, "constrain": _constrain,
    "occur": _occur, "name": _name, "remember": _remember, "forget": _forget, "chart": _chart, "reflect": _reflect,
}


# ── grammar: what the model is told it may nominate ────────────────────────

def grammar_text(spec: dict) -> str:
    """The permitted verbs with their exact arg names and an example, from the declaration."""
    lines = []
    for verb, d in spec.get("verbs", {}).items():
        # Engine-built verbs (chart) are written by the engine, not offered to the model.
        if not d.get("permitted") or d.get("engine_built"):
            continue
        args = "; ".join(f"{k}:<{r.get('type', 'str')}>" for k, r in d.get("args", {}).items())
        lines.append(f"  verb={verb} (writes {d['writes']}) args={args}")
        if d.get("example"):
            lines.append(f"    example: {d['example']}")
    return "\n".join(lines)


# ── invariants: pure checks over a candidate (trial) state ─────────────────
# Built from the declaration so the numbers live in the boundary file, not here.

def build_invariants(spec: dict, in_story=lambda: False) -> dict:
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
            "self_within_budget": self_within_budget,
            "no_secrets": lambda verb, what, args: screen(verb, what, args, in_story())}
