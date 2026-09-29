"""Secrets stay out of the store: credentials, keys, card and ID numbers are never kept in memory or the
world graph (the gate's `no_secrets` screen), and are withheld from the audit trail and the checkpoint.

Confidential (never kept): what grants access, money or identity: credentials, keys, tokens, card, bank and
ID numbers. Personal (kept, private to the person): everything else they tell us about themselves, from
names and family to health and preferences (Gordon, 2026-09-29). Only the confidential is screened here.

Detection is by shape and by name, and never echoes what it found: a reason names the kind only. In a story
(ADVENTURE) a password is a puzzle, so only the shapes apply: no door's password looks like an API key."""
from __future__ import annotations

import math
import re
from collections import Counter

_SHAPES = [
    ("a private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("an API key", re.compile(r"\b(?:sk-(?:ant-|proj-)?[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
                              r"|glpat-[A-Za-z0-9_-]{20,}|hf_[A-Za-z0-9]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}"
                              r"|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35})")),
    ("a signed token", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+")),
    ("a government ID number", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
]
# Issuers start 2 to 6; grouped by fours or run together. Not a float's digits or a 1... timestamp.
_CARD = re.compile(r"(?<![\d.-])[2-6]\d{3}(?:(?:[ -]\d{4}){2,3}(?:[ -]\d{1,4})?|\d{9,15})(?![\d-])")
_HEX = re.compile(r"\b[0-9a-fA-F]{32,}\b")
_BLOB = re.compile(r"(?<![A-Za-z0-9+/_=-])[A-Za-z0-9+/_-]{24,}={0,2}(?![A-Za-z0-9+/_=-])")
_SAID = re.compile(r"\b(password|passwd|passcode|passphrase|pin(?: code| number)?|api key|secret key|access token|auth token)\b"
                   r"\s*(?:is|was|=|:)\s*[\"']?([^\s\"',;]+)", re.IGNORECASE)
# "the password is in the drawer" says where it is, not what it is.
_NOT_A_VALUE = {"in", "on", "at", "the", "a", "an", "my", "your", "our", "not", "still", "too", "so", "very", "really",
                "written", "saved", "stored", "somewhere", "under", "with", "for", "from", "and", "or", "same",
                "different", "wrong", "right", "correct", "expired", "changed", "reset", "weak", "strong", "long",
                "short", "easy", "hard", "safe", "secret", "what", "that", "this", "it", "being", "no", "none"}

_KEY_PARTS = {"password", "passwd", "passcode", "passphrase", "pin", "cvv", "cvc", "ssn", "apikey", "iban", "otp"}
_KEY_JOINED = re.compile(r"api_?key|secret_?key|private_?key|client_?secret|(?:api|access|auth|refresh|bearer|session|bot|github)_?token"
                         r"|card_?number|credit_?card|social_?security|(?:bank|routing)_?(?:account|number)|account_?number")
_KEY_ABOUT = {"hint", "manager", "app", "policy", "reset", "rule", "rules", "length"}  # about a secret, not one


def _luhn(digits: str) -> bool:
    total = 0
    for i, d in enumerate(int(c) for c in reversed(digits)):
        total += d if i % 2 == 0 else (d * 2 - 9 if d > 4 else d * 2)
    return total % 10 == 0


def _entropy(s: str) -> float:
    return -sum(n / len(s) * math.log2(n / len(s)) for n in Counter(s).values())


def _blob(token: str) -> bool:
    # Random base64 is about 40% capitals; paths and camelCase run near 10%.
    body = token.rstrip("=")
    seps = sum(not c.isalnum() for c in body)
    if seps * 12 > len(body) or max(map(len, re.split(r"[^A-Za-z0-9]", body))) < 10:
        return False  # archive/SESSION_LOGS_2026_09
    upper, lower = (sum(f(c) for c in body) / len(body) for f in (str.isupper, str.islower))
    return any(c.isdigit() for c in body) and upper >= 0.2 and lower >= 0.2 and _entropy(body) >= 3.5


def _finds(text: str, in_story: bool = False):
    """(start, end, kind) for every secret-shaped span."""
    for kind, pattern in _SHAPES:
        yield from ((m.start(), m.end(), kind) for m in pattern.finditer(text))
    for m in _CARD.finditer(text):
        digits = re.sub(r"\D", "", m.group())
        if 13 <= len(digits) <= 19 and _luhn(digits):
            yield m.start(), m.end(), "a card number"
    for m in _HEX.finditer(text):
        if re.search(r"\d", m.group()) and re.search(r"[a-fA-F]", m.group()):
            yield m.start(), m.end(), "a long hex key"
    for m in _BLOB.finditer(text):
        if _blob(m.group()):
            yield m.start(), m.end(), "an encoded token"
    for m in () if in_story else _SAID.finditer(text):
        if m.group(2).lower() not in _NOT_A_VALUE:
            yield m.start(2), m.end(2), "a " + m.group(1).lower().replace("pin", "PIN")


def kind_of(text, in_story: bool = False) -> str | None:
    """What kind of secret `text` holds, or None."""
    return next((kind for _, _, kind in _finds(str(text or ""), in_story)), None)


def credential_key(key) -> bool:
    k = re.sub(r"[^a-z0-9]+", "_", str(key or "").lower()).strip("_")
    parts = set(k.split("_"))
    return not parts & _KEY_ABOUT and bool(parts & _KEY_PARTS or _KEY_JOINED.search(k))


def redact(text, in_story: bool = False, marker: str = "[withheld: {kind}]") -> str:
    text = str(text or "")
    out, at = [], 0
    for start, end, kind in sorted(_finds(text, in_story)):
        if start >= at:
            out += [text[at:start], marker.format(kind=kind)]
            at = end
    return "".join(out) + text[at:]


def strip(text) -> str:
    """`text` with its secrets gone, for the tokenizer: no fragment of a key becomes a learned word."""
    return redact(text, marker=" ")


def screen(verb: str, what: str, args: dict, in_story: bool = False) -> str | None:
    """The gate's `no_secrets` screen: why these args may not be kept, or None. Forgetting one is always allowed."""
    if verb == "forget":
        return None
    if not in_story and (credential_key(args.get("key")) or credential_key(what.rsplit("/", 1)[-1])):
        return "the memory is named as a credential; confidential things are never kept"
    for name, value in args.items():
        if kind := kind_of(value, in_story):
            return f"{name} looks like {kind}; confidential things are never kept"
    return None


def _args(raw: str) -> dict:
    return dict(p.split(":", 1) for p in raw.split(";") if ":" in p)


def scrub(text, in_story: bool = False) -> str:
    """`text` fit for disk: secrets withheld, and a NOMINATE line the screen would refuse loses its args."""
    from .kernel import NOMINATION

    lines = []
    for line in str(text or "").splitlines(keepends=True):
        m = NOMINATION.match(line.strip())
        if m and screen(m["verb"], m["what"], {k.strip(): v.strip() for k, v in _args(m["args"]).items()}, in_story):
            line = line[:line.index("args=")] + "args=[withheld: a secret]" + ("\n" if line.endswith("\n") else "")
        lines.append(redact(line, in_story))
    return "".join(lines)


def scrub_all(value, in_story: bool = False):
    """Every string in a JSON-shaped value, scrubbed."""
    if isinstance(value, str):
        return scrub(value, in_story)
    if isinstance(value, list):
        return [scrub_all(v, in_story) for v in value]
    if isinstance(value, dict):
        named = not in_story and any(isinstance(v, str) and credential_key(v) for v in value.values())
        # {"wifi_password": "..."} and {"key": "wifi_password", "value": "..."} alike
        return {k: "[withheld: a secret]" if isinstance(v, str) and not in_story and (credential_key(k) or named and k == "value")
                else scrub_all(v, in_story) for k, v in value.items()}
    return value
