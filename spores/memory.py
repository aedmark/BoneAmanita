"""spores/memory.py
This module governs the architecture of the engine's memory systems.
It maps the transition of semantic data from volatile, highly connected
short-term graph networks (MemoryCore) down into the permanent, compressed
mathematical substrate of long-term storage (SubconsciousStrata).
Classes:
    - SubconsciousStrata: The deep, append-only fossil record and matrix space.
    - MemoryCore: The active semantic graph (Hippocampus) that learns,
      forgets, and occasionally cannibalizes its own nodes to survive.
"""
import json
import os
import random
import time
from collections import deque
from typing import List, Tuple, Optional, Dict
from core import BoneJSONEncoder
from struts import ux, ux_format
from presets import BoneConfig
from spores.spore_utils import _identity, _word_to_vector, _mat_mul, _reorthogonalize, _householder


class SubconsciousStrata:
    """
    The deep substrate. When active memories are destroyed (cannibalized)
    or deliberately repressed, they are "buried" here.
    Instead of just keeping a text log, this class maintains two mathematical
    matrices (M_t and Q_n) that constantly rotate and decay. This allows the
    system to retain the "vibe" or geometric signature of long-forgotten words
    without carrying the metabolic cost of keeping them in active memory.
    """

    def __init__(self, filename="memories/subconscious.jsonl"):
        self.filepath = filename
        self.directory = os.path.dirname(filename)
        if self.directory and not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.index = set()
        self._load_index()
        self.matrix_filepath = os.path.join(self.directory, "m_t_matrix.json")
        self.q_filepath = os.path.join(self.directory, "q_n_matrix.json")
        self.M_t = self._load_matrix()
        self.Q_n = self._load_q_matrix()

    def _load_json(self, path, default_factory):
        """[H]euristic: Failsafe loading. If the file is locked or corrupt, return the default."""
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return default_factory()

    def _load_matrix(self):
        return self._load_json(self.matrix_filepath, lambda: [[0.0] * 8 for _ in range(8)])

    def _load_q_matrix(self):
        return self._load_json(self.q_filepath, lambda: _identity(8))

    def save_matrix(self):
        try:
            with open(self.matrix_filepath, "w") as f:
                json.dump(self.M_t, f)
            with open(self.q_filepath, "w") as f:
                json.dump(self.Q_n, f)
        except Exception:
            pass

    def _iter_entries(self):
        """Yields JSON records from the log line-by-line to prevent massive RAM spikes."""
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
        self.index = {e.get("word"): e for e in self._iter_entries() if e.get("word")}

    def bury(self, fossil_data: Dict, config_ref=None):
        """
        The act of permanent compression. Takes a dying active memory, appends it
        to the JSONL fossil record, and permanently warps the deep matrices (M_t and Q_n)
        using the word's structural vector.
        """
        try:
            from struts import safe_get
            target_cfg = config_ref or BoneConfig
            cfg = safe_get(target_cfg, "SPORES", {})
            max_idx = int(safe_get(cfg, "MAX_INDEX_SIZE", 1000))
            if len(self.index) > max_idx:
                self._prune_strata()
            with open(self.filepath, "a", encoding="utf-8") as f:
                fossil_data["buried_at"] = time.time()
                f.write(json.dumps(fossil_data, cls=BoneJSONEncoder) + "\n")
            self.index[fossil_data["word"]] = fossil_data
            word = fossil_data["word"]
            mass = fossil_data.get("mass", 1.0)
            K = _word_to_vector(word)
            V = _word_to_vector(word + "_val")
            scale = min(1.0, mass / 10.0)
            decay = 0.99
            self.M_t = [[(self.M_t[i][j] * decay) + (K[i] * V[j]) * scale for j in range(8)] for i in range(8)]
            H = _householder(K)
            self.Q_n = _mat_mul(H, self.Q_n)
            self.Q_n = _reorthogonalize(self.Q_n)
            if not fossil_data.get("reconstructive", False):
                self.save_matrix()
            return True
        except IOError:
            return False

    def _prune_strata(self):
        """Trims the JSONL file to keep only the most recent 90% of entries."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            keep_count = int(len(lines) * 0.9)
            survivors = lines[-keep_count:] if keep_count else []
            import tempfile
            fd, temp_path = tempfile.mkstemp(dir=self.directory, text=True)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.writelines(survivors)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self.filepath)
            self._load_index()
        except Exception:
            pass

    def dredge(self, trigger_word: str) -> Optional[Dict]:
        """Attempts to dig up the exact literal data of a buried word using O(1) memory cache."""
        return self.index.get(trigger_word)

    def dredge_vibe(self, trigger_word: str) -> list:
        """
        Retrieves the mathematical "ghost" of a word. By multiplying the word's
        vector against the current M_t matrix, we get its structural relevance
        to everything else the system has ever learned.
        """
        Q = _word_to_vector(trigger_word)
        out = [0.0] * 8
        for i in range(8):
            for j in range(8):
                out[j] += Q[i] * self.M_t[i][j]
        return [round(val, 3) for val in out]


class MemoryCore:
    """
    The active semantic graph (Hippocampus).
    This is where current context lives. Words are nodes, and the frequency
    at which they appear together form weighted synaptic edges.
    """
    DIMENSION_MAP = {
        "STR": {"heavy", "constructive", "base"},
        "VEL": {"kinetic", "explosive", "mot"},
        "ENT": {"antigen", "toxin", "broken"},
        "PHI": {"thermal", "photo"},
        "PSI": {"abstract", "sacred", "idea"},
        "BET": {"social", "suburban", "play"},
    }

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
        """
        Retrieves graph memories that resonate with the current dimensional state.
        Critically, the act of remembering mathematically alters the memory.
        """
        if not self.graph:
            return []
        active_dims = {k: v for k, v in vector.items() if v > 0.4}
        if not active_dims and vector:
            top_dim = max(vector, key=vector.get)
            if vector[top_dim] > 0.1:
                active_dims = {top_dim: vector[top_dim]}
            else:
                active_dims = {"ENT": 0.2}
        active_dim_cats = {dim: self.DIMENSION_MAP.get(dim, set()) for dim in active_dims}
        scored_memories = []
        for node, data in self.graph.items():
            resonance_score = 0.0
            node_cats = self.lex.get_categories_for_word(node) if self.lex else set()
            for dim, val in active_dims.items():
                if node_cats & active_dim_cats[dim]:
                    resonance_score += val * 1.5
            mass = sum(data.get("edges", {}).values())
            resonance_score += mass * 0.1
            if resonance_score > 0.5:
                scored_memories.append((resonance_score, node, data))
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        results = []
        res_prefix = ux("spore_strings", "core_illuminate_resonant") or "Resonant"
        assoc_prefix = ux("spore_strings", "core_illuminate_associated") or "Associated"
        fmt = (ux("spore_strings", "core_illuminate_format") or "{prefix} Engram: '{name}'{conn_str}")
        for score, name, data in scored_memories[:limit]:
            connections = list(data.get("edges", {}).keys())
            if active_dims:
                if not data.get("is_diamond", False):
                    for edge_k, edge_v in data.get("edges", {}).items():
                        if not self.graph.get(edge_k, {}).get("is_diamond", False):
                            data["edges"][edge_k] = edge_v * 0.95
                top_active_dim = max(active_dims, key=active_dims.get)
                dim_words = list(self.DIMENSION_MAP.get(top_active_dim, {"static"}))
                if dim_words:
                    chosen_word = random.choice(dim_words)
                    edges = data.setdefault("edges", {})
                    edges[chosen_word] = edges.get(chosen_word, 0.0) + 1.0
                try:
                    self.subconscious.bury({"word": name, "mass": 1.0, "reconstructive": True}, config_ref=self.cfg)
                except Exception:
                    pass
            is_resonant = score > 0.5
            current_prefix = res_prefix if is_resonant else assoc_prefix
            connection_string = f" -> [{', '.join(connections[:2])}]" if connections else ""
            formatted_result = fmt.format(prefix=current_prefix, name=name.upper(), conn_str=connection_string)
            results.append(formatted_result)
        return results

    def calculate_mass(self, node):
        """Calculates the structural weight of a node based on its total synaptic bonds."""
        if node not in self.graph:
            return 0.0
        return sum(self.graph[node]["edges"].values())

    def strengthen_link(self, source, target, rate, decay):
        """Reinforces the connection between two ideas. Capped at 10.0 to prevent runaway optimization."""
        if source not in self.graph:
            return
        edges = self.graph[source]["edges"]
        current_weight = edges.get(target, 0.0)
        edges[target] = min(10.0, current_weight + rate * (1.0 - current_weight * decay))

    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
        """
        Global decay loop. Simulates the passage of time.
        Edges weaken. If an edge drops below the threshold, it snaps.
        If a node loses all its edges, the system forgets it entirely.
        """
        pruned_count = total_decayed = 0
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
                del self.graph[node]
        valid_nodes = set(self.graph.keys())
        for data in self.graph.values():
            data["edges"] = {k: v for k, v in data["edges"].items() if k in valid_nodes}
        return ux_format("spore_strings", "core_pruned", default="", total=total_decayed, pruned=pruned_count)

    def cannibalize(self, current_tick, preserve_current=None) -> Tuple[Optional[str], str]:
        """
        Autophagy mechanism. Activated when the system reaches critical cognitive load.
        The system identifies the weakest, oldest, unprotected node in its graph,
        destroys it to free up RAM/ATP, and dumps its corpse into the Subconscious strata.
        """
        protected = set(self.cortical_stack)
        if preserve_current:
            protected.update(preserve_current if isinstance(preserve_current, list) else [preserve_current])
        candidates = []
        for k, v in self.graph.items():
            if k not in protected and not v.get("is_diamond", False):
                mass = sum(v.get("edges", {}).values())
                age = max(1, current_tick - v.get("last_tick", 0))
                score = (mass + 1.0) * (1.0 + (10.0 / age))
                candidates.append((k, v, score))
        if not candidates:
            return None, ux("spore_strings", "core_lock") or ""
        victim, data, score = min(candidates, key=lambda x: x[2])
        mass = sum(data["edges"].values())
        lifespan = current_tick - data.get("strata", {}).get("birth_tick", current_tick)
        fossil_data = {
            "word": victim,
            "mass": round(mass, 2),
            "lifespan": lifespan,
            "edges": data["edges"],
            "death_tick": current_tick,
        }
        self.subconscious.bury(fossil_data, config_ref=self.cfg)
        del self.graph[victim]
        for node_data in self.graph.values():
            node_data["edges"].pop(victim, None)
        msg = ux("spore_strings", "core_repressed") or "Core Repressed"
        return victim, msg.format(victim=victim, score=score) if msg else "Memory Consumed"
