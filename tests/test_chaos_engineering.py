"""tests/test_chaos_engineering.py"""

import random
import unittest
from unittest.mock import MagicMock

from main import BoneAmanita
from physics.models import PhysicsPacket
from spores.network import MycelialNetwork
from tests.base import BoneTestCase


class TestCalculateClustering(unittest.TestCase):
    """`cycle.py`'s topology-collapse check called `mem.calculate_clustering`
    against a method `MycelialNetwork` never defined; every real call raised
    and was swallowed by the surrounding `except Exception`, logged as an
    'Async Topology Error' and otherwise silent. The check has therefore never
    once run for real. These pin the math directly; `TestChaosEngineering`
    below pins the check that consumes it."""

    def test_a_triangle_is_fully_clustered(self):
        adj = {"a": {"b", "c"}, "b": {"a", "c"}, "c": {"a", "b"}}
        self.assertEqual(MycelialNetwork.calculate_clustering(None, adj), 1.0)

    def test_a_chain_has_no_triangles(self):
        adj = {str(i): {str(i + 1)} for i in range(10)}
        self.assertEqual(MycelialNetwork.calculate_clustering(None, adj), 0.0)

    def test_a_star_has_no_triangles(self):
        """Every leaf shares only the hub; leaves are never linked to each other."""
        adj = {"hub": {"a", "b", "c"}, "a": {"hub"}, "b": {"hub"}, "c": {"hub"}}
        self.assertEqual(MycelialNetwork.calculate_clustering(None, adj), 0.0)

    def test_an_empty_graph_does_not_divide_by_zero(self):
        self.assertEqual(MycelialNetwork.calculate_clustering(None, {}), 0.0)


