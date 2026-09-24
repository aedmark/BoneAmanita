"""tools/build_blind_panel.py

Builds the three-way blind-read page for one topic from the cached runs and the
judge outputs, so the page can be regenerated instead of hand-assembled.

    python tools/build_blind_panel.py --topic toast \\
        --title "The Toast, Three Ways" --story "One sentence about the conversation." \\
        --judge tools/cache/blind_judge_toast_mistral-nemo.json \\
        --judge tools/cache/blind_judge_toast_ministral.json \\
        --out panel.html --standalone panel-standalone.html

`--responsive` builds it from the simulated-person runs instead: each system's
conversation drifted on its own, so every card carries what you said in that
conversation (and, collapsed, the exchange before it), not one shared message.
A held turn is shown as the notice the person saw and can still be picked.
Judges are optional there, since none is validated for responsive ranking yet.

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
RESPONSIVE_ARMS = {"boneamanita": "bone", "prompted": "friend", "vanilla": "vanilla"}
HEADINGS = {
    False: (
        "Three responders &middot; one 30-turn conversation &middot; gemma4:12b behind all of them",
        "Three responders answer every message. <strong>Replies A, B and C</strong> are reshuffled at random "
        "each turn, so position tells you nothing. Pick the one you would rather receive, turn by turn, before "
        "revealing who wrote what.",
    ),
    True: (
        "Three conversations &middot; one simulated person reacting to each &middot; gemma4:12b behind all of them",
        "The same simulated person (see how this page was made, below) talked to three responders, and "
        "because each answered differently the three "
        "conversations drifted apart. Each turn shows <strong>Conversations A, B and C</strong>, reshuffled at "
        "random: what you had just said in that conversation, and the reply it got. Pick the exchange you would "
        "rather have been in, turn by turn, before revealing who wrote what.",
    ),
}
TEMPLATE = Path(__file__).with_name("blind_panel_template.html")
SEED = 20260920


def load_latest(name: str, topic: str, arm: str = None) -> dict:
    recs = [json.loads(l) for l in (CACHE / name).open(encoding="utf-8") if l.strip()]
    recs = [r for r in recs if r.get("topic") == topic and (arm is None or r.get("arm") == arm)]
    latest = sorted({r["run"] for r in recs})[-1]
    return {r["turn"]: r for r in recs if r["run"] == latest}


def shown(rec: dict) -> str:
    """What the person saw: the reply, or the notice that replaced it on a held turn."""
    return rec.get("shown") or rec.get("reply") or ""


def bone_text(rec: dict) -> str:
    """BoneAmanita's reply as the engine displayed it; the raw model text only for runs that predate `displayed`."""
    return rec.get("displayed") or rec.get("reply") or ""


def method_lines(runs: dict, responsive: bool) -> list:
    """How the page's content was made, stated from the run records rather than from memory."""
    from somatic_sim_user import PHASE_MAX_WORDS

    bone = list(runs["boneamanita"].values())
    models = sorted({r.get("model") for rs in runs.values() for r in rs.values() if r.get("model")})
    lines = [
        f"Every reply was written by the same model ({', '.join(models)}), run locally. The three responders "
        f"differ only in what surrounds it: BoneAmanita's full engine, one instruction (\u201c{FRIEND_PROMPT}\u201d), "
        "or nothing at all.",
    ]
    if responsive:
        sims = sorted({r.get("sim_model") for r in read_jsonl("somatic_responsive_exit.jsonl") if r.get("sim_model")})
        lines.append(
            "The person is not a real person. Their messages were written by a different AI model "
            f"({', '.join(sims) or 'not recorded'}) playing one fixed character through a fixed arc (engaged, tiring, "
            "flagging, distressed, recovering) and reacting to each responder's actual replies, so the three "
            "conversations drift apart. Only the first message is identical in all three."
        )
        if any("sim_trimmed" in r for rs in runs.values() for r in rs.values()):
            caps = ", ".join(f"{p} {n}" for p, n in PHASE_MAX_WORDS.items())
            lines.append(f"The person's messages were capped by phase ({caps} words), so they cannot run long when "
                         "the character is meant to be worn out.")
    else:
        lines.append("The person's 30 messages are a fixed script written in advance; every responder received "
                     "exactly the same messages, whatever it replied.")
    lines.append("This is the only run of each conversation. Nothing was regenerated or chosen for this page.")
    if all("displayed" in r for r in bone):
        lines.append("BoneAmanita's replies are shown exactly as the engine displayed them, after its own filters. "
                     "The status lines its terminal prints above each reply are left out.")
    else:
        lines.append("BoneAmanita's replies are the model's raw text before the engine's own filters: this run "
                     "predates capturing what the engine displayed, so a line the engine would have removed may show.")
    if all(r.get("fresh_state") for r in bone):
        lines.append("BoneAmanita ran as a first conversation, with no memory of earlier sessions; its memory, "
                     "embeddings and Creative Determinant were live within this one.")
    else:
        lines.append("BoneAmanita's memory, embeddings and Creative Determinant were live, but this run may have "
                     "started with saved state left by earlier sessions or tests (it predates starting each run "
                     "fresh).")
    if all("paced_seconds" in r for r in bone):
        lines.append("Between messages the engine was given the time a person would take to read the reply and type "
                     "the next message, since its energy recovers while idle.")
    else:
        lines.append("Messages reached the engine back to back, with none of the idle time a real person's reading "
                     "and typing would give it (its energy recovers while idle).")
    if all("salvaged" in r for r in bone):
        ux = json.loads(Path("lore/ux_strings.json").read_text(encoding="utf-8"))
        pool = set(ux.get("brain_strings", {}).get("cortex_pause", []))
        redrafted = sum(1 for r in bone if r.get("rejections"))
        cut = sum(1 for r in bone if r.get("salvaged"))
        paused = sum(1 for r in bone if (r.get("displayed") or "").strip() in pool)
        lines.append(f"BoneAmanita checks every draft against its style rules and rewrites it on a hit. It rewrote "
                     f"on {redrafted} of {len(bone)} turns. When the last rewrite still broke a rule, it cut the "
                     f"offending sentence ({cut} turns) or, if that would gut the reply, showed a short pause line "
                     f"instead ({paused} turns). Those pause lines are canned text, not the model's.")
    lines.append("Where BoneAmanita declined to reply, its card shows the notice the person saw instead.")
    lines.append("A, B and C are shuffled every turn with a fixed seed. The answer key is in the page source, so this "
                 "is a casual blind read, not a sealed one.")
    return lines


