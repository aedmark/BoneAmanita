#!/usr/bin/env python3
"""Check the project docs for the mistakes that make a handoff lie.

    python3 tools/check_docs.py              # from the repo root
    python3 tools/check_docs.py --template   # the template itself: placeholders are expected

Errors (exit 1):
  - a {{placeholder}} left in a doc
  - a roadmap ID used twice, filed under the wrong phase, or with an unknown checkbox
  - a decision number used twice or out of order, or superseded by one that does not exist or comes earlier
  - an open question (Q-NNN) defined twice
  - a held tension (T-NNN) used twice, out of order, or referenced but not defined
  - a roadmap ID, decision number, question, or tension mentioned in a doc that does not exist
  - two session-log entries with the same number (HANDOFF and docs/archive/ together)
  - a relative link, or a path in AGENTS.md's Layout table, that points at nothing
  - an invisible or bidirectional control character in a document
  - a roadmap item in HANDOFF's Next steps that is already completed in ROADMAP.md
  - an em dash in prose outside code blocks (Lexical Firewall violation)
Warnings (exit 0):
  - HANDOFF's "Last updated" is missing, or older than its newest session-log entry
  - HANDOFF's session log or "Current state" has outgrown the limits below (time to archive)
  - an invariant in INVARIANTS.md is defined but never cited outside INVARIANTS.md
  - a claim in HANDOFF's verified/what-works section lacks an explicit Pramāṇa tag

Standard library only. HTML comments are ignored, so examples can live in them.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = [
    "AGENTS.md", "CLAUDE.md", "README.md", "ROADMAP.md",
    "docs/README.md", "docs/INVARIANTS.md", "docs/HANDOFF.md", "docs/ARCHITECTURE.md", "docs/DECISIONS.md",
    "docs/TESTING.md", "docs/SECURITY.md", "docs/CHANGELOG.md", "docs/CONTRIBUTING.md",
    "docs/devlog.html", "docs/bonereport.html", "docs/bonereport_0926.html",
]
# Keep in step with AGENTS.md (end of session, step 3) and HANDOFF's header.
LOG_LIMIT = 10
CURRENT_STATE_LINES = 80

ITEM_RE = re.compile(r"\bP(\d+)-(\d+)\b")
DECISION_RE = re.compile(r"\bD-(\d{3})\b")
QUESTION_RE = re.compile(r"\bQ-(\d{3})\b")
TENSION_RE = re.compile(r"\bT-(\d{3})\b")
INVARIANT_RE = re.compile(r"\bINV-(\d{3})\b")
INVISIBLE_RE = re.compile(r"[\u180e\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)|\b(?:href|src)=\"([^\"]+)\"")
PRAMANA_RE = re.compile(r"\[(OBSERVED|DEDUCED|CONTRACT|HYPOTHESIS|UNTESTED)\]")

errors, warnings = [], []


def read(path):
    text = path.read_text(encoding="utf-8")
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def where(path, text, pos):
    return f"{path.relative_to(ROOT)}:{text.count(chr(10), 0, pos) + 1}"


def section(text, heading):
    m = re.search(rf"^## {heading}\b.*?(?=^## |\Z)", text, flags=re.M | re.S)
    return (m.group(0), m.start()) if m else ("", 0)


def main():
    template = "--template" in sys.argv[1:]
    docs = [ROOT / d for d in DOCS if (ROOT / d).is_file()]
    for folder in ("docs/archive",):
        if (ROOT / folder).is_dir():
            docs += sorted(p for p in (ROOT / folder).iterdir()
                           if p.suffix in (".md", ".html") and not p.name.startswith("_"))
    texts = {p: read(p) for p in docs}

    # 1. Placeholder check
    if not template:
        for path, text in texts.items():
            for m in re.finditer(r"\{\{[^}]*\}\}", text):
                errors.append(f"{where(path, text, m.start())}: placeholder left: {m.group(0)[:60]}")

    # 2. Roadmap validation
    roadmap = ROOT / "ROADMAP.md" if (ROOT / "ROADMAP.md") in texts else None
    items, completed_items = set(), set()
    if roadmap is None:
        errors.append("no ROADMAP.md in the repository root")
    else:
        text, phase = texts[roadmap], None
        for m in re.finditer(r"^## Phase (\d+)|^- \[(.)\] (P(\d+)-(\d+))\b", text, flags=re.M):
            if m.group(1):
                phase = m.group(1)
                continue
            box, item, item_phase = m.group(2), m.group(3), m.group(4)
            if item in items:
                errors.append(f"{where(roadmap, text, m.start())}: {item} is used twice")
            items.add(item)
            if box == "x":
                completed_items.add(item)
            if box not in " x~-":
                errors.append(f"{where(roadmap, text, m.start())}: {item} has checkbox [{box}]; use [ ], [~], [x] or [-]")
            if phase is not None and item_phase != phase:
                errors.append(f"{where(roadmap, text, m.start())}: {item} is filed under Phase {phase}")
        # Archived phases keep their IDs reserved.
        for path, text in texts.items():
            if path.parent.name == "archive":
                items.update(m.group(1) for m in re.finditer(r"^- \[.\] (P\d+-\d+)\b", text, flags=re.M))

    # 3. Invariants validation (Śruti)
    invariants_path = ROOT / "docs" / "INVARIANTS.md"
    invariants = set()
    if invariants_path in texts:
        text = texts[invariants_path]
        for m in re.finditer(r"^## INV-(\d{3})\b", text, flags=re.M):
            inv_id = f"INV-{m.group(1)}"
            if inv_id in invariants:
                errors.append(f"{where(invariants_path, text, m.start())}: {inv_id} is used twice")
            invariants.add(inv_id)

    # 4. Decisions validation (Smṛti)
    decisions_path = ROOT / "docs" / "DECISIONS.md"
    decisions, supersessions, questions, tensions = set(), [], set(), set()
    if decisions_path in texts:
        text, last = texts[decisions_path], 0
        for m in re.finditer(r"^## D-(\d{3})\b([^\n]*)", text, flags=re.M):
            number = int(m.group(1))
            if f"D-{m.group(1)}" in decisions:
                errors.append(f"{where(decisions_path, text, m.start())}: D-{m.group(1)} is used twice")
            elif number < last:
                errors.append(f"{where(decisions_path, text, m.start())}: D-{m.group(1)} comes after D-{last:03d}")
            decisions.add(f"D-{m.group(1)}")
            last = max(last, number)
            by = re.search(r"superseded by D-(\d{3})", m.group(2))
            if by:
                supersessions.append((number, int(by.group(1)), m.start()))
        for number, by, pos in supersessions:
            if f"D-{by:03d}" in decisions and by <= number:
                errors.append(f"{where(decisions_path, text, pos)}: D-{number:03d} is superseded by an earlier "
                              f"decision, D-{by:03d}")
        for m in re.finditer(r"^(?:### Q-(\d{3})\b|- \*\*Q-(\d{3})\*\*)", text, flags=re.M):
            q_num = m.group(1) or m.group(2)
            q_id = f"Q-{q_num}"
            if q_id in questions:
                errors.append(f"{where(decisions_path, text, m.start())}: {q_id} is used twice")
            questions.add(q_id)
        last_t = 0
        for m in re.finditer(r"^### T-(\d{3})\b", text, flags=re.M):
            number = int(m.group(1))
            t_id = f"T-{m.group(1)}"
            if t_id in tensions:
                errors.append(f"{where(decisions_path, text, m.start())}: {t_id} is used twice")
            elif number < last_t:
                errors.append(f"{where(decisions_path, text, m.start())}: {t_id} comes after T-{last_t:03d}")
            tensions.add(t_id)
            last_t = max(last_t, number)

    # 5. Cross-reference, invisible character, and link validation
    for path, text in texts.items():
        for m in INVISIBLE_RE.finditer(text):
            errors.append(f"{where(path, text, m.start())}: invisible or bidirectional control character "
                          f"U+{ord(m.group(0)):04X}")
        if roadmap is not None:
            for m in ITEM_RE.finditer(text):
                if m.group(0) not in items:
                    errors.append(f"{where(path, text, m.start())}: {m.group(0)} is not in the roadmap")
        if decisions_path in texts:
            for m in DECISION_RE.finditer(text):
                if m.group(0) not in decisions:
                    errors.append(f"{where(path, text, m.start())}: {m.group(0)} is not in DECISIONS.md")
            for m in QUESTION_RE.finditer(text):
                if m.group(0) not in questions:
                    errors.append(f"{where(path, text, m.start())}: {m.group(0)} is not in DECISIONS.md's open questions")
            for m in TENSION_RE.finditer(text):
                if m.group(0) not in tensions:
                    errors.append(f"{where(path, text, m.start())}: {m.group(0)} is not in DECISIONS.md's held tensions")
        if invariants_path in texts:
            for m in INVARIANT_RE.finditer(text):
                if m.group(0) not in invariants:
                    errors.append(f"{where(path, text, m.start())}: {m.group(0)} is not in INVARIANTS.md")
        for m in LINK_RE.finditer(text):
            target = (m.group(1) or m.group(2)).split("#")[0]
            if not target or "{{" in target or re.match(r"[a-z][a-z0-9+.-]*:", target):
                continue
            if not (path.parent / target).exists():
                errors.append(f"{where(path, text, m.start())}: link to {target}, which does not exist")

    # 6. Repository Map validation in AGENTS.md
    agents = ROOT / "AGENTS.md"
    if agents in texts:
        layout, offset = section(texts[agents], "Layout")
        if not layout:
            layout, offset = section(texts[agents], "Repository map")
        for m in re.finditer(r"^\| `([^`]+)` \|", layout, flags=re.M):
            if "{{" not in m.group(1) and not (ROOT / m.group(1)).exists():
                errors.append(f"{where(agents, texts[agents], offset + m.start())}: Repository Map lists {m.group(1)}, "
                              f"which does not exist")

    # 7. Handoff validation (Vartamāna & Pramāṇa & Ghana-pāṭha Reciprocity)
    handoff = ROOT / "docs" / "HANDOFF.md"
    if handoff in texts:
        text = texts[handoff]
        session_re = re.compile(r"^### Session (\d+)\b([^\n]*)", flags=re.M)
        sessions = [(m.group(1), (DATE_RE.search(m.group(2)) or [None])[0]) for m in session_re.finditer(text)]
        seen = set()
        for path in [handoff] + [p for p in texts if p.parent.name == "archive"]:
            for m in session_re.finditer(texts[path]):
                if m.group(1) in seen:
                    errors.append(f"{where(path, texts[path], m.start())}: a second entry for Session {m.group(1)}")
                seen.add(m.group(1))
        updated = re.search(r"Last updated:\s*(\d{4}-\d{2}-\d{2})", text)
        newest = max((d for _, d in sessions if d), default=None)
        if not updated:
            if not template:
                warnings.append("docs/HANDOFF.md: no 'Last updated: YYYY-MM-DD' line in Current state")
        elif newest and updated.group(1) < newest:
            warnings.append(f"docs/HANDOFF.md: Current state was last updated {updated.group(1)}, "
                            f"but the session log has an entry from {newest}")
        if len(sessions) > LOG_LIMIT:
            warnings.append(f"docs/HANDOFF.md: {len(sessions)} session-log entries; move all but the newest "
                            f"{LOG_LIMIT} to docs/archive/")
        current, _ = section(text, "Current state")
        if current.count("\n") > CURRENT_STATE_LINES:
            warnings.append(f"docs/HANDOFF.md: Current state is {current.count(chr(10))} lines (limit "
                            f"{CURRENT_STATE_LINES}); move history to the session log")

        # Ghana-pāṭha Reciprocal Check: Next steps must not be already completed
        next_steps, ns_offset = section(text, "Next steps")
        for m in ITEM_RE.finditer(next_steps):
            item = m.group(0)
            if item in completed_items:
                errors.append(f"{where(handoff, text, ns_offset + m.start())}: {item} is listed in Next steps, "
                              f"but is already marked completed [x] in ROADMAP.md")

        # Pramāṇa Validation: 'What works' or verified items must carry an explicit Pramāṇa tag
        m = re.search(r"^(?:## What works|\*\*What works\b|\*\*Verified\b).*?(?=(?:^\*\*|\Z|^## ))", text, flags=re.M | re.S)
        if m:
            what_works = m.group(0)
            for line in what_works.splitlines():
                if line.strip().startswith("- "):
                    if not PRAMANA_RE.search(line) and "{{" not in line:
                        warnings.append(f"docs/HANDOFF.md: claim lacks explicit Pramāṇa tag "
                                        f"([OBSERVED], [DEDUCED], [CONTRACT], [HYPOTHESIS], [UNTESTED]): {line.strip()[:60]}")

    # 8. Ghana-pāṭha Reciprocal Invariant Citation Check
    if invariants_path in texts:
        outside_texts = {p: t for p, t in texts.items() if p != invariants_path and p.parent.name != "archive"}
        for inv in sorted(invariants):
            referenced = any(inv in t for t in outside_texts.values())
            if not referenced:
                warnings.append(f"docs/INVARIANTS.md: {inv} is defined but never cited in architecture, testing, or agents protocol")

    # 9. Lexical Firewall Check (Śikṣā: zero em dashes across all prose)
    for path, text in texts.items():
        if path.parent.name == "archive":
            continue
        # Mask code blocks and inline code preserving newlines and char offsets
        prose = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
        prose = re.sub(r"`[^`\n]+`", lambda m: " " * len(m.group(0)), prose)
        for m in re.finditer(r"—", prose):
            errors.append(f"{where(path, text, m.start())}: em dash detected in prose (Lexical Firewall violation; use comma, semicolon, or parentheses)")

    for line in errors:
        print(f"ERROR {line}")
    for line in warnings:
        print(f"WARN  {line}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s) in {len(texts)} file(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
