"""Secrets stay out of the store: the gate's no_secrets screen refuses a credential, key, card or ID number
in any nomination, and the audit trail and checkpoint keep only "[withheld: ...]" in its place.
In ADVENTURE a password is a puzzle, so there only the shapes count."""

import copy
import sqlite3
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import yaml

from engine.gate.kernel import Boundary, Gate
from engine.gate.secrets import credential_key, kind_of, redact, scrub
from engine.gate.tools import TOOLS, build_invariants
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase

KEY = "sk-proj-abcdEFGH1234ijklMNOP5678"
SHAPES = {
    KEY: "an API key",
    "ghp_abcdefghijklmnopqrstuvwxyz0123456789": "an API key",
    "AKIAIOSFODNN7EXAMPLE": "an API key",
    "-----BEGIN RSA PRIVATE KEY-----": "a private key",
    "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U": "a signed token",
    "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY": "an encoded token",
    "d41d8cd98f00b204e9800998ecf8427e": "a long hex key",
    "4111 1111 1111 1111": "a card number",
    "378282246310005": "a card number",
    "123-45-6789": "a government ID number",
    "my password is hunter2": "a password",
    "The PIN is 4821": "a PIN",
}
ORDINARY = ["Odalys, visiting next week", "commit 96485b0", "https://github.com/aedmark/BoneAmanita",
            "antidisestablishmentarianism", "+1 555 123 4567", "call me at 555-867-5309", "2026-09-27",
            "the password is in the drawer", "/home/gordonk/PycharmProjects/BoneAmanita/tests/test2",
            "getUserAccountBalanceForId2", "123e4567-e89b-12d3-a456-426614174000", "4111 1111 1111 1112",
            "archive/SESSION_LOGS_2026_09.md", "run 20260924-074939", "thermal_z 0.038104142842068756",
            "epoch 1790439252000", "pinball wizard"]


class TheDetector(BoneTestCase):
    def test_it_knows_the_shapes(self):
        for text, kind in SHAPES.items():
            self.assertEqual(kind_of(text), kind, text)

    def test_ordinary_things_pass(self):
        for text in ORDINARY:
            self.assertIsNone(kind_of(text), text)

    def test_credential_names(self):
        for key in ("wifi_password", "bank_pin", "api_key", "openai_api_key", "github_token", "card number"):
            self.assertTrue(credential_key(key), key)
        for key in ("password_hint", "password_manager", "sister_name", "pinball_score", "pet_name"):
            self.assertFalse(credential_key(key), key)

    def test_in_a_story_a_password_is_a_puzzle_but_a_key_is_still_a_key(self):
        self.assertIsNone(kind_of("the password is moonlight", in_story=True))
        self.assertEqual(kind_of(KEY, in_story=True), "an API key")

    def test_withheld_names_the_kind_only(self):
        self.assertEqual(redact(f"my key is {KEY} ok"), "my key is [withheld: an API key] ok")
        line = "NOMINATE what=self/memory/wifi_password verb=remember args=key:wifi_password; value:hunter2"
        self.assertEqual(scrub(f"Noted.\n{line}"),
                         "Noted.\nNOMINATE what=self/memory/wifi_password verb=remember args=[withheld: a secret]")


