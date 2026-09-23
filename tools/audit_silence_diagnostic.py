"""tools/audit_silence_diagnostic.py

Diagnostic, not a permanent gate check: re-runs one scripted conversation with
instrumentation around every point that can hold a turn to silence, so a held
turn can be told apart from a turn that silently failed.

    python tools/audit_silence_diagnostic.py --topic lease            # live model
    python tools/audit_silence_diagnostic.py --topic lease --canned   # fixed reply, no GPU
    python tools/audit_silence_diagnostic.py --topic lease --trace-drag

Canned mode reproduces holds that depend only on the input text; holds that
depend on what the model actually said (most of the interesting ones) need the
live run. `--trace-drag` logs every narrative_drag write of 8 or more with the
code line that made it, which is how the BENEDICT|GORDON synergy was found.

Wraps, without changing behaviour:
  - TheVillageCouncil._evaluate: which voice thresholds fired, before
    StageManager sees them.
  - StageManager.negotiate: the verdict and gate for every turn.
  - TheCortex.nominate_toxicity: the MOOG branch resets narrative_drag to 0.0
    as a side effect of firing, so the census log's post-turn "gate_inputs"
    can never show the value that crossed the threshold; this captures it first.
  - SimulationPreflightPhase.run: ROS_PANIC and the keyword gates live inline
    there, so it logs their inputs and every nomination (with magnitude).
  - TheGatekeeper._audit_safety: which cursed-list word, if any, matched.
"""

import argparse
import sys
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.struts import safe_get, dump_state  # noqa: E402
from audit_somatic_census import boot, SCRIPTS, trace_field  # noqa: E402
import archetypes.council as council_mod  # noqa: E402
import archetypes.stage as stage_mod  # noqa: E402
import brain.cortex as cortex_mod  # noqa: E402
import phases.cognitive as cognitive_mod  # noqa: E402
import physics.filters as filters_mod  # noqa: E402

CANNED_REPLY = (
    "That is a lot to hold at once. It sounds like part of you already has a lean, "
    "even if the rest of you is not ready to say it out loud yet."
)
LOG = []


def log(turn, line):
    LOG.append(f"[{turn:>2}] {line}")


CURRENT_TURN = {"n": -1}

_real_evaluate = council_mod.TheVillageCouncil._evaluate
_real_negotiate = stage_mod.StageManager.negotiate
_real_nominate_toxicity = cortex_mod.TheCortex.nominate_toxicity
_real_audit_safety = filters_mod.TheGatekeeper._audit_safety
_real_preflight_run = cognitive_mod.SimulationPreflightPhase.run


def spy_evaluate(p, _bio_state):
    triggers, extra = _real_evaluate(p, _bio_state)
    fired = [key for cond, _color, key in triggers if cond]
    if fired:
        log(CURRENT_TURN["n"], f"voices fired: {fired}")
    return triggers, extra


def spy_negotiate(self, tension, *args, **kwargs):
    verdict = _real_negotiate(self, tension, *args, **kwargs)
    log(
        CURRENT_TURN["n"],
        f"negotiate: voices={tension.voices} magnitude={tension.magnitude} "
        f"-> outcome={verdict.outcome!r} gate={verdict.gate!r} reason={verdict.reason!r}",
    )
    return verdict


def spy_nominate_toxicity(self, ctx):
    phys_state = dump_state(ctx.physics) if ctx.physics else {}
    c_cfg = safe_get(self.cfg, "CORTEX", {})
    f_drag = float(phys_state.get("narrative_drag", 0.0))
    chi_val = float(phys_state.get("chi", phys_state.get("entropy", 0.0)))
    m_a = float(phys_state.get("m_a", 0.0))
    tolerance_mod = float(safe_get(self.cfg, "GATE_TOLERANCE", 1.0))
    if getattr(self, "active_mode", "") in ["CREATIVE", "CATALYST"]:
        tolerance_mod = max(tolerance_mod, 1.5)
    drag_limit = float(safe_get(c_cfg, "DRAG_STRESS_THRESHOLD", 8.0)) * tolerance_mod
    chi_limit = 0.8 * tolerance_mod
    log(
        CURRENT_TURN["n"],
        f"MOOG check (pre-reset): f_drag={f_drag:.3f} (limit {drag_limit:.3f}) "
        f"chi={chi_val:.3f} (limit {chi_limit:.3f}) m_a={m_a:.3f} "
        f"mode={getattr(self, 'active_mode', '?')} "
        f"would_fire={(f_drag > drag_limit or chi_val > chi_limit) and m_a < 0.3}",
    )
    return _real_nominate_toxicity(self, ctx)


