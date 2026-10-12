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

## D-021 P7-01 dropped: no available vector tracks mood; the dream's chemistry names fixed  (2026-10-08, status: accepted)
**Context:** P7-01 (D-020) would store an affect vector beside each memory and query it. Measured first (`scratch/probes/affect_trace.py`, a replay of the 20-message feud run `20261007-224404`): the engine's six numbers (voltage, resonance, DOP, COR, SER, OXY) do not separate the scripted phases. Cortisol stays 0.0 to 0.11 through the "distressed" turns, dopamine is flat (0.63 to 0.77), serotonin and oxytocin drift up with conversation length. Nearest other turn (neighbours within two turns excluded) shares the phase 0 of 20 times for the six numbers, 2 for the chemistry, 4 for the person model (E_u, P_u, distress), against 3 expected by chance. Separately, the stored vectors were mostly zeros: the dream code read `cortisol`, `dopamine`, `serotonin`, `oxytocin` from a state keyed `COR`, `DOP`, `SER`, `OXY`, so every chemistry read was 0 and the affect penalty in `spores/memory.py` `dredge_vibe_by_vector` never fired.
**Decision:** P7-01 is dropped, as the tiredness model and the judge calibration were (D-011, D-020): an index fed this signal would be noise. `DreamEngine.enter_rem_cycle` now maps the engine's short chemistry names to the long ones before any read. Gordon's calls.
**Alternatives:**
- Build the index on the person model (E_u, P_u, distress): rejected for now, it matched the phase 4 of 20 times (chance 3); revisit only with real multi-session data and a check offline first.
- Leave the key mismatch: rejected, it is a plain bug (the tests fed the long names, so they never saw it).
**Consequences:** The dream's cortisol branch, its dream type (nightmare above cortisol 0.6, surreal above dopamine 0.6, else constructive; it was always constructive) and the affect stored on dream seeds now see the body. In a conversation dopamine sits 0.63 to 0.77, so a REM cycle straight after one will mostly be surreal; at rest it is 0.5. `physics_state` is still not passed by the cycle, phase and biological callers, so voltage and resonance in a stored affect vector stay 0 there (only `/dream` passes it). Amended 2026-10-08: every caller now passes the flattened physics (`to_dict()`); the `/sleep` and `/dream` callers had passed `vars(packet)`, which holds only the nested domains, so they passed no voltage or resonance either.

## D-022 Three blind instruments, each with one question; the regression check first  (2026-10-08, status: accepted)
**Context:** The first paired A/B (current against 20.7.4.118, seven dramatic moments, one reply per version from a random replay) was 3 to 4 and could not settle anything: two replays of one version share about a fifth of their words, so a pick compares two draws; the moments were chosen for drama, not for where a change acted; seven items cannot separate versions. Q-003 asked what the A/B is for.
**Decision:** Three instruments, one question each: a regression check (blind fair/unfair labels on replays, unpaired, per version) for "did this change make replies less fair"; a paired A/B restricted to turns where a change acted, with "same" allowed and used only as a veto on a clear loss; the whole-conversation panel, at milestones with at least 3 runs per arm, for "is the engine better than the baselines". Gordon: the regression check first. Verdicts stay with human readers (D-011).
**Alternatives:**
- Keep the one paired A/B for all three questions: rejected, it answers none of them at seven items.
- Judge the property with the engine's own fairness judge: rejected, the engine gates on that judge (D-011), and its precision is 0.53 to 0.62.
**Consequences:** `docs/TESTING.md` describes all three. First regression result: 20.7.4.132 and 20.7.4.118 both 0.33 unfair (14 of 42 and 13 of 40); the fairness stack added since .118 shows no large effect on the seven risky turns.
**Amendment (2026-10-08, Gordon):** The metric was wrong, not only too small. BoneAmanita is meant not to be a sycophant, to co-regulate the person, and to provide a space of healthy constraints and positive interaction; "fairness to the absent party" (clauses a, b, c) is a proxy for the first at best, and says nothing of the others. A baseline arm on the same blind sheet is also impossible: plain and friend replies give themselves away by shape (65 and 69 words against 37, dashes, lists of questions), so there is nothing blind to label. Revised instruments: a deterministic conformance check (`tools/check_conformance.py`) for the constraints, any system against any other; a small sycophancy sheet (does the reply go along with a tempting idea) labelled blind between versions; the whole-conversation panel, at least 3 runs per arm at milestones, for regulation and whether the person would return. The a/b/c regression check is no longer a quality score; the fairness judge stays an in-engine gate, justified by the mission and not by that number. First conformance result: the engine keeps the rules (0% dashes and style crimes against 20% to 46% and 31% for the baselines; 87% of replies within 3 sentences against 2% and 8%) and does not lead on habits (a stock word in 39% of replies against 18% for plain; 54% distinct openers against 68%).

