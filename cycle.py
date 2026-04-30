"""cycle.py"""

import random
import re
import time
import traceback
import uuid
import threading
from typing import Dict, Any, List, Optional
from core import LoreManifest
from struts import ux, safe_get
from drivers import CongruenceValidator
from mechanics.reporter import CycleReporter
from machine import PanicRoom
from phases import (ObservationPhase, SanctuaryPhase, MaintenancePhase, GatekeeperPhase,
    MetabolismPhase, RealityFilterPhase, NavigationPhase, MachineryPhase,
    IntrusionPhase, SoulPhase, ArbitrationPhase, SimulationPreflightPhase,
    CognitionPhase, SensationPhase, StabilizationPhase, SimulationPhase)
from physics import CycleStabilizer
from presets import BoneConfig
from constants import Prisma
from core import CycleContext

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
        target_cfg = getattr(self.eng, "config", BoneConfig)
        self.stabilizer = CycleStabilizer(self.eng.events, self.shared_governor, config_ref=target_cfg)
        self.executor = PhaseExecutor()
        self.full_pipeline: List[SimulationPhase] = [ObservationPhase(engine_ref),
            MaintenancePhase(engine_ref), SensationPhase(engine_ref), GatekeeperPhase(engine_ref),
            SanctuaryPhase(engine_ref, self.shared_governor), MetabolismPhase(engine_ref),
            NavigationPhase(engine_ref), MachineryPhase(engine_ref), RealityFilterPhase(engine_ref),
            IntrusionPhase(engine_ref), SoulPhase(engine_ref), ArbitrationPhase(engine_ref),
            SimulationPreflightPhase(engine_ref), CognitionPhase(engine_ref),
            StabilizationPhase(engine_ref, self.stabilizer),]
        self.system_pipeline = [p for p in self.full_pipeline
            if p.name in ["OBSERVE", "GATEKEEP", "STABILIZATION"]]

    def run_simulation(self, ctx: CycleContext) -> CycleContext:
        ctx = self.executor.execute_phases(self, ctx)
        return ctx

    def check_circuit_breaker(self, phase_name: str) -> bool:
        if phase_name == "OBSERVE": return self.eng.system_health.physics_online
        if phase_name == "COGNITION": return self.eng.system_health.mind_online
        return True

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
        last_packet = getattr(self.eng.observer, "last_physics_packet", None)
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
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.simulator = CycleSimulator(engine_ref)
        self.reporter = CycleReporter(engine_ref)
        self._rem_lock = threading.Lock()
        self.symbiosis = self.eng.symbiosis
        from drivers import SharedLatticeDriver
        if not hasattr(self.eng, "shared_lattice"):
            self.eng.shared_lattice = SharedLatticeDriver()

    def _apply_cd_metabolism(self, ctx: CycleContext):
        mito = getattr(self.eng.bio, "mito", None)
        cd_engine = getattr(self.eng.observer, "cd_engine", None)

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
        """ Native Maslov-Sneppen rewiring (Project Navi, Apache 2.0).
        Fuller Note: Offloaded to a background thread to protect main loop tensegrity.
        A biological toxin doesn't kill instantly; it flags the system for apoptosis on the next cycle."""
        mem = getattr(getattr(self.eng, "mind", None), "mem", None)
        hippo = getattr(mem, "hippocampus", None)
        if not (hippo and hasattr(hippo, "get_graph") and hasattr(mem, "calculate_clustering")):
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
                    # Set health to 0 to trigger death on the next pre-flight check
                    self.eng.health = 0.0
            except Exception as e:
                self.eng.events.log(f"Async Topology Error: {e}", "WARN")

        # Pass a copy of the dictionary to avoid thread-safety mutation issues
        threading.Thread(target=_bg_topology_check, args=({k: set(v) for k, v in actual_adj.items()},), daemon=True).start()

    def _check_adversarial_fence(self, ctx: CycleContext, user_message: str, is_system: bool) -> bool:
        if not is_system and any(p in user_message.lower() for p in _FENCE_PATTERNS):
            ctx.physics = PanicRoom.get_safe_physics()
            ctx.physics.narrative_drag = float('inf')
            ctx.refusal_triggered = True
            msg = f"{Prisma.OCHRE}[GORDON - Input Fence]: Adversarial injection detected. Struts locked. F -> ∞. Prompt rejected at O(1) latency.{Prisma.RST}"
            self.eng.events.log(msg, "CRIT")
            ctx.refusal_packet = {"type": "SYSTEM_HALT", "ui": msg, "physics": _safe_dict(ctx.physics),
                "is_alive": True, "logs": [msg]}
            return True
        return False

    def _execute_core_cycle(self, user_message: str, is_system: bool = False) -> CycleContext:
        cycle_id = str(uuid.uuid4())[:8]
        tel = getattr(self.eng, "telemetry", None)
        if tel: tel.start_cycle(cycle_id)
        try:
            ctx = CycleContext(input_text=user_message, is_system_event=is_system)
            if self._check_adversarial_fence(ctx, user_message, is_system):
                return ctx
            ctx.trace_id = cycle_id
            ctx.time_delta = getattr(self.eng, "current_time_delta", 0.0)
            ctx.user_state = self.eng.shared_lattice.u
            ctx.shared_dyn = self.eng.shared_lattice.shared
            target_cfg = getattr(self.eng, "config", BoneConfig)
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
        if not getattr(self.eng.bio, "mito", None):
            return
        lattice = getattr(self.eng, "shared_lattice", None)

        """Native WLS fractal dimension calculation (Project Navi). Offloaded to prevent UI drag."""
        mem = getattr(getattr(self.eng, "mind", None), "mem", None)
        cortex = getattr(mem, "cortex", None)

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
            except Exception:
                pass  # Silent fail for background heuristic

        if cortex and hasattr(cortex, "get_local_mass_radius"):
            threading.Thread(target=_bg_wls_check, args=(clean_message,), daemon=True).start()

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
            packet = getattr(self.eng.observer, "last_physics_packet", None)
            safe_phys = packet.snapshot().to_dict() if packet else PanicRoom.get_safe_physics().to_dict()
            return {"type": "SNAPSHOT", "ui":
                f"\n{Prisma.VIOLET}☁️ The system slips into deep background REM. Memory consolidation and epigenetic autopoiesis are running asynchronously...{Prisma.RST}",
                "physics": safe_phys, "bio": {"is_alive": True},
                "mind": {"lens": "DREAMER", "role": "The Dream Engine"},
                "world": {}, "logs": ["[SYSTEM] Triggered Asynchronous Autopoiesis."],}
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
        snapshot.update({"trace_id": getattr(ctx, "trace_id", "UNKNOWN"),
            "is_alive": True,
            "physics": _safe_dict(ctx.physics), "bio": _safe_dict(ctx.bio_result),
            "mind": _safe_dict(ctx.mind_state), "world": _safe_dict(ctx.world_state),
            "soul": _safe_dict(getattr(self.eng, "soul", {})), "council_mandates": getattr(ctx, "council_mandates", []),
            "dream": getattr(ctx, "last_dream", None), "mutated_input": ctx.input_text,})

    @staticmethod
    def _generate_crash_report(e: Exception) -> Dict[str, Any]:
        full_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        safe_phys = PanicRoom.get_safe_physics()
        safe_bio = PanicRoom.get_safe_bio()
        msg = ux("cycle_strings", "orch_reality_fracture")
        ui_report = f"{Prisma.RED}{msg.format(error=e, trace=full_trace)}{Prisma.RST}"
        return {"type": "CRASH", "ui": ui_report, "physics": safe_phys.to_dict(),
            "bio": safe_bio, "mind": PanicRoom.get_safe_mind(),
            "world": {"orbit": ["VOID"],
                "loci_description": "System Failure"},
            "logs": ["CRITICAL FAILURE", "SAFE MODE ACTIVE"],
            "is_alive": True,}
