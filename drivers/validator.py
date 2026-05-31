"""drivers/validator.py"""

import math
from typing import Any
from core import LoreManifest
from presets import BoneConfig
from struts import safe_get

class CongruenceValidator:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.last_phi = 1.0
        self._archetype_map = None

    @property
    def map(self):
        if self._archetype_map is None:
            self._archetype_map = LoreManifest.get_instance(config_ref=self.cfg).get("LENSES") or {}
        return self._archetype_map

    def calculate_resonance(self, text: str, context: Any) -> float:
        if not text:
            return 0.0
        cfg = safe_get(self.cfg, "DRIVERS", {})
        default_lens = safe_get(cfg, "DEFAULT_LENS", "OBSERVER")
        raw_lens = safe_get(context, "active_lens", default_lens)
        archetype = str(raw_lens).upper().replace("THE ", "")
        tone_score = float(safe_get(cfg, "CONGRUENCE_BASE_TONE", 0.8))
        target_data = self.map.get(archetype, {})
        if isinstance(target_data, dict):
            vocab_str = target_data.get("vocab", "")
            vocab_set = {w.strip().lower() for w in vocab_str.split(",") if w}
            keyword_set = {k.lower() for k in target_data.get("keywords", [])}
            target_words = vocab_set | keyword_set
            if target_words and hasattr(context, "clean_words"):
                words_to_check = set(w.lower() for w in context.clean_words)
                exact_hits = words_to_check.intersection(target_words)
                hits = len(exact_hits)
                if hits > 0:
                    bonus = safe_get(cfg, "CONGRUENCE_HIT_BONUS", 0.1)
                    tone_score += bonus * math.log1p(hits)
        return min(safe_get(cfg, "CONGRUENCE_MAX_TONE", 2.0), tone_score)
