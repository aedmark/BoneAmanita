"""
brain/ann.py

The Dual-Tier Semantic Substrate

This module defines the spatial topology of the Hypervisor's memory.
It rejects standard "lossy summarization" of context windows. Instead, it
relies on a biological two-stage memory system:
1. The Hippocampus: Fast, exact-match cache for the current session.
2. The Cerebral Index: Deep, Approximate Nearest Neighbor (ANN) storage using FAISS.
3. The Consolidator: The REM sleep bridge that transfers data between them.
"""

import hashlib
import heapq
import math
import time
from itertools import islice
from typing import Dict, List, Any, Tuple, Optional

import faiss
import numpy as np

from core import EventBus


class HippocampalCache:
    """
    The Short-Term Working Memory.
    A fast, O(N) dictionary cache. It generates "Phantoms"—hyper-dense mathematical
    coordinate hashes that act as index cards pointing to the raw text. Highly volatile;
    clears out old memories if max_capacity is reached before a REM cycle can save them.
    """
    def __init__(self, max_capacity: int = 500):
        self.max_capacity = max_capacity
        self.nodes: Dict[str, Any] = {}

    def encode(self, node_id: str, vector: List[float], metadata: Dict[str, Any]):
        """
        Creates a new memory node. Automatically generates a short MD5 hash
        of the vector (the "Phantom") to ensure rapid lookup without doing
        heavy floating-point math during active conversation.
        """
        self.nodes.pop(node_id, None)

        # Create the Phantom: An 8-character hex string representing the exact semantic vector
        short_hash = hashlib.md5(np.array(vector, dtype=np.float32).tobytes()).hexdigest()[:8]

        self.nodes[node_id] = {
            "phantom": {
                "vector_hash": short_hash,
                "wing_id": metadata.get("wing_id", "GLOBAL"),
                "room_id": metadata.get("room_id", "GENERAL")
            },
            "vector": vector,
            "meta": metadata,
            "timestamp": time.time()
        }

        # Strict biological limit: if we learn too much too fast, the oldest memory drops.
        if len(self.nodes) > self.max_capacity:
            del self.nodes[next(iter(self.nodes))]

    def retrieve_exact(self, node_id: str) -> Optional[Dict]:
        """O(1) exact match retrieval. Refreshes the memory so it isn't pruned."""
        if val := self.nodes.pop(node_id, None):
            self.nodes[node_id] = val
            return val
        return None

    def extract_for_consolidation(self, limit: Optional[int] = None) -> List[Tuple[str, Dict]]:
        """
        Pulls a batch of memories OUT of the volatile cache to be permanently
        written to the deep Cortex during REM sleep.
        """
        target_keys = list(islice(self.nodes.keys(), limit))
        return [(k, self.nodes.pop(k)) for k in target_keys]

    def get_graph(self) -> Dict[str, set]:
        """
        Builds a map of how the short-term memories connect to each other.
        Uses vectorized matrix multiplication to find ideas that are semantically adjacent
        (> 0.75 similarity) instantly without an O(N^2) Python loop.
        """
        keys = list(self.nodes.keys())
        adj = {k: set() for k in keys}
        if len(keys) < 2:
            return adj

        vectors = np.array([self.nodes[k]["vector"] for k in keys], dtype=np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0  # Prevent division by zero
        normalized = vectors / norms

        sim_matrix = np.dot(normalized, normalized.T)
        i_idx, j_idx = np.where(sim_matrix > 0.75)

        for i, j in zip(i_idx, j_idx):
            if i != j:
                adj[keys[i]].add(keys[j])

        return adj


class CerebralIndex:
    """
    The Deep Substrate Storage

    Uses FAISS (Facebook AI Similarity Search) to manage an O(logN) Hierarchical
    Navigable Small World (HNSW) graph. This allows the system to instantly search
    thousands of memories across multiple sessions based on concept similarity.
    """
    def __init__(self, dimension: int = 8):
        self.dimension = dimension
        self.is_trained = False
        self.total_nodes = 0
        # HNSWFlat is highly efficient for nearest-neighbor approximations
        self._index = faiss.IndexHNSWFlat(self.dimension, 32)
        self._payloads: List[Dict] = []
        self._phantom_lookup: Dict[str, str] = {}

    def resolve_phantom(self, vector_hash: str) -> str:
        """Looks up the raw verbatim text."""
        return self._phantom_lookup.get(vector_hash, "")

    def add_memories(self, vectors: List[List[float]], metadata_payloads: List[Dict]):
        """Injects consolidated memories from the Hippocampus into the deep FAISS index."""
        if not vectors:
            return

        np_vectors = np.array(vectors, dtype=np.float32)
        self._index.add(np_vectors)

        for p in metadata_payloads:
            # Preserve the exact string to prevent the LLM from paraphrasing history
            if "vector_hash" in p and p["vector_hash"]:
                self._phantom_lookup[p["vector_hash"]] = p.get("raw_verbatim_text", "")

        self._payloads.extend(metadata_payloads)
        self.total_nodes += len(vectors)
        self.is_trained = True

    def lateral_ofc_retrieval(self, physics_state: Dict[str, float], k: int = 2) -> List[Dict]:
        """
        The Shadow Retrieval.
        Activates when systemic Chaos/Voltage is extremely high. Instead of looking
        for the most 'similar' memory (cosine similarity), it runs an additive heuristic.
        It retrieves explosive, compounded structural patterns to force a paradigm shift.
        """
        if not self._payloads:
            return []

        base_omega = physics_state.get("omega", 0.5)     # Structural complexity
        base_omega_r = physics_state.get("omega_r", 0.5) # Relational resonance

        def _score(payload):
            # We want the heaviest, most structurally demanding memory available.
            omega = payload.get("omega", base_omega)
            omega_r = payload.get("omega_r", base_omega_r)
            f_cost = payload.get("narrative_drag", 1.0)
            return (omega ** 2) + (2 * omega_r) + f_cost

        return heapq.nlargest(k, self._payloads, key=_score)

    def query_neighborhood(self, query_vector: List[float], k: int = 5, resonance_threshold: float = 0.5, physics_state: Optional[Dict[str, float]] = None) -> List[Dict]:
        """
        The Primary Dredge.
        Searches the deep index for the 'k' closest memories to the current thought.
        """
        if not self.is_trained or self.total_nodes == 0 or len(query_vector) != self.dimension:
            return []

        target_wing, is_lateral = None, False

        if physics_state:
            # If the system is panicking or highly energized, abandon linear search
            if physics_state.get("voltage", 0.0) > 80.0 and physics_state.get("chi", 0.0) > 0.7:
                return self.lateral_ofc_retrieval(physics_state, k=k)

            # Restrict search geometrically to save energy (don't cross-contaminate projects)
            target_wing = physics_state.get("wing_id", "GLOBAL")
            is_lateral = physics_state.get("lateral_search", False)

        np_query = np.array([query_vector], dtype=np.float32)
        distances, indices = self._index.search(np_query, min(k, self.total_nodes))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            payload = self._payloads[idx]

            # Enforce the strict 'Wing' boundary unless explicitly told to look laterally
            if target_wing and not is_lateral and payload.get("wing_id", "GLOBAL") != target_wing:
                continue

            # Convert raw Euclidean distance into a resonance score
            resonance = 1.0 / (1.0 + float(dist))
            if resonance >= resonance_threshold:
                results.append({**payload, "resonance": resonance})

        return results

    def get_local_mass_radius(self, query_text: str = "") -> Optional[Dict[str, List[float]]]:
        """
        Calculates the topological density of the memory space around a given point.
        Used to determine if the system is fixating on a single concept.
        """
        if not self.is_trained or self.total_nodes < 5:
            return None

        # Map the actual query text space instead of defaulting to the Void
        if query_text:
            from spores.spore_utils import _word_to_vector
            vec = _word_to_vector(query_text)
            # Failsafe: pad or truncate to match expected FAISS dimensions
            vec = (vec + [0.0] * self.dimension)[:self.dimension]
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
            "weights": [1.0] * len(valid_dists)
        }


