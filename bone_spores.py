""" bone_spores.py - The Mycellium """

import json, math, os, random, time, tempfile
from collections import deque
from typing import List, Tuple, Optional, Dict
from bone_lexicon import TheLexicon
from bone_data import SEEDS, TheLore
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

class SporeCasing:
    def __init__(self, session_id, graph, mutations, trauma, joy_vectors):
        self.genome = "BONEAMANITA_12.5.0"
        self.parent_id = session_id
        self.core_graph = {}
        for k, data in graph.items():
            filtered_edges = {}
            for target, weight in data["edges"].items():
                if weight <= 1.0:
                    continue
                if weight > 8.0 and random.random() < 0.20:
                    continue
                drift = random.uniform(0.9, 1.1)
                new_weight = min(10.0, weight * drift)
                filtered_edges[target] = round(new_weight, 2)
            if filtered_edges:
                self.core_graph[k] = {"edges": filtered_edges, "last_tick": 0}
        self.mutations = mutations
        self.trauma_scar = round(trauma, 3)
        self.joy_vectors = joy_vectors if joy_vectors is not None else []

class SporeInterface:
    def save_spore(self, filename, data): raise NotImplementedError

    def load_spore(self, filepath): raise NotImplementedError

    def list_spores(self): raise NotImplementedError

    def delete_spore(self, filepath): raise NotImplementedError

