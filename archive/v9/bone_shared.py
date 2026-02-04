# bone_shared.py - The Shared Lineage

import re, random, string, unicodedata, json, os, time
from dataclasses import field, dataclass
from typing import Dict, Optional, List, Any, Tuple, Type
from bone_data import LEXICON, DEATH, GENETICS, SEEDS

class Prisma:
    RST = "\033[0m"
    RED = "\033[31m"
    GRN = "\033[32m"
    YEL = "\033[33m"
    BLU = "\033[34m"
    MAG = "\033[35m"
    CYN = "\033[36m"
    WHT = "\033[97m"
    GRY = "\033[90m"
    INDIGO = "\033[34;1m"
    OCHRE = "\033[33;2m"
    VIOLET = "\033[35;2m"
    SLATE = "\033[30;1m"

    @classmethod
    def paint(cls, text, color_key="0"):
        color_map = {
            "R": cls.RED, "G": cls.GRN, "Y": cls.YEL, "B": cls.BLU,
            "M": cls.MAG, "C": cls.CYN, "W": cls.WHT, "0": cls.GRY,
            "I": cls.INDIGO, "O": cls.OCHRE, "V": cls.VIOLET
        }
        code = color_map.get(color_key.upper(), cls.WHT)
        return f"{code}{text}{cls.RST}"

class BoneConfig:
    MAX_HEALTH = 100.0
    MAX_STAMINA = 100.0
    STAMINA_REGEN = 1.0
    MAX_ATP = 200.0
    MAX_DRAG_LIMIT = 5.0
    SHAPLEY_MASS_THRESHOLD = 5.0
    GRAVITY_WELL_THRESHOLD = 15.0
    GEODESIC_STRENGTH = 10.0
    BASE_IGNITION_THRESHOLD = 0.5
    MAX_REPETITION_LIMIT = 0.8
    BOREDOM_THRESHOLD = 10.0
    ANVIL_TRIGGER_VOLTAGE = 10.0
    MIN_DENSITY_THRESHOLD = 0.3
    LAGRANGE_TOLERANCE = 2.0
    FLASHPOINT_THRESHOLD = 10.0
    SIGNAL_DRAG_MULTIPLIER = 1.0
    KINETIC_GAIN = 1.0
    CRITICAL_ROS_LIMIT = 100.0
    MAX_MEMORY_CAPACITY = 100
    ZONE_THRESHOLDS = {"LABORATORY": 1.5, "COURTYARD": 0.8}
    BETA_EPSILON = 0.01
    TOXIN_WEIGHT = 1.0
    ANTIGENS = ["basically", "actually", "literally", "utilize"]
    TRAUMA_VECTOR = {"THERMAL":0, "CRYO":0, "SEPTIC":0, "BARIC":0}
    VERBOSE_LOGGING = True
    BASE_METABOLIC_RATE = 2.0

    @staticmethod
    def check_pareidolia(words):
        triggers = {"face", "ghost", "jesus", "cloud", "voice", "eyes"}
        hits = [w for w in words if w in triggers]
        if hits:
            return True, f"{Prisma.VIOLET}PAREIDOLIA: You see a {hits[0].upper()} in the noise. It blinks.{Prisma.RST}"
        return False, None

# --- LEXICON LOGIC ---

