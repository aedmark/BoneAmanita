"""/tune (ROADMAP A7, Gordon 2026-09-30). The risk is a knob that reports success and changes nothing, so every
key /tune calls live is tuned here through the command and its behaviour seen to change; everything else is
reported as taking effect at the next start. Both config objects are set: six modules read the class."""

import copy
import json
import os
import tempfile
from unittest.mock import MagicMock, patch

from body.endocrine import EndocrineSystem
from body.somatic_budget import SomaticBudget
from engine import tuning
from engine.constants import Prisma
from engine.presets import BoneConfig
from engine.receipts import ReceiptLedger
from tests.base import BoneTestCase


class Tune(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.class_sectors = {k: copy.deepcopy(getattr(BoneConfig, k)) for k in BoneConfig._TEMPLATE_DATA}
        self.addCleanup(self._restore_class)
        self.said = []
        self.engine.cmd.interface.log = lambda text, *a, **k: self.said.append(Prisma.strip(str(text)))

    def _restore_class(self):
        for k, v in self.class_sectors.items():
            setattr(BoneConfig, k, v)
        if "GATE_TOLERANCE" in BoneConfig.__dict__:
            delattr(BoneConfig, "GATE_TOLERANCE")

    def tune(self, line):
        self.said.clear()
        self.engine.cmd.execute(line)
        return "\n".join(self.said)

    # Parsing and reporting.

    def test_values_are_read_as_the_settings_type(self):
        self.assertEqual([tuning.parse("true", False), tuning.parse("off", True), tuning.parse("7", 3),
                          tuning.parse("0.3", 0.2), tuning.parse("Night Desk", "")],
                         [True, False, 7, 0.3, "Night Desk"])
        self.assertEqual([tuning.parse("7.5", 3), tuning.parse("fast", 0.2), tuning.parse("maybe", True)],
                         [None, None, None])

    def test_a_bad_value_changes_nothing(self):
        before = self.engine.config.BIO.DECAY_RATE
        self.assertIn("takes a float", self.tune("/tune BIO DECAY_RATE fast"))
        self.assertEqual(self.engine.config.BIO.DECAY_RATE, before)

    def test_listing_marks_what_takes_effect_now_and_hides_credentials(self):
        self.assertIn("WHIMSY", self.tune("/tune"))
        listing = self.tune("/tune WHIMSY")
        self.assertIn("* LUDICROUS_SPEED", listing)
        self.assertNotIn("API_KEY", self.tune("/tune ROOT"))

    def test_a_key_nothing_rereads_says_so(self):
        self.assertIn("at the next start", self.tune("/tune BIO REWARD_MEDIUM 0.2"))

    def test_each_change_is_receipted_and_shown_in_diag(self):
        self.tune("/tune BIO DECAY_RATE 0.3")
        receipts = [r for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "config.tune"]
        self.assertEqual(receipts[-1].inputs["key"], "BIO.DECAY_RATE")
        self.assertIn("BIO.DECAY_RATE: 0.2 -> 0.3", self.tune("/diag"))

    # Live keys: tuned through the command, behaviour seen to change.

    def test_ludicrous_speed_reaches_the_typewriter_which_reads_the_class(self):
        from mechanics.terminal import typewriter

        self.tune("/tune WHIMSY LUDICROUS_SPEED false")
        with patch("mechanics.terminal.time.sleep") as slept, patch("builtins.print"), patch("sys.stdout"):
            typewriter("abc", speed=0.01)
        self.assertTrue(slept.called)
        self.assertIn("Takes effect now", self.tune("/tune WHIMSY LUDICROUS_SPEED true"))
        with patch("mechanics.terminal.time.sleep") as slept, patch("builtins.print"), patch("sys.stdout"):
            typewriter("abc", speed=0.01)
        self.assertFalse(slept.called)

    def test_decay_rate_zero_freezes_the_engines_chemistry(self):
        endo = EndocrineSystem(config_ref=self.engine.config)
        endo.oxytocin = 0.6
        self.tune("/tune BIO DECAY_RATE 0")
        endo.metabolize(health=100.0, stamina=100.0, feedback={}, social_context=False)
        self.assertAlmostEqual(endo.oxytocin, 0.6, places=6)

    def test_stutter_length_changes_what_the_validator_takes(self):
        v = self.engine.cortex.validator
        state = {"meta": {"active_mode": "CONVERSATION"}}
        self.assertTrue(v.validate("Sure, Thursday works.", state)["valid"])
        self.tune("/tune CORTEX VALIDATOR_STUTTER_LENGTH 100")
        self.assertEqual(v.validate("Sure, Thursday works.", state).get("reason"), "STUTTER")

    def test_atp_depleted_moves_the_budgets_line(self):
        user, engine = {"exhaustion": 0.0, "effort": 100.0}, {"atp_pool": 50.0}
        cap = lambda: SomaticBudget.evaluate(user, engine, "CONVERSATION", config_ref=self.engine.config).retry_allowance
        self.assertGreater(cap(), 1)
        self.tune("/tune SOMATIC_BUDGET ATP_DEPLETED 60")
        self.assertEqual(cap(), 1)

    def test_gate_tolerance_moves_the_crucibles_meltdown_and_the_next_mode_resets_it(self):
        crucible = self.engine.phys.crucible
        physics = lambda: {"voltage": 60.0, "narrative_drag": 0.0, "kappa": 0.0}
        crucible.instability_index = 0.0
        tight = crucible.audit_fire(physics())[0]
        self.assertIn("the next /mode resets it", self.tune("/tune ROOT GATE_TOLERANCE 50"))
        crucible.instability_index = 0.0
        self.assertNotEqual(crucible.audit_fire(physics())[0], tight)
        self.engine.switch_mode("CONVERSATION")
        self.assertNotEqual(self.engine.config.GATE_TOLERANCE, 50.0)

    def test_every_live_key_has_a_behaviour_test(self):
        tested = {"WHIMSY.LUDICROUS_SPEED", "BIO.DECAY_RATE", "CORTEX.VALIDATOR_STUTTER_LENGTH",
                  "SOMATIC_BUDGET.ATP_DEPLETED", "ROOT.GATE_TOLERANCE"}
        self.assertEqual(tuning.LIVE, tested)

    # Saving.

    def test_save_writes_the_persons_config_and_never_lore(self):
        folder = tempfile.mkdtemp()
        path = os.path.join(folder, "config.json")
        with open(path, "w") as f:
            json.dump({"model": "gemma4:12b"}, f)
        lore = {p: os.path.getmtime(os.path.join("lore", p)) for p in os.listdir("lore")}
        with patch("mechanics.setup.ConfigWizard.CONFIG_FILE", path):
            self.tune("/tune WHIMSY LUDICROUS_SPEED true --save")
        saved = json.load(open(path))
        self.assertEqual(saved, {"model": "gemma4:12b", "TUNED": {"WHIMSY.LUDICROUS_SPEED": True}})
        self.assertEqual(lore, {p: os.path.getmtime(os.path.join("lore", p)) for p in os.listdir("lore")})

    def test_a_saved_tuning_is_applied_at_boot(self):
        from main import BoneAmanita

        eng = BoneAmanita({"provider": "mock", "user_name": "T", "boot_mode": "CONVERSATION",
                           "TUNED": {"BIO.DECAY_RATE": 0.05}})
        self.addCleanup(self._shutdown_engine, eng)
        self.assertEqual(eng.config.BIO.DECAY_RATE, 0.05)
        self.assertEqual(eng.tuned["BIO.DECAY_RATE"]["value"], 0.05)
