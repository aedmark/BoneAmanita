"""bone_ann.py - The Dual-Tier Semantic Substrate"""

import math
import time
import hashlib
from itertools import combinations
from typing import Dict, List, Any, Tuple, Optional
import faiss
import numpy as np
from bone_core import EventBus

class HippocampalCache:
    def __init__(self, max_capacity: int = 500):
        self.max_capacity = max_capacity
        self.nodes: Dict[str, Any] = {}

    def encode(self, node_id: str, vector: List[float], metadata: Dict[str, Any]):
        if node_id in self.nodes:
            del self.nodes[node_id]
        vector_bytes = np.array(vector, dtype=np.float32).tobytes()
        raw_hash = hashlib.md5(vector_bytes).hexdigest()
        short_hash = raw_hash[:8]
        phantom = {
            "vector_hash": short_hash,
            "wing_id": metadata.get("wing_id", "GLOBAL"),
            "room_id": metadata.get("room_id", "GENERAL")
        }
        self.nodes[node_id] = {
            "phantom": phantom,
            "vector": vector,
            "meta": metadata,
            "timestamp": time.time()
        }
        if len(self.nodes) > self.max_capacity:
            self._prune_oldest()

    def retrieve_exact(self, node_id: str) -> Optional[Dict]:
        if node_id in self.nodes:
            val = self.nodes.pop(node_id)
            self.nodes[node_id] = val
            return val
        return None

    def extract_for_consolidation(self, limit: Optional[int] = None) -> List[Tuple[str, Dict]]:
        from itertools import islice
        target_keys = list(islice(self.nodes.keys(), limit))
        return [(k, self.nodes.pop(k)) for k in target_keys]

    def _prune_oldest(self):
        if not self.nodes:
            return
        oldest_key = next(iter(self.nodes))
        del self.nodes[oldest_key]

    def get_graph(self) -> Dict[str, set]:
        adj = {k: set() for k in self.nodes}
        norms = {k: math.hypot(*n["vector"]) for k, n in self.nodes.items()}
        for (k1, n1), (k2, n2) in combinations(self.nodes.items(), 2):
            mag = norms[k1] * norms[k2]
            if mag > 0:
                dot = np.dot(n1["vector"], n2["vector"])
                if (dot / mag) > 0.75:
                    adj[k1].add(k2)
                    adj[k2].add(k1)
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
        if not vectors:
            return
        np_vectors = np.array(vectors, dtype=np.float32)
        self._index.add(np_vectors)
        for p in metadata_payloads:
            p.setdefault("raw_verbatim_text", "")
            if "vector_hash" in p:
                self._phantom_lookup[p["vector_hash"]] = p["raw_verbatim_text"]
        self._payloads.extend(metadata_payloads)
        self.total_nodes += len(vectors)
        self.is_trained = True

    def lateral_ofc_retrieval(self, physics_state: Dict[str, float], k: int = 2) -> List[Dict]:
        if not self._payloads:
            return []
        base_omega = physics_state.get("omega", 0.5)
        base_omega_r = physics_state.get("omega_r", 0.5)

        def _score(payload):
            omega = payload.get("omega", base_omega)
            omega_r = payload.get("omega_r", base_omega_r)
            f_cost = payload.get("narrative_drag", 1.0)
            return (omega ** 2) + (2 * omega_r) + f_cost

        scored = sorted(self._payloads, key=_score, reverse=True)
        return scored[:k]

    def query_neighborhood(self, query_vector: List[float], k: int = 5, resonance_threshold: float = 0.5,
                           physics_state: Optional[Dict[str, float]] = None) -> List[Dict]:
        if not self.is_trained or self.total_nodes == 0:
            return []
        if physics_state:
            voltage = physics_state.get("voltage", 0.0)
            chi = physics_state.get("chi", 0.0)
            if voltage > 80.0 and chi > 0.7:
                return self.lateral_ofc_retrieval(physics_state, k=k)
        if len(query_vector) != self.dimension:
            return []
        np_query = np.array([query_vector], dtype=np.float32)
        actual_k = min(k, self.total_nodes)
        distances, indices = self._index.search(np_query, actual_k)
        valid_neighbors = []
        target_wing = None
        is_lateral = False
        if physics_state:
            target_wing = physics_state.get("wing_id", "GLOBAL")
            is_lateral = physics_state.get("lateral_search", False)
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            payload = self._payloads[idx]
            if target_wing and payload.get("wing_id", "GLOBAL") != target_wing and not is_lateral:
                continue
            resonance = 1.0 / (1.0 + float(dist))
            if resonance >= resonance_threshold:
                valid_neighbors.append({**payload, "resonance": resonance})
        return valid_neighbors

    def get_local_mass_radius(self) -> Optional[Dict[str, List[float]]]:
        if not self.is_trained or self.total_nodes < 5:
            return None

        """We don't know where the center is, so we just query the absolute void (0,0,0...)
         and see what yells back. It works. Don't touch it."""
        np_query = np.zeros((1, self.dimension), dtype="float32")
        distances, _ = self._index.search(np_query, min(50, self.total_nodes))
        valid_dists = [float(d) for d in distances[0] if d > 0]
        if len(valid_dists) < 3:
            return None
        return {
            "log_r": [math.log(d) for d in valid_dists],
            "log_m": [math.log(i + 1) for i in range(len(valid_dists))],
            "weights": [1.0] * len(valid_dists)
        }

class MemoryConsolidator:
    def __init__(self, hippocampus: HippocampalCache, cortex: CerebralIndex, events: EventBus):
        self.hippocampus = hippocampus
        self.cortex = cortex
        self.events = events

    def trigger_rem_consolidation(self, available_atp: float) -> Tuple[int, float]:
        base_rem_cost = 20.0
        cost_per_node = 0.1
        if available_atp < base_rem_cost:
            return 0, 0.0
        surplus_atp = available_atp - base_rem_cost
        max_affordable_nodes = int(surplus_atp / cost_per_node)
        if max_affordable_nodes <= 0:
            return 0, 0.0
        pending_nodes = self.hippocampus.extract_for_consolidation(limit=max_affordable_nodes)
        vectors, payloads = [], []
        for node_id, node_data in pending_nodes:
            if "vector" in node_data:
                vectors.append(node_data["vector"])
                payloads.append({"id": node_id, **node_data.get("meta", {})})
        if not vectors:
            return 0, 0.0
        self.cortex.add_memories(vectors, payloads)
        count = len(vectors)
        atp_cost = base_rem_cost + (count * 0.1)
        if self.events:
            self.events.publish("SYNAPTIC_CONSOLIDATION", {"count": count, "atp_burned": atp_cost})
        return count, atp_cost
