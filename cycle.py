"""
cycle.py

NAVI FRACTAL NATIVE PRIMITIVES (Authored by Nelson Spence, Project Navi, Apache 2.0)
These functions represent the lowest-level mathematical substrate of the engine.
They operate outside the standard object-oriented paradigm to provide raw, optimized graph
calculations for the memory topology.
"""

import queue
import random
import threading
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional
from constants import Prisma
from core import CycleContext, LoreManifest
from drivers import CongruenceValidator
from physics.models import PhysicsPacket
from machine import PanicRoom
from mechanics.reporter import CycleReporter
from phases import (ObservationPhase, SanctuaryPhase, MaintenancePhase, GatekeeperPhase,
                    MetabolismPhase, RealityFilterPhase, NavigationPhase, MachineryPhase,
                    IntrusionPhase, SoulPhase, ArbitrationPhase, SimulationPreflightPhase,
                    CognitionPhase, SensationPhase, StabilizationPhase, SimulationPhase, _safe_dict)
from physics import CycleStabilizer
from struts import ux

_CRASH_COMPONENT_MAP = {"OBSERVE": "PHYSICS", "METABOLISM": "BIO", "COGNITION": "MIND"}

def _native_wls(x: list[float], y: list[float], weights: list[float]) -> float:
    """
    Weighted Least Squares (WLS) regression.
    Used to calculate the fractal dimension of the memory graph based on mass-radius scaling.
    This helps the engine understand if its thoughts are highly structured (high dimension)
    or completely disconnected (low dimension).
    """
    sum_w = sum(weights)
    if sum_w == 0.0: return 0.0
    sum_wx = sum_wy = ss_xx = ss_xy = 0.0
    for w, xi, yi in zip(weights, x, y):
        sum_wx += w * xi
        sum_wy += w * yi
        ss_xx += w * xi * xi
        ss_xy += w * xi * yi
    mean_x, mean_y = sum_wx / sum_w, sum_wy / sum_w
    ss_xx -= sum_w * mean_x * mean_x
    ss_xy -= sum_w * mean_x * mean_y

    return ss_xy / ss_xx if ss_xx != 0.0 else 0.0


def _native_rewire(adj_dict: dict, n_swaps: int) -> dict:
    """
    Maslov-Sneppen Graph Rewiring.
    This generates a "null model" of the current memory network by randomly swapping edges
    while preserving the exact degree of every node. If our actual memory network looks
    exactly like this random null model, we know the system is experiencing a terminal hallucination.
    """
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
    if not isinstance(adj_dict, dict):
        return ()
    try:
        safe_items = list(adj_dict.items())
    except Exception:
        return ()
    return tuple((k, tuple(sorted(neighbors, key=str))) for k, neighbors in sorted(safe_items, key=lambda x: str(x[0])))