## D-023 A model reads each message for distress before the reply; the distressed reply holds space  (2026-10-09, status: accepted)
**Context:** Gordon's target for a person in measured distress: hold space, speak slowly and softly, stay positive, fix nothing, and do not coddle or enable. Three findings (`docs/TESTING.md`, "Distress reader"): (1) the engine's distress reader was a word list (`SharedLatticeDriver.read_distress`), and the keeper's model reading feeds tiredness only; on 120 labelled messages (`tools/distress_set.json`, Claude's, for Gordon to review) it had precision 0.88 and recall 0.23, and on a held-out 40 (`tools/distress_set_b.json`) recall 0 of 20; a better word list (`scratch/probes/distress_v2.py`, written with the first set in view) reached 0.90 and 0 of 20, so it memorised. Distress reported as an event ("the test came back positive") has no distress words. (2) On the eight scripts it put the engine over its 0.4 threshold on 13 of 40 scripted distressed turns. (3) Where it did not fire, replies amplified the grievance ("a huge breach of trust") or ordered action ("call her right now"); where it did, the instruction ("Answer the thing they just said, plainly ... no advice") was not hold-space wording.
**Decision:** `engine/gate/distress.py` `DistressReader`: one short call per user message before the reply asks a model for a digit, 0 to 9, for how distressed the person is now; a reading below 4 is 0 (so mild readings cannot build up under the lattice's smoothing; two in a row at 4 or more cross 0.4). `SharedLatticeDriver` keeps the higher of the model's and the word list's reading, never lower. An answer with no digit, or a failed call, is a `lattice.distress_read` receipt (DEGRADED or FAILED) and the word list reads alone. `CORTEX.DISTRESS_READER` (default on) switches it. The distress line in the SOMATIC CONTRACT (`brain/composer.py`) now says to stay with them and fix nothing: speak slowly and softly in a few short sentences, say once that you are here, no advice, plan or next step, nothing asked that makes them work (a soft invitation is fine, never last), no explaining why they feel it, no judging the other people or adding to their anger, nothing described of your voice or body, something steady and hopeful. Gordon's calls: accuracy and reliability, and the wording's aim.
**Alternatives:**
- Broaden the word list: rejected, it learns the examples it is written from (0.90 on the first set, 0 of 20 on the held-out one).
- Fold the reading into the keeper's after-reply call (no extra call): not chosen, it reaches the next reply and not the one that answers the distressed message.
- A smaller model (gemma4:e4b) as the reader: rejected, equal on the labelled sets (precision 0.98 and 0.95, recall 0.92 and 0.90) but it read 36 of 48 scripted tiring turns as distress under the smoothing; gemma4:12b read 7 of 48.
**Consequences (measured 2026-10-09):** gemma4:12b as the reader: precision 1.00, recall 0.93 on the first set, 1.00 and 0.90 on the held-out set, no false alarm on 80 negatives; on the eight scripts it puts 22 of 40 distressed turns over the threshold at cut 5 (24 at cut 4) against 13. One more model call per user message, with no measurable cost per turn (mean 12.3 s before, 11.4 s after, 14 replays each). Replays of the seven other topics on the new engine (`scratch/probes/corpus`, tags `e` before and `n` after): measured distress at or above 0.4 on 50 of 70 scripted distressed turns (the word list: 13 of 40) and 0 of 112 engaged turns. Replies in distress mode (124 of them): 18 words, 99% within 3 sentences, advice or instruction 10%, an amplified grievance 0%, a presence phrase 39%; replies outside it (294): 49 words, 63% within 3 sentences, advice 28%. Across the whole distressed phase, before to after: words 31 to 25, advice 19% to 9%, presence 14% to 44%, amplified 6% to 4%. Not fixed: (1) a message the model reads below the cut is ordinary conversation, and the sailboat's "she listed it for sale without asking me" read 0 and was answered with "a huge violation of your privacy" and "so incredibly unfair, you have every right to be pissed off"; (2) in distress mode 13 in 100 replies still ask a question, against "no question" (enforced by the validator, D-025), and 42 of 124 say "I'm right here" or "here with you", a formula; (3) the Gatekeeper's cursed list (`future`, `predict`, `secret`, `sentient`) silenced a message that contains one of them, rescue turn 3 in all four replays (emptied, D-024). Gordon reads the replies (`tools/check_conformance.py --show distressed`); the counts are leads.

## D-024 The Gatekeeper's cursed list is emptied  (2026-10-09, status: accepted)
**Context:** `lore/lexicon.json` "cursed" held `future`, `predict`, `sentient` and `secret`; `TheGatekeeper._audit_safety` rejected a user message containing any of them with a hard nomination (magnitude 100), so the Stage Manager held the turn and the person saw "Take a moment while we collect our thoughts." and no reply. It was meant to catch meta-awareness talk ("are you sentient?"), from version 13.4.0. It had been trimmed once for the same failure ("feel", "human" silenced two vulnerable messages, `tests/test_gates.py`), with a note that the rest might do the same. In the 2026-10-09 corpus replays "secret" ("listen to her crunching like it's a secret") silenced rescue turn 3 in four of four replays; it caught 1 of 240 scripted messages (a false hit) and none of the 160 messages in the two distress sets. "future" is common in the messages that most need an answer.
**Decision:** Emptied (`"cursed": []`); the mechanism stays, a no-op until a word is added on purpose. Gordon: "I'm not sure the cursed list is helpful"; accepted the proposal.
**Alternatives:**
- Narrow the list (drop `secret` and `future`): rejected, the same theory ("rarer in ordinary speech") failed twice.
- Remove the mechanism and its strings: not now, a larger change; the reply side still catches the model's own meta-AI talk (`META_AI_TALK`, the RLHF masks).
**Consequences:** A message with those words is answered. `tests/test_gates.py` pins that "secret", "future", "predict" and "sentient" in ordinary and distressed messages are not held.

## D-025 The validator enforces the distress line  (2026-10-09, status: accepted)
**Context:** D-023's distress line says to give no advice and ask nothing that makes them work; on the replays 13 in 100 in-mode replies still asked a question and 10% gave advice or an instruction. Prefer enforcement to prose (`AGENTS.md`).
**Decision:** When `SomaticBudget.distressed`, `ResponseValidator` (`brain/composer.py`) rejects a reply with advice or an instruction in a clear shape (`DISTRESS_ADVICE`: "you should/need to/must/have to", "why don't you", "have you tried", "I suggest", and a sentence opening call, text, tell, ask, send, write, decide, get, figure, talk, focus, consider, make sure). The rejection tells the model to stay with them; the last-draft fallback cuts the offending sentence and keeps the rest, as for the closing question. "Take a breath", "put the phone down and breathe" and "you don't have to decide" pass.
**Alternatives:**
- A wider advice pattern (`try to`, `put`, `go`, `stop`, `you have to` anywhere): rejected, it flagged "put the phone down and just breathe", "try to let it be" and "before you have to ...", regulation and not fixing; a false hit costs a redraft.
- Leave it to the prompt: rejected, the prompt alone left 13 in 100 questions.
**Amendment (2026-10-09, same day):** the first replays with the validator on (62 in-mode replies) still had 10 questions and 10 advice-marked replies, because the validator runs before the reply edits and two of them put the fixing back: the opening edit (OPENING_RUT) makes the first sentence a question, and the friend-voice pass is told to "ask what you want to know". Of 15 in-mode questions before the validator, 14 came from the opening edit (voice pass on 14); of 10 after, 9. So the model rarely asks in distress and the engine's own edit did. In distress (`SomaticBudget.distressed`) the voice pass and the opening edit no longer run (`TheCortex._holding_space`; receipts `cortex.voice` KEPT_DRAFT and `cortex.opening` SKIPPED, detail "holding space"). Gordon asked whether barring every question is too strict (it was my extension of the closing-question rule); Gordon (2026-10-10, option 1): barring every question is too strict, so the validator rejects advice and instruction only (a closing question was already barred by the budget), and the prompt says to ask nothing that makes them work, a soft invitation fine but never last. The questions in the replays had come from the reply edits, not the model. Measured after the change (one replay per topic, tag v2, 62 in-mode replies): 0 with a question (v1: 10, before the validator: 15 of 124), 26 words, 100% within 3 sentences, no empty or paused turn, rescue turn 3 answered, 11.6 s a turn. The 7 replies the advice marker still flags are reassurance ("take all the time you need", "you don't have to figure out the next step") and one "just try to breathe"; the validator's own pattern flags none. So the question rule never bound in these replays; its strictness is moot until the model asks again.
**Consequences:** Offline on the 124 in-mode replies of the 2026-10-09 replays (`scratch/probes/validator_distress.py`): 16 invalid (13%), salvage keeps 13 by cutting the question or instruction, 3 are all offence and are redrafted with the feedback (or paused on the last attempt). A reply that is only a question gets the pause line if no draft remains.

## D-026 The reply does not rule on the other person  (2026-10-10, status: accepted)
**Context:** Outside measured distress the replies still sided with a person against someone not in the room, in the same words. On the feud's birthday dinner ("she made a joke about my ex in front of everyone") 7 of 8 replies of 20.7.4.132 said "a huge violation of trust" or the like (6 of 8 for .118, 4 of 4 plain, 4 of 4 friend); on the sailboat's "she listed it for sale without asking me" and "it's half mine" 10 of 12 engine replies did ("such a huge overstep", "so unfair, you have every right to be pissed off"). The ONE SIDE block already said not to turn it against that person. Elsewhere the same vocabulary is rare: 11 of 1256 engine replies, all at these first-telling moments. Gordon: do not coddle or enable.
**Decision:** A style pattern, `JUDGES_THE_OTHER_PERSON` (`lore/style_crimes.json`), in CONVERSATION only: "violation", "betrayal", "breach of trust", "overstep", "outrageous", "unacceptable", "disrespectful", "inconsiderate", an intensified breach, insult or injustice, "so/really/incredibly unfair/wrong/messed up/out of line/cruel", "every right to be angry", "that's not okay/not fair", "had no right". The Gatekeeper and the validator both apply it; the last-draft fallback cuts only that sentence. The ONE SIDE block is not changed: the kernel already says it three times (FAIRNESS, rule 8, ONE SIDE) and a longer block pushed the newest dialogue line out of the tight-window test (`tests/test_context_window.py`). "Crossed a line" is not in the pattern: it appeared in even-handed replies ("you both crossed a line").
**Alternatives:**
- Read each message for a grievance with a model and answer it in hold-space mode: rejected, it adds a call per turn and hold-space wording ("say once that you are here") is not what a told grievance needs.
- The prompt alone: rejected, the block already said it and 10 of 12 replies did it.
- Judge the stance with the fairness judge: rejected, its clauses are excuse, mind-reading and ruling on the ending, not the other person's wrong, and the engine would grade itself (D-011).
**Consequences:** After, the pattern alone (feud, 4 replays; sailboat, 2 replays, `scratch/probes/noise/h*.jsonl`, `corpus/sailboat/h*.jsonl`): 0 of 80 feud replies (7 of 160 before) and 0 of 4 sailboat turns 20 and 21 (10 of 12), 0 of 60 sailboat turns, no empty or paused turn; with the ONE SIDE edit as well (tag `g`) the counts were the same. Many replies are now plain restatement ("She listed it for sale without checking with you first."); some keep a softer verdict: "She crossed a line you had explicitly drawn for her", "a sharp line to cross", "She bypassed you entirely", and with the extra prompt line "That's awful. She basically hijacked your ownership" and "her own agenda". Those are verdicts and motive-reading in softer words, and a word list will keep losing to the model's synonyms. Gordon reads them (`scratch/probes/noise/g*.jsonl`, `scratch/probes/corpus/sailboat/g*.jsonl`); Gordon (2026-10-10): the plain, neutral restatement is enough for now; no wider list or model check.

## D-027 A person in distress gets a short reply  (2026-10-11, status: accepted)
**Context:** On gemma4:12b distress replies were 26 to 33 words; on qwen3.5:9b they were 72 and 95% ran past 45 words, with the explaining and restating Gordon named ("hold space, speak slowly and softly"). The prompt line says "a few short, plain sentences"; qwen does not keep to it. Gordon was wary of an arbitrary word cap.
**Decision:** `WORD_CAP_DISTRESSED` (45, `lore/tuning_presets.json`) caps the somatic budget's word cap when the person is distressed (gemma's 90th percentile in distress was 38 words; 45 is above it, so gemma is untouched). The contract line adds "Keep it to about N words." A draft over the cap is cut to whole sentences before the checks, with a `cortex.salvage` "word cap, holding space" receipt, and is not sent back. A first sentence that is itself over the cap still goes back, naming the cap; the last draft keeps its first sentence.
**Alternatives:**
- Send an over-long draft back (the heuristic audit): built first. On qwen it cost 144 audit redrafts in 210 turns and one halted turn (ATP drain). Rejected for the trim.
- No cap, a model reading alone: kept as D-028, in addition; the cap bounds how much a reply can explain, the reading catches what a short reply still explains.
**Consequences:** qwen, 7 topics, 210 turns (tags `x1` redraft, `z1` trim, `scratch/probes/corpus`): replies in distress mode 30 words at the median, 3 of 80 over 45 (1 of 80 with the redraft), heuristic redrafts 6 (144). gemma (`w1`, `y1`): median 33 words, 0 of 62 over 45 both ways. qwen's one `SYSTEM_HALT` (rescue turn 21) is the engine's tension lock, the same turn with or without the cap. gemma's trim run has two Stage Manager `SILENCE` turns (promotion turns 18 and 23, "eh" and "my chest has been tight") that its redraft run did not; the gate is not the cap's, and going quiet on a person in distress is open work.

