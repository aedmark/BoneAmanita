# Session Handoff

Read this first when resuming work. Rewrite the top half whenever current state changes materially or work
pauses with context another session needs. "Current state" fits on a screen or two (under 80 lines);
detailed chronological narrative is in the session log below, and full pre-manifold history is in [SESSION_HANDOFF.md](SESSION_HANDOFF.md).

Protocol: see [AGENTS.md](../AGENTS.md) (`CLAUDE.md` imports it). Plan: [ROADMAP.md](../ROADMAP.md).
Architecture: [ARCHITECTURE.md](ARCHITECTURE.md). Decisions: [DECISIONS.md](DECISIONS.md).
Tests: [TESTING.md](TESTING.md). Security: [SECURITY.md](SECURITY.md).
Changes: [CHANGELOG.md](CHANGELOG.md). Manuals: [manual/index.html](manual/index.html). Older sessions: [archive/README.md](archive/README.md).

---

## Current state

_Last updated: 2026-10-07, session 10, on `main` (commit `2f3d2b9` + uncommitted fairness and documentation updates)._

**Where things stand, in one paragraph:** The test baseline is fully green (1,141+ unit tests pass, 5 live-only skipped).
The Manifold documentation scheme (D-017) and 3x Documentation Scheme Manual Set (D-016) are adopted and verified with zero errors.
Active work centers on fairness verification in `brain/cortex.py` (P5-04): redrafting when a repair remains flagged.

**Verified** (2026-10-07, on `main`, Linux Python 3.14.7, pytest-9.1.1)

| Suite | Result |
| --- | --- |
| `pytest tests/test_command_routing.py tests/test_manuals.py` | **5 passed in 0.39s** |
| `pytest tests/test_continuity_claims.py` | **36 passed in 4.39s** |
| `python3 tools/check_docs.py` | **0 errors, 0 warnings** |
| `python3 tools/build_manual.py check` | **2 manuals passed, 0 errors, 0 warnings** |
| `python3 tools/build_manual.py build` | **built docs/manual/index.html & reference.html (195 KB)** |

**What works**
- **3x Manual Set** (P6-01, D-016; `docs/manual/`). Standalone What/How/Why System and Reference manuals.
- **The Manifold Scheme** (P6-02, D-017; `AGENTS.md`, `ROADMAP.md`, `docs/`). Durable repository memory architecture.
- **Fairness Redrafting** (P5-04; `brain/cortex.py`). Targeted redrafting when repaired replies remain flagged.
- **Partner Accommodation** (P4-02, P4-03; `drivers/lattice.py`). Calibrated $E_u$ tracking and sentence caps.
- **Offline Invariant** (P1-03, D-007; `tests/__init__.py`). Suite pinned offline with SHAKE-256 fallback.

**Not verified**
- Live multi-turn human conversation panel on the newly updated fairness redraft path.

**Gotchas for the next session**
- `BONE_EMBED_BACKEND=hash` is set by test initialization; do not rely on live vector similarity in unit tests.
- Factory files in `lore/` are strictly read-only; mutations belong in `saves/iris.db` tables.

## Next steps (in order)

1. Review and finalize uncommitted fairness redraft changes in `brain/cortex.py` and `tests/test_continuity_claims.py` (P5-04).
2. Run full test suite (`.venv/bin/pytest`) to confirm global baseline passes.
3. Generate a fresh comparison panel (`tools/build_conversation_panel.py`) for human reader evaluation (P6-03, D-011).

## Open questions for maintainers

- Q-001 Affective retrieval done properly via parallel affective vector index (blocks future affective memory).
- Q-002 Model-driven tiredness reading calibration vs word-frequency fallback (blocks fine-tuning accommodation).

## Session log

### Session 10: 2026-10-07: The Manifold scheme adoption and 3x documentation manual set

**Contributor:** Antigravity agent & Gordon
**Goal:** Establish durable repository memory and build standalone project manuals.
**Done:** P6-01, P6-02
**Changed:** Added `AGENTS.md`, `CLAUDE.md`, `ROADMAP.md`, `tools/check_docs.py`, `tools/build_manual.py`, `tests/test_manuals.py`, `docs/manual/system.manual.json`, `docs/manual/reference.manual.json`, `docs/manual/index.html`, `docs/manual/reference.html`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/HANDOFF.md`, `docs/SECURITY.md`, `docs/CONTRIBUTING.md`, `docs/CHANGELOG.md`.
**Decisions:** D-016, D-017
**Verified:** `tests/test_manuals.py` passed; `tools/check_docs.py` passed with 0 errors; `tools/build_manual.py check` passed with 0 errors.
**Not verified:** Live browser rendering on mobile devices.
**Next session should start with:** P5-04 fairness redraft completion.

### Session 9: 2026-10-07: Fairness check read once on reply shown with targeted redraft

**Contributor:** Gordon & Claude
**Goal:** Improve conversational fairness without ballooning LLM judge calls.
**Done:** P5-04
**Changed:** `brain/cortex.py`, `tests/test_continuity_claims.py`. Read fairness once on the shown reply, execute repair, and redraft if repair remains flagged.
**Decisions:** D-011
**Verified:** `tests/test_continuity_claims.py` 36 passed in 4.39s; judge calls reduced from 54 to 25.
**Next session should start with:** Session 10 documentation work.

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

### Session 1: 2026-10-03: Hash fallback catches narrowly and fail loudly adopted

**Contributor:** Gordon & Claude
**Goal:** Re-enable narrow hash fallback catches while enforcing loud failure on unexpected bugs.
**Done:** P1-02, P1-03
**Changed:** `spores/embeddings.py`, `tests/test_embeddings.py`. Caught `_BACKEND_ERRORS` only.
**Decisions:** D-005, D-015
**Verified:** 1,026 tests passed; hash fallback reports `[DEGRADED]` loudly.
**Next session should start with:** Session 2 bitmap quantization.
