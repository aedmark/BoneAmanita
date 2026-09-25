"""Impossible requests: asks for something this engine cannot do (lore/capabilities.json).

A request pattern only counts in a sentence that asks the engine for something;
a question pattern only in a question. When unsure, it does not flag: a false
positive tells the person no when the answer was yes.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from engine.core import LoreManifest

_SENTENCES = re.compile(r"(?<=[.!?])\s+|\n+")
_FILLER = re.compile(r"^(?:(?:please|pls|just|now|ok|okay|hey|so|and|then|also)[,\s]+)+", re.I)
_CUE = re.compile(r"\b(?:can|could|would|will|won't) you\b|\bi (?:need|want|would like) you to\b|\bplease\b|\bfor me\b", re.I)
_QUESTION_OPEN = re.compile(r"^(?:what|what's|whats|how|who|when|where|is|are|did|do|does|will)\b", re.I)
_NUMBER_UNIT = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d+)\s*-?\s*(words?|pages?)\b", re.I)


@dataclass(frozen=True)
class OutOfReach:
    name: str
    limit: str
    phrase: str


class CapabilityCheck:
    def __init__(self, max_reply_words: int = 3000):
        data = LoreManifest.get_instance().get("capabilities") or {}
        self.max_reply_words = max_reply_words
        self.limits = [
            (
                entry["name"],
                entry["limit"],
                [re.compile(p, re.I) for p in entry.get("request", [])],
                [re.compile(p, re.I) for p in entry.get("question", [])],
            )
            for entry in data.get("LIMITS", [])
        ]
        length = data.get("LENGTH") or {}
        self.length_name = length.get("name", "TOO_LONG")
        self.length_limit = length.get("limit", "")
        self.words_per_page = int(length.get("words_per_page", 300))
        self.writing_verb = re.compile(length.get("writing_verb", r"\bwrite\b"), re.I)
        self.whole_work = re.compile(length.get("whole_work", r"(?!)"), re.I)

    def detect(self, text: str, mode: str = "") -> Optional[OutOfReach]:
        """The first thing asked for that the engine cannot do, or None."""
        for raw in _SENTENCES.split(text or ""):
            sentence = _FILLER.sub("", raw.strip())
            if not sentence:
                continue
            hit = self._length(sentence)
            # Adventure's world is fiction: calling, ordering or looking there is play.
            if hit or mode.upper() == "ADVENTURE":
                if hit:
                    return hit
                continue
            asked = bool(_CUE.search(sentence))
            is_question = sentence.endswith("?") or bool(_QUESTION_OPEN.match(sentence))
            for name, limit, requests, questions in self.limits:
                for pattern in requests:
                    m = pattern.search(sentence)
                    if m and (asked or m.start() == 0):
                        return OutOfReach(name, limit, m.group(0))
                for pattern in questions:
                    m = pattern.search(sentence)
                    if m and is_question:
                        return OutOfReach(name, limit, m.group(0))
        return None

    def _length(self, sentence: str) -> Optional[OutOfReach]:
        if not self.writing_verb.search(sentence):
            return None
        if m := self.whole_work.search(sentence):
            return OutOfReach(self.length_name, self.length_limit, m.group(0))
        for m in _NUMBER_UNIT.finditer(sentence):
            n = int(m.group(1).replace(",", ""))
            words = n * self.words_per_page if m.group(2).lower().startswith("page") else n
            if words > self.max_reply_words:
                return OutOfReach(self.length_name, self.length_limit, m.group(0))
        return None
