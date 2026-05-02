"""drivers/liminal.py"""

from typing import Dict

from presets import BoneConfig
from struts import safe_get


class LiminalModule:
    """
    The LiminalModule calculates Lambda (Λ), representing the 'Liminality' or
    metaphysical depth of the conversation. It tracks when the user pushes
    the boundaries of formal logic, entering spaces of paradox, void, or deep abstraction.
    """
    def __init__(self, config_ref=None, lexicon_ref=None):
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref

        # lambda_val tracks the active, current level of liminal tension (0.0 to 1.0).
        self.lambda_val = 0.0

        # Godel Scars represent permanent structural memories. When the system hits
        # the absolute ceiling of its logical capacity, it takes a "scar" and resets.
        self.godel_scars = 0
        self.drivers_cfg = getattr(self.cfg, "DRIVERS", {})

    def analyze(self, text: str, physics_vector: Dict[str, float]) -> float:
        """
        Calculates the accumulation of liminal energy based on vocabulary,
        syntactic collisions, and the underlying physics of the system.
        """
        cfg = self.drivers_cfg
        words = text.lower().split()

        # 1. Lexical Hits: Direct matches against a known dictionary of liminal concepts.
        liminal_vocab = self.lex.get("liminal") if self.lex else set()
        void_hits = sum(1 for w in words if w in liminal_vocab)
        lexical_lambda = min(1.0, void_hits * safe_get(cfg, "LIMINAL_LEXICAL_WEIGHT", 0.15))

        # 2. Semantic Friction ("Dark Matter Sparks") - Pinker's syntactic collision.
        dark_matter_sparks = 0
        if len(words) > 1 and hasattr(self.lex, "get_categories_for_word"):
            # We classify words into two incompatible semantic domains.
            phys_set, void_set = {"heavy", "kinetic"}, {"abstract", "liminal", "void"}

            # Map the sentence into a sequence of flags: 1 (Physical), 2 (Abstract), or 0 (Neutral).
            flags = [1 if cats & phys_set else (2 if cats & void_set else 0) for w in words
                     if (cats := set(self.lex.get_categories_for_word(w) or []))]

            # A "spark" occurs when an explicitly physical word is placed immediately
            # adjacent to an explicitly abstract/void word, creating deliberate cognitive tension.
            dark_matter_sparks = sum(
                1 for i in range(len(flags) - 1)
                if flags[i] and flags[i + 1] and flags[i] != flags[i + 1])

        dark_matter_lambda = min(
            1.0, dark_matter_sparks * safe_get(cfg, "LIMINAL_DARK_MATTER_WEIGHT", 0.25))

        # 3. Vector Integration: We pull in the macro-physics of the system.
        # PSI (Void/Disconnection), ENT (Entropy/Chaos), DEL (Delta/Silence).
        pv = physics_vector or {}
        vector_lambda = ((pv.get("PSI", 0) * safe_get(cfg, "LIMINAL_VEC_PSI_MULT", 0.5)) +
                         (pv.get("ENT", 0) * safe_get(cfg, "LIMINAL_VEC_ENT_MULT", 0.3)) +
                         (pv.get("DEL", 0) * safe_get(cfg, "LIMINAL_VEC_DEL_MULT", 0.2)))

        # 4. System Dynamics: The Leaky Bucket (Meadows).
        # Liminality naturally decays over time if not fed, but spikes with new inputs.
        self.lambda_val = (self.lambda_val * safe_get(cfg, "LIMINAL_DECAY", 0.7)) + (
                (lexical_lambda + dark_matter_lambda + vector_lambda) *
                safe_get(cfg, "LIMINAL_GROWTH", 0.15))

        # 5. The Pressure Release Valve.
        # If the tension exceeds the carrying capacity of the architecture...
        if self.lambda_val > safe_get(cfg, "LIMINAL_SCAR_THRESHOLD", 0.85):
            # We record a permanent Godel Scar (the system acknowledges a truth it cannot prove/hold).
            self.godel_scars += 1
            # And violently vent the active pressure to prevent a system collapse.
            self.lambda_val *= safe_get(cfg, "LIMINAL_SCAR_RELIEF", 0.5)

        return min(1.0, self.lambda_val)