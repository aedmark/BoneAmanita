import re
from typing import Any, Dict, Tuple

from engine.core import Prisma


class ThePragmatist:

    def __init__(self, events_ref=None):
        self.events = events_ref

    def enforce_maxims(
        self, draft_text: str, user_prompt: str, physics: Dict[str, Any], stamina: float
    ) -> Tuple[str, bool]:
        is_phys_dict = isinstance(physics, dict)
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
        lower_draft = draft_text.lower()
        # Negative comparisons are the gatekeeper's (NEGATIVE_COMPARISON), which can cut one sentence instead of the draft.
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
