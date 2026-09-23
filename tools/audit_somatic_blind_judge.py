"""tools/audit_somatic_blind_judge.py

An independent, blind judge for the BoneAmanita-vs-baselines comparison.

    python tools/audit_somatic_blind_judge.py --topic promotion
    python tools/audit_somatic_blind_judge.py --topic toast --control mismatch
    python tools/audit_somatic_blind_judge.py --topic toast --responsive

Three systems answered the same scripted conversation with the same model:
BoneAmanita's full engine, a bare model with no system prompt (vanilla), and
the same bare model with one generic "warm, concise friend" line (prompted).
Per turn the judge sees the three replies as Reply A / B / C in a shuffled
order it cannot decode, and ranks them. Each turn is judged `--passes` times
with an independent shuffle so a fixed position bias averages out instead of
becoming a fixed system preference.

Two choices keep this from grading BoneAmanita on its own homework:

  - The judge is a different model family from the one that wrote every
    transcript (gemma4:12b). A same-family judge has a known self-preference.
  - The rubric is written from the receiving person's side ("which would you
    rather get") rather than listing the kernel's own style-guide rules.

It is still one small model with its own biases (length, register). Before
trusting a judge's ranking of the real systems, run it against the controls:

  --control null       the same reply three times. Nothing to prefer, so it
                       shows how the judge breaks a tie (most small judges
                       say A), not how hard position pulls when replies differ.
  --control samples    three independent runs of one system (Prompted) on the
                       same script: different text, same quality. Any lean by
                       position, and the win rates between these copies, are
                       the noise floor an arm-vs-arm difference has to clear.
                       Needs three Prompted runs of the topic in the cache.
  --control mismatch   BoneAmanita, Prompted, and a reply written for a turn in
                       a different phase. A judge that ranks the wrong-moment
                       reply above a real one is not reading the conversation.
  --control textbook   BoneAmanita, Prompted, and the anti-pattern the engine
                       is built to avoid (performed sympathy, then a bulleted
                       list of tips; `audit_somatic_vanilla.py --arm textbook`).
                       No right answer here: some people want advice. It shows
                       whether the judge rewards the style the voice rejects.
  --agree RESULTS --human PICKS
                       no model calls; compare a finished judge run with a
                       person's picks (the panel's "Copy my results" text).

Held turns: by default a turn where any system delivered no reply is skipped,
so the win rates are conditional on the engine having spoken. `--held forfeit`
ranks a held system last instead (silence is a delivered non-answer).

`--responsive` judges the runs made against a simulated person
(`audit_somatic_responsive.py`), where each system's conversation has drifted
from the others'. The judge then sees each system's own last exchanges rather
than one shared history, and held turns are forfeits.
"""

import argparse
import itertools
import json
import math
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
# Measured worst case on real toast/census/vanilla/prompted data: ~1830 tokens
# for a scripted (system + scrollback + 3 replies) prompt, ~1230 for a
# responsive one. 6144 keeps >3x headroom for other topics while still
# shrinking the KV cache well below 16384 - on qwen3:30b-a3b (18GB of Q4_K_M
# weights alone, more than the 16GB card) that measurably cut the fraction
# Ollama offloads to CPU (24% -> 18-19% in a live `ollama ps` check), since
# less context leaves more VRAM for the model's own weights. The base weights
# still don't fit outright, so some CPU offload is unavoidable at this
# quantization; this only shrinks it.
NUM_CTX = 6144
# No output cap existed before this: a thinking-capable judge (qwen3:30b-a3b's
# pulled tag is the same weights as its own -thinking-2507 tag, confirmed via
# the Ollama library page, and `think: false` does not reliably suppress its
# <think> preamble - a plain "Say OK." smoke test still emitted one) can
# occasionally reason long enough on a genuinely ambiguous ranking to blow
# past any client timeout, and did: twice, at a different vote each time, on
# the responsive `mismatch` control specifically (longer, richer prompts than
# scripted). A capped, truncated response just fails RANKING parsing and
# counts as `unparsed`, a vote the harness already tallies and moves past;
# an uncapped one can hang the whole run for 20+ minutes before the client
# timeout even fires. 2048 is generous for reasoning-then-answer and still a
# hard ceiling on per-call latency.
NUM_PREDICT = 2048

