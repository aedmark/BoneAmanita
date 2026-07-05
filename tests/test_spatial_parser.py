import unittest
from mechanics.projector import parse_spatial_reality, anchor_to_bedrock

class MockEngine:
    def __init__(self):
        self.world_atlas = None

class TestSpatialParser(unittest.TestCase):

    def test_ideal_extraction(self):
        """Tests the parser against a perfectly formatted LLM output."""
        raw_text = """
        System: You step forward into the dark.
        Room Name: **The Obsidian Vault**
        Points of Interest: A glowing pedestal, scattered ash, and a broken terminal
        Exits: North door, South corridor
        """
        result = parse_spatial_reality(raw_text)
        self.assertEqual(result["room_name"], "The Obsidian Vault")
        self.assertIn("A glowing pedestal", result["pois"])
        self.assertIn("scattered ash", result["pois"])
        self.assertIn("North door", result["exits"])
        self.assertIn("South corridor", result["exits"])

    def test_messy_extraction(self):
        """Tests the parser against varied keyword usage and missing markdown."""
        raw_text = """
        Location: Derelict Bridge
        Notice: Control console, smashed window
        Paths: Airlock, Service Hatch
        """
        result = parse_spatial_reality(raw_text)
        self.assertEqual(result["room_name"], "Derelict Bridge")
        self.assertEqual(result["pois"], ["Control console", "smashed window"])
        self.assertEqual(result["exits"], ["Airlock", "Service Hatch"])

    def test_empty_or_hallucinated_text(self):
        """Tests the parser's fallback mechanisms when the LLM hallucinates without formatting."""
        raw_text = "You just look around and see nothing but the deep void. You can't go anywhere."
        result = parse_spatial_reality(raw_text)
        self.assertEqual(result["room_name"], "Uncharted Zone")
        self.assertEqual(result["pois"], [])
        self.assertEqual(result["exits"], [])

    def test_anchor_to_bedrock(self):
        """Tests that the parsed node is successfully attached to the engine's memory structure."""
        engine = MockEngine()
        raw_text = """
        Room Name: Server Room A
        POIs: Server Rack 1, Server Rack 2
        Exits: Hallway
        """

        anchor_to_bedrock(engine, raw_text)
        self.assertIsNotNone(engine.world_atlas)
        self.assertEqual(len(engine.world_atlas["nodes"]), 1)
        self.assertEqual(engine.world_atlas["nodes"][0]["room_name"], "Server Room A")

        raw_text_2 = "Room Name: Server Room B\nPOIs: Cables\nExits: Hallway"
        anchor_to_bedrock(engine, raw_text_2)
        self.assertEqual(len(engine.world_atlas["nodes"]), 2)
        self.assertEqual(engine.world_atlas["nodes"][1]["room_name"], "Server Room B")

if __name__ == '__main__':
    unittest.main()