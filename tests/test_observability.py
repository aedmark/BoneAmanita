"""tests/test_observability.py

Guards for the failure mode this codebase is most prone to: a subsystem that
stops working without saying anything. The engine's only output is prose, and
prose looks identical whether the physics ran or returned a default, so silent
degradation is invisible by construction. See ROADMAP.md track A.
"""

import ast
import logging
import subprocess
import unittest
from unittest.mock import MagicMock

from core import EventBus

SEVERITIES = {"CRIT", "CRITICAL", "ERROR", "WARN", "WARNING"}


def _source_files():
    out = subprocess.check_output(["git", "ls-files", "*.py"], text=True).split()
    return [f for f in out if not f.startswith(("tests/", "tools/"))]


class LogSeverityRouting(unittest.TestCase):
    """EventBus.log is (message, source, level). A severity in the source slot
    used to leave level at INFO, routing the line to logger.debug and muting it
    entirely, including the daemon's own crash handler."""

    def test_no_severity_passed_in_the_source_position(self):
        offenders = []
        for path in _source_files():
            try:
                tree = ast.parse(open(path, encoding="utf-8").read())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "log"
                    and len(node.args) == 2
                    and isinstance(node.args[1], ast.Constant)
                    and node.args[1].value in SEVERITIES
                ):
                    offenders.append(f"{path}:{node.lineno} -> {node.args[1].value!r}")
        self.assertEqual(
            offenders,
            [],
            "[FAIL] These pass a severity where `source` belongs, which mutes them.\n"
            "Use log(msg, SOURCE, SEVERITY):\n  " + "\n  ".join(offenders),
        )

    def test_severity_escalates_to_the_logger(self):
        bus = EventBus()
        with self.assertLogs("bone", level=logging.WARNING) as captured:
            bus.log("a real problem", "CYCLE", "CRIT")
        self.assertTrue(any("a real problem" in line for line in captured.output))

    def test_two_arg_severity_form_is_still_honoured(self):
        """The guard must catch the legacy spelling rather than drop it."""
        bus = EventBus()
        with self.assertLogs("bone", level=logging.WARNING) as captured:
            bus.log("legacy spelling", "CRIT")
        self.assertTrue(any("legacy spelling" in line for line in captured.output))
        self.assertEqual(bus.buffer[-1]["level"], "CRIT")

    def test_routine_lines_do_not_flood_stderr(self):
        """The TUI renders the buffer; ordinary lines must stay off the handler."""
        bus = EventBus()
        with self.assertNoLogs("bone", level=logging.WARNING):
            bus.log("routine telemetry", "BIO")
        self.assertEqual(bus.buffer[-1]["level"], "INFO")

    def test_source_is_preserved_for_event_routing(self):
        bus = EventBus()
        seen = []
        bus.subscribe("CYCLE", lambda payload: seen.append(payload))
        bus.log("routed", "CYCLE", "CRIT")
        self.assertTrue(seen, "[FAIL] log() stopped publishing on its source tag.")


