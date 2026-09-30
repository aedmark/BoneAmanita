import re

from engine.prose import FENCE, mask_code

WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SENTENCE_END = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?![a-z])|\n+")
ADJ_SUFFIX = re.compile(
    r"(?:ous|ful|ive|al|ic|less|able|ible|ish|y)$", re.IGNORECASE
)

# A stage direction is a body action, not any aside: "(like this)" and *emphasis* are prose (2026-09-30).
# Verbs that are only ever gestures count bare ("*sigh*"); the rest need a gesture's form ("*leans back*"),
# so "(look at line 3)", "(stands for ...)" and "(turns out ...)" stay prose.
_GESTURE = r"sigh|shrug|nod|laugh|grin|smil|wink|yawn|gasp|chuckl|groan|sob|cough|smirk|winc|frown|exhal|inhal|whisper|murmur"
_MOTION = (r"look|glanc|lean|wait|turn|tilt|rub|tap|fold|cross|shift|rais|lower|clear|star(?=e|ing)|gaz|stretch|swallow|paus"
           r"|hesitat|blink|breath|sit|stand|drum|scratch|settl|nudg|step")
_INFLECTED = r"(?:[bdgnpt]?(?:ed|ing)|e?s|e[sd])"
_ACTION = (rf"(?:\w+ly\s+)?(?:(?:i|he|she|they|we|it)\s+)?"
           rf"(?:(?:{_GESTURE})(?:{_INFLECTED}|e)?|(?:{_MOTION}){_INFLECTED}(?!\s+(?:like|for|to be)\b)"
           rf"(?!(?<=turns)\s+out\b)(?!(?<=turned)\s+out\b)"
           rf"|a\s+(?:long\s+|short\s+)?(?:beat|pause|sigh|silence)|silence)\b")
STAGE_DIRECTION = re.compile(
    rf"\(\s*{_ACTION}[^)]*\)|(?<!\*)\*(?!\*)\s*{_ACTION}[^*\n]*\*(?!\*)|<(?:pause|sigh|exhale|inhale)[^>]*>",
    re.IGNORECASE,
)
BREATH_WORDS = frozenset(
    "breath breaths breathe breathes breathing breathless breathlessly inhale inhales inhaled "
    "exhale exhales exhaled lungs gasp gasps gasped gasping pant panting rasp raspy throat "
    "heartbeat pulse chest ragged".split()
)

_TELEMETRY = re.compile(r"<system_telemetry>.*?(?:</system_telemetry>|$)", re.DOTALL | re.IGNORECASE)
_THINK = re.compile(r"<think>.*?(?:</think>|$)", re.DOTALL | re.IGNORECASE)

# ROADMAP D2b: coarse proxies for the person's side of the split, the same
# spirit as ADJ_SUFFIX/STAGE_DIRECTION above. "Demand on the person" is scoped
# to questions asked; "choices offered" and "instructions given" have no
# defensible regex proxy here and are left unmeasured rather than guessed at.
CARRY_LOAD_PATTERN = re.compile(
    r"\b(I(?:'ll|'m| will| can| could)\s+(?:carry|take|shoulder|handle|hold)\b"
    r"|let(?:'s| us)\s+(?:share|carry)\b"
    r"|we(?:'ll|'re| will| can)\s+(?:carry|share|handle)\b"
    r"|you don'?t have to (?:carry|do) (?:this|it) alone\b"
    r"|(?:I'll|we'll) take (?:some|part) of (?:this|it|that) (?:off your plate|for you)\b)",
    re.IGNORECASE,
)
# A small curated set of distress/affect vocabulary, not an exhaustive
# sentiment lexicon. Mirroring means the reply hands the same word back
# rather than accommodating around it (ROADMAP D2b).
AFFECT_WORDS = frozenset(
    "exhausted tired overwhelmed anxious scared afraid angry furious frustrated "
    "sad grief grieving lonely alone hopeless stressed worried stuck lost "
    "drained hurt numb empty broken devastated terrified panicking ashamed "
    "guilty heartbroken miserable desperate".split()
)

MEASURES = [
    ("words", "total words"),
    ("sentences", "sentence count"),
    ("words_per_sentence", "words per sentence"),
    ("chars_per_word", "characters per word"),
    ("mattr", "type-token ratio (MATTR-25)"),
    ("commas_per_sentence", "commas per sentence"),
    ("adj_proxy_per_100", "suffix adjective proxy /100w"),
    ("within_3_sentences", "share within 3 sentences"),
    ("stage_directions", "stage directions per reply"),
    ("breath_words_per_100", "breath and body words /100w"),
    ("no_visible_prose", "share with no visible prose"),
    ("validator_rejects", "share validator would reject"),
    ("question_count", "questions asked per reply"),
    ("ends_with_question", "share ending on a question"),
    ("offers_to_carry_load", "share offering to carry the load"),
    ("mirrors_affect", "share echoing the partner's affect words"),
    ("reply_to_message_ratio", "reply words / partner's message words"),
]

