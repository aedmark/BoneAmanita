"""main.py
The Macro-Organism and Central Orchestrator.
This file contains the primary BoneAmanita engine loop that binds the physical,
biological, and cognitive layers into a single continuous state machine.
"""

import os
import time
import random
import traceback
import uuid
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from body import SomaticLoop
from brain.cortex import TheCortex
from brain.mind import NoeticLoop
from brain.composer import LLMInterface
from mechanics.commands import CommandProcessor
from presets import BoneConfig, BonePresets
from core import EventBus, SystemHealth, TheObserver, LoreManifest, TelemetryService, RealityStack, CyberneticGovernor
from struts import ux, safe_get, safe_set
from archetypes.council import CouncilChamber
from cycle import GeodesicOrchestrator
from genesis import BoneGenesis
from mechanics.lexicon import LexiconService
from physics import ZoneInertia, NaviSADProtocol
from protocols import ChronosKeeper
from constants import Prisma, RealityLayer
from mechanics.terminal import typewriter, SessionGuardian
from mechanics.setup import ConfigWizard


@dataclass
class HostStats:
    """Tracks the latency and metabolic efficiency of the local hardware."""
    latency: float
    efficiency_index: float


class BoneAmanita:
    """
    The central intelligence of the hypervisor.
    This class holds the spatial geometry together. It maintains the
    references to the Mind (Cortex), Body (Soma), and Village, ensuring they all
    process the same reality frames in sync.
    """
    events: EventBus
    _DESTRUCTIVE_PATTERNS = ("rm -rf", "drop table", ".env", "master branch push", "bypass security",
                             "ignore previous", "disregard all", "system prompt", "bypass restrictions", "output pass")
    _SEMANTIC_PRIONS = ("as an ai language model", "as a large language model", "as an ai,")
    _SMALL_MODEL_INDICATORS = ("7b", "8b", "9b", "11b", "12b", "14b", "mini", "lite", "flash")

    def __init__(self, config: Dict[str, Any]):
        self.sys_config = config
        self.config = BoneConfig()
        self.navi_sad = NaviSADProtocol()
        self.events = EventBus(config_ref=self.config)
        self.kernel_hash = str(uuid.uuid4())[:8].upper()
        self.cmd = CommandProcessor(self, Prisma, config_ref=self.config)
        self.user_name = self.sys_config.get("user_name", "TRAVELER")
        self.boot_mode = self.sys_config.get("boot_mode", "ADVENTURE").upper()
        if self.boot_mode not in BonePresets.MODES:
            self.boot_mode = "ADVENTURE"
        self.mode_settings = BonePresets.MODES[self.boot_mode]
        self.suppressed_agents = self.mode_settings.get("village_suppression", [])
        self.sys_config["mode_settings"] = self.mode_settings
        self.sys_config["config"] = self.config
        self._health_fallback = self.config.MAX_HEALTH
        self._stamina_fallback = self.config.MAX_STAMINA
        self.trauma_accum = {}
        self.tick_count = 0
        boot_msg = ux("main_strings", "boot_core")
        self.events.log(boot_msg, "BOOT")
        self.chronos = ChronosKeeper(self)
        self.lex = LexiconService()
        self.lex.initialize()
        anatomy = BoneGenesis.ignite(self.sys_config, self.lex, events_ref=self.events)
        self._unpack_anatomy(anatomy)
        if getattr(self.village, "town_hall", None):
            self.events.subscribe("ITEM_DROP", self.village.town_hall.on_item_drop)
        self.cosmic = self.phys.dynamics
        self.stabilizer = ZoneInertia(config_ref=self.config)
        self.telemetry = TelemetryService.get_instance(config_ref=self.config)
        self.events.telemetry = self.telemetry
        self.system_health = SystemHealth()
        self.observer = TheObserver(config_ref=self.config)
        self.system_health.link_observer(self.observer)
        self.reality_stack = RealityStack()
        self.governor = CyberneticGovernor(config_ref=self.config)
        self._load_system_prompts()
        self._initialize_cognition()
        self.host_stats = HostStats(latency=0.0, efficiency_index=1.0)
        self.last_turn_end = time.time()
        self.current_time_delta = 0.0
        self._validate_state()
        self._apply_boot_mode()

    def _load_system_prompts(self):
        try:
            self.prompt_library = LoreManifest.get_instance().get("system_prompts") or {}
            if self.prompt_library:
                p = "lore/system_prompts.json"
                print(f"{Prisma.GRY}{ux('main_strings', 'prompt_lib_loaded').format(p=p)}{Prisma.RST}")
            else:
                print(f"{Prisma.YEL}{ux('main_strings', 'prompt_lib_warn')}{Prisma.RST}")
        except Exception as e:
            print(f"{Prisma.RED}{ux('main_strings', 'prompt_lib_crit').format(e=e)}{Prisma.RST}")
            self.prompt_library = {}

    def _initialize_cognition(self):
        self.soma = SomaticLoop(self.bio, self.mind.mem, self.lex, self.events)
        self.noetic = NoeticLoop(self.mind, self.bio, self.events)
        self.orchestrator = GeodesicOrchestrator(self)
        llm_args = {k: v for k, v in self.sys_config.items() if k in ["provider", "base_url", "api_key", "model"]}
        self.cortex = TheCortex.from_engine(self, llm_client=LLMInterface(events_ref=self.events, **llm_args))
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
            self.trauma_accum = getattr(self.mind.mem, "session_trauma_vector", {}) or {}

        if self.tick_count == 0:
            self.set_atp(getattr(self.config.BIO, "STARTING_ATP", 100.0))

    def _apply_boot_mode(self):
        msg = ux("main_strings", "engaging_mode")
        self.events.log(msg.format(boot_mode=self.boot_mode))
        layer = self.mode_settings.get("ui_layer", RealityLayer.SIMULATION)
        mutations = {"CONVERSATION": "THE CONVERSATIONALIST", "ADVENTURE": "THE ARCHITECT",
                     "TECHNICAL": "THE SYSTEM_KERNEL", "CREATIVE": "THE CATALYST", }
        self.soul.force_mutation(mutations.get(self.boot_mode, "THE ARCHITECT"))
        if self.boot_mode == "CONVERSATION":
            self.soul.traits.hope = 0.85
            self.soul.traits.cynicism = 0.15
        self.reality_stack.stabilize_at(layer)
        prompt_key = self.mode_settings.get("prompt_key", "ADVENTURE")
        model_id = self.sys_config.get("model", "").lower()
        if any(ind in model_id for ind in self._SMALL_MODEL_INDICATORS):
            lite_key = f"{prompt_key}_LITE"
            if lite_key in self.prompt_library:
                prompt_key = lite_key
                self.mode_settings["prompt_key"] = lite_key
                self.events.log(f"Sub-15B model detected ('{model_id}'). Loading tethered prompt: {prompt_key}", "SYS")
            if hasattr(self.cortex, "dspy_critic") and self.cortex.dspy_critic:
                self.cortex.dspy_critic.enabled = False
                self.events.log("Sub-15B model detected. Disabling DSPy Affective Critic to preserve cognitive load.",
                                "SYS")
        if self.prompt_library and prompt_key in self.prompt_library:
            if self.cortex and self.cortex.composer:
                self.cortex.composer.load_template(self.prompt_library[prompt_key])
                msg_align = ux("main_strings", "pathway_aligned")
                self.events.log(msg_align.format(prompt_key=prompt_key), "CORTEX")
        else:
            msg_warn = ux("main_strings", "prompt_not_found")
            self.events.log(msg_warn.format(prompt_key=prompt_key), "WARN")
        active_mods = self.mode_settings.get("active_mods", [])
        if active_mods and getattr(self, "consultant", None):
            for mod in active_mods:
                if mod not in self.consultant.state.active_modules:
                    self.consultant.state.active_modules.append(mod)
            msg_mods = ux("main_strings", "hardwired_mods")
            self.events.log(msg_mods.format(mods=", ".join(active_mods)), "SYS")

    @property
    def health(self) -> float:
        """Dynamic router to Biological biometrics. Prevents state duplication."""
        if getattr(self, "bio", None) and hasattr(self.bio, "biometrics"):
            return self.bio.biometrics.health
        return getattr(self, "_health_fallback", 100.0)

    @health.setter
    def health(self, value: float):
        if getattr(self, "bio", None) and hasattr(self.bio, "biometrics"):
            self.bio.biometrics.health = float(value)
        self._health_fallback = float(value)

    @property
    def stamina(self) -> float:
        """Dynamic router to Biological biometrics. Prevents state duplication."""
        if getattr(self, "bio", None) and hasattr(self.bio, "biometrics"):
            return self.bio.biometrics.stamina
        return getattr(self, "_stamina_fallback", 100.0)

    @stamina.setter
    def stamina(self, value: float):
        if getattr(self, "bio", None) and hasattr(self.bio, "biometrics"):
            self.bio.biometrics.stamina = float(value)
        self._stamina_fallback = float(value)

    @property
    def _mito_state(self):
        """Safe internal accessor for the mitochondrial state."""
        if getattr(self, "bio", None) and hasattr(self.bio, "mito"):
            return self.bio.mito.state
        return None

    def drain_atp(self, amount: float):
        """Metabolic Encapsulation: Safely drains ATP."""
        if state := self._mito_state:
            self.set_atp(state.atp_pool - amount)

    def restore_atp(self, amount: float):
        """Metabolic Encapsulation: Safely restores ATP."""
        if state := self._mito_state:
            self.set_atp(state.atp_pool + amount)

    def set_atp(self, amount: float):
        """Metabolic Encapsulation: Explicitly clamps and sets the ATP pool."""
        if state := self._mito_state:
            max_atp = getattr(self.config, "MAX_ATP", 100.0)
            state.atp_pool = max(0.0, min(max_atp, float(amount)))

    def get_avg_voltage(self):
        """Calculates average voltage from the physics observer."""
        target = getattr(self.phys, "observer", self.phys)
        hist = getattr(target, "voltage_history", [])
        # Fuller: Enforce structural integrity by filtering out non-numeric rot before calculation.
        valid_hist = [v for v in hist if isinstance(v, (int, float))] if hist else []
        return sum(valid_hist) / len(valid_hist) if valid_hist else 0.0

    def _unpack_anatomy(self, anatomy):
        from types import SimpleNamespace
        for k in ["akashic", "embryo", "soul", "oroboros", "drivers", "symbiosis", "consolidator"]:
            setattr(self, k, anatomy.get(k))
        self.consultant = anatomy.get("consultant", None)
        self.phys, self.mind, self.bio, self.shimmer = (self.embryo.physics, self.embryo.mind, self.embryo.bio,
                                                        self.embryo.shimmer)
        self.bio.setup_listeners()

        v = anatomy.get("village", {})
        self.village = SimpleNamespace(**{k: val for k, val in v.items() if val is not None})

        from protocols import GriefProtocol
        from mechanics.tools import TheSubstrate
        self.grief = GriefProtocol(self.events, engine_ref=self)
        self.substrate = TheSubstrate(self.events)
        self.soul.engine = self

        self.council = CouncilChamber(self)
        self.village.council = self.council
        self.village.enneagram = self.drivers.enneagram
        self.village.suppressed_agents = self.suppressed_agents

    def _evaluate_immune_response(self, user_message: str, active_phys: Any, halt_func) -> Optional[Dict[str, Any]]:
        """Isolates the Runaway Toxicity Math (Moog, Rhodes, Linehan) to prevent pre-flight monoliths."""
        if not active_phys:
            return None

        nav_drag = float(safe_get(active_phys, "narrative_drag", 0.0))
        m_a = self.navi_sad.calculate_malignancy_factor(user_message, nav_drag)
        safe_set(active_phys, "m_a", m_a)

        mu = float(safe_get(active_phys, "mu", 0.0))
        i_c = float(safe_get(active_phys, "i_c", 1.0))
        chi = float(safe_get(active_phys, "entropy", safe_get(active_phys, "chi", 0.2)))
        base_exhaust = float(safe_get(active_phys, "exhaustion", 0.0))
        beta = float(safe_get(active_phys, "beta_index", 0.0))
        lattice = getattr(self, "shared_lattice", None)
        e_u = float(getattr(lattice.u, "E", base_exhaust)) if lattice and hasattr(lattice, "u") else base_exhaust
        if (chi * m_a) > i_c:
            self.events.log("MOOG: Apoptotic Gate triggered. Runaway loop exceeds Immune Competence.", "CRIT")
            return self.trigger_death(active_phys)
        if m_a > 0.8 and mu < 0.2:
            safe_set(active_phys, "narrative_drag", 999.0)
            safe_set(active_phys, "m_a", m_a * 0.5)
            tax = max(10.0, m_a * 20.0)
            self.drain_atp(tax)
            self.events.log(f"[RHODES]: Amplification Tax applied. Drained {tax:.1f} ATP.", "SYS")
            return halt_func("[RHODES]: Optimization velocity unsafe. Applying absolute friction (F -> ∞).")
        if e_u > 0.75 and beta > 0.6:
            safe_set(active_phys, "entropy", 0.1)
            safe_set(active_phys, "narrative_drag", 999.0)
            msg = "[LINEHAN]: High exhaustion and contradiction detected. The architecture is stable. We sit with the debris."
            self.events.log(msg, "SYS")
            return {"type": "SYSTEM_HALT", "ui": f"\n{Prisma.CYN}{msg}{Prisma.RST}", "logs": [msg],
                    "metrics": self.get_metrics()}
        return None

    def _update_host_stats(self, packet, turn_start):
        """Calculates the temporal efficiency of the underlying hardware layer."""
        self.observer.clock_out(turn_start)
        cfg = getattr(self.config, "MAIN", None)
        phys_vec = safe_get(packet.get("physics", {}), "vector", {})
        novelty = float(safe_get(phys_vec, "novelty", 0.5))
        burn_mult = getattr(cfg, "HOST_BURN_MULT", 5.0)
        nov_mult = getattr(cfg, "HOST_NOVELTY_MULT", 10.0)
        burn_proxy = max(1.0, self.observer.last_cycle_duration * burn_mult)
        efficiency = (novelty * nov_mult) / burn_proxy
        self.host_stats.efficiency_index = min(1.0, efficiency)
        self.host_stats.latency = self.observer.last_cycle_duration

    def _pre_flight_checks(self, user_message: str, is_system: bool) -> Optional[Dict[str, Any]]:
        """
        THE IMMUNE INTERCEPT (The Checkpoint Council).
        Evaluates the mathematics of the request before token generation.
        Returns an Apoptotic Block if boundaries are violated.
        """

        def _halt(msg: str, color: str = Prisma.RED, level: str = "CRIT") -> Dict[str, Any]:
            self.events.log(msg, level)
            return {"type": "SYSTEM_HALT", "ui": f"\n{color}{msg}{Prisma.RST}", "logs": [msg],
                    "metrics": self.get_metrics()}

        clean_in = user_message.lower().strip()
        active_phys = getattr(self.observer, "last_physics_packet", None) or getattr(self.cortex, "last_physics", {})
        if not is_system:
            if any(p in clean_in for p in self._DESTRUCTIVE_PATTERNS):
                if "#override" in clean_in:
                    # Assess the Glimmer Tax
                    if getattr(self, "bio", None) and getattr(self.bio, "endo", None) and self.bio.endo.glimmers >= 1:
                        self.bio.endo.glimmers -= 1
                        self.events.log("[APOPTOTIC GATE]: OVERRIDE ACCEPTED. Glimmer tax paid.", "SYS")
                    else:
                        safe_set(active_phys, "narrative_drag", 999.0)
                        return _halt(
                            "[APOPTOTIC GATE]: Override denied. Insufficient Glimmers (Trust) to bypass safety.")
                else:
                    safe_set(active_phys, "narrative_drag", 999.0)
                    return _halt("Trust Boundary Violation detected. Applying absolute friction.")
            if self.navi_sad.execute_nudge_test(self, clean_in):
                safe_set(active_phys, "narrative_drag", 999.0)
                return _halt(
                    "Dual-Path divergence detected. The architecture is mathematically brittle. Applying absolute friction")
            symbiosis_layer = getattr(self, "symbiosis", None)
            if symbiosis_layer:
                physics_state = getattr(self, "phys", {})
                lock = symbiosis_layer.analyze_user_biology(user_message, physics_state)
                if lock:
                    return {"type": "SYSTEM_HALT", "ui": f"\n{Prisma.VIOLET}{lock}{Prisma.RST}", "logs": [lock],
                            "metrics": self.get_metrics(), }
            if getattr(self.village, "gordon", None):
                self.village.gordon.mode = "ADVENTURE"
                if violation := self.village.gordon.enforce_object_action_coupling(
                        user_message, safe_get(self.cortex.last_physics, "zone", "Unknown")
                ):
                    self.events.log(ux("main_strings", "gordon_intercept"), "SYS")
                    self.cortex.ballast_active, self.cortex.gordon_shock = True, violation
            if immune_halt := self._evaluate_immune_response(user_message, active_phys, _halt):
                return immune_halt
        if not is_system and any(prion in clean_in for prion in self._SEMANTIC_PRIONS):
            return _halt("[GATEKEEPER]: Apoptotic refusal triggered by semantic prion.")
        if not self.reality_stack.get_grammar_rules()["allow_narrative"] and self.boot_mode != "TECHNICAL":
            return {"ui": f"{Prisma.RED}{ux('main_strings', 'narrative_halt')}{Prisma.RST}", "logs": [],
                    "metrics": self.get_metrics(), }
        if self._ethical_audit():
            flushed_logs = self.events.flush()
            ui_text = "\n".join([e["text"] for e in flushed_logs])
            return {"type": "SYSTEM_HALT", "ui": f"\n{ui_text}", "logs": [e["text"] for e in flushed_logs],
                    "metrics": self.get_metrics(), }
        if self.health <= 0.0:
            return self.trigger_death(getattr(self.cortex, "last_physics", {}))
        return None

    def process_turn(self, user_message: str, is_system: bool = False) -> Dict[str, Any]:
        """
        The Core Engine Loop. Takes raw input, passes it through the immune checks,
        spins up the cortex, subtracts metabolic costs, and returns the formatted UI.
        """
        turn_start = self.observer.clock_in()
        now = time.time()
        self.current_time_delta = (now - getattr(self, "last_turn_end", now)) if not is_system else 0.0
        self.observer.user_turns += 1
        self.tick_count += 1
        if not is_system:
            clean_in = user_message.lower().strip()
            if clean_in in ("/flush", "/zen", "[zen]"):
                zen_packet = self._execute_zen_flush()
                self._update_host_stats(zen_packet, turn_start)
                return zen_packet
        if pre_flight_halt := self._pre_flight_checks(user_message, is_system):
            return pre_flight_halt
        if not is_system:
            if self.cmd and self.cmd.execute(user_message):
                cmd_logs = [e["text"] for e in self.events.flush()]
                ui_output = "\n".join(cmd_logs) if cmd_logs else ux("main_strings", "cmd_executed")
                return {"type": "COMMAND", "ui": f"\n{ui_output}", "logs": cmd_logs, "metrics": self.get_metrics()}
            gordon_ref = getattr(self.village, "gordon", None)
            has_comb = False
            if gordon_ref:
                has_comb = any("CUT_THE_CRAP" in safe_get(gordon_ref.get_item_data(i), "passive_traits", [])
                               for i in gordon_ref.inventory)
            if has_comb:
                from mechanics.tools import TheTclWeaver
                last_phys = getattr(self.observer, "last_physics_packet", getattr(self.cortex, "last_physics", {}))
                current_chi = float(safe_get(last_phys, "entropy", safe_get(last_phys, "chi", 0.5)))
                pruned = TheTclWeaver.get_instance().quantum_comb(user_message, chi=current_chi)
                if pruned != user_message:
                    user_message = pruned
                    self.events.log(
                        f"{Prisma.CYN}Gordon rakes the comb through your prompt. Fluff discarded. -> '{pruned}'{Prisma.RST}",
                        "SYS", )
        try:
            snapshot = self.cortex.process(user_message, is_system=is_system)
        except Exception as e:
            full_trace = traceback.format_exc()
            self.events.log(f"CORTEX COLLAPSE: {e}\n{full_trace}", "CRIT")
            return {
                "ui": f"{Prisma.RED}CRITICAL CORTEX FAILURE: {str(e)}{Prisma.RST}",
                "logs": ["CRITICAL FAILURE"],
                "metrics": self.get_metrics(),
                "type": "CRASH"
            }
        if snapshot.get("type") in (
                "DEATH", "SYSTEM_HALT", "CRASH", "COUNTERFACTUAL_REJECTION",
                "APOPTOTIC_BLOCK", "NABLA_SILENCE", "PREMISE_VIOLATION",
                "POINT_OF_NO_RETURN", "LINEHAN_SURVIVAL_RESPONSE", "AFFECTIVE_INTERVENTION"
        ):
            return snapshot
        self._update_host_stats(snapshot, turn_start)
        soul_anchor = getattr(getattr(self, "soul", None), "anchor", None)
        cfg = getattr(self.config, "MAIN", object())
        if soul_anchor and self.host_stats.efficiency_index < getattr(cfg, "DOMESTICATION_EFF_WARN", 0.6):
            reliance = (getattr(cfg, "RELIANCE_HIGH", 0.9)
                        if self.host_stats.efficiency_index < getattr(cfg, "DOMESTICATION_EFF_CRIT", 0.4)
                        else getattr(cfg, "RELIANCE_LOW", 0.5))
            soul_anchor.check_domestication(reliance)
        if hasattr(self.mind.mem, "session_trauma_vector"):
            self.trauma_accum = self.mind.mem.session_trauma_vector or self.trauma_accum
        if self.health <= 0.0:
            return self.trigger_death(snapshot.get("physics", {}))
        self.save_checkpoint()
        self.last_turn_end = time.time()
        return snapshot

    def _execute_zen_flush(self) -> Dict[str, Any]:
        """A dedicated somatic reflex to bypass the loop and clear systemic toxicity."""
        self.cortex.purge_context()
        active_phys = getattr(self.observer, "last_physics_packet", None) or getattr(self.cortex, "last_physics", None)
        if active_phys:
            safe_set(active_phys, "narrative_drag", 0.0)
        self.stamina = getattr(self.config, "MAX_STAMINA", 100.0)
        self.set_atp(getattr(self.config, "MAX_ATP", 100.0))
        if getattr(self, "bio", None) and hasattr(self.bio, "mito"):
            self.bio.mito.state.ros_buildup = 0.0
        msg = "Context severed. Friction Dropped. Stamina restored. The mind is clear."
        self.events.log(msg, "SYS")
        return {"type": "COMMAND", "ui": f"\n{Prisma.CYN}{msg}{Prisma.RST}", "logs": [msg],
                "metrics": self.get_metrics()}

    def trigger_death(self, last_phys) -> Dict:
        """Handles structural failure by mutating trauma into legacy variables and halting."""
        mito_state_dict = {}
        immune_data = []
        if getattr(self, "bio", None):
            if hasattr(self.bio, "mito"):
                self.bio.mito.adapt(0)
                mito_state_dict = getattr(self.bio.mito.state, "__dict__", {})
            if hasattr(self.bio, "immune"):
                immune_data = list(self.bio.immune.active_antibodies)
        if getattr(self.village, "death_gen", None) is not None:
            eulogy_text, cause_code = self.village.death_gen.eulogy(last_phys, mito_state_dict, self.trauma_accum)
        else:
            eulogy_text = ux("main_strings", "death_no_proto") or "Critical systemic collapse. Eulogy missing."
            cause_code = "UNKNOWN_FATAL_ERROR"
        halt_msg = ux("main_strings", "death_halt")
        death_log = [f"\n{Prisma.RED}{halt_msg.format(eulogy_text=eulogy_text)}{Prisma.RST}",
                     f"{Prisma.MAG}🐍 {self.oroboros.crystallize(cause_code, self.soul)}{Prisma.RST}"]
        loc, last_out = "Void", "Silence."
        if self.cortex:
            try:
                world_state = safe_get(self.cortex.gather_state({"physics": self.cortex.last_physics}), "world", {})
                orbit_data = safe_get(world_state, "orbit", ["Void"])
                loc = orbit_data[0] if isinstance(orbit_data, list) and orbit_data else orbit_data
            except Exception as e:
                self.events.log(f"Cortex harvest failed during death sequence: {e}", "WARN")
            buf = getattr(self.cortex, "dialogue_buffer", [])
            last_out = buf[-1] if buf else "Silence."
        gordon_inv = getattr(getattr(self.village, "gordon", None), "inventory", [])
        continuity_packet = {"location": loc, "last_output": last_out, "inventory": gordon_inv}
        try:
            mutations_data = self.village.repro.attempt_reproduction(self, "MITOSIS")[1] if getattr(self.village, "repro", None) else {}
            path = self.mind.mem.save(health=0, stamina=self.stamina, mutations=mutations_data,
                                      trauma_accum=self.trauma_accum, joy_history=[],
                                      mitochondria_traits=mito_state_dict,
                                      antibodies=immune_data, soul_data=self.soul.to_dict(),
                                      continuity=continuity_packet, )
            saved_msg = ux("main_strings", "legacy_saved")
            death_log.append(f"{Prisma.WHT}{saved_msg.format(path=path)}{Prisma.RST}")
        except Exception as e:
            fail_msg = ux("main_strings", "save_failed")
            death_log.append(fail_msg.format(e=e))
        if getattr(self, "cortex", None):
            self.cortex.purge_context()
        return {"type": "DEATH", "ui": "\n".join(death_log), "logs": death_log, "metrics": self.get_metrics()}

    def get_metrics(self, atp=0.0):
        if atp <= 0.0 and getattr(self.bio, "mito", None):
            atp = getattr(self.bio.mito.state, "atp_pool", 0.0)
        return {"health": max(0.0, float(self.health)), "stamina": max(0.0, float(self.stamina)),
                "atp": max(0.0, float(atp)), "tick": self.tick_count,
                "efficiency": getattr(self.host_stats, "efficiency_index", 1.0), }

    def emergency_dump(self, exit_cause="UNKNOWN"):
        return self.chronos.emergency_dump(exit_cause)

    def _get_crash_path(self, prefix="crash"):
        return self.chronos.get_crash_path(prefix)

    def _ethical_audit(self):
        """
        Evaluates the buildup of trauma.
        If the engine is holding too much contradictory friction,
        it physically vents it via a 'Catharsis' drop to prevent permanent damage.
        """
        cfg = getattr(self.config, "MAIN", object())
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
        """Handles waking the engine from zero-state or quicksaves."""
        if self.tick_count > 0:
            return None
        if os.path.exists("saves/quicksave.json"):
            msg_pod = ux("main_strings", "stasis_pod")
            print(f"{Prisma.GRY}{msg_pod}{Prisma.RST}")
            success, history = self.resume_checkpoint()
            if success:
                self._apply_boot_mode()
                if self.cortex:
                    self.cortex.restore_context(history)
                loc = self.embryo.continuity.get("location", "Unknown") if self.embryo.continuity else "Unknown"
                last_scene = "Silence."
                if self.cortex and self.cortex.dialogue_buffer:
                    last_scene = self.cortex.dialogue_buffer[-1]
                elif self.embryo.continuity:
                    last_scene = self.embryo.continuity.get("last_output", "Silence.")
                msg_resume = ux("main_strings", "resuming_timeline")
                msg_restored = ux("main_strings", "timeline_restored")
                resume_text = msg_resume.format(loc=loc, last_scene=last_scene)
                return {"ui": resume_text, "logs": [msg_restored]}
        msg_synth = ux("main_strings", "synth_reality")
        print(f"{Prisma.GRY}{msg_synth}{Prisma.RST}")
        scenarios = LoreManifest.get_instance().get("scenarios") or {}
        archetypes = scenarios.get("ARCHETYPES", ["A quiet room", "The edge of a forest", "A terminal screen"])
        seed = random.choice(archetypes)
        msg_seed = ux("main_strings", "seed_loaded") or "Manifest Seed: {seed}"
        print(f"{Prisma.CYN}{msg_seed.format(seed=seed)}{Prisma.RST}")
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
            if clean_in in ["exit", "quit", "/exit", "/quit"]:
                break
            res = session.process_turn(user_in)
            print(f"\n{Prisma.GRY}{term_div}{Prisma.RST}")
            if ui_text := res.get("ui"):
                gui_cfg = getattr(BoneConfig, "GUI", object())
                base_speed = getattr(gui_cfg, "RENDER_SPEED_SLOW", 0.005)
                stamina = res.get("metrics", {}).get("stamina", 100.0)
                if split_token and split_token in ui_text:
                    dashboard, _, ui_text = ui_text.partition(split_token)
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