class SilentExceptionHandlers(unittest.TestCase):
    """A budget, not a ban. Some catches are legitimate (backend probes, cache
    warms); the point is that the count cannot quietly grow."""

    # A ratchet, not a ceiling: lower it when the count drops, never raise it.
    # It has already caught one regression (the resonance classifier shipped
    # with three silent catches and this test refused them).
    #
    # A2 took this from 72 to 28. Most of what remains reports through a house
    # helper this AST walk cannot see (`self._log`, `self._dream_failed`,
    # `handle_phase_crash`, an `err` string carried to a later raise), so the
    # number overstates the problem. The unambiguous measure is the
    # pass-only ban below, which is at zero tolerance.
    BUDGET = 30

    def test_silent_handler_count_does_not_grow(self):
        silent = []
        for path in _source_files():
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
                        (
                            isinstance(n.func, ast.Attribute)
                            and n.func.attr
                            in {"log", "warning", "error", "critical", "exception", "print"}
                        )
                        or (isinstance(n.func, ast.Name) and n.func.id == "print")
                    )
                    for n in inner
                )
                if not (has_raise or has_log):
                    silent.append(f"{path}:{node.lineno}")
        self.assertLessEqual(
            len(silent),
            self.BUDGET,
            f"[FAIL] Silent exception handlers grew to {len(silent)} (budget "
            f"{self.BUDGET}). A new catch must log or re-raise. Run "
            f"`python tools/audit_handlers.py` to see them all.",
        )

    # The three handlers whose entire body is `pass`, and why each one is right.
    # This is an allowlist rather than a budget because every entry has to be
    # argued for in writing, and a reviewer can disagree with a line of it.
    PASS_ONLY_ALLOWED = {
        "core.py": (
            "JSONEncoder.default walks __slots__, and a declared-but-unset slot "
            "raises AttributeError by design. Skipping it IS the algorithm."
        ),
        "drivers/userprofile.py": (
            "No profile on first run is the normal state, not a fault. The "
            "unreadable and corrupt cases were split out and do report."
        ),
        "spores/embeddings.py": (
            "SemanticEmbedder._log is the logger of last resort: if the EventBus "
            "raises, it falls through to print() and the message still arrives. "
            "There is nowhere to report a failure to report."
        ),
    }

    def test_no_new_pass_only_handlers(self):
        """A handler whose whole body is `pass` or `continue` and nothing else.

        This is the unambiguous half of the problem: whatever a reader might
        argue about a handler that sets a flag or returns a default, a body of
        `pass` provably discards the exception and leaves no trace anywhere.
        Every one that survives here is named above with its reason.
        """
        offenders = []
        for path in _source_files():
            try:
                tree = ast.parse(open(path, encoding="utf-8").read())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ExceptHandler):
                    continue
                if len(node.body) != 1:
                    continue
                if not isinstance(node.body[0], (ast.Pass, ast.Continue)):
                    continue
                if path in self.PASS_ONLY_ALLOWED:
                    continue
                exc = ast.unparse(node.type) if node.type else "BARE"
                offenders.append(f"{path}:{node.lineno} (except {exc})")
        self.assertEqual(
            offenders,
            [],
            "[FAIL] These handlers discard an exception and leave no trace:\n  "
            + "\n  ".join(offenders)
            + "\n\nEither log it, re-raise it, or add the file to "
            "PASS_ONLY_ALLOWED with a written reason.",
        )

    def test_the_allowlist_has_not_gone_stale(self):
        """An allowlist entry for a file that no longer needs one is a lie.

        Left unchecked it silently re-permits the pattern in that whole file,
        which is how an exception list becomes an exception.
        """
        pass_only_files = set()
        for path in _source_files():
            try:
                tree = ast.parse(open(path, encoding="utf-8").read())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.ExceptHandler)
                    and len(node.body) == 1
                    and isinstance(node.body[0], (ast.Pass, ast.Continue))
                ):
                    pass_only_files.add(path)
        stale = sorted(set(self.PASS_ONLY_ALLOWED) - pass_only_files)
        self.assertEqual(
            stale,
            [],
            f"[FAIL] These files are on PASS_ONLY_ALLOWED but no longer contain a "
            f"pass-only handler: {stale}. Remove them from the allowlist.",
        )


class ConfigStrictness(unittest.TestCase):
    """Ten config constants were absent from every config file for the life of
    the project, so their subsystems ran on inline fallbacks and tuning them did
    nothing. The manifest makes that state detectable at boot."""

    def test_shipped_manifest_fully_resolves(self):
        from genesis import BoneGenesis
        from presets import BoneConfig

        missing = BoneGenesis._audit_config(BoneConfig, EventBus())
        self.assertEqual(
            missing,
            [],
            "[FAIL] Config keys declared in BoneConfig.REQUIRED_CONFIG do not "
            "resolve. Either add them to lore/tuning_presets.json or remove them "
            "from the manifest: " + ", ".join(missing),
        )

    def test_audit_reports_every_miss_at_once(self):
        from struts import audit_cfg

        manifest = {"BLOCK": ["PRESENT", "GONE_A", "GONE_B"]}
        missing = audit_cfg(manifest, lambda _b: {"PRESENT": 1})
        self.assertEqual(missing, ["BLOCK.GONE_A", "BLOCK.GONE_B"])

    def test_require_cfg_raises_instead_of_defaulting(self):
        from struts import ConfigError, require_cfg

        self.assertEqual(require_cfg({"K": 5}, "K", where="test"), 5)
        with self.assertRaises(ConfigError):
            require_cfg({}, "ABSENT", where="test")

    def test_the_previously_missing_keys_now_resolve(self):
        """Regression for the specific ten found by tools/audit_safe_get.py."""
        from presets import BoneConfig
        from struts import safe_get

        expected = {
            "CORTEX": ["BASE_TOKENS", "MAX_TOKENS", "SELF_CARE_THRESHOLD",
                       "LLM_FAILURE_THRESHOLD", "MAX_HISTORY_LENGTH"],
            "MACHINE": ["PACEMAKER_BOREDOM_THRESHOLD"],
            "DRIVERS": ["LIMINAL_SCAR_RELIEF", "LIMINAL_TRAUMA_HEAL",
                        "LIMINAL_TRAUMA_AGGRAVATE", "LIMINAL_STRESS_THRESH"],
        }
        for block, keys in expected.items():
            scope = safe_get(BoneConfig, block, {})
            for key in keys:
                self.assertIsNotNone(
                    safe_get(scope, key, None),
                    f"[FAIL] {block}.{key} is absent again.",
                )

    def test_governor_shift_resolves_from_the_lore_manifest(self):
        """Regression: regulation.py read BODY_CONFIG off BoneConfig, where it
        has never lived, so GOVERNOR_SHIFT was always {}."""
        from core import LoreManifest

        body_cfg = LoreManifest.get_instance().get("BODY_CONFIG") or {}
        self.assertTrue(
            body_cfg.get("GOVERNOR_SHIFT"),
            "[FAIL] GOVERNOR_SHIFT missing from lore/body_config.json.",
        )


if __name__ == "__main__":
    unittest.main()
