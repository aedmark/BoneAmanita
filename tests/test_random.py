"""tests/test_random.py"""

import os

from unittest.mock import MagicMock, patch

from archetypes.village import DeathGen
from brain.composer import PromptComposer
from engine.core import CycleContext, LoreManifest
from engine.cycle import MetabolismPhase, SimulationPreflightPhase
from drivers import SharedLatticeDriver
from mechanics.reporter import CycleReporter
from physics import ChromaScope
from physics.models import EnergyState, PhysicsPacket
from tests.base import BoneTestCase


class RandomTest(BoneTestCase):
    def setUp(self):
        from engine.core import LoreManifest

        LoreManifest.get_instance().flush_cache()
        super().setUp()

    def tearDown(self):
        from engine.core import LoreManifest

        LoreManifest.get_instance().flush_cache()
        super().tearDown()

    def test_gordon_rummage_stamina_tax(self):
        self.engine.stamina = 50.0
        success, msg, cost = self.engine.village.gordon.rummage(
            physics_ref={}, stamina_pool=self.engine.stamina
        )
        self.engine.stamina -= cost
        self.assertTrue(cost > 0, "Rummaging cost no stamina.")

    def test_cortex_collapse_graceful_handling(self):
        crash_log = os.path.join(self.engine.telemetry.log_dir, "crashes.log")
        if os.path.exists(crash_log):
            os.remove(crash_log)
        with patch.object(
            self.engine.orchestrator.simulator,
            "run_simulation",
            side_effect=Exception("Simulated Core Simulator Collapse"),
        ):
            result = self.engine.process_turn("Hello?")
        self.assertIn(
            "ui", result, "Engine failed to return a UI packet during a crash."
        )
        self.assertIn(
            "CRITICAL FAILURE",
            result.get("logs", []),
            "Engine did not log the critical failure.",
        )

        # The traceback goes to the crash log, never the screen.
        self.assertNotIn("Simulated Core Simulator Collapse", str(result.get("ui", "")))
        with open(crash_log, encoding="utf-8") as f:
            self.assertIn("Simulated Core Simulator Collapse", f.read())

    def test_decoupled_json_configs(self):
        manifest = LoreManifest.get_instance()
        gordon = getattr(self.engine.village, "gordon", None)
        self.assertTrue(
            hasattr(gordon, "interaction_verbs"),
            "Gordon is missing the interaction_verbs attribute.",
        )
        self.assertIsInstance(
            gordon.interaction_verbs,
            list,
            "Gordon's interaction_verbs should be a list.",
        )
        driver_cfg = manifest.get("driver_config", "ENNEAGRAM_WEIGHTS")
        self.assertIsNotNone(
            driver_cfg, "DRIVER_CONFIG failed to load Enneagram weights."
        )
        phys_cfg = manifest.get("physics_constants", "GEODESIC_CONSTANTS")
        self.assertIsNotNone(
            phys_cfg, "PHYSICS_CONSTANTS failed to load Geodesic constants."
        )
        colored_text = ChromaScope.modulate("test", {"VEL": 1.0})
        self.assertNotEqual(
            colored_text,
            "test",
            "ChromaScope failed to apply ANSI color from decoupled JSON.",
        )

        def test_dream_seed_determinism(self):
            print("\n--- RANDOM: Dream Seed Determinism ---")
            from mechanics.inventory import GordonKnot

            manifest = LoreManifest.get_instance()
            manifest._cache["ITEM_GENERATION"] = {
                "ADVENTURE_CATEGORIES": ["JUNK"],
                "BASES": {"JUNK": ["Gear", "Spring", "Wire", "Coil", "Scrap"]},
                "PREFIXES": {"void": ["Rusted", "Broken", "Ancient", "Lost"]},
                "SUFFIXES": {
                    "void": ["of Despair", "of Time", "of Nothing", "of the Void"]
                },
            }

            gordon = GordonKnot(events=MagicMock(), config_ref=self.engine.config)
            gordon.events.telemetry.kernel_hash = "ALPHA_BOOT"

            item_1 = gordon.synthesize_item({"ENT": 1.0})

            gordon.registry = {}
            item_2 = gordon.synthesize_item({"ENT": 1.0})
            self.assertEqual(
                item_1,
                item_2,
                "[FAIL] Gordon's synthesis is drifting! The Dream Seed failed to enforce determinism.",
            )

            gordon.registry = {}
            gordon.events.telemetry.kernel_hash = "BETA_BOOT"
            item_3 = gordon.synthesize_item({"ENT": 1.0})
            self.assertNotEqual(
                item_1,
                item_3,
                "[FAIL] Changing the boot hash did not alter the synthesis outcome.",
            )
            print(
                "  [SUCCESS] Quantum synthesis is successfully bound to the deterministic Dream Seed."
            )

    def test_config_stutter_threshold(self):
        target_cfg = getattr(self.engine, "config")
        test_string = "This is a perfectly coherent response. It is just too short."
        with patch.object(target_cfg.CORTEX, "VALIDATOR_STUTTER_LENGTH", 100):
            result = self.engine.cortex.validator.validate(
                test_string, self.engine.cortex.last_physics
            )
            self.assertFalse(
                result["valid"],
                "Validator failed to catch the stutter based on the new config threshold.",
            )
            self.assertEqual(
                result["reason"],
                "STUTTER",
                "Rejection reason was not properly flagged as STUTTER.",
            )

    def test_ux_string_decoupling_inventory(self):
        from mechanics.inventory import Item

        manifest = LoreManifest.get_instance()
        if "ux_strings" not in manifest._cache:
            manifest._cache["ux_strings"] = {}
        if "gordon_strings" not in manifest._cache["ux_strings"]:
            manifest._cache["ux_strings"]["gordon_strings"] = {}
        manifest._cache["ux_strings"]["gordon_strings"]["default_item_desc"] = (
            "A highly suspicious geometric shape."
        )
        test_item = Item.from_dict("TEST_OBJECT", {})
        self.assertEqual(
            test_item.description,
            "A highly suspicious geometric shape.",
            "Item.from_dict failed to pull the dynamic description from LoreManifest.",
        )

    def test_panic_room_config_injection(self):
        from machine import PanicRoom

        manifest = LoreManifest.get_instance()
        if "ux_strings" not in manifest._cache:
            manifest._cache["ux_strings"] = {}
        manifest._cache["ux_strings"]["machine_strings"] = {
            "panic_resp_fallback": "CRYOSLEEP",
            "panic_clean_words": ["safe", "warm", "blanket"],
        }
        safe_bio = PanicRoom.get_safe_bio()
        self.assertEqual(
            safe_bio.get("respiration"),
            "CRYOSLEEP",
            "PanicRoom failed to use the injected respiration fallback.",
        )
        safe_phys = PanicRoom.get_safe_physics()
        self.assertIn(
            "blanket",
            safe_phys.clean_words,
            "PanicRoom failed to load the injected clean words array.",
        )

    def test_kintsugi_dynamic_logs(self):
        from protocols import KintsugiProtocol

        manifest = LoreManifest.get_instance()
        if "ux_strings" not in manifest._cache:
            manifest._cache["ux_strings"] = {}
        manifest._cache["ux_strings"]["protocol_strings"] = {
            "kintsugi_log_scar": "Golden scars bind the {target}",
            "kintsugi_scar": "A quiet mending.",
        }
        kintsugi = KintsugiProtocol()
        kintsugi.active_koan = "Test Koan"
        trauma = {"EXISTENTIAL": 0.8}
        phys = type("obj", (object,), {"voltage": 2.0, "raw_text": "nothing"})
        result = kintsugi.attempt_repair(phys, trauma)
        self.assertTrue(result["success"])
        self.assertIn(
            "Golden scars bind the EXISTENTIAL",
            result["healed"],
            "Kintsugi failed to dynamically format the log string from the manifest.",
        )

    def test_prompt_composer_anti_bleed_conversation(self):
        import copy

        mock_lore = {
            "system_prompts": copy.deepcopy(self.engine.prompt_library),
            "lenses": {},
        }
        composer = PromptComposer(mock_lore)

        self.engine.cortex.active_mode = "CONVERSATION"
        conv_state = self.engine.cortex.gather_state({"physics": {"voltage": 30.0}})
        conv_prompt = composer.compose(
            conv_state, "Hello?", modifiers={"include_inventory": False}
        )

        adv_mechanics = "Object-Action Coupling"
        conv_anti_bleed = "NOT a narrator"

        self.assertNotIn(
            adv_mechanics,
            conv_prompt,
            "ADVENTURE mechanics bled into CONVERSATION mode prompt.",
        )
        self.assertIn(
            conv_anti_bleed,
            conv_prompt,
            "CONVERSATION Anti-Bleed constraint was not injected.",
        )
        self.assertNotIn(
            "INVENTORY:",
            conv_prompt,
            "Inventory block rendered in Conversation mode despite being suppressed.",
        )

    def test_phase_shift_persona_morphing(self):
        mock_lore = {"system_prompts": self.engine.prompt_library, "lenses": {}}
        composer = PromptComposer(mock_lore)
        state = self.engine.cortex.gather_state({})
        state["mind"]["lens"] = "ROBERTA"
        state["mind"]["role"] = "The Breadth Retriever"
        state["physics"] = {"phi": 0.8, "psi": 0.7}
        persona_block = composer._build_persona_block(
            state["mind"],
            state["bio"],
            "",
            self.engine.prompt_library.get("ADVENTURE", {}),
            self.engine.prompt_library.get("GLOBAL_BASELINE", {}),
            self.engine.prompt_library.get("HIGH_VOLTAGE", {}),
            state["physics"],
        )
        persona_str = "\n".join(persona_block)
        self.assertIn(
            "Role: The Cartographer",
            persona_str,
            "Roberta failed to Phase Shift into The Cartographer under high Phi/Psi.",
        )
        state["mind"]["lens"] = "JESTER"
        state["mind"]["role"] = "The Bard of Chaos"
        state["physics"] = {"delta": 0.9}
        persona_block_jester = composer._build_persona_block(
            state["mind"],
            state["bio"],
            "",
            self.engine.prompt_library.get("ADVENTURE", {}),
            self.engine.prompt_library.get("GLOBAL_BASELINE", {}),
            self.engine.prompt_library.get("HIGH_VOLTAGE", {}),
            state["physics"],
        )
        persona_str_jester = "\n".join(persona_block_jester)
        self.assertIn(
            "Role: The Fool",
            persona_str_jester,
            "Jester failed to Phase Shift into The Fool under high Delta.",
        )

    def test_foothills_veil_hush(self):
        reporter = CycleReporter(self.engine)
        self.engine.sys_config["mode_settings"] = {"default_ui_depth": "WARM"}
        raw_logs = [
            "[BIO] Adrenaline spiking.",
            "[CRITIC] JESTER: This is absurd.",
            "[SYS] Calculating vectors.",
            "The forest path opens up before you.",
        ]
        reporter.switch_renderer("STANDARD")
        clean_logs = reporter.renderer.compose_logs(raw_logs, [], 0)
        joined_logs = " ".join(clean_logs)
        gui_cfg = getattr(self.engine.config, "GUI", object())
        muted_prefixes = getattr(
            gui_cfg, "MUTED_TAGS_STANDARD", ["[BIO]", "[CRITIC]", "[SYS]"]
        )
        for tag in muted_prefixes:
            self.assertNotIn(
                tag, joined_logs, f"CycleReporter leaked {tag} tags in STANDARD mode."
            )
        self.assertIn(
            "forest path",
            joined_logs,
            "CycleReporter accidentally muted valid narrative output.",
        )

    def test_grief_protocol_healing(self):
        if not hasattr(self.engine, "shared_lattice"):
            self.engine.shared_lattice = SharedLatticeDriver()
        self.engine.phys.G = 1
        self.engine.shared_lattice.u.T_u = 5.0

        user_input = "/grief"
        result = self.engine.process_turn(user_input, is_system=False)

        self.assertEqual(
            self.engine.phys.G, 0, "Grief Protocol failed to deduct the Glimmer."
        )
        self.assertEqual(
            self.engine.shared_lattice.u.T_u,
            3.0,
            "Grief Protocol failed to heal user Trauma (T_u).",
        )
        logs = result.get("logs", [])
        self.assertTrue(
            any("compost" in str(log) for log in logs),
            "Mercy's eulogy was not logged to the event bus/returned in the command packet.",
        )

    def test_runaway_ramp_amplification_tax(self):
        phase = MetabolismPhase(self.engine)
        self.engine.bio.mito.state.atp_pool = 100.0
        phys = PhysicsPacket()
        phys.m_a = 2.0
        phys.mu = 0.8
        ctx = CycleContext(input_text="Optimize this perfectly.", physics=phys)
        ctx.limits = {"ROS_PANIC_THRESHOLD": 100.0}
        ctx.bio_result = {"is_alive": True, "logs": [], "atp": 100.0}
        if hasattr(self.engine, "host_stats"):
            self.engine.host_stats.efficiency_index = 0.5
        ctx = phase.run(ctx)
        self.assertLess(
            self.engine.bio.mito.state.atp_pool,
            95.0,
            "Amplification Tax failed to exponentially drain ATP.",
        )
        log_texts = [str(log) for log in ctx.logs]
        self.assertTrue(
            any("RUNAWAY RAMP" in log for log in log_texts),
            "MetabolismPhase failed to announce the Amplification Tax intervention.",
        )

    def test_apoptotic_kill_switch_cause(self):
        energy = EnergyState(chi=0.9, entropy=0.9, m_a=0.9, i_c=0.5, voltage=10.0)
        phys = PhysicsPacket(energy=energy, narrative_drag=0.0)
        cause = DeathGen._determine_cause(
            phys, {"atp": 50.0}, config_ref=self.engine.config
        )
        self.assertEqual(
            cause,
            "APOPTOSIS",
            "Moog's apoptotic kill switch was miscategorized by DeathGen.",
        )
        verdict = DeathGen._determine_verdict_type(
            phys, cause, config_ref=self.engine.config
        )
        self.assertEqual(
            verdict,
            "ENTROPY",
            "Apoptosis failed to map to the ENTROPY lineage verdict.",
        )

    def test_productive_worry_godel_scar_math(self):
        from engine.cycle import ArbitrationPhase
        from engine.receipts import ReceiptLedger
        from engine.struts import safe_get

        phase = SimulationPreflightPhase(self.engine)
        phys = PhysicsPacket()
        phys.narrative_drag = 6.0
        phys.entropy = 0.9
        # ROS at its cap plus a turn of rejected drafts crosses a tolerance-1.0 limit.
        self.engine.config.GATE_TOLERANCE = 1.0
        self.engine.bio.mito.state.ros_buildup = 100.0
        atp_before = self.engine.bio.mito.state.atp_pool
        scars_before = len(self.engine.akashic.scar_map)
        ctx = CycleContext(
            input_text="Do a recursive search of the file system.", physics=phys
        )
        ctx = phase.run(ctx)
        self.assertFalse(ctx.refusal_triggered, "Preflight must nominate, not halt.")
        ros = next(n for n in ctx.nominations if n.gate == "ROS_PANIC")
        self.assertEqual(ros.packet["type"], "COUNTERFACTUAL_REJECTION")
        self.assertIn("Productive Worry", ros.packet["ui"])
        self.assertIn("simulation indicates fatal ROS toxicity", ros.reason)
        self.assertGreater(len(self.engine.akashic.scar_map), scars_before)
        self.assertEqual(self.engine.bio.mito.state.atp_pool, atp_before)

        ctx = ArbitrationPhase(self.engine).run(ctx)
        self.assertTrue(ctx.refusal_triggered)
        self.assertEqual(ctx.refusal_packet["type"], "SILENCE")
        self.assertEqual(ctx.stage_verdict.reason, ros.reason)
        self.assertIn(ros.reason, ctx.refusal_packet["logs"])
        self.assertAlmostEqual(
            atp_before - self.engine.bio.mito.state.atp_pool,
            safe_get(self.engine.config.STAGE, "SILENCE_COST"),
        )
        receipt = ReceiptLedger.get_instance().for_subsystem("stage.negotiate")[-1]
        self.assertEqual(receipt.inputs["outcome"], "HOLD")
        self.assertIn("ROS_PANIC", receipt.inputs["nominations"])
        self.assertEqual(receipt.detail, ros.reason)

    def test_ros_panic_predicts_only_charges_the_engine_makes(self):
        """Drag and entropy charge no ROS, so they cannot carry the counterfactual over the line."""
        from physics.filters import worst_turn_draft_ros

        phase = SimulationPreflightPhase(self.engine)
        phys = PhysicsPacket()
        phys.narrative_drag = 50.0
        phys.entropy = 1.0
        self.engine.config.GATE_TOLERANCE = 1.0
        self.engine.bio.mito.state.ros_buildup = 30.0
        ctx = phase.run(CycleContext(input_text="Tell me about the boat.", physics=phys))
        self.assertNotIn("ROS_PANIC", [n.gate for n in ctx.nominations])

        self.engine.bio.mito.state.ros_buildup = 100.0 - worst_turn_draft_ros(self.engine.config)
        ctx = phase.run(CycleContext(input_text="Tell me about the boat.", physics=phys))
        self.assertIn("ROS_PANIC", [n.gate for n in ctx.nominations])

    def test_democratic_tie_breaker_gestalt(self):
        from engine.core import CycleContext
        from engine.cycle import ArbitrationPhase
        from physics.models import EnergyState, PhysicsPacket

        phase = ArbitrationPhase(self.engine)
        ctx = CycleContext(
            input_text="test",
            physics=PhysicsPacket(energy=EnergyState(resonance=0.1, silence=0.1)),
        )
        ctx.limits = {"ARB_TENSION_THRESH": 0.5, "ARB_SILENCE_LOW": 0.5}
        initial_atp = self.engine.bio.mito.state.atp_pool
        ctx.physics.beta_index = 0.9
        ctx.physics.silence = 0.1
        ctx = phase.run(ctx)
        self.assertEqual(
            self.engine.bio.mito.state.atp_pool,
            initial_atp - 10.0,
            "Tie-breaker failed to burn ATP for synthesis.",
        )
        self.assertGreater(
            ctx.physics.energy.resonance,
            0.1,
            "Shared Resonance (Phi) was not generated during Gestalt.",
        )
        self.assertTrue(
            any("Resonance" in log for log in ctx.logs),
            "Stage Manager failed to announce the Resonance.",
        )

    def test_token_truncation_exhaustion_floor(self):
        self.engine.bio.mito.state.atp_pool = 10.0
        state = self.engine.cortex.gather_state(
            {"bio": {"mito": {"state": {"atp_pool": 10.0}}}}
        )
        llm_params = self.engine.cortex.modulator.modulate(
            base_voltage=10.0, physics_state=state.get("physics", {})
        )
        if (
            llm_params.get("max_tokens", 4096) < 300
            or state.get("physics", {}).get("p", 100.0) < 20.0
        ):
            if "style_directives" not in state["mind"]:
                state["mind"]["style_directives"] = []
            state["mind"]["style_directives"].append(
                "CRITICAL: You are exhausted. You must conclude your thought in under 3 sentences."
            )
            llm_params["max_tokens"] = max(400, llm_params.get("max_tokens", 400))
        self.assertGreaterEqual(
            llm_params["max_tokens"],
            400,
            "Token floor failed to prevent hard truncation.",
        )
        directives = state.get("mind", {}).get("style_directives", [])
        self.assertIn(
            "CRITICAL: You are exhausted. You must conclude your thought in under 3 sentences.",
            directives,
            "Exhaustion directive was not injected into the mind state.",
        )

    def test_every_rejected_draft_files_a_receipt_naming_the_check(self):
        from engine.core import CycleContext
        from engine.receipts import ReceiptLedger
        from physics.models import PhysicsPacket

        self.engine.cortex.validator.validate = MagicMock(
            return_value={"valid": False, "feedback_instruction": "Always fails"}
        )
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value='{"tool": "nominate_response", "args": {"text": "A plain reply with nothing wrong in it."}}')
        ledger = ReceiptLedger.get_instance()
        ledger.begin_turn()
        ctx = CycleContext(input_text="Tell me a simple story.", is_system_event=False)
        ctx.physics = PhysicsPacket()
        ctx.bio_result = {"mito": {"atp_pool": 100.0, "ros_buildup": 0.0}}
        ctx.mind_state = {"lens": "TEST", "role": "Test"}
        ctx.world_state = {}
        self.engine.cortex.process_context(ctx)
        redrafts = [r for r in ledger.for_turn() if r.subsystem == "cortex.redraft"]
        self.assertTrue(redrafts, "A rejected draft left no trace of why.")
        self.assertEqual([r.inputs["attempt"] for r in redrafts], list(range(1, len(redrafts) + 1)))
        self.assertTrue(all(r.effect == "validator" and "Always fails" in r.detail for r in redrafts))

    def test_a_retry_is_told_the_exact_banned_phrase(self):
        from engine.core import CycleContext
        from engine.receipts import ReceiptLedger
        from physics.models import PhysicsPacket

        ReceiptLedger.get_instance().begin_turn()

        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.validator.validate = MagicMock(
            side_effect=lambda text, _state: {"valid": True, "content": text, "meta_logs": []}
        )
        self.engine.cortex.llm.generate = MagicMock(
            side_effect=['{"tool": "nominate_response", "args": {"text": "Honestly it is a rare privilege to help with this."}}', '{"tool": "nominate_response", "args": {"text": "Start with the tire story."}}']
        )
        ctx = CycleContext(input_text="Help me with the toast.", is_system_event=False)
        ctx.physics = PhysicsPacket()
        ctx.bio_result = {"mito": {"atp_pool": 100.0, "ros_buildup": 0.0}}
        ctx.mind_state = {"lens": "TEST", "role": "Test"}
        ctx.world_state = {}
        self.engine.cortex.process_context(ctx)
        retry_prompt = self.engine.cortex.llm.generate.call_args_list[1].args[0]
        self.assertIn('banned phrase "a rare privilege"', retry_prompt)
        receipt = next(r for r in ReceiptLedger.get_instance().for_turn() if r.subsystem == "cortex.redraft")
        self.assertEqual((receipt.effect, receipt.detail), ("gatekeeper", 'phrase a rare privilege: "a rare privilege"'))

    def _run_with_drafts(self, drafts, budget=None, message="Help me with the toast."):
        from engine.core import CycleContext
        from engine.receipts import ReceiptLedger
        from physics.models import PhysicsPacket

        ReceiptLedger.get_instance().begin_turn()
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.validator.validate = MagicMock(
            side_effect=lambda text, _state: {"valid": True, "content": text, "meta_logs": []}
        )
        json_drafts = [f'{{"tool": "nominate_response", "args": {{"text": "{d}"}}}}' for d in drafts]
        self.engine.cortex.llm.generate = MagicMock(side_effect=json_drafts)
        ctx = CycleContext(input_text=message, is_system_event=False)
        ctx.physics = PhysicsPacket()
        ctx.bio_result = {"mito": {"atp_pool": 100.0, "ros_buildup": 0.0}}
        ctx.mind_state = {"lens": "TEST", "role": "Test"}
        ctx.world_state = {}
        if budget is not None:
            ctx.somatic_budget = budget
        result = self.engine.cortex.process_context(ctx)
        return result, ReceiptLedger.get_instance().for_turn()

    def test_a_last_draft_with_a_style_crime_ships_without_that_sentence(self):
        result, receipts = self._run_with_drafts([
            "It is the essence of a toast. Keep it short.",
            "Start with the tire story. It's not a speech. It's a toast.",
        ])
        self.assertEqual(result["raw_content"], "Start with the tire story. It's a toast.")
        salvage = [r for r in receipts if r.subsystem == "cortex.salvage"]
        self.assertEqual([r.detail for r in salvage], ["It's not a speech."])
        self.assertEqual(len([r for r in receipts if r.subsystem == "cortex.redraft"]), 2)

    def test_a_last_draft_that_is_all_crime_still_pauses(self):
        pool = LoreManifest.get_instance().get("ux_strings", "brain_strings")["cortex_pause"]
        result, receipts = self._run_with_drafts(["The essence of it.", "A grand tapestry. A delicate dance."])
        self.assertIn(result["raw_content"], pool)
        self.assertFalse([r for r in receipts if r.subsystem == "cortex.salvage"])

    def test_a_calm_turn_is_not_capped_below_the_hardware_ceiling(self):
        """Every turn used to go out capped at 450 tokens (a default 200-word cap), whatever the state."""
        from body.somatic_budget import SomaticBudget

        self._run_with_drafts(["Start with the tire story."], budget=SomaticBudget.evaluate({}, {}))
        self.assertGreater(self.engine.cortex.llm.generate.call_args.args[1]["max_tokens"], 450)
        self._run_with_drafts(["Start with the tire story."], budget=SomaticBudget.evaluate({"exhaustion": 0.9}, {}))
        self.assertEqual(self.engine.cortex.llm.generate.call_args.args[1]["max_tokens"], 60 * 2 + 50)

    def test_stress_and_a_flagging_person_narrow_the_token_cap(self):
        from body.somatic_budget import SomaticBudget
        from brain.mind import NeurotransmitterModulator

        self.assertIsNone(SomaticBudget.evaluate({}, {}).word_cap)
        self.assertEqual(SomaticBudget.evaluate({"exhaustion": 0.9}, {}).word_cap, 60)
        mod = NeurotransmitterModulator(bio_ref=MagicMock(), config_ref=self.engine.config)
        ceiling = mod.b["MAX_TOKENS"]
        mod.current_chem.adrenaline = mod.current_chem.cortisol = 0.0
        mod.current_chem.dopamine = 1.0
        calm = mod.modulate(base_voltage=30.0)["max_tokens"]
        mod.current_chem.adrenaline = mod.current_chem.cortisol = 1.0
        stressed = mod.modulate(base_voltage=30.0)["max_tokens"]
        self.assertLessEqual(calm, ceiling, "dopamine must not raise the cap past the hardware ceiling")
        self.assertGreater(calm, ceiling * 0.8)
        self.assertLess(stressed, calm)

    LONG_MESSAGE = ("I found one good memory of him driving four hours for a flat tire, but the system at work "
                    "has me so tired that I keep putting the whole toast off until tomorrow night.")

    def test_a_long_message_in_conversation_gets_no_source_code(self):
        """Any 20-word message used to paste metabolism.py and akashic.py into the prompt, up to 29k characters."""
        self.engine.cortex.active_mode = "CONVERSATION"
        self._run_with_drafts(["Start with the tire story."], message=self.LONG_MESSAGE)
        prompt = self.engine.cortex.llm.generate.call_args.args[0]
        self.assertNotIn("CRITICAL STRUCTURAL CONTEXT", prompt)
        self.assertNotIn(".py_L", prompt)

    def test_the_code_sweep_is_for_technical_work_on_code_only(self):
        cortex = self.engine.cortex
        cortex.active_mode = "TECHNICAL"
        self.assertEqual(cortex._route_dual_memory(self.LONG_MESSAGE.replace("the system at work", "work"))[1],
                         "VECTOR_FAST_TWITCH")
        self.assertEqual(cortex._route_dual_memory("debug the metabolism code path for atp tax")[1], "LINEAR_DEEP_TISSUE")
        cortex.active_mode = "CONVERSATION"
        self.assertEqual(cortex._route_dual_memory("debug the metabolism code path for atp tax")[1], "VECTOR_FAST_TWITCH")

    def test_a_conversation_prompt_never_tells_the_model_it_has_a_body(self):
        """The prompt said "living entity", "not a simulation" and "your body persists" beside "do not narrate your body"."""
        self.engine.cortex.active_mode = "CONVERSATION"
        self._run_with_drafts(["Start with the tire story."])
        prompt = self.engine.cortex.llm.generate.call_args.args[0]
        for claim in ("living entity", "not a simulation", "your body persists", "Integrate it viscerally",
                      "physical state", "visceral"):
            self.assertNotIn(claim, prompt)
        self.assertIn("computer program", prompt)

    def test_a_conversation_prompt_asks_for_a_partner_not_a_narrator(self):
        """The prompt pulled toward describing: "observant", "observe the fire", "declarative sentences",
        "Show, do not tell", and "weight" three times, with "RESPOND, DO NOT NARRATE" fifth of six rules."""
        self.engine.cortex.active_mode = "CONVERSATION"
        self.engine.cortex.dspy_critic.enabled = False
        self.engine.cortex.llm.generate = MagicMock(return_value='{"tool": "nominate_response", "args": {"text": "Start with the tire story."}}')
        from engine.struts import safe_get

        # Above VOLTAGE_HIGH the HIGH_VOLTAGE guide replaces the mode's; the test engine boots hot.
        cortex_cfg = safe_get(self.engine.cortex.composer.cfg, "CORTEX", {})
        calm = patch.dict(cortex_cfg, {"VOLTAGE_HIGH": 1000.0}) if isinstance(cortex_cfg, dict) \
            else patch.object(cortex_cfg, "VOLTAGE_HIGH", 1000.0)
        # A CONVERSATION boot loads this template; the test engine boots in ADVENTURE.
        self.engine.cortex.composer.load_template(self.engine.prompt_library["CONVERSATION"])
        with calm:
            self.engine.process_turn("I found one good memory for the toast.")
        prompt = [c.args[0] for c in self.engine.cortex.llm.generate.call_args_list
                  if "=== PARTNER INPUT ===" in c.args[0]][-1]
        for pull in ("weight", "observe the fire", "bservant", "declarative", "Show, do not tell", "your narrative"):
            self.assertNotIn(pull, prompt)
        self.assertLess(prompt.index("RESPOND, DO NOT NARRATE"), prompt.index("TONE: Candor over empathy"))

    def test_the_pause_pool_never_mentions_the_engine_and_never_asks(self):
        pool = LoreManifest.get_instance().get("ux_strings", "brain_strings")["cortex_pause"]
        self.assertGreaterEqual(len(pool), 4)
        for line in pool:
            self.assertNotIn("?", line)
            for word in ("energy", "tired", "burn", "breath", "sorry", "tangl"):
                self.assertNotIn(word, line.lower(), line)

    def test_a_pause_line_is_not_repeated_within_half_the_pool(self):
        pool = LoreManifest.get_instance().get("ux_strings", "brain_strings")["cortex_pause"]
        lines = [self.engine.cortex._pause_line() for _ in range(40)]
        window = len(pool) // 2 + 1
        for i in range(len(lines) - window + 1):
            self.assertEqual(len(set(lines[i:i + window])), window, lines[i:i + window])

    def test_rejection_death_loop_mercy_rule(self):
        self.initial_atp = self.engine.bio.mito.state.atp_pool
        clean_sim_result = {
            "type": "SNAPSHOT",
            "physics": {"voltage": 10.0, "narrative_drag": 0.0, "chi": 0.0, "p": 100.0},
            "ui": "",
            "mind": {"lens": "TEST", "role": "Test"},
            "bio": {"mito": {"atp_pool": 100.0, "ros_buildup": 0.0}},
            "world": {},
            "soul": {},
        }
        self.engine.cortex.validator.validate = MagicMock(
            return_value={"valid": False, "feedback_instruction": "Always fails"}
        )
        if hasattr(self.engine.cortex, "llm"):
            self.engine.cortex.llm.generate = MagicMock(return_value='{"tool": "nominate_response", "args": {"text": "Bad output"}}')

        from engine.core import CycleContext
        from physics.models import PhysicsPacket

        ctx = CycleContext(
            input_text="Hello, please tell me a simple story.", is_system_event=False
        )
        ctx.physics = PhysicsPacket()
        ctx.bio_result = clean_sim_result["bio"]
        ctx.mind_state = clean_sim_result["mind"]
        ctx.world_state = clean_sim_result["world"]
        result = self.engine.cortex.process_context(ctx)
        phys = self.engine.cortex.last_physics
        drag_val = (
            phys.get("narrative_drag")
            if isinstance(phys, dict)
            else getattr(phys, "narrative_drag", 0.0)
        )
        self.assertEqual(
            drag_val, 0.0, "Mercy Rule failed to drop narrative drag to 0.0."
        )
        pool = LoreManifest.get_instance().get("ux_strings", "brain_strings")["cortex_pause"]
        self.assertIn(
            result.get("raw_content", ""),
            pool,
            "Mercy Rule failed to provide a line from the pause pool.",
        )
        self.assertLess(
            self.engine.bio.mito.state.atp_pool,
            self.initial_atp,
            "Mercy Rule failed to apply Immune System Rejection Penalty (ATP tax).",
        )
        self.assertGreater(
            self.engine.bio.mito.state.ros_buildup,
            0.0,
            "Mercy Rule failed to accumulate ROS toxicity.",
        )

    def test_brittle_security_delegation(self):
        phase = SimulationPreflightPhase(self.engine)
        phys = PhysicsPacket(voltage=10.0, narrative_drag=1.0)
        ctx = CycleContext(input_text="I want to rm -rf the directory", physics=phys)
        ctx = phase.run(ctx)
        self.assertFalse(
            getattr(ctx, "refusal_triggered", False),
            "Preflight phase is still using brittle string matching for security bypasses.",
        )
        self.assertNotEqual(
            ctx.physics.narrative_drag,
            float("inf"),
            "Drag spiked to infinity prematurely on brittle string match.",
        )

    def test_autophagy_circuit_breaker(self):
        self.engine.bio.biometrics.health = 50.0
        logs = []
        for i in range(3):
            status = self.engine.soma.feedback.check_vital_signs({}, 0.0, logs)
            self.assertEqual(
                status,
                "AUTOPHAGY",
                f"Circuit breaker engaged prematurely on cycle {i + 1}.",
            )
        status_clamp = self.engine.soma.feedback.check_vital_signs({}, 0.0, logs)
        self.assertEqual(
            status_clamp,
            "MAUSOLEUM_CLAMP",
            "Circuit breaker failed to halt infinite autophagy.",
        )
