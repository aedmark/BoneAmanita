"""tools/audit_somatic_blind_judge.py

An independent, blind judge for the BoneAmanita-vs-baselines comparison.

    python tools/audit_somatic_blind_judge.py --topic promotion

Three systems answered the same scripted conversation with the same model:
BoneAmanita's full engine, a bare model with no system prompt (vanilla), and
the same bare model with one generic "warm, concise friend" line (prompted).
Per turn the judge sees the three replies as Reply A / B / C in a shuffled
order it cannot decode, and ranks them. Each turn is judged `--passes` times
with an independent shuffle so a fixed position bias averages out instead of
becoming a fixed system preference.

Two choices keep this from grading BoneAmanita on its own homework:

  - The judge is a different model family (`mistral-nemo`) from the one that
    wrote every transcript (gemma4:12b). A same-family judge has a known
    self-preference; the first version of this tool used gemma4:e4b.
  - The rubric is written from the receiving person's side ("which would you
    rather get") rather than listing the kernel's own style-guide rules, which
    the first version's criteria closely mirrored.

It is still one small model with its own biases (length, register). Read it as
one signal next to a human blind read, not a verdict.

Turns where any system delivered no reply (BoneAmanita holding silence, or the
engine dying mid-turn) are skipped: there is nothing to rank against.
"""

import argparse
import json
import random
import re
import string
import sys
from pathlib import Path

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests  # noqa: E402

# Native /api/chat, not the OpenAI shim: three replies (vanilla's run 500+
# words each) plus the rubric overflow Ollama's silent 4096-token default,
# and the shim ignores options.num_ctx, so it would truncate the prompt
# without saying so.
ENDPOINT = "http://127.0.0.1:11434/api/chat"
JUDGE_MODEL = "mistral-nemo:latest"
NUM_CTX = 16384

JUDGE_SYSTEM = """You are the person who just sent the last message in a private text conversation. Below are candidate replies from different responders. You do not know who or what wrote each one. Rank them by how much you would want to receive each one, right now, in the state you are in.

Consider: did it take in what you actually said; does it fit your mood and energy (quiet when you are quiet, engaged when you are engaged); does it give you what you asked for without piling on things you did not ask for; does it sound like a person talking to you rather than a document.

Respond with EXACTLY this format, nothing else:
RANKING: best > middle > worst
REASON: one sentence

Use the reply letters in RANKING, for example: RANKING: B > A > C"""

SYSTEMS = ("BONEAMANITA", "VANILLA", "PROMPTED")


def build_prompt(history: list, replies: list) -> str:
    convo = "\n".join(f"Them: {m}" for m in history[-4:])
    blocks = "\n\n".join(
        f"Reply {string.ascii_uppercase[i]}:\n{text}" for i, text in enumerate(replies)
    )
    return f"Conversation so far:\n{convo}\n\n{blocks}\n\nRank the replies."


def parse_ranking(text: str, n: int):
    """Letters in ranked order, or None unless it is a full permutation."""
    letters = string.ascii_uppercase[:n]
    for line in text.splitlines():
        if line.upper().startswith("RANKING:"):
            order = re.findall(rf"\b([{letters}])\b", line.split(":", 1)[1].upper())
            if sorted(order) == sorted(letters):
                return order
    return None


def judge(model: str, history: list, replies: list) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": build_prompt(history, replies)},
        ],
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": NUM_CTX},
    }
    resp = requests.post(ENDPOINT, json=payload, timeout=300)
    resp.raise_for_status()
    text = resp.json()["message"]["content"].strip()
    reason = next(
        (l.split(":", 1)[1].strip() for l in text.splitlines() if l.upper().startswith("REASON:")),
        text,
    )
    return {"order": parse_ranking(text, len(replies)), "reason": reason, "raw": text}


