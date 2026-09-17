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

Eleven times now, a subsystem has been found doing nothing while looking
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
| The CD PDE solve | ordvec indexes built with the wrong constructor; every call raised into a PID fallback | since inception |

None of these produced an error, a log line, or a test failure. They
could not have: **the engine's only output is prose, and prose looks the
same whether the physics ran or returned a default.** A crash is a gift
here; silence is the expensive failure mode. Every one of them was found
by looking, not by anything the engine said.

All eleven are now fixed: the first two in `7e90a74`, the rest in the work
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
| **A3** receipts | **done**: ledger, roll call, 7 subsystems, `/diag`, 20 tests |
| **C2** `wing_id` zones | **done**: tagged, scoped, doorway wired, 14 tests |
| **A5** physics input balance | **done**: all four fixes, scorecard tool |
| **A6** close the guessing gap | **done**: 13% -> 81% resolved, 37 tests |
| **B3** the manifold | **done**: was built and broken; PDE solves, 395 tests |
| **B4** make the credits true | **done**: all three overclaims corrected |
| **A2** retire the silent handlers | **done**: 72 -> 28, pass-only banned, 2 ratchet tests |
| **A4** state-asserting tests | **done**: physics-to-prompt pinned end to end, 20 tests |
| **C3** co-regulation | **done**: found the severed serialization; user model now first-class |
| **C4** Stage Manager and Silence | **done**: Tension is a state, Silence is an outcome, 21 tests |
| **C5** somatic translation | **measured**: anaerobic shortens sentences ~10%; "3 sentences or less" is not obeyed |

Tracks A, B and C are finished. C5's result is a
finding against a claim rather than a repair, and the follow-up it points to
(rewording or relocating the exhaustion directive) is a design decision,
not a listed task.

Suite: **489 passed, 5 skipped**. The five skips are the live-embedding tests
behind `BONE_EMBED_LIVE_TEST=1`, not a missing chat model. Re-run
`tools/audit_receipts.py` after touching any instrumented subsystem, and
`tools/audit_handlers.py` after adding a catch.

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

## A2. Retire the silent handlers, **DONE**

72 silent handlers went to 28, and the unambiguous subset (a handler whose
entire body is `pass` or `continue`) went from 30 to 3, all three named in
an allowlist with a written reason.

Most of the 28 that remain are not silent at all; they report through a
house helper the AST walk cannot recognise (`self._log`,
`self._dream_failed`, `simulator.handle_phase_crash`, an `err` string
carried into a later `raise`). The budget test keeps its number as a
ratchet, and the pass-only ban is the measure that actually means
something.

### What it found

**`TheTinkerer` had no `to_dict` and no `load_state`.** `TheCortex.gather_state`
called `tinkerer.to_dict()` inside a handler catching AttributeError and
substituting `{}`. One missing pair of methods, three dead paths:

- The composer's `_inject_resonances` reads `village.tinkerer.tool_resonance`
  and emits a HARMONIC RESONANCE directive for any tool above level 4. It
  always read `{}`, so that block has never once appeared in a prompt.
- `ChronosKeeper._gather_village_state` filters on `hasattr(comp, "to_dict")`,
  so tool resonance was never saved.
- `_restore_village_state` dispatches on `load_state`, so it was never
  restored.

Nothing raised, nothing logged, and the Tinkerer appeared to work: it
accumulates resonance correctly, it just had no way to tell anyone. This is
number thirteen, and the only one found by deleting a handler rather than
by measuring.

**The async pool was a silent-failure sink with no handler in it at all.**
All four background submissions in `cycle.py` were fire-and-forget.
`ThreadPoolExecutor.submit` captures any exception into the Future and
discards it when nobody calls `.result()`, and nobody did. That is worse
than a bare `except: pass`, because there is no handler for an audit to
find and no line of code to point at. `_submit_background` now attaches a
done-callback that logs the traceback, which is what made it safe to delete
the defensive handlers inside those tasks.

