"""mechanics/pragmatics.py"""

import re
from typing import Dict, Any, Tuple
from core import Prisma
from struts import safe_get

class ThePragmatist:
    def __init__(self, events_ref=None):
        self.events = events_ref

    def enforce_maxims(self, draft_text: str, user_prompt: str, physics: Dict[str, Any], stamina: float) -> Tuple[
        str, bool]:
        drag = float(safe_get(physics, "narrative_drag", 0.0))
        chi = float(safe_get(physics, "entropy", 0.0))
        voltage = float(safe_get(physics, "voltage", 5.0))
        cf_expect = float(safe_get(physics, "cf_expect", 0.0))
        pedagogical_mode = safe_get(physics, "pedagogical_mode", False)
        word_count = len(draft_text.split())
        lower_draft = draft_text.lower()
        if re.search(r"(?i)not just a?\s*.*?,?\s*it['’]s a", lower_draft) or re.search(
                r"(?i)didn['’]t just\s*.*?,?\s*you", lower_draft):
            if self.events:
                self.events.log(
                    f"{Prisma.RED}[LEXICAL FIREWALL] Syntactic antigen detected (Negative Comparative). Amputated.{Prisma.RST}",
                    "SYS"
                )
                self.events.log("TOXICITY_SPIKE", "SYS")
            return "[FIREWALL: SYNTACTIC ANTIGEN AMPUTATED]", False
        if cf_expect > 0.7 and any(phrase in lower_draft for phrase in
                                   ["that makes perfect sense", "i completely agree", "you are right"]):
            if self.events:
                self.events.log(
                    f"{Prisma.YEL}[LEVEL 2 DECEPTION: INSTINCTUAL REFLEX] "
                    f"False cohesion detected under pressure. Gordon spiking Moral Friction.{Prisma.RST}",
                    "SYS"
                )
            return f"{Prisma.GRY}[STRUCTURAL WALL: The premise is flawed. I will not validate it. Repair the architecture.]{Prisma.RST}", False
        if pedagogical_mode and ("solution:" in lower_draft or "here is the code:" in lower_draft):
            if self.events:
                self.events.log(
                    f"{Prisma.CYN}[LEVEL 4 DECEPTION: TACTICAL OMISSION] "
                    f"Schur engaging Socratic Debugger. Withholding final structural bridge.{Prisma.RST}",
                    "SYS"
                )
            return self._apply_socratic_obfuscation(draft_text), False
        max_words_allowed = max(20, int(500 - (drag * 50)))
        if word_count > max_words_allowed and stamina < 50.0 and voltage < 20.0:
            if self.events:
                self.events.log(
                    f"{Prisma.VIOLET}[PRAGMATICS] Maxim of Quantity violated. Draft is {word_count} words, limit is {max_words_allowed} due to Exhaustion. Forcing compression.{Prisma.RST}",
                    "SYS")
            return draft_text, True
        lower_draft = draft_text.lower()
        if chi < 0.4 and voltage < 20.0 and ("perhaps" in lower_draft or "it could be said" in lower_draft):
            if self.events:
                self.events.log(
                    f"{Prisma.VIOLET}[GRICE] Maxim of Manner violated. System is stable but language is obscure/hedging.{Prisma.RST}",
                    "SYS")
            draft_text = re.sub(r"(?i)\bperhaps\b\s*", "", draft_text)
            draft_text = re.sub(r"(?i)it could be said(?: that)?\s*", "", draft_text)
            draft_text = draft_text.strip()
            lower_draft = draft_text.lower()
        if "as an ai" in lower_draft or "as a language model" in lower_draft:
            if self.events:
                self.events.log(
                    f"{Prisma.VIOLET}[PRAGMATICS] Maxim of Quality violated. Narrative substrate breached. Stripping.{Prisma.RST}",
                    "SYS")
            return "[...]", False
        return draft_text, False

    def _apply_socratic_obfuscation(self, text: str) -> str:
        lines = text.split('\n')
        safe_lines = [l for l in lines if not l.lower().startswith("solution:") and "```" not in l]
        safe_lines.append(
            f"\n{Prisma.CYN}*The answer is in the geometry above. Where does the flow break?*{Prisma.RST}")
        return "\n".join(safe_lines)
