"""REM reflection (plan R2): once per sleep, one call reads what was kept since the last reflection, with how
each felt when it was kept, and says what it means together; the engine nominates that through the gate as
an engine-built `reflect`, one per zone, so a story's day is reflected on in the story."""
from __future__ import annotations

import logging
import re

from engine.gate.keeper import _ANSWER, _key
from engine.gate.secrets import scrub
from engine.receipts import issue as issue_receipt

from .feeling import REST, reading
from .recall import STORY

logger = logging.getLogger("bone")

PROMPT = """You are reflecting while the conversation sleeps. These are the things you kept since you last reflected, each with how it felt when you kept it:
{kept}

If together they mean something worth knowing later (what matters to the person, a pattern, what this stretch was about), answer with ONE line: a short name for it, " = ", and what they mean together in one sentence. For example:
busy_week = your sister visits while a release is due, and you care about both
Say it plainly, with the names and specifics, the way a friend would sum up the week; no abstractions like "balancing", "milestone" or "connection". Say only what these memories support. If they do not add up to anything beyond themselves, answer with exactly: NONE
"""
REFLECTION = "reflection."
DREAM_PROMPT = """You are dreaming, between conversations. This is what the last stretch meant, and how it felt:
{meant}

Dream it: two or three sentences of images built from these, the way a real dream bends a day. Keep the names and the things; let them move and change. Do not explain it, name it as a dream, or speak to anyone.{fever}"""
FEVER = " The system is carrying heavy trauma: let the dream turn strange and unsettled."


def mean_feeling(feelings: list) -> dict | None:
    """The sources' chemistry, averaged: a reflection feels like what it came from."""
    feelings = [f for f in feelings if isinstance(f, dict)]
    if not feelings:
        return None
    return {h: round(sum(float(f.get(h, rest)) for f in feelings) / len(feelings), 2) for h, rest in REST.items()}


class MemoryReflector:
    def __init__(self, llm, enabled: bool = True, least: int = 2, max_value: int = 300):
        self.llm, self.enabled, self.least, self.max_value = llm, enabled, least, max_value

    def line_for(self, answer: str, sources: list, prefix: str = ""):
        """The reflect line for the answer, or None when it saw nothing or answered off-format."""
        for raw in str(answer or "").splitlines():
            if raw.strip().upper().startswith("NONE"):
                return None
            if (m := _ANSWER.match(raw)) and (name := _key(m.group(1))):
                value = re.sub(r"\s+", " ", m.group(2).replace(";", ",")).strip().strip("\"'")[: self.max_value]
                if value:
                    key = f"{prefix}{REFLECTION}{name}"
                    return (f"NOMINATE what=self/memory/{key} verb=reflect "
                            f"args=key:{key}; value:{value}; from:{' | '.join(sources)}")
        return None

    def dream(self, meant: dict, feelings: dict, fever: bool = False) -> str | None:
        """REM plan R3: a short dream built from the reflections (name: what it meant) and how they felt; a
        Fever Dream under heavy trauma, labelled so, as the Hypervisor says."""
        if not self.enabled or not meant:
            return None
        lines = "\n".join(f"- {v}" + (f" (felt {', '.join(reading(feelings.get(k)))})" if reading(feelings.get(k)) else "")
                          for k, v in meant.items())
        usage = getattr(self.llm, "last_usage", None)
        try:
            raw = self.llm.generate(DREAM_PROMPT.format(meant=lines, fever=FEVER if fever else ""),
                                    {"temperature": 0.9, "max_tokens": 150})
        except Exception as e:
            logger.warning(f"REM dream failed, no dream this sleep: {type(e).__name__}: {e}")
            issue_receipt("halcyon.dream", "FAILED", result_count=0, degraded=True, detail=f"{type(e).__name__}: {e}")
            raise
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        text = re.sub(r"\s+", " ", re.sub(r"\s*\u2014\s*", ", ", str(raw or ""))).strip().strip("\"'")
        if not text:
            issue_receipt("halcyon.dream", "NONE", result_count=0, inputs={"reflections": len(meant)})
            return None
        issue_receipt("halcyon.dream", "FEVER" if fever else "DREAMT", result_count=1,
                      inputs={"reflections": len(meant)}, detail=scrub(text[:80]))
        return f"Fever Dream: {text}" if fever else text

    def reflect(self, memory: dict, feelings: dict, prefix: str = ""):
        """One call over `memory` (this zone's new memories); returns the line, or None (receipted)."""
        if not self.enabled:
            return None
        kept = "\n".join(f"- {k.removeprefix(prefix)} = {v}" + (f" (felt {', '.join(reading(feelings.get(k)))})"
                                                               if reading(feelings.get(k)) else "")
                         for k, v in memory.items())
        usage = getattr(self.llm, "last_usage", None)
        try:
            answer = self.llm.generate(PROMPT.format(kept=kept), {"temperature": 0.3, "max_tokens": 120})
        except Exception as e:
            logger.warning(f"REM reflection failed, nothing reflected this sleep: {type(e).__name__}: {e}")
            issue_receipt("halcyon.reflect", "FAILED", result_count=0, degraded=True, detail=f"{type(e).__name__}: {e}")
            raise
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        line = self.line_for(answer, list(memory), prefix)
        if not line:  # a line is receipted with the gate's decision on it
            issue_receipt("halcyon.reflect", "NONE", result_count=0,
                          inputs={"memories": len(memory), "zone": "story" if prefix == STORY else "real"},
                          detail=scrub(str(answer or "").strip()[:80]))
        return line
