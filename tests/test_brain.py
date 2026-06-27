"""tests/test_brain.py"""

import unittest
from unittest.mock import MagicMock, patch

from brain.akashic import TheAkashicRecord
from brain.cortex import CortexServices, TheCortex
from brain.mind import DreamEngine, NeurotransmitterModulator
from presets import BoneConfig
from spores.memory import SubconsciousStrata

try:
    from tests.base import BoneTestCase
except ImportError:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tests.base import BaseTest as BoneTestCase


class BrainSubstrateTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig

    def test_modulator_cached_bounds(self):
        bio_mock = MagicMock()
        bio_mock.endo.get_state.return_value = {
            "DOP": 0.5,
            "COR": 0.2,
            "ADR": 0.1,
            "SER": 0.4,
        }
        mod = NeurotransmitterModulator(bio_ref=bio_mock, config_ref=self.config)
        self.assertTrue(
            hasattr(mod, "b"),
            "[FAIL] Modulator failed to initialize the 'self.b' dictionary cache.",
        )
        self.assertIn("BASE_TOKENS", mod.b, "[FAIL] Cache is missing critical bounds.")
        params = mod.modulate(
            base_voltage=50.0, physics_state={"chi": 0.5, "contradiction": 0.3}
        )
        self.assertIn("temperature", params)
        self.assertIn("max_tokens", params)
        self.assertIsInstance(params["max_tokens"], int)

    def test_akashic_native_dict_handling(self):
        akashic = TheAkashicRecord(lore_manifest=MagicMock(), config_ref=self.config)
        raw_physics = {
            "exhaustion": 0.8,
            "beta_index": 0.9,
            "energy": {"voltage": 100.0},
        }
        try:
            akashic.record_scar("System Overload", raw_physics)
        except AttributeError as e:
            self.fail(
                f"[CRITICAL] Akashic Record crashed during native dictionary extraction: {e}"
            )
        self.assertEqual(akashic.scar_map[-1]["concept"], "System Overload")
        self.assertEqual(akashic.scar_map[-1]["coordinates"]["E"], 0.8)

    def test_cortex_dictionary_coercion(self):
        services = CortexServices(
            events=MagicMock(),
            lore=MagicMock(),
            lexicon=MagicMock(),
            inventory=MagicMock(),
            consultant=MagicMock(),
            orchestrator=MagicMock(),
            symbiosis=MagicMock(),
            mind_memory=MagicMock(),
            bio=MagicMock(),
            config_ref=self.config,
        )
        cortex = TheCortex(services)
        sim_result = {
            "physics": {"voltage": 75.0, "narrative_drag": 5.0, "chi": 0.8},
            "bio": {},
        }
        try:
            state = cortex.gather_state(sim_result)
        except Exception as e:
            self.fail(
                f"[CRITICAL] Cortex gather_state failed to parse the native dictionary: {e}"
            )
        self.assertEqual(state["physics"]["voltage"], 75.0)

    def test_dream_engine_strict_mock_subconscious(self):
        strict_subconscious = MagicMock(spec=SubconsciousStrata)
        strict_mem = MagicMock()
        strict_mem.subconscious = strict_subconscious
        mock_lore = {"DREAMS": {"SURREAL": ["The void stares back at {ghost}."]}}
        engine = DreamEngine(
            events=MagicMock(),
            lore_ref=mock_lore,
            mem_ref=strict_mem,
            eng_ref=MagicMock(),
            config_ref=self.config,
        )
        soul_snapshot = {"obsession": {"title": "The Abyss"}}
        bio_state = {"chem": {"cortisol": 0.2, "dopamine": 0.1}}
        dream_text, shift = engine._generate_narrative_dream(
            soul_snapshot, bio_state["chem"], bio_state["chem"]["cortisol"]
        )
        self.assertIn(
            "The void stares back",
            dream_text,
            "[FAIL] Dream engine failed to generate the fallback narrative.",
        )
        self.assertTrue(
            strict_subconscious.bury.called,
            "[FAIL] The engine failed to call the correct .bury() method.",
        )

    @patch("random.random", return_value=0.1)
    def test_dream_engine_terminal_sleep_failure(self, mock_random):
        engine = DreamEngine(
            events=MagicMock(),
            lore_ref={"DREAMS": {"NIGHTMARES": ["Terminal cold."]}},
            mem_ref=MagicMock(),
            config_ref=self.config,
        )
        engine._weaver = MagicMock()
        engine._weaver.deform_reality.return_value = "glitch"
        bio_state = {"mito": {"atp": 2.0}, "chem": {"cortisol": 0.8}}
        dream_text, shift = engine.enter_rem_cycle({}, bio_state)
        self.assertIn(
            "Apoptotic cascade",
            dream_text,
            "[FAIL] Engine failed to trigger terminal death on starved REM.",
        )
        self.assertEqual(shift.get("voltage"), 100.0, "[FAIL] Terminal sleep did not instantly spike the voltage.")

        @patch("brain.mind.DreamEngine._weave_dream")
        def test_dream_engine_oneroi_diamond_forge(self, mock_weave):
            """Tests Project Oneroi's diamond forging and massive ATP surge during REM."""
            mock_weave.return_value = "Surreal geometry unfolds."
            strict_mem = MagicMock()
            strict_mem.cortical_stack = ["anchor_concept"]
            strict_mem.subconscious.dredge_vibe_by_vector.return_value = [{"word": "ancient_fossil", "score": 0.95}]
            strict_mem.forge_diamond.return_value = True
            mock_eng = MagicMock()
            mock_eng.bio.mito.state.ros_buildup = 100.0
            engine = DreamEngine(
                events=MagicMock(), lore_ref={}, mem_ref=strict_mem, eng_ref=mock_eng, config_ref=self.config
            )
            engine._w2v = MagicMock(return_value=[0.5, 0.5])
            dream_text, shift = engine._generate_narrative_dream({}, {}, cortisol=0.2)
            self.assertTrue(shift.get("diamond_forged"), "[FAIL] Shift payload missing diamond flag.")
            self.assertEqual(shift.get("fossil_word"), "ancient_fossil")
            self.assertIn("The architecture stabilizes", dream_text)
            self.assertIn("Surreal geometry unfolds.", dream_text)
            mock_eng.bio.mito.adjust_atp.assert_called_with(500.0, "Diamond Crystallization")
            self.assertEqual(
                mock_eng.bio.mito.state.ros_buildup, 50.0, "[FAIL] ROS toxicity was not purged by the forge."
            )

    def test_hippocampal_stress_blindness(self):
        """Ensures HippocampalCache violently amputates memories when cortisol spikes."""
        from brain.ann import HippocampalCache

        cache = HippocampalCache(max_capacity=10)
        for i in range(10):
            cache.encode(f"node_{i}", [0.1] * 8, {"data": i})
        self.assertEqual(
            len(cache.nodes), 10, "[FAIL] Cache failed to fill to base capacity."
        )
        cache.apply_stress_blindness(cortisol=0.9)
        self.assertEqual(
            len(cache.nodes),
            1,
            "[FAIL] HippocampalCache failed to amputate nodes under high cortisol.",
        )
        self.assertEqual(
            cache.current_capacity, 1, "[FAIL] Cache capacity float math failed."
        )

    def test_cerebral_tunnel_vision(self):
        """Ensures FAISS K-limit is clamped and positive dimensions are blocked under stress."""
        from brain.ann import CerebralIndex

        idx = CerebralIndex(dimension=2)
        vectors = [[0.1, 0.1], [0.1, 0.1], [0.1, 0.1]]
        payloads = [
            {"id": "trauma", "dimensions": ["heavy", "void"]},
            {"id": "playful", "dimensions": ["social", "play"]},
            {"id": "neutral", "dimensions": ["standard"]},
        ]
        idx.add_memories(vectors, payloads)
        res_normal = idx.query_neighborhood(
            [0.1, 0.1], k=3, physics_state={"cortisol": 0.1}
        )
        self.assertEqual(
            len(res_normal),
            3,
            "[FAIL] FAISS failed to return all nodes under low cortisol.",
        )
        res_stress = idx.query_neighborhood([0.1, 0.1], k=3, physics_state={"cortisol": 0.9})
        ids = [r["id"] for r in res_stress]
        self.assertNotIn("playful", ids, "[FAIL] Cortisol failed to block positive dimensions (Tunnel Vision failed).")
        self.assertLess(len(res_stress), 3, "[FAIL] Cortisol failed to clamp the FAISS K limit.")

    def test_heuristic_audit_exhaustion_limits(self):
        """Tests that the S.L.A.S.H. Heuristic Guillotine enforces boundaries on an exhausted user."""
        services = CortexServices(
            events=MagicMock(),
            lore=MagicMock(),
            lexicon=MagicMock(),
            inventory=MagicMock(),
            consultant=MagicMock(),
            orchestrator=MagicMock(),
            symbiosis=MagicMock(),
            mind_memory=MagicMock(),
            bio=MagicMock(),
            config_ref=self.config,
        )
        cortex = TheCortex(services=services)

        long_text = "word " * 105
        is_faithful, reason = cortex._run_heuristic_audit("Hello", long_text, e_u=0.85, beta=0.0)
        self.assertFalse(
            is_faithful, "[FAIL] Heuristic audit failed to block overly verbose response under high exhaustion."
        )
        self.assertIn("verbose", reason.lower())

        q_text = "Are you sure about that?"
        is_faithful, reason = cortex._run_heuristic_audit("Hello", q_text, e_u=0.85, beta=0.0)
        self.assertFalse(is_faithful, "[FAIL] Heuristic audit failed to block interrogating an exhausted user.")
        self.assertIn("question", reason.lower())

        heavy_text = "word " * 155
        is_faithful, reason = cortex._run_heuristic_audit("Hello", heavy_text, e_u=0.0, beta=0.85)
        self.assertFalse(is_faithful, "[FAIL] Heuristic audit failed to block heavy response under high tension.")

        good_text = "I am here with you. We will rest."
        is_faithful, reason = cortex._run_heuristic_audit("Hello", good_text, e_u=0.85, beta=0.85)
        self.assertTrue(is_faithful, "[FAIL] Heuristic audit falsely blocked a safe, short, declarative response.")


    if __name__ == "__main__":
        unittest.main()
