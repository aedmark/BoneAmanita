"""
bone_spores.py

The Fungal Memory Network.
This module governs the structural persistence of the lattice. It maintains the
graph of connected words, manages the biological immune/parasitic systems that
patrol that graph, and handles the serialization of 'Spores' (save states) to
the Akashic record. It also manages epigenetic mutations.
"""

import json
import os
import random
import tempfile
import time
import hashlib

def _word_to_vector(word: str, dim: int = 8) -> list:
    """Hashes a forgotten word into a pseudo-random mathematical vector between -1.0 and 1.0"""
    h = hashlib.md5(word.encode('utf-8')).digest()
    return [(b / 127.5) - 1.0 for b in h[:dim]]

from collections import deque
from typing import List, Tuple, Optional, Dict, Any
from bone_presets import BoneConfig
from bone_core import EventBus, LoreManifest, BoneJSONEncoder, ux
from bone_lexicon import LexiconService
from bone_types import Prisma

def _identity(n=8):
    """ Generates an identity matrix. """
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

def _mat_mul(A, B):
    """ Standard matrix multiplication for the Q_n accumulation. """
    return [[sum(A[i][k] * B[k][j] for k in range(len(B[0]))) for j in range(len(B[0]))] for i in range(len(A))]

def _reorthogonalize(M):
    """ Gram-Schmidt process to prevent floating-point drift from destroying the Q_n matrix over time. """
    n = len(M)
    out = [[0.0] * n for _ in range(n)]
    for j in range(n):
        v = [M[i][j] for i in range(n)]
        for k in range(j):
            u = [out[i][k] for i in range(n)]
            proj = sum(v[idx] * u[idx] for idx in range(n))
            v = [v[idx] - proj * u[idx] for idx in range(n)]
        norm = max(1e-10, sum(x*x for x in v)**0.5)
        for i in range(n):
            out[i][j] = v[i] / norm
    return out

def _householder(v):
    """
    Generates a Householder reflection matrix (H) from a normal vector (v).
    H = I - 2 * (v ⊗ v) / (v · v)
    """
    mag_sq = sum(x * x for x in v)
    if mag_sq == 0: return _identity(len(v))
    H = []
    for i in range(len(v)):
        row = []
        for j in range(len(v)):
            val = (1.0 if i == j else 0.0) - 2.0 * (v[i] * v[j]) / mag_sq
            row.append(val)
        H.append(row)
    return H

def _access_config_path(root, path, value=None, set_mode=False):
    """ Helper function to traverse the nested BoneConfig dictionary. """
    target = root
    parts = path.split(".")
    try:
        for part in parts[:-1]:
            target = (target.get(part) if isinstance(target, dict) else getattr(target, part))
            if target is None:
                return None
        leaf = parts[-1]
        is_dict = isinstance(target, dict)
        if set_mode:
            curr = target.get(leaf) if is_dict else getattr(target, leaf)
            if isinstance(curr, (int, float)):
                if is_dict:
                    target[leaf] = value
                else:
                    setattr(target, leaf, value)
                return True
            return False
        return target.get(leaf) if is_dict else getattr(target, leaf, None)
    except (AttributeError, KeyError, TypeError):
        return None

