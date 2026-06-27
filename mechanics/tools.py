"""mechanics/tools.py"""

import math
import os
import random
import re
import time
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from constants import Prisma

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


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
    _MODES = {
        "PURIST": {"range": (0.0, 0.2), "desc": "Shortest path, structural fidelity"},
        "TOURIST": {"range": (0.2, 0.4), "desc": "Occasional scenic detours"},
        "EXPLORER": {
            "range": (0.4, 0.6),
            "desc": "Deliberate wrong turns, adjacent possible",
        },
        "FLANEUR": {"range": (0.6, 0.8), "desc": "Let the library browse you"},
        "CHAOS": {
            "range": (0.8, 1.0),
            "desc": "Maximum entropy, minimum predictability",
        },
    }

    def __init__(
        self, library_graph: LibraryGraph, config: dict[str, Any] | None = None
    ):
        self.library = library_graph
        self._node_index = {n.id: n for n in self.library.nodes}
        self.randomness_dial: float = float((config or {}).get("randomnessDial", 0.0))
        self.traversal_history: list[dict[str, Any]] = []

    def retrieve(
        self, query_coordinates: Coordinates, query_vector: list[float]
    ) -> dict[str, Any]:
        r_val, mode = self.randomness_dial, self._get_mode(self.randomness_dial)
        start_node = self._find_structural_match(query_coordinates)
        retrieval_path = self._generate_traversal_path(start_node, r_val)
        tagged_results = self._calculate_serendipity(
            self._traverse_and_collect(retrieval_path, query_vector, r_val),
            query_coordinates,
        )
        return {
            "mode": mode,
            "randomness_used": r_val,
            "path_length": len(retrieval_path),
            "results": tagged_results,
            "traversal_history": self.traversal_history[-5:],
            "note": self._generate_path_note(mode, tagged_results),
        }

    def _find_structural_match(self, coords: Coordinates) -> LibraryNode:
        for n in self.library.nodes:
            s_match = abs(n.coords.S - coords.S) < 0.15
            d_match = abs(n.coords.D - coords.D) < 0.20
            c_match = abs(n.coords.C - coords.C) < 0.25
            if s_match and d_match and c_match:
                return n
        return self.library.root

    def _generate_traversal_path(
        self, start_node: LibraryNode, r_val: float
    ) -> list[LibraryNode]:
        path = [start_node]
        visited = {start_node.id}
        for _ in range(math.floor(1 + r_val * 5)):
            available = [
                n for n in self._get_neighbors(path[-1]) if n.id not in visited
            ]
            if not available:
                break
            if random.random() < r_val:
                rb = (
                    self._get_random_branch(path[-1])
                    if (r_val > 0.7 and random.random() < 0.3)
                    else None
                )
                next_node = (
                    rb if (rb and rb.id not in visited) else random.choice(available)
                )
            else:
                next_node = self._most_structural_neighbor(available, start_node)
            if next_node:
                path.append(next_node)
                visited.add(next_node.id)
        self.traversal_history.append(
            {
                "timestamp": time.time(),
                "start_node": start_node.id,
                "path": [n.id for n in path],
                "R": self.randomness_dial,
            }
        )
        if len(self.traversal_history) > 20:
            self.traversal_history.pop(0)
        return path

    def _get_neighbors(self, node: LibraryNode) -> list[LibraryNode]:
        refs_set = set(node.refs)
        neighbors = []
        for n in self.library.nodes:
            if (
                (n.id == node.parent_id)
                or (n.parent_id == node.id)
                or (
                    node.parent_id and n.parent_id == node.parent_id and n.id != node.id
                )
                or (n.id in refs_set)
            ):
                neighbors.append(n)
        return neighbors

    def _most_structural_neighbor(
        self, neighbors: list[LibraryNode], target_node: LibraryNode
    ) -> LibraryNode:
        return max(
            neighbors,
            key=lambda current: self._structural_similarity(current, target_node),
        )

    def _structural_similarity(self, a: LibraryNode, b: LibraryNode) -> float:
        return 1.0 / (
            1.0
            + math.dist(
                (a.coords.S, a.coords.D, a.coords.C),
                (b.coords.S, b.coords.D, b.coords.C),
            )
        )

    def _get_random_branch(self, current_node: LibraryNode) -> Optional[LibraryNode]:
        lineage = self._get_lineage(current_node)
        c = [
            n
            for n in self.library.nodes
            if n.id not in lineage and n.id != current_node.id
        ]
        return random.choice(c) if c else None

    def _get_lineage(self, node: LibraryNode) -> set[str]:
        lineage = {node.id}
        current = node
        while current.parent_id and current.parent_id in self._node_index:
            if current.parent_id in lineage:
                break
            lineage.add(current.parent_id)
            current = self._node_index[current.parent_id]
        return lineage

    def _traverse_and_collect(
        self, path: list[LibraryNode], query_vector: list[float], r_val: float
    ) -> list[RetrievalResult]:
        path_len = len(path)
        query_mag = math.hypot(*query_vector) if query_vector else 0.0

        def _build_result(i: int, n: LibraryNode) -> RetrievalResult:
            rel = self._vector_similarity(n.vector, query_vector, query_mag)
            ser = r_val * (i / path_len) * 0.7
            final = (rel * (1.0 - (i / path_len) * 0.5)) + ser
            return RetrievalResult(
                node_id=n.id,
                title=n.title,
                content=n.content,
                coords=n.coords,
                path_position=i,
                relevance_score=rel,
                serendipity_bonus=ser,
                final_score=final,
                snippet=n.content[:150] + "...",
            )

        results = [_build_result(i, n) for i, n in enumerate(path)]
        return sorted(results, key=lambda x: x.final_score, reverse=True)

    def _vector_similarity(
        self, v1: list[float], v2: list[float], v2_mag: Optional[float] = None
    ) -> float:
        if not v1 or not v2:
            return 0.5
        dot = sum(a * b for a, b in zip(v1, v2))
        m2 = float(v2_mag) if v2_mag is not None else math.hypot(*v2)
        mag = math.hypot(*v1) * m2
        return ((dot / mag) + 1.0) / 2.0 if mag != 0 else 0.5

    def _calculate_serendipity(
        self, results: list[RetrievalResult], query_coords: Coordinates
    ) -> list[RetrievalResult]:
        for r in results:
            r.serendipity = r.relevance_score * math.dist(
                (r.coords.S, r.coords.D, r.coords.C),
                (query_coords.S, query_coords.D, query_coords.C),
            )
            r.is_surprising = r.serendipity > 0.5
        return results

    def _get_mode(self, r_val: float) -> dict[str, str]:
        return next(
            (
                {"name": str(name), "description": str(spec["desc"])}
                for name, spec in self._MODES.items()
                if float(spec["range"][0]) <= r_val <= float(spec["range"][1])
            ),
            {"name": "TOURIST", "description": "Default mode"},
        )

    def _generate_path_note(
        self, mode: dict[str, str], results: list[RetrievalResult]
    ) -> str:
        surprising_count = sum(1 for r in results if r.is_surprising)
        notes = {
            "PURIST": "Staying on the beaten path. Nothing wasted, nothing unexpected.",
            "TOURIST": "Took a small detour. Found a nice view.",
            "EXPLORER": "Went where the path was thin. Came back with something odd.",
            "FLANEUR": "The library started talking. I just listened.",
            "CHAOS": "At this point, the books are reading you.",
        }
        base_note = notes.get(mode["name"], "Wandering...")
        if surprising_count > 0:
            gem_str = "gem" if surprising_count == 1 else "gems"
            return f"{base_note} Found {surprising_count} unexpected {gem_str}."
        return f"{base_note} Nothing surprising—but sometimes that's the point."

    def set_randomness(self, value: float) -> dict[str, Any]:
        self.randomness_dial = max(0.0, min(1.0, float(value)))
        return {
            "new_value": self.randomness_dial,
            "mode": self._get_mode(self.randomness_dial)["name"],
            "message": f"Random retrieval dial set to {self.randomness_dial:.2f}",
        }

    def get_state(self) -> dict[str, Any]:
        return {
            "randomness_dial": self.randomness_dial,
            "mode": self._get_mode(self.randomness_dial),
            "traversal_history": self.traversal_history[-3:],
        }


