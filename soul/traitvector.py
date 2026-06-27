"""/soul/traitvector.py"""

from dataclasses import dataclass
from typing import ClassVar, Dict


@dataclass
class TraitVector:
    curiosity: float = 0.5
    cynicism: float = 0.5
    hope: float = 0.5
    discipline: float = 0.5
    wisdom: float = 0.1
    empathy: float = 0.5
    _TRAITS: ClassVar[set] = {
        "curiosity",
        "cynicism",
        "hope",
        "discipline",
        "wisdom",
        "empathy",
    }

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
        for t in self._TRAITS:
            current = getattr(self, t)
            target = 0.1 if t == "wisdom" else 0.5
            setattr(self, t, self._clamp(current + ((target - current) * decay_rate)))

    def _clamp_all(self):
        for t in self._TRAITS:
            setattr(self, t, self._clamp(getattr(self, t)))
