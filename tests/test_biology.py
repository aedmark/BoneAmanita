"""tests/test_biology.py"""

from unittest.mock import patch, MagicMock
from cycle import ObservationPhase, SensationPhase
from physics.models import PhysicsPacket
from core import CycleContext
from archetypes.village import DeathGen
from tests.base import BoneTestCase

class BiologyTests(BoneTestCase):
    def test_death_by_starvation(self):
            phys = PhysicsPacket(voltage=5.0, narrative_drag=1.0)
            bio_state = {"atp": 0.0}
            _, cause = DeathGen.eulogy(phys, bio_state)
            self.assertEqual(cause, "STARVATION", "DeathGen failed to diagnose STARVATION.")

    def test_death_by_gluttony(self):
        phys = PhysicsPacket(voltage=150.0, narrative_drag=0.0)
        bio_state = {"atp": 50.0}
        _, cause = DeathGen.eulogy(phys, bio_state)
        self.assertEqual(cause, "GLUTTONY", "DeathGen failed to diagnose GLUTTONY.")

    def test_config_metabolic_recovery(self):
            target_cfg = getattr(self.engine, "config")
            self.engine.bio.biometrics.health = 50.0
            self.engine.bio.biometrics.stamina = 50.0
            with patch.object(target_cfg.BIO, 'REST_HEALTH_RECOVERY', 20.0), \
                    patch.object(target_cfg.BIO, 'REST_STAMINA_RECOVERY', 40.0):
                self.engine.bio.rest(factor=1.0)
                self.assertEqual(
                    self.engine.bio.biometrics.health,
                    70.0,
                    "Health did not recover at the configured rate.",
                )
                self.assertEqual(
                    self.engine.bio.biometrics.stamina,
                    90.0,
                    "Stamina did not recover at the configured rate.",
                )

    def test_config_glimmer_yield(self):
            target_cfg = getattr(self.engine, "config")
            feedback = {"INTEGRITY": 0.95}
            with patch.object(target_cfg.BIO, 'GLIMMER_INTEGRITY_THRESH', 1.5):
                glimmer_msg = self.engine.bio.endo.check_for_glimmer(feedback, harvest_hits=1)
                self.assertIsNone(
                    glimmer_msg,
                    "System generated a glimmer even though the integrity threshold was not met.",
                )
            with patch.object(target_cfg.BIO, 'GLIMMER_INTEGRITY_THRESH', 0.5):
                glimmer_msg_success = self.engine.bio.endo.check_for_glimmer(feedback, harvest_hits=1)
                self.assertIsNotNone(
                    glimmer_msg_success,
                    "System failed to generate a glimmer after the threshold was lowered.",
                )

    def test_somatic_unity(self):
            print("\n--- Somatic Unity (The Orphan Limb) ---")
            has_unified_cortex = hasattr(self.engine.bio, "synesthesia") or hasattr(
                self.engine.soma, "synesthesia")
            self.assertTrue(
                has_unified_cortex,
                "[FAIL] SynestheticCortex is not centralized in the Somatic Loop.",
            )
            ctx = CycleContext(input_text="Testing unity.")
            phase = SensationPhase(self.engine.cycle_controller.eng)
            try:
                phase.run(ctx)
                print(
                    "  [SUCCESS] SensationPhase ran using the centralized biological timeline without crashing."
                )
            except AttributeError as e:
                self.fail(f"[FAIL] Somatic unity fractured during execution: {e}")

    def test_retroactive_metabolism_and_sleep_isolated(self):
        self.engine.bio.mito.state.atp_pool = 10.0
        if self.engine.bio.biometrics:
            self.engine.bio.biometrics.health = 50.0
        shared_lattice_backup = getattr(self.engine, "shared_lattice", None)
        if shared_lattice_backup:
            self.engine.shared_lattice = None
        try:
            phase = ObservationPhase(self.engine)
            ctx = CycleContext(
                input_text="Hello?",
                physics=PhysicsPacket(voltage=5.0, narrative_drag=1.0),
                is_system_event=False,
            )
            ctx.time_delta = 10800.0
            ctx.limits = getattr(self.engine.config, "CYCLE", {}).__dict__
            ctx = phase.run(ctx)
            self.assertEqual(
                self.engine.bio.mito.state.atp_pool,
                85.0,
                "ObservationPhase failed to correctly apply retroactive ATP.",
            )
            if self.engine.bio.biometrics:
                self.assertEqual(
                    self.engine.bio.biometrics.health,
                    80.0,
                    "ObservationPhase failed to correctly apply retroactive Health.",
                )
            log_texts = [str(log) for log in ctx.logs]
            self.assertTrue(
                any("Retroactive metabolism applied" in log for log in log_texts),
                "System failed to log the retroactive metabolism event.",
            )
            if hasattr(self.engine.mind, "dreamer") and self.engine.mind.dreamer:
                self.assertTrue(
                    any("While you were gone" in log for log in log_texts),
                    "DreamEngine failed to execute the retroactive REM cycle.",
                )
        finally:
            if shared_lattice_backup:
                self.engine.shared_lattice = shared_lattice_backup