### The three buckets, as applied

1. **Genuinely optional**: `ordvec` and `sentence-transformers`, and nothing
   else. `numpy`, `faiss-cpu`, `requests` and `markdown` are in the install
   line, so guarding them only relocates the failure (`np = None` does not
   make the engine run without numpy; it makes it fail later, somewhere
   confusing). `ordvec` is now probed once, in `core`, and `spores.memory`
   reads `ORDVEC_AVAILABLE` rather than probing again.
2. **Defensive by habit**: the majority, deleted. Two were guarding
   `ImportError` around code containing no import, so they could never have
   fired. One converted a structural fault into in-fiction flavour text
   ("The Parliament doors are sealed"), which is the worst available
   outcome: the bug becomes content. One guarded
   `self.svc.bio.mito.adjust_atp(...)` eight lines above an identical
   unguarded call to the same method.
3. **Load-bearing barriers**: kept, and made to report. The CSF gatekeeper
   still rejects a turn it cannot wash (hostile input should not kill the
   session) but now logs the traceback, so a code fault is no longer
   indistinguishable from a cursed string.

### The deliverable

`tests/test_observability.py` gained two tests beside the existing budget:

- **`test_no_new_pass_only_handlers`**: zero tolerance on a handler whose
  whole body is `pass` or `continue`, with a three-entry allowlist keyed by
  file, each with a written reason a reviewer can disagree with.
- **`test_the_allowlist_has_not_gone_stale`**: an allowlist entry for a file
  that no longer needs one silently re-permits the pattern across that whole
  file. This fails when an entry stops being necessary.

### The original triage

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

## A3. Receipts, **DONE**

The highest-leverage item in this track, because it is what would have
caught every subsystem in the table above.

**It caught two on its first real turn.** Both are recorded under "What it
found" below. Neither was crashing, neither was logged, and neither was
visible in the prose.

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

### As built

`receipts.py` holds `Receipt` and `ReceiptLedger`. It imports no engine
code at all, so any subsystem can report without risking an import cycle;
`main._wire_receipts` installs a sink that forwards each receipt into
`TelemetryService` as a typed event, which is the only place that knows
telemetry exists. `cycle._execute_core_cycle` calls `begin_turn()`, so
every receipt is attributed to the turn that produced it.

`CORE_SUBSYSTEMS` is the roll call: the seven subsystems that have agreed
to report. `tests/test_receipts.py::TestRollCall` parses the tree with
`ast` and fails if the roll call and the actual `issue_receipt` call sites
drift apart in either direction. A name on the list that nothing issues
would read as permanently silent and turn the signal into noise; a
subsystem issuing under a name not on the list would go silent one day
with nothing watching.

`/diag` reports last turn's receipts, then the three ways a subsystem lies
by omission, kept separate because they are different illnesses with the
same symptom:

| | meaning |
|---|---|
| **silent** | expected to report, never did; wired to nothing, or never called |
| **chronic degraded** | ran every time, on a fallback path every time |
| **chronic empty** | ran every time, returned nothing every time |

`tools/audit_receipts.py` drives the instrumented subsystems over a
synthetic utterance and prints the same table without booting the
organism.

### What it found

Two bugs on the first real turn, which is the entire argument for the item.

**1. The Creative Determinant was solving one turn behind the conversation.**
`cycle.py` did not pass `regulate()` the utterance it already had. It
scraped one back out of the cortex dialogue buffer by prefix match. That
buffer is only written from inside the cortex response path, by
`_update_history(user_input, final_output)`, which cannot run until the
model has already replied. So the scrape could never see the current turn:
the PDE anchored its subgraph on the PREVIOUS utterance every turn, and
fell back to PID entirely on the first turn of every session. B3 fixed the
solve; this is the separate question of what it was solving about, and the
answer was "the thing you said before this one". A PID loop and a solved
manifold both return two floats, so nothing anywhere could have said so.
The receipt reporting `memory_core=True, user_text=False` is what surfaced
it. Fixed: the turn's own text is used, with the buffer scrape kept for
system-driven turns, which have no human utterance of their own.

