# BoneAmanita Roadmap

Written 2026-09-15, after the embeddings work (`7e90a74`). Companion to
`SESSION_HANDOFF.md`, which describes what *is*; this describes what's
next and why. Every claim here was measured against the running system,
and the measurements are included so a future session can re-run them
rather than trust them.

Three tracks, in dependency order:

- **A. Observability**: make failure visible. Everything else depends on this.
- **B. The Creative Determinant**: make the Navi math load-bearing.
- **C. The Biological Harness**: associative memory and real co-regulation.

## The thesis: all three problems are one problem

Ten times now, a subsystem has been found doing nothing while looking
perfectly healthy:

| Subsystem | How it was dead | How long |
|---|---|---|
| Memory coordinates | SHAKE-256 hashes, no semantic signal | since inception |
| `mind_memory.ann` | attribute is `cortex`; `getattr` returned `None` forever | unknown |
| λ₁ thermal lock | `<cd_lambda_1>` parsed by `generate()`, never emitted by anything | unknown |
| 10 config constants | keys absent from all config; every read returns the inline fallback | unknown |
| 25 severity logs | severity passed as `source`; `CRIT` lines route to DEBUG | unknown |
| γ and μ | computed by the observer, absent from `_SYNC_KEYS`, dropped every turn | unknown |
| `GOVERNOR_SHIFT` | read off `BoneConfig`; it lives in the `LoreManifest` | unknown |
| `HippocampalCache` | wired readers, no writer; cache permanently empty | unknown |
| `get_graph()` consumers | all three asked for `.adj`; it returns a plain dict | unknown |
| Edge threshold `0.75` | a hash-vector constant, above every real embedding similarity | since embeddings |

None of these produced an error, a log line, or a test failure. They
could not have: **the engine's only output is prose, and prose looks the
same whether the physics ran or returned a default.** A crash is a gift
here; silence is the expensive failure mode. Every one of them was found
by looking, not by anything the engine said.

All ten are now fixed: the first two in `7e90a74`, the rest in the work
logged under Status below. Three of them were found only because fixing
the one above them removed the cover it was hiding under.

This is why "get rid of the paranoid programming" is not a style
preference, it is the precondition for the other two tracks. You cannot
verify that a PDE is steering behaviour inside a system that cannot tell
you whether it ran.

## Status

| Item | State |
|---|---|
| **B1** emit λ₁ | **done**: thermal lock live, 14 tests |
| **A1b** unmute severity logs | **done**: 25 sites fixed, 0 remain, lint test added |
| **A1** strict config + boot manifest | **done**: 10 keys promoted, audit wired into genesis |
| **C1** hippocampus | **done**: write path, graph contract, amputation, 11 tests |
| **A3** receipts | next |
| **C2** `wing_id` zones | **done**: tagged, scoped, doorway wired, 14 tests |
| **A5** physics input balance | **done**: all four fixes, scorecard tool |
| **A6** close the guessing gap | **done**: 13% -> 81% resolved, 37 tests |

Suite: **331 passed, 2 failed, 2 skipped**. Both failures are the
long-standing environmental ones (no chat model pulled in Ollama; `ordvec`
not installed), unchanged in message from before this work.

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
mandates*, the "`__init__` Bedrock Caching" rule says these must be
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

Do this before A3, because receipts are worth much less if their
warnings land in the same silent channel.

## A2. Retire the silent handlers

Triage all 73 into three buckets:

1. **Genuinely optional** (backend probes, cache warms, the
   `sentence-transformers` import). Keep the catch, but log once at WARN
   with the reason and set a visible degraded flag. Precedent already
   exists: `SemanticEmbedder.degraded` plus the `/status` line.
2. **Defensive-by-habit** (the majority). Delete the handler. Let it
   raise. `conventions.md` already says "Fail loudly. Do not silently
   catch `TypeError` on critical system structures", the code simply
   does not follow its own rule, by 73 to 3.
3. **Load-bearing crash barriers** (the daemon loop's top-level handler
   at `cycle.py:427`, which keeps one bad turn from killing the session).
   Keep, but they must record the traceback to telemetry, not just a
   one-line message.

