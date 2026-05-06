"""
tests/test_inventory.py
The Physical Constraint Torture Chamber.
Validates the GordonKnot's ability to maintain the physical reality of the simulation,
enforce inventory coupling, and execute emergency metabolic reflexes.
"""

from tests.base import BoneTestCase
from main import BoneAmanita


class InventorySystemTests(BoneTestCase):
    def test_pinker_substring_contamination(self):
        """
        Ensures the explicit extraction parser uses strict word boundary tokens
        and does not mistake sub-strings ('forget') for acquisition verbs ('get').
        """
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
        """
        Evaluates the Object-Action Coupling. The system must hard-block actions
        if the required topological item is missing from the inventory.
        """
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
        """
        Validates that passive inventory items can intercept terminal physical
        states (like critical voltage) and consume themselves to save the host.
        """
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
        """
        Ensures the system does not double-walk arrays and catches its own
        ValueErrors gracefully when attempting to remove phantom items.
        """
        engine = BoneAmanita({})
        gordon = getattr(engine.village, "gordon", None)
        gordon.inventory = ["REAL_ITEM"]
        try:
            result = gordon.safe_remove_item("GHOST_ITEM")
            self.assertFalse(result)
        except ValueError as e:
            self.fail(f"safe_remove_item crashed and threw a ValueError instead of catching it: {e}")