class LexiconStore:
    def __init__(self):
        self.categories = {
            "heavy", "kinetic", "explosive", "constructive", "abstract",
            "photo", "aerobic", "thermal", "cryo", "suburban", "play",
            "sacred", "buffer", "antigen", "diversion", "meat", "gradient_stop"
        }
        self.VOCAB = {}
        self.LEARNED_VOCAB = {}
        self.USER_FLAGGED_BIAS = set()
        self.ANTIGEN_REPLACEMENTS = {}
        self.SOLVENTS = set()
        self._ENGINE = None

    def load_vocabulary(self):
        data = LEXICON
        self.SOLVENTS = set(data.get("solvents", []))
        self.ANTIGEN_REPLACEMENTS = data.get("antigen_replacements", {})
        for cat, words in data.items():
            if cat in self.categories or cat in ["refusal_guru", "cursed"]:
                self.VOCAB[cat] = set(words)
        if "antigen" not in self.VOCAB and "antigen" in data:
            self.VOCAB["antigen"] = set(data["antigen"])

    def set_engine(self, engine_ref): self._ENGINE = engine_ref

    def get_raw(self, category):
        base = self.VOCAB.get(category, set())
        learned = set(self.LEARNED_VOCAB.get(category, {}).keys())
        if category == "suburban": return (base | learned) - self.USER_FLAGGED_BIAS
        return base | learned

    def teach(self, word, category, tick):
        if category not in self.LEARNED_VOCAB: self.LEARNED_VOCAB[category] = {}
        self.LEARNED_VOCAB[category][word.lower()] = tick
        return True

    def atrophy(self, current_tick, max_age=100):
        rotted = []
        for cat, words in self.LEARNED_VOCAB.items():
            for w in list(words.keys()):
                if (current_tick - words[w]) > max_age:
                    del words[w]; rotted.append(w)
        return rotted

class SemanticsBioassay:
    def __init__(self, store_ref):
        self.store = store_ref
        self._TRANSLATOR = str.maketrans(string.punctuation, " " * len(string.punctuation))
        self.PHONETICS = {
            "PLOSIVE": set("bdgkpt"), "FRICATIVE": set("fthszsh"),
            "LIQUID": set("lr"), "NASAL": set("mn"),
            "VOWELS": set("aeiouy")
        }
        self.ROOTS = {
            "HEAVY": ("lith", "ferr", "petr", "dens", "grav", "struct", "base", "fund", "mound"),
            "KINETIC": ("mot", "mov", "ject", "tract", "pel", "crat", "dynam", "flux"),
            "ABSTRACT": ("tion", "ism", "ence", "ance", "ity", "ology", "ness", "ment", "idea"),
            "SUBURBAN": ("norm", "comm", "stand", "pol", "reg", "mod"),
            "VITAL": ("viv", "vita", "spir", "anim", "bio", "luc", "lum", "phot", "phon", "surg", "bloom")
        }

    def clean(self, text):
        if not text: return []
        normalized = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        cleaned_text = normalized.translate(self._TRANSLATOR).lower()
        words = cleaned_text.split()
        return [w for w in words if w.strip() and w not in self.store.USER_FLAGGED_BIAS]

    def assay(self, word):
        w = word.lower()
        clean_len = len(w)
        if clean_len < 3: return None, 0.0
        for cat, roots in self.ROOTS.items():
            for r in roots:
                if r in w: return cat.lower(), 0.8
        plosive = sum(1 for c in w if c in self.PHONETICS["PLOSIVE"])
        liquid = sum(1 for c in w if c in self.PHONETICS["LIQUID"])
        nasal = sum(1 for c in w if c in self.PHONETICS["NASAL"])
        vowel = sum(1 for c in w if c in self.PHONETICS["VOWELS"])
        density_score = (plosive * 1.5) + (nasal * 0.8)
        flow_score = liquid + sum(1 for c in w if c in self.PHONETICS["FRICATIVE"])
        vitality_score = (vowel * 1.2) + (flow_score * 0.8)
        compression_mod = 1.0 if clean_len > 5 else 1.5
        final_density = (density_score / clean_len) * compression_mod
        final_vitality = (vitality_score / clean_len) * compression_mod
        if final_density > 0.55: return "heavy", round(final_density, 2)
        if final_vitality > 0.6: return "play", round(final_vitality, 2)
        if (flow_score / clean_len) > 0.6: return "kinetic", 0.5
        return None, 0.0

    def measure_viscosity(self, word):
        if not word: return 0.0
        consonants = sum(1 for c in word if c.lower() not in "aeiou")
        return (consonants / len(word)) if len(word) > 0 else 0.0

    def measure_turbulence(self, words):
        if len(words) < 2: return 0.0
        lengths = [len(w) for w in words]
        mean = sum(lengths) / len(lengths)
        variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        return min(1.0, (variance ** 0.5) / 5.0)

    def walk_gradient(self, text):
        clean_words = self.clean(text)
        structure_path = []
        high_entropy = {"thermal", "cryo", "explosive", "sacred", "play", "cursed"}
        for w in clean_words:
            is_noise = False
            for cat in high_entropy:
                if w in self.store.get_raw(cat):
                    is_noise = True; break
            if not is_noise or w in self.store.get_raw("heavy") or w in self.store.SOLVENTS:
                structure_path.append(w)
        return " ".join(structure_path) if structure_path else "null"

