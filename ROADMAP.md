# BoneAmanita Roadmap

Written 2026-09-15, after the embeddings work (`7e90a74`). Companion to
`SESSION_HANDOFF.md`, which describes what *is*; this describes what's
next and why. Every claim here was measured against the running system,
and the measurements are included so a future session can re-run them
rather than trust them.

Three tracks, in dependency order:

- **A. Observability** — make failure visible. Everything else depends on this.
- **B. The Creative Determinant** — make the Navi math load-bearing.
- **C. The Biological Harness** — associative memory and real co-regulation.

## The thesis: all three problems are one problem

Four times now, a subsystem has been found doing nothing while looking
perfectly healthy:

| Subsystem | How it was dead | How long |
|---|---|---|
| Memory coordinates | SHAKE-256 hashes, no semantic signal | since inception |
| `mind_memory.ann` | attribute is `cortex`; `getattr` returned `None` forever | unknown |
| λ₁ thermal lock | `<cd_lambda_1>` parsed by `generate()`, never emitted by anything | unknown |
| 8 config constants | keys absent from all config; every read returns the inline fallback | unknown |
| 25 severity logs | severity passed as `source`; `CRIT` lines route to DEBUG | unknown |

None of these produced an error, a log line, or a test failure. They
could not have: **the engine's only output is prose, and prose looks the
same whether the physics ran or returned a default.** A crash is a gift
here; silence is the expensive failure mode.

This is why "get rid of the paranoid programming" is not a style
preference, it is the precondition for the other two tracks. You cannot
verify that a PDE is steering behaviour inside a system that cannot tell
you whether it ran.

---

# Track A: Observability

## A0. The measurement (re-runnable)

Instrumenting `struts.safe_get` across two real turns, excluding the
mock-generation path:

```
safe_get calls: 554   resolved: 410   fell through to default: 144  (26%)
```

Of the sites that **never once resolved**, nearly all are config
constants that do not exist anywhere in the project:

```
PACEMAKER_BOREDOM_THRESHOLD   absent from lore/*.json and presets.py
MOOD_THRESHOLD                absent
BASE_TOKENS                   absent
MAX_TOKENS                    absent
SELF_CARE_THRESHOLD           absent
LIMINAL_SCAR_RELIEF           absent
LIMINAL_TRAUMA_HEAL           absent
LIMINAL_TRAUMA_AGGRAVATE      absent
LIMINAL_STRESS_THRESH         absent
LLM_FAILURE_THRESHOLD         absent
MAX_HISTORY_LENGTH            absent
GOVERNOR_SHIFT                present in one lore file, not at the queried path
```

Every subsystem reading those has been running on its hardcoded fallback
for its entire life. Anyone tuning `lore/tuning_presets.json` expecting
`MOOD_THRESHOLD` to do something would see no effect, forever, with no
indication why.

Exception handlers, counted by AST across non-test source:

```
152 handlers:  73 silent (no log, no raise)  |  76 logged  |  3 re-raise
                31 of the silent ones are a bare `pass` or `continue`
```

**Six of those silent handlers are in `spores/embeddings.py`, which I
wrote.** "Never raises into the hot path" was the right call for a
network dependency, but it is the same pattern in a new coat, and it
should meet the same bar as everything else below.

## A1. Strict config, checked once at boot

`safe_get` conflates two different operations:

- **Config reads**: the key either exists or the config is wrong. A miss
  is a bug, always.
- **Runtime state reads**: a field may legitimately be absent mid-cycle.

Only the second deserves a default. Split them:

```python
# struts.py
def require_cfg(obj, key, *, where):
    """Config constant. A miss is a bug and must surface at boot."""
    ...raises ConfigError(f"{where}: missing config key {key!r}") on miss
```

Then a **boot-time config manifest**: each module declares the keys it
needs, `BoneGenesis.ignite` validates the whole set once and fails
loudly with the complete list of missing keys rather than one at a time.

This costs nothing at runtime and is *already what `conventions.md`
mandates* — the "`__init__` Bedrock Caching" rule says these must be
read once at init anyway. Strictness at init is free; it is only
expensive in a hot loop, and in a hot loop these values should already
be cached attributes.

**Deliverable**: `require_cfg`, a manifest, the 12 missing keys either
added to config with real values or deleted from the code along with the
dead branches they gate. Decide per key which it is; some of those
subsystems may want tuning, others may be vestigial.

## A1b. The engine cannot currently shout