class TheSubstrate:
    def __init__(self, events_ref):
        self.events = events_ref
        self.pending_writes: List[Dict[str, Any]] = []
        self._cords_instance = None
        from core import LoreManifest

        self.config = LoreManifest.get_instance().get("SUBSTRATE_CONFIG") or {
            "ATP_COST_PER_CHAR": 0.02,
            "MAX_ATP_PER_FILE": 100.0,
            "SUBSTRATE_WRITE_RETRIES": 3,
        }

    def queue_write(self, path: str, content: str):
        self.pending_writes.append({"path": path, "content": content, "retries": 0})

    def execute_writes(self, stamina_pool: float) -> Tuple[List[str], float]:
        logs, cost = [], 0.0
        if not self.pending_writes:
            return logs, cost
        os.makedirs("output", exist_ok=True)
        base_dir = os.path.realpath("output")
        retained_writes = []
        for w in self.pending_writes:
            s_path = os.path.realpath(os.path.join(base_dir, w["path"].lstrip("/")))
            s_name = os.path.basename(s_path)
            if os.path.commonpath([base_dir, s_path]) != base_dir:
                logs.append(
                    f"{Prisma.VIOLET}FATAL ERROR: Path traversal breach detected ({w['path']}). Purged.{Prisma.RST}"
                )
                continue
            w_cost = len(w["content"]) * self.config.get("ATP_COST_PER_CHAR", 0.02)
            if w_cost > self.config.get("MAX_ATP_PER_FILE", 100.0):
                logs.append(
                    f"{Prisma.VIOLET}FATAL ERROR: {s_name} exceeds absolute biological carrying capacity (Cost: {w_cost:.1f} ATP). Purged from system.{Prisma.RST}"
                )
                continue
            if stamina_pool - cost < w_cost:
                retries = w.get("retries", 0) + 1
                if retries > self.config.get("SUBSTRATE_WRITE_RETRIES", 3):
                    logs.append(
                        f"{Prisma.VIOLET}FATAL ERROR: {s_name} starved for ATP 3 times. Dropping file.{Prisma.RST}"
                    )
                else:
                    logs.append(
                        f"{Prisma.OCHRE}CRITICAL FAULT: Insufficient stamina to forge {s_name}. Retaining in queue ({retries}/3).{Prisma.RST}"
                    )
                    w["retries"] = retries
                    retained_writes.append(w)
                continue
            try:
                os.makedirs(os.path.dirname(s_path), exist_ok=True)
                with open(s_path, "w", encoding="utf-8") as f:
                    f.write(w["content"])
                cost += w_cost
                kb_size = len(w["content"]) / 1024.0
                logs.append(
                    f"{Prisma.GRN}Physically forged {s_path} ({kb_size:.1f} KB).{Prisma.RST}"
                )
                if self.events:
                    self.events.publish(
                        "SUBSTRATE_FORGED", {"cost": w_cost, "file": s_name}
                    )
            except Exception as e:
                retries = w.get("retries", 0) + 1
                if retries > self.config.get("SUBSTRATE_WRITE_RETRIES", 3):
                    logs.append(
                        f"{Prisma.VIOLET}FATAL ERROR: Write failed 3 times for {s_name} - {e}. Purging corrupted matter.{Prisma.RST}"
                    )
                else:
                    logs.append(
                        f"{Prisma.RED}CRITICAL FAULT: Write failed - {e}. Retrying ({retries}/3).{Prisma.RST}"
                    )
                    w["retries"] = retries
                    retained_writes.append(w)
        self.pending_writes = retained_writes
        return logs, cost


