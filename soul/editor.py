"""/soul/editor.py"""

import random

from constants import Prisma

from core import LoreManifest


class TheEditor:
    @staticmethod
    def critique(chapter_title: str, stress_mode: bool = False) -> str:
        manifest_data = LoreManifest.get_instance().get("NARRATIVE_DATA", {})
        reviews = manifest_data.get("LITERARY_REVIEWS", {})
        pos, neg, conf = (
            reviews.get("POSITIVE", ["Valid."]),
            reviews.get("NEGATIVE", ["Invalid."]),
            reviews.get("CONFUSED", ["Unclear."]),
        )
        pool, prefix, color = (
            (pos + conf, "[THE WITNESS]", Prisma.CYN)
            if stress_mode
            else (pos + neg, "[THE EDITOR]", Prisma.GRY)
        )
        comment = random.choice(pool) if pool else "No comment."
        return f"{color}{prefix}: Re: '{chapter_title}' - \"{comment}\"{Prisma.RST}"
