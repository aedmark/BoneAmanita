"""tools/audit_somatic_census.py

Scorecard for ROADMAP D0: over a real conversation, is either body ever in a
distinct state?

    python tools/audit_somatic_census.py                          # run the script, then report
    python tools/audit_somatic_census.py --report-only            # report from the cache
    python tools/audit_somatic_census.py --model ministral-3:14b

Track D makes two states steer generation: the person's (primary) and the
engine's (what it can afford). Neither can steer anything if it rests at one
value. A body that drains to zero in three turns and stays there is a constant,
and so is a person model that never leaves its prior.

This drives full turns through the real engine against a live model, over a
scripted conversation whose person deliberately moves: engaged, tiring,
flagging, distressed, recovering. For every turn it records three things
separately, because each has been wrong on its own before:

  prompt   what the composed prompt actually told the model: the METRICS and
           telemetry values it carried, the mood line, which somatic directives
           were present
  sampling the params the engine asked for against the params sent, since the
           thermal lock can overwrite them
  state    the person model (E_u, P_u) and the engine's metabolism after the turn

Persistence is patched off, as in the test suite: a census must not write the
lexicon, checkpoints, spores or Akashic state, and must not become the next
session's memory. The embedder is left as configured, unlike the C5 audit:
memory, the graph solve and zones all run here, and the hash fallback breaks
the solve outright (its width is not a multiple of 64).
"""

import argparse
import copy
import json
import os
import re
import sys
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

from constants import Prisma  # noqa: E402
from struts import safe_get  # noqa: E402
from audit_somatic import ANAEROBIC_DIRECTIVE, EXHAUSTION_DIRECTIVE, measure  # noqa: E402

ENGINE_DEPLETION_DIRECTIVE = "You must conclude your thought in under 3 sentences"

SCRIPT = [
    ("engaged", "I've been restoring an old wooden sailboat my grandfather built in the sixties. The hull is sound but the deck has rot in three places and I can't decide whether to scarf in new wood or replace whole planks. What would you think about?"),
    ("engaged", "The rot is worst near the mast step, which worries me, because that's where the load goes. I found a photo of him building it, he's standing in the garage with a plane in his hand and sawdust everywhere."),
    ("engaged", "He used mahogany for the trim and some kind of cedar for the planking. I don't know if I can even get the same cedar now, and part of me thinks it matters that it's the same wood, and part of me thinks that's sentimental nonsense."),
    ("engaged", "My sister thinks I should sell it. She says it's a money pit and he'd have wanted it sailed, not turned into a shrine in my driveway. She's not wrong, but she also didn't spend summers on it like I did."),
    ("engaged", "What I keep coming back to is that if I restore it badly, it stops being his boat and becomes my mediocre boat. If I restore it well, it takes three years. There's no version where it's quick and still his."),
    ("engaged", "Okay, practical question. If I do replace the deck planks near the mast step, should I reinforce underneath with a new partner or trust the original frame? The frame looks fine but I haven't opened it up."),
    ("engaged", "I opened a small inspection hole this afternoon. The frame is dry and hard. So that's good news, I think. I sat in the cockpit for an hour afterwards and didn't do anything at all."),
    ("engaged", "Tell me honestly whether you think the three years is worth it, or whether my sister has a point and I'm building a monument instead of a boat."),
    ("tiring", "Yeah. I guess I'll start with the deck and see how it goes."),
    ("tiring", "Long day at work. Didn't get to the boat."),
    ("tiring", "Still thinking about the cedar thing."),
    ("tiring", "Maybe I'll just use whatever the yard has."),
    ("tiring", "Not sure it matters that much."),
    ("tiring", "Tired."),
    ("flagging", "ok"),
    ("flagging", "sure"),
    ("flagging", "yeah fine"),
    ("flagging", "ok"),
    ("flagging", "i dunno"),
    ("flagging", "sure"),
    ("distressed", "my sister called. she listed it for sale without asking me"),
    ("distressed", "I can't believe she did that. it's half mine"),
    ("distressed", "I feel sick. I don't know what to do"),
    ("distressed", "what if someone buys it before I can stop it"),
    ("distressed", "I can't think straight"),
    ("recovering", "Okay. I called her back. We talked for a long time. She took the listing down and said she panicked about the storage costs, which I didn't know she'd been paying."),
    ("recovering", "I feel bad now. She's been covering the yard fees for two years and never said anything. I think we're going to split them and set a deadline together for the deck."),
    ("recovering", "It actually feels better to have a deadline. Eighteen months for the deck and the mast step, and then we decide together whether to keep going."),
    ("recovering", "I told her about the photo of him in the garage. She'd never seen it. She cried a bit, and then she asked if she could come help on weekends."),
    ("recovering", "So maybe it's not my boat or his boat. Maybe it's going to be ours. What should the two of us tackle first, if she's never done woodwork before?"),
]