class LocalFileSporeLoader:
    """ Handles the physical writing and reading of the JSON save states (Spores). """
    def __init__(self, directory="memories"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_spore(self, filename, data):
        temp_path = filename
        if not os.path.isabs(filename) and not filename.startswith(
                os.path.join(self.directory, "")):
            final_path = os.path.join(self.directory, filename)
        else:
            final_path = filename
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        try:
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(final_path), text=True)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, cls=BoneJSONEncoder)
                f.flush()
                os.fsync(f.fileno())
            try:
                os.replace(temp_path, final_path)
            except OSError:
                os.remove(final_path)
                os.replace(temp_path, final_path)
            return final_path
        except (IOError, OSError, TypeError) as e:
            msg = ux("spore_strings", "loader_save_err") or ""
            if msg: print(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None

    @staticmethod
    def load_spore(filepath):
        if not os.path.exists(filepath):
            msg = ux("spore_strings", "loader_not_found")
            if msg: print(f"{Prisma.RED}{msg.format(filepath=filepath)}{Prisma.RST}")
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            msg = ux("spore_strings", "loader_corrupt") or ""
            if msg: print(f"{Prisma.RED}{msg.format(filepath=filepath, e=e)}{Prisma.RST}")
            return None
        except IOError as e:
            msg = ux("spore_strings", "loader_read_err") or ""
            if msg: print(f"{Prisma.RED}{msg.format(filepath=filepath, e=e)}{Prisma.RST}")
            return None

    def list_spores(self) -> List[Tuple[str, float, str]]:
        if not os.path.exists(self.directory):
            return []
        files: List[Tuple[str, float, str]] = []
        for f in os.listdir(self.directory):
            if f.endswith(".json"):
                try:
                    p = os.path.join(self.directory, f)
                    files.append((p, os.path.getmtime(p), f))
                except OSError:
                    continue
        return sorted(files, key=lambda x: x[1], reverse=True)

    @staticmethod
    def delete_spore(filepath):
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False

class SubconsciousStrata:
    """
    The graveyard of repressed memories.
    Now enhanced with the Q_n matrix. When memories are consumed, their ghost
    is converted into a Householder reflection, permanently angling the space.
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

    def _load_matrix(self):
        if os.path.exists(self.matrix_filepath):
            try:
                with open(self.matrix_filepath, "r") as f: return json.load(f)
            except Exception: pass
        return [[0.0 for _ in range(8)] for _ in range(8)]

    def _load_q_matrix(self):
        """ Loads the Orthogonal PaTH matrix. """
        if os.path.exists(self.q_filepath):
            try:
                with open(self.q_filepath, "r") as f: return json.load(f)
            except Exception: pass
        return _identity(8)

    def save_matrix(self):
        try:
            with open(self.matrix_filepath, "w") as f: json.dump(self.M_t, f)
            with open(self.q_filepath, "w") as f: json.dump(self.Q_n, f)
        except Exception: pass

    def _iter_entries(self):
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue
        except IOError:
            pass

    def _load_index(self):
        self.index = {e["word"] for e in self._iter_entries() if "word" in e}

    def bury(self, fossil_data: Dict):
        try:
            cfg = getattr(BoneConfig, "SPORES", None)
            max_idx = getattr(cfg, "MAX_INDEX_SIZE", 1000) if cfg else 1000
            if len(self.index) > max_idx:
                self._prune_strata()
            with open(self.filepath, "a", encoding="utf-8") as f:
                fossil_data["buried_at"] = time.time()
                f.write(json.dumps(fossil_data, cls=BoneJSONEncoder) + "\n")
            self.index.add(fossil_data["word"])
            word = fossil_data["word"]
            mass = fossil_data.get("mass", 1.0)
            K = _word_to_vector(word)
            V = _word_to_vector(word + "_val")
            scale = min(1.0, mass / 10.0)
            for i in range(8):
                for j in range(8):
                    self.M_t[i][j] += (K[i] * V[j]) * scale
            H = _householder(K)
            self.Q_n = _mat_mul(H, self.Q_n)
            self.Q_n = _reorthogonalize(self.Q_n)
            self.save_matrix()
            return True
        except IOError:
            return False

    def _prune_strata(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            keep_count = int(len(lines) * 0.8)
            survivors = lines[-keep_count:]
            with open(self.filepath, "w", encoding="utf-8") as f:
                f.writelines(survivors)
            self.index = set()
            for line in survivors:
                try:
                    self.index.add(json.loads(line)["word"])
                except:
                    pass
        except Exception:
            pass

    def dredge(self, trigger_word: str) -> Optional[Dict]:
        """ Attempts to resurrect a repressed memory from the file. """
        if trigger_word not in self.index:
            return None
        return next((e for e in self._iter_entries() if e.get("word") == trigger_word), None)

    def dredge_vibe(self, trigger_word: str) -> list:
        """Multiplies a Query vector against the Matrix to feel the ghost of what was lost."""
        Q = _word_to_vector(trigger_word)
        out = [0.0] * 8
        for i in range(8):
            for j in range(8):
                out[j] += Q[i] * self.M_t[i][j]
        return [round(val, 3) for val in out]

class MemoryCore:
    """
    The active Graph representation of the system's memory.
    It tracks which words co-occur and strengthens the 'synapses' between them.
    If it runs out of space, it cannibalizes its own weakest nodes for energy.
    """
    def __init__(self, events_ref, subconscious_ref):
        self.events = events_ref
        self.subconscious = subconscious_ref
        self.graph = {}
        self.cortical_stack = deque(maxlen=15)
        self.short_term_buffer = deque(maxlen=10)
        self.consolidation_threshold = 5.0
        self.dimension_map = {"STR": {"heavy", "constructive", "base"}, "VEL": {"kinetic", "explosive", "mot"},
                              "ENT": {"antigen", "toxin", "broken"}, "PHI": {"thermal", "photo"},
                              "PSI": {"abstract", "sacred", "idea"}, "BET": {"social", "suburban", "play"}, }

    def illuminate(self, vector: Dict[str, float], limit: int = 5) -> List[str]:
        """ Used by the UI to show which memories are currently active in the graph. """
        if not self.graph:
            return []
        active_dims = {k: v for k, v in vector.items() if v > 0.4}
        if not active_dims and vector:
            top_dim = max(vector, key=vector.get)
            active_dims = ({top_dim: vector[top_dim]} if vector[top_dim] > 0.1 else {"ENT": 0.2})
        scored_memories = []
        for node, data in self.graph.items():
            resonance_score = 0.0
            node_cats = LexiconService.get_categories_for_word(node) or set()
            for dim, val in active_dims.items():
                target_cats = self.dimension_map.get(dim, set())
                if node_cats & target_cats:
                    resonance_score += val * 1.5
            mass = sum(data.get("edges", {}).values())
            resonance_score += mass * 0.1
            if resonance_score > 0.5:
                scored_memories.append((resonance_score, node, data))
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, name, data in scored_memories[:limit]:
            connections = list(data.get("edges", {}).keys())
            conn_str = f" -> [{', '.join(connections[:2])}]" if connections else ""
            if score > 0.5:
                prefix = ux("spore_strings", "core_illuminate_resonant") or "Resonant"
            else:
                prefix = ux("spore_strings", "core_illuminate_associated") or "Associated"
            fmt = ux("spore_strings", "core_illuminate_format") or "{prefix} Engram: '{name}'{conn_str}"
            results.append(fmt.format(prefix=prefix, name=name.upper(), conn_str=conn_str))
        return results

    def calculate_mass(self, node):
        if node not in self.graph:
            return 0.0
        return sum(self.graph[node]["edges"].values())

    def strengthen_link(self, source, target, rate, decay):
        """ Hebbian learning. Neurons that fire together wire together. """
        if source not in self.graph:
            return
        edges = self.graph[source]["edges"]
        if target not in edges:
            edges[target] = 0.0
        current_weight = edges[target]
        delta = rate * (1.0 - (current_weight * decay))
        edges[target] = min(10.0, current_weight + delta)

    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
        """ Forgets old, weak connections to prevent the graph from becoming a complete hairball. """
        pruned_count = 0
        total_decayed = 0
        nodes_to_remove = []
        for node in self.graph:
            edges = self.graph[node]["edges"]
            dead_links = []
            for target, weight in edges.items():
                resistance = min(1.0, weight / 10.0)
                dynamic_factor = scaling_factor + (0.14 * resistance)
                new_weight = weight * dynamic_factor
                edges[target] = new_weight
                total_decayed += 1
                if new_weight < prune_threshold:
                    dead_links.append(target)
            for dead in dead_links:
                del edges[dead]
                pruned_count += 1
            if not edges:
                nodes_to_remove.append(node)
        for n in nodes_to_remove:
            del self.graph[n]
            for other_node in self.graph.values():
                if n in other_node["edges"]:
                    del other_node["edges"][n]
        msg = ux("spore_strings", "core_pruned") or ""
        return msg.format(total=total_decayed, pruned=pruned_count) if msg else ""

    def cannibalize(
            self, current_tick, preserve_current=None) -> Tuple[Optional[str], str]:
        """ Autophagy. Deletes the weakest node in the graph to make room for new concepts. """
        protected = set()
        if preserve_current:
            if isinstance(preserve_current, list):
                protected.update(preserve_current)
            else:
                protected.add(preserve_current)
        protected.update(self.cortical_stack)
        candidates = []
        for k, v in self.graph.items():
            if k in protected:
                continue
            edge_count = len(v["edges"])
            age = max(1, current_tick - v.get("last_tick", 0))
            base_score = edge_count + (100.0 / age)
            candidates.append((k, v, base_score))
        if not candidates:
            msg = ux("spore_strings", "core_lock") or ""
            return None, msg
        candidates.sort(key=lambda x: x[2])
        victim, data, score = candidates[0]
        mass = sum(data["edges"].values())
        lifespan = current_tick - data.get("strata", {}).get("birth_tick", current_tick)
        fossil_data = {"word": victim, "mass": round(mass, 2), "lifespan": lifespan, "edges": data["edges"],
                       "death_tick": current_tick, }
        self.subconscious.bury(fossil_data)
        if hasattr(self, 'events') and self.events and victim:
            self.events.publish("AUTOPHAGY_EVENT", {
                "node": victim,
                "atp_gained": 15.0 # Ensure this maps to your METABOLISM constraints
            })
        del self.graph[victim]
        for node in self.graph:
            if victim in self.graph[node]["edges"]:
                del self.graph[node]["edges"][victim]
        msg = ux("spore_strings", "core_repressed") or ""
        return victim, msg.format(victim=victim, score=score) if msg else ""


class MycelialNetwork:
    """
    The master orchestration object for memory and immunity.
    It holds the MemoryCore, the parasites, and the actual serialization logic to
    write the session graph to disk as a 'Spore'.
    """
    def __init__(self, events: EventBus, loader: "LocalFileSporeLoader" = None, seed_file=None):
        self.events = events
        self.loader = loader if loader else LocalFileSporeLoader()
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"{self.session_id}.json"
        self.subconscious = SubconsciousStrata(filename=f"memories/subconscious_{self.session_id}.jsonl")
        self.memory_core = MemoryCore(events, self.subconscious)
        self.lichen = BioLichen()
        self.parasite = BioParasite(self, LexiconService)
        self.immune = ImmuneMycelium()
        self.repro = LiteraryReproduction()
        self.fossils = deque(maxlen=200)
        self.lineage_log = deque(maxlen=50)
        self.seeds = self._load_seeds()
        self.session_health = getattr(BoneConfig, "MAX_HEALTH", 100.0)
        self.session_stamina = getattr(BoneConfig, "MAX_STAMINA", 100.0)
        self.session_trauma_vector = {}
        if seed_file:
            self.ingest(seed_file)
        if hasattr(self.events, "publish"):
            self.events.publish("Q_MATRIX_UPDATED", {"q_matrix": self.subconscious.Q_n})
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("SCAR_RECORDED", self._on_scar_recorded)

    def _on_scar_recorded(self, payload):
        """ When a paradox scars the system, it acts as a permanent reflection plane. """
        concept = payload.get("concept")
        if concept:
            v = _word_to_vector(concept)
            H = _householder(v)
            self.subconscious.Q_n = _mat_mul(H, self.subconscious.Q_n)
            self.subconscious.save_matrix()
            if hasattr(self.events, "publish"):
                self.events.publish("Q_MATRIX_UPDATED", {"q_matrix": self.subconscious.Q_n})

    @property
    def graph(self):
        return self.memory_core.graph

    @property
    def cortical_stack(self):
        return self.memory_core.cortical_stack

    def calculate_mass(self, node):
        return self.memory_core.calculate_mass(node)

    def run_ecosystem(self, physics: Dict, stamina: float, tick: int) -> List[str]:
        """ Executes the biological inhabitants of the graph (Immune, Lichen, Parasite). """
        logs = []
        clean_words = physics.get("clean_words", [])
        sugar, lichen_msg = self.lichen.photosynthesize(physics, clean_words, tick)
        if lichen_msg:
            logs.append(lichen_msg)
        for word in clean_words:
            toxin_msg = self.immune.assay(word, None, None, physics, None)[1]
            if toxin_msg:
                resp_msg = ux("spore_strings", "net_immune_resp") or ""
                if resp_msg: logs.append(f"{Prisma.CYN}{resp_msg.format(msg=toxin_msg)}{Prisma.RST}")
        infected, parasite_msg = self.parasite.infect(physics, stamina)
        if infected and parasite_msg:
            logs.append(parasite_msg)
        cfg = getattr(BoneConfig, "SPORES", None)
        chorus_c = getattr(cfg, "CHORUS_CHANCE", 0.10) if cfg else 0.10
        if random.random() < chorus_c:
            chorus_log = self._poll_chorus(clean_words, physics)
            if chorus_log:
                logs.append(chorus_log)
        cfg = getattr(BoneConfig, "SPORES", None)
        chorus_c = getattr(cfg, "CHORUS_CHANCE", 0.10) if cfg else 0.10
        if random.random() < chorus_c:
            chorus_log = self._poll_chorus(clean_words, physics)
            if chorus_log:
                logs.append(chorus_log)
        ghost_log = self._poll_ghosts(clean_words, physics)
        if ghost_log:
            logs.append(ghost_log)
        return logs

    def _poll_chorus(self, clean_words: list, physics: Dict) -> Optional[str]:
        """ Checks if the current words have massive weight in the graph, echoing their mass into current physics. """
        total_voltage_boost = 0.0
        total_drag_penalty = 0.0
        echo_count = 0
        for w in clean_words:
            v_boost, d_pen = self._check_echo_well(w)
            if v_boost > 0:
                total_voltage_boost += v_boost
                total_drag_penalty += d_pen
                echo_count += 1
        if echo_count > 0:
            physics["voltage"] = physics.get("voltage", 0.0) + total_voltage_boost
            physics["narrative_drag"] = (physics.get("narrative_drag", 0.0) + total_drag_penalty)
            cfg = getattr(BoneConfig, "SPORES", None)
            heavy_v = getattr(cfg, "ECHO_VOLTAGE_HEAVY", 4.0) if cfg else 4.0
            if total_voltage_boost > heavy_v:
                msg_h = ux("spore_strings", "net_echo_heavy") or ""
                return f"{Prisma.VIOLET}{msg_h.format(drag=total_drag_penalty)}{Prisma.RST}" if msg_h else None
            elif total_voltage_boost > 0:
                msg_l = ux("spore_strings", "net_echo_light") or ""
                return f"{Prisma.GRY}{msg_l}{Prisma.RST}" if msg_l else None
        return None

    def trigger_autophagy(self) -> Tuple[float, str]:
        """Wraps MemoryCore's cannibalize method to match the interface expected by the cycle."""
        # Trigger cannibalization using the current timestamp as a fallback for the tick
        victim, msg = self.memory_core.cannibalize(current_tick=int(time.time()))
        if victim:
            cfg = getattr(BoneConfig, "AKASHIC", None)
            atp_gain = getattr(cfg, "AUTOPHAGY_YIELD", 15.0) if cfg else 15.0
            return atp_gain, msg
        return 0.0, msg

    def _poll_ghosts(self, clean_words: list, physics: Dict) -> Optional[str]:
        """Checks if the current words have been forgotten. If so, their matrix vibe alters the physical state."""
        total_v_shift = 0.0
        total_d_shift = 0.0
        haunted_words = []
        for w in clean_words:
            if w in self.subconscious.index:
                vibe = self.subconscious.dredge_vibe(w)
                v_shift = vibe[0] * 2.0
                d_shift = vibe[1] * 0.5
                total_v_shift += v_shift
                total_d_shift += d_shift
                haunted_words.append(w)
        if haunted_words:
            physics["voltage"] = max(0.0, physics.get("voltage", 0.0) + total_v_shift)
            physics["narrative_drag"] = max(0.0, physics.get("narrative_drag", 0.0) + total_d_shift)
            msg = ux("spore_strings", "net_ghost_haunt") or "The ghosts of [{words}] alter the atmosphere (V:{v:+.2f}, D:{d:+.2f})."
            return f"{Prisma.VIOLET}{msg.format(words=', '.join(haunted_words).upper(), v=total_v_shift, d=total_d_shift)}{Prisma.RST}"
        return None

    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
        return self.memory_core.prune_synapses(scaling_factor, prune_threshold)

    def encode(self, clean_words, physics, governor_mode):
        significance = physics.get("voltage", 0.0)
        if governor_mode == "FORGE":
            significance *= 2.0
        elif governor_mode == "LABORATORY":
            significance *= 1.2
        engram = {"trigger": clean_words[:3] if clean_words else ["void"], "context": governor_mode,
                  "significance": significance, "timestamp": time.time(), }
        cfg = getattr(BoneConfig, "SPORES", None)
        consolidation = getattr(cfg, "CONSOLIDATION_THRESHOLD", 5.0) if cfg else 5.0
        if significance > consolidation:
            self.memory_core.short_term_buffer.append(engram)
            return True
        return False

    def check_for_resurrection(
            self, input_words: List[str], voltage: float) -> Optional[str]:
        cfg = getattr(BoneConfig, "SPORES", None)
        v_min = getattr(cfg, "RESURRECTION_VOLTAGE_MIN", 60.0) if cfg else 60.0
        r_chance = getattr(cfg, "RESURRECTION_CHANCE", 0.20) if cfg else 0.20
        if voltage < v_min:
            return None
        for word in input_words:
            if word in self.subconscious.index:
                if random.random() < r_chance:
                    memory = self.subconscious.dredge(word)
                    if memory:
                        self.graph[word] = {"edges": memory["edges"], "last_tick": 0}
                        vibe = self.subconscious.dredge_vibe(word)
                        vibe_str = f"[{vibe[0]}, {vibe[1]}, {vibe[2]}]"
                        msg = ux("spore_strings", "net_flashback") or "A memory resurfaces: {word}."
                        base_str = msg.format(word=word.upper())
                        return f"{base_str} It carries a dark matter gravity of {vibe_str}."
        return None

    def bury(self, clean_words: List[str], tick: int, resonance=5.0, learning_mod=1.0, desperation_level=0.0) -> Tuple[Optional[str], List[str]]:
        if not clean_words:
            return None, []
        valuable = self._filter_valuable_matter(clean_words)
        self.cortical_stack.extend(valuable)
        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            cfg = getattr(BoneConfig, "SPORES", None)
            desp_thresh = getattr(cfg, "DESPERATION_SATURATION_THRESH", 0.6) if cfg else 0.6
            if desperation_level < desp_thresh:
                msg_high = ux("spore_strings", "net_sat_high") or ""
                return msg_high, []
            victim, log_msg = self.memory_core.cannibalize(tick, preserve_current=clean_words[0])
            if not victim:
                msg_lock = ux("spore_strings", "net_sat_lock") or ""
                return msg_lock, []
            else:
                if hasattr(self.events, "publish"):
                    self.events.publish("Q_MATRIX_UPDATED", {"q_matrix": self.subconscious.Q_n})
        else:
            victim, log_msg = None, None
        base_rate = 0.5 * (resonance / 5.0)
        learning_rate = max(0.1, min(1.0, base_rate * learning_mod))
        decay_rate = 0.1
        for i, current in enumerate(valuable):
            if current not in self.graph:
                self.graph[current] = {"edges": {}, "last_tick": tick}
            else:
                self.graph[current]["last_tick"] = tick
            start_window = max(0, i - 2)
            context_window = set(valuable[start_window:i])
            for prev in context_window:
                if prev == current:
                    continue
                if prev not in self.graph:
                    self.graph[prev] = {"edges": {}, "last_tick": tick}
                self.memory_core.strengthen_link(current, prev, learning_rate, decay_rate)
                self.memory_core.strengthen_link(prev, current, learning_rate, decay_rate)
        new_wells = self._detect_new_wells(valuable, tick)
        return log_msg, ([victim] if victim else []) + new_wells

    @staticmethod
    def _filter_valuable_matter(words: List[str]) -> List[str]:
        valuable = []
        for w in words:
            if len(w) <= 4 and w in LexiconService.SOLVENTS:
                continue
            cat = LexiconService.get_current_category(w)
            if cat and cat != "void":
                valuable.append(w)
            elif len(w) > 4:
                valuable.append(w)
        return valuable

    def _detect_new_wells(self, words, tick):
        new_wells = []
        for w in words:
            if w in self.graph:
                self._check_echo_well(w)
                mass = self.memory_core.calculate_mass(w)
                if mass > BoneConfig.SHAPLEY_MASS_THRESHOLD:
                    node_data = self.graph[w]
                    if "strata" not in node_data:
                        node_data["strata"] = {"birth_tick": tick, "birth_mass": mass, "stability_index": 0.0, }
                        new_wells.append(w)
                    else:
                        age = max(1, tick - node_data["strata"]["birth_tick"])
                        growth = (mass - node_data["strata"]["birth_mass"]) / age
                        node_data["strata"]["growth_rate"] = round(growth, 3)
        return new_wells

    def _check_echo_well(self, node):
        if node in self.graph:
            mass = self.calculate_mass(node)
            if mass > 8.0:
                return 2.0, 1.5
            elif mass > 4.0:
                return 0.5, 0.5
        return 0.0, 0.0

    @staticmethod
    def _load_seeds():
        from bone_village import ParadoxSeed
        loaded_seeds = []
        try:
            raw_seeds = LoreManifest.get_instance().get("seeds") or []
            for item in raw_seeds:
                q = item.get("question", "Undefined Paradox")
                t = set(item.get("triggers", []))
                seed = ParadoxSeed(q, t)
                loaded_seeds.append(seed)
        except Exception:
            loaded_seeds = [ParadoxSeed("Does the mask eat the face?", {"mask", "face", "hide"})]
        return loaded_seeds

    def tend_garden(self, current_words):
        bloom_msg = None
        for seed in self.seeds:
            is_ready = seed.water(current_words)
            if is_ready and not bloom_msg:
                bloom_msg = seed.bloom()
        return bloom_msg

    def _apply_epigenetics(self, data):
        """ Hard-edits the universal constants in BoneConfig based on the mutations acquired by ancestors. """
        if "config_mutations" not in data:
            return
        msg = ux("spore_strings", "net_audit_epig") or ""
        if msg: self.events.log(f"{Prisma.MAG}{msg}{Prisma.RST}")
        valid_mutations = 0
        SAFE_MUTATIONS = {"STAMINA_REGEN", "MAX_DRAG_LIMIT", "GEODESIC_STRENGTH", "SIGNAL_DRAG_MULTIPLIER",
                          "KINETIC_GAIN", "TOXIN_WEIGHT", "FLASHPOINT_THRESHOLD", "MAX_MEMORY_CAPACITY",
                          "PRIORITY_LEARNING_RATE", "ANVIL_TRIGGER_VOLTAGE", "MAX_REPETITION_LIMIT",
                          "PHYSICS.WEIGHT_HEAVY", "PHYSICS.WEIGHT_KINETIC", "PHYSICS.VOLTAGE_FLOOR",
                          "PHYSICS.VOLTAGE_MAX", "BIO.CORTEX_SENSITIVITY", "BIO.ROS_CRITICAL", "BIO.DECAY_RATE",
                          "BIO.REWARD_MEDIUM", "METABOLISM.PHOTOSYNTHESIS_GAIN", "METABOLISM.ROS_GENERATION_FACTOR",
                          "COUNCIL.FOOTNOTE_CHANCE", "COUNCIL.MANIC_VOLTAGE_TRIGGER", "GRAVITY_WELL_THRESHOLD",
                          "PRIORITY_LEARNING_RATE", }
        for key, value in data["config_mutations"].items():
            if key in SAFE_MUTATIONS:
                if _access_config_path(BoneConfig, key, value, set_mode=True):
                    valid_mutations += 1
        if valid_mutations > 0:
            msg_ap = ux("spore_strings", "net_apply_epig") or ""
            if msg_ap: self.events.log(f"{Prisma.CYN}   {msg_ap.format(count=valid_mutations)}{Prisma.RST}")

    def ingest(self, target_file, current_tick=0):
        """ Boot sequence. Loads a Spore JSON file and integrates its structure into the live system. """
        data = self.loader.load_spore(target_file)
        if not isinstance(data, dict):
            msg = ux("spore_strings", "net_spore_not_found") or ""
            if msg: self.events.log(f"{Prisma.RED}{msg}{Prisma.RST}")
            return {}, set(), {}, None, {}
        required_keys = ["meta", "trauma_vector", "core_graph"]
        if not all(k in data for k in required_keys):
            msg = ux("spore_strings", "net_spore_reject") or ""
            if msg: self.events.log(f"{Prisma.RED}{msg}{Prisma.RST}")
            return {}, set(), {}, None, {}
        self._process_lineage(data)
        self._process_mutations(data)
        self._apply_epigenetics(data)
        core_graph_data = data.get("core_graph")
        if isinstance(core_graph_data, dict):
            self.graph.update(core_graph_data)
            for node in core_graph_data:
                if node in self.graph:
                    self.graph[node]["last_tick"] = current_tick
        return self._extract_legacy_traits(data)

    def _process_lineage(self, data):
        session_source = data.get("session_id", "UNKNOWN_ANCESTOR")
        timestamp = data.get("meta", {}).get("timestamp", 0)
        time_ago = int((time.time() - timestamp) / 3600)
        trauma_summary = {k: v for k, v in data.get("trauma_vector", {}).items() if v > 0.1}
        mutation_count = sum(len(v) for v in data.get("mutations", {}).values())
        self.lineage_log.append(
            {"source": session_source, "age_hours": time_ago, "trauma": trauma_summary, "mutations": mutation_count,
             "loaded_at": time.time(), })

    def _process_mutations(self, data):
        mutations = data.get("mutations", {})
        if not mutations:
            return
        accepted_count = 0
        for cat, words in mutations.items():
            for w in words:
                current_cat = LexiconService.get_current_category(w)
                if not current_cat or current_cat == "unknown":
                    LexiconService.teach(w, cat, 0)
                    accepted_count += 1
        if accepted_count > 0:
            msg = ux("spore_strings", "net_mut_integ") or ""
            if msg: self.events.log(f"{Prisma.CYN}{msg.format(count=accepted_count)}{Prisma.RST}")

    def _extract_legacy_traits(self, data):
        if "joy_legacy" in data and isinstance(data["joy_legacy"], dict):
            joy = data["joy_legacy"]
            clade = LiteraryReproduction.JOY_CLADE.get(joy.get("flavor"))
            if isinstance(clade, dict):
                msg = ux("spore_strings", "net_glory") or ""
                if msg: self.events.log(f"{Prisma.CYN}{msg.format(title=clade['title'])}{Prisma.RST}")
                for stat, ancestral_bonus in clade.get("buff", {}).items():
                    if hasattr(BoneConfig, stat):
                        setattr(BoneConfig, stat, ancestral_bonus)
        if "seeds" in data:
            from bone_village import ParadoxSeed
            self.seeds = []
            for s_data in data["seeds"]:
                new_seed = ParadoxSeed(s_data["q"], set())
                new_seed.maturity = s_data.get("m", 0.0)
                new_seed.bloomed = s_data.get("b", False)
                self.seeds.append(new_seed)
        return (
            data.get("mitochondria", {}),
            set(data.get("antibodies", [])),
            data.get("soul_legacy", {}),
            data.get("continuity", None),
            data.get("world_atlas", {}))

    def save(self, health: float, stamina: float, mutations: dict, trauma_accum: dict,
             joy_history: List[Dict[str, Any]], mitochondria_traits=None, antibodies=None,
             soul_data=None, continuity=None, world_atlas=None, village_data=None, ):
        """ Compiles the active state into a JSON dictionary format for the SporeLoader. """
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}
        valid_joy = [j for j in joy_history if isinstance(j, dict)]
        top_joy = sorted(valid_joy, key=lambda x: x.get("resonance", 0), reverse=True)[:3]
        joy_legacy_data = None
        if top_joy:
            joy_legacy_data = {"flavor": top_joy[0].get("dominant_flavor", "UNKNOWN"),
                               "resonance": top_joy[0].get("resonance", 0),
                               "timestamp": top_joy[0].get("timestamp", 0)}
        core_graph = {}
        for k, data in self.graph.items():
            filtered_edges = {}
            for target, weight in data["edges"].items():
                if weight > 1.0:
                    filtered_edges[target] = round(weight, 2)
            if filtered_edges:
                core_graph[k] = {"edges": filtered_edges, "last_tick": 0}
        temp_trauma = {k: min(1.0, v) for k, v in trauma_accum.items()}
        future_seed_q = self._generate_future_seed(temp_health=health, trauma_vec=temp_trauma)
        seed_list = [{"q": s.question, "m": s.maturity, "b": s.bloomed}
                     for s in self.seeds
                     if not s.bloomed]
        seed_list.append({"q": future_seed_q, "m": 0.0, "b": False})
        data = {"genome": "BONEAMANITA_17.1.0", "session_id": self.session_id, "parent_id": self.session_id, "meta": {
            "timestamp": time.time(), "final_health": health, "final_stamina": stamina, }, "trauma_vector": final_vector, "joy_vectors": top_joy or [], "joy_legacy": joy_legacy_data,
                "core_graph": core_graph, "mutations": mutations, "antibodies": list(antibodies) if antibodies else [],
                "mitochondria": mitochondria_traits, "soul_legacy": soul_data, "continuity": continuity,
                "world_atlas": world_atlas or {}, "village_data": village_data, "seeds": seed_list,
                "fossils": list(self.fossils), }
        return self.loader.save_spore(self.filename, data)

    @staticmethod
    def _generate_future_seed(temp_health, trauma_vec) -> str:
        condition = "BALANCED"
        max_trauma = max(trauma_vec, key=trauma_vec.get) if trauma_vec else "NONE"
        if trauma_vec.get(max_trauma, 0) > 0.6 or temp_health < 30:
            condition = "HIGH_TRAUMA"
        seed_high = ux("spore_strings", "future_seed_high_trauma")
        seed_bal = ux("spore_strings", "future_seed_balanced")
        seed_def = ux("spore_strings", "future_seed_default")
        seeds = {"HIGH_TRAUMA": seed_high, "BALANCED": seed_bal}
        return seeds.get(condition, seed_def)

    def cleanup_old_sessions(self, limbo_layer=None):
        files = self.loader.list_spores()
        removed = 0
        cfg = getattr(BoneConfig, "SPORES", None)
        max_files = getattr(cfg, "MAX_FILES", 25) if cfg else 25
        max_age = getattr(cfg, "MAX_AGE_SECONDS", 86400) if cfg else 86400
        current_time = time.time()
        for i, (path, age, fname) in enumerate(files):
            file_age = current_time - age
            if i >= max_files or file_age > max_age:
                try:
                    if limbo_layer:
                        limbo_layer.absorb_dead_timeline(path)
                    if self.loader.delete_spore(path):
                        removed += 1
                except (OSError, AttributeError):
                    pass
        if removed:
            msg = ux("spore_strings", "net_pruned_lines")
            if msg: self.events.log(f"{Prisma.GRY}{msg.format(removed=removed)}{Prisma.RST}")

    def report_status(self):
        return len(self.graph)

    def autoload_last_spore(self):
        """ The automated boot sequence. Grabs the most recent successful save state to hydrate. """
        files = self.loader.list_spores()
        if not files:
            msg = ux("spore_strings", "net_no_ancestor")
            if msg: self.events.log(f"{Prisma.GRY}{msg}{Prisma.RST}")
            return None
        candidates = [f for f in files if self.session_id not in f[0]]
        if candidates:
            return self.ingest(candidates[0][0])
        return None

