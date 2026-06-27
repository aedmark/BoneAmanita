"""tests/test_genesis_continuity.py"""

import json
import os
from unittest.mock import MagicMock, patch

from soul.oroboros import Scar, TheOroboros
from tests.base import BoneTestCase


class GenesisContinuityTests(BoneTestCase):
    def setUp(self):
        super().setUp()
        self.test_legacy_file = "test_legacy_temp.json"
        self.patcher = patch(
            "soul.oroboros.TheOroboros.LEGACY_FILE", self.test_legacy_file
        )
        self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()
        if os.path.exists(self.test_legacy_file):
            os.remove(self.test_legacy_file)

    def test_crystallize_existential_dread(self):
        oro = TheOroboros(config_ref=self.test_config)
        mock_soul = MagicMock()
        mock_soul.eng.trauma_accum = {"THERMAL": 8.0, "SEPTIC": 5.0}
        mock_soul.core_memories = []
        with patch("core.LoreManifest.get", return_value={}):
            oro.crystallize("STARVATION", mock_soul)
        dread_scar = next((s for s in oro.scars if s.name == "Existential Dread"), None)
        self.assertIsNotNone(
            dread_scar,
            "[FAIL] Oroboros failed to translate > 10.0 trauma into Existential Dread.",
        )
        self.assertEqual(dread_scar.stat_affected, "trauma_baseline")
        self.assertGreater(dread_scar.value, 0.0)
        self.assertTrue(
            os.path.exists(self.test_legacy_file),
            "[FAIL] legacy.json was not written to disk.",
        )

    def test_apply_legacy_karma(self):
        oro = TheOroboros(config_ref=self.test_config)
        oro.scars = [
            Scar("Heavy Burden", "narrative_drag", 3.0, "Drag increase."),
            Scar("Exhaustion", "voltage_cap", 5.0, "Voltage penalty."),
        ]
        fresh_physics = {"voltage": 20.0, "narrative_drag": 1.0}
        fresh_bio = {"trauma_vector": {}}
        oro.apply_legacy(fresh_physics, fresh_bio)
        self.assertEqual(
            fresh_physics["narrative_drag"],
            4.0,
            "[FAIL] Generational narrative drag was not applied to the new physics state.",
        )
        self.assertEqual(
            fresh_physics["voltage"],
            15.0,
            "[FAIL] Starting voltage was not penalized! The karma engine failed to enforce exhaustion.",
        )

    def test_apply_legacy_empty_state(self):
        oro = TheOroboros(config_ref=self.test_config)
        oro.scars = []
        fresh_physics = {}
        logs = oro.apply_legacy(fresh_physics, {})
        self.assertEqual(
            len(logs),
            0,
            "[FAIL] Oroboros generated logs for an empty legacy application.",
        )
        self.assertEqual(
            fresh_physics,
            {},
            "[FAIL] Oroboros mutated an empty physics packet unexpectedly.",
        )