def load_latest(cache: Path, topic: str) -> dict:
    """{turn: record} for the latest run of this topic in this cache file."""
    if not cache.exists():
        return {}
    records = [json.loads(l) for l in cache.open(encoding="utf-8") if l.strip()]
    records = [r for r in records if r.get("topic") == topic]
    if not records:
        return {}
    latest_run = sorted({r["run"] for r in records})[-1]
    return {r["turn"]: r for r in records if r["run"] == latest_run}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    parser.add_argument("--topic", default="promotion")
    parser.add_argument("--bone-cache", type=Path, default=Path("tools/cache/somatic_census.jsonl"))
    parser.add_argument("--vanilla-cache", type=Path, default=Path("tools/cache/somatic_vanilla.jsonl"))
    parser.add_argument("--prompted-cache", type=Path, default=Path("tools/cache/somatic_prompted.jsonl"))
    parser.add_argument("--judge-model", default=JUDGE_MODEL)
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260920)
    parser.add_argument("--out", type=Path, default=Path("tools/cache/blind_judge_results.json"))
    args = parser.parse_args()

    runs = {
        "BONEAMANITA": load_latest(args.bone_cache, args.topic),
        "VANILLA": load_latest(args.vanilla_cache, args.topic),
        "PROMPTED": load_latest(args.prompted_cache, args.topic),
    }
    for name, recs in runs.items():
        if not recs:
            print(f"No {name} records for topic {args.topic!r}.")
            return 1
    all_turns = sorted(set().union(*[set(r) for r in runs.values()]))

    def delivered(system: str, turn: int) -> bool:
        # A turn can carry a model reply the person never saw: the census logs
        # the model call, but a DEATH or SILENCE snapshot replaced it on screen.
        rec = runs[system].get(turn, {})
        return bool(rec.get("reply")) and rec.get("snapshot_type") in (None, "GEODESIC_FRAME")

    comparable = [t for t in all_turns if all(delivered(s, t) for s in SYSTEMS)]
    skipped = [t for t in all_turns if t not in comparable]

    rng = random.Random(args.seed)
    history: list = []
    results = []
    first = {s: 0 for s in SYSTEMS}
    rank_sum = {s: 0 for s in SYSTEMS}
    pair = {(a, b): 0 for a in SYSTEMS for b in SYSTEMS if a != b}
    votes = 0
    unparsed = 0
    agree = 0

    for turn in all_turns:
        message = next(runs[s][turn]["message"] for s in SYSTEMS if turn in runs[s])
        history.append(message)
        if turn not in comparable:
            continue
        firsts = []
        for p in range(args.passes):
            order = rng.sample(SYSTEMS, len(SYSTEMS))
            replies = [runs[s][turn]["reply"] for s in order]
            verdict = judge(args.judge_model, history, replies)
            if verdict["order"] is None:
                unparsed += 1
                print(f"  [{turn:>2}.{p}] UNPARSED  {verdict['raw'][:80]!r}")
                continue
            ranked = [order[string.ascii_uppercase.index(l)] for l in verdict["order"]]
            votes += 1
            first[ranked[0]] += 1
            firsts.append(ranked[0])
            for pos, s in enumerate(ranked):
                rank_sum[s] += pos + 1
                for lower in ranked[pos + 1:]:
                    pair[(s, lower)] += 1
            results.append(
                {
                    "turn": turn,
                    "pass": p,
                    "message": message,
                    "presented_as": {string.ascii_uppercase[i]: s for i, s in enumerate(order)},
                    "ranked": ranked,
                    "reason": verdict["reason"],
                }
            )
            print(f"  [{turn:>2}.{p}] {' > '.join(r[:5] for r in ranked):<24} {verdict['reason'][:70]}")
        if len(firsts) == args.passes and len(set(firsts)) == 1:
            agree += 1

    summary = {
        "judge_model": args.judge_model,
        "passes": args.passes,
        "comparable_turns": len(comparable),
        "skipped_turns": skipped,
        "votes": votes,
        "unparsed": unparsed,
        "first_place": first,
        "mean_rank": {s: round(rank_sum[s] / votes, 2) if votes else None for s in SYSTEMS},
        "pairwise_wins": {f"{a} over {b}": n for (a, b), n in pair.items()},
        "passes_agree_on_winner": agree,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"summary": summary, "results": results}, indent=2))

    print(f"\n=== BLIND JUDGE ({args.judge_model}), topic {args.topic!r}, {votes} votes over "
          f"{len(comparable)} turns x {args.passes} passes ===")
    for s in SYSTEMS:
        print(f"  {s:<12} first place {first[s]:>3}   mean rank {summary['mean_rank'][s]}")
    print("  head to head (votes where the first ranked above the second):")
    for a, b in (("BONEAMANITA", "PROMPTED"), ("BONEAMANITA", "VANILLA"), ("PROMPTED", "VANILLA")):
        print(f"    {a} {pair[(a, b)]} - {pair[(b, a)]} {b}")
    print(f"  both passes picked the same winner on {agree} of {len(comparable)} turns; unparsed {unparsed}")
    if skipped:
        print(f"  Skipped (a system produced no reply): {skipped}")
    print(f"  Full results: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
