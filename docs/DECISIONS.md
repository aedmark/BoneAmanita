# Decisions

Short, append-only record of choices that a future session might otherwise re-litigate. One entry per decision.
Newest at the bottom. To reverse a decision, add a new entry that supersedes it; the old one keeps its text and only
its status changes ("superseded by D-MMM").

Format:

```
## D-NNN Title  (YYYY-MM-DD, status: proposed | accepted | rejected | superseded by D-MMM)
**Context:** why this came up (the roadmap item, the bug, the measurement).
**Decision:** what we chose (numbered points if there are several).
**Alternatives:** what else was considered, and why not (one line each).
**Consequences:** what it costs or constrains; what was left out and why.
**Review trigger:** an event that should cause reconsideration. Optional.
```

---

## D-001 The model never performs a body; the person's state shapes the reply  (2026-09-17, status: accepted)
**Context:** Evaluation session C5 found that instructing language models that they were physically breathless, exhausted, or running out of oxygen resulted in theatrical roleplay ("my lungs burn") or abrupt emotional reversals rather than authentic conversational accommodation.
**Decision:** The model is strictly forbidden from performing a body or roleplaying physical fatigue. The human partner's state (tiredness, effort, disengagement, distress) shapes reply length, question allowance, and pacing. The engine's state (ATP, respiration, chemistry) sets what it can afford (token ceilings, retries, sampling bands).
**Alternatives:**
- Drop the engine's internal state entirely: rejected because co-regulation requires an anchored partner with its own limits, not pure mirroring.
- Allow mild bodily roleplay in creative modes: rejected because open-weight models quickly slip into melodramatic tropes.
**Consequences:** Prompts explicitly forbid body narration; `SomaticBudget` enforces word and sentence caps directly; `SelfClaimPrism` omits state-conditioned physical descriptions.

## D-002 Zero orchestration frameworks  (2026-09-15, status: accepted)
**Context:** Former Constitution Article 1. External frameworks were evaluated for control loop management and vector store indexing.
**Decision:** Strictly exclude general-purpose orchestration frameworks (LangChain, LlamaIndex, SemanticKernel) and vector database packages (Chroma, LanceDB). All networking uses standard library `urllib` or minimal `requests` calls; vector lookups use raw HTTP calls to Ollama with LRU caching.
**Alternatives:**
- Adopt LangChain for agent tooling: rejected because it takes ownership of the execution loop and obscures failure paths.
- Use Chroma or LanceDB for memory: rejected due to heavy binary dependencies and opaque persistence mechanisms.
**Consequences:** Requires hand-writing HTTP transport, retry logic, and SQLite schemas; ensures complete observability and tiny dependency footprint.

## D-003 Poetic variable names are load-bearing  (2026-09-15, status: accepted)
**Context:** Former Constitution Article 2. Code reviews suggested refactoring biological and metaphorical variable names to standard engineering terms.
**Decision:** Retain biological metaphors (`atp_pool`, `cortisol`, `narrative_drag`, `chi`, `godel_scars`) across the codebase.
**Alternatives:**
- Rename to `energy_level`, `stress_score`, `slow_factor`, `error_count`: rejected because the metaphorical names describe what the numbers are *for* within an embodied system, preventing developers from treating them as conventional request counters.
**Consequences:** Contributors must learn the domain metaphor before editing physics and metabolic equations.

## D-004 HTTP-first, package-optional embedder  (2026-09-15, status: accepted)
**Context:** Vector embeddings were initially considered using `sentence-transformers` and local PyTorch models.
**Decision:** The primary embedder connects via HTTP POST to an OpenAI-compatible `/v1/embeddings` endpoint (default Ollama `nomic-embed-text`). `sentence-transformers` is optional and not included in default requirements.
**Alternatives:**
- Mandate `sentence-transformers` in `requirements.txt`: rejected because pulling in PyTorch and transformer weights introduces a ~2GB dependency when the user already runs a local LLM server.
**Consequences:** Boot requires a reachable embedding server on `127.0.0.1:11434` or falls back to hash vectors.

