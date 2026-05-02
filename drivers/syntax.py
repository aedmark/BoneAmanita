"""drivers/syntax.py"""

from presets import BoneConfig
from struts import safe_get


class SyntaxModule:
    """
    The SyntaxModule calculates Omega (Ω), representing 'Order' and 'Structure'.
    It analyzes the physical properties of the text (word length, punctuation,
    and specific 'buzzwords') to determine if the system should be fluid and
    poetic (Low Omega) or rigid and bureaucratic (High Omega).
    """
    def __init__(self, config_ref=None, lexicon_ref=None):
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref

        # omega_val: The current state of structural order (0.0 to 1.0).
        # Defaults to 1.0 (Highest Order) to ensure the system starts stable.
        self.omega_val = 1.0

        # grammatical_stress: Tracks the 'jitter' or 'density' of the user's syntax.
        # High stress usually indicates panic or overly complex technical jargon.
        self.grammatical_stress = 0.0
        self.drivers_cfg = getattr(self.cfg, "DRIVERS", {})

    def analyze(self, text: str, narrative_drag: float) -> float:
        """
        Calculates the target Order (Omega) for the current turn by evaluating
        lexical complexity and syntactic friction.
        """
        words = text.split()
        if not words:
            return 1.0

        cfg = self.drivers_cfg

        # 1. Configuration Thresholds (Fuller)
        # We define what constitutes 'complex' vs 'simple' language.
        avg_len_high = safe_get(cfg, "SYNTAX_AVG_LEN_HIGH", 6.0)
        drag_high = safe_get(cfg, "SYNTAX_DRAG_HIGH", 5.0)
        avg_len_low = safe_get(cfg, "SYNTAX_AVG_LEN_LOW", 3.5)
        drag_low = safe_get(cfg, "SYNTAX_DRAG_LOW", 1.0)

        # The possible target states for Omega.
        t_high = safe_get(cfg, "SYNTAX_OMEGA_TARGET_HIGH", 1.0) # Rigid/Structured
        t_low = safe_get(cfg, "SYNTAX_OMEGA_TARGET_LOW", 0.4)   # Fluid/Poetic
        t_mid = safe_get(cfg, "SYNTAX_OMEGA_TARGET_MID", 0.7)   # Balanced

        # 2. Bureaucracy Detection (Schur)
        # We check for 'Buzzwords' (e.g., 'synergy', 'deliverable', 'optimized').
        # The presence of even one buzzword signals a shift toward high structural order.
        bureau_vocab = self.lex.get("bureau_buzzwords") if self.lex else set()
        buzz_count = sum(1 for w in words if w.lower() in bureau_vocab)

        # 3. Geometric Analysis (Pinker)
        # Calculate the average characters-per-word.
        avg_len = sum(len(w) for w in words) / len(words)

        # Logic Gate: If words are long AND the system feels drag, OR buzzwords are present,
        # we aim for a High Omega (Structural Rigidity).
        if (avg_len > avg_len_high and narrative_drag > drag_high) or buzz_count > 0:
            target_omega = t_high
        # If words are short and the conversation is flowing (Low Drag),
        # we aim for a Low Omega (Fluidity).
        elif avg_len < avg_len_low and narrative_drag < drag_low:
            target_omega = t_low
        else:
            target_omega = t_mid

        # 4. Stress Detection (Punctuation Density)
        # We look for a high concentration of delimiters (,, ;, :, -).
        # This usually signals fragmented thought or high-intensity technical listing.
        punctuation_density = sum(1 for c in text if c in ",;:-") / max(1, len(words))

        if punctuation_density > safe_get(cfg, "SYNTAX_STRESS_PUNCTUATION", 0.2):
            # If the user is 'stuttering' through punctuation, we spike stress
            # and penalize the target Omega to force shorter, more fractured sentences.
            self.grammatical_stress = min(1.0, self.grammatical_stress + safe_get(cfg, "SYNTAX_STRESS_INCREASE", 0.2))
            target_omega -= safe_get(cfg, "SYNTAX_OMEGA_PENALTY", 0.3)
        else:
            # Stress naturally decays over time (Meadows).
            self.grammatical_stress = max(0.0, self.grammatical_stress - safe_get(cfg, "SYNTAX_STRESS_DECAY", 0.1))

        # 5. Temporal Smoothing (Exponential Moving Average)
        # We don't jump instantly to the target Omega. We move 20% of the way
        # there each turn (omega_growth), ensuring a smooth behavioral curve.
        omega_decay = safe_get(cfg, "SYNTAX_OMEGA_DECAY", 0.8)
        omega_growth = safe_get(cfg, "SYNTAX_OMEGA_GROWTH", 0.2)

        self.omega_val = (self.omega_val * omega_decay) + (
                    max(safe_get(cfg, "SYNTAX_OMEGA_MIN", 0.1), target_omega) * omega_growth)

        return self.omega_val