from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

@dataclass
class EnergyState:
    voltage: float = 0.0
    stamina: float = 100.0  # Equivalent to ATP
    health: float = 100.0
    ros: float = 0.0
    cortisol: float = 0.1
    dopamine: float = 0.1

@dataclass
class SpatialState:
    narrative_drag: float = 0.6
    tension: float = 0.0
    flow: float = 0.5

@dataclass
class PhysicsPacket:
    energy: EnergyState = field(default_factory=EnergyState)
    space: SpatialState = field(default_factory=SpatialState)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "energy": asdict(self.energy),
            "space": asdict(self.space)
        }

    def apply_vector(self, vector: Dict[str, float]) -> None:
        """
        Applies a semantic vector (from Lexicon) to the physical state.
        Translates linguistic properties into biological metabolism.
        """
        # Narrative drag is a direct output of "heavy" words + tension
        drag = vector.get("narrative_drag", 0.0) + (vector.get("tension", 0.0) * 0.5)
        self.space.narrative_drag = max(0.6, drag)
        
        # Kinetic flow boosts voltage
        flow = vector.get("flow", 0.0)
        self.space.flow = flow
        self.energy.voltage = min(100.0, self.energy.voltage + (flow * 5.0))
        
        # Calculate ATP/Stamina cost based on drag and flow
        # Base cost of 2.0 per turn, multiplied by drag
        cost = 2.0 * self.space.narrative_drag
        self.energy.stamina = max(0.0, self.energy.stamina - cost)
        
        # Cortisol rises with tension, drops with flow
        self.energy.cortisol = max(0.0, min(1.0, self.energy.cortisol + (vector.get("tension", 0.0) * 0.2) - (flow * 0.1)))

    @classmethod
    def void_state(cls):
        return cls()
