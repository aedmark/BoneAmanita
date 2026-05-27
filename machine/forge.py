"""machine/forge.py"""

import random
from typing import Tuple, Optional, List, Any
from core import LoreManifest
from struts import ux, safe_get
from mechanics.lexicon import LexiconService

class TheForge:
    def __init__(self, lex_ref=None):
        self.lex = lex_ref
        gordon_data = LoreManifest.get_instance().get("GORDON") or {}
        self.recipe_map = {}
        for r in gordon_data.get("RECIPES", []):
            if ing := r.get("ingredient"):
                self.recipe_map.setdefault(ing, []).append(r)

    @staticmethod
    def hammer_alloy(physics: Any) -> Tuple[bool, Optional[str], Optional[str]]:
        counts = safe_get(physics, "counts", {})
        clean_words = safe_get(physics, "clean_words", [])
        if not clean_words:
            return False, None, None
        heavy = counts.get("heavy", 0)
        kinetic = counts.get("kinetic", 0)
        avg_density = ((heavy * 2.0) + (kinetic * 0.5)) / len(clean_words)
        voltage = float(safe_get(physics, "voltage", 0.0))
        if random.random() >= (voltage / 20.0) * avg_density:
            return False, None, None
        if heavy > 3:
            msg = ux("machine_strings", "forge_lead_boots")
            return True, msg.format(avg_density=avg_density), "LEAD_BOOTS"
        if kinetic > 3:
            return True, ux("machine_strings", "forge_safety_scissors"), "SAFETY_SCISSORS"
        return True, ux("machine_strings", "forge_anchor_stone"), "ANCHOR_STONE"

    def attempt_crafting(self, physics: Any, inventory_list: List[str]) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        if not inventory_list or not (clean_words := safe_get(physics, "clean_words", [])):
            return False, None, None, None
        clean_set = set(clean_words)
        voltage = float(safe_get(physics, "voltage", 0.0))
        lex_srv = self.lex or LexiconService()
        cat_cache = {}
        for item in inventory_list:
            for recipe in self.recipe_map.get(item, []):
                cat = recipe["catalyst_category"]
                if cat not in cat_cache:
                    cat_cache[cat] = set(lex_srv.get(cat) or [])
                overlap = clean_set & cat_cache[cat]
                if not overlap:
                    continue
                entanglement = self._calculate_entanglement(len(overlap), voltage)
                if random.random() < entanglement:
                    msg = ux("machine_strings", "forge_alchemy_success") or "Alchemy successful! {item} -> {result}"
                    return True, msg.format(result=recipe["result"], item=item), item, recipe["result"]
        return False, None, None, None

    @staticmethod
    def _calculate_entanglement(hit_count: int, voltage: float) -> float:
        return min(1.0, 0.2 + (hit_count * 0.1) + (voltage / 133.0))

    @staticmethod
    def transmute(physics: Any) -> Optional[str]:
        counts = safe_get(physics, "counts", {})
        voltage = float(safe_get(physics, "voltage", 0.0))
        gamma = float(safe_get(physics, "gamma", 0.0))
        if gamma < 0.15 and counts.get("abstract", 0) > 1:
            return ux("machine_strings", "forge_emulsion_fail")
        if voltage > 15.0:
            msg = ux("machine_strings", "forge_overheat")
            return msg.format(voltage=voltage)
        return None
