"""protocols/zen.py"""

import random
from typing import Any, Dict, Optional, Tuple

from constants import Prisma
from core import LoreManifest
from presets import BoneConfig
from struts import safe_get, ux, ux_format


class ZenGarden:
    def __init__(self, events_ref, config_ref=None):
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.stillness_streak = 0
        self.max_streak = 0
        self.pebbles_collected = 0
        narrative_data = LoreManifest.get_instance().get("narrative_data") or {}
        self.koans = narrative_data.get(
            "ZEN_KOANS", ["The code that is not written has no bugs."]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stillness_streak": self.stillness_streak,
            "max_streak": self.max_streak,
            "pebbles_collected": self.pebbles_collected,
        }

    def load_state(self, data: Dict[str, Any]):
        self.stillness_streak = data.get("stillness_streak", 0)
        self.max_streak = data.get("max_streak", 0)
        self.pebbles_collected = data.get("pebbles_collected", 0)

    def raking_the_sand(self, physics: Any, _bio: Dict) -> Tuple[float, Optional[str]]:
        vol = float(safe_get(physics, "voltage", 0.0))
        drag = float(safe_get(physics, "narrative_drag", 0.0))
        cfg = safe_get(self.cfg, "ZEN", {})
        v_min = float(safe_get(cfg, "VOLTAGE_MIN", 5.0))
        v_max = float(safe_get(cfg, "VOLTAGE_MAX", 12.0))
        d_max = float(safe_get(cfg, "DRAG_MAX", 2.0))
        is_stable = (v_min <= vol <= v_max) and (drag <= d_max)
        if is_stable:
            self.stillness_streak += 1
            self.max_streak = max(self.max_streak, self.stillness_streak)
            efficiency_boost = min(
                float(safe_get(cfg, "EFFICIENCY_CAP", 0.5)),
                self.stillness_streak * float(safe_get(cfg, "EFFICIENCY_SCALAR", 0.05)),
            )
            msg = None
            zen_first = int(float(safe_get(cfg, "ZEN_FIRST_TICK", 1)))
            zen_freq = int(float(safe_get(cfg, "ZEN_MILESTONE_FREQ", 5)))

            if self.stillness_streak == zen_first:
                msg = f"{Prisma.GRY}{ux('protocol_strings', 'zen_enter')}{Prisma.RST}"
            elif self.stillness_streak % zen_freq == 0:
                self.pebbles_collected += 1
                koan = random.choice(self.koans)
                msg = f"{Prisma.CYN}{ux_format('protocol_strings', 'zen_streak', default='Stillness {streak}: {koan} (+{boost}%)', streak=self.stillness_streak, koan=koan, boost=int(efficiency_boost * 100))}{Prisma.RST}"
            return efficiency_boost, msg

        break_thresh = int(float(safe_get(cfg, "STREAK_BREAK_THRESHOLD", 3)))
        if self.stillness_streak > break_thresh:
            break_msg = ux("protocol_strings", "zen_break")
            self.events.log(
                f"{Prisma.GRY}{break_msg}{Prisma.RST}",
                "SYS",
            )
        self.stillness_streak = 0
        return 0.0, None
