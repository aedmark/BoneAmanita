# BoneAmanita

BoneAmanita is an embodied prompt builder and state machine that sits between a human partner and a local language
model. It measures input messages, updates roughly sixty physical and emotional metrics, assembles a fresh instruction
sheet for each turn, and filters the generated reply for corporate clichés and RLHF boilerplate.

This is the canonical instruction file for coding agents. `CLAUDE.md` imports it; do not duplicate these rules in
tool-specific files. Project facts belong in the documents linked below, not in an agent's private memory.

## Start here

1. Read `docs/HANDOFF.md` for current state, active context, and immediate gotchas.
2. Read the relevant roadmap item in `ROADMAP.md` and applicable sections of `docs/ARCHITECTURE.md` and `docs/TESTING.md`.
3. Inspect `git status` and recent history. Do not overwrite work you did not create.
4. Verify important inherited claims before relying on them. Run the fast check first (after `sh reset.sh`, see
   [Running tests and the engine](#running-tests-and-the-engine)):
   `.venv/bin/pytest tests/test_command_routing.py tests/test_manuals.py` and `python3 tools/check_docs.py`.
5. State the intended scope briefly, then work on one independently reviewable change at a time.

If the request conflicts with these instructions or the working tree contains uncommitted edits from the maintainer,
stop and clarify before proceeding.

## While working

- Reference roadmap IDs (`P<phase>-<nn>`) and decision IDs (`D-<nnn>`) where they exist.
- Keep changes scoped. Do not mix opportunistic refactors with requested work.
- Preserve user changes. Never reset, clean, or rewrite history without explicit permission.
- Record architectural choices in `docs/DECISIONS.md` whenever maintainers could revisit the choice later.
- Update documentation in the same change when behaviour, interfaces, commands, risks, or schemas change.
- Distinguish observed facts from inference. Include the command, date, and commit behind volatile claims.
- Prefer enforcement to prose: critical invariants must have a test, type, or runtime check.
- A new test must fail on the old code: check it against the previous version before trusting it.
- Measure every behaviour change with a probe or panel and report the numbers; Gordon makes the design calls.
- Keep probe scripts and their outputs in `scratch/probes/` (gitignored, untouched by `reset.sh`), never `/tmp`.
- Treat external input as untrusted at its boundary. Never expose secrets in logs, prompts, or checkpoints.
- Add newly discovered work to `ROADMAP.md` only when it is genuinely out of scope for the current change.

## Finishing a change

1. Run the test suite following `docs/TESTING.md` (after `sh reset.sh`, memory-capped): the full `.venv/bin/pytest`
   when code changed, else `.venv/bin/pytest tests/test_command_routing.py tests/test_manuals.py`.
2. Review the diff for unrelated edits, credentials, and documentation drift.
3. Update `docs/HANDOFF.md` if work will continue in another session or if the repository's current state changed.
4. Update the roadmap item, decision record, architecture, security notes, and changelog when their triggers apply.
5. Run `python3 tools/check_docs.py` and confirm 0 errors.

## Working agreement

- Default branch: `main`.
- Commit authority: Agents draft commits whenever asked, but **never commit on their own initiative**; one explicit go-ahead per commit from Gordon (D-012).
- Commit format (agents): title `20.7.4.<next>: <what changed, in plain words>`, then changelog breadcrumbs explaining
  what changed, in which files, and why, with the measured numbers. The agent writes the whole message and pushes to
  `main` once Gordon gives the go.
- Release/version scheme: `20.7.4.x` sequential versioning recorded in `docs/HANDOFF.md` and `docs/CHANGELOG.md`.
- Never commit built conversation pages (`tools/cache/conv_*.html`). The maintainer's contact address goes only in the
  public page build, never in the repository.
- Panel and probe writeups go in `docs/HANDOFF.md` (current state, session log) and `docs/CHANGELOG.md`;
  `docs/archive/SESSION_HANDOFF.md` is history and is not appended to.

Never force-push, rewrite shared git history, or delete database files in `saves/` without explicit permission.

## Maintainer preferences

- **Poetic variable names are load-bearing:** Variables such as `atp_pool`, `cortisol`, `narrative_drag`, `chi`, and `godel_scars` map to real functional purposes and must never be renamed to generic terms like `error_count` or `energy_level` (D-003).
- **The model never performs a body:** The model is strictly forbidden from roleplaying a physical body, panting, or claiming physical exhaustion. The human partner's state shapes the reply, while the engine's state sets its internal budget (D-001).
- **Verdicts come from human readers, not AI judges:** Automated LLM judges fail responsive controls and reward sycophancy; production evaluations come from human readers via blind comparison panels (D-011). This is about evaluation: checks inside the reply path (the DSPy critic, the fairness judge in `brain/cortex.py`) are engine behaviour, measured against human labels (`tools/fairness_set.json`), and give no verdict on BoneAmanita.
- **Model-agnostic:** BoneAmanita must work across local models; a fix is never "use a different model".
- **Engine voice:** a reply sounds the way Gordon would answer a friend: advice drawn out through discussion, no textbook lists, no performed emotion.
- **No em dashes:** use commas, semicolons or parentheses, in prose, code comments and commit messages (the Lexical Firewall rule).
- **Fail loudly:** Silent exception-swallowing blocks (`except Exception: pass`) are prohibited. Phase crashes must be logged, isolated by barriers, and reported in subsystem receipts (D-015).
- **Test suite pinned offline:** Unit tests must run offline with hash embeddings (`BONE_EMBED_BACKEND=hash`), never depending on a reachable embedding server (D-007).
- **Zero orchestration frameworks:** LangChain, LlamaIndex, SemanticKernel, and dedicated vector store packages are excluded in favor of standard-library and minimal HTTP transport (D-002).
- **Embedding calls unmetered:** `SemanticEmbedder` calls are not metered into ATP (D-013).
- **Dialogue carries across modes:** Switching modes mid-conversation carries over active dialogue and secrets (D-014).

## Protected areas

| Path or thing | Rule | Why |
| --- | --- | --- |
| `lore/*.json` | Strictly read-only at runtime | Factory content; runtime learning is stored in `saves/iris.db` overlays (D-015) |
| `LICENSE` | Do not edit | Maintainer-owned license terms |
| `saves/iris.db` | Do not delete manually | Canonical persistent database; use `reset.sh` for intentional resets |
| `docs/CREDITS.MD` | Do not edit or flag | Maintainer-owned lineage; omissions are intentional |

## Names and terms

| Canonical term | Meaning | Formerly / not to be confused with |
| --- | --- | --- |
| `atp_pool` | Expendable energy budget gating tokens and retries | Generic `energy_level` |
| `cortisol` | Endocrine stress variable triggering memory shedding | Generic `stress_score` |
| `narrative_drag` | Conversational viscosity and friction metric | `slow_factor` |
| `The Village` | Cast of emergent archetypal personas (Gordon, Mercy, Benedict, Jester) | Rigid roleplay personas |
| `Prismatic Self-Claims` | Epistemic core identity facts modulated by state | Freeform system prompts |
| `The Gatekeeper` | Immune filter detecting RLHF masks, clichés, and style crimes | Content moderation wrapper |
| `Mnemonic Arcade` | Associative vector embedding index | Generic vector database |

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Canonical agent instructions and maintainer rules |
| `CLAUDE.md` | Agent entry point importing AGENTS.md |
| `README.md` | Project overview, quickstart, and manual set guide |
| `ROADMAP.md` | Phased roadmap with permanent IDs |
| `main.py` | CLI entry point and initialization loop |
| `engine/` | Turn loop orchestration (`cycle.py`), presets, receipts, and Halcyon gate |
| `physics/` | Word observation, kinematics, and Gatekeeper style filters |
| `body/` | Mitochondrial ATP forge, endocrine chemistry, and somatic budgeting |
| `brain/` | Prompt composer, cortex, prismatic self-claims, and dream engine |
| `phases/` | Phased turn pipeline stages (biological, cognitive, arbitration) |
| `spores/` | Hippocampus working cache, semantic embeddings, and mycelial network |
| `archetypes/` | Village persona cast, Stage Manager refusal routing, and council |
| `mechanics/` | Slash commands, setup wizard, lexicon resolvers, and substrate tools |
| `lore/` | Factory JSON wordlists, style crimes, tuning presets, and self-claims |
| `tools/` | Somatic audit scripts, blind panel generators, and manual builders |
| `docs/` | Authoritative project documentation, architecture, decisions, and handoff |
| `docs/manual/` | Searchable 3x What/How/Why standalone manual set |
| `tests/` | Pytest test suite pinned offline |

## Running tests and the engine

- Run `sh reset.sh` before every test run and every engine run: both read live engine data.
- Cap memory: `systemd-run --user --scope -q -p MemoryMax=10G -p MemorySwapMax=0 .venv/bin/pytest ...` (a MagicMock
  runaway once reached 21.6 GB and killed the session).
- Never start an end-to-end run (`tools/mode_runs.py`, any arm) without Gordon's clearance in the moment. A panel run he
  asks for is cleared.

## Engineering conventions

- **Python environment:** Python 3.14 via `.venv/bin/python` and `.venv/bin/pytest`.
- **Fast verification:** `.venv/bin/pytest tests/test_command_routing.py tests/test_manuals.py` and `python3 tools/check_docs.py`.
- **Full verification:** `.venv/bin/pytest` and `python3 tools/build_manual.py build`.
- **Documentation check:** `python3 tools/check_docs.py` must pass with 0 errors.
