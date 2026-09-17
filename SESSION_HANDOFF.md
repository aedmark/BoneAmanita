# Session handoff: BoneAmanita & The Hypervisor

Paste this into a fresh context window to resume. Written at the point
where `ROADMAP.md` is complete apart from C5: every subsystem the document
listed as disconnected is now connected, and what remains is one
measurement against a live model rather than any more building.

Structure and working conventions here are inherited from the T.R.S. →
SCI0 handoff (`/home/gordonk/RiderProjects/TRS_SCI/SESSION_HANDOFF.md`);
the project-specific content is obviously all BoneAmanita's. Where that
file and this one describe the same working habit, they should stay in
sync, those habits are not project-specific.

## Start here if you are cold

`README.md` explains what BoneAmanita is in plain language, with no
jargon and no assumption that you remember how any of it works. Read that
first if you have been away; this file assumes you already have the
shape of the thing in your head.

**The next task is C5**, and its full brief is in this file under "Next
session: C5, and it is a different kind of work". It is a measurement, not
a build, and it is the only remaining item on `ROADMAP.md`. Read that
section, the C5 entry in `ROADMAP.md`, and `tests/test_physics_to_prompt.py`
(which is the rig to copy), in that order.

Before starting anything, run the suite and the audits. The numbers in this
document are re-derivable on purpose and should never be taken on trust:

```bash
.venv/bin/python -m pytest -q                      # expect 484 passed, 5 skipped
.venv/bin/python tools/audit_receipts.py           # which subsystems did real work
.venv/bin/python tools/audit_handlers.py           # 28 silent, 3 pass-only
.venv/bin/python tools/audit_physics_inputs.py     # vocabulary coverage, zone spread
```

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

- **Test suite: 484 passed, 0 failed, 5 skipped**, about three minutes. Green.
  Needs `ordvec` from PyPI and `mistral-nemo` in Ollama. The skips are
  live-backend tests behind `BONE_EMBED_LIVE_TEST=1`; run with that set
  when touching embeddings or the resonance classifier.
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
- **The Mnemonic Arcade does real associative recall**, exact and
  semantic, scoped to zones, with short-term memory feeding REM
  consolidation and cortisol genuinely amputating it.
- **The Creative Determinant steers generation.** Project Navi's math
  drives ATP/ROS, and the nonlinear elliptic BVP is solved each turn by
  Picard iteration over the Laplacian of a memory subgraph. The solution
  sets target voltage and drag; its principal eigenvalue, taken as a
  Rayleigh quotient, selects the macro policy and gates sampling
  temperature.
- **Word resolution is 81% unguessed**, up from 13%: grammatical filler,
  the curated lexicon plus inflections, embedding resonance, then a
  last-resort spelling guess at under 3%.
- **Failures are visible.** Crashes surface with tracebacks, missing
  config is named at boot, a degraded embedder announces itself in
  `/status`.
- **Failures are not swallowed.** Silent exception handlers went from 72
  to 28, and handlers whose entire body is `pass` went from 30 to 3, each
  of those three named in an allowlist with a written reason. Background
  tasks on the async pool now report their own exceptions, which they
  previously discarded into an unread Future.
- **The physics actually reaches the prompt now.** Until C3 it did not:
  `PhysicsPacket.to_dict()` emitted only the nested shape while every
  consumer read flat, so sixteen measured fields never arrived and a turn
  measuring contradiction 1.0 composed a prompt saying 0.40. Every
  physics-driven directive read a hardcoded default instead.
- **The engine can decline to answer.** More than one voice triggered at
  once is Tension, and the Stage Manager negotiates it before anyone
  speaks: it pairs them if a fusion exists, and holds otherwise. A held
  turn sets `refusal_triggered` in `ArbitrationPhase`, which runs
  immediately before `CognitionPhase`, so the model is never called. The
  packet is typed `SILENCE` with `is_alive: True` and is deliberately not
  built through `_build_refusal`, because a refusal is something being
  rejected and this is the engine declining to speak yet. Every verdict
  carries a mandatory reason, and negotiation is deterministic.
