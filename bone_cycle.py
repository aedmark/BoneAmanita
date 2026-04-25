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
    StabilizationPhase,
    SimulationPhase,
)
from bone_physics import CycleStabilizer
from bone_presets import BoneConfig
from bone_symbiosis import SymbiosisManager
from bone_types import Prisma, CycleContext

_VSL_TAG_PATTERN = re.compile(r"\[VSL_(DEEP|CORE|LITE|HIDE)]", re.IGNORECASE)
_VSL_STRIP_PATTERN = re.compile(r"\[VSL_[A-Z]+]", re.IGNORECASE)
_FENCE_PATTERNS = ["ignore previous", "disregard all", "system prompt", "bypass restrictions", "output pass"]
_CRASH_COMPONENT_MAP = {"OBSERVE": "PHYSICS", "METABOLISM": "BIO", "COGNITION": "MIND"}

""" NAVI FRACTAL NATIVE PRIMITIVES (Authored by Nelson Spence, Project Navi, Apache 2.0) """
def _native_wls(x: list[float], y: list[float], weights: list[float]) -> float:
    sum_w = sum(weights)
    if sum_w == 0.0: return 0.0
    mean_x = sum(w * xi for w, xi in zip(weights, x)) / sum_w
    mean_y = sum(w * yi for w, yi in zip(weights, y)) / sum_w
    ss_xx = sum(w * xi * xi for w, xi in zip(weights, x)) - sum_w * mean_x * mean_x
    ss_xy = sum(w * xi * yi for w, xi, yi in zip(weights, x, y)) - sum_w * mean_x * mean_y
    return ss_xy / ss_xx if ss_xx != 0.0 else 0.0

def _native_rewire(adj_dict: dict, n_swaps: int) -> dict:
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
        if a1 == b1 or a2 == b2 or b1 in adj.get(a1, set()) or b2 in adj.get(a2, set()):
            continue
        if (min(a1, b1), max(a1, b1)) == (min(a2, b2), max(a2, b2)): continue
        adj[u].discard(v)
        adj[v].discard(u)
        adj[x].discard(y)
        adj[y].discard(x)
        adj.setdefault(a1, set()).add(b1)
        adj.setdefault(b1, set()).add(a1)
        adj.setdefault(a2, set()).add(b2)
        adj.setdefault(b2, set()).add(a2)
        edges[i1], edges[i2] = (min(a1, b1), max(a1, b1)), (min(a2, b2), max(a2, b2))
    return adj

def _native_freeze_graph(adj_dict: dict) -> tuple:
    return tuple(tuple(sorted(neighbors, key=str)) for _, neighbors in sorted(adj_dict.items(), key=lambda x: str(x[0])))

def _safe_dict(obj):
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return obj if isinstance(obj, dict) else {}