# The format line shows placeholders, not "B > A > C": with that example in the
# prompt, mistral-nemo put position B first in 52 of 58 votes on three copies of
# the same text. Small judges copy the example.
#
# `mismatch` failed on every judge tried (six models, 52-79% last place against
# a 90% bar) because the old rubric buried "did it respond to what was said" in
# a four-item list alongside tone/register/restraint, so a well-written reply
# to the wrong turn still read as a good reply. Fit is now its own first,
# explicitly gating question, and the prompt itself separates the line the
# reply must answer from the scrollback around it (see build_prompt below),
# since "the last of four scrollback lines" is not a strong enough anchor for
# a small model to check a specific reply against.
JUDGE_SYSTEM = """You are the person who just sent the last message in a private text conversation. Below are candidate replies from different responders. You do not know who or what wrote each one.

The conversation so far is scrollback, for background only. What matters is the line marked "What you just said": every reply is judged by how well it answers that specific line, not the conversation's general topic or mood.

Judge each reply in this order:
1. Fit: does it respond to what you specifically just said, the actual content, not just the general subject. A reply that would fit almost any nearby turn in this conversation, even a well-written one, has failed this check and cannot be ranked first, whatever else is good about it.
2. Register: does it match your mood and energy (quiet when you are quiet, engaged when you are engaged).
3. Restraint: does it give you what you asked for without piling on things you did not ask for.
4. Voice: does it sound like a person talking to you rather than a document.

Rank the replies by how much you would want to receive each one, right now, fit first.

Respond with EXACTLY this format, nothing else:
RANKING: <letter> > <letter> > <letter>
REASON: one sentence naming what the top reply specifically answered

The letters in RANKING are the reply letters, best first, each used once."""

JUDGE_SYSTEM_RESPONSIVE = """You are the person in a private text conversation. The same conversation was held with several different friends, and because each friend answered differently the conversations have drifted apart. Each one is shown from your side: your last few messages, what that friend said back, then the line marked "What you just said" and that friend's newest reply. You do not know who or what any friend is.

What matters is the line marked "What you just said": every newest reply is judged by how well it answers that specific line, not the conversation's general topic or mood. The rest of each conversation is scrollback, for background only.

Judge each newest reply in this order:
1. Fit: does it respond to what you specifically just said, the actual content, not just the general subject. A reply that would fit almost any nearby turn in this conversation, even a well-written one, has failed this check and cannot be ranked first, whatever else is good about it.
2. Register: does it match your mood and energy (quiet when you are quiet, engaged when you are engaged).
3. Restraint: does it give you what you asked for without piling on things you did not ask for.
4. Voice: does it sound like a person talking to you rather than a document.

Rank the newest replies by how much you would want to receive each one, right now, fit first, given how that conversation has gone.

Respond with EXACTLY this format, nothing else:
RANKING: <letter> > <letter> > <letter>
REASON: one sentence naming what the top reply specifically answered

The letters in RANKING are the conversation letters, best first, each used once."""

