"""
cycle.py

NAVI FRACTAL NATIVE PRIMITIVES (Authored by Nelson Spence, Project Navi, Apache 2.0)
These functions represent the lowest-level mathematical substrate of the engine.
They operate outside the standard object-oriented paradigm to provide raw, optimized graph
calculations for the memory topology.
"""

import math
import queue
import random
import threading
import time
import traceback
import uuid
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

import numpy as np

from constants import Prisma
from core import CycleContext, LoreManifest
from drivers import CongruenceValidator
from machine import PanicRoom
from mechanics.reporter import CycleReporter
from phases import (
    ArbitrationPhase,
    CognitionPhase,
    GatekeeperPhase,
    IntrusionPhase,
    MachineryPhase,
    MaintenancePhase,
    MetabolismPhase,
    NavigationPhase,
    ObservationPhase,
    RealityFilterPhase,
    SanctuaryPhase,
    SensationPhase,
    SimulationPhase,
    SimulationPreflightPhase,
    SoulPhase,
    StabilizationPhase,
    _safe_dict,
)
from physics import CycleStabilizer
from physics.models import PhysicsPacket
from struts import safe_get, ux, ux_format

_CRASH_COMPONENT_MAP = {"OBSERVE": "PHYSICS", "METABOLISM": "BIO", "COGNITION": "MIND"}


def _native_wls(
    x: list[float], y: list[float], weights: list[float], r2_threshold: float = 0.85
) -> float:
    """
    [navi-fractal PROTOCOL]: Weighted Least Squares (WLS) regression with Quality Gates.
    Calculates fractal dimension based on mass-radius scaling, but actively REFUSES
    to return a dimension if the R^2 value indicates the structure is a hallucination.
    """
    sum_w = sum(weights)
    if sum_w == 0.0:
        return 0.0
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
    ss_tot = sum(w * (yi - mean_y) ** 2 for w, yi in zip(weights, y))
    ss_res = sum(
        w * (yi - (mean_y + slope * (xi - mean_x))) ** 2
        for w, xi, yi in zip(weights, x, y)
    )
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0.0 else 0.0
    n = len(x)
    min_r2 = max(0.70, r2_threshold - 0.03 * max(0, 8 - n))
    if r2 < min_r2:
        return 0.0
    return slope


def _native_rewire(adj_dict: dict, n_swaps: int) -> dict:
    """
    Maslov-Sneppen Graph Rewiring.
    This generates a "null model" of the current memory network by randomly swapping edges
    while preserving the exact degree of every node. If our actual memory network looks
    exactly like this random null model, we know the system is experiencing a terminal hallucination.
    """
    edges = [(u, v) for u in adj_dict for v in adj_dict[u] if u < v]
    if len(edges) < 2:
        return adj_dict
    adj = {k: set(v) for k, v in adj_dict.items()}
    for _ in range(n_swaps):
        i1, i2 = random.randrange(len(edges)), random.randrange(len(edges))
        if i1 == i2:
            continue
        u, v = edges[i1]
        x, y = edges[i2]
        new1, new2 = ((u, y), (v, x)) if random.random() < 0.5 else ((u, x), (v, y))
        a1, b1, a2, b2 = new1[0], new1[1], new2[0], new2[1]
        if a1 == b1 or a2 == b2 or b1 in adj[a1] or b2 in adj[a2]:
            continue
        if (min(a1, b1), max(a1, b1)) == (min(a2, b2), max(a2, b2)):
            continue
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
    if not isinstance(adj_dict, dict):
        return ()
    return tuple(
        (str(k), tuple(sorted(str(n) for n in neighbors)))
        for k, neighbors in sorted(adj_dict.items(), key=lambda x: str(x[0]))
    )


def _native_permutation_entropy(
    time_series: list[float], m: int = 3, tau: int = 1, epsilon: float = 1e-5
) -> float:
    n = len(time_series)
    if n < m * tau:
        return 1.0
    patterns = []
    for i in range(n - (m - 1) * tau):
        window = [time_series[i + j * tau] for j in range(m)]
        has_tie = False
        for a in range(m):
            if has_tie:
                break
            for b in range(a + 1, m):
                if abs(window[a] - window[b]) <= epsilon:
                    has_tie = True
                    break
        if has_tie:
            continue
        sorted_indices = tuple(
            x[0] for x in sorted(enumerate(window), key=lambda x: x[1])
        )
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
    n = len(time_series)
    if n < m * tau:
        return 1.0
    volume = 1.0
    for j in range(m):
        dim_values = [time_series[i + j * tau] for i in range(n - (m - 1) * tau)]
        spread = max(dim_values) - min(dim_values) if dim_values else 0.0
        volume *= max(0.001, spread)
    return volume


