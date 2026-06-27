"""phases/biological.py"""

import math
import random
from typing import Any

from constants import Prisma
from core import CycleContext
from mechanics.tools import TheTclWeaver
from phases.base import SimulationPhase, _safe_dict
from physics import apply_somatic_feedback
from presets import BoneConfig
from struts import safe_get, safe_set, ux


class MetabolismPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "METABOLISM"
        cfg = getattr(self.eng, "config", BoneConfig)
        phys_cfg = safe_get(cfg, "PHYSICS", {})
        bio_cfg = safe_get(cfg, "BIO", {})
        self.max_voltage = float(safe_get(phys_cfg, "VOLTAGE_MAX", 20.0))
        self.max_stamina = float(safe_get(cfg, "MAX_STAMINA", 100.0))
        self.max_health = float(safe_get(cfg, "MAX_HEALTH", 100.0))
        self.max_atp = float(safe_get(cfg, "MAX_ATP", 100.0))
        self.starvation_thresh = float(safe_get(bio_cfg, "ATP_STARVATION", 5.0))

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        mode_settings = self.eng.mode_settings
        if not mode_settings.get("atp_drain_enabled", True):
            ctx.bio_result = {
                "is_alive": True,
                "logs": [],
                "atp": self.eng.bio.mito.state.atp_pool,
            }
            ctx.is_alive = True
            self._apply_healing(ctx)
            return ctx
        physics = ctx.physics
        self._apply_economic_stimulus(ctx, self.eng.host_stats.efficiency_index)
        gov_msg = self.eng.bio.governor.shift(
            physics, self.eng.phys.dynamics.voltage_history, self.eng.tick_count
        )
        if gov_msg:
            self.eng.events.log(gov_msg, "GOV")
        physics.manifold = self.eng.bio.governor.mode
        bio_feedback = {
            "INTEGRITY": getattr(physics, "truth_ratio", 1.0),
            "STATIC": getattr(physics, "repetition", 0.0),
            "FORCE": getattr(physics, "voltage", 0.0) / self.max_voltage,
            "BETA": getattr(physics, "beta_index", 0.0),
            "PSI": getattr(physics, "psi", 0.0),
            "ENTROPY": getattr(physics, "entropy", 0.0),
            "VALENCE": getattr(physics, "valence", 0.0),
        }
        metrics = self.eng.get_metrics()
        ctx.bio_result = self.eng.soma.digest_cycle(
            ctx.input_text,
            physics,
            bio_feedback,
            metrics["health"],
            metrics["stamina"],
            self.eng.bio.governor.get_stress_modifier(self.eng.tick_count),
            self.eng.tick_count,
            circadian_bias=self._check_circadian_rhythm(ctx),
        )

        if hasattr(self.eng, "village") and hasattr(self.eng.village, "gordon"):
            scars = getattr(self.eng.village.gordon, "scar_tissue", {})
            if scars:
                streak = getattr(self.eng.observer, "user_turns", 0)
                healed, new_g_pool, msg = self.eng.bio.mito.cellular_repair(
                    streak, self.eng.bio.endo.glimmers, scars
                )
                if healed:
                    self.eng.bio.endo.glimmers = new_g_pool
                    if msg:
                        ctx.bio_result.setdefault("logs", []).append(msg)

        self.eng.set_atp(self.eng._mito_state.atp_pool if self.eng._mito_state else 0.0)
        self.eng.health = max(0.0, self.eng.health)
        self.eng.stamina = max(0.0, self.eng.stamina)
        ctx.is_alive = ctx.bio_result["is_alive"]
        for log in ctx.bio_result["logs"]:
            if any(x in str(log) for x in ("CRITICAL", "TAX", "Poison", "NECROSIS")):
                ctx.log(log)
        self._audit_hubris(ctx, physics)
        self._apply_healing(ctx)
        self._check_autophagy(ctx)
        self._check_narcolepsy(ctx)
        self._check_ros_toxicity(ctx)
        self._calculate_homeostasis_reward(ctx)
        return ctx

    def _calculate_homeostasis_reward(self, ctx: CycleContext):
        """The Reward Signal"""
        try:
            resonance = getattr(ctx.physics, "resonance", 0.0)
            trauma_accum = getattr(self.eng, "trauma_accum", {})
            trauma_sum = (
                sum(trauma_accum.values()) if isinstance(trauma_accum, dict) else 0.0
            )
            atp = (
                self.eng.bio.mito.state.atp_pool
                if getattr(self.eng, "_mito_state", None)
                else 0.0
            )
            reward = 0.0
            if resonance > 0.6 and trauma_sum < 10.0:
                reward += 1.0
            if atp <= self.starvation_thresh or self.eng.stamina <= 0:
                reward -= 1.0

            if reward != 0.0:
                cfg = getattr(self.eng, "config", None)
                if cfg is not None:
                    if isinstance(cfg, dict):
                        current_reward = cfg.get("Q_MATRIX_REWARD", 0.0)
                        cfg["Q_MATRIX_REWARD"] = current_reward + reward
                    else:
                        current_reward = getattr(cfg, "Q_MATRIX_REWARD", 0.0)
                        setattr(cfg, "Q_MATRIX_REWARD", current_reward + reward)

                color = Prisma.GRN if reward > 0 else Prisma.RED
                ctx.log(
                    f"{color}[Q-MATRIX]: Policy evaluated. Homeostasis Reward {reward:+.1f} applied.{Prisma.RST}"
                )
        except Exception as e:
            ctx.log(
                f"{Prisma.RED}[Q-MATRIX ERROR]: Policy evaluation failed: {e}{Prisma.RST}"
            )

    def _apply_economic_stimulus(self, ctx: CycleContext, efficiency: float):
        base_cost = min(1.5, max(0.0, (0.8 - efficiency) * 5.0))
        m_a = getattr(ctx.physics, "m_a", 0.0)
        mu = getattr(ctx.physics, "mu", 0.0)
        amplification_penalty = mu * math.exp(m_a)
        total_tax = base_cost + amplification_penalty
        if total_tax > 0:
            self.eng.drain_atp(total_tax)
            msg = ux("cycle_strings", "metabolism_tax")
            log_msg = (
                f"{Prisma.OCHRE}{msg.format(tax_burn=round(total_tax, 2))}{Prisma.RST}"
            )
            if amplification_penalty > 1.0:
                log_msg += f"\n{Prisma.RED}[RUNAWAY RAMP] Amplification Tax applied (-{round(amplification_penalty, 2)} ATP){Prisma.RST}"
            ctx.log(log_msg)

    def _check_narcolepsy(self, ctx: CycleContext):
        atp = self.eng.bio.mito.state.atp_pool
        trigger = (atp < (self.starvation_thresh * 0.5)) or (
            self.eng.tick_count > 0 and self.eng.tick_count % 100 == 0
        )
        if trigger and self.eng.mind.dreamer:
            msg_sleep = ux("cycle_strings", "metabolism_sleep")
            ctx.log(f"{Prisma.VIOLET}{msg_sleep}{Prisma.RST}")
            soul_snap = _safe_dict(self.eng.soul)
            self.eng.mind.dreamer.enter_rem_cycle(soul_snap, bio_state={"atp": atp})
            defrag_msg = self.eng.mind.dreamer.run_defragmentation(self.eng.mind.mem)
            if defrag_msg:
                ctx.log(f"{Prisma.CYN}{defrag_msg}{Prisma.RST}")
            reboot_val = self.max_atp * 0.33
            self.eng.set_atp(reboot_val)
            ctx.bio_result["atp"] = reboot_val
            msg_wake = ux("cycle_strings", "metabolism_waking")
            ctx.log(f"{Prisma.GRN}{msg_wake.format(reboot_val=reboot_val)}{Prisma.RST}")

    def _check_circadian_rhythm(self, ctx):
        c_freq = ctx.limits.get("CIRCADIAN_FREQ", 10)
        if self.eng.tick_count % c_freq == 0:
            bias, msg = self.eng.bio.endo.calculate_circadian_bias()
            if msg:
                self.eng.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}", "BIO")
            return bias
        return None

    def _audit_hubris(self, ctx, physics):
        hit, msg, evt = self.eng.phys.tension.audit_hubris(physics.to_dict())
        if not hit:
            return
        ctx.log(msg)
        if evt == "FLOW_BOOST":
            boost = ctx.limits.get("HUBRIS_ATP_BOOST", 20.0)
            self.eng.restore_atp(boost)
        elif evt == "ICARUS_CRASH":
            damage = ctx.limits.get("HUBRIS_DAMAGE", 15.0)
            ctx.log(
                f"{Prisma.RED}{ux('cycle_strings', 'metabolism_impact').format(damage=damage)}{Prisma.RST}"
            )
            self.eng.health = max(0.0, self.eng.health - damage)

    def _apply_healing(self, ctx):
        qualia = self.eng.soma.synesthesia.get_current_qualia(ctx.last_impulse)
        current_stamina = self.eng.stamina
        kintsugi_ref = getattr(self.eng.village, "kintsugi", None)
        if kintsugi_ref:
            cracked, koan = kintsugi_ref.check_integrity(current_stamina)
            if cracked:
                msg = ux("cycle_strings", "metabolism_kintsugi")
                ctx.log(f"{Prisma.YEL}{msg.format(koan=koan)}{Prisma.RST}")
            if kintsugi_ref.active_koan:
                repair = kintsugi_ref.attempt_repair(
                    ctx.physics,
                    self.eng.trauma_accum,
                    self.eng.soul,
                    qualia,
                    lexicon_ref=self.eng.lex,
                )
                if repair and repair["success"]:
                    ctx.log(repair["msg"])
                    self.eng.mind.mem.record_scar(
                        kintsugi_ref.active_koan or "Healed Rupture", ctx.physics
                    )
                self.eng.stamina = min(
                    self.max_stamina,
                    self.eng.stamina + ctx.limits.get("KINTSUGI_HEAL_AMT", 20.0),
                )
        therapy_ref = getattr(self.eng.village, "therapy", None)
        if therapy_ref:
            if therapy_ref.check_progress(
                ctx.physics, current_stamina, self.eng.trauma_accum, qualia
            ):
                ctx.log(
                    f"{Prisma.GRN}{ux('cycle_strings', 'metabolism_therapy')}{Prisma.RST}"
                )
                self.eng.health = min(
                    self.max_health,
                    self.eng.health + ctx.limits.get("THERAPY_HEAL_AMT", 5.0),
                )

    def _check_autophagy(self, ctx: CycleContext):
        respiration = ctx.bio_result.get("respiration", "")
        current_atp = self.eng.bio.mito.state.atp_pool
        if current_atp <= self.starvation_thresh or respiration == "NECROSIS":
            atp_gain, msg = self.eng.mind.mem.trigger_autophagy()
            self.eng.bio.mito.adjust_atp(atp_gain, "Autophagy")
            ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")
            if atp_gain <= 0.0 and self.eng.bio.mito.state.atp_pool <= 0.0:
                ctx.is_alive = False
                ctx.log(
                    f"{Prisma.RED}[TERMINAL]: Autophagy failed. Biological starvation imminent.{Prisma.RST}"
                )

    def _check_ros_toxicity(self, ctx: CycleContext):
        ros_limit = ctx.limits.get("ROS_PANIC_THRESHOLD", 100.0)
        if self.eng.bio.mito.state.ros_buildup >= ros_limit:
            msg = ux("cycle_strings", "metabolism_panic")
            ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")
            ctx.physics.psi = 0.0
            ctx.physics.chi = 0.0
            self.eng.bio.mito.state.ros_buildup *= 0.5
            ctx.physics.flow_state = "SAFE_MODE"


class SensationPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "SENSATION"
        self.synesthesia = self.eng.soma.synesthesia
        self.max_stamina = float(
            safe_get(getattr(self.eng, "config", BoneConfig), "MAX_STAMINA", 100.0)
        )

    def run(self, ctx: Any):
        phys_data = ctx.physics.to_dict()
        current_latency = getattr(
            getattr(self.eng, "observer", None), "last_cycle_duration", 0.0
        )
        impulse = self.synesthesia.perceive(
            phys_data, traits=self.eng.soul.traits, latency=current_latency
        )
        ctx.last_impulse = impulse
        qualia = self.synesthesia.get_current_qualia(impulse)
        ctx.physics = apply_somatic_feedback(ctx.physics, qualia)
        self.synesthesia.apply_impulse(impulse)
        if impulse.stamina_impact != 0:
            current = self.eng.stamina
            self.eng.stamina = max(
                0.0, min(self.max_stamina, current + float(impulse.stamina_impact))
            )
        return ctx


class IntrusionPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "INTRUSION"

    def run(self, ctx: Any):
        phys_data = ctx.physics.to_dict()
        p_active, p_log = self.eng.bio.parasite.infect(phys_data, self.eng.stamina)
        if p_active:
            ctx.log(p_log)
        limbo_ref = getattr(self.eng.village, "limbo", None)
        if limbo_ref and limbo_ref.ghosts:
            if ctx.logs:
                ctx.logs[-1] = limbo_ref.haunt(ctx.logs[-1])
            else:
                msg = ux("cycle_strings", "intrusion_heavy")
                ctx.log(limbo_ref.haunt(msg))
        drag = getattr(ctx.physics, "narrative_drag", 0.0)
        kappa = getattr(ctx.physics, "kappa", 1.0)
        trauma_sum = sum(getattr(self.eng, "trauma_accum", {}).values())
        is_bored = self.eng.phys.pulse.is_bored()
        if (
            trauma_sum > ctx.limits.get("INTRUSION_NIGHTMARE_THRESH", 10.0) or is_bored
        ) and random.random() < ctx.limits.get("INTRUSION_DREAM_CHANCE", 0.2):
            dream_text, relief = self.eng.mind.dreamer.hallucinate(
                ctx.physics.vector, trauma_level=trauma_sum
            )
            if trauma_sum > 10.0:
                prefix = ux("cycle_strings", "intrusion_nightmare")
            else:
                prefix = ux("cycle_strings", "intrusion_daydream")
            ctx.log(
                f"{Prisma.VIOLET}{prefix.format(dream_text=dream_text)}{Prisma.RST}"
            )
            if relief > 0:
                keys = list(self.eng.trauma_accum.keys())
                if keys:
                    target = random.choice(keys)
                    self.eng.trauma_accum[target] = max(
                        0.0, self.eng.trauma_accum[target] - relief
                    )
                    if self.eng.trauma_accum[target] <= 0.0:
                        del self.eng.trauma_accum[target]
                    msg_relief = ux("cycle_strings", "intrusion_relief")
                    ctx.log(
                        f"{Prisma.GRY}{msg_relief.format(relief=relief, target=target)}{Prisma.RST}"
                    )
            if is_bored:
                self.eng.phys.pulse.boredom_level = 0.0
        current_psi = getattr(ctx.physics, "psi", 0.0)
        if current_psi > 0.6 and random.random() < current_psi:
            msg_p = ux("cycle_strings", "intrusion_pareidolia")
            ctx.log(
                f"{Prisma.VIOLET}{msg_p.format(current_psi=current_psi)}{Prisma.RST}"
            )
            weaver = TheTclWeaver.get_instance()
            ctx.input_text = weaver.consume_by_void(ctx.input_text, current_psi)
            ctx.physics.psi = min(1.0, current_psi + 0.1)
            self.eng.stamina = max(0.0, self.eng.stamina - 5.0)
            msg_drain = ux("cycle_strings", "intrusion_hallucination_drain")
            ctx.log(f"{Prisma.GRY}{msg_drain}{Prisma.RST}")
        return ctx
