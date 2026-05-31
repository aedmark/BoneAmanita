"""/soul/traitvector.py"""

from dataclasses import dataclass
from typing import Dict, ClassVar

@dataclass
class TraitVector:
    curiosity: float = 0.5
    cynicism: float = 0.5
    hope: float = 0.5
    discipline: float = 0.5
    wisdom: float = 0.1
    empathy: float = 0.5
    _TRAITS: ClassVar[set] = {"curiosity", "cynicism", "hope", "discipline", "wisdom", "empathy", }

    def __post_init__(self):
        self._clamp_all()

    def to_dict(self):
        return {k.upper(): getattr(self, k) for k in self._TRAITS}

    @classmethod
    def from_dict(cls, data: Dict):
        kwargs = {k: float(data.get(k.upper(), 0.5)) for k in cls._TRAITS}
        return cls(**kwargs)

    def _clamp(self, val: float) -> float:
        return max(0.0, min(1.0, float(val)))

    def adjust(self, trait: str, delta: float):
        t = trait.lower()
        if t in self._TRAITS:
            setattr(self, t, self._clamp(getattr(self, t) + delta))

    def normalize(self, decay_rate: float):
        self.curiosity = self._clamp(self.curiosity + ((0.5 - self.curiosity) * decay_rate))
        self.cynicism = self._clamp(self.cynicism + ((0.5 - self.cynicism) * decay_rate))
        self.hope = self._clamp(self.hope + ((0.5 - self.hope) * decay_rate))
        self.discipline = self._clamp(self.discipline + ((0.5 - self.discipline) * decay_rate))
        self.empathy = self._clamp(self.empathy + ((0.5 - self.empathy) * decay_rate))
        self.wisdom = self._clamp(self.wisdom + ((0.1 - self.wisdom) * decay_rate))

    def _clamp_all(self):
        self.curiosity = self._clamp(self.curiosity)
        self.cynicism = self._clamp(self.cynicism)
        self.hope = self._clamp(self.hope)
        self.discipline = self._clamp(self.discipline)
        self.empathy = self._clamp(self.empathy)
        self.wisdom = self._clamp(self.wisdom)
