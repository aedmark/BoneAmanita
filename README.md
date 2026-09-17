# BoneAmanita: what this is, in plain language

## The one paragraph version

BoneAmanita is a program that sits between you and a language model and
rewrites your instructions to it on every single turn. It measures your
message, keeps a running physical and emotional state that persists
between sessions, and uses that state to assemble a fresh instruction
sheet for the model each time you speak. Then it filters the reply for
clichés and makes the model try again if it finds any.

That is the whole machine. Everything else is detail about how the state
is measured and which sentences it produces.

## What actually happens when you type something

1. **Your words get sorted into categories.** Four stages, most
   trustworthy first:
   - **Grammatical filler** (`the, a, is, at, and`). About 40% of normal
     speech. These are not unclassified, they are connective tissue, and
     the engine measures their density as its own signal.
   - **The curated word lists** in `lore/lexicon.json`: heavy words,
     kinetic words, abstract words, void words, corporate cliché words,
     and thirty odd other categories. Inflections resolve to their root,
     so `forge` answers for `forging` and `forged`.
   - **Semantic resonance.** A word the lists do not know is compared
     against an average of each category's meaning, using the same
     embedding model the memory uses. If it clearly belongs somewhere,
     the engine files it and remembers it. If it is genuinely between two
     categories, it stays unfiled.
   - **A last-resort guess from spelling**, which now fires on about 3%
     of words.

   Roughly 81% of ordinary English resolves without guessing. The rest
   stays unresolved on purpose. Nobody knows all of English, and an
   engine that pretends to is the failure mode this whole layer was
   rebuilt to escape.

2. **Those counts become numbers.** Formulas in `physics/` turn the
   counts into roughly sixty values with names like `voltage`,
   `narrative_drag`, `cortisol`, `atp_pool` and `chi`. These are hand
   tuned heuristics wearing physics names. They are not real physics,
   and they do not need to be; they work as a way of tracking the shape
   of a conversation.

3. **Thresholds pick sentences.** If contradiction is high, a sentence
   about holding paradox goes into the instruction sheet. If energy is
   low, an instruction to write shorter sentences goes in. This assembly
   happens in `brain/composer.py`, and the result is about 900 tokens.

4. **One request goes out.** A single HTTP call to whatever model you
   have configured (Ollama by default). The model sees only the
   assembled instructions plus your message.

5. **The reply gets inspected.** A filter checks for banned phrases
   ("I understand how you feel", "rich tapestry", and a long list in
   `lore/style_crimes.json`). On a hit, the reply is discarded and the
   model is asked again.

6. **State is written to disk.** Energy spent, stress accumulated, scars
   earned. This is why the next session does not start fresh.

## The vocabulary problem

The code is written in biological metaphor throughout: ATP, cortisol,
autophagy, Gödel scars, the Village, the Mnemonic Arcade. This is
deliberate and it is protected by the project's own constitution
(`agents/constitution.md`, Article 2): the names are not decoration,
they map to real variables and must not be renamed to `error_count` and
`energy_level`.

The thing to hold in your head is that the metaphor describes what the
numbers are *for*, not what they *are*. `ATP` is a float that goes down
when work happens and gates certain behaviours. Calling it ATP tells you
its purpose. It does not mean the program has a metabolism in any sense
a biologist would accept.

This matters because the vocabulary is persuasive enough to make you
stop asking whether a thing is connected. That turned out to be the
central problem with the codebase (see below).

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

If you only remember two file names: `lore/lexicon.json` is the
vocabulary the engine thinks in, and `lore/tuning_presets.json` is every
number you can turn.

## The problem we spent this week on

Large parts of this program were running correctly and connected to
nothing. Not crashed, not erroring, just wired to the wrong place or
wired nowhere at all. We found a dozen.

A few, in plain terms:

- **Memory had no sense of meaning.** Words were turned into numbers
  using a cryptographic hash, a tool designed specifically to destroy
  any relationship between similar inputs. "dog" and "canine" landed
  further apart than "dog" and "asphalt". Every memory search had been
  returning near random results since the project began.

- **The creativity math was computed and discarded.** Nelson Spence's
  Creative Determinant equations ran correctly and produced a number
  that was meant to control how loose or rigid the output was. Nothing
  ever passed it along. The receiving code was written, correct, and
  never called.

- **Ten settings did not exist.** Not in any config file. Every
  subsystem reading them silently used a hardcoded fallback. Editing
  them in `tuning_presets.json` would have done nothing, forever, with
  no way to notice.

- **Error reports went nowhere.** Twenty five places tried to report a
  serious problem and, because of an argument ordering mistake, were all
  downgraded to debug level and thrown away. That included the handler
  that catches a crashed turn: it would format a full stack trace and
  then discard it.

- **Short term memory had no writer.** The hippocampus had readers, a
  consolidation process and a stress response, but nothing ever put a
  memory in. It was permanently empty.

- **The word lists supplied 13% of their own physics.** The rest came
  from a spelling based guesser that classified two thirds of English as
  "play". That saturated one of the eight dimensions, which pinned every
  conversation to the same zone. This one was different from the others:
  it was not disconnected. It was connected, running, and confidently
  wrong, which made it both more serious and much harder to see.

**None of these produced an error, a log line, or a failing test.** They
could not have. The only output this program has is prose, and prose
looks identical whether the physics ran properly or quietly returned
zeros. A crash would have been a gift. Silence was the expensive failure.

This is why the defensive programming mattered. It was not a style
question; it was the disease. A program that never crashes and whose only
output is fluent text can be completely broken and still look healthy.

## What works now that did not before

- **Memory finds related things.** Mention your grandmother's letters and
  it can surface the shoebox conversation from weeks ago, with no shared
  words. Related concepts now measure 0.92 similarity where they used to
  measure negative numbers.

