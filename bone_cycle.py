import re
import traceback, random, time, uuid, os, json
from typing import Dict, Any, List
from bone_core import ArchetypeArbiter, LoreManifest
from bone_types import Prisma, CycleContext
from bone_physics import (
    TheGatekeeper,
    apply_somatic_feedback,
    TRIGRAM_MAP,
    CycleStabilizer,
)
from bone_gui import SoulDashboard, CycleReporter
from bone_machine import PanicRoom
from bone_body import SynestheticCortex
from bone_symbiosis import SymbiosisManager
from bone_config import BoneConfig, BonePresets
from bone_drivers import CongruenceValidator

UX_STRINGS_PATH = os.path.join(os.path.dirname(__file__), "lore", "ux_strings.json")
try:
    with open(UX_STRINGS_PATH, "r", encoding="utf-8") as f:
        _UX_DATA = json.load(f)
except Exception:
    _UX_DATA = {}


def _get_ux(section: str, key: str, default: Any) -> Any:
    return _UX_DATA.get(section, {}).get(key, default)


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
        if self.eng.gordon and "GORDON" not in self.eng.suppressed_agents:
            loot_candidate = self.eng.gordon.parse_loot(ctx.input_text, "")
            if loot_candidate:
                acquire_msg = self.eng.gordon.acquire(loot_candidate)
                ctx.log(acquire_msg)
        gaze_result = self.eng.phys.observer.gaze(
            ctx.input_text, self.eng.mind.mem.graph
        )
        input_phys = gaze_result["physics"]
        transfer_keys = {
            "clean_words",
            "counts",
            "vector",
            "valence",
            "entropy",
            "beta",
            "S",
            "D",
            "C",
            "PHI_RES",
            "DELTA",
            "LQ",
            "ROS",
            "G",
            "raw_text",
            "antigens",
            "psi",
            "kappa",
            "zone",
            "flow_state",
            "repetition",
        }
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
        if current_atp < 15.0:
            msg = _get_ux(
                "cycle_strings",
                "observe_low_energy",
                "🧠 INTENTION: Low Energy. Metabolism slowing down.",
            )
            ctx.log(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
        if hasattr(self.eng, "symbiosis"):
            diag = self.eng.symbiosis.current_health.diagnosis
            if diag != "STABLE":
                msg = _get_ux(
                    "cycle_strings", "observe_symbiont", "⚕️ SYMBIONT DIAGNOSIS: {diag}"
                )
                ctx.log(f"{Prisma.OCHRE}{msg.format(diag=diag)}{Prisma.RST}")
        self.eng.phys.dynamics.commit(ctx.physics.voltage)
        self.eng.tick_count += 1
        return ctx


class SanctuaryPhase(SimulationPhase):
    def __init__(self, engine_ref, governor_ref):
        super().__init__(engine_ref)
        self.name = "SANCTUARY"
        self.governor = governor_ref

    def run(self, ctx: CycleContext):
        in_safe_zone, distance = self.governor.assess(ctx.physics)
        trauma_sum = (
            sum(self.eng.trauma_accum.values())
            if getattr(self.eng, "trauma_accum", None)
            else 0.0
        )
        if in_safe_zone and trauma_sum < 25.0:
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
            msg = _get_ux(
                "cycle_strings",
                "sanctuary_breathe",
                "![☀️] SANCTUARY: Breathing space.",
            )
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
            else 0.0
        )
        bio_packet = {
            "chem": self.eng.bio.endo.get_state(),
            "mito": {
                "atp": self.eng.bio.mito.state.atp_pool,
                "ros": self.eng.bio.mito.state.ros_buildup,
            },
            "physics": (
                ctx.physics.to_dict()
                if hasattr(ctx.physics, "to_dict")
                else ctx.physics
            ),
            "trauma_vector": current_trauma_load,
        }
        soul_snapshot = (
            self.eng.soul.to_dict()
            if hasattr(self.eng, "soul") and hasattr(self.eng.soul, "to_dict")
            else {}
        )
        dream_packet = self.eng.mind.dreamer.enter_rem_cycle(
            soul_snapshot, bio_state=bio_packet
        )
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
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MAINTENANCE"

    def run(self, ctx: CycleContext):
        if hasattr(self.eng, "town_hall"):
            blooms = self.eng.town_hall.tend_garden(ctx.clean_words) or []
            for bloom in blooms:
                ctx.log(bloom)
            if self.eng.tick_count % 5 == 0:
                weather_report = self.eng.town_hall.consult_almanac(ctx.physics)
                if weather_report:
                    ctx.log(f"{Prisma.CYN}{weather_report}{Prisma.RST}")
            is_census_due = self.eng.tick_count > 0 and self.eng.tick_count % 20 == 0
            if is_census_due or "census" in ctx.clean_words:
                report = self.eng.town_hall.conduct_census(
                    ctx.physics, self.eng.host_stats
                )
                if report:
                    msg = _get_ux(
                        "cycle_strings", "town_hall_report", "📜 TOWN HALL: {report}"
                    )
                    ctx.log(f"{Prisma.CYN}{msg.format(report=report)}{Prisma.RST}")
            session_snapshot = {
                "trauma_vector": self.eng.trauma_accum,
                "meta": {"final_health": self.eng.health},
            }
            status, advice = self.eng.town_hall.diagnose_condition(
                session_data=session_snapshot,
                _host_health=self.eng.bio.biometrics if self.eng.bio else None,
                soul=self.eng.soul,
            )
            if status != "BALANCED":
                msg = _get_ux(
                    "cycle_strings",
                    "town_hall_vitals",
                    "🩺 VITAL SIGNS: {status} - {advice}",
                )
                ctx.log(
                    f"{Prisma.OCHRE}{msg.format(status=status, advice=advice)}{Prisma.RST}"
                )
        if self.eng.mind and hasattr(self.eng.mind, "mem"):
            if hasattr(self.eng.mind.mem, "run_ecosystem"):
                eco_logs = self.eng.mind.mem.run_ecosystem(
                    ctx.physics.to_dict(), self.eng.stamina, self.eng.tick_count
                )
                for log in eco_logs:
                    ctx.log(log)
        return ctx


