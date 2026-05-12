"""
tests/test_commands.py
"""

from unittest.mock import MagicMock
from tests.base import BoneTestCase
from main import BoneAmanita
from constants import Prisma
from mechanics.commands import CommandProcessor, ResourceTax, CommandStateInterface


class CommandSystemTests(BoneTestCase):
    def test_fuller_resource_clamping_integrity(self):
        engine = BoneAmanita({})
        processor = CommandProcessor(engine, Prisma)
        processor.interface.modify_resource("stamina", -500.0)
        self.assertEqual(processor.interface.get_resource("stamina"), 0.0, "Stamina failed to clamp at absolute zero.")
        max_stamina = engine.config.MAX_STAMINA
        processor.interface.modify_resource("stamina", 5000.0)
        self.assertEqual(processor.interface.get_resource("stamina"), max_stamina,
                         "Stamina breached the architectural ceiling.")

    def test_gordon_reality_stack_lockout(self):
        engine = BoneAmanita({})
        processor = CommandProcessor(engine, Prisma)

        class MockRealityStack:
            current_depth = 4

            def get_grammar_rules(self):
                return {"allow_commands": False}

        engine.reality_stack = MockRealityStack()
        engine.health = 100.0
        processor.execute("/trauma")
        self.assertEqual(engine.health, 100.0, "Gordon failed to hold the wall. Command bypassed Reality Stack lock.")

    def test_pinker_syntactic_resilience(self):
        engine = BoneAmanita({})
        processor = CommandProcessor(engine, Prisma)
        try:
            processor.execute("/hallucinate")
            processor.execute("/mode")
            processor.execute("/truth")
            processor.execute("/use    ITEM    NAME  ")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Syntactic noise shattered the command processor: {e}")

    def test_jester_shuffle_resets_drag(self):
        engine = BoneAmanita({})
        engine.set_atp(100.0)

        class MockPhys:
            narrative_drag = 8.5

        engine.phys = MockPhys()
        processor = CommandProcessor(engine, Prisma)
        initial_atp = engine.get_metrics().get("atp", 0.0)
        processor.execute("/shuffle")
        self.assertEqual(engine.phys.narrative_drag, 0.0, "Jester failed to clear the narrative gravity well.")
        final_atp = engine.get_metrics().get("atp", 0.0)
        self.assertTrue(final_atp < initial_atp, "The Shuffle occurred without levying the ATP tax.")
