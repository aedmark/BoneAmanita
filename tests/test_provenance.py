"""Provenance (bone-iris's roadmap: receipt IDs on the facts, not just in the log): what a commit writes to
the world carries its receipt in `sources`, each memory records who kept it and the receipt, and
`/memory why <name>` traces either back to the person's words and the gate's checks."""

import os
import sqlite3
import tempfile
from unittest.mock import MagicMock

from engine.gate.report import why_report
from engine.gate.store import Store, stamp_sources
from engine.constants import Prisma
from tests.base import BoneTestCase

PROSE = "The river runs east past the mill."
CREATE = "NOMINATE what=world/node/Riverhold verb=create args=type:city; name:Riverhold"


def world(nodes=None, edges=None):
    return {"schema_version": 2, "sources": {}, "nodes": nodes or {}, "edges": edges or [], "constraints": []}


class TheStamp(BoneTestCase):
    def test_what_changed_carries_the_receipt_and_the_rest_does_not(self):
        old = world({"a": {"id": "a", "label": "A", "sources": ["r0"]}}, [{"id": "e1", "status": "active", "sources": ["r0"]}])
        old["sources"] = {"r0": {"kind": "gate"}}
        new = world({"a": {"id": "a", "label": "A", "sources": ["r0"]}, "b": {"id": "b", "label": "B"}},
                    [{"id": "e1", "status": "retired", "sources": ["r0"]}])
        out = stamp_sources(old, new, "r1", {"kind": "gate", "verb": "chart"})
        self.assertEqual(out["nodes"]["a"]["sources"], ["r0"])
        self.assertEqual(out["nodes"]["b"]["sources"], ["r1"])
        self.assertEqual(out["edges"][0]["sources"], ["r0", "r1"])
        self.assertEqual(set(out["sources"]), {"r0", "r1"})
        self.assertNotIn("sources", new["nodes"]["b"])  # the caller's state is left alone

    def test_an_uncited_source_is_dropped_and_the_list_is_capped(self):
        out = stamp_sources(world(), world(), "r1", {"kind": "gate"})
        self.assertEqual(out["sources"], {})
        many = world({"a": {"id": "a", "label": "A", "sources": [f"r{i}" for i in range(8)]}})
        changed = world({"a": {"id": "a", "label": "A2", "sources": [f"r{i}" for i in range(8)]}})
        self.assertEqual(stamp_sources(many, changed, "r8", {})["nodes"]["a"]["sources"], [f"r{i}" for i in range(1, 9)])

    def test_an_older_store_gains_the_new_columns(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "iris.db")
            db = sqlite3.connect(path)
            db.execute("CREATE TABLE memory_meta (key TEXT PRIMARY KEY, mode TEXT, turn_id TEXT NOT NULL, kept_at REAL NOT NULL)")
            db.commit()
            db.close()
            Store(path)
            columns = {r[1] for r in sqlite3.connect(path).execute("PRAGMA table_info(memory_meta)")}
        self.assertTrue({"receipt_id", "kept_by", "feeling_json"} <= columns)


