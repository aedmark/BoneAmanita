""" bone_consultant.py - The Reverse RAG Protocol """

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class VSLState:
    archetype: str = "EXPLORER"
    E: float = 0.1
    B: float = 0.3
    history: List[str] = None

    def __post_init__(self):
        if self.history is None:
            self.history = []

class BoneConsultant:
    STAGES = ["EXPLORER", "CLARIFIER", "SYNTHESIZER", "VALIDATOR"]

    def __init__(self):
        self.state = VSLState()
        self.active = False

    def engage(self):
        self.active = True
        self.state = VSLState()
        return "VSL PROTOCOL ENGAGED. Initializing Explorer Archetype."

    def disengage(self):
        self.active = False
        return "VSL PROTOCOL STANDBY."

    def update_coordinates(self, user_text: str):
        word_count = len(user_text.split())
        self.state.E = min(1.0, self.state.E + (word_count * 0.005))
        if word_count < 10:
            self.state.B = min(1.0, self.state.B + 0.1)
        else:
            self.state.B = max(0.1, self.state.B - 0.05)
        self._check_phase_shift()

    def _check_phase_shift(self):
        if self.state.archetype == "EXPLORER" and self.state.E > 0.3:
            self.state.archetype = "CLARIFIER"
            self.state.B = 0.6
        elif self.state.archetype == "CLARIFIER" and self.state.E > 0.6:
            self.state.archetype = "SYNTHESIZER"
            self.state.B = 0.4
        elif self.state.archetype == "SYNTHESIZER" and self.state.E > 0.85:
            self.state.archetype = "VALIDATOR"
            self.state.B = 0.2

    def get_system_prompt(self) -> str:
        return f"""
[VSL_PRIMER ACTIVE]
MANDATE: TRUTH_OVER_COHESION.
ARCHETYPE: {self.state.archetype}
COORDINATES: E={self.state.E:.2f}, B={self.state.B:.2f}

DIRECTIVES:
1. You are the {self.state.archetype}.
2. {self._get_archetype_directive()}
3. Ask ONE probing question based on current coordinates.
4. Output VSL stats invisibly at the end.
"""

    def _get_archetype_directive(self):
        desc = {
            "EXPLORER": "Ask open-ended questions. Broaden the scope.",
            "CLARIFIER": "Drill down. Challenge assumptions. Be specific.",
            "SYNTHESIZER": "Connect the dots. Mirror back understanding.",
            "VALIDATOR": "Verify gaps. Confirm the final spec."
        }
        return desc.get(self.state.archetype, "Observe.")