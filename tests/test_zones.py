"""tests/test_zones.py

Zones, end to end.

Hypervisor v7: "Distinct projects and people live in separate Zones; when the
conversation crosses from one to another, the old Zone goes out of scope."

Three pieces had to be connected. `wing_id` was read from a `scope_boundary`
key defined nowhere in the project, so every memory ever written was tagged
GLOBAL. The filter in CerebralIndex.query_neighborhood was correct and had
nothing to filter on, because nothing set `physics_state["wing_id"]` either.
And MemoryCore.execute_doorway_flush had no production caller, so crossing a
zone boundary never flushed anything.
"""

import unittest

from brain.ann import CerebralIndex
from spores.network import MycelialNetwork
from tests.base import BoneTestCase


class WingResolution(unittest.TestCase):
    def test_reads_the_nested_stabilized_zone(self):
        self.assertEqual(
            MycelialNetwork.current_wing({"space": {"zone": "THE_FORGE"}}),
            "THE_FORGE",
        )

    def test_accepts_a_flattened_zone_and_normalises_case(self):
        self.assertEqual(MycelialNetwork.current_wing({"zone": "aerie"}), "AERIE")

    def test_unreadable_physics_degrades_to_the_wildcard(self):
        """Unscoped is recoverable; a wrong zone label strands the memory."""
        for bad in ({}, None, {"space": {}}, {"zone": ""}):
            self.assertEqual(MycelialNetwork.current_wing(bad), "GLOBAL")


class WingFiltering(unittest.TestCase):
    """GLOBAL is a wildcard on both sides, not a zone name."""

    def setUp(self):
        self.index = CerebralIndex()
        rows = [
            ("THE_FORGE", "compiling the tokenizer again"),
            ("AERIE", "a thought about thoughts themselves"),
            ("GLOBAL", "an old memory from before zoning existed"),
        ]
        self.index.add_memories(
            [self.index.embed(t) for _, t in rows],
            [{"id": t[:20], "raw_verbatim_text": t, "wing_id": w} for w, t in rows],
        )

    def _wings(self, target):
        hits = self.index.query_neighborhood(
            self.index.embed("what was I working on"),
            k=5,
            resonance_threshold=0.0,
            physics_state={"wing_id": target},
        )
        return sorted(h["wing_id"] for h in hits)

    def test_a_zone_sees_itself_and_global(self):
        self.assertEqual(self._wings("THE_FORGE"), ["GLOBAL", "THE_FORGE"])

    def test_a_zone_does_not_see_a_sibling_zone(self):
        self.assertNotIn("AERIE", self._wings("THE_FORGE"))

    def test_global_sees_everything(self):
        self.assertEqual(self._wings("GLOBAL"), ["AERIE", "GLOBAL", "THE_FORGE"])

    def test_unscoped_memories_are_never_stranded(self):
        """Regression: naive filtering would orphan every memory written
        before zoning was switched on, since all of them are tagged GLOBAL."""
        for target in ("THE_FORGE", "AERIE", "THE_MUD", "COURTYARD"):
            self.assertIn("GLOBAL", self._wings(target))

    def test_lateral_search_ignores_zoning(self):
        hits = self.index.query_neighborhood(
            self.index.embed("anything"),
            k=5,
            resonance_threshold=0.0,
            physics_state={"wing_id": "THE_FORGE", "lateral_search": True},
        )
        self.assertEqual(len(hits), 3)


class Ingestion(BoneTestCase):
    def test_engrams_carry_the_zone_they_formed_in(self):
        mem = self.engine.mind.mem
        for zone, text in (
            ("THE_FORGE", "hammering the parser into shape"),
            ("AERIE", "the abstract shape of the whole idea"),
        ):
            mem.encode(
                text.split(),
                {"space": {"zone": zone}, "raw_text": text, "voltage": 50.0},
                "GEODESIC",
            )
        wings = {n["meta"]["wing_id"] for n in mem.hippocampus.nodes.values()}
        self.assertEqual(wings, {"THE_FORGE", "AERIE"})

    def test_cortex_gather_state_attaches_the_wing(self):
        phys = {"space": {"zone": "THE_MUD"}}
        self.engine.cortex._attach_wing(phys)
        self.assertEqual(phys["wing_id"], "THE_MUD")


class Doorway(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.core = self.engine.mind.mem.memory_core

    def test_first_entry_does_not_flush(self):
        self.core.short_term_buffer.extend([{"x": 1}, {"x": 2}])
        self.core.execute_doorway_flush("THE_FORGE")
        self.assertEqual(len(self.core.short_term_buffer), 2)

    def test_crossing_a_boundary_flushes_working_memory(self):
        self.core.execute_doorway_flush("THE_FORGE")
        self.core.short_term_buffer.extend([{"x": 1}, {"x": 2}])
        self.core.execute_doorway_flush("AERIE")
        self.assertEqual(len(self.core.short_term_buffer), 0)

    def test_staying_in_a_zone_preserves_working_memory(self):
        self.core.execute_doorway_flush("THE_FORGE")
        self.core.short_term_buffer.extend([{"x": 1}, {"x": 2}])
        self.core.execute_doorway_flush("THE_FORGE")
        self.assertEqual(len(self.core.short_term_buffer), 2)

    def test_navigation_phase_calls_the_doorway(self):
        """Regression: execute_doorway_flush had no production caller."""
        from phases.environmental import NavigationPhase

        phase = NavigationPhase(self.engine)
        self.core.execute_doorway_flush("THE_FORGE")
        self.core.short_term_buffer.extend([{"x": 1}])

        class Ctx:
            logs = []

            def log(self, msg):
                self.logs.append(msg)

        phase._cross_doorway(Ctx(), "AERIE")
        self.assertEqual(len(self.core.short_term_buffer), 0)
        self.assertEqual(self.core.current_doorway_zone, "AERIE")


if __name__ == "__main__":
    unittest.main()