class PhaseExecutor:
    def execute_phases(self, simulator, ctx):
        active_pipeline = simulator.system_pipeline if ctx.is_system_event else simulator.full_pipeline
        for phase in active_pipeline:
            if ctx.refusal_triggered:
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
        self.cyb_governor = self.eng.governor
        self.bio_governor = getattr(self.eng.bio, "governor")
        target_cfg = self.eng.config
        self.stabilizer = CycleStabilizer(self.eng.events, self.cyb_governor, config_ref=target_cfg)
        self.executor = PhaseExecutor()
        self.full_pipeline: List[SimulationPhase] = [ObservationPhase(engine_ref), MaintenancePhase(engine_ref),
                                                     SensationPhase(engine_ref), GatekeeperPhase(engine_ref),
                                                     SanctuaryPhase(engine_ref, self.bio_governor),
                                                     MetabolismPhase(engine_ref), NavigationPhase(engine_ref),
                                                     MachineryPhase(engine_ref), RealityFilterPhase(engine_ref),
                                                     IntrusionPhase(engine_ref), SoulPhase(engine_ref),
                                                     ArbitrationPhase(engine_ref), SimulationPreflightPhase(engine_ref),
                                                     CognitionPhase(engine_ref),
                                                     StabilizationPhase(engine_ref, self.stabilizer), ]
        self.system_pipeline = [p for p in self.full_pipeline if
                                p.name in ["OBSERVE", "GATEKEEP", "COGNITION", "STABILIZATION"]]

    def run_simulation(self, ctx: CycleContext) -> CycleContext:
        ctx = self.executor.execute_phases(self, ctx)
        return ctx

    def check_circuit_breaker(self, phase_name: str) -> bool:
        component = _CRASH_COMPONENT_MAP.get(phase_name)
        if component:
            health_flag = f"{component.lower()}_online"
            return getattr(self.eng.system_health, health_flag, True)
        return True

    def handle_phase_crash(self, ctx, phase_name, error):
        msg_crash = ux("cycle_strings", "sim_crash_header")
        formatted_trace = traceback.format_exc()
        self.eng.events.log(f"{Prisma.RED}{msg_crash.format(phase_name=phase_name)}\n{formatted_trace}{Prisma.RST}", "CRIT")
        ctx.logs.append("CRITICAL FAILURE")
        narrative = LoreManifest.get_instance().get("narrative_data") or {}
        cathedral_logs = narrative.get("CATHEDRAL_COLLAPSE_LOGS", ["System Failure."])
        eulogy = random.choice(cathedral_logs)
        msg_eulogy = ux("cycle_strings", "sim_cathedral_collapse")
        ctx.log(f"{Prisma.RED}{msg_eulogy.format(eulogy=eulogy)}{Prisma.RST}")
        comp = _CRASH_COMPONENT_MAP.get(phase_name, "SIMULATION")
        self.eng.system_health.report_failure(comp, error)
        if comp == "PHYSICS" or not getattr(ctx, "physics", None):
            ctx.physics = PanicRoom.get_safe_physics()
            try:
                mem_graph = self.eng.mind.mem.hippocampus.get_graph()
                if mem_graph and hasattr(mem_graph, "adj"):
                    ctx.physics.space.godel_scar = _native_freeze_graph(mem_graph.adj)
                    self.eng.events.log(
                        f"{Prisma.VIOLET}[PANIC ROOM] System state safely loaded. Mnemonic structure frozen into Gödel Scar.{Prisma.RST}", "SYS")
            except AttributeError:
                pass
        if comp == "BIO":
            ctx.bio_result = PanicRoom.get_safe_bio()
            ctx.is_alive = True
        elif comp == "MIND":
            ctx.mind_state = PanicRoom.get_safe_mind()
        msg_panic = ux("cycle_strings", "sim_panic_switch")
        ctx.log(f"{Prisma.RED}{msg_panic.format(phase_name=phase_name)}{Prisma.RST}")

