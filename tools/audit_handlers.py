"""tools/audit_handlers.py

Two static audits behind the numbers in ROADMAP.md Track A. Re-run these
rather than trusting the figures in the document.

    python tools/audit_handlers.py

1. Exception handlers that swallow silently (no log, no re-raise).
2. events.log(msg, SEVERITY) calls that pass a severity where `source`
   is expected, which silently demotes the line to DEBUG.
"""

import ast
import collections
import subprocess

SEVERITIES = {"CRIT", "WARN", "ERROR", "CRITICAL"}
LOGGING_ATTRS = {"log", "warning", "error", "critical", "exception", "print"}


def source_files():
    out = subprocess.check_output(["git", "ls-files", "*.py"], text=True).split()
    return [f for f in out if not f.startswith(("tests/", "tools/"))]


def audit_handlers(files):
    silent, logged, reraise, pass_only = [], [], [], 0
    for path in files:
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler):
                continue
            inner = list(ast.walk(node))
            has_raise = any(isinstance(n, ast.Raise) for n in inner)
            has_log = any(
                isinstance(n, ast.Call)
                and (
                    (isinstance(n.func, ast.Attribute) and n.func.attr in LOGGING_ATTRS)
                    or (isinstance(n.func, ast.Name) and n.func.id == "print")
                )
                for n in inner
            )
            where = (path, node.lineno)
            if len(node.body) == 1 and isinstance(node.body[0], (ast.Pass, ast.Continue)):
                pass_only += 1
                silent.append(where)
            elif has_raise:
                reraise.append(where)
            elif has_log:
                logged.append(where)
            else:
                silent.append(where)
    return silent, logged, reraise, pass_only


def audit_log_levels(files):
    demoted, two_arg = [], 0
    for path in files:
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "log"
            ):
                continue
            args = node.args
            if len(args) == 2 and isinstance(args[1], ast.Constant):
                two_arg += 1
                if args[1].value in SEVERITIES:
                    demoted.append((path, node.lineno, args[1].value))
    return demoted, two_arg


def main():
    files = source_files()
    silent, logged, reraise, pass_only = audit_handlers(files)
    total = len(silent) + len(logged) + len(reraise)
    print(f"except handlers: {total}")
    print(f"  silent (no log, no raise): {len(silent)}  (bare pass/continue: {pass_only})")
    print(f"  logged: {len(logged)}   re-raise: {len(reraise)}")
    worst = collections.Counter(f for f, _ in silent)
    for f, n in worst.most_common(10):
        print(f"    {n:3d}  {f}")

    demoted, two_arg = audit_log_levels(files)
    print(f"\nevents.log(msg, X) two-arg calls: {two_arg}")
    print(f"  passing a SEVERITY as `source` (demoted to DEBUG): {len(demoted)}")
    by_sev = collections.Counter(s for _, _, s in demoted)
    for s, n in by_sev.most_common():
        print(f"    {s:10s} {n}")
    for f, ln, s in demoted[:10]:
        print(f"      {f}:{ln}  ({s})")


if __name__ == "__main__":
    main()