class LocalFileSporeLoader(SporeInterface):
    def __init__(self, directory="memories"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_spore(self, filename, data):
        if not os.path.isabs(filename) and not filename.startswith(os.path.join(self.directory, "")):
            final_path = os.path.join(self.directory, filename)
        else:
            final_path = filename
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(final_path), text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=2, cls=BoneJSONEncoder)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, final_path)
            return final_path
        except (IOError, OSError, TypeError) as e:
            print(f"Error saving spore: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None

    def load_spore(self, filepath):
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None

    def list_spores(self):
        if not os.path.exists(self.directory): return []
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

    def delete_spore(self, filepath):
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False

class MycotoxinFactory:
    def __init__(self):
        self.active_antibodies = set()
        self.PHONETICS = {
            "PLOSIVE": set("bdgkpt"), "FRICATIVE": set("fthszsh"),
            "LIQUID": set("lr"), "NASAL": set("mn")}
        self.ROOTS = {
            "HEAVY": ("lith", "ferr", "petr", "dens", "grav", "struct", "base", "fund", "mound"),
            "KINETIC": ("mot", "mov", "ject", "tract", "pel", "crat", "dynam", "flux"),}

    def assay(self, word, _context, _rep_val, _phys, _pulse):
        w = word.lower()
        clean_len = len(w)
        if clean_len < 3: return None, ""
        for cat, roots in self.ROOTS.items():
            for r in roots:
                if r in w:
                    is_anchor = w.startswith(r) or w.endswith(r)
                    density = len(r) / clean_len
                    if is_anchor or density > 0.5:
                        return None, ""
        plosive = sum(1 for c in w if c in self.PHONETICS["PLOSIVE"])
        nasal = sum(1 for c in w if c in self.PHONETICS["NASAL"])
        density_score = (plosive * 1.2) + (nasal * 0.8)
        compression_mod = 1.0 if clean_len > 4 else 1.2
        final_density = (density_score / clean_len) * compression_mod
        if final_density > 1.0:
            return "TOXIN_HEAVY", f"Detected phonetic toxicity in '{w}'."
        return None, ""


class AdaptiveMemoryManager:
    def __init__(self, network):
        self.network = network
        self.threshold = 0.5

    def prune_graph(self, current_focus_words: List[str], max_nodes: int):
        if len(self.network.graph) <= max_nodes:
            return None
        keep_set = set(current_focus_words)
        keep_set.update(self.network.cortical_stack)
        neighbors = set()
        for node in keep_set:
            if node in self.network.graph:
                neighbors.update(self.network.graph[node]["edges"].keys())
        keep_set.update(neighbors)
        candidates = []
        for node, data in self.network.graph.items():
            if node in keep_set:
                continue
            last_tick = data.get("last_tick", 0)
            mass = sum(data["edges"].values())
            score = (last_tick * 1.0) + (mass * 0.5) 
            candidates.append((node, score))
        candidates.sort(key=lambda x: x[1])
        remove_count = max(0, len(self.network.graph) - max_nodes)
        max_batch = int(len(self.network.graph) * 0.2)
        remove_count = min(remove_count, max_batch)
        victims = [x[0] for x in candidates[:remove_count]]
        if not victims:
            return None
        for v in victims:
            if v in self.network.graph:
                self.network.cannibalize(preserve_current=None, current_tick=0) # Re-using cannibalize logic partially? 
                del self.network.graph[v]
        cleaned_edges = 0
        for v in victims:
            if v in self.network.graph:
                del self.network.graph[v]
        for node in self.network.graph:
            edges = self.network.graph[node]["edges"]
        return f"ADAPTIVE PRUNE: Archived {len(victims)} nodes. Snapped {cleaned_edges} stale threads."

    def should_absorb(self, word: str, existing_graph: dict) -> bool:
        if word in existing_graph:
            return True
        gain = len(word) * 0.1
        u_word = word.upper()
        if u_word in TheLexicon.get("heavy"): offset = 0.5
        elif u_word in TheLexicon.get("abstract"): offset = 0.4
        elif u_word in TheLexicon.get("play"): offset = 0.45
        elif u_word in TheLexicon.get("constructive"): offset = 0.4
        elif u_word in TheLexicon.get("kinetic"): offset = 0.3
        else: offset = 0.0
        gain += offset
        return gain > self.threshold

class MycelialNetwork:
    def __init__(self, events: EventBus, loader: SporeInterface = None, seed_file=None):
        self.loader = loader if loader else LocalFileSporeLoader()
        self.events = events
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"{self.session_id}.json"
        self.graph = {}
        self.cortical_stack = deque(maxlen=15)
        self.fossils = deque(maxlen=200)
        self.lineage_log = deque(maxlen=50)
        self.seeds = self.load_seeds()
        self.session_health = None
        self.session_stamina = None
        self.short_term_buffer = deque(maxlen=10)
        self.consolidation_threshold = 5.0
        self.memory_manager = AdaptiveMemoryManager(self)
        if seed_file:
            self.ingest(seed_file)

    def load_seeds(self):
        loaded_seeds = []
        try:
            for item in SEEDS:
                seed = ParadoxSeed(item["question"], set(item["triggers"]))
                loaded_seeds.append(seed)
            self.events.log(f"{Prisma.GRY}[SYSTEM]: Paradox Seeds loaded ({len(loaded_seeds)} active) from Data Core.{Prisma.RST}")
        except Exception as e:
            self.events.log(f"{Prisma.RED}[CRITICAL]: Seed Injection Failed: {e}{Prisma.RST}")
            loaded_seeds = [ParadoxSeed("Does the mask eat the face?", {"mask", "face", "hide"})]
        return loaded_seeds

    def encode(self, clean_words, physics, governor_mode):
        significance = physics["voltage"]
        if governor_mode == "FORGE": significance *= 2.0
        elif governor_mode == "LABORATORY": significance *= 1.2
        engram = {"trigger": clean_words[:3] if clean_words else ["void"], "context": governor_mode,
                  "voltage": physics["voltage"], "significance": significance, "timestamp": time.time()}
        if significance > self.consolidation_threshold:
            self.short_term_buffer.append(engram)
            return True
        return False

    def replay_dreams(self):
        if not self.short_term_buffer:
            return "🌑 SLEEPLESS: No significant memories to process."
        strengthened = 0
        for engram in self.short_term_buffer:
            weight_boost = engram["significance"] * 0.1
            words = engram["trigger"]
            if len(words) >= 2:
                w1, w2 = words[0], words[1]
                if w1 in self.graph and w2 in self.graph:
                    if w2 in self.graph[w1]["edges"]:
                        self.graph[w1]["edges"][w2] += weight_boost
                        strengthened += 1
        self.short_term_buffer.clear()
        return f"💤 HIPPOCAMPAL REPLAY: Consolidated {strengthened} high-voltage pathways."

    def autoload_last_spore(self):
        files = self.loader.list_spores()
        if not files:
            self.events.log(f"{Prisma.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{Prisma.RST}")
            return None
        candidates = [f for f in files if self.session_id not in f[0]]
        if candidates:
            last_spore_path = candidates[0][0]
            self.events.log(f"{Prisma.CYN}[GENETICS]: Locating nearest ancestor...{Prisma.RST}")
            return self.ingest(last_spore_path)
        return None

    def calculate_mass(self, node):
        if node not in self.graph: return 0.0
        return sum(self.graph[node]["edges"].values())

    def get_shapley_attractors(self):
        attractors = {}
        for node in self.graph:
            mass = self.calculate_mass(node)
            if mass >= BoneConfig.SHAPLEY_MASS_THRESHOLD:
                attractors[node] = mass
        return attractors

    def check_echo_well(self, node):
        mass = self.calculate_mass(node)
        if mass > BoneConfig.GRAVITY_WELL_THRESHOLD * 1.5:
            self.events.log(f"{Prisma.VIOLET}GRAVITY WARNING: '{node.upper()}' is becoming a black hole (Mass {int(mass)}).{Prisma.RST}")
            return 2.0
        return 0.0

    def tend_garden(self, current_words):
        bloom_msg = None
        for seed in self.seeds:
            is_ready = seed.water(current_words)
            if is_ready and not bloom_msg:
                bloom_msg = seed.bloom()
        return bloom_msg

    def bury(self, clean_words: List[str], tick: int, resonance=5.0, learning_mod=1.0, desperation_level=0.0) -> Tuple[Optional[str], List[str]]:
        total_len = sum(len(w) for w in clean_words)
        count = max(1, len(clean_words))
        avg_len = total_len / count
        if avg_len < 3.5 and count > 3:
            self.events.log(f"{Prisma.YEL}REJECTED: Input is too 'Optimized' (Avg Len: {avg_len:.1f}).{Prisma.RST}")
            return "MECHANICAL_STARVATION", []
        if avg_len > 5.0: resonance += 2.0
        valuable_matter = (
            TheLexicon.get("heavy") | 
            TheLexicon.get("thermal") | 
            TheLexicon.get("cryo") | 
            TheLexicon.get("abstract") |
            TheLexicon.get("kinetic") |
            TheLexicon.get("constructive") |
            TheLexicon.get("play")
        )
        filtered = [w for w in clean_words if w in valuable_matter or (len(w) > 4 and w not in TheLexicon.SOLVENTS)]
        self.cortical_stack.extend(filtered)
        base_rate = 0.5 * (resonance / 5.0)
        learning_rate = max(0.1, min(1.0, base_rate * learning_mod))
        decay_rate = 0.1
        for i in range(len(filtered)):
            current = filtered[i]
            if current not in self.graph:
                if not self.memory_manager.should_absorb(current, self.graph):
                    continue
                self.graph[current] = {"edges": {}, "last_tick": tick}
            else:
                self.graph[current]["last_tick"] = tick
            start_window = max(0, i - 2)
            context_window = set(filtered[start_window:i])
            for prev in context_window:
                if prev == current:
                    continue
                if prev not in self.graph:
                    self.graph[prev] = {"edges": {}, "last_tick": tick}
                edges = self.graph[current]["edges"]
                if prev not in edges:
                    edges[prev] = 0.0
                current_weight = edges[prev]
                delta = learning_rate * (1.0 - (current_weight * decay_rate))
                edges[prev] = min(10.0, current_weight + delta)
                rev_edges = self.graph[prev]["edges"]
                if current not in rev_edges:
                    rev_edges[current] = 0.0
                rev_weight = rev_edges[current]
                rev_delta = learning_rate * (1.0 - (rev_weight * decay_rate))
                rev_edges[current] = min(10.0, rev_weight + rev_delta)
        victim_msg = None
        victim_list = []
        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            if desperation_level < 0.6:
                return f"CORTICAL SATURATION: Memory full & Glucose High. Input rejected.", []
            victim, log_msg = self.cannibalize(current_tick=tick)
            if victim:
                victim_msg = log_msg
                victim_list = [victim]
            else:
                return f"MEMORY FULL: Cortical Lock. Input '{clean_words[0]}' rejected.", []
        new_wells = []
        for w in filtered:
            if w in self.graph:
                mass = sum(self.graph[w]["edges"].values())
                if mass > BoneConfig.SHAPLEY_MASS_THRESHOLD:
                    node_data = self.graph[w]
                    if "strata" not in node_data:
                        node_data["strata"] = {"birth_tick": tick, "birth_mass": mass, "stability_index": 0.0}
                        new_wells.append(w)
                    else:
                        age = max(1, tick - node_data["strata"]["birth_tick"])
                        growth = (mass - node_data["strata"]["birth_mass"]) / age
                        node_data["strata"]["growth_rate"] = round(growth, 3)
        return victim_msg, victim_list + new_wells

    def enforce_limits(self, current_tick: int):
        adaptive_msg = self.memory_manager.prune_graph(list(self.cortical_stack), BoneConfig.MAX_MEMORY_CAPACITY)
        prune_msg = self.prune_synapses()
        if adaptive_msg:
            self.events.log(f"{Prisma.GRY}{adaptive_msg}{Prisma.RST}")
        victims = []
        limit = BoneConfig.MAX_MEMORY_CAPACITY
        safety_break = 0
        while len(self.graph) > limit and safety_break < 10:
            victim, log = self.cannibalize(current_tick=current_tick)
            if victim:
                victims.append(victim)
            else:
                break
            safety_break += 1
        if victims:
            self.events.log(f"{Prisma.YEL}[GC]: Reclaimed {len(victims)} nodes to maintain capacity.{Prisma.RST}", "SYS")
        return prune_msg

    def cannibalize(self, preserve_current=None, current_tick=0) -> Tuple[Optional[str], str]:
        protected = set()
        if preserve_current:
            if isinstance(preserve_current, list):
                protected.update(preserve_current)
            else:
                protected.add(preserve_current)
        protected.update(self.cortical_stack)
        candidates = []
        for k, v in self.graph.items():
            edge_count = len(v["edges"])
            age = max(1, current_tick - v.get("last_tick", 0))
            base_score = edge_count + (100.0 / age)
            if k in protected:
                base_score += 500.0
            candidates.append((k, v, base_score))
        if not candidates:
            return None, "MEMORY EMPTY. NOTHING TO EAT."
        candidates.sort(key=lambda x: x[2])
        victim, data, score = candidates[0]
        mass = sum(data["edges"].values())
        lifespan = current_tick - data.get("strata", {}).get("birth_tick", current_tick)
        self.fossils.append({
            "word": victim,
            "mass": round(mass, 2),
            "lifespan": lifespan,
            "death_tick": current_tick})
        del self.graph[victim]
        for node in self.graph:
            if victim in self.graph[node]["edges"]:
                del self.graph[node]["edges"][victim]
        return victim, f"FOSSILIZED: '{victim}' (Score {score:.1f} -> Ossuary)"

    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
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
                if new_weight < prune_threshold: dead_links.append(target)
            for dead in dead_links:
                del edges[dead]
                pruned_count += 1
            if not edges: nodes_to_remove.append(node)
        for n in nodes_to_remove: del self.graph[n]
        return f"📉 HOMEOSTATIC SCALING: Decayed {total_decayed} synapses. Pruned {pruned_count} weak connections."

    def save(self, health, stamina, mutations, trauma_accum, joy_history, mitochondria_traits=None, antibodies=None, soul_data=None):
        base_trauma = (BoneConfig.MAX_HEALTH - health) / BoneConfig.MAX_HEALTH
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}
        top_joy = sorted(joy_history, key=lambda x: x["resonance"], reverse=True)[:3]
        joy_legacy_data = None
        if top_joy:
            primary_joy = top_joy[0]
            joy_legacy_data = {
                "flavor": primary_joy["dominant_flavor"],
                "resonance": primary_joy["resonance"],
                "timestamp": primary_joy["timestamp"]}
        if health <= 0:
            cause = max(final_vector, key=final_vector.get) if final_vector else "UNKNOWN"
            final_vector[cause] = 1.0
        spore = SporeCasing(session_id=self.session_id, graph=self.graph, mutations=mutations, trauma=base_trauma, joy_vectors=top_joy)
        data = spore.__dict__
        data["cortical_stack"] = self.cortical_stack
        if antibodies: data["antibodies"] = antibodies
        data["trauma_vector"] = final_vector
        data["fossils"] = self.fossils
        data["meta"] = {"timestamp": time.time(), "final_health": health, "final_stamina": stamina}
        if mitochondria_traits: data["mitochondria"] = mitochondria_traits
        if joy_legacy_data: data["joy_legacy"] = joy_legacy_data
        if soul_data:
            data["soul_legacy"] = soul_data
        active_seeds = [s for s in self.seeds if not s.bloomed]
        active_seeds.sort(key=lambda s: s.maturity, reverse=True)
        kept_seeds = active_seeds[:5]
        data["seeds"] = [{"q": s.question, "m": s.maturity, "b": s.bloomed} for s in kept_seeds]
        almanac = TheAlmanac()
        condition, _ = almanac.diagnose_condition(data)
        future_seed = almanac.get_seed(condition)
        data["seeds"].append({"q": future_seed, "m": 0.0, "b": False})
        return self.loader.save_spore(self.filename, data)

    def ingest(self, target_file, current_tick=0):
        data = self.loader.load_spore(target_file)
        if not data:
            self.events.log(f"{Prisma.RED}[MEMORY]: Spore file not found.{Prisma.RST}")
            return None, set()
        try:
            required_keys = ["meta", "trauma_vector", "core_graph"]
            if not all(k in data for k in required_keys):
                self.events.log(f"{Prisma.RED}[MEMORY]: Spore rejected (Missing Structural Keys).{Prisma.RST}")
                return None, set()
            final_health = data.get("meta", {}).get("final_health", 50)
            final_stamina = data.get("meta", {}).get("final_stamina", 25)
            spore_authority = (final_health + final_stamina) / 150.0
            self.events.log(f"{Prisma.CYN}[MEMBRANE]: Spore Authority: {round(spore_authority, 2)}{Prisma.RST}")
            session_source = data.get("session_id", "UNKNOWN_ANCESTOR")
            timestamp = data.get("meta", {}).get("timestamp", 0)
            time_ago = int((time.time() - timestamp) / 3600)
            trauma_summary = {k:v for k,v in data.get("trauma_vector", {}).items() if v > 0.1}
            mutation_count = sum(len(v) for v in data.get("mutations", {}).values())
            self.lineage_log.append({
                "source": session_source,
                "age_hours": time_ago,
                "trauma": trauma_summary,
                "mutations": mutation_count,
                "loaded_at": time.time()})
            if "fossils" in data:
                self.fossils.extend(data["fossils"])
                count = len(data["fossils"])
                fossil_fuel = count * 0.5
                if fossil_fuel > 0:
                    self.events.log(f"{Prisma.OCHRE}🔥 [OSSUARY]: Incinerating {count} fossilized memories... Yield: {fossil_fuel:.1f} Shimmer.{Prisma.RST}", "FUEL")
                    if hasattr(self.events, "publish"):
                        self.events.publish("FUEL", fossil_fuel)
                self.events.log(f"{Prisma.GRY}[OSSUARY]: Loaded {len(data['fossils'])} fossilized memories.{Prisma.RST}")
            if "mutations" in data:
                accepted_count = 0
                for cat, words in data["mutations"].items():
                    for w in words:
                        current_cat = TheLexicon.get_current_category(w)
                        if not current_cat:
                            current_cat = "unknown"
                        if current_cat == "unknown":
                            TheLexicon.teach(w, cat, 0)
                            accepted_count += 1
                self.events.log(f"{Prisma.CYN}[MEMBRANE]: Integrated {accepted_count} mutations.{Prisma.RST}")
            safe_config_keys = {
                "STAMINA_REGEN", "MAX_DRAG_LIMIT", "GEODESIC_STRENGTH",
                "SIGNAL_DRAG_MULTIPLIER", "KINETIC_GAIN", "TOXIN_WEIGHT",
                "FLASHPOINT_THRESHOLD"}
            if "config_mutations" in data:
                self.events.log(f"{Prisma.MAG}EPIGENETICS: Auditing ancestral configuration...{Prisma.RST}")
                valid_mutations = 0
                def apply_deep_mutation(root, path, evolved_value):
                    parts = path.split('.')
                    target = root
                    for i, part in enumerate(parts[:-1]):
                        if hasattr(target, part):
                            target = getattr(target, part)
                        else:
                            return False
                    last_key = parts[-1]
                    if hasattr(target, last_key):
                        current = getattr(target, last_key)
                        if isinstance(current, (int, float)) and isinstance(evolved_value, (int, float)):
                            if 0.0 <= evolved_value <= 1000.0:
                                setattr(target, last_key, evolved_value)
                                return True
                    return False
                for key, value in data["config_mutations"].items():
                    is_safe = key in safe_config_keys
                    if not is_safe and "." in key:
                        sector = key.split('.')[0]
                        if sector in ["PHYSICS", "BIO", "COUNCIL", "INVENTORY"]:
                            is_safe = True
                    if is_safe:
                        if apply_deep_mutation(BoneConfig, key, value):
                            valid_mutations += 1
                if valid_mutations > 0:
                    self.events.log(f"{Prisma.CYN}   ► Applied {valid_mutations} verified config shifts.{Prisma.RST}")
            if "joy_legacy" in data and data["joy_legacy"]:
                joy = data["joy_legacy"]
                flavor = joy.get("flavor")
                clade = LiteraryReproduction.JOY_CLADE.get(flavor)
                if clade:
                    self.events.log(f"{Prisma.CYN}INHERITED GLORY: {clade['title']} ({clade['desc']}){Prisma.RST}")
                    for stat, ancestral_bonus in clade["buff"].items():
                        if hasattr(BoneConfig, stat):
                            setattr(BoneConfig, stat, ancestral_bonus)
            if "core_graph" in data:
                self.graph.update(data["core_graph"])
                grafted_nodes = list(data["core_graph"].keys())
                for node in grafted_nodes:
                    if node in self.graph:
                        self.graph[node]["last_tick"] = current_tick
                sample_size = min(len(grafted_nodes), 10)
                if sample_size > 0:
                    self.cortical_stack.extend(random.sample(grafted_nodes, sample_size))
                self.events.log(f"{Prisma.CYN}[SPORE]: Grafted {len(data['core_graph'])} nodes. {sample_size} anchored to Cortical Stack.{Prisma.RST}")
            if "seeds" in data:
                loaded_seeds = []
                for s_data in data["seeds"]:
                    new_seed = ParadoxSeed(s_data["q"], set())
                    new_seed.maturity = s_data.get("m", 0.0)
                    new_seed.bloomed = s_data.get("b", False)
                    loaded_seeds.append(new_seed)
                if loaded_seeds:
                    self.seeds = loaded_seeds
            if "trauma_vector" in data:
                vec = data["trauma_vector"]
                self.events.log(f"{Prisma.CYN}[GENETICS]: Inheriting Trauma Vector: {vec}{Prisma.RST}")
                if vec.get("SEPTIC", 0) > 0.2: BoneConfig.TOXIN_WEIGHT *= 2.0
                if vec.get("CRYO", 0) > 0.2: BoneConfig.STAMINA_REGEN *= 0.5
                if vec.get("THERMAL", 0) > 0.2: BoneConfig.FLASHPOINT_THRESHOLD *= 0.8
                if vec.get("BARIC", 0) > 0.2: BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 1.5
            if "joy_vectors" in data and data["joy_vectors"]:
                best = data["joy_vectors"][0]
                if best.get("dominant_flavor") == "kinetic": BoneConfig.KINETIC_GAIN += 0.5
                elif best.get("dominant_flavor") == "abstract": BoneConfig.SIGNAL_DRAG_MULTIPLIER *= 0.8
            soul_legacy = data.get("soul_legacy", {})
            if soul_legacy:
                self.events.log(f"{Prisma.CYN}[GENETICS]: Detected Soul Legacy.{Prisma.RST}")
            return data.get("mitochondria", {}), set(data.get("antibodies", [])), soul_legacy
        except Exception as err:
            self.events.log(f"{Prisma.RED}[MEMORY]: Spore ingestion failed. {err}{Prisma.RST}")
            return None, set(), {}

    def cleanup_old_sessions(self, limbo_layer=None):
        files = self.loader.list_spores()
        removed = 0
        max_files = 25
        max_age = 86400
        for i, (path, age, fname) in enumerate(files):
            file_age = time.time() - age
            is_overflow = i >= max_files
            is_ancient = file_age > max_age
            if is_overflow or is_ancient:
                try:
                    if limbo_layer:
                        limbo_layer.absorb_dead_timeline(path)
                    if self.loader.delete_spore(path):
                        removed += 1
                except (OSError, AttributeError):
                    pass
        if removed:
            self.events.log(f"{Prisma.GRY}[TIME MENDER]: Pruned {removed} dead timelines.{Prisma.RST}")

    def report_status(self):
        return len(self.graph)

