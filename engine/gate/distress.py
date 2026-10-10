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