class TheTclWeaver:
    _instance = None
    _HTML_TAG_RE = re.compile(r"<[^>]+>")
    _PUNC_RE = re.compile(r"[^\w\s\.,!?]*$")
    _WORD_SPLIT_RE = re.compile(r"\W+")
    _CLEAN_RE = re.compile(r"[^a-zA-Z0-9]")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TheTclWeaver()
        return cls._instance

    def deform_reality(self, text: str, chi: float, voltage: float) -> str:
        def _warp(w):
            L = len(w)
            if chi > 0.85 and L > 4 and random.random() < (chi / 3.0):
                return f"{w[0]}{w[1:-1][::-1]}{w[-1]}"
            if chi > 0.6 and L > 4 and random.random() < (chi / 2.0):
                return f"{w[: L // 2]}·{w[L // 2 :]}"
            if voltage > 80.0 and random.random() < 0.1:
                return w.upper()
            return w

        return " ".join(_warp(w) for w in text.split(" "))

    def haunt_string(self, text: str) -> str:
        words = [w for w in self._WORD_SPLIT_RE.split(text) if w]
        if not words:
            return text
        clean = self._CLEAN_RE.sub("", words[-1]).lower()
        return f"{text}... {clean}..." if clean else f"{text}..."

    def quantum_comb(self, text: str, chi: float) -> str:
        if chi < 0.5 or not text:
            return text
        return " ".join(
            w
            for w in text.split(" ")
            if w
            and not (
                len(w) > 5 and random.random() < chi and self._QUANTUM_REGEX.search(w)
            )
        )

    def consume_by_void(self, text: str, psi: float) -> str:
        def _void(w):
            if psi > 0.5 and len(w) > 3 and random.random() < (psi / 2.5):
                return "████"
            return w

        return " ".join(_void(w) for w in text.split(" "))
