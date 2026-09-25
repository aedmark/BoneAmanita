# Archived Session Logs (September 2026)

<a id="distress-refusal-fixes-toast-2026-09-21"></a>

## Earlier: the distressed-refusal fixes, a sixth topic that ran clean, and where the evidence stands, 2026-09-21

### Fixes applied (Gordon chose options 1 and 2 from the diagnosis below)

1. **Friction synergies do not fire in CONVERSATION**
   (`COUNCIL.FRICTION_SYNERGY_DISABLED_MODES`; `council.convene()` takes
   `active_mode`, passed from `phases/cognitive.py`). This is deliberately not
   an edit to the +50: THE DIGNITY LOCK is a designed mechanic (my earlier
   "probably a typo" guess was wrong), so the row is untouched for other modes.
2. **MOOG's worry-quarantine does not run in CONVERSATION**
   (`CORTEX.MOOG_DISABLED_MODES`, in `brain/cortex.py` `nominate_toxicity`).
   **Caveat found while testing:** with MOOG off and drag at 55 in
   CONVERSATION, the branch that falls through is `GORDON_ANCHOR` (magnitude
   10), which still holds the turn and, unlike MOOG, does not reset drag
   afterwards. Fix 1 removes the known source of such a spike, so this should
   be rare, but if drag ever jumps by another route, a hold could last longer
   than before. The real protection is still option 3 (a distress shield that
   reads what was said, not only the exhaustion-derived sentence cap).
- Observation, not acted on: the CONVERSATION preset already lists GORDON in
  `village_suppression`, and `genesis.py` honors it for the village *agent* (so
  there is no `village.gordon`), but the council's voice detection ignores it.
  Honoring it there would remove the GORDON+BENEDICT co-firing at its root and
  probably some TENSION_MAGNITUDE holds. Bigger change; not made.
- Tests: `tests/test_conversation_gates.py` (6, mutation-checked: disabling
  either gate fails exactly the two conversation-mode tests). Wiring checked
  live: `active_mode` reaches `council.convene` on a real turn as
  `"CONVERSATION"`. Full suite: **594 passed, 5 skipped, 142 subtests.**

### A sixth topic, `toast`, composed after the fixes and never tuned on

A wedding toast for a younger brother (performance anxiety, a friend's hard
truth, then finding the real story; no parent, no money, no workplace). Engine:
**29 of 30 turns generated, all five distressed turns answered**, health never
below 85, ATP never below 17, drag never above 4.1, no death, no mutation. The
one hold was turn 13, "Going to bed. The toast will still be terrible
tomorrow.", held by the ATP floor ("not quite enough left in me"). That is a
legitimate mechanism landing badly: a goodnight met with silence. **Open.**
Honest limit: the earlier refusals needed GORDON and BENEDICT to co-fire, which
is state-dependent (it did not happen in some earlier distressed phases
either), so one clean run is consistent with the fixes, not proof of them.

### Judges, both clean topics

Two judges (mistral-nemo, ministral-3:14b), two shuffled passes each:

| pooled pairwise votes | BoneAmanita vs Prompted | BoneAmanita vs Vanilla | Prompted vs Vanilla |
|---|---|---|---|
| `toast` (fresh) | 60-56 (52%, p = 0.78) | 70-46 (60%, p = 0.03) | 73-43 (63%, p = 0.007) |
| `lease` | 56-47 (54%, p = 0.43) | 66-37 (64%, p = 0.006) | 70-33 (68%, p = 0.0003) |
| both | 116-103 (53%, p = 0.42) | 136-83 (62%, p = 0.0004) | 143-76 (65%, p < 0.0001) |

The conclusion does not move: by these judges the engine is not
distinguishable from one friendly sentence, and both beat a bare model. The
one-line prompt actually beat vanilla by slightly *more* than the engine did.
Votes are not fully independent (each turn is judged twice on the same three
replies), so the p-values flatter; the judges are small models and one of them
agreed with its own second pass on only 8 of 29 turns on `toast`. The human
reads (Gordon 28 of 28 on `lease`, a friend about 7 of 28) point the other way
and are the better instrument; more of them, with the per-turn export, is the
next real evidence.

**Judge bug fixed:** `parse_ranking` required a line starting with `RANKING:`,
so a judge that writes `**RANKING: B > C > A**` had its vote dropped (20 of 58
ministral votes on `toast`, the first time). It now strips markdown emphasis;
`toast` was re-run. The `lease` ministral run (9 of 56 dropped) predates the
fix and was not re-run.

### Tooling

`tools/build_blind_panel.py` and `tools/blind_panel_template.html` build the
three-way page (and a standalone Neocities version) from the caches and judge
outputs; it reproduces the `lease` page's cards and judge data exactly. The
scratch directory had been wiped twice, which is why the builder is now in the
repo. Panel: <https://claude.ai/artifact/H3vGPaVz2RUdKjEaQPPazN> (private
until shared).

### Still open

The distress shield keyed on exhaustion (option 3); the goodnight hold at the
ATP floor; the friend's per-turn picks; a stronger baseline prompt (one that
mentions advice and narration); the D0 economy (ATP ran down to 1.8 on
`lease`); the still-unexplained 999 drag and PINKER over 5000 in the run made
while the first critic gate was inert.

<a id="three-way-blind-comparison-2026-09-20"></a>

## Earlier: a fairer three-way comparison, a fresh topic that killed the engine, and what a clean topic showed, 2026-09-20

Gordon, on the blind panel: it is "kind of comical that we even present it
like there's a choice." Fair: vanilla answers with headers and 500-word
lists, so it is distinguishable from BoneAmanita on shape alone, and the
judge that scored 27-1-1 for BoneAmanita shared its model family with the
answerer and used a rubric that closely mirrored the kernel's own style
guide. Asked for a third arm and a genuinely new topic, with clean results.

### What changed in the evaluation

- **Third arm, `--arm friend`** (`tools/audit_somatic_vanilla.py`): the same
  bare gemma4:12b plus exactly one line, *"You are a warm, concise friend.
  Keep replies short and conversational."* Nothing about advice, narration or
  punctuation, which are what the kernel targets. Own cache
  (`tools/cache/somatic_prompted.jsonl`); both baseline arms now record
  `done_reason` so truncation is checkable per turn (all 60 replies below
  ended `stop`).
- **Judge rewritten** (`tools/audit_somatic_blind_judge.py`): three-way
  ranking, each turn judged twice with independent shuffles, a rubric written
  from the receiving person's side ("which would you rather get") instead of
  the kernel's rules, and a judge from a different family than the answerer
  (`mistral-nemo`, cross-checked with `ministral-3:14b`). It also only counts
  replies that were actually delivered: the census logs the model call even on
  a turn where a DEATH or SILENCE screen replaced it.
- **The earlier tallies (22-3, then 27-1-1) came from the same-family judge
  and the kernel-shaped rubric. Read them as upper bounds, not as the result.**
- `tools/audit_silence_diagnostic.py` takes `--topic` and `--canned` (fixed
  reply, no GPU) now, which reproduced the failures below deterministically.

### A new topic, `promotion`, and the engine died on it

A workplace decision with no parent, no physical project and no third party's
crisis (a team-lead offer, then snapping at a colleague in standup, then
asking for a trial period). Live census: **7 of 30 turns generated; the
engine was permanently dead from turn 11.** Everything before the death was
deterministic and reproduced with canned replies:

- **Turn 3**, "the **deploy** pipeline": `POINT_OF_NO_RETURN`
  (`phases/cognitive.py`), an ops-style gate that waits for a literal
  `CONSENT` keyword, matched by substring on a person talking about their job.
- **Turn 9**, "the news traveled **faster** than I did": `physics/observer.py`
  forces voltage to 160 whenever the uppercased text contains `FASTER` or
  `ACCELERATE`, or has three or more `!`. Confirmed with controlled probes:
  "faster" gives 160, "slower" gives 2; "Thanks so much!!!" gives 160,
  "Thanks so much." gives 0. The same block has substring keywords for
  `LOOP`, `VOID` (so "avoid") and `NONSENSE`. Voltage stayed near 100 for
  several turns, PINKER held turns 9 and 10, the two-hold cap forced a reply
  on 11, and the crucible's `MELTDOWN` (`voltage * 0.5` damage when structure
  is at or below 0.5) took health to zero. One enthusiastic message could do
  this to any conversation.
- **Turns 7 and 8**, MOOG holds: not reproduced under canned replies, and in a
  later canned run turn 8 held with drag at 54 against a limit of 12.8 that
  four further traced boots could not reproduce. **Unexplained. Still open.**

### Fix (a judgment call, easy to revert), and why the test topic changed

The same principle as the critic gate, one config key:
`CORTEX.KEYWORD_TRIGGERS_DISABLED_MODES = ["CONVERSATION"]`. In those modes
the observer's substring keywords and the ops "deploy" gate do not run.
`active_mode` is passed in from the call sites (`phases/environmental.py`,
`phases/cognitive.py`), not read through a back-reference, which is what broke
the first attempt at the critic gate. Tests: `tests/test_physics.py` (voltage
stays low in CONVERSATION and still hits 160 in ADVENTURE),
`tests/test_preflight_nominations.py` (no `POINT_OF_NO_RETURN` in
CONVERSATION, still fires in ADVENTURE); mutation-checked (disabling either
gate fails exactly those tests). Full suite: **588 passed, 5 skipped, 142
subtests.** Canned replay of `promotion` after the fix: no death, turns 3 and
9 to 11 answered.

Because two fixes were tuned against `promotion`, it can no longer be an
untouched test. Its baselines are kept (they do not depend on the engine).
A fifth topic was composed and run without any further tuning.

### The clean run, `lease` (roommate leaves mid-lease, money scare, footing)

