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
- [-] P6-03 Human blind panel calibration against automated LLM judge failures (D-011). Dropped 2026-10-08: automated judging is a wash; verdicts are replays read against their noise floor plus Gordon's reading (`docs/TESTING.md`). The AI-judge tool was removed 2026-10-11.

## Phase 7: Affective Memory

Goal: Recall memories by how a moment felt, not by text similarity alone.

- [-] P7-01 Affective retrieval: an affective state vector stored beside each semantic embedding, queried by emotional resonance (Q-001, D-020). Dropped 2026-10-08 before any code: no available vector tracks mood (D-021).

## Phase 8: Holding Space

Goal: A person in measured distress is held, not fixed, coddled or argued with (Gordon, 2026-10-08).

- [x] P8-01 A model reads each message for distress; the word list can only raise it (`engine/gate/distress.py`; D-023).
- [x] P8-02 The contract says to hold space and fix nothing; the validator and Gatekeeper reject advice, a closing question and verdicts on others; the voice and opening edits stand down (D-024, D-025, D-026).
- [x] P8-03 A distress word cap (45), trimmed not redrafted (D-027), and a model reading of the draft for staying with them (D-028).
- [x] P8-04 A person in distress is never answered with the Stage Manager's silence for the engine's own load (D-029).
- [ ] P8-05 The hold reader on qwen3.5:9b flags nearly every draft at the shipped cut; try `HOLD_CUT` 3 (D-028).
- [x] P8-06 `/note`: the person's own verdict on the last exchange, saved to `notes/notes.jsonl` (D-030).

## Phase 10: The Check-in

Goal: A short, bounded conversation that holds space, keeps nothing unless asked, and ends (Gordon, 2026-10-11).

- [x] P10-01 `/checkin [turns]`: 12 turns at most, hold-space contract throughout, a closing that lands without a hook, a fixed risk line, `/checkin keep` (D-032).
- [ ] P10-02 Read the risk line's misses (conditional threats, passive thoughts of not being around) with Gordon; decide whether the risk reading belongs outside a check-in.

## Phase 9: Anyone Can Run It

Goal: A person who is not the maintainer gets from clone to a first reply without guessing.

- [x] P9-01 `python main.py --doctor` and a first-run wizard that lists the models Ollama has (D-031).
- [ ] P9-02 A first install on a machine that is not Gordon's, with what went wrong written down.