class MemoryConsolidator:
    """
    The REM Sleep Bridge.
    Decouples memory writing from the active conversation loop.
    It transfers data from the volatile Hippocampus to the permanent Cortex,
    but only if the system has enough ATP to pay the synaptic cost.
    """
    def __init__(self, hippocampus: HippocampalCache, cortex: CerebralIndex, events: EventBus):
        self.hippocampus = hippocampus
        self.cortex = cortex
        self.events = events

    def trigger_rem_consolidation(self, available_atp: float) -> Tuple[int, float]:
        """
        Executes the 'Sleep' cycle.
        Calculates how many memories the system can afford to save based on current fuel.
        If ATP < 20, the system is too exhausted to dream, and memories remain stranded.
        """
        if available_atp < 20.0:
            return 0, 0.0 # Insufficient energy to consolidate memories

        # 0.1 ATP cost per memory node saved, reserving 20.0 ATP for basic survival
        max_nodes = int((available_atp - 20.0) / 0.1)
        if max_nodes < 1:
            return 0, 0.0

        pending_nodes = self.hippocampus.extract_for_consolidation(limit=max_nodes)
        vectors = [n["vector"] for _, n in pending_nodes if "vector" in n]

        # Package the metadata, ensuring the Phantom hash points back to the raw text
        payloads = [
            {"id": k, "vector_hash": n.get("phantom", {}).get("vector_hash", ""), **n.get("meta", {})}
            for k, n in pending_nodes if "vector" in n
        ]

        if not vectors:
            return 0, 0.0

        # Burn the memory permanently into the Cortex
        self.cortex.add_memories(vectors, payloads)

        count = len(vectors)
        atp_cost = 20.0 + (len(vectors) * 0.1) # Base cost of REM sleep + per-node cost

        if self.events:
            self.events.publish("SYNAPTIC_CONSOLIDATION", {"count": count, "atp_burned": atp_cost})

        return count, atp_cost