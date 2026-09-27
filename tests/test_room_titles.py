"""Gordon's law: an ADVENTURE room title names the place, never the zone. Zones and orbits (VOID_DRIFT,
PROTO_COSMOS) are for TECHNICAL and the DEEP HUD. The prompt's CURRENT LOCATION was the orbit, and the
model titled 6 of 9 rooms with it."""

from unittest.mock import MagicMock

from mechanics.projector import drop_title, is_system_label
from tests.base import BoneTestCase

ROOM = "**{title}**\nDust hangs over a stopped wheel.\n\n**Points of Interest:**\n- A sack of grain\n\n**Exits:**\n- North (via Door) to The Yard"


class SystemLabels(BoneTestCase):
    def test_zone_and_orbit_labels_are_caught_and_place_names_are_not(self):
        for label in ("VOID_DRIFT", "PROTO_COSMOS", "ORBITAL", "LAGRANGE_POINT", "THE_FORGE", "COURTYARD", "THE_FRACTURE"):
            self.assertTrue(is_system_label(label), label)
        for place in ("The Mill Loft", "Courtyard", "The Great Hall", "Orbital Station Nine", "MILL", ""):
            self.assertFalse(is_system_label(place), place)

    def test_drop_title_keeps_the_rest(self):
        text = drop_title(ROOM.format(title="VOID_DRIFT"))
        self.assertNotIn("VOID_DRIFT", text)
        self.assertIn("Dust hangs over a stopped wheel.", text)
        self.assertIn("**Exits:**", text)


class RoomTitlesInPlay(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.assertEqual(self.engine.cortex.active_mode, "ADVENTURE")

    def turn(self, reply, message="I look around."):
        self.engine.cortex.llm.generate = MagicMock(return_value=reply)
        return self.engine.process_turn(message)

    def prompt(self):
        return self.engine.cortex.llm.generate.call_args[0][0]

    def test_a_zone_title_never_reaches_the_screen_or_the_map(self):
        result = self.turn(ROOM.format(title="VOID_DRIFT"))
        # Below the divider is the story; the log panel above it may name the zone, as debugging should.
        story = result.get("ui", "").split("────────")[-1]
        self.assertNotIn("VOID_DRIFT", story)
        self.assertIn("Dust hangs over a stopped wheel.", story)
        self.assertNotIn("void_drift", self.engine.cortex.visited_rooms)
        self.assertEqual(self.engine.cortex.current_room_name, "")

    def test_the_prompt_gives_the_room_not_the_zone(self):
        self.turn(ROOM.format(title="VOID_DRIFT"))
        self.assertIn("CURRENT LOCATION: Not named yet. Give this place a name of its own.", self.prompt())
        self.turn(ROOM.format(title="The Mill Loft"))
        self.turn(ROOM.format(title="The Mill Loft"), "I check the sack.")
        self.assertIn("CURRENT LOCATION: The Mill Loft", self.prompt())
        self.assertIn("8. ROOM TITLES: The title names the place itself", self.prompt())
        self.assertIn("**[Name of this place]**", self.prompt())