- **The engine co-regulates, in the right direction.** The user model
  carries two separate signals now. `P_u` is effort spent, so long messages
  drain it and that is what makes the engine offer to carry part of the
  load. `E_u` is disengagement, measured against this person's own recent
  baseline plus repetition, and it is what shortens the engine's replies.
  It used to be one signal pointing the wrong way: writing at length made
  the engine read you as exhausted and cut its answers to three sentences,
  while "ok, sure, fine" restored you to full. The model persists across
  sessions, files a receipt, and shows in `/status` as "You: steady /
  tiring / flagging". All the constants are in `BoneConfig.USER`.
- **Physics reaching the prompt is pinned end to end.**
  `tests/test_physics_to_prompt.py` asserts that each measured state
  produces its specific directive and, just as importantly, that a calm
  state produces none of them. Thresholds are read from `BoneConfig` so
  retuning a constant moves the tests with it.
- **Subsystems issue receipts.** Seven of them record what they were
  handed and what came back, every turn, in their own voice. `/diag`
  prints the turn's receipts plus anything silent, chronically degraded
  or chronically empty; `tools/audit_receipts.py` prints the same table
  without booting the organism. `result_count` and `degraded` are set by
  the code that did the work, never by its caller and never inferred from
  whether an exception was raised.
- **The `agents/` docs are unusually disciplined.** `constitution.md`
  with explicit "WHY NOT" blocks is better design documentation than
  most commercial codebases have. They are load-bearing: read them
  before touching anything, in the order `agents/prompt.md` specifies
  (constitution, conventions, glossary, then domain_*).

## What changed most recently

Work landed in this order. `ROADMAP.md` has the detail and the
measurements; this is the shape of it.

1. **B1, the Creative Determinant went live.** `<cd_lambda_1>` had a
   parser in `LLMInterface.generate` and no producer, so the thermal
   lock was dead. Wiring it exposed two deeper faults: `gamma` and `mu`
   were computed by the observer and dropped, because only `kappa` was
   in `ObservationPhase._SYNC_KEYS`; and the `(pi/L)^2` term with L
   defaulting to pi made the constant exactly 1.0, putting the coherent
   regime out of reach for every state the engine could produce. Lambda
   is now `-beta*b` (Theorem 3.16 stated directly), the contradiction
   weight ships at 0.5 in `BoneConfig.CD`, and a real turn measurably
   opens heat.
2. **A1b, severity logs unmuted.** 25 call sites passed a severity where
   `source` belongs, routing them to DEBUG. Including the daemon's own
   crash handler, which formatted a full traceback and discarded it.
3. **A1, strict config.** Ten constants existed in no config file. Every
   subsystem reading them used an inline fallback, so tuning them did
   nothing, forever. Promoted at their existing values, with a boot-time
   audit that names any miss.
4. **C1, the hippocampus.** Three faults stacked: no writer at all, then
   all three `get_graph()` consumers asking for a `.adj` attribute the
   method never returned, then an edge threshold calibrated for hash
   vectors and therefore above every similarity real embeddings produce.
5. **Retrieval, both paths.** `retrieve_semantic` had no caller either,
   so exact recall was reachable only through dead code.
6. **C2, zones.** `wing_id` read a key defined nowhere, the query side
   never set it, and the Doorway Effect had no caller.
7. **B3, the CD solve.** `_sync_ordvec_indices` built its ordvec indexes
   with the wrong constructor (`SignBitmap(matrix)` where a dimension is
   expected, and `bits=8` which ordvec rejects), so every call raised,
   `regulate()` caught it, and the engine ran a plain PID controller
   under the name of a PDE for the life of the project. Fixed; first real
   solve gave lambda_1 = -0.4196 over 23 memory nodes. The thermal lock
   now uses that instead of the scalar approximation B1 wired in.
8. **A5 and A6, the physics inputs.** The largest finding, and the only
   one that was not a disconnected wire. See below.