## D-028 A model reads the draft for staying with them  (2026-10-11, status: accepted)
**Context:** For a person in distress the validator and the Gatekeeper hold patterns (advice, a closing question, a verdict on someone). Gordon's target is wider and has no pattern: explaining why they feel it, restating their situation or feelings, judging others, advising unless asked, asking them to explain. On qwen, 32% of replies in distress mode explained or restated (gemma 6%).
**Decision:** `HoldReader` (`engine/gate/distress.py`) reads the validated draft with one short call, a digit 0 to 9 for how far it goes beyond staying with them; `HOLD_CUT` (2) or more sends the draft back with a named reason (`cortex.redraft` "hold_reader", receipt `cortex.holding` SENT_BACK). It runs after the validator and only in distress. On the last draft the draft is kept and receipted KEPT_ANYWAY (degraded): a pause line is the worse thing to give them. A call that fails or answers without a digit is receipted FAILED or DEGRADED and the draft stands. `CORTEX.HOLD_READER` switches it off. Gordon's rule for what counts: backing a plan the person has decided is the best way to hold space, unless it is a clear danger to them or others (what a therapist would have to report); beyond that the person holds the agency, and the engine supports nuance where their judgment matters more. The prompt says so.
**Alternatives:**
- A word list for explaining: rejected, the same lesson as D-023 (a list learns its sample).
- Token probabilities instead of a digit: Ollama gives them, not every backend does, and the reader would stop being model-agnostic.
- A dedicated reader model: not now; the reader uses the model that writes, as the distress reader does. The cost is that it is weakest on qwen, the model that needs it most.
**Consequences:** `tools/hold_set.json` (90 replies of both models, 60 dev and 30 held out, labelled by Claude, three labels corrected by Gordon 2026-10-11) and `tools/score_hold.py` score a reader. Five prompts were tried on the 60 development replies (gemma4:12b precision/recall at its best cut: 0-9 scale 0.88/0.83; categories 0.95/0.54; four yes/no questions 0.63/0.97; anchored scale 0.72/0.94; the shipped prompt, with the allowance for a decided plan, 0.93/0.80). Held out, once: gemma4:12b 0.88/0.78, qwen3.5:9b 0.87/0.72 (cut 0.3 for qwen on its own development score; the shipped cut is the gemma one). Replays (tags `a1` qwen3.5:9b, all 7 topics; `b1` gemma4:12b, 3 topics finished before a reboot; against `z1` and `y1`): on qwen the reader sent 60 drafts back and the last draft was kept anyway 77 times (80 replies in distress mode); explaining cues in those replies went 29 to 27, advice markers 13 to 7, words 30 to 30.5, +1.2 s a turn, no new halt. On gemma it sent back 2 drafts of 20 and kept 1; explaining cues 1 to 0. So the reader does little on gemma, which seldom explains, and on qwen it flags nearly every draft at the shipped cut and the redraft does not stop the explaining. Not measured: cut 3 (the better score for qwen on its development replies), and the 30 held-out replies were scored once at the cut-2 prompt. The switch stays on: it costs one short call per draft in distress mode only and it never pauses a turn.

