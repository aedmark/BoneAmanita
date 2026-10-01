from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Item:
    name: str
    description: str
    traits: List[str] = None

    def __post_init__(self):
        if self.traits is None:
            self.traits = []

class GordonKnot:
    """
    Inventory Management System for Adventure Mode.
    Handles pockets, carrying capacity, and item ownership.
    """
    def __init__(self, max_slots: int = 10, starters: Optional[List[str]] = None):
        self.inventory: List[Item] = []
        self.max_slots = max_slots
        
        if starters:
            for s in starters:
                self.acquire(Item(name=s, description="A starting item."))

    def has(self, item_name: str) -> bool:
        return any(i.name.lower() == item_name.lower() for i in self.inventory)

    def get_item(self, item_name: str) -> Optional[Item]:
        for i in self.inventory:
            if i.name.lower() == item_name.lower():
                return i
        return None

    def acquire(self, item: Item) -> bool:
        if len(self.inventory) >= self.max_slots:
            return False
        if not self.has(item.name):
            self.inventory.append(item)
            return True
        return False

    def drop(self, item_name: str) -> bool:
        item = self.get_item(item_name)
        if item:
            self.inventory.remove(item)
            return True
        return False

    def list_items(self) -> List[str]:
        return [i.name for i in self.inventory]

    def render_block(self) -> str:
        """Renders the inventory block for the PromptComposer."""
        if not self.inventory:
            return "Inventory: [Empty Pocket]"
        
        names = [i.name for i in self.inventory]
        return f"Inventory ({len(names)}/{self.max_slots}): " + ", ".join(names)
