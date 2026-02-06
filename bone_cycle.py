""" bone_cycle.py = - 'The wheel turns, and ages come and pass.' - Jordan """

import traceback, random, time, uuid, re, copy
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Tuple, List, Optional, cast
from bone_core import Prisma, BoneConfig, CycleContext, PhysicsPacket, TelemetryService, DecisionCrystal, BlackBoxReader, BonePresets, ArchetypeArbiter, PhysicsSandbox
from bone_metaphysics import CongruenceValidator
from bone_village import TownHall, PIDController
from bone_protocols import TheBureau
from bone_physics import TheGatekeeper, QuantumObserver, ChromaScope, GeodesicEngine, apply_somatic_feedback, TRIGRAM_MAP
from bone_gui import GeodesicRenderer, CachedRenderer, get_renderer
from bone_architect import PanicRoom
from bone_soul import SynestheticCortex
from bone_symbiosis import SymbiosisManager
from bone_village import SanctuaryGovernor
from bone_lexicon import SomaticInterface

def _get_p(p, key, default=None):
    if isinstance(p, dict):
        return p.get(key, default)
    return getattr(p, key, default)

def _set_p(p, key, value):
    if isinstance(p, dict):
        p[key] = value
    else:
        setattr(p, key, value)

class CycleStabilizer:
    MANIFOLD_CONFIGS = {
        "THE_FORGE": {"voltage": 15.0, "drag": 1.5},
        "THE_MUD": {"voltage": 10.0, "drag": 5.0},
        "THE_AERIE": {"voltage": 10.0, "drag": 0.5},
        "LABORATORY": {"voltage": 12.0, "drag": 1.0},
        "COURTYARD": {"voltage": 8.0, "drag": 2.0},
        "DEFAULT": {"voltage": 10.0, "drag": 1.5}}

    HIGH_ENERGY_STATES = {"SUPERCONDUCTIVE", "FLOW_BOOST", "HUBRIS_RISK"}

    def __init__(self, events_ref, governor_ref):
        self.events = events_ref
        self.governor = governor_ref
        self.last_phase: str = "INIT"
        self.last_tick_time = time.time()

    def _adjust_setpoints(self, ctx: CycleContext, p: Any):
        flow = str(getattr(p, "flow_state", "LAMINAR"))
        current_manifold = getattr(p, "manifold", "THE_CONSTRUCT")
        if current_manifold in ["THE_CONSTRUCT", "DEFAULT", "None"]:
            world = getattr(ctx, "world_state", {})
            if isinstance(world, dict):
                orbit = world.get("orbit")
                if orbit and isinstance(orbit, (list, tuple)) and orbit[0]:
                    current_manifold = orbit[0]
        target_cfg = self.MANIFOLD_CONFIGS.get(current_manifold, self.MANIFOLD_CONFIGS["DEFAULT"])
        base_max_v = getattr(BoneConfig.PHYSICS, "VOLTAGE_MAX", 20.0)
        target_v = base_max_v if flow in self.HIGH_ENERGY_STATES else target_cfg["voltage"]
        target_d = target_cfg["drag"]
        self.governor.recalibrate(target_v, target_d)

    def stabilize(self, ctx: CycleContext, current_phase: str):
        now = time.time()
        dt = max(0.001, min(1.0, now - self.last_tick_time))
        self.last_tick_time = now
        p = ctx.physics
        self._adjust_setpoints(ctx, p)
        curr_v = p.voltage
        curr_d = p.narrative_drag
        v_force, d_force = self.governor.regulate(p, dt=dt)
        CRITICAL_VOLT = getattr(BoneConfig.PHYSICS, "VOLTAGE_CRITICAL", 15.0)
        CRITICAL_DRAG = getattr(BoneConfig.PHYSICS, "DRAG_CRITICAL", 8.0)
        if p.voltage > CRITICAL_VOLT and p.narrative_drag > (CRITICAL_DRAG * 0.5):
            d_force = min(d_force, 0.0)
        corrections_made = False
        MAX_V = getattr(BoneConfig.PHYSICS, "VOLTAGE_MAX", 20.0)
        MIN_V = getattr(BoneConfig.PHYSICS, "VOLTAGE_FLOOR", 0.0)
        if abs(v_force) > 0.01:
            raw_new_v = curr_v + v_force
            new_v = max(MIN_V, min(MAX_V, raw_new_v))
            p.voltage = new_v
            if abs(v_force) > 0.5:
                reason = "PID_DAMPENER" if v_force < 0 else "PID_EXCITATION"
                ctx.record_flux(current_phase, "voltage", curr_v, new_v, reason)
                if abs(v_force) > 1.0:
                    self.events.log(
                        f"{Prisma.GRY}⚖️ STABILIZER: Voltage active correction ({v_force:+.2f}v).{Prisma.RST}", "SYS")
            corrections_made = True
        if abs(d_force) > 0.01:
            new_d = max(0.0, curr_d + d_force)
            p.narrative_drag = new_d
            if abs(d_force) > 0.5:
                reason = "PID_LUBRICATION" if d_force < 0 else "PID_BRAKING"
                ctx.record_flux(current_phase, "narrative_drag", curr_d, new_d, reason)
            corrections_made = True
        self.last_phase = current_phase
        return corrections_made

class SimulationPhase:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.name = "GENERIC_PHASE"

    def run(self, ctx: CycleContext) -> CycleContext:
        raise NotImplementedError


class ObservationPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "OBSERVE"

    def run(self, ctx: CycleContext):
        gaze_result = self.eng.phys.observer.gaze(ctx.input_text, self.eng.mind.mem.graph)
        input_phys = gaze_result["physics"]
        meta_keys = ["clean_words", "counts", "vector", "valence", "entropy", "beta_index", "raw_text", "antigens",
                     "psi", "kappa", "zone", "flow_state"]
        for k in meta_keys:
            if hasattr(input_phys, k) and hasattr(ctx.physics, k):
                setattr(ctx.physics, k, getattr(input_phys, k))
        curr_v = ctx.physics.voltage
        input_v = getattr(input_phys, "voltage", 0.0)
        if input_v > curr_v:
            ctx.physics.voltage = (curr_v * 0.8) + (input_v * 0.2)
        else:
            ctx.physics.voltage = (curr_v * 0.95) + (input_v * 0.05)
        curr_d = ctx.physics.narrative_drag
        input_d = getattr(input_phys, "narrative_drag", 0.0)
        ctx.physics.narrative_drag = (curr_d * 0.9) + (input_d * 0.1)
        ctx.clean_words = gaze_result["clean_words"]
        self.eng.phys.dynamics.commit(ctx.physics.voltage)
        self.eng.tick_count += 1
        return ctx

class IntentionPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "INTENTION"

    def run(self, ctx: CycleContext):
        physics = ctx.physics
        clean = ctx.clean_words
        if any(w in clean for w in ["analyze", "scan", "think", "query"]):
            physics.narrative_drag = max(0.0, physics.narrative_drag - 1.0)
            ctx.log(f"{Prisma.CYN}🧠 INTENTION: Focus engaged. Drag reduced.{Prisma.RST}")
        if any(w in clean for w in ["error", "fail", "critical", "bug"]):
            physics.voltage = min(20.0, physics.voltage + 2.0)
            ctx.log(f"{Prisma.MAG}🧠 INTENTION: Bracing for impact. Voltage spiked.{Prisma.RST}")
        current_atp = self.eng.bio.mito.state.atp_pool
        if current_atp < 15.0:
            physics.narrative_drag += 2.0
            ctx.log(f"{Prisma.OCHRE}🧠 INTENTION: Low Energy. Conservation mode active.{Prisma.RST}")
        return ctx


class SanctuaryPhase(SimulationPhase):
    def __init__(self, engine_ref, governor_ref):
        super().__init__(engine_ref)
        self.name = "SANCTUARY"
        self.governor = governor_ref

    def run(self, ctx: CycleContext):
        in_safe_zone, distance = self.governor.assess(ctx.physics)
        trauma_sum = sum(self.eng.trauma_accum.values())
        if in_safe_zone and trauma_sum < 25.0:
            self._enter_sanctuary(ctx)
            self._apply_restoration(ctx)
            if random.random() < 0.3:
                self._trigger_dream(ctx)
        return ctx

    def _enter_sanctuary(self, ctx: CycleContext):
        _set_p(ctx.physics, "zone", getattr(BonePresets.SANCTUARY, "ZONE", "SANCTUARY"))
        _set_p(ctx.physics, "zone_color", getattr(BonePresets.SANCTUARY, "COLOR_NAME", "GRN"))
        _set_p(ctx.physics, "flow_state", "LAMINAR")
        if random.random() < 0.1:
            color = getattr(BonePresets.SANCTUARY, 'COLOR', Prisma.GRN)
            ctx.log(f"{color}![☀️] SANCTUARY: Breathing space.{Prisma.RST}")

    def _apply_restoration(self, ctx: CycleContext):
        self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + 0.5)
        self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 1.0)
        if hasattr(self.eng, 'bio'):
            self.eng.bio.endo.serotonin = min(1.0, self.eng.bio.endo.serotonin + 0.05)
        for key in list(self.eng.trauma_accum.keys()):
            self.eng.trauma_accum[key] = max(0.0, self.eng.trauma_accum[key] - 0.1)

    def _trigger_dream(self, ctx: CycleContext):
        if not hasattr(self.eng.mind, "dreamer"):
            return
        bio_packet = {
            "chem": self.eng.bio.endo.get_state(),
            "mito": {"atp": self.eng.bio.mito.state.atp_pool, "ros": self.eng.bio.mito.state.ros_buildup},
            "physics": ctx.physics.to_dict() if hasattr(ctx.physics, 'to_dict') else ctx.physics}
        dream_packet = self.eng.mind.dreamer.enter_rem_cycle(
            self.eng.mind.mem,
            bio_readout=bio_packet)
        if isinstance(dream_packet, dict):
            ctx.log(dream_packet.get("log", "The mind wanders..."))
            ctx.last_dream = dream_packet

class MaintenancePhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MAINTENANCE"
        if not hasattr(self.eng, 'soil_fertility'):
            self.eng.soil_fertility = 0.0

    def run(self, ctx: CycleContext):
        if hasattr(self.eng, 'town_hall'):
            blooms = self.eng.town_hall.tend_garden(ctx.clean_words)
            for bloom in blooms:
                ctx.log(bloom)
        if self.eng.tick_count % 10 != 0: return ctx
        try:
            solvents = {'the', 'and', 'is', 'a', 'of', 'to', 'in', 'it', 'i', 'you'}
            rotted = self.eng.lex.atrophy(self.eng.tick_count, 100, protected=solvents)
            if rotted:
                biomass = len(rotted) * 0.5
                self.eng.soil_fertility = min(50.0, self.eng.soil_fertility + biomass)
                for w in rotted:
                    self.eng.limbo.ghosts.append(f"👻{w.upper()}_ECHO")
                ctx.log(
                    f"{Prisma.GRY}♻️ COMPOST: {len(rotted)} concepts decayed -> +{biomass:.1f} Fertility.{Prisma.RST}")
            if self.eng.soil_fertility > 10.0:
                drag_reduction = self.eng.soil_fertility * 0.05
                ctx.physics.narrative_drag = max(0.0, ctx.physics.narrative_drag - drag_reduction)
                ctx.log(f"{Prisma.GRN}🌱 FERTILE GROUND: The compost lowers drag by {drag_reduction:.2f}.{Prisma.RST}")
            self.eng.mind.mem.enforce_limits(self.eng.tick_count)
        except Exception as e:
            if BoneConfig.VERBOSE_LOGGING: print(f"Maintenance Error: {e}")
        return ctx

class GatekeeperPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "GATEKEEP"
        self.gatekeeper = TheGatekeeper(self.eng)
        self.bureau = TheBureau()

    def run(self, ctx: CycleContext):
        is_allowed, refusal_packet = self.gatekeeper.check_entry(ctx)
        if not is_allowed:
            ctx.refusal_triggered = True
            ctx.refusal_packet = refusal_packet
            return ctx
        audit_result = self.bureau.audit(ctx.physics, getattr(ctx, "bio_result", {}))
        if audit_result:
            self.eng.bio.mito.state.atp_pool += audit_result.get("atp_gain", 0.0)
            if audit_result.get("log"): ctx.log(audit_result["log"])
        return ctx

class MetabolismPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "METABOLISM"
        self.bailout_pid = PIDController(
            kp=5.0, ki=1.0, kd=2.0,
            setpoint=1.0,
            output_limits=(0.0, 10.0))

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        physics = ctx.physics
        if hasattr(self.eng, "host_stats"):
            efficiency = self.eng.host_stats.efficiency_index
            self._apply_economic_stimulus(ctx, efficiency)
        gov_msg = self.eng.bio.governor.shift(
            physics,
            self.eng.phys.dynamics.voltage_history, self.eng.tick_count)
        if gov_msg:
            self.eng.events.log(gov_msg, "GOV")
        physics.manifold = self.eng.bio.governor.mode
        max_v = getattr(BoneConfig.PHYSICS, "VOLTAGE_MAX", 20.0)
        bio_feedback = {
            "INTEGRITY": physics.truth_ratio,
            "STATIC": physics.repetition,
            "FORCE": physics.voltage / max_v,
            "BETA": physics.beta_index}
        stress_mod = self.eng.bio.governor.get_stress_modifier(self.eng.tick_count)
        circadian_bias = self._check_circadian_rhythm()
        ctx.bio_result = self.eng.soma.digest_cycle(
            ctx.input_text, physics, bio_feedback,
            self.eng.health, self.eng.stamina, stress_mod, self.eng.tick_count,
            circadian_bias=circadian_bias)
        ctx.is_alive = ctx.bio_result["is_alive"]
        for bio_item in ctx.bio_result["logs"]:
            if any(x in str(bio_item) for x in ["CRITICAL", "TAX", "Poison", "NECROSIS"]):
                ctx.log(bio_item)
        self._audit_hubris(ctx, physics)
        self._apply_healing(ctx)
        self._check_narcolepsy(ctx)
        return ctx

    def _apply_economic_stimulus(self, ctx: CycleContext, efficiency: float):
        raw_tax = 0.0
        if efficiency < 0.8:
            raw_tax = min(1.5, (1.0 - efficiency) * 2.0)
        stimulus = self.bailout_pid.update(efficiency)
        adjusted_tax = max(0.0, raw_tax - stimulus)
        if adjusted_tax > 0.0:
            self.eng.bio.mito.state.atp_pool -= adjusted_tax
            subsidy = raw_tax - adjusted_tax
            msg = f"{Prisma.OCHRE}⚡ METABOLIC TAX: System strain burns {adjusted_tax:.1f} ATP.{Prisma.RST}"
            if subsidy > 0.1:
                msg += f" {Prisma.GRY}(System subsidized {subsidy:.1f} cost){Prisma.RST}"
            ctx.log(msg)
        elif raw_tax > 0.0 and adjusted_tax == 0.0:
            ctx.log(f"{Prisma.GRN}🛡️ METABOLIC SHIELD: Emergency Stimulus negated {raw_tax:.1f} ATP tax.{Prisma.RST}")

    def _check_narcolepsy(self, ctx: CycleContext):
        current_atp = self.eng.bio.mito.state.atp_pool
        tick = self.eng.tick_count
        trigger = False
        reason = ""
        starvation_line = getattr(BoneConfig.BIO, "ATP_STARVATION", 5.0)
        collapse_threshold = max(1.0, starvation_line * 0.5)
        if current_atp < collapse_threshold:
            trigger = True
            reason = f"METABOLIC CRASH (ATP < {collapse_threshold:.1f})"
        elif tick > 0 and tick % 100 == 0:
            trigger = True
            reason = "CIRCADIAN CLEANUP"
        if trigger and hasattr(self.eng.mind, "dreamer"):
            phys_data = ctx.physics.to_dict() if hasattr(ctx.physics, 'to_dict') else ctx.physics
            bio_packet = {
                "chem": ctx.bio_result.get("chemistry", {}),
                "mito": {"ros": 0.0, "atp": current_atp},
                "physics": phys_data}
            ctx.log(f"\n{Prisma.VIOLET}[AUTO-SLEEP]: {reason} initiated.{Prisma.RST}")
            dream_packet = self.eng.mind.dreamer.enter_rem_cycle(self.eng.mind.mem, bio_readout=bio_packet)
            if isinstance(dream_packet, dict):
                ctx.log(dream_packet["log"])
                ctx.last_dream = dream_packet
            else:
                ctx.log(dream_packet)
            defrag_log = self.eng.mind.dreamer.run_defragmentation(self.eng.mind.mem)
            ctx.log(f"{Prisma.GRY}   {defrag_log}{Prisma.RST}")
            max_atp = getattr(BoneConfig, "MAX_ATP", 100.0)
            reboot_val = max_atp * 0.33
            self.eng.bio.mito.state.atp_pool = reboot_val
            ctx.is_alive = True
            ctx.bio_result["respiration"] = "REM_CYCLE"
            ctx.bio_result["atp"] = reboot_val
            ctx.log(
                f"{Prisma.GRN}   (Microsleep / Defibrillator Active. ATP stabilized at {reboot_val:.1f}){Prisma.RST}")

    @staticmethod
    def _generate_feedback(physics):
        max_v = getattr(BoneConfig.PHYSICS, "VOLTAGE_MAX", 20.0)
        return {
            "INTEGRITY": _get_p(physics, "truth_ratio", 0.0),
            "STATIC": _get_p(physics, "repetition", 0.0),
            "FORCE": _get_p(physics, "voltage", 0.0) / max_v,
            "BETA": _get_p(physics, "beta_index", 1.0)}

    def _check_circadian_rhythm(self):
        if self.eng.tick_count % 10 == 0:
            bias, msg = self.eng.bio.endo.calculate_circadian_bias()
            if msg:
                self.eng.events.log(f"{Prisma.CYN}🕒 {msg}{Prisma.RST}", "BIO")
            return bias
        return None

    def _audit_hubris(self, ctx, physics):
        hubris_hit, hubris_msg, event_type = self.eng.phys.tension.audit_hubris(physics.to_dict())
        if hubris_hit:
            ctx.log(hubris_msg)
            if event_type == "FLOW_BOOST":
                self.eng.bio.mito.state.atp_pool += 20.0
            elif event_type == "ICARUS_CRASH":
                damage = 15.0
                self.eng.health -= damage
                ctx.log(f"   {Prisma.RED}IMPACT TRAUMA: -{damage} HP.{Prisma.RST}")

    def _apply_healing(self, ctx):
        impulse = getattr(ctx, "last_impulse", None)
        qualia = self.eng.somatic.get_current_qualia(impulse)
        is_cracked, koan = self.eng.kintsugi.check_integrity(self.eng.stamina)
        if is_cracked:
            ctx.log(f"{Prisma.YEL}🏺 KINTSUGI ACTIVATED: Vessel cracking.{Prisma.RST}")
            ctx.log(f"   {Prisma.WHT}KOAN: {koan}{Prisma.RST}")
        if self.eng.kintsugi.active_koan:
            repair = self.eng.kintsugi.attempt_repair(
                ctx.physics,
                self.eng.trauma_accum,
                soul_ref=self.eng.soul,
                qualia=qualia)
            if repair and repair["success"]:
                ctx.log(repair["msg"])
                self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 20.0)
        healed = self.eng.therapy.check_progress(
            ctx.physics,
            self.eng.stamina,
            self.eng.trauma_accum,
            qualia=qualia)
        if healed:
            joined = ", ".join(healed)
            ctx.log(f"{Prisma.GRN}❤️ THERAPY STREAK: Healing [{joined}]. Health +5.{Prisma.RST}")
            self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + 5.0)

class RealityFilterPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "REALITY_FILTER"
        self.TRIGRAMS = TRIGRAM_MAP

    def run(self, ctx: CycleContext):
        reflection = self.eng.mind.mirror.get_reflection_modifiers()
        ctx.physics.narrative_drag *= reflection["drag_mult"]
        vector = ctx.physics.vector
        if vector:
            dom = max(vector, key=vector.get)
            entry = self.TRIGRAMS.get(dom, self.TRIGRAMS["E"])
            sym, name, _, color = entry
            ctx.world_state["trigram"] = {"symbol": sym, "name": name, "color": color}
            if random.random() < 0.05:
                ctx.log(f"{color}I CHING: {sym} {name} is in the ascendant.{Prisma.RST}")
        return ctx


class NavigationPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "NAVIGATION"

    def run(self, ctx: CycleContext):
        physics = ctx.physics
        new_drag, grav_logs = self.eng.gordon.check_gravity(
            current_drift=physics.narrative_drag,
            psi=physics.psi)
        physics.narrative_drag = new_drag
        for log in grav_logs:
            ctx.log(log)
        flinch_result = self.eng.gordon.check_flinch(
            clean_words=ctx.clean_words,
            current_turn=self.eng.tick_count)
        if flinch_result:
            if flinch_result.get("message"):
                ctx.log(flinch_result["message"])
            effects = flinch_result.get("physics_effects", {})
            for k, v in effects.items():
                if hasattr(physics, k):
                    setattr(physics, k, v)
        phys_dict = physics.to_dict()
        current_loc, entry_msg = self.eng.navigator.locate(phys_dict, self.eng.host_stats)
        if entry_msg:
            ctx.log(entry_msg)
        env_logs = self.eng.navigator.apply_environment(physics)
        for e_log in env_logs:
            ctx.log(e_log)
        orbit_state, drag_pen, orbit_msg = self.eng.cosmic.analyze_orbit(
            self.eng.mind.mem,
            ctx.clean_words)
        if orbit_msg:
            ctx.log(orbit_msg)
        raw_zone = getattr(physics, "zone", "COURTYARD")
        stabilized_zone = self.eng.stabilizer.stabilize(
            proposed_zone=raw_zone,
            physics=phys_dict,
            cosmic_state=(orbit_state, drag_pen))
        physics.zone = stabilized_zone
        adjusted_drag = self.eng.stabilizer.override_cosmic_drag(drag_pen, stabilized_zone)
        self.eng.apply_cosmic_physics(phys_dict, orbit_state, adjusted_drag)
        ctx.world_state["orbit"] = orbit_state
        return ctx


class MachineryPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MACHINERY"

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        physics = ctx.physics
        phys_dict = physics.to_dict()
        eff_boost, zen_msg = self.eng.zen.raking_the_sand(phys_dict, ctx.bio_result)
        if zen_msg:
            ctx.log(zen_msg)
        if eff_boost > 0:
            current_eff = self.eng.bio.mito.state.efficiency_mod
            self.eng.bio.mito.state.membrane_potential = min(2.0, current_eff + (eff_boost * 0.1))
        if self.eng.gordon.inventory:
            self._process_crafting(ctx, phys_dict)
        transmute_msg = self.eng.phys.forge.transmute(phys_dict)
        if transmute_msg:
            ctx.log(transmute_msg)
        _, forge_msg, new_item = self.eng.phys.forge.hammer_alloy(phys_dict)
        if forge_msg:
            ctx.log(forge_msg)
        if new_item:
            ctx.log(self.eng.gordon.acquire(new_item))
        _, _, theremin_msg, t_crit = self.eng.phys.theremin.listen(
            phys_dict,
            self.eng.bio.governor.mode)
        if theremin_msg:
            ctx.log(theremin_msg)
        if t_crit == "AIRSTRIKE":
            self._handle_airstrike(ctx)
        c_state, c_val, c_msg = self.eng.phys.crucible.audit_fire(phys_dict)
        if c_msg:
            ctx.log(c_msg)
        if c_state == "MELTDOWN":
            self.eng.health -= c_val
        return ctx

    def _process_crafting(self, ctx, phys_dict):
        is_craft, craft_msg, old_item, new_item = self.eng.phys.forge.attempt_crafting(
            phys_dict,
            self.eng.gordon.inventory)
        if is_craft:
            ctx.log(craft_msg)
            vec = ctx.physics.vector
            catalyst_cat = max(vec, key=vec.get) if vec else "void"
            self.eng.events.publish("FORGE_SUCCESS", {
                "ingredient": old_item,
                "catalyst": catalyst_cat,
                "result": new_item})
            if old_item in self.eng.gordon.inventory:
                self.eng.gordon.inventory.remove(old_item)
            ctx.log(self.eng.gordon.acquire(new_item))

    def _handle_airstrike(self, ctx):
        max_hp = getattr(BoneConfig, "MAX_HEALTH", 100.0)
        damage = max_hp * 0.25
        self.eng.health -= damage
        ctx.log(f"{Prisma.RED}*** CRITICAL THEREMIN DISCHARGE *** -{damage:.1f} HP{Prisma.RST}")
        if hasattr(self.eng.events, "publish"):
            self.eng.events.publish("AIRSTRIKE", {"damage": damage, "source": "THEREMIN"})

class IntrusionPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "INTRUSION"

    def run(self, ctx: CycleContext):
        phys_data = ctx.physics.to_dict()
        p_active, p_log = self.eng.bio.parasite.infect(phys_data, self.eng.stamina)
        if p_active: ctx.log(p_log)
        if self.eng.limbo.ghosts:
            if ctx.logs:
                ctx.logs[-1] = self.eng.limbo.haunt(ctx.logs[-1])
            else:
                ctx.log(self.eng.limbo.haunt("The air is heavy."))
        drag = ctx.physics.narrative_drag
        kappa = ctx.physics.kappa
        if (drag > 4.0 or kappa < 0.3) and ctx.clean_words:
            start_node = random.choice(ctx.clean_words)
            loop_path = self.eng.mind.tracer.inject(start_node)
            if loop_path:
                rewire_msg = self.eng.mind.tracer.psilocybin_rewire(loop_path)
                if rewire_msg:
                    ctx.log(f"{Prisma.CYN}🦠 IMMUNE SYSTEM: {rewire_msg}{Prisma.RST}")
                    self.eng.bio.endo.dopamine += 0.2
                    ctx.physics.narrative_drag = max(0.0, drag - 2.0)
        trauma_sum = sum(self.eng.trauma_accum.values())
        is_bored = self.eng.phys.pulse.is_bored()
        if (trauma_sum > 10.0 or is_bored) and random.random() < 0.2:
            dream_text, relief = self.eng.mind.dreamer.hallucinate(
                ctx.physics.vector,
                trauma_level=trauma_sum)
            prefix = "💭 NIGHTMARE" if trauma_sum > 10.0 else "💭 DAYDREAM"
            ctx.log(f"{Prisma.VIOLET}{prefix}: {dream_text}{Prisma.RST}")
            if relief > 0:
                keys = list(self.eng.trauma_accum.keys())
                if keys:
                    target = random.choice(keys)
                    self.eng.trauma_accum[target] = max(0.0, self.eng.trauma_accum[target] - relief)
                    ctx.log(f"   {Prisma.GRY}(Psychic pressure released: -{relief:.1f} {target}){Prisma.RST}")
            if is_bored:
                self.eng.phys.pulse.boredom_level = 0.0
        is_p, p_msg = self.eng.check_pareidolia(ctx.clean_words)
        if is_p:
            ctx.log(p_msg)
            ctx.physics.psi = min(1.0, ctx.physics.psi + 3.0)
        return ctx

class SoulPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "SOUL"

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        lesson = self.eng.soul.crystallize_memory(ctx.physics.to_dict(), ctx.bio_result, self.eng.tick_count)
        if lesson:
            ctx.log(f"{Prisma.VIOLET}   (The lesson '{lesson}' echoes in the chamber.){Prisma.RST}")
        if not self.eng.soul.current_obsession:
            self.eng.soul.find_obsession(self.eng.lex)
        self.eng.soul.pursue_obsession(ctx.physics.to_dict())
        if self.eng.gordon.inventory:
            self.eng.tinkerer.audit_tool_use(ctx.physics.to_dict(), self.eng.gordon.inventory)
        council_mandates = self._consult_council(self.eng.soul.traits)
        if council_mandates:
            ctx.council_mandates = getattr(ctx, "council_mandates", []) + council_mandates
            for mandate in council_mandates:
                ctx.log(mandate['log'])
                self._execute_mandate(ctx, mandate)
        council_advice, adjustments, mandates = self.eng.council.convene(
            ctx.input_text,
            ctx.physics.to_dict(),
            ctx.bio_result)
        if mandates:
            if not hasattr(ctx, 'council_mandates'): ctx.council_mandates = []
            ctx.council_mandates.extend(mandates)
        for advice in council_advice:
            ctx.log(advice)
        for mandate in mandates:
            action = mandate.get("action")
            if action == "FORCE_MODE":
                target = mandate["value"]
                self.eng.bio.governor.set_override(target)
                ctx.log(f"{Prisma.RED}⚖️ COUNCIL ORDER: Emergency Shift to {target}.{Prisma.RST}")
            elif action == "CIRCUIT_BREAKER":
                ctx.physics.voltage = 0.0
                ctx.physics.narrative_drag = 20.0
                ctx.log(f"{Prisma.RED}⚖️ COUNCIL ORDER: Circuit Breaker Tripped. Voltage dump.{Prisma.RST}")
        if adjustments:
            for param, delta in adjustments.items():
                old_val = getattr(ctx.physics, param, 0.0)
                new_val = old_val + delta
                setattr(ctx.physics, param, new_val)
                ctx.record_flux("SIMULATION", param, old_val, new_val, "COUNCIL_MANDATE")
        return ctx

    def _consult_council(self, traits: Dict[str, float]) -> List[Dict]:
        mandates = []
        if traits.get("CYNICISM", 0) > 0.8:
            mandates.append({
                "type": "LOCKDOWN",
                "log": f"{Prisma.OCHRE}⚖️ COUNCIL: The Cynic holds the gavel. 'Stop doing things.' (Drag Increased).{Prisma.RST}",
                "effect": {"narrative_drag": 5.0, "voltage": -5.0}})
        elif traits.get("HOPE", 0) > 0.8:
            mandates.append({
                "type": "STIMULUS",
                "log": f"{Prisma.MAG}⚖️ COUNCIL: The Optimist filibustered. 'We can build it!' (Voltage Spiked).{Prisma.RST}",
                "effect": {"voltage": 5.0, "narrative_drag": -2.0}})
        elif traits.get("DISCIPLINE", 0) > 0.8:
            mandates.append({
                "type": "STANDARDIZE",
                "log": f"{Prisma.CYN}⚖️ COUNCIL: The Engineer demands efficiency. (Entropy Reduced).{Prisma.RST}",
                "effect": {"kappa": -0.5, "beta_index": 1.0}})
        return mandates

    def _execute_mandate(self, ctx: CycleContext, mandate: Dict):
        effects = mandate.get("effect", {})
        for key, delta in effects.items():
            current = getattr(ctx.physics, key, 0.0)
            setattr(ctx.physics, key, max(0.0, current + delta))

class ArbitrationPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "ARBITRATION"
        if not hasattr(self.eng, 'arbiter'):
            self.eng.arbiter = ArchetypeArbiter()

    def run(self, ctx: CycleContext):
        phys_lens, _, _ = self.eng.drivers.enneagram.decide_persona(
            ctx.physics,
            soul_ref=self.eng.soul)
        soul_arch = self.eng.soul.archetype
        mandates = getattr(ctx, "council_mandates", [])
        current_trigram = ctx.world_state.get("trigram", None)
        final_lens, source, opinion = self.eng.arbiter.arbitrate(
            physics_lens=phys_lens,
            soul_archetype=soul_arch,
            council_mandates=mandates,
            trigram=current_trigram)
        ctx.active_lens = final_lens
        self.eng.events.publish("LENS_INTERACTION", {
            "lenses": [phys_lens, soul_arch]})
        if source != "PHYSICS_VECTOR":
            ctx.log(f"{Prisma.MAG}⚖️ {opinion}{Prisma.RST}")
        self.eng.drivers.current_focus = final_lens
        return ctx

class CognitionPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "COGNITION"

    def run(self, ctx: CycleContext):
        if hasattr(self.eng, 'consultant'):
            self.eng.consultant.update_coordinates(ctx.input_text, ctx.bio_result, ctx.physics)
        self.eng.mind.mem.encode(ctx.clean_words, ctx.physics.to_dict(), "GEODESIC")
        if ctx.is_alive and ctx.clean_words:
            max_h = getattr(BoneConfig, "MAX_HEALTH", 100.0)
            current_h = max(0.0, self.eng.health)
            desperation = 1.0 - (current_h / max_h)
            bury_msg, new_wells = self.eng.mind.mem.bury(
                ctx.clean_words,
                self.eng.tick_count,
                resonance=ctx.physics.voltage,
                desperation_level=desperation)
            if bury_msg:
                prefix = f"{Prisma.YEL}⚠️ MEMORY:{Prisma.RST}" if "SATURATION" in bury_msg else f"{Prisma.RED}🍖 DONNER PROTOCOL:{Prisma.RST}"
                ctx.log(f"{prefix} {bury_msg}")
            if new_wells:
                ctx.log(f"{Prisma.CYN}🌌 GRAVITY WELL FORMED: {new_wells}{Prisma.RST}")
        ctx.mind_state = self.eng.noetic.think(
            ctx.physics.to_dict(),
            ctx.bio_result,
            self.eng.gordon.inventory,
            self.eng.phys.dynamics.voltage_history,
            self.eng.tick_count,
            soul_ref=self.eng.soul)
        thought = ctx.mind_state.get("context_msg", ctx.mind_state.get("thought"))
        if thought:
            ctx.log(thought)
        return ctx

class StateReconciler:
    @staticmethod
    def fork(ctx: CycleContext) -> CycleContext:
        new_ctx = CycleContext(input_text=ctx.input_text)
        new_ctx.user_profile = ctx.user_profile
        new_ctx.is_alive = ctx.is_alive
        new_ctx.refusal_triggered = ctx.refusal_triggered
        new_ctx.is_bureaucratic = ctx.is_bureaucratic
        new_ctx.timestamp = ctx.timestamp
        new_ctx.bureau_ui = ctx.bureau_ui
        if hasattr(ctx.physics, "snapshot"):
            new_ctx.physics = ctx.physics.snapshot()
        elif hasattr(ctx.physics, "copy"):
            new_ctx.physics = ctx.physics.copy()
        else:
            new_ctx.physics = copy.deepcopy(ctx.physics)
        new_ctx.clean_words = list(ctx.clean_words)
        new_ctx.logs = list(ctx.logs)
        new_ctx.flux_log = list(ctx.flux_log)
        new_ctx.bio_result = copy.deepcopy(ctx.bio_result)
        new_ctx.world_state = ctx.world_state.copy()
        new_ctx.mind_state = ctx.mind_state.copy()
        if hasattr(ctx, 'reality_stack'):
            new_ctx.reality_stack = copy.deepcopy(ctx.reality_stack)
        if hasattr(ctx, 'active_lens'):
            new_ctx.active_lens = ctx.active_lens
        return new_ctx

    @staticmethod
    def reconcile(canonical: CycleContext, sandbox: CycleContext, engine_ref=None):
        canonical.physics = sandbox.physics
        new_logs = sandbox.logs[len(canonical.logs):]
        if new_logs:
            canonical.logs.extend(new_logs)
        new_flux = sandbox.flux_log[len(canonical.flux_log):]
        if new_flux:
            canonical.flux_log.extend(new_flux)
        canonical.is_alive = sandbox.is_alive
        canonical.refusal_triggered = sandbox.refusal_triggered
        canonical.is_bureaucratic = sandbox.is_bureaucratic
        canonical.bureau_ui = sandbox.bureau_ui
        canonical.bio_result = sandbox.bio_result
        canonical.world_state = sandbox.world_state
        canonical.mind_state = sandbox.mind_state
        canonical.clean_words = sandbox.clean_words
        if hasattr(sandbox, 'active_lens'):
            canonical.active_lens = sandbox.active_lens

class SensationPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "SENSATION"
        if hasattr(self.eng, 'somatic'):
            self.synesthesia = self.eng.somatic
        else:
            self.synesthesia = SynestheticCortex(self.eng.bio)
            self.eng.somatic = self.synesthesia

    def run(self, ctx: CycleContext):
        phys_data = ctx.physics.to_dict() if hasattr(ctx.physics, 'to_dict') else ctx.physics
        current_latency = 0.0
        if hasattr(self.eng, "host_stats"):
            current_latency = self.eng.host_stats.latency
        impulse = self.synesthesia.perceive(
            phys_data,
            traits=self.eng.soul.traits,
            latency=current_latency)
        ctx.last_impulse = impulse
        qualia = self.synesthesia.get_current_qualia(impulse)
        ctx.physics = apply_somatic_feedback(ctx.physics, qualia)
        self.synesthesia.apply_impulse(impulse)
        if impulse.stamina_impact != 0:
            self.eng.stamina = max(0.0, self.eng.stamina + impulse.stamina_impact)
        return ctx

