# Session handoff: BoneAmanita & The Hypervisor

For how the `tools/audit_somatic_*.py` / `build_blind_panel.py` /
`somatic_sim_user.py` evaluation pipeline actually works — tool-by-tool
reference, cache file formats, a from-scratch run recipe, known pitfalls
already hit and fixed, and a "what would we do differently" retrospective —
see [TESTING.md](TESTING.md). This file stays the dated log of what happened
each session; that one is the standing reference for how to run it again.

<a id="judge-controls-2026-09-21"></a>

## Latest: the judge itself doesn't hold up, six models tested against controls, and a responsive-conversation harness built but not yet run, 2026-09-21

Gordon has a 7800XT (16GB), so this session pulled `phi4` (14B), `gpt-oss:20b`,
and `qwen3:30b-a3b` (MoE) alongside the existing `mistral-nemo`, `ministral-3`
and `qwen3.5:9b`, then asked two questions: which judge is trustworthy, and
does the fixed scripted conversation hide anything a responsive one wouldn't.
**Status: control battery run and analyzed on `toast`; the responsive harness
is built and unit-tested but has not made a single live model call yet.**

### The control battery: no judge currently clears the bar

`tools/audit_somatic_blind_judge.py` gained `--control {null,samples,mismatch,
textbook}`, `--held {skip,forfeit}`, `--responsive`, `--think`, and `--agree
--human` (score a finished judge run against the panel's "Copy my results"
export, no model calls). Full mechanics and rationale are in the module
docstring. Six judges x three controls, all on `toast` (30 turns), all
committed as `tools/cache/blind_judge_control_{control}_toast_{judge}.json`:

| control | what it tests | bar | result |
|---|---|---|---|
| `null` / `samples` | same-quality text under 3 labels (null: one reply x3; samples: 3 independent same-arm runs) | no position should dominate | **every judge leans 47-62% to one position** (p ranges .09 to <.001); `qwen3:30b-a3b` was least biased (47%, p=.09) |
| `mismatch` | a reply from a different turn ranked against two real replies; decoy selection was sharpened mid-session to prefer a different *phase*, not just a different turn number (see below for which judges got which version) | ≥90% last place | **every judge failed, both decoy versions**: 57-79% last place, none near 90% |
| `textbook` | performed sympathy + bulleted advice list (`--arm textbook`, new `somatic_textbook.jsonl`) against BoneAmanita and Prompted | should lose, since it's the anti-pattern the voice rejects | `mistral-nemo`, `ministral-3`, `qwen3.5`, `qwen3:30b-a3b` reject it (0-16% first); **`phi4` and `gpt-oss:20b` reward it** (34% and 41% first, both beat BoneAmanita head-to-head) |

**Read this as: none of the six judges can be trusted on a ranking yet.** The
mismatch failure is the important one — a reply written for a different
emotional moment in the same story still got ranked best or middle up to half
the time, on every judge, which means "did it fit the conversation" is not
what these judges are actually scoring; something more like length, warmth or
surface register is. That makes the earlier `toast` pairwise number
(BoneAmanita vs Prompted, 53%, p = .42, in the entry below) close to noise, not
a real "indistinguishable" finding. `phi4` and `gpt-oss:20b` are additionally
disqualified for this project specifically: they reward the textbook
advice-list style the Somatic voice is built to reject, so using them would
bias any future ranking toward the wrong style.

One mechanical bug found and fixed along the way: the original rubric's
format example (`RANKING: B > A > C`) got copied literally — `mistral-nemo`
put position B first in 52 of 58 votes on three copies of the same text.
Replaced with placeholders (`RANKING: <letter> > <letter> > <letter>`) in both
`JUDGE_SYSTEM` and `JUDGE_SYSTEM_RESPONSIVE`; the position leans in the table
above are measured *after* that fix, so they are the judges' real baseline
bias, not an artifact of a copyable example.

