"""bone_cycle.py"""

import random
import re
import time
import traceback
import uuid
from typing import Dict, Any, List

from bone_body import SynestheticCortex
from bone_config import BoneConfig, BonePresets
from bone_core import ArchetypeArbiter, LoreManifest, ux
from bone_drivers import CongruenceValidator
from bone_gui import SoulDashboard, CycleReporter
from bone_machine import PanicRoom
from bone_physics import TheGatekeeper, apply_somatic_feedback, CycleStabilizer
from bone_symbiosis import SymbiosisManager
from bone_types import Prisma, CycleContext

class SimulationPhase:
    """The base class for the 14-step metabolic cycle. Each phase takes a CycleContext, mutates it, and returns it."""
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.name = "GENERIC_PHASE"

    def run(self, ctx: CycleContext) -> CycleContext:
        raise NotImplementedError

class ObservationPhase(SimulationPhase):
    """
    Phase 1. The system "looks" at the user's input. It calculates the initial 
    physics vectors (Voltage, Drag, Sentiment) using lexical analysis before the LLM ever sees the text.
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "OBSERVE"

    def run(self, ctx: CycleContext):
        if self.eng.gordon and "GORDON" not in self.eng.suppressed_agents:
            if "TCL9_QUANTUM_COMB" in self.eng.gordon.inventory:
                from bone_tcl import TheTclWeaver
                weaver = TheTclWeaver.get_instance()
                original_text = ctx.input_text
                ctx.input_text = weaver.quantum_comb(ctx.input_text)
                if original_text != ctx.input_text:
                    ctx.log(f"{Prisma.CYN}🪮 QUANTUM COMB: Fluff stripped -> '{ctx.input_text}'{Prisma.RST}")
            loot_candidate = self.eng.gordon.parse_loot(ctx.input_text, "")
            if loot_candidate:
                acquire_msg = self.eng.gordon.acquire(loot_candidate)
                ctx.log(acquire_msg)
        gaze_result = self.eng.phys.observer.gaze(ctx.input_text, self.eng.mind.mem.graph)
        input_phys = gaze_result["physics"]
        transfer_keys = {"clean_words", "counts", "vector", "valence", "entropy", "beta", "S", "D", "C", "PHI_RES",
                         "DELTA", "LQ", "ROS", "G", "raw_text", "antigens", "psi", "kappa", "zone", "flow_state",
                         "repetition", }
        for k in transfer_keys:
            if hasattr(input_phys, k):
                setattr(ctx.physics, k, getattr(input_phys, k))
        if (obs_v := getattr(input_phys, "voltage", 0.0)) > 0:
            ctx.physics.voltage += obs_v * 0.5
        curr_d = max(0.1, ctx.physics.narrative_drag)
        input_d = getattr(input_phys, "narrative_drag", 0.0)
        ctx.physics.narrative_drag = (curr_d * 0.7) + (input_d * 0.3)
        ctx.clean_words = gaze_result["clean_words"]
        current_atp = self.eng.bio.mito.state.atp_pool
        cfg = getattr(BoneConfig, "CYCLE", None)
        atp_warn = getattr(cfg, "OBSERVE_ATP_WARN", 15.0) if cfg else 15.0
        if current_atp < atp_warn:
            msg = ux("cycle_strings", "observe_low_energy")
            ctx.log(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
        if hasattr(self.eng, "symbiosis"):
            diag = self.eng.symbiosis.current_health.diagnosis
            if diag != "STABLE":
                msg = ux("cycle_strings", "observe_symbiont")
                ctx.log(f"{Prisma.OCHRE}{msg.format(diag=diag)}{Prisma.RST}")
        if hasattr(self.eng, "shared_lattice") and not ctx.is_system_event:
            shared_logs, atp_cost = self.eng.shared_lattice.infer_and_couple(text=ctx.input_text, sys_phys=ctx.physics,
                                                                             input_phys=input_phys,
                                                                             atp_pool=current_atp)
            for s_log in shared_logs:
                ctx.log(s_log)
            if atp_cost > 0 and self.eng.bio and self.eng.bio.mito:
                self.eng.bio.mito.adjust_atp(-atp_cost, "Carrier Mode (System lent stamina to User)")
        self.eng.phys.dynamics.commit(ctx.physics.voltage)
        self.eng.tick_count += 1
        return ctx

class SanctuaryPhase(SimulationPhase):
    """
    Phase 5. If the user creates a "safe" lexical environment and trauma is low,
    the system enters Sanctuary, accelerating healing and increasing the chance of dreaming.
    """
    def __init__(self, engine_ref, governor_ref):
        super().__init__(engine_ref)
        self.name = "SANCTUARY"
        self.governor = governor_ref

    def run(self, ctx: CycleContext):
        in_safe_zone, distance = self.governor.assess(ctx.physics)
        trauma_sum = (
            sum(self.eng.trauma_accum.values())
            if getattr(self.eng, "trauma_accum", None)
            else 0.0)
        cfg = getattr(BoneConfig, "CYCLE", None)
        t_limit = getattr(cfg, "SANCTUARY_TRAUMA_LIMIT", 25.0) if cfg else 25.0
        if in_safe_zone and trauma_sum < t_limit:
            self._enter_sanctuary(ctx)
            self._apply_restoration(ctx)
            if random.random() < 0.3:
                self._trigger_dream(ctx)
        return ctx

    @staticmethod
    def _enter_sanctuary(ctx: CycleContext):
        ctx.physics.zone = getattr(BonePresets.SANCTUARY, "ZONE", "SANCTUARY")
        ctx.physics.zone_color = getattr(BonePresets.SANCTUARY, "COLOR_NAME", "GRN")
        ctx.physics.flow_state = "LAMINAR"
        if random.random() < 0.1:
            color = getattr(BonePresets.SANCTUARY, "COLOR", Prisma.GRN)
            msg = ux("cycle_strings", "sanctuary_breathe")
            ctx.log(f"{color}{msg}{Prisma.RST}")

    def _apply_restoration(self, ctx: CycleContext):
        if self.eng.bio:
            rest_logs = self.eng.bio.rest(factor=1.0)
            for log in rest_logs:
                ctx.log(log)
        for key in list(self.eng.trauma_accum.keys()):
            self.eng.trauma_accum[key] = max(0.0, self.eng.trauma_accum[key] - 0.1)

    def _trigger_dream(self, ctx: CycleContext):
        if not hasattr(self.eng, "mind") or not hasattr(self.eng.mind, "dreamer"):
            return
        if hasattr(self.eng.mind.mem, "replay_dreams"):
            dream_log = self.eng.mind.mem.replay_dreams()
            if dream_log:
                ctx.log(f"{Prisma.VIOLET}{dream_log}{Prisma.RST}")
        current_trauma_load = (
            sum(self.eng.trauma_accum.values())
            if hasattr(self.eng, "trauma_accum")
            else 0.0)
        bio_packet = {
            "chem": self.eng.bio.endo.get_state(),
            "mito": {"atp": self.eng.bio.mito.state.atp_pool,
                     "ros": self.eng.bio.mito.state.ros_buildup,},
            "physics": (
                ctx.physics.to_dict()
                if hasattr(ctx.physics, "to_dict")
                else ctx.physics),
            "trauma_vector": current_trauma_load,}
        soul_snapshot = (
            self.eng.soul.to_dict()
            if hasattr(self.eng, "soul") and hasattr(self.eng.soul, "to_dict")
            else {})
        dream_packet = self.eng.mind.dreamer.enter_rem_cycle(
            soul_snapshot, bio_state=bio_packet)
        if isinstance(dream_packet, dict):
            ctx.log(dream_packet.get("log", "The mind wanders..."))
            ctx.last_dream = dream_packet
        elif isinstance(dream_packet, tuple):
            log_msg, effects = dream_packet
            ctx.log(log_msg)
            if effects:
                if "adrenaline" in effects:
                    self.eng.bio.endo.adrenaline += effects["adrenaline"]
                if "voltage" in effects:
                    ctx.physics.voltage += effects["voltage"]

class MaintenancePhase(SimulationPhase):
    """Phase 2. The Town Hall cleans up memory leaks, checks the "weather" (systemic entropy), and runs the memory ecosystem."""
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MAINTENANCE"

    def run(self, ctx: CycleContext):
        if hasattr(self.eng, "town_hall"):
            blooms = self.eng.town_hall.tend_garden(ctx.clean_words) or []
            for bloom in blooms:
                ctx.log(bloom)
            cfg = getattr(BoneConfig, "CYCLE", None)
            w_freq = getattr(cfg, "MAINTENANCE_WEATHER_FREQ", 5) if cfg else 5
            c_freq = getattr(cfg, "MAINTENANCE_CENSUS_FREQ", 20) if cfg else 20
            if self.eng.tick_count % w_freq == 0:
                weather_report = self.eng.town_hall.consult_almanac(ctx.physics)
                if weather_report:
                    ctx.log(f"{Prisma.CYN}{weather_report}{Prisma.RST}")
            is_census_due = self.eng.tick_count > 0 and self.eng.tick_count % c_freq == 0
            if is_census_due or "census" in ctx.clean_words:
                report = self.eng.town_hall.conduct_census(ctx.physics, self.eng.host_stats)
                if report:
                    msg = ux("cycle_strings", "town_hall_report")
                    ctx.log(f"{Prisma.CYN}{msg.format(report=report)}{Prisma.RST}")
            session_snapshot = {
                "trauma_vector": self.eng.trauma_accum,
                "meta": {"final_health": self.eng.health},}
            status, advice = self.eng.town_hall.diagnose_condition(session_data=session_snapshot,
                                                                   _host_health=self.eng.bio.biometrics if self.eng.bio else None,
                                                                   soul=self.eng.soul, )
            if status != "BALANCED":
                msg = ux("cycle_strings", "town_hall_vitals")
                ctx.log(
                    f"{Prisma.OCHRE}{msg.format(status=status, advice=advice)}{Prisma.RST}")
        if self.eng.mind and hasattr(self.eng.mind, "mem"):
            if hasattr(self.eng.mind.mem, "run_ecosystem"):
                eco_logs = self.eng.mind.mem.run_ecosystem(ctx.physics.to_dict(), self.eng.stamina, self.eng.tick_count)
                for log in eco_logs:
                    ctx.log(log)
        return ctx

class GatekeeperPhase(SimulationPhase):
    """
    Phase 4. Security and compliance. If the user input violates the
    foundational rules of the simulation (e.g., trying to use an object that isn't there),
    the Gatekeeper intercepts the cycle and returns a refusal packet before the LLM wastes tokens.
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "GATEKEEP"
        self.gatekeeper = TheGatekeeper(self.eng.lex)

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        if hasattr(self.eng, "soul") and hasattr(self.eng.soul, "anchor"):
            anchor = self.eng.soul.anchor
            if anchor.agency_lock:
                passed = anchor.assess_humanity(ctx.input_text)
                if not passed:
                    dash_view = SoulDashboard(self.eng).render()
                    ctx.refusal_triggered = True
                    msg = ux("cycle_strings", "gatekeep_locked")
                    log_msg = ux("cycle_strings", "gatekeep_log_agency")
                    ctx.refusal_packet = {
                        "ui": f"{dash_view}\n\n{Prisma.RED}{msg}{Prisma.RST}",
                        "logs": [log_msg] if log_msg else [],
                        "metrics": self.eng.get_metrics(),}
                    return ctx
        if self.eng.gordon:
            current_zone = getattr(ctx.physics, "zone", "UNKNOWN")
            coupling_error = self.eng.gordon.enforce_object_action_coupling(ctx.input_text, current_zone)
            if coupling_error:
                log_msg = ux("cycle_strings", "gatekeep_log_premise")
                ctx.refusal_triggered = True
                ctx.refusal_packet = {"type": "PREMISE_VIOLATION", "ui": f"\n{coupling_error}",
                                      "logs": [log_msg] if log_msg else [], "metrics": self.eng.get_metrics(), }
                return ctx
        is_allowed, refusal_packet = self.gatekeeper.check_entry(ctx)
        if not is_allowed:
            ctx.refusal_triggered = True
            ctx.refusal_packet = refusal_packet
            return ctx
        if self.eng.bureau:
            current_bio = self.eng.get_metrics()
            audit_result = self.eng.bureau.audit(ctx.physics.to_dict(), current_bio, origin="USER")
            if audit_result:
                if audit_result.get("block", False):
                    ctx.refusal_triggered = True
                    injunction_fb = ux("cycle_strings", "gatekeep_bureau_injunction")
                    log_msg = ux("cycle_strings", "gatekeep_log_bureau_block")
                    ctx.refusal_packet = {"type": "BUREAU_BLOCK", "ui": audit_result.get("ui", injunction_fb),
                                          "logs": [log_msg] if log_msg else [], "metrics": (
                            self.eng.get_metrics()
                            if hasattr(self.eng, "get_metrics")
                            else {}), }
                    return ctx
                if self.eng.bio and self.eng.bio.mito:
                    fine_msg = ux("cycle_strings", "gatekeep_bureau_fine")
                    self.eng.bio.mito.adjust_atp(
                        audit_result.get("atp_gain", 0.0), fine_msg)
                if audit_result.get("log"):
                    ctx.log(audit_result["log"])
                if audit_result.get("ui"):
                    ctx.bureau_ui = audit_result["ui"]
                    ctx.is_bureaucratic = True
        return ctx

class MetabolismPhase(SimulationPhase):
    """
    Phase 6. The core burn. Calculates the ATP cost of the incoming physics
    vectors, manages toxicity (ROS), processes healing (Kintsugi), and checks for starvation (Autophagy/Narcolepsy).
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "METABOLISM"

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        if not hasattr(self.eng, "bio") or not self.eng.bio:
            return ctx
        mode_settings = getattr(self.eng, "mode_settings", {})
        if not mode_settings.get("atp_drain_enabled", True):
            atp_level = (
                self.eng.bio.mito.state.atp_pool
                if self.eng.bio and self.eng.bio.mito
                else 100.0)
            ctx.bio_result = {"is_alive": True, "logs": [], "atp": atp_level}
            ctx.is_alive = True
            self._apply_healing(ctx)
            return ctx
        physics = ctx.physics
        if hasattr(self.eng, "host_stats"):
            self._apply_economic_stimulus(ctx, self.eng.host_stats.efficiency_index)
        gov_msg = self.eng.bio.governor.shift(
            physics, self.eng.phys.dynamics.voltage_history, self.eng.tick_count)
        if gov_msg:
            self.eng.events.log(gov_msg, "GOV")
        physics.manifold = self.eng.bio.governor.mode
        max_v = getattr(BoneConfig.PHYSICS, "VOLTAGE_MAX", 20.0)
        bio_feedback = {"INTEGRITY": getattr(physics, "truth_ratio", 1.0),
                        "STATIC": getattr(physics, "repetition", 0.0),
                        "FORCE": getattr(physics, "voltage", 0.0) / max_v, "BETA": getattr(physics, "beta_index", 0.0),
                        "PSI": getattr(physics, "psi", 0.0), "ENTROPY": getattr(physics, "entropy", 0.0),
                        "VALENCE": getattr(physics, "valence", 0.0), }
        metrics = self.eng.get_metrics()
        ctx.bio_result = self.eng.soma.digest_cycle(ctx.input_text, physics, bio_feedback, metrics["health"],
                                                    metrics["stamina"],
                                                    self.eng.bio.governor.get_stress_modifier(self.eng.tick_count),
                                                    self.eng.tick_count,
                                                    circadian_bias=self._check_circadian_rhythm(), )
        if self.eng.bio.biometrics:
            self.eng.health = self.eng.bio.biometrics.health
            self.eng.stamina = self.eng.bio.biometrics.stamina
        ctx.is_alive = ctx.bio_result["is_alive"]
        for log in ctx.bio_result["logs"]:
            if any(x in str(log) for x in ["CRITICAL", "TAX", "Poison", "NECROSIS"]):ctx.log(log)
        self._audit_hubris(ctx, physics)
        self._apply_healing(ctx)
        self._check_narcolepsy(ctx)
        self._check_autophagy(ctx)
        self._check_ros_toxicity(ctx)
        return ctx

    def _apply_economic_stimulus(self, ctx: CycleContext, efficiency: float):
        if efficiency >= 0.8:
            return
        tax_burn = min(1.5, (0.8 - efficiency) * 5.0)
        if tax_burn > 0:
            self.eng.bio.mito.state.atp_pool = max(0.0, self.eng.bio.mito.state.atp_pool - tax_burn)
            msg = ux("cycle_strings", "metabolism_tax")
            ctx.log(f"{Prisma.OCHRE}{msg.format(tax_burn=tax_burn)}{Prisma.RST}")

    def _check_narcolepsy(self, ctx: CycleContext):
        """If ATP drops too low, the system forces a nap, dreaming to defragment memory and restore energy."""
        atp = self.eng.bio.mito.state.atp_pool
        starvation = getattr(BoneConfig.BIO, "ATP_STARVATION", 5.0)
        trigger = (atp < (starvation * 0.5)) or (self.eng.tick_count > 0 and self.eng.tick_count % 100 == 0)
        if trigger and hasattr(self.eng.mind, "dreamer"):
            msg_sleep = ux("cycle_strings", "metabolism_sleep")
            ctx.log(f"{Prisma.VIOLET}{msg_sleep}{Prisma.RST}")
            soul_snap = self.eng.soul.to_dict() if hasattr(self.eng, "soul") else {}
            self.eng.mind.dreamer.enter_rem_cycle(soul_snap, bio_state={"atp": atp})
            self.eng.mind.dreamer.run_defragmentation(self.eng.mind.mem)
            reboot_val = getattr(BoneConfig, "MAX_ATP", 100.0) * 0.33
            self.eng.bio.mito.state.atp_pool = reboot_val
            ctx.bio_result["atp"] = reboot_val
            msg_wake = ux("cycle_strings", "metabolism_waking")
            ctx.log(f"{Prisma.GRN}{msg_wake.format(reboot_val=reboot_val)}{Prisma.RST}")

    def _check_circadian_rhythm(self):
        cfg = getattr(BoneConfig, "CYCLE", None)
        c_freq = getattr(cfg, "CIRCADIAN_FREQ", 10) if cfg else 10
        if self.eng.tick_count % c_freq == 0:
            bias, msg = self.eng.bio.endo.calculate_circadian_bias()
            if msg:
                self.eng.events.log(f"{Prisma.CYN}🕒 {msg}{Prisma.RST}", "BIO")
            return bias
        return None

    def _audit_hubris(self, ctx, physics):
        """If the system tries to build structure with excessive drag and voltage, it crashes (Icarus)."""
        hit, msg, evt = self.eng.phys.tension.audit_hubris(physics.to_dict())
        if hit:
            ctx.log(msg)
            cfg = getattr(BoneConfig, "CYCLE", None)
            boost = getattr(cfg, "HUBRIS_ATP_BOOST", 20.0) if cfg else 20.0
            damage = getattr(cfg, "HUBRIS_DAMAGE", 15.0) if cfg else 15.0
            if evt == "FLOW_BOOST":
                self.eng.bio.mito.state.atp_pool += boost
            elif evt == "ICARUS_CRASH":
                msg_impact = ux("cycle_strings", "metabolism_impact")
                ctx.log(f"{Prisma.RED}{msg_impact.format(damage=damage)}{Prisma.RST}")
                if self.eng.bio.biometrics:
                    self.eng.bio.biometrics.health = max(0.0, self.eng.bio.biometrics.health - damage)
                self.eng.health -= damage

    def _apply_healing(self, ctx):
        """Kintsugi checks the scars left by paradoxes, gilding them to prevent further system bleed."""
        qualia = self.eng.somatic.get_current_qualia(getattr(ctx, "last_impulse", None))
        current_stamina = self.eng.stamina
        if self.eng.bio.biometrics:
            current_stamina = self.eng.bio.biometrics.stamina
        cracked, koan = self.eng.kintsugi.check_integrity(current_stamina)
        if cracked:
            msg = ux("cycle_strings", "metabolism_kintsugi")
            ctx.log(f"{Prisma.YEL}{msg.format(koan=koan)}{Prisma.RST}")
        if self.eng.kintsugi.active_koan:
            repair = self.eng.kintsugi.attempt_repair(ctx.physics, self.eng.trauma_accum, self.eng.soul, qualia)
            if repair and repair["success"]:
                ctx.log(repair["msg"])
                cfg = getattr(BoneConfig, "CYCLE", None)
                heal_amt = getattr(cfg, "KINTSUGI_HEAL_AMT", 20.0) if cfg else 20.0
                if hasattr(self.eng.mind.mem, "record_scar"):
                    self.eng.mind.mem.record_scar(self.eng.kintsugi.active_koan or "Healed Rupture", ctx.physics)
                if self.eng.bio.biometrics:
                    self.eng.bio.biometrics.stamina = min(
                        BoneConfig.MAX_STAMINA,
                        self.eng.bio.biometrics.stamina + heal_amt,)
                self.eng.stamina = min(
                    BoneConfig.MAX_STAMINA, self.eng.stamina + heal_amt)
        if self.eng.therapy.check_progress(
                ctx.physics, current_stamina, self.eng.trauma_accum, qualia):
            msg = ux("cycle_strings", "metabolism_therapy")
            ctx.log(f"{Prisma.GRN}{msg}{Prisma.RST}")
            cfg = getattr(BoneConfig, "CYCLE", None)
            t_heal = getattr(cfg, "THERAPY_HEAL_AMT", 5.0) if cfg else 5.0
            if self.eng.bio.biometrics:
                self.eng.bio.biometrics.health = min(
                    BoneConfig.MAX_HEALTH, self.eng.bio.biometrics.health + t_heal)
            self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + t_heal)

    def _check_autophagy(self, ctx: CycleContext):
        """Survival reflex. If ATP hits zero, consume an old memory to generate energy."""
        if self.eng.bio.mito.state.atp_pool <= 0:
            if hasattr(self.eng.mind.mem, "trigger_autophagy"):
                atp_gain, msg = self.eng.mind.mem.trigger_autophagy()
                self.eng.bio.mito.state.atp_pool += atp_gain
                ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")

    def _check_ros_toxicity(self, ctx: CycleContext):
        cfg = getattr(BoneConfig, "CYCLE", None)
        ros_limit = getattr(cfg, "ROS_PANIC_THRESHOLD", 100.0) if cfg else 100.0
        if self.eng.bio.mito.state.ros_buildup >= ros_limit:
            msg = ux("cycle_strings", "metabolism_panic")
            ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")
            ctx.physics.psi = 0.0
            ctx.physics.chi = 0.0
            self.eng.bio.mito.state.ros_buildup *= 0.5
            ctx.physics.flow_state = "SAFE_MODE"


class RealityFilterPhase(SimulationPhase):
    """Phase 9. Translates raw numerical physics vectors back into thematic Trigrams (e.g., Lake, Mountain)."""
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "REALITY_FILTER"

    def run(self, ctx: CycleContext):
        reflection = self.eng.mind.mirror.get_reflection_modifiers()
        ctx.physics.narrative_drag *= reflection["drag_mult"]
        vector = ctx.physics.vector
        if vector:
            dom = max(vector, key=vector.get)
            trigrams = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TRIGRAM_MAP") or {}
            entry = trigrams.get(dom, trigrams.get("E", ["?", "UNKNOWN", "Unknown", "GRY"]))
            sym, name, _, color_attr = entry
            color = getattr(Prisma, color_attr, Prisma.GRY)
            ctx.world_state["trigram"] = {"symbol": sym, "name": name, "color": color}
            if random.random() < 0.05:
                msg = ux("cycle_strings", "filter_iching")
                ctx.log(f"{color}{msg.format(sym=sym, name=name)}{Prisma.RST}")
        return ctx

class NavigationPhase(SimulationPhase):
    """Phase 7. Maneuvers the system through conceptual space, applying gravity to the narrative drag."""
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "NAVIGATION"

    def run(self, ctx: CycleContext):
        physics = ctx.physics
        mode_settings = getattr(self.eng, "mode_settings", {})
        v_floor = mode_settings.get("voltage_floor_override")
        if v_floor is not None:
            physics.voltage = max(physics.voltage, v_floor)
            if v_floor >= 50.0:
                physics.narrative_drag = 0.0
        new_drag, grav_logs = self.eng.phys.dynamics.check_gravity(current_drift=physics.narrative_drag, psi=physics.psi)
        physics.narrative_drag = new_drag
        for log in grav_logs:
            ctx.log(log)
        if self.eng.gordon:
            phys_snapshot = physics.to_dict()
            reflex_triggered, reflex_msg = self.eng.gordon.emergency_reflex(phys_snapshot)
            if reflex_triggered:
                for key, val in phys_snapshot.items():
                    if hasattr(physics, key):
                        current_val = getattr(physics, key)
                        if current_val != val:
                            if key in ["energy", "space", "matter"]:
                                sub_obj = getattr(physics, key)
                                if isinstance(val, dict) and sub_obj:
                                    for sk, sv in val.items():
                                        if hasattr(sub_obj, sk):
                                            setattr(sub_obj, sk, sv)
                            else:
                                setattr(physics, key, val)
                if reflex_msg:
                    ctx.log(reflex_msg)
                ctx.record_flux("NAVIGATION", "REFLEX", 1.0, 0.0, "ITEM_TRIGGERED")
        phys_dict = physics.to_dict()
        if self.eng.navigator:
            current_loc, entry_msg = self.eng.navigator.locate(packet=ctx.physics,)
            if entry_msg:
                ctx.log(entry_msg)
            env_logs = self.eng.navigator.apply_environment(physics)
            for e_log in env_logs:
                ctx.log(e_log)
        if self.eng.gordon and self.eng.tinkerer:
            inv_data = self.eng.gordon.get_inventory_data()
            deltas = self.eng.tinkerer.calculate_passive_deltas(inv_data)
            for delta in deltas:
                if delta.field == "narrative_drag":
                    if delta.operator == "ADD":
                        physics.narrative_drag += delta.value
                    elif delta.operator == "MULT":
                        physics.narrative_drag *= delta.value
                    msg = ux("cycle_strings", "nav_gear_drag")
                    ctx.log(f"{Prisma.GRY}{msg.format(source=delta.source, operator=delta.operator, value=delta.value)}{Prisma.RST}")
        orbit_state, drag_pen, orbit_msg = self.eng.cosmic.analyze_orbit(self.eng.mind.mem, ctx.clean_words)
        if orbit_msg:
            ctx.log(orbit_msg)
        physics.narrative_drag += drag_pen
        cfg = getattr(BoneConfig, "CYCLE", None)
        if orbit_state == "VOID_DRIFT":
            physics.voltage = max(0.0, physics.voltage - getattr(cfg, "NAV_VOID_PENALTY", 0.5))
        elif orbit_state == "LAGRANGE_POINT":
            physics.narrative_drag = max(0.1, physics.narrative_drag - getattr(cfg, "NAV_LAGRANGE_RELIEF", 2.0))
        elif orbit_state == "WATERSHED_FLOW":
            physics.voltage += getattr(cfg, "NAV_WATERSHED_BOOST", 0.5)
        raw_zone = getattr(physics, "zone", "COURTYARD")
        stabilization_result = self.eng.stabilizer.stabilize(
            proposed_zone=raw_zone,
            physics=phys_dict,
            cosmic_state=(orbit_state, drag_pen),)
        if isinstance(stabilization_result, tuple):
            stabilized_zone = stabilization_result[0]
            if len(stabilization_result) > 1 and stabilization_result[1]:
                ctx.log(stabilization_result[1])
        else:
            stabilized_zone = stabilization_result
        physics.zone = stabilized_zone
        adjusted_drag = self.eng.stabilizer.override_cosmic_drag(
            drag_pen, stabilized_zone)
        if adjusted_drag != drag_pen:
            physics.narrative_drag -= drag_pen - adjusted_drag
        ctx.world_state["orbit"] = orbit_state
        return ctx

class MachineryPhase(SimulationPhase):
    """Phase 8. Transmutes user input into conceptual items, or discharges built-up electrical tension (The Theremin)."""
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MACHINERY"

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        phys_dict = ctx.physics.to_dict()
        if hasattr(self.eng, "critics") and (
                review := self.eng.critics.audit_performance(phys_dict, self.eng.tick_count)):
            ctx.log(review)
            good_icon = ux("cycle_strings", "machinery_critic_good_icon")
            ctx.physics.narrative_drag += -1.0 if good_icon in review else 1.0
        boost, z_msg = self.eng.zen.raking_the_sand(phys_dict, ctx.bio_result)
        if z_msg:
            ctx.log(z_msg)
        if boost > 0:
            self.eng.bio.mito.state.membrane_potential = min(
                2.0, self.eng.bio.mito.state.efficiency_mod + (boost * 0.1))
        if self.eng.gordon and self.eng.gordon.inventory:
            self._process_crafting(ctx, phys_dict)
        if t_msg := self.eng.phys.forge.transmute(phys_dict):
            ctx.log(t_msg)
        _, f_msg, new_item = self.eng.phys.forge.hammer_alloy(phys_dict)
        if f_msg:
            ctx.log(f_msg)
        if new_item and self.eng.gordon:
            ctx.log(self.eng.gordon.acquire(new_item))
        _, _, t_msg, t_crit = self.eng.phys.theremin.listen(phys_dict, self.eng.bio.governor.mode)
        if t_msg:
            ctx.log(t_msg)
        if t_crit == "AIRSTRIKE":
            self._handle_theremin_discharge(ctx)
        self.eng.phys.pulse.update(getattr(ctx.physics, "repetition", 0.0), ctx.physics.voltage)
        c_state, c_val, c_msg = self.eng.phys.crucible.audit_fire(phys_dict)
        if c_msg:
            ctx.log(c_msg)
        if c_state == "MELTDOWN":
            damage = c_val
            if self.eng.bio.biometrics:
                self.eng.bio.biometrics.health = max(0.0, self.eng.bio.biometrics.health - damage)
            self.eng.health = max(0.0, self.eng.health - damage)
        for k, v in phys_dict.items():
            if hasattr(ctx.physics, k) and not callable(getattr(ctx.physics, k)):
                try:
                    if k in ["energy", "space", "matter"]:
                        sub_obj = getattr(ctx.physics, k)
                        if isinstance(v, dict) and sub_obj:
                            for sk, sv in v.items():
                                if hasattr(sub_obj, sk):
                                    setattr(sub_obj, sk, sv)
                    else:
                        setattr(ctx.physics, k, v)
                except AttributeError:
                    pass
        return ctx

    def _process_crafting(self, ctx, phys_dict):
        is_craft, craft_msg, old_item, new_item = self.eng.phys.forge.attempt_crafting(phys_dict, self.eng.gordon.inventory)
        if is_craft:
            ctx.log(craft_msg)
            vec = ctx.physics.vector
            catalyst_cat = max(vec, key=vec.get) if vec else "void"
            self.eng.events.publish("FORGE_SUCCESS",{"ingredient": old_item, "catalyst": catalyst_cat, "result": new_item},)
            if old_item in self.eng.gordon.inventory:
                self.eng.gordon.inventory.remove(old_item)
            ctx.log(self.eng.gordon.acquire(new_item))

    def _handle_theremin_discharge(self, ctx):
        max_hp = getattr(BoneConfig, "MAX_HEALTH", 100.0)
        damage = max_hp * 0.25
        if self.eng.bio.biometrics:
            self.eng.bio.biometrics.health = max(0.0, self.eng.bio.biometrics.health - damage)
        self.eng.health = max(0.0, self.eng.health - damage)
        msg = ux("cycle_strings", "machinery_theremin")
        ctx.log(f"{Prisma.RED}{msg.format(damage=damage)}{Prisma.RST}")
        if hasattr(self.eng.events, "publish"):
            self.eng.events.publish("AIRSTRIKE", {"damage": damage, "source": "THEREMIN"})

class IntrusionPhase(SimulationPhase):
    """
    Phase 10. The Parasite and the Ghost. If the system is bored, or trauma is too high,
    it hallucinating random semantic elements to entertain itself or vent entropy.
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "INTRUSION"

    def run(self, ctx: CycleContext):
        phys_data = ctx.physics.to_dict()
        p_active, p_log = self.eng.bio.parasite.infect(phys_data, self.eng.stamina)
        if p_active:
            ctx.log(p_log)
        if self.eng.limbo.ghosts:
            if ctx.logs:
                ctx.logs[-1] = self.eng.limbo.haunt(ctx.logs[-1])
            else:
                msg = ux("cycle_strings", "intrusion_heavy")
                ctx.log(self.eng.limbo.haunt(msg))
        drag = getattr(ctx.physics, "narrative_drag", 0.0)
        kappa = getattr(ctx.physics, "kappa", 1.0)
        cfg = getattr(BoneConfig, "CYCLE", None)

        if (drag > getattr(cfg, "INTRUSION_DRAG_THRESH", 4.0) or kappa < getattr(cfg, "INTRUSION_KAPPA_THRESH", 0.3)) and ctx.clean_words:
            start_node = random.choice(ctx.clean_words)
            loop_path = self.eng.mind.tracer.inject(start_node)
            if loop_path:
                rewire_msg = self.eng.mind.tracer.psilocybin_rewire(loop_path)
                if rewire_msg:
                    msg = ux("cycle_strings", "intrusion_immune")
                    ctx.log(f"{Prisma.CYN}{msg.format(rewire_msg=rewire_msg)}{Prisma.RST}")
                    self.eng.bio.endo.dopamine += getattr(cfg, "INTRUSION_REWIRE_DOP", 0.2)
                    ctx.physics.narrative_drag = max(0.0, drag - getattr(cfg, "INTRUSION_REWIRE_RELIEF", 2.0))

        trauma_sum = (sum(self.eng.trauma_accum.values())
                      if getattr(self.eng, "trauma_accum", None)
                      else 0.0)
        is_bored = self.eng.phys.pulse.is_bored()

        if (trauma_sum > getattr(cfg, "INTRUSION_NIGHTMARE_THRESH", 10.0) or is_bored) and random.random() < getattr(cfg, "INTRUSION_DREAM_CHANCE", 0.2):
            dream_text, relief = self.eng.mind.dreamer.hallucinate(ctx.physics.vector, trauma_level=trauma_sum)
            if trauma_sum > 10.0:
                prefix = ux("cycle_strings", "intrusion_nightmare")
            else:
                prefix = ux("cycle_strings", "intrusion_daydream")
            ctx.log(f"{Prisma.VIOLET}{prefix.format(dream_text=dream_text)}{Prisma.RST}")
            if relief > 0:
                keys = list(self.eng.trauma_accum.keys())
                if keys:
                    target = random.choice(keys)
                    self.eng.trauma_accum[target] = max(0.0, self.eng.trauma_accum[target] - relief)
                    msg_relief = ux("cycle_strings", "intrusion_relief")
                    ctx.log(f"{Prisma.GRY}{msg_relief.format(relief=relief, target=target)}{Prisma.RST}")
            if is_bored:
                self.eng.phys.pulse.boredom_level = 0.0
        current_psi = getattr(ctx.physics, "psi", 0.0)
        if current_psi > 0.6 and random.random() < current_psi:
            msg_p = ux("cycle_strings", "intrusion_pareidolia")
            ctx.log(f"{Prisma.VIOLET}{msg_p.format(current_psi=current_psi)}{Prisma.RST}")
            ctx.physics.psi = min(1.0, current_psi + 0.1)
            if self.eng.bio and self.eng.bio.biometrics:
                self.eng.bio.biometrics.stamina = max(0.0, self.eng.bio.biometrics.stamina - 5.0)
                msg_drain = ux("cycle_strings", "intrusion_hallucination_drain")
                ctx.log(f"{Prisma.GRY}{msg_drain}{Prisma.RST}")
        return ctx

class SoulPhase(SimulationPhase):
    """Phase 11. Crystallizes memories and applies long-term character evolution."""
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "SOUL"

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        if not hasattr(self.eng, "soul") or not self.eng.soul:
            return ctx
        dignity = self.eng.soul.anchor.dignity_reserve
        if dignity < 30.0:
            ctx.physics.narrative_drag *= 1.5
            msg = ux("cycle_strings", "soul_dignity_low")
            ctx.log(f"{Prisma.GRY}{msg}{Prisma.RST}")
        elif dignity > 80.0:
            ctx.physics.voltage += 2.0
            ctx.physics.narrative_drag *= 0.8
            msg = ux("cycle_strings", "soul_dignity_high")
            ctx.log(f"{Prisma.MAG}{msg}{Prisma.RST}")
        lesson = self.eng.soul.crystallize_memory(ctx.physics.to_dict(), ctx.bio_result, self.eng.tick_count)
        if lesson:
            msg = ux("cycle_strings", "soul_lesson")
            ctx.log(f"{Prisma.VIOLET}{msg.format(lesson=lesson)}{Prisma.RST}")
        if not self.eng.soul.current_obsession:
            self.eng.soul.find_obsession(self.eng.lex)
        self.eng.soul.pursue_obsession(ctx.physics.to_dict())
        if hasattr(self.eng, "oroboros") and self.eng.oroboros.myths:
            for myth in self.eng.oroboros.myths:
                if myth.trigger in ctx.clean_words:
                    msg = ux("cycle_strings", "soul_myth")
                    ctx.log(f"{Prisma.YEL}{msg.format(title=myth.title)}{Prisma.RST}")
                    ctx.log(f'   "{myth.lesson}"')
                    old_volts = ctx.physics.voltage
                    ctx.physics.voltage += 5.0
                    ctx.record_flux("SOUL", "VOLTAGE", old_volts, ctx.physics.voltage, "MYTH_BUFF")
                    if self.eng.bio.biometrics:
                        self.eng.bio.biometrics.stamina = min(100.0, self.eng.bio.biometrics.stamina + 5.0)
        if self.eng.gordon and self.eng.tinkerer:
            if self.eng.gordon.inventory:
                self.eng.tinkerer.audit_tool_use(ctx.physics, self.eng.gordon.inventory)
        council_mandates = self._consult_council(self.eng.soul.traits)
        if council_mandates:
            ctx.council_mandates = getattr(ctx, "council_mandates", []) + council_mandates
            for mandate in council_mandates:
                ctx.log(mandate["log"])
                self._execute_mandate(ctx, mandate)
        council_advice, adjustments, mandates = self.eng.council.convene(
            ctx.input_text, ctx.physics, ctx.bio_result)
        if mandates:
            if not hasattr(ctx, "council_mandates"):
                ctx.council_mandates = []
            ctx.council_mandates.extend(mandates)
        for advice in council_advice:
            ctx.log(advice)
        for mandate in mandates:
            action = mandate.get("action")
            if action == "FORCE_MODE":
                target = mandate["value"]
                self.eng.bio.governor.set_override(target)
                msg = ux("cycle_strings", "council_force_mode")
                ctx.log(f"{Prisma.RED}{msg.format(target=target)}{Prisma.RST}")
            elif action == "CIRCUIT_BREAKER":
                ctx.physics.voltage = 0.0
                ctx.physics.narrative_drag = 10.0
                msg = ux("cycle_strings", "council_circuit_breaker")
                ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")
        if adjustments:
            for param, delta in adjustments.items():
                old_val = getattr(ctx.physics, param, 0.0)
                new_val = old_val + delta
                setattr(ctx.physics, param, new_val)
                ctx.record_flux("SIMULATION", param, old_val, new_val, "COUNCIL_MANDATE")
        return ctx

    @staticmethod
    def _consult_council(traits: Any) -> List[Dict]:
        t_map = (
            traits.to_dict()
            if hasattr(traits, "to_dict")
            else traits.__dict__ if hasattr(traits, "__dict__") else traits)
        get_t = lambda k: t_map.get(k, t_map.get(k.lower(), 0.0))
        council_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        mandates_text = council_data.get("SOUL_MANDATES", {})
        rules = council_data.get("SOUL_MANDATE_RULES", [
            ["CYNICISM", 0.8, "LOCKDOWN", "CYNICISM", {"narrative_drag": 5.0, "voltage": -5.0}, "OCHRE"],
            ["HOPE", 0.8, "STIMULUS", "HOPE", {"voltage": 5.0, "narrative_drag": -2.0}, "MAG"],
            ["DISCIPLINE", 0.8, "STANDARDIZE", "DISCIPLINE", {"kappa": -0.5, "beta_index": 1.0}, "CYN"]
        ])
        mandates = []
        for trait, thresh, m_type, msg_key, eff, col_attr in rules:
            if get_t(trait) > thresh:
                col = getattr(Prisma, col_attr, Prisma.GRY)
                msg = mandates_text.get(msg_key, "")
                str_msg = ux("cycle_strings", "council_log")
                mandates.append({"type": m_type, "log": f"{col}{str_msg.format(msg=msg)}{Prisma.RST}", "effect": eff})
        return mandates

    @staticmethod
    def _execute_mandate(ctx: CycleContext, mandate: Dict):
        effects = mandate.get("effect", {})
        for key, delta in effects.items():
            current = getattr(ctx.physics, key, 0.0)
            setattr(ctx.physics, key, max(0.0, current + delta))

class ArbitrationPhase(SimulationPhase):
    """
    Phase 12. Decides which Archetype will speak. If structural tension is too high,
    the Stage Manager intervenes and cuts the output short to prevent a hallucination loop.
    """
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "ARBITRATION"
        if not hasattr(self.eng, "arbiter"):
            self.eng.arbiter = ArchetypeArbiter()

    def run(self, ctx: CycleContext):
        phys_lens, _, _ = self.eng.drivers.enneagram.decide_persona(ctx.physics, soul_ref=self.eng.soul)
        soul_arch = self.eng.soul.archetype
        mandates = getattr(ctx, "council_mandates", [])
        current_trigram = ctx.world_state.get("trigram", None)
        final_lens, source, opinion = self.eng.arbiter.arbitrate(physics_lens=phys_lens, soul_archetype=soul_arch,
                                                                 council_mandates=mandates, trigram=current_trigram, )
        tension = getattr(ctx.physics, "beta_index", 0.0)
        silence = getattr(ctx.physics, "silence", 0.0)
        synergy_active = False
        synergy_name = None
        for log in ctx.logs:
            if "The lenses align" in log and "fuse into [" in log:
                synergy_active = True
                try:
                    synergy_name = log.split("fuse into [")[1].split("]")[0]
                except Exception:
                    pass
        council_data = LoreManifest.get_instance().get("COUNCIL_DATA") or {}
        arb_opinions = council_data.get("ARBITRATION_OPINIONS", {})
        cfg = getattr(BoneConfig, "CYCLE", None)
        if tension > getattr(cfg, "ARB_TENSION_THRESH", 0.85) and silence < getattr(cfg, "ARB_SILENCE_LOW", 0.5) and not synergy_active:
            final_lens = "THE STAGE MANAGER"
            opinion = arb_opinions.get("TENSION_CUT", "")
            ctx.physics.silence = getattr(cfg, "ARB_CUT_SILENCE", 0.9)
            ctx.physics.narrative_drag += getattr(cfg, "ARB_CUT_DRAG", 2.0)
            msg = ux("cycle_strings", "arbiter_stage_manager_cut")
            ctx.log(f"{Prisma.WHT}{msg}{Prisma.RST}")
            msg_silence = ux("cycle_strings", "arbiter_silence")
            ctx.log(f"{Prisma.GRY}{msg_silence}{Prisma.RST}")
        elif silence > getattr(cfg, "ARB_SILENCE_HIGH", 0.85) and not synergy_active:
            final_lens = "THE STAGE MANAGER"
            opinion = arb_opinions.get("SILENCE_HOLD", "")
            msg = ux("cycle_strings", "arbiter_stage_manager_hold")
            ctx.log(f"{Prisma.WHT}{msg}{Prisma.RST}")
        else:
            if synergy_active and synergy_name:
                final_lens = synergy_name
                msg = ux("cycle_strings", "arbiter_synergy_named")
                ctx.log(f"{Prisma.GRY}{msg.format(synergy_name=synergy_name)}{Prisma.RST}")
            elif synergy_active:
                msg = ux("cycle_strings", "arbiter_synergy_unnamed")
                ctx.log(f"{Prisma.GRY}{msg}{Prisma.RST}")
            else:
                msg = ux("cycle_strings", "arbiter_normal_lens")
                ctx.log(f"{Prisma.GRY}{msg.format(final_lens=final_lens)}{Prisma.RST}")
        ctx.active_lens = final_lens
        self.eng.events.publish("LENS_INTERACTION", {"lenses": [phys_lens, soul_arch]})
        if source != "PHYSICS_VECTOR" or final_lens == "THE STAGE MANAGER":
            msg = ux("cycle_strings", "arbiter_opinion")
            ctx.log(f"{Prisma.MAG}{msg.format(opinion=opinion)}{Prisma.RST}")
        self.eng.drivers.current_focus = final_lens
        return ctx

class CognitionPhase(SimulationPhase):
    """Phase 13. High-level cognitive processing. Resonant inputs return ATP. Memories are encoded."""
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "COGNITION"

    def run(self, ctx: CycleContext):
        if ctx.validator and ctx.input_text:
            phi = ctx.validator.calculate_resonance(ctx.input_text, ctx)
            if phi > 0.8:
                drag_relief = (phi - 0.5) * 2.0
                ctx.physics.narrative_drag = max(
                    0.0, ctx.physics.narrative_drag - drag_relief)
                if self.eng.bio and self.eng.bio.mito:
                    refund = 5.0 * phi
                    self.eng.bio.mito.adjust_atp(refund, "Harmonic Resonance")
                msg = ux("cycle_strings", "cog_resonance")
                ctx.log(f"{Prisma.CYN}{msg.format(phi=phi)}{Prisma.RST}")
        if hasattr(self.eng, "consultant"):
            self.eng.consultant.update_coordinates(
                ctx.input_text, ctx.bio_result, ctx.physics)
            if (
                    "LIMINAL" in self.eng.consultant.state.active_modules
                    and self.eng.bio
                    and self.eng.bio.mito):
                lambda_val = self.eng.consultant.state.L
                if lambda_val > 0.1:
                    lambda_tax = (lambda_val**2) * 10.0
                    self.eng.bio.mito.adjust_atp(-lambda_tax, f"Λ² Liminal Tax")
                    if lambda_tax > 2.0:
                        msg = ux("cycle_strings", "cog_liminal_tax")
                        ctx.log(f"{Prisma.VIOLET}{msg.format(lambda_tax=lambda_tax)}{Prisma.RST}")
        if hasattr(self.eng.mind.mem, "check_for_resurrection"):
            flashback_msg = self.eng.mind.mem.check_for_resurrection(ctx.clean_words, ctx.physics.voltage)
            if flashback_msg:
                ctx.log(f"{Prisma.MAG}{flashback_msg}{Prisma.RST}")
                shock_cost = 5.0
                if self.eng.bio.biometrics:
                    self.eng.bio.biometrics.stamina = max(0.0, self.eng.bio.biometrics.stamina - shock_cost)
                self.eng.stamina = max(0.0, self.eng.stamina - shock_cost)
        self.eng.mind.mem.encode(ctx.clean_words, ctx.physics.to_dict(), "GEODESIC")
        if ctx.is_alive and ctx.clean_words:
            max_h = getattr(BoneConfig, "MAX_HEALTH", 100.0)
            current_h = max(0.0, self.eng.health)
            if self.eng.bio.biometrics:
                current_h = max(0.0, self.eng.bio.biometrics.health)
            desperation = 1.0 - (current_h / max_h)
            learn_mod = getattr(BoneConfig, "PRIORITY_LEARNING_RATE", 1.0)
            bury_msg, new_wells = self.eng.mind.mem.bury(ctx.clean_words, self.eng.tick_count,
                                                         resonance=ctx.physics.voltage, desperation_level=desperation,
                                                         learning_mod=learn_mod, )
            if bury_msg:
                if "SATURATION" in bury_msg:
                    prefix = f"{Prisma.YEL}{ux('cycle_strings', 'cog_memory_warn').format(bury_msg=bury_msg)}{Prisma.RST}"
                else:
                    prefix = f"{Prisma.RED}{ux('cycle_strings', 'cog_memory_donner').format(bury_msg=bury_msg)}{Prisma.RST}"
                ctx.log(prefix)
            if new_wells:
                msg = ux("cycle_strings", "cog_gravity_well")
                ctx.log(f"{Prisma.CYN}{msg.format(new_wells=new_wells)}{Prisma.RST}")
        inventory_data = self.eng.gordon.inventory if self.eng.gordon else []
        ctx.mind_state = self.eng.noetic.think(physics_packet=ctx.physics.to_dict(), _bio=ctx.bio_result,
                                               _inventory=inventory_data,
                                               voltage_history=self.eng.phys.dynamics.voltage_history,
                                               _tick_count=self.eng.tick_count, soul_ref=self.eng.soul, )
        thought = ctx.mind_state.get("context_msg", ctx.mind_state.get("thought"))
        if thought:
            ctx.log(thought)
        return ctx

class SensationPhase(SimulationPhase):
    """Phase 3. The Synesthetic cortex translates numbers into feelings (Qualia), which cost or restore stamina."""
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "SENSATION"
        if hasattr(self.eng, "somatic"):
            self.synesthesia = self.eng.somatic
        else:
            self.synesthesia = SynestheticCortex(self.eng.bio)
            self.eng.somatic = self.synesthesia

    def run(self, ctx: CycleContext):
        phys_data = ctx.physics.to_dict()
        current_latency = 0.0
        if hasattr(self.eng, "host_stats"):
            current_latency = self.eng.host_stats.latency
        impulse = self.synesthesia.perceive(phys_data, traits=self.eng.soul.traits, latency=current_latency)
        ctx.last_impulse = impulse
        qualia = self.synesthesia.get_current_qualia(impulse)
        ctx.physics = apply_somatic_feedback(ctx.physics, qualia)
        self.synesthesia.apply_impulse(impulse)
        if impulse.stamina_impact != 0:
            max_s = getattr(BoneConfig, "MAX_STAMINA", 100.0)
            if self.eng.bio.biometrics:
                self.eng.bio.biometrics.stamina = max(0.0, min(max_s, self.eng.bio.biometrics.stamina + impulse.stamina_impact),)
            self.eng.stamina = max(0.0, min(max_s, self.eng.stamina + impulse.stamina_impact))
        return ctx

class StabilizationPhase(SimulationPhase):
    """Phase 14. Final check before output. Ensure physics arrays are clamped within bounds."""
    def __init__(self, engine_ref, stabilizer_ref):
        super().__init__(engine_ref)
        self.name = "STABILIZATION"
        self.stabilizer = stabilizer_ref

    def run(self, ctx: CycleContext):
        self.stabilizer.stabilize(ctx, self.name)
        return ctx

class PhaseExecutor:
    """A circuit breaker execution loop. Iterates through the phases, halting if the system is overloaded."""
    def execute_phases(self, simulator, ctx):
        for phase in simulator.pipeline:
            if getattr(ctx, "refusal_triggered", False):
                break
            if not simulator.check_circuit_breaker(phase.name):
                continue
            snapshot_before = ctx.physics.snapshot()
            try:
                phase.run(ctx)
            except Exception as e:
                simulator.handle_phase_crash(ctx, phase.name, e)
                self._audit_flux(ctx, phase.name, snapshot_before, ctx.physics)
                break
            self._audit_flux(ctx, phase.name, snapshot_before, ctx.physics)
        return ctx

    @staticmethod
    def _audit_flux(ctx, phase, before, after):
        def _safe_get(obj, key):
            try:
                if isinstance(obj, dict):
                    return obj.get(key, 0.0)
                return getattr(obj, key, 0.0)
            except Exception:
                return 0.0
        b_v = _safe_get(before, "voltage")
        a_v = _safe_get(after, "voltage")
        b_d = _safe_get(before, "narrative_drag")
        a_d = _safe_get(after, "narrative_drag")
        if abs(b_v - a_v) > 0.01:
            ctx.record_flux(phase, "voltage", b_v, a_v, "PHASE_DELTA")
        if abs(b_d - a_d) > 0.01:
            ctx.record_flux(phase, "drag", b_d, a_d, "PHASE_DELTA")

class CycleSimulator:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.shared_governor = self.eng.bio.governor
        self.stabilizer = CycleStabilizer(self.eng.events, self.shared_governor)
        self.executor = PhaseExecutor()
        self.pipeline: List[SimulationPhase] = [ObservationPhase(engine_ref), MaintenancePhase(engine_ref),
                                                SensationPhase(engine_ref), GatekeeperPhase(engine_ref),
                                                SanctuaryPhase(engine_ref, self.shared_governor),
                                                MetabolismPhase(engine_ref), NavigationPhase(engine_ref),
                                                MachineryPhase(engine_ref), RealityFilterPhase(engine_ref),
                                                IntrusionPhase(engine_ref), SoulPhase(engine_ref),
                                                ArbitrationPhase(engine_ref), CognitionPhase(engine_ref),
                                                StabilizationPhase(engine_ref, self.stabilizer), ]

    def run_simulation(self, ctx: CycleContext) -> CycleContext:
        ctx = self.executor.execute_phases(self, ctx)
        return ctx

    def check_circuit_breaker(self, phase_name: str) -> bool:
        health = self.eng.system_health
        if phase_name == "OBSERVE" and not health.physics_online:
            return False
        if phase_name == "METABOLISM" and not health.bio_online:
            return False
        if phase_name == "COGNITION" and not health.mind_online:
            return False
        return True

    def handle_phase_crash(self, ctx, phase_name, error):
        """Gracefully catch code crashes and translate them into diegetic 'Cathedral Collapses'."""
        msg_crash = ux("cycle_strings", "sim_crash_header")
        print(f"\n{Prisma.RED}{msg_crash.format(phase_name=phase_name)}{Prisma.RST}")
        traceback.print_exc()
        narrative = LoreManifest.get_instance().get("narrative_data") or {}
        cathedral_logs = narrative.get("CATHEDRAL_COLLAPSE_LOGS", ["System Failure."])
        eulogy = random.choice(cathedral_logs)
        msg_eulogy = ux("cycle_strings", "sim_cathedral_collapse")
        ctx.log(f"{Prisma.RED}{msg_eulogy.format(eulogy=eulogy)}{Prisma.RST}")
        component_map = {"OBSERVE": "PHYSICS", "METABOLISM": "BIO", "COGNITION": "MIND"}
        comp = component_map.get(phase_name, "SIMULATION")
        self.eng.system_health.report_failure(comp, error)
        if comp == "PHYSICS":
            ctx.physics = PanicRoom.get_safe_physics()
        elif comp == "BIO":
            ctx.bio_result = PanicRoom.get_safe_bio()
            ctx.is_alive = True
        elif comp == "MIND":
            ctx.mind_state = PanicRoom.get_safe_mind()
        msg_panic = ux("cycle_strings", "sim_panic_switch")
        ctx.log(f"{Prisma.RED}{msg_panic.format(phase_name=phase_name)}{Prisma.RST}")

class GeodesicOrchestrator:
    """The top-level wrapper for the simulator. Connects user string input to the Cycle Context object."""
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.simulator = CycleSimulator(engine_ref)
        self.reporter = CycleReporter(engine_ref)
        if hasattr(self.eng, "symbiosis"):
            self.symbiosis = self.eng.symbiosis
        else:
            self.symbiosis = SymbiosisManager(self.eng.events)
        from bone_drivers import SharedLatticeDriver
        if not hasattr(self.eng, "shared_lattice"):
            self.eng.shared_lattice = SharedLatticeDriver()

    def _execute_core_cycle(
            self, user_message: str, is_system: bool = False) -> CycleContext:
        cycle_id = str(uuid.uuid4())[:8]
        if hasattr(self.eng, "telemetry") and self.eng.telemetry:
            self.eng.telemetry.start_cycle(cycle_id)
        try:
            ctx = CycleContext(input_text=user_message, is_system_event=is_system)
            ctx.trace_id = cycle_id
            ctx.user_state = self.eng.shared_lattice.u
            ctx.shared_dyn = self.eng.shared_lattice.shared
            if (self.eng.phys
                    and hasattr(self.eng.phys, "observer")
                    and self.eng.phys.observer.last_physics_packet):
                ctx.physics = self.eng.phys.observer.last_physics_packet.snapshot()
            elif not ctx.physics:
                ctx.physics = PanicRoom.get_safe_physics()
                msg = ux("cycle_strings", "orch_physics_bypass")
                self.eng.events.log(msg, "SYS")
            ctx.validator = CongruenceValidator()
            ctx.reality_stack = getattr(self.eng, "reality_stack", None)
            ctx.user_name = self.eng.user_name
            ctx.council_mandates = []
            ctx.timestamp = time.time()
            pre_logs = [e["text"] for e in self.eng.events.flush()]
            ctx.logs.extend(pre_logs)
            self.eng.telemetry.start_cycle(cycle_id)
            ctx = self.simulator.run_simulation(ctx)
            if self.eng.phys and hasattr(self.eng.phys, "observer"):
                self.eng.phys.observer.last_physics_packet = ctx.physics.snapshot()
            if hasattr(self.eng, "telemetry") and self.eng.telemetry:
                self.eng.telemetry.finalize_cycle()
            return ctx
        except Exception as e:
            self.eng.events.log(f"CYCLE CRASH: {e}", "CRIT")
            ctx = CycleContext(input_text=user_message)
            ctx.is_alive = False
            ctx.crash_error = e
            if hasattr(self.eng, "telemetry") and self.eng.telemetry:
                self.eng.telemetry.finalize_cycle()
            return ctx

    def run_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        """The entrypoint for GUI clients. Processes metadata tags before executing the cycle."""
        upper_msg = user_message.upper()
        if "[VSL_DEEP]" in upper_msg:
            self.eng.ui_mode = "DEEP"
        elif "[VSL_CORE]" in upper_msg:
            self.eng.ui_mode = "CORE"
        elif "[VSL_LITE]" in upper_msg:
            self.eng.ui_mode = "LITE"
        elif "[VSL_HIDE]" in upper_msg:
            self.eng.ui_mode = "IDLE"
        clean_message = re.sub(r"(?i)\[VSL_[A-Z]+]", "", user_message).strip()
        if not clean_message:
            clean_message = "(Waiting)"
        ctx = self._execute_core_cycle(clean_message, is_system)
        if not ctx.is_alive:
            if hasattr(ctx, "crash_error"):
                return self._generate_crash_report(ctx.crash_error)
            return self.eng.trigger_death(ctx.physics)
        if getattr(ctx, "refusal_triggered", False) and getattr(
                ctx, "refusal_packet", None):
            return ctx.refusal_packet
        snapshot = self.reporter.render_snapshot(ctx)
        self._hydrate_snapshot_metadata(snapshot, ctx)
        latency = time.time() - ctx.timestamp
        if "ui" in snapshot:
            self.symbiosis.monitor_host(latency, snapshot["ui"], len(user_message))
        return snapshot

    def run_headless_turn(
            self, user_message: str, latency: float = 0.0) -> Dict[str, Any]:
        """Alternative execution path for automated agents or API wrappers that do not need terminal UI rendering."""
        ctx = self._execute_core_cycle(user_message)
        if not ctx.is_alive:
            if hasattr(ctx, "crash_error"):
                return self._generate_crash_report(ctx.crash_error)
            return self.eng.trigger_death(ctx.physics)
        if getattr(ctx, "refusal_triggered", False) and getattr(
                ctx, "refusal_packet", None):
            return ctx.refusal_packet
        snapshot = {"type": "HEADLESS", "logs": ctx.logs}
        self._hydrate_snapshot_metadata(snapshot, ctx)
        self.symbiosis.monitor_host(latency, "HEADLESS_MODE", len(user_message))
        return snapshot

    def _hydrate_snapshot_metadata(self, snapshot: Dict, ctx: CycleContext):
        def _safe_dict(obj):
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            if isinstance(obj, dict):
                return obj
            return {}
        snapshot.update(
            {"trace_id": getattr(ctx, "trace_id", "UNKNOWN"), "is_alive": True, "physics": _safe_dict(ctx.physics),
             "bio": _safe_dict(ctx.bio_result), "mind": _safe_dict(ctx.mind_state),
             "world": _safe_dict(ctx.world_state), "soul": _safe_dict(getattr(self.eng, "soul", {})),
             "council_mandates": getattr(ctx, "council_mandates", []), "dream": getattr(ctx, "last_dream", None), "mutated_input": ctx.input_text,})

    @staticmethod
    def _generate_crash_report(e: Exception) -> Dict[str, Any]:
        full_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        safe_phys = PanicRoom.get_safe_physics()
        safe_bio = PanicRoom.get_safe_bio()
        msg = ux("cycle_strings", "orch_reality_fracture")
        ui_report = f"{Prisma.RED}{msg.format(error=e, trace=full_trace)}{Prisma.RST}"
        return {"type": "CRASH", "ui": ui_report, "physics": safe_phys.to_dict(), "bio": safe_bio,
                "mind": PanicRoom.get_safe_mind(), "world": {"orbit": ["VOID"], "loci_description": "System Failure"},
                "logs": ["CRITICAL FAILURE", "SAFE MODE ACTIVE"], "is_alive": True, }