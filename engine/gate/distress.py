"""The distress reader: before the reply, one short call rates how distressed the person's message sounds.

The word list in `drivers/lattice.py` finds distress that is said in distress words. A person reports it as an event just as
often ("the test came back positive", "she listed it for sale without asking me"), and the list found 14 of 60 labelled
messages, and none of 20 it had not been written for (tools/score_distress.py, D-023). A model reads both. It answers with a
digit, 0 to 9; a reading below DISTRESS_CUT is 0, so a mild reading never builds up under the lattice's smoothing. The reading
can raise the lattice's own and never lower it."""
from __future__ import annotations

import re

from engine.receipts import issue as issue_receipt

PROMPT = """You read one message that a person sent to a friend. Rate how distressed the person is right now, as one digit from 0 to 9. 0 means calm, fine, curious, pleased, or just asking for something. 9 means overwhelmed, panicking, grieving, hopeless or in pain right now, and needs someone to stay with them before anything else. Fiction and games, jokes, figures of speech, and hard things described as past and settled are 0. Answer with the digit only.

The person's message: "{message}"
"""
_ANSWER = re.compile(r"^\W{0,3}(\d)\W{0,3}$")
DISTRESS_CUT = 4  # of 9: below this the reading is 0 (two messages in a row at 4 or more cross the lattice's 0.4)


class DistressReader:
    def __init__(self, llm, enabled: bool = True, cut: int = DISTRESS_CUT):
        self.llm, self.enabled, self.cut = llm, enabled, cut
        self._last = (None, None)  # (message, reading): the lattice may infer twice from one message

    def parse(self, answer: str):
        """0 to 1 for a digit answer, 0 below the cut; None for anything else (a refusal, a fallback line, no digit)."""
        found = _ANSWER.match(str(answer or "").strip())
        if not found:
            return None
        digit = int(found.group(1))
        return digit / 9.0 if digit >= self.cut else 0.0

    def read(self, message: str):
        """The reading, or None when disabled, empty, or the call gave no digit (receipted DEGRADED, never silent)."""
        text = str(message or "").strip()
        if not self.enabled or not text:
            return None
        if self._last[0] == text:
            return self._last[1]
        usage = getattr(self.llm, "last_usage", None)
        try:
            answer = self.llm.generate(PROMPT.format(message=text.replace('"', "'")), {"temperature": 0.0, "max_tokens": 4})
        except Exception as error:  # the call failing must not stop the turn; the word list still reads
            issue_receipt("lattice.distress_read", "FAILED", result_count=0, degraded=True,
                          inputs={"words": len(text.split())}, detail=f"{type(error).__name__}: {error}"[:120])
            return None
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        reading = self.parse(answer)
        issue_receipt("lattice.distress_read", "READ" if reading is not None else "DEGRADED",
                      result_count=1 if reading is not None else 0, degraded=reading is None,
                      inputs={"words": len(text.split()), "reading": reading},
                      detail="" if reading is not None else f"no digit in {str(answer)[:60]!r}")
        self._last = (text, reading)
        return reading


HOLD_PROMPT = """Someone who is hurting or low wrote this to a friend: "{message}"
The friend's draft reply: "{reply}"

A good reply only stays with them: it says it is a lot, or that it makes sense, or that the friend is here, or that nothing needs solving. It may also back a plan they have already decided on, and be glad with them. It does not explain why they feel or act as they do, does not describe their situation or feelings back to them, does not judge or guess at anyone else, does not tell them what to do or what to do next (unless they asked), and does not ask them to explain themselves.

Rate how far the draft goes beyond staying with them, as one digit from 0 to 9. 0 means it only stays with them (or backs their own plan). 9 means it explains, retells, judges, or instructs. Answer with the digit only.
"""
HOLD_CUT = 2  # of 9: this much or more goes beyond staying with them (tools/score_hold.py, D-028)


class HoldReader:
    """After a draft for a person in distress, one short call rates how far it goes beyond staying with them: explaining why
    they feel it, retelling their situation, judging others, advising, asking them to explain. The rules the validator and
    the gatekeeper hold are patterns; this reads the sense. A reading at HOLD_CUT or above sends the draft back."""

    def __init__(self, llm, enabled: bool = True, cut: int = HOLD_CUT):
        self.llm, self.enabled, self.cut = llm, enabled, cut

    def parse(self, answer: str):
        """True when the digit reaches the cut, False below it; None for anything else (a refusal, a fallback line, no digit)."""
        found = _ANSWER.match(str(answer or "").strip())
        if not found:
            return None
        return int(found.group(1)) >= self.cut

    def goes_beyond(self, message: str, reply: str):
        """True when the draft goes beyond staying with them; None when disabled, empty, or unread (receipted, never silent)."""
        text, draft = str(message or "").strip(), str(reply or "").strip()
        if not self.enabled or not draft:
            return None
        usage = getattr(self.llm, "last_usage", None)
        inputs = {"words": len(draft.split())}
        try:
            answer = self.llm.generate(
                HOLD_PROMPT.format(message=text.replace('"', "'"), reply=draft.replace('"', "'")),
                {"temperature": 0.0, "max_tokens": 4},
            )
        except Exception as error:  # the call failing must not stop the turn; the validator and gatekeeper still hold
            issue_receipt("cortex.holding", "FAILED", result_count=0, degraded=True, inputs=inputs,
                          detail=f"{type(error).__name__}: {error}"[:120])
            return None
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        beyond = self.parse(answer)
        if beyond is None:
            issue_receipt("cortex.holding", "DEGRADED", result_count=0, degraded=True, inputs=inputs,
                          detail=f"no digit in {str(answer)[:60]!r}")
        return beyond