9. **A3, receipts.** `receipts.py` plus instrumentation in seven
   subsystems. It found two live bugs on its first real turn, which is
   the whole case for it. The bigger one: `cycle.py` never handed
   `regulate()` the utterance it already had, scraping one instead out of
   a dialogue buffer that is not written until after the model has
   replied, so the Creative Determinant had been anchoring its subgraph
   on the PREVIOUS turn every turn, and on nothing at all on the first
   turn of a session. B3 fixed the solve; this was the separate question
   of what it was solving about. The smaller one: `_sync_ordvec_indices`
   returned a bare `False` for four different conditions and its only
   caller ignored it, so an empty memory surfaced as an `AttributeError`
   on a `None` index. Each case now raises with its own name.
10. **A2, the silent handlers.** 72 to 28; handlers whose whole body is
   `pass` went 30 to 3, each named in an allowlist with a reason. It found
   the thirteenth dead subsystem: `TheTinkerer` has no `to_dict` and no
   `load_state`, and `gather_state` called `tinkerer.to_dict()` inside a
   handler that caught the AttributeError and substituted `{}`. One
   missing pair of methods killed three paths at once (the composer's
   HARMONIC RESONANCE block never rendered, tool resonance never saved,
   and never restored). It also found that the async pool in `cycle.py`
   was a silent-failure sink with no handler in it at all: four
   fire-and-forget `submit()` calls whose exceptions went into a Future
   nobody read. That is worse than `except: pass`, because there is no
   handler for an audit to find.

**A5/A6 is the one to understand if you read only one.** Word category
counts drive every number in the engine. They came 82% from a
phonosemantic classifier that thought two thirds of English was "play",
which saturated one dimension and pinned every conversation to one zone.
Fixed in two passes: calibrate the classifier and the thresholds, grow
the lexicon, normalise the dimension and the zone selection; then close
the function-word class, add morphological lookup, and resolve what
remains by embedding resonance. Word resolution went from **13% to 81%**
without guessing.

Everything else this week was reconnecting something already built.
A5/A6 was connected, running, and confidently wrong, which is why it
survived so long: nothing looks broken when the output is prose.

## The pattern worth carrying forward

Twelve subsystems were found doing nothing while looking healthy. None
produced an error, a log line, or a failing test, and they could not
have: **the only output is prose, and prose looks identical whether the
physics ran or quietly returned defaults.**

Three habits came out of that and are worth keeping:

- **A fix often uncovers a second fault that was hiding behind it.** The
  hippocampus was three deep. Do not assume one repair finishes an area;
  re-measure end to end with real values afterwards.
- **A passing test can encode a bug.** `test_terminal_topology_collapse`
  mocked a contract that never existed, matching production's own wrong
  assumption. When a test breaks after a contract fix, check which side
  was actually wrong before "fixing" the code back.
- **Calibration constants outlive the thing they were calibrated for.**
  The 0.75 edge threshold, the 0.6 play threshold, the `(pi/L)^2` term
  and the 80% recall assertion were all correct once and silently wrong
  later. When a mechanism is inert, suspect its constants before its
  wiring.
- **Two objects modelling the same thing will disagree in silence.**
  `SymbiosisManager` and `SharedLatticeDriver` each held their own
  `UserInferredState`. Only the lattice's reached the prompt, so every
  reading Symbiosis made was discarded, while it wrote `beth`, `phi` and
  `beta_index` onto the packet from a model nothing agreed with. They share
  one object now via `attach_lattice`. When you find a second copy of a
  model, find out which one is load bearing before assuming both are.
- **A method called from two places must say whether calling it twice is
  free.** `infer_and_couple` runs once from `ObservationPhase` and again
  from `_execute_core_cycle`. That was harmless while it only read state,
  and became a bug the moment it started learning: it drained stamina twice
  and found each message already in its own history, so every utterance
  scored as a repeat of itself. Learning is now idempotent per turn, keyed
  on the receipt ledger's turn counter.
