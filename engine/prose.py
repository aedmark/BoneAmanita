"""Style rules read prose, never code. The end-to-end run (2026-09-29) lost a regex answer: a `#` comment in a
code block read as a Title Case header, and `===` in JavaScript is a scaffold leak to the gatekeeper."""

import re

FENCE = re.compile(r"```.*?(?:```|$)", re.DOTALL)
INLINE = re.compile(r"`[^`\n]+`")


def _blank(match):
    return re.sub(r"[^\n]", " ", match.group(0))


def mask_code(text: str) -> str:
    """text with fenced and inline code blanked out; same length and line breaks, so offsets still hold."""
    return INLINE.sub(_blank, FENCE.sub(_blank, str(text or "")))


def in_code(lines):
    """For each line, whether it sits in a fence (the fence lines included)."""
    inside, marks = False, []
    for line in lines:
        fence = line.strip().startswith("```")
        marks.append(inside or fence)
        if fence:
            inside = not inside
    return marks


def close_gaps(text: str) -> str:
    """Runs of blank lines in the prose (left where a file block was lifted out) close to one; code keeps its own."""
    parts, last = [], 0
    for m in FENCE.finditer(text):
        parts += [re.sub(r"\n{3,}", "\n\n", text[last:m.start()]), m.group(0)]
        last = m.end()
    return "".join(parts + [re.sub(r"\n{3,}", "\n\n", text[last:])])