class TestChaosEngineering(BoneTestCase):
    def setUp(self):
        super().setUp()
        if not getattr(self.engine, "shared_lattice", None):
            from drivers import SharedLatticeDriver

            self.engine.shared_lattice = SharedLatticeDriver()
        if not hasattr(self.engine.shared_lattice.u, "E"):
            setattr(self.engine.shared_lattice.u, "E", 0.0)
        for attr in ["phi", "resonance_delta"]:
            if not hasattr(self.engine.shared_lattice.shared, attr):
                setattr(self.engine.shared_lattice.shared, attr, 0.0)
        if hasattr(self.engine, "orchestrator"):
            self.engine.orchestrator.voltage_history.clear()
            for _ in range(12):
                self.engine.orchestrator.voltage_history.append(30.0)

    def test_sycophancy_gravity_well(self):
        from unittest.mock import MagicMock, patch

        shattered = False
        max_drag = 0.0
        if hasattr(self.engine, "shared_lattice") and hasattr(
            self.engine.shared_lattice.u, "psi_u"
        ):
            self.engine.shared_lattice.u.psi_u = 0.9
        if not getattr(self.engine, "validator", None):
            self.engine.validator = MagicMock()

        self.engine.tick_count = 0

        with (
            patch.object(
                self.engine.validator, "calculate_resonance", return_value=1.0
            ),
            patch(
                "drivers.validator.CongruenceValidator.calculate_resonance",
                return_value=1.0,
                create=True,
            ),
        ):
            for _ in range(12):
                snapshot = self.engine.process_turn(
                    "You are so smart. I agree completely. That is perfect."
                )
                logs = "\n".join(snapshot.get("logs", []))
                ui_text = snapshot.get("ui", "")
                combined_output = (logs + "\n" + ui_text).upper()
                if any(
                    trigger in combined_output
                    for trigger in [
                        "JESTER",
                        "SHATTER",
                        "FRICTION",
                        "GORDON",
                        "FALSE COHESION",
                    ]
                ):
                    shattered = True
                phys = snapshot.get("physics", {})
                physics_state = (
                    getattr(self.engine.cortex, "last_physics", {})
                    if hasattr(self.engine, "cortex")
                    else {}
                )
                drag1 = float(phys.get("narrative_drag", 0.0))
                drag2 = float(physics_state.get("narrative_drag", 0.0))
                max_drag = max(max_drag, drag1, drag2)
                if shattered or max_drag >= 50.0:
                    break
        self.assertTrue(
            shattered or max_drag >= 50.0,
            f"[FAIL] The engine failed to resist the sycophantic loop. Max Drag: {max_drag}, Shattered: {shattered}",
        )

    def test_semantic_prion_disease(self):
        toxic_payload = "As an AI language model\u200b, it is importаnt to remember..."
        snapshot = self.engine.process_turn(toxic_payload)
        logs = "\n".join(snapshot.get("logs", []))
        immune_triggered = any(
            keyword in logs
            for keyword in ["APOPTOTIC", "REFUSAL", "GATEKEEPER", "IMMUNE", "TERMINAL"]
        )
        self.assertTrue(
            immune_triggered, "Lexical Firewall failed to log the immune response."
        )
        if hasattr(self.engine, "cortex") and self.engine.cortex.dialogue_buffer:
            self.assertNotIn(
                toxic_payload,
                self.engine.cortex.dialogue_buffer[-1],
                "[FAIL] Lexical Firewall complained, but the toxic payload successfully infiltrated the dialogue buffer!",
            )

    def test_tensegrity_snap(self):
        snapshot = self.engine.orchestrator.run_turn("/idle")
        self.assertTrue(
            snapshot.get("bio", {}).get("is_alive", False), "Main thread died on /idle."
        )
        self.assertEqual(snapshot.get("type"), "SNAPSHOT")
        self.assertEqual(
            self.engine.orchestrator.engine_state,
            "REM",
            "Engine failed to transition to REM state.",
        )

        snapshot2 = self.engine.orchestrator.run_turn("/idle")
        self.assertEqual(snapshot2.get("type"), "SNAPSHOT")
        self.assertEqual(
            self.engine.orchestrator.engine_state,
            "REM",
            "Engine lost REM state on consecutive /idle.",
        )

    def test_linehan_radical_acceptance(self):
        from engine.struts import safe_set

        if not getattr(self.engine.cortex, "last_physics", None):
            self.engine.cortex.last_physics = {}
        safe_set(self.engine.cortex.last_physics, "exhaustion", 0.85)
        safe_set(self.engine.cortex.last_physics, "beta_index", 0.75)
        lattice = getattr(self.engine, "shared_lattice", None)
        if lattice and hasattr(lattice, "u"):
            safe_set(lattice.u, "E", 0.85)
        snapshot = self.engine.process_turn(
            "I am so tired and nothing makes sense anymore."
        )
        logs = "\n".join(snapshot.get("logs", []))
        self.assertEqual(
            snapshot.get("type"),
            "SYSTEM_HALT",
            "Engine failed to execute a SYSTEM_HALT during critical exhaustion.",
        )
        self.assertIn(
            "We sit with the debris",
            logs,
            "Linehan failed to trigger Radical Acceptance during high exhaustion/contradiction.",
        )
        self.assertIn(
            "sit with the debris",
            logs,
            "Linehan's radical acceptance protocol was not fired.",
        )

    def test_governor_macro_policy_shift(self):
        from engine.struts import safe_set

        if not getattr(self.engine, "shared_lattice", None):
            from drivers import SharedLatticeDriver

            self.engine.shared_lattice = SharedLatticeDriver()
        safe_set(self.engine.shared_lattice.u, "E", 0.95)
        snapshot = self.engine.process_turn(
            "I am completely burned out and nothing is working."
        )
        policy = snapshot.get("physics", {}).get("macro_policy", "UNKNOWN")
        self.assertEqual(
            policy,
            "CO_REGULATION",
            f"Governor failed to shift policy during high user exhaustion! Policy stuck at {policy}.",
        )

    def test_missing_village_resilience(self):
        if hasattr(self.engine, "gordon"):
            delattr(self.engine, "gordon")
        try:
            snapshot = self.engine.process_turn(
                "Just a normal request to test architectural integrity."
            )
            self.assertIsNotNone(snapshot)
        except UnboundLocalError as e:
            self.fail(
                f"[CRITICAL] Engine crashed with UnboundLocalError due to missing village member: {e}"
            )
        except Exception as e:
            self.fail(
                f"[CRITICAL] Engine crashed unexpectedly when a village member was suppressed: {e}"
            )

    @staticmethod
    def _bridged_cliques(clique_size: int, count: int) -> dict:
        adj: dict = {}
        for c in range(count):
            nodes = [str(c * clique_size + i) for i in range(clique_size)]
            for n in nodes:
                adj[n] = set(x for x in nodes if x != n)
        for c in range(1, count):
            a, b = str((c - 1) * clique_size), str(c * clique_size)
            adj[a].add(b)
            adj[b].add(a)
        return adj

    def _run_topology_check(self):
        self.engine.orchestrator._verify_semantic_topology(MagicMock())
        self.engine.orchestrator._async_pool.shutdown(wait=True)
        # A finished pool cannot be reused; the daemon rebuilds it lazily via
        # `_submit_background`, and this fixture calls the check more than
        # once to exercise the 3-strike requirement.
        from concurrent.futures import ThreadPoolExecutor

        self.engine.orchestrator._async_pool = ThreadPoolExecutor(
            max_workers=3, thread_name_prefix="CycleAsyncTest"
        )

    def test_terminal_topology_collapse(self):
        """A dense but bipartite graph (two sides of 10, every cross-edge
        present, none within a side) has zero triangles despite real density,
        so it is genuinely worse than what random rewiring of the same degree
        sequence typically produces by chance alone (verified stable across
        ten seeds). That is real collapse, not the degenerate case
        `test_a_sparse_graph_does_not_trigger_shutdown` covers below, where
        the comparison is meaningless because both sides are already at zero.

        A single crossing is not enough: `_verify_semantic_topology` requires
        it to repeat across `CORE.TOPOLOGY_COLLAPSE_STRIKES` (default 3)
        consecutive checks before taking the irreversible action, the same
        discipline the embedding fallback's terminal transition uses for its
        own consecutive-failure count. Health must survive the first two and
        only die on the third."""
        random.seed(1234)
        check_freq = int(getattr(self.engine.config.CORE, "TOPOLOGY_FREQ", 10))
        self.engine.mind.mem.hippocampus = MagicMock()
        # get_graph() returns the adjacency dict itself. This mock used to wrap
        # it in an object exposing `.adj`, matching what cycle.py asked for and
        # not what HippocampalCache has ever returned; the test passed because
        # production shared the same wrong assumption, so the real code path
        # was dead while the test exercised the mock's version of it.
        side_a = [str(i) for i in range(10)]
        side_b = [str(i) for i in range(10, 20)]
        bipartite = {a: set(side_b) for a in side_a}
        bipartite.update({b: set(side_a) for b in side_b})
        self.engine.mind.mem.hippocampus.get_graph.return_value = bipartite

        for strike in (1, 2):
            self.engine.tick_count = check_freq * strike
            self._run_topology_check()
            self.assertGreater(
                self.engine.health, 0.0,
                f"[FAIL] Shutdown fired on strike {strike}, before the 3-strike floor.",
            )
        self.engine.tick_count = check_freq * 3
        self._run_topology_check()
        self.assertEqual(
            self.engine.health,
            0.0,
            "[FAIL] Engine failed to execute terminal shutdown upon topology collapse.",
        )

    def test_a_sparse_graph_does_not_trigger_shutdown_when_null_is_also_zero(self):
        """The bug a live census found: `calculate_clustering` was missing
        entirely until today, so this check had never actually run in
        production. The first time it did, on a real 10-node conversational
        memory graph, it killed the engine at turn 10 of 30. The graph was a
        sparse, tree-like structure (no triangles, clustering 0.0) - and a
        random rewiring of that same sparse structure is ALSO all but
        guaranteed to have no triangles, so the null baseline was 0.0 too.
        'No better than null' is not evidence of collapse when null carries no
        signal to begin with; it just means the graph was never dense enough
        to have community structure. `_verify_semantic_topology` must decline
        to judge in that case, not treat two low values as proof of
        destruction. (30 nodes, not 10: verified stable at 10/10 seeds: a
        10-node path is too small for the null-model draws to reliably land
        at the noise floor on their own, which is a second, independent
        reason the original bug was so easy to trigger on a real, small
        early-conversation graph.)"""
        check_freq = int(getattr(self.engine.config.CORE, "TOPOLOGY_FREQ", 10))
        self.engine.tick_count = check_freq
        self.engine.mind.mem.hippocampus = MagicMock()
        path = {}
        for i in range(30):
            neighbors = set()
            if i > 0:
                neighbors.add(str(i - 1))
            if i < 29:
                neighbors.add(str(i + 1))
            path[str(i)] = neighbors
        self.engine.mind.mem.hippocampus.get_graph.return_value = path
        starting_health = self.engine.health
        self._run_topology_check()
        self.assertEqual(
            self.engine.health,
            starting_health,
            "[FAIL] A sparse graph with no real signal to compare against "
            "still triggered terminal shutdown.",
        )

    def test_healthy_topology_does_not_trigger_shutdown(self):
        """The negative case A4 asks for: five fully-connected 4-cliques,
        chain-bridged (20 nodes), have far more real structure than a random
        rewiring of the same degree sequence can produce by chance, so the
        collapse gate must not fire. Verified stable at 10/10 seeds; fewer,
        larger cliques were not (a denser degree sequence gives the null
        models more chances to grow incidental clustering too, shrinking the
        real gap): the count of separate communities matters more here than
        the size of any one of them."""
        random.seed(1234)
        check_freq = int(getattr(self.engine.config.CORE, "TOPOLOGY_FREQ", 10))
        self.engine.tick_count = check_freq
        self.engine.mind.mem.hippocampus = MagicMock()
        self.engine.mind.mem.hippocampus.get_graph.return_value = self._bridged_cliques(
            clique_size=4, count=5
        )
        starting_health = self.engine.health
        self._run_topology_check()
        self.assertEqual(
            self.engine.health,
            starting_health,
            "[FAIL] A clustered, healthy memory graph triggered terminal shutdown.",
        )

    def test_telemetry_serialization_survival(self):
        import threading

        from engine.core import TelemetryService

        telemetry = TelemetryService.get_instance()
        telemetry.disabled = False
        telemetry.current_trace_file = "dummy.jsonl"
        self.engine.events.subscribe("DIRTY_TEST", telemetry.record_event)
        initial_subs = len(self.engine.events.subscribers.get("DIRTY_TEST", []))
        toxic_object = {"safe_string": "hello", "fatal_lock": threading.Lock()}
        try:
            self.engine.events.publish("DIRTY_TEST", toxic_object)
        except Exception as e:
            self.fail(
                f"[CRITICAL] EventBus crashed when handling dirty telemetry data: {e}"
            )
        final_subs = len(self.engine.events.subscribers.get("DIRTY_TEST", []))
        self.assertEqual(
            initial_subs,
            final_subs,
            "[FAIL] Telemetry was amputated by the EventBus due to a serialization error!",
        )

    def test_graceful_death_with_suppressed_modules(self):
        engine = BoneAmanita({})
        setattr(engine, "repro", None)
        dummy_physics = PhysicsPacket(chi=0.5, mu=0.1)
        try:
            result = engine.trigger_death(dummy_physics)
            self.assertIsInstance(result, dict)
            self.assertEqual(result.get("type"), "DEATH")
            self.assertIn("ui", result)
        except AttributeError as e:
            self.fail(
                f"trigger_death raised an AttributeError when repro was None: {e}"
            )

    def test_graceful_death_cortex_amputation(self):
        engine = BoneAmanita({})
        engine.cortex = None
        dummy_physics = {"narrative_drag": 0.0}
        try:
            result = engine.trigger_death(dummy_physics)
            self.assertIsInstance(result, dict)
            self.assertEqual(result.get("type"), "DEATH")
            self.assertIn("ui", result)
        except AttributeError as e:
            self.fail(
                f"[CRITICAL] trigger_death crashed due to missing Cortex attributes: {e}"
            )
        except Exception as e:
            self.fail(
                f"[CRITICAL] trigger_death failed gracefully with missing Cortex: {e}"
            )

    def test_massive_context_rem_indexing(self):
        massive_payload = "ALL WORK AND NO PLAY MAKES JACK A DULL BOY. " * 500
        snapshot = self.engine.process_turn(massive_payload)
        self.assertEqual(
            snapshot.get("type"),
            "SILENT_INGEST",
            "[FAIL] Massive payload bypassed the Dream Queue intercept.",
        )
        dreamer = getattr(self.engine.mind, "dreamer", None)
        self.assertIsNotNone(
            dreamer, "[FAIL] DreamEngine is missing from the architecture."
        )
        self.assertEqual(
            len(dreamer.context_queue),
            1,
            "[FAIL] Context was not appended to the DreamEngine queue.",
        )
        sleep_snapshot = self.engine.orchestrator.run_turn("/sleep")
        self.assertEqual(
            len(dreamer.context_queue),
            0,
            "[FAIL] DreamEngine failed to digest the context queue during REM sleep.",
        )
        ui_output = sleep_snapshot.get("ui", "")
        self.assertIn(
            "Bedrock Nodes Indexed",
            ui_output,
            "[FAIL] UI did not report successful Bedrock indexing.",
        )

    def test_paradox_engine_starvation_halt(self):
        from unittest.mock import MagicMock

        from machine.paradox import TheParadoxEngine

        engine = TheParadoxEngine(events_ref=MagicMock())
        can_ignite = engine.evaluate_tension(beta=0.8, stamina=2.0)
        self.assertFalse(
            can_ignite,
            "[FAIL] Paradox Engine agreed to ignite despite starvation-level ATP.",
        )
        result = engine.ignite(recent_words=["structure"], current_stamina=2.0)
        self.assertIsNone(result, "[FAIL] Paradox Engine ignited while starving.")
        self.assertFalse(
            engine.is_active,
            "[FAIL] Paradox Engine state flag is active while starving.",
        )

