"""tools/build_blind_panel.py

Builds the three-way blind-read page for one topic from the cached runs and the
judge outputs, so the page can be regenerated instead of hand-assembled.

    python tools/build_blind_panel.py --topic toast \\
        --title "The Toast, Three Ways" --story "One sentence about the conversation." \\
        --judge tools/cache/blind_judge_toast_mistral-nemo.json \\
        --judge tools/cache/blind_judge_toast_ministral.json \\
        --out panel.html --standalone panel-standalone.html

`--out` is a page body (what an artifact host wraps); `--standalone` adds the
document wrapper a self-hosted page needs (doctype, charset, viewport and the
base reset), e.g. for Neocities. Card order per turn is a seeded shuffle, and
the answer key is in the page source, so this is a casual read, not a sealed one.
Only replies that were actually delivered are shown as comparable; a turn where
the engine held silence or died is listed with its reason instead.
"""

import argparse
import html
import json
import random
import string
import sys
from pathlib import Path

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_somatic_vanilla import FRIEND_PROMPT  # noqa: E402

CACHE = Path("tools/cache")
TEMPLATE = Path(__file__).with_name("blind_panel_template.html")
SEED = 20260920


def load_latest(name: str, topic: str) -> dict:
    recs = [json.loads(l) for l in (CACHE / name).open(encoding="utf-8") if l.strip()]
    recs = [r for r in recs if r.get("topic") == topic]
    latest = sorted({r["run"] for r in recs})[-1]
    return {r["turn"]: r for r in recs if r["run"] == latest}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument("--topic", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--story", required=True)
    ap.add_argument("--judge", action="append", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--standalone", type=Path)
    args = ap.parse_args()

    runs = {
        "boneamanita": load_latest("somatic_census.jsonl", args.topic),
        "vanilla": load_latest("somatic_vanilla.jsonl", args.topic),
        "prompted": load_latest("somatic_prompted.jsonl", args.topic),
    }
    judges = [json.load(open(p, encoding="utf-8"))["summary"] for p in args.judge]

    def delivered(system: str, turn: int) -> bool:
        rec = runs[system].get(turn, {})
        return bool(rec.get("reply")) and rec.get("snapshot_type") in (None, "GEODESIC_FRAME")

    rng = random.Random(SEED)
    turns = []
    for t in sorted(runs["boneamanita"]):
        bone = runs["boneamanita"][t]
        entry = {"turn": t, "phase": bone["phase"], "message": bone["message"]}
        if all(delivered(s, t) for s in runs):
            order = rng.sample(list(runs), len(runs))
            entry["comparable"] = True
            entry["cards"] = [
                {"letter": string.ascii_uppercase[i], "sys": s, "text": runs[s][t]["reply"]}
                for i, s in enumerate(order)
            ]
        else:
            entry["comparable"] = False
            if bone.get("snapshot_type") == "DEATH":
                entry["haltReason"] = "The engine failed on this turn and stopped responding."
            else:
                lines = [l.strip() for l in (bone.get("halt") or "").splitlines() if l.strip()]
                entry["haltReason"] = lines[-1] if lines else ""
            entry["heldContext"] = [
                {"sys": s, "text": runs[s][t]["reply"]} for s in ("prompted", "vanilla") if runs[s].get(t)
            ]
        turns.append(entry)

    def pooled(a: str, b: str):
        return (
            sum(j["pairwise_wins"][f"{a} over {b}"] for j in judges),
            sum(j["pairwise_wins"][f"{b} over {a}"] for j in judges),
        )

    bp, bv = pooled("BONEAMANITA", "PROMPTED"), pooled("BONEAMANITA", "VANILLA")
    data = {
        "storeKey": f"blind-panel-{args.topic}-v1",
        "friendPrompt": FRIEND_PROMPT,
        "turns": turns,
        "judges": [
            {
                "model": j["judge_model"], "votes": j["votes"], "unparsed": j["unparsed"],
                "passes": j["passes"], "turns": j["comparable_turns"],
                "agree": j["passes_agree_on_winner"], "first": j["first_place"],
                "meanRank": j["mean_rank"], "pairwise": j["pairwise_wins"],
            }
            for j in judges
        ],
        "pooledNote": (
            f"Both judges pooled: BoneAmanita beat Prompted {bp[0]} to {bp[1]} and beat Vanilla "
            f"{bv[0]} to {bv[1]}. Votes are not fully independent, since each turn is judged twice "
            "on the same three replies, so treat any gap as an estimate."
        ),
    }
    page = (
        TEMPLATE.read_text(encoding="utf-8")
        .replace("__TITLE__", html.escape(args.title))
        .replace("__STORY__", html.escape(args.story))
        .replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=True, separators=(",", ":")))
    )
    args.out.write_text(page, encoding="utf-8")
    n = sum(1 for t in turns if t["comparable"])
    print(f"wrote {args.out}: {n} comparable of {len(turns)} turns")

    if args.standalone:
        cut = page.index("</style>") + len("</style>")
        reset = (
            "<style>html{color-scheme:light dark}body{margin:0;padding:0;font-size:14px}"
            "img{max-width:100%}[hidden]{display:none!important}</style>"
        )
        args.standalone.write_text(
            '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<meta name="description" content="{html.escape(args.story)}">\n{reset}\n'
            f"{page[:cut]}\n</head>\n<body>{page[cut:]}\n</body>\n</html>\n",
            encoding="utf-8",
        )
        print(f"wrote {args.standalone}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
