"""Run main.BoneAmanita against a cloud provider in an isolated workspace."""
import argparse
import getpass
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=["xai", "anthropic"])
    parser.add_argument("--model", help="Default: grok-4.3 or claude-haiku-4-5")
    parser.add_argument("--mode", default="CONVERSATION", choices=["CONVERSATION", "ADVENTURE", "CREATIVE", "TECHNICAL"])
    parser.add_argument("--prompt", action="append", help="Repeat for a multi-turn run")
    args = parser.parse_args()
    args.model = args.model or {"xai": "grok-4.3", "anthropic": "claude-haiku-4-5"}[args.provider]
    key_name = "XAI_API_KEY" if args.provider == "xai" else "ANTHROPIC_API_KEY"
    if not os.getenv(key_name):
        if not sys.stdin.isatty():
            parser.error(f"Set {key_name}, or run in a terminal for hidden key entry")
        os.environ[key_name] = getpass.getpass(f"Paste {key_name} (hidden; not saved): ").strip()
        if not os.environ[key_name]:
            parser.error("An API key is required")
    root = Path(__file__).resolve().parents[1]
    run_dir = Path(tempfile.mkdtemp(prefix="bone-live-"))
    # Copy authored inputs only: no existing memories, saves, logs, or secrets.
    for path in root.glob("*.py"):
        shutil.copy2(path, run_dir / path.name)
    for name in ("archetypes", "body", "brain", "drivers", "lore", "machine", "mechanics", "phases", "physics", "protocols", "soul", "spores"):
        shutil.copytree(root / name, run_dir / name, ignore=shutil.ignore_patterns("__pycache__", "lenses.json", "akashic_discovered_words.json"))
    os.chdir(run_dir)
    sys.path.insert(0, str(run_dir))
    os.environ["BONE_STRICT_LIVE"] = "1"
    from main import BoneAmanita
    from mechanics.providers import CLOUD_ENDPOINTS
    engine = None
    report = {"passed": False, "provider": args.provider, "model": args.model, "mode": args.mode, "turns": []}
    try:
        engine = BoneAmanita({"provider": args.provider, "model": args.model,
                              "base_url": CLOUD_ENDPOINTS[args.provider], "boot_mode": args.mode,
                              "user_name": "LIVE_TEST"})
        boot = engine.engage_cold_boot()
        report["boot"] = boot
        for prompt in args.prompt or ["Describe the room around us and one object I can examine.", "Examine that object. What changes?"]:
            result = engine.process_turn(prompt)
            report["turns"].append({"prompt": prompt, "result": result})
            print(result.get("ui", ""))
        llm = engine.cortex.llm
        report.update(live_successes=llm.live_successes, live_failures=llm.live_failures)
        packets = [boot] + [turn["result"] for turn in report["turns"]]
        report["passed"] = llm.live_successes > 0 and llm.live_failures == 0 and all(
            packet and packet.get("type") not in engine._TERMINAL_STATES for packet in packets)
    except Exception as exc:
        report["error"] = type(exc).__name__
        raise
    finally:
        if engine:
            engine.shutdown()
        (run_dir / "live_report.json").write_text(json.dumps(report, indent=2, default=str))
        print(f"Live run artifacts: {run_dir}")
    return 0 if report.get("passed") else 1


if __name__ == "__main__":
    sys.exit(main())
