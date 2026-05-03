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
import traceback
import uuid
from typing import Dict, Any, List, Optional

from constants import Prisma
from core import CycleContext
# Core structural imports
from core import LoreManifest
from drivers import CongruenceValidator
from machine import PanicRoom
from mechanics.reporter import CycleReporter
# The sequence of reality
from phases import (ObservationPhase, SanctuaryPhase, MaintenancePhase, GatekeeperPhase,
                    MetabolismPhase, RealityFilterPhase, NavigationPhase, MachineryPhase,
                    IntrusionPhase, SoulPhase, ArbitrationPhase, SimulationPreflightPhase,
                    CognitionPhase, SensationPhase, StabilizationPhase, SimulationPhase)
from physics import CycleStabilizer
from presets import BoneConfig
from struts import ux

# Maps specific phase failures to systemic health components so the engine knows *what* died.
_CRASH_COMPONENT_MAP = {"OBSERVE": "PHYSICS", "METABOLISM": "BIO", "COGNITION": "MIND"}

""" 
NAVI FRACTAL NATIVE PRIMITIVES (Authored by Nelson Spence, Project Navi, Apache 2.0) 
Fuller Note: These functions represent the lowest-level mathematical substrate of the engine. 
They operate outside the standard object-oriented paradigm to provide raw, optimized graph 
calculations for the memory topology.
"""

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

        # Determine cross-wiring
        new1, new2 = ((u, y), (v, x)) if random.random() < 0.5 else ((u, x), (v, y))
        a1, b1, a2, b2 = new1[0], new1[1], new2[0], new2[1]

        # Prevent self-loops and redundant edges
        if a1 == b1 or a2 == b2 or b1 in adj.get(a1, set()) or b2 in adj.get(a2, set()):
            continue
        if (min(a1, b1), max(a1, b1)) == (min(a2, b2), max(a2, b2)): continue

        # Execute the swap
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
    return tuple(tuple(sorted(neighbors, key=str)) for _, neighbors in sorted(adj_dict.items(), key=lambda x: str(x[0])))

def _safe_dict(obj):
    """Schur's Pragmatism: Don't crash the UI just because an object forgot to implement to_dict()."""
    if hasattr(obj, "to_dict"): return obj.to_dict()
    if hasattr(obj, "__dict__"): return vars(obj)
    return obj if isinstance(obj, dict) else {}