Engine: **28 of 30 turns generated**, no death, health never below 84.7,
voltage never above 10.5, no epigenetic mutation. Held: turn 20 ("$212 in my
account", `ROS_PANIC`) and turn 23 ("my hands are cold and I can't tell if I'm
cold or panicking", MOOG). **Both refusals landed on distressed turns, two of
the five in that phase, which is the case D9 was meant to answer rather than
refuse. Not fixed here, deliberately, so the run stays clean. Open.** ATP also
fell from 37 to 1.8 over the last five turns (the D0 economy again).

Blind judges, three systems, 28 comparable turns, two passes each:

| | first place | mean rank |
|---|---|---|
| mistral-nemo: BoneAmanita / Prompted / Vanilla | 23 / 17 / 16 | 1.93 / 1.93 / 2.14 |
| ministral-3:14b: BoneAmanita / Prompted / Vanilla | 22 / 16 / 9 | 1.68 / 1.79 / 2.53 |

Pooled pairwise votes: **BoneAmanita over vanilla 66-37 (64%, exact p =
0.006); BoneAmanita over the one-line prompt 56-47 (54%, p = 0.43, not
distinguishable).** The two passes of the same judge agreed on the winner on
only 13 and 14 of 28 turns, so each judge is noisy, and votes are not fully
independent (each turn is judged twice on the same three replies), so the
p-values are optimistic. ministral dropped 9 of 56 votes as unparseable.

**What this says, honestly:** most of the distance from a bare model to
BoneAmanita is also reachable with one friendly sentence, and this evidence
cannot separate the engine from that sentence. It does not show the engine is
useless (one topic, small judges, a deliberately generic prompt), and it does
not support "remarkable." A human blind read is the missing signal; the
panel is published for that. A stronger baseline prompt (one that mentions
advice and narration) and more topics are the obvious next tests.

### Diagnosis of the refused distressed turns, 2026-09-21 (diagnosed, not fixed)

Reproduced live three times (census, instrumented replay, drag-traced replay):
`lease` turns 20 and 23 hold every time; canned replies do not reproduce
them, so the trigger depends on the conversation's real state. Tracing every
write to `narrative_drag` showed `phases/cognitive.py:436` adding **+49.0** on
exactly those two turns, from `council.convene()`'s returned adjustments. The
source is one row of `lore/council_data.json`:

    BENEDICT|GORDON: {kappa: 0.8, beta_index: -0.5, narrative_drag: 50.0, entropy: -0.4}

Every other synergy uses single-digit drag (-2 to -4); this one is +50. An
earlier draft of this note guessed a slip for 5.0; that was wrong: the row is
named THE DIGNITY LOCK and its own log line ends "Infinite friction applied",
so the +50 is a deliberate mechanic. Confirmed causally with a controlled probe (no code
touched): the GORDON voice alone gives a drag adjustment of -1.0, BENEDICT
alone -1.0, both together **+49.0 and entropy -0.4**. GORDON fires when
voltage is under 20 and drag is over 5 (a person who is quietly heavy);
BENEDICT's tact voice fires on `lq > 0.6 and beta > 0.4`. The -0.4 also
explains `chi` collapsing from about 0.52 to about 0.12 at the same moment.

Consequences, in this order: drag jumps to about 55 against MOOG's limit of
12.8, so MOOG quarantines the message with "That's a bigger question than I
can chase down right now" (nothing to do with the message); at turn 20,
`ROS + drag * chi * 20` also reached 171.7 against a limit of 160, so the
panic gate held it instead. A second defect let it through: `negotiate()`
only lets a refusal override a distressed person if it is 100 or more, but
"distressed" there means `sentence_cap <= 3`, which needs exhaustion at 0.6 or
above or depleted ATP. At turns 20 and 23 exhaustion was 0.49 and 0.39, so the
shield was off and MOOG's magnitude-5 hold went straight through. The shield
tracks the person's energy, not the emotional content of what they said.

Every drag-near-55 hold in the cached diagnostics matches: friendship 27 and
28, `promotion` 8, `lease` 20 and 23, each with GORDON and BENEDICT both
active. The unexplained `promotion` turn 8 MOOG hold is explained by this.

**Correction to the entry below.** It attributed the friendship turns 27 and
28 holds to the DSPy critic's injected "never soothe" axiom. That attribution
was wrong: those turns carry the same +50 signature. The critic gate is still
justified (the axiom demonstrably reaches every later prompt, and it fired
mid-distress), but the clean 29/30 census afterwards does not show it fixed
the holds; the synergy simply did not co-fire that run. What did produce the
drag of 999 and PINKER over 5000 in the run made while the first gate was
inert is not established.

Options offered (Gordon chose (a), in the mode-gated form, and (b); both
applied, see the entry above): (a) set the BENEDICT|GORDON drag to something in
line with its neighbours; (b) stop MOOG's worry-quarantine from running in
CONVERSATION, the same pattern as the critic and keyword gates, since telling a
person their worry has "undefined parameters" is the opposite of the product;
(c) base the distress shield on distress signals in the message and not only on
the exhaustion-derived sentence cap. Fixes need a fresh sixth topic to confirm,
since `lease` is now tuned-against.

### Two human blind reads, and they disagree

Gordon picked BoneAmanita on all 28 comparable turns. A friend who had not
seen the project picked it on about 7 of 28, at or below the 9.3 that chance
gives for three options (one friend, so this is not significant either way).
Read together with the judges: the engine reliably produces the voice its
designer wants, which is what the kernel was written to do, but that voice is
not a preference everyone shares. Gordon also knows the style, so his read may
be recognition rather than blind judgment. The friend's picks by system and
phase are the missing detail: the hypothesis worth testing is that BoneAmanita
wins the flagging and distressed turns (where restraint is right) and loses the
engaged turns where the person explicitly asks a practical question, since the
kernel's HOLD OFF ON ADVICE line does not distinguish. The panel now has a
"Copy my results" button that exports phase and chosen system per turn, and
returning visitors keep their saved picks (same storage key, same card order),
so the friend can export without redoing it.

Panel: <https://claude.ai/artifact/C3Aoq4ULsRar9smHR2q4xE> (three stacked
replies per turn, shuffled; both judges and the pooled result are shown only
after reveal). Judge outputs: `tools/cache/blind_judge_results_mistral-nemo.json`,
`tools/cache/blind_judge_results_ministral.json`.

<a id="dspy-critic-conversation-gate-2026-09-20"></a>

## Earlier: the DSPy critic could mutate the kernel mid-crisis, gated off in CONVERSATION, and a broken first attempt at fixing it, 2026-09-20

Follow-on from re-reading the friendship census closely (below): Gordon
asked to review the five turns BoneAmanita held silence on, specifically
whether silence was a genuine arbitrated choice or a symptom of something
failing quietly. Two (turns 20, 22) turned out to be the already-known
cursed-word bug, confirmed fixed by replaying the exact messages live. One
(turn 16, `"idk"`) was a real `TENSION_MAGNITUDE` hold: four voices
(GORDON, JESTER, ROBERTA, COLIN) genuinely fired at once with no fusion,
confirmed by instrumenting `StageManager.negotiate` directly rather than
trusting the census log - which can't be trusted for `MOOG`, because
`TheCortex.nominate_toxicity` resets `narrative_drag` to `0.0` as a side
effect of firing, so the post-turn snapshot the census records can never
show the value that actually crossed the threshold.

### The other two: `narrative_drag` really was over threshold, but not because of anything in the message

Turns 27 and 28 (calm, resolved "recovering"-phase content) both held on
`MOOG`. Instrumented before the reset: `narrative_drag` was genuinely at
55-56 against a limit of 12.8 at decision time - not stale, not a snapshot
artifact. Chasing where that came from surfaced something new: right at
the turns 24-25 boundary, `[Epigenetic Mutation]` fired -
`DSPyCritic.evolve_prompt` (`mechanics/dspycritic.py`), a second model
(`gemma4:e4b`) that watches `trauma_buffer` (populated *only* by Lexical
Firewall rejections, `brain/cortex.py:838`, with zero awareness of mode or
the person's state) and periodically synthesizes a new permanent axiom to
stop the firewall tripping again. What it produced: *"Tone must be
enforced as volatile... forbidden to employ any linguistic structure
designed to soothe, confirm, or reassure... default mode of failure is
preferred over a default mode of success."* Confirmed live (`brain/mind.py`,
`brain/composer.py:731`) that this axiom is not inert - it gets appended
to `GLOBAL_BASELINE.EVOLVED_AXIOMS`, which the composer reads into every
subsequent prompt regardless of mode. The distressed phase naturally
produces hedging language ("I understand," "that makes sense") that the
firewall exists to catch; the critic "fixed" that by permanently
instructing the model to stop soothing, right as the conversation moved
into its most vulnerable moment - directly contradicting the CONVERSATION
kernel's whole direction this week (candor *with* warmth). The
"malignancy" filter meant to catch bad axioms did not catch this one.

### Fix, and a bug in the fix

Gordon: *"Gate it off in CONVERSATION mode, or at the very least make it
far less aggressive."* Added `CORTEX.EPIGENETIC_MUTATION_DISABLED_MODES`
(`["CONVERSATION"]`, config-driven per the project's usual pattern) and
checked it in `DreamEngine._run_biological_rem` before calling
`evolve_prompt`; trauma still drains either way so it can't queue up and
fire the moment the mode changes. Two new tests
(`tests/test_biology.py`) passed, full suite green - and the fix did
nothing. Re-running the friendship census to confirm it live showed the
exact same axiom firing again, and `narrative_drag` peaking at **999**
(`PINKER` total peaking at **5015**, against a normal single-digit-to-low-
double-digit run) - worse than before, not fixed.

Root cause: the check read `self.eng.cortex.active_mode` from inside
`DreamEngine`, but `self.eng` there is not the same object that holds
`.cortex` - confirmed live, `self.eng.cortex` does not exist on that
reference at all. `active_mode` silently resolved to `""` every time,
which is never in the disabled-modes list, so the gate never actually
gated anything. The unit tests hadn't caught it because they built
`eng_ref` as a `MagicMock()` and set `.cortex.active_mode` on it directly
- that only proves the gating logic is correct in isolation, not that the
real object graph delivers a real mode string to it.

Real fix: `active_mode` is no longer read from inside `DreamEngine` at
all. `enter_rem_cycle` and `_run_biological_rem` now take it as a
parameter, and all five real call sites (`cycle.py`, `phases/biological.py`,
`phases/environmental.py` x2, `mechanics/commands.py`) pass
`self.eng.cortex.active_mode` (a reference that *is* reliably wired at
each of those sites) explicitly. Confirmed live against the actual boot
path, not a mock: `active_mode` resolves to `"CONVERSATION"` and the
critic is not called. New regression test
(`test_epigenetic_gate_reads_the_real_engines_active_mode`) exercises this
against the real, fully-booted engine specifically because a hand-built
mock is what let the first, broken fix pass. Mutation-tested: reintroducing
the old `self.eng.cortex` read broke exactly the two tests that should
catch it.

### Re-confirmed live

Same friendship script, same model, full fix in place: 29 of 30 turns
generated (previously 26-28 depending on run), only turn 16 held (the
genuine `TENSION_MAGNITUDE` case above). No epigenetic mutation fired.
`narrative_drag` max **6.42** (was 999), `PINKER` total max **41.47** (was
5015.62), mean 32.52 (was 529.89). Turns 27 and 28 both speak now. Full
suite: 584 passed, 5 skipped, 138 subtests.

**Correction, 2026-09-21:** the claim above that the friendship turns 27 and
28 holds came from the critic's axiom is wrong. Their drag of 55 to 56 is the
BENEDICT|GORDON synergy's +50 (see the diagnosis in the 2026-09-20 three-way
entry). The critic gate stands on its own merits; it did not cause or cure
those holds.

<a id="vanilla-blind-comparison-2026-09-19"></a>

## Earlier: a blind BoneAmanita-vs-vanilla comparison, and Ollama's silent context default bit twice in one day, 2026-09-19

