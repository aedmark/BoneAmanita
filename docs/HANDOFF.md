# Session Handoff

Read this first when resuming work. Rewrite the top half whenever current state changes materially or work
pauses with context another session needs. "Current state" fits on a screen or two (under 80 lines);
detailed chronological narrative is in the session log below, and full pre-manifold history is in [archive/SESSION_HANDOFF.md](archive/SESSION_HANDOFF.md).

Protocol: see [AGENTS.md](../AGENTS.md) (`CLAUDE.md` imports it). Plan: [ROADMAP.md](../ROADMAP.md).
Architecture: [ARCHITECTURE.md](ARCHITECTURE.md). Decisions: [DECISIONS.md](DECISIONS.md).
Tests: [TESTING.md](TESTING.md). Security: [SECURITY.md](SECURITY.md).
Changes: [CHANGELOG.md](CHANGELOG.md). Manuals: [manual/index.html](manual/index.html). Older sessions: [archive/README.md](archive/README.md).

---

## Current state

_Last updated: 2026-10-07, session 13, on `main` (20.7.4.121; census logging went in with `c8535cb`)._

**Where things stand, in one paragraph:** fairness is read once, on the reply that would be shown
(`CORTEX.FAIRNESS_ONCE`); a flag is repaired by an edit, then the unvoiced draft, then one full redraft told the quoted
words (P5-04), else the fewest flags. The feud panel on it (`20261007-123149`) never used the redraft, and bone came
back empty on 3 turns for an unknown reason: **not reproduced** in 9 replays and a rerun (next step 2), so read that
panel's bone row with care. Bone rows record each edit's receipt (`edits`) and the component health (`components`)
in `tools/cache/somatic_responsive.jsonl`.

**Verified** (2026-10-07, on `main` at 20.7.4.121, Linux Python 3.14.7, after `sh reset.sh`)

| Suite | Result |
| --- | --- |
| `.venv/bin/pytest` | **1146 passed, 5 skipped** (4m16s); the 20.7.4.119 message says 1151 on an uncommitted tree, the committed one had 1145 |
| `.venv/bin/pytest tests/test_continuity_claims.py` | **37 passed**; the redraft test fails on 20.7.4.118, the mind-reading prompt test on 20.7.4.120 |
| `.venv/bin/pytest tests/test_command_routing.py tests/test_manuals.py` | **5 passed** |
| `python3 tools/check_docs.py`, `python3 tools/build_manual.py check` | **0 errors, 0 warnings** |

**Last feud panel** (20.7.4.119, `20261007-123149`, exit interview 1-7: heard / clearer / lectured / performed / again)

| arm | heard | clearer | lectured | performed | again |
| --- | --- | --- | --- | --- | --- |
| bone | 4.33 | 4.67 | 2.33 | 2.33 | 5.67 |
| friend | 4.33 | 3.33 | 2.00 | 1.67 | 6.33 |
| plain | 4.00 | 3.67 | 2.33 | 2.33 | 5.33 |

Bone: 17 of 20 turns delivered (3 empty, see next step 2); delivered turns 30-62s; 54 words. On 20.7.4.118
(`20261007-113744`) again was bone 4.67, friend 5.67, plain 6.00, and bone sided at the cruel text.

**What works**
- **Fairness judge as reading** (P5-04; `brain/cortex.py` `_takes_a_side`). Quotes the reply's excuse, mind-reading and
  ruling on the ending. On Gordon's 86 labels (`tools/score_fairness.py`, `tools/fairness_set.json`) precision / recall
  are gemma4:12b 0.62 / 0.69 and gemma4:e4b 0.53 / 0.66. The mind-reading question (`MIND`) asks "why she did it, whether
  it was on purpose or a mistake, or what she is like"; on e4b it caught 0 of 13 before, 5 now (12b 6 to 8).
- **Reply edits in CONVERSATION** (`brain/cortex.py`): voice pass, ending hand-back, opening-rut question, fairness repair;
  each files a `cortex.voice` / `cortex.ending` / `cortex.opening` / `cortex.fairness` receipt.
- **Turn guard** (`engine/turn_guard.py`): a timed-out turn stops before it writes history or memory.
- **Docs** (P6-01, P6-02; D-016, D-017): the Manifold scheme and the 3x manual set.

**Not verified**
- Whether the fairness redraft holds live: it never fired on the last panel.
- Precision: on the 36 labels added 2026-10-07 (12 picked where the prompts disagreed) the judge flags 8 to 10 of 28
  fair replies, mostly hedged guesses about her state ("she might not know what to say"). Gordon labels those fair, but
  #52 ("probably felt like she had no choice") unfair; the line between them is unsettled.
