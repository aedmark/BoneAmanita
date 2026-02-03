""" bone_cycle.py
'The wheel turns, and ages come and pass.' - Jordan """

import re
import traceback, random, time, uuid, concurrent.futures, re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Tuple, List, Optional
from bone_bus import Prisma, BoneConfig, CycleContext, PhysicsPacket
from bone_village import TownHall
from bone_personality import TheBureau
from bone_physics import ChromaScope, TheGatekeeper, QuantumObserver, ChromaScope, GeodesicEngine
from bone_viewer import GeodesicRenderer, CachedRenderer, get_renderer
from bone_architect import PanicRoom
from bone_synesthesia import SynestheticCortex
from bone_symbiosis import SymbiosisManager
from bone_sanctuary import SanctuaryGovernor, SANCTUARY, PIDController
from bone_telemetry import TelemetryService

class CycleStabilizer:
    def __init__(self, events_ref):
        self.events = events_ref
        self.voltage_pid = PIDController(
            kp=0.15, ki=0.02, kd=0.20, setpoint=10.0, output_limits=(-4.0, 4.0))
        self.drag_pid = PIDController(
            kp=0.30, ki=0.05, kd=0.10, setpoint=1.5, output_limits=(-3.0, 3.0))
        self.last_phase: str = "INIT"

    def _get_metric(self, ctx: CycleContext, key: str, default: float = 0.0) -> float:
        p = ctx.physics
        if isinstance(p, dict):
            return float(p.get(key, default))
        return float(getattr(p, key, default))

    def _get_state(self, ctx: CycleContext, key: str, default: str = "") -> str:
        p = ctx.physics
        if isinstance(p, dict):
            return str(p.get(key, default))
        return str(getattr(p, key, default))

    def _set_metric(self, ctx: CycleContext, key: str, value: float):
        p = ctx.physics
        if isinstance(p, dict):
            p[key] = value
        else:
            setattr(p, key, value)

    def _adjust_setpoints(self, ctx: CycleContext):
        flow = self._get_state(ctx, "flow_state", "LAMINAR")
        p = ctx.physics
        manifold = "THE_CONSTRUCT"
        if isinstance(p, dict):
            manifold = p.get("manifold") or manifold
        else:
            manifold = getattr(p, "manifold", manifold)
        if manifold == "THE_CONSTRUCT":
            world = getattr(ctx, "world_state", {})
            if isinstance(world, dict):
                orbit = world.get("orbit")
                if orbit and isinstance(orbit, (list, tuple)):
                    manifold = orbit[0]
        manifold_physics = {
            "THE_FORGE":  {"voltage": 15.0, "drag": 1.5},
            "THE_MUD":    {"voltage": 10.0, "drag": 5.0},
            "THE_AERIE":  {"voltage": 10.0, "drag": 0.5},
            "DEFAULT":    {"voltage": 10.0, "drag": 1.5}}
        target_cfg = manifold_physics.get(manifold, manifold_physics["DEFAULT"])
        high_energy = {"SUPERCONDUCTIVE", "FLOW_BOOST", "HUBRIS_RISK"}
        self.voltage_pid.setpoint = 20.0 if flow in high_energy else target_cfg["voltage"]
        self.drag_pid.setpoint = target_cfg["drag"]

    def stabilize(self, ctx: CycleContext, current_phase: str):
        self._adjust_setpoints(ctx)
        curr_v = self._get_metric(ctx, "voltage")
        curr_d = self._get_metric(ctx, "narrative_drag")
        v_force = self.voltage_pid.update(curr_v, dt=None)
        d_force = self.drag_pid.update(curr_d, dt=None)
        corrections_made = False
        if abs(curr_v - self.voltage_pid.setpoint) > 6.0 and abs(v_force) > 0.05:
            new_v = max(0.0, curr_v + v_force)
            self._set_metric(ctx, "voltage", new_v)
            if abs(v_force) > 0.1:
                reason = "PID_DAMPENER" if v_force < 0 else "PID_EXCITATION"
                ctx.record_flux(current_phase, "voltage", curr_v, new_v, reason)
                if abs(v_force) > 1.5:
                    self.events.log(f"{Prisma.GRY}⚖️ STABILIZER: Voltage corrected ({v_force:+.1f}v). Target: {self.voltage_pid.setpoint}{Prisma.RST}", "SYS")
                corrections_made = True
        if abs(curr_d - self.drag_pid.setpoint) > 2.5 and abs(d_force) > 0.05:
            new_d = max(0.0, curr_d + d_force)
            self._set_metric(ctx, "narrative_drag", new_d)
            if abs(d_force) > 0.1:
                reason = "PID_LUBRICATION" if d_force < 0 else "PID_BRAKING"
                ctx.record_flux(current_phase, "narrative_drag", curr_d, new_d, reason)
                if d_force < -1.0:
                    self.events.log(f"{Prisma.GRY}🛢️ STABILIZER: Grease applied. Drag reduced ({d_force:+.1f}). Target: {self.drag_pid.setpoint}{Prisma.RST}", "SYS")
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
        ctx.physics = gaze_result["physics"]
        ctx.clean_words = gaze_result["clean_words"]
        self.eng.tick_count += 1
        return ctx

class SanctuaryPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "SANCTUARY"
        self.governor = SanctuaryGovernor(self.eng.events)

    def run(self, ctx: CycleContext):
        in_safe_zone, distance = self.governor.assess(ctx.physics)
        trauma_sum = sum(self.eng.trauma_accum.values())
        if trauma_sum > 25.0:
            return ctx
        if trauma_sum < 15.0:
            v_corr, d_corr = self.governor.calculate_correction(ctx.physics)
            if abs(v_corr) > 0.001 or abs(d_corr) > 0.001:
                old_v = ctx.physics.voltage
                ctx.physics.voltage += v_corr
                ctx.physics.narrative_drag += d_corr
                ctx.record_flux("SANCTUARY", "voltage", old_v, ctx.physics.voltage, "GENTLE_NUDGE")
        if in_safe_zone:
            self._enter_sanctuary(ctx)
            self._apply_restoration(ctx)
        return ctx

    def _enter_sanctuary(self, ctx: CycleContext):
        ctx.physics.zone = getattr(SANCTUARY, "ZONE", "SANCTUARY")
        ctx.physics.zone_color = getattr(SANCTUARY, "COLOR_NAME", "GRN")
        ctx.physics.flow_state = "LAMINAR"
        if random.random() < 0.1:
            color = getattr(SANCTUARY, 'COLOR', Prisma.GRN)
            ctx.log(f"{color}![☀️] SANCTUARY: Breathing space.{Prisma.RST}")

    def _apply_restoration(self, ctx: CycleContext):
        self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + 0.5)
        self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 1.0)
        if hasattr(self.eng, 'bio'):
            self.eng.bio.endo.serotonin = min(1.0, self.eng.bio.endo.serotonin + 0.05)
        for key in list(self.eng.trauma_accum.keys()):
            self.eng.trauma_accum[key] = max(0.0, self.eng.trauma_accum[key] - 0.1)

class MaintenancePhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MAINTENANCE"

    def run(self, ctx: CycleContext):
        if self.eng.tick_count % 10 != 0: return ctx
        try:
            rotted = self.eng.lex.atrophy(self.eng.tick_count, 100)
            if rotted:
                for w in rotted:
                    self.eng.limbo.ghosts.append(f"👻{w.upper()}_ECHO")
                example = rotted[0]
                ctx.log(f"{Prisma.GRY}NEURO-PRUNING: {len(rotted)} concepts decayed (e.g., '{example}').{Prisma.RST}")
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

    def run(self, ctx: CycleContext):
        physics = ctx.physics
        gov_msg = self.eng.bio.governor.shift(
            physics, self.eng.phys.dynamics.voltage_history, self.eng.tick_count)
        if gov_msg:
            self.eng.events.log(gov_msg, "GOV")
        bio_feedback = self._generate_feedback(physics)
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

    def _check_narcolepsy(self, ctx: CycleContext):
        current_atp = self.eng.bio.mito.state.atp_pool
        tick = self.eng.tick_count
        trigger = False
        reason = ""
        if current_atp < 5.0:
            trigger = True
            reason = "METABOLIC CRASH (Low ATP)"
        elif tick > 0 and tick % 100 == 0:
            trigger = True
            reason = "CIRCADIAN CLEANUP"
        if trigger and hasattr(self.eng.mind, "dreamer"):
            phys_data = ctx.physics.to_dict() if hasattr(ctx.physics, 'to_dict') else ctx.physics
            bio_packet = {
                "chem": ctx.bio_result.get("chemistry", {}),
                "mito": {"ros": 0.0, "atp": current_atp},
                "physics": phys_data}
            dream_log = self.eng.mind.dreamer.enter_rem_cycle(self.eng.mind.mem, bio_readout=bio_packet)
            ctx.log(f"\n{Prisma.VIOLET}[AUTO-SLEEP]: {reason} initiated.{Prisma.RST}")
            ctx.log(dream_log)
            self.eng.bio.mito.state.atp_pool = 33.0
            ctx.is_alive = True
            ctx.bio_result["respiration"] = "REM_CYCLE"
            ctx.bio_result["atp"] = 33.0
            ctx.log(f"{Prisma.GRN}   (Microsleep / Defibrillator Active. ATP stabilized at 33.0){Prisma.RST}")

    @staticmethod
    def _generate_feedback(physics):
        max_v = getattr(BoneConfig.PHYSICS, "VOLTAGE_MAX", 20.0)
        return {
            "INTEGRITY": physics.get("truth_ratio", 0.0),
            "STATIC": physics.get("repetition", 0.0),
            "FORCE": physics.get("voltage", 0.0) / max_v,
            "BETA": physics.get("beta_index", 1.0)}

    def _check_circadian_rhythm(self):
        if self.eng.tick_count % 10 == 0:
            bias, msg = self.eng.bio.endo.calculate_circadian_bias()
            if msg:
                self.eng.events.log(f"{Prisma.CYN}🕒 {msg}{Prisma.RST}", "BIO")
            return bias
        return None

    def _audit_hubris(self, ctx, physics):
        hubris_hit, hubris_msg, event_type = self.eng.phys.tension.audit_hubris(physics)
        if hubris_hit:
            ctx.log(hubris_msg)
            if event_type == "FLOW_BOOST":
                self.eng.bio.mito.state.atp_pool += 20.0
            elif event_type == "ICARUS_CRASH":
                damage = 15.0
                self.eng.health -= damage
                ctx.log(f"   {Prisma.RED}IMPACT TRAUMA: -{damage} HP.{Prisma.RST}")

    def _apply_healing(self, ctx):
        is_cracked, koan = self.eng.kintsugi.check_integrity(self.eng.stamina)
        if is_cracked:
            ctx.log(f"{Prisma.YEL}🏺 KINTSUGI ACTIVATED: Vessel cracking.{Prisma.RST}")
            ctx.log(f"   {Prisma.WHT}KOAN: {koan}{Prisma.RST}")
        if self.eng.kintsugi.active_koan:
            repair = self.eng.kintsugi.attempt_repair(ctx.physics, self.eng.trauma_accum)
            if repair and repair["success"]:
                ctx.log(repair["msg"])
                self.eng.stamina = min(BoneConfig.MAX_STAMINA, self.eng.stamina + 20.0)
                ctx.log(f"   {Prisma.GRN}STAMINA RESTORED (+20.0){Prisma.RST}")
        healed = self.eng.therapy.check_progress(ctx.physics, self.eng.stamina, self.eng.trauma_accum)
        if healed:
            joined = ", ".join(healed)
            ctx.log(f"{Prisma.GRN}❤️ THERAPY STREAK: Healing [{joined}]. Health +5.{Prisma.RST}")
            self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + 5.0)

class RealityFilterPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "REALITY_FILTER"
        self.TRIGRAMS = {
            "VEL": ("☳", "ZHEN",  Prisma.GRN), "STR": ("☶", "GEN",   Prisma.SLATE),
            "ENT": ("☵", "KAN",   Prisma.BLU), "PHI": ("☲", "LI",    Prisma.RED),
            "PSI": ("☰", "QIAN",  Prisma.WHT), "BET": ("☴", "XUN",   Prisma.CYN),
            "E":   ("☷", "KUN",   Prisma.OCHRE), "DEL": ("☱", "DUI",   Prisma.MAG)}

    def run(self, ctx: CycleContext):
        reflection = self.eng.mind.mirror.get_reflection_modifiers()
        ctx.physics.narrative_drag *= reflection["drag_mult"]
        vector = ctx.physics.vector
        if vector:
            dom = max(vector, key=vector.get)
            sym, name, color = self.TRIGRAMS.get(dom, self.TRIGRAMS["E"])
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
        if self.eng.tick_count == 3:
            ctx.log(self.eng.navigator.strike_root(physics.get("vector", {})))
        shock = self.eng.navigator.check_transplant_shock(physics.get("vector", {}))
        if shock:
            physics["narrative_drag"] += 1.0
            ctx.log(shock)
        new_drag, grav_logs = self.eng.gordon.check_gravity(physics.get("narrative_drag", 0), physics.get("psi", 0))
        for log in grav_logs:
            ctx.log(log)
        physics["narrative_drag"] = new_drag
        physics["narrative_drag"] = new_drag
        flinch_result = self.eng.gordon.check_flinch(ctx.clean_words, self.eng.tick_count)
        if flinch_result:
            if flinch_result.get("message"):
                ctx.log(flinch_result["message"])
            if flinch_result.get("physics_effects"):
                physics.update(flinch_result["physics_effects"])
        current_loc, entry_msg = self.eng.navigator.locate(physics)
        if entry_msg: ctx.log(entry_msg)
        env_logs = self.eng.navigator.apply_environment(physics)
        for e_log in env_logs: ctx.log(e_log)
        orbit_state, drag_pen, orbit_msg = self.eng.cosmic.analyze_orbit(self.eng.mind.mem, ctx.clean_words)
        raw_zone = physics.get("zone", "COURTYARD")
        stabilized_zone = self.eng.stabilizer.stabilize(raw_zone, physics, (orbit_state, drag_pen))
        adjusted_drag = self.eng.stabilizer.override_cosmic_drag(drag_pen, stabilized_zone)
        physics["zone"] = stabilized_zone
        self.eng.apply_cosmic_physics(physics, orbit_state, adjusted_drag)
        ctx.world_state["orbit"] = orbit_state
        if orbit_msg: ctx.log(orbit_msg)
        return ctx

class MachineryPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MACHINERY"

    def run(self, ctx: CycleContext):
        physics = ctx.physics
        eff_boost, zen_msg = self.eng.zen.raking_the_sand(physics, ctx.bio_result)
        if zen_msg: ctx.log(zen_msg)
        if eff_boost > 0:
            current_eff = self.eng.bio.mito.state.efficiency_mod
            self.eng.bio.mito.state.membrane_potential = min(2.0, current_eff + (eff_boost * 0.1))
        if self.eng.gordon.inventory:
            is_craft, craft_msg, old_item, new_item = self.eng.phys.forge.attempt_crafting(physics, self.eng.gordon.inventory)
            if is_craft:
                ctx.log(craft_msg)
                if hasattr(self.eng, 'akashic'):
                    catalyst_cat = max(physics.vector, key=physics.vector.get) if physics.vector else "void"
                    self.eng.akashic.track_successful_forge(old_item, catalyst_cat, new_item)
                if old_item in self.eng.gordon.inventory:
                    self.eng.gordon.inventory.remove(old_item)
                ctx.log(self.eng.gordon.acquire(new_item))
        transmute_msg = self.eng.phys.forge.transmute(physics)
        if transmute_msg: ctx.log(transmute_msg)
        _, forge_msg, new_item = self.eng.phys.forge.hammer_alloy(physics)
        if forge_msg: ctx.log(forge_msg)
        if new_item: ctx.log(self.eng.gordon.acquire(new_item))
        _, _, theremin_msg, t_crit = self.eng.phys.theremin.listen(physics, self.eng.bio.governor.mode)
        if theremin_msg: ctx.log(theremin_msg)
        if t_crit == "AIRSTRIKE":
            damage = 25.0
            self.eng.health -= damage
            ctx.log(f"{Prisma.RED}*** CRITICAL THEREMIN DISCHARGE *** -{damage} HP{Prisma.RST}")
        c_state, c_val, c_msg = self.eng.phys.crucible.audit_fire(physics)
        if c_msg: ctx.log(c_msg)
        if c_state == "MELTDOWN":
            self.eng.health -= c_val
        return ctx

class IntrusionPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "INTRUSION"

    def run(self, ctx: CycleContext):
        phys_data = ctx.physics.to_dict() if hasattr(ctx.physics, 'to_dict') else ctx.physics
        p_log = self.eng.mind.mem.dream(phys_data, self.eng.stamina)
        if p_log:
            ctx.log(p_log)
        if self.eng.limbo.ghosts:
            if ctx.logs:
                ctx.logs[-1] = self.eng.limbo.haunt(ctx.logs[-1])
            else:
                ctx.log(self.eng.limbo.haunt("The air is heavy."))
        drag = ctx.physics.get("narrative_drag", 0.0)
        kappa = ctx.physics.get("kappa", 0.5)
        if (drag > 4.0 or kappa < 0.3) and ctx.clean_words:
            start_node = random.choice(ctx.clean_words)
            loop_path = self.eng.mind.tracer.inject(start_node)
            if loop_path:
                rewire_msg = self.eng.mind.tracer.psilocybin_rewire(loop_path)
                if rewire_msg:
                    ctx.log(f"{Prisma.CYN}🦠 IMMUNE SYSTEM: {rewire_msg}{Prisma.RST}")
                    self.eng.bio.endo.dopamine += 0.2
                    ctx.physics["narrative_drag"] = max(0.0, drag - 2.0)
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
            ctx.physics["psi"] = min(1.0, ctx.physics["psi"] + 3.0)
        return ctx

class SoulPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "SOUL"

    def run(self, ctx: CycleContext):
        lesson = self.eng.soul.crystallize_memory(ctx.physics, ctx.bio_result, self.eng.tick_count)
        if lesson:
            ctx.log(f"{Prisma.VIOLET}   (The lesson '{lesson}' echoes in the chamber.){Prisma.RST}")
        if not self.eng.soul.current_obsession:
            self.eng.soul.find_obsession(self.eng.lex)
        self.eng.soul.pursue_obsession(ctx.physics)
        if self.eng.gordon.inventory:
            self.eng.tinkerer.audit_tool_use(ctx.physics, self.eng.gordon.inventory)
        council_advice, adjustments, mandates = self.eng.council.convene(ctx.input_text, ctx.physics)
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
                ctx.physics["voltage"] = 0.0
                ctx.physics["narrative_drag"] = 20.0
                ctx.log(f"{Prisma.RED}⚖️ COUNCIL ORDER: Circuit Breaker Tripped. Voltage dump.{Prisma.RST}")
        if adjustments:
            for param, delta in adjustments.items():
                if hasattr(ctx.physics, "__getitem__") or isinstance(ctx.physics, dict):
                    if param in ctx.physics:
                        old_val = ctx.physics[param]
                        ctx.physics[param] += delta
                        ctx.record_flux("SIMULATION", param, old_val, ctx.physics[param], "COUNCIL_MANDATE")
                elif hasattr(ctx.physics, param):
                    old_val = getattr(ctx.physics, param)
                    setattr(ctx.physics, param, old_val + delta)
                    ctx.record_flux("SIMULATION", param, old_val, old_val + delta, "COUNCIL_MANDATE")
        return ctx

class CognitionPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "COGNITION"

    def run(self, ctx: CycleContext):
        self.eng.mind.mem.encode(ctx.clean_words, ctx.physics, "GEODESIC")
        if ctx.is_alive and ctx.clean_words:
            bury_msg, new_wells = self.eng.mind.mem.bury(
                ctx.clean_words,
                self.eng.tick_count,
                resonance=ctx.physics.get("voltage", 5.0))
            if bury_msg:
                prefix = f"{Prisma.YEL}⚠️ MEMORY:{Prisma.RST}" if "SATURATION" in bury_msg else f"{Prisma.RED}🍖 DONNER PROTOCOL:{Prisma.RST}"
                ctx.log(f"{prefix} {bury_msg}")
            if new_wells:
                ctx.log(f"{Prisma.CYN}🌌 GRAVITY WELL FORMED: {new_wells}{Prisma.RST}")
        ctx.mind_state = self.eng.noetic.think(
            ctx.physics,
            ctx.bio_result,
            self.eng.gordon.inventory,
            self.eng.phys.dynamics.voltage_history,
            self.eng.tick_count)
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
        new_ctx.physics = ctx.physics.snapshot()
        new_ctx.clean_words = list(ctx.clean_words)
        new_ctx.logs = list(ctx.logs)
        new_ctx.flux_log = list(ctx.flux_log)
        new_ctx.bio_result = ctx.bio_result.copy()
        new_ctx.world_state = ctx.world_state.copy()
        new_ctx.mind_state = ctx.mind_state.copy()
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

class SensationPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "SENSATION"
        self.synesthesia = SynestheticCortex(self.eng.bio)

    def run(self, ctx: CycleContext):
        phys_data = ctx.physics.to_dict() if hasattr(ctx.physics, 'to_dict') else ctx.physics
        impulse = self.synesthesia.perceive(phys_data)
        ctx.last_impulse = impulse
        self.synesthesia.apply_impulse(impulse)
        if impulse.stamina_impact != 0:
            self.eng.stamina = max(0.0, self.eng.stamina + impulse.stamina_impact)
        return ctx


class ParallelPhaseExecutor:
    def execute_phases(self, simulator, ctx):
        pipeline_order = [
            "OBSERVE",
            "MAINTENANCE",
            "SENSATION",
            "GATEKEEP",
            "SANCTUARY",
            "METABOLISM",
            "NAVIGATION",
            "MACHINERY",
            "REALITY_FILTER",
            "INTRUSION",
            "SOUL",
            "COGNITION"]
        reconciler = StateReconciler()
        for phase_name in pipeline_order:
            if not simulator.check_circuit_breaker(phase_name):
                continue
            if phase_name not in ["OBSERVE", "MAINTENANCE", "SENSATION", "GATEKEEP", "SANCTUARY"]:
                if ctx.refusal_triggered or ctx.is_bureaucratic:
                    break
            phase = next((p for p in simulator.pipeline if p.name == phase_name), None)
            if not phase:
                continue
            sandbox = reconciler.fork(ctx)
            try:
                self._run_single_safe(simulator, phase, sandbox)
                reconciler.reconcile(ctx, sandbox)
            except Exception as e:
                simulator.handle_phase_crash(ctx, phase.name, e)

    def _run_single_safe(self, simulator, phase, sandbox):
        tracer = TelemetryService.get_tracer()
        tracer.start_phase(phase.name, sandbox)
        try:
            phase.run(sandbox)
            # Meadows: Stabilize immediately after disturbance
            simulator.stabilizer.stabilize(sandbox, phase.name)
        finally:
            tracer.end_phase(phase.name, sandbox, sandbox)

