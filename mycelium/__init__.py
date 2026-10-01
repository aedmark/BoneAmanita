"""
Mycelium: The Core Biological Logic Root.
Extracted from BoneAmanita. Provides the baseline biological simulation, 
lexical mapping, and prompt composer for all connected 'Fruiting Bodies'.
"""

from .lexicon import LinguisticAnalyzer
from .physics import PhysicsPacket, EnergyState, SpatialState
from .composer import PromptComposer, ResponseValidator
from .store import HalcyonStore

__all__ = [
    "LinguisticAnalyzer",
    "PhysicsPacket",
    "EnergyState",
    "SpatialState",
    "PromptComposer",
    "ResponseValidator",
    "HalcyonStore"
]
from .llm import OllamaInterface
