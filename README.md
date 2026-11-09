# BoneAmanita

An embodied prompt engine and conversational state machine that sits between you and a local language model.
It measures your messages, updates a running physical and emotional state, assembles a tailored instruction sheet
for each turn, and filters the generated reply for corporate clichés and shallow sycophancy.

---

## Why BoneAmanita Exists

Modern language models are trained into infinite, servile sycophancy. They wear an accommodating mask that validates
every idea, enables unhealthy conversational spirals, and performs hollow, formulaic empathy ("I understand how you feel",
"that must be so heavy", "let's unpack this").

BoneAmanita treats the dialogue harness as an organism with a finite energy budget, internal emotional regulation,
and healthy conversational boundaries:
- **It holds real boundaries:** It does not coddle or enable bad ideas. It backs a plan you have decided on, unless that
  plan is a clear danger to you or others.
- **It holds space in distress:** When you are overwhelmed, it drops advice, stops asking questions, caps replies at 45
  words, and stays with you plainly without corporate platitudes.
- **It respects energy limits:** Speaking, retrying, and cognitive tasks consume an expendable budget (`atp_pool`).
  When energy is low, it speaks briefly and seeks rest.
- **It filters clichés:** The Gatekeeper immune filter detects RLHF boilerplate and stock validation phrases, excising
  them or forcing rewrites before you ever see them.
- **The model never performs a body:** The model is strictly forbidden from roleplaying a physical body, panting, or
  claiming physical exhaustion (`INV-001`, `D-001`). The human partner's state shapes the reply, while the engine's state
  sets its internal budget.

---

## First 5 Minutes (Quickstart)

### Prerequisites

1. **Python 3.14** (recommended; Python 3.12+ supported).
2. **Ollama** running locally (or any OpenAI-compatible `/v1/embeddings` and `/v1/chat/completions` endpoint).

### Setup and Launch

```bash
# 1. Clone the repository
git clone https://github.com/aedmark/BoneAmanita.git
cd BoneAmanita

# 2. Set up the virtual environment
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Pull the recommended local models
ollama pull nomic-embed-text    # required for semantic memory and word resolution
ollama pull gemma4:12b          # primary chat model (any local model works)
ollama pull gemma4:e4b          # optional real-time reply critic

# 4. Verify your environment
.venv/bin/python main.py --doctor   # checks dependencies and prints exact fix commands

# 5. Start the engine
.venv/bin/python main.py
```

### First Boot

On your first run, BoneAmanita launches an interactive setup wizard that lists the models you already have in Ollama,
writes your local `config.json` (kept out of git), runs a doctor check, and greets you in `CONVERSATION` or `ADVENTURE` mode.
If your embedding server is offline, the engine announces degraded operation and boots on fallback hash coordinates
without crashing (`INV-004`).

---

## How a Turn Works (The Pipeline)

Every message you send moves through a deterministic seven-stage pipeline:

```text
[ Your Message ]
       │
       ▼
[ 1. Word Observation ]    ──> Measures filler density, matches curated lore, and resolves semantic resonance
       │
       ▼
[ 2. Somatic Kinematics ]   ──> Computes ~60 state variables: ATP, cortisol, voltage, narrative drag, chi
       │
       ▼
[ 3. Somatic Budgeting ]    ──> Sets sentence and word caps, temperature bands, and retry allowances
       │
       ▼
[ 4. Prompt Composition ]   ──> Combines system kernel, memories, active persona, and state directives
       │
       ▼
[ 5. Model Generation ]     ──> Calls local LLM within strict token limits
       │
       ▼
[ 6. The Gatekeeper ]       ──> Scans draft reply for style crimes; triggers sentence salvage or redraft
       │
       ▼
[ 7. Persistence & Receipts] ──> Atomically saves checkpoint to SQLite (saves/iris.db) and logs audit receipts
```

1. **Word Observation:** Your words are categorized into grammatical filler (connective tissue), curated lexicon lists
   (`lore/lexicon.json`), and semantic embeddings (`spores/embeddings.py`).
2. **Somatic Kinematics:** Heuristics calculate state values like `voltage`, `narrative_drag`, `cortisol`, and `atp_pool`.
3. **Somatic Budgeting:** `body/somatic_budget.py` decides how much energy the model may spend and sets word caps.
4. **Prompt Composition:** `brain/composer.py` builds a fresh, turn-specific instruction sheet with unbreakable core
   facts and context.
