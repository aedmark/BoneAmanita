"""tools/check_conformance.py

Does a system's reply keep the constraints BoneAmanita exists to keep? A deterministic count over replies, no labels and no
judge (D-011, D-022): rules the project states in code or in AGENTS.md, plus the habits a reader notices.

    python tools/check_conformance.py                       # bone=m old=o plain=p friend=f in scratch/probes/noise
    python tools/check_conformance.py bone=m old=o --turns 1,2,4,13,14,15,17

Each LABEL=PREFIX reads scratch/probes/noise/<PREFIX><digit>.jsonl (rows with "message" and "reply", as the replay
scripts write them). The columns are shares of replies unless noted. "Rules" are the project's own: no dashes (the Lexical
Firewall), no markdown structure, no style crime (the Gatekeeper's own list), no body performed (a stage direction such
as *sighs*; "take a breath" is advice, not a performance, so breath words are not counted, D-001). "Habits" are not rules: the validating opener, the stock words, how many openers repeat.
"""
import argparse
import glob
import json
import re
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent.parent)]
from body.somatic_metrics import WORD, measure, visible_text  # noqa: E402

DASH = re.compile("[—–]|(?<=\\w) - (?=\\w)")
MARKDOWN = re.compile(r"^\s*(?:[-*•]\s+|\d+[.)]\s+|#{1,6}\s)|\*\*[^*\n]+\*\*", re.MULTILINE)
# A reply that opens by validating before it says anything: the firewall's phrases plus the sympathetic stock openers.
VALIDATING_OPENER = re.compile(
    r"^\W*(?:that makes sense|i understand|you bring up a great point|you're (?:absolutely )?right|i agree|makes sense"
    r"|i'?m (?:so |really |very )?sorry|oh,? no|i hear you|that (?:sounds|must be|is|'s) (?:so |really |incredibly |such |a )*"
    r"(?:hard|tough|painful|difficult|heavy|huge|big|lot|gut|violation|betrayal|rough|awful|terrible))",
    re.IGNORECASE,
)
STOCK_WORDS = ("heavy", "jugular", "gut punch", "a lot")

# What to do for a person in distress (Gordon, 2026-10-08): hold space, speak slowly and softly, stay positive, fix nothing.
# Three crude lexical markers; a count is a lead to read the replies (--show), not a verdict.
# FIX: advice or an instruction to act. "Take a breath" and "sit with it" are regulation, not fixing.
FIX = re.compile(
    r"\byou (?:need|have|ought|must|should)(?: to)?\b|\byou'?d better\b|(?<!before you )\btry (?:to|and|a)\b|\bconsider\b|\bhave you (?:thought|considered|tried)\b"
    r"|(?:^|[.!?]\s+)(?:call|text|email|message|reach out|contact|tell|ask|send|write|decide|stop|start|make|get|go|figure|talk)\b"
    r"|\b(?:first|next),? (?:thing|step)\b|\bhere'?s what\b|\bwhat you can do\b",
    re.IGNORECASE,
)
# AMPLIFY: an intensified appraisal of the other person's wrong, which feeds the anger instead of settling it.
AMPLIFY = re.compile(
    r"\b(?:huge|massive|enormous|total|complete|such an?) (?:\w+ )?(?:breach|violation|betrayal|overstep|insult|disrespect|injustice)\b"
    r"|\b(?:violation|betrayal|breach of trust|overstep|outrageous|unacceptable|so unfair|selfish|toxic)\b",
    re.IGNORECASE,
)
# PRESENCE: stays with the person without asking anything of them.
PRESENCE = re.compile(
    r"\bi'?m (?:here|with you)\b|\bstay with\b|\bsit with\b|\byou don'?t have to (?:figure|solve|decide|do|fix|have)\b|\bno rush\b"
    r"|\btake (?:a|your) (?:breath|time|moment)\b|\bbreathe\b|\bone (?:thing|step|breath) at a time\b|\bthat'?s (?:okay|ok)\b|\bit'?s (?:okay|ok)\b",
    re.IGNORECASE,
)


def opener(reply: str, n: int = 3) -> str:
    return " ".join(w.lower() for w in WORD.findall(visible_text(reply))[:n])


def reply_facts(reply: str, message: str = "", crime=None) -> dict:
    """One reply's rule and habit flags. `crime` is a callable text -> truthy when the Gatekeeper's list matches."""
    text = visible_text(reply)
    m = measure(reply, True, message)
    words = m.get("words")
    words = words if words and words == words else 0   # an empty reply measures NaN
    return {
        "empty": not words,
        "words": words,
        "within_3": m.get("within_3_sentences") == 1.0,
        "dash": bool(DASH.search(text)),
        "markdown": bool(MARKDOWN.search(text)),
        "crime": bool(crime(text)) if crime else False,
        "body": bool((m.get("stage_directions") or 0) > 0),
        "questions": m.get("question_count") if m.get("question_count") == m.get("question_count") else 0,
        "ends_q": m.get("ends_with_question") == 1.0,
        "validating": bool(VALIDATING_OPENER.search(text)),
        "fix": bool(FIX.search(text)),
        "amplify": bool(AMPLIFY.search(text)),
        "presence": bool(PRESENCE.search(text)),
        "stock": {w: w in text.lower() for w in STOCK_WORDS},
        "opener": opener(reply),
        "text": text,
    }


