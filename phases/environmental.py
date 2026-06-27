"""phases/environmental.py"""

import random

from constants import Prisma
from core import CycleContext, LoreManifest
from mechanics.tools import TheTclWeaver
from phases.base import SimulationPhase, _deep_update, _safe_dict
from physics import QuantumObserver
from presets import BonePresets
from struts import safe_get, safe_set, ux


class NavigationPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "NAVIGATION"

    def run(self, ctx: CycleContext):
        physics = ctx.physics
        mode_settings = self.eng.mode_settings
        is_fresh_boot = len(self.eng.cortex.dialogue_buffer) == 0
        if is_fresh_boot:
            ctx.log(
                f"{Prisma.MAG}[NAVIGATION]: Fresh boot detected. Bypassing Orthogonal Attention Loss. Orienting to JSON bedrock.{Prisma.RST}"
            )
            physics.narrative_drag = max(0.1, physics.narrative_drag * 0.1)
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
        gordon_ref = getattr(self.eng.village, "gordon", None)
        if gordon_ref:
            phys_snapshot = _safe_dict(physics)
            reflex_triggered, reflex_msg = gordon_ref.emergency_reflex(phys_snapshot)
            if reflex_triggered:
                _deep_update(physics, phys_snapshot)
                if reflex_msg:
                    ctx.log(reflex_msg)
                ctx.record_flux("NAVIGATION", "REFLEX", 1.0, 0.0, "ITEM_TRIGGERED")
        phys_dict = _safe_dict(physics)
        navigator_ref = getattr(self.eng.village, "navigator", None)
        if navigator_ref:
            current_loc, entry_msg = navigator_ref.locate(
                packet=ctx.physics,
            )
            if entry_msg:
                ctx.log(entry_msg)
            env_logs = navigator_ref.apply_environment(physics)
            for e_log in env_logs:
                ctx.log(e_log)
        tinkerer_ref = getattr(self.eng.village, "tinkerer", None)
        if gordon_ref and tinkerer_ref:
            inv_data = gordon_ref.get_inventory_data()
            deltas = tinkerer_ref.calculate_passive_deltas(inv_data)
            for delta in deltas:
                if delta.field == "narrative_drag":
                    if delta.operator == "ADD":
                        physics.narrative_drag += delta.value
                    elif delta.operator == "MULT":
                        physics.narrative_drag *= delta.value
                    msg = ux("cycle_strings", "nav_gear_drag")
                    ctx.log(
                        f"{Prisma.GRY}{msg.format(source=delta.source, operator=delta.operator, value=delta.value)}{Prisma.RST}"
                    )
        clean_words_safe = ctx.clean_words if ctx.clean_words else ["boot_sequence"]
        orbit_state, drag_pen, orbit_msg = self.eng.phys.dynamics.analyze_orbit(
            self.eng.mind.mem, clean_words_safe
        )
        if orbit_msg:
            ctx.log(orbit_msg)
        physics.narrative_drag += drag_pen
        if orbit_state == "VOID_DRIFT" and ctx.clean_words:
            physics.voltage = max(
                0.0, physics.voltage - ctx.limits.get("NAV_VOID_PENALTY", 0.5)
            )
        elif orbit_state == "LAGRANGE_POINT":
            physics.narrative_drag = max(
                0.1, physics.narrative_drag - ctx.limits.get("NAV_LAGRANGE_RELIEF", 2.0)
            )
        elif orbit_state == "WATERSHED_FLOW":
            physics.voltage += ctx.limits.get("NAV_WATERSHED_BOOST", 0.5)
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


class RealityFilterPhase(SimulationPhase):
    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "REALITY_FILTER"
        self.trigrams = (
            LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TRIGRAM_MAP") or {}
        )

    def run(self, ctx: CycleContext):
        vector = ctx.physics.vector
        sufficient_mass = len(ctx.clean_words) >= 3
        sufficient_tension = getattr(ctx.physics, "voltage", 0.0) >= 5.0
        if vector and (
            sufficient_mass or sufficient_tension or "trigram" not in ctx.world_state
        ):
            dom = max(vector, key=vector.get)
            entry = self.trigrams.get(
                dom, self.trigrams.get("E", ["?", "UNKNOWN", "Unknown", "GRY"])
            )
            sym, name, _, color_attr = entry
            color = getattr(Prisma, color_attr, Prisma.GRY)
            ctx.world_state["trigram"] = {"symbol": sym, "name": name, "color": color}
            if random.random() < 0.05:
                msg = ux("cycle_strings", "filter_iching")
                ctx.log(f"{color}{msg.format(sym=sym, name=name)}{Prisma.RST}")
        return ctx