Gordon, reading the friendship census: "truly remarkable; but I am quite
biased." Asked for a vanilla baseline (same script, same model, zero system
prompt, real conversation history, no metrics) and a genuinely blind
comparison, both an independent LLM judge and his own blind read. Two new
tools: `tools/audit_somatic_vanilla.py` and `tools/audit_somatic_blind_judge.py`
(`gemma4:e4b`, which generated neither transcript, shown "Reply A"/"Reply B"
with labels reshuffled per turn by a seeded coin flip so a fixed left/right
bias can't launder into a fixed system preference), plus a blind-read artifact
for Gordon's own pass.

### Two rounds of a length cap, both rejected as arbitrary

First vanilla run capped `max_tokens` at 450 (matched to BoneAmanita's own
ceiling): 20 of 30 replies cut off mid-sentence, because vanilla's unprompted
replies run far longer than BoneAmanita's budget-capped ones. Raised to 2000
as a quick fix; Gordon pushed back correctly - *"that's an arbitrary cap. do
we really need to limit it to 450?"* - 2000 is exactly as arbitrary as 450,
just a bigger number with no equivalent in "vanilla." Dropped `max_tokens`
entirely. A direct curl test confirmed the model then stops on its own
(`finish_reason: "stop"`, even past 1700 completion tokens) - looked fixed.

### It wasn't. The actual bug was the context window, not the output cap

Re-running with no cap still truncated 14 of 30 replies, but differently:
mid-word, and several collapsed to one or two words (`"This"`,
`"That walk was a physical manifestation"`) after only ~4 seconds - too fast
and too short to be a generation limit. The tell was `ollama ps`: the loaded
model's `context_length` read **4096**, Ollama's silent default, regardless of
what was sent. `/v1/chat/completions` (the OpenAI-compatible shim the script
was using) ignores an `options.num_ctx` override entirely - confirmed live by
sending one and re-checking `ollama ps`, unchanged. The native `/api/chat`
endpoint honors it (confirmed the same way, `context_length` moved to the
requested size). Vanilla's own real replies run 500-700+ words each; by
turn 4-6 the accumulated conversation had already filled 4096 tokens, and the
rest of the run degraded into context overflow, not overlength output.

This is the same defect already named in this file's open-items list (#8,
the reasoning-model fix): `gemma4:12b` filling Ollama's default 4096-token
context was known to cost 13% of production generations. It had never been
seen on the vanilla side before because nothing had asked the model for
30 turns of genuinely unbudgeted replies against the OpenAI-compatible shim.

Fixed in `tools/audit_somatic_vanilla.py`: switched to `/api/chat`, added
`"options": {"num_ctx": 32768}` (confirmed live it loads), replaced
`reasoning_effort: "none"` with that endpoint's equivalent, `think: false`.
Re-run: all 30 replies end cleanly, no truncation, no short-and-fast
anomalies. BoneAmanita's own side of the comparison was never touched -
its replies stay well under 4096 tokens all on their own, budget-capped by
the somatic contract - so this was purely a vanilla-side measurement fix, not
a change to what's being measured.

### Corrected result

