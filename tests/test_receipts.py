"""tests/test_receipts.py

ROADMAP A3. A receipt is a structured record issued by the code that performed
the work, stating what it was handed and what came back.

These tests assert two different things and it is worth keeping them apart.
The `Ledger` and `Honesty` cases test the mechanism. The `RollCall` case tests
that the mechanism and the engine have not drifted apart, which is the failure
mode that produced the roadmap in the first place: instrumentation that names
subsystems nothing issues, or subsystems that issue under names nothing watches.
"""

import ast
import os
import unittest

from receipts import CORE_SUBSYSTEMS, Receipt, ReceiptLedger
from tests.base import BoneTestCase

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".venv", ".git", "tests", "__pycache__", "saves", "logs"}


def _python_sources():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".py"):
                yield os.path.join(dirpath, name)


def _issued_subsystem_names():
    """Every string literal passed as the first argument to issue_receipt().

    Parsed rather than grepped so that a name inside a comment or a docstring
    cannot satisfy the roll call.
    """
    found = set()
    for path in _python_sources():
        with open(path, "r", encoding="utf-8") as handle:
            try:
                tree = ast.parse(handle.read(), filename=path)
            except SyntaxError:  # pragma: no cover - a broken file fails elsewhere
                continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if name not in ("issue_receipt", "issue"):
                continue
            if node.args and isinstance(node.args[0], ast.Constant):
                value = node.args[0].value
                if isinstance(value, str):
                    found.add(value)
    return found


class TestReceiptLedger(unittest.TestCase):
    def setUp(self):
        ReceiptLedger.reset_instance()
        self.ledger = ReceiptLedger.get_instance()

    def tearDown(self):
        ReceiptLedger.reset_instance()

    def test_issue_records_what_the_worker_said(self):
        receipt = self.ledger.issue(
            "probe.alpha", "did a thing", result_count=4, inputs={"k": 2}
        )
        self.assertIsInstance(receipt, Receipt)
        self.assertEqual(receipt.result_count, 4)
        self.assertFalse(receipt.degraded)
        self.assertEqual(receipt.inputs, {"k": 2})
        self.assertEqual(self.ledger.for_subsystem("probe.alpha"), [receipt])

    def test_result_count_cannot_be_passed_positionally(self):
        """`result_count` and `degraded` are keyword-only on purpose.

        A positional third argument would let a caller supply a subsystem's own
        verdict by accident, which is the exact authority the contract withholds
        from callers.
        """
        with self.assertRaises(TypeError):
            self.ledger.issue("probe.alpha", "did a thing", 4)

    def test_turn_boundary_partitions_receipts(self):
        self.ledger.begin_turn()
        self.ledger.issue("probe.alpha", "turn one", result_count=1)
        self.ledger.begin_turn()
        self.ledger.issue("probe.alpha", "turn two", result_count=2)
        self.assertEqual(len(self.ledger.for_turn()), 1)
        self.assertEqual(self.ledger.for_turn()[0].result_count, 2)
        self.assertEqual(self.ledger.for_turn(1)[0].result_count, 1)

    def test_ring_buffer_bounds_memory(self):
        self.ledger.capacity = 10
        for i in range(25):
            self.ledger.issue("probe.alpha", "spin", result_count=i)
        held = self.ledger.all()
        self.assertEqual(len(held), 10)
        self.assertEqual(held[-1].result_count, 24)
        self.assertEqual(held[0].result_count, 15)

    def test_sink_receives_every_receipt(self):
        seen = []
        self.ledger.sink = seen.append
        self.ledger.issue("probe.alpha", "a", result_count=1)
        self.ledger.issue("probe.beta", "b", result_count=0)
        self.assertEqual([r.subsystem for r in seen], ["probe.alpha", "probe.beta"])


