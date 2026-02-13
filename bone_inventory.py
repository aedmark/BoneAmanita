""" bone_inventory.py
 'Organization is the first step toward civilization.' - Schur """

import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
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
    REFUSAL_MARKERS = [
        "cannot", "can't", "unable", "fail", "too heavy",
        "stuck", "don't", "do not", "locked", "refuse"
    ]

    def __init__(self, events=None):
        self.events = events
        self.inventory: List[str] = []  # Stores item names
        self.registry: Dict[str, Item] = {} # Active Item Objects

        # Legacy/Raw Data Compatibility (Expected by bone_diag)
        self.ITEM_REGISTRY: Dict[str, Dict] = {}

        self.recipes: List[Dict] = []
        self.max_slots = 10
        self.last_flinch_turn = 0 # Legacy State
        self.load_config()

    def load_config(self):
        """ Loads gordon.json into memory via TheLore. """
        data = TheLore.get("GORDON") or {}
        if not data and hasattr(TheLore, "get_raw"):
             data = TheLore.get_raw("gordon.json") or {}

        # 1. Load Raw Registry (Legacy/Config Source)
        self.ITEM_REGISTRY = data.get("ITEM_REGISTRY", {})

        # 2. Hydrate into Item Objects
        for name, props in self.ITEM_REGISTRY.items():
            self.registry[name] = Item.from_dict(name, props)

        self.recipes = data.get("RECIPES", [])

        # Load Starter
        starters = data.get("STARTING_INVENTORY", [])
        if not self.inventory and starters:
            self.inventory = [s for s in starters if isinstance(s, str)]

        if hasattr(BoneConfig, "INVENTORY"):
            self.max_slots = getattr(BoneConfig.INVENTORY, "MAX_SLOTS", 10)

    def get_item_data(self, item_name: str) -> Optional[Item]:
        """
        Retrieves Item object. Checks active registry first,
        then falls back to raw ITEM_REGISTRY (lazy hydration).
        """
        # 1. Check active registry
        if item_name in self.registry:
            return self.registry[item_name]

        # 2. Check legacy raw dict (e.g. added by bone_diag)
        if item_name in self.ITEM_REGISTRY:
            raw_data = self.ITEM_REGISTRY[item_name]
            item_obj = Item.from_dict(item_name, raw_data)
            self.registry[item_name] = item_obj # Cache it
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
        # Ensure it exists in registry
        if not self.get_item_data(tool_name):
            # Auto-register unknown item
            new_item = Item(name=tool_name, description="???", function="MISC")
            self.registry[tool_name] = new_item
            self.ITEM_REGISTRY[tool_name] = new_item.__dict__ # Sync raw

        if len(self.inventory) >= self.max_slots:
            dropped = self.inventory.pop(0)
            if self.events:
                self.events.log(f"Inventory full. Dropped {dropped}.", "INV")

        self.inventory.append(tool_name)

        if self.events:
            self.events.publish("ITEM_ACQUIRED", {"item": tool_name})

        return f"{Prisma.GRN}📦 ACQUIRED: {tool_name}{Prisma.RST}"

    def safe_remove_item(self, item_name: str) -> bool:
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
        # Iterate over registry keys to find valid spawns
        # (We use ITEM_REGISTRY keys to ensure we cover everything loaded)
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
        # Expanded triggers to catch "I take the X" and "grab the X"
        triggers = ["found a", "picked up", "acquired", "took the", "take the", "grab the", "takes the"]
        text = (user_text + " " + sys_text).lower()

        # Check all known items
        all_known_items = set(self.registry.keys()) | set(self.ITEM_REGISTRY.keys())

        for name in all_known_items:
            # Simple check: Name must be in text, AND user must not already have it
            if name.lower() in text and name not in self.inventory:
                # Context check: Did they actually take it?
                for t in triggers:
                    if t in text:
                        return name
        return None

    def check_flinch(self, user_text: str, turn_count: int) -> bool:
        """
        Detects if the user is refusing the call/narrative.
        Used by bone_cycle to trigger Drift/Drag penalties.
        """
        for marker in self.REFUSAL_MARKERS:
            if marker in user_text.lower():
                self.last_flinch_turn = turn_count
                return True
        return False

    def deploy_pizza(self, physics_ref: Dict, item_name="STABILITY_PIZZA") -> Tuple[bool, str]:
        if item_name not in self.inventory:
            return False, "No pizza found."
        self.inventory.remove(item_name)
        return True, "🍕 PIZZA TIME: Entropy paused. Satisfaction nominal."

    def emergency_reflex(self, physics_ref: Dict) -> Tuple[bool, Optional[str]]:
        voltage = physics_ref.get("voltage", 0.0)
        drag = physics_ref.get("narrative_drag", 0.0)

        for name in self.inventory:
            item = self.get_item_data(name) # Ensure object
            if not item: continue

            trigger = item.reflex_trigger

            if trigger == "VOLTAGE_CRITICAL" and voltage > 18.0:
                self.safe_remove_item(name)
                return True, f"{Prisma.CYN}🛡️ REFLEX: {name} sacrificed to absorb voltage spike!{Prisma.RST}"

            if trigger == "DRIFT_CRITICAL" and drag > 8.0:
                self.safe_remove_item(name)
                return True, f"{Prisma.OCHRE}⚓ REFLEX: {name} deployed to arrest drift!{Prisma.RST}"

        return False, None