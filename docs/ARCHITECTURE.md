# Architecture

How BoneAmanita fits together. This document describes the system components, data flow, invariants, and boundaries.
Detailed design rationales live in [DECISIONS.md](DECISIONS.md).

## The shape, in one paragraph

BoneAmanita mediates between a human partner and a local language model. On each turn, the partner's message is
received by `main.py` and processed through `engine/cycle.py`. The input is observed for lexical density and emotional
cues; `physics/` and `body/` update roughly sixty state metrics (ATP, cortisol, voltage, narrative drag);
`brain/composer.py` queries `body/somatic_budget.py` and composes a structured prompt; the local model generates a reply;
`physics/filters.py` scans for clichés and salvages clean sentences; in CONVERSATION, `brain/cortex.py` then edits the
reply (voice, ending, opening, fairness); and the final state is committed to SQLite in `saves/iris.db`.

## System Topology

BoneAmanita bounds ephemeral LLM execution within a three-speed epistemic memory manifold:

```text
                      ┌────────────────────────────┐
                      │    AI Context (Śūnya)      │
                      │  Empty, unconditioned,     │
                      │   ephemeral potentiality   │
                      └─────────────┬──────────────┘
                                    │ Projects from & Writes to
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                BONEAMANITA MEMORY MANIFOLD              │
       ├─────────────────────────────────────────────────────────┤
       │  ŚRUTI LAYER (docs/INVARIANTS.md)                       │
       │  - Axioms INV-001 through INV-010                       │
       │  - Immutable foundational laws                          │
       ├─────────────────────────────────────────────────────────┤
       │  SMṚTI LAYER (AGENTS.md, ARCHITECTURE.md, DECISIONS.md) │
       │  - The Six Vedāṅgas (Protocol, Lexicon, Grammar...)     │
       │  - Sūtra ADRs (D-NNN), Held Tensions (T-NNN), Roadmap   │
       ├─────────────────────────────────────────────────────────┤
       │  VARTAMĀNA LAYER (docs/HANDOFF.md)                      │
       │  - Ephemeral state qualified by Pramāṇa tags            │
       │  - Strict Chandas bound (<= 80 lines)                   │
       ├─────────────────────────────────────────────────────────┤
       │  SOMATIC SUBSTRATE & VYĀKARAṆA LINTER                   │
       │  - Phase pipeline, receipts, and SQLite (iris.db)       │
       │  - check_docs.py Ghana-pāṭha & firewall enforcement     │
       └─────────────────────────────────────────────────────────┘
```

## Code map