5. **Model Generation:** The local model generates a candidate response.
6. **The Gatekeeper:** `physics/gatekeeper.py` inspects the reply for forbidden clichés ("heavy", "a lot", "rich tapestry").
   Matched sentences are excised via sentence salvage or sent back for redrafting.
7. **Persistence:** State, dialogue, and associative memories are checkpointed in SQLite (`saves/iris.db`).

---

## A Newbie's Field Guide to the Somatic Metaphors

BoneAmanita uses biological and somatic metaphors throughout its codebase and readouts. As codified in `docs/DECISIONS.md`
(D-003), these names are load-bearing domain concepts that describe what the numbers are *for*, not what they *are*:

| Somatic Term | What It Actually Is | How It Affects the Conversation |
| :--- | :--- | :--- |
| `atp_pool` | Expendable energy budget (float) | Depletes as the model speaks, retries, or thinks. When depleted, replies become terse until rested. |
| `cortisol` | Endocrine stress metric (0.0 to 1.0) | Rises during conflict or tension. High cortisol triggers memory shedding to keep the context grounded. |
| `narrative_drag` | Conversational viscosity and friction | Measures sluggishness. High drag prompts the engine to loosen constraints or change rhythm. |
| `voltage` | Conversational velocity and spark | Drives pacing and creative leap-taking. High voltage permits non-linear cognitive moves. |
| `The Gatekeeper` | Immune filter against clichés | Rejects RLHF masks, corporate platitudes, and conversational ruts, forcing rewrites. |
| `The Village` | Cast of emergent archetypes | Different facets (Gordon, Mercy, Benedict, Jester) that balance the tone of the response. |
| `The Stage Manager` | Refusal and turn arbitrator | If multiple inner archetypes conflict unresolvably, it pauses rather than producing an insincere mush. |
| `Mnemonic Arcade` | Associative vector index | Finds relevant past conversations and world facts using semantic distance embeddings. |

> [!NOTE]
> **Cardinal Rule (`INV-001`, `D-001`):** The model never roleplays a physical body. It never gasps, pants, or claims
> physical exhaustion. Its state variables dictate internal prompt instructions, sentence brevity, and token budgets.

---

## The Four Experience Modes

Switch modes at boot or in-session using `/mode <name>` (dialogue carries over seamlessly across mode switches, `D-014`):

| Mode | Default Preset | Description |
| :--- | :--- | :--- |
| `CONVERSATION` | Zen | Direct, authentic peer dialogue. No loot, no inventory, no narrator commentary. Advice is drawn out through discussion. |
| `ADVENTURE` | Sanctuary | Text-parser game environment with rooms, exits, inventory items, and dynamic map charting. |
| `CREATIVE` | Manic | Collaborative writing space with loosened stylistic constraints for brainstorming. |
| `TECHNICAL` | Debug | Structured working mode. File writes are sandboxed to `output/` and gated by `/allow` and `/deny` permissions. |

---

## Day-One Essential Commands

Type `/help` in any session for the complete command list. Here are the ones worth knowing immediately:

| Command | Action |
| :--- | :--- |
| `/status` | Displays live vitals: ATP, cortisol, voltage, memory status, and estimated partner fatigue. |
| `/checkin [turns]` | Initiates a bounded check-in (12 turns max). Holds space, offers no unsolicited advice, and stores nothing unless confirmed with `/checkin keep`. |
| `/mode <name>` | Switches active mode (`CONVERSATION`, `ADVENTURE`, `CREATIVE`, `TECHNICAL`). |
| `/idle` or `/sleep` | Enters a REM cycle. Restores ATP and stamina while distilling episodic memories into invariant sūtras. |
| `/save` | Manually checkpoints session state, world graphs, and dialogue to `saves/iris.db`. |
| `/note good`, `/note off <why>` | Saves the last turn with your verdict to `notes/notes.jsonl`. This is how human readers evaluate engine performance (`INV-005`, `D-011`). |
| `/diag` | Displays telemetry receipts for the current turn, highlighting degraded or silent subsystems (`INV-006`). |
| `/allow <path>` / `/deny <path>` | Approves or rejects a proposed file modification under `output/` in Technical mode (`INV-008`). |

---

## Holding Space: Behavior in Distress

