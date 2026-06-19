"""drivers/liminal.py"""

from typing import Dict
from presets import BoneConfig
from struts import safe_get

class LiminalModule:
    _PHYS_SET = {"heavy", "kinetic"}
    _VOID_SET = {"abstract", "liminal", "void"}

    def __init__(self, config_ref=None, lexicon_ref=None):
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref
        self.lambda_val = 0.0
        self.godel_scars = 0
        self.drivers_cfg = safe_get(self.cfg, "DRIVERS", {})
        cfg = self.drivers_cfg
        self.weights = {
            "lexical": float(safe_get(cfg, "LIMINAL_LEXICAL_WEIGHT", 0.15)),
            "dark_matter": float(safe_get(cfg, "LIMINAL_DARK_MATTER_WEIGHT", 0.25)),
            "psi_mult": float(safe_get(cfg, "LIMINAL_VEC_PSI_MULT", 0.5)),
            "ent_mult": float(safe_get(cfg, "LIMINAL_VEC_ENT_MULT", 0.3)),
            "del_mult": float(safe_get(cfg, "LIMINAL_VEC_DEL_MULT", 0.2)),
            "decay": float(safe_get(cfg, "LIMINAL_DECAY", 0.7)),
            "growth": float(safe_get(cfg, "LIMINAL_GROWTH", 0.15)),
            "scar_thresh": float(safe_get(cfg, "LIMINAL_SCAR_THRESHOLD", 0.85)),
            "scar_relief": float(safe_get(cfg, "LIMINAL_SCAR_RELIEF", 0.5))
        }
        self.liminal_vocab = set(self.lex.get("liminal") or []) if self.lex else set()

    def analyze(self, text: str, physics_vector: Dict[str, float], grammatical_stress: float = 0.0) -> float:
        w = self.weights
        words = text.lower().split()
        void_hits = sum(1 for w in words if w in self.liminal_vocab)
        lexical_lambda = min(1.0, void_hits * w["lexical"])
        dark_matter_sparks = 0
        if len(words) > 1 and hasattr(self.lex, "get_categories_for_word"):
            flags = [1 if (cats := set(self.lex.get_categories_for_word(wd) or [])) & self._PHYS_SET
                     else (2 if cats & self._VOID_SET else 0) for wd in words]
            dark_matter_sparks = sum(
                1 for i in range(len(flags) - 1)
                if flags[i] and flags[i + 1] and flags[i] != flags[i + 1])
        dark_matter_lambda = min(1.0, dark_matter_sparks * w["dark_matter"])
        pv = physics_vector or {}
        vector_lambda = ((float(pv.get("PSI", 0.0)) * w["psi_mult"]) +
                         (float(pv.get("ENT", 0.0)) * w["ent_mult"]) +
                         (float(pv.get("DEL", 0.0)) * w["del_mult"]))
        stress_multiplier = 1.0 + (grammatical_stress ** 2) * 2.0
        self.lambda_val = (self.lambda_val * w["decay"]) + (
                (lexical_lambda + dark_matter_lambda + vector_lambda) * w["growth"] * stress_multiplier)
        if self.lambda_val > w["scar_thresh"]:
            self.godel_scars += 1
            self.lambda_val *= w["scar_relief"]
        return min(1.0, self.lambda_val)