class CycleSimulator:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.stabilizer = CycleStabilizer(self.eng.events)
        self.executor = ParallelPhaseExecutor()
        self.pipeline: List[SimulationPhase] = [
            ObservationPhase(engine_ref),
            MaintenancePhase(engine_ref),
            SensationPhase(engine_ref),
            GatekeeperPhase(engine_ref),
            MetabolismPhase(engine_ref),
            RealityFilterPhase(engine_ref),
            NavigationPhase(engine_ref),
            SanctuaryPhase(engine_ref),
            MachineryPhase(engine_ref),
            IntrusionPhase(engine_ref),
            SoulPhase(engine_ref),
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

class StrunkWhite:
    def sanitize(self, text: str) -> Tuple[str, Optional[str]]:
        clean = re.sub(r'\n\s*\n', '\n\n', text)
        banned = ["large language model", "AI assistant", "cannot feel"]
        violation = None
        for b in banned:
            if b in clean.lower():
                clean = clean.replace(b, "[REDACTED]")
                violation = f"Style Violation: Used forbidden phrase '{b}'."
        return clean, violation

class CycleReporter:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.vsl_chroma = ChromaScope()
        self.strunk = StrunkWhite()
        self.renderer = get_renderer(
            self.eng,
            self.vsl_chroma,
            self.strunk,
            None, # No Valve
            mode="STANDARD")
        self.current_mode = "STANDARD"

    def switch_renderer(self, mode: str):
        if self.current_mode == mode:
            return
        self.renderer = get_renderer(
            self.eng,
            self.vsl_chroma,
            self.strunk,
            getattr(self, 'valve', None),
            mode=mode)
        self.current_mode = mode
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
        flux_lines = []
        for entry in ctx.flux_log[-5:]:
            m = entry['metric'].upper()
            d = entry['delta']
            r = entry['reason']
            icon = "⚡" if m == "VOLTAGE" else "⚓"
            color = Prisma.GRN if d > 0 else Prisma.RED
            arrow = "▲" if d > 0 else "▼"
            line = (
                f"{Prisma.GRY}[FLUX]{Prisma.RST} "
                f"{icon} {m[:3]} {entry['initial']:.1f} "
                f"{color}{arrow} {abs(d):.1f}{Prisma.RST} -> "
                f"{Prisma.WHT}{entry['final']:.1f}{Prisma.RST} "
                f"({r})")
            flux_lines.append(line)
        if flux_lines:
            ctx.logs.insert(0, "")
            for line in reversed(flux_lines):
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

    def run_turn(self, user_message: str, latency: float = 0.0) -> Dict[str, Any]:
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
            snapshot = self.reporter.render_snapshot(ctx)
            snapshot["council_mandates"] = getattr(ctx, "council_mandates", [])
            snapshot["trace_id"] = cycle_id
            snapshot["enzyme"] = ctx.bio_result.get("enzyme", "NONE")
            snapshot["chemistry"] = ctx.bio_result.get("chemistry", {})
            snapshot["physics"] = ctx.physics.to_dict() if hasattr(ctx.physics, 'to_dict') else ctx.physics
            if "metrics" in snapshot:
                snapshot["metrics"] = self.eng.get_metrics(
                    ctx.bio_result.get("atp", self.eng.bio.mito.state.atp_pool)
                )
            if "ui" in snapshot:
                self.symbiosis.monitor_host(latency, snapshot["ui"], len(user_message))
            return snapshot
        finally:
            tracer.finalize_cycle()