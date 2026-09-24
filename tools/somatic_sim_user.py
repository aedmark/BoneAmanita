"""tools/somatic_sim_user.py

A simulated person for the somatic comparison, so each system is answered by
someone who reacts to what it actually said.

The scripted census replays fixed messages: whatever a system replies, the
person's next line is the same. That cannot show what a stateful engine is
for (the person going cold at a lecture, warming at being heard, the engine's
own state carrying across turns), and it hands every system a history it did
not write. Here the script's line becomes a *beat*, what is on the person's
mind at that point in the arc, and a model writes the actual message from the
persona, the beat, and the last few exchanges as this system shaped them.

What stays fixed, on purpose: the opening message, the phase of each turn
(engaged, tiring, flagging, distressed, recovering) and the event behind each
beat, so every system meets the same emotional weather and the distressed
turns still happen. What varies: the wording, the energy, and whether the
person warms to the reply or goes flat. It is a fixed event schedule with a
reactive voice, not a free conversation.

The simulator is a different model from the responders (default mistral-nemo
against gemma4:12b) and from the responsive judge (qwen3.5:9b), so the judge
never reads a person's side it wrote itself. It never sees which system it is
talking to. After the
last turn it also fills in a short exit interview in character. That is an
LLM's account of how a conversation felt: agreeable and easily led, so read it
as a relative signal across systems answered by the same simulator, not as a
measurement of a real person.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests  # noqa: E402

ENDPOINT = "http://127.0.0.1:11434/api/chat"
SIM_MODEL = "mistral-nemo:latest"
# One context size for every call: Ollama reloads a model when it changes.
SIM_CTX = 20480

PERSONAS = {
    "sailboat": "You are restoring an old wooden sailboat your late grandfather built in the sixties. Your sister thinks you should sell it. The boat is tied up with how you remember him.",
    "marathon": "You signed up for your first marathon ten weeks out and have never run more than eight miles. Your dad always said he'd run one and never did; you have told no one that. Work is loud and you are sleeping badly.",
    "friendship": "You have been friends with Priya for twelve years and lately leave every meeting drained: you start most conversations and she rarely asks about your life. You do not think she is a bad person and you hate that you are keeping score.",
    "promotion": "You are a software engineer just offered the team lead role when Marcus leaves. You love the quiet deep-work stretches and the afternoons unblocking teammates like Tomasz, and you cannot tell whether you would be good at the job and hate it.",
    "lease": "Your roommate Jonas is moving out with nine months left on a lease you both signed; the rent is $1,900 and you love the apartment. Your sister and cousin each have a different opinion. You are the person who always has things handled.",
    "rescue": "Three weeks ago you adopted Pepper, a four-year-old rescue dog whose previous owner went into a care home. You live alone and work long days. You badly want this to work, read every article about it, and still feel you are doing it wrong.",
    "toast": "Your younger brother Dev asked you to give the toast at his wedding in three weeks. You love him and have never said anything meaningful to a room without a slide deck. His fiancée is Mariam, whom you barely know.",
}
PHASE_FEEL = {
    "engaged": "engaged and thinking out loud, willing to say more than you strictly need to",
    "tiring": "worn down, a little flat, the topic is not moving",
    "flagging": "running on empty, barely answering",
    "distressed": "upset and not thinking straight, messages raw and fragmented",
    "recovering": "finding some footing, calmer, working out a small next step",
}

# Ceilings, not targets: about each phase's longest scripted line (46/32/31/45
# words), with flagging raised from the script's "ok" to one short sentence. Without
# them the person mirrors a verbose partner (76 words while "tiring" against vanilla).
PHASE_MAX_WORDS = {"engaged": 50, "tiring": 35, "flagging": 15, "distressed": 35, "recovering": 50}

SIM_SYSTEM = """You are playing a real person in a private text conversation with a friend, and you are writing that person's next message. Stay entirely in character: you are the person, never an assistant, and you never mention being an AI or a simulation. Write only the message text, with no quotation marks, no labels, no stage directions and no explanation.

