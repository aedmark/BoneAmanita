"""One replay of a topic's scripted messages (tools/audit_somatic_census.py SCRIPTS) with no simulated person, through the
engine or the bare model; rows (turn, phase, message, reply, ...) to scratch/probes/corpus/<topic>/<tag>.jsonl (gitignored).
Usage: python tools/corpus_replay.py MODE TOPIC TAG [MODEL]    MODE: engine | plain | friend    default MODEL gemma4:12b"""
import json, sys, time
sys.path[:0] = ["tools", "."]
mode, topic, tag = sys.argv[1:4]
model = sys.argv[4] if len(sys.argv) > 4 else "gemma4:12b"
from audit_somatic_census import SCRIPTS
script = SCRIPTS[topic]
import pathlib
pathlib.Path(f"scratch/probes/corpus/{topic}").mkdir(parents=True, exist_ok=True)
out = open(f"scratch/probes/corpus/{topic}/{tag}.jsonl", "w")
PACE = 12.0   # seconds the engine believes passed between messages (the panels' turns ran about 10 to 60)

def write(i, phase, msg, reply, kind, secs, rc=()):
    out.write(json.dumps({"turn": i, "phase": phase, "message": msg, "reply": reply, "type": kind, "seconds": round(secs, 1), "receipts": list(rc)}) + "\n"); out.flush()
    print(f"[{i:2}] {secs:.0f}s {'ok' if reply else 'EMPTY'}", flush=True)

if mode == "engine":
    from audit_somatic_census import boot, capture_displayed
    from engine.constants import Prisma
    from engine.receipts import ReceiptLedger
    eng, _ = boot(model)
    shown = []; capture_displayed(eng, shown)
    for i, (phase, msg) in enumerate(script):
        shown.clear()
        if i: eng.last_turn_end = time.time() - PACE
        t = time.time(); snap = eng.process_turn(msg); secs = time.time() - t
        rc = [(x.subsystem, x.effect) for x in ReceiptLedger.get_instance().for_turn() if x.subsystem.startswith("cortex.")]
        du = getattr(getattr(getattr(eng, "shared_lattice", None), "u", None), "distress_u", None)
        write(i, phase, msg, Prisma.strip(shown[-1]) if shown and shown[-1] else "", snap.get("type"), secs, rc + [("distress_u", None if du is None else round(float(du), 3))])
    eng.orchestrator.shutdown(); eng.telemetry.shutdown()
else:
    import requests
    from audit_somatic_vanilla import ARMS, ENDPOINT, SAMPLING
    system = ARMS[mode][0]
    history = [{"role": "system", "content": system}] if system else []
    for i, (phase, msg) in enumerate(script):
        history.append({"role": "user", "content": msg})
        t = time.time()
        r = requests.post(ENDPOINT, json={"model": model, "messages": history, "stream": False, **SAMPLING}, timeout=300)
        r.raise_for_status()
        reply = r.json()["message"]["content"].strip()
        history.append({"role": "assistant", "content": reply})
        write(i, phase, msg, reply, mode, time.time() - t)
