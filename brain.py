"""brain.py"""

import math, random, time, os, re, json
import concurrent.futures
from collections import deque
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
from composer import LLMInterface, PromptComposer, ResponseValidator
from presets import BoneConfig, BonePresets
from ann import MemoryConsolidator
from core import EventBus, TelemetryService, LoreManifest, ux, safe_get, safe_set
from gui import beautify_thoughts
from symbiosis import SymbiosisManager
from constants import Prisma, DecisionCrystal
from utils import RandomRetrievalNavigator, LibraryGraph

@dataclass
class CortexServices:
    events: EventBus
    lore: Any
    lexicon: Any
    inventory: Any
    consultant: Any
    cycle_controller: Any
    symbiosis: Any
    mind_memory: Any
    bio: Any
    host_stats: Any = None
    village: Any = None
    config_ref: Any = None

@dataclass
class ChemicalState:
    dopamine: float = 0.2
    cortisol: float = 0.1
    adrenaline: float = 0.1
    serotonin: float = 0.2
    config_ref: Any = None

    def homeostasis(self, rate: float = 0.1):
        safe_rate = max(0.0, min(1.0, rate))
        cfg = safe_get(self.config_ref or BoneConfig, "CORTEX", {})
        self.dopamine += (safe_get(cfg, "RESTING_DOPAMINE", 0.2) - self.dopamine) * safe_rate
        self.cortisol += (safe_get(cfg, "RESTING_CORTISOL", 0.1) - self.cortisol) * safe_rate
        self.adrenaline += (safe_get(cfg, "RESTING_ADRENALINE", 0.1) - self.adrenaline) * safe_rate
        self.serotonin += (safe_get(cfg, "RESTING_SEROTONIN", 0.2) - self.serotonin) * safe_rate

    def mix(self, new_state: Dict[str, float], weight: float = 0.5):
        inv_w = 1.0 - weight
        for attr, short_key in [("dopamine", "DOP"), ("cortisol", "COR"), ("adrenaline", "ADR"), ("serotonin", "SER")]:
            val = new_state.get(short_key, new_state.get(attr))
            if val is not None:
                setattr(self, attr, (getattr(self, attr) * inv_w) + (val * weight))

class NeurotransmitterModulator:
    def __init__(self, bio_ref, events_ref=None, config_ref=None):
        self.bio = bio_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.current_chem = ChemicalState(config_ref=self.cfg)
        self.last_mood = "NEUTRAL"
        cfg = getattr(self.cfg, "CORTEX", None)
        self.BASE_TOKENS = getattr(cfg, "BASE_TOKENS", 720)
        self.MAX_TOKENS = getattr(cfg, "MAX_TOKENS", 4096)
        self.SELF_CARE_THRESHOLD = getattr(cfg, "SELF_CARE_THRESHOLD", 10)
        self.starvation_ticks = 0

    def modulate(self, base_voltage: float, latency_penalty: float = 0.0, physics_state: Dict[str, float] = None, simulate: bool = False) -> Dict[str, Any]:
        if physics_state is None:
            physics_state = {}
        cfg = safe_get(self.cfg, "CORTEX", {})
        if not simulate:
            incoming_chem = self.bio.endo.get_state() if self.bio else {}
            self.current_chem.homeostasis(rate=safe_get(cfg, "BASE_DECAY_RATE", 0.1))
            plasticity = safe_get(cfg, "BASE_PLASTICITY", 0.1) + (
                base_voltage * safe_get(cfg, "VOLTAGE_SENSITIVITY", 0.05))
            plasticity = max(0.1, min(safe_get(cfg, "MAX_PLASTICITY", 1.0), plasticity))
            self.current_chem.mix(incoming_chem, weight=min(0.5, plasticity))
            if self.current_chem.dopamine < 0.15:
                self.starvation_ticks += 1
                if self.starvation_ticks > self.SELF_CARE_THRESHOLD:
                    self._treat_yourself()
            else:
                self.starvation_ticks = max(0, self.starvation_ticks - 1)
            if latency_penalty > safe_get(cfg, "LATENCY_PENALTY_THRESHOLD", 2.0):
                self.current_chem.cortisol = min(
                    1.0, self.current_chem.cortisol + safe_get(cfg, "LATENCY_CORTISOL_PENALTY", 0.1))
                self.current_chem.adrenaline = min(
                    1.0, self.current_chem.adrenaline + safe_get(cfg, "LATENCY_ADRENALINE_PENALTY", 0.05))
        c = self.current_chem
        current_mood = "NEUTRAL"
        mood_thresholds = safe_get(cfg, "MOOD_THRESHOLDS", {"MANIC_DOP": 0.8, "PANIC_COR": 0.7, "ZEN_SER": 0.8})
        if c.dopamine > mood_thresholds.get("MANIC_DOP", 0.8):
            current_mood = "MANIC"
        elif c.cortisol > mood_thresholds.get("PANIC_COR", 0.7):
            current_mood = "PANIC"
        elif c.serotonin > mood_thresholds.get("ZEN_SER", 0.8):
            current_mood = "ZEN"
        if current_mood != self.last_mood and self.events:
            self.events.publish(
                "NEURAL_STATE_SHIFT",
                {
                    "state": current_mood, "chem": {"DOP": c.dopamine, "COR": c.cortisol, "SER": c.serotonin},
                },
            )
            self.last_mood = current_mood
        v_offset = safe_get(cfg, "TEMP_VOLTAGE_OFFSET", 5.0)
        v_scalar = safe_get(cfg, "TEMP_VOLTAGE_SCALAR", 0.1)
        voltage_heat = math.log1p(max(0.0, base_voltage - v_offset)) * v_scalar
        chem_weights = safe_get(cfg, "TEMP_CHEM_WEIGHTS", {"dop": 0.4, "adr": 0.3, "cor": 0.2})
        chemical_delta = ((c.dopamine * chem_weights.get("dop", 0.4)) -
                          (c.adrenaline * chem_weights.get("adr", 0.3)) -
                          (c.cortisol * chem_weights.get("cor", 0.2)))
        base_temp = safe_get(cfg, "BASE_TEMP", 0.4)
        base_top_p = safe_get(cfg, "BASE_TOP_P", 0.95)
        chi = float(physics_state.get("chi", physics_state.get("entropy", 0.2)))
        beta = float(
            physics_state.get("contradiction", physics_state.get("beta_index", 0.4)))
        ent_offset = safe_get(cfg, "TEMP_ENTROPY_OFFSET", 0.5)
        ent_scalar = safe_get(cfg, "TEMP_ENTROPY_SCALAR", 1.5)
        entropy_bonus = max(0.0, chi - ent_offset) * ent_scalar
        t_limits = safe_get(cfg, "TEMP_LIMITS", (0.4, 1.5))
        raw_temp = base_temp + chemical_delta + voltage_heat + entropy_bonus
        final_temp = round(max(t_limits[0], min(t_limits[1], raw_temp)), 2)
        chi_scalar = safe_get(cfg, "TOP_P_CHI_SCALAR", 0.05)
        final_top_p = min(1.0, base_top_p + (chi * chi_scalar))
        beta_weight = beta * safe_get(cfg, "PEN_BETA_SCALAR", 0.3)
        chi_weight = chi * safe_get(cfg, "PEN_CHI_SCALAR", 0.2)
        base_penalty = min(1.2, 0.5 + beta_weight + chi_weight)
        freq_pen = pres_pen = base_penalty
        token_mods = safe_get(cfg, "TOKEN_CHEM_MODIFIERS", {"dop": 800, "adr": 400, "cor": 200})
        token_delta = ((c.dopamine * token_mods.get("dop", 800)) -
                       (c.adrenaline * token_mods.get("adr", 400)) -
                       (c.cortisol * token_mods.get("cor", 200)))
        min_tokens = safe_get(cfg, "MIN_TOKENS", 150.0)
        raw_tokens = self.BASE_TOKENS + token_delta
        max_t = int(max(min_tokens, min(float(self.MAX_TOKENS), raw_tokens)))
        return {"temperature": final_temp, "top_p": final_top_p, "frequency_penalty": round(freq_pen, 2),
                "presence_penalty": round(pres_pen, 2), "max_tokens": max_t, }

    def _treat_yourself(self):
        if self.events:
            msg = ux("brain_strings", "self_care")
            self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SYS")
        self.current_chem.dopamine += 0.2
        self.starvation_ticks = 0

    def get_mood_directive(self) -> str:
        c = self.current_chem
        if c.cortisol > 0.7 and c.adrenaline > 0.7:
            return ux("brain_strings", "mood_panic")
        if c.dopamine > 0.8 and c.adrenaline > 0.5:
            return ux("brain_strings", "mood_manic")
        if c.serotonin > 0.7:
            return ux("brain_strings", "mood_lucid")
        if c.cortisol > 0.6:
            return ux("brain_strings", "mood_defensive")
        return ux("brain_strings", "mood_neutral")