**2. `_sync_ordvec_indices` collapsed four conditions into a bare `False`.**
ordvec missing, no memory core, no vectorizer, and fewer than three
vectorizable nodes all returned the same value, and the only caller ignored
it before dereferencing an index that was therefore still `None`. The first
receipt read `AttributeError: 'NoneType' object has no attribute
'top_m_candidates'`, which looks like a code fault and is usually just an
empty memory. Each case now raises a named `ValueError`, so the receipt
reads `Memory holds 0 vectorizable node(s); the Laplacian needs at least 3`.

A third thing turned up that was not a bug and is worth recording anyway:
`cortex.recall` was silent on a fresh engine because it is correctly gated
behind `is_trained`. Silence could not distinguish that from dead code, so
the gate now issues a receipt saying it declined and why. That is the
pattern to copy: a subsystem that chose not to act should say so, because
the alternative is indistinguishable from a subsystem that could not.

### A note on the test harness

`tests/base.py` and `tests/test_adventure.py` shut telemetry down by
reaching past its public API into `_executor`, which left a service that
reported itself enabled and raised on the next write. Nothing wrote to it
after teardown, so the inconsistency was invisible until the receipt sink
outlived the engine that installed it. Both now call
`TelemetryService.shutdown()`, and both reset the ledger singleton between
tests.

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

## A4. Tests that assert state, not absence of crash, **DONE**

`tests/test_physics_to_prompt.py`, 20 tests. The suite knew `compose()`
returned a string; it did not know that a high contradiction put a paradox
directive in it. That step is the contract of the entire engine, and
everything upstream of it (the lexicon, the physics, the memory, the
Creative Determinant) exists only to produce numbers that reach it.

### What is pinned

| State | Directive |
|---|---|
| `chi` and `contradiction` both over threshold | PARADOX REST |
| `contradiction` over threshold, `chi` under | ORTHOGONAL ATTENTION |
| Both conditions true | PARADOX REST only; they are mutually exclusive |
| ADVENTURE mode | Neither, `system_injection` is blanked outright |
| `exhaustion` over 0.8 | "conclude in 3 sentences or less" |
| `respiration == ANAEROBIC` | "Raw, breathless, efficient prose" |
| ANAEROBIC plus an explicit mood | The body wins; the mood is discarded |
| psi / chi / contradiction / valence | Their own somatic cue, and no other |
| `voltage` over 60 | A different directive block entirely |

Two rules the tests follow, both worth keeping:

**Thresholds come from `BoneConfig`, never hardcoded.** A test pinning 0.6
would go green against a threshold nobody is using any more, which is the
same illness as a subsystem wired to nothing.

**Every positive assertion is paired with a negative one.** A directive
that is always present tells you nothing and would satisfy a test that only
checks for its presence under load.

### Mutation tested, and it caught one of its own

Five deliberate breaks were introduced into `brain/composer.py` to check
the tests were load bearing rather than vacuous: the exhaustion gate turned
off, the paradox `and` turned into an `or`, the somatic threshold
comparison turned into `> 0.0`, the ANAEROBIC string made unmatchable, and
the ADVENTURE suppression removed. All five failed the suite.

The precedence test did NOT fail the first time, and the reason is worth
recording. `mood_override` is an argument of `compose()`, not a key in the
state dict, and the test helper had been passing it into the state where
the composer never looks. The test passed against a deliberately broken
composer because it was asserting on a value that never arrived. Fixed,
and re-checked against the same mutation.

That is the failure this whole document is about, reproduced inside the
test written to prevent it. Mutation testing is the only thing that
distinguishes a test that holds a contract from one that describes it.

### A naming trap, now pinned

