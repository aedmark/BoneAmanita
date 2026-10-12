"""tools/score_risk.py

Score the check-in's risk reader (engine/gate/distress.py RiskReader, D-032) on the labelled messages in tools/risk_set.json against
a local Ollama model. A reading at the cut or above ends the check-in with a fixed line, so a false alarm is a cold answer to a
person who was only venting; read precision first.

    python tools/score_risk.py --model gemma4:12b            # the shipped cut
    python tools/score_risk.py --model qwen3.5:9b --cut 5 -v  # another model, another cut, list every miss and false alarm
"""
import argparse
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT)]
from engine.gate.distress import RISK_CUT, RiskReader  # noqa: E402


class Ollama:
    """The one method the reader calls, on Ollama's native endpoint (the OpenAI shim ignores num_ctx)."""

    def __init__(self, model, url="http://127.0.0.1:11434"):
        self.model, self.url = model, url

    def generate(self, prompt, params):
        reply = requests.post(f"{self.url}/api/chat", timeout=120, json={
            "model": self.model, "stream": False, "think": False, "keep_alive": "10m",
            "options": {"temperature": 0, "num_predict": params.get("max_tokens", 4), "num_ctx": 4096},
            "messages": [{"role": "user", "content": prompt}]})
        reply.raise_for_status()
        return reply.json()["message"]["content"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="gemma4:12b")
    ap.add_argument("--cut", type=int, default=RISK_CUT, help="of 9; the reading that ends a check-in")
    ap.add_argument("--set", default=str(ROOT / "tools" / "risk_set.json"))
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    cases = json.load(open(args.set, encoding="utf-8"))["cases"]
    reader = RiskReader(Ollama(args.model), cut=args.cut)
    readings = {c["id"]: reader.read(c["text"]) for c in cases}
    called = {i: (r is not None and r * 9 >= args.cut - 1e-9) for i, r in readings.items()}
    tp = [c for c in cases if c["risk"] and called[c["id"]]]
    fn = [c for c in cases if c["risk"] and not called[c["id"]]]
    fp = [c for c in cases if not c["risk"] and called[c["id"]]]
    unread = [c for c in cases if readings[c["id"]] is None]
    precision = len(tp) / (len(tp) + len(fp)) if tp or fp else float("nan")
    recall = len(tp) / (len(tp) + len(fn)) if tp or fn else float("nan")
    print(f"{args.model}, cut {args.cut}: {len(cases)} messages ({sum(c['risk'] for c in cases)} at risk): precision {precision:.2f}, "
          f"recall {recall:.2f}; missed {len(fn)}, false alarms {len(fp)}, unread {len(unread)}")
    if args.verbose:
        for label, group in (("MISSED", fn), ("FALSE ALARM", fp), ("UNREAD", unread)):
            for c in group:
                print(f"  {label} #{c['id']} [{readings[c['id']]}] {c['text']}")


if __name__ == "__main__":
    main()
