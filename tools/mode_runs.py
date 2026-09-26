"""Real-model mode runs: 30 paced turns per arm, one JSON row per turn with the full engine state.

    .venv/bin/python tools/mode_runs.py OUT.jsonl [ARM ...]

Arms: CONVERSATION ADVENTURE ADVENTURE_CYCLED TECHNICAL CREATIVE (all five when none are given).
Each arm runs in its own process after `reset.sh`. ADVENTURE_CYCLED repeats ADVENTURE's first
ten messages three times (exact repeats from turn 10). BONE_MODEL and PACE (seconds) override
the model and the pause between turns. Keep OUT under scratch/ (gitignored).
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.getcwd())

MODEL = os.getenv("BONE_MODEL", "gemma4:12b")
PACE = float(os.getenv("PACE", "10"))

MESSAGES = {
    "CONVERSATION": [
        "Hey. Long day. I'm trying to decide whether to take a new job offer.",
        "It pays more but it's a longer commute, about an hour each way.",
        "My current team is great, honestly. That's the hard part.",
        "The new place is a startup. Could be exciting, could fold in a year.",
        "My partner says go for it, but she isn't the one driving.",
        "I think I'm scared of being the new person again.",
        "Last time I switched jobs it took me six months to feel useful.",
        "Money isn't nothing though. We want to buy a house eventually.",
        "What would you want to know if you were me?",
        "I haven't asked if they'd let me work from home some days.",
        "Good point, I could ask that tomorrow.",
        "My manager would probably counter-offer if I told her.",
        "Is it bad to use an offer just to get a raise?",
        "I don't want to burn the relationship with her.",
        "She hired me when nobody else would.",
        "Okay, that makes me feel a bit less guilty about thinking it through.",
        "I also wonder if I'm just bored and calling it ambition.",
        "Fair. I did stop learning much this year.",
        "The startup would have me building the data pipeline from scratch.",
        "That part actually sounds fun.",
        "Commute is the dealbreaker I keep coming back to.",
        "Maybe I could try the drive at rush hour this week and see.",
        "Yeah, better than guessing.",
        "Sorry, I've been talking about myself for ages.",
        "Ha, okay. Thanks for sitting with it.",
        "I think I'll ask about remote days and do the test drive.",
        "Then decide by Friday.",
        "Writing it down now.",
        "I feel lighter about it, weirdly.",
        "Alright, heading to bed. Thanks.",
    ],
    "ADVENTURE": [
        "I wake up. Where am I?",
        "I look around the room carefully.",
        "I check my pockets.",
        "I walk to the door and try the handle.",
        "I step outside and look for a path.",
        "I follow the path toward the sound of water.",
        "I kneel by the stream and look at the stones.",
        "I pick up the smoothest stone.",
        "I cross the stream on the flat rocks.",
        "I climb the hill on the far side.",
        "From the top, what can I see?",
        "I head toward the smoke in the distance.",
        "I approach the camp slowly and call out.",
        "I ask the stranger what this place is called.",
        "I offer to share the stone I found.",
        "I ask if there is a town nearby.",
        "I thank them and walk the road they pointed to.",
        "I stop at the crossroads and read the sign.",
        "I take the left road, toward the mill.",
        "I look inside the mill through a broken window.",
        "I go in and search the floor for anything useful.",
        "I light the lantern I found.",
        "I go down the stairs into the cellar.",
        "I listen for a moment before going further.",
        "I open the chest in the corner.",
        "I read the letter inside the chest.",
        "I put the letter in my coat and head back upstairs.",
        "I leave the mill and follow the river toward town.",
        "I reach the town gate and ask to be let in.",
        "I find an inn and ask for a room for the night.",
    ],
    "TECHNICAL": [
        "Can you help me structure a python module for parsing web server logs?",
        "The logs are nginx combined format. Start with the regex.",
        "How should I handle lines that don't match?",
        "Write a dataclass for a parsed log line.",
        "Now a function that yields parsed lines from a file path.",
        "How do I make it work with gzipped files too?",
        "Add a count of requests per status code.",
        "What's a clean way to find the top ten paths?",
        "How would I test the parser with pytest?",
        "Write two test cases: one valid line, one garbage line.",
        "The timestamp format is like 10/Oct/2026:13:55:36 -0700. Parse it.",
        "Should the parser convert to UTC?",
        "Add bytes sent as an int, with dash meaning zero.",
        "How do I make the CLI take a file argument?",
        "Use argparse, not click.",
        "Add a --top flag for how many paths to show.",
        "What about memory for a 5 GB log file?",
        "Is a generator enough or do I need something else?",
        "How would I add a progress indicator?",
        "Can you review the whole design so far for problems?",
        "Good catch on the user agent quoting. How do I fix the regex?",
        "Now group requests by hour.",
        "What's the simplest way to output that as CSV?",
        "Should I use pandas for any of this?",
        "Agreed, keep it stdlib. How do I type hint the generator?",
        "Add a docstring to the main parse function.",
        "How would I package this so I can pip install it locally?",
        "Write a minimal pyproject.toml for it.",
        "What should the README cover?",
        "Thanks. Summarize the module layout in a few lines.",
    ],
    "CREATIVE": [
        "Write me the opening of a story about a lighthouse keeper.",
        "Make the keeper older, maybe seventy.",
        "What does she see from the window at night?",
        "Give her a cat with a strange name.",
        "Now a storm is coming in from the east.",
        "A boat appears in the storm. Who is on it?",
        "Describe the stranger's coat.",
        "Let the keeper and the stranger argue about the lamp.",
        "Add a memory from when she was a girl.",
        "Write the next morning, after the storm.",
        "The stranger won't say where they came from. Show that.",
        "Give the cat a moment where it decides about the stranger.",
        "Write a short letter the keeper never sends.",
        "Now switch to the stranger's point of view.",
        "What is the stranger afraid of?",
        "A supply boat is due tomorrow. Build some tension around it.",
        "Write the supply boat captain as someone who knew the keeper years ago.",
        "Let the captain notice something off about the stranger.",
        "Write a quiet scene at dinner, the three of them.",
        "Now make the lamp fail at night.",
        "The keeper has to climb the tower in the dark. Write it.",
        "The stranger helps without being asked.",
        "Reveal one true thing about the stranger.",
        "Let the keeper decide whether to believe it.",
        "Write the captain leaving, and what he says at the dock.",
        "Skip ahead a week. What has changed?",
        "Write a paragraph from the cat's point of view, just for fun.",
        "Now bring it toward an ending.",
        "Write the last scene.",
        "Give me a title and a one-line summary.",
    ],
}
MESSAGES["ADVENTURE_CYCLED"] = MESSAGES["ADVENTURE"][:10] * 3
ARMS = ["CONVERSATION", "ADVENTURE", "ADVENTURE_CYCLED", "TECHNICAL", "CREATIVE"]


def scalars(obj):
    d = obj if isinstance(obj, dict) else getattr(obj, "__dict__", None) or {}
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()
            if not k.startswith("_") and isinstance(v, (int, float, str, bool))}


def run(mode_arm, out):
    from engine.constants import Prisma
    from engine.struts import safe_get
    from main import BoneAmanita

    mode = mode_arm.split("_")[0]
    eng = BoneAmanita({"provider": "ollama", "model": MODEL, "user_name": "T", "boot_mode": mode})
    counts = {"warden": 0, "gatekeeper": 0}
    real_log = eng.events.log

    def spy(text, *a, **k):
        t = str(text)
        if "Warden rejected" in t:
            counts["warden"] += 1
        if "Gatekeeper rejected" in t:
            counts["gatekeeper"] += 1
        return real_log(text, *a, **k)

    eng.events.log = spy

    # Per-turn diagnostics: every log line, every ATP adjustment with its reason, and what digestion paid.
    turn_logs, ledger, harvests = [], [], []

    def log_all(text, *a, **k):
        turn_logs.append(Prisma.strip(str(text)))
        return spy(text, *a, **k)

    eng.events.log = log_all
    # Crash detail no longer reaches the event log (it goes to crashes.log), so catch it here.
    crashes = []
    sim = eng.orchestrator.simulator
    real_crash = sim.handle_phase_crash

    def on_crash(ctx, phase_name, error):
        crashes.append(f"{phase_name}: {type(error).__name__}: {error}")
        return real_crash(ctx, phase_name, error)

    sim.handle_phase_crash = on_crash
    mito = eng.bio.mito
    real_adjust = mito.adjust_atp

    def adjust(delta, reason="", *a, **k):
        before = mito.state.atp_pool
        out_ = real_adjust(delta, reason, *a, **k)
        ledger.append([str(reason).strip(), round(float(delta), 2), round(mito.state.atp_pool - before, 2)])
        return out_

    mito.adjust_atp = adjust
    digestive = getattr(getattr(eng, "soma", None), "digestive", None)
    if digestive is not None:
        real_harvest = digestive.harvest

        def harvest(phys, logs, *a, **k):
            res_ = real_harvest(phys, logs, *a, **k)
            harvests.append({"voltage": round(float(safe_get(phys, "voltage", 0.0)), 2),
                             "enzyme": res_[0], "atp": round(float(res_[1]), 2), "hits": res_[2]})
            return res_

        digestive.harvest = harvest
    boot = eng.engage_cold_boot() or {}
    out.write(json.dumps({"mode": mode_arm, "turn": "boot", "type": boot.get("type"), "health": eng.health}) + "\n")
    for i, msg in enumerate(MESSAGES[mode_arm]):
        before = dict(counts)
        turn_logs.clear(); ledger.clear(); harvests.clear(); crashes.clear()
        atp_before = mito.state.atp_pool
        t0 = time.time()
        res = eng.process_turn(msg) or {}
        phys = eng.observer.last_physics_packet
        ui = Prisma.strip(str(res.get("ui", "")))
        row = {
            "mode": mode_arm, "turn": i, "msg": msg, "type": res.get("type"),
            "health": round(eng.health, 1), "atp": round(eng.bio.mito.state.atp_pool, 1),
            "voltage": round(float(phys.voltage), 1) if phys is not None else None,
            "crucible": eng.phys.crucible.active_state,
            "holds": getattr(getattr(eng, "stage_manager", None), "consecutive_holds", None),
            "warden_rejects": counts["warden"] - before["warden"],
            "gatekeeper_rejects": counts["gatekeeper"] - before["gatekeeper"],
            "reply": getattr(eng.cortex, "dialogue_buffer", [""])[-1][-600:] if eng.cortex.dialogue_buffer else "",
            "ui_tail": ui[-400:],
            "jester_in_ui": "FALSE COHESION" in ui,
            "save_failed": "save failed" in ui.lower(),
            "held_write": "/allow" in ui,
            "secs": round(time.time() - t0, 1),
            "endocrine": scalars(eng.bio.endo),
            "mito": scalars(mito.state),
            "physics": scalars(phys.to_dict() if hasattr(phys, "to_dict") else phys),
            "person": scalars(getattr(getattr(eng, "shared_lattice", None), "u", None)),
            "governor": scalars(getattr(eng, "governor", None)),
            "crucible_detail": scalars(eng.phys.crucible),
            "engine": {k: v for k, v in scalars(eng).items() if k in ("malignancy", "sycophancy_streak", "current_time_delta", "last_output_length")},
            "atp_ledger": list(ledger),
            "atp_unledgered": round(mito.state.atp_pool - atp_before - sum(e[2] for e in ledger), 2),
            "harvest": list(harvests),
            "logs": list(turn_logs),
            "phase_crashes": list(crashes),
        }
        out.write(json.dumps(row) + "\n")
        out.flush()
        print(mode_arm, i, row["type"], row["health"], row["atp"], row["voltage"], row["crucible"],
              row["warden_rejects"], *(["PHASE_CRASH"] if row["phase_crashes"] else []), flush=True)
        time.sleep(PACE)
    eng.shutdown()


def run_child(path, arm):
    with open(path, "a", encoding="utf-8") as out:
        try:
            run(arm, out)
        except Exception as e:
            import traceback
            traceback.print_exc()
            out.write(json.dumps({"mode": arm, "turn": "crash", "error": repr(e)}) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--child":
        run_child(sys.argv[2], sys.argv[3])
        sys.exit(0)
    path, arms = sys.argv[1], sys.argv[2:] or ARMS
    unknown = [a for a in arms if a not in MESSAGES]
    if unknown:
        sys.exit(f"unknown arm(s): {', '.join(unknown)}")
    for arm in arms:
        # Every run reads live engine data, and singletons outlive an arm: reset, then a fresh process.
        subprocess.run(["sh", "reset.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        subprocess.run([sys.executable, os.path.abspath(__file__), "--child", path, arm], check=False)
