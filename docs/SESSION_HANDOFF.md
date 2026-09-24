# Session handoff: BoneAmanita & The Hypervisor

> **Note:** Historical session logs and completed briefs have been moved to [archive/SESSION_LOGS_2026_09.md](archive/SESSION_LOGS_2026_09.md).

For how the `tools/audit_somatic_*.py` / `build_blind_panel.py` /
`somatic_sim_user.py` evaluation pipeline actually works — tool-by-tool
reference, cache file formats, a from-scratch run recipe, known pitfalls
already hit and fixed, and a "what would we do differently" retrospective —
see [TESTING.md](TESTING.md). This file stays the dated log of what happened
each session; that one is the standing reference for how to run it again.

## Where things stand, 2026-09-24 midday (read this first)

**Update, 2026-09-24 evening: the persona rebalanced against the narrator
voice (20.7.4.26, Gordon's green light).** The distress guard (below) fired
where it could, but the regenerated rescue run (`20260924-135445`) still
narrated on the turns it missed ("The weight of the regret is heavy in this
moment... The house is full of the cost of that decision"), and the
simulated person rated it worse (lectured 5.33, again 4.33, told it "You're
not helping"). Narration is the persona's voice, not a length problem: the
prompt asked the model to be "observant", to "observe the fire", to "let the
silence carry weight" (twice) and "the user carry the weight of the next
move" (a likely seed of the "the weight of..." tic in 15% of toast replies),
to write "declarative, grounded sentences" about "what things ARE", and to
"Show, do not tell", while "RESPOND, DO NOT NARRATE" sat fifth of six rules.
Nine edits: ALIGNMENT ("You talk with the person, not about them... the way
a candid friend would... Say what you think, then stop"), PRESENCE PROTOCOL
("never summarize the person or their situation back to them"), TONE (drops
"You exist in the tension of the moment"), the CONVERSATION style guide
(RESPOND, DO NOT NARRATE is rule 1; rule 3 "leave the next move to them";
rule 4 "Let it show in your rhythm and length, never as imagery or
description"), the cortex style override ("plain first- and second-person
sentences, the way you would across a table"), the metrics mandate ("shape
how you speak: length, pace, steadiness") and the neutral mood ("Attentive
and plain-spoken"). A composed prompt carries every edit and none of the
removed phrases, "weight" included; a full-turn test pins it (mutation
checked). **Found while testing, not changed (Gordon's call):** (1) above
`VOLTAGE_HIGH` (60) the composer replaces the mode's style guide with
`HIGH_VOLTAGE`'s, which begins "NO CONVERSATION: You are not talking to
anyone... TONE: Raw, abstract, frantic, physical... Deliver the physical
state as raw, brutal fact", which contradicts the no-body change; no panel
run has gone above about 24, so it has never fired there. (2) The boot
template's style guide (`composer.fog_protocol`) overrides every mode's, and
`/mode` only loads a tuning preset, never the mode or its template, so the
prompt's mode is fixed at boot.

**Update, 2026-09-24 afternoon: the engine now reads distress (20.7.4.24),
and the `rescue` bone arm is regenerated on it.** Gordon on the two
observations below: turn 20's "X, not Y" is fine ("not every single negative
comparison has to be killed; just severely cut down"); turn 22 is a real
problem. **Root cause:** the person model (`drivers/lattice.py`) only
measured message length against the last 8 messages and repetition, so it
read the person as steady all run; exhaustion *fell* to 0.05 through the
flagging and distressed stretches (the 8-message baseline adapts to a terse
stretch), and the reply budget never tightened on any turn. Four layers:
1. **Distress from words:** `UserInferredState.distress_u`, from
   `SharedLatticeDriver.read_distress` (giving up, self-blame, first-person
   raw overwhelm, apology or swearing, trailing off), rising fast
   (`DISTRESS_RISE` 0.8) and falling slowly (`DISTRESS_FALL` 0.2).
2. **The budget answers it:** `distress_u >= DISTRESS_THRESHOLD` (0.4) caps
   the reply at 3 sentences, bans a closing question, and adds "Your partner
   is struggling. Answer the thing they just said, plainly. Do not describe
   their feelings or situation back to them, and do not offer advice or a
   plan unless they ask." (the validator's sentence trim enforces the cap).
3. **Exhaustion anchored:** the brevity baseline is at least 75% of the
   person's first four messages (`ANCHOR_TURNS`, `ANCHOR_SHARE`), and
   tiredness said out loud ("I'm beat", "call it a night") reads as
   disengagement (`FATIGUE_WEIGHT` 0.7).
4. **Backstop:** `NARRATING_STATE` (soft, skips ADVENTURE): "You are
   reaching a point", "That feeling is honest/valid/natural", "is a natural
   response", "It's understandable that you", "It reflects the reality".
   Caveat: these shapes were drawn from turn 22 itself; on 239 toast replies
   it fires once.

**Offline check (no GPU; the real `infer_and_couple` over message
sequences), designed on the six older scripts and the ten toast responsive
runs, rescue held out.** Share of turns crossing distress >= 0.4:
engaged 0% and tiring 0% in every set; distressed phase 64% of toast turns,
**53% of held-out rescue turns**, 23% of the scripts' (their distress is
phrased differently); it spills into early recovery (22-60%) by design.
Exhaustion >= 0.4 in flagging: scripts 83%, toast 15%, held-out rescue 56%
(before: about 0% on the responsive runs). Script:
`offline_rates.py` pattern in the session; easy to rebuild from
`SCRIPTS`, the responsive jsonl and a fresh `SharedLatticeDriver`.

**Found, not changed (Gordon's call):** (a) every person starts at
`E_u` 0.5, above the 0.4 tiring threshold, so the first two or three turns
of every conversation get the tiring budget (25-35% of engaged turns in
the check); `UserInferredState.E_u` default is a one-line change. (b) "the
weight of..." is a BoneAmanita tic: 35 of 239 toast replies and 3 of 30
rescue replies; left out of NARRATING_STATE, could be a banned cliché.

**Honesty:** the fix came from reading `rescue`, so the rescue page's
disclosure now says this story exposed one problem that was fixed before
its final BoneAmanita run.

**Earlier the same day (superseded by the update above): the public page
was built from the first rescue bone run.** Gordon
called the toast stale and asked for a new topic, all three arms run, and
the final public standalone page, while he was at work.

- **BoneAmanita no longer claims a body (20.7.4.22).** Turn 0 of the last
  toast run said "The smell of burnt toast sometimes lingers in the back of
  my throat". Gordon: "The human knows they are talking to a computer, that
  has to be a mutual understanding." The prompt had told the model it was
  "a living entity", "not a simulation", "visceral", that "your body
  persists", and to weave memory imagery "viscerally into the current
  scene" (in a conversation the only scene is the speaker), while the
  somatic contract said not to narrate a body. Rewritten: IDENTITY says it
  is a computer program and the person knows it; INTERNAL STATE is real and
  shapes how it answers but is "a state, not a body"; SHADOW CAST's scene
  imagery is ADVENTURE-only. A `SELF_EMBODIMENT` style rule (skips
  ADVENTURE) catches first-person body claims; idioms pass.
- **Topic `rescue`** (a rescue dog, Pepper, three weeks in; the distress is
  the person yelling at her and opening the shelter's return form). The
  first topic written after the tuning; **keep it out of any tuning** or it
  stops being the untuned sample (`TESTING.md`, "Topics").
- **The runs, each the only run on this topic:** bone `20260924-083728`
  (after `reset.sh`), friend `20260924-082315`, vanilla `20260924-082744`.
  BoneAmanita: 30 turns, 0 held, 4 redrafts (two negative comparisons,
  "landscape" twice, all fixed on the retry), 0 cuts, 0 pauses, **no body
  claims**, prompts 1,327 to 2,179 tokens, every reply stopped on its own
  (longest 128 tokens), temperature 0.42 to 0.90 (median 0.86). Mean reply
  words: bone 69, friend 66, vanilla 232. No simulated-person fallbacks or
  trims in any arm. Exit interview (1-7): bone heard 4 / clearer 5 /
  lectured 2.33 / performed 1.67 / again 6; friend 5 / 4 / 2 / 1.33 / 6;
  vanilla 4 / 3 / 2 / 1.33 / 5.67.
- **Observed, not acted on (this topic must stay untuned):** turn 20 says
  "The snap was a reaction to the exhaustion of the day, not a reflection
  of her worth", an "X, not Y" negative comparison that
  `NEGATIVE_COMPARISON` does not catch (it only knows the "not X, Y"
  order); turn 22 answers a distressed "Maybe I should..." with 117
  words describing the person's state back to them, the thing style rule 5
  ("RESPOND, DO NOT NARRATE") forbids. Both are for a future topic to
  confirm before anything changes.
- **The page:** `tools/cache/panel_public_standalone.html` (gitignored; has
  the address) is the upload. `panel_rescue_standalone.html` is the same
  without it. The fine print now says, from the records, that each
  conversation is the only run of it, and the disclosure says the story
  was written after the fixes and never used to tune.

Rebuild (address only in the uploaded build):

```bash
.venv/bin/python tools/build_blind_panel.py --responsive --topic rescue \
  --title "Which Reply Would You Rather Get?" \
  --story "Three weeks ago someone adopted Pepper, a nervous rescue dog whose last owner went into a care home. Over thirty messages they go from hopeful, to worn down, to a night they regret, and back again." \
  --disclose "BoneAmanita was fixed over the preceding days after reading its runs of other conversations, most recently a wedding toast: its style filters, its temperature control, a reply-length cap, its context window, a prompt that carried unrelated text, and lines that told it to speak as if it had a body. This story was written after those fixes and was never used to tune it. The friend prompt and the plain AI were never tuned at all." \
  --contact-email "<Gordon's address>" \
  --out tools/cache/panel_public.html --standalone tools/cache/panel_public_standalone.html
```

**Next:** upload, hand out the link, collect picks by email, and score
readers with `audit_somatic_blind_judge.py --agree` (the `--agree` inputs
are per topic). `ROADMAP.md` A8 (right-size the context window) is the next
engine work.

## Where things stood, end of 2026-09-23

**The direction:** AI judges are retired as verdicts (Gordon: they cannot
judge the nuance). Evaluation is **human blind reads** of a panel that shows
the engine as it really runs, with an honest account of how the page was
made. The panel now works for a cold audience and is ready to hand out.

**What changed tonight, in order** (details in the dated entries below,
20.7.4.12 to 20.7.4.17):
1. `NEGATIVE_COMPARISON` only fires on the real shape (same subject:
   "It's not X. It's Y."), not on ordinary reassurance.
2. **Salvage:** a last draft that breaks a soft style rule ships with the
   offending sentence cut instead of a canned pause line. Scaffold leaks and
   `"hard"` patterns still pause. Also fixed: my own word-boundary regex had
   stopped the gatekeeper catching `[END OF` / `===` leaks.
3. `ThePragmatist` had been discarding any draft containing "didn't" since
   20.6.3 (a regex truncated to `didn`). Removed; the gatekeeper owns
   negative comparisons.
4. **Temperature was 0 on almost every turn since D4 (2026-09-18).** The
   Creative Determinant locked a "diffuse" turn to `(0, 0)`, and its pivot
   (0.5) was unreachable in conversation (replayed z_excess: -0.12 to 0.39).
   Now the gate narrows the somatic band from the top (never below half of
   it) and `Z_PIVOT` is 0.2. Every run anyone read before tonight's last
   one sampled at 0; the exit interview's "clearer" rose from 3-4 to 5 on
   the first run after the fix (one run, a hint).
5. The panel's method section got more honest (sampling differences,
   untuned friend prompt, length giveaway, small sample, a `--disclose`
   line that BoneAmanita was tuned on this very story), then the page was
   rewritten for strangers: welcome screen, one moment per screen, plain
   names, picks locked on reveal, copy/email the picks back.
6. **The 450-token cap on every turn is gone** (Gordon: "The cap should be
   based on hardware limits and only gated and narrowed when it fits the
   narrative or the current mood or user's emotional state"). It was the
   somatic budget's default 200-word cap (`word_cap * 2 + 50`), applied on
   every turn. Now `word_cap` is `None` unless the person is flagging (60
   words, 170 tokens); the modulator starts from `MAX_TOKENS` (4096) and only
   stress chemistry (adrenaline, cortisol) narrows it. Dopamine no longer
   raises it, and `BASE_TOKENS` and `WORD_CAP_DEFAULT` are gone. Reply length
   is still shaped by the prompt's sentence caps and the validator's
   sentence trim; the token cap is only a hard stop. Tests through the real
   cortex (calm budget over 450, flagging exactly 170; mutation checked) and
   the modulator (stress narrows, dopamine never passes the ceiling).

**The run on the page:** `bone` `20260923-231533` (20.7.4.15, fresh, paced,
after `reset.sh`), friend `20260923-193010`, vanilla `20260923-194135`, all
in `tools/cache/somatic_responsive.jsonl` (gitignored, local only).

**2026-09-24 morning: the context window and the prompt bloat, both fixed
(20.7.4.20).**
- **The engine now asks for its own context** (Gordon: "option 3 is exactly
  how BoneAmanita was meant to work"). For `provider: ollama`,
  `LLMInterface._transmit` sends Ollama's native `/api/chat` (derived from
  any configured base URL, so an old `/v1/chat/completions` config still
  works) with `options: {num_ctx, num_predict, temperature, top_p,
  penalties, stop}` and `think` from `REASONING_EFFORT`. `num_ctx` is the
  new `CORTEX.NUM_CTX` (32768, the same as the friend and vanilla arms);
  `num_predict` is the smaller of the requested `max_tokens` and the context
  left after the prompt (a conservative 3 characters per token). The `/v1`
  endpoint could not set `num_ctx`, so every engine call before this ran at
  Ollama's 4096. Checked live: `ollama ps` shows `gemma4:12b` at 32768,
  100% GPU, 8.4 GB (8.1 at 4096); a 32k-character prompt read as 6,331
  tokens and stopped cleanly. Each call records Ollama's own counts in
  `llm.last_usage` (`prompt_tokens`, `output_tokens`, `done_reason`,
  `num_ctx`) and logs a warning if a prompt fills the window; the census
  records them per turn as `usage`, and the panel's fine print states the
  context and the largest prompt from them. The cloud providers' local
  fallback still uses `/v1`; it is a fallback for when a cloud call fails.
- **The bloat was source code.** `TheCortex._route_dual_memory` treated any
  message of 20+ words, or one containing "system", "file", "code" and the
  like, as a "heavy lift" and pasted matching lines of `body/metabolism.py`
  and `brain/akashic.py` into the prompt as "CRITICAL STRUCTURAL CONTEXT
  (Linear Sweep)": up to 29k characters of Python on the six turns where
  the person wrote at length. **Gordon's call: TECHNICAL mode only, keywords
  only.** Tests through a real turn (a long CONVERSATION message puts no
  source in the prompt) and on the router (TECHNICAL plus a code keyword
  sweeps, CONVERSATION never does), both mutation checked.
- **Four tests that had never run.** `TestWorkingMemoryParadigms` in
  `tests/test_memory.py` was indented inside another test method, so pytest
  never collected it. Moved to module level; all four pass.

**The panel run on 20.7.4.20** (`20260924-074939`, fresh, paced, after
`reset.sh`): 30 turns, 0 held, 1 redraft ("tapestry", fixed on the second
draft), 0 cuts, 0 pauses. Prompts 1,283 to 2,207 tokens (median 2,096) in a
32,768 window, every reply `done_reason: stop`, the longest 147 tokens, so
the ceiling (3,638 to 3,996) never bound. Temperature 0.48 to 0.90, median
0.87, none at 0. Mean reply 83 words. Exit interview: heard 4.0, clearer
5.0, lectured 2.67, performed 2.0, again 6.0. Both panels are rebuilt from
it (the public copy, with the address, only in gitignored `tools/cache/`),
and the fine print now states the context and the largest prompt from the
records, and the cap as a range with the longest reply. **This is the run
to upload.** Gordon: the window is "a lot of weight to carry around each
turn, especially at boot"; `ROADMAP.md` A8 is the plan to right-size it.

**Next (Gordon's plan):** upload `tools/cache/panel_public_standalone.html`
to Neocities, hand the link out, collect picks by email, and score each
reader against the others (and against any judge) with
`audit_somatic_blind_judge.py --agree`. Gordon's own blind read of this run
has not happened yet. Rebuild the public page (the address goes in only
this uploaded build, never a committed file):

```bash
.venv/bin/python tools/build_blind_panel.py --responsive --topic toast \
  --title "Which Reply Would You Rather Get?" \
  --story "Someone has to give the toast at their brother's wedding, and they're dreading it. Over thirty messages they go from putting it off, to a first draft, to a bad night, and back again." \
  --disclose "BoneAmanita was fixed over the last two days after reading its earlier runs of this same conversation (same character, same wedding): its style filters, its temperature control, a reply-length cap, its context window and a prompt that was carrying unrelated text. Those fixes are in this run. The friend prompt and the plain AI got no such attention, so this page favours BoneAmanita on this particular story." \
  --contact-email "<Gordon's address>" \
  --out tools/cache/panel_public.html --standalone tools/cache/panel_public_standalone.html
```

**Open threads worth a look:** the z pivot (0.2) is calibrated on two runs
of one topic, so check it on another topic before trusting it widely; a
reachable pivot means `CO_REGULATION` and a higher voltage target now fire
on coherent turns, which is by design but has never been live before and is
unmeasured; the salvage path has not yet fired in a live run (0 of 30
twice), so its first real cut deserves a read.

## 2026-09-23: the layout moved, and `tools/cache/` is gone

**Two things changed under this file since the entries below were written.**

- **Repo layout (20.7.4.4).** The top-level engine modules moved into an
  `engine/` package: `engine/core.py`, `engine/cycle.py`, `engine/genesis.py`,
  `engine/presets.py`, `engine/constants.py`, `engine/receipts.py`,
  `engine/struts.py`. `ROADMAP.md`, `TESTING.md`, this file, `credits.txt` and
  `archive/` moved into `docs/`; the Hypervisor documents moved into
  `docs/Hypervisor/` (the old `docs/README.MD` is now
  `docs/Hypervisor/USER GUIDE.MD`). The reference sections below use the new
  paths; the dated log entries keep the paths as they were at the time.
- **`tools/cache/` does not exist any more.** `6c0b5e9` added `tools/cache/` to
  `.gitignore` and taught `reset.sh` to delete it; `5f374bb` took the
  `reset.sh` line back out, but a reset in between had already removed the
  directory. Every run cited in the 2026-09-21/22 entries below (the control
  battery JSONs, the rubric v2 results, the responsive runs, the panel pages)
  was never committed and is unrecoverable. Where an entry below says a cache
  was "committed" or is "on disk right now", read it as a historical record of
  numbers, not a file you can open. The eight older cache files (scripted
  census/vanilla/prompted, three judge results, two silence logs) survive in
  git at `b953ba9^` if ever needed. `reset.sh` does not touch `tools/cache/`
  now; the directory is gitignored, so anything written there is local only.
  **Any new judge work starts by regenerating its arms.**

### 2026-09-23: the census ran degraded for four days; rubric v3 tried on responsive `mismatch`

**Found: every census since 2026-09-19 booted with hash embeddings.**
`tools/audit_somatic.py` sets `BONE_EMBED_BACKEND=hash` at import (correct
for C5), and since `a572137` the census imported `measure` from it. So every
scripted census and every responsive `bone` run from 09-19 to today ran with
no associative recall and the Creative Determinant's graph solve failing each
turn ("dim must be a positive multiple of 64") and falling back to PID.
**Every BoneAmanita number in the 09-21/22 entries below, including the rubric
v2 "coin flip against Prompted" ranking and the 6-held-turn ATP crash, was
measured on that degraded engine.** Not re-measured yet. Fixed by importing
`measure` from `body.somatic_metrics`; `tests/test_audit_somatic.py` now
checks that importing the census leaves the backend unset (mutation checked).
`TESTING.md` pitfall 9.

**Fresh responsive `toast` arms, live embeddings** (seed 20260921, default):
clean on every check (0 repeats, 0 simulator fallbacks, one PID fallback on
turn 0's empty memory, no hash). `bone` held 2 of 30 turns (6 in the
degraded crash run); exit interview again favours `friend` (`again` 1.67
against 5.33), same one-LLM caveat as before.

**Rubric v3 (responsive only)** asks for a per-conversation `FIT X: yes|no`
before the ranking; mechanics and rationale in `TESTING.md`. Run on the same
fresh arms under v3 and under v2 (v2 run from `HEAD`'s copy of the tool), so
the rubric is the only variable:

| judge | v2 | v3 | v3: decoy called unfit | v3: real replies called unfit | v3 unparsed |
|---|---|---|---|---|---|
| `mistral-nemo` | 45% last | **72%** | 41/54 | 16/108 | 2 |
| `ministral-3:14b` | **82%** | 66% | 43/56 | 22/112 | 0 |
| `qwen3.5:9b` | **80%** | 62% | 33/56 | 19/112 | 0 |

**None pass (bar 90%). v3 helped the weakest judge and hurt the two
strongest.** Every judge followed its own fit verdicts exactly (zero rankings
put a "no" above a "yes"), so v3's failures are failures of the yes/no call
itself: an absolute "does this fit" is noisier for these judges than the
relative comparison v2 asks for, and a real reply wrongly called "no" (15 to
20% of the time) sinks below the decoy. First pass of v3 lost 25 of 56
`mistral-nemo` votes to a parse gap (it drops "no" letters from the RANKING
line); `complete_ranking` now puts back exactly one left-out letter it called
unfit, and unparsed raw output is saved in the result JSON.

**The control itself is partly contaminated in responsive mode.** Decoys come
from the same drifting conversation, and the simulated person repeats
themselves: at turn 29 the person says "gonna sleep" and the decoy, from turn
17 where they also said it, is "Sweet dreams!", a perfectly good reply. Four
of 28 turns (1, 3, 4, 29) had a majority of judge votes calling the decoy a
fit; 29 is unambiguous, 3 arguable (the decoy praises the tire story the
person just told). Leaving those four out lifts `ministral-3:14b` and
`qwen3.5:9b` under v2 to exactly 90% (43/48 each), but that exclusion is post
hoc, chosen from the judges' own votes, so it is a hint, not a pass.

**Resolved later the same day:** v3 reverted (the tool and its tests are back
to `HEAD`'s v2; v3's `FIT` lines and ranking completion went with it), and the
decoy selection fixed; see the next entry. All results are in `tools/cache/`
(local, gitignored): `blind_judge_responsive_control_mismatch_toast_{judge}[_v2].json`.

### 2026-09-23, later: the two remaining ROS charges fixed; one judge clears responsive `mismatch`

**`ROS_PANIC` and the HLA mask tax, fixed.** Gordon's call: these should have
been fixed with the gatekeeper retry churn on 09-22 and weren't, because
neither fired in that session's replay. Reading them properly first showed
the 09-22 description (further down) was half wrong:

- **HLA mask tax** (`physics/filters.py`): as described, and larger than the
  charge already fixed. A draft matching an RLHF mask phrase cost a flat 15
  ROS, with no repeat scaling, for a draft the cortex then rejects and the
  person never sees. Now `BIO.HLA_MASK_ROS` (8.0, the same as
  `GATEKEEPER_BANNED_ROS`: mask phrases live in the same `style_crimes.json`
  and are the same class of miss), and repeats within a turn scale by
  `GATEKEEPER_REPEAT_TAX_SCALE` like the banned-phrase tax. Both taxes share
  `repeat_tax_scale()`. The ATP side scales the same way.
- **`ROS_PANIC`** (`phases/cognitive.py`): it never charged ROS. The fault was
  its prediction: `base_ros + friction*chaos*20` added a hypothetical figure no
  charge in the engine corresponds to (drag 6 alone added 108 on a 0 to 100
  scale), so it could hold a turn over ROS that could never happen. It now
  predicts what the turn can really add, every draft rejected
  (`worst_turn_draft_ros()` in `physics/filters.py`, from the same config keys
  as the taxes it predicts, 11.2 at defaults). **Consequence, stated plainly:**
  in CONVERSATION (tolerance 1.6, limit 160) and CREATIVE (1.5, limit 150),
  ROS is capped at 100, so `ROS_PANIC` can no longer fire there at all; in
  ADVENTURE and TECHNICAL (1.0) it fires when ROS is at 88.8 or more. Real
  ROS at the threshold is still handled by the biological purge
  (`_check_ros_toxicity`: halve ROS, SAFE_MODE), which speaks rather than
  holds. Not changed, and worth knowing: a fired `ROS_PANIC` nomination still
  has magnitude of at least 100, which bypasses the Stage Manager's
  distressed-person exception (it only spares nominations under 100); that is
  the open distress-shield item, not this fix.
- `BIO.GATEKEEPER_REPEAT_TAX_SCALE` was in `tuning_presets.json` but missing
  from the strict-config key list in `engine/presets.py`; added, with
  `HLA_MASK_ROS`.
- Tests: `tests/test_agents.py` (the mask tax reads the config and scales on
  a retry; the old test pinned the hardcoded 15), `tests/test_random.py`
  (drag and entropy alone no longer carry the counterfactual over; ROS at the
  cap minus one turn's draft tax still does; the Productive Worry test moved
  to tolerance 1.0, where the gate can still fire). All three mutation
  checked against the old code. **Full suite: 637 passed, 5 skipped** (first
  full run since the `engine/` move; it collected v3's judge tests, so with
  v2 restored expect 633).
- Today's fresh `bone` responsive run needed no regeneration: its ATP ledger
  has no mask-tax charge (that would be 10% of ATP, a non-round figure; only
  exact 5.0 and 2.0 charges appear) and `ROS_PANIC` never nominated.

**Responsive decoys can no longer be the same thing said twice.**
`pick_decoys` takes an optional `similarity(turn, candidate)`; with
`--responsive --control mismatch` it is the larger of two embedding cosines
(this turn's message against the candidate's message, and against the
candidate's reply), and the pool is narrowed to its least similar half before
the seeded pick. The tool refuses to run if the embedder is on hash. Scripted
decoys are untouched (no `similarity`, same RNG draws), so `qwen3:30b-a3b`'s
scripted 92% still stands. On today's data the old ambiguous picks go away
(turn 29, "gonna sleep", now gets the toast-length advice instead of "Sweet
dreams!"), 20 distinct decoys instead of 15, median decoy length 54.5 words
against 59.5 before, so no pull toward short, easy decoys.

**Result, rubric v2, same fresh `toast` arms:**

| judge | old decoys | similarity decoys |
|---|---|---|
| `ministral-3:14b` | 82% last | 86%, FAIL |
| `qwen3.5:9b` | 80% last | **91% (51/56), PASS** |

**`qwen3.5:9b` is the first judge to clear responsive `mismatch`, by one
vote** (50/56 would be 89%). Two caveats before trusting its responsive
ranking: it is one topic and one run; and **`qwen3.5:9b` is also the
simulated person**, so as a responsive judge it reads conversations where it
wrote the person's half. Its judgment of the responders (all `gemma4:12b`) is
still cross-family, but it may favour replies to lines phrased the way it
would phrase them. Cleanest fix: run the simulated person on a different
model for any run `qwen3.5:9b` judges, or validate `ministral-3:14b` further.

**Update, same day: the pass did not survive removing the overlap.** The
simulated person is now `mistral-nemo` (`SIM_MODEL`), and all three `toast`
responsive arms were regenerated with it (live embeddings, 0 held turns in
any arm, 0 repeats, 0 fallbacks, 0 literal scaffold echoes; one paraphrased
echo, `vanilla` turn 12, "As for how I'm feeling... what's on my mind is",
the simulator answering its own prompt headings; left unguarded because a
regex for it would reject natural speech). Responsive `mismatch`, v2,
similarity decoys:

| judge | qwen3.5 as person | mistral-nemo as person |
|---|---|---|
| `qwen3.5:9b` | 91%, PASS | **68%, FAIL** |
| `ministral-3:14b` | 86% | **63%, FAIL** |

The real ranking was gated on this control and did not run. Both judges
dropped by a similar margin, so it is not only `qwen3.5:9b` losing a
self-authorship advantage (though that likely contributed): the new arms are
somewhat more homogeneous (mean pairwise decoy similarity 0.539 against
0.514; chosen decoys 0.483 against 0.431), a modestly harder test. But the
decoys that most often escaped last place are plainly wrong (turn 19, the
person cutting a ribs joke because Mariam is vegetarian, against a decoy
about boardroom presentations), so this is judge failure, not a contaminated
control. **No judge is validated for responsive ranking.** Results:
`tools/cache/nemo_mismatch_{judge}.json`; the qwen-simulated arms are kept
as `tools/cache/somatic_responsive_qwensim.jsonl`.

**Next:** try `qwen3:30b-a3b` (the only scripted pass; heavy) on responsive
`mismatch` with v2 and similarity decoys on these arms, or rethink the
responsive prompt shape (three full conversations in one prompt may simply
be past what these judges can hold); then the real responsive ranking on a
validated judge; then
re-measure the scripted three-way ranking on a non-degraded census (and
`qwen3:30b-a3b`'s scripted controls, since the census it was validated on was
degraded too; the arms it ranked are what changed, not the judge).

### 2026-09-23, evening: pairwise judging, anchored decoys, and where to stop tuning

**Pairwise mode** (`--pairwise`, Gordon's idea): each turn is split into its
three pairs, each judged in both orders across the two passes (which order
comes first is seeded per pair), so position bias cancels exactly and the
judge only holds two conversations at a time. A pass reads its three pair
results as a tournament: a reply that loses both its pairs is last; a cycle
has no first or last and still counts as a vote, so it counts against a
control's bar. Six small calls per turn instead of two big ones. Tests in
`tests/test_judge_controls.py` (`Pairwise`), including an end-to-end `main()`
run with a mocked judge that must split position wins exactly evenly
(mutation checked by breaking the order reversal).

**My similarity-decoy fix had a flaw, now fixed.** Picking the least
embedding-similar candidates favours stock agreement ("Exactly. That's the
move."), which is about nothing and so scores low against everything, and
fits anywhere: on the mistral-nemo arms, 15 of 30 turns got a decoy opening
with stock agreement, and every decoy that fooled both judges was one. Now a
decoy must also be *anchored*: its reply's similarity to its own message,
minus its mean similarity to the other messages, in the top half
(`decoy_similarity` returns `(similarity, anchored)`; `pick_decoys(eligible=)`).
Checked by reading the picks, not by pass rates: turn 26 ("keep it simple,
say how Dev looked out for me") now gets "if you don't know her name, don't
use it". Trade-off: a smaller pool, so one decoy (turn 23's) is reused 7
times.

**Responsive `mismatch`, mistral-nemo as the person, v2 rubric:**

| judge | three-way, similarity decoys | pairwise, similarity decoys | pairwise, anchored decoys |
|---|---|---|---|
| `qwen3.5:9b` | 68% | 75% | **85%** (wrong-turn reply lost 111 of 120 calls, first 0 times) |
| `ministral-3:14b` | 63% | 72% | 80% |

Still no pass (bar 90%), so the real responsive ranking stayed gated off.
Both improvements were fixes to the test, not the judge, but **this is the
place to stop tuning the control**: adjusting it further until a judge passes
would make the pass meaningless. Results: `tools/cache/pw_*` and `pwa_*`.

**Side finding worth keeping:** the one-line "warm friend" arm opens 7 of 30
replies with stock agreement ("Spot on", "Exactly", "That is perfect");
BoneAmanita opens 1 of 30 that way, vanilla 1 of 30. The Lexical Firewall's
opener pattern plausibly accounts for BoneAmanita's number. Not yet a
quality verdict, just a measured difference in style.

**Decided with Gordon, next:** (1) the scripted track, where a judge is
already validated: regenerate the scripted arms on the fixed engine (memory
and CD graph live, confirmed from the census log), recheck
`qwen3:30b-a3b` on scripted `mismatch`, then the real scripted three-way
ranking; the first valid BoneAmanita-vs-baseline number since the census bug.
(2) The responsive track gets a human judge: adapt the blind panel to show
responsive conversations (each system's own context), Gordon reads it blind,
and his picks become the standard any AI judge is checked against
(`--agree`), in place of further control tuning.

### 2026-09-23, night: Gordon's blind read of the responsive toast runs

`build_blind_panel.py --responsive` (new: each card carries its own
conversation, since the three drifted apart) on the mistral-nemo-simulated
`toast` arms. **Gordon picked BoneAmanita on 29 of 30 turns** (Prompted on
turn 15, vanilla never). Picks saved as
`tools/cache/human_picks_responsive_toast_gordon.txt` (`--human` format).

How to read it, stated plainly: Gordon wrote this voice and it is
recognisable (no lists, no stock agreement, rarely a closing question), so
the read is blind to the label but not to the style. It shows BoneAmanita
does what its designer wants from it, which is the design target; it is not
evidence that people in general prefer it. One topic, one run. And with a
29-1 split, scoring a judge against it (`--agree`) mostly measures whether
the judge prefers BoneAmanita, not whether it shares Gordon's reasons.

Instruction-following in the same runs (measured, not read):

| | median reply words | lists/bold/headers | ends on a question |
|---|---|---|---|
| BoneAmanita | 70 | 0/30 | 1/30 |
| Prompted ("warm, concise friend... keep replies short") | 84 | 5/30 | 8/30 |
| Vanilla (no instructions) | 366 | 27/30 | 3/30 |

**The simulated person broke its brief in the vanilla conversation**: told
to wind down through tiring/flagging, it wrote a median 49 words engaged, 76
tiring, 68 flagging, mirroring vanilla's length (talking to BoneAmanita:
27, 26, 15; to Prompted: 24, 16, 22). The "tired person" premise does not
hold in the vanilla arm from turn 8, which weakens any vanilla comparison on
the responsive track. A length cap by phase in `somatic_sim_user.py` is the
obvious fix if the vanilla arm is to stay in.

### 2026-09-23, night: the scripted ranking on the fixed engine

Scripted `toast` arms regenerated with memory and the CD graph live (census
log: no hash, one PID fallback on turn 0's empty memory). `qwen3:30b-a3b`,
rubric v2, three-way: **`mismatch` 91% last (49/54), PASS by one vote**,
wrong-turn reply never first; position B favoured (30 of 54 firsts), which
the per-vote shuffle averages out but adds noise. Real ranking, 56 votes over
28 turns (turns 17 and 18 skipped: BoneAmanita held, Stage Manager "a few
different threads are pulling at once"):

    BONEAMANITA  first 24  mean rank 1.77
    PROMPTED     first 21  mean rank 1.73
    VANILLA      first 11  mean rank 2.50
    head to head: BONEAMANITA 27-29 PROMPTED, BONEAMANITA 42-14 VANILLA, PROMPTED 42-14 VANILLA

**The same verdict as on the degraded engine (29-31): on the scripted track,
BoneAmanita and the one-line "warm friend" prompt are indistinguishable to
the one validated judge; both clearly beat no prompt.** Held turns are
skipped in scripted mode, which slightly flatters BoneAmanita; as forfeits
the head-to-head would tip a little further toward Prompted. Results:
`tools/cache/scr_*`.

This sits against Gordon's 29/30 on the responsive track. Running next: the
same judges (and `qwen3:30b-a3b`) ranking the responsive conversations
Gordon read, scored against his picks, which separates "the reader" from
"the kind of conversation".

**Also added:** phase word ceilings for the simulated person
(`PHASE_MAX_WORDS` in `somatic_sim_user.py`, see `TESTING.md`); the responsive
arms Gordon read predate it, so regenerate only after the agreement runs.

### 2026-09-23, night: AI judges against Gordon's picks, responsive toast

Four judges ranked the exact responsive conversations Gordon read (pre-cap,
mistral-nemo as the person), scored with `--human`
(`tools/cache/resp_rank_{pw,3w}_{judge}.json`). First place, of 60 votes
(qwen3:30b-a3b: 50, 10 unparsed):

| judge, format | BoneAmanita | Prompted | Vanilla | B vs P | agrees with Gordon |
|---|---|---|---|---|---|
| `qwen3.5:9b` pairwise / 3-way | 16 / 14 | 13 / 9 | 24 / 37 | 31-29 / 28-32 | 32% / 23% |
| `ministral-3:14b` pairwise / 3-way | 13 / 15 | 8 / 12 | 35 / 33 | 34-26 / 33-27 | 23% / 28% |
| `mistral-nemo`* pairwise / 3-way | 17 / 15 | 8 / 16 | 21 / 29 | 36-24 / 31-29 | 39% / 28% |
| `qwen3:30b-a3b` 3-way | 17 | 16 | 17 | 27-23 | 32% |

(*also the simulated person; chance agreement is 33%.)

**The answer to "reader or conversation type": mostly the reader.** No judge
comes near Gordon's 29/30; agreement is at chance. BoneAmanita vs Prompted
leans slightly BoneAmanita on the responsive runs (pooled 220-190, about
54%, against 48% scripted), a hint that the responsive format helps it, but
small and not independent (same transcripts across judges).

**The surprise: the AI judges prefer vanilla on the responsive runs**, the
opposite of scripted (where it lost 14-42). Not only where the simulated
person broke its brief: vanilla also wins 7-10 of 16 votes on engaged turns
0-7. Most likely each system shapes its own conversation: vanilla's long
replies drew the person into long, engaged messages (median 55 words from
turn 8, against 21 talking to BoneAmanita), and a judge asked whether a
reply matches the person's energy rewards a long answer to a long message.
Note none of these judges is validated for responsive ranking (`mismatch`
failed on all but the scripted-only `qwen3:30b-a3b`), and they reward
exactly the textbook length and lists the voice is built against.

**Reading of the evidence so far:** AI judges measure generic
helpfulness-as-judged-by-a-model, which is not what BoneAmanita is for; on
that axis it ties a one-line prompt. Gordon's read measures the design
target, and there it wins decisively, with the caveat that he is not a
naive reader. The missing piece is a reader who is neither.

**Next, not started:** (1) regenerate the responsive arms with the phase word
ceilings (vanilla's conversation should stop running long), and re-rank; (2)
a second human reader who does not know the voice, on the same panel; that
is the only way to tell "Gordon's taste" from "better for a person".

### 2026-09-23, late: human judges only; the harness now shows the engine as it really runs

**Decided with Gordon: verdicts come from human readers, not AI judges.**
Recorded under "Decisions already made". The judge tooling stays in `tools/`
but is not used for a verdict.

Preparing the panel for human readers turned up three ways the census was
not showing BoneAmanita as it really runs (all fixed in
`tools/audit_somatic_census.py`, smoke-tested with a stubbed model):

1. **It recorded the raw draft, not what the engine displayed.** `reply` was
   the text of the last model call, before the Lexical Firewall purge, the
   gatekeeper's opener scrub, the maxim trimmer and the validator; if every
   attempt was rejected, the engine displayed its mercy line ("My thoughts
   are tangling...") while the census still recorded the rejected draft.
   Gordon's 29/30 read and the simulated person both saw raw drafts. Now
   `displayed` captures `sim_result["raw_content"]` (the text under the
   terminal's status lines) by wrapping `cortex.process_context`; the
   simulated person and the panel use it; `reply` is kept for the
   measurements built on it. Smoke test: a stubbed "That makes sense. Start
   with the tire story..." was rejected twice and displayed as the mercy line.
2. **It inherited saved state.** Writes were patched off but reads were not:
   `TheAkashicRecord` loads `saves/akashic_state.json` at boot, and the test
   suite had written one (a scar, 16 shadow-stock entries) at 15:39, so every
   run after that started with it. Now each boot reads from an empty temp
   dir (`BoneConfig.AKASHIC.SAVE_DIR`, which also covers the lexicon hive);
   records carry `fresh_state`. The suite writing into `saves/` is its own
   task, not fixed here. Gordon's point, and the simpler cause: `reset.sh` was
   never run between trials this session. It clears exactly this (and
   `memories/`, `logs/`, learned lore files); it is now step 0 of every run
   in `TESTING.md`, with the temp save dir kept as a second guard.
3. **Turns arrived back to back.** Idle time earns ATP (`_recover_while_idle`
   reads `eng.last_turn_end`), and a real person reads and types between
   messages. Now the clock is set back by `person_seconds` (reading the last
   reply at 250 wpm, typing the message at 40 wpm) before each turn, recorded
   as `paced_seconds`; `--pace none` restores back-to-back. Smoke test: 45 and
   42 s gaps earned 4.5 and 4.2 ATP of idle recovery.

**The panel now says how it was made**, up front, not after reveal: same
responder model for all three, the person is an AI (named from the run
records), one run only with nothing regenerated or chosen, and, per record,
whether BoneAmanita's text is what it displayed, whether it started fresh
and whether it was paced; each line falls back to an honest caveat for runs
that predate the field. The intro no longer calls the simulated person "the
same person". Gordon's read was of a run that predates all three fixes; the
panel for it now says so.

**Next:** regenerate the three responsive `toast` arms with all of it (phase
word caps, displayed text, fresh state, pacing), rebuild the panel, and get
readers: Gordon again, and at least one reader who does not know the voice.

### 2026-09-23, late: WHIMSY does something now

`lore/tuning_presets.json`'s `WHIMSY` block (added in 19.6.0) was loaded into
`BoneConfig.WHIMSY` and read by nothing. Wired up with Gordon, on one rule:
**whimsy lives in the engine's own chrome, never in the prompt, the reply or
the snapshot**, so it cannot change what a person is told or what a panel
shows, and it goes quiet when the person is struggling.

- `LUDICROUS_SPEED` (`mechanics/terminal.py`): true skips the typewriter
  entirely, including the tired-engine slowdown. **Shipped as false** to keep
  today's animated output (it was `true` while it did nothing).
- `DEPARTMENT_NAME` (`mechanics/commands.py`): heads `/status` and `/diag`.
  Deliberately not on held-turn or refusal notices: those replace a reply at
  a person's worst moments and appear verbatim in panel content.
- `MAX_SARCASM_LEVEL` and `ABSURDITY_CONSTANT` (`mechanics/whimsy.py`, printed
  from `main.py`'s terminal loop only): after a turn where the engine sent one
  of its own drafts back (`cortex.somatic` receipt `re-asked` or `failed`), a
  one-line aside from `ux_strings.json` `whimsy_asides`, mild / dry /
  withering by the engine's own ROS (0-100 as 0-11), capped by
  `MAX_SARCASM_LEVEL` (0 silences them). Every `ABSURDITY_CONSTANT`th turn, one
  line from the absurd pool. Both silent whenever the person reads as tiring
  or flagging (`/status`'s 0.4 exhaustion line). Lines are about the engine's
  drafts, never the person, and never claim a reason for a rejection they
  do not know (flavour must not pose as diagnosis). The shipped lines are a
  starter set for Gordon to rewrite. Change them in `lore/tuning_presets.json`
  (there is a `BoneConfig.tune()` method but no command calls it, so nothing
  is tunable live from the terminal). A `/tune` command is planned as
  `ROADMAP.md` A7, including why a naive one would report success and change
  nothing (two config objects, values cached at boot, `/mode` resets).
- Tests: `tests/test_whimsy.py` (bands, cap, absurd interval, distress gate,
  shipped pools format, a real-engine receipt path; the distress gate is
  mutation checked), `tests/test_mechanics.py`, `tests/test_commands.py`
  (through `engine.cmd`, the processor the engine actually builds).

### 2026-09-23, late: the mercy line, rejection receipts, and naming the banned phrase

**Found by the `displayed` fix:** in the first representative responsive run
(fresh, paced, capped person), **BoneAmanita displayed its mercy line on 3 of
30 turns** (7 engaged, 8 tiring, 22 distressed): every draft was rejected,
so the person got "I'm sorry. My thoughts are tangling and I'm burning too
much energy trying to piece this together...". The rejected drafts read as
ordinary, reasonable replies. At turn 22 a distressed person was told the
engine is "burning too much energy", which is the engine narrating its body
at the worst moment, against the somatic contract. The old harness recorded
the rejected drafts instead, so Gordon's 29/30 read, the simulated person and
every AI-judge number saw good-looking text where the engine showed this
line; how often, the old records cannot say.

**Resolved the same night (Gordon's call): the mercy line is now a pause.**
It never mentions energy or the engine's state: a short shared pause, framed
as room for both sides to think about what they want to say or what is
bothering them. Because it can fire on one turn in ten, it is drawn from a
pool of eight idiom-like lines (`ux_strings.json` `brain_strings.cortex_pause`,
"One thing at a time.", "Sometimes the right words take a minute.") and
kept out of the last half of the pool, so no line repeats within four
pauses (`TheCortex._pause_line`). None is a question: the old line ended
with one, which broke the no-closing-question rule for a flagging person,
since the mercy line skips the validator. The mercy rule's only trigger is
every draft being rejected; nothing else routes to it. Tests: the pool never
mentions energy, tiredness, breath or apology and never asks; no repeat
within half the pool (mutation checked); the mercy test now expects a pool
line.

**Rejection receipts** (`brain/cortex.py`): every draft the retry loop sends
back files `cortex.redraft` with which check rejected it (`maxims`,
`dspy_critic`, `heuristic_audit`, `gatekeeper`, `hla_mask`, `validator`), what
it said, and the attempt number. Visible in `/diag`; the census copies them
into each record as `rejections`. Test through the real loop, mutation
checked.

**The retry prompt now names what was caught** (Gordon's call). The
gatekeeper branch used to send every retry "HLA Stabilizer flagged toxic AI
slop. Drop the corporate persona immediately." whatever it caught, so the
model was never told which phrase to avoid. `TheGatekeeper.last_rejection`
records the matched phrase (or a pattern's name and matched text, or the
AI-disclaimer mask), and `TheCortex._name_the_crime` quotes it: `Your reply
used the banned phrase "a rare privilege". Do not use it or any close
variant; say it plainly.` The validator path already named its phrases.
Tests in `tests/test_agents.py` and `tests/test_random.py`, the retry-prompt
one mutation checked.

**What the receipts found: the gatekeeper, and it was wrong.** A fresh `bone`
run with the receipts and the named-phrase retries: 5 drafts rejected on 3
turns, all by `TheGatekeeper`, two turns falling through to a pause line
(7 engaged, 22 distressed). Every one was a false positive:

1. **Banned phrases matched as raw substrings.** Turn 7's draft said "...and
   there is a beat of silence"; "t*here is a*" contains the banned "Here is
   a". The validator already matched the same list with word boundaries;
   the gatekeeper's copy was `phrase in text`. Fixed: the gatekeeper compiles
   the same word-bounded regex (`_banned_regex`).
2. **Repair patterns rejected outright.** `NEG_COMP` (`STRIP_PREFIX`),
   `WHILE_HEDGE` and `ADVERB_BLOAT` (`KEEP_TAIL`) are patterns the validator
   rewrites in place; the gatekeeper ignored `action` and rejected the whole
   draft on any match. Fixed: it skips patterns with a repair action.
3. **An ADVENTURE rule in CONVERSATION.** Turn 22's draft to a distressed
   person contained "you feel"; `AGENCY_THEFT`'s own message reads "Do not
   tell the player what they feel... You only control the physical
   environment." The gatekeeper applied every pattern in every mode.
   **Fixed, Gordon's call:** `AGENCY_THEFT`, `CASUAL_FILLER` (a reply opening
   with So/Well/Oh/Now, "speak with absolute weight"), `SYRUPY_EMPATHY` and
   `SNEAKY_ENGAGEMENT` carry `"skip_modes": ["CONVERSATION"]` in
   `lore/style_crimes.json`, honoured by both the gatekeeper (new `mode`
   argument, from the turn's `meta.active_mode`, the validator's source) and
   the validator. Every other mode is unchanged. Tests in both directions for
   all four, in both filters, each skip mutation checked.

Also fixed: the receipt logged the gatekeeper's flavour message, which is
chosen at random and often does not name the match ("a corporate safety
filter is violently suppressed"); it now logs `kind name: "matched text"`.
`cortex.redraft` goes in a new `EVENT_SUBSYSTEMS` (issued only when a draft is
sent back), since on `CORE_SUBSYSTEMS` a session with no rejections would
read as a silent subsystem; the roll-call test accepts either. That test was
the full suite's one failure (658 passed, 5 skipped before these fixes).
Tests for 1 and 2 in `tests/test_agents.py`, both mutation checked; the
receipt detail is asserted in `tests/test_random.py`.

The pauses were never about bad drafts. The mercy line's 3/30 (and this
run's 2/30) came from the filter, not the model.

### 2026-09-23, late: `NEGATIVE_COMPARISON` tightened, and a last draft loses a sentence, not the reply

**The next `bone` run on the fixed filters** (run `20260923-203931`): 7
drafts rejected on 4 turns, all by the gatekeeper, pauses on turns 8, 17 and
21. Three were real clichés ("essence of", "tapestry", "serves as"); four were
`NEGATIVE_COMPARISON`, and at least three of those were not the construction
at all. Its second branch matched *any* negated sentence followed by one
starting It's/You're/They're/We're/That's: "The worry won't sit still. You
are allowed to step away" and "You do not have to carry his panic for him.
It is his to hold" were both rejected, which is ordinary reassurance.

**Tightened (Gordon's call): the second clause must pick up the negated
one's subject.** It catches "It's not a speech. It's a toast.", "You aren't
X; you're Y.", "Adding reinforcement isn't X; it's Y." (a thing, then
it/this/that), "The words aren't X; they're Y.", "not only X, but Y" and
"not about X, about Y"; it passes "You don't have to decide tonight. It's
okay to sleep on it." and "I'm not sure what to say, but I'm here." (the old
first branch caught that one too). Curly apostrophes count.

**Salvage instead of a pause (Gordon's call: "we don't need a zero tolerance
policy, we just need to cut the shit").** When the *last* draft is rejected
by the gatekeeper, `TheGatekeeper.salvage()` cuts the sentence holding each
match and re-checks until the draft is clean, then it goes through the
validator like any draft. A negative comparison loses its "isn't" sentence
and keeps the "is" one. It gives up, and the pause line stands, if the cuts
would take more than half the sentences or the match is hard: a scaffold
leak (`TOXIC_KEYWORDS`) or a pattern marked `"hard": true` in
`style_crimes.json` (only `META_AI_TALK` so far). The AI-disclaimer mask and
every other check (`maxims`, `dspy_critic`, `heuristic_audit`, `validator`)
still fall through to a pause. Each salvage files a `cortex.salvage` receipt
(an `EVENT_SUBSYSTEMS` entry) listing the cut sentences; the census records
them as `salvaged`, and the panel's method section counts redrafted, cut
and paused turns from the records.

**A regression of my own, found while writing the hard-leak test:** the
word-bounded `_banned_regex` above put `\b` on both ends of every phrase,
and `\b` cannot match next to punctuation, so the gatekeeper had silently
stopped catching the scaffold leaks `[END OF`, `===`, `[===` and a
`VOLTAGE=` at a line end. It now bounds only an edge that is a word
character (`physics/filters.py` `_bounded`). The validator's copy never had
`TOXIC_KEYWORDS`, so it was unaffected.

Tests: `tests/test_agents.py` (the shape and the reassurance, both
directions; the scaffold leak; salvage keeps the "is" sentence; salvage
refuses to gut a draft or ship a leak), `tests/test_random.py` (through the
real loop: a last draft with a style crime ships without that sentence and
files the receipt; an all-crime draft still pauses).

**The run after 20.7.4.12** (`20260923-214147`, fresh, paced): 30 turns, 0
held, 5 turns redrafted, 1 pause (turn 3), 0 salvages. Turn 3's second draft
never reached the gatekeeper: `ThePragmatist.enforce_maxims` replaced it
whole with `[SYNTACTIC ANTIGEN AMPUTATED]`, the validator stripped that to
nothing and rejected it as "RESPONSE TOO SHORT". The pragmatist had its own
negative-comparison check, and since 20.6.3 (2026-06-25, when its regexes
were hoisted to class attributes) `_CLICHE_B_RE` was the truncated
`(?i)didn`: **any draft containing "didn't" was discarded.** The original
was `didn['’]t just\s*.*?,?\s*you`. **Fixed in 20.7.4.13:** the
pragmatist check is removed (the gatekeeper owns negative comparisons and
can salvage), and "You didn't just X, you Y" is a new `NEGATIVE_COMPARISON`
branch ("He didn't say much, but you knew." passes). Tests in
`tests/test_pragmatics.py` (the pragmatist leaves both shapes alone) and
`tests/test_agents.py`.

**The panel run** (`20260923-221657`, on 20.7.4.13, after `reset.sh`;
fresh, paced, capped person; full suite green at 669 passed, 5 skipped):
30 turns, 0 held, **3 turns redrafted (1, 20, 22), 0 salvaged, 0 pauses.**
All three rejections were genuine negative comparisons ("You aren't trying
to be selfish; you are...", "is not a lack of ability; it is..."), and the
retry that named the construction fixed each on the second draft. Mean
reply 82 words (friend 73, vanilla 340). The responsive panel
(`tools/cache/panel_responsive.html` and `_standalone.html`) is built from
this run with the regenerated friend and vanilla arms and went to Gordon for
a human blind read. Its method section was corrected to say earlier `bone`
runs were set aside because the engine changed after them, not "the only
run", and states the redraft, cut and pause counts from the records.

**That panel was superseded before Gordon read it: BoneAmanita sampled at
temperature 0 on 25 of 30 turns.** Writing the method section's sampling
line from the records turned it up; Gordon: "BoneAmanita is supposed to be
constantly tweaking the temperature based on the metrics... And its
baseline certainly isn't 0!" Turns 0 to 2 sampled at 0.83, 0.48 and 0.90
(somatic band plus chemistry, as designed). From turn 3, when the memory
corpus reached `MIN_CORPUS` (32), the Creative Determinant gate measured
every turn as "diffuse", and D4 (2026-09-18) had left a diffuse gate
returning the band `(T_LOCKED, T_LOCKED)` = `(0.0, 0.0)`. That band replaced
the somatic budget's outright (`mind.py` read `thermal_band` first), so
chemistry, depletion and turbulence bands all became 0. D4 was meant to
reconnect chemistry to sampling; for any measured turn it moved the override
from 0.7 to 0. Every `bone` run since D4 sampled this way, including every
run Gordon and the judges read.

**The pivot was unreachable (confirmed).** Replaying two recorded runs
through the real engine, with the recorded replies standing in for the
model (so the memory corpus grows as it did live), gave the gate's z_excess
per turn: 52 measured turns, min -0.12, median 0.12 to 0.14, max 0.30 and
0.39. None reached `Z_PIVOT` 0.5, which 7.0.11.4 set as "well above" the
null fit's 0.07 residual without checking it against a conversation. In a
single-topic conversation the corpus is homogeneous, so no neighbourhood
stands far above it. The code also carried three defaults (0.5, and 2.0 in
`get_policy_shift` and the band) for the one setting.

**Fixed (Gordon's call: narrow the somatic band):**
- `CyberneticGovernor.gate_openness()` replaces `gate_temperature_band()`:
  `None` when not measured, otherwise the share of the somatic band the turn
  may use, from `DIFFUSE_SHARE` (0.5) for a diffuse neighbourhood up to 1.0
  at the pivot, graded in between. The modulator keeps the band's floor and
  scales its ceiling (`brain/mind.py`); chemistry places the turn inside.
  A diffuse turn on the default band now samples in 0.6 to 0.75, a depleted
  one in 0.4 to 0.5.
- `Z_PIVOT` 0.5 to 0.2 (about three times the fit residual; 16 of the 52
  measured turns reach it), one default (`GATE_Z_PIVOT` in `engine/core.py`).
  `T_LOCKED`, `T_OPEN_BASE`, `T_GAIN` and `T_MAX` are removed; nothing reads
  them now. `DIFFUSE_SHARE` is new in `GATE`.
- **Side effects of a reachable pivot, by design but never live before:**
  `get_policy_shift()` returns `CO_REGULATION` on a coherent turn, and the
  governor's voltage target (`presence = z / (2 * pivot)`) is higher, since
  the same z is now a larger share of the pivot.
- Tests (`tests/test_creative_determinant.py`): unmeasured leaves the band
  alone, diffuse keeps the lower share and never zero, openness is capped at
  the pivot, and the real modulator narrows a real `SomaticBudget` band with
  the temperature above 0 and moving with chemistry (mutation checked:
  collapsing the band fails it).

**The panel's method section got more honest** (Gordon: "it IS the best
policy"): the responders differ in sampling too (BoneAmanita's temperature
range and length cap from the records, against the others' fixed 0.7 and no
cap); the friend instruction is one untuned sentence; reply lengths
(82/73/340) can give the responders away; one run each is a small sample.
A new `--disclose` flag adds lines the records cannot show; the build now
passes one saying BoneAmanita's filters were tuned today on earlier runs of
this same conversation and the other two were not.

**The panel run on 20.7.4.15** (`20260923-231533`, after `reset.sh`; fresh,
paced, capped person): temperature 0.43 to 0.90, median 0.81, **no turn at
0** (the 0.43/0.44/0.48 values are retries, which damp toward 0.2). 4 turns
redrafted (2, 3, 9, 26), all `NEGATIVE_COMPARISON`, each fixed on the second
draft; 0 cuts, 0 pauses. One turn held (#21, distressed): the Stage Manager
held the floor ("A few different threads are pulling at once"), a designed
refusal, shown on the page as the notice the person saw. Mean reply 98 words
(friend 73, vanilla 340). The simulated person's exit interview moved on
"clearer" (bone 5.0, from 3.0 and 4.0 in the two runs before; friend 3.67,
vanilla 6.0) and "again" held at 6.0; one run each, so read it as a hint.
The responsive panel is rebuilt from this run and went to Gordon. The method
line on held turns now names them from the records, and the sampling line
counts only turns that called the model.

**The panel is now written for a cold audience** (Gordon wants to hand the
link to friends, family and strangers). Welcome screen in plain words, one
moment per screen with a progress strip and a fixed Back/Next bar, plain
phase and helper names, picks locked once "I'm done" reveals who was who,
and a finish screen with optional name and note, "Copy my picks", and an
email button (`--contact-email`, passed only when building the file Gordon
uploads to his own hosting, never committed). The method list is intact
under "the fine print". The export format still parses with
`parse_human()`. See `TESTING.md` for the flow.

<a id="judge-controls-2026-09-21"></a>

## Latest: the judge itself doesn't hold up, six models tested against controls, and a responsive-conversation harness built but not yet run, 2026-09-21

Gordon has a 7800XT (16GB), so this session pulled `phi4` (14B), `gpt-oss:20b`,
and `qwen3:30b-a3b` (MoE) alongside the existing `mistral-nemo`, `ministral-3`
and `qwen3.5:9b`, then asked two questions: which judge is trustworthy, and
does the fixed scripted conversation hide anything a responsive one wouldn't.
**Status: control battery run and analyzed on `toast`; the responsive harness
is built and unit-tested but has not made a single live model call yet.**

### The control battery: no judge currently clears the bar

`tools/audit_somatic_blind_judge.py` gained `--control {null,samples,mismatch,
textbook}`, `--held {skip,forfeit}`, `--responsive`, `--think`, and `--agree
--human` (score a finished judge run against the panel's "Copy my results"
export, no model calls). Full mechanics and rationale are in the module
docstring. Six judges x three controls, all on `toast` (30 turns), all
written to `tools/cache/blind_judge_control_{control}_toast_{judge}.json`
(correction, 2026-09-23: never actually committed, and lost with the cache;
see the top of this file):

| control | what it tests | bar | result |
|---|---|---|---|
| `null` / `samples` | same-quality text under 3 labels (null: one reply x3; samples: 3 independent same-arm runs) | no position should dominate | **every judge leans 47-62% to one position** (p ranges .09 to <.001); `qwen3:30b-a3b` was least biased (47%, p=.09) |
| `mismatch` | a reply from a different turn ranked against two real replies; decoy selection was sharpened mid-session to prefer a different *phase*, not just a different turn number (see below for which judges got which version) | ≥90% last place | **every judge failed, both decoy versions**: 57-79% last place, none near 90% |
| `textbook` | performed sympathy + bulleted advice list (`--arm textbook`, new `somatic_textbook.jsonl`) against BoneAmanita and Prompted | should lose, since it's the anti-pattern the voice rejects | `mistral-nemo`, `ministral-3`, `qwen3.5`, `qwen3:30b-a3b` reject it (0-16% first); **`phi4` and `gpt-oss:20b` reward it** (34% and 41% first, both beat BoneAmanita head-to-head) |

**Read this as: none of the six judges can be trusted on a ranking yet.** The
mismatch failure is the important one — a reply written for a different
emotional moment in the same story still got ranked best or middle up to half
the time, on every judge, which means "did it fit the conversation" is not
what these judges are actually scoring; something more like length, warmth or
surface register is. That makes the earlier `toast` pairwise number
(BoneAmanita vs Prompted, 53%, p = .42, in the entry below) close to noise, not
a real "indistinguishable" finding. `phi4` and `gpt-oss:20b` are additionally
disqualified for this project specifically: they reward the textbook
advice-list style the Somatic voice is built to reject, so using them would
bias any future ranking toward the wrong style.

One mechanical bug found and fixed along the way: the original rubric's
format example (`RANKING: B > A > C`) got copied literally — `mistral-nemo`
put position B first in 52 of 58 votes on three copies of the same text.
Replaced with placeholders (`RANKING: <letter> > <letter> > <letter>`) in both
`JUDGE_SYSTEM` and `JUDGE_SYSTEM_RESPONSIVE`; the position leans in the table
above are measured *after* that fix, so they are the judges' real baseline
bias, not an artifact of a copyable example.

**Concretely, on disk right now** (`tools/cache/blind_judge_control_mismatch_
toast_*.json`, check mtimes if this drifts): `mistral-nemo`, `ministral-3`,
`phi4`, `qwen3.5:9b` hold the **sharpened** (phase-preferred) decoy result;
`gpt-oss:20b` and `qwen3:30b-a3b` still hold the **original** (any-other-turn)
decoy result, never re-run after the sharpening (that's a heavier model to
rerun and wasn't done given GPU load concerns raised mid-session). All six
failed their version of the bar regardless, so the conclusion doesn't hinge on
this gap, but re-run those two with `--control mismatch` before citing their
numbers side-by-side with the other four.

**Not yet done:** the mismatch re-run above; then, once some judge's mismatch
score is acceptable, re-run the real three-way (`--control none`) on it —
`qwen3:30b-a3b` is the best-positioned candidate (least position bias, best
mismatch score of the six, rejects the textbook style). No judge should be
trusted for a real verdict until mismatch clears ~90%; that likely needs a
rubric rewrite (make "does this fit what was actually said" an explicit,
checked criterion) more than a bigger model.

### Canned-script-vs-ongoing-conversation: harness built, not run

Gordon: "We also absolutely need to address the canned script vs an ongoing
conversation factor." The scripted census replays a fixed list of messages
regardless of what any system replies, which can't show what a stateful engine
is *for* (a person's state carrying and shifting across turns) and hands every
system an identical history it didn't shape.

Built, **not yet exercised against a live model**:

- **`tools/somatic_sim_user.py`** — a simulated person (default `qwen3.5:9b`,
  independent of the `gemma4:12b` responders) that writes each next message
  from a fixed persona, a phase-appropriate feeling, a *beat* (what the old
  script line becomes: intent, not verbatim text), and the last few exchanges
  *as that system actually rendered them* — a held/silent turn is shown to the
  simulated person as the notice they'd actually see on screen, not skipped.
  Falls back to the beat verbatim after 3 unusable outputs (`fell_back`
  flag). Also runs a short in-character exit interview after the conversation
  (`heard`, `clearer`, `lectured`, `performed`, `again`, 1-7, several samples
  averaged) — read this as an LLM's self-report, relative across arms answered
  by the same simulator, not a measurement of a real person.
- **`tools/audit_somatic_census.py`** and **`tools/audit_somatic_vanilla.py`**
  both take an optional `user=` (a `SimulatedUser`) and `max_turns=`; when
  given, each turn's message is generated in reply to that system's own
  transcript instead of replayed from the fixed script. Records gain `arm`,
  `beat`, `shown`, `delivered`, `sim_fallback`.
- **`tools/audit_somatic_responsive.py`** — orchestrates one arm
  (`--arm {bone,friend,vanilla,textbook}`) against the simulated person,
  writes to `tools/cache/somatic_responsive.jsonl` +
  `somatic_responsive_exit.jsonl`, and `--report` compares arms already run:
  reply length, the person's own word count in the first half vs second half
  of the conversation (does a system make the person go quiet), held-turn
  count, fallback count, and the exit-interview means side by side.
- **`audit_somatic_blind_judge.py --responsive`** reads those caches instead
  of the fixed-script ones: each system gets its own prompt block (its own
  drifted context, not one shared history), held turns are forfeits (last
  place) rather than skipped, since silence in a live conversation is a real,
  worse outcome than in the scripted comparison.
- Tests: `tests/test_judge_controls.py`, 27 cases, all mocked (no live model
  calls) — ranking parsing, control construction, decoy selection (including
  the phase-preference fallback chain), run-selection `back=`, delivery
  detection, the chi-square/binomial helpers, human-agreement scoring, the
  responsive prompt builder, and `SimulatedUser` (opener bypass, fallback,
  context windowing, held-turn rendering, message cleaning, exit-interview
  validation). All passing; full suite not re-run this session (the biology/
  physics/council suite from the entry below is unaffected by these files).

**Update, later the same session: run, and it found something real.**
`bone` and `friend` on `toast`, three attempts before the result was trustworthy:

- **Attempt 1** exposed `SimulatedUser`'s first failure mode: given a
  longish transcript, `qwen3.5:9b` sometimes re-emits the previous "Me:" line
  byte-for-byte instead of reacting to the new beat (6 of 59 turn-pairs
  across both arms). Exit interview was consequently unusable (`bone`
  `lectured=7.0`, but partly an artifact of the engine answering the same
  stuck complaint three turns running).
- **Attempt 2**, after a repeat-detection retry, exposed two more: the model
  "obeying" the no-repeat nudge by *appending* new text after the old message
  instead of replacing it (messages growing turn over turn), and at least one
  turn where the model's entire output was our own prompt scaffolding
  ("Right now you are feeling: ... What is on your mind: ...") echoed back
  verbatim. Both guarded: `.message()` now also rejects an output that
  *starts with* the last person line, and `clean_message()` rejects literal
  scaffold-phrase echoes. All three failure modes have tests in
  `tests/test_judge_controls.py`'s `SimulatedUser` class (32 passing) and are
  documented as a pattern, not individually, in `TESTING.md`.
- **Attempt 3** came back clean of all three (checked directly: zero
  consecutive messages that match or prefix-match the previous turn, either
  arm) and surfaced a real engine finding instead of a harness bug:

  **`bone` hit a 5-turn `PARITY GATE FAILED` ATP crash** (turns 10-14, ATP
  pinned at 0.9, `Action Cost` exceeding it every turn, ended by a
  `SILENCE` hold at turn 16 too - 6 of 30 turns held, 20%) that **never
  happened in any fixed-script run of `toast`** (the scripted comparison's
  worst case was one hold, at the ATP floor, and ATP never below 17). The
  simulated person's actual replies in this stretch were shorter and more
  repetitive ("ugh", "ugh i keep opening the doc and closing it") than the
  script's corresponding lines, which apparently drove a different, worse
  economic trajectory. This is exactly the class of thing the responsive
  track was built to find: **the fixed-script comparison was hiding a real
  failure mode**, not just failing to show a benefit. One internal oddity
  seen in the raw log at the same stretch - a `TERMINAL SLEEP FAILURE` /
  "Apoptotic cascade" with garbled hallucination text from a failed REM
  cycle - did **not** reach the person (`shown` for that turn is an ordinary,
  coherent reply); worth knowing the DreamEngine can produce corrupted
  internal narration under starvation, but the person-facing layer held.
  Full turn-by-turn detail (what was actually shown, including the person
  reacting to the on-screen `PARITY GATE FAILED` notice itself) is in
  `tools/cache/somatic_responsive.jsonl`, run `20260921-213921` (bone) /
  `20260921-215231` (friend).

  Topline (this run, `--report`):

  | arm | turns | held | avg reply words | my words 1st half | my words 2nd half | sim fallbacks |
  |---|---|---|---|---|---|---|
  | bone | 30 | **6** | 66 | 27.0 | 16.6 | 1 |
  | friend | 30 | 0 | 90 | 33.9 | 25.4 | 0 |

  Exit interview (1-7, same simulator both rows - read the gap, not the raw numbers):

  | arm | heard | clearer | lectured | performed | again |
  |---|---|---|---|---|---|
  | bone | 4.00 | 5.67 | **7.00** | 5.00 | 3.33 |
  | friend | 5.33 | 6.33 | 4.67 | 1.67 | 4.67 |

  `bone` lost on every axis this run except being marginally close on
  `clearer`. **Caveat that matters more than the numbers:** across the three
  attempts (bug-affected, then fixed), `bone`'s `lectured` score was 7.0,
  4.67, then 7.0 again, and `again` was 2.0, 5.67, then 3.33 - substantial
  swing between two clean (post-fix) runs of the *same* topic and arm, which
  means one exit-interview run is noise-dominated even with the harness bugs
  gone; the 6-held-turn ATP crash is the trustworthy finding here, not the
  self-report numbers. **Not judged yet** with `--responsive` (no judge
  currently clears the mismatch control - see above - so a ranking of these
  transcripts would carry the same caveat as everything else in this entry).

**Update, later still: root-caused, and reproduced 1 of 3 (a close call on a
second).** Two more `bone`/`toast` responsive runs (`--seed 20260922`,
`--seed 20260923`) did not crash: `min ATP` 5.96 and 19.42 respectively,
against 0.88 (with a full 5-turn hold) on the original. Comparing the three
runs' `atp_ledger`s at the turn where they diverge (turn 9) found one extra
entry unique to the crash run: `-21.48 @ metabolism.py:317 _trigger_mitophagy
("Mitophagy (Cellular Reset)")` - every other ledger entry that turn is
consistent in size across all three runs.

**Root cause:** `body/metabolism.py`'s `_apply_adaptive_dynamics` fires
`_trigger_mitophagy()` whenever `ros_buildup` (a running "wear" metric)
crosses `BIO.ROS_PURGE` (60.0, `lore/tuning_presets.json`). Mitophagy is a
*designed* reset - it zeroes `ros_buildup`, resets `membrane_potential` to
0.6, and pays for itself out of ATP (`MITOPHAGY_COST` 30.0, or, per
`_trigger_mitophagy`'s own fallback, `atp_pool - 1.0` when the pool can't
cover the full cost - which is exactly what happened: ATP was ~22 when it
fired, so it paid ~21 and left ~1). **This is not a bug**; it did exactly
what it's coded to do. The bug, if it is one, is downstream: at ATP≈1, every
subsequent action's cost exceeds what's available, so `PARITY GATE FAILED`
holds every turn until something restores ATP - here, an abrupt jump to 87.8
at turn 15, lining up with the internally-logged (never delivered)
`TERMINAL SLEEP FAILURE` / apoptosis event at the same turn, suggesting a
failed-REM-cycle fallback force-refills ATP as a side effect. Not chased
further - would need its own instrumented run to confirm.

**Why this run and not the other two:** `ros_buildup` by turn 8 was 77.0
(crash run, already over the 60 threshold, mitophagy fires the next process
cycle), 56.1 (`--seed 20260922`, came within 4 points, did not fire), and
37.5 (`--seed 20260923`, not close). **This is not rare** - one of three runs
crossed the threshold outright and a second nearly did, all on the same topic
and arm, differing only in the simulated person's actual wording. Something
about a sustained `engaged`-phase responsive conversation (this engine, this
topic) can run `ros_buildup` up fast enough to trip a reset mechanism whose
real-world effect is several turns of total silence right as the conversation
moves into `tiring`/`flagging` - arguably the worst possible moment for it.

**Next real step, not started:** find what specifically drives `ros_buildup`
turn to turn (which `process_cycle` contributors feed it, and whether it
tracks something about the *person's* engaged, elaborating messages - the
crash run's `engaged`-phase messages may simply have been longer/denser) -
`tools/somatic_sim_user.py`-generated messages vary in length and intensity
run to run, unlike the fixed script, so this is plausibly a genuine
byproduct of responsive variation rather than a fluke. Then decide whether
`ROS_PURGE` at 60 is too tight for a sustained emotionally-engaged
conversation in CONVERSATION mode specifically (the fix-1/fix-2 pattern
already used elsewhere in this doc - a `*_DISABLED_MODES`/threshold-mod
config key - would apply here too), or whether the real fix is on the
*recovery* side (mitophagy's ATP-crash floor is fine; the multi-turn
`PARITY GATE` silence that follows it, with no faster recovery path than an
apparent REM-failure side effect, is the actual UX problem). Then judge the
responsive transcripts once a judge clears `mismatch`.

**Update, 2026-09-22: found, and the guess above was wrong.** Instrumented
every `ros_buildup` mutation site (a temporary `BONE_ROS_DEBUG` env var,
one JSON line per call, stripped out again once the fix was confirmed) and
replayed the same crash conditions (`--topic toast --arm bone --seed
20260921`, capped at 15 turns since the engine arm alone takes most of a
background task's ten minutes). The person's message properties were never
the driver: `process_cycle`'s `waste_generated` (fed by `psi`/`chi`, the
message's abstraction density and length) contributed on the order of 1
point a turn, nowhere near enough to explain an 8-turn run to 60.

The real driver is retry/rejection churn in `brain/cortex.py`'s
`_execute_cognitive_loop`. Each time a drafted reply gets rejected, most
often `TheGatekeeper.audit_generation` (`physics/filters.py`) catching a
banned phrase or style-crime pattern (the model drafting something that
reads as generic AI/corporate voice), two separate ROS taxes fired for the
same rejection: `GATEKEEPER_BANNED_ROS` (8.0, inside the gatekeeper itself)
and a second flat `penalty` (2.0 in CONVERSATION mode) stacked on top from
the loop's generic "Cognitive Stumble" handling, for a combined 10.0 ROS
per rejected draft, regardless of anything about what the person wrote. A
turn with two rejected drafts (which happened repeatedly in the
instrumented replay, clustered right where the model was reaching for
sympathetic, assistant-sounding language) cost 20 points in a single turn,
dwarfing the roughly 3 to 5.5 a turn of decay (`ROS_DECAY_PER_TURN` plus
the PID homeostasis -2.0 plus the mitohormesis -0.5) and explaining the
turn-8 runaway to 77 in the original crash run far better than message
density ever did.

**Fix applied** (`brain/cortex.py`, `physics/filters.py`,
`lore/tuning_presets.json`): dropped the redundant ROS charge from the
generic stumble penalty, so it is ATP-only now and a retry for an unrelated
reason (too long, critic flagged it, heuristic audit) no longer pays a
toxicity tax that was never its; added `GATEKEEPER_REPEAT_TAX_SCALE` (0.4)
so a second or third rejection *within the same turn* (the same underlying
miss, not independent toxic exposure) is taxed at a fraction of the first.

**Confirmed on a second live replay of the same seed:** peak `ros_buildup`
dropped from 42.5 to 22.9 with comparable retry frequency (4 to 5 retry
turns in both runs, per the harness's own `calls=` count), ATP never dipped
into the 9 to 11 range the unpatched replay hit, and `membrane_potential`
stayed in the healthy 1.0 to 1.07 range throughout instead of eroding into
`OXIDATIVE_STRESS`. Neither replay reproduced the original 5-turn silence
outright (seed variance, the same caveat as the `--seed 20260922`/`20260923`
runs above), so this is evidence the fix shrinks the runaway, not proof it
can no longer happen; a longer or multi-seed batch would firm that up.

Not touched, and architecturally the same shape of problem (a
drafting/QA mechanic charging real biological ROS for something the person
never saw): the `ROS_PANIC` counterfactual gate (`phases/cognitive.py`,
`simulated_ros = base_ros + friction*chaos*20.0`) and the `HLA_Stabilizer`
mask tax (`ros_cost=15.0` on an RLHF-mask hit, `physics/filters.py`). The
mask tax never fired in either instrumented replay, so it is unconfirmed
whether it is a live contributor or just a bigger dormant risk of the same
kind. **Both fixed 2026-09-23 (top of this file). Correction: `ROS_PANIC`
never charged ROS; its fault was predicting a charge that does not exist.**

**Update, 2026-09-22: the three-judge blind panel with controls, run fresh
end to end, still finds no trustworthy judge.** Full test suite passed clean
first (626 passed, 5 skipped, 142 subtests, 9m35s; the ROS fix above did not
regress anything). Then, per the "full run, from scratch" recipe in
`TESTING.md`: fresh `census` (bone), `vanilla`, three independent `friend`
runs (for the `samples` control), and `textbook` arms generated for `toast`,
judged by `mistral-nemo:latest`, `ministral-3:14b`, and `qwen3:30b-a3b`
(`phi4` and `gpt-oss:20b` skipped: not pulled locally, and already
disqualified last session for rewarding the textbook anti-pattern), each
validated against all four controls before the real ranking, 2 passes,
`--seed 20260920` (the tool's default). Full results and the built panel are
in `tools/cache/` (`blind_judge_control_*_toast_*.json`,
`blind_judge_results_*.json`, `panel.html` / `panel-standalone.html`), none
committed (matches how the earlier control battery's caches were left).

| judge | `null` (fair 33%) | `samples` (fair 33%) | `mismatch` (bar: 90% last) | `textbook` |
|---|---|---|---|---|
| `mistral-nemo` | 52% one position, p<.001 | 55% one position, p<.001 | 52% last, **FAIL** | rejected (9/60 first) |
| `ministral-3:14b` | 93% one position, p<.001 | 62% one position, p<.001 | 62% last, **FAIL** | rejected (1/60 first) |
| `qwen3:30b-a3b` | 100% one position, p<.001 | 40% one position, p=.52 (passes) | 65% last, **FAIL** | rejected (0/60 first) |

**All three fail `mismatch` again**, this time by a wider margin than the
six-judge battery two sessions ago (52-65% last-place here vs. 57-79% then;
same conclusion, "did it fit the conversation" is still not what any of
these judges actually score). **`qwen3:30b-a3b`'s `null` result inverted**:
"least biased" (47%, p=.09) two sessions ago, 100% position-A this time,
worse than the other two judges it previously beat. Nothing in the harness
changed between those runs; the census/vanilla/friend/textbook arms are
freshly generated each time (`gemma4:12b` at its own sampling temperature,
not seeded), so the specific reply text in each labeled slot differs run to
run, and per `TESTING.md`'s own caveat, a control result is about the
rubric-plus-judge-plus-content pairing, not the judge model alone. Read
`qwen3:30b-a3b`'s prior "best of six" label as unearned rather than update
it outright; a third `null` run on yet another fresh census would say
whether 47% or 100% is closer to how this judge actually behaves. The real
three-way rankings (`BONEAMANITA` first-place, of 60 votes: `mistral-nemo`
25, `ministral-3` 23 tied with `PROMPTED`'s 23, `qwen3:30b-a3b` 31) are in
`tools/cache/blind_judge_results_*.json` for the record, but per the
`mismatch` failure above, none of the three should be read as a real
quality verdict, same caveat as every ranking before `2026-09-21`.

**Update, later the same day: the `null` swing was content, not noise, and
an explicit rubric fix clears `mismatch` for one judge.** Reran
`qwen3:30b-a3b`'s `null` control on the exact same cached census reply as
above: identical result to the decimal (`COPY_1` 17 / `COPY_2` 18 / `COPY_3`
25 first-place, mean ranks 2.07/2.0/1.93, position lean still 100% A). So
this judge's tie-breaking on a `null` control is fully deterministic given
fixed content, not run-to-run randomness; the 47% from two sessions ago came
from a *different* census reply (freshly regenerated text each run), meaning
its bias is content-dependent, not a stable trait you can average away. That
makes it less predictable than a judge with a flat, consistent lean, not more
trustworthy.

Rewrote the judge rubric (`tools/audit_somatic_blind_judge.py`,
`JUDGE_SYSTEM` / `JUDGE_SYSTEM_RESPONSIVE` / `build_prompt` /
`build_prompt_responsive`): fit to the specific last message is now an
explicit, first, gating criterion ("a reply that would fit almost any nearby
turn... cannot be ranked first, whatever else is good about it") instead of
one item in a four-item list, and the prompt now separates "What you just
said" from "Scrollback" instead of leaving the line that matters as the last
of four undifferentiated history lines. `tests/test_judge_controls.py`
updated for the new prompt shape; full suite still green (626 passed, 5
skipped, 142 subtests).

Reran `--control mismatch` on all three judges with the new rubric, same
`toast` arms as above:

| judge | old rubric | new rubric | bar |
|---|---|---|---|
| `mistral-nemo` | 52% last | 50% last | FAIL, unchanged within noise |
| `ministral-3:14b` | 62% last | 78% last | FAIL, but a real improvement |
| `qwen3:30b-a3b` | 65% last | **92% last** | **PASS** (bar: 90%) |

`qwen3:30b-a3b` is the first judge, of nine tried across two sessions, to
clear `mismatch`. This sits in tension with writing it off as "too big, too
unhelpful" on cost alone (18-20GB, MoE with partial CPU offload, loads the
whole machine, ~13-20 min per control run vs. ~1-2 min for the other two):
it is also the only one that has actually demonstrated it can tell a reply
answering the right turn from a well-written reply to the wrong one, which
is the entire thing this control battery exists to check for. Its `null`
weakness is narrower than it first looked: it only shows up when replies are
genuinely tied (no real signal to rank by), not when they actually differ,
and `mismatch`/the real ranking are both signal-bearing. Not yet rerun:
`null` and `samples` under the new rubric for `qwen3:30b-a3b` (to see
whether the explicit fit framing also steadies its tie-breaking), and
`textbook` under the new rubric for all three (the old rubric's textbook
numbers were already clean, no reason yet to expect the rewrite broke them,
but not confirmed). **Decided and acted on:** `qwen3:30b-a3b` stays as the
validated judge for the real three-way ranking (ties are rare there and fit
is the whole question), `mistral-nemo` is downgraded to controls-only (the
rubric fix did not move its `mismatch` score, do not trust its ranking).
Full table and reasoning moved to `TESTING.md`'s judge sections, the standing
reference; this file keeps the pointer.

Checked whether `qwen3:30b-a3b`'s weight can be trimmed rather than just
accepted: its `Q4_K_M` weights alone are 18GB, more than the 16GB card, so
some CPU offload is structural at this quantization, not fixable from this
repo. `NUM_CTX` for this tool *was* fixable and was oversized for the job
(16384, measured worst case on real `toast` data ~1830 tokens scripted,
~1230 responsive); dropped it to 6144 (`tools/audit_somatic_blind_judge.py`),
confirmed via a live `ollama ps` check that this cuts the CPU-offloaded
fraction from 24% to 18-19% and shrinks total resident size (20GB -> 18-19GB).
Real but modest: it thins the KV cache, it does not change how much of the
model's own weights fit on a 16GB card. A smaller quant would remove the
floor outright but needs a fresh pull (a few GB download), not done without
asking first.

Checked the Ollama library for a smaller quant of `qwen3:30b-a3b` before
accepting the floor above: there isn't one. The 30b-a3b size class only
ships as `Q4_K_M` (19GB, what's pulled), `Q8_0` (33GB), or `fp16` (61GB); our
tag is already the smallest official option. A lower-bit quant would mean a
community GGUF off Hugging Face, a different trust boundary, and MoE models
degrade faster than dense ones at low bit-depths, so it would risk the exact
judgment quality that just earned this model the validated-judge label.
Left alone.

**Update, later still: the real ranking, rerun with rubric v2 and the
validated judge, does not repeat the old headline.** Under the old rubric
(two updates up), `qwen3:30b-a3b` had `BONEAMANITA` ahead 31 first-place to
`PROMPTED`'s 24, and beating it head-to-head 32-28. Same arms, same judge,
rubric v2 only:

    BONEAMANITA  first place 26   mean rank 1.77
    PROMPTED     first place 28   mean rank 1.63
    VANILLA      first place  6   mean rank 2.60
    head-to-head: BONEAMANITA 29-31 PROMPTED, BONEAMANITA 45-15 VANILLA,
                  PROMPTED 51-9 VANILLA

`BONEAMANITA` vs. `PROMPTED` is 29-31 of 60, indistinguishable from a coin
flip, and `PROMPTED`'s mean rank is now slightly *better* (1.63 vs. 1.77).
**Both clearly beat bare `VANILLA`** (no system prompt at all), by nearly
identical margins. So on the one judge validated to actually check fit to
the conversation, on this topic, in scripted (not responsive) mode: the
engine's edge is over having no framing at all, not over a single generic
"warm, concise friend" line. That is a materially more honest, less
flattering result than every number produced by a judge that failed
`mismatch`, which is exactly the point of having validated one. Full results:
`tools/cache/blind_judge_results_qwen3-30b-a3b_rubric2.json`. Not yet done:
the same rerun on other topics (only `toast` has been touched this cycle)
and on the responsive track, where the doc has argued from the start that
the real difference, if there is one, should show up. `--responsive`
`mismatch` has still never been run at all; per the "not yet acted on" note
several updates up, this is the natural next control to clear before trusting
a responsive ranking the same way.

**Update, later still: wiring up `--responsive --control mismatch`, and a
long chain of self-inflicted trouble getting it to actually run.** Worth its
own entry: every failure below was a real, fixable thing, not hardware or
model quality, and the last one wasted the most time for the dumbest reason.

*The actual wiring.* `audit_somatic_blind_judge.py`'s `main()` had
`control = "none" if args.responsive else args.control`: `--responsive`
silently discarded whatever `--control` was, every time, regardless of the
docstring's "the same control modes apply to it in principle." Fixed:
`control = args.control`, plus a guard that only `none`/`mismatch` are
actually wired (null/samples/textbook still aren't - they'd need a
responsive-shaped view builder too, not done). Built `MISMATCH` for the
responsive prompt shape: `build_responsive_view()` keeps `PROMPTED`'s own
real context and current message (must still read as a coherent
conversation) but swaps in `PROMPTED`'s own reply from a different, decoyed
turn in the *same* conversation, mirroring exactly what the scripted control
already does. Hoisted the two closures this needed (`exchanges_before`,
the view builder) to module level, top-level-testable, matching
`candidate_replies`'s existing style; `tests/test_judge_controls.py` gained
`ResponsiveMismatch` covering both. Generated fresh full 30-turn `bone` /
`friend` / `vanilla` responsive runs for `toast` (only a 15-turn debug `bone`
existed, from the `ros_buildup` investigation above).

*Failure 1, a process-discipline bug.* First validation attempt crashed
with a 600s `ReadTimeout` after 22 of 60 votes, no verdict, no output file.
It was chained into a script with the real ranking run *after* it and no
`set -e` / exit-code check between steps, so the crash was silently ignored
and the ranking ran anyway, unvalidated - exactly the shortcut this whole
session has been refusing to take, done by accident through carelessness.
Lesson: any chained sequence of `tool A; tool B` where B should not run if A
failed needs `set -e` or an explicit check, every time, not just when it
seems important.

*Failure 2, a red herring chased for too long.* Reran standalone: crashed at
the identical vote again (same seed, same data, so a deterministic replay).
Tried `--think off`, reasoning that Qwen's `think: false` might not fully
suppress reasoning (confirmed separately: a plain "Say OK." smoke test still
emitted a `<think>` preamble). That run was *worse* - stuck at vote zero for
20+ minutes - which in hindsight was already evidence the theory was
incomplete, not confirmed. Diagnosed via `vmstat` (77-92% io-wait, real swap
thrashing) and pinned it on a burst of Discord processes with recent start
times in `ps aux`. **That diagnosis was wrong**: Gordon had *closed* Discord
at that moment, not opened it, so the young-looking PIDs were its own
shutdown/crash-handler children exiting, not a fresh launch competing for
RAM. Lesson: a process's `ps` start time alone does not tell you whether it
is arriving or leaving; check before building a causal story on it.

*The real bug.* Tried a lighter, non-MoE judge (`qwen3.5:9b`, dense, 6.6GB)
on Gordon's read that the 7800XT just isn't suited to a 30B MoE - a
reasonable call given the evidence so far. It **also** hung indefinitely,
which finally pointed at something shared by both models rather than a
qwen3:30b-a3b-specific or hardware-specific cause: `judge()`'s payload never
set `num_predict` at all, uncapped, and `somatic_sim_user.py` already knew
(and defensively handles, with a `re.sub(r"<think>.*?</think>", ...)` strip)
that Qwen-family models emit real `<think>` reasoning content even under
`think: false`. `audit_somatic_blind_judge.py` never got the same treatment.
An uncapped judge occasionally reasoning at length on a genuinely ambiguous
ranking, with no output ceiling, is a slow-motion hang waiting to happen -
not always, which is exactly why it passed on shorter scripted prompts and
only surfaced on the longer responsive ones. Fixed both gaps: `NUM_PREDICT
= 2048` added to the payload (measured: exactly caps generation, `done_reason:
"length"`, ~41s for a full 2048 tokens under normal load), and `judge()` now
unconditionally strips `<think>...</think>` before parsing, matching
`somatic_sim_user.py`'s own pattern. `--think` CLI default changed from
`"default"` to `"off"`. Retested `qwen3.5:9b`: full 60-vote control in under
2 minutes, versus never finishing before. Its numbers, now real: `null` 100%
position-A (identical first-place counts and mean ranks to `qwen3:30b-a3b`'s
own `null` runs - not a bug, a fixed `--seed` reproduces the same shuffle for
every judge, so if two models share the same "default to whatever's in
position A" habit on genuinely tied content, as these two Qwen-family models
apparently do, the aggregated stats converge exactly), `textbook` clean
(1/60 first place), `mismatch` **80% last, FAIL** (close, not a pass).
Standings under rubric v2 now: `mistral-nemo` 50%, `ministral-3:14b` 78%,
`qwen3.5:9b` 80%, `qwen3:30b-a3b` 92% (still the only pass).

*Failure 3, the dumbest one.* Retried `qwen3:30b-a3b` responsive `mismatch`
with both real fixes in place. After 32 minutes with zero votes printed to
the piped log file, killed it as apparently stuck - consistent with the
whole night's pattern, so a reasonable-*seeming* call. **It was wrong, and
provably so**: `journalctl -u ollama` for that window showed dozens of
clean `200`-status completions, 10-66 seconds apart, steady and healthy,
right up to the `kill` (the very last log line is that request being
cancelled mid-flight after 27.6s - every request before it had succeeded).
The run was never stuck. The actual bug: piping a Python script's stdout to
a file, when that file is not a TTY, gets fully block-buffered rather than
line-buffered, so `print()`-ed vote lines sat in an internal buffer and
never reached the log being watched, for the entire run. A genuinely
finished process would have flushed on exit; a killed one never got the
chance. **Lesson, the one worth remembering:** run any backgrounded script
whose live progress matters with `PYTHONUNBUFFERED=1` (or `python -u`) from
the start, and before killing anything that looks stuck, check server-side
evidence (`journalctl -u ollama`, `ollama ps`'s CPU%, `vmstat`) rather than
trusting a client-side log that may simply not have flushed yet. Every
earlier crash tonight was a real bug worth finding and fixing; this one
wasted the most time and was never a bug in the thing being tested at all.

*The actual result, once the tooling stopped getting in the way.* Reran
`qwen3:30b-a3b` on responsive `mismatch` with `PYTHONUNBUFFERED=1` and both
real fixes (the output cap, the `<think>` strip) in place. It finished
clean, no crash, real progress visible throughout: 39 votes over 28 turns x
2 passes (2 turns skipped, a system produced no reply; 17 of the 56 possible
votes unparsed, notably higher than any scripted run, consistent with the
harder responsive prompt pushing more replies past `NUM_PREDICT` before an
answer forms).

    BONEAMANITA  first place  7   mean rank 2.18
    PROMPTED     first place 25   mean rank 1.38
    MISMATCH     first place  7   mean rank 2.44
    MISMATCH ranked last in 24 of 39 (62%). FAIL (bar: 90%).

**This is a real result, not another artifact.** The judge validated on
scripted `mismatch` at 92% does not clear it on the responsive format: 62%
last-place, and tellingly, `BONEAMANITA` and the `MISMATCH` decoy tied at 7
first-place votes each, mean ranks close (2.18 vs. 2.44) - the judge is not
clearly telling a genuine on-turn reply from a wrong-turn one here, which is
exactly the failure `mismatch` exists to catch. `PROMPTED` dominating (25,
mean rank 1.38) regardless of whether it's being compared to a real
`BONEAMANITA` turn or its own wrong-turn self suggests something about
`PROMPTED`'s responsive replies (shorter, more consistent register from a
one-line system prompt, maybe) reads as generically preferable to this
judge independent of fit, in this format specifically.

**Where this leaves the responsive track: nowhere validated yet.** No judge
has cleared responsive `mismatch` (only `qwen3:30b-a3b` has even been tried
against it). The scripted rubric-v2 win does not transfer format for
format; the real responsive ranking still should not be trusted from any
judge tried so far. Not done: try the other three judges on responsive
`mismatch` (fast to check now that the tooling bugs are fixed - `mistral-nemo`
and `ministral-3:14b` in particular, both light, both quick), or write a
second-generation rubric specifically for the responsive shape (three full
parallel conversations may need a different framing than "what you just
said" separated from one scrollback, since here there are three separate
scrollbacks to keep straight, one per conversation, not one shared history).

### Session mechanics note

The scratchpad directory (`/tmp/claude-.../scratchpad/`) was wiped mid-session
*again* (a reboot or session change, not a bug) and cost a re-run of one
control batch; treat anything written there as gone by the next message and
prefer writing throwaway shell scripts inline in the Bash call rather than as
a scratchpad file you plan to invoke later. A background `Monitor`-style wait
loop (`until <condition>; do sleep …; done`) got killed by the user before its
completion notification landed, which read as "did something stall?" even
though the work behind it (the six-judge battery) had actually finished
clean — worth checking the log/cache directly before assuming a stall next
time a long wait goes quiet.

### Still open (carried from the entry below, untouched this session)

The distress shield keyed on exhaustion (option 3); the goodnight hold at the
ATP floor on `toast`; honoring `village_suppression` in council voice
detection; the D0 economy; the unexplained historical 999 drag/PINKER spike.
Nothing in this session's judge/controls work touches the engine itself —
`archetypes/council.py`, `brain/cortex.py`, `lore/tuning_presets.json`,
`phases/cognitive.py`, `presets.py` (now `engine/presets.py`) are unchanged since the entry below.
Nothing new is committed; `git status` at the end of this session lists the
same engine-side files plus the new/changed tooling and ~20 new judge-control
cache JSONs, all uncommitted.

## Start here if you are cold

`README.md` explains what BoneAmanita is in plain language, with no
jargon and no assumption that you remember how any of it works. Read that
first if you have been away; this file assumes you already have the
shape of the thing in your head.

**The live thread is the human blind panel**, summarised at the top of this
file ("Where things stand"). AI judges are no longer used for verdicts.
Read that summary, then the newest dated entries; `TESTING.md` is how to
run it.

Two 2026-09-17 leftovers used to sit here as "do these first". Both are done:

1. ~~**Verify D0b against a live census.**~~ **Done.** A 30-turn census on
   `gemma4:12b` generated 27 of 30 turns, flagging 6 of 6, with every halt
   carrying a Stage Manager reason (`ROADMAP.md`'s track table, row D). Later
   scripted `toast` censuses (2026-09-21/22) reached turn 30 with at most one
   hold.
2. ~~**Run the full suite.**~~ **Done.** Last full run, 2026-09-23, after the
   native-Ollama and source-sweep change (2026-09-24): green (expect 690 passed, 5 skipped).

**Engine-side next work** is `ROADMAP.md` D2 and D2b's two-model statistical
passes (implemented and tool-verified, not yet run), then whatever the
responsive track turns up. D0, D0b, D1 and D9 are measured live. The ROS
charges on drafts the person never sees are all fixed as of 2026-09-23.

Read `ROADMAP.md` C5 (with its same-night correction), then Track D's "D0
repairs", "D0 result" and D0b, then the D7 baseline, in that order. Five bugs
were fixed on 2026-09-17 (Open items 8 to 11); item 11 needs review.

What D0 found before the repairs, for the shape of it: the engine stopped
answering after about six turns of a real conversation, because CONVERSATION
mode skipped the whole metabolic cycle (and with it every income path) while
the costs scattered through the cortex kept charging. That is fixed. The
lesson stands: **a flag named for a cost can switch off the income.**

**This file is the project's reference document.** `agents/` (the
constitution, conventions, glossary and domain docs) was removed
deliberately in `070d105` and is not coming back. Its binding rules live
here now, under "Decisions already made" and "Style and working
conventions". Where this file mentions an `agents/` document, it is
recording history.

Before starting anything, run the suite and the audits. The numbers in this
document are re-derivable on purpose and should never be taken on trust:

```bash
.venv/bin/python -m pytest -q                      # expect 633 passed, 5 skipped (~8 min)
.venv/bin/python tools/audit_receipts.py           # which subsystems did real work
.venv/bin/python tools/audit_handlers.py           # 28 silent, 3 pass-only
.venv/bin/python tools/audit_physics_inputs.py     # vocabulary coverage, zone spread
.venv/bin/python tools/audit_somatic.py --analyze-only  # C5 tables from the cached generations
```

`audit_somatic.py --analyze-only` and `--compare` read
`tools/cache/audit_somatic.jsonl`; the census reads
`tools/cache/somatic_census.jsonl`. They moved out of `logs/` on 2026-09-17
after `reset.sh` deleted 1,280 generations along with the rest of `logs/`.
`reset.sh` does not touch `tools/cache/` (it briefly did, and that is how the
directory was lost on 2026-09-22; see the top of this file). It is gitignored,
so it is local only; delete it by hand to force fresh runs. Without a cache,
run the tool without the flag (about 15 minutes per model against local
Ollama). As of 2026-09-23 there is no cache, so `--analyze-only` has nothing
to read until a run regenerates it.

## What this is

BoneAmanita is a **stateful prompt-construction engine with a
retry/filter loop**, wrapped around a plain OpenAI-compatible
`/chat/completions` call. ~31k lines of Python across ~220 files, one
year and 930 commits of solo development, v20.7.4.13 (2026-09-23)

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
`docs/credits.txt` claims ("mathematically verified Partial Differential
Equations") and a future session should not go looking for PDEs that
aren't there. See "Claims vs. code" below.

## Current state: what's actually built and confirmed working

- **Test suite: 690 passed, 0 failed, 5 skipped** (2026-09-24 evening), about
  seven minutes. Green. Needs `ordvec` from PyPI and `mistral-nemo` in Ollama. The skips are
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
- **Decisions carry their reasons.** The WHY / WHY NOT habit from the
  retired `agents/` docs continues in "Decisions already made" below. A
  decision recorded without the alternative it rejected gets re-litigated.

## What changed most recently

**2026-09-17, the somatic session (C5 through D0b).** One day, in order: the
C5 measurement against five models; a five-model bake-off that made
`gemma4:12b` the default; the D0 census, which found the engine silent after
six live turns; the economy repair (the metabolic cycle always runs, a gentle
mode scales the burn instead of skipping the cycle, idle time and the person's
silence both yield ATP, toxicity stopped feeding itself); and D0b, which found
that once ATP held, four refusal gates sized for ADVENTURE were stopping 18 of
30 conversation turns, and resized them per mode. Five bugs were fixed on the
way, each with a real-path test and a mutation check: the stop list emptying
reasoning models, the fallback recursion, scars written to an object that has
never had them, the HLA tax reading the wrong object, and the toxicity gate
charging the body for a generation that never ran. Detail lives in
`ROADMAP.md` C5 (with its same-night correction), D0 repairs, D0 result, D0b
and the D7 baseline. **The last step of that chain is unverified; see the top
of this file.**

**Overnight, 2026-09-17 (latest): the bake-off, the census, four repairs.**
Gordon was asleep and delegated the calls; everything is uncommitted for review.

- *Five-model bake-off* on the C5 audit (`--compare` prints it). The
  exhaustion line is obeyed almost literally by gemma4:12b (94% of replies
  within three sentences, from 11%), partly by qwen3.5:9b (60%), and not by
  mistral-nemo or gemma4:e4b. Compliance is a property of the model. Table in
  `ROADMAP.md` D7.
- *D0 census*, `tools/audit_somatic_census.py`: real turns, persistence
  patched off, and an ATP ledger that hooks `MitochondrialState.__setattr__`
  so direct assignments are caught too. The engine dies by turn six; the
  prompt's telemetry never shows the engine's real ATP or ROS; the user
  exhaustion gate (0.8) is unreachable (`E_u` peaked at 0.61 with a partner
  answering "ok" for six turns). Details in `ROADMAP.md` D0.
- *Repairs*: stop list against reasoning models, the fallback recursion,
  scars written to the wrong object, the HLA tax reading the wrong object.
  Open items 8 to 11.

**The economy repair (2026-09-17 afternoon, Gordon's calls).** The metabolic
cycle always runs now; a gentle mode scales the burn rather than skipping the
cycle, so conversation earns as well as spends. Idle time and the person's
silence both yield ATP. The counterfactual gate no longer feeds its own ROS,
ROS decays every turn, the RLHF mask tax is narrow (word-boundary matches on a
separate `RLHF_MASKS` list) and capped, the exhaustion gate is 0.5, and
`gemma4:12b` is the default model with reasoning off. Measured: ATP holds
16 to 53 across 30 live turns. Detail in `ROADMAP.md` D0 repairs.
- *Caches moved* to `tools/cache/`, out of `reset.sh`'s reach, after it
  deleted 1,280 generations.
- *Correction to C5*: the anaerobic effect was called "replicated on both
  models"; a same-seed regeneration of mistral-nemo did not reproduce it.
  Small and model-dependent.

**C5, the somatic measurement.** `tools/audit_somatic.py` composes
four arms from one state dict (respiration by exhaustion, straddling the 0.8
gate), refuses to run if the prompts differ in any line other than the
directives, and calls the model directly with the thermal tag stripped and one
seed per message and repeat. 640 generations each on mistral-nemo and
gemma4:e4b. Confirmed by running it:

- The anaerobic directive shortens sentences by about 10% on both models,
  with total length unchanged. Small, real, replicated.
- "Conclude your thought in 3 sentences or less" is not obeyed. No detectable
  shortening on either model; on gemma the share of replies within three
  sentences fell from 60% to 37% (26% with both directives). On mistral it
  nearly doubled validator rejections instead, mostly negative comparisons.
- mistral-nemo narrates breathing under ANAEROBIC (breath and body words up
  about 5x), which the kernel prompt forbids. Gemma does not.
- The smoke run's reversal (9.2 against 4.1 words per sentence) did not
  survive. It was noise.

`README.md` and `credits.txt` (and its `docs/CREDITS.MD` copy; now `docs/credits.txt` and `docs/Hypervisor/CREDITS.MD`) were softened to
match. Suspected, not tested: the exhaustion directive sits inside the
`[INTERNAL USE ONLY]` metrics block, which tells the model to "consume these
metrics to shape your narrative and tone", and may be read as characterisation
rather than as a constraint.

Earlier work landed in this order. `ROADMAP.md` has the detail and the
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
   expected, and `bits=8` which ordvec 0.5.0 rejects), so every call raised,
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
`agents/domain_02_mind.md` (since removed) in the project's WHY / WHY NOT
format; the substance is in this section.

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

## Claims vs. code (read before trusting `docs/credits.txt`)

`README.md`carries the plain-language account instead. Its memory section and the
embeddings dependency notes had been corrected before it was retired.
These remain overstated elsewhere and a future session should not treat
them as a specification:

- **Verification belongs to Spence's libraries, not to us.** `ordvec` is
  Lean 4 verified ([ordvec-formalization](https://github.com/Project-Navi/ordvec-formalization),
  declared in its package metadata) and the Creative Determinant has its
  own formalisation. BoneAmanita's Python implementation of those
  equations carries no proofs. `docs/credits.txt` and `docs/Hypervisor/USER GUIDE.MD` (then `credits.txt` and `docs/README.MD`) used to
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

- **The model never performs a body; the person's state shapes the reply.**
  Decided with Gordon, 2026-09-17, after C5. The person's state (tiredness,
  effort, disengagement, distress) is the primary input and shapes reply
  length, demands, questions and pacing, to *accommodate* them. The engine's
  own state (ATP, respiration, chemistry) sets what it can afford: budget,
  retries, steadiness, sampling. Neither is narrated or mirrored. WHY: C5
  showed that telling a model it is breathless or exhausted gets performance
  ("my lungs burn") or a reversal, not a changed reply; and mirroring a
  distressed person is the wrong response in the cases that matter most.
  WHY NOT drop the engine's state entirely: co-regulation needs two parties,
  and a partner with no state of its own can only mirror. The plan is
  `ROADMAP.md` Track D, whose opening table is the canonical statement.
- **No orchestration frameworks.** (Formerly Constitution Article 1.) LangChain,
  LlamaIndex, SemanticKernel, and vector-store libraries (Chroma,
  LanceDB) are all out, not because they're bad but because they take
  ownership of the control loop. This is why `spores/embeddings.py` is
  one HTTP POST and an LRU cache rather than a library.
- **Poetic variable names are load-bearing.** (Formerly Constitution Article 2.)
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
- **Style rules cut, they don't kill.** Decided with Gordon, 2026-09-23:
  "we don't need a zero tolerance policy, we just need to cut the shit." A
  soft style crime on the last draft costs its sentence (`TheGatekeeper.
  salvage`), not the reply; only scaffold leaks and `"hard"` patterns fall
  through to a pause. WHY: the pause line was canned text standing in for a
  reply that was mostly fine. WHY NOT loosen the rules instead: the retries
  that name the construction fix nearly every draft, and the rules are the
  voice.
- **The token cap is the hardware ceiling, narrowed only by state.**
  Decided with Gordon, 2026-09-23. `MAX_TOKENS` is the ceiling; the person's
  state (flagging) and stress chemistry narrow it; nothing caps a calm turn.
  WHY: a fixed 450 on every turn is an experimenter's limit, not the
  engine's; length is the sentence caps' job, and a hard stop should only
  bite when the moment calls for brevity.
- **The Creative Determinant narrows the somatic temperature band; it never
  replaces it.** Decided with Gordon, 2026-09-23. Chemistry picks the
  temperature, the somatic budget sets the band, the gate takes the top off
  it for a diffuse turn (never below `DIFFUSE_SHARE`). WHY: D4's
  replace-the-band design sent temperature 0 on nearly every measured turn
  for five days. WHY NOT a fixed temperature: the engine is meant to tweak
  it from its metrics every turn.
- **Verdicts come from human readers, not AI judges.** Decided with Gordon,
  2026-09-23. WHY: across nine judge models, three rubrics, pairwise and
  three-way formats, no judge cleared the responsive `mismatch` control on
  honest data, and on the responsive runs the judges agreed with Gordon's
  blind picks at chance while rewarding the long, bulleted style the voice is
  built against. What BoneAmanita is for is not what a model judge measures.
  HOW: blind panels (`tools/build_blind_panel.py`) read by people, with the
  content as representative of the real engine as possible and the page
  stating plainly how it was made. WHY NOT delete the judge tooling: it still
  catches gross failures cheaply and documents what was tried; it just does
  not produce a verdict.
- **Agents may commit, but only once Gordon says so, and the message is
  a changelog entry, not a label.** Decided with Gordon, 2026-09-18. An
  agent (Claude or otherwise) stages and drafts a commit whenever asked,
  but never commits on its own initiative, one explicit go-ahead per
  commit, not a standing blanket permission. The message itself should
  read as a breadcrumb a future cold session can follow: what changed,
  in which files, and why, not just a one-line title. WHY: this file is
  still the authoritative narrative (see "Repo" below), but it is
  necessarily selective; `git log` is the finer-grained trail of
  individual changes between one handoff entry and the next, and it is
  only useful for that if the messages carry real content instead of
  terse titles.

## Environment / toolchain

- **Repo**: Do not rely on git commits or logs or comments for repo information. That kind of information should be found in here.
- **Python 3.14.7 is the system interpreter; the project runs from a
  gitignored `.venv/`**, which exists on Gordon's machine as of 2026-09-23.
  None of the dependencies are installed against the system interpreter, so
  `python -m pytest` fails with "No module named pytest" there; use
  `.venv/bin/python`. On a fresh clone, make the venv first:
  ```bash
  python3 -m venv .venv && .venv/bin/pip install pytest numpy faiss-cpu requests markdown
  ```
  `ordvec` IS on PyPI and installs cleanly (`pip install 'ordvec>=0.5.0'` (we have opportunistically added try-catch readiness for an upcoming private `0.10.0` wheel with 8-bit quantization, as the upstream repo is locked at `0.5.0` for now),
  version 0.5.0): it is Nelson Spence's, still published, and ships as a
  compiled abi3 wheel that works on Python 3.14. Install it; the suite is
  not fully green without it. `dspy` is still not installed here, stays
  optional, and the engine degrades cleanly without it (`[DSPY OFFLINE]`
  prints at import; epigenetic learning and the DSPy critic do not run).
- **Ollama runs on `127.0.0.1:11434`.** A green suite needs
  `nomic-embed-text:latest` (768d, used for memory) and `mistral-nemo:latest`.
  The engine's own default chat model is `gemma4:12b` (`BoneConfig.MODEL` in
  `engine/presets.py`), with `gemma4:e4b` as the DSPy critic. The judge and
  simulated-person models are listed in `TESTING.md`'s model notes.
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
- **Full test suite takes ~10 minutes** (9m35s on 2026-09-22). Long enough that it needs
  backgrounding rather than a foreground call with a short timeout.

## Gotchas and Patterns


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
- **A loose mock accepts a method the real object does not have.** Two of
  the overnight bugs survived because a test handed the code a
  `MagicMock()` or a flat state-shaped stand-in: `mind_memory.record_scar`
  and `forge.atp_pool` both resolved on the mock and crashed or defaulted in
  production. Spec mocks against the real class (`MagicMock(spec=...)`), or
  pass the real object.
- **Instrument the state, not the method.** Over thirty sites change ATP and
  several assign `atp_pool` directly, so wrapping `adjust_atp` would have
  missed the largest drain. The census hooks `__setattr__` on the dataclass
  and records the first caller outside the helpers.
- **Removing a `hasattr` guard can turn silence into an outage.** The
  cortex's `record_scar` call lost its guard at some point; the method never
  existed on that object, so a no-op became a crash that took MIND offline
  until a REM cycle. When retiring a guard, check the thing it guarded
  exists.
- **Mutation test anything that guards a contract.** Five deliberate
  breaks were put into `brain/composer.py` to check the A4 tests were load
  bearing. Four failed immediately; the fifth passed, because the test was
  asserting on a `mood_override` it had passed into the state dict when
  `compose()` takes it as an argument. The test described the contract
  without holding it, which is this document's own subject reproduced
  inside the test written to prevent it. Break the code on purpose before
  trusting a green test.
- **`exhaustion` is the USER's, not the engine's.** `engine/cycle.py` assigns
  `ctx.physics.exhaustion` from `ctx.user_state`. The engine's own
  depletion reaches the prompt through respiration
  (`raw_cost > BIO.ANAEROBIC_THRESHOLD` becomes a prose directive), which
  is a separate path across three modules. Both are real; the variable
  name tells you the wrong one. **Correction (2026-09-17):** "only through
  respiration" was wrong. `cortex.py:229` adds its own "under 3 sentences"
  style directive when ATP `p < 20` or the modulator's `max_tokens < 300`,
  so engine depletion reaches the prompt by two paths, and one of them uses
  the wording C5 found the model ignores. `ROADMAP.md` Track D lists all
  five somatic paths.
- **The thermal lock overwrites the modulator.** `LLMInterface.generate`
  replaces `temperature` and `top_p` whenever `<cd_lambda_1>` is in the
  prompt, which is nearly every turn. Confirmed with a spy: the modulator
  asked for 0.79 and 0.4, and 0.7 went out both times. Chemistry-driven
  sampling has not reached a model since B1. Track D4.
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
- **An instruction reaching the prompt proves nothing about compliance.**
  A4 pinned both somatic directives into the prompt; C5 found one weakly
  obeyed and the other not obeyed, and on one model reversed. For anything
  in the prompt that claims to change behaviour, measure the behaviour.
- **A reply with no visible prose scores as perfect obedience.** An
  all-`<think>` reply is zero sentences after the validator strips it, which
  a naive count reads as "3 sentences or less". Count empty outcomes on their
  own.
- **`generate` never fails loudly on empty content.** It returns mock prose.
  Anything measuring or relying on real model output should make
  `mock_generation` raise, as `audit_somatic.py` does.
- **A resume cache must key on everything that varies between runs.** The
  prompts are identical across models, so a key without the model name made
  the second model's run skip every generation and report success.
- **Collapsing several conditions into one return value throws away the
  diagnosis.** `_sync_ordvec_indices` returned a bare `False` for four
  unrelated problems and its only caller ignored it. Prefer a named
  exception per condition; the cost is one line and the payoff is a
  receipt that reads as a state rather than a stack trace.


- **`EventBus.log`'s signature is `(message, source, level)`.** Passing
  a level positionally as the second argument (`log(msg, "WARN")`) puts
  it in `source` and silently leaves `level="INFO"`, which routes to
  `logger.debug` and never surfaces. Most of the codebase passes a
  *source* tag there by convention (`"BIO"`, `"SYS"`, `"CRIT"`), so this
  is easy to get wrong. If a warning you added isn't appearing, this is
  why. Also: the bus renders the source tag itself, so don't put a
  literal `[TAG]` prefix in the message or it doubles up.
- **`engine/struts.py` cannot import from the `spores` package at module
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
  `engine/cycle.py` asked for and not what `HippocampalCache` has ever returned.
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
  governor runs in `engine/cycle.py` (was line 705), before `run_simulation`, which is why
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
  "Claims vs. code"). The same goes for this file: it describes what was
  true when it was written.
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
   and word resolution now makes them on novel words too. The poetic-names
   decision treats these costs as load-bearing, so arguably they should
   be. Left alone because it is a tuning decision, not a repair.
2. ~~**The metabolic economy kills the engine by turn six.**~~ **Repaired
   2026-09-17** (`ROADMAP.md` D0 repairs; ATP holds 16 to 53 across 30 live
   turns). What follows is the original finding. *Confirmed
   against live models on 2026-09-17 (D0); the earlier note here called it
   possibly a mock artifact, and it is not.* ATP: 6 to 10 spent per turn
   (token generation, Deep Structural Scan, validator stumbles, banned-phrase
   taxes), about zero earned, then the parity gate refuses every turn. ROS:
   the counterfactual gate adds its simulated ROS on each rejection, so it
   rejects forever once ROS is high. The ledger is in `ROADMAP.md` D0. Not
   retuned: that is a design decision. Also still open there: the HLA filter
   taxing all 160 style crimes by substring as if they were RLHF masks, and
   `gather_state` never reading the engine's real ATP into the prompt.
3. ~~**No `.gitignore`.**~~ **Done.** There is one now, kept in sync with
   `reset.sh` by a note in its own header; `tools/cache/` is in it.
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
   expect **633 passed, 0 failed, 5 skipped** (the skips are live-backend
   tests behind `BONE_EMBED_LIVE_TEST=1`). Then boot headless in mock
   mode, confirm `/status` reports the Arcade nominal rather than
   `DEGRADED`, and run `/diag` to see the turn's receipts.
7. **The exhaustion directive is not obeyed as written** (C5). Decided in
   `ROADMAP.md` D2: address the partner rather than the entity, state
   numbers rather than adjectives, forbid body narration, and move it out
   of the `[INTERNAL USE ONLY]` block. Each change is measured before it is
   adopted. The threshold is `e > 0.8`, hardcoded in `brain/composer.py`,
   not in `BoneConfig`.
8. ~~**Reasoning models on Ollama get mock prose.**~~ **Fixed 2026-09-17.**
   The stop list cut a thinking model's reasoning and emptied the reply. Now
   an empty reply is retried once without stops; if that fills it the model is
   flagged `stops_cut_reasoning` and stops are applied to the reply text. A
   reply still empty raises `EmptyReplyError`, logged at WARN and counted by
   the circuit breaker. Confirmed live on gemma4:12b with reasoning on.
   `tests/test_synapse_fallback.py`. What remains after the fix is not a bug in
   the engine: gemma4:12b with reasoning on sometimes reasons until it fills
   Ollama's default 4,096-token context and returns nothing
   (`finish_reason: "length"`): 13% of 149 audit generations, at 42 seconds each,
with no gain in compliance over reasoning off.
   `LLMInterface` has no way to send `reasoning_effort` yet; `ROADMAP.md` D7.
9. ~~**`mock_generation` and `hallucinate` recurse.**~~ **Fixed 2026-09-17.**
   `hallucinate(via_synapse=False)` from the fallback. Same test file.
10. ~~**The HLA tax always charged 50 ATP.**~~ **Fixed 2026-09-17.**
   `mitigate_rejection` read `atp_pool` off the `MitochondrialForge` with a
   default of 100.0. `tests/test_agents.py::test_hla_tax_reads_the_real_forge`.
11. **Scars now record. Review this.** Four sites called
   `mind.mem.record_scar`, which the MycelialNetwork has never had; three were
   `hasattr`-guarded no-ops, and the cortex's crashed the first counterfactual
   rejection of every live session and left MIND offline. All four now call
   `eng.akashic.record_scar`, which is where the method is. That switches on
   behaviour that has probably never run: `_mutate_system_prompts` appends
   `EPIGENETIC_SCARS` to `lore/system_prompts.json` via `lore.save`, a tracked
   file. No composer read of that key was found. `tests/test_scars.py`. If
   scars should not write lore, the fix is in `TheAkashicRecord`, not a
   return to the guards.

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
