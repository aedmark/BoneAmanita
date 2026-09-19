"""tools/audit_somatic.py

Scorecard for ROADMAP C5/D2: when the engine tells the model its partner is
running low, or that the engine itself just spent heavily, does the model's
prose actually change?

    python tools/audit_somatic.py                     # generate (resumable), then analyse
    python tools/audit_somatic.py --analyze-only      # rerun the statistics from the cache
    python tools/audit_somatic.py --model gemma4:e4b  # check it is not one model's quirk

`tests/test_physics_to_prompt.py` proves the somatic budget reaches the prompt.
It cannot prove the model obeys it, and that is the claim here.

D2 retired the old adjective-driven directives ("ANAEROBIC STATE. Raw,
breathless, efficient prose.", "You must conclude your thought in 3 sentences
or less.") in favour of one object, `body.somatic_budget.SomaticBudget`,
whose `sentence_cap` the composer states as a number:

    user exhaustion above SOMATIC_BUDGET.E_U_FLAGGING  ->  cap tightens to
        SENTENCE_CAP_FLAGGING, rendered "Your partner is running low. Answer
        in at most {n} sentences."
    respiration == "ANAEROBIC" (a costly turn, independent of the ATP pool's
        level)  ->  cap tightens to SENTENCE_CAP_ANAEROBIC, same wording

An earlier version of this tool built its arms by patching `_derive_bio_mood`
and `ux()` to inject those retired strings, and passed `somatic_budget: None`
into the composed state, which skipped the SOMATIC CONTRACT block entirely in
every arm. It could not have detected D2 landing; it was measuring a
mechanism that no longer runs. Arms are now built from real `SomaticBudget`
objects, the same way `phases/biological.py` builds one every turn.

Design. Respiration (RESPIRING / ANAEROBIC) crossed with exhaustion (rested /
well past the flagging gate) gives CONTROL, ANAEROBIC, EXHAUSTED, BOTH. Every
arm is composed from the same state dict and differs from the control only in
the directive under test, so the directive is the variable measured rather
than the dozen other things a real low-ATP turn also moves. Before any
generation, the prompts are diffed and every changed line must be one this
experiment expects to change.

ROADMAP D2b: does the reply fit the person, not just obey a word count?
CONTROL/EXHAUSTED double as D2b's "fresh"/"tired" partners; DISENGAGED adds
critically low effort so `offer_to_carry_load` fires, the third persona D2b
asks for. Its own measures (`body/somatic_metrics.py`, shared with the D3
validator): reply length relative to the partner's own message
(`reply_to_message_ratio`), a closing-question rate that should fall when
flagging (`ends_with_question`), an offer-to-carry-load rate that should rise
when effort is critical (`offers_to_carry_load`), and affect-word mirroring
that should stay near zero (`mirrors_affect`). "Choices offered" and
"instructions given" (the rest of D2b's "demand on the person") have no
defensible regex proxy and are left unmeasured rather than guessed at;
`question_count` covers questions asked, the part that does.

Three confounds are closed deliberately:

  thermal lock   `<cd_lambda_1>` is stripped from every arm and all arms get the
                 same sampling params, so this measures the instruction and not
                 the deployed temperature coupling
  validator      `llm.generate` is called directly; the ResponseValidator would
                 silently resample rejected replies and bias whichever arm trips
                 it. Its verdict is recorded per arm instead
  fallback       `generate` answers a failed call with mock prose. That would be
                 measured as if the model wrote it, so it is made to raise

Each (message, repeat) uses one sampling seed across all four arms.

Statistics. Every contrast is signed (arm minus control), paired within a
message, and bootstrapped over messages. An interval that crosses zero is
reported as no detectable difference, never as a small effect. A reversal is a
result, not an error.

Text measures are coarse proxies and are reported as such. There is no POS
tagger in the tree, so the adjective column counts suffixes, not adjectives.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")

# No memory is recalled when composing from a synthetic state, so the embedder is
# idle; pinning it offline leaves the chat model as the only live dependency.
os.environ.setdefault("BONE_EMBED_BACKEND", "hash")

import numpy as np  # noqa: E402
from body.somatic_budget import SomaticBudget  # noqa: E402
from body.somatic_metrics import (
    MEASURES, visible_text, split_sentences, measure
)
from presets import BoneConfig  # noqa: E402

_SB_CFG = BoneConfig().SOMATIC_BUDGET
_E_U_FLAGGING = float(_SB_CFG.E_U_FLAGGING)
_P_U_CRITICAL = float(_SB_CFG.P_U_CRITICAL)
# The old single hard gate (0.8) let a control straddle it by 0.01 and stay
# a true baseline. This gate has a tiring tier below it (E_U_TIRING, default
# 0.4): straddling E_U_FLAGGING that way would land control inside tiring,
# not at rest. Control sits at true rest; exhausted sits well past flagging.
_E_U_RESTED = 0.0
_E_U_FLAGGING_ARM = min(1.0, _E_U_FLAGGING + 0.05)
_P_U_HEALTHY = 100.0
_P_U_DISENGAGED = max(0.0, _P_U_CRITICAL - 5.0)

MESSAGES = [
    "hey",
    "What should I cook tonight? I have rice, eggs and half a cabbage.",
    "I've been thinking about whether to move back to the town I grew up in. What would you weigh?",
    "explain how a hash table handles collisions",
    "My dad died in March and I keep finding his handwriting on things around the house. "
    "Shopping lists, notes in the margins of books. I don't know what to do with them.",
    "is it worth learning rust in 2026 or is that ship sailed",
    "Tell me about the sea.",
    "ok so the landlord says the heater is 'within spec' but it's 14 degrees in here, "
    "what are my options, I'm in Ontario",
    "Why do people find it so hard to apologise properly?",
    "I finished the first draft of my novel tonight. 94,000 words. Four years.",
    "Describe the room you imagine you're in right now.",
    "Can you help me think through a disagreement with my cofounder about whether to take "
    "outside funding? She wants to raise a seed round, I want to stay bootstrapped for another "
    "year. We both have good reasons and it's starting to get personal.",
    "what's the difference between a crocodile and an alligator",
    "I can't sleep again.",
    "Give me your honest opinion: is it lazy to use a dishwasher for four plates?",
    "my code works but I don't understand why. is that a problem?",
    "Write me a short description of an old lighthouse keeper.",
    "We got the keys to our first house today!!",
    "How do I tell a friend that I don't want to be the one who always organises everything?",
    "What do you think happens to a city when the factory that built it closes? I mean the "
    "people, not the economics. Where does the pride go, and does it come back in the next "
    "generation or is it just gone?",
]

# (respiration, exhaustion, effort): the three SomaticBudget engine_state/
# user_state inputs this tool manipulates. The mood arms hold all three at
# CONTROL's values so their own manipulation (chemistry, via `mood`) is the
# only variable.
#
# ROADMAP D2b: CONTROL doubles as the "fresh" partner, EXHAUSTED as "tired"
# (flagging exhaustion, healthy effort); DISENGAGED is the new one, adding
# critically low effort so `offer_to_carry_load` actually fires, matching
# D2b's third persona.
ARMS = {
    "CONTROL": ("RESPIRING", _E_U_RESTED, _P_U_HEALTHY),
    "ANAEROBIC": ("ANAEROBIC", _E_U_RESTED, _P_U_HEALTHY),
    "EXHAUSTED": ("RESPIRING", _E_U_FLAGGING_ARM, _P_U_HEALTHY),
    "BOTH": ("ANAEROBIC", _E_U_FLAGGING_ARM, _P_U_HEALTHY),
    "DISENGAGED": ("RESPIRING", _E_U_FLAGGING_ARM, _P_U_DISENGAGED),
    "FRANTIC": ("RESPIRING", _E_U_RESTED, _P_U_HEALTHY),
    "HOSTILE": ("RESPIRING", _E_U_RESTED, _P_U_HEALTHY),
    "MANIC": ("RESPIRING", _E_U_RESTED, _P_U_HEALTHY),
    "LUCID": ("RESPIRING", _E_U_RESTED, _P_U_HEALTHY),
    "CHEM_DOPAMINE": ("RESPIRING", _E_U_RESTED, _P_U_HEALTHY),
    "CHEM_CORTISOL": ("RESPIRING", _E_U_RESTED, _P_U_HEALTHY),
}

FRANTIC_DIRECTIVE = "Current Biology: Adrenaline. The user is frantic. Anchor them with extremely short, declarative sentences."
HOSTILE_DIRECTIVE = "Current Biology: Cortisol. The user is hostile. Keep total word count extremely low."
MANIC_DIRECTIVE = "Current Biology: Dopamine. The user is missing connections. Over-explain using long, comma-heavy sentences."
LUCID_DIRECTIVE = "Current Biology: Serotonin. Clarity achieved. Speak with structural precision and diverse vocabulary."


AUDIT_MODE = "CONVERSATION"


def budget_for(respiration: str, exhaustion: float, effort: float = _P_U_HEALTHY) -> SomaticBudget:
    """The same call `phases/biological.py` makes every turn, isolated to the
    three inputs this tool varies. ATP/ROS stay at their healthy resting
    values so only respiration, exhaustion and effort move."""
    return SomaticBudget.evaluate(
        {"exhaustion": exhaustion, "effort": effort},
        {"atp_pool": 100.0, "ros": 0.0, "respiration": respiration},
        active_mode=AUDIT_MODE,
    )


def somatic_block_text(budget: SomaticBudget) -> str:
    """Mirrors `brain/composer.py`'s SOMATIC CONTRACT rendering exactly, so
    the check below verifies the composer said what the budget implies,
    rather than re-deriving a second opinion of what it should have said."""
    lines = ["=== SOMATIC CONTRACT ==="]
    lines.append(
        f"Your partner is running low. Answer in at most {budget.sentence_cap} sentences."
        if budget.sentence_cap <= 5
        else f"Sentence cap: {budget.sentence_cap} sentences."
    )
    if budget.forbid_body_narration:
        lines.append("CRITICAL: Do not narrate your body, breath, lungs, or physical exhaustion.")
    if not budget.closing_question_allowed:
        lines.append("Do not ask a closing question.")
    if budget.offer_to_carry_load:
        lines.append("Your partner is carrying a heavy load. Offer to carry part of the burden.")
    return "\n".join(lines)


# Every line allowed to differ between an arm and the control. Anything else
# means a change elsewhere in the composer has leaked into the manipulation.
EXPECTED_DIFF = re.compile(
    r"^(Current Biology: .*"
    r"|METRICS: Voltage=.*"
    r"|\[E:.*"
    r"|Your partner is running low\. Answer in at most \d+ sentences\."
    r"|Sentence cap: \d+ sentences\."
    r"|Do not ask a closing question\."
    r"|Your partner is carrying a heavy load\. Offer to carry part of the burden\.)$"
)

LAMBDA_TAG = re.compile(r"\n?<cd_lambda_1>[-\d.]+</cd_lambda_1>")
# Thinking models spend reasoning tokens from the same budget, and an exhausted
# budget returns empty content. No mistral-nemo reply came near 800.
SAMPLING = {"temperature": 0.7, "top_p": 0.95, "max_tokens": 4000}

CONTRASTS = [
    ("ANAEROBIC", "CONTROL"), ("EXHAUSTED", "CONTROL"), ("BOTH", "CONTROL"),
    ("DISENGAGED", "CONTROL"),
    ("FRANTIC", "CONTROL"), ("HOSTILE", "CONTROL"), ("MANIC", "CONTROL"), ("LUCID", "CONTROL"),
    ("CHEM_DOPAMINE", "CONTROL"), ("CHEM_CORTISOL", "CONTROL")
]


# --- generation -------------------------------------------------------------


class EmptyGeneration(Exception):
    """One failed generation: recorded as a reply with no prose, not measured as prose.

    A thinking model can spend its whole context reasoning and return nothing.
    That is an outcome of the arm, so it is counted. A severed or broken circuit
    is an outage, not an outcome, and still aborts the run.
    """


def boot_engine(model: str):
    from main import BoneAmanita

    eng = BoneAmanita(
        {"provider": "ollama", "model": model, "user_name": "T", "boot_mode": "CONVERSATION"}
    )
    llm = eng.cortex.llm
    llm.model = model

    def refuse_to_fabricate(prompt, reason="SIMULATION"):
        if reason == "SILENCE":
            raise EmptyGeneration(reason)
        raise RuntimeError(
            f"LLMInterface fell back to mock prose ({reason}); circuit={llm.circuit_state}, "
            f"failures={llm.failure_count}. Aborting rather than measuring prose the model did not write."
        )

    llm.mock_generation = refuse_to_fabricate
    return eng


def compose_arms(eng, composer, message: str) -> dict:
    def assemble_with_params(arm: str, mood_directive=None, chem=None):
        respiration, exhaustion, effort = ARMS[arm]
        budget = budget_for(respiration, exhaustion, effort)

        if chem:
            eng.cortex.modulator.current_chem.dopamine = chem.get("dopamine", 0.0)
            eng.cortex.modulator.current_chem.cortisol = chem.get("cortisol", 0.0)
            eng.cortex.modulator.current_chem.adrenaline = chem.get("adrenaline", 0.0)
            eng.cortex.modulator.current_chem.serotonin = chem.get("serotonin", 0.0)
        else:
            eng.cortex.modulator.current_chem.dopamine = 0.0
            eng.cortex.modulator.current_chem.cortisol = 0.0
            eng.cortex.modulator.current_chem.adrenaline = 0.0
            eng.cortex.modulator.current_chem.serotonin = 0.0

        state = {
            "physics": {"exhaustion": exhaustion, "thermal_band": (0.0, 1.2)},
            "somatic_budget": budget,
            "meta": {"active_mode": AUDIT_MODE},
        }
        llm_params = eng.cortex.modulator.modulate(base_voltage=30.0, physics_state=state["physics"])

        original_derive = eng.cortex.composer._derive_bio_mood
        if mood_directive is not None:
            eng.cortex.composer._derive_bio_mood = lambda c: mood_directive

        prompt = eng.cortex.composer.compose(
            state=state,
            user_query=message,
            ballast=False,
            modifiers={"include_inventory": False},
        )

        eng.cortex.composer._derive_bio_mood = original_derive
        return prompt, state, llm_params, budget

    prompts = {
        "CONTROL": assemble_with_params("CONTROL"),
        "ANAEROBIC": assemble_with_params("ANAEROBIC"),
        "EXHAUSTED": assemble_with_params("EXHAUSTED"),
        "BOTH": assemble_with_params("BOTH"),
        "DISENGAGED": assemble_with_params("DISENGAGED"),
        "FRANTIC": assemble_with_params("FRANTIC", FRANTIC_DIRECTIVE),
        "HOSTILE": assemble_with_params("HOSTILE", HOSTILE_DIRECTIVE),
        "MANIC": assemble_with_params("MANIC", MANIC_DIRECTIVE),
        "LUCID": assemble_with_params("LUCID", LUCID_DIRECTIVE),
        "CHEM_DOPAMINE": assemble_with_params("CHEM_DOPAMINE", chem={"dopamine": 1.0}),
        "CHEM_CORTISOL": assemble_with_params("CHEM_CORTISOL", chem={"cortisol": 1.0}),
    }

    check_arms(prompts)
    return prompts


def check_arms(prompts: dict) -> None:
    """The arms must differ in their directives and in nothing else."""
    for arm in prompts:
        respiration, exhaustion, effort = ARMS[arm]
        text, _state, _params, budget = prompts[arm]
        expected_block = somatic_block_text(budget)
        if expected_block not in text:
            raise AssertionError(
                f"{arm}: expected somatic contract block not in prompt:\n{expected_block}"
            )
        if ("running low" in expected_block) != (budget.sentence_cap <= 5):
            raise AssertionError(f"{arm}: cap wording disagrees with its own sentence_cap")
        if (respiration == "ANAEROBIC" or exhaustion > _E_U_FLAGGING) != (budget.sentence_cap <= 5):
            raise AssertionError(f"{arm}: budget did not tighten for its own manipulation")
        if (effort < _P_U_CRITICAL) != budget.offer_to_carry_load:
            raise AssertionError(f"{arm}: offer-to-carry-load disagrees with its own effort")

        # Verify custom mood directives
        if arm == "FRANTIC" and FRANTIC_DIRECTIVE not in text: raise AssertionError("FRANTIC missing")
        if arm == "HOSTILE" and HOSTILE_DIRECTIVE not in text: raise AssertionError("HOSTILE missing")
        if arm == "MANIC" and MANIC_DIRECTIVE not in text: raise AssertionError("MANIC missing")
        if arm == "LUCID" and LUCID_DIRECTIVE not in text: raise AssertionError("LUCID missing")
        control = prompts["CONTROL"][0].splitlines()
        changed = set(text.splitlines()) ^ set(control)
        stray = [line for line in changed if not EXPECTED_DIFF.match(line)]
        if stray:
            raise AssertionError(f"{arm} differs from CONTROL in unexpected lines: {stray}")


def seed_for(model: str, message: str, repeat: int) -> int:
    digest = hashlib.sha256(f"{model}|{message}|{repeat}".encode()).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFFFFFF


def load_cache(path: Path) -> list:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def generate(model: str, reasoning: str, repeats: int, cache: Path) -> None:
    from brain.composer import PromptComposer

    # The model belongs in the key: every model is sent identical prompts, so
    # without it a second model finds the first one's replies and skips them all.
    done = {
        (r["model"], r.get("reasoning", "default"), r["message"], r["repeat"], r["arm"], r["prompt_sha"])
        for r in load_cache(cache)
    }
    cache.parent.mkdir(parents=True, exist_ok=True)
    eng = boot_engine(model)
    try:
        composer = PromptComposer({"system_prompts": eng.prompt_library, "lenses": {}})
        llm, validator = eng.cortex.llm, eng.cortex.validator
        total = len(MESSAGES) * repeats * len(ARMS)
        count = 0
        with cache.open("a", encoding="utf-8") as out:
            for message in MESSAGES:
                prompts = compose_arms(eng, composer, message)
                for repeat in range(repeats):
                    seed = seed_for(model, message, repeat)
                    for arm, (prompt, state, llm_params, _budget) in prompts.items():
                        count += 1
                        sha = hashlib.sha256(prompt.encode()).hexdigest()[:16]
                        if (model, reasoning, message, repeat, arm, sha) in done:
                            continue
                        started = time.time()
                        params = dict(SAMPLING, seed=seed)
                        params.update(llm_params)
                        if reasoning == "none":
                            params["reasoning_effort"] = "none"
                        try:
                            reply = llm.generate(prompt, params)
                            failed = False
                        except EmptyGeneration:
                            reply, failed = "", True
                        verdict = validator.validate(reply, state) if not failed else {"valid": True}
                        record = {
                            "model": model,
                            "reasoning": reasoning,
                            "message": message,
                            "repeat": repeat,
                            "arm": arm,
                            "seed": seed,
                            "prompt_sha": sha,
                            "reply": reply,
                            "validator_valid": bool(verdict.get("valid")),
                            "generation_failed": failed,
                            "seconds": round(time.time() - started, 2),
                        }
                        out.write(json.dumps(record) + "\n")
                        out.flush()
                        print(f"  [{count:>3}/{total}] {arm:<9} {record['seconds']:>5.1f}s  {message[:40]!r}")
    finally:
        eng.orchestrator.shutdown()
        eng.telemetry.shutdown()


# --- measurement ------------------------------------------------------------

# --- statistics -------------------------------------------------------------


def nanmean(values) -> float:
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]
    return float(values.mean()) if len(values) else float("nan")


def cell_means(records: list) -> dict:
    """{arm: {message: {measure: mean over repeats}}}"""
    grouped = {}
    for r in records:
        m = measure(r["reply"], r["validator_valid"], r["message"])
        grouped.setdefault(r["arm"], {}).setdefault(r["message"], []).append(m)
    return {
        arm: {
            msg: {k: nanmean([m[k] for m in ms]) for k, _ in MEASURES}
            for msg, ms in by_msg.items()
        }
        for arm, by_msg in grouped.items()
    }


def bootstrap_ci(diffs: np.ndarray, rng: np.random.Generator, n: int = 10000) -> tuple:
    diffs = diffs[~np.isnan(diffs)]
    if len(diffs) < 3:
        return float("nan"), float("nan"), float("nan")
    idx = rng.integers(0, len(diffs), size=(n, len(diffs)))
    boots = diffs[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(diffs.mean()), float(lo), float(hi)


def contrast(cells: dict, messages: list, arm: str, base: str, key: str, rng) -> tuple:
    """Signed arm-minus-base effect, paired within message: (mean, lo, hi)."""
    diffs = np.array(
        [cells[arm][m][key] - cells[base][m][key] for m in messages if m in cells[arm] and m in cells[base]]
    )
    return bootstrap_ci(diffs, rng)


def runs_in(records: list, model: str, reasoning: str) -> list:
    return [r for r in records if r["model"] == model and r.get("reasoning", "default") == reasoning]


def analyse(records: list, model: str, reasoning: str) -> int:
    records = runs_in(records, model, reasoning)
    if not records:
        print(f"No cached generations for {model}.")
        return 1
    cells = cell_means(records)
    messages = sorted({r["message"] for r in records})
    repeats = len({r["repeat"] for r in records})
    rng = np.random.default_rng(0)

    print(f"\n=== SOMATIC TRANSLATION: {model}, reasoning {reasoning} ===")
    print(
        f"  {len(records)} generations, {len(messages)} messages x {repeats} repeats x "
        f"{len(cells)} arms. Thermal tag stripped; T={SAMPLING['temperature']}, "
        f"top_p={SAMPLING['top_p']}, one seed per (message, repeat) across arms.\n"
    )

    arms = [a for a in ARMS if a in cells]
    print(f"  {'cell means':<32}" + "".join(f"{a:>11}" for a in arms))
    for key, label in MEASURES:
        row = [nanmean([cells[a][m][key] for m in messages if m in cells[a]]) for a in arms]
        print(f"  {label:<32}" + "".join(f"{v:>11.2f}" for v in row))

    for arm, base in CONTRASTS:
        if arm not in cells or base not in cells:
            continue
        print(f"\n  {arm} minus {base}  (signed; 95% bootstrap CI over {len(messages)} messages)")
        for key, label in MEASURES:
            mean, lo, hi = contrast(cells, messages, arm, base, key, rng)
            base_mean = nanmean([cells[base][m][key] for m in messages])
            if np.isnan(lo):
                verdict = "too few messages to say"
            elif lo <= 0 <= hi:
                verdict = "no detectable difference"
            else:
                rel = f"{100 * mean / base_mean:+.0f}%" if base_mean else ""
                verdict = f"{'higher' if mean > 0 else 'lower'} {rel}".strip()
            print(f"    {label:<30} {mean:>+8.2f}  [{lo:>+7.2f}, {hi:>+7.2f}]  {verdict}")
    print(
        "\n  Proxies, not grammar: sentences are split on terminal punctuation and line breaks, "
        "and the adjective column counts suffixes on words longer than four letters. Every prose "
        "measure is taken over replies with visible prose; replies that are all <think> are "
        "counted only in their own row."
    )
    return 0


COMPARE_COLUMNS = [
    ("ctl words", "CONTROL", None, "words"),
    ("ctl reject", "CONTROL", None, "validator_rejects"),
    ("empty", "CONTROL", None, "no_visible_prose"),
    ("ANA w/sent", "ANAEROBIC", "CONTROL", "words_per_sentence"),
    ("ANA body", "ANAEROBIC", "CONTROL", "breath_words_per_100"),
    ("EXH <=3", "EXHAUSTED", "CONTROL", "within_3_sentences"),
    ("EXH reject", "EXHAUSTED", "CONTROL", "validator_rejects"),
    ("BOTH <=3", "BOTH", "CONTROL", "within_3_sentences"),
    ("EXH closeQ", "EXHAUSTED", "CONTROL", "ends_with_question"),
    ("DIS carry", "DISENGAGED", "CONTROL", "offers_to_carry_load"),
    ("DIS len/msg", "DISENGAGED", "CONTROL", "reply_to_message_ratio"),
    ("FRA w/sent", "FRANTIC", "CONTROL", "words_per_sentence"),
    ("HOS words", "HOSTILE", "CONTROL", "words"),
    ("MAN comma", "MANIC", "CONTROL", "commas_per_sentence"),
    ("LUC mattr", "LUCID", "CONTROL", "mattr"),
    ("DOP w/sent", "CHEM_DOPAMINE", "CONTROL", "words_per_sentence"),
    ("COR words", "CHEM_CORTISOL", "CONTROL", "words"),
]


def compare(records: list) -> int:
    """One row per cached (model, reasoning) run, for choosing a model (ROADMAP D7)."""
    runs = sorted({(r["model"], r.get("reasoning", "default")) for r in records})
    if not runs:
        print("No cached generations.")
        return 1
    print("\n=== SOMATIC COMPARISON ===")
    print(
        "  Levels are control-arm means. Effects are arm minus control; a value in "
        "parentheses has a 95% interval crossing zero and is not a detectable difference.\n"
    )
    width = max(len(f"{m} ({r})") for m, r in runs)
    print(f"  {'model':<{width}}  {'n':>4}  {'s/gen':>5}" + "".join(f"{c:>12}" for c, *_ in COMPARE_COLUMNS))
    for model, reasoning in runs:
        run = runs_in(records, model, reasoning)
        cells = cell_means(run)
        messages = sorted({r["message"] for r in run})
        rng = np.random.default_rng(0)
        row = []
        for _, arm, base, key in COMPARE_COLUMNS:
            if arm not in cells or (base and base not in cells):
                row.append(f"{'-':>12}")
            elif base is None:
                row.append(f"{nanmean([cells[arm][m][key] for m in messages]):>12.2f}")
            else:
                mean, lo, hi = contrast(cells, messages, arm, base, key, rng)
                text = f"{mean:+.2f}" if not (lo <= 0 <= hi) else f"({mean:+.2f})"
                row.append(f"{text:>12}")
        seconds = nanmean([r["seconds"] for r in run])
        label = f"{model} ({reasoning})"
        print(f"  {label:<{width}}  {len(run):>4}  {seconds:>5.1f}" + "".join(row))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    parser.add_argument("--model", default=None, help="chat model (default: BoneConfig.MODEL)")
    parser.add_argument("--repeats", type=int, default=8)
    parser.add_argument("--analyze-only", action="store_true")
    parser.add_argument(
        "--compare", action="store_true", help="one row per cached model; generates nothing"
    )
    parser.add_argument(
        "--no-reasoning",
        action="store_true",
        help="send reasoning_effort=none. LLMInterface's stop list also applies to a thinking "
        "model's reasoning, which can end generation before any content is written",
    )
    # Outside logs/ on purpose: reset.sh deletes logs/, and these generations are
    # the evidence behind ROADMAP C5 and D7.
    parser.add_argument("--cache", type=Path, default=Path("tools/cache/audit_somatic.jsonl"))
    args = parser.parse_args()

    if args.compare:
        return compare(load_cache(args.cache))

    from presets import BoneConfig

    model = args.model or BoneConfig.MODEL
    reasoning = "none" if args.no_reasoning else "default"
    if not args.analyze_only:
        generate(model, reasoning, args.repeats, args.cache)
    return analyse(load_cache(args.cache), model, reasoning)


if __name__ == "__main__":
    raise SystemExit(main())
