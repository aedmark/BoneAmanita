"""tests/test_brain.py"""

import unittest
from unittest.mock import MagicMock, patch
from brain.mind import NeurotransmitterModulator, DreamEngine
from brain.akashic import TheAkashicRecord
from spores.memory import SubconsciousStrata
from brain.cortex import TheCortex, CortexServices
from presets import BoneConfig

try:
    from tests.base import BoneTestCase
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from tests.base import BaseTest as BoneTestCase

class BrainSubstrateTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.config = BoneConfig

    def test_modulator_cached_bounds(self):
        bio_mock = MagicMock()
        bio_mock.endo.get_state.return_value = {"DOP": 0.5, "COR": 0.2, "ADR": 0.1, "SER": 0.4}
        mod = NeurotransmitterModulator(bio_ref=bio_mock, config_ref=self.config)
        self.assertTrue(hasattr(mod, 'b'), "[FAIL] Modulator failed to initialize the 'self.b' dictionary cache.")
        self.assertIn("BASE_TOKENS", mod.b, "[FAIL] Cache is missing critical bounds.")
        params = mod.modulate(base_voltage=50.0, physics_state={"chi": 0.5, "contradiction": 0.3})
        self.assertIn("temperature", params)
        self.assertIn("max_tokens", params)
        self.assertIsInstance(params["max_tokens"], int)

    def test_akashic_native_dict_handling(self):
        akashic = TheAkashicRecord(lore_manifest=MagicMock(), config_ref=self.config)
        raw_physics = {"exhaustion": 0.8, "beta_index": 0.9, "energy": {"voltage": 100.0}}
        try:
            akashic.record_scar("System Overload", raw_physics)
        except AttributeError as e:
            self.fail(f"[CRITICAL] Akashic Record crashed during native dictionary extraction: {e}")
        self.assertEqual(akashic.scar_map[-1]["concept"], "System Overload")
        self.assertEqual(akashic.scar_map[-1]["coordinates"]["E"], 0.8)

    def test_cortex_dictionary_coercion(self):
        services = CortexServices(events=MagicMock(), lore=MagicMock(), lexicon=MagicMock(), inventory=MagicMock(), consultant=MagicMock(), orchestrator=MagicMock(),
            symbiosis=MagicMock(), mind_memory=MagicMock(), bio=MagicMock(),  config_ref=self.config)
        cortex = TheCortex(services)
        sim_result = {"physics": {"voltage": 75.0, "narrative_drag": 5.0, "chi": 0.8}, "bio": {}}
        try:
            state = cortex.gather_state(sim_result)
        except Exception as e:
            self.fail(f"[CRITICAL] Cortex gather_state failed to parse the native dictionary: {e}")
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
            config_ref=self.config
        )
        soul_snapshot = {"obsession": {"title": "The Abyss"}}
        bio_state = {"chem": {"cortisol": 0.2, "dopamine": 0.1}}
        dream_text, shift = engine._generate_narrative_dream(soul_snapshot, bio_state["chem"], bio_state["chem"]["cortisol"])
        self.assertIn("The void stares back", dream_text, "[FAIL] Dream engine failed to generate the fallback narrative.")
        self.assertTrue(strict_subconscious.bury.called, "[FAIL] The engine failed to call the correct .bury() method.")

    @patch('random.random', return_value=0.1)
    def test_dream_engine_terminal_sleep_failure(self, mock_random):
        engine = DreamEngine(
            events=MagicMock(),
            lore_ref={"DREAMS": {"NIGHTMARES": ["Terminal cold."]}},
            mem_ref=MagicMock(),
            config_ref=self.config
        )
        engine._weaver = MagicMock()
        engine._weaver.deform_reality.return_value = "glitch"
        bio_state = {"mito": {"atp": 2.0}, "chem": {"cortisol": 0.8}}
        dream_text, shift = engine.enter_rem_cycle({}, bio_state)
        self.assertIn("Apoptotic cascade", dream_text, "[FAIL] Engine failed to trigger terminal death on starved REM.")
        self.assertEqual(shift.get("voltage"), 100.0, "[FAIL] Terminal sleep did not instantly spike the voltage.")

if __name__ == '__main__':
    unittest.main()