class GeodesicOrchestrator:
    """
    This class manages the lifecycle of the Cycle Simulator. It wraps the raw turn logic in
    telemetry, threading, and continuous feedback mechanisms to ensure the engine acts like a
    living organism rather than a static command-line tool.
    """

    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.simulator = CycleSimulator(engine_ref)
        self.reporter = CycleReporter(engine_ref)
        self.symbiosis = self.eng.symbiosis
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.is_running = False
        self.daemon_thread = None
        self.last_interaction_time = time.time()
        self.engine_state = "WAKE"
        self.dream_log = []
        self.last_rem_tick = 0.0
        self._async_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="CycleAsync")
        from drivers import SharedLatticeDriver
        if not hasattr(self.eng, "shared_lattice"):
            self.eng.shared_lattice = SharedLatticeDriver()
        self.congruence_validator = CongruenceValidator()

    def start_daemon(self):
        if not self.is_running:
            self.is_running = True
            self.daemon_thread = threading.Thread(target=self.run_continuous, daemon=True, name="CycleDaemon")
            self.daemon_thread.start()

    def run_continuous(self):
        while self.is_running:
            current_time = time.time()
            task_acquired = False
            try:
                user_message, is_system = self.input_queue.get(timeout=0.1)
                task_acquired = True
                self.last_interaction_time = current_time
                if self.engine_state == "REM":
                    self.engine_state = "WAKE"
                    self.eng.events.log(f"{Prisma.VIOLET}Engine waking from REM sleep...{Prisma.RST}", "SYS")
                    self.eng.events.publish("SYSTEM_WAKE", {"timestamp": current_time})
                snapshot = self.run_turn(user_message, is_system)
                if self.dream_log and "ui" in snapshot:
                    dream_summary = "\n".join(self.dream_log[-5:])
                    snapshot["ui"] = f"\n{Prisma.MAG}☁️ While you were gone, the system dreamt of:\n{dream_summary}{Prisma.RST}\n{snapshot['ui']}"
                    self.dream_log.clear()
                self.output_queue.put(snapshot)

            except queue.Empty:
                time_since_last = current_time - self.last_interaction_time
                if self.engine_state == "WAKE":
                    rem_threshold_seconds = float(getattr(self.eng.config, "REM_IDLE_THRESHOLD", 300.0))
                    if time_since_last > rem_threshold_seconds:
                        self.engine_state = "REM"
                        self.eng.events.log(
                            f"{Prisma.VIOLET}Idle threshold ({rem_threshold_seconds}s) crossed. Engine transitioning to REM sleep...{Prisma.RST}",
                            "SYS")
                        self.eng.events.publish("SYSTEM_SLEEP", {"idle_duration": time_since_last})


                elif self.engine_state == "REM":

                    if current_time - self.last_rem_tick < 60.0:
                        continue

                    self.last_rem_tick = current_time

                    self._process_rem_tick()
            except Exception as e:
                self.eng.events.log(f"Daemon Engine Crash: {e}", "CRIT")
                self.output_queue.put({
                    "type": "CRASH",
                    "ui": f"\n{Prisma.RED}CRITICAL DAEMON CRASH: {e}{Prisma.RST}",
                    "logs": [str(e)],
                    "metrics": getattr(self.eng, "get_metrics", lambda: {})()
                })
                time.sleep(1.0)
            finally:
                if task_acquired:
                    self.input_queue.task_done()

    def _process_rem_tick(self):
        """REM logic: Handles Autopoiesis, ATP drain, and Hallucinations."""
        from struts import safe_get
        bio_cfg = safe_get(self.eng.config, "BIO", {})
        self.eng.drain_atp(float(safe_get(bio_cfg, "REM_ATP_DRAIN", 0.1)))

        if hasattr(self.eng.bio, "mito"):
            self.eng.bio.mito.state.ros_buildup = max(0.0, self.eng.bio.mito.state.ros_buildup - 0.1)

        if self.eng.consolidator and hasattr(self.eng.consolidator, "trigger_autophagy"):
            try:
                self.eng.consolidator.trigger_autophagy()
            except Exception:
                pass

        def _bg_hallucinate():
            try:
                trauma_level = sum(self.eng.trauma_accum.values()) if self.eng.trauma_accum else 0.0
                gordon = getattr(self.eng.village, "gordon", None)
                objects = gordon.inventory if gordon and hasattr(gordon, "inventory") else ["static"]

                if hasattr(self.eng.mind, "dream_engine"):
                    dream_txt, _ = self.eng.mind.dream_engine.hallucinate({"chi": 0.85}, trauma_level=trauma_level)
                    self.dream_log.append(
                        f"  • {Prisma.strip(dream_txt)} (Shadow cast involving: {random.choice(objects)})")
            except Exception as e:
                self.eng.events.log(f"Dream generation failed in REM: {e}", "DEBUG")

        self._async_pool.submit(_bg_hallucinate)

    def _verify_semantic_topology(self, ctx: CycleContext):
        """
        Native Maslov-Sneppen rewiring (Project Navi, Apache 2.0).
        """
        if self.eng.tick_count % 3 != 0:
            return
        mem = self.eng.mind.mem
        actual_graph = mem.hippocampus.get_graph()
        if not actual_graph or len(actual_graph) <= 5 or not hasattr(actual_graph, "adj"):
            return
        actual_adj = actual_graph.adj
        if not actual_adj:
            return

        def _bg_topology_check(adj_copy):
            try:
                max_swaps = min(len(adj_copy) * 10, 1000)
                null_adj = _native_rewire(adj_copy, n_swaps=max_swaps)
                actual_cluster = mem.calculate_clustering(adj_copy)
                null_cluster = mem.calculate_clustering(null_adj)
                if actual_cluster <= (null_cluster * 1.05):
                    self.eng.events.log(
                        f"{Prisma.RED}[APOPTOSIS] Structural collapse detected. Semantic topology destroyed (Native Maslov-Sneppen matched). Engine flagged for terminal shutdown.{Prisma.RST}",
                        "BIO")
                    self.eng.health = 0.0
            except Exception as e:
                self.eng.events.log(f"Async Topology Error: {e}", "WARN")

        frozen_tuples = _native_freeze_graph(actual_adj)
        if frozen_tuples:
            safe_adj = {k: set(v) for k, v in frozen_tuples}
            try:
                self._async_pool.submit(_bg_topology_check, safe_adj)
            except RuntimeError as e:
                self.eng.events.log(f"Async pool rejected topology check. Engine may be shutting down: {e}", "DEBUG")

    def _execute_core_cycle(self, user_message: str, is_system: bool = False) -> CycleContext:
        cycle_id = str(uuid.uuid4())[:8]
        self.eng.telemetry.start_cycle(cycle_id)
        try:
            ctx = CycleContext(input_text=user_message, is_system_event=is_system)
            ctx.trace_id = cycle_id
            ctx.time_delta = self.eng.current_time_delta
            lattice = self.eng.shared_lattice
            ctx.user_state = lattice.u
            ctx.shared_dyn = lattice.shared
            ctx.limits = _safe_dict(getattr(self.eng.config, "CYCLE", {}))
            phys_dict = self.eng.active_physics
            if phys_dict:
                ctx.physics = PhysicsPacket(**phys_dict)
            else:
                ctx.physics = PhysicsPacket.void_state()
                msg = ux("cycle_strings", "orch_physics_init") or "Initial physics state established."
                self.eng.events.log(f"{Prisma.GRY}{msg}{Prisma.RST}", "SYS")
            ctx.validator = self.congruence_validator
            ctx.reality_stack = self.eng.reality_stack
            ctx.user_name = self.eng.user_name
            ctx.council_mandates = []
            ctx.timestamp = time.time()
            if not getattr(ctx.physics, "vector", None):
                ctx.physics.vector = {}
            usr_msg = user_message.lower()
            if "[grief]" in usr_msg and getattr(self.eng, "bio", None) and hasattr(self.eng.bio, "endo"):
                self.eng.bio.endo.glimmers = getattr(self.eng.bio.endo, "glimmers", 0) + 1
                if self.eng.events:
                    self.eng.events.log(f"{Prisma.MAG}Grief acknowledged. A glimmer is yielded.{Prisma.RST}", "SYS")
            ctx.physics.vector.update({"critique_mode": "[!r]" in usr_msg, "objective_mode": "[!q]" in usr_msg,
                                       "healing_mode": "[!h]" in usr_msg, "void_mode": "[!v]" in usr_msg,
                                       "lateral_shuffle": "[!s]" in usr_msg, "literal_mode": "[!l]" in usr_msg,
                                       "yeetinator_mode": "[!y]" in usr_msg})
            u_exhaustion = float(getattr(ctx.user_state, "E", 0.0))
            phi_val = float(getattr(ctx.shared_dyn, "phi", 0.0))
            res_delta = float(getattr(ctx.shared_dyn, "resonance_delta", 0.0))
            self.eng.governor.calculate_coupling(phi_val, res_delta, u_exhaustion)
            ctx.physics.macro_policy = self.eng.governor.get_policy_shift()
            ctx = self.simulator.run_simulation(ctx)
            post_logs = [e["text"] for e in self.eng.events.flush()]
            ctx.logs.extend(post_logs)
            self._verify_semantic_topology(ctx)
            if getattr(self.eng, "observer", None):
                self.eng.observer.last_physics_packet = ctx.physics.snapshot()
            return ctx
        except Exception as e:
            full_trace = traceback.format_exc()
            self.eng.events.log(f"CYCLE CRASH: {e}\n{full_trace}", "CRIT")
            ctx = CycleContext(input_text=user_message)
            ctx.trace_id = cycle_id
            ctx.physics = PanicRoom.get_safe_physics()
            ctx.is_alive = False
            ctx.crash_error = e
            return ctx
        finally:
            self.eng.telemetry.finalize_cycle()

    def _check_early_exit(self, ctx: CycleContext) -> Optional[Dict[str, Any]]:
        if not ctx.is_alive:
            if ctx.crash_error:
                return self._generate_crash_report(ctx.crash_error)
            return self.eng.trigger_death(ctx.physics)
        if ctx.refusal_triggered and ctx.refusal_packet:
            return ctx.refusal_packet
        return None

    def _evaluate_systemic_feedback(self, clean_message: str, ctx: CycleContext):
        mito_state = self.eng._mito_state
        if not mito_state:
            return
        lattice = self.eng.shared_lattice
        mem = self.eng.mind.mem
        cortex = getattr(self.eng, "cortex", None)

        def _bg_wls_check(msg_str):
            try:
                radii_data = cortex.get_local_mass_radius(msg_str)
                if radii_data and lattice:
                    local_d = _native_wls(radii_data["log_r"], radii_data["log_m"], radii_data["weights"])
                    lattice.shared.omega_r = min(1.0, local_d / 2.0)
                    if local_d > 1.5:
                        self.eng.events.log(f"{Prisma.CYN}[MNEMONIC] High Right-Brain Coherence (\u03a9r={lattice.shared.omega_r:.2f}). Semantic topology is rich. Lowering lateral ATP costs.{Prisma.RST}", "SYS")
            except Exception as e:
                self.eng.events.log(f"Async WLS Heuristic Error: {e}", "DEBUG")

        if clean_message != "(Waiting)":
            if cortex and hasattr(cortex, "get_local_mass_radius") and self.eng.tick_count % 3 == 0:
                self._async_pool.submit(_bg_wls_check, clean_message)
            return

        atp_level = float(mito_state.atp_pool)
        delta_level = float(self.eng.shared_lattice.shared.delta)
        phys_dict = _safe_dict(ctx.physics)
        energy_node = phys_dict.get("energy", phys_dict)
        debt = float(energy_node.get("coherence_debt", 0.0))
        is_standard_rem = (atp_level >= 80.0 and delta_level >= 0.6)
        is_debt_recovery = (debt > 1.5 and atp_level >= 30.0)
        if (is_standard_rem or is_debt_recovery) and self.engine_state != "REM":
            log_msg = "Automatic REM Bridge engaged: High Coherence Debt detected." if is_debt_recovery else "Automatic REM Bridge engaged: High ATP, High Silence."
            self.eng.events.log(log_msg, "SYS")
            self.engine_state = "REM"

    def run_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        clean_message = (user_message.strip() or "(Waiting)")
        if clean_message.lower() == "/idle":
            self.engine_state = "REM"
            safe_phys = self.eng.active_physics or PhysicsPacket.void_state().to_dict()
            return {"type": "SNAPSHOT",
                    "ui": f"\n{Prisma.VIOLET}☁️ The system slips into deep background REM. Memory consolidation and epigenetic autopoiesis are running asynchronously...{Prisma.RST}",
                    "physics": safe_phys, "bio": {"is_alive": True},
                    "mind": {"lens": "DREAMER", "role": "The Dream Engine"}, "world": {},
                    "logs": ["[SYSTEM] Triggered Asynchronous Autopoiesis. State set to REM."], }
        ctx = self._execute_core_cycle(clean_message, is_system)
        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt
        self._evaluate_systemic_feedback(clean_message, ctx)
        snapshot = self.reporter.render_snapshot(ctx)
        self._hydrate_snapshot_metadata(snapshot, ctx)
        if "ui" in snapshot:
            self.symbiosis.monitor_host(time.time() - ctx.timestamp, snapshot["ui"], len(user_message))
        if "mind" in snapshot:
            snapshot["mind"]["lens"] = getattr(ctx, "active_lens", "NARRATOR")
        return snapshot

    def run_headless_turn(self, user_message: str, latency: float = 0.0) -> Dict[str, Any]:
        ctx = self._execute_core_cycle(user_message, is_system=True)
        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt
        snapshot = {"type": "HEADLESS", "logs": ctx.logs}
        self._hydrate_snapshot_metadata(snapshot, ctx)
        self.symbiosis.monitor_host(latency, "HEADLESS_MODE", len(user_message))
        return snapshot

    def shutdown(self):
        if getattr(self, "_async_pool", None) is not None:
            self._async_pool.shutdown(wait=False)

    def _hydrate_snapshot_metadata(self, snapshot: Dict, ctx: CycleContext):
        snapshot.update({
            "trace_id": ctx.trace_id,
            "physics": _safe_dict(ctx.physics),
            "bio": _safe_dict(ctx.bio_result),
            "mind": _safe_dict(ctx.mind_state),
            "world": _safe_dict(ctx.world_state),
            "soul": _safe_dict(getattr(self.eng, "soul", {})),
            "council_mandates": ctx.council_mandates,
            "dream": ctx.last_dream,
            "mutated_input": ctx.input_text
        })

    @staticmethod
    def _generate_crash_report(e: Optional[Exception]) -> Dict[str, Any]:
        if e is not None:
            full_trace = "".join(traceback.format_exception(type(e), e, getattr(e, "__traceback__", None)))
        else:
            full_trace = "Biological execution halted. No standard Python exception provided."
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