**Deliverable**: a test that fails on any new bare `except: pass` in
non-test source, so this does not silently regrow. The AST script used
for the count above is the basis for it.

## A3. Receipts

The highest-leverage item in this track, because it is what would have
caught every subsystem in the table above.

### Why not just a liveness flag

The first draft of this item proposed a per-turn liveness ring: each
subsystem stamps "I fired." That catches dead code. It does not catch the
failure this engine actually kept producing, which is a subsystem that
fires enthusiastically and returns garbage. The hash-vector retriever
fired on every turn for the life of the project. A liveness flag would
have shown it green the entire time.

### The contract

Borrowed from a gate/nomination architecture (untrusted proposer,
deterministic gate, canonical state, receipt contract). The part worth
stealing is the receipt: **an effect is not allowed to describe itself.
The thing that performed the work issues a structured record of what it
was given, what it did, and what came back.**

Each memory retrieval, physics phase, and daemon emits a small typed
record:

```python
@dataclass(frozen=True)
class Receipt:
    subsystem: str        # "cortex.query_neighborhood"
    inputs: dict          # what it was actually handed
    effect: str           # what it claims to have done
    result_count: int     # how much came back
    degraded: bool        # ran on a fallback path
    detail: str = ""      # why, when degraded
```

The rule that gives it teeth: **`result_count` and `degraded` are set by
the code that did the work, never by its caller, and never inferred from
whether an exception was raised.**

### What this would have caught

Each of these produced fluent, confident output while the receipt would
have been unwritable without admitting the problem:

| Failure | The receipt it could not have honestly written |
|---|---|
| Hash vectors | `retrieved 3 of 3, degraded=True (no embedding backend)` |
| `mind_memory.ann` is `None` | `retrieved 0, inputs={index: None}` |
| λ₁ never emitted | no receipt from `thermal_lock` on any turn |
| 10 missing config keys | `degraded=True, detail="CORTEX.BASE_TOKENS absent"` |
| γ/μ dropped in `_SYNC_KEYS` | `inputs={gamma: 0.0, mu: 0.0}` on every turn |

The point is not that receipts raise alarms. It is that a subsystem
cannot produce a healthy-looking record of unhealthy work without
someone writing a deliberate lie into the receipt line.

### Scope

- `TelemetryService` already records events and already has the ring
  buffer; receipts are a typed event, not new infrastructure.
- `/diag` reads receipts instead of flags: last turn's receipts, any
  subsystem with no receipt this session, any subsystem whose receipts
  are consistently `degraded` or `result_count == 0`.
- Boot self-test runs one synthetic turn and prints the receipt table.
  A subsystem missing from it is dead; one reporting zeros is wired to
  nothing.

### What it does not do

It records what a subsystem did, not whether that was correct. A receipt
saying `retrieved 3` from a semantically meaningless index is honest and
still useless on its own. Receipts make the engine auditable, not right.
That gap is what A4's state assertions are for.

### Why this is not a provenance system

An earlier draft of this section proposed going further: require every
assertion to carry provenance pointing at a non-model source, and have
the gate reject anything whose provenance does not resolve. That was
wrong as stated, and the reason is worth recording so nobody rebuilds it.

**Declaring a dependency is not enforcing one.** A required pointer field
is a schema constraint. It proves a pointer was supplied, not that the
claim follows from what it points at. Three things have to hold before it
becomes a governance mechanism, and only the third is cheap:

1. **An oracle the gate can run.** Checking that a sentence faithfully
   represents a document is entailment, which needs either another model
   (trust moved, not removed, and now two models can be jointly wrong) or
   a mechanical comparison. Only the mechanical version is a guarantee,
   and it requires the assertion to be re-derivable: the gate recomputes
   the value from the source and accepts the nomination only if they
   match. That reduces the model from author of the fact to pointer at
   the fact, and a wrong pointer is then detectable. It covers extraction,
   arithmetic, lookup and citation. It does not cover judgment,
   synthesis or inference, and no schema makes it.
