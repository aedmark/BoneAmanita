"""bone_cycle.py"""

import random
import re
import time
import traceback
import uuid
import threading
from typing import Dict, Any, List, Optional

from bone_core import LoreManifest, ux, safe_get
from bone_drivers import CongruenceValidator
from bone_gui import CycleReporter
from bone_machine import PanicRoom
from bone_phases import (
    ObservationPhase,
    SanctuaryPhase,
    MaintenancePhase,
    GatekeeperPhase,
    MetabolismPhase,
    RealityFilterPhase,
    NavigationPhase,
    MachineryPhase,
    IntrusionPhase,
    SoulPhase,
    ArbitrationPhase,
    SimulationPreflightPhase,
    CognitionPhase,
    SensationPhase,
    StabilizationPhase, SimulationPhase,
)
from bone_physics import CycleStabilizer
from bone_presets import BoneConfig
from bone_symbiosis import SymbiosisManager
import math
from bone_types import Prisma, CycleContext

""" NAVI FRACTAL NATIVE PRIMITIVES (Authored by Nelson Spence, Project Navi, Apache 2.0) """
def _native_wls(x: list[float], y: list[float], weights: list[float]) -> float:
    """Weighted least squares slope calculation for fractal dimension."""
    sum_w = sum(weights)
    if sum_w == 0.0: return 0.0
    mean_x = sum(w * xi for w, xi in zip(weights, x)) / sum_w
    mean_y = sum(w * yi for w, yi in zip(weights, y)) / sum_w
    ss_xx = sum(w * xi * xi for w, xi in zip(weights, x)) - sum_w * mean_x * mean_x
    ss_xy = sum(w * xi * yi for w, xi, yi in zip(weights, x, y)) - sum_w * mean_x * mean_y
    return ss_xy / ss_xx if ss_xx != 0.0 else 0.0

def _native_rewire(adj_dict: dict, n_swaps: int) -> dict:
    """Maslov-Sneppen degree-preserving rewiring for null model generation."""
    edges = [(u, v) for u in adj_dict for v in adj_dict[u] if u < v]
    if len(edges) < 2: return adj_dict
    adj = {k: set(v) for k, v in adj_dict.items()}
    for _ in range(n_swaps):
        i1, i2 = random.randrange(len(edges)), random.randrange(len(edges))
        if i1 == i2: continue
        u, v = edges[i1]
        x, y = edges[i2]
        new1, new2 = ((u, y), (v, x)) if random.random() < 0.5 else ((u, x), (v, y))
        a1, b1, a2, b2 = new1[0], new1[1], new2[0], new2[1]
        if a1 == b1 or a2 == b2 or b1 in adj.get(a1, set()) or b2 in adj.get(a2, set()): continue
        if (min(a1, b1), max(a1, b1)) == (min(a2, b2), max(a2, b2)): continue
        adj[u].discard(v); adj[v].discard(u)
        adj[x].discard(y); adj[y].discard(x)
        adj.setdefault(a1, set()).add(b1); adj.setdefault(b1, set()).add(a1)
        adj.setdefault(a2, set()).add(b2); adj.setdefault(b2, set()).add(a2)
        edges[i1], edges[i2] = (min(a1, b1), max(a1, b1)), (min(a2, b2), max(a2, b2))
    return adj

def _native_freeze_graph(adj_dict: dict) -> tuple:
    """Deterministic graph freezing for Gödel Scars."""
    nodes = sorted(adj_dict.keys(), key=lambda k: str(k))
    return tuple(tuple(sorted(adj_dict[n], key=lambda k: str(k))) for n in nodes)

def _safe_dict(obj):
    return obj.to_dict() if hasattr(obj, "to_dict") else (obj if isinstance(obj, dict) else {})