class TheScreen(BoneTestCase):
    def gate(self, in_story=False, memory=None):
        spec = yaml.safe_load(open("engine/gate/boundary.yaml"))
        state = {"world": {"schema_version": 2, "sources": {}, "nodes": {}, "edges": [], "constraints": []},
                 "self": {"memory": dict(memory or {})}}
        return Gate(Boundary(spec), state, TOOLS, build_invariants(spec, in_story=lambda: in_story))

    def remember(self, gate, key, value):
        return gate.adjudicate(f"Kept.\nNOMINATE what=self/memory/{key} verb=remember args=key:{key}; value:{value}")

    def test_a_secret_value_is_refused_without_repeating_it(self):
        gate = self.gate()
        receipt = self.remember(gate, "openai", KEY)
        self.assertEqual(receipt["decision"], "DENY")
        self.assertEqual(receipt["decision_basis"][-1][:2], ["screen", "DENY"])
        self.assertIn("value looks like an API key", receipt["decision_basis"][-1][2])
        self.assertNotIn(KEY, str(receipt["decision_basis"]))
        self.assertEqual(gate.state["self"]["memory"], {})

    def test_a_memory_named_as_a_credential_is_refused(self):
        receipt = self.remember(self.gate(), "wifi_password", "swordfish")
        self.assertEqual(receipt["decision"], "DENY")
        self.assertIn("named as a credential", receipt["decision_basis"][-1][2])

    def test_ordinary_memories_pass_the_screen(self):
        gate = self.gate()
        receipt = self.remember(gate, "sister_name", "Odalys")
        self.assertEqual(receipt["decision"], "ACCEPT")
        self.assertIn(["screen", "PASS", "1 screen(s) hold"], receipt["decision_basis"])

    def test_a_story_keeps_its_passwords_but_not_real_keys(self):
        self.assertEqual(self.remember(self.gate(in_story=True), "door_password", "moonlight")["decision"], "ACCEPT")
        self.assertEqual(self.remember(self.gate(in_story=True), "door", KEY)["decision"], "DENY")

    def test_world_writes_are_screened_too(self):
        receipt = self.gate().adjudicate(f"A place.\nNOMINATE what=world/node/x verb=create args=type:city; name:{KEY}")
        self.assertEqual(receipt["decision"], "DENY")

    def test_forgetting_a_secret_is_always_allowed(self):
        named = "ghp_abcdefghijklmnopqrstuvwxyz0123456789"  # a key kept under its own name
        gate = self.gate(memory={named: "hunter2"})
        receipt = gate.adjudicate(f"(Forgetting)\nNOMINATE what=self/memory/consolidation verb=forget args=keys:{named}")
        self.assertEqual((receipt["decision"], gate.state["self"]["memory"]), ("ACCEPT", {}))

    def test_the_attestation_says_so(self):
        self.assertEqual(self.engine.boundary.attestation()["screens"], ["no_secrets"])


