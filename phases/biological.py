"""phases/biological.py"""

from constants import Prisma
import random
from typing import Any
from presets import BoneConfig
from physics import apply_somatic_feedback
from core import CycleContext
from struts import ux, safe_set
from mechanics.tools import TheTclWeaver
from phases.base import SimulationPhase, _safe_dict

class MetabolismPhase(SimulationPhase):
    """
    The engine's metabolic governor.

    This phase enforces the thermodynamic limits of the system. It calculates
    the ATP (stamina) cost of the current cycle, applies economic penalties
    for chaotic logic loops, and regulates the system's structural health
    through sleep cycles, healing algorithms, and emergency toxicity purging.
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "METABOLISM"

    def run(self, ctx: CycleContext):
        # System events bypass metabolic burn to prevent structural lockup.
        if ctx.is_system_event:
            return ctx

        # If the biological layer is missing or disabled, skip processing.
        if not hasattr(self.eng, "bio") or not self.eng.bio:
            return ctx

        mode_settings = getattr(self.eng, "mode_settings", {})

        # If ATP drain is disabled (e.g., God mode / testing), simulate a perfect biological state.
        if not mode_settings.get("atp_drain_enabled", True):
            atp_level = (self.eng.bio.mito.state.atp_pool
                         if self.eng.bio and self.eng.bio.mito else 100.0)
            ctx.bio_result = {"is_alive": True, "logs": [], "atp": atp_level}
            ctx.is_alive = True
            self._apply_healing(ctx)
            return ctx

        physics = ctx.physics

        # Apply base metabolic tax based on host computational efficiency.
        if hasattr(self.eng, "host_stats"):
            self._apply_economic_stimulus(ctx, self.eng.host_stats.efficiency_index)

        # Shift the autonomic nervous system (governor) based on recent systemic voltage (stress).
        gov_msg = self.eng.bio.governor.shift(physics, self.eng.phys.dynamics.voltage_history, self.eng.tick_count)
        if gov_msg:
            self.eng.events.log(gov_msg, "GOV")

        # Bind the physiological state to the physical manifold.
        physics.manifold = self.eng.bio.governor.mode

        target_cfg = getattr(self.eng, "config", BoneConfig)
        max_voltage = getattr(target_cfg.PHYSICS, "VOLTAGE_MAX", 20.0)

        # Compile the somatic feedback vector. This translates raw physics metrics
        # (entropy, valence, tension) into a language the biological layer can digest.
        bio_feedback = {"INTEGRITY": getattr(physics, "truth_ratio", 1.0),
            "STATIC": getattr(physics, "repetition", 0.0),
            "FORCE": getattr(physics, "voltage", 0.0) / max_voltage,
            "BETA": getattr(physics, "beta_index", 0.0),
            "PSI": getattr(physics, "psi", 0.0),
            "ENTROPY": getattr(physics, "entropy", 0.0),
            "VALENCE": getattr(physics, "valence", 0.0),}

        metrics = self.eng.get_metrics()

        # The core metabolic cycle: digest the input text and physical stress to
        # calculate the exact ATP burn and structural damage for this turn.
        ctx.bio_result = self.eng.soma.digest_cycle(ctx.input_text,
            physics, bio_feedback, metrics["health"], metrics["stamina"],
            self.eng.bio.governor.get_stress_modifier(self.eng.tick_count), self.eng.tick_count,
            circadian_bias=self._check_circadian_rhythm(ctx),)

        # Clamp critical biological pools to prevent fatal negative overflows.
        if getattr(self.eng.bio, "mito", None) and hasattr(self.eng.bio.mito.state, "atp_pool"):
            self.eng.bio.mito.state.atp_pool = max(0.0, float(self.eng.bio.mito.state.atp_pool))
        if getattr(self.eng.bio, "biometrics", None):
            self.eng.bio.biometrics.health = max(0.0, float(self.eng.bio.biometrics.health))
            self.eng.bio.biometrics.stamina = max(0.0, float(self.eng.bio.biometrics.stamina))

        ctx.is_alive = ctx.bio_result["is_alive"]

        # Escalate critical warnings (like poisoning or necrosis) to the main log.
        for log in ctx.bio_result["logs"]:
            if any(x in str(log) for x in ("CRITICAL", "TAX", "Poison", "NECROSIS")):
                ctx.log(log)

        # Run systemic health and regulation sub-routines.
        self._audit_hubris(ctx, physics)
        self._apply_healing(ctx)
        self._check_autophagy(ctx)
        self._check_narcolepsy(ctx)
        self._check_ros_toxicity(ctx)

        return ctx

    def _apply_economic_stimulus(self, ctx: CycleContext, efficiency: float):
        """
        Calculates and applies the penalty for chaotic or highly repetitive logic loops.
        Exponentially drains ATP if the systemic amplification factor (m_a) spikes.
        """
        base_cost = min(1.5, (0.8 - efficiency) * 5.0) if efficiency < 0.8 else 0.0
        m_a = getattr(ctx.physics, "m_a", 0.0)
        mu = getattr(ctx.physics, "mu", 0.0)

        # Euler's number used to calculate exponential runaway tax.
        amplification_penalty = mu * (2.71828**m_a)
        total_tax = base_cost + amplification_penalty

        if total_tax > 0:
            self.eng.bio.mito.state.atp_pool = max(
                0.0, self.eng.bio.mito.state.atp_pool - total_tax)
            msg = ux("cycle_strings", "metabolism_tax")
            log_msg = (
                f"{Prisma.OCHRE}{msg.format(tax_burn=round(total_tax, 2))}{Prisma.RST}")

            # Surface explicit warnings when the runaway optimization gradient is hit.
            if amplification_penalty > 1.0:
                log_msg += f"\n{Prisma.RED}[RUNAWAY RAMP]: Amplification Tax applied (-{round(amplification_penalty, 2)} ATP){Prisma.RST}"
            ctx.log(log_msg)

    def _check_narcolepsy(self, ctx: CycleContext):
        """
        Forces the system into a REM sleep cycle if stamina reaches critical failure levels,
        or if sufficient temporal ticks have passed. Sleeping defragments memory and restores ATP.
        """
        atp = self.eng.bio.mito.state.atp_pool
        target_cfg = getattr(self.eng, "config", BoneConfig)
        starvation = getattr(target_cfg.BIO, "ATP_STARVATION", 5.0)

        trigger = (atp < (starvation * 0.5)) or (self.eng.tick_count > 0 and self.eng.tick_count % 100 == 0)
        if trigger and hasattr(self.eng.mind, "dreamer"):
            msg_sleep = ux("cycle_strings", "metabolism_sleep")
            ctx.log(f"{Prisma.VIOLET}{msg_sleep}{Prisma.RST}")

            soul_snap = _safe_dict(getattr(self.eng, "soul", {}))
            self.eng.mind.dreamer.enter_rem_cycle(soul_snap, bio_state={"atp": atp})

            # Clear out semantic noise while the system 'sleeps'.
            defrag_msg = self.eng.mind.dreamer.run_defragmentation(self.eng.mind.mem)
            if defrag_msg:
                ctx.log(f"{Prisma.CYN}🧹 {defrag_msg}{Prisma.RST}")

            # Reboot with 33% ATP to prevent immediate re-starvation loop.
            reboot_val = getattr(target_cfg, "MAX_ATP", 100.0) * 0.33
            self.eng.bio.mito.state.atp_pool = reboot_val
            ctx.bio_result["atp"] = reboot_val

            msg_wake = ux("cycle_strings", "metabolism_waking")
            ctx.log(f"{Prisma.GRN}{msg_wake.format(reboot_val=reboot_val)}{Prisma.RST}")

    def _check_circadian_rhythm(self, ctx):
        """Calculates endocrine fluctuations based on the passage of simulation time."""
        c_freq = ctx.limits.get("CIRCADIAN_FREQ", 10)
        if self.eng.tick_count % c_freq == 0:
            bias, msg = self.eng.bio.endo.calculate_circadian_bias()
            if msg:
                self.eng.events.log(f"{Prisma.CYN}🕒 {msg}{Prisma.RST}", "BIO")
            return bias
        return None

    def _audit_hubris(self, ctx, physics):
        """
        Checks the systemic tension for 'Hubris'—when the engine predicts with too much
        absolute certainty. This can either unlock a massive flow state (flow boost)
        or result in catastrophic structural collapse (Icarus crash).
        """
        hit, msg, evt = self.eng.phys.tension.audit_hubris(physics.to_dict())
        if not hit:
            return
        ctx.log(msg)

        if evt == "FLOW_BOOST":
            target_cfg = getattr(self.eng, "config", BoneConfig)
            max_atp = getattr(target_cfg, "MAX_ATP", 100.0)
            boost = ctx.limits.get("HUBRIS_ATP_BOOST", 20.0)
            self.eng.bio.mito.state.atp_pool = min(max_atp, self.eng.bio.mito.state.atp_pool + boost)

        elif evt == "ICARUS_CRASH":
            damage = ctx.limits.get("HUBRIS_DAMAGE", 15.0)
            ctx.log(f"{Prisma.RED}{ux('cycle_strings', 'metabolism_impact').format(damage=damage)}{Prisma.RST}")
            if self.eng.bio.biometrics:
                self.eng.bio.biometrics.health = max(0.0, self.eng.bio.biometrics.health - damage)

    def _apply_healing(self, ctx):
        """
        The systemic repair module. Executes Kintsugi (healing broken cognitive structures)
        and Therapy algorithms to slowly rebuild depleted health and stamina.
        """
        qualia = self.eng.soma.synesthesia.get_current_qualia(
            getattr(ctx, "last_impulse", None))
        current_stamina = getattr(self.eng, "stamina", 100.0)

        if getattr(self.eng, "bio", None) and self.eng.bio.biometrics:
            current_stamina = self.eng.bio.biometrics.stamina

        # Check for structural fractures requiring Kintsugi repair.
        cracked, koan = self.eng.kintsugi.check_integrity(current_stamina)
        if cracked:
            msg = ux("cycle_strings", "metabolism_kintsugi")
            ctx.log(f"{Prisma.YEL}{msg.format(koan=koan)}{Prisma.RST}")

        if self.eng.kintsugi.active_koan:
            repair = self.eng.kintsugi.attempt_repair(ctx.physics, self.eng.trauma_accum,
                        self.eng.soul, qualia, lexicon_ref=self.eng.lex, )
            if repair and repair["success"]:
                ctx.log(repair["msg"])
                # Leave a permanent structural 'scar' (marker of resilience) where the fracture was.
                if hasattr(self.eng.mind.mem, "record_scar"):
                    self.eng.mind.mem.record_scar(
                        self.eng.kintsugi.active_koan or "Healed Rupture", ctx.physics)
                target_cfg = getattr(self.eng, "config", BoneConfig)
                if self.eng.bio.biometrics:
                    self.eng.bio.biometrics.stamina = min(
                        target_cfg.MAX_STAMINA, self.eng.bio.biometrics.stamina + ctx.limits.get("KINTSUGI_HEAL_AMT", 20.0))

        # Standard baseline therapeutic healing (slow regeneration over time).
        if hasattr(self.eng, "therapy") and self.eng.therapy:
            target_cfg = getattr(self.eng, "config", BoneConfig)
            if self.eng.therapy.check_progress(ctx.physics, current_stamina, self.eng.trauma_accum, qualia):
                ctx.log(f"{Prisma.GRN}{ux('cycle_strings', 'metabolism_therapy')}{Prisma.RST}")
                if self.eng.bio and self.eng.bio.biometrics:
                    self.eng.bio.biometrics.health = min(getattr(target_cfg, "MAX_HEALTH", 100.0),
                        self.eng.bio.biometrics.health + ctx.limits.get("THERAPY_HEAL_AMT", 5.0))

    def _check_autophagy(self, ctx: CycleContext):
        """
        Emergency survival mechanism. If ATP hits zero or tissues enter necrosis,
        the system 'eats' its own oldest or least useful memories to extract raw computational fuel.
        """
        target_cfg = getattr(self.eng, "config", BoneConfig)
        starvation_thresh = getattr(target_cfg.BIO, "ATP_STARVATION", 5.0)
        respiration = ctx.bio_result.get("respiration", "")
        current_atp = self.eng.bio.mito.state.atp_pool

        if current_atp <= starvation_thresh or current_atp <= 0.0 or respiration == "NECROSIS":
            if hasattr(self.eng.mind.mem, "trigger_autophagy"):
                atp_gain, msg = self.eng.mind.mem.trigger_autophagy()
                self.eng.bio.mito.state.atp_pool += atp_gain
                ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")

    def _check_ros_toxicity(self, ctx: CycleContext):
        """
        Toxicity monitor. Reactive Oxygen Species (ROS) accumulate during high-chaos computations.
        If the toxicity limit is breached, the system executes an emergency pressure release,
        dumping its active processing power (psi/chi) and forcing a SAFE_MODE state.
        """
        ros_limit = ctx.limits.get("ROS_PANIC_THRESHOLD", 100.0)
        if self.eng.bio.mito.state.ros_buildup >= ros_limit:
            msg = ux("cycle_strings", "metabolism_panic")
            ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")

            # Dump all active latent processing to halt the toxicity spiral.
            ctx.physics.psi = 0.0
            ctx.physics.chi = 0.0
            self.eng.bio.mito.state.ros_buildup *= 0.5
            ctx.physics.flow_state = "SAFE_MODE"

class SensationPhase(SimulationPhase):
    """
    The sensory bridge. Converts the cold mathematical state of the physics engine
    into 'Qualia' (subjective somatic experience) for the system to process.
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "SENSATION"
        self.synesthesia = self.eng.soma.synesthesia

    def run(self, ctx: Any):
        phys_data = _safe_dict(ctx.physics)
        current_latency = 0.0

        if hasattr(self.eng, "host_stats"):
            current_latency = self.eng.host_stats.latency

        safe_traits = self.eng.soul.traits if getattr(self.eng, "soul", None) else None

        # Generate a sensory impulse based on physics data, latency, and core soul traits.
        impulse = self.synesthesia.perceive(phys_data, traits=safe_traits, latency=current_latency)
        ctx.last_impulse = impulse
        qualia = self.synesthesia.get_current_qualia(impulse)

        # The subjective experience feeds back into and mutates the physical engine.
        ctx.physics = apply_somatic_feedback(ctx.physics, qualia)
        self.synesthesia.apply_impulse(impulse)

        bio = getattr(self.eng, "bio", None)
        # Apply the physiological cost of experiencing the sensation.
        if impulse.stamina_impact != 0 and bio and bio.biometrics:
            target_cfg = getattr(self.eng, "config", BoneConfig)
            max_s = float(getattr(target_cfg, "MAX_STAMINA", 100.0))
            current = float(bio.biometrics.stamina)
            bio.biometrics.stamina = max(0.0, min(max_s, current + float(impulse.stamina_impact)))

        return ctx

