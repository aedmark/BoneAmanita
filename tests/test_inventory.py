"""tests/test_inventory.py"""

from main import BoneAmanita
from tests.base import BoneTestCase


class InventorySystemTests(BoneTestCase):
    def test_pinker_substring_contamination(self):
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.acquisition_verbs = ["get"]
        sys_text = "You see a [[LOOT: GOLD_COIN]]."
        user_input = "I think I will forget about the gold coin."
        gordon.process_loot_tags(sys_text, user_input)
        self.assertNotIn(
            "GOLD_COIN",
            gordon.inventory,
            "Gordon incorrectly auto-looted due to sub-string contamination ('forget' -> 'get').",
        )

    def test_fuller_reality_wall(self):
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.action_coupling = {"unlock": ["key", "passcard"]}
        gordon.inventory = []
        refusal = gordon.enforce_object_action_coupling(
            "I want to unlock the door.", "HALLWAY"
        )
        self.assertIsNotNone(
            refusal, "Gordon allowed an action without the required physical object."
        )
        gordon.inventory.append("KEY")
        allow = gordon.enforce_object_action_coupling(
            "I want to unlock the door.", "HALLWAY"
        )
        self.assertIsNone(
            allow,
            "Gordon blocked a valid action despite the user possessing the required object.",
        )

    def test_meadows_emergency_reflex(self):
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.register_dynamic_item(
            "COOLANT_ROD",
            {
                "description": "An emergency heat sink.",
                "reflex_trigger": "VOLTAGE_CRITICAL",
            },
        )
        gordon.inventory.append("COOLANT_ROD")
        phys = {"voltage": 25.0}
        triggered, msg = gordon.emergency_reflex(phys)
        self.assertTrue(triggered, "Reflex failed to trigger during critical voltage.")
        self.assertNotIn(
            "COOLANT_ROD",
            gordon.inventory,
            "Item was not consumed during the emergency reflex.",
        )
        self.assertTrue(
            phys["voltage"] < 25.0,
            "Reflex consumed the item but failed to reset the physical voltage.",
        )

    def test_schur_graceful_removal(self):
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.inventory = ["REAL_ITEM"]
        try:
            result = gordon.safe_remove_item("GHOST_ITEM")
            self.assertFalse(result)
        except ValueError as e:
            self.fail(
                f"safe_remove_item crashed and threw a ValueError instead of catching it: {e}"
            )

    def test_container_pack_and_unpack(self):
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.register_dynamic_item(
            "LEATHER_POUCH",
            {
                "description": "A small pouch.",
                "is_container": True,
                "capacity": 2,
                "contents": [],
            },
        )
        gordon.register_dynamic_item("MAP", {"description": "An old map."})
        gordon.inventory = ["LEATHER_POUCH", "MAP"]
        success, msg = gordon.pack_item("MAP", "LEATHER_POUCH")
        self.assertTrue(success, f"Packing failed: {msg}")
        self.assertNotIn(
            "MAP", gordon.inventory, "MAP should be removed from main inventory."
        )
        pouch = gordon.get_item_data("LEATHER_POUCH")
        self.assertIn("MAP", pouch.contents, "MAP should be inside the pouch.")
        success, msg = gordon.unpack_item("MAP", "LEATHER_POUCH")
        self.assertTrue(success, f"Unpacking failed: {msg}")
        self.assertIn(
            "MAP", gordon.inventory, "MAP should be returned to main inventory."
        )
        self.assertNotIn("MAP", pouch.contents, "MAP should be removed from the pouch.")

    def test_container_capacity_and_nesting_limits(self):
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.register_dynamic_item(
            "BOX", {"is_container": True, "capacity": 1, "contents": []}
        )
        gordon.register_dynamic_item("ROCK", {})
        gordon.register_dynamic_item("STONE", {})
        gordon.inventory = ["BOX", "ROCK", "STONE"]
        success1, _ = gordon.pack_item("ROCK", "BOX")
        self.assertTrue(success1)
        success2, msg2 = gordon.pack_item("STONE", "BOX")
        self.assertFalse(success2, "Gordon allowed packing into a full container.")
        self.assertIn("full", msg2.lower())
        success3, msg3 = gordon.pack_item("BOX", "BOX")
        self.assertFalse(success3, "Gordon allowed packing a container into itself.")
        self.assertIn("itself", msg3.lower())
        success4, msg4 = gordon.pack_item("BOX", "STONE")
        self.assertFalse(
            success4, "Gordon allowed packing into an item that isn't a container."
        )
        self.assertIn("not a container", msg4.lower())

    def test_container_parser_regex(self):
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.register_dynamic_item(
            "MAGIC_BAG", {"is_container": True, "capacity": 5, "contents": []}
        )
        gordon.register_dynamic_item("RUSTY_SWORD", {})
        gordon.inventory = ["MAGIC_BAG", "RUSTY_SWORD"]
        logs, handled = gordon.process_container_commands(
            "I quickly put the rusty sword in my magic bag."
        )
        self.assertTrue(handled, "Regex failed to capture the 'put in' phrase.")
        self.assertNotIn(
            "RUSTY_SWORD", gordon.inventory, "Sword was not removed from belt."
        )
        bag = gordon.get_item_data("MAGIC_BAG")
        self.assertIn("RUSTY_SWORD", bag.contents, "Sword was not added to the bag.")
        logs, handled = gordon.process_container_commands(
            "take the rusty sword out of the magic bag please"
        )
        self.assertTrue(handled, "Regex failed to capture the 'take from' phrase.")
        self.assertIn(
            "RUSTY_SWORD", gordon.inventory, "Sword was not returned to belt."
        )
