"""tests/test_machine.py"""

import unittest
from unittest.mock import MagicMock

from machine.crucible import TheCrucible
from machine.forge import TheForge
from machine.panic import PanicRoom
from machine.theremin import TheTheremin
from presets import BoneConfig

try:
    from tests.base import BoneTestCase
except ImportError:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tests.base import BaseTest as BoneTestCase


class MachineContractTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig

    def test_theremin_dict_contract(self):
        theremin = TheTheremin(config_ref=self.config)
        raw_physics = {
            "counts": {"heavy": 2, "abstract": 5, "thermal": 1},
            "voltage": 12.0,
            "turbulence": 0.7,
            "repetition": 0.2,
            "truth_ratio": 0.8,
            "narrative_drag": 5.0,
        }
        is_stuck, resin, msg, crit = theremin.listen(raw_physics)
        self.assertIsInstance(is_stuck, bool)
        self.assertIsInstance(resin, float)

    def test_forge_dict_contract(self):
        forge = TheForge(lex_ref=MagicMock())
        raw_physics = {
            "counts": {"heavy": 1, "kinetic": 5},
            "clean_words": ["metal", "spark", "strike", "heat", "iron"],
            "voltage": 100.0,
        }
        success, msg, alloy = forge.hammer_alloy(raw_physics)
        self.assertTrue(success)
        self.assertEqual(alloy, "SAFETY_SCISSORS")

    def test_crucible_dict_contract(self):
        crucible = TheCrucible(config_ref=self.config)
        raw_physics = {
            "narrative_drag": 2.0,
            "voltage": 19.0,
            "kappa": 0.8,
            "system_surge_event": False,
        }
        state, metric, msg = crucible.audit_fire(raw_physics)
        self.assertEqual(state, "RITUAL")
        self.assertIn("narrative_drag", raw_physics)

    def test_panic_room_dict_preservation(self):
        previous_state = {"chem": {"SER": 0.85, "DOP": 0.5}}
        safe_bio = PanicRoom.get_safe_bio(previous_state)
        self.assertEqual(safe_bio["chem"]["SER"], 0.85)
        self.assertEqual(safe_bio["chem"]["DOP"], 0.0)


if __name__ == "__main__":
    unittest.main()