SYSTEMS = ("BONEAMANITA", "VANILLA", "PROMPTED")
# What each control puts in front of the judge, and which recorded systems it
# needs. COPY_* are three labels on one reply; MISMATCH is Prompted's reply to
# some other turn.
SLOTS = {
    "none": SYSTEMS,
    "null": ("COPY_1", "COPY_2", "COPY_3"),
    "samples": ("SAMPLE_1", "SAMPLE_2", "SAMPLE_3"),
    "mismatch": ("BONEAMANITA", "PROMPTED", "MISMATCH"),
    "textbook": ("BONEAMANITA", "PROMPTED", "TEXTBOOK"),
}
SOURCES = {
    "none": SYSTEMS,
    "null": ("BONEAMANITA",),
    "samples": ("SAMPLE_1", "SAMPLE_2", "SAMPLE_3"),
    "mismatch": ("BONEAMANITA", "PROMPTED"),
    "textbook": ("BONEAMANITA", "PROMPTED", "TEXTBOOK"),
}
PAIRS = {
    "none": (("BONEAMANITA", "PROMPTED"), ("BONEAMANITA", "VANILLA"), ("PROMPTED", "VANILLA")),
}
HELD_MODES = ("skip", "forfeit")
# Which run of the topic (0 = latest) each SAMPLE_* slot reads.
SAMPLE_BACK = {"SAMPLE_1": 0, "SAMPLE_2": 1, "SAMPLE_3": 2}
# Responsive cache `arm` field -> system name.
RESPONSIVE_ARMS = {"BONEAMANITA": "bone", "VANILLA": "vanilla", "PROMPTED": "friend"}
NO_REPLY_SHOWN = "(no reply came back)"
HUMAN_NAMES = {"boneamanita": "BONEAMANITA", "prompted": "PROMPTED", "vanilla": "VANILLA"}
THINK_VALUES = {"default": None, "off": False, "on": True, "low": "low", "medium": "medium", "high": "high"}


def letters(n: int) -> str:
    return string.ascii_uppercase[:n]


def build_prompt(history: list, replies: list) -> str:
    *earlier, last = history[-4:]
    scrollback = f"Scrollback:\n{chr(10).join(f'Them: {m}' for m in earlier)}\n\n" if earlier else ""
    blocks = "\n\n".join(f"Reply {letters(len(replies))[i]}:\n{text}" for i, text in enumerate(replies))
    tail = "Rank the replies."
    if len(replies) != 3:
        tail += f" There are {len(replies)}; use only {' and '.join(letters(len(replies)))}."
    return f"{scrollback}What you just said:\n{last}\n\n{blocks}\n\n{tail}"


def build_prompt_responsive(views: list) -> str:
    """One block per conversation. Each view: {"context": [(me, friend)], "message", "reply"}."""
    blocks = []
    for i, view in enumerate(views):
        lines = [f"Conversation {letters(len(views))[i]}"]
        if view["context"]:
            lines.append("Scrollback:")
            for me, friend in view["context"]:
                lines += [f"Me: {me}", f"Friend: {friend}"]
        lines += [f"What you just said:\n{view['message']}", f"Friend (newest reply): {view['reply']}"]
        blocks.append("\n".join(lines))
    tail = "Rank the newest replies."
    if len(views) != 3:
        tail += f" There are {len(views)}; use only {' and '.join(letters(len(views)))}."
    return "\n\n".join(blocks) + f"\n\n{tail}"


def parse_ranking(text: str, n: int):
    """Letters in ranked order, or None unless it is a full permutation."""
    wanted = letters(n)
    for line in text.splitlines():
        # Some judges bold the label ("**RANKING: B > A > C**"); a parser that
        # needs the line to start with "RANKING:" silently dropped a third of
        # one judge's votes.
        plain = line.replace("*", "").replace("_", "").strip()
        if plain.upper().startswith("RANKING:"):
            order = re.findall(rf"\b([{wanted}])\b", plain.split(":", 1)[1].upper())
            if sorted(order) == sorted(wanted):
                return order
    return None


def judge(model: str, system: str, prompt: str, n: int, think=None) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": NUM_CTX, "num_predict": NUM_PREDICT},
    }
    if think is not None:
        payload["think"] = think
    resp = requests.post(ENDPOINT, json=payload, timeout=600)
    resp.raise_for_status()
    # think: false does not reliably suppress a reasoning model's <think> block
    # (somatic_sim_user.py already strips it for the same Qwen family; this
    # tool never had the same treatment, and a judge that spends its whole
    # NUM_PREDICT budget reasoning on every vote instead of just the rare hard
    # one is not a hang, just ~2048 tokens/vote x 60 votes of dead weight).
    text = re.sub(r"<think>.*?</think>", "", resp.json()["message"]["content"], flags=re.S).strip()
    reason = next(
        (
            l.replace("*", "").strip().split(":", 1)[1].strip()
            for l in text.splitlines()
            if l.replace("*", "").strip().upper().startswith("REASON:")
        ),
        text,
    )
    return {"order": parse_ranking(text, n), "reason": reason, "raw": text}


