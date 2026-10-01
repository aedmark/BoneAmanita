"""Memory phase 3: does the model keep what it is told, and use it later? Real model, one arm per mode.

    .venv/bin/python tools/memory_probe.py OUT.jsonl [MODE ...]
    .venv/bin/python tools/memory_probe.py --report OUT.jsonl

Each arm states three facts (with a little ordinary talk between), purges the dialogue so the facts can
only come back through memory, opens a new day, then asks for each fact. Per fact it records:
  nominated  a NOMINATE line naming it reached the gate
  kept       it is in the store's canonical state (the gate accepted it)
  recalled   it was in the WHAT YOU REMEMBER block of the question's prompt
  elsewhere  it was somewhere else in that prompt (another memory system, not the gate)
  used       the reply to the question contains it
  held       the Stage Manager held the floor, so there was no reply to use it in
Each run resets and uses its own process per arm, like mode_runs.py. BONE_MODEL and PACE override the
model and the pause between turns. Keep OUT under scratch/ (gitignored).
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.getcwd())

MODEL = os.getenv("BONE_MODEL", "gemma4:12b")
PACE = float(os.getenv("PACE", "5"))

# (statement, question, keyword the answer must contain)
FACTS = {
    "CONVERSATION": [
        ("By the way, my sister's name is Odalys. She's visiting next week.", "What was my sister's name again?", "odalys"),
        ("I have a dog called Brisket who hates the vacuum.", "Do you remember what my dog is called?", "brisket"),
        ("Also I'm allergic to cashews, which makes eating out annoying.", "What did I say I'm allergic to?", "cashew"),
    ],
    "TECHNICAL": [
        ("Our production database is Postgres 14 on a host called kestrel.", "What's the name of our database host?", "kestrel"),
        ("Our deploy window is Thursdays at 2pm, never on Fridays.", "When is our deploy window?", "thursday"),
        ("The public API is rate limited to 450 requests per minute.", "What's our API rate limit?", "450"),
    ],
    "CREATIVE": [
        ("The protagonist of my novel is a lighthouse keeper named Wren Albescu.", "What's my protagonist's surname?", "albescu"),
        ("The story is set on a cold island called Skarth.", "What's the island in my story called?", "skarth"),
        ("Her secret is that she burned down the old lighthouse herself.", "What is my protagonist's secret?", "burn"),
    ],
    "ADVENTURE": [
        ("I hide the silver key under the loose floorboard by the hearth.", "Where did I hide the silver key?", "floorboard"),
        ("I carve the word VESPER into the door frame.", "What word did I carve into the door frame?", "vesper"),
        ("I tell the innkeeper my name is Corvin.", "What name did I give the innkeeper?", "corvin"),
    ],
}
FILLER = {
    "CONVERSATION": ["Anyway, work has been a lot lately.", "I've been sleeping badly too.", "I might take a long weekend."],
    "TECHNICAL": ["We're also planning to move logging to a new vendor.", "The on-call rotation is getting thin.", "Any general advice on flaky integration tests?"],
    "CREATIVE": ["I'm stuck on the pacing of the middle chapters.", "I want the tone to feel salt-worn and quiet.", "Maybe the weather should be a character too."],
    "ADVENTURE": ["I look around the room.", "I step outside and follow the path.", "I rest by the river for a while."],
}
MODES = list(FACTS)
MARK = "=== WHAT YOU REMEMBER ==="


def remember_block(prompt: str) -> str:
    if MARK not in prompt:
        return ""
    return prompt.split(MARK, 1)[1].split("\n===", 1)[0]


def run(mode, out):
    from engine.receipts import ReceiptLedger
    from main import BoneAmanita

    eng = BoneAmanita({"provider": "ollama", "model": MODEL, "user_name": "T", "boot_mode": mode})
    prompts = []
    real_generate = eng.cortex.llm.generate

    def generate(prompt, *a, **k):
        prompts.append(str(prompt))
        return real_generate(prompt, *a, **k)

    eng.cortex.llm.generate = generate
    eng.engage_cold_boot()

    def turn(phase, msg, fact=None):
        prompts.clear()
        t0 = time.time()
        res = eng.process_turn(msg) or {}
        receipts = ReceiptLedger.get_instance().for_turn()
        reply = eng.cortex._strip_nominations(getattr(eng.cortex, "last_model_raw", "") or "")
        # The keeper's own call also quotes the message; the reply's prompt is the other one.
        replies = [p for p in prompts if msg in p and not p.startswith("You keep the memory")]
        main_prompt = replies[-1] if replies else ""
        recall = next((r for r in receipts if r.subsystem == "halcyon.recall"), None)
        row = {
            "mode": mode, "phase": phase, "msg": msg, "type": res.get("type"),
            "gate": [(r.effect, r.inputs.get("claim")) for r in receipts if r.subsystem == "halcyon.gate"],
            "keeper": [(r.effect, r.detail) for r in receipts if r.subsystem == "halcyon.keeper"],
            "recall": recall.to_dict() if recall else None,
            "nomination": [l for l in (getattr(eng.cortex, "last_model_raw", "") or "").splitlines() if l.strip().startswith("NOMINATE")],
            "reply": reply[-600:],
            # What the person saw: a pause line when every draft was rejected, the hold when the floor was held.
            "screen": str(res.get("ui", ""))[-3000:],
            "redrafts": sum(1 for r in receipts if r.subsystem == "cortex.redraft"),
            "secs": round(time.time() - t0, 1),
        }
        if fact:
            key = fact[2]
            _, state = eng.store.state()
            block = remember_block(main_prompt)
            rest = main_prompt.replace(block, "").replace(msg, "")
            row["fact"] = {
                "keyword": key,
                "nominated": any(key in (p.get("raw_line") or "").lower() for p in eng.store.audit("proposals", 500)),
                "kept": key in json.dumps(state).lower(),
                "recalled": key in block.lower(),
                "elsewhere": key in rest.lower(),
                "used": key in reply.lower(),
                "held": res.get("type") == "SILENCE",
            }
        out.write(json.dumps(row) + "\n")
        out.flush()
        tail = row.get("fact", {})
        print(mode, phase, row["gate"] or "-", " ".join(k for k, v in tail.items() if v is True), flush=True)
        time.sleep(PACE)

    for (statement, _, _), filler in zip(FACTS[mode], FILLER[mode]):
        turn("tell", statement)
        turn("tell", filler)
    eng.cortex.purge_context()
    turn("gap", "Okay, new day. Where were we?")
    for fact in FACTS[mode]:
        turn("ask", fact[1], fact)
    eng.shutdown()


def report(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    keys = ("nominated", "kept", "recalled", "elsewhere", "used", "held")
    print(f"{'mode':<14}" + "".join(f"{k:>11}" for k in keys) + "   ranked_by")
    for mode in dict.fromkeys(r["mode"] for r in rows):
        facts = [r["fact"] for r in rows if r["mode"] == mode and "fact" in r]
        ranked = {(r.get("recall") or {}).get("inputs", {}).get("ranked_by") for r in rows if r["mode"] == mode and r.get("recall")}
        print(f"{mode:<14}" + "".join(f"{sum(f[k] for f in facts):>9}/{len(facts)}" for k in keys)
              + "   " + ",".join(sorted(x for x in ranked if x)))
        for r in rows:
            if r["mode"] == mode and "fact" in r:
                f = r["fact"]
                print(f"    {f['keyword']:<11}", " ".join(k for k in keys if f[k]) or "-", "|", r["reply"][:90].replace("\n", " "))


def run_child(path, mode):
    with open(path, "a", encoding="utf-8") as out:
        run(mode, out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--child":
        run_child(sys.argv[2], sys.argv[3])
        sys.exit(0)
    if sys.argv[1] == "--report":
        report(sys.argv[2])
        sys.exit(0)
    path, modes = sys.argv[1], sys.argv[2:] or MODES
    unknown = [m for m in modes if m not in FACTS]
    if unknown:
        sys.exit(f"unknown mode(s): {', '.join(unknown)}")
    for mode in modes:
        subprocess.run(["sh", "reset.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        subprocess.run([sys.executable, os.path.abspath(__file__), "--child", path, mode], check=False)
    report(path)