2. **A source admission boundary the model cannot cross.** If the model
   chose the document, it chose its own evidence and the check is
   circular. Sources must enter through a channel the model cannot
   nominate into, and be hashed at ingest so the verified artifact is
   immutable even when the world moves. External evidence that can drift
   after verification makes the receipt a claim about a page that no
   longer exists.
3. **Serialization across check, verify and commit.** Validating against
   state S0, verifying evidence, then committing into S1 attests to a
   state that no longer holds. Standard fixes apply because this is an
   ordinary TOCTOU problem: carry the state version the nomination was
   computed against and reject on mismatch (compare-and-swap), or
   serialize every nomination through a single writer that re-validates
   at apply time. **Validation at nomination time is an optimization;
   validation at commit time is the guarantee.**

For BoneAmanita specifically, (1) and (2) are mostly out of scope: this
engine's assertions are prose, and prose is not mechanically re-derivable.
What is in scope is (3) and the honest half of (1): a receipt states what
a subsystem was handed and what it returned, both facts the subsystem can
report mechanically about itself. That is a much smaller claim than
"cannot fabricate", and it is one this codebase can actually keep.

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

## B3. Build the actual manifold, and why this was impossible before

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
of work in this document, treat B1 as the deliverable that proves the
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

## C1. Connect short-term memory to consolidation, **DONE**

**The hippocampal cache was a deliberate design request, not an accident
of refactoring.** It is meant to be used.

Restoring it required three fixes, each hidden behind the one before it:

1. **The write path.** `MycelialNetwork.encode()` appended engrams to
   `memory_core.short_term_buffer` and nothing ever wrote to
   `hippocampus.nodes`. Added `_encode_hippocampal`, which mirrors any
   engram above the consolidation threshold into the cache with a real
   embedding. REM consolidation now has something to promote.
2. **The graph contract.** All three `get_graph()` consumers in
   `cycle.py` asked for a `.adj` attribute; the method returns a plain
   `Dict[str, set]`. One guarded on `hasattr(..., "adj")` and skipped,
   one raised `AttributeError` into a bare `return`, one used
   `getattr(graph, "adj", {})`. So the Gödel scar freeze, the
   Maslov-Sneppen rewiring and the WLS fractal check were all dead
   independently of the empty cache. A test
   (`test_terminal_topology_collapse`) had encoded the broken contract in
   its mock, which is why nothing caught it.
3. **The edge threshold.** `0.75` was calibrated for SHAKE-256 vectors,
   where similarity was noise near zero. Measured over 4 topics x 4
   memories with nomic-embed-text: within-topic cosine averages 0.48,
   cross-topic 0.38. `0.75` sat above every meaningful pair, so the graph
   would have stayed empty even with a populated cache. Now
   `SPORES.HIPPOCAMPAL_EDGE_THRESHOLD`, default 0.50 (~33% of true
   topical links at ~3% false), matching the resonance threshold already
   used by `query_neighborhood`.

Also wired: `apply_stress_blindness` had no production caller, so the
Tunnel Vision Protocol never ran. It now fires every turn from
`MetabolismPhase` against live cortisol. Verified: at cortisol 0.9 with
85 cached nodes it sheds 36.

### Retrieval, both paths

`MycelialNetwork.retrieve_semantic` had no production caller either, so
`hippocampus.retrieve_exact` was reachable only through dead code. Both
are now live through `TheCortex._recall`:

- **Exact**: `room_key(clean_words)` looks up whether this turn revisits
  a room already in short-term memory. Write and read derive that key
  through one shared method; if they ever drift the cache is written and
  never hit, which is the same silent failure in a new place.
- **Semantic**: the cortex query, unchanged, still steered by physics
  through `physics_state`.

`retrieve_semantic` returns tagged wrappers of mixed shape
(`hippocampus`, `cortex`, `cortex_radius`); `_recall` unwraps the two
that name a memory and drops the radius, which is fractal geometry rather
than recall. Verified live: revisiting "greenhouse tomatoes" hits the
hippocampus exactly, while "thinking about my grandmother and the things
she saved" hits nothing exactly and ranks the grandmother memory first
semantically.

### The disconnect

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

## C2. Zones, **DONE**