class GatekeeperPhase(SimulationPhase):
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
                    msg = _get_ux(
                        "cycle_strings",
                        "gatekeep_locked",
                        "⛔ ACCESS DENIED: The machine is sulking.\n    Status: LOCKED (Solve the riddle or prove you are alive).",
                    )
                    ctx.refusal_packet = {
                        "ui": f"{dash_view}\n\n{Prisma.RED}{msg}{Prisma.RST}",
                        "logs": ["Command Rejected (Agency Lock)"],
                        "metrics": self.eng.get_metrics(),
                    }
                    return ctx
        if self.eng.gordon:
            current_zone = getattr(ctx.physics, "zone", "UNKNOWN")
            coupling_error = self.eng.gordon.enforce_object_action_coupling(
                ctx.input_text, current_zone
            )
            if coupling_error:
                ctx.refusal_triggered = True
                ctx.refusal_packet = {
                    "type": "PREMISE_VIOLATION",
                    "ui": f"\n{coupling_error}",
                    "logs": ["Premise Violation: Object-Action Coupling Failed"],
                    "metrics": self.eng.get_metrics(),
                }
                return ctx
        is_allowed, refusal_packet = self.gatekeeper.check_entry(ctx)
        if not is_allowed:
            ctx.refusal_triggered = True
            ctx.refusal_packet = refusal_packet
            return ctx
        if self.eng.bureau:
            current_bio = self.eng.get_metrics()
            audit_result = self.eng.bureau.audit(
                ctx.physics.to_dict(), current_bio, origin="USER"
            )
            if audit_result:
                if audit_result.get("block", False):
                    ctx.refusal_triggered = True
                    ctx.refusal_packet = {
                        "type": "BUREAU_BLOCK",
                        "ui": audit_result.get("ui", "Bureaucratic Injunction."),
                        "logs": ["Bureaucratic Block Triggered"],
                        "metrics": (
                            self.eng.get_metrics()
                            if hasattr(self.eng, "get_metrics")
                            else {}
                        ),
                    }
                    return ctx
                if self.eng.bio and self.eng.bio.mito:
                    self.eng.bio.mito.adjust_atp(
                        audit_result.get("atp_gain", 0.0), "Bureaucratic Fine (User)"
                    )
                if audit_result.get("log"):
                    ctx.log(audit_result["log"])
                if audit_result.get("ui"):
                    ctx.bureau_ui = audit_result["ui"]
                    ctx.is_bureaucratic = True
        return ctx


