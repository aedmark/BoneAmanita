"""tests/test_adventure.py"""

import json
from unittest.mock import patch, MagicMock
from mechanics.inventory import GordonKnot, Item
from archetypes.village import TheCartographer
from tests.base import BoneTestCase

class TestAdventureMechanics(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.gordon = getattr(self.engine.village, "gordon", None)
        if not self.gordon:
            self.gordon = GordonKnot(mode="ADVENTURE")
        self.gordon.mode = "ADVENTURE"

    def test_clean_noun_parsing(self):
        cases = {"the brass key": "BRASS_KEY", "a rusty sword!": "RUSTY_SWORD",
                 "some mysterious water...": "MYSTERIOUS_WATER", "my old backpack": "OLD_BACKPACK",
                 "the wooden chest please": "WOODEN_CHEST", "the heavy stone and the pebble": "HEAVY_STONE",
                 "an apple because I am hungry": "APPLE", "up the ladder": "LADDER"}
        for raw, expected in cases.items():
            self.assertEqual(self.gordon._clean_noun(raw), expected,
                f"[FAIL] The parser failed to clean '{raw}'. Expected {expected}.")

    def test_spatial_inventory_movement(self):
        self.gordon.registry["BAG"] = Item(name="bag", description="A bag", function="MISC", is_container=True)
        self.gordon.registry["COIN"] = Item(name="coin", description="A coin", function="MISC")
        self.gordon.acquire("BAG")
        self.gordon.acquire("COIN")
        self.assertEqual(self.gordon.get_item_data("COIN").location, "inventory")
        self.assertEqual(self.gordon.get_item_data("BAG").location, "inventory")
        success, msg = self.gordon.pack_item("COIN", "BAG")
        self.assertTrue(success, "[FAIL] Failed to pack coin into bag.")
        self.assertNotIn("COIN", self.gordon.inventory)
        self.assertIn("COIN", self.gordon.get_item_data("BAG").contents)
        self.assertEqual(self.gordon.get_item_data("COIN").location, "BAG")
        success, msg = self.gordon.unpack_item("COIN", "BAG")
        self.assertTrue(success, "[FAIL] Failed to unpack coin from bag.")
        self.assertIn("COIN", self.gordon.inventory)
        self.assertNotIn("COIN", self.gordon.get_item_data("BAG").contents)
        self.assertEqual(self.gordon.get_item_data("COIN").location, "inventory")
        self.gordon.safe_remove_item("COIN", new_location="VOID")
        self.assertEqual(self.gordon.get_item_data("COIN").location, "VOID")

    def test_fractal_compiler_output(self):
        carto = TheCartographer(shimmer_ref=None)
        self.gordon.registry["LAMP"] = Item(name="lamp", description="A brass lamp", function="LIGHT")
        self.gordon.acquire("LAMP")
        fractal_str = self.gordon.export_fractal_state(cartographer_ref=carto)
        fractal_data = json.loads(fractal_str)
        self.assertEqual(fractal_data["startingRoomId"], "GENESIS_POINT", "[FAIL] Missing genesis point.")
        self.assertIn("GENESIS_POINT", fractal_data["rooms"], "[FAIL] Map nodes not compiled into rooms.")
        self.assertIn("lamp", fractal_data["items"], "[FAIL] Registry items not compiled correctly.")
        self.assertEqual(fractal_data["items"]["lamp"]["location"], "inventory", "[FAIL] Item location not preserved in JSON.")

    @patch("builtins.open", new_callable=MagicMock)
    def test_hypervisor_save_triggers_fractal_export(self, mock_open):
        self.engine.chronos.save_checkpoint = MagicMock(return_value="mock_path")
        self.engine.save_checkpoint()
        mock_open.assert_any_call("fractal_adventure.json", "w", encoding="utf-8")