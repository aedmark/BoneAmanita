# Session handoff: BoneAmanita & The Hypervisor

Paste this into a fresh context window to resume. Written at the point
where the Mnemonic Arcade was given a real coordinate system (see
"What changed most recently"), which is the first change in a while that
altered what the engine actually *does* rather than how it is tuned.

Structure and working conventions here are inherited from the T.R.S. →
SCI0 handoff (`/home/gordonk/RiderProjects/TRS_SCI/SESSION_HANDOFF.md`);
the project-specific content is obviously all BoneAmanita's. Where that
file and this one describe the same working habit, they should stay in
sync, those habits are not project-specific.

## What this is

BoneAmanita is a **stateful prompt-construction engine with a
retry/filter loop**, wrapped around a plain OpenAI-compatible
`/chat/completions` call. ~31k lines of Python across ~220 files, one
year and 930 commits of solo development, v20.7.0.

That plain description is not a demotion, it is the thing to hold onto
when reading the code, because the vocabulary actively works against it.
The pipeline, per turn:

1. Input is tokenized and words are counted against hand-written keyword
   lists in `lore/lexicon.json` (`heavy`, `kinetic`, `abstract`, `void`,
   `liminal`, `antigen`, ...).
2. Those counts feed hand-tuned arithmetic (`physics/geodesics.py`,
   `physics/dynamics.py`) producing ~60 floats: `voltage`, `chi`,
   `narrative_drag`, `atp_pool`, `cortisol`, and the rest.
3. Thresholds on those floats select which English sentences get
   assembled into a system prompt (`brain/composer.py:336`, `compose()`).
4. One HTTP call, single user message, ~900 tokens of assembled prompt
   (`brain/composer.py:147`, `generate()`).
5. The response is regex-filtered for clichés and boilerplate; on a hit
   it re-asks (`brain/composer.py:792`, `ResponseValidator`).
6. State persists to JSON on disk and carries across sessions.

Everything else, the daemons, the village, the council, REM cycles,
autophagy, is machinery for deciding which sentences land in step 3.

