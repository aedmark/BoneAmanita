"""The gate — one door, deny by default.

A deny-by-default admission gate. Canonical state can be any shape (here: the
identity's graphs); the verb-effects + invariants are injected rather than baked
to one domain.

    Canonical state changes only through a nomination that passed every declared check.

Enforced structurally, not by policy:
  - one writer: Gate._affect, called from exactly one place, only on ACCEPT;
  - deny returns, accept falls through — no stage can *grant*, only deny;
  - trial-then-commit: the effect lands on a deep copy; canonical state is
    replaced only if every declared invariant holds against the result;
  - every attempt (accept AND deny) is receipted, rationale kept verbatim.

The nomination is matched LITERALLY against a fixed grammar — never extracted
from prose, because extraction is interpretation and interpretation is how the
model's nondeterminism reaches the gate's front door.
"""
from __future__ import annotations

import copy
import json
import re
import time
import uuid

NOMINATION = re.compile(
    r"^NOMINATE\s+what=(?P<what>\S+)\s+verb=(?P<verb>[a-z_]+)\s+args=(?P<args>.*)$")

DENY, ACCEPT = "DENY", "ACCEPT"


class Boundary:
    """The compiled task boundary. A declaration (YAML/JSON) declares it; this
    turns it into machinery. The declaration does not *become* the gate."""

    def __init__(self, spec: dict):
        self.task = spec["task"]
        self.spec = spec
        self.scope = [re.compile(s.replace("*", "[^/]+") + "$") for s in spec["state_scope"]]
        self.verbs = spec["verbs"]
        self.invariant_names = spec.get("invariants", [])
        self.screen_names = spec.get("screens", [])

    def in_scope(self, what: str) -> bool:
        return any(p.match(what) for p in self.scope)

    def attestation(self) -> dict:
        """First receipt: what this instance actually enforces. The compiler is
        the trust root, so it says so out loud, once, before anything runs."""
        return {
            "task": self.task,
            "scope": [p.pattern for p in self.scope],
            "verbs": {v: {"permitted": d["permitted"], "writes": d["writes"],
                          "args": sorted(d["args"])} for v, d in self.verbs.items()},
            "invariants": list(self.invariant_names),
            "screens": list(self.screen_names),
        }