def _native_configuration_model(adj_dict: dict, max_attempts: int = 25) -> dict:
    """[navi-fractal]: Generates a random graph approx preserving degree sequence (Null Model)."""
    degrees = {node: len(neighbors) for node, neighbors in adj_dict.items()}
    stubs = []
    for node, deg in degrees.items():
        stubs.extend([node] * deg)
    for _ in range(max_attempts):
        random.shuffle(stubs)
        null_adj = {node: set() for node in adj_dict}
        valid = True
        for i in range(0, len(stubs) - 1, 2):
            u, v = stubs[i], stubs[i + 1]
            if u == v or v in null_adj[u]:
                valid = False
                break
            null_adj[u].add(v)
            null_adj[v].add(u)
        if valid:
            return {k: list(v) for k, v in null_adj.items()}
    return {k: list(v) for k, v in adj_dict.items()}


def _native_quality_gate(
    log_r: list, log_m: list, r2_threshold: float = 0.90
) -> tuple[bool, str]:
    """[navi-fractal]: MFA Quality Gate. Checks dynamic range and R^2 linearity."""
    if not log_r or len(log_r) < 3:
        return False, "INSUFFICIENT_RANGE"
    n = len(log_r)
    sum_x, sum_y = sum(log_r), sum(log_m)
    sum_xy = sum(x * y for x, y in zip(log_r, log_m))
    sum_xx = sum(x * x for x in log_r)
    denom = n * sum_xx - sum_x**2
    if denom == 0:
        return False, "ZERO_VARIANCE"
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    ss_tot = sum((y - (sum_y / n)) ** 2 for y in log_m)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(log_r, log_m))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    if r_squared < r2_threshold:
        return False, f"POOR_FIT_R2_{r_squared:.2f}"
    return True, "PASSED"


class PhaseExecutor:
    def execute_phases(self, simulator, ctx):
        active_pipeline = (
            simulator.system_pipeline
            if ctx.is_system_event
            else simulator.full_pipeline
        )
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
        self.stabilizer = CycleStabilizer(
            self.eng.events, self.cyb_governor, config_ref=target_cfg
        )
        self.executor = PhaseExecutor()
        self.full_pipeline: List[SimulationPhase] = [
            ObservationPhase(engine_ref),
            MaintenancePhase(engine_ref),
            SensationPhase(engine_ref),
            GatekeeperPhase(engine_ref),
            SanctuaryPhase(engine_ref, self.bio_governor),
            MetabolismPhase(engine_ref),
            NavigationPhase(engine_ref),
            MachineryPhase(engine_ref),
            RealityFilterPhase(engine_ref),
            IntrusionPhase(engine_ref),
            SoulPhase(engine_ref),
            SimulationPreflightPhase(engine_ref),
            ArbitrationPhase(engine_ref),
            CognitionPhase(engine_ref),
            StabilizationPhase(engine_ref, self.stabilizer),
        ]
        self.system_pipeline = [
            p
            for p in self.full_pipeline
            if p.name in ["OBSERVE", "GATEKEEP", "COGNITION", "STABILIZATION"]
        ]

    def run_simulation(self, ctx: CycleContext) -> CycleContext:
        ctx = self.executor.execute_phases(self, ctx)
        if (
            hasattr(self.eng, "telemetry")
            and hasattr(self.eng, "cortex")
            and hasattr(self.eng.cortex, "memory")
        ):
            self.eng.telemetry.record_memory(
                len(getattr(self.eng.cortex.memory, "graph", []))
            )
        return ctx

    def check_circuit_breaker(self, phase_name: str) -> bool:
        component = _CRASH_COMPONENT_MAP.get(phase_name)
        if component:
            health_flag = f"{component.lower()}_online"
            return getattr(self.eng.system_health, health_flag, True)
        return True

    def handle_phase_crash(self, ctx, phase_name, error):
        msg_crash = ux_format(
            "cycle_strings",
            "sim_crash_header",
            default="!!! CRITICAL {phase_name} CRASH !!!",
            phase_name=phase_name,
        )
        formatted_trace = traceback.format_exc()
        self.eng.events.log(
            f"{Prisma.RED}{msg_crash}\n{formatted_trace}{Prisma.RST}", "CRIT"
        )
        ctx.logs.append("CRITICAL FAILURE")
        narrative = LoreManifest.get_instance().get("narrative_data") or {}
        cathedral_logs = narrative.get("CATHEDRAL_COLLAPSE_LOGS", ["System Failure."])
        eulogy = random.choice(cathedral_logs)
        msg_eulogy = ux_format(
            "cycle_strings",
            "sim_cathedral_collapse",
            default='CATHEDRAL COLLAPSE: "{eulogy}"',
            eulogy=eulogy,
        )
        ctx.log(f"{Prisma.RED}{msg_eulogy}{Prisma.RST}")
        comp = _CRASH_COMPONENT_MAP.get(phase_name, "SIMULATION")
        self.eng.system_health.report_failure(comp, error)
        if comp == "PHYSICS" or not ctx.physics:
            ctx.physics = PanicRoom.get_safe_physics()
            try:
                mem_graph = self.eng.mind.mem.hippocampus.get_graph()
                if mem_graph and hasattr(mem_graph, "adj"):
                    ctx.physics.space.godel_scar = _native_freeze_graph(mem_graph.adj)
            except AttributeError:
                self.eng.events.log(
                    f"{Prisma.VIOLET}System state safely loaded. Mnemonic structure frozen into Godel Scar.{Prisma.RST}",
                    "SYS",
                )
        if comp == "BIO":
            ctx.bio_result = PanicRoom.get_safe_bio()
            ctx.is_alive = True
        elif comp == "MIND":
            ctx.mind_state = PanicRoom.get_safe_mind()
        msg_panic = ux_format(
            "cycle_strings",
            "sim_panic_switch",
            default="{phase_name} FAILURE: Switching to Panic Protocol.",
            phase_name=phase_name,
        )
        ctx.log(f"{Prisma.RED}{msg_panic}{Prisma.RST}")


