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
)
from bone_physics import CycleStabilizer
from bone_presets import BoneConfig
from bone_symbiosis import SymbiosisManager
from bone_types import Prisma, CycleContext


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
        breakers = {"OBSERVE": h.physics_online, "METABOLISM": h.bio_online, "COGNITION": h.mind_online}
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
        if comp == "PHYSICS":
            ctx.physics = PanicRoom.get_safe_physics()
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
