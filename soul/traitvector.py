"""/soul/traitvector.py"""
import json
import os
import random
import time
from dataclasses import dataclass, field, fields
from typing import List, Dict, Optional, Any, Tuple, ClassVar
from brain.akashic import TheAkashicRecord
from presets import BoneConfig
from core import LoreManifest, EventBus
from struts import ux, ux_format, safe_get, safe_set
from mechanics.lexicon import LexiconService
from constants import Prisma


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
        Meadows (Systems Dynamics): Homeostasis.
        Traits naturally decay back toward their biological baselines over time.
        Notice that wisdom decays to 0.1—true wisdom is metabolically expensive
        to maintain and fades quickly without active reinforcement.
        """
        for t in self._TRAITS:
            val = getattr(self, t)
            target = 0.1 if t == "wisdom" else 0.5
            resistance = 1.0 - (1.5 * abs(val - target))
            actual_decay = decay_rate * max(0.1, min(1.0, resistance))
            setattr(self, t, self._clamp(val + ((target - val) * actual_decay)))

    def _clamp_all(self):
        for t in self._TRAITS:
            setattr(self, t, self._clamp(getattr(self, t)))
