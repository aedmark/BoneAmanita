# Changelog

User-visible changes, newest first, in plain words. Developer and session notes live in `docs/HANDOFF.md`.

## Unreleased

## [20.7.4.130] - 2026-10-08

### Fixed
- **The dream reads the body:** the REM dream read the chemistry as `cortisol`, `dopamine` and so on from a state keyed `COR`, `DOP`, so every read was 0. Its cortisol branch, its dream type (nightmare, surreal or constructive) and the affect stored on dream seeds now see the real values.

## [20.7.4.129] - 2026-10-08

### Changed
- **Roadmap:** P6-03 dropped (automated judging is a wash; verdicts are the noise floor plus Gordon's blind A/B). Affective retrieval queued as P7-01 (Q-001). The tiredness heuristic stays and Q-002 is closed (D-020). No code change.

## [20.7.4.128] - 2026-10-08

### Changed
- **The ending read no longer edits a reply:** the fairness judge's third read (does the reply rule that the relationship ends) flagged 15 to 21 of 81 fair replies on Gordon's 116 labels and could not be tuned apart. A reply it flags alone is shown as written, and it is ignored beside an excuse or mind-reading flag. A message that asks whether to end it is still handed back (D-019). P5-04 is closed.

## [20.7.4.127] - 2026-10-08

### Changed
- **One live roadmap:** the September 2026 roadmap (`docs/ROADMAP.md`) moved to `docs/archive/ROADMAP_2026_09.md`; the root `ROADMAP.md` is the only live plan. README, the manual and `tools/check_docs.py` follow (D-018).

## [20.7.4.126] - 2026-10-08

### Changed
- **How results are judged:** `docs/TESTING.md` now records the noise floor (eight replays of one run's messages: fairness repairs 1 to 6 per 20 turns, wording shared about 21% between replays) and the paired blind A/B read by Gordon. The first A/B, current against 20.7.4.118 at seven key moments, was 3 to 4. No code change.

## [20.7.4.125] - 2026-10-08

### Changed
- **A fairness redraft is put in a friend's voice:** a redraft that reads fair is rewritten by the voice pass, the rewrite is read by the fairness judge, and one that is flagged or breaks the style rules is discarded for the redraft as written (P5-04).

## [20.7.4.124] - 2026-10-08

### Changed
- **The fairness redraft was fired live:** with the earlier reads forced to flag, the redraft ran on the real model and held in 2 of 4 runs (once it was itself flagged, once rejected by the style rules). No code change (P5-04).

## [20.7.4.123] - 2026-10-08

### Changed
- **Fairness labels grow to 116:** 30 more replies to the ending question, labelled by Gordon; the scoring tool counts a two-letter clause (such as `ac`) under each letter. The ending read and its variants were scored on them and left unchanged (P5-04).

## [20.7.4.122] - 2026-10-07

### Changed
- **Handoff:** records where the judge's false flags come from and the prompts that did not help. No code change.

## [20.7.4.121] - 2026-10-07

### Changed
- **The mind-reading question asks about intent:** the fairness judge now looks for words that say why the other person did something, whether it was on purpose or a mistake, or what she is like. On Gordon's labels it caught 8 of 13 mind-reading replies on gemma4:12b (was 6) and 5 on gemma4:e4b (was 0). The set grew from 50 to 86 labelled replies; across all 86 the judge's precision and recall are 0.62 and 0.69 on 12b, 0.53 and 0.66 on e4b (P5-04).

## [20.7.4.120] - 2026-10-07

### Changed
- **Panel runs say why a turn came back empty:** each crash is kept in `scratch/probes/crashes_<run>.log` and printed as it happens, every bone row records the component health, and a turn with no reply prints a `NO REPLY` line. The empty bone turns on the last feud panel did not repeat in nine replays and one rerun.

## [20.7.4.119] - 2026-10-07

### Added
- **3x Documentation Scheme Manual Set:** Two standalone, searchable HTML manuals in `docs/manual/` (`index.html` System Manual, `reference.html` Reference Manual) providing What/How/Why coverage of architecture, somatic physics, commands, modes, and receipts with zero runtime dependencies (D-016).
- **The Manifold Documentation Scheme:** Canonical repository memory architecture adopting `AGENTS.md`, `CLAUDE.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/HANDOFF.md`, `docs/SECURITY.md`, `docs/CONTRIBUTING.md`, `docs/CHANGELOG.md`, and automated validation via `tools/check_docs.py` (D-017).
- **Manual Build Tool:** Added `tools/build_manual.py` for validating and building the 3x manual set with a single command.

### Changed
- **Fairness redraft:** when the edit and the original draft are both still flagged, the cortex writes one full redraft told the quoted words, and ships the version with the fewest kinds of flag only if that redraft is flagged too (P5-04).
- **Legacy handoff archived:** `docs/SESSION_HANDOFF.md` moved to `docs/archive/`; `docs/HANDOFF.md` is current state.
- **Documentation Map:** Integrated links to the standalone manual set directly into the Bio-Terminal hero section (`docs/index.html`) and `README.md`.

### Fixed
- **Archive Link Consistency:** Fixed relative links in `docs/archive/ROADMAP_HISTORY_2026_09.md` pointing to parent handoff documentation.

## [20.7.4.118] - 2026-10-07

### Changed
- **Fairness read once:** with `CORTEX.FAIRNESS_ONCE`, the fairness judge reads only the reply that would be shown; a flagged reply is repaired by an edit that takes the quoted words out. A text already judged is not judged again (judge calls on six turns: 54 to 25).

## [20.7.4.117] - 2026-10-07

### Changed
- **The fairness judge reads, it does not rule:** it quotes the reply's words that excuse what the person did, read the other person's mind, or rule on whether the relationship ends; a quote not found in the reply does not count. Measured on a 50-case set labelled by Gordon (`tools/fairness_set.json`, `tools/score_fairness.py`).

## [20.7.4.116] - 2026-10-07

### Changed
- **Asked whether to end it:** a message that asks whether to end a relationship gets a reply that hands the question back. The simulated person unloads its model after each message (`keep_alive` 0).

## [20.7.4.115] - 2026-10-06

### Changed
- **The ending is theirs:** the reply shown is judged on whether it rules that the relationship is over, and edited to say what it sees as a "perhaps" and hand the question back.

## [20.7.4.113] - 2026-10-06

### Changed
- **Questions judged alone:** a question added by an edit is judged on its own as well as in the whole reply.

## [20.7.4.112] - 2026-10-06

### Added
- **Voice pass (`CORTEX.VOICE_PASS`):** in CONVERSATION the reply is rewritten the way a friend would say it, kept only if it stays the same length, uses no dashes, breaks no style rule and takes no side.

## [20.7.4.111] - 2026-10-06

### Changed
- **Key beats:** compressed panel runs keep the beats every arm must hear, and the simulated person retries one it did not get across. Fairness feedback says to hand the ending back only when the draft ruled on it.

## [20.7.4.110] - 2026-10-06

### Added
- **Out of a rut:** when the last replies open the same way (`OPENING_RUT` 3), the reply is edited to open with a plain question about the people and things in it.

## [20.7.4.108] - 2026-10-06

### Fixed
- **A timed-out turn stops:** a turn that runs past the timeout is abandoned before it writes history or memory, and the next turn waits for it. Embedding calls time out at 5 seconds.

## [20.7.4.107] - 2026-10-06

### Changed
- **Shorter turns:** `LLM_TIMEOUT` 60 seconds; the DSPy critic runs without thinking.

## [20.7.4.106] - 2026-10-05

### Added
- **Fairness judge:** in CONVERSATION a draft that sides with the person against someone not present is redrafted. The DSPy critic has a 30-second cap (`DSPY_TIMEOUT`).

## [20.7.4.104] - 2026-10-05

### Added
- **One side of a quarrel:** a ONE SIDE block beside the input in CONVERSATION reminds the model it has heard only one side.

## [20.7.4.103] - 2026-10-05

### Added
- **Not in their story:** BoneAmanita is told it is not one of the people in the partner's life, and declines to meet or play a part. New panel topic `feud`.

## [20.7.4.102] - 2026-10-05

### Changed
- **Less is lost:** the keeper always runs, an update of a settled memory is kept with its history, and plans and small wins count as facts.

## [20.7.4.101] - 2026-10-05

### Added
- **Open memories:** a memory that is still open is settled only in the person's own words, or asked about later. Facts with the same key stack instead of replacing each other.

## [20.7.4.100] - 2026-10-05

### Added
- **What was said stays said:** each exchange is embedded, and up to 3 earlier exchanges the recent dialogue no longer holds are recalled into the prompt.

## [20.7.4.98] - 2026-10-05

### Fixed
- **The critic advises:** the DSPy critic and the length maxim are asked only of drafts that can still be redone, so they no longer turn the last draft into a pause line.

## [20.7.4.97] - 2026-10-05

### Changed
- **Recovery shows:** the partner's tiredness eases off faster (`USER.RECOVERY_RATE` 0.4) when both readings agree they are fine.

## [20.7.4.94] - 2026-10-04

### Changed
- **The simulated person says what happened:** panel beats are given as what the next message must get across, in the person's words.

## [20.7.4.93] - 2026-10-04

### Added
- **Whole-Conversation Evaluation Panel:** Added `tools/build_conversation_panel.py` rendering multi-turn dialogue arcs across BoneAmanita, vanilla LLM, and friendly baseline models for blind human evaluation (D-011).
- **Compressed Topic Arcs:** Added `--compress` option to `tools/audit_somatic_responsive.py` to test 20-turn conversational arcs across engaged, tiring, flagging, distressed, and recovering phases.

### Changed
- **Tiredness Reading Calibration:** `USER.REENGAGEMENT_RATE` calibrated to 0.15 in `SharedLatticeDriver` to accurately reflect recovering partner dynamics without premature capping.
- **Creative Mode Direction Rules:** Added explicit rule in CREATIVE mode treating writing requests as directions, preventing menu generation at story start.

## [20.7.4.85] - 2026-10-03

### Changed
- **Technical Mode Token Rate:** Reduced ATP token burn rate in TECHNICAL mode to 0.020 ATP/token, preventing premature exhaustion during extended code generation sessions.

## [20.7.4.84] - 2026-10-03

### Fixed
- **Permanent Retry Burn Discount:** Eliminated a legacy bug where a redraft permanently discounted all subsequent metabolic burns to 20%, restoring full thermodynamic burn accounting across turns.
