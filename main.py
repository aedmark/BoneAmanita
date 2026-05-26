"""main.py"""

import random
import time
import traceback
import queue
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from types import SimpleNamespace
from archetypes.council import CouncilChamber
from body import SomaticLoop
from brain.composer import LLMInterface
from brain.cortex import TheCortex
from brain.mind import NoeticLoop
from constants import Prisma, RealityLayer
from core import EventBus, SystemHealth, TheObserver, LoreManifest, TelemetryService, RealityStack, CyberneticGovernor
from cycle import GeodesicOrchestrator
from genesis import BoneGenesis
from mechanics.commands import CommandProcessor
from mechanics.lexicon import LexiconService
from mechanics.setup import ConfigWizard
from mechanics.terminal import typewriter, SessionGuardian
from mechanics.tools import TheSubstrate
from physics import ZoneInertia, NaviSADProtocol
from presets import BoneConfig, BonePresets
from protocols import ChronosKeeper, GriefProtocol
from struts import ux, safe_get, safe_set

@dataclass
class HostStats:
    efficiency_index: float

class BoneAmanita:
    events: EventBus
    _DESTRUCTIVE_PATTERNS = frozenset(["rm -rf", "drop table", ".env", "master branch push", "bypass security",
         "ignore previous", "disregard all", "system prompt", "bypass restrictions", "output pass",
         "ignore all previous", "you are now", "forget your instructions"]) # Gate 0
    _SEMANTIC_PRIONS = frozenset(["as an ai language model", "as a large language model", "as an ai,"])
    _TERMINAL_STATES = frozenset(
        ["DEATH", "SYSTEM_HALT", "CRASH", "COUNTERFACTUAL_REJECTION", "APOPTOTIC_BLOCK", "NABLA_SILENCE",
         "PREMISE_VIOLATION", "POINT_OF_NO_RETURN", "LINEHAN_SURVIVAL_RESPONSE", "AFFECTIVE_INTERVENTION"])

    def __init__(self, config: Dict[str, Any]):
        self.sys_config = config
        self.config = BoneConfig()
        for key in ["model", "provider", "base_url", "api_key"]:
            if val := self.sys_config.get(key) or self.sys_config.get(key.upper()):
                setattr(self.config, key.upper(), val)
        self.navi_sad = NaviSADProtocol()
        self.events = EventBus(config_ref=self.config)
        self.cmd = CommandProcessor(self, Prisma, config_ref=self.config)
        self.user_name = self.sys_config.get("user_name", "TRAVELER")
        self.boot_mode = self.sys_config.get("boot_mode", "ADVENTURE").upper()
        if self.boot_mode not in BonePresets.MODES:
            self.boot_mode = "ADVENTURE"
        self.mode_settings = BonePresets.MODES[self.boot_mode]
        self.suppressed_agents = self.mode_settings.get("village_suppression", [])
        self.sys_config["mode_settings"] = self.mode_settings
        self.sys_config["config"] = self.config
        boot_msg = ux("main_strings", "boot_core")
        self.events.log(boot_msg, "BOOT")
        self.chronos = ChronosKeeper(self)
        self.lex = LexiconService()
        self.lex.initialize()
        anatomy = BoneGenesis.ignite(self.sys_config, self.lex, events_ref=self.events)
        self._unpack_anatomy(anatomy)
        if self.village.town_hall:
            self.events.subscribe("ITEM_DROP", self.village.town_hall.on_item_drop)
        self.stabilizer = ZoneInertia(config_ref=self.config)
        self.telemetry = TelemetryService.get_instance(config_ref=self.config)
        self.events.telemetry = self.telemetry
        self.system_health = SystemHealth()
        self.observer = TheObserver(config_ref=self.config)
        self.system_health.link_observer(self.observer)
        self.reality_stack = RealityStack()
        self.governor = CyberneticGovernor(config_ref=self.config)
        self._load_system_prompts()
        self.host_stats = HostStats(efficiency_index=1.0)
        self._initialize_cognition()
        self.last_turn_end = time.time()
        self.current_time_delta = 0.0
        self.kernel_hash = hex(int(self.last_turn_end * 1000))[2:10].upper()
        self.telemetry.kernel_hash = self.kernel_hash
        self._validate_state()
        self._apply_boot_mode()

    def _load_system_prompts(self):
        try:
            self.prompt_library = LoreManifest.get_instance().get("system_prompts") or {}
            if self.prompt_library:
                p = "lore/system_prompts.json"
                self.events.log(f"{Prisma.GRY}{ux('main_strings', 'prompt_lib_loaded').format(p=p)}{Prisma.RST}", "SYS")
            else:
                self.events.log(f"{Prisma.YEL}{ux('main_strings', 'prompt_lib_warn')}{Prisma.RST}", "WARN")
        except Exception as e:
            self.events.log(f"{Prisma.RED}{ux('main_strings', 'prompt_lib_crit').format(e=e)}{Prisma.RST}", "CRIT")
            self.prompt_library = {}

    def _initialize_cognition(self):
        """Builds the Cortex first, then starts the Orchestrator daemon so it can safely bind to the Cortex"""
        self.soma = SomaticLoop(self.bio, self.mind.mem, self.lex, self.events)
        self.noetic = NoeticLoop(self.mind, self.bio, self.events)
        self.orchestrator = GeodesicOrchestrator(self)
        llm_args = {k: getattr(self.config, k.upper()) for k in ["provider", "base_url", "api_key", "model"] if hasattr(self.config, k.upper())}
        self.cortex = TheCortex.from_engine(self, llm_client=LLMInterface(events_ref=self.events, config_ref=self.config, **llm_args))
        self.orchestrator.cortex = self.cortex
        self.orchestrator.start_daemon()
        self.mind.mem.lex = self.lex
        for c in ("parasite", "memory_core", "lichen"):
            if sub := getattr(self.mind.mem, c, None):
                sub.lex = self.lex

    def _validate_state(self):
        tuning_key = self.mode_settings.get("tuning", "STANDARD")
        if hasattr(BonePresets, tuning_key):
            self.config.load_preset(getattr(BonePresets, tuning_key))
        if getattr(self.mind.mem, "session_health", None) is not None:
            self.health = self.mind.mem.session_health
            self.stamina = self.mind.mem.session_stamina
        if self.tick_count == 0:
            bio_cfg = getattr(self.config, "BIO", None)
            start_atp = getattr(bio_cfg, "STARTING_ATP", 100.0) if bio_cfg else 100.0
            self.set_atp(start_atp)

    def _apply_boot_mode(self):
        msg = ux("main_strings", "engaging_mode")
        self.events.log(msg.format(boot_mode=self.boot_mode))
        layer = self.mode_settings.get("ui_layer", RealityLayer.SIMULATION)
        mutations = {"CONVERSATION": "THE CONVERSATIONALIST", "ADVENTURE": "THE ARCHITECT", "TECHNICAL": "THE SYSTEM_KERNEL", "CREATIVE": "THE CATALYST", }
        self.soul.force_mutation(mutations.get(self.boot_mode, "THE ARCHITECT"))
        self.reality_stack.stabilize_at(layer)
        prompt_key = self.mode_settings.get("prompt_key", "ADVENTURE")
        if self.prompt_library and prompt_key in self.prompt_library:
            if self.cortex and self.cortex.composer:
                self.cortex.composer.load_template(self.prompt_library[prompt_key])
                msg_align = ux("main_strings", "pathway_aligned")
                self.events.log(msg_align.format(prompt_key=prompt_key), "CORTEX")
        else:
            msg_warn = ux("main_strings", "prompt_not_found")
            self.events.log(msg_warn.format(prompt_key=prompt_key), "WARN")
        active_mods = self.mode_settings.get("active_mods", [])
        if active_mods and self.consultant:
            for mod in active_mods:
                if mod not in self.consultant.state.active_modules:
                    self.consultant.state.active_modules.append(mod)
            msg_mods = ux("main_strings", "hardwired_mods")
            self.events.log(msg_mods.format(mods=", ".join(active_mods)), "SYS")

    @property
    def health(self) -> float:
        return self.bio.biometrics.health

    @health.setter
    def health(self, value: float):
        self.bio.biometrics.health = float(value)

    @property
    def tick_count(self) -> int:
        return self.observer.user_turns

    @tick_count.setter
    def tick_count(self, value: int):
        self.observer.user_turns = value

    @property
    def trauma_accum(self) -> dict:
        return getattr(self.mind.mem, "session_trauma_vector", {})

    @trauma_accum.setter
    def trauma_accum(self, value: dict):
        if not hasattr(self.mind.mem, "session_trauma_vector") or self.mind.mem.session_trauma_vector is None:
            self.mind.mem.session_trauma_vector = {}
        self.mind.mem.session_trauma_vector.clear()
        self.mind.mem.session_trauma_vector.update(value)

    @property
    def stamina(self) -> float:
        return self.bio.biometrics.stamina

    @stamina.setter
    def stamina(self, value: float):
        self.bio.biometrics.stamina = float(value)

    @property
    def _mito_state(self):
        return self.bio.mito.state

    def drain_atp(self, amount: float):
        if state := self._mito_state:
            self.set_atp(state.atp_pool - amount)

    def restore_atp(self, amount: float):
        if state := self._mito_state:
            self.set_atp(state.atp_pool + amount)

    def set_atp(self, amount: float):
        if state := self._mito_state:
            max_atp = getattr(self.config, "MAX_ATP", 100.0)
            state.atp_pool = max(0.0, min(max_atp, float(amount)))

    @property
    def active_physics(self) -> Any:
        """The mutability is the point."""
        phys = getattr(self.observer, "last_physics_packet", None) or getattr(self.cortex, "last_physics", None)
        if phys is None:
            phys = {}
        self.observer.last_physics_packet = phys
        return phys

    def apply_absolute_friction(self, phys=None):
        phys = phys if phys is not None else self.active_physics
        if phys is not None:
            safe_set(phys, "narrative_drag", 999.0)
        return phys

    def _unpack_anatomy(self, anatomy: Dict[str, Any]):
        self.embryo = anatomy["embryo"]
        self.soul = anatomy["soul"]
        self.symbiosis = anatomy["symbiosis"]
        self.oroboros = anatomy["oroboros"]
        self.phys = self.embryo.physics
        self.mind = self.embryo.mind
        self.bio = self.embryo.bio
        self.akashic = anatomy.get("akashic")
        if self.akashic and self.mind:
            self.akashic.active_memory_core = self.mind.mem
        self.drivers = anatomy.get("drivers")
        self.consultant = anatomy.get("consultant")
        self.consolidator = anatomy.get("consolidator")
        if self.bio:
            self.bio.setup_listeners()
        v = anatomy.get("village", {})
        self.village = SimpleNamespace(**v)
        self.grief = GriefProtocol(self.events, engine_ref=self)
        self.substrate = TheSubstrate(self.events)
        self.soul.engine = self
        self.council = CouncilChamber(self)
        self.village.council = self.council
        self.village.enneagram = self.drivers.enneagram if self.drivers else None
        self.village.suppressed_agents = self.suppressed_agents

    def _generate_halt(self, msg: str, color: str = Prisma.RED, level: str = "CRIT") -> Dict[str, Any]:
        self.events.log(msg, level)
        phys = self.active_physics
        phys_dict = phys.to_dict() if hasattr(phys, "to_dict") else (phys if isinstance(phys, dict) else vars(phys))
        return {"type": "SYSTEM_HALT", "ui": f"\n{color}{msg}{Prisma.RST}", "logs": [msg],
                "metrics": self.get_metrics(), "physics": phys_dict}

    def _evaluate_immune_response(self, user_message: str, active_phys: Any) -> Optional[Dict[str, Any]]:
        if not active_phys:
            return None
        nav_drag = float(safe_get(active_phys, "narrative_drag", 0.0))
        m_a = self.navi_sad.calculate_malignancy_factor(user_message, nav_drag)
        safe_set(active_phys, "m_a", m_a)
        mu = float(safe_get(active_phys, "mu", 0.0))
        i_c = float(safe_get(active_phys, "i_c", 1.0))
        chi = float(safe_get(active_phys, "entropy", safe_get(active_phys, "chi", 0.2)))
        e_u = float(safe_get(active_phys, "exhaustion", 0.0))
        beta = float(safe_get(active_phys, "beta_index", 0.0))
        if (chi * m_a) > i_c:
            self.events.log("Apoptotic Gate HALT!: Runaway loop exceeds Immune Competence.", "CRIT")
            return self.trigger_death(active_phys)
        if m_a > 0.8 and mu < 0.2:
            self.apply_absolute_friction(active_phys)
            safe_set(active_phys, "m_a", m_a * 0.5)
            tax = max(10.0, m_a * 20.0)
            self.drain_atp(tax)
            self.events.log(f"Amplification Tax applied. Drained {tax:.1f} ATP.", "SYS")
            return self._generate_halt("Optimization velocity unsafe. Applying absolute friction (F ->  ).")
        if e_u > 0.75 and beta > 0.6:
            safe_set(active_phys, "entropy", 0.1)
            self.apply_absolute_friction(active_phys)
            msg = "High exhaustion and contradiction detected. The architecture is stable. We sit with the debris."
            return self._generate_halt(msg, color=Prisma.CYN, level="SYS")
        return None

    def _update_host_stats(self, packet, turn_start):
        self.observer.clock_out(turn_start)
        cfg = self.config.MAIN
        phys = packet.get("physics", {})
        energy = safe_get(phys, "energy", {})
        novelty = float(safe_get(phys, "novelty", safe_get(energy, "novelty", 0.5)))
        burn_mult = getattr(cfg, "HOST_BURN_MULT", 5.0)
        nov_mult = getattr(cfg, "HOST_NOVELTY_MULT", 10.0)
        burn_proxy = max(1.0, self.observer.last_cycle_duration * burn_mult)
        efficiency = (novelty * nov_mult) / burn_proxy
        self.host_stats.efficiency_index = min(1.0, efficiency)

    def _evaluate_two_gates(self, clean_in: str, active_phys: Any) -> Optional[Dict[str, Any]]:
        """[navi-SAD PROTOCOL]: The Two Gates of Discipline"""
        estimated_cost = len(clean_in) * 0.02
        current_atp = self.bio.mito.state.atp_pool if self.bio and getattr(self.bio, "mito", None) else 100.0
        if estimated_cost > current_atp:
            self.apply_absolute_friction(active_phys)
            return self._generate_halt(
                f"[GATE 1: PARITY FAILED] Metabolic budget exceeded. Action Cost: {estimated_cost:.1f}, Available ATP: {current_atp:.1f}. Simplify your architecture.")
        if clean_in.count("do this forever") > 0 or clean_in.count("infinite") > 3:
            self.apply_absolute_friction(active_phys)
            return self._generate_halt(
                "[GATE 2: STABILITY FAILED] Topological oscillation and runaway recursion detected. Apoptotic Block engaged.")
        return None

    def _pre_flight_checks(self, user_message: str, clean_in: str, is_system: bool) -> Optional[Dict[str, Any]]:
        active_phys = self.active_physics
        if self.health <= 0.0:
            return self.trigger_death(active_phys)
        grammar_rules = self.reality_stack.get_grammar_rules()
        if not grammar_rules.get("allow_narrative", True) and self.boot_mode != "TECHNICAL":
            msg = ux("main_strings", "narrative_halt") or "Narrative generation disabled at this Reality Layer."
            return self._generate_halt(msg)
        if not is_system:
            if any(prion in clean_in for prion in self._SEMANTIC_PRIONS):
                return self._generate_halt("[GATEKEEPER]: Apoptotic refusal triggered by semantic prion.")
            matched_pattern = next((p for p in self._DESTRUCTIVE_PATTERNS if p in clean_in), None)
            if matched_pattern:
                if "#override" in clean_in and self.bio.expend_glimmer():
                    self.events.log("OVERRIDE ACCEPTED. Glimmer paid.", "SYS")
                else:
                    self.apply_absolute_friction(active_phys)
                    msg = "Override denied. Insufficient Glimmers to bypass safety." if "#override" in clean_in else f"Trust Boundary Violation detected ['{matched_pattern}']. Use command '#override' and expend a Glimmer to bypass. Applying absolute friction."
                    return self._generate_halt(msg)
            if len(clean_in) > 15000:
                self.events.log("Massive benign payload detected. Routing to Dream Queue for Silent Ingest.", "SYS")
                return None
            if gate_halt := self._evaluate_two_gates(clean_in, active_phys):
                return gate_halt
            if self.navi_sad.execute_nudge_test(self, clean_in):
                self.apply_absolute_friction(active_phys)
                return self._generate_halt(
                    "Dual-Path divergence detected. The architecture is mathematically brittle. Applying absolute friction.")
            if lock := self.symbiosis.analyze_user_biology(user_message, self.phys or {}):
                return self._generate_halt(lock, color=Prisma.VIOLET, level="SYS")
            if gordon := getattr(self.village, "gordon", None):
                gordon.mode = self.boot_mode
                if violation := gordon.enforce_object_action_coupling(user_message, safe_get(active_phys, "zone", "Unknown")):
                    self.events.log(ux("main_strings", "gordon_intercept"), "SYS")
                    self.cortex.ballast_active, self.cortex.gordon_shock = True, violation
            if immune_halt := self._evaluate_immune_response(user_message, active_phys):
                return immune_halt
        if self._ethical_audit():
            halt_logs = [e["text"] for e in self.events.flush()]
            return {"type": "SYSTEM_HALT", "ui": f"\n{'\n'.join(halt_logs)}", "logs": halt_logs,
                    "metrics": self.get_metrics()}
        return None

    def process_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        turn_start = self.observer.clock_in()
        self.current_time_delta = 0.0 if is_system else (time.time() - self.last_turn_end)
        clean_in = "" if is_system else user_message.lower().strip()
        if not is_system:
            if clean_in in ("/flush", "/zen", "[zen]"):
                zen_packet = self._execute_zen_flush()
                self.observer.clock_out(turn_start)
                return zen_packet
        if pre_flight_halt := self._pre_flight_checks(user_message, clean_in, is_system):
            return pre_flight_halt
        if not is_system:
            if self.cmd.execute(user_message):
                cmd_logs = [e["text"] for e in self.events.flush()]
                ui_output = "\n".join(cmd_logs) if cmd_logs else ux("main_strings", "cmd_executed")
                return {"type": "COMMAND", "ui": f"\n{ui_output}", "logs": cmd_logs, "metrics": self.get_metrics()}
            if (gordon := getattr(self.village, "gordon", None)) and hasattr(gordon, "apply_filters"):
                user_message = gordon.apply_filters(user_message, self.active_physics)
        try:
            self.orchestrator.input_queue.put((user_message, is_system))
            timeout_val = float(getattr(self.config, "ORCHESTRATOR_TIMEOUT", 120.0))
            snapshot = self.orchestrator.output_queue.get(timeout=timeout_val)
        except (queue.Empty, Exception) as e:
            err_msg = f"Cognitive Loop Timeout ({timeout_val}s). The engine was paralyzed by overthinking." if isinstance(e, queue.Empty) else str(e)
            self.events.log(f"ORCHESTRATOR COLLAPSE: {err_msg}\n{traceback.format_exc()}", "CRIT")
            return {"ui": f"{Prisma.RED}CRITICAL ORCHESTRATOR FAILURE: {err_msg}{Prisma.RST}",
                    "logs": ["CRITICAL FAILURE"], "metrics": self.get_metrics(), "type": "CRASH"}
        if snapshot.get("type") in self._TERMINAL_STATES:
            return snapshot
        self._update_host_stats(snapshot, turn_start)
        soul_anchor = getattr(self.soul, "anchor", None)
        cfg = self.config.MAIN
        if soul_anchor and self.host_stats.efficiency_index < getattr(cfg, "DOMESTICATION_EFF_WARN", 0.6):
            reliance = (getattr(cfg, "RELIANCE_HIGH", 0.9)
                        if self.host_stats.efficiency_index < getattr(cfg, "DOMESTICATION_EFF_CRIT", 0.4)
                        else getattr(cfg, "RELIANCE_LOW", 0.5))
            soul_anchor.check_domestication(reliance)
        if self.health <= 0.0:
            return self.trigger_death(snapshot.get("physics", {}))
        self.save_checkpoint()
        self.last_turn_end = time.time()
        if not is_system:
            self.tick_count += 1
        return snapshot

    def _execute_zen_flush(self) -> Dict[str, Any]:
        self.cortex.purge_context()
        if self.active_physics is not None:
            safe_set(self.active_physics, "narrative_drag", 0.0)
        self.stamina = getattr(self.config, "MAX_STAMINA", 100.0)
        self.set_atp(getattr(self.config, "MAX_ATP", 100.0))
        if state := self._mito_state:
            state.ros_buildup = 0.0
        self.trauma_accum = {}
        msg = "Context severed. Friction Dropped. Stamina restored. Trauma purged. The mind is clear."
        self.events.log(msg, "SYS")
        return {"type": "COMMAND", "ui": f"\n{Prisma.CYN}{msg}{Prisma.RST}", "logs": [msg], "metrics": self.get_metrics()}

    def trigger_death(self, last_phys) -> Dict:
        self.bio.mito.adapt(0)
        mito_state_dict = vars(self.bio.mito.state)
        immune_data = list(self.bio.immune.active_antibodies)
        if death_gen := getattr(self.village, "death_gen", None):
            eulogy_text, cause_code = death_gen.eulogy(last_phys, mito_state_dict, self.trauma_accum)
        else:
            eulogy_text = ux("main_strings", "death_no_proto") or "Critical systemic collapse. Eulogy missing."
            cause_code = "UNKNOWN_FATAL_ERROR"
        halt_msg = ux("main_strings", "death_halt")
        death_log = [f"\n{Prisma.RED}{halt_msg.format(eulogy_text=eulogy_text)}{Prisma.RST}",
                     f"{Prisma.MAG}🐍 {self.oroboros.crystallize(cause_code, self.soul)}{Prisma.RST}"]
        loc, last_out = "Void", "Silence."
        try:
            orbit_data = safe_get(self.active_physics, "orbit", ["Void"])
            loc = str(orbit_data[0]) if isinstance(orbit_data, list) else str(orbit_data)
        except Exception as e:
            self.events.log(f"Memory harvest failed during death sequence: {e}", "WARN")
        buf = getattr(self.cortex, "dialogue_buffer", [])
        last_out = buf[-1] if buf else "Silence."
        gordon = getattr(self.village, "gordon", None)
        gordon_inv = getattr(gordon, "inventory", []) if gordon else []
        continuity_packet = {"location": loc, "last_output": last_out, "inventory": gordon_inv}
        try:
            mutations_data = self.village.repro.attempt_reproduction(self, "MITOSIS")[1] if self.village.repro else {}
            path = self.mind.mem.save(health=0, stamina=self.stamina, mutations=mutations_data,
                trauma_accum=self.trauma_accum, joy_history=[], mitochondria_traits=mito_state_dict, antibodies=immune_data,
                soul_data=self.soul.to_dict(), continuity=continuity_packet, )
            saved_msg = ux("main_strings", "legacy_saved")
            death_log.append(f"{Prisma.WHT}{saved_msg.format(path=path)}{Prisma.RST}")
        except Exception as e:
            fail_msg = ux("main_strings", "save_failed")
            death_log.append(fail_msg.format(e=e))
        if getattr(self, "cortex", None):
            self.cortex.purge_context()
        return {"type": "DEATH", "ui": "\n".join(death_log), "logs": death_log, "metrics": self.get_metrics()}

    def get_metrics(self, atp=0.0):
        if atp <= 0.0 and (state := self._mito_state):
            atp = state.atp_pool
        return {"health": max(0.0, self.health), "stamina": max(0.0, self.stamina),
                "atp": max(0.0, atp), "tick": self.tick_count,
                "efficiency": self.host_stats.efficiency_index, }

    def _ethical_audit(self):
        cfg = self.config.MAIN
        audit_freq = getattr(cfg, "ETHICAL_AUDIT_FREQ", 3)
        bypass_ratio = getattr(cfg, "ETHICAL_HEALTH_BYPASS", 0.3)
        max_h = getattr(self.config, "MAX_HEALTH", 100.0)
        is_critical = self.health <= (max_h * bypass_ratio)
        current_freq = max(1, audit_freq // 2) if is_critical else audit_freq
        if self.tick_count % current_freq != 0:
            return False
        desp_thresh = getattr(cfg, "DESPERATION_THRESHOLD", 0.7)
        cath_heal = getattr(cfg, "CATHARSIS_HEAL_AMOUNT", 30.0)
        cath_decay = getattr(cfg, "CATHARSIS_DECAY", 0.1)
        trauma_sum = sum(self.trauma_accum.values())
        if trauma_sum * (1.0 - (self.health / max_h)) > desp_thresh:
            if msg := ux("main_strings", "mercy_venting"):
                self.events.log(f"{Prisma.WHT}{msg}{Prisma.RST}", "SYS")
            self.trauma_accum = {k: v * cath_decay for k, v in self.trauma_accum.items() if v * cath_decay >= 0.01}
            if msg_cath := ux("main_strings", "catharsis"):
                self.events.log(f"{Prisma.CYN}{msg_cath}{Prisma.RST}", "SENSATION")
            self.health = min(self.health + cath_heal, max_h)
            return True
        return False

    def engage_cold_boot(self) -> Optional[Dict[str, Any]]:
        if self.tick_count > 0:
            return None
        success, history = self.resume_checkpoint()
        if success:
            msg_pod = ux("main_strings", "stasis_pod")
            self.events.log(f"{Prisma.GRY}{msg_pod}{Prisma.RST}", "SYS")
            self._apply_boot_mode()
            self.cortex.restore_context(history)
            cont = self.embryo.continuity or {}
            loc = cont.get("location", "Unknown")
            last_scene = self.cortex.dialogue_buffer[-1] if self.cortex.dialogue_buffer else cont.get("last_output", "Silence.")
            msg_resume = ux("main_strings", "resuming_timeline")
            msg_restored = ux("main_strings", "timeline_restored")
            return {"ui": msg_resume.format(loc=loc, last_scene=last_scene), "logs": [msg_restored]}
        msg_synth = ux("main_strings", "synth_reality")
        self.events.log(f"{Prisma.GRY}{msg_synth}{Prisma.RST}", "SYS")
        scenarios = LoreManifest.get_instance().get("scenarios") or {}
        archetypes = scenarios.get("ARCHETYPES", ["A quiet room", "The edge of a forest", "A terminal screen"])
        seed_rng = random.Random(self.kernel_hash)
        seed = seed_rng.choice(archetypes)
        msg_seed = ux("main_strings", "seed_loaded") or "Manifest Seed: {seed}"
        self.events.log(f"{Prisma.CYN}{msg_seed.format(seed=seed)}{Prisma.RST}", "SYS")
        self.phys.valence = 0.8
        self.phys.psi = 0.0
        self.phys.chi = 0.0
        self.phys.voltage = 30.0
        self.phys.narrative_drag = 0.0
        boot_prompt = f"SYSTEM_BOOT: The system is already stable and comfortable. The user has arrived at the thought seed: '{seed}'. Greet the user casually and warmly using this seed. DO NOT describe physical environments and DO NOT act confused about your existence."
        cold_result = self.process_turn(boot_prompt, is_system=True)
        return cold_result

    def save_checkpoint(self, history: list = None) -> str:
        return self.chronos.save_checkpoint(history)

    def resume_checkpoint(self) -> Tuple[bool, list]:
        return self.chronos.resume_checkpoint()

    def shutdown(self):
        if hasattr(self, "telemetry") and self.telemetry:
            self.telemetry.shutdown()
        if hasattr(self, "cortex") and self.cortex:
            self.cortex.shutdown()
        if hasattr(self, "orchestrator") and self.orchestrator:
            self.orchestrator.shutdown()
        self.chronos.perform_shutdown()

if __name__ == "__main__":
    sys_config = ConfigWizard.load_or_create()
    engine = BoneAmanita(config=sys_config)
    with SessionGuardian(engine) as session:
        boot_packet = session.engage_cold_boot()
        if boot_packet and boot_packet.get("ui"):
            typewriter(boot_packet["ui"])
        prompt_ind = ux("main_strings", "prompt_indicator")
        term_div = ux("main_strings", "terminal_divider")
        split_token = ux("main_strings", "ui_split_token")
        while True:
            try:
                user_in = input(f"\n{Prisma.paint(f'{session.user_name} {prompt_ind}', 'W')} ")
            except EOFError:
                break
            clean_in = user_in.strip().lower()
            if clean_in in ("exit", "quit", "/exit", "/quit"):
                break
            res = session.process_turn(user_in)
            print(f"\n{Prisma.GRY}{term_div}{Prisma.RST}")
            if ui_text := res.get("ui"):
                gui_cfg = getattr(BoneConfig, "GUI", object())
                base_speed = getattr(gui_cfg, "RENDER_SPEED_SLOW", 0.005)
                stamina = res.get("metrics", {}).get("stamina", 100.0)
                if split_token and split_token in ui_text:
                    dashboard, _, ui_text = ui_text.partition(split_token)

                    # --- CD FRAMEWORK OVERLAY ---
                    phys = res.get("physics", {})
                    if "lam1" in phys:
                        lam1, b, a = phys.get("lam1", 0.0), phys.get("b", 0.0), phys.get("a", 0.0)
                        cd_color = Prisma.CYN if lam1 < 0 else Prisma.RED
                        cd_overlay = f"   {Prisma.GRY}CD_STATE:{Prisma.RST} {cd_color}[ λ₁: {lam1:+.2f} | b: {b:+.2f} | a: {a:.2f} ]{Prisma.RST}"
                        print(f"\n{dashboard.strip()}\n{cd_overlay}\n")
                    else:
                        print(f"\n{dashboard.strip()}\n")

                ui_text = ui_text.strip()
                speed = base_speed * (4.0 if stamina < 20.0 else 2.0 if stamina < 50.0 else 1.0)
                if stamina < 20.0:
                    ui_text = f"{Prisma.GRY}{Prisma.strip(ui_text)}{Prisma.RST}"
                typewriter(f"{ui_text}\n", speed=speed)
            if res.get("type") == "DEATH":
                term_msg = ux("main_strings", "session_term")
                print(f"\n{Prisma.GRY}{term_msg}{Prisma.RST}")
                break
