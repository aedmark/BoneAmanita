"""What a memory felt like (REM plan R1): the endocrine state when it was kept, read into words. Measured by
the engine, not guessed by the model (Gordon, 2026-09-29).

The rest point is EndocrineSystem's defaults; the margins are a first guess, to calibrate on real runs."""
from __future__ import annotations

REST = {"DOP": 0.5, "OXY": 0.1, "COR": 0.0, "SER": 0.5, "ADR": 0.0, "MEL": 0.0}
# (hormone, above or below rest, margin, word)
READINGS = (
    ("COR", 1, 0.3, "tense"),
    ("ADR", 1, 0.3, "alert"),
    ("OXY", 1, 0.25, "close"),
    ("DOP", 1, 0.2, "eager"),
    ("DOP", -1, 0.2, "flat"),
    ("SER", 1, 0.2, "settled"),
    ("SER", -1, 0.2, "low"),
    ("MEL", 1, 0.3, "drowsy"),
)


def reading(chem: dict | None) -> list[str]:
    """The words for what stood out, strongest first; ["calm"] when nothing did; [] with no record."""
    if not isinstance(chem, dict) or not chem:
        return []
    found = []
    for hormone, sign, margin, word in READINGS:
        value = chem.get(hormone)
        if isinstance(value, (int, float)) and sign * (value - REST[hormone]) > margin:
            found.append((abs(value - REST[hormone]) - margin, word))
    return [word for _, word in sorted(found, reverse=True)] or ["calm"]


def describe(chem: dict | None) -> str:
    """ "tense, close (COR 0.42, OXY 0.51)", or "" with no record."""
    words = reading(chem)
    if not words:
        return ""
    levels = ", ".join(f"{h} {chem[h]:.2f}" for h in REST if isinstance(chem.get(h), (int, float))
                       and abs(chem[h] - REST[h]) > 0.05)
    return ", ".join(words) + (f" ({levels})" if levels else "")