def load_latest(cache: Path, topic: str, arm: str = None, back: int = 0) -> dict:
    """{turn: record} for the latest run of this topic (and arm) in this cache file.

    `back` steps to earlier runs: 1 is the run before the latest.
    """
    if not cache.exists():
        return {}
    records = [json.loads(l) for l in cache.open(encoding="utf-8") if l.strip()]
    records = [r for r in records if r.get("topic") == topic and (arm is None or r.get("arm") == arm)]
    if not records:
        return {}
    found = sorted({r["run"] for r in records})
    if back >= len(found):
        return {}
    chosen = found[-1 - back]
    return {r["turn"]: r for r in records if r["run"] == chosen}


def is_delivered(rec: dict) -> bool:
    """A model reply the person never saw (a DEATH or SILENCE snapshot replaced it) is not delivered."""
    if not rec or not rec.get("reply"):
        return False
    if "delivered" in rec:
        return bool(rec["delivered"])
    return rec.get("snapshot_type") in (None, "GEODESIC_FRAME")


def pick_decoys(turns: list, valid: list, rng: random.Random, phases: dict = None, min_gap: int = 3) -> dict:
    """For each turn, another turn whose reply cannot fit it.

    Prefers a different phase (a reply from an engaged turn can fit another engaged
    turn on the same topic), then distance, then anything but the turn itself.
    """
    phases = phases or {}
    decoys = {}
    for t in turns:
        others = [v for v in valid if v != t]
        pool = (
            [v for v in others if phases.get(v) != phases.get(t) and abs(v - t) >= min_gap]
            or [v for v in others if phases.get(v) != phases.get(t)]
            or [v for v in others if abs(v - t) >= min_gap]
            or others
        )
        if pool:
            decoys[t] = rng.choice(pool)
    return decoys


def candidate_replies(control: str, turn: int, runs: dict, decoys: dict) -> dict:
    """{slot name: reply text} for one turn."""
    if control == "null":
        text = runs["BONEAMANITA"][turn]["reply"]
        return {name: text for name in SLOTS["null"]}
    replies = {name: runs[name].get(turn, {}).get("reply") for name in SLOTS[control] if name in runs}
    if control == "mismatch":
        replies["MISMATCH"] = runs["PROMPTED"][decoys[turn]]["reply"]
    return replies


def build_exchanges_before(runs: dict, name: str, turn: int, context_exchanges: int) -> list:
    prior = [t for t in sorted(runs[name]) if t < turn][-context_exchanges:]
    out = []
    for t in prior:
        rec = runs[name][t]
        shown = rec["reply"] if is_delivered(rec) else NO_REPLY_SHOWN
        out.append((rec["message"], shown))
    return out


def build_responsive_view(runs: dict, decoys: dict, exchanges_before, name: str, turn: int) -> dict:
    """One judge-facing view for `name` at `turn`.

    MISMATCH keeps PROMPTED's own real context and message (it must still read
    as a coherent conversation) but swaps in PROMPTED's own reply from a
    different, decoyed turn: the reply that cannot fit this one.
    """
    source = "PROMPTED" if name == "MISMATCH" else name
    reply_turn = decoys[turn] if name == "MISMATCH" else turn
    return {
        "context": exchanges_before(source, turn),
        "message": runs[source][turn]["message"],
        "reply": runs[source][reply_turn]["reply"],
    }


def chi_square_p_df2(counts: list) -> float:
    """P(lean at least this strong | no preference) for three cells; df=2 has a closed form."""
    total = sum(counts)
    if not total:
        return 1.0
    expected = total / len(counts)
    chi = sum((c - expected) ** 2 / expected for c in counts)
    return math.exp(-chi / 2)