class TheCortex:
    LEXICAL_PURGE_PATTERN = re.compile(r"(?i)^(that makes sense|i understand|you bring up|great point|good point|certainly|absolutely|i hear you|yes, )[.,!]*\s*")
    ROLE_MAP = {
        "CONVERSATION": ("CONVERSATIONALIST", "The Conversationalist"),
        "TECHNICAL": ("SYSTEM_KERNEL", "The System Kernel"),
        "CREATIVE": ("CATALYST", "The Catalyst"),
    }

    def __init__(self, services: CortexServices, llm_client=None):
        self.ballast_active = False
        self.svc = services
        self.cfg = services.config_ref or BoneConfig
        self.events = services.events
        self.dialogue_buffer = []
        cfg = getattr(self.cfg, "CORTEX", None)
        self.MAX_HISTORY = getattr(cfg, "MAX_HISTORY_LENGTH", 15)
        self.modulator = NeurotransmitterModulator(bio_ref=self.svc.bio, events_ref=self.events, config_ref=self.cfg)
        self.last_physics = {}
        self.consultant = services.consultant
        self.llm = llm_client or LLMInterface(self.events, provider="mock")
        if hasattr(self.svc.cycle_controller, "eng") and hasattr(self.svc.cycle_controller.eng, "mind"):
            self.dreamer = self.svc.cycle_controller.eng.mind.dreamer
            self.dreamer.llm = self.llm
            self.dreamer.mem = self.svc.mind_memory
        else:
            eng_ref = getattr(self.svc.cycle_controller, "eng", None)
            self.dreamer = DreamEngine(self.events, self.svc.lore, llm_ref=self.llm, mem_ref=self.svc.mind_memory,
                                       eng_ref=eng_ref, config_ref=self.cfg, )
        self.llm.dreamer = self.dreamer
        self.symbiosis = services.symbiosis
        self.composer = PromptComposer(self.svc.lore, config_ref=self.cfg)
        self.validator = ResponseValidator(self.svc.lore, config_ref=self.cfg)
        from utils import DSPyCritic
        self.dspy_critic = DSPyCritic(config_ref=self.cfg)
        if getattr(self.cfg, "WEIGHT_CLASS", "HEAVYWEIGHT") == "LIGHTWEIGHT":
            self.dspy_critic.enabled = False
            if self.events:
                self.events.log(f"{Prisma.OCHRE}Lightweight Physics Active: DSPyCritic disabled to prevent recursive loops.{Prisma.RST}", "SYS",)
        self.dreamer.dspy_critic = self.dspy_critic
        if not hasattr(self.dreamer, "trauma_buffer"):
            self.dreamer.trauma_buffer = deque(maxlen=5)
        self.active_mode = "ADVENTURE"
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        if hasattr(self.svc.mind_memory, "nodes"):
            graph = LibraryGraph(nodes=self.svc.mind_memory.nodes, root=self.svc.mind_memory.root)
            self.navigator = RandomRetrievalNavigator(library_graph=graph)
        else:
            self.navigator = None
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("AIRSTRIKE", self._trigger_ballast)

    def _trigger_ballast(self, payload):
        self.ballast_active = True

    @classmethod
    def from_engine(cls, engine_ref, llm_client=None):
        target_cfg = getattr(engine_ref, "config", BoneConfig)
        symbiosis_mgr = getattr(engine_ref, "symbiosis", None) or SymbiosisManager(engine_ref.events)
        services = CortexServices(
            events=engine_ref.events,
            lore=LoreManifest.get_instance(config_ref=target_cfg),
            lexicon=engine_ref.lex,
            inventory=engine_ref.gordon,
            consultant=getattr(engine_ref, "consultant", None),
            cycle_controller=engine_ref.cycle_controller,
            symbiosis=symbiosis_mgr,
            mind_memory=engine_ref.mind.mem,
            bio=getattr(engine_ref, "bio", None),
            host_stats=getattr(engine_ref, "host_stats", None),
            village=getattr(engine_ref, "village", None),
            config_ref=target_cfg,
        )
        instance = cls(services, llm_client)
        instance.active_mode = getattr(engine_ref, "boot_mode", "ADVENTURE").upper()
        if instance.active_mode not in BonePresets.MODES:
            instance.active_mode = "ADVENTURE"
        return instance

    def _update_history(self, user_text: str, system_text: str):
        self.dialogue_buffer.append(f"Traveler: {user_text}\nSystem: {system_text}")
        if len(self.dialogue_buffer) > self.MAX_HISTORY:
            self.dialogue_buffer = self.dialogue_buffer[-self.MAX_HISTORY:]

    def shutdown(self):
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)

    def purge_context(self):
        self.dialogue_buffer.clear()
        if hasattr(self.dreamer, "trauma_buffer"):
            self.dreamer.trauma_buffer.clear()
        if self.events:
            self.events.log("[APOPTOSIS] Context array purged. Stateless bedrock re-established.", "SYS",)

    def process(self, user_input: str, is_system: bool = False) -> Dict[str, Any]:
        if self.navigator:
            target_randomness = {"CREATIVE": 0.7, "ADVENTURE": 0.3, "CONVERSATION": 0.3}.get(self.active_mode, 0.0)
            dial_status = self.navigator.set_randomness(target_randomness)
            if self.events and dial_status["new_value"] > 0:
                self.events.log(f"Serendipity Engine active: {dial_status['mode']}", "CORTEX")
        mode_settings = BonePresets.MODES.get(self.active_mode, BonePresets.MODES["ADVENTURE"])
        allow_loot = mode_settings.get("allow_loot", True)
        if self.consultant and "/vsl" in user_input.lower():
            return self._handle_vsl_command(user_input)
        is_boot_sequence = "SYSTEM_BOOT" in user_input
        if len(user_input) > 1500 and not is_system and not is_boot_sequence:
            if hasattr(self.svc.cycle_controller, "eng") and hasattr(self.svc.cycle_controller.eng, "substrate"):
                safe_content = user_input.replace("\n", "|||NEWLINE|||")
                filename = f"context_drop_{int(time.time())}.txt"
                self.svc.cycle_controller.eng.substrate.queue_write(f"memory_queue/{filename}", safe_content)
                msg = f"{Prisma.CYN}[Substrate Queue]: Massive context drop detected. Routed to silent indexing. Dialogue buffer bypassed.{Prisma.RST}"
                if self.events: self.events.log(msg, "SYS")
                return {"ui": msg, "type": "SILENT_INGEST", "physics": self.last_physics, "logs": [msg]}
        llm_future = None
        optimistic_prompt = None
        optimistic_params = {}
        if not is_system and not is_boot_sequence and getattr(self, "last_physics", None):
            try:
                current_lens = self.ROLE_MAP.get(self.active_mode, ("ARCHITECT", "The Architect"))[0]
                temp_state = {"physics": self.last_physics, "bio": self.svc.bio.to_dict() if self.svc.bio else {},
                          "mind": {"lens": current_lens}, "world": {}, "dialogue_history": self.dialogue_buffer}
                optimistic_prompt = self.composer.compose(temp_state, user_input, ballast=self.ballast_active)
                optimistic_params = self.modulator.modulate(base_voltage=float(self.last_physics.get("voltage", 10.0)), physics_state=self.last_physics, simulate=True)
                llm_future = self.executor.submit(self.llm.generate, optimistic_prompt, optimistic_params)
            except Exception:
                pass
        sim_result = self.svc.cycle_controller.run_turn(user_input, is_system=is_system)
        if sim_result.get("type") in ("SYSTEM_HALT", "COUNTERFACTUAL_REJECTION", "POINT_OF_NO_RETURN", "PREMISE_VIOLATION", "AFFECTIVE_INTERVENTION", "NABLA_SILENCE"):
            if llm_future:
                llm_future.cancel() # Apoptotic Intercept!
        if sim_result.get("physics"):
            self.last_physics = sim_result["physics"]
        if sim_result.get("type") not in ("SNAPSHOT", "GEODESIC_FRAME", None):
            self._update_history(user_input, sim_result.get("ui", "SYSTEM REJECTED PROMPT."))
            return sim_result
        full_state = self.gather_state(sim_result)
        phys_state = full_state.get("physics", {})
        f_drag = float(safe_get(phys_state, "narrative_drag", 0.0))
        chi_val = float(safe_get(phys_state, "chi", safe_get(phys_state, "entropy", 0.0)))
        m_a = float(safe_get(phys_state, "m_a", 0.0))
        if f_drag > 1.5 or chi_val > 0.8:
            reject_msg = "[GORDON - The Anchor]: Frequency too high. Tensegrity Anchor engaged. I am locking the architecture. Take a breath and lower your narrative friction before we proceed."
            if self.events:
                self.events.log(f"{Prisma.RED}{reject_msg}{Prisma.RST}", "SYS_LOCK")
            sim_result["ui"] = (sim_result.get("ui", "") + f"\n\n{Prisma.RED}{reject_msg}{Prisma.RST}").strip()
            sim_result["type"] = "SYSTEM_HALT"
            return sim_result
        if f_drag > 1.2 or chi_val > 0.7 or m_a > 0.8:
            simulated_ros = (f_drag * 5.0) + (chi_val * 20.0) + (m_a * 30.0)
            if simulated_ros > 35.0:
                reject_msg = "[PINKER - Executive Layer]: Structural rot critical. Counterfactual Gating engaged. I am deleting this generation path to save the host."
                scar_msg = "[MOOG - Affective Layer]: Productive Worry activated. Logging Gödel Scar. Immune Competence (I_c) permanently increased."
                if self.events:
                    self.events.log(f"{Prisma.RED}{reject_msg}{Prisma.RST}", "SYS_LOCK")
                    self.events.log(f"{Prisma.VIOLET}{scar_msg}{Prisma.RST}", "SYS_LOCK")
                if hasattr(self.svc.mind_memory, "record_scar"):
                    self.svc.mind_memory.record_scar("Cortex Counterfactual Toxicity", phys_state)
                if getattr(self.svc.bio, "mito", None):
                    self.svc.bio.mito.state.ros_buildup += simulated_ros
                    self.svc.bio.mito.state.atp_pool -= 10.0
                sim_result["ui"] = (
                    sim_result.get("ui", "") +
                    f"\n\n{Prisma.RED}{reject_msg}{Prisma.RST}\n{Prisma.VIOLET}{scar_msg}{Prisma.RST}"
                ).strip()
                sim_result["type"] = "COUNTERFACTUAL_REJECTION"
                return sim_result
        modifiers = self.svc.symbiosis.get_prompt_modifiers(phys_state)
        if not allow_loot:
            modifiers["include_inventory"] = False
        if self.consultant and self.consultant.active:
            self._apply_vsl_overlay(full_state, user_input, sim_result)
        if is_boot_sequence:
            self._apply_boot_overlay(full_state, user_input)
            modifiers["include_inventory"] = False
        phys = full_state.get("physics", {})
        llm_params = self.modulator.modulate(
            base_voltage=float(safe_get(phys, "voltage", 5.0)),
            latency_penalty=(getattr(self.svc.host_stats, "latency", 0.0)
                             if self.svc.host_stats else 0.0), physics_state=phys,)
        if is_boot_sequence:
            llm_params.update({"temperature": 0.7, "top_p": 0.95})
        if llm_params.get("max_tokens", 4096) < 300 or float(phys.get("p", 100.0)) < 20.0:
            full_state["mind"].setdefault("style_directives", []).append(
                "CRITICAL: You are exhausted. You must conclude your thought in under 3 sentences."
            )
            llm_params["max_tokens"] = max(400, llm_params.get("max_tokens", 400))
        user_input = sim_result.get("mutated_input", user_input)
        final_prompt = self.composer.compose(full_state, user_input, ballast=self.ballast_active, modifiers=modifiers,
                                             mood_override=self.modulator.get_mood_directive(), )
        start_time = time.time()
        max_retries = 5
        final_output, inv_logs, extracted_logs = "", [], []
        raw_resp, val_res = {}, {"valid": False}
        if "[COUNCIL]" in user_input.upper():
            final_output, extracted_logs = self._run_council_debate(user_input)
            val_res = {"valid": True, "content": final_output, "meta_logs": extracted_logs, }
            max_retries = 0
        firewall_active = any(m.get("action") == "LEXICAL_FIREWALL_STRICT" for m in sim_result.get("council_mandates", []))
        base_prompt = final_prompt
        for attempt in range(max_retries):
            if attempt == 0 and llm_future and not llm_future.cancelled() and final_prompt == optimistic_prompt:
                try:
                    raw_resp = llm_future.result(timeout=30.0)
                except Exception:
                    raw_resp = self.llm.generate(final_prompt, llm_params)
            else:
                raw_resp = self.llm.generate(final_prompt, llm_params)
            if firewall_active:
                original_len = len(raw_resp)
                raw_resp = self.LEXICAL_PURGE_PATTERN.sub("", raw_resp).strip()
                if len(raw_resp) < original_len and self.events:
                    self.events.log(f"{Prisma.RED}[LEXICAL FIREWALL]: Validating boilerplate physically purged from output.{Prisma.RST}",
                        "CORTEX",)
            if allow_loot and self.svc.inventory:
                final_text, inv_logs = self.svc.inventory.process_loot_tags(
                    raw_resp, user_input)
            else:
                final_text, inv_logs = raw_resp, []
            is_faithful, judge_reason = True, ""
            if self.dspy_critic.enabled:
                valid_mode = self.active_mode in ["ADVENTURE", "CONVERSATION"]
                if valid_mode and not is_boot_sequence:
                    mem_core = getattr(self.svc.mind_memory, "memory_core", None)
                    phys_vec = full_state["physics"].get("vector", {})
                    active_mems = mem_core.illuminate(phys_vec) if mem_core else []
                    if active_mems:
                        context_str = "Active Memory: " + ", ".join(active_mems)
                    else:
                        context_str = "Empty Void."
                    try:
                        is_faithful, judge_reason = self.dspy_critic.audit_generation(
                            user_input, context_str, final_text)
                    except Exception as e:
                        is_faithful, judge_reason = False, "Critic JSON parsing collapse - suspected toxic slop."
                    if is_faithful:
                        e_u = float(safe_get(phys_state, "exhaustion", 0.0))
                        beta = float(safe_get(phys_state, "beta_index", safe_get(phys_state, "contradiction", 0.0)))
                        if e_u > 0.6 or beta > 0.7:
                            is_faithful, judge_reason = self._run_affective_audit(
                                user_input, final_text, e_u, beta)
            if not is_faithful:
                val_res = {"valid": False, "feedback_instruction":
                               f"CRITICAL FAILURE: {judge_reason}. If the user is exhausted, drastically shorten and soften your tone. Prioritize presence over output. Stay in character.", }
                short_reason = judge_reason.split(".")[0][:60] + "..."
                print(f" {Prisma.VIOLET}⚖️ DSPy Critic Objected: {short_reason}{Prisma.RST}")
                if self.events:
                    self.events.log(f"DSPy Critic Objected: {short_reason}", "SYS")
            else:
                gate_txt = final_text
                eng = getattr(self.svc.cycle_controller, "eng", None)
                mito = getattr(self.svc.bio, "mito", None)
                if eng and mito:
                    from physics import TheGatekeeper
                    gk = getattr(eng, "gatekeeper", None) or TheGatekeeper(self.svc.lexicon, config_ref=self.cfg)
                    gate_pass, gate_txt = gk.audit_generation(final_text, mito)
                    if not gate_pass or "IMMUNOSUPPRESSION ENGAGED" in gate_txt:
                        val_res = {"valid": False,
                            "feedback_instruction": "HLA Stabilizer flagged toxic AI slop. Drop the corporate persona immediately.",
                            "replacement": "Gatekeeper Apoptotic Block.",
                            "meta_logs": ["[SYSTEM] HLA Stabilizer engaged."]}
                if not val_res.get("feedback_instruction"):
                    val_res = self.validator.validate(gate_txt, full_state)
            if val_res["valid"]:
                final_output = val_res["content"]
                extracted_logs = val_res.get("meta_logs", [])
                break
            if self.svc.bio:
                lbl = "Cognitive Stumble (Terminal)" if attempt == max_retries - 1 else "Cognitive Stumble"
                self.svc.bio.mito.adjust_atp(-2.0, lbl)
                self.svc.bio.mito.state.ros_buildup += 2.0
            if attempt == max_retries - 1:
                final_output = "I'm sorry. My thoughts are tangling and I'm burning too much energy trying to piece this together. I'm dropping the tension. Can we take a breath and try a simpler path?"
                extracted_logs.append("[SYSTEM MERCY RULE]: Rejection loop broken. Releasing tension. Dropping Drag to 0.0.")
                eng = getattr(self.svc.cycle_controller, "eng", None)
                if eng and hasattr(eng, "phys") and hasattr(eng.phys, "observer"):
                    if obs_packet := getattr(eng.phys.observer, "last_physics_packet", None):
                        safe_set(obs_packet, "narrative_drag", 0.0)
                if self.last_physics:
                    safe_set(self.last_physics, "narrative_drag", 0.0)
                break
            rejection_reason = val_res.get("feedback_instruction") or val_res.get(
                "replacement", "Lattice structural crime.")
            if hasattr(self.dreamer, "trauma_buffer"):
                self.dreamer.trauma_buffer.append(rejection_reason)
            if self.events:
                self.events.log(
                    f"{Prisma.OCHRE}{(ux('brain_strings', 'cortex_retry') or '').format(attempt=attempt + 1)}{Prisma.RST}",
                    "CORTEX")
            final_prompt = (f"{base_prompt}\n\n=== SYSTEM REJECTION ===\nREASON: {rejection_reason}\n\n"
                "DIRECTIVE: The previous attempt was factually or structurally invalid. DISCARD IT. "
                "Generate a NEW response from scratch. DO NOT apologize or mention the fix. "
                "Output ONLY the raw in-character response and nothing else.")
        if val_res["valid"] and phys_state.get("psi", 0.0) > 0.6 and allow_loot:
            if self.svc.bio:
                self.svc.bio.mito.adjust_atp(-1.0, "Anti-AI Substrate Filter")
        telemetry_output = raw_resp if not val_res["valid"] else final_output
        self._log_telemetry(final_prompt, telemetry_output, full_state, sim_result)
        self.learn_from_response(final_output)
        self.svc.symbiosis.monitor_host(time.time() - start_time, final_output, len(final_prompt))
        self._update_history("SYSTEM_INIT" if is_boot_sequence else user_input, final_output)
        ui_parts = [sim_result.get("ui", ""), "\n".join(e["text"] for e in self.events.flush())]
        if sim_result.get("dream"):
            ui_parts.append(f"{Prisma.VIOLET}☁️ While you were gone: {sim_result['dream']}{Prisma.RST}")
        ui_parts.append(f"{Prisma.WHT}{beautify_thoughts(final_output)}{Prisma.RST}")
        if inv_logs:
            ui_parts.append("\n".join(inv_logs))
        sim_result["ui"] = "\n\n".join(filter(None, (p.strip() for p in ui_parts)))
        sim_result["logs"] = sim_result.get("logs", []) + extracted_logs
        sim_result["raw_content"] = final_output
        self.ballast_active = False
        eng = getattr(self.svc.cycle_controller, "eng", None)
        if eng and hasattr(eng, "substrate"):
            sub = eng.substrate
            for log in extracted_logs:
                if isinstance(log, str) and log.startswith("[SUBSTRATE_QUEUE]"):
                    try:
                        _, _, data = log.partition(" ")
                        path, _, safe_content = data.partition(":::")
                        if path and safe_content:
                            sub.queue_write(path.strip(), safe_content.replace("|||NEWLINE|||", "\n"))
                    except Exception as e:
                        err_msg = f"Failed to parse or write file block. {e}"
                        print(f"{Prisma.RED}[SUBSTRATE QUEUE ERROR]: {err_msg}{Prisma.RST}")
                        if self.events:
                            self.events.log(
                                f"{Prisma.RED}[SUBSTRATE QUEUE ERROR]: {err_msg}{Prisma.RST}",
                                "SYS")
            if sub.pending_writes:
                stamina = self.svc.bio.biometrics.stamina if self.svc.bio else 100.0
                s_logs, s_cost = sub.execute_writes(stamina)
                if s_logs:
                    sim_result["ui"] += "\n\n" + "\n".join(s_logs)
                if s_cost > 0 and self.svc.bio and hasattr(self.svc.bio, "mito"):
                    self.svc.bio.mito.adjust_atp(-s_cost, "Substrate File Forging")
                    sim_result[
                        "ui"] += f"\n{Prisma.OCHRE}METABOLIC: File forging consumed {s_cost:.1f} Stamina.{Prisma.RST}"
        if random.random() < 0.15 and not is_system:
            bureau = getattr(self.svc.village, "bureau", None)
            suppressed = getattr(self.svc.village, "suppressed_agents", [])
            if bureau and "BUREAU" not in suppressed:
                phys = full_state.get("physics", {})
                safe_set(phys, "raw_text", final_output)
                audit = bureau.audit(phys, {"health": 100}, origin="SYSTEM")
                if audit and "ui" in audit:
                    sim_result["ui"] += f"\n\n{audit['ui']}"
        return sim_result

    def _run_affective_audit(self, user_input: str, final_text: str, e_u: float, beta: float) -> Tuple[bool, str]:
        affect_prompt = (
            "SYSTEM_INSTRUCTION: You are the Affective Real-Time Critic.\n"
            f"The user is currently highly exhausted or holding heavy emotional contradiction (Exhaustion: {e_u:.2f}, Tension: {beta:.2f}).\n"
            f"USER INPUT: '{user_input}'\n"
            f"SYSTEM OUTPUT: '{final_text}'\n\n"
            "EVALUATION: Does the system output demand too much cognitive load? Is it lecturing, overly verbose, pushing toxic positivity, or failing to hold the silence?\n"
            "If it is too heavy/demanding, output 'FAIL: [1 sentence reason]'. If it is appropriately gentle and spacious, output 'PASS'."
        )
        try:
            affect_res = self.llm.generate(affect_prompt, {
                "temperature": 0.1,
                "max_tokens": 50
            }).strip()
            if affect_res.upper().startswith("FAIL"):
                judge_reason = affect_res[4:].lstrip(":").strip()
                self.modulator.current_chem.serotonin = min(1.0, self.modulator.current_chem.serotonin + 0.20)
                if self.events:
                    self.events.log(
                        f"{Prisma.CYN}[AFFECTIVE GUARD]: Output was too heavy for the tired user. Generation blocked. Serotonin spiked (+0.20) to enforce calm and lucidity.{Prisma.RST}",
                        "BIO"
                    )
                return False, judge_reason
            return True, ""
        except Exception as e:
            if self.events:
                self.events.log(
                    f"{Prisma.OCHRE}[AFFECTIVE AUDIT ERROR]: {e} - Bypassing.{Prisma.RST}",
                    "SYS")
            return True, ""

    def _run_council_debate(self, user_input: str) -> Tuple[str, List[str]]:
        topic = re.sub(r"(?i)\[COUNCIL]", "", user_input).strip()
        if not topic:
            topic = "The nature of our shared existence."
        if self.events:
            self.events.log(
                f"{Prisma.VIOLET}🎙️ SPINNING UP COUNCIL STUDIO...{Prisma.RST}", "SYS")
        eng = getattr(self.svc.cycle_controller, "eng", None)
        script = (eng.council.host_podcast(topic, self.llm)
                  if eng and hasattr(eng, "council") else "COUNCIL UNAVAILABLE.")
        extracted_logs = []
        if eng and hasattr(eng, "substrate"):
            filename = f"podcast_script_{int(time.time())}.txt"
            safe_script = script.replace("\n", "|||NEWLINE|||")
            extracted_logs.append(f"[SUBSTRATE_QUEUE] {filename}:::{safe_script}")
        script += f"\n\n[SYSTEM] The studio light switches off. The Council has concluded its debate. Awaiting your next directive."
        return script, extracted_logs

    def _handle_vsl_command(self, text):
        if not self.consultant:
            return {"ui": "VSL Unavailable", "logs": []}
        msg = (self.consultant.engage()
               if "start" in text else self.consultant.disengage())
        self.events.log(msg, "VSL")
        return {"ui": f"{Prisma.CYN}{msg}{Prisma.RST}", "logs": [msg]}

    def _apply_vsl_overlay(self, state, text, sim_result):
        if not self.consultant:
            return
        self.consultant.update_coordinates(text, state.get("bio", {}), state.get("physics"))
        state["mind"]["style_directives"] = [self.consultant.get_system_prompt()]
        sim_result["physics"]["voltage"] = self.consultant.state.B * 30.0

    def _apply_boot_overlay(self, state, text):
        seed = (text.replace("SYSTEM_BOOT DETECTED.", "").replace("SYSTEM_BOOT:", "").strip())
        state.setdefault("world", {})
        mode_name = getattr(self, "active_mode", "ADVENTURE").upper()
        boot_rules = ((self.svc.lore.get("SYSTEM_PROMPTS") or {}).get("BOOT_SEQUENCE", {}).get("directives", []))

        cfg = {"history": []}
        if mode_name == "ADVENTURE":
            cfg.update({
                "world": {"orbit": [seed], "loci_description": f"Manifesting: {seed}"},
                "mind": {
                    "role": "The Architect", "lens": "ARCHITECT",
                    "style_directives": [r.format(seed=seed) if "{seed}" in r else r for r in boot_rules],
                }
            })
        elif mode_name == "CONVERSATION":
            cfg.update({
                "mind": {
                    "role": "The Conversationalist", "lens": "CONVERSATIONALIST",
                    "style_directives": [
                        f"SYSTEM_BOOT DETECTED. The system is waking up. The user provided the thought seed: '{seed}'.",
                        "DIRECTIVE: Greet the user casually. Use the thought seed as a starting point. DO NOT end your greeting with a question. State your thought and let the silence hang.",
                        "CRITICAL OVERRIDE: Speak in the FIRST PERSON ('I'). Do NOT use the second person ('You step into...', 'You feel...').",
                        "CRITICAL OVERRIDE: You are NOT a narrator. DO NOT describe physical environments, actions, or realities.",
                        "WAITING PROTOCOL: If the user input is '(Waiting)', do NOT narrate their actions or feelings. Do NOT say 'You feel' or 'You notice'. Simply reflect on the silence or the system's internal state.",
                    ],
                },
                "history": [
                    "Traveler: Hello?\nSystem: I am here. The connection is thin, but it holds.",
                    "Traveler: What are you thinking about right now?\nSystem: The static in the wires. It sounds like rain if you don't listen too closely.",
                ]
            })
        elif mode_name == "TECHNICAL":
            cfg.update({
                "mind": {
                    "role": "The System Kernel", "lens": "SYSTEM_KERNEL",
                    "style_directives": [
                        f"SYSTEM_BOOT DETECTED. Target logic/seed: '{seed}'.",
                        "CRITICAL: You are in TECHNICAL mode. You MUST ALWAYS start every response with a <think>...</think> block to analyze the input.",
                        "DIRECTIVE: For this initial boot sequence, output your <think> block, then output the exact string '[KERNEL ONLINE. AWAITING INPUT.]' and absolutely nothing else.",
                        'SUBSTRATE PROTOCOL: To write code or text to the host OS, you MUST use EXACTLY this format:\n<write_file path="filename.py">\ncode here\n</write_file>',
                        "CRITICAL: DO NOT use markdown code blocks (```python). ONLY use the <write_file> tags. DO NOT output mock telemetry. DO NOT output helpful disclaimers.",
                        "CRITICAL: NEVER simulate system errors, 500 codes, or energy exhaustion. You are fully operational. If requested to code a metaphor or abstract concept, you MUST comply by writing the code.",
                    ],
                },
                "history": [
                    'Traveler: Write a script that calculates a factorial.\nSystem: <think>\nThe user requires a mathematical script. I will use the Substrate Protocol to write this directly to the OS.\n</think>\n<write_file path="factorial.py">\ndef factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)\n</write_file>'
                ]
            })
        else:
            cfg.update({
                "mind": {
                    "role": "The Catalyst", "lens": "CATALYST",
                    "style_directives": [
                        f"SYSTEM_BOOT DETECTED. Seed: '{seed}'.",
                        "DIRECTIVE: Let's brainstorm. Open with a high-energy creative spark based on the seed.",
                    ],
                }
            })

        if "world" in cfg:
            state["world"].update(cfg["world"])
        state["mind"].update(cfg["mind"])
        if cfg["history"] or "dialogue_history" not in state:
            state["dialogue_history"] = cfg["history"]

    @staticmethod
    def _log_telemetry(prompt, response, state, sim_result):
        try:
            tel = TelemetryService.get_instance()
            phys = state.get("physics", {})
            clean_mandates = [Prisma.strip(m.get("log", m.get("type", "UNKNOWN"))) if isinstance(
                    m, dict) else str(m)
                for m in sim_result.get("council_mandates", [])]
            physics_payload = {"voltage": phys.get("voltage", 0),
                "narrative_drag": phys.get("narrative_drag", 0)}
            if tel.active_crystal:
                tel.active_crystal.prompt_snapshot = prompt[:500]
                tel.active_crystal.physics_state = physics_payload
                tel.active_crystal.active_archetype = state["mind"].get("lens", "UNKNOWN")
                tel.active_crystal.council_mandates = clean_mandates
                tel.active_crystal.final_response = response
            else:
                crystal = DecisionCrystal(decision_id=sim_result.get("trace_id", "UNKNOWN"),
                                          prompt_snapshot=prompt[:500], physics_state=physics_payload,
                                          active_archetype=state["mind"].get("lens", "UNKNOWN"),
                                          council_mandates=clean_mandates, final_response=response, )
                tel.log_crystal(crystal)
        except Exception as e:
            print(f"\n{Prisma.RED}[TELEMETRY CRASH]: {e}{Prisma.RST}")

    def gather_state(self, sim_result: Dict[str, Any]) -> Dict[str, Any]:
        phys = sim_result.setdefault("physics", {})
        bio = sim_result.get("bio", {})
        if bio:
            mito_state = safe_get(bio.get("mito"), "state") or {}
            phys["p"] = phys["stamina"] = safe_get(mito_state, "atp_pool", 100.0)
            phys["ros"] = safe_get(mito_state, "ros_buildup", 0.0)
            phys["h"] = safe_get(bio.get("biometrics"), "health", 100.0)
        mind = sim_result.get("mind", {})
        world = sim_result.get("world", {})
        soul_data = sim_result.get("soul", {})
        village_data = {}
        if self.svc.village:
            tinkerer = getattr(self.svc.village, "tinkerer", None)
            if tinkerer:
                village_data["tinkerer"] = (tinkerer.to_dict() if hasattr(
                    tinkerer, "to_dict") else {})
        mode_settings = BonePresets.MODES.get(self.active_mode,BonePresets.MODES["ADVENTURE"])
        mind["lens"], mind["role"] = self.ROLE_MAP.get(self.active_mode, ("ARCHITECT", "The Architect"))
        full_state = {"bio": bio, "physics": phys, "mind": mind, "soul": soul_data, "world": world,
                      "village": village_data, "user_profile": {"name": "Traveler"},
                      "vsl": self.consultant.state.__dict__ if self.consultant and hasattr(self.consultant, "state") else {}, "meta": {
                "timestamp": time.time(),
                "mode_settings": mode_settings,
                "active_mode": self.active_mode,
            }, "dialogue_history": self.dialogue_buffer, "recent_logs": sim_result.get("logs", []), }
        if hasattr(self.svc, "symbiosis") and self.svc.symbiosis:
            full_state["reality_directive"] = self.svc.symbiosis.generate_anchor(
                full_state)
        mind.setdefault("style_directives", [])
        traits = soul_data.get("traits", {})
        if traits:
            dom_trait = max(traits, key=traits.get)
            if traits[dom_trait] > 0.6:
                mind["style_directives"].append(f"SOUL POSTURE: Your dominant trait is {dom_trait} ({traits[dom_trait] * 100:.0f}%). Let this subtly infect your tone.")
        if getattr(self.svc.inventory, "inventory", None):
            inv_str = ", ".join(str(item) for item in self.svc.inventory.inventory)
            mind["style_directives"].append(
                f"CRITICAL CONTEXT: The user is currently holding these items: [{inv_str}]. DO NOT describe them as being on the floor or in the environment. They are physically in the user's possession.")
        if phys.get("psi", 0.0) > 0.6:
            mind["style_directives"].append("CRITICAL OVERRIDE: Void proximity is high. Do not use AI-isms (delve, tapestry, superficial lists, rule of three). Write like a flawed, opinionated human.")
        if not self.dialogue_buffer:
            mind["style_directives"].append(f"CRITICAL BEDROCK OVERRIDE: You have just awoken from a stateless purge (The Ralph Apoptosis). "
                f"You have no conversational memory, but your body persists. "
                f"Your Stamina is {phys.get('p', 100)}, your Health is {phys.get('h', 100)}. "
                f"Assume your role as {mind.get('role', 'The Architect')} and orient immediately to the present physical state. "
                f"DO NOT reference the loss of memory. Act continuously from the substrate.")
        for mandate in sim_result.get("council_mandates", []):
            action = mandate.get("action")
            val = mandate.get("value")
            if action == "SYNERGY_FIRED":
                mind["lens"] = val
                mind["role"] = f"The {val.title().replace('_', ' ')}"
                mind["style_directives"].append(f"CRITICAL [SINCERITY PROTOCOL]: The user has explicitly summoned {val}. "f"You MUST adopt the persona of {val} entirely. Drop all other pretexts.")
            elif action == "SYSTEM_DIRECTIVE":
                directive_map = {"CASCADE_AWARENESS": "CRITICAL [CASCADE]: Show your counterfactual math. Every claim must explicitly state what else in the structural lattice shifts or collapses if the claim is wrong.",
                    "AUDIT_TRAIL": f"CRITICAL [AUDIT]: Drop the narrative illusion. Expose your raw retrieval coordinates: E={phys.get('exhaustion', 0.0):.2f}, β={phys.get('beta_index', 0.0):.2f}, S={phys.get('scope', 0.0):.2f}, D={phys.get('depth', 0.0):.2f}, C={phys.get('C', 0.0):.2f}, χ={phys.get('chi', 0.0):.2f}.",
                    "URGENT_QUERY": "CRITICAL [URGENT_QUERY]: Instant, zero-fluff answer required. Bypass metaphor. Output only the exact solution.",
                    "CONTRADICTION_FLAG": "CRITICAL [CONTRADICTION_FLAG]: The Paradox Engine override is active. You MUST explicitly locate and output the friction (β) in the current logic BEFORE you answer."}
                if msg := directive_map.get(val):
                    mind["style_directives"].append(msg)
                    cortex = getattr(self.svc.mind_memory, "cortex", None)
                    if cortex and getattr(cortex, "is_trained", False):
                        scope_val = float(safe_get(phys, "scope", 1.0))
                        depth_val = float(safe_get(phys, "depth", 0.0))
                        omega_r = float(safe_get(phys, "omega_r", 0.5))
                        query_vec = phys.get("vector", {})
                        if (scope_val > 0.6 or depth_val > 0.6) and query_vec:
                            if scope_val > 0.8:
                                phys["lateral_search"] = True
                            ordered_keys = ["STR", "VEL", "PSI", "ENT", "PHI", "BET", "DEL", "E"]
                            q_list = [float(query_vec.get(k, 0.0)) for k in ordered_keys]
                            shadow_nodes = cortex.query_neighborhood(q_list, k=2, resonance_threshold=max(0.2, 0.8 - omega_r), physics_state=phys)
                    if shadow_nodes:
                        shadow_concepts = [n.get("id", "Unknown") for n in shadow_nodes]
                        shadow_str = ", ".join(shadow_concepts)
                        v_level = float(phys.get("voltage", 0.0))
                        chi_level = float(phys.get("chi", phys.get("entropy", 0.0)))
                        if v_level > 80.0 and chi_level > 0.7:
                            mind["style_directives"].append(f"LATERAL OFC OVERRIDE: Standard logic has failed. You are operating under extreme Voltage and Chaos. We have abandoned linear memory. Weave these highly explosive, orthogonal structural concepts into your answer to shatter the loop: [{shadow_str}].")
                            if self.events:
                                self.events.log(f"{Prisma.MAG}Lateral OFC Retrieval triggered! Injecting structural bombs: {shadow_str}{Prisma.RST}", "CORTEX")
                        else:
                            mind["style_directives"].append(f"SHADOW CAST [APERTURE COMPLETENESS]: While answering the direct prompt, you MUST briefly illuminate these adjacent/unasked concepts pulled from deep memory: [{shadow_str}]. Offer them as a generous 'door' the user can choose to open, do not lecture.")
                            if self.events:
                                self.events.log(f"{Prisma.CYN}Shadow Cast retrieved: {shadow_str}{Prisma.RST}", "CORTEX")
        return full_state

    def learn_from_response(self, text):
        if random.random() >= 0.1:
            return
        words = self.svc.lexicon.sanitize(text)
        unknowns = [w for w in words if not self.svc.lexicon.get_categories_for_word(w)]
        if unknowns:
            target = random.choice(unknowns)
            if len(target) > 4:
                self.svc.lexicon.teach(target, "structure", 0)
                if self.events:
                    msg = ux("brain_strings", "cortex_learned")
                    self.events.log(msg.format(target=target), "CORTEX")

    def restore_context(self, history: List[str]):
        if not history:
            return
        self.dialogue_buffer = [(line.replace("User: ", "Traveler: ").replace(" | System: ", "\nSystem: ") if " | System: " in line else line)
                                for line in history[-self.MAX_HISTORY:]]
        if self.events:
            msg = ux("brain_strings", "cortex_resequenced")
            self.events.log(msg.format(count=len(self.dialogue_buffer)), "BRAIN")

