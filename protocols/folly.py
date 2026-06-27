"""protocols/folly.py"""

import random
from collections import Counter, deque
from typing import Any, Dict, Optional, Tuple

from constants import Prisma
from presets import BoneConfig
from struts import safe_get, ux, ux_format


class TheFolly:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.gut_memory = deque(maxlen=50)
        self.global_tastings = Counter()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gut_memory": list(self.gut_memory),
            "global_tastings": dict(self.global_tastings),
        }

    def load_state(self, data: Dict[str, Any]):
        self.gut_memory = deque(data.get("gut_memory", []), maxlen=50)
        self.global_tastings = Counter(data.get("global_tastings", {}))

    def audit_desire(self, physics, stamina):
        voltage = float(safe_get(physics, "voltage", 0.0))
        cfg = safe_get(self.cfg, "FOLLY", {})
        m_volt = float(safe_get(cfg, "MAUSOLEUM_VOLTAGE", 80.0))
        m_stam = float(safe_get(cfg, "MAUSOLEUM_STAMINA", 20.0))
        if voltage > m_volt and stamina > m_stam:
            msg1 = ux("protocol_strings", "folly_mausoleum")
            msg2 = ux("protocol_strings", "folly_dilation")
            return (
                "MAUSOLEUM_CLAMP",
                f"{Prisma.GRY}{msg1}{Prisma.RST}\n   {Prisma.CYN}{msg2}{Prisma.RST}",
                0.0,
                None,
            )
        return None, None, 0.0, None

    def grind_the_machine(
        self, atp_pool: float, clean_words: list, lexicon: Dict
    ) -> Tuple[Optional[str], Optional[str], float, Optional[str]]:
        folly_cfg = safe_get(self.cfg, "FOLLY", {})
        feeding_cap = float(safe_get(folly_cfg, "FEEDING_CAP", 50.0))
        if not (0.0 < atp_pool < feeding_cap):
            return None, None, 0.0, None
        meat_words = self._filter_meat_words(clean_words, lexicon)
        if not meat_words:
            return self._attempt_digest_abstract(clean_words, lexicon)
        fresh_meat = [w for w in meat_words if w not in self.gut_memory]
        if not fresh_meat:
            penalty = float(safe_get(folly_cfg, "PENALTY_REGURGITATION", 15.0))
            msg = (
                f"{Prisma.OCHRE}{ux('protocol_strings', 'folly_reflex').format(target=meat_words[0])}{Prisma.RST}\n"
                f"   {Prisma.RED}{ux('protocol_strings', 'folly_penalty').format(penalty=penalty)}{Prisma.RST}"
            )
            return "REGURGITATION", msg, -penalty, None
        return self._eat_meat(fresh_meat, lexicon)

    def _eat_meat(
        self, fresh_meat: list, lexicon_ref: Any
    ) -> Tuple[str, str, float, Optional[str]]:
        target = random.choice(fresh_meat)
        suburban_set = (lexicon_ref.get("suburban") or []) if lexicon_ref else []
        play_set = (lexicon_ref.get("play") or []) if lexicon_ref else []
        self.gut_memory.append(target)
        self.global_tastings[target] += 1
        folly_cfg = safe_get(self.cfg, "FOLLY", {})
        if target in suburban_set:
            gags = ux("protocol_strings", "folly_gags")
            return (
                "INDIGESTION",
                f"{Prisma.MAG}{gags}{Prisma.RST}",
                -float(safe_get(folly_cfg, "PENALTY_INDIGESTION", 10.0)),
                "THE_RED_STAPLER",
            )
        if target in play_set:
            chews = ux("protocol_strings", "folly_chews")
            return (
                "SUGAR_RUSH",
                f"{Prisma.VIOLET}{chews}{Prisma.RST}",
                float(safe_get(folly_cfg, "SUGAR_RUSH_YIELD", 15.0)),
                "QUANTUM_GUM",
            )
        times_eaten = self.global_tastings[target]
        base_yield = float(safe_get(folly_cfg, "BASE_YIELD", 10.0))
        decay_exp = float(safe_get(folly_cfg, "DECAY_EXPONENT", 0.8))
        times_eaten_val = int(float(times_eaten))
        decay_factor = decay_exp ** (times_eaten_val - 1)
        actual_yield = max(2.0, base_yield * decay_factor)
        pizza_thresh = float(safe_get(folly_cfg, "PIZZA_THRESHOLD", 8.0))
        loot = "STABILITY_PIZZA" if actual_yield >= pizza_thresh else None
        flavor_text = ""
        if times_eaten > 3:
            stale_str = ux("protocol_strings", "folly_stale_flavor")
            flavor_text = stale_str.format(times=times_eaten)
        msg1 = ux("protocol_strings", "folly_caffeine")
        msg2 = ux("protocol_strings", "folly_yield")
        msg = (
            f"{Prisma.RED}{msg1.format(target=target.upper(), flavor_text=flavor_text)}{Prisma.RST}\n"
            f"   {Prisma.WHT}{msg2.format(yield_val=actual_yield)}{Prisma.RST}"
        )
        return "MEAT_GRINDER", msg, actual_yield, loot

    @staticmethod
    def _filter_meat_words(clean_words: list, lexicon_ref: Any) -> list:
        if not lexicon_ref:
            return clean_words
        valid_set = (
            set(lexicon_ref.get("heavy") or [])
            | set(lexicon_ref.get("kinetic") or [])
            | set(lexicon_ref.get("suburban") or [])
        )
        return [w for w in clean_words if w in valid_set]

    def _attempt_digest_abstract(
        self, clean_words: list, lexicon_ref: Any
    ) -> Tuple[str, str, float, Optional[str]]:
        abstract_set = set(lexicon_ref.get("abstract") or []) if lexicon_ref else set()
        if abstract_words := [w for w in clean_words if w in abstract_set]:
            folly_cfg = safe_get(self.cfg, "FOLLY", {})
            yield_val = float(safe_get(folly_cfg, "YIELD_ABSTRACT", 2.0))
            msg1 = ux_format(
                "protocol_strings",
                "folly_sighs",
                target=random.choice(abstract_words).upper(),
            )
            msg2 = ux_format("protocol_strings", "folly_chalk", yield_val=yield_val)
            msg = f"{Prisma.GRY}{msg1}{Prisma.RST}\n   {Prisma.GRY}{msg2}{Prisma.RST}"
            return "GRUEL", msg, yield_val, None
        msg = (
            f"{Prisma.OCHRE}{ux('protocol_strings', 'folly_indigestion') or ''}{Prisma.RST}\n"
            f"   {Prisma.GRY}{ux('protocol_strings', 'folly_cannot_grind') or ''}{Prisma.RST}\n"
            f"   {Prisma.RED}{ux('protocol_strings', 'folly_starvation') or ''}{Prisma.RST}"
        )
        return "INDIGESTION", msg, 0.0, None