class TestLiesByOmission(unittest.TestCase):
    """The three states that a liveness flag reports as green."""

    def setUp(self):
        ReceiptLedger.reset_instance()
        self.ledger = ReceiptLedger.get_instance()

    def tearDown(self):
        ReceiptLedger.reset_instance()

    def test_silent_subsystem_is_named(self):
        self.ledger.expect("probe.alpha")
        self.ledger.expect("probe.ghost")
        self.ledger.issue("probe.alpha", "worked", result_count=1)
        self.assertEqual(self.ledger.silent(), {"probe.ghost"})

    def test_chronic_degraded_requires_every_receipt_to_be_degraded(self):
        for _ in range(3):
            self.ledger.issue("probe.fallback", "fell back", result_count=1, degraded=True)
        self.ledger.issue("probe.mixed", "fell back", result_count=1, degraded=True)
        self.ledger.issue("probe.mixed", "worked", result_count=1, degraded=False)
        self.assertIn("probe.fallback", self.ledger.chronic_degraded())
        self.assertNotIn("probe.mixed", self.ledger.chronic_degraded())

    def test_chronic_empty_catches_the_retriever_that_never_retrieves(self):
        for _ in range(4):
            self.ledger.issue("probe.retriever", "searched", result_count=0)
        self.ledger.issue("probe.working", "searched", result_count=0)
        self.ledger.issue("probe.working", "searched", result_count=3)
        self.assertIn("probe.retriever", self.ledger.chronic_empty())
        self.assertNotIn("probe.working", self.ledger.chronic_empty())

    def test_scorecard_reports_all_three_in_one_pass(self):
        self.ledger.expect("probe.ghost")
        self.ledger.begin_turn()
        self.ledger.issue("probe.fallback", "fell back", result_count=0, degraded=True)
        card = self.ledger.scorecard()
        self.assertEqual(card["silent"], ["probe.ghost"])
        self.assertEqual(card["chronic_degraded"], ["probe.fallback"])
        self.assertEqual(card["chronic_empty"], ["probe.fallback"])
        self.assertEqual(len(card["this_turn"]), 1)


class TestRollCall(unittest.TestCase):
    """The roll call and the call sites must not drift apart."""

    def test_every_declared_subsystem_actually_issues_receipts(self):
        issued = _issued_subsystem_names()
        missing = sorted(set(CORE_SUBSYSTEMS) - issued)
        self.assertEqual(
            missing,
            [],
            f"CORE_SUBSYSTEMS names subsystems that issue no receipts: {missing}. "
            "They would show as permanently silent and the signal would be noise.",
        )

    def test_every_issuing_subsystem_is_on_the_roll_call(self):
        issued = {n for n in _issued_subsystem_names() if not n.startswith("probe.")}
        unwatched = sorted(issued - set(CORE_SUBSYSTEMS))
        self.assertEqual(
            unwatched,
            [],
            f"These subsystems issue receipts but are not in CORE_SUBSYSTEMS: "
            f"{unwatched}. Nothing would notice if they went silent.",
        )


class TestRealSubsystemsReport(unittest.TestCase):
    """The receipts the roadmap said each historical failure could not have written.

    Each of these reproduces a state that used to produce fluent output and no
    signal whatsoever, and asserts that the subsystem now says so in its own
    voice rather than a caller inferring it from an empty return.
    """

    def setUp(self):
        ReceiptLedger.reset_instance()
        self.ledger = ReceiptLedger.get_instance()

    def tearDown(self):
        ReceiptLedger.reset_instance()

    def _only(self, subsystem):
        entries = self.ledger.for_subsystem(subsystem)
        self.assertEqual(len(entries), 1, f"expected one {subsystem} receipt, got {entries}")
        return entries[0]

    def test_untrained_index_names_its_illness(self):
        """`mind_memory.ann is None` and an empty index both returned []."""
        from brain.ann import CerebralIndex

        index = CerebralIndex()
        self.assertEqual(index.query_neighborhood([0.0] * index.dimension, k=3), [])
        receipt = self._only("cortex.query_neighborhood")
        self.assertTrue(receipt.degraded)
        self.assertEqual(receipt.result_count, 0)
        self.assertEqual(receipt.detail, "index untrained")
        self.assertFalse(receipt.inputs["trained"])

    def test_dimension_mismatch_is_distinguishable_from_an_empty_index(self):
        from brain.ann import CerebralIndex

        index = CerebralIndex()
        index.is_trained = True
        index.total_nodes = 5
        index.query_neighborhood([0.0] * (index.dimension + 1), k=3)
        receipt = self._only("cortex.query_neighborhood")
        self.assertIn("dimension", receipt.detail)
        self.assertNotEqual(
            receipt.inputs["query_dim"], receipt.inputs["index_dim"]
        )

    def test_governor_reports_the_pid_fallback_it_used_to_hide(self):
        """The handler that swallowed a TypeError every turn for the project's life."""
        from unittest.mock import patch as mock_patch

        from core import CyberneticGovernor

        governor = CyberneticGovernor()
        physics = {"voltage": 30.0, "narrative_drag": 0.6}
        with mock_patch.object(
            CyberneticGovernor,
            "_bitmap_regulation",
            side_effect=TypeError("argument 'dim': 'numpy.ndarray' object cannot be interpreted as an integer"),
        ):
            governor.regulate(physics, 1.0, memory_core=object(), user_text="anything")
        receipt = self._only("governor.bitmap_gate")
        self.assertTrue(receipt.degraded)
        self.assertEqual(receipt.result_count, 0)
        self.assertIn("TypeError", receipt.detail)
        self.assertIn("dim", receipt.detail)

    def test_governor_reports_an_utterance_that_never_arrived(self):
        """The bug the receipts found: the PDE was anchored on a stale scrape.

        `regulate` was handed a memory core and an empty `user_text` on every
        turn, because the utterance was read back out of a dialogue buffer that
        is not written until after the model has already replied.
        """
        from core import CyberneticGovernor

        governor = CyberneticGovernor()
        governor.regulate({"voltage": 30.0}, 1.0, memory_core=object(), user_text="")
        receipt = self._only("governor.bitmap_gate")
        self.assertTrue(receipt.degraded)
        self.assertTrue(receipt.inputs["memory_core"])
        self.assertFalse(receipt.inputs["user_text"])
        self.assertIn("no utterance", receipt.detail)

    def test_a_pid_only_caller_does_not_forge_a_failed_solve(self):
        """CycleStabilizer wants a PID loop and passes neither input.

        Reporting that as a degraded Creative Determinant would bury the calls
        where one of the two inputs really did go missing, which is the only
        thing this receipt is for.
        """
        from core import CyberneticGovernor

        governor = CyberneticGovernor()
        governor.regulate({"voltage": 30.0}, 1.0, memory_core=None, user_text="")
        self.assertEqual(self.ledger.for_subsystem("governor.bitmap_gate"), [])

    def test_word_resolution_reports_each_stage_separately(self):
        """13% lexicon coverage and 81% coverage produced identical prose."""
        from mechanics.lexicon import LexiconService
        from physics.observer import QuantumObserver

        lex = LexiconService()
        lex.initialize()
        words = lex.clean("the heavy iron hammer fell on the anvil and the forge rang")
        QuantumObserver._tally_categories_static(lex, words)
        receipt = self._only("physics.word_resolution")
        self.assertEqual(receipt.inputs["words"], len(words))
        stages = ("solvent", "lexicon", "resonance", "taste", "unresolved")
        self.assertEqual(
            sum(receipt.inputs[s] for s in stages),
            receipt.inputs["words"],
            "every word must be accounted for by exactly one resolution stage",
        )
        self.assertEqual(
            receipt.result_count,
            receipt.inputs["words"] - receipt.inputs["unresolved"],
        )


