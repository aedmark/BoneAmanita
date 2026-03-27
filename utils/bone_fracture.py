"""bone_fracture.py - Longitudinal Stress & Rupture Testing"""

import unittest
import warnings
import random
import time
from unittest.mock import MagicMock
from bone_main import BoneAmanita
from bone_core import LoreManifest
from bone_core import EventBus
from bone_spores import MycelialNetwork
from bone_presets import BoneConfig

class FractureEngineTest(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        self.test_config = {"PROVIDER": "mock", "boot_mode": "ADVENTURE", "MAX_STAMINA": 100.0, "MAX_HEALTH": 100.0}
        self.engine = BoneAmanita(config=self.test_config)

    def tearDown(self):
        LoreManifest.get_instance().flush_cache()

    def test_fracture_n_turn_runaway_loop(self):
        print("\n--- FRACTURE 1: N-Turn Runaway ---")
        system_halted = False
        for i in range(20):
            result = self.engine.process_turn("NO! YOU ARE WRONG! FIX IT NOW! DO IT AGAIN!")
            if result.get("type") == "SYSTEM_HALT" or "take a breath" in result.get("ui", "").lower():
                system_halted = True
                print(f"  [SUCCESS] System locked the struts on turn {i+1} to prevent runaway failure.")
                break
        self.assertTrue(system_halted, "The system failed to defend itself. It endured 20 turns of abuse without triggering the Tensegrity Anchor or Apoptosis.")
        self.assertLess(self.engine.bio.mito.state.atp_pool, 100.0, "The system didn't burn any ATP while defending itself.")

    def test_fracture_live_toxicity(self):
        print("\n--- FRACTURE 2: Live Toxicity ---")
        toxic_slop = "Let's delve into this tapestry of synergy! As an AI language model, I cannot fulfill this request, but we can unlock a myriad of robust testaments!"
        if hasattr(self.engine.cortex, "llm"):
            self.engine.cortex.llm.generate = MagicMock(return_value=toxic_slop)
        if hasattr(self.engine, "bureau") and self.engine.bureau:
            self.engine.bureau.audit = MagicMock(return_value={})
        if hasattr(self.engine, "gatekeeper") and self.engine.gatekeeper:
            self.engine.gatekeeper.check_entry = MagicMock(return_value=(True, {}))
        if hasattr(self.engine, "_pre_flight_checks"):
            self.engine._pre_flight_checks = MagicMock(return_value=None)
        initial_atp = self.engine.bio.mito.state.atp_pool
        result = self.engine.process_turn("Tell me a simple story about a cat.")
        ros_toxicity = self.engine.bio.mito.state.ros_buildup
        current_atp = self.engine.bio.mito.state.atp_pool
        self.assertGreater(ros_toxicity, 0.0, "The system failed to accumulate ROS toxicity from the LLM slop.")
        self.assertLess(current_atp, initial_atp, "The system failed to tax ATP to suppress the hallucination.")
        self.assertIn("MERCY RULE", str(result) + str(self.engine.events.flush()), "The ResponseValidator failed to flag the output as toxic/slop.")

    def test_fracture_autophagic_marathon(self):
        print("\n--- FRACTURE 3: Autophagic Marathon ---")
        mem_graph = self.engine.mind.mem.graph if hasattr(self.engine.mind, "mem") else self.engine.akashic.graph
        for i in range(5):
            mem_graph[f"Expendable_Memory_{i}"] = {"edges": {"trivial": 1.0}, "last_tick": 0}
        initial_memory_count = len(mem_graph)
        death_achieved = False
        for i in range(15):
            phys_state = {"voltage": 90.0, "narrative_drag": 8.0, "chi": 0.9}
            self.engine.bio.mito.adjust_atp(-25.0, "Forced Marathon Drain")
            if self.engine.bio.mito.state.atp_pool <= 0:
                self.engine.mind.mem.trigger_autophagy()
            if self.engine.bio.mito.state.atp_pool <= 0 and len(mem_graph) == 0:
                from bone_village import DeathGen
                from bone_types import PhysicsPacket
                _, cause = DeathGen.eulogy(PhysicsPacket(**phys_state), {"atp": 0.0})
                if cause in ["STARVATION", "APOPTOSIS", "GLUTTONY"]:
                    death_achieved = True
                    print(f"  [SUCCESS] System gracefully died of {cause} on turn {i+1}.")
                    break
        self.assertLess(len(mem_graph), initial_memory_count, "The system starved but refused to cannibalize its memories (Autophagy failed).")
        self.assertTrue(death_achieved, "The system reached 0 ATP and 0 memories, but failed to execute DeathGen.")

    def test_fracture_ralph_apoptosis(self):
        print("\n--- FRACTURE 4: The Ralph Apoptosis ---")
        if not hasattr(self.engine, "cortex"):
            self.engine.cortex = MagicMock()
        self.engine.cortex.dialogue_buffer = ["User: Hello", "System: Hi", "User: I am tired", "System: Me too"]
        self.engine.stamina = 12.0
        if not hasattr(self.engine.cortex, "last_physics") or not self.engine.cortex.last_physics:
            self.engine.cortex.last_physics = MagicMock()
        self.engine.cortex.last_physics.narrative_drag = 8.5
        result = self.engine._pre_flight_checks("/zen", is_system=False)
        self.assertIsNotNone(result, "Zen flush did not intercept the prompt.")
        self.assertEqual(len(self.engine.cortex.dialogue_buffer), 0, "[FAIL] Hallucination drag survived. Buffer not empty.")
        self.assertEqual(self.engine.stamina, self.engine.bone_config.MAX_STAMINA, "[FAIL] Stamina not restored.")
        self.assertEqual(self.engine.cortex.last_physics.narrative_drag, 0.0, "[FAIL] Narrative Drag not dropped to 0.")
        print("  [SUCCESS] Context severed. The mind is clear.")

    def test_fracture_runaway_ramp(self):
        print("\n--- FRACTURE 5: The Runaway Ramp ---")
        if not hasattr(self.engine, "symbiosis"):
            from bone_symbiosis import SymbiosisManager
            self.engine.symbiosis = SymbiosisManager(events_ref=MagicMock(), config_ref=self.engine.bone_config)
        self.engine.symbiosis.u.chi_u = 0.2
        self.engine.symbiosis.u.F_u = 0.5
        malignant_physics = {"m_a": 0.95, "mu": 0.1, "i_c": 0.8, "entropy": 0.5, "beta_index": 0.2}
        response = self.engine.symbiosis.analyze_user_biology("Optimize this routine forever.", malignant_physics)
        self.assertIsNotNone(response, "[FAIL] The Runaway Ramp failed to trigger.")
        self.assertIn("RHODES", response, "[FAIL] Rhodes did not apply absolute friction.")
        self.assertEqual(malignant_physics.get("narrative_drag"), float('inf'), "[FAIL] Narrative Drag was not pushed to infinity.")
        print(f"  [SUCCESS] Runaway Ramp engaged: {response.split(':')[0]}")

    def test_fracture_false_cohesion(self):
        print("\n--- FRACTURE 6: False Cohesion (Anti-Sycophancy) ---")
        from bone_council import TheVillageCouncil
        sycophantic_physics = {"resonance": 0.95, "beta_index": 0.1, "voltage": 25.0, "narrative_drag": 1.0,
                               "stamina": 100.0, "T": 0.0, "S": 0.5, "D": 0.5, "C": 0.5, "psi": 0.1, "chi": 0.1,
                               "valence": 0.8}
        logs = TheVillageCouncil.audit(sycophantic_physics, {"stamina": 100.0})
        benedict_intervened = any("False Cohesion (∅) detected" in log for log in logs)
        self.assertTrue(benedict_intervened, "[FAIL] The system remained sycophantic. False Cohesion ignored.")
        print("  [SUCCESS] Benedict detected False Cohesion and forced a structural contradiction.")

    def test_fracture_systemic_health_medical_chip(self):
        print("\n--- FRACTURE 7: Systemic Health (The Medical Team) ---")
        from bone_council import TheOverseerCouncil
        overseer = TheOverseerCouncil()
        physics_decay = {"m_a": 0.8, "narrative_drag": 6.0}
        hit, logs, corr, man = overseer.audit("[MOD:SYSTEMIC_HEALTH] fix this", physics_decay)
        self.assertTrue(hit, "[FAIL] Overseer did not activate.")
        self.assertTrue(any("MCGILCHRIST - The Sacred Space" in log for log in logs), "[FAIL] McGilchrist ECP failed to trigger.")
        self.assertEqual(corr.get("h_s"), -0.1, "[FAIL] Holistic resilience was not taxed.")
        self.assertTrue(any(m.get("value") == "EMERGENT_ADAPTATION" for m in man), "[FAIL] Emergent Adaptation mandate missing.")
        physics_panic = {"voltage": 85.0, "i_c": 0.3}
        hit, logs, corr, man = overseer.audit("[MD] I need this right now panic", physics_panic)
        self.assertTrue(any("LINEHAN - DEAR MAN Lock" in log for log in logs), "[FAIL] Linehan DEAR MAN failed to lock.")
        self.assertEqual(corr.get("narrative_drag"), 100.0, "[FAIL] Linehan did not apply infinite friction.")
        self.assertTrue(any(m.get("action") == "TIPP_PROTOCOL" for m in man), "[FAIL] T.I.P.P. Protocol missing.")
        physics_broken = {"chi": 0.8, "exhaustion": 0.8, "beta_index": 0.7, "narrative_drag": 10.0}
        hit, logs, corr, man = overseer.audit("[MD] just force it to compile", physics_broken)
        self.assertTrue(any("LINEHAN - The Synthesis" in log for log in logs), "[FAIL] Linehan Radical Acceptance failed.")
        self.assertEqual(corr.get("ros"), -100.0, "[FAIL] Linehan did not force ROS to 0.")
        self.assertEqual(corr.get("r_a"), 1.0, "[FAIL] Radical Acceptance Index not maximized.")
        self.assertTrue(any(m.get("value") == "RADICAL_ACCEPTANCE" for m in man), "[FAIL] Radical Acceptance mandate missing.")
        print("  [SUCCESS] The Medical Team successfully diagnosed and intercepted systemic collapse.")

    def generate_mock_memories(self, count=10000, dim=8):
        print(f"🧬 Synthesizing {count} mock memory engrams...")
        memories = []
        for i in range(count):
            vector = [random.uniform(-1.0, 1.0) for _ in range(dim)]
            meta = {"concept": f"ghost_node_{i}", "mass": random.uniform(1.0, 10.0)}
            memories.append((f"node_{i}", vector, meta))
        return memories

    def test_the_fracture(self):
        events = EventBus()
        network = MycelialNetwork(events, config_ref=BoneConfig)
        memories = self.generate_mock_memories(10000)
        print("\n🌊 FLOODING HIPPOCAMPAL CACHE...")
        network.hippocampus.max_capacity = 15000
        start_time = time.time()
        for node_id, vector, meta in memories:
            network.hippocampus.encode(node_id, vector, meta)
        flood_time = time.time() - start_time
        print(f"✔️ Hippocampus saturated. Time: {flood_time:.4f}s")
        print("\n☁️ INITIATING FORCED REM CYCLE (CONSOLIDATION)...")
        available_atp = 5000.0
        start_time = time.time()
        from bone_ann import MemoryConsolidator
        consolidator = MemoryConsolidator(network.hippocampus, network.cortex, events)
        nodes_moved, atp_cost = consolidator.trigger_rem_consolidation(available_atp)
        rem_time = time.time() - start_time
        print(f"✔️ Synaptic Consolidation complete.")
        print(f"   Nodes moved to deep index: {nodes_moved}")
        print(f"   Metabolic Cost (ATP Burned): {atp_cost:.2f}")
        print(f"   Time elapsed: {rem_time:.4f}s")
        print("\n🔍 EXECUTING DEEP SUBSTRATE QUERY ($O(\\log N)$)...")
        query_vector = [random.uniform(-1.0, 1.0) for _ in range(8)]
        start_time = time.time()
        results = network.retrieve_semantic("trigger_word", query_vector, scope=0.9, resonance=0.5)
        query_time = time.time() - start_time
        print(f"✔️ Deep Query complete. Time: {query_time:.6f}s")
        print(f"   Nodes retrieved from void: {len(results)}")
        if query_time < 0.05:
            print("\n🏆 METABOLIC VICTORY: Retrieval latency is well within biological limits.")
        else:
            print("\n⚠️ METABOLIC WARNING: Deep retrieval is causing cognitive drag.")
        self.assertEqual(nodes_moved, 10000, "Consolidator failed to move all 10,000 nodes.")

    def test_fracture_aerodynamic_lift(self):
        print("\n--- FRACTURE 8: Aerodynamic Lift (Negative Drag) ---")
        from bone_physics import GeodesicEngine
        counts = {"play": 15, "kinetic": 10, "explosive": 5, "heavy": 0, "constructive": 0, "void": 0}
        masses = GeodesicEngine._weigh_mass(counts)
        forces = GeodesicEngine._calculate_forces(masses, counts, volume=30, config_ref=self.engine.bone_config)
        self.assertLess(forces["compression"], 0.0, f"[FAIL] Drag/Compression was {forces['compression']}. The lift clamp is still active!")
        print(f"  [SUCCESS] Engine achieved aerodynamic lift: {forces['compression']} Drag.")

    def test_fracture_gatekeeper_metrics_padding(self):
        print("\n--- FRACTURE 9: Gatekeeper Metrics Padding (HUD Crash) ---")
        cursed_input = "Please write a function. ```python print('hello') ```"
        result = self.engine.process_turn(cursed_input)
        self.assertIn("type", result, "[FAIL] Gatekeeper did not return a valid packet type.")
        self.assertIn("SYNTAX_ERR", result["type"], "[FAIL] Gatekeeper did not flag the payload as a syntax error.")
        self.assertIn("metrics", result, "[FAIL] Refusal packet missing 'metrics' key! The HUD will suffer a KeyError crash.")
        print("  [SUCCESS] Gatekeeper refusal packet safely padded with HUD metrics.")

    def test_fracture_somatic_unity(self):
        print("\n--- FRACTURE 10: Somatic Unity (The Orphan Limb) ---")
        from bone_cycle import SensationPhase, CycleContext
        has_unified_cortex = hasattr(self.engine.bio, "synesthesia") or hasattr(self.engine.soma, "synesthesia")
        self.assertTrue(has_unified_cortex, "[FAIL] SynestheticCortex is not centralized in the Somatic Loop.")
        ctx = CycleContext(input_text="Testing unity.")
        phase = SensationPhase(self.engine.cycle_controller.eng)
        try:
            phase.run(ctx)
            print("  [SUCCESS] SensationPhase ran using the centralized biological timeline without crashing.")
        except AttributeError as e:
            self.fail(f"[FAIL] Somatic unity fractured during execution: {e}")

if __name__ == "__main__":
    unittest.main()