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
        self.patcher = patch("engine.core.LoreManifest.get_instance")
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


class TestTinkererPersistence(BoneTestCase):
    """The Tinkerer had no `to_dict` and no `load_state`, and nothing said so.

    `TheCortex.gather_state` called `tinkerer.to_dict()` inside a handler that
    caught AttributeError and substituted `{}`. Three paths died on that one
    missing pair: the composer's HARMONIC RESONANCE block read an empty
    `tool_resonance` and never once rendered, `ChronosKeeper` filters the save
    on `hasattr(comp, "to_dict")` so resonance never persisted, and the restore
    dispatches on `load_state` so it never came back.
    """

    def _tinkerer(self):
        tinkerer = getattr(self.engine.village, "tinkerer", None)
        self.assertIsNotNone(tinkerer, "the village has no tinkerer to test")
        return tinkerer

    def test_resonance_survives_a_round_trip(self):
        tinkerer = self._tinkerer()
        tinkerer.tool_resonance = {"hammer": 6.0, "lens": 2.5}
        payload = tinkerer.to_dict()
        self.assertEqual(payload["tool_resonance"], {"hammer": 6.0, "lens": 2.5})

        tinkerer.tool_resonance = {}
        tinkerer.load_state(payload)
        self.assertEqual(tinkerer.tool_resonance, {"hammer": 6.0, "lens": 2.5})

    def test_load_state_refuses_a_shape_it_cannot_use(self):
        """Silently accepting the wrong shape is how the original bug survived."""
        with self.assertRaises(TypeError):
            self._tinkerer().load_state({"tool_resonance": ["hammer", "lens"]})

    def test_chronos_now_includes_the_tinkerer_in_the_save(self):
        """The save filters on hasattr(comp, "to_dict"), so this was skipped."""
        tinkerer = self._tinkerer()
        tinkerer.tool_resonance = {"hammer": 7.0}
        village_state = self.engine.chronos._gather_village_state()
        self.assertIn("tinkerer", village_state)
        self.assertEqual(
            village_state["tinkerer"]["tool_resonance"], {"hammer": 7.0}
        )

    def test_mastered_tools_reach_the_composed_prompt(self):
        """The end of the path: resonance above level 4 becomes a directive."""
        from brain.composer import PromptComposer

        style_notes = []
        state = {"village": {"tinkerer": {"tool_resonance": {"hammer": 6.0, "twig": 1.0}}}}
        PromptComposer._inject_resonances(style_notes, state, {})
        rendered = "\n".join(style_notes)
        self.assertIn("HARMONIC RESONANCE", rendered)
        self.assertIn("hammer", rendered)
        self.assertNotIn("twig", rendered, "a level 1 tool is not mastery")

    def test_gather_state_carries_resonance_rather_than_an_empty_dict(self):
        tinkerer = self._tinkerer()
        tinkerer.tool_resonance = {"hammer": 6.0}
        state = self.engine.cortex.gather_state({})
        self.assertEqual(
            state["village"]["tinkerer"]["tool_resonance"],
            {"hammer": 6.0},
            "gather_state is handing the composer an empty tinkerer again",
        )
