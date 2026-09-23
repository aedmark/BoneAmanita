# Archived Roadmap Items (September 2026)


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

**September 18 correction:** the original claim that a misleading receipt
requires a deliberate lie was too strong. A transient embedding failure leaves
the backend identity and degraded flag unchanged while serving hash vectors,
so the worker accidentally reports healthy HTTP vectorization. Receipts make
the claimed work inspectable; fault-injection tests must verify that claim.

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


## B4. Make the credits true, **DONE**

`credits.txt` and `docs/CREDITS.MD` have been updated to reflect the new reality: BoneAmanita implements the `CreativeDeterminantEngine` and the `SignBitmap` memory aligner. We no longer claim "lean4 certified algorithms" for PDEs that we aren't even running anymore. We now properly attribute the math we actually use.

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


## D1. One somatic budget per turn (done)

**2026-09-19 status:** the audit found the September 18 caveat was right to
flag. Every threshold in `SomaticBudget.evaluate()` was hardcoded in Python,
against this section's own "Constants live in `BoneConfig`" line below; moved
to `BoneConfig.SOMATIC_BUDGET` (19 keys, mirrored into
`lore/tuning_presets.json`). Separately, `engine_state` never carried
respiration, only `atp_pool`/`ros`, so a costly single turn (ANAEROBIC) that
hadn't yet drained the pool produced no budget effect at all; now wired
through, with its own config-driven, milder tier than full ATP depletion.
`chemistry` is deliberately not folded in: D4 already gives it its own real
channel (temperature/sampling), and it has no natural role in word/sentence
caps, so adding it here would be inventing a mapping the roadmap never
specified. See the
[2026-09-19 handoff](SESSION_HANDOFF.md#d9-d1-d2-census-2026-09-19).

**September 18 status (superseded above):** `body/somatic_budget.py:SomaticBudget`
existed and was consumed by composition and generation controls. Its
thresholds were inline, and the implementation's presence did not establish
every requirement below.

Replace the five paths with one object computed once per turn, before
composition, and read by every consumer: the composer's text, the
generation params, and the validator. The handoff's own lesson applies
directly: two objects modelling the same thing disagree in silence, and
here there are five.

It carries the split's two inputs and keeps them separate, because they
mean different things and C5 suggests conflating them is part of why the
directive fails:

- **The person's state** (`E_u`, `P_u` from the lattice, and whatever
  distress signal D0 shows is reliable). Primary. It sets *how much the reply
  asks of them*: `word_cap`, `sentence_cap`, whether a closing question is
  allowed, and whether to offer to carry part of the load.
- **The engine's state** (ATP, respiration, ROS, chemistry). Secondary. It
  sets *what the engine can afford*: it can lower the caps further but never
  raise them past what the person needs, it sets the `retry_allowance` for
  firewall re-asks, and it sets the `temperature_band` (steadier when
  depleted or when the conversation is turbulent).