## D-005 The hash fallback stays with SHAKE-256 self-reporting DEGRADED  (2026-09-18, status: accepted)
**Context:** When the embedding backend is unreachable at boot or fails mid-session, the engine needs an offline operating mode.
**Decision:** Retain the `hashlib.shake_256` 8-dimensional fallback vector generator. The engine announces `[DEGRADED]` at boot and in `/status` receipts rather than silently pretending associative recall is working.
**Alternatives:**
- Refuse to boot without a live embedding server: rejected because offline execution, testing, and grammatical classification remain fully functional without embeddings.
- Quietly degrade to hash vectors: rejected because hash coordinates return semantically meaningless memories that sound identical to real ones from the outside.
**Consequences:** Degraded operation is completely visible to users and diagnostic commands.

## D-006 Environment variables outrank BoneConfig.EMBEDDINGS  (2026-09-18, status: accepted)
**Context:** `BoneConfig.EMBEDDINGS` shipped populated with default values, which caused `BONE_EMBED_URL` environment overrides to be silently ignored.
**Decision:** Enforce a strict configuration precedence: environment variables (`BONE_EMBED_*`) outrank `config.json`, which outranks `BoneConfig`, which outranks module defaults.
**Alternatives:**
- Keep `BoneConfig` as the primary source: rejected because CI and containerized deployments require environment variable overrides.
**Consequences:** Verified by explicit regression tests in `tests/test_embeddings.py`.

## D-007 Test suite is strictly pinned offline  (2026-09-18, status: accepted)
**Context:** Tests that touched vector retrieval previously hung or failed if the local Ollama server was stopped or slow.
**Decision:** `tests/__init__.py` unconditionally sets `BONE_EMBED_BACKEND=hash` before any test module is imported. A full suite run must never depend on external network or server availability.
**Alternatives:**
- Mock HTTP responses globally with `responses` or `vcrpy`: rejected because setting hash mode is zero-dependency and deterministic.
**Consequences:** Live-server integration tests are explicitly guarded behind `BONE_EMBED_LIVE_TEST=1`.

## D-008 Style rules cut, they don't kill  (2026-09-23, status: accepted)
**Context:** The Gatekeeper previously discarded model replies on any cliché match, substituting a canned pause message.
**Decision:** On the final allowed redraft, soft style crimes trigger sentence salvage (`TheGatekeeper.salvage`) rather than killing the reply. Offending sentences are excised while valid surrounding prose is preserved. Only hard scaffold leaks fall through to canned pauses.
**Alternatives:**
- Zero-tolerance replacement with pauses: rejected because canned pause lines broke conversational immersion for minor stylistic blemishes.
- Loosen style rules: rejected because unconstrained model output quickly reverts to corporate RLHF filler.
**Consequences:** Preserves reply substance while cleanly cutting corporate phrasing.

## D-009 Token cap is the hardware ceiling, narrowed only by state  (2026-09-23, status: accepted)
**Context:** A hardcoded token limit of 450 tokens was originally enforced on every turn regardless of context.
**Decision:** `MAX_TOKENS` acts as the absolute hardware ceiling. Length is managed by `SomaticBudget` sentence targets; the token budget is narrowed only when partner or engine state calls for brevity (e.g. partner flagging).
**Alternatives:**
- Fixed token cap across all turns: rejected because lengthy coding replies in TECHNICAL mode were unnecessarily truncated.
**Consequences:** Calm, engaged turns can use full context space while tired turns remain short.

## D-010 Creative Determinant narrows somatic temperature band, never replaces it  (2026-09-23, status: accepted)
**Context:** An earlier design replaced the sampling temperature band with the Creative Determinant's proposed value, causing the engine to sample at temperature 0 for five straight days.
**Decision:** The Creative Determinant bitmap similarity score narrows the upper bound of the somatic temperature band for diffuse turns, but never replaces the band entirely and never drops below `DIFFUSE_SHARE`.
**Alternatives:**
- Fixed temperature across all states: rejected because state-dependent temperature modulation is a core thesis of somatic physics.
**Consequences:** Prevents deterministic lockup while still reflecting bitmap convergence.

## D-011 Verdicts come from human readers, not AI judges  (2026-09-23, status: accepted)
**Context:** Extensive evaluation across nine judge models, three rubrics, and pairwise controls showed that LLM judges rewarded verbose, sycophantic, bulleted assistant prose and failed responsive controls.
**Decision:** Evaluative verdicts come from human readers via randomized, double-blind comparison panels (`tools/build_blind_panel.py`). Automated LLM judge scripts remain in `tools/` for gross sanity checking but do not produce official verdicts.
**Alternatives:**
- Tune judge prompts with few-shot examples: rejected because model judges still exhibited fundamental sycophancy bias.
**Consequences:** Requires manual human reading panels for official benchmark runs.

