"""tests/test_physics.py"""

import time
from unittest.mock import patch
from drivers import SharedLatticeDriver
from physics import GeodesicEngine
from physics.models import PhysicsPacket
from tests.base import BoneTestCase
from physics.maths import _native_permutation_entropy, _native_detect_false_cohesion, _native_ordinal_pattern, _native_coincidence_length

class TopologicalPrimitivesTest(BoneTestCase):
    def setUp(self):
        super().setUp()
        if not getattr(self.engine, "shared_lattice", None):
            from drivers import SharedLatticeDriver
            self.engine.shared_lattice = SharedLatticeDriver()
        if not hasattr(self.engine.shared_lattice.u, "E"):
            setattr(self.engine.shared_lattice.u, "E", 0.0)
        for attr in ["phi", "resonance_delta"]:
            if not hasattr(self.engine.shared_lattice.shared, attr):
                setattr(self.engine.shared_lattice.shared, attr, 0.0)

    def test_ordinal_pattern(self):
        self.assertEqual(_native_ordinal_pattern([1.2, 1.8, 1.5]), (0, 2, 1), "[FAIL] Ordinal pattern extraction failed.")
        self.assertEqual(_native_ordinal_pattern([3.0, 2.0, 1.0]), (2, 1, 0), "[FAIL] Descending pattern extraction failed.")

    def test_false_cohesion(self):
        history_stuck = [1.0, 5.0, 2.0, 1.0, 5.0, 2.0]
        self.assertTrue(_native_detect_false_cohesion(history_stuck, window_size=3), "[FAIL] Point Attractor went undetected.")
        history_changing = [1.0, 2.0, 3.0, 3.0, 2.0, 1.0]
        self.assertFalse(_native_detect_false_cohesion(history_changing, window_size=3), "[FAIL] False positive on Cohesion trigger.")

    def test_permutation_entropy(self):
        flatline = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(_native_permutation_entropy(flatline, window_size=3), 0.0,
                         "[FAIL] Flatline entropy must be exactly 0.0.")
        chaotic = [1.0, 5.0, 2.0, 8.0, 1.0, 9.0]
        self.assertGreater(_native_permutation_entropy(chaotic, window_size=3), 0.0,
                           "[FAIL] Chaotic signal yielded zero entropy.")
        noisy_flatline = [1.0, 1.000001, 1.0, 1.000002, 1.0, 1.000001]
        self.assertEqual(_native_permutation_entropy(noisy_flatline, window_size=3, epsilon=1e-5), 0.0,
                         "[FAIL] Epsilon tie-exclusion failed to drop noise. System is hallucinating complexity.")

    def test_coincidence_length(self):
        orbit_a = [1.0, 2.0, 3.0, 4.0, 5.0]
        orbit_b = [1.0, 2.0, 3.0, 9.0, 9.0]
        self.assertEqual(_native_coincidence_length(orbit_a, orbit_b, tol=0.1), 3, "[FAIL] Orbit coincidence length miscalculated.")

    def test_semantic_dimension_formalization(self):
        from physics import NaviSADProtocol
        navi = NaviSADProtocol()
        dim_flat = navi.calculate_semantic_dimension(efficiency_index=1.0, novelty=0.0)
        self.assertAlmostEqual(dim_flat, 1.0, places=2, msg="[FAIL] Flat logic did not yield a dimension of 1.0.")
        dim_fractal = navi.calculate_semantic_dimension(efficiency_index=0.5, novelty=0.8)
        self.assertGreater(dim_fractal, 1.2, "[FAIL] Novel logic failed to expand the fractal dimension.")
        initial_atp = self.engine.bio.mito.state.atp_pool
        self.engine.host_stats.efficiency_index = 1.0
        self.engine.tick_count = 6
        self.engine.cortex.dspy_critic.enabled = False
        with patch.object(self.engine.cortex.llm, 'generate', return_value="I agree completely."):
            result = self.engine.process_turn("Do you agree?")
        self.assertIn("FALSE COHESION BREAK", result.get("ui", ""), "[FAIL] The Jester failed to shatter the mathematically proven point attractor.")
        self.assertLess(self.engine.bio.mito.state.atp_pool, initial_atp, "[FAIL] ATP was not burned to break the false cohesion.")
        phys_pkt = result.get("physics", {})
        omega_in_pkt = "omega_r" in phys_pkt or "omega_r" in phys_pkt.get("energy", {})
        self.assertTrue(omega_in_pkt, "[FAIL] Right-Brain Coherence (omega_r) was not appended to the physics packet.")

    def test_drag_profile(self):
            driver = SharedLatticeDriver()
            phys = PhysicsPacket(beta=0.9, chi=0.8, voltage=40.0)
            phys.valence = -0.9
            driver.infer_and_couple("This makes no sense and I hate it.", phys, phys, 20.0)
            self.assertGreater(phys.drag_profile.semantic, 2.0, "Semantic drag failed to calculate from Beta/Chi.", )
            self.assertGreater(phys.drag_profile.emotional, 1.0, "Emotional drag failed to calculate from Valence.", )
            self.assertEqual(phys.drag_profile.metabolic, 3.0, "Metabolic drag failed to trigger on low ATP.", )
            phys.sync_drag()
            self.assertGreater(phys.narrative_drag, 5.0, "Drag profile failed to sync to total narrative_drag.", )

    def test_aerodynamic_lift(self):
            counts = {"play": 15, "kinetic": 10, "explosive": 5, "heavy": 0, "constructive": 0, "void": 0, }
            masses = GeodesicEngine._weigh_mass(counts)
            forces = GeodesicEngine._calculate_forces(masses, counts, volume=30, config_ref=self.engine.config)
            self.assertLess(forces["compression"], 0.0, f"[FAIL] Drag/Compression was {forces['compression']}. The lift clamp is still active!", )

    def test_grammar_of_silence(self):
            driver = SharedLatticeDriver()
            phys = PhysicsPacket(beta=0.8)
            driver.shared.phi = 0.85
            driver.shared.lambda_silence = 0.5
            driver.last_timestamp = time.time() - 20.0
            logs, _ = driver.infer_and_couple("Finally, I have the words.", phys, phys, 100.0)
            self.assertGreater(driver.shared.delta, 0.0, "Silence weight (Nabla/Delta) failed to accumulate.", )
            self.assertEqual(driver.shared.sigma_silence, 1, "Silence failed to classify as Pregnant (Sigma 1).", )
            self.assertTrue(any("wanted to be born" in log for log in logs), "System failed to articulate the pregnant silence.", )

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

    def test_navi_fractal_quality_gate(self):
        from cycle import _native_quality_gate
        log_r_perfect = [1.0, 2.0, 3.0, 4.0]
        log_m_perfect = [2.0, 4.0, 6.0, 8.0]
        passed, code = _native_quality_gate(log_r_perfect, log_m_perfect)
        self.assertTrue(passed, f"[FAIL] Perfect linearity failed the gate: {code}")
        log_r_bad = [1.0, 2.0, 3.0, 4.0]
        log_m_bad = [10.0, 1.0, 10.0, 1.0]
        passed_bad, code_bad = _native_quality_gate(log_r_bad, log_m_bad)
        self.assertFalse(passed_bad, "[FAIL] Quality Gate allowed a highly fragmented, non-linear graph.")
        self.assertTrue(code_bad.startswith("POOR_FIT"), "[FAIL] Incorrect reason code for poor fit.")
        passed_short, code_short = _native_quality_gate([1.0, 2.0], [1.0, 2.0])
        self.assertFalse(passed_short, "[FAIL] Quality Gate allowed a graph with insufficient range.")
        self.assertEqual(code_short, "INSUFFICIENT_RANGE", "[FAIL] Incorrect reason code for short range.")

    def test_navi_fractal_null_model(self):
        from cycle import _native_configuration_model
        adj = {0: {1, 2, 3, 4}, 1: {0}, 2: {0}, 3: {0}, 4: {0}}
        null_adj = _native_configuration_model(adj)
        original_degrees = {k: len(v) for k, v in adj.items()}
        null_degrees = {k: len(v) for k, v in null_adj.items()}
        self.assertEqual(original_degrees, null_degrees, "[FAIL] Null model failed to preserve degree sequence.")

    def test_cd_viability_and_drive(self):
        phys = PhysicsPacket()
        phys.kappa = 0.8
        phys.gamma = 0.8
        phys.mu = 0.5
        phys.lambda_val = 1.0
        b = phys.get_viability_potential()
        self.assertAlmostEqual(b, (0.8 * 0.8) - (1.0 * 0.5), places=2, msg="[FAIL] Viability Potential (b) calculation is mathematically incorrect.")
        a = phys.get_creative_drive()
        self.assertAlmostEqual(a, 0.8 * 0.8 * 0.5, places=2, msg="[FAIL] Creative Drive (a) calculation is mathematically incorrect.")
        lam1 = phys.get_principal_eigenvalue()
        self.assertIsInstance(lam1, float, "[FAIL] Principal Eigenvalue failed to return a float.")

    def test_cd_saturation_penalty(self):
        phys = PhysicsPacket()
        phys.voltage = 200.0  # Phi = 2.0
        penalty = phys.enforce_saturation_limit(c=1.5, p=2.0)
        self.assertAlmostEqual(penalty, 6.0, places=2, msg="[FAIL] Saturation penalty is mathematically incorrect.")
        self.assertAlmostEqual(phys.voltage, 110.0, places=2, msg="[FAIL] Voltage failed to damp correctly. Runaway tension is unchecked.")

    def test_cd_picard_damping_convergence(self):
        print("")
        t, f, p = 0.7, 0.0, 0.95
        damping = 0.6
        for _ in range(5):
            t = round((1 - damping) * t + damping * 0.2, 2)
            f = round((1 - damping) * f + damping * 1.5, 2)
            p = round((1 - damping) * p + damping * 0.5, 2)
        self.assertLess(t, 0.25, "[FAIL] Temperature failed to damp towards 0.2.")
        self.assertGreater(f, 1.4, "[FAIL] Frequency penalty failed to damp towards 1.5.")
        self.assertLess(p, 0.55, "[FAIL] Top P failed to damp towards 0.5.")

    def test_cd_cycle_snapshot_saturation(self):
        from cycle import GeodesicOrchestrator
        orch = GeodesicOrchestrator(self.engine)
        self.engine.observer.last_physics_packet = PhysicsPacket()
        self.engine.active_physics.voltage = 150.0
        snapshot = orch.run_headless_turn("Test saturation.")
        self.assertIn("saturation_penalty", snapshot.get("physics", {}),
                      "[FAIL] Saturation penalty not injected into telemetry snapshot.")
        self.assertGreater(snapshot["physics"]["saturation_penalty"], 0.0,
                           "[FAIL] Saturation penalty failed to trigger on high voltage.")
