# Contributing

Workflow for human and automated contributors to BoneAmanita. Agent-specific standing instructions are in
[../AGENTS.md](../AGENTS.md).

## Before changing code

1. Read `../README.md`, relevant roadmap items in `../ROADMAP.md`, and [ARCHITECTURE.md](ARCHITECTURE.md).
2. Follow the local setup using Python 3.14:
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
3. Check `git status` and confirm that your change will not overwrite work from other sessions.
4. For architectural or structural changes, review existing choices in [DECISIONS.md](DECISIONS.md).

## Make the change

- Keep each change reviewable, well-scoped, and focused on one outcome.
- Preserve biological variable names (`atp_pool`, `cortisol`, `godel_scars`); do not rename domain metaphors (D-003).
- Respect the anti-performance contract: never prompt the model to perform or narrate physical fatigue (D-001).
- Add or update tests for changed behaviour. Make tests fail for the intended reason before trusting them.
- Update documentation according to [update triggers](README.md#update-triggers).
- Do not commit secrets, personal data, or local `config.json` files.

## Verify

```bash
# Fast verification:
.venv/bin/pytest tests/test_command_routing.py tests/test_manuals.py
python3 tools/check_docs.py

# Full test suite:
.venv/bin/pytest

# Manual set re-build:
python3 tools/build_manual.py build
```

Follow [TESTING.md](TESTING.md) for test prerequisites and offline execution rules.

## Submit and review

- Work happens directly on `main` or on scoped feature branches (`feature/<topic>`).
- Commit messages must be structured as informative changelog entries explaining what changed, in which files, and why (D-012).
- Agents draft commits upon request but never commit without explicit approval from Gordon.
- A change is ready when the fast test suite passes, documentation checks pass with 0 errors, and no extraneous files are staged.

## Compatibility and migrations

- Persistent state is consolidated in SQLite (`saves/iris.db`).
- SQLite migrations must preserve existing columns and table structures.
- Factory files in `lore/` are strictly read-only; user overrides go into database overlay tables.

## Reporting security issues

Do not open public issues for security vulnerabilities or secret leaks. Follow [SECURITY.md](SECURITY.md).
