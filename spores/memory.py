"""spores/memory.py
ORDVEC math provided by Nelson Spence and Project Navi via Apache 2.0 Licensing
"""

import json
import os
import re
import tempfile
import time
from collections import deque
from typing import Any
from typing import List, Tuple, Optional, Dict

from core import JSONEncoder
from presets import BoneConfig
from spores.spore_utils import _word_to_vector
from struts import ux, ux_format

try:
    import numpy as np
except ImportError:
    np = None

_ZERO_WIDTH_RE = re.compile(r'[\u200B-\u200D\uFEFF\u202A-\u202E]')

def _billy_mitchell_protocol(data: Any, seen: set = None) -> Any:
    if seen is None:
        seen = set()
    if id(data) in seen:
        return data
    if isinstance(data, (dict, list)):
        seen.add(id(data))
    if isinstance(data, str):
        return _ZERO_WIDTH_RE.sub('', data)
    elif isinstance(data, dict):
        return {_billy_mitchell_protocol(k, seen): _billy_mitchell_protocol(v, seen) for k, v in data.items()}
    elif isinstance(data, list):
        return [_billy_mitchell_protocol(i, seen) for i in data]
    return data

class SubconsciousStrata:
    def __init__(self, filename="memories/subconscious.jsonl"):
        self.filepath = filename
        self.directory = os.path.dirname(filename)
        if self.directory and not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.index = {}
        self.metadata_log = []
        self.rank_bank = None
        self._load_index()

    def _rank_transform(self, vec: list) -> Optional['np.ndarray']:
        """Convert absolute float vectors into noise-resistant ordinal ranks."""
        if np is None:
            return None
        arr = np.array(vec, dtype=np.float32)
        return np.argsort(np.argsort(arr)).astype(np.uint16)

    def _iter_entries(self):
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            pass
        except IOError:
            pass

    def _load_index(self):
        self.index = {}
        self.metadata_log = []
        ranks = []
        for e in self._iter_entries():
            if e.get("word"):
                self.index[e["word"]] = e
                self.metadata_log.append(e)
                if np is not None:
                    vec = _word_to_vector(e["word"])
                    ranks.append(self._rank_transform(vec))
        if np is not None and ranks:
            self.rank_bank = np.vstack(ranks)

    def bury(self, fossil_data: Dict, config_ref=None):
        try:
            from struts import safe_get
            clean_fossil = _billy_mitchell_protocol(fossil_data)
            target_cfg = config_ref or BoneConfig
            cfg = safe_get(target_cfg, "SPORES", {})
            max_idx = int(safe_get(cfg, "MAX_INDEX_SIZE", 1000))
            if len(self.index) > max_idx:
                self._prune_strata()
            with open(self.filepath, "a", encoding="utf-8") as f:
                clean_fossil["buried_at"] = time.time()
                f.write(json.dumps(clean_fossil, cls=JSONEncoder) + "\n")
            word = clean_fossil.get("word")
            if word:
                self.index[word] = clean_fossil
            self.metadata_log.append(clean_fossil)
            if np is not None:
                K = _word_to_vector(word)
                rank_vec = self._rank_transform(K)
                if self.rank_bank is None:
                    self.rank_bank = rank_vec.reshape(1, -1)
                else:
                    self.rank_bank = np.vstack([self.rank_bank, rank_vec])
            return True
        except IOError:
            return False

    def _prune_strata(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            keep_count = int(len(lines) * 0.9)
            survivors = lines[-keep_count:] if keep_count else []
            fd, temp_path = tempfile.mkstemp(dir=self.directory, text=True)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.writelines(survivors)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self.filepath)
            if keep_count:
                self.metadata_log = self.metadata_log[-keep_count:]
                self.index = {e["word"]: e for e in self.metadata_log if "word" in e}
                if self.rank_bank is not None and len(self.rank_bank) >= keep_count:
                    self.rank_bank = self.rank_bank[-keep_count:]
            else:
                self.metadata_log, self.index, self.rank_bank = [], {}, None
        except Exception:
            pass

    def dredge(self, trigger_word: str) -> Optional[Dict]:
        return self.index.get(trigger_word)

    def dredge_vibe_by_vector(self, query_vector, k: int = 3) -> list:
        """Core Asymmetric Rank-Cosine Search accepting a raw vector."""
        if np is None or self.rank_bank is None or len(self.rank_bank) == 0:
            return []
        dim = self.rank_bank.shape[1]
        mean = (dim - 1) / 2.0
        norm = np.sqrt((dim * (dim**2 - 1.0)) / 12.0)
        inv_norm = 1.0 / norm
        Q_arr = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(Q_arr)
        q_unit = Q_arr / q_norm if q_norm > 0 else Q_arr
        q_sum = np.sum(q_unit)
        raw_scores = np.dot(self.rank_bank, q_unit)
        scores = (raw_scores - (mean * q_sum)) * inv_norm
        if len(scores) <= k:
            top_k_idx = np.argsort(scores)[::-1]
        else:
            top_k_idx = np.argpartition(scores, -k)[-k:]
            top_k_idx = top_k_idx[np.argsort(scores[top_k_idx])[::-1]]
        results = []
        for idx in top_k_idx:
            if 0 <= idx < len(self.metadata_log):
                meta = self.metadata_log[idx]
                results.append({"word": meta.get("word"), "score": float(scores[idx]), "data": meta})
        return results

    def dredge_vibe(self, trigger_word: str, k: int = 3) -> list:
        """True Asymmetric Rank-Cosine Search."""
        Q = _word_to_vector(trigger_word)
        return self.dredge_vibe_by_vector(Q, k)

