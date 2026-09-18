"""Shutdown must finish background work before persistence and telemetry stop."""

import threading
import unittest
from unittest.mock import patch

from tests.base import BoneTestCase


class EngineShutdownTests(BoneTestCase):
    def test_idle_daemon_stops_before_persistence(self):
        orchestrator = self.engine.orchestrator
        self.assertTrue(orchestrator.daemon_thread.is_alive())

        def persist():
            self.assertFalse(orchestrator.is_running)
            self.assertFalse(orchestrator.daemon_thread.is_alive())

        with patch.object(self.engine.chronos, "perform_shutdown", side_effect=persist):
            self.engine.shutdown()
            self.engine.shutdown()

    def test_shutdown_waits_for_background_work_before_persistence(self):
        self._assert_shutdown_waits(for_turn=False)

    def test_shutdown_waits_for_active_turn_before_persistence(self):
        self._assert_shutdown_waits(for_turn=True)

    def _assert_shutdown_waits(self, for_turn):
        started = threading.Event()
        release = threading.Event()
        finished = threading.Event()
        persisted = threading.Event()
        errors = []

        def work(*args):
            started.set()
            release.wait(5)
            finished.set()
            return {"type": "TEST"}

        orchestrator = self.engine.orchestrator
        if for_turn:
            turn_patch = patch.object(orchestrator, "run_turn", side_effect=work)
            turn_patch.start()
            self.addCleanup(turn_patch.stop)
            orchestrator.input_queue.put(("test", False))
        else:
            future = orchestrator._async_pool.submit(work)
        self.assertTrue(started.wait(2))

        def persist():
            if not finished.is_set():
                errors.append("Persistence ran while a worker was still active")
            persisted.set()

        def shutdown():
            try:
                self.engine.shutdown()
            except Exception as exc:
                errors.append(exc)

        with patch.object(self.engine.chronos, "perform_shutdown", side_effect=persist):
            thread = threading.Thread(target=shutdown)
            thread.start()
            try:
                self.assertFalse(persisted.wait(0.2))
            finally:
                release.set()
                thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertTrue(persisted.is_set())
        if for_turn:
            self.assertEqual(orchestrator.input_queue.unfinished_tasks, 0)
            self.assertEqual(orchestrator.output_queue.get_nowait()["type"], "TEST")
        else:
            self.assertTrue(future.done())
        self.assertFalse(orchestrator.daemon_thread.is_alive())


class FixtureShutdownTests(unittest.TestCase):
    def test_subclass_setup_failure_still_stops_engine(self):
        engines = []

        class FailingSetup(BoneTestCase):
            def setUp(self):
                super().setUp()
                engines.append(self.engine)
                raise RuntimeError("Deliberate setup failure")

            def runTest(self):
                pass

        result = unittest.TestResult()
        case = FailingSetup()
        try:
            case.run(result)
            self.assertEqual(len(result.errors), 1)
            self.assertIn("Deliberate setup failure", result.errors[0][1])
            self.assertEqual(len(engines), 1)
            self.assertFalse(engines[0].orchestrator.daemon_thread.is_alive())
        finally:
            # Keep the failing regression safe on the old fixture too.
            for engine in engines:
                engine.orchestrator.is_running = False
                engine.orchestrator.daemon_thread.join(2)
            case.doCleanups()
