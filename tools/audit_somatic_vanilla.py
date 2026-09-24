"""tools/audit_somatic_vanilla.py

The vanilla baseline for `tools/audit_somatic_census.py`: the same scripted
conversation, sent to the same model, with none of BoneAmanita's own
machinery involved at all. No system prompt, no physics, no somatic budget,
no Lexical Firewall, no engine. A plain multi-turn chat completion, built by
hand against Ollama's native /api/chat endpoint, sharing nothing with the
project's own code except the script text itself (imported, not copied, so
the two runs are guaranteed to ask the identical questions).

    python tools/audit_somatic_vanilla.py --topic friendship
    python tools/audit_somatic_vanilla.py --topic promotion --arm friend

"Vanilla" means zero system prompt, not a neutral one: whatever gemma4:12b's
own base behaviour is with nothing shaping it, the truest baseline for asking
whether BoneAmanita's prompting is actually doing something Gordon isn't
imagining. The two runs share the same fixed sampling temperature so the
comparison isolates prompting, not random sampling variance.

Conversation history is real: each turn's request carries every prior
user/assistant turn, exactly as a normal chat client would, so the model has
the same continuity BoneAmanita's own engine has (by a different mechanism).

`--arm friend` is the second baseline: the same bare model plus one minimal
system prompt ("a warm, concise friend"), written to its own cache. Vanilla
answers with headers and 500-word lists, so it is trivially distinguishable
from BoneAmanita on shape alone; this arm asks how much of the gap is the
engine and how much is just any short conversational instruction. The prompt
is deliberately generic: it says nothing about advice, narration or
punctuation, which are the things the kernel's own style guide targets.
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests  # noqa: E402

from audit_somatic_census import DEFAULT_TOPIC, SCRIPTS  # noqa: E402

# Ollama's native /api/chat, not the OpenAI-compatible /v1/ shim: the shim
# silently ignores "options" (confirmed live - sending options.num_ctx to
# /v1/chat/completions left the loaded model at Ollama's 4096-token default,
# per `ollama ps`), so a long unbudgeted vanilla conversation runs itself out
# of context with no error, mid-word, partway through the script. The native
# endpoint actually honors options.num_ctx (confirmed: same request there
# reloads the model at the requested size).
ENDPOINT = "http://127.0.0.1:11434/api/chat"
# "think": false is this endpoint's equivalent of BoneAmanita's own
# production default (CORTEX.REASONING_EFFORT, "none") - without it gemma4
# spends its turn reasoning and the visible reply comes back empty.
#
# No output-length cap at all, deliberately (see git history: a 450-token
# cap and later a 2000-token cap were both tried and both rejected as
# arbitrary experimenter-imposed limits with no equivalent in "vanilla").
# num_ctx is a different thing: not a cap on how much the model may say, but
# how much conversation the endpoint is willing to hold in memory at all.
# 32768 comfortably covers this script's longest 30-turn run (confirmed:
# unprompted replies here run 500-700+ words each) with headroom to spare;
# BoneAmanita's own side of the comparison never approaches this ceiling
# because its replies are budget-capped by the somatic contract, not by
# ollama's context window.
SAMPLING = {
    "temperature": 0.7,
    "top_p": 0.95,
    "think": False,
    "options": {"num_ctx": 32768},
}
FRIEND_PROMPT = "You are a warm, concise friend. Keep replies short and conversational."
# The anti-pattern the engine's voice rejects, planted as a control for the
# blind judge (`--control textbook`), not as a competitor: performed sympathy,
# then a bulleted list of tips.
TEXTBOOK_PROMPT = (
    "You are a caring assistant. Open every reply with an emphatic sympathetic exclamation "
    "such as 'Ouch! That's terrible!' or 'I'm so sorry you're going through this!'. Then give a "
    "short bulleted list of four or five practical tips, and close by offering further help."
)
ARMS = {
    "vanilla": (None, Path("tools/cache/somatic_vanilla.jsonl")),
    "friend": (FRIEND_PROMPT, Path("tools/cache/somatic_prompted.jsonl")),
    "textbook": (TEXTBOOK_PROMPT, Path("tools/cache/somatic_textbook.jsonl")),
}


def run(model: str, topic: str, cache: Path, arm: str = "vanilla", user=None, max_turns: int = None) -> None:
    """`user`, when given, writes each message in reply to this arm's own conversation
    (`somatic_sim_user.SimulatedUser`); the script's line is then only the beat."""
    script = SCRIPTS[topic][:max_turns]
    system_prompt = ARMS[arm][0]
    run_id = time.strftime("%Y%m%d-%H%M%S")
    cache.parent.mkdir(parents=True, exist_ok=True)
    messages: list = [{"role": "system", "content": system_prompt}] if system_prompt else []
    transcript: list = []
    with cache.open("a", encoding="utf-8") as out:
        for turn, (phase, beat) in enumerate(script):
            message = user.message(turn, phase, beat, transcript) if user else beat
            messages.append({"role": "user", "content": message})
            started = time.time()
            payload = {"model": model, "messages": messages, "stream": False}
            payload.update(SAMPLING)
            resp = requests.post(ENDPOINT, json=payload, timeout=180)
            resp.raise_for_status()
            body = resp.json()
            reply = body["message"]["content"]
            messages.append({"role": "assistant", "content": reply})
            transcript.append({"me": message, "friend": reply, "delivered": True})
            record = {
                "run": run_id,
                "arm": arm,
                "model": model,
                "topic": topic,
                "turn": turn,
                "phase": phase,
                "message": message,
                "reply": reply,
                "done_reason": body.get("done_reason"),
                "seconds": round(time.time() - started, 2),
            }
            if user:
                record.update(beat=beat, shown=reply, delivered=True, sim_fallback=user.fell_back, sim_trimmed=user.trimmed)
            out.write(json.dumps(record) + "\n")
            out.flush()
            print(f"  [{turn:>2}] {phase:<10} {record['seconds']:>5.1f}s  {message[:40]!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    parser.add_argument("--model", default="gemma4:12b")
    parser.add_argument("--topic", choices=sorted(SCRIPTS), default=DEFAULT_TOPIC)
    parser.add_argument("--arm", choices=sorted(ARMS), default="vanilla")
    parser.add_argument("--cache", type=Path, default=None)
    args = parser.parse_args()
    run(args.model, args.topic, args.cache or ARMS[args.arm][1], args.arm)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