class PhaseExecutor:
    def execute_phases(self, simulator, ctx):
        reconciler = StateReconciler()
        SYSTEM_SKIP_LIST = ["OBSERVE", "METABOLISM", "INTRUSION", "MAINTENANCE", "SENSATION"]
        for phase in simulator.pipeline:
            phase_name = phase.name
            if ctx.is_system_event and phase_name in SYSTEM_SKIP_LIST:
                continue
            if not simulator.check_circuit_breaker(phase_name):
                continue
            is_critical = phase_name in ["OBSERVE", "MAINTENANCE", "SENSATION", "GATEKEEP", "SANCTUARY"]
            if not is_critical:
                if ctx.refusal_triggered or ctx.is_bureaucratic:
                    break
            sandbox = reconciler.fork(ctx)
            try:
                self._run_single_safe(simulator, phase, sandbox)
                reconciler.reconcile(ctx, sandbox)
            except Exception as e:
                simulator.handle_phase_crash(ctx, phase_name, e)

    def _run_single_safe(self, simulator, phase, sandbox):
        tracer = TelemetryService.get_tracer()
        tracer.start_phase(phase.name, sandbox)
        current_packet = cast(PhysicsPacket, cast(object, sandbox.physics))
        wrapped_physics = PhysicsSandbox.create(current_packet)
        sandbox.physics = wrapped_physics
        try:
            phase.run(sandbox)
            simulator.stabilizer.stabilize(sandbox, phase.name)
        finally:
            sandbox.physics = wrapped_physics.packet
            for mod in wrapped_physics.get_modification_log():
                val_old = mod['old']
                val_new = mod['new']
                if isinstance(val_old, (int, float)) and isinstance(val_new, (int, float)):
                    sandbox.record_flux(
                        phase=phase.name,
                        metric=mod['key'],
                        initial=float(val_old),
                        final=float(val_new),
                        reason=mod['reason'])
            tracer.end_phase(phase.name, sandbox, sandbox)

class CycleSimulator:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.shared_governor = SanctuaryGovernor(self.eng.events)
        self.stabilizer = CycleStabilizer(self.eng.events, self.shared_governor)
        self.executor = PhaseExecutor()
        self.pipeline: List[SimulationPhase] = [
            ObservationPhase(engine_ref),
            IntentionPhase(engine_ref),
            MaintenancePhase(engine_ref),
            SensationPhase(engine_ref),
            GatekeeperPhase(engine_ref),
            SanctuaryPhase(engine_ref, self.shared_governor),
            MetabolismPhase(engine_ref),
            NavigationPhase(engine_ref),
            MachineryPhase(engine_ref),
            RealityFilterPhase(engine_ref),
            IntrusionPhase(engine_ref),
            SoulPhase(engine_ref),
            ArbitrationPhase(engine_ref),
            CognitionPhase(engine_ref)]

    def run_simulation(self, ctx: CycleContext) -> CycleContext:
        reconciler = StateReconciler()
        self.executor.execute_phases(self, ctx)
        return ctx

    def check_circuit_breaker(self, phase_name: str) -> bool:
        health = self.eng.system_health
        if phase_name == "OBSERVE" and not health.physics_online: return False
        if phase_name == "METABOLISM" and not health.bio_online: return False
        if phase_name == "COGNITION" and not health.mind_online: return False
        return True

    def handle_phase_crash(self, ctx, phase_name, error):
        print(f"\n{Prisma.RED}!!! CRITICAL {phase_name} CRASH !!!{Prisma.RST}")
        traceback.print_exc()
        component_map = {
            "OBSERVE": "PHYSICS",
            "METABOLISM": "BIO",
            "COGNITION": "MIND"}
        comp = component_map.get(phase_name, "SIMULATION")
        self.eng.system_health.report_failure(comp, error)
        if comp == "PHYSICS":
            ctx.physics = PanicRoom.get_safe_physics()
        elif comp == "BIO":
            ctx.bio_result = PanicRoom.get_safe_bio()
            ctx.is_alive = True
        elif comp == "MIND":
            ctx.mind_state = PanicRoom.get_safe_mind()
        ctx.log(f"{Prisma.RED}⚠ {phase_name} FAILURE: Switching to Panic Protocol.{Prisma.RST}")

