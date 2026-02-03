# bone_pipeline.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

@dataclass
class CycleContext:
    """
    A structural container for the state of a single turn.
    Pinker Note: Explicitly naming the context reduces cognitive load.
    Fuller Note: This acts as the tension strut holding the turn data together.
    """
    input_text: str
    clean_words: List[str] = field(default_factory=list)
    physics: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)

    # State flags
    is_alive: bool = True
    refusal_triggered: bool = False
    refusal_packet: Optional[Dict] = None

    # Biological results
    bio_result: Dict = field(default_factory=dict)
    world_state: Dict = field(default_factory=dict)
    mind_state: Dict = field(default_factory=dict)

    # Metrics
    timestamp: float = field(default_factory=time.time)

    def log(self, message: str):
        """Adds a message to the cycle logs."""
        self.logs.append(message)

class EventBus:
    def __init__(self):
        self.buffer = []

    def log(self, text: str, category: str = "SYSTEM"):
        self.buffer.append({
            "text": text,
            "category": category,
            "timestamp": time.time()
        })

    def flush(self) -> List[Dict]:
        logs = list(self.buffer)
        self.buffer.clear()
        return logs

@dataclass
class PhysicsPacket:
    """
    A strictly typed container for physical reality.
    Pinker Note: Explicit attributes > Dictionary keys.
    """
    voltage: float
    narrative_drag: float
    repetition: float
    clean_words: List[str]
    counts: Dict[str, int]
    vector: Dict[str, float]
    # Optional fields with defaults to prevent breakage
    psi: float = 0.0
    kappa: float = 0.0
    beta_index: float = 1.0
    turbulence: float = 0.0
    raw_text: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Factory to convert the legacy dictionary if needed."""
        # Filter out keys that don't match the dataclass fields to prevent errors
        valid_keys = cls.__annotations__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)