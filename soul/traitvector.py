"""/soul/traitvector.py"""
from dataclasses import dataclass
from typing import Dict, ClassVar


@dataclass
class TraitVector:
    """
    The epigenetic sliders of the system's personality.
    Instead of hardcoding an archetype, the system drifts organically based on
    conversational trauma, oxytocin (connection), and fatigue.
    """
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
        """Physical geometry has limits. Values cannot escape the [0.0, 1.0] manifold."""
        return max(0.0, min(1.0, float(val)))

    def adjust(self, trait: str, delta: float):
        t = trait.lower()
        if t in self._TRAITS:
            setattr(self, t, self._clamp(getattr(self, t) + delta))

    def normalize(self, decay_rate: float):
        """
        Meadows: Linear Homeostasis.
        Ensures a consistent pull toward the biological baseline (0.1 for Wisdom, 0.5 for others)
        without the 'resistance' trap that causes trait stagnation.
        """
        for t in self._TRAITS:
            val = getattr(self, t)
            target = 0.1 if t == "wisdom" else 0.5
            # Pull the value toward the target by a fixed percentage of the distance.
            setattr(self, t, self._clamp(val + ((target - val) * decay_rate)))

    def _clamp_all(self):
        for t in self._TRAITS:
            setattr(self, t, self._clamp(getattr(self, t)))
