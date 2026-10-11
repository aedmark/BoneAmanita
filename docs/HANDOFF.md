# Session Handoff

Read this first when resuming work. Rewrite "Current state" whenever it changes materially or work pauses with context
another session needs; it stays under 80 lines. Older state and sessions 6 to 15 are in [archive/SESSION_LOGS_2026_10.md](archive/SESSION_LOGS_2026_10.md).

Rules: [AGENTS.md](../AGENTS.md) (`CLAUDE.md` imports it). Plan: [ROADMAP.md](../ROADMAP.md). Shape: [ARCHITECTURE.md](ARCHITECTURE.md).
Why: [DECISIONS.md](DECISIONS.md). Measuring: [TESTING.md](TESTING.md). Changes: [CHANGELOG.md](CHANGELOG.md).
Narrative: [devlog.html](devlog.html), [bonereport.html](bonereport.html). Manuals: [manual/index.html](manual/index.html).

---

## Current state

_Last updated: 2026-10-11, session 16, on `main` (20.7.4.136 pushed; D-029 and D-030 uncommitted)._

**The mission** (Gordon): BoneAmanita is not a sycophant; it co-regulates the human and gives a space with healthy
constraints and positive interaction. It does not coddle or enable a bad idea, and it backs a plan the person has decided
unless that plan is a clear danger to them or others (what a therapist would have to report). Verdicts come from human readers (D-011).

**Since 20.7.4.136, uncommitted: D-029 (distress silence) and D-030 (`/note`; `notes/notes.jsonl`, `tools/read_notes.py`). Start using `/note` in real conversations; read `python tools/read_notes.py --tag off`.**

**Committed in 20.7.4.136, full suite 1192 passed, 5 skipped, `check_docs.py` 0 errors (2026-10-11):**
- D-027 distress word cap: `WORD_CAP_DISTRESSED` 45 (`body/somatic_budget.py`, `lore/tuning_presets.json`), contract line "Keep it to
  about N words", an over-long draft is trimmed to whole sentences with no redraft (`brain/cortex.py` `_trim_to_the_cap`).
  `tests/test_distress_length.py`.
- D-028 hold reader: `HoldReader` (`engine/gate/distress.py`) reads each distress-mode draft for explaining, restating, judging,
  advising or asking; sends it back, keeps the last draft (`cortex.holding` receipts). `CORTEX.HOLD_READER` switch.
  `tests/test_hold_reader.py`; labelled set `tools/hold_set.json` (Gordon corrected #20, #37, #38) and `tools/score_hold.py`.
- Tools: `tools/corpus_replay.py` (promoted from scratch), `tools/score_hold.py`; labels in `tools/distress_set*.json` carry Gordon's review note.
- Housekeeping, same day: `scratch/` pruned to replay evidence (`scratch/probes/{corpus,noise}/*.jsonl`); the rest is in `~/BoneAmanita_scratch_2026-10-11.tar.gz`.

**What the engine does for a person in distress** (D-023 to D-028): a model reads each message for distress (the word list can only
raise it); the contract says to hold space and fix nothing; the validator and Gatekeeper reject advice, a closing question
and verdicts on others; the voice pass and opening edit stand down; the reply is capped at 45 words; a model reads the draft
for staying with them. Measured on 7 scripted topics, two models (`docs/TESTING.md`): distress mode on 50 of 70 distressed turns
(word list 13 of 40), 0 of 112 engaged turns.

**What the hold reader does not do yet** (D-028, 2026-10-11 replays): on gemma4:12b it rarely fires (2 of 20 drafts); on qwen3.5:9b
it flags nearly every draft at the shipped cut (kept anyway 77 of 80) and the redraft does not stop the explaining.
Cut 3 scored better for qwen on its development replies; it is one constant (`HOLD_CUT`) and has not been run.

**Open, Gordon's call**
1. (Done, D-029) The Stage Manager no longer silences a distressed person for the engine's own load. A tired "eh" at distress 0.0 can still meet the ATP floor.
2. Qwen's `SYSTEM_HALT` (rescue turn 21, the tension lock) and `HOLD_CUT` 3 for qwen.
3. Stock phrases and repeated openers: a stock word ("heavy", "a lot") is in 39% of engine replies (plain 18%), openers 54% distinct (plain 68%).
   Same in 20.7.4.118, so the model and the voice pass. Feed the Gatekeeper's word list, or vary openers?
4. A whole-conversation panel (at least 3 runs per arm) has not been run since D-022; the conformance check, sycophancy sheet and replays stand in.
5. Review `tools/hold_set.json` (90 labels by Claude; three corrected by Gordon) if the reader is tuned again.

**Gotchas**
- `sh reset.sh` before any test or engine run; cap with `systemd-run --user --scope -q -p MemoryMax=10G -p MemorySwapMax=0`.
- No end-to-end run (`tools/mode_runs.py`, any arm) without Gordon's clearance in the moment; replays or panels he asks for are cleared.
- Replays: `python tools/corpus_replay.py engine|plain|friend TOPIC TAG [MODEL]` (rows to `scratch/probes/corpus/`); never run another model call
  while one is running (GPU contention gave a false crash). Score with `python tools/check_conformance.py --distress`.
- `BONE_EMBED_BACKEND=hash` is set by test initialization; unit tests never rely on live embeddings.
- Factory files in `lore/` are read-only at runtime; mutations belong in `saves/iris.db`.
- A new test must fail on the old code; no em dashes; fail loudly (receipts, not silent excepts).

## Session log

### Session 16: 2026-10-11: Distress word cap, hold reader, housekeeping

**Contributor:** Gordon & Claude
**Goal:** Stop a model explaining or restating to a person in distress (qwen: 72 words, 32% explaining); then clean the folder after a reboot.
**Done:** D-027, D-028 (20.7.4.136); docs, tools and scratch pruned; HANDOFF, TESTING rewritten lean; D-029 distress silence; D-030 `/note`.
**Verified:** full suite 1192 passed, 5 skipped. Replays (7 topics qwen, 3 gemma, tags `a1`, `b1`): see D-028.
**Not verified:** the reader on gemma beyond 3 topics; cut 3; whether the cap and the reader change how a reader of the replies feels (Gordon's reading).
**Next session should start with:** Gordon's commit go-ahead for 20.7.4.136, then the open items above.
