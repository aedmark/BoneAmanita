"""machine/pacemaker.py"""

from presets import BoneConfig


class ThePacemaker:
    def __init__(self, config_ref=None):
        from struts import safe_get

        self.cfg = config_ref or BoneConfig
        self.boredom_level = 0.0
        self.heart_rate = 60
        cfg = safe_get(self.cfg, "MACHINE", {})
        self.BOREDOM_THRESHOLD = float(
            safe_get(cfg, "PACEMAKER_BOREDOM_THRESHOLD", 10.0)
        )

    def beat(self, stress: float):
        self.heart_rate = 60 + (stress * 20)

    def update(self, repetition_score: float, voltage: float):
        step = self.BOREDOM_THRESHOLD * 0.1
        if repetition_score > 0.5 or voltage < 5.0:
            self.boredom_level = min(
                self.BOREDOM_THRESHOLD * 2.0, self.boredom_level + step
            )
        else:
            self.boredom_level = max(0.0, self.boredom_level - (step * 2.0))

    def is_bored(self) -> bool:
        if self.boredom_level > self.BOREDOM_THRESHOLD:
            self.boredom_level = 0.0
            return True
        return False