class CycleReporter:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.vsl_chroma = ChromaScope()
        self.renderer = None
        self.current_mode = None
        self.switch_renderer("STANDARD")

    def switch_renderer(self, mode: str):
        if self.current_mode == mode and self.renderer is not None:
            return
        self.renderer = get_renderer(
            self.eng,
            self.vsl_chroma,
            None,
            getattr(self, 'valve', None),
            mode=mode)
        self.current_mode = mode
        if hasattr(self.eng, 'tick_count') and self.eng.tick_count > 0:
            self.eng.events.log(f"VIEWPORT SHIFT: Switched to {mode} mode.", "SYS")

    def render_snapshot(self, ctx: CycleContext) -> Dict[str, Any]:
        try:
            if ctx.refusal_triggered and ctx.refusal_packet:
                return ctx.refusal_packet
            if ctx.is_bureaucratic:
                return self._package_bureaucracy(ctx)
            self._inject_diagnostics(ctx)
            self._inject_flux_readout(ctx)
            self._inject_somatic_pulse(ctx)
            captured_events = self.eng.events.flush()
            return self.renderer.render_frame(ctx, self.eng.tick_count, captured_events)
        except Exception as e:
            return {
                "type": "CRITICAL_RENDER_FAIL",
                "ui": f"{Prisma.RED}REALITY FRACTURE (Renderer Crash): {e}{Prisma.RST}\nRaw Output: {ctx.logs}",
                "logs": ctx.logs,
                "metrics": self.eng.get_metrics()}

    def _inject_diagnostics(self, ctx: CycleContext):
        feedback = self.eng.system_health.flush_feedback()
        if feedback["hints"]:
            for hint in feedback["hints"]:
                ctx.logs.append(f"{Prisma.CYN}💡 HINT: {hint}{Prisma.RST}")
        if feedback["warnings"]:
            for warn in feedback["warnings"]:
                ctx.logs.append(f"{Prisma.OCHRE}⚠️ WARNING: {warn}{Prisma.RST}")
        if hasattr(ctx, 'validator') and ctx.validator:
            phi = ctx.validator.last_phi
            color = Prisma.GRN if phi > 0.8 else Prisma.RED
            ctx.logs.append(f"{color}Φ RESONANCE: {phi:.3f}{Prisma.RST}")

    def _inject_somatic_pulse(self, ctx: CycleContext):
        impulse = getattr(ctx, "last_impulse", None)
        qualia = self.eng.somatic.get_current_qualia(impulse)
        somatic_log = (
            f"{qualia.color_code}♦ SENSATION: {qualia.somatic_sensation} "
            f"[{qualia.tone}]{Prisma.RST}")
        hint_log = f"{Prisma.GRY}   ({qualia.internal_monologue_hint}){Prisma.RST}"
        ctx.logs.insert(0, hint_log)
        ctx.logs.insert(0, somatic_log)

    @staticmethod
    def _inject_flux_readout(ctx: CycleContext):
        if not ctx.flux_log:
            return
        significant_flux = []
        for entry in ctx.flux_log[-5:]:
            r = entry['reason']
            d = abs(entry['delta'])
            if r in ["AUTO_TRACE", "PID_BRAKING", "PID_EXCITATION", "PID_DAMPENER", "PID_LUBRICATION"]:
                if d < 5.0: continue
            m = entry['metric'].upper()
            icon = "⚡" if m == "VOLTAGE" else "⚓"
            color = Prisma.GRN if entry['delta'] > 0 else Prisma.RED
            arrow = "▲" if entry['delta'] > 0 else "▼"
            line = (
                f"{Prisma.GRY}[FLUX]{Prisma.RST} "
                f"{icon} {m[:3]} {entry['initial']:.1f} "
                f"{color}{arrow} {d:.1f}{Prisma.RST} -> "
                f"{Prisma.WHT}{entry['final']:.1f}{Prisma.RST} "
                f"({r})")
            significant_flux.append(line)
        if significant_flux:
            ctx.logs.insert(0, "")
            for line in reversed(significant_flux):
                ctx.logs.insert(0, line)
            ctx.logs.insert(0, f"{Prisma.CYN}--- LIVE STATE MIRROR ---{Prisma.RST}")

    def _package_bureaucracy(self, ctx: CycleContext):
        return {
            "type": "BUREAUCRACY",
            "ui": ctx.bureau_ui,
            "logs": GeodesicRenderer.compose_logs(ctx.logs, self.eng.events.flush(), self.eng.tick_count),
            "metrics": self.eng.get_metrics(ctx.bio_result.get("atp", 0.0))}

class GeodesicOrchestrator:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.simulator = CycleSimulator(engine_ref)
        self.reporter = CycleReporter(engine_ref)
        self.symbiosis = SymbiosisManager(self.eng.events)

    def run_turn(self, user_message: str, latency: float = 0.0, is_system: bool = False) -> Dict[str, Any]:
        tracer = TelemetryService.get_tracer()
        cycle_id = str(uuid.uuid4())[:8]
        tracer.start_cycle(cycle_id)
        try:
            ctx = CycleContext(input_text=user_message, is_system_event=is_system)
            if self.eng.phys and hasattr(self.eng.phys, 'observer') and self.eng.phys.observer.last_physics_packet:
                ctx.physics = self.eng.phys.observer.last_physics_packet.snapshot()
            ctx.validator = CongruenceValidator()
            if hasattr(self.eng, 'reality_stack'):
                ctx.reality_stack = self.eng.reality_stack
            ctx.user_name = self.eng.user_name
            ctx.council_mandates = []
            self.eng.events.flush()
            ctx = self.simulator.run_simulation(ctx)
            if hasattr(ctx, 'validator') and ctx.validator:
                last_log = ctx.logs[-1] if ctx.logs else ""
                ctx.validator.calculate_resonance(last_log, ctx)
                if hasattr(ctx.physics, "phi"):
                    ctx.physics.phi = ctx.validator.last_phi
                else:
                    setattr(ctx.physics, "phi", ctx.validator.last_phi)
            if not ctx.is_alive:
                return self.eng.trigger_death(ctx.physics)
            snapshot = self.reporter.render_snapshot(ctx)
            snapshot["council_mandates"] = getattr(ctx, "council_mandates", [])
            snapshot["trace_id"] = cycle_id
            if hasattr(ctx, "last_dream") and ctx.last_dream:
                snapshot["dream"] = ctx.last_dream
            snapshot["enzyme"] = ctx.bio_result.get("enzyme", "NONE")
            snapshot["chemistry"] = ctx.bio_result.get("chemistry", {})
            snapshot["physics"] = ctx.physics.to_dict() if hasattr(ctx.physics, 'to_dict') else ctx.physics
            if hasattr(self.eng, "soul"):
                snapshot["soul"] = self.eng.soul.to_dict()
            if "ui" in snapshot:
                self.symbiosis.monitor_host(latency, snapshot["ui"], len(user_message))
            return snapshot
        finally:
            tracer.finalize_cycle()

    def run_headless_turn(self, user_message: str, latency: float = 0.0) -> Dict[str, Any]:
        tracer = TelemetryService.get_tracer()
        cycle_id = str(uuid.uuid4())[:8]
        tracer.start_cycle(cycle_id)
        try:
            ctx = CycleContext(input_text=user_message)
            ctx.user_name = self.eng.user_name
            ctx.council_mandates = []
            self.eng.events.flush()
            ctx = self.simulator.run_simulation(ctx)
            if not ctx.is_alive:
                return self.eng.trigger_death(ctx.physics)
            state_snapshot = {
                "trace_id": cycle_id,
                "is_alive": ctx.is_alive,
                "physics": ctx.physics.to_dict() if hasattr(ctx.physics, 'to_dict') else ctx.physics,
                "bio": ctx.bio_result,
                "mind": ctx.mind_state,
                "world": ctx.world_state,
                "logs": ctx.logs,
                "soul": self.eng.soul.to_dict() if hasattr(self.eng, "soul") else {},
                "council_mandates": getattr(ctx, "council_mandates", [])}
            self.symbiosis.monitor_host(latency, "HEADLESS_MODE", len(user_message))
            return state_snapshot
        finally:
            tracer.finalize_cycle()