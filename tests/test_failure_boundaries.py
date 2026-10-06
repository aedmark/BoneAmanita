"""tests/test_failure_boundaries.py

The fail-loudly codemod (2f70ddf) removed every `except Exception`, including the ones A2 had kept on
purpose: optional backends, retries and crash barriers. These pin the ones restored in 20.7.4.83, each
reported (crashes.log, a log line or both) and each narrowed where the failure has a known type.
"""

import http.client
import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


class ACommandThatFails(unittest.TestCase):
    def test_is_reported_and_the_session_goes_on(self):
        from mechanics.commands import CommandRegistry

        state = MagicMock()
        registry = CommandRegistry(state)
        registry.register("/boom", MagicMock(side_effect=RuntimeError("broke")), "fails")
        self.assertTrue(registry.execute("/boom"))
        self.assertIn("/boom failed: RuntimeError: broke", state.log.call_args.args[0])


class TheTransport(unittest.TestCase):
    def test_a_reset_mid_response_is_retried(self):
        from brain.composer import LLMInterface

        ok = MagicMock(status=200)
        ok.read.return_value = json.dumps({"choices": [{"message": {"content": "hello"}}]}).encode()
        ok.__enter__.return_value = ok
        llm = LLMInterface(events_ref=MagicMock(), provider="ollama", model="m")
        with patch("urllib.request.urlopen", side_effect=[http.client.RemoteDisconnected("gone"), ok]), \
                patch("time.sleep"):
            self.assertEqual(llm._transmit({"messages": []}, network_retries=1, override_url="http://x"), "hello")

    def test_a_failed_local_fallback_lets_the_breaker_decide(self):
        from brain.composer import LLMInterface, TransientError

        llm = LLMInterface(events_ref=MagicMock(), provider="ollama", model="m")
        with patch.object(llm, "_transmit", side_effect=TransientError("down")):
            self.assertIsNone(llm._local_fallback({"messages": []}))


class TheCritic(unittest.TestCase):
    def critic(self, judge):
        from mechanics.dspycritic import DSPyCritic

        c = DSPyCritic.__new__(DSPyCritic)
        c.enabled, c.judge = True, judge
        c.navi_sad = SimpleNamespace(calculate_malignancy_factor=lambda *a, **k: 0.0)
        return c

    def test_an_unreachable_judge_fails_open(self):
        ok, why = self.critic(MagicMock(side_effect=ConnectionError("no e4b"))).audit_generation("q", "", "a")
        self.assertTrue(ok)
        self.assertIn("unavailable", why)

    def test_a_judge_that_never_answers_fails_open_at_the_cap(self):
        """feud20 (2026-10-05): one judge call took 71.5s, and with retries turns ran past the 240s loop limit."""
        import socket
        import time

        from mechanics.dspycritic import DSPyCritic

        silent = socket.socket()
        silent.bind(("127.0.0.1", 0))
        silent.listen()
        url = f"http://127.0.0.1:{silent.getsockname()[1]}/v1"
        critic = DSPyCritic({"PROVIDER": "ollama", "BASE_URL": url, "DSPY_TIMEOUT": 1.0})
        critic.navi_sad = SimpleNamespace(calculate_malignancy_factor=lambda *a, **k: 0.0)
        start = time.monotonic()
        ok, why = critic.audit_generation(f"q {start}", "", "a")
        silent.close()
        self.assertTrue(ok)
        self.assertIn("unavailable", why)
        self.assertLess(time.monotonic() - start, 5.0)

    def test_only_the_library_call_is_covered(self):
        broken = MagicMock(return_value=object())  # no .faithfulness: our parsing, not the library
        with self.assertRaises(AttributeError):
            self.critic(broken).audit_generation("q", "", "a")


class Checkpoints(unittest.TestCase):
    def keeper(self, **eng):
        from protocols.chronos import ChronosKeeper

        return ChronosKeeper(SimpleNamespace(events=MagicMock(), **eng))

    def test_a_resume_that_cannot_read_starts_fresh(self):
        k = self.keeper()
        with patch.object(k, "_load_checkpoint", side_effect=ValueError("corrupt")):
            self.assertEqual(k.resume_checkpoint(), (False, []))

    def test_shutdown_persists_each_subsystem_alone(self):
        akashic = SimpleNamespace(save_all=MagicMock())
        k = self.keeper(tick_count=1, lex=SimpleNamespace(save=MagicMock(side_effect=OSError("disk full"))),
                        akashic=akashic, village=SimpleNamespace(), mind=None)
        k.perform_shutdown()
        akashic.save_all.assert_called_once()

    def test_one_bad_villager_does_not_stop_the_rest(self):
        good = SimpleNamespace(load_state=MagicMock())
        bad = SimpleNamespace(load_state=MagicMock(side_effect=KeyError("x")))
        k = self.keeper(village=SimpleNamespace(bad=bad, good=good))
        k._restore_village_state({"bad": {}, "good": {"a": 1}})
        good.load_state.assert_called_once_with({"a": 1})


class FileWrites(unittest.TestCase):
    def test_a_disk_error_is_retried_not_raised(self):
        from mechanics.tools import TheSubstrate

        with tempfile.TemporaryDirectory() as d:
            sub = TheSubstrate(MagicMock())
            sub.pending_writes = [{"path": "a.txt", "content": "x"}]
            with patch.object(sub, "_base_dir", return_value=os.path.realpath(d)), \
                    patch("builtins.open", side_effect=PermissionError("read-only")):
                logs, _ = sub.execute_writes(100.0)
            self.assertEqual(sub.pending_writes[0]["retries"], 1)
            self.assertIn("Retrying (1/3)", logs[-1])


class TheConfigFile(unittest.TestCase):
    def test_a_corrupt_one_is_backed_up_and_set_up_again(self):
        from mechanics.setup import ConfigWizard

        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "config.json")
            open(path, "w").write("{not json")
            with patch.object(ConfigWizard, "CONFIG_FILE", path), \
                    patch.object(ConfigWizard, "_run_setup", return_value={"fresh": True}):
                self.assertEqual(ConfigWizard.load_or_create(), {"fresh": True})
            self.assertFalse(os.path.exists(path))
            self.assertEqual(len([f for f in os.listdir(d) if f.endswith(".bak")]), 1)


class TheEventBus(unittest.TestCase):
    def test_one_failing_subscriber_does_not_silence_the_rest(self):
        from engine.core import EventBus

        bus, heard = EventBus(), []
        bus.subscribe("PING", MagicMock(side_effect=RuntimeError("bad listener")))
        bus.subscribe("PING", heard.append)
        bus.publish("PING", 1)
        self.assertEqual(heard, [1])


class TheAtlas(unittest.TestCase):
    def test_a_node_that_cannot_be_restored_is_dropped_not_fatal(self):
        from archetypes.village import TheCartographer

        c = TheCartographer.__new__(TheCartographer)
        c.world_graph = {}
        c._init_genesis = lambda: c.world_graph.setdefault("GENESIS_POINT", object())
        c.load_state({"nodes": {"bad": {"nonsense": True}}, "current_id": "GENESIS_POINT"})
        self.assertNotIn("bad", c.world_graph)


if __name__ == "__main__":
    unittest.main()
