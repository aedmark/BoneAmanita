"""tests/test_physics.py"""

import time
from unittest.mock import patch
from drivers import SharedLatticeDriver
from physics import GeodesicEngine
from physics.models import PhysicsPacket
from tests.base import BoneTestCase
from physics.maths import _native_permutation_entropy, _native_detect_false_cohesion, _native_ordinal_pattern, _native_coincidence_length

class TopologicalPrimitivesTest(BoneTestCase):
    def test_ordinal_pattern(self):
        self.assertEqual(_native_ordinal_pattern([1.2, 1.8, 1.5]), (0, 2, 1),
                         "[FAIL] Ordinal pattern extraction failed.")
        self.assertEqual(_native_ordinal_pattern([3.0, 2.0, 1.0]), (2, 1, 0),
                         "[FAIL] Descending pattern extraction failed.")

    def test_false_cohesion(self):
        history_stuck = [1.0, 5.0, 2.0, 1.0, 5.0, 2.0]
        self.assertTrue(_native_detect_false_cohesion(history_stuck, window_size=3),
                        "[FAIL] Point Attractor went undetected.")
        history_changing = [1.0, 2.0, 3.0, 3.0, 2.0, 1.0]
        self.assertFalse(_native_detect_false_cohesion(history_changing, window_size=3),
                         "[FAIL] False positive on Cohesion trigger.")

    def test_permutation_entropy(self):
        flatline = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(_native_permutation_entropy(flatline, window_size=3), 0.0,
                         "[FAIL] Flatline entropy must be exactly 0.0.")
        chaotic = [1.0, 5.0, 2.0, 8.0, 1.0, 9.0]
        self.assertGreater(_native_permutation_entropy(chaotic, window_size=3), 0.0,
                           "[FAIL] Chaotic signal yielded zero entropy.")

    def test_coincidence_length(self):
        orbit_a = [1.0, 2.0, 3.0, 4.0, 5.0]
        orbit_b = [1.0, 2.0, 3.0, 9.0, 9.0]
        self.assertEqual(_native_coincidence_length(orbit_a, orbit_b, tol=0.1), 3,
                         "[FAIL] Orbit coincidence length miscalculated.")

    def test_semantic_dimension_formalization(self):
            print("\n--- Semantic Dimension (fd-formalization) ---")
            from physics import NaviSADProtocol
            navi = NaviSADProtocol()
            dim_flat = navi.calculate_semantic_dimension(efficiency_index=1.0, novelty=0.0)
            self.assertAlmostEqual(dim_flat, 1.0, places=2, msg="[FAIL] Flat logic did not yield a dimension of 1.0.")
            dim_fractal = navi.calculate_semantic_dimension(efficiency_index=0.5, novelty=0.8)
            self.assertGreater(dim_fractal, 1.2, "[FAIL] Novel logic failed to expand the fractal dimension.")
            initial_atp = self.engine.bio.mito.state.atp_pool
            self.engine.host_stats.efficiency_index = 1.0
            self.engine.tick_count = 6
            with patch.object(self.engine.cortex.llm, 'generate', return_value="I agree completely."):
                result = self.engine.process_turn("Do you agree?")
            self.assertIn(
                "FALSE COHESION BREAK", result.get("ui", ""),
                "[FAIL] The Jester failed to shatter the mathematically proven point attractor."
            )
            self.assertLess(self.engine.bio.mito.state.atp_pool, initial_atp,
                            "[FAIL] ATP was not burned to break the false cohesion.")
            self.assertIn(
                "omega_r", result.get("physics", {}),
                "[FAIL] Right-Brain Coherence (omega_r) was not appended to the physics packet."
            )
            print(
                "  [SUCCESS] Semantic dimension formalization correctly triggered the False Cohesion break."
            )

    def test_drag_profile(self):
            driver = SharedLatticeDriver()
            phys = PhysicsPacket(beta=0.9, chi=0.8, voltage=40.0)
            phys.valence = -0.9
            driver.infer_and_couple("This makes no sense and I hate it.", phys, phys, 20.0)
            self.assertGreater(
                phys.drag_profile.semantic,
                2.0,
                "Semantic drag failed to calculate from Beta/Chi.",
            )
            self.assertGreater(
                phys.drag_profile.emotional,
                1.0,
                "Emotional drag failed to calculate from Valence.",
            )
            self.assertEqual(
                phys.drag_profile.metabolic,
                3.0,
                "Metabolic drag failed to trigger on low ATP.",
            )
            phys.sync_drag()
            self.assertGreater(
                phys.narrative_drag,
                5.0,
                "Drag profile failed to sync to total narrative_drag.",
            )

    def test_aerodynamic_lift(self):
            print("\n--- Aerodynamic Lift (Negative Drag) ---")
            counts = {"play": 15, "kinetic": 10, "explosive": 5, "heavy": 0, "constructive": 0, "void": 0, }
            masses = GeodesicEngine._weigh_mass(counts)
            forces = GeodesicEngine._calculate_forces(masses, counts, volume=30, config_ref=self.engine.config)
            self.assertLess(forces["compression"], 0.0,
                            f"[FAIL] Drag/Compression was {forces['compression']}. The lift clamp is still active!", )
            print(f"  [SUCCESS] Engine achieved aerodynamic lift: {forces['compression']} Drag.")

    def test_grammar_of_silence(self):
            driver = SharedLatticeDriver()
            phys = PhysicsPacket(beta=0.8)
            driver.shared.phi = 0.85
            driver.shared.lambda_silence = 0.5
            driver.last_timestamp = time.time() - 20.0
            logs, _ = driver.infer_and_couple("Finally, I have the words.", phys, phys, 100.0)
            self.assertGreater(
                driver.shared.delta,
                0.0,
                "Silence weight (Nabla/Delta) failed to accumulate.",
            )
            self.assertEqual(
                driver.shared.sigma_silence,
                1,
                "Silence failed to classify as Pregnant (Sigma 1).",
            )
            self.assertTrue(
                any("wanted to be born" in log for log in logs),
                "System failed to articulate the pregnant silence.",
            )

    def test_gravity_floor_clamp(self):
            from physics.dynamics import CosmicDynamics
            dyn = CosmicDynamics(config_ref=self.engine.config)
            new_drag, _ = dyn.check_gravity(current_drift=0.5, psi=1.0)
            floor = getattr(self.engine.config.PHYSICS, "DRAG_FLOOR", 1.0)
            self.assertGreaterEqual(new_drag, floor, "[FAIL] Gravity engine breached the physical floor.")

    def test_zone_inertia_vector_update(self):
            from physics.dynamics import ZoneInertia
            zi = ZoneInertia(config_ref=self.engine.config)
            phys_mock = PhysicsPacket()
            phys_mock.energy.beta_index = 1.0
            cosmic_state = ("ORBITAL", 0.0, "msg")
            zi.stabilize("THE_FORGE", phys_mock, cosmic_state)
            first_vector = zi.last_vector
            phys_mock.energy.beta_index = 0.1
            zi.stabilize("AERIE", phys_mock, cosmic_state)
            self.assertNotEqual(zi.last_vector, first_vector, "[FAIL] ZoneInertia failed to update topology during a rejected migration.")

    def test_gatekeeper_metrics_padding(self):
            print("\n--- Gatekeeper Metrics Padding (HUD Crash) ---")
            cursed_input = "Please write a function. ```python print('hello') ```"
            result = self.engine.process_turn(cursed_input)
            self.assertIn("type", result, "[FAIL] Gatekeeper did not return a valid packet type.")
            self.assertIn("SYNTAX_ERR", result["type"], "[FAIL] Gatekeeper did not flag the payload as a syntax error.", )
            self.assertIn("metrics", result, "[FAIL] Refusal packet missing 'metrics' key! The HUD will suffer a KeyError crash.", )
            print("  [SUCCESS] Gatekeeper refusal packet safely padded with HUD metrics.")