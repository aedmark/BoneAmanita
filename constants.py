"""constants.py"""

import re
from enum import Enum

class Prisma:
    RST = "\033[0m"
    RED, GRN, YEL, BLU = "\033[31m", "\033[32m", "\033[33m", "\033[34m"
    MAG, CYN, WHT, GRY = "\033[35m", "\033[36m", "\033[97m", "\033[90m"

    INDIGO = "\033[34;1m"
    OCHRE = "\033[33;2m"
    VIOLET = "\033[35;2m"
    SLATE = "\033[30;1m"

    _STRIP_PATTERN = re.compile(r"<span class='[^']+'>|</span>|\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    _COLOR_MAP = {"R": RED, "G": GRN, "Y": YEL, "B": BLU, "M": MAG, "C": CYN, "W": WHT, "0": GRY, "I": INDIGO,
                  "O": OCHRE, "V": VIOLET, "S": SLATE, }

    @classmethod
    def enable_web_mode(cls):
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
        k = str(color_key).strip()
        code = cls._COLOR_MAP.get(k[0].upper() if k else "0", cls.WHT)
        txt = "" if text is None else str(text)
        return f"{code}{txt}" if txt.endswith(cls.RST) else f"{code}{txt}{cls.RST}"

    @classmethod
    def strip(cls, text: str) -> str:
        return cls._STRIP_PATTERN.sub("", str(text)) if text is not None else ""

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