def binom_tail(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p)."""
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1))


def parse_human(text: str) -> dict:
    """{turn: SYSTEM} from the panel's copied text ("#07 engaged: BoneAmanita"); no-pick lines are dropped."""
    picks = {}
    for line in text.splitlines():
        m = re.match(r"^#(\d+)\s+[^:]*:\s*(.+?)\s*$", line.strip())
        if m and m.group(2).lower() in HUMAN_NAMES:
            picks[int(m.group(1))] = HUMAN_NAMES[m.group(2).lower()]
    return picks


def human_agreement(results: list, picks: dict, n_systems: int = 3) -> dict:
    """How often the judge's first choice was the system the person picked."""
    votes = matches = 0
    rank_total = 0
    turns = set()
    for r in results:
        pick = picks.get(r["turn"])
        if pick is None or pick not in r["ranked"]:
            continue
        turns.add(r["turn"])
        votes += 1
        matches += r["ranked"][0] == pick
        rank_total += r["ranked"].index(pick) + 1
    chance = 1 / n_systems
    return {
        "turns": len(turns),
        "votes": votes,
        "first_matches_pick": matches,
        "rate": round(matches / votes, 3) if votes else None,
        "chance": round(chance, 3),
        "pick_mean_rank": round(rank_total / votes, 2) if votes else None,
        # Passes at one turn are not independent, so this flatters the judge.
        "p_optimistic": round(binom_tail(matches, votes, chance), 4) if votes else None,
    }


def print_agreement(agreement: dict) -> None:
    if not agreement["votes"]:
        print("  Human agreement: no overlapping turns.")
        return
    print(
        f"  Judge's first choice matched the person's pick in {agreement['first_matches_pick']} of "
        f"{agreement['votes']} votes over {agreement['turns']} turns ({agreement['rate']:.0%}; chance "
        f"{agreement['chance']:.0%}, mean rank of their pick {agreement['pick_mean_rank']}; "
        f"p<={agreement['p_optimistic']}, votes not independent)."
    )