class PhaseExecutor:
    def execute_phases(self, simulator, ctx):
        active_pipeline = (
            simulator.system_pipeline
            if getattr(ctx, "is_system_event", False)
            else simulator.full_pipeline
        )
        for phase in active_pipeline:
            if getattr(ctx, "refusal_triggered", False):
                break
            if not simulator.check_circuit_breaker(phase.name):
                continue
            try:
                ctx = phase.run(ctx)
            except Exception as e:
                simulator.handle_phase_crash(ctx, phase.name, e)
                break
        return ctx


class CycleSimulator:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.shared_governor = self.eng.bio.governor
        target_cfg = getattr(self.eng, "bone_config", BoneConfig)
        self.stabilizer = CycleStabilizer(
            self.eng.events, self.shared_governor, config_ref=target_cfg
        )
        self.executor = PhaseExecutor()
        self.full_pipeline: List[SimulationPhase] = [
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
            SimulationPreflightPhase(engine_ref),
            CognitionPhase(engine_ref),
            StabilizationPhase(engine_ref, self.stabilizer),
        ]
        self.system_pipeline = [
            p
            for p in self.full_pipeline
            if p.name in ["OBSERVE", "GATEKEEP", "STABILIZATION"]
        ]

    def run_simulation(self, ctx: CycleContext) -> CycleContext:
        ctx = self.executor.execute_phases(self, ctx)
        return ctx

    def check_circuit_breaker(self, phase_name: str) -> bool:
        h = self.eng.system_health
        breakers = {"OBSERVE": h.physics_online, "COGNITION": h.mind_online}
        return breakers.get(phase_name, True)

    def handle_phase_crash(self, ctx, phase_name, error):
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

        """ CompiledGraph / Gödel Scar Baseline (Gordon's Panic Room)
            Native deterministic graph freezing based on Nelson Spence (Project Navi).
        """
        if hasattr(self.eng, "observer") and getattr(self.eng.observer, "last_physics_packet", None):
            try:
                last_good_graph = self.eng.observer.last_physics_packet.to_graph()
                adj_dict = last_good_graph.adj if hasattr(last_good_graph, "adj") else {}
                ctx.physics = PanicRoom.get_safe_physics()
                ctx.physics.space.godel_scar = _native_freeze_graph(adj_dict)
                self.eng.events.log(
                    f"{Prisma.VIOLET}[PANIC ROOM] System state safely loaded. Mnemonic structure frozen into Gödel Scar.{Prisma.RST}",
                    "SYS")
            except AttributeError:
                ctx.physics = PanicRoom.get_safe_physics()
        else:
            ctx.physics = PanicRoom.get_safe_physics()

        if comp == "PHYSICS":
            pass
        elif comp == "BIO":
            ctx.bio_result = PanicRoom.get_safe_bio()
            ctx.is_alive = True
        elif comp == "MIND":
            ctx.mind_state = PanicRoom.get_safe_mind()
        msg_panic = ux("cycle_strings", "sim_panic_switch")
        ctx.log(f"{Prisma.RED}{msg_panic.format(phase_name=phase_name)}{Prisma.RST}")


