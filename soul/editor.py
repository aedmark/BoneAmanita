"""/soul/editor.py"""

import random
from typing import Any

from constants import Prisma
# The soul does not exist in a vacuum. It sits atop the physical layer (akashic, core, struts)
# and translates metabolic states (ATP, voltage) into narrative meaning.
from core import LoreManifest
from mechanics.lexicon import LexiconService

class TheEditor:
    @staticmethod
    def critique(chapter_title: str, stress_mode: bool = False) -> str:
        manifest_data = LoreManifest.get_instance().get("NARRATIVE_DATA", {})
        reviews = manifest_data.get("LITERARY_REVIEWS", {})
        pos, neg, conf = reviews.get("POSITIVE", ["Valid."]), reviews.get("NEGATIVE", ["Invalid."]), reviews.get("CONFUSED", ["Unclear."])
        pool, prefix, color = (pos + conf, "[THE WITNESS]", Prisma.CYN) if stress_mode else (pos + neg, "[THE EDITOR]", Prisma.GRY)
        comment = random.choice(pool) if pool else "No comment."
        return f"{color}{prefix}: Re: '{chapter_title}' - \"{comment}\"{Prisma.RST}"

