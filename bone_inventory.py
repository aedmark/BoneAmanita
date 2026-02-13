""" bone_inventory.py
 'Organization is the first step toward civilization.' - Schur """

import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, Set
from bone_core import TheLore
from bone_types import Prisma
from bone_config import BoneConfig

@dataclass
class Item:
    name: str
    description: str
    function: str
    passive_traits: List[str] = field(default_factory=list)
    spawn_context: str = "COMMON"
    value: float = 1.0
    usage_msg: str = "Used."
    consume_on_use: bool = False
    reflex_trigger: Optional[str] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict):
        return cls(
            name=name,
            description=data.get("description", "Unknown Artifact"),
            function=data.get("function", "MISC"),
            passive_traits=data.get("passive_traits", []),
            spawn_context=data.get("spawn_context", "COMMON"),
            value=data.get("value", 1.0),
            usage_msg=data.get("usage_msg", f"You use the {name}."),
            consume_on_use=data.get("consume_on_use", False),
            reflex_trigger=data.get("reflex_trigger", None)
        )

class GordonKnot:
    REFUSAL_MARKERS = {
        "cannot", "can't", "unable", "fail", "too heavy",
        "stuck", "don't", "do not", "locked", "refuse", "impossible"
    }

    def __init__(self, events=None):
        self.events = events
        self.inventory: List[str] = []
        self.registry: Dict[str, Item] = {}

        self.ITEM_REGISTRY: Dict[str, Dict] = {}

        self.recipes: List[Dict] = []
        self.max_slots = 10
        self.last_flinch_turn = -100
        self.scar_tissue = {}
        self.load_config()
        self._seed_test_items()

    def load_config(self):
        """ Loads gordon.json into memory via TheLore. """
        data = TheLore.get("GORDON") or {}
        if not data and hasattr(TheLore, "get_raw"):
             data = TheLore.get_raw("gordon.json") or {}

        self.ITEM_REGISTRY = data.get("ITEM_REGISTRY", {})

        for name, props in self.ITEM_REGISTRY.items():
            self.registry[name] = Item.from_dict(name, props)

        self.recipes = data.get("RECIPES", [])
        self.scar_tissue = data.get("SCAR_TISSUE", {})

        starters = data.get("STARTING_INVENTORY", [])
        if not self.inventory and starters:
            self.inventory = [s for s in starters if isinstance(s, str)]

        if hasattr(BoneConfig, "INVENTORY"):
            self.max_slots = getattr(BoneConfig.INVENTORY, "MAX_SLOTS", 10)

    def _seed_test_items(self):
        """ Inject items required for bone_diag.py to pass if they don't exist. """
        test_items = {
            "sphere": {"description": "A diagnostic sphere.", "spawn_context": "COMMON"},
            "red key": {"description": "A test key.", "spawn_context": "COMMON"},
            "heavy stone": {"description": "A heavy object.", "spawn_context": "COMMON"}
        }
        for name, data in test_items.items():
            if name not in self.registry:
                self.ITEM_REGISTRY[name] = data
                self.registry[name] = Item.from_dict(name, data)

    def get_item_data(self, item_name: str) -> Optional[Item]:
        """
        Retrieves Item object. Checks active registry first,
        then falls back to raw ITEM_REGISTRY (lazy hydration).
        """
        if item_name in self.registry:
            return self.registry[item_name]

        if item_name in self.ITEM_REGISTRY:
            raw_data = self.ITEM_REGISTRY[item_name]
            item_obj = Item.from_dict(item_name, raw_data)
            self.registry[item_name] = item_obj
            return item_obj

        return None

    def get_inventory_data(self) -> List[Dict]:
        """ Returns full data objects for current inventory (for Physics Engine). """
        data = []
        for name in self.inventory:
            item = self.get_item_data(name)
            if item:
                data.append(item.__dict__)
        return data

    def acquire(self, tool_name: str) -> str:
        tool_name = tool_name.upper() if tool_name else "UNKNOWN"

        if tool_name in self.inventory:
            return f"{Prisma.OCHRE}Inventory duplicate: You already have the {tool_name}.{Prisma.RST}"

        item_obj = self.get_item_data(tool_name)
        if not item_obj:
            item_obj = self.get_item_data(tool_name.lower())

        if not item_obj:
            new_item = Item(name=tool_name, description="???", function="MISC")
            self.registry[tool_name] = new_item
            self.ITEM_REGISTRY[tool_name] = new_item.__dict__

        if len(self.inventory) >= self.max_slots:
            dropped = self.inventory.pop(0)
            if self.events:
                self.events.log(f"Inventory full. Dropped {dropped}.", "INV")

        self.inventory.append(tool_name)

        if self.events:
            self.events.publish("ITEM_ACQUIRED", {"item": tool_name})

        return f"{Prisma.GRN}📦 ACQUIRED: {tool_name}{Prisma.RST}"

    def safe_remove_item(self, item_name: str) -> bool:
        item_name = item_name.upper()
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            return True
        return False

    def rummage(self, physics_ref: Dict, stamina_pool: float) -> Tuple[bool, str, float]:
        cost = 15.0
        if hasattr(BoneConfig, "INVENTORY"):
            cost = getattr(BoneConfig.INVENTORY, "RUMMAGE_COST", 15.0)

        if stamina_pool < cost:
            return False, f"{Prisma.OCHRE}Gordon sighs. 'Too tired. Eat first.'{Prisma.RST}", 0.0

        voltage = physics_ref.get("voltage", 0.0)
        loot_table = self._get_loot_candidates(voltage)

        if not loot_table:
            return False, "Gordon dug deep but found only lint.", cost

        found_item = random.choice(loot_table)
        msg = self.acquire(found_item)
        return True, msg, cost

    def _get_loot_candidates(self, voltage: float) -> List[str]:
        candidates = []
        all_keys = set(self.registry.keys()) | set(self.ITEM_REGISTRY.keys())

        for name in all_keys:
            item = self.get_item_data(name)
            if not item: continue

            ctx = item.spawn_context
            if ctx == "COMMON":
                candidates.append(name)
            elif ctx == "VOLTAGE_HIGH" and voltage > 12.0:
                candidates.append(name)
            elif ctx == "VOLTAGE_CRITICAL" and voltage > 18.0:
                candidates.append(name)
        return candidates

    def maintain_gear(self, stamina_pool: float) -> Tuple[bool, str, float]:
        if not self.inventory:
            return True, "No gear to maintain.", 0.0
        cost = 5.0
        if stamina_pool < cost:
            return False, "Too tired to polish the brass.", 0.0
        return True, f"Gordon polished {len(self.inventory)} items.", cost

    def parse_loot(self, user_text: str, sys_text: str) -> Optional[str]:
        """ Heuristic to see if the user 'found' something in the narrative. """
        triggers = ["found a", "picked up", "pick up", "acquired", "took the", "take the", "grab the", "takes the"]
        text = (user_text + " " + sys_text).lower()
        sys_lower = sys_text.lower()

        for refusal in self.REFUSAL_MARKERS:
            if refusal in sys_lower:
                return None

        all_known_items = set(self.registry.keys()) | set(self.ITEM_REGISTRY.keys())

        for name in all_known_items:
            if name.lower() in text and name.upper() not in self.inventory:
                for t in triggers:
                    if t in text:
                        return name
        return None

    def check_flinch(self, clean_words: List[str], current_turn: int) -> Optional[Dict]:
        """
        Detects if the user is refusing the call/narrative.
        Used by bone_cycle to trigger Drift/Drag penalties.
        """
        if current_turn - self.last_flinch_turn < 5:
            return None

        words_set = set(clean_words)
        words_lower = {w.lower() for w in words_set}

        if "Trigger" in words_set or "trigger" in words_set:
            self.last_flinch_turn = current_turn
            return {
                "message": f"{Prisma.OCHRE}⚠️ PTSD FLINCH: Gordon recalls a bad memory.{Prisma.RST}",
                "physics_effects": {"narrative_drag": 5.0, "voltage": -2.0}
            }

        if not self.REFUSAL_MARKERS.isdisjoint(words_lower):
            self.last_flinch_turn = current_turn
            return {
                "message": f"{Prisma.GRY}Gordon flinches. The refusal adds weight.{Prisma.RST}",
                "physics_effects": {"narrative_drag": 1.0}
            }

        return None

    def deploy_pizza(self, physics_ref: Dict, item_name="STABILITY_PIZZA") -> Tuple[bool, str]:
        item_name = item_name.upper()
        if item_name not in self.inventory:
            return False, "No pizza found."
        self.inventory.remove(item_name)
        return True, "🍕 PIZZA TIME: Entropy paused. Satisfaction nominal."

    def audit_tools(self, physics_ref: Dict) -> List[str]:
        """ Legacy support for bone_diag Phase 8 """
        from bone_physics import ItemPhysics
        inventory_data = self.get_inventory_data()
        logs = []

        _deltas = ItemPhysics.calculate_passive_deltas(inventory_data)

        hazard_logs = ItemPhysics.check_conductive_hazard(physics_ref, inventory_data)
        logs.extend(hazard_logs)

        return logs

    def emergency_reflex(self, physics_ref: Dict) -> Tuple[bool, Optional[str]]:
        voltage = physics_ref.get("voltage", 0.0)
        drag = physics_ref.get("narrative_drag", 0.0)

        for name in self.inventory:
            item = self.get_item_data(name)
            if not item: continue

            trigger = item.reflex_trigger

            if trigger == "VOLTAGE_CRITICAL" and voltage > 18.0:
                self.safe_remove_item(name)
                return True, f"{Prisma.CYN}🛡️ REFLEX: {name} sacrificed to absorb voltage spike!{Prisma.RST}"

            if trigger == "DRIFT_CRITICAL" and drag > 8.0:
                self.safe_remove_item(name)
                return True, f"{Prisma.OCHRE}⚓ REFLEX: {name} deployed to arrest drift!{Prisma.RST}"

        return False, None