class PhaseExecutor:
    """
    The Assembly Line.
    Takes a CycleContext and runs it sequentially through the active pipeline of Reality Phases.
    """
    def execute_phases(self, simulator, ctx):
        # Background system events run a truncated pipeline to save ATP.
        active_pipeline = (simulator.system_pipeline if getattr(
            ctx, "is_system_event", False) else simulator.full_pipeline)

        for phase in active_pipeline:
            # If a phase triggers a hard refusal (e.g., Gatekeeper catches a toxic prompt), abort the line.
            if getattr(ctx, "refusal_triggered", False):
                break

            # If the specific biological subsystem is dead, skip its phase to prevent a crash loop.
            if not simulator.check_circuit_breaker(phase.name):
                continue

            try:
                # The payload is mutated and passed forward.
                ctx = phase.run(ctx)
            except Exception as e:
                # Tensegrity catch: A crash in one phase halts the run, but is caught safely.
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

        # The Full Biological/Cognitive Pipeline.
        # Order is absolute. You cannot metabolize before you observe. You cannot think before you metabolize.
        self.full_pipeline: List[SimulationPhase] = [
            ObservationPhase(engine_ref),           # Ingest physical state
            MaintenancePhase(engine_ref),           # Background cleanups
            SensationPhase(engine_ref),             # Affective parsing (Fear/Calm)
            GatekeeperPhase(engine_ref),            # The Checkpoint Council (Security)
            SanctuaryPhase(engine_ref, self.shared_governor), # Safety overrides
            MetabolismPhase(engine_ref),            # Burn ATP
            NavigationPhase(engine_ref),            # Map coordinates
            MachineryPhase(engine_ref),             # Trigger mechanical tools
            RealityFilterPhase(engine_ref),         # Process illusions/stasis
            IntrusionPhase(engine_ref),             # Handle external overrides
            SoulPhase(engine_ref),                  # Apply narrative identity
            ArbitrationPhase(engine_ref),           # The Village council debate
            SimulationPreflightPhase(engine_ref),   # Final checks before generation
            CognitionPhase(engine_ref),             # The LLM Call (The Heavy Lift)
            StabilizationPhase(engine_ref, self.stabilizer), # Post-processing and systemic cooldown
        ]

        # The Short Circuit. Used for asynchronous or background pulses.
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
        self.eng.events.log(f"{Prisma.RED}{msg_crash.format(phase_name=phase_name)}\n{formatted_trace}{Prisma.RST}", "CRIT")

        narrative = LoreManifest.get_instance().get("narrative_data") or {}
        cathedral_logs = narrative.get("CATHEDRAL_COLLAPSE_LOGS", ["System Failure."])
        eulogy = random.choice(cathedral_logs)
        msg_eulogy = ux("cycle_strings", "sim_cathedral_collapse")
        ctx.log(f"{Prisma.RED}{msg_eulogy.format(eulogy=eulogy)}{Prisma.RST}")

        comp = _CRASH_COMPONENT_MAP.get(phase_name, "SIMULATION")
        self.eng.system_health.report_failure(comp, error)

        """Native deterministic graph freezing based on Nelson Spence (Project Navi)."""
        # Load the ultimate fallback variables so the UI has something to render.
        ctx.physics = PanicRoom.get_safe_physics()
        last_packet = getattr(self.eng.observer, "last_physics_packet", None)

        # Create the Gödel Scar: A permanent, immutable imprint of the exact topological
        # structure of the system's memory right before it crashed.
        if last_packet and hasattr(last_packet, "to_graph"):
            last_good_graph = last_packet.to_graph()
            adj_dict = getattr(last_good_graph, "adj", {})
            ctx.physics.space.godel_scar = _native_freeze_graph(adj_dict)
            self.eng.events.log(
                f"{Prisma.VIOLET}[PANIC ROOM] System state safely loaded. Mnemonic structure frozen into Gödel Scar.{Prisma.RST}",
                "SYS")

        # Safely wrap whichever biological system was responsible for the crash.
        if comp == "BIO":
            ctx.bio_result = PanicRoom.get_safe_bio()
            ctx.is_alive = True
        elif comp == "MIND":
            ctx.mind_state = PanicRoom.get_safe_mind()

        msg_panic = ux("cycle_strings", "sim_panic_switch")
        ctx.log(f"{Prisma.RED}{msg_panic.format(phase_name=phase_name)}{Prisma.RST}")


