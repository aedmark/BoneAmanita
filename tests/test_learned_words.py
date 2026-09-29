"""Roadmap step 3c: the words the lexicon teaches itself live in the Halcyon store.

They were saves/cortex_hive.json, written only at shutdown, so a crash lost everything learned
since boot. Each word is now durable the moment it is learned."""

import json
import os
from pathlib import Path
import tempfile

from engine.gate.store import Store
from mechanics.lexicon import LexiconService
from tests.base import BoneTestCase


class LearnedWordsLiveInTheStore(BoneTestCase):
    def fresh_lexicon(self, store, hive=None):
        lex = LexiconService()
        if hive:
            lex._STORE.HIVE_FILENAME = hive
        lex.attach_store(store)
        return lex

    def test_a_word_is_in_the_store_the_moment_it_is_learned(self):
        self.assertTrue(self.engine.lex._STORE.teach("quernstone", "heavy", 7))
        self.assertEqual(self.engine.store.learned_vocabulary().get("heavy", {}).get("quernstone"), 7)

    def test_the_next_engine_knows_what_this_one_learned(self):
        self.engine.lex._STORE.teach("quernstone", "heavy", 7)
        lex = self.fresh_lexicon(self.engine.store)
        self.assertIn("heavy", lex._STORE.get_categories_for_word("quernstone"))

    def test_a_word_evicted_from_a_full_category_leaves_the_store_too(self):
        full = {"heavy": {f"word{i:04d}": i + 1 for i in range(1000)}}
        self.engine.store.save_learned_vocabulary(full)
        lex = self.fresh_lexicon(self.engine.store)
        lex._STORE.teach("quernstone", "heavy", 5000)
        kept = self.engine.store.learned_vocabulary()["heavy"]
        self.assertNotIn("word0000", kept)
        self.assertEqual((len(kept), kept["quernstone"]), (1000, 5000))

    def test_the_shutdown_sync_writes_the_store_and_no_file(self):
        store = self.engine.lex._STORE
        store.LEARNED_VOCAB.setdefault("light", {})["feather"] = 3
        store.save_hive()
        self.assertEqual(self.engine.store.learned_vocabulary()["light"]["feather"], 3)
        self.assertFalse(os.path.exists(store.HIVE_FILENAME))

    def test_an_old_hive_is_imported_once_and_kept(self):
        with tempfile.TemporaryDirectory() as d:
            hive = os.path.join(d, "cortex_hive.json")
            with open(hive, "w", encoding="utf-8") as f:
                json.dump({"heavy": {"quernstone": 2}}, f)
            store = Store(path=Path(d) / "iris.db")
            lex = self.fresh_lexicon(store, hive)
            self.assertIn("heavy", lex._STORE.get_categories_for_word("quernstone"))
            self.assertEqual(store.learned_vocabulary(), {"heavy": {"quernstone": 2}})
            self.assertFalse(os.path.exists(hive))
            self.assertTrue(os.path.exists(hive + ".imported"))
