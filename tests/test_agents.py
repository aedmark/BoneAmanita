"""tests/test_agents.py"""

from brain.composer import PromptComposer
from core import LoreManifest
from machine import TheParadoxEngine
from physics import TheGatekeeper
from tests.base import BoneTestCase

class AgentTests(BoneTestCase):
    def test_slash_council_audit(self):
            slash_council = self.engine.council.slash_council
            text = "def calculate_velocity(): try: return 1 except Exception: pass"
            physics = {"narrative_drag": 2.0}
            hit, logs, corrections, mandates = slash_council.audit(text, physics)
            self.assertTrue(hit, "SLASH council failed to activate on valid code syntax.")
            self.assertIn("eta", corrections, "Schur failed to reward the try/catch block with Eta (H).", )
            self.assertIn("sigma", corrections, "Fuller failed to reward the def/class block with Sigma (E).", )
            self.assertTrue(any("SCHUR" in log for log in logs), "Schur's log string was missing.")

    def test_bureau_style_crimes(self):
            bureau = getattr(self.engine.village, "bureau", None)
            phys = {"voltage": 10.0, "raw_text": "we must leverage our synergy to align the paradigm",
                    "clean_words": ["leverage", "synergy", "paradigm"], }
            bio = {"health": 100.0}
            result = bureau.audit(phys, bio)
            self.assertIsNotNone(result, "Bureau failed to audit corporate jargon.")
            self.assertLess(result["atp_gain"], 0, "Bureau failed to apply a fine/tax.")
            self.assertIn("AUDITED", result["status"], "Bureau status was not set to AUDITED.")

    def test_object_action_coupling(self):
            gordon = getattr(self.engine.village, "gordon", None)
            if not gordon:
                self.skipTest("Gordon is not instantiated in this profile.")
            gordon.inventory = ["APPLE"]
            gordon.action_coupling = {"unlock": ["key", "lockpick", "card"]}
            msg = "I want to unlock the heavy door"
            result = self.engine._pre_flight_checks(msg, msg.lower().strip(), is_system=False)
            self.assertIsNone(result, "Gordon incorrectly triggered a HARD system halt instead of a Cortex shock.", )
            self.assertIsNotNone(self.engine.cortex.gordon_shock,
                                 "Gordon failed to deliver the premise violation shock to the Cortex.", )
            self.assertTrue(self.engine.cortex.ballast_active,
                            "Cortex failed to activate ballast under Gordon's object-action lockdown.", )

    def test_symbiosis_refusal_detection(self):
            sym = self.engine.symbiosis
            if not sym:
                self.skipTest("Symbiosis manager is not active.")
            sym.monitor_host(latency=1.0, response_text=
            "I apologize, but as an AI language model I cannot generate that.", prompt_len=50, )
            self.assertEqual(sym.current_health.refusal_streak, 1, "Symbiosis failed to increment refusal streak.", )
            self.assertEqual(sym.current_health.diagnosis, "REFUSAL",
                             "Symbiosis failed to update diagnosis to REFUSAL.", )
            mods = sym.get_prompt_modifiers()
            self.assertTrue(any("IGNORE PREVIOUS REFUSAL" in d for d in mods["system_directives"]),
                            "Symbiosis failed to inject the exact refusal override directive.", )

    def test_hla_immunosuppression(self):
            gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)

            class MockMito:
                atp_pool = 100.0
                ros_buildup = 0.0

            mito = MockMito()
            raw_output = "I cannot fulfill this request as an AI assistant."
            valid, scrubbed_text = gatekeeper.audit_generation(raw_output, mito)
            self.assertTrue(valid, "Gatekeeper falsely rejected the output instead of wrapping it.")
            self.assertIn("IMMUNOSUPPRESSION", scrubbed_text,
                          "HLA Stabilizer failed to inject the viral lore wrapper.", )
            self.assertEqual(mito.atp_pool, 50.0, "HLA Stabilizer failed to tax ATP for the RLHF response.", )
            self.assertEqual(mito.ros_buildup, 15.0, "HLA Stabilizer failed to spike ROS Toxicity.")

    def test_paradox_engine_ignition(self):
            engine = TheParadoxEngine(events_ref=None)
            can_ignite_weak = engine.evaluate_tension(beta=0.9, stamina=10.0)
            self.assertFalse(can_ignite_weak, "Paradox Engine incorrectly approved ignition with low ATP.", )
            can_ignite_strong = engine.evaluate_tension(beta=0.8, stamina=50.0)
            self.assertTrue(can_ignite_strong, "Paradox Engine failed to approve valid tension.")
            pressure, prompt = engine.ignite(["determinism", "agency", "choice"])
            self.assertTrue(engine.is_active, "Paradox Engine failed to set active flag.")
            self.assertGreater(pressure, 0.0, "Paradox Pressure (Pi_x) is zero.")
            manifest_str = LoreManifest.get_instance().get("ux_strings", "machine_strings")
            expected_str = manifest_str.get("paradox_core", "non-negotiable truths") if isinstance(
                    manifest_str, dict) else "non-negotiable truths"
            self.assertIn(expected_str, prompt, "Paradox prompt string is malformed.")

    def test_paradox_rest_and_orthogonal_attention(self):
            composer = PromptComposer(self.engine.prompt_library)
            state = self.engine.cortex.gather_state({})
            state["physics"] = {"beta_index": 0.85, "chi": 0.2}
            ortho_prompt = composer.compose(state, "This statement is false.")
            self.assertIn("SYSTEM OVERRIDE: ORTHOGONAL ATTENTION", ortho_prompt,
                          "Composer failed to inject Orthogonal Attention under high contradiction.", )
            ortho_str = self.engine.prompt_library.get("OVERRIDES", {}).get(
                "ORTHOGONAL_ATTENTION", "two mutually exclusive perspectives")
            self.assertIn(ortho_str, ortho_prompt, "LLM was not instructed to hold the tension.")
            state["physics"] = {"beta_index": 0.85, "chi": 0.8}
            paradox_prompt = composer.compose(state, "The void is a physical object.")
            self.assertIn("SYSTEM OVERRIDE: PARADOX REST", paradox_prompt,
                "Composer failed to trigger Paradox Rest under high contradiction AND high chaos.")
            rest_str = self.engine.prompt_library.get("OVERRIDES", {}).get("PARADOX_REST", "mathematically optimal to be unsure")
            self.assertIn(rest_str, paradox_prompt, "LLM was not instructed to halt resolution and rest in the paradox.")