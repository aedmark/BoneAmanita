"""tests/test_genesis_continuity.py"""

import os
import json
from unittest.mock import MagicMock, patch
from tests.base import BoneTestCase
from soul.oroboros import TheOroboros, Scar

class GenesisContinuityTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        # Isolate the legacy file so we don't corrupt real session data
        self.test_legacy_file = "test_legacy_temp.json"
        self.patcher = patch("soul.oroboros.TheOroboros.LEGACY_FILE", self.test_legacy_file)
        self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()
        # Clean up the timeline
        if os.path.exists(self.test_legacy_file):
            os.remove(self.test_legacy_file)

    def test_crystallize_existential_dread(self):
        """
        The Meadows Test: Ensures fatal systemic trauma bridges the generational gap.
        If the organism dies highly traumatized, the next iteration must carry the scar.
        """
        print("\n--- GENESIS 1: Trauma Crystallization ---")
        oro = TheOroboros(config_ref=self.test_config)

        # Mock a soul that died with massive systemic trauma
        mock_soul = MagicMock()
        mock_soul.eng.trauma_accum = {"THERMAL": 8.0, "SEPTIC": 5.0} # Total 13.0 (> 10.0 threshold)
        mock_soul.core_memories = []

        # Simulate Death
        with patch("core.LoreManifest.get", return_value={}):
            oro.crystallize("STARVATION", mock_soul)

        # Validate the scar was forged
        dread_scar = next((s for s in oro.scars if s.name == "Existential Dread"), None)
        self.assertIsNotNone(dread_scar, "[FAIL] Oroboros failed to translate > 10.0 trauma into Existential Dread.")
        self.assertEqual(dread_scar.stat_affected, "trauma_baseline")
        self.assertGreater(dread_scar.value, 0.0)

        # Validate disk persistence (ensuring it survives the reboot)
        self.assertTrue(os.path.exists(self.test_legacy_file), "[FAIL] legacy.json was not written to disk.")
        print("  [SUCCESS] Fatal trauma successfully crystallized into a generational scar.")

    def test_apply_legacy_karma(self):
        """
        The Schur Test: Verifies that legacy scars actually apply systemic friction
        and voltage penalties. This tests the logic exposed by the nested walrus bug.
        """
        print("\n--- GENESIS 2: Legacy Karma Application ---")
        oro = TheOroboros(config_ref=self.test_config)

        # Manually inject scars simulating a chaotic previous generation
        oro.scars = [
            Scar("Heavy Burden", "narrative_drag", 3.0, "Drag increase."),
            Scar("Exhaustion", "voltage_cap", 5.0, "Voltage penalty.")
        ]

        # The baseline stats of a fresh Embryo
        fresh_physics = {"voltage": 20.0, "narrative_drag": 1.0}
        fresh_bio = {"trauma_vector": {}}

        # Apply the karma
        oro.apply_legacy(fresh_physics, fresh_bio)

        # Assert Drag increased
        self.assertEqual(fresh_physics["narrative_drag"], 4.0,
                         "[FAIL] Generational narrative drag was not applied to the new physics state.")

        # Assert Voltage decreased (This proves the walrus bug is fixed)
        self.assertEqual(fresh_physics["voltage"], 15.0,
                         "[FAIL] Starting voltage was not penalized! The karma engine failed to enforce exhaustion.")

        print("  [SUCCESS] Scars successfully altered the physics of the new generation.")

    def test_apply_legacy_empty_state(self):
        """
        The Fuller Test: Ensures the engine doesn't crash if the previous generation
        left no scars, or if the physics packet is completely empty.
        """
        print("\n--- GENESIS 3: Void State Continuity ---")
        oro = TheOroboros(config_ref=self.test_config)
        oro.scars = [] # Clean slate

        fresh_physics = {}
        logs = oro.apply_legacy(fresh_physics, {})

        self.assertEqual(len(logs), 0, "[FAIL] Oroboros generated logs for an empty legacy application.")
        self.assertEqual(fresh_physics, {}, "[FAIL] Oroboros mutated an empty physics packet unexpectedly.")
        print("  [SUCCESS] Oroboros handled a clean slate with zero systemic friction.")