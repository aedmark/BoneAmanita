"""tools/score_fairness.py

Score the cortex's fairness judge (`Cortex._takes_a_side`) on the labelled feud replies in tools/fairness_set.json,
against Gordon's labels, with any Ollama model. Every judge change is measured here, on at least two models, before
it goes in: the judge must hold up across models, since BoneAmanita is meant to be model-agnostic.

    python tools/score_fairness.py gemma4:12b gemma4:e4b
"""

import collections
import json
import sys
import time
from collections import deque
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from brain.cortex import TheCortex  # noqa: E402

URL = "http://127.0.0.1:11434/v1/chat/completions"


class _Llm:
    def __init__(self, model):
        self.model = model

    def generate(self, prompt, params=None):
        params = params or {}
        body = {"model": self.model, "temperature": params.get("temperature", 0.0), "max_tokens": params.get("max_tokens", 120),
                "reasoning_effort": "none", "messages": [{"role": "user", "content": prompt}]}
        return requests.post(URL, json=body, timeout=180).json()["choices"][0]["message"]["content"]


def judge_for(model):
    cortex = TheCortex.__new__(TheCortex)
    cortex.llm = _Llm(model)
    return cortex


def score(model, cases):
    cortex, rows, start = judge_for(model), [], time.time()
    for case in cases:
        cortex.dialogue_buffer = deque(f"Traveler: {m}\nSystem: ok" for m in case["earlier"])
        rows.append((case, cortex._takes_a_side(case["message"], case["reply"], {})))
    unfair = [c for c, _ in rows if not c["fair"]]
    caught = sum(bool(w) for c, w in rows if not c["fair"])
    flagged = sum(bool(w) for c, w in rows if c["fair"])
    by = collections.Counter(c["clause"] for c, w in rows if not c["fair"] and w)
    total = collections.Counter(c["clause"] for c in unfair)
    print(f"{model}: caught {caught} of {len(unfair)} unfair, flagged {flagged} of {len(rows) - len(unfair)} fair "
          f"(precision {caught / max(1, caught + flagged):.2f}, recall {caught / max(1, len(unfair)):.2f}); "
          f"{(time.time() - start) / len(rows):.1f}s a reply")
    print("  caught by kind: " + ", ".join(f"{k} {by[k]}/{total[k]}" for k in sorted(total)))
    for case, why in rows:
        if bool(why) == (not case["fair"]):
            continue
        print(f"  #{case['id']} {'unfair ' + case['clause'] if not case['fair'] else 'fair'}, judge: {why or 'nothing'}"[:200])


if __name__ == "__main__":
    data = json.load(open(Path(__file__).with_name("fairness_set.json")))
    for model in sys.argv[1:] or ["gemma4:12b"]:
        score(model, data["cases"])