class MetabolismPhase(SimulationPhase):
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
                else 100.0
            )
            ctx.bio_result = {"is_alive": True, "logs": [], "atp": atp_level}
            ctx.is_alive = True
            self._apply_healing(ctx)
            return ctx
        physics = ctx.physics
        if hasattr(self.eng, "host_stats"):
            self._apply_economic_stimulus(ctx, self.eng.host_stats.efficiency_index)
        gov_msg = self.eng.bio.governor.shift(
            physics, self.eng.phys.dynamics.voltage_history, self.eng.tick_count
        )
        if gov_msg:
            self.eng.events.log(gov_msg, "GOV")
        physics.manifold = self.eng.bio.governor.mode
        max_v = getattr(BoneConfig.PHYSICS, "VOLTAGE_MAX", 20.0)
        bio_feedback = {
            "INTEGRITY": getattr(physics, "truth_ratio", 1.0),
            "STATIC": getattr(physics, "repetition", 0.0),
            "FORCE": getattr(physics, "voltage", 0.0) / max_v,
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
            circadian_bias=self._check_circadian_rhythm(),
        )
        if self.eng.bio.biometrics:
            self.eng.health = self.eng.bio.biometrics.health
            self.eng.stamina = self.eng.bio.biometrics.stamina
        ctx.is_alive = ctx.bio_result["is_alive"]
        for log in ctx.bio_result["logs"]:
            if any(x in str(log) for x in ["CRITICAL", "TAX", "Poison", "NECROSIS"]):
                ctx.log(log)
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
            self.eng.bio.mito.state.atp_pool = max(
                0.0, self.eng.bio.mito.state.atp_pool - tax_burn
            )
            msg = _get_ux(
                "cycle_strings",
                "metabolism_tax",
                "⚡ METABOLIC TAX: System strain burns {tax_burn:.1f} ATP.",
            )
            ctx.log(f"{Prisma.OCHRE}{msg.format(tax_burn=tax_burn)}{Prisma.RST}")

    def _check_narcolepsy(self, ctx: CycleContext):
        atp = self.eng.bio.mito.state.atp_pool
        starvation = getattr(BoneConfig.BIO, "ATP_STARVATION", 5.0)
        trigger = (atp < (starvation * 0.5)) or (
            self.eng.tick_count > 0 and self.eng.tick_count % 100 == 0
        )
        if trigger and hasattr(self.eng.mind, "dreamer"):
            msg_sleep = _get_ux(
                "cycle_strings",
                "metabolism_sleep",
                "\n[AUTO-SLEEP]: Forced reboot sequence.",
            )
            ctx.log(f"{Prisma.VIOLET}{msg_sleep}{Prisma.RST}")
            soul_snap = self.eng.soul.to_dict() if hasattr(self.eng, "soul") else {}
            self.eng.mind.dreamer.enter_rem_cycle(soul_snap, bio_state={"atp": atp})
            self.eng.mind.dreamer.run_defragmentation(self.eng.mind.mem)
            reboot_val = getattr(BoneConfig, "MAX_ATP", 100.0) * 0.33
            self.eng.bio.mito.state.atp_pool = reboot_val
            ctx.bio_result["atp"] = reboot_val
            msg_wake = _get_ux(
                "cycle_strings",
                "metabolism_waking",
                "   (System restored. ATP stabilized at {reboot_val:.1f})",
            )
            ctx.log(f"{Prisma.GRN}{msg_wake.format(reboot_val=reboot_val)}{Prisma.RST}")

    def _check_circadian_rhythm(self):
        if self.eng.tick_count % 10 == 0:
            bias, msg = self.eng.bio.endo.calculate_circadian_bias()
            if msg:
                self.eng.events.log(f"{Prisma.CYN}🕒 {msg}{Prisma.RST}", "BIO")
            return bias
        return None

    def _audit_hubris(self, ctx, physics):
        hit, msg, evt = self.eng.phys.tension.audit_hubris(physics.to_dict())
        if hit:
            ctx.log(msg)
            if evt == "FLOW_BOOST":
                self.eng.bio.mito.state.atp_pool += 20.0
            elif evt == "ICARUS_CRASH":
                damage = 15.0
                msg_impact = _get_ux(
                    "cycle_strings",
                    "metabolism_impact",
                    "   IMPACT TRAUMA: -{damage} HP.",
                )
                ctx.log(f"{Prisma.RED}{msg_impact.format(damage=damage)}{Prisma.RST}")
                if self.eng.bio.biometrics:
                    self.eng.bio.biometrics.health = max(
                        0.0, self.eng.bio.biometrics.health - damage
                    )
                self.eng.health -= damage

    def _apply_healing(self, ctx):
        qualia = self.eng.somatic.get_current_qualia(getattr(ctx, "last_impulse", None))
        current_stamina = self.eng.stamina
        if self.eng.bio.biometrics:
            current_stamina = self.eng.bio.biometrics.stamina
        cracked, koan = self.eng.kintsugi.check_integrity(current_stamina)
        if cracked:
            msg = _get_ux(
                "cycle_strings",
                "metabolism_kintsugi",
                "🏺 KINTSUGI ACTIVATED. KOAN: {koan}",
            )
            ctx.log(f"{Prisma.YEL}{msg.format(koan=koan)}{Prisma.RST}")
        if self.eng.kintsugi.active_koan:
            repair = self.eng.kintsugi.attempt_repair(
                ctx.physics, self.eng.trauma_accum, self.eng.soul, qualia
            )
            if repair and repair["success"]:
                ctx.log(repair["msg"])
                heal_amt = 20.0

                if hasattr(self.eng.mind.mem, "record_scar"):
                    self.eng.mind.mem.record_scar(
                        self.eng.kintsugi.active_koan or "Healed Rupture", ctx.physics
                    )

                if self.eng.bio.biometrics:
                    self.eng.bio.biometrics.stamina = min(
                        BoneConfig.MAX_STAMINA,
                        self.eng.bio.biometrics.stamina + heal_amt,
                    )
                self.eng.stamina = min(
                    BoneConfig.MAX_STAMINA, self.eng.stamina + heal_amt
                )
        if self.eng.therapy.check_progress(
            ctx.physics, current_stamina, self.eng.trauma_accum, qualia
        ):
            msg = _get_ux(
                "cycle_strings",
                "metabolism_therapy",
                "❤️ THERAPY: Trauma processed. Health +5.",
            )
            ctx.log(f"{Prisma.GRN}{msg}{Prisma.RST}")
            if self.eng.bio.biometrics:
                self.eng.bio.biometrics.health = min(
                    BoneConfig.MAX_HEALTH, self.eng.bio.biometrics.health + 5.0
                )
            self.eng.health = min(BoneConfig.MAX_HEALTH, self.eng.health + 5.0)

    def _check_autophagy(self, ctx: CycleContext):
        if self.eng.bio.mito.state.atp_pool <= 0:
            if hasattr(self.eng.mind.mem, "trigger_autophagy"):
                atp_gain, msg = self.eng.mind.mem.trigger_autophagy()
                self.eng.bio.mito.state.atp_pool += atp_gain
                ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")

    def _check_ros_toxicity(self, ctx: CycleContext):
        if self.eng.bio.mito.state.ros_buildup >= 100.0:
            msg = _get_ux(
                "cycle_strings",
                "metabolism_panic",
                "☣️ PANIC ROOM: Toxicity critical (ROS 100). Venting.",
            )
            ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")
            ctx.physics.psi = 0.0
            ctx.physics.chi = 0.0
            self.eng.bio.mito.state.ros_buildup *= 0.5
            ctx.physics.flow_state = "SAFE_MODE"


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
                msg = _get_ux(
                    "cycle_strings",
                    "filter_iching",
                    "I CHING: {sym} {name} is in the ascendant.",
                )
                ctx.log(f"{color}{msg.format(sym=sym, name=name)}{Prisma.RST}")
        return ctx


