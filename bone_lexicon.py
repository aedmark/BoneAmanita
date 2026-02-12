""" bone_lexicon.py - The Global Dictionary """

import json
import random
import re
import string
import time
import unicodedata
import os
from dataclasses import dataclass
from typing import Tuple, Dict, Set, Optional, List, Any
from bone_core import Prisma, TheLore
from functools import lru_cache

class LexiconStore:
    HIVE_FILENAME = "cortex_hive.json"
    _PUNCTUATION = string.punctuation.replace("_", "")
    _TRANSLATOR = str.maketrans(_PUNCTUATION, " " * len(_PUNCTUATION))

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

    def save_hive(self):
        try:
            with open(self.HIVE_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(self.LEARNED_VOCAB, f, indent=2)
        except IOError:
            pass

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
        return self.REVERSE_INDEX.get(w, set()).copy()

    def teach(self, word, category, tick):
        w = word.lower()
        if category not in self.LEARNED_VOCAB: self.LEARNED_VOCAB[category] = {}
        if w in self.LEARNED_VOCAB[category]:
            return False
        self.LEARNED_VOCAB[category][w] = tick
        self._index_word(w, category)
        return True

    def atrophy(self, current_tick, max_age=100, protected: Set[str] = None):
        if not self.LEARNED_VOCAB:
            return []
        cats = list(self.LEARNED_VOCAB.keys())
        if not cats: return []
        target_cat = random.choice(cats)
        words = self.LEARNED_VOCAB[target_cat]
        rotted = []
        protected = protected or set()
        candidates = list(words.keys())
        sample_size = max(5, len(candidates) // 10)
        audit_batch = random.sample(candidates, min(len(candidates), sample_size))
        for candidate in audit_batch:
            if candidate in protected:
                continue
            age = current_tick - words[candidate]
            if age > max_age:
                death_probability = 1.0 if age > (max_age * 2) else 0.2
                if random.random() < death_probability:
                    del words[candidate]
                    rotted.append(candidate)
        if rotted:
            self.save_hive()
        return rotted

    def harvest(self, text: str) -> Dict[str, List[str]]:
        results = {}
        if not text: return results
        clean_text = text.translate(self._TRANSLATOR).lower()
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
        punct = string.punctuation.replace("_", "")
        self._TRANSLATOR = str.maketrans(punct, " " * len(punct))
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
        self.thresholds = {
            "heavy_density": 0.55,
            "play_vitality": 0.6,
            "kinetic_flow": 0.6}
        self.biases = {
            "heavy": 1.0,
            "play": 1.0,
            "kinetic": 1.0}

    def measure_viscosity(self, word: str) -> float:
        if not word: return 0.0
        w = word.lower()
        if w in self.store.SOLVENTS: return 0.1
        length_score = min(1.0, len(w) / 12.0)
        stops = sum(1 for c in w if c in self.PHONETICS["PLOSIVE"])
        flow = sum(1 for c in w if c in self.PHONETICS["LIQUID"] or c in self.PHONETICS["VOWELS"])
        stop_score = min(1.0, stops / 3.0)
        flow_score = min(1.0, flow / 4.0)
        substance_score = max(stop_score, flow_score)
        return (length_score * 0.5) + (substance_score * 0.5)

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
        bias_set = getattr(self.store, 'USER_FLAGGED_BIAS', set())
        return [w for w in words if w.strip() and w not in bias_set]

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
        heavy_thresh = self.thresholds["heavy_density"] * self.biases["heavy"]
        play_thresh = self.thresholds["play_vitality"] * self.biases["play"]
        kinetic_thresh = self.thresholds["kinetic_flow"] * self.biases["kinetic"]
        if final_density > heavy_thresh:
            return "heavy", round(final_density, 2)
        if final_vitality > play_thresh:
            return "play", round(final_vitality, 2)
        if (flow_score / len(w)) > kinetic_thresh:
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

    def tune_sensitivity(self, voltage: float, drag: float):
        if voltage > 15.0:
            self.biases["kinetic"] = 0.8
        elif voltage < 5.0:
            self.biases["kinetic"] = 1.2
        else:
            self.biases["kinetic"] = 1.0
        if drag > 5.0:
            self.biases["heavy"] = 0.8
        else:
            self.biases["heavy"] = 1.0

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
            cls.compile_antigens()
            cls.SOLVENTS = cls._STORE.SOLVENTS
            total_words = sum(len(s) for s in cls._STORE.VOCAB.values())
            print(f"{Prisma.GRN}[LEXICON]: Systems Nominal. {total_words} words loaded.{Prisma.RST}")

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
        escaped = [re.escape(str(p)) for p in patterns]
        cls.ANTIGEN_REGEX = re.compile('|'.join(escaped), re.IGNORECASE)

    @classmethod
    @_ensure_ready
    def sanitize(cls, text):
        return cls._ANALYZER.sanitize(text)

    @classmethod
    @_ensure_ready
    def classify(cls, word):
        PRIORITY_ORDER = [
            "heavy", "kinetic", "explosive", "thermal", "cryo",
            "sacred", "antigen", "meat",
            "play", "suburban", "abstract"]
        known_cats = cls._STORE.get_categories_for_word(word)
        if known_cats:
            for p_cat in PRIORITY_ORDER:
                if p_cat in known_cats:
                    return p_cat, 1.0
            return next(iter(known_cats)), 1.0
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
    def save(cls):
        if cls._INITIALIZED and cls._STORE:
            cls._STORE.save_hive()
            print(f"{Prisma.GRN}[LEXICON]: Hive saved to disk.{Prisma.RST}")

    @classmethod
    @_ensure_ready
    def harvest(cls, text: str) -> Dict[str, List[str]]:
        return cls._STORE.harvest(text)

    @classmethod
    @_ensure_ready
    def atrophy(cls, current_tick, max_age=100, protected: Set[str] = None):
        return cls._STORE.atrophy(current_tick, max_age, protected=protected)

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

    @classmethod
    @_ensure_ready
    def tune_perception(cls, voltage: float, narrative_drag: float):
        if cls._ANALYZER:
            cls._ANALYZER.tune_sensitivity(voltage, narrative_drag)

TheLexicon = LexiconService

@dataclass
class SomaticState:
    tone: str
    pacing: str
    focus: str
    somatic_sensation: str
    metaphor: str
    internal_monologue_hint: str
    color_code: str = Prisma.GRY

class RosettaStone:
    @staticmethod
    def translate(physics, bio, impulse):
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        coherence = physics.get("coherence", 0.5)
        tone = RosettaStone._derive_voltage_tone(voltage)
        sensation = RosettaStone._derive_drag_sensation(drag)
        if impulse and hasattr(impulse, 'somatic_reflex') and impulse.somatic_reflex:
            sensation = f"{sensation} ({impulse.somatic_reflex})"
        focus = RosettaStone._derive_coherence_focus(coherence)
        chem_state = bio.get("chem", {})
        flavor = RosettaStone._apply_chemistry(tone, chem_state)
        somatic_lib = TheLore.get("SOMATIC_LIBRARY") or {}
        pacing_key = "HIGH" if voltage > 12 else "LOW"
        pacing_options = somatic_lib.get("PACING_RESERVOIR", {}).get(pacing_key, ["Normal"])
        pacing = random.choice(pacing_options)
        meta_key = "HIGH_DRAG" if drag > 4 else "LOW_DRAG"
        meta_options = somatic_lib.get("METAPHOR_RESERVOIR", {}).get(meta_key, ["Stable"])
        metaphor = random.choice(meta_options)
        hint = f"Focus on the {sensation.lower()} nature of this moment."
        return SomaticState(
            tone=flavor,
            pacing=pacing,
            focus=focus,
            somatic_sensation=sensation,
            metaphor=metaphor,
            internal_monologue_hint=hint)

    @staticmethod
    def _derive_voltage_tone(v):
        if v < 5.0: return "Lethargic (Hypo-active)"
        if v < 10.0: return "Lucid (Flow)"
        if v < 15.0: return "Vibrating (Manic precursor)"
        return "FRACTURED (Hyper-voltage)"

    @staticmethod
    def _derive_drag_sensation(d):
        if d < 1.0: return "Weightless"
        if d < 3.0: return "Viscous"
        if d < 6.0: return "Crushing"
        return "IMMOBILIZED (Event Horizon)"

    @staticmethod
    def _derive_coherence_focus(k):
        if k > 0.8: return "Laser"
        if k > 0.4: return "Soft"
        return "Scattershot"

    @staticmethod
    def _apply_chemistry(current_tone, chem):
        cortisol = chem.get("COR", 0.0)
        dopamine = chem.get("DOP", 0.0)
        if cortisol > 0.6: return f"{current_tone} (Trembling)"
        if dopamine > 0.6: return f"{current_tone} (Giddy)"
        return current_tone

class SomaticInterface:
    def __init__(self, engine_ref):
        self.eng = engine_ref

    def get_current_qualia(self, impulse: Any = None) -> SomaticState:
        physics = self.eng.phys.observer.last_physics_packet if self.eng.phys.observer.last_physics_packet else {}
        if hasattr(physics, "to_dict"): physics = physics.to_dict()
        bio = {}
        if hasattr(self.eng, 'bio') and self.eng.bio:
            if hasattr(self.eng.bio, 'endo'):
                bio = self.eng.bio.endo.get_state()
            if hasattr(self.eng.bio, 'mito') and hasattr(self.eng.bio.mito, 'state'):
                bio["atp"] = self.eng.bio.mito.state.atp_pool
        return RosettaStone.translate(physics, bio, impulse)

    def report(self):
        qualia = self.get_current_qualia()
        print(f"\n{qualia.color_code}--- SOMATIC REPORT ---")
        print(f"TONE: {qualia.tone}")
        print(f"BODY: {qualia.somatic_sensation}")
        print(f"MIND: {qualia.focus}")
        print(f"STATE: {qualia.metaphor}{Prisma.RST}\n")
