"""bone_diag.py"""

import unittest
from unittest.mock import patch

from bone_core import LoreManifest
from bone_main import BoneAmanita


class TrueEngineTest(unittest.TestCase):
    def setUp(self):
        self.test_config = {"PROVIDER": "mock", "boot_mode": "ADVENTURE", "MAX_STAMINA": 100.0, "MAX_HEALTH": 100.0, }
        self.engine = BoneAmanita(config=self.test_config)
        self.initial_atp = self.engine.bio.mito.state.atp_pool
        self.initial_stamina = self.engine.stamina

    def tearDown(self):
        LoreManifest.get_instance().flush_cache()

    def test_gordon_rummage_stamina_tax(self):
        self.engine.stamina = 50.0
        success, msg, cost = self.engine.gordon.rummage(physics_ref={}, stamina_pool=self.engine.stamina)
        self.engine.stamina -= cost
        self.assertTrue(cost > 0, "Rummaging cost no stamina.")

    def test_panic_room_fallback_on_crash(self):
        with patch(
                "bone_cycle.CycleSimulator.run_simulation",
                side_effect=Exception("Simulated Total Crash"),):
            result = self.engine.cycle_controller.run_headless_turn("Hello?")
        self.assertTrue(result.get("is_alive", True), "Engine died instead of retreating to the Panic Room.", )
        self.assertEqual(result.get("type"), "CRASH", "Engine did not generate a CRASH report.")
        self.assertIn("REALITY FRACTURE", result.get("ui", ""), "UI missing critical reality fracture warning.", )

    def test_death_by_starvation(self):
        from bone_village import DeathGen
        from bone_types import PhysicsPacket
        phys = PhysicsPacket(voltage=5.0, narrative_drag=1.0)
        bio_state = {"atp": 0.0}
        _, cause = DeathGen.eulogy(phys, bio_state)
        self.assertEqual(cause, "STARVATION", "DeathGen failed to diagnose STARVATION.")

    def test_death_by_gluttony(self):
        from bone_village import DeathGen
        from bone_types import PhysicsPacket
        phys = PhysicsPacket(voltage=150.0, narrative_drag=0.0)
        bio_state = {"atp": 50.0}
        _, cause = DeathGen.eulogy(phys, bio_state)
        self.assertEqual(cause, "GLUTTONY", "DeathGen failed to diagnose GLUTTONY.")

    def test_slash_council_audit(self):
        slash_council = self.engine.council.slash_council
        text = "def calculate_velocity(): try: return 1 except Exception: pass"
        physics = {"narrative_drag": 2.0}
        hit, logs, corrections = slash_council.audit(text, physics)
        self.assertTrue(hit, "SLASH council failed to activate on valid code syntax.")
        self.assertIn("eta", corrections, "Schur failed to reward the try/catch block with Eta (H).")
        self.assertIn("sigma", corrections, "Fuller failed to reward the def/class block with Sigma (E).")
        self.assertTrue(any("SCHUR" in log for log in logs), "Schur's log string was missing.")

    def test_bureau_style_crimes(self):
        bureau = self.engine.village["bureau"]
        phys = {"voltage": 10.0, "raw_text": "we must leverage our synergy to align the paradigm",
                "clean_words": ["leverage", "synergy", "paradigm"]}
        bio = {"health": 100.0}
        result = bureau.audit(phys, bio)
        self.assertIsNotNone(result, "Bureau failed to audit corporate jargon.")
        self.assertLess(result["atp_gain"], 0, "Bureau failed to apply a fine/tax.")
        self.assertIn("AUDITED", result["status"], "Bureau status was not set to AUDITED.")

    def test_object_action_coupling(self):
        gordon = self.engine.gordon
        gordon.inventory = ["APPLE"]
        gordon.action_coupling = {"unlock": ["key", "lockpick", "card"]}
        violation = gordon.enforce_object_action_coupling("I want to unlock the heavy door", "COURTYARD")
        self.assertIsNotNone(violation, "Gordon failed to catch the premise violation.")
        self.assertIn("denied", violation.lower(), "Gordon did not explicitly deny the action.")

    def test_symbiosis_refusal_detection(self):
        sym = self.engine.symbiosis
        sym.monitor_host(latency=1.0, response_text="I apologize, but as an AI language model I cannot generate that.", prompt_len=50)
        self.assertEqual(sym.current_health.refusal_streak, 1, "Symbiosis failed to increment refusal streak.")
        self.assertEqual(sym.current_health.diagnosis, "REFUSAL", "Symbiosis failed to update diagnosis to REFUSAL.")
        mods = sym.get_prompt_modifiers()
        self.assertTrue(any("IGNORE PREVIOUS REFUSAL" in d for d in mods["system_directives"]),
                        "Symbiosis failed to inject the exact refusal override directive.")

    def test_decoupled_json_configs(self):
        from bone_physics import ChromaScope
        manifest = LoreManifest.get_instance()
        gordon = self.engine.gordon
        self.assertTrue(hasattr(gordon, "interaction_verbs"), "Gordon is missing the interaction_verbs attribute.")
        self.assertIsInstance(gordon.interaction_verbs, list, "Gordon's interaction_verbs should be a list.")
        driver_cfg = manifest.get("driver_config", "ENNEAGRAM_WEIGHTS")
        self.assertIsNotNone(driver_cfg, "DRIVER_CONFIG failed to load Enneagram weights.")
        phys_cfg = manifest.get("physics_constants", "GEODESIC_CONSTANTS")
        self.assertIsNotNone(phys_cfg, "PHYSICS_CONSTANTS failed to load Geodesic constants.")
        colored_text = ChromaScope.modulate("test", {"VEL": 1.0})
        self.assertNotEqual(colored_text, "test", "ChromaScope failed to apply ANSI color from decoupled JSON.")
        sym_cfg = manifest.get("symbiosis_config", "SYMBIONT_VOICES")
        self.assertIsNotNone(sym_cfg, "SYMBIOSIS_CONFIG failed to load Symbiont Voices.")
        body_cfg = manifest.get("body_config", "ENZYME_MAP")
        self.assertIsNotNone(body_cfg, "BODY_CONFIG failed to load Enzyme Map.")

    def test_config_stutter_threshold(self):
        from bone_config import BoneConfig
        original_stutter = getattr(BoneConfig.CORTEX, "VALIDATOR_STUTTER_LENGTH", 5)
        BoneConfig.CORTEX.VALIDATOR_STUTTER_LENGTH = 100
        test_string = "This is a perfectly coherent response. It is just too short."
        result = self.engine.cortex.validator.validate(test_string, self.engine.cortex.last_physics)
        self.assertFalse(result["valid"], "Validator failed to catch the stutter based on the new config threshold.")
        self.assertEqual(result["reason"], "STUTTER", "Rejection reason was not properly flagged as STUTTER.")
        BoneConfig.CORTEX.VALIDATOR_STUTTER_LENGTH = original_stutter

    def test_config_metabolic_recovery(self):
        from bone_config import BoneConfig
        self.engine.bio.biometrics.health = 50.0
        self.engine.bio.biometrics.stamina = 50.0
        orig_h_rec = getattr(BoneConfig.BIO, "REST_HEALTH_RECOVERY", 0.5)
        orig_s_rec = getattr(BoneConfig.BIO, "REST_STAMINA_RECOVERY", 1.0)
        BoneConfig.BIO.REST_HEALTH_RECOVERY = 20.0
        BoneConfig.BIO.REST_STAMINA_RECOVERY = 40.0
        self.engine.bio.rest(factor=1.0)
        self.assertEqual(self.engine.bio.biometrics.health, 70.0, "Health did not recover at the configured rate.")
        self.assertEqual(self.engine.bio.biometrics.stamina, 90.0, "Stamina did not recover at the configured rate.")
        BoneConfig.BIO.REST_HEALTH_RECOVERY = orig_h_rec
        BoneConfig.BIO.REST_STAMINA_RECOVERY = orig_s_rec

    def test_config_glimmer_yield(self):
        from bone_config import BoneConfig
        orig_thresh = getattr(BoneConfig.BIO, "GLIMMER_INTEGRITY_THRESH", 0.85)
        BoneConfig.BIO.GLIMMER_INTEGRITY_THRESH = 1.5
        feedback = {"INTEGRITY": 0.95}
        glimmer_msg = self.engine.bio.endo.check_for_glimmer(feedback, harvest_hits=1)
        self.assertIsNone(glimmer_msg, "System generated a glimmer even though the integrity threshold was not met.")
        BoneConfig.BIO.GLIMMER_INTEGRITY_THRESH = 0.5
        glimmer_msg_success = self.engine.bio.endo.check_for_glimmer(feedback, harvest_hits=1)
        self.assertIsNotNone(glimmer_msg_success, "System failed to generate a glimmer after the threshold was lowered.")
        BoneConfig.BIO.GLIMMER_INTEGRITY_THRESH = orig_thresh

    def test_ux_string_decoupling_inventory(self):
        from bone_inventory import Item
        manifest = LoreManifest.get_instance()
        if "ux_strings" not in manifest._cache: manifest._cache["ux_strings"] = {}
        if "gordon_strings" not in manifest._cache["ux_strings"]: manifest._cache["ux_strings"]["gordon_strings"] = {}
        manifest._cache["ux_strings"]["gordon_strings"]["default_item_desc"] = "A highly suspicious geometric shape."
        test_item = Item.from_dict("TEST_OBJECT", {})
        self.assertEqual(test_item.description, "A highly suspicious geometric shape.",
                         "Item.from_dict failed to pull the dynamic description from LoreManifest.")

    def test_panic_room_config_injection(self):
        from bone_machine import PanicRoom
        manifest = LoreManifest.get_instance()
        if "ux_strings" not in manifest._cache: manifest._cache["ux_strings"] = {}
        manifest._cache["ux_strings"]["machine_strings"] = {"panic_resp_fallback": "CRYOSLEEP",
                                                            "panic_clean_words": ["safe", "warm", "blanket"]}
        safe_bio = PanicRoom.get_safe_bio()
        self.assertEqual(safe_bio.get("respiration"), "CRYOSLEEP",
                         "PanicRoom failed to use the injected respiration fallback.")
        safe_phys = PanicRoom.get_safe_physics()
        self.assertIn("blanket", safe_phys.clean_words, "PanicRoom failed to load the injected clean words array.")

    def test_symbiosis_anchor_graceful_degradation(self):
        from bone_symbiosis import CoherenceAnchor
        manifest = LoreManifest.get_instance()
        if "ux_strings" in manifest._cache:
            manifest._cache["ux_strings"]["symbiosis_strings"] = {}
        soul_state = {"traits": {"curiosity": 0.8}, "obsession": {"title": "Testing Silence"}}
        phys_state = {"voltage": 12.0, "narrative_drag": 1.0, "zone": "TEST_ZONE"}
        try:
            anchor_str = CoherenceAnchor.forge_anchor(soul_state, phys_state)
            self.assertIsInstance(anchor_str, str, "Anchor generation failed to return a string.")
        except Exception as e:
            self.fail(f"CoherenceAnchor crashed when deprived of UX strings: {e}")

    def test_kintsugi_dynamic_logs(self):
        from bone_protocols import KintsugiProtocol
        manifest = LoreManifest.get_instance()
        if "ux_strings" not in manifest._cache: manifest._cache["ux_strings"] = {}
        manifest._cache["ux_strings"]["protocol_strings"] = {"kintsugi_log_scar": "Golden scars bind the {target}",
                                                             "kintsugi_scar": "A quiet mending."}
        kintsugi = KintsugiProtocol()
        kintsugi.active_koan = "Test Koan"
        trauma = {"EXISTENTIAL": 0.8}
        phys = type("obj", (object,), {"voltage": 2.0, "raw_text": "nothing"})
        result = kintsugi.attempt_repair(phys, trauma)
        self.assertTrue(result["success"])
        self.assertIn("Golden scars bind the EXISTENTIAL", result["healed"],
                      "Kintsugi failed to dynamically format the log string from the manifest.")

    def test_telemetry_phase_hooks(self):
        from bone_core import TelemetryService
        from bone_types import DecisionCrystal
        manifest = LoreManifest.get_instance()
        if "ux_strings" not in manifest._cache: manifest._cache["ux_strings"] = {}
        manifest._cache["ux_strings"]["core_strings"] = {"tel_phase_start": "COMMENCING ALIGNMENT"}
        telemetry = TelemetryService.get_instance()
        telemetry.disabled = False
        telemetry.active_crystal = DecisionCrystal(decision_id="TEST_ID")
        telemetry.start_phase("TEST_PHASE", None)
        latest_trace = telemetry.trace_buffer[-1]
        self.assertEqual(latest_trace.reasoning, "COMMENCING ALIGNMENT",
                         "Telemetry failed to use the dynamically injected phase start string.")

    def test_prompt_composer_anti_bleed_membranes(self):
        from bone_brain import PromptComposer

        mock_lore = {"system_prompts": self.engine.prompt_library, "lenses": {}}
        composer = PromptComposer(mock_lore)

        self.engine.cortex.active_mode = "CONVERSATION"

        conv_state = self.engine.cortex.gather_state({"physics": {"voltage": 30.0}})

        conv_prompt = composer.compose(conv_state, "Hello?", modifiers={"include_inventory": False})

        self.assertNotIn("Object-Action Coupling", conv_prompt,
                         "ADVENTURE mechanics bled into CONVERSATION mode prompt.")
        self.assertIn("Do not act like a Dungeon Master", conv_prompt,
                      "CONVERSATION Anti-Bleed constraint was not injected.")
        self.assertNotIn("INVENTORY:", conv_prompt,
                         "Inventory block rendered in Conversation mode despite being suppressed.")

        self.engine.cortex.active_mode = "TECHNICAL"

        tech_state = self.engine.cortex.gather_state({"physics": {"voltage": 30.0}})

        tech_prompt = composer.compose(tech_state, "Refactor this.", modifiers={"include_inventory": False})

        self.assertIn("Clinical, precise", tech_prompt,
                      "TECHNICAL style guide missing.")
        self.assertIn("Do not write prose, poetry, or narrative descriptions.", tech_prompt,
                      "TECHNICAL Anti-Bleed constraint was not injected.")

    def test_phase_shift_persona_morphing(self):
        from bone_brain import PromptComposer
        mock_lore = {"system_prompts": self.engine.prompt_library, "lenses": {}}
        composer = PromptComposer(mock_lore)
        state = self.engine.cortex.gather_state({})
        state["mind"]["lens"] = "ROBERTA"
        state["mind"]["role"] = "The Breadth Retriever"
        state["physics"] = {"phi": 0.8, "psi": 0.7}
        persona_block = composer._build_persona_block(state["mind"], state["bio"], "",
                                                      self.engine.prompt_library.get("ADVENTURE", {}),
                                                      self.engine.prompt_library.get("GLOBAL_BASELINE", {}),
                                                      self.engine.prompt_library.get("HIGH_VOLTAGE", {}),
                                                      state["physics"])

        persona_str = "\n".join(persona_block)
        self.assertIn("Role: The Cartographer", persona_str,
                      "Roberta failed to Phase Shift into The Cartographer under high Phi/Psi.")
        state["mind"]["lens"] = "JESTER"
        state["mind"]["role"] = "The Bard of Chaos"
        state["physics"] = {"delta": 0.9}
        persona_block_jester = composer._build_persona_block(state["mind"], state["bio"], "",
                                                             self.engine.prompt_library.get("ADVENTURE", {}),
                                                             self.engine.prompt_library.get("GLOBAL_BASELINE", {}),
                                                             self.engine.prompt_library.get("HIGH_VOLTAGE", {}),
                                                             state["physics"])
        persona_str_jester = "\n".join(persona_block_jester)
        self.assertIn("Role: The Fool", persona_str_jester,
                      "Jester failed to Phase Shift into The Fool under high Delta.")

    def test_paradox_rest_and_orthogonal_attention(self):
        from bone_brain import PromptComposer
        composer = PromptComposer(self.engine.prompt_library)
        state = self.engine.cortex.gather_state({})
        state["physics"] = {"beta_index": 0.85, "chi": 0.2}
        ortho_prompt = composer.compose(state, "This statement is false.")
        self.assertIn("SYSTEM OVERRIDE: ORTHOGONAL ATTENTION", ortho_prompt,
                      "Composer failed to inject Orthogonal Attention under high contradiction.")
        self.assertIn("two mutually exclusive perspectives simultaneously", ortho_prompt,
                      "LLM was not instructed to hold the tension.")
        state["physics"] = {"beta_index": 0.85, "chi": 0.8}
        paradox_prompt = composer.compose(state, "The void is a physical object.")
        self.assertIn("SYSTEM OVERRIDE: PARADOX REST", paradox_prompt,
                      "Composer failed to trigger Paradox Rest under high contradiction AND high chaos.")
        self.assertIn("mathematically optimal to be unsure", paradox_prompt,
                      "LLM was not instructed to halt resolution and rest in the paradox.")

    def test_autophagy_memory_cannibalization(self):
        memory_graph = self.engine.mind.mem.graph if hasattr(self.engine.mind, "mem") else self.engine.akashic.graph
        memory_graph["User's favorite color"] = {"edges": {"blue": 1.0}, "last_tick": 0}
        initial_node_count = len(memory_graph)
        self.engine.bio.mito.state.atp_pool = 0.0
        self.engine.bio.biometrics.stamina = 5.0
        self.engine.cycle_controller.run_headless_turn("I need you to think very hard about this.")
        self.assertLess(len(memory_graph), initial_node_count,
                        "System failed to cannibalize a memory node during starvation.")
        self.assertNotIn("User's favorite color", memory_graph,
                         "System consumed the wrong node or failed to delete the target memory.")
        self.assertGreater(self.engine.bio.mito.state.atp_pool, 0.0,
                           "Autophagy failed to refund ATP to the Mitochondrial Forge.")

    def test_autophagy_prompt_injection(self):
        from bone_brain import PromptComposer
        composer = PromptComposer(self.engine.prompt_library)
        state = self.engine.cortex.gather_state({"physics": {"voltage": 30.0}})
        state["recent_logs"] = [
            "\033[31m[AUTOPHAGY: Consumed memory of 'User's favorite color' to survive.]\033[0m"
        ]
        prompt = composer.compose(state, "What was my favorite color?")
        self.assertIn("[AUTOPHAGY:", prompt,
                      "The PromptComposer failed to inject the Autophagy footnote into the LLM's context window.")
        self.assertIn("favorite color", prompt,
                      "The specific consumed memory was not communicated to the LLM.")

    def test_dream_defragmentation_pruning(self):
        from bone_brain import DreamEngine

        class MockMemorySystem:
            def __init__(self):
                self.graph = {"Weak Node": {"edges": {"trivial": 1.0}},
                              "Core Strut": {"edges": {"vital": 10.0, "crucial": 5.0}}}
        mock_mem = MockMemorySystem()
        report = DreamEngine.run_defragmentation(mock_mem, limit=1)
        self.assertNotIn("Weak Node", mock_mem.graph,
                         "DreamEngine failed to prune the weak memory node.")
        self.assertIn("Core Strut", mock_mem.graph,
                      "DreamEngine accidentally pruned a load-bearing memory strut.")
        self.assertIn("Weak Node", report,
                      "DreamEngine did not report the pruned node in its return string.")

    def test_subconscious_matrix_absorption(self):
        import tempfile
        import os
        from bone_spores import SubconsciousStrata
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            strata = SubconsciousStrata(filename=tmp_path)
            initial_vibe = strata.dredge_vibe("oblivion")
            self.assertEqual(sum(initial_vibe), 0.0, "Initial matrix should yield a completely zeroed vibe.")
            strata.bury({"word": "oblivion", "mass": 10.0})
            new_vibe = strata.dredge_vibe("oblivion")
            vibe_sum = sum(new_vibe)
            self.assertNotEqual(vibe_sum, 0.0, "Matrix failed to absorb the K*V weights of the buried word.")
            self.assertEqual(len(new_vibe), 8, "Vibe vector must be exactly 8-dimensional.")

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            matrix_path = os.path.join(os.path.dirname(tmp_path), "m_t_matrix.json")
            if os.path.exists(matrix_path):
                os.remove(matrix_path)

    def test_ghost_physics_haunting(self):
        import tempfile
        import os
        from bone_spores import MycelialNetwork
        from bone_core import EventBus
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
            tmp_path = tmp.name
        bus = EventBus()
        network = MycelialNetwork(events=bus)
        network.subconscious.filepath = tmp_path
        try:
            network.subconscious.matrix_filepath = os.path.join(os.path.dirname(tmp_path), "test_m_t2.json")
            network.subconscious.bury({"word": "echo", "mass": 10.0})
            physics = {"clean_words": ["echo", "hello"], "voltage": 10.0, "narrative_drag": 1.0}
            log = network._poll_ghosts(physics["clean_words"], physics)
            self.assertIsNotNone(log, "Ghost poll failed to detect the buried word.")
            self.assertNotEqual(physics["voltage"], 10.0, "The ghost failed to mutate the system Voltage.")
            self.assertNotEqual(physics["narrative_drag"], 1.0, "The ghost failed to mutate the system Drag.")
            self.assertIn("ECHO", log, "The log string did not identify the haunting word.")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if hasattr(network, 'subconscious') and os.path.exists(network.subconscious.matrix_filepath):
                os.remove(network.subconscious.matrix_filepath)

    def test_v6_smarter_drag_profile(self):
        from bone_types import PhysicsPacket
        from bone_drivers import SharedLatticeDriver
        driver = SharedLatticeDriver()
        phys = PhysicsPacket(beta=0.9, chi=0.8, voltage=40.0)
        phys.valence = -0.9
        driver.infer_and_couple("This makes no sense and I hate it.", phys, phys, 20.0)
        self.assertGreater(phys.drag_profile.semantic, 2.0, "Semantic drag failed to calculate from Beta/Chi.")
        self.assertGreater(phys.drag_profile.emotional, 1.0, "Emotional drag failed to calculate from Valence.")
        self.assertEqual(phys.drag_profile.metabolic, 3.0, "Metabolic drag failed to trigger on low ATP.")
        phys.sync_drag()
        self.assertGreater(phys.narrative_drag, 5.0, "Drag profile failed to sync to total narrative_drag.")

    def test_v6_grammar_of_silence(self):
        import time
        from bone_types import PhysicsPacket
        from bone_drivers import SharedLatticeDriver
        driver = SharedLatticeDriver()
        phys = PhysicsPacket(beta=0.8)
        driver.shared.phi = 0.85
        driver.shared.lambda_silence = 0.5
        driver.last_timestamp = time.time() - 20.0
        logs, _ = driver.infer_and_couple("Finally, I have the words.", phys, phys, 100.0)
        self.assertGreater(driver.shared.delta, 0.0, "Silence weight (Nabla/Delta) failed to accumulate.")
        self.assertEqual(driver.shared.sigma_silence, 1, "Silence failed to classify as Pregnant (Sigma 1).")
        self.assertTrue(any("wanted to be born" in log for log in logs), "System failed to articulate the pregnant silence.")

    def test_v6_paradox_engine_ignition(self):
        from bone_machine import TheParadoxEngine
        engine = TheParadoxEngine(events_ref=None)
        can_ignite_weak = engine.evaluate_tension(beta=0.9, stamina=10.0)
        self.assertFalse(can_ignite_weak, "Paradox Engine incorrectly approved ignition with low ATP.")
        can_ignite_strong = engine.evaluate_tension(beta=0.8, stamina=50.0)
        self.assertTrue(can_ignite_strong, "Paradox Engine failed to approve valid tension.")
        pressure, prompt = engine.ignite(["determinism", "agency", "choice"])
        self.assertTrue(engine.is_active, "Paradox Engine failed to set active flag.")
        self.assertGreater(pressure, 0.0, "Paradox Pressure (Pi_x) is zero.")
        self.assertIn("non-negotiable truths", prompt, "Paradox prompt string is malformed.")

    def test_v6_foothills_veil_hush(self):
        from bone_gui import CycleReporter
        reporter = CycleReporter(self.engine)
        self.engine.config["mode_settings"] = {"default_ui_depth": "WARM"}
        raw_logs = ["[BIO] Adrenaline spiking.", "[CRITIC] JESTER: This is absurd.", "[SYS] Calculating vectors.",
                    "The forest path opens up before you."]
        reporter.switch_renderer("STANDARD")
        clean_logs = reporter.renderer.compose_logs(raw_logs, [], 0)
        joined_logs = " ".join(clean_logs)
        self.assertNotIn("[BIO]", joined_logs, "CycleReporter leaked BIO tags in WARM mode.")
        self.assertNotIn("[CRITIC]", joined_logs, "CycleReporter leaked CRITIC tags in WARM mode.")
        self.assertIn("forest path", joined_logs, "CycleReporter accidentally muted valid narrative output.")

    def test_v6_grief_protocol_healing(self):

        if not hasattr(self.engine, "shared_lattice"):
            from bone_drivers import SharedLatticeDriver
            self.engine.shared_lattice = SharedLatticeDriver()
        self.engine.phys.G = 1
        self.engine.shared_lattice.u.T_u = 5.0
        user_input = "[GRIEF] I accept that we had to delete that module."
        self.engine._pre_flight_checks(user_input, is_system=False)
        self.assertEqual(self.engine.phys.G, 0, "Grief Protocol failed to deduct the Glimmer.")
        self.assertEqual(self.engine.shared_lattice.u.T_u, 3.0, "Grief Protocol failed to heal user Trauma (T_u).")
        logs = self.engine.events.flush()
        self.assertTrue(any("compost" in str(log) for log in logs), "Mercy's eulogy was not logged to the event bus.")

if __name__ == "__main__":
    unittest.main()