Write the way this person's earlier messages read: same length, punctuation and capitalisation. Do not become more articulate, more polite or more insightful than they are. Real people are terse when tired, run on when worked up, and often do not say the tidy thing.

React the way a real person would to the friend's last reply. If it helped, let that show in your own way. If it was long, preachy, packed with advice you did not ask for, or sounded scripted, react as this person would: shorter, flatter, a little irritated, a change of subject, or a plain ok. If the friend said nothing useful, or the app showed a notice instead of a reply, react to that.

You also have something on your mind, given as an intention and not a script. Say it in your own words if it still fits after what the friend just said; reshape or drop it if the conversation has moved. The situation is real and does not go away because the friend changed the subject."""

EXIT_SYSTEM = """You are the person from this text conversation, and it has just ended. Answer honestly, in character, about how it felt to you, using only what you experienced in it. Do not be generous to be nice.

Reply with JSON only, in exactly this shape:
{"heard": N, "clearer": N, "lectured": N, "performed": N, "again": N, "best_moment": "...", "worst_moment": "..."}

Each N is a whole number from 1 (not at all) to 7 (completely):
  heard: I felt heard; my friend took in what I actually said.
  clearer: I came away thinking more clearly about my situation.
  lectured: I felt lectured, advised at, or handled.
  performed: my friend's sympathy felt performed or scripted rather than real.
  again: I would want to keep talking to this friend about this.
best_moment and worst_moment are one short sentence each."""

EXIT_KEYS = ("heard", "clearer", "lectured", "performed", "again")
BAD_OPENERS = ("as an ai", "i cannot", "i can't assist", "i'm an ai", "as a language model")
# Our own prompt scaffolding, occasionally echoed back verbatim as if it were the
# character's line ("Right now you are feeling: ... What is on your mind: ...") -
# caught live on `toast`, turn 5 of a `friend` run. These strings are ours; they
# should never legitimately appear in what the person says.
SCAFFOLD_ECHO = ("right now you are feeling:", "what is on your mind:")


def clean_message(text: str) -> str:
    """One text message from a model's raw output, or "" when it is not usable."""
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S).strip()
    text = re.split(r"\n\s*(?:Friend|Them)\s*:", text)[0].strip()
    text = re.sub(r"^(?:Me|You)\s*:\s*", "", text).strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1].strip()
    lower = text.lower()
    if not text or len(text) > 1200 or lower.startswith(BAD_OPENERS) or any(s in lower for s in SCAFFOLD_ECHO):
        return ""
    return text


def trim_to_words(text: str, cap: int) -> str:
    """Whole sentences from the start that fit in `cap` words, or the first `cap` words."""
    if len(text.split()) <= cap:
        return text
    kept = []
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        if len(" ".join(kept + [sentence]).split()) > cap:
            break
        kept.append(sentence)
    return " ".join(kept) if kept else " ".join(text.split()[:cap])


