# BoneAmanita Roadmap

> **Note:** Completed roadmap items and their historical implementation details have been moved to [archive/ROADMAP_HISTORY_2026_09.md](archive/ROADMAP_HISTORY_2026_09.md).

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

## Status — reconciled 2026-09-21 (latest)

**The judge itself doesn't hold up yet; a responsive-conversation harness
built but not run, 2026-09-21:** asked which local judge to trust (Gordon has
a 7800XT; `phi4`, `gpt-oss:20b`, `qwen3:30b-a3b` pulled alongside the existing
three) and to address the scripted-conversation-vs-responsive-conversation gap
in the methodology. Built control modes for the blind judge
(`--control null|samples|mismatch|textbook`) and ran all six judges against
all three on `toast`. Result: **no judge currently clears the bar** — every
judge shows real position bias (47-62% favoring one slot, p ≤ .09) and every
judge fails the mismatch control badly (a reply written for a different
emotional moment still ranks first or middle up to half the time; bar was
90% last place, best was 79%), so the earlier "BoneAmanita indistinguishable
from Prompted" pairwise numbers on `toast` are closer to noise than a finding.
`phi4` and `gpt-oss:20b` are additionally disqualified for this project: they
reward the textbook advice-list style the Somatic voice rejects (34% and 41%
first place against it, both beating BoneAmanita head-to-head).
`qwen3:30b-a3b` is the best-positioned judge (least biased, best mismatch
score, rejects textbook) but its mismatch score still isn't good enough to
trust a verdict from. Built `tools/somatic_sim_user.py` +
`tools/audit_somatic_responsive.py` so the census/vanilla runners can answer a
simulated person reacting to what each system actually said, instead of
replaying a fixed script; found and fixed three failure modes in the
simulator itself along the way (verbatim self-repeat, repeat-then-append,
prompt-scaffold echo — all three tested, `tests/test_judge_controls.py`, 32
passing). Once clean, it found something the fixed script never showed: on
`toast`, the `bone` (full engine) arm hit a **5-turn ATP crash**
(`PARITY GATE FAILED`, ATP pinned at 0.9, 6 of 30 turns held total) that never
happened across any fixed-script run of the same topic. Root-caused and
reproduced 1 of 3 (a close second): `ros_buildup` (a "wear" metric) crossing
`BIO.ROS_PURGE` (60.0) triggers a *designed* reset, `_trigger_mitophagy`,
which pays for itself out of ATP and left the engine at ~1.0 when the pool
couldn't cover the full cost — every subsequent action then failed
`PARITY GATE` until an apparent failed-REM-cycle side effect abruptly refilled
ATP six turns later. Not rare: `ros_buildup` by turn 8 was 77.0 (crashed),
56.1 (within 4 points, didn't), and 37.5 (not close) across three runs
differing only in the simulated person's actual wording. Still open: what
drives `ros_buildup` turn to turn, and whether the fix belongs at the
threshold (mode-gate `ROS_PURGE` for CONVERSATION, the same pattern as the
earlier distress-refusal fixes) or at recovery (the multi-turn silence with no
faster recovery path than an apparent REM-failure side effect). Not yet
judged (no judge clears `mismatch`). See the
[2026-09-21 judge-controls handoff](SESSION_HANDOFF.md#judge-controls-2026-09-21)
and [TESTING.md](TESTING.md) for the tooling itself.

**Distressed-refusal fixes and a sixth, clean topic, 2026-09-21:** applied
Gordon's two choices: friction-raising council synergies (THE DIGNITY LOCK,
+50 drag by design, so the row is untouched) and MOOG's worry-quarantine are
off in CONVERSATION (`COUNCIL.FRICTION_SYNERGY_DISABLED_MODES`,
`CORTEX.MOOG_DISABLED_MODES`); 594 passed. Caveat: with MOOG off, a drag spike
by another route would fall through to `GORDON_ANCHOR`, which does not reset
drag. A sixth topic composed after the fixes (`toast`) ran clean for the engine
(29/30 turns, all distressed turns answered, one hold on a goodnight message at
the ATP floor). Two judges on both clean topics: BoneAmanita beats a bare model
(136-83, 62%) but is not distinguishable from a one-line "warm, concise friend"
prompt (116-103, 53%, p = 0.42); the human reads disagree with each other. See
the [2026-09-21 handoff](SESSION_HANDOFF.md#distress-refusal-fixes-toast-2026-09-21).

**The refused distressed turns, diagnosed, 2026-09-21:** the two refusals on
the clean `lease` run (and the friendship 27/28 and `promotion` 8 holds that
looked unrelated) share one cause. A synergy row in `lore/council_data.json`,
`BENEDICT|GORDON`, adds +50 narrative drag whenever both voices are active,
which happens when a person is quietly heavy; that trips MOOG's worry
quarantine (and at one turn the ROS panic gate), and the D9 distress shield
does not stop it because it keys on exhaustion (`sentence_cap <= 3`), not on
what was said. Reproduced three times, traced to the line, and confirmed with a
controlled probe. Not fixed yet; options are in the
[handoff](SESSION_HANDOFF.md#three-way-blind-comparison-2026-09-20). This also
corrects the 2026-09-20 note below that blamed the DSPy critic for the
friendship turns 27/28 holds.

**A fairer three-way comparison, and a fresh topic that killed the engine,
2026-09-20:** the blind comparison gained a third arm (the bare model plus one
"warm, concise friend" line) and a stricter judge (different model family, a
rubric from the receiving person's side, two shuffled passes, two judge
models); the earlier 22-3 and 27-1-1 tallies came from a same-family judge with
a kernel-shaped rubric and should be read as upper bounds. A new topic
(`promotion`) killed the engine on turn 11: `physics/observer.py` forces
voltage to 160 on the substring "faster" or three `!`, the crucible's meltdown
turned that into fatal damage, and an ops-style "deploy" gate held an earlier
turn. Both are now off in CONVERSATION (`CORTEX.KEYWORD_TRIGGERS_DISABLED_MODES`,
regression-tested, 588 passed). A fifth, untouched topic (`lease`) then ran
clean for the engine (28/30 turns, no death) but refused two of five
distressed turns and ended nearly out of ATP, both left open on purpose.
Judged blind, BoneAmanita beat the bare model 66-37 (p = 0.006) and was not
distinguishable from the one-line prompt, 56-47 (p = 0.43). Two human blind
reads split: Gordon picked BoneAmanita 28 of 28, a friend about 7 of 28. See the
[2026-09-20 three-way handoff](SESSION_HANDOFF.md#three-way-blind-comparison-2026-09-20).

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

## A7. A `/tune` command (plan, not started; drafted 2026-09-23)

`BoneConfig.tune(sector, parameter, value)` already exists
(`engine/presets.py`): it checks the sector and key exist, refuses a type
change, sets the value and runs `validate_integrity()`. `tests/test_presets.py`
covers it. **Nothing calls it**, so every tuning change today means editing
`lore/tuning_presets.json` and restarting. Found while wiring up `WHIMSY`,
when the handoff nearly claimed the keys were "live-tunable with `/tune`".

The command itself is small. The risk is the same one this whole document is
about: **a knob that reports success and changes nothing.** Three things
make that likely here:

1. **Two config objects.** The engine reads `engine.config` (an instance);
   six modules read the `BoneConfig` class directly (`mechanics/terminal.py`,
   `setup.py`, `lexicon.py`, `dspycritic.py`, `archetypes/council.py`,
   `main.py`). Tuning one leaves the other stale: `/tune WHIMSY
   LUDICROUS_SPEED true` on the instance would not reach `typewriter()`, which
   reads the class.
2. **Values cached at boot.** The "`__init__` Bedrock Caching" rule (A1) means
   many subsystems copy a config value once and never read it again
   (`HLA_Stabilizer.mask_ros`, the idle-recovery rate, the gatekeeper's
   patterns). Setting the config afterwards changes nothing they do.
3. **Values rewritten later.** `main.py` sets `config.GATE_TOLERANCE` from the
   mode's settings on every mode change, so a tuned tolerance silently reverts
   at the next `/mode`.

**Plan:**

- **`/tune`**: no args lists the sectors; `/tune SECTOR` lists its keys with
  current values; `/tune SECTOR KEY VALUE` sets one. Auto-registers like every
  other `_cmd_` method and goes through the same reality-layer gate.
- **Parse by the current type**, since command arguments arrive as strings:
  `true`/`false` for bools, int, float, else string. `tune()` already rejects a
  type change; parsing first is what makes it usable.
- **Set both objects**: `engine.config` and the `BoneConfig` class, until the
  six class readers are moved onto the engine's config (a follow-up, tracked
  here, not a prerequisite).
- **Say whether it took effect.** Each key is classed *live* (read per use)
  or *at next boot* (cached in an `__init__`). Start with an explicit
  allowlist of keys proven live by a test that tunes them and observes the
  behaviour change (the `WHIMSY` keys, the somatic budget constants read per
  turn); everything else reports "set; takes effect at next boot". Grow the
  allowlist one tested key at a time. Never report "TUNED" for a key nothing
  will read.
- **Say when it will be undone**: a tuned `GATE_TOLERANCE` warns that `/mode`
  resets it.
- **A receipt per change** (`config.tune`, A3's pattern), so `/diag` shows
  what was changed this session and a transcript can be told apart from a
  stock engine's. A census or panel run must be able to state it ran on
  stock tuning.
- **Persisting is opt-in**: `/tune --save` writes to the user's own
  gitignored `config.json`, never to the tracked `lore/tuning_presets.json`,
  so an experiment cannot leak into the repo's defaults. (Check first that
  `config.json` values are merged at boot for the sector in question.)

**Deliverables:** the command; a type-parsing helper with tests; the live
allowlist with one behaviour test per key; the two-object write, with a test
that a tuned `WHIMSY.LUDICROUS_SPEED` reaches `typewriter()`; the receipt;
the `/mode` warning; `--save` with a test that it never touches `lore/`.

**Not in scope:** tuning mid-panel-run. The census boots a stock engine and
must keep doing so.

## A8. Right-size the context window (done 2026-09-24, 20.7.4.32; plan kept below)

**Measured.** Largest composed prompt per mode over 30 paced turns (stand-in
model; exact counts from Ollama's `prompt_eval_count`): CONVERSATION 2,162
tokens (2,407 in the real rescue run), ADVENTURE 1,830, CREATIVE 1,323,
TECHNICAL **5,668** with the code sweep. Characters per token: prose 3.5-3.9,
code **2.88**, so the shared estimate is now 2.5 (`CHARS_PER_TOKEN`).
Window cost on `gemma4:12b`: 8.1 GB at 4096 and **8.4 GB at 8192, 16384
and 32768 alike**, load about 2 s at each (the first, 3.6 s, was a cold
start); its sliding-window attention keeps the reservation nearly flat, so
the premise "32k is heavy" did not hold on this model (it would on one
without that design).
**Chosen:** `NUM_CTX` 16384, the smallest bucket that fits every mode's
largest prompt plus the 4,096-token reply ceiling. **Built:**
`PromptComposer._fit_to_window` cuts the code sweep first, then the oldest
dialogue, never the kernel, persona, rules or the person's message, and the
`composer.compose` receipt now carries `block_chars` and `trimmed`
(`tests/test_context_window.py`, mutation checked).
**Found on the way:** (1) TECHNICAL crashed on any turn at chi >= 0.5:
20.6.3 removed `TheTclWeaver._QUANTUM_REGEX` but kept its use (restored,
tested). (2) The high-voltage audit had missed a third replacement: above a
hard-coded 60 the dialogue block became "RECENT THOUGHTS... memory streams
strained" and the person's message "INCOMING SHOCKWAVE [VECTOR]", dropping
the `=== PARTNER INPUT ===` marker; removed under the same approval as A.
(3) In the stand-in measurement TECHNICAL reached the model on 2 of 30
turns, CREATIVE 4 and ADVENTURE 10 (holds and ATP halts); not chased,
since a fixed 70-word stand-in reply may trip the economy and repetition
checks those modes lean on. (4) D, `VOLTAGE_LOW`: besides the reply prefix
(neutral since 20.7.4.30), `mechanics/pragmatics.py` gates two rules on a
hard-coded `voltage < 20`, a length rewrite at engine stamina < 50 and a
"perhaps" strip at chi < 0.4; both effectively always on in conversation,
neither mislabels the engine's state; left as they are.

20.7.4.20 made the engine ask Ollama for its own window (`CORTEX.NUM_CTX`,
native `/api/chat`) and set it to 32768 to match the baseline arms. That
fixed the truncation, but it is far bigger than the engine needs: with the
source-code sweep scoped to TECHNICAL, a conversation prompt is about 1.3k
tokens (turns 0 and 1 of the first run after the fix, which were 4k and 7.8k
before). Gordon: "That's a lot of weight to carry around each turn,
especially at boot."

**Why the window costs even when the prompt is small:** Ollama reserves the
KV cache for the whole `num_ctx` when it loads the model, whatever a prompt
uses. On `gemma4:12b` that was 8.1 GB at 4096 and 8.4 GB at 32768 (its
sliding-window attention keeps the difference small; a model without it pays
far more), and it is VRAM the critic (`gemma4:e4b`) and the simulated person
share. A bigger reservation also means a slower load at boot.

**The trap:** sizing the window per call. A request with a different
`num_ctx` makes Ollama reload the model (verify on 0.32 before relying on
it), so a window that tracks each prompt would reload on most turns. The
window has to be one size per session, chosen from measurement.

**Plan:**

- **Measure what prompts actually need.** Census records carry
  `usage.prompt_tokens` per turn from Ollama's own count. Take the largest
  across a responsive run in each mode that matters (CONVERSATION,
  ADVENTURE, TECHNICAL with the sweep, a boot turn), plus the largest reply
  the engine allows, plus a margin.
- **Measure what a window costs**: VRAM (`ollama ps`) and cold load time at
  4096, 8192, 16384 and 32768 on the shipped model, so the choice is a
  trade-off with numbers on both sides.
- **Pick the smallest bucket that fits** (likely 8192) as `NUM_CTX`, fixed
  per session. Keep the per-call warning when a prompt fills the window.
- **Never let Ollama truncate.** When a prompt plus reply room would
  overflow, Ollama cuts from the *start*, which is the system kernel. The
  composer knows its blocks' priorities; it should drop or shorten the
  lowest-priority ones (oldest dialogue first) itself, and file a receipt
  saying what it cut, so an overflow is visible and ordered, never silent.
- **Weigh the prompt's standing blocks.** On a typical turn "BOOT
  DIRECTIVES" is still about 2.6k characters and "RECENT DIALOGUE" grows to
  about 4k. Find out what BOOT DIRECTIVES carries after boot and whether it
  must ride along every turn. The `composer.compose` receipt already lists
  the blocks; add each block's size so this is measurable per turn.

**Fairness:** the baseline arms need a large window for a different reason:
they carry the whole transcript, and vanilla's replies run to 340 words. The
panel's fine print states each side's context from the records, so the two
can differ as long as neither truncates.

**Deliverables:** the prompt-size table by mode; the VRAM/load table by
window; `NUM_CTX` set from them; composer-side overflow trimming with a
receipt and a test that the system kernel survives an oversized dialogue;
block sizes in the compose receipt.

**Not in scope:** changing the baseline arms' window.

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

# Track C: The Biological Harness

Measured against `docs/The Hypervisor/HYPERVISOR_V7.0.MD`, which is the
design target.

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

**Correction (2026-09-23):** D4 did not reconnect the channel for measured
turns. It turned the lock into a band, but a diffuse gate returned
`(T_LOCKED, T_LOCKED)` = `(0, 0)`, which replaced the somatic band, and the
0.5 pivot was unreachable in conversation, so from `MIN_CORPUS` on every turn
sampled at 0. Fixed in 20.7.4.15: the gate narrows the somatic band from the
top (`gate_openness`), never below half of it, and `Z_PIVOT` is 0.2. See the
handoff's 2026-09-23 entries.

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
