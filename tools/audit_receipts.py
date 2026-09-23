"""tools/audit_receipts.py

Scorecard for ROADMAP A3: which subsystems reported work, and what they said
about it.

    python tools/audit_receipts.py

Drives the engine's instrumented subsystems over a synthetic turn without
booting the whole organism, then prints the receipt table plus the three ways a
subsystem can lie by omission:

  silent            expected to report and never did; wired to nothing
  chronic degraded  ran every time, on a fallback path every time
  chronic empty     ran every time, returned nothing every time

A receipt records what a subsystem did, not whether it was right. A green table
means the engine is auditable, not that it is correct.
"""

import sys

sys.path.insert(0, ".")

from engine.receipts import CORE_SUBSYSTEMS, ReceiptLedger  # noqa: E402

PROBE_TEXT = (
    "the heavy iron hammer fell on the anvil and the whole forge rang, "
    "and I could not tell whether the sound meant anything at all"
)


def drive_probe() -> None:
    """Call each instrumented subsystem once, the way a turn would."""
    from mechanics.lexicon import LexiconService
    from physics.observer import QuantumObserver
    from spores.embeddings import SemanticEmbedder

    lex = LexiconService()
    lex.initialize()
    words = lex.clean(PROBE_TEXT)

    SemanticEmbedder.get_instance().embed_batch(words[:8])
    QuantumObserver._tally_categories_static(lex, words)

    from brain.ann import CerebralIndex

    index = CerebralIndex()
    index.query_neighborhood(index.embed(PROBE_TEXT), k=3)


def main() -> int:
    ledger = ReceiptLedger.get_instance()
    for name in CORE_SUBSYSTEMS:
        ledger.expect(name)
    ledger.begin_turn()

    drive_probe()

    card = ledger.scorecard()
    print(f"\n=== RECEIPTS: {card['total']} issued over {card['turn']} turn(s) ===\n")
    width = max((len(r.subsystem) for r in ledger.all()), default=20)
    for receipt in ledger.all():
        flag = "DEGRADED" if receipt.degraded else ("empty" if receipt.is_empty() else "ok")
        print(f"  {receipt.subsystem:<{width}}  {receipt.result_count:>6}  {flag:<9}  {receipt.effect}")
        if receipt.detail:
            print(f"  {'':<{width}}          {receipt.detail}")
        if receipt.inputs:
            given = ", ".join(f"{k}={v}" for k, v in receipt.inputs.items())
            print(f"  {'':<{width}}          given: {given}")

    print()
    problems = 0
    for label, names in (
        ("NEVER REPORTED", card["silent"]),
        ("ALWAYS DEGRADED", card["chronic_degraded"]),
        ("ALWAYS EMPTY", card["chronic_empty"]),
    ):
        if names:
            problems += len(names)
            print(f"  {label}: {', '.join(names)}")

    if not problems:
        print("  Every subsystem on the roll call reported real work.")
    else:
        print(
            "\n  Some of the above are expected from a probe that never builds a "
            "memory graph or calls a model. Compare against a real session "
            "rather than treating this list as a failure."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
