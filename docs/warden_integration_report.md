# The Warden and the Gatekeeper

What `69caa5d` added, as the code does it. Revised 2026-09-25 (20.7.4.34):
an audit found the first version of this report claimed more than the code
did. Where the claim was worth keeping, the code was changed to match; where
it was not, the claim was cut. Both are listed at the end.

BoneAmanita is a prompt builder with a simulated state behind it (see the
README). The model's output is untrusted input to that state. These two
pieces check it before it gets in.

## The Warden: one JSON object per reply

`PromptComposer` ends every prompt with a `STRUCTURAL INVARIANT GOVERNANCE`
block: reply with exactly one JSON object and nothing else, using one of two
tools.

- `nominate_response`: `{"tool": "nominate_response", "args": {"internal_monologue": "...", "text": "..."}}`
- `commit_memory`: the same, plus `"evidence"`, an exact quote from the dialogue.

The cortex takes the object from a fenced block if there is one, otherwise
from the first `{` to the last `}`. If it does not parse, or has no `tool`
or `args`, the draft is rejected (`warden.json_gate` receipt and a log line)
and the model is asked again with the reason. Only `args.text` goes on to
the rest of the pipeline (lexical firewall, validator, style rules), so prose
outside the JSON never reaches the person.

On gemma4:12b, 6 of 30 CONVERSATION replies were rejected once for not being
JSON and all passed on the retry (2026-09-25 real-model run).

## The Gatekeeper: evidence-gated memory

`engine/invariants.py`. A `commit_memory` passes only if its `evidence` is an
exact quote from the dialogue buffer:

- case and words must match exactly; runs of whitespace are treated as one space;
- at least five words, so a stray word or a single letter cannot pass as a quote;
- the dialogue buffer holds both sides of the conversation, so the quote can
  come from the person or from an earlier reply.

A failed check is an `InvariantViolation`: the draft is rejected
(`gatekeeper.invariant` receipt) and the model is asked again.

What is stored is the verified quote itself, as the memory's text and
trigger words; the model's `internal_monologue` is never stored. The memory
layer keeps an engram only above its significance threshold (voltage
against `SPORES.CONSOLIDATION_THRESHOLD`); the log says whether it was kept.

This grounds what the Warden commits. It does not cover the engine's other
memory writes: the per-turn engram, dreams and REM consolidation work as they
always have.

## Retries and what happens when they run out

Every rejection (the Warden's, the Gatekeeper's, the validator's, the style
rules') costs an attempt: `CORTEX.COGNITIVE_RETRY_LIMIT` (2), lowered by the
somatic budget's allowance. When they run out, the person gets a short pause
line from `lore/ux_strings.json` (`cortex_pause`, for example "One thing at a
time."). That is a degraded turn, not a healed one. The first 2026-09-25
run showed it on ADVENTURE turns where the DSPy critic rejected every draft;
the critic is now off in ADVENTURE (`CORTEX.DSPY_CRITIC_DISABLED_MODES`).

## The turn snapshot

`CycleSimulator.run_simulation` snapshots health, stamina, trauma, the soul
and the mitochondrial state before the phases run, and restores them if the
phase run raises or ATP ends below zero. In practice it rarely fires: each
phase's own errors are caught by `PhaseExecutor` first, and ATP is clamped at
zero. The physics packet, memory, the village and the dialogue are not in the
snapshot.

## Response length

Not the Gatekeeper's job. Length is set by the somatic budget: a token
ceiling when the person's state calls for a word cap, and the validator's
sentence trim. An earlier budget check here read a context that does not
exist and never ran; it was removed rather than wired in, because a
rejection costs a retry and exhausted retries end in the fallback line.

## Audit, 2026-09-25

Made true in the code:
- "Exact, verbatim citations": the check was a case-insensitive substring,
  so any single letter from the dialogue passed. Now exact, five words
  minimum.
- "Evidence-gated memory": commits were never stored (the cortex looked for a
  memory handle it does not have), and would have stored the unverified
  monologue. Now the verified quote is stored.

Cut from this report:
- "Cryptographically bound": no cryptography is involved; it is an exact
  string match.
- "Mathematically guaranteed to never fall into an illegal state": the
  snapshot covers five fields and rarely fires (above).
- "Entirely eliminating hallucinated historical context": only Warden commits
  are gated.
- "Self-healing": exhausted retries end in a fallback line.
- The length check: removed (above), and the prompt no longer threatens it.