**The physics is a keyword-driven rule engine, not physics.** The
formulas are dimensionally meaningless by design (word counts times
tuned weights, divided by token volume). That is a legitimate way to
build a prompt-steering state machine. It is not what
`credits.txt` claims ("mathematically verified Partial Differential
Equations") and a future session should not go looking for PDEs that
aren't there. See "Claims vs. code" below.

## Current state: what's actually built and confirmed working

- **Test suite: 306 passed, 2 failed, 2 skipped.** Both failures are
  environmental and predate any recent work, details under Environment.
  Baseline before the embeddings work was 282 passed / 2 failed.
- **Module boundaries are genuinely clean.** `physics/`, `body/`,
  `brain/`, `phases/`, `mechanics/`, `spores/`, `soul/`, `archetypes/`
  are real separations. Config is externalized to `lore/*.json`. Most
  classes take a `config_ref` for injection. Above average for a solo
  project this size.
- **The Lexical Firewall works.** `ResponseValidator` compiles banned
  phrases and patterns from `lore/style_crimes.json` and forces
  regeneration on a hit. Suppressing "I understand how you feel" and
  "rich tapestry" via deny-list plus retry is a real anti-slop mechanism
  and is the single highest-value thing in the codebase.
- **Circuit breaker and local fallback work** (`brain/composer.py:235`).
- **The Mnemonic Arcade now does real associative recall** (new, see
  below).
- **The `agents/` docs are unusually disciplined.** `constitution.md`
  with explicit "WHY NOT" blocks is better design documentation than
  most commercial codebases have. They are load-bearing: read them
  before touching anything, in the order `agents/prompt.md` specifies
  (constitution → conventions → glossary → domain_*).

## What changed most recently: real embeddings

`_word_to_vector` used to derive memory coordinates from
`shake_256(word)`. A cryptographic digest is designed to destroy input
correlation, so that space had no semantic structure at all. Measured
before and after:

```
                 before (SHAKE-256)    after (nomic-embed-text)
dog / canine           -0.083                  +0.919
dog / puppy            +0.700                  +0.790
happy / joyful         +0.512                  +0.833
dog / asphalt          +0.448                  +0.416   <- now correctly below
```

Every nearest-neighbour sweep over the old space was noise. The whole
Arcade, Subconscious Dredging, Shadow Casting, the Tunnel Vision
Protocol, was clamping and scoping a retriever that had nothing to
retrieve.

**What was added**: `spores/embeddings.py`, one `SemanticEmbedder`
probed once at boot. Order: OpenAI-compatible `/v1/embeddings` → local
`sentence-transformers` if installed → the legacy hash. L2-normalized
(so `resonance_threshold` means the same thing across backends),
LRU-cached, batched, thread-safe, never raises into the hot path. A
transient blip does not sever the backend; three consecutive failures
do, loudly. **No new dependency**: it POSTs over `requests`, already
present.

**Two other bugs had to be fixed or the swap would have been inert**,
both of which had been silently dead for a long time:

1. `brain/cortex.py` built its query vector out of *physics*
   coordinates (`STR`, `VEL`, `PSI`, `ENT`, ...) and searched an index
   populated with *text* vectors. Unrelated coordinate systems, so that
   lookup could not return a meaningful neighbour under any input in any
   biological state. Now queries through `CerebralIndex.embed()`;
   physics still steers via `physics_state` (cortisol clamping, wing
   scoping, lateral search).
2. `getattr(self.svc.mind_memory, "ann", None)` was always `None`, the
   attribute on `MycelialNetwork` is `cortex`. The entire FAISS branch
   was dead and every shadow cast fell through to the `random.sample()`
   fallback below it.

Also: ingestion embedded `text[:50]`, making a memory retrievable only
by a query sharing its exact opening 50 characters. Now embeds the
passage. `CerebralIndex` sizes itself to the embedder instead of a
hardcoded 8. Documented as `[DEC-09]` and `[DEC-10]` in
`agents/domain_02_mind.md` in the project's own WHY / WHY NOT format.

**Verified end to end** against live Ollama, on queries with no lexical
overlap with what was stored:

```
"my grandmother and the things she saved"          -> "My grandmother kept every letter..."
"spent all night chasing a memory corruption bug"  -> "Debugging a segfault in the parser..."
"nothing grew in the garden that year"             -> "The greenhouse behind the old house..."
```

Cortisol clamping still bites (2 hits at 0.95 vs 3 at 0.0). The degraded
path was separately confirmed to still boot and complete turns with the
server unreachable.

## Claims vs. code (read before trusting `readme.txt` or `credits.txt`)

`readme.txt`'s memory section and the embeddings dependency notes were
corrected as part of the work above. These remain overstated and a
future session should not treat them as a specification:

- **`credits.txt` credits "mathematically verified Partial Differential
  Equations."** There are none. There is polynomial arithmetic over word
  counts with tuned coefficients, e.g. `physics/geodesics.py:117`.
  Heuristics with physics names, which is fine as a design; just don't
  go hunting for the math.
- **"Semantic Bio-Physics" as a unified economy** is, concretely, ~247
  magic float literals in `phases/` alone driving if-statements.
- The engine's *behaviour* claims (exhaustion affecting prose, trauma
  persisting, the Tri-Gate) are broadly real, they're just produced by
  prompt assembly rather than by the simulation the naming implies.

## Decisions already made (don't re-litigate these)

- **No orchestration frameworks.** Constitution Article 1. LangChain,
  LlamaIndex, SemanticKernel, and vector-store libraries (Chroma,
  LanceDB) are all out, not because they're bad but because they take
  ownership of the control loop. This is why `spores/embeddings.py` is
  one HTTP POST and an LRU cache rather than a library.
- **Poetic variable names are load-bearing.** Constitution Article 2.
  `godel_scars`, `narrative_drag`, `ATP`, `psi` do not get renamed to
  `error_count` / `slow_factor` / `energy`. This has bitten previous
  sessions.
- **The embedder is HTTP-first, package-optional.** `sentence-transformers`
  is deliberately *not* in `requirements.txt`: the project already
  assumes a local model server, and pulling in torch to embed short
  strings is a ~2GB dependency for something one POST already does.
  It is detected and preferred if the user installs it themselves.
- **The hash fallback stays.** It needs no server and no package, which
  is genuinely worth something. It now self-reports `DEGRADED` at
  genesis and in `/status`, because an engine serving arbitrary memories
  sounds exactly like one serving real ones.
