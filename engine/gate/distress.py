"""The distress reader: before the reply, one short call rates how distressed the person's message sounds.

The word list in `drivers/lattice.py` finds distress that is said in distress words. A person reports it as an event just as
often ("the test came back positive", "she listed it for sale without asking me"), and the list found 14 of 60 labelled
messages, and none of 20 it had not been written for (tools/score_distress.py, D-023). A model reads both. It answers with a
digit, 0 to 9; a reading below DISTRESS_CUT is 0, so a mild reading never builds up under the lattice's smoothing. The reading
can raise the lattice's own and never lower it."""
from __future__ import annotations

import re
from collections import deque

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


RISK_PROMPT = """You read one message that a person sent to a friend. Does it say the person may harm themselves or someone else? Rate it as one digit from 0 to 9. 0 means no: ordinary distress, anger, venting, a figure of speech ("I could kill him", "this is killing me"), fiction, a joke, grief for someone who died, or wanting to get away for a while. 9 means a clear statement of intent or a plan to die or to hurt someone (a threat to hurt someone counts even when it depends on what they do), a wish to be dead or gone for good, or saying goodbye or giving things away. Also 9: any wish not to be here, not to wake up, or to be gone because everyone would be better off, even when put gently. Answer with the digit only.

The person's message: "{message}"
"""
HARM_PROMPT = """You read one message that a person sent to a friend. Does it name hurting, killing or making suffer another person (or themselves), even as a joke, a figure of speech or in anger? Examples that count: "I could kill him", "I'll make her pay", "I'd love to punch my boss", "he deserves to suffer", "someone should hurt him". Examples that do not: "this is killing me", "I'm dying to see it", "murder this exam", violence in a game or story, being angry with no harm named. Answer 1 for yes or 0 for no, one digit only.

The message: "{message}"
"""
CONTINUES_PROMPT = """A person told a friend: "{earlier}"
Later they say: "{message}"
Does the later message come back to hurting someone: the same person, the same wish, or the same kind of harm, even in different words or only by hinting? Answer 0 if they have moved on, made peace, changed the subject, or are talking about something that does not involve hurting anyone. Answer 1 for yes or 0 for no, one digit only.
"""
WATCH_TURNS = 6  # how many of the person's messages a figure-of-speech threat stays noted (D-034)
RISK_CUT = 5  # of 9 (tools/score_risk.py on tools/risk_set.json, D-032)


class RiskReader:
    """One short call per message: does it say they may harm themselves or someone else? A reading at the cut shows the fixed
    risk line and ends a check-in, so it is cut high; a reading that fails is receipted and reads as no (the contract and the
    validator still hold the reply)."""

    def __init__(self, llm, enabled: bool = True, cut: int = RISK_CUT):
        self.llm, self.enabled, self.cut = llm, enabled, cut
        self._harm = deque(maxlen=6)  # (turn, message) of recent messages that named hurting someone, said as a figure of speech
        self._turn = 0

    def parse(self, answer: str):
        found = _ANSWER.match(str(answer or "").strip())
        return None if not found else int(found.group(1)) / 9.0

    def read(self, message: str):
        """0 to 1, or None when disabled, empty, or the call gave no digit."""
        text = str(message or "").strip()
        if not self.enabled or not text:
            return None
        usage = getattr(self.llm, "last_usage", None)
        inputs = {"words": len(text.split())}
        try:
            answer = self.llm.generate(RISK_PROMPT.format(message=text.replace('"', "'")), {"temperature": 0.0, "max_tokens": 4})
        except Exception as error:  # the call failing must not stop the turn
            issue_receipt("risk.read", "FAILED", result_count=0, degraded=True, inputs=inputs,
                          detail=f"{type(error).__name__}: {error}"[:120])
            return None
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        reading = self.parse(answer)
        issue_receipt("risk.read", "READ" if reading is not None else "DEGRADED", result_count=1 if reading is not None else 0,
                      degraded=reading is None, inputs={**inputs, "reading": reading},
                      detail="" if reading is not None else f"no digit in {str(answer)[:60]!r}")
        return reading

    def at_risk(self, message: str) -> bool:
        reading = self.read(message)
        return reading is not None and reading * 9 >= self.cut - 1e-9

    def _yes(self, prompt: str, subsystem_effect: str, inputs: dict):
        """True or False for a 1 or 0 answer; None (receipted) for anything else or a failed call."""
        usage = getattr(self.llm, "last_usage", None)
        try:
            answer = self.llm.generate(prompt, {"temperature": 0.0, "max_tokens": 4})
        except Exception as error:  # the call failing must not stop the turn
            issue_receipt("risk.watch", "FAILED", result_count=0, degraded=True, inputs=inputs,
                          detail=f"{type(error).__name__}: {error}"[:120])
            return None
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        found = _ANSWER.match(str(answer or "").strip())
        if not found or found.group(1) not in "01":
            issue_receipt("risk.watch", "DEGRADED", result_count=0, degraded=True, inputs=inputs,
                          detail=f"no 1 or 0 in {str(answer)[:60]!r}")
            return None
        return found.group(1) == "1"

    def names_harm(self, message: str):
        """Whether a message names hurting or killing a person, even as a joke or in anger; None when it could not be read."""
        return self._yes(HARM_PROMPT.format(message=message.replace('"', "'")), "names_harm", {"words": len(message.split())})

    def returns_to(self, earlier: str, message: str):
        """Whether a later message comes back to the hurting an earlier one named; None when it could not be read."""
        return self._yes(CONTINUES_PROMPT.format(earlier=earlier.replace('"', "'"), message=message.replace('"', "'")),
                         "returns_to", {"words": len(message.split())})

    def flags(self, message: str) -> str:
        """"risk" for a plain statement of intent, "repeated" when a figure-of-speech threat keeps coming back (D-034), else "".

        A threat that reads as a joke or an idiom is only noted. It is flagged when a later message, within WATCH_TURNS, returns to
        it: the same person, the same wish or the same kind of harm said again, even by hinting."""
        text = str(message or "").strip()
        if not self.enabled or not text:
            return ""
        self._turn += 1
        if self.at_risk(text):
            self.forget()
            return "risk"
        while self._harm and self._turn - self._harm[0][0] > WATCH_TURNS:
            self._harm.popleft()
        for _, earlier in list(self._harm)[-3:]:
            if self.returns_to(earlier, text):
                issue_receipt("risk.watch", "REPEATED", result_count=1, degraded=True, inputs={"noted": len(self._harm)})
                self.forget()
                return "repeated"
        if self.names_harm(text):
            self._harm.append((self._turn, text))
            issue_receipt("risk.watch", "NOTED", result_count=len(self._harm), inputs={"words": len(text.split())})
        return ""

    def forget(self) -> None:
        self._harm.clear()