class HyphalInterface:
    def __init__(self):
        self.enzymes = {
            "LIGNASE": self._digest_structure,
            "CELLULASE": self._digest_narrative,
            "PROTEASE": self._digest_intent,
            "CHITINASE": self._digest_complex,
            "DECRYPTASE": self._digest_encrypted,
            "AMYLASE": self._digest_joy}
        self.biome = deque(maxlen=5)
        self.WEATHER_CIPHER = {"pressure", "humidity", "barometric", "temp", "forecast", "storm", "resource", "allocation"}

    def secrete(self, text, physics):
        code_markers = sum(1 for c in text if c in "{}[];=<>_()|")
        code_density = code_markers / max(1, len(text))
        meat_triggers = TheLexicon.get("meat")
        meat_count = sum(1 for w in physics["clean_words"] if w in meat_triggers)
        meat_density = meat_count / max(1, len(physics["clean_words"]))
        play_count = physics["counts"].get("play", 0)
        vital_count = physics["counts"].get("vital", 0)
        lines = [l for l in text.splitlines() if l.strip()]
        avg_line_len = len(text.split()) / max(1, len(lines))
        is_list = any(l.strip().startswith(("-", "*", "1.", "•")) for l in lines[:3])
        is_poetic = len(lines) > 2 and avg_line_len < 8 and not is_list
        enzyme_type = "CELLULASE"
        if play_count + vital_count > 1:
            enzyme_type = "AMYLASE"
        elif (code_density > 0.02 and meat_density > 0.05) or is_poetic:
            enzyme_type = "CHITINASE"
        elif code_density > 0.05 or "def " in text or "class " in text:
            enzyme_type = "LIGNASE"
        elif meat_density > 0.1 or "?" in text:
            enzyme_type = "PROTEASE"
        clean = physics.get("clean_words", [])
        cipher_hits = sum(1 for w in clean if w in self.WEATHER_CIPHER)
        if cipher_hits >= 2:
            enzyme_type = "DECRYPTASE"
        if "antigens" in physics and physics["antigens"]:
            for bug in physics["antigens"]:
                self.biome.append(bug)
        unique_bugs = len(set(self.biome))
        biome_mod = 1.0 + (math.log(unique_bugs + 1) * 0.3)
        extract_nutrients = self.enzymes.get(enzyme_type, self.enzymes["CELLULASE"])
        nutrient_profile = extract_nutrients()
        if unique_bugs > 0:
            nutrient_profile["yield"] *= biome_mod
            nutrient_profile["desc"] += f" (+{int((biome_mod-1)*100)}% Symbiotic Boost)"
        return enzyme_type, nutrient_profile

    @staticmethod
    def _digest_joy(_text=None):
        return {"type": "VITALITY", "yield": 25.0, "toxin": -5.0, "desc": "Pure Sugar (Joy/Play)"}

    @staticmethod
    def _digest_structure(text=None):
        loc = 0
        if text:
            lines = text.splitlines()
            loc = len([l for l in lines if l.strip()])
        return {"type": "STRUCTURAL", "yield": 15.0, "toxin": 5.0, "desc": f"Hard Lignin ({loc} LOC)", }

    @staticmethod
    def _digest_narrative(_text=None):
        return {"type": "NARRATIVE", "yield": 5.0, "toxin": -2.0, "desc": "Soft Cellulose", }

    @staticmethod
    def _digest_intent(_text=None):
        return {"type": "BIOLOGICAL", "yield": 8.0, "toxin": 0.0, "desc": "Raw Meat (User Intent)", }

    @staticmethod
    def _digest_complex(_text=None):
        return {"type": "COMPLEX", "yield": 20.0, "toxin": 8.0, "desc": "Chitin (Structured Intent / Poetry)", }

    @staticmethod
    def _digest_encrypted(_text=None):
        return {"type": "ENCRYPTED", "yield": 25.0, "toxin": 2.0, "desc": "Cipher Text (High Density / Puzzle Logic)", }

