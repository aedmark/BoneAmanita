"""brain/ann.py"""

import hashlib
import heapq
import math
import random
import time
from itertools import islice
from typing import Any, Dict, List, Optional, Tuple

import faiss
import numpy as np

from core import EventBus


class HippocampalCache:
    def __init__(self, max_capacity: int = 500):
        self.base_capacity = max_capacity
        self.current_capacity = max_capacity
        self.nodes: Dict[str, Any] = {}

    def apply_stress_blindness(self, cortisol: float):
        """Actively dials down max_capacity based on cortisol to simulate biological stress blindness."""
        if cortisol > 0.8:
            self.current_capacity = max(1, int(self.base_capacity * (1.0 - cortisol)))
        else:
            self.current_capacity = self.base_capacity
        while len(self.nodes) > self.current_capacity:
            del self.nodes[next(iter(self.nodes))]

    def encode(self, node_id: str, vector: List[float], metadata: Dict[str, Any]):
        self.nodes.pop(node_id, None)
        short_hash = hashlib.sha256(
            np.array(vector, dtype=np.float32).tobytes()
        ).hexdigest()[:8]
        self.nodes[node_id] = {
            "phantom": {
                "vector_hash": short_hash,
                "wing_id": metadata.get("wing_id", "GLOBAL"),
                "room_id": metadata.get("room_id", "GENERAL"),
            },
            "vector": vector,
            "meta": metadata,
            "timestamp": time.time(),
        }
        if len(self.nodes) > self.current_capacity:
            del self.nodes[next(iter(self.nodes))]

    def retrieve_exact(self, node_id: str) -> Optional[Dict]:
        if val := self.nodes.pop(node_id, None):
            self.nodes[node_id] = val
            return val
        return None

    def extract_for_consolidation(
        self, limit: Optional[int] = None
    ) -> List[Tuple[str, Dict]]:
        target_keys = list(islice(self.nodes.keys(), limit))
        return [(k, self.nodes.pop(k)) for k in target_keys]

    def get_graph(self) -> Dict[str, set]:
        keys: List[str] = list(self.nodes.keys())
        adj: Dict[str, set] = {k: set() for k in keys}
        if len(keys) < 2:
            return adj
        vectors = np.array([self.nodes[k]["vector"] for k in keys], dtype=np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = vectors / norms
        sim_matrix = np.dot(normalized, normalized.T)
        i_idx, j_idx = np.where(sim_matrix > 0.75)
        for i, j in zip(i_idx, j_idx):
            if i != j:
                idx_i, idx_j = int(i), int(j)
                adj[keys[idx_i]].add(keys[idx_j])
        return adj


class CerebralIndex:
    def __init__(self, dimension: int = 8):
        self.dimension = dimension
        self.is_trained = False
        self.total_nodes = 0
        self._index = faiss.IndexHNSWFlat(self.dimension, 32)
        self._payloads: List[Dict] = []
        self._phantom_lookup: Dict[str, str] = {}

    def resolve_phantom(self, vector_hash: str) -> str:
        return self._phantom_lookup.get(vector_hash, "")

    def add_memories(self, vectors: List[List[float]], metadata_payloads: List[Dict]):
        if not vectors or len(vectors) != len(metadata_payloads):
            print(
                f"Alignment failure. Vector count ({len(vectors)}) != Payload count ({len(metadata_payloads)}). Aborting ingestion."
            )
            return
        np_vectors = np.array(vectors, dtype=np.float32)
        self._index.add(np_vectors)
        for p in metadata_payloads:
            v_hash = p.get("vector_hash")
            if isinstance(v_hash, str) and v_hash:
                self._phantom_lookup[v_hash] = str(p.get("raw_verbatim_text", ""))
        self._payloads.extend(metadata_payloads)
        self.total_nodes = self.total_nodes + len(vectors)
        self.is_trained = True

    def lateral_ofc_retrieval(
        self, physics_state: Dict[str, Any], k: int = 2
    ) -> List[Dict]:
        if not self._payloads:
            return []
        if not isinstance(physics_state, dict):
            physics_state = {}
        base_omega = float(physics_state.get("omega", 0.5))
        base_omega_r = float(physics_state.get("omega_r", 0.5))

        def _score(payload):
            omega = float(payload.get("omega", base_omega))
            omega_r = float(payload.get("omega_r", base_omega_r))
            f_cost = float(payload.get("narrative_drag", 1.0))
            return (omega**2) + (2 * omega_r) + f_cost

        sample_size = min(len(self._payloads), 100)
        candidates = random.sample(self._payloads, sample_size)
        return heapq.nlargest(k, candidates, key=_score)

    def query_neighborhood(
        self,
        query_vector: List[float],
        k: int = 5,
        resonance_threshold: float = 0.5,
        physics_state: Optional[Dict[str, Any]] = None,
    ) -> List[Dict]:
        if (
            not self.is_trained
            or self.total_nodes == 0
            or len(query_vector) != self.dimension
        ):
            return []
        target_wing, is_lateral = None, False
        cortisol = 0.0
        if isinstance(physics_state, dict):
            cortisol = float(physics_state.get("cortisol", 0.0))
            if (
                float(physics_state.get("voltage", 0.0)) > 80.0
                and float(physics_state.get("chi", 0.0)) > 0.7
            ):
                return self.lateral_ofc_retrieval(physics_state, k=k)
            target_wing = physics_state.get("wing_id", "GLOBAL")
            is_lateral = bool(physics_state.get("lateral_search", False))
        if cortisol > 0.8:
            k = max(1, min(k, 2))
        np_query = np.array([query_vector], dtype=np.float32)
        distances, indices = self._index.search(np_query, min(k, self.total_nodes))
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            payload = self._payloads[idx]
            if not isinstance(payload, dict):
                continue
            if (
                target_wing
                and not is_lateral
                and payload.get("wing_id", "GLOBAL") != target_wing
            ):
                continue
            if cortisol > 0.8:
                dims = payload.get("dimensions", [])
                if isinstance(dims, list) and any(
                    d in dims for d in ("constructive", "play", "social")
                ):
                    continue
            resonance = 1.0 / (1.0 + float(dist))
            if resonance >= resonance_threshold:
                results.append({**payload, "resonance": resonance})
        return results

    def get_local_mass_radius(
        self, query_text: str = ""
    ) -> Optional[Dict[str, List[float]]]:
        if not self.is_trained or self.total_nodes < 5:
            return None
        if query_text:
            if not hasattr(self, "_w2v"):
                from spores.spore_utils import _word_to_vector

                self._w2v = _word_to_vector
            vec = self._w2v(query_text)
            vec = (vec + [0.0] * self.dimension)[: self.dimension]
            np_query = np.array([vec], dtype="float32")
        else:
            np_query = np.zeros((1, self.dimension), dtype="float32")
        distances, _ = self._index.search(np_query, min(50, self.total_nodes))
        valid_dists = [float(d) for d in distances[0] if d > 0]
        if len(valid_dists) < 3:
            return None
        return {
            "log_r": [math.log(d) for d in valid_dists],
            "log_m": [math.log(i + 1) for i in range(len(valid_dists))],
            "weights": [1.0] * len(valid_dists),
        }
