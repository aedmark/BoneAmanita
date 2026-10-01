"""
Mycelium: A generalized library for state-driven, biologically-constrained agentic workflows.
Extracted from the BoneAmanita engine.
"""

from .soma import Soma, ExhaustionError
from .prism import Prism
from .macrophage import Macrophage, ToxicityError
from .strata import Strata

__version__ = "0.1.0"
__all__ = ["Soma", "ExhaustionError", "Prism", "Macrophage", "ToxicityError", "Strata"]