`ctx.physics.exhaustion` is assigned in `cycle.py` from `ctx.user_state`.
It is the engine's inference about how tired the PERSON is, not the
engine's own ATP pool, despite sitting in the same metrics line as it and
reading like a property of the machine. The engine's own depletion reaches
the prompt by a different route: `raw_cost > BIO.ANAEROBIC_THRESHOLD` sets
a respiration status that becomes a prose directive, through three modules
with no single place where the whole path is visible.

Both signals are real and both reach the prompt. They just mean different
things, and `TestExhaustionIsTheUsersNotTheEngines` exists so the next
reader does not have to work that out from the variable name.

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

`credits.txt` claimed "mathematically verified Partial Differential
Equations" and `docs/README.MD` claimed "lean4 certified algorithms under
the hood". Both claimed the verification for BoneAmanita. The verified
code is Spence's: `ordvec` is Lean 4 verified and the Creative
Determinant has its own formalisation, but our Python implementation of
the equations carries no proofs of its own. Corrected in **B4**.

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

## B3. The manifold, **which already existed and was broken**

**Correcting this entry.** It previously said the manifold had to be
built, called it the largest single piece of work in the document, and
described building a graph Laplacian from embedding similarity as future
work. That was wrong. `CyberneticGovernor._graph_regulation` in `core.py`
had been doing all of it since before this project was picked back up:

- ordvec selects a subgraph of memory nodes near the current utterance
- the weighted adjacency comes from the memory graph's real edges,
  symmetrised as `W = max(W, W^T)`
- the graph Laplacian is formed as `L = D - W`
- `b` comes from the ordvec similarity scores, scaled by narrative drag
- `_solve_nd_picard` solves the nonlinear elliptic BVP by Picard iteration
- λ₁ is taken as a Rayleigh quotient, `(Phi^T L Phi)/(Phi^T Phi) - b_mean`
- Φ sets the engine's target voltage and target drag, and the sign of λ₁
  selects the macro policy

That is the field theory on the manifold, not an approximation of it.

**It had never run.** `_sync_ordvec_indices` built its indexes as
`ordvec.SignBitmap(fp32_matrix)` and
`ordvec.RankQuantIndex(fp32_matrix, bits=8)`. Both are wrong: ordvec
indexes take a dimension and are then fed vectors, and RankQuant accepts
1, 2 or 4 bits, not 8. Every call raised, `regulate()` caught it and fell
back to a plain PID controller, and the Creative Determinant solve was
dead for the life of the project. The engine was running a PID loop under
the name of a PDE.

Fixed. First real solve, over 23 memory nodes: λ₁ = -0.4196,
b̄ = +0.4276, Picard converged, nontrivial solution, target voltage 20.53,
target drag 1.00, policy CO_REGULATION.

This is the eleventh instance of the pattern in the table at the top, and
the most consequential one: the single most sophisticated piece of
mathematics in the project, silently replaced by a fallback.

### Reconciled with the thermal lock

B1 wired a *scalar* λ₁ (`-beta * (kappa*gamma - lambda*mu)`) into the
sampling temperature, because at the time the graph solve appeared not to
exist. Two eigenvalues therefore coexisted, and the worse one was driving
generation while the better one reached only the post-turn snapshot,
which is assembled after the prompt has already been composed.

Now: the governor's λ₁ is carried onto `ctx.physics.lam1` immediately
after `regulate()`, which is before `run_simulation` runs the cortex, so
the composer sees it. `_attach_principal_eigenvalue` prefers it whenever
a solve has happened and records which one it used in
`cd_lambda_1_source`. Verified end to end: a solve at λ₁ = -0.4196
produced sampling temperature 1.1196.

The scalar remains the honest fallback for a cold first turn, before
there is enough dialogue history for the governor to anchor a subgraph,
and for any turn where Picard declines to converge. It states the right
sign condition over three per-turn scalars; it simply cannot see memory
structure.

### What is genuinely still open here

Not the manifold. What remains is that κ, γ and μ are still per-turn
scalars fed into a field equation, rather than per-node fields over the
graph. `b` varies across nodes (it comes from the similarity scores) but
the care/coherence/contradiction triple does not. Making those genuinely
local is the remaining piece, and it is a much smaller piece than this
entry used to claim.

