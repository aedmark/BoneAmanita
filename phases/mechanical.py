"""phases/mechanical.py"""

from constants import Prisma
from typing import Any
from presets import BoneConfig
from physics import TheGatekeeper
from core import LoreManifest, CycleContext
from struts import ux
from mechanics.projector import SoulDashboard
from phases.base import SimulationPhase, _safe_dict, _deep_update

class MaintenancePhase(SimulationPhase):
    """
    The Routine Upkeep Layer.

    This phase simulates background systemic processes that run on specific time intervals
    (ticks). It triggers the 'Town Hall' to run a census, consult the almanac for weather
    (environmental shifts), and diagnose the holistic balance of the system.
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MAINTENANCE"

    def run(self, ctx: CycleContext):
        # The 'Garden' represents latent, long-term conceptual seeds planted by the user.
        if hasattr(self.eng, "town_hall"):
            blooms = self.eng.town_hall.tend_garden(ctx.clean_words) or []
            for bloom in blooms:
                ctx.log(bloom)

            w_freq = ctx.limits.get("MAINTENANCE_WEATHER_FREQ", 5)
            c_freq = ctx.limits.get("MAINTENANCE_CENSUS_FREQ", 20)

            # Periodic weather shifts alter the baseline physics context.
            if self.eng.tick_count % w_freq == 0:
                weather_report = self.eng.town_hall.consult_almanac(ctx.physics)
                if weather_report:
                    ctx.log(f"{Prisma.CYN}{weather_report}{Prisma.RST}")

            # The Census gathers holistic metrics about the system's health and diversity.
            is_census_due = (self.eng.tick_count > 0
                             and self.eng.tick_count % c_freq == 0)
            if is_census_due or "census" in ctx.clean_words:
                report = self.eng.town_hall.conduct_census(ctx.physics, self.eng.host_stats)
                if report:
                    msg = ux("cycle_strings", "town_hall_report")
                    ctx.log(f"{Prisma.CYN}{msg.format(report=report)}{Prisma.RST}")

            # Diagnostic check on the relationship between accumulated trauma and host health.
            session_snapshot = {"trauma_vector": self.eng.trauma_accum, "meta": {"final_health": self.eng.health},}
            status, advice = self.eng.town_hall.diagnose_condition(session_data=session_snapshot,
                _host_health=self.eng.bio.biometrics if self.eng.bio else None, soul=self.eng.soul,)

            if status != "BALANCED":
                msg = (ux("cycle_strings", "town_hall_vitals")
                       or "[TOWN HALL] {status}: {advice}")
                ctx.log(f"{Prisma.OCHRE}{msg.format(status=status, advice=advice)}{Prisma.RST}")

        # Simulates the background decay and growth of old memory nodes.
        if self.eng.mind and hasattr(self.eng.mind, "mem"):
            if hasattr(self.eng.mind.mem, "run_ecosystem"):
                eco_logs = self.eng.mind.mem.run_ecosystem(_safe_dict(ctx.physics), self.eng.stamina, self.eng.tick_count)
                for log in eco_logs:
                    ctx.log(log)

        return ctx

class GatekeeperPhase(SimulationPhase):
    """
    The Structural Firewall.

    This phase acts as a rigid boundary enforcer. It ensures logical consistency
    (object-action coupling), audits the prompt for bureaucratic 'red tape',
    and checks if the user has lost their 'agency' privileges due to toxic inputs.
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "GATEKEEP"
        target_cfg = getattr(self.eng, "config", BoneConfig)
        self.gatekeeper = TheGatekeeper(self.eng.lex, config_ref=target_cfg)

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx

        anchor = getattr(getattr(self.eng, "soul", None), "anchor", None)

        # Agency Lock: If the user has repeatedly abused the system or violated safety
        # bounds, the system locks them out until they pass a 'humanity' (sincerity) check.
        if anchor and anchor.agency_lock:
                passed = anchor.assess_humanity(ctx.input_text)
                if not passed:
                    dash_view = SoulDashboard(self.eng).render()
                    ctx.refusal_triggered = True
                    msg = ux("cycle_strings", "gatekeep_locked")
                    log_msg = ux("cycle_strings", "gatekeep_log_agency")
                    ctx.refusal_packet = {"ui": f"{dash_view}\n\n{Prisma.RED}{msg}{Prisma.RST}", "logs": [log_msg] if log_msg else [],
                        "metrics": self.eng.get_metrics(),}
                    return ctx

        # Object-Action Coupling Enforcer (Gordon's Wall).
        # You cannot execute a logical action on an object that does not exist in the space.
        if self.eng.gordon:
            current_zone = getattr(ctx.physics, "zone", "UNKNOWN")
            coupling_error = self.eng.gordon.enforce_object_action_coupling(
                ctx.input_text, current_zone)

            if coupling_error:
                log_msg = (ux("cycle_strings", "gatekeep_log_premise") or f"Premise Violation: {coupling_error}")
                ctx.log(f"{Prisma.OCHRE}[GORDON] {log_msg}. Applying massive Narrative Drag.{Prisma.RST}")
                current_drag = float(getattr(ctx.physics, "narrative_drag", 0.0))
                max_drag = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "DRAG_MAX")

                # Apply immense friction to halt the false logic from propagating.
                setattr(ctx.physics, "narrative_drag", min(max_drag, current_drag + 50.0))

                # Instruct the downstream LLM to physically roleplay the failure of the action.
                ctx.council_mandates.append({"action": "STYLE_INJECTION",
                    "log": f"CRITICAL CONTEXT: The user attempted an impossible action ({coupling_error}). Do NOT fulfill the action. React to their failure in-character based on your current archetype."})

        # Check standard dictionary/lexicon-based boundary violations.
        is_allowed, refusal_packet = self.gatekeeper.check_entry(ctx)
        if not is_allowed:
            ctx.refusal_triggered = True
            ctx.refusal_packet = refusal_packet
            return ctx

        # The Bureaucracy Audit. Evaluates if the prompt is overly complex, corporatized,
        # or bogged down in unnecessary "red tape".
        if self.eng.bureau:
            current_bio = self.eng.get_metrics()
            audit_result = self.eng.bureau.audit(_safe_dict(ctx.physics), current_bio, origin="USER")
            if audit_result:
                # The Bureau can outright block a prompt if it violates internal compliance rules.
                if audit_result.get("block", False):
                    ctx.refusal_triggered = True
                    ui_msg = audit_result.get(
                        "ui", ux("cycle_strings", "gatekeep_bureau_injunction"))
                    log_msg = ux("cycle_strings", "gatekeep_log_bureau_block")
                    ctx.refusal_packet = {"type": "BUREAU_BLOCK",
                        "ui": ui_msg,
                        "logs": [log_msg] if log_msg else [],
                        "metrics": getattr(self.eng, "get_metrics", lambda: {})(),}
                    return ctx

                # The Bureau taxes the system's ATP (stamina) for processing bureaucratic requests.
                if self.eng.bio and self.eng.bio.mito:
                    self.eng.bio.mito.adjust_atp(
                        audit_result.get("atp_gain", 0.0),
                        ux("cycle_strings", "gatekeep_bureau_fine"),)
                if audit_result.get("log"):
                    ctx.log(audit_result["log"])
                if audit_result.get("ui"):
                    ctx.bureau_ui = audit_result["ui"]
                    ctx.is_bureaucratic = True

        return ctx

