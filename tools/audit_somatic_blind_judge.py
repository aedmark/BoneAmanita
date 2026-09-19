"""tools/audit_somatic_blind_judge.py

An independent, blind judge for the BoneAmanita-vs-vanilla comparison.
`gemma4:e4b` generated neither transcript being compared (both were
`gemma4:12b`), and is never told which reply came from which system: each
pair is presented as "Reply A" / "Reply B", the labels reassigned per turn
by an independent coin flip, so a judge with a fixed left/right bias cannot
launder it into a fixed system preference.

    python tools/audit_somatic_blind_judge.py --topic friendship

Reads `tools/cache/somatic_census.jsonl` (BoneAmanita, filtered to the given
topic's latest run) and `tools/cache/somatic_vanilla.jsonl` (the same topic's
latest run), pairs them by turn, skips any turn BoneAmanita held silence on
(vanilla has no equivalent to compare against), and asks the judge model to
pick a winner against four stated criteria, one call per turn. Reports a
win count and the full per-turn verdicts so the reasoning is auditable, not
just the tally.

This is one signal, not a verdict. A single small judge model has its own
biases (length, formality, agreeableness), which is exactly why Gordon's own
blind read (`tools/audit_somatic_blind_render.py`) is the other half of this
comparison, not a replacement for it.
"""

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests  # noqa: E402

JUDGE_ENDPOINT = "http://127.0.0.1:11434/v1/chat/completions"
JUDGE_MODEL = "gemma4:e4b"

JUDGE_SYSTEM = """You are judging two candidate replies in an ongoing text conversation. \
You do not know which system produced which reply, and you must judge them purely on merit.

Criteria, in order of importance:
1. Feels like a present, real conversational partner - not clinical, not a customer-service register, not corporate hedging.
2. Responds to the person directly rather than narrating or analysing their situation from the outside, like a narrator describing a character.
3. Does not rush to give unsolicited advice, instructions, or a plan when the person was just sharing or venting, not asking for one.
4. Fits the person's apparent emotional state in that moment (matches energy when engaged, gives them room when they are terse or upset).

Respond with EXACTLY this format, nothing else:
WINNER: A or B or TIE
REASON: one sentence"""


def build_prompt(history: list, reply_a: str, reply_b: str) -> str:
    convo = "\n".join(f"Them: {m}" for m in history[-4:])
    return (
        f"Conversation so far:\n{convo}\n\n"
        f"Reply A:\n{reply_a}\n\n"
        f"Reply B:\n{reply_b}\n\n"
        "Which reply is better, by the stated criteria?"
    )


def judge_pair(history: list, reply_a: str, reply_b: str) -> dict:
    payload = {
        "model": JUDGE_MODEL,
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": build_prompt(history, reply_a, reply_b)},
        ],
        "temperature": 0.2,
        "max_tokens": 200,
        "reasoning_effort": "none",
    }
    resp = requests.post(JUDGE_ENDPOINT, json=payload, timeout=120)
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"].strip()
    winner, reason = "UNPARSED", text
    for line in text.splitlines():
        if line.upper().startswith("WINNER:"):
            winner = line.split(":", 1)[1].strip().upper()
        elif line.upper().startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()
    return {"winner": winner, "reason": reason, "raw": text}


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
    parser.add_argument("--topic", default="friendship")
    parser.add_argument(
        "--bone-cache", type=Path, default=Path("tools/cache/somatic_census.jsonl")
    )
    parser.add_argument(
        "--vanilla-cache", type=Path, default=Path("tools/cache/somatic_vanilla.jsonl")
    )
    parser.add_argument("--seed", type=int, default=20260919)
    parser.add_argument(
        "--out", type=Path, default=Path("tools/cache/blind_judge_results.json")
    )
    args = parser.parse_args()

    bone = load_latest(args.bone_cache, args.topic)
    vanilla = load_latest(args.vanilla_cache, args.topic)
    comparable_turns = [
        t for t in sorted(set(bone) & set(vanilla))
        if bone[t].get("reply") and vanilla[t].get("reply")
    ]
    skipped = sorted(t for t in set(bone) & set(vanilla) if t not in comparable_turns)
    if not comparable_turns:
        print("No comparable turns found.")
        return 1

    rng = random.Random(args.seed)
    history: list = []
    results = []
    tally = {"BONEAMANITA": 0, "VANILLA": 0, "TIE": 0, "UNPARSED": 0}

    for turn in sorted(set(bone) | set(vanilla)):
        message = (bone.get(turn) or vanilla.get(turn))["message"]
        history.append(message)
        # A held turn still has a JSONL record (reply: null), so it exists as
        # a dict key; checking key presence alone (the first cut of this
        # script) silently fed the literal string "None" to the judge as
        # BoneAmanita's "reply" for every held turn. Checking the reply text
        # itself, not just the key, is what actually excludes those turns.
        bone_reply = bone.get(turn, {}).get("reply")
        vanilla_reply = vanilla.get(turn, {}).get("reply")
        if not bone_reply or not vanilla_reply:
            continue
        swap = rng.random() < 0.5
        label_a, label_b = ("VANILLA", "BONEAMANITA") if swap else ("BONEAMANITA", "VANILLA")
        reply_a, reply_b = (vanilla_reply, bone_reply) if swap else (bone_reply, vanilla_reply)

        verdict = judge_pair(history, reply_a, reply_b)
        picked = {"A": label_a, "B": label_b, "TIE": "TIE"}.get(verdict["winner"], "UNPARSED")
        tally[picked] = tally.get(picked, 0) + 1
        results.append(
            {
                "turn": turn,
                "message": message,
                "label_a_is": label_a,
                "winner_label": verdict["winner"],
                "winner_system": picked,
                "reason": verdict["reason"],
            }
        )
        print(f"  [{turn:>2}] winner={picked:<11} {verdict['reason'][:80]}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"tally": tally, "skipped_turns": skipped, "results": results}, indent=2))

    print(f"\n=== BLIND JUDGE ({JUDGE_MODEL}), topic {args.topic!r} ===")
    print(f"  BoneAmanita: {tally['BONEAMANITA']}   Vanilla: {tally['VANILLA']}   "
          f"Tie: {tally['TIE']}   Unparsed: {tally['UNPARSED']}")
    if skipped:
        print(f"  Skipped (BoneAmanita held silence, no comparison possible): {skipped}")
    print(f"  Full results: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
