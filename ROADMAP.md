# BoneAmanita Roadmap

Written 2026-09-15, after the embeddings work (`7e90a74`). Companion to
`SESSION_HANDOFF.md`, which describes what *is*; this describes what's
next and why. This is a cumulative record of measurements, decisions, and
implementation plans; older present-tense descriptions can be superseded.
The September 18 status below and the latest `SESSION_HANDOFF.md` entry take
precedence. Recorded experiments should be rerun before treating their results
as evidence for a newer implementation.

Four tracks, in dependency order:

- **A. Observability**: make failure visible. Everything else depends on this.
- **B. The Creative Determinant**: make the Navi math load-bearing.
- **C. The Biological Harness**: associative memory and real co-regulation.
- **D. The Somatic Contract**: the person's state shapes the reply, the
  engine's state sets what it can afford, and neither is performed. Added
  after C5 found the somatic layer mostly decorative.

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

## Status — reconciled 2026-09-20 (latest)

**The DSPy critic could mutate the kernel mid-crisis; gated off in
CONVERSATION mode, 2026-09-20:** reviewing the friendship census's five
silences (Gordon: "was silence the correct choice, or the only choice
because something silently failed?") found two already-known bugs
(confirmed fixed), one genuine `TENSION_MAGNITUDE` arbitration (four
voices, no fusion), and two `MOOG` holds whose real trigger - instrumented
live before `MOOG`'s own reset erases the evidence - was `narrative_drag`
at 55-56 against a limit of 12.8. Traced further: `DSPyCritic.evolve_prompt`
(`mechanics/dspycritic.py`), triggered purely by Lexical Firewall
rejections with zero awareness of mode or the person's state, had
permanently injected an axiom forbidding the model from soothing or
reassuring - right as the conversation moved into its most vulnerable
turns - and confirmed that axiom does reach every subsequent prompt via
`GLOBAL_BASELINE.EVOLVED_AXIOMS`. Gated off in CONVERSATION mode via a new
config key. First attempt did nothing (verified live, made it worse:
`narrative_drag` peaked at 999): the gate read `self.eng.cortex.active_mode`
from inside `DreamEngine`, but `self.eng` there isn't the object that holds
`.cortex` at all, so the check silently always saw `""`. Real fix threads
`active_mode` in as a parameter from each of the five real call sites
instead. Re-confirmed live: 29/30 turns generated (previously 26-28),
`narrative_drag` max 6.42, `PINKER` total max 41.47 (was 5015.62). Full
suite: 584 passed, 5 skipped, 138 subtests. See the
[2026-09-20 handoff](SESSION_HANDOFF.md#dspy-critic-conversation-gate-2026-09-20).

**A blind BoneAmanita-vs-vanilla comparison, and Ollama's silent 4096-token
context default, 2026-09-19:** Gordon asked for a vanilla baseline (same
script, same model, zero system prompt) and a genuinely blind comparison
(independent judge model plus his own blind read) against the friendship
census. Two length-cap fixes (`max_tokens` 450, then 2000) were both correctly
rejected as arbitrary; the real bug surfaced only once the cap was dropped
entirely - vanilla's unprompted replies (500-700+ words) fill Ollama's silent
4096-token context default within a handful of turns, the same defect this
file's D7/open-items already named on the reasoning-model side, just never
seen here before because nothing had asked for this much unbudgeted output.
Fixed by moving `tools/audit_somatic_vanilla.py` off the OpenAI-compatible
shim (which silently ignores `options.num_ctx`) onto Ollama's native
`/api/chat` endpoint with `num_ctx: 32768`; confirmed live both that the shim
really does ignore the option and that the native endpoint honors it.
BoneAmanita's own side needed no change - its replies stay well under 4096
tokens on their own. Corrected blind-judge result: **BoneAmanita 22, Vanilla
3** (an earlier 23-2 figure, run against the truncated data and a separate
key-presence bug in the judge script itself, should not be cited). See the
[2026-09-19 vanilla-comparison handoff](SESSION_HANDOFF.md#vanilla-blind-comparison-2026-09-19).

**A third census, advice-restraint, and a cursed-word false positive,
2026-09-19:** a third scripted conversation (`--topic friendship`,
deliberately no physical project or parent theme this time, so more of its
early turns are venting rather than requests) verified a new kernel line
("HOLD OFF ON ADVICE" - do not default to solving a problem the moment it is
mentioned) against real generations: clear improvement in the
tiring/flagging/distressed/recovering phases, partial in the early engaged
phase. The run also caught a real bug live: `TheGatekeeper._audit_safety`
(`physics/filters.py`) rejected two completely ordinary distressed messages
as `CURSED_INPUT` because both used the word "feel," which was on
`lore/lexicon.json`'s `"cursed"` list alongside "human" - a list meant to
catch meta-awareness talk, catching ordinary emotional language instead, at
exactly the moments (mid-crisis, carrying guilt) this session's whole
direction exists to answer rather than refuse. Both words removed; regression
added (`tests/test_gates.py`); confirmed live that the same two messages now
reach a real answer. The mechanism itself (checking the *person's* words for
AI-meta-awareness language, rather than the *model's* output) is flagged as
worth a further look, not redesigned here. See the
[2026-09-19 handoff](SESSION_HANDOFF.md#advice-restraint-cursed-word-bug-2026-09-19).
Full suite: 581 passed, 5 skipped, 138 subtests, holding green.

**Firewall widening, tone fix, and a live-killing topology bug, 2026-09-19:**
reading the sailboat census transcript directly (not just its summary
numbers) found antithesis slipping past `NEGATIVE_COMPARISON` when split
across a sentence or semicolon (widened, verified against the failing text),
and flagging/distressed replies narrating the person's situation from
outside it rather than answering them (kernel gained "RESPOND, DO NOT
NARRATE"; live re-run shows a real, visible shift toward first-person
presence). Verifying both on a second, unrelated scripted conversation
(`--topic marathon`) found the engine dying at turn 10 of 30: today's
`calculate_clustering` fix had activated a terminal-shutdown check that had
never once run in production, and its comparison logic was broken in two
ways only a working implementation could expose (a zero-vs-zero false
positive, then single-sample null-model noise). Fixed with the same
discipline `GATE.MIN_CORPUS` and the embedding fallback's consecutive-failure
count already use elsewhere in this codebase: a real minimum graph size, an
averaged multi-draw null baseline, a noise floor, and three consecutive
confirmations before the irreversible action. Marathon census re-run clean:
28/30 generated, flagging 6/6. See the
[2026-09-19 firewall/topology handoff](SESSION_HANDOFF.md#firewall-topology-second-census-2026-09-19).
Full suite: 574 passed, 5 skipped, 29 subtests, throughout.

**D9/D1/D2/D2b audit and census, 2026-09-19 (earlier):** auditing D1/D2/D9 against their
own written acceptance criteria (this section's own instruction below) found
each partly complete, not just unmeasured. D9 had four refusal paths in
`SimulationPreflightPhase` still bypassing the Stage Manager entirely,
untested; fixed, and confirmed live. D1's `SomaticBudget` thresholds were
hardcoded in Python against its own "constants live in `BoneConfig`" rule, and
its `engine_state` never carried respiration, a different signal than the ATP
pool's level; both fixed. D2's audit tool (`tools/audit_somatic.py`) was
measuring a mechanism D2 had already retired, plus three unrelated breakages
that meant it could not run at all; rebuilt around real `SomaticBudget`
objects. D2b's accommodation measures and its third ("disengaged") persona
arm did not exist; built. See the
[D9/D1/D2/D2b handoff](SESSION_HANDOFF.md#d9-d1-d2-census-2026-09-19) for the
full account of each, including the specific bugs found.

With those fixes in place, the live 30-turn census
(`tools/audit_somatic_census.py --model gemma4:12b`) that D0b and D9 were both
waiting on finally ran: **27 of 30 turns generated a reply, flagging phase 6
of 6**, every halt carries an identical Stage Manager reason with a matching
ATP ledger entry, and no independent gate fired on its own. D0b and D9 are now
measured, not just plausible. D2 and D2b's own statistical passes (the
two-model comparisons their "done when" sections ask for) are unblocked by the
tool rebuild but not yet run.

The complete suite after all of the above (except the census tool's own fix,
which has no test coverage and was instead verified by the census run itself
completing cleanly) returned **559 passed, 5 skipped, 29 subtests passed**,
about 6 minutes 43 seconds. Also fixed in passing: `DSPyCritic` read the same
`MODEL` config key as the answering model, so a filter with no need of it rode
along on whatever D7 tuned for compliance (`gemma4:12b`). New
`BoneConfig.DSPY_MODEL` (`gemma4:e4b`) decouples them; full-suite wall clock
dropped from about 14 minutes to about 7.

**Refusal-test follow-up, 2026-09-18:** all seven known failures pass in the
focused run (54 passed, 4 subtests passed). Concrete physics fixtures now reach
the production serialization path, and refusal tests cover nomination followed
by Stage Manager arbitration, including reason, receipt, scar, and one ATP
charge. Production gate thresholds and routing are unchanged. See the
[refusal-test handoff](SESSION_HANDOFF.md#refusal-tests-2026-09-18).
The complete suite on the latest tree plus the refusal routing unification returned
**525 passed, 5 skipped, 29 subtests passed**. All existing unit tests pass
cleanly. This is the new full-suite baseline.

**Atomic quicksave follow-up, 2026-09-18:** R2 is repaired. Quicksave now writes
and syncs a same-directory temporary file before atomic replacement. Failure
regressions verify preservation of the previous checkpoint and cleanup of
unpublished temporary files. The next priority is the seven refusal-test
failures. See the [quicksave handoff](SESSION_HANDOFF.md#quicksave-repair-2026-09-18).
The complete suite on `8069778` plus the embedding and quicksave repairs returned
**518 passed, 7 failed, 5 skipped, 29 subtests passed**. All five new quicksave
tests passed; the seven failures are unchanged. This is the current full-suite
baseline.

**Embedding follow-up, 2026-09-18:** R1/R1b are repaired. Transient hash vectors
are uncached, fallback receipts identify their actual source, recovery retries
failed texts, and runtime degradation preserves the startup vector width.
The terminal hash transition clears the semantic cache. Downstream stores are
not automatically re-embedded; hash operation remains non-semantic. See the
[embedding handoff](SESSION_HANDOFF.md#embedding-repair-2026-09-18).
The complete suite on `8069778` plus the embedding repair returned **513 passed,
7 failed, 5 skipped, 27 subtests passed**. The seven failures are unchanged;
all five new embedding regressions passed. The quicksave run above supersedes
this baseline.

**Shutdown follow-up, 2026-09-18:** R3 is repaired. The cycle daemon and workers
finish before persistence and telemetry teardown, and test fixtures clean up
engines even after a subclass setup failure. A complete suite on `8bdd960`
plus this repair returned **508 passed, 7 failed, 5 skipped, 22 subtests passed**.
All four new shutdown regressions passed; the seven failures are the same
ones reproduced before the repair. Embedding fallback and quicksave defects
were still open at that point; both are repaired in the follow-ups above. See the [latest handoff](SESSION_HANDOFF.md#stabilization-2026-09-18).
This follow-up supersedes the review baseline below.

The review covered `b0a096e` plus existing working-tree changes. No repairs were
made in that review or the documentation reconciliation. The implementation
milestones below do not imply a currently green suite or validated live behavior;
test counts attached to older milestones describe those earlier checks.

| Item | State |
|---|---|
| **B1** sampling gate | **replaced**: bitmap regime signal proposes `<thermal_gate>` temperature; the model interface clamps it to its temperature band |
| **A1b** unmute severity logs | **done**: 25 sites fixed, 0 remain, lint test added |
| **A1** strict config + boot manifest | **done**: 10 keys promoted, audit wired into genesis |
| **C1** hippocampus | **done**: write path, graph contract, amputation, 11 tests |
| **A3** receipts | **implemented, embedding receipt defect repaired**: nine registered subsystem names and `/diag`; fallback provenance now has failure/recovery regression coverage |
| **C2** `wing_id` zones | **done**: tagged, scoped, doorway wired, 14 tests |
| **A5** physics input balance | **done**: all four fixes, scorecard tool |
| **A6** close the guessing gap | **done**: 13% -> 81% resolved, 37 tests |
| **B3** governor validation | **PDE removed**: bitmap gate is current; previous green-suite claims are superseded by the September 18 failures |
| **B4** make the credits true | **done**: all three overclaims corrected |
| **A2** retire the silent handlers | **done**: 72 -> 28, pass-only banned, 2 ratchet tests |
| **A4** state-asserting tests | **done**: physics-to-prompt pinned end to end, 20 tests |
| **C3** co-regulation | **done**: found the severed serialization; user model now first-class |
| **C4** Stage Manager and Silence | **done**: Tension is a state, Silence is an outcome, 21 tests |
| **C5** somatic translation | **measured**: anaerobic shortens sentences ~10%; "3 sentences or less" is not obeyed |
| **D** the somatic contract | **D0/D0b/D1/D9 measured live**: D0's ATP result stands; D0b's tolerances and D9's nomination routing are confirmed by a 30-turn census (27/30 generated, flagging 6/6, every halt carries a Stage Manager reason). D1's budget is complete and config-driven. D2's wording and D2b's measures are implemented and tool-verified; their own two-model statistical passes are unblocked but not yet run |

Next round: checkpoint, embedding fallback, shutdown, the seven failing
regressions, and the D1/D2/D9 audit have all been repaired and, where
applicable, measured live, as recorded above. Remaining: D2's and D2b's own
statistical passes (two models, real generation counts), and the
`MycelialNetwork.calculate_clustering` AttributeError found during the census
(see the 2026-09-19 handoff entry). The D0 census recorded ATP between
16 and 53 over 30 turns after the earlier six-turn starvation defect was
addressed. That historical energy result does not validate the current refusal
behavior; D0b's post-tolerance census was interrupted before its first turn.

**Earlier review baseline: seven confirmed failing tests.** The corrected follow-up
selection returned **129 passed, 7 failed, 4 skipped**; this is not a full-suite
total. The initial broad run stopped at its failure cap and included four
temporary-checkout Git-metadata failures, all resolved by correcting the review
setup. The historical **501 passed, 5 skipped** must not be quoted as current.
See [the September 18 handoff](SESSION_HANDOFF.md#review-2026-09-18) for exact
commands, failure nodes, fault-injection reproductions, and scope limits.

No live-model behavioral audit was run during this review. Before the next one,
check that the audit arms describe the current somatic prompt text. Receipts
remain useful evidence, but the reproduced embedding defect shows their
accuracy also requires regression coverage.

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

# Track B: The Creative Determinant

**Correction (2026-09-17):** The graph Laplacian and Picard solver described in earlier versions of this document have been removed. Following a recommendation from Nelson Spence, who pointed out the Laplacian term was contributing only ~1.5% of the eigenvalue, the governor no longer builds a memory subgraph or solves an elliptic BVP. Instead, `CyberneticGovernor._bitmap_regulation` reads `SignBitmap.score_all(q)` in one pass to compute a standard deviation score over the corpus mean, gating temperature directly. The prompt tag is now `<thermal_gate>`. B0 through B3 below have been updated to reflect the current design.

## B0. The Mathematical Core

The Creative Determinant drives the engine's physics state via metabolic calculus:

- `CreativeDeterminantEngine` (in `physics/maths.py`) calculates `viability` ($b = \kappa\gamma - \lambda_{eff}\mu$) and uses it to update ATP and ROS via `execute_metabolic_tick`.
- `physics/observer.py` maps the supplied `frustration_ratio` to $\mu_{viability}$ with `min(1.0, frustration_ratio * 10.0)`. This is a scaled computational signal, not independently established evidence of semantic contradiction.
- $\lambda_{eff}$ is divided by $R_{base}$, which is derived using a 4-sample finite-difference window over $\psi_{history}$ (`geo.abstraction`). This provides momentum to the penalty term and stops the system from becoming too frantic or too sluggish too quickly.

## B1. The Thermal Gate

The engine directly controls the LLM generation temperature using the thermal gate mechanism. 

- `CyberneticGovernor` computes `z_excess` by subtracting a corpus-size null estimate from the standardized top-match score and proposes a temperature via `gate_temperature()`. Insufficient corpus evidence declines the measurement and falls back to PID regulation.
- `brain/cortex.py` attaches that proposed temperature; `PromptComposer` emits the `<thermal_gate>` tag. `LLMInterface.generate()` strips the tag and clamps its value to the supplied `temperature_band`. A proposed zero can therefore become a nonzero sampling temperature. No eigenvalue sign testing is performed.

## B2. The Solver has been Removed

Because the Laplacian and Picard solvers provided minimal mathematical signal while adding massive complexity, they were stripped out. 

The system uses `ordvec.SignBitmap` to score memories in one pass. The governor
uses the top-match excess over its estimated corpus null and the sharpness of
those matches to influence sampling and regulation. These are similarity-based
heuristics; they do not establish that an utterance is coherent or creative.

## B3. Tuning and Validation

The earlier blanket claim that all tests pass is withdrawn. The September 18
review confirmed seven failures across cortex, gate-tolerance, Moog, preflight,
and scar tests, including `MagicMock` fixture/type errors. It also reproduced
embedding fallback defects outside those tests. A new complete suite run and
live validation are still needed; passing a governor-specific test does not
validate the whole turn or the model's response.

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

**Correction, same night (2026-09-17), after three more models and a
regeneration.** Two claims above do not hold as written.

- *"Replicated on both models"* (item 1) was too strong. mistral-nemo's
  cache was deleted by `reset.sh` and regenerated with the same seeds;
  Ollama is not bit-for-bit deterministic, and the rerun gave -0.75 words per
  sentence with an interval crossing zero, against -0.97 [-1.74, -0.20] the
  first time. gemma4:e4b reproduced closely. Across all five models the
  anaerobic sentence-length effect clears zero on gemma4:12b (-1.34) and
  gemma4:e4b (-0.65) only. Read it as small and model-dependent.
- *"Not obeyed"* (item 2) is a finding about two models, not about the
  instruction. On gemma4:12b the same words put 94% of replies within three
  sentences (11% on control) and cut length by 62%; qwen3.5:9b reached 60%;
  ministral-3:14b halved length without reaching three sentences. How well a
  model obeys a body depends heavily on the model. D7 carries the full table.

Verdict: the somatic layer is partly decoration. Metabolic state measurably
reaches the prose through respiration, weakly. The exhaustion instruction is
not obeyed as written and should either be reworded (a hard word or sentence
budget stated outside the `[INTERNAL USE ONLY]` block is the obvious first
try, and `audit_somatic.py` will measure it) or stop being described as a
constraint. `README.md` and `credits.txt` now say this.

**Found on the way.** Three failures of this document's usual kind, each
silent:

- **Reasoning models get fabricated replies.** *(Fixed the same night; see
  D0 "Repairs".)* `LLMInterface.generate` sends a
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

# Track D: The Somatic Contract

Written 2026-09-17, after C5. The body is meant to be BoneAmanita's
centerpiece, the thing no other harness has. C5 measured it and found it
mostly decorative: every somatic instruction reaches the prompt, one moves
sentence length by about 10%, and the other is ignored or reversed. This
track makes the body load-bearing, and it inherits C5's rule: **no somatic
behaviour is claimed until an audit measures it on at least two models.**

## The split (decided 2026-09-17)

The model never performs a body. Two states feed generation, and they have
different jobs:

| Input | Shapes | Never |
|---|---|---|
| **The person's state** (tiredness, effort, disengagement, distress) | reply length, how much is asked of them, questions, pacing, the tone of care | mirrored back at them |
| **The engine's state** (ATP, respiration, ROS, chemistry) | what the engine can afford: budget, retries, steadiness against turbulence, sampling | narrated or performed |

The person's state is the primary input: the output is colored to
**accommodate** them, not to reflect them. Mirroring is wrong in exactly the
cases that matter; someone anxious or flagging needs a steady partner, not
an echo. The engine's state still matters, because co-regulation needs two
parties and a partner with no state of its own can only mirror, but the
person never reads "the engine is tired". They see a partner that gets
briefer and steadier when the conversation has been draining.

This retires the idea of prose that sounds breathless. C5's one positive
result (anaerobic shortens sentences about 10%) is not a behaviour to
preserve; depletion should lower the budget, not change the voice.

The shape of the problem is the same as the rest of this document, one
level up. A subsystem that computes a value nobody uses is dead wiring; an
instruction the model does not follow is dead wiring with a live model on
the other end. The fix is also the same: fewer channels that pretend, more
channels that bind, and a receipt for each one.

## What exists today (confirmed by reading the code and one spied turn)

Five separate paths claim to carry the body into generation, and nothing
reconciles them:

| Path | Where | Trigger | What it does | Status |
|---|---|---|---|---|
| Respiration line | `composer.py`, `bio_anaerobic` | `respiration == "ANAEROBIC"` | "Raw, breathless, efficient prose." | ~10% shorter sentences (C5) |
| User exhaustion line | `composer.py:709` | user `exhaustion > 0.8` | "You are exhausted. ... 3 sentences or less" | not obeyed; reversed on gemma (C5) |
| Engine depletion directive | `cortex.py:229` | ATP `p < 20` or `max_tokens < 300` | "under 3 sentences", caps `max_tokens` at 400 | unmeasured; same wording C5 found ignored |
| Chemistry sampling | `mind.py` modulator | dopamine, cortisol, adrenaline, chi | temperature, top_p, penalties, max_tokens | **temperature and top_p overwritten every turn** |
| Standing metabolism line | mode directives | always | "Let fatigue shorten your sentences" | present in every prompt, calm or not |

The fourth row is new and confirmed: over three mock turns, spying on
`llm.generate`, the modulator asked for temperature 0.79 and 0.4 and both
went out as 0.7. The `<cd_lambda_1>` thermal lock replaces temperature and
top_p outright whenever the tag is present, which is nearly every turn, so
the whole chemistry-to-sampling mapping is computed and discarded. The
`max_tokens` side survives but never binds: base is 720 to 930 tokens and
the depletion cap is 400, against replies averaging 20 to 50 words.

The third row also corrects `SESSION_HANDOFF.md`, which says the engine's
own depletion reaches the prompt only through respiration. It also reaches
it through `cortex.py:229`, as a style directive.

## D0. Somatic census: is the body ever in a distinct state?

**Do this first; it can invalidate the rest.** Handoff open item 2 records
three mock turns taking ATP from 60 to 0. If a real session pins ATP near
zero within a few turns, every depletion directive is permanently on, a
permanent instruction is a constant, and a constant cannot express a body
no matter how it is worded.

Run a scripted 30 to 50 turn conversation against a live model and record,
per turn: the person's `E_u` and `P_u` (and their message length against
baseline), ATP, ROS, respiration, which of the five paths fired, modulator params against sent params, and the reply measures
from `audit_somatic.py`. Deliverable: `tools/audit_somatic.py --census` (or
a sibling tool), printing the state distribution over the session.

**Done when** the table shows, for both the person's state and the
engine's, that each state is reachable, is left again, and is not the
resting state. If the engine's economy rests at depletion, retune it before
D1 to D3. If the person's signals barely move over a real conversation, the
primary input of this whole track is too weak to steer anything, and that
has to be fixed first. Say which, here.

### D0 repairs (2026-09-17, afternoon): the economy now holds

Gordon's calls, implemented and measured. A 30-turn live census on gemma4:12b
now ends with ATP between 16 and 53 (it used to be zero from turn six) and ROS
peaking at 5 to 45 rather than 98.

- **The metabolic cycle always runs.** `MetabolismPhase` used to return early
  when a mode set `atp_drain_enabled: False`, which skipped the cycle, and the
  cycle is where every income path lives (vagus support under 20 ATP, PID
  homeostasis, photosynthesis, digestion). The costs are scattered through the
  cortex and kept charging, so CONVERSATION had every cost and no income. The
  flag now scales the burn (`BIO.GENTLE_COST_SCALE`, 0.35) instead of skipping
  the cycle. Measured income over 30 turns: symbiotic yield +123, PID +42.
- **Passive recovery**: `BIO.ATP_IDLE_RECOVERY_PER_MIN` (6.0, capped 25) turns
  the clock between turns into ATP.
- **Deliberate recovery**: silence now yields ATP as well as stamina
  (`BIO.ATP_SILENCE_YIELD`, +58 over the run). The person leaving space is the
  intentful half; `/rest` and `/idle` remain the explicit half.
- **Toxicity is no longer a glutton.** The counterfactual gate no longer adds
  its simulated ROS to the body (the generation never ran, and charging it made
  rejection feed rejection), its cost is `BIO.COUNTERFACTUAL_ATP_COST` (4, was
  10), and ROS decays `BIO.ROS_DECAY_PER_TURN` (3) every turn.
- **The boilerplate filter is narrower and cheaper.** `mitigate_rejection`
  matched all 160 `BANNED_PHRASES` as substrings and charged a flat 50 ATP, so
  "ultimately" anywhere in a reply emptied the pool. It now matches a separate
  `RLHF_MASKS` list on word boundaries and charges 10% of the pool capped at
  `BIO.HLA_MASK_TAX_MAX` (8). The gatekeeper's own banned-phrase tax is
  `BIO.GATEKEEPER_BANNED_TAX` (5, was 15) and `GATEKEEPER_BANNED_ROS` (8, was
  20). The Lexical Firewall still rejects style crimes; it just no longer bills
  the body for them as deception.
- **The exhaustion gate is `CORTEX.EXHAUSTION_GATE`, now 0.5.** D0 measured a
  flagging partner peaking at 0.61, so 0.8 could never fire. 0.5 sits above the
  engaged mean (0.38) and below the flagging mean (0.56).
- **`gemma4:12b` is the default model** (D7), with `CORTEX.REASONING_EFFORT`
  defaulting to `none`.

Every constant above is in `lore/tuning_presets.json` and registered in
`BonePresets.REQUIRED_CONFIG`, so the boot audit names any that goes missing.

### D0 result (measured 2026-09-17, overnight)

`tools/audit_somatic_census.py`: 30 scripted turns through the real engine
(engaged, tiring, flagging, distressed, recovering), persistence patched off,
the real embedder, an ATP ledger that records every write to the pool and
who made it. Re-run it; the cache is `tools/cache/somatic_census.jsonl`.

**Both.** The engine's economy rests at depletion, and the person's signal
moves the right way but never reaches the gate that would use it.

**The engine dies by turn six.** On mistral-nemo, after the repairs below,
ATP went 57, 35, 26, 17, 8, 0 and the parity gate refused every later turn
("Metabolic budget exceeded ... Available ATP: 0.0"). The ledger for those
six turns:

| ATP | count | source |
|---|---|---|
| -15.0 | 1 | gatekeeper banned-phrase tax (`physics/filters.py`, via `apply_metabolic_tax`) |
| -13.0 | 6 | Deep Structural Scan (`metabolism.py:82`) |
| -12.4 | 6 | LLM token generation (`cortex.py:300`) |
| -10.0 | 2 | `main.py:270 set_atp` |
| -14.0 | 7 | cognitive stumbles (validator re-asks, including terminal) |
| +4.4 | 1 | Harmonic Resonance, the only income |

Nothing regenerates ATP during a conversation; REM, which does, needs idle
time and itself drains 2.0. gemma4:12b with reasoning on died after turn 1,
before the HLA repair below, and took 136 seconds a turn.

**ROS is a second, independent spiral.** Re-run with ATP held at 60 before
every turn (`--hold-atp`, labelled as scaffolding in the report): ROS rose to
about 98 and never cleared, the counterfactual gate rejected every turn from
turn 9 (each rejection *adds* its simulated ROS to the pool, so rejection
feeds rejection), `Somatic Shock (ROS Toxicity)` took 195 ATP over 13 turns,
and health reached zero at turn 24 ("CRITICAL FAILURE (NO DEATH PROTOCOL)").

**The person's signal moves, weakly.** With ATP held, `E_u` averaged 0.38
engaged, 0.37 tiring, 0.56 flagging, 0.47 distressed; the maximum over the
whole session was 0.61. The user exhaustion directive is gated at `> 0.8`,
so a partner answering "ok", "sure", "yeah fine" for six turns never
triggers it. It is unreachable, not merely disobeyed. `P_u` fell from 83 to 6
over six long engaged messages and recovered to 65 during short ones, which
is the designed direction and a steep rate.

**The prompt never sees the engine's body.** Telemetry carried `P:100.0 ROS:0.0`
on every turn while the real pool fell to zero and ROS sat near 40. This
confirms the suspected `gather_state` mismatch: it reads
`bio["mito"]["state"]`, the bio result has no `mito` key, and `p` falls back
to 100. So the anaerobic line and `cortex.py:229`'s depletion directive fired
0 of 10 turns. The thermal lock overwrote temperature on 10 of 10.

**Repairs made while measuring**, each with a real-path test and a mutation
check (the reverted code fails the new test):

1. *Stop list against reasoning models* (`brain/composer.py`). An empty reply
   is retried once without stop sequences; if that fills it, the model is
   marked `stops_cut_reasoning` and stops are applied to the reply text from
   then on. A reply still empty is a named `EmptyReplyError`, logged at WARN
   and counted by the circuit breaker, not mock prose. Confirmed live on
   gemma4:12b with reasoning on.
2. *Fallback recursion* (`brain/mind.py`, `brain/composer.py`).
   `hallucinate(via_synapse=False)` from `mock_generation`; one `generate`
   call per fallback where there were 486.
3. *Scars written to a network that has no scars* (`brain/cortex.py`,
   `cycle.py`, `phases/biological.py`, `phases/cognitive.py`). Four sites
   called `mind.mem.record_scar`; `record_scar` lives on the Akashic Record.
   Three were `hasattr`-guarded and silently recorded nothing; the cortex's
   was not, so the first counterfactual rejection raised, SystemHealth took
   MIND offline, and cognition was skipped without a word on every later
   turn. All four now call `eng.akashic`. **Review this one**: scars now
   actually record, which runs `_mutate_system_prompts` and writes
   `EPIGENETIC_SCARS` into `lore/system_prompts.json` through `lore.save`. No
   composer path reads that key back as far as a search found, but it is a
   tracked file and it will change in real sessions.
4. *HLA tax read the wrong object* (`physics/filters.py`). The cortex passes
   the `MitochondrialForge`; `getattr(forge, "atp_pool", 100.0)` always read
   the default, so every hit charged the maximum 50 ATP. It now reads
   `.state.atp_pool`. The existing test passed a flat state-shaped mock and
   could not see it.

Found and **not** changed, because they are design:

- `mitigate_rejection` treats the whole `BANNED_PHRASES` list (160 style
  crimes, substring match, so "ultimately" anywhere) as the RLHF-mask
  patterns its 50-ATP "LEVEL 1 DECEPTION" tax was written for, and the
  gatekeeper then taxes the same reply 15 ATP and 20 ROS again, and the
  validator charges a stumble on top.
- No per-turn ATP income, and the counterfactual ROS gate feeding itself.
- The 0.8 exhaustion gate against an `E_u` that peaked at 0.61.
- `gather_state`'s `bio["mito"]` read (a wiring fix, but it would switch the
  depletion directives on for the first time, so it belongs with D1).

## D0b. The refusal gates, resized

D0 repaired the economy and uncovered the next layer. Over 30 live turns with
ATP healthy, generation was refused on 18 of them by four independent gates:

| Gate | Where | Refused | Rule |
|---|---|---|---|
| PINKER counterfactual | `brain/cortex.py` `_evaluate_toxicity` | 12 turns | `drag*5 + chi*20 + m_a*30 > CORTEX.COUNTERFACTUAL_ROS_GATE` (35) |
| ROS panic | `phases/cognitive.py` | 2 turns | `ros + friction*chi*20 >= BIO.ROS_PANIC_THRESHOLD` (100), costs 15 ATP |
| Gatekeeper syntax | `physics/filters.py` | 2 turns | banned phrase in the reply |
| Tensegrity anchor | `brain/cortex.py` | 1 turn | drag or chi over their limits |

Plus the crucible, which is not a refusal but a health drain: `voltage > 18`
with `kappa < 0.5` costs `voltage * 0.5` health, 126 health over 9 events, and
a dead engine at turn 29.

What a normal conversation actually produces (census, same 30 turns):

| Reading | min | mean | max | the gate |
|---|---|---|---|---|
| PINKER total | 11.4 | **44.0** | 62.5 | fires above 35 |
| narrative drag | 1.6 | 5.3 | 9.7 | contributes `drag*5` |
| chi | -0.29 | 0.54 | 0.99 | contributes `chi*20` |
| voltage | 10.0 | **21.7** | 44.3 | MELTDOWN above 18 |
| kappa | 0.0 | 0.35 | 1.0 | MELTDOWN below 0.5 |

**Both thresholds sit below the mean of ordinary conversation.** These gates
were tuned for ADVENTURE, where high drag is a story coming apart and a health
cost is the point. In CONVERSATION they fire on a person answering "ok" for
six turns, and the engine goes silent exactly when its partner is flagging,
which is the reverse of the split this track is built on. Letting normal
conversation through needs roughly 65 for PINKER (above the observed maximum)
and about 45 for MELTDOWN.

**Decided (Gordon, 2026-09-17): option 1 now, option 3 staged as D9.**

**Unverified.** The tolerances below were sized from the census and had earlier
unit checks; the September 18 review found two failures in
`tests/test_gate_tolerance.py` caused by a missing `MagicMock` import. The live
30-turn census that would prove a conversation now
reaches its end was interrupted before its first turn. Run it before treating
this section as measured; everything else in D0 was confirmed against a live
model, and this is not.

*Option 1, done.* Every mode carries a `gate_tolerance`
(`BonePresets.MODES`), applied at boot as `config.GATE_TOLERANCE` and read by
each gate: the PINKER counterfactual gate, the Moog quarantine and tensegrity
anchor (which already had a hardcoded 1.5 for CREATIVE and 1.0 for everything
else), the ROS panic gate in `phases/cognitive.py`, and the crucible's
meltdown line (`MACHINE.CRUCIBLE_MELTDOWN_VOLTAGE`, new, 18.0). Tolerances:
ADVENTURE 1.0, TECHNICAL 1.0, CREATIVE 1.5 (its old hardcoded value),
CONVERSATION 1.6. At 1.6 the PINKER gate sits at 56 against a census mean of
44 and a maximum of 62.5, so ordinary conversation passes and a genuine
extreme still does not; the meltdown line sits at 28.8 against a mean voltage
of 21.7. `tests/test_gate_tolerance.py` pins that a conversation allows what
an adventure refuses, that an extreme is still refused, and that the crucible
line moves. Both wirings were mutation tested.

*Option 2 was not taken.* Gating on measured ROS rather than predicted is the
better idea in isolation, but it deletes the counterfactual mechanism rather
than resizing it, and D9 replaces that mechanism wholesale. Revisit only if
D9 is dropped.

Re-run `tools/audit_somatic_census.py` after any change here: a 30-turn
conversation must reach its end with generation on most turns, including the
flagging and distressed phases.

## D9. One refusal, with a reason (done, confirmed live)

**2026-09-19 status:** the audit found what "acceptance target, not proof"
undersold: four refusal paths in `SimulationPreflightPhase`
(`NABLA_SILENCE`, `APOPTOTIC_BLOCK`, `PREMISE_VIOLATION`,
`POINT_OF_NO_RETURN`) were still bypassing nomination entirely, untested,
deciding unilaterally one phase before `ArbitrationPhase` ever ran. Fixed:
all four now nominate and let the Stage Manager decide, with regression
coverage. The 30-turn live census below confirms it: every halt carries the
same Stage Manager reason and a matching ATP ledger entry, and the flagging
phase (6 of 6) and most of distressed (4 of 5) were answered, not refused.
See the [2026-09-19 handoff](SESSION_HANDOFF.md#d9-d1-d2-census-2026-09-19).

**September 18 status (superseded above):** nomination objects, Stage Manager
arbitration, and refusal receipts were already present in the code, but the
design below was an acceptance target, not proof that every refusal had
migrated. Seven regression tests failed in the reviewed tree, several at this
boundary; all seven were repaired in the follow-up above. No live census had
yet established completion.

Chosen as the destination for refusal, after the D0b tolerances buy room to
work. Before nomination routing, five mechanisms could independently stop a
turn: the PINKER
counterfactual gate, the ROS panic gate, the Moog quarantine, the tensegrity
anchor, and the gatekeeper's syntax rejection. Each had its own threshold, its
own message, and its own idea of what danger was, without a common record of
why the engine declined to speak.

C4 already built the right shape for this. The Stage Manager negotiates
Tension before anyone speaks, sets `refusal_triggered`, and types the packet
`SILENCE` with a mandatory reason. D9 routes every refusal through it:

- each gate becomes a *nomination* with a named reason and a magnitude, not a
  decision of its own;
- the Stage Manager weighs the nominations against the person's state (D1's
  budget), because refusing to answer a distressed partner is a different act
  from refusing a runaway argument;
- one receipt per turn records what was nominated, what was decided, and why
  (D5), so a silent turn is auditable rather than mysterious;
- the ATP cost of declining is decided once, in one place, instead of five
  gates each charging their own.

**Done when** a census run shows every halted turn carrying a Stage Manager
reason and a receipt, no gate stopping a turn on its own, and the flagging and
distressed phases answered rather than refused. **Met**, 2026-09-19: run
`20260919-095553` against `gemma4:12b`, all three halts share one Stage
Manager reason and one matching ATP ledger entry each, flagging 6/6 and
distressed 4/5 answered.

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

## D2. The somatic instructions, rewritten (decision)

**2026-09-19 status:** confirmed by direct inspection and the new pin tests
that decisions 1-3 and 5 below are implemented as written: the partner-framed
cap wording, the retired anaerobic voice line, the always-on
do-not-narrate line, and the kernel's "Meet the person where they are"
replacement for "Mirror the user's energy" (`lore/system_prompts.json`).
Decision 4 is partial: the SOMATIC CONTRACT block sits after `dialogue` and
before a one-line `[MODE: X]` tag, which sits before `=== PARTNER INPUT ===`
- not literally the last instruction, though nothing substantive intervenes.
Not yet done: the tool that would run decision 4's own measurement
(`tools/audit_somatic.py`) was broken and measuring a retired mechanism; it is
rebuilt and verified working (see the
[2026-09-19 handoff](SESSION_HANDOFF.md#d9-d1-d2-census-2026-09-19)), but the
statistical pass in this section's own "done when" has not been run.

**September 18 status (superseded above):** partner-focused sentence caps and
the prohibition on body narration already appeared in the current composer's
somatic contract. Their live effects were not measured in that review. The C5
results above are for earlier wording; they cannot certify this
implementation. The following five decisions describe the intended changes and
required measurement arms:

1. **Address the right body.** User exhaustion stops saying "You are
   exhausted". It becomes about the partner: "Your partner is running low.
   Answer in at most {n} sentences." Telling a model it is exhausted invites
   it to play a tired character, which is what gemma did (more, shorter
   sentences) and plausibly what mistral did (more antithesis).
2. **Numbers, not adjectives, and no voice.** The anaerobic line ("Raw,
   breathless, efficient prose") is retired. Depletion lowers the budget
   and states it as a number ("Answer in under {n} words"); it does not ask
   for a different voice. A model can check a number against its own
   output; it cannot check "raw".
3. **Say what not to do.** Always, not only under depletion: "Do not
   mention breath, lungs or a body." mistral-nemo's breath and body words
   rose about 5x under the anaerobic instruction, which the kernel already
   forbids in general terms and which the model does not connect to it.
4. **Move it out of the metrics block and to the end.** Today the
   exhaustion line sits inside `[INTERNAL USE ONLY]`, directly after an
   instruction to "consume these metrics to shape your narrative and tone",
   which frames it as characterisation. Place the budget as the last
   instruction before `=== PARTNER INPUT ===`. Also delete the standing
   "Let fatigue shorten your sentences" from calm prompts.
5. **Accommodate, do not mirror.** The kernel's "Mirror the user's energy"
   is replaced with an instruction to meet the person where they are:
   steady when they are agitated, brief when they are flagging, and never
   matching distress with distress.

`audit_somatic.py` gains variant arms (current wording against each
rewrite, and placement inside against outside the block), so the four
changes are measured separately rather than as one bundle.

**Done when**, on two models: the share of replies within the cap rises
against control with an interval clear of zero, body narration does not
rise, and D2b's accommodation measures move in the intended direction. If a change does not clear that bar, it is not
adopted, and this entry records which one failed. **Not yet run**: the
2026-09-19 audit rebuilt the tool this needs (it could not previously have
produced this measurement at all); the actual pass is next.

## D2b. Measure accommodation, not obedience (measures built, pass not run)

**2026-09-19 status:** implemented. `body/somatic_metrics.py` gained
`reply_to_message_ratio`, `ends_with_question`, `offers_to_carry_load`,
`mirrors_affect`, and `question_count`; `tools/audit_somatic.py` gained a
`DISENGAGED` arm (flagging exhaustion and critically low effort together,
the only combination that sets `offer_to_carry_load`), with `CONTROL`/
`EXHAUSTED` doubling as the "fresh"/"tired" personas. "Choices offered" and
"instructions given" (part of "demand on the person" below) have no
defensible regex proxy and are left unmeasured rather than guessed at.
Verified live in a smoke run, not yet the statistical pass below. See the
[2026-09-19 handoff](SESSION_HANDOFF.md#d9-d1-d2-census-2026-09-19).

C5 asked whether the prose obeys an instruction. The split asks a different
question: does the reply fit the person? That needs arms built from the
person's side (the same message sent as from a fresh, a tired, and a
disengaged partner, with the lattice state set accordingly) and measures
taken relative to them:

- reply length relative to the person's own message and recent baseline;
- demand on the person: questions asked, choices offered, instructions given;
- closing-question rate when they are flagging (should fall);
- offers to carry the load when effort is high (should rise);
- body narration and emotional mirroring (should stay at zero; mirroring
  needs a declared proxy, for example the reply repeating the person's
  affect words back).

These live in `tools/audit_somatic.py` beside the C5 measures and share
D3's measurement module.

**Done when** the audit reports these per arm, with intervals, on at least
two models, and a tired or disengaged partner measurably gets a lighter
reply than a fresh one. **Not yet run**, as above.

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

## Sequencing within D

**Historical feature sequence.** The current priority is the stabilization and
validation work in the September 18 Status section. D1/D2/D9 code is already
present; use this sequence to check dependencies and acceptance criteria, not
to assume those features have yet to be started.

D0 first, because it can change what the rest means. D1, D2 and D2b
together, since the budget is where the new wording lives and D2b is how
it is judged. Then D3 and D5 together (the
receipt records what the enforcement did). D4 after, D6 as a sweep, and D7
whenever D2 has landed.

**Track D does not close until the stop-list bug is fixed** (Gordon's call,
2026-09-17). Three of the four D7 candidates are thinking models
(gemma4:e4b, gemma4:12b, qwen3.5:9b), and while the bug stands they can only
be measured with `reasoning_effort=none`, which is not how they would run in
production, and in production they would be served mock prose. Fix it before
D7's decision, so the models are judged as they would actually be deployed,
and fix the `mock_generation` recursion alongside it, since both live on the
same fallback path. Details in `SESSION_HANDOFF.md` Open items 8 and 9.

## Deliberately not in Track D

- **A body the model performs.** No instruction asks the model to sound
  tired, breathless, stressed or warm because of the engine's numbers. That
  is the split, and it is a decision, not an omission.
- **Fine-tuning or LoRA.** The body has to work on whatever model a person
  runs. A fine-tune would make one model obey and hide the problem for all
  the others.
- **Grammar-constrained decoding.** It can force JSON; it cannot force prose
  to be breathless, and it ties the engine to one backend's feature set.
- **A POS tagger or NLP library.** The no-frameworks decision, and C5 showed coarse
  proxies with intervals are enough to find effects and reversals.

---

# Historical sequencing — superseded

This original sequence is retained as development history. In particular, the
Laplacian/PDE and solver-vendoring items below are no longer the plan, and the
receipt guarantee was corrected in A3. Use the September 18 Status section and
latest handoff to choose the next work.

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
- **Adopting a vector store or an agent framework.** The no-frameworks
  decision (`SESSION_HANDOFF.md`). The embeddings work stayed at one HTTP POST for this reason
  and the manifold work should too.
- **Renaming the poetic variables.** The poetic-names decision. `ATP`,
  `godel_scars`, `narrative_drag` stay.
- **Shrinking the engine to the composer plus validator.** Raised in the
  original assessment as an option. Given the stated goal is a
  biological harness rather than a prompt tool, the breadth is the
  point; withdrawn as a recommendation.
