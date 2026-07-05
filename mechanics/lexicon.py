"""mechanics/lexicon.py"""

import functools
import json
import os
import random
import re
import string
import time
import unicodedata
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple

from core import LoreManifest, Prisma
from struts import safe_get, ux


class LexiconStore:
    _PUNCTUATION = string.punctuation.replace("_", "")
    _TRANSLATOR = str.maketrans(_PUNCTUATION, " " * len(_PUNCTUATION))

    def __init__(self):
        from presets import BoneConfig
        from struts import safe_get

        akashic_cfg = safe_get(BoneConfig, "AKASHIC", {})
        self.save_dir = safe_get(akashic_cfg, "SAVE_DIR", "saves")
        self.HIVE_FILENAME = os.path.join(self.save_dir, "cortex_hive.json")
        self.categories = set()
        self.VOCAB: Dict[str, Set[str]] = {}
        self.LEARNED_VOCAB: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.USER_FLAGGED_BIAS = set()
        self.ANTIGEN_REPLACEMENTS = {}
        self.SOLVENTS = set()
        self.REVERSE_INDEX = defaultdict(set)
        self.hive_loaded = False

    def load_vocabulary(self):
        data = LoreManifest.get_instance().get("LEXICON") or {}
        self.SOLVENTS = set(data.get("solvents", []))
        self.ANTIGEN_REPLACEMENTS = data.get("antigen_replacements", {})
        for cat, words in data.items():
            if cat not in ("solvents", "antigen_replacements"):
                self.categories.add(cat)
                word_set = set(words)
                self.VOCAB[cat] = word_set
                for w in word_set:
                    self._index_word(w, cat)
        self._load_hive()

    def _index_word(self, word: str, category: str):
        self.REVERSE_INDEX[word.lower()].add(category)

    def _load_hive(self):
        if not os.path.exists(self.HIVE_FILENAME):
            return
        try:
            with open(self.HIVE_FILENAME, "r", encoding="utf-8") as f:
                hive_data = json.load(f)
            if not isinstance(hive_data, dict):
                return
            count = 0
            for cat, entries in hive_data.items():
                self.LEARNED_VOCAB.setdefault(cat, {}).update(entries)
                for word in entries:
                    self._index_word(word, cat)
                    count += 1
            self.hive_loaded = True
            if msg := ux("lexicon_strings", "hive_restored"):
                print(f"{Prisma.CYN}{msg.format(count=count)}{Prisma.RST}")
        except (IOError, json.JSONDecodeError):
            if msg := ux("lexicon_strings", "hive_corruption"):
                print(
                    f"{Prisma.OCHRE}{msg.format(e='Amnesia detected. Rebuilding pathways.')}{Prisma.RST}"
                )

    def save_hive(self):
        try:
            with open(self.HIVE_FILENAME, "w", encoding="utf-8") as f:
                json.dump(self.LEARNED_VOCAB, f, indent=2)
        except IOError as e:
            if msg := ux("lexicon_strings", "hive_corruption"):
                print(
                    f"{Prisma.RED}{msg.format(e=f'Failed to save Hive memory: {e}')}{Prisma.RST}"
                )
            else:
                print(
                    f"{Prisma.RED}CRITICAL: Failed to save Hive memory to disk: {e}{Prisma.RST}"
                )

    def get_raw(self, category: str) -> Set[str]:
        base = self.VOCAB.get(category, set())
        learned = self.LEARNED_VOCAB.get(category, {}).keys()
        combined = base | learned
        return combined - self.USER_FLAGGED_BIAS

    def get_categories_for_word(self, word: str) -> Set[str]:
        return self.REVERSE_INDEX.get(word.lower(), set())

    def teach(self, word: str, category: str, tick: int) -> bool:
        w = word.lower()
        cat_dict = self.LEARNED_VOCAB.setdefault(category, {})
        if w in cat_dict:
            return False
        if len(cat_dict) >= 1000:
            oldest_word = min(cat_dict, key=lambda k: int(cat_dict[k]))
            del cat_dict[oldest_word]
            if oldest_word in self.REVERSE_INDEX:
                self.REVERSE_INDEX[oldest_word].discard(category)
                if not self.REVERSE_INDEX[oldest_word]:
                    del self.REVERSE_INDEX[oldest_word]
        cat_dict[w] = tick
        self._index_word(w, category)
        return True

    def harvest(self, text: Any) -> Dict[str, List[str]]:
        if not text:
            return {}
        text_str = str(text).translate(self._TRANSLATOR).lower()
        chunk_hash = hash(text_str)
        if hasattr(self, "_chunk_cache") and chunk_hash in self._chunk_cache:
            return self._chunk_cache[chunk_hash]
        results = defaultdict(list)
        for word in text_str.split():
            for category in self.get_categories_for_word(word):
                results[category].append(word)
        final_results = dict(results)
        if not hasattr(self, "_chunk_cache"):
            self._chunk_cache = {}
        self._chunk_cache[chunk_hash] = final_results
        return final_results