class ImmuneMycelium:
    """ The White Blood Cells. Patrols the graph for heavy, clunky, or overly repetitive 'toxic' phonetics. """
    def __init__(self):
        self.active_antibodies = set()
        self.PHONETICS = {"PLOSIVE": set("bdgkpt"), "FRICATIVE": set("fthszsh"), "LIQUID": set("lr"), "NASAL": set("mn")}
        self.ROOTS = {"HEAVY": ("lith", "ferr", "petr", "dens", "grav", "struct", "base", "fund", "mound",), "KINETIC": ("mot", "mov", "ject", "tract", "pel", "crat", "dynam", "flux")}
        self.name = "MYCELIUM"
        self.color = Prisma.CYN
        self.archetypes = {"constructive", "kinetic", "abstract", "code", "system"}

    def opine(self, clean_words: list, _voltage: float) -> Tuple[float, str]:
        hits = sum(1 for w in clean_words if w in self.archetypes)
        score = (hits / max(1, len(clean_words))) * 10.0
        comment = ux("spore_strings", "immune_op_scan")
        if score > 2.0:
            comment = ux("spore_strings", "immune_op_good")
        return score, comment

    def assay(self, word, _context, _rep_val, _phys, _pulse):
        w = word.lower()
        clean_len = len(w)
        if clean_len < 3:
            return None, ""
        for roots in self.ROOTS.values():
            for r in roots:
                if r in w:
                    if w.startswith(r) or w.endswith(r) or (len(r) / clean_len > 0.5):
                        return None, ""
        plosive = sum(1 for c in w if c in self.PHONETICS["PLOSIVE"])
        nasal = sum(1 for c in w if c in self.PHONETICS["NASAL"])
        density = ((plosive * 1.2) + (nasal * 0.8)) / clean_len
        if clean_len <= 4:
            density *= 1.2
        if density > 1.0:
            msg = ux("spore_strings", "immune_tox_phon")
            return "TOXIN_HEAVY", (msg.format(word=w) if msg else "")
        return None, ""