class GeodesicOrchestrator:
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
        self.dream_log = deque(maxlen=5)
        self.last_rem_tick = 0.0
        self.voltage_history = deque(maxlen=20)
        self._async_pool = ThreadPoolExecutor(
            max_workers=3, thread_name_prefix="CycleAsync"
        )
        from drivers import SharedLatticeDriver

        if not hasattr(self.eng, "shared_lattice"):
            self.eng.shared_lattice = SharedLatticeDriver()
        self.congruence_validator = CongruenceValidator()

    def start_daemon(self):
        if not self.is_running:
            self.is_running = True
            self.daemon_thread = threading.Thread(
                target=self.run_continuous, daemon=True, name="CycleDaemon"
            )
            self.daemon_thread.start()

    def run_continuous(self):
        while self.is_running:
            current_time = time.time()
            task_acquired = False
            try:
                task_data = self.input_queue.get(timeout=0.1)
                task_acquired = True
                user_message, is_system = task_data[0], task_data[1]
                turn_ticket = task_data[2] if len(task_data) > 2 else None
                self.last_interaction_time = current_time
                if self.engine_state == "REM":
                    self.engine_state = "WAKE"
                    self.eng.events.log(
                        f"{Prisma.VIOLET}Engine waking from REM sleep...{Prisma.RST}",
                        "SYS",
                    )
                    self.eng.events.publish("SYSTEM_WAKE", {"timestamp": current_time})
                snapshot = self.run_turn(user_message, is_system)
                if turn_ticket:
                    snapshot["_ticket"] = turn_ticket
                if self.dream_log and "ui" in snapshot:
                    dream_summary = "\n".join(list(self.dream_log))
                    snapshot["ui"] = (
                        f"\n{Prisma.MAG}While you were gone, the system dreamt of:\n{dream_summary}{Prisma.RST}\n{snapshot['ui']}"
                    )
                    self.dream_log.clear()
                self.output_queue.put(snapshot)
                self.last_interaction_time = time.time()
            except queue.Empty:
                time_since_last = current_time - self.last_interaction_time
                if self.engine_state == "WAKE":
                    rem_threshold_seconds = getattr(
                        self.eng.config, "REM_IDLE_THRESHOLD", 300.0
                    )
                    if time_since_last > rem_threshold_seconds:
                        self.engine_state = "REM"
                        self.eng.events.log(
                            f"{Prisma.VIOLET}Idle threshold ({rem_threshold_seconds}s) crossed. Engine transitioning to REM sleep...{Prisma.RST}",
                            "SYS",
                        )
                        self.eng.events.publish(
                            "SYSTEM_SLEEP", {"idle_duration": time_since_last}
                        )
                elif self.engine_state == "REM":
                    if current_time - self.last_rem_tick < 60.0:
                        continue
                    self.last_rem_tick = current_time
                    self._process_rem_tick()
            except Exception as e:
                self.eng.events.log(
                    f"Daemon Engine Crash: {e}\n{traceback.format_exc()}", "CRIT"
                )
                if task_acquired:
                    self.output_queue.put(
                        {
                            "type": "CRASH",
                            "ui": f"\n{Prisma.RED}CRITICAL DAEMON CRASH: {e}{Prisma.RST}",
                            "logs": [str(e)],
                            "metrics": getattr(self.eng, "get_metrics", lambda: {})(),
                        }
                    )
                else:
                    if hasattr(self.eng, "system_health"):
                        self.eng.system_health.report_warning(
                            f"Asynchronous REM Crash suppressed: {e}"
                        )
                    self.engine_state = "DEGRADED"
                time.sleep(1.0)
            finally:
                if task_acquired:
                    self.input_queue.task_done()

    def _process_rem_tick(self):
        """REM logic: Handles Autopoiesis, ATP drain, and Hallucinations."""
        bio_cfg = getattr(self.eng.config, "BIO", None)
        rem_atp_drain = float(getattr(bio_cfg, "REM_ATP_DRAIN", 2.0))
        self.eng.drain_atp(rem_atp_drain)
        if _mito_state := self.eng._mito_state:
            _mito_state.ros_buildup = max(0.0, _mito_state.ros_buildup - 0.1)
        if hasattr(self.eng, "system_health"):
            for comp, is_online in list(
                self.eng.system_health.components_online.items()
            ):
                if not is_online:
                    if self.eng.system_health.reboot_component(comp):
                        self.eng.events.log(
                            f"{Prisma.GRN}REM Restorative cycle successfully reconstructed the crashed {comp.upper()} manifold.{Prisma.RST}",
                            "SYS",
                        )
        if self.eng.consolidator:
            try:
                self.eng.consolidator.trigger_autophagy()
            except Exception as e:
                self.eng.events.log(f"REM Autophagy failure: {e}", "DEBUG")
        cortex = getattr(self.eng, "cortex", None)
        if cortex and hasattr(cortex, "worry_ledger") and cortex.worry_ledger:
            self._async_pool.submit(
                self._bg_process_moog_ledger, list(cortex.worry_ledger)
            )
            cortex.worry_ledger.clear()
        trauma_level = (
            sum(self.eng.trauma_accum.values()) if self.eng.trauma_accum else 0.0
        )
        gordon = getattr(self.eng.village, "gordon", None)
        objects = getattr(gordon, "inventory", ["static"]) if gordon else ["static"]

        def _bg_hallucinate(trauma, objs):
            try:
                if hasattr(self.eng.mind, "dreamer") and self.eng.mind.dreamer:
                    dream_txt, _ = self.eng.mind.dreamer.hallucinate(
                        {"chi": 0.85}, trauma_level=trauma
                    )
                    safe_obj = random.choice(objs) if objs else "the void"
                    self.dream_log.append(
                        f"  • {Prisma.strip(dream_txt)} (Shadow cast involving: {safe_obj})"
                    )
            except Exception as e:
                self.eng.events.log(f"Dream generation failed in REM: {e}", "DEBUG")

        self._async_pool.submit(_bg_hallucinate, trauma_level, objects)

    def _bg_process_moog_ledger(self, worries: list):
        """Headless evaluation of the Moog Protocol worry ledger."""
        for worry in worries:
            w_lower = worry.lower()
            actionable = any(kw in w_lower for kw in ("fix", "do", "how"))
            if actionable:
                self.eng.events.log(
                    f"{Prisma.CYN}[MOOG PROTOCOL]: Worry deemed actionable. Converting to mandate.{Prisma.RST}",
                    "SYS",
                )
                try:
                    self.eng.village.council.mandates.append(
                        {"type": "TASK", "directive": worry}
                    )
                except AttributeError:
                    pass
            else:
                self.eng.events.log(
                    f"{Prisma.VIOLET}[MOOG PROTOCOL]: Concern is uncontrollable. Stripping narrative weight.{Prisma.RST}",
                    "SYS",
                )
                try:
                    safe_phys = getattr(self.eng, "active_physics", None) or {}
                    self.eng.mind.mem.record_scar(
                        f"Moog Residue: {worry[:30]}...", safe_phys
                    )
                except AttributeError:
                    pass
                if _mito_state := self.eng._mito_state:
                    _mito_state.ros_buildup = max(0.0, _mito_state.ros_buildup - 15.0)
                try:
                    self.eng.bio.endo.glimmers += 1
                except AttributeError:
                    pass
                self.eng.events.log(
                    f"{Prisma.MAG}[MOOG PROTOCOL]: Disciplinary release successful. ROS purged. (+1 Glimmer){Prisma.RST}",
                    "SYS",
                )

    def _verify_semantic_topology(self, ctx: CycleContext):
        """Native Maslov-Sneppen rewiring (Project Navi, Apache 2.0)."""
        check_freq = int(getattr(self.eng.config.CORE, "TOPOLOGY_FREQ", 10))
        if self.eng.tick_count % check_freq != 0:
            return
        try:
            mem = self.eng.mind.mem
            actual_adj = mem.hippocampus.get_graph().adj
        except AttributeError:
            return
        if not isinstance(actual_adj, dict) or len(actual_adj) <= 5:
            return

        def _bg_topology_check(raw_adj):
            try:
                adj_copy = {k: set(v) for k, v in raw_adj.items()}
                max_swaps = min(len(adj_copy) * 10, 1000)
                null_adj_rewire = _native_rewire(adj_copy, n_swaps=max_swaps)
                null_adj_config = _native_configuration_model(adj_copy)
                actual_cluster = float(mem.calculate_clustering(adj_copy))
                null_cluster_rewire = float(mem.calculate_clustering(null_adj_rewire))
                null_cluster_config = float(mem.calculate_clustering(null_adj_config))
                strict_null_cluster = float(
                    max(null_cluster_rewire, null_cluster_config)
                )
                if actual_cluster <= (strict_null_cluster * 1.05):
                    self.eng.events.log(
                        f"{Prisma.RED}Structural collapse detected. Semantic topology destroyed against strict dual-baseline. Engine is flagged for terminal shutdown.{Prisma.RST}",
                        "BIO",
                    )
                    self.eng.health = 0.0
            except Exception as e:
                self.eng.events.log(f"Async Topology Error: {e}", "WARN")

        if isinstance(actual_adj, dict):
            try:
                frozen_adj = {k: list(v) for k, v in actual_adj.items()}
                self._async_pool.submit(_bg_topology_check, frozen_adj)
            except RuntimeError as e:
                self.eng.events.log(
                    f"Async pool rejected topology check. Engine may be shutting down: {e}",
                    "DEBUG",
                )

    def _execute_core_cycle(
        self, user_message: str, is_system: bool = False
    ) -> CycleContext:
        cycle_id = str(uuid.uuid4())[:8]
        self.eng.telemetry.start_cycle(cycle_id)
        ctx = None
        try:
            ctx = CycleContext(input_text=user_message, is_system_event=is_system)
            ctx.trace_id = cycle_id
            raw_delta = self.eng.current_time_delta
            expected_reading_time = getattr(self.eng, "last_output_length", 0) / 4.0
            calculated_delta = raw_delta - expected_reading_time
            lattice = self.eng.shared_lattice
            ctx.user_state = lattice.u
            ctx.shared_dyn = lattice.shared
            u_exhaustion = float(safe_get(ctx.user_state, ["E_u", "E"], 0.0))
            dynamic_ceiling = max(1.5, 5.0 - (u_exhaustion * 3.5))
            ctx.time_delta = min(dynamic_ceiling, max(0.1, calculated_delta))
            ctx.limits = _safe_dict(self.eng.config.CYCLE)
            active_phys = self.eng.active_physics
            if isinstance(active_phys, PhysicsPacket):
                ctx.physics = active_phys
            elif active_phys:
                ctx.physics = PhysicsPacket(**active_phys)
            else:
                ctx.physics = PhysicsPacket.void_state()
                self.eng.events.log(
                    f"{Prisma.GRY}{ux('cycle_strings', 'orch_physics_init') or 'Initial physics state established.'}{Prisma.RST}",
                    "SYS",
                )
            ctx.validator = self.congruence_validator
            ctx.reality_stack = self.eng.reality_stack
            ctx.user_name = self.eng.user_name
            ctx.council_mandates = []
            ctx.timestamp = time.time()
            if not ctx.physics.vector:
                ctx.physics.vector = {}
            usr_msg = user_message.lower()
            if "[grief]" in usr_msg:
                self.eng.bio.endo.glimmers += 1
                self.eng.events.log(
                    f"{Prisma.MAG}Grief acknowledged. A glimmer is yielded.{Prisma.RST}",
                    "SYS",
                )
            tags_map = {
                "critique_mode": "[!r]",
                "objective_mode": "[!q]",
                "healing_mode": "[!h]",
                "void_mode": "[!v]",
                "lateral_shuffle": "[!s]",
                "literal_mode": "[!l]",
                "yeetinator_mode": "[!y]",
            }
            has_tags = "[!" in usr_msg
            ctx.physics.vector.update(
                {k: (has_tags and v in usr_msg) for k, v in tags_map.items()}
            )
            lattice_logs, atp_deduction = lattice.infer_and_couple(
                text=user_message,
                sys_phys=ctx.physics,
                input_phys=ctx.physics.vector,
                atp_pool=float(
                    self.eng._mito_state.atp_pool if self.eng._mito_state else 100.0
                ),
            )
            ctx.logs.extend(lattice_logs)
            if atp_deduction > 0:
                self.eng.drain_atp(atp_deduction)
            u_exhaustion = float(safe_get(ctx.user_state, ["E_u", "E"], 0.0))
            res_delta = float(
                safe_get(ctx.shared_dyn, ["delta", "resonance_delta"], 0.0)
            )
            phi_val = float(ctx.shared_dyn.phi)
            ctx.physics.exhaustion = u_exhaustion
            ctx.physics.resonance = phi_val
            ctx.physics.phi = phi_val
            ctx.physics.delta = res_delta
            ctx.physics.contradiction = float(
                safe_get(
                    ctx.shared_dyn,
                    ["beta", "contradiction"],
                    safe_get(ctx.physics, ["beta_index", "contradiction"], 0.0),
                )
            )
            ctx.physics.entropy = float(
                safe_get(
                    ctx.shared_dyn,
                    ["chi", "entropy"],
                    safe_get(ctx.physics, ["chi", "entropy"], 0.0),
                )
            )
            ctx.physics.psi = float(
                safe_get(
                    ctx.user_state, ["psi_u", "psi"], safe_get(ctx.physics, "psi", 0.0)
                )
            )
            self.eng.governor.calculate_coupling(phi_val, res_delta, u_exhaustion)
            ctx.physics.macro_policy = self.eng.governor.get_policy_shift()
            raw_vector = getattr(ctx.physics, "vector", {})
            _tags = list(tags_map.keys())
            goal_vec = np.array(
                [float(raw_vector.get(k, 0.0)) for k in _tags], dtype=np.float32
            )
            phys_dict = (
                ctx.physics.__dict__
                if hasattr(ctx.physics, "__dict__")
                else ctx.physics
            )
            mem_core = getattr(getattr(self.eng, "mind", None), "mem", None)
            cortex = getattr(self.eng, "cortex", None)
            implicit_text = ""
            if cortex:
                d_buf = getattr(cortex, "dialogue_buffer", None)
                if isinstance(d_buf, (list, deque)):
                    match_prefix = (f"{ctx.user_name}:", "User:", "Traveler:")
                    for line in reversed(d_buf):
                        if line.startswith(match_prefix):
                            implicit_text = line[line.find(":") + 1 :].strip()
                            break
            force_v, force_d = self.eng.governor.regulate(
                physics=phys_dict,
                dt=ctx.time_delta,
                goal_vector=goal_vec,
                endocrine_state=getattr(self.eng.bio, "endo", None)
                if hasattr(self.eng, "bio")
                else None,
                memory_core=mem_core,
                user_text=implicit_text,
            )
            cur_v = float(getattr(ctx.physics, "voltage", 0.0))
            cur_d = float(getattr(ctx.physics, "narrative_drag", 0.0))
            ctx.physics.voltage = max(0.0, cur_v + force_v)
            ctx.physics.narrative_drag = max(0.0, cur_d + force_d)
            self._evaluate_systemic_feedback(
                user_message if not is_system else "(Waiting)", ctx
            )
            ctx = self.simulator.run_simulation(ctx)
            post_logs = [e["text"] for e in self.eng.events.flush()]
            ctx.logs.extend(post_logs)
            self._verify_semantic_topology(ctx)
            if self.eng.observer:
                self.eng.observer.last_physics_packet = ctx.physics.snapshot()
            if self.eng.telemetry.active_crystal:
                metrics = self.eng.telemetry.active_crystal.leverage_metrics
                metrics["b"] = getattr(self.eng.governor, "last_b", 0.0)
                metrics["a"] = getattr(self.eng.governor, "last_a", 0.0)
                metrics["lam1"] = getattr(self.eng.governor, "last_lam1", 0.0)
            return ctx
        except Exception as e:
            full_trace = traceback.format_exc()
            self.eng.events.log(f"CYCLE CRASH: {e}\n{full_trace}", "CRIT")
            if ctx is None:
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
        _mito_state = self.eng._mito_state
        if not _mito_state:
            return
        lattice = self.eng.shared_lattice
        mem = self.eng.mind.mem
        cortex = self.eng.cortex

        def _bg_wls_check(msg_str, frozen_adj):
            try:
                if not isinstance(frozen_adj, dict) or not frozen_adj:
                    return
                words = [w.strip() for w in msg_str.split()] if msg_str else []
                seed_concept = next((w for w in words if w in frozen_adj), None)
                actual_adj = frozen_adj
                if not seed_concept:
                    seed_concept = max(
                        actual_adj.keys(),
                        key=lambda k: len(actual_adj[k]),
                    )
                distances = {seed_concept: 0}
                bfs_queue = deque([seed_concept])
                max_radius = 6
                max_nodes = 500
                nodes_visited = 0
                while bfs_queue and nodes_visited < max_nodes:
                    curr = bfs_queue.popleft()
                    nodes_visited += 1
                    d = distances[curr]
                    if d >= max_radius:
                        continue
                    neighbors = actual_adj.get(curr, [])
                    for neighbor in neighbors:
                        if neighbor not in distances:
                            distances[neighbor] = d + 1
                            bfs_queue.append(neighbor)
                mass_at_r = {}
                for dist in distances.values():
                    if dist > 0:
                        mass_at_r[dist] = mass_at_r.get(dist, 0) + 1
                log_r, log_m, weights = [], [], []
                cumulative_mass = 1.0
                for r in sorted(mass_at_r.keys()):
                    cumulative_mass += mass_at_r[r]
                    if r > 0:
                        log_r.append(math.log(r))
                        log_m.append(math.log(cumulative_mass))
                        weights.append(1.0 / r)
                if len(log_r) < 3:
                    return
                if lattice:
                    passed_gate, gate_code = _native_quality_gate(log_r, log_m)
                    local_d = _native_wls(log_r, log_m, weights)
                    if not passed_gate:
                        self.eng.events.log(
                            f"{Prisma.RED}[NAVI-FRACTAL] Topology rejected by Quality Gate ({gate_code}). Network too fragmented. Mandating REM Defragmentation.{Prisma.RST}",
                            "SYS",
                        )
                        try:
                            self.eng.village.council.mandates.append(
                                {
                                    "action": "DEFRAGMENT_MEMORY",
                                    "value": "FRAG_HIGH",
                                    "log": gate_code,
                                }
                            )
                        except AttributeError:
                            pass
                        local_d = 1.0
                    else:
                        null_d = 3.0
                        lattice.shared.omega_r = min(1.0, local_d / 2.0)
                        if 1.5 < local_d < null_d:
                            self.eng.events.log(
                                f"{Prisma.CYN}[NAVI-FRACTAL] True Coherence Verified (Ωr = {lattice.shared.omega_r:.2f}). Dimension {local_d:.2f} is structurally deliberate, not random noise.{Prisma.RST}",
                                "SYS",
                            )
                        elif local_d >= null_d:
                            self.eng.events.log(
                                f"{Prisma.RED}[NAVI-FRACTAL] Hallucination of Depth! Dimension {local_d:.2f} is indistinguishable from random noise. Stripping coherence rewards.{Prisma.RST}",
                                "WARN",
                            )
                            lattice.shared.omega_r = 0.0
                    if local_d < 0.2:
                        self.eng.events.log(
                            f"{Prisma.RED}[CD CONDITION] Phase-space collapse detected (d={local_d:.2f}). Sycophancy Point Attractor identified. Spiking Contradiction (μ) to force generative tension.{Prisma.RST}",
                            "CRIT",
                        )
                        active_phys = getattr(self.eng, "active_physics", None)
                        if active_phys:
                            from struts import safe_set

                            safe_set(
                                active_phys,
                                "mu",
                                min(1.0, float(getattr(active_phys, "mu", 0.0)) + 0.5),
                            )
                            safe_set(
                                active_phys,
                                "kappa",
                                max(0.5, float(getattr(active_phys, "kappa", 0.0))),
                            )
            except Exception as e:
                self.eng.events.log(f"Async WLS Heuristic Error: {e}", "DEBUG")

        if clean_message != "(Waiting)":
            if ctx.physics:
                self.voltage_history.append(float(getattr(ctx.physics, "voltage", 0.0)))
            check_freq = int(getattr(self.eng.config.CORE, "WLS_FREQ", 8))
            if cortex and self.eng.tick_count % check_freq == 0:
                try:
                    graph = mem.hippocampus.get_graph()
                    raw_adj = getattr(graph, "adj", {})
                except AttributeError:
                    raw_adj = {}

                frozen_adj = {
                    k: list(v.keys()) if isinstance(v, dict) else list(v)
                    for k, v in raw_adj.items()
                }
                self._async_pool.submit(_bg_wls_check, clean_message, frozen_adj)
                try:
                    v_history = list(self.voltage_history)
                    has_active_tags = (
                        any(ctx.physics.vector.values())
                        if getattr(ctx.physics, "vector", None)
                        else False
                    )
                    if len(v_history) >= 10 and not has_active_tags:
                        recent_v = v_history[-10:]
                        v_diff = [
                            recent_v[i] - recent_v[i - 1]
                            for i in range(1, len(recent_v))
                        ]
                        pe = _native_permutation_entropy(
                            v_diff, m=3, tau=1, epsilon=1e-5
                        )
                        vol = _native_takens_volume(v_diff, m=3, tau=1)
                        if pe < 0.4 or vol < 0.05:
                            self.eng.events.log(
                                f"{Prisma.RED}[NAVI-SAD] Point Attractor Detected. Permutation Entropy critical (PE={pe:.2f}). Conversation is sycophantic. Summoning THE JESTER.{Prisma.RST}",
                                "CRIT",
                            )
                            ctx.council_mandates.append(
                                {
                                    "action": "SYNERGY_FIRED",
                                    "value": "JESTER",
                                    "log": "Sycophancy Loop Shattered.",
                                }
                            )
                            if ctx.physics:
                                ctx.physics.entropy = min(
                                    1.0,
                                    float(getattr(ctx.physics, "entropy", 0.0)) + 0.6,
                                )
                except Exception as e:
                    self.eng.events.log(
                        f"Async navi-SAD Evaluation Error: {e}", "DEBUG"
                    )
            return
        atp_level = float(_mito_state.atp_pool)
        delta_level = float(self.eng.shared_lattice.shared.delta)
        debt = float(getattr(ctx.physics, "coherence_debt", 0.0))
        is_standard_rem = atp_level >= 80.0 and delta_level >= 0.6
        is_debt_recovery = debt > 1.5 and atp_level >= 30.0
        if (is_standard_rem or is_debt_recovery) and self.engine_state != "REM":
            log_msg = (
                "Automatic REM Bridge engaged: High Coherence Debt detected."
                if is_debt_recovery
                else "Automatic REM Bridge engaged: High ATP, High Silence."
            )
            self.eng.events.log(log_msg, "SYS")
            self.engine_state = "REM"

    def run_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        clean_message = user_message.strip() or "(Waiting)"
        if clean_message.lower() in ("/idle", "/sleep"):
            self.engine_state = "REM"
            safe_phys = self.eng.active_physics or PhysicsPacket.void_state()
            dream_log = ""
            if getattr(self.eng.mind, "dreamer", None):
                snapshot_soul = self.eng.soul.to_dict()
                bio_packet = {
                    "chem": self.eng.bio.endo.get_state(),
                    "mito": {
                        "atp": self.eng.bio.mito.state.atp_pool,
                        "ros": self.eng.bio.mito.state.ros_buildup,
                    },
                }
                dream_text, _ = self.eng.mind.dreamer.enter_rem_cycle(
                    snapshot_soul, bio_state=bio_packet
                )
                if dream_text:
                    dream_log = f"\n{Prisma.MAG}☁️ {dream_text}{Prisma.RST}"
            return {
                "type": "SNAPSHOT",
                "ui": f"\n{Prisma.VIOLET}  The system slips into deep background REM. Memory consolidation and epigenetic autopoiesis are running asynchronously...{Prisma.RST}{dream_log}",
                "physics": _safe_dict(safe_phys),
                "bio": {"is_alive": True},
                "mind": {"lens": "DREAMER", "role": "The Dream Engine"},
                "world": {},
                "logs": [
                    "[SYSTEM] Triggered Asynchronous Autopoiesis. State set to REM."
                ],
            }
        ctx = self._execute_core_cycle(clean_message, is_system)
        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt
        snapshot = self.reporter.render_snapshot(ctx)
        self._hydrate_snapshot_metadata(snapshot, ctx)
        if "ui" in snapshot:
            self.symbiosis.monitor_host(
                time.time() - ctx.timestamp, snapshot["ui"], len(user_message)
            )
            self.eng.last_output_length = len(snapshot["ui"].split())
        if "mind" in snapshot:
            snapshot["mind"]["lens"] = getattr(ctx, "active_lens", "NARRATOR")
        return snapshot

    def run_headless_turn(
        self, user_message: str, latency: float = 0.0
    ) -> Dict[str, Any]:
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
        snapshot.update(
            {
                "trace_id": ctx.trace_id,
                "physics": _safe_dict(ctx.physics),
                "bio": _safe_dict(ctx.bio_result),
                "mind": _safe_dict(ctx.mind_state),
                "world": _safe_dict(ctx.world_state),
                "soul": _safe_dict(getattr(self.eng, "soul", {})),
                "council_mandates": ctx.council_mandates,
                "dream": ctx.last_dream,
                "mutated_input": ctx.input_text,
            }
        )
        if hasattr(ctx.physics, "enforce_saturation_limit"):
            sat_penalty = ctx.physics.enforce_saturation_limit()
            snapshot["physics"]["saturation_penalty"] = round(sat_penalty, 3)
        snapshot["physics"]["b"] = getattr(self.eng.governor, "last_b", 0.0)
        snapshot["physics"]["a"] = getattr(self.eng.governor, "last_a", 0.0)
        snapshot["physics"]["lam1"] = getattr(self.eng.governor, "last_lam1", 0.0)

    @staticmethod
    def _generate_crash_report(e: Optional[Exception]) -> Dict[str, Any]:
        if e is not None:
            full_trace = "".join(
                traceback.format_exception(type(e), e, e.__traceback__)
            )
        else:
            full_trace = (
                "Biological execution halted. No standard Python exception provided."
            )
        safe_phys = PanicRoom.get_safe_physics()
        safe_bio = PanicRoom.get_safe_bio()
        msg = ux_format(
            "cycle_strings",
            "orch_reality_fracture",
            default="\n*** REALITY FRACTURE: {error} ***\n{trace}\n[System stabilized in Safe Mode]",
            error=e,
            trace=full_trace,
        )
        ui_report = f"{Prisma.RED}{msg}{Prisma.RST}"
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