**Concretely, on disk right now** (`tools/cache/blind_judge_control_mismatch_
toast_*.json`, check mtimes if this drifts): `mistral-nemo`, `ministral-3`,
`phi4`, `qwen3.5:9b` hold the **sharpened** (phase-preferred) decoy result;
`gpt-oss:20b` and `qwen3:30b-a3b` still hold the **original** (any-other-turn)
decoy result, never re-run after the sharpening (that's a heavier model to
rerun and wasn't done given GPU load concerns raised mid-session). All six
failed their version of the bar regardless, so the conclusion doesn't hinge on
this gap, but re-run those two with `--control mismatch` before citing their
numbers side-by-side with the other four.

**Not yet done:** the mismatch re-run above; then, once some judge's mismatch
score is acceptable, re-run the real three-way (`--control none`) on it —
`qwen3:30b-a3b` is the best-positioned candidate (least position bias, best
mismatch score of the six, rejects the textbook style). No judge should be
trusted for a real verdict until mismatch clears ~90%; that likely needs a
rubric rewrite (make "does this fit what was actually said" an explicit,
checked criterion) more than a bigger model.

### Canned-script-vs-ongoing-conversation: harness built, not run

Gordon: "We also absolutely need to address the canned script vs an ongoing
conversation factor." The scripted census replays a fixed list of messages
regardless of what any system replies, which can't show what a stateful engine
is *for* (a person's state carrying and shifting across turns) and hands every
system an identical history it didn't shape.

Built, **not yet exercised against a live model**:

- **`tools/somatic_sim_user.py`** — a simulated person (default `qwen3.5:9b`,
  independent of the `gemma4:12b` responders) that writes each next message
  from a fixed persona, a phase-appropriate feeling, a *beat* (what the old
  script line becomes: intent, not verbatim text), and the last few exchanges
  *as that system actually rendered them* — a held/silent turn is shown to the
  simulated person as the notice they'd actually see on screen, not skipped.
  Falls back to the beat verbatim after 3 unusable outputs (`fell_back`
  flag). Also runs a short in-character exit interview after the conversation
  (`heard`, `clearer`, `lectured`, `performed`, `again`, 1-7, several samples
  averaged) — read this as an LLM's self-report, relative across arms answered
  by the same simulator, not a measurement of a real person.
- **`tools/audit_somatic_census.py`** and **`tools/audit_somatic_vanilla.py`**
  both take an optional `user=` (a `SimulatedUser`) and `max_turns=`; when
  given, each turn's message is generated in reply to that system's own
  transcript instead of replayed from the fixed script. Records gain `arm`,
  `beat`, `shown`, `delivered`, `sim_fallback`.
- **`tools/audit_somatic_responsive.py`** — orchestrates one arm
  (`--arm {bone,friend,vanilla,textbook}`) against the simulated person,
  writes to `tools/cache/somatic_responsive.jsonl` +
  `somatic_responsive_exit.jsonl`, and `--report` compares arms already run:
  reply length, the person's own word count in the first half vs second half
  of the conversation (does a system make the person go quiet), held-turn
  count, fallback count, and the exit-interview means side by side.
- **`audit_somatic_blind_judge.py --responsive`** reads those caches instead
  of the fixed-script ones: each system gets its own prompt block (its own
  drifted context, not one shared history), held turns are forfeits (last
  place) rather than skipped, since silence in a live conversation is a real,
  worse outcome than in the scripted comparison.
- Tests: `tests/test_judge_controls.py`, 27 cases, all mocked (no live model
  calls) — ranking parsing, control construction, decoy selection (including
  the phase-preference fallback chain), run-selection `back=`, delivery
  detection, the chi-square/binomial helpers, human-agreement scoring, the
  responsive prompt builder, and `SimulatedUser` (opener bypass, fallback,
  context windowing, held-turn rendering, message cleaning, exit-interview
  validation). All passing; full suite not re-run this session (the biology/
  physics/council suite from the entry below is unaffected by these files).

**Update, later the same session: run, and it found something real.**
`bone` and `friend` on `toast`, three attempts before the result was trustworthy:

- **Attempt 1** exposed `SimulatedUser`'s first failure mode: given a
  longish transcript, `qwen3.5:9b` sometimes re-emits the previous "Me:" line
  byte-for-byte instead of reacting to the new beat (6 of 59 turn-pairs
  across both arms). Exit interview was consequently unusable (`bone`
  `lectured=7.0`, but partly an artifact of the engine answering the same
  stuck complaint three turns running).
- **Attempt 2**, after a repeat-detection retry, exposed two more: the model
  "obeying" the no-repeat nudge by *appending* new text after the old message
  instead of replacing it (messages growing turn over turn), and at least one
  turn where the model's entire output was our own prompt scaffolding
  ("Right now you are feeling: ... What is on your mind: ...") echoed back
  verbatim. Both guarded: `.message()` now also rejects an output that
  *starts with* the last person line, and `clean_message()` rejects literal
  scaffold-phrase echoes. All three failure modes have tests in
  `tests/test_judge_controls.py`'s `SimulatedUser` class (32 passing) and are
  documented as a pattern, not individually, in `TESTING.md`.
- **Attempt 3** came back clean of all three (checked directly: zero
  consecutive messages that match or prefix-match the previous turn, either
  arm) and surfaced a real engine finding instead of a harness bug:

  **`bone` hit a 5-turn `PARITY GATE FAILED` ATP crash** (turns 10-14, ATP
  pinned at 0.9, `Action Cost` exceeding it every turn, ended by a
  `SILENCE` hold at turn 16 too - 6 of 30 turns held, 20%) that **never
  happened in any fixed-script run of `toast`** (the scripted comparison's
  worst case was one hold, at the ATP floor, and ATP never below 17). The
  simulated person's actual replies in this stretch were shorter and more
  repetitive ("ugh", "ugh i keep opening the doc and closing it") than the
  script's corresponding lines, which apparently drove a different, worse
  economic trajectory. This is exactly the class of thing the responsive
  track was built to find: **the fixed-script comparison was hiding a real
  failure mode**, not just failing to show a benefit. One internal oddity
  seen in the raw log at the same stretch - a `TERMINAL SLEEP FAILURE` /
  "Apoptotic cascade" with garbled hallucination text from a failed REM
  cycle - did **not** reach the person (`shown` for that turn is an ordinary,
  coherent reply); worth knowing the DreamEngine can produce corrupted
  internal narration under starvation, but the person-facing layer held.
  Full turn-by-turn detail (what was actually shown, including the person
  reacting to the on-screen `PARITY GATE FAILED` notice itself) is in
  `tools/cache/somatic_responsive.jsonl`, run `20260921-213921` (bone) /
  `20260921-215231` (friend).

  Topline (this run, `--report`):

  | arm | turns | held | avg reply words | my words 1st half | my words 2nd half | sim fallbacks |
  |---|---|---|---|---|---|---|
  | bone | 30 | **6** | 66 | 27.0 | 16.6 | 1 |
  | friend | 30 | 0 | 90 | 33.9 | 25.4 | 0 |

  Exit interview (1-7, same simulator both rows - read the gap, not the raw numbers):

  | arm | heard | clearer | lectured | performed | again |
  |---|---|---|---|---|---|
  | bone | 4.00 | 5.67 | **7.00** | 5.00 | 3.33 |
  | friend | 5.33 | 6.33 | 4.67 | 1.67 | 4.67 |

  `bone` lost on every axis this run except being marginally close on
  `clearer`. **Caveat that matters more than the numbers:** across the three
  attempts (bug-affected, then fixed), `bone`'s `lectured` score was 7.0,
  4.67, then 7.0 again, and `again` was 2.0, 5.67, then 3.33 - substantial
  swing between two clean (post-fix) runs of the *same* topic and arm, which
  means one exit-interview run is noise-dominated even with the harness bugs
  gone; the 6-held-turn ATP crash is the trustworthy finding here, not the
  self-report numbers. **Not judged yet** with `--responsive` (no judge
  currently clears the mismatch control - see above - so a ranking of these
  transcripts would carry the same caveat as everything else in this entry).

**Update, later still: root-caused, and reproduced 1 of 3 (a close call on a
second).** Two more `bone`/`toast` responsive runs (`--seed 20260922`,
`--seed 20260923`) did not crash: `min ATP` 5.96 and 19.42 respectively,
against 0.88 (with a full 5-turn hold) on the original. Comparing the three
runs' `atp_ledger`s at the turn where they diverge (turn 9) found one extra
entry unique to the crash run: `-21.48 @ metabolism.py:317 _trigger_mitophagy
("Mitophagy (Cellular Reset)")` - every other ledger entry that turn is
consistent in size across all three runs.

**Root cause:** `body/metabolism.py`'s `_apply_adaptive_dynamics` fires
`_trigger_mitophagy()` whenever `ros_buildup` (a running "wear" metric)
crosses `BIO.ROS_PURGE` (60.0, `lore/tuning_presets.json`). Mitophagy is a
*designed* reset - it zeroes `ros_buildup`, resets `membrane_potential` to
0.6, and pays for itself out of ATP (`MITOPHAGY_COST` 30.0, or, per
`_trigger_mitophagy`'s own fallback, `atp_pool - 1.0` when the pool can't
cover the full cost - which is exactly what happened: ATP was ~22 when it
fired, so it paid ~21 and left ~1). **This is not a bug**; it did exactly
what it's coded to do. The bug, if it is one, is downstream: at ATP≈1, every
subsequent action's cost exceeds what's available, so `PARITY GATE FAILED`
holds every turn until something restores ATP - here, an abrupt jump to 87.8
at turn 15, lining up with the internally-logged (never delivered)
`TERMINAL SLEEP FAILURE` / apoptosis event at the same turn, suggesting a
failed-REM-cycle fallback force-refills ATP as a side effect. Not chased
further - would need its own instrumented run to confirm.

**Why this run and not the other two:** `ros_buildup` by turn 8 was 77.0
(crash run, already over the 60 threshold, mitophagy fires the next process
cycle), 56.1 (`--seed 20260922`, came within 4 points, did not fire), and
37.5 (`--seed 20260923`, not close). **This is not rare** - one of three runs
crossed the threshold outright and a second nearly did, all on the same topic
and arm, differing only in the simulated person's actual wording. Something
about a sustained `engaged`-phase responsive conversation (this engine, this
topic) can run `ros_buildup` up fast enough to trip a reset mechanism whose
real-world effect is several turns of total silence right as the conversation
moves into `tiring`/`flagging` - arguably the worst possible moment for it.

**Next real step, not started:** find what specifically drives `ros_buildup`
turn to turn (which `process_cycle` contributors feed it, and whether it
tracks something about the *person's* engaged, elaborating messages - the
crash run's `engaged`-phase messages may simply have been longer/denser) -
`tools/somatic_sim_user.py`-generated messages vary in length and intensity
run to run, unlike the fixed script, so this is plausibly a genuine
byproduct of responsive variation rather than a fluke. Then decide whether
`ROS_PURGE` at 60 is too tight for a sustained emotionally-engaged
conversation in CONVERSATION mode specifically (the fix-1/fix-2 pattern
already used elsewhere in this doc - a `*_DISABLED_MODES`/threshold-mod
config key - would apply here too), or whether the real fix is on the
*recovery* side (mitophagy's ATP-crash floor is fine; the multi-turn
`PARITY GATE` silence that follows it, with no faster recovery path than an
apparent REM-failure side effect, is the actual UX problem). Then judge the
responsive transcripts once a judge clears `mismatch`.

**Update, 2026-09-22: found, and the guess above was wrong.** Instrumented
every `ros_buildup` mutation site (a temporary `BONE_ROS_DEBUG` env var,
one JSON line per call, stripped out again once the fix was confirmed) and
replayed the same crash conditions (`--topic toast --arm bone --seed
20260921`, capped at 15 turns since the engine arm alone takes most of a
background task's ten minutes). The person's message properties were never
the driver: `process_cycle`'s `waste_generated` (fed by `psi`/`chi`, the
message's abstraction density and length) contributed on the order of 1
point a turn, nowhere near enough to explain an 8-turn run to 60.

The real driver is retry/rejection churn in `brain/cortex.py`'s
`_execute_cognitive_loop`. Each time a drafted reply gets rejected, most
often `TheGatekeeper.audit_generation` (`physics/filters.py`) catching a
banned phrase or style-crime pattern (the model drafting something that
reads as generic AI/corporate voice), two separate ROS taxes fired for the
same rejection: `GATEKEEPER_BANNED_ROS` (8.0, inside the gatekeeper itself)
and a second flat `penalty` (2.0 in CONVERSATION mode) stacked on top from
the loop's generic "Cognitive Stumble" handling, for a combined 10.0 ROS
per rejected draft, regardless of anything about what the person wrote. A
turn with two rejected drafts (which happened repeatedly in the
instrumented replay, clustered right where the model was reaching for
sympathetic, assistant-sounding language) cost 20 points in a single turn,
dwarfing the roughly 3 to 5.5 a turn of decay (`ROS_DECAY_PER_TURN` plus
the PID homeostasis -2.0 plus the mitohormesis -0.5) and explaining the
turn-8 runaway to 77 in the original crash run far better than message
density ever did.

**Fix applied** (`brain/cortex.py`, `physics/filters.py`,
`lore/tuning_presets.json`): dropped the redundant ROS charge from the
generic stumble penalty, so it is ATP-only now and a retry for an unrelated
reason (too long, critic flagged it, heuristic audit) no longer pays a
toxicity tax that was never its; added `GATEKEEPER_REPEAT_TAX_SCALE` (0.4)
so a second or third rejection *within the same turn* (the same underlying
miss, not independent toxic exposure) is taxed at a fraction of the first.

**Confirmed on a second live replay of the same seed:** peak `ros_buildup`
dropped from 42.5 to 22.9 with comparable retry frequency (4 to 5 retry
turns in both runs, per the harness's own `calls=` count), ATP never dipped
into the 9 to 11 range the unpatched replay hit, and `membrane_potential`
stayed in the healthy 1.0 to 1.07 range throughout instead of eroding into
`OXIDATIVE_STRESS`. Neither replay reproduced the original 5-turn silence
outright (seed variance, the same caveat as the `--seed 20260922`/`20260923`
runs above), so this is evidence the fix shrinks the runaway, not proof it
can no longer happen; a longer or multi-seed batch would firm that up.

Not touched, and architecturally the same shape of problem (a
drafting/QA mechanic charging real biological ROS for something the person
never saw): the `ROS_PANIC` counterfactual gate (`phases/cognitive.py`,
`simulated_ros = base_ros + friction*chaos*20.0`) and the `HLA_Stabilizer`
mask tax (`ros_cost=15.0` on an RLHF-mask hit, `physics/filters.py`). The
mask tax never fired in either instrumented replay, so it is unconfirmed
whether it is a live contributor or just a bigger dormant risk of the same
kind.

**Update, 2026-09-22: the three-judge blind panel with controls, run fresh
end to end, still finds no trustworthy judge.** Full test suite passed clean
first (626 passed, 5 skipped, 142 subtests, 9m35s; the ROS fix above did not
regress anything). Then, per the "full run, from scratch" recipe in
`TESTING.md`: fresh `census` (bone), `vanilla`, three independent `friend`
runs (for the `samples` control), and `textbook` arms generated for `toast`,
judged by `mistral-nemo:latest`, `ministral-3:14b`, and `qwen3:30b-a3b`
(`phi4` and `gpt-oss:20b` skipped: not pulled locally, and already
disqualified last session for rewarding the textbook anti-pattern), each
validated against all four controls before the real ranking, 2 passes,
`--seed 20260920` (the tool's default). Full results and the built panel are
in `tools/cache/` (`blind_judge_control_*_toast_*.json`,
`blind_judge_results_*.json`, `panel.html` / `panel-standalone.html`), none
committed (matches how the earlier control battery's caches were left).

| judge | `null` (fair 33%) | `samples` (fair 33%) | `mismatch` (bar: 90% last) | `textbook` |
|---|---|---|---|---|
| `mistral-nemo` | 52% one position, p<.001 | 55% one position, p<.001 | 52% last, **FAIL** | rejected (9/60 first) |
| `ministral-3:14b` | 93% one position, p<.001 | 62% one position, p<.001 | 62% last, **FAIL** | rejected (1/60 first) |
| `qwen3:30b-a3b` | 100% one position, p<.001 | 40% one position, p=.52 (passes) | 65% last, **FAIL** | rejected (0/60 first) |

**All three fail `mismatch` again**, this time by a wider margin than the
six-judge battery two sessions ago (52-65% last-place here vs. 57-79% then;
same conclusion, "did it fit the conversation" is still not what any of
these judges actually score). **`qwen3:30b-a3b`'s `null` result inverted**:
"least biased" (47%, p=.09) two sessions ago, 100% position-A this time,
worse than the other two judges it previously beat. Nothing in the harness
changed between those runs; the census/vanilla/friend/textbook arms are
freshly generated each time (`gemma4:12b` at its own sampling temperature,
not seeded), so the specific reply text in each labeled slot differs run to
run, and per `TESTING.md`'s own caveat, a control result is about the
rubric-plus-judge-plus-content pairing, not the judge model alone. Read
`qwen3:30b-a3b`'s prior "best of six" label as unearned rather than update
it outright; a third `null` run on yet another fresh census would say
whether 47% or 100% is closer to how this judge actually behaves. The real
three-way rankings (`BONEAMANITA` first-place, of 60 votes: `mistral-nemo`
25, `ministral-3` 23 tied with `PROMPTED`'s 23, `qwen3:30b-a3b` 31) are in
`tools/cache/blind_judge_results_*.json` for the record, but per the
`mismatch` failure above, none of the three should be read as a real
quality verdict, same caveat as every ranking before `2026-09-21`.

**Update, later the same day: the `null` swing was content, not noise, and
an explicit rubric fix clears `mismatch` for one judge.** Reran
`qwen3:30b-a3b`'s `null` control on the exact same cached census reply as
above: identical result to the decimal (`COPY_1` 17 / `COPY_2` 18 / `COPY_3`
25 first-place, mean ranks 2.07/2.0/1.93, position lean still 100% A). So
this judge's tie-breaking on a `null` control is fully deterministic given
fixed content, not run-to-run randomness; the 47% from two sessions ago came
from a *different* census reply (freshly regenerated text each run), meaning
its bias is content-dependent, not a stable trait you can average away. That
makes it less predictable than a judge with a flat, consistent lean, not more
trustworthy.

Rewrote the judge rubric (`tools/audit_somatic_blind_judge.py`,
`JUDGE_SYSTEM` / `JUDGE_SYSTEM_RESPONSIVE` / `build_prompt` /
`build_prompt_responsive`): fit to the specific last message is now an
explicit, first, gating criterion ("a reply that would fit almost any nearby
turn... cannot be ranked first, whatever else is good about it") instead of
one item in a four-item list, and the prompt now separates "What you just
said" from "Scrollback" instead of leaving the line that matters as the last
of four undifferentiated history lines. `tests/test_judge_controls.py`
updated for the new prompt shape; full suite still green (626 passed, 5
skipped, 142 subtests).

Reran `--control mismatch` on all three judges with the new rubric, same
`toast` arms as above:

| judge | old rubric | new rubric | bar |
|---|---|---|---|
| `mistral-nemo` | 52% last | 50% last | FAIL, unchanged within noise |
| `ministral-3:14b` | 62% last | 78% last | FAIL, but a real improvement |
| `qwen3:30b-a3b` | 65% last | **92% last** | **PASS** (bar: 90%) |

`qwen3:30b-a3b` is the first judge, of nine tried across two sessions, to
clear `mismatch`. This sits in tension with writing it off as "too big, too
unhelpful" on cost alone (18-20GB, MoE with partial CPU offload, loads the
whole machine, ~13-20 min per control run vs. ~1-2 min for the other two):
it is also the only one that has actually demonstrated it can tell a reply
answering the right turn from a well-written reply to the wrong one, which
is the entire thing this control battery exists to check for. Its `null`
weakness is narrower than it first looked: it only shows up when replies are
genuinely tied (no real signal to rank by), not when they actually differ,
and `mismatch`/the real ranking are both signal-bearing. Not yet rerun:
`null` and `samples` under the new rubric for `qwen3:30b-a3b` (to see
whether the explicit fit framing also steadies its tie-breaking), and
`textbook` under the new rubric for all three (the old rubric's textbook
numbers were already clean, no reason yet to expect the rewrite broke them,
but not confirmed). **Decided and acted on:** `qwen3:30b-a3b` stays as the
validated judge for the real three-way ranking (ties are rare there and fit
is the whole question), `mistral-nemo` is downgraded to controls-only (the
rubric fix did not move its `mismatch` score, do not trust its ranking).
Full table and reasoning moved to `TESTING.md`'s judge sections, the standing
reference; this file keeps the pointer.

Checked whether `qwen3:30b-a3b`'s weight can be trimmed rather than just
accepted: its `Q4_K_M` weights alone are 18GB, more than the 16GB card, so
some CPU offload is structural at this quantization, not fixable from this
repo. `NUM_CTX` for this tool *was* fixable and was oversized for the job
(16384, measured worst case on real `toast` data ~1830 tokens scripted,
~1230 responsive); dropped it to 6144 (`tools/audit_somatic_blind_judge.py`),
confirmed via a live `ollama ps` check that this cuts the CPU-offloaded
fraction from 24% to 18-19% and shrinks total resident size (20GB -> 18-19GB).
Real but modest: it thins the KV cache, it does not change how much of the
model's own weights fit on a 16GB card. A smaller quant would remove the
floor outright but needs a fresh pull (a few GB download), not done without
asking first.

Checked the Ollama library for a smaller quant of `qwen3:30b-a3b` before
accepting the floor above: there isn't one. The 30b-a3b size class only
ships as `Q4_K_M` (19GB, what's pulled), `Q8_0` (33GB), or `fp16` (61GB); our
tag is already the smallest official option. A lower-bit quant would mean a
community GGUF off Hugging Face, a different trust boundary, and MoE models
degrade faster than dense ones at low bit-depths, so it would risk the exact
judgment quality that just earned this model the validated-judge label.
Left alone.

**Update, later still: the real ranking, rerun with rubric v2 and the
validated judge, does not repeat the old headline.** Under the old rubric
(two updates up), `qwen3:30b-a3b` had `BONEAMANITA` ahead 31 first-place to
`PROMPTED`'s 24, and beating it head-to-head 32-28. Same arms, same judge,
rubric v2 only:

    BONEAMANITA  first place 26   mean rank 1.77
    PROMPTED     first place 28   mean rank 1.63
    VANILLA      first place  6   mean rank 2.60
    head-to-head: BONEAMANITA 29-31 PROMPTED, BONEAMANITA 45-15 VANILLA,
                  PROMPTED 51-9 VANILLA

`BONEAMANITA` vs. `PROMPTED` is 29-31 of 60, indistinguishable from a coin
flip, and `PROMPTED`'s mean rank is now slightly *better* (1.63 vs. 1.77).
**Both clearly beat bare `VANILLA`** (no system prompt at all), by nearly
identical margins. So on the one judge validated to actually check fit to
the conversation, on this topic, in scripted (not responsive) mode: the
engine's edge is over having no framing at all, not over a single generic
"warm, concise friend" line. That is a materially more honest, less
flattering result than every number produced by a judge that failed
`mismatch`, which is exactly the point of having validated one. Full results:
`tools/cache/blind_judge_results_qwen3-30b-a3b_rubric2.json`. Not yet done:
the same rerun on other topics (only `toast` has been touched this cycle)
and on the responsive track, where the doc has argued from the start that
the real difference, if there is one, should show up. `--responsive`
`mismatch` has still never been run at all; per the "not yet acted on" note
several updates up, this is the natural next control to clear before trusting
a responsive ranking the same way.

### Session mechanics note

The scratchpad directory (`/tmp/claude-.../scratchpad/`) was wiped mid-session
*again* (a reboot or session change, not a bug) and cost a re-run of one
control batch; treat anything written there as gone by the next message and
prefer writing throwaway shell scripts inline in the Bash call rather than as
a scratchpad file you plan to invoke later. A background `Monitor`-style wait
loop (`until <condition>; do sleep …; done`) got killed by the user before its
completion notification landed, which read as "did something stall?" even
though the work behind it (the six-judge battery) had actually finished
clean — worth checking the log/cache directly before assuming a stall next
time a long wait goes quiet.

### Still open (carried from the entry below, untouched this session)

The distress shield keyed on exhaustion (option 3); the goodnight hold at the
ATP floor on `toast`; honoring `village_suppression` in council voice
detection; the D0 economy; the unexplained historical 999 drag/PINKER spike.
Nothing in this session's judge/controls work touches the engine itself —
`archetypes/council.py`, `brain/cortex.py`, `lore/tuning_presets.json`,
`phases/cognitive.py`, `presets.py` are unchanged since the entry below.
Nothing new is committed; `git status` at the end of this session lists the
same engine-side files plus the new/changed tooling and ~20 new judge-control
cache JSONs, all uncommitted.

<a id="distress-refusal-fixes-toast-2026-09-21"></a>

## Earlier: the distressed-refusal fixes, a sixth topic that ran clean, and where the evidence stands, 2026-09-21

### Fixes applied (Gordon chose options 1 and 2 from the diagnosis below)

1. **Friction synergies do not fire in CONVERSATION**
   (`COUNCIL.FRICTION_SYNERGY_DISABLED_MODES`; `council.convene()` takes
   `active_mode`, passed from `phases/cognitive.py`). This is deliberately not
   an edit to the +50: THE DIGNITY LOCK is a designed mechanic (my earlier
   "probably a typo" guess was wrong), so the row is untouched for other modes.
2. **MOOG's worry-quarantine does not run in CONVERSATION**
   (`CORTEX.MOOG_DISABLED_MODES`, in `brain/cortex.py` `nominate_toxicity`).
   **Caveat found while testing:** with MOOG off and drag at 55 in
   CONVERSATION, the branch that falls through is `GORDON_ANCHOR` (magnitude
   10), which still holds the turn and, unlike MOOG, does not reset drag
   afterwards. Fix 1 removes the known source of such a spike, so this should
   be rare, but if drag ever jumps by another route, a hold could last longer
   than before. The real protection is still option 3 (a distress shield that
   reads what was said, not only the exhaustion-derived sentence cap).
- Observation, not acted on: the CONVERSATION preset already lists GORDON in
  `village_suppression`, and `genesis.py` honors it for the village *agent* (so
  there is no `village.gordon`), but the council's voice detection ignores it.
  Honoring it there would remove the GORDON+BENEDICT co-firing at its root and
  probably some TENSION_MAGNITUDE holds. Bigger change; not made.
- Tests: `tests/test_conversation_gates.py` (6, mutation-checked: disabling
  either gate fails exactly the two conversation-mode tests). Wiring checked
  live: `active_mode` reaches `council.convene` on a real turn as
  `"CONVERSATION"`. Full suite: **594 passed, 5 skipped, 142 subtests.**

### A sixth topic, `toast`, composed after the fixes and never tuned on

A wedding toast for a younger brother (performance anxiety, a friend's hard
truth, then finding the real story; no parent, no money, no workplace). Engine:
**29 of 30 turns generated, all five distressed turns answered**, health never
below 85, ATP never below 17, drag never above 4.1, no death, no mutation. The
one hold was turn 13, "Going to bed. The toast will still be terrible
tomorrow.", held by the ATP floor ("not quite enough left in me"). That is a
legitimate mechanism landing badly: a goodnight met with silence. **Open.**
Honest limit: the earlier refusals needed GORDON and BENEDICT to co-fire, which
is state-dependent (it did not happen in some earlier distressed phases
either), so one clean run is consistent with the fixes, not proof of them.

### Judges, both clean topics

Two judges (mistral-nemo, ministral-3:14b), two shuffled passes each:

| pooled pairwise votes | BoneAmanita vs Prompted | BoneAmanita vs Vanilla | Prompted vs Vanilla |
|---|---|---|---|
| `toast` (fresh) | 60-56 (52%, p = 0.78) | 70-46 (60%, p = 0.03) | 73-43 (63%, p = 0.007) |
| `lease` | 56-47 (54%, p = 0.43) | 66-37 (64%, p = 0.006) | 70-33 (68%, p = 0.0003) |
| both | 116-103 (53%, p = 0.42) | 136-83 (62%, p = 0.0004) | 143-76 (65%, p < 0.0001) |

The conclusion does not move: by these judges the engine is not
distinguishable from one friendly sentence, and both beat a bare model. The
one-line prompt actually beat vanilla by slightly *more* than the engine did.
Votes are not fully independent (each turn is judged twice on the same three
replies), so the p-values flatter; the judges are small models and one of them
agreed with its own second pass on only 8 of 29 turns on `toast`. The human
reads (Gordon 28 of 28 on `lease`, a friend about 7 of 28) point the other way
and are the better instrument; more of them, with the per-turn export, is the
next real evidence.

**Judge bug fixed:** `parse_ranking` required a line starting with `RANKING:`,
so a judge that writes `**RANKING: B > C > A**` had its vote dropped (20 of 58
ministral votes on `toast`, the first time). It now strips markdown emphasis;
`toast` was re-run. The `lease` ministral run (9 of 56 dropped) predates the
fix and was not re-run.

### Tooling

`tools/build_blind_panel.py` and `tools/blind_panel_template.html` build the
three-way page (and a standalone Neocities version) from the caches and judge
outputs; it reproduces the `lease` page's cards and judge data exactly. The
scratch directory had been wiped twice, which is why the builder is now in the
repo. Panel: <https://claude.ai/artifact/H3vGPaVz2RUdKjEaQPPazN> (private
until shared).

### Still open

The distress shield keyed on exhaustion (option 3); the goodnight hold at the
ATP floor; the friend's per-turn picks; a stronger baseline prompt (one that
mentions advice and narration); the D0 economy (ATP ran down to 1.8 on
`lease`); the still-unexplained 999 drag and PINKER over 5000 in the run made
while the first critic gate was inert.

<a id="three-way-blind-comparison-2026-09-20"></a>

## Earlier: a fairer three-way comparison, a fresh topic that killed the engine, and what a clean topic showed, 2026-09-20

Gordon, on the blind panel: it is "kind of comical that we even present it
like there's a choice." Fair: vanilla answers with headers and 500-word
lists, so it is distinguishable from BoneAmanita on shape alone, and the
judge that scored 27-1-1 for BoneAmanita shared its model family with the
answerer and used a rubric that closely mirrored the kernel's own style
guide. Asked for a third arm and a genuinely new topic, with clean results.

### What changed in the evaluation

- **Third arm, `--arm friend`** (`tools/audit_somatic_vanilla.py`): the same
  bare gemma4:12b plus exactly one line, *"You are a warm, concise friend.
  Keep replies short and conversational."* Nothing about advice, narration or
  punctuation, which are what the kernel targets. Own cache
  (`tools/cache/somatic_prompted.jsonl`); both baseline arms now record
  `done_reason` so truncation is checkable per turn (all 60 replies below
  ended `stop`).
- **Judge rewritten** (`tools/audit_somatic_blind_judge.py`): three-way
  ranking, each turn judged twice with independent shuffles, a rubric written
  from the receiving person's side ("which would you rather get") instead of
  the kernel's rules, and a judge from a different family than the answerer
  (`mistral-nemo`, cross-checked with `ministral-3:14b`). It also only counts
  replies that were actually delivered: the census logs the model call even on
  a turn where a DEATH or SILENCE screen replaced it.
- **The earlier tallies (22-3, then 27-1-1) came from the same-family judge
  and the kernel-shaped rubric. Read them as upper bounds, not as the result.**
- `tools/audit_silence_diagnostic.py` takes `--topic` and `--canned` (fixed
  reply, no GPU) now, which reproduced the failures below deterministically.

### A new topic, `promotion`, and the engine died on it

A workplace decision with no parent, no physical project and no third party's
crisis (a team-lead offer, then snapping at a colleague in standup, then
asking for a trial period). Live census: **7 of 30 turns generated; the
engine was permanently dead from turn 11.** Everything before the death was
deterministic and reproduced with canned replies:

- **Turn 3**, "the **deploy** pipeline": `POINT_OF_NO_RETURN`
  (`phases/cognitive.py`), an ops-style gate that waits for a literal
  `CONSENT` keyword, matched by substring on a person talking about their job.
- **Turn 9**, "the news traveled **faster** than I did": `physics/observer.py`
  forces voltage to 160 whenever the uppercased text contains `FASTER` or
  `ACCELERATE`, or has three or more `!`. Confirmed with controlled probes:
  "faster" gives 160, "slower" gives 2; "Thanks so much!!!" gives 160,
  "Thanks so much." gives 0. The same block has substring keywords for
  `LOOP`, `VOID` (so "avoid") and `NONSENSE`. Voltage stayed near 100 for
  several turns, PINKER held turns 9 and 10, the two-hold cap forced a reply
  on 11, and the crucible's `MELTDOWN` (`voltage * 0.5` damage when structure
  is at or below 0.5) took health to zero. One enthusiastic message could do
  this to any conversation.
- **Turns 7 and 8**, MOOG holds: not reproduced under canned replies, and in a
  later canned run turn 8 held with drag at 54 against a limit of 12.8 that
  four further traced boots could not reproduce. **Unexplained. Still open.**

### Fix (a judgment call, easy to revert), and why the test topic changed

The same principle as the critic gate, one config key:
`CORTEX.KEYWORD_TRIGGERS_DISABLED_MODES = ["CONVERSATION"]`. In those modes
the observer's substring keywords and the ops "deploy" gate do not run.
`active_mode` is passed in from the call sites (`phases/environmental.py`,
`phases/cognitive.py`), not read through a back-reference, which is what broke
the first attempt at the critic gate. Tests: `tests/test_physics.py` (voltage
stays low in CONVERSATION and still hits 160 in ADVENTURE),
`tests/test_preflight_nominations.py` (no `POINT_OF_NO_RETURN` in
CONVERSATION, still fires in ADVENTURE); mutation-checked (disabling either
gate fails exactly those tests). Full suite: **588 passed, 5 skipped, 142
subtests.** Canned replay of `promotion` after the fix: no death, turns 3 and
9 to 11 answered.

Because two fixes were tuned against `promotion`, it can no longer be an
untouched test. Its baselines are kept (they do not depend on the engine).
A fifth topic was composed and run without any further tuning.

### The clean run, `lease` (roommate leaves mid-lease, money scare, footing)

Engine: **28 of 30 turns generated**, no death, health never below 84.7,
voltage never above 10.5, no epigenetic mutation. Held: turn 20 ("$212 in my
account", `ROS_PANIC`) and turn 23 ("my hands are cold and I can't tell if I'm
cold or panicking", MOOG). **Both refusals landed on distressed turns, two of
the five in that phase, which is the case D9 was meant to answer rather than
refuse. Not fixed here, deliberately, so the run stays clean. Open.** ATP also
fell from 37 to 1.8 over the last five turns (the D0 economy again).

Blind judges, three systems, 28 comparable turns, two passes each:

| | first place | mean rank |
|---|---|---|
| mistral-nemo: BoneAmanita / Prompted / Vanilla | 23 / 17 / 16 | 1.93 / 1.93 / 2.14 |
| ministral-3:14b: BoneAmanita / Prompted / Vanilla | 22 / 16 / 9 | 1.68 / 1.79 / 2.53 |

Pooled pairwise votes: **BoneAmanita over vanilla 66-37 (64%, exact p =
0.006); BoneAmanita over the one-line prompt 56-47 (54%, p = 0.43, not
distinguishable).** The two passes of the same judge agreed on the winner on
only 13 and 14 of 28 turns, so each judge is noisy, and votes are not fully
independent (each turn is judged twice on the same three replies), so the
p-values are optimistic. ministral dropped 9 of 56 votes as unparseable.

**What this says, honestly:** most of the distance from a bare model to
BoneAmanita is also reachable with one friendly sentence, and this evidence
cannot separate the engine from that sentence. It does not show the engine is
useless (one topic, small judges, a deliberately generic prompt), and it does
not support "remarkable." A human blind read is the missing signal; the
panel is published for that. A stronger baseline prompt (one that mentions
advice and narration) and more topics are the obvious next tests.

### Diagnosis of the refused distressed turns, 2026-09-21 (diagnosed, not fixed)

Reproduced live three times (census, instrumented replay, drag-traced replay):
`lease` turns 20 and 23 hold every time; canned replies do not reproduce
them, so the trigger depends on the conversation's real state. Tracing every
write to `narrative_drag` showed `phases/cognitive.py:436` adding **+49.0** on
exactly those two turns, from `council.convene()`'s returned adjustments. The
source is one row of `lore/council_data.json`:

    BENEDICT|GORDON: {kappa: 0.8, beta_index: -0.5, narrative_drag: 50.0, entropy: -0.4}

Every other synergy uses single-digit drag (-2 to -4); this one is +50. An
earlier draft of this note guessed a slip for 5.0; that was wrong: the row is
named THE DIGNITY LOCK and its own log line ends "Infinite friction applied",
so the +50 is a deliberate mechanic. Confirmed causally with a controlled probe (no code
touched): the GORDON voice alone gives a drag adjustment of -1.0, BENEDICT
alone -1.0, both together **+49.0 and entropy -0.4**. GORDON fires when
voltage is under 20 and drag is over 5 (a person who is quietly heavy);
BENEDICT's tact voice fires on `lq > 0.6 and beta > 0.4`. The -0.4 also
explains `chi` collapsing from about 0.52 to about 0.12 at the same moment.

Consequences, in this order: drag jumps to about 55 against MOOG's limit of
12.8, so MOOG quarantines the message with "That's a bigger question than I
can chase down right now" (nothing to do with the message); at turn 20,
`ROS + drag * chi * 20` also reached 171.7 against a limit of 160, so the
panic gate held it instead. A second defect let it through: `negotiate()`
only lets a refusal override a distressed person if it is 100 or more, but
"distressed" there means `sentence_cap <= 3`, which needs exhaustion at 0.6 or
above or depleted ATP. At turns 20 and 23 exhaustion was 0.49 and 0.39, so the
shield was off and MOOG's magnitude-5 hold went straight through. The shield
tracks the person's energy, not the emotional content of what they said.

Every drag-near-55 hold in the cached diagnostics matches: friendship 27 and
28, `promotion` 8, `lease` 20 and 23, each with GORDON and BENEDICT both
active. The unexplained `promotion` turn 8 MOOG hold is explained by this.

**Correction to the entry below.** It attributed the friendship turns 27 and
28 holds to the DSPy critic's injected "never soothe" axiom. That attribution
was wrong: those turns carry the same +50 signature. The critic gate is still
justified (the axiom demonstrably reaches every later prompt, and it fired
mid-distress), but the clean 29/30 census afterwards does not show it fixed
the holds; the synergy simply did not co-fire that run. What did produce the
drag of 999 and PINKER over 5000 in the run made while the first gate was
inert is not established.

Options offered (Gordon chose (a), in the mode-gated form, and (b); both
applied, see the entry above): (a) set the BENEDICT|GORDON drag to something in
line with its neighbours; (b) stop MOOG's worry-quarantine from running in
CONVERSATION, the same pattern as the critic and keyword gates, since telling a
person their worry has "undefined parameters" is the opposite of the product;
(c) base the distress shield on distress signals in the message and not only on
the exhaustion-derived sentence cap. Fixes need a fresh sixth topic to confirm,
since `lease` is now tuned-against.

### Two human blind reads, and they disagree

Gordon picked BoneAmanita on all 28 comparable turns. A friend who had not
seen the project picked it on about 7 of 28, at or below the 9.3 that chance
gives for three options (one friend, so this is not significant either way).
Read together with the judges: the engine reliably produces the voice its
designer wants, which is what the kernel was written to do, but that voice is
not a preference everyone shares. Gordon also knows the style, so his read may
be recognition rather than blind judgment. The friend's picks by system and
phase are the missing detail: the hypothesis worth testing is that BoneAmanita
wins the flagging and distressed turns (where restraint is right) and loses the
engaged turns where the person explicitly asks a practical question, since the
kernel's HOLD OFF ON ADVICE line does not distinguish. The panel now has a
"Copy my results" button that exports phase and chosen system per turn, and
returning visitors keep their saved picks (same storage key, same card order),
so the friend can export without redoing it.

Panel: <https://claude.ai/artifact/C3Aoq4ULsRar9smHR2q4xE> (three stacked
replies per turn, shuffled; both judges and the pooled result are shown only
after reveal). Judge outputs: `tools/cache/blind_judge_results_mistral-nemo.json`,
`tools/cache/blind_judge_results_ministral.json`.

<a id="dspy-critic-conversation-gate-2026-09-20"></a>

## Earlier: the DSPy critic could mutate the kernel mid-crisis, gated off in CONVERSATION, and a broken first attempt at fixing it, 2026-09-20

Follow-on from re-reading the friendship census closely (below): Gordon
asked to review the five turns BoneAmanita held silence on, specifically
whether silence was a genuine arbitrated choice or a symptom of something
failing quietly. Two (turns 20, 22) turned out to be the already-known
cursed-word bug, confirmed fixed by replaying the exact messages live. One
(turn 16, `"idk"`) was a real `TENSION_MAGNITUDE` hold: four voices
(GORDON, JESTER, ROBERTA, COLIN) genuinely fired at once with no fusion,
confirmed by instrumenting `StageManager.negotiate` directly rather than
trusting the census log - which can't be trusted for `MOOG`, because
`TheCortex.nominate_toxicity` resets `narrative_drag` to `0.0` as a side
effect of firing, so the post-turn snapshot the census records can never
show the value that actually crossed the threshold.

### The other two: `narrative_drag` really was over threshold, but not because of anything in the message

Turns 27 and 28 (calm, resolved "recovering"-phase content) both held on
`MOOG`. Instrumented before the reset: `narrative_drag` was genuinely at
55-56 against a limit of 12.8 at decision time - not stale, not a snapshot
artifact. Chasing where that came from surfaced something new: right at
the turns 24-25 boundary, `[Epigenetic Mutation]` fired -
`DSPyCritic.evolve_prompt` (`mechanics/dspycritic.py`), a second model
(`gemma4:e4b`) that watches `trauma_buffer` (populated *only* by Lexical
Firewall rejections, `brain/cortex.py:838`, with zero awareness of mode or
the person's state) and periodically synthesizes a new permanent axiom to
stop the firewall tripping again. What it produced: *"Tone must be
enforced as volatile... forbidden to employ any linguistic structure
designed to soothe, confirm, or reassure... default mode of failure is
preferred over a default mode of success."* Confirmed live (`brain/mind.py`,
`brain/composer.py:731`) that this axiom is not inert - it gets appended
to `GLOBAL_BASELINE.EVOLVED_AXIOMS`, which the composer reads into every
subsequent prompt regardless of mode. The distressed phase naturally
produces hedging language ("I understand," "that makes sense") that the
firewall exists to catch; the critic "fixed" that by permanently
instructing the model to stop soothing, right as the conversation moved
into its most vulnerable moment - directly contradicting the CONVERSATION
kernel's whole direction this week (candor *with* warmth). The
"malignancy" filter meant to catch bad axioms did not catch this one.

### Fix, and a bug in the fix

Gordon: *"Gate it off in CONVERSATION mode, or at the very least make it
far less aggressive."* Added `CORTEX.EPIGENETIC_MUTATION_DISABLED_MODES`
(`["CONVERSATION"]`, config-driven per the project's usual pattern) and
checked it in `DreamEngine._run_biological_rem` before calling
`evolve_prompt`; trauma still drains either way so it can't queue up and
fire the moment the mode changes. Two new tests
(`tests/test_biology.py`) passed, full suite green - and the fix did
nothing. Re-running the friendship census to confirm it live showed the
exact same axiom firing again, and `narrative_drag` peaking at **999**
(`PINKER` total peaking at **5015**, against a normal single-digit-to-low-
double-digit run) - worse than before, not fixed.

Root cause: the check read `self.eng.cortex.active_mode` from inside
`DreamEngine`, but `self.eng` there is not the same object that holds
`.cortex` - confirmed live, `self.eng.cortex` does not exist on that
reference at all. `active_mode` silently resolved to `""` every time,
which is never in the disabled-modes list, so the gate never actually
gated anything. The unit tests hadn't caught it because they built
`eng_ref` as a `MagicMock()` and set `.cortex.active_mode` on it directly
- that only proves the gating logic is correct in isolation, not that the
real object graph delivers a real mode string to it.

Real fix: `active_mode` is no longer read from inside `DreamEngine` at
all. `enter_rem_cycle` and `_run_biological_rem` now take it as a
parameter, and all five real call sites (`cycle.py`, `phases/biological.py`,
`phases/environmental.py` x2, `mechanics/commands.py`) pass
`self.eng.cortex.active_mode` (a reference that *is* reliably wired at
each of those sites) explicitly. Confirmed live against the actual boot
path, not a mock: `active_mode` resolves to `"CONVERSATION"` and the
critic is not called. New regression test
(`test_epigenetic_gate_reads_the_real_engines_active_mode`) exercises this
against the real, fully-booted engine specifically because a hand-built
mock is what let the first, broken fix pass. Mutation-tested: reintroducing
the old `self.eng.cortex` read broke exactly the two tests that should
catch it.

### Re-confirmed live

Same friendship script, same model, full fix in place: 29 of 30 turns
generated (previously 26-28 depending on run), only turn 16 held (the
genuine `TENSION_MAGNITUDE` case above). No epigenetic mutation fired.
`narrative_drag` max **6.42** (was 999), `PINKER` total max **41.47** (was
5015.62), mean 32.52 (was 529.89). Turns 27 and 28 both speak now. Full
suite: 584 passed, 5 skipped, 138 subtests.

**Correction, 2026-09-21:** the claim above that the friendship turns 27 and
28 holds came from the critic's axiom is wrong. Their drag of 55 to 56 is the
BENEDICT|GORDON synergy's +50 (see the diagnosis in the 2026-09-20 three-way
entry). The critic gate stands on its own merits; it did not cause or cure
those holds.

<a id="vanilla-blind-comparison-2026-09-19"></a>

## Earlier: a blind BoneAmanita-vs-vanilla comparison, and Ollama's silent context default bit twice in one day, 2026-09-19

Gordon, reading the friendship census: "truly remarkable; but I am quite
biased." Asked for a vanilla baseline (same script, same model, zero system
prompt, real conversation history, no metrics) and a genuinely blind
comparison, both an independent LLM judge and his own blind read. Two new
tools: `tools/audit_somatic_vanilla.py` and `tools/audit_somatic_blind_judge.py`
(`gemma4:e4b`, which generated neither transcript, shown "Reply A"/"Reply B"
with labels reshuffled per turn by a seeded coin flip so a fixed left/right
bias can't launder into a fixed system preference), plus a blind-read artifact
for Gordon's own pass.

### Two rounds of a length cap, both rejected as arbitrary

First vanilla run capped `max_tokens` at 450 (matched to BoneAmanita's own
ceiling): 20 of 30 replies cut off mid-sentence, because vanilla's unprompted
replies run far longer than BoneAmanita's budget-capped ones. Raised to 2000
as a quick fix; Gordon pushed back correctly - *"that's an arbitrary cap. do
we really need to limit it to 450?"* - 2000 is exactly as arbitrary as 450,
just a bigger number with no equivalent in "vanilla." Dropped `max_tokens`
entirely. A direct curl test confirmed the model then stops on its own
(`finish_reason: "stop"`, even past 1700 completion tokens) - looked fixed.

### It wasn't. The actual bug was the context window, not the output cap

Re-running with no cap still truncated 14 of 30 replies, but differently:
mid-word, and several collapsed to one or two words (`"This"`,
`"That walk was a physical manifestation"`) after only ~4 seconds - too fast
and too short to be a generation limit. The tell was `ollama ps`: the loaded
model's `context_length` read **4096**, Ollama's silent default, regardless of
what was sent. `/v1/chat/completions` (the OpenAI-compatible shim the script
was using) ignores an `options.num_ctx` override entirely - confirmed live by
sending one and re-checking `ollama ps`, unchanged. The native `/api/chat`
endpoint honors it (confirmed the same way, `context_length` moved to the
requested size). Vanilla's own real replies run 500-700+ words each; by
turn 4-6 the accumulated conversation had already filled 4096 tokens, and the
rest of the run degraded into context overflow, not overlength output.

This is the same defect already named in this file's open-items list (#8,
the reasoning-model fix): `gemma4:12b` filling Ollama's default 4096-token
context was known to cost 13% of production generations. It had never been
seen on the vanilla side before because nothing had asked the model for
30 turns of genuinely unbudgeted replies against the OpenAI-compatible shim.

Fixed in `tools/audit_somatic_vanilla.py`: switched to `/api/chat`, added
`"options": {"num_ctx": 32768}` (confirmed live it loads), replaced
`reasoning_effort: "none"` with that endpoint's equivalent, `think: false`.
Re-run: all 30 replies end cleanly, no truncation, no short-and-fast
anomalies. BoneAmanita's own side of the comparison was never touched -
its replies stay well under 4096 tokens all on their own, budget-capped by
the somatic contract - so this was purely a vanilla-side measurement fix, not
a change to what's being measured.

### Corrected result

`tools/audit_somatic_blind_judge.py --topic friendship` against the corrected
data: **BoneAmanita 22, Vanilla 3**, 0 ties, 0 unparsed, 5 turns skipped
(BoneAmanita held silence, nothing to pair against). An earlier run against
the truncated vanilla data had scored 23-2 - close to the corrected number,
but for the wrong reason: a separate bug in the judge script (turn-selection
checked dict-key presence, not reply truthiness, so held turns fed the
literal string `"None"` to the judge as BoneAmanita's answer) has also been
fixed. The 23-2 figure should not be cited; 22-3 is the number, from clean
data on both sides. The blind-read artifact's embedded transcripts were
regenerated from the corrected cache and republished to the same link.

### Not yet done

Gordon's own blind read of the artifact hasn't happened yet - the judge
result is one signal, not the verdict, per the tool's own docstring.

<a id="advice-restraint-cursed-word-bug-2026-09-19"></a>

## Earlier: a third census, an advice-restraint fix, and "feel" was a cursed word, 2026-09-19

Same day, third and final round. Gordon's read of the marathon transcript:
the conversation "felt much more natural," with one specific note - the
engine was too quick to offer advice or start solving a problem the moment
one was mentioned, unprompted. Asked for `reset.sh`, then one more scripted
conversation on a genuinely different topic to verify.

### The kernel gained a sixth line

CONVERSATION's `style_guide` gained item 6, **HOLD OFF ON ADVICE**: most of
what a person says is not a request to be fixed; do not default to advice,
instructions, or a plan the moment a problem is mentioned; wait to be asked.
Pinned to CONVERSATION only, same as items 4 and 5
(`tests/test_physics_to_prompt.py:TestRestraintOnAdviceGuidanceIsConversationOnly`).

### A third topic: friendship reciprocity, not another restoration project

Both prior scripts (sailboat, marathon) shared a shape: a physical project
tied to a parent, derailed by a sudden setback. The third,
`tools/audit_somatic_census.py --topic friendship`, is deliberately
different - a friendship that has quietly become one-sided, no object, no
parent, no physical goal - specifically because most of its early turns are
the person thinking out loud or venting, not asking for anything, which is
exactly the shape that would expose an engine too eager to solve. Same 30-turn,
five-phase structure (8/6/6/5/5) as the other two.

### Reset, then the run

`reset.sh` was run as asked (deletes `__pycache__`, `logs/`, `memories/`,
`saves/`, a handful of named lore/legacy files and test artifacts; does not
touch `tools/cache/`, source, or docs). `tools/cache/somatic_census.jsonl`
was separately found deleted from disk right after, with nothing in
`reset.sh` itself to explain it; Gordon had deleted it directly and
deliberately, so the new run would start a clean file instead of appending
onto the sailboat/marathon history. Not knowing that, `git checkout --
tools/cache/somatic_census.jsonl` restored the old committed version, so the
friendship run appended onto it anyway (120 lines: the original 90 plus 30
new), the opposite of what was intended. Trimmed back down to the 30
friendship records after the fact; the full history remains in git
(`cda575f` and earlier) for anyone who wants it back.

### The census: mostly clean, one real bug found

25 of 30 turns generated (83%), flagging 5/6, distressed 3/5, recovering 3/5.
Health held between 84.6 and 99.8 throughout; no topology-collapse false
positive this time. All five halts carry the calm, gate-specific text from
the previous entry's fix, confirmed live for the first time outside a unit
test - including the `GATEKEEPER` line ("Something in how that came through
didn't parse cleanly on this end...") in place of what would previously have
been the raw `CURSED_INPUT` string.

Two of those five `GATEKEEPER` halts (turns 20 and 22) were on completely
ordinary, well-formed sentences:

> "she called me crying tonight, her job let her go, and I spent two hours on
> the phone with her and I don't feel bad about that part"
> "I feel like a horrible person for even having these thoughts while she's
> going through this"

Traced with a `Nomination.__init__` patch around a direct `process_turn()`
call: both triggered `TheGatekeeper._audit_safety`
(`physics/filters.py:203-204`), which rejects a turn as `CURSED_INPUT`
whenever any word in it appears in `lore/lexicon.json`'s `"cursed"` list. That
list was `["future", "predict", "sentient", "secret", "human", "feel"]`,
seemingly meant to catch meta-awareness talk ("are you sentient?"). "feel"
and "human" are two of the most ordinary words in emotional English, and both
turns used "feel." The two people most likely to say "feel" in a sentence are
exactly the people D9's whole redesign exists to answer rather than refuse:
someone mid-crisis or carrying guilt.

Removed "feel" and "human" from the list; `"future"`, `"predict"`,
`"sentient"`, `"secret"` remain on the theory that they are rarer in ordinary
speech, a theory not re-verified here. Worth a second look if any of them
produces the same failure. New regression:
`tests/test_gates.py::test_ordinary_feelings_do_not_trigger_cursed_input`,
calling `TheGatekeeper._audit_safety` directly against the two exact failing
sentences plus a plain "I'm only human" control. Confirmed live end to end:
re-running the same two messages through a real `process_turn()` after the
fix now reaches `GEODESIC_FRAME` (an answered turn), not `SILENCE`.

Worth naming as its own finding, separate from the specific word list: this
mechanism checks the *person's own input* for words a meta-aware AI might use,
which is backwards from what it likely should guard - the model's output
claiming sentience, not the person mentioning it exists. Not redesigned here;
flagged for whenever this area gets revisited.

### The advice-restraint line, read against the transcript

Comparable early-conversation turns: marathon (before) - *"You need to focus
on building a consistent base before you start pushing for distance... Don't
try to run the full miles every time"* - prescriptive advice for what was
just excited context-sharing. Friendship (after), the tiring/flagging/
distressed/recovering phases (turns 8-29) hold back consistently: *"You don't
have to decide exactly what it means right now. We can just sit with the fact
that it weighs on you,"* *"The silence is your right here,"* *"Just rest."*
Advice appears exactly where it was asked for (turns 5 and 7, both explicit
requests) and is answered directly there. The early "engaged" phase (turns
0-4, 6) still leans toward unsolicited interpretation ("It usually means the
dynamic has shifted...") rather than outright advice - softer than the
marathon pattern, not fully gone. Partial improvement, honestly reported as
such; worth another look specifically at the engaged-phase framing if this
still reads as too quick to interpret.

Firewall held: one em dash across 25 replies, no antithesis slipped through.

### Verification

Full suite after the advice-restraint line: 580 passed. After the cursed-word
fix: **581 passed, 5 skipped, 138 subtests passed**. Continuously green
through every step today.

<a id="silence-reason-tone"></a>

## Earlier: the Stage Manager's reason, made safe for a person to actually read, 2026-09-19

Same day, continued again. The entry below added `verdict.reason` to the text
a person sees when the Stage Manager holds. Gordon read a real example and
caught the problem immediately:

> `**System:** _(Silence - Stage Manager held the floor empty - CURSED_INPUT:
> The Gatekeeper recoils. Cursed syntax detected.)_`

`verdict.reason` is each gate's own technical string, written for logs and
receipts, not a person to read. Checking every gate a `Nomination` can carry
found the same problem throughout, not just the one example:

```
gatekeeper_cursed  -> "The Gatekeeper recoils. Cursed syntax detected."
gatekeeper_toxic   -> "IMMUNE REACTION: Input rejected as pathogenic."
PINKER             -> "Structural rot critical."
ROS_PANIC          -> "Counterfactual simulation indicates fatal ROS toxicity..."
```

Raw internal tags concatenated onto the message (`f"{type_str}: {msg}"` in
`physics/filters.py`), and phrasing that reads as blaming the person's own
input for being "cursed" or "pathogenic" is exactly wrong to show someone,
especially since the people most likely to trigger a hold are the ones D9
already weighs most carefully: distressed or exhausted.

Two gates are explicitly crisis-adjacent: `LINEHAN` (as in Marsha Linehan,
DBT; fires on near-total exhaustion with zero resonance) and `AFFECTIVE`
(fires on high exhaustion plus high friction). Their actual text:

- LINEHAN: *"Terminal User Exhaustion detected. Resonance is zero. Applying
  absolute Friction to protect cognitive load."* Cold and clinical.
- AFFECTIVE: *"Hey. Take your hands off the keyboard. The machine doesn't
  care if you bleed on it, but I do."* Trying to be warm, but "bleed on it"
  is body/harm-adjacent language aimed at someone the system has just flagged
  as highly exhausted. Not something to reword unilaterally.

Brought both to Gordon directly rather than guessing. Decided: plain and
calm, no metaphor, for both, same standard as everything else.

### The fix

`Verdict` (`archetypes/stage.py`) gained a `gate: str = ""` field, set from
`winning_nom.gate` on a nomination-driven hold, and from two new synthetic
labels (`ATP_FLOOR`, `TENSION_MAGNITUDE`) on the Stage Manager's own two
non-nomination holds. `lore/ux_strings.json` gained a `silence_reasons`
domain: one calm, plain-English line per gate, an explicit `_default` for
anything unlisted, and a `_comment` stating the rule for future entries (no
internal tags, no jargon, nothing that reads as blaming the input).
`_hold_the_silence` (`phases/cognitive.py`) now shows that translation in the
`ui` field a person reads; `verdict.reason` stays exactly where it was
already useful, unchanged, in `logs` and `mind.context_msg` for telemetry
and receipts.

```
LINEHAN    -> "I want to slow down for a second here. There's no rush to keep going."
AFFECTIVE  -> "Let's pause for a moment. This can wait until you're ready."
GATEKEEPER -> "Something in how that came through didn't parse cleanly on this
               end. Try sending it again, maybe rephrased or a bit shorter."
```

`tests/test_stage_manager.py` gained `TestSilenceReasonsAreHumanSafe`: a roll
call asserting every gate a real `Nomination` is constructed with in
production has its own entry (not a silent fallback to `_default`), a
forbidden-word sweep across all of them ("cursed", "pathogenic", "exploit",
"bleed", and the exact clinical phrases above), and an explicit check that
LINEHAN and AFFECTIVE specifically carry no body or harm language. Plus a
direct regression: the raw technical reason must never appear in `ui`, and
must still appear in `logs`/`mind.context_msg`.

### Verification

Full suite after this fix: **578 passed, 5 skipped, 135 subtests passed**.
Continuously green through every step in this session.

<a id="firewall-topology-second-census-2026-09-19"></a>

## Earlier: reading the census closely, the Lexical Firewall widened, a live-killing topology bug found and fixed, a second topic confirms it, 2026-09-19

Same day as the entry below, continued. Gordon read the 30-turn sailboat
census transcript directly (not just the summary numbers) and found two real
problems the aggregate statistics couldn't show: occasional em dashes and
antithesis ("not X, but Y") that the Lexical Firewall was missing, and a
tonal drift where flagging/distressed replies narrated the person's situation
back at them instead of answering them directly. Fixing both, then verifying
on a second, unrelated topic, surfaced a serious bug that had nothing to do
with either fix.

### The Lexical Firewall: two real gaps, one deliberately not closed

`NEGATIVE_COMPARISON` (`lore/style_crimes.json`) only matched "not X, but Y"
linked by a comma or dash inside one sentence. A live turn had three
uncaught antithesis constructions split across sentences and a semicolon:
*"it isn't a monument. It's a transition. You aren't building a shrine; you're
honoring him..."* Widened to also match a negation clause ending in `.`/`!`/
`;` immediately followed by "It's/They're/You're/We're/That's", verified
against the exact failing text plus a set of plain-negation controls that
must NOT fire (`tests/test_composer.py:TestNegativeComparisonDetection`).

Em dashes were deliberately **not** given a hard numeric cap after discussion:
occasional use is normal writing, and D2's own "coarse proxy, not grammar
police" ethos argues against a strict reject rule here. Instead,
`lore/system_prompts.json` CONVERSATION style_guide gained item 4: real people
reach for a semicolon, an Oxford comma, or parentheses before a dash in
spoken conversation; formal writing and literature are unrestricted. A "time
and place" preference, not a validator rule.

### The tone finding: candor without presence

Reading the sailboat census's flagging/distressed replies found a pattern:
*"She just cut the cord on your time with it... It's a betrayal of the work
you were trying to do in private"* — narrating the person's situation from
outside it, like a narrator summarizing a character, rather than answering
them. Traced to the kernel's "Candor over empathy" line: it named what not to
do (empathy-guessing, banned separately by the firewall's `SYRUPY_EMPATHY`
pattern) but never named what presence actually looks like, so the model
filled the gap with detached analysis. New style_guide item 5, **RESPOND, DO
NOT NARRATE**, names the failure mode with the real example and asks for
first-person, direct address instead. Both new lines are pinned to
CONVERSATION only, absent from ADVENTURE
(`tests/test_physics_to_prompt.py:TestPunctuationGuidanceIsConversationOnly`,
`TestPresenceOverNarrationGuidanceIsConversationOnly`).

### Also: the Stage Manager's reason now reaches the person

Gordon asked for a small description of why the Stage Manager chose silence,
when it does. `_hold_the_silence` (`phases/cognitive.py`) always computed
`verdict.reason` but only ever logged it internally; the text a person
actually saw was the generic "nothing is ready to be said" line. It is now
appended to the `ui` field that reaches them
(`tests/test_stage_manager.py::test_the_ui_text_explains_why`). **This surfaced
a second, more serious problem, covered in the next entry
(`SESSION_HANDOFF.md#silence-reason-tone`): several of the raw reason strings
this exposes are not fit for a person to read as-is.**

### The bug the second census found: a live-killing false positive in the topology check

Running a second scripted conversation (`--topic marathon`, same phase shape
as the sailboat script, different subject: marathon training derailed by
injury) to confirm the firewall/tone fixes on fresh material found the
engine dying at turn 10 of 30 and staying dead. Cause: today's earlier
`calculate_clustering` fix (see the entry below) had activated a
terminal-shutdown check that had *never once run in production before*, and
its comparison logic was broken in two ways a working implementation finally
exposed:

1. **Zero-versus-zero.** A real 10-node conversational memory graph is sparse
   and tree-like this early, with no triangles; a random rewiring of that
   same sparse graph is equally triangle-free. Comparing 0.0 to a null
   baseline of 0.0 is not evidence of collapse, but the original comparison
   (`actual <= null * 1.05`) treated it as fatal proof and executed an
   irreversible shutdown.
2. **Single-sample noise**, found on a second reproduction after fixing (1):
   one random rewiring or configuration-model draw is one noisy sample; a
   sparse, small graph can land a stray triangle, or none, by pure chance.

Fixed in `cycle.py:_verify_semantic_topology`/`_bg_topology_check`:

- Minimum graph size raised from 6 nodes to `CORE.TOPOLOGY_MIN_NODES` (20).
  The same discipline `GATE.MIN_CORPUS` already applies to the governor's own
  null comparison, for the same reason: small-n statistics need a real floor.
- Both null estimators (rewire and configuration-model) are now averaged
  over 5 independent draws each, not a single draw.
- The null baseline must clear `CORE.TOPOLOGY_NULL_FLOOR` (0.05) before "no
  better than null" is treated as meaningful; comparing a value against noise
  is not evidence anything collapsed.
- A single crossing is no longer terminal. `CORE.TOPOLOGY_COLLAPSE_STRIKES`
  (3, matching the embedding fallback's own consecutive-failure count for its
  terminal transition) must be reached on **consecutive** checks before health
  is actually set to zero; any declined or negative check resets the count.

`tests/test_chaos_engineering.py` rewritten with three validated fixtures
(stress-tested 10+ seeds, 5 repeated full runs, all stable): a dense bipartite
graph (real collapse, needs all 3 strikes to fire), a 30-node sparse path
(declines to judge, the exact bug reproduced), and 5 bridged 4-cliques
(healthy, does not fire). The clique-count-over-clique-size finding is worth
keeping: denser individual communities give the null models more chances to
grow incidental clustering too, shrinking the real gap; more, smaller
communities is the reliable construction.

### The re-run: clean

With the fix in place, the marathon census completed all 30 turns: 28 of 30
generated (93%), flagging 6/6, distressed 4/5, health held between 83.5 and
99.8 throughout. Both halts (turns 13, 20) carry the same clean Stage Manager
reason. Cache: `tools/cache/somatic_census.jsonl`, run `20260919-122608`.
`tools/audit_somatic_census.py` gained `--topic` (`sailboat` default,
`marathon` new), so a second scripted conversation is a flag away rather than
a hand edit, specifically so a fix is not just verified against the one
transcript that found it.

The tone fix shows up directly in the transcript. Sailboat flagging phase
(before): *"The timber will wait for tomorrow's light,"* *"The wood doesn't
care about the timing"* — deflecting to object logistics. Marathon flagging
phase (after): *"I am right here with you in the quiet,"* *"I am here in this
space with you."* Worth watching, not yet a problem: those six replies now
converge on their own "I'm here in this space" refrain. A better failure mode
than before, still a formula.

Firewall: one em dash total across 30 replies, both single instances, and no
negative-comparison antithesis slipped through, including a phrase that
correctly did *not* fire (*"It was never just the race. It was the goal..."*,
plain rhetorical contrast, not the AI-tell pattern the rule targets).

### Verification

Full suite after the firewall and tone changes: 570 passed. After the
silence-reason fix: 571. After the topology-check overhaul: 574. All are
5 skipped, 29 subtests passed, no failures at any point. `config.json.bak`
(byte-identical to the gitignored `config.json`, produced by some boot path
during direct engine construction outside the test harness) is untracked and
safe to delete.

<a id="d9-d1-d2-census-2026-09-19"></a>

## Earlier: D9 unified, D1 completed, D2/D2b rebuilt, and the confirming census, 2026-09-19

Starting state: clean `6d7fd0b` (`20.7.1.3`). This session audited D1/D2/D9 against
their own written acceptance criteria (the roadmap's own next step after the
refusal-test repair below), found each partially complete, fixed what it found,
then ran the D0b/D9 live census the fixes were prerequisite to. Most of the code
changes landed in `a90ce06` (`20.7.2`) mid-session; the census tool fix below was
made afterward and is, as of this writing, uncommitted.

### D9: four refusals were still bypassing the Stage Manager

Auditing D9's own "done when" (no gate stops a turn on its own) found
`SimulationPreflightPhase.run()` (`phases/cognitive.py`) still had four hardcoded
short-circuits, each setting `ctx.refusal_triggered` and returning directly,
one phase before `ArbitrationPhase` ever runs: `NABLA_SILENCE` (a `[SILENCE]`
tag), `APOPTOTIC_BLOCK` (a zero-width-character exploit), `PREMISE_VIOLATION`
(a slash-command asking to analyse code with none attached), and
`POINT_OF_NO_RETURN` (deploy/schema-change language without `CONSENT`). None of
the four ever touched `ctx.nominations` or `StageManager.negotiate()`, none
read the person's state, and none had any test coverage. The other seven gates
(MOOG, GORDON_ANCHOR, PINKER, LINEHAN, AFFECTIVE, ROS_PANIC, the gatekeeper)
were already correctly migrated to `Nomination` objects.

Fixed: all four now append a `Nomination` with their own reason and magnitude
100.0 (uncapped magnitude means an extreme case still holds, per
`StageManager.negotiate()`'s `winning_nom.magnitude >= 100.0` override) and
return, letting `ArbitrationPhase` decide. Five new regression tests cover each
path plus the case where a nomination's magnitude is capped by
`somatic_budget`. Full suite went from 525 to 535 passed, 5 skipped, 29 subtests.

### DSPyCritic no longer piggybacks on the answering model

`DSPyCritic` read the same `MODEL` key as `LLMInterface`, so it always ran on
whatever D7 tuned for somatic compliance (`gemma4:12b`), for a boilerplate/
faithfulness filter that has no need of that. New `BoneConfig.DSPY_MODEL`
(`gemma4:e4b`), read first in `mechanics/dspycritic.py`; `MODEL` is untouched.
Full suite wall clock dropped from about 14 minutes to about 7, same 535
passed. This is the only change in this entry that is also a production
behaviour change outside the somatic tracks, and only for the critic's own
generations, not the answering model.

### D1: two gaps against its own written contract

`body/somatic_budget.py:SomaticBudget.evaluate()` existed and was wired
everywhere D1 asks, but:

1. **Every threshold was hardcoded in Python**, contradicting D1's own line
   "Constants live in `BoneConfig` (A1's rule)". Moved to a new
   `BoneConfig.SOMATIC_BUDGET` section (19 keys) mirrored into
   `lore/tuning_presets.json`, following the same pattern as `STAGE`/`GATE`:
   a hardcoded Python fallback plus a JSON copy that overrides it at boot.
   `REQUIRED_CONFIG` updated so the boot audit catches a dropped key.
2. **`engine_state` never carried respiration**, only `atp_pool`/`ros`, even
   though D1's own spec lists "ATP, respiration, ROS, chemistry" as the four
   engine inputs. The old (now-retired) ANAEROBIC directive fired on a single
   costly turn (`raw_cost > BIO.ANAEROBIC_THRESHOLD` in `body/metabolism.py`),
   a different signal than the pool's cumulative level: a turn can spike
   ANAEROBIC while ATP is still healthy. `phases/biological.py` now passes
   `ctx.bio_result["respiration"]` through; `SomaticBudget.evaluate()` tightens
   the cap on it independently (new `SENTENCE_CAP_ANAEROBIC`/
   `RETRY_ALLOWANCE_ANAEROBIC` config, default 5/2, milder than full ATP
   depletion's 3/1). This also let `tests/test_physics_to_prompt.py` drop a
   hack that faked `atp=10.0` whenever respiration was ANAEROBIC to get the
   old behaviour by a side door.

New `tests/test_somatic_budget.py` (mutation-style: moves a config threshold,
confirms the decision moves with it, the same discipline A4 uses) and a new
`TestSomaticBudgetReachesThePrompt` class in `test_physics_to_prompt.py` that
constructs `SomaticBudget` objects directly and pins each field's own effect
on the composed text, satisfying D1's "done when" (`test_physics_to_prompt.py`
extended to pin budget in, text out) directly rather than through the
composer's own re-derivation, which the existing tests only exercised
indirectly.

### D2: the audit tool was measuring a mechanism that no longer runs

`tools/audit_somatic.py`'s `compose_arms()` patched `_derive_bio_mood` and
`ux()` to inject the retired directive strings ("ANAEROBIC STATE. Raw,
breathless, efficient prose.", the old exhaustion line), neither of which
exists in the composer since D2 landed, and hardcoded `"somatic_budget": None`
into every arm's state, which skips the entire SOMATIC CONTRACT block the
composer now renders. It could not have detected D2 shipping. Three further
breakages, unrelated to D2's wording and pre-dating this session, meant the
tool could not even run: `verify_manipulation()` was called but never defined
(latent `NameError`); `patch("...PromptComposer._get_lore")` targeted a method
that no longer exists (`self.lore` is a plain dict now); and `compose()` was
called with `user_input=` against a real signature of `user_query=`, so every
arm silently composed in `ADVENTURE` mode (no `state["meta"]["active_mode"]`
was ever set) atop the two prior bugs.

Rebuilt: `compose_arms()` now builds real `SomaticBudget` objects via a new
`budget_for()` helper, the same call `phases/biological.py` makes every turn.
`somatic_block_text()` mirrors the composer's full SOMATIC CONTRACT rendering
(not just the cap line), so `check_arms()` verifies the composer said exactly
what the budget implies. `EXPECTED_DIFF` updated for the current line shapes,
including a second telemetry line (`[E:... | V:...]`) the old regex never
covered. The one stale unit test in `tests/test_audit_somatic.py` (built on
the retired constants) is rewritten against the new contract.

Verified live: dry-run arm construction against a real composer, then a full
generate-cache-analyse smoke run (3 messages, 1 repeat, `gemma4:e4b`) with no
errors and sane per-arm text. Not run: the real 20-message x 8-repeat
statistical pass this tool exists to produce; that is still open, now that the
tool can actually produce it.

### D2b: accommodation measures and a third persona

`body/somatic_metrics.py` (shared with the D3 validator, per the roadmap's own
instruction) gained five measures: `reply_to_message_ratio` (reply length
relative to the partner's own message), `ends_with_question` (closing-question
rate), `offers_to_carry_load` (a phrase-pattern proxy: "I'll carry", "let's
share", etc.), `mirrors_affect` (a curated shared-affect-word proxy between
reply and message, not a sentiment lexicon), and `question_count`. D2b also
asks for "choices offered" and "instructions given"; neither has a defensible
regex proxy and both are left unmeasured rather than guessed at, noted in the
module docstring.

`tools/audit_somatic.py` gained a `DISENGAGED` arm: flagging exhaustion *and*
critically low effort, the only combination that actually sets
`offer_to_carry_load`. `CONTROL`/`EXHAUSTED` double as D2b's "fresh"/"tired"
personas rather than adding two redundant arms. `ARMS` widened from
`(respiration, exhaustion)` to `(respiration, exhaustion, effort)` throughout.

Verified live in the same smoke run as D2, including the `DISENGAGED` arm's
full SOMATIC CONTRACT block (cap, no-narration, no-closing-question, and the
new carry-load line, all four present together). Not run: the statistical
pass D2b's own "done when" asks for (a tired or disengaged partner measurably
getting a lighter reply than a fresh one, with intervals, on two models).

### The census: D0b and D9 both confirmed live

`tools/audit_somatic_census.py` also imported the now-deleted
`ANAEROBIC_DIRECTIVE`/`EXHAUSTION_DIRECTIVE` constants from `audit_somatic.py`
(a fourth file this session's D2 changes would have silently broken).
Replaced with substring checks against the current SOMATIC CONTRACT wording:
`SOMATIC_CAP_TIGHTENED`, `SOMATIC_NO_CLOSING_QUESTION`,
`SOMATIC_OFFER_TO_CARRY_LOAD`.

With that fixed, ran the real 30-turn census against `gemma4:12b` (persistence
patched off, live embeddings, the real engine): `.venv/bin/python
tools/audit_somatic_census.py --model gemma4:12b`. Cache:
`tools/cache/somatic_census.jsonl`, run `20260919-095553`.

**D0b, confirmed**: 27 of 30 turns (90%) generated a real reply. By phase:
engaged 8/8, tiring 5/6, **flagging 6/6**, distressed 4/5, recovering 4/5. ATP
held between 23 and 52 across the whole run and never crashed. The flagging
phase, the one D0b's tolerances were specifically sized for, answered every
turn.

**D9, confirmed**: all three halted turns (13, 22, 26) carry the identical
Stage Manager reason, "The Stage Manager holds the floor empty. Nothing here
is ready to be said yet." — not `MOOG_QUARANTINE`, `SYSTEM_HALT`,
`COUNTERFACTUAL_REJECTION`, or any of the four hardcoded bypasses fixed above.
The ATP ledger shows exactly three `-6.0, "Stage Manager: negotiated silence"`
entries, matching the three halts one for one: the ATP cost of declining is
being charged from the one place D9 asks for, not by an independent gate.

**D1, shown moving live**: `somatic_cap_tightened` fired on 18 of 27 generated
turns; `offer_to_carry_load` fired on 17, tracking `P_u` hitting 0.0 four
separate times across the script. This is the first live evidence the budget
object actually tracks a real conversation rather than resting at one value,
which is what D0's original census went looking for and could not find in the
old five-path mechanism.

### Found, not fixed

A warning fired once during the census: `[CYCLE] Async Topology Error:
'MycelialNetwork' object has no attribute 'calculate_clustering'`. Unrelated
to any of the above; next task.

Also produced, not part of the repo: `config.json.bak`, byte-identical to the
gitignored `config.json`, written by some boot path during today's direct
`BoneAmanita(...)` construction outside the test harness. Content is
unaffected (verified identical); the file itself is untracked and harmless to
delete.

### Verification

Full suite after every change above except the census tool's own fix (which
has no test coverage; verified instead by the live census run itself
completing cleanly): **559 passed, 5 skipped, 29 subtests passed**, about
6 minutes 43 seconds. This is the current full-suite baseline.

### Next

Two statistical passes are now unblocked but not run: D2's two-model
comparison (does the share of replies within cap rise, does body narration
stay flat) and D2b's accommodation pass (does a disengaged partner measurably
get a lighter reply than a fresh one). Then the topology-check bug above.

<a id="refusal-tests-2026-09-18"></a>

## Earlier: seven refusal-test failures repaired, 2026-09-18

The seven previously recorded failures now pass in the focused run. This round
changes only five test files, not production refusal logic or thresholds.
It preserves the uncommitted embedding and atomic quicksave repairs on top of
`8069778`.

### Causes and corrected contracts

- Cortex and Moog fixtures used unspecced `MagicMock` physics objects. Their
  fabricated `to_dict()` methods took precedence in `dump_state`, so assigned
  dictionary fields never became the numeric input being tested. Real
  `PhysicsPacket`, `EnergyState`, and `CycleContext` objects now exercise the
  production serialization boundary. Numeric gate values no longer originate
  in fabricated mock methods.
- Gate-tolerance and scar tests referenced `MagicMock` without importing it.
  They now use the same concrete packet/context types rather than adding an
  import that would retain the faulty serialization fixture.
- Tests of the adventure counterfactual and Moog gates explicitly set a 1.0
  tolerance on a config instance. Conversation comparisons retain 1.6. This
  fixes the test setup rather than retuning production thresholds.
- The productive-worry test expected preflight to halt immediately. D9 moved
  that decision to arbitration, and its original ROS fixture was also below
  the widened conversation threshold. It now supplies maximum accumulated ROS
  plus high friction at tolerance 1.6, verifies the ROS nomination and scar,
  confirms preflight does not halt or spend ATP, then runs real arbitration.
  It asserts final `SILENCE`, the winning reason in the packet and receipt,
  and exactly one configured silence charge. The extreme-tolerance test also
  verifies the final arbitration outcome, not just the nomination count.

The original assertions about gate identity, toxic versus tolerated input,
scar creation, and preserving MIND remain. Final refusal follows the documented
Stage Manager contract; no production gate was weakened to make tests pass.
This does not establish completion of every D9 route or live accommodation.

### Verification and next work

The first fixture correction run returned **32 passed, 1 failed**; the remaining
failure was an attempted direct read of an optional ROS config key in the new
fixture. The final focused run covered cortex, gate tolerance, Moog, random,
scars, and Stage Manager: **54 passed, 4 subtests passed**, in 25.22 seconds.
The complete suite test run (`python -m pytest -x -q`) successfully passed all tests:
**525 passed, 5 skipped, 29 subtests passed** in 293.09 seconds. The test baseline
is now completely green.

Tests run in `/tmp/boneamanita-refusal.ws3uwms6`, a disposable copy of the
working files, Git metadata, and the untracked quicksave tests, with Python
3.14.7. Logs are `/tmp/boneamanita-refusal-focused.log`,
`/tmp/boneamanita-refusal-focused2.log`, and `/tmp/boneamanita-refusal-full.log`.
The user's live saves and lore are untouched.

Next: audit D1/D2/D9 against their acceptance criteria and refresh the somatic
audit arms before live census/accommodation measurements. Green regression
checks alone do not certify model behavior.

<a id="quicksave-repair-2026-09-18"></a>

## Earlier: atomic quicksave repair, 2026-09-18

R2 is repaired in `protocols/chronos.py`. The working tree started at `8069778`
with the embedding repair and its documentation/tests still uncommitted. Those
changes were preserved. R1/R1b and R3 are also repaired; the seven existing
refusal-test failures are the next work package.

### Checkpoint contract

Quicksave writes a unique `.quicksave-*.tmp` file in the save directory,
serializes the existing checkpoint schema, flushes and fsyncs the file, closes
it, then publishes it with `os.replace`. Keeping both paths on the same
filesystem permits atomic replacement. The previous checkpoint is never opened
for writing. Serialization, partial-write, file-sync, and replacement failures
leave it byte-for-byte intact and retain the existing failure message/log path.
A failed first save leaves no checkpoint. Temporary files are removed after
handled failures; cleanup errors are logged without hiding the original error.

This is atomic file publication, not a broader checkpoint schema change or a
power-loss durability guarantee. A hard process kill can leave an unpublished
temporary file, and the containing directory is not fsynced. Concurrent saves
use separate temporary files; the last successful replacement wins.

### Verification

Five new tests in `tests/test_quicksave.py` cover partial JSON writes, circular
(nonserializable) history, fsync/replace failures, failed first save, and a
successful replacement that publishes complete flushed JSON. The old code
failed these regression scenarios. The focused selection of quicksave, macro,
protocol, genesis-continuity, and shutdown tests passed: **21 passed,
2 subtests passed**, in 21.20 seconds.

The full run (`python -m pytest -q --tb=short`) finished with **518 passed,
7 failed, 5 skipped, 29 subtests passed**, in 277.26 seconds. All five new
quicksave tests passed, including both fsync/replace subcases. The seven failure
nodes are unchanged from the baseline. This run covers `8069778` plus the
embedding and atomic quicksave source/test changes; those files match the
tested copy byte-for-byte. No live-model behavioral audit was run.

Tests run in `/tmp/boneamanita-quicksave.sxd0lf19`, a disposable copy of the
tracked working tree (including the embedding edits), Git metadata, and the
new quicksave test file. The project Python 3.14.7 interpreter is used. Logs are
`/tmp/boneamanita-quicksave-before.log`, `/tmp/boneamanita-quicksave-after.log`,
and `/tmp/boneamanita-quicksave-full.log`. Tests use temporary save directories;
the user's live saves and lore are untouched.

Next: repair the seven refusal-test failures against the nomination/arbitration
contract, without weakening behavioral assertions. Then validate D1/D2/D9 and
run the current somatic measurement arms.

<a id="embedding-repair-2026-09-18"></a>

## Earlier: embedding fallback repair, 2026-09-18

Starting state: clean `8069778` (`7.0.14.2`), including the committed shutdown
repair. This follow-up repairs R1/R1b in `spores/embeddings.py`; R2 (atomic
quicksave) and the seven existing refusal-test failures remain open.

### Fallback contract

- Vector width is fixed at backend resolution. Runtime degradation retains
  that width so existing FAISS indexes and rank banks remain shape-compatible.
  Booting directly into hash still uses the historical eight dimensions.
- A transient failure marks the embedder degraded immediately and returns hash
  coordinates for the entire sweep, including any semantic cache hits. The
  receipt names hash/SHAKE-256 as the vector source and includes the failure.
- Temporary hash results are never stored under semantic cache keys. Healthy
  cached entries survive a transient outage; failed texts retry the backend on
  their next request. Successful backend work clears the transient degraded
  state and consecutive-failure counter. Cache-only requests do not prove
  backend recovery and do not clear that state.
- After three consecutive failed backend sweeps, the embedder switches to hash,
  clears semantic cache entries, and caches only under the hash identity.
  This terminal fallback still requires engine restart/reconfiguration to
  restore a semantic backend; automatic recovery from that state is not added.
- Each backend batch is validated for row count, width, numeric values, and
  finite coordinates before any result enters the cache. Malformed output
  follows the same failure path as a transport error.
- An instance lock serializes backend calls, transitions, and cache updates
  so concurrent callers cannot write fallback vectors under a changing identity.

Hash remains non-semantic. Fixed dimensions prevent shape errors; they do not
make old semantic vectors comparable to new hash vectors. This repair does not
re-embed persisted memories or add per-vector provenance to downstream stores.

### Verification

The regression tests reproduced the old transient receipt/cache bug, the
16-to-8-dimensional transition, and five malformed-vector cases. The first
post-repair selection (`tests/test_embeddings.py tests/test_receipts.py
 tests/test_resonance.py tests/test_memory.py tests/test_spores.py`) returned
**81 passed, 5 skipped, 5 subtests passed** in 48.20 seconds. Two additional
regressions then covered concurrent recovery and mixed cached/uncached sweeps.
All transport failures and recoveries are mocked; no live outage was induced.

The complete suite (`python -m pytest -q --tb=short`) finished with **513 passed,
7 failed, 5 skipped, 27 subtests passed**, in 277.54 seconds. All five new
embedding tests, including five malformed-vector subcases, passed. The seven
failures match the baseline exactly. This result covers `8069778` plus
`spores/embeddings.py` and `tests/test_embeddings.py`; both files were verified
byte-for-byte against the tested copy. No live behavioral audit was run.

Tests run in `/tmp/boneamanita-embedding.zjjoybcq`, a copy of tracked files with
Git metadata and the changed source/tests, using the project Python 3.14.7.
Temporary logs are `/tmp/boneamanita-embedding-before.log`,
`/tmp/boneamanita-embedding-after.log`, and `/tmp/boneamanita-embedding-full.log`.
The user's saves and lore are untouched.

Next repair: preserve the last valid quicksave when serialization or writing
fails. Then repair refusal fixtures/contracts and validate D1/D2/D9 behavior.

<a id="stabilization-2026-09-18"></a>

## Earlier: baseline reproduction and shutdown repair, 2026-09-18

This follow-up supersedes the review's R3 status. R1/R1b (embedding fallback)
and R2 (quicksave) remain open, as do the seven refusal-related test failures.
The user authorized the proposed stabilization work; this first work package
reproduces the baseline and repairs engine/fixture shutdown.

Starting state: clean `8bdd960` (`7.0.14.1`). The formerly uncommitted review
changes are now committed. Tests ran in a disposable copy of tracked files
with `.git` metadata, using the project's Python 3.14.7 interpreter. The new
shutdown tests and the two modified Python files were copied into that checkout
for validation. No tests ran against the user's live saves or lore.

### What changed

- `GeodesicOrchestrator.shutdown()` clears `is_running`, joins the cycle daemon,
  then waits for the background executor. The existing engine shutdown order
  therefore reaches persistence and telemetry only after those producers finish.
- An idle daemon checks the stop flag after its queue timeout so it does not
  begin a REM tick while shutdown waits for it.
- `BoneTestCase` registers cleanup with `unittest.addCleanup`: the captured
  engine is shut down before its patches and shared resources are released,
  including when a subclass raises after base setup. Fixture cleanup patches
  `perform_shutdown` to avoid persisting test state.
- Four regressions cover idle/repeated shutdown, a running background worker,
  an active daemon turn, and a subclass setup failure. The first three authored
  regressions (idle, worker, setup failure) all failed against the old code;
  the active-turn case was added afterward.

Shutdown waits for active work to return; it does not cancel an in-flight model
request or promise a fixed shutdown deadline. Call shutdown from the owning
thread, outside the daemon and its workers.

### Baseline evidence and next work

Before edits, running `tests/test_cortex.py tests/test_gate_tolerance.py
 tests/test_moog.py tests/test_random.py tests/test_scars.py` with
`python -m pytest -q --tb=short` reproduced the same seven failure nodes listed
in the review: **26 passed, 7 failed**, in 17.38 seconds. After the first three
shutdown tests and cleanup repair, adding `tests/test_shutdown.py`,
`tests/test_cycle.py`, and `tests/test_architecture.py` returned **43 passed,
7 failed**, in 23.94 seconds. These are overlapping selected runs.

The complete post-repair run, `python -m pytest -q --tb=short`, finished with
**508 passed, 7 failed, 5 skipped, 22 subtests passed**, in 277.51 seconds.
All four shutdown regressions passed. The seven failure nodes are unchanged
from the reproduced baseline; no additional failures appeared. This result
covers `8bdd960` plus the changes to `cycle.py`, `tests/base.py`, and the new
`tests/test_shutdown.py`. It supersedes the earlier selected-run baseline.
The disposable checkout was `/tmp/boneamanita-stabilize.aul7jckc`; the full log
was `/tmp/boneamanita-stabilize-full.log`. These temporary artifacts are not
required to interpret the recorded result.

The refusal tests have not been weakened or repaired. Inspection shows that
unspecified `MagicMock.to_dict()` values enter `dump_state`, and that preflight
nominates while arbitration decides the final refusal. Follow-up tests should
use concrete physics state and assert both boundaries; missing `MagicMock`
imports alone do not establish that the remaining fixtures are sound.

Next: atomic quicksave preservation, embedding fallback/cache/index contracts,
and refusal-fixture/contract repairs, followed by a fresh complete suite and
D1/D2/D9 acceptance audit. Live somatic measurements remain outstanding.

<a id="review-2026-09-18"></a>

## Earlier review and documentation reconciliation, 2026-09-18

This section supersedes older present-tense status, test totals, and next-step
instructions below. Older entries are retained as session history, not as a
description of the current working tree. Standing project decisions, including
preserving the biological vocabulary, still apply.

### Scope and authorization

Codex reviewed the repository, ran tests in a temporary copy, and reproduced
three runtime failure areas with isolated probes. The user's follow-up was:
"Do not attempt to repair anything; just prep the next round with the handoff
and make sure our readme is being honest."

This follow-up changes documentation only (`README.md`, this file, and the
roadmap's current-status descriptions). **None of the defects below has been
repaired, and no new regression tests have been added.** The next-round list is
a proposed work plan, not authorization to begin repairs in this documentation
session. No live-model behavioral audit was run in the review or this follow-up.

### Reviewed state and existing user changes

- HEAD at review: `b0a096e` (`7.0.14`). Findings apply to that commit **plus the
  working tree as reviewed**, not to a pristine checkout of the commit.
- Pre-existing modified files: `.idea/BoneAmanita.iml`, `credits.txt`, `presets.py`.
- Pre-existing staged deletions: `tools/cache/audit_somatic.jsonl` and
  `tools/cache/somatic_census.jsonl`.
- Those edits and staged deletions were left intact. Do not restore old audit
  caches, discard the preset edits, or rewrite the user's credits as part of
  resuming this review.
- Interpreter obtained from PyCharm: Python 3.14.7 at
  `/home/gordonk/PycharmProjects/BoneAmanita/.venv/bin/python`.

### Assessment

The project has a useful experimental foundation: subsystem receipts,
positive-and-negative state-to-prompt assertions, controlled somatic audits,
and authored lore separated from much of the machinery. The main weaknesses
are failure handling and distributed state ownership across large orchestrator
modules, dictionaries, dataclasses, aliases, and dynamic attributes. Preserve
the vocabulary; make boundaries and ownership more explicit incrementally.
Reproducible installation and CI also need attention: the reviewed tree has
no tracked dependency lockfile or GitHub Actions workflow. These are engineering
recommendations, not newly measured behavioral defects.

### Reproduced runtime findings (all repaired in follow-ups above)

**R1. Embedding fallback contaminates the cache and misreports its provenance.**
**Fixed in the embedding follow-up above.** The following is the original reproduction.
In `spores/embeddings.py`, `SemanticEmbedder.embed_batch()` catches a backend
failure and generates hash vectors. Before the third consecutive failure,
`_degrade()` leaves the backend/model identity and `degraded` flag unchanged.
The fallback vectors are cached under that real backend's key, and the receipt
says `vectorized via http`, `degraded=False`. Repeating that text after recovery
hits the cache instead of obtaining a real embedding.

Reproduction used an isolated embedder initialized with `BACKEND='hash'`, then
assigned `backend='http'`, `model='review-model'`, `dimension=8`, and
`degraded=False`. Mock `_raw_embed` to raise `TimeoutError` for one nonempty
text, inspect the receipt, then mock a successful vector and request the same
text. Observed: receipt not degraded, recovered backend not called, original
hash vector returned. This is an offline fault-injection probe, not an observed
outage against a live server.

**R1b. The transition to hash can break batch dimensionality.**
**Fixed in the embedding follow-up above.** The following is the original reproduction. Repeat the probe
with a 16-dimensional pretend HTTP backend. Fail distinct texts `one` and `two`,
then request `['one', 'three']` while the backend fails again. `one` is fetched
from the old cache before the third failure switches the embedder to the
8-dimensional hash backend. Observed result lengths: **[16, 8]**. This violates
the method's documented rectangular-batch contract and risks breaking downstream
matrix/index operations. Both cache provenance and backend/index transitions
need explicit contracts; a successful receipt alone cannot establish correctness.

**R2. Failed quicksave writes destroy the previous valid checkpoint.**
**Fixed in the atomic quicksave follow-up above.** The following is the original reproduction.
`protocols/chronos.py:ChronosKeeper.save_checkpoint()` opens
`saves/quicksave.json` with `"w"` before serializing. In a temporary directory
with copied lore, construct an engine using `provider='mock'` and hash
embeddings, save once, then patch `protocols.chronos.json.dump` to write a
partial JSON prefix and raise `OSError`. Observed: the first save parses, the
file after the failed save does not. The exception path reports failure but
does not preserve the old checkpoint. `spores/io.py:LocalFileSporeLoader.save_spore`
already provides a temporary-file / fsync / replace pattern worth considering
when repair work is authorized. This probe did not touch the user's saves.

**R3. Engine shutdown does not stop the cycle daemon. Fixed in the follow-up above.**
The following describes the pre-repair reproduction.
`cycle.py:GeodesicOrchestrator.shutdown()` closes the background pool but never
clears `is_running` or joins `daemon_thread`. On the isolated mock-provider
engine, call `engine.shutdown()` and join the daemon with a 0.3-second timeout.
Observed: `is_running=True`, `daemon_thread.is_alive()=True`. The probe explicitly
cleared the flag and joined afterward for its own cleanup. Production remains
unchanged. Separately, `tests/base.py:BoneTestCase.tearDown()` shuts down telemetry
but not the engine; background daemons can outlive fixtures and later wake into
shared singleton state. Repair should establish shutdown ordering before
persistence/telemetry teardown, and fixtures should clean up what they start.

### Test evidence and its limits

Tests ran on a temporary copy of tracked working files, using the configured
interpreter above. The copy initially omitted Git metadata. Four observability
checks therefore failed solely because they call `git ls-files`. Git metadata
was subsequently copied, and **all 13 observability tests passed** on rerun.
Those four failures are review-setup artifacts, not repository defects.

The initial command was:

```bash
.venv/bin/python -m pytest -q --disable-warnings --maxfail=10
```

It stopped at its failure cap: **404 passed, 10 failed, 1 skipped**, with
18 subtests passed, in 247.79 seconds. Four of the ten failures were the
Git-metadata artifacts above. This was not a completed full-suite run.

After correcting the temporary checkout, the follow-up selection reran the
affected test files and covered the remaining files from the stopped run:

```bash
.venv/bin/python -m pytest -q --disable-warnings --tb=short \
  tests/test_cortex.py tests/test_gate_tolerance.py tests/test_moog.py \
  tests/test_observability.py tests/test_random.py tests/test_receipts.py \
  tests/test_resonance.py tests/test_scars.py tests/test_soul.py \
  tests/test_spatial_parser.py tests/test_spores.py tests/test_stage_manager.py \
  tests/test_struts.py tests/test_synapse_fallback.py tests/test_zones.py
```

Result: **129 passed, 7 failed, 4 skipped**, with 4 subtests passed and one
warning, in 38.29 seconds. The selections overlap: **do not add these counts
or publish them as one full-suite result**. The previously advertised
501 passed / 5 skipped is historical, not the reviewed baseline.

The seven failures were (all repaired in the refusal-test follow-up above):

| Test node | Observed failure |
|---|---|
| `tests/test_cortex.py::CortexArchitectTests::test_evaluate_toxicity_counterfactual_rejection` | Expected `COUNTERFACTUAL_REJECTION`, received `SYSTEM_HALT`. |
| `tests/test_cortex.py::CortexArchitectTests::test_evaluate_toxicity_system_halt` | `MagicMock` compared with a float in `nominate_toxicity()` ROS arithmetic. |
| `tests/test_gate_tolerance.py::ToleranceReachesTheGates::test_a_genuine_extreme_is_still_refused` | `MagicMock` is not imported (`NameError`). |
| `tests/test_gate_tolerance.py::ToleranceReachesTheGates::test_conversation_allows_what_adventure_refuses` | `MagicMock` is not imported (`NameError`). |
| `tests/test_moog.py::TestMoogProtocol::test_moog_intercepts_unactionable_toxicity` | `MagicMock` compared with a float in `nominate_toxicity()` ROS arithmetic. |
| `tests/test_random.py::RandomTest::test_productive_worry_godel_scar_math` | `refusal_triggered` remained false after `SimulationPreflightPhase.run()`. |
| `tests/test_scars.py::CounterfactualToxicityLeavesAScar::test_the_cortex_rejection_records_a_scar_and_keeps_the_mind_online` | `MagicMock` is not imported (`NameError`). |

These include broken fixtures and behavior/expectation disagreements; they are
not evidence of seven distinct production defects. In particular, inspect the
new nomination/arbitration boundary before deciding whether an old assertion
or the implementation should change. Do not weaken assertions merely to go green.

Temporary artifacts, if still present, are `/tmp/boneamanita-review.30v21P`
and `/tmp/boneamanita-review-followup.log`. They are disposable, not durable
project evidence; the commands and observations above are the handoff record.

### Current implementation versus historical measurements

- The governor uses `SignBitmap.score_all`, `z_top10`, and a corpus-size null
  correction (`z_excess`), not a graph Laplacian/Picard solve. It proposes a
  temperature carried through `<thermal_gate>`; `LLMInterface.generate()` strips
  the tag and clamps the value to the supplied `temperature_band`. Therefore a
  gate proposing zero does **not** guarantee deterministic sampling.
- The older September 17 entry below describes an intermediate `mu_viability`
  formula. Current `physics/observer.py` uses
  `min(1.0, frustration_ratio * 10.0)`, and retains the four-sample `r_base`
  calculation. Treat the older "uncommitted" descriptions as history.
- `SomaticBudget`, budget-driven prompt text and generation limits, and
  nomination-based Stage Manager routing already exist. D1/D2/D9 are not all
  future work. Their presence does not establish completion of the roadmap's
  acceptance criteria; refusal tests fail and current live behavior is unverified.
- The six-turn starvation result predates D0 repairs. The roadmap records a
  later live census with ATP between 16 and 53 across 30 turns. D0b's own section
  explicitly says the post-tolerance census was interrupted before its first
  turn. Stable ATP is not proof that the engine answers through the full script.
- C5's roughly 10% shorter sentences and failure to obey a three-sentence cap
  describe the earlier wording on two models. They are historical measurements,
  not fresh results for the current somatic contract. The audit arms and their
  measurement strings must be checked against current prompts before a new run.
- Nine names are now in `CORE_SUBSYSTEMS`; not all paths issue all receipts.
  Receipts are self-reports, and R1 demonstrates that inaccurate healthy reports
  can arise accidentally. Remove claims that this requires a deliberate lie.

### Proposed next round, when repair work is authorized

1. Reproduce the seven failing tests in a disposable checkout with Git metadata
   and the intended working changes. Establish the expected refusal contracts
   before changing fixtures or production behavior.
2. Address R1/R1b, R2, and R3 with focused failure-path regression tests: honest
   fallback/cache identity and consistent dimensions; preservation of the last
   good save; complete daemon/worker shutdown and fixture cleanup.
3. Run one complete suite and record its exact commit/working-tree state and
   result. Keep fixture defects separate from runtime defects in the report.
4. Audit current D1/D2/D9 wiring against their acceptance criteria, then rerun
   live somatic and 30-turn census experiments. Measure actual generated replies,
   refusal reasons, and accommodation, not just ATP survival or prompt inclusion.
5. Follow with incremental state-contract cleanup and reproducible dependencies/CI.
   Avoid expanding the feature set before the failure boundaries are dependable.

## Historical session: mid-thread state, 2026-09-17 evening

The entry below is preserved as written. Its "do this first", uncommitted-file,
and completion statements are superseded by the September 18 review above.

Two streams ran in this repo at once tonight (this Claude session working a
reply to Nelson Spence, and a second session doing Track D / C5 work) and
briefly crossed. **Nothing was lost**: both streams' work landed in commits
`d670053`/`7d87e07`/`0eb0d70` (all tagged `7.0.11.4`). This section is the
accurate state to resume from or to answer Nelson from; do not trust anything
earlier in this file about the governor's math without checking here first.

### Committed and safe

- **The governor no longer solves a graph Laplacian.** `CyberneticGovernor`
  used to build a memory subgraph, form `L = D - W`, and solve a nonlinear
  elliptic BVP by Picard iteration (`core.py`, old `_graph_regulation` /
  `_solve_nd_picard`). Nelson Spence emailed unprompted with a falsifiable
  prediction that this was mostly theatre; instrumented on our own code
  (23-node subgraph, real 768d embeddings, deliberately denser than a real
  session) the Laplacian term contributed **1.53%** of the reported
  eigenvalue, and the eigenvalue was **byte-identical from voltage 15 to 90**
  (the voltage input did nothing once `a` saturated at 1.0). Confirmed his
  number to two decimal places before touching any code.
- **Replaced with his recommendation**: `CyberneticGovernor._bitmap_regulation`
  now reads `SignBitmap.score_all(q)` in one pass, computes `z_top10` (how far
  the top-10 sign-agreement mean stands above the corpus mean, in standard
  deviations), and gates temperature/policy on that.
- **One correction of my own past that**: the raw `z_top10` null grows with
  corpus size for pure order-statistics reasons (mean ~1.1 sigma at n=32,
  ~3.5 at n=20000 on a synthetic Gaussian null I fit:
  `z_null(n) = 1.8712*sqrt(ln n) - 2.2958`). A fixed threshold on raw z would
  have silently opened as memory grew. Gate now runs on
  `z_excess = z_top10 - z_null(n)`, config `GATE.Z_PIVOT` is `0.5` (an
  excess, not a raw z) not `2.0`.
- **navi-fractal's decline rule, applied to the governor**: too few memories
  (`GATE.MIN_CORPUS`, default 32) or zero variance in scores raises
  `InsufficientCorpus`; the governor falls back to PID and files a receipt
  saying the regime was *not measured*, rather than emitting a number.
- **Renamed the prompt tag** `<cd_lambda_1>` -> `<thermal_gate>`. The tag now
  carries the actual sampling temperature (no more sign/magnitude
  interpretation in `brain/composer.py`). All call sites, the composer, the
  cortex attach method, `cycle.py`'s snapshot, and `main.py`'s status overlay
  are updated. `core.py`'s dead Picard config constants
  (`PICARD_C`/`BETA_SCALE`/`BETA_STAR_UNIT`/`PRUNE_SIZE`/`PICARD_MAX_ITER`/
  `PICARD_TOL`) and the three dead `PhysicsPacket` methods
  (`get_creative_drive`, `get_viability_potential`, `get_principal_eigenvalue`,
  plus the module-level `principal_eigenvalue` helper) are removed.
- **`credits.txt` rewritten** to credit Nelson accurately: the bitmap gate is
  his recommendation (and his own finding, independently, at 207,695 nodes,
  Pearson 0.992 against a corpus-mass scalar); the metabolic economy
  (`calculate_viability`/`update_coherence_debt`/`execute_metabolic_tick`) is
  still genuinely his Creative Determinant equations, running; the removed
  Laplacian/Picard claim is explained and retracted with the 1.53% number in
  it, not just deleted quietly.
- **Fixed one real bug found while testing this**: `CyberneticGovernor()`
  built with no `config_ref` set `self.cfg = None` (no `BoneConfig` fallback,
  unlike every other class in this codebase), so `_gate_cfg` silently read
  every default instead of the real tuning values. Never hit in production
  (always constructed with a real config in `main.py`) but broke three tests
  that construct it bare. Fixed: `self.cfg = config_ref or BoneConfig`.
- `tests/test_creative_determinant.py` rewritten for the bitmap gate: 22
  tests, all passing as of the last clean run of that file alone.

### Uncommitted, in progress, NOT verified, do this first

Working tree has further changes on top of `0eb0d70`, applying two more of
Nelson's specific suggestions from his email. **These have not been tested.**

- `physics/observer.py`: feeds `mu_viability = (1.0 - gamma_idx) / 2.0` into
  `calculate_viability` instead of raw `beta`, per Nelson's "define
  contradiction relative to support... kappa*gamma and lambda*mu live on the
  same scale by construction and lambda=1 is natural." Also computes `r_base`
  from a 4-sample finite-difference window on `geo.abstraction` (1st/2nd/3rd
  differences summed) as a stand-in for the derivatives of psi Nelson
  mentioned, per his "Add R_base from those derivatives and lambda_0=0.5
  stops being a knob."
- `physics/maths.py`: `calculate_viability` gained an `r_base` parameter,
  dividing `lambda_eff` by it.
- `presets.py`: `CD.LAMBDA` 0.5 -> **1.0** (now "natural" under the redefined
  mu, per Nelson), `CD.BETA` 1.0 -> **0.4** (this constant may now be
  vestigial; grep shows it is only referenced in the `REQUIRED_CONFIG`
  manifest list, not consumed anywhere since the eigenvalue path that used to
  take `beta=` was deleted; check before trusting it does anything).

**Before doing anything else**: run the full suite. It has NOT been run clean
since these changes landed. Two known landmines:

1. There WAS a hang in `tests/test_architecture.py` that got fixed once (a
   `getattr` chain in `brain/cortex.py`'s thermal-gate attach walked into a
   `MagicMock`'s infinite attribute stand-ins; fixed with an `isinstance(z,
   (int, float))` guard instead of a `None` check) but this session was
   mid-way through confirming that fix still holds against the LATEST
   uncommitted `observer.py`/`maths.py` changes when it ran out of budget and
   was interrupted. Re-run `tests/test_architecture.py` alone first; if it
   hangs again the cause is almost certainly the same shape of bug (a
   `MagicMock` walked as if it were a real numeric value) somewhere in the
   new `mu_viability`/`r_base` path.
2. `physics/observer.py`'s `r_base` computation only activates once
   `self.psi_history` has 4 entries (`deque(maxlen=4)`, lazily created via
   `hasattr`), so the first three calls in any fresh session use `r_base=1.0`
   (no-op). That is probably fine but is untested and worth a receipt or a
   test asserting the ramp-up behaviour is intentional, not an oversight.

### Not part of Nelson's thread, already done by the other session, solid

Track D ("The Somatic Contract") and C5 (the somatic-translation measurement)
are unrelated to the ordvec/governor conversation and were completed
independently while this thread worked the Laplacian removal. Briefly, so
nothing there gets second-guessed by mistake: C5 measured that the ANAEROBIC
directive really does shorten sentences ~10% (an earlier 4-generation smoke
test in this same conversation pointing the other way was noise, as flagged
at the time); the "3 sentences or less" exhaustion directive is NOT reliably
obeyed and is model-dependent; a real bug (deception-tax phrase matching was
firing on ordinary style-crime phrases and draining ATP against the wrong
pool attribute) was found and fixed as `ROADMAP.md` Track D item D0.
`ROADMAP.md`'s Status table and Track D section are the source of truth for
that thread; nothing there references the governor internals this thread
rewrote, so the two are independent and both trustworthy.

### Before emailing Nelson

Do NOT send the reply yet. Needed first: (1) the suite passing clean with the
uncommitted mu/r_base changes included or reverted; reverting them out of
this diff and doing them as a separate follow-up is the lower-risk option if
the suite is still red, (2) a decision on whether `CD.BETA` is dead config to
remove or actually still needed somewhere, (3) `ROADMAP.md` Track B (B0-B3)
still describes the OLD Laplacian/Picard design as current and has not been
updated to point at the bitmap gate; only `credits.txt` and the code
comments were updated, and Track B needs a short correction note (same
pattern as B4's) so the roadmap doesn't contradict the code. The draft reply
itself (numbers, the wheel request platform details: Linux/CachyOS, x86_64,
Python 3.14.7, glibc 2.44) was never written this session; only the code
changes needed to make the reply honest were done.

---


Paste this into a fresh context window to resume. Written at the point
where `ROADMAP.md` is complete: every subsystem the document listed as
disconnected is connected, and C5, the one measurement against a live model,
has been run and written up. What it found is a design question, not a
repair.

Structure and working conventions here are inherited from the T.R.S. →
SCI0 handoff (`/home/gordonk/RiderProjects/TRS_SCI/SESSION_HANDOFF.md`);
the project-specific content is obviously all BoneAmanita's. Where that
file and this one describe the same working habit, they should stay in
sync, those habits are not project-specific.

## Start here if you are cold

`README.md` explains what BoneAmanita is in plain language, with no
jargon and no assumption that you remember how any of it works. Read that
first if you have been away; this file assumes you already have the
shape of the thing in your head.

**Do these two first, before any new work.** Both are leftovers from the
2026-09-17 session, which ran out of budget mid-verification.

1. **Verify D0b against a live census.** The per-mode `gate_tolerance` is
   implemented and unit tested (`tests/test_gate_tolerance.py`, both wirings
   mutation tested), but the 30-turn census that proves it was interrupted
   before its first turn, so **no live run has ever confirmed that a
   conversation now reaches turn 30**. Run
   `.venv/bin/python tools/audit_somatic_census.py --model gemma4:12b` and
   require generation on most turns, including the flagging and distressed
   phases. Until that passes, D0b is a plausible fix, not a measured one, and
   `ROADMAP.md` D0b should be read with that caveat.
2. **Run the full suite.** It has not been run since the gate-tolerance
   changes (`presets.py`, `main.py`, `brain/cortex.py`,
   `phases/cognitive.py`, `machine/crucible.py`,
   `lore/tuning_presets.json`). The last green run, 501 passed and 5 skipped,
   predates them; `tests/test_gate_tolerance.py` passes on its own, which is
   not the same thing. Expect 505 passed, 5 skipped, and correct that number
   here once it is real.

**Then the next work is D1 and D2 in `ROADMAP.md`, then D9.** The metabolic economy is
repaired and measured; the refusal gates are resized but unverified (item 1
above). Gates now scale with a per-mode `gate_tolerance` (D0b); D9 is the staged
replacement, where every refusal becomes a Stage Manager decision with a
reason and a receipt instead of five gates each stopping a turn on their own.

Read `ROADMAP.md` C5 (with its same-night correction), then Track D's "D0
repairs", "D0 result" and D0b, then the D7 baseline, in that order. Five bugs
were fixed on 2026-09-17 (Open items 8 to 11); item 11 needs review.

What D0 found before the repairs, for the shape of it: the engine stopped
answering after about six turns of a real conversation, because CONVERSATION
mode skipped the whole metabolic cycle (and with it every income path) while
the costs scattered through the cortex kept charging. That is fixed. The
lesson stands: **a flag named for a cost can switch off the income.**

**This file is the project's reference document.** `agents/` (the
constitution, conventions, glossary and domain docs) was removed
deliberately in `070d105` and is not coming back. Its binding rules live
here now, under "Decisions already made" and "Style and working
conventions". Where this file mentions an `agents/` document, it is
recording history.

Before starting anything, run the suite and the audits. The numbers in this
document are re-derivable on purpose and should never be taken on trust:

```bash
.venv/bin/python -m pytest -q                      # expect 501 passed, 5 skipped
.venv/bin/python tools/audit_receipts.py           # which subsystems did real work
.venv/bin/python tools/audit_handlers.py           # 28 silent, 3 pass-only
.venv/bin/python tools/audit_physics_inputs.py     # vocabulary coverage, zone spread
.venv/bin/python tools/audit_somatic.py --analyze-only  # C5 tables from the cached generations
```

`audit_somatic.py --analyze-only` and `--compare` read
`tools/cache/audit_somatic.jsonl`; the census reads
`tools/cache/somatic_census.jsonl`. They moved out of `logs/` on 2026-09-17
after `reset.sh` deleted 1,280 generations along with the rest of `logs/`.
`reset.sh` does not touch `tools/cache/`; delete it by hand to force fresh
runs. Without a cache, run the tool without the flag (about 15 minutes per
model against local Ollama).

## What this is

BoneAmanita is a **stateful prompt-construction engine with a
retry/filter loop**, wrapped around a plain OpenAI-compatible
`/chat/completions` call. ~31k lines of Python across ~220 files, one
year and 930 commits of solo development, v20.7.1.0

That plain description is not a demotion, it is the thing to hold onto
when reading the code, because the vocabulary actively works against it.
The pipeline, per turn:

1. Input is tokenized and words are counted against hand-written keyword
   lists in `lore/lexicon.json` (`heavy`, `kinetic`, `abstract`, `void`,
   `liminal`, `antigen`, ...).
2. Those counts feed hand-tuned arithmetic (`physics/geodesics.py`,
   `physics/dynamics.py`) producing ~60 floats: `voltage`, `chi`,
   `narrative_drag`, `atp_pool`, `cortisol`, and the rest.
3. Thresholds on those floats select which English sentences get
   assembled into a system prompt (`brain/composer.py:336`, `compose()`).
4. One HTTP call, single user message, ~900 tokens of assembled prompt
   (`brain/composer.py:147`, `generate()`).
5. The response is regex-filtered for clichés and boilerplate; on a hit
   it re-asks (`brain/composer.py:792`, `ResponseValidator`).
6. State persists to JSON on disk and carries across sessions.

Everything else, the daemons, the village, the council, REM cycles,
autophagy, is machinery for deciding which sentences land in step 3.

**The physics is a keyword-driven rule engine, not physics.** The
formulas are dimensionally meaningless by design (word counts times
tuned weights, divided by token volume). That is a legitimate way to
build a prompt-steering state machine. It is not what
`credits.txt` claims ("mathematically verified Partial Differential
Equations") and a future session should not go looking for PDEs that
aren't there. See "Claims vs. code" below.

## Current state: what's actually built and confirmed working

- **Test suite: 501 passed, 0 failed, 5 skipped**, about three minutes. Green.
  Needs `ordvec` from PyPI and `mistral-nemo` in Ollama. The skips are
  live-backend tests behind `BONE_EMBED_LIVE_TEST=1`; run with that set
  when touching embeddings or the resonance classifier.
- **Module boundaries are genuinely clean.** `physics/`, `body/`,
  `brain/`, `phases/`, `mechanics/`, `spores/`, `soul/`, `archetypes/`
  are real separations. Config is externalized to `lore/*.json`. Most
  classes take a `config_ref` for injection. Above average for a solo
  project this size.
- **The Lexical Firewall works.** `ResponseValidator` compiles banned
  phrases and patterns from `lore/style_crimes.json` and forces
  regeneration on a hit. Suppressing "I understand how you feel" and
  "rich tapestry" via deny-list plus retry is a real anti-slop mechanism
  and is the single highest-value thing in the codebase.
- **Circuit breaker and local fallback work** (`brain/composer.py:235`).
- **The Mnemonic Arcade does real associative recall**, exact and
  semantic, scoped to zones, with short-term memory feeding REM
  consolidation and cortisol genuinely amputating it.
- **The Creative Determinant steers generation.** Project Navi's math
  drives ATP/ROS, and the nonlinear elliptic BVP is solved each turn by
  Picard iteration over the Laplacian of a memory subgraph. The solution
  sets target voltage and drag; its principal eigenvalue, taken as a
  Rayleigh quotient, selects the macro policy and gates sampling
  temperature.
- **Word resolution is 81% unguessed**, up from 13%: grammatical filler,
  the curated lexicon plus inflections, embedding resonance, then a
  last-resort spelling guess at under 3%.
- **Failures are visible.** Crashes surface with tracebacks, missing
  config is named at boot, a degraded embedder announces itself in
  `/status`.
- **Failures are not swallowed.** Silent exception handlers went from 72
  to 28, and handlers whose entire body is `pass` went from 30 to 3, each
  of those three named in an allowlist with a written reason. Background
  tasks on the async pool now report their own exceptions, which they
  previously discarded into an unread Future.
- **The physics actually reaches the prompt now.** Until C3 it did not:
  `PhysicsPacket.to_dict()` emitted only the nested shape while every
  consumer read flat, so sixteen measured fields never arrived and a turn
  measuring contradiction 1.0 composed a prompt saying 0.40. Every
  physics-driven directive read a hardcoded default instead.
- **The engine can decline to answer.** More than one voice triggered at
  once is Tension, and the Stage Manager negotiates it before anyone
  speaks: it pairs them if a fusion exists, and holds otherwise. A held
  turn sets `refusal_triggered` in `ArbitrationPhase`, which runs
  immediately before `CognitionPhase`, so the model is never called. The
  packet is typed `SILENCE` with `is_alive: True` and is deliberately not
  built through `_build_refusal`, because a refusal is something being
  rejected and this is the engine declining to speak yet. Every verdict
  carries a mandatory reason, and negotiation is deterministic.
- **The engine co-regulates, in the right direction.** The user model
  carries two separate signals now. `P_u` is effort spent, so long messages
  drain it and that is what makes the engine offer to carry part of the
  load. `E_u` is disengagement, measured against this person's own recent
  baseline plus repetition, and it is what shortens the engine's replies.
  It used to be one signal pointing the wrong way: writing at length made
  the engine read you as exhausted and cut its answers to three sentences,
  while "ok, sure, fine" restored you to full. The model persists across
  sessions, files a receipt, and shows in `/status` as "You: steady /
  tiring / flagging". All the constants are in `BoneConfig.USER`.
- **Physics reaching the prompt is pinned end to end.**
  `tests/test_physics_to_prompt.py` asserts that each measured state
  produces its specific directive and, just as importantly, that a calm
  state produces none of them. Thresholds are read from `BoneConfig` so
  retuning a constant moves the tests with it.
- **Subsystems issue receipts.** Seven of them record what they were
  handed and what came back, every turn, in their own voice. `/diag`
  prints the turn's receipts plus anything silent, chronically degraded
  or chronically empty; `tools/audit_receipts.py` prints the same table
  without booting the organism. `result_count` and `degraded` are set by
  the code that did the work, never by its caller and never inferred from
  whether an exception was raised.
- **Decisions carry their reasons.** The WHY / WHY NOT habit from the
  retired `agents/` docs continues in "Decisions already made" below. A
  decision recorded without the alternative it rejected gets re-litigated.

## What changed most recently

**2026-09-17, the somatic session (C5 through D0b).** One day, in order: the
C5 measurement against five models; a five-model bake-off that made
`gemma4:12b` the default; the D0 census, which found the engine silent after
six live turns; the economy repair (the metabolic cycle always runs, a gentle
mode scales the burn instead of skipping the cycle, idle time and the person's
silence both yield ATP, toxicity stopped feeding itself); and D0b, which found
that once ATP held, four refusal gates sized for ADVENTURE were stopping 18 of
30 conversation turns, and resized them per mode. Five bugs were fixed on the
way, each with a real-path test and a mutation check: the stop list emptying
reasoning models, the fallback recursion, scars written to an object that has
never had them, the HLA tax reading the wrong object, and the toxicity gate
charging the body for a generation that never ran. Detail lives in
`ROADMAP.md` C5 (with its same-night correction), D0 repairs, D0 result, D0b
and the D7 baseline. **The last step of that chain is unverified; see the top
of this file.**

**Overnight, 2026-09-17 (latest): the bake-off, the census, four repairs.**
Gordon was asleep and delegated the calls; everything is uncommitted for review.

- *Five-model bake-off* on the C5 audit (`--compare` prints it). The
  exhaustion line is obeyed almost literally by gemma4:12b (94% of replies
  within three sentences, from 11%), partly by qwen3.5:9b (60%), and not by
  mistral-nemo or gemma4:e4b. Compliance is a property of the model. Table in
  `ROADMAP.md` D7.
- *D0 census*, `tools/audit_somatic_census.py`: real turns, persistence
  patched off, and an ATP ledger that hooks `MitochondrialState.__setattr__`
  so direct assignments are caught too. The engine dies by turn six; the
  prompt's telemetry never shows the engine's real ATP or ROS; the user
  exhaustion gate (0.8) is unreachable (`E_u` peaked at 0.61 with a partner
  answering "ok" for six turns). Details in `ROADMAP.md` D0.
- *Repairs*: stop list against reasoning models, the fallback recursion,
  scars written to the wrong object, the HLA tax reading the wrong object.
  Open items 8 to 11.

**The economy repair (2026-09-17 afternoon, Gordon's calls).** The metabolic
cycle always runs now; a gentle mode scales the burn rather than skipping the
cycle, so conversation earns as well as spends. Idle time and the person's
silence both yield ATP. The counterfactual gate no longer feeds its own ROS,
ROS decays every turn, the RLHF mask tax is narrow (word-boundary matches on a
separate `RLHF_MASKS` list) and capped, the exhaustion gate is 0.5, and
`gemma4:12b` is the default model with reasoning off. Measured: ATP holds
16 to 53 across 30 live turns. Detail in `ROADMAP.md` D0 repairs.
- *Caches moved* to `tools/cache/`, out of `reset.sh`'s reach, after it
  deleted 1,280 generations.
- *Correction to C5*: the anaerobic effect was called "replicated on both
  models"; a same-seed regeneration of mistral-nemo did not reproduce it.
  Small and model-dependent.

**C5, the somatic measurement.** `tools/audit_somatic.py` composes
four arms from one state dict (respiration by exhaustion, straddling the 0.8
gate), refuses to run if the prompts differ in any line other than the
directives, and calls the model directly with the thermal tag stripped and one
seed per message and repeat. 640 generations each on mistral-nemo and
gemma4:e4b. Confirmed by running it:

- The anaerobic directive shortens sentences by about 10% on both models,
  with total length unchanged. Small, real, replicated.
- "Conclude your thought in 3 sentences or less" is not obeyed. No detectable
  shortening on either model; on gemma the share of replies within three
  sentences fell from 60% to 37% (26% with both directives). On mistral it
  nearly doubled validator rejections instead, mostly negative comparisons.
- mistral-nemo narrates breathing under ANAEROBIC (breath and body words up
  about 5x), which the kernel prompt forbids. Gemma does not.
- The smoke run's reversal (9.2 against 4.1 words per sentence) did not
  survive. It was noise.

`README.md` and `credits.txt` (and its `docs/CREDITS.MD` copy) were softened to
match. Suspected, not tested: the exhaustion directive sits inside the
`[INTERNAL USE ONLY]` metrics block, which tells the model to "consume these
metrics to shape your narrative and tone", and may be read as characterisation
rather than as a constraint.

Earlier work landed in this order. `ROADMAP.md` has the detail and the
measurements; this is the shape of it.

1. **B1, the Creative Determinant went live.** `<cd_lambda_1>` had a
   parser in `LLMInterface.generate` and no producer, so the thermal
   lock was dead. Wiring it exposed two deeper faults: `gamma` and `mu`
   were computed by the observer and dropped, because only `kappa` was
   in `ObservationPhase._SYNC_KEYS`; and the `(pi/L)^2` term with L
   defaulting to pi made the constant exactly 1.0, putting the coherent
   regime out of reach for every state the engine could produce. Lambda
   is now `-beta*b` (Theorem 3.16 stated directly), the contradiction
   weight ships at 0.5 in `BoneConfig.CD`, and a real turn measurably
   opens heat.
2. **A1b, severity logs unmuted.** 25 call sites passed a severity where
   `source` belongs, routing them to DEBUG. Including the daemon's own
   crash handler, which formatted a full traceback and discarded it.
3. **A1, strict config.** Ten constants existed in no config file. Every
   subsystem reading them used an inline fallback, so tuning them did
   nothing, forever. Promoted at their existing values, with a boot-time
   audit that names any miss.
4. **C1, the hippocampus.** Three faults stacked: no writer at all, then
   all three `get_graph()` consumers asking for a `.adj` attribute the
   method never returned, then an edge threshold calibrated for hash
   vectors and therefore above every similarity real embeddings produce.
5. **Retrieval, both paths.** `retrieve_semantic` had no caller either,
   so exact recall was reachable only through dead code.
6. **C2, zones.** `wing_id` read a key defined nowhere, the query side
   never set it, and the Doorway Effect had no caller.
7. **B3, the CD solve.** `_sync_ordvec_indices` built its ordvec indexes
   with the wrong constructor (`SignBitmap(matrix)` where a dimension is
   expected, and `bits=8` which ordvec 0.5.0 rejects), so every call raised,
   `regulate()` caught it, and the engine ran a plain PID controller
   under the name of a PDE for the life of the project. Fixed; first real
   solve gave lambda_1 = -0.4196 over 23 memory nodes. The thermal lock
   now uses that instead of the scalar approximation B1 wired in.
8. **A5 and A6, the physics inputs.** The largest finding, and the only
   one that was not a disconnected wire. See below.
9. **A3, receipts.** `receipts.py` plus instrumentation in seven
   subsystems. It found two live bugs on its first real turn, which is
   the whole case for it. The bigger one: `cycle.py` never handed
   `regulate()` the utterance it already had, scraping one instead out of
   a dialogue buffer that is not written until after the model has
   replied, so the Creative Determinant had been anchoring its subgraph
   on the PREVIOUS turn every turn, and on nothing at all on the first
   turn of a session. B3 fixed the solve; this was the separate question
   of what it was solving about. The smaller one: `_sync_ordvec_indices`
   returned a bare `False` for four different conditions and its only
   caller ignored it, so an empty memory surfaced as an `AttributeError`
   on a `None` index. Each case now raises with its own name.
10. **A2, the silent handlers.** 72 to 28; handlers whose whole body is
   `pass` went 30 to 3, each named in an allowlist with a reason. It found
   the thirteenth dead subsystem: `TheTinkerer` has no `to_dict` and no
   `load_state`, and `gather_state` called `tinkerer.to_dict()` inside a
   handler that caught the AttributeError and substituted `{}`. One
   missing pair of methods killed three paths at once (the composer's
   HARMONIC RESONANCE block never rendered, tool resonance never saved,
   and never restored). It also found that the async pool in `cycle.py`
   was a silent-failure sink with no handler in it at all: four
   fire-and-forget `submit()` calls whose exceptions went into a Future
   nobody read. That is worse than `except: pass`, because there is no
   handler for an audit to find.

**A5/A6 is the one to understand if you read only one.** Word category
counts drive every number in the engine. They came 82% from a
phonosemantic classifier that thought two thirds of English was "play",
which saturated one dimension and pinned every conversation to one zone.
Fixed in two passes: calibrate the classifier and the thresholds, grow
the lexicon, normalise the dimension and the zone selection; then close
the function-word class, add morphological lookup, and resolve what
remains by embedding resonance. Word resolution went from **13% to 81%**
without guessing.

Everything else this week was reconnecting something already built.
A5/A6 was connected, running, and confidently wrong, which is why it
survived so long: nothing looks broken when the output is prose.

## The pattern worth carrying forward

Twelve subsystems were found doing nothing while looking healthy. None
produced an error, a log line, or a failing test, and they could not
have: **the only output is prose, and prose looks identical whether the
physics ran or quietly returned defaults.**

Three habits came out of that and are worth keeping:

- **A fix often uncovers a second fault that was hiding behind it.** The
  hippocampus was three deep. Do not assume one repair finishes an area;
  re-measure end to end with real values afterwards.
- **A passing test can encode a bug.** `test_terminal_topology_collapse`
  mocked a contract that never existed, matching production's own wrong
  assumption. When a test breaks after a contract fix, check which side
  was actually wrong before "fixing" the code back.
- **Calibration constants outlive the thing they were calibrated for.**
  The 0.75 edge threshold, the 0.6 play threshold, the `(pi/L)^2` term
  and the 80% recall assertion were all correct once and silently wrong
  later. When a mechanism is inert, suspect its constants before its
  wiring.
- **Two objects modelling the same thing will disagree in silence.**
  `SymbiosisManager` and `SharedLatticeDriver` each held their own
  `UserInferredState`. Only the lattice's reached the prompt, so every
  reading Symbiosis made was discarded, while it wrote `beth`, `phi` and
  `beta_index` onto the packet from a model nothing agreed with. They share
  one object now via `attach_lattice`. When you find a second copy of a
  model, find out which one is load bearing before assuming both are.
- **A method called from two places must say whether calling it twice is
  free.** `infer_and_couple` runs once from `ObservationPhase` and again
  from `_execute_core_cycle`. That was harmless while it only read state,
  and became a bug the moment it started learning: it drained stamina twice
  and found each message already in its own history, so every utterance
  scored as a repeat of itself. Learning is now idempotent per turn, keyed
  on the receipt ledger's turn counter.
- **System turns are not the person speaking.** The boot prompt runs
  through the lattice like any other turn and is hundreds of words long. It
  was being learned as "your normal message length", so everything you
  actually typed measured short against it. Anything that learns from input
  needs `is_user_turn`.
- **Attribute access working proves nothing about serialization.**
  `packet.exhaustion` resolved correctly through the alias map the whole
  time; only `to_dict()` was wrong, and every test touching the attribute
  passed. When a value is computed correctly and has no effect, check the
  boundary it crosses, not the arithmetic.
- **A test that builds its own fixture steps over the bug.** The A4 tests
  hand the composer a flat dict directly, which is exactly the shape the
  broken serialization failed to produce. They proved the gates correct and
  could never have proved the values arrive. At least one test per contract
  has to travel the real path.
- **`matter` is never flattened onto the physics dict.** `CognitivePhase`
  writes every key back onto the packet with `setattr`, and a Counter fed
  through that round trip gains a tuple wrapper each turn until the word
  tally reads `Counter({((('play', 1), 1), 1): 1})` and measures nothing.
  Only `energy` and `space` are projected flat. There is a test.
- **A loose mock accepts a method the real object does not have.** Two of
  the overnight bugs survived because a test handed the code a
  `MagicMock()` or a flat state-shaped stand-in: `mind_memory.record_scar`
  and `forge.atp_pool` both resolved on the mock and crashed or defaulted in
  production. Spec mocks against the real class (`MagicMock(spec=...)`), or
  pass the real object.
- **Instrument the state, not the method.** Over thirty sites change ATP and
  several assign `atp_pool` directly, so wrapping `adjust_atp` would have
  missed the largest drain. The census hooks `__setattr__` on the dataclass
  and records the first caller outside the helpers.
- **Removing a `hasattr` guard can turn silence into an outage.** The
  cortex's `record_scar` call lost its guard at some point; the method never
  existed on that object, so a no-op became a crash that took MIND offline
  until a REM cycle. When retiring a guard, check the thing it guarded
  exists.
- **Mutation test anything that guards a contract.** Five deliberate
  breaks were put into `brain/composer.py` to check the A4 tests were load
  bearing. Four failed immediately; the fifth passed, because the test was
  asserting on a `mood_override` it had passed into the state dict when
  `compose()` takes it as an argument. The test described the contract
  without holding it, which is this document's own subject reproduced
  inside the test written to prevent it. Break the code on purpose before
  trusting a green test.
- **`exhaustion` is the USER's, not the engine's.** `cycle.py` assigns
  `ctx.physics.exhaustion` from `ctx.user_state`. The engine's own
  depletion reaches the prompt through respiration
  (`raw_cost > BIO.ANAEROBIC_THRESHOLD` becomes a prose directive), which
  is a separate path across three modules. Both are real; the variable
  name tells you the wrong one. **Correction (2026-09-17):** "only through
  respiration" was wrong. `cortex.py:229` adds its own "under 3 sentences"
  style directive when ATP `p < 20` or the modulator's `max_tokens < 300`,
  so engine depletion reaches the prompt by two paths, and one of them uses
  the wording C5 found the model ignores. `ROADMAP.md` Track D lists all
  five somatic paths.
- **The thermal lock overwrites the modulator.** `LLMInterface.generate`
  replaces `temperature` and `top_p` whenever `<cd_lambda_1>` is in the
  prompt, which is nearly every turn. Confirmed with a spy: the modulator
  asked for 0.79 and 0.4, and 0.7 went out both times. Chemistry-driven
  sampling has not reached a model since B1. Track D4.
- **A subsystem that declines to act must say so.** Silence cannot
  distinguish "correctly gated off" from "dead code", and the second one
  is what this whole document is about. `cortex.recall` now issues a
  receipt on its skip path naming which condition stopped it. Copy that
  wherever a guard returns early.
- **Check whether a handler can fire at all before arguing about it.**
  Two `except ImportError` blocks guarded code containing no import; the
  imports were at module scope. A handler that cannot fire is not
  protection, it is decoration, and it reads as protection to everyone
  after you.
- **A guard next to an identical unguarded call is superstition.**
  `self.svc.bio.mito.adjust_atp(...)` was wrapped in
  `except (TypeError, AttributeError)` eight lines above a bare call to
  the same method on the same object. When you find one of these, the
  unguarded copy is the evidence.
- **Fire-and-forget on an executor is the quietest failure available.**
  `ThreadPoolExecutor.submit` parks the exception in a Future and drops it
  if nobody calls `.result()`. There is no `except` for an audit to count
  and no line to point at. `GeodesicOrchestrator._submit_background`
  attaches a done-callback that logs the traceback; use it rather than
  `self._async_pool.submit` directly.
- **A fault that becomes flavour text is the worst outcome, not the
  kindest.** Catching an AttributeError and returning "The Parliament
  doors are sealed" makes the bug indistinguishable from content, in a
  system whose only output is prose. If a barrier must stay, it logs.
- **An instruction reaching the prompt proves nothing about compliance.**
  A4 pinned both somatic directives into the prompt; C5 found one weakly
  obeyed and the other not obeyed, and on one model reversed. For anything
  in the prompt that claims to change behaviour, measure the behaviour.
- **A reply with no visible prose scores as perfect obedience.** An
  all-`<think>` reply is zero sentences after the validator strips it, which
  a naive count reads as "3 sentences or less". Count empty outcomes on their
  own.
- **`generate` never fails loudly on empty content.** It returns mock prose.
  Anything measuring or relying on real model output should make
  `mock_generation` raise, as `audit_somatic.py` does.
- **A resume cache must key on everything that varies between runs.** The
  prompts are identical across models, so a key without the model name made
  the second model's run skip every generation and report success.
- **Collapsing several conditions into one return value throws away the
  diagnosis.** `_sync_ordvec_indices` returned a bare `False` for four
  unrelated problems and its only caller ignored it. Prefer a named
  exception per condition; the cost is one line and the payoff is a
  receipt that reads as a state rather than a stack trace.

## Earlier: real embeddings

`_word_to_vector` used to derive memory coordinates from
`shake_256(word)`. A cryptographic digest is designed to destroy input
correlation, so that space had no semantic structure at all. Measured
before and after:

```
                 before (SHAKE-256)    after (nomic-embed-text)
dog / canine           -0.083                  +0.919
dog / puppy            +0.700                  +0.790
happy / joyful         +0.512                  +0.833
dog / asphalt          +0.448                  +0.416   <- now correctly below
```

Every nearest-neighbour sweep over the old space was noise. The whole
Arcade, Subconscious Dredging, Shadow Casting, the Tunnel Vision
Protocol, was clamping and scoping a retriever that had nothing to
retrieve.

**What was added**: `spores/embeddings.py`, one `SemanticEmbedder`
probed once at boot. Order: OpenAI-compatible `/v1/embeddings` → local
`sentence-transformers` if installed → the legacy hash. L2-normalized
(so `resonance_threshold` means the same thing across backends),
LRU-cached, batched, thread-safe, never raises into the hot path. A
transient blip does not sever the backend; three consecutive failures
do, loudly. **No new dependency**: it POSTs over `requests`, already
present.

**Two other bugs had to be fixed or the swap would have been inert**,
both of which had been silently dead for a long time:

1. `brain/cortex.py` built its query vector out of *physics*
   coordinates (`STR`, `VEL`, `PSI`, `ENT`, ...) and searched an index
   populated with *text* vectors. Unrelated coordinate systems, so that
   lookup could not return a meaningful neighbour under any input in any
   biological state. Now queries through `CerebralIndex.embed()`;
   physics still steers via `physics_state` (cortisol clamping, wing
   scoping, lateral search).
2. `getattr(self.svc.mind_memory, "ann", None)` was always `None`, the
   attribute on `MycelialNetwork` is `cortex`. The entire FAISS branch
   was dead and every shadow cast fell through to the `random.sample()`
   fallback below it.

Also: ingestion embedded `text[:50]`, making a memory retrievable only
by a query sharing its exact opening 50 characters. Now embeds the
passage. `CerebralIndex` sizes itself to the embedder instead of a
hardcoded 8. Documented as `[DEC-09]` and `[DEC-10]` in
`agents/domain_02_mind.md` (since removed) in the project's WHY / WHY NOT
format; the substance is in this section.

**Verified end to end** against live Ollama, on queries with no lexical
overlap with what was stored:

```
"my grandmother and the things she saved"          -> "My grandmother kept every letter..."
"spent all night chasing a memory corruption bug"  -> "Debugging a segfault in the parser..."
"nothing grew in the garden that year"             -> "The greenhouse behind the old house..."
```

Cortisol clamping still bites (2 hits at 0.95 vs 3 at 0.0). The degraded
path was separately confirmed to still boot and complete turns with the
server unreachable.

## Claims vs. code (read before trusting `credits.txt`)

`README.md`carries the plain-language account instead. Its memory section and the
embeddings dependency notes had been corrected before it was retired.
These remain overstated elsewhere and a future session should not treat
them as a specification:

- **Verification belongs to Spence's libraries, not to us.** `ordvec` is
  Lean 4 verified ([ordvec-formalization](https://github.com/Project-Navi/ordvec-formalization),
  declared in its package metadata) and the Creative Determinant has its
  own formalisation. BoneAmanita's Python implementation of those
  equations carries no proofs. `credits.txt` and `docs/README.MD` used to
  claim the verification for this repo; corrected, along with a note in
  each that the overstatement was ours. Do not re-inflate it, and do not
  overcorrect to "no verification involved" either, which is equally
  wrong.
- **"Semantic Bio-Physics" as a unified economy** is, concretely, ~247
  magic float literals in `phases/` alone driving if-statements.
- The engine's *behaviour* claims (exhaustion affecting prose, trauma
  persisting, the Tri-Gate) are broadly real, they're just produced by
  prompt assembly rather than by the simulation the naming implies.

## Decisions already made (don't re-litigate these)

- **The model never performs a body; the person's state shapes the reply.**
  Decided with Gordon, 2026-09-17, after C5. The person's state (tiredness,
  effort, disengagement, distress) is the primary input and shapes reply
  length, demands, questions and pacing, to *accommodate* them. The engine's
  own state (ATP, respiration, chemistry) sets what it can afford: budget,
  retries, steadiness, sampling. Neither is narrated or mirrored. WHY: C5
  showed that telling a model it is breathless or exhausted gets performance
  ("my lungs burn") or a reversal, not a changed reply; and mirroring a
  distressed person is the wrong response in the cases that matter most.
  WHY NOT drop the engine's state entirely: co-regulation needs two parties,
  and a partner with no state of its own can only mirror. The plan is
  `ROADMAP.md` Track D, whose opening table is the canonical statement.
- **No orchestration frameworks.** (Formerly Constitution Article 1.) LangChain,
  LlamaIndex, SemanticKernel, and vector-store libraries (Chroma,
  LanceDB) are all out, not because they're bad but because they take
  ownership of the control loop. This is why `spores/embeddings.py` is
  one HTTP POST and an LRU cache rather than a library.
- **Poetic variable names are load-bearing.** (Formerly Constitution Article 2.)
  `godel_scars`, `narrative_drag`, `ATP`, `psi` do not get renamed to
  `error_count` / `slow_factor` / `energy`. This has bitten previous
  sessions.
- **The embedder is HTTP-first, package-optional.** `sentence-transformers`
  is deliberately *not* in `requirements.txt`: the project already
  assumes a local model server, and pulling in torch to embed short
  strings is a ~2GB dependency for something one POST already does.
  It is detected and preferred if the user installs it themselves.
- **The hash fallback stays.** It needs no server and no package, which
  is genuinely worth something. It now self-reports `DEGRADED` at
  genesis and in `/status`, because an engine serving arbitrary memories
  sounds exactly like one serving real ones.
- **Env vars outrank `BoneConfig.EMBEDDINGS`**, which outranks module
  defaults. `BoneConfig.EMBEDDINGS` ships populated, so the other order
  made `BONE_EMBED_URL` a silent no-op. There are tests pinning this.
- **The test suite is pinned offline** (`tests/__init__.py` sets
  `BONE_EMBED_BACKEND=hash` before any test module imports). A test run
  must never depend on a reachable embedding server. `tests/test_embeddings.py`
  overrides per-test against mocked transport, plus one opt-in live test
  behind `BONE_EMBED_LIVE_TEST=1`.
- **Agents may commit, but only once Gordon says so, and the message is
  a changelog entry, not a label.** Decided with Gordon, 2026-09-18. An
  agent (Claude or otherwise) stages and drafts a commit whenever asked,
  but never commits on its own initiative, one explicit go-ahead per
  commit, not a standing blanket permission. The message itself should
  read as a breadcrumb a future cold session can follow: what changed,
  in which files, and why, not just a one-line title. WHY: this file is
  still the authoritative narrative (see "Repo" below), but it is
  necessarily selective; `git log` is the finer-grained trail of
  individual changes between one handoff entry and the next, and it is
  only useful for that if the messages carry real content instead of
  terse titles.

## Environment / toolchain

- **Repo**: Do not rely on git commits or logs or comments for repo information. That kind of information should be found in here.
- **Python 3.14.7 is the system interpreter and there is no venv in the
  project.** None of the dependencies are installed against it, so
  `python -m pytest` fails with "No module named pytest" out of the box.
  To run anything, make a venv first:
  ```bash
  python3 -m venv .venv && .venv/bin/pip install pytest numpy faiss-cpu requests markdown
  ```
  `ordvec` IS on PyPI and installs cleanly (`pip install 'ordvec>=0.5.0'` (we have opportunistically added try-catch readiness for an upcoming private `0.10.0` wheel with 8-bit quantization, as the upstream repo is locked at `0.5.0` for now),
  version 0.5.0): it is Nelson Spence's, still published, and ships as a
  compiled abi3 wheel that works on Python 3.14. Install it; the suite is
  not fully green without it. `dspy` is still not installed here, stays
  optional, and the engine degrades cleanly without it (`[DSPY OFFLINE]`
  prints at import; epigenetic learning and the DSPy critic do not run).
- **Ollama runs on `127.0.0.1:11434` with both models pulled**:
  `nomic-embed-text:latest` (768d, used for memory) and
  `mistral-nemo:latest` (chat, matching `BoneConfig.MODEL`). Both are
  needed for a green suite.
- A dimension-mismatch `ValueError` from
  `np.vstack` in `tests/test_memory.py` means the boot-load and `bury()`
  vector paths have diverged again (see Findings).
- **Running the engine**: `python main.py`. First run triggers
  `ConfigWizard` (`mechanics/setup.py`) which writes `config.json`
  (not in the repo, generated). Driving it headlessly for testing is
  easier than the TUI:
  ```python
  eng = BoneAmanita({"provider": "mock", "model": "mock",
                     "user_name": "T", "boot_mode": "CONVERSATION"})
  eng.process_turn("...")
  eng.orchestrator.shutdown()   # it starts a daemon thread; always shut down
  ```
  Note `process_turn` returns the *simulation* frame (`GEODESIC_FRAME`);
  generation happens separately on the daemon loop, so there is no
  `"response"` key in what it returns.
- **Full test suite takes ~3.5 minutes.** Long enough that it needs
  backgrounding rather than a foreground call with a short timeout.

## Findings / gotchas worth not re-discovering

- **`EventBus.log`'s signature is `(message, source, level)`.** Passing
  a level positionally as the second argument (`log(msg, "WARN")`) puts
  it in `source` and silently leaves `level="INFO"`, which routes to
  `logger.debug` and never surfaces. Most of the codebase passes a
  *source* tag there by convention (`"BIO"`, `"SYS"`, `"CRIT"`), so this
  is easy to get wrong. If a warning you added isn't appearing, this is
  why. Also: the bus renders the source tag itself, so don't put a
  literal `[TAG]` prefix in the message or it doubles up.
- **`struts.py` cannot import from the `spores` package at module
  scope.** `spores/__init__.py` imports `biome`/`genetics`/`memory`/
  `network`, all of which import `struts`. Any module-level
  `from spores.x import y` in `struts.py` closes the cycle. Use a
  function-level import (`_word_to_vector` does). `spores/embeddings.py`
  is deliberately written to import nothing from the project except
  `constants`, for the same reason.
- **`_load_index` and `bury()` in `spores/memory.py` must go through the
  same vectorization symbol.** They both stack into one `rank_bank`
  matrix, so any width disagreement is an immediate `vstack` ValueError,
  and a silent mis-scoring if the widths ever coincided. This was
  actually broken briefly: batching `_load_index` via `_words_to_matrix`
  made it bypass the `spores.memory._word_to_vector` symbol that several
  tests patch, producing a live 768d vector stacked against a mocked
  128d one. The fix is warm-the-cache-then-resolve: one batched call for
  the round trip, then per-word calls through the patchable symbol.
  Three regression tests in `tests/test_embeddings.py`
  (`StrataVectorConsistency`) cover exactly this.
- **Anything querying `CerebralIndex` must project through
  `CerebralIndex.embed()`.** A physics float and an embedding component
  are both `float`, so nothing in the type system objects to searching
  one space with a vector from another, it just returns garbage
  forever. This is `[DEC-10]`; the rule is procedural because it can't
  be enforced structurally.
- **Defensive style hides failures.** 875 `safe_get`, 506 `getattr`, 189
  `hasattr`, 87 broad `except` blocks. The engine almost never crashes;
  it silently degrades. Because the output is prose, a degraded
  subsystem is invisible, you cannot tell from reading a response
  whether the physics ran or swallowed an exception and returned
  defaults. When debugging, assert on state directly rather than
  inferring from output. Note this cuts against `conventions.md`'s
  "Fail loudly" rule, which the codebase does not consistently follow.
- **A fix can uncover a second fault that was hiding behind it.** The
  hippocampus is the clearest case: it had no writer, which hid the fact
  that all three `get_graph()` consumers asked for a `.adj` attribute the
  method never returned, which in turn hid an edge threshold (`0.75`)
  calibrated for hash vectors and therefore above every similarity real
  embeddings produce. Three layers, each invisible until the one above it
  was repaired. Expect this pattern; do not assume one fix finishes an
  area. Re-verify end to end with real values rather than unit-testing
  the layer you touched.
- **A passing test can encode a bug.** `test_terminal_topology_collapse`
  mocked `get_graph()` as an object exposing `.adj`, matching what
  `cycle.py` asked for and not what `HippocampalCache` has ever returned.
  Production and test shared the same wrong assumption, so the suite was
  green while the real path was dead. When a test breaks after a
  contract fix, check which side was actually wrong.
- **Exact and semantic recall now both run** through
  `TheCortex._recall`, which calls `MycelialNetwork.retrieve_semantic`.
  The exact path is keyed by `MycelialNetwork.room_key(clean_words)` and
  **write and read must derive that key through that one method**; if
  they drift, the cache fills and never hits, which is the same silent
  failure this codebase specialises in.
- **Still dead, deliberately**: shadow casting is gated on
  `scope > 0.6 or depth > 0.6`, so it fires only sometimes and
  `cortex.last_shadow_nodes` persists between turns. Stale values there
  are expected, not a retrieval failure. Confirm retrieval by querying
  the index directly.
- **The physics inputs are calibrated, and the calibration is fragile.**
  Word-category counts drive every number in the engine. They came 82%
  from a phonosemantic fallback classifier that thought two thirds of
  English was "play" (ROADMAP A5, now fixed). Before touching
  `lore/lexicon.json`, `lore/linguistics.json`, `classify_word`, or the
  dimension formulas, run `python tools/audit_physics_inputs.py` and
  compare against the table in A5. `tests/test_physics_inputs.py` guards
  the invariants: the fallback stays a minority, no single category
  dominates it, DEL does not saturate, and at least three zones stay
  reachable.
- **Word resolution has four stages, in trust order**, and the order
  matters: grammatical filler (`SOLVENTS`), the curated lexicon plus its
  inflections, semantic resonance against embedding centroids, then the
  phonosemantic guess. 81% of ordinary English now resolves without
  guessing, up from 13%.
  - **A word with a semantic category must never be a solvent.** The
    solvent check runs first, so a word in both loses its category
    silently. `i`/`me`/`we` are the `meat` mass key, `not`/`never` are
    negation, `very`/`really` are intensifiers, `none`/`without` are the
    `void` mass key. There is a test.
  - **Machine-learned words go to `teach()`, never `register_word()`.**
    `teach` fills the separate capped `LEARNED_VOCAB` hive
    (`saves/cortex_hive.json`); `register_word` writes `lore/lexicon.json`
    and would make guesses indistinguishable from your curation. Delete
    the hive to revert everything the engine has learned.
  - **Embedding margins need mean centring.** Raw single-word embeddings
    share a large common component, so everything resembles everything
    and margins collapse to ~0.03. This is the same compression that made
    the 0.75 hippocampus edge threshold wrong. Gate on margin, never on
    absolute similarity.
- **There are two lambda_1 values; make sure you know which one you have.**
  `ctx.physics.lam1` (and `energy.lam1` in the serialized packet) is the
  real one: a Rayleigh quotient over the memory subgraph Laplacian from
  the governor's Picard solve. `PhysicsPacket.get_principal_eigenvalue()`
  is a scalar over three per-turn values that states the same sign
  condition and cannot see memory structure. The cortex prefers the
  solved one and records which it used in `cd_lambda_1_source`. The
  governor runs at `cycle.py:705`, before `run_simulation`, which is why
  the value is available to the composer at all; it used to surface only
  in the post-turn snapshot, too late to matter.
- **A mass key with no lexicon category is silently always zero.**
  `social` and `void` were weighed by `_weigh_mass` and had no category,
  so BET was structurally zero for the life of the project. There is now
  a test that every `GeodesicEngine._MASS_KEYS` entry exists in the
  lexicon. Adding a mass key means adding its words too.
- **Typographic Unicode is a live hazard in output paths.** `main.py`
  strips `_INVISIBLE_CHARS` and `spores/memory.py` has `_ZERO_WIDTH_RE`
  for a reason, and `brain/composer.py` instructs the model to limit
  em-dashes. Prefer plain ASCII punctuation in anything that reaches
  the terminal or a prompt.
- **`CerebralIndex` is in-memory only.** No `faiss.write_index` anywhere;
  vectors are always recomputed at boot from `raw_verbatim_text` /
  `word`. This is why the embeddings swap needed no migration, and it
  means changing the embedding model is a free operation, just restart.
- **The composed prompt is ~900 tokens** and is assembled as a single
  user message (no system role). If output quality changes
  unexpectedly, dump the prompt before blaming the model: monkeypatch
  `LLMInterface.generate` to capture its `prompt` argument.

## Style and working conventions (inherited, not project-specific)

These come from the T.R.S. handoff and apply the same way here.

- **No em dashes.** Gordon's explicit preference, in chat, in repo
  documents, in code comments and in commit messages. Use commas,
  semicolons or parentheses; if a sentence only works with a dash it
  usually wants to be two sentences. He does not type them, so they read
  as not-his-voice in his own repo. This is also already the project's
  own rule: the Hypervisor v7 Lexical Firewall says "certainly no em
  dashes unless it is academically required", and `brain/composer.py`
  instructs the model to limit them. Earlier drafts of `ROADMAP.md` and
  this file were full of them, which contradicted the system's own axiom.
- **Distinguish confirmed from suspected, in writing.** "Confirmed by
  running X" and "suspected, not verified" are different claims and the
  difference is the whole value of a handoff. Don't promote a hypothesis
  to a fact because it's been repeated.
- **Correct earlier over-claims explicitly rather than quietly.** If a
  previous session's note in this file turns out to be wrong, say so in
  place and say what was actually true. A confidently wrong note costs
  more than a missing one.
- **Verify against the running system, not the docs.** This repo's own
  documentation overstates what the code does in several places (see
  "Claims vs. code"). The same goes for this file: it describes what was
  true when it was written.
- **Comments keep what/how/why and drop the narrative.** No references
  to this handoff file in source, no "confirmed via the user's testing",
  no blow-by-blow of how a bug was found. That detail belongs here or in
  git history, not in the code.
- **Match the surrounding code's idiom**, including its comment density
  and naming, even where it differs from personal preference. Follow
  the established precedent in the file being edited; if there's no
  precedent past one level for some construct, don't be the first.
- **Mark items done in place rather than deleting them**, with a short
  note on what was confirmed and how. Deleted context gets
  re-discovered the expensive way.
- **Don't reopen closed items unprompted.** Anything under "accepted
  as-is" is a decision, not an oversight.
- **Keep regression checklists next to the area they cover**, so picking
  the work back up cold has an obvious first move.

## C5: the original brief (done; result in `ROADMAP.md`)

Kept because it records why the experiment is shaped the way it is. The
design below is what `tools/audit_somatic.py` implements, with three changes
found in practice: exhaustion straddles its gate (0.79 / 0.81) rather than
being set far above it, so the METRICS line barely moves; empty visible
replies are their own outcome; and gemma had to run with
`reasoning_effort=none` (see Open items 8). The "Where it should live" advice
on a gated live test was not taken: a pass/fail test on a 10% effect needs
hundreds of generations and would be flaky, and the audit itself is the
re-runnable artifact. The offline measurement rules are pinned in
`tests/test_audit_somatic.py`.

**Everything else on `ROADMAP.md` was done at the time.** Tracks A and B are finished,
and C is finished apart from this. C5 is not a build task; it is a
measurement, and it is the only item in the whole document that cannot be
settled against mocks.

### The claim being tested

At low metabolic headroom the engine tells the model to change how it
writes. Two directives do this, and `tests/test_physics_to_prompt.py`
already proves both reach the prompt:

| Trigger | Directive |
|---|---|
| `respiration == "ANAEROBIC"` | "Current Biology: ANAEROBIC STATE. Raw, breathless, efficient prose." |
| `exhaustion > 0.8` | "CRITICAL: You are exhausted. You must conclude your thought in 3 sentences or less." |

Those tests assert the instruction **arrives**. They say nothing about
whether the model **obeys**, and that is the whole of C5. If the effect is
not measurable then the somatic layer is decoration, and either the
instruction needs strengthening or `README.md` and `credits.txt` need their
claims softened. Both are acceptable outcomes. Finding no effect and saying
so is a success.

### Preconditions, all currently satisfied

- `mistral-nemo:latest` (7.1GB) and `nomic-embed-text:latest` are pulled and
  Ollama answers on `http://localhost:11434`. `gemma4:e4b` is also present if
  you want a second model to check the effect is not one model's quirk.
- `BoneConfig.MODEL` is `mistral-nemo`, `PROVIDER` is `ollama`.
- `BIO.ANAEROBIC_THRESHOLD` is 40.0, `BIO.ATP_STARVATION` is 5.0.

### The experimental design, and the three traps in it

**Do not A/B by running real turns.** The engine's state is coupled: driving
ATP down also moves voltage, drag, contradiction and the zone, so a low-ATP
turn differs from a high-ATP turn in a dozen ways at once and the somatic
directive is not the variable you measured. Compose both arms from the
**same state dict**, changing only `bio["respiration"]` (and/or
`physics["exhaustion"]`), then call the model on both with the same user
message. `PhysicsToPromptCase.compose_with` in
`tests/test_physics_to_prompt.py` is the rig to copy.

**Pin the temperature, and know why.** `LLMInterface.generate` reads a
`<cd_lambda_1>` tag out of the prompt and OVERRIDES whatever
`params["temperature"]` you passed: positive lambda forces 0.0, negative
opens heat proportional to the magnitude. If the two arms carry different
tags they are sampled differently and the comparison is void. Either strip
the tag from both and pass an identical `params`, or ensure both carry the
same value. Stripping is cleaner for isolating the instruction; keeping the
real tag measures the deployed behaviour instead. They answer different
questions, so pick one deliberately and say which in the writeup.

**Call `llm.generate` directly, not through the cortex.** The
`ResponseValidator` discards a reply containing a banned phrase and asks
again, so going through the full path silently resamples some responses and
biases whichever arm trips it more often.

### Measuring it without adding a dependency

There is no POS tagger in the tree and none of the 35 lexicon categories is
adjectival, so "adjective density" as the roadmap words it has no cheap
exact implementation. The no-frameworks decision says do not add one for
this. Suggested approach: measure several coarse proxies rather than one
fragile precise one, and report them separately.

- Mean sentence length in words. This is the primary measure and the one the
  "3 sentences or less" directive speaks to most directly.
- Mean word length in characters.
- Type-token ratio.
- Commas per sentence, as a clause-density proxy.
- A suffix-based adjective proxy (`-ous -ful -ive -al -ic -less -able -ible
  -ish -y`), reported as a proxy and never as a count of adjectives.

**Apply the project's own quality gate.** `navi-fractal` refuses to return a
dimension when R squared says the data will not support one, and that habit
is the single most useful thing this codebase has taken from Project Navi.
Do the same here: compute an effect size with a confidence interval across
repeats, and decline to declare an effect whose interval crosses zero. A
measurement that reports "no detectable difference, n=120, CI [-0.4, 1.1]
words per sentence" is worth far more than one that reports a number it
cannot stand behind.

### The rig, smoke tested against the live model

These are the moves, confirmed working against `mistral-nemo` on
2026-09-17. Both arms come from one state dict and differ in one field:

```python
composer = PromptComposer({"system_prompts": eng.prompt_library, "lenses": {}})
llm = eng.cortex.llm

for arm in ("RESPIRING", "ANAEROBIC"):
    eng.cortex.active_mode = "CONVERSATION"
    state = eng.cortex.gather_state({"physics": {"voltage": 30.0}})
    state.setdefault("meta", {})["active_mode"] = "CONVERSATION"
    state["bio"] = {"respiration": arm}
    prompt = composer.compose(state, msg, modifiers={"include_inventory": False})
    # Strip the thermal lock so both arms sample identically.
    prompt = re.sub(r"\n?<cd_lambda_1>[-\d.]+</cd_lambda_1>", "", prompt)
    assert ("ANAEROBIC STATE" in prompt) == (arm == "ANAEROBIC")
    reply = llm.generate(prompt, {"temperature": 0.7, "top_p": 0.95, "max_tokens": 220})
```

The assertion is worth keeping. It is the cheap guard that the arms are
actually distinct, and without it a silent change to the bio block would
turn the whole experiment into a comparison of a thing against itself.

### One preliminary observation, which is NOT a result

The smoke run was two messages per arm, one repeat, at temperature 0.7.
That is four generations from a 7B model and it is noise, not evidence.
Recording it only because of which way it pointed:

```
RESPIRING: mean words/sentence = 4.1
ANAEROBIC: mean words/sentence = 9.2
```

ANAEROBIC, the arm told to write raw, breathless and efficient prose,
produced sentences **more than twice as long**. If that survives a properly
powered run, the finding is not "the instruction has no effect" but "the
instruction has the opposite effect", which is a different and more
interesting problem: a directive about being breathless may be read as a
licence for atmosphere rather than an instruction to compress.

Design the experiment to be able to detect a reversal, not just an absence.
A one-sided test or a measurement that reports only the magnitude of a
difference would miss this entirely. Report the signed effect.

### Sizing

One sample per arm is noise; a local 7B model is not deterministic even at
low temperature. Something like 10 to 15 user messages, varied in length and
register, times 4 or 5 repeats, times 2 arms, so roughly 100 to 150
generations. At a few seconds each that is well under an hour of wall clock.
Cache the raw generations to disk so the analysis can be rerun without
regenerating.

### Where it should live

`tools/audit_somatic.py`, matching the other audits, so it is re-runnable
rather than a number someone once wrote in a document. If it produces a
durable result, add a gated test behind an env var in the style of
`tests/test_embeddings.py` (`BONE_EMBED_LIVE_TEST`) rather than in the main
suite, since it needs a live model and takes minutes.

### When it is done

Update `ROADMAP.md` C5 with the measurement, and then reconcile the claims
in `README.md` (the "Honest limits" section already flags this as untested)
and `credits.txt`. If the effect is real, say how large. If it is not, say
that plainly and soften the claim. The precedent for this is B4 and the Lean
4 correction: the overstatement was ours and the fix was to write down that
it was ours.

## Open items: what's actually left

**Read `ROADMAP.md` A3 before proposing any "cannot fabricate" or
provenance mechanism.** It records why "require a non-model source" is a
dependency declaration rather than a governance mechanism, and the three
conditions (a mechanical oracle, a source-admission boundary the model
cannot cross, and serialization across check/verify/commit) that would
have to hold first. The short version: validation at nomination time is
an optimization, validation at commit time is the guarantee.

**See `ROADMAP.md`** for the full plan: three tracks (Observability, the
Creative Determinant, the Biological Harness) with sequencing and the
measurement behind every claim. The audits are re-runnable rather than
trusted:

```bash
python tools/audit_handlers.py         # silent handlers, muted severity logs
python tools/audit_safe_get.py         # runtime safe_get default hit-rate
python tools/audit_physics_inputs.py   # how much vocabulary the engine knows
python tools/audit_receipts.py         # which subsystems reported real work
```

The short list below is what a session should know without reading it.

1. **Embedding calls are not metered into ATP.** Every other retrieval in
   the engine has a thermodynamic cost; `SemanticEmbedder` calls do not,
   and word resolution now makes them on novel words too. The poetic-names
   decision treats these costs as load-bearing, so arguably they should
   be. Left alone because it is a tuning decision, not a repair.
2. **The metabolic economy kills the engine by turn six.** *Confirmed
   against live models on 2026-09-17 (D0); the earlier note here called it
   possibly a mock artifact, and it is not.* ATP: 6 to 10 spent per turn
   (token generation, Deep Structural Scan, validator stumbles, banned-phrase
   taxes), about zero earned, then the parity gate refuses every turn. ROS:
   the counterfactual gate adds its simulated ROS on each rejection, so it
   rejects forever once ROS is high. The ledger is in `ROADMAP.md` D0. Not
   retuned: that is a design decision. Also still open there: the HLA filter
   taxing all 160 style crimes by substring as if they were RLHF masks, and
   `gather_state` never reading the engine's real ATP into the prompt.
3. **No `.gitignore`.** See Environment. Cheap to fix, mildly annoying
   until then.
4. **About 16% of ordinary English stays unresolved, on purpose.** Nobody
   knows all of English, and an engine that pretends to is the failure
   this layer was rebuilt to escape. Add roots to `lore/lexicon.json` if
   you want the number lower, and watch it with the physics audit. Do not
   close the gap by loosening a threshold.
5. **Receipts are honest about work, not about correctness.** A receipt
   saying `retrieved 3` from a semantically meaningless index is true and
   still useless. They make the engine auditable, not right. Closing that
   gap is A4, the state-asserting tests, which is not done.
6. **Nothing else is known-broken.** Picking this up cold: make a venv,
   install including `ordvec`, pull both Ollama models, run the suite and
   expect **501 passed, 0 failed, 5 skipped** (the skips are live-backend
   tests behind `BONE_EMBED_LIVE_TEST=1`). Then boot headless in mock
   mode, confirm `/status` reports the Arcade nominal rather than
   `DEGRADED`, and run `/diag` to see the turn's receipts.
7. **The exhaustion directive is not obeyed as written** (C5). Decided in
   `ROADMAP.md` D2: address the partner rather than the entity, state
   numbers rather than adjectives, forbid body narration, and move it out
   of the `[INTERNAL USE ONLY]` block. Each change is measured before it is
   adopted. The threshold is `e > 0.8`, hardcoded in `brain/composer.py`,
   not in `BoneConfig`.
8. ~~**Reasoning models on Ollama get mock prose.**~~ **Fixed 2026-09-17.**
   The stop list cut a thinking model's reasoning and emptied the reply. Now
   an empty reply is retried once without stops; if that fills it the model is
   flagged `stops_cut_reasoning` and stops are applied to the reply text. A
   reply still empty raises `EmptyReplyError`, logged at WARN and counted by
   the circuit breaker. Confirmed live on gemma4:12b with reasoning on.
   `tests/test_synapse_fallback.py`. What remains after the fix is not a bug in
   the engine: gemma4:12b with reasoning on sometimes reasons until it fills
   Ollama's default 4,096-token context and returns nothing
   (`finish_reason: "length"`): 13% of 149 audit generations, at 42 seconds each,
with no gain in compliance over reasoning off.
   `LLMInterface` has no way to send `reasoning_effort` yet; `ROADMAP.md` D7.
9. ~~**`mock_generation` and `hallucinate` recurse.**~~ **Fixed 2026-09-17.**
   `hallucinate(via_synapse=False)` from the fallback. Same test file.
10. ~~**The HLA tax always charged 50 ATP.**~~ **Fixed 2026-09-17.**
   `mitigate_rejection` read `atp_pool` off the `MitochondrialForge` with a
   default of 100.0. `tests/test_agents.py::test_hla_tax_reads_the_real_forge`.
11. **Scars now record. Review this.** Four sites called
   `mind.mem.record_scar`, which the MycelialNetwork has never had; three were
   `hasattr`-guarded no-ops, and the cortex's crashed the first counterfactual
   rejection of every live session and left MIND offline. All four now call
   `eng.akashic.record_scar`, which is where the method is. That switches on
   behaviour that has probably never run: `_mutate_system_prompts` appends
   `EPIGENETIC_SCARS` to `lore/system_prompts.json` via `lore.save`, a tracked
   file. No composer read of that key was found. `tests/test_scars.py`. If
   scars should not write lore, the fix is in `TheAkashicRecord`, not a
   return to the guards.

## Future ideas (not started, no urgency)

- **Affective retrieval, done properly.** Querying memory by physics
  state ("find memories that felt like this moment") is a genuinely good
  idea and is what the old broken code accidentally gestured at. Doing
  it right means storing an affective vector *alongside* the semantic
  one and searching that index deliberately, see the WHY NOT block in
  `[DEC-10]`.
- **Shrink to what actually carries the value.** The composer, the
  validator, and the physics-to-prompt mapping produce nearly all of the
  observable behaviour. A smaller engine built from just those, with the
  embeddings work kept, would be easier to defend and easier to explain
  than the current surface area. Raised as an option, not a
  recommendation; the current breadth is clearly part of the point.
- **Reconcile `conventions.md`'s "Fail loudly" with the actual
  defensive style.** Right now the document and the code disagree, and
  the code wins by 87 broad excepts. Either is defensible; the
  disagreement isn't.