v7: *"Distinct projects and people live in separate Zones; when the
conversation crosses from one to another, the old Zone goes out of
scope."*

Three disconnected pieces, now joined:

1. **Tagging.** `wing_id` was read from `safe_get(physics,
   "scope_boundary", ...)`, and `scope_boundary` is defined nowhere in
   the project, so every memory ever written was tagged `GLOBAL`. Now
   `MycelialNetwork.current_wing()` reads the stabilized zone (the one
   `ZoneInertia` produces, so it does not flap turn to turn), and both
   ingestion paths use it: engrams in `network.py` and REM consolidation
   in `mind.py`, which had `"wing_id": "GLOBAL"` hardcoded.
2. **Scoping.** `query_neighborhood` filters on
   `physics_state["wing_id"]` and nothing ever set it, so the filter was
   inert in both directions. `TheCortex._attach_wing` now flattens it
   onto the physics dict beside `cd_lambda_1`.
3. **The doorway.** `MemoryCore.execute_doorway_flush` had no production
   caller, so crossing a zone never flushed working memory. Now called
   from `NavigationPhase` on the stabilized zone, not the raw one:
   flushing on every per-turn flap would just be amnesia.

**`GLOBAL` is a wildcard on both sides, not a zone name.** A memory
tagged GLOBAL stays reachable from anywhere, and a query from GLOBAL sees
every zone. Without that, switching zoning on would have stranded every
memory written before it, which is a migration cliff rather than a
feature. There is a regression test for exactly this.

Verified: a THE_FORGE query returns THE_FORGE and GLOBAL and not AERIE;
a GLOBAL query returns all three; the doorway does not flush on first
entry and does flush on a real transition.

When this landed, zoning was correct and still nearly inert, because its
input was saturated: 11 of 12 varied inputs classified as AERIE. That was
not a zoning bug, and chasing it produced **A5** below, which fixed the
cause. Zones now distribute across all four.

## A5. Physics input balance, **DONE**

Found while wiring C2. The first finding this week that was not a
disconnected wire: this was connected, running, and doing the wrong
thing, which made it both more serious and harder to see.

`QuantumObserver._tally_categories` resolves each word three ways: the
solvents list, the lexicon, then `lex.taste()`, a phonosemantic fallback
for unknown words. The fallback was deciding the physics.

All four fixes were applied together, because each one alone just moves
the imbalance somewhere else. Measured with
`tools/audit_physics_inputs.py` over a 16-line corpus of ordinary
conversational English:

| | before | after |
|---|---|---|
| resolved by `lore/lexicon.json` | 13.0% | 27.3% |
| decided by the fallback | 67.5% | 9.1% |
| `play` share of fallback verdicts | 69% | 14% |
| DEL saturated at 1.0 | 15 of 16 lines | 0 of 16 |
| DEL mean | 0.994 | 0.025 |
| zones reachable | 2 of 4 | **4 of 4** |
| zone distribution | AERIE 15, FORGE 1 | COURTYARD 5, AERIE 5, MUD 4, FORGE 2 |

### 1. The classifier returned a score where a confidence was expected

`classify_word` returned `round(final_vitality, 2)` as its second value,
so `apart` came back as `("play", 1.2)`. Callers compared that against
0.5 as though it were a probability, which meant anything over threshold
at all read as highly confident. It also returned the FIRST category over
threshold in a fixed order, so a word comfortably over two thresholds was
assigned by ordering rather than by strength of signal.

Now it scores every category by margin above its own threshold,
normalised into [0, 1] (0.0 at threshold, 1.0 at twice threshold), and
returns the strongest. A caller's `>= 0.5` finally means something about
the word rather than about the scale.

### 2. The thresholds were calibrated for the wrong language

`play_vitality` was 0.6. English is vowel-dense, so vitality cleared that
for most words. Swept against zone balance: at 0.6 the fallback claimed
38% of words with a 72% play share; at **0.95** it claims 12% with an 11%
play share and DEL stops saturating. `heavy_density` inherited exactly
the same skew once play was fixed (72% of verdicts), so it moved 0.55 ->
**0.70**; 0.85 removes the heavy verdict entirely, which is too far.

