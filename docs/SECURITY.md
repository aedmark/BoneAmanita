# Security

This document describes BoneAmanita's security assumptions, boundaries, and reporting paths.

## Supported versions

| Version / branch | Security fixes |
| --- | --- |
| `20.7.4.x` (`main`) | Supported |

## Report a vulnerability

Report suspected vulnerabilities privately to the maintainers or repository security advisory page. Include reproduction steps,
affected version, and observed impact. Do not include real API keys or sensitive personal data.

## Assets and boundaries

| Asset or boundary | Sensitivity / threat | Protection and validation | Owner |
| --- | --- | --- | --- |
| LLM & Embedding API Keys | Exposure in logs, prompts, or checkpoints | Environment variables; redacted in checkpoints and crash logs (D-006) | `spores/embeddings.py`, `brain/composer.py` |
| Partner Credentials | Leaked into associative memory or turns | Automated regex redaction in `engine/gate/secrets.py` replacing with `[withheld: ...]` | `engine/gate/secrets.py` |
| Local File System | Arbitrary file creation or overwriting | Substrate sandboxing in `output/`; modifications gated by `/allow` and `/deny` | `mechanics/tools.py` |
| SQLite Store (`saves/iris.db`) | Data corruption or injection | Strict parameterized SQL queries via `Store.transaction(immediate=True)` | `engine/gate/store.py` |

Architecture details belong in [ARCHITECTURE.md](ARCHITECTURE.md); this table records security consequences.

## Secure development rules

- Keep API keys and credentials out of version control, prompts, logs, and committed fixtures.
- Redact matched secrets automatically before writing checkpoints, audit traces, or spores (`engine/gate/secrets.py`).
- Confine model file writes to `output/`. Pre-existing files must never be modified without explicit `/allow` approval from the user.
- Use explicit timeouts (`BONE_EMBED_TIMEOUT`) and payload limits (`BONE_EMBED_MAX_CHARS`) on all external HTTP requests.
- Factory lore files in `lore/` are strictly read-only; write operations target `saves/iris.db` tables.

## Security verification

- `tests/test_secrets.py`: Verifies that API keys, passwords, private keys, and credit card numbers are scrubbed from dialogue, audit logs, and quicksave checkpoints.
- `tests/test_save_file_directive.py`: Verifies that substrate file write directives are sandboxed to `output/` and held pending `/allow` permissions.
- In ADVENTURE mode, puzzle passwords are part of the story and retained, while keys and tokens remain withheld.

## Incident response

If credential exposure or unexpected file modification occurs: isolate the process, inspect `output/.substrate_ledger.json`
and `saves/iris.db`, rotate affected keys, and run `sh reset.sh` to purge contaminated session state.
