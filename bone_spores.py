""" bone_spores.py - The Mycelium & Persistence Layer """

import json, os, random, time, tempfile
from collections import deque
from typing import List, Tuple, Optional, Dict, Any, Set

from bone_lexicon import TheLexicon
from bone_core import EventBus, TheLore, BoneJSONEncoder
from bone_types import Prisma
from bone_config import BoneConfig

"""HELPER FUNCTIONS"""

def _access_config_path(root, path, value=None, set_mode=False):
    """Safe accessor for dot-notation config paths."""
    parts = path.split(".")
    target = root
    try:
        for part in parts[:-1]:
            if isinstance(target, dict):
                target = target.get(part)
            else:
                target = getattr(target, part)
            if target is None:
                return None
        leaf = parts[-1]
        if set_mode:
            if isinstance(target, dict):
                if leaf in target and isinstance(target[leaf], (int, float)):
                    target[leaf] = value
                    return True
            elif hasattr(target, leaf):
                current = getattr(target, leaf)
                if isinstance(current, (int, float)):
                    setattr(target, leaf, value)
                    return True
            return False
        else:
            if isinstance(target, dict):
                return target.get(leaf)
            return getattr(target, leaf, None)
    except (AttributeError, KeyError, TypeError):
        return None


"""PERSISTENCE LAYER"""


class LocalFileSporeLoader:
    def __init__(self, directory="memories"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_spore(self, filename, data):
        temp_path = filename
        if not os.path.isabs(filename) and not filename.startswith(
            os.path.join(self.directory, "")
        ):
            final_path = os.path.join(self.directory, filename)
        else:
            final_path = filename
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        try:
            fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(final_path), text=True)
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2, cls=BoneJSONEncoder)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, final_path)
            return final_path
        except (IOError, OSError, TypeError) as e:
            print(f"{Prisma.RED}[LOADER] Error saving spore: {e}{Prisma.RST}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None

    def load_spore(self, filepath):
        if not os.path.exists(filepath):
            print(f"{Prisma.RED}[LOADER] File not found: {filepath}{Prisma.RST}")
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"{Prisma.RED}[LOADER] CORRUPT SPORE ({filepath}): {e}{Prisma.RST}")
            return None
        except IOError as e:
            print(f"{Prisma.RED}[LOADER] READ ERROR ({filepath}): {e}{Prisma.RST}")
            return None

    def list_spores(self):
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

    def delete_spore(self, filepath):
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False


class SubconsciousStrata:
    def __init__(self, filename="memories/subconscious.jsonl"):
        self.filepath = filename
        self.directory = os.path.dirname(filename)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.index = set()
        self._load_index()

    def _load_index(self):
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        if "word" in entry:
                            self.index.add(entry["word"])
                    except json.JSONDecodeError:
                        continue
        except IOError:
            pass

    def bury(self, fossil_data: Dict):
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                fossil_data["buried_at"] = time.time()
                f.write(json.dumps(fossil_data, cls=BoneJSONEncoder) + "\n")
            self.index.add(fossil_data["word"])
            return True
        except IOError:
            return False

    def dredge(self, trigger_word: str) -> Optional[Dict]:
        if trigger_word not in self.index:
            return None
        found = None
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get("word") == trigger_word:
                        found = entry
        except IOError:
            return None
        return found


"""MEMORY CORE (GRAPH LOGIC)"""


class MemoryCore:
    """Handles the raw graph operations: Synapses, Weights, Pruning."""

    def __init__(self, events_ref, subconscious_ref):
        self.events = events_ref
        self.subconscious = subconscious_ref
        self.graph = {}
        self.cortical_stack = deque(maxlen=15)
        self.short_term_buffer = deque(maxlen=10)
        self.consolidation_threshold = 5.0

    def calculate_mass(self, node):
        if node not in self.graph:
            return 0.0
        return sum(self.graph[node]["edges"].values())

    def strengthen_link(self, source, target, rate, decay):
        if source not in self.graph:
            return
        edges = self.graph[source]["edges"]
        if target not in edges:
            edges[target] = 0.0
        current_weight = edges[target]
        delta = rate * (1.0 - (current_weight * decay))
        edges[target] = min(10.0, current_weight + delta)

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
                if new_weight < prune_threshold:
                    dead_links.append(target)
            for dead in dead_links:
                del edges[dead]
                pruned_count += 1
            if not edges:
                nodes_to_remove.append(node)
        for n in nodes_to_remove:
            del self.graph[n]
        return f"📉 HOMEOSTATIC SCALING: Decayed {total_decayed} synapses. Pruned {pruned_count} weak connections."

    def cannibalize(
        self, current_tick, preserve_current=None
    ) -> Tuple[Optional[str], str]:
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
        fossil_data = {
            "word": victim,
            "mass": round(mass, 2),
            "lifespan": lifespan,
            "edges": data["edges"],
            "death_tick": current_tick,
        }
        self.subconscious.bury(fossil_data)

        del self.graph[victim]
        for node in self.graph:
            if victim in self.graph[node]["edges"]:
                del self.graph[node]["edges"][victim]

        return victim, f"REPRESSED: '{victim}' (Score {score:.1f} -> Subconscious)"


