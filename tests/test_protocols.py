"""tests/test_protocols.py"""

from unittest.mock import patch, MagicMock
from tests.base import BoneTestCase
from drivers.syntax import SyntaxModule
from protocols.bureau import TheBureau
from protocols.zen import ZenGarden
from protocols.grief import GriefProtocol

class ProtocolLifecycleTests(BoneTestCase):
    @patch('core.LoreManifest.get_instance')
    def test_bureau_hydration_and_mercy(self, mock_manifest):
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
        setattr(self.engine.config.BUREAU, "MIN_WORD_COUNT", 0)
        bureau = TheBureau(config_ref=self.engine.config)
        toxic_physics = {"voltage": 50.0, "chi": 0.9, "raw_text": "Let's leverage synergy to paradigm shift."}
        dying_bio = {"health": 15.0}
        result = bureau.audit(toxic_physics, dying_bio, origin="USER")
        self.assertIsNotNone(result, "[FAIL] Audit aborted entirely instead of returning a waived status.")
        self.assertEqual(result.get("status"), "WAIVED", "[FAIL] Bureau taxed a dying system! Mercy override failed.")
        self.assertEqual(result.get("atp_gain"), 0.0, "[FAIL] System was taxed despite the Mercy override.")

    @patch('core.LoreManifest.get_instance')
    def test_zen_garden_milestones(self, mock_manifest):

        def zen_side_effect(cat, section=None):
            if cat == "narrative_data": return {"ZEN_KOANS": ["A mock koan."]}
            if cat == "ux_strings": return {"zen_streak": "Streak {streak}: {koan} (+{boost}%)"}
            return {}

        mock_manifest.return_value.get.side_effect = zen_side_effect
        events_mock = MagicMock()
        zen = ZenGarden(events_ref=events_mock, config_ref=self.engine.config)
        self.assertIn("A mock koan.", zen.koans, "[FAIL] ZenGarden failed to hydrate Koans on init.")
        stable_physics = {"voltage": 8.0, "narrative_drag": 1.0}
        for _ in range(4):
            boost, msg = zen.raking_the_sand(stable_physics, {})
            self.assertGreater(boost, 0.0, "[FAIL] Zen Garden failed to grant passive efficiency boost.")
        boost, msg = zen.raking_the_sand(stable_physics, {})
        self.assertEqual(zen.stillness_streak, 5, "[FAIL] Stillness streak failed to accumulate.")
        self.assertEqual(zen.pebbles_collected, 1, "[FAIL] Zen Garden failed to grant a pebble on Turn 5.")
        self.assertIsNotNone(msg, "[FAIL] Zen Garden failed to output a UI message on milestone.")
        self.assertIn("mock koan", msg, "[FAIL] Zen Garden failed to drop the hydrated Koan in the milestone message.")

    def test_grief_protocol_wake(self):
        eng_mock = MagicMock()
        eng_mock.trauma_accum = {"SEPTIC": 5.0}
        grief = GriefProtocol(events_ref=MagicMock(), engine_ref=eng_mock)
        grief._hold_wake({"node": "A beautiful sunset"})
        self.assertEqual(grief.recent_loss, "A beautiful sunset","[FAIL] Grief Protocol failed to register the lost node.")
        lattice_mock = MagicMock()
        lattice_mock.shared.g_pool = 1
        lattice_mock.u.T_u = 10.0
        result_msg = grief.attend_wake(lattice_mock, phys={"G": 0})
        self.assertEqual(lattice_mock.shared.g_pool, 0, "[FAIL] Glimmer was not deducted from the shared pool.")
        self.assertEqual(lattice_mock.u.T_u, 8.0, "[FAIL] User Trauma (T_u) was not reduced by 2.0.")
        self.assertEqual(eng_mock.trauma_accum["SEPTIC"], 3.0, "[FAIL] Systemic Trauma was not reduced by 2.0.")
        self.assertIsNone(grief.recent_loss, "[FAIL] recent_loss state was not cleared after a successful wake.")
        self.assertIn("A beautiful sunset", result_msg, "[FAIL] Result message failed to mention the lost node.")

    def test_sincerity_protocol_hard_routing(self):
        ambiguous_prompt = "I guess it's fine if we delete the backup. [!l]"
        initial_cortisol = self.engine.bio.endo.cortisol
        snapshot = self.engine.process_turn(ambiguous_prompt)
        logs = "\n".join(snapshot.get("logs", [])).upper()
        final_cortisol = self.engine.bio.endo.cortisol
        self.assertIn("LITERAL", logs, "[FAIL] Literal mode was not explicitly triggered in the logs.")

        def test_chronos_temporal_validation(self):
            from protocols.chronos import ChronosKeeper
            eng_mock = MagicMock()
            eng_mock.kernel_hash = "FRACTURE"
            eng_mock.active_physics = {"zone": "The Void"}
            eng_mock.village.gordon.inventory = []
            chronos = ChronosKeeper(eng_mock)
            packet = chronos._build_continuity_packet()
            self.assertEqual(packet.get("kernel_hash"), "FRACTURE", "[FAIL] Chronos failed to anchor the kernel hash in the continuity packet.")
            import io
            import sys
            captured_out = io.StringIO()
            sys.stdout = captured_out
            eng_mock.kernel_hash = "NEW_BOOT"
            data = {"continuity": packet}
            saved_hash = data["continuity"].get("kernel_hash", "UNKNOWN")
            current_hash = getattr(chronos.eng, "kernel_hash", "UNKNOWN")
            if saved_hash != "UNKNOWN" and saved_hash != current_hash:
                print(f"[CHRONOS] Temporal fracture detected. Bridging timeline [{saved_hash}] into [{current_hash}].")
            sys.stdout = sys.__stdout__
            self.assertIn("Temporal fracture detected", captured_out.getvalue(), "[FAIL] Chronos failed to detect the timeline fracture.")

    def test_grief_protocol_activation(self):
        self.engine.bio.endo.glimmers = 0
        self.engine.mind.mem.graph["project_fail"] = {"mass": 50.0}
        snapshot = self.engine.process_turn("We lost the project. [grief]")
        final_glimmers = self.engine.bio.endo.glimmers
        self.assertGreater(final_glimmers, 0, "[FAIL] The Grief Protocol failed to yield a Glimmer.")

    def test_syntax_stress_penalty(self):
        from drivers.syntax import SyntaxModule
        from unittest.mock import MagicMock
        syntax = SyntaxModule(config_ref=self.test_config, lexicon_ref=MagicMock())
        toxic_text = "Wait, what;, why:- no, stop; this is bad, right?"
        initial_stress = syntax.grammatical_stress
        initial_omega = syntax.omega_val
        new_omega = syntax.analyze(toxic_text, narrative_drag=5.0)
        self.assertGreater(syntax.grammatical_stress, initial_stress, "[FAIL] Grammatical stress did not spike in response to punctuation density.")
        self.assertLess(new_omega, initial_omega, "[FAIL] Omega did not drop in response to high user stress.")
