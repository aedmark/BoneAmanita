"""drivers/syntax.py"""

from presets import BoneConfig
from struts import safe_get

class SyntaxModule:
    def __init__(self, config_ref=None, lexicon_ref=None):
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref
        self.omega_val = 1.0
        self.grammatical_stress = 0.0
        self.drivers_cfg = safe_get(self.cfg, "DRIVERS", {})

    def analyze(self, text: str, narrative_drag: float) -> float:
        words = text.split()
        if not words:
            return 1.0
        cfg = self.drivers_cfg
        avg_len_high = float(safe_get(cfg, "SYNTAX_AVG_LEN_HIGH", 6.0))
        drag_high = float(safe_get(cfg, "SYNTAX_DRAG_HIGH", 5.0))
        avg_len_low = float(safe_get(cfg, "SYNTAX_AVG_LEN_LOW", 3.5))
        drag_low = float(safe_get(cfg, "SYNTAX_DRAG_LOW", 1.0))
        t_high = float(safe_get(cfg, "SYNTAX_OMEGA_TARGET_HIGH", 1.0))
        t_low = float(safe_get(cfg, "SYNTAX_OMEGA_TARGET_LOW", 0.4))
        t_mid = float(safe_get(cfg, "SYNTAX_OMEGA_TARGET_MID", 0.7))
        bureau_vocab = self.lex.get("bureau_buzzwords") if self.lex else set()
        buzz_count = sum(1 for w in words if w.lower() in bureau_vocab)
        avg_len = sum(len(w) for w in words) / len(words)
        if (avg_len > avg_len_high and narrative_drag > drag_high) or buzz_count > 0:
            target_omega = t_high
        elif avg_len < avg_len_low and narrative_drag < drag_low:
            target_omega = t_low
        else:
            target_omega = t_mid
        punctuation_density = sum(text.count(c) for c in ",;:-") / max(1, len(words))
        if punctuation_density > float(safe_get(cfg, "SYNTAX_STRESS_PUNCTUATION", 0.2)):
            self.grammatical_stress = min(1.0, self.grammatical_stress + float(safe_get(cfg, "SYNTAX_STRESS_INCREASE", 0.2)))
            target_omega -= float(safe_get(cfg, "SYNTAX_OMEGA_PENALTY", 0.1))
        else:
            self.grammatical_stress = max(0.0, self.grammatical_stress - safe_get(cfg, "SYNTAX_STRESS_DECAY", 0.1))
        omega_decay = safe_get(cfg, "SYNTAX_OMEGA_DECAY", 0.8)
        omega_growth = safe_get(cfg, "SYNTAX_OMEGA_GROWTH", 0.2)
        self.omega_val = (self.omega_val * omega_decay) + (
                max(safe_get(cfg, "SYNTAX_OMEGA_MIN", 0.1), target_omega) * omega_growth)
        return self.omega_val
