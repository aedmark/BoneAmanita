"""tests/test_drivers.py"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from drivers.consultant import BoneConsultant
from drivers.enneagram import EnneagramDriver
from drivers.liminal import LiminalModule
from drivers.syntax import SyntaxModule
from drivers.userprofile import UserProfile
from drivers.validator import CongruenceValidator
from tests.base import BoneTestCase


class TestDrivers(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.chaotic_config = {
            "DRIVERS": {
                "VSL_E_GROWTH_MULT": "0.1",
                "VSL_FATIGUE_MULT": "0.5",
                "VSL_LIMINAL_THRESHOLD": "0.5",
                "ENNEAGRAM_HYSTERESIS": "2",
                "PROFILE_MIN_WORDS": "2",
                "PROFILE_ALPHA_HIGH": "0.5",
                "LIMINAL_LEXICAL_WEIGHT": "0.5",
                "SYNTAX_STRESS_PUNCTUATION": "0.1",
                "SYNTAX_STRESS_INCREASE": "0.3",
            },
            "SANCTUARY": {"ZONE": "SAFE_ROOM"},
        }
        self.mock_manifest_data = {
            "DRIVER_CONFIG": {
                "ENNEAGRAM_WEIGHTS": {
                    "NARRATOR": {"tension_min": 0.0},
                    "THE MANIC": {"tension_min": "10.0", "coherence_max": "0.5"},
                    "THE MACHINE": {"coherence_min": "0.8", "vectors": {"ENT": "2.0"}},
                },
                "PERSONA_STATE_MAP": {"NARRATOR": "ACTIVE", "THE MANIC": "UNSTABLE"},
            },
            "LENSES": {"OBSERVER": {"vocab": "watch,see", "keywords": ["witness"]}},
        }
        self.patcher = patch("core.LoreManifest.get_instance")
        self.mock_manifest = self.patcher.start()
        self.mock_manifest.return_value.get.side_effect = lambda *args: (
            self.mock_manifest_data.get(args[0], {})
        )
        self.mock_lexicon = MagicMock()
        self.mock_lexicon.get.return_value = {"void", "abyss", "bureaucracy"}
        self.mock_lexicon.get_categories_for_word.side_effect = lambda w: (
            ["heavy"] if w == "iron" else ["void"] if w == "abyss" else []
        )

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def test_consultant_type_coercion_and_growth(self):
        consultant = BoneConsultant(
            config_ref=self.chaotic_config, lexicon_ref=self.mock_lexicon
        )
        loose_physics = {"beta_index": "0.8", "narrative_drag": "2.0"}
        consultant.update_coordinates(
            "Just a few words.", bio_state={"fatigue": 0.5}, physics=loose_physics
        )
        self.assertTrue(
            isinstance(consultant.state.E, float),
            "[FAIL] State E failed to cast to float.",
        )
        self.assertTrue(
            isinstance(consultant.state.B, float),
            "[FAIL] State B failed to cast to float.",
        )
        self.assertGreater(
            consultant.state.E, 0.1, "[FAIL] E growth multiplier failed to execute."
        )

    def test_consultant_system_prompt_routing(self):
        consultant = BoneConsultant(
            config_ref=self.chaotic_config, lexicon_ref=self.mock_lexicon
        )
        consultant.state.active_modules.append("LIMINAL")
        prompt = consultant.get_system_prompt()
        self.assertIn(
            "Embrace the void.",
            prompt,
            "[FAIL] Consultant failed to route to Liminal directive.",
        )

    def test_enneagram_raw_persona_loose_physics(self):
        enneagram = EnneagramDriver(
            events_ref=MagicMock(), config_ref=self.chaotic_config
        )
        chaotic_physics = {
            "voltage": "15.0",
            "narrative_drag": "5.0",
            "kappa": "0.2",
            "vector": {"ENT": "0.9"},
        }
        persona, state, reason = enneagram._calculate_raw_persona(chaotic_physics)
        self.assertIsNotNone(
            persona,
            "[FAIL] Enneagram crashed while attempting to coerce dictionary physics.",
        )
        self.assertIn(
            "THE MANIC",
            persona,
            "[FAIL] Persona failed to evaluate high-tension string bounds.",
        )

    def test_enneagram_hysteresis_lock(self):
        enneagram = EnneagramDriver(
            events_ref=MagicMock(), config_ref=self.chaotic_config
        )
        shifting_physics = {"voltage": 15.0, "narrative_drag": 5.0, "kappa": 0.2}
        p1, _, _ = enneagram.decide_persona(shifting_physics)
        self.assertEqual(
            p1, "NARRATOR", "[FAIL] Enneagram shifted immediately, ignoring hysteresis."
        )
        p2, _, _ = enneagram.decide_persona(shifting_physics)
        self.assertNotEqual(
            p2,
            "NARRATOR",
            "[FAIL] Enneagram failed to shift after surpassing hysteresis threshold.",
        )

    def test_liminal_dark_matter_sparks(self):
        liminal = LiminalModule(
            config_ref=self.chaotic_config, lexicon_ref=self.mock_lexicon
        )
        text = "iron abyss iron abyss"
        loose_vector = {"PSI": "0.8", "ENT": "0.5"}
        score = liminal.analyze(text, loose_vector)
        self.assertTrue(
            isinstance(score, float),
            "[FAIL] Liminal analysis failed to return a float.",
        )
        self.assertGreater(
            score,
            0.1,
            "[FAIL] Failed to calculate dark matter lambda from alternating lexical categories.",
        )

    def test_syntax_stress_induction(self):
        syntax = SyntaxModule(
            config_ref=self.chaotic_config, lexicon_ref=self.mock_lexicon
        )
        stressful_text = "Wait, what? No; this cannot be... right?!"
        omega = syntax.analyze(stressful_text, narrative_drag=5.0)
        self.assertTrue(
            isinstance(omega, float), "[FAIL] Syntax analysis failed to return a float."
        )
        self.assertGreater(
            syntax.grammatical_stress,
            0.0,
            "[FAIL] Syntax module failed to induce grammatical stress.",
        )

    def test_user_profile_affinity_shift(self):
        profile = UserProfile(config_ref=self.chaotic_config)
        self.assertEqual(profile.affinities["heavy"], 0.0)
        counts = {"heavy": 10, "kinetic": 0}
        profile.update(counts, total_words=10)
        self.assertGreater(
            profile.affinities["heavy"],
            0.0,
            "[FAIL] Profile failed to apply high-alpha affinity shift.",
        )

        def test_validator_loose_context(self):
            validator = CongruenceValidator(config_ref=self.chaotic_config)
            loose_context = SimpleNamespace(
                active_lens="THE OBSERVER", clean_words=["watch", "witness", "void"]
            )
            resonance = validator.calculate_resonance(
                "I watch the void.", loose_context
            )
            self.assertTrue(
                isinstance(resonance, float),
                "[FAIL] Validator crashed evaluating loosely typed context.",
            )
            self.assertGreater(
                resonance, 0.0, "[FAIL] Validator failed to match vocab/keywords."
            )

        def test_validator_vocab_caching(self):
            validator = CongruenceValidator(config_ref=self.chaotic_config)
            loose_context = SimpleNamespace(
                active_lens="THE OBSERVER", clean_words=["watch", "witness", "void"]
            )
            self.assertNotIn("OBSERVER", validator._compiled_vocab)
            validator.calculate_resonance("I watch the void.", loose_context)
            self.assertIn(
                "OBSERVER",
                validator._compiled_vocab,
                "[FAIL] Validator failed to compile and cache the vocabulary set.",
            )
            self.assertIn(
                "witness",
                validator._compiled_vocab["OBSERVER"],
                "[FAIL] Compiled cache is missing keywords.",
            )
            validator.map["OBSERVER"] = {}
            resonance = validator.calculate_resonance(
                "I watch the void.", loose_context
            )
            self.assertGreater(
                resonance,
                0.8,
                "[FAIL] Validator recalculated from map instead of utilizing the compiled cache.",
            )

    if __name__ == "__main__":
        unittest.main()
