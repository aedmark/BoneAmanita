"""drivers/registry.py"""

from dataclasses import dataclass, field
from typing import List
from presets import BoneConfig
from drivers.enneagram import EnneagramDriver

@dataclass
class VSLState:
    """
    The VSLState is the 'Coordinate Cache' (Fuller).
    It stores the core metabolic and cognitive variables that represent the
    system's current state of being. These values act as the 'pulse' of the
    machine, used to steer generation behavior without re-calculating
    complex physics on every single token.
    """
    # archetype: The dominant personality currently leading the Village (e.g., JESTER, GORDON).
    archetype: str = "EXPLORER"

    # E (Energy/Exhaustion): 0.0 (Zen/Rest) to 1.0 (Terminal Burnout).
    # Tracks how much ATP the system has burned through interaction.
    E: float = 0.1

    # B (Beta/Contradiction): Measures the tension between opposing truths.
    # High Beta occurs during deep philosophical or logical paradoxes.
    B: float = 0.3

    # L (Liminality/Lambda): Tracks proximity to the 'Void' or the edge of formal logic.
    L: float = 0.0

    # O (Order/Syntax): 1.0 is rigid, structural, and bureaucratic.
    # 0.0 is fluid, poetic, or chaotic.
    O: float = 1.0

    # active_modules: A dynamic list of loaded Mod Chips (e.g., 'LIMINAL', 'SYNTAX').
    active_modules: List[str] = field(default_factory=list)

class DriverRegistry:
    """
    The DriverRegistry is the 'Central Switchboard' (Fuller).
    It maintains the state container and manages the identity-routing drivers.
    It ensures that the Enneagram and other governance tools have a
    consistent reference to the system's global state and configuration.
    """
    def __init__(self, events_ref, config_ref=None):
        # We ingest the global config and event bus to maintain
        # system-wide synchronization.
        self.cfg = config_ref or BoneConfig

        # The Enneagram is the decision-engine that shifts archetypes based on physics.
        self.enneagram = EnneagramDriver(events_ref, config_ref=self.cfg)

        # current_focus: An optional tag to track what the system is currently
        # prioritizing (e.g., "DEBUGGING", "CO-REGULATION").
        self.current_focus = "NONE"