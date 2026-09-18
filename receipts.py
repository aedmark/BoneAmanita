"""receipts.py

A receipt is a structured record issued by the code that performed a piece of
work, stating what it was handed and what came back.

The rule that gives receipts teeth: `result_count` and `degraded` are set by the
code that did the work, never by its caller, and never inferred from whether an
exception was raised. A subsystem cannot produce a healthy-looking record of
unhealthy work without someone writing a deliberate lie into the receipt line.

This is deliberately not a liveness flag. A liveness ring catches dead code; it
does not catch the failure this engine kept producing, which is a subsystem that
fires enthusiastically every turn and returns garbage. The hash-vector retriever
would have shown green for the life of the project.

Receipts record what a subsystem did, not whether it was correct. A receipt
saying `retrieved 3` from a semantically meaningless index is honest and still
useless on its own. Receipts make the engine auditable, not right.

This module imports nothing from the engine so that any subsystem can issue a
receipt without risking an import cycle. Delivery to telemetry is done by a sink
that `main.py` installs, not by importing `core`.
"""

import logging
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger("bone")

DEFAULT_CAPACITY = 512

# The roll call: every subsystem that has agreed to report. A name here that
# never appears in a session is dead code, which is the one failure a receipt
# cannot report about itself (silence is indistinguishable from not being
# called). `tests/test_receipts.py` asserts this list and the actual call sites
# in the tree stay in step, so neither can drift away from the other unnoticed.
CORE_SUBSYSTEMS = (
    "composer.compose",
    "cortex.query_neighborhood",
    "cortex.recall",
    "embeddings.embed_batch",
    "governor.bitmap_gate",
    "lattice.infer_and_couple",
    "memory.retrieve_semantic",
    "physics.word_resolution",
    "stage.negotiate",
)


@dataclass(frozen=True)
class Receipt:
    """What one subsystem did on one turn.

    `subsystem` is a stable dotted name (`cortex.recall`, `governor.thermal_lock`)
    and is the key everything else joins on. `effect` is a short human phrase
    describing the action. `inputs` is what the subsystem was actually handed,
    not what its caller believes it was handed.
    """

    subsystem: str
    effect: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    result_count: int = 0
    degraded: bool = False
    detail: str = ""
    turn: int = 0
    ts: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    def is_empty(self) -> bool:
        """Ran, reported no work. Not an error; often the interesting case."""
        return self.result_count == 0

    def __str__(self) -> str:
        flag = "DEGRADED" if self.degraded else "ok"
        line = f"[{self.subsystem}] {self.effect}: {self.result_count} ({flag})"
        return f"{line} {self.detail}" if self.detail else line


class ReceiptLedger:
    """Session-scoped ring buffer of receipts, plus the roll-call of subsystems
    that said they would report and then did or did not.

    Held as a process singleton because the subsystems that issue receipts are
    scattered across the engine and none of them own the others.
    """

    _instance: Optional["ReceiptLedger"] = None
    _cls_lock = threading.Lock()

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        self.capacity = int(capacity)
        self._lock = threading.RLock()
        self._entries: List[Receipt] = []
        self._expected: Set[str] = set()
        self._seen: Set[str] = set()
        self._turn = 0
        self.sink: Optional[Callable[[Receipt], None]] = None

    @classmethod
    def get_instance(cls) -> "ReceiptLedger":
        if cls._instance is None:
            with cls._cls_lock:
                if cls._instance is None:
                    cls._instance = ReceiptLedger()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Drop the singleton. For tests; the engine never calls this."""
        with cls._cls_lock:
            cls._instance = None

    # -- the roll call ----------------------------------------------------

    def expect(self, subsystem: str) -> None:
        """Declare that `subsystem` intends to issue receipts this session.

        A name that is expected and never seen is dead code, and that is the one
        failure a receipt cannot report about itself.
        """
        with self._lock:
            self._expected.add(subsystem)

    def expected(self) -> Set[str]:
        with self._lock:
            return set(self._expected)

    def silent(self) -> Set[str]:
        """Expected to report, never did. Wired to nothing, or never called."""
        with self._lock:
            return self._expected - self._seen

    # -- issuing ----------------------------------------------------------

    def issue(
        self,
        subsystem: str,
        effect: str,
        *,
        result_count: int,
        degraded: bool = False,
        inputs: Optional[dict] = None,
        detail: str = "",
    ) -> Receipt:
        """Record work that was performed. Called by the worker, never the caller.

        `result_count` and `degraded` are required to be stated positionally by
        keyword so that neither can be supplied by accident or left to a default
        that flatters the subsystem.
        """
        receipt = Receipt(
            subsystem=subsystem,
            effect=effect,
            inputs=dict(inputs or {}),
            result_count=int(result_count),
            degraded=bool(degraded),
            detail=str(detail),
            turn=self._turn,
            ts=time.time(),
        )
        with self._lock:
            self._entries.append(receipt)
            self._seen.add(subsystem)
            self._expected.add(subsystem)
            if len(self._entries) > self.capacity:
                del self._entries[: len(self._entries) - self.capacity]
            sink = self.sink
        if sink is not None:
            sink(receipt)
        return receipt

    # -- reading ----------------------------------------------------------

    def begin_turn(self) -> int:
        with self._lock:
            self._turn += 1
            return self._turn

    @property
    def turn(self) -> int:
        with self._lock:
            return self._turn

    def all(self) -> List[Receipt]:
        with self._lock:
            return list(self._entries)

    def for_turn(self, turn: Optional[int] = None) -> List[Receipt]:
        with self._lock:
            target = self._turn if turn is None else int(turn)
            return [r for r in self._entries if r.turn == target]

    def for_subsystem(self, subsystem: str) -> List[Receipt]:
        with self._lock:
            return [r for r in self._entries if r.subsystem == subsystem]

    def chronic_degraded(self) -> Set[str]:
        """Subsystems whose every receipt in the buffer says it ran on a fallback."""
        return self._chronic(lambda r: r.degraded)

    def chronic_empty(self) -> Set[str]:
        """Subsystems that have run and never once returned anything."""
        return self._chronic(lambda r: r.is_empty())

    def _chronic(self, predicate: Callable[[Receipt], bool]) -> Set[str]:
        with self._lock:
            by_name: Dict[str, List[Receipt]] = {}
            for entry in self._entries:
                by_name.setdefault(entry.subsystem, []).append(entry)
        return {
            name
            for name, entries in by_name.items()
            if entries and all(predicate(e) for e in entries)
        }

    def scorecard(self) -> dict:
        """Everything `/diag` and the boot self-test need, in one pass."""
        with self._lock:
            entries = list(self._entries)
            expected = set(self._expected)
            seen = set(self._seen)
            turn = self._turn
        return {
            "turn": turn,
            "total": len(entries),
            "expected": sorted(expected),
            "silent": sorted(expected - seen),
            "chronic_degraded": sorted(self.chronic_degraded()),
            "chronic_empty": sorted(self.chronic_empty()),
            "this_turn": [r for r in entries if r.turn == turn],
        }


def issue(
    subsystem: str,
    effect: str,
    *,
    result_count: int,
    degraded: bool = False,
    inputs: Optional[dict] = None,
    detail: str = "",
) -> Receipt:
    """Module-level shorthand so a call site is one import and one line."""
    return ReceiptLedger.get_instance().issue(
        subsystem,
        effect,
        result_count=result_count,
        degraded=degraded,
        inputs=inputs,
        detail=detail,
    )


def expect(*subsystems: str) -> None:
    ledger = ReceiptLedger.get_instance()
    for name in subsystems:
        ledger.expect(name)