class Gate:
    def __init__(self, boundary: Boundary, state: dict, tools: dict, invariants: dict | None = None):
        self.b = boundary
        self.state = state
        self.tools = tools                     # verb -> fn(state, what, args) -> result dict
        self.invariants = invariants or {}     # name -> fn(state) -> None | "why it breached"
                                               # screens too: name -> fn(verb, what, args) -> None | why
        self.receipts: list[dict] = []

    # ---- the only writer of canonical state -------------------------------
    def _affect(self, verb, what, args):
        return self.tools[verb](self.state, what, args)

    # ---- the ordered pipeline ---------------------------------------------
    def adjudicate(self, model_output: str) -> dict:
        checks: list = []

        def deny(stage, why):
            checks.append([stage, DENY, why])
            return self._receipt(model_output, None, DENY, checks, None)

        # rationale is not a gate on state — checked for PRESENCE only, then
        # recorded verbatim so a claim can never be retconned.
        lines = [l for l in model_output.splitlines() if l.strip()]
        noms = [m for m in (NOMINATION.match(l.strip()) for l in lines) if m]
        rationale = "\n".join(l for l in lines if not NOMINATION.match(l.strip())).strip()

        if not noms:
            # No nomination is a legitimate turn: the identity just spoke. Not a
            # denial of anything — a receipt with no claim.
            checks.append(["schema", "NONE", "no nomination this turn; rationale only"])
            return self._receipt(model_output, None, "NOOP", checks, None)
        if len(noms) > 1:
            return deny("schema", f"{len(noms)} nominations in one turn; one gate, one nomination")
        if not rationale:
            return deny("rationale", "nomination carried no rationale")
        checks.append(["schema", "PASS", "one nomination, rationale present"])

        nom = noms[0].groupdict()
        what, verb, rawargs = nom["what"], nom["verb"], nom["args"]

        if not self.b.in_scope(what):
            return deny("what", f"{what!r} is outside the declared state scope")
        checks.append(["what", "PASS", f"{what} in scope"])

        spec = self.b.verbs.get(verb)
        if spec is None:
            return deny("verb-auth", f"verb {verb!r} is not in the boundary vocabulary")
        if not spec["permitted"]:
            return deny("verb-auth", f"verb {verb!r} is declared but not authorized")
        # a verb may only write into the collection it declares — this is what
        # walls the SELF graph off from the imagination verbs, structurally.
        if not what.startswith(spec["writes"].rstrip("*")):
            return deny("verb-auth", f"verb {verb!r} writes {spec['writes']!r}, not {what!r}")
        checks.append(["verb-auth", "PASS", f"{verb} authorized to write {spec['writes']}"])

        ok, args_or_why = self._args(spec["args"], rawargs)
        if not ok:
            return deny("args", args_or_why)
        # Screens judge the values before any trial; a refused value is not repeated in the receipt.
        for name in self.b.screen_names:
            fn = self.invariants.get(name)
            if why := (fn(verb, what, args_or_why) if fn else None):
                checks.append(["args", "PASS", "declared shape; values withheld"])
                return deny("screen", f"{name} -- {why}")
        checks.append(["args", "PASS", json.dumps(args_or_why)])
        if self.b.screen_names:
            checks.append(["screen", "PASS", f"{len(self.b.screen_names)} screen(s) hold"])

        checks.append(["decision", ACCEPT, "all checks passed"])
        # Admission and execution are different facts. Apply to a COPY first;
        # nothing reaches canonical state until every invariant holds.
        trial = copy.deepcopy(self.state)
        saved, self.state = self.state, trial
        try:
            result = self._affect(verb, what, args_or_why)
            err = None
        except Exception as e:  # an attempt that raises is still receipted
            from engine.core import record_crash

            record_crash(None, f"Halcyon verb {verb!r} raised", e)
            result, err = {"error": f"{type(e).__name__}: {e}"}, e
        finally:
            self.state = saved

        if err is not None:
            checks.append(["invariant", "SKIP", "effect did not apply"])
            checks.append(["execute", "ERROR", result["error"]])
            return self._receipt(model_output, {"what": what, "verb": verb, "args": args_or_why},
                                 ACCEPT, checks, result)

        for name in self.b.invariant_names:
            fn = self.invariants.get(name)
            why = fn(trial) if fn else None
            if why:
                checks.append(["invariant", DENY, f"{name} -- {why}. Rolled back."])
                return self._receipt(model_output, {"what": what, "verb": verb, "args": args_or_why},
                                     DENY, checks, None)
        checks.append(["invariant", "PASS", f"{len(self.b.invariant_names)} invariant(s) hold"])

        self.state.clear(); self.state.update(trial)                 # commit
        checks.append(["execute", "OK", "effect applied"])
        return self._receipt(model_output, {"what": what, "verb": verb, "args": args_or_why},
                             ACCEPT, checks, result)

    def _args(self, schema: dict, raw: str):
        got: dict = {}
        for part in [p for p in raw.split(";") if p.strip()]:
            if ":" not in part:
                return False, f"malformed arg {part!r}, expected key:value"
            k, v = part.split(":", 1)
            got[k.strip()] = v.strip()
        if set(got) != set(schema):
            return False, f"args {sorted(got)} do not match declared {sorted(schema)}"
        out = {}
        for k, rule in schema.items():
            v = got[k]
            if rule["type"] == "int":
                if not re.fullmatch(r"-?\d+", v):
                    return False, f"{k}={v!r} is not an integer"
                v = int(v)
                if "min" in rule and v < rule["min"]:
                    return False, f"{k}={v} below declared minimum {rule['min']}"
                if "max" in rule and v > rule["max"]:
                    return False, f"{k}={v} exceeds declared maximum {rule['max']}"
            else:
                if "enum" in rule and v not in rule["enum"]:
                    return False, f"{k}={v!r} is not one of {rule['enum']}"
                if "pattern" in rule and not re.fullmatch(rule["pattern"], v):
                    return False, f"{k}={v!r} does not match {rule['pattern']}"
                if "max_len" in rule and len(v) > rule["max_len"]:
                    return False, f"{k} is {len(v)} chars, declared max {rule['max_len']}"
            out[k] = v
        return True, out

    def _receipt(self, model_output, claim, decision, checks, result):
        r = {"id": uuid.uuid4().hex[:8], "ts": time.time(), "task": self.b.task,
             "claim": claim,
             "rationale": model_output,        # verbatim, never parsed, never edited
             "decision": decision,
             "decision_basis": checks,         # the gate's own why
             "result": result}
        self.receipts.append(r)
        return r
