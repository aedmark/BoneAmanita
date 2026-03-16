"""
bone_lexicon.py
"""

import json
import os
import random
import re
import string
import time
import unicodedata
from typing import Tuple, Dict, Set, Optional, List
from bone_core import Prisma, LoreManifest, ux

class LexiconStore:
    HIVE_FILENAME = "cortex_hive.json"
    _PUNCTUATION = string.punctuation.replace("_", "")
    _TRANSLATOR = str.maketrans(_PUNCTUATION, " " * len(_PUNCTUATION))

    def __init__(self):
        self.categories = {"heavy", "kinetic", "explosive", "constructive", "abstract", "photo", "aerobic", "thermal",
                           "cryo", "suburban", "play", "sacred", "buffer", "antigen", "diversion", "meat",
                           "gradient_stop", "liminal", "void", "bureau_buzzwords", "crisis_term", "harvest",
                           "pareidolia", "passive_watch", "repair_trigger", "refusal_guru", "cursed", "sentiment_pos",
                           "sentiment_neg", "sentiment_negators", "toxin", }
        self.VOCAB: Dict[str, Set[str]] = {k: set() for k in self.categories}
        self.LEARNED_VOCAB: Dict[str, Dict[str, int]] = {}
        self.USER_FLAGGED_BIAS = set()
        self.ANTIGEN_REPLACEMENTS = {}
        self.SOLVENTS = set()
        self.REVERSE_INDEX: Dict[str, Set[str]] = {}
        self.hive_loaded = False

    def load_vocabulary(self):
        data = LoreManifest.get_instance().get("LEXICON") or {}
        self.SOLVENTS = set(data.get("solvents", []))
        self.ANTIGEN_REPLACEMENTS = data.get("antigen_replacements", {})
        for cat, words in data.items():
            if cat in self.categories:
                word_set = set(words)
                self.VOCAB[cat] = word_set
                if not cat.startswith("sentiment"):
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
            with open(self.HIVE_FILENAME, "r", encoding="utf-8") as f:
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
            msg = ux("lexicon_strings", "hive_restored")
            print(f"{Prisma.CYN}{msg.format(count=count)}{Prisma.RST}")
        except (IOError, json.JSONDecodeError) as e:
            msg = ux("lexicon_strings", "hive_corruption")
            print(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}")

    def save_hive(self):
        try:
            with open(self.HIVE_FILENAME, "w", encoding="utf-8") as f:
                json.dump(self.LEARNED_VOCAB, f, indent=2)
        except IOError:
            pass

    def get_raw(self, category: str) -> Set[str]:
        base = self.VOCAB.get(category, set())
        learned = set(self.LEARNED_VOCAB.get(category, {}).keys())
        combined = base | learned
        if category == "suburban":
            return combined - self.USER_FLAGGED_BIAS
        return combined

    def get_categories_for_word(self, word: str) -> Set[str]:
        w = word.lower()
        return self.REVERSE_INDEX.get(w, set()).copy()

    def teach(self, word: str, category: str, tick: int) -> bool:
        w = word.lower()
        if category not in self.LEARNED_VOCAB:
            self.LEARNED_VOCAB[category] = {}
        if w in self.LEARNED_VOCAB[category]:
            return False
        self.LEARNED_VOCAB[category][w] = tick
        self._index_word(w, category)
        return True

    def harvest(self, text: str) -> Dict[str, List[str]]:
        results = {}
        if not text:
            return results
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
        self._TRANSLATOR = getattr(self.store, "_TRANSLATOR", None)
        ling_data = LoreManifest.get_instance().get("LINGUISTICS") or {}
        raw_phonetics = ling_data.get("PHONETICS", {})
        self.PHONETICS = {k: set(v) for k, v in raw_phonetics.items()}
        raw_roots = ling_data.get("ROOTS", {})
        self.ROOTS = {k: tuple(v) for k, v in raw_roots.items()}
        self.thresholds = ling_data.get("THRESHOLDS", {"heavy_density": 0.55, "play_vitality": 0.6, "kinetic_flow": 0.6, })
        self.biases = ling_data.get("BIASES", {"heavy": 1.0, "play": 1.0, "kinetic": 1.0})
        self.dimension_map = ling_data.get("DIMENSION_MAP", {})

    def measure_viscosity(self, word: str) -> float:
        if not word:
            return 0.0
        w = word.lower()
        if w in self.store.SOLVENTS:
            return 0.1
        length_score = min(1.0, len(w) / 12.0)
        stops, flow = 0, 0
        for c in w:
            if c in self.PHONETICS["PLOSIVE"]:
                stops += 1
            elif c in self.PHONETICS["LIQUID"] or c in self.PHONETICS["VOWELS"]:
                flow += 1
        stop_score = min(1.0, stops / 3.0)
        flow_score = min(1.0, flow / 4.0)
        substance_score = max(stop_score, flow_score)
        return (length_score * 0.5) + (substance_score * 0.5)

    @staticmethod
    def get_turbulence(words: List[str]) -> float:
        if len(words) < 2:
            return 0.0
        lengths = [len(w) for w in words]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        turbulence = min(1.0, variance / 10.0)
        return round(turbulence, 2)

    def vectorize(self, text: str) -> Dict[str, float]:
        words = self.sanitize(text)
        if not words:
            return {}
        dims = {"VEL": 0.0, "STR": 0.0, "CHI": 0.0, "PHI": 0.0, "PSI": 0.0, "BET": 0.0, "DEL": 0.0, "LAMBDA": 0.0,
                "ENT": 0.0, }
        for w in words:
            cats = self.store.get_categories_for_word(w)
            for cat in cats:
                if cat in self.dimension_map:
                    target_dim = self.dimension_map[cat]
                    dims[target_dim] += 1.0
        total = max(1.0, sum(dims.values()))
        result = {k: round(v / total, 3) for k, v in dims.items()}
        result["ENT"] = result["CHI"]
        return result

    @staticmethod
    def calculate_flux(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        keys = set(vec_a.keys()) | set(vec_b.keys())
        diff_sq = sum((vec_a.get(k, 0.0) - vec_b.get(k, 0.0)) ** 2 for k in keys)
        return round(diff_sq**0.5, 3)

    def contextualize(self, word: str, field_vector: Dict[str, float]) -> str:
        base_cat, _score = self.classify_word(word)
        if not field_vector or not base_cat:
            return base_cat
        dominant_field = max(field_vector, key=field_vector.get)
        if field_vector.get(dominant_field, 0.0) > 0.8:
            if dominant_field == "PSI" and base_cat == "heavy":
                return "abstract"
        return base_cat

    def sanitize(self, text: str) -> List[str]:
        if not text:
            return []
        try:
            normalized = (unicodedata.normalize("NFKD", text)
                          .encode("ASCII", "ignore")
                          .decode("utf-8"))
        except (TypeError, AttributeError):
            normalized = text
        xlate = self._TRANSLATOR if self._TRANSLATOR else str.maketrans("", "")
        cleaned_text = normalized.translate(xlate).lower()
        words = cleaned_text.split()
        bias_set = getattr(self.store, "USER_FLAGGED_BIAS", set())
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
        char_to_sound = {
            char: sound_type
            for sound_type, chars in self.PHONETICS.items()
            for char in chars}
        for char in w:
            if sound_type := char_to_sound.get(char):
                counts[sound_type] += 1
        density_score = (counts.get("PLOSIVE", 0) * 1.5) + (counts.get("NASAL", 0) * 0.8)
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
        for i, word in enumerate(words):
            cats = self.store.get_categories_for_word(word)
            val = 0.0
            if "sentiment_pos" in cats:
                val = 1.0
            elif "sentiment_neg" in cats:
                val = -1.0
            if val != 0.0 and i > 0 and "sentiment_negators" in self.store.get_categories_for_word(words[i - 1]):
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

from collections import deque

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
        flux = self.analyzer.calculate_flux(self.current_vector, new_vector)
        self.momentum = (self.momentum * 0.7) + (flux * 0.3)
        blended = {k: round(v * 0.6, 3) for k, v in self.current_vector.items()}
        for k, v in new_vector.items():
            blended[k] = round(blended.get(k, 0.0) + (v * 0.4), 3)
        self.current_vector = blended
        self.history.append((time.time(), flux))
        return self.current_vector

    def get_atmosphere(self) -> str:
        if not self.current_vector:
            return "VOID"
        dom = max(self.current_vector, key=self.current_vector.get)
        if self.momentum > 0.5:
            return f"Volatile {dom.upper()} Storm"
        return f"Stable {dom.upper()} Atmosphere"

class LexiconService:
    def __init__(self):
        self._INITIALIZED = False
        self._STORE = None
        self._ANALYZER = None
        self.ANTIGEN_REGEX = None
        self.SOLVENTS = set()

    def get_store(self):
        if not self._INITIALIZED:
            self.initialize()
        return self._STORE

    def initialize(self):
        if self._INITIALIZED:
            return
        self._INITIALIZED = True
        try:
            self._STORE = LexiconStore()
            self._STORE.load_vocabulary()
            self._ANALYZER = LinguisticAnalyzer(self._STORE)
            self.compile_antigens()
            self.SOLVENTS = self._STORE.SOLVENTS
            total_words = sum(len(s) for s in self._STORE.VOCAB.values())
            msg = ux("lexicon_strings", "sys_nominal")
            print(f"{Prisma.GRN}{msg.format(total_words=total_words)}{Prisma.RST}")

        except Exception as e:
            self._INITIALIZED = False
            msg = ux("lexicon_strings", "sys_init_fail")
            print(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}")
            raise e

    def get_valence(self, words: List[str]) -> float:
        if not self._INITIALIZED:
            self.initialize()
        return self._ANALYZER.measure_valence(words)

    def get_categories_for_word(self, word: str) -> Set[str]:
        if not self._INITIALIZED:
            self.initialize()
        return self._STORE.get_categories_for_word(word)

    def get_current_category(self, word: str) -> Optional[str]:
        if not self._INITIALIZED:
            self.initialize()
        categories = self._STORE.get_categories_for_word(word)
        if categories:
            return next(iter(categories))
        return None

    def measure_viscosity(self, word: str) -> float:
        if not self._INITIALIZED:
            self.initialize()
        return self._ANALYZER.measure_viscosity(word)

    def get_turbulence(self, words: List[str]) -> float:
        if not self._INITIALIZED:
            self.initialize()
        return self._ANALYZER.get_turbulence(words)

    def vectorize(self, text: str) -> Dict[str, float]:
        if not self._INITIALIZED:
            self.initialize()
        return self._ANALYZER.vectorize(text)

    def compile_antigens(self):
        if not self._INITIALIZED:
            self.initialize()
            return
        replacements = self._STORE.ANTIGEN_REPLACEMENTS
        if not replacements:
            self.ANTIGEN_REGEX = None
            return
        patterns = sorted(replacements.keys(), key=len, reverse=True)
        escaped = [fr"\b{re.escape(str(p))}\b" for p in patterns]
        self.ANTIGEN_REGEX = re.compile("|".join(escaped), re.IGNORECASE)

    def purge_toxins(self, text: str) -> str:
        if not self._INITIALIZED:
            self.initialize()
        if not self.ANTIGEN_REGEX or not text:
            return text

        def replacer(match):
            m_lower = match.group(0).lower()
            return self._STORE.ANTIGEN_REPLACEMENTS.get(m_lower, "")
        return self.ANTIGEN_REGEX.sub(replacer, text)

    def sanitize(self, text: str) -> List[str]:
        if not self._INITIALIZED:
            self.initialize()
        return self._ANALYZER.sanitize(text)

    def classify(self, word: str) -> Tuple[Optional[str], float]:
        if not self._INITIALIZED:
            self.initialize()
        ling_data = LoreManifest.get_instance().get("LINGUISTICS") or {}
        priority_order = ling_data.get("PRIORITY_ORDER", [])
        known_cats = self._STORE.get_categories_for_word(word)
        if known_cats:
            for p_cat in priority_order:
                if p_cat in known_cats:
                    return p_cat, 1.0
            return next(iter(known_cats)), 1.0
        return self._ANALYZER.classify_word(word)

    def clean(self, text: str) -> List[str]:
        return self.sanitize(text)

    def taste(self, word: str) -> Tuple[Optional[str], float]:
        return self.classify(word)

    def create_field(self):
        if not self._INITIALIZED:
            self.initialize()
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
        self.compile_antigens()

    def tune_perception(self, voltage: float, narrative_drag: float):
        if self._ANALYZER:
            self._ANALYZER.tune_sensitivity(voltage, narrative_drag)