class NavigationPhase(SimulationPhase):
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
        new_drag, grav_logs = self.eng.phys.dynamics.check_gravity(
            current_drift=physics.narrative_drag, psi=physics.psi
        )
        physics.narrative_drag = new_drag
        for log in grav_logs:
            ctx.log(log)
        if self.eng.gordon:
            phys_snapshot = physics.to_dict()
            reflex_triggered, reflex_msg = self.eng.gordon.emergency_reflex(
                phys_snapshot
            )
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
            current_loc, entry_msg = self.eng.navigator.locate(
                packet=ctx.physics,
            )
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
                    msg = _get_ux(
                        "cycle_strings",
                        "nav_gear_drag",
                        "🎒 GEAR: {source} affects drag ({operator} {value}).",
                    )
                    ctx.log(
                        f"{Prisma.GRY}{msg.format(source=delta.source, operator=delta.operator, value=delta.value)}{Prisma.RST}"
                    )
        orbit_state, drag_pen, orbit_msg = self.eng.cosmic.analyze_orbit(
            self.eng.mind.mem, ctx.clean_words
        )
        if orbit_msg:
            ctx.log(orbit_msg)
        physics.narrative_drag += drag_pen
        if orbit_state == "VOID_DRIFT":
            physics.voltage = max(0.0, physics.voltage - 0.5)
        elif orbit_state == "LAGRANGE_POINT":
            physics.narrative_drag = max(0.1, physics.narrative_drag - 2.0)
        elif orbit_state == "WATERSHED_FLOW":
            physics.voltage += 0.5
        raw_zone = getattr(physics, "zone", "COURTYARD")
        stabilization_result = self.eng.stabilizer.stabilize(
            proposed_zone=raw_zone,
            physics=phys_dict,
            cosmic_state=(orbit_state, drag_pen),
        )
        if isinstance(stabilization_result, tuple):
            stabilized_zone = stabilization_result[0]
            if len(stabilization_result) > 1 and stabilization_result[1]:
                ctx.log(stabilization_result[1])
        else:
            stabilized_zone = stabilization_result
        physics.zone = stabilized_zone
        adjusted_drag = self.eng.stabilizer.override_cosmic_drag(
            drag_pen, stabilized_zone
        )
        if adjusted_drag != drag_pen:
            physics.narrative_drag -= drag_pen - adjusted_drag
        ctx.world_state["orbit"] = orbit_state
        return ctx


class MachineryPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "MACHINERY"

    def run(self, ctx: CycleContext):
        if ctx.is_system_event:
            return ctx
        phys_dict = ctx.physics.to_dict()
        if hasattr(self.eng, "critics") and (
            review := self.eng.critics.audit_performance(phys_dict, self.eng.tick_count)
        ):
            ctx.log(review)
            ctx.physics.narrative_drag += -1.0 if "🌟" in review else 1.0
        boost, z_msg = self.eng.zen.raking_the_sand(phys_dict, ctx.bio_result)
        if z_msg:
            ctx.log(z_msg)
        if boost > 0:
            self.eng.bio.mito.state.membrane_potential = min(
                2.0, self.eng.bio.mito.state.efficiency_mod + (boost * 0.1)
            )
        if self.eng.gordon and self.eng.gordon.inventory:
            self._process_crafting(ctx, phys_dict)
        if t_msg := self.eng.phys.forge.transmute(phys_dict):
            ctx.log(t_msg)
        _, f_msg, new_item = self.eng.phys.forge.hammer_alloy(phys_dict)
        if f_msg:
            ctx.log(f_msg)
        if new_item and self.eng.gordon:
            ctx.log(self.eng.gordon.acquire(new_item))
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
            damage = c_val
            if self.eng.bio.biometrics:
                self.eng.bio.biometrics.health = max(
                    0.0, self.eng.bio.biometrics.health - damage
                )
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
        is_craft, craft_msg, old_item, new_item = self.eng.phys.forge.attempt_crafting(
            phys_dict, self.eng.gordon.inventory
        )
        if is_craft:
            ctx.log(craft_msg)
            vec = ctx.physics.vector
            catalyst_cat = max(vec, key=vec.get) if vec else "void"
            self.eng.events.publish(
                "FORGE_SUCCESS",
                {"ingredient": old_item, "catalyst": catalyst_cat, "result": new_item},
            )
            if old_item in self.eng.gordon.inventory:
                self.eng.gordon.inventory.remove(old_item)
            ctx.log(self.eng.gordon.acquire(new_item))

    def _handle_theremin_discharge(self, ctx):
        max_hp = getattr(BoneConfig, "MAX_HEALTH", 100.0)
        damage = max_hp * 0.25
        if self.eng.bio.biometrics:
            self.eng.bio.biometrics.health = max(
                0.0, self.eng.bio.biometrics.health - damage
            )
        self.eng.health = max(0.0, self.eng.health - damage)
        msg = _get_ux(
            "cycle_strings",
            "machinery_theremin",
            "*** CRITICAL THEREMIN DISCHARGE *** -{damage:.1f} HP",
        )
        ctx.log(f"{Prisma.RED}{msg.format(damage=damage)}{Prisma.RST}")
        if hasattr(self.eng.events, "publish"):
            self.eng.events.publish(
                "AIRSTRIKE", {"damage": damage, "source": "THEREMIN"}
            )


