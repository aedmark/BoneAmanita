"""constants.py"""

import re
from enum import Enum


class Prisma:
    """
    Immutable color registry.
    The engine speaks ANSI exclusively. Web consumers must translate at the boundary.
    """

    RED = "\033[31m"
    GRN = "\033[32m"
    YEL = "\033[33m"
    BLU = "\033[34m"
    MAG = "\033[35m"
    CYN = "\033[36m"
    WHT = "\033[97m"
    GRY = "\033[90m"
    INDIGO = "\033[34;1m"
    OCHRE = "\033[33;2m"
    VIOLET = "\033[35;2m"
    SLATE = "\033[30;1m"
    RST = "\033[0m"

    _ANSI_MAP = {
        "R": RED,
        "G": GRN,
        "Y": YEL,
        "B": BLU,
        "M": MAG,
        "C": CYN,
        "W": WHT,
        "0": GRY,
        "I": INDIGO,
        "O": OCHRE,
        "V": VIOLET,
        "S": SLATE,
    }

    _STRIP_PATTERN = re.compile(
        r"<span class='[^']+'>|</span>"
        r"|\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
    )

    _ANSI_TO_HTML = {
        RED: "<span class='prisma-red'>",
        GRN: "<span class='prisma-grn'>",
        YEL: "<span class='prisma-yel'>",
        BLU: "<span class='prisma-blu'>",
        MAG: "<span class='prisma-mag'>",
        CYN: "<span class='prisma-cyn'>",
        WHT: "<span class='prisma-wht'>",
        GRY: "<span class='prisma-gry'>",
        INDIGO: "<span class='prisma-indigo'>",
        OCHRE: "<span class='prisma-ochre'>",
        VIOLET: "<span class='prisma-violet'>",
        SLATE: "<span class='prisma-slate'>",
        RST: "</span>",
    }

    @classmethod
    def paint(cls, text: str, color_key: str = "0") -> str:
        """Standard CLI painting."""
        k = str(color_key).strip()
        code = cls._ANSI_MAP.get(k[0].upper() if k else "0", cls.WHT)
        txt = "" if text is None else str(text)
        if txt.endswith(cls.RST):
            return f"{code}{txt}"
        return f"{code}{txt}{cls.RST}"

    @classmethod
    def strip(cls, text: str) -> str:
        """Removes all ANSI and HTML tags."""
        return cls._STRIP_PATTERN.sub("", str(text)) if text else ""

    @classmethod
    def translate_to_web(cls, text: str) -> str:
        """
        [WEB BOUNDARY OVERRIDE]
        Replaces ANSI codes with corresponding HTML span classes.
        Call this in your Web API response formatter, NOT inside the engine.
        """
        if not text:
            return ""
        result = text.replace(cls.RST, cls._ANSI_TO_HTML[cls.RST])
        for ansi_code, html_span in cls._ANSI_TO_HTML.items():
            if ansi_code != cls.RST:
                result = result.replace(ansi_code, html_span)
        return result


class LoreCategory(Enum):
    LEXICON = "lexicon"
    SCENARIOS = "scenarios"
    GORDON = "gordon"
    GORDON_LOGS = "gordon_logs"
    GENETICS = "genetics"
    DEATH = "death"
    ALMANAC = "almanac"
    DREAMS = "dreams"


class RealityLayer:
    TERMINAL = 0
    SIMULATION = 1
    VILLAGE = 2
    DEBUG = 3
    DEEP_CX = 4

    @classmethod
    def get_rules(cls, depth: int, boot_mode: str = "ADVENTURE") -> dict:
        """Absolute source of truth for Grammar Policies."""
        rules = {
            "allow_narrative": depth in (cls.SIMULATION, cls.DEEP_CX, cls.DEBUG),
            "allow_commands": depth >= cls.SIMULATION,
            "allow_meta": depth >= cls.DEBUG,
            "raw_output": depth == cls.DEEP_CX,
            "system_override": depth == cls.DEBUG,
        }
        if boot_mode == "TECHNICAL":
            rules["allow_narrative"] = True
        return rules