class GlobalLexiconFacade:
    _INITIALIZED = False
    _STORE = None
    _ENGINE = None
    ANTIGEN_REGEX = None
    SOLVENTS = set()

    @classmethod
    def initialize(cls):
        if cls._INITIALIZED: return
        cls._STORE = LexiconStore()
        cls._STORE.load_vocabulary()
        cls._ENGINE = SemanticsBioassay(cls._STORE)
        cls._STORE.set_engine(cls._ENGINE)
        cls.compile_antigens()
        cls.SOLVENTS = cls._STORE.SOLVENTS
        cls._INITIALIZED = True

    @classmethod
    def get(cls, category): return cls._STORE.get_raw(category)
    @classmethod
    def teach(cls, word, category, tick): return cls._STORE.teach(word, category, tick)
    @classmethod
    def clean(cls, text): return cls._ENGINE.clean(text)
    @classmethod
    def taste(cls, word): return cls._ENGINE.assay(word)
    @classmethod
    def measure_viscosity(cls, word): return cls._ENGINE.measure_viscosity(word)
    @classmethod
    def harvest(cls, category):
        candidates = list(cls._STORE.get_raw(category))
        return random.choice(candidates) if candidates else "void"
    @classmethod
    def get_turbulence(cls, words): return cls._ENGINE.measure_turbulence(words)
    @classmethod
    def get_current_category(cls, word):
        for cat, vocab in cls._STORE.LEARNED_VOCAB.items():
            if word.lower() in vocab: return cat
        for cat, vocab in cls._STORE.VOCAB.items():
            if word.lower() in vocab: return cat
        return None
    @classmethod
    def compile_antigens(cls):
        antigens = cls._STORE.get_raw("antigen")
        if antigens:
            pattern = "|".join(map(re.escape, antigens))
            cls.ANTIGEN_REGEX = re.compile(fr"\b({pattern})\b", re.IGNORECASE)
        else: cls.ANTIGEN_REGEX = None
    @classmethod
    def learn_antigen(cls, t, r):
        if "antigen" not in cls._STORE.VOCAB: cls._STORE.VOCAB["antigen"] = set()
        cls._STORE.VOCAB["antigen"].add(t.lower())
        if r: cls._STORE.ANTIGEN_REPLACEMENTS[t.lower()] = r
        cls.compile_antigens()
        return True
    @classmethod
    def walk_gradient(cls, text): return cls._ENGINE.walk_gradient(text)
    @classmethod
    def atrophy(cls, tick, max_age): return cls._STORE.atrophy(tick, max_age)

GlobalLexiconFacade.initialize()
TheLexicon = GlobalLexiconFacade

# --- SPORE & MEMORY LOGIC (Moved from Main) ---

class SporeCasing:
    def __init__(self, session_id, graph, mutations, trauma, joy_vectors):
        self.genome = "BONEAMANITA_9.8.2"
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
            path = os.path.join(self.directory, filename)
        else:
            path = filename
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            return path
        except IOError:
            return None

    def load_spore(self, filepath):
        path = os.path.join(self.directory, filepath) if not filepath.startswith(self.directory) else filepath
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
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