class LinguisticAnalyzer:
    def __init__(self, store_ref):
        self.ANTIGEN_REGEX = None
        self.store = store_ref
        self._TRANSLATOR = store_ref._TRANSLATOR
        ling_data = LoreManifest.get_instance().get("LINGUISTICS") or {}
        raw_phonetics = ling_data.get("PHONETICS", {})
        self.PHONETICS = {k: set(v) for k, v in raw_phonetics.items()}
        raw_roots = ling_data.get("ROOTS", {})
        self.ROOTS = {k: tuple(v) for k, v in raw_roots.items()}
        self.thresholds = ling_data.get(
            "THRESHOLDS",
            {"heavy_density": 0.55, "play_vitality": 0.6, "kinetic_flow": 0.6},
        )
        self.biases = ling_data.get(
            "BIASES", {"heavy": 1.0, "play": 1.0, "kinetic": 1.0}
        )
        self.dimension_map = ling_data.get("DIMENSION_MAP", {})
        self.char_to_sound = {
            char: sound for sound, chars in self.PHONETICS.items() for char in chars
        }
        self.plosive_chars = self.PHONETICS.get("PLOSIVE", set())
        self.flow_chars = self.PHONETICS.get("LIQUID", set()) | self.PHONETICS.get(
            "VOWELS", set()
        )
        self.compile_antigens()

    def compile_antigens(self):
        reps = self.store.ANTIGEN_REPLACEMENTS
        if reps:
            patterns = sorted(reps.keys(), key=len, reverse=True)
            escaped = [rf"\b{re.escape(str(p))}\b" for p in patterns]
            self.ANTIGEN_REGEX = re.compile("|".join(escaped), re.IGNORECASE)
        else:
            self.ANTIGEN_REGEX = None

    @functools.lru_cache(maxsize=5000)
    def measure_viscosity(self, word: str) -> float:
        if not word:
            return 0.0
        clean_word = word.lower()
        if clean_word in self.store.SOLVENTS:
            return 0.1
        stops = sum(1 for char in clean_word if char in self.plosive_chars)
        flow = sum(1 for char in clean_word if char in self.flow_chars)
        length_penalty = min(1.0, len(clean_word) / 12.0)
        stop_ratio = min(1.0, stops / 3.0)
        flow_ratio = min(1.0, flow / 4.0)
        phonetic_balance = max(stop_ratio, flow_ratio)
        return (length_penalty * 0.5) + (phonetic_balance * 0.5)

    @staticmethod
    def get_turbulence(words: List[str]) -> float:
        word_count = len(words)
        if word_count < 2:
            return 0.0
        lengths = [len(word) for word in words]
        avg_length = sum(lengths) / word_count
        variance = sum((length - avg_length) ** 2 for length in lengths) / word_count
        normalized_variance = min(1.0, variance / 10.0)
        return round(normalized_variance, 2)

    _VECTOR_DIMS = ("VEL", "STR", "CHI", "PHI", "PSI", "BET", "DEL", "LAMBDA", "ENT")

    def vectorize(self, text: str) -> Dict[str, float]:
        if not (words := self.sanitize(text)):
            return {}
        dims = dict.fromkeys(self._VECTOR_DIMS, 0.0)
        for w in words:
            for cat in self.store.get_categories_for_word(w):
                if cat in self.dimension_map:
                    dims[self.dimension_map[cat]] += 1.0
        total = max(1.0, sum(dims.values()))
        result = {k: round(v / total, 3) for k, v in dims.items()}
        result["ENT"] = round(
            (result.get("CHI", 0.0) + min(1.0, total / max(1, len(words)))) / 2.0, 3
        )
        return result

    @staticmethod
    def calculate_flux(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        return round(
            sum(
                (vec_a.get(k, 0.0) - vec_b.get(k, 0.0)) ** 2
                for k in LinguisticAnalyzer._VECTOR_DIMS
            )
            ** 0.5,
            3,
        )

    def contextualize(self, word: str, field_vector: Dict[str, float]) -> str:
        base_cat, _ = self.classify_word(word)
        if field_vector and base_cat == "heavy":
            dom = max(field_vector, key=lambda k: float(field_vector[k]))
            if dom == "PSI" and field_vector.get(dom, 0.0) > 0.8:
                return "abstract"
        return str(base_cat) if base_cat else "unknown"

    def sanitize(self, text: Any) -> List[str]:
        if not text:
            return []
        text_str = str(text)
        normalized = (
            unicodedata.normalize("NFKD", text_str)
            .encode("ASCII", "ignore")
            .decode("utf-8")
        )
        cleaned_text = normalized.translate(self._TRANSLATOR).lower()
        if self.ANTIGEN_REGEX:
            cleaned_text = self.ANTIGEN_REGEX.sub(
                lambda m: self.store.ANTIGEN_REPLACEMENTS.get(m.group(0).lower(), ""),
                cleaned_text,
            )
        bias_set = self.store.USER_FLAGGED_BIAS
        return [w for w in cleaned_text.split() if w not in bias_set]

    @functools.lru_cache(maxsize=5000)
    def classify_word(self, word: str) -> Tuple[Optional[str], float]:
        w = word.lower()
        if len(w) < 3:
            return None, 0.0
        for category, roots in self.ROOTS.items():
            if any(r in w for r in roots):
                return category.lower(), 0.8
        counts = {}
        for char in w:
            if sound_type := self.char_to_sound.get(char):
                counts[sound_type] = counts.get(sound_type, 0) + 1
        density_score = (counts.get("PLOSIVE", 0) * 1.5) + (
            counts.get("NASAL", 0) * 0.8
        )
        flow_score = counts.get("LIQUID", 0) + counts.get("FRICATIVE", 0)
        vitality_score = (counts.get("VOWELS", 0) * 1.2) + (flow_score * 0.8)
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
        if not words:
            return 0.0
        score = 0.0
        prev_negator = False
        for word in words:
            cats = self.store.get_categories_for_word(word)
            val = (
                1.0
                if "sentiment_pos" in cats
                else (-1.0 if "sentiment_neg" in cats else 0.0)
            )
            if val != 0.0 and prev_negator:
                val *= -0.5
            score += val
            prev_negator = "sentiment_negators" in cats
        return max(-1.0, min(1.0, score / max(1.0, len(words) * 0.5)))

    def tune_sensitivity(self, voltage: float, drag: float):
        kinetic_shift = 1.0 + ((10.0 - voltage) * 0.02)
        self.biases["kinetic"] = round(max(0.8, min(1.2, kinetic_shift)), 3)
        heavy_shift = 1.0 - ((drag - 2.0) * 0.05)
        self.biases["heavy"] = round(max(0.5, min(1.0, heavy_shift)), 3)


class SemanticField:
    def __init__(self, analyzer_ref):
        self.analyzer = analyzer_ref
        self.current_vector = {}
        self.momentum = 0.0
        self.history = deque(maxlen=10)

    def update(self, text: str) -> Dict[str, float]:
        new_vector = self.analyzer.vectorize(text)
        if not new_vector:
            return self.current_vector
        if not self.current_vector:
            self.current_vector = new_vector
            flux = 0.0
        else:
            flux = self.analyzer.calculate_flux(self.current_vector, new_vector)
            self.momentum = (self.momentum * 0.7) + (flux * 0.3)
            all_dimensions = self.current_vector.keys() | new_vector.keys()
            self.current_vector = {
                dimension: round(
                    (self.current_vector.get(dimension, 0.0) * 0.6)
                    + (new_vector.get(dimension, 0.0) * 0.4),
                    3,
                )
                for dimension in all_dimensions
            }
        self.history.append((time.time(), flux))
        return self.current_vector

    def get_atmosphere(self) -> str:
        if not self.current_vector:
            return f"{Prisma.GRY}VOID{Prisma.RST}"
        dom = max(self.current_vector, key=lambda k: float(self.current_vector[k]))
        if self.momentum > 0.5:
            return f"{Prisma.VIOLET}Volatile {dom.upper()} Storm{Prisma.RST}"
        return f"{Prisma.CYN}Stable {dom.upper()} Atmosphere{Prisma.RST}"


class LexiconService:
    def __init__(self, events_ref=None):
        self._INITIALIZED = False
        self._STORE = LexiconStore()
        self._STORE.load_vocabulary()
        self._ANALYZER = LinguisticAnalyzer(self._STORE)
        self.SOLVENTS = self._STORE.SOLVENTS
        ling_data = LoreManifest.get_instance().get("LINGUISTICS") or {}
        self.PRIORITY_ORDER = ling_data.get("PRIORITY_ORDER", [])
        if events_ref:
            events_ref.subscribe("MYTHOLOGY_UPDATE", self._on_mythology_update)

    def _on_mythology_update(self, payload: Any):
        word = safe_get(payload, "word")
        category = safe_get(payload, "category")
        if word and category:
            self.teach(word, category, tick=int(time.time()))
            total_words = sum(len(s) for s in self._STORE.VOCAB.values()) + sum(
                len(s) for s in self._STORE.LEARNED_VOCAB.values()
            )
            if msg := ux("lexicon_strings", "sys_nominal"):
                print(f"{Prisma.GRN}{msg.format(total_words=total_words)}{Prisma.RST}")

    def initialize(self):
        self._INITIALIZED = True

    def get_store(self):
        return self._STORE

    def get_valence(self, words: List[str]) -> float:
        return self._ANALYZER.measure_valence(words)

    def get_categories_for_word(self, word: str) -> Set[str]:
        return self._STORE.get_categories_for_word(word)

    def get_current_category(self, word: str) -> Optional[str]:
        categories = self._STORE.get_categories_for_word(word)
        if categories:
            return next(iter(categories))
        return None

    def measure_viscosity(self, word: str) -> float:
        return self._ANALYZER.measure_viscosity(word)

    def get_turbulence(self, words: List[str]) -> float:
        return self._ANALYZER.get_turbulence(words)

    def vectorize(self, text: str) -> Dict[str, float]:
        return self._ANALYZER.vectorize(text)

    def purge_toxins(self, text: Any) -> str:
        text_str = str(text) if text else ""
        if not self._ANALYZER.ANTIGEN_REGEX or not text_str:
            return text_str
        return self._ANALYZER.ANTIGEN_REGEX.sub(
            lambda m: self._STORE.ANTIGEN_REPLACEMENTS.get(m.group(0).lower(), ""),
            text_str,
        )

    def sanitize(self, text: str) -> List[str]:
        return self._ANALYZER.sanitize(text)

    clean = sanitize

    def taste(self, word: str) -> Tuple[Optional[str], float]:
        known_cats = self._STORE.get_categories_for_word(word)
        if known_cats:
            for p_cat in self.PRIORITY_ORDER:
                if p_cat in known_cats:
                    return p_cat, 1.0
            return next(iter(known_cats)), 1.0
        return self._ANALYZER.classify_word(word)

    def create_field(self):
        return SemanticField(self._ANALYZER)

    def get(self, category: str) -> Set[str]:
        return self._STORE.get_raw(category)

    def get_random(self, category: str) -> str:
        words = list(self.get(category))
        if not words:
            return ux("lexicon_strings", "default_random_word") or "void"
        return random.choice(words)

    def teach(self, word: str, category: str, tick: int = 0):
        self._STORE.teach(word, category, tick)

    def save(self):
        if self._INITIALIZED and self._STORE:
            self._STORE.save_hive()
            msg = ux("lexicon_strings", "hive_saved")
            print(f"{Prisma.GRN}{msg}{Prisma.RST}")

    def harvest(self, text: str) -> Dict[str, List[str]]:
        return self._STORE.harvest(text)

    def learn_antigen(self, word: str, replacement: str = ""):
        self._STORE.ANTIGEN_REPLACEMENTS[word] = replacement
        self._ANALYZER.compile_antigens()

    def tune_perception(self, voltage: float, narrative_drag: float):
        if self._ANALYZER:
            self._ANALYZER.tune_sensitivity(voltage, narrative_drag)
