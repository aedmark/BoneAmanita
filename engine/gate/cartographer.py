"""The cartographer (memory phase 4): each ADVENTURE room the narrator describes is charted into the world
graph through the gate, in its own cycle, and the next prompt reads the room back from the graph.

The narrator never nominated rooms itself, so the engine builds the chart from the parsed room block,
as the keeper does for memories. The kernel's one nomination per cycle is untouched."""
from __future__ import annotations

import copy
import re

from .graph import slug
from .tools import _chart


def _clean(value, limit: int) -> str:
    # ";" separates args and "|" separates entries, so neither may appear inside one.
    return re.sub(r"\s+", " ", str(value or "").replace(";", ",").replace("|", "/")).strip()[:limit]


def _joined(entries, limit: int) -> str:
    out = ""
    for entry in entries:
        piece = entry if not out else f" | {entry}"
        if len(out) + len(piece) > limit:
            break
        out += piece
    return out


def chart_args(room: dict | None) -> dict | None:
    """The chart's args for a parsed room, or None when it has no name to chart under."""
    from mechanics.projector import is_system_label

    name = _clean((room or {}).get("name"), 120)
    if not name or name == "Uncharted Zone" or is_system_label(name):
        return None
    exits = [_clean(e, 150) for e in room.get("exits", []) if " to " in str(e)]
    items = [_clean(i, 100) for i in room.get("pois", []) if _clean(i, 100)]
    return {"room": name, "description": _clean(room.get("description"), 600),
            "exits": _joined(exits, 600), "items": _joined(items, 600)}


def chart_line(args: dict) -> str:
    return (f"NOMINATE what=world/room/{slug(args['room'])} verb=chart args=room:{args['room']}; "
            f"description:{args['description']}; exits:{args['exits']}; items:{args['items']}")


def needs_chart(state: dict, args: dict) -> bool:
    """Whether charting would change anything; the same tool, run on a copy."""
    return "noop" not in _chart(copy.deepcopy(state), None, args)


def room_view(state: dict, name: str) -> dict | None:
    """A charted room as the graph holds it: description, active exits and the things in it."""
    world = (state or {}).get("world") or {}
    nodes = world.get("nodes", {}) or {}
    room_id = f"entity:{slug(str(name or ''))}"
    node = nodes.get(room_id)
    if not name or not node or node.get("type") != "room":
        return None
    active = [e for e in world.get("edges", []) or [] if e.get("status", "active") == "active"]
    label = lambda node_id: (nodes.get(node_id) or {}).get("label", node_id)
    return {
        "name": node.get("label", name),
        "description": (node.get("properties") or {}).get("description", ""),
        "exits": [f"{e['relation'][5:].title()} to {label(e['target'])}" for e in active
                  if e["source"] == room_id and e["relation"].startswith("exit ")],
        "items": [label(e["source"]) for e in active if e["relation"] == "is in" and e["target"] == room_id],
    }