## D-012 Agents commit only once Gordon explicitly approves; changelog commit format  (2026-09-18, status: accepted)
**Context:** Autonomous agent commits created noisy git history and lacked context when reviewing regressions.
**Decision:** Agents draft commits whenever asked, but never commit on their own initiative without explicit maintainer approval. Commit messages must read as detailed changelog entries explaining what changed, in which files, and why.
**Alternatives:**
- Blanket commit permission for green test runs: rejected because subtle stylistic or architectural regressions are not caught by unit tests alone.
**Consequences:** Slower commit cadence with a pristine, informative git log.

## D-013 Embedding calls are not metered into ATP  (2026-10-03, status: accepted)
**Context:** Whether `SemanticEmbedder` calls for novel word resolution and memory retrieval should impose an ATP thermodynamic drain.
**Decision:** Embedding lookups remain unmetered in ATP. Generation token burn and cognitive stumbles bear metabolic costs; vector lookups do not.
**Alternatives:**
- Charge 0.05 ATP per vector lookup: rejected because associative recall is a sensory/indexing process, not a metabolic cognitive action, and charging for it caused premature death during vocabulary-dense turns.
**Consequences:** Keeps vocabulary learning and associative memory search thermodynamically free.

## D-014 Live conversation dialogue carries across modes  (2026-10-04, status: accepted)
**Context:** When switching between modes (`/mode ADVENTURE` to `/mode CONVERSATION`), should the dialogue history be cleared or retained?
**Decision:** The live dialogue buffer carries over across mode switches, secrets included. Zones scope what is recalled from long-term memory, not what was spoken in the current live session.
**Alternatives:**
- Flush dialogue on every mode change: rejected because partners expect continuity when shifting conversational posture.
**Consequences:** Door passwords shared in ADVENTURE can be referenced in CONVERSATION mode.

## D-015 Fail loudly: remove swallowing exception handlers and report receipts  (2026-09-30, status: accepted)
**Context:** Twelve subsystems were discovered quietly returning defaults or doing nothing because broad `except Exception: pass` blocks masked runtime crashes.
**Decision:** Removed 92 swallowing exception handlers across engine and phases. Phase exceptions route to `PhaseExecutor.handle_phase_crash`, logging tracebacks and marking components offline. Subsystems file work receipts into `ReceiptLedger`.
**Alternatives:**
- Defensive try-catch blocks everywhere: rejected because prose output looks identical whether internal code ran or silently crashed.
**Consequences:** Subsystem defects cause visible test failures and receipts declare `DEGRADED` status.

## D-016 3x Documentation Scheme adopted for standalone system and reference manuals  (2026-10-07, status: accepted)
**Context:** BoneAmanita's complex somatic architecture, CLI commands, and design rationale required accessible, standalone documentation for human operators and AI agents without server dependencies.
**Decision:** Adopted the 3x documentation scheme template from `3x-documentation-scheme/` to build a two-volume manual set in `docs/manual/`: `system.manual.json` (System Manual) and `reference.manual.json` (Reference Manual), compiled to standalone HTML via `tools/build_manual.py`.
**Alternatives:**
- Hand-authored static HTML: rejected because hand-authored HTML quickly drifts from code and cannot be schema-validated.
- Markdown files only: rejected because the 3x scheme's structured What/How/Why content contract provides searchable progressive disclosure.
**Consequences:** Two verified, standalone HTML manuals (`docs/manual/index.html` and `docs/manual/reference.html`) built with zero runtime dependencies.

## D-017 The Manifold documentation scheme adopted as canonical repository memory  (2026-10-07, status: accepted)
**Context:** Project memory was concentrated in a massive, sprawling handoff document (`SESSION_HANDOFF.md`, 5,000+ lines), blending standing architecture rules, permanent decisions, test recipes, and daily session logs.
**Decision:** Adopted `the-manifold` documentation architecture scheme. Extracted standing rules into `AGENTS.md`, decisions into `docs/DECISIONS.md`, architecture into `docs/ARCHITECTURE.md`, testing into `docs/TESTING.md`, security into `docs/SECURITY.md`, and bounded current state into `docs/HANDOFF.md`. Validated continuously via `tools/check_docs.py`.
**Alternatives:**
- Keep single monolithic `SESSION_HANDOFF.md`: rejected because it exceeded useful working context limits and mixed durable decisions with transient session notes.
**Consequences:** Strict boundaries between current state, durable decisions, planned work, and historical logs.

