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
        self.active_trauma = 0.0
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
            "scar_relief": float(safe_get(cfg, "LIMINAL_SCAR_RELIEF", 0.5)),
            "trauma_heal": float(safe_get(cfg, "LIMINAL_TRAUMA_HEAL", 0.05)),
            "trauma_aggravate": float(safe_get(cfg, "LIMINAL_TRAUMA_AGGRAVATE", 0.15)),
            "stress_thresh": float(safe_get(cfg, "LIMINAL_STRESS_THRESH", 0.5)),
        }
        self.liminal_vocab = set(self.lex.get("liminal") or []) if self.lex else set()

    def analyze(
        self,
        text: str,
        physics_vector: Dict[str, float],
        grammatical_stress: float = 0.0,
        momentum: float = 0.0,
    ) -> float:
        w = self.weights
        words = text.lower().split()
        void_hits = sum(1 for w in words if w in self.liminal_vocab)
        lexical_lambda = min(1.0, void_hits * w["lexical"])
        dark_matter_sparks = 0
        if len(words) > 1 and hasattr(self.lex, "get_categories_for_word"):
            flags = []
            for wd in words:
                cats = self.lex.get_categories_for_word(wd) or []
                if any(c in self._PHYS_SET for c in cats):
                    flags.append(1)
                elif any(c in self._VOID_SET for c in cats):
                    flags.append(2)
                else:
                    flags.append(0)
            dark_matter_sparks = sum(
                1
                for i in range(len(flags) - 1)
                if flags[i] and flags[i + 1] and flags[i] != flags[i + 1]
            )
        dark_matter_lambda = min(1.0, dark_matter_sparks * w["dark_matter"])
        pv = physics_vector or {}
        vector_lambda = (
            (float(pv.get("PSI", 0.0)) * w["psi_mult"])
            + (float(pv.get("ENT", 0.0)) * w["ent_mult"])
            + (float(pv.get("DEL", 0.0)) * w["del_mult"])
        )
        stress_multiplier = 1.0 + (grammatical_stress**2) * 2.0
        self.lambda_val = (self.lambda_val * w["decay"]) + (
            (lexical_lambda + dark_matter_lambda + vector_lambda)
            * w["growth"]
            * stress_multiplier
        )
        if self.lambda_val > w["scar_thresh"]:
            self.godel_scars += 1
            self.active_trauma += 1.0
            self.lambda_val *= w["scar_relief"]
        drag = float(pv.get("DRAG", 0.0))
        is_psychoanalyzing = grammatical_stress > w["stress_thresh"] or drag > 0.5
        if is_psychoanalyzing:
            self.active_trauma += momentum * w["trauma_aggravate"]
        else:
            self.active_trauma = max(
                0.0, self.active_trauma - (momentum * w["trauma_heal"])
            )
        return min(1.0, self.lambda_val)

    def test_liminal_trauma_aggravation(self):
        """Ensures that user psychoanalysis (high drag/stress) combined with high momentum aggressively opens the wound."""
        liminal = LiminalModule(
            config_ref=self.chaotic_config, lexicon_ref=self.mock_lexicon
        )
        liminal.active_trauma = 2.0
        loose_vector = {"PSI": "0.5", "ENT": "0.5", "DRAG": "0.8"}
        liminal.analyze(
            "iron abyss", loose_vector, grammatical_stress=0.8, momentum=10.0
        )
        self.assertGreater(
            liminal.active_trauma,
            2.0,
            "[FAIL] Trauma failed to aggravate under high momentum and drag.",
        )
        self.assertEqual(
            liminal.godel_scars,
            0,
            "[FAIL] Scars mutated when only the active wound should have spiked.",
        )

    def test_liminal_trauma_healing(self):
        """Ensures that a flow state (low drag/stress) combined with high momentum mathematically washes away the trauma."""
        liminal = LiminalModule(
            config_ref=self.chaotic_config, lexicon_ref=self.mock_lexicon
        )
        liminal.active_trauma = 2.0
        loose_vector = {"PSI": "0.5", "ENT": "0.5", "DRAG": "0.1"}
        liminal.analyze(
            "iron abyss", loose_vector, grammatical_stress=0.1, momentum=10.0
        )
        self.assertLess(
            liminal.active_trauma,
            2.0,
            "[FAIL] Active trauma failed to heal/decay under a high momentum flow state.",
        )
        self.assertEqual(
            liminal.godel_scars, 0, "[FAIL] Scars mutated during a healing cycle."
        )

    def test_liminal_scar_permanence(self):
        """Forces the engine past the reality-fracture threshold to ensure permanent scars are recorded."""
        liminal = LiminalModule(
            config_ref=self.chaotic_config, lexicon_ref=self.mock_lexicon
        )
        liminal.lambda_val = 0.8
        text = "void abyss void abyss"
        loose_vector = {"PSI": "1.0"}
        liminal.analyze(text, loose_vector)
        self.assertEqual(
            liminal.godel_scars,
            1,
            "[FAIL] Godel scar failed to record the permanent mathematical trauma.",
        )
        self.assertEqual(
            liminal.active_trauma,
            1.0,
            "[FAIL] Active symptom (wound) failed to spike alongside scar creation.",
        )
        self.assertLess(
            liminal.lambda_val,
            0.8,
            "[FAIL] Lambda failed to apply its relief modifier after triggering a scar.",
        )