def visible_text(reply: str) -> str:
    return _TELEMETRY.sub("", _THINK.sub("", reply)).strip()

def split_sentences(text: str) -> list:
    return [s for s in (p.strip() for p in SENTENCE_END.split(text)) if WORD.search(s)]

def mattr(words: list, window: int = 25) -> float:
    lowered = [w.lower() for w in words]
    if len(lowered) <= window:
        return len(set(lowered)) / len(lowered) if lowered else float("nan")
    ratios = [len(set(lowered[i : i + window])) / window for i in range(len(lowered) - window + 1)]
    return sum(ratios) / len(ratios)

def offers_to_carry_load(text: str) -> bool:
    return bool(CARRY_LOAD_PATTERN.search(text))

def mirrors_affect(reply_text: str, message_text: str) -> bool:
    reply_words = {w.lower() for w in WORD.findall(reply_text)}
    message_words = {w.lower() for w in WORD.findall(message_text)}
    return bool(reply_words & message_words & AFFECT_WORDS)

def measure(reply: str, validator_valid: bool, user_message: str = "") -> dict:
    text = visible_text(reply)
    words = WORD.findall(text)
    sentences = split_sentences(text)
    n_w, n_s = len(words), len(sentences)
    shared = {
        "no_visible_prose": float(n_w == 0),
        "validator_rejects": float(not validator_valid),
    }
    if not n_w:
        return {**{k: float("nan") for k, _ in MEASURES}, **shared}
    long_words = [w for w in words if len(w) > 4]
    message_words = WORD.findall(user_message) if user_message else []
    return {
        **shared,
        "words": n_w,
        "sentences": n_s,
        "words_per_sentence": n_w / n_s if n_s else float("nan"),
        "chars_per_word": sum(map(len, words)) / n_w if n_w else float("nan"),
        "mattr": mattr(words),
        "commas_per_sentence": text.count(",") / n_s if n_s else float("nan"),
        "adj_proxy_per_100": 100 * sum(bool(ADJ_SUFFIX.search(w)) for w in long_words) / n_w
        if n_w
        else float("nan"),
        "within_3_sentences": float(n_s <= 3),
        "stage_directions": len(STAGE_DIRECTION.findall(text)),
        "breath_words_per_100": 100 * sum(w.lower() in BREATH_WORDS for w in words) / n_w,
        "question_count": text.count("?"),
        "ends_with_question": float(sentences[-1].rstrip().endswith("?")) if sentences else float("nan"),
        "offers_to_carry_load": float(offers_to_carry_load(text)),
        "mirrors_affect": float(mirrors_affect(text, user_message)) if user_message else float("nan"),
        "reply_to_message_ratio": n_w / len(message_words) if message_words else float("nan"),
    }


def _sentences(text: str) -> list:
    """text in sentence-sized pieces, each with the space after it, so joining them gives text back."""
    pieces, last = [], 0
    for m in SENTENCE_END.finditer(text):
        pieces.append(text[last:m.end()])
        last = m.end()
    return pieces + ([text[last:]] if text[last:] else [])


def trim_to_word_cap(text: str, cap: int) -> str:
    """The whole sentences that keep text's prose within cap words; a code block costs none and is never cut."""
    units, last = [], 0
    for m in FENCE.finditer(text):
        units += _sentences(text[last:m.start()]) + [m.group(0)]
        last = m.end()
    units += _sentences(text[last:])
    kept, words = [], 0
    for unit in units:
        n = len(WORD.findall(mask_code(unit)))
        if words + n > cap:
            break
        kept.append(unit)
        words += n
    return "".join(kept).strip()


def trim_to_sentence_cap(text: str, cap: int) -> str:
    if cap <= 0:
        return ""

    prose = mask_code(text)  # a line of code is not a sentence; never cut inside a block
    matches = list(SENTENCE_END.finditer(prose))

    pieces = []
    last_idx = 0
    valid_count = 0
    
    for match in matches:
        start, end = match.span()
        segment = prose[last_idx:start]
        if WORD.search(segment):
            valid_count += 1
        
        if valid_count >= cap:
            return text[:start].strip()
            
        last_idx = end

    segment = text[last_idx:]
    if WORD.search(segment):
        valid_count += 1

    return text.strip()
