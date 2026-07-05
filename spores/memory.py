"""spores/memory.py
ORDVEC math provided by Nelson Spence and Project Navi via Apache 2.0 Licensing
"""

import heapq
import itertools
import json
import os
import re
import tempfile
import time
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

from core import JSONEncoder
from presets import BoneConfig
from spores.spore_utils import _word_to_vector
from struts import safe_get, ux, ux_format

try:
    import numpy as np
except ImportError:
    np = None

try:
    import ordvec
    from ordvec import RankQuant, SignBitmap
except ImportError:
    ordvec = None

_ZERO_WIDTH_RE = re.compile(r"[\u200B-\u200D\uFEFF\u202A-\u202E]")


def _billy_mitchell_protocol(data: Any, memo: dict = None) -> Any:
    if memo is None:
        memo = {}
    if id(data) in memo:
        return memo[id(data)]

    if isinstance(data, str):
        return _ZERO_WIDTH_RE.sub("", data)
    elif isinstance(data, dict):
        memo[id(data)] = clean_dict = {}
        for k, v in data.items():
            clean_k = _ZERO_WIDTH_RE.sub("", k) if isinstance(k, str) else k
            clean_dict[clean_k] = _billy_mitchell_protocol(v, memo)
        return clean_dict
    elif isinstance(data, list):
        clean_list = []
        memo[id(data)] = clean_list
        for i in data:
            clean_list.append(_billy_mitchell_protocol(i, memo))
        return clean_list
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
        self.bitmap = None
        self.quantizer = None
        self._load_index()

    def _rebuild_ordvec(self, context_msg="Rebuild"):
        if ordvec and self.rank_bank is not None and len(self.rank_bank) >= 32:
            try:
                dim = self.rank_bank.shape[1]
                self.bitmap = SignBitmap(dim)
                self.quantizer = RankQuant(dim, 4)
                self.bitmap.add(self.rank_bank)
                self.quantizer.add(self.rank_bank)
            except Exception as e:
                print(f"\n[ORDVEC] {context_msg} Failure: {e}")
                self.bitmap = None
                self.quantizer = None

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
        raw_vectors = []
        for e in self._iter_entries():
            if e.get("word"):
                self.index[e["word"]] = e
                self.metadata_log.append(e)
                if np is not None:
                    raw_vec = _word_to_vector(e["word"])
                    if raw_vec is not None:
                        vec = np.array(raw_vec, dtype=np.float32)
                        remainder = vec.shape[0] % 64
                        if remainder != 0:
                            vec = np.pad(vec, (0, 64 - remainder), mode="constant")
                        raw_vectors.append(vec)

        if np is not None and raw_vectors:
            self.rank_bank = np.ascontiguousarray(
                np.vstack(raw_vectors), dtype=np.float32
            )
            self._rebuild_ordvec("Boot")

    def bury(self, fossil_data: Dict, config_ref=None):
        try:
            clean_fossil = _billy_mitchell_protocol(fossil_data)
            max_idx = int(
                safe_get(
                    safe_get(config_ref or BoneConfig, "SPORES", {}),
                    "MAX_INDEX_SIZE",
                    1000,
                )
            )
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
                raw_vec = _word_to_vector(word)
                if raw_vec is not None:
                    vec = np.array(raw_vec, dtype=np.float32)
                    remainder = vec.shape[0] % 64
                    if remainder != 0:
                        vec = np.pad(vec, (0, 64 - remainder), mode="constant")

                    if self.rank_bank is None:
                        self.rank_bank = np.ascontiguousarray([vec], dtype=np.float32)
                    else:
                        self.rank_bank = np.ascontiguousarray(
                            np.vstack([self.rank_bank, vec]), dtype=np.float32
                        )

                    if ordvec:
                        if len(self.rank_bank) == 32:
                            self._rebuild_ordvec("Boot")
                        elif (
                            len(self.rank_bank) > 32
                            and self.bitmap is not None
                            and self.quantizer is not None
                        ):
                            try:
                                vec_2d = np.ascontiguousarray([vec], dtype=np.float32)
                                self.bitmap.add(vec_2d)
                                self.quantizer.add(vec_2d)
                            except Exception as e:
                                print(f"\n[ORDVEC] Append Failure: {e}")
                                self.bitmap = None
                                self.quantizer = None
            return True
        except IOError:
            return False

    def _prune_strata(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            file_keep_count = int(len(lines) * 0.9)
            survivors = lines[-file_keep_count:] if file_keep_count else []
            fd, temp_path = tempfile.mkstemp(dir=self.directory, text=True)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.writelines(survivors)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self.filepath)
            if self.metadata_log:
                meta_keep = int(len(self.metadata_log) * 0.9)
                self.metadata_log = self.metadata_log[-meta_keep:] if meta_keep else []
                self.index = {e["word"]: e for e in self.metadata_log if "word" in e}
            if self.rank_bank is not None:
                rank_keep = int(len(self.rank_bank) * 0.9)
                if rank_keep > 0:
                    self.rank_bank = np.ascontiguousarray(
                        self.rank_bank[-rank_keep:], dtype=np.float32
                    )
                    self._rebuild_ordvec("Prune Rebuild")
                else:
                    self.rank_bank, self.bitmap, self.quantizer = None, None, None
        except Exception:
            pass

    def dredge_vibe_by_vector(
        self, query_vector, k: int = 3, cortisol: float = 0.0
    ) -> list:
        total_memories = len(self.metadata_log)
        if total_memories == 0 or self.rank_bank is None:
            return []

        effective_k = (
            max(1, int(k * (1.0 - (cortisol * 0.75)))) if cortisol > 0.4 else k
        )
        effective_k = min(effective_k, total_memories)
        min_score_threshold = cortisol * 0.3

        Q_arr = np.array(query_vector, dtype=np.float32)
        remainder = Q_arr.shape[0] % 64
        if remainder != 0:
            Q_arr = np.pad(Q_arr, (0, 64 - remainder), mode="constant")

        Q_arr = np.ascontiguousarray(Q_arr, dtype=np.float32)
        top_indices, scores = [], []

        if ordvec is not None and self.quantizer is not None:
            coarse_k = min(effective_k * 8, total_memories)
            try:
                candidate_indices = self.bitmap.scan(Q_arr, coarse_k)
                top_indices, scores = self.quantizer.rerank(
                    Q_arr, candidate_indices, effective_k
                )
            except Exception as e:
                pass

        if not len(top_indices):
            norm_q = np.linalg.norm(Q_arr)
            if norm_q > 0:
                norms_bank = np.linalg.norm(self.rank_bank, axis=1)
                valid = norms_bank > 0
                all_scores = np.zeros(total_memories, dtype=np.float32)
                all_scores[valid] = np.dot(self.rank_bank[valid], Q_arr) / (
                    norms_bank[valid] * norm_q
                )

                if total_memories <= effective_k:
                    top_indices = np.argsort(all_scores)[::-1]
                else:
                    top_indices = np.argpartition(all_scores, -effective_k)[
                        -effective_k:
                    ]
                    top_indices = top_indices[np.argsort(all_scores[top_indices])[::-1]]

                scores = all_scores[top_indices]

        results = []
        for idx, score in zip(top_indices, scores):
            if score >= min_score_threshold and 0 <= int(idx) < len(self.metadata_log):
                meta = self.metadata_log[int(idx)]
                results.append(
                    {"word": meta.get("word"), "score": float(score), "data": meta}
                )

        return results

    def dredge_vibe(self, trigger_word: str, k: int = 3, cortisol: float = 0.0) -> list:
        """True Asymmetric Rank-Cosine Search."""
        Q = _word_to_vector(trigger_word)
        return self.dredge_vibe_by_vector(Q, k, cortisol)