Plus `forbid_body_narration`, always on, and a `reason` string naming which
input produced each value. Graded, not gated: caps scale with depth
of depletion instead of flipping at 0.8. Constants live in `BoneConfig`
(A1's rule). The name should come from the project's vocabulary, not from
this document.

**Done when** `cortex.py:229`, the composer's exhaustion line, the
respiration line and the standing metabolism line all read from it, and
`tests/test_physics_to_prompt.py` is extended to pin budget in, text out.
**Met**, 2026-09-19: `cortex.py:229`'s old ad hoc directive is gone,
superseded by the budget; the exhaustion/respiration/standing lines all render
through `somatic_block_text`'s equivalent in `brain/composer.py`; new
`tests/test_somatic_budget.py` and `TestSomaticBudgetReachesThePrompt` in
`test_physics_to_prompt.py` construct budgets directly and pin their exact
text.


## D3. Enforce what does not need the model's cooperation (done)

The Lexical Firewall is the most valuable mechanism in the codebase
because it does not trust the model: it checks and re-asks. The body should
work the same way. Instructions become a preference that makes enforcement
rarely fire; enforcement becomes the guarantee.

- **Sentence cap: trim, do not re-ask.** After validation, cut to the first
  `sentence_cap` sentences at a boundary. Deterministic, free, never costs a
  retry. The cost is that a trimmed reply can lose its last sentence; that
  is what D2's wording is for, and the trim rate is the compliance measure.
- **Body narration and over-demand: re-ask with named feedback,** the
  firewall's existing path. Narrating a body the model does not have, or
  ending on a question to a partner who is flagging, is the same class of
  fault as a banned phrase. A re-ask spends ATP and draws on the engine's
  `retry_allowance`, which is where the engine's state belongs: a depleted
  engine can afford fewer corrections, and says so in its receipt.
- **One measurement, two users.** Move `visible_text`, `split_sentences` and
  `measure` out of `tools/audit_somatic.py` into a runtime module the
  validator imports, and have the audit import it back. What the audit
  measures is then exactly what the engine enforces, and they cannot drift.

**Done when** a depleted turn cannot exceed its sentence cap in what the
user sees, on any model, with a test that travels the real path (not a
hand-built fixture, per the A4 lesson).


## D4. Reconnect the sampling channel (done)

The chemistry-to-sampling map is real code, is tuned, and has not reached
a model since the thermal lock went live in B1. Neither side should simply
win. Proposed composition: the Creative Determinant sets the band (lambda
positive locks it narrow and low; negative opens it), and chemistry sets the
position within the band. `max_tokens` either derives from `word_cap` (about
1.5 tokens per word plus slack, with D3's trim handling a mid-sentence cut)
or stops being described as a somatic channel.

C5 held sampling fixed on purpose, so it could not see this channel. Add
audit arms that vary chemistry with identical prompts.

**Done when** a spied turn shows modulator and sent params agree within the
band, and the audit shows a measurable text difference between chemistry
extremes on a live model. If there is none, remove the claim rather than
the audit.


## D5. The body issues receipts (done)

One somatic receipt per turn, in A3's format: the state it was given, the
budget it produced, the reply's measures, and the outcome (`complied`,
`trimmed`, `re-asked`, `failed`). It shows in `/diag` and joins the roll call
in `tools/audit_receipts.py`. "Complied only by trimming, every turn" is the
somatic equivalent of chronic degraded, and it should be as visible.

This is what makes the fix permanent. C5 was a one-off experiment; a
receipt is the same measurement taken on every real turn, forever.

**Done when** `/diag` after a depleted turn names the budget and the outcome,
and a turn with the somatic layer deliberately disabled shows as silent.


## D6. The rest of the somatic cues (done)

Adrenaline ("speak in fragmented/liminal ways"), cortisol ("act highly
stressed, erratic, or defensive"), paradox, oxytocin ("warmth, connection,
healing") and the chemistry moods are all instructions of the kind C5 found
weak, and none has been measured. Most of them also violate the split as
written: "act highly stressed" asks the model to perform a state.

Each cue gets re-read as a response to the person rather than a mood to
act out (a cortisol spike in the conversation calls for a steadier reply,
not a stressed one), and then needs a **declared observable before it is
measured**. A cue that cannot be re-read that way, or for which no
observable can be named, is flavour by definition, and the documents should
call it that or remove it.

**Done when** every cue in `lore/ux_strings.json` under `somatic_*` and
`bio_*` has a row in the audit with a signed effect and interval, or a
written note saying it is flavour.


## D7. Model selection as a somatic benchmark (done)

The audit is now the most direct test available of the one thing this
engine needs from a model: whether its body changes the prose. Choose the
chat model on that, not on general leaderboards. Criteria, in order:

1. Accommodation (D2b) and compliance under D2's wording: within-cap share,
   lighter replies for a tired partner, body narration and mirroring rates.
2. Firewall reject rate on the control arm. Every reject is a retry and an
   ATP penalty, and D0 showed ATP is what kills the engine.
3. No silent failure modes: reasoning models need the stop-list fix first,
   or `reasoning_effort=none`.
4. Latency at interactive length, and fitting the 16GB card with the
   embedding model also loaded.

A baseline bake-off on the current wording can run now; the decision should
wait for D2, since a model that ignores bad instructions and one that obeys
good ones are different findings.

**Baseline, 2026-09-17** (`tools/audit_somatic.py --compare`; 640 generations
each, current wording, thermal tag stripped). Levels are control means;
effects are arm minus control; parentheses mean the interval crosses zero.

| model | reasoning | s/gen | control words | control reject | anaerobic words/sentence | exhausted: within 3 sentences | both: within 3 |
|---|---|---|---|---|---|---|---|
| gemma4:12b | off | 1.8 | 71 | 5% | -1.34 | **+0.82** (11% to 94%) | +0.78 |
| qwen3.5:9b | off | 3.4 | 110 | 22% | (-0.29) | +0.57 | +0.51 |
| ministral-3:14b | n/a | 3.8 | 123 | 28% | (-0.20) | +0.06 | +0.04 |
| mistral-nemo | n/a | 1.3 | 44 | 24% | (-0.75) | (+0.04) | -0.12 |
| gemma4:e4b | off | 0.6 | 23 | 5% | -0.65 | **-0.23** | -0.34 |

gemma4:12b is the clear leader on this baseline: it obeys the exhaustion
line almost literally, rarely trips the firewall (which D0 shows is what
drains ATP), never uses stage directions, and is fastest of the capable
models. ministral-3:14b writes the longest replies, uses stage directions
(0.55 a reply) and trips the firewall most. qwen3.5:9b obeys by writing
longer sentences, and its body words double under the anaerobic line. The
thinking models were run with reasoning off. Not a decision: D2's rewording
comes first.

**Reasoning on is a poor fit for this prompt, at least on gemma4:12b.** With
the stop-list repair in place it does answer, but at about 35 to 45 seconds a
generation (136 seconds a full engine turn in the census), and on some
messages it never answers at all: it re-checks its draft against the kernel's
style rules ("One more look at 'No negative comparison'") until
prompt plus reasoning fills Ollama's default 4,096-token context, and the reply
comes back empty with `finish_reason: "length"`. Reproduced twice on the same
prompt. If a thinking model is chosen, run it with `reasoning_effort=none`,
which `LLMInterface` has no config for yet, or raise `num_ctx`. The
two-repeat reasoning-on audit settles it: 149 generations before five empty
replies in a row tripped the circuit breaker and the audit stopped, as it
should on an outage. Compliance was unchanged (within three sentences
+0.78 under the exhaustion line, words per sentence -1.31 under anaerobic, both
clear of zero, against +0.82 and -1.34 with reasoning off), but **13% of
generations were empty** (18% on control) and each took **42 seconds**
against 1.8. Reasoning buys nothing measurable here and costs a fifth of the
replies. `--compare` shows it as `gemma4:12b (default)`.

