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

- **The model never performs a body:** The model is forbidden from narrating physical exhaustion, breathlessness, or biological roleplay. Enforced by `SomaticBudget.forbid_body_narration` and `tests/test_composer.py` (D-001).
- **Poetic variable names are load-bearing:** Variables like `atp_pool`, `cortisol`, and `godel_scars` map to real control loops and must not be renamed (D-003).
- **Fail loudly:** No broad `except Exception: pass` handlers; phase crashes are recorded in `record_crash` and isolated by `PhaseExecutor`. Enforced by `tests/test_failure_boundaries.py` and `tests/test_observability.py` (D-015).
- **Test suite runs offline:** Tests run without network access or running model servers. Enforced by `tests/__init__.py` setting `BONE_EMBED_BACKEND=hash` (D-007).
- **Sensitive credentials withheld:** Passwords, API keys, and card numbers are redacted with `[withheld: ...]`. Enforced by `engine/gate/secrets.py` and `tests/test_secrets.py`.
- **Substrate writes sandboxed:** File modifications outside the engine are confined to `output/` and require `/allow` permission (P3-02).

## Boundaries

| Boundary | Comes in as | Checked by | Rule |
| --- | --- | --- | --- |
| Partner message | String from terminal or API | `mechanics/lexicon.py` | Word classification; filler, curated lists, and resonance |
| Model reply | Raw text stream from LLM | `TheGatekeeper` in `physics/filters.py` | RLHF masks and style crimes; soft crimes salvaged, hard crimes paused (D-008) |
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
