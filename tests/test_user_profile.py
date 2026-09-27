"""Roadmap step 3f: the user profile is learned each turn and kept in the Halcyon store.

UserProfile existed since 19.6.0 but nothing constructed it, so user_profile.json was never written.
The engine now builds one, feeds it every user turn, and keeps it as the user.profile record."""

import json
import os
from pathlib import Path
import tempfile
from unittest.mock import MagicMock

from drivers.userprofile import UserProfile
from engine.gate.store import Store
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

HEAVY = "The anvil and the granite boulder sat on the bedrock like an anchor of iron."


class TheProfileLearnsEachTurn(BoneTestCase):
    def turn(self, message):
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value="Noted.")
        return self.engine.process_turn(message)

    def receipts(self):
        return ReceiptLedger.get_instance().for_subsystem("user.profile")

    def test_a_user_turn_moves_the_profile_and_keeps_it(self):
        self.turn(HEAVY)
        profile = self.engine.user_profile
        self.assertGreater(profile.affinities["heavy"], 0.0)
        self.assertEqual(profile.confidence, 1)
        saved = self.engine.store.record("user.profile")
        self.assertEqual(saved["affinities"]["heavy"], profile.affinities["heavy"])
        receipt = self.receipts()[-1]
        self.assertEqual(receipt.effect, "LEARNED")
        self.assertIn("heavy", receipt.detail)
        self.assertFalse(os.path.exists("user_profile.json"))

    def test_a_short_turn_is_skipped_and_receipted(self):
        self.turn("hi")
        self.assertEqual(self.engine.user_profile.confidence, 0)
        self.assertIsNone(self.engine.store.record("user.profile"))
        self.assertEqual(self.receipts()[-1].effect, "SKIPPED")

    def test_the_next_engine_knows_the_person(self):
        self.turn(HEAVY)
        profile = UserProfile(config_ref=self.engine.config)
        profile.attach_store(self.engine.store)
        self.assertEqual(profile.affinities, self.engine.user_profile.affinities)
        self.assertEqual(profile.confidence, 1)


class AnOldProfileIsImported(BoneTestCase):
    def test_an_old_profile_is_imported_once_and_kept(self):
        with tempfile.TemporaryDirectory() as d:
            legacy = os.path.join(d, "user_profile.json")
            with open(legacy, "w", encoding="utf-8") as f:
                json.dump({"name": "T", "affinities": {"heavy": 0.4}, "confidence": 12}, f)
            store = Store(path=Path(d) / "iris.db", state_dir=d)
            profile = UserProfile(config_ref=self.engine.config)
            profile.file_path = legacy
            profile.attach_store(store)
            self.assertEqual((profile.affinities["heavy"], profile.confidence), (0.4, 12))
            self.assertEqual(store.record("user.profile")["confidence"], 12)
            self.assertFalse(os.path.exists(legacy))
            self.assertTrue(os.path.exists(legacy + ".imported"))
