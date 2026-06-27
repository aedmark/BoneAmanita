"""drivers/syntax.py"""

from presets import BoneConfig
from struts import safe_get


class SyntaxModule:
    def __init__(self, config_ref=None, lexicon_ref=None):
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref
        self.omega_val = 1.0
        self.grammatical_stress = 0.0
        cfg = safe_get(self.cfg, "DRIVERS", {})
        self.bounds = {
            "len_hi": float(safe_get(cfg, "SYNTAX_AVG_LEN_HIGH", 6.0)),
            "drag_hi": float(safe_get(cfg, "SYNTAX_DRAG_HIGH", 5.0)),
            "len_lo": float(safe_get(cfg, "SYNTAX_AVG_LEN_LOW", 3.5)),
            "drag_lo": float(safe_get(cfg, "SYNTAX_DRAG_LOW", 1.0)),
            "t_hi": float(safe_get(cfg, "SYNTAX_OMEGA_TARGET_HIGH", 1.0)),
            "t_lo": float(safe_get(cfg, "SYNTAX_OMEGA_TARGET_LOW", 0.4)),
            "t_mid": float(safe_get(cfg, "SYNTAX_OMEGA_TARGET_MID", 0.7)),
            "s_punct": float(safe_get(cfg, "SYNTAX_STRESS_PUNCTUATION", 0.2)),
            "s_inc": float(safe_get(cfg, "SYNTAX_STRESS_INCREASE", 0.2)),
            "s_dec": float(safe_get(cfg, "SYNTAX_STRESS_DECAY", 0.1)),
            "o_pen": float(safe_get(cfg, "SYNTAX_OMEGA_PENALTY", 0.1)),
            "o_dec": float(safe_get(cfg, "SYNTAX_OMEGA_DECAY", 0.8)),
            "o_gro": float(safe_get(cfg, "SYNTAX_OMEGA_GROWTH", 0.2)),
            "o_min": float(safe_get(cfg, "SYNTAX_OMEGA_MIN", 0.1)),
        }
        self.bureau_vocab = (
            set(self.lex.get("bureau_buzzwords") or []) if self.lex else set()
        )

    def analyze(self, text: str, narrative_drag: float) -> float:
        words = text.split()
        if not words:
            return 1.0
        b = self.bounds
        buzz_count = sum(1 for w in words if w.lower() in self.bureau_vocab)
        avg_len = sum(len(w) for w in words) / len(words)
        if (avg_len > b["len_hi"] and narrative_drag > b["drag_hi"]) or buzz_count > 0:
            target_omega = b["t_hi"]
        elif avg_len < b["len_lo"] and narrative_drag < b["drag_lo"]:
            target_omega = b["t_lo"]
        else:
            target_omega = b["t_mid"]
        punctuation_density = sum(text.count(c) for c in ",;:-") / max(1, len(words))
        if punctuation_density > b["s_punct"]:
            self.grammatical_stress = min(1.0, self.grammatical_stress + b["s_inc"])
            target_omega -= b["o_pen"]
        else:
            self.grammatical_stress = max(0.0, self.grammatical_stress - b["s_dec"])
        self.omega_val = (self.omega_val * b["o_dec"]) + (
            max(b["o_min"], target_omega) * b["o_gro"]
        )
        return self.omega_val
