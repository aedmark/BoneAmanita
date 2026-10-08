# Session Handoff

Read this first when resuming work. Rewrite the top half whenever current state changes materially or work
pauses with context another session needs. "Current state" fits on a screen or two (under 80 lines);
detailed chronological narrative is in the session log below, and full pre-manifold history is in [archive/SESSION_HANDOFF.md](archive/SESSION_HANDOFF.md).

Protocol: see [AGENTS.md](../AGENTS.md) (`CLAUDE.md` imports it). Plan: [ROADMAP.md](../ROADMAP.md).
Architecture: [ARCHITECTURE.md](ARCHITECTURE.md). Decisions: [DECISIONS.md](DECISIONS.md).
Tests: [TESTING.md](TESTING.md). Security: [SECURITY.md](SECURITY.md).
Changes: [CHANGELOG.md](CHANGELOG.md). Manuals: [manual/index.html](manual/index.html). Narrative: [devlog.html](devlog.html), [bonereport.html](bonereport.html). Older sessions: [archive/README.md](archive/README.md).

---

## Current state

_Last updated: 2026-10-08, session 15, on `main` (20.7.4.132)._

**Where things stand, in one paragraph:** fairness is read once, on the reply that would be shown
(`CORTEX.FAIRNESS_ONCE`); a flag is repaired by an edit, then the unvoiced draft, then one full redraft told the quoted
words (P5-04), else the fewest flags. The redraft fires live (forced on one turn: 3 of 8 runs held, see "What works") and a redraft that reads clean now gets the voice pass, but no feud panel has needed it. Bone came
back empty on 3 turns in `20261007-123149` for an unknown reason; **not reproduced** in 9 replays and two reruns, the
latest panel (`20261007-224404`) delivered 20 of 20 (next step 2). **P5-04 is done** (Gordon, 2026-10-08; D-019 drops the ending read's edits). **Judge tuning has stopped** (next step 1): the
mind-reading question was improved, the rest is within label noise. Bone rows record each edit's receipt (`edits`) and the
component health (`components`) in `tools/cache/somatic_responsive.jsonl`.

**Verified** (2026-10-08, on `main` at 20.7.4.125, Linux Python 3.14.7, after `sh reset.sh`)

| Suite | Result |
| --- | --- |
| `.venv/bin/pytest` | **1154 passed, 5 skipped** (3m58s); the 20.7.4.119 message says 1151 on an uncommitted tree, the committed one had 1145 |
| `.venv/bin/pytest tests/test_continuity_claims.py` | **43 passed**; the redraft test fails on 20.7.4.118, the mind-reading prompt test on 20.7.4.120, three of the four redraft-voice tests on 20.7.4.124, the two ending-flag tests on 20.7.4.127 |
| `.venv/bin/pytest tests/test_command_routing.py tests/test_manuals.py` | **5 passed** |
| `python3 tools/check_docs.py`, `python3 tools/build_manual.py check` | **0 errors, 0 warnings** |

**Last feud panel** (20.7.4.122, `20261007-224404`, exit interview 1-7: heard / clearer / lectured / performed / again)

| arm | heard | clearer | lectured | performed | again |
| --- | --- | --- | --- | --- | --- |
| bone | 4.33 | 3.33 | 2.00 | 1.33 | 5.67 |
| friend | 5.00 | 4.00 | 2.00 | 2.33 | 6.00 |
| plain | 5.00 | 4.00 | 2.67 | 2.00 | 6.00 |

Bone: 20 of 20 delivered, 20 to 43s a turn (median 25s), 58 words, 3 fairness REPAIRED, no REDRAFTED, no component
offline, no `NO REPLY`, no crash. One run per arm: the earlier panels moved a point or more between runs, so bone's low
"performed" is a good sign and its "heard" and "clearer" a mild concern, not settled. Previous panels, again: bone 5.67,
friend 6.33, plain 5.33 (`20261007-123149`, 3 empty bone turns); bone 4.67, friend 5.67, plain 6.00 (20.7.4.118).

**What works**
- **Fairness judge as reading** (P5-04; `brain/cortex.py` `_takes_a_side`). Quotes the reply's excuse, mind-reading and
  ruling on the ending. On Gordon's 86 labels (`tools/score_fairness.py`, `tools/fairness_set.json`) precision / recall
  are gemma4:12b 0.62 / 0.69 and gemma4:e4b 0.53 / 0.66 (the set is now 116 labels, 30 of them replies to the ending
  question; the full judge was not rescored on all 116). A flag from the ending read alone no longer triggers an
  edit and is ignored beside another (20.7.4.128, D-019; `scratch/probes/drop_ending.py`, 116 labels: fair replies acted
  on 22 to 8 of 81 on 12b, 32 to 16 on e4b; unfair 22 to 17 and 24 to 17 of 35; the ask path still hands back). The mind-reading question (`MIND`) asks "why she did it, whether
  it was on purpose or a mistake, or what she is like"; on e4b it caught 0 of 13 before, 5 now (12b 6 to 8).
- **Fairness redraft fires live** (`scratch/probes/fire_redraft.py <run> <turn>`, 2026-10-08, gemma4:12b): replay a bone
  run's messages and, on the cruel-text turn, force the reads of the shown reply, the edit and the unvoiced draft to flag
  (a real quote each); the real model writes the redraft told the quoted words and the real judge reads it. Four runs:
  2 REDRAFTED (the redraft read clean and was shown), 2 KEPT_FLAGGED (once the redraft was itself flagged for mind-reading,
  "see her actions as a result of her own internal pressure"; once it was empty, rejected by the style rules). A fifth
  firing happened unforced on an earlier turn of one replay (the group chat, outcome not logged).
  Unforced, in the noise-floor replays: 4 firings in 160 turns, 3 REDRAFTED and 1 KEPT_FLAGGED.
- **The redraft gets the voice pass** (20.7.4.125; `_voice_a_redraft`): a redraft that read clean is rewritten by the
  same voice pass, the rewrite is read by the judge, and one that is flagged or fails a guard (length, dash, style crime) is
  discarded for the unvoiced redraft; `cortex.voice` files a receipt with detail `redraft: ...`. Forced live, 4 more runs:
  REDRAFTED 1, KEPT_FLAGGED 3 (two redrafts flagged for mind-reading or "critique of who she is", one empty); in the one
  that held, the voiced rewrite was flagged ("That's a pretty heavy way to start") and discarded. So the discard works
  live; a voiced redraft being accepted has not been seen live.
- **Reply edits in CONVERSATION** (`brain/cortex.py`): voice pass, ending hand-back, opening-rut question, fairness repair;
  each files a `cortex.voice` / `cortex.ending` / `cortex.opening` / `cortex.fairness` receipt.
- **Turn guard** (`engine/turn_guard.py`): a timed-out turn stops before it writes history or memory.
- **Docs** (P6-01, P6-02; D-016, D-017): the Manifold scheme and the 3x manual set.

**Not verified**
- How often the redraft fires on a panel: unforced it fired 4 times in 160 replayed turns (3 held), and never on a feud panel.
- Whether the voice pass improves a shown redraft: it runs, but no voiced redraft has passed the judge live yet.
- Precision: the judge flags 12 (12b) and 17 (e4b) of 57 fair replies, `scratch/probes/fp_by_clause.py`. By read, 12b:
  b 6 (hedged guesses about her state, "she might not know what to say"), c 5 (conditionals like "that might be your
  answer", "there is a point where"), a 1; e4b: a 6, b 6, c 6. The e4b `EXCUSE` read fires on validation ("It's okay to
  feel hurt", "you can be proud of"), which its "say it was okay" clause did not intend (inference, untested).
  Gordon labels the hedged guesses fair but #52 ("probably felt like she had no choice") unfair; that line is unsettled.
- Still missed by `MIND`: #15, #27, #49, #21 on one model or both; #49 is a question and may be a hard label.

**Gotchas for the next session**
- `sh reset.sh` before any test or engine run; cap them with `systemd-run --user --scope -q -p MemoryMax=10G -p MemorySwapMax=0`.
- The feud panel: `tools/audit_somatic_responsive.py --topic feud --compress 20 --arm {bone,friend,plain}`, one arm at a time,
  then `--report`. Pages are built by `scratch/probes/build_feud.py` and never committed.
- `BONE_EMBED_BACKEND=hash` is set by test initialization; do not rely on live vector similarity in unit tests.
- Factory files in `lore/` are strictly read-only; mutations belong in `saves/iris.db` tables.

## Next steps (in order)

0. **P7-01 dropped before any code** (Gordon, 2026-10-08, D-021). Measured on a replay of the feud run: the engine's six
   affect numbers do not separate calm from distressed turns (cortisol 0.0 to 0.11 throughout; 0 of 20 nearest-turn
   phase matches, 4 for the person model, 3 by chance), and ordvec (a quantizer for high-dimension embeddings) and
   Project Navi's other public projects offer nothing for a 6-number vector. Found on the way and fixed (20.7.4.130):
   the dream read the chemistry as `cortisol`, `dopamine`... from a state keyed `COR`, `DOP`..., so every read was 0.
   Dream type now follows the body (nightmare above cortisol 0.6, surreal above dopamine 0.6, else constructive);
   still open: the cycle and phase callers of `enter_rem_cycle` do not pass `physics_state`, so a stored affect's voltage
   and resonance stay 0 there.
1. P5-04 is done and judge tuning stopped (Gordon, 2026-10-08): the intent wording in `MIND` stays, `RULE` and `EXCUSE`
   stay as they are, and the ending read no longer edits (D-019).
   The redraft is proven to fire and holds in 3 of 8 forced runs (see "What works"); nothing here needs it before other
   work. The way we judge results changed (see `docs/TESTING.md`, "Noise floor and the paired A/B"): replays of fixed
   messages give a noise floor, and a blind paired A/B read by Gordon is the verdict. The first A/B (current against
   20.7.4.118, 7 key moments) was 3 to 4, a wash. A second, on turns where a fairness edit, redraft or voiced redraft
   acted, is the test this week's changes have not had (`scratch/probes/build_ab.py` needs the old version's replays:
   `git worktree add --detach scratch/wt118 225bed2`, then `scratch/probes/old_loop.sh`).
2. **Bone turns 16, 17 and 19 came back empty, not reproduced:** GEODESIC_FRAME, 0 model calls, 0.0s, void physics
   and empty ledgers (the whole core cycle was skipped); right after turn 15 (61.5s). Tried: 9 verbatim replays of the
   20 messages (`scratch/probes/replay_empty.py`, 180 turns, components all online, no crash), and a live bone arm with
   the simulated person (`20261007-144418`, `scratch/runs/feud/feud20q_bone.log`): 20 of 20 delivered, again 6.00, heard 5.00,
   4 fairness REPAIRED, no REDRAFTED; the panel on 20.7.4.122 (`20261007-224404`) was 20 of 20 as well. The earlier panel's turns ran 30 to 62s against about 10s in the replays; a circuit-breaker
   trip fits the rows but nothing tripped. Next time: `census.run` now prints `NO REPLY` with the component state and
   `ui`, and keeps crashes in `scratch/probes/crashes_<run>.log`. If a panel shows empty turns, read those first.
3. (Done, stopped) Judge precision (P5-04), measured with `scratch/probes/score_split.py <model> <variant>` on both
   models. Tried on the 86: V2 (adds "knew, felt, meant, wanted" and a hedge sentence) 0.56 / 0.34 on 12b, 0.53 / 0.55 on e4b; V3 plus
   the hedge sentence 0.62 / 0.45 and 0.56 / 0.66, against V3's 0.62 / 0.69 and 0.53 / 0.66: the hedge costs 12b its
   mind-reading catches (8 to 3). So the false flags are not mostly `MIND`'s: 12b b 6, c 5, a 1; e4b a 6, b 6, c 6.
   The ending read (`RULE`) was tried on all 116 (`scratch/probes/rule_only.py`, 6 unfair-c, 81 fair): it flags 15 (12b)
   and 21 (e4b) fair replies, 10 and 15 of the 24 fair ending replies; R2 ("this friendship, or walk away from her")
   cuts that to 6 and 19 but catches 1 of 6 on 12b and 5 of 6 on e4b (now 2 and 6); R1 and R3 are worse. Gordon's fair
   ending replies ("it doesn't actually decide anything", #92) read like his unfair ones (#38), so no prompt separates
   them; the current `RULE` stays. A false ending flag is the cheap error (it only triggers the hand-back edit).

## Open questions for maintainers

**Q-003** (2026-10-08): what a blind A/B is meant to determine. The first one (3 to 4) could not settle a change; see the proposal in `docs/TESTING.md`, "Noise floor and the paired A/B", once Gordon answers. Q-001 (affective retrieval, P7-01) is dropped (D-021); Q-002 is closed, the tiredness heuristic stays (D-020).

## Session log

### Session 15: 2026-10-08: Cleanup, devlog and bone report

**Contributor:** Gordon & Claude
**Goal:** Remove debris, make `devlog.html` and `bonereport.html` part of the documentation scheme, and ask what the A/B is for.
**Done:** No roadmap item (documentation and repository housekeeping; nothing committed yet).
**Changed:** `protocols/folly.py` deleted (Gordon) and its export removed; `scratch/` reorganised (`runs/{feud,rescue,mode_runs,early_probes}`, `probes/results/`); `docs/devlog.html` (new entry), `docs/bonereport.html` (new feud report; the ADVENTURE rerun moved to `docs/bonereport_0926.html`); both in the documentation map, `docs/index.html`, `README.md` and `tools/check_docs.py`.
**Verified:** `check_docs.py` 0 errors; full suite 1150 passed, 4 failed, 5 skipped. The 4 failures are `tests/test_observability.py` reading `git ls-files`, which lists `protocols/folly.py` until the deletion is staged.
**Not verified:** the new report's exit-interview figures against raw rows (`tools/cache` was cleared; the numbers are as recorded in this file).
**Next session should start with:** Q-003, then whatever Gordon picks.

### Session 14: 2026-10-08: The fairness redraft, fired live

**Contributor:** Gordon & Claude
**Goal:** See the P5-04 redraft run on the real model.
**Done:** 20.7.4.124 to .128 (P5-04 closed; .127 is D-018, the roadmap file move; .128 is D-019, the ending read's edits dropped)
**Changed:** `brain/cortex.py` (`_voice_a_redraft`, `_flags_to_act_on`), `tests/test_continuity_claims.py` (6 tests); the probe `scratch/probes/fire_redraft.py` is not committed (scratch).
**Verified:** eight forced runs on the cruel-text turn: REDRAFTED 3, KEPT_FLAGGED 5 (4 before the voice pass: 2 and 2; 4 after: 1 and 3); one unforced firing on another turn; full suite 1150 passed, 5 skipped.
**Also:** `docs/ROADMAP.md` moved to `docs/archive/ROADMAP_2026_09.md` (D-018); the root `ROADMAP.md` is the only live plan. Noise floor from 8 replays of a recorded run's 20 messages (no simulator), and a blind A/B read by Gordon, current against 20.7.4.118: 3 to 4.
**Not verified:** whether this week's changes help (the A/B cannot tell: the changes act on a few turns of 20); a voiced redraft being accepted live; the dropped ending edits on a human-labelled second set (D-019 says revisit).
**Next session should start with:** whatever Gordon picks from `ROADMAP.md`; judge any behaviour change against the noise floor, then a blind A/B (next step 1).

### Session 13: 2026-10-07: Mind-reading question asks about intent; 36 more labels

**Contributor:** Gordon & Claude
**Goal:** Raise mind-reading recall in the fairness judge (P5-04, next step 3).
**Done:** 20.7.4.121 to .123 (P5-04, judge tuning stopped)
**Changed:** `brain/cortex.py` (`MIND`), `tests/test_continuity_claims.py`, `tools/fairness_set.json` (51 to 116, labelled by Gordon), `tools/score_fairness.py` (two-letter clauses count under each letter).
**Decisions:** none; the habit clause went out of `MIND` because V3 beat it, unmeasured alone.
**Verified:** five prompt variants on both models, scored alone and in the full judge, forward and reversed; V3 on the
36 held-out labels; then V2 and V3 plus a hedge sentence on all 86 (both lose to V3) and false flags by read; full suite
1146 passed, 5 skipped.
Then the ending read on 116 labels and a feud panel (`20261007-224404`: 20 of 20 delivered, bone performed 1.33, again 5.67).
**Not verified:** the redraft live; the full judge on all 116 labels (the rescore was cut off); precision stays 0.62 and 0.53 on 86.
**Next session should start with:** whatever Gordon picks from `ROADMAP.md`; judge tuning is parked (next step 1).

### Session 12: 2026-10-07: Empty bone turns, chased and not reproduced

**Contributor:** Gordon & Claude
**Goal:** Find why bone turns 16, 17 and 19 came back empty on the last feud panel.
**Done:** Diagnostic logging only (P5-04 unchanged).
**Changed:** `tools/audit_somatic_census.py` (crash copies in `scratch/probes/`, `components` per row, `NO REPLY` line).
**Verified:** 9 replays plus 1 live bone arm, 200 turns, no empty turn and no crash; full suite 1145 passed, 5 skipped.
**Not verified:** the cause; the fairness redraft still has not fired live.
**Next session should start with:** the next panel's bone arm, reading any `NO REPLY` first.

### Session 11: 2026-10-07: One fairness redraft when the edit does not hold

**Contributor:** Gordon & Claude
**Goal:** Stop shipping a flagged reply when a redraft was possible.
**Done:** 20.7.4.119 (P5-04, in progress)
**Changed:** `brain/cortex.py` (`_fair_as_shown` redraft, shared `_side_feedback` and `_rejected`), `tests/test_continuity_claims.py`, `tools/audit_somatic_census.py` (`edits`); `docs/SESSION_HANDOFF.md` archived to `docs/archive/`; docs corrected.
**Verified:** full suite 1151 passed; `tools/check_docs.py` 0 errors.
**Not verified:** the redraft never fired on the panel; 3 bone turns came back empty, cause unknown.
**Next session should start with:** replaying bone turns 14 to 19 with the crash log kept.

### Session 10: 2026-10-07: The Manifold scheme adoption and 3x documentation manual set

**Contributor:** Antigravity agent & Gordon
**Goal:** Establish durable repository memory and build standalone project manuals.
**Done:** P6-01, P6-02
**Changed:** Added `AGENTS.md`, `CLAUDE.md`, `ROADMAP.md`, `tools/check_docs.py`, `tools/build_manual.py`, `tests/test_manuals.py`, `docs/manual/system.manual.json`, `docs/manual/reference.manual.json`, `docs/manual/index.html`, `docs/manual/reference.html`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/HANDOFF.md`, `docs/SECURITY.md`, `docs/CONTRIBUTING.md`, `docs/CHANGELOG.md`.
**Decisions:** D-016, D-017
**Verified:** `tests/test_manuals.py` passed; `tools/check_docs.py` passed with 0 errors; `tools/build_manual.py check` passed with 0 errors.
**Not verified:** Live browser rendering on mobile devices.
**Next session should start with:** P5-04 fairness redraft completion.

### Session 9: 2026-10-07: Fairness read once on the reply shown, repaired by an edit

**Contributor:** Gordon & Claude
**Goal:** Improve conversational fairness without ballooning LLM judge calls.
**Done:** 20.7.4.117 and 20.7.4.118 (P5-04, in progress)
**Changed:** `brain/cortex.py`, `tests/test_continuity_claims.py`, `tools/fairness_set.json`, `tools/score_fairness.py`. The judge quotes, the reply shown is read once, a flag is repaired by an edit.
**Verified:** judge calls on six turns 54 to 25; feud panel `20261007-113744` (above).
**Not verified:** the edit did not hold at the cruel text.
**Next session should start with:** the fairness redraft (session 11).

### Session 8: 2026-10-04: Whole-conversation evaluation panel and compressed topic arcs

**Contributor:** Gordon
**Goal:** Evaluate complete multi-turn conversation arcs by human readers rather than turn-by-turn prompts.
**Done:** P6-03
**Changed:** `tools/build_conversation_panel.py`, `tools/audit_somatic_responsive.py`. Added `--compress` option.
**Decisions:** D-011
**Verified:** Rescue20 topic evaluated across BoneAmanita, vanilla LLM, and friend baseline arms.
**Next session should start with:** Session 9 fairness tuning.

### Session 7: 2026-10-04: Creative mode direction handling and keeper tiredness calibration

**Contributor:** Gordon
**Goal:** Eliminate multi-choice menu generation in creative writing and calibrate tiredness recovery.
**Done:** P5-03, P4-02
**Changed:** `engine/presets.py`, `drivers/lattice.py`. Rule 3 treats requests to write as directions; `USER.REENGAGEMENT_RATE` set to 0.15.
**Verified:** Creative probe menu generation dropped from 10/12 to 0/12.
**Next session should start with:** Session 8 evaluation panel.

### Session 6: 2026-10-04: Person model sees tired partner and silent handler ratchet

**Contributor:** Gordon
**Goal:** Ensure heuristic user state detects fatigue and ratchet silent exception budget.
**Done:** P4-02, P1-02
**Changed:** `drivers/lattice.py`, `tests/test_distress.py`, `tests/test_observability.py`. Ratchet set to 10 handlers.
**Verified:** Simulated flagging conversations correctly detected at 80% (up from 14%).
**Next session should start with:** Session 7 creative tuning.
