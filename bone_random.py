"""
VSL-R RANDOM RETRIEVAL MODULE
Extends retrieval navigation with stochastic path traversal.
Purpose: Enable serendipitous discovery alongside structural completeness.
Couples deeply with JESTER (Chaos) and CASSANDRA (Mystic) archetypes.
"""

import math
import random
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Coordinates:
    S: float
    D: float
    C: float


@dataclass
class LibraryNode:
    id: str
    content: str
    title: str
    coords: Coordinates
    vector: list[float]
    parent_id: Optional[str] = None
    refs: list[str] = field(default_factory=list)

@dataclass
class RetrievalResult:
    node_id: str
    title: str
    content: str
    coords: Coordinates
    path_position: int
    relevance_score: float
    serendipity_bonus: float
    final_score: float
    snippet: str
    serendipity: float = 0.0
    is_surprising: bool = False

class LibraryGraph:
    def __init__(self, nodes: list[LibraryNode], root: LibraryNode):
        self.nodes = nodes
        self.root = root

class RandomRetrievalNavigator:
    def __init__(self, library_graph: LibraryGraph, config: dict[str, Any] | None = None):
        if config is None:
            config = {}
        self.library = library_graph
        self.randomness_dial: float = float(config.get("randomnessDial", 0.0))
        self.traversal_history: list[dict[str, Any]] = []
        self.serendipity_cache: dict[str, Any] = {}
        self.modes = {
            "PURIST":   {"range": (0.0, 0.2), "desc": "Shortest path, structural fidelity"},
            "TOURIST":  {"range": (0.2, 0.4), "desc": "Occasional scenic detours"},
            "EXPLORER": {"range": (0.4, 0.6), "desc": "Deliberate wrong turns, adjacent possible"},
            "FLANEUR":  {"range": (0.6, 0.8), "desc": "Let the library browse you"},
            "CHAOS":    {"range": (0.8, 1.0), "desc": "Maximum entropy, minimum predictability"}
        }

    def retrieve(self, query_coordinates: Coordinates, query_vector: list[float]) -> dict[str, Any]:
        r_val = self.randomness_dial
        mode = self._get_mode(r_val)
        structural_target = self._find_structural_match(query_coordinates)
        retrieval_path = self._generate_traversal_path(structural_target, r_val)
        results = self._traverse_and_collect(retrieval_path, query_vector, r_val)
        tagged_results = self._calculate_serendipity(results, query_coordinates)

        return {"mode": mode, "randomness_used": r_val, "path_length": len(retrieval_path), "results": tagged_results,
                "traversal_history": self.traversal_history[-5:],
                "note": self._generate_path_note(mode, tagged_results)}

    def _find_structural_match(self, coords: Coordinates) -> LibraryNode:
        candidates = [
            node for node in self.library.nodes
            if abs(node.coords.S - coords.S) < 0.15
            and abs(node.coords.D - coords.D) < 0.2
            and abs(node.coords.C - coords.C) < 0.25
        ]
        return candidates[0] if candidates else self.library.root

    def _generate_traversal_path(self, start_node: LibraryNode, r_val: float) -> list[LibraryNode]:
        import time
        path = [start_node]
        visited = {start_node.id}
        steps = math.floor(1 + r_val * 5)
        for _ in range(steps):
            current_node = path[-1]
            neighbors = self._get_neighbors(current_node)
            available = [n for n in neighbors if n.id not in visited]
            if not available:
                break
            if random.random() < r_val:
                if r_val > 0.7 and random.random() < 0.3:
                    random_branch = self._get_random_branch(current_node)
                    next_node = random_branch if (random_branch and random_branch.id not in visited) else random.choice(
                        available)
                else:
                    next_node = random.choice(available)
            else:
                next_node = self._most_structural_neighbor(available, start_node)
            if next_node:
                path.append(next_node)
                visited.add(next_node.id)
        self.traversal_history.append(
            {"timestamp": time.time(), "start_node": start_node.id, "path": [n.id for n in path],
             "R": self.randomness_dial}
        )
        return path

    def _get_neighbors(self, node: LibraryNode) -> list[LibraryNode]:
        neighbors = []
        if node.parent_id:
            parent = next((n for n in self.library.nodes if n.id == node.parent_id), None)
            if parent:
                neighbors.append(parent)
        children = [n for n in self.library.nodes if n.parent_id == node.id]
        neighbors.extend(children)
        if node.parent_id:
            siblings = [n for n in self.library.nodes if n.parent_id == node.parent_id and n.id != node.id]
            neighbors.extend(siblings)
        if node.refs:
            refs = [n for n in self.library.nodes if n.id in node.refs]
            neighbors.extend(refs)
        return neighbors

    def _most_structural_neighbor(self, neighbors: list[LibraryNode], target_node: LibraryNode) -> LibraryNode:
        return max(neighbors, key=lambda current: self._structural_similarity(current, target_node))

    def _structural_similarity(self, a: LibraryNode, b: LibraryNode) -> float:
        dist = math.sqrt(
            (a.coords.S - b.coords.S) ** 2 +
            (a.coords.D - b.coords.D) ** 2 +
            (a.coords.C - b.coords.C) ** 2
        )
        return 1.0 / (1.0 + dist)

    def _get_random_branch(self, current_node: LibraryNode) -> Optional[LibraryNode]:
        lineage = self._get_lineage(current_node)
        candidates = [n for n in self.library.nodes if n.id not in lineage and n.id != current_node.id]

        if not candidates:
            return None
        return random.choice(candidates)

    def _get_lineage(self, node: LibraryNode) -> set[str]:
        lineage = {node.id}
        current = node
        while current.parent_id:
            lineage.add(current.parent_id)
            current = next((n for n in self.library.nodes if n.id == current.parent_id), None)
            if not current:
                break
        return lineage

    def _traverse_and_collect(self, path: list[LibraryNode], query_vector: list[float], r_val: float) -> list[RetrievalResult]:
        collected = []
        path_len = len(path)
        for i, node in enumerate(path):
            relevance = self._vector_similarity(node.vector, query_vector)
            position_weight = 1.0 - (i / path_len) * 0.5
            serendipity_bonus = r_val * (i / path_len) * 0.7
            score = (relevance * position_weight) + serendipity_bonus
            collected.append(RetrievalResult(node_id=node.id, title=node.title, content=node.content,
                                             coords=node.coords, path_position=i, relevance_score=relevance,
                                             serendipity_bonus=serendipity_bonus, final_score=score,
                                             snippet=node.content[:150] + "..."))

        return sorted(collected, key=lambda x: x.final_score, reverse=True)

    def _vector_similarity(self, v1: list[float], v2: list[float]) -> float:
        if not v1 or not v2:
            return 0.5
        dot = sum(val1 * val2 for val1, val2 in zip(v1, v2))
        mag1 = math.sqrt(sum(val ** 2 for val in v1))
        mag2 = math.sqrt(sum(val ** 2 for val in v2))
        if mag1 * mag2 == 0:
            return 0.5
        return ((dot / (mag1 * mag2)) + 1.0) / 2.0

    def _calculate_serendipity(self, results: list[RetrievalResult], query_coords: Coordinates) -> list[RetrievalResult]:
        for r in results:
            expected_delta = math.sqrt(
                (r.coords.S - query_coords.S) ** 2 +
                (r.coords.D - query_coords.D) ** 2 +
                (r.coords.C - query_coords.C) ** 2
            )
            r.serendipity = r.relevance_score * expected_delta
            r.is_surprising = r.serendipity > 0.5

        return results

    def _get_mode(self, r_val: float) -> dict[str, str]:
        for name, spec in self.modes.items():
            if spec["range"][0] <= r_val <= spec["range"][1]:
                return {"name": name, "description": spec["desc"]}
        return {"name": "TOURIST", "description": "Default mode"}

    def _generate_path_note(self, mode: dict[str, str], results: list[RetrievalResult]) -> str:
        surprising_count = sum(1 for r in results if r.is_surprising)

        notes = {"PURIST": "Staying on the beaten path. Nothing wasted, nothing unexpected.",
                 "TOURIST": "Took a small detour. Found a nice view.",
                 "EXPLORER": "Went where the path was thin. Came back with something odd.",
                 "FLANEUR": "The library started talking. I just listened.",
                 "CHAOS": "At this point, the books are reading you."}

        base_note = notes.get(mode["name"], "Wandering...")
        if surprising_count > 0:
            noun = "gem" if surprising_count == 1 else "gems"
            surprise_note = f" Found {surprising_count} unexpected {noun}."
        else:
            surprise_note = " Nothing surprising—but sometimes that's the point."
        return base_note + surprise_note

    def set_randomness(self, value: float) -> dict[str, Any]:
        self.randomness_dial = max(0.0, min(1.0, float(value)))
        mode = self._get_mode(self.randomness_dial)
        return {"new_value": self.randomness_dial, "mode": mode["name"],
                "message": f"Random retrieval dial set to {self.randomness_dial:.2f}"}

    def get_state(self) -> dict[str, Any]:
        return {"randomness_dial": self.randomness_dial, "mode": self._get_mode(self.randomness_dial),
                "traversal_history": self.traversal_history[-3:], "serendipity_cache_size": len(self.serendipity_cache)}
