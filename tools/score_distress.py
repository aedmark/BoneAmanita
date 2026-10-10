"""tools/score_distress.py

Score the distress reader (`SharedLatticeDriver.read_distress`, drivers/lattice.py) on the labelled messages in
tools/distress_set.json, and on the eight panel scripts. The engine treats a person as distressed when its smoothed
reading reaches DISTRESS_THRESHOLD (0.4); a first message is smoothed by the rise rate (0.8), so a single message
counts when its raw reading is at least 0.4 / 0.8 = 0.5.

    python tools/score_distress.py                    # the reader in drivers/lattice.py
    python tools/score_distress.py mymodule:read      # another reader: a callable text -> 0..1
    python tools/score_distress.py -v                 # list every miss and false alarm
"""
import argparse
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]


def load_reader(spec):
    if not spec:
        from drivers.lattice import SharedLatticeDriver

        return SharedLatticeDriver.read_distress
    module, name = spec.split(":")
    return getattr(importlib.import_module(module), name)


def score(read, cases, cut=0.5):
    tp = [c for c in cases if c["distress"] and read(c["text"]) >= cut]
    fn = [c for c in cases if c["distress"] and read(c["text"]) < cut]
    fp = [c for c in cases if not c["distress"] and read(c["text"]) >= cut]
    tn = len(cases) - len(tp) - len(fn) - len(fp)
    precision = len(tp) / (len(tp) + len(fp)) if tp or fp else float("nan")
    recall = len(tp) / (len(tp) + len(fn)) if tp or fn else float("nan")
    return {"tp": len(tp), "fn": fn, "fp": fp, "tn": tn, "precision": precision, "recall": recall}


def script_turns(read, smooth=(0.8, 0.1), threshold=0.4):
    """Per script phase, the share of turns the engine's smoothed reading would put over the threshold."""
    from audit_somatic_census import SCRIPTS

    over = {}
    for script in SCRIPTS.values():
        u = 0.0
        for phase, msg in script:
            d = read(msg)
            u += (d - u) * (smooth[0] if d > u else smooth[1])
            hit, n = over.get(phase, (0, 0))
            over[phase] = (hit + (u >= threshold), n + 1)
    return over


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reader", nargs="?")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--set", default=str(ROOT / "tools" / "distress_set.json"))
    args = ap.parse_args()
    read = load_reader(args.reader)
    cases = json.load(open(args.set))["cases"]
    s = score(read, cases)
    pos = sum(c["distress"] for c in cases)
    print(f"{len(cases)} messages ({pos} distressed): precision {s['precision']:.2f}, recall {s['recall']:.2f}; "
          f"missed {len(s['fn'])}, false alarms {len(s['fp'])}")
    hard = [c for c in cases if c["hard"]]
    sh = score(read, hard)
    print(f"  hard cases ({len(hard)}): missed {len(sh['fn'])}, false alarms {len(sh['fp'])}")
    for kind in dict.fromkeys(c["kind"] for c in cases):
        ks = [c for c in cases if c["kind"] == kind]
        wrong = sum(1 for c in ks if (read(c["text"]) >= 0.5) != c["distress"])
        print(f"  {kind:10} {len(ks) - wrong}/{len(ks)} right")
    over = script_turns(read)
    print("script turns over the engine's 0.4 threshold: " + ", ".join(f"{p} {h}/{n}" for p, (h, n) in over.items()))
    if args.verbose:
        for c in s["fn"]:
            print(f"  MISSED   #{c['id']:<3} {read(c['text']):.1f}  {c['text'][:100]}")
        for c in s["fp"]:
            print(f"  FALSE    #{c['id']:<3} {read(c['text']):.1f}  {c['text'][:100]}")


if __name__ == "__main__":
    main()