`EventBus.log`'s signature is `(message, source, level)`. Almost every
call site passes a *source* tag second (`"SYS"`, `"BIO"`, `"CORTEX"`),
which is correct. But **25 call sites pass a severity there instead**,
which lands in `source` and leaves `level="INFO"`, routing the line to
`logger.debug` where nothing displays it:

```
events.log(msg, X) two-arg calls:            177
  ...of which pass a SEVERITY as `source`:    25   -> demoted to DEBUG
        CRIT   15
        WARN    9
        ERROR   1
events.log(msg, source, level) three-arg:      2
```

The daemon's top-level crash handler is one of them
(`cycle.py:427-429`): when a turn dies, the engine formats a full
traceback, tags it `CRIT`, and logs it at DEBUG. **The single most
important error path in the system is muted.**

This is the cheapest high-value fix in the document: correct the 25 call
sites to the three-argument form, then make it un-regressable. Two
options, and the second is better:

1. A lint test rejecting a severity string in the `source` position.
2. Change `EventBus.log` to accept `level=` by keyword only and infer
   severity from a known-tag set, so the mistake becomes impossible
   rather than merely detected.

Do this before A3, because liveness tracking is worth much less if its
warnings land in the same silent channel.

## A2. Retire the silent handlers

Triage all 73 into three buckets:

1. **Genuinely optional** (backend probes, cache warms, the
   `sentence-transformers` import). Keep the catch, but log once at WARN
   with the reason and set a visible degraded flag. Precedent already
   exists: `SemanticEmbedder.degraded` plus the `/status` line.
2. **Defensive-by-habit** (the majority). Delete the handler. Let it
   raise. `conventions.md` already says "Fail loudly. Do not silently
   catch `TypeError` on critical system structures" — the code simply
   does not follow its own rule, by 73 to 3.
3. **Load-bearing crash barriers** (the daemon loop's top-level handler
   at `cycle.py:427`, which keeps one bad turn from killing the session).
   Keep, but they must record the traceback to telemetry, not just a
   one-line message.

**Deliverable**: a test that fails on any new bare `except: pass` in
non-test source, so this does not silently regrow. The AST script used
for the count above is the basis for it.

## A3. Subsystem liveness tracking

The highest-leverage item in this track, because it is what would have
caught all four dead subsystems on day one.

`TelemetryService` already exists and already records events. Add a
per-turn liveness ring: each physics/memory/daemon subsystem stamps
"I fired" when it does real work. Then:

- `/diag` gains a **"never fired this session"** list.
- A boot-time self-test runs one synthetic turn and reports any
  subsystem that did not participate.

A subsystem that never fires is either dead code or a broken wire, and
both are worth knowing. This is cheap, and it converts the engine's
worst property (invisible degradation) into its most useful diagnostic.

## A4. Tests that assert state, not absence of crash

The current suite is good at "does it run" and weak at "did it do the
thing." Every test in `tests/test_embeddings.py::IndexWiring` is the
shape to copy: assert on retrieved content and dimensions, not on the
call returning.

Golden-path assertions worth adding: after a high-contradiction turn,
`beta_index` exceeds its threshold **and** the composed prompt contains
the paradox directive. After a starvation turn, ATP is at floor **and**
the prose-degradation instruction is present. These tie physics to
prompt, which is the actual contract of the whole engine and is
currently untested end to end.

---

# Track B: The Creative Determinant

## B0. Correcting the record

My first assessment said the PDEs were missing. **That was too strong,
and I was wrong about it.** What is actually present and live:

| Component | Location | Status |
|---|---|---|
| `CreativeDeterminantEngine` | `physics/maths.py:68` | **live** |
| `calculate_viability` (b = κγ − λμ) | called `physics/observer.py:191` | **live**, drives ATP/ROS |
| `update_coherence_debt` | `physics/observer.py:188` | **live** |
| `execute_metabolic_tick` | `physics/observer.py:194` | **live** |
| `enforce_saturation_limit` (−cΦᵖ) | called `cycle.py:1002` | **live** |
| `_solve_nd_picard` (nonlinear elliptic solve) | called `core.py:768` | **live** |
| Permutation entropy / Takens volume | `cycle.py:887-890` | **live** |
| `get_principal_eigenvalue` (λ₁) | `physics/models.py:190` | **called only from a test** |
| `<cd_lambda_1>` thermal lock | parsed `brain/composer.py:151` | **nothing ever emits it** |

κ, γ, μ are fed from real conversational quantities (resonance,
coherence index, contradiction), not placeholders. So the metabolic half
of the CD framework is genuinely load-bearing.

