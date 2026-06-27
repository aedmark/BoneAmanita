"""tests/test_archetypes.py"""

import unittest
from unittest.mock import MagicMock, patch

from archetypes.council import TheVillageCouncil
from archetypes.symbiosis import SymbiosisManager
from archetypes.village import DeathGen, TheTherapist, TownHall
from tests.base import BoneTestCase


class TestArchetypes(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.chaotic_config = {
            "VILLAGE": {
                "TOWN_NEGLECT_CRIT": "8.0",
                "TOWN_TRAUMA_CRIT": "0.6",
                "TOWN_HEALTH_CRIT": "30.0",
                "DEATH_TRAUMA_CRIT": "50.0",
                "DEATH_TOXICITY_CRIT": "5.0",
                "THERAPY_TRAUMA_THRESH": "15.0",
                "THERAPY_HEALTH_THRESH": "50.0",
            },
            "BIO": {"ATP_STARVATION": "0.0"},
            "PHYSICS": {"VOLTAGE_CRITICAL": "100.0", "DRAG_HALT": "10.0"},
        }
        self.patcher = patch("core.LoreManifest.get_instance")
        self.mock_manifest = self.patcher.start()
        self.mock_manifest.return_value.get.side_effect = lambda *args: {}

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def test_townhall_string_trauma_vector(self):
        session_data = {
            "trauma_vector": {"papercut": "9.0", "decapitation": "10.0"},
            "meta": {"final_health": "25.0"},
        }
        status, msg = TownHall.diagnose_condition(
            session_data, config_ref=self.chaotic_config
        )
        self.assertEqual(
            status,
            "HIGH_TRAUMA",
            "[FAIL] TownHall failed to diagnose trauma from string data.",
        )
        self.assertIn(
            "decapitation",
            msg,
            "[FAIL] TownHall incorrectly sorted strings lexicographically instead of numerically.",
        )

    def test_deathgen_string_math_coercion(self):
        string_trauma = {"A": "30.0", "B": "25.0"}
        dummy_mito = {"atp": 100}
        cause = DeathGen._determine_cause(
            {}, dummy_mito, string_trauma, config_ref=self.chaotic_config
        )
        self.assertEqual(
            cause,
            "TRAUMA",
            "[FAIL] DeathGen crashed or failed to sum string trauma vector.",
        )
        toxic_physics = {
            "counts": {"antigen": "10.0"},
            "voltage": "0.0",
            "narrative_drag": "0.0",
        }
        cause_tox = DeathGen._determine_cause(
            toxic_physics, dummy_mito, None, config_ref=self.chaotic_config
        )
        self.assertEqual(
            cause_tox,
            "TOXICITY",
            "[FAIL] DeathGen failed to evaluate string antigen counts.",
        )

    def test_therapist_string_math_coercion(self):
        therapist = TheTherapist(events_ref=MagicMock(), config_ref=self.chaotic_config)
        string_trauma = {"A": "10.0", "B": "10.0"}
        triggered, msg = therapist.evaluate_catharsis(string_trauma, health=20.0)
        self.assertTrue(
            triggered,
            "[FAIL] Therapist failed to trigger catharsis with string trauma vectors.",
        )

    def test_council_audit_string_physics(self):
        from archetypes.council import TheOverseerCouncil

        overseer = TheOverseerCouncil(engine_ref=MagicMock())
        loose_physics = {
            "voltage": "110.0",
            "narrative_drag": "0.0",
            "stamina": "100.0",
            "i_c": "0.1",
        }
        triggered, logs, corrections, mandates = overseer.audit(
            "[OVERSEER] [PANIC]", loose_physics
        )
        self.assertTrue(
            triggered, "[FAIL] Overseer failed to parse string physics dictionary."
        )
        self.assertTrue(
            any("TIPP" in m.get("action", "") for m in mandates),
            "[FAIL] Overseer failed to issue TIPP mandate for critical string voltage.",
        )

    def test_symbiosis_somatic_mods(self):
        symbiosis = SymbiosisManager(
            events_ref=MagicMock(), config_ref=self.chaotic_config
        )
        string_phys = {"voltage": "25.0", "narrative_drag": "6.0", "chi": "0.8"}
        mods = symbiosis.get_prompt_modifiers(string_phys)
        self.assertIn(
            "system_directives",
            mods,
            "[FAIL] Symbiosis failed to generate directives from string physics.",
        )
        self.assertTrue(
            isinstance(mods["system_directives"], list),
            "[FAIL] Symbiosis returned a malformed directives list.",
        )


if __name__ == "__main__":
    unittest.main()