"""THE COORDINATOR"""


class MycelialNetwork:
    def __init__(
        self, events: EventBus, loader: "LocalFileSporeLoader" = None, seed_file=None
    ):
        self.events = events
        self.loader = loader if loader else LocalFileSporeLoader()
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"{self.session_id}.json"
        self.subconscious = SubconsciousStrata()
        self.memory_core = MemoryCore(events, self.subconscious)
        self.lichen = BioLichen()
        self.parasite = BioParasite(self, TheLexicon)
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

    @property
    def graph(self):
        return self.memory_core.graph

    @property
    def cortical_stack(self):
        return self.memory_core.cortical_stack

    def calculate_mass(self, node):
        return self.memory_core.calculate_mass(node)

    """ECOSYSTEM DELEGATION"""

    def run_ecosystem(self, physics: Dict, stamina: float, tick: int) -> List[str]:
        logs = []
        clean_words = physics.get("clean_words", [])
        sugar, lichen_msg = self.lichen.photosynthesize(physics, clean_words, tick)
        if lichen_msg:
            logs.append(lichen_msg)
        infected, parasite_msg = self.parasite.infect(physics, stamina)
        if infected and parasite_msg:
            logs.append(parasite_msg)
        return logs

    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
        return self.memory_core.prune_synapses(scaling_factor, prune_threshold)

    """MEMORY OPERATIONS"""

    def encode(self, clean_words, physics, governor_mode):
        significance = physics.get("voltage", 0.0)
        if governor_mode == "FORGE":
            significance *= 2.0
        elif governor_mode == "LABORATORY":
            significance *= 1.2
        engram = {
            "trigger": clean_words[:3] if clean_words else ["void"],
            "context": governor_mode,
            "significance": significance,
            "timestamp": time.time(),
        }
        if significance > self.memory_core.consolidation_threshold:
            self.memory_core.short_term_buffer.append(engram)
            return True
        return False

    def check_for_resurrection(
        self, input_words: List[str], voltage: float
    ) -> Optional[str]:
        if voltage < 60.0:
            return None
        for word in input_words:
            if word in self.subconscious.index:
                if random.random() < 0.20:
                    memory = self.subconscious.dredge(word)
                    if memory:
                        self.graph[word] = {"edges": memory["edges"], "last_tick": 0}
                        return f"⚠️ FLASHBACK: The word '{word}' clawed its way back from the deep."
        return None

    def bury(
        self,
        clean_words: List[str],
        tick: int,
        resonance=5.0,
        learning_mod=1.0,
        desperation_level=0.0,
    ) -> Tuple[Optional[str], List[str]]:
        if not clean_words:
            return None, []
        valuable = self._filter_valuable_matter(clean_words)
        self.cortical_stack.extend(valuable)
        if len(self.graph) > BoneConfig.MAX_MEMORY_CAPACITY:
            if desperation_level < 0.6:
                return (
                    f"CORTICAL SATURATION: Memory full & Glucose High. Input rejected.",
                    [],
                )
            victim, log_msg = self.memory_core.cannibalize(
                tick, preserve_current=clean_words[0]
            )
            if not victim:
                return f"MEMORY FULL: Cortical Lock. Input rejected.", []
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
                self.memory_core.strengthen_link(
                    current, prev, learning_rate, decay_rate
                )
                self.memory_core.strengthen_link(
                    prev, current, learning_rate, decay_rate
                )
        new_wells = self._detect_new_wells(valuable, tick)
        return log_msg, ([victim] if victim else []) + new_wells

    def _filter_valuable_matter(self, words: List[str]) -> List[str]:
        valuable = []
        for w in words:
            if len(w) <= 4 and w in TheLexicon.SOLVENTS:
                continue
            cat = TheLexicon.get_current_category(w)
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
                        node_data["strata"] = {
                            "birth_tick": tick,
                            "birth_mass": mass,
                            "stability_index": 0.0,
                        }
                        new_wells.append(w)
                    else:
                        age = max(1, tick - node_data["strata"]["birth_tick"])
                        growth = (mass - node_data["strata"]["birth_mass"]) / age
                        node_data["strata"]["growth_rate"] = round(growth, 3)
        return new_wells

    def _check_echo_well(self, node):
        mass = self.memory_core.calculate_mass(node)
        if mass > BoneConfig.GRAVITY_WELL_THRESHOLD * 1.5:
            self.events.log(
                f"{Prisma.VIOLET}GRAVITY WARNING: '{node.upper()}' is becoming a black hole (Mass {int(mass)}).{Prisma.RST}"
            )
            return 2.0
        return 0.0

    """SEED & GENETICS LOGIC"""

    def _load_seeds(self):
        from bone_village import ParadoxSeed

        loaded_seeds = []
        try:
            raw_seeds = TheLore.get("seeds") or []
            for item in raw_seeds:
                q = item.get("question", "Undefined Paradox")
                t = set(item.get("triggers", []))
                seed = ParadoxSeed(q, t)
                loaded_seeds.append(seed)
        except Exception:
            loaded_seeds = [
                ParadoxSeed("Does the mask eat the face?", {"mask", "face", "hide"})
            ]
        return loaded_seeds

    def tend_garden(self, current_words):
        bloom_msg = None
        for seed in self.seeds:
            is_ready = seed.water(current_words)
            if is_ready and not bloom_msg:
                bloom_msg = seed.bloom()
        return bloom_msg

    def _apply_epigenetics(self, data):
        if "config_mutations" not in data:
            return
        self.events.log(
            f"{Prisma.MAG}EPIGENETICS: Auditing ancestral configuration...{Prisma.RST}"
        )
        valid_mutations = 0
        SAFE_MUTATIONS = {
            "STAMINA_REGEN",
            "MAX_DRAG_LIMIT",
            "GEODESIC_STRENGTH",
            "SIGNAL_DRAG_MULTIPLIER",
            "KINETIC_GAIN",
            "TOXIN_WEIGHT",
            "FLASHPOINT_THRESHOLD",
            "MAX_MEMORY_CAPACITY",
            "PRIORITY_LEARNING_RATE",
            "ANVIL_TRIGGER_VOLTAGE",
            "MAX_REPETITION_LIMIT",
            "PHYSICS.WEIGHT_HEAVY",
            "PHYSICS.WEIGHT_KINETIC",
            "PHYSICS.VOLTAGE_FLOOR",
            "PHYSICS.VOLTAGE_MAX",
            "BIO.CORTEX_SENSITIVITY",
            "BIO.ROS_CRITICAL",
            "BIO.DECAY_RATE",
            "BIO.REWARD_MEDIUM",
            "METABOLISM.PHOTOSYNTHESIS_GAIN",
            "METABOLISM.ROS_GENERATION_FACTOR",
            "COUNCIL.FOOTNOTE_CHANCE",
            "COUNCIL.MANIC_VOLTAGE_TRIGGER",
        }

        for key, value in data["config_mutations"].items():
            if key in SAFE_MUTATIONS:
                if _access_config_path(BoneConfig, key, value, set_mode=True):
                    valid_mutations += 1
        if valid_mutations > 0:
            self.events.log(
                f"{Prisma.CYN}   ► Applied {valid_mutations} verified config shifts.{Prisma.RST}"
            )

    """PERSISTENCE & INGESTION"""

    def ingest(self, target_file, current_tick=0):
        data = self.loader.load_spore(target_file)
        if not data:
            self.events.log(f"{Prisma.RED}[MEMORY]: Spore file not found.{Prisma.RST}")
            return None, set(), {}, None

        required_keys = ["meta", "trauma_vector", "core_graph"]
        if not all(k in data for k in required_keys):
            self.events.log(
                f"{Prisma.RED}[MEMORY]: Spore rejected (Missing Structural Keys).{Prisma.RST}"
            )
            return None, set(), {}, None
        self._process_lineage(data)
        self._process_mutations(data)
        self._apply_epigenetics(data)
        if "core_graph" in data:
            self.graph.update(data["core_graph"])
            for node in data["core_graph"]:
                if node in self.graph:
                    self.graph[node]["last_tick"] = current_tick
        return self._extract_legacy_traits(data)

    def _process_lineage(self, data):
        session_source = data.get("session_id", "UNKNOWN_ANCESTOR")
        timestamp = data.get("meta", {}).get("timestamp", 0)
        time_ago = int((time.time() - timestamp) / 3600)
        trauma_summary = {
            k: v for k, v in data.get("trauma_vector", {}).items() if v > 0.1
        }
        mutation_count = sum(len(v) for v in data.get("mutations", {}).values())
        self.lineage_log.append(
            {
                "source": session_source,
                "age_hours": time_ago,
                "trauma": trauma_summary,
                "mutations": mutation_count,
                "loaded_at": time.time(),
            }
        )

    def _process_mutations(self, data):
        if "mutations" in data:
            accepted_count = 0
            for cat, words in data["mutations"].items():
                for w in words:
                    current_cat = TheLexicon.get_current_category(w)
                    if not current_cat or current_cat == "unknown":
                        TheLexicon.teach(w, cat, 0)
                        accepted_count += 1
            if accepted_count > 0:
                self.events.log(
                    f"{Prisma.CYN}[MEMBRANE]: Integrated {accepted_count} mutations.{Prisma.RST}"
                )

    def _extract_legacy_traits(self, data):
        if "joy_legacy" in data and data["joy_legacy"]:
            joy = data["joy_legacy"]
            clade = LiteraryReproduction.JOY_CLADE.get(joy.get("flavor"))
            if clade:
                self.events.log(
                    f"{Prisma.CYN}INHERITED GLORY: {clade['title']}{Prisma.RST}"
                )
                for stat, ancestral_bonus in clade["buff"].items():
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
            data.get("world_atlas", {}),
        )

    def save(
        self,
        health,
        stamina,
        mutations,
        trauma_accum,
        joy_history,
        mitochondria_traits=None,
        antibodies=None,
        soul_data=None,
        continuity=None,
        world_atlas=None,
        village_data=None,
    ):
        base_trauma = (BoneConfig.MAX_HEALTH - health) / BoneConfig.MAX_HEALTH
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}
        top_joy = sorted(joy_history, key=lambda x: x["resonance"], reverse=True)[:3]
        joy_legacy_data = None
        if top_joy:
            joy_legacy_data = {
                "flavor": top_joy[0]["dominant_flavor"],
                "resonance": top_joy[0]["resonance"],
                "timestamp": top_joy[0]["timestamp"],
            }
        core_graph = {}
        for k, data in self.graph.items():
            filtered_edges = {}
            for target, weight in data["edges"].items():
                if weight > 1.0:
                    filtered_edges[target] = round(weight, 2)
            if filtered_edges:
                core_graph[k] = {"edges": filtered_edges, "last_tick": 0}
        temp_meta = {"final_health": health}
        temp_trauma = {k: min(1.0, v) for k, v in trauma_accum.items()}
        future_seed_q = self._generate_future_seed(
            temp_health=health, trauma_vec=temp_trauma
        )
        seed_list = [
            {"q": s.question, "m": s.maturity, "b": s.bloomed}
            for s in self.seeds
            if not s.bloomed
        ]
        seed_list.append({"q": future_seed_q, "m": 0.0, "b": False})
        data = {
            "genome": "BONEAMANITA_15.0.1",
            "session_id": self.session_id,
            "parent_id": self.session_id,
            "parent_id": self.session_id,
            "meta": {
                "timestamp": time.time(),
                "final_health": health,
                "final_stamina": stamina,
            },
            "trauma_vector": final_vector,
            "joy_vectors": top_joy or [],
            "joy_legacy": joy_legacy_data,
            "core_graph": core_graph,
            "mutations": mutations,
            "antibodies": antibodies,
            "mitochondria": mitochondria_traits,
            "soul_legacy": soul_data,
            "continuity": continuity,
            "world_atlas": world_atlas or {},
            "village_data": village_data,
            "seeds": seed_list,
            "fossils": list(self.fossils),
        }

        return self.loader.save_spore(self.filename, data)

    def _generate_future_seed(self, temp_health, trauma_vec) -> str:
        condition = "BALANCED"
        max_trauma = max(trauma_vec, key=trauma_vec.get) if trauma_vec else "NONE"
        if trauma_vec.get(max_trauma, 0) > 0.6 or temp_health < 30:
            condition = "HIGH_TRAUMA"
        seeds = {"HIGH_TRAUMA": "Recovery", "BALANCED": "Growth"}
        return seeds.get(condition, "Hope")

    def cleanup_old_sessions(self, limbo_layer=None):
        files = self.loader.list_spores()
        removed = 0
        max_files = 25
        max_age = 86400
        for i, (path, age, fname) in enumerate(files):
            file_age = time.time() - age
            if i >= max_files or file_age > max_age:
                try:
                    if limbo_layer:
                        limbo_layer.absorb_dead_timeline(path)
                    if self.loader.delete_spore(path):
                        removed += 1
                except (OSError, AttributeError):
                    pass
        if removed:
            self.events.log(
                f"{Prisma.GRY}[TIME MENDER]: Pruned {removed} dead timelines.{Prisma.RST}"
            )

    def report_status(self):
        return len(self.graph)

    def autoload_last_spore(self):
        files = self.loader.list_spores()
        if not files:
            self.events.log(
                f"{Prisma.GRY}[GENETICS]: No ancestors found. Genesis Bloom.{Prisma.RST}"
            )
            return None
        candidates = [f for f in files if self.session_id not in f[0]]
        if candidates:
            return self.ingest(candidates[0][0])
        return None