class LiteraryReproduction:
    MUTATIONS = {}
    JOY_CLADE = {}

    @classmethod
    def load_genetics(cls):
        try:
            cls.MUTATIONS = GENETICS.get("MUTATIONS", {})
            cls.JOY_CLADE = GENETICS.get("JOY_CLADE", {})
        except ImportError:
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
        return mutations

    @staticmethod
    def mitosis(parent_id, bio_state, physics, memory):
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

    # Needs to be called with an engine_ref (or suitable parts) to work
    def attempt_reproduction(self, engine_ref, mode="MITOSIS", target_spore=None) -> Tuple[str, Dict]:
        mem = engine_ref.mind.mem
        phys = engine_ref.phys.tension.last_physics_packet
        genome = {}
        if mode == "MITOSIS":
            bio_state = {"trauma_vector": engine_ref.trauma_accum}
            child_id, genome = self.mitosis(mem.session_id, bio_state, phys, mem)
            log_msg = [f"   ► CHILD SPAWNED: {Prisma.WHT}{child_id}{Prisma.RST}"]
            log_msg.append(f"   ► TRAIT: {genome['mutations']}")
        elif mode == "CROSSOVER":
            if not target_spore:
                return f"{Prisma.RED}FERTILITY ERROR: No partner found.{Prisma.RST}", {}
            current_bio = {"trauma_vector": engine_ref.trauma_accum, "mito": engine_ref.bio.mito}
            child_id, genome = self.crossover(mem.session_id, current_bio, target_spore)
            if not child_id:
                return f"{Prisma.RED}CROSSOVER FAILED: {genome}{Prisma.RST}", {}
            log_msg = [f"   HYBRID SPAWNED: {Prisma.WHT}{child_id}{Prisma.RST}"]
        full_spore_data = {
            "session_id": child_id,
            "meta": {
                "timestamp": time.time(),
                "final_health": engine_ref.health,
                "final_stamina": engine_ref.stamina
            },
            "trauma_vector": genome.get("trauma_inheritance", {}),
            "config_mutations": genome.get("config_mutations", {}),
            "mitochondria": {"enzymes": list(genome.get("inherited_enzymes", []))},
            "core_graph": mem.graph,
            "antibodies": list(engine_ref.bio.immune.active_antibodies)
        }
        filename = f"{child_id}.json"
        saved_path = mem.loader.save_spore(filename, full_spore_data)
        if saved_path:
            log_msg.append(f"   {Prisma.GRN}SAVED: {saved_path}{Prisma.RST}")
        return "\n".join(log_msg), genome.get("mutations", {})

# --- MISC SHARED UTILS ---

class TheTinkerer:
    def __init__(self, gordon_ref, events_ref):
        self.gordon = gordon_ref
        self.events = events_ref
        self.tool_confidence = {}

    def audit_tool_use(self, physics_packet, inventory_list):
        if isinstance(physics_packet, dict):
            voltage = physics_packet.get("voltage", 0.0)
            drag = physics_packet.get("narrative_drag", 0.0)
        else:
            voltage = physics_packet.voltage
            drag = physics_packet.narrative_drag
        is_forge = (voltage > 12.0) or (drag < 2.0)
        is_mud = (voltage < 5.0) and (drag > 6.0)
        learning_rate = 0.05
        rust_rate = 0.02
        items_to_shed = []
        for item_name in inventory_list:
            if item_name not in self.tool_confidence:
                self.tool_confidence[item_name] = 1.0
            current = self.tool_confidence[item_name]
            if is_forge:
                self.tool_confidence[item_name] = min(2.0, current + learning_rate)
                if random.random() < 0.1:
                    self.events.log(f"{Prisma.CYN}[TINKER]: {item_name} is tempering in the heat (Confidence {self.tool_confidence[item_name]:.2f}).{Prisma.RST}", "SYS")
            elif is_mud:
                self.tool_confidence[item_name] = max(0.0, current - rust_rate)
                if random.random() < 0.1:
                    self.events.log(f"{Prisma.OCHRE}[TINKER]: {item_name} is rusting in the damp.{Prisma.RST}", "SYS")
            if self.tool_confidence[item_name] <= 0.1:
                items_to_shed.append(item_name)
        for item in items_to_shed:
            if item in inventory_list:
                inventory_list.remove(item)
            if item in self.tool_confidence:
                del self.tool_confidence[item]
            self.events.log(f"{Prisma.GRY}[TINKER]: {item} has rusted away. Gordon put it in the Shed.{Prisma.RST}", "SYS")
        for item_name in inventory_list:
            if item_name in self.tool_confidence:
                self._mutate_tool_stats(item_name, self.tool_confidence[item_name])

    def _mutate_tool_stats(self, item_name, confidence):
        item_data = self.gordon.ITEM_REGISTRY.get(item_name)
        if not item_data:
            return
        if "value" in item_data:
            if "base_value" not in item_data:
                item_data["base_value"] = item_data["value"]
            new_value = item_data["base_value"] * confidence
            item_data["value"] = round(new_value, 2)
        if confidence > 1.5 and "LUCKY" not in item_data.get("passive_traits", []):
            if "passive_traits" not in item_data: item_data["passive_traits"] = []
            item_data["passive_traits"].append("LUCKY")
            self.events.log(f"{Prisma.CYN}✨ EVOLUTION: {item_name} gained trait [LUCKY].{Prisma.RST}", "TINKER")

    def save_state(self):
        return self.tool_confidence

    def load_state(self, data):
        if data:
            self.tool_confidence = data
            for item, conf in self.tool_confidence.items():
                self._mutate_tool_stats(item, conf)

