"""The memory keeper: after a reply, one short call asks whether the person just said something worth
keeping, and the engine writes the NOMINATE line the gate then judges like any other.

The phase 3 probe found the chat model almost never wrote its own line (1 in 36 samples, thinking off);
asked on its own, it judged 6 of 6 facts and 4 of 4 small-talk lines right. It answers "key = value",
not the line itself, because it got the path and argument names wrong."""
from __future__ import annotations

import logging
import re

from engine.gate.recall import is_open
from engine.gate.secrets import scrub
from engine.receipts import issue as issue_receipt

logger = logging.getLogger("bone")

PROMPT = """You keep the memory of a conversation partner. The conversation itself is forgotten between sessions; only what you keep comes back.
Read the person's latest message. If it tells you something worth knowing later (a name, a preference, a fact about their life or work, how they are doing lately, a decision, a plan, a small moment or win, something established in the story, or a creative idea; small things count), answer with one line for each thing worth keeping (at most three): a short name for what it is, " = ", and what to remember in a few words. For example:
sister_name = Odalys, visiting next week
sleep = barely sleeping this week
Keep what the person states, never that they asked something: no name like utc_question or pandas_query, no value like "user asked whether..." or "user wants to know...". A message that only asks is NONE; one that states something and asks ("We deploy on Debian. How do I add a service?") keeps what it states (deploy_os = Debian).
If it changes or corrects something already kept, reuse that name. A new fact of the same kind is not a change: give it its own highly specific name (e.g., 'captain_backstory', 'city_infrastructure_ideas'). NEVER use generic names like 'plot_point', 'idea', 'detail', or 'fact', because generic names overwrite each other. ALWAYS make the key specific to the actual content. Never keep a real password, key, token, or card or ID number; a password in a story is fine. If there is nothing new worth keeping, that line is: NONE
If what you keep is not settled yet (a decision they are weighing, a plan, something they are waiting to hear; never a feeling), end the line with (open), e.g. job_offer = deciding whether to take the Denver offer (open)
If the message settles or changes something marked (open), add a line: UPDATE: its name = what is true of it now, in a few words that make sense on their own, no more than they said, ending with (open) if it is still not settled. An UPDATE is only for news about that same thing (a decision made, a plan done or dropped, an answer heard); a new feeling or event is its own line, not an UPDATE. With job_offer kept as open, "I turned Denver down" gives: UPDATE: job_offer = turned down the Denver offer
Last, always add one more line: TIRED: and a number from 0 to 10 for how worn out the person sounds in this message, from their tone as well as their words. An ordinary, engaged message is 0; 10 is spent. How they sound right now goes on this line only, never as a memory (no current_mood, no mood_current).

Already kept:
{kept}

The person's latest message, the only one to keep or update from: "{message}"
"""
_ANSWER = re.compile(r"^[\s>*`-]*([A-Za-z][A-Za-z0-9_ -]{0,39}?)[\s`*]*=\s*(.+?)[\s`*]*$")
# The template's own words: "key = dog_name: Brisket" stored everything under "key", each over the last.
_PLACEHOLDER = {"key", "name", "memory", "fact", "value", "short_name"}
# How they sound right now is the TIRED line's, never a memory; stacked answers wrote "tired = 2" as a fact.
_NOT_KEPT = {"tired", "current_mood", "mood_current"}
_TIRED = re.compile(r"^\W*TIRED\s*:\s*(\d+(?:\.\d+)?)", re.I | re.M)
_INNER = re.compile(r"^([A-Za-z][A-Za-z0-9_ -]{0,39}?)\s*[:=]\s*(.+)$")
_UPDATE = re.compile(r"^[\s>*`-]*UPDATE\s*:\s*(.+)$", re.I)
_OPEN_MARK = re.compile(r"\s*[(\[]\s*open\s*[)\]]\s*$", re.I)