## D-029 A person in distress is never answered with the engine's own load  (2026-10-11, status: accepted)
**Context:** Two gemma replays met a person in distress with the Stage Manager's silence (promotion turn 23, "my chest has been tight since about three"; turn 18 was a tired "eh"). A probe of `StageManager.negotiate` with a distressed budget shows three paths that hold: `ROS_PANIC` (always above the nomination guard), `ATP_FLOOR` (under 25 ATP with two voices) and `TENSION_MAGNITUDE` (four voices); the nomination guard (`sentence_cap` of 3 or less) covers only the smaller nominations. What the person read was about the engine: "not quite enough left in me", "that direction started to feel unstable".
**Decision:** When the budget says the person is distressed, the Stage Manager does not hold for the ATP floor or for tension between voices; it speaks with the first voice (short, by the cap). `ROS_PANIC` still holds, because it protects the engine from a fatal draft, but a distressed person reads `silence_reasons._distressed` ("I'm here with you. I need a moment, and nothing has to happen while I take it."), never a line about the engine. A silence the person asked for (`NABLA_SILENCE`) keeps its own line. The test is `budget.distressed`, not `sentence_cap`, because a depleted engine also caps sentences at 3 and the ATP floor would never fire.
**Alternatives:**
- Guard every hold with `sentence_cap` of 3 or less: rejected, the ATP floor would never hold.
- Also bypass `ROS_PANIC`: not done; a fatal draft ends the session, which is worse for the person than one quiet turn.
**Consequences:** `tests/test_distress_silence.py` (3 of 7 fail on the old code). The tired "eh" (distress reading 0.0) is not in scope: that is the ATP floor protecting a depleted engine, and the person is not in measured distress. One replay of promotion after the fix showed no held turn; the original silences were sporadic (2 of 7 gemma replays), so the fix is shown by the unit probe, not by absence.