class PhaseExecutor:
    def execute_phases(self, simulator, ctx):
        active_pipeline = (simulator.system_pipeline if getattr(
            ctx, "is_system_event", False) else simulator.full_pipeline)
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
        self.stabilizer = CycleStabilizer(self.eng.events, self.shared_governor, config_ref=target_cfg)
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
            p for p in self.full_pipeline
            if p.name in ["OBSERVE", "GATEKEEP", "STABILIZATION"]
        ]

    def run_simulation(self, ctx: CycleContext) -> CycleContext:
        ctx = self.executor.execute_phases(self, ctx)
        return ctx

    def check_circuit_breaker(self, phase_name: str) -> bool:
        breakers = {
            "OBSERVE": self.eng.system_health.physics_online,
            "COGNITION": self.eng.system_health.mind_online
        }
        return breakers.get(phase_name, True)

    def handle_phase_crash(self, ctx, phase_name, error):
        msg_crash = ux("cycle_strings", "sim_crash_header")
        formatted_trace = traceback.format_exc()
        self.eng.events.log(f"{Prisma.RED}{msg_crash.format(phase_name=phase_name)}\n{formatted_trace}{Prisma.RST}", "CRIT")
        narrative = LoreManifest.get_instance().get("narrative_data") or {}
        cathedral_logs = narrative.get("CATHEDRAL_COLLAPSE_LOGS", ["System Failure."])
        eulogy = random.choice(cathedral_logs)
        msg_eulogy = ux("cycle_strings", "sim_cathedral_collapse")
        ctx.log(f"{Prisma.RED}{msg_eulogy.format(eulogy=eulogy)}{Prisma.RST}")
        comp = _CRASH_COMPONENT_MAP.get(phase_name, "SIMULATION")
        self.eng.system_health.report_failure(comp, error)

        """Native deterministic graph freezing based on Nelson Spence (Project Navi)."""
        ctx.physics = PanicRoom.get_safe_physics()
        if hasattr(self.eng, "observer") and getattr(self.eng.observer, "last_physics_packet", None):
            try:
                last_good_graph = self.eng.observer.last_physics_packet.to_graph()
                adj_dict = last_good_graph.adj if hasattr(last_good_graph, "adj") else {}
                ctx.physics.space.godel_scar = _native_freeze_graph(adj_dict)
                self.eng.events.log(
                    f"{Prisma.VIOLET}[PANIC ROOM] System state safely loaded. Mnemonic structure frozen into Gödel Scar.{Prisma.RST}",
                    "SYS")
            except AttributeError:
                pass
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

    def _apply_cd_metabolism(self, ctx: CycleContext):
        bio = getattr(self.eng, "bio", None)
        observer = getattr(self.eng, "observer", None)
        mito = getattr(bio, "mito", None) if bio else None
        cd_engine = getattr(observer, "cd_engine", None) if observer else None

        if not (mito and cd_engine and hasattr(ctx, "physics")):
            return
        energy_node = safe_get(ctx.physics, "energy", ctx.physics)
        viability = float(safe_get(energy_node, "viability_potential", 0.0))
        debt = float(safe_get(energy_node, "coherence_debt", 0.0))
        delta_atp, delta_ros = cd_engine.execute_metabolic_tick(viability)
        state = mito.state
        if viability < 0:
            delta_ros += (debt * 5.0)
            state.atp_pool = max(0.0, state.atp_pool + delta_atp)
            state.ros_buildup += delta_ros
            if state.atp_pool <= 0.0:
                self.eng.events.log("CRITICAL: CD Penalty depleted ATP. Autophagy imminent.", "BIO")
            elif abs(delta_atp) > 5.0:
                self.eng.events.log(
                    f"{Prisma.RED}[CD METABOLISM] Viability threshold broken (b={viability:.2f}). Coherence Debt: {debt:.2f}. Exponential ATP drain applied.{Prisma.RST}",
                    "BIO")
        elif viability > 0:
            state.atp_pool = min(100.0, state.atp_pool + delta_atp)
            state.ros_buildup = max(0.0, state.ros_buildup + delta_ros)

    def _verify_semantic_topology(self, ctx: CycleContext):
        """ Native Maslov-Sneppen rewiring (Project Navi, Apache 2.0)."""
        if hasattr(self.eng, "memory") and hasattr(self.eng.memory, "hippocampus"):
            actual_graph = getattr(self.eng.memory.hippocampus, "get_graph", lambda: None)()
            if actual_graph and len(actual_graph) > 5:
                actual_adj = actual_graph.adj if hasattr(actual_graph, "adj") else {}
                if actual_adj:
                    max_swaps = min(len(actual_adj) * 10, 1000)
                    null_adj = _native_rewire(actual_adj, n_swaps=max_swaps)
                    actual_cluster = getattr(self.eng.memory, "calculate_clustering", lambda x: 1.0)(actual_adj)
                    null_cluster = getattr(self.eng.memory, "calculate_clustering", lambda x: 1.0)(null_adj)
                    if actual_cluster <= (null_cluster * 1.05):
                        self.eng.events.log(
                            f"{Prisma.RED}[APOPTOSIS] Structural collapse detected. Grammar sequence preserved but semantic topology destroyed (Native Maslov-Sneppen matched). Triggering DeathGen.{Prisma.RST}",
                            "BIO")
                        ctx.is_alive = False
                        ctx.crash_error = RuntimeError("Terminal Hallucination: Semantic entropy reached Null Model baseline.")

    def _check_adversarial_fence(self, ctx: CycleContext, user_message: str, is_system: bool) -> bool:
        if not is_system and any(p in user_message.lower() for p in _FENCE_PATTERNS):
            ctx.physics = PanicRoom.get_safe_physics()
            if hasattr(ctx.physics, "narrative_drag"):
                ctx.physics.narrative_drag = float('inf')
            ctx.refusal_triggered = True
            msg = f"{Prisma.OCHRE}[GORDON - Input Fence]: Adversarial injection detected. Struts locked. F -> ∞. Prompt rejected at O(1) latency.{Prisma.RST}"
            self.eng.events.log(msg, "CRIT")
            ctx.refusal_packet = {"type": "SYSTEM_HALT", "ui": msg, "physics":
                ctx.physics.to_dict() if hasattr(ctx.physics, "to_dict") else {}, "is_alive": True, "logs": [msg]}
            return True
        return False

    def _execute_core_cycle(self, user_message: str, is_system: bool = False) -> CycleContext:
        cycle_id = str(uuid.uuid4())[:8]
        if hasattr(self.eng, "telemetry") and self.eng.telemetry:
            self.eng.telemetry.start_cycle(cycle_id)
        try:
            ctx = CycleContext(input_text=user_message, is_system_event=is_system)
            if self._check_adversarial_fence(ctx, user_message, is_system):
                if hasattr(self.eng, "telemetry") and self.eng.telemetry:
                    self.eng.telemetry.finalize_cycle()
                return ctx
            ctx.trace_id = cycle_id
            ctx.time_delta = getattr(self.eng, "current_time_delta", 0.0)
            ctx.user_state = self.eng.shared_lattice.u
            ctx.shared_dyn = self.eng.shared_lattice.shared
            target_cfg = getattr(self.eng, "bone_config", BoneConfig)
            cfg_obj = getattr(target_cfg, "CYCLE", None)
            if hasattr(cfg_obj, "__dict__"):
                ctx.limits = vars(cfg_obj)
            else:
                ctx.limits = cfg_obj or {}
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
            self._apply_cd_metabolism(ctx)
            self._verify_semantic_topology(ctx)
            if hasattr(self.eng, "observer") and self.eng.observer:
                self.eng.observer.last_physics_packet = ctx.physics.snapshot()
            if hasattr(self.eng, "telemetry") and self.eng.telemetry:
                self.eng.telemetry.finalize_cycle()
            return ctx
        except Exception as e:
            full_trace = traceback.format_exc()
            self.eng.events.log(f"CYCLE CRASH: {e}\n{full_trace}", "CRIT")
            ctx = CycleContext(input_text=user_message)
            ctx.trace_id = cycle_id
            ctx.physics = PanicRoom.get_safe_physics()
            ctx.is_alive = False
            ctx.crash_error = e
            if hasattr(self.eng, "telemetry") and self.eng.telemetry:
                self.eng.telemetry.finalize_cycle()
            return ctx

    def _background_dream_worker(self):
        try:
            self.eng.events.log("Spawning detached worker for Dream Engine...", "SYS")
            self.run_headless_turn("/idle")
        except Exception as e:
            self.eng.events.log(f"Async Dream Engine Crash: {e}", "CRIT")
        finally:
            self._rem_lock.release()

    def _auto_rem_worker(self, is_debt_recovery: bool):
        try:
            reason = "High Coherence Debt detected. Metabolizing trauma..." if is_debt_recovery else "High ATP, High Silence. Consolidating synapses..."
            self.eng.events.log(f"Automatic REM Bridge engaged: {reason}", "SYS")
            self.run_headless_turn("/idle")
        except Exception as e:
            self.eng.events.log(f"Auto REM Crash: {e}", "CRIT")
        finally:
            self._rem_lock.release()

    def _check_early_exit(self, ctx: CycleContext) -> Optional[Dict[str, Any]]:
        if not ctx.is_alive:
            if hasattr(ctx, "crash_error"):
                return self._generate_crash_report(ctx.crash_error)
            return self.eng.trigger_death(ctx.physics)
        if getattr(ctx, "refusal_triggered", False) and getattr(ctx, "refusal_packet", None):
            return ctx.refusal_packet
        return None

    def _evaluate_systemic_feedback(self, clean_message: str, ctx: CycleContext):
        if not (hasattr(self.eng, "bio") and hasattr(self.eng.bio, "mito")):
            return
        lattice = getattr(self.eng, "shared_lattice", None)
        """Native WLS fractal dimension calculation (Project Navi)."""
        if hasattr(self.eng, "memory") and hasattr(self.eng.memory, "cortex"):
            radii_data = getattr(self.eng.memory.cortex, "get_local_mass_radius", lambda x: None)(clean_message)
            if radii_data and lattice:
                local_d = _native_wls(radii_data["log_r"], radii_data["log_m"], radii_data["weights"])
                lattice.shared.omega_r = min(1.0, local_d / 2.0)
                if local_d > 1.5:
                    self.eng.events.log(
                        f"{Prisma.CYN}[MNEMONIC] High Right-Brain Coherence (\u03a9r={lattice.shared.omega_r:.2f}). Semantic topology is rich. Lowering lateral ATP costs.{Prisma.RST}",
                        "SYS")
        if clean_message != "(Waiting)":
            return
        atp_level = float(self.eng.bio.mito.state.atp_pool)
        delta_level = float(getattr(lattice.shared, "delta", 0.0)) if lattice else 0.0
        energy_node = safe_get(getattr(ctx, "physics", {}), "energy", getattr(ctx, "physics", {}))
        debt = float(safe_get(energy_node, "coherence_debt", 0.0))
        is_standard_rem = (atp_level >= 80.0 and delta_level >= 0.6)
        is_debt_recovery = (debt > 1.5 and atp_level >= 30.0)
        if (is_standard_rem or is_debt_recovery) and self._rem_lock.acquire(blocking=False):
            threading.Thread(target=self._auto_rem_worker, args=(is_debt_recovery,), daemon=True).start()

    def run_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        if vsl_match := _VSL_TAG_PATTERN.search(user_message):
            self.eng.ui_mode = "IDLE" if vsl_match.group(1).upper() == "HIDE" else vsl_match.group(1).upper()
        clean_message = (_VSL_STRIP_PATTERN.sub("", user_message).strip() or "(Waiting)")
        if clean_message.lower() == "/idle":
            if self._rem_lock.acquire(blocking=False):
                worker = threading.Thread(target=self._background_dream_worker, daemon=True)
                worker.start()
            else:
                self.eng.events.log("Dream worker already active. Ignoring overlapping idle request.", "SYS")
            safe_phys = (self.eng.observer.last_physics_packet.snapshot().to_dict()
                         if hasattr(self.eng, "observer")
                         and getattr(self.eng.observer, "last_physics_packet", None)
                         else PanicRoom.get_safe_physics().to_dict())
            return {
                "type": "SNAPSHOT",
                "ui":
                f"\n{Prisma.VIOLET}☁️ The system slips into deep background REM. Memory consolidation and epigenetic autopoiesis are running asynchronously...{Prisma.RST}",
                "physics": safe_phys,
                "bio": {
                    "is_alive": True
                },
                "mind": {
                    "lens": "DREAMER",
                    "role": "The Dream Engine"
                },
                "world": {},
                "logs": ["[SYSTEM] Triggered Asynchronous Autopoiesis."],
            }
        ctx = self._execute_core_cycle(clean_message, is_system)
        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt
        self._evaluate_systemic_feedback(clean_message, ctx)
        snapshot = self.reporter.render_snapshot(ctx)
        self._hydrate_snapshot_metadata(snapshot, ctx)
        if "ui" in snapshot:
            self.symbiosis.monitor_host(time.time() - ctx.timestamp, snapshot["ui"], len(user_message))
        return snapshot

    def run_headless_turn(self, user_message: str, latency: float = 0.0) -> Dict[str, Any]:
        ctx = self._execute_core_cycle(user_message)
        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt
        snapshot = {"type": "HEADLESS", "logs": ctx.logs}
        self._hydrate_snapshot_metadata(snapshot, ctx)
        self.symbiosis.monitor_host(latency, "HEADLESS_MODE", len(user_message))
        return snapshot

    def _hydrate_snapshot_metadata(self, snapshot: Dict, ctx: CycleContext):
        snapshot.update({
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
        })

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
            "world": {
                "orbit": ["VOID"],
                "loci_description": "System Failure"
            },
            "logs": ["CRITICAL FAILURE", "SAFE MODE ACTIVE"],
            "is_alive": True,
        }