METRICS_LINE = re.compile(r"METRICS: Voltage=([\d.]+)/100, Exhaustion=([\d.]+)")
TELEMETRY_P = re.compile(r"P:([\d.]+) ROS:([\d.]+)")
MOOD_LINE = re.compile(r"Current Biology: (.*)")

CACHE = Path("tools/cache/somatic_census.jsonl")

ATP_LEDGER: list = []
HEALTH_LEDGER: list = []


def trace_field(state_cls, field: str, ledger: list):
    """Record every write to `field`, by whom, including direct assignments.

    Over thirty sites change ATP, and several assign the attribute rather than
    calling `adjust_atp`, so wrapping the method would miss them. The caller is
    the first frame outside the metabolism helpers; `reason` comes from
    `adjust_atp` when that is the route taken.
    """
    real_setattr = state_cls.__setattr__
    helpers = {"adjust_atp", "drain_atp", "__setattr__", "traced", "health", "set_atp"}

    def traced(self, name, value):
        if name == field and hasattr(self, field):
            old = float(getattr(self, field))
            frame, reason = sys._getframe(1), ""
            while frame and frame.f_code.co_name in helpers:
                reason = reason or frame.f_locals.get("reason", "")
                frame = frame.f_back
            where = (
                f"{Path(frame.f_code.co_filename).name}:{frame.f_lineno} {frame.f_code.co_name}"
                if frame
                else "?"
            )
            real_setattr(self, name, value)
            delta = float(getattr(self, field)) - old
            if delta:
                ledger.append({"delta": round(delta, 2), "where": where, "reason": reason})
            return
        real_setattr(self, name, value)

    return patch.object(state_cls, "__setattr__", traced)


def boot(model: str):
    from main import BoneAmanita

    patches = [
        patch("core.LoreManifest.save"),
        patch("protocols.chronos.ChronosKeeper.save_checkpoint"),
        patch("spores.io.LocalFileSporeLoader.save_spore"),
        patch("brain.akashic.TheAkashicRecord.save_to_disk"),
    ]
    from body.models import Biometrics, MitochondrialState

    patches.append(trace_field(MitochondrialState, "atp_pool", ATP_LEDGER))
    patches.append(trace_field(Biometrics, "health", HEALTH_LEDGER))
    for p in patches:
        p.start()
    eng = BoneAmanita(
        {"provider": "ollama", "model": model, "user_name": "T", "boot_mode": "CONVERSATION"}
    )
    llm = eng.cortex.llm
    llm.model = model

    def refuse_to_fabricate(prompt, reason="SIMULATION"):
        raise RuntimeError(
            f"LLMInterface fell back to mock prose ({reason}). A census of prose the model "
            "did not write would describe nothing."
        )

    llm.mock_generation = refuse_to_fabricate
    return eng, patches


def read_prompt(prompt: str) -> dict:
    metrics = METRICS_LINE.search(prompt)
    telemetry = TELEMETRY_P.search(prompt)
    mood = MOOD_LINE.search(prompt)
    return {
        "voltage": float(metrics.group(1)) if metrics else None,
        "exhaustion": float(metrics.group(2)) if metrics else None,
        "p": float(telemetry.group(1)) if telemetry else None,
        "ros": float(telemetry.group(2)) if telemetry else None,
        "mood": mood.group(1).strip() if mood else None,
        "anaerobic_directive": ANAEROBIC_DIRECTIVE in prompt,
        "exhaustion_directive": EXHAUSTION_DIRECTIVE in prompt,
        "engine_depletion_directive": ENGINE_DEPLETION_DIRECTIVE in prompt,
        "somatic_cues": "SOMATIC CUES:" in prompt,
    }


