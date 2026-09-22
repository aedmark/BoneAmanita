"""tools/audit_somatic_responsive.py

Run one system against a simulated person who reacts to it, then report.

    python tools/audit_somatic_responsive.py --topic toast --arm friend
    python tools/audit_somatic_responsive.py --topic toast --arm vanilla
    python tools/audit_somatic_responsive.py --topic toast --arm bone      # the full engine
    python tools/audit_somatic_responsive.py --topic toast --report

One arm per invocation (the engine arm alone takes most of a background
task's ten minutes). Each arm writes to `tools/cache/somatic_responsive.jsonl`
and its exit interview to `somatic_responsive_exit.jsonl`; the blind judge's
`--responsive` mode reads them back. Why the person is simulated, and what
stays fixed, is in `somatic_sim_user.py`.

The report sets the systems side by side on what the scripted comparison could
not see: how much each one made the person write, whether the person went
quiet after the first half, how often the engine held silence, and the
simulated person's own exit interview.
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_somatic_census import DEFAULT_TOPIC, SCRIPTS  # noqa: E402
from somatic_sim_user import EXIT_KEYS, SIM_MODEL, SimulatedUser  # noqa: E402

CACHE = Path("tools/cache/somatic_responsive.jsonl")
EXIT_CACHE = Path("tools/cache/somatic_responsive_exit.jsonl")
ARMS = ("bone", "friend", "vanilla", "textbook")


def read_rows(path: Path) -> list:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def latest_by_arm(rows: list, topic: str) -> dict:
    """{arm: [records of its latest run, in turn order]}."""
    out = {}
    for arm in ARMS:
        mine = [r for r in rows if r.get("topic") == topic and r.get("arm") == arm]
        if mine:
            run_id = max(r["run"] for r in mine)
            out[arm] = sorted((r for r in mine if r["run"] == run_id), key=lambda r: r["turn"])
    return out


def words(text) -> int:
    return len((text or "").split())


def report(topic: str) -> int:
    arms = latest_by_arm(read_rows(CACHE), topic)
    if not arms:
        print(f"No responsive runs for topic {topic!r}.")
        return 1
    exits = {r["arm"]: r for r in read_rows(EXIT_CACHE) if r.get("topic") == topic}
    print(f"=== SIMULATED-PERSON RUNS, topic {topic!r} ===")
    print(f"  {'arm':<9}{'turns':>6}{'held':>6}{'reply w':>9}{'me w 1st half':>15}{'me w 2nd half':>15}{'fallbacks':>11}")
    for arm, recs in arms.items():
        half = len(recs) // 2
        mine = [words(r["message"]) for r in recs]
        first, second = mine[:half], mine[half:]
        delivered = [r for r in recs if r.get("delivered")]
        print(
            f"  {arm:<9}{len(recs):>6}{len(recs) - len(delivered):>6}"
            f"{sum(words(r['reply']) for r in delivered) / max(1, len(delivered)):>9.0f}"
            f"{sum(first) / max(1, len(first)):>15.1f}{sum(second) / max(1, len(second)):>15.1f}"
            f"{sum(bool(r.get('sim_fallback')) for r in recs):>11}"
        )
    print("\n  Exit interview by the simulated person, 1-7, mean of the samples (higher is more of it):")
    print(f"  {'arm':<9}" + "".join(f"{k:>11}" for k in EXIT_KEYS))
    for arm in arms:
        mean = (exits.get(arm) or {}).get("mean")
        cells = "".join(f"{mean[k]:>11.2f}" for k in EXIT_KEYS) if mean else "  not recorded"
        print(f"  {arm:<9}{cells}")
    print("  Lower is better for lectured and performed. Same simulator for every arm, so read the")
    print("  differences between rows, not the numbers themselves.")
    return 0


def run(args) -> int:
    user = SimulatedUser(args.topic, model=args.sim_model, window=args.sim_window, seed=args.seed)
    run_id = time.strftime("%Y%m%d-%H%M%S")
    if args.arm == "bone":
        import audit_somatic_census as census

        # The census names its own run id; read it back from what it wrote.
        before = len(read_rows(CACHE))
        census.run(args.model, CACHE, topic=args.topic, user=user, max_turns=args.turns)
        written = read_rows(CACHE)[before:]
        run_id = written[-1]["run"] if written else run_id
        transcript = [
            {"me": r["message"], "friend": r["shown"], "delivered": r["delivered"]} for r in written
        ]
    else:
        import audit_somatic_vanilla as vanilla

        before = len(read_rows(CACHE))
        vanilla.run(args.model, args.topic, CACHE, args.arm, user=user, max_turns=args.turns)
        written = read_rows(CACHE)[before:]
        run_id = written[-1]["run"] if written else run_id
        transcript = [{"me": r["message"], "friend": r["reply"], "delivered": True} for r in written]

    print("\n  Exit interview...")
    interview = user.exit_interview(transcript, samples=args.exit_samples)
    with EXIT_CACHE.open("a", encoding="utf-8") as out:
        out.write(
            json.dumps(
                {"run": run_id, "arm": args.arm, "topic": args.topic, "sim_model": args.sim_model, **interview}
            )
            + "\n"
        )
    print(f"  {interview['mean'] or 'no parsable answers'}")
    return report(args.topic)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[2])
    parser.add_argument("--topic", choices=sorted(SCRIPTS), default=DEFAULT_TOPIC)
    parser.add_argument("--arm", choices=ARMS)
    parser.add_argument("--model", default="gemma4:12b", help="the responder")
    parser.add_argument("--sim-model", default=SIM_MODEL)
    parser.add_argument("--sim-window", type=int, default=6, help="exchanges the simulated person remembers")
    parser.add_argument("--exit-samples", type=int, default=3)
    parser.add_argument("--turns", type=int, default=None, help="stop after this many turns")
    parser.add_argument("--seed", type=int, default=20260921)
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    if args.report:
        return report(args.topic)
    if not args.arm:
        parser.error("--arm is required unless --report")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