## D-018 One live roadmap: the September 2026 roadmap is archived  (2026-10-08, status: accepted)
**Context:** Two files were called `ROADMAP.md`: the root one (phases with permanent `P<phase>-<nn>` IDs, adopted with D-017) and `docs/ROADMAP.md`, the 1,452-line September roadmap of tracks A to E with dated measurements. `README.md` and the manual described the root name but meant the old file.
**Decision:** `docs/ROADMAP.md` moved to `docs/archive/ROADMAP_2026_09.md` (history, kept for the measurements; code comments such as "ROADMAP D2b" mean it). The root `ROADMAP.md` is the only live plan; `tools/check_docs.py` looks for it in the root only.
**Alternatives:**
- Keep both and say `docs/ROADMAP.md` where the old one is meant: rejected because two files with one name invite the same mix-up.
**Consequences:** One place for planned work; the old tracks stay readable but are labelled historical.

## D-019 The fairness judge's ending read no longer triggers an edit  (2026-10-08, status: accepted)
**Context:** On 116 replies Gordon labelled, the ending read (`RULE`) flagged 15 (gemma4:12b) and 21 (gemma4:e4b) of 81 fair replies, 10 and 15 of the 24 fair replies to "is there a point where you stop trying to fix a friendship and just let it end?". Four wordings (`scratch/probes/rule_only.py`) did not separate them from the unfair ones. A message that asks whether to end it is handed back by `_asks_about_ending` regardless of the judge (Gordon).
**Decision:** A flag from the ending read alone files a `cortex.fairness` `NOT_ACTED` receipt and the reply is shown as written; beside an excuse or mind-reading flag it is ignored when repairing and when reading an edit, a redraft or a voiced redraft (`_flags_to_act_on`). The excuse and mind-reading reads still repair, redraft and voice.
**Alternatives:**
- Keep acting on it: rejected, it rewrote 22 (12b) and 32 (e4b) of 81 fair replies in all reads, 14 and 16 of them on the ending read alone.
- Tune `RULE` further: rejected, four variants (R1 to R3 and the current) did not separate fair from unfair; Gordon's own labels ("close to a c, but it doesn't actually decide anything") read like the unfair ones.
**Consequences:** Across the 116 labels, replies acted on: unfair 22 to 17 of 35 and fair 22 to 8 of 81 on 12b (precision 0.50 to 0.68, recall 0.63 to 0.49); e4b unfair 24 to 17, fair 32 to 16 (0.43 to 0.52, 0.69 to 0.49). The unfair replies given up are mostly replies to the ending question itself (#10, 18, 38, 47, 100 are c), which the ask path covers live. Revisit with a second human-labelled set of ending replies.

## D-020 Q-001 queued as P7-01; Q-002 closed, the tiredness heuristic stays  (2026-10-08, status: accepted)
**Context:** Two open questions: Q-001, affective retrieval through a parallel affective vector index; Q-002, whether the model should read the partner's tiredness instead of the word-frequency fallback, calibrated on mistral-nemo and gemma4:12b.
**Decision:** Q-001 becomes roadmap item P7-01, queued for immediate work. Q-002 is closed without calibration: the heuristic works (P4-02: flagging conversations detected at 80%, up from 14%), and calibrating a model reading needs the same kind of labelling and automated judging that produced noise and no signal for the fairness judge (D-011, `docs/TESTING.md`). Gordon's call.
**Alternatives:**
- Calibrate a model-driven tiredness reading: rejected, it would be judged by the same unreliable measures.
**Consequences:** The heuristic in `drivers/lattice.py` stays as it is. Affective memory is the next build, with `ordvec` and Project Navi's code to be read for anything reusable first.

## Open questions

None open. Answered 2026-10-08, kept so that references resolve:

- **Q-001** Affective retrieval done properly via parallel affective vector index. (asked 2026-09-27, by Claude; answered: queued as P7-01, D-020)
- **Q-002** Model-driven tiredness reading calibration vs word-frequency fallback. (asked 2026-10-04, by Gordon; answered: closed, the heuristic stays, D-020)
