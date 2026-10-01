from lichen.inventory import GordonKnot, Item
from lichen.cartographer import Cartographer
from lichen.commands import CommandProcessor

def test_inventory():
    inv = GordonKnot(max_slots=2)
    assert inv.acquire(Item("Key", "A rusty key"))
    assert inv.has("key")
    assert inv.acquire(Item("Map", "An old map"))
    assert not inv.acquire(Item("Sword", "Too heavy")) # Full
    assert inv.drop("key")
    assert not inv.has("key")
    
def test_cartographer():
    llm_out = """
**[The Dark Cave]**
It is very dark here. You hear bats.
**Points of Interest:**
- A shiny rock
**Exits:**
- North to [Sunlight Clearing]
- West via crack to [Deep Chasm]
"""
    c = Cartographer()
    room = c.parse_room(llm_out)
    assert room.name == "The Dark Cave"
    assert room.slug == "the_dark_cave"
    assert "A shiny rock" in room.points_of_interest
    assert room.exits["NORTH"] == "sunlight_clearing"
    assert room.exits["WEST"] == "deep_chasm"
    
def test_commands():
    inv = GordonKnot()
    inv.acquire(Item("Lantern", "A bright light"))
    c = Cartographer()
    c.parse_room("**[Start]**\nA place.\n**Exits:**\n- North to [End]")
    
    processor = CommandProcessor(inv, c)
    assert "Lantern" in processor.execute("/inventory")
    assert "A place." in processor.execute("/look")
    assert "Moving NORTH..." in processor.execute("/go north")
    assert c.current_room == "end"
