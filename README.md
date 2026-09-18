# BoneAmanita

A state machine that sits between you and a local language model and rewrites
the model's instructions on every turn, based on a physical and emotional state
with selected state saved between sessions.

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
backend is unreachable the engine still boots on hash coordinates and announces
degraded operation. Those coordinates do not support meaningful associative
recall. Grammatical filler and the curated word lists need no server. Runtime
embedding failures have additional known defects; see Honest limits below.

### Requirements

- **Python 3.14 is the development version.** The September 18 review used
  3.14.7. Compatibility with older versions was not established by that review.
- **An OpenAI-compatible `/v1/embeddings` endpoint** for the memory's coordinate
  system. Ollama, LM Studio, llama.cpp and OpenAI all serve one. Point at a
  different one with `BONE_EMBED_URL` and `BONE_EMBED_MODEL`.
- **A chat model**, local by default via Ollama.
- Everything else is in `requirements.txt`. Two entries there are load bearing
  in a way worth knowing: `ordvec` (Project Navi) backs both the subconscious
  memory search and the governor's bitmap similarity gate, and the
  engine announces at boot if it is missing rather than quietly doing without.
  `sentence-transformers` is commented out; uncomment it for a fully offline
  embedder with no server at all.

### Files it writes

`config.json` is generated on first run and is not in the repo.
`saves/cortex_hive.json` holds every word the engine has taught itself;
deleting it is the clean way to make it forget without touching your curated
lists. `saves/quicksave.json` stores selected session state and dialogue;
checkpoint writes currently have a known data-loss risk on write failure.
`reset.sh` deletes saved memories, saves, logs, and other files listed in the
script; it leaves the setup configuration in place.

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

   Earlier vocabulary audits reported roughly 81% resolved through filler,
   curated lists, or semantic resonance, about 3% through spelling heuristics,
   and about 16% unresolved. These are corpus- and backend-dependent audit
   results, not coverage guarantees for arbitrary English.

2. **Those counts become numbers.** Formulas in `physics/` turn the counts into
   roughly sixty values with names like `voltage`, `narrative_drag`, `cortisol`,
   `atp_pool` and `chi`. These are hand tuned heuristics wearing physics names.
   They are not real physics, and they do not need to be; they work as a way of
   tracking the shape of a conversation.

3. **Thresholds pick instructions and generation limits.** If contradiction is
   high, a sentence about holding paradox can enter the instruction sheet.
   `SomaticBudget` sets sentence and word targets, a retry allowance, and a
   temperature band from inferred user state and engine state. The composer
   asks for shorter replies and forbids narrating bodily exhaustion; the cortex
   also limits output tokens. Prompt instructions do not guarantee compliance,
   and a token limit is not an exact word or sentence limit. Prompt length
   varies with history, memory, and mode.

4. **The engine may call the model.** A held turn can stop before generation.
   Otherwise the request includes assembled instructions, dialogue context,
   and your message. Transport retries, empty-reply retries, optional DSPy
   critic calls, and council behavior can add model requests.

5. **The reply gets inspected.** A filter checks for banned phrases ("I
   understand how you feel", "rich tapestry", and a long list in
   `lore/style_crimes.json`). On a hit, the reply is discarded and the model is
   asked again within a retry budget. Exhausting that budget produces a
   fallback response rather than unlimited retries.

6. **Selected state is saved.** The normal completed-turn path writes a
   checkpoint; other memory and learned-state stores also have persistence
   paths. Not every runtime field or early-exit path is checkpointed. Save
   reliability is one of the outstanding issues below.

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
| `lore/` | Authored JSON content: word lists, many thresholds, banned phrases, prompt text. |
| `tools/` | Audit scripts. Run these instead of trusting numbers in the docs. |

The entry point is `main.py`. The per turn loop is `cycle.py`.

If you only remember two file names: `lore/lexicon.json` is the vocabulary the
engine thinks in, and `lore/tuning_presets.json` holds much of the tuning.
Additional defaults and mode settings live in `presets.py`; some thresholds
remain inline in the code.

## Before you read the source: the vocabulary problem

