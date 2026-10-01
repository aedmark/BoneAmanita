from dataclasses import dataclass, field
from typing import Dict, Any

class ExhaustionError(RuntimeError):
    """Raised when ATP reaches absolute zero, triggering metabolic collapse."""
    pass

@dataclass
class Soma:
    """
    The metabolic state tracker. 
    Maintains simulated biochemical and physical constraints for an AI agent.
    """
    atp: float = 100.0
    voltage: float = 30.0
    cortisol: float = 0.0
    dopamine: float = 0.0
    serotonin: float = 0.0
    oxytocin: float = 0.0
    resonance: float = 0.0

    def expend(self, amount: float) -> None:
        """Expend ATP for cognitive or physical tasks."""
        self.atp = max(0.0, self.atp - amount)
        if self.atp == 0.0:
            raise ExhaustionError("Metabolic collapse: Insufficient ATP.")

    def rest(self, amount: float) -> None:
        """Recover ATP through simulated idle/REM states."""
        self.atp = min(100.0, self.atp + amount)

    def stress(self, amount: float) -> None:
        """Increase cortisol and voltage due to tension or pathogens."""
        self.cortisol = min(1.0, self.cortisol + amount)
        self.voltage = min(100.0, self.voltage + (amount * 50))

    def reward(self, amount: float) -> None:
        """Increase dopamine due to resolution or resonance."""
        self.dopamine = min(1.0, self.dopamine + amount)
        self.cortisol = max(0.0, self.cortisol - (amount / 2))

    def to_affect_vector(self) -> list[float]:
        """
        Returns a normalized 6D vector representing the current emotional/physical state.
        Mapping: [voltage/100, resonance, dopamine, cortisol, serotonin, oxytocin]
        """
        return [
            max(0.0, min(1.0, self.voltage / 100.0)),
            self.resonance,
            self.dopamine,
            self.cortisol,
            self.serotonin,
            self.oxytocin
        ]
