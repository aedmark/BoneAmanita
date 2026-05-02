"""tests/test_protocols.py"""

from unittest.mock import patch, MagicMock
from tests.base import BoneTestCase

from protocols.bureau import TheBureau
from protocols.zen import ZenGarden
from protocols.grief import GriefProtocol

class ProtocolLifecycleTests(BoneTestCase):

    @patch('core.LoreManifest.get_instance')
    def test_bureau_hydration_and_mercy(self, mock_manifest):
        """
        The Schur Test: Verifies the Bureau hydrates its forms correctly, and proves
        that the Mercy Override successfully waives the tax on a dying system.
        """
        print("\n--- PROTOCOLS 1: Bureau Hydration & Mercy Override ---")

        # 1. Mock the LoreManifest to provide specific, testable strings
        mock_data = {
            "BUREAU_FORMS": ["Test Form 101"],
            "BUREAU_RESPONSES": ["Test Response"],
            "bureau_buzzwords": ["synergy"]
        }

        def bureau_side_effect(cat, section=None):
            if cat == "narrative_data": return mock_data
            if cat == "LEXICON": return mock_data
            if cat == "ux_strings":
                return {
                    "bureau_form_zoning": "Form Zoning Violation",
                    "bureau_ev_voltage": "High Voltage Detected",
                    "bureau_ev_fiction": "Low Truth Ratio"
                }
            return {}

        mock_manifest.return_value.get.side_effect = bureau_side_effect

        # 2. Instantiate and verify hydration (Proving the import-time bug is fixed)
        # We explicitly drop the length limit so our short test string doesn't get silently ignored
        setattr(self.engine.config.BUREAU, "MIN_WORD_COUNT", 0)
        bureau = TheBureau(config_ref=self.engine.config)

        # 3. Simulate a massive infraction (High Voltage, High Chaos)
        toxic_physics = {"voltage": 50.0, "chi": 0.9, "raw_text": "Let's leverage synergy to paradigm shift."}

        # 4. Simulate a dying system (Health < 20.0)
        dying_bio = {"health": 15.0}

        # 5. Audit the system
        result = bureau.audit(toxic_physics, dying_bio, origin="USER")

        # Assert the Mercy Override caught the dying system
        self.assertIsNotNone(result, "[FAIL] Audit aborted entirely instead of returning a waived status.")
        self.assertEqual(result.get("status"), "WAIVED", "[FAIL] Bureau taxed a dying system! Mercy override failed.")
        self.assertEqual(result.get("atp_gain"), 0.0, "[FAIL] System was taxed despite the Mercy override.")
        print("  [SUCCESS] Bureau successfully hydrated and waived the tax via Mercy Override.")


    @patch('core.LoreManifest.get_instance')
    def test_zen_garden_milestones(self, mock_manifest):
        """
        The Fuller Test: Verifies the Zen Garden hydrates its Koans and properly
        accumulates a Stillness Streak, generating pebbles and passive ATP.
        """
        print("\n--- PROTOCOLS 2: Zen Garden Hydration & Milestones ---")

        # Mock narrative data and UI strings dynamically
        def zen_side_effect(cat, section=None):
            if cat == "narrative_data": return {"ZEN_KOANS": ["A mock koan."]}
            if cat == "ux_strings": return {"zen_streak": "Streak {streak}: {koan} (+{boost}%)"}
            return {}
        mock_manifest.return_value.get.side_effect = zen_side_effect

        events_mock = MagicMock()
        zen = ZenGarden(events_ref=events_mock, config_ref=self.engine.config)

        # Assert Hydration
        self.assertIn("A mock koan.", zen.koans, "[FAIL] ZenGarden failed to hydrate Koans on init.")

        # Simulate 5 turns of perfect stillness (Voltage 8.0, Drag 1.0)
        stable_physics = {"voltage": 8.0, "narrative_drag": 1.0}

        # Turns 1 through 4 (Building streak)
        for _ in range(4):
            boost, msg = zen.raking_the_sand(stable_physics, {})
            self.assertGreater(boost, 0.0, "[FAIL] Zen Garden failed to grant passive efficiency boost.")

        # Turn 5 (Milestone Trigger)
        boost, msg = zen.raking_the_sand(stable_physics, {})

        # Assert state and milestone rewards
        self.assertEqual(zen.stillness_streak, 5, "[FAIL] Stillness streak failed to accumulate.")
        self.assertEqual(zen.pebbles_collected, 1, "[FAIL] Zen Garden failed to grant a pebble on Turn 5.")
        self.assertIsNotNone(msg, "[FAIL] Zen Garden failed to output a UI message on milestone.")
        self.assertIn("mock koan", msg, "[FAIL] Zen Garden failed to drop the hydrated Koan in the milestone message.")

        print("  [SUCCESS] Zen Garden successfully accumulated stillness and granted rewards.")


    def test_grief_protocol_wake(self):
        """
        The Pinker Test: Verifies the Grief Protocol successfully heals trauma
        when the user spends a Glimmer to mourn an Autophagy event.
        """
        print("\n--- PROTOCOLS 3: The Grief Protocol Wake ---")

        eng_mock = MagicMock()
        eng_mock.trauma_accum = {"SEPTIC": 5.0} # System has 5.0 trauma

        grief = GriefProtocol(events_ref=MagicMock(), engine_ref=eng_mock)

        # 1. Simulate a memory purge (Autophagy)
        grief._hold_wake({"node": "A beautiful sunset"})
        self.assertEqual(grief.recent_loss, "A beautiful sunset", "[FAIL] Grief Protocol failed to register the lost node.")

        # 2. Simulate the User Lattice (They have 1 Glimmer and 10 User Trauma)
        lattice_mock = MagicMock()
        lattice_mock.shared.g_pool = 1
        lattice_mock.u.T_u = 10.0

        # 3. Attend the Wake
        result_msg = grief.attend_wake(lattice_mock, phys={"G": 0})

        # 4. Assert the healing mechanics
        self.assertEqual(lattice_mock.shared.g_pool, 0, "[FAIL] Glimmer was not deducted from the shared pool.")
        self.assertEqual(lattice_mock.u.T_u, 8.0, "[FAIL] User Trauma (T_u) was not reduced by 2.0.")
        self.assertEqual(eng_mock.trauma_accum["SEPTIC"], 3.0, "[FAIL] Systemic Trauma was not reduced by 2.0.")
        self.assertIsNone(grief.recent_loss, "[FAIL] recent_loss state was not cleared after a successful wake.")
        self.assertIn("A beautiful sunset", result_msg, "[FAIL] Result message failed to mention the lost node.")

        print("  [SUCCESS] Grief Protocol successfully exchanged a Glimmer for trauma reduction.")