class MemoryCore:
    DIMENSION_MAP = {"STR": {"heavy", "constructive", "base"}, "VEL": {"kinetic", "explosive", "mot"},
                     "ENT": {"antigen", "toxin", "broken"}, "PHI": {"thermal", "photo"},
                     "PSI": {"abstract", "sacred", "idea"}, "BET": {"social", "suburban", "play"}, }

    def __init__(self, events_ref, subconscious_ref, config_ref=None, lexicon_ref=None):
        self.events = events_ref
        self.subconscious = subconscious_ref
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref
        self.graph = {}
        self.cortical_stack = deque(maxlen=15)
        self.short_term_buffer = deque(maxlen=10)
        self.consolidation_threshold = 5.0

    def illuminate(self, vector: Dict[str, float], limit: int = 5) -> List[str]:
        if not self.graph:
            return []
        active_dims = {k: v for k, v in vector.items() if v > 0.4}
        if not active_dims and vector:
            top_dim = max(vector, key=vector.__getitem__)
            active_dims = {top_dim: vector[top_dim]} if vector[top_dim] > 0.1 else {"ENT": 0.2}
        active_dim_cats = {dim: self.DIMENSION_MAP.get(dim, set()) for dim in active_dims}
        scored_memories = []
        ent_vel_boost = active_dims.get("ENT", 0.0) > 0.7 or active_dims.get("VEL", 0.0) > 0.7
        for node, data in self.graph.items():
            resonance_score = 0.0
            node_cats = self.lex.get_categories_for_word(node) if self.lex else set()
            for dim, val in active_dims.items():
                if not node_cats.isdisjoint(active_dim_cats[dim]):  # isdisjoint is faster than intersection &
                    resonance_score += val * 1.5
            mass = float(sum(data.get("edges", {}).values()))
            base_mass_score = mass * 0.1
            if ent_vel_boost:
                resonance_score = (resonance_score + base_mass_score) * (1.0 + (mass * 0.5))
            else:
                resonance_score += base_mass_score
            if resonance_score > 0.5:
                scored_memories.append((resonance_score, node, data))
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        results = []
        res_prefix = ux("spore_strings", "core_illuminate_resonant") or "Resonant"
        assoc_prefix = ux("spore_strings", "core_illuminate_associated") or "Associated"
        fmt = (ux("spore_strings", "core_illuminate_format") or "{prefix} Engram: '{name}'{conn_str}")
        for score, name, data in scored_memories[:limit]:
            connections = list(data.get("edges", {}).keys())
            if not data.get("is_diamond", False):
                data["edges"] = {k: (v if self.graph.get(k, {}).get("is_diamond", False) else v * 0.95)
                                 for k, v in data.get("edges", {}).items()}
            is_resonant = score > 0.5
            current_prefix = res_prefix if is_resonant else assoc_prefix
            connection_string = f" -> [{', '.join(connections[:2])}]" if connections else ""
            results.append(fmt.format(prefix=current_prefix, name=name.upper(), conn_str=connection_string))
        survivors = [name for score, name, data in scored_memories[:limit] if score > 0.5]
        if len(survivors) > 1:
            import itertools
            for node_a, node_b in itertools.combinations(survivors, 2):
                self.graph[node_a].setdefault("edges", {})
                self.graph[node_b].setdefault("edges", {})
                current_a_to_b = self.graph[node_a]["edges"].get(node_b, 0.0)
                self.graph[node_a]["edges"][node_b] = min(10.0, current_a_to_b + 0.5)
                current_b_to_a = self.graph[node_b]["edges"].get(node_a, 0.0)
                self.graph[node_b]["edges"][node_a] = min(10.0, current_b_to_a + 0.5)
        if len(survivors) >= 2:
            self.hallucinate_from_subconscious(survivors)
        return results

    def hallucinate_from_subconscious(self, active_nodes: List[str]):
        """Vector Centroid Hallucination (The Deep Dredge)."""
        if len(active_nodes) < 2 or np is None:
            return
        vectors = []
        for node in active_nodes:
            vec = _word_to_vector(node)
            if vec is not None:
                vectors.append(vec)
        if not vectors:
            return
        centroid_vector = np.mean(vectors, axis=0)
        recovered = self.subconscious.dredge_vibe_by_vector(centroid_vector, k=1)
        if recovered:
            phantom_word = recovered[0]["word"]
            if phantom_word not in self.graph:
                self.graph[phantom_word] = {"edges": {}, "is_diamond": False}
            for node in active_nodes:
                w_out = self.graph[node].setdefault("edges", {}).get(phantom_word, 0.0)
                self.graph[node]["edges"][phantom_word] = min(10.0, w_out + 0.5)
                w_in = self.graph[phantom_word].setdefault("edges", {}).get(node, 0.0)
                self.graph[phantom_word]["edges"][node] = min(10.0, w_in + 0.5)

    def calculate_mass(self, node):
        if node not in self.graph:
            return 0.0
        return float(sum(self.graph[node]["edges"].values()))

    def strengthen_link(self, source, target, rate, decay):
        if source not in self.graph:
            return
        edges = self.graph[source]["edges"]
        current_weight = edges.get(target, 0.0)
        edges[target] = min(10.0, current_weight + rate * (1.0 - current_weight * decay))

    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
        pruned_count = total_decayed = 0
        dead_nodes = set()
        for node in list(self.graph.keys()):
            edges = self.graph[node]["edges"]
            new_edges = {}
            for t, w in edges.items():
                decayed_w = w * (scaling_factor + (0.14 * min(1.0, w / 10.0)))
                if decayed_w >= prune_threshold:
                    new_edges[t] = decayed_w
            total_decayed += len(edges)
            pruned_count += len(edges) - len(new_edges)
            self.graph[node]["edges"] = new_edges
            if not new_edges and not self.graph[node].get("is_diamond", False):
                dead_nodes.add(node)
                del self.graph[node]
        if dead_nodes:
            for data in self.graph.values():
                if edges := data.get("edges"):
                    for dead in dead_nodes.intersection(edges.keys()):
                        del edges[dead]
        return ux_format("spore_strings", "core_pruned", default="", total=total_decayed, pruned=pruned_count)

    def cannibalize(self, current_tick, preserve_current=None) -> Tuple[Optional[str], str]:
        protected = set(self.cortical_stack)
        if preserve_current:
            protected.update(preserve_current) if isinstance(preserve_current, list) else protected.add(preserve_current)
        victim, min_data, min_score = None, None, float('inf')
        for k, v in self.graph.items():
            if k not in protected and not v.get("is_diamond", False):
                mass = float(sum(v.get("edges", {}).values()))
                age = max(1, current_tick - v.get("last_tick", 0))
                score = (mass + 1.0) * (1.0 + (10.0 / age))
                if score < min_score:
                    victim, min_data, min_score = k, v, score
        if not victim:
            return None, ux("spore_strings", "core_lock") or ""
        data, score = min_data, min_score
        mass = float(sum(data.get("edges", {}).values()))
        lifespan = current_tick - (data.get("strata") or {}).get("birth_tick", current_tick)
        fossil_data = {"word": victim, "mass": round(mass, 2), "lifespan": lifespan, "edges": data["edges"], "death_tick": current_tick, }
        self.subconscious.bury(fossil_data, config_ref=self.cfg)
        if hasattr(self, "events") and self.events:
            self.events.publish("MEMORY_BURIED", {"fossil": fossil_data})
        del self.graph[victim]
        for node_data in self.graph.values():
            node_data["edges"].pop(victim, None)
        msg = ux("spore_strings", "core_repressed") or "Core Repressed"
        return victim, msg.format(victim=victim, score=score) if msg else "Memory Consumed"
