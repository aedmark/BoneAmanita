# Testing: how the BoneAmanita-vs-baselines evaluation actually works

> **Note:** Historical testing reflections and old open items have been moved to [archive/TESTING_HISTORY_2026_09.md](archive/TESTING_HISTORY_2026_09.md).

This is the reference for `tools/audit_somatic_*.py`, `tools/build_blind_panel.py`
and `tools/somatic_sim_user.py`: what each one does, how they chain together,
the caches they read and write, and the mistakes already made and fixed so a
new session or a different team doesn't re-make them. `SESSION_HANDOFF.md` is
still the log of what happened and when; this is the standing reference for
how to run it again. `ROADMAP.md` is the project's own status; this file
assumes you've read enough of it to know what "the Somatic Contract" is.

**As of 2026-09-23, verdicts come from human readers** (see
`SESSION_HANDOFF.md`, "Decisions already made"). The AI-judge sections below
document what was built and tried; the judges are not a verdict.

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

The simulated person is itself an LLM (default `mistral-nemo` since
2026-09-23, `qwen3.5:9b` before that; a different
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

**Representative runs** (2026-09-23): each boot reads saved state from an
empty temp dir (`fresh_state`), `displayed` is the reply as the engine showed
it (after its filters, or the mercy line), and turns are paced by a person's
reading and typing time (`paced_seconds`, `--pace none` to disable). Records
from before this lack the three fields; `build_blind_panel.py` says so on the
page when it builds from them.

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

`SimulatedUser(topic, model="mistral-nemo:latest", window=6, ...)`. `.message(turn,
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

4. **Paraphrased scaffold echo** (`mistral-nemo`, 2026-09-23, 1 turn in 90):
   the simulator answers its own prompt headings in prose ("As for how I'm
   feeling... I guess what's on my mind is"). **Not guarded**: any regex for
   it would also reject a person naturally saying how they feel. Grep a run
   for it and judge by eye.

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

**Phase word ceilings** (`PHASE_MAX_WORDS`, 2026-09-23): 50 / 35 / 15 / 35 / 50
words for engaged / tiring / flagging / distressed / recovering, about each
phase's longest scripted line, with flagging raised from the script's "ok" to
one short sentence. Ceilings, not targets, the same for every arm. Added after
the person mirrored vanilla's length (76 words "tiring" against vanilla, 26
against BoneAmanita). The cap is stated in the prompt; an over-long message is
retried once with a "shorter" nudge, then trimmed to whole sentences
(`trim_to_words`) and recorded as `sim_trimmed` (a report column next to
fallbacks). Runs from before this change have no `sim_trimmed` field.

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
outright. There is no smaller official quant: the 30b-a3b size class ships
only as `Q4_K_M` (what's pulled), `Q8_0` and `fp16` (checked 2026-09-22). A
community GGUF would be a different trust boundary, and MoE models degrade
faster than dense ones at low bit depths, so it was left alone.

`--responsive` swaps the input source and prompt shape (see "Scripted vs.
responsive" above). Only `--control none` and `--control mismatch` are wired
for it; the others need a responsive-shaped view builder and refuse to run.
A control forces `--held skip`, since it needs every system present. The
responsive `MISMATCH` view keeps Prompted's own real context and last message
and swaps in Prompted's own reply from a decoyed turn of the same
conversation.

**Responsive decoys are anchored and dissimilar** (2026-09-23). A simulated
person repeats themselves ("gonna sleep" at turn 17 and again at 29), so a
decoy from elsewhere in the same conversation can genuinely fit ("Sweet
dreams!"). With `--responsive --control mismatch`, `pick_decoys` first keeps
only *anchored* candidates (reply similarity to its own message minus its
mean similarity to the other messages, top half: stock agreement that fits
anywhere is out), then narrows the usual phase/distance pool to its least
similar half, by the larger of two embedding cosines (this turn's message
against the candidate's message, and against the candidate's reply). Both
from `decoy_similarity`. Without the anchoring step, low similarity alone
selected stock agreement for half the turns. It needs the real embedder and
refuses to run on hash. Scripted decoys are untouched.

**`--pairwise`** splits each turn into its three pairs, each shown in both
orders across the two passes, so position bias cancels exactly and the judge
holds two replies (or conversations) at a time. Each pass reads as a
tournament: last means losing both pairs; a cycle has no first or last and
counts against a control's bar. It helped every judge tried on responsive
`mismatch` (see `SESSION_HANDOFF.md`, 2026-09-23 evening). Note the bar is
steep in call terms: losing both pairs 90% of the time needs about 95%
accuracy per call.

**Responsive rubric: v2, and v3 was tried and reverted.** v3 (2026-09-23)
asked for a per-conversation `FIT X: yes|no` before the ranking. On the same
arms it lifted `mistral-nemo` (45% to 72%) but dropped `ministral-3:14b` (82%
to 66%) and `qwen3.5:9b` (80% to 62%): the judges followed their own yes/no
calls exactly, and an absolute "does this fit" call proved noisier for them
than v2's side-by-side comparison. Details in `SESSION_HANDOFF.md`, 2026-09-23.

**Responsive `mismatch` history, v2 with similarity decoys, `toast`:** `qwen3.5:9b`
91% last (51/56), **PASS by one vote**; `ministral-3:14b` 86%, FAIL.
That pass was on arms where `qwen3.5:9b` was also the simulated person, so it
read conversations where it wrote the person's half. **On arms regenerated
with `mistral-nemo` as the person it fell to 68% (`ministral-3:14b` 63%)**:
no judge is currently validated for a responsive ranking (best since:
`qwen3.5:9b`, pairwise with anchored decoys, 85%). Keep the simulated
person and the responsive judge on different models; a pass earned with them
the same is not a pass.

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

`--responsive` (2026-09-23) builds the page from `somatic_responsive.jsonl`
instead. The three conversations drifted apart, so there is no shared
message: each card carries what the person had just said in *that*
conversation, the reply it got (or the on-screen notice, if the engine held),
and the exchange before it collapsed under "Earlier in this conversation".
`--judge` is optional (none is validated for responsive ranking). The export
is the same format, so a human read of the responsive runs can score any
judge with `--agree`; that is the plan for validating a responsive judge
against Gordon's own picks rather than tuning the `mismatch` control further.

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
# 0. What's available locally, and a clean engine: reset.sh clears saves/,
#    memories/, logs/ and learned lore files (not tools/cache/). Run it before
#    every trial; the census also boots from an empty save dir as a second guard.
ollama list
bash reset.sh

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
| `qwen3.5:9b` | judge (cleared responsive `mismatch` at 91% only on arms it also simulated the person for; 68% once the person was `mistral-nemo`, not validated); simulated person until 2026-09-23 | 6.6GB | `off` |
| `mistral-nemo` | simulated person (default since 2026-09-23; family differs from the responders and from `qwen3.5:9b`, shared with `ministral-3:14b`, so if that becomes the judge pull a third family such as `llama3.1:8b` for the person); judge (default, controls-only as of 2026-09-22: fast, but the rubric v2 fix did not clear `mismatch` for it) | 7.1GB | none (no reasoning mode) |
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
9. **An audit module's import-time side effect leaks into every tool that
   imports it.** `audit_somatic.py` sets `BONE_EMBED_BACKEND=hash` at import
   (right for C5, which must not depend on an embedding server). From
   2026-09-19 (`a572137`) to 2026-09-23 the census imported `measure` from
   it, so every census and responsive `bone` run in that window booted with
   hash vectors: no associative recall, and the Creative Determinant's graph
   solve failing on every turn ("dim must be a positive multiple of 64") and
   falling back to PID. The census now imports `measure` from
   `body.somatic_metrics`, and `tests/test_audit_somatic.py` checks that
   importing the census leaves the backend unset. Before trusting a `bone`
   run, grep its log for `hash coordinates` and `falling back to PID`.
