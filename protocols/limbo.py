"""protocols/limbo.py"""

import json
import random
from collections import deque
from typing import Any, Dict

from constants import Prisma
from core import LoreManifest
from presets import BoneConfig
from struts import safe_get, ux


class LimboLayer:
    MAX_ECTOPLASM = 50

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg = safe_get(self.cfg, "LIMBO", {})
        self.MAX_ECTOPLASM = int(safe_get(cfg, "MAX_ECTOPLASM", 50))
        self.ghosts = deque(maxlen=self.MAX_ECTOPLASM)
        self.haunt_chance = float(safe_get(cfg, "HAUNT_CHANCE", 0.05))
        self.stasis_leak = 0.0
        narrative_data = LoreManifest.get_instance().get("narrative_data") or {}
        self.stasis_screams = narrative_data.get(
            "CASSANDRA_SCREAMS", ["BANGING ON THE GLASS", "IT'S TOO COLD", "LET ME OUT"]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"ghosts": list(self.ghosts), "stasis_leak": self.stasis_leak}

    def load_state(self, data: Dict[str, Any]):
        self.ghosts = deque(data.get("ghosts", []), maxlen=self.MAX_ECTOPLASM)
        self.stasis_leak = data.get("stasis_leak", 0.0)

    def absorb_dead_timeline(self, filepath: str) -> None:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            self._extract_ghosts(data)
        except (IOError, json.JSONDecodeError) as e:
            err_msg = ux("protocol_strings", "limbo_absorb_fail")
            print(f"{Prisma.RED}{err_msg.format(filepath=filepath, e=e)}{Prisma.RST}")

    def _extract_ghosts(self, data: Dict[str, Any]) -> None:
        if "trauma_vector" in data:
            for k, v in data["trauma_vector"].items():
                if v > 0.3:
                    echo_msg = ux("protocol_strings", "limbo_echo")
                    self.ghosts.append(echo_msg.format(k=k))
        if "mutations" in data and "heavy" in data["mutations"]:
            bones = data["mutations"]["heavy"]
            self.ghosts.extend(random.sample(bones, min(3, len(bones))))

    def trigger_stasis_failure(self, intended_thought):
        self.stasis_leak = min(100.0, self.stasis_leak + 1.0)
        horror = random.choice(self.stasis_screams)
        self.ghosts.append(f"{Prisma.VIOLET}{horror}{Prisma.RST}")
        err_msg = ux("protocol_strings", "limbo_stasis_err")
        return f"{Prisma.CYN}{err_msg.format(thought=intended_thought, horror=horror)}{Prisma.RST}"

    def haunt(self, text):
        from struts import safe_get

        cfg = safe_get(self.cfg, "LIMBO", {})
        l_chance = float(safe_get(cfg, "LEAK_DECAY_CHANCE", 0.2))
        l_amount = float(safe_get(cfg, "LEAK_DECAY_AMOUNT", 0.5))
        if self.stasis_leak > 0:
            if random.random() < l_chance:
                self.stasis_leak = max(0.0, self.stasis_leak - l_amount)
                scream = random.choice(self.stasis_screams)
                return f"{text} ...{Prisma.RED}{scream}{Prisma.RST}..."
        if self.ghosts and random.random() < self.haunt_chance:
            spirit = random.choice(self.ghosts)
            return f"{text} ...{Prisma.GRY}{spirit}{Prisma.RST}..."
        return text