class SecretsNeverReachTheStore(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.engine.memory_keeper.enabled = True
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.active_mode = "CONVERSATION"  # tests boot in ADVENTURE

    def respond(self, reply, keeps):
        self.engine.cortex.llm.generate = MagicMock(
            side_effect=lambda prompt, *a, **k: keeps if prompt.startswith("You keep the memory") else reply)

    def on_disk(self):
        db = sqlite3.connect(self.engine.store.path)
        try:
            tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            return "\n".join(str(row) for t in tables for row in db.execute(f"SELECT * FROM {t}"))
        finally:
            db.close()

    def memory(self):
        return self.engine.store.state()[1]["self"]["memory"]

    def test_a_pasted_key_is_refused_and_withheld_everywhere(self):
        self.respond(f"Got it, {KEY} is noted.", f"openai_api_key = {KEY}")
        self.engine.process_turn(f"Here's my OpenAI key: {KEY}")
        self.engine.cortex.dialogue_buffer.append(f"Traveler: my wifi password is hunter2, key {KEY}")
        self.chronos_patcher.stop()  # the test base patches saving out
        self.engine.save_checkpoint()
        self.assertEqual(self.memory(), {})
        self.assertEqual(ReceiptLedger.get_instance().for_subsystem("halcyon.gate")[-1].effect, "DENY")
        self.assertNotIn(KEY, ReceiptLedger.get_instance().for_subsystem("halcyon.keeper")[-1].detail)
        disk = self.on_disk()
        self.assertNotIn(KEY, disk)
        self.assertNotIn("hunter2", disk)
        self.assertIn("[withheld: a secret]", self.engine.store.audit("proposals")[0]["raw_line"])
        self.assertIn("[withheld: an API key]", disk)
        self.assertIn("my wifi password is [withheld: a password]", str(self.engine.store.checkpoint()))

    def test_an_adventure_keeps_the_doors_password(self):
        self.engine.cortex.active_mode = "ADVENTURE"
        self.respond("The door listens.", "door_password = moonlight")
        self.engine.process_turn("The old man said the door's password is moonlight.")
        self.assertEqual(self.memory().get("story.door_password"), "moonlight")
        # The story's audit trail keeps it too; a resumed adventure needs its riddle.
        self.assertIn("value:moonlight", self.engine.store.audit("proposals")[0]["raw_line"])

    def keep_unscreened(self, key, value, mode):
        """A memory as kept before the screen existed, in `mode`."""
        spec = copy.deepcopy(self.engine.boundary.spec)
        spec.pop("screens")
        self.engine.cortex.active_mode = mode
        seq, state = self.engine.store.state()
        gate = Gate(Boundary(spec), state, TOOLS, build_invariants(spec))
        text = f"Old.\nNOMINATE what=self/memory/{key} verb=remember args=key:{key}; value:{value}"
        self.engine.store.commit_cycle("legacy", gate.state, seq, gate.adjudicate(text), text)

    def rem(self):
        embedder = SimpleNamespace(degraded=True, backend="hash", model="shake_256")
        with patch("spores.embeddings.SemanticEmbedder.get_instance", return_value=embedder):
            self.engine.orchestrator._process_rem_tick()

    def test_rem_forgets_secrets_kept_before_the_screen_but_not_a_storys(self):
        self.keep_unscreened("wifi_password", "swordfish", "CONVERSATION")
        self.keep_unscreened("openai", KEY, "TECHNICAL")
        self.keep_unscreened("door_password", "moonlight", "ADVENTURE")
        self.assertEqual(self.engine.store.memory_modes(),
                         {"wifi_password": "CONVERSATION", "openai": "TECHNICAL", "door_password": "ADVENTURE"})
        self.rem()
        self.assertEqual(self.memory(), {"door_password": "moonlight"})
        self.assertEqual(self.engine.store.memory_modes(), {"door_password": "ADVENTURE"})
        self.assertNotIn(KEY, self.on_disk())

    def test_a_memory_from_before_modes_is_judged_in_full(self):
        self.keep_unscreened("vault_password", "moonlight", "ADVENTURE")
        db = sqlite3.connect(self.engine.store.path)
        db.execute("DELETE FROM memory_meta")
        db.commit()
        db.close()
        self.rem()
        self.assertEqual(self.memory(), {})


class SecretsNeverReachTheOtherFiles(BoneTestCase):
    """Beyond iris.db: the tokenizer's words, telemetry, the crash log and spores."""

    def test_no_fragment_of_a_key_becomes_a_word(self):
        words = self.engine.lex.sanitize(f"here is my key {KEY} and my password is hunter2")
        self.assertFalse({"abcdefgh1234ijklmnop5678", "proj", "hunter2"} & set(words), words)
        self.assertIn("here", words)

    def test_telemetry_withholds(self):
        import os
        import tempfile

        from engine.core import TelemetryService

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        telemetry = TelemetryService()
        self.addCleanup(telemetry.shutdown)
        telemetry.current_trace_file = os.path.join(directory.name, "trace.jsonl")
        telemetry.record_event({"text": f"Traveler: {KEY}"})
        self.assertIn("[withheld: an API key]", telemetry.write_buffer[-1])
        telemetry.start_cycle("t")
        telemetry.active_crystal.final_response = f"Noted, {KEY}."
        telemetry.active_crystal.prompt_snapshot = "my wifi password is hunter2"
        telemetry.log_crystal(telemetry.active_crystal)
        self.assertNotIn(KEY, "".join(telemetry.write_buffer))
        self.assertNotIn("hunter2", "".join(telemetry.write_buffer))

    def test_the_crash_log_withholds(self):
        import os
        import tempfile

        from engine.core import record_crash

        with tempfile.TemporaryDirectory() as log_dir:
            record_crash(SimpleNamespace(telemetry=SimpleNamespace(log_dir=log_dir)), "boom", ValueError(f"bad {KEY}"))
            logged = open(os.path.join(log_dir, "crashes.log")).read()
        self.assertIn("[withheld: an API key]", logged)
        self.assertNotIn(KEY, logged)

    def test_a_spore_withholds(self):
        import tempfile

        from spores.io import LocalFileSporeLoader

        self.spore_patcher.stop()  # the test base patches saving out
        with tempfile.TemporaryDirectory() as directory:
            path = LocalFileSporeLoader(directory).save_spore("s.json", {"continuity": {"last_output": f"key {KEY}"}})
            saved = open(path).read()
        self.assertNotIn(KEY, saved)
        self.assertIn("[withheld: an API key]", saved)
