# Archived Testing Reflections (September 2026)


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
