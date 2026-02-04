""" bone_spores.py - The Mycellium """

import json, math, os, random, time, tempfile
from collections import deque
from typing import List, Tuple, Optional
from bone_lexicon import LiteraryReproduction, TheLexicon
from bone_data import SEEDS
from bone_bus import EventBus, Prisma, BoneConfig
from bone_village import ParadoxSeed, TheAlmanac

class BoneJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, deque):
            return list(obj)
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)

class SporeLoader:
    def __init__(self, directory="memories"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def list_spores(self) -> List[Tuple[str, float, str]]:
        if not os.path.exists(self.directory):
            return []
        files = []
        for f in os.listdir(self.directory):
            if f.endswith(".json"):
                path = os.path.join(self.directory, f)
                try:
                    files.append((path, os.path.getmtime(path), f))
                except OSError:
                    continue
        files.sort(key=lambda x: x[1], reverse=True)
        return files

    def save(self, filename: str, data: dict) -> Optional[str]:
        core_graph = {}
        raw_graph = data.get("graph", {})
        for node, node_data in raw_graph.items():
            filtered_edges = {}
            for target, weight in node_data["edges"].items():
                if weight <= 1.0: continue
                drift = random.uniform(0.9, 1.1)
                new_weight = min(10.0, weight * drift)
                filtered_edges[target] = round(new_weight, 2)
            if filtered_edges:
                core_graph[node] = {
                    "edges": filtered_edges,
                    "last_tick": 0
                }
        payload = {
            "genome": "BONEAMANITA_11.7.0_DYMAXION",
            "session_id": data.get("session_id"),
            "core_graph": core_graph,
            "mutations": data.get("mutations", {}),
            "trauma_vector": data.get("trauma_vector", {}),
            "joy_legacy": data.get("joy_legacy"),
            "soul_legacy": data.get("soul_legacy"),
            "seeds": data.get("seeds", []),
            "fossils": data.get("fossils", []),
            "meta": data.get("meta", {})
        }
        final_path = os.path.join(self.directory, filename) if not os.path.isabs(filename) else filename
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(final_path), text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(payload, f, indent=2, cls=BoneJSONEncoder)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, final_path)
            return final_path
        except (IOError, OSError, TypeError) as e:
            print(f"Error saving spore: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None

    def load(self, filepath: str) -> Optional[dict]:
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None

    def delete(self, filepath: str) -> bool:
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False

class MycelialNetwork:
    def __init__(self, events: EventBus, loader: SporeLoader = None, seed_file=None):
        self.events = events
        self.loader = loader if loader else SporeLoader()
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"{self.session_id}.json"

        self.session_health = None
        self.session_stamina = None
        self.session_trauma_vector = None

        self.graph = {}
        self.cortical_stack = deque(maxlen=15)
        self.short_term_buffer = deque(maxlen=10)
        self.fossils = deque(maxlen=200)
        self.lineage_log = deque(maxlen=50)
        self.consolidation_threshold = 5.0
        self.memory_threshold = 0.5
        self.seeds = self._load_initial_seeds()
        if seed_file:
            self.ingest(seed_file)

    def _load_initial_seeds(self):
        loaded = []
        try:
            for item in SEEDS:
                loaded.append(ParadoxSeed(item["question"], set(item["triggers"])))
            self.events.log(f"{Prisma.GRY}[SYSTEM]: Paradox Seeds loaded ({len(loaded)} active).{Prisma.RST}")
        except Exception as e:
            self.events.log(f"{Prisma.RED}[CRITICAL]: Seed Injection Failed: {e}{Prisma.RST}")
            loaded = [ParadoxSeed("Does the mask eat the face?", {"mask", "face", "hide"})]
        return loaded

    def encode(self, clean_words, physics, governor_mode):
        significance = physics["voltage"]
        if governor_mode == "FORGE": significance *= 2.0
        elif governor_mode == "LABORATORY": significance *= 1.2
        engram = {
            "trigger": clean_words[:3] if clean_words else ["void"],
            "context": governor_mode,
            "voltage": physics["voltage"],
            "significance": significance,
            "timestamp": time.time()
        }
        if significance > self.consolidation_threshold:
            self.short_term_buffer.append(engram)
            return True
        return False

    def bury(self, clean_words: List[str], tick: int, resonance=5.0, learning_mod=1.0) -> Tuple[Optional[str], List[str]]:
        total_len = sum(len(w) for w in clean_words)
        count = max(1, len(clean_words))
        if (total_len / count) < 3.5 and count > 3:
            return "MECHANICAL_STARVATION", []
        valuable_matter = (TheLexicon.get("heavy") | TheLexicon.get("thermal") | TheLexicon.get("cryo") | TheLexicon.get("abstract"))
        filtered = [w for w in clean_words if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)]
        self.cortical_stack.extend(filtered)
        base_rate = 0.5 * (resonance / 5.0)
        learning_rate = max(0.1, min(1.0, base_rate * learning_mod))
        decay_rate = 0.1
        new_wells = []
        for i, current in enumerate(filtered):
            if current not in self.graph:
                if not self._should_absorb(current): continue
                self.graph[current] = {"edges": {}, "last_tick": tick}
            else:
                self.graph[current]["last_tick"] = tick
            start_window = max(0, i - 2)
            context_window = set(filtered[start_window:i])
            for prev in context_window:
                if prev == current: continue
                self._strengthen_bond(current, prev, learning_rate, decay_rate)
                self._strengthen_bond(prev, current, learning_rate, decay_rate)
            if self.calculate_mass(current) > BoneConfig.SHAPLEY_MASS_THRESHOLD:
                if "strata" not in self.graph[current]:
                    self.graph[current]["strata"] = {"birth_tick": tick, "birth_mass": self.calculate_mass(current)}
                    new_wells.append(current)
        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            victim, log_msg = self._cannibalize(current_tick=tick)
            return log_msg, [victim] if victim else []
        return None, new_wells

    def _strengthen_bond(self, source, target, rate, decay):
        if source not in self.graph: return
        if target not in self.graph: return
        edges = self.graph[source]["edges"]
        if target not in edges: edges[target] = 0.0
        current_weight = edges[target]
        delta = rate * (1.0 - (current_weight * decay))
        edges[target] = min(10.0, current_weight + delta)

    def _should_absorb(self, word: str) -> bool:
        gain = len(word) * 0.1
        if word.upper() in TheLexicon.get("heavy"): gain += 0.5
        elif word.upper() in TheLexicon.get("abstract"): gain += 0.4
        return gain > self.memory_threshold

    def enforce_limits(self, current_tick: int):
        prune_msg = self._prune_synapses()
        limit = BoneConfig.MAX_MEMORY_CAPACITY
        victims = []
        safety_break = 0
        while len(self.graph) > limit and safety_break < 20:
            victim = self._smart_prune(current_tick)
            if not victim:
                victim, _ = self._cannibalize(current_tick=current_tick)
            if victim: victims.append(victim)
            else: break
            safety_break += 1
        if victims:
            self.events.log(f"{Prisma.YEL}[GC]: Reclaimed {len(victims)} nodes.{Prisma.RST}", "SYS")
        return prune_msg

    def _smart_prune(self, current_tick):
        keep_set = set(self.cortical_stack)
        neighbors = set()
        for node in keep_set:
            if node in self.graph:
                neighbors.update(self.graph[node]["edges"].keys())
        keep_set.update(neighbors)
        candidates = []
        for node, data in self.graph.items():
            if node in keep_set: continue
            last_tick = data.get("last_tick", 0)
            mass = sum(data["edges"].values())
            score = (last_tick * 1.0) + (mass * 0.5)
            candidates.append((node, score))
        if not candidates: return None
        candidates.sort(key=lambda x: x[1])
        victim = candidates[0][0]
        self._cannibalize(preserve_current=None, current_tick=current_tick, specific_victim=victim)
        return victim

    def _cannibalize(self, preserve_current=None, current_tick=0, specific_victim=None) -> Tuple[Optional[str], str]:
        if specific_victim:
            victim = specific_victim
            if victim not in self.graph: return None, "Victim missing."
        else:
            protected = set(self.cortical_stack)
            if preserve_current: protected.add(preserve_current)
            candidates = []
            for k, v in self.graph.items():
                if k in protected: continue
                edge_count = len(v["edges"])
                age = max(1, current_tick - v.get("last_tick", 0))
                score = edge_count + (100.0 / age)
                candidates.append((k, score))
            if not candidates: return None, "MEMORY EMPTY."
            candidates.sort(key=lambda x: x[1])
            victim = candidates[0][0]
        data = self.graph[victim]
        mass = sum(data["edges"].values())
        lifespan = current_tick - data.get("strata", {}).get("birth_tick", current_tick)
        self.fossils.append({
            "word": victim, "mass": round(mass, 2),
            "lifespan": lifespan, "death_tick": current_tick
        })
        del self.graph[victim]
        for node in self.graph:
            if victim in self.graph[node]["edges"]:
                del self.graph[node]["edges"][victim]
        return victim, f"FOSSILIZED: '{victim}'"

    def _prune_synapses(self, scaling_factor=0.9, prune_threshold=0.5):
        pruned_count = 0
        for node in self.graph:
            edges = self.graph[node]["edges"]
            dead_links = []
            for target, weight in edges.items():
                new_weight = weight * scaling_factor
                edges[target] = new_weight
                if new_weight < prune_threshold: dead_links.append(target)
            for dead in dead_links:
                del edges[dead]
                pruned_count += 1
        return f"📉 HOMEOSTASIS: Pruned {pruned_count} weak connections."

    def dream(self, physics_packet, stamina):
        psi = physics_packet.get("psi", 0.0)
        if stamina > 40.0 and psi < 0.6: return None
        heavy = [w for w in self.graph if w in TheLexicon.get("heavy")]
        abstract = [w for w in self.graph if w in TheLexicon.get("abstract")]
        if not heavy or not abstract: return None
        host = random.choice(heavy)
        parasite = random.choice(abstract)
        if parasite in self.graph[host]["edges"]: return None
        weight = 8.88
        self.graph[host]["edges"][parasite] = weight
        if parasite not in self.graph:
            self.graph[parasite] = {"edges": {}, "last_tick": 0}
        self.graph[parasite]["edges"][host] = weight
        is_metaphor = psi > 0.7
        if is_metaphor:
            return f"{Prisma.CYN}✨ SYNAPSE SPARK: Bridging '{host.upper()}' and '{parasite.upper()}'.{Prisma.RST}"
        else:
            return f"{Prisma.VIOLET}🍄 INTRUSIVE THOUGHT: Exhaustion links '{host.upper()}' <-> '{parasite.upper()}'.{Prisma.RST}"

    def replay_dreams(self):
        if not self.short_term_buffer:
            return "🌑 SLEEPLESS: No significant memories to process."
        strengthened = 0
        for engram in self.short_term_buffer:
            boost = engram["significance"] * 0.1
            words = engram["trigger"]
            if len(words) >= 2:
                w1, w2 = words[0], words[1]
                if w1 in self.graph and w2 in self.graph:
                    if w2 in self.graph[w1]["edges"]:
                        self.graph[w1]["edges"][w2] += boost
                        strengthened += 1
        self.short_term_buffer.clear()
        return f"💤 HIPPOCAMPAL REPLAY: Consolidated {strengthened} pathways."

    def save(self, health, stamina, mutations, trauma_accum, joy_history, mitochondria_traits=None, antibodies=None, soul_data=None):
        base_trauma = (BoneConfig.MAX_HEALTH - health) / BoneConfig.MAX_HEALTH
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}
        if health <= 0:
            cause = max(final_vector, key=final_vector.get) if final_vector else "UNKNOWN"
            final_vector[cause] = 1.0
        top_joy = sorted(joy_history, key=lambda x: x["resonance"], reverse=True)[:3]
        joy_legacy = None
        if top_joy:
            joy_legacy = {
                "flavor": top_joy[0]["dominant_flavor"],
                "resonance": top_joy[0]["resonance"],
                "timestamp": top_joy[0]["timestamp"]
            }
        active_seeds = [s for s in self.seeds if not s.bloomed]
        active_seeds.sort(key=lambda s: s.maturity, reverse=True)
        kept_seeds = [{"q": s.question, "m": s.maturity, "b": s.bloomed} for s in active_seeds[:5]]
        almanac = TheAlmanac()
        condition, _ = almanac.diagnose_condition(final_vector)
        future_seed = almanac.get_seed(condition)
        kept_seeds.append({"q": future_seed, "m": 0.0, "b": False})
        data = {
            "session_id": self.session_id,
            "graph": self.graph,
            "mutations": mutations,
            "trauma_vector": final_vector,
            "joy_legacy": joy_legacy,
            "mitochondria": mitochondria_traits,
            "antibodies": list(antibodies) if antibodies else [],
            "soul_legacy": soul_data,
            "seeds": kept_seeds,
            "fossils": list(self.fossils),
            "meta": {"timestamp": time.time(), "final_health": health, "final_stamina": stamina}
        }
        return self.loader.save(self.filename, data)

    def ingest(self, target_file, current_tick=0):
        data = self.loader.load(target_file)
        if not data:
            self.events.log(f"{Prisma.RED}[MEMORY]: Spore file not found.{Prisma.RST}")
            return None, set(), {}
        required = ["meta", "trauma_vector", "core_graph"]
        if not all(k in data for k in required):
            self.events.log(f"{Prisma.RED}[MEMORY]: Spore rejected (Corrupt).{Prisma.RST}")
            return None, set(), {}
        session_source = data.get("session_id", "UNKNOWN")
        self.session_health = data.get("meta", {}).get("final_health", 50)
        self.session_stamina = data.get("meta", {}).get("final_stamina", 25)
        self.session_trauma_vector = data.get("trauma_vector", {})
        time_ago = int((time.time() - data.get("meta", {}).get("timestamp", 0)) / 3600)
        self.lineage_log.append({
            "source": session_source, "age_hours": time_ago, "loaded_at": time.time()
        })
        if "core_graph" in data:
            self.graph.update(data["core_graph"])
            for node in data["core_graph"]:
                if node in self.graph: self.graph[node]["last_tick"] = current_tick
            grafted = list(data["core_graph"].keys())
            if grafted:
                sample = random.sample(grafted, min(len(grafted), 10))
                self.cortical_stack.extend(sample)
                self.events.log(f"{Prisma.CYN}[SPORE]: Grafted {len(grafted)} nodes.{Prisma.RST}")
        ALLOWED_MUTATIONS = {
            "STAMINA_REGEN", "MAX_DRAG_LIMIT", "KINETIC_GAIN",
            "TOXIN_WEIGHT", "FLASHPOINT_THRESHOLD"
        }
        if "config_mutations" in data:
            valid = 0
            for key, val in data["config_mutations"].items():
                if key in ALLOWED_MUTATIONS and hasattr(BoneConfig, key):
                    if isinstance(val, (int, float)) and 0 <= val <= 1000:
                        setattr(BoneConfig, key, val)
                        valid += 1
            if valid:
                self.events.log(f"{Prisma.CYN}► Epigenetics: Applied {valid} config shifts.{Prisma.RST}")
        if "joy_legacy" in data and data["joy_legacy"]:
            flavor = data["joy_legacy"].get("flavor")
            clade = LiteraryReproduction.JOY_CLADE.get(flavor)
            if clade:
                self.events.log(f"{Prisma.CYN}INHERITED GLORY: {clade['title']}{Prisma.RST}")
                for stat, bonus in clade["buff"].items():
                    if hasattr(BoneConfig, stat): setattr(BoneConfig, stat, bonus)
        return (
            data.get("mitochondria", {}),
            set(data.get("antibodies", [])),
            data.get("soul_legacy", {})
        )

    def autoload_last_spore(self):
        files = self.loader.list_spores()
        if not files:
            self.events.log(f"{Prisma.GRY}[GENETICS]: Genesis Bloom (No Ancestors).{Prisma.RST}")
            return None
        candidates = [f for f in files if self.session_id not in f[0]]
        if candidates:
            self.events.log(f"{Prisma.CYN}[GENETICS]: Loading ancestor...{Prisma.RST}")
            return self.ingest(candidates[0][0])
        return None

    def cleanup_old_sessions(self, limbo_layer=None):
        files = self.loader.list_spores()
        removed = 0
        max_files = 25
        for i, (path, age, fname) in enumerate(files):
            if i >= max_files:
                if limbo_layer: limbo_layer.absorb_dead_timeline(path)
                if self.loader.delete(path): removed += 1
        if removed:
            self.events.log(f"{Prisma.GRY}[TIME]: Pruned {removed} dead timelines.{Prisma.RST}")

    def report_status(self):
        return len(self.graph)

    def calculate_mass(self, node):
        if node not in self.graph: return 0.0
        return sum(self.graph[node]["edges"].values())