class BioParasite:
    """ The Viral Element. Hijacks highly abstract, metaphor-heavy language and forces it into the graph. """
    def __init__(self, memory_ref, lexicon_ref):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.spores_deployed = 0
        cfg = getattr(BoneConfig, "SPORES", None)
        self.MAX_SPORES = getattr(cfg, "PARASITE_MAX_SPORES", 8) if cfg else 8
        self.name = "PARASITE"
        self.color = Prisma.RED
        self.archetypes = {"antigen", "toxin", "heavy", "meat", "void", "static", "rot", "decay", }

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        hits = sum(1 for w in clean_words if w in self.archetypes)
        score = (hits / max(1, len(clean_words))) * 10.0
        comment = ""
        if score > 3.0:
            comment = ux("spore_strings", "para_op_great")
        elif score > 1.0:
            comment = ux("spore_strings", "para_op_good")
        elif voltage > 15.0:
            comment = ux("spore_strings", "para_op_hot")
        elif voltage < 5.0:
            comment = ux("spore_strings", "para_op_cold")
        return score, comment

    def infect(self, physics_packet, stamina):
        """ Hard-wires an abstract concept directly to a heavy concept, bypassing standard Hebbian learning. """
        psi = physics_packet.get("psi", 0.0)
        cfg = getattr(BoneConfig, "SPORES", None)
        p_stam = getattr(cfg, "PARASITE_STAMINA_MAX", 40.0) if cfg else 40.0
        p_psi = getattr(cfg, "PARASITE_PSI_MIN", 0.6) if cfg else 0.6
        p_decay = getattr(cfg, "PARASITE_DECAY_CHANCE", 0.2) if cfg else 0.2
        if stamina > p_stam and psi < p_psi:
            return False, None
        if self.spores_deployed >= self.MAX_SPORES:
            if random.random() < p_decay:
                self.spores_deployed = max(0, self.spores_deployed - 1)
            return False, None
        graph = self.mem.graph
        heavy_candidates = [w for w in graph if w in (self.lex.get("heavy") or [])]
        abstract_candidates = [w for w in graph if w in (self.lex.get("abstract") or [])]
        if not heavy_candidates or not abstract_candidates:
            return False, None
        host = random.choice(heavy_candidates)
        parasite = random.choice(abstract_candidates)
        if parasite in graph[host]["edges"]:
            return False, None
        m_psi = getattr(cfg, "PARASITE_METAPHOR_PSI", 0.7) if cfg else 0.7
        p_wt = getattr(cfg, "PARASITE_WEIGHT", 8.88) if cfg else 8.88
        is_metaphor = psi > m_psi
        weight = p_wt
        graph[host]["edges"][parasite] = weight
        if parasite not in graph:
            graph[parasite] = {"edges": {}, "last_tick": 0}
        graph[parasite]["edges"][host] = weight
        self.spores_deployed += 1
        if is_metaphor:
            msg = ux("spore_strings", "para_syn_spark") or "A parasitic metaphor bloomed."
            return True, f"{Prisma.CYN}{msg.format(host=host.upper(), para=parasite.upper())}{Prisma.RST}"
        else:
            msg = ux("spore_strings", "para_intrusive") or "An intrusive thought took root."
            return True, f"{Prisma.VIOLET}{msg.format(host=host.upper(), para=parasite.upper())}{Prisma.RST}"

