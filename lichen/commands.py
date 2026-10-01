from typing import Callable, Dict, List, Optional
from .inventory import GordonKnot
from .cartographer import Cartographer

class CommandProcessor:
    """
    Parses and executes spatial/UI slash commands in Adventure Mode.
    """
    def __init__(self, inventory: GordonKnot, cartographer: Cartographer):
        self.inventory = inventory
        self.cartographer = cartographer
        self.registry: Dict[str, Callable] = {
            "inventory": self._cmd_inventory,
            "look": self._cmd_look,
            "go": self._cmd_go
        }

    def execute(self, text: str) -> Optional[str]:
        if not text.startswith('/'):
            return None
            
        parts = text[1:].strip().split()
        if not parts:
            return None
            
        cmd = parts[0].lower()
        if cmd in self.registry:
            return self.registry[cmd](parts)
        
        # Check directional aliases
        directions = {"n": "NORTH", "north": "NORTH", "s": "SOUTH", "south": "SOUTH", 
                      "e": "EAST", "east": "EAST", "w": "WEST", "west": "WEST"}
        if cmd in directions:
            return self._cmd_go(["go", directions[cmd]])
            
        return f"[System] Unknown command: {cmd}"

    def _cmd_inventory(self, parts: List[str]) -> str:
        return self.inventory.render_block()

    def _cmd_look(self, parts: List[str]) -> str:
        room_slug = self.cartographer.current_room
        if not room_slug:
            return "[System] You are nowhere. The map is empty."
            
        room = self.cartographer.get_room(room_slug)
        if not room:
            return "[System] Error reading current room."
            
        out = f"**{room.name}**\n{room.description}\n"
        if room.points_of_interest:
            out += "Points of Interest:\n" + "\n".join(f"- {p}" for p in room.points_of_interest) + "\n"
        if room.exits:
            out += "Exits:\n" + "\n".join(f"- {k} to {v}" for k, v in room.exits.items())
        return out

    def _cmd_go(self, parts: List[str]) -> str:
        if len(parts) < 2:
            return "[System] Go where? (e.g. /go north)"
            
        direction = parts[1].upper()
        current_slug = self.cartographer.current_room
        if not current_slug:
            return "[System] You are nowhere."
            
        room = self.cartographer.get_room(current_slug)
        if direction not in room.exits:
            return f"[System] There is no exit to the {direction}."
            
        target_slug = room.exits[direction]
        # In a real loop, this would trigger the LLM to generate the new room.
        # For the command processor, we just update the pointer.
        self.cartographer.current_room = target_slug
        return f"[System] Moving {direction}..."
