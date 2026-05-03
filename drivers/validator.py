"""drivers/validator.py"""

from typing import Any
from core import LoreManifest
from presets import BoneConfig
from struts import safe_get

class CongruenceValidator:
    """
    The CongruenceValidator acts as the Quality Assurance layer (Fuller).
    It measures how mathematically aligned ('congruent') the generated text is
    with the currently active archetype or persona. It ensures that if the system
    claims to be 'THE JESTER', it is actually using the Jester's vocabulary.
    """
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig

        # last_phi tracks the previous turn's resonance score, allowing us
        # to measure if the system is drifting out of character over time.
        self.last_phi = 1.0

        # We lazy-load the archetype map to save memory. It remains None until needed.
        self._archetype_map = None

    @property
    def map(self):
        """
        Lazy-loads and caches the 'LENSES' configuration from the LoreManifest.
        This dictionary contains the specific vocabularies and keywords expected
        for each distinct archetype.
        """
        if self._archetype_map is None:
            self._archetype_map = LoreManifest.get_instance(config_ref=self.cfg).get("LENSES") or {}
        return self._archetype_map

    def calculate_resonance(self, text: str, context: Any) -> float:
        """
        Calculates the resonance (tone_score) by intersecting the generated text
        with the active archetype's ideal vocabulary matrix.
        """
        if not text:
            return 0.0

        cfg = getattr(self.cfg, "DRIVERS", None)
        default_lens = getattr(cfg, "DEFAULT_LENS", "OBSERVER")
        raw_lens = getattr(context, "active_lens", default_lens)

        # Schur Heuristic: Normalize the input. We don't care if the system logged
        # "The Jester", "the jester", or "JESTER". We strip it down to the raw key.
        archetype = raw_lens.upper().replace("THE ", "")

        # We start with a baseline assumption of competence (usually 0.8).
        # The system shouldn't fail validation just because it didn't use a catchphrase.
        tone_score = getattr(cfg, "CONGRUENCE_BASE_TONE", 0.8)

        # Fetch the expected vocabulary for this specific archetype.
        target_data = self.map.get(archetype, {})

        if isinstance(target_data, dict):
            # Compile the target vocabulary into a mathematical Set (Pinker).
            # This allows for instant O(1) intersection lookups.
            target_words = ({w.strip().lower() for w in target_data.get("vocab", "").split(",") if w} |
                            {k.lower() for k in target_data.get("keywords", [])})

            # If the context object has already pre-cleaned the generated words,
            # we intersect them with our target dictionary.
            if target_words and hasattr(context, "clean_words"):
                words_to_check = set(w.lower() for w in context.clean_words)

                # exact_hits represents the overlapping semantic space between
                # what was said and what *should* have been said.
                exact_hits = words_to_check.intersection(target_words)
                hits = len(exact_hits)

                # Additive Loop: Every exact vocabulary match acts as a multiplier,
                # increasing the overall tone score for this generation.
                if hits > 0:
                    tone_score += safe_get(cfg, "CONGRUENCE_HIT_BONUS", 0.1) * hits

        # Apply the ceiling. No matter how many keywords were used, the score
        # cannot exceed the hardcoded maximum.
        return min(safe_get(cfg, "CONGRUENCE_MAX_TONE", 1.5), tone_score)