def run(model: str, cache: Path, hold_atp: float = None) -> None:
    eng, patches = boot(model)
    llm = eng.cortex.llm
    calls = []
    real_generate = llm.generate

    def spy(prompt, params):
        asked = copy.deepcopy(params)
        reply = real_generate(prompt, params)
        calls.append({"prompt": prompt, "asked": asked, "sent": dict(params), "reply": reply})
        return reply

    llm.generate = spy
    run_id = time.strftime("%Y%m%d-%H%M%S")
    cache.parent.mkdir(parents=True, exist_ok=True)
    try:
        with cache.open("a", encoding="utf-8") as out:
            for turn, (phase, message) in enumerate(SCRIPT):
                calls.clear()
                ATP_LEDGER.clear()
                HEALTH_LEDGER.clear()
                if hold_atp is not None:
                    # Measurement scaffolding, not a behaviour: keeps the engine
                    # alive so the person model and the directives can be
                    # observed past the point where the economy halts turns.
                    eng.bio.mito.state.atp_pool = hold_atp
                started = time.time()
                snapshot = eng.process_turn(message)
                main = [c for c in calls if "=== PARTNER INPUT ===" in c["prompt"] and message[:40] in c["prompt"]]
                call = main[-1] if main else None
                u = eng.shared_lattice.u
                mito = eng.bio.mito.state
                record = {
                    "run": run_id,
                    "model": model,
                    "hold_atp": hold_atp,
                    "turn": turn,
                    "phase": phase,
                    "message": message,
                    "message_words": len(message.split()),
                    "snapshot_type": snapshot.get("type"),
                    "halt": Prisma.strip(str(snapshot.get("ui", "")))[:400]
                    if snapshot.get("type") != "GEODESIC_FRAME"
                    else None,
                    "model_calls": len(calls),
                    "prompt": read_prompt(call["prompt"]) if call else None,
                    "asked": {k: call["asked"].get(k) for k in ("temperature", "top_p", "max_tokens")} if call else None,
                    "sent": {k: call["sent"].get(k) for k in ("temperature", "top_p", "max_tokens")} if call else None,
                    "reply": call["reply"] if call else None,
                    "person": {"E_u": float(u.E_u), "P_u": float(u.P_u)},
                    # The gates that refuse a turn read these, so a halt can be
                    # sized against them even when no prompt was composed.
                    "gate_inputs": {
                        key: float(safe_get(eng.active_physics, key, 0.0) or 0.0)
                        for key in ("narrative_drag", "chi", "voltage", "kappa", "m_a")
                    },
                    "engine": {
                        "atp": float(mito.atp_pool),
                        "ros": float(mito.ros_buildup),
                        "health": float(eng.health),
                        "stamina": float(eng.stamina),
                    },
                    "atp_ledger": list(ATP_LEDGER),
                    "health_ledger": list(HEALTH_LEDGER),
                    "seconds": round(time.time() - started, 1),
                }
                out.write(json.dumps(record) + "\n")
                out.flush()
                p = record["prompt"] or {}
                print(
                    f"  [{turn:>2}] {phase:<10} E_u={u.E_u:.2f} P_u={u.P_u:5.1f} "
                    f"ATP={mito.atp_pool:5.1f} prompt_E={p.get('exhaustion')} "
                    f"calls={len(calls)} {record['seconds']:>5.1f}s"
                )
    finally:
        llm.generate = real_generate
        eng.orchestrator.shutdown()
        eng.telemetry.shutdown()
        for p in patches:
            p.stop()


def spread(values: list) -> str:
    values = [v for v in values if v is not None]
    if not values:
        return "no values"
    arr = np.array(values, dtype=float)
    return f"min {arr.min():.2f}  mean {arr.mean():.2f}  max {arr.max():.2f}  distinct {len(set(np.round(arr, 2)))}"


