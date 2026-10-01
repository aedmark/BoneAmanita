import re
import string
import functools
from collections import defaultdict
from typing import Dict, List, Set, Any, Tuple, Optional

class LinguisticAnalyzer:
    """
    Core semantic analysis engine. Maps raw text into physical drag, viscosity,
    and semantic dimensions (Heavy, Kinetic, Play, Tension, etc.).
    """
    _PUNCTUATION = string.punctuation.replace("_", "")
    _TRANSLATOR = str.maketrans(_PUNCTUATION, " " * len(_PUNCTUATION))

    def __init__(self, vocab_config: Dict[str, Any], linguistics_config: Dict[str, Any]):
        """
        vocab_config: Dict containing categorized words (e.g. {"heavy": ["delve", "synergy"]})
        linguistics_config: Dict containing ROOTS, PHONETICS, BIASES.
        """
        self.vocab = vocab_config
        self.solvents = set(vocab_config.get("solvents", []))
        self.antigen_replacements = vocab_config.get("antigen_replacements", {})
        
        self.phonetics = {k: set(v) for k, v in linguistics_config.get("PHONETICS", {}).items()}
        self.roots = {k: tuple(v) for k, v in linguistics_config.get("ROOTS", {}).items()}
        self.biases = linguistics_config.get("BIASES", {"heavy": 1.0, "play": 1.0, "kinetic": 1.0})
        self.dimension_map = linguistics_config.get("DIMENSION_MAP", {})
        
        self.plosive_chars = self.phonetics.get("PLOSIVE", set())
        self.flow_chars = self.phonetics.get("LIQUID", set()) | self.phonetics.get("VOWELS", set())
        
        self._reverse_index = defaultdict(set)
        for cat, words in self.vocab.items():
            if cat not in ("solvents", "antigen_replacements"):
                for w in words:
                    self._reverse_index[w].add(cat)
                    
        self.compile_antigens()

    def compile_antigens(self):
        if self.antigen_replacements:
            patterns = sorted(self.antigen_replacements.keys(), key=len, reverse=True)
            escaped = [rf"\b{re.escape(str(p))}\b" for p in patterns]
            self.antigen_regex = re.compile("|".join(escaped), re.IGNORECASE)
        else:
            self.antigen_regex = None

    def sanitize(self, text: str) -> List[str]:
        if not text:
            return []
        text_str = str(text).translate(self._TRANSLATOR).lower()
        return [w for w in text_str.split() if w]

    @functools.lru_cache(maxsize=5000)
    def measure_viscosity(self, word: str) -> float:
        if not word: return 0.0
        clean = word.lower()
        if clean in self.solvents: return 0.1
        
        stops = sum(1 for char in clean if char in self.plosive_chars)
        flow = sum(1 for char in clean if char in self.flow_chars)
        
        length_penalty = min(1.0, len(clean) / 12.0)
        phonetic_balance = max(min(1.0, stops / 3.0), min(1.0, flow / 4.0))
        return (length_penalty * 0.5) + (phonetic_balance * 0.5)

    def vectorize(self, text: str) -> Dict[str, float]:
        """Calculates the presence of semantic dimensions (kinetic, heavy, play)."""
        words = self.sanitize(text)
        if not words:
            return {}
            
        dims = defaultdict(float)
        for w in words:
            categories = self._reverse_index.get(w, set())
            for cat in categories:
                mapped_dims = self.dimension_map.get(cat, {cat: 1.0})
                bias = self.biases.get(cat, 1.0)
                for dim_name, weight in mapped_dims.items():
                    dims[dim_name] += weight * bias
                    
            # Root fallback
            if not categories and len(w) >= 3:
                for cat, roots in self.roots.items():
                    if any(r in w for r in roots):
                        mapped = self.dimension_map.get(cat, {cat: 0.5})
                        bias = self.biases.get(cat, 1.0)
                        for d, wt in mapped.items():
                            dims[d] += wt * bias
                            
        word_count = len(words)
        return {k: min(1.0, v / (word_count * 0.2)) for k, v in dims.items()}