## B4. Make the credits true, **DONE**

`credits.txt` and `docs/CREDITS.MD` claimed "mathematically verified
Partial Differential Equations"; `docs/README.MD` claimed "lean4 certified
algorithms under the hood" and "real, verified math". None of that was
true as stated: BoneAmanita's own implementation carries no proofs, and
until B3 the PDE was not executing at all.

All three now describe what the code actually does, which turns out to be
the better credit anyway: the graph Laplacian, the Picard solve, the
Rayleigh quotient, and Theorem 3.16 gating both the macro policy and the
model's sampling temperature.

Verification is attributed correctly, and the correct version is stronger
than either the overclaim or my first attempt at fixing it. **`ordvec` is
itself Lean 4 verified**
([ordvec-formalization](https://github.com/Project-Navi/ordvec-formalization),
declared in the package's own metadata), so the candidate selection under
both the subconscious search and the governor's subgraph extraction rests
on machine-checked code. The Creative Determinant has its own
formalisation in
[cd-formalization](https://github.com/Project-Navi/cd-formalization).
What carries no proofs is BoneAmanita's own Python implementation of
those equations.

My first correction said flatly that there was "no Lean verification"
involved, which swung too far the other way: it disclaimed verification
that genuinely is underneath us, just not ours. Each file now says the
overstatement was ours rather than a claim Spence made.

The `navi-SAD` and `navi-fractal` contributions are now credited too;
they were doing work in the engine and were not mentioned at all.

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

## C3. Co-regulation (the actual goal), **DONE**

**Measuring this first turned up the largest single fault in the project.**

`SharedLatticeDriver` infers `E_u`, how tired the person is, on every turn,
and it does it correctly: driven to maximum it reported `E_u = 1.00`. The
prompt composed on that same turn said `Exhaustion=0.20`, which is the
composer's hardcoded fallback.

### The serialization was severed

`PhysicsPacket` routes attribute access through an alias map, so
`packet.exhaustion` resolves into `energy.exhaustion` and writes route back
the same way. `to_dict()` used `asdict()`, which knows nothing about that
routing, so the serialized form carried only the nested shape. Every
consumer downstream reads flat, via `safe_get(phys_ref, "exhaustion", 0.2)`,
and `safe_get` on a dict does exactly one flat `.get`.

**Sixteen measured fields never reached the prompt**: exhaustion,
contradiction, beta_index, psi, chi, entropy, valence, narrative_drag,
scope, depth, connectivity, lq, gamma, sigma, eta, theta, upsilon. A turn
measuring contradiction 1.0 composed a prompt saying `Contradiction=0.40`.
Five of the six numbers in the VSL metrics line were hardcoded defaults.

So every directive pinned in A4 the day before (the paradox gate, the
orthogonal gate, all four somatic cues) had never once fired in a real
conversation. The gates were correct and nothing arrived at them. The A4
tests passed because they hand the composer a flat dict directly and step
straight over the boundary that was broken, which is a real weakness in
how they were written and the reason a suite built to catch exactly this
did not.

Nothing else caught it either, and could not have: attribute access always
worked. Any test touching `packet.exhaustion` passed. Only the serialized
dict was wrong.

### Fixing it woke two things that had never run

**The Moog quarantine.** `brain/cortex.py` gated Gordon's "I am placing
this in the ledger" on `narrative_drag > 1.5`. But drag runs from
DRAG_FLOOR to DRAG_HALT, 0 to 10 as shipped, and measures 1.4 to 8.6 on
ordinary input. With real values arriving it fired on 8 turns out of 10 and
the engine deferred everything. The limit now reads
`CORTEX.DRAG_STRESS_THRESHOLD`, which is not a number invented here:
`body/somatic.py` already used that same constant to mean "drag is
extreme". Moog now fires once in ten turns, on genuine saturation.

**`matter` must not be flattened.** `CognitivePhase` writes every key of
the serialized dict back onto a packet with `setattr(ctx.physics, k, v)`.
Projecting `matter` flat exposed its mutable containers to that round trip,
and a Counter fed through it gains a tuple wrapper on every pass, so the
word tally that drives the entire physics layer degraded into
`Counter({((('play', 1), 1), 1): 1})` and measured nothing. Only the scalar
layers (`energy`, `space`) are projected; the nested shape is preserved in
full, so existing readers are untouched.

### What C3 actually delivers

`tests/test_physics_to_prompt.py` gained ten tests, four of which fail if
the serialization is reverted:

- Every field a composer gate reads survives `to_dict()`.
- The nested shape is preserved alongside the flat one.
- `matter` is explicitly NOT flattened, with the Counter corruption named.
- A measured value reaches the prompt through a real turn, no hand-built
  dict anywhere in the path.
- A tired user shortens the engine; a fresh one does not.

And the user model is now first-class in the three ways this entry asked
for. It persists: `ChronosKeeper` saves and restores it, so an engine that
spent an hour learning you were running low no longer wakes up assuming you
are fresh. It reports: `lattice.infer_and_couple` files a receipt carrying
`E_u`, `P_u`, `phi` and the silence classification. It is visible: `/status`
prints "You: steady / tiring / flagging" with the numbers behind it.

### Better built than this entry claimed

Two things the original text listed as missing already existed. The lattice
has a silence classifier with four kinds (pregnant, exhausted, reverent,
strategic), triggered by a conversational pause over fifteen seconds. And
there is a real ATP transfer: at low user stamina with decent resonance the
engine spends its own energy and says "We'll carry this part. Rest a
moment." Both were live. Neither could be seen, which is the theme.

### Realigning what "tired" means

The inference answered this entry's own spec backwards, and fixing it turned
up three more faults.

**The model was "typing is work".** Every word drained `P_u`, and `E_u` rose
only once `P_u` fell below 30. So writing three searching paragraphs about
something hard was what made the engine read you as exhausted and start
cutting its replies to three sentences, while "ok. sure. fine." restored you
to full. Backwards for an engine whose stated purpose is supporting the
first person.

Now two signals, deliberately separate:

- **`P_u` is effort spent.** Long messages still drain it, because low `P_u`
  is what triggers the engine to offer to carry part of the load. Draining
  it is the supportive path, not a penalty.
- **`E_u` is disengagement**, measured against this person's own recent
  baseline rather than an absolute length, with repetition as the second
  term. Someone who always writes tersely has a style, not a mood; someone
  whose messages went from eighty words to three has withdrawn.

Measured across three input shapes, `E_u` now falls 0.45 to 0.24 on
consistently terse input, falls 0.47 to 0.36 on long searching prose while
`P_u` drains 95 to 81, and rises 0.52 to 0.78 on blunt repetition.

**The ceiling.** `P_u` had none and climbed to 172 from a starting 100.
Every other pool in the engine clamps. It now clamps to a ceiling that moves:
high shared resonance buys headroom, accumulated trauma (`T_u`) spends it,
and a floor fraction stops it collapsing however heavy things get. All of it
is in `BoneConfig.USER` and `lore/tuning_presets.json`.

### Three faults found on the way

**There were two user models.** `SymbiosisManager` built its own
`UserInferredState` and wrote exhaustion into it from a raw character count,
while `SharedLatticeDriver` kept a separate one. Only the lattice's ever
reached the prompt, so every reading Symbiosis made was computed and
discarded, and it wrote `beth`, `phi` and `beta_index` onto the physics
packet from a model nothing else agreed with. `attach_lattice` now shares one
object, and the lattice owns exhaustion.

**The boot sequence was teaching the baseline.** `infer_and_couple` runs on
system turns too, and the boot prompt is hundreds of words. It was learned as
"your normal message", so everything you actually typed measured short
against it and the engine read a fully engaged user as withdrawing from the
first word. Learning is now gated on `is_user_turn`.

**Every message was scoring as a repeat of itself.** `infer_and_couple` is
called twice per turn, from `ObservationPhase.run` and again from
`_execute_core_cycle`. Reading the state twice is harmless; learning from it
twice is not. The second pass drained `P_u` again for the same message and
found the text already in `_recent_texts` from the first pass, so every
utterance scored maximal repetition. Learning is now idempotent per turn,
keyed on the receipt ledger's turn counter.

That last one is worth noting as a pattern: the duplicate call was harmless
for as long as the method only read state, and became a bug the moment it
started learning. A method called from two places should say whether calling
it twice is meant to be free.

### The original entry

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

**Measured, 2026-09-17.** `tools/audit_somatic.py`, 1,280 generations over two
models. Re-run it rather than trusting this table.

Design: four arms composed from one state dict, crossed respiration
(RESPIRING / ANAEROBIC) by exhaustion (0.79 / 0.81, straddling the `> 0.8`
gate so the METRICS line barely moves). The tool diffs the prompts and refuses
to run if any line other than the directive and its metric changed. Thermal tag
stripped, identical sampling, one seed per (message, repeat) across arms, the
model called directly so the validator cannot resample. 20 messages x 8 repeats
x 4 arms per model. Effects are arm minus control, paired within message, 95%
bootstrap CI over messages; an interval crossing zero is reported as no
detectable difference.

| Contrast | mistral-nemo | gemma4:e4b (reasoning off) |
|---|---|---|
| ANAEROBIC, words per sentence | **-0.97** [-1.74, -0.20], -11% | **-0.65** [-0.89, -0.43], -10% |
| ANAEROBIC, total words | -6.5 [-15.6, +1.8], none detectable | -0.1 [-2.3, +2.0], none detectable |
| ANAEROBIC, breath and body words /100w | **+1.31** [+0.56, +2.25], 4.8x | +0.06 [-0.20, +0.32], none detectable |
| EXHAUSTED, share within 3 sentences | +0.07 [-0.00, +0.14], none detectable (38% -> 45%) | **-0.23** [-0.37, -0.09] (60% -> 37%) |
| EXHAUSTED, sentence count | -0.45 [-1.07, +0.12], none detectable | +0.27 [-0.16, +0.68], none detectable |
| EXHAUSTED, validator would reject | **+0.17** [+0.06, +0.29] (19% -> 37%) | +0.02 [-0.03, +0.07], none detectable |
| BOTH, share within 3 sentences | -0.01 [-0.10, +0.08], none detectable | **-0.34** [-0.49, -0.20] (60% -> 26%) |

What that says, in order of how much weight it will bear:

1. **The anaerobic directive does something small and real.** Sentences get
   about 10% shorter in both models, with intervals clear of zero in both.
   Total length does not change: the model chops, it does not compress.
   The four-generation smoke run that pointed the other way (9.2 against 4.1
   words per sentence) was noise, as it said it might be.
2. **The exhaustion directive does not do what it says.** "Conclude your
   thought in 3 sentences or less" produced no detectable drop in sentence
   count in either model. On gemma it **reversed** its own target: replies
   within three sentences fell from 60% to 37%, and to 26% with both
   directives present, because the model answered "be brief" with more,
   shorter sentences. On mistral-nemo it did not shorten anything and nearly
   doubled the replies the Lexical Firewall would reject, mostly negative
   comparisons ("not X, but Y"), which in production means more retries.
   Checked that the gemma reversal is not a splitter artifact: 1-2% of its
   replies contain a line break, and ignoring line breaks gives the same
   shares.
3. **mistral-nemo performs the state instead of writing in it.** Under
   ANAEROBIC it uses nearly five times as many breath and body words
   ("inhales", "lungs", "breathless"), which the kernel prompt forbids
   ("Embody your state in the structure of your words, do not describe it").
   Gemma does not. This is the "licence for atmosphere" reading the smoke run
   suggested, and it is real on one model of two.

Limits, stated so nobody inflates this later. Twelve measures, three
contrasts and two models make 72 intervals, so two or three will clear zero
by chance; weight the effects that replicate across models (item 1) above
the ones that appear on one (items 2 and 3). All text measures are coarse
proxies: sentences are split on punctuation, and the adjective column counts
suffixes. Gemma was run with `reasoning_effort=none` because with reasoning on
it produced no content at all (see "Found on the way"), so its row describes
gemma without thinking. Neither model is large; a frontier model may obey
"3 sentences" outright. The thermal tag was stripped, so this measures the
instructions and not the deployed temperature coupling.

Verdict: the somatic layer is partly decoration. Metabolic state measurably
reaches the prose through respiration, weakly. The exhaustion instruction is
not obeyed as written and should either be reworded (a hard word or sentence
budget stated outside the `[INTERNAL USE ONLY]` block is the obvious first
try, and `audit_somatic.py` will measure it) or stop being described as a
constraint. `README.md` and `credits.txt` now say this.

**Found on the way.** Three failures of this document's usual kind, each
silent:

- **Reasoning models get fabricated replies.** `LLMInterface.generate` sends a
  stop list that includes `Traveler:`. Ollama applies stop sequences to a
  thinking model's reasoning too, gemma quotes `Traveler:` while reasoning,
  generation ends with empty content, and `generate` answers with
  `mock_generation(reason="SILENCE")` without counting a failure. Any thinking
  model on Ollama would be served mock prose indistinguishable from a reply.
  Not fixed here; filed as its own task. The audit makes `mock_generation`
  raise, which is how this surfaced at all.
- **An all-`<think>` reply looks like perfect obedience.** mistral-nemo often
  puts its entire reply inside `<think>`, which the validator strips, leaving
  nothing visible. Scored naively that is zero sentences, i.e. compliance with
  "3 sentences or less". The audit reports empty replies as their own outcome
  and excludes them from every prose measure; there is a test.
- **A resume cache keyed without the model skips the second model.** Every
  model is sent identical prompts, so the first gemma run found mistral's
  replies under the same key and generated nothing. It surfaced only because
  the analysis refused to print a table with no rows.

The original brief, kept for the design rationale, is in `SESSION_HANDOFF.md`
under "Next session: C5". That brief covers
the rig (smoke tested against `mistral-nemo`), the three confounds that make
a naive A/B void, how to measure without adding a POS tagger, and sizing.

One thing worth repeating here. A four-generation smoke run, which is noise
and not a result, pointed the wrong way: the ANAEROBIC arm, told to write
"raw, breathless, efficient prose", averaged 9.2 words per sentence against
the control's 4.1. If that survives a powered run the finding is not "no
effect" but "opposite effect", so the experiment has to be able to detect a
reversal. Report the signed effect, not the magnitude.


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
5. ~~**A3**: receipts~~, **done**. The permanent fix for the failure mode
   that produced this entire document: a subsystem cannot report healthy
   work it did not do. Found two live bugs on its first turn.
6. ~~**C2**: populate `wing_id`~~ **done**. Cheap, compounding.
7. ~~**A2**: retire the silent handlers~~, **done**. 72 to 28, pass-only
   banned outright, and it found the Tinkerer.

**Long term**: each is a project, not a task.

8. **B3**: the real manifold: graph Laplacian from embeddings, κ/γ/μ as
   fields, Φ as a presence field over memory.
9. **B2**: vendor the Navi solver, extract λ₁ properly, cite the Lean
   theorems.
10. ~~**C3**: the user-state model as a first-class object~~, **done**.
    Found the severed serialization on the way in.
11. ~~**C4**: the Stage Manager, Tension, Silence~~, **done**. The ATP and
    telemetry design is settled and written down under C4.
12. ~~**A4**: physics-to-prompt golden-path tests~~, **done**. ~~**C5**, the
    somatic translation measurement~~, **measured**: see C5.
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
