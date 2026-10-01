"""Memory phase 4: the world graph is the story's truth in ADVENTURE. Each room the narrator describes is
charted through the gate in its own cycle (Gordon's call), and the next prompt reads the room, its exits
and what is in it back from the graph instead of scraping the last reply."""

import copy
from unittest.mock import MagicMock

import yaml

from lichen.cartographer import chart_args, chart_line, room_view
from engine.gate.graph import empty_world
from engine.gate.kernel import Boundary, Gate
from engine.gate.tools import TOOLS, build_invariants
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

LOFT = {"name": "The Mill Loft", "description": "Dust over a stopped wheel.",
        "exits": ["North (via Iron Door) to The Yard", "Down to The Mill Floor"], "pois": ["A sack of grain", "A lamp"]}
REPLY = ("**The Mill Loft**\nDust over a stopped wheel.\n\n**Points of Interest:**\n- A sack of grain\n- A lamp\n\n"
         "**Exits:**\n- North (via Iron Door) to The Yard\n- Down to The Mill Floor")


def chart(state, room):
    spec = yaml.safe_load(open("engine/gate/boundary.yaml"))
    gate = Gate(Boundary(spec), copy.deepcopy(state), TOOLS, build_invariants(spec))
    receipt = gate.adjudicate(f"(Cartographer)\n{chart_line(chart_args(room))}")
    return receipt, gate.state


class TheChartVerb(BoneTestCase):
    def fresh(self):
        return {"world": empty_world(), "self": {"memory": {}}}

    def test_a_room_is_charted_with_its_exits_and_things(self):
        receipt, state = chart(self.fresh(), LOFT)
        self.assertEqual(receipt["decision"], "ACCEPT")
        self.assertEqual(room_view(state, "The Mill Loft"), {
            "name": "The Mill Loft", "description": "Dust over a stopped wheel.",
            "exits": ["North to The Yard", "Down to The Mill Floor"], "items": ["A sack of grain", "A lamp"]})

    def test_charting_the_same_room_again_changes_nothing(self):
        _, state = chart(self.fresh(), LOFT)
        receipt, again = chart(state, LOFT)
        self.assertIn("noop", receipt["result"])
        self.assertEqual(again, state)

    def test_what_is_gone_is_retired_not_deleted(self):
        _, state = chart(self.fresh(), LOFT)
        _, state = chart(state, dict(LOFT, pois=["A lamp"]))
        self.assertEqual(room_view(state, "The Mill Loft")["items"], ["A lamp"])
        sack = [e for e in state["world"]["edges"] if e["source"] == "entity:a-sack-of-grain"]
        self.assertEqual([e["status"] for e in sack], ["retired"])

    def test_a_thing_seen_elsewhere_leaves_the_old_room(self):
        _, state = chart(self.fresh(), LOFT)
        _, state = chart(state, {"name": "The Yard", "description": "Mud.", "exits": ["South to The Mill Loft"], "pois": ["A lamp"]})
        self.assertEqual(room_view(state, "The Mill Loft")["items"], ["A sack of grain"])
        self.assertEqual(room_view(state, "The Yard")["items"], ["A lamp"])

    def test_nothing_is_charted_under_a_zone(self):
        self.assertIsNone(chart_args(dict(LOFT, name="VOID_DRIFT")))
        self.assertIsNone(chart_args(dict(LOFT, name="Uncharted Zone")))

    def test_separators_in_the_text_cannot_split_an_arg(self):
        args = chart_args(dict(LOFT, description="Dust; wheels | gears.", pois=["Rope; coiled"]))
        receipt, state = chart(self.fresh(), dict(LOFT, description="Dust; wheels | gears.", pois=["Rope; coiled"]))
        self.assertEqual(receipt["decision"], "ACCEPT")
        self.assertEqual(args["description"], "Dust, wheels / gears.")
        self.assertEqual(room_view(state, "The Mill Loft")["items"], ["Rope, coiled"])

    def test_the_model_is_not_offered_the_verb(self):
        from engine.gate.tools import grammar_text

        self.assertNotIn("verb=chart", grammar_text(yaml.safe_load(open("engine/gate/boundary.yaml"))))


class TheCartographerInPlay(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.cortex.dspy_critic.enabled = False
        self.assertEqual(self.engine.cortex.active_mode, "ADVENTURE")

    def turn(self, reply, message="I look around."):
        self.engine.cortex.llm.generate = MagicMock(return_value=reply)
        return self.engine.process_turn(message)

    def prompt(self):
        return self.engine.cortex.llm.generate.call_args[0][0]

    def charts(self):
        return ReceiptLedger.get_instance().for_subsystem("halcyon.chart")

    def test_a_described_room_is_charted_in_its_own_gate_cycle(self):
        self.turn(REPLY)
        self.assertEqual([r.effect for r in self.charts()], ["ACCEPT"])
        _, state = self.engine.store.state()
        self.assertEqual(room_view(state, "The Mill Loft")["exits"], ["North to The Yard", "Down to The Mill Floor"])
        proposals = self.engine.store.audit("proposals")
        self.assertEqual([p["verb"] for p in proposals], ["chart"])
        self.assertEqual(len(self.engine.store.audit("turns")), 2)

    def test_the_same_room_is_not_charted_again(self):
        self.turn(REPLY)
        self.turn(REPLY, "I wait.")
        self.assertEqual(len(self.charts()), 1)

    def test_the_next_prompt_reads_the_room_from_the_graph(self):
        self.turn(REPLY)
        # The narrator's next reply drops the exits; the graph still holds them.
        self.turn("**The Mill Loft**\nThe wheel creaks.", "I listen.")
        self.turn("**The Mill Loft**\nStill.", "I wait.")
        prompt = self.prompt()
        self.assertIn("CURRENT EXITS:\n**Exits:**\n- North to The Yard\n- Down to The Mill Floor", prompt)
        self.assertIn("ON RECORD HERE: A sack of grain, A lamp.", prompt)

    def test_a_turn_with_no_room_charts_nothing(self):
        self.turn("The wind picks up.")
        self.assertEqual(self.charts(), [])

    def test_charted_rooms_stay_out_of_the_remembered_facts(self):
        from engine.gate.recall import recall

        self.turn(REPLY)
        _, state = self.engine.store.state()
        self.assertEqual(recall(state, "Where is the lamp in the mill loft?")["facts"], [])

    def test_a_turn_with_no_room_does_not_rechart_the_last_one(self):
        self.turn(REPLY)
        # Meanwhile the lamp is charted in the yard; a stale Loft chart would pull it back.
        seq, state = self.engine.store.state()
        receipt, moved = chart(state, {"name": "The Yard", "description": "Mud.", "exits": [], "pois": ["A lamp"]})
        self.engine.store.commit_cycle("t", moved, seq, receipt, "raw")
        self.turn("The wind picks up.", "I wait.")
        _, state = self.engine.store.state()
        self.assertEqual(room_view(state, "The Yard")["items"], ["A lamp"])
        self.assertEqual(len(self.charts()), 1)
