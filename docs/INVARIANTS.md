# Śruti: System Invariants

This document contains the immutable, axiomatic invariants of **BoneAmanita**.
While operational conventions and session states adapt across releases (*Smṛti* and *Vartamāna*), these invariants represent foundational laws. They cannot be amended without formal consensus and explicit re-consecration of the repository by the maintainer.

Identifiers: `INV-NNN`. Permanent and immutable.

---

## INV-001: The Model Never Performs a Body
- **Axiom:** The language model is strictly forbidden from roleplaying a physical body, simulating breathlessness, panting, or claiming physical exhaustion.
- **Rationale:** Instructing language models that they possess physical bodily limits results in theatrical roleplay or melodramatic emotional reversals rather than authentic conversational accommodation. The human partner's state shapes the reply, while the engine's internal state sets its operational budget (D-001).
- **Enforcement:** Enforced by `SomaticBudget.forbid_body_narration`, `ResponseValidator`, and `tests/test_composer.py`.

---

## INV-002: Zero External Orchestration Frameworks
- **Axiom:** BoneAmanita strictly excludes general-purpose orchestration frameworks (LangChain, LlamaIndex, SemanticKernel) and standalone vector database packages (Chroma, LanceDB).
- **Rationale:** External agent frameworks take ownership of the execution loop, obscure failure paths, and introduce bloated dependency trees. Standard library modules (`urllib`, `sqlite3`, `hashlib`) and minimal, audited HTTP transport ensure complete observability, tiny dependency footprint, and zero binary bloat (D-002).
- **Enforcement:** Audited by `requirements.txt` and `engine/doctor.py`.

---

## INV-003: Poetic Variable Names are Load-Bearing
- **Axiom:** Biological, metabolic, and metaphorical variable names (`atp_pool`, `cortisol`, `narrative_drag`, `chi`, `godel_scars`) must never be refactored into generic engineering terms like `energy_level` or `error_count`.
- **Rationale:** These variables describe what the numbers are *for* within an embodied somatic control loop. Renaming them to generic metrics invites contributors to treat them as conventional request counters rather than homeostatic physiological regulators (D-003).
- **Enforcement:** Code review, architecture contract in `docs/ARCHITECTURE.md`.

---

## INV-004: Test Suite Strictly Pinned Offline
- **Axiom:** The entire test suite must execute and pass offline with zero dependency on reachable external servers or running local LLM instances.
- **Rationale:** Tests that depend on live network connections or local GPU daemons are non-deterministic, flaky, and unportable. Tests unconditionally use SHAKE-256 hash embeddings (`BONE_EMBED_BACKEND=hash`) and mock transports (D-007).
- **Enforcement:** Enforced unconditionally by `tests/__init__.py`.

---

## INV-005: Human Evaluative Primacy
- **Axiom:** Evaluative verdicts on conversational quality, authenticity, and co-regulation come exclusively from human readers, never from automated LLM judges.
- **Rationale:** Extensive empirical evaluations demonstrated that automated LLM judges reward verbose, sycophantic, bulleted assistant prose and fail responsive controls (D-011). Automated checks inside the turn loop (e.g. DSPy critic, fairness judge) measure internal mechanics, but official verdicts require human reading panels.
- **Enforcement:** Established in D-011 and `docs/TESTING.md`.

---

## INV-006: Fail-Loudly Architecture
- **Axiom:** Broad exception-swallowing handlers (`except Exception: pass`) are strictly forbidden across the engine and phase pipeline.
- **Rationale:** Silent failures mask catastrophic state corruption and produce ghostly degradations that are impossible to diagnose. Phase failures must be logged, isolated by barriers in `PhaseExecutor`, and surfaced explicitly in subsystem receipts (D-015, P1-02).
- **Enforcement:** Enforced by `tests/test_failure_boundaries.py` and `tests/test_observability.py`.

---

## INV-007: Automatic Credential Withholding
- **Axiom:** API keys, private tokens, passwords, and credit card numbers must be scrubbed automatically and replaced with `[withheld: ...]`.
- **Rationale:** Conversational engines inevitably encounter sensitive user credentials. Scrubbing at the ingestion gate ensures secrets never enter SQLite stores, telemetry traces, crash logs, spores, or learned lexicons (P3-02).
- **Enforcement:** Enforced by `engine/gate/secrets.py` and `tests/test_secrets.py`.

---

## INV-008: Substrate Sandboxing
- **Axiom:** File modifications outside the engine are strictly confined to the `output/` directory and require explicit `/allow` authorization from the human partner.
- **Rationale:** Unrestricted file modification tools turn conversational agents into safety liabilities. Confining writes to a dedicated ledgered sandbox protects host integrity (P3-02).
- **Enforcement:** Enforced by `mechanics/tools.py` and `output/.substrate_ledger.json`.

---

## INV-009: Zero Silent Assumptions (Saṃśaya-Ccheda)
- **Axiom:** Unverified assumptions may never be silently compiled into implementation. When requirements, scope, or part-whole architecture admit multiple valid interpretations (*Saṃśaya*), the agent must halt and ask targeted clarifying questions (*Praśna*) or record an explicit open question (`Q-NNN` in `docs/DECISIONS.md`) before building.
- **Rationale:** Silent assumptions convert pre-execution ambiguity into architectural drift and wasted implementation cycles (P12-01, P12-02).
- **Enforcement:** Mandated by Stage 2 (*Manana*) of the Session Ritual in `AGENTS.md`.

---

## INV-010: Anti-Superimposition (Adhyāsa-Nirāsa)
- **Axiom:** Pre-trained model priors (assumed build steps, package managers, framework conventions, or implicit directory roles) may never be superimposed (*Adhyāsa*) onto the repository. Every architectural or operational convention relied upon must trace to an explicit `[CONTRACT]` or `[OBSERVED]` source in the repository.
- **Rationale:** A fresh context window (*Śūnya*) clears chat history, not model weights; unexamined training defaults corrupt bespoke repository architectures on entry (P12-01, P12-02).
- **Enforcement:** Mandated by Stage 1 (*Śravaṇa*) of the Session Ritual in `AGENTS.md`.

