"""
cycle.py
The Heartbeat.
This module defines the main execution loop (The Cycle) of the engine. It is responsible for
orchestrating the linear progression of reality phases (Observation -> Metabolism -> Cognition, etc.)
and managing the asynchronous biological rhythms (REM cycles, topological memory checks) that keep
the system stable over time.
"""
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import traceback
import uuid
from typing import Dict, Any, List, Optional
from constants import Prisma
from core import CycleContext, LoreManifest, safe_dict
from drivers import CongruenceValidator
from machine import PanicRoom
from mechanics.reporter import CycleReporter
from phases import (ObservationPhase, SanctuaryPhase, MaintenancePhase, GatekeeperPhase,
                    MetabolismPhase, RealityFilterPhase, NavigationPhase, MachineryPhase,
                    IntrusionPhase, SoulPhase, ArbitrationPhase, SimulationPreflightPhase,
                    CognitionPhase, SensationPhase, StabilizationPhase, SimulationPhase)
from physics import CycleStabilizer
from presets import BoneConfig
from struts import ux

_CRASH_COMPONENT_MAP = {"OBSERVE": "PHYSICS", "METABOLISM": "BIO", "COGNITION": "MIND"}

# =============================================================================
# NAVI FRACTAL NATIVE PRIMITIVES (Authored by Nelson Spence, Project Navi, Apache 2.0)
# Fuller Note: These functions represent the lowest-level mathematical substrate of the engine.
# They operate outside the standard object-oriented paradigm to provide raw, optimized graph
# calculations for the memory topology.
# =============================================================================

def _native_wls(x: list[float], y: list[float], weights: list[float]) -> float:
    """
    Weighted Least Squares (WLS) regression.
    Used to calculate the fractal dimension of the memory graph based on mass-radius scaling.
    This helps the engine understand if its thoughts are highly structured (high dimension)
    or completely disconnected (low dimension).
    """
    sum_w = sum(weights)
    if sum_w == 0.0: return 0.0
    mean_x = sum(w * xi for w, xi in zip(weights, x)) / sum_w
    mean_y = sum(w * yi for w, yi in zip(weights, y)) / sum_w
    ss_xx = sum(w * xi * xi for w, xi in zip(weights, x)) - sum_w * mean_x * mean_x
    ss_xy = sum(w * xi * yi for w, xi, yi in zip(weights, x, y)) - sum_w * mean_x * mean_y
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
    """
    Immutability enforcer. Converts a mutable adjacency dictionary into a deeply nested,
    hashed tuple. Used to permanently freeze a snapshot of the graph when the system crashes (The Gödel Scar).
    """
    safe_items = []
    for _ in range(3):
        try:
            safe_items = list(adj_dict.items())
            break
        except RuntimeError:
            continue
    return tuple((k, tuple(sorted(neighbors, key=str))) for k, neighbors in sorted(safe_items, key=lambda x: str(x[0])))