def read_jsonl(name: str) -> list:
    path = CACHE / name
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()] if path.exists() else []


def scripted_turns(runs: dict, rng: random.Random) -> list:
    """One entry per scripted turn; a turn any system did not deliver is listed with the engine's reason."""
    def delivered(system: str, turn: int) -> bool:
        rec = runs[system].get(turn, {})
        return bool(rec.get("reply")) and rec.get("snapshot_type") in (None, "GEODESIC_FRAME")

    turns = []
    for t in sorted(runs["boneamanita"]):
        bone = runs["boneamanita"][t]
        entry = {"turn": t, "phase": bone["phase"], "message": bone["message"]}
        if all(delivered(s, t) for s in runs):
            order = rng.sample(list(runs), len(runs))
            entry["comparable"] = True
            entry["cards"] = [
                {"letter": string.ascii_uppercase[i], "sys": s,
                 "text": bone_text(runs[s][t]) if s == "boneamanita" else runs[s][t]["reply"]}
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
    return turns


def responsive_turns(runs: dict, rng: random.Random) -> list:
    """One entry per turn every system reached; each card is that system's own last exchange."""
    shared = sorted(set.intersection(*(set(r) for r in runs.values())))
    turns = []
    for t in shared:
        order = rng.sample(list(runs), len(runs))
        cards = []
        for i, s in enumerate(order):
            rec, prev = runs[s][t], runs[s].get(t - 1)
            cards.append(
                {
                    "letter": string.ascii_uppercase[i],
                    "sys": s,
                    "said": rec["message"],
                    "context": [{"me": prev["message"], "friend": shown(prev)}] if prev else [],
                    "text": bone_text(rec) if s == "boneamanita" and rec.get("delivered", True) else shown(rec),
                }
            )
        turns.append({"turn": t, "phase": runs["boneamanita"][t]["phase"], "comparable": True, "cards": cards})
    return turns


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    ap.add_argument("--topic", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--story", required=True)
    ap.add_argument("--judge", action="append", default=[], type=Path)
    ap.add_argument("--responsive", action="store_true", help="the simulated-person runs, one conversation per card")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--standalone", type=Path)
    args = ap.parse_args()

    if args.responsive:
        runs = {s: load_latest("somatic_responsive.jsonl", args.topic, arm) for s, arm in RESPONSIVE_ARMS.items()}
    else:
        runs = {
            "boneamanita": load_latest("somatic_census.jsonl", args.topic),
            "vanilla": load_latest("somatic_vanilla.jsonl", args.topic),
            "prompted": load_latest("somatic_prompted.jsonl", args.topic),
        }
    judges = [json.load(open(p, encoding="utf-8"))["summary"] for p in args.judge]

    rng = random.Random(SEED)
    turns = responsive_turns(runs, rng) if args.responsive else scripted_turns(runs, rng)

    def pooled(a: str, b: str):
        return (
            sum(j["pairwise_wins"][f"{a} over {b}"] for j in judges),
            sum(j["pairwise_wins"][f"{b} over {a}"] for j in judges),
        )

    bp, bv = pooled("BONEAMANITA", "PROMPTED"), pooled("BONEAMANITA", "VANILLA")
    data = {
        "storeKey": f"blind-panel-{args.topic}-{'responsive-' if args.responsive else ''}v1",
        "friendPrompt": FRIEND_PROMPT,
        "method": method_lines(runs, args.responsive),
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
            f"Judges pooled: BoneAmanita beat Prompted {bp[0]} to {bp[1]} and beat Vanilla "
            f"{bv[0]} to {bv[1]}. Votes are not fully independent, since each turn is judged twice "
            "on the same three replies, so treat any gap as an estimate."
        )
        if judges
        else "",
    }
    eyebrow, how = HEADINGS[args.responsive]
    page = (
        TEMPLATE.read_text(encoding="utf-8")
        .replace("__EYEBROW__", eyebrow)
        .replace("__HOW__", how)
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