class TestRollCallOnARealTurn(BoneTestCase):
    """The acceptance test for A3: a whole turn, and what it says about itself.

    Every unit test above proves a subsystem can write a receipt. This one
    proves the receipts arrive during an actual cycle, which is the only claim
    that matters; the subsystems in the roadmap table were all individually
    correct and collectively disconnected.
    """

    def test_a_turn_produces_receipts_from_the_subsystems_that_ran(self):
        ledger = ReceiptLedger.get_instance()
        self.engine.orchestrator.run_turn("the heavy iron hammer rang on the anvil")

        reported = {r.subsystem for r in ledger.all()}
        self.assertTrue(reported, "a complete turn issued no receipts at all")
        for required in ("physics.word_resolution", "composer.compose"):
            self.assertIn(
                required,
                reported,
                f"{required} ran during the turn and said nothing about it",
            )

    def test_receipts_are_attributed_to_the_turn_that_produced_them(self):
        ledger = ReceiptLedger.get_instance()
        self.engine.orchestrator.run_turn("the first utterance, about forges")
        first = ledger.turn
        self.engine.orchestrator.run_turn("the second utterance, about rivers")
        self.assertGreater(ledger.turn, first)
        self.assertTrue(ledger.for_turn(first), "the first turn's receipts were lost")
        self.assertTrue(
            all(r.turn == ledger.turn for r in ledger.for_turn()),
            "for_turn() returned receipts belonging to another turn",
        )

    def test_the_thermal_lock_reaches_the_prompt(self):
        """`composer.compose` reports degraded when the eigenvalue never arrives.

        This is the receipt the roadmap said lambda_1 could not have written
        while it was being computed and discarded.
        """
        ledger = ReceiptLedger.get_instance()
        from unittest.mock import patch as mock_patch
        with mock_patch("core.CyberneticGovernor.regulate", return_value=(0.0, 0.0)):
            self.engine.governor.last_z = 2.0
            self.engine.orchestrator.run_turn("a rich and coherent thing to say")
        composed = ledger.for_subsystem("composer.compose")
        self.assertTrue(composed, "the composer assembled a prompt and said nothing")
        latest = composed[-1]
        self.assertIn("thermal_lock", latest.inputs["blocks"])
        self.assertFalse(
            latest.degraded,
            f"the prompt went out without a thermal lock: {latest.detail}",
        )