| Area | Where | Entry point | Talks to |
| --- | --- | --- | --- |
| Main REPL | `main.py` | `BoneAmanita.process_turn()` | `engine/cycle.py`, `mechanics/terminal.py` |
| Turn Lifecycle | `engine/cycle.py` | `CycleSimulator.run_turn()` | `phases/`, `engine/core.py`, `engine/receipts.py` |
| Somatic Physics | `physics/` | `QuantumObserver.gaze()` | `body/metabolism.py`, `body/endocrine.py` |
| Biological State | `body/` | `SomaticLoop.digest_cycle()` (`body/system.py`) | `BioSystem`, `MitochondrialForge`, `SomaticBudget` |
| Prompt Brain | `brain/` | `PromptComposer.compose()` | `brain/prism.py`, `brain/cortex.py`, LLM transport |
| Cortex & reply edits | `brain/cortex.py` | `TheCortex.process_context()` | Cognitive loop, `TheGatekeeper`, DSPy critic, fairness judge |
| Gatekeeper | `physics/filters.py` | `TheGatekeeper.mitigate_rejection()` | `lore/style_crimes.json`, `engine/receipts.py` |
| Memory & Spores | `spores/` | `SemanticEmbedder.embed_batch()` | Ollama `/v1/embeddings`, `spores/memory.py` |
| The Village | `archetypes/` | `StageManager.negotiate()` | `archetypes/village.py`, `brain/composer.py` |
| Distress reader | `engine/gate/distress.py` | `DistressReader.read()` | `drivers/lattice.py` (`SharedLatticeDriver`), `body/somatic_budget.py`, `brain/composer.py`; one short model call per message before the reply, the word list as floor (D-023) |
| Risk reader | `engine/gate/distress.py` | `RiskReader.flags()` (`at_risk`, and the repeat watch of D-034) | `phases/cognitive.py` (the `RISK` nomination, every conversation but a story; D-033), `main.py` (`engine.risk_reader`) |
| Check-in | `engine/checkin.py` | `CheckIn` | `main.py` (`after_turn`), `mechanics/commands.py` (`/checkin`), `phases/biological.py` (the stage reaches `SomaticBudget.checkin`), `phases/cognitive.py` (the `RISK` nomination), `engine/cycle.py` (the gate keeps nothing); D-032 |
| Doctor | `engine/doctor.py` | `run_doctor()`, `render()` | `main.py --doctor`, `mechanics/setup.py` (first run); read-only checks, no paid request (D-031) |
| Hold reader | `engine/gate/distress.py` | `HoldReader.goes_beyond()` | `brain/cortex.py` (`_beyond_staying_with`, in the retry loop after the validator, distress mode only); one short call per draft, sends it back, keeps the last (D-028) |
| Sūtra Consolidator | `engine/gate/sutra.py` | `SutraConsolidator.consolidate()` | `engine/cycle.py` (`consolidate_sutras`), `engine/gate/store.py`, `mechanics/commands.py` (`/sutra`); distills memories into invariant seeds in REM (D-036, P11-01) |
| Halcyon Store | `engine/gate/` | `Store.save_checkpoint()` | `saves/iris.db`, `engine/gate/secrets.py` |
| Slash Commands | `mechanics/` | `CommandProcessor.execute()` | `mechanics/commands.py`, engine subsystems |

## Interfaces and data flow

```text
Partner Input -> Lexical Observation -> Metabolic Processing -> Cognitive Assembly -> LLM Synapse -> Gatekeeper Salvage
  -> Reply Edits (CONVERSATION: voice, ending, opening, fairness) -> SQLite Checkpoint
```

| Interface | Producer | Consumer | Contract / compatibility |
| --- | --- | --- | --- |
| `CycleContext` | `engine/cycle.py` | Turn phases in `phases/` | Mutable dataclass carrying turn state and receipts |
| `PhysicsPacket` | `physics/observer.py` | `phases/biological.py`, `body/` | Kinematic coordinates (voltage, drag, chi) |
| `SomaticBudget` | `body/somatic_budget.py` | `brain/composer.py` | Word/sentence caps, temperature band, body narration rules |
| `Receipt` | Engine subsystems | `engine/receipts.py:ReceiptLedger` | Subsystem work receipts audited by `/diag` (D-015) |
| SQLite Schema | `engine/gate/store.py` | SQLite `saves/iris.db` | WAL mode, foreign keys enabled, single-row checkpoint |

## Invariants

The immutable axiomatic foundation is codified in [INVARIANTS.md](INVARIANTS.md) (Śruti). Core architectural invariants include:

- **INV-001 [The model never performs a body]:** The model is forbidden from narrating physical exhaustion, breathlessness, or biological roleplay. Enforced by `SomaticBudget.forbid_body_narration` and `tests/test_composer.py` (D-001).
- **INV-002 [Zero external orchestration frameworks]:** LangChain, LlamaIndex, SemanticKernel, and dedicated vector packages are excluded in favor of standard-library and minimal HTTP transport (D-002).
- **INV-003 [Poetic variable names are load-bearing]:** Variables like `atp_pool`, `cortisol`, and `godel_scars` map to real control loops and must not be renamed (D-003).
- **INV-004 [Test suite runs offline]:** Tests run without network access or running model servers. Enforced by `tests/__init__.py` setting `BONE_EMBED_BACKEND=hash` (D-007).
- **INV-005 [Human evaluative primacy]:** Production verdicts on conversational authenticity come from human reading panels, never automated AI judges (D-011).
- **INV-006 [Fail loudly]:** No broad `except Exception: pass` handlers; phase crashes are recorded in `record_crash` and isolated by `PhaseExecutor`. Enforced by `tests/test_failure_boundaries.py` and `tests/test_observability.py` (D-015).
- **INV-007 [Sensitive credentials withheld]:** Passwords, API keys, and card numbers are redacted with `[withheld: ...]`. Enforced by `engine/gate/secrets.py` and `tests/test_secrets.py`.
- **INV-008 [Substrate writes sandboxed]:** File modifications outside the engine are confined to `output/` and require `/allow` permission (P3-02).
- **INV-009 [Zero silent assumptions]:** Unverified assumptions may never be silently compiled into implementation. Ambiguity triggers clarifying questions (*Praśna*) or open questions (`Q-NNN`) in `docs/DECISIONS.md` before building (P12-01, P12-02).
- **INV-010 [Anti-superimposition]:** Pre-trained model priors may never be superimposed onto the repository; all conventions must trace to explicit `[CONTRACT]` or `[OBSERVED]` repository truth (P12-01, P12-02).

## Boundaries

| Boundary | Comes in as | Checked by | Rule |
| --- | --- | --- | --- |
| Partner message | String from terminal or API | `mechanics/lexicon.py` | Word classification; filler, curated lists, and resonance |
| Model reply | Raw text stream from LLM | `TheGatekeeper` in `physics/filters.py` | RLHF masks and style crimes (including `STOCK_EMPATHY`); soft crimes salvaged, hard crimes paused (D-008, D-037) |
| Embedding backend | JSON from `/v1/embeddings` | `SemanticEmbedder` | Checked for 768d vectors; network errors fall back loudly to hash (D-005) |
| File modifications | `<write_file>` blocks | `mechanics/tools.py` | Contained to `output/`; existing files held until `/allow` |

## Dependencies

| Dependency | Version (`requirements.txt`) | For | Why this one (and not writing it) |
| --- | --- | --- | --- |
| `numpy` | `>=1.24.0` | Vector math and array calculations | Standard compiled array math; FAISS needs contiguous arrays |
| `faiss-cpu` | `>=1.13.2` | Nearest-neighbor vector search | Efficient CPU similarity indexing |
| `requests` | `>=2.31.0` | HTTP to local LLMs and the embeddings endpoint | Reliable HTTP connection handling |
| `dspy`, `dspy-ai` | `>=2.4.0` (`dspy-ai`) | The real-time critic in `mechanics/dspycritic.py` | Structured judge calls with its own LM, timeout and retries |
| `ordvec` | `>=0.5.0` | 4-bit `RankQuant` sign bitmap governor | Project Navi's fast bitmap quantization (D-010) |
| `markdown` | unpinned | Markdown generation and rendering | Light text rendering |
| `pytest` | unpinned | The test suite | Standard runner |
| Python standard library | 3.14 | SQLite, hashlib, urllib, threading | Standard library preferred over external frameworks (D-002) |

## State and Caches

Everything a run leaves on disk or in external stores, and what may delete it. Reset commands must never wipe expensive caches without warning.

| What | Where | Written by | Reset by | Committed? |
| :--- | :--- | :--- | :--- | :--- |
| Persistent SQLite store | `saves/iris.db` | `engine/gate/store.py` (`Store`) | `sh reset.sh` | No, gitignored |
| Subconscious Sūtra seeds | `self/memory/sutra.*` | `engine/gate/sutra.py` (`SutraConsolidator`) | Manual pruning or `sh reset.sh` | No, gitignored |
| Replay corpus rows | `scratch/probes/corpus/` | `tools/corpus_replay.py` | Manual cleanup | No, gitignored |
| Substrate output sandbox | `output/` | `mechanics/tools.py` under `/allow` | `sh reset.sh` | No, gitignored |
| Substrate audit ledger | `output/.substrate_ledger.json` | `mechanics/tools.py` | `sh reset.sh` | No, gitignored |
| Human verdict notes | `notes/notes.jsonl` | `mechanics/commands.py` (`/note`) | Preserved across resets | No, gitignored |
| Built conversation pages | `tools/cache/conv_*.html` | `tools/build_manual.py` | Cleaned before commits | Never committed |

