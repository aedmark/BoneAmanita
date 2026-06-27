"""tests/test_commands.py"""

from unittest.mock import MagicMock

from constants import Prisma
from main import BoneAmanita
from mechanics.commands import CommandProcessor, CommandStateInterface, ResourceTax
from tests.base import BoneTestCase


class CommandSystemTests(BoneTestCase):
    def test_fuller_resource_clamping_integrity(self):
        engine = BoneAmanita({})
        processor = CommandProcessor(engine, Prisma)
        processor.interface.modify_resource("stamina", -500.0)
        self.assertEqual(
            processor.interface.get_resource("stamina"),
            0.0,
            "Stamina failed to clamp at absolute zero.",
        )
        max_stamina = engine.config.MAX_STAMINA
        processor.interface.modify_resource("stamina", 5000.0)
        self.assertEqual(
            processor.interface.get_resource("stamina"),
            max_stamina,
            "Stamina breached the architectural ceiling.",
        )

    def test_gordon_reality_stack_lockout(self):
        from constants import RealityLayer

        engine = BoneAmanita({})
        processor = CommandProcessor(engine, Prisma)

        class MockRealityStack:
            current_depth = RealityLayer.TERMINAL

        engine.reality_stack = MockRealityStack()
        engine.health = 100.0
        engine.boot_mode = "ADVENTURE"
        processor.execute("/trauma")
        self.assertEqual(
            engine.health,
            100.0,
            "Gordon failed to hold the wall. Command bypassed Reality Stack lock.",
        )

    def test_pinker_syntactic_resilience(self):
        engine = BoneAmanita({})
        processor = CommandProcessor(engine, Prisma)
        processor.interface.log = MagicMock()
        processor.execute("/fakecmd")
        processor.execute("/mode")
        processor.execute("/truth")
        processor.execute("/use    ITEM    NAME  ")

        self.assertTrue(
            processor.interface.log.called,
            "The command processor swallowed the broken input without executing the safety logs.",
        )
        self.assertEqual(
            processor.interface.log.call_count,
            4,
            "Not all syntactic edge cases were caught and logged by the engine.",
        )

    def test_jester_shuffle_resets_drag(self):
        engine = BoneAmanita({})
        processor = CommandProcessor(engine, Prisma)

        processor.interface.modify_resource("atp", 100.0)

        class MockPhys:
            narrative_drag = 8.5

        engine.phys = MockPhys()

        initial_atp = processor.interface.get_resource("atp")
        processor.execute("/shuffle")

        self.assertEqual(
            engine.phys.narrative_drag,
            0.0,
            "Jester failed to clear the narrative gravity well.",
        )
        self.assertTrue(
            processor.interface.get_resource("atp") < initial_atp,
            "The Shuffle occurred without levying the ATP tax.",
        )

    def test_jester_hallucination_phase_shift(self):
        engine = BoneAmanita({})
        processor = CommandProcessor(engine, Prisma)
        processor.interface.modify_resource("atp", 100.0)
        initial_atp = processor.interface.get_resource("atp")

        class MockPhys:
            mu = 0.1
            kappa = 0.2

        class MockCortex:
            dialogue_buffer = []

        engine.phys = MockPhys()
        engine.cortex = MockCortex()
        processor.execute("/hallucinate")
        self.assertTrue(
            processor.interface.get_resource("atp") < initial_atp,
            "The Hallucination did not levy the ATP tax.",
        )

        self.assertAlmostEqual(
            engine.phys.mu, 0.9, places=2, msg="Tension (μ) did not spike correctly."
        )
        self.assertTrue(
            engine.phys.kappa >= 0.5,
            "Creative drive (κ) was not elevated to the threshold.",
        )

        self.assertTrue(
            len(engine.cortex.dialogue_buffer) > 0,
            "Dialogue buffer is empty. The mandate failed to inject.",
        )
        self.assertIn(
            "THERMAL LOCK OVERRIDE",
            engine.cortex.dialogue_buffer[-1],
            "The Jester's mandate was not injected into the active cortex buffer.",
        )