- **Env vars outrank `BoneConfig.EMBEDDINGS`**, which outranks module
  defaults. `BoneConfig.EMBEDDINGS` ships populated, so the other order
  made `BONE_EMBED_URL` a silent no-op. There are tests pinning this.
- **The test suite is pinned offline** (`tests/__init__.py` sets
  `BONE_EMBED_BACKEND=hash` before any test module imports). A test run
  must never depend on a reachable embedding server. `tests/test_embeddings.py`
  overrides per-test against mocked transport, plus one opt-in live test
  behind `BONE_EMBED_LIVE_TEST=1`.

## Environment / toolchain

- **Repo**: `/home/gordonk/PycharmProjects/BoneAmanita`, branch `main`,
  a PyCharm project. Remote is github.com/aedmark/BoneAmanita.
  930 commits, 221 tracked files. Commit subjects are almost all bare
  version numbers, and not monotonic ("20.7.0", then "7.0", then
  "7.0.1"), so `git log --oneline` is close to useless for finding when
  something changed, use `git log -S'<symbol>'` or `git log -p -- <path>`
  instead. The embeddings work described above is commit `7e90a74`
  ("7.0.1"), a useful anchor: it is the most recent change that altered
  behaviour rather than tuning.
- **There is no `.gitignore`.** This is why `git status` is permanently
  full of untracked runtime output (`__pycache__/`, `logs/`, `memories/`,
  `saves/`, `MagicMock/`, `test_*.log`, `test_telemetry_logs/`,
  `tests_isolated_legacy_*.json`, `dummy.jsonl`, `fractal_adventure.json`).
  `reset.sh` deletes all of it. Worth adding a `.gitignore` at some
  point; until then, don't mistake that noise for uncommitted work.
- **`.git` is 522MB** against ~525MB total, i.e. essentially the entire
  repo size is history. Not a problem, just don't be alarmed by
  `du -sh`.