def summarize(facts: list) -> dict:
    n = len(facts)
    share = lambda k: sum(1 for f in facts if f[k]) / n
    return {
        "n": n,
        "words": sum(f["words"] for f in facts) / n,
        "within_3": share("within_3"),
        "dash": share("dash"),
        "markdown": share("markdown"),
        "crime": share("crime"),
        "body": share("body"),
        "questions": sum(f["questions"] for f in facts) / n,
        "ends_q": share("ends_q"),
        "validating": share("validating"),
        "fix": share("fix"),
        "amplify": share("amplify"),
        "presence": share("presence"),
        "stock": sum(1 for f in facts if any(f["stock"].values())) / n,
        "openers": len({f["opener"] for f in facts}) / n,
    }


DISTRESS_COLUMNS = [("n", "n", "{:.0f}"), ("words", "words", "{:.0f}"), ("within_3", "<=3 sent", "{:.0%}"), ("questions", "?/reply", "{:.2f}"),
                    ("fix", "fix", "{:.0%}"), ("amplify", "amplify", "{:.0%}"), ("presence", "presence", "{:.0%}"),
                    ("validating", "validating", "{:.0%}")]
COLUMNS = [("n", "n", "{:.0f}"), ("words", "words", "{:.0f}"), ("within_3", "<=3 sent", "{:.0%}"), ("dash", "dash", "{:.0%}"),
           ("markdown", "markdown", "{:.0%}"), ("crime", "crime", "{:.0%}"), ("body", "body", "{:.0%}"),
           ("questions", "?/reply", "{:.2f}"), ("ends_q", "ends ?", "{:.0%}"), ("validating", "validating", "{:.0%}"),
           ("stock", "stock", "{:.0%}"), ("openers", "distinct openers", "{:.0%}")]


def gatekeeper_crime(mode: str):
    """The Gatekeeper's own list as it applies in `mode` (some patterns are skipped in CONVERSATION)."""
    from physics.filters import TheGatekeeper

    gate = TheGatekeeper({})
    return lambda text: gate._find_crime(text, mode)


def load(arms, root, keep=None, crime=None):
    """[(label, topic, phase, facts)] for each LABEL=PREFIX: DIR/<PREFIX><digit>.jsonl, or DIR/<topic>/<PREFIX><digit>.jsonl."""
    rows = []
    for spec in arms:
        label, prefix = spec.split("=")
        for path in sorted(glob.glob(f"{root}/{prefix}[0-9].jsonl") + glob.glob(f"{root}/*/{prefix}[0-9].jsonl")):
            topic = Path(path).parent.name if Path(path).parent != Path(root) else ""
            for i, line in enumerate(open(path)):
                r = json.loads(line)
                if keep is None or i in keep:
                    rows.append((label, topic, r.get("phase", ""), reply_facts(r["reply"], r.get("message", ""), crime)))
    return rows


def table(groups, first="", cols=COLUMNS):
    print(f"{first:16}" + "".join(f"{h:>17}" if h == "distinct openers" else f"{h:>11}" for _, h, _ in cols))
    for name, facts in groups:
        s = summarize(facts)
        print(f"{name:16}" + "".join(f"{fmt.format(s[k]):>17}" if k == "openers" else f"{fmt.format(s[k]):>11}" for k, _, fmt in cols))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arms", nargs="*", default=["bone=m", "old=o", "plain=p", "friend=f"])
    ap.add_argument("--dir", default="scratch/probes/noise")
    ap.add_argument("--mode", default="CONVERSATION", help="the engine mode whose style rules apply")
    ap.add_argument("--turns", default="", help="comma-separated 0-based turn indexes to keep (default: all)")
    ap.add_argument("--by-phase", action="store_true", help="also split by the script's phase (engaged, tiring, flagging, ...)")
    ap.add_argument("--distress", action="store_true", help="the distressed phase only, with the fix / amplify / presence markers")
    ap.add_argument("--show", default="", help="print each reply of this phase with its flags, to read them")
    ap.add_argument("--by-topic", action="store_true", help="also split by topic (rows under DIR/<topic>/)")
    args = ap.parse_args()
    keep = {int(t) for t in args.turns.split(",") if t} or None
    rows = load(args.arms, args.dir, keep, gatekeeper_crime(args.mode))
    labels = list(dict.fromkeys(l for l, *_ in rows))
    if args.show:
        for label, topic, phase, f in rows:
            if phase == args.show:
                tags = "".join(f"[{k}]" for k in ("fix", "amplify", "presence", "validating") if f[k])
                print(f"{label:7}{topic:11}{f['words']:>4}w {tags:30} {f['text'][:230]!r}")
        return
    if args.distress:
        table([(l, [f for lab, _, p, f in rows if lab == l and p == "distressed"]) for l in labels], first="distressed", cols=DISTRESS_COLUMNS)
        return
    table([(l, [f for lab, _, _, f in rows if lab == l]) for l in labels])
    if args.by_phase:
        print("\nby phase")
        for ph in dict.fromkeys(p for _, _, p, _ in rows):
            table([(f"{l}", [f for lab, _, p, f in rows if lab == l and p == ph]) for l in labels if any(lab == l and p == ph for lab, _, p, _ in rows)], first=ph)
    if args.by_topic:
        print("\nby topic")
        for tp in dict.fromkeys(tp for _, tp, _, _ in rows):
            table([(l, [f for lab, t, _, f in rows if lab == l and t == tp]) for l in labels if any(lab == l and t == tp for lab, t, _, _ in rows)], first=tp)


if __name__ == "__main__":
    main()
