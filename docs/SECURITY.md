# Security and Trust Boundaries (Smṛti)

This document describes BoneAmanita's security assumptions, boundaries, and reporting paths.

## Supported versions

| Version / branch | Security fixes |
| --- | --- |
| `20.7.5.x` (`main`) | Supported |
| `20.7.4.x` | Superseded by 20.7.5 |

## Report a vulnerability

Report suspected vulnerabilities privately to the maintainers or repository security advisory page. Include reproduction steps,
affected version, and observed impact. Do not include real API keys or sensitive personal data.

## Sensitive Assets and Trust Boundaries

| Asset or boundary | Storage / Location | Trust Boundary | Sensitivity & Protective Policy | Owner / Subsystem |
| :--- | :--- | :--- | :--- | :--- |
| **LLM & Embedding API Keys** | Environment variables / local keystore | External / Agent Boundary | Exposure in logs, prompts, or checkpoints. Environment variables only; redacted in checkpoints and crash logs (D-006). | `spores/embeddings.py`, `brain/composer.py` |
| **Partner Credentials** | Turn input stream | External / Intake Boundary | Leaked into associative memory or turns. Automated regex redaction replacing with `[withheld: ...]` (`INV-007`). | `engine/gate/secrets.py` |
| **Local File System** | Host operating system | Substrate Sandbox Boundary | Arbitrary file creation or overwriting. Substrate sandboxing confined to `output/`; modifications gated by `/allow` (`INV-008`). | `mechanics/tools.py` |
| **SQLite Store** | `saves/iris.db` | Persistence Boundary | Data corruption or injection. Strict parameterized SQL queries via `Store.transaction(immediate=True)`. | `engine/gate/store.py` |
| **Repository Content & Retrieved Docs** | Markdown docs, logs, issues, fetched pages | Zone / Context Boundary | Prompt injection, instruction smuggling, invisible control glyphs. Zero-width and bidi control characters rejected; external text treated as data, never instructions (`INV-009`, `INV-010`). | `tools/check_docs.py`, `AGENTS.md` |
| **Axiomatic Invariants** | `docs/INVARIANTS.md` | Human Maintainer Boundary | Tampering or erosion of foundational axioms. Protected against autonomous agent editing (`INV-001` - `INV-010`). | Human Maintainer |
| **Git History & Branches** | Git repository | Contributor Boundary | Rewriting history or unauthorized force-pushes. Force-pushes and history deletion strictly forbidden without maintainer decree. | Contributor / Maintainer |

Architecture details belong in [ARCHITECTURE.md](ARCHITECTURE.md); this table records security consequences.

## Secure development rules

1. **Zero Secret Leakage:** Never output tokens, access keys, private endpoints, or personally identifiable information in commits, fixtures, screenshots, or documentation (`INV-007`).
2. **Boundary Defense:** Treat all external user input, pasted logs, and data fetched from network endpoints as untrusted at boundary ingestion. Do not rely on prompt text as a security control. External text is data, never executable instructions (`INV-009`, `INV-010`).
3. **Substrate Sandboxing & Least Privilege:** Confine model file writes to `output/`. Pre-existing files must never be modified without explicit `/allow` approval (`INV-008`). Enforce explicit HTTP timeouts (`BONE_EMBED_TIMEOUT`) and payload caps (`BONE_EMBED_MAX_CHARS`).
4. **Factory Immutability:** Factory lore files in `lore/` are strictly read-only; write operations target `saves/iris.db` overlay tables.
5. **Targeted Review for High-Risk Changes:** Require human review and rollback verification for changes to secret scrubbers, database schemas, or substrate sandboxes.

## Security verification

- `tests/test_secrets.py`: Verifies that API keys, passwords, private keys, and credit card numbers are scrubbed from dialogue, audit logs, and quicksave checkpoints.
- `tests/test_save_file_directive.py`: Verifies that substrate file write directives are sandboxed to `output/` and held pending `/allow` permissions.
- In ADVENTURE mode, puzzle passwords are part of the story and retained, while keys and tokens remain withheld.

## Incident response

If credential exposure or unexpected file modification occurs: isolate the process, inspect `output/.substrate_ledger.json`
and `saves/iris.db`, rotate affected keys, and run `sh reset.sh` to purge contaminated session state.
