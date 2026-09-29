"""Memory phase 6: /memory shows what the model keeps, how often recall handed it back, what the world graph
holds and the gate's latest decisions. Systems detail, so only in TECHNICAL mode or on the DEEP HUD."""

from unittest.mock import MagicMock

from engine.gate.kernel import Gate
from engine.gate.report import memory_report
from tests.base import BoneTestCase


class TheReport(BoneTestCase):
    def test_newest_first_with_recall_counts_and_a_limit(self):
        state = {"self": {"memory": {f"note{i}": f"detail {i}" for i in range(5)}}, "world": {}}
        lines = memory_report(state, {"note4": (3, 940.0)}, [], 500, "http:nomic 768d [NOMINAL]", limit=2, now=1000.0)
        self.assertEqual(lines[0], "MEMORY: 5 kept of 500 (forgetting starts at 450). Embedder: http:nomic 768d [NOMINAL].")
        self.assertEqual(lines[1:4], ["  note4: detail 4  (recalled 3x, last 1m ago)",
                                      "  note3: detail 3  (never recalled)",
                                      "  ...and 3 more (newest first; /memory <word> to filter, /memory why <name> to trace)."])

    def test_a_filter_narrows_the_list(self):
        state = {"self": {"memory": {"sister_name": "Odalys", "pet_name": "Brisket"}}, "world": {}}
        lines = memory_report(state, {}, [], 500, "hash", needle="brisket")
        self.assertIn("Matching 'brisket': 1.", lines)
        self.assertTrue(any(l.startswith("  pet_name: Brisket") for l in lines))
        self.assertFalse(any("Odalys" in l for l in lines))


class TheCommand(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.log = self.engine.cmd.interface.log = MagicMock()

    def shown(self):
        return "\n".join(str(c.args[0]) for c in self.log.call_args_list)

    def nominate(self, line):
        store = self.engine.store
        seq, state = store.state()
        gate = Gate(self.engine.boundary, state, self.engine.gate_tools, self.engine.gate_invariants)
        text = f"Said.\n{line}"
        store.commit_cycle("t", gate.state, seq, gate.adjudicate(text), text)

    def test_hidden_in_conversation(self):
        self.engine.cortex.active_mode, self.engine.ui_mode = "CONVERSATION", "WARM"
        self.nominate("NOMINATE what=self/memory/sister_name verb=remember args=key:sister_name; value:Odalys")
        self.engine.cmd.execute("/memory")
        self.assertIn("/memory is for TECHNICAL mode or the DEEP HUD", self.shown())
        self.assertNotIn("Odalys", self.shown())

    def test_technical_shows_the_memory_the_world_and_the_decisions(self):
        self.engine.cortex.active_mode, self.engine.ui_mode = "TECHNICAL", "WARM"
        self.nominate("NOMINATE what=self/memory/sister_name verb=remember args=key:sister_name; value:Odalys")
        self.nominate("NOMINATE what=self/identity verb=remember args=key:name; value:Iris")
        self.engine.store.note_recalled(["sister_name"])
        self.engine.cmd.execute("/memory")
        out = self.shown()
        self.assertIn("MEMORY: 1 kept of 500", out)
        self.assertIn("sister_name: Odalys  (kept 0s ago in TECHNICAL by the model; recalled 1x", out)
        self.assertIn("WORLD: 0 nodes", out)
        self.assertIn("ACCEPT remember self/memory/sister_name", out)
        self.assertIn("DENY   remember self/identity: 'self/identity' is outside the declared state scope", out)

    def test_the_deep_hud_shows_it_in_any_mode(self):
        self.engine.cortex.active_mode, self.engine.ui_mode = "ADVENTURE", "DEEP"
        self.engine.cmd.execute("/memory")
        self.assertIn("Nothing kept yet.", self.shown())
        self.assertIn("RECENT GATE DECISIONS: none yet.", self.shown())

    def test_plain_turns_are_not_listed_as_decisions(self):
        self.engine.cortex.active_mode = "TECHNICAL"
        store = self.engine.store
        seq, state = store.state()
        gate = Gate(self.engine.boundary, state, self.engine.gate_tools, self.engine.gate_invariants)
        store.commit_cycle("t", gate.state, seq, gate.adjudicate("Just talking."), "Just talking.")
        self.assertEqual(store.recent_decisions(), [])

    def test_it_is_in_the_help(self):
        self.engine.cmd.execute("/help")
        from engine.constants import Prisma

        maintenance = Prisma.strip(self.shown()).split("[MAINTENANCE]", 1)[1].split("\n[", 1)[0]
        self.assertIn("/memory", maintenance)
