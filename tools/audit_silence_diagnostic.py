"""tools/audit_silence_diagnostic.py

One-off diagnostic, not a permanent tool: re-runs the friendship census live
with instrumentation wrapped around every point that can hold a turn to
silence, so a held turn can be told apart from a turn that silently failed.

Answers a specific question Gordon asked after reading the friendship
census: of the five turns BoneAmanita held silence on, was silence the
Stage Manager's actual arbitrated choice, or just the only thing left after
something else (a gate misfire, a mechanism reading stale state) broke?

Wraps, without changing behaviour:
  - TheVillageCouncil._evaluate: which of the ~17 threshold voices fired,
    and on what physics values, before StageManager ever sees them.
  - StageManager.negotiate: the verdict and the gate for every turn, not
    just held ones, so a held turn's tension can be compared to a spoken
    turn's.
  - TheCortex.nominate_toxicity: the MOOG branch resets narrative_drag to
    0.0 as a side effect of firing, which is why the census log's
    "gate_inputs" snapshot (captured after the turn finishes) can never
    show the value that actually crossed the threshold. This captures it
    before the reset.
  - TheGatekeeper._audit_safety: which cursed-list word, if any, matched.
"""

import sys
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from struts import safe_get, dump_state  # noqa: E402
from audit_somatic_census import boot, SCRIPTS  # noqa: E402
import archetypes.council as council_mod  # noqa: E402
import archetypes.stage as stage_mod  # noqa: E402
import brain.cortex as cortex_mod  # noqa: E402
import physics.filters as filters_mod  # noqa: E402

TOPIC = "friendship"
LOG = []


def log(turn, line):
    LOG.append(f"[{turn:>2}] {line}")


CURRENT_TURN = {"n": -1}

_real_evaluate = council_mod.TheVillageCouncil._evaluate
_real_negotiate = stage_mod.StageManager.negotiate
_real_nominate_toxicity = cortex_mod.TheCortex.nominate_toxicity
_real_audit_safety = filters_mod.TheGatekeeper._audit_safety


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


def main() -> int:
    script = SCRIPTS[TOPIC]
    eng, _patches = boot("gemma4:12b")
    with patch.object(council_mod.TheVillageCouncil, "_evaluate", staticmethod(spy_evaluate)), \
         patch.object(stage_mod.StageManager, "negotiate", spy_negotiate), \
         patch.object(cortex_mod.TheCortex, "nominate_toxicity", spy_nominate_toxicity), \
         patch.object(filters_mod.TheGatekeeper, "_audit_safety", spy_audit_safety):
        for turn, (phase, message) in enumerate(script):
            CURRENT_TURN["n"] = turn
            started = time.time()
            snapshot = eng.process_turn(message)
            held = snapshot.get("type") == "SILENCE"
            print(
                f"[{turn:>2}] {phase:<10} {time.time()-started:>5.1f}s "
                f"{'HELD' if held else 'spoke'}  {message[:50]!r}"
            )
    Path("tools/cache/silence_diagnostic.log").write_text("\n".join(LOG) + "\n")
    print("\nFull diagnostic log: tools/cache/silence_diagnostic.log")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