class ObservationPhase(SimulationPhase):
    _SYNC_KEYS = (
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
    )

    def __init__(self, engine_ref):
        super().__init__(engine_ref)
        self.name = "OBSERVE"

    def run(self, ctx: CycleContext):
        if ctx.time_delta > 10.0 and not ctx.is_system_event and ctx.physics:
            if nabla_msg := QuantumObserver.evaluate_silence(
                ctx.time_delta, ctx.physics
            ):
                ctx.log(f"{Prisma.GRY}*... {nabla_msg} ...*{Prisma.RST}")
            if ctx.time_delta > 600.0:
                hours_passed = min(24.0, ctx.time_delta / 3600.0)
                target_cfg = self.eng.config
                self.eng.health = min(
                    float(safe_get(target_cfg, "MAX_HEALTH", 100.0)),
                    self.eng.health + (hours_passed * 10.0),
                )
                self.eng.restore_atp(hours_passed * 25.0)
                ctx.log(
                    f"{Prisma.GRN}[BIO]: Retroactive metabolism applied for {hours_passed:.1f} hours of absence. ATP and Health restored.{Prisma.RST}"
                )
                dream_engine = self.eng.mind.dreamer
                if dream_engine:
                    soul_snap = _safe_dict(self.eng.soul)
                    bio_packet = {
                        "chem": self.eng.bio.endo.get_state(),
                        "mito": {
                            "atp": self.eng.bio.mito.state.atp_pool,
                            "ros": self.eng.bio.mito.state.ros_buildup,
                        },
                    }
                    dream_text, shift = dream_engine.enter_rem_cycle(
                        soul_snap, bio_state=bio_packet
                    )
                    if dream_text:
                        ctx.log(
                            f"{Prisma.VIOLET}☁While you were gone: {dream_text}{Prisma.RST}"
                        )
                        ctx.last_dream = {
                            "log": dream_text,
                            "source": "RETROACTIVE_SLEEP",
                        }
                    if hours_passed > 4.0:
                        defrag_msg = dream_engine.run_defragmentation(self.eng.mind.mem)
                        if defrag_msg:
                            ctx.log(f"{Prisma.CYN}🧹 {defrag_msg}{Prisma.RST}")
        gordon_ref = getattr(self.eng.village, "gordon", None)
        if (
            gordon_ref
            and "GORDON" not in self.eng.suppressed_agents
            and not ctx.is_system_event
        ):
            if "TCL9_QUANTUM_COMB" in gordon_ref.inventory:
                weaver = TheTclWeaver.get_instance()
                original_text = ctx.input_text
                current_chi = float(
                    safe_get(ctx.physics, "entropy", safe_get(ctx.physics, "chi", 0.5))
                )
                ctx.input_text = weaver.quantum_comb(ctx.input_text, chi=current_chi)
                if original_text != ctx.input_text:
                    ctx.log(
                        f"{Prisma.CYN}🪮 QUANTUM COMB: Fluff stripped -> '{ctx.input_text}'{Prisma.RST}"
                    )
            container_handled = False
            if hasattr(gordon_ref, "process_container_commands"):
                container_logs, container_handled = (
                    gordon_ref.process_container_commands(ctx.input_text)
                )
                for c_log in container_logs:
                    ctx.log(c_log)
            if not container_handled:
                loot_candidate = gordon_ref.parse_loot(ctx.input_text, "")
                if loot_candidate:
                    acquire_msg = gordon_ref.acquire(loot_candidate)
                    ctx.log(acquire_msg)
        gaze_result = self.eng.phys.observer.gaze(
            ctx.input_text, self.eng.mind.mem.graph
        )
        input_phys = gaze_result["physics"]
        ctx.clean_words = gaze_result["clean_words"]

        echo = (
            getattr(self.eng.bio.somatic, "somatic_echo", 0.0)
            if hasattr(self.eng, "bio") and hasattr(self.eng.bio, "somatic")
            else 0.0
        )
        if echo > 0.05:
            ctx.log(
                f"{Prisma.RED}Somatic Echo active ({echo:.2f}). Perception blurred by residual shock.{Prisma.RST}"
            )
            input_phys["entropy"] = min(1.0, input_phys.get("entropy", 0.0) + echo)
            input_phys["narrative_drag"] = input_phys.get("narrative_drag", 0.0) + (
                echo * 5.0
            )

            if ctx.clean_words:
                drop_count = int(len(ctx.clean_words) * echo)
                for _ in range(drop_count):
                    ctx.clean_words.pop(random.randrange(len(ctx.clean_words)))

        for k in self._SYNC_KEYS:
            if (val := input_phys.get(k)) is not None:
                setattr(ctx.physics, k, val)
        observed_voltage = input_phys.get("voltage", 0.0)
        if observed_voltage > 0:
            ctx.physics.voltage += observed_voltage * 0.5
        current_drag = max(0.1, getattr(ctx.physics, "narrative_drag", 0.1))
        input_drag = input_phys.get("narrative_drag", 0.0)
        ctx.physics.narrative_drag = (current_drag * 0.7) + (input_drag * 0.3)
        current_atp = self.eng.bio.mito.state.atp_pool
        atp_warn = ctx.limits.get("OBSERVE_ATP_WARN", 15.0)
        if current_atp < atp_warn:
            msg = ux("cycle_strings", "observe_low_energy")
            ctx.log(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
        diag = self.eng.symbiosis.current_health.diagnosis
        if diag != "STABLE":
            msg = ux("cycle_strings", "observe_symbiont")
            ctx.log(f"{Prisma.OCHRE}{msg.format(diag=diag)}{Prisma.RST}")
        if self.eng.shared_lattice and not ctx.is_system_event:
            shared_logs, atp_cost = self.eng.shared_lattice.infer_and_couple(
                text=ctx.input_text,
                sys_phys=ctx.physics,
                input_phys=input_phys,
                atp_pool=current_atp,
            )
            for s_log in shared_logs:
                ctx.log(s_log)
            if atp_cost > 0:
                self.eng.bio.mito.adjust_atp(
                    -atp_cost, "Carrier Mode (System lent stamina to User)"
                )
        self.eng.phys.dynamics.commit(ctx.physics.voltage)
        return ctx


class SanctuaryPhase(SimulationPhase):
    def __init__(self, engine_ref, governor_ref):
        super().__init__(engine_ref)
        self.name = "SANCTUARY"

    @property
    def bio_governor(self):
        return self.eng.bio.governor

    def run(self, ctx: CycleContext):
        in_safe_zone, distance = self.bio_governor.assess(ctx.physics)
        trauma_sum = sum(getattr(self.eng, "trauma_accum", {}).values())
        t_limit = ctx.limits.get("SANCTUARY_TRAUMA_LIMIT", 25.0)
        if in_safe_zone and trauma_sum < t_limit:
            self._enter_sanctuary(ctx)
            self._apply_restoration(ctx)
            self._trigger_dream(ctx)
        return ctx

    @staticmethod
    def _enter_sanctuary(ctx: CycleContext):
        ctx.physics.zone = getattr(BonePresets.SANCTUARY, "ZONE", "SANCTUARY")
        ctx.physics.zone_color = getattr(BonePresets.SANCTUARY, "COLOR_NAME", "GRN")
        ctx.physics.flow_state = "LAMINAR"
        if random.random() < 0.1:
            color = getattr(BonePresets.SANCTUARY, "COLOR", Prisma.GRN)
            msg = ux("cycle_strings", "sanctuary_breathe")
            ctx.log(f"{color}{msg}{Prisma.RST}")

    def _apply_restoration(self, ctx: CycleContext):
        for log in self.eng.bio.rest(factor=1.0):
            ctx.log(log)
        for key in list(self.eng.trauma_accum.keys()):
            self.eng.trauma_accum[key] -= 0.1
            if self.eng.trauma_accum[key] <= 0.0:
                del self.eng.trauma_accum[key]

    def _trigger_dream(self, ctx: CycleContext):
        if not self.eng.mind.dreamer:
            return
        if getattr(self.eng, "tick_count", 0) <= 2 or random.random() > 0.15:
            return
        if hasattr(self.eng, "akashic") and hasattr(self.eng.akashic, "replay_dreams"):
            if dream_log := self.eng.akashic.replay_dreams():
                ctx.log(f"{Prisma.VIOLET}{dream_log}{Prisma.RST}")
        current_trauma_load = sum(self.eng.trauma_accum.values())
        bio_packet = {
            "chem": self.eng.bio.endo.get_state(),
            "mito": {
                "atp": self.eng.bio.mito.state.atp_pool,
                "ros": self.eng.bio.mito.state.ros_buildup,
            },
            "physics": _safe_dict(ctx.physics),
            "trauma_vector": current_trauma_load,
        }
        soul_snapshot = _safe_dict(getattr(self.eng, "soul", {}))
        dream_packet = self.eng.mind.dreamer.enter_rem_cycle(
            soul_snapshot, bio_state=bio_packet
        )
        dream_text_to_archive = None
        if isinstance(dream_packet, dict):
            dream_text_to_archive = dream_packet.get("log", "The mind wanders...")
            ctx.log(dream_text_to_archive)
            ctx.last_dream = dream_packet
        elif isinstance(dream_packet, tuple):
            log_msg, effects = dream_packet
            dream_text_to_archive = log_msg
            ctx.log(f"{Prisma.VIOLET}  {log_msg}{Prisma.RST}")
            ctx.last_dream = {"log": log_msg, "effects": effects}
            if hasattr(effects, "get"):
                if adr := effects.get("adrenaline"):
                    self.eng.bio.endo.adrenaline = max(
                        0.0, self.eng.bio.endo.adrenaline + adr
                    )
                if cor := effects.get("cortisol"):
                    self.eng.bio.endo.cortisol = max(
                        0.0, self.eng.bio.endo.cortisol + cor
                    )
                if v := effects.get("voltage"):
                    ctx.physics.voltage = max(0.0, ctx.physics.voltage + v)
                if (g := effects.get("glimmers")) and g > 0:
                    self.eng.shared_lattice.shared.g_pool += g
                    ctx.log(
                        f"{Prisma.MAG}The dream yielded a Glimmer (+{g} G_pool).{Prisma.RST}"
                    )
        if (
            dream_text_to_archive
            and hasattr(self.eng, "akashic")
            and hasattr(self.eng.akashic, "archive_dream")
        ):
            clean_dream = Prisma.strip(dream_text_to_archive)
            self.eng.akashic.archive_dream(clean_dream)
