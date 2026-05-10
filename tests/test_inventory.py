"""
tests/test_inventory.py
"""

from tests.base import BoneTestCase
from main import BoneAmanita

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
            "Gordon incorrectly auto-looted due to sub-string contamination ('forget' -> 'get')."
        )

    def test_fuller_reality_wall(self):
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.action_coupling = {"unlock": ["key", "passcard"]}
        gordon.inventory = []
        refusal = gordon.enforce_object_action_coupling("I want to unlock the door.", "HALLWAY")
        self.assertIsNotNone(refusal, "Gordon allowed an action without the required physical object.")
        gordon.inventory.append("KEY")
        allow = gordon.enforce_object_action_coupling("I want to unlock the door.", "HALLWAY")
        self.assertIsNone(allow, "Gordon blocked a valid action despite the user possessing the required object.")

    def test_meadows_emergency_reflex(self):
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.register_dynamic_item("COOLANT_ROD", {
            "description": "An emergency heat sink.",
            "reflex_trigger": "VOLTAGE_CRITICAL"
        })
        gordon.inventory.append("COOLANT_ROD")
        phys = {"voltage": 25.0}
        triggered, msg = gordon.emergency_reflex(phys)
        self.assertTrue(triggered, "Reflex failed to trigger during critical voltage.")
        self.assertNotIn("COOLANT_ROD", gordon.inventory, "Item was not consumed during the emergency reflex.")
        self.assertTrue(phys["voltage"] < 25.0, "Reflex consumed the item but failed to reset the physical voltage.")

    def test_schur_graceful_removal(self):
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.inventory = ["REAL_ITEM"]
        try:
            result = gordon.safe_remove_item("GHOST_ITEM")
            self.assertFalse(result)
        except ValueError as e:
            self.fail(f"safe_remove_item crashed and threw a ValueError instead of catching it: {e}")
