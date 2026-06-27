"""mechanics/pragmatics.py"""

import re
from typing import Any, Dict, Tuple

from core import Prisma


class ThePragmatist:
    _CLICHE_A_RE = re.compile(r"(?i)not just a?\s*.*?,?\s*it['’]s a")
    _CLICHE_B_RE = re.compile(r"(?i)didn")
    _HEDGE_A_RE = re.compile(r"(?i)\bperhaps\b\s*")
    _HEDGE_B_RE = re.compile(r"(?i)it could be said(?: that)?\s*")

    def __init__(self, events_ref=None):
        self.events = events_ref

    def enforce_maxims(
        self, draft_text: str, user_prompt: str, physics: Dict[str, Any], stamina: float
    ) -> Tuple[str, bool]:
        is_phys_dict = isinstance(physics, dict)
        drag = float(
            physics.get("narrative_drag", 0.0)
            if is_phys_dict
            else getattr(physics, "narrative_drag", 0.0)
        )
        chi = float(
            physics.get("entropy", 0.0)
            if is_phys_dict
            else getattr(physics, "entropy", 0.0)
        )
        voltage = float(
            physics.get("voltage", 5.0)
            if is_phys_dict
            else getattr(physics, "voltage", 5.0)
        )
        cf_expect = float(
            physics.get("cf_expect", 0.0)
            if is_phys_dict
            else getattr(physics, "cf_expect", 0.0)
        )
        pedagogical_mode = (
            physics.get("pedagogical_mode", False)
            if is_phys_dict
            else getattr(physics, "pedagogical_mode", False)
        )
        word_count = len(draft_text.split())
        lower_draft = draft_text.lower()
        if self._CLICHE_A_RE.search(draft_text) or self._CLICHE_B_RE.search(draft_text):
            if self.events:
                self.events.log(
                    f"{Prisma.RED}Syntactic antigen detected (Negative Comparative). Amputated.{Prisma.RST}",
                    "SYS",
                )
                self.events.log("TOXICITY_SPIKE", "SYS")
            return "[SYNTACTIC ANTIGEN AMPUTATED]", False
        if cf_expect > 0.7 and any(
            phrase in lower_draft
            for phrase in [
                "that makes perfect sense",
                "i completely agree",
                "you are right",
            ]
        ):
            if self.events:
                self.events.log(
                    f"{Prisma.YEL}False cohesion detected under pressure. Gordon spiking Moral Friction.{Prisma.RST}",
                    "SYS",
                )
            return (
                f"{Prisma.GRY}The premise is flawed. I will not validate it. Repair the architecture.{Prisma.RST}",
                False,
            )
        if pedagogical_mode and (
            "solution:" in lower_draft or "here is the code:" in lower_draft
        ):
            if self.events:
                self.events.log(
                    f"{Prisma.CYN}Schur engaging Socratic Debugger. Withholding final structural bridge.{Prisma.RST}",
                    "SYS",
                )
            return self._apply_socratic_obfuscation(draft_text), False
        max_words_allowed = max(20, int(500 - (drag * 50)))
        if word_count > max_words_allowed and stamina < 50.0 and voltage < 20.0:
            if self.events:
                self.events.log(
                    f"{Prisma.VIOLET}Draft is {word_count} words, limit is {max_words_allowed} due to Exhaustion. Forcing compression.{Prisma.RST}",
                    "SYS",
                )
            return draft_text, True
        lower_draft = draft_text.lower()
        if (
            chi < 0.4
            and voltage < 20.0
            and ("perhaps" in lower_draft or "it could be said" in lower_draft)
        ):
            if self.events:
                self.events.log(
                    f"{Prisma.VIOLET}System is stable but language is obscure/hedging.{Prisma.RST}",
                    "SYS",
                )
            draft_text = self._HEDGE_A_RE.sub("", draft_text)
            draft_text = self._HEDGE_B_RE.sub("", draft_text)
            draft_text = draft_text.strip()
            lower_draft = draft_text.lower()
        if "as an ai" in lower_draft or "as a language model" in lower_draft:
            if self.events:
                self.events.log(
                    f"{Prisma.VIOLET}Narrative substrate breached. Stripping.{Prisma.RST}",
                    "SYS",
                )
            return "[...]", False
        return draft_text, False

    def _apply_socratic_obfuscation(self, text: str) -> str:
        lines = text.split("\n")
        safe_lines = [
            safe_l for safe_l in lines if not safe_l.lower().startswith("solution:") and "```" not in safe_l
        ]
        safe_lines.append(
            f"\n{Prisma.CYN}*The answer is in the geometry above. Where does the flow break?*{Prisma.RST}"
        )
        return "\n".join(safe_lines)
