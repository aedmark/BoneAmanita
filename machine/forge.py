"""machine/forge.py

The Forge is the semantic alchemy engine of the simulation.
It governs the creation and transformation of items based on the user's vocabulary.
It listens to the 'clean_words' (the raw, structural tokens of the user's prompt)
and checks if they act as catalysts to combine with existing inventory items,
or if the sheer density of the speech spontaneous forges new base materials.
"""

import random
from typing import Tuple, Optional, List, Any
from core import LoreManifest
from struts import ux, safe_get
from mechanics.lexicon import LexiconService

class TheForge:
    def __init__(self, lex_ref=None):
        """
        Initializes the Forge by loading Gordon's recipe manifest.
        Recipes are mapped by their base ingredient for O(1) lookup during the crafting loop.
        """
        self.lex = lex_ref
        gordon_data = LoreManifest.get_instance().get("GORDON") or {}

        # Build the recipe map: { "Base_Ingredient": [ {recipe_dict}, ... ] }
        self.recipe_map = {}
        for r in gordon_data.get("RECIPES", []):
            if ing := r.get("ingredient"):
                self.recipe_map.setdefault(ing, []).append(r)

    @staticmethod
    def hammer_alloy(physics: Any) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Spontaneous Generation (No inventory required).
        Evaluates the "weight" of the user's prompt. If the user uses a high density
        of 'heavy' or 'kinetic' words during a high-voltage state, the system may
        spontaneously forge a base item (like Lead Boots or Safety Scissors).
        """
        counts = safe_get(physics, "counts", {})
        clean_words = safe_get(physics, "clean_words", [])

        if not clean_words:
            return False, None, None

        heavy = counts.get("heavy", 0)
        kinetic = counts.get("kinetic", 0)

        # Calculate how dense the prompt is with structural/action words.
        # Heavy words carry 4x the weight of kinetic words in this specific alloy.
        avg_density = ((heavy * 2.0) + (kinetic * 0.5)) / len(clean_words)
        voltage = float(safe_get(physics, "voltage", 0.0))

        # The RNG Gate: High voltage and high word density increase the chance of forging.
        if random.random() >= (voltage / 20.0) * avg_density:
            return False, None, None

        # Determine the resulting item based on the dominant semantic category.
        if heavy > 3:
            msg = ux("machine_strings", "forge_lead_boots")
            return True, msg.format(avg_density=avg_density), "LEAD_BOOTS"

        if kinetic > 3:
            return True, ux("machine_strings", "forge_safety_scissors"), "SAFETY_SCISSORS"

        # Fallback base item if the alloy succeeds but lacks a specific heavy/kinetic lean.
        return True, ux("machine_strings", "forge_anchor_stone"), "ANCHOR_STONE"

    def attempt_crafting(
        self, physics: Any, inventory_list: List[str]
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Targeted Alchemy (Inventory Required).
        Checks the user's current inventory against the words they just spoke.
        If a spoken word belongs to a 'catalyst_category' required by an inventory item's
        recipe, the forge attempts a transmutation.
        """
        if not inventory_list or not (clean_words := safe_get(physics, "clean_words", [])):
            return False, None, None, None

        clean_set = set(clean_words)
        voltage = float(safe_get(physics, "voltage", 0.0))
        lex_srv = self.lex or LexiconService()

        # Pragmatic Optimization: Cache lexicon category lists locally during the loop
        # to prevent redundant, expensive lookups if multiple recipes share a catalyst category.
        cat_cache = {}

        for item in inventory_list:
            for recipe in self.recipe_map.get(item, []):
                cat = recipe["catalyst_category"]

                # Fetch and cache the valid words for this specific catalyst category.
                if cat not in cat_cache:
                    cat_cache[cat] = set(lex_srv.get(cat) or [])

                # Check if the user's prompt contains any words from the required category.
                overlap = clean_set & cat_cache[cat]
                if not overlap:
                    continue

                # We have a catalyst match. Calculate the probability of success.
                entanglement = self._calculate_entanglement(len(overlap), voltage)

                if random.random() < entanglement:
                    msg = ux("machine_strings", "forge_alchemy_success") or "Alchemy successful! {item} -> {result}"
                    return True, msg.format(result=recipe["result"], item=item), item, recipe["result"]
                else:
                    msg = ux("machine_strings", "forge_alchemy_fail") or "Alchemy failed. Entanglement: {entanglement}%"
                    return False, msg.format(entanglement=int(entanglement * 100)), None, None

        return False, None, None, None

    @staticmethod
    def _calculate_entanglement(hit_count: int, voltage: float) -> float:
        """
        Calculates the probability curve of a successful craft.
        Base chance (20%) + semantic resonance (10% per matching word) + systemic energy (voltage).
        Capped at 100% (1.0).
        """
        return min(1.0, 0.2 + (hit_count * 0.1) + (voltage / 133.0))

    @staticmethod
    def transmute(physics: Any) -> Optional[str]:
        """
        Environmental Check: Evaluates if the current state of the physics engine
        is fundamentally hostile to forging, returning a failure message if so.
        """
        counts = safe_get(physics, "counts", {})
        voltage = float(safe_get(physics, "voltage", 0.0))

        # 'gamma' represents cohesive flow. If flow is low and the user is speaking
        # in highly abstract terms, the physical elements cannot bind.
        gamma = float(safe_get(physics, "gamma", 0.0))
        if gamma < 0.15 and counts.get("abstract", 0) > 1:
            return ux("machine_strings", "forge_emulsion_fail")

        # Overheat safety: The forge physically cannot operate if the system
        # tension is approaching critical meltdown levels.
        if voltage > 15.0:
            msg = ux("machine_strings", "forge_overheat")
            return msg.format(voltage=voltage)

        return None