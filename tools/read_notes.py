"""tools/read_notes.py

Read what /note saved (notes/notes.jsonl, or BONE_NOTES): counts by tag, then the exchanges.

    python tools/read_notes.py              # counts and every note, newest last
    python tools/read_notes.py --tag off    # only the ones marked off
    python tools/read_notes.py --distress   # only exchanges the engine read as distress (distress_u of 0.4 or more)
"""
import argparse
import json
import os
from collections import Counter
from pathlib import Path


def load(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", default=os.environ.get("BONE_NOTES", "notes/notes.jsonl"))
    ap.add_argument("--tag")
    ap.add_argument("--distress", action="store_true")
    args = ap.parse_args()
    rows = load(args.path)
    print(f"{len(rows)} notes: {dict(Counter(r['tag'] for r in rows))}")
    for r in rows:
        if args.tag and r["tag"] != args.tag:
            continue
        if args.distress and not (r.get("distress_u") or 0) >= 0.4:
            continue
        print(f"\n[{r['ts']}] {r['tag']} ({r['mode']}, {r['model']}, distress {r.get('distress_u')}) {r['comment']}")
        print(f"  they: {r['user']}\n  it:   {r['reply']}")
        if r["receipts"]:
            print(f"  receipts: {r['receipts']}")


if __name__ == "__main__":
    main()