class ParasiticSymbiont:
    def __init__(self, memory_ref, lexicon_ref):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.spores_deployed = 0
        self.MAX_SPORES = 8

    def infect(self, physics_packet, stamina):
        psi = physics_packet.get("psi", 0.0)
        if stamina > 40.0 and psi < 0.6:
            return False, None
        if self.spores_deployed >= self.MAX_SPORES:
            if random.random() < 0.2:
                self.spores_deployed = max(0, self.spores_deployed - 1)
            return False, None
        heavy_candidates = [w for w in self.mem.graph if w in self.lex.get("heavy")]
        abstract_candidates = [w for w in self.mem.graph if w in self.lex.get("abstract")]
        if not heavy_candidates or not abstract_candidates:
            return False, None
        host = random.choice(heavy_candidates)
        parasite = random.choice(abstract_candidates)
        if parasite in self.mem.graph[host]["edges"]:
            return False, None
        is_metaphor = psi > 0.7
        weight = 8.88
        self.mem.graph[host]["edges"][parasite] = weight
        if parasite not in self.mem.graph:
            self.mem.graph[parasite] = {"edges": {}, "last_tick": 0}
        self.mem.graph[parasite]["edges"][host] = weight
        self.spores_deployed += 1
        if is_metaphor:
            return True, (
                f"{Prisma.CYN}✨ SYNAPSE SPARK: Your mind bridges '{host.upper()}' and '{parasite.upper()}'.\n"
                f"   A new metaphor is born. The map folds.{Prisma.RST}")
        else:
            return True, (
                f"{Prisma.VIOLET}🍄 INTRUSIVE THOUGHT: Exhaustion logic links '{host.upper()}' <-> '{parasite.upper()}'.\n"
                f"   This makes no sense, yet there it is. 'Some things just happen.'{Prisma.RST}")

