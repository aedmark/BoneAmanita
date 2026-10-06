"""A turn the person stopped waiting for (the cognitive loop timed out) stops at its next check, before it writes
what they would be remembered as having heard: the dialogue history and kept memories."""

import threading

_lock = threading.Lock()
_current = None
_abandoned = None


class TurnAbandoned(BaseException):
    """Not an Exception: the turn's broad crash handlers must let it through to the daemon."""


def begin(ticket) -> None:
    global _current
    with _lock:
        _current = ticket


def abandon(ticket) -> None:
    global _abandoned
    with _lock:
        _abandoned = ticket


def check(where: str) -> None:
    with _lock:
        if _current is not None and _current == _abandoned:
            raise TurnAbandoned(where)