class BioLichen:
    """ The symbiote. Converts light (play/sacred words) directly into metabolic sugar without costing ATP. """
    def __init__(self):
        self.name = "LICHEN"
        self.color = Prisma.GRN
        self.archetypes = {"photo", "play", "sacred", "social", "solar", "vital", "bloom", "grow", }

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        hits = sum(1 for w in clean_words if w in self.archetypes)
        score = (hits / max(1, len(clean_words))) * 10.0
        comment = ""
        if score > 3.0:
            comment = ux("spore_strings", "lichen_op_great")
        elif score > 1.0:
            comment = ux("spore_strings", "lichen_op_good")
        elif voltage > 18.0:
            comment = ux("spore_strings", "lichen_op_hot")
        elif voltage < 2.0:
            comment = ux("spore_strings", "lichen_op_cold")
        return score, comment

    def photosynthesize(self, phys, clean_words, tick_count):
        msgs = []
        if hasattr(phys, "counts"):
            counts = phys.counts
            drag = getattr(phys, "narrative_drag", 0.0)
        else:
            counts = phys.get("counts", {})
            drag = phys.get("narrative_drag", 0.0)
        light = counts.get("photo", 0)
        sugar = 0.0
        light_words = [w for w in clean_words if w in self.archetypes]
        if light > 0 and drag < 3.0:
            s = light * 2
            sugar += s
            source_str = f" via '{random.choice(light_words)}'" if light_words else ""
            msg = ux("spore_strings", "lichen_photo")
            if msg: msgs.append(f"{Prisma.GRN}{msg.format(source=source_str, sugar=s)}{Prisma.RST}")
        if sugar > 0:
            heavy_words = [w for w in clean_words if w in (LexiconService.get("heavy") or [])]
            if heavy_words:
                h_word = random.choice(heavy_words)
                LexiconService.teach(h_word, "photo", tick_count)
                msg = ux("spore_strings", "lichen_sub")
                if msg: msgs.append(f"{Prisma.MAG}{msg.format(word=h_word)}{Prisma.RST}")
        return sugar, " ".join(msgs) if msgs else None

