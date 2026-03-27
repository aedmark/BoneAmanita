""" bone_ann.py - The Dual-Tier Semantic Substrate """

import time
import numpy as np
import faiss
from typing import Dict, List, Any, Tuple, Optional
from bone_core import safe_get, safe_set, EventBus

class HippocampalCache:
    def __init__(self, max_capacity: int = 500):
        self.max_capacity = max_capacity
        self.nodes: Dict[str, Any] = {}
        self.tick_tracker = 0

    def encode(self, node_id: str, vector: List[float], metadata: Dict[str, Any]):
        self.nodes[node_id] = {"vector": vector, "meta": metadata, "timestamp": time.time(), "last_accessed": self.tick_tracker}
        if len(self.nodes) > self.max_capacity:
            self._prune_weakest()

    def retrieve_exact(self, node_id: str) -> Optional[Dict]:
        if node_id in self.nodes:
            self.tick_tracker += 1
            self.nodes[node_id]["last_accessed"] = self.tick_tracker
            return self.nodes[node_id]
        return None

    def extract_for_consolidation(self) -> List[Tuple[str, Dict]]:
        consolidated = list(self.nodes.items())
        self.nodes.clear()
        return consolidated

    def _prune_weakest(self):
        if not self.nodes: return
        weakest = min(self.nodes.items(), key=lambda x: x[1].get("last_accessed", 0))
        del self.nodes[weakest[0]]

class CerebralIndex:
    def __init__(self, dimension: int = 8, index_type: str = "HNSW"):
        self.dimension = dimension
        self.index_type = index_type
        self.is_trained = False
        self.total_nodes = 0
        self._index = faiss.IndexHNSWFlat(self.dimension, 32)
        self._payloads: List[Dict] = []

    def add_memories(self, vectors: List[List[float]], metadata_payloads: List[Dict]):
        if not vectors: return
        np_vectors = np.array(vectors).astype('float32')
        self._index.add(np_vectors)
        self._payloads.extend(metadata_payloads)
        self.total_nodes += len(vectors)
        self.is_trained = True

    def query_neighborhood(self, query_vector: List[float], k: int = 5, resonance_threshold: float = 0.5) -> List[Dict]:
        if not self.is_trained or self.total_nodes == 0:
            return []
        np_query = np.array([query_vector]).astype('float32')
        actual_k = min(k, self.total_nodes)
        distances, indices = self._index.search(np_query, actual_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:
                pseudo_resonance = 1.0 / (1.0 + float(dist))
                if pseudo_resonance >= resonance_threshold:
                    node_data = dict(self._payloads[idx])
                    node_data["resonance"] = pseudo_resonance
                    results.append(node_data)
        return results

class MemoryConsolidator:
    def __init__(self, hippocampus: HippocampalCache, cortex: CerebralIndex, events: EventBus):
        self.hippocampus = hippocampus
        self.cortex = cortex
        self.events = events

    def trigger_rem_consolidation(self, available_atp: float) -> Tuple[int, float]:
        if available_atp < 20.0:
            return 0, 0.0
        pending_nodes = self.hippocampus.extract_for_consolidation()
        valid_nodes = [(nid, d) for nid, d in pending_nodes if "vector" in d]
        if not valid_nodes:
            return 0, 0.0
        vectors = [d["vector"] for _, d in valid_nodes]
        payloads = [{"id": nid, **d.get("meta", {})} for nid, d in valid_nodes]
        self.cortex.add_memories(vectors, payloads)
        atp_cost = len(valid_nodes) * 0.1
        if self.events:
            self.events.publish("SYNAPTIC_CONSOLIDATION", {"count": len(pending_nodes), "atp_burned": atp_cost})
        return len(pending_nodes), atp_cost