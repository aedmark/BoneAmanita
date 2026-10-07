# Documentation Map

This directory stores durable project knowledge for BoneAmanita. Each fact has one authoritative home;
other documents link to it instead of duplicating it.

## Audiences and ownership

| Document | Primary audience | Owns | Does not own |
| --- | --- | --- | --- |
| `../README.md` | Users and newcomers | Purpose, quickstart, public entry points | Internal workflow or session history |
| `../AGENTS.md` | Coding agents and maintainers | Standing working rules and repository conventions | Feature history or design rationale |
| `../ROADMAP.md` | Maintainers and contributors | Phased planned scope and permanent item status | Detailed implementation notes |
| `HANDOFF.md` | The next work session | Bounded current state, active context, next steps | Permanent architectural rules |
| `ARCHITECTURE.md` | Developers and agents | System shape, interfaces, invariants, data flow | Chronological session history |
| `DECISIONS.md` | Future decision-makers | Rationale and alternatives for durable choices (D-NNN) | Routine implementation detail |
| `TESTING.md` | Contributors and test runners | Verification commands, test suites, and blind evaluation | Full current test output |
| `SECURITY.md` | Users and developers | Sensitive assets, secret withholding, substrate sandbox | Operational incident history |
| `CONTRIBUTING.md` | Human and agent contributors | Setup, change, review, and submission workflow | Agent-only rules |
| `CHANGELOG.md` | Users and operators | User-visible changes and release history | Developer-facing commit logs |
| `manual/index.html` | Operators and architects | Standalone What/How/Why System Manual (3x scheme) | Transient session context |
| `manual/reference.html` | Operators and developers | Standalone What/How/Why Reference Manual (3x scheme) | Internal decision logs |
| `archive/` | Historians and maintainers | Historical session logs, older tracks, and test notes | Normative current rules |

## Update triggers

Update documents because a relevant fact changed, not merely because a session ended.

| Change | Required documentation |
| --- | --- |
| User-visible behaviour or CLI command | `../README.md` if onboarding changed; `CHANGELOG.md` |
| Component, interface, dependency, or data flow | `ARCHITECTURE.md` |
| Durable tradeoff, architecture rule, or reversal | `DECISIONS.md`; mark old decisions superseded |
| Test command, coverage boundary, or audit harness | `TESTING.md` |
| Secret redaction, trust boundary, or sandboxing | `SECURITY.md` |
| Work pauses with context another session needs | `HANDOFF.md` |
| Contribution or agent workflow change | `CONTRIBUTING.md` and `../AGENTS.md` |
| New planned work | `../ROADMAP.md`, with permanent item ID |
| 3x manual content or schema | `manual/system.manual.json` and `manual/reference.manual.json` |

## Style and evidence

- Lead with the reader's task or current truth.
- Use exact commands and repository-relative paths.
- Date volatile observations and identify the environment or commit when it affects reproducibility.
- Link to the canonical source of truth instead of copying prose.
- Keep secrets, personal data, and raw private tokens out of documentation and fixtures.
