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


def opener(reply: str, n: int = 3) -> str:
    return " ".join(w.lower() for w in WORD.findall(visible_text(reply))[:n])


def reply_facts(reply: str, message: str = "", crime=None) -> dict:
    """One reply's rule and habit flags. `crime` is a callable text -> truthy when the Gatekeeper's list matches."""
    text = visible_text(reply)
    m = measure(reply, True, message)
    words = m.get("words") or 0
    return {
        "empty": not words,
        "words": words,
        "within_3": m.get("within_3_sentences") == 1.0,
        "dash": bool(DASH.search(text)),
        "markdown": bool(MARKDOWN.search(text)),
        "crime": bool(crime(text)) if crime else False,
        "body": bool((m.get("stage_directions") or 0) > 0),
        "questions": m.get("question_count") or 0,
        "ends_q": m.get("ends_with_question") == 1.0,
        "validating": bool(VALIDATING_OPENER.search(text)),
        "stock": {w: w in text.lower() for w in STOCK_WORDS},
        "opener": opener(reply),
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
        "stock": sum(1 for f in facts if any(f["stock"].values())) / n,
        "openers": len({f["opener"] for f in facts}) / n,
    }


COLUMNS = [("n", "n", "{:.0f}"), ("words", "words", "{:.0f}"), ("within_3", "<=3 sent", "{:.0%}"), ("dash", "dash", "{:.0%}"),
           ("markdown", "markdown", "{:.0%}"), ("crime", "crime", "{:.0%}"), ("body", "body", "{:.0%}"),
           ("questions", "?/reply", "{:.2f}"), ("ends_q", "ends ?", "{:.0%}"), ("validating", "validating", "{:.0%}"),
           ("stock", "stock", "{:.0%}"), ("openers", "distinct openers", "{:.0%}")]


def gatekeeper_crime(mode: str):
    """The Gatekeeper's own list as it applies in `mode` (some patterns are skipped in CONVERSATION)."""
    from physics.filters import TheGatekeeper

    gate = TheGatekeeper({})
    return lambda text: gate._find_crime(text, mode)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arms", nargs="*", default=["bone=m", "old=o", "plain=p", "friend=f"])
    ap.add_argument("--dir", default="scratch/probes/noise")
    ap.add_argument("--mode", default="CONVERSATION", help="the engine mode whose style rules apply")
    ap.add_argument("--turns", default="", help="comma-separated 0-based turn indexes to keep (default: all)")
    args = ap.parse_args()
    keep = {int(t) for t in args.turns.split(",") if t} or None
    crime = gatekeeper_crime(args.mode)
    rows = {}
    for spec in args.arms:
        label, prefix = spec.split("=")
        facts = []
        for path in sorted(glob.glob(f"{args.dir}/{prefix}[0-9].jsonl")):
            for i, line in enumerate(open(path)):
                r = json.loads(line)
                if keep is None or i in keep:
                    facts.append(reply_facts(r["reply"], r.get("message", ""), crime))
        if facts:
            rows[label] = summarize(facts)
    print(f"{'':8}" + "".join(f"{h:>17}" if h == "distinct openers" else f"{h:>11}" for _, h, _ in COLUMNS))
    for label, s in rows.items():
        print(f"{label:8}" + "".join(f"{fmt.format(s[k]):>17}" if k == "openers" else f"{fmt.format(s[k]):>11}" for k, _, fmt in COLUMNS))


if __name__ == "__main__":
    main()
