"""protocols/zen.py"""

import random
from typing import Dict, Tuple, Optional, Any
from core import LoreManifest
from struts import ux, safe_get
from presets import BoneConfig
from constants import Prisma

NARRATIVE_DATA = LoreManifest.get_instance().get("narrative_data") or {}

class ZenGarden:
    def __init__(self, events_ref, config_ref=None):
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.stillness_streak = 0
        self.max_streak = 0
        self.pebbles_collected = 0
        self.koans = NARRATIVE_DATA.get("ZEN_KOANS", ["The code that is not written has no bugs."])

    def to_dict(self) -> Dict[str, Any]:
        return {"stillness_streak": self.stillness_streak, "max_streak": self.max_streak, "pebbles_collected": self.pebbles_collected,}

    def load_state(self, data: Dict[str, Any]):
        self.stillness_streak = data.get("stillness_streak", 0)
        self.max_streak = data.get("max_streak", 0)
        self.pebbles_collected = data.get("pebbles_collected", 0)

    def raking_the_sand(self, physics: Any, _bio: Dict) -> Tuple[float, Optional[str]]:
        vol = float(safe_get(physics, "voltage", 0.0))
        drag = float(safe_get(physics, "narrative_drag", 0.0))
        cfg = getattr(self.cfg, "ZEN", object())
        v_min = getattr(cfg, "VOLTAGE_MIN", 5.0)
        v_max = getattr(cfg, "VOLTAGE_MAX", 12.0)
        d_max = getattr(cfg, "DRAG_MAX", 2.0)
        is_stable = (v_min <= vol <= v_max) and (drag <= d_max)
        if is_stable:
            self.stillness_streak += 1
            self.max_streak = max(self.max_streak, self.stillness_streak)
            efficiency_boost = min(
                getattr(cfg, "EFFICIENCY_CAP", 0.5),
                self.stillness_streak * getattr(cfg, "EFFICIENCY_SCALAR", 0.05))
            msg = None
            if self.stillness_streak == getattr(cfg, "ZEN_FIRST_TICK", 1):
                msg = f"{Prisma.GRY}{ux('protocol_strings', 'zen_enter')}{Prisma.RST}"
            elif self.stillness_streak % getattr(cfg, "ZEN_MILESTONE_FREQ", 5) == 0:
                self.pebbles_collected += 1
                koan = random.choice(self.koans)
                msg = f"{Prisma.CYN}{ux('protocol_strings', 'zen_streak').format(streak=self.stillness_streak, koan=koan, boost=int(efficiency_boost * 100))}{Prisma.RST}"
            return efficiency_boost, msg
        if self.stillness_streak > getattr(cfg, "STREAK_BREAK_THRESHOLD", 3):
            break_msg = ux("protocol_strings", "zen_break")
            self.events.log(f"{Prisma.GRY}{break_msg}{Prisma.RST}", "SYS",)
        self.stillness_streak = 0
        return 0.0, None