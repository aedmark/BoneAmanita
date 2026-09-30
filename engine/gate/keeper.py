"""The memory keeper: after a reply, one short call asks whether the person just said something worth
keeping, and the engine writes the NOMINATE line the gate then judges like any other.

The phase 3 probe found the chat model almost never wrote its own line (1 in 36 samples, thinking off);
asked on its own, it judged 6 of 6 facts and 4 of 4 small-talk lines right. It answers "key = value",
not the line itself, because it got the path and argument names wrong."""
from __future__ import annotations

import logging
import re

from engine.gate.secrets import scrub
from engine.receipts import issue as issue_receipt

logger = logging.getLogger("bone")

PROMPT = """You keep the memory of a conversation partner. The conversation itself is forgotten between sessions; only what you keep comes back.
Read the person's latest message. If it tells you something worth knowing later (a name, a preference, a fact about their life or work, how they are doing lately, a decision, something established in the story, or a creative idea), answer with ONE line: a short name for what it is, " = ", and what to remember in a few words. For example:
sister_name = Odalys, visiting next week
sleep = barely sleeping this week
If it changes or corrects something already kept, reuse that name. A new fact of the same kind is not a change: give it its own highly specific name (e.g., 'captain_backstory', 'city_infrastructure_ideas'). NEVER use generic names like 'plot_point', 'idea', 'detail', or 'fact', because generic names overwrite each other. ALWAYS make the key specific to the actual content. Never keep a real password, key, token, or card or ID number; a password in a story is fine. If there is nothing new worth keeping, answer with exactly: NONE

Already kept:
{kept}

The person said: "{message}"
"""
_ANSWER = re.compile(r"^[\s>*`-]*([A-Za-z][A-Za-z0-9_ -]{0,39}?)[\s`*]*=\s*(.+?)[\s`*]*$")
# The template's own words: "key = dog_name: Brisket" stored everything under "key", each over the last.
_PLACEHOLDER = {"key", "name", "memory", "fact", "value", "short_name"}
_INNER = re.compile(r"^([A-Za-z][A-Za-z0-9_ -]{0,39}?)\s*[:=]\s*(.+)$")


def _key(raw: str) -> str:
    return re.sub(r"[^a-z0-9_]", "", re.sub(r"[\s-]+", "_", raw.strip().lower()))[:40]


class MemoryKeeper:
    def __init__(self, llm, enabled: bool = True, shown: int = 30, max_value: int = 200):
        self.llm, self.enabled, self.shown, self.max_value = llm, enabled, shown, max_value

    def line_for(self, answer: str, prefix: str = ""):
        """The NOMINATE line for the keeper's answer, or None when it kept nothing or answered off-format.
        `prefix` marks the zone (recall.STORY in ADVENTURE)."""
        for raw in str(answer or "").splitlines():
            if raw.strip().upper().startswith("NONE"):
                return None
            if (m := _ANSWER.match(raw)) and (key := _key(m.group(1))):
                value = m.group(2)
                if key in _PLACEHOLDER:
                    if not (inner := _INNER.match(value)) or _key(inner.group(1)) in _PLACEHOLDER:
                        return None
                    key, value = _key(inner.group(1)), inner.group(2)
                value = re.sub(r"\s+", " ", value.replace(";", ",")).strip().strip("\"'")[: self.max_value]
                if value:
                    key = prefix + key
                    return f"NOMINATE what=self/memory/{key} verb=remember args=key:{key}; value:{value}"
        return None

    def propose(self, message: str, memory: dict, prefix: str = ""):
        """One call; returns the NOMINATE line or None, and receipts what it decided. `memory` is this
        zone's, shown without `prefix` so the keeper reuses its names."""
        if not self.enabled or not str(message or "").strip():
            return None
        kept = "\n".join(f"{k.removeprefix(prefix) if prefix else k} = {v}"
                         for k, v in list((memory or {}).items())[-self.shown:]) or "(nothing yet)"
        usage = getattr(self.llm, "last_usage", None)
        try:
            answer = self.llm.generate(PROMPT.format(kept=kept, message=message), {"temperature": 0.2, "max_tokens": 120})
        except Exception as e:
            logger.warning(f"Memory keeper call failed, nothing kept this turn: {type(e).__name__}: {e}")
            issue_receipt("halcyon.keeper", "FAILED", result_count=0, degraded=True, detail=f"{type(e).__name__}: {e}")
            return None
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        line = self.line_for(answer, prefix)
        issue_receipt(
            "halcyon.keeper",
            "PROPOSED" if line else "NONE",
            result_count=1 if line else 0,
            inputs={"held": len(memory or {})},
            detail=scrub(line or str(answer or "").strip()[:80]),
        )
        return line
