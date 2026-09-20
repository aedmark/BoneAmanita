"""tests/test_biology.py"""

from unittest.mock import MagicMock, patch

from archetypes.village import DeathGen
from core import CycleContext
from cycle import ObservationPhase, SensationPhase
from physics.models import PhysicsPacket
from tests.base import BoneTestCase


class BiologyTests(BoneTestCase):
    def test_fatal_fever_dream_starvation(self):
        from brain.mind import DreamEngine

        mock_lore = MagicMock()
        mock_lore.get.return_value = {"NIGHTMARES": ["Test Nightmare {ghost}"]}
        dreamer = DreamEngine(events=MagicMock(), lore_ref=mock_lore)
        bio_state = {"mito": {"atp": 3.0}, "chem": {"cortisol": 0.0}}
        with patch("random.random", return_value=0.1):
            msg, shift = dreamer.enter_rem_cycle(soul_snapshot={}, bio_state=bio_state)
            self.assertIn(
                "fatal fever dream",
                msg,
                "[FAIL] DreamEngine failed to trigger the fatal fever dream on starvation.",
            )
            self.assertEqual(
                shift.get("voltage"),
                100.0,
                "[FAIL] Thermal runaway voltage was not applied.",
            )
            self.assertEqual(
                shift.get("atp_drain"),
                13.0,
                "[FAIL] Terminal starvation ATP drain was not calculated correctly.",
            )

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
        with (
            patch.object(target_cfg.BIO, "REST_HEALTH_RECOVERY", 20.0),
            patch.object(target_cfg.BIO, "REST_STAMINA_RECOVERY", 40.0),
        ):
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

    def test_epigenetic_trauma_pruning_rem_cycle(self):
        from brain.mind import DreamEngine

        mock_lore = MagicMock()
        mock_lore.get.return_value = {"SYSTEM_PROMPTS": {}}
        mock_eng = MagicMock()
        mock_mem = MagicMock()
        dreamer = DreamEngine(
            events=MagicMock(), lore_ref=mock_lore, eng_ref=mock_eng, mem_ref=mock_mem
        )
        dreamer.dspy_critic = MagicMock()
        dreamer.dspy_critic.enabled = True
        dreamer.dspy_critic.evolve_prompt.return_value = "NEW_SCAR_AXIOM"
        dreamer.dspy_critic.compress_prompts = lambda x: "COMPRESSED_AXIOMS"
        dreamer.trauma_buffer.append("Critical failure: Generative slop detected.")
        bio_state = {"mito": {"atp": 50.0}, "chem": {"cortisol": 0.0}}
        try:
            msg, shift = dreamer.enter_rem_cycle(
                soul_snapshot={"archetype": "THE_VOID"}, bio_state=bio_state
            )
        except NameError as e:
            self.fail(f"[FAIL] Epigenetic pruning crashed with a NameError: {e}")
        self.assertIsNotNone(
            msg, "[FAIL] DreamEngine failed to return a valid dream string."
        )
        self.assertIn(
            "scar-tissue axiom",
            msg,
            "[FAIL] Epigenetic trauma pruning text missing from dream.",
        )
        self.assertTrue(
            mock_lore.save.called,
            "[FAIL] Lore manifest was not saved after epigenetic mutation.",
        )

    def test_epigenetic_mutation_gated_off_in_conversation_mode(self):
        """The critic only ever sees "the lattice rejected this" and nothing
        about mode or the person's state; it once turned a run of ordinary
        CONVERSATION-mode hedging (natural mid-crisis) into a permanent
        "never soothe or reassure" axiom. CONVERSATION is listed in
        CORTEX.EPIGENETIC_MUTATION_DISABLED_MODES so this can't recur."""
        from brain.mind import DreamEngine

        mock_lore = MagicMock()
        mock_lore.get.return_value = {"SYSTEM_PROMPTS": {}}
        dreamer = DreamEngine(
            events=MagicMock(),
            lore_ref=mock_lore,
            eng_ref=MagicMock(),
            mem_ref=MagicMock(),
        )
        dreamer.dspy_critic = MagicMock()
        dreamer.dspy_critic.enabled = True
        dreamer.dspy_critic.evolve_prompt.return_value = "NEW_SCAR_AXIOM"
        dreamer.trauma_buffer.append("Critical failure: Generative slop detected.")
        bio_state = {"mito": {"atp": 50.0}, "chem": {"cortisol": 0.0}}
        msg, shift = dreamer.enter_rem_cycle(
            soul_snapshot={"archetype": "THE_VOID"},
            bio_state=bio_state,
            active_mode="CONVERSATION",
        )
        dreamer.dspy_critic.evolve_prompt.assert_not_called()
        self.assertNotIn(
            "scar-tissue axiom",
            msg or "",
            "[FAIL] CONVERSATION mode still let a new axiom mutate the prompt.",
        )
        self.assertFalse(
            mock_lore.save.called,
            "[FAIL] Lore was written even though the mutation was gated off.",
        )
        self.assertEqual(
            len(dreamer.trauma_buffer),
            0,
            "[FAIL] Trauma should still drain in a gated mode, or it queues up "
            "and fires the moment the mode changes.",
        )

    def test_epigenetic_mutation_still_fires_outside_conversation_mode(self):
        from brain.mind import DreamEngine

        mock_lore = MagicMock()
        mock_lore.get.return_value = {"SYSTEM_PROMPTS": {}}
        dreamer = DreamEngine(
            events=MagicMock(),
            lore_ref=mock_lore,
            eng_ref=MagicMock(),
            mem_ref=MagicMock(),
        )
        dreamer.dspy_critic = MagicMock()
        dreamer.dspy_critic.enabled = True
        dreamer.dspy_critic.evolve_prompt.return_value = "NEW_SCAR_AXIOM"
        dreamer.trauma_buffer.append("Critical failure: Generative slop detected.")
        bio_state = {"mito": {"atp": 50.0}, "chem": {"cortisol": 0.0}}
        msg, shift = dreamer.enter_rem_cycle(
            soul_snapshot={"archetype": "THE_VOID"},
            bio_state=bio_state,
            active_mode="ADVENTURE",
        )
        dreamer.dspy_critic.evolve_prompt.assert_called_once()
        self.assertIn(
            "scar-tissue axiom",
            msg,
            "[FAIL] The gate should only apply to CONVERSATION, not other modes.",
        )

    def test_epigenetic_gate_reads_the_real_engines_active_mode(self):
        """Regression for the actual production bug: the gate originally
        read self.eng.cortex.active_mode from inside DreamEngine, but
        self.eng there is not the same object that holds .cortex (confirmed
        live - self.eng.cortex did not exist), so it silently always saw ""
        and never gated anything. Every real call site now reads
        active_mode off its own self.eng.cortex and passes it in; this
        exercises that against the real, fully-booted engine rather than a
        hand-built mock, which is exactly what let the original bug pass."""
        self.assertTrue(
            hasattr(self.engine.cortex, "active_mode"),
            "[FAIL] The real engine's cortex has no active_mode; the call "
            "sites' getattr(self.eng.cortex, 'active_mode', '') would fail open.",
        )
        dreamer = self.engine.mind.dreamer
        dreamer.dspy_critic = MagicMock()
        dreamer.dspy_critic.enabled = True
        dreamer.dspy_critic.evolve_prompt.return_value = "NEW_SCAR_AXIOM"
        dreamer.trauma_buffer.append("Critical failure: Generative slop detected.")
        original_mode = self.engine.cortex.active_mode
        try:
            self.engine.cortex.active_mode = "CONVERSATION"
            dreamer.enter_rem_cycle(
                soul_snapshot={"archetype": "THE_VOID"},
                bio_state={"mito": {"atp": 50.0}, "chem": {"cortisol": 0.0}},
                active_mode=self.engine.cortex.active_mode,
            )
        finally:
            self.engine.cortex.active_mode = original_mode
        dreamer.dspy_critic.evolve_prompt.assert_not_called()

    def test_config_glimmer_yield(self):
        target_cfg = getattr(self.engine, "config")
        feedback = {"INTEGRITY": 0.95}
        with patch.object(target_cfg.BIO, "GLIMMER_INTEGRITY_THRESH", 1.5):
            glimmer_msg = self.engine.bio.endo.check_for_glimmer(
                feedback, harvest_hits=1
            )
            self.assertIsNone(
                glimmer_msg,
                "System generated a glimmer even though the integrity threshold was not met.",
            )
        with patch.object(target_cfg.BIO, "GLIMMER_INTEGRITY_THRESH", 0.5):
            glimmer_msg_success = self.engine.bio.endo.check_for_glimmer(
                feedback, harvest_hits=1
            )
            self.assertIsNotNone(
                glimmer_msg_success,
                "System failed to generate a glimmer after the threshold was lowered.",
            )

    def test_somatic_unity(self):
        has_unified_cortex = hasattr(self.engine.bio, "synesthesia") or hasattr(
            self.engine.soma, "synesthesia"
        )
        self.assertTrue(
            has_unified_cortex,
            "[FAIL] SynestheticCortex is not centralized in the Somatic Loop.",
        )
        ctx = CycleContext(input_text="Testing unity.")
        phase = SensationPhase(self.engine.orchestrator.eng)
        try:
            phase.run(ctx)
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

    def test_bio_physical_coupling(self):
        from core import CyberneticGovernor

        gov = CyberneticGovernor()
        gov.recalibrate(target_voltage=50.0, target_drag=5.0)
        phys_mock = {"voltage": 100.0, "narrative_drag": 10.0}
        v_shift_base, d_shift_base = gov.regulate(phys_mock, dt=1.0)

        class MockEndo:
            def __init__(self, glimmers):
                self.glimmers = glimmers

        endo_depleted = MockEndo(glimmers=0)
        v_shift_dep, _ = gov.regulate(phys_mock, dt=1.0, endocrine_state=endo_depleted)
        endo_rich = MockEndo(glimmers=2)
        v_shift_rich, _ = gov.regulate(phys_mock, dt=1.0, endocrine_state=endo_rich)
        self.assertTrue(
            abs(v_shift_dep) < abs(v_shift_base),
            "[FAIL] Depleted biology failed to throttle physics regulation.",
        )
        self.assertTrue(
            abs(v_shift_rich) > abs(v_shift_base),
            "[FAIL] High glimmers failed to accelerate physics regulation.",
        )
