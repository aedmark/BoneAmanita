"""/soul/narrativeself.py"""

import random
from typing import Any

from constants import Prisma
# The soul does not exist in a vacuum. It sits atop the physical layer (akashic, core, struts)
# and translates metabolic states (ATP, voltage) into narrative meaning.
from core import LoreManifest
from mechanics.lexicon import LexiconService


class TheEditor:
    """
    An internal adversarial critic. It reviews the system's own narrative chapters.
    Used to prevent the LLM from falling into sycophantic, self-congratulatory loops.
    """
    def __init__(self, lexicon_ref: Any = None):
        self.lex = lexicon_ref if lexicon_ref else LexiconService

    @staticmethod
    def critique(chapter_title: str, stress_mode: bool = False) -> str:
        manifest_data = LoreManifest.get_instance().get("NARRATIVE_DATA", {}) if hasattr(LoreManifest, "get_instance") else {}
        reviews = manifest_data.get("LITERARY_REVIEWS", {})
        pos, neg, conf = reviews.get("POSITIVE", ["Valid."]), reviews.get("NEGATIVE", ["Invalid."]), reviews.get("CONFUSED", ["Unclear."])

        # If the system is under stress, the Editor becomes 'The Witness'—colder, sharper.
        pool, prefix, color = (pos + conf, "[THE WITNESS]", Prisma.CYN) if stress_mode else (pos + neg, "[THE EDITOR]", Prisma.GRY)
        comment = random.choice(pool) if pool else "No comment."
        return f"{color}{prefix}: Re: '{chapter_title}' - \"{comment}\"{Prisma.RST}"