class WhereThingsCameFrom(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode, self.engine.ui_mode = "TECHNICAL", "WARM"
        self.keeps, self.reply = "NONE", "Noted."
        self.engine.cortex.llm.generate = MagicMock(
            side_effect=lambda prompt, *a, **k: self.keeps if prompt.startswith("You keep the memory") else self.reply)
        self.log = self.engine.cmd.interface.log = MagicMock()

    def turn(self, message, keeps="NONE", reply="Noted."):
        self.keeps, self.reply = keeps, reply
        self.engine.process_turn(message)

    def shown(self, command):
        self.log.reset_mock()
        self.engine.cmd.execute(command)
        return Prisma.strip("\n".join(str(c.args[0]) for c in self.log.call_args_list))

    def test_a_world_node_carries_its_receipt(self):
        self.turn("Tell me of Riverhold.", reply=f"{PROSE}\n{CREATE}")
        world = self.engine.store.state()[1]["world"]
        (rid,) = world["nodes"]["entity:riverhold"]["sources"]
        self.assertTrue(rid.startswith("rcpt_"))
        self.assertEqual({k: world["sources"][rid][k] for k in ("kind", "verb", "mode", "by")},
                         {"kind": "gate", "verb": "create", "mode": "TECHNICAL", "by": "model"})
        self.assertEqual(self.engine.store.provenance(rid)["user_text"], "Tell me of Riverhold.")

    def test_a_memory_records_who_kept_it(self):
        self.turn("My sister Odalys is visiting next week.", keeps="sister_name = Odalys, visiting next week")
        meta = self.engine.store.memory_meta()["sister_name"]
        self.assertEqual((meta["mode"], meta["kept_by"]), ("TECHNICAL", "keeper"))
        self.assertTrue(meta["receipt_id"].startswith("rcpt_"))
        self.assertEqual(self.engine.store.state()[1]["world"]["sources"], {})  # a memory adds no world source

    def test_memory_says_who_kept_each_one(self):
        self.turn("My sister Odalys is visiting next week.", keeps="sister_name = Odalys")
        self.assertIn("sister_name: Odalys  (kept 0s ago in TECHNICAL by the memory keeper; never recalled)",
                      self.shown("/memory"))

    def test_why_traces_a_memory_to_the_persons_words(self):
        self.turn("My sister Odalys is visiting next week.", keeps="sister_name = Odalys")
        out = self.shown("/memory why sister_name")
        self.assertIn("  Kept 0s ago in TECHNICAL by the memory keeper.", out)
        self.assertIn('The person said: "My sister Odalys is visiting next week."', out)
        self.assertIn("The gate: schema PASS, what PASS, verb-auth PASS, args PASS, screen PASS", out)

    def test_why_traces_a_world_node(self):
        self.turn("Tell me of Riverhold.", reply=f"{PROSE}\n{CREATE}")
        out = self.shown("/memory why riverhold")
        self.assertIn("Riverhold (city), written by 1 commit(s):", out)
        self.assertIn("create 0s ago in TECHNICAL by the model", out)
        self.assertIn('The person said: "Tell me of Riverhold."', out)

    def test_why_finds_a_story_memory_by_its_plain_name(self):
        self.engine.cortex.active_mode = "ADVENTURE"
        self.turn("The vault opens at midnight.", keeps="vault = opens at midnight")
        self.engine.cortex.active_mode = "TECHNICAL"
        self.assertIn("story.vault: opens at midnight", self.shown("/memory why vault"))

    def test_why_says_when_nothing_is_there(self):
        self.assertIn("Nothing kept under 'nobody'.", self.shown("/memory why nobody"))

    def test_a_memory_without_a_source_says_so(self):
        state = {"self": {"memory": {"old": "thing"}}, "world": {}}
        self.assertIn("  Kept before its source was recorded.", why_report("old", state, {}, {}, lambda r: None))

    def test_a_charted_room_names_the_cartographer(self):
        from types import SimpleNamespace

        room = {"name": "The Mill Loft", "description": "Dust and old sacks.", "exits": ["North to Riverside Path"], "pois": ["a lamp"]}
        self.engine.orchestrator._chart_room(SimpleNamespace(trace_id="t"), room)
        world = self.engine.store.state()[1]["world"]
        (rid,) = world["nodes"]["entity:the-mill-loft"]["sources"]
        self.assertEqual((world["sources"][rid]["verb"], world["sources"][rid]["by"]), ("chart", "cartographer"))


class WhatTheModelWasHanded(BoneTestCase):
    """turn_contexts, adopted on purpose (Gordon, 2026-09-29): what each reply was handed, and its tokens."""

    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode, self.engine.ui_mode = "TECHNICAL", "WARM"
        self.keeps = "NONE"
        self.engine.cortex.llm.generate = MagicMock(
            side_effect=lambda prompt, *a, **k: self.keeps if prompt.startswith("You keep the memory") else "Noted.")
        self.engine.cortex.llm.last_usage = {"prompt_tokens": 5412, "output_tokens": 80, "num_ctx": 16384}
        self.log = self.engine.cmd.interface.log = MagicMock()

    def turn(self, message, keeps="NONE"):
        self.keeps = keeps
        self.engine.process_turn(message)

    def test_each_reply_records_what_it_was_handed_and_its_tokens(self):
        self.turn("My sister is Odalys.", keeps="sister_name = Odalys")
        self.turn("How is my sister?", keeps="pet_name = Brisket")
        db = self.engine.store.connect()
        try:
            rows = db.execute("SELECT c.*, t.input_tokens, t.output_tokens, t.total_tokens, t.context_limit, "
                              "t.token_count_source FROM turn_contexts c JOIN turns t ON t.id=c.turn_id "
                              "ORDER BY c.created_at").fetchall()
        finally:
            db.close()
        last = dict(rows[-1])
        self.assertEqual((last["mode"], last["zone"], last["recalled_json"]), ("TECHNICAL", "real", '["sister_name"]'))
        self.assertEqual((last["input_tokens"], last["output_tokens"], last["total_tokens"], last["context_limit"],
                          last["token_count_source"]), (5412, 80, 5492, 16384, "provider"))

    def test_why_says_what_the_model_had_been_handed(self):
        self.turn("My sister is Odalys.", keeps="sister_name = Odalys")
        self.turn("She has a dog, Brisket.", keeps="pet_name = Brisket")
        self.engine.cmd.execute("/memory why pet_name")
        out = Prisma.strip("\n".join(str(c.args[0]) for c in self.log.call_args_list))
        self.assertIn("The model had been handed 1 memory (sister_name) and 0 facts; the prompt was 5,412 of 16,384 tokens.", out)


    def test_a_held_turn_records_no_stale_context(self):
        from unittest.mock import patch

        from archetypes.stage import HOLD, StageManager, Tension, Verdict

        self.turn("My sister is Odalys.", keeps="sister_name = Odalys")
        verdict = Verdict(HOLD, "THE STAGE MANAGER", "held for the test", Tension(("MOIRA", "CASSANDRA")), gate="ATP_FLOOR")
        with patch.object(StageManager, "negotiate", return_value=verdict):
            self.turn("Our deploy window is Thursdays.", keeps="deploy_window = Thursdays")
        db = self.engine.store.connect()
        try:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM turn_contexts").fetchone()[0], 1)
        finally:
            db.close()

    def test_only_a_real_context_is_recorded(self):
        self.engine.cortex.last_context = "not a context"
        self.assertIsNone(self.engine.orchestrator._turn_context())


class ThePrunedStore(BoneTestCase):
    """Iris's parts BoneAmanita had no use for are gone from new and old stores; the shelved trio stays."""

    PRUNED = {"turn_braid_contexts", "turn_system_contexts", "memory_entries", "active_context", "capabilities",
              "tool_receipts", "imagination_runs", "imagination_turns"}
    DORMANT = {"affect_state", "affect_history", "self_claims", "seed_imports", "domain_versions"}

    def tables(self, path):
        db = sqlite3.connect(path)
        try:
            return {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            db.close()

    def test_a_new_store_has_only_what_is_used_and_the_shelved_trio(self):
        tables = self.tables(self.engine.store.path)
        self.assertFalse(self.PRUNED & tables)
        self.assertTrue(self.DORMANT <= tables)

    def test_an_old_store_is_pruned_and_its_turn_contexts_reshaped(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "iris.db")
            db = sqlite3.connect(path)
            for table in self.PRUNED:
                db.execute(f"CREATE TABLE {table} (x TEXT)")
            db.execute("CREATE TABLE turn_contexts (turn_id TEXT PRIMARY KEY, instructions_text TEXT NOT NULL)")
            db.commit()
            db.close()
            Store(path)
            self.assertFalse(self.PRUNED & self.tables(path))
            columns = {r[1] for r in sqlite3.connect(path).execute("PRAGMA table_info(turn_contexts)")}
        self.assertIn("recalled_json", columns)
        self.assertNotIn("instructions_text", columns)
