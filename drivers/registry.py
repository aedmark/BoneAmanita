"""drivers/registry.py"""

from dataclasses import dataclass, field
from typing import List

from drivers.enneagram import EnneagramDriver
from presets import BoneConfig


@dataclass
class VSLState:
    archetype: str = "EXPLORER"
    E: float = 0.1
    B: float = 0.3
    L: float = 0.0
    O: float = 1.0
    active_modules: List[str] = field(default_factory=list)


class DriverRegistry:
    def __init__(self, events_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.enneagram = EnneagramDriver(events_ref, config_ref=self.cfg)
        self.current_focus = "NONE"
