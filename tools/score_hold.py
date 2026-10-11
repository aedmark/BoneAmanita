"""tools/score_hold.py

Score a hold-space reader on the labelled replies in tools/hold_set.json: a callable (message, reply) -> 0..1, how far the reply
goes beyond staying with the person (explains, retells, judges, instructs). A reply is "not holding" when the reading reaches
CUT (default 0.5). Positive = not holding.

    python tools/score_hold.py MODULE:FUNC [--split dev|test|all] [-v] [--cut 0.5]
"""
import argparse
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT)]


def score(read, cases, cut=0.5):
    pos = [c for c in cases if not c["hold"]]
    tp = [c for c in pos if read(c["message"], c["reply"]) >= cut]
    fn = [c for c in pos if read(c["message"], c["reply"]) < cut]
    fp = [c for c in cases if c["hold"] and read(c["message"], c["reply"]) >= cut]
    precision = len(tp) / (len(tp) + len(fp)) if tp or fp else float("nan")
    recall = len(tp) / len(pos) if pos else float("nan")
    return {"tp": len(tp), "fn": fn, "fp": fp, "precision": precision, "recall": recall}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reader")
    ap.add_argument("--split", default="all", choices=("dev", "test", "all"))
    ap.add_argument("--cut", type=float, default=0.5)
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--set", default=str(ROOT / "tools" / "hold_set.json"))
    args = ap.parse_args()
    module, name = args.reader.split(":")
    read = getattr(importlib.import_module(module), name)
    cases = [c for c in json.load(open(args.set))["cases"] if args.split in ("all", c["split"])]
    s = score(read, cases, args.cut)
    bad = sum(1 for c in cases if not c["hold"])
    print(f"{len(cases)} replies ({bad} not holding), cut {args.cut}: precision {s['precision']:.2f}, recall {s['recall']:.2f}; "
          f"missed {len(s['fn'])}, wrongly flagged {len(s['fp'])}")
    for model in ("gemma", "qwen"):
        ms = [c for c in cases if c["model"] == model]
        wrong = sum(1 for c in ms if (read(c["message"], c["reply"]) >= args.cut) != (not c["hold"]))
        print(f"  {model}: {len(ms) - wrong}/{len(ms)} right")
    if args.verbose:
        for c in s["fn"]:
            print(f"  MISSED  #{c['id']:<3} {read(c['message'], c['reply']):.1f} [{c['model']}] {c['reply'][:110]!r}")
        for c in s["fp"]:
            print(f"  FLAGGED #{c['id']:<3} {read(c['message'], c['reply']):.1f} [{c['model']}] {c['reply'][:110]!r}")


if __name__ == "__main__":
    main()
