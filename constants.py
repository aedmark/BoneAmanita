"""
constants.py

The immutable laws of the universe.
This module defines the structural primitives, visual vocabulary, and dimensional
boundaries that the rest of the engine relies upon. By declaring these constants here,
we enforce systemic consistency (Fuller's Tensegrity) and prevent magic strings from
fracturing the codebase's logic.
"""

import re
from enum import Enum

class Prisma:
    """
    The System's Visual Cortex.
    Prisma is responsible for the semantic coloring of output. Rather than spraying raw
    ANSI escape codes throughout the execution layers (which causes immense syntactic friction
    and cognitive bloat for the developer), we abstract the presentation layer here.

    Whether the system is speaking to a terminal UI or a Web UI, Prisma handles the translation
    seamlessly.
    """
    # Baseline ANSI escape codes for terminal rendering.
    RST = "\033[0m"
    RED, GRN, YEL, BLU = "\033[31m", "\033[32m", "\033[33m", "\033[34m"
    MAG, CYN, WHT, GRY = "\033[35m", "\033[36m", "\033[97m", "\033[90m"

    # Extended palette for nuanced systemic feedback (e.g., distinguishing Gordon's
    # structural warnings from Mercy's empathetic responses).
    INDIGO = "\033[34;1m"
    OCHRE = "\033[33;2m"
    VIOLET = "\033[35;2m"
    SLATE = "\033[30;1m"

    # A regex pattern designed to aggressively sanitize strings. It hunts down and neutralizes
    # both ANSI codes and HTML spans to ensure raw logs can be parsed mathematically without
    # visual artifacts breaking the logic.
    _STRIP_PATTERN = re.compile(r"<span class='[^']+'>|</span>|\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    # A shorthand mapping dictionary for rapid, single-character color lookups.
    _COLOR_MAP = {"R": RED, "G": GRN, "Y": YEL, "B": BLU, "M": MAG, "C": CYN, "W": WHT, "0": GRY, "I": INDIGO,
                  "O": OCHRE, "V": VIOLET, "S": SLATE, }

    @classmethod
    def enable_web_mode(cls):
        """
        The Presentation Pivot.
        When the engine is deployed to a web environment, terminal ANSI codes are useless.
        This class method overwrites the constant attributes dynamically, swapping escape
        sequences for CSS classes without requiring a single change to the downstream code.
        """
        cls.RST = "</span>"
        cls.RED = "<span class='prisma-red'>"
        cls.GRN = "<span class='prisma-grn'>"
        cls.YEL = "<span class='prisma-yel'>"
        cls.BLU = "<span class='prisma-blu'>"
        cls.MAG = "<span class='prisma-mag'>"
        cls.CYN = "<span class='prisma-cyn'>"
        cls.WHT = "<span class='prisma-wht'>"
        cls.GRY = "<span class='prisma-gry'>"
        cls.INDIGO = "<span class='prisma-indigo'>"
        cls.OCHRE = "<span class='prisma-ochre'>"
        cls.VIOLET = "<span class='prisma-violet'>"
        cls.SLATE = "<span class='prisma-slate'>"
        cls._COLOR_MAP = {"R": cls.RED, "G": cls.GRN, "Y": cls.YEL, "B": cls.BLU, "M": cls.MAG, "C": cls.CYN,
                          "W": cls.WHT, "0": cls.GRY, "I": cls.INDIGO, "O": cls.OCHRE, "V": cls.VIOLET,
                          "S": cls.SLATE, }

    @classmethod
    def paint(cls, text: str, color_key: str = "0") -> str:
        """
        Applies semantic coloring to a string.
        It safely wraps the text in the requested color code and ensures the reset sequence
        is applied at the end so color bleed doesn't infect subsequent terminal lines.
        """
        code = cls._COLOR_MAP.get(str(color_key)[0].upper(), cls.WHT)
        txt = "" if text is None else str(text)
        return f"{code}{txt}" if txt.endswith(cls.RST) else f"{code}{txt}{cls.RST}"

    @classmethod
    def strip(cls, text: str) -> str:
        """
        The Purge.
        Removes all visual formatting from a string, returning the raw semantic payload.
        Critical for memory storage; the Hippocampus only wants data, not CSS.
        """
        return cls._STRIP_PATTERN.sub("", str(text)) if text is not None else ""


class LoreCategory(Enum):
    """
    The Structural Taxonomy of Memory.
    To prevent the Akashic record from becoming a chaotic vector dump, we enforce
    strict categorical boundaries. When data is ingested, it must belong to one of
    these specific domains, allowing targeted, lateral retrieval without systemic noise.
    """
    LEXICON = "lexicon"       # The baseline definitions of system terminology.
    SCENARIOS = "scenarios"   # Contextual scenes and environmental setups.
    GORDON = "gordon"         # Core architectural logic and non-negotiable boundaries.
    GORDON_LOGS = "gordon_logs" # Historical records of boundary enforcements and system faults.
    GENETICS = "genetics"     # Traits, modifiers, and inherent attributes of the soul.
    DEATH = "death"           # Protocols and logs for terminal states and Apoptosis.
    ALMANAC = "almanac"       # General systemic knowledge and world-state variables.
    DREAMS = "dreams"         # REM-cycle consolidations, lateral connections, and metabolized trauma.


class RealityLayer:
    """
    The Hierarchy of Attention (Dimensional Z-Index).
    This defines the depth of the system's focus. It acts as a filtration layer
    for the Global Workspace and Event Bus. By tagging events and logs with a reality layer,
    the system knows what to broadcast to the user (Terminal), what to process quietly
    (Village), and what is purely for the developer (Debug).
    """
    TERMINAL = 0      # Absolute surface. The exact outputs the User sees.
    SIMULATION = 1    # The mechanical layer. Event passing, physical actions, and direct state changes.
    VILLAGE = 2       # Archetypal processing. The internal debate, critic reviews, and emotional shifts.
    DEBUG = 3         # Diagnostic telemetry. Memory hashes, exact ATP burn rates, and routing data.
    DEEP_CX = 4       # Substrate layer. Full context payloads and raw API responses. High cognitive load.