def spy_audit_safety(self, words):
    result = _real_audit_safety(self, words)
    if result:
        cursed = safe_get(self.lex, "cursed", []) if hasattr(self, "lex") else []
        hit = [w for w in words if w.lower() in [c.lower() for c in cursed]]
        log(CURRENT_TURN["n"], f"GATEKEEPER cursed-input fired, matched word(s): {hit}")
    return result


def spy_preflight_run(self, ctx):
    """ROS_PANIC and every keyword gate live inline in this phase, so log what
    they read on the way in and every nomination that comes out."""
    phys = ctx.physics
    mito = getattr(getattr(self.eng, "bio", None), "mito", None)
    ros = float(mito.state.ros_buildup) if mito else 0.0
    friction = float(getattr(phys, "narrative_drag", 0.0))
    chaos = float(getattr(phys, "entropy", getattr(phys, "chi", 0.0)))
    voltage = float(getattr(phys, "voltage", 0.0))
    tol = float(safe_get(self.eng.config, "GATE_TOLERANCE", 1.0))
    limit = float(getattr(getattr(self.eng.config, "BIO", object()), "ROS_PANIC_THRESHOLD", 100.0)) * tol
    simulated = ros + friction * chaos * 20.0
    armed = friction > 1.2 or chaos > 0.7 or voltage > 80.0
    log(
        CURRENT_TURN["n"],
        f"PREFLIGHT entry: ros={ros:.1f} friction={friction:.2f} chaos={chaos:.2f} voltage={voltage:.1f} "
        f"| ROS_PANIC armed={armed} simulated_ros={simulated:.1f} limit={limit:.1f} "
        f"would_fire={armed and simulated >= limit}",
    )
    out = _real_preflight_run(self, ctx)
    noms = ", ".join(f"{n.gate}@{n.magnitude:.1f}" for n in ctx.nominations) or "none"
    log(CURRENT_TURN["n"], f"PREFLIGHT nominations: {noms}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    parser.add_argument("--topic", default="friendship", choices=sorted(SCRIPTS))
    parser.add_argument("--model", default="gemma4:12b")
    parser.add_argument("--canned", action="store_true",
                        help="answer every turn with one fixed reply instead of calling the model; "
                             "physics and gates still run, so held turns are explained without GPU time")
    parser.add_argument("--max-turns", type=int, default=None)
    parser.add_argument("--trace-drag", action="store_true",
                        help="log every narrative_drag write of 8 or more, with the code line that made it")
    args = parser.parse_args()
    drag_ledger: list = []

    script = SCRIPTS[args.topic][: args.max_turns]
    eng, _patches = boot(args.model)
    if args.canned:
        eng.cortex.llm.generate = lambda prompt, params: CANNED_REPLY
    if args.trace_drag:
        from physics.models import PhysicsPacket
        trace_field(PhysicsPacket, "narrative_drag", drag_ledger).start()
    with patch.object(council_mod.TheVillageCouncil, "_evaluate", staticmethod(spy_evaluate)), \
         patch.object(stage_mod.StageManager, "negotiate", spy_negotiate), \
         patch.object(cortex_mod.TheCortex, "nominate_toxicity", spy_nominate_toxicity), \
         patch.object(filters_mod.TheGatekeeper, "_audit_safety", spy_audit_safety), \
         patch.object(cognitive_mod.SimulationPreflightPhase, "run", spy_preflight_run):
        for turn, (phase, message) in enumerate(script):
            CURRENT_TURN["n"] = turn
            drag_ledger.clear()
            started = time.time()
            snapshot = eng.process_turn(message)
            for move in drag_ledger:
                if abs(move["delta"]) >= 8.0:
                    log(turn, f"DRAG {move['delta']:+.1f} at {move['where']}")
            kind = snapshot.get("type")
            print(
                f"[{turn:>2}] {phase:<10} {time.time()-started:>5.1f}s "
                f"{kind:<15}  {message[:50]!r}"
            )
    log_path = Path(f"tools/cache/silence_diagnostic_{args.topic}.log")
    log_path.write_text("\n".join(LOG) + "\n")
    print(f"\nFull diagnostic log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