- **System turns are not the person speaking.** The boot prompt runs
  through the lattice like any other turn and is hundreds of words long. It
  was being learned as "your normal message length", so everything you
  actually typed measured short against it. Anything that learns from input
  needs `is_user_turn`.
- **Attribute access working proves nothing about serialization.**
  `packet.exhaustion` resolved correctly through the alias map the whole
  time; only `to_dict()` was wrong, and every test touching the attribute
  passed. When a value is computed correctly and has no effect, check the
  boundary it crosses, not the arithmetic.
- **A test that builds its own fixture steps over the bug.** The A4 tests
  hand the composer a flat dict directly, which is exactly the shape the
  broken serialization failed to produce. They proved the gates correct and
  could never have proved the values arrive. At least one test per contract
  has to travel the real path.
- **`matter` is never flattened onto the physics dict.** `CognitivePhase`
  writes every key back onto the packet with `setattr`, and a Counter fed
  through that round trip gains a tuple wrapper each turn until the word
  tally reads `Counter({((('play', 1), 1), 1): 1})` and measures nothing.
  Only `energy` and `space` are projected flat. There is a test.
- **Mutation test anything that guards a contract.** Five deliberate
  breaks were put into `brain/composer.py` to check the A4 tests were load
  bearing. Four failed immediately; the fifth passed, because the test was
  asserting on a `mood_override` it had passed into the state dict when
  `compose()` takes it as an argument. The test described the contract
  without holding it, which is this document's own subject reproduced
  inside the test written to prevent it. Break the code on purpose before
  trusting a green test.
- **`exhaustion` is the USER's, not the engine's.** `cycle.py` assigns
  `ctx.physics.exhaustion` from `ctx.user_state`. The engine's own
  depletion reaches the prompt through respiration
  (`raw_cost > BIO.ANAEROBIC_THRESHOLD` becomes a prose directive), which
  is a separate path across three modules. Both are real; the variable
  name tells you the wrong one.
- **A subsystem that declines to act must say so.** Silence cannot
  distinguish "correctly gated off" from "dead code", and the second one
  is what this whole document is about. `cortex.recall` now issues a
  receipt on its skip path naming which condition stopped it. Copy that
  wherever a guard returns early.
- **Check whether a handler can fire at all before arguing about it.**
  Two `except ImportError` blocks guarded code containing no import; the
  imports were at module scope. A handler that cannot fire is not
  protection, it is decoration, and it reads as protection to everyone
  after you.
- **A guard next to an identical unguarded call is superstition.**
  `self.svc.bio.mito.adjust_atp(...)` was wrapped in
  `except (TypeError, AttributeError)` eight lines above a bare call to
  the same method on the same object. When you find one of these, the
  unguarded copy is the evidence.
- **Fire-and-forget on an executor is the quietest failure available.**
  `ThreadPoolExecutor.submit` parks the exception in a Future and drops it
  if nobody calls `.result()`. There is no `except` for an audit to count
  and no line to point at. `GeodesicOrchestrator._submit_background`
  attaches a done-callback that logs the traceback; use it rather than
  `self._async_pool.submit` directly.
- **A fault that becomes flavour text is the worst outcome, not the
  kindest.** Catching an AttributeError and returning "The Parliament
  doors are sealed" makes the bug indistinguishable from content, in a
  system whose only output is prose. If a barrier must stay, it logs.
- **Collapsing several conditions into one return value throws away the
  diagnosis.** `_sync_ordvec_indices` returned a bare `False` for four
  unrelated problems and its only caller ignored it. Prefer a named
  exception per condition; the cost is one line and the payoff is a
  receipt that reads as a state rather than a stack trace.

## Earlier: real embeddings

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

## Claims vs. code (read before trusting `credits.txt`)

`readme.txt` is gone: it was the theatrical version, and `README.md` now
carries the plain-language account instead. Its memory section and the
embeddings dependency notes had been corrected before it was retired.
These remain overstated elsewhere and a future session should not treat
them as a specification:

