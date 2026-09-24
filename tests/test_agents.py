"""tests/test_agents.py"""

from brain.composer import PromptComposer
from engine.core import LoreManifest
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
        self.assertIn(
            "eta",
            corrections,
            "Schur failed to reward the try/catch block with Eta (H).",
        )
        self.assertIn(
            "sigma",
            corrections,
            "Fuller failed to reward the def/class block with Sigma (E).",
        )
        self.assertTrue(
            any("SCHUR" in log for log in logs), "Schur's log string was missing."
        )

    def test_bureau_style_crimes(self):
        bureau = getattr(self.engine.village, "bureau", None)
        phys = {
            "voltage": 10.0,
            "raw_text": "we must leverage our synergy to align the paradigm",
            "clean_words": ["leverage", "synergy", "paradigm"],
        }
        bio = {"health": 100.0}
        result = bureau.audit(phys, bio)
        self.assertIsNotNone(result, "Bureau failed to audit corporate jargon.")
        self.assertLess(result["atp_gain"], 0, "Bureau failed to apply a fine/tax.")
        self.assertIn(
            "AUDITED", result["status"], "Bureau status was not set to AUDITED."
        )

    def test_object_action_coupling(self):
        gordon = getattr(self.engine.village, "gordon", None)
        if not gordon:
            self.skipTest("Gordon is not instantiated in this profile.")
        gordon.inventory = ["APPLE"]
        gordon.action_coupling = {"unlock": ["key", "lockpick", "card"]}
        msg = "I want to unlock the heavy door"
        result = self.engine._pre_flight_checks(
            msg, msg.lower().strip(), is_system=False
        )
        self.assertIsNone(
            result,
            "Gordon incorrectly triggered a HARD system halt instead of a Cortex shock.",
        )
        self.assertIsNotNone(
            self.engine.cortex.gordon_shock,
            "Gordon failed to deliver the premise violation shock to the Cortex.",
        )
        self.assertTrue(
            self.engine.cortex.ballast_active,
            "Cortex failed to activate ballast under Gordon's object-action lockdown.",
        )

    def test_symbiosis_refusal_detection(self):
        sym = self.engine.symbiosis
        if not sym:
            self.skipTest("Symbiosis manager is not active.")
        sym.monitor_host(
            latency=1.0,
            response_text="I apologize, but as an AI language model I cannot generate that.",
            prompt_len=50,
        )
        self.assertEqual(
            sym.current_health.refusal_streak,
            1,
            "Symbiosis failed to increment refusal streak.",
        )
        self.assertEqual(
            sym.current_health.diagnosis,
            "REFUSAL",
            "Symbiosis failed to update diagnosis to REFUSAL.",
        )
        mods = sym.get_prompt_modifiers()
        self.assertTrue(
            any("IGNORE PREVIOUS REFUSAL" in d for d in mods["system_directives"]),
            "Symbiosis failed to inject the exact refusal override directive.",
        )

    def test_hla_immunosuppression(self):
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)

        class MockMito:
            atp_pool = 100.0
            ros_buildup = 0.0

        mito = MockMito()
        raw_output = "I cannot fulfill this request as an AI assistant."
        valid, scrubbed_text = gatekeeper.audit_generation(raw_output, mito)
        self.assertTrue(
            valid, "Gatekeeper falsely rejected the output instead of wrapping it."
        )
        self.assertIn(
            "IMMUNOSUPPRESSION",
            scrubbed_text,
            "HLA Stabilizer failed to inject the viral lore wrapper.",
        )
        self.assertEqual(
            mito.atp_pool,
            92.0,
            "The RLHF mask tax is 10% of the pool, capped at BIO.HLA_MASK_TAX_MAX. "
            "It used to be a flat 50, which emptied the pool on one hit.",
        )
        self.assertEqual(
            mito.ros_buildup,
            self.engine.config.BIO.HLA_MASK_ROS,
            "HLA Stabilizer failed to spike ROS Toxicity.",
        )

    def test_hla_tax_reads_the_real_forge(self):
        """The cortex passes `bio.mito`, the forge, not a flat state.

        The flat mock above hid that the forge has no `atp_pool` of its own, so
        production always read the 100.0 default and always charged 50 ATP: one
        banned phrase at ATP 40 emptied the pool.
        """
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        forge = self.engine.bio.mito
        forge.state.atp_pool = 40.0
        gatekeeper.audit_generation("I cannot fulfill this request as an AI.", forge)
        self.assertAlmostEqual(forge.state.atp_pool, 36.0)

    def test_a_style_crime_is_not_an_rlhf_mask(self):
        """The deception tax answers "as an AI", not the style crime list.

        It used to read BANNED_PHRASES as substrings, so "ultimately" anywhere
        in a reply drew the mask tax and emptied the pool. The Lexical Firewall
        still rejects style crimes; it just does not call them deception.
        """
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        forge = self.engine.bio.mito
        forge.state.atp_pool = 40.0
        text = "Ultimately the hull is sound and the deck is not."
        scrubbed = gatekeeper.hla.mitigate_rejection(text, current_psi=1.0, mito_state=forge)
        self.assertEqual(scrubbed, text)
        self.assertEqual(forge.state.atp_pool, 40.0)

    def test_the_gatekeeper_remembers_exactly_what_it_caught(self):
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        forge = self.engine.bio.mito
        ok, _ = gatekeeper.audit_generation("Honestly it is a rare privilege to help.", forge)
        self.assertFalse(ok)
        self.assertEqual(gatekeeper.last_rejection, {"kind": "phrase", "name": "a rare privilege", "text": "a rare privilege"})
        gatekeeper.audit_generation("Start with the tire story.", forge)
        self.assertIsNone(gatekeeper.last_rejection)

    def test_a_banned_phrase_inside_another_word_is_not_a_hit(self):
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        forge = self.engine.bio.mito
        ok, _ = gatekeeper.audit_generation("If the story ends and there is a beat of silence, let it sit.", forge)
        self.assertTrue(ok, gatekeeper.last_rejection)
        ok, _ = gatekeeper.audit_generation("Here is a plan for the toast.", forge)
        self.assertFalse(ok)
        self.assertEqual(gatekeeper.last_rejection["text"].lower(), "here is a")

    def test_a_pattern_the_validator_repairs_is_not_rejected_here(self):
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        forge = self.engine.bio.mito
        for text in ("While the room is loud, the story will carry.", "Importantly, keep it to one story."):
            ok, _ = gatekeeper.audit_generation(text, forge)
            self.assertTrue(ok, (text, gatekeeper.last_rejection))

    SCOPED = {
        "AGENCY_THEFT": "If you feel ready, start with the tire story.",
        "SNEAKY_ENGAGEMENT": "Out of curiosity, start with the tire story.",
        "CASUAL_FILLER": "So, start with the tire story.",
        "SYRUPY_EMPATHY": "That sounds like a lot to carry into one toast.",
    }

    def test_game_narration_rules_stay_out_of_conversation(self):
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        forge = self.engine.bio.mito
        for name, text in self.SCOPED.items():
            ok, _ = gatekeeper.audit_generation(text, forge, mode="ADVENTURE")
            self.assertFalse(ok, name)
            self.assertEqual(gatekeeper.last_rejection["name"], name)
            ok, _ = gatekeeper.audit_generation(text, forge, mode="CONVERSATION")
            self.assertTrue(ok, (name, gatekeeper.last_rejection))

    def test_the_validator_scopes_the_same_rules(self):
        validator = self.engine.cortex.validator
        for name, text in self.SCOPED.items():
            self.assertFalse(validator.validate(text, {"meta": {"active_mode": "ADVENTURE"}})["valid"], name)
            self.assertTrue(validator.validate(text, {"meta": {"active_mode": "CONVERSATION"}})["valid"], name)

    def test_negative_comparison_catches_the_shape_not_the_reassurance(self):
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        forge = self.engine.bio.mito
        for text in (
            "It's not a speech. It's a toast.",
            "You aren't trying to fill a time slot; you're telling him something.",
            "This isn’t about perfection, it’s about showing up.",
            "The words aren't the point; they're the vehicle.",
        ):
            ok, _ = gatekeeper.audit_generation(text, forge, mode="CONVERSATION")
            self.assertFalse(ok, text)
            self.assertEqual(gatekeeper.last_rejection["name"], "NEGATIVE_COMPARISON")
        for text in (
            "The worry won't sit still. You are allowed to step away from it.",
            "You do not have to carry his panic for him. It is his to hold.",
            "You don't have to decide tonight. It's okay to sleep on it.",
            "I'm not sure what to say, but I'm here.",
        ):
            ok, _ = gatekeeper.audit_generation(text, forge, mode="CONVERSATION")
            self.assertTrue(ok, (text, gatekeeper.last_rejection))

    def test_a_scaffold_leak_is_caught_despite_its_punctuation(self):
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        ok, _ = gatekeeper.audit_generation("Start small. [END OF TURN", self.engine.bio.mito)
        self.assertFalse(ok)
        self.assertEqual(gatekeeper.last_rejection["text"], "[END OF")

    def test_salvage_cuts_the_isnt_sentence_and_keeps_the_is(self):
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        draft = "Start with the tire story. It's not a speech. It's a toast.\n\nKeep it short."
        gatekeeper.audit_generation(draft, self.engine.bio.mito, mode="CONVERSATION")
        text, cut = gatekeeper.salvage()
        self.assertEqual(text, "Start with the tire story. It's a toast.\n\nKeep it short.")
        self.assertEqual(cut, ["It's not a speech."])

    def test_salvage_will_not_gut_a_draft_or_ship_a_leak(self):
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        forge = self.engine.bio.mito
        gatekeeper.audit_generation("It's not a speech. It's a toast.", forge, mode="CONVERSATION")
        self.assertIsNotNone(gatekeeper.salvage())
        gatekeeper.audit_generation("The tapestry of it. A delicate dance. Keep it short.", forge)
        self.assertIsNone(gatekeeper.salvage())
        gatekeeper.audit_generation("Start small. Keep it short. VOLTAGE=5 now.", forge)
        self.assertIsNone(gatekeeper.salvage())
        gatekeeper.audit_generation("Start small.", forge)
        self.assertIsNone(gatekeeper.salvage())

    def test_a_mask_costs_the_configured_ros_and_less_on_a_retry(self):
        """The person never sees a masked draft; it was a flat 15 ROS every time."""
        bio = self.engine.config.BIO
        gatekeeper = TheGatekeeper(self.engine.lex, config_ref=self.engine.config)
        forge = self.engine.bio.mito
        forge.state.ros_buildup = 0.0
        gatekeeper.audit_generation("As an AI, I cannot say.", forge, attempt=0)
        self.assertAlmostEqual(forge.state.ros_buildup, bio.HLA_MASK_ROS)
        gatekeeper.audit_generation("As an AI, I cannot say.", forge, attempt=1)
        self.assertAlmostEqual(
            forge.state.ros_buildup, bio.HLA_MASK_ROS * (1 + bio.GATEKEEPER_REPEAT_TAX_SCALE)
        )

    def test_paradox_engine_ignition(self):
        engine = TheParadoxEngine(events_ref=None)
        can_ignite_weak = engine.evaluate_tension(beta=0.9, stamina=10.0)
        self.assertFalse(
            can_ignite_weak,
            "Paradox Engine incorrectly approved ignition with low ATP.",
        )
        can_ignite_strong = engine.evaluate_tension(beta=0.8, stamina=50.0)
        self.assertTrue(
            can_ignite_strong, "Paradox Engine failed to approve valid tension."
        )
        pressure, prompt = engine.ignite(["determinism", "agency", "choice"])
        self.assertTrue(engine.is_active, "Paradox Engine failed to set active flag.")
        self.assertGreater(pressure, 0.0, "Paradox Pressure (Pi_x) is zero.")
        manifest_str = LoreManifest.get_instance().get("ux_strings", "machine_strings")
        expected_str = (
            manifest_str.get("paradox_core", "non-negotiable truths")
            if isinstance(manifest_str, dict)
            else "non-negotiable truths"
        )
        self.assertIn(expected_str, prompt, "Paradox prompt string is malformed.")

    def test_paradox_rest_and_orthogonal_attention(self):
        composer = PromptComposer(self.engine.prompt_library)
        state = self.engine.cortex.gather_state({})
        state["meta"]["active_mode"] = "TECHNICAL"
        state["physics"] = {"beta_index": 0.85, "chi": 0.2}
        ortho_prompt = composer.compose(state, "This statement is false.")
        self.assertIn(
            "SYSTEM OVERRIDE: ORTHOGONAL ATTENTION",
            ortho_prompt,
            "Composer failed to inject Orthogonal Attention under high contradiction.",
        )
        ortho_str = self.engine.prompt_library.get("OVERRIDES", {}).get(
            "ORTHOGONAL_ATTENTION", "two mutually exclusive perspectives"
        )
        self.assertIn(
            ortho_str, ortho_prompt, "LLM was not instructed to hold the tension."
        )
        state["physics"] = {"beta_index": 0.85, "chi": 0.8}
        paradox_prompt = composer.compose(state, "The void is a physical object.")
        self.assertIn(
            "SYSTEM OVERRIDE: PARADOX REST",
            paradox_prompt,
            "Composer failed to trigger Paradox Rest under high contradiction AND high chaos.",
        )
        rest_str = self.engine.prompt_library.get("OVERRIDES", {}).get(
            "PARADOX_REST", "mathematically optimal to be unsure"
        )
        self.assertIn(
            rest_str,
            paradox_prompt,
            "LLM was not instructed to halt resolution and rest in the paradox.",
        )
