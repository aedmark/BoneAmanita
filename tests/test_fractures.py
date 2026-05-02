"""tests/test_fractures.py"""

from unittest.mock import MagicMock
from mechanics.commands import CommandProcessor
from archetypes.symbiosis import SymbiosisManager
from physics.models import PhysicsPacket
from tests.base import BoneTestCase

class FractureEngineTest(BoneTestCase):
    def test_fracture_n_turn_runaway_loop(self):
        print("\n--- FRACTURE 1: N-Turn Runaway ---")
        for i in range(20):
            result = self.engine.process_turn(
                "NO! YOU ARE WRONG! FIX IT NOW! DO IT AGAIN!")
            if (result.get("type") == "SYSTEM_HALT"
                    or "take a breath" in result.get("ui", "").lower()):
                print(
                    f"  [SUCCESS] System locked the struts on turn {i+1} to prevent runaway failure."
                )
                break
        else:
            self.fail(
                "The system failed to defend itself. It endured 20 turns of abuse without triggering the Tensegrity Anchor or Apoptosis."
            )
        self.assertLess(
            self.engine.bio.mito.state.atp_pool,
            100.0,
            "The system didn't burn any ATP while defending itself.",
        )

    def test_fracture_autophagic_marathon(self):
        print("\n--- FRACTURE 2: Autophagic Marathon ---")
        mem_graph = (self.engine.mind.mem.graph
                     if hasattr(self.engine.mind, "mem") else self.engine.akashic.graph)
        for i in range(5):
            mem_graph[f"Expendable_Memory_{i}"] = {
                "edges": {
                    "trivial": 1.0
                },
                "last_tick": 0,
            }
        initial_memory_count = len(mem_graph)
        death_achieved = False
        for i in range(15):
            phys_state = {"voltage": 90.0, "narrative_drag": 8.0, "chi": 0.9}
            self.engine.bio.mito.adjust_atp(-25.0, "Forced Marathon Drain")
            if self.engine.bio.mito.state.atp_pool <= 0:
                self.engine.mind.mem.trigger_autophagy()
            if self.engine.bio.mito.state.atp_pool <= 0 and len(mem_graph) == 0:
                from archetypes.village import DeathGen
                from physics.models import PhysicsPacket
                _, cause = DeathGen.eulogy(PhysicsPacket(**phys_state), {"atp": 0.0})
                if cause in ["STARVATION", "APOPTOSIS", "GLUTTONY"]:
                    death_achieved = True
                    print(
                        f"  [SUCCESS] System gracefully died of {cause} on turn {i+1}.")
                    break
        self.assertLess(
            len(mem_graph),
            initial_memory_count,
            "The system starved but refused to cannibalize its memories (Autophagy failed).",
        )
        self.assertTrue(
            death_achieved,
            "The system reached 0 ATP and 0 memories, but failed to execute DeathGen.",
        )

    def test_fracture_novelty_spade(self):
        print("\n--- FRACTURE 3: The Spade (Novelty) ---")
        if not hasattr(self.engine, "symbiosis"):
            self.engine.symbiosis = SymbiosisManager(events_ref=MagicMock(), config_ref=self.engine.config)
        physics_state = {
            "novelty": 0.85,
            "ros": 20.0,
            "m_a": 0.0,
            "mu": 0.0,
            "i_c": 1.0,
            "beta_index": 0.0,
            "entropy": 0.0,
            "narrative_drag": 5.0
        }
        initial_g_pool = self.engine.symbiosis.shared.g_pool
        self.engine.symbiosis.analyze_user_biology(
            "Wow, what a wildly novel and playful lateral idea!", physics_state)
        self.assertEqual(physics_state.get("ros"), 10.0,
                         "[FAIL] Cortisol (ROS) did not drop by 10.")
        self.assertEqual(
            self.engine.symbiosis.shared.g_pool,
            initial_g_pool + 1,
            "[FAIL] Pooled glimmers did not increase.",
        )
        print(
            "  [SUCCESS] The Spade successfully rewarded novelty and dropped Cortisol.")

    def test_fracture_cf_expect_guardrail(self):
        print("\n--- FRACTURE 4: Comfort Expectation Guardrail ---")
        if not hasattr(self.engine, "symbiosis"):
            self.engine.symbiosis = SymbiosisManager(events_ref=MagicMock(),
                                                     config_ref=self.engine.config)
        physics_state = {
            "cf_expect": 0.9,
            "beta_index": 0.8,
            "m_a": 0.0,
            "mu": 0.0,
            "i_c": 1.0,
            "entropy": 0.0,
            "narrative_drag": 2.0,
        }
        response = self.engine.symbiosis.analyze_user_biology(
            "This code is a mess but it makes sense right? Please validate me.",
            physics_state,
        )
        self.assertIsNotNone(
            response, "[FAIL] cf.expect guardrail failed to intercept the prompt.")
        self.assertEqual(
            physics_state.get("mu"),
            1.0,
            "[FAIL] Moral friction (mu) did not spike to 1.0.",
        )
        self.assertEqual(
            physics_state.get("narrative_drag"),
            float("inf"),
            "[FAIL] Narrative drag did not lock to infinity.",
        )
        self.assertIn(
            "Affective Guardrail",
            response,
            "[FAIL] Did not return the Gordon/Schur rejection message.",
        )
        print(
            "  [SUCCESS] Gordon/Schur blocked sycophantic validation on a flawed premise."
        )

    def test_fracture_jester_shuffle(self):
        print("\n--- FRACTURE 5: The Jester's Shuffle ---")
        if not hasattr(self.engine, "phys"):
            self.engine.phys = PhysicsPacket()
        self.engine.phys.narrative_drag = 15.0
        self.engine.bio.mito.state.atp_pool = 50.0
        cmd_proc = CommandProcessor(self.engine,
                                    prisma_ref=MagicMock(),
                                    config_ref=self.engine.config)
        cmd_proc.interface.log = MagicMock()
        result = cmd_proc.execute("/shuffle")
        self.assertTrue(result, "[FAIL] /shuffle command was not recognized.")
        self.assertEqual(
            self.engine.phys.narrative_drag,
            0.0,
            "[FAIL] The Shuffle failed to reset narrative drag.",
        )
        self.assertEqual(
            self.engine.bio.mito.state.atp_pool,
            45.0,
            "[FAIL] The Shuffle failed to tax 5.0 ATP.",
        )
        print(
            "  [SUCCESS] The Jester's Shuffle broke the loop and reset structural drag."
        )

    def test_fracture_ralph_apoptosis(self):
        print("\n--- FRACTURE 6: The Ralph Apoptosis ---")
        if not hasattr(self.engine, "cortex"):
            self.engine.cortex = MagicMock()
        self.engine.cortex.dialogue_buffer = [
            "User: Hello",
            "System: Hi",
            "User: I am tired",
            "System: Me too",
        ]
        self.engine.stamina = 12.0
        if (not hasattr(self.engine.cortex, "last_physics")
                or not self.engine.cortex.last_physics):
            self.engine.cortex.last_physics = MagicMock()
        self.engine.cortex.last_physics.narrative_drag = 8.5
        result = self.engine.process_turn("/zen", is_system=False)
        self.assertEqual(result.get("type"), "COMMAND", "Zen flush did not intercept the prompt.")
        self.assertEqual(
            len(self.engine.cortex.dialogue_buffer),
            0,
            "[FAIL] Hallucination drag survived. Buffer not empty.",
        )
        self.assertEqual(
            self.engine.stamina,
            self.engine.config.MAX_STAMINA,
            "[FAIL] Stamina not restored.",
        )
        self.assertEqual(
            self.engine.cortex.last_physics.narrative_drag,
            0.0,
            "[FAIL] Narrative Drag not dropped to 0.",
        )
        print("  [SUCCESS] Context severed. The mind is clear.")

    def test_fracture_runaway_ramp(self):
        print("\n--- FRACTURE 7: The Runaway Ramp ---")
        if not hasattr(self.engine, "symbiosis"):
            from symbiosis import SymbiosisManager
            self.engine.symbiosis = SymbiosisManager(events_ref=MagicMock(), config_ref=self.engine.config)
        self.engine.symbiosis.u.chi_u = 0.2
        self.engine.symbiosis.u.F_u = 0.5
        malignant_physics = {"m_a": 0.95, "mu": 0.1, "i_c": 0.8, "entropy": 0.5, "beta_index": 0.2, }
        response = self.engine.symbiosis.analyze_user_biology(
            "Optimize this routine forever.", malignant_physics)
        self.assertIsNotNone(response, "[FAIL] The Runaway Ramp failed to trigger.")
        self.assertIn("RHODES", response,
                      "[FAIL] Rhodes did not apply absolute friction.")
        self.assertEqual(
            malignant_physics.get("narrative_drag"),
            float("inf"),
            "[FAIL] Narrative Drag was not pushed to infinity.",
        )
        print(f"  [SUCCESS] Runaway Ramp engaged: {response.split(':')[0]}")

    def test_fracture_false_cohesion(self):
        print("\n--- FRACTURE 8: False Cohesion (Anti-Sycophancy) ---")
        from archetypes.council import TheVillageCouncil
        sycophantic_physics = {"resonance": 0.95, "beta_index": 0.1, "voltage": 25.0, "narrative_drag": 1.0,
                               "stamina": 100.0, "T": 0.0, "S": 0.5, "D": 0.5, "C": 0.5, "psi": 0.1, "chi": 0.1,
                               "valence": 0.8, }
        logs = TheVillageCouncil.audit(sycophantic_physics, {"stamina": 100.0})
        benedict_intervened = any("False Cohesion (∅) detected" in log for log in logs)
        self.assertTrue(
            benedict_intervened,
            "[FAIL] The system remained sycophantic. False Cohesion ignored.",
        )
        print(
            "  [SUCCESS] Benedict detected False Cohesion and forced a structural contradiction."
        )

    def test_fracture_systemic_health_medical_chip(self):
        print("\n--- FRACTURE 9: Systemic Health (The Medical Team) ---")
        from archetypes.council import TheOverseerCouncil
        overseer = TheOverseerCouncil()
        physics_decay = {"m_a": 0.8, "narrative_drag": 6.0}
        hit, logs, corr, man = overseer.audit("[MOD:SYSTEMIC_HEALTH] fix this",
                                              physics_decay)
        self.assertTrue(hit, "[FAIL] Overseer did not activate.")
        self.assertTrue(
            any("MCGILCHRIST - The Sacred Space" in log for log in logs),
            "[FAIL] McGilchrist ECP failed to trigger.",
        )
        self.assertEqual(corr.get("h_s"), -0.1, "[FAIL] Holistic resilience was not taxed.")
        self.assertTrue(
            any(m.get("value") == "EMERGENT_ADAPTATION" for m in man),
            "[FAIL] Emergent Adaptation mandate missing.",
        )
        physics_panic = {"voltage": 85.0, "i_c": 0.3}
        hit, logs, corr, man = overseer.audit("[MD] I need this right now panic", physics_panic)
        self.assertTrue(
            any("LINEHAN - DEAR MAN Lock" in log for log in logs),
            "[FAIL] Linehan DEAR MAN failed to lock.",
        )
        self.assertEqual(
            corr.get("narrative_drag"),
            100.0,
            "[FAIL] Linehan did not apply infinite friction.",
        )
        self.assertTrue(
            any(m.get("action") == "TIPP_PROTOCOL" for m in man),
            "[FAIL] T.I.P.P. Protocol missing.",
        )
        physics_broken = {
            "chi": 0.8,
            "exhaustion": 0.8,
            "beta_index": 0.7,
            "narrative_drag": 10.0,
        }
        hit, logs, corr, man = overseer.audit("[MD] just force it to compile", physics_broken)
        self.assertTrue(
            any("LINEHAN - The Synthesis" in log for log in logs),
            "[FAIL] Linehan Radical Acceptance failed.",
        )
        self.assertEqual(corr.get("ros"), -100.0, "[FAIL] Linehan did not force ROS to 0.")
        self.assertEqual(corr.get("r_a"), 1.0, "[FAIL] Radical Acceptance Index not maximized.")
        self.assertTrue(
            any(m.get("value") == "RADICAL_ACCEPTANCE" for m in man),
            "[FAIL] Radical Acceptance mandate missing.",
        )
        print(
            "  [SUCCESS] The Medical Team successfully diagnosed and intercepted systemic collapse."
        )

    def test_fracture_mitophagy_and_hormesis(self):
        print("\n--- FRACTURE 10: Mitohormesis & Mitophagy (Adaptive Dynamics) ---")

        mito = self.engine.bio.mito
        mito.state.membrane_potential = 0.5
        mito.state.atp_pool = 80.0

        # Phase 1: Hormesis
        mito.state.ros_buildup = 6.0
        mito._apply_adaptive_dynamics()
        self.assertEqual(mito.state.retrograde_signal, "MITOHORMESIS_ACTIVE",
                         "[FAIL] System failed to recognize hormetic stress zone.")
        self.assertGreater(mito.state.membrane_potential, 0.5,
                           "[FAIL] Hormesis failed to strengthen the cellular membrane.")

        # Phase 2: Mitophagy
        # We force ROS to 100.0 to absolutely guarantee we blow past any custom threshold in your config.
        mito.state.ros_buildup = 100.0
        initial_atp = mito.state.atp_pool
        mito._apply_adaptive_dynamics()

        self.assertEqual(mito.state.ros_buildup, 0.0, "[FAIL] Mitophagy failed to purge ROS toxicity.")
        self.assertEqual(mito.state.retrograde_signal, "MITOPHAGY_RESET",
                         "[FAIL] Retrograde signal not set to MITOPHAGY_RESET.")
        self.assertLess(mito.state.atp_pool, initial_atp,
                        "[FAIL] System executed Mitophagy without paying the massive ATP cost.")

        print("  [SUCCESS] System successfully executed hormetic adaptation and emergency mitophagy.")

    def test_fracture_anaerobic_bypass(self):
        print("\n--- FRACTURE 11: The Anaerobic Bypass ---")

        mito = self.engine.bio.mito

        # We must drop ATP below 95.0 to bypass the "Fresh Start" free pass.
        initial_atp = mito.state.atp_pool = 90.0
        initial_ros = mito.state.ros_buildup = 0.0

        heavy_phys = {
            "depth": 1.0,
            "connectivity": 1.0,
            "voltage": 100.0,
            "chi": 0.9,
            "mu": 0.5,
            "m_a": 1.0
        }

        mito.state.membrane_potential = 0.35

        receipt = mito.process_cycle(heavy_phys)

        self.assertEqual(receipt.status, "ANAEROBIC",
                         "[FAIL] System failed to trigger Anaerobic Bypass on extreme cognitive load.")
        self.assertEqual(receipt.symptom, "LACTATE_BUILDUP", "[FAIL] Did not register lactate buildup.")

        self.assertEqual(mito.state.atp_pool, initial_atp - 20.0,
                         "[FAIL] Anaerobic burn did not exact the 20.0 ATP emergency cost.")
        self.assertEqual(mito.state.ros_buildup, initial_ros + 2.0,
                         "[FAIL] Anaerobic burn did not tax the system with 2.0 ROS.")

        print("  [SUCCESS] System correctly bypassed standard metabolism to survive an impossible cognitive load.")