class IntrusionPhase(SimulationPhase):
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
                msg = _get_ux("cycle_strings", "intrusion_heavy", "The air is heavy.")
                ctx.log(self.eng.limbo.haunt(msg))

        drag = getattr(ctx.physics, "narrative_drag", 0.0)
        kappa = getattr(ctx.physics, "kappa", 1.0)

        if (drag > 4.0 or kappa < 0.3) and ctx.clean_words:
            start_node = random.choice(ctx.clean_words)
            loop_path = self.eng.mind.tracer.inject(start_node)
            if loop_path:
                rewire_msg = self.eng.mind.tracer.psilocybin_rewire(loop_path)
                if rewire_msg:
                    msg = _get_ux(
                        "cycle_strings",
                        "intrusion_immune",
                        "🦠 IMMUNE SYSTEM: {rewire_msg}",
                    )
                    ctx.log(
                        f"{Prisma.CYN}{msg.format(rewire_msg=rewire_msg)}{Prisma.RST}"
                    )
                    self.eng.bio.endo.dopamine += 0.2
                    ctx.physics.narrative_drag = max(0.0, drag - 2.0)
        trauma_sum = (
            sum(self.eng.trauma_accum.values())
            if getattr(self.eng, "trauma_accum", None)
            else 0.0
        )
        is_bored = self.eng.phys.pulse.is_bored()
        if (trauma_sum > 10.0 or is_bored) and random.random() < 0.2:
            dream_text, relief = self.eng.mind.dreamer.hallucinate(
                ctx.physics.vector, trauma_level=trauma_sum
            )
            if trauma_sum > 10.0:
                prefix = _get_ux(
                    "cycle_strings", "intrusion_nightmare", "💭 NIGHTMARE: {dream_text}"
                )
            else:
                prefix = _get_ux(
                    "cycle_strings", "intrusion_daydream", "💭 DAYDREAM: {dream_text}"
                )
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
                    msg_relief = _get_ux(
                        "cycle_strings",
                        "intrusion_relief",
                        "   (Psychic pressure released: -{relief:.1f} {target})",
                    )
                    ctx.log(
                        f"{Prisma.GRY}{msg_relief.format(relief=relief, target=target)}{Prisma.RST}"
                    )
            if is_bored:
                self.eng.phys.pulse.boredom_level = 0.0
        current_psi = getattr(ctx.physics, "psi", 0.0)
        if current_psi > 0.6 and random.random() < current_psi:
            msg_p = _get_ux(
                "cycle_strings",
                "intrusion_pareidolia",
                "👁️ PAREIDOLIA: The patterns are watching back (PSI {current_psi:.2f}).",
            )
            ctx.log(
                f"{Prisma.VIOLET}{msg_p.format(current_psi=current_psi)}{Prisma.RST}"
            )
            ctx.physics.psi = min(1.0, current_psi + 0.1)
            if self.eng.bio and self.eng.bio.biometrics:
                self.eng.bio.biometrics.stamina = max(
                    0.0, self.eng.bio.biometrics.stamina - 5.0
                )
                msg_drain = _get_ux(
                    "cycle_strings",
                    "intrusion_hallucination_drain",
                    "   (The hallucination drains 5.0 Stamina)",
                )
                ctx.log(f"{Prisma.GRY}{msg_drain}{Prisma.RST}")
        return ctx


class SoulPhase(SimulationPhase):
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
            msg = _get_ux(
                "cycle_strings",
                "soul_dignity_low",
                "⚓ DIGNITY CRITICAL: The narrative feels heavy. (Drag x1.5)",
            )
            ctx.log(f"{Prisma.GRY}{msg}{Prisma.RST}")
        elif dignity > 80.0:
            ctx.physics.voltage += 2.0
            ctx.physics.narrative_drag *= 0.8
            msg = _get_ux(
                "cycle_strings",
                "soul_dignity_high",
                "✨ DIGNITY HIGH: The soul is sovereign. (Flow Optimized)",
            )
            ctx.log(f"{Prisma.MAG}{msg}{Prisma.RST}")
        lesson = self.eng.soul.crystallize_memory(
            ctx.physics.to_dict(), ctx.bio_result, self.eng.tick_count
        )
        if lesson:
            msg = _get_ux(
                "cycle_strings",
                "soul_lesson",
                "   (The lesson '{lesson}' echoes in the chamber.)",
            )
            ctx.log(f"{Prisma.VIOLET}{msg.format(lesson=lesson)}{Prisma.RST}")
        if not self.eng.soul.current_obsession:
            self.eng.soul.find_obsession(self.eng.lex)
        self.eng.soul.pursue_obsession(ctx.physics.to_dict())
        if hasattr(self.eng, "oroboros") and self.eng.oroboros.myths:
            for myth in self.eng.oroboros.myths:
                if myth.trigger in ctx.clean_words:
                    msg = _get_ux(
                        "cycle_strings", "soul_myth", "📜 ANCIENT MYTH INVOKED: {title}"
                    )
                    ctx.log(f"{Prisma.YEL}{msg.format(title=myth.title)}{Prisma.RST}")
                    ctx.log(f'   "{myth.lesson}"')
                    old_volts = ctx.physics.voltage
                    ctx.physics.voltage += 5.0
                    ctx.record_flux(
                        "SOUL", "VOLTAGE", old_volts, ctx.physics.voltage, "MYTH_BUFF"
                    )
                    if self.eng.bio.biometrics:
                        self.eng.bio.biometrics.stamina = min(
                            100.0, self.eng.bio.biometrics.stamina + 5.0
                        )
        if self.eng.gordon and self.eng.tinkerer:
            if self.eng.gordon.inventory:
                self.eng.tinkerer.audit_tool_use(ctx.physics, self.eng.gordon.inventory)
        council_mandates = self._consult_council(self.eng.soul.traits)
        if council_mandates:
            ctx.council_mandates = (
                getattr(ctx, "council_mandates", []) + council_mandates
            )
            for mandate in council_mandates:
                ctx.log(mandate["log"])
                self._execute_mandate(ctx, mandate)
        council_advice, adjustments, mandates = self.eng.council.convene(
            ctx.input_text, ctx.physics, ctx.bio_result
        )
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
                msg = _get_ux(
                    "cycle_strings",
                    "council_force_mode",
                    "⚖️ COUNCIL ORDER: Emergency Shift to {target}.",
                )
                ctx.log(f"{Prisma.RED}{msg.format(target=target)}{Prisma.RST}")
            elif action == "CIRCUIT_BREAKER":
                ctx.physics.voltage = 0.0
                ctx.physics.narrative_drag = 10.0
                msg = _get_ux(
                    "cycle_strings",
                    "council_circuit_breaker",
                    "⚖️ COUNCIL ORDER: Circuit Breaker Tripped. Voltage dump.",
                )
                ctx.log(f"{Prisma.RED}{msg}{Prisma.RST}")
        if adjustments:
            for param, delta in adjustments.items():
                old_val = getattr(ctx.physics, param, 0.0)
                new_val = old_val + delta
                setattr(ctx.physics, param, new_val)
                ctx.record_flux(
                    "SIMULATION", param, old_val, new_val, "COUNCIL_MANDATE"
                )
        return ctx

    @staticmethod
    def _consult_council(traits: Any) -> List[Dict]:
        t_map = (
            traits.to_dict()
            if hasattr(traits, "to_dict")
            else (traits.__dict__ if hasattr(traits, "__dict__") else traits)
        )
        get_t = lambda k: t_map.get(k, t_map.get(k.lower(), 0.0))
        rules = [
            (
                "CYNICISM",
                0.8,
                "LOCKDOWN",
                "The Cynic holds the gavel. 'Stop doing things.'",
                {"narrative_drag": 5.0, "voltage": -5.0},
                Prisma.OCHRE,
            ),
            (
                "HOPE",
                0.8,
                "STIMULUS",
                "The Optimist filibustered. 'We can build it!'",
                {"voltage": 5.0, "narrative_drag": -2.0},
                Prisma.MAG,
            ),
            (
                "DISCIPLINE",
                0.8,
                "STANDARDIZE",
                "The Engineer demands efficiency.",
                {"kappa": -0.5, "beta_index": 1.0},
                Prisma.CYN,
            ),
        ]
        mandates = []
        for trait, thresh, m_type, msg, eff, col in rules:
            if get_t(trait) > thresh:
                str_msg = _get_ux("cycle_strings", "council_log", "⚖️ COUNCIL: {msg}")
                mandates.append(
                    {
                        "type": m_type,
                        "log": f"{col}{str_msg.format(msg=msg)}{Prisma.RST}",
                        "effect": eff,
                    }
                )
        return mandates

    @staticmethod
    def _execute_mandate(ctx: CycleContext, mandate: Dict):
        effects = mandate.get("effect", {})
        for key, delta in effects.items():
            current = getattr(ctx.physics, key, 0.0)
            setattr(ctx.physics, key, max(0.0, current + delta))


class ArbitrationPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "ARBITRATION"
        if not hasattr(self.eng, "arbiter"):
            self.eng.arbiter = ArchetypeArbiter()

    def run(self, ctx: CycleContext):
        phys_lens, _, _ = self.eng.drivers.enneagram.decide_persona(
            ctx.physics, soul_ref=self.eng.soul
        )
        soul_arch = self.eng.soul.archetype
        mandates = getattr(ctx, "council_mandates", [])
        current_trigram = ctx.world_state.get("trigram", None)

        final_lens, source, opinion = self.eng.arbiter.arbitrate(
            physics_lens=phys_lens,
            soul_archetype=soul_arch,
            council_mandates=mandates,
            trigram=current_trigram,
        )
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

        if tension > 0.85 and silence < 0.5 and not synergy_active:
            final_lens = "THE STAGE MANAGER"
            opinion = "The tension is too high. The Stage Manager cuts the mic. Silence is enforced."
            ctx.physics.silence = 0.9
            ctx.physics.narrative_drag += 2.0
            msg = _get_ux(
                "cycle_strings",
                "arbiter_stage_manager_cut",
                "🎭 STAGE MANAGER: 'Too many voices. Step back.'",
            )
            ctx.log(f"{Prisma.WHT}{msg}{Prisma.RST}")
            msg_silence = _get_ux(
                "cycle_strings",
                "arbiter_silence",
                "∇ [THE SILENCE]: The system pauses, waiting for structure.",
            )
            ctx.log(f"{Prisma.GRY}{msg_silence}{Prisma.RST}")

        elif silence > 0.85 and not synergy_active:
            final_lens = "THE STAGE MANAGER"
            opinion = "The Stage Manager holds the silence. No archetype is called."
            msg = _get_ux(
                "cycle_strings",
                "arbiter_stage_manager_hold",
                "🎭 STAGE MANAGER: (Gestures for the cosmos to hold.)",
            )
            ctx.log(f"{Prisma.WHT}{msg}{Prisma.RST}")

        else:
            if synergy_active and synergy_name:
                final_lens = synergy_name
                msg = _get_ux(
                    "cycle_strings",
                    "arbiter_synergy_named",
                    "🎭 (The Stage Manager steps back. [{synergy_name}] speaks.)",
                )
                ctx.log(
                    f"{Prisma.GRY}{msg.format(synergy_name=synergy_name)}{Prisma.RST}"
                )
            elif synergy_active:
                msg = _get_ux(
                    "cycle_strings",
                    "arbiter_synergy_unnamed",
                    "🎭 (The Stage Manager steps back. The Synergy speaks.)",
                )
                ctx.log(f"{Prisma.GRY}{msg}{Prisma.RST}")
            else:
                msg = _get_ux(
                    "cycle_strings",
                    "arbiter_normal_lens",
                    "🎭 (The Stage Manager nods. {final_lens} steps into the light.)",
                )
                ctx.log(f"{Prisma.GRY}{msg.format(final_lens=final_lens)}{Prisma.RST}")

        ctx.active_lens = final_lens
        self.eng.events.publish("LENS_INTERACTION", {"lenses": [phys_lens, soul_arch]})

        if source != "PHYSICS_VECTOR" or final_lens == "THE STAGE MANAGER":
            msg = _get_ux("cycle_strings", "arbiter_opinion", "⚖️ {opinion}")
            ctx.log(f"{Prisma.MAG}{msg.format(opinion=opinion)}{Prisma.RST}")

        self.eng.drivers.current_focus = final_lens
        return ctx


class CognitionPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "COGNITION"

    def run(self, ctx: CycleContext):
        if ctx.validator and ctx.input_text:
            phi = ctx.validator.calculate_resonance(ctx.input_text, ctx)
            if phi > 0.8:
                drag_relief = (phi - 0.5) * 2.0
                ctx.physics.narrative_drag = max(
                    0.0, ctx.physics.narrative_drag - drag_relief
                )
                if self.eng.bio and self.eng.bio.mito:
                    refund = 5.0 * phi
                    self.eng.bio.mito.adjust_atp(refund, "Harmonic Resonance")
                msg = _get_ux(
                    "cycle_strings",
                    "cog_resonance",
                    "✨ HARMONIC RESONANCE (Φ={phi:.2f}): The narrative flows effortlessly.",
                )
                ctx.log(f"{Prisma.CYN}{msg.format(phi=phi)}{Prisma.RST}")
        if hasattr(self.eng, "consultant"):
            self.eng.consultant.update_coordinates(
                ctx.input_text, ctx.bio_result, ctx.physics
            )
            if (
                "LIMINAL" in self.eng.consultant.state.active_modules
                and self.eng.bio
                and self.eng.bio.mito
            ):
                lambda_val = self.eng.consultant.state.L
                if lambda_val > 0.1:
                    lambda_tax = (lambda_val**2) * 10.0
                    self.eng.bio.mito.adjust_atp(-lambda_tax, f"Λ² Liminal Tax")
                    if lambda_tax > 2.0:
                        msg = _get_ux(
                            "cycle_strings",
                            "cog_liminal_tax",
                            "🌌 DARK MATTER: Liminal navigation burns {lambda_tax:.1f} ATP.",
                        )
                        ctx.log(
                            f"{Prisma.VIOLET}{msg.format(lambda_tax=lambda_tax)}{Prisma.RST}"
                        )
        if hasattr(self.eng.mind.mem, "check_for_resurrection"):
            flashback_msg = self.eng.mind.mem.check_for_resurrection(
                ctx.clean_words, ctx.physics.voltage
            )
            if flashback_msg:
                ctx.log(f"{Prisma.MAG}{flashback_msg}{Prisma.RST}")
                shock_cost = 5.0
                if self.eng.bio.biometrics:
                    self.eng.bio.biometrics.stamina = max(
                        0.0, self.eng.bio.biometrics.stamina - shock_cost
                    )
                self.eng.stamina = max(0.0, self.eng.stamina - shock_cost)
        self.eng.mind.mem.encode(ctx.clean_words, ctx.physics.to_dict(), "GEODESIC")
        if ctx.is_alive and ctx.clean_words:
            max_h = getattr(BoneConfig, "MAX_HEALTH", 100.0)
            current_h = max(0.0, self.eng.health)
            if self.eng.bio.biometrics:
                current_h = max(0.0, self.eng.bio.biometrics.health)
            desperation = 1.0 - (current_h / max_h)
            learn_mod = getattr(BoneConfig, "PRIORITY_LEARNING_RATE", 1.0)
            bury_msg, new_wells = self.eng.mind.mem.bury(
                ctx.clean_words,
                self.eng.tick_count,
                resonance=ctx.physics.voltage,
                desperation_level=desperation,
                learning_mod=learn_mod,
            )
            if bury_msg:
                if "SATURATION" in bury_msg:
                    prefix = f"{Prisma.YEL}{_get_ux('cycle_strings', 'cog_memory_warn', '⚠️ MEMORY: {bury_msg}').format(bury_msg=bury_msg)}{Prisma.RST}"
                else:
                    prefix = f"{Prisma.RED}{_get_ux('cycle_strings', 'cog_memory_donner', '🍖 DONNER PROTOCOL: {bury_msg}').format(bury_msg=bury_msg)}{Prisma.RST}"
                ctx.log(prefix)
            if new_wells:
                msg = _get_ux(
                    "cycle_strings",
                    "cog_gravity_well",
                    "🌌 GRAVITY WELL FORMED: {new_wells}",
                )
                ctx.log(f"{Prisma.CYN}{msg.format(new_wells=new_wells)}{Prisma.RST}")

        inventory_data = self.eng.gordon.inventory if self.eng.gordon else []

        ctx.mind_state = self.eng.noetic.think(
            physics_packet=ctx.physics.to_dict(),
            _bio=ctx.bio_result,
            _inventory=inventory_data,
            voltage_history=self.eng.phys.dynamics.voltage_history,
            _tick_count=self.eng.tick_count,
            soul_ref=self.eng.soul,
        )

        thought = ctx.mind_state.get("context_msg", ctx.mind_state.get("thought"))
        if thought:
            ctx.log(thought)
        return ctx


class SensationPhase(SimulationPhase):
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
        impulse = self.synesthesia.perceive(
            phys_data, traits=self.eng.soul.traits, latency=current_latency
        )
        ctx.last_impulse = impulse
        qualia = self.synesthesia.get_current_qualia(impulse)
        ctx.physics = apply_somatic_feedback(ctx.physics, qualia)
        self.synesthesia.apply_impulse(impulse)
        if impulse.stamina_impact != 0:
            max_s = getattr(BoneConfig, "MAX_STAMINA", 100.0)
            if self.eng.bio.biometrics:
                self.eng.bio.biometrics.stamina = max(
                    0.0,
                    min(
                        max_s, self.eng.bio.biometrics.stamina + impulse.stamina_impact
                    ),
                )
            self.eng.stamina = max(
                0.0, min(max_s, self.eng.stamina + impulse.stamina_impact)
            )
        return ctx


class StabilizationPhase(SimulationPhase):
    def __init__(self, engine_ref, stabilizer_ref):
        super().__init__(engine_ref)
        self.name = "STABILIZATION"
        self.stabilizer = stabilizer_ref

    def run(self, ctx: CycleContext):
        self.stabilizer.stabilize(ctx, self.name)
        return ctx


