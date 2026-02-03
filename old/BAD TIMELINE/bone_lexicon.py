""" bone_lexicon.py - The Global Dictionary
 'Words are things, I'm convinced.' - Maya Angelou """

import json, random, re, string, time, unicodedata, os
from typing import Tuple, Dict, Set, Optional, List
from bone_bus import BoneConfig, Prisma
from bone_data import TheLore
from functools import lru_cache

class LexiconStore:
    HIVE_FILENAME = "cortex_hive.json"
    def __init__(self):
        self.categories = {
            "heavy", "kinetic", "explosive", "constructive", "abstract",
            "photo", "aerobic", "thermal", "cryo", "suburban", "play",
            "sacred", "buffer", "antigen", "diversion", "meat", "gradient_stop"}
        self.VOCAB: Dict[str, Set[str]] = {k: set() for k in self.categories}
        self.LEARNED_VOCAB: Dict[str, Dict[str, int]] = {}
        self.USER_FLAGGED_BIAS = set()
        self.ANTIGEN_REPLACEMENTS = {}
        self.SOLVENTS = set()
        self.REVERSE_INDEX: Dict[str, Set[str]] = {}
        self._ENGINE = None
        self.hive_loaded = False

    def load_vocabulary(self):
        data = TheLore.get("LEXICON")
        self.SOLVENTS = set(data.get("solvents", []))
        self.ANTIGEN_REPLACEMENTS = data.get("antigen_replacements", {})
        for cat, words in data.items():
            if cat in self.categories or cat in ["refusal_guru", "cursed"]:
                word_set = set(words)
                self.VOCAB[cat] = word_set
                for w in word_set:
                    self._index_word(w, cat)
        self._load_hive()

    def _index_word(self, word: str, category: str):
        w = word.lower()
        if w not in self.REVERSE_INDEX:
            self.REVERSE_INDEX[w] = set()
        self.REVERSE_INDEX[w].add(category)

    def _load_hive(self):
        if not os.path.exists(self.HIVE_FILENAME):
            return
        try:
            with open(self.HIVE_FILENAME, 'r', encoding='utf-8') as f:
                hive_data = json.load(f)
            count = 0
            for cat, entries in hive_data.items():
                if cat not in self.LEARNED_VOCAB:
                    self.LEARNED_VOCAB[cat] = {}
                for word, tick in entries.items():
                    self.LEARNED_VOCAB[cat][word] = tick
                    self._index_word(word, cat)
                    count += 1
            self.hive_loaded = True
            print(f"{Prisma.CYN}[HIVE]: The Library is open. {count} memories restored.{Prisma.RST}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"{Prisma.RED}[HIVE]: Memory corruption detected. Starting fresh. ({e}){Prisma.RST}")

    def _save_hive(self):
        try:
            with open(self.HIVE_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(self.LEARNED_VOCAB, f, indent=2)
        except IOError:
            pass

    def set_engine(self, engine_ref): self._ENGINE = engine_ref

    def get_raw(self, category):
        base = self.VOCAB.get(category, set())
        learned = set(self.LEARNED_VOCAB.get(category, {}).keys())
        combined = base | learned
        if category == "suburban":
            return combined - self.USER_FLAGGED_BIAS
        return combined

    @lru_cache(maxsize=4096)
    def get_categories_for_word(self, word: str) -> Set[str]:
        w = word.lower()
        cats = self.REVERSE_INDEX.get(w, set()).copy()
        for cat, words in self.LEARNED_VOCAB.items():
            if w in words:
                cats.add(cat)
        return cats

    def teach(self, word, category, tick):
        w = word.lower()
        if category not in self.LEARNED_VOCAB: self.LEARNED_VOCAB[category] = {}
        if w in self.LEARNED_VOCAB[category]:
            return False
        self.LEARNED_VOCAB[category][w] = tick
        self._index_word(w, category)
        self._save_hive()
        return True

    def atrophy(self, current_tick, max_age=100):
        rotted = []
        for cat, words in self.LEARNED_VOCAB.items():
            for w in list(words.keys()):
                if (current_tick - words[w]) > max_age:
                    del words[w]
                    rotted.append(w)
        if rotted:
            self._save_hive()
        return rotted

    def harvest(self, text: str) -> Dict[str, List[str]]:
        results = {}
        if not text: return results
        translator = str.maketrans(string.punctuation, " " * len(string.punctuation))
        clean_text = text.translate(translator).lower()
        words = clean_text.split()
        for w in words:
            cats = self.get_categories_for_word(w)
            for cat in cats:
                if cat not in results:
                    results[cat] = []
                results[cat].append(w)
        return results

class LinguisticAnalyzer:
    def __init__(self, store_ref):
        self.store = store_ref
        self._TRANSLATOR = str.maketrans(string.punctuation, " " * len(string.punctuation))
        self.PHONETICS = {
            "PLOSIVE": set("bdgkpt"),
            "FRICATIVE": set("fthszsh"),
            "LIQUID": set("lr"),
            "NASAL": set("mn"),
            "VOWELS": set("aeiouy")}
        self.ROOTS = {
            "HEAVY": ("lith", "ferr", "petr", "dens", "grav", "struct", "base", "fund", "mound"),
            "KINETIC": ("mot", "mov", "ject", "tract", "pel", "crat", "dynam", "flux"),
            "ABSTRACT": ("tion", "ism", "ence", "ance", "ity", "ology", "ness", "ment", "idea"),
            "SUBURBAN": ("norm", "comm", "stand", "pol", "reg", "mod"),
            "VITAL": ("viv", "vita", "spir", "anim", "bio", "luc", "lum", "phot", "phon", "surg", "bloom")}

    def measure_viscosity(self, word: str) -> float:
        if not word: return 0.0
        w = word.lower()
        if w in self.store.SOLVENTS: return 0.1
        length_score = min(1.0, len(w) / 12.0)
        stops = sum(1 for c in w if c in self.PHONETICS["PLOSIVE"])
        stop_score = min(1.0, stops / 4.0)
        return (length_score * 0.6) + (stop_score * 0.4)

    @staticmethod
    def get_turbulence(words: List[str]) -> float:
        if len(words) < 2: return 0.0
        lengths = [len(w) for w in words]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        turbulence = min(1.0, variance / 10.0)
        return round(turbulence, 2)

    def vectorize(self, text: str) -> Dict[str, float]:
        words = self.sanitize(text)
        if not words: return {}
        DIMENSION_MAP = {
            "kinetic": "VEL", "explosive": "VEL",
            "heavy": "STR", "constructive": "STR",
            "antigen": "ENT", "toxin": "ENT",
            "thermal": "PHI", "photo": "PHI",
            "abstract": "PSI", "sacred": "PSI",
            "suburban": "BET", "buffer": "BET",
            "play": "DEL", "aerobic": "DEL"}
        dims = {"VEL": 0.0, "STR": 0.0, "ENT": 0.0, "PHI": 0.0, "PSI": 0.0, "BET": 0.0, "DEL": 0.0}
        for w in words:
            cats = self.store.get_categories_for_word(w)
            for cat in cats:
                if cat in DIMENSION_MAP:
                    target_dim = DIMENSION_MAP[cat]
                    dims[target_dim] += 1.0
        total = max(1.0, sum(dims.values()))
        return {k: round(v / total, 3) for k, v in dims.items()}

    @staticmethod
    def calculate_flux(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        if not vec_a or not vec_b: return 0.0
        keys = set(vec_a.keys()) | set(vec_b.keys())
        diff_sq = sum((vec_a.get(k, 0.0) - vec_b.get(k, 0.0)) ** 2 for k in keys)
        return round(diff_sq ** 0.5, 3)

    def contextualize(self, word: str, field_vector: Dict[str, float]) -> str:
        base_cat, score = self.classify_word(word)
        if not field_vector or not base_cat:
            return base_cat
        dominant_field = max(field_vector, key=field_vector.get) if field_vector else None
        if dominant_field and field_vector[dominant_field] > 0.6:
            return base_cat
        return base_cat

    def sanitize(self, text: str) -> List[str]:
        if not text: return []
        try:
            normalized = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        except (TypeError, AttributeError):
            normalized = text
        cleaned_text = normalized.translate(self._TRANSLATOR).lower()
        words = cleaned_text.split()
        return [w for w in words if w.strip() and w not in self.store.USER_FLAGGED_BIAS]

    def classify_word(self, word: str) -> Tuple[Optional[str], float]:
        w = word.lower()
        if len(w) < 3:
            return None, 0.0
        for category, roots in self.ROOTS.items():
            for root in roots:
                if root in w:
                    return category.lower(), 0.8
        counts = {k: 0 for k in self.PHONETICS}
        for char in w:
            for sound_type, chars in self.PHONETICS.items():
                if char in chars:
                    counts[sound_type] += 1
                    break
        density_score = (counts["PLOSIVE"] * 1.5) + (counts["NASAL"] * 0.8)
        flow_score = counts["LIQUID"] + counts["FRICATIVE"]
        vitality_score = (counts["VOWELS"] * 1.2) + (flow_score * 0.8)
        length_mod = 1.0 if len(w) > 5 else 1.5
        final_density = (density_score / len(w)) * length_mod
        final_vitality = (vitality_score / len(w)) * length_mod
        if final_density > 0.55:
            return "heavy", round(final_density, 2)
        if final_vitality > 0.6:
            return "play", round(final_vitality, 2)
        if (flow_score / len(w)) > 0.6:
            return "kinetic", 0.5
        return None, 0.0

    def measure_valence(self, words: List[str]) -> float:
        if not words: return 0.0
        pos_set = self.store.get_raw("sentiment_pos")
        neg_set = self.store.get_raw("sentiment_neg")
        negators = self.store.get_raw("sentiment_negators")
        score = 0.0
        for i, word in enumerate(words):
            is_negated = False
            if i > 0 and words[i-1] in negators:
                is_negated = True
            val = 0.0
            if word in pos_set:
                val = 1.0
            elif word in neg_set:
                val = -1.0
            if is_negated:
                val *= -0.5
            score += val
        normalized = score / max(1.0, len(words) * 0.5)
        return max(-1.0, min(1.0, normalized))

class SemanticField:
    def __init__(self, analyzer_ref):
        self.analyzer = analyzer_ref
        self.current_vector = {}
        self.momentum = 0.0
        self.history = []

    def update(self, text: str) -> Dict[str, float]:
        new_vector = self.analyzer.vectorize(text)
        if not new_vector:
            return self.current_vector
        flux = self.analyzer.calculate_flux(self.current_vector, new_vector)
        self.momentum = (self.momentum * 0.7) + (flux * 0.3)
        blended = {}
        all_keys = set(self.current_vector.keys()) | set(new_vector.keys())
        for k in all_keys:
            old_val = self.current_vector.get(k, 0.0)
            new_val = new_vector.get(k, 0.0)
            blended[k] = round((old_val * 0.6) + (new_val * 0.4), 3)
        self.current_vector = blended
        self.history.append((time.time(), flux))
        if len(self.history) > 10: self.history.pop(0)
        return self.current_vector

    def get_atmosphere(self) -> str:
        if not self.current_vector: return "VOID"
        dom = max(self.current_vector, key=self.current_vector.get)
        if self.momentum > 0.5:
            return f"Volatile {dom.upper()} Storm"
        return f"Stable {dom.upper()} Atmosphere"

class LexiconService:
    _INITIALIZED = False
    _STORE = None
    _ANALYZER = None
    ANTIGEN_REGEX = None
    SOLVENTS = set()

    @staticmethod
    def _ensure_ready(func):
        def wrapper(cls, *args, **kwargs):
            if not cls._INITIALIZED:
                cls.initialize()
            return func(cls, *args, **kwargs)
        return wrapper

    @classmethod
    def get_store(cls):
        if not cls._INITIALIZED:
            cls.initialize()
        return cls._STORE

    @classmethod
    def initialize(cls):
        if cls._INITIALIZED:
            return
        cls._INITIALIZED = True
        try:
            cls._STORE = LexiconStore()
            cls._STORE.load_vocabulary()
            cls._ANALYZER = LinguisticAnalyzer(cls._STORE)
            cls._STORE.set_engine(cls._ANALYZER)
            cls.compile_antigens()
            cls.SOLVENTS = cls._STORE.SOLVENTS
            print(f"{Prisma.GRN}[LEXICON]: Systems Nominal. Vocabulary Loaded.{Prisma.RST}")
        except Exception as e:
            cls._INITIALIZED = False
            print(f"{Prisma.RED}[LEXICON]: Initialization Failed: {e}{Prisma.RST}")
            raise e

    @classmethod
    @_ensure_ready
    def get_valence(cls, words: List[str]) -> float:
        return cls._ANALYZER.measure_valence(words)

    @classmethod
    @_ensure_ready
    def get_categories_for_word(cls, word: str) -> Set[str]:
        return cls._STORE.get_categories_for_word(word)

    @classmethod
    @_ensure_ready
    def get_current_category(cls, word: str) -> Optional[str]:
        categories = cls._STORE.get_categories_for_word(word)
        if categories:
            return next(iter(categories))
        return None

    @classmethod
    @_ensure_ready
    def measure_viscosity(cls, word: str) -> float:
        return cls._ANALYZER.measure_viscosity(word)

    @classmethod
    @_ensure_ready
    def get_turbulence(cls, words: List[str]) -> float:
        return cls._ANALYZER.get_turbulence(words)

    @classmethod
    @_ensure_ready
    def vectorize(cls, text: str) -> Dict[str, float]:
        return cls._ANALYZER.vectorize(text)

    @classmethod
    def compile_antigens(cls):
        if not cls._INITIALIZED:
            cls.initialize()
            return
        replacements = cls._STORE.ANTIGEN_REPLACEMENTS
        if not replacements:
            cls.ANTIGEN_REGEX = None
            return
        patterns = sorted(replacements.keys(), key=len, reverse=True)
        escaped = [re.escape(p) for p in patterns]
        cls.ANTIGEN_REGEX = re.compile('|'.join(escaped), re.IGNORECASE)

    @classmethod
    @_ensure_ready
    def sanitize(cls, text):
        return cls._ANALYZER.sanitize(text)

    @classmethod
    @_ensure_ready
    def classify(cls, word):
        return cls._ANALYZER.classify_word(word)

    @classmethod
    def clean(cls, text): return cls.sanitize(text)

    @classmethod
    def taste(cls, word): return cls.classify(word)

    @classmethod
    @_ensure_ready
    def create_field(cls):
        return SemanticField(cls._ANALYZER)

    @classmethod
    @_ensure_ready
    def get(cls, category: str) -> Set[str]:
        return cls._STORE.get_raw(category)

    @classmethod
    @_ensure_ready
    def get_random(cls, category: str) -> str:
        words = list(cls.get(category))
        return random.choice(words) if words else "void"

    @classmethod
    @_ensure_ready
    def teach(cls, word: str, category: str, tick: int = 0):
        cls._STORE.teach(word, category, tick)

    @classmethod
    @_ensure_ready
    def harvest(cls, text: str) -> Dict[str, List[str]]:
        return cls._STORE.harvest(text)

    @classmethod
    @_ensure_ready
    def atrophy(cls, current_tick, max_age=100):
        return cls._STORE.atrophy(current_tick, max_age)

    @classmethod
    def walk_gradient(cls, text: str) -> str:
        clean_words = cls.sanitize(text)
        if not clean_words: return "..."
        kept = []
        for w in clean_words:
            cat, _ = cls.classify(w)
            if cat in ["heavy", "abstract", "sacred"]:
                kept.append(w)
        return " ".join(kept) if kept else " ".join(clean_words[:3])

    @classmethod
    @_ensure_ready
    def learn_antigen(cls, word: str, replacement: str = ""):
        cls._STORE.ANTIGEN_REPLACEMENTS[word] = replacement
        cls.compile_antigens()

TheLexicon = LexiconService

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