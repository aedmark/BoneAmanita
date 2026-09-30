"""Crash recovery (Gordon, 2026-09-30). A crashed component came back only in the REM tick, after minutes
idle, so a busy or scripted session ran without it for good. It is now retried on the next turn, the wait
doubling per repeat crash (1, 2, 4, up to 8 turns)."""

from unittest.mock import MagicMock, patch

from phases.biological import MetabolismPhase
from tests.base import BoneTestCase


class ComesBack(BoneTestCase):
    ALLOWS_PHASE_CRASH = True

    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value="The path forks.")
        self.health = self.engine.system_health
        self.ran = 0
        real = MetabolismPhase.run

        def run(phase, ctx):
            self.ran += 1
            if self.crash:
                raise RuntimeError("metabolism fell over")
            return real(phase, ctx)

        patcher = patch.object(MetabolismPhase, "run", run)
        patcher.start()
        self.addCleanup(patcher.stop)

    def turn(self):
        self.engine.process_turn("I walk north toward the old mill")

    def test_one_crash_is_retried_on_the_next_turn(self):
        self.crash = True
        self.turn()
        self.assertFalse(self.health.components_online["bio"])
        self.crash = False
        self.turn()
        self.assertTrue(self.health.components_online["bio"])
        self.assertEqual(self.ran, 2)
        self.assertNotIn("bio", self.health.strikes)

    def test_repeat_crashes_wait_longer_each_time(self):
        self.crash = True
        runs_by_turn = []
        for _ in range(8):
            before = self.ran
            self.turn()
            runs_by_turn.append(self.ran - before)
        # Crash on turn 1; retried after 1 turn, then 2, then 4.
        self.assertEqual(runs_by_turn, [1, 1, 0, 1, 0, 0, 0, 1])

    def test_the_wait_is_capped(self):
        for _ in range(10):
            self.health.report_failure("BIO", RuntimeError("again"))
        self.assertEqual(self.health.retry_in["bio"], self.health.RETRY_CAP)


class NoTurnLost(BoneTestCase):
    """The gate commits mid-turn and the checkpoint is saved at the turn's end: a crash between them left the
    store a turn ahead of the resume point. Resume fills the dialogue back in from the store's messages."""

    def commit(self, said, answered):
        from engine.gate.kernel import Gate

        seq, state = self.engine.store.state()
        gate = Gate(self.engine.boundary, state, self.engine.gate_tools, self.engine.gate_invariants)
        self.engine.store.commit_cycle("t", gate.state, seq, gate.adjudicate(answered), answered,
                                       user_text=said, display=answered)

    def test_a_turn_committed_after_the_checkpoint_is_resumed(self):
        self.engine.store.save_checkpoint({"chat_history": ["Traveler: hi\nSystem: Hello."]})
        self.commit("", "A reflection, no one spoke.")
        self.commit("My sister Odalys visits Thursday.", "Thursday, then.")
        ok, history = self.engine.chronos.resume_checkpoint()
        self.assertTrue(ok)
        self.assertEqual(history, ["Traveler: hi\nSystem: Hello.",
                                   "Traveler: My sister Odalys visits Thursday.\nSystem: Thursday, then."])

    def test_nothing_is_added_when_the_checkpoint_is_current(self):
        self.commit("Earlier.", "Before the checkpoint.")
        self.engine.store.save_checkpoint({"chat_history": ["Traveler: Earlier.\nSystem: Before the checkpoint."]})
        self.assertEqual(self.engine.chronos.resume_checkpoint()[1],
                         ["Traveler: Earlier.\nSystem: Before the checkpoint."])
