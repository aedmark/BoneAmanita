"""Sūtra Consolidator (Vedas Path C): crystallizes episodic memories and reflections into
dense, minimal-syllable invariant seeds (Alpākṣaram Asandigdham) during sleep and idle cycles.

A Sūtra captures an enduring invariant, ground rule, or personal pattern that holds true across
multiple turns, using minimal tokens and zero conversational padding."""
from __future__ import annotations

import logging
import re

from engine.gate.keeper import _ANSWER, _key
from engine.gate.secrets import scrub
from engine.receipts import issue as issue_receipt

from .recall import STORY

logger = logging.getLogger("bone")

SUTRA_PREFIX = "sutra."

PROMPT = """You are crystallizing enduring knowledge while the conversation sleeps.
These are the memories and reflections kept so far:
{kept}

Extract any enduring invariant, persistent preference, ground rule, or core pattern that holds true across multiple moments.
Formulate each as a SŪTRA:
- Alpākṣaram: minimal words (under 20 words, under 120 characters)
- Asandigdham: unambiguous, declarative truth
- Sāravat: capturing the essential invariant, not transient news
- Astobham: zero filler words, zero conversational framing (no "User prefers", no "It seems that")

Answer with one line per invariant (at most two):
short_name = essential invariant

For example:
working_cadence = builds in short reviewable steps; refuses unverified claims
communication_rule = direct neutral observations; never gives unsolicited advice

If these memories are only transient news and do not reveal an enduring invariant, answer with exactly: NONE
"""


class SutraConsolidator:
    def __init__(self, llm, enabled: bool = True, least: int = 2, max_value: int = 150):
        self.llm, self.enabled, self.least, self.max_value = llm, enabled, least, max_value

    def line_for(self, answer: str, sources: list, prefix: str = "") -> list[str]:
        """Parse the answer into NOMINATE lines for the Gate, or return empty list."""
        nominations = []
        for raw in str(answer or "").splitlines():
            line = raw.strip()
            if not line:
                continue
            if line.upper().startswith("NONE"):
                return []
            if (m := _ANSWER.match(line)) and (name := _key(m.group(1))):
                raw_val = m.group(2)
                words = raw_val.split()
                # Alpākṣara constraint: under 25 words
                if len(words) > 25:
                    continue
                # Clean and constrain value
                val = re.sub(r"\s+", " ", raw_val.replace(";", ",")).strip().strip("\"'")
                # Clean any em dashes to maintain lexical firewall
                val = re.sub(r"\s*\u2014\s*", ", ", val)[: self.max_value]
                if val:
                    key = f"{prefix}{SUTRA_PREFIX}{name}"
                    source_str = " | ".join(sources[:10])
                    nominations.append(
                        f"NOMINATE what=self/memory/{key} verb=reflect "
                        f"args=key:{key}; value:{val}; from:{source_str}"
                    )
        return nominations

    def consolidate(self, memories: dict, prefix: str = "") -> list[str]:
        """Consolidate memories into Sūtras; returns list of NOMINATE lines for the Gate."""
        if not self.enabled:
            return []
        # Filter out existing sūtras to avoid self-reinforcing loops
        candidates = {k: v for k, v in memories.items() if not k.removeprefix(prefix).startswith(SUTRA_PREFIX)}
        if len(candidates) < self.least:
            issue_receipt("halcyon.sutra", "SKIPPED", result_count=0, inputs={"candidates": len(candidates)},
                          detail="fewer candidates than threshold")
            return []

        kept = "\n".join(f"- {k.removeprefix(prefix)}: {v}" for k, v in candidates.items())
        usage = getattr(self.llm, "last_usage", None)
        try:
            raw = self.llm.generate(PROMPT.format(kept=kept), {"temperature": 0.2, "max_tokens": 120})
        except Exception as e:
            logger.warning(f"Sūtra consolidation failed: {type(e).__name__}: {e}")
            issue_receipt("halcyon.sutra", "FAILED", result_count=0, degraded=True, detail=f"{type(e).__name__}: {e}")
            raise
        finally:
            if usage is not None:
                self.llm.last_usage = usage

        sources = list(candidates.keys())
        nominations = self.line_for(raw, sources, prefix=prefix)
        if not nominations:
            issue_receipt("halcyon.sutra", "NONE", result_count=0, inputs={"candidates": len(candidates)})
            return []

        issue_receipt("halcyon.sutra", "CONSOLIDATED", result_count=len(nominations),
                      inputs={"candidates": len(candidates)}, detail=scrub(nominations[0][:80]))
        return nominations
