# Changelog

User-visible changes, newest first, in plain words. Developer and session notes live in `docs/HANDOFF.md`.

## Unreleased

### Added
- **3x Documentation Scheme Manual Set:** Two standalone, searchable HTML manuals in `docs/manual/` (`index.html` System Manual, `reference.html` Reference Manual) providing What/How/Why coverage of architecture, somatic physics, commands, modes, and receipts with zero runtime dependencies (D-016).
- **The Manifold Documentation Scheme:** Canonical repository memory architecture adopting `AGENTS.md`, `CLAUDE.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/HANDOFF.md`, `docs/SECURITY.md`, `docs/CONTRIBUTING.md`, `docs/CHANGELOG.md`, and automated validation via `tools/check_docs.py` (D-017).
- **Manual Build Tool:** Added `tools/build_manual.py` for validating and building the 3x manual set with a single command.

### Changed
- **Fairness Redrafting:** When a repaired draft remains flagged by the fairness critic, the cortex now requests a single targeted redraft identifying the sided language before falling back to the least-flagged candidate (P5-04).
- **Documentation Map:** Integrated links to the standalone manual set directly into the Bio-Terminal hero section (`docs/index.html`) and `README.md`.

### Fixed
- **Archive Link Consistency:** Fixed relative links in `docs/archive/ROADMAP_HISTORY_2026_09.md` pointing to parent handoff documentation.

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
