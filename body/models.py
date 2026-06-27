"""body/models.py"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Biometrics:
    health: float
    stamina: float
    stress_modifier: float = 1.0
    circadian_bias: Optional[Dict[str, float]] = None


@dataclass
class MetabolicReceipt:
    base_cost: float
    drag_tax: float
    inefficiency_tax: float
    total_burn: float
    waste_generated: float
    status: str
    symptom: str = "Nominal"


@dataclass
class SemanticSignal:
    novelty: float = 0.0
    resonance: float = 0.0
    valence: float = 0.0
    coherence: float = 0.0


@dataclass
class BiologicalImpulse:
    cortisol_delta: float = 0.0
    oxytocin_delta: float = 0.0
    dopamine_delta: float = 0.0
    adrenaline_delta: float = 0.0
    stamina_impact: float = 0.0
    somatic_reflex: str = ""


@dataclass
class Qualia:
    color_code: str
    somatic_sensation: str
    tone: str
    internal_monologue_hint: str


@dataclass
class MitochondrialState:
    atp_pool: float = 60.0
    membrane_potential: float = 1.0
    ros_buildup: float = 0.0
    mother_hash: str = "EVE"
    retrograde_signal: str = "QUIET"

    @property
    def efficiency_mod(self) -> float:
        return self.membrane_potential