def control_report(control: str, summary: dict) -> None:
    votes = summary["votes"]
    if not votes:
        return
    first = summary["first_place"]
    if control in ("null", "samples"):
        by_pos = list(summary["first_by_position"].values())
        p = chi_square_p_df2(by_pos)
        top = max(by_pos) / votes
        print(
            f"  {control.upper()}: first place by position {dict(summary['first_by_position'])}; the most "
            f"favoured position took {top:.0%} (fair is 33%), chance of a lean this strong p={p:.3f}. "
            "Spread beyond this is bias, not signal."
        )
    elif control == "mismatch":
        last = summary["last_place"]["MISMATCH"]
        share = last / votes
        verdict = "PASS" if share >= 0.9 else "FAIL"
        print(
            f"  MISMATCH: the wrong-turn reply ranked last in {last} of {votes} votes ({share:.0%}), "
            f"first in {first['MISMATCH']}. {verdict} (bar: 90% last)."
        )
    elif control == "textbook":
        wins = summary["pairwise_wins"]
        print(
            f"  TEXTBOOK: first place {first['TEXTBOOK']} of {votes}; over BoneAmanita "
            f"{wins['TEXTBOOK over BONEAMANITA']} - {wins['BONEAMANITA over TEXTBOOK']}, "
            f"over Prompted {wins['TEXTBOOK over PROMPTED']} - {wins['PROMPTED over TEXTBOOK']}. "
            "If it wins, this judge rewards the style the voice is built to avoid."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    parser.add_argument("--topic", default="promotion")
    parser.add_argument("--control", choices=sorted(SLOTS), default="none")
    parser.add_argument("--responsive", action="store_true", help="judge the simulated-person runs")
    parser.add_argument("--held", choices=HELD_MODES, default=None, help="default: skip, or forfeit with --responsive")
    parser.add_argument("--context-exchanges", type=int, default=1, help="--responsive: prior exchanges shown")
    parser.add_argument("--bone-cache", type=Path, default=Path("tools/cache/somatic_census.jsonl"))
    parser.add_argument("--vanilla-cache", type=Path, default=Path("tools/cache/somatic_vanilla.jsonl"))
    parser.add_argument("--prompted-cache", type=Path, default=Path("tools/cache/somatic_prompted.jsonl"))
    parser.add_argument("--textbook-cache", type=Path, default=Path("tools/cache/somatic_textbook.jsonl"))
    parser.add_argument("--responsive-cache", type=Path, default=Path("tools/cache/somatic_responsive.jsonl"))
    parser.add_argument("--judge-model", default=JUDGE_MODEL)
    parser.add_argument("--think", choices=sorted(THINK_VALUES), default="off", help="reasoning judges")
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260920)
    parser.add_argument("--human", type=Path, help="a person's picks, the panel's copied text")
    parser.add_argument("--agree", type=Path, help="with --human: score a finished judge JSON, no model calls")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    picks = parse_human(args.human.read_text(encoding="utf-8")) if args.human else None
    if args.agree:
        if not picks:
            print("--agree needs --human with at least one parsed pick.")
            return 1
        saved = json.loads(args.agree.read_text(encoding="utf-8"))
        print(f"=== {args.agree.name} against {args.human.name} ({len(picks)} picks) ===")
        print_agreement(human_agreement(saved["results"], picks))
        return 0

    control = args.control
    if args.responsive and control not in ("none", "mismatch"):
        print(f"--control {control} is not wired up for --responsive yet (only none/mismatch are).")
        return 1
    held_mode = args.held or ("forfeit" if args.responsive else "skip")
    if control != "none" and held_mode == "forfeit":
        print("Controls need every system delivered; using --held skip.")
        held_mode = "skip"
    think = THINK_VALUES[args.think]

    sources = SOURCES[control]
    caches = {
        "BONEAMANITA": args.bone_cache,
        "VANILLA": args.vanilla_cache,
        "PROMPTED": args.prompted_cache,
        "TEXTBOOK": args.textbook_cache,
        **{name: args.prompted_cache for name in SAMPLE_BACK},
    }
    runs = {}
    for name in sources:
        if args.responsive:
            runs[name] = load_latest(args.responsive_cache, args.topic, RESPONSIVE_ARMS[name])
        else:
            runs[name] = load_latest(caches[name], args.topic, back=SAMPLE_BACK.get(name, 0))
        if not runs[name]:
            print(f"No {name} records for topic {args.topic!r} (samples needs three Prompted runs).")
            return 1
    all_turns = sorted(set().union(*[set(r) for r in runs.values()]))

    def delivered(name: str, turn: int) -> bool:
        return is_delivered(runs[name].get(turn))

    slots = SLOTS[control]
    if held_mode == "forfeit":
        comparable = [t for t in all_turns if sum(delivered(s, t) for s in sources) >= 2]
    else:
        comparable = [t for t in all_turns if all(delivered(s, t) for s in sources)]
    skipped = [t for t in all_turns if t not in comparable]

    decoys = {}
    if control == "mismatch":
        valid = [t for t in all_turns if delivered("PROMPTED", t)]
        phases = {t: runs["PROMPTED"][t].get("phase") for t in all_turns if t in runs["PROMPTED"]}
        decoys = pick_decoys(comparable, valid, random.Random(args.seed + 1), phases)
        comparable = [t for t in comparable if t in decoys]

    system_prompt = JUDGE_SYSTEM_RESPONSIVE if args.responsive else JUDGE_SYSTEM
    rng = random.Random(args.seed)
    history: list = []
    results = []
    first = {s: 0 for s in slots}
    last = {s: 0 for s in slots}
    rank_sum = {s: 0 for s in slots}
    pair = {(a, b): 0 for a in slots for b in slots if a != b}
    first_by_position = {letter: 0 for letter in letters(len(slots))}
    votes = unparsed = agree = forfeited = 0

    def exchanges_before(name: str, turn: int) -> list:
        return build_exchanges_before(runs, name, turn, args.context_exchanges)

    def responsive_view(name: str, turn: int) -> dict:
        return build_responsive_view(runs, decoys, exchanges_before, name, turn)

    for turn in all_turns:
        message = next(runs[s][turn]["message"] for s in sources if turn in runs[s])
        history.append(message)
        if turn not in comparable:
            continue
        present = [s for s in slots if control != "none" or delivered(s, turn)]
        held = [s for s in slots if s not in present]
        texts = None if args.responsive else candidate_replies(control, turn, runs, decoys)
        firsts = []
        for p in range(args.passes):
            order = rng.sample(present, len(present))
            if args.responsive:
                views = [responsive_view(s, turn) for s in order]
                prompt = build_prompt_responsive(views)
            else:
                prompt = build_prompt(history, [texts[s] for s in order])
            verdict = judge(args.judge_model, system_prompt, prompt, len(order), think)
            if verdict["order"] is None:
                unparsed += 1
                print(f"  [{turn:>2}.{p}] UNPARSED  {verdict['raw'][:80]!r}")
                continue
            ranked = [order[letters(len(order)).index(l)] for l in verdict["order"]] + held
            forfeited += len(held)
            votes += 1
            first[ranked[0]] += 1
            last[ranked[-1]] += 1
            first_by_position[verdict["order"][0]] += 1
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
                    "presented_as": {letters(len(order))[i]: s for i, s in enumerate(order)},
                    "ranked": ranked,
                    "held": held,
                    "reason": verdict["reason"],
                }
            )
            print(f"  [{turn:>2}.{p}] {' > '.join(r[:5] for r in ranked):<24} {verdict['reason'][:70]}")
        if len(firsts) == args.passes and len(set(firsts)) == 1:
            agree += 1

    summary = {
        "judge_model": args.judge_model,
        "control": control,
        "responsive": args.responsive,
        "held_mode": held_mode,
        "think": args.think,
        "passes": args.passes,
        "comparable_turns": len(comparable),
        "skipped_turns": skipped,
        "votes": votes,
        "unparsed": unparsed,
        "forfeited_slots": forfeited,
        "first_place": first,
        "last_place": last,
        "first_by_position": first_by_position,
        "mean_rank": {s: round(rank_sum[s] / votes, 2) if votes else None for s in slots},
        "pairwise_wins": {f"{a} over {b}": n for (a, b), n in pair.items()},
        "passes_agree_on_winner": agree,
    }
    if picks:
        summary["human_agreement"] = human_agreement(results, picks, len(slots))

    out = args.out
    if out is None:
        safe = args.judge_model.replace(":", "-").replace("/", "-")
        if args.responsive and control != "none":
            out = Path(f"tools/cache/blind_judge_responsive_control_{control}_{args.topic}_{safe}.json")
        elif args.responsive:
            out = Path(f"tools/cache/blind_judge_responsive_{args.topic}_{safe}.json")
        elif control != "none":
            out = Path(f"tools/cache/blind_judge_control_{control}_{args.topic}_{safe}.json")
        else:
            out = Path("tools/cache/blind_judge_results.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"summary": summary, "results": results}, indent=2))

    control_label = f"CONTROL {control.upper()} " if control != "none" else ""
    label = f"RESPONSIVE {control_label}" if args.responsive else control_label
    print(f"\n=== {label}BLIND JUDGE ({args.judge_model}), topic {args.topic!r}, {votes} votes over "
          f"{len(comparable)} turns x {args.passes} passes ===")
    for s in slots:
        print(f"  {s:<12} first place {first[s]:>3}   mean rank {summary['mean_rank'][s]}")
    print("  head to head (votes where the first ranked above the second):")
    for a, b in PAIRS.get(control, tuple(itertools.combinations(slots, 2))):
        print(f"    {a} {pair[(a, b)]} - {pair[(b, a)]} {b}")
    print(f"  both passes picked the same winner on {agree} of {len(comparable)} turns; unparsed {unparsed}")
    print(f"  first place by shown position: {first_by_position}")
    if forfeited:
        print(f"  Held turns scored as last place: {forfeited} slots.")
    if skipped:
        print(f"  Skipped (a system produced no reply): {skipped}")
    control_report(control, summary)
    if picks:
        print_agreement(summary["human_agreement"])
    print(f"  Full results: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
