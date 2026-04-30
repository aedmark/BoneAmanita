"""drivers/liminal.py"""

from typing import Dict

from presets import BoneConfig
from struts import safe_get


class LiminalModule:
    def __init__(self, config_ref=None, lexicon_ref=None):
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref
        self.lambda_val = 0.0
        self.godel_scars = 0
        self.drivers_cfg = getattr(self.cfg, "DRIVERS", {})

    def analyze(self, text: str, physics_vector: Dict[str, float]) -> float:
        cfg = self.drivers_cfg
        words = text.lower().split()
        liminal_vocab = self.lex.get("liminal") if self.lex else set()
        void_hits = sum(1 for w in words if w in liminal_vocab)
        lexical_lambda = min(1.0, void_hits * safe_get(cfg, "LIMINAL_LEXICAL_WEIGHT", 0.15))
        dark_matter_sparks = 0
        if len(words) > 1 and hasattr(self.lex, "get_categories_for_word"):
            phys_set, void_set = {"heavy", "kinetic"}, {"abstract", "liminal", "void"}
            flags = [1 if cats & phys_set else (2 if cats & void_set else 0) for w in words
                     if (cats := set(self.lex.get_categories_for_word(w) or []))]
            dark_matter_sparks = sum(
                1 for i in range(len(flags) - 1)
                if flags[i] and flags[i + 1] and flags[i] != flags[i + 1])
        dark_matter_lambda = min(
            1.0, dark_matter_sparks * safe_get(cfg, "LIMINAL_DARK_MATTER_WEIGHT", 0.25))
        pv = physics_vector or {}
        vector_lambda = ((pv.get("PSI", 0) * safe_get(cfg, "LIMINAL_VEC_PSI_MULT", 0.5)) +
                         (pv.get("ENT", 0) * safe_get(cfg, "LIMINAL_VEC_ENT_MULT", 0.3)) +
                         (pv.get("DEL", 0) * safe_get(cfg, "LIMINAL_VEC_DEL_MULT", 0.2)))
        self.lambda_val = (self.lambda_val * safe_get(cfg, "LIMINAL_DECAY", 0.7)) + (
                (lexical_lambda + dark_matter_lambda + vector_lambda) *
                safe_get(cfg, "LIMINAL_GROWTH", 0.15))
        if self.lambda_val > safe_get(cfg, "LIMINAL_SCAR_THRESHOLD", 0.85):
            self.godel_scars += 1
            self.lambda_val *= safe_get(cfg, "LIMINAL_SCAR_RELIEF", 0.5)
        return min(1.0, self.lambda_val)
