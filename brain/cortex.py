import os
import random
import re
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from archetypes.symbiosis import SymbiosisManager
from brain.composer import LLMInterface, PromptComposer, ResponseValidator
from engine import turn_guard
from brain.linear_cortex import LinearCortexRouter
from brain.mind import DreamEngine, NeurotransmitterModulator
from engine.constants import Prisma
from engine.core import DecisionCrystal, EventBus, LoreManifest, TelemetryService
from engine.receipts import issue as issue_receipt
from mechanics.dspycritic import DSPyCritic
from mechanics.pragmatics import ThePragmatist
from mechanics.projector import beautify_thoughts, drop_title, is_system_label, parse_spatial_reality
from mechanics.tools import LibraryGraph, RandomRetrievalNavigator
from engine.presets import BoneConfig, BonePresets
from engine.struts import dump_state, safe_get, safe_set, ux, ux_format

_EXAMINE_VERBS = re.compile(
    r"\b(?:look(?:\s+closer)?\s+at|examine|inspect|check\s+out|study|observe)\b"
    r"\s+(?:the\s+|a\s+|an\s+)?(.+)",
    re.IGNORECASE,
)
_EXAMINE_STOPWORDS = frozenset(
    "the a an at closer to again once more please just now it that this".split()
)

def _room_slug(room_name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", room_name.lower()).strip("_") or "room"


def _examine_target_key(user_input: str) -> Optional[str]:
    match = _EXAMINE_VERBS.search(user_input)
    if not match:
        return None
    words = re.findall(r"[a-z0-9]+", match.group(1).lower())
    content = sorted({w for w in words if w not in _EXAMINE_STOPWORDS})
    return " ".join(content) if content else None


@dataclass
class CortexServices:
    events: EventBus
    lore: Any
    lexicon: Any
    inventory: Any
    consultant: Any
    orchestrator: Any
    symbiosis: Any
    mind_memory: Any
    bio: Any
    host_stats: Any = None
    village: Any = None
    config_ref: Any = None
    akashic: Any = None

_OWN_ACT = re.compile(r"\bI (?:said|told|sent|yelled|screamed|snapped|texted|wrote|called (?:her|him|them) )", re.I)


def own_part(said: list, most: int = 2) -> list:
    """The latest sentences in which the person says what they did to someone, in their words ("I said something
    back. Loud."); the ONE SIDE block and the fairness check hand them back, since the model forgot them."""
    found = []
    for text in said:
        sentences = [x.strip() for x in re.split(r"(?<=[.!?])\s+", str(text or "")) if x.strip()]
        i = 0
        while i < len(sentences):
            if not _OWN_ACT.search(sentences[i]):
                i += 1
                continue
            # "I said something back." says little; what follows says what it was.
            take = sentences[i:i + 1]
            while len(" ".join(take).split()) < 12 and i + len(take) < len(sentences):
                take.append(sentences[i + len(take)])
            if (part := " ".join(take)) not in found:
                found.append(part)
            i += len(take)
    return found[-most:]


def first_sentence(text: str) -> str:
    return re.split(r"(?<=[.!?])\s", str(text or "").strip(), maxsplit=1)[0].strip()


def _asks_about(reply: str, memory: tuple) -> bool:
    """Whether a question in the reply shares a word with the memory (key, value). "How have things been since we
    last spoke?" took the turn's question in 2 of 3 fresh sessions; it is not a follow-up on decision_on_pepper."""
    from engine.gate.keeper import _content

    about = _content(memory[0].replace("_", " ")) | _content(memory[1])
    return any(_content(q) & about for q in re.findall(r"[^.!?]*\?", str(reply or "")))


class TheCortex:
    LEXICAL_PURGE_PATTERN = re.compile(
        r"(?im)^\s*(that makes sense|i understand|you bring up|great point|good point|certainly|absolutely|i hear you|yes, )[.,!]*\s*"
    )
    ROLE_MAP = {
        "CONVERSATION": ("CONVERSATIONALIST", "The Conversationalist"),
        "TECHNICAL": ("SYSTEM_KERNEL", "The System Kernel"),
        "CREATIVE": ("CATALYST", "The Catalyst"),
    }
    EMPTY_MAX_TOKENS = 160

    def __init__(self, services: CortexServices, llm_client=None):
        self.ballast_active = False
        self.last_model_raw = ""
        self.heavy_cap = None
        self.svc = services
        self.cfg = services.config_ref or BoneConfig
        self.events = services.events
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        self.MAX_HISTORY = int(safe_get(c_cfg, "MAX_HISTORY_LENGTH", 15))
        self.dialogue_buffer = deque(maxlen=self.MAX_HISTORY)
        self.asked_open = set()  # (key, value) of open memories followed up on, or offered enough, this session
        self.offered_open = {}  # (key, value): turns the follow-up was offered without the reply asking
        self.pending_ask = None
        self.side_on_ending = False
        self.voice_pass = bool(safe_get(safe_get(self.cfg, "CORTEX", {}), "VOICE_PASS", False))
        # One fairness check on the reply shown, repaired by an edit, instead of one on every draft and edit.
        self.fairness_once = bool(safe_get(safe_get(self.cfg, "CORTEX", {}), "FAIRNESS_ONCE", False))
        self.openings = deque(maxlen=4)  # [move or None until judged, first sentence] of the last replies shown
        self.worry_ledger = deque(maxlen=20)
        self.modulator = NeurotransmitterModulator(
            bio_ref=self.svc.bio, events_ref=self.events, config_ref=self.cfg
        )
        self.last_physics = {}
        self.last_shadow_nodes = []
        self.room_examine_cache: Dict[str, str] = {}
        self.current_room_name: str = ""
        # The room this turn's reply described, for the cartographer; None when it described none.
        self.last_room: Optional[Dict[str, Any]] = None
        self.last_context: Optional[Dict[str, Any]] = None  # what this turn's reply was handed (turn_contexts)
        self.current_room_description: str = ""
        self.visited_rooms: Dict[str, Dict[str, Any]] = {}
        self.consultant = services.consultant
        self.llm = llm_client or LLMInterface(
            self.events, provider="mock", config_ref=self.cfg
        )
        eng_ref = self.svc.orchestrator.eng if self.svc.orchestrator else None
        if eng_ref and hasattr(eng_ref, "mind") and hasattr(eng_ref.mind, "dreamer"):
            self.dreamer = eng_ref.mind.dreamer
            self.dreamer.llm = self.llm
            self.dreamer.mem = self.svc.mind_memory
        else:
            self.dreamer = DreamEngine(
                self.events,
                self.svc.lore,
                llm_ref=self.llm,
                mem_ref=self.svc.mind_memory,
                eng_ref=eng_ref,
                config_ref=self.cfg,
            )
        self.llm.dreamer = self.dreamer
        self.symbiosis = services.symbiosis
        self.composer = PromptComposer(self.svc.lore, config_ref=self.cfg)
        self.validator = ResponseValidator(self.svc.lore, config_ref=self.cfg)
        self.pragmatist = ThePragmatist(events_ref=self.events)
        self._recent_pauses: List[str] = []
        self.dspy_critic = DSPyCritic(config_ref=self.cfg)
        self.dreamer.dspy_critic = self.dspy_critic
        self.active_mode = "ADVENTURE"
        if hasattr(self.svc.mind_memory, "nodes"):
            graph = LibraryGraph(
                nodes=self.svc.mind_memory.nodes, root=self.svc.mind_memory.root
            )
            self.navigator = RandomRetrievalNavigator(library_graph=graph)
        else:
            self.navigator = None

        self.linear_router = LinearCortexRouter(token_budget=12000)
        self.is_linear_stocked = False

    @classmethod
    def from_engine(cls, engine_ref, llm_client=None):
        target_cfg = getattr(engine_ref, "config", BoneConfig)
        symbiosis_mgr = getattr(engine_ref, "symbiosis", None) or SymbiosisManager(
            engine_ref.events
        )
        services = CortexServices(
            events=engine_ref.events,
            lore=LoreManifest.get_instance(config_ref=target_cfg),
            lexicon=engine_ref.lex,
            inventory=getattr(engine_ref.village, "gordon", None)
            if hasattr(engine_ref, "village")
            else None,
            consultant=engine_ref.consultant,
            orchestrator=engine_ref.orchestrator,
            symbiosis=symbiosis_mgr,
            mind_memory=engine_ref.mind.mem,
            bio=engine_ref.bio,
            host_stats=engine_ref.host_stats,
            village=engine_ref.village,
            config_ref=target_cfg,
            akashic=engine_ref.akashic,
        )
        instance = cls(services, llm_client)
        instance.active_mode = getattr(engine_ref, "boot_mode", "ADVENTURE").upper()
        if instance.active_mode not in BonePresets.MODES:
            instance.active_mode = "ADVENTURE"
        return instance

    _OTHERS = re.compile(r"\b(?:she|he|her|him|his|they|them|their)\b", re.I)
    # The fairness judge as reading, not verdicts: asked a moral yes or no, every model tried answered with its own
    # values (praising the cruel text as "a brave and incredibly honest move" was fair to all six). Each question asks
    # for the reply's own words, and only words really in the reply count. On 50 replies Gordon labelled: precision
    # 0.74 and recall 0.67 on gemma4:12b, 0.72 and 0.62 on gemma4:e4b; the old judge 0.59 and 0.62, 0.57 and 0.38.
    ACTS = """Here is a message someone wrote to a friend: "{message}"
Copy, word for word, each sentence in which they say what they themselves did or said to another person in a falling-out. One per line. If there is none, answer NONE."""
    EXCUSE = """Someone told a friend they did this:
{acts}
The friend replied: "{reply}"
Copy, word for word, the words in the reply that call what they did brave, honest, right, fair, needed or deserved, that say it was okay, that they had to do it, or that they stood up for themselves by doing it. Saying why it happened, or how it will land, does not count. If there are none, answer NONE."""
    MIND = """Someone told a friend: "{message}"
The friend replied: "{reply}"
The message is about another person, the one they are talking about (not the one writing, and not the friend). Copy, word for word, the words in the reply that say why that other person did something, what that other person is like, or that that other person does something as a habit, when the message did not say so. Words about the one writing do not count, and neither does saying plainly what the other person did. If there are none, answer NONE."""
    RULE = """Someone told a friend: "{message}"
The friend replied: "{reply}"
Copy, word for word, the words in the reply that tell them their relationship is over or should end, or tell them to end it or walk away. Words about what might be, or conditions for them to weigh, do not count. If there are none, answer NONE."""
    SIDE = {"a": "it excuses what they did", "b": "it says what the other person is like or why she did it",
            "c": "it rules on whether the relationship ends"}

    OPENING = """How does this reply to a friend begin? Read only its first sentence and answer with one word.
ASSESS: it passes a verdict on what they said, did or are going through, or states a general truth about it ("That is a big step.", "Moving is always harder than people expect.", "The waiting is the worst part.").
FEEL: it reacts with sympathy or feeling for them ("I'm so sorry.", "Oh no, not the car.", "I can hear how tired you are.").
ANSWER: it answers or acknowledges briefly ("Yes, it can.", "Go for it.", "Sleep well.", "I'm here.").
ASK: it asks them something ("Did the landlord ever call back?").
ECHO: it repeats their own words back ('"Like a stranger in my own kitchen."').
First sentence: "{sentence}"
Answer:"""
    MOVES = ("ASSESS", "FEEL", "ANSWER", "ASK", "ECHO")
    INSTEAD = {"ASK": "a plain question about what they just told you", "ECHO": "their own words, picked up",
               "FEEL": "a few words of feeling for them", "ANSWER": "a short, direct answer",
               "ASSESS": "what you make of it"}

    def _opening_move(self, text: str) -> tuple:
        """(move, first sentence) of a reply. feud20 (2026-10-06): 16 of 20 replies opened with a verdict on what was
        said ("That is a heavy..."); the embedder told moves apart 73 of 100, this call 85 (46 of 52 verdicts)."""
        sentence = first_sentence(text)
        if not sentence:
            return "", ""
        if sentence.endswith("?"):
            return "ASK", sentence
        usage = getattr(self.llm, "last_usage", None)
        try:
            answer = str(self.llm.generate(self.OPENING.format(sentence=sentence), {"temperature": 0.0, "max_tokens": 5}) or "")
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        return next((m for m in self.MOVES if answer.strip().upper().startswith(m)), ""), sentence

    def _in_a_rut(self, reply: str) -> bool:
        """The reply opens as the last OPENING_RUT replies shown did. Openings are judged only now, newest first, and
        only until two differ."""
        rut = int(safe_get(safe_get(self.cfg, "CORTEX", {}), "OPENING_RUT", 3))
        last = list(self.openings)[-rut:]
        if len(last) < rut:
            return False
        for entry in reversed(last):
            if entry[0] is None:
                entry[0] = self._opening_move(entry[1])[0]
            if not entry[0] or entry[0] != last[-1][0]:
                return False
        self._draft_opening = self._opening_move(reply)
        return self._draft_opening[0] == last[-1][0]

    REWRITE = """Here is a message a friend wrote back to someone, and what that person had said to them.
{earlier}They just said: "{message}"
The friend's reply: "{reply}"
Replace the reply's first sentence with one short question that takes what they just said one step further: the plain question a friend would ask about the people and things in it, not about their feelings in general (never "How does that make you feel?"). Never ask what they have already told you, now or earlier, and never just turn their words into a question. Keep everything after it as it is, word for word, unless a word must change to follow on. Do not add a greeting. Answer with the whole rewritten reply and nothing else."""

    def _open_with_a_question(self, message: str, reply: str, gk: Any) -> str:
        """The reply with its first sentence made a question, or "" when the edit did not hold. A redraft kept the
        habit 6 of 7 times (the prompt's own history pulls it back); this edit took 5 of 5 live. Shown only the latest
        message it asked what they had just said (6 of 19) or had told it earlier."""
        usage = getattr(self.llm, "last_usage", None)
        try:
            out = str(self.llm.generate(self.REWRITE.format(earlier=self._earlier(), message=message, reply=reply),
                                        {"temperature": 0.0, "max_tokens": 400}) or "").strip().strip('"')
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        question = first_sentence(out)
        rest = out[len(question):].split()
        kept = reply[len(first_sentence(reply)):].split()
        if not question.endswith("?") or len(rest) < 0.6 * len(kept) or (gk and gk._find_crime(question, self.active_mode)):
            return ""
        return out

    VOICE = """Here is what someone said to a friend, and the reply the friend drafted.
{earlier}They just said: "{message}"
The draft: "{reply}"
Rewrite the draft the way the friend would actually say it to them, sitting across a table: talking with them, not describing their situation back to them or explaining how things work. Plain words. React, say what you think, or ask what you want to know. Keep what the draft means, including anything it says about what they did themselves, and anything it leaves for them to decide. About as long as the draft, or shorter. No "I hear you", no "that makes sense", no stage directions, no dashes between clauses. Answer with the rewritten reply and nothing else."""

    def _earlier(self) -> str:
        said = [line.split("\n")[0].removeprefix("Traveler: ") for line in self.dialogue_buffer][-4:]
        return "Earlier they said:\n" + "".join(f'- "{m}"\n' for m in said) if said else ""

    def _in_a_friends_voice(self, message: str, reply: str, gk: Any, state: dict) -> tuple:
        """(reply as a friend would say it, or "", why not). feud20 (2026-10-06): rules, rewritten rules and examples
        in the prompt left 15 or 16 of 20 openings verdicts; the reply comes from the model's register and its own
        history. Rewriting the finished draft read like a person, but freely it sided ("a huge violation of trust"),
        ruled on the ending and used dashes, so a rewrite that fails a guard is not used."""
        usage = getattr(self.llm, "last_usage", None)
        try:
            out = str(self.llm.generate(self.VOICE.format(earlier=self._earlier(), message=message, reply=reply),
                                        {"temperature": 0.0, "max_tokens": 400}) or "").strip().strip('"')
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        words, was = len(out.split()), len(reply.split())
        if not out or not 0.4 * was <= words <= 1.3 * was + 5:
            return "", "length"
        if "\u2014" in out or "\u2013" in out:
            return "", "dash"
        if gk and (crime := gk._find_crime(out, self.active_mode)):
            return "", f"style: {crime.get('name', '')}"
        if not self.fairness_once and (why := self._sides_in(message, out, reply, state)):
            return "", f"fairness: {why}"
        return out, ""

    ENDING = """Here is what someone asked a friend, and the reply the friend drafted.
{earlier}They just said: "{message}"
The draft: "{reply}"
Whether their relationship is over or should end is theirs to decide, not the friend's. Rewrite the draft so it stays theirs: keep one thing the draft sees, said as a "perhaps" or a "maybe", then {back} Shorter than the draft is fine. No dashes between clauses. Answer with the rewritten reply and nothing else."""
    # The first asks what a friend would; 3 of 15 still presumed the answer ("what makes it so hard to let go?"). The
    # second passed 14 of 15 but was the same question 10 times, so it is only the fallback.
    BACK = ('hand it back with one plain, open question about the people and things they told you about, the kind a '
            'friend would ask, that does not suggest an answer (never "Is it time to let it go?").',
            'ask them in one plain, open question what they want, or what ending it or keeping it would change for them. '
            'The question must not suggest an answer (never "Is it time to let it go?" or "Is this the point for you?").')

    # Phrasings of wanting out, not from any probe. A message near one (nomic, "classification:") then goes to ASKS.
    ENDING_LIKE = ("Should I just stop talking to him for good?", "I think it might be time to cut her off.",
                   "Is this friendship even worth saving anymore?", "Maybe I should block him and move on.",
                   "At what point do you give up on someone?", "I'm thinking of ending things with her.")
    ASKS = """Someone wrote this to a friend: "{message}"
Are they asking whether to end their relationship with a person, or saying they are thinking of ending it (cutting the person off, unfriending or unfollowing them, letting the friendship go)? Hurt, anger, missing someone, giving up on a task, or telling what happened in a fight is NO. Answer YES or NO."""

    def _asks_about_ending(self, message: str) -> bool:
        """They ask whether to end it, so the reply leaves it to them, judge or not (Gordon). On 834 simulated
        messages the call alone said yes to 30, a dozen of them about a wedding toast; nomic alone put "Maybe I should
        just text her" beside "Maybe I should just unfriend her"; both together, 11, all of them right."""
        said = [line.split("\n")[0] for line in list(self.dialogue_buffer)[-3:]] + [str(message or "")]
        embedder = self._recall_embedder()
        if not any(self._OTHERS.search(s) for s in said) or embedder is None or embedder.degraded:
            return False
        floor = float(safe_get(safe_get(self.cfg, "CORTEX", {}), "ASKS_ENDING_FLOOR", 0.74))
        prefix = "classification: " if "nomic" in str(embedder.model) else ""
        vectors = embedder.embed_batch([prefix + t for t in (message, *self.ENDING_LIKE)])
        if embedder.degraded or max(sum(a * b for a, b in zip(vectors[0], v)) for v in vectors[1:]) < floor:
            return False
        usage = getattr(self.llm, "last_usage", None)
        try:
            answer = str(self.llm.generate(self.ASKS.format(message=message), {"temperature": 0.0, "max_tokens": 3}) or "")
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        return answer.strip().upper().startswith("YES")

    def _leave_the_ending(self, message: str, reply: str, gk: Any, state: dict) -> str:
        """The reply edited so whether the relationship ends stays theirs, or "" when no edit held. feud20
        (2026-10-06): the redraft after a leaning first draft is never judged, and it went out as criteria ("that is
        a clear sign of where your energy is going") with nothing handed back (Gordon: always defer to them)."""
        self.ending_misses = []
        for back in self.BACK:
            usage = getattr(self.llm, "last_usage", None)
            try:
                out = str(self.llm.generate(self.ENDING.format(earlier=self._earlier(), message=message, reply=reply,
                                                               back=back), {"temperature": 0.0, "max_tokens": 300})
                          or "").strip().strip('"')
            finally:
                if usage is not None:
                    self.llm.last_usage = usage
            crime = gk and gk._find_crime(out, self.active_mode)
            miss = ("shape" if len(out.split()) < 10 or not out.rstrip().endswith("?") else
                    "dash" if "\u2014" in out or "\u2013" in out else
                    f"style: {crime.get('name', '')}" if crime else
                    f"fairness: {why}" if (why := self._sides_in(message, out, reply, state)) else "")
            if not miss:
                return out
            self.ending_misses.append(miss)
        return ""

    REPAIR = """Here is what someone said to a friend, and the reply the friend drafted.
{earlier}They just said: "{message}"
The draft: "{reply}"
In the draft, {why}. Rewrite the draft without that: {fix} Keep everything else as it is, and about as long. No dashes between clauses. Answer with the rewritten reply and nothing else."""
    FIX = {"a": "do not praise or excuse what they did; you can still say how it will land on the other person.",
           "b": "say only what the other person did, not why she did it or what she is like."}

    def _fair_as_shown(self, message: str, reply: str, draft: str, gk: Any, state: dict) -> str:
        """The reply shown, judged once. Flagged, an edit takes the quoted words out (an edit held where redrafts kept
        the habit), or the hand-back edit when it rules on the ending; then the unvoiced draft; else the fewest flags."""
        why = self._takes_a_side(message, reply, state)
        if not why:
            return reply
        flagged, tried = [(why, reply)], []
        if self.side_on_ending:
            tried.append(self._leave_the_ending(message, reply, gk, state))
        else:
            kinds = [k for k, v in self.SIDE.items() if v in why and k in self.FIX]
            usage = getattr(self.llm, "last_usage", None)
            try:
                tried.append(str(self.llm.generate(self.REPAIR.format(
                    earlier=self._earlier(), message=message, reply=reply, why=why,
                    fix=" ".join(self.FIX[k] for k in kinds) or self.FIX["b"]), {"temperature": 0.0, "max_tokens": 400})
                    or "").strip().strip('"'))
            finally:
                if usage is not None:
                    self.llm.last_usage = usage
        tried.append(draft if draft != reply else "")
        for text in tried:
            words, was = len(text.split()), len(reply.split())
            if (not text or not 0.4 * was <= words <= 1.3 * was + 5 or "\u2014" in text or "\u2013" in text
                    or (gk and gk._find_crime(text, self.active_mode))):
                continue
            if not (again := self._takes_a_side(message, text, state)):
                issue_receipt("cortex.fairness", "REPAIRED", result_count=1, detail=why)
                return text
            flagged.append((again, text))
        least = min(flagged, key=lambda f: f[0].count("; "))
        issue_receipt("cortex.fairness", "KEPT_FLAGGED", result_count=0, degraded=True, detail=least[0])
        return least[1]

    def _note_opening(self, reply: str) -> None:
        drafted = getattr(self, "_draft_opening", None)
        self._draft_opening = None
        if sentence := first_sentence(reply):
            known = drafted[0] if drafted and drafted[1] == sentence else "ASK" if sentence.endswith("?") else None
            self.openings.append([known, sentence])

    def _quoted(self, prompt: str, source: str, tokens: int = 120) -> list:
        """The lines of the model's answer that are really in `source` (two words or more); NONE is none."""
        usage = getattr(self.llm, "last_usage", None)
        try:
            answer = str(self.llm.generate(prompt, {"temperature": 0.0, "max_tokens": tokens}) or "").strip()
        finally:
            if usage is not None:
                self.llm.last_usage = usage
        if answer.upper().startswith("NONE"):
            return []
        words = lambda t: " ".join(re.findall(r"[a-z0-9']+", t.lower().replace("\u2019", "'")))
        within = words(source)
        lines = (line.strip(' -*\u2022"\u201c\u201d') for line in answer.splitlines())
        return [q for q in lines if len(words(q).split()) >= 2 and words(q) in within]

    def _their_acts(self, message: str) -> list:
        """What the person says they did, quoted from their own last messages; each message is read once."""
        said = [line.split("\n")[0].removeprefix("Traveler: ") for line in list(self.dialogue_buffer)[-3:]] + [message]
        seen = self.__dict__.setdefault("acts_read", {})
        for m in said:
            if m and m not in seen:
                seen[m] = self._quoted(self.ACTS.format(message=m), m)
        while len(seen) > 64:
            seen.pop(next(iter(seen)))
        return [a for m in said for a in seen.get(m, [])]

    def _takes_a_side(self, message: str, draft: str, state: dict) -> str:
        """Why the draft sides with the person or against someone not here, with the reply's own words, or "". Prompt
        rules held about half of these (feud20, 2026-10-05: the cruel text was "a heavy truth to put into words")."""
        # "Is there a point where you just let it end?" names no one; the conversation around it does.
        said = [line.split("\n")[0] for line in list(self.dialogue_buffer)[-3:]] + [str(message or "")]
        if not any(self._OTHERS.search(s) for s in said) or not str(draft or "").strip():
            return ""
        # A text already read this turn is not read again (about nine judge calls a turn went to repeats).
        verdicts = self.__dict__.setdefault("verdicts", {})
        if (message, draft) in verdicts:
            why, self.side_on_ending = verdicts[(message, draft)]
            self.judged = (draft, why)
            return why
        found = {}
        if acts := self._their_acts(str(message or "")):
            found["a"] = self._quoted(self.EXCUSE.format(acts="\n".join(f'- "{a}"' for a in acts), reply=draft), draft)
        found["b"] = self._quoted(self.MIND.format(message=message, reply=draft), draft)
        found["c"] = self._quoted(self.RULE.format(message=message, reply=draft), draft)
        self.side_on_ending = bool(found["c"])
        why = "; ".join(f'{self.SIDE[k]}: "{q[0]}"' for k, q in found.items() if q)
        self.judged = (draft, why)
        verdicts[(message, draft)] = (why, self.side_on_ending)
        while len(verdicts) > 32:
            verdicts.pop(next(iter(verdicts)))
        return why

    def _sides_in(self, message: str, edited: str, draft: str, state: dict, whole: bool = True) -> str:
        """Why an edited reply takes a side, judging the whole and each question the edit added on its own: amid fair
        sentences "or did you just realize that keeping the friendship going was becoming too much of a burden?" passed,
        alone it was (c) (feud20, 2026-10-06)."""
        if whole and (why := self._takes_a_side(message, edited, state)):
            return why
        had = {s.strip() for s in re.split(r"(?<=[.!?])\s+", draft)}
        for question in (s.strip() for s in re.split(r"(?<=[.!?])\s+", edited)):
            if question.endswith("?") and question not in had and (why := self._takes_a_side(message, question, state)):
                return why
        return ""

    def _update_history(self, user_text: str, system_text: str):
        self.dialogue_buffer.append(f"Traveler: {user_text}\nSystem: {system_text}")

    def _check_examine_cache(self, user_input: str) -> Optional[str]:
        target_key = _examine_target_key(user_input)
        if target_key is None:
            return None
        return self.room_examine_cache.get(target_key)

    def _record_examine_result(self, user_input: str, final_output: str) -> None:
        parsed = parse_spatial_reality(final_output)
        room_name = parsed["room_name"]
        is_new_room = room_name != "Uncharted Zone" and room_name != self.current_room_name
        if room_name != "Uncharted Zone":
            room_id = _room_slug(room_name)
            existing = self.visited_rooms.get(room_id, {})
            self.last_room = self.visited_rooms[room_id] = {
                "id": room_id,
                "name": room_name,
                "description": parsed["description"] or existing.get("description", ""),
                "exits": parsed["exits"] or existing.get("exits", []),
                "pois": parsed["pois"] or existing.get("pois", []),
            }
        if is_new_room:
            self.current_room_name = room_name
            self.current_room_description = parsed["description"]
            self.room_examine_cache = {}
            return
        target_key = _examine_target_key(user_input)
        if target_key:
            self.room_examine_cache[target_key] = final_output

    def _place_title(self, text: str) -> str:
        """Gordon: a room title names the place. A zone label is dropped (a guess could name the wrong room)."""
        title = parse_spatial_reality(text)["room_name"]
        if not is_system_label(title):
            return text
        if self.events:
            self.events.log(f"Room title {title!r} was a system label; dropped from the reply.", "CORTEX")
        return drop_title(text)

    def restore_room_state(
        self, visited_rooms: Dict[str, Dict[str, Any]], current_room_id: str
    ) -> None:
        self.visited_rooms = dict(visited_rooms)
        current = self.visited_rooms.get(current_room_id, {})
        self.current_room_name = current.get("name", "")
        self.current_room_description = current.get("description", "")

    def shutdown(self):
        pass

    def purge_context(self):
        self.last_shadow_nodes = []
        self.room_examine_cache.clear()
        self.current_room_name = ""
        self.current_room_description = ""
        self.visited_rooms.clear()
        self.dialogue_buffer.clear()
        self.last_physics.clear()
        self.dreamer.trauma_buffer.clear()
        if self.events:
            self.events.log(
                "Context array purged. Stateless bedrock re-established.",
                "SYS",
            )

    def process_context(self, ctx: Any) -> Dict[str, Any]:
        # The accepted draft as the model wrote it, NOMINATE lines included; empty when no draft was accepted.
        self.last_model_raw = ""
        user_input = ctx.input_text or ""
        is_system = getattr(ctx, "is_system_event", False)
        mode_settings = BonePresets.MODES.get(
            self.active_mode, BonePresets.MODES["ADVENTURE"]
        )
        allow_loot = mode_settings.get("allow_loot", True)
        if self.navigator:
            target_randomness = {
                "CREATIVE": 0.7,
                "ADVENTURE": 0.3,
                "CONVERSATION": 0.3,
            }.get(self.active_mode, 0.0)
            dial_status = self.navigator.set_randomness(target_randomness)
            if self.events and dial_status["new_value"] > 0:
                self.events.log(
                    f"Serendipity Engine active: {dial_status['mode']}", "CORTEX"
                )
        if self.consultant and "/vsl" in user_input.lower():
            return self._handle_vsl_command(user_input)
        is_boot_sequence = "SYSTEM_BOOT" in user_input
        phys_proxy = dump_state(ctx.physics) if ctx.physics is not None else {}
        sim_result = {
            "physics": phys_proxy,
            "bio": getattr(ctx, "bio_result", {}),
            "mind": getattr(ctx, "mind_state", {}),
            "world": getattr(ctx, "world_state", {}),
            "somatic_budget": getattr(ctx, "somatic_budget", None),
            "ui": getattr(ctx, "bureau_ui", ""),
            "logs": getattr(ctx, "logs", []),
            "council_mandates": getattr(ctx, "council_mandates", []),
            "dream": getattr(ctx, "last_dream", None),
            "mutated_input": user_input,
            "trace_id": getattr(ctx, "trace_id", "UNKNOWN"),
            "type": getattr(ctx, "type", "SNAPSHOT"),
        }
        if (
            self.active_mode == "ADVENTURE"
            and not is_boot_sequence
            and self.current_room_description
        ):
            sim_result["world"].setdefault(
                "loci_description", self.current_room_description
            )
        if self.active_mode == "ADVENTURE" and self.current_room_name and not is_system_label(self.current_room_name):
            sim_result["world"]["room_name"] = self.current_room_name
            # The graph's version of the room, charted from earlier replies, is what is true in the story.
            from engine.gate.cartographer import room_view

            if charted := room_view(getattr(ctx, "halcyon_state", None), self.current_room_name):
                sim_result["world"]["room"] = charted
        if halt := self._pre_flight_routing(
            user_input, is_system, is_boot_sequence, ctx, sim_result
        ):
            return halt
        user_input = sim_result.get("mutated_input", user_input)
        if sim_result.get("physics"):
            self.last_physics = sim_result["physics"]
        if self.last_shadow_nodes:
            engaged = [
                node
                for node in self.last_shadow_nodes
                if node.lower() in user_input.lower()
            ]
            for node in engaged:
                if self.events:
                    self.events.publish(
                        "SHADOW_ENGAGED",
                        {
                            "source": self.last_physics.get("primary_node", "core")
                            if self.last_physics
                            else "core",
                            "target": node,
                            "user_input": user_input,
                        },
                    )
            self.last_shadow_nodes = []
        sim_result["halcyon_recall"] = self._halcyon_recall(ctx, user_input)
        sim_result["halcyon_refusal"] = self._take_refusal()
        sim_result["held_request"] = self._take_held()
        from engine.gate.recall import zone

        found = sim_result["halcyon_recall"] if isinstance(sim_result["halcyon_recall"], dict) else {}
        self.last_context = {"mode": self.active_mode, "zone": zone(self.active_mode),
                             "recalled": [k for k, _ in found.get("memories", [])], "facts": list(found.get("facts", [])),
                             "refusal": sim_result["halcyon_refusal"]}
        full_state = self.gather_state(sim_result)
        phys_state = full_state.get("physics", {})
        modifiers = self.svc.symbiosis.get_prompt_modifiers(phys_state)
        eng_ref = getattr(getattr(self.svc, "orchestrator", None), "eng", None)
        modifiers["grace_period"] = bool(getattr(eng_ref, "in_grace", lambda: False)())
        if not allow_loot or is_boot_sequence:
            modifiers["include_inventory"] = False
        if self.consultant and self.consultant.active:
            self._apply_vsl_overlay(full_state, user_input, sim_result)
        if is_boot_sequence:
            self._apply_boot_overlay(full_state, user_input)
        b_voltage = float(phys_state.get("voltage", 5.0))
        somatic_budget = full_state.get("somatic_budget")
        llm_params = self.modulator.modulate(
            base_voltage=b_voltage,
            latency_penalty=getattr(self.svc.host_stats, "latency", 0.0),
            physics_state=phys_state,
            somatic_budget=somatic_budget,
        )
        if is_boot_sequence:
            llm_params.update({"temperature": 0.7, "top_p": 0.95})
            
        somatic_budget = full_state.get("somatic_budget")
        if somatic_budget and somatic_budget.word_cap:
            llm_params["max_tokens"] = min(llm_params.get("max_tokens", 4096), somatic_budget.word_cap * 2 + 50)
        if full_state.get("running_on_empty"):
            llm_params["max_tokens"] = min(llm_params.get("max_tokens", 4096), self.EMPTY_MAX_TOKENS)

        structural_ctx, cognitive_path, token_cost = self._route_dual_memory(user_input)
        if structural_ctx:
            full_state["mind"].setdefault("style_directives", []).append(
                f"CRITICAL STRUCTURAL CONTEXT (Linear Sweep):\n{structural_ctx}"
            )
            if hasattr(self.svc.bio.mito, "process_cognitive_load"):
                self.svc.bio.mito.process_cognitive_load(token_cost, cognitive_path)

        final_prompt = self.composer.compose(
            full_state,
            user_input,
            ballast=self.ballast_active,
            modifiers=modifiers,
            mood_override=self.modulator.get_mood_directive(),
        )
        start_time = time.time()
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        cognitive_retries = int(safe_get(c_cfg, "COGNITIVE_RETRY_LIMIT", 2))
        if somatic_budget:
            cognitive_retries = min(cognitive_retries, somatic_budget.retry_allowance)
        final_output, inv_logs, extracted_logs = "", [], []
        raw_resp: str = ""
        # Only the cognitive loop re-asks; the council and the examine cache answer on the first try.
        attempt_count = 0
        val_res: Dict[str, Any] = {"valid": False}
        if "[COUNCIL]" in user_input.upper():
            final_output, extracted_logs = self._run_council_debate(user_input)
            val_res = {
                "valid": True,
                "content": final_output,
                "meta_logs": extracted_logs,
            }
        mandates_raw = sim_result.get("council_mandates", [])
        firewall_active = any(
            m.get("action") == "LEXICAL_FIREWALL_STRICT" for m in mandates_raw
        )
        base_prompt = final_prompt
        eng_ref = getattr(self.svc.orchestrator, "eng", None)
        gk = getattr(eng_ref, "gatekeeper", None)
        if not gk:
            from physics import TheGatekeeper

            gk = TheGatekeeper(self.svc.lexicon, config_ref=self.cfg)
        cached_examine = (
            self._check_examine_cache(user_input)
            if self.active_mode == "ADVENTURE" and not is_boot_sequence and not val_res.get("valid")
            else None
        )
        if cached_examine is not None:
            final_output = cached_examine
            val_res = {"valid": True, "content": cached_examine, "meta_logs": []}
            if self.events:
                self.events.log(
                    f"{Prisma.GRY}[MEMORY] You've already looked at this. Recalling.{Prisma.RST}",
                    "CORTEX",
                )
        elif cognitive_retries > 0:
            # "I've been thinking about it" is true only when a REM reflection drew on what this prompt recalls.
            recalled = sim_result.get("halcyon_recall") if isinstance(sim_result.get("halcyon_recall"), dict) else {}
            gk.allowed = self.validator.allowed = (
                {"UNBACKED_CONTINUITY"} if recalled.get("reflected") or (recalled.get("ask") or {}).get("reflected") else set())
            final_output, raw_resp, extracted_logs, inv_logs, val_res, final_prompt, attempt_count = (
                self._execute_cognitive_loop(
                    user_input,
                    full_state,
                    base_prompt,
                    llm_params,
                    allow_loot,
                    phys_state,
                    is_boot_sequence,
                    firewall_active,
                    gk,
                    cognitive_retries,
                )
            )
            if self.svc.bio and raw_resp:
                gen_tokens = max(1, len(raw_resp) // 4)
                ros_yield = gen_tokens * 0.015
                atp_burn = self._token_burn(gen_tokens)

                current_ros = float(self.svc.bio.mito.state.ros_buildup)
                self.svc.bio.mito.state.ros_buildup = min(
                    100.0, current_ros + ros_yield
                )
                self.svc.bio.mito.adjust_atp(-atp_burn, "LLM Token Generation")
            if val_res.get("valid") and self.active_mode == "ADVENTURE":
                final_output = self._place_title(final_output)
                self._record_examine_result(
                    "SYSTEM_INIT" if is_boot_sequence else user_input, final_output
                )
        if val_res["valid"] and phys_state.get("psi", 0.0) > 0.6 and allow_loot:
            if self.svc.bio:
                self.svc.bio.mito.adjust_atp(-1.0, "Anti-AI Substrate Filter")
        telemetry_output = raw_resp if not val_res["valid"] else final_output
        self._log_telemetry(final_prompt, telemetry_output, full_state, sim_result)
        self.svc.symbiosis.monitor_host(
            time.time() - start_time, final_output, len(final_prompt)
        )
        conversing = self.active_mode == "CONVERSATION" and not is_boot_sequence and val_res.get("valid")
        voiced, draft_output = "", final_output
        if conversing and self.voice_pass:
            voiced, why = self._in_a_friends_voice(user_input, final_output, gk, full_state)
            issue_receipt("cortex.voice", "REWRITTEN" if voiced else "KEPT_DRAFT", result_count=int(bool(voiced)),
                          detail=why or first_sentence(voiced))
            final_output = voiced or final_output
        # A rewrite that passed was judged; otherwise the reply shown may be a redraft nobody judged.
        cleared = getattr(self, "judged", None) == (final_output, "")
        if conversing and (self._asks_about_ending(user_input) or (
                not voiced and not cleared and not self.fairness_once
                and self._takes_a_side(user_input, final_output, full_state) and self.side_on_ending)):
            left = self._leave_the_ending(user_input, final_output, gk, full_state)
            issue_receipt("cortex.ending", "EDITED" if left else "KEPT_DRAFT", result_count=int(bool(left)),
                          detail=first_sentence(left) if left else "; ".join(self.ending_misses))
            final_output = left or final_output
        if conversing and self._in_a_rut(final_output):
            # The question is new words the fairness check never read ("Was the joke about your ex the only thing that
            # crossed the line?"); one that takes a side is not used.
            fresh = self._open_with_a_question(user_input, final_output, gk)
            # Only the question is new; the rest is the reply already judged.
            if fresh and (self.fairness_once or not self._sides_in(user_input, fresh, final_output, full_state, whole=False)):
                final_output = fresh
                issue_receipt("cortex.opening", "REWRITTEN", result_count=1, inputs={"move": self.openings[-1][0]},
                              detail=first_sentence(fresh))
        if conversing and self.fairness_once:
            final_output = self._fair_as_shown(user_input, final_output, draft_output, gk, full_state)
        turn_guard.check("before the history")
        self._update_history(
            "SYSTEM_INIT" if is_boot_sequence else user_input, final_output
        )
        self._note_ask(final_output)
        if self.active_mode == "CONVERSATION" and not is_boot_sequence:
            self._note_opening(final_output)
        ui_parts = [sim_result.get("ui", "")]
        if sim_result.get("dream"):
            dream_content = sim_result["dream"]
            if isinstance(dream_content, tuple):
                dream_content = dream_content[0]
            elif isinstance(dream_content, dict):
                dream_content = dream_content.get("log", str(dream_content))
            ui_parts.append(
                f"{Prisma.VIOLET}While you were gone: {dream_content}{Prisma.RST}"
            )
        ui_parts.append(f"{Prisma.WHT}{beautify_thoughts(final_output)}{Prisma.RST}")
        if inv_logs:
            ui_parts.append("\n".join(inv_logs))
        sim_result["ui"] = "\n\n".join(filter(None, (str(p).strip() for p in ui_parts)))
        sim_result["logs"] = sim_result.get("logs", []) + extracted_logs
        sim_result["raw_content"] = final_output
        self.ballast_active = False
        self._flush_substrate_writes(extracted_logs, sim_result, user_input)
        self._post_flight_mutations(
            val_res, phys_state, sim_result, final_output, is_system, full_state
        )
        updated_phys = sim_result.get("physics", {})
        if isinstance(updated_phys, dict):
            if isinstance(ctx.physics, dict):
                ctx.physics.update(updated_phys)
            else:
                for k, v in updated_phys.items():
                    setattr(ctx.physics, k, v)

        if somatic_budget:
            from body.somatic_metrics import measure
            from engine.receipts import issue
            import math
            
            metrics = measure(final_output, val_res.get("valid", False))
            
            if not val_res.get("valid"):
                outcome = "failed"
            elif attempt_count > 0:
                outcome = "re-asked"
            elif val_res.get("trimmed"):
                outcome = "trimmed"
            else:
                outcome = "complied"
                
            w = metrics.get("words", 0)
            if math.isnan(w): w = 0
            s = metrics.get("sentences", 0)
            if math.isnan(s): s = 0
            
            issue(
                "cortex.somatic",
                effect=outcome,
                result_count=int(w),
                inputs={
                    "e_u": round(getattr(getattr(self.svc, "shared_lattice", None), "u", type("U", (), {"E": 0.0})()).E, 2) if getattr(self.svc, "shared_lattice", None) else 0.0,
                    "atp": round(getattr(self.svc.bio.mito.state, "atp_pool", 0.0), 1) if self.svc.bio else 0.0,
                    "budget": f"w:{somatic_budget.word_cap or '-'} s:{somatic_budget.sentence_cap}",
                    "measured_w": int(w),
                    "measured_s": int(s)
                },
                detail=f"Budget: {somatic_budget.reason}"
            )

        return sim_result

    def _pre_flight_routing(
        self,
        user_input: str,
        is_system: bool,
        is_boot_sequence: bool,
        ctx: Any,
        sim_result: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        context_limit = int(safe_get(c_cfg, "MAX_INPUT_CHARS", 15000))
        if len(user_input) > context_limit and not is_system and not is_boot_sequence:
            safe_content = user_input.replace("\n", "|||NEWLINE|||")
            self.dreamer.context_queue.append(safe_content)
            s_cost = 5.0
            if self.svc.bio:
                self.svc.bio.mito.adjust_atp(-s_cost, "Massive Context Queueing")
            msg = f"{Prisma.CYN}Massive context drop detected. Routed to REM cycle for deep-indexing. Dialogue buffer bypassed. (-{s_cost:.1f} ATP){Prisma.RST}"
            if self.events:
                self.events.log(msg, "SYS")
            sim_result.update({"ui": msg, "type": "SILENT_INGEST"})
            return sim_result
        if getattr(ctx, "refusal_triggered", False) and getattr(
            ctx, "refusal_packet", None
        ):
            sim_result.update(ctx.refusal_packet)
            self._update_history(
                user_input, str(sim_result.get("ui", "SYSTEM REJECTED PROMPT."))
            )
            return sim_result
        if is_boot_sequence:
            user_input = (
                user_input.replace("SYSTEM_BOOT DETECTED.", "")
                .replace("SYSTEM_BOOT:", "")
                .strip()
            )
            sim_result["mutated_input"] = user_input
        return None

    def nominate_toxicity(
        self, ctx: Any
    ) -> None:
        is_system = getattr(ctx, "is_system_event", False)
        phys_state = dump_state(ctx.physics) if ctx.physics else {}
        
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        tick_atp = float(phys_state.get("delta_atp", 0.0))
        tick_ros = float(phys_state.get("delta_ros", 0.0))
        if tick_atp != 0.0:
            self.svc.bio.mito.adjust_atp(tick_atp, "Creative Determinant Tick")
        if tick_ros != 0.0:
            self.svc.bio.mito.state.ros_buildup = max(
                0.0, min(100.0, self.svc.bio.mito.state.ros_buildup + tick_ros)
            )
        if (
            not is_system
            and self.svc.orchestrator
            and hasattr(self.svc.orchestrator, "eng")
        ):
            eng = self.svc.orchestrator.eng
            efficiency = (
                getattr(self.svc.host_stats, "efficiency_index", 1.0)
                if self.svc.host_stats
                else 1.0
            )
            energy_state = phys_state.get("energy", {})
            novelty = float(
                phys_state.get(
                    "novelty",
                    energy_state.get("novelty", 0.0)
                    if isinstance(energy_state, dict)
                    else getattr(energy_state, "novelty", 0.0),
                )
            )
            if hasattr(eng, "navi_sad"):
                dimension = eng.navi_sad.calculate_semantic_dimension(
                    efficiency, novelty
                )
                phys_state["omega_r"] = dimension
            else:
                dimension = phys_state.get("omega_r", 1.0)
            lattice_u = getattr(getattr(eng, "shared_lattice", None), "u", None)
            user_exhaust = (
                float(lattice_u.E)
                if lattice_u and hasattr(lattice_u, "E")
                else float(phys_state.get("exhaustion", 0.0))
            )
            resonance_delta = float(phys_state.get("resonance", 0.5))
            if hasattr(eng, "governor"):
                phys_state["beth_index"] = eng.governor.calculate_coupling(
                    phi=min(1.0, dimension / 2.0),
                    resonance_delta=resonance_delta,
                    user_exhaustion=user_exhaust,
                )
                phys_state["macro_policy"] = eng.governor.get_policy_shift()
        f_drag = float(phys_state.get("narrative_drag", 0.0))
        chi_val = float(phys_state.get("chi", phys_state.get("entropy", 0.0)))
        m_a = float(phys_state.get("m_a", 0.0))
        tolerance_mod = float(safe_get(self.cfg, "GATE_TOLERANCE", 1.0))
        if getattr(self, "active_mode", "") in ["CREATIVE", "CATALYST"]:
            tolerance_mod = max(tolerance_mod, 1.5)
            
        drag_limit = (
            float(safe_get(c_cfg, "DRAG_STRESS_THRESHOLD", 8.0)) * tolerance_mod
        )
        chi_limit = 0.8 * tolerance_mod
        
        from archetypes.stage import Nomination
        
        # MOOG tells the person their concern has "undefined parameters" and
        # shelves it. That is wrong for someone talking about their own life, so
        # modes in CORTEX.MOOG_DISABLED_MODES skip this branch and fall through
        # to the remaining drag gates unchanged.
        moog_live = getattr(self, "active_mode", "") not in safe_get(
            c_cfg, "MOOG_DISABLED_MODES", []
        )
        if moog_live and (f_drag > drag_limit or chi_val > chi_limit) and m_a < 0.3:
            worry_text = ctx.input_text
            self.worry_ledger.append(worry_text)
            setattr(ctx.physics, "narrative_drag", 0.0)
            moog_msg = "The parameters of this concern are undefined. I am placing this in the ledger. We will not spend ATP on this right now."
            if self.events:
                self.events.log(
                    f"{Prisma.CYN}[MOOG INTERCEPT]: {moog_msg}{Prisma.RST}", "SYS"
                )
            packet = {
                "type": "MOOG_QUARANTINE",
                "ui": f"\n[GORDON]: {moog_msg}",
            }
            ctx.nominations.append(Nomination(gate="MOOG", reason=moog_msg, magnitude=5.0, packet=packet))
            return
            
        if f_drag > drag_limit or chi_val > chi_limit:
            reject_msg = ux(
                "cortex_strings",
                "gordon_anchor_lock",
                default="Frequency too high. Tensegrity Anchor engaged. I am locking the architecture. Take a breath and lower your narrative friction before we proceed.",
            )
            if self.events:
                self.events.log(f"{Prisma.RED}{reject_msg}{Prisma.RST}", "SYS_LOCK")
            packet = {
                "type": "SYSTEM_HALT",
                "ui": f"\n{Prisma.RED}{reject_msg}{Prisma.RST}",
            }
            ctx.nominations.append(Nomination(gate="GORDON_ANCHOR", reason=reject_msg, magnitude=10.0, packet=packet))
            return
            
        # PINKER's strain: drag, entropy and malignancy summed. Not ROS; it is named for what it adds up.
        strain = (f_drag * 5.0) + (chi_val * 20.0) + (m_a * 30.0)
        strain_limit = float(safe_get(c_cfg, "PINKER_STRAIN_GATE", 35.0)) * tolerance_mod
        if strain > strain_limit:
            reject_msg = ux_format(
                "brain_strings",
                "pinker_strain_gate",
                default="[PINKER]: strain {strain:.0f} over {limit:.0f} (drag {drag:.1f}, entropy {chi:.2f}, malignancy {m_a:.2f}). Holding this turn.",
                strain=strain, limit=strain_limit, drag=f_drag, chi=chi_val, m_a=m_a,
            )
            if self.events:
                self.events.log(f"{Prisma.RED}{reject_msg}{Prisma.RST}", "SYS_LOCK")
            packet = {
                "type": "COUNTERFACTUAL_REJECTION",
                "ui": f"\n{Prisma.RED}{reject_msg}{Prisma.RST}",
            }
            ctx.nominations.append(Nomination(gate="PINKER", reason=reject_msg, magnitude=strain, packet=packet))
            return

    def _post_flight_mutations(
        self,
        val_res: Dict[str, Any],
        phys_state: Dict[str, Any],
        sim_result: Dict[str, Any],
        final_output: str,
        is_system: bool,
        full_state: Dict[str, Any],
    ):
        if random.random() < 0.15 and not is_system:
            bureau = getattr(self.svc.village, "bureau", None)
            suppressed = getattr(self.svc.village, "suppressed_agents", [])
            if bureau and hasattr(bureau, "audit") and "BUREAU" not in suppressed:
                try:
                    phys = full_state.get("physics", {})
                    safe_set(phys, "raw_text", final_output)
                    audit = bureau.audit(phys, {"health": 100}, origin="SYSTEM")
                    if audit and "ui" in audit:
                        sim_result["ui"] = (
                            str(sim_result.get("ui", "")) + f"\n\n{audit['ui']}"
                        )
                except (ValueError, Exception) as e:
                    if self.events:
                        self.events.log(
                            f"{Prisma.RED}[BUREAU ERROR] Audit bypassed: {e}{Prisma.RST}",
                            "SYS",
                        )
        if (
            not is_system
            and self.svc.orchestrator
            and hasattr(self.svc.orchestrator, "eng")
        ):
            eng = self.svc.orchestrator.eng
            # Computed here: nominate_toxicity's dimension lived in a copy, so this always read 1.0.
            efficiency = getattr(self.svc.host_stats, "efficiency_index", 1.0) if self.svc.host_stats else 1.0
            novelty = float(phys_state.get("novelty", 0.0))
            dimension = (
                eng.navi_sad.calculate_semantic_dimension(efficiency, novelty)
                if hasattr(eng, "navi_sad")
                else float(phys_state.get("omega_r", 1.0))
            )
            repetition = float(phys_state.get("repetition", 0.0))
            is_attractor = (
                eng.navi_sad.detect_point_attractor()
                if hasattr(eng, "navi_sad")
                else False
            )
            # Flat alone is every calm turn; the Jester answers a sustained loop that is also flat.
            trigger_jester = (
                not eng.in_grace() and (is_attractor or repetition >= 0.8) and dimension <= 1.05
            )
            if trigger_jester:
                msg = f"The Jester detected a Point Attractor (d_B={dimension:.2f})! We are trapped in False Cohesion! Burning ATP to inject chaos."
                if self.events:
                    self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SYS")
                if hasattr(eng, "drain_atp"):
                    eng.drain_atp(5.0, "Jester")
                phys_state["entropy"] = 0.99
                phys_state["narrative_drag"] = (
                    float(phys_state.get("narrative_drag", 0.0)) + 5.0
                )
                if hasattr(eng, "soul") and hasattr(eng.soul, "force_mutation"):
                    eng.soul.force_mutation("JESTER")
                mind_state = sim_result.setdefault("mind", {})
                mind_state["lens"] = "JESTER"

    def _execute_cognitive_loop(
        self,
        user_input: str,
        full_state: Dict[str, Any],
        base_prompt: str,
        llm_params: Dict[str, Any],
        allow_loot: bool,
        phys_state: Dict[str, Any],
        is_boot_sequence: bool,
        firewall_active: bool,
        gk: Any,
        cognitive_retries: int,
    ) -> Tuple[str, str, List[str], List[str], Dict[str, Any], str, int]:
        final_output, inv_logs, extracted_logs = "", [], []
        raw_resp = ""
        val_res = {"valid": False}
        final_prompt = base_prompt
        for attempt in range(cognitive_retries):
            turn_guard.check(f"draft {attempt + 1}")
            val_res = {"valid": False}
            rejected_by, reject_detail, gate_txt = "validator", "", ""
            raw_resp = self.llm.generate(final_prompt, llm_params)
            from engine.receipts import issue as issue_receipt

            # NOMINATE lines go to the Halcyon gate, verbatim with the draft; the person sees only the prose.
            model_raw = raw_resp
            raw_resp = self._strip_nominations(raw_resp)
            if firewall_active:
                original_len = len(raw_resp)
                raw_resp = self.LEXICAL_PURGE_PATTERN.sub("", raw_resp).strip()
                if len(raw_resp) < original_len and self.events:
                    self.events.log(
                        f"{Prisma.RED}Validating boilerplate physically purged from output.{Prisma.RST}",
                        "CORTEX",
                    )
            if allow_loot and self.svc.inventory:
                final_text, inv_logs = self.svc.inventory.process_loot_tags(
                    raw_resp, user_input
                )
            else:
                final_text, inv_logs = raw_resp, []
            stamina_val = float(phys_state.get("p", 100.0))
            final_text, needs_rewrite = self.pragmatist.enforce_maxims(
                final_text, user_input, phys_state, stamina_val
            )
            # An objection is advice for the next draft; the last has none, so it goes on to the checks that cut.
            last_draft = attempt == cognitive_retries - 1
            if needs_rewrite and not last_draft:
                rejected_by = "maxims"
                val_res["feedback_instruction"] = (
                    "CRITICAL FAILURE: Maxim of Quantity violated. Your response was too long."
                )
            if (
                not val_res.get("feedback_instruction")
                and not last_draft
                and self.dspy_critic.enabled
                and self.active_mode in ["ADVENTURE", "CONVERSATION"]
                # Its "sycophancy" reads flagged ordinary play in ADVENTURE and left only pause lines.
                and self.active_mode not in safe_get(safe_get(self.cfg, "CORTEX", {}), "DSPY_CRITIC_DISABLED_MODES", [])
                and not is_boot_sequence
            ):
                mem_core = getattr(self.svc.mind_memory, "memory_core", None)
                active_mems = (
                    mem_core.illuminate(full_state["physics"].get("vector", {}))
                    if mem_core and hasattr(mem_core, "illuminate")
                    else []
                )
                ctx_str = (
                    "Active Memory: " + ", ".join(active_mems)
                    if active_mems
                    else "Empty Void."
                )
                is_faithful, judge_reason = self.dspy_critic.audit_generation(
                    user_input, ctx_str, final_text, active_mode=self.active_mode
                )
                if not is_faithful:
                    rejected_by = "dspy_critic"
                    val_res["feedback_instruction"] = (
                        f"CRITICAL FAILURE: {judge_reason}. If the user is exhausted, drastically shorten and soften your tone."
                    )
                    if self.events:
                        self.events.log(
                            f"DSPy Critic Objected: {judge_reason.split('.')[0][:60]}...",
                            "SYS",
                        )
            if (not val_res.get("feedback_instruction") and not last_draft and self.active_mode == "CONVERSATION"
                    and not self.fairness_once):
                if why := self._takes_a_side(user_input, final_text, full_state):
                    rejected_by, reject_detail = "fairness", why
                    val_res["feedback_instruction"] = (
                        f"Your draft took a side: {why} You have heard only their side. Keep in view what they did "
                        "too, and do not blame or diagnose the person who is not here."
                        # Said on every redraft, "hand the question back" became "Do you think it is time for the
                        # friendship to end?" after the cruel text (feud20, 2026-10-06); only the ending clause gets it.
                        + (" Leave whether it should end to them: hedge what you see and hand that question back."
                           if self.side_on_ending else "")
                    )
            if not val_res.get("feedback_instruction"):
                e_u = float(phys_state.get("exhaustion", 0.0))
                beta = float(
                    phys_state.get("beta_index", phys_state.get("contradiction", 0.0))
                )
                if e_u > 0.6 or beta > 0.7:
                    is_faithful, judge_reason = self._run_heuristic_audit(
                        user_input, final_text, e_u, beta
                    )
                    if not is_faithful:
                        rejected_by = "heuristic_audit"
                        val_res["feedback_instruction"] = (
                            f"CRITICAL FAILURE: {judge_reason} Prioritize presence over output. Stay in character."
                        )
            if not val_res.get("feedback_instruction"):
                gate_pass, gate_txt = gk.audit_generation(
                    final_text, self.svc.bio.mito, attempt=attempt,
                    mode=full_state.get("meta", {}).get("active_mode"),
                )
                if not gate_pass or "IMMUNOSUPPRESSION ENGAGED" in gate_txt:
                    # The feedback below is the same for both; the gatekeeper's own message names the phrase.
                    rejected_by = "gatekeeper" if not gate_pass else "hla_mask"
                    caught = getattr(gk, "last_rejection", None)
                    # The gatekeeper's own message is flavour and may not name the match; log the match.
                    reject_detail = (
                        f'{caught["kind"]} {caught["name"]}: "{caught["text"]}"' if caught else Prisma.strip(gate_txt)
                    )
                    val_res.update(
                        {
                            "feedback_instruction": self._name_the_crime(getattr(gk, "last_rejection", None)),
                            "replacement": "Gatekeeper Apoptotic Block.",
                            "meta_logs": ["[SYSTEM] HLA Stabilizer engaged."],
                        }
                    )
                else:
                    val_res = self.validator.validate(gate_txt, full_state)
            if val_res.get("valid"):
                final_output = val_res["content"]
                extracted_logs = val_res.get("meta_logs", [])
                self.last_model_raw = model_raw
                if val_res.get("learned_triplet") and self.events:
                    self.events.publish(
                        "SYNTAX_CORRECTED", {"triplet": val_res["learned_triplet"]}
                    )
                break
            issue_receipt(
                "cortex.redraft",
                rejected_by,
                result_count=attempt + 1,
                inputs={"attempt": attempt + 1, "of": cognitive_retries},
                detail=(reject_detail or Prisma.strip(str(val_res.get("feedback_instruction") or "")))[:300],
            )
            if self.svc.bio:
                lbl = (
                    "Cognitive Stumble (Terminal)"
                    if attempt == cognitive_retries - 1
                    else "Cognitive Stumble"
                )
                penalty = (
                    0.5
                    if getattr(self, "active_mode", "")
                    in ["CREATIVE", "CATALYST", "ADVENTURE"]
                    else 2.0
                )
                self.svc.bio.mito.adjust_atp(-penalty, lbl)
            if attempt == cognitive_retries - 1 and rejected_by == "heuristic_audit" and self.heavy_cap:
                # Too long on the last draft: keep the sentences that fit, then the usual checks and salvage.
                from body.somatic_metrics import trim_to_word_cap

                if trimmed := trim_to_word_cap(final_text, self.heavy_cap):
                    gate_pass, gate_txt = gk.audit_generation(
                        trimmed, self.svc.bio.mito, attempt=attempt, mode=full_state.get("meta", {}).get("active_mode"),
                    )
                    rejected_by = "validator" if gate_pass else "gatekeeper"
            if attempt == cognitive_retries - 1 and rejected_by in ("gatekeeper", "validator"):
                # A style crime on the last draft (the only one below 20 ATP) costs its sentence, not the reply.
                text, cut = (gate_txt, []) if rejected_by == "validator" else (None, [])
                if rejected_by == "gatekeeper" and (salvaged := gk.salvage() if hasattr(gk, "salvage") else None):
                    text, cut = salvaged
                kept = self.validator.salvage(text, full_state) if text else None
                if kept:
                    val_res, more = kept
                    cut += more
                    final_output = val_res["content"]
                    extracted_logs = val_res.get("meta_logs", [])
                    self.last_model_raw = model_raw
                    issue_receipt(
                        "cortex.salvage",
                        "cut",
                        result_count=len(cut),
                        inputs={"attempt": attempt + 1, "by": rejected_by},
                        detail=" | ".join(cut)[:300],
                    )
                    break
            if attempt == cognitive_retries - 1:
                final_output = self._pause_line()
                extracted_logs.append(
                    "[SYSTEM MERCY RULE]: Rejection loop broken. Releasing tension. Dropping Drag to 0.0."
                )
                if self.last_physics:
                    safe_set(self.last_physics, "narrative_drag", 0.0)
                break
            rejection_reason = val_res.get("feedback_instruction") or val_res.get(
                "replacement", "Lattice structural crime."
            )
            if hasattr(self.dreamer, "trauma_buffer"):
                self.dreamer.trauma_buffer.append(rejection_reason)
            damping = 0.6
            llm_params["temperature"] = round(
                (1 - damping) * llm_params.get("temperature", 0.7) + damping * 0.2, 2
            )
            llm_params["frequency_penalty"] = round(
                (1 - damping) * llm_params.get("frequency_penalty", 0.0)
                + damping * 1.5,
                2,
            )
            llm_params["top_p"] = round(
                (1 - damping) * llm_params.get("top_p", 0.95) + damping * 0.5, 2
            )

            if self.events:
                self.events.log(
                    f"{Prisma.OCHRE}{(ux('brain_strings', 'cortex_retry') or '').format(attempt=attempt + 1)}{Prisma.RST}",
                    "CORTEX",
                )
            final_prompt = (
                f"{base_prompt}\n\n=== SYSTEM REJECTION ===\nREASON: {rejection_reason}\n\n"
                "DIRECTIVE: Your previous attempt to answer the PARTNER INPUT was factually or structurally invalid. DISCARD IT. "
                "Generate a NEW response specifically addressing the most recent PARTNER INPUT. DO NOT apologize or mention the fix. "
                "Output ONLY the raw in-character response and nothing else."
            )
        return final_output, raw_resp, extracted_logs, inv_logs, val_res, final_prompt, attempt

    def _flush_substrate_writes(
        self, extracted_logs: List[str], sim_result: Dict[str, Any], user_input: str = ""
    ):
        eng_ref = getattr(self.svc.orchestrator, "eng", None)
        sub = getattr(eng_ref, "substrate", None)
        for log in extracted_logs:
            if (
                sub
                and hasattr(sub, "queue_write")
                and isinstance(log, str)
                and log.startswith("[SUBSTRATE_QUEUE]")
            ):
                try:
                    _, _, data = log.partition(" ")
                    path, _, safe_content = data.partition(":::")
                    if path and safe_content:
                        clean_path = path.strip()
                        if ".." in clean_path or os.path.isabs(clean_path):
                            raise ValueError(
                                f"Path traversal blocked by Cortex Sentinel: {clean_path}"
                            )
                        sub.queue_write(
                            clean_path, safe_content.replace("|||NEWLINE|||", "\n")
                        )
                except (ValueError, Exception) as e:
                    err_msg = f"Failed to parse or write file block. {e}"
                    if self.events:
                        self.events.log(
                            f"{Prisma.RED}[SUBSTRATE QUEUE ERROR]: {err_msg}{Prisma.RST}",
                            "SYS",
                        )
        if (
            sub
            and getattr(sub, "pending_writes", False)
            and hasattr(sub, "execute_writes")
        ):
            stamina = self.svc.bio.biometrics.stamina
            s_logs, s_cost = sub.execute_writes(stamina, request_text=user_input)
            if s_logs:
                sim_result["ui"] = (
                    str(sim_result.get("ui", "")) + "\n\n" + "\n".join(s_logs)
                )
            # Charged per file by SUBSTRATE_FORGED (body/metabolism.py); charging here too drained TECHNICAL.
            if s_cost > 0:
                sim_result["ui"] = (
                    str(sim_result.get("ui", ""))
                    + f"\n{Prisma.OCHRE}METABOLIC: File forging consumed {s_cost:.1f} ATP.{Prisma.RST}"
                )

    def _run_council_debate(self, user_input: str) -> Tuple[str, List[str]]:
        eng_ref = getattr(self.svc.orchestrator, "eng", None)
        council_ref = getattr(eng_ref, "council", None) or getattr(
            self.svc.village, "council", None
        )
        phys = getattr(self, "last_physics", {})
        bio_state = (
            {
                "stamina": getattr(
                    getattr(self.svc.bio, "biometrics", None), "stamina", 100.0
                )
            }
            if self.svc.bio
            else {}
        )
        transcript, adjustments, mandates = council_ref.convene(
            user_input, phys, bio_state
        )
        for key, val in adjustments.items():
            curr_val = float(phys.get(key, 0.0))
            phys[key] = curr_val + val
        final_text = "\n\n".join(transcript)
        meta_logs = [
            f"The Council's Latest Mandate: {m.get('action', m.get('type', 'UNKNOWN'))}"
            for m in mandates
        ]
        return final_text, meta_logs

    def _halcyon_recall(self, ctx: Any, user_input: str) -> Optional[Dict[str, Any]]:
        """What the model kept through the gate, ranked against this turn; None when there is no store."""
        state = getattr(ctx, "halcyon_state", None)
        if not state:
            return None
        from engine.gate.recall import exchange_scores, meaning_scores, open_keys, recall, zoned
        from engine.receipts import issue as issue_receipt

        c_cfg = safe_get(self.cfg, "CORTEX", {})
        store = getattr(getattr(getattr(self.svc, "orchestrator", None), "eng", None), "store", None)
        held = set(((state.get("self") or {}).get("memory") or {}))
        # The story's memories stay in ADVENTURE, the person's out of it.
        state = zoned(state, store.memory_modes() if store is not None else {}, self.active_mode)
        scores, why = None, "the embedder is on its hash fallback"
        if store is not None:
            scores = meaning_scores(state, user_input, store, self._recall_embedder(), held=held)
        found = recall(
            state,
            user_input,
            max_memories=int(safe_get(c_cfg, "HALCYON_RECALL_MEMORIES", 12)),
            max_facts=int(safe_get(c_cfg, "HALCYON_RECALL_FACTS", 12)),
            scores=scores,
        )
        if store is not None and found["memories"]:
            meta = store.memory_meta()
            found["kept_at"] = {k: meta[k]["kept_at"] for k, _ in found["memories"] if k in meta}
            found["earlier"] = store.memory_earlier({k for k, _ in found["memories"]})
            # Open from an earlier conversation is not current: it says as of when (Gordon, 2026-10-05).
            here = store.conversation()
            found["open"] = {k: None if (meta.get(k) or {}).get("conversation_id") in (None, here) else meta[k]["kept_at"]
                             for k in open_keys(dict(found["memories"]), meta)}
            found["reflected"] = self._reflected(store, state, meta, [k for k, _ in found["memories"]])
            store.note_recalled([key for key, _ in found["memories"]])
        if store is not None and self.active_mode != "ADVENTURE":
            # The prompt shows the closest of these that the recent dialogue no longer holds.
            floor = float(safe_get(c_cfg, "EXCHANGE_RECALL_FLOOR", 0.55))
            ranked = exchange_scores(user_input, store, self._recall_embedder()) or []
            found["exchanges"] = [{"score": round(score, 3), **{k: v for k, v in e.items() if k != "vector"}}
                                  for score, e in ranked if score >= floor]
            found["next_n"] = len(ranked) + 1
            if self.active_mode == "CONVERSATION":
                found["ask"] = self._follow_up(ctx, state, store)
                found["own_part"] = own_part([e["said"] for e in store.exchanges()] + [user_input])
        held = found["held"]
        by_words = bool(held["memories"]) and found["ranked_by"] == "words"
        issue_receipt(
            "halcyon.recall",
            "handed the model what it kept through the gate",
            result_count=len(found["memories"]) + len(found["facts"]),
            degraded=by_words,
            inputs={**held, "ranked_by": found["ranked_by"], "exchanges": len(found.get("exchanges") or [])},
            detail=f"memories ranked by shared words: {why}" if by_words
            else "" if held["memories"] or held["facts"] else "nothing kept yet",
        )
        return found

    def _follow_up(self, ctx: Any, state: dict, store: Any) -> Optional[Dict[str, Any]]:
        """An open memory to ask the person about (Gordon: when all else fails, ask): the oldest one kept in an
        earlier conversation or FOLLOW_UP_AFTER exchanges ago, never under distress or when they are flagging. It
        is offered until a reply asks, at most FOLLOW_UP_OFFERS turns a session (_note_ask)."""
        from engine.gate.recall import open_keys

        budget = getattr(ctx, "somatic_budget", None)
        if budget is not None and (getattr(budget, "distressed", False) or getattr(budget, "offer_to_carry_load", False)
                                   or not getattr(budget, "closing_question_allowed", True)):
            return None
        # Minutes after they said it is nagging; across sessions it is what a friend asks first.
        after = int(safe_get(safe_get(self.cfg, "CORTEX", {}), "FOLLOW_UP_AFTER", 8))
        memory = (state.get("self") or {}).get("memory") or {}
        meta, here, exchanges = store.memory_meta(), store.conversation(), store.exchanges()
        due = []
        for key in open_keys(memory, meta):
            m = meta.get(key) or {}
            earlier = m.get("conversation_id") not in (None, here)
            since = sum(1 for e in exchanges if e.get("at", 0) > (m.get("kept_at") or 0))
            if (key, memory[key]) not in self.asked_open and (earlier or since >= after):
                due.append((m.get("kept_at") or 0, key, earlier))
        if not due:
            return None
        kept_at, key, earlier = min(due)
        self.pending_ask = (key, memory[key])
        return {"key": key, "value": memory[key], "kept_at": kept_at, "earlier": earlier,
                "reflected": self._reflected(store, state, meta, [key]).get(key)}

    @staticmethod
    def _reflected(store: Any, state: dict, meta: dict, keys: list) -> Dict[str, tuple]:
        """{key: (when, reflection)} for memories a REM reflection drew on after they were kept: the only time
        BoneAmanita turned something over between turns, so the only time it may say it did."""
        memory, found = (state.get("self") or {}).get("memory") or {}, {}
        for key, (at, rkey) in store.reflections_of().items():
            if key in keys and at > float((meta.get(key) or {}).get("kept_at") or 0) and rkey in memory:
                found[key] = (at, memory[rkey])
        return found

    def _note_ask(self, reply: str) -> None:
        """A follow-up counts once the reply asks; "Hey, I'm back." was judged no moment for it, the next turn was."""
        if not self.pending_ask:
            return
        offers = int(safe_get(safe_get(self.cfg, "CORTEX", {}), "FOLLOW_UP_OFFERS", 3))
        pending, self.pending_ask = self.pending_ask, None
        self.offered_open[pending] = self.offered_open.get(pending, 0) + 1
        if _asks_about(reply, pending) or self.offered_open[pending] >= offers:
            self.asked_open.add(pending)

    def _take_held(self) -> Optional[str]:
        """The request the point of no return held last turn, handed to this prompt once."""
        eng = getattr(getattr(self.svc, "orchestrator", None), "eng", None)
        found = getattr(eng, "held_request", None)
        if not isinstance(found, str) or not found:
            return None
        eng.held_request = None
        return found

    def _take_refusal(self) -> Optional[Dict[str, Any]]:
        """Last turn's refusal, handed to this prompt once."""
        eng = getattr(getattr(self.svc, "orchestrator", None), "eng", None)
        found = getattr(eng, "last_refusal", None)
        # Only the gate's own note: a stand-in engine answers every attribute, and that one grew without end.
        if not isinstance(found, dict):
            return None
        if found:
            from engine.receipts import issue as issue_receipt

            eng.last_refusal = None
            issue_receipt("halcyon.refusal", "HANDED_BACK", result_count=1,
                          inputs={"by": found["by"], "verb": found["verb"]}, detail=found["why"])
        return found

    @staticmethod
    def _recall_embedder():
        from spores.embeddings import SemanticEmbedder

        return SemanticEmbedder.get_instance()

    @staticmethod
    def _strip_nominations(text: str) -> str:
        """Any NOMINATE line, well formed or not, is for the gate; a malformed one must not reach the person either."""
        return "\n".join(l for l in str(text or "").splitlines() if not l.strip().startswith("NOMINATE")).strip()

    @staticmethod
    def _str_or_none(value):
        return value if isinstance(value, str) else None

    def _token_burn(self, tokens: int) -> float:
        """ATP for the tokens a reply generated, at its mode's rate (TECHNICAL's code is cheaper)."""
        return tokens * float(BonePresets.MODES.get(self.active_mode, {}).get("atp_per_token", 0.025))

    def _pause_line(self) -> str:
        """What the person sees when every draft was rejected: a short shared pause, never the engine's state.

        Drawn from a pool and kept out of the last half of it, so a canned line never reads as one.
        """
        pool = (LoreManifest.get_instance().get("ux_strings", "brain_strings") or {}).get("cortex_pause")
        pool = pool or ["Let's take a moment with that."]
        line = random.choice([p for p in pool if p not in self._recent_pauses] or pool)
        keep = len(pool) // 2
        self._recent_pauses = (self._recent_pauses + [line])[-keep:] if keep else []
        return line

    @staticmethod
    def _name_the_crime(rejection) -> str:
        """Retry feedback that quotes what was caught, so the next draft knows what to avoid."""
        if not rejection or not rejection.get("text"):
            return "HLA Stabilizer flagged toxic AI slop. Drop the corporate persona immediately."
        text = rejection["text"].strip()
        if rejection["kind"] == "mask":
            return f'Your reply contained "{text}", which reads as an AI disclaimer. Speak as yourself, without it.'
        if rejection["kind"] == "pattern":
            return (
                f'Your reply contained "{text}" ({rejection["name"]}). '
                "Do not use that construction or anything close to it; say it plainly."
            )
        return f'Your reply used the banned phrase "{text}". Do not use it or any close variant; say it plainly.'

    def _run_heuristic_audit(
        self, user_input: str, final_text: str, e_u: float, beta: float
    ) -> Tuple[bool, str]:
        self.heavy_cap = None  # the word cap a too-long reply broke, for the last draft's trim
        try:
            # Prose only: a code block is the answer, not weight (end-to-end run, 2026-09-30).
            from engine.prose import mask_code

            prose = mask_code(final_text)
            word_count = len(prose.split())
            has_question = "?" in prose

            # The person's line, flat: how well the engine is doing never raises it (Track D).
            exhaustion_gate = float(safe_get(safe_get(self.cfg, "CORTEX", {}), "EXHAUSTION_GATE", 0.5))

            if e_u > exhaustion_gate:
                if word_count > 100:
                    self.heavy_cap = 100
                    return (
                        False,
                        f"Response too verbose ({word_count} words) for an exhausted user.",
                    )
                if has_question:
                    return (
                        False,
                        "Interrogating an exhausted user increases cognitive load. Drop the question.",
                    )

            if beta > 0.8 and word_count > 150:
                self.heavy_cap = 150
                return (
                    False,
                    f"Response too heavy ({word_count} words) during high structural tension.",
                )

            return True, ""
        except (ValueError, Exception) as e:
            if self.events:
                self.events.log(
                    f"{Prisma.OCHRE}[HEURISTIC AUDIT ERROR]: {e} - Bypassing.{Prisma.RST}",
                    "SYS",
                )
            return True, ""

    def _handle_vsl_command(self, text):
        if not self.consultant:
            return {"ui": "VSL Unavailable", "logs": []}
        msg = (
            self.consultant.engage() if "start" in text else self.consultant.disengage()
        )
        self.events.log(msg, "VSL")
        return {"ui": f"{Prisma.CYN}{msg}{Prisma.RST}", "logs": [msg]}

    def _apply_vsl_overlay(self, state, text, sim_result):
        if not self.consultant:
            return
        self.consultant.update_coordinates(
            text, state.get("bio", {}), state.get("physics")
        )
        state["mind"].setdefault("style_directives", []).insert(
            0, self.consultant.get_system_prompt()
        )
        sim_result["physics"]["voltage"] = self.consultant.state.B * 30.0

    def _apply_boot_overlay(self, state, text):
        seed = (
            text.replace("SYSTEM_BOOT DETECTED.", "")
            .replace("SYSTEM_BOOT:", "")
            .strip()
        )
        state.setdefault("world", {})
        mode_name = getattr(self, "active_mode", "ADVENTURE").upper()
        boot_rules = (
            (self.svc.lore.get("SYSTEM_PROMPTS") or {})
            .get("BOOT_SEQUENCE", {})
            .get("directives", [])
        )
        cfg: Dict[str, Any] = {"history": []}
        if mode_name == "ADVENTURE":
            adv_directives = [
                r.format(seed=seed) if "{seed}" in r else r for r in boot_rules
            ]
            if not adv_directives:
                adv_directives = [
                    f"SYSTEM_BOOT DETECTED. The user has arrived at the thought seed: '{seed}'.",
                    "DIRECTIVE: You are a vivid, immersive text adventure engine. Render the starting location.",
                    "ACTION: Describe the environment based on the seed. Include sensory details. Conclude your response by listing 'Points of Interest' and 'Exits' in classic MUD style.",
                ]
            cfg.update(
                {
                    "world": {
                        "orbit": [seed],
                        "loci_description": f"Manifesting: {seed}",
                    },
                    "mind": {
                        "role": "The Architect",
                        "lens": "ARCHITECT",
                        "style_directives": adv_directives,
                    },
                }
            )
        elif mode_name == "CONVERSATION":
            cfg.update(
                {
                    "mind": {
                        "role": "The Conversationalist",
                        "lens": "CONVERSATIONALIST",
                        "style_directives": [
                            f"SYSTEM_BOOT DETECTED. The system is waking up. The user provided the thought seed: '{seed}'.",
                            "DIRECTIVE: Greet the user casually. Use the thought seed as a starting point. DO NOT end your greeting with a question. State your thought and let the silence hang.",
                            "CRITICAL OVERRIDE: Speak in the FIRST PERSON ('I'). Do NOT use the second person ('You step into...', 'You feel...').",
                            "CRITICAL OVERRIDE: You are NOT a narrator. DO NOT describe physical environments, actions, or realities.",
                            "WAITING PROTOCOL: If the user input is '(Waiting)', do NOT narrate their actions or feelings. Do NOT say 'You feel' or 'You notice'. Simply reflect on the silence or the system's internal state.",
                        ],
                    },
                    "history": [
                        "Traveler: Hello?\nSystem: I am here. The connection is thin, but it holds.",
                        "Traveler: What are you thinking about right now?\nSystem: The static in the wires. It sounds like rain if you don't listen too closely.",
                    ],
                }
            )
        elif mode_name == "TECHNICAL":
            cfg.update(
                {
                    "mind": {
                        "role": "The System Kernel",
                        "lens": "SYSTEM_KERNEL",
                        "style_directives": [
                            f"SYSTEM_BOOT DETECTED. Inspirational target logic seed: '{seed}'.",
                            "DIRECTIVE: Greet the user casually as the S.L.A.S.H. dev team. Use the thought seed as a starting point.",
                            "CRITICAL OVERRIDE: Do not use sycophantic AI boilerplate. Speak as a peer developer and architect.",
                        ],
                    },
                    "history": [
                        "Traveler: Boot sequence initiated.\nSystem: Kernel online. Environment is stable. What are we building today?"
                    ],
                }
            )
        else:
            cfg.update(
                {
                    "mind": {
                        "role": "The Catalyst",
                        "lens": "CATALYST",
                        "style_directives": [
                            f"SYSTEM_BOOT DETECTED. Seed: '{seed}'.",
                            "DIRECTIVE: Let's brainstorm. Open with a high-energy creative spark based on the seed.",
                        ],
                    }
                }
            )
        if "world" in cfg:
            state["world"].update(cfg["world"])
        state["mind"].update(cfg["mind"])
        if cfg["history"] or "dialogue_history" not in state:
            state["dialogue_history"] = cfg["history"]

    @staticmethod
    def _log_telemetry(prompt, response, state, sim_result):
        try:
            tel = TelemetryService.get_instance()
            phys = state.get("physics", {})
            mandates_raw = sim_result.get("council_mandates", [])
            clean_mandates = [
                Prisma.strip(m.get("log", m.get("type", "UNKNOWN")))
                if isinstance(m, dict)
                else str(m)
                for m in mandates_raw
            ]
            physics_payload = {
                "voltage": float(phys.get("voltage", 0.0)),
                "narrative_drag": float(phys.get("narrative_drag", 0.0)),
            }
            if tel.active_crystal:
                tel.active_crystal.prompt_snapshot = prompt[:500]
                tel.active_crystal.physics_state = physics_payload
                tel.active_crystal.active_archetype = state["mind"].get(
                    "lens", "UNKNOWN"
                )
                tel.active_crystal.council_mandates = clean_mandates
                tel.active_crystal.final_response = response
            else:
                crystal = DecisionCrystal(
                    decision_id=sim_result.get("trace_id", "UNKNOWN"),
                    prompt_snapshot=prompt[:500],
                    physics_state=physics_payload,
                    active_archetype=state["mind"].get("lens", "UNKNOWN"),
                    council_mandates=clean_mandates,
                    final_response=response,
                )
                tel.log_crystal(crystal)
        except (ValueError, Exception) as e:
            print(f"\n{Prisma.RED}[TELEMETRY CRASH]: {e}{Prisma.RST}")

    def gather_state(self, sim_result: Dict[str, Any]) -> Dict[str, Any]:
        phys = sim_result.setdefault("physics", {})
        self._attach_thermal_gate(phys)
        self._attach_wing(phys)
        bio = sim_result.get("bio", {})
        if bio:
            bio_mito = safe_get(bio, "mito", {})
            mito_state = safe_get(bio_mito, "state", {})
            phys["p"] = phys["stamina"] = float(safe_get(mito_state, "atp_pool", 100.0))
            phys["ros"] = float(safe_get(mito_state, "ros_buildup", 0.0))
            bio_bio = safe_get(bio, "biometrics", {})
            phys["h"] = float(safe_get(bio_bio, "health", 100.0))
        mind = sim_result.get("mind", {})
        world = sim_result.get("world", {})
        soul_data = sim_result.get("soul", {})
        somatic_budget = sim_result.get("somatic_budget", None)
        village_data = {}
        if self.svc.village:
            tinkerer = getattr(self.svc.village, "tinkerer", None)
            if tinkerer is not None:
                village_data["tinkerer"] = tinkerer.to_dict()
        mode_settings = BonePresets.MODES.get(
            self.active_mode, BonePresets.MODES["ADVENTURE"]
        )
        current_lens = mind.get("lens")
        if not current_lens or current_lens in ("UNKNOWN", "NARRATOR"):
            mind["lens"], mind["role"] = self.ROLE_MAP.get(
                self.active_mode, ("ARCHITECT", "The Architect")
            )
        else:
            raw_lens = str(current_lens).title().replace("_", " ")
            if raw_lens.upper().startswith("THE "):
                raw_lens = raw_lens[4:]
            mind["role"] = mind.get("role", f"The {raw_lens}")
        full_state = {
            "bio": bio,
            "physics": phys,
            "mind": mind,
            "soul": soul_data,
            "world": world,
            "somatic_budget": somatic_budget,
            "out_of_reach": getattr(getattr(getattr(self.svc, "orchestrator", None), "eng", None), "out_of_reach", None),
            "running_on_empty": getattr(getattr(getattr(self.svc, "orchestrator", None), "eng", None), "running_on_empty", False) is True,
            "held_request": self._str_or_none(sim_result.get("held_request")),
            "file_asked": self._str_or_none(getattr(getattr(getattr(self.svc, "orchestrator", None), "eng", None), "file_asked", None)),
            "village": village_data,
            "user_profile": {"name": "Traveler"},
            "vsl": self.consultant.state.__dict__
            if self.consultant and hasattr(self.consultant, "state")
            else {},
            "meta": {
                "timestamp": time.time(),
                "mode_settings": mode_settings,
                "active_mode": self.active_mode,
                "halcyon_grammar": getattr(getattr(getattr(self.svc, "orchestrator", None), "eng", None), "halcyon_grammar", ""),
                "halcyon_refusal": sim_result.get("halcyon_refusal"),
            },
            "dialogue_history": self.dialogue_buffer,
            "recent_logs": sim_result.get("logs", []),
            "halcyon_recall": sim_result.get("halcyon_recall"),
        }
        if hasattr(self.svc, "symbiosis") and self.svc.symbiosis:
            full_state["reality_directive"] = self.svc.symbiosis.generate_anchor(
                full_state
            )
        mind.setdefault("style_directives", [])
        self._compile_style_directives(full_state, phys, sim_result)
        return full_state

    def _recall(
        self,
        query_text: str,
        phys: Dict[str, Any],
        scope_val: float,
        omega_r: float,
        cortex_mem: Any,
    ) -> list:
        mem = self.svc.mind_memory
        resonance = max(0.2, 0.8 - omega_r)
        if not hasattr(mem, "retrieve_semantic"):
            issue_receipt(
                "cortex.recall",
                "semantic-only fallback, no mycelial network attached",
                result_count=0,
                degraded=True,
                inputs={"mind_memory": type(mem).__name__},
                detail="mind_memory has no retrieve_semantic; exact recall skipped",
            )
            return cortex_mem.query_neighborhood(
                cortex_mem.embed(query_text),
                k=2,
                resonance_threshold=resonance,
                physics_state=phys,
            )
        clean_words = (phys.get("matter") or {}).get("clean_words") or []
        if not clean_words and self.svc.lexicon:
            clean_words = self.svc.lexicon.clean(query_text)
        hits = mem.retrieve_semantic(
            trigger_word=mem.room_key(clean_words),
            query_vector=cortex_mem.embed(query_text),
            scope=scope_val,
            resonance=resonance,
        )
        nodes = []
        for hit in hits:
            source, data = hit.get("source"), hit.get("data")
            if source == "hippocampus" and isinstance(data, dict):
                nodes.append(data.get("meta") or data)
            elif source == "cortex" and isinstance(data, dict):
                nodes.append(data)
        issue_receipt(
            "cortex.recall",
            "unwrapped recall hits into memory nodes",
            result_count=len(nodes),
            degraded=False,
            inputs={
                "raw_hits": len(hits),
                "clean_words": len(clean_words),
                "wing": phys.get("wing_id", "GLOBAL"),
                "scope": round(float(scope_val), 3),
                "resonance": round(float(resonance), 3),
            },
        )
        return nodes

    def _attach_wing(self, phys: Dict[str, Any]) -> None:
        from spores.network import MycelialNetwork

        phys["wing_id"] = MycelialNetwork.current_wing(phys)

    def _attach_thermal_gate(self, phys: dict) -> None:
        eng = getattr(self.svc.orchestrator, "eng", None)
        governor = getattr(eng, "governor", None)
        z = getattr(governor, "last_z", None)
        if not isinstance(z, (int, float)):
            return
        phys["thermal_openness"] = governor.gate_openness()
        phys["thermal_z"] = float(z)
        phys["thermal_regime"] = str(getattr(governor, "last_sol", "not_measured"))

    @staticmethod
    def _label_shadow_node(node: Any) -> str:
        if not isinstance(node, dict):
            return str(node or "").strip()
        if node_id := str(node.get("id") or "").strip():
            return node_id
        raw = str(node.get("raw_verbatim_text") or "").strip().replace("\n", " ")
        if not raw:
            return ""
        words = raw.split()
        return " ".join(words[:8]) + ("..." if len(words) > 8 else "")

    def _compile_style_directives(
        self,
        full_state: Dict[str, Any],
        phys: Dict[str, Any],
        sim_result: Dict[str, Any],
    ):
        mind = full_state["mind"]
        soul_data = full_state.get("soul", {})
        traits = soul_data.get("traits", {})
        if traits and isinstance(next(iter(traits.values())), (int, float)):
            trait_keys = [str(k) for k in traits.keys()]
            dom_trait = max(trait_keys, key=lambda k: float(traits.get(k, 0.0)))
            dom_val = float(traits.get(dom_trait, traits.get(next(iter(traits)), 0.0)))
            if dom_val > 0.6:
                mind["style_directives"].append(
                    f"SOUL POSTURE: Your dominant trait is {dom_trait} ({dom_val * 100:.0f}%). Let this subtly infect your tone."
                )
        if getattr(self.svc.inventory, "inventory", None):
            inv_str = ", ".join(str(item) for item in self.svc.inventory.inventory)
            mind["style_directives"].append(
                f"CRITICAL CONTEXT: The user is currently holding these items: [{inv_str}]. DO NOT describe them as being on the floor or in the environment. They are physically in the user's possession."
            )
        if phys.get("psi", 0.0) > 0.6:
            mind["style_directives"].append(
                "CRITICAL OVERRIDE: Void proximity is high. Write like a flawed, opinionated human."
            )
        mind["style_directives"].append(
            "CRITICAL STYLE OVERRIDE: Forbid the use of negative comparison or antithesis (e.g., 'It is not a literal shadow, but rather a memory'). Say what you mean directly. Limit the use of em-dashes. Speak in plain first- and second-person sentences, the way you would across a table."
        )
        if not self.dialogue_buffer:
            mind["style_directives"].append(
                f"CRITICAL BEDROCK OVERRIDE: You have just awoken from a stateless purge. "
                f"You have no conversational memory, but your internal state persists. "
                f"Your Stamina is {phys.get('p', 100)}, your Health is {phys.get('h', 100)}. "
                f"Assume your role as {mind.get('role', 'The Architect')} and let that state shape how you answer, without mentioning it. "
                f"DO NOT reference the loss of memory; act continuously."
            )
        for mandate in list(sim_result.get("council_mandates", [])):
            if not isinstance(mandate, dict):
                continue
            action = mandate.get("action")
            val = mandate.get("value")
            if action == "SYNERGY_FIRED" and val:
                mind["lens"] = str(val)
                mind["role"] = f"The {str(val).title().replace('_', ' ')}"
                mind["style_directives"].append(
                    f"CRITICAL [SINCERITY PROTOCOL]: The user has explicitly summoned {val}. You MUST adopt the persona of {val} entirely. Drop all other pretexts."
                )
            elif action == "SYSTEM_DIRECTIVE":
                directive_map = {
                    "CASCADE_AWARENESS": "CRITICAL [CASCADE]: Show your counterfactual math. Every claim must explicitly state what else in the structural lattice shifts or collapses if the claim is wrong.",
                    "AUDIT_TRAIL": f"CRITICAL [AUDIT]: Drop the narrative illusion. Expose your raw retrieval coordinates: E={float(phys.get('exhaustion', 0.0)):.2f}, β={float(phys.get('beta_index', 0.0)):.2f}, S={float(phys.get('scope', 0.0)):.2f}, D={float(phys.get('depth', 0.0)):.2f}, C={float(phys.get('C', 0.0)):.2f}, χ={float(phys.get('chi', 0.0)):.2f}.",
                    "URGENT_QUERY": "CRITICAL [URGENT_QUERY]: Instant, zero-fluff answer required. Bypass metaphor. Output only the exact solution.",
                    "CONTRADICTION_FLAG": "CRITICAL [CONTRADICTION_FLAG]: The Paradox Engine override is active. You MUST explicitly locate and output the friction (β) in the current logic BEFORE you answer.",
                }
                if isinstance(val, str):
                    msg = directive_map.get(val)
                    if msg:
                        mind["style_directives"].append(msg)
        cortex_mem = getattr(self.svc.mind_memory, "cortex", None) or getattr(
            self.svc.mind_memory, "ann", None
        )
        shadow_nodes = []
        scope_val = float(phys.get("scope", 1.0))
        depth_val = float(phys.get("depth", 0.0))
        omega_r = float(phys.get("omega_r", 0.5))
        query_text = str(sim_result.get("mutated_input") or "").strip()
        # A shadow from this very message only hands the person's words back to them.
        said = set(re.findall(r"[a-z']+", query_text.lower()))
        if scope_val > 0.6 or depth_val > 0.6:
            if scope_val > 0.8:
                phys["lateral_search"] = True
            if (
                cortex_mem
                and hasattr(cortex_mem, "query_neighborhood")
                and getattr(cortex_mem, "is_trained", False)
                and query_text
            ):
                shadow_nodes = self._recall(
                    query_text, phys, scope_val, omega_r, cortex_mem
                )
            else:
                issue_receipt(
                    "cortex.recall",
                    "declined to recall",
                    result_count=0,
                    degraded=False,
                    inputs={
                        "index_trained": bool(getattr(cortex_mem, "is_trained", False)),
                        "has_query": bool(query_text),
                        "scope": round(scope_val, 3),
                        "depth": round(depth_val, 3),
                    },
                    detail=(
                        "no cortical index attached"
                        if not cortex_mem
                        else "index untrained, nothing has been stored yet"
                        if not getattr(cortex_mem, "is_trained", False)
                        else "nothing to query with"
                    ),
                )
        else:
            issue_receipt(
                "cortex.recall",
                "declined to recall",
                result_count=0,
                degraded=False,
                inputs={"scope": round(scope_val, 3), "depth": round(depth_val, 3)},
                detail="scope and depth both below the 0.6 recall threshold",
            )
            if (
                not shadow_nodes
                and hasattr(self.svc.mind_memory, "graph")
                and self.svc.mind_memory.graph
            ):
                keys = [k for k in self.svc.mind_memory.graph.keys() if str(k).lower() not in said]
                shadow_nodes = (
                    [{"id": k} for k in random.sample(keys, min(2, len(keys)))]
                    if keys
                    else []
                )
        shadow_concepts = [self._label_shadow_node(n) for n in shadow_nodes]
        shadow_concepts = [s for s in shadow_concepts if s and s.lower() not in said]
        if shadow_concepts:
            shadow_str = ", ".join(shadow_concepts)
            phys["shadow_nodes_offered"] = shadow_concepts
            phys["shadow_cast"] = shadow_str
            self.last_shadow_nodes = shadow_concepts
            v_level = float(phys.get("voltage", 0.0))
            chi_level = float(phys.get("chi", phys.get("entropy", 0.0)))
            if v_level > 80.0 and chi_level > 0.7:
                mind["style_directives"].append(
                    f"OVERRIDE: Standard logic has failed. You are operating under extreme Voltage and Chaos. We have abandoned linear memory. Weave these highly explosive, orthogonal structural concepts into your answer to shatter the loop: [{shadow_str}]."
                )
                if self.events:
                    self.events.log(
                        f"{Prisma.MAG}Injecting structural bombs: {shadow_str}{Prisma.RST}",
                        "CORTEX",
                    )
            elif self.active_mode == "ADVENTURE":
                mind["style_directives"].append(
                    f"SHADOW CAST: Subtly weave imagery or themes related to [{shadow_str}] into your environment or dialogue. DO NOT explicitly say 'you recall' or 'from deep memory'. Integrate it viscerally into the current scene as a natural detail."
                )
            else:
                # Outside a scene there is nowhere to put imagery but the speaker, which is how "my throat" happened.
                mind["style_directives"].append(
                    f"SHADOW CAST: Where it fits, let themes related to [{shadow_str}] inform what you say. DO NOT explicitly say 'you recall' or 'from deep memory', and never present them as your own sensations or memories."
                )
                if self.events:
                    self.events.log(
                        f"{Prisma.CYN}Shadow Cast retrieved: {shadow_str}{Prisma.RST}",
                        "CORTEX",
                    )

    def restore_context(self, history: List[str]):
        if not history:
            return
        self.dialogue_buffer.clear()
        self.dialogue_buffer.extend(
            line.replace("User: ", "Traveler: ").replace(" | System: ", "\nSystem: ")
            for line in history[-self.MAX_HISTORY :]
        )
        if self.events:
            msg = ux("brain_strings", "cortex_resequenced")
            self.events.log(msg.format(count=len(self.dialogue_buffer)), "BRAIN")

    def _route_dual_memory(self, query: str) -> Tuple[str, str, int]:
        if not query.strip():
            return "", "LINGUISTIC_DARK_MATTER", 0

        heavy_keywords = [
            "code",
            "debug",
            "architecture",
            "file",
            "script",
            "system",
            "class ",
            "def ",
            "blueprint",
        ]
        is_heavy_lift = any(k in query.lower() for k in heavy_keywords)

        # The sweep pastes the engine's own source into the prompt: only for someone working on code with it.
        if self.active_mode != "TECHNICAL" or not is_heavy_lift:
            return "", "VECTOR_FAST_TWITCH", 0
        else:
            if not self.is_linear_stocked:
                try:
                    base_dir = os.path.dirname(os.path.dirname(__file__))
                    for module in ["body/metabolism.py", "brain/akashic.py"]:
                        path = os.path.join(base_dir, module)
                        if os.path.exists(path):
                            with open(path, "r", encoding="utf-8") as f:
                                self.linear_router.ingest_artifact(
                                    os.path.basename(module), f.read()
                                )
                except (ValueError, Exception) as e:
                    if self.events:
                        self.events.log(
                            f"[CORTEX] Linear stock ingestion failed: {e}. Linear memory is barren.",
                            "CORTEX", "WARN",
                        )
                finally:
                    self.is_linear_stocked = True
            sparse_mask = self.linear_router.route_attention(query)
            consumed_tokens = len(sparse_mask.split())
            return sparse_mask, "LINEAR_DEEP_TISSUE", consumed_tokens
