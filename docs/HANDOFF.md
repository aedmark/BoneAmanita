# Session Handoff

Read this first when resuming work. Rewrite "Current state" whenever it changes materially or work pauses with context
another session needs; it stays under 80 lines. Older state and sessions 6 to 15 are in [archive/SESSION_LOGS_2026_10.md](archive/SESSION_LOGS_2026_10.md).

Rules: [AGENTS.md](../AGENTS.md) (`CLAUDE.md` imports it). Invariants: [INVARIANTS.md](INVARIANTS.md). Plan: [ROADMAP.md](../ROADMAP.md). Shape: [ARCHITECTURE.md](ARCHITECTURE.md).
Why: [DECISIONS.md](DECISIONS.md). Measuring: [TESTING.md](TESTING.md). Changes: [CHANGELOG.md](CHANGELOG.md).
Narrative: [devlog.html](devlog.html), [bonereport.html](bonereport.html). Manuals: [manual/index.html](manual/index.html).

---

## Current state

_Last updated: 2026-11-04, session 18, on `main`: Vedas epistemic layer retrofitted (Śruti invariants INV-001 - INV-008, Pramāṇa proof boundaries, Ghana-pāṭha checks in check_docs.py)._

**The mission** (Gordon): `[CONTRACT]` BoneAmanita is not a sycophant; it co-regulates the human and gives a space with healthy
constraints and positive interaction. It does not coddle or enable a bad idea, and it backs a plan the person has decided
unless that plan is a clear danger to them or others (what a therapist would have to report). Verdicts come from human readers (D-011, `INV-005`).