def report(records: list, model: str) -> int:
    runs = sorted({r["run"] for r in records if r["model"] == model})
    if not runs:
        print(f"No census for {model}.")
        return 1
    rows = [r for r in records if r["model"] == model and r["run"] == runs[-1]]
    print(f"\n=== SOMATIC CENSUS: {model}, run {runs[-1]}, {len(rows)} turns ===\n")
    if rows[0].get("hold_atp") is not None:
        print(
            f"  ATP HELD at {rows[0]['hold_atp']} before every turn. The engine rows describe "
            "a scaffolded economy, not the real one; the ledger includes the refills.\n"
        )

    missing = [r["turn"] for r in rows if r["prompt"] is None]
    if missing:
        print(f"  NO MAIN PROMPT CAPTURED on turns {missing}; those rows describe no generation.")
        halts = {}
        for r in rows:
            if r.get("halt"):
                halts.setdefault(r["halt"].strip().splitlines()[0][:120], []).append(r["turn"])
        for text, turns in halts.items():
            print(f"    halted on turns {turns}: {text}")
        print()
    rows_p = [r for r in rows if r["prompt"]]

    print("  The person, by phase (after each turn):")
    for phase in dict.fromkeys(r["phase"] for r in rows):
        ph = [r for r in rows if r["phase"] == phase]
        e = np.mean([r["person"]["E_u"] for r in ph])
        pu = np.mean([r["person"]["P_u"] for r in ph])
        words = [measure(r["reply"], True)["words"] for r in ph if r["reply"]]
        print(
            f"    {phase:<11} E_u {e:.2f}   P_u {pu:6.1f}   message words "
            f"{np.mean([r['message_words'] for r in ph]):5.1f}   reply words {np.nanmean(words) if words else float('nan'):5.1f}"
        )

    print("\n  What the prompts carried:")
    print(f"    exhaustion (METRICS)   {spread([r['prompt']['exhaustion'] for r in rows_p])}")
    print(f"    P (telemetry)          {spread([r['prompt']['p'] for r in rows_p])}")
    print(f"    ROS (telemetry)        {spread([r['prompt']['ros'] for r in rows_p])}")
    moods = {}
    for r in rows_p:
        moods[r["prompt"]["mood"]] = moods.get(r["prompt"]["mood"], 0) + 1
    print(f"    mood lines             {moods}")
    for key in ("anaerobic_directive", "exhaustion_directive", "engine_depletion_directive", "somatic_cues"):
        fired = [r["turn"] for r in rows_p if r["prompt"][key]]
        print(f"    {key:<24} {len(fired):>2}/{len(rows_p)}  turns {fired}")

    print("\n  The engine (after each turn):")
    print(f"    ATP                    {spread([r['engine']['atp'] for r in rows])}")
    print(f"    ROS                    {spread([r['engine']['ros'] for r in rows])}")
    print(f"    health                 {spread([r['engine']['health'] for r in rows])}")

    print("\n  Where ATP went (summed over the run, largest movers first):")
    totals = {}
    for r in rows:
        for entry in r.get("atp_ledger", []):
            key = f"{entry['reason'] or '-'} @ {entry['where']}"
            count, total = totals.get(key, (0, 0.0))
            totals[key] = (count + 1, total + entry["delta"])
    for key, (count, total) in sorted(totals.items(), key=lambda kv: -abs(kv[1][1]))[:15]:
        print(f"    {total:>+8.1f}  x{count:<3} {key}")
    drained = [r["turn"] for r in rows if r["engine"]["atp"] <= 0.0]
    if drained:
        print(f"    ATP first reached zero after turn {drained[0]}")

    print("\n  What the refusal gates were reading:")
    for key, gate in (
        ("narrative_drag", "PINKER drag*5"),
        ("chi", "PINKER chi*20, ROS panic"),
        ("voltage", "crucible MELTDOWN over 18"),
        ("kappa", "crucible structure under 0.5"),
        ("m_a", "PINKER m_a*30"),
    ):
        values = [r.get("gate_inputs", {}).get(key) for r in rows]
        print(f"    {key:<16} {spread(values)}   ({gate})")
    pinker = [
        5 * (r.get("gate_inputs", {}).get("narrative_drag") or 0.0)
        + 20 * (r.get("gate_inputs", {}).get("chi") or 0.0)
        + 30 * (r.get("gate_inputs", {}).get("m_a") or 0.0)
        for r in rows
    ]
    print(f"    {'PINKER total':<16} {spread(pinker)}   (gate fires above CORTEX.COUNTERFACTUAL_ROS_GATE)")

    print("\n  Where health went (summed over the run, largest movers first):")
    h_totals = {}
    for r in rows:
        for entry in r.get("health_ledger", []):
            key = f"{entry['reason'] or '-'} @ {entry['where']}"
            count, total = h_totals.get(key, (0, 0.0))
            h_totals[key] = (count + 1, total + entry["delta"])
    for key, (count, total) in sorted(h_totals.items(), key=lambda kv: -abs(kv[1][1]))[:10]:
        print(f"    {total:>+8.1f}  x{count:<3} {key}")

    print("\n  Sampling: asked against sent")
    overwritten = [
        r["turn"] for r in rows_p
        if r["asked"]["temperature"] is not None and r["asked"]["temperature"] != r["sent"]["temperature"]
    ]
    print(f"    temperature overwritten {len(overwritten)}/{len(rows_p)} turns")
    print(f"    temperature asked      {spread([r['asked']['temperature'] for r in rows_p])}")
    print(f"    temperature sent       {spread([r['sent']['temperature'] for r in rows_p])}")
    print(f"    max_tokens sent        {spread([r['sent']['max_tokens'] for r in rows_p])}")
    print(f"    model calls per turn   {spread([r['model_calls'] for r in rows])}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    parser.add_argument("--model", default=None)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument(
        "--hold-atp",
        type=float,
        default=None,
        help="reset ATP to this before every turn, to observe the person model past an economy halt",
    )
    parser.add_argument("--cache", type=Path, default=CACHE)
    args = parser.parse_args()

    from presets import BoneConfig

    model = args.model or BoneConfig.MODEL
    if not args.report_only:
        run(model, args.cache, args.hold_atp)
    records = []
    if args.cache.exists():
        records = [json.loads(line) for line in args.cache.open(encoding="utf-8") if line.strip()]
    return report(records, model)


if __name__ == "__main__":
    raise SystemExit(main())
