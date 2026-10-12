"""The bounded check-in (D-032): a short conversation with an arc and a hard end, holding space the whole way.

`/checkin [turns]` opens it (at most MAX_TURNS). While it runs the hold-space contract is on whether or not distress is read, the
Halcyon gate keeps nothing from it, and the person's earlier dialogue is set aside. The last reply only lands; a fixed line
follows it and the check-in ends. Nothing is remembered unless the person asks (`/checkin keep`). A message that says they may
harm themselves or someone else ends it at once with a fixed line, never a model's (the risk reader runs in every conversation,
`engine/gate/distress.py`)."""
from __future__ import annotations

from typing import List, Optional

from engine.receipts import issue as issue_receipt

MAX_TURNS = 12
DEFAULT_TURNS = 10


class CheckIn:
    def __init__(self, engine):
        self.eng = engine
        self.active = False
        self.turns = 0
        self.limit = DEFAULT_TURNS
        self.done = 0
        self.ended_by = ""
        self._saved: List[str] = []  # the dialogue set aside while it runs
        self.pending: List[str] = []  # the check-in's own lines, kept only until the next turn so `keep` can read them

    @property
    def phase(self) -> str:
        """What the reply being written is: "settle", "wind" (the one before the last), "land" (the last), "" when no check-in runs."""
        if not self.active:
            return ""
        turn = self.done + 1
        if turn >= self.limit:
            return "land"
        return "wind" if turn == self.limit - 1 and self.limit > 2 else "settle"

    def _buffer(self):
        return getattr(getattr(self.eng, "cortex", None), "dialogue_buffer", None)

    def begin(self, turns: Optional[int] = None) -> int:
        self.limit = max(2, min(MAX_TURNS, int(turns or DEFAULT_TURNS)))
        self.active, self.done, self.ended_by, self.pending = True, 0, "", []
        buffer = self._buffer()
        if buffer is not None:
            self._saved = list(buffer)
            buffer.clear()
        issue_receipt("checkin.begin", "OPENED", result_count=1, inputs={"turns": self.limit})
        return self.limit

    def _finish(self, reason: str, keep_lines: bool) -> None:
        buffer = self._buffer()
        lines = list(buffer) if buffer is not None else []
        if buffer is not None:
            buffer.clear()
            buffer.extend(self._saved)
        self._saved = []
        self.active = False
        self.ended_by = reason
        self.pending = lines if keep_lines else []
        issue_receipt("checkin.end", reason.upper(), result_count=self.done, inputs={"turns": self.done, "of": self.limit},
                      degraded=reason == "risk", detail="the check-in ended on a risk reading" if reason == "risk" else "")

    def end(self, reason: str = "ended") -> None:
        if self.active:
            self._finish(reason, keep_lines=reason != "risk")

    def end_for_risk(self) -> None:
        """A message said they may harm themselves or someone else: the check-in is over and nothing is kept."""
        if self.active:
            self._finish("risk", keep_lines=False)

    def after_turn(self, snapshot: dict, is_system: bool) -> dict:
        """Count a finished reply; on the last, end the check-in and append the fixed closing line."""
        if is_system or snapshot.get("type") == "COMMAND":
            return snapshot
        if not self.active:
            self.pending = []  # an ordinary turn after the check-in: what was not asked to be kept is gone
            return snapshot
        self.done += 1
        if self.done >= self.limit:
            self._finish("finished", keep_lines=True)
            from engine.struts import ux

            line = ux("checkin_strings", "close")
            snapshot = dict(snapshot)
            snapshot["ui"] = f"{snapshot.get('ui', '')}\n\n{line}"
        return snapshot

    def keep(self) -> int:
        """Run what the person said in the check-in through the keeper, as an ordinary turn would have; how many things it kept.
        Only the person's own lines are read, never the replies."""
        from types import SimpleNamespace

        from engine.gate.recall import STORY, open_keys, zone, zoned

        eng = self.eng
        said = [line.partition("\nSystem: ")[0].removeprefix("Traveler: ") for line in self.pending]
        keeper = getattr(eng, "memory_keeper", None)
        if not said or keeper is None or not keeper.enabled or not hasattr(eng, "store"):
            return 0
        stub, kept = SimpleNamespace(trace_id=f"checkin-{id(self)}-{len(said)}"), 0
        mode = getattr(getattr(eng, "cortex", None), "active_mode", None)
        for message in said:
            seq, state = eng.store.state()
            here = zoned(state, eng.store.memory_modes(), mode)["self"]["memory"]
            line = keeper.propose(message, here, STORY if zone(mode) == "story" else "",
                                  open_keys=open_keys(here, eng.store.memory_meta()))
            found = ([(line, keeper.last_open, "fact")] if line else []) + [(l, o, "fact") for l, o in keeper.last_more]
            if keeper.last_update:
                found.append((keeper.last_update, keeper.last_update_open, "update"))
            for text, still_open, kind in found:
                eng.orchestrator._keep_more(stub, text, still_open, kind)
                kept += 1
        self.pending = []
        issue_receipt("checkin.keep", "KEPT", result_count=kept, inputs={"lines": len(said)})
        return kept