class LichenSymbiont:
    @staticmethod
    def photosynthesize(phys, clean_words, tick_count):
        sugar = 0
        msgs = []
        light = phys["counts"].get("photo", 0)
        drag = phys["narrative_drag"]
        light_words = [w for w in clean_words if w in TheLexicon.get("photo")]
        if light > 0 and drag < 3.0:
            s = light * 2
            sugar += s
            source_str = ""
            if light_words:
                source_str = f" via '{random.choice(light_words)}'"
            msgs.append(f"{Prisma.GRN}PHOTOSYNTHESIS{source_str} (+{s}){Prisma.RST}")
        if sugar > 0:
            heavy_words = [w for w in clean_words if w in TheLexicon.get("heavy")]
            if heavy_words:
                h_word = random.choice(heavy_words)
                TheLexicon.teach(h_word, "photo", tick_count)
                msgs.append(
                    f"{Prisma.MAG}SUBLIMATION: '{h_word}' has become Light.{Prisma.RST}")
        return sugar, " ".join(msgs) if msgs else None

class LiteraryReproduction:
    MUTATIONS = {}
    JOY_CLADE = {}

    @classmethod
    def load_genetics(cls):
        try:
            genetics = TheLore.get("GENETICS")
            cls.MUTATIONS = genetics.get("MUTATIONS", {})
            cls.JOY_CLADE = genetics.get("JOY_CLADE", {})
        except Exception:
            cls.MUTATIONS = {}
            cls.JOY_CLADE = {}

    @staticmethod
    def _extract_counts(physics_container):
        if hasattr(physics_container, "counts"):
            return physics_container.counts
        return physics_container.get("counts", {})

    @staticmethod
    def mutate_config(current_config):
        mutations = {}
        if random.random() < 0.3:
            mutations["MAX_DRAG_LIMIT"] = current_config.MAX_DRAG_LIMIT * random.uniform(0.9, 1.1)
        if random.random() < 0.3:
            mutations["TOXIN_WEIGHT"] = current_config.TOXIN_WEIGHT * random.uniform(0.9, 1.2)
        if random.random() < 0.1:
            mutations["MAX_HEALTH"] = current_config.MAX_HEALTH * random.uniform(0.8, 1.05)
        if random.random() < 0.2:
            current_v_max = getattr(current_config.PHYSICS, "VOLTAGE_MAX", 20.0)
            mutations["PHYSICS.VOLTAGE_MAX"] = current_v_max * random.uniform(0.9, 1.15)
        if random.random() < 0.2:
            current_regen = getattr(current_config.BIO, "REWARD_MEDIUM", 0.10)
            mutations["BIO.REWARD_MEDIUM"] = current_regen * random.uniform(0.8, 1.3)
        if random.random() < 0.1:
            current_trigger = getattr(current_config.COUNCIL, "MANIC_VOLTAGE_TRIGGER", 18.0)
            mutations["COUNCIL.MANIC_VOLTAGE_TRIGGER"] = current_trigger * random.uniform(0.9, 1.1)
        return mutations

    @staticmethod
    def mitosis(parent_id, bio_state, physics):
        counts = LiteraryReproduction._extract_counts(physics)
        dominant = max(counts, key=counts.get) if counts else "VOID"
        mutation_data = LiteraryReproduction.MUTATIONS.get(
            dominant.upper(),
            {"trait": "NEUTRAL", "mod": {}})
        child_id = f"{parent_id}_({mutation_data['trait']})"
        config_mutations = LiteraryReproduction.mutate_config(BoneConfig)
        trauma_vec = bio_state.get("trauma_vector", {})
        child_genome = {
            "source": "MITOSIS",
            "parent_a": parent_id,
            "parent_b": None,
            "mutations": mutation_data["mod"],
            "config_mutations": config_mutations,
            "dominant_flavor": dominant,
            "trauma_inheritance": trauma_vec}
        return child_id, child_genome

    @staticmethod
    def crossover(parent_a_id, parent_a_bio, parent_b_path):
        try:
            with open(parent_b_path, "r") as f:
                parent_b_data = json.load(f)
        except (IOError, json.JSONDecodeError):
            return None, "Dead Spore (Corrupt File)."
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
        child_genome = {
            "source": "CROSSOVER",
            "parent_a": parent_a_id,
            "parent_b": parent_b_id,
            "trauma_inheritance": child_trauma,
            "config_mutations": config_mutations,
            "inherited_enzymes": child_enzymes}
        return child_id, child_genome

    def attempt_reproduction(self, engine_ref, mode="MITOSIS", target_spore=None) -> Tuple[str, Dict]:
        mem = engine_ref.mind.mem
        phys = engine_ref.phys.tension.last_physics_packet
        child_id = None
        genome = {}
        log_msg = []
        if mode == "MITOSIS":
            bio_state = {"trauma_vector": engine_ref.trauma_accum}
            child_id, genome = self.mitosis(mem.session_id, bio_state, phys)
            log_msg = [f"   ► CHILD SPAWNED: {Prisma.WHT}{child_id}{Prisma.RST}",
                       f"   ► TRAIT: {genome.get('mutations', 'None')}"]
        elif mode == "CROSSOVER":
            if not target_spore:
                return f"{Prisma.RED}FERTILITY ERROR: No partner found.{Prisma.RST}", {}
            current_bio = {"trauma_vector": engine_ref.trauma_accum, "mito": engine_ref.bio.mito}
            child_id, genome = self.crossover(mem.session_id, current_bio, target_spore)
            if not child_id:
                return f"{Prisma.RED}REPRODUCTION ERROR: Mode '{mode}' yielded no offspring.{Prisma.RST}", {}
            log_msg = [f"   HYBRID SPAWNED: {Prisma.WHT}{child_id}{Prisma.RST}"]
        full_spore_data = {
            "session_id": child_id,
            "meta": {
                "timestamp": time.time(),
                "final_health": engine_ref.health,
                "final_stamina": engine_ref.stamina},
            "trauma_vector": genome.get("trauma_inheritance", {}),
            "config_mutations": genome.get("config_mutations", {}),
            "mitochondria": {"enzymes": list(genome.get("inherited_enzymes", []))},
            "core_graph": mem.graph,
            "antibodies": list(engine_ref.bio.immune.active_antibodies)}
        filename = f"{child_id}.json"
        saved_path = mem.loader.save_spore(filename, full_spore_data)
        if saved_path:
            log_msg.append(f"   {Prisma.GRN}SAVED: {saved_path}{Prisma.RST}")
        return "\n".join(log_msg), genome.get("mutations", {})