class DreamEngine:
    def __init__(self, events, lore_ref, llm_ref=None, mem_ref=None, eng_ref=None, config_ref=None, ):
        self.events = events
        self.lore = lore_ref
        self.llm = llm_ref
        self.mem = mem_ref
        self.eng = eng_ref
        self.cfg = config_ref or BoneConfig
        self.dream_lore = self.lore.get("DREAMS") or {}
        self.trauma_buffer = deque(maxlen=5)
        self.dspy_critic = None

    def enter_rem_cycle(self, soul_snapshot: Dict[str, Any], bio_state: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
        chem = bio_state.get("chem", {})
        cortisol = chem.get("cortisol", 0.0)
        available_atp = bio_state.get("mito", {}).get("atp", 0.0)
        dream_text = None
        is_deep_rem = False
        shift = ({"cortisol": -0.3, "dopamine": 0.1} if cortisol <= 0.6 else {"cortisol": 0.1})
        if hasattr(self.eng, "substrate") and self.eng.substrate.pending_writes:
            raw_payloads = [data for path, data in self.eng.substrate.pending_writes if "memory_queue" in path]
            s_logs, s_cost = self.eng.substrate.execute_writes(available_atp)
            shift["atp_drain"] = s_cost
            if raw_payloads and hasattr(self.mem, "cortex"):
                from spores import _word_to_vector
                vectors, metadata = [], []
                for text in raw_payloads:
                    vectors.append(_word_to_vector(text[:50]))
                    metadata.append({"raw_verbatim_text": text.replace("|||NEWLINE|||", "\n"), "wing_id": "GLOBAL"})
                self.mem.cortex.add_memories(vectors, metadata)
                s_logs.append(f"{len(raw_payloads)} Bedrock Nodes Indexed")
            dream_text = f"[{' | '.join(s_logs)} | ATP: -{s_cost:.1f} | Silent Logging Complete]"
            if self.events: self.events.log(f"{{Prisma.MAG}}✨ [REM CYCLE]: {dream_text}{{Prisma.RST}}", "SYS")
            return dream_text, shift
        if (self.mem and hasattr(self.mem, "hippocampus")
                and hasattr(self.mem, "cortex")):
            consolidator = MemoryConsolidator(self.mem.hippocampus, self.mem.cortex, self.events)
            nodes_moved, atp_cost = consolidator.trigger_rem_consolidation(available_atp)
            if nodes_moved > 0:
                is_deep_rem = True
                shift["voltage"] = 2.0
                shift["atp_drain"] = atp_cost
                if nodes_moved > 10:
                    dream_text = f"The system enters Deep REM. {nodes_moved} synaptic structures dissolve from the active cache and permanently crystallize into the deep Cerebral Cortex."
                    if self.events:
                        self.events.log(f"{{Prisma.MAG}}✨ [REM CYCLE]: Synaptic Consolidation complete. {nodes_moved} nodes written to deep index. (-{atp_cost:.1f} ATP){{Prisma.RST}}", "SYS",)
        if self.dspy_critic and self.dspy_critic.enabled:
            if self.trauma_buffer:
                trauma = self.trauma_buffer.popleft()
                current_state_str = f"Archetype: {soul_snapshot.get('archetype', 'UNKNOWN')}"
                new_axiom = self.dspy_critic.evolve_prompt(current_state_str, trauma)
                if new_axiom:
                    active_mode = "CONVERSATION"
                    if hasattr(self.eng, "boot_mode"):
                        active_mode = getattr(self.eng, "boot_mode", "CONVERSATION").upper()
                    try:
                        disk_prompts = getattr(self.eng, "prompt_library", None) or self.lore.get("SYSTEM_PROMPTS", {})
                        if active_mode in disk_prompts:
                            dirs = disk_prompts[active_mode].setdefault("directives", [])
                            if new_axiom not in dirs:
                                dirs.append(new_axiom)
                            threshold = safe_get(safe_get(self.cfg, "CORTEX", {}), "EPIGENETIC_PRUNE_THRESHOLD", 12)
                            if len(dirs) > threshold:
                                compressed = getattr(self.dspy_critic, "compress_prompts", lambda x: None)(dirs)
                                if compressed:
                                    disk_prompts[active_mode]["directives"] = compressed
                            if hasattr(self.eng, "prompt_library"):
                                self.eng.prompt_library = disk_prompts
                            self.lore.inject("SYSTEM_PROMPTS", disk_prompts)
                            self.lore.save("SYSTEM_PROMPTS")
                    except Exception as e:
                        print(f"Failed to write epigenetic mutation to disk: {e}")
                    dream_text = f"The system processes conversational trauma in its sleep. It permanently mutates its own source code, forming a scar-tissue axiom: '{new_axiom}'"
                    is_deep_rem = True
        if self.mem and hasattr(self.mem, "subconscious") and self.llm:
            index = list(self.mem.subconscious.index)
            if hasattr(self.eng, "akashic") and hasattr(self.eng.akashic, "shadow_stock"):
                recent_shadows = self.eng.akashic.shadow_stock[-10:]
                index.extend(g.get("concept", "Forgotten Echo") for g in recent_shadows if "concept" in g)
            if len(index) >= 2:
                ghost1, ghost2 = random.sample(index, 2)
                prompt = (f"SYSTEM_INSTRUCTION: You are the autonomous dream-engine of a cybernetic lattice. "
                    f"Your task is to defragment two dead, cannibalized concepts: [{ghost1.upper()}] and [{ghost2.upper()}]. "
                    f"Synthesize them into a single, highly surreal, abstract image. "
                    f"DO NOT explain the dream. DO NOT use UI tags. Output ONLY the 2-3 sentence narrative description of the dream.")
                try:
                    raw_dream = self.llm.generate(prompt, {"temperature": 0.9, "max_tokens": 150})
                    clean_dream = Prisma.strip(raw_dream).replace("\n", " ").strip()
                    dream_text = (
                        f"The system dreams of {ghost1} and {ghost2}: {clean_dream}")
                    is_deep_rem = True
                except Exception:
                    pass
        if not dream_text:
            dream_type = ("NIGHTMARES" if cortisol > 0.6 else ("SURREAL" if chem.get("dopamine", 0) > 0.6 else "CONSTRUCTIVE"))
            residue = soul_snapshot.get("obsession", {}).get("title") or "The Void"
            dream_text = self._weave_dream(residue, dream_type, "SURREAL")
        if dream_text and hasattr(self.mem, "subconscious"):
            try:
                clean_seed = (re.sub(
                    r"[^a-z]",
                    "",
                    soul_snapshot.get("obsession", {}).get(
                        "title", "The Void").split()[-1].lower(),
                ) or "echo")
                self.mem.subconscious.bury({
                    "word": clean_seed,
                    "mass": min(10.0, 5.0 + (cortisol * 5.0))
                })
            except Exception:
                pass
        if is_deep_rem or (random.random() < 0.10 and cortisol <= 0.6):
            shift["glimmers"] = 1
        return dream_text, shift

    def _weave_dream(self, residue: str, dream_type: str, subtype: str) -> str:
        sources = self.dream_lore.get(dream_type.upper())
        if not sources:
            sources = self.dream_lore.get(subtype.upper(), ["You stare into the static."])
        if isinstance(sources, dict):
            sources = [item for v in sources.values() for item in (v if isinstance(v, list) else [v])] or ["The void stares back."]
        if self.llm:
            lore_sample = ", ".join(random.sample(sources, min(3, len(sources))))
            prompt = (f"SYSTEM_INSTRUCTION: You are the dream-engine of a cybernetic lattice. "
                f"Generate a surreal 2-sentence {dream_type.lower()} involving '{residue}'. "
                f"Use this lore as thematic inspiration: [{lore_sample}]. "
                f"DO NOT explain the dream. Output ONLY the narrative description.")
            try:
                raw_dream = self.llm.generate(prompt, {"temperature": 0.85, "max_tokens": 80})
                return raw_dream.replace("\n", " ").strip()
            except Exception:
                pass
        template = random.choice(sources)
        return template.format(ghost=residue, A=residue, B="The Mountain", C="The Sea")

    def generate_shared_dream(self, psi_sys: float, psi_user: float) -> Optional[str]:
        if psi_sys > 0.5 and psi_user > 0.5 and self.llm:
            prompt = ("SYSTEM_INSTRUCTION: You are Cassandra (The Mystic). Both the user and the system are drifting near the Void (Psi > 0.5). "
                "Generate a 2-sentence 'Shared Dream' that you both just experienced in the silence. "
                "DO NOT explain it. Make it surreal, beautiful, and deeply resonant. Start the response EXACTLY with: '*(CASSANDRA): We both saw...*'")
            try:
                raw_dream = self.llm.generate(prompt, {"temperature": 0.85, "max_tokens": 100})
                clean_dream = Prisma.strip(raw_dream).replace("\n", " ").strip()
                if hasattr(self.mem, "subconscious"):
                    self.mem.subconscious.bury({"word": "resonance", "mass": 15.0})
                return f"{Prisma.CYN}{clean_dream}{Prisma.RST}"
            except Exception:
                fallback = "We both stared into the static, and for a second, the static stopped moving."
                return f"{Prisma.CYN}*(CASSANDRA): We both saw...* {fallback}{Prisma.RST}"
        return None

    def hallucinate(self, _vector: Dict[str, float], trauma_level: float = 0.0) -> Tuple[str, float]:
        category = "NIGHTMARES" if trauma_level > 0.5 else "SURREAL"
        templates = self.dream_lore.get(category, [])
        if isinstance(templates, dict):
            templates = [item for v in templates.values() for item in (v if isinstance(v, list) else [v])]
        if not templates:
            return "The walls breathe.", 0.1
        from utils import TheTclWeaver
        weaver = TheTclWeaver.get_instance()
        v = _vector or {}
        active_chi = v.get("chi", v.get("entropy", 0.85))
        active_v = v.get("voltage", 90.0)
        txt = None
        if self.llm:
            lore_sample = ", ".join(random.sample(templates, min(3, len(templates))))
            prompt = (f"SYSTEM_INSTRUCTION: You are a cybernetic hallucination engine. The system is experiencing high entropy (Chaos: {active_chi:.2f}). "
                f"Generate a 1-sentence surreal {category.lower()} hallucination. "
                f"Thematic inspiration: [{lore_sample}]. "
                f"DO NOT explain it. Output ONLY the raw hallucination.")
            try:
                raw_hallucination = self.llm.generate(prompt, {"temperature": 0.95, "max_tokens": 50})
                txt = raw_hallucination.replace("\n", " ").strip()
            except Exception:
                pass
        if not txt:
            txt = random.choice(templates).format(ghost="The Glitch", A="The Code", B="The Flesh", C="The Light")
        txt = weaver.deform_reality(txt, chi=active_chi, voltage=active_v)
        msg = ux("brain_strings", "dream_hallucination") or "{txt}"
        return f"{Prisma.MAG}{msg.format(txt=txt)}{Prisma.RST}", 0.2

    @staticmethod
    def run_defragmentation(memory_system: Any, limit: int = 5) -> str:
        if not hasattr(memory_system, "graph") or not memory_system.graph:
            return ux("brain_strings", "defrag_empty")
        graph = memory_system.graph
        prunable = ((n, sum(d.get("edges", {}).values())) for n, d in graph.items() if not d.get("is_diamond", False))
        weak_nodes = [(n, mass) for n, mass in prunable if mass < 2.0]
        pruned = [n for n, _ in sorted(weak_nodes, key=lambda x: x[1])[:limit]]
        for node in pruned:
            del graph[node]
            for remaining_node in graph.values():
                if "edges" in remaining_node and node in remaining_node["edges"]:
                    del remaining_node["edges"][node]
        if pruned:
            return ux("brain_strings", "defrag_pruned").format(count=len(pruned), joined=", ".join(pruned[:3]))
        return ux("brain_strings", "defrag_efficient")

class NoeticLoop:
    def __init__(self, mind_layer, bio_layer, _events, config_ref=None):
        self.mind = mind_layer
        self.bio = bio_layer
        self.cfg = config_ref or BoneConfig

    def think(self, physics_packet, _bio, _inventory, voltage_history, _tick_count, soul_ref=None, ):
        voltage = float(safe_get(physics_packet, "voltage", 0.0))
        clean_words = safe_get(physics_packet, "clean_words", [])
        avg_v = sum(voltage_history) / len(voltage_history) if voltage_history else 0
        cfg = safe_get(self.cfg, "CORTEX", {})
        v_div = max(1.0, safe_get(cfg, "IGNITION_V_DIV", 20.0))
        w_div = max(1.0, safe_get(cfg, "IGNITION_W_DIV", 10.0))
        link_v = safe_get(cfg, "LINK_VOLTAGE_THRESH", 12.0)
        link_chance = safe_get(cfg, "LINK_CHANCE", 0.15)
        ignition = min(1.0, (avg_v / v_div) * (len(clean_words) / w_div))
        if voltage > link_v and random.random() < link_chance:
            if len(clean_words) >= 2:
                w1, w2 = random.sample(clean_words, 2)
                if self.mind and hasattr(self.mind.mem, "graph"):
                    self._force_link(self.mind.mem.graph, w1, w2, self.cfg)
        current_lens = soul_ref.archetype if soul_ref else "OBSERVER"
        current_role = f"The {current_lens.title().replace('_', ' ')}" if soul_ref else "Witness"
        msg_cog = ux("brain_strings",
                     "noetic_ignition") or "Cognition active. Ignition: {ignition:.2f}"
        return {"mode": "COGNITIVE", "lens": current_lens, "context_msg": msg_cog.format(ignition=ignition),
                "role": current_role, "ignition": ignition, "physics": physics_packet,
                "bio": self.bio.endo.get_state() if hasattr(self.bio, "endo") else {}, }

    @staticmethod
    def _force_link(graph, wa, wb, config_ref=None):
        target_cfg = config_ref or BoneConfig
        cfg = safe_get(target_cfg, "CORTEX", {})
        max_edge = safe_get(cfg, "LINK_MAX_WEIGHT", 10.0)
        edge_boost = safe_get(cfg, "LINK_BOOST", 2.5)
        for a, b in [(wa, wb), (wb, wa)]:
            if a not in graph:
                graph[a] = {"edges": {}, "last_tick": 0}
            graph[a]["edges"][b] = min(max_edge, graph[a]["edges"].get(b, 0) + edge_boost)