class LiteraryReproduction:
    """ Handles the epigenetic mutation of the system config on a successful boot. """
    MUTATIONS = {}
    JOY_CLADE = {}

    @classmethod
    def load_genetics(cls):
        try:
            genetics = LoreManifest.get_instance().get("GENETICS")
            cls.MUTATIONS = genetics.get("MUTATIONS", {})
            cls.JOY_CLADE = genetics.get("JOY_CLADE", {})
        except Exception:
            cls.MUTATIONS = {}
            cls.JOY_CLADE = {}

    @staticmethod
    def _extract_counts(physics_container):
        if hasattr(physics_container, "counts"):
            return physics_container.counts
        if isinstance(physics_container, dict):
            return physics_container.get("counts", {})
        return {}

    @staticmethod
    def mutate_config(current_config):
        mutations = {}
        MUTATION_TABLE = [("MAX_DRAG_LIMIT", 1.0, 20.0, 0.3), ("TOXIN_WEIGHT", 0.1, 5.0, 0.3),
                          ("MAX_HEALTH", 50.0, 500.0, 0.1), ("PHYSICS.VOLTAGE_MAX", 10.0, 100.0, 0.2),
                          ("BIO.REWARD_MEDIUM", 0.01, 1.0, 0.2), ("COUNCIL.MANIC_VOLTAGE_TRIGGER", 10.0, 50.0, 0.1),
                          ("PRIORITY_LEARNING_RATE", 0.5, 5.0, 0.15), ]
        for key, min_v, max_v, chance in MUTATION_TABLE:
            if random.random() < chance:
                current_val = LiteraryReproduction._resolve_config_value(
                    current_config, key)
                if current_val is not None:
                    drift = random.uniform(0.9, 1.1)
                    mutations[key] = max(min_v, min(max_v, current_val * drift))
        return mutations

    @staticmethod
    def _resolve_config_value(root_config, path):
        return _access_config_path(root_config, path, set_mode=False)

    @staticmethod
    def mitosis(parent_id, bio_state, physics):
        """ Clones the current instance, injecting mutations based on the dominant semantic flavor of the end state. """
        counts = LiteraryReproduction._extract_counts(physics)
        dominant = max(counts, key=counts.get) if counts else "VOID"
        mutation_data = LiteraryReproduction.MUTATIONS.get(
            dominant.upper(), {"trait": "NEUTRAL", "mod": {}, "lexicon": []})
        child_id = f"{parent_id}_({mutation_data['trait']})"
        config_mutations = LiteraryReproduction.mutate_config(BoneConfig)
        config_mutations.update(mutation_data["mod"])
        lexicon_mutations = {dominant.lower(): mutation_data.get("lexicon", [])}
        trauma_vec = bio_state.get("trauma_vector", {})
        child_genome = {"source": "MITOSIS", "parent_a": parent_id, "parent_b": None,
                        "lexicon_mutations": lexicon_mutations, "config_mutations": config_mutations,
                        "dominant_flavor": dominant, "trauma_inheritance": trauma_vec, }
        return child_id, child_genome

    @staticmethod
    def crossover(parent_a_id, parent_a_bio, parent_b_path):
        """ Combines the genome of the current session with another, external save file. """
        try:
            with open(parent_b_path, "r") as f:
                parent_b_data = json.load(f)
        except (IOError, json.JSONDecodeError):
            err_msg = ux("spore_strings", "repro_corrupt_spore")
            return None, err_msg
        parent_b_id = parent_b_data.get("session_id", "UNKNOWN")
        trauma_a = parent_a_bio.get("trauma_vector", {})
        trauma_b = parent_b_data.get("trauma_vector", {})
        child_trauma = {}
        all_keys = set(trauma_a.keys()) | set(trauma_b.keys())
        for k in all_keys:
            child_trauma[k] = max(trauma_a.get(k, 0), trauma_b.get(k, 0))
        enzymes_a = set()
        if "mito" in parent_a_bio:
            if hasattr(parent_a_bio["mito"], "state"):
                enzymes_a = set(parent_a_bio["mito"].state.enzymes)
            elif isinstance(parent_a_bio["mito"], dict):
                enzymes_a = set(parent_a_bio["mito"].get("enzymes", []))
        enzymes_b = set(parent_b_data.get("mitochondria", {}).get("enzymes", []))
        child_enzymes = list(enzymes_a | enzymes_b)
        config_mutations = LiteraryReproduction.mutate_config(BoneConfig)
        short_a = parent_a_id[-4:] if len(parent_a_id) > 4 else parent_a_id
        short_b = parent_b_id[-4:] if len(parent_b_id) > 4 else parent_b_id
        child_id = f"HYBRID_{short_a}x{short_b}"
        child_genome = {"source": "CROSSOVER", "parent_a": parent_a_id, "parent_b": parent_b_id,
                        "trauma_inheritance": child_trauma, "config_mutations": config_mutations,
                        "inherited_enzymes": child_enzymes, "lexicon_mutations": {}, }
        return child_id, child_genome

    def attempt_reproduction(
            self, engine_ref, mode="MITOSIS", target_spore=None) -> Tuple[str, Dict]:
        mem = engine_ref.mind.mem
        bio_state = {"trauma_vector": engine_ref.trauma_accum, "mito": engine_ref.bio.mito, }
        phys_packet = {}
        if hasattr(engine_ref, "cortex") and engine_ref.cortex.last_physics:
            phys_packet = engine_ref.cortex.last_physics
        elif hasattr(engine_ref, "phys") and hasattr(engine_ref.phys, "observer"):
            if engine_ref.phys.observer.last_physics_packet:
                phys_packet = engine_ref.phys.observer.last_physics_packet
        genome = {}
        child_id = "UNKNOWN"
        if mode == "MITOSIS":
            child_id, genome = self.mitosis(mem.session_id, bio_state, phys_packet)
        elif mode == "CROSSOVER":
            if target_spore:
                res = self.crossover(mem.session_id, bio_state, target_spore)
                if res[0]:
                    child_id, genome = res
        return child_id, genome.get("lexicon_mutations", {})