The code is written in biological metaphor throughout: ATP, cortisol, autophagy,
Gödel scars, the Village, the Mnemonic Arcade. This is deliberate and it is
protected by a standing project decision (`SESSION_HANDOFF.md`, "Decisions
already made"): the names are not decoration, they map to real variables and must not be
renamed to `error_count` and `energy_level`.

The thing to hold in your head is that the metaphor describes what the numbers
are *for*, not what they *are*. `ATP` is a float that goes down when work happens
and gates certain behaviours. Calling it ATP tells you its purpose. It does not
mean the program has a metabolism in any sense a biologist would accept.

This matters because the vocabulary is persuasive enough to make you stop asking
whether a thing is connected. That turned out to be the central problem with the
codebase, and it is what most of the recent work was about.

## What it does

- **Semantic memory can find related things with a working embedder.** Mention
  your grandmother's letters and it can surface a related shoebox conversation
  without shared words. Related
  concepts reached 0.92 similarity in an earlier audit; that is an example,
  not a retrieval guarantee. Hash fallback does not preserve these relationships.

- **Memory similarity influences sampling.** The governor scores the current
  utterance against an `ordvec` sign bitmap and compares its top matches with
  the corpus distribution, correcting for corpus size. That signal influences
  policy and a proposed sampling temperature. With too little evidence it
  declines to measure the regime and falls back to PID regulation. The model
  interface clamps the proposed temperature to the supplied temperature band,
  so a closed gate does not guarantee zero-temperature sampling. The former
  graph-Laplacian/Picard solver has been removed. The Creative Determinant
  equations remain in the metabolic viability, ATP, and ROS calculations.

- **Short term memory works, and is consumed.** Significant moments land in the
  hippocampus, connect to similar recent moments, and get promoted into long
  term storage during sleep. Stress driven forgetting is real: at high cortisol
  holding 85 memories, it sheds 36 of them.

- **Both kinds of recall run.** Exact recall (have we been in this exact room
  before) and semantic recall (what does this remind me of).

- **Conversations have places.** Memories are tagged with the zone they were
  formed in, retrieval is scoped to the zone you are in, and crossing from one to
  another flushes working memory.

- **Word classification combines curated lists and semantic matching.** Earlier
  audits reported 81% resolution through filler, curated lists, or resonance.
  This measures classification coverage, not language understanding. When the
  engine meets a word it does not know and can place it confidently, it files it
  and keeps it.

- **Many failures are reported.** Turn crashes can surface with stack traces,
  missing config is named at startup, and a degraded embedding backend is
  announced. Reporting is not complete: transient embedding failures can
  currently produce misleadingly healthy receipts.

- **It can decline to answer.** The Village is a cast of voices, each
  triggered by a different shape of conversation. When several are triggered
  at once the Stage Manager negotiates before anyone speaks: certain pairs
  have a named fusion and merge, and when there is no resolution it holds the
  floor empty rather than blending them into something smooth and false. A
  held turn stops before response generation. Refusal routing is still under
  development, and its current regression tests include failures.

- **It adapts to you, not just to itself.** The engine keeps a running guess
  at how tired *you* are. It reads withdrawal rather than volume: messages
  getting shorter or blunter *than your own normal* is the signal, so someone
  who simply writes tersely is intended to be distinguished from someone who
  has gone quiet. This remains a heuristic inference about the person.
  When it reads you as flagging it requests shorter replies and lowers the
  output-token budget. Actual accommodation still needs measurement. Writing
  at length does the opposite; it counts as effort spent, and when you have
  spent enough the prompt asks the model to offer to carry part of the load.
  The user model is included in quicksave/restore, and `/status` shows what it
  currently believes ("You: steady", "tiring", "flagging") so you can disagree
  with it.

- **Subsystems file receipts.** Nine subsystem names are registered in the
  current core roll call; which ones report depends on the path taken. Records
  describe what they were handed, what came back, and whether they ran normally or on a
  fallback. `/diag` prints the turn's records plus three lists that matter more:
  anything that promised to report and never did, anything on its fallback path
  every single time, and anything that runs and returns nothing, always. From the
  outside all three look exactly like healthy output, which is the whole reason
  the mechanism exists.

  The rule that gives it teeth is small: the part doing the job fills in its own
  record. That makes work inspectable, but it does not make the record
  automatically accurate. The September 18 review reproduced hash fallback
  reported as successful HTTP vectorization. Receipt correctness needs tests too.

## Project status

An experimental system in active development. **The current test baseline is
not green.** A September 18, 2026 review of `b0a096e` plus the existing working
tree changes found seven failing tests. Its follow-up selection finished with
**129 passed, 7 failed, 4 skipped**; that is a selected run, not a full-suite
total. The previously quoted 501 passed / 5 skipped is historical. The review
did not run the live-model behavioral audits.

See the [latest session handoff](SESSION_HANDOFF.md#review-2026-09-18) for exact
commands, all seven failures, reproduced runtime defects, and next-round work.

Earlier audits found disconnected components, hash-based memory coordinates,
settings absent from config files, and severity logs routed incorrectly. That
history motivated the receipts and state-to-prompt tests. Fluent prose can hide
broken internals: neither a plausible reply nor the absence of an exception is
enough to establish that the machinery worked. The current review shows that
failure paths still need scrutiny even when diagnostics are present.

`ROADMAP.md` preserves the earlier measurements and development plan. Its dated
status summary and the latest handoff take precedence over historical sections.

### Honest limits

- It is a prompt builder. The word counting layer is hand tuned heuristics with
  physics names, and that is a legitimate design, but it is not a simulation.
- Earlier vocabulary audits left about 16% of their inputs unresolved; results
  depend on the corpus and embedding backend.
- Receipts record a subsystem's account of its work. They make the engine
  inspectable; both that account and the underlying result need verification.
- **Embedding outages can compromise recall and diagnostics.** Transient
  failures cache hash vectors under the real backend's identity and report
  non-degraded receipts. Switching to hash after repeated failures can return
  mixed vector dimensions in a batch. These defects were reproduced and remain
  unfixed.
- **Persistence and shutdown need repair.** An interrupted or failed quicksave
  write can replace a valid checkpoint with incomplete JSON. Engine shutdown
  leaves the cycle daemon running. Both were reproduced in isolated probes.
- **The six-turn starvation result is historical.** The roadmap records later
  D0 repairs and a 30-turn live census with ATP between 16 and 53. That establishes
  an improved energy budget for that experiment, not reliable responses on every
  turn. D0b's resized refusal gates still lack a completed confirming live census;
  the current somatic and refusal changes have not been revalidated by this review.
- **Earlier somatic wording had weak effects.** Measured on two local
  models (`tools/audit_somatic.py`), the low-energy instruction makes sentences
  about 10% shorter and no shorter overall, and one of the two models mostly
  responds by writing about its breathing. The "three sentences or less"
  instruction is not obeyed: neither model got shorter, and one wrote more
  sentences under it than without it. The instructions reach the model every
  time in those experiments; what the model does with them is weak, and for
  exhaustion it is wrong. These measurements describe the earlier directives.
  The current somatic-budget wording needs a fresh live audit before claiming
  improved compliance.

## Checking it yourself

Run these rather than trusting the numbers in any document, including this one.
Use a disposable checkout with Git metadata and the working changes you intend
to test: some checks call `git ls-files`, and engine tests write state and logs.
The suite pins embeddings to hash in many tests, but not every chat path is
isolated from the configured backend. Live embedding tests can be enabled with
`BONE_EMBED_LIVE_TEST=1`.

```bash
.venv/bin/python -m pytest -q                      # current baseline has known failures
.venv/bin/python tools/audit_physics_inputs.py     # how much vocabulary it knows
.venv/bin/python tools/audit_receipts.py           # which subsystems did real work
.venv/bin/python tools/audit_handlers.py           # silent exception handlers
.venv/bin/python tools/audit_safe_get.py           # runtime default hit-rate
.venv/bin/python tools/audit_somatic.py            # does the model obey its body (live, ~15 min)
.venv/bin/python tools/audit_somatic_census.py     # a scripted conversation: where the energy goes (live)
```

If replies ever start feeling generic, `audit_receipts.py` is the first thing to
check.

## Documentation

| File | What it is |
|---|---|
| `ROADMAP.md` | Current priorities plus dated measurements and historical implementation plans. |
| `SESSION_HANDOFF.md` | The project's reference document: what is true right now, the decisions that bind changes, and which traps to avoid. Read before changing anything. |
| `docs/README.MD` | The Hypervisor, BoneAmanita's no-math sibling for cloud models. |
| `credits.txt` | Full lineage and attribution. |
| `license.txt` | MIT, human/computer variant. |

## Credits

BoneAmanita builds directly on other people's work, most of it load bearing
rather than inspirational:

- **Nelson Spence** ([Project Navi](https://project-navi.github.io)) for the
  Creative Determinant metabolic equations, `ordvec`, and the recommendation
  behind the current bitmap regime gate.
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