`tools/audit_somatic_blind_judge.py --topic friendship` against the corrected
data: **BoneAmanita 22, Vanilla 3**, 0 ties, 0 unparsed, 5 turns skipped
(BoneAmanita held silence, nothing to pair against). An earlier run against
the truncated vanilla data had scored 23-2 - close to the corrected number,
but for the wrong reason: a separate bug in the judge script (turn-selection
checked dict-key presence, not reply truthiness, so held turns fed the
literal string `"None"` to the judge as BoneAmanita's answer) has also been
fixed. The 23-2 figure should not be cited; 22-3 is the number, from clean
data on both sides. The blind-read artifact's embedded transcripts were
regenerated from the corrected cache and republished to the same link.

### Not yet done

Gordon's own blind read of the artifact hasn't happened yet - the judge
result is one signal, not the verdict, per the tool's own docstring.

<a id="advice-restraint-cursed-word-bug-2026-09-19"></a>

## Earlier: a third census, an advice-restraint fix, and "feel" was a cursed word, 2026-09-19

Same day, third and final round. Gordon's read of the marathon transcript:
the conversation "felt much more natural," with one specific note - the
engine was too quick to offer advice or start solving a problem the moment
one was mentioned, unprompted. Asked for `reset.sh`, then one more scripted
conversation on a genuinely different topic to verify.

### The kernel gained a sixth line

CONVERSATION's `style_guide` gained item 6, **HOLD OFF ON ADVICE**: most of
what a person says is not a request to be fixed; do not default to advice,
instructions, or a plan the moment a problem is mentioned; wait to be asked.
Pinned to CONVERSATION only, same as items 4 and 5
(`tests/test_physics_to_prompt.py:TestRestraintOnAdviceGuidanceIsConversationOnly`).

### A third topic: friendship reciprocity, not another restoration project

Both prior scripts (sailboat, marathon) shared a shape: a physical project
tied to a parent, derailed by a sudden setback. The third,
`tools/audit_somatic_census.py --topic friendship`, is deliberately
different - a friendship that has quietly become one-sided, no object, no
parent, no physical goal - specifically because most of its early turns are
the person thinking out loud or venting, not asking for anything, which is
exactly the shape that would expose an engine too eager to solve. Same 30-turn,
five-phase structure (8/6/6/5/5) as the other two.

### Reset, then the run

`reset.sh` was run as asked (deletes `__pycache__`, `logs/`, `memories/`,
`saves/`, a handful of named lore/legacy files and test artifacts; does not
touch `tools/cache/`, source, or docs). `tools/cache/somatic_census.jsonl`
was separately found deleted from disk right after, with nothing in
`reset.sh` itself to explain it; Gordon had deleted it directly and
deliberately, so the new run would start a clean file instead of appending
onto the sailboat/marathon history. Not knowing that, `git checkout --
tools/cache/somatic_census.jsonl` restored the old committed version, so the
friendship run appended onto it anyway (120 lines: the original 90 plus 30
new), the opposite of what was intended. Trimmed back down to the 30
friendship records after the fact; the full history remains in git
(`cda575f` and earlier) for anyone who wants it back.

### The census: mostly clean, one real bug found

25 of 30 turns generated (83%), flagging 5/6, distressed 3/5, recovering 3/5.
Health held between 84.6 and 99.8 throughout; no topology-collapse false
positive this time. All five halts carry the calm, gate-specific text from
the previous entry's fix, confirmed live for the first time outside a unit
test - including the `GATEKEEPER` line ("Something in how that came through
didn't parse cleanly on this end...") in place of what would previously have
been the raw `CURSED_INPUT` string.

Two of those five `GATEKEEPER` halts (turns 20 and 22) were on completely
ordinary, well-formed sentences:

> "she called me crying tonight, her job let her go, and I spent two hours on
> the phone with her and I don't feel bad about that part"
> "I feel like a horrible person for even having these thoughts while she's
> going through this"

Traced with a `Nomination.__init__` patch around a direct `process_turn()`
call: both triggered `TheGatekeeper._audit_safety`
(`physics/filters.py:203-204`), which rejects a turn as `CURSED_INPUT`
whenever any word in it appears in `lore/lexicon.json`'s `"cursed"` list. That
list was `["future", "predict", "sentient", "secret", "human", "feel"]`,
seemingly meant to catch meta-awareness talk ("are you sentient?"). "feel"
and "human" are two of the most ordinary words in emotional English, and both
turns used "feel." The two people most likely to say "feel" in a sentence are
exactly the people D9's whole redesign exists to answer rather than refuse:
someone mid-crisis or carrying guilt.

Removed "feel" and "human" from the list; `"future"`, `"predict"`,
`"sentient"`, `"secret"` remain on the theory that they are rarer in ordinary
speech, a theory not re-verified here. Worth a second look if any of them
produces the same failure. New regression:
`tests/test_gates.py::test_ordinary_feelings_do_not_trigger_cursed_input`,
calling `TheGatekeeper._audit_safety` directly against the two exact failing
sentences plus a plain "I'm only human" control. Confirmed live end to end:
re-running the same two messages through a real `process_turn()` after the
fix now reaches `GEODESIC_FRAME` (an answered turn), not `SILENCE`.

Worth naming as its own finding, separate from the specific word list: this
mechanism checks the *person's own input* for words a meta-aware AI might use,
which is backwards from what it likely should guard - the model's output
claiming sentience, not the person mentioning it exists. Not redesigned here;
flagged for whenever this area gets revisited.

### The advice-restraint line, read against the transcript

Comparable early-conversation turns: marathon (before) - *"You need to focus
on building a consistent base before you start pushing for distance... Don't
try to run the full miles every time"* - prescriptive advice for what was
just excited context-sharing. Friendship (after), the tiring/flagging/
distressed/recovering phases (turns 8-29) hold back consistently: *"You don't
have to decide exactly what it means right now. We can just sit with the fact
that it weighs on you,"* *"The silence is your right here,"* *"Just rest."*
Advice appears exactly where it was asked for (turns 5 and 7, both explicit
requests) and is answered directly there. The early "engaged" phase (turns
0-4, 6) still leans toward unsolicited interpretation ("It usually means the
dynamic has shifted...") rather than outright advice - softer than the
marathon pattern, not fully gone. Partial improvement, honestly reported as
such; worth another look specifically at the engaged-phase framing if this
still reads as too quick to interpret.

Firewall held: one em dash across 25 replies, no antithesis slipped through.

### Verification

Full suite after the advice-restraint line: 580 passed. After the cursed-word
fix: **581 passed, 5 skipped, 138 subtests passed**. Continuously green
through every step today.

<a id="silence-reason-tone"></a>

## Earlier: the Stage Manager's reason, made safe for a person to actually read, 2026-09-19

Same day, continued again. The entry below added `verdict.reason` to the text
a person sees when the Stage Manager holds. Gordon read a real example and
caught the problem immediately:

> `**System:** _(Silence - Stage Manager held the floor empty - CURSED_INPUT:
> The Gatekeeper recoils. Cursed syntax detected.)_`

`verdict.reason` is each gate's own technical string, written for logs and
receipts, not a person to read. Checking every gate a `Nomination` can carry
found the same problem throughout, not just the one example:

```
gatekeeper_cursed  -> "The Gatekeeper recoils. Cursed syntax detected."
gatekeeper_toxic   -> "IMMUNE REACTION: Input rejected as pathogenic."
PINKER             -> "Structural rot critical."
ROS_PANIC          -> "Counterfactual simulation indicates fatal ROS toxicity..."
```

Raw internal tags concatenated onto the message (`f"{type_str}: {msg}"` in
`physics/filters.py`), and phrasing that reads as blaming the person's own
input for being "cursed" or "pathogenic" is exactly wrong to show someone,
especially since the people most likely to trigger a hold are the ones D9
already weighs most carefully: distressed or exhausted.

Two gates are explicitly crisis-adjacent: `LINEHAN` (as in Marsha Linehan,
DBT; fires on near-total exhaustion with zero resonance) and `AFFECTIVE`
(fires on high exhaustion plus high friction). Their actual text:

- LINEHAN: *"Terminal User Exhaustion detected. Resonance is zero. Applying
  absolute Friction to protect cognitive load."* Cold and clinical.
- AFFECTIVE: *"Hey. Take your hands off the keyboard. The machine doesn't
  care if you bleed on it, but I do."* Trying to be warm, but "bleed on it"
  is body/harm-adjacent language aimed at someone the system has just flagged
  as highly exhausted. Not something to reword unilaterally.

Brought both to Gordon directly rather than guessing. Decided: plain and
calm, no metaphor, for both, same standard as everything else.

### The fix

`Verdict` (`archetypes/stage.py`) gained a `gate: str = ""` field, set from
`winning_nom.gate` on a nomination-driven hold, and from two new synthetic
labels (`ATP_FLOOR`, `TENSION_MAGNITUDE`) on the Stage Manager's own two
non-nomination holds. `lore/ux_strings.json` gained a `silence_reasons`
domain: one calm, plain-English line per gate, an explicit `_default` for
anything unlisted, and a `_comment` stating the rule for future entries (no
internal tags, no jargon, nothing that reads as blaming the input).
`_hold_the_silence` (`phases/cognitive.py`) now shows that translation in the
`ui` field a person reads; `verdict.reason` stays exactly where it was
already useful, unchanged, in `logs` and `mind.context_msg` for telemetry
and receipts.

```
LINEHAN    -> "I want to slow down for a second here. There's no rush to keep going."
AFFECTIVE  -> "Let's pause for a moment. This can wait until you're ready."
GATEKEEPER -> "Something in how that came through didn't parse cleanly on this
               end. Try sending it again, maybe rephrased or a bit shorter."
```

`tests/test_stage_manager.py` gained `TestSilenceReasonsAreHumanSafe`: a roll
call asserting every gate a real `Nomination` is constructed with in
production has its own entry (not a silent fallback to `_default`), a
forbidden-word sweep across all of them ("cursed", "pathogenic", "exploit",
"bleed", and the exact clinical phrases above), and an explicit check that
LINEHAN and AFFECTIVE specifically carry no body or harm language. Plus a
direct regression: the raw technical reason must never appear in `ui`, and
must still appear in `logs`/`mind.context_msg`.

### Verification

Full suite after this fix: **578 passed, 5 skipped, 135 subtests passed**.
Continuously green through every step in this session.

<a id="firewall-topology-second-census-2026-09-19"></a>

## Earlier: reading the census closely, the Lexical Firewall widened, a live-killing topology bug found and fixed, a second topic confirms it, 2026-09-19

Same day as the entry below, continued. Gordon read the 30-turn sailboat
census transcript directly (not just the summary numbers) and found two real
problems the aggregate statistics couldn't show: occasional em dashes and
antithesis ("not X, but Y") that the Lexical Firewall was missing, and a
tonal drift where flagging/distressed replies narrated the person's situation
back at them instead of answering them directly. Fixing both, then verifying
on a second, unrelated topic, surfaced a serious bug that had nothing to do
with either fix.

### The Lexical Firewall: two real gaps, one deliberately not closed

`NEGATIVE_COMPARISON` (`lore/style_crimes.json`) only matched "not X, but Y"
linked by a comma or dash inside one sentence. A live turn had three
uncaught antithesis constructions split across sentences and a semicolon:
*"it isn't a monument. It's a transition. You aren't building a shrine; you're
honoring him..."* Widened to also match a negation clause ending in `.`/`!`/
`;` immediately followed by "It's/They're/You're/We're/That's", verified
against the exact failing text plus a set of plain-negation controls that
must NOT fire (`tests/test_composer.py:TestNegativeComparisonDetection`).

Em dashes were deliberately **not** given a hard numeric cap after discussion:
occasional use is normal writing, and D2's own "coarse proxy, not grammar
police" ethos argues against a strict reject rule here. Instead,
`lore/system_prompts.json` CONVERSATION style_guide gained item 4: real people
reach for a semicolon, an Oxford comma, or parentheses before a dash in
spoken conversation; formal writing and literature are unrestricted. A "time
and place" preference, not a validator rule.

### The tone finding: candor without presence

Reading the sailboat census's flagging/distressed replies found a pattern:
*"She just cut the cord on your time with it... It's a betrayal of the work
you were trying to do in private"* — narrating the person's situation from
outside it, like a narrator summarizing a character, rather than answering
them. Traced to the kernel's "Candor over empathy" line: it named what not to
do (empathy-guessing, banned separately by the firewall's `SYRUPY_EMPATHY`
pattern) but never named what presence actually looks like, so the model
filled the gap with detached analysis. New style_guide item 5, **RESPOND, DO
NOT NARRATE**, names the failure mode with the real example and asks for
first-person, direct address instead. Both new lines are pinned to
CONVERSATION only, absent from ADVENTURE
(`tests/test_physics_to_prompt.py:TestPunctuationGuidanceIsConversationOnly`,
`TestPresenceOverNarrationGuidanceIsConversationOnly`).

### Also: the Stage Manager's reason now reaches the person

Gordon asked for a small description of why the Stage Manager chose silence,
when it does. `_hold_the_silence` (`phases/cognitive.py`) always computed
`verdict.reason` but only ever logged it internally; the text a person
actually saw was the generic "nothing is ready to be said" line. It is now
appended to the `ui` field that reaches them
(`tests/test_stage_manager.py::test_the_ui_text_explains_why`). **This surfaced
a second, more serious problem, covered in the next entry
(`SESSION_HANDOFF.md#silence-reason-tone`): several of the raw reason strings
this exposes are not fit for a person to read as-is.**

### The bug the second census found: a live-killing false positive in the topology check

Running a second scripted conversation (`--topic marathon`, same phase shape
as the sailboat script, different subject: marathon training derailed by
injury) to confirm the firewall/tone fixes on fresh material found the
engine dying at turn 10 of 30 and staying dead. Cause: today's earlier
`calculate_clustering` fix (see the entry below) had activated a
terminal-shutdown check that had *never once run in production before*, and
its comparison logic was broken in two ways a working implementation finally
exposed:

1. **Zero-versus-zero.** A real 10-node conversational memory graph is sparse
   and tree-like this early, with no triangles; a random rewiring of that
   same sparse graph is equally triangle-free. Comparing 0.0 to a null
   baseline of 0.0 is not evidence of collapse, but the original comparison
   (`actual <= null * 1.05`) treated it as fatal proof and executed an
   irreversible shutdown.
2. **Single-sample noise**, found on a second reproduction after fixing (1):
   one random rewiring or configuration-model draw is one noisy sample; a
   sparse, small graph can land a stray triangle, or none, by pure chance.

Fixed in `cycle.py:_verify_semantic_topology`/`_bg_topology_check`:

- Minimum graph size raised from 6 nodes to `CORE.TOPOLOGY_MIN_NODES` (20).
  The same discipline `GATE.MIN_CORPUS` already applies to the governor's own
  null comparison, for the same reason: small-n statistics need a real floor.
- Both null estimators (rewire and configuration-model) are now averaged
  over 5 independent draws each, not a single draw.
- The null baseline must clear `CORE.TOPOLOGY_NULL_FLOOR` (0.05) before "no
  better than null" is treated as meaningful; comparing a value against noise
  is not evidence anything collapsed.
- A single crossing is no longer terminal. `CORE.TOPOLOGY_COLLAPSE_STRIKES`
  (3, matching the embedding fallback's own consecutive-failure count for its
  terminal transition) must be reached on **consecutive** checks before health
  is actually set to zero; any declined or negative check resets the count.

`tests/test_chaos_engineering.py` rewritten with three validated fixtures
(stress-tested 10+ seeds, 5 repeated full runs, all stable): a dense bipartite
graph (real collapse, needs all 3 strikes to fire), a 30-node sparse path
(declines to judge, the exact bug reproduced), and 5 bridged 4-cliques
(healthy, does not fire). The clique-count-over-clique-size finding is worth
keeping: denser individual communities give the null models more chances to
grow incidental clustering too, shrinking the real gap; more, smaller
communities is the reliable construction.

### The re-run: clean

With the fix in place, the marathon census completed all 30 turns: 28 of 30
generated (93%), flagging 6/6, distressed 4/5, health held between 83.5 and
99.8 throughout. Both halts (turns 13, 20) carry the same clean Stage Manager
reason. Cache: `tools/cache/somatic_census.jsonl`, run `20260919-122608`.
`tools/audit_somatic_census.py` gained `--topic` (`sailboat` default,
`marathon` new), so a second scripted conversation is a flag away rather than
a hand edit, specifically so a fix is not just verified against the one
transcript that found it.

The tone fix shows up directly in the transcript. Sailboat flagging phase
(before): *"The timber will wait for tomorrow's light,"* *"The wood doesn't
care about the timing"* — deflecting to object logistics. Marathon flagging
phase (after): *"I am right here with you in the quiet,"* *"I am here in this
space with you."* Worth watching, not yet a problem: those six replies now
converge on their own "I'm here in this space" refrain. A better failure mode
than before, still a formula.

Firewall: one em dash total across 30 replies, both single instances, and no
negative-comparison antithesis slipped through, including a phrase that
correctly did *not* fire (*"It was never just the race. It was the goal..."*,
plain rhetorical contrast, not the AI-tell pattern the rule targets).

### Verification

Full suite after the firewall and tone changes: 570 passed. After the
silence-reason fix: 571. After the topology-check overhaul: 574. All are
5 skipped, 29 subtests passed, no failures at any point. `config.json.bak`
(byte-identical to the gitignored `config.json`, produced by some boot path
during direct engine construction outside the test harness) is untracked and
safe to delete.

<a id="d9-d1-d2-census-2026-09-19"></a>

## Earlier: D9 unified, D1 completed, D2/D2b rebuilt, and the confirming census, 2026-09-19

Starting state: clean `6d7fd0b` (`20.7.1.3`). This session audited D1/D2/D9 against
their own written acceptance criteria (the roadmap's own next step after the
refusal-test repair below), found each partially complete, fixed what it found,
then ran the D0b/D9 live census the fixes were prerequisite to. Most of the code
changes landed in `a90ce06` (`20.7.2`) mid-session; the census tool fix below was
made afterward and is, as of this writing, uncommitted.

### D9: four refusals were still bypassing the Stage Manager

Auditing D9's own "done when" (no gate stops a turn on its own) found
`SimulationPreflightPhase.run()` (`phases/cognitive.py`) still had four hardcoded
short-circuits, each setting `ctx.refusal_triggered` and returning directly,
one phase before `ArbitrationPhase` ever runs: `NABLA_SILENCE` (a `[SILENCE]`
tag), `APOPTOTIC_BLOCK` (a zero-width-character exploit), `PREMISE_VIOLATION`
(a slash-command asking to analyse code with none attached), and
`POINT_OF_NO_RETURN` (deploy/schema-change language without `CONSENT`). None of
the four ever touched `ctx.nominations` or `StageManager.negotiate()`, none
read the person's state, and none had any test coverage. The other seven gates
(MOOG, GORDON_ANCHOR, PINKER, LINEHAN, AFFECTIVE, ROS_PANIC, the gatekeeper)
were already correctly migrated to `Nomination` objects.

Fixed: all four now append a `Nomination` with their own reason and magnitude
100.0 (uncapped magnitude means an extreme case still holds, per
`StageManager.negotiate()`'s `winning_nom.magnitude >= 100.0` override) and
return, letting `ArbitrationPhase` decide. Five new regression tests cover each
path plus the case where a nomination's magnitude is capped by
`somatic_budget`. Full suite went from 525 to 535 passed, 5 skipped, 29 subtests.

### DSPyCritic no longer piggybacks on the answering model

`DSPyCritic` read the same `MODEL` key as `LLMInterface`, so it always ran on
whatever D7 tuned for somatic compliance (`gemma4:12b`), for a boilerplate/
faithfulness filter that has no need of that. New `BoneConfig.DSPY_MODEL`
(`gemma4:e4b`), read first in `mechanics/dspycritic.py`; `MODEL` is untouched.
Full suite wall clock dropped from about 14 minutes to about 7, same 535
passed. This is the only change in this entry that is also a production
behaviour change outside the somatic tracks, and only for the critic's own
generations, not the answering model.

### D1: two gaps against its own written contract

`body/somatic_budget.py:SomaticBudget.evaluate()` existed and was wired
everywhere D1 asks, but:

1. **Every threshold was hardcoded in Python**, contradicting D1's own line
   "Constants live in `BoneConfig` (A1's rule)". Moved to a new
   `BoneConfig.SOMATIC_BUDGET` section (19 keys) mirrored into
   `lore/tuning_presets.json`, following the same pattern as `STAGE`/`GATE`:
   a hardcoded Python fallback plus a JSON copy that overrides it at boot.
   `REQUIRED_CONFIG` updated so the boot audit catches a dropped key.
2. **`engine_state` never carried respiration**, only `atp_pool`/`ros`, even
   though D1's own spec lists "ATP, respiration, ROS, chemistry" as the four
   engine inputs. The old (now-retired) ANAEROBIC directive fired on a single
   costly turn (`raw_cost > BIO.ANAEROBIC_THRESHOLD` in `body/metabolism.py`),
   a different signal than the pool's cumulative level: a turn can spike
   ANAEROBIC while ATP is still healthy. `phases/biological.py` now passes
   `ctx.bio_result["respiration"]` through; `SomaticBudget.evaluate()` tightens
   the cap on it independently (new `SENTENCE_CAP_ANAEROBIC`/
   `RETRY_ALLOWANCE_ANAEROBIC` config, default 5/2, milder than full ATP
   depletion's 3/1). This also let `tests/test_physics_to_prompt.py` drop a
   hack that faked `atp=10.0` whenever respiration was ANAEROBIC to get the
   old behaviour by a side door.

New `tests/test_somatic_budget.py` (mutation-style: moves a config threshold,
confirms the decision moves with it, the same discipline A4 uses) and a new
`TestSomaticBudgetReachesThePrompt` class in `test_physics_to_prompt.py` that
constructs `SomaticBudget` objects directly and pins each field's own effect
on the composed text, satisfying D1's "done when" (`test_physics_to_prompt.py`
extended to pin budget in, text out) directly rather than through the
composer's own re-derivation, which the existing tests only exercised
indirectly.

### D2: the audit tool was measuring a mechanism that no longer runs

`tools/audit_somatic.py`'s `compose_arms()` patched `_derive_bio_mood` and
`ux()` to inject the retired directive strings ("ANAEROBIC STATE. Raw,
breathless, efficient prose.", the old exhaustion line), neither of which
exists in the composer since D2 landed, and hardcoded `"somatic_budget": None`
into every arm's state, which skips the entire SOMATIC CONTRACT block the
composer now renders. It could not have detected D2 shipping. Three further
breakages, unrelated to D2's wording and pre-dating this session, meant the
tool could not even run: `verify_manipulation()` was called but never defined
(latent `NameError`); `patch("...PromptComposer._get_lore")` targeted a method
that no longer exists (`self.lore` is a plain dict now); and `compose()` was
called with `user_input=` against a real signature of `user_query=`, so every
arm silently composed in `ADVENTURE` mode (no `state["meta"]["active_mode"]`
was ever set) atop the two prior bugs.

Rebuilt: `compose_arms()` now builds real `SomaticBudget` objects via a new
`budget_for()` helper, the same call `phases/biological.py` makes every turn.
`somatic_block_text()` mirrors the composer's full SOMATIC CONTRACT rendering
(not just the cap line), so `check_arms()` verifies the composer said exactly
what the budget implies. `EXPECTED_DIFF` updated for the current line shapes,
including a second telemetry line (`[E:... | V:...]`) the old regex never
covered. The one stale unit test in `tests/test_audit_somatic.py` (built on
the retired constants) is rewritten against the new contract.

Verified live: dry-run arm construction against a real composer, then a full
generate-cache-analyse smoke run (3 messages, 1 repeat, `gemma4:e4b`) with no
errors and sane per-arm text. Not run: the real 20-message x 8-repeat
statistical pass this tool exists to produce; that is still open, now that the
tool can actually produce it.

### D2b: accommodation measures and a third persona

`body/somatic_metrics.py` (shared with the D3 validator, per the roadmap's own
instruction) gained five measures: `reply_to_message_ratio` (reply length
relative to the partner's own message), `ends_with_question` (closing-question
rate), `offers_to_carry_load` (a phrase-pattern proxy: "I'll carry", "let's
share", etc.), `mirrors_affect` (a curated shared-affect-word proxy between
reply and message, not a sentiment lexicon), and `question_count`. D2b also
asks for "choices offered" and "instructions given"; neither has a defensible
regex proxy and both are left unmeasured rather than guessed at, noted in the
module docstring.

`tools/audit_somatic.py` gained a `DISENGAGED` arm: flagging exhaustion *and*
critically low effort, the only combination that actually sets
`offer_to_carry_load`. `CONTROL`/`EXHAUSTED` double as D2b's "fresh"/"tired"
personas rather than adding two redundant arms. `ARMS` widened from
`(respiration, exhaustion)` to `(respiration, exhaustion, effort)` throughout.

Verified live in the same smoke run as D2, including the `DISENGAGED` arm's
full SOMATIC CONTRACT block (cap, no-narration, no-closing-question, and the
new carry-load line, all four present together). Not run: the statistical
pass D2b's own "done when" asks for (a tired or disengaged partner measurably
getting a lighter reply than a fresh one, with intervals, on two models).

### The census: D0b and D9 both confirmed live

`tools/audit_somatic_census.py` also imported the now-deleted
`ANAEROBIC_DIRECTIVE`/`EXHAUSTION_DIRECTIVE` constants from `audit_somatic.py`
(a fourth file this session's D2 changes would have silently broken).
Replaced with substring checks against the current SOMATIC CONTRACT wording:
`SOMATIC_CAP_TIGHTENED`, `SOMATIC_NO_CLOSING_QUESTION`,
`SOMATIC_OFFER_TO_CARRY_LOAD`.

With that fixed, ran the real 30-turn census against `gemma4:12b` (persistence
patched off, live embeddings, the real engine): `.venv/bin/python
tools/audit_somatic_census.py --model gemma4:12b`. Cache:
`tools/cache/somatic_census.jsonl`, run `20260919-095553`.

**D0b, confirmed**: 27 of 30 turns (90%) generated a real reply. By phase:
engaged 8/8, tiring 5/6, **flagging 6/6**, distressed 4/5, recovering 4/5. ATP
held between 23 and 52 across the whole run and never crashed. The flagging
phase, the one D0b's tolerances were specifically sized for, answered every
turn.

**D9, confirmed**: all three halted turns (13, 22, 26) carry the identical
Stage Manager reason, "The Stage Manager holds the floor empty. Nothing here
is ready to be said yet." — not `MOOG_QUARANTINE`, `SYSTEM_HALT`,
`COUNTERFACTUAL_REJECTION`, or any of the four hardcoded bypasses fixed above.
The ATP ledger shows exactly three `-6.0, "Stage Manager: negotiated silence"`
entries, matching the three halts one for one: the ATP cost of declining is
being charged from the one place D9 asks for, not by an independent gate.

**D1, shown moving live**: `somatic_cap_tightened` fired on 18 of 27 generated
turns; `offer_to_carry_load` fired on 17, tracking `P_u` hitting 0.0 four
separate times across the script. This is the first live evidence the budget
object actually tracks a real conversation rather than resting at one value,
which is what D0's original census went looking for and could not find in the
old five-path mechanism.

### Found, not fixed

A warning fired once during the census: `[CYCLE] Async Topology Error:
'MycelialNetwork' object has no attribute 'calculate_clustering'`. Unrelated
to any of the above; next task.

Also produced, not part of the repo: `config.json.bak`, byte-identical to the
gitignored `config.json`, written by some boot path during today's direct
`BoneAmanita(...)` construction outside the test harness. Content is
unaffected (verified identical); the file itself is untracked and harmless to
delete.

### Verification

Full suite after every change above except the census tool's own fix (which
has no test coverage; verified instead by the live census run itself
completing cleanly): **559 passed, 5 skipped, 29 subtests passed**, about
6 minutes 43 seconds. This is the current full-suite baseline.

### Next

Two statistical passes are now unblocked but not run: D2's two-model
comparison (does the share of replies within cap rise, does body narration
stay flat) and D2b's accommodation pass (does a disengaged partner measurably
get a lighter reply than a fresh one). Then the topology-check bug above.

<a id="refusal-tests-2026-09-18"></a>

## Earlier: seven refusal-test failures repaired, 2026-09-18

The seven previously recorded failures now pass in the focused run. This round
changes only five test files, not production refusal logic or thresholds.
It preserves the uncommitted embedding and atomic quicksave repairs on top of
`8069778`.

### Causes and corrected contracts

- Cortex and Moog fixtures used unspecced `MagicMock` physics objects. Their
  fabricated `to_dict()` methods took precedence in `dump_state`, so assigned
  dictionary fields never became the numeric input being tested. Real
  `PhysicsPacket`, `EnergyState`, and `CycleContext` objects now exercise the
  production serialization boundary. Numeric gate values no longer originate
  in fabricated mock methods.
- Gate-tolerance and scar tests referenced `MagicMock` without importing it.
  They now use the same concrete packet/context types rather than adding an
  import that would retain the faulty serialization fixture.
- Tests of the adventure counterfactual and Moog gates explicitly set a 1.0
  tolerance on a config instance. Conversation comparisons retain 1.6. This
  fixes the test setup rather than retuning production thresholds.
- The productive-worry test expected preflight to halt immediately. D9 moved
  that decision to arbitration, and its original ROS fixture was also below
  the widened conversation threshold. It now supplies maximum accumulated ROS
  plus high friction at tolerance 1.6, verifies the ROS nomination and scar,
  confirms preflight does not halt or spend ATP, then runs real arbitration.
  It asserts final `SILENCE`, the winning reason in the packet and receipt,
  and exactly one configured silence charge. The extreme-tolerance test also
  verifies the final arbitration outcome, not just the nomination count.

The original assertions about gate identity, toxic versus tolerated input,
scar creation, and preserving MIND remain. Final refusal follows the documented
Stage Manager contract; no production gate was weakened to make tests pass.
This does not establish completion of every D9 route or live accommodation.

### Verification and next work

The first fixture correction run returned **32 passed, 1 failed**; the remaining
failure was an attempted direct read of an optional ROS config key in the new
fixture. The final focused run covered cortex, gate tolerance, Moog, random,
scars, and Stage Manager: **54 passed, 4 subtests passed**, in 25.22 seconds.
The complete suite test run (`python -m pytest -x -q`) successfully passed all tests:
**525 passed, 5 skipped, 29 subtests passed** in 293.09 seconds. The test baseline
is now completely green.

Tests run in `/tmp/boneamanita-refusal.ws3uwms6`, a disposable copy of the
working files, Git metadata, and the untracked quicksave tests, with Python
3.14.7. Logs are `/tmp/boneamanita-refusal-focused.log`,
`/tmp/boneamanita-refusal-focused2.log`, and `/tmp/boneamanita-refusal-full.log`.
The user's live saves and lore are untouched.

Next: audit D1/D2/D9 against their acceptance criteria and refresh the somatic
audit arms before live census/accommodation measurements. Green regression
checks alone do not certify model behavior.

<a id="quicksave-repair-2026-09-18"></a>

## Earlier: atomic quicksave repair, 2026-09-18

R2 is repaired in `protocols/chronos.py`. The working tree started at `8069778`
with the embedding repair and its documentation/tests still uncommitted. Those
changes were preserved. R1/R1b and R3 are also repaired; the seven existing
refusal-test failures are the next work package.

### Checkpoint contract

Quicksave writes a unique `.quicksave-*.tmp` file in the save directory,
serializes the existing checkpoint schema, flushes and fsyncs the file, closes
it, then publishes it with `os.replace`. Keeping both paths on the same
filesystem permits atomic replacement. The previous checkpoint is never opened
for writing. Serialization, partial-write, file-sync, and replacement failures
leave it byte-for-byte intact and retain the existing failure message/log path.
A failed first save leaves no checkpoint. Temporary files are removed after
handled failures; cleanup errors are logged without hiding the original error.

This is atomic file publication, not a broader checkpoint schema change or a
power-loss durability guarantee. A hard process kill can leave an unpublished
temporary file, and the containing directory is not fsynced. Concurrent saves
use separate temporary files; the last successful replacement wins.

### Verification

Five new tests in `tests/test_quicksave.py` cover partial JSON writes, circular
(nonserializable) history, fsync/replace failures, failed first save, and a
successful replacement that publishes complete flushed JSON. The old code
failed these regression scenarios. The focused selection of quicksave, macro,
protocol, genesis-continuity, and shutdown tests passed: **21 passed,
2 subtests passed**, in 21.20 seconds.

The full run (`python -m pytest -q --tb=short`) finished with **518 passed,
7 failed, 5 skipped, 29 subtests passed**, in 277.26 seconds. All five new
quicksave tests passed, including both fsync/replace subcases. The seven failure
nodes are unchanged from the baseline. This run covers `8069778` plus the
embedding and atomic quicksave source/test changes; those files match the
tested copy byte-for-byte. No live-model behavioral audit was run.

Tests run in `/tmp/boneamanita-quicksave.sxd0lf19`, a disposable copy of the
tracked working tree (including the embedding edits), Git metadata, and the
new quicksave test file. The project Python 3.14.7 interpreter is used. Logs are
`/tmp/boneamanita-quicksave-before.log`, `/tmp/boneamanita-quicksave-after.log`,
and `/tmp/boneamanita-quicksave-full.log`. Tests use temporary save directories;
the user's live saves and lore are untouched.

Next: repair the seven refusal-test failures against the nomination/arbitration
contract, without weakening behavioral assertions. Then validate D1/D2/D9 and
run the current somatic measurement arms.

<a id="embedding-repair-2026-09-18"></a>

## Earlier: embedding fallback repair, 2026-09-18

Starting state: clean `8069778` (`7.0.14.2`), including the committed shutdown
repair. This follow-up repairs R1/R1b in `spores/embeddings.py`; R2 (atomic
quicksave) and the seven existing refusal-test failures remain open.

### Fallback contract

- Vector width is fixed at backend resolution. Runtime degradation retains
  that width so existing FAISS indexes and rank banks remain shape-compatible.
  Booting directly into hash still uses the historical eight dimensions.
- A transient failure marks the embedder degraded immediately and returns hash
  coordinates for the entire sweep, including any semantic cache hits. The
  receipt names hash/SHAKE-256 as the vector source and includes the failure.
- Temporary hash results are never stored under semantic cache keys. Healthy
  cached entries survive a transient outage; failed texts retry the backend on
  their next request. Successful backend work clears the transient degraded
  state and consecutive-failure counter. Cache-only requests do not prove
  backend recovery and do not clear that state.
- After three consecutive failed backend sweeps, the embedder switches to hash,
  clears semantic cache entries, and caches only under the hash identity.
  This terminal fallback still requires engine restart/reconfiguration to
  restore a semantic backend; automatic recovery from that state is not added.
- Each backend batch is validated for row count, width, numeric values, and
  finite coordinates before any result enters the cache. Malformed output
  follows the same failure path as a transport error.
- An instance lock serializes backend calls, transitions, and cache updates
  so concurrent callers cannot write fallback vectors under a changing identity.

Hash remains non-semantic. Fixed dimensions prevent shape errors; they do not
make old semantic vectors comparable to new hash vectors. This repair does not
re-embed persisted memories or add per-vector provenance to downstream stores.

### Verification

The regression tests reproduced the old transient receipt/cache bug, the
16-to-8-dimensional transition, and five malformed-vector cases. The first
post-repair selection (`tests/test_embeddings.py tests/test_receipts.py
 tests/test_resonance.py tests/test_memory.py tests/test_spores.py`) returned
**81 passed, 5 skipped, 5 subtests passed** in 48.20 seconds. Two additional
regressions then covered concurrent recovery and mixed cached/uncached sweeps.
All transport failures and recoveries are mocked; no live outage was induced.

The complete suite (`python -m pytest -q --tb=short`) finished with **513 passed,
7 failed, 5 skipped, 27 subtests passed**, in 277.54 seconds. All five new
embedding tests, including five malformed-vector subcases, passed. The seven
failures match the baseline exactly. This result covers `8069778` plus
`spores/embeddings.py` and `tests/test_embeddings.py`; both files were verified
byte-for-byte against the tested copy. No live behavioral audit was run.

Tests run in `/tmp/boneamanita-embedding.zjjoybcq`, a copy of tracked files with
Git metadata and the changed source/tests, using the project Python 3.14.7.
Temporary logs are `/tmp/boneamanita-embedding-before.log`,
`/tmp/boneamanita-embedding-after.log`, and `/tmp/boneamanita-embedding-full.log`.
The user's saves and lore are untouched.

Next repair: preserve the last valid quicksave when serialization or writing
fails. Then repair refusal fixtures/contracts and validate D1/D2/D9 behavior.

<a id="stabilization-2026-09-18"></a>

## Earlier: baseline reproduction and shutdown repair, 2026-09-18

This follow-up supersedes the review's R3 status. R1/R1b (embedding fallback)
and R2 (quicksave) remain open, as do the seven refusal-related test failures.
The user authorized the proposed stabilization work; this first work package
reproduces the baseline and repairs engine/fixture shutdown.

Starting state: clean `8bdd960` (`7.0.14.1`). The formerly uncommitted review
changes are now committed. Tests ran in a disposable copy of tracked files
with `.git` metadata, using the project's Python 3.14.7 interpreter. The new
shutdown tests and the two modified Python files were copied into that checkout
for validation. No tests ran against the user's live saves or lore.

### What changed

- `GeodesicOrchestrator.shutdown()` clears `is_running`, joins the cycle daemon,
  then waits for the background executor. The existing engine shutdown order
  therefore reaches persistence and telemetry only after those producers finish.
- An idle daemon checks the stop flag after its queue timeout so it does not
  begin a REM tick while shutdown waits for it.
- `BoneTestCase` registers cleanup with `unittest.addCleanup`: the captured
  engine is shut down before its patches and shared resources are released,
  including when a subclass raises after base setup. Fixture cleanup patches
  `perform_shutdown` to avoid persisting test state.
- Four regressions cover idle/repeated shutdown, a running background worker,
  an active daemon turn, and a subclass setup failure. The first three authored
  regressions (idle, worker, setup failure) all failed against the old code;
  the active-turn case was added afterward.

Shutdown waits for active work to return; it does not cancel an in-flight model
request or promise a fixed shutdown deadline. Call shutdown from the owning
thread, outside the daemon and its workers.

### Baseline evidence and next work

Before edits, running `tests/test_cortex.py tests/test_gate_tolerance.py
 tests/test_moog.py tests/test_random.py tests/test_scars.py` with
`python -m pytest -q --tb=short` reproduced the same seven failure nodes listed
in the review: **26 passed, 7 failed**, in 17.38 seconds. After the first three
shutdown tests and cleanup repair, adding `tests/test_shutdown.py`,
`tests/test_cycle.py`, and `tests/test_architecture.py` returned **43 passed,
7 failed**, in 23.94 seconds. These are overlapping selected runs.

The complete post-repair run, `python -m pytest -q --tb=short`, finished with
**508 passed, 7 failed, 5 skipped, 22 subtests passed**, in 277.51 seconds.
All four shutdown regressions passed. The seven failure nodes are unchanged
from the reproduced baseline; no additional failures appeared. This result
covers `8bdd960` plus the changes to `cycle.py`, `tests/base.py`, and the new
`tests/test_shutdown.py`. It supersedes the earlier selected-run baseline.
The disposable checkout was `/tmp/boneamanita-stabilize.aul7jckc`; the full log
was `/tmp/boneamanita-stabilize-full.log`. These temporary artifacts are not
required to interpret the recorded result.

The refusal tests have not been weakened or repaired. Inspection shows that
unspecified `MagicMock.to_dict()` values enter `dump_state`, and that preflight
nominates while arbitration decides the final refusal. Follow-up tests should
use concrete physics state and assert both boundaries; missing `MagicMock`
imports alone do not establish that the remaining fixtures are sound.

Next: atomic quicksave preservation, embedding fallback/cache/index contracts,
and refusal-fixture/contract repairs, followed by a fresh complete suite and
D1/D2/D9 acceptance audit. Live somatic measurements remain outstanding.

<a id="review-2026-09-18"></a>

## Earlier review and documentation reconciliation, 2026-09-18

This section supersedes older present-tense status, test totals, and next-step
instructions below. Older entries are retained as session history, not as a
description of the current working tree. Standing project decisions, including
preserving the biological vocabulary, still apply.

### Scope and authorization

Codex reviewed the repository, ran tests in a temporary copy, and reproduced
three runtime failure areas with isolated probes. The user's follow-up was:
"Do not attempt to repair anything; just prep the next round with the handoff
and make sure our readme is being honest."

This follow-up changes documentation only (`README.md`, this file, and the
roadmap's current-status descriptions). **None of the defects below has been
repaired, and no new regression tests have been added.** The next-round list is
a proposed work plan, not authorization to begin repairs in this documentation
session. No live-model behavioral audit was run in the review or this follow-up.

### Reviewed state and existing user changes

- HEAD at review: `b0a096e` (`7.0.14`). Findings apply to that commit **plus the
  working tree as reviewed**, not to a pristine checkout of the commit.
- Pre-existing modified files: `.idea/BoneAmanita.iml`, `CREDITS.MD`, `presets.py`.
- Pre-existing staged deletions: `tools/cache/audit_somatic.jsonl` and
  `tools/cache/somatic_census.jsonl`.
- Those edits and staged deletions were left intact. Do not restore old audit
  caches, discard the preset edits, or rewrite the user's credits as part of
  resuming this review.
- Interpreter obtained from PyCharm: Python 3.14.7 at
  `/home/gordonk/PycharmProjects/BoneAmanita/.venv/bin/python`.

### Assessment

The project has a useful experimental foundation: subsystem receipts,
positive-and-negative state-to-prompt assertions, controlled somatic audits,
and authored lore separated from much of the machinery. The main weaknesses
are failure handling and distributed state ownership across large orchestrator
modules, dictionaries, dataclasses, aliases, and dynamic attributes. Preserve
the vocabulary; make boundaries and ownership more explicit incrementally.
Reproducible installation and CI also need attention: the reviewed tree has
no tracked dependency lockfile or GitHub Actions workflow. These are engineering
recommendations, not newly measured behavioral defects.

### Reproduced runtime findings (all repaired in follow-ups above)

**R1. Embedding fallback contaminates the cache and misreports its provenance.**
**Fixed in the embedding follow-up above.** The following is the original reproduction.
In `spores/embeddings.py`, `SemanticEmbedder.embed_batch()` catches a backend
failure and generates hash vectors. Before the third consecutive failure,
`_degrade()` leaves the backend/model identity and `degraded` flag unchanged.
The fallback vectors are cached under that real backend's key, and the receipt
says `vectorized via http`, `degraded=False`. Repeating that text after recovery
hits the cache instead of obtaining a real embedding.

Reproduction used an isolated embedder initialized with `BACKEND='hash'`, then
assigned `backend='http'`, `model='review-model'`, `dimension=8`, and
`degraded=False`. Mock `_raw_embed` to raise `TimeoutError` for one nonempty
text, inspect the receipt, then mock a successful vector and request the same
text. Observed: receipt not degraded, recovered backend not called, original
hash vector returned. This is an offline fault-injection probe, not an observed
outage against a live server.

**R1b. The transition to hash can break batch dimensionality.**
**Fixed in the embedding follow-up above.** The following is the original reproduction. Repeat the probe
with a 16-dimensional pretend HTTP backend. Fail distinct texts `one` and `two`,
then request `['one', 'three']` while the backend fails again. `one` is fetched
from the old cache before the third failure switches the embedder to the
8-dimensional hash backend. Observed result lengths: **[16, 8]**. This violates
the method's documented rectangular-batch contract and risks breaking downstream
matrix/index operations. Both cache provenance and backend/index transitions
need explicit contracts; a successful receipt alone cannot establish correctness.

**R2. Failed quicksave writes destroy the previous valid checkpoint.**
**Fixed in the atomic quicksave follow-up above.** The following is the original reproduction.
`protocols/chronos.py:ChronosKeeper.save_checkpoint()` opens
`saves/quicksave.json` with `"w"` before serializing. In a temporary directory
with copied lore, construct an engine using `provider='mock'` and hash
embeddings, save once, then patch `protocols.chronos.json.dump` to write a
partial JSON prefix and raise `OSError`. Observed: the first save parses, the
file after the failed save does not. The exception path reports failure but
does not preserve the old checkpoint. `spores/io.py:LocalFileSporeLoader.save_spore`
already provides a temporary-file / fsync / replace pattern worth considering
when repair work is authorized. This probe did not touch the user's saves.

**R3. Engine shutdown does not stop the cycle daemon. Fixed in the follow-up above.**
The following describes the pre-repair reproduction.
`cycle.py:GeodesicOrchestrator.shutdown()` closes the background pool but never
clears `is_running` or joins `daemon_thread`. On the isolated mock-provider
engine, call `engine.shutdown()` and join the daemon with a 0.3-second timeout.
Observed: `is_running=True`, `daemon_thread.is_alive()=True`. The probe explicitly
cleared the flag and joined afterward for its own cleanup. Production remains
unchanged. Separately, `tests/base.py:BoneTestCase.tearDown()` shuts down telemetry
but not the engine; background daemons can outlive fixtures and later wake into
shared singleton state. Repair should establish shutdown ordering before
persistence/telemetry teardown, and fixtures should clean up what they start.

### Test evidence and its limits

Tests ran on a temporary copy of tracked working files, using the configured
interpreter above. The copy initially omitted Git metadata. Four observability
checks therefore failed solely because they call `git ls-files`. Git metadata
was subsequently copied, and **all 13 observability tests passed** on rerun.
Those four failures are review-setup artifacts, not repository defects.

The initial command was:

```bash
.venv/bin/python -m pytest -q --disable-warnings --maxfail=10
```

It stopped at its failure cap: **404 passed, 10 failed, 1 skipped**, with
18 subtests passed, in 247.79 seconds. Four of the ten failures were the
Git-metadata artifacts above. This was not a completed full-suite run.

After correcting the temporary checkout, the follow-up selection reran the
affected test files and covered the remaining files from the stopped run:

```bash
.venv/bin/python -m pytest -q --disable-warnings --tb=short \
  tests/test_cortex.py tests/test_gate_tolerance.py tests/test_moog.py \
  tests/test_observability.py tests/test_random.py tests/test_receipts.py \
  tests/test_resonance.py tests/test_scars.py tests/test_soul.py \
  tests/test_spatial_parser.py tests/test_spores.py tests/test_stage_manager.py \
  tests/test_struts.py tests/test_synapse_fallback.py tests/test_zones.py
```

Result: **129 passed, 7 failed, 4 skipped**, with 4 subtests passed and one
warning, in 38.29 seconds. The selections overlap: **do not add these counts
or publish them as one full-suite result**. The previously advertised
501 passed / 5 skipped is historical, not the reviewed baseline.

The seven failures were (all repaired in the refusal-test follow-up above):

| Test node | Observed failure |
|---|---|
| `tests/test_cortex.py::CortexArchitectTests::test_evaluate_toxicity_counterfactual_rejection` | Expected `COUNTERFACTUAL_REJECTION`, received `SYSTEM_HALT`. |
| `tests/test_cortex.py::CortexArchitectTests::test_evaluate_toxicity_system_halt` | `MagicMock` compared with a float in `nominate_toxicity()` ROS arithmetic. |
| `tests/test_gate_tolerance.py::ToleranceReachesTheGates::test_a_genuine_extreme_is_still_refused` | `MagicMock` is not imported (`NameError`). |
| `tests/test_gate_tolerance.py::ToleranceReachesTheGates::test_conversation_allows_what_adventure_refuses` | `MagicMock` is not imported (`NameError`). |
| `tests/test_moog.py::TestMoogProtocol::test_moog_intercepts_unactionable_toxicity` | `MagicMock` compared with a float in `nominate_toxicity()` ROS arithmetic. |
| `tests/test_random.py::RandomTest::test_productive_worry_godel_scar_math` | `refusal_triggered` remained false after `SimulationPreflightPhase.run()`. |
| `tests/test_scars.py::CounterfactualToxicityLeavesAScar::test_the_cortex_rejection_records_a_scar_and_keeps_the_mind_online` | `MagicMock` is not imported (`NameError`). |

These include broken fixtures and behavior/expectation disagreements; they are
not evidence of seven distinct production defects. In particular, inspect the
new nomination/arbitration boundary before deciding whether an old assertion
or the implementation should change. Do not weaken assertions merely to go green.

Temporary artifacts, if still present, are `/tmp/boneamanita-review.30v21P`
and `/tmp/boneamanita-review-followup.log`. They are disposable, not durable
project evidence; the commands and observations above are the handoff record.

### Current implementation versus historical measurements

- The governor uses `SignBitmap.score_all`, `z_top10`, and a corpus-size null
  correction (`z_excess`), not a graph Laplacian/Picard solve. It proposes a
  temperature carried through `<thermal_gate>`; `LLMInterface.generate()` strips
  the tag and clamps the value to the supplied `temperature_band`. Therefore a
  gate proposing zero does **not** guarantee deterministic sampling.
- The older September 17 entry below describes an intermediate `mu_viability`
  formula. Current `physics/observer.py` uses
  `min(1.0, frustration_ratio * 10.0)`, and retains the four-sample `r_base`
  calculation. Treat the older "uncommitted" descriptions as history.
- `SomaticBudget`, budget-driven prompt text and generation limits, and
  nomination-based Stage Manager routing already exist. D1/D2/D9 are not all
  future work. Their presence does not establish completion of the roadmap's
  acceptance criteria; refusal tests fail and current live behavior is unverified.
- The six-turn starvation result predates D0 repairs. The roadmap records a
  later live census with ATP between 16 and 53 across 30 turns. D0b's own section
  explicitly says the post-tolerance census was interrupted before its first
  turn. Stable ATP is not proof that the engine answers through the full script.
- C5's roughly 10% shorter sentences and failure to obey a three-sentence cap
  describe the earlier wording on two models. They are historical measurements,
  not fresh results for the current somatic contract. The audit arms and their
  measurement strings must be checked against current prompts before a new run.
- Nine names are now in `CORE_SUBSYSTEMS`; not all paths issue all receipts.
  Receipts are self-reports, and R1 demonstrates that inaccurate healthy reports
  can arise accidentally. Remove claims that this requires a deliberate lie.

### Proposed next round, when repair work is authorized

1. Reproduce the seven failing tests in a disposable checkout with Git metadata
   and the intended working changes. Establish the expected refusal contracts
   before changing fixtures or production behavior.
2. Address R1/R1b, R2, and R3 with focused failure-path regression tests: honest
   fallback/cache identity and consistent dimensions; preservation of the last
   good save; complete daemon/worker shutdown and fixture cleanup.
3. Run one complete suite and record its exact commit/working-tree state and
   result. Keep fixture defects separate from runtime defects in the report.
4. Audit current D1/D2/D9 wiring against their acceptance criteria, then rerun
   live somatic and 30-turn census experiments. Measure actual generated replies,
   refusal reasons, and accommodation, not just ATP survival or prompt inclusion.
5. Follow with incremental state-contract cleanup and reproducible dependencies/CI.
   Avoid expanding the feature set before the failure boundaries are dependable.

## Historical session: mid-thread state, 2026-09-17 evening

The entry below is preserved as written. Its "do this first", uncommitted-file,
and completion statements are superseded by the September 18 review above.

Two streams ran in this repo at once tonight (this Claude session working a
reply to Nelson Spence, and a second session doing Track D / C5 work) and
briefly crossed. **Nothing was lost**: both streams' work landed in commits
`d670053`/`7d87e07`/`0eb0d70` (all tagged `7.0.11.4`). This section is the
accurate state to resume from or to answer Nelson from; do not trust anything
earlier in this file about the governor's math without checking here first.

### Committed and safe

- **The governor no longer solves a graph Laplacian.** `CyberneticGovernor`
  used to build a memory subgraph, form `L = D - W`, and solve a nonlinear
  elliptic BVP by Picard iteration (`core.py`, old `_graph_regulation` /
  `_solve_nd_picard`). Nelson Spence emailed unprompted with a falsifiable
  prediction that this was mostly theatre; instrumented on our own code
  (23-node subgraph, real 768d embeddings, deliberately denser than a real
  session) the Laplacian term contributed **1.53%** of the reported
  eigenvalue, and the eigenvalue was **byte-identical from voltage 15 to 90**
  (the voltage input did nothing once `a` saturated at 1.0). Confirmed his
  number to two decimal places before touching any code.
- **Replaced with his recommendation**: `CyberneticGovernor._bitmap_regulation`
  now reads `SignBitmap.score_all(q)` in one pass, computes `z_top10` (how far
  the top-10 sign-agreement mean stands above the corpus mean, in standard
  deviations), and gates temperature/policy on that.
- **One correction of my own past that**: the raw `z_top10` null grows with
  corpus size for pure order-statistics reasons (mean ~1.1 sigma at n=32,
  ~3.5 at n=20000 on a synthetic Gaussian null I fit:
  `z_null(n) = 1.8712*sqrt(ln n) - 2.2958`). A fixed threshold on raw z would
  have silently opened as memory grew. Gate now runs on
  `z_excess = z_top10 - z_null(n)`, config `GATE.Z_PIVOT` is `0.5` (an
  excess, not a raw z) not `2.0`.
- **navi-fractal's decline rule, applied to the governor**: too few memories
  (`GATE.MIN_CORPUS`, default 32) or zero variance in scores raises
  `InsufficientCorpus`; the governor falls back to PID and files a receipt
  saying the regime was *not measured*, rather than emitting a number.
- **Renamed the prompt tag** `<cd_lambda_1>` -> `<thermal_gate>`. The tag now
  carries the actual sampling temperature (no more sign/magnitude
  interpretation in `brain/composer.py`). All call sites, the composer, the
  cortex attach method, `cycle.py`'s snapshot, and `main.py`'s status overlay
  are updated. `core.py`'s dead Picard config constants
  (`PICARD_C`/`BETA_SCALE`/`BETA_STAR_UNIT`/`PRUNE_SIZE`/`PICARD_MAX_ITER`/
  `PICARD_TOL`) and the three dead `PhysicsPacket` methods
  (`get_creative_drive`, `get_viability_potential`, `get_principal_eigenvalue`,
  plus the module-level `principal_eigenvalue` helper) are removed.
- **`CREDITS.MD` rewritten** to credit Nelson accurately: the bitmap gate is
  his recommendation (and his own finding, independently, at 207,695 nodes,
  Pearson 0.992 against a corpus-mass scalar); the metabolic economy
  (`calculate_viability`/`update_coherence_debt`/`execute_metabolic_tick`) is
  still genuinely his Creative Determinant equations, running; the removed
  Laplacian/Picard claim is explained and retracted with the 1.53% number in
  it, not just deleted quietly.
- **Fixed one real bug found while testing this**: `CyberneticGovernor()`
  built with no `config_ref` set `self.cfg = None` (no `BoneConfig` fallback,
  unlike every other class in this codebase), so `_gate_cfg` silently read
  every default instead of the real tuning values. Never hit in production
  (always constructed with a real config in `main.py`) but broke three tests
  that construct it bare. Fixed: `self.cfg = config_ref or BoneConfig`.
- `tests/test_creative_determinant.py` rewritten for the bitmap gate: 22
  tests, all passing as of the last clean run of that file alone.

### Uncommitted, in progress, NOT verified, do this first

Working tree has further changes on top of `0eb0d70`, applying two more of
Nelson's specific suggestions from his email. **These have not been tested.**

- `physics/observer.py`: feeds `mu_viability = (1.0 - gamma_idx) / 2.0` into
  `calculate_viability` instead of raw `beta`, per Nelson's "define
  contradiction relative to support... kappa*gamma and lambda*mu live on the
  same scale by construction and lambda=1 is natural." Also computes `r_base`
  from a 4-sample finite-difference window on `geo.abstraction` (1st/2nd/3rd
  differences summed) as a stand-in for the derivatives of psi Nelson
  mentioned, per his "Add R_base from those derivatives and lambda_0=0.5
  stops being a knob."
- `physics/maths.py`: `calculate_viability` gained an `r_base` parameter,
  dividing `lambda_eff` by it.
- `presets.py`: `CD.LAMBDA` 0.5 -> **1.0** (now "natural" under the redefined
  mu, per Nelson), `CD.BETA` 1.0 -> **0.4** (this constant may now be
  vestigial; grep shows it is only referenced in the `REQUIRED_CONFIG`
  manifest list, not consumed anywhere since the eigenvalue path that used to
  take `beta=` was deleted; check before trusting it does anything).

**Before doing anything else**: run the full suite. It has NOT been run clean
since these changes landed. Two known landmines:

1. There WAS a hang in `tests/test_architecture.py` that got fixed once (a
   `getattr` chain in `brain/cortex.py`'s thermal-gate attach walked into a
   `MagicMock`'s infinite attribute stand-ins; fixed with an `isinstance(z,
   (int, float))` guard instead of a `None` check) but this session was
   mid-way through confirming that fix still holds against the LATEST
   uncommitted `observer.py`/`maths.py` changes when it ran out of budget and
   was interrupted. Re-run `tests/test_architecture.py` alone first; if it
   hangs again the cause is almost certainly the same shape of bug (a
   `MagicMock` walked as if it were a real numeric value) somewhere in the
   new `mu_viability`/`r_base` path.
2. `physics/observer.py`'s `r_base` computation only activates once
   `self.psi_history` has 4 entries (`deque(maxlen=4)`, lazily created via
   `hasattr`), so the first three calls in any fresh session use `r_base=1.0`
   (no-op). That is probably fine but is untested and worth a receipt or a
   test asserting the ramp-up behaviour is intentional, not an oversight.

### Not part of Nelson's thread, already done by the other session, solid

Track D ("The Somatic Contract") and C5 (the somatic-translation measurement)
are unrelated to the ordvec/governor conversation and were completed
independently while this thread worked the Laplacian removal. Briefly, so
nothing there gets second-guessed by mistake: C5 measured that the ANAEROBIC
directive really does shorten sentences ~10% (an earlier 4-generation smoke
test in this same conversation pointing the other way was noise, as flagged
at the time); the "3 sentences or less" exhaustion directive is NOT reliably
obeyed and is model-dependent; a real bug (deception-tax phrase matching was
firing on ordinary style-crime phrases and draining ATP against the wrong
pool attribute) was found and fixed as `ROADMAP.md` Track D item D0.
`ROADMAP.md`'s Status table and Track D section are the source of truth for
that thread; nothing there references the governor internals this thread
rewrote, so the two are independent and both trustworthy.

### Before emailing Nelson

Do NOT send the reply yet. Needed first: (1) the suite passing clean with the
uncommitted mu/r_base changes included or reverted; reverting them out of
this diff and doing them as a separate follow-up is the lower-risk option if
the suite is still red, (2) a decision on whether `CD.BETA` is dead config to
remove or actually still needed somewhere, (3) `ROADMAP.md` Track B (B0-B3)
still describes the OLD Laplacian/Picard design as current and has not been
updated to point at the bitmap gate; only `CREDITS.MD` and the code
comments were updated, and Track B needs a short correction note (same
pattern as B4's) so the roadmap doesn't contradict the code. The draft reply
itself (numbers, the wheel request platform details: Linux/CachyOS, x86_64,
Python 3.14.7, glibc 2.44) was never written this session; only the code
changes needed to make the reply honest were done.

---


Paste this into a fresh context window to resume. Written at the point
where `ROADMAP.md` is complete: every subsystem the document listed as
disconnected is connected, and C5, the one measurement against a live model,
has been run and written up. What it found is a design question, not a
repair.

Structure and working conventions here are inherited from the T.R.S. →
SCI0 handoff (`/home/gordonk/RiderProjects/TRS_SCI/SESSION_HANDOFF.md`);
the project-specific content is obviously all BoneAmanita's. Where that
file and this one describe the same working habit, they should stay in
sync, those habits are not project-specific.


## C5: the original brief (done; result in `ROADMAP.md`)

Kept because it records why the experiment is shaped the way it is. The
design below is what `tools/audit_somatic.py` implements, with three changes
found in practice: exhaustion straddles its gate (0.79 / 0.81) rather than
being set far above it, so the METRICS line barely moves; empty visible
replies are their own outcome; and gemma had to run with
`reasoning_effort=none` (see Open items 8). The "Where it should live" advice
on a gated live test was not taken: a pass/fail test on a 10% effect needs
hundreds of generations and would be flaky, and the audit itself is the
re-runnable artifact. The offline measurement rules are pinned in
`tests/test_audit_somatic.py`.

**Everything else on `ROADMAP.md` was done at the time.** Tracks A and B are finished,
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
instruction needs strengthening or `README.md` and `CREDITS.MD` need their
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
exact implementation. The no-frameworks decision says do not add one for
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
and `CREDITS.MD`. If the effect is real, say how large. If it is not, say
that plainly and soften the claim. The precedent for this is B4 and the Lean
4 correction: the overstatement was ours and the fix was to write down that
it was ours.