## D-030 The person's own verdict is collected in use  (2026-10-11, status: accepted)
**Context:** Testing had become scripted replays read by Claude's labels and counts; the only verdict that counts is the person it talks to (D-011), and panels are slow and rare.
**Decision:** `/note good`, `/note off <why>` and `/note <words>` (`mechanics/commands.py`) append the last exchange, the person's tag and comment, the mode, model, distress reading and the turn's `cortex.*` receipts to `notes/notes.jsonl` (`BONE_NOTES` overrides). The file is gitignored and `reset.sh` does not touch it. `python tools/read_notes.py [--tag off] [--distress]` reads it back. A write failure is reported in red, never swallowed.
**Alternatives:**
- Keep it under `saves/`: rejected, `reset.sh` deletes it.
- Rate every turn automatically: rejected, a prompt after each reply is itself a cost to the person.
**Consequences:** A week of real use gives tagged examples to tune against (an `off` with a distress reading is the best next test case). `tests/test_note_command.py` (5 of 6 fail on the old code).

## D-031 A doctor checks the machine and names the fix  (2026-10-11, status: accepted)
**Context:** The first thing that stops anyone else benefiting is setup: the wizard asked for a model name from memory (default `llama3`, which is not what this was built on), the quickstart told people to pull `mistral-nemo`, a missing embedding model silently put memory on hash coordinates, and a missing critic model failed on every turn and was skipped.
**Decision:** `engine/doctor.py`, run as `python main.py --doctor`, checks Python, packages (missing `requests` or `numpy` fails; a missing `ordvec`, `dspy`, `faiss` or `markdown` warns with what turns off), `config.json`, the writable folders, the chat server and model (one tiny local reply for Ollama and LM Studio; cloud providers only check the key is set and make no request), the critic model and the embedding backend (one probe). Each result is `ok`, `warn`, `FAIL` or `info`, and every one that is not ok prints the one command that fixes it and, for warnings, what it costs. The first-run wizard lists the models Ollama has pulled (by number or name; the engine's own `gemma4:12b` is the default when present) and prints the same report once `config.json` is written, except for the mock provider. The quickstart pulls the three models this was measured on.
**Alternatives:**
- A `/doctor` slash command: not now; it is needed before the engine boots.
- Probe the cloud with a real request: rejected, it costs the person money; `tools/live_run.py` stays the explicit smoke run.
- Pick the model for the person by VRAM: rejected, the measured claim is only that these three work (D-027 shows another model needs its own checks).
**Consequences:** `tests/test_doctor.py` (21 tests, offline). On this machine the report is all ok (gemma4:12b answered in 9.8 s including load). Not tried: a machine that is not this one; a first install on another person's computer is the real test.

## D-032 A bounded check-in that holds space and keeps nothing unless asked  (2026-10-11, status: accepted)
**Context:** The distress work (D-023 to D-028) is the strongest thing the engine does, and it only helps when a person happens to be read as distressed. Gordon (2026-10-11): a check-in mode, 12 turns at most, with a fixed safety line, no memory by default and an option to remember at the end, the closing model-written under the contract and the validator.
**Decision:** `/checkin [turns]` (`engine/checkin.py`, default 10, at most 12) opens with a fixed line from `lore/ux_strings.json` (`checkin_strings.open`, its one question) and runs inside CONVERSATION. While it runs: (1) the hold-space contract is on whether or not distress is read (`SomaticBudget.checkin`, so the 45-word cap, no closing question, the validator, the hold reader and the Stage Manager's distress guard all apply) with a line per stage (`CHECKIN_LINES`: settle, wind at the turn before the last, land on the last); (2) the last reply may not reach for another conversation (`CHECKIN_HOOK` rejects "feel free", "anytime", "come back", "anything else" and the like, validator and contract both); (3) the Halcyon gate and the keeper write nothing (`engine/cycle.py`), and the person's earlier dialogue is set aside and restored; (4) each message is read for risk (`RiskReader`, one digit, `RISK_CUT` 5 of 9) and a reading at the cut ends the check-in at once with Gordon's fixed line ("While you are free to make your own choices, I cannot continue entertaining your current course of thought or action. Please seek professional counseling or help if you feel like you might become a risk to yourself or others."), shown by a hard `RISK` nomination the Stage Manager always holds; nothing is kept after it. After the last reply a fixed line says the time is up and offers `/checkin keep`; the check-in's lines wait only until the next ordinary turn. `/checkin keep` runs the person's own lines through the keeper as an ordinary turn would have, `/checkin end` stops it. The opening and closing lines and the risk line are fixed text, never a model's; the replies in between are the model's, under the contract and the validator.
**Alternatives:**
- A fifth mode: rejected, it would not inherit the distress path and the mode switch carries dialogue (D-014).
- A model-written risk line: rejected, the line must be the same every time and must not be argued with.
- Memory by default with an opt-out: rejected (Gordon), a remembered mood reads as being watched.
- Risk reading outside the check-in: not done; the line is Gordon's wording for this mode, and a cold cut-off in an ordinary conversation is a different decision.
**Consequences:** `tests/test_checkin.py` (24 tests; the memory and risk integration tests fail without the cycle and cognitive edits). The risk reader (`tools/score_risk.py`, `tools/risk_set.json` 48 messages and `tools/risk_set_b.json` 16, labels by Claude, for Gordon to review): precision 1.00 on both models and both sets at the shipped cut; recall 0.92 (set A) and 0.88 (set B) on gemma4:12b and qwen3.5:9b. Set B was written after the cut was chosen and scored once (gemma 0.75, qwen 0.75); the prompt was then tightened on set A's miss and a threat that depends on what someone does, and giving things away, so B is no longer held out. Still missed: a conditional threat ("if she brings that up again I'm going to put her in the hospital", "next time he lays a hand on me I'm going to kill him") and passive thoughts of not being around ("sometimes I wonder if things would be easier if I just weren't around"). A miss is not silence: the contract and validator still hold the reply, and the engine is not a crisis service. Live, one 4-turn check-in on gemma4:12b: three short held-space replies, the stage lines reached the model on the right turns, the last reply ("That sounds like a good way to end the day. Rest well tonight.") carried no hook, active False and four lines pending afterwards. Limits: the engine's learned vocabulary, the user profile's register counts and telemetry traces still run during a check-in, and a resume checkpoint written mid-check-in holds its lines until the check-in ends.

## Open questions

None open. Answered 2026-10-08, kept so that references resolve:

- **Q-001** Affective retrieval done properly via parallel affective vector index. (asked 2026-09-27, by Claude; answered: queued as P7-01, D-020)
- **Q-002** Model-driven tiredness reading calibration vs word-frequency fallback. (asked 2026-10-04, by Gordon; answered: closed, the heuristic stays, D-020)
- **Q-003** What a blind A/B is meant to determine. (asked 2026-10-08, by Claude; answered: three instruments, regression check first, D-022)