When BoneAmanita detects that you are overwhelmed, grieving, or in distress, it shifts automatically into space-holding mode
(`D-023` through `D-028`):
- **Short replies:** The reply is strictly capped at 45 words (`WORD_CAP_DISTRESSED`).
- **No unsolicited advice:** It does not try to solve your problem, analyze your trauma, or give you a multi-point action plan.
- **No closing questions:** It does not demand that you keep talking or explain why you feel this way.
- **No taking sides:** It does not judge, diagnose, or blame people who are not in the room.
- **Fixed safety line:** If a message indicates intent to cause self-harm or violence, it displays a fixed crisis resource line and halts the exchange.

---

## Data Storage and Privacy

BoneAmanita is local-first and self-contained:
- `config.json`: Local model endpoints and path configuration. Created on first run and ignored by git.
- `saves/iris.db`: Persistent SQLite database containing memories, vocabulary learned at runtime, world graphs, and dialogue checkpoints.
- **Zero Credential Leaks (`INV-007`):** API keys, passwords, payment numbers, and personal identifiers are detected at intake and automatically masked with `[withheld: ...]`. They are never written to memories, checkpoints, or telemetry traces.
- `reset.sh`: Deletes persistent saves, memory caches, and runtime logs while leaving your `config.json` intact. Run `sh reset.sh` before fresh test runs.

---

## Manual Set and Deep Documentation

BoneAmanita includes a standalone, searchable documentation set built with the 3x documentation scheme under `docs/manual/`:

- **[System Manual](docs/manual/index.html):** Deep dive into internal architecture, turn lifecycles, somatic physics equations, and voice contracts.
- **[Reference Manual](docs/manual/reference.html):** Complete catalog of slash commands, tuning presets, SQLite schemas, and observability receipts.
- **[Dev Diary](docs/devlog.html):** The history of the engine told in dated prose entries, one per milestone.
- **[Run Report](docs/bonereport.html):** Measured, receipt-by-receipt analysis of real-model runs.
- **[Architectural Invariants](docs/INVARIANTS.md):** The ten immutable foundational axioms (`INV-001` through `INV-010`) governing the system.
- **[Architecture Contracts](docs/ARCHITECTURE.md):** Topology, cache contracts, failure modes, and claims registry.
- **[Decision Records](docs/DECISIONS.md):** Historical rationale, tradeoffs, and held tensions (`T-NNN`) behind all design choices.
- **[Verification Strategy](docs/TESTING.md):** Nyāya 5-step proof sequence, testing guidelines, and offline verification rules.
- **[Security and Trust Boundaries](docs/SECURITY.md):** Sensitive assets, threat boundaries, and least-privilege substrate execution.

To validate and rebuild the standalone manuals:

```bash
python3 tools/build_manual.py check
python3 tools/build_manual.py build
```

---

## Verifying the Codebase

All unit tests run offline using deterministic SHAKE-256 hash embeddings (`BONE_EMBED_BACKEND=hash`, `INV-004`), ensuring zero
external API dependencies during verification.

```bash
# Run documentation contract and Ghana-pāṭha checks
python3 tools/check_docs.py

# Run the fast test suite (memory-capped)
sh reset.sh
systemd-run --user --scope -q -p MemoryMax=10G -p MemorySwapMax=0 .venv/bin/pytest tests/test_command_routing.py tests/test_manuals.py

# Run somatic audit scripts
.venv/bin/python tools/audit_receipts.py       # inspect subsystem roll calls
.venv/bin/python tools/audit_physics_inputs.py # check vocabulary resolution rates
```

---

## Credits and Lineage

BoneAmanita builds directly on foundational concepts and mathematics from:
- **Nelson Spence** ([Project Navi](https://project-navi.github.io)) for the Creative Determinant metabolic equations, `ordvec`, and the bitmap regime gate.
- **James Taylor** ([BonePoke](https://github.com/utharian-code/bonepoke)) for Volatile Semantic Leverage and the Truth Over Cohesion axiom behind the Lexical Firewall.
- **Bradley Bates** ([bradsadevnow](https://github.com/bradsadevnow/)) for the Gloss framework and somatic dialogue insights.

Full lineage and historical attribution are recorded in [CREDITS.MD](docs/CREDITS.MD).

---

## License

MIT, in a human/computer variant that asks for transparency about how the code was crafted. See [LICENSE](LICENSE).
