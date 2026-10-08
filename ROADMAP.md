# Roadmap

Item IDs are permanent: `P<phase>-<nn>`. Never renumber; append new items at the end of their phase.
`[ ]` open · `[~]` in progress · `[x]` done · `[-]` dropped.

Historical track details and completed items from earlier sessions are preserved in
[docs/archive/ROADMAP_HISTORY_2026_09.md](docs/archive/ROADMAP_HISTORY_2026_09.md) and
[docs/archive/ROADMAP_2026_09.md](docs/archive/ROADMAP_2026_09.md)

## Phase 1: Observability and Fail-Loudly Architecture

Goal: Eliminate silent failures, report subsystem receipts, and guarantee test offline invariants.

- [x] P1-01 Subsystem receipt roll call and `/diag` command telemetry to expose silent components (D-015).
- [x] P1-02 Removal of broad exception-swallowing handlers (`except Exception: pass`) across engine and phases (2026-09-30).
- [x] P1-03 Offline test suite pinning via SHAKE-256 hash embeddings in `tests/__init__.py` (D-007).
- [x] P1-04 Phase crash isolation in `PhaseExecutor.handle_phase_crash` with component offline tracking.

## Phase 2: Creative Determinant and Bitmap Governance

Goal: Replace heuristic sampling guesses with quantized sign bitmap similarity.

- [x] P2-01 4-bit `RankQuant` sign bitmap quantization using Project Navi's `ordvec` (D-010).
- [x] P2-02 Corpus distance measurement and sampling temperature clamping to the somatic budget band.
- [x] P2-03 Fallback from sparse memory corpuses (<3 memories) to somatic PID regulation.

## Phase 3: Biological Harness and Halcyon Persistence

Goal: Consolidate storage into a single transactional SQLite database and protect secrets.

- [x] P3-01 Migration of fragmented quicksaves, overlays, and learned words into `saves/iris.db` (2026-09-27).
- [x] P3-02 Automated credential withholding replacing API keys and private tokens with `[withheld: ...]`.
- [x] P3-03 Formalizing unmetered `SemanticEmbedder` calls in the ATP metabolic ledger (D-013).
- [x] P3-04 Preserving live dialogue history and secrets across experience mode switches (D-014).

## Phase 4: Somatic Contract and Partner Accommodation

Goal: Enforce anti-performance rules, model partner fatigue, and calibrate metabolic burn.

- [x] P4-01 Anti-performance contract prohibiting model bodily roleplay and physical breathlessness (D-001).
- [x] P4-02 Partner exhaustion ($E_u$) and fatigue cue tracking in `SharedLatticeDriver` (2026-10-03).
- [x] P4-03 `SomaticBudget` generation caps (3 sentences, 60 words, no closing questions) for flagging partners.
- [x] P4-04 Calibrating ATP burn rates, clearing permanent retry discounts, and setting 0.020 ATP/token in TECHNICAL (2026-10-03).

## Phase 5: Voice Protection and Fairness Safeguards

Goal: Protect conversational authenticity against RLHF sycophancy, clichés, and one-sided bias.

- [x] P5-01 Gatekeeper sentence salvage on soft style crimes, eliminating false pause lines (D-008).
- [x] P5-02 Prismatic Self-Claims defining epistemic boundaries without state-conditioned physical roleplay.
- [x] P5-03 CREATIVE mode anti-menu rules enforcing continuous narrative prose over multi-choice menus.
- [x] P5-04 Fairness verification and redrafting when repairs remain flagged (`brain/cortex.py`; D-019).

## Phase 6: Documentation and Evaluation Manifold

Goal: Structure repository knowledge into standalone manuals and maintainer-agent protocols.

- [x] P6-01 Standalone What/How/Why Manual Set via the 3x Documentation Scheme in `docs/manual/` (D-016).
- [x] P6-02 Adoption of the Manifold documentation scheme (`AGENTS.md`, `ROADMAP.md`, `docs/`) (D-017).
- [ ] P6-03 Human blind panel calibration against automated LLM judge failures (D-011).