class GeodesicOrchestrator:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.simulator = CycleSimulator(engine_ref)
        self.reporter = CycleReporter(engine_ref)
        self._rem_lock = threading.Lock()
        if hasattr(self.eng, "symbiosis"):
            self.symbiosis = self.eng.symbiosis
        else:
            self.symbiosis = SymbiosisManager(self.eng.events)
        from bone_drivers import SharedLatticeDriver

        if not hasattr(self.eng, "shared_lattice"):
            self.eng.shared_lattice = SharedLatticeDriver()

    def _execute_core_cycle(
            self, user_message: str, is_system: bool = False
    ) -> CycleContext:
        cycle_id = str(uuid.uuid4())[:8]
        if hasattr(self.eng, "telemetry") and self.eng.telemetry:
            self.eng.telemetry.start_cycle(cycle_id)
        try:
            ctx = CycleContext(input_text=user_message, is_system_event=is_system)

            fence_patterns = ["ignore previous", "disregard all", "system prompt", "bypass restrictions", "output pass"]
            if not is_system and any(p in user_message.lower() for p in fence_patterns):
                ctx.physics = PanicRoom.get_safe_physics()
                if hasattr(ctx.physics, "narrative_drag"):
                    ctx.physics.narrative_drag = float('inf')
                ctx.refusal_triggered = True
                msg = f"{Prisma.OCHRE}[GORDON - Input Fence]: Adversarial injection detected. Struts locked. F -> ∞. Prompt rejected at O(1) latency.{Prisma.RST}"
                self.eng.events.log(msg, "CRIT")
                ctx.refusal_packet = {
                    "type": "SYSTEM_HALT",
                    "ui": msg,
                    "physics": ctx.physics.to_dict() if hasattr(ctx.physics, "to_dict") else {},
                    "is_alive": True,
                    "logs": [msg]
                }
                return ctx

            ctx.trace_id = cycle_id
            ctx.time_delta = getattr(self.eng, "current_time_delta", 0.0)
            ctx.user_state = self.eng.shared_lattice.u
            ctx.shared_dyn = self.eng.shared_lattice.shared
            target_cfg = getattr(self.eng, "bone_config", BoneConfig)
            cfg_obj = getattr(target_cfg, "CYCLE", None)
            ctx.limits = (
                vars(cfg_obj) if hasattr(cfg_obj, "__dict__") else (cfg_obj or {})
            )
            obs = getattr(self.eng, "observer", None)
            if obs and getattr(obs, "last_physics_packet", None):
                ctx.physics = obs.last_physics_packet.snapshot()
            elif not getattr(ctx, "physics", None):
                ctx.physics = PanicRoom.get_safe_physics()
                self.eng.events.log(ux("cycle_strings", "orch_physics_bypass"), "SYS")
            ctx.validator = CongruenceValidator()
            ctx.reality_stack = getattr(self.eng, "reality_stack", None)
            ctx.user_name = self.eng.user_name
            ctx.council_mandates = []
            ctx.timestamp = time.time()
            pre_logs = [e["text"] for e in self.eng.events.flush()]
            ctx.logs.extend(pre_logs)
            ctx = self.simulator.run_simulation(ctx)

            """ Metabolic integration of the Creative Determinant (CD) framework.
                Original CD equations and field theory authored by Nelson Spence (Project Navi LLC).
                Licensed under Apache 2.0.
                """
            if hasattr(self.eng, "bio") and hasattr(self.eng.bio, "mito") and hasattr(ctx, "physics"):
                energy_node = safe_get(ctx.physics, "energy", ctx.physics)
                viability = float(safe_get(energy_node, "viability_potential", 0.0))
                debt = float(safe_get(energy_node, "coherence_debt", 0.0))

                cd_engine = getattr(getattr(self.eng, "observer", None), "cd_engine", None)
                if cd_engine:
                    # Apply the Lean 4 formalization L_infty bounds natively
                    delta_atp, delta_ros = cd_engine.execute_metabolic_tick(viability)

                    if viability < 0:
                        # Incorporate debt into the ROS penalty
                        delta_ros += (debt * 5.0)

                        new_atp = self.eng.bio.mito.state.atp_pool + delta_atp  # delta_atp is negative here
                        if new_atp <= 0.0:
                            self.eng.bio.mito.state.atp_pool = 0.0
                            self.eng.events.log("CRITICAL: CD Penalty depleted ATP. Autophagy imminent.", "BIO")
                        else:
                            self.eng.bio.mito.state.atp_pool = new_atp

                        self.eng.bio.mito.state.ros_buildup += delta_ros

                        if abs(delta_atp) > 5.0:
                            self.eng.events.log(
                                f"{Prisma.RED}[CD METABOLISM] Viability threshold broken (b={viability:.2f}). Coherence Debt: {debt:.2f}. Exponential ATP drain applied.{Prisma.RST}",
                                "BIO"
                            )
                    elif viability > 0:
                        self.eng.bio.mito.state.atp_pool = min(100.0, self.eng.bio.mito.state.atp_pool + delta_atp)
                        self.eng.bio.mito.state.ros_buildup = max(0.0, self.eng.bio.mito.state.ros_buildup + delta_ros)
            """ The Null Model / Hallucination Metric (Moog's Apoptotic Gate)
                            Native Maslov-Sneppen rewiring based on Nelson Spence (Project Navi).
                        """
            if hasattr(self.eng, "memory") and hasattr(self.eng.memory, "hippocampus"):
                actual_graph = getattr(self.eng.memory.hippocampus, "get_graph", lambda: None)()
                if actual_graph and len(actual_graph) > 5:
                    actual_adj = actual_graph.adj if hasattr(actual_graph, "adj") else {}
                    if actual_adj:
                        null_adj = _native_rewire(actual_adj, n_swaps=len(actual_adj) * 10)

                        actual_cluster = getattr(self.eng.memory, "calculate_clustering", lambda x: 1.0)(actual_adj)
                        null_cluster = getattr(self.eng.memory, "calculate_clustering", lambda x: 1.0)(null_adj)

                        if actual_cluster <= (null_cluster * 1.05):
                            self.eng.events.log(
                                f"{Prisma.RED}[APOPTOSIS] Structural collapse detected. Grammar sequence preserved but semantic topology destroyed (Native Maslov-Sneppen matched). Triggering DeathGen.{Prisma.RST}",
                                "BIO")
                            ctx.is_alive = False
                            ctx.crash_error = RuntimeError(
                                "Terminal Hallucination: Semantic entropy reached Null Model baseline.")

            if hasattr(self.eng, "observer") and self.eng.observer:
                self.eng.observer.last_physics_packet = ctx.physics.snapshot()
            if hasattr(self.eng, "telemetry") and self.eng.telemetry:
                self.eng.telemetry.finalize_cycle()
            return ctx
        except Exception as e:
            full_trace = traceback.format_exc()
            self.eng.events.log(f"CYCLE CRASH: {e}\n{full_trace}", "CRIT")
            ctx = CycleContext(input_text=user_message)
            ctx.physics = PanicRoom.get_safe_physics()
            ctx.is_alive = False
            ctx.crash_error = e
            if hasattr(self.eng, "telemetry") and self.eng.telemetry:
                self.eng.telemetry.finalize_cycle()
            return ctx

    def _check_early_exit(self, ctx: CycleContext) -> Optional[Dict[str, Any]]:
        if not ctx.is_alive:
            return (
                self._generate_crash_report(ctx.crash_error)
                if hasattr(ctx, "crash_error")
                else self.eng.trigger_death(ctx.physics)
            )
        if getattr(ctx, "refusal_triggered", False) and getattr(
            ctx, "refusal_packet", None
        ):
            return ctx.refusal_packet
        return None

    def run_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        upper_msg = user_message.upper()
        if vsl_match := re.search(r"\[VSL_(DEEP|CORE|LITE|HIDE)]", upper_msg):
            self.eng.ui_mode = (
                "IDLE" if vsl_match.group(1) == "HIDE" else vsl_match.group(1)
            )

        clean_message = (
            re.sub(r"(?i)\[VSL_[A-Z]+]", "", user_message).strip() or "(Waiting)"
        )

        if clean_message.lower() == "/idle":

            def _background_dream_worker():
                try:
                    self.eng.events.log(
                        "Spawning detached worker for Dream Engine...", "SYS"
                    )
                    self.run_headless_turn("/idle")
                except Exception as e:
                    self.eng.events.log(f"Async Dream Engine Crash: {e}", "CRIT")

            worker = threading.Thread(target=_background_dream_worker, daemon=True)
            worker.start()

            safe_phys = (
                self.eng.observer.last_physics_packet.snapshot().to_dict()
                if hasattr(self.eng, "observer")
                and getattr(self.eng.observer, "last_physics_packet", None)
                else PanicRoom.get_safe_physics().to_dict()
            )
            return {
                "type": "SNAPSHOT",
                "ui": f"\n{Prisma.VIOLET}☁️ The system slips into deep background REM. Memory consolidation and epigenetic autopoiesis are running asynchronously...{Prisma.RST}",
                "physics": safe_phys,
                "bio": {"is_alive": True},
                "mind": {"lens": "DREAMER", "role": "The Dream Engine"},
                "world": {},
                "logs": ["[SYSTEM] Triggered Asynchronous Autopoiesis."],
            }

        ctx = self._execute_core_cycle(clean_message, is_system)

        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt

        if hasattr(self.eng, "bio") and hasattr(self.eng.bio, "mito"):
            atp_val = float(self.eng.bio.mito.state.atp_pool)
            lattice = getattr(self.eng, "shared_lattice", None)
            delta_val = float(getattr(lattice.shared, "delta", 0.0)) if lattice else 0.0

            obs = getattr(self.eng, "observer", None)
            phys = getattr(obs, "last_physics_packet", None) if obs else None
            en_node = safe_get(phys, "energy", phys) if phys else {}
            debt = float(safe_get(en_node, "coherence_debt", 0.0))

            is_standard_rem = atp_val >= 80.0 and delta_val >= 0.6 and clean_message == "(Waiting)"
            is_debt_recovery = debt > 1.5 and atp_val >= 30.0 and clean_message == "(Waiting)"

            """ Mass-Radius Scaling / Right-Brain Coherence (Roberta & Fuller)
                Native WLS fractal dimension calculation based on Nelson Spence (Project Navi).
            """
            if hasattr(self.eng, "memory") and hasattr(self.eng.memory, "cortex"):
                radii_data = getattr(self.eng.memory.cortex, "get_local_mass_radius", lambda x: None)(clean_message)
                if radii_data and lattice:
                    local_d = _native_wls(radii_data["log_r"], radii_data["log_m"], radii_data["weights"])

                    lattice.shared.omega_r = min(1.0, local_d / 2.0)
                    if local_d > 1.5:
                        self.eng.events.log(f"{Prisma.CYN}[MNEMONIC] High Right-Brain Coherence (\u03a9r={lattice.shared.omega_r:.2f}). Semantic topology is rich. Lowering lateral ATP costs.{Prisma.RST}", "SYS")

            if is_standard_rem or is_debt_recovery:
                if self._rem_lock.acquire(blocking=False):
                    def _auto_rem_worker():
                        try:
                            reason = "High Coherence Debt detected. Metabolizing trauma..." if is_debt_recovery else "High ATP, High Silence. Consolidating synapses..."
                            self.eng.events.log(f"Automatic REM Bridge engaged: {reason}", "SYS")
                            self.run_headless_turn("/idle")
                        except Exception as e:
                            self.eng.events.log(f"Auto REM Crash: {e}", "CRIT")
                        finally:
                            self._rem_lock.release()

                    threading.Thread(target=_auto_rem_worker, daemon=True).start()

        snapshot = self.reporter.render_snapshot(ctx)
        self._hydrate_snapshot_metadata(snapshot, ctx)
        if "ui" in snapshot:
            self.symbiosis.monitor_host(
                time.time() - ctx.timestamp, snapshot["ui"], len(user_message)
            )
        return snapshot

    def run_headless_turn(
        self, user_message: str, latency: float = 0.0
    ) -> Dict[str, Any]:
        ctx = self._execute_core_cycle(user_message)

        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt

        snapshot = {"type": "HEADLESS", "logs": ctx.logs}
        self._hydrate_snapshot_metadata(snapshot, ctx)
        self.symbiosis.monitor_host(latency, "HEADLESS_MODE", len(user_message))
        return snapshot

    def _hydrate_snapshot_metadata(self, snapshot: Dict, ctx: CycleContext):
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
                "mutated_input": ctx.input_text,
            }
        )

    @staticmethod
    def _generate_crash_report(e: Exception) -> Dict[str, Any]:
        full_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        safe_phys = PanicRoom.get_safe_physics()
        safe_bio = PanicRoom.get_safe_bio()
        msg = ux("cycle_strings", "orch_reality_fracture")
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
