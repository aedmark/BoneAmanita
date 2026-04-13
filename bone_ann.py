"""bone_ann.py - The Dual-Tier Semantic Substrate"""

import math
import time
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
        self.nodes[node_id] = {"vector": vector, "meta": metadata, "timestamp": time.time(), }
        if len(self.nodes) > self.max_capacity:
            self._prune_weakest()

    def retrieve_exact(self, node_id: str) -> Optional[Dict]:
        if node_id in self.nodes:
            val = self.nodes.pop(node_id)
            self.nodes[node_id] = val
            return val
        return None

    def extract_for_consolidation(
        self, limit: Optional[int] = None
    ) -> List[Tuple[str, Dict]]:
        target_keys = list(self.nodes.keys())[:limit] if limit is not None else list(self.nodes.keys())
        return [(k, self.nodes.pop(k)) for k in target_keys]

    def _prune_weakest(self):
        if not self.nodes:
            return
        oldest_key = next(iter(self.nodes))
        del self.nodes[oldest_key]

    def get_graph(self) -> Any:
        class _Graph:
            def __init__(self, adj):
                self.adj = adj

            def __len__(self): return len(self.adj)

        adj = {k: set() for k in self.nodes}
        for (k1, n1), (k2, n2) in combinations(self.nodes.items(), 2):
            v1, v2 = n1["vector"], n2["vector"]
            dot = sum(a * b for a, b in zip(v1, v2))
            mag = (sum(a * a for a in v1) ** 0.5) * (sum(b * b for b in v2) ** 0.5)
            if mag > 0 and (dot / mag) > 0.75:  # 0.75 Cosine Similarity Threshold
                adj[k1].add(k2)
                adj[k2].add(k1)
        return _Graph(adj)


class CerebralIndex:
    def __init__(self, dimension: int = 8, index_type: str = "HNSW"):
        self.dimension = dimension
        self.index_type = index_type
        self.is_trained = False
        self.total_nodes = 0
        self._index = faiss.IndexHNSWFlat(self.dimension, 32)
        self._payloads: List[Dict] = []

    def add_memories(self, vectors: List[List[float]], metadata_payloads: List[Dict]):
        if not vectors:
            return
        np_vectors = np.ascontiguousarray(np.array(vectors).astype("float32"))
        if np_vectors.shape[1] != self.dimension:
            return
        self._index.add(np_vectors)
        self._payloads.extend(metadata_payloads)
        self.total_nodes += len(vectors)
        self.is_trained = True

    def query_neighborhood(self, query_vector: List[float], k: int = 5, resonance_threshold: float = 0.5) -> List[Dict]:
        if (not self.is_trained
            or self.total_nodes == 0
            or len(query_vector) != self.dimension ):
            return []
        np_query = np.ascontiguousarray(np.array([query_vector]).astype("float32"))
        actual_k = min(k, self.total_nodes)
        distances, indices = self._index.search(np_query, actual_k)
        valid_neighbors = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            resonance = 1.0 / (1.0 + float(dist))
            if resonance >= resonance_threshold:
                valid_neighbors.append({**self._payloads[idx], "resonance": resonance})
        return valid_neighbors

    def get_local_mass_radius(self, query_text: str) -> Optional[Dict[str, List[float]]]:
        if not self.is_trained or self.total_nodes < 5:
            return None
        np_query = np.zeros((1, self.dimension), dtype="float32")
        distances, _ = self._index.search(np_query, min(50, self.total_nodes))
        log_r, log_m, weights = [], [], []
        mass = 1
        for dist in (float(d) for d in distances[0] if d > 0):
            log_r.append(math.log(dist))
            log_m.append(math.log(mass))
            weights.append(1.0)
            mass += 1
        if len(log_r) < 3:
            return None
        return {"log_r": log_r, "log_m": log_m, "weights": weights}

class MemoryConsolidator:
    def __init__(
        self, hippocampus: HippocampalCache, cortex: CerebralIndex, events: EventBus ):
        self.hippocampus = hippocampus
        self.cortex = cortex
        self.events = events

    def trigger_rem_consolidation(self, available_atp: float) -> Tuple[int, float]:
        if available_atp < 20.0:
            return 0, 0.0
        max_affordable_nodes = int((available_atp - 20.0) / 0.1)
        if max_affordable_nodes <= 0:
            return 0, 0.0
        pending_nodes = self.hippocampus.extract_for_consolidation(limit=max_affordable_nodes)
        valid_nodes = [(nid, d) for nid, d in pending_nodes if "vector" in d]
        if not valid_nodes:
            return 0, 0.0
        vectors = [d["vector"] for _, d in valid_nodes]
        payloads = [{"id": nid, **d.get("meta", {})} for nid, d in valid_nodes]
        self.cortex.add_memories(vectors, payloads)
        atp_cost = len(valid_nodes) * 0.1
        if self.events:
            self.events.publish("SYNAPTIC_CONSOLIDATION", {"count": len(valid_nodes), "atp_burned": atp_cost})
        return len(valid_nodes), atp_cost