What is *not* true is `credits.txt`'s "mathematically verified Partial
Differential Equations" and "lean4 certified algorithms under the hood"
(the latter in `docs/The Hypervisor/README.MD`). There is no Lean
verification in this repo, and the manifold is a single scalar triple
per turn rather than a field. Both claims become defensible after B2–B3.

## B1. Emit λ₁ (do this first, it is nearly free)

`brain/composer.py:148` already implements the coupling:

- λ₁ > 0 → `temperature = 0.0`, `top_p = 0.1`
- λ₁ < 0 → `temperature = min(1.2, 0.7 + |λ₁|)`, `top_p = 0.95`

This is exactly right against Theorem 3.16 (λ₁(−Δ − b; M) < 0 is the
existence condition for nontrivial coherent configurations): when no
coherent configuration exists, collapse to deterministic logic; when one
does, allow generative heat proportional to how strongly it exists.

It has never run. Nothing emits the tag. The fix is to compute
`ctx.physics.get_principal_eigenvalue()` in the cycle and append the tag
in `compose()`. Call it five lines plus a round-trip test.

This single change makes the PDE physically steer token generation,
which is the thing the README has been claiming all along.

## B2. Adopt the real solver

Vendor `Project-Navi/navi-creative-determinant` (Apache 2.0, compatible
with this project's license) under `physics/navi/` with attribution, or
add it as a submodule. It is not on PyPI, so a `requirements.txt` entry
is not available; vendoring also keeps Constitution Article 1 satisfied,
since the control loop stays here.

Two substantive upgrades over the current approximation:

1. **λ₁ properly.** `get_principal_eigenvalue` currently returns
   `(π/L)² − βb`, the analytic first Dirichlet eigenvalue of an interval.
   That is a 1-D box, not the conversation manifold. The real quantity
   is the principal eigenvalue of `(−Δ − b)` on `M`.
2. **The Picard solver already has the right shape.** `core.py:768`
   solves `(L + cI)Φ = (c + a)Φ − b|Φ|Φ`, the discretized nonlinear
   elliptic BVP. It is fed a Laplacian today; feed it the real one (B3)
   and extract λ₁ from it rather than approximating.

Cite theorem numbers in the code next to the implementations, and point
at `Project-Navi/cd-formalization` for the Lean 4 proofs. That is what
makes "verified" an honest word: not that this repo proves anything, but
that it implements something proved elsewhere and says exactly where.

## B3. Build the actual manifold — and why this was impossible before

The CD framework is a field theory on a compact Riemannian manifold. In
BoneAmanita, M should be the conversation's own semantic manifold, with
κ, γ, μ as fields over it rather than three scalars per turn.

**This is the payoff from the embeddings work, and the reason these two
tracks are ordered this way.** Building a graph Laplacian requires a
meaningful notion of distance between memories. Under SHAKE-256 that
distance was noise, so there was no manifold to solve on and no honest
way to build one. With real embeddings there is: nodes are memories,
edge weights come from embedding similarity (`HippocampalCache.get_graph`
already does cosine thresholding at 0.75), and `L` is the resulting
graph Laplacian.

Then κ/γ/μ become per-node fields (care, coherence, contradiction
localized to regions of the conversation), Φ is a presence field over
memory rather than a single voltage, and λ₁ genuinely reports whether
*this* conversation can currently sustain a coherent structure.

That is the version worth the name. It is also the largest single piece
of work in this document — treat B1 as the deliverable that proves the
idea and B3 as the one that earns the claim.

## B4. Make the credits true

Once B1–B3 land, update `credits.txt` and
`docs/The Hypervisor/README.MD` to describe what the code does, with
theorem references. Until then, soften them. Nelson Spence's work
deserves an accurate citation more than a flattering one.

---

# Track C: The Biological Harness

Measured against `docs/The Hypervisor/HYPERVISOR_V7.0.MD`, which is the
design target.

## C1. Connect short-term memory to consolidation

`MycelialNetwork.encode()` (`spores/network.py:268`) appends engrams to
`memory_core.short_term_buffer`. REM consolidation
(`brain/mind.py:427`) reads from `hippocampus.nodes`. **These are two
different objects, and nothing ever writes to the second one.**
`HippocampalCache.encode()` has no production caller at all.

So: short-term memory is never populated, `extract_for_consolidation()`
always returns empty, and the only route into long-term memory is the
`context_queue` path. The "Cortisol-Induced Stress Blindness → Short-Term
Amputation" behaviour in the README is amputating an empty buffer.

Fix: route `encode()` through the hippocampus, or collapse the two
buffers into one. Then REM has something to consolidate, and the
cortisol amputation becomes a real consequence.

## C2. Zones

v7: *"Distinct projects and people live in separate Zones; when the
conversation crosses from one to another, the old Zone goes out of
scope."*

`wing_id` exists throughout `CerebralIndex` and is always `"GLOBAL"`.
The filtering logic in `query_neighborhood` is written and correct; it
has nothing to filter on. Populate `wing_id` from the Cartographer's
current zone at ingestion, and the Doorway Effect gets a real boundary
instead of a metaphorical one.

Cheap, and it makes retrieval noticeably better as memory grows.

## C3. Co-regulation (the actual goal)

This is the least-built part of the vision and the most valuable. v7
specifies behaviour that is currently only partly present:

- Terse input → efficiency mode; long searching prose → presence mode
- Repetitive or blunt input read as **exhaustion**: the system drops its
  own energy to match, stops generating content, holds space
- Chaotic input gets **Presence and structured Silence**, not the system
  quietly stitching the user's logic together for them
- Deep insight → **Connection**, named plainly, generating shared Resonance

Partial foundations exist: `shared_lattice` with `E_u` (user exhaustion),
`archetypes/symbiosis.py`, the co-metabolic mirroring in CONVERSATION
mode. What is missing is an explicit, inspectable **user-state model**
as a first-class object alongside `PhysicsPacket`, with the same
treatment: tracked, logged, and visible in `/status`.

The Village side is in better shape than I first reported: `GORDON`,
`MERCY`, `BENEDICT`, `JESTER` all exist as council lenses in
`lore/council_data.json`, including fusion pairs. The daemons
(Cartographer, Tinkerer, Therapist, Grave Digger) are a separate layer.
What is missing is v7's **Stage Manager** as an explicit arbiter, and
**Tension → Silence** as a real outcome: an unresolved multi-voice
conflict producing a delayed or withheld answer rather than a blend.

Silence is the hardest and most distinctive behaviour in the whole
design. An engine that can genuinely decline to answer until the human
brings more structure is doing something no mainstream assistant does.

## C4. Verify somatic translation actually happens

Gate 3 claims to degrade prose at low ATP (shorter sentences, fewer
adjectives). It is an instruction in the prompt, so whether it *happens*
depends on the model complying. Measure it: run matched prompts at high
and low ATP against a real model and compare mean sentence length and
adjective density. If the effect is not measurable, it is decoration,
and either the instruction needs strengthening or the claim needs
softening. This is a half-day experiment that settles a load-bearing
claim.

---

# Sequencing

**Short term** — in rough priority order. Each is independently
shippable and each makes the next one verifiable.

1. **B1** — emit λ₁. Smallest change, largest symbolic and practical
   payoff: the PDE starts steering generation.
2. **A1b** — fix the 25 muted log calls. Roughly an hour, and it is the
   difference between an engine that reports its own crashes and one
   that does not.
3. **A1** — strict config + boot manifest. Resolves the 12 missing keys
   and stops the whole class of bug.
4. **C1** — connect the hippocampus. Unblocks REM consolidation and
   makes cortisol amputation real.
5. **A3** — subsystem liveness tracking. The permanent fix for the
   failure mode that produced this entire document.
6. **C2** — populate `wing_id`. Cheap, compounding.
7. **A2** — retire the silent handlers, including mine in
   `spores/embeddings.py`, plus the regression lint.

**Long term** — each is a project, not a task.

8. **B3** — the real manifold: graph Laplacian from embeddings, κ/γ/μ as
   fields, Φ as a presence field over memory.
9. **B2** — vendor the Navi solver, extract λ₁ properly, cite the Lean
   theorems.
10. **C3** — the user-state model, the Stage Manager, and Silence as a
   real outcome.
11. **A4 / C4** — physics-to-prompt golden-path tests, and the somatic
    translation measurement.
12. **B4** — rewrite the credits once they are true.

# Things deliberately not on this list

- **Rewriting the physics into "real" physics.** The keyword-driven rule
  engine is a legitimate design and it works. The CD layer is where the
  real math belongs; the lexicon-and-thresholds layer does not need to
  become dimensionally coherent to be useful.
- **Adopting a vector store or an agent framework.** Constitution
  Article 1. The embeddings work stayed at one HTTP POST for this reason
  and the manifold work should too.
- **Renaming the poetic variables.** Constitution Article 2. `ATP`,
  `godel_scars`, `narrative_drag` stay.
- **Shrinking the engine to the composer plus validator.** Raised in the
  original assessment as an option. Given the stated goal is a
  biological harness rather than a prompt tool, the breadth is the
  point; withdrawn as a recommendation.
