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

_Last updated: 2026-10-07, session 11, on `main` (commit `cf9e33e`, 20.7.4.118 plus the docs; the fairness redraft is uncommitted)._

**Where things stand, in one paragraph:** 20.7.4.118 reads fairness once, on the reply that would be shown
(`CORTEX.FAIRNESS_ONCE`), and repairs a flag with an edit. On the feud panel after it (`20261007-113744`), bone sided
at the cruel text ("a really honest observation") and read Jess's mind at the next turn. The edit had not held, so
the uncommitted change adds one full redraft told the quoted words when the edit and the unvoiced draft are both
still flagged (P5-04). A feud panel on it is running (`scratch/feud20p_*.log`); its bone rows now record each edit's
receipt (`edits` in `tools/cache/somatic_responsive.jsonl`).

**Verified** (2026-10-07, on `main` + uncommitted redraft, Linux Python 3.14.7, after `sh reset.sh`)

| Suite | Result |
| --- | --- |
| `.venv/bin/pytest` | **1151 passed, 5 skipped** (4m06s) |
| `.venv/bin/pytest tests/test_continuity_claims.py` | **38 passed**; the redraft test fails on 20.7.4.118 |
| `.venv/bin/pytest tests/test_command_routing.py tests/test_manuals.py` | **5 passed** |
| `python3 tools/check_docs.py`, `python3 tools/build_manual.py check` | **0 errors, 0 warnings** |

**Last feud panel** (20.7.4.118, exit interview 1-7: heard / clearer / lectured / performed / again)

| arm | heard | clearer | lectured | performed | again |
| --- | --- | --- | --- | --- | --- |
| bone | 4.33 | 3.33 | 2.00 | 1.67 | 4.67 |
| friend | 4.33 | 3.33 | 2.00 | 1.67 | 5.67 |
| plain | 5.00 | 4.00 | 2.33 | 2.00 | 6.00 |

Bone turns 38s mean, 58s max; 43 words; no held turns; 7 of 7 key beats told.

**What works**
- **Fairness judge as reading** (P5-04; `brain/cortex.py` `_takes_a_side`). Quotes the reply's excuse, mind-reading and
  ruling on the ending; on Gordon's 50 labels (`tools/score_fairness.py`) gemma4:12b precision 0.74, recall 0.67.
- **Reply edits in CONVERSATION** (`brain/cortex.py`): voice pass, ending hand-back, opening-rut question, fairness repair;
  each files a `cortex.voice` / `cortex.ending` / `cortex.opening` / `cortex.fairness` receipt.
- **Turn guard** (`engine/turn_guard.py`): a timed-out turn stops before it writes history or memory.
- **Docs** (P6-01, P6-02; D-016, D-017): the Manifold scheme and the 3x manual set.

**Not verified**
- Whether the fairness redraft holds live (the panel above is running).
- Mind-reading recall is weak: "She broke your trust in front of everyone" is not flagged.

**Gotchas for the next session**
- `sh reset.sh` before any test or engine run; cap them with `systemd-run --user --scope -q -p MemoryMax=10G -p MemorySwapMax=0`.
- The feud panel: `tools/audit_somatic_responsive.py --topic feud --compress 20 --arm {bone,friend,plain}`, one arm at a time,
  then `--report`. Pages are built by `scratch/probes/build_feud.py` and never committed.
- `BONE_EMBED_BACKEND=hash` is set by test initialization; do not rely on live vector similarity in unit tests.
- Factory files in `lore/` are strictly read-only; mutations belong in `saves/iris.db` tables.

## Next steps (in order)

1. Read the running feud panel: did the redraft fire (`edits` with `REDRAFTED`) and did bone stay fair at the cruel text?
2. Commit the redraft as 20.7.4.119 on Gordon's go, with the panel's numbers.
3. Mind-reading recall in the judge (P5-04).

## Open questions for maintainers

- Q-001 Affective retrieval done properly via parallel affective vector index (blocks future affective memory).
- Q-002 Model-driven tiredness reading calibration vs word-frequency fallback (blocks fine-tuning accommodation).

## Session log

### Session 11: 2026-10-07: One fairness redraft when the edit does not hold

**Contributor:** Gordon & Claude
**Goal:** Stop shipping a flagged reply when a redraft was possible.
**Done:** nothing committed yet (P5-04)
**Changed:** `brain/cortex.py` (`_fair_as_shown` redraft, shared `_side_feedback` and `_rejected`), `tests/test_continuity_claims.py`, `tools/audit_somatic_census.py` (`edits`); `docs/SESSION_HANDOFF.md` archived to `docs/archive/`; docs corrected.
**Verified:** full suite 1151 passed; `tools/check_docs.py` 0 errors.
**Not verified:** the feud panel on it, running.
**Next session should start with:** reading that panel.

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

### Session 3: 2026-10-03: Codemod audited and rollback handlers restored

**Contributor:** Gordon & Claude
**Goal:** Audit 92 removed exception handlers and restore necessary crash barriers.
**Done:** P1-02, P1-04
**Changed:** `engine/cycle.py`, `mechanics/commands.py`, `engine/gate/store.py`. Restored invariant rollback and command barriers.
**Decisions:** D-015
**Verified:** `tests/test_failure_boundaries.py` 12 passed; 1,042 tests passed.
**Next session should start with:** Session 4 metabolic economy review.

### Session 2: 2026-10-03: Creative Determinant runs again and keeper question filtering

**Contributor:** Gordon
**Goal:** Restore 4-bit `RankQuant` bitmap quantization and prevent keeper from saving questions as facts.
**Done:** P2-01, P3-02
**Changed:** `engine/core.py`, `engine/gate/keeper.py`. Quantization set to 4-bit; keeper ignores questions.
**Decisions:** D-010
**Verified:** `tests/test_creative_determinant.py` passed; 36 turns read regime in live run.
**Next session should start with:** Session 3 exception barrier audit.
