import re

WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SENTENCE_END = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?![a-z])|\n+")
ADJ_SUFFIX = re.compile(
    r"(?:ous|ful|ive|al|ic|less|able|ible|ish|y)$", re.IGNORECASE
)

STAGE_DIRECTION = re.compile(
    r"\([^)]{3,}\)|(?<!\*)\*(?!\*)[^*\n]{3,}\*(?!\*)|<(?:pause|sigh|exhale|inhale)[^>]*>",
    re.IGNORECASE,
)
BREATH_WORDS = frozenset(
    "breath breaths breathe breathes breathing breathless breathlessly inhale inhales inhaled "
    "exhale exhales exhaled lungs gasp gasps gasped gasping pant panting rasp raspy throat "
    "heartbeat pulse chest ragged".split()
)

_TELEMETRY = re.compile(r"<system_telemetry>.*?(?:</system_telemetry>|$)", re.DOTALL | re.IGNORECASE)
_THINK = re.compile(r"<think>.*?(?:</think>|$)", re.DOTALL | re.IGNORECASE)

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

def measure(reply: str, validator_valid: bool) -> dict:
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
    }


def trim_to_sentence_cap(text: str, cap: int) -> str:
    if cap <= 0:
        return ""

    matches = list(SENTENCE_END.finditer(text))

    pieces = []
    last_idx = 0
    valid_count = 0
    
    for match in matches:
        start, end = match.span()
        segment = text[last_idx:start]
        if WORD.search(segment):
            valid_count += 1
        
        if valid_count >= cap:
            return text[:start].strip()
            
        last_idx = end

    segment = text[last_idx:]
    if WORD.search(segment):
        valid_count += 1

    return text.strip()
