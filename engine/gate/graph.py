"""Rich world-graph schema and legacy adapters."""
from __future__ import annotations

import hashlib
import re


def slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return clean or hashlib.sha256(value.encode()).hexdigest()[:12]


def edge_id(source: str, relation: str, target: str) -> str:
    raw = f"{source}\0{relation}\0{target}".encode()
    return "edge:" + hashlib.sha256(raw).hexdigest()[:16]


def empty_world() -> dict:
    return {"schema_version": 2, "sources": {}, "nodes": {}, "edges": [], "constraints": []}


def normalize_world(world: dict) -> dict:
    """Return schema v2 while accepting the original name->type/list triples."""
    if world.get("schema_version") == 2:
        world.setdefault("nodes", {})
        world.setdefault("sources", {})
        world.setdefault("edges", [])
        world.setdefault("constraints", [])
        return world
    out = empty_world()
    name_to_id: dict[str, str] = {}
    for name, value in world.get("nodes", {}).items():
        if name.startswith("_"):
            continue
        node_id = f"entity:{slug(name)}"
        name_to_id[name] = node_id
        out["nodes"][node_id] = {"id": node_id, "label": name, "type": value if isinstance(value, str) else value.get("type", "entity"),
                                  "visibility": "standard", "properties": {}, "sources": []}
    def ensure(name: str) -> str:
        node_id = name_to_id.get(name, f"entity:{slug(name)}")
        if node_id not in out["nodes"]:
            out["nodes"][node_id] = {"id": node_id, "label": name, "type": "reference", "visibility": "standard", "properties": {}, "sources": []}
        return node_id
    for triple in world.get("edges", []):
        if isinstance(triple, dict):
            out["edges"].append(triple)
            continue
        source, relation, target = triple
        source_id, target_id = ensure(source), ensure(target)
        out["edges"].append({"id": edge_id(source_id, relation, target_id), "source": source_id, "relation": relation,
                             "target": target_id, "assertion": "legacy", "confidence": None,
                             "visibility": "standard", "sources": [], "status": "active"})
    for triple in world.get("constraints", []):
        if isinstance(triple, dict):
            out["constraints"].append(triple)
            continue
        target, rule, value = triple
        out["constraints"].append({"id": edge_id(ensure(target), rule, value), "target": ensure(target), "rule": rule,
                                   "value": value, "visibility": "standard", "sources": []})
    return out


def visible_world(world: dict, include_protected: bool = False) -> dict:
    world = normalize_world(world)
    allowed = {"standard", "protected"} if include_protected else {"standard"}
    nodes = {key: value for key, value in world["nodes"].items() if value.get("visibility", "standard") in allowed}
    edges = [edge for edge in world["edges"] if edge.get("visibility", "standard") in allowed and edge["source"] in nodes and edge["target"] in nodes]
    constraints = [item for item in world["constraints"] if item.get("visibility", "standard") in allowed and item["target"] in nodes]
    used_sources = {source for node in nodes.values() for source in node.get("sources", [])}
    used_sources.update(source for edge in edges for source in edge.get("sources", []))
    return {"schema_version": 2, "sources": {key: value for key, value in world.get("sources", {}).items() if key in used_sources},
            "nodes": nodes, "edges": edges, "constraints": constraints}