class PhaseExecutor:
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
        self.pipeline: List[SimulationPhase] = [
            ObservationPhase(engine_ref),
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
            CognitionPhase(engine_ref),
            StabilizationPhase(engine_ref, self.stabilizer),
        ]

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
        msg_crash = _get_ux(
            "cycle_strings", "sim_crash_header", "!!! CRITICAL {phase_name} CRASH !!!"
        )
        print(f"\n{Prisma.RED}{msg_crash.format(phase_name=phase_name)}{Prisma.RST}")
        traceback.print_exc()
        narrative = LoreManifest.get_instance().get("narrative_data") or {}
        cathedral_logs = narrative.get("CATHEDRAL_COLLAPSE_LOGS", ["System Failure."])
        eulogy = random.choice(cathedral_logs)
        msg_eulogy = _get_ux(
            "cycle_strings",
            "sim_cathedral_collapse",
            '🏛️ CATHEDRAL COLLAPSE: "{eulogy}"',
        )
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
        msg_panic = _get_ux(
            "cycle_strings",
            "sim_panic_switch",
            "⚠ {phase_name} FAILURE: Switching to Panic Protocol.",
        )
        ctx.log(f"{Prisma.RED}{msg_panic.format(phase_name=phase_name)}{Prisma.RST}")


class GeodesicOrchestrator:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.simulator = CycleSimulator(engine_ref)
        self.reporter = CycleReporter(engine_ref)
        if hasattr(self.eng, "symbiosis"):
            self.symbiosis = self.eng.symbiosis
        else:
            self.symbiosis = SymbiosisManager(self.eng.events)

    def _execute_core_cycle(
        self, user_message: str, is_system: bool = False
    ) -> CycleContext:
        cycle_id = str(uuid.uuid4())[:8]
        try:
            ctx = CycleContext(input_text=user_message, is_system_event=is_system)
            ctx.trace_id = cycle_id
            if (
                self.eng.phys
                and hasattr(self.eng.phys, "observer")
                and self.eng.phys.observer.last_physics_packet
            ):
                ctx.physics = self.eng.phys.observer.last_physics_packet.snapshot()
            elif not ctx.physics:
                ctx.physics = PanicRoom.get_safe_physics()
                msg = _get_ux(
                    "cycle_strings",
                    "orch_physics_bypass",
                    "⚠️ PHYSICS BYPASS: Running on Panic Protocol.",
                )
                self.eng.events.log(msg, "SYS")
            ctx.validator = CongruenceValidator()
            ctx.reality_stack = getattr(self.eng, "reality_stack", None)
            ctx.user_name = self.eng.user_name
            ctx.council_mandates = []
            ctx.timestamp = time.time()
            pre_logs = [e["text"] for e in self.eng.events.flush()]
            ctx.logs.extend(pre_logs)
            ctx = self.simulator.run_simulation(ctx)
            if self.eng.phys and hasattr(self.eng.phys, "observer"):
                self.eng.phys.observer.last_physics_packet = ctx.physics.snapshot()
            return ctx
        except Exception as e:
            self.eng.events.log(f"CYCLE CRASH: {e}", "CRIT")
            ctx = CycleContext(input_text=user_message)
            ctx.is_alive = False
            ctx.crash_error = e
            return ctx

    def run_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
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
            ctx, "refusal_packet", None
        ):
            return ctx.refusal_packet

        snapshot = self.reporter.render_snapshot(ctx)
        self._hydrate_snapshot_metadata(snapshot, ctx)
        latency = time.time() - ctx.timestamp
        if "ui" in snapshot:
            self.symbiosis.monitor_host(latency, snapshot["ui"], len(user_message))
        return snapshot

    def run_headless_turn(
        self, user_message: str, latency: float = 0.0
    ) -> Dict[str, Any]:
        ctx = self._execute_core_cycle(user_message)
        if not ctx.is_alive:
            if hasattr(ctx, "crash_error"):
                return self._generate_crash_report(ctx.crash_error)
            return self.eng.trigger_death(ctx.physics)

        if getattr(ctx, "refusal_triggered", False) and getattr(
            ctx, "refusal_packet", None
        ):
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
            {
                "trace_id": getattr(ctx, "trace_id", "UNKNOWN"),
                "is_alive": True,
                "physics": _safe_dict(ctx.physics),
                "bio": _safe_dict(ctx.bio_result),
                "mind": _safe_dict(ctx.mind_state),
                "world": _safe_dict(ctx.world_state),
                "soul": _safe_dict(getattr(self.eng, "soul", {})),
                "council_mandates": getattr(ctx, "council_mandates", []),
                "dream": getattr(ctx, "last_dream", None),
            }
        )

    @staticmethod
    def _generate_crash_report(e: Exception) -> Dict[str, Any]:
        full_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        safe_phys = PanicRoom.get_safe_physics()
        safe_bio = PanicRoom.get_safe_bio()
        msg = _get_ux(
            "cycle_strings",
            "orch_reality_fracture",
            "\n*** REALITY FRACTURE: {error} ***\n{trace}\n[System stabilized in Safe Mode]",
        )
        ui_report = f"{Prisma.RED}{msg.format(error=e, trace=full_trace)}{Prisma.RST}"
        return {
            "type": "CRASH",
            "ui": ui_report,
            "physics": safe_phys.to_dict(),
            "bio": safe_bio,
            "mind": PanicRoom.get_safe_mind(),
            "world": {"orbit": ["VOID"], "loci_description": "System Failure"},
            "logs": ["CRITICAL FAILURE", "SAFE MODE ACTIVE"],
            "is_alive": True,
        }