class MachineryPhase(SimulationPhase):
    """
    The Internal Industrial Layer.

    This phase handles the chaotic, transformative modules: The Forge (item crafting),
    The Crucible (heat/meltdowns), The Theremin (ambient noise monitoring), and
    The Critics (evaluating systemic performance).
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MACHINERY"

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        phys_dict = _safe_dict(ctx.physics)

        # The Critics Circle: Autonomous agents that review the system's current logic state.
        if getattr(self.eng, "critics", None) and (review := self.eng.critics.audit_performance(phys_dict, self.eng.tick_count)):
            ctx.log(review)
            good_icon = ux("cycle_strings", "machinery_critic_good_icon")
            # Praise lowers friction; harsh critiques raise it.
            ctx.physics.narrative_drag += -1.0 if good_icon in review else 1.0

        _, z_msg = 0.0, None

        # Zen Module: Raking the sand clears systemic noise and boosts baseline efficiency.
        if getattr(self.eng, "zen", None):
            boost, z_msg = self.eng.zen.raking_the_sand(phys_dict, ctx.bio_result)
            if z_msg: ctx.log(z_msg)
            if boost > 0:
                self.eng.bio.mito.state.membrane_potential = min(2.0, self.eng.bio.mito.state.efficiency_mod + (boost * 0.1))

        # The Forge: Attempt to combine inventory items based on current contextual physics.
        if self.eng.gordon and self.eng.gordon.inventory:
            self._process_crafting(ctx, phys_dict)

        if t_msg := self.eng.phys.forge.transmute(phys_dict): ctx.log(t_msg)

        _, f_msg, new_item = self.eng.phys.forge.hammer_alloy(phys_dict)
        if f_msg: ctx.log(f_msg)
        if new_item and self.eng.gordon:
            ctx.log(self.eng.gordon.acquire(new_item))

        # The Theremin: Monitors the ambient 'noise' (entropy) of the logic stream.
        # If the noise becomes chaotic and destructive, it triggers an 'Airstrike'.
        _, _, t_msg, t_crit = self.eng.phys.theremin.listen(phys_dict, self.eng.bio.governor.mode)
        if t_msg: ctx.log(t_msg)
        if t_crit == "AIRSTRIKE": self._handle_theremin_discharge(ctx)

        # Update the heartbeat of the physics engine based on repetition and stress.
        self.eng.phys.pulse.update(getattr(ctx.physics, "repetition", 0.0), ctx.physics.voltage)

        # The Crucible: Measures pure logical tension (Heat).
        # Extreme tension causes a Meltdown, physically damaging the host system.
        c_state, c_val, c_msg = self.eng.phys.crucible.audit_fire(phys_dict)
        if c_msg: ctx.log(c_msg)
        if c_state == "MELTDOWN" and getattr(getattr(self.eng, "bio", None), "biometrics", None):
            self.eng.bio.biometrics.health = max(0.0, self.eng.bio.biometrics.health - c_val)

        _deep_update(ctx.physics, phys_dict)
        return ctx

    def _process_crafting(self, ctx, phys_dict):
        """
        Calculates if the current environment and semantic vector match the recipe
        requirements to fuse items in the user's inventory into a new tool.
        """
        is_craft, craft_msg, old_item, new_item = self.eng.phys.forge.attempt_crafting(
            phys_dict, self.eng.gordon.inventory)
        if is_craft:
            ctx.log(craft_msg)
            vec = ctx.physics.vector
            catalyst_cat = max(vec, key=vec.get) if vec else "void"
            self.eng.events.publish("FORGE_SUCCESS",
                {"ingredient": old_item, "catalyst": catalyst_cat, "result": new_item},)
            if old_item in self.eng.gordon.inventory:
                self.eng.gordon.inventory.remove(old_item)
            ctx.log(self.eng.gordon.acquire(new_item))

    def _handle_theremin_discharge(self, ctx):
        """
        Executes an 'Airstrike'. An extreme penalty applied when the system detects
        runaway chaotic logic loops. Shaves off 20% of the system's max health instantly.
        """
        target_cfg = getattr(self.eng, "config", BoneConfig)
        max_hp = getattr(target_cfg, "MAX_HEALTH", 100.0)
        damage = max_hp * 0.20
        if getattr(self.eng, "bio", None) and self.eng.bio.biometrics:
            self.eng.bio.biometrics.health = max(
                0.0, self.eng.bio.biometrics.health - damage)

        msg = ux("cycle_strings", "machinery_theremin")
        ctx.log(f"{Prisma.RED}{msg.format(damage=damage)}{Prisma.RST}")

        if hasattr(self.eng.events, "publish"):
            self.eng.events.publish("AIRSTRIKE", {"damage": damage, "source": "THEREMIN"})

class StabilizationPhase(SimulationPhase):
    """
    The PID Controller Layer.

    This phase acts as a mathematical dampener. It reads the extreme spikes in
    the engine's physics and endocrine systems, and applies fractional corrections
    to prevent the variables from spiraling into NaN or out-of-bounds states.
    """
    def __init__(self, engine_ref, stabilizer_ref):
        super().__init__(engine_ref)
        self.name = "STABILIZATION"
        self.stabilizer = stabilizer_ref

    def run(self, ctx: Any):
        if hasattr(self.stabilizer, "stabilize"):
            endo = getattr(self.eng.bio, "endo", None) if getattr(self.eng, "bio", None) else None
            # Evaluate and clamp wild swings in the physics vector.
            applied = self.stabilizer.stabilize(ctx.physics, endocrine_state=endo)
            if applied:
                ctx.record_flux(self.name, "PID_CORRECTION", 0.0, 1.0, "STABILIZER_APPLIED")
        return ctx