class PhaseExecutor:
    """
    The Assembly Line.
    Takes a CycleContext and runs it sequentially through the active pipeline of Reality Phases.
    """

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
    """
    The Reality Blueprint.
    Defines the exact order in which the universe is simulated per turn.
    """

    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.shared_governor = self.eng.bio.governor
        target_cfg = getattr(self.eng, "config", BoneConfig)
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
        self.system_pipeline = [p for p in self.full_pipeline
                                if p.name in ["OBSERVE", "GATEKEEP", "STABILIZATION"]]

    def run_simulation(self, ctx: CycleContext) -> CycleContext:
        """Kicks off the execution."""
        ctx = self.executor.execute_phases(self, ctx)
        return ctx

    def check_circuit_breaker(self, phase_name: str) -> bool:
        """
        Prevents cascading failure by dynamically checking system health against the crash map.
        If a mapped subsystem is offline, its corresponding phases are bypassed.
        """
        component = _CRASH_COMPONENT_MAP.get(phase_name)
        if component:
            health_flag = f"{component.lower()}_online"
            return getattr(self.eng.system_health, health_flag, True)
        return True

    def handle_phase_crash(self, ctx, phase_name, error):
        """
        The Cathedral Collapse Protocol.
        When a phase fails catastrophically, we do not let the python thread die. We log the
        exact trace, output a poetic eulogy to the terminal, and physically lock the broken
        subsystems into the Panic Room.
        """
        msg_crash = ux("cycle_strings", "sim_crash_header")
        formatted_trace = traceback.format_exc()
        self.eng.events.log(f"{Prisma.RED}{msg_crash.format(phase_name=phase_name)}\n{formatted_trace}{Prisma.RST}",
                            "CRIT")
        if phase_name == "COGNITION":
            self.eng.events.log(f"CORTEX COLLAPSE: {error} (See trace above)", "CRIT")
        ctx.logs.append("CRITICAL FAILURE")
        narrative = LoreManifest.get_instance().get("narrative_data") or {}
        cathedral_logs = narrative.get("CATHEDRAL_COLLAPSE_LOGS", ["System Failure."])
        eulogy = random.choice(cathedral_logs)
        msg_eulogy = ux("cycle_strings", "sim_cathedral_collapse")
        ctx.log(f"{Prisma.RED}{msg_eulogy.format(eulogy=eulogy)}{Prisma.RST}")
        comp = _CRASH_COMPONENT_MAP.get(phase_name, "SIMULATION")
        self.eng.system_health.report_failure(comp, error)
        """Native deterministic graph freezing based on Nelson Spence (Project Navi)."""
        last_packet = getattr(self.eng.observer, "last_physics_packet", None)
        if comp == "PHYSICS" or not getattr(ctx, "physics", None):
            ctx.physics = PanicRoom.get_safe_physics()
            if last_packet and hasattr(last_packet, "to_graph"):
                last_good_graph = last_packet.to_graph()
                adj_dict = getattr(last_good_graph, "adj", {})
                ctx.physics.space.godel_scar = _native_freeze_graph(adj_dict)
                self.eng.events.log(
                    f"{Prisma.VIOLET}[PANIC ROOM] System state safely loaded. Mnemonic structure frozen into Gödel Scar.{Prisma.RST}",
                    "SYS")
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
        self._rem_lock = threading.Lock()
        self.symbiosis = self.eng.symbiosis
        self._async_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="CycleAsync")
        from drivers import SharedLatticeDriver
        if not hasattr(self.eng, "shared_lattice"):
            self.eng.shared_lattice = SharedLatticeDriver()
        self.congruence_validator = CongruenceValidator()

    def _verify_semantic_topology(self, ctx: CycleContext):
        """
        Native Maslov-Sneppen rewiring (Project Navi, Apache 2.0).
        A biological toxin doesn't kill instantly; it flags the system for apoptosis on the next cycle.
        """
        if getattr(self.eng, "tick_count", 0) % 3 != 0:
            return
        mem = self.eng.mind.mem
        hippo = mem.hippocampus
        if not (hasattr(hippo, "get_graph") and hasattr(mem, "calculate_clustering")):
            return
        actual_graph = hippo.get_graph()
        if not actual_graph or len(actual_graph) <= 5:
            return
        actual_adj = getattr(actual_graph, "adj", {})
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

        try:
            safe_adj = {k: set(v) for k, v in list(actual_adj.items())}
            self._async_pool.submit(_bg_topology_check, safe_adj)
        except RuntimeError as e:
            self.eng.events.log(f"Async pool rejected topology check. Engine may be shutting down: {e}", "DEBUG")

    def _execute_core_cycle(self, user_message: str, is_system: bool = False) -> CycleContext:
        """
        The inner workings of a single heartbeat. Prepares the context, hydrates it with
        physical and biological reality, and runs it through the Simulator.
        """
        cycle_id = str(uuid.uuid4())[:8]
        tel = getattr(self.eng, "telemetry", None)
        if tel: tel.start_cycle(cycle_id)
        try:
            if not is_system:
                self.eng.tick_count += 1
            ctx = CycleContext(input_text=user_message, is_system_event=is_system)
            ctx.trace_id = cycle_id
            ctx.time_delta = getattr(self.eng, "current_time_delta", 0.0)
            lattice = getattr(self.eng, "shared_lattice", None)
            if lattice:
                ctx.user_state = getattr(lattice, "u", None)
                ctx.shared_dyn = getattr(lattice, "shared", None)
            target_cfg = getattr(self.eng, "config", BoneConfig)
            ctx.limits = safe_dict(getattr(target_cfg, "CYCLE", {}))
            obs = self.eng.observer
            last_packet = getattr(obs, "last_physics_packet", None)
            if last_packet:
                ctx.physics = last_packet.snapshot()
            else:
                ctx.physics = PanicRoom.get_safe_physics()
                self.eng.events.log(
                    ux("cycle_strings", "orch_physics_bypass", default="Initial physics bypass. Safe state engaged."),
                    "SYS")
            ctx.validator = self.congruence_validator
            ctx.reality_stack = getattr(self.eng, "reality_stack", None)
            ctx.user_name = self.eng.user_name
            ctx.council_mandates = []
            ctx.timestamp = time.time()

            # [LEVEL 4 PROTOCOL TRIGGER]
            if not getattr(ctx.physics, "vector", None):
                ctx.physics.vector = {}

            # Correctly map the Sincerity Protocols to their structural vectors
            ctx.physics.vector["pedagogical_mode"] = ("pedagogy" in user_message.lower())
            ctx.physics.vector["lateral_shuffle"] = ("[!" + "s]" in user_message)  # The Shuffle
            ctx = self.simulator.run_simulation(ctx)
            post_logs = [e["text"] for e in self.eng.events.flush()]
            ctx.logs.extend(post_logs)
            self._verify_semantic_topology(ctx)
            if obs:
                obs.last_physics_packet = ctx.physics.snapshot()
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
            if tel: tel.finalize_cycle()

    def _dispatch_rem_worker(self, log_msg: str):
        """Handles asynchronous REM sleep consolidation."""
        try:
            self.eng.events.log(log_msg, "SYS")
            self.run_headless_turn("/idle")
        except Exception as e:
            self.eng.events.log(f"REM Engine Crash: {e}", "CRIT")
        finally:
            self._rem_lock.release()

    def _check_early_exit(self, ctx: CycleContext) -> Optional[Dict[str, Any]]:
        """Intercepts the pipeline return if the organism died or explicitly refused a toxic prompt."""
        if not ctx.is_alive:
            if getattr(ctx, "crash_error", None) is not None:
                return self._generate_crash_report(ctx.crash_error)
            return self.eng.trigger_death(ctx.physics)
        if ctx.refusal_triggered and ctx.refusal_packet:
            return ctx.refusal_packet
        return None

    def _evaluate_systemic_feedback(self, clean_message: str, ctx: CycleContext):
        """
        Meadows' Dynamics: This observes the state *after* the cycle and triggers autonomous
        reactions (like falling asleep) based on the resultant stocks and flows.
        """
        if not hasattr(self.eng.bio, "mito"):
            return
        lattice = getattr(self.eng, "shared_lattice", None)
        """Native WLS fractal dimension calculation (Project Navi). Offloaded to prevent UI drag."""
        mem = self.eng.mind.mem
        cortex = mem.cortex

        def _bg_wls_check(msg_str):
            try:
                radii_data = cortex.get_local_mass_radius(msg_str)
                if radii_data and lattice:
                    local_d = _native_wls(radii_data["log_r"], radii_data["log_m"], radii_data["weights"])
                    lattice.shared.omega_r = min(1.0, local_d / 2.0)
                    if local_d > 1.5:
                        self.eng.events.log(
                            f"{Prisma.CYN}[MNEMONIC] High Right-Brain Coherence (\u03a9r={lattice.shared.omega_r:.2f}). Semantic topology is rich. Lowering lateral ATP costs.{Prisma.RST}",
                            "SYS")
            except Exception as e:
                self.eng.events.log(f"Async WLS Heuristic Error: {e}", "DEBUG")

        if cortex and hasattr(cortex, "get_local_mass_radius"):
            if clean_message != "(Waiting)" and getattr(self.eng, "tick_count", 0) % 3 == 0:
                self._async_pool.submit(_bg_wls_check, clean_message)

        if clean_message != "(Waiting)":
            return
        atp_level = float(self.eng.bio.mito.state.atp_pool)
        delta_level = float(getattr(lattice.shared, "delta", 0.0)) if lattice else 0.0
        phys_dict = safe_dict(ctx.physics)
        energy_node = phys_dict.get("energy", phys_dict)
        debt = float(energy_node.get("coherence_debt", 0.0))
        is_standard_rem = (atp_level >= 80.0 and delta_level >= 0.6)
        is_debt_recovery = (debt > 1.5 and atp_level >= 30.0)
        if (is_standard_rem or is_debt_recovery) and self._rem_lock.acquire(blocking=False):
            log_msg = "Automatic REM Bridge engaged: High Coherence Debt detected." if is_debt_recovery else "Automatic REM Bridge engaged: High ATP, High Silence."
            try:
                self._async_pool.submit(self._dispatch_rem_worker, log_msg)
            except RuntimeError as e:
                self._rem_lock.release()
                self.eng.events.log(f"REM worker rejected by async pool: {e}", "DEBUG")

    def run_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        """
        This is what `main.py` calls to interact with the engine. It handles special commands
        (like manual sleep) and translates the deep Cycle Context into a flat snapshot for the UI.
        """
        clean_message = (user_message.strip() or "(Waiting)")
        if clean_message.lower() == "/idle":
            if self._rem_lock.acquire(blocking=False):
                try:
                    self._async_pool.submit(self._dispatch_rem_worker, "Spawning detached worker for Dream Engine...")
                except RuntimeError as e:
                    self._rem_lock.release()
                    self.eng.events.log(f"Dream worker rejected by async pool: {e}", "WARN")
            else:
                self.eng.events.log("Dream worker already active. Ignoring overlapping idle request.", "SYS")
            packet = getattr(self.eng.observer, "last_physics_packet", None)
            safe_phys = packet.snapshot().to_dict() if packet else PanicRoom.get_safe_physics().to_dict()
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
        self._evaluate_systemic_feedback(clean_message, ctx)
        snapshot = self.reporter.render_snapshot(ctx)
        self._hydrate_snapshot_metadata(snapshot, ctx)
        if "ui" in snapshot:
            self.symbiosis.monitor_host(time.time() - ctx.timestamp, snapshot["ui"], len(user_message))
        if "mind" in snapshot:
            snapshot["mind"]["lens"] = getattr(ctx, "active_lens", "NARRATOR")
        return snapshot

    def run_headless_turn(self, user_message: str, latency: float = 0.0) -> Dict[str, Any]:
        """
        A silent cycle used by the Dream Engine or automated systemic pulses.
        It does not render a UI response.
        """
        ctx = self._execute_core_cycle(user_message, is_system=True)
        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt
        snapshot = {"type": "HEADLESS", "logs": ctx.logs}
        self._hydrate_snapshot_metadata(snapshot, ctx)
        self.symbiosis.monitor_host(latency, "HEADLESS_MODE", len(user_message))
        return snapshot

    def shutdown(self):
        """Meadows: Closes the async flow to prevent zombie thread accumulation."""
        if getattr(self, "_async_pool", None) is not None:
            self._async_pool.shutdown(wait=False)

    def _hydrate_snapshot_metadata(self, snapshot: Dict, ctx: CycleContext):
        """Ensures the UI layer receives all necessary telemetry and background state info."""
        snapshot.update({
            "trace_id": ctx.trace_id,
            "is_alive": True,
            "physics": safe_dict(ctx.physics),
            "bio": safe_dict(ctx.bio_result),
            "mind": safe_dict(ctx.mind_state),
            "world": safe_dict(ctx.world_state),
            "soul": safe_dict(getattr(self.eng, "soul", {})),
            "council_mandates": ctx.council_mandates,
            "dream": ctx.last_dream,
            "mutated_input": ctx.input_text,
        })

    @staticmethod
    def _generate_crash_report(e: Exception) -> Dict[str, Any]:
        """The absolute final safety net to ensure the UI layer never receives a NoneType on crash."""
        if e is not None:
            full_trace = "".join(traceback.format_exception(e))
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
