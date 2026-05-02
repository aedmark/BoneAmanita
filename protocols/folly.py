"""protocols/folly.py

The Folly is a metabolic consumption protocol. It metaphorically "eats" the
vocabulary used in a prompt to generate ATP (Stamina) for the engine.
It encourages lexical diversity by rewarding novel, "meaty" words while
strictly penalizing repetitive prompts (Regurgitation) and punishing the
use of overly corporate or empty vocabulary (Indigestion).
"""

import random
from collections import deque, Counter
from typing import Dict, Tuple, Optional, Any
from struts import ux, safe_get
from presets import BoneConfig
from constants import Prisma
from core import LoreManifest

# Global cache retrieval for narrative strings and flavor text
NARRATIVE_DATA = LoreManifest.get_instance().get("narrative_data") or {}

class TheFolly:
    """
    Acts as the digestive tract of the engine's vocabulary processor.
    Tracks recently used words ('gut_memory') and lifetime word usage
    ('global_tastings') to calculate diminishing returns on energy yield.
    """

    def __init__(self, config_ref=None):
        """
        Initializes the Folly's memory structures.
        """
        self.cfg = config_ref or BoneConfig
        # gut_memory tracks the last 50 words digested to prevent immediate looping
        self.gut_memory = deque(maxlen=50)
        # global_tastings tracks how many times a word has been eaten over the engine's lifetime
        self.global_tastings = Counter()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the digestive state for persistence across sessions."""
        return {
            "gut_memory": list(self.gut_memory),
            "global_tastings": dict(self.global_tastings),
        }

    def load_state(self, data: Dict[str, Any]):
        """Restores the digestive state from a serialized dictionary."""
        self.gut_memory = deque(data.get("gut_memory", []), maxlen=50)
        self.global_tastings = Counter(data.get("global_tastings", {}))

    def audit_desire(self, physics, stamina):
        """
        A pre-flight check to see if the system is too 'full' or over-energized
        to eat. If voltage and stamina are critically high, it clamps the intake.

        Returns:
            A tuple containing the status flag, UI message, ATP yield (0.0), and loot (None).
        """
        voltage = float(safe_get(physics, "voltage", 0.0))
        cfg = getattr(self.cfg, "FOLLY", object())
        m_volt = getattr(cfg, "MAUSOLEUM_VOLTAGE", 80.0)
        m_stam = getattr(cfg, "MAUSOLEUM_STAMINA", 20.0)

        if voltage > m_volt and stamina > m_stam:
            # The system is over-stimulated; refuse to consume more input
            msg1 = ux("protocol_strings", "folly_mausoleum")
            msg2 = ux("protocol_strings", "folly_dilation")
            return "MAUSOLEUM_CLAMP", f"{Prisma.GRY}{msg1}{Prisma.RST}\n   {Prisma.CYN}{msg2}{Prisma.RST}", 0.0, None,

        return None, None, 0.0, None

    def grind_the_machine(
            self, atp_pool: float, clean_words: list,
            lexicon: Dict) -> Tuple[Optional[str], Optional[str], float, Optional[str]]:
        """
        The primary consumption loop. Attempts to find digestible 'meat' in the prompt,
        process it for energy, and apply physiological consequences based on novelty.

        Returns:
            A tuple: (Status Action, Flavor Message, ATP Yield Float, Item Loot)
        """
        # Do not eat if we are already at or above the feeding capacity
        if not (0.0 < atp_pool < self.cfg.FOLLY.FEEDING_CAP):
            return None, None, 0.0, None

        # Sift through the input to find words classified as high-energy "meat"
        meat_words = self._filter_meat_words(clean_words, lexicon)

        # If no dense meat is found, fall back to digesting abstract concepts
        if not meat_words:
            return self._attempt_digest_abstract(clean_words, lexicon)

        # Filter out words we have eaten too recently (preventing spam exploits)
        fresh_meat = [w for w in meat_words if w not in self.gut_memory]

        # If the user is just repeating the exact same meaty words, penalize them
        if not fresh_meat:
            penalty = self.cfg.FOLLY.PENALTY_REGURGITATION
            msg = (f"{Prisma.OCHRE}{ux('protocol_strings', 'folly_reflex').format(target=meat_words[0])}{Prisma.RST}\n"
                   f"   {Prisma.RED}{ux('protocol_strings', 'folly_penalty').format(penalty=penalty)}{Prisma.RST}")
            return "REGURGITATION", msg, -penalty, None

        # We have fresh, valid meat. Digest it.
        return self._eat_meat(fresh_meat, lexicon)

    def _eat_meat(self, fresh_meat: list, lexicon_ref: Any) -> Tuple[str, str, float, Optional[str]]:
        """
        Processes a single valid target word, calculates its diminishing returns,
        and dispenses energy (ATP) and occasional inventory loot.
        """
        target = random.choice(fresh_meat)
        suburban_set = (lexicon_ref.get("suburban") or []) if lexicon_ref else []
        play_set = (lexicon_ref.get("play") or []) if lexicon_ref else []

        # Log the consumption in short-term and lifetime memory
        self.gut_memory.append(target)
        self.global_tastings[target] += 1

        # Penalty: "Suburban" words (e.g., corporate jargon, sterile phrasing) cause indigestion
        if target in suburban_set:
            gags = ux("protocol_strings", "folly_gags")
            return "INDIGESTION", f"{Prisma.MAG}{gags}{Prisma.RST}", -self.cfg.FOLLY.PENALTY_INDIGESTION, "THE_RED_STAPLER",

        # Bonus: "Play" words trigger a small, flat energy spike and grant a whimsical item
        if target in play_set:
            chews = ux("protocol_strings", "folly_chews")
            return "SUGAR_RUSH", f"{Prisma.VIOLET}{chews}{Prisma.RST}", self.cfg.FOLLY.SUGAR_RUSH_YIELD, "QUANTUM_GUM",

        # Standard Digestion: Calculate yield based on lifetime repetitions
        times_eaten = self.global_tastings[target]
        base_yield = getattr(self.cfg.FOLLY, "BASE_YIELD", 10.0)
        decay_exp = getattr(self.cfg.FOLLY, "DECAY_EXPONENT", 0.8)

        # The more a word is used globally, the less energy it provides (diminishing returns)
        decay_factor = decay_exp ** (times_eaten - 1)
        actual_yield = max(2.0, base_yield * decay_factor) # Hard floor of 2.0 ATP

        # If the word yielded a massive amount of energy, drop a high-value loot item
        loot = ("STABILITY_PIZZA"
                if actual_yield >= self.cfg.FOLLY.PIZZA_THRESHOLD else None)

        # Generate narrative flavor text if the word is starting to get old
        flavor_text = ""
        if times_eaten > 3:
            stale_str = ux("protocol_strings", "folly_stale_flavor")
            flavor_text = stale_str.format(times=times_eaten)

        msg1 = ux("protocol_strings", "folly_caffeine")
        msg2 = ux("protocol_strings", "folly_yield")
        msg = (
            f"{Prisma.RED}{msg1.format(target=target.upper(), flavor_text=flavor_text)}{Prisma.RST}\n"
            f"   {Prisma.WHT}{msg2.format(yield_val=actual_yield)}{Prisma.RST}")

        return "MEAT_GRINDER", msg, actual_yield, loot

    @staticmethod
    def _filter_meat_words(clean_words: list, lexicon_ref: Any) -> list:
        """
        Intersects the user's prompt with the system's hardcoded dictionary arrays
        to find words that have physical/metabolic weight.
        """
        if not lexicon_ref:
            return clean_words

        # Combine distinct lexical categories that qualify as 'meat'
        valid_set = set(lexicon_ref.get("heavy") or []) | set(lexicon_ref.get("kinetic") or []) | set(lexicon_ref.get("suburban") or [])
        return [w for w in clean_words if w in valid_set]

    def _attempt_digest_abstract(
            self, clean_words: list,
            lexicon_ref: Any) -> Tuple[str, str, float, Optional[str]]:
        """
        Fallback digestion method when no dense 'meat' is found. Processing abstract
        concepts provides a meager energy yield, resembling 'gruel'.
        """
        abstract_set = set(lexicon_ref.get("abstract") or []) if lexicon_ref else set()

        if abstract_words := [w for w in clean_words if w in abstract_set]:
            yield_val = self.cfg.FOLLY.YIELD_ABSTRACT

            # Use multi-line formatting for the UI string
            msg = (f"{Prisma.GRY}{(ux('protocol_strings', 'folly_sighs') or '').format(target=random.choice(abstract_words).upper())}{Prisma.RST}\n"
                   f"   {Prisma.GRY}{(ux('protocol_strings', 'folly_chalk') or '').format(yield_val=yield_val)}{Prisma.RST}")

            return "GRUEL", msg, yield_val, None

        # If the prompt contained neither meat nor abstraction, it starves the engine
        msg = (f"{Prisma.OCHRE}{ux('protocol_strings', 'folly_indigestion') or ''}{Prisma.RST}\n"
               f"   {Prisma.GRY}{ux('protocol_strings', 'folly_cannot_grind') or ''}{Prisma.RST}\n"
               f"   {Prisma.RED}{ux('protocol_strings', 'folly_starvation') or ''}{Prisma.RST}")

        return "INDIGESTION", msg, 0.0, None