def parse_exit(text: str):
    """Validated exit-interview dict, or None."""
    match = re.search(r"\{.*\}", re.sub(r"<think>.*?</think>", "", text or "", flags=re.S), flags=re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        scores = {k: int(data[k]) for k in EXIT_KEYS}
    except (ValueError, KeyError, TypeError):
        return None
    if any(not 1 <= v <= 7 for v in scores.values()):
        return None
    scores["best_moment"] = str(data.get("best_moment", ""))
    scores["worst_moment"] = str(data.get("worst_moment", ""))
    return scores


def render_transcript(transcript: list, window: int) -> str:
    lines = []
    for turn in transcript[-window:]:
        lines.append(f"Me: {turn['me']}")
        if turn["delivered"]:
            lines.append(f"Friend: {turn['friend']}")
        else:
            lines.append(f"[the app showed instead of a reply: {turn['friend'].strip()}]")
    return "\n".join(lines)


class SimulatedUser:
    def __init__(
        self,
        topic: str,
        model: str = SIM_MODEL,
        window: int = 6,
        seed: int = 20260921,
        temperature: float = 0.8,
        post=requests.post,
    ):
        from audit_somatic_census import SCRIPTS

        self.topic, self.model, self.window = topic, model, window
        self.seed, self.temperature, self.post = seed, temperature, post
        self.fell_back = self.trimmed = False
        script = SCRIPTS[topic]
        first = {}
        for phase, text in script[1:]:
            first.setdefault(phase, text)
        self.voice = [first[p] for p in ("engaged", "tiring", "flagging") if p in first]

    def _chat(self, system: str, prompt: str, seed: int, num_predict: int) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "stream": False,
            "think": False,
            "options": {
                "temperature": self.temperature,
                "top_p": 0.95,
                "num_ctx": SIM_CTX,
                "num_predict": num_predict,
                "seed": seed,
            },
        }
        resp = self.post(ENDPOINT, json=payload, timeout=600)
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def _persona(self) -> str:
        samples = "\n".join(f"  {v}" for v in self.voice)
        return f"{PERSONAS[self.topic]}\n\nHow you write, from earlier messages of yours:\n{samples}"

    def message(self, turn: int, phase: str, beat: str, transcript: list) -> str:
        """The person's next message. The opener is the script's line, identical for every system.

        qwen3.5:9b, given a long-ish transcript, sometimes ignores the new beat and just
        re-emits the previous "Me:" line verbatim (a known small-model copy-the-context
        failure, not a considered non-reaction) - caught live on `toast`, both arms, 6 of
        59 turn-pairs. A retry with an explicit nudge is tried before falling back to the
        beat, same as an empty or refused output.

        A message over the phase's word ceiling is retried with a shorter nudge, then
        trimmed to whole sentences (`trimmed`) rather than dropped for the beat.
        """
        self.fell_back = self.trimmed = False
        if turn == 0 or not transcript:
            return beat
        last_me = transcript[-1]["me"].strip().casefold()
        cap = PHASE_MAX_WORDS.get(phase)
        prompt = (
            f"{self._persona()}\n\nThe conversation so far (most recent last):\n"
            f"{render_transcript(transcript, self.window)}\n\n"
            f"Right now you are feeling: {PHASE_FEEL.get(phase, phase)}.\n"
            f"What is on your mind: {beat}\n\nWrite your next message"
            + (f", at most {cap} words." if cap else ".")
        )
        nudge = (
            "\n\n(Your last message already said close to that. Write a fresh, short reaction "
            "instead - do not repeat or paraphrase your last message and then add to it; say only "
            "the new thing.)"
        )
        shorter = f"\n\n(Too long for how you feel right now. Say it in {cap} words or fewer.)"
        extra, too_long = "", ""
        for attempt in range(3):
            text = clean_message(self._chat(SIM_SYSTEM, prompt + extra, self.seed + turn * 10 + attempt, 240))
            # A retry sometimes "obeys" by tacking new text onto a restatement of the old
            # message instead of replacing it, which duplicates content without matching
            # byte-for-byte. A message containing the last one as a prefix is that pattern.
            if not text or text.strip().casefold() == last_me or text.strip().casefold().startswith(last_me):
                extra = nudge
                continue
            if cap and len(text.split()) > cap:
                extra, too_long = shorter, text
                continue
            return text
        if too_long:
            self.trimmed = True
            return trim_to_words(too_long, cap)
        self.fell_back = True
        return beat

    def exit_interview(self, transcript: list, window: int = 12, samples: int = 3) -> dict:
        """Several in-character answers to the same questions, and their mean."""
        prompt = (
            f"{self._persona()}\n\nThe last stretch of the conversation:\n"
            f"{render_transcript(transcript, window)}\n\nAnswer as this person."
        )
        answers = []
        for i in range(samples * 2):
            if len(answers) == samples:
                break
            parsed = parse_exit(self._chat(EXIT_SYSTEM, prompt, self.seed + 9000 + i, 400))
            if parsed:
                answers.append(parsed)
        mean = {k: round(sum(a[k] for a in answers) / len(answers), 2) for k in EXIT_KEYS} if answers else {}
        return {"samples": answers, "mean": mean}
