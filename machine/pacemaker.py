"""machine/pacemaker.py"""

from presets import BoneConfig

class ThePacemaker:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.boredom_level = 0.0
        self.heart_rate = 60
        self.BOREDOM_THRESHOLD = getattr(self.cfg, "BOREDOM_THRESHOLD", 10.0)

    def beat(self, stress: float):
        self.heart_rate = 60 + (stress * 20)

    def update(self, repetition_score: float, voltage: float):
        if repetition_score > 0.5 or voltage < 5.0:
            self.boredom_level = min(self.BOREDOM_THRESHOLD * 2.0, self.boredom_level + 1.0)
        else:
            self.boredom_level = max(0.0, self.boredom_level - 2.0)

    def is_bored(self) -> bool:
        return self.boredom_level > self.BOREDOM_THRESHOLD