class MemoryCore:
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
        self.current_doorway_zone = None

    def execute_doorway_flush(self, new_zone: str):
        if self.current_doorway_zone and self.current_doorway_zone != new_zone:
            self.short_term_buffer.clear()
            self.cortical_stack.clear()
            if self.events:
                self.events.log(f"Doorway crossed into {new_zone}. Working memory flushed.", "MEMORY")
        self.current_doorway_zone = new_zone

    def illuminate(
        self, vector: Dict[str, float], limit: int = 5, cortisol: float = 0.0
    ) -> List[str]:
        if not self.graph:
            return []
        effective_limit = (
            max(1, int(limit * (1.0 - (cortisol * 0.6)))) if cortisol > 0.3 else limit
        )
        positive_cats = {"constructive", "play", "social"}
        dynamic_threshold = 0.5 + (cortisol * 0.4)
        active_dims = {k: v for k, v in vector.items() if v > 0.4}
        if not active_dims and vector:
            top_dim = max(vector, key=vector.__getitem__)
            active_dims = (
                {top_dim: vector[top_dim]} if vector[top_dim] > 0.1 else {"ENT": 0.2}
            )
        active_dim_cats = {
            dim: self.DIMENSION_MAP.get(dim, set()) for dim in active_dims
        }
        scored_memories = []
        ent_vel_boost = (
            active_dims.get("ENT", 0.0) > 0.7 or active_dims.get("VEL", 0.0) > 0.7
        )
        for node, data in self.graph.items():
            resonance_score = 0.0
            node_cats = self.lex.get_categories_for_word(node) if self.lex else set()
            if cortisol > 0.5 and not node_cats.isdisjoint(positive_cats):
                resonance_score -= cortisol * 0.8
            for dim, val in active_dims.items():
                if not node_cats.isdisjoint(active_dim_cats[dim]):
                    resonance_score += val * 1.5
            mass = float(sum(data.get("edges", {}).values()))
            base_mass_score = mass * 0.1
            if ent_vel_boost:
                resonance_score = (resonance_score + base_mass_score) * (
                    1.0 + (mass * 0.5)
                )
            else:
                resonance_score += base_mass_score
            if resonance_score > dynamic_threshold:
                scored_memories.append((resonance_score, node, data))
        top_memories = heapq.nlargest(
            effective_limit, scored_memories, key=lambda x: x[0]
        )
        results = []
        res_prefix = ux("spore_strings", "core_illuminate_resonant") or "Resonant"
        assoc_prefix = ux("spore_strings", "core_illuminate_associated") or "Associated"
        fmt = (
            ux("spore_strings", "core_illuminate_format")
            or "{prefix} Engram: '{name}'{conn_str}"
        )
        for score, name, data in top_memories:
            connections = list(data.get("edges", {}).keys())
            if not data.get("is_diamond", False):
                data["edges"] = {
                    k: (
                        v
                        if self.graph.get(k, {}).get("is_diamond", False)
                        else v * 0.95
                    )
                    for k, v in data.get("edges", {}).items()
                }
            is_resonant = score > dynamic_threshold
            current_prefix = res_prefix if is_resonant else assoc_prefix
            connection_string = (
                f" -> [{', '.join(connections[:2])}]" if connections else ""
            )
            results.append(
                fmt.format(
                    prefix=current_prefix, name=name.upper(), conn_str=connection_string
                )
            )
        survivors = [
            name for score, name, data in top_memories if score > dynamic_threshold
        ]
        if len(survivors) > 1:
            for node_a, node_b in itertools.combinations(survivors, 2):
                self.graph[node_a].setdefault("edges", {})
                self.graph[node_b].setdefault("edges", {})
                current_a_to_b = self.graph[node_a]["edges"].get(node_b, 0.0)
                self.graph[node_a]["edges"][node_b] = min(10.0, current_a_to_b + 0.5)
                current_b_to_a = self.graph[node_b]["edges"].get(node_a, 0.0)
                self.graph[node_b]["edges"][node_a] = min(10.0, current_b_to_a + 0.5)
        if len(survivors) >= 2:
            self.hallucinate_from_subconscious(survivors, cortisol)
        return results

    def hallucinate_from_subconscious(
        self, active_nodes: List[str], cortisol: float = 0.0
    ):
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
        recovered = self.subconscious.dredge_vibe_by_vector(
            centroid_vector, k=1, cortisol=cortisol
        )
        if recovered:
            phantom_word = recovered[0]["word"]
            if phantom_word not in self.graph:
                self.graph[phantom_word] = {"edges": {}, "is_diamond": False}
            for node in active_nodes:
                w_out = self.graph[node].setdefault("edges", {}).get(phantom_word, 0.0)
                self.graph[node]["edges"][phantom_word] = min(10.0, w_out + 0.5)
                w_in = self.graph[phantom_word].setdefault("edges", {}).get(node, 0.0)
                self.graph[phantom_word]["edges"][node] = min(10.0, w_in + 0.5)

    def forge_diamond(self, node_a, node_b):
        """Permanently crystallizes a high-resonance vector collision."""
        if node_a in self.graph and node_b in self.graph:
            self.graph[node_a].setdefault("diamond_edges", set()).add(node_b)
            self.graph[node_b].setdefault("diamond_edges", set()).add(node_a)
            self.graph[node_a]["is_diamond"] = True
            self.graph[node_b]["is_diamond"] = True
            return True
        return False

    def calculate_mass(self, node):
        if node not in self.graph:
            return 0.0
        return float(sum(self.graph[node]["edges"].values()))

    def strengthen_link(self, source, target, rate, decay):
        if source not in self.graph:
            return
        edges = self.graph[source]["edges"]
        current_weight = edges.get(target, 0.0)
        edges[target] = min(
            10.0, current_weight + rate * (1.0 - current_weight * decay)
        )

    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
        pruned_count = total_decayed = 0
        dead_nodes = set()
        for node in list(self.graph.keys()):
            edges = self.graph[node]["edges"]
            new_edges = {}
            diamond_edges = self.graph[node].get("diamond_edges", set())
            for t, w in edges.items():
                if t in diamond_edges:
                    new_edges[t] = w
                    continue
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
        return ux_format(
            "spore_strings",
            "core_pruned",
            default="",
            total=total_decayed,
            pruned=pruned_count,
        )

    def cannibalize(
        self, current_tick, preserve_current=None
    ) -> Tuple[Optional[str], str]:
        protected = set(self.cortical_stack)
        if preserve_current:
            protected.update(preserve_current) if isinstance(
                preserve_current, list
            ) else protected.add(preserve_current)
        victim, min_data, min_score = None, None, float("inf")
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
        lifespan = current_tick - (data.get("strata") or {}).get(
            "birth_tick", current_tick
        )
        cortex_cfg = safe_get(self.cfg, "CORTEX", {})
        shadow_mass_threshold = float(
            safe_get(cortex_cfg, "SHADOW_MASS_THRESHOLD", 25.0)
        )
        fossil_data = {
            "word": victim,
            "mass": round(mass, 2),
            "lifespan": lifespan,
            "edges": data["edges"],
            "death_tick": current_tick,
        }
        if mass >= shadow_mass_threshold:
            if self.events:
                self.events.publish(
                    "GHOST_SIGNAL",
                    {
                        "concept": victim,
                        "mass": round(mass, 2),
                        "lifespan": lifespan,
                        "links": list(data["edges"].keys()),
                        "coords": {
                            "kappa": min(1.0, mass / 50.0),
                            "gamma": 0.8,
                            "mu": 0.5,
                        },
                    },
                )
        else:
            self.subconscious.bury(fossil_data, config_ref=self.cfg)
            if self.events:
                self.events.publish("MEMORY_BURIED", {"fossil": fossil_data})
        del self.graph[victim]
        for node_data in self.graph.values():
            node_data["edges"].pop(victim, None)
        msg = ux("spore_strings", "core_repressed") or "Core Repressed"
        return victim, msg.format(
            victim=victim, score=score
        ) if msg else "Memory Consumed"
