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
from collections import deque
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
from struts import ux, ux_format

_CRASH_COMPONENT_MAP = {"OBSERVE": "PHYSICS", "METABOLISM": "BIO", "COGNITION": "MIND"}


def _native_wls(x: list[float], y: list[float], weights: list[float]) -> float:
    """
    [navi-fractal PROTOCOL]: Weighted Least Squares (WLS) regression with Quality Gates.
    Calculates fractal dimension based on mass-radius scaling, but actively REFUSES
    to return a dimension if the R^2 value indicates the structure is a hallucination.
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

    if ss_xx == 0.0:
        return 0.0

    slope = ss_xy / ss_xx

    # [navi-fractal] Quality Gate: R^2 validation
    ss_tot = sum(w * (yi - mean_y) ** 2 for w, yi in zip(weights, y))
    ss_res = sum(w * (yi - (mean_y + slope * (xi - mean_x))) ** 2 for w, xi, yi in zip(weights, x, y))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0.0 else 0.0

    if r2 < 0.85:  # The 'inclusive' preset gate
        return 0.0  # Refused. The topology is not truly fractal.

    return slope


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
        adj[a1].add(b1)
        adj[b1].add(a1)
        adj[a2].add(b2)
        adj[b2].add(a2)
        edges[i1], edges[i2] = (min(a1, b1), max(a1, b1)), (min(a2, b2), max(a2, b2))
    return adj


def _native_freeze_graph(adj_dict: dict) -> tuple:
    if not adj_dict or not hasattr(adj_dict, "items"): return ()
    return tuple((k, tuple(sorted(neighbors, key=str))) for k, neighbors in sorted(adj_dict.items(), key=lambda x: str(x[0])))


def _native_permutation_entropy(time_series: list[float], m: int = 3, tau: int = 1, epsilon: float = 1e-5) -> float:
    """
    Calculates Permutation Entropy (PE) using Takens' Delay-Coordinate Embedding.
    Incorporates Navi-SAD strict Tie-Exclusion to prevent fake structural inflation.
    """
    import math
    from collections import Counter
    n = len(time_series)
    if n < m * tau:
        return 1.0

    patterns = []
    for i in range(n - (m - 1) * tau):
        window = [time_series[i + j * tau] for j in range(m)]

        has_tie = False
        for a in range(m):
            if has_tie: break
            for b in range(a + 1, m):
                if abs(window[a] - window[b]) <= epsilon:
                    has_tie = True
                    break
        if has_tie:
            continue

        sorted_indices = tuple(x[0] for x in sorted(enumerate(window), key=lambda x: x[1]))
        patterns.append(sorted_indices)

    if not patterns:
        return 0.0

    counts = Counter(patterns)
    total = len(patterns)
    pe = 0.0
    for count in counts.values():
        p = count / total
        pe -= p * math.log2(p)

    max_e = math.log2(math.factorial(m))
    return pe / max_e if max_e > 0 else 0.0


def _native_takens_volume(time_series: list[float], m: int = 3, tau: int = 1) -> float:
    """
    Estimates the phase-space volume using Takens' Delay Coordinate Embedding.
    Maps the 'shape' of the conversation's attractor.
    """
    n = len(time_series)
    if n < m * tau:
        return 1.0

    points = []
    for i in range(n - (m - 1) * tau):
        points.append([time_series[i + j * tau] for j in range(m)])

    if not points:
        return 1.0

    volume = 1.0
    for dim_values in zip(*points):
        spread = max(dim_values) - min(dim_values)
        volume *= max(0.001, spread)

    return volume


def _native_configuration_model(adj_dict: dict) -> dict:
    """[navi-fractal]: Generates a random graph preserving degree sequence (Null Model)."""
    import random
    degrees = {node: len(neighbors) for node, neighbors in adj_dict.items()}
    stubs = []
    for node, deg in degrees.items():
        stubs.extend([node] * deg)
    random.shuffle(stubs)
    null_adj = {node: list() for node in adj_dict}
    for i in range(0, len(stubs) - 1, 2):
        u, v = stubs[i], stubs[i + 1]
        null_adj[u].append(v)
        null_adj[v].append(u)
    return null_adj


def _native_quality_gate(log_r: list, log_m: list) -> tuple[bool, str]:
    """[navi-fractal]: MFA Quality Gate. Checks dynamic range and R^2 linearity."""
    if not log_r or len(log_r) < 3:
        return False, "INSUFFICIENT_RANGE"

    n = len(log_r)
    sum_x, sum_y = sum(log_r), sum(log_m)
    sum_xy = sum(x * y for x, y in zip(log_r, log_m))
    sum_xx = sum(x * x for x in log_r)

    denom = (n * sum_xx - sum_x ** 2)
    if denom == 0:
        return False, "ZERO_VARIANCE"

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    ss_tot = sum((y - (sum_y / n)) ** 2 for y in log_m)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(log_r, log_m))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    if r_squared < 0.90:
        return False, f"POOR_FIT_R2_{r_squared:.2f}"
    return True, "PASSED"

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
        self.bio_governor = self.eng.bio.governor
        target_cfg = self.eng.config
        self.stabilizer = CycleStabilizer(self.eng.events, self.cyb_governor, config_ref=target_cfg)
        self.executor = PhaseExecutor()
        self.full_pipeline: List[SimulationPhase] = [ObservationPhase(engine_ref), MaintenancePhase(engine_ref),
            SensationPhase(engine_ref), GatekeeperPhase(engine_ref), SanctuaryPhase(engine_ref, self.bio_governor),
            MetabolismPhase(engine_ref), NavigationPhase(engine_ref), MachineryPhase(engine_ref), RealityFilterPhase(engine_ref),
            IntrusionPhase(engine_ref), SoulPhase(engine_ref), SimulationPreflightPhase(engine_ref), ArbitrationPhase(engine_ref),
            CognitionPhase(engine_ref), StabilizationPhase(engine_ref, self.stabilizer), ]
        self.system_pipeline = [p for p in self.full_pipeline if p.name in ["OBSERVE", "GATEKEEP", "COGNITION", "STABILIZATION"]]

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
        msg_crash = ux_format("cycle_strings", "sim_crash_header", default="!!! CRITICAL {phase_name} CRASH !!!", phase_name=phase_name)
        formatted_trace = traceback.format_exc()
        self.eng.events.log(f"{Prisma.RED}{msg_crash}\n{formatted_trace}{Prisma.RST}", "CRIT")
        ctx.logs.append("CRITICAL FAILURE")
        narrative = LoreManifest.get_instance().get("narrative_data") or {}
        cathedral_logs = narrative.get("CATHEDRAL_COLLAPSE_LOGS", ["System Failure."])
        eulogy = random.choice(cathedral_logs)
        msg_eulogy = ux_format("cycle_strings", "sim_cathedral_collapse", default="CATHEDRAL COLLAPSE: \"{eulogy}\"", eulogy=eulogy)
        ctx.log(f"{Prisma.RED}{msg_eulogy}{Prisma.RST}")
        comp = _CRASH_COMPONENT_MAP.get(phase_name, "SIMULATION")
        self.eng.system_health.report_failure(comp, error)
        if comp == "PHYSICS" or not ctx.physics:
            ctx.physics = PanicRoom.get_safe_physics()
            try:
                mem_graph = self.eng.mind.mem.hippocampus.get_graph()
                if mem_graph and hasattr(mem_graph, "adj"):
                    ctx.physics.space.godel_scar = _native_freeze_graph(mem_graph.adj)
                    self.eng.events.log(
                        f"{Prisma.VIOLET}System state safely loaded. Mnemonic structure frozen into Godel Scar.{Prisma.RST}", "SYS")
            except AttributeError:
                pass
        if comp == "BIO":
            ctx.bio_result = PanicRoom.get_safe_bio()
            ctx.is_alive = True
        elif comp == "MIND":
            ctx.mind_state = PanicRoom.get_safe_mind()
        msg_panic = ux_format("cycle_strings", "sim_panic_switch", default="{phase_name} FAILURE: Switching to Panic Protocol.", phase_name=phase_name)
        ctx.log(f"{Prisma.RED}{msg_panic}{Prisma.RST}")

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
        self.voltage_history = deque(maxlen=20)
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
                    snapshot["ui"] = f"\n{Prisma.MAG}While you were gone, the system dreamt of:\n{dream_summary}{Prisma.RST}\n{snapshot['ui']}"
                    self.dream_log.clear()
                self.output_queue.put(snapshot)

            except queue.Empty:
                time_since_last = current_time - self.last_interaction_time
                if self.engine_state == "WAKE":
                    rem_threshold_seconds = self.eng.config.REM_IDLE_THRESHOLD
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
        rem_atp_drain = self.eng.config.BIO.REM_ATP_DRAIN
        self.eng.drain_atp(rem_atp_drain)
        if mito_state := self.eng._mito_state:
            mito_state.ros_buildup = max(0.0, mito_state.ros_buildup - 0.1)
        if self.eng.consolidator:
            try:
                self.eng.consolidator.trigger_autophagy()
            except Exception as e:
                self.eng.events.log(f"REM Autophagy failure: {e}", "DEBUG")
        trauma_level = sum(self.eng.trauma_accum.values()) if self.eng.trauma_accum else 0.0
        gordon = getattr(self.eng.village, "gordon", None)
        objects = getattr(gordon, "inventory", ["static"]) if gordon else ["static"]

        def _bg_hallucinate(trauma, objs):
            try:
                if hasattr(self.eng.mind, "dream_engine"):
                    dream_txt, _ = self.eng.mind.dream_engine.hallucinate({"chi": 0.85}, trauma_level=trauma)
                    self.dream_log.append(
                        f"  • {Prisma.strip(dream_txt)} (Shadow cast involving: {random.choice(objs)})")
            except Exception as e:
                self.eng.events.log(f"Dream generation failed in REM: {e}", "DEBUG")

        self._async_pool.submit(_bg_hallucinate, trauma_level, objects)

    def _verify_semantic_topology(self, ctx: CycleContext):
        """ Native Maslov-Sneppen rewiring (Project Navi, Apache 2.0). """
        if self.eng.tick_count % 3 != 0:
            return
        mem = getattr(self.eng.mind, "mem", None)
        hippocampus = getattr(mem, "hippocampus", None) if mem else None
        actual_graph = hippocampus.get_graph() if hippocampus else None
        actual_adj = getattr(actual_graph, "adj", None)
        if not actual_adj or len(actual_adj) <= 5:
            return

        def _bg_topology_check(adj_copy):
            try:
                max_swaps = min(len(adj_copy) * 10, 1000)
                # [navi-fractal PROTOCOL]: Dual Null-Model generation
                null_adj_rewire = _native_rewire(adj_copy, n_swaps=max_swaps)
                null_adj_config = _native_configuration_model(adj_copy)
                actual_cluster = mem.calculate_clustering(adj_copy)
                null_cluster_rewire = mem.calculate_clustering(null_adj_rewire)
                null_cluster_config = mem.calculate_clustering(null_adj_config)
                strict_null_cluster = max(null_cluster_rewire, null_cluster_config)
                if actual_cluster <= (strict_null_cluster * 1.05):
                    self.eng.events.log(
                        f"{Prisma.RED}Structural collapse detected. Semantic topology destroyed against strict dual-baseline. Engine is flagged for terminal shutdown.{Prisma.RST}",
                        "BIO")
                    if hasattr(self.eng, "bio") and hasattr(self.eng.bio, "biometrics"):
                        self.eng.bio.biometrics.health = 0.0
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
            raw_delta = self.eng.current_time_delta
            expected_reading_time = getattr(self.eng, "last_output_length", 0) / 4.0  # ~250 WPM
            ctx.time_delta = max(0.1, raw_delta - expected_reading_time)
            lattice = self.eng.shared_lattice
            ctx.user_state = lattice.u
            ctx.shared_dyn = lattice.shared
            ctx.limits = _safe_dict(self.eng.config.CYCLE)
            active_phys = self.eng.active_physics
            if isinstance(active_phys, PhysicsPacket):
                ctx.physics = active_phys
            elif active_phys:
                ctx.physics = PhysicsPacket(**active_phys)
            else:
                ctx.physics = PhysicsPacket.void_state()
                self.eng.events.log(f"{Prisma.GRY}{ux('cycle_strings', 'orch_physics_init') or 'Initial physics state established.'}{Prisma.RST}", "SYS")
            ctx.validator = self.congruence_validator
            ctx.reality_stack = self.eng.reality_stack
            ctx.user_name = self.eng.user_name
            ctx.council_mandates = []
            ctx.timestamp = time.time()
            if not ctx.physics.vector:
                ctx.physics.vector = {}
            usr_msg = user_message.lower()
            if "[grief]" in usr_msg:  # NECESSARY GRIEF INTERCEPT
                self.eng.bio.endo.glimmers += 1
                self.eng.events.log(f"{Prisma.MAG}Grief acknowledged. A glimmer is yielded.{Prisma.RST}", "SYS")
            tags_map = {"critique_mode": "[!r]", "objective_mode": "[!q]", "healing_mode": "[!h]",
                        "void_mode": "[!v]", "lateral_shuffle": "[!s]", "literal_mode": "[!l]",
                        "yeetinator_mode": "[!y]"}
            has_tags = "[!" in usr_msg
            ctx.physics.vector.update({k: (has_tags and v in usr_msg) for k, v in tags_map.items()})
            lattice_logs, atp_deduction = lattice.infer_and_couple(text=user_message, sys_phys=ctx.physics, input_phys=ctx.physics.vector, atp_pool=float(
                    self.eng._mito_state.atp_pool if self.eng._mito_state else 100.0))
            ctx.logs.extend(lattice_logs)
            if atp_deduction > 0:
                self.eng.drain_atp(atp_deduction)
            u_exhaustion = float(getattr(ctx.user_state, "E_u", getattr(ctx.user_state, "E", 0.0)))
            phi_val = float(ctx.shared_dyn.phi)
            res_delta = float(getattr(ctx.shared_dyn, "delta", getattr(ctx.shared_dyn, "resonance_delta", 0.0)))
            self.eng.governor.calculate_coupling(phi_val, res_delta, u_exhaustion)
            ctx.physics.macro_policy = self.eng.governor.get_policy_shift()
            self._evaluate_systemic_feedback(user_message if not is_system else "(Waiting)", ctx)
            ctx = self.simulator.run_simulation(ctx)
            post_logs = [e["text"] for e in self.eng.events.flush()]
            ctx.logs.extend(post_logs)
            self._verify_semantic_topology(ctx)
            if self.eng.observer:
                self.eng.observer.last_physics_packet = ctx.physics.snapshot()
            # [CD PROTOCOL] Inject metrics into the Telemetry Crystal
            if self.eng.telemetry.active_crystal and hasattr(ctx.physics, "get_principal_eigenvalue"):
                self.eng.telemetry.active_crystal.leverage_metrics.update({
                    "b": ctx.physics.get_viability_potential(),
                    "a": ctx.physics.get_creative_drive(),
                    "lam1": ctx.physics.get_principal_eigenvalue()
                })
            return ctx
        except Exception as e:
            full_trace = traceback.format_exc()
            self.eng.events.log(f"CYCLE CRASH: {e}\n{full_trace}", "CRIT")
            if 'ctx' not in locals():
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
        cortex = self.eng.cortex

        def _bg_wls_check(msg_str):
            try:
                if hasattr(cortex, "get_local_mass_radius"):
                    radii_data = cortex.get_local_mass_radius(msg_str)
                    if radii_data and lattice:
                        # [navi-fractal PROTOCOL]: Evaluate Quality Gates and Null Model
                        passed_gate, gate_code = _native_quality_gate(radii_data["log_r"], radii_data["log_m"])
                        local_d = _native_wls(radii_data["log_r"], radii_data["log_m"], radii_data["weights"])
                        if not passed_gate:
                            self.eng.events.log(
                                f"{Prisma.RED}[NAVI-FRACTAL] Topology rejected by Quality Gate ({gate_code}). Network too fragmented. Mandating REM Defragmentation.{Prisma.RST}",
                                "SYS")
                            ctx.council_mandates.append(
                                {"action": "DEFRAGMENT_MEMORY", "value": "FRAG_HIGH", "log": gate_code})
                            local_d = 1.0  # Flatten dimension on failure
                        else:
                            # Generate Null Model to detect Hallucinations of Depth
                            null_d = 3.0  # A completely random graph trends toward infinite/high dimension
                            lattice.shared.omega_r = min(1.0, local_d / 2.0)
                            if 1.5 < local_d < null_d:
                                self.eng.events.log(
                                    f"{Prisma.CYN}[NAVI-FRACTAL] True Coherence Verified (\u03a9r={lattice.shared.omega_r:.2f}). Dimension {local_d:.2f} is structurally deliberate, not random noise.{Prisma.RST}",
                                    "SYS")
                            elif local_d >= null_d:
                                self.eng.events.log(
                                    f"{Prisma.RED}[NAVI-FRACTAL] Hallucination of Depth! Dimension {local_d:.2f} is indistinguishable from random noise. Stripping coherence rewards.{Prisma.RST}",
                                    "WARN")
                                lattice.shared.omega_r = 0.0

                        if local_d < 0.2:
                            self.eng.events.log(f"{Prisma.RED}[CD CONDITION] Phase-space collapse detected (d={local_d:.2f}). Sycophancy Point Attractor identified. Spiking Contradiction (μ) to force generative tension.{Prisma.RST}", "CRIT")
                            if ctx.physics:
                                ctx.physics.mu = min(1.0, float(getattr(ctx.physics, "mu", 0.0)) + 0.5)
                                ctx.physics.kappa = max(0.5, float(getattr(ctx.physics, "kappa", 0.0)))
            except Exception as e:
                self.eng.events.log(f"Async WLS Heuristic Error: {e}", "DEBUG")

        if clean_message != "(Waiting)":
            if ctx.physics:
                self.voltage_history.append(float(getattr(ctx.physics, "voltage", 0.0)))
            if cortex and self.eng.tick_count % 3 == 0:
                self._async_pool.submit(_bg_wls_check, clean_message)
            # [navi-SAD PROTOCOL]: Calculate Permutation Entropy & Takens Volume
            try:
                v_history = list(self.voltage_history)
                if len(v_history) >= 10:
                    recent_v = v_history[-10:]
                    v_diff = [recent_v[i] - recent_v[i - 1] for i in range(1, len(recent_v))]
                    pe = _native_permutation_entropy(v_diff, m=3, tau=1, epsilon=1e-5)
                    vol = _native_takens_volume(v_diff, m=3, tau=1)
                    if pe < 0.4 or vol < 0.05:
                        self.eng.events.log(
                            f"{Prisma.RED}[NAVI-SAD] Point Attractor Detected. Permutation Entropy critical (PE={pe:.2f}). Conversation is sycophantic. Summoning THE JESTER.{Prisma.RST}",
                            "CRIT")
                        ctx.council_mandates.append(
                            {"action": "SYNERGY_FIRED", "value": "JESTER", "log": "Sycophancy Loop Shattered."})
                        if ctx.physics:
                            ctx.physics.entropy = min(1.0, float(getattr(ctx.physics, "entropy", 0.0)) + 0.6)
            except Exception as e:
                self.eng.events.log(f"Async navi-SAD Evaluation Error: {e}", "DEBUG")
            return

        atp_level = float(mito_state.atp_pool)
        delta_level = float(self.eng.shared_lattice.shared.delta)
        debt = float(getattr(ctx.physics, "coherence_debt", 0.0))
        is_standard_rem = (atp_level >= 80.0 and delta_level >= 0.6)
        is_debt_recovery = (debt > 1.5 and atp_level >= 30.0)
        if (is_standard_rem or is_debt_recovery) and self.engine_state != "REM":
            log_msg = "Automatic REM Bridge engaged: High Coherence Debt detected." if is_debt_recovery else "Automatic REM Bridge engaged: High ATP, High Silence."
            self.eng.events.log(log_msg, "SYS")
            self.engine_state = "REM"

    def run_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        """NOTE: /idle is here as a short-circuit protection for REM sleep. Leave it alone."""
        clean_message = (user_message.strip() or "(Waiting)")
        if clean_message.lower() in ("/idle", "/sleep"):
            self.engine_state = "REM"
            safe_phys = self.eng.active_physics or PhysicsPacket.void_state()
            dream_log = ""
            if getattr(self.eng.mind, "dreamer", None):
                snapshot_soul = self.eng.soul.to_dict()
                bio_packet = {
                    "chem": self.eng.bio.endo.get_state(),
                    "mito": {"atp": self.eng.bio.mito.state.atp_pool, "ros": self.eng.bio.mito.state.ros_buildup}
                }
                dream_text, _ = self.eng.mind.dreamer.enter_rem_cycle(snapshot_soul, bio_state=bio_packet)
                if dream_text:
                    dream_log = f"\n{Prisma.MAG}☁️ {dream_text}{Prisma.RST}"
            return {"type": "SNAPSHOT",
                    "ui": f"\n{Prisma.VIOLET}  The system slips into deep background REM. Memory consolidation and epigenetic autopoiesis are running asynchronously...{Prisma.RST}{dream_log}",
                    "physics": _safe_dict(safe_phys), "bio": {"is_alive": True},
                    "mind": {"lens": "DREAMER", "role": "The Dream Engine"}, "world": {},
                    "logs": ["[SYSTEM] Triggered Asynchronous Autopoiesis. State set to REM."], }
        ctx = self._execute_core_cycle(clean_message, is_system)
        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt
        snapshot = self.reporter.render_snapshot(ctx)
        self._hydrate_snapshot_metadata(snapshot, ctx)
        if "ui" in snapshot:
            self.symbiosis.monitor_host(time.time() - ctx.timestamp, snapshot["ui"], len(user_message))
            self.eng.last_output_length = len(snapshot["ui"].split())
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

        # [CD PROTOCOL] Inject CD Metrics into the physics snapshot for UI rendering
        if hasattr(ctx.physics, "get_principal_eigenvalue") and isinstance(snapshot.get("physics"), dict):
            if hasattr(ctx.physics, "enforce_saturation_limit"):
                sat_penalty = ctx.physics.enforce_saturation_limit()
                snapshot["physics"]["saturation_penalty"] = round(sat_penalty, 3)

            snapshot["physics"]["b"] = ctx.physics.get_viability_potential()
            snapshot["physics"]["a"] = ctx.physics.get_creative_drive()
            snapshot["physics"]["lam1"] = ctx.physics.get_principal_eigenvalue()

    @staticmethod
    def _generate_crash_report(e: Optional[Exception]) -> Dict[str, Any]:
        if e is not None:
            full_trace = "".join(traceback.format_exception(type(e), e, getattr(e, "__traceback__", None)))
        else:
            full_trace = "Biological execution halted. No standard Python exception provided."
        safe_phys = PanicRoom.get_safe_physics()
        safe_bio = PanicRoom.get_safe_bio()
        msg = ux_format("cycle_strings", "orch_reality_fracture", default="\n*** REALITY FRACTURE: {error} ***\n{trace}\n[System stabilized in Safe Mode]", error=e, trace=full_trace)
        ui_report = f"{Prisma.RED}{msg}{Prisma.RST}"
        return {"type": "CRASH", "ui": ui_report, "physics": safe_phys.to_dict(), "bio": safe_bio,
                "mind": PanicRoom.get_safe_mind(), "world": {"orbit": ["VOID"], "loci_description": "System Failure"},
                "logs": ["CRITICAL FAILURE", "SAFE MODE ACTIVE"], "is_alive": True, }