### 3. The lexicon was supplying 13% of its own physics

Two mass keys, **`social` and `void`, had no lexicon category at all**,
so `BET` was structurally zero and `void` never subtracted from
structural mass. Added both, plus growth across every physics-bearing
category (`heavy`, `kinetic`, `constructive`, `abstract`, `liminal`,
`harvest`, `explosive`, `meat`, `thermal`, `cryo`, `photo`, sentiment,
and `crisis_term`, which a new test caught at 7 words).

### 4. DEL could dominate zone selection by scale alone

`DEL` used a `* 3.0` amplifier, the largest of any dimension, so it won
`max()` whenever play mass was non-trivial. Matched to STR/VEL at `2.0`.

`_determine_zone` was also a bare `max()`, which meant the largest-scaled
dimension won regardless of whether it carried signal. It now requires
the leader to beat the runner-up by `ZONE_MARGIN` (0.15) of its own
value, and ranks **only dimensions that name a zone**. COURTYARD becomes
what it should always have been: no dominant character. Previously it was
reachable only from an empty vector, so it never occurred.

### Found along the way

`counts["solvents"]` could never be non-zero. `LexiconStore` deliberately
keeps solvents out of the general category map, so `lex.get("solvents")`
is empty by construction, and the tally was reading that instead of
`LexiconService.SOLVENTS`. The `E` dimension was structurally dead.

### A6. Closing the gap without bloat or dependencies

The 63% left unresolved after A5 was not one problem. Measured, it was
three populations wanting three different answers:

```
                        share of ordinary English
function words                    39.6%
inflections of known words         7.1%
genuinely novel vocabulary        22.1%
```

**Function words are filler, not unknowns.** `the, a, is, at, and, because`.
English has roughly 150 and does not acquire new ones, so enumerating the
closed class is a one-time paste that cannot bloat. `solvents` held 12
entries and now holds 201. This is also what the `E` dimension has always
been for, and E was structurally dead until A5.

One trap worth recording: `_tally_categories` checks solvents FIRST, so a
word that is both filler and semantic loses its category silently. The
first pass made `i`, `me`, `we` (the `meat` mass key), `not`, `never`
(negation), `very`, `really` (intensifiers) and `none`, `without` (the
`void` mass key) into filler and would have killed all of it. **A word
with a semantic category is never a solvent**, and a test enforces it.

**Morphology costs about twenty lines.** `LexiconStore.get_categories_for_word`
falls back to stripping inflectional suffixes and looking up the root, so
`forge` answers for `forging` and `forged`. The file grows in roots, not
forms, and every root added later inherits the same reach. Cached, with
invalidation on `_index_word`, because misses are cached too and a word
learned after a failed lookup would otherwise stay invisible until
restart.

**The remaining 22% resolves by meaning, using the embedder already
running.** `mechanics/resonance.py` builds one centroid per curated
category and assigns unknown words to the nearest, then teaches the
verdict. No new dependency: arithmetic over vectors from
`SemanticEmbedder`. No bloat: categories stay curated and small, the
centroid generalises.

Two details, both measured rather than assumed:

  * **Mean centring is required.** Raw centroids rank correctly and
    separate uselessly: margins averaged 0.03 and bottomed at 0.001
    (`afternoon` beat its runner-up by 0.004). Single-word embeddings
    share a large common component. Subtracting the global mean lifts the
    average margin to 0.109. Same near-tie compression that made the 0.75
    hippocampus threshold wrong.
  * **Gate on margin, not similarity.** After centring, confident cases
    separate cleanly (glacier/cryo 0.471, night/photo 0.332) from
    genuinely ambiguous ones (letter 0.001, laughter 0.003). Absolute
    similarity does not distinguish those. A word between two categories
    stays unresolved, which is correct: `letter` really is poised between
    social and sacred.

**Learned words go to `LexiconStore.teach()`, not `register_word`.** That
machinery already existed and was fully wired (persist, publish
`MYTHOLOGY_UPDATE`, live-update the index) with nothing ever deciding a
category; this supplied the missing decider. `teach` puts them in the
separate `LEARNED_VOCAB` hive, capped at 1000 per category with LRU
eviction. `register_word` writes `lore/lexicon.json` directly, which
would make machine guesses indistinguishable from hand curation. Deleting
`saves/cortex_hive.json` reverts everything the engine ever learned.

