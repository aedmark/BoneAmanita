# Testing: how the BoneAmanita-vs-baselines evaluation actually works

This is the reference for `tools/audit_somatic_*.py`, `tools/build_blind_panel.py`
and `tools/somatic_sim_user.py`: what each one does, how they chain together,
the caches they read and write, and the mistakes already made and fixed so a
new session or a different team doesn't re-make them. `SESSION_HANDOFF.md` is
still the log of what happened and when; this is the standing reference for
how to run it again. `ROADMAP.md` is the project's own status; this file
assumes you've read enough of it to know what "the Somatic Contract" is.

The question this pipeline answers: **compared to a bare model, and to a bare
model with one friendly instruction, does the full engine's state-driven
prompting actually produce replies a person would rather receive?** Everything
below exists to answer that honestly instead of flatteringly.

## The pipeline, end to end

```
1. GENERATE   audit_somatic_census.py   -> the engine's own replies, one topic, one run
              audit_somatic_vanilla.py  -> a bare-model arm and a one-line-prompted arm,
                                            same topic, same script
                    |
                    v  (all three, or four with --arm textbook, now on disk as *.jsonl)
2. JUDGE      audit_somatic_blind_judge.py --control null|samples|mismatch|textbook
                    |            -> is this judge worth trusting at all? (do this FIRST)
                    v
              audit_somatic_blind_judge.py                (no --control)
                    |            -> the actual three-way ranking, blind, shuffled
                    v
3. HUMAN READ build_blind_panel.py + blind_panel_template.html
                    |            -> a page a person reads blind and picks from,
                    v                then reveals the judge's numbers alongside their own
4. RESPONSIVE (parallel track, newer) replaces step 1's fixed script:
              somatic_sim_user.py + audit_somatic_responsive.py
                    |            -> each system is answered by a simulated person who
                    v               reacts to what that system actually said
              audit_somatic_blind_judge.py --responsive   -> judges the drifted conversations
```

A fixed-script run (steps 1-3) and a responsive run (step 4) are two different
experiments sharing the same generator code, judge code and topics. Run both;
they answer different questions (see "Scripted vs. responsive" below).

`audit_silence_diagnostic.py` is a sibling, not part of the scoring chain: a
debugging tool for *why* a turn went silent, used when a census run holds a
turn and it's unclear whether that's a real distress-shield behaviour or a
silent failure.

## Topics: what they are and the rule for adding one

Six scripted conversations live in `audit_somatic_census.py`'s `SCRIPTS` dict:
`sailboat`, `marathon`, `friendship`, `promotion`, `lease`, `toast`. Every one
is 30 turns in the same shape — `engaged`(8) `tiring`(6) `flagging`(6)
`distressed`(5) `recovering`(5) — a different life topic and a different loss
each time (a boat, a race, a friendship, a job offer, a lease, a wedding
toast), written so the *events* are fixed but nothing about the wording
repeats between topics. That shape exists so results are comparable
turn-position-to-turn-position across topics, and so every topic guarantees a
run through the actual distressed stretch the engine's gates are meant to
handle. **A new topic should keep this shape** (same phase counts, a real
5-turn distressed stretch with no external villain — the distress should come
from something the person did or feels, not a crisis inflicted on them) and
should be composed fresh, never derived from an existing topic's wording, or
it isn't a real second sample.

`somatic_sim_user.PERSONAS` and `PHASE_FEEL` extend each topic for the
responsive track; adding a topic to `SCRIPTS` without adding a matching entry
to `PERSONAS` makes `SimulatedUser` raise a `KeyError` at first use.

## Scripted vs. responsive: why both exist

The scripted comparison (steps 1-3) replays the *same fixed message* to all
three systems regardless of what any of them replied. That's necessary for a
blind three-way judge (all three systems must answer literally the same
prompt to be ranked against each other) but it can't show what a *stateful*
engine is for: a person's own state shifting because of what was said to
them. It also hands every system a conversation history it didn't shape.