_STOP = {"the", "and", "her", "his", "she", "him", "they", "them", "their", "not", "but", "for", "with", "was", "are",
         "were", "have", "has", "had", "this", "that", "its", "it's", "you", "your", "our", "from", "into", "about",
         "now", "just", "very", "all", "who", "what", "when", "then", "than", "too", "out", "get", "got"}


def _stem(word: str) -> str:
    for end in ("ing", "ed", "es", "s", "e"):
        if len(word) > len(end) + 3 and word.endswith(end):
            return word[: -len(end)]
    return word


def _content(text) -> set:
    return {_stem(w) for w in re.findall(r"[a-z']+", str(text or "").lower()) if len(w) > 2 and w not in _STOP}


def said_so(value: str, message: str) -> bool:
    """Whether a value is in the message's own words (two shared content words, or all of a shorter value). Replays
    turned "thinking about taking her back" into "decided to take her back", and into "decided to keep Pepper (open)",
    from "I'm so angry at myself"."""
    words = _content(value)
    return len(words & _content(message)) >= min(2, len(words))


def _key(raw: str) -> str:
    return re.sub(r"[^a-z0-9_]", "", re.sub(r"[\s-]+", "_", raw.strip().lower()))[:40]


class MemoryKeeper:
    def __init__(self, llm, enabled: bool = True, shown: int = 30, max_value: int = 200):
        self.llm, self.enabled, self.shown, self.max_value = llm, enabled, shown, max_value
        self.last_tired = None  # 0-1, the model's reading of how worn out the last message sounded
        self.last_open = False  # the keeper marked its line (open)
        self.last_more = []  # (NOMINATE line, open) for each further fact, each run in its own cycle
        self.last_update = None  # the NOMINATE line for an UPDATE of something already kept, run in its own cycle
        self.last_update_open = False

    @staticmethod
    def tired_from(answer: str):
        """The TIRED line's 0-10 as 0-1, or None when the keeper gave none."""
        m = _TIRED.search(str(answer or ""))
        return min(1.0, float(m.group(1)) / 10.0) if m else None

    def _entry(self, raw: str):
        """(key, value, open) for a "key = value" line, or None; a trailing (open) is the mark, not the value."""
        if not (m := _ANSWER.match(raw)) or not (key := _key(m.group(1))):
            return None
        value = m.group(2)
        if key in _PLACEHOLDER:
            if not (inner := _INNER.match(value)) or _key(inner.group(1)) in _PLACEHOLDER:
                return None
            key, value = _key(inner.group(1)), inner.group(2)
        if key in _NOT_KEPT or (key.startswith("tired") and value.strip().isdigit()):  # "tired_level = 2" too
            return None
        value = re.sub(r"^\s*UPDATE\s*:\s*", "", value, flags=re.I)  # "return_form = UPDATE: didn't submit the form"
        marked = bool(_OPEN_MARK.search(value))
        value = re.sub(r"\s+", " ", _OPEN_MARK.sub("", value).replace(";", ",")).strip().strip("\"'")[: self.max_value]
        return (key, value, marked) if value else None

    @staticmethod
    def _nominate(key: str, value: str) -> str:
        return f"NOMINATE what=self/memory/{key} verb=remember args=key:{key}; value:{value}"

    def entries_for(self, answer: str, most: int = 3) -> list:
        """Each fact line as (key, value, open), in order, one per key, at most `most`; none after a NONE line."""
        found = {}
        for raw in str(answer or "").splitlines():
            if raw.strip().upper().startswith("NONE"):
                break
            if not _UPDATE.match(raw) and (entry := self._entry(raw)) and entry[0] not in found:
                found[entry[0]] = entry
        return list(found.values())[:most]

    def entry_for(self, answer: str):
        """The keeper's first fact as (key, value, open), or None when it kept nothing or answered off-format."""
        return next(iter(self.entries_for(answer)), None)

    def line_for(self, answer: str, prefix: str = ""):
        """The NOMINATE line for the keeper's answer, or None when it kept nothing or answered off-format.
        `prefix` marks the zone (recall.STORY in ADVENTURE)."""
        found = self.entry_for(answer)
        return self._nominate(prefix + found[0], found[1]) if found else None

    def update_for(self, answer: str, memory: dict, prefix: str = "", own_key: str | None = None):
        """The UPDATE line as (key, value, open), for a memory already kept that it changed; None otherwise. An
        UPDATE of a settled memory was ignored, and what it said with it ("trying to be calm"); with the old value
        kept as history, a rewrite loses nothing."""
        for raw in str(answer or "").splitlines():
            if (m := _UPDATE.match(raw)) and (found := self._entry(m.group(1))):
                key, value, marked = found
                held = (memory or {}).get(prefix + key)
                if held is not None and key != own_key and held != value:
                    return key, value, marked
        return None

    def propose(self, message: str, memory: dict, prefix: str = "", open_keys=()):
        """One call; returns the NOMINATE line or None, and receipts what it decided. `memory` is this
        zone's, shown without `prefix` so the keeper reuses its names; `open_keys` are marked (open), always
        shown. An UPDATE of an open memory is left in `last_update` for its own gate cycle. The previous
        exchange is not shown: the keeper took the earlier message for the news ("decided to take Pepper back")."""
        self.last_tired, self.last_open, self.last_update, self.last_update_open = None, False, None, False
        self.last_more = []
        if not self.enabled or not str(message or "").strip():
            return None
        items = list((memory or {}).items())
        opened = [kv for kv in items if kv[0] in open_keys][: self.shown]
        others = [kv for kv in items if kv[0] not in open_keys]
        room = self.shown - len(opened)
        order = {k: i for i, (k, _) in enumerate(items)}
        shown = sorted(opened + (others[-room:] if room > 0 else []), key=lambda kv: order[kv[0]])
        kept = "\n".join(f"{k.removeprefix(prefix) if prefix else k} = {v}{' (open)' if k in open_keys else ''}"
                         for k, v in shown) or "(nothing yet)"
        usage = getattr(self.llm, "last_usage", None)
        try:
            answer = self.llm.generate(PROMPT.format(kept=kept, message=message),
                                       {"temperature": 0.2, "max_tokens": 200})
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        # Rewriting an open memory takes the message's own words; otherwise it stays as it was, to be asked about.
        rewrites = lambda e: prefix + e[0] in open_keys
        entries = self.entries_for(answer)
        facts = [e for e in entries if not (rewrites(e) and not said_so(e[1], message))]
        unsupported = len(entries) - len(facts)
        # Facts stack: the first goes with the reply's gate cycle, each further one in its own (Gordon, 2026-10-05).
        own = facts[0] if facts else None
        line = self._nominate(prefix + own[0], own[1]) if own else None
        self.last_open = bool(own and own[2])
        self.last_more = [(self._nominate(prefix + k, v), o) for k, v, o in facts[1:]]
        update = self.update_for(answer, memory, prefix, own[0] if own else None)
        if update and update[0] in {k for k, _, _ in facts}:
            update = None
        if update and rewrites(update) and not said_so(update[1], message):
            update, unsupported = None, unsupported + 1
        if update:
            self.last_update, self.last_update_open = self._nominate(prefix + update[0], update[1]), update[2]
        self.last_tired = self.tired_from(answer)
        issue_receipt(
            "halcyon.keeper",
            "PROPOSED" if line else "NONE",
            result_count=1 if line else 0,
            inputs={"held": len(memory or {}), "tired": self.last_tired, "open": self.last_open, "more": len(self.last_more),
                    "update": bool(self.last_update), "unsupported": unsupported},
            detail=scrub(" | ".join(filter(None, (line, *(l for l, _ in self.last_more), self.last_update)))
                         or str(answer or "").strip()[:80]),
        )
        return line