"""ECOSYSTEM & EVOLUTION"""


class ImmuneMycelium:
    def __init__(self):
        self.active_antibodies = set()
        self.PHONETICS = {
            "PLOSIVE": set("bdgkpt"),
            "FRICATIVE": set("fthszsh"),
            "LIQUID": set("lr"),
            "NASAL": set("mn"),
        }
        self.ROOTS = {
            "HEAVY": (
                "lith",
                "ferr",
                "petr",
                "dens",
                "grav",
                "struct",
                "base",
                "fund",
                "mound",
            ),
            "KINETIC": ("mot", "mov", "ject", "tract", "pel", "crat", "dynam", "flux"),
        }
        self.name = "MYCELIUM"
        self.color = Prisma.CYN
        self.archetypes = {"constructive", "kinetic", "abstract", "code", "system"}

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        hits = sum(1 for w in clean_words if w in self.archetypes)
        score = (hits / max(1, len(clean_words))) * 10.0
        comment = "Scanning for structural integrity..."
        if score > 2.0:
            comment = "The pattern holds. Integration probable."
        return score, comment

    def assay(self, word, _context, _rep_val, _phys, _pulse):
        w = word.lower()
        clean_len = len(w)
        if clean_len < 3:
            return None, ""
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


class BioParasite:
    def __init__(self, memory_ref, lexicon_ref):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.spores_deployed = 0
        self.MAX_SPORES = 8
        self.name = "PARASITE"
        self.color = Prisma.RED
        self.archetypes = {
            "antigen",
            "toxin",
            "heavy",
            "meat",
            "void",
            "static",
            "rot",
            "decay",
        }

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        hits = sum(1 for w in clean_words if w in self.archetypes)
        score = (hits / max(1, len(clean_words))) * 10.0
        comment = "..."
        if score > 3.0:
            comment = "Delicious. The entropy is sweet."
        elif score > 1.0:
            comment = "I smell rust."
        elif voltage > 15.0:
            comment = "Stop vibrating. Be still and rot."
        elif voltage < 5.0:
            comment = "Finally. Silence."
        return score, comment

    def infect(self, physics_packet, stamina):
        psi = physics_packet.get("psi", 0.0)
        if stamina > 40.0 and psi < 0.6:
            return False, None
        if self.spores_deployed >= self.MAX_SPORES:
            if random.random() < 0.2:
                self.spores_deployed = max(0, self.spores_deployed - 1)
            return False, None
        graph = self.mem.graph
        heavy_candidates = [w for w in graph if w in self.lex.get("heavy")]
        abstract_candidates = [w for w in graph if w in self.lex.get("abstract")]
        if not heavy_candidates or not abstract_candidates:
            return False, None
        host = random.choice(heavy_candidates)
        parasite = random.choice(abstract_candidates)
        if parasite in graph[host]["edges"]:
            return False, None
        is_metaphor = psi > 0.7
        weight = 8.88
        graph[host]["edges"][parasite] = weight
        if parasite not in graph:
            graph[parasite] = {"edges": {}, "last_tick": 0}
        graph[parasite]["edges"][host] = weight
        self.spores_deployed += 1
        if is_metaphor:
            return True, (
                f"{Prisma.CYN}✨ SYNAPSE SPARK: Your mind bridges '{host.upper()}' and '{parasite.upper()}'.\n"
                f"   A new metaphor is born. The map folds.{Prisma.RST}"
            )
        else:
            return True, (
                f"{Prisma.VIOLET}🍄 INTRUSIVE THOUGHT: Exhaustion logic links '{host.upper()}' <-> '{parasite.upper()}'.\n"
                f"   This makes no sense, yet there it is. 'Some things just happen.'{Prisma.RST}"
            )