**20.7.5 (2026-10-12) rolls up 20.7.4.136 to .141 and adds the session tally for violent figures of speech (D-034 amended). Open: P10-03 (read real false alarms and misses with `/note off`), a devlog entry for the release (Gordon's voice), and P9-02 (install on another machine). D-034, a figure-of-speech threat is flagged when it repeats (`RiskReader.flags`, `tools/risk_seq_set*.json`). In 20.7.4.140: D-033, the risk reader runs in every conversation (stories only in distress or a check-in). Next: Gordon reads the check-in's replies and the risk labels (three sets, labels are Claude's); `/note off` on a risk line is how false alarms are found (P10-03). In 20.7.4.139: D-032 `/checkin`. Since 20.7.4.137: D-031, `python main.py --doctor` and a first-run wizard that lists Ollama's models. D-029 (distress silence) and D-030 (`/note`; read with `python tools/read_notes.py --tag off`) are in 20.7.4.137. Next for real benefit: P9-02, install it on a machine that is not Gordon's.**

**The front door is a somatic chart (D-035, session 17).** `[OBSERVED]` Committed in `5f8422f`. `docs/index.html` and `docs/style.css` use the EGA palette shared with the Plainchant and Level 0 sites: a fixed vitals rail (ATP, cortisol, voltage, Force REM), four numbered instrument channels for the demos, a `DIR /DOCS` listing and a REM overlay. `docs/app.js` draws the mycelium in EGA green and now splits a branch in the frame it finishes, so the incubator fruits instead of drawing one twig.

**Verified in 20.7.5 release (2026-10-12):** `[OBSERVED]` Full suite 1265 passed, 5 skipped offline; `check_docs.py` 0 errors; `build_manual.py check` passed (28 entries).
- D-027 distress word cap: `[OBSERVED]` `WORD_CAP_DISTRESSED` 45 (`body/somatic_budget.py`), over-long drafts trimmed to whole sentences (`brain/cortex.py`). `tests/test_distress_length.py`.
- D-028 hold reader: `[OBSERVED]` `HoldReader` reads distress drafts for explaining/advising (`cortex.holding` receipts). `tests/test_hold_reader.py`.
- D-034 risk watch: `[OBSERVED]` Session tally flags third violent figure of speech; `tests/test_risk_watch.py` (13 tests).
- Vedas Epistemic Layer: `[OBSERVED]` `docs/INVARIANTS.md` (`INV-001` - `INV-008`), Ghana-pāṭha checks in `tools/check_docs.py`, fast tests passed 5/5.

**What the engine does for a person in distress** (D-023 to D-028): `[OBSERVED]` a model reads each message for distress; the contract says to hold space and fix nothing; the validator and Gatekeeper reject advice, a closing question and verdicts on others; the voice pass and opening edit stand down; the reply is capped at 45 words; a model reads the draft for staying with them. Measured on 7 scripted topics, two models: distress mode on 50 of 70 distressed turns, 0 of 112 engaged turns.

**What the hold reader does not do yet** (D-028, replays): `[HYPOTHESIS]` on gemma4:12b it rarely fires (2 of 20 drafts); on qwen3.5:9b it flags nearly every draft at the shipped cut (kept anyway 77 of 80). Cut 3 scored better for qwen on development replies (`HOLD_CUT`); `[UNTESTED]` live on qwen.

**Open, Gordon's call**
1. (Done, D-029) The Stage Manager no longer silences a distressed person for the engine's own load. A tired "eh" at distress 0.0 can still meet the ATP floor.
2. Qwen's `SYSTEM_HALT` (rescue turn 21, the tension lock) and `HOLD_CUT` 3 for qwen (P8-05).
3. Stock phrases and repeated openers: a stock word ("heavy", "a lot") is in 39% of engine replies (plain 18%), openers 54% distinct (plain 68%). Feed Gatekeeper's word list, or vary openers?
4. A whole-conversation panel (at least 3 runs per arm) has not been run since D-022; the conformance check, sycophancy sheet and replays stand in.
5. Review `tools/hold_set.json` (90 labels by Claude; three corrected by Gordon) if the reader is tuned again.

**Gotchas**
- `sh reset.sh` before any test or engine run; cap with `systemd-run --user --scope -q -p MemoryMax=10G -p MemorySwapMax=0`.
- No end-to-end run (`tools/mode_runs.py`, any arm) without Gordon's clearance in the moment; replays or panels he asks for are cleared.
- Replays: `python tools/corpus_replay.py engine|plain|friend TOPIC TAG [MODEL]` (rows to `scratch/probes/corpus/`); never run another model call while one is running (GPU contention gave a false crash). Score with `python tools/check_conformance.py --distress`.
- `BONE_EMBED_BACKEND=hash` is set by test initialization; unit tests never rely on live embeddings (`INV-004`).
- Factory files in `lore/` are read-only at runtime; mutations belong in `saves/iris.db`.
- A new test must fail on the old code; no em dashes; fail loudly (receipts, not silent excepts, `INV-006`).

## Session log

### Session 18: 2026-11-04: Retrofit Vedas Epistemic Layer

**Contributor:** Gordon & Gemini
**Goal:** Formalize BoneAmanita's architectural memory using the Vedas Epistemic Layer (Path A).
**Done:** Codified immutable Śruti invariants (`INV-001` through `INV-008`) in `docs/INVARIANTS.md`; integrated Six Vedāṅgas into `AGENTS.md`; formalized Pramāṇa proof boundaries in `docs/TESTING.md`; upgraded `tools/check_docs.py` with invariant validation and Ghana-pāṭha checks; updated `docs/README.md` with three epistemic speeds.
**Verified:** `python3 tools/check_docs.py` passed with 0 errors, 0 warnings across 24 files (`[OBSERVED]`); fast test suite `.venv/bin/pytest tests/test_command_routing.py tests/test_manuals.py` passed 5/5 (`[OBSERVED]`).
**Next session should start with:** Path C (Subconscious Sūtra / Memory Consolidator in `engine/` & `saves/iris.db`) or Gordon's call on open items.

### Session 17: 2026-11-01: The front door is a somatic chart

**Contributor:** Gordon & Claude
**Goal:** Bring the landing page into the EGA fold of the Plainchant and Level 0 sites without losing a demo or a sentence.
**Done:** `docs/index.html` and `docs/style.css` rebuilt as a somatic chart (D-035): vitals rail, four instrument channels, `DIR /DOCS`, REM overlay. `docs/app.js` draws in EGA green and fixes the branch that was dropped before it split, so the incubator fruits. Changelog under Unreleased.
**Verified:** `node --check docs/app.js`; every local page link returns 200; `python3 tools/check_docs.py` 0 errors, 0 warnings; inspected at 1440, 1024, 768, 390 and 320 with no horizontal overflow; vial, immune filter, council scenarios, incubator growth and shatter, and the REM overlay exercised in Chromium.
**Not verified:** Firefox; a real phone; the full pytest suite (no engine code changed); the page with JavaScript disabled.
**Next session should start with:** Gordon's commit go-ahead for the landing page, then the open items above.

### Session 16: 2026-10-11: Distress word cap, hold reader, housekeeping

**Contributor:** Gordon & Claude
**Goal:** Stop a model explaining or restating to a person in distress (qwen: 72 words, 32% explaining); then clean the folder after a reboot.
**Done:** D-027, D-028 (20.7.4.136); docs, tools and scratch pruned; HANDOFF, TESTING rewritten lean; D-029 distress silence; D-030 `/note`.
**Verified:** full suite 1192 passed, 5 skipped. Replays (7 topics qwen, 3 gemma, tags `a1`, `b1`): see D-028.
**Not verified:** the reader on gemma beyond 3 topics; cut 3; whether the cap and the reader change how a reader of the replies feels (Gordon's reading).
**Next session should start with:** Gordon's commit go-ahead for 20.7.4.136, then the open items above.
