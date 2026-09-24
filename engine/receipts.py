import logging
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger("bone")

DEFAULT_CAPACITY = 512

CORE_SUBSYSTEMS = (
    "composer.compose",
    "cortex.query_neighborhood",
    "cortex.recall",
    "cortex.somatic",
    "embeddings.embed_batch",
    "governor.bitmap_gate",
    "lattice.infer_and_couple",
    "memory.retrieve_semantic",
    "physics.word_resolution",
    "stage.negotiate",
)
# Issued only when their event happens (a draft sent back or cut), so their absence is not silence.
EVENT_SUBSYSTEMS = ("cortex.redraft", "cortex.salvage")


@dataclass(frozen=True)
class Receipt:
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
        return self.result_count == 0

    def __str__(self) -> str:
        flag = "DEGRADED" if self.degraded else "ok"
        line = f"[{self.subsystem}] {self.effect}: {self.result_count} ({flag})"
        return f"{line} {self.detail}" if self.detail else line


class ReceiptLedger:
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
        with cls._cls_lock:
            cls._instance = None

    def expect(self, subsystem: str) -> None:
        with self._lock:
            self._expected.add(subsystem)

    def expected(self) -> Set[str]:
        with self._lock:
            return set(self._expected)

    def silent(self) -> Set[str]:
        with self._lock:
            return self._expected - self._seen

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
        return self._chronic(lambda r: r.degraded)

    def chronic_empty(self) -> Set[str]:
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