- **Creativity actually varies with the conversation.** When the maths
  says a coherent structure can exist, the model's temperature opens up;
  when it cannot, output collapses to deterministic logic. Rich, coherent
  input runs hot. Scattered or contradictory input stays cold.

- **Short term memory works, and is consumed.** Significant moments land
  in the hippocampus, connect to similar recent moments, and get promoted
  into long term storage during sleep. Stress driven forgetting is real:
  at high cortisol holding 85 memories, it sheds 36 of them.

- **Both kinds of recall run.** Exact recall (have we been in this exact
  room before) and semantic recall (what does this remind me of).

- **Failures are visible.** Crashes surface with stack traces, missing
  config is named at startup, and a degraded memory backend announces
  itself rather than quietly serving nonsense.

- **Mistakes are no longer swallowed.** The code was full of places that
  caught an error and carried on as if nothing had happened; there were 72
  of them, and 30 threw the error away entirely without leaving so much as
  a note. Those 30 are down to 3, and all three are cases where ignoring
  the error is genuinely the right thing (a settings file that does not
  exist yet on your first run, for instance). A test now refuses any new
  ones.

  Doing this turned up another dead part. The Tinkerer is the character who
  notices which of your tools you keep reaching for and gradually
  recognises them; once a tool reaches level 5 it is supposed to be
  mentioned in the model's instructions as something you have mastery over.
  It was counting correctly the whole time and had no way to tell anyone,
  because a single method for handing that information onward had never
  been written. The place that asked for it caught the resulting error and
  substituted an empty answer, every turn. So mastery has never appeared in
  a prompt, and it was never saved between sessions either. Now it is both.

- **Each part of the engine now says what it did.** Seven of them file a
  short record every turn: what they were handed, what came back, and
  whether they were running normally or on a backup path. Type `/diag`
  and you get the turn's records, plus three lists that matter more:
  anything that promised to report and never did, anything that has been
  on its backup path every single time, and anything that runs and
  returns nothing, always. Each of those looks exactly like healthy
  output from the outside, which is the whole reason for the mechanism.

  The rule that makes it work is small: the part doing the job fills in
  its own record. Nothing is allowed to report on another part's behalf,
  and nothing is inferred from whether an error was thrown. A component
  cannot write a healthy-looking record of a job it did not do without
  someone typing a deliberate lie.

  It paid for itself immediately. On the very first turn it ran, it
  caught the creativity maths solving against the wrong sentence: the
  code was reading the user's message back out of the conversation log,
  and that log is not written until after the model has already replied,
  so it had always been working from the previous thing you said. On the
  first message of a session it had nothing at all. Nothing was broken,
  nothing crashed, and the output looked fine; the maths was just one
  step behind the conversation the whole time.

- **Words are understood rather than guessed at.** 81% of ordinary
  English now resolves through filler, the curated lists, or semantic
  resonance, up from 13%. When the engine meets a word it does not know
  and can place it confidently, it files it and keeps it. Those learned
  words live in their own file, separate from your hand written lists,
  capped and reversible: delete `saves/cortex_hive.json` and it forgets
  everything it taught itself.

- **Conversations have places again.** Memories are tagged with the zone
  they were formed in, retrieval is scoped to the zone you are in, and
  crossing from one to another flushes working memory. All four zones
  are reachable; before this, eleven of twelve inputs landed in the same
  one.

Tests went from 282 passing to 422, all green. The suite needs two
optional pieces installed (`ordvec` from PyPI, `mistral-nemo` in Ollama);
with those present, a red suite now means something.

## What this is now, honestly

The same architecture, with the wiring connected. Nothing was redesigned.
The metaphors are more true than they were: where the documentation
claimed associative memory, there is now association; where it claimed
the equations constrain generation, they now do.

What has not changed: it is still fundamentally a prompt builder. The
word counting layer is still hand tuned heuristics with physics names,
and that is fine. The genuine mathematics lives in one identifiable place
(the Creative Determinant, in `physics/`) and is now load bearing.

The fair summary is that this was already more coherent as a design than
it was as a running program. Most of the work was not adding features. It
was reconnecting things that had been correctly designed and written, and
had come apart quietly enough that nothing ever said so.

The one genuine addition is the last stage of word resolution, and even
that mostly supplied a missing piece rather than a new system: the
machinery for learning a word was already built and persisted and wired
into the index, and nothing anywhere decided what category a word
belonged to.

Two things are worth keeping in mind about what it still is. It remains a
prompt builder, so its effects are produced by instructions to a model
rather than by the simulation the naming implies. And it deliberately
leaves about 16% of ordinary English unresolved, because nobody knows all
of English and an engine that pretends to is exactly the failure this
layer was rebuilt to escape.

## Running it

```bash
python3 -m venv .venv
.venv/bin/pip install pytest numpy faiss-cpu requests markdown ordvec
ollama pull nomic-embed-text    # memory and word resolution need this
ollama pull mistral-nemo        # or whatever chat model you prefer
.venv/bin/python main.py
```

First run asks some setup questions and writes `config.json`. If the
memory backend is unreachable it will still boot, and will tell you that
recall is disabled rather than pretending otherwise. Word resolution
degrades too but keeps working: filler and the curated lists need no
server at all.

Two things worth knowing about the files it writes. `config.json` is
generated, not in the repo. `saves/cortex_hive.json` holds every word the
engine has taught itself; deleting it is the clean way to make it forget
without touching your curated lists.

`python tools/audit_physics_inputs.py` prints how much of its own
vocabulary the engine actually knows, which is the number to watch if you
ever add words. `python tools/audit_receipts.py` prints which parts of the
engine reported doing real work, which is the thing to check first if the
replies ever start feeling generic.