- **Python 3.14.7 is the system interpreter and there is no venv in the
  project.** None of the dependencies are installed against it, so
  `python -m pytest` fails with "No module named pytest" out of the box.
  To run anything, make a venv first:
  ```bash
  python3 -m venv .venv && .venv/bin/pip install pytest numpy faiss-cpu requests markdown
  ```
  `dspy` and `ordvec` are *not* installable/installed here; both are
  optional and the engine degrades cleanly without them (`[DSPY OFFLINE]`
  prints at import, epigenetic learning and the DSPy critic just don't run).
- **Ollama is running on `127.0.0.1:11434` with exactly one model
  pulled: `nomic-embed-text:latest` (768d).** That is an *embedding*
  model only, there is no chat model installed, which is why
  `test_main.py::test_true_metabolic_token_generation` fails: it needs a
  live chat completion and `BoneConfig.MODEL` defaults to
  `mistral-nemo`, which isn't pulled. Fix by `ollama pull mistral-nemo`
  (or whatever chat model is wanted) if that test needs to pass.
- **The other failing test**, `test_memory.py::TestRankQuantAccuracy::test_fastscan_recall_accuracy`,
  fails with "Quantizer failed to boot" purely because `ordvec` is not
  installed. Both failures are environmental. If either fails with a
  *different* message than those two, that is new and worth
  investigating, in particular a dimension-mismatch `ValueError` from
  `np.vstack` in that test means the boot-load and `bury()` vector paths
  have diverged again (see Findings).
- **Running the engine**: `python main.py`. First run triggers
  `ConfigWizard` (`mechanics/setup.py`) which writes `config.json`
  (not in the repo, generated). Driving it headlessly for testing is
  easier than the TUI:
  ```python
  eng = BoneAmanita({"provider": "mock", "model": "mock",
                     "user_name": "T", "boot_mode": "CONVERSATION"})
  eng.process_turn("...")
  eng.orchestrator.shutdown()   # it starts a daemon thread; always shut down
  ```
  Note `process_turn` returns the *simulation* frame (`GEODESIC_FRAME`);
  generation happens separately on the daemon loop, so there is no
  `"response"` key in what it returns.
- **Full test suite takes ~3.5 minutes.** Long enough that it needs
  backgrounding rather than a foreground call with a short timeout.

## Findings / gotchas worth not re-discovering

- **`EventBus.log`'s signature is `(message, source, level)`.** Passing
  a level positionally as the second argument (`log(msg, "WARN")`) puts
  it in `source` and silently leaves `level="INFO"`, which routes to
  `logger.debug` and never surfaces. Most of the codebase passes a
  *source* tag there by convention (`"BIO"`, `"SYS"`, `"CRIT"`), so this
  is easy to get wrong. If a warning you added isn't appearing, this is
  why. Also: the bus renders the source tag itself, so don't put a
  literal `[TAG]` prefix in the message or it doubles up.
- **`struts.py` cannot import from the `spores` package at module
  scope.** `spores/__init__.py` imports `biome`/`genetics`/`memory`/
  `network`, all of which import `struts`. Any module-level
  `from spores.x import y` in `struts.py` closes the cycle. Use a
  function-level import (`_word_to_vector` does). `spores/embeddings.py`
  is deliberately written to import nothing from the project except
  `constants`, for the same reason.
- **`_load_index` and `bury()` in `spores/memory.py` must go through the
  same vectorization symbol.** They both stack into one `rank_bank`
  matrix, so any width disagreement is an immediate `vstack` ValueError,
  and a silent mis-scoring if the widths ever coincided. This was
  actually broken briefly: batching `_load_index` via `_words_to_matrix`
  made it bypass the `spores.memory._word_to_vector` symbol that several
  tests patch, producing a live 768d vector stacked against a mocked
  128d one. The fix is warm-the-cache-then-resolve: one batched call for
  the round trip, then per-word calls through the patchable symbol.
  Three regression tests in `tests/test_embeddings.py`
  (`StrataVectorConsistency`) cover exactly this.
- **Anything querying `CerebralIndex` must project through
  `CerebralIndex.embed()`.** A physics float and an embedding component
  are both `float`, so nothing in the type system objects to searching
  one space with a vector from another, it just returns garbage
  forever. This is `[DEC-10]`; the rule is procedural because it can't
  be enforced structurally.
- **Defensive style hides failures.** 875 `safe_get`, 506 `getattr`, 189
  `hasattr`, 87 broad `except` blocks. The engine almost never crashes;
  it silently degrades. Because the output is prose, a degraded
  subsystem is invisible, you cannot tell from reading a response
  whether the physics ran or swallowed an exception and returned
  defaults. When debugging, assert on state directly rather than
  inferring from output. Note this cuts against `conventions.md`'s
  "Fail loudly" rule, which the codebase does not consistently follow.
- **Two paths are dead code, deliberately left alone.** Worth knowing so
  a future session doesn't waste time or assume they work:
  - `HippocampalCache.encode()` is never called anywhere in production.
    The short-term cache is never populated, so
    `extract_for_consolidation()` always returns empty and the only
    route into the cortex is `mind.py`'s `context_queue`.
  - Shadow casting is gated on `scope > 0.6 or depth > 0.6`, so it fires
    only sometimes, and `cortex.last_shadow_nodes` persists between
    turns. Stale values there are expected, not a retrieval failure.
    Confirm retrieval by querying the index directly rather than by
    reading `last_shadow_nodes`.
- **Typographic Unicode is a live hazard in output paths.** `main.py`
  strips `_INVISIBLE_CHARS` and `spores/memory.py` has `_ZERO_WIDTH_RE`
  for a reason, and `brain/composer.py` instructs the model to limit
  em-dashes. Prefer plain ASCII punctuation in anything that reaches
  the terminal or a prompt.
- **`CerebralIndex` is in-memory only.** No `faiss.write_index` anywhere;
  vectors are always recomputed at boot from `raw_verbatim_text` /
  `word`. This is why the embeddings swap needed no migration, and it
  means changing the embedding model is a free operation, just restart.
- **The composed prompt is ~900 tokens** and is assembled as a single
  user message (no system role). If output quality changes
  unexpectedly, dump the prompt before blaming the model: monkeypatch
  `LLMInterface.generate` to capture its `prompt` argument.

## Style and working conventions (inherited, not project-specific)

These come from the T.R.S. handoff and apply the same way here.

- **Distinguish confirmed from suspected, in writing.** "Confirmed by
  running X" and "suspected, not verified" are different claims and the
  difference is the whole value of a handoff. Don't promote a hypothesis
  to a fact because it's been repeated.
- **Correct earlier over-claims explicitly rather than quietly.** If a
  previous session's note in this file turns out to be wrong, say so in
  place and say what was actually true. A confidently wrong note costs
  more than a missing one.
- **Verify against the running system, not the docs.** This repo's own
  documentation overstates what the code does in several places (see
  "Claims vs. code"). The same goes for `agents/domain_*.md`: they are
  good, but they describe intent.
- **Comments keep what/how/why and drop the narrative.** No references
  to this handoff file in source, no "confirmed via the user's testing",
  no blow-by-blow of how a bug was found. That detail belongs here or in
  git history, not in the code.
- **Match the surrounding code's idiom**, including its comment density
  and naming, even where it differs from personal preference. Follow
  the established precedent in the file being edited; if there's no
  precedent past one level for some construct, don't be the first.
- **Mark items done in place rather than deleting them**, with a short
  note on what was confirmed and how. Deleted context gets
  re-discovered the expensive way.
- **Don't reopen closed items unprompted.** Anything under "accepted
  as-is" is a decision, not an oversight.
- **Keep regression checklists next to the area they cover**, so picking
  the work back up cold has an obvious first move.

## Open items: what's actually left

**See `ROADMAP.md`** for the full plan behind these: three tracks
(Observability, the Creative Determinant, the Biological Harness) with
sequencing and the measurements behind each claim. The audits are
re-runnable rather than trusted: `python tools/audit_handlers.py`
(silent exception handlers, muted severity logs) and
`python tools/audit_safe_get.py` (runtime `safe_get` default hit-rate).
The short list below is what a session should know without reading it.

1. **Embedding calls are not metered into ATP.** Every other retrieval
   in the engine has a thermodynamic cost; `SemanticEmbedder` calls
   don't. This is a deliberate open question rather than an oversight:
   Constitution Article 2 says these costs are load-bearing, so
   arguably they should be. Not done because it's a tuning decision.
2. **The metabolic economy may be mistuned toward immediate death.**
   Observed in mock mode: three turns took ATP 60 → 0 and ROS 0 → 100.
   That may be an artifact of mock generation length and has **not**
   been confirmed against a real chat model, which is the first thing to
   check before changing any BIO constants. Flagged, not diagnosed.
3. **No `.gitignore`** (see Environment). Cheap to fix, mildly annoying
   until then.
3b. **25 `events.log` calls pass a severity where `source` belongs**, so
   they route to DEBUG and never display, including the daemon's own
   crash handler at `cycle.py:427`. See ROADMAP A1b. This is the reason
   to distrust "no errors appeared" as evidence of anything.
4. ~~`main.py`'s archetype fallback still carrying the `"THE "` prefix
   after the other four entries lost it~~, **done** in `7e90a74`.
   `main.py:182` now reads `mutations.get(self.boot_mode, "ARCHITECT")`.
   It was unreachable anyway (`boot_mode` is validated against
   `BonePresets.MODES` upstream), so this was cosmetic.
5. **Nothing else is known-broken.** If picking this up cold, the sanity
   check is: make a venv, run the suite, expect 306/2/2 with those two
   specific environmental failures; then boot headless in mock mode and
   confirm `/status` reports the Arcade as nominal (not `DEGRADED`)
   with Ollama up.

## Future ideas (not started, no urgency)

- **Affective retrieval, done properly.** Querying memory by physics
  state ("find memories that felt like this moment") is a genuinely good
  idea and is what the old broken code accidentally gestured at. Doing
  it right means storing an affective vector *alongside* the semantic
  one and searching that index deliberately, see the WHY NOT block in
  `[DEC-10]`.
- **Shrink to what actually carries the value.** The composer, the
  validator, and the physics-to-prompt mapping produce nearly all of the
  observable behaviour. A smaller engine built from just those, with the
  embeddings work kept, would be easier to defend and easier to explain
  than the current surface area. Raised as an option, not a
  recommendation; the current breadth is clearly part of the point.
- **Reconcile `conventions.md`'s "Fail loudly" with the actual
  defensive style.** Right now the document and the code disagree, and
  the code wins by 87 broad excepts. Either is defensible; the
  disagreement isn't.