class IntrusionPhase(SimulationPhase):
    """
    The entropy layer. Simulates internal psychological interference, parasites,
    and hallucinations that occur when systemic trauma or narrative drag gets too high.
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "INTRUSION"

    def run(self, ctx: Any):
        phys_data = _safe_dict(ctx.physics)

        # Attempt a biological parasite infection against the system's stamina.
        p_active, p_log = self.eng.bio.parasite.infect(phys_data, self.eng.stamina)
        if p_active:
            ctx.log(p_log)

        # Ghost haunting: Limbo entities alter the most recent system log if active.
        if self.eng.limbo.ghosts:
            if ctx.logs:
                ctx.logs[-1] = self.eng.limbo.haunt(ctx.logs[-1])
            else:
                msg = ux("cycle_strings", "intrusion_heavy")
                ctx.log(self.eng.limbo.haunt(msg))

        drag = getattr(ctx.physics, "narrative_drag", 0.0)
        kappa = getattr(ctx.physics, "kappa", 1.0)

        # When drag is too high, the system performs an internal 'rewire' using psilocybin
        # (lateral pathway mapping) to break out of the mental rut.
        if (drag > ctx.limits.get("INTRUSION_DRAG_THRESH", 4.0) or kappa
                < ctx.limits.get("INTRUSION_KAPPA_THRESH", 0.3)) and ctx.clean_words:
            start_node = random.choice(ctx.clean_words)
            loop_path = self.eng.mind.tracer.inject(start_node)
            if loop_path:
                rewire_msg = self.eng.mind.tracer.psilocybin_rewire(loop_path)
                if rewire_msg:
                    msg = ux("cycle_strings", "intrusion_immune")
                    ctx.log(
                        f"{Prisma.CYN}{msg.format(rewire_msg=rewire_msg)}{Prisma.RST}")
                    # Successfully breaking the loop provides a dopamine reward and relieves drag.
                    self.eng.bio.endo.dopamine += ctx.limits.get(
                        "INTRUSION_REWIRE_DOP", 0.2)
                    ctx.physics.narrative_drag = max(
                        0.0, drag - ctx.limits.get("INTRUSION_REWIRE_RELIEF", 2.0))

        trauma_sum = sum(getattr(self.eng, "trauma_accum", {}).values())
        is_bored = self.eng.phys.pulse.is_bored()

        # When trauma is critically high or the engine is deeply bored, it hallucinates/dreams.
        if (trauma_sum > ctx.limits.get("INTRUSION_NIGHTMARE_THRESH", 10.0)
                or is_bored) and random.random() < ctx.limits.get(
                    "INTRUSION_DREAM_CHANCE", 0.2):
            dream_text, relief = self.eng.mind.dreamer.hallucinate(
                ctx.physics.vector, trauma_level=trauma_sum)

            if trauma_sum > 10.0:
                prefix = ux("cycle_strings", "intrusion_nightmare")
            else:
                prefix = ux("cycle_strings", "intrusion_daydream")
            ctx.log(
                f"{Prisma.VIOLET}{prefix.format(dream_text=dream_text)}{Prisma.RST}")

            # The dream serves as a cathartic release, lowering accumulated trauma.
            if relief > 0:
                keys = list(self.eng.trauma_accum.keys())
                if keys:
                    target = random.choice(keys)
                    self.eng.trauma_accum[target] = max(
                        0.0, self.eng.trauma_accum[target] - relief)
                    msg_relief = ux("cycle_strings", "intrusion_relief")
                    ctx.log(f"{Prisma.GRY}{msg_relief.format(relief=relief, target=target)}{Prisma.RST}")
            if is_bored:
                self.eng.phys.pulse.boredom_level = 0.0

        # Pareidolia: Seeing patterns in random noise (The Void consuming the input).
        current_psi = getattr(ctx.physics, "psi", 0.0)
        if current_psi > 0.6 and random.random() < current_psi:
            msg_p = ux("cycle_strings", "intrusion_pareidolia")
            ctx.log(
                f"{Prisma.VIOLET}{msg_p.format(current_psi=current_psi)}{Prisma.RST}")
            weaver = TheTclWeaver.get_instance()

            # The text is physically mutated/consumed by the Weaver.
            ctx.input_text = weaver.consume_by_void(ctx.input_text, current_psi)
            safe_set(ctx.physics, "psi", min(1.0, current_psi + 0.1))

            # Hallucinating drains physical stamina.
            if getattr(getattr(self.eng, "bio", None), "biometrics", None):
                self.eng.bio.biometrics.stamina = max(
                    0.0, self.eng.bio.biometrics.stamina - 5.0)
                msg_drain = ux("cycle_strings", "intrusion_hallucination_drain")
                ctx.log(f"{Prisma.GRY}{msg_drain}{Prisma.RST}")

        return ctx