class ParadoxSeed:
    def __init__(self, question, triggers):
        self.question = question
        self.triggers = {t.lower() for t in triggers}
        self.maturity = 0.0
        self.bloomed = False

    def water(self, current_words):
        if self.bloomed: return False
        overlap = sum(1 for w in current_words if w in self.triggers)
        if overlap > 0:
            self.maturity += (overlap * 0.1)
            if self.maturity >= 1.0:
                self.bloomed = True
                return True
        return False

    def bloom(self):
        return f"{Prisma.GRN}🌸 BLOOM: The seed '{self.question}' has opened. A new truth takes root.{Prisma.RST}"

class DeathGen:
    PREFIXES = []
    CAUSES = {}
    VERDICTS = {}

    @classmethod
    def load_protocols(cls):
        cls.PREFIXES = DEATH.get("PREFIXES", ["System Halt."])
        cls.CAUSES = DEATH.get("CAUSES", {})
        cls.VERDICTS = DEATH.get("VERDICTS", {})

    @staticmethod
    def eulogy(physics, mito_state):
        cause = "UNKNOWN"
        if mito_state.atp_pool <= 0: cause = "STARVATION"
        elif physics["counts"]["toxin"] > 3: cause = "TOXICITY"
        elif physics["narrative_drag"] > 8.0: cause = "BOREDOM"
        flavor_text = random.choice(DeathGen.CAUSES.get(cause, ["System Error"]))
        prefix = random.choice(DeathGen.PREFIXES)
        verdict = "You vanished."
        if physics["voltage"] > 15.0: verdict = random.choice(DeathGen.VERDICTS.get("HEAVY", []))
        elif physics["voltage"] < 2.0: verdict = random.choice(DeathGen.VERDICTS.get("LIGHT", []))
        return f"{prefix} Cause of Death: {flavor_text}. {verdict}"

class TheCartographer:
    GRID_SIZE = 7

    @staticmethod
    def _get_tile(x, y, center, physics, vectors):
        dist_from_center = ((x - center)**2 + (y - center)**2) ** 0.5
        entropy_threshold = 3.0 - (vectors.get("ENT", 0.5) * 2.0)
        if dist_from_center > entropy_threshold:
            return f"{Prisma.GRY} . {Prisma.RST}"
        structure_noise = (x * 3 + y * 7) % 10 / 10.0
        if structure_noise < vectors.get("STR", 0.0):
            return f"{Prisma.OCHRE} ▲ {Prisma.RST}"
        if vectors.get("VEL", 0) > 0.6:
            if x == center or y == center:
                return f"{Prisma.CYN} = {Prisma.RST}"
        if vectors.get("BET", 0) > 0.5:
            return f"{Prisma.SLATE} ∷ {Prisma.RST}"
        return "   "

    @classmethod
    def weave(cls, _text, _graph, _bio_metrics, _limbo, physics=None):
        if not physics:
            return "MAP ERROR: No Physics Data", []
        vectors = physics.get("vector", {})
        center = cls.GRID_SIZE // 2
        rows = []
        border = f"{Prisma.GRY}+{'-' * (cls.GRID_SIZE * 3)}+{Prisma.RST}"
        rows.append(border)
        anchors = []
        for y in range(cls.GRID_SIZE):
            row_str = f"{Prisma.GRY}|{Prisma.RST}"
            for x in range(cls.GRID_SIZE):
                if x == center and y == center:
                    row_str += f"{Prisma.WHT} @ {Prisma.RST}"
                else:
                    row_str += cls._get_tile(x, y, center, physics, vectors)
            row_str += f"{Prisma.GRY}|{Prisma.RST}"
            rows.append(row_str)
        rows.append(border)
        if vectors.get("STR", 0) > 0.7: anchors.append("MOUNTAIN")
        if vectors.get("ENT", 0) > 0.7: anchors.append("VOID_EDGE")
        if vectors.get("VEL", 0) > 0.7: anchors.append("HIGHWAY")
        map_display = "\n".join(rows)
        return map_display, anchors

    @staticmethod
    def detect_voids(packet):
        return [w for w in packet["clean_words"] if w in TheLexicon.get("abstract")]

    @staticmethod
    def spin_web(_graph, inventory, _gordon):
        if "TIME_BRACELET" in inventory:
            return True, "WEB SPUN: The bracelet helps you tie the knots."
        return False, "WEAVE FAILED: You lack the tools to bind these concepts."