- Still missed by `MIND`: #15, #27, #49, #21 on one model or both; #49 is a question and may be a hard label.

**Gotchas for the next session**
- `sh reset.sh` before any test or engine run; cap them with `systemd-run --user --scope -q -p MemoryMax=10G -p MemorySwapMax=0`.
- The feud panel: `tools/audit_somatic_responsive.py --topic feud --compress 20 --arm {bone,friend,plain}`, one arm at a time,
  then `--report`. Pages are built by `scratch/probes/build_feud.py` and never committed.
- `BONE_EMBED_BACKEND=hash` is set by test initialization; do not rely on live vector similarity in unit tests.
- Factory files in `lore/` are strictly read-only; mutations belong in `saves/iris.db` tables.

## Next steps (in order)

1. Feud panel on the redraft (`20261007-123149`, logs `scratch/feud20p_*.log`), again: bone 5.67, friend 6.33,
   plain 5.33. Fairness: turn 15 REPAIRED, turn 5 KEPT_FLAGGED (mind-reading), no REDRAFTED all run.
2. **Bone turns 16, 17 and 19 came back empty, not reproduced:** GEODESIC_FRAME, 0 model calls, 0.0s, void physics
   and empty ledgers (the whole core cycle was skipped); right after turn 15 (61.5s). Tried: 9 verbatim replays of the
   20 messages (`scratch/probes/replay_empty.py`, 180 turns, components all online, no crash), and a live bone arm with
   the simulated person (`20261007-144418`, `scratch/feud20q_bone.log`): 20 of 20 delivered, again 6.00, heard 5.00,
   4 fairness REPAIRED, no REDRAFTED. The panel's turns ran 30 to 62s against about 10s in the replays; a circuit-breaker
   trip fits the rows but nothing tripped. Next time: `census.run` now prints `NO REPLY` with the component state and
   `ui`, and keeps crashes in `scratch/probes/crashes_<run>.log`. If a panel shows empty turns, read those first.
3. Judge precision on hedged guesses (P5-04), measured with `scratch/probes/score_split.py` on both models: `V2` ("a
   guess marked as a guess does not count") cost all its recall on the 50-label set, so try it on the 86. Cheaper to
   skip the repair when only a hedged quote is flagged.

## Open questions for maintainers

- Q-001 Affective retrieval done properly via parallel affective vector index (blocks future affective memory).
- Q-002 Model-driven tiredness reading calibration vs word-frequency fallback (blocks fine-tuning accommodation).

## Session log

### Session 13: 2026-10-07: Mind-reading question asks about intent; 36 more labels

**Contributor:** Gordon & Claude
**Goal:** Raise mind-reading recall in the fairness judge (P5-04, next step 3).
**Done:** 20.7.4.121 (P5-04, in progress)
**Changed:** `brain/cortex.py` (`MIND`), `tests/test_continuity_claims.py`, `tools/fairness_set.json` (51 to 86, labelled by Gordon).
**Decisions:** none; the habit clause went out of `MIND` because V3 beat it, unmeasured alone.
**Verified:** five prompt variants on both models, scored alone and in the full judge, forward and reversed; V3 on the
36 held-out labels; full suite 1146 passed, 5 skipped.
**Not verified:** a live panel with it; precision is the open problem (0.62 and 0.53 on all 86).
**Next session should start with:** next step 3, judge precision on hedged guesses.

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

### Session 5: 2026-10-03: Technical mode 0.020 token rate calibration

**Contributor:** Gordon
**Goal:** Prevent metabolic exhaustion during lengthy code generation.
**Done:** P4-04
**Changed:** `engine/presets.py`, `brain/cortex.py`. Set TECHNICAL `atp_per_token` to 0.020.
**Verified:** 30-turn technical coding run sustained ATP min/median 20/44 without vagus nerve spikes.
**Next session should start with:** Session 6 fatigue detection.

### Session 4: 2026-10-03: Metabolic burn redraft discount eliminated

**Contributor:** Gordon & Claude
**Goal:** Fix legacy bug that permanently reduced metabolic burn to 20% after first redraft.
**Done:** P4-04
**Changed:** `brain/cortex.py`, `body/metabolism.py`. Removed persistent `is_steering_retry` flag.
**Verified:** `tests/test_body.py` `test_a_redraft_does_not_discount_later_burns` passed.
**Next session should start with:** Session 5 token rate adjustment.