## Failure Modes and Epistemic Mitigations

| Failure Mode | Mechanism in Standard Agents | Epistemic Mitigation in BoneAmanita |
| :--- | :--- | :--- |
| **Cognitive Drift** | Nuanced rules in chat context fade as conversations lengthen. | **Śruti Contracts:** Invariants live in dedicated, immutable files outside the chat (`INV-001` - `INV-010`). |
| **Hallucinated Competence** | Agent assumes untested functions work because they look plausible. | **Pramāṇa Tagging:** Every capability assertion must explicitly state whether it is `[OBSERVED]` or `[UNTESTED]`. |
| **Tautological Testing** | Tests written post-hoc that never failed on defective code. | **Negative Proof Grounding:** Mandatory proof of failure on pre-change code before accepting tests. |
| **Semantic Inflation** | Documents balloon with conversational explanations and boilerplate. | **Sūtra Compression:** Minimal-syllable, high-density propositions save context tokens (`INV-008`, `D-036`). |
| **Sycophantic Cliché & Opener Rut** | Model defaults to formulaic validation ("heavy", "a lot") and repetitive openers. | **Lexical Firewall & Rut Breaker:** Soft style crime salvage (`INV-006`, `D-008`) and consecutive 3-word opener rewrites (`D-037`). |
| **Dangling Intentions** | Tasks mentioned in handoffs are never tracked in roadmaps. | **Ghana-pāṭha Reciprocity:** `check_docs.py` fails if a handoff step is not an active roadmap item. |
| **Silent Assumption** | Agent guesses intent when requirements or edge cases are ambiguous. | **Saṃśaya & Praśna:** Agent halts during *Manana* to ask clarifying questions or log `Q-NNN` before building (`INV-009`). |
| **Prior Superimposition** | Agent projects training-distribution defaults (assumed build steps, packages, idioms) onto the repository. | **Adhyāsa-Nirāsa:** Agent audits priors during *Śravaṇa* and relies only on `[CONTRACT]` or `[OBSERVED]` conventions (`INV-010`). |
| **Linear Tunnel Vision** | Agent discovers a broken premise mid-build and patches locally to reach handoff, widening scope silently. | **Āvartana Loopback:** Agent halts during *Nididhyāsana* or *Pramāṇa* and returns to *Manana* to re-scope or issue *Praśna* (`INV-009`). |
| **Workaround Smoothing** | Agent papers over unexpected test, type, or contract resistance with silent fallbacks or weakened assertions. | **Pratibandha Stop-Trigger:** Agent halts on textual resistance and surfaces the contradiction via *Praśna* or `[HYPOTHESIS]` (`INV-009`). |
| **Fence Demolition** | Agent deletes or refactors an unfamiliar guard or constraint without knowing what defect it prevented. | **Pūrva-Pakṣa Reconstruction:** Agent traces the originating `D-NNN` or `INV-NNN` (or asks *Praśna*) before altering a constraint (`INV-009`). |

## Claims vs. Code

Places where a doc, a name, or a comment says more than the code does, so nobody builds on an unverified claim. When a session encounters friction (*Pratibandha*) where the code contradicts a documented claim (or vice versa), record the mismatch here (`[HYPOTHESIS]`) and ask the maintainer (*Praśna*) rather than papering over the discrepancy in code (`INV-009`). Remove a row when the code catches up or the claim is corrected.

- `physics/`: Suggests a continuous Newtonian / quantum simulation; in practice it is kinematic coordinates (voltage, drag, chi) computed from lexical density thresholds and punctuation rates feeding the prompt and somatic budget.
- `The Village`: Emergent archetypal persona cast; in practice mediated by Stage Manager refusal routing and composer directives rather than separate autonomous model instances.
- `spores/`: Mycelial associative network; in practice a 768d vector index with SHAKE-256 hash fallback in SQLite overlays.