class BioLichen:
    def __init__(self):
        self.name = "LICHEN"
        self.color = Prisma.GRN
        self.archetypes = {
            "photo",
            "play",
            "sacred",
            "social",
            "solar",
            "vital",
            "bloom",
            "grow",
        }

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        hits = sum(1 for w in clean_words if w in self.archetypes)
        score = (hits / max(1, len(clean_words))) * 10.0
        comment = "..."
        if score > 3.0:
            comment = "Yes! The roots are drinking deep."
        elif score > 1.0:
            comment = "We see the light."
        elif voltage > 18.0:
            comment = "Too hot! You'll scorch the leaves!"
        elif voltage < 2.0:
            comment = "It is cold... we are sleeping."
        return score, comment

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
            source_str = f" via '{random.choice(light_words)}'" if light_words else ""
            msgs.append(f"{Prisma.GRN}PHOTOSYNTHESIS{source_str} (+{s}){Prisma.RST}")
        if sugar > 0:
            heavy_words = [w for w in clean_words if w in TheLexicon.get("heavy")]
            if heavy_words:
                h_word = random.choice(heavy_words)
                TheLexicon.teach(h_word, "photo", tick_count)
                msgs.append(
                    f"{Prisma.MAG}SUBLIMATION: '{h_word}' has become Light.{Prisma.RST}"
                )
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
        if isinstance(physics_container, dict):
            return physics_container.get("counts", {})
        return {}

    @staticmethod
    def mutate_config(current_config):
        mutations = {}
        MUTATION_TABLE = [
            ("MAX_DRAG_LIMIT", 1.0, 20.0, 0.3),
            ("TOXIN_WEIGHT", 0.1, 5.0, 0.3),
            ("MAX_HEALTH", 50.0, 500.0, 0.1),
            ("PHYSICS.VOLTAGE_MAX", 10.0, 100.0, 0.2),
            ("BIO.REWARD_MEDIUM", 0.01, 1.0, 0.2),
            ("COUNCIL.MANIC_VOLTAGE_TRIGGER", 10.0, 50.0, 0.1),
        ]
        for key, min_v, max_v, chance in MUTATION_TABLE:
            if random.random() < chance:
                current_val = LiteraryReproduction._resolve_config_value(
                    current_config, key
                )
                if current_val is not None:
                    drift = random.uniform(0.9, 1.1)
                    mutations[key] = max(min_v, min(max_v, current_val * drift))
        return mutations

    @staticmethod
    def _resolve_config_value(root_config, path):
        return _access_config_path(root_config, path, set_mode=False)

    @staticmethod
    def mitosis(parent_id, bio_state, physics):
        counts = LiteraryReproduction._extract_counts(physics)
        dominant = max(counts, key=counts.get) if counts else "VOID"
        mutation_data = LiteraryReproduction.MUTATIONS.get(
            dominant.upper(), {"trait": "NEUTRAL", "mod": {}, "lexicon": []}
        )
        child_id = f"{parent_id}_({mutation_data['trait']})"
        config_mutations = LiteraryReproduction.mutate_config(BoneConfig)
        config_mutations.update(mutation_data["mod"])
        lexicon_mutations = {dominant.lower(): mutation_data.get("lexicon", [])}
        trauma_vec = bio_state.get("trauma_vector", {})
        child_genome = {
            "source": "MITOSIS",
            "parent_a": parent_id,
            "parent_b": None,
            "lexicon_mutations": lexicon_mutations,
            "config_mutations": config_mutations,
            "dominant_flavor": dominant,
            "trauma_inheritance": trauma_vec,
        }
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
            "inherited_enzymes": child_enzymes,
        }
        return child_id, child_genome

    def attempt_reproduction(
        self, engine_ref, mode="MITOSIS", target_spore=None
    ) -> Tuple[str, Dict]:
        mem = engine_ref.mind.mem
        bio_state = {
            "trauma_vector": engine_ref.trauma_accum,
            "mito": engine_ref.bio.mito,
        }
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