- **Verification belongs to Spence's libraries, not to us.** `ordvec` is
  Lean 4 verified ([ordvec-formalization](https://github.com/Project-Navi/ordvec-formalization),
  declared in its package metadata) and the Creative Determinant has its
  own formalisation. BoneAmanita's Python implementation of those
  equations carries no proofs. `credits.txt` and `docs/README.MD` used to
  claim the verification for this repo; corrected, along with a note in
  each that the overstatement was ours. Do not re-inflate it, and do not
  overcorrect to "no verification involved" either, which is equally
  wrong.
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
  `ordvec` IS on PyPI and installs cleanly (`pip install 'ordvec>=0.5.0'`,
  version 0.5.0): it is Nelson Spence's, still published, and ships as a
  compiled abi3 wheel that works on Python 3.14. Install it; the suite is
  not fully green without it. `dspy` is still not installed here, stays
  optional, and the engine degrades cleanly without it (`[DSPY OFFLINE]`
  prints at import; epigenetic learning and the DSPy critic do not run).
- **Ollama runs on `127.0.0.1:11434` with both models pulled**:
  `nomic-embed-text:latest` (768d, used for memory) and
  `mistral-nemo:latest` (chat, matching `BoneConfig.MODEL`). Both are
  needed for a green suite.
- A dimension-mismatch `ValueError` from
  `np.vstack` in `tests/test_memory.py` means the boot-load and `bury()`
  vector paths have diverged again (see Findings).
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
- **A fix can uncover a second fault that was hiding behind it.** The
  hippocampus is the clearest case: it had no writer, which hid the fact
  that all three `get_graph()` consumers asked for a `.adj` attribute the
  method never returned, which in turn hid an edge threshold (`0.75`)
  calibrated for hash vectors and therefore above every similarity real
  embeddings produce. Three layers, each invisible until the one above it
  was repaired. Expect this pattern; do not assume one fix finishes an
  area. Re-verify end to end with real values rather than unit-testing
  the layer you touched.
- **A passing test can encode a bug.** `test_terminal_topology_collapse`
  mocked `get_graph()` as an object exposing `.adj`, matching what
  `cycle.py` asked for and not what `HippocampalCache` has ever returned.
  Production and test shared the same wrong assumption, so the suite was
  green while the real path was dead. When a test breaks after a
  contract fix, check which side was actually wrong.
- **Exact and semantic recall now both run** through
  `TheCortex._recall`, which calls `MycelialNetwork.retrieve_semantic`.
  The exact path is keyed by `MycelialNetwork.room_key(clean_words)` and
  **write and read must derive that key through that one method**; if
  they drift, the cache fills and never hits, which is the same silent
  failure this codebase specialises in.
- **Still dead, deliberately**: shadow casting is gated on
  `scope > 0.6 or depth > 0.6`, so it fires only sometimes and
  `cortex.last_shadow_nodes` persists between turns. Stale values there
  are expected, not a retrieval failure. Confirm retrieval by querying
  the index directly.
- **The physics inputs are calibrated, and the calibration is fragile.**
  Word-category counts drive every number in the engine. They came 82%
  from a phonosemantic fallback classifier that thought two thirds of
  English was "play" (ROADMAP A5, now fixed). Before touching
  `lore/lexicon.json`, `lore/linguistics.json`, `classify_word`, or the
  dimension formulas, run `python tools/audit_physics_inputs.py` and
  compare against the table in A5. `tests/test_physics_inputs.py` guards
  the invariants: the fallback stays a minority, no single category
  dominates it, DEL does not saturate, and at least three zones stay
  reachable.
- **Word resolution has four stages, in trust order**, and the order
  matters: grammatical filler (`SOLVENTS`), the curated lexicon plus its
  inflections, semantic resonance against embedding centroids, then the
  phonosemantic guess. 81% of ordinary English now resolves without
  guessing, up from 13%.
  - **A word with a semantic category must never be a solvent.** The
    solvent check runs first, so a word in both loses its category
    silently. `i`/`me`/`we` are the `meat` mass key, `not`/`never` are
    negation, `very`/`really` are intensifiers, `none`/`without` are the
    `void` mass key. There is a test.
  - **Machine-learned words go to `teach()`, never `register_word()`.**
    `teach` fills the separate capped `LEARNED_VOCAB` hive
    (`saves/cortex_hive.json`); `register_word` writes `lore/lexicon.json`
    and would make guesses indistinguishable from your curation. Delete
    the hive to revert everything the engine has learned.
  - **Embedding margins need mean centring.** Raw single-word embeddings
    share a large common component, so everything resembles everything
    and margins collapse to ~0.03. This is the same compression that made
    the 0.75 hippocampus edge threshold wrong. Gate on margin, never on
    absolute similarity.
- **There are two lambda_1 values; make sure you know which one you have.**
  `ctx.physics.lam1` (and `energy.lam1` in the serialized packet) is the
  real one: a Rayleigh quotient over the memory subgraph Laplacian from
  the governor's Picard solve. `PhysicsPacket.get_principal_eigenvalue()`
  is a scalar over three per-turn values that states the same sign
  condition and cannot see memory structure. The cortex prefers the
  solved one and records which it used in `cd_lambda_1_source`. The
  governor runs at `cycle.py:705`, before `run_simulation`, which is why
  the value is available to the composer at all; it used to surface only
  in the post-turn snapshot, too late to matter.
- **A mass key with no lexicon category is silently always zero.**
  `social` and `void` were weighed by `_weigh_mass` and had no category,
  so BET was structurally zero for the life of the project. There is now
  a test that every `GeodesicEngine._MASS_KEYS` entry exists in the
  lexicon. Adding a mass key means adding its words too.
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

- **No em dashes.** Gordon's explicit preference, in chat, in repo
  documents, in code comments and in commit messages. Use commas,
  semicolons or parentheses; if a sentence only works with a dash it
  usually wants to be two sentences. He does not type them, so they read
  as not-his-voice in his own repo. This is also already the project's
  own rule: the Hypervisor v7 Lexical Firewall says "certainly no em
  dashes unless it is academically required", and `brain/composer.py`
  instructs the model to limit them. Earlier drafts of `ROADMAP.md` and
  this file were full of them, which contradicted the system's own axiom.
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

## Next session: C5, and it is a different kind of work

**Everything else on `ROADMAP.md` is done.** Tracks A and B are finished,
and C is finished apart from this. C5 is not a build task; it is a
measurement, and it is the only item in the whole document that cannot be
settled against mocks.

### The claim being tested

At low metabolic headroom the engine tells the model to change how it
writes. Two directives do this, and `tests/test_physics_to_prompt.py`
already proves both reach the prompt:

| Trigger | Directive |
|---|---|
| `respiration == "ANAEROBIC"` | "Current Biology: ANAEROBIC STATE. Raw, breathless, efficient prose." |
| `exhaustion > 0.8` | "CRITICAL: You are exhausted. You must conclude your thought in 3 sentences or less." |

Those tests assert the instruction **arrives**. They say nothing about
whether the model **obeys**, and that is the whole of C5. If the effect is
not measurable then the somatic layer is decoration, and either the
instruction needs strengthening or `README.md` and `credits.txt` need their
claims softened. Both are acceptable outcomes. Finding no effect and saying
so is a success.

### Preconditions, all currently satisfied

- `mistral-nemo:latest` (7.1GB) and `nomic-embed-text:latest` are pulled and
  Ollama answers on `http://localhost:11434`. `gemma4:e4b` is also present if
  you want a second model to check the effect is not one model's quirk.
- `BoneConfig.MODEL` is `mistral-nemo`, `PROVIDER` is `ollama`.
- `BIO.ANAEROBIC_THRESHOLD` is 40.0, `BIO.ATP_STARVATION` is 5.0.

### The experimental design, and the three traps in it

**Do not A/B by running real turns.** The engine's state is coupled: driving
ATP down also moves voltage, drag, contradiction and the zone, so a low-ATP
turn differs from a high-ATP turn in a dozen ways at once and the somatic
directive is not the variable you measured. Compose both arms from the
**same state dict**, changing only `bio["respiration"]` (and/or
`physics["exhaustion"]`), then call the model on both with the same user
message. `PhysicsToPromptCase.compose_with` in
`tests/test_physics_to_prompt.py` is the rig to copy.

**Pin the temperature, and know why.** `LLMInterface.generate` reads a
`<cd_lambda_1>` tag out of the prompt and OVERRIDES whatever
`params["temperature"]` you passed: positive lambda forces 0.0, negative
opens heat proportional to the magnitude. If the two arms carry different
tags they are sampled differently and the comparison is void. Either strip
the tag from both and pass an identical `params`, or ensure both carry the
same value. Stripping is cleaner for isolating the instruction; keeping the
real tag measures the deployed behaviour instead. They answer different
questions, so pick one deliberately and say which in the writeup.

**Call `llm.generate` directly, not through the cortex.** The
`ResponseValidator` discards a reply containing a banned phrase and asks
again, so going through the full path silently resamples some responses and
biases whichever arm trips it more often.

### Measuring it without adding a dependency

There is no POS tagger in the tree and none of the 35 lexicon categories is
adjectival, so "adjective density" as the roadmap words it has no cheap
exact implementation. Constitution Article 1 says do not add a framework for
this. Suggested approach: measure several coarse proxies rather than one
fragile precise one, and report them separately.

- Mean sentence length in words. This is the primary measure and the one the
  "3 sentences or less" directive speaks to most directly.
- Mean word length in characters.
- Type-token ratio.
- Commas per sentence, as a clause-density proxy.
- A suffix-based adjective proxy (`-ous -ful -ive -al -ic -less -able -ible
  -ish -y`), reported as a proxy and never as a count of adjectives.

**Apply the project's own quality gate.** `navi-fractal` refuses to return a
dimension when R squared says the data will not support one, and that habit
is the single most useful thing this codebase has taken from Project Navi.
Do the same here: compute an effect size with a confidence interval across
repeats, and decline to declare an effect whose interval crosses zero. A
measurement that reports "no detectable difference, n=120, CI [-0.4, 1.1]
words per sentence" is worth far more than one that reports a number it
cannot stand behind.

### The rig, smoke tested against the live model

These are the moves, confirmed working against `mistral-nemo` on
2026-09-17. Both arms come from one state dict and differ in one field:

```python
composer = PromptComposer({"system_prompts": eng.prompt_library, "lenses": {}})
llm = eng.cortex.llm

for arm in ("RESPIRING", "ANAEROBIC"):
    eng.cortex.active_mode = "CONVERSATION"
    state = eng.cortex.gather_state({"physics": {"voltage": 30.0}})
    state.setdefault("meta", {})["active_mode"] = "CONVERSATION"
    state["bio"] = {"respiration": arm}
    prompt = composer.compose(state, msg, modifiers={"include_inventory": False})
    # Strip the thermal lock so both arms sample identically.
    prompt = re.sub(r"\n?<cd_lambda_1>[-\d.]+</cd_lambda_1>", "", prompt)
    assert ("ANAEROBIC STATE" in prompt) == (arm == "ANAEROBIC")
    reply = llm.generate(prompt, {"temperature": 0.7, "top_p": 0.95, "max_tokens": 220})
```

The assertion is worth keeping. It is the cheap guard that the arms are
actually distinct, and without it a silent change to the bio block would
turn the whole experiment into a comparison of a thing against itself.

### One preliminary observation, which is NOT a result

The smoke run was two messages per arm, one repeat, at temperature 0.7.
That is four generations from a 7B model and it is noise, not evidence.
Recording it only because of which way it pointed:

```
RESPIRING: mean words/sentence = 4.1
ANAEROBIC: mean words/sentence = 9.2
```

ANAEROBIC, the arm told to write raw, breathless and efficient prose,
produced sentences **more than twice as long**. If that survives a properly
powered run, the finding is not "the instruction has no effect" but "the
instruction has the opposite effect", which is a different and more
interesting problem: a directive about being breathless may be read as a
licence for atmosphere rather than an instruction to compress.

Design the experiment to be able to detect a reversal, not just an absence.
A one-sided test or a measurement that reports only the magnitude of a
difference would miss this entirely. Report the signed effect.

### Sizing

One sample per arm is noise; a local 7B model is not deterministic even at
low temperature. Something like 10 to 15 user messages, varied in length and
register, times 4 or 5 repeats, times 2 arms, so roughly 100 to 150
generations. At a few seconds each that is well under an hour of wall clock.
Cache the raw generations to disk so the analysis can be rerun without
regenerating.

### Where it should live

`tools/audit_somatic.py`, matching the other audits, so it is re-runnable
rather than a number someone once wrote in a document. If it produces a
durable result, add a gated test behind an env var in the style of
`tests/test_embeddings.py` (`BONE_EMBED_LIVE_TEST`) rather than in the main
suite, since it needs a live model and takes minutes.

### When it is done

Update `ROADMAP.md` C5 with the measurement, and then reconcile the claims
in `README.md` (the "Honest limits" section already flags this as untested)
and `credits.txt`. If the effect is real, say how large. If it is not, say
that plainly and soften the claim. The precedent for this is B4 and the Lean
4 correction: the overstatement was ours and the fix was to write down that
it was ours.

## Open items: what's actually left

**Read `ROADMAP.md` A3 before proposing any "cannot fabricate" or
provenance mechanism.** It records why "require a non-model source" is a
dependency declaration rather than a governance mechanism, and the three
conditions (a mechanical oracle, a source-admission boundary the model
cannot cross, and serialization across check/verify/commit) that would
have to hold first. The short version: validation at nomination time is
an optimization, validation at commit time is the guarantee.

**See `ROADMAP.md`** for the full plan: three tracks (Observability, the
Creative Determinant, the Biological Harness) with sequencing and the
measurement behind every claim. The audits are re-runnable rather than
trusted:

```bash
python tools/audit_handlers.py         # silent handlers, muted severity logs
python tools/audit_safe_get.py         # runtime safe_get default hit-rate
python tools/audit_physics_inputs.py   # how much vocabulary the engine knows
python tools/audit_receipts.py         # which subsystems reported real work
```

The short list below is what a session should know without reading it.

1. **Embedding calls are not metered into ATP.** Every other retrieval in
   the engine has a thermodynamic cost; `SemanticEmbedder` calls do not,
   and word resolution now makes them on novel words too. Constitution
   Article 2 says these costs are load-bearing, so arguably they should
   be. Left alone because it is a tuning decision, not a repair.
2. **The metabolic economy may be mistuned toward immediate death.**
   Observed in mock mode: three turns took ATP from 60 to 0 and ROS from
   0 to 100. That may be an artifact of mock generation length and has
   **not** been confirmed against a real chat model, which is the first
   thing to check before changing any BIO constants. Flagged, not
   diagnosed.
3. **No `.gitignore`.** See Environment. Cheap to fix, mildly annoying
   until then.
4. **About 16% of ordinary English stays unresolved, on purpose.** Nobody
   knows all of English, and an engine that pretends to is the failure
   this layer was rebuilt to escape. Add roots to `lore/lexicon.json` if
   you want the number lower, and watch it with the physics audit. Do not
   close the gap by loosening a threshold.
5. **Receipts are honest about work, not about correctness.** A receipt
   saying `retrieved 3` from a semantically meaningless index is true and
   still useless. They make the engine auditable, not right. Closing that
   gap is A4, the state-asserting tests, which is not done.
6. **Nothing else is known-broken.** Picking this up cold: make a venv,
   install including `ordvec`, pull both Ollama models, run the suite and
   expect **484 passed, 0 failed, 5 skipped** (the skips are live-backend
   tests behind `BONE_EMBED_LIVE_TEST=1`). Then boot headless in mock
   mode, confirm `/status` reports the Arcade nominal rather than
   `DEGRADED`, and run `/diag` to see the turn's receipts.

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