### Result

| | before A5 | after A6 |
|---|---|---|
| curated lexicon | 13.0% | 34.4% |
| solvents (filler) | 0% | 39.6% |
| resonance | 0% | 7.1% |
| **resolved without guessing** | **13.0%** | **81.2%** |
| phonosemantic guess | 67.5% | 2.6% |
| unresolved | 19.5% | 16.2% |

The phonosemantic classifier survives as the offline fallback: steps 1
and 2 need no server at all, so the degraded path improved too.

16% still unresolved is the honest remainder, and it should stay
unresolved rather than be guessed at. `tools/audit_physics_inputs.py` is
the scorecard.

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

## C4. The Stage Manager and Silence

Promoted out of C3 to its own goal, because it is the piece that makes
the Village a system rather than a cast list.

v7 specifies it precisely: *"The Stage Manager keeps the four in
balance. When more than one is triggered at once, it's labeled as
**Tension**, and the Stage Manager negotiates it before anyone speaks.
**Unresolved Tension** becomes **Silence**: a delayed, considered
answer, or no answer until you bring more structure or energy. The Stage
Manager can also pair voices for a moment that needs both."*

What exists today: `archetypes/council.py` (`CouncilChamber`) runs
debates, and `lore/council_data.json` already defines fusion pairs
(`GORDON|MERCY`, `BENEDICT|GIDEON`, `JESTER|REVENANT`) with their own
names and log lines. Voice pairing is therefore half-built already.

What is missing is the arbiter itself and, more importantly, its most
distinctive outcome:

- **Tension as a first-class state.** Multiple voices triggered at once
  should be detectable and nameable, not blended into one response.
- **Silence as a real output.** Unresolved Tension must be able to
  produce a delayed answer, or no answer, rather than always producing
  prose. This is the hardest behaviour in the design and the one with no
  mainstream equivalent: an engine that can genuinely decline to speak
  until the human brings more structure or more energy.
- **Pairing as a deliberate choice** rather than a lookup that happens
  to hit.

Design note: Silence interacts with the ATP economy in a way worth
deciding rather than guessing. Declining to answer must not read as a
failure, and it must be distinguishable in telemetry from the engine
simply erroring out. Worth an explicit decision before implementation.

## C5. Verify somatic translation actually happens

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

**Short term**: in rough priority order. Each is independently
shippable and each makes the next one verifiable.

1. **B1**: emit λ₁. Smallest change, largest symbolic and practical
   payoff: the PDE starts steering generation.
2. **A1b**: fix the 25 muted log calls. Roughly an hour, and it is the
   difference between an engine that reports its own crashes and one
   that does not.
3. **A1**: strict config + boot manifest. Resolves the 12 missing keys
   and stops the whole class of bug.
4. ~~**C1**: connect the hippocampus~~, **done**. Explicitly requested;
   REM consolidation and cortisol amputation both work now.
5. **A3**: receipts. The permanent fix for the failure mode that
   produced this entire document: a subsystem cannot report healthy work
   it did not do.
6. ~~**C2**: populate `wing_id`~~ **done**. Cheap, compounding.
7. **A2**: retire the silent handlers, including mine in
   `spores/embeddings.py`, plus the regression lint.

**Long term**: each is a project, not a task.

8. **B3**: the real manifold: graph Laplacian from embeddings, κ/γ/μ as
   fields, Φ as a presence field over memory.
9. **B2**: vendor the Navi solver, extract λ₁ properly, cite the Lean
   theorems.
10. **C3**: the user-state model as a first-class object beside
    `PhysicsPacket`.
11. **C4**: the Stage Manager, Tension as a named state, and Silence as
    a real outcome. Settle the ATP/telemetry design before building.
12. **A4 / C5**: physics-to-prompt golden-path tests, and the somatic
    translation measurement.
13. **B4**: rewrite the credits once they are true.

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