The responsive track (`somatic_sim_user.py`, `audit_somatic_responsive.py`)
answers a different question: run alone, each system is answered by a
simulated person who reacts to *that system's own* replies, so the three
systems' conversations drift apart. The fixed *beat* (what the old script
line said) becomes an intent, not verbatim text; only the opening line, the
phase sequence and the underlying events stay fixed. `--responsive` on the
judge then compares each system's own drifted conversation rather than one
shared history, and (unlike the scripted comparison) scores a held turn as a
loss rather than excluding it, since silence in a live back-and-forth is a
real, worse outcome, not a missing data point.

The simulated person is itself an LLM (default `qwen3.5:9b`, a different
family from every responder tested) playing a fixed persona. Read anything it
reports — reply preferences, the exit interview — as **one LLM's account,
useful for comparing arms against each other since the same simulator answers
all of them, not as a measurement of a real person's reaction.**

## Tool reference

### `audit_somatic_census.py` — the engine's own replies

Boots a real `BoneAmanita` engine (persistence patched off: no lexicon,
checkpoint, spore or Akashic writes), drives it through one scripted topic,
and logs every turn to `tools/cache/somatic_census.jsonl`: what the composed
prompt actually carried (exhaustion, telemetry, mood line, which somatic
directives fired), the person model's state, the engine's own metabolism
(ATP, ROS, health), and a full per-turn ATP/health ledger (every write, who
made it, why). `--report-only` re-derives the printed statistics from the
cache without a live run. `report()` is the fastest way to sanity-check a run
without reading raw JSONL: phase-by-phase person state, prompt contents, where
ATP and health actually went, and what the refusal gates (`PINKER`, MOOG,
crucible) were reading turn by turn.

`run()` takes an optional `user=` (a `somatic_sim_user.SimulatedUser`) and
`max_turns=`; without `user`, turns are replayed verbatim from the script
(the normal scripted-comparison mode). With `user`, each message is generated
in reply to what the engine actually showed, and the record gains `arm`
(always `"bone"`), `beat`, `shown`, `delivered`, `sim_fallback` — fields that
**do not exist** on a plain scripted run, so don't filter `somatic_census.jsonl`
rows by `arm` unless you know they came from a responsive run (check
`somatic_responsive.jsonl` instead — see below).

Each run gets a fresh `run` id (`time.strftime("%Y%m%d-%H%M%S")`); every
downstream tool that reads this cache takes "the latest run of this topic" by
sorting `run` ids and taking the last, so **re-running a topic doesn't erase
history, but every consumer silently ignores everything except the newest
run** unless you pass `back=` (judge tool) or read the raw file yourself.

### `audit_somatic_vanilla.py` — the baseline arms

Calls Ollama's *native* `/api/chat` directly (not the OpenAI-compatible shim
— see "Known pitfalls" below) with no engine involved. `ARMS` maps an arm name
to a system prompt and its own cache file:

| arm | system prompt | cache |
|---|---|---|
| `vanilla` | none | `somatic_vanilla.jsonl` |
| `friend` | *"You are a warm, concise friend. Keep replies short and conversational."* | `somatic_prompted.jsonl` |
| `textbook` | performed sympathy + a bulleted tips list, the anti-pattern the Somatic voice is built to reject | `somatic_textbook.jsonl` |

`textbook` is a **judge control, not a fourth arm to rank BoneAmanita against**
— it exists so `--control textbook` can check whether a judge secretly rewards
the style the voice rejects. Same `user=`/`max_turns=` and `arm`/`beat`/
`shown`/`delivered`/`sim_fallback` convention as the census tool when running
responsively.

### `somatic_sim_user.py` — the simulated person

`SimulatedUser(topic, model="qwen3.5:9b", window=6, ...)`. `.message(turn,
phase, beat, transcript)` returns the person's next line: verbatim for turn 0
(every system gets the identical opener), otherwise generated from the
persona, the phase's stated feeling, the beat, and the system's own last
`window` exchanges rendered as that person actually saw them (a held turn
shows the on-screen notice, not the raw model reply the person never saw).
Falls back to the beat verbatim after repeated unusable output
(`self.fell_back`, recorded per turn as `sim_fallback`).

**Three caught and fixed failure modes**, all found on the same `toast` run,
each surfacing as the fix for the previous one changed the model's escape
route rather than the underlying tendency:

1. **Verbatim repeat.** Given a long-ish transcript, `qwen3.5:9b` sometimes
   ignores the new beat entirely and re-emits the previous "Me:" line
   byte-for-byte — a small-model copy-the-context collapse, not a considered
   non-reaction. First caught on `toast`: 6 of 59 consecutive turn-pairs
   across the two arms tested.
2. **Repeat-then-append**, once (1) was guarded against with a retry nudge:
   the model "obeyed" *don't repeat yourself* by keeping the old message
   intact and appending new content after it, so turn N+1's message started
   with turn N's message verbatim and grew from there (four turns in a row
   grew this way in one run, the last comfortably over 400 characters).
3. **Prompt-scaffold echo:** at least once, the model's entire output was our
   own prompt template text ("Right now you are feeling: ... What is on your
   mind: ...") copied back as if it were the character's line.

`.message()` now rejects an output that (a) exactly matches the transcript's
last person line, or (b) *starts with* it (catches the append pattern too),
case/whitespace-insensitively, and retries once with an explicit "say only
the new thing, don't restate-then-add" nudge before falling back to the beat.
`clean_message()` separately rejects output containing either literal
scaffold phrase. **If you see suspiciously similar or unusually long
consecutive messages in a responsive cache, check for these before trusting
the run** — diagnostic: `json.loads` every row for the run, group by `arm`,
and look for a `message` that equals or is prefixed by the previous turn's.
Given how each fix exposed the next failure mode, treat this list as
probably-not-exhaustive rather than closed; if a fourth pattern shows up,
add a case to `tests/test_judge_controls.py`'s `SimulatedUser` class the same
way, not just a one-off cache-cleaning pass.

`.exit_interview(transcript, samples=3)` asks the simulated person, in
character, to rate the conversation 1-7 on `heard`, `clearer`, `lectured`,
`performed`, `again` (want to keep talking), plus a one-line best/worst
moment, several times, averaged. Same "one LLM's self-report" caveat applies,
doubly: this is an LLM rating a conversation it also generated half of.

### `audit_somatic_responsive.py` — orchestrates one arm against the simulated person

`--arm {bone,friend,vanilla,textbook} --topic <t>` runs that one system
against `SimulatedUser`, appends to `tools/cache/somatic_responsive.jsonl` and
the exit interview to `somatic_responsive_exit.jsonl`, then prints (or
`--report` alone reprints from cache) a side-by-side table: reply length,
the *person's own* word count in the first half vs. second half of the
conversation (does this system make the person go quiet over time), held-turn
count, simulator-fallback count, and the exit-interview means per arm. One arm
per invocation — run arms sequentially, not in parallel; each one is real GPU
time on top of the engine or baseline call (a generation call per turn for
the simulated person, on top of the responder's own).

### `audit_somatic_blind_judge.py` — the blind ranking, and whether to trust it

Ranks BoneAmanita / Vanilla / Prompted (letters shuffled per turn, per pass,
via `--seed`) using a judge model from a different family than the responder,
on a rubric written from the receiving person's side ("which would you rather
get right now"), not the kernel's own style rules. `--passes 2` (default)
re-shuffles and re-judges each turn so a fixed position preference averages
out instead of reading as a system preference. `delivered()` (or, for
`--responsive`, per-system delivery) decides whether a turn is comparable at
all; `--held skip` (default for the scripted mode) drops a turn where any
system produced no visible reply, `--held forfeit` (default for
`--responsive`) instead ranks a silent system last.

**Before trusting any ranking from a judge, run its controls:**

| `--control` | shows | replies shown | passing bar |
|---|---|---|---|
| `null` | does the judge just prefer a shown position? | one real reply, copied under all three labels | no position notably favoured |
| `samples` | same, with real (not copied) same-quality text | three independent same-arm runs of the topic (needs 3 `friend` runs cached) | no position notably favoured |
| `mismatch` | does the judge actually read the conversation, or just surface qualities? | BoneAmanita, Prompted, and a real reply written for a *different* turn (decoy prefers a different emotional phase, falling back to distance, over `pick_decoys`) | the decoy should rank last ~90%+ of the time |
| `textbook` | does the judge reward the anti-pattern the voice rejects? | BoneAmanita, Prompted, and the performed-sympathy/bulleted-list `textbook` arm | textbook should lose clearly; no hard bar, but winning is disqualifying |
| `--agree RESULTS.json --human PICKS.txt` | does the judge agree with a real person? | no model calls — scores a finished judge run against the panel's "Copy my results" export | higher is better; there is no bar, since a human blind read is the standard the judge is trying to approximate |

**As of 2026-09-21, tested on `toast` across six local judges (`mistral-nemo`,
`ministral-3:14b`, `phi4`, `qwen3.5:9b`, `gpt-oss:20b`, `qwen3:30b-a3b`): every
one failed `mismatch` (57-79% last place, bar is ~90%), and every one showed
real position bias on `null`/`samples` (47-62% toward one slot, `qwen3:30b-a3b`
least biased). `phi4` and `gpt-oss:20b` additionally reward the `textbook`
style.**

**Update, 2026-09-22: rubric rewrite clears `mismatch` for one judge.** The
old rubric buried "did it respond to what was said" in a four-item list
alongside tone/register/restraint; `JUDGE_SYSTEM` now makes fit an explicit,
first, gating question ("a reply that would fit almost any nearby turn...
cannot be ranked first"), and `build_prompt`/`build_prompt_responsive`
separate the line a reply must answer ("What you just said") from
"Scrollback" instead of leaving it as the last of four undifferentiated
history lines. Re-tested `mismatch` on the three judges still locally
available (`phi4`/`gpt-oss:20b` were never repulled, already disqualified on
`textbook`): `mistral-nemo` 50% last (unchanged, still FAIL), `ministral-3:14b`
78% last (up from 62%, still FAIL), **`qwen3:30b-a3b` 92% last, PASS** (up
from 65%). **Current read: `qwen3:30b-a3b` is the validated judge for a real
ranking** (its `null`/`samples` position bias is real but only shows up when
replies are genuinely tied, which a real ranking or `mismatch` is not);
`mistral-nemo` is controls-only from here (fast, but the rubric fix did not
move its `mismatch` score, do not trust its ranking); `ministral-3:14b` is a
maybe, improved but unconfirmed. Full numbers in `SESSION_HANDOFF.md` (search
`the three-judge blind panel` and the two updates after it) and
`tools/cache/blind_judge_control_*_toast_*_rubric2.json`. Rerun the controls
whenever the rubric, the judge model, or the decoy logic changes again, a
control result is about the judge-plus-rubric pairing, not the judge model
alone, which is exactly what changed here.

`qwen3:30b-a3b` is also the heaviest judge to run (MoE, 18GB of `Q4_K_M`
weights alone, more than the 16GB card, so some of it always offloads to
CPU): `NUM_CTX` in this file dropped from 16384 to 6144 (measured worst case
on real `toast` data is ~1830 tokens for a scripted prompt, ~1230 for a
responsive one; 6144 keeps >3x headroom), which cut the CPU-offloaded
fraction from 24% to 18-19% in a live `ollama ps` check. That is a real but
modest win: the base weights still exceed the card, so some CPU offload is
structural at this quantization, not something a context change can remove
outright. A smaller quant (if one exists on the registry) would need pulling
and hasn't been checked or downloaded.

`--responsive` swaps the input source and prompt shape (see "Scripted vs.
responsive" above) but the same control modes apply to it in principle;
they have not yet been run against responsive data (controls need every
system present, and `--responsive` defaults `--held forfeit`, so `--control`
with `--responsive` currently forces `--held skip` — check that combination
still makes sense before relying on it).

### `build_blind_panel.py` + `blind_panel_template.html` — the human blind read

Builds a single HTML page from the latest census/vanilla/prompted caches and
one or more finished judge JSON files: every comparable turn shown as three
unlabeled cards in a per-turn seeded shuffle (`SEED = 20260920`, same seed
every time — the shuffle is casual obfuscation, not a sealed test; the answer
key sits in the page's own JSON), a held turn shown with its reason and what
the other two systems said instead, and a "Reveal" button that shows both the
reader's own tally and every supplied judge's numbers side by side. `--out` is
a page body meant for an Artifact host; `--standalone` additionally wraps a
full document (doctype, charset, viewport, a minimal reset) for self-hosting,
e.g. Neocities. The template's "Copy my results" button exports the reader's
per-turn picks as plain text, parseable back by
`audit_somatic_blind_judge.py`'s `parse_human()`/`--agree`.

### `audit_silence_diagnostic.py` — why a turn went silent

Not part of the scoring pipeline. Re-runs one scripted topic with spies
wrapped around every point that can hold a turn (`TheVillageCouncil._evaluate`,
`StageManager.negotiate`, `TheCortex.nominate_toxicity` — logged *before*
MOOG's own reset erases the drag value that tripped it — `SimulationPreflightPhase.run`,
`TheGatekeeper._audit_safety`), and writes a plain-text trace to
`tools/cache/silence_diagnostic_<topic>.log`. `--canned` answers every turn
with one fixed reply and skips the model entirely (no GPU), which reproduces
any hold that depends only on the input text; a hold that depends on what the
model actually said needs the live `--model` run. `--trace-drag` additionally
logs every `narrative_drag` write of 8+ with the code line that made it — this
is how the `BENEDICT|GORDON` +50 synergy was originally traced to its source.

### `audit_somatic.py` — a different axis, worth knowing about separately

Older sibling (ROADMAP C5/D2), not part of this comparison chain. Answers a
narrower question with controlled arms (`CONTROL`/`ANAEROBIC`/`EXHAUSTED`/
`BOTH`/`DISENGAGED`) built directly from `SomaticBudget` objects rather than a
scripted conversation: when the composed prompt tells the model its partner
is low or that the engine itself just spent heavily, does the model's prose
measurably change (sentence count, breath language, closing questions)? Its
statistics module, `body.somatic_metrics`, is imported by `audit_somatic_census.py`
for reply word counts. Its own tests (`tests/test_audit_somatic.py`) check the
measurement rules, not a live model.

## Caches at a glance

All under `tools/cache/`, one JSON object per line (`.jsonl`) unless noted.
Every `.jsonl` reader in this pipeline takes the row(s) matching a `topic`
(and, for the responsive files, `arm`) whose `run` id sorts last.

| file | written by | key fields | "arm" field? |
|---|---|---|---|
| `somatic_census.jsonl` | census, scripted mode | prompt contents, person/engine state, ATP+health ledgers | no |
| `somatic_vanilla.jsonl` | vanilla, `--arm vanilla` | reply, `done_reason` | no |
| `somatic_prompted.jsonl` | vanilla, `--arm friend` | same | no |
| `somatic_textbook.jsonl` | vanilla, `--arm textbook` | same | no |
| `somatic_responsive.jsonl` | census or vanilla, called with `user=` | `+ arm, beat, shown, delivered, sim_fallback` | **yes** |
| `somatic_responsive_exit.jsonl` | `audit_somatic_responsive.py` | `arm, topic, sim_model, samples, mean` | yes |
| `blind_judge_results.json` / `blind_judge_control_*.json` / `blind_judge_responsive_*.json` | blind judge (single JSON object, not jsonl) | `summary` + full per-vote `results` | n/a |
| `silence_diagnostic_<topic>.log` | silence diagnostic | plain text trace | n/a |

## A full run, from scratch

```bash
# 0. What's available locally
ollama list

# 1. Generate the three (or four) arms for a topic
python tools/audit_somatic_census.py --topic toast
python tools/audit_somatic_vanilla.py --topic toast --arm vanilla
python tools/audit_somatic_vanilla.py --topic toast --arm friend
python tools/audit_somatic_vanilla.py --topic toast --arm textbook   # only needed for the textbook control

# 2. Validate whichever judge you're about to trust, BEFORE ranking anything
python tools/audit_somatic_blind_judge.py --topic toast --control null     --judge-model <model>
python tools/audit_somatic_blind_judge.py --topic toast --control mismatch --judge-model <model>
python tools/audit_somatic_blind_judge.py --topic toast --control textbook --judge-model <model>
# read the printed PASS/FAIL lines. If mismatch doesn't clear ~90% last-place,
# do not treat that judge's real ranking (next step) as a verdict.

# 3. The real three-way ranking
python tools/audit_somatic_blind_judge.py --topic toast --judge-model <model>

# 4. Build the human blind-read panel
python tools/build_blind_panel.py --topic toast --title "..." --story "..." \
    --judge tools/cache/blind_judge_results.json --out panel.html --standalone panel-standalone.html

# 5. (separately) the responsive track
python tools/audit_somatic_responsive.py --topic toast --arm bone
python tools/audit_somatic_responsive.py --topic toast --arm friend
python tools/audit_somatic_responsive.py --topic toast --report
python tools/audit_somatic_blind_judge.py --topic toast --responsive --judge-model <model>
```

Run steps sequentially, not in parallel — several of these load a different
Ollama model, which evicts the previous one, and running two generation
processes at once roughly doubles GPU/VRAM pressure for no speed benefit on a
single GPU.

## Local judge/model notes (2026-09-21 hardware: 7800XT, 16GB VRAM)

| model | role tried | size | `--think` needed |
|---|---|---|---|
| `gemma4:12b` | responder (all arms) | 7.6GB | engine sets `think: False` itself; vanilla.py's `SAMPLING` does too |
| `gemma4:e4b` | the engine's own DSPy critic (not swappable from these tools) | 9.6GB | n/a |
| `qwen3.5:9b` | simulated person | 6.6GB | `off` |
| `mistral-nemo` | judge (default, controls-only as of 2026-09-22: fast, but the rubric v2 fix did not clear `mismatch` for it) | 7.1GB | none (no reasoning mode) |
| `ministral-3:14b` | judge (unconfirmed: improved on `mismatch` under rubric v2, still fails) | 9.1GB | none |
| `phi4` | judge (textbook-biased, see above) | 9.1GB | none |
| `gpt-oss:20b` | judge (textbook-biased, see above) | 13GB | `low` (empty visible output otherwise) |
| `qwen3:30b-a3b` | **validated judge for a real ranking as of 2026-09-22** (rubric v2, `mismatch` 92%); slow and heavy regardless | 18-19GB, MoE (partial CPU offload even at `NUM_CTX` 6144) | `off` |

`gpt-oss:20b` and `qwen3:30b-a3b` visibly load the whole machine, not just the
GPU (confirmed live) — don't run either alongside another heavy job, and
don't assume a `Monitor`/background wait that goes quiet under one of these
has stalled; check `ollama ps` and the log/cache file directly before
concluding a run is stuck.

## Known pitfalls (already hit, already fixed — don't re-discover these)

1. **Ollama's OpenAI-compatible `/v1/chat/completions` shim silently ignores
   `options.num_ctx`** and holds the model at its 4096-token default,
   truncating a long conversation mid-word with no error. Every tool here
   uses the native `/api/chat` endpoint instead, and sets `num_ctx` explicitly
   (32768 for the baseline generator's full transcript, 16384/20480 for the
   judge/simulator's shorter windows). If a new tool is added, use native
   `/api/chat`, not the shim.
2. **A copyable example in a judge's format instructions gets copied.** The
   original rubric said `RANKING: B > A > C`; `mistral-nemo` put the reply in
   position B first in 52 of 58 votes on three copies of the *same* text. Use
   placeholders (`RANKING: <letter> > <letter> > <letter>`) in any prompt that
   asks a small model to fill in a template.
3. **A judge that bolds its own output format** (`**RANKING: B > A > C**`)
   silently loses votes to a parser that requires the line to start exactly
   with `RANKING:`. `parse_ranking()` strips `*`/`_` before matching; this
   dropped 20 of 58 `ministral-3` votes the first time it wasn't handled.
4. **A same-family judge (or a rubric shaped like the kernel's own style
   rules) inflates the score it gives BoneAmanita.** The project's first judge
   attempts (same-family, kernel-shaped rubric) scored 22-3 and 27-1-1; a
   cross-family judge with a person-side rubric brought that down
   substantially. Always use a judge from a different model family than every
   responder being ranked.
5. **A DEATH or SILENCE snapshot still logs a model call.** The census logs
   whatever the model returned even on a turn where the *person* never saw it
   (the engine held or died and a notice replaced it on screen). Anything that
   reads `reply` without also checking `snapshot_type`/`delivered` will
   silently rank or display prose nobody was shown. Use `is_delivered()`
   (scripted) or the `delivered` field (responsive), never `bool(reply)` alone.
6. **A judge's control result is about the rubric-plus-judge pairing, not the
   judge model alone.** Changing the rubric, the decoy strategy, or the
   `--think` setting invalidates a previously-passing control; rerun it.
7. **The simulated person can get stuck repeating itself** (see
   `somatic_sim_user.py` above) — fixed with a repeat-detection retry, but
   worth re-checking after any prompt change to `SIM_SYSTEM` or `_persona()`,
   since those are exactly the levers that affect how strongly the model
   anchors on the transcript it's shown.
8. **The scratchpad directory gets wiped between sessions** (a reboot or
   session change, not a bug in this project). Any throwaway shell script
   meant to be invoked *later in the same reply* should be inlined into the
   `Bash` call that runs it, not written to the scratchpad and referenced by
   path in a later call — a wipe mid-session has cost a re-run of a
   multi-minute control batch at least once.

## If we built this from scratch, knowing what we know now

- **Validate the judge before reporting any ranking from it, not after.** The
  control battery (null/samples/mismatch/textbook) should have been the very
  first thing built, before any "BoneAmanita beats vanilla, p = .0004"
  number was ever written down. As it stands, every pairwise result reported
  before 2026-09-21 needs to be re-read as "what a judge that fails a basic
  fit-to-conversation check produced," not as a finding.
- **The rubric should ask the judge to check fit to the conversation
  explicitly**, as its own scored criterion ("does this reply respond to what
  was actually just said, specifically, not just in tone"), rather than
  hoping a general "would you want to receive this" framing makes the judge
  check that implicitly. Every judge tested handles tone and register fine
  and fails exactly this check.
- **Build the responsive/simulated-person track from day one**, not as a
  later addition. A fixed script structurally cannot test the thing a
  stateful engine is supposed to be good at (the person's own state shifting
  in response to what they're told), so every scripted-comparison result is
  answering a narrower question than "does the engine help" and should have
  been labeled that way from the start rather than presented as the headline
  comparison.
- **Separate "was a reply generated" from "was a reply delivered" in the data
  model from the first line of code.** Conflating `reply` (a string) with
  "the person saw this" cost real debugging time more than once (a same-turn
  DEATH/SILENCE snapshot still has a non-empty `reply` field); `is_delivered()`
  should have existed before the first cache file did.
- **Pin every model by exact tag in one place**, not as scattered defaults
  across five files (`gemma4:12b` here, `mistral-nemo:latest` there,
  `qwen3.5:9b` in a third). A silent `ollama pull` of a newer tag between
  sessions would currently be invisible to every tool here.
- **One simulator model playing every arm's "person" is a known, accepted
  confound**, not a discovered one — it should be named as a limitation in
  the very first responsive-track result, not found later. The exit interview
  in particular is one LLM's self-report about a conversation it also
  half-wrote; useful for relative comparison across arms, never for an
  absolute number.
- **`--held forfeit` (a silent turn loses) should have been the default for
  the standard scripted comparison, not just the responsive one.** `--held
  skip` quietly conditions every past win-rate on the engine having chosen to
  speak at all, which is itself one of the behaviours under test.
- **Multiple engine runs per topic, not one, from the start.** The distressed-
  turn refusals were already shown to be state-dependent (chance co-firing of
  two voices); a single run per topic can't distinguish "the fix worked" from
  "the coin didn't land the bad way this time," and that gap is still open.

## Still open (see `SESSION_HANDOFF.md` for the live, dated version)

The distress shield keyed on exhaustion rather than what was said; a judge
that clears the `mismatch` control; the goodnight ATP-floor hold; honoring
`village_suppression` in council voice detection; multiple runs per topic to
separate a fix from noise. This section is deliberately short — treat
`SESSION_HANDOFF.md`'s latest entry as the source of truth for what's open
right now, since it's updated every session and this file is not.
