#!/usr/bin/env python3
"""Build and validate the BoneAmanita 3x Manual Set."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL_PY = ROOT / "tools" / "manual.py"

if not MANUAL_PY.exists():
    print(f"error: cannot find manual generator script at {MANUAL_PY}", file=sys.stderr)
    sys.exit(1)

SPEC = importlib.util.spec_from_file_location("manual", MANUAL_PY)
manual_mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(manual_mod)

MANUAL_SET = [
    {
        "source": ROOT / "docs" / "manual" / "system.manual.json",
        "output": ROOT / "docs" / "manual" / "index.html",
        "name": "System Manual",
    },
    {
        "source": ROOT / "docs" / "manual" / "reference.manual.json",
        "output": ROOT / "docs" / "manual" / "reference.html",
        "name": "Reference Manual",
    },
]


def run_checks() -> int:
    status = 0
    print("Checking BoneAmanita manual sources...")
    for item in MANUAL_SET:
        print(f"\n[{item['name']}] Checking {item['source'].relative_to(ROOT)}:")
        res = manual_mod.run_check(item["source"], [])
        if res != 0:
            status = res
    return status


def run_builds() -> int:
    status = 0
    print("Building BoneAmanita manual set...")
    for item in MANUAL_SET:
        print(f"\n[{item['name']}] Building {item['output'].relative_to(ROOT)}:")
        res = manual_mod.run_build(item["source"], item["output"], [])
        if res != 0:
            status = res
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and build the BoneAmanita manual set")
    parser.add_argument("action", nargs="?", default="build", choices=["build", "check"], help="Action to execute")
    args = parser.parse_args()

    if args.action == "check":
        return run_checks()
    return run_builds()


if __name__ == "__main__":
    sys.exit(main())
