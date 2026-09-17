# BoneAmanita

A state machine that sits between you and a local language model and rewrites
the model's instructions on every turn, based on a physical and emotional state
that persists between sessions.

It is a prompt builder. A large and unusual one, with real mathematics in the
middle of it, but the effects it produces are produced by instructions to a
model rather than by the simulation its naming implies. That distinction is
worth holding onto while reading everything below.

## The one paragraph version

BoneAmanita measures your message, keeps a running state, and uses that state to
assemble a fresh instruction sheet for the model each time you speak. Then it
filters the reply for clichés and makes the model try again if it finds any.

That is the whole machine. Everything else is detail about how the state is
measured and which sentences it produces.

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
ollama pull nomic-embed-text    # memory and word resolution need this
ollama pull mistral-nemo        # or whatever chat model you prefer
.venv/bin/python main.py
```

First run asks some setup questions and writes `config.json`. If the embedding
backend is unreachable the engine still boots and tells you that associative
recall is disabled, rather than pretending otherwise. Word resolution degrades
too but keeps working: grammatical filler and the curated lists need no server
at all.

### Requirements

- **Python 3.10 or newer.** The code uses `match` statements; it is developed on
  3.14.
- **An OpenAI-compatible `/v1/embeddings` endpoint** for the memory's coordinate
  system. Ollama, LM Studio, llama.cpp and OpenAI all serve one. Point at a
  different one with `BONE_EMBED_URL` and `BONE_EMBED_MODEL`.
- **A chat model**, local by default via Ollama.
- Everything else is in `requirements.txt`. Two entries there are load bearing
  in a way worth knowing: `ordvec` (Project Navi) backs both the subconscious
  memory search and the Creative Determinant's subgraph selection, and the
  engine announces at boot if it is missing rather than quietly doing without.
  `sentence-transformers` is commented out; uncomment it for a fully offline
  embedder with no server at all.

### Files it writes

`config.json` is generated on first run and is not in the repo.
`saves/cortex_hive.json` holds every word the engine has taught itself;
deleting it is the clean way to make it forget without touching your curated
lists. `reset.sh` clears all generated state.

## Using it

### Modes

Set at boot, or switched in-session with `/mode`. Each selects a different
tuning preset, and only Adventure has an inventory and a world to move through.

| Mode | Tuning | For |
|---|---|---|
| `ADVENTURE` | Sanctuary | The default. Parser-game framing, items, zones. |
| `CONVERSATION` | Zen | Talking. No loot, no world model. |
| `CREATIVE` | Manic | Writing. Loosest constraints. |
| `TECHNICAL` | Debug | Working on something. Tightest constraints. |

### Commands

`/help` lists them in-session. The ones worth knowing first:

| Command | What it does |
|---|---|
| `/status` | Vitals: health, stamina, energy, the memory backend, and what it believes about you. |
| `/diag` | This turn's receipts, plus anything silent or degraded. See below. |
| `/save` | Persist state to disk. |
| `/mode <name>` | Switch operational mode. |
| `/idle`, `/sleep` | Enter a REM cycle, regenerating ATP and stamina. Dreams happen here. |
| `/rest`, `/zen`, `/flush` | The hard reset. Severs context, drops drag to zero, restores stamina and ATP, purges trauma. |
| `/truth <0-3>` | Adjust reality ambiguity. |
| `/hud <depth>` | Set readout depth: `warm`, `lite`, `core` or `deep`. |
| `/reload` | Hot-reload `lore/*.json` without restarting. |
| `/look`, `/use`, `/inventory`, `/map` | Adventure mode only: the world and what you carry. |

## How a turn works

1. **Your words get sorted into categories.** Four stages, most trustworthy
   first:
   - **Grammatical filler** (`the, a, is, at, and`). About 40% of normal speech.
     These are not unclassified, they are connective tissue, and the engine
     measures their density as its own signal.
   - **The curated word lists** in `lore/lexicon.json`: heavy words, kinetic
     words, abstract words, void words, corporate cliché words, and thirty odd
     other categories. Inflections resolve to their root, so `forge` answers for
     `forging` and `forged`.
   - **Semantic resonance.** A word the lists do not know is compared against an
     average of each category's meaning, using the same embedding model the
     memory uses. If it clearly belongs somewhere, the engine files it and
     remembers it. If it is genuinely between two categories, it stays unfiled.
   - **A last-resort guess from spelling**, which fires on about 3% of words.

   Roughly 81% of ordinary English resolves without guessing. The rest stays
   unresolved on purpose. Nobody knows all of English, and an engine that
   pretends to is the failure mode this whole layer was rebuilt to escape.

2. **Those counts become numbers.** Formulas in `physics/` turn the counts into
   roughly sixty values with names like `voltage`, `narrative_drag`, `cortisol`,
   `atp_pool` and `chi`. These are hand tuned heuristics wearing physics names.
   They are not real physics, and they do not need to be; they work as a way of
   tracking the shape of a conversation.

3. **Thresholds pick sentences.** If contradiction is high, a sentence about
   holding paradox goes into the instruction sheet. If energy is low, an
   instruction to write shorter sentences goes in. This assembly happens in
   `brain/composer.py`, and the result is about 900 tokens.

4. **One request goes out.** A single HTTP call to whatever model you have
   configured. The model sees only the assembled instructions plus your message.

5. **The reply gets inspected.** A filter checks for banned phrases ("I
   understand how you feel", "rich tapestry", and a long list in
   `lore/style_crimes.json`). On a hit, the reply is discarded and the model is
   asked again.

6. **State is written to disk.** Energy spent, stress accumulated, scars earned.
   This is why the next session does not start fresh.

## Where things live

| Directory | What is in it |
|---|---|
| `physics/` | The formulas. Word counts in, state numbers out. Also the Creative Determinant math. |
| `body/` | Energy, stress chemistry, the regulator that keeps them in range. |
| `brain/` | The prompt assembler, the reply filter, the memory index, the dream engine. |
| `phases/` | The ordered steps each turn runs through: observe, metabolise, think. |
| `spores/` | Memory storage: short term cache, long term index, the network that joins them. |
| `soul/` | Personality traits and how they drift over time. |
| `archetypes/` | The Village: Gordon, Mercy, Benedict, Jester and the rest. |
| `mechanics/` | Slash commands, the terminal interface, setup wizard, inventory, and the word lookup (`lexicon.py`, `resonance.py`). |
| `lore/` | All the tunable content as JSON: word lists, thresholds, banned phrases, prompt text. |
| `agents/` | Design documents that bind future AI sessions. Read these before changing anything. |
| `tools/` | Audit scripts. Run these instead of trusting numbers in the docs. |

The entry point is `main.py`. The per turn loop is `cycle.py`.

If you only remember two file names: `lore/lexicon.json` is the vocabulary the
engine thinks in, and `lore/tuning_presets.json` is every number you can turn.

## Before you read the source: the vocabulary problem

The code is written in biological metaphor throughout: ATP, cortisol, autophagy,
Gödel scars, the Village, the Mnemonic Arcade. This is deliberate and it is
protected by the project's own constitution (`agents/constitution.md`, Article
2): the names are not decoration, they map to real variables and must not be
renamed to `error_count` and `energy_level`.

The thing to hold in your head is that the metaphor describes what the numbers
are *for*, not what they *are*. `ATP` is a float that goes down when work happens
and gates certain behaviours. Calling it ATP tells you its purpose. It does not
mean the program has a metabolism in any sense a biologist would accept.

This matters because the vocabulary is persuasive enough to make you stop asking
whether a thing is connected. That turned out to be the central problem with the
codebase, and it is what most of the recent work was about.

## What it does

- **Memory finds related things.** Mention your grandmother's letters and it can
  surface the shoebox conversation from weeks ago, with no shared words. Related
  concepts measure 0.92 similarity where they used to measure negative numbers.

- **Creativity varies with the conversation.** When the maths says a coherent
  structure can exist, the model's temperature opens up; when it cannot, output
  collapses to deterministic logic. Rich, coherent input runs hot. Scattered or
  contradictory input stays cold. This is Nelson Spence's Creative Determinant,
  solved per turn over the graph Laplacian of a memory subgraph, and it is the
  one piece of genuine mathematics in the engine.

- **Short term memory works, and is consumed.** Significant moments land in the
  hippocampus, connect to similar recent moments, and get promoted into long
  term storage during sleep. Stress driven forgetting is real: at high cortisol
  holding 85 memories, it sheds 36 of them.

- **Both kinds of recall run.** Exact recall (have we been in this exact room
  before) and semantic recall (what does this remind me of).

- **Conversations have places.** Memories are tagged with the zone they were
  formed in, retrieval is scoped to the zone you are in, and crossing from one to
  another flushes working memory.

- **Words are understood rather than guessed at.** 81% of ordinary English
  resolves through filler, the curated lists, or semantic resonance. When the
  engine meets a word it does not know and can place it confidently, it files it
  and keeps it.

- **Failures are visible.** Crashes surface with stack traces, missing config is
  named at startup, and a degraded memory backend announces itself rather than
  quietly serving nonsense.

- **It can decline to answer.** The Village is a cast of voices, each
  triggered by a different shape of conversation. When several are triggered
  at once the Stage Manager negotiates before anyone speaks: certain pairs
  have a named fusion and merge, and when there is no resolution it holds the
  floor empty rather than blending them into something smooth and false. A
  held turn never reaches the model at all. This is the one behaviour here
  with no mainstream equivalent, and it is rare on purpose; most turns have
  one voice in the room and nothing to negotiate.

- **It adapts to you, not just to itself.** The engine keeps a running guess
  at how tired *you* are. It reads withdrawal rather than volume: messages
  getting shorter or blunter *than your own normal* is the signal, so someone
  who simply writes tersely is not mistaken for someone who has gone quiet.
  When it reads you as flagging it shortens its own replies to match. Writing
  at length does the opposite; it counts as effort spent, and when you have
  spent enough the engine offers to carry part of the load. The guess
  survives between sessions, and `/status` shows what it currently believes
  ("You: steady", "tiring", "flagging") so you can disagree with it.

- **Subsystems say what they did.** Eight of them file a short record every turn:
  what they were handed, what came back, and whether they ran normally or on a
  fallback. `/diag` prints the turn's records plus three lists that matter more:
  anything that promised to report and never did, anything on its fallback path
  every single time, and anything that runs and returns nothing, always. From the
  outside all three look exactly like healthy output, which is the whole reason
  the mechanism exists.

  The rule that gives it teeth is small: the part doing the job fills in its own
  record. Nothing reports on another part's behalf, and nothing is inferred from
  whether an error was thrown. A component cannot write a healthy-looking record
  of work it did not do without someone typing a deliberate lie.

## Project status

Working and in active development. The test suite is **484 passing, 5 skipped**
(the skips need a chat model pulled in Ollama).

Recent work was almost entirely archaeology rather than features. Large parts of
this program were running correctly and connected to nothing: not crashed, not
erroring, just wired to the wrong place or wired nowhere at all. Thirteen of
them. Memory coordinates came from a cryptographic hash, which is a tool designed
specifically to destroy the relationship between similar inputs. The Creative
Determinant was computed every turn and discarded. Ten settings existed in no
config file, so editing them did nothing, forever. Twenty five error reports were
downgraded to debug and thrown away by an argument ordering mistake, including
the handler that catches a crashed turn.

**None of these produced an error, a log line, or a failing test.** They could
not have. The only output this program has is prose, and prose looks identical
whether the physics ran properly or quietly returned zeros. A crash would have
been a gift; silence was the expensive failure. That is why the receipts above
exist, and why defensive programming is treated here as a disease rather than a
style question. A program that never crashes and whose only output is fluent text
can be completely broken and still look healthy.

`ROADMAP.md` has the full account with the measurement behind every claim, and
the plan for what is next.

### Honest limits

- It is a prompt builder. The word counting layer is hand tuned heuristics with
  physics names, and that is a legitimate design, but it is not a simulation.
- About 16% of ordinary English stays unresolved, on purpose.
- Receipts record what a subsystem did, not whether it was right. They make the
  engine auditable, not correct.
- The metabolic economy has not been tuned against a real chat model end to end.

## Checking it yourself

Run these rather than trusting the numbers in any document, including this one:

```bash
.venv/bin/python -m pytest -q                      # 484 passed, 5 skipped
.venv/bin/python tools/audit_physics_inputs.py     # how much vocabulary it knows
.venv/bin/python tools/audit_receipts.py           # which subsystems did real work
.venv/bin/python tools/audit_handlers.py           # silent exception handlers
.venv/bin/python tools/audit_safe_get.py           # runtime default hit-rate
```

If replies ever start feeling generic, `audit_receipts.py` is the first thing to
check.

## Documentation

| File | What it is |
|---|---|
| `ROADMAP.md` | What is next and why, with the measurement behind every claim. |
| `SESSION_HANDOFF.md` | What is true right now and which traps to avoid. Read before changing anything. |
| `agents/constitution.md` | The rules that bind changes to this codebase. Load-bearing. |
| `docs/README.MD` | The Hypervisor, BoneAmanita's no-math sibling for cloud models. |
| `credits.txt` | Full lineage and attribution. |
| `license.txt` | MIT, human/computer variant. |

## Credits

BoneAmanita builds directly on other people's work, most of it load bearing
rather than inspirational:

- **Nelson Spence** ([Project Navi](https://project-navi.github.io)) for the
  Creative Determinant and `ordvec`. The Creative Determinant is this engine's
  control loop, not a flavour layer over one.
- **James Taylor** ([BonePoke](https://github.com/utharian-code/bonepoke)) for
  Volatile Semantic Leverage and the "Truth Over Cohesion" axiom that the
  Lexical Firewall is built on.
- **Bradley Bates** ([bradsadevnow](https://github.com/bradsadevnow/)) for the "Gloss" framework and endless inspiration and advice.


`credits.txt` has the full list and the specifics. On verification: `ordvec` is
itself Lean 4 verified and the Creative Determinant has its own formalisation,
both in Project Navi's repos. BoneAmanita's own implementation of those equations
is ordinary Python and carries no proofs.

## License

MIT, in a human/computer variant that asks for transparency about how the code
was made. See `license.txt`.