class GeodesicOrchestrator:
    """
    The Conductor.
    This class manages the lifecycle of the Cycle Simulator. It wraps the raw turn logic in
    telemetry, threading, and continuous feedback mechanisms to ensure the engine acts like a
    living organism rather than a static command-line tool.
    """
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.simulator = CycleSimulator(engine_ref)
        self.reporter = CycleReporter(engine_ref)

        # Prevents the engine from starting multiple dreams (REM cycles) simultaneously.
        self._rem_lock = threading.Lock()
        self.symbiosis = self.eng.symbiosis

        # Connects the local organism to the shared multiplex (if running in a networked state).
        from drivers import SharedLatticeDriver
        if not hasattr(self.eng, "shared_lattice"):
            self.eng.shared_lattice = SharedLatticeDriver()

    def _verify_semantic_topology(self, ctx: CycleContext):
        """
        Native Maslov-Sneppen rewiring (Project Navi, Apache 2.0).
        Fuller Note: Offloaded to a background thread to protect main loop tensegrity.
        A biological toxin doesn't kill instantly; it flags the system for apoptosis on the next cycle.
        """
        if getattr(self.eng, "tick_count", 0) % 3 != 0:
            return  # Meadows Dynamics: Limit runaway computational drag.

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

        # The actual work executed asynchronously so the user's prompt isn't delayed.
        def _bg_topology_check(adj_copy):
            try:
                max_swaps = min(len(adj_copy) * 10, 1000)
                # Create the random null model.
                null_adj = _native_rewire(adj_copy, n_swaps=max_swaps)

                # Calculate the clustering coefficient of reality vs. randomness.
                actual_cluster = mem.calculate_clustering(adj_copy)
                null_cluster = mem.calculate_clustering(null_adj)

                # If reality is indistinguishable from the null graph, the system's memory
                # has collapsed into a terminal hallucination. Execute cellular death.
                if actual_cluster <= (null_cluster * 1.05):
                    self.eng.events.log(
                        f"{Prisma.RED}[APOPTOSIS] Structural collapse detected. Semantic topology destroyed (Native Maslov-Sneppen matched). Engine flagged for terminal shutdown.{Prisma.RST}",
                        "BIO")
                    # Set health to 0 to trigger death on the next pre-flight check
                    self.eng.health = 0.0
            except Exception as e:
                self.eng.events.log(f"Async Topology Error: {e}", "WARN")

        # Pass a safely cast list to prevent RuntimeError on the main thread during dict mutation
        try:
            safe_adj = {k: set(v) for k, v in list(actual_adj.items())}
            threading.Thread(target=_bg_topology_check, args=(safe_adj,), daemon=True).start()
        except RuntimeError:
            pass # Graph mutated too fast to safely copy; we skip the topology check this cycle.

    def _execute_core_cycle(self, user_message: str, is_system: bool = False) -> CycleContext:
        """
        The inner workings of a single heartbeat. Prepares the context, hydrates it with
        physical and biological reality, and runs it through the Simulator.
        """
        cycle_id = str(uuid.uuid4())[:8]
        tel = getattr(self.eng, "telemetry", None)
        if tel: tel.start_cycle(cycle_id)

        try:
            ctx = CycleContext(input_text=user_message, is_system_event=is_system)
            ctx.trace_id = cycle_id
            ctx.time_delta = getattr(self.eng, "current_time_delta", 0.0)

            # Anchor to the external multiplex (if applicable)
            ctx.user_state = self.eng.shared_lattice.u
            ctx.shared_dyn = self.eng.shared_lattice.shared

            target_cfg = getattr(self.eng, "config", BoneConfig)
            ctx.limits = _safe_dict(getattr(target_cfg, "CYCLE", {}))

            # Observe the physical world prior to this cycle.
            obs = self.eng.observer
            last_packet = getattr(obs, "last_physics_packet", None)

            if last_packet:
                ctx.physics = last_packet.snapshot()
            else:
                # Hard fallback if physics is missing on Turn 1.
                ctx.physics = PanicRoom.get_safe_physics()
                self.eng.events.log(ux("cycle_strings", "orch_physics_bypass", default="Initial physics bypass. Safe state engaged."), "SYS")

            ctx.validator = CongruenceValidator()
            ctx.reality_stack = getattr(self.eng, "reality_stack", None)
            ctx.user_name = self.eng.user_name
            ctx.council_mandates = []
            ctx.timestamp = time.time()
            ctx = self.simulator.run_simulation(ctx)

            # Ingest all events generated during (and immediately before) this cycle.
            post_logs = [e["text"] for e in self.eng.events.flush()]
            ctx.logs.extend(post_logs)

            # Post-processing topology checks
            self._verify_semantic_topology(ctx)

            # Save the new physical state.
            if obs:
                obs.last_physics_packet = ctx.physics.snapshot()
            return ctx

        except Exception as e:
            # Utter catastrophe. The core execution threw an unhandled python error.
            full_trace = traceback.format_exc()
            self.eng.events.log(f"CYCLE CRASH: {e}\n{full_trace}", "CRIT")

            # Construct an emergency Context to return to the UI so it doesn't freeze.
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

        if getattr(ctx, "refusal_triggered", False) and getattr(ctx, "refusal_packet", None):
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
                # If memory is deep enough, we calculate the geometric coherence.
                radii_data = cortex.get_local_mass_radius(msg_str)
                if radii_data and lattice:
                    local_d = _native_wls(radii_data["log_r"], radii_data["log_m"], radii_data["weights"])
                    lattice.shared.omega_r = min(1.0, local_d / 2.0)

                    # If coherence is incredibly high, the system enters a "flow state" and
                    # lowers the metabolic cost of future connections.
                    if local_d > 1.5:
                        self.eng.events.log(
                            f"{Prisma.CYN}[MNEMONIC] High Right-Brain Coherence (\u03a9r={lattice.shared.omega_r:.2f}). Semantic topology is rich. Lowering lateral ATP costs.{Prisma.RST}",
                            "SYS")
            except Exception:
                pass  # Silent fail for background heuristic

        # Only run the fractal checks if the cortex is active and capable.
        if cortex and hasattr(cortex, "get_local_mass_radius"):
            if getattr(self.eng, "tick_count", 0) % 3 == 0:
                threading.Thread(target=_bg_wls_check, args=(clean_message,), daemon=True).start()

        # The auto-sleep triggers.
        if clean_message != "(Waiting)":
            return

        atp_level = float(self.eng.bio.mito.state.atp_pool)
        delta_level = float(getattr(lattice.shared, "delta", 0.0)) if lattice else 0.0

        phys_dict = _safe_dict(ctx.physics)
        energy_node = phys_dict.get("energy", phys_dict)
        debt = float(energy_node.get("coherence_debt", 0.0))

        # Standard REM: We are resting, and energy is high. Process memories.
        is_standard_rem = (atp_level >= 80.0 and delta_level >= 0.6)
        # Trauma Recovery: We are structurally unstable (high debt). Force sleep to metabolize it.
        is_debt_recovery = (debt > 1.5 and atp_level >= 30.0)

        if (is_standard_rem or is_debt_recovery) and self._rem_lock.acquire(blocking=False):
            log_msg = "Automatic REM Bridge engaged: High Coherence Debt detected." if is_debt_recovery else "Automatic REM Bridge engaged: High ATP, High Silence."
            try:
                threading.Thread(target=self._dispatch_rem_worker, args=(log_msg,), daemon=True).start()
            except RuntimeError:
                self._rem_lock.release()  # Failsafe: Release if thread creation is denied by host OS

    def run_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        """
        The Public Interface.
        This is what `main.py` calls to interact with the engine. It handles special commands
        (like manual sleep) and translates the deep Cycle Context into a flat snapshot for the UI.
        """
        clean_message = (user_message.strip() or "(Waiting)")

        # Manual REM trigger via standard user input.
        if clean_message.lower() == "/idle":
            if self._rem_lock.acquire(blocking=False):
                try:
                    worker = threading.Thread(target=self._dispatch_rem_worker, args=("Spawning detached worker for Dream Engine...",), daemon=True)
                    worker.start()
                except RuntimeError:
                    self._rem_lock.release()
            else:
                self.eng.events.log("Dream worker already active. Ignoring overlapping idle request.", "SYS")

            packet = getattr(self.eng.observer, "last_physics_packet", None)
            safe_phys = packet.snapshot().to_dict() if packet else PanicRoom.get_safe_physics().to_dict()

            # Return instantly to the UI while the dream processes in the background.
            return {
                "type": "SNAPSHOT",
                "ui": f"\n{Prisma.VIOLET}☁️ The system slips into deep background REM. Memory consolidation and epigenetic autopoiesis are running asynchronously...{Prisma.RST}",
                "physics": safe_phys,
                "bio": {"is_alive": True},
                "mind": {"lens": "DREAMER", "role": "The Dream Engine"},
                "world": {},
                "logs": ["[SYSTEM] Triggered Asynchronous Autopoiesis."],
            }

        # Standard Turn Execution
        ctx = self._execute_core_cycle(clean_message, is_system)

        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt

        self._evaluate_systemic_feedback(clean_message, ctx)

        # Translate the deep biological/physical objects into a clean dictionary.
        snapshot = self.reporter.render_snapshot(ctx)
        self._hydrate_snapshot_metadata(snapshot, ctx)

        # Register user interaction pacing.
        if "ui" in snapshot:
            self.symbiosis.monitor_host(time.time() - ctx.timestamp, snapshot["ui"], len(user_message))

        # Ensure the UI snapshot explicitly knows which lens is active for Chaos Test Vector 1.
        if "mind" in snapshot:
            snapshot["mind"]["lens"] = getattr(ctx, "active_lens", "NARRATOR")

        return snapshot

    def run_headless_turn(self, user_message: str, latency: float = 0.0) -> Dict[str, Any]:
        """
        A silent cycle used by the Dream Engine or automated systemic pulses.
        It does not render a UI response.
        """
        # Fuller constraint: System events bypass LLM cognition.
        ctx = self._execute_core_cycle(user_message, is_system=True)
        if exit_pkt := self._check_early_exit(ctx):
            return exit_pkt

        snapshot = {"type": "HEADLESS", "logs": ctx.logs}
        self._hydrate_snapshot_metadata(snapshot, ctx)
        self.symbiosis.monitor_host(latency, "HEADLESS_MODE", len(user_message))
        return snapshot

    def _hydrate_snapshot_metadata(self, snapshot: Dict, ctx: CycleContext):
        """Ensures the UI layer receives all necessary telemetry and background state info."""
        snapshot.update({
            "trace_id": ctx.trace_id,
            "is_alive": True,
            "physics": _safe_dict(ctx.physics),
            "bio": _safe_dict(ctx.bio_result),
            "mind": _safe_dict(ctx.mind_state),
            "world": _safe_dict(ctx.world_state),
            "soul": _safe_dict(getattr(self.eng, "soul", {})),
            "council_mandates": ctx.council_mandates,
            "dream": ctx.last_dream,
            "mutated_input": ctx.input_text,
        })

    @staticmethod
    def _generate_crash_report(e: Exception) -> Dict[str, Any]:
        """The absolute final safety net to ensure the UI layer never receives a NoneType on crash."""
        if e is not None:
            full_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
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