@dataclass
class CycleContext:
    input_text: str
    clean_words: List[str] = field(default_factory=list)
    physics: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    is_alive: bool = True
    refusal_triggered: bool = False
    refusal_packet: Optional[Dict] = None
    is_bureaucratic: bool = False
    bio_result: Dict = field(default_factory=dict)
    world_state: Dict = field(default_factory=dict)
    mind_state: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def log(self, message: str):
        self.logs.append(message)

class EventBus:
    def __init__(self):
        self.buffer = []

    def log(self, text: str, category: str = "SYSTEM"):
        self.buffer.append({
            "text": text,
            "category": category,
            "timestamp": time.time()
        })

    def flush(self) -> List[Dict]:
        logs = list(self.buffer)
        self.buffer.clear()
        return logs

@dataclass
class PhysicsPacket:
    voltage: float = 0.0
    narrative_drag: float = 0.0
    repetition: float = 0.0
    clean_words: List[str] = field(default_factory=list)
    counts: Dict[str, int] = field(default_factory=dict)
    vector: Dict[str, float] = field(default_factory=dict)
    psi: float = 0.0
    kappa: float = 0.0
    beta_index: float = 1.0
    gamma: float = 0.0
    turbulence: float = 0.0
    flow_state: str = "LAMINAR"
    zone: str = "COURTYARD"
    zone_color: str = "OCHRE"
    truth_ratio: float = 0.0
    raw_text: str = ""
    antigens: int = 0
    perfection_streak: int = 0
    avg_viscosity: float = 0.0
    E: float = 0.0
    B: float = 0.0
    humility_flag: bool = False
    system_surge_event: bool = False
    pain_signal: float = 0.0

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def update(self, data: Dict):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        valid_keys = cls.__annotations__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__annotations__}

class ZoneInertia:
    def __init__(self, inertia=0.7, min_dwell=2):
        self.inertia = inertia
        self.min_dwell = min_dwell
        self.current_zone = "COURTYARD"
        self.dwell_counter = 0
        self.last_vector = None

    def stabilize(self, proposed_zone, physics, cosmic_state):
        beta = physics.get("beta_index", 1.0)
        truth = physics.get("truth_ratio", 0.5)
        grav_pull = 1.0 if cosmic_state[0] != "VOID_DRIFT" else 0.0
        current_vec = (beta, truth, grav_pull)
        self.dwell_counter += 1
        if proposed_zone == self.current_zone:
            self.dwell_counter = 0
            self.last_vector = current_vec
            return proposed_zone
        if self.dwell_counter < self.min_dwell:
            return self.current_zone
        similarity = 0.0
        if self.last_vector:
            dist = sum((a - b) ** 2 for a, b in zip(current_vec, self.last_vector)) ** 0.5
            similarity = max(0.0, 1.0 - (dist / 2.0))
        change_probability = (1.0 - self.inertia) * (1.0 - similarity)
        if proposed_zone in ["AERIE", "THE_FORGE"]:
            change_probability += 0.2
        if random.random() < change_probability:
            self.current_zone = proposed_zone
            self.dwell_counter = 0
            self.last_vector = current_vec
        return self.current_zone

    def override_cosmic_drag(self, cosmic_drag_penalty, current_zone):
        if current_zone == "AERIE" and cosmic_drag_penalty > 0:
            return cosmic_drag_penalty * 0.3
        return cosmic_drag_penalty

class TheAlmanac:
    def __init__(self):
        self.forecasts = {
            "HIGH_VOLTAGE": [
                "The wire is hot. Write immediately, without editing.",
                "Burn the fuel before it explodes. Speed is your friend.",
                "Do not seek structure. Seek impact."
            ],
            "HIGH_DRAG": [
                "The mud is deep. Stop trying to run.",
                "Focus on texture. Describe the weight of things.",
                "Slow down. The obstacle *is* the path."
            ],
            "HIGH_ENTROPY": [
                "The center is not holding. Find one true sentence.",
                "Simplify. Cut the adjectives. Locate the noun.",
                "Anchor yourself. Pick a physical object and describe it."
            ],
            "HIGH_TRAUMA": [
                "The wound is open. Treat it with care.",
                "Write what hurts, but write it in the third person.",
                "Use the pain as fuel, but filter it through the lens."
            ],
            "BALANCED": [
                "The Garden is growing. Tend to the edges.",
                "Structure and flow are aligned. Build something tall.",
                "You are in the zone. Maintain the rhythm."
            ]
        }

    def diagnose_condition(self, session_data: dict) -> Tuple[str, str]:
        meta = session_data.get("meta", {})
        trauma = session_data.get("trauma_vector", {})
        final_health = meta.get("final_health", 0)
        final_stamina = meta.get("final_stamina", 0)

        condition = "BALANCED"
        advice = "System nominal."

        max_trauma = max(trauma, key=trauma.get) if trauma else "NONE"
        trauma_val = trauma.get(max_trauma, 0)

        if final_health < 30 or trauma_val > 0.6:
            condition = "HIGH_TRAUMA"
            advice = f"Warning: High levels of {max_trauma} residue detected."
        elif final_stamina < 20:
            condition = "HIGH_DRAG"
            advice = "System exhaustion imminent. Semantic drag is heavy."
        elif meta.get("avg_voltage", 0) > 12.0:
            condition = "HIGH_VOLTAGE"
            advice = "The capacitor is overcharged."

        return condition, advice

    def get_seed(self, condition):
        strategies = {
            "HIGH_VOLTAGE": "What if you whispered instead of screamed?",
            "HIGH_DRAG": "Honor the error as a hidden intention.",
            "HIGH_ENTROPY": "Repetition is a form of change.",
            "HIGH_TRAUMA": "Turn it into a wallpaper pattern.",
            "BALANCED": "Discard the first idea. Trust the third."
        }
        return strategies.get(condition, "Look closely at the most boring thing in the room.")

    def compile_forecast(self, session_data: dict) -> str:
        condition, advice = self.diagnose_condition(session_data)
        forecast_text = random.choice(self.forecasts.get(condition, self.forecasts["BALANCED"]))
        seed_text = self.get_seed(condition)

        border = f"{Prisma.OCHRE}{'='*40}{Prisma.RST}"
        report = [
            "\n",
            border,
            f"{Prisma.CYN}   THE ALMANAC: CREATIVE WEATHER REPORT{Prisma.RST}",
            border,
            f"Condition: {Prisma.WHT}{condition}{Prisma.RST}",
            f"Observation: {Prisma.GRY}{advice}{Prisma.RST}",
            f"{Prisma.SLATE}---{Prisma.RST}",
            f"{Prisma.MAG}PRESCRIPTION:{Prisma.RST}",
            f"   {forecast_text}",
            "",
            f"{Prisma.GRN}Seed for Next Session:{Prisma.RST}",
            f"   {seed_text}",
            border,
            "\n"
        ]
        return "\n".join(report)
