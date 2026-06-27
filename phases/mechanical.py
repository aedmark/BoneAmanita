"""phases/mechanical.py"""

from typing import Any

from constants import Prisma
from core import CycleContext, LoreManifest
from mechanics.projector import SoulDashboard
from phases.base import SimulationPhase, _deep_update, _safe_dict
from physics import TheGatekeeper
from struts import safe_get, ux


class MaintenancePhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MAINTENANCE"

    def run(self, ctx: CycleContext):
        if hasattr(self.eng, "town_hall"):
            blooms = self.eng.town_hall.tend_garden(ctx.clean_words) or []
            for bloom in blooms:
                ctx.log(bloom)
            w_freq = ctx.limits.get("MAINTENANCE_WEATHER_FREQ", 5)
            c_freq = ctx.limits.get("MAINTENANCE_CENSUS_FREQ", 20)
            if self.eng.tick_count % w_freq == 0:
                weather_report = self.eng.town_hall.consult_almanac(ctx.physics)
                if weather_report:
                    ctx.log(f"{Prisma.CYN}{weather_report}{Prisma.RST}")
            is_census_due = (
                self.eng.tick_count > 0 and self.eng.tick_count % c_freq == 0
            )
            if is_census_due or "census" in ctx.clean_words:
                report = self.eng.town_hall.conduct_census(
                    ctx.physics, self.eng.host_stats
                )
                if report:
                    msg = ux("cycle_strings", "town_hall_report")
                    ctx.log(f"{Prisma.CYN}{msg.format(report=report)}{Prisma.RST}")
            session_snapshot = {
                "trauma_vector": self.eng.trauma_accum,
                "meta": {"final_health": self.eng.health},
            }
            status, advice = self.eng.town_hall.diagnose_condition(
                session_data=session_snapshot,
                _host_health=self.eng.bio.biometrics,
                soul=self.eng.soul,
            )
            if status != "BALANCED":
                msg = (
                    ux("cycle_strings", "town_hall_vitals")
                    or "[TOWN HALL] {status}: {advice}"
                )
                ctx.log(
                    f"{Prisma.OCHRE}{msg.format(status=status, advice=advice)}{Prisma.RST}"
                )
        eco_logs = self.eng.mind.mem.run_ecosystem(
            _safe_dict(ctx.physics), self.eng.stamina, self.eng.tick_count
        )
        for log in eco_logs:
            ctx.log(log)
        return ctx


class GatekeeperPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "GATEKEEP"
        self.gatekeeper = TheGatekeeper(self.eng.lex, config_ref=self.eng.config)
        self.max_drag = float(
            LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "DRAG_MAX") or 100.0
        )

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        anchor = self.eng.soul.anchor
        if anchor and anchor.agency_lock:
            passed = anchor.assess_humanity(ctx.input_text)
            if not passed:
                dash_view = SoulDashboard(self.eng).render()
                ctx.refusal_triggered = True
                msg = ux("cycle_strings", "gatekeep_locked")
                log_msg = ux("cycle_strings", "gatekeep_log_agency")
                ctx.refusal_packet = {
                    "ui": f"{dash_view}\n\n{Prisma.RED}{msg}{Prisma.RST}",
                    "logs": [log_msg] if log_msg else [],
                    "metrics": self.eng.get_metrics(),
                }
                return ctx
        gordon = getattr(self.eng.village, "gordon", None)
        if gordon:
            current_zone = getattr(ctx.physics, "zone", "UNKNOWN")
            coupling_error = gordon.enforce_object_action_coupling(
                ctx.input_text, current_zone
            )
            if coupling_error:
                log_msg = (
                    ux("cycle_strings", "gatekeep_log_premise")
                    or f"Premise Violation: {coupling_error}"
                )
                ctx.log(
                    f"{Prisma.OCHRE}[GORDON] {log_msg}. Applying massive Narrative Drag and Somatic Shock.{Prisma.RST}"
                )
                current_drag = float(getattr(ctx.physics, "narrative_drag", 0.0))
                ctx.physics.narrative_drag = min(self.max_drag, current_drag + 50.0)
                shock_damage = 15.0
                if hasattr(self.eng, "bio") and hasattr(self.eng.bio, "mito"):
                    self.eng.bio.mito.state.atp_pool = max(
                        0.0, self.eng.bio.mito.state.atp_pool - shock_damage
                    )
                    ctx.log(
                        f"{Prisma.RED}[BIOLOGY] Somatic Shock detected. Burned {shock_damage} ATP.{Prisma.RST}"
                    )
                    if hasattr(self.eng.bio, "somatic"):
                        current_echo = getattr(
                            self.eng.bio.somatic, "somatic_echo", 0.0
                        )
                        self.eng.bio.somatic.somatic_echo = min(1.0, current_echo + 0.8)
                elif hasattr(self.eng, "stamina"):
                    self.eng.stamina = max(0.0, self.eng.stamina - shock_damage)
                    ctx.log(
                        f"{Prisma.RED}[BIOLOGY] Somatic Shock detected. Burned {shock_damage} Stamina.{Prisma.RST}"
                    )
                ctx.council_mandates.append(
                    {
                        "action": "STYLE_INJECTION",
                        "log": f"CRITICAL CONTEXT: The user attempted an impossible action ({coupling_error}). Do NOT fulfill the action. React to their failure in-character based on your current archetype.",
                    }
                )
        is_allowed, refusal_packet = self.gatekeeper.check_entry(ctx)
        if not is_allowed:
            ctx.refusal_triggered = True
            ctx.refusal_packet = refusal_packet
            return ctx
        bureau = getattr(self.eng.village, "bureau", None)
        if bureau:
            current_bio = self.eng.get_metrics()
            audit_result = bureau.audit(
                _safe_dict(ctx.physics), current_bio, origin="USER"
            )
            if audit_result:
                if audit_result.get("block", False):
                    ctx.refusal_triggered = True
                    ui_msg = audit_result.get(
                        "ui", ux("cycle_strings", "gatekeep_bureau_injunction")
                    )
                    log_msg = ux("cycle_strings", "gatekeep_log_bureau_block")
                    ctx.refusal_packet = {
                        "type": "BUREAU_BLOCK",
                        "ui": ui_msg,
                        "logs": [log_msg] if log_msg else [],
                        "metrics": self.eng.get_metrics(),
                    }
                    return ctx
                self.eng.bio.mito.adjust_atp(
                    audit_result.get("atp_gain", 0.0),
                    ux("cycle_strings", "gatekeep_bureau_fine"),
                )
                if audit_result.get("log"):
                    ctx.log(audit_result["log"])
                if audit_result.get("ui"):
                    ctx.bureau_ui = audit_result["ui"]
                    ctx.is_bureaucratic = True
        return ctx


class MachineryPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MACHINERY"

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        phys_dict = _safe_dict(ctx.physics)
        critics_ref = getattr(self.eng.village, "critics", None)
        if critics_ref and (
            review := critics_ref.audit_performance(phys_dict, self.eng.tick_count)
        ):
            ctx.log(review)
            good_icon = ux("cycle_strings", "machinery_critic_good_icon")
            ctx.physics.narrative_drag += -1.0 if good_icon in review else 1.0
        _, z_msg = 0.0, None
        zen_ref = getattr(self.eng.village, "zen", None)
        if zen_ref:
            boost, z_msg = zen_ref.raking_the_sand(phys_dict, ctx.bio_result)
            if z_msg:
                ctx.log(z_msg)
            if boost > 0:
                self.eng.bio.mito.state.membrane_potential = min(
                    2.0, self.eng.bio.mito.state.efficiency_mod + (boost * 0.1)
                )
        gordon = getattr(self.eng.village, "gordon", None)
        if gordon is not None and getattr(gordon, "inventory", None):
            self._process_crafting(ctx, phys_dict, gordon)
        if t_msg := self.eng.phys.forge.transmute(phys_dict):
            ctx.log(t_msg)
        _, f_msg, new_item = self.eng.phys.forge.hammer_alloy(phys_dict)
        if f_msg:
            ctx.log(f_msg)
        if new_item and gordon:
            ctx.log(gordon.acquire(new_item))
        _, _, t_msg, t_crit = self.eng.phys.theremin.listen(
            phys_dict, self.eng.bio.governor.mode
        )
        if t_msg:
            ctx.log(t_msg)
        if t_crit == "AIRSTRIKE":
            self._handle_theremin_discharge(ctx)
        self.eng.phys.pulse.update(
            getattr(ctx.physics, "repetition", 0.0), ctx.physics.voltage
        )
        c_state, c_val, c_msg = self.eng.phys.crucible.audit_fire(phys_dict)
        if c_msg:
            ctx.log(c_msg)
        if c_state == "MELTDOWN":
            self.eng.health = max(0.0, self.eng.health - c_val)
        _deep_update(ctx.physics, phys_dict)
        return ctx

    def _process_crafting(self, ctx: Any, phys_dict: dict, gordon: Any):
        is_craft, craft_msg, old_item, new_item = self.eng.phys.forge.attempt_crafting(
            phys_dict, gordon.inventory
        )
        if is_craft:
            ctx.log(craft_msg)
            vec = ctx.physics.vector
            catalyst_cat = max(vec, key=lambda k: float(vec[k])) if vec else "void"
            self.eng.events.publish(
                "FORGE_SUCCESS",
                {"ingredient": old_item, "catalyst": catalyst_cat, "result": new_item},
            )
            if old_item in gordon.inventory:
                gordon.inventory.remove(old_item)
            ctx.log(gordon.acquire(new_item))

    def _handle_theremin_discharge(self, ctx):
        max_hp = float(safe_get(self.eng.config, "MAX_HEALTH", 100.0))
        damage = max_hp * 0.20
        self.eng.health = max(0.0, self.eng.health - damage)
        msg = ux("cycle_strings", "machinery_theremin")
        ctx.log(f"{Prisma.RED}{msg.format(damage=damage)}{Prisma.RST}")
        self.eng.events.publish("AIRSTRIKE", {"damage": damage, "source": "THEREMIN"})


class StabilizationPhase(SimulationPhase):
    def __init__(self, engine_ref, stabilizer_ref):
        super().__init__(engine_ref)
        self.name = "STABILIZATION"
        self.stabilizer = stabilizer_ref

    def run(self, ctx: Any):
        applied = self.stabilizer.stabilize(
            ctx.physics, endocrine_state=self.eng.bio.endo
        )
        if applied:
            ctx.record_flux(self.name, "PID_CORRECTION", 0.0, 1.0, "STABILIZER_APPLIED")
        return ctx
