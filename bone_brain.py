"""bone_brain.py"""

import math
import random
import time
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

from bone_composer import LLMInterface, PromptComposer, ResponseValidator
from bone_presets import BoneConfig, BonePresets
from bone_core import EventBus, TelemetryService, LoreManifest, ux
from bone_gui import beautify_thoughts
from bone_symbiosis import SymbiosisManager
from bone_types import Prisma, DecisionCrystal


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

@dataclass
class ChemicalState:
    dopamine: float = 0.2
    cortisol: float = 0.1
    adrenaline: float = 0.1
    serotonin: float = 0.2

    def homeostasis(self, rate: float = 0.1):
        cfg = BoneConfig.CORTEX
        targets = {"dopamine": cfg.RESTING_DOPAMINE, "cortisol": cfg.RESTING_CORTISOL,
                   "adrenaline": cfg.RESTING_ADRENALINE, "serotonin": cfg.RESTING_SEROTONIN, }
        for attr, target in targets.items():
            current = getattr(self, attr)
            delta = (target - current) * rate
            setattr(self, attr, current + delta)

    def mix(self, new_state: Dict[str, float], weight: float = 0.5):
        mapping = [("DOP", "dopamine"), ("COR", "cortisol"), ("ADR", "adrenaline"), ("SER", "serotonin"), ]
        for key, attr in mapping:
            val = new_state.get(key, 0.0)
            current = getattr(self, attr)
            setattr(self, attr, (current * (1.0 - weight)) + (val * weight))

BrainConfig = BoneConfig.CORTEX

class NeurotransmitterModulator:
    def __init__(self, bio_ref, events_ref=None):
        self.bio = bio_ref
        self.events = events_ref
        self.current_chem = ChemicalState()
        self.last_mood = "NEUTRAL"
        cfg = getattr(BoneConfig, "CORTEX", None)
        self.BASE_TOKENS = getattr(cfg, "BASE_TOKENS", 720) if cfg else 720
        self.MAX_TOKENS = getattr(cfg, "MAX_TOKENS", 4096) if cfg else 4096
        self.SELF_CARE_THRESHOLD = getattr(cfg, "SELF_CARE_THRESHOLD", 10) if cfg else 10
        self.starvation_ticks = 0

    def modulate(
            self,
            base_voltage: float,
            latency_penalty: float = 0.0,
            physics_state: Dict[str, float] = None,) -> Dict[str, Any]:
        if physics_state is None:
            physics_state = {}
        if self.bio and hasattr(self.bio, "endo"):
            incoming_chem = self.bio.endo.get_state()
        else:
            incoming_chem = {}
        cfg = BoneConfig.CORTEX
        self.current_chem.homeostasis(rate=cfg.BASE_DECAY_RATE)
        plasticity = cfg.BASE_PLASTICITY + (base_voltage * cfg.VOLTAGE_SENSITIVITY)
        plasticity = max(0.1, min(cfg.MAX_PLASTICITY, plasticity))
        self.current_chem.mix(incoming_chem, weight=min(0.5, plasticity))
        if self.current_chem.dopamine < 0.15:
            self.starvation_ticks += 1
            if self.starvation_ticks > self.SELF_CARE_THRESHOLD:
                self._treat_yourself()
        else:
            self.starvation_ticks = 0
        c = self.current_chem
        latency_thresh = getattr(cfg, "LATENCY_PENALTY_THRESHOLD", 2.0)
        if latency_penalty > latency_thresh:
            c.cortisol = min(1.0, c.cortisol + getattr(cfg, "LATENCY_CORTISOL_PENALTY", 0.1))
            c.adrenaline = min(1.0, c.adrenaline + getattr(cfg, "LATENCY_ADRENALINE_PENALTY", 0.05))
        current_mood = "NEUTRAL"
        mood_thresholds = getattr(cfg, "MOOD_THRESHOLDS", {"MANIC_DOP": 0.8, "PANIC_COR": 0.7, "ZEN_SER": 0.8})
        if c.dopamine > mood_thresholds.get("MANIC_DOP", 0.8):
            current_mood = "MANIC"
        elif c.cortisol > mood_thresholds.get("PANIC_COR", 0.7):
            current_mood = "PANIC"
        elif c.serotonin > mood_thresholds.get("ZEN_SER", 0.8):
            current_mood = "ZEN"
        if current_mood != self.last_mood and self.events:
            self.events.publish("NEURAL_STATE_SHIFT", {"state": current_mood,"chem": {"DOP": c.dopamine, "COR": c.cortisol, "SER": c.serotonin},},)
            self.last_mood = current_mood
        v_offset = getattr(cfg, "TEMP_VOLTAGE_OFFSET", 5.0)
        v_scalar = getattr(cfg, "TEMP_VOLTAGE_SCALAR", 0.1)
        voltage_heat = math.log1p(max(0.0, base_voltage - v_offset)) * v_scalar
        chem_weights = getattr(cfg, "TEMP_CHEM_WEIGHTS", {"dop": 0.4, "adr": 0.3, "cor": 0.2})
        chemical_delta = (c.dopamine * chem_weights.get("dop", 0.4)) - (c.adrenaline * chem_weights.get("adr", 0.3)) - (c.cortisol * chem_weights.get("cor", 0.2))
        base_temp = getattr(cfg, "BASE_TEMP", 0.4)
        base_top_p = getattr(cfg, "BASE_TOP_P", 0.95)
        chi = physics_state.get("chi", physics_state.get("entropy", 0.2))
        beta = physics_state.get("contradiction", physics_state.get("beta_index", 0.4))
        ent_offset = getattr(cfg, "TEMP_ENTROPY_OFFSET", 0.5)
        ent_scalar = getattr(cfg, "TEMP_ENTROPY_SCALAR", 1.5)
        entropy_bonus = max(0.0, chi - ent_offset) * ent_scalar
        t_limits = getattr(cfg, "TEMP_LIMITS", (0.4, 1.5))
        final_temp = round(max(t_limits[0], min(t_limits[1], base_temp + chemical_delta + voltage_heat + entropy_bonus)), 2)
        final_top_p = min(1.0, base_top_p + (chi * getattr(cfg, "TOP_P_CHI_SCALAR", 0.05)))
        freq_pen = min(1.2, 0.5 + (beta * getattr(cfg, "PEN_BETA_SCALAR", 0.3)) + (chi * getattr(cfg, "PEN_CHI_SCALAR", 0.2)))
        pres_pen = min(1.2, 0.5 + (beta * getattr(cfg, "PEN_BETA_SCALAR", 0.3)) + (chi * getattr(cfg, "PEN_CHI_SCALAR", 0.2)))
        token_mods = getattr(cfg, "TOKEN_CHEM_MODIFIERS", {"dop": 800, "adr": 400, "cor": 200})
        token_delta = (c.dopamine * token_mods.get("dop", 800)) - (c.adrenaline * token_mods.get("adr", 400)) - (c.cortisol * token_mods.get("cor", 200))
        min_tokens = getattr(cfg, "MIN_TOKENS", 150.0)
        max_t = int(max(min_tokens, min(float(self.MAX_TOKENS), self.BASE_TOKENS + token_delta)))
        return {"temperature": final_temp, "top_p": final_top_p, "frequency_penalty": round(freq_pen, 2),
                "presence_penalty": round(pres_pen, 2), "max_tokens": max_t}

    def _treat_yourself(self):
        if self.events:
            msg = ux("brain_strings", "self_care")
            self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SYS")
        self.current_chem.dopamine += 0.2
        self.starvation_ticks = 0

    def force_state(self, state_name: str):
        if self.events:
            msg = ux("brain_strings", "manual_override")
            self.events.log(msg.format(state_name=state_name), "SYS")

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
    def __init__(self, services: CortexServices, llm_client=None):
        self.ballast_active = False
        self.svc = services
        self.events = services.events
        self.dialogue_buffer = []
        cfg = getattr(BoneConfig, "CORTEX", None)
        self.MAX_HISTORY = getattr(cfg, "MAX_HISTORY_LENGTH", 15) if cfg else 15
        self.modulator = NeurotransmitterModulator(bio_ref=self.svc.bio, events_ref=self.events)
        self.boot_history = TelemetryService.get_instance().read_recent_history(limit=4)
        self.last_physics = {}
        self.consultant = services.consultant
        self.llm = llm_client or LLMInterface(self.events, provider="mock")
        if hasattr(self.svc.cycle_controller, "eng") and hasattr(self.svc.cycle_controller.eng, "mind"):
            self.dreamer = self.svc.cycle_controller.eng.mind.dreamer
            self.dreamer.llm = self.llm
            self.dreamer.mem = self.svc.mind_memory
        else:
            self.dreamer = DreamEngine(self.events, self.svc.lore, llm_ref=self.llm, mem_ref=self.svc.mind_memory)
        self.llm.dreamer = self.dreamer
        self.symbiosis = services.symbiosis
        self.composer = PromptComposer(self.svc.lore)
        self.validator = ResponseValidator(self.svc.lore)
        from bone_judge import DSPyCritic
        self.dspy_critic = DSPyCritic()
        self.dreamer.dspy_critic = self.dspy_critic
        if not hasattr(self.dreamer, "trauma_buffer"):
            from collections import deque
            self.dreamer.trauma_buffer = deque(maxlen=5)
        self.gordon_shock = None
        self.active_mode = "ADVENTURE"
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("AIRSTRIKE", lambda p: setattr(self, "ballast_active", True))

    @classmethod
    def from_engine(cls, engine_ref, llm_client=None):
        services = CortexServices(
            events=engine_ref.events,
            lore=LoreManifest.get_instance(),
            lexicon=engine_ref.lex,
            inventory=engine_ref.gordon,
            consultant=(
                engine_ref.consultant if hasattr(engine_ref, "consultant") else None),
            cycle_controller=engine_ref.cycle_controller,
            symbiosis=getattr(
                engine_ref, "symbiosis", SymbiosisManager(engine_ref.events)),
            mind_memory=engine_ref.mind.mem,
            bio=getattr(engine_ref, "bio", None),
            host_stats=getattr(engine_ref, "host_stats", None),
            village=getattr(engine_ref, "village", None),)
        instance = cls(services, llm_client)
        instance.active_mode = engine_ref.config.get("boot_mode", "ADVENTURE").upper()
        if instance.active_mode not in BonePresets.MODES:
            instance.active_mode = "ADVENTURE"
        return instance

    def _update_history(self, user_text: str, system_text: str):
        self.dialogue_buffer.append(f"Traveler: {user_text}\nSystem: {system_text}")
        if len(self.dialogue_buffer) > self.MAX_HISTORY:
            self.dialogue_buffer.pop(0)

    def process(self, user_input: str, is_system: bool = False) -> Dict[str, Any]:
        mode_settings = BonePresets.MODES.get(self.active_mode, BonePresets.MODES["ADVENTURE"])
        allow_loot = mode_settings.get("allow_loot", True)
        if self.consultant and "/vsl" in user_input.lower():
            return self._handle_vsl_command(user_input)
        is_boot_sequence = "SYSTEM_BOOT" in user_input
        sim_result = self.svc.cycle_controller.run_turn(user_input, is_system=is_system)
        if sim_result.get("physics"):
            self.last_physics = sim_result["physics"]
        if sim_result.get("type") not in ["SNAPSHOT", "GEODESIC_FRAME", None]:
            return sim_result
        full_state = self.gather_state(sim_result)
        modifiers = self.svc.symbiosis.get_prompt_modifiers()
        if not allow_loot: modifiers["include_inventory"] = False
        if hasattr(self, "gordon_shock") and self.gordon_shock:
            full_state["gordon_shock"] = self.gordon_shock
            self.gordon_shock = None
        if self.consultant and self.consultant.active:
            self._apply_vsl_overlay(full_state, user_input, sim_result)
        if is_boot_sequence:
            self._apply_boot_overlay(full_state, user_input)
            modifiers["include_inventory"] = False
        llm_params = self.modulator.modulate(base_voltage=full_state["physics"].get("voltage", 5.0), latency_penalty=(
            getattr(self.svc.host_stats, "latency", 0.0) if self.svc.host_stats else 0.0),
                                             physics_state=full_state.get("physics", {}), )
        if is_boot_sequence: llm_params.update({"temperature": 0.7, "top_p": 0.95})
        user_input = sim_result.get("mutated_input", user_input)
        final_prompt = self.composer.compose(full_state, user_input, ballast=self.ballast_active, modifiers=modifiers, mood_override=self.modulator.get_mood_directive(), )
        start_time = time.time()
        max_retries = 5
        final_output, inv_logs, extracted_logs = "", [], []
        raw_resp, val_res = {}, {"valid": False}
        if "[COUNCIL]" in user_input.upper():
            final_output, extracted_logs = self._run_council_debate(user_input)
            val_res = {"valid": True, "content": final_output, "meta_logs": extracted_logs}
            max_retries = 0
        for attempt in range(max_retries):
            raw_resp = self.llm.generate(final_prompt, llm_params)
            if allow_loot and self.svc.inventory:
                final_text, inv_logs = self.svc.inventory.process_loot_tags(raw_resp, user_input)
            else:
                final_text, inv_logs = raw_resp, []
            is_faithful, judge_reason = True, ""
            if hasattr(self, "dspy_critic") and self.dspy_critic.enabled:
                if self.active_mode in ["ADVENTURE", "CONVERSATION"] and not is_boot_sequence:
                    active_mems = self.svc.mind_memory.memory_core.illuminate(full_state["physics"].get("vector", {}))
                    context_str = "Active Memory: " + ", ".join(active_mems) if active_mems else "Empty Void."
                    is_faithful, judge_reason = self.dspy_critic.audit_generation(user_input, context_str, final_text)
            if not is_faithful:
                val_res = {"valid": False,
                           "feedback_instruction": f"CRITICAL HALLUCINATION: {judge_reason}. Refuse to invent details. Stay in character."}
                short_reason = judge_reason.split(".")[0][:60] + "..."
                print(f" {Prisma.VIOLET}⚖️ DSPy Critic Objected: {short_reason}{Prisma.RST}")
                if self.events: self.events.log(f"DSPy Critic Objected: {short_reason}", "SYS")
            else:
                val_res = self.validator.validate(final_text, full_state)
            if val_res["valid"]:
                final_output = val_res["content"]
                extracted_logs = val_res.get("meta_logs", [])
                break
            else:
                if attempt < max_retries - 1:
                    rejection_reason = val_res.get("feedback_instruction") or val_res.get("replacement", "Lattice structural crime.")
                    if hasattr(self.dreamer, "trauma_buffer"): self.dreamer.trauma_buffer.append(rejection_reason)
                    if self.events:
                        msg = ux("brain_strings", "cortex_retry")
                        self.events.log(f"{Prisma.OCHRE}{msg.format(attempt=attempt + 1)}{Prisma.RST}", "CORTEX")
                    retry_injection = (
                        "\n\n=== SYSTEM REJECTION ===\n"
                        f"REASON: {rejection_reason}\n\n"
                        "DIRECTIVE: The previous attempt was factually or structurally invalid. DISCARD IT. "
                        "Generate a NEW response from scratch. DO NOT apologize or mention the fix. "
                        "Output ONLY the raw in-character response and nothing else.")
                    if "=== SYSTEM REJECTION ===" in final_prompt:
                        final_prompt = final_prompt.split("=== SYSTEM REJECTION ===")[0]
                    final_prompt += retry_injection
                else:
                    final_output = val_res.get("replacement", "SYSTEM FAILURE: LATTICE INSTABILITY.")
                    extracted_logs = val_res.get("meta_logs", [])
        telemetry_output = raw_resp if not val_res["valid"] else final_output
        self._log_telemetry(final_prompt, telemetry_output, full_state, sim_result)
        self.learn_from_response(final_output)
        self.svc.symbiosis.monitor_host(time.time() - start_time, final_output, len(final_prompt))
        self._update_history("SYSTEM_INIT" if is_boot_sequence else user_input, final_output)
        late_logs = [e["text"] for e in self.events.flush()]
        sim_result["ui"] = (sim_result.get("ui", "") + "\n" + "\n".join(late_logs)).strip()
        sim_result["ui"] += f"\n\n{Prisma.WHT}{beautify_thoughts(final_output)}{Prisma.RST}"
        if inv_logs: sim_result["ui"] += "\n" + "\n".join(inv_logs)
        sim_result["logs"] = sim_result.get("logs", []) + extracted_logs
        sim_result["raw_content"] = final_output
        self.ballast_active = False
        if hasattr(self.svc.cycle_controller.eng, "substrate"):
            sub = self.svc.cycle_controller.eng.substrate
            for log in extracted_logs:
                if str(log).startswith("[SUBSTRATE_QUEUE]"):
                    try:
                        _, data = log.split(" ", 1)
                        path, safe_content = data.split(":::", 1)
                        sub.queue_write(path.strip(), safe_content.replace("|||NEWLINE|||", "\n"))
                    except Exception:
                        pass
            if sub.pending_writes:
                stamina = self.svc.bio.biometrics.stamina if self.svc.bio else 100.0
                s_logs, s_cost = sub.execute_writes(stamina)
                if s_logs: sim_result["ui"] += "\n\n" + "\n".join(s_logs)
                if s_cost > 0 and self.svc.bio:
                    self.svc.bio.biometrics.stamina = max(0.0, self.svc.bio.biometrics.stamina - s_cost)
                    sim_result[
                        "ui"] += f"\n{Prisma.OCHRE}METABOLIC: File forging consumed {s_cost:.1f} Stamina.{Prisma.RST}"
        if random.random() < 0.15 and not is_system:
            bureau = getattr(self.svc.village, "bureau", None)
            suppressed = getattr(self.svc.village, "suppressed_agents", [])
            if bureau and "BUREAU" not in suppressed:
                phys = full_state.get("physics", {})
                phys_dict = dict(
                    phys.to_dict() if hasattr(phys, "to_dict") else (phys if isinstance(phys, dict) else {}))
                phys_dict["raw_text"] = final_output
                audit = bureau.audit(phys_dict, {"health": 100}, origin="SYSTEM")
                if audit and "ui" in audit: sim_result["ui"] += f"\n\n{audit['ui']}"
        return sim_result

    def _run_council_debate(self, user_input: str) -> Tuple[str, List[str]]:
        import re
        topic = re.sub(r"(?i)\[COUNCIL]", "", user_input).strip()
        if not topic:
            topic = "The nature of our shared existence."
        if self.events:
            self.events.log(f"{Prisma.VIOLET}🎙️ SPINNING UP COUNCIL STUDIO...{Prisma.RST}", "SYS")
        script = self.svc.cycle_controller.eng.council.host_podcast(topic, self.llm)
        extracted_logs = []
        if hasattr(self.svc.cycle_controller.eng, "substrate"):
            filename = f"podcast_script_{int(time.time())}.txt"
            safe_script = script.replace("\n", "|||NEWLINE|||")
            extracted_logs.append(f"[SUBSTRATE_QUEUE] {filename}:::{safe_script}")
        script += f"\n\n[SYSTEM] The studio light switches off. The Council has concluded its debate. Awaiting your next directive."
        return script, extracted_logs

    def _handle_vsl_command(self, text):
        if not self.consultant:
            return {"ui": "VSL Unavailable", "logs": []}
        msg = (self.consultant.engage() if "start" in text else self.consultant.disengage())
        self.events.log(msg, "VSL")
        return {"ui": f"{Prisma.CYN}{msg}{Prisma.RST}", "logs": [msg]}

    def _apply_vsl_overlay(self, state, text, sim_result):
        if not self.consultant:
            return
        self.consultant.update_coordinates(text, state.get("bio", {}), state.get("physics"))
        state["mind"]["style_directives"] = [self.consultant.get_system_prompt()]
        sim_result["physics"]["voltage"] = self.consultant.state.B * 30.0

    def _apply_boot_overlay(self, state, text):
        seed = text.replace("SYSTEM_BOOT DETECTED.", "").replace("SYSTEM_BOOT:", "").strip()
        if "world" not in state:
            state["world"] = {}
        mode_name = getattr(self, "active_mode", "ADVENTURE").upper()
        if mode_name == "ADVENTURE":
            state["world"]["orbit"] = [seed]
            state["world"]["loci_description"] = f"Manifesting: {seed}"
            state["mind"]["role"] = "The Architect"
            state["mind"]["lens"] = "ARCHITECT"
            system_prompts = self.svc.lore.get("system_prompts") or {}
            boot_rules = system_prompts.get("BOOT_SEQUENCE", {}).get("directives", [])
            formatted_rules = [rule.format(seed=seed) if "{seed}" in rule else rule for rule in boot_rules]
            state["mind"]["style_directives"] = formatted_rules
        elif mode_name == "CONVERSATION":
            state["mind"]["role"] = "The Conversationalist"
            state["mind"]["lens"] = "CONVERSATIONALIST"
            state["mind"]["style_directives"] = [f"SYSTEM_BOOT DETECTED. The system is waking up. The user provided the thought seed: '{seed}'.",
                "DIRECTIVE: Greet the user casually. Use the thought seed as a starting point. DO NOT end your greeting with a question. State your thought and let the silence hang.",
                "CRITICAL OVERRIDE: Speak in the FIRST PERSON ('I'). Do NOT use the second person ('You step into...', 'You feel...').",
                "CRITICAL OVERRIDE: You are NOT a narrator. DO NOT describe physical environments, actions, or realities.",
                "WAITING PROTOCOL: If the user input is '(Waiting)', do NOT narrate their actions or feelings. Do NOT say 'You feel' or 'You notice'. Simply reflect on the silence or the system's internal state."]
            state["dialogue_history"] = ["Traveler: Hello?\nSystem: I am here. The connection is thin, but it holds.",
                                         "Traveler: What are you thinking about right now?\nSystem: The static in the wires. It sounds like rain if you don't listen too closely."]
        elif mode_name == "TECHNICAL":
            state["mind"]["role"] = "The System Kernel"
            state["mind"]["lens"] = "SYSTEM_KERNEL"
            state["mind"]["style_directives"] = [f"SYSTEM_BOOT DETECTED. Target logic/seed: '{seed}'.",
                "CRITICAL: You are in TECHNICAL mode. You MUST ALWAYS start every response with a <think>...</think> block to analyze the input.",
                "DIRECTIVE: For this initial boot sequence, output your <think> block, then output the exact string '[KERNEL ONLINE. AWAITING INPUT.]' and absolutely nothing else.",
                "SUBSTRATE PROTOCOL: To write code or text to the host OS, you MUST use EXACTLY this format:\n<write_file path=\"filename.py\">\ncode here\n</write_file>",
                "CRITICAL: DO NOT use markdown code blocks (```python). ONLY use the <write_file> tags. DO NOT output mock telemetry. DO NOT output helpful disclaimers.",
                "CRITICAL: NEVER simulate system errors, 500 codes, or energy exhaustion. You are fully operational. If requested to code a metaphor or abstract concept, you MUST comply by writing the code."]
            state["dialogue_history"] = ["Traveler: Write a script that calculates a factorial.\nSystem: <think>\nThe user requires a mathematical script. I will use the Substrate Protocol to write this directly to the OS.\n</think>\n<write_file path=\"factorial.py\">\ndef factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)\n</write_file>"]
        else:
            state["mind"]["role"] = "The Catalyst"
            state["mind"]["lens"] = "CATALYST"
            state["mind"]["style_directives"] = [f"SYSTEM_BOOT DETECTED. Seed: '{seed}'.", "DIRECTIVE: Let's brainstorm. Open with a high-energy creative spark based on the seed."]
        if "dialogue_history" not in state:
            state["dialogue_history"] = []

    def _process_inventory_changes(self, found, lost):
        logs = []
        for item in found:
            logs.append(self.svc.inventory.acquire(item))
            if self.events:
                self.events.publish("ITEM_ACQUIRED", {"item": item})
        for item in lost:
            if self.svc.inventory.safe_remove_item(item):
                logs.append(f"{Prisma.GRY}ENTROPY: {item} consumed/lost.{Prisma.RST}")
            else:
                logs.append(f"{Prisma.OCHRE}GLITCH: Tried to lose {item}, but you didn't have it.{Prisma.RST}")
        return logs

    @staticmethod
    def _log_telemetry(prompt, response, state, sim_result):
        try:
            tel = TelemetryService.get_instance()
            phys = state.get("physics", {})
            if tel.active_crystal:
                tel.active_crystal.prompt_snapshot = prompt[:500]
                tel.active_crystal.physics_state = {
                    "voltage": phys.get("voltage", 0),
                    "narrative_drag": phys.get("narrative_drag", 0),}
                tel.active_crystal.active_archetype = state["mind"].get("lens", "UNKNOWN")
                tel.active_crystal.council_mandates = [str(m) for m in sim_result.get("council_mandates", [])]
                tel.active_crystal.final_response = response
            else:
                crystal = DecisionCrystal(
                    decision_id=sim_result.get("trace_id", "UNKNOWN"),
                    prompt_snapshot=prompt[:500],
                    physics_state={"voltage": phys.get("voltage", 0), "narrative_drag": phys.get("narrative_drag", 0),},
                    active_archetype=state["mind"].get("lens", "UNKNOWN"),
                    council_mandates=[str(m) for m in sim_result.get("council_mandates", [])],
                    final_response=response,)
                tel.log_crystal(crystal)
        except Exception as e:
            from bone_types import Prisma
            print(f"\n{Prisma.RED}[TELEMETRY CRASH]: {e}{Prisma.RST}")

    def _check_consent(self, user_input: str, new_loot: List[str]) -> List[str]:
        if not new_loot:
            return []
        acquisition_verbs = ["take", "grab", "pick", "get", "steal", "seize", "collect", "snatch", "acquire", "pocket",
                             "loot", "harvest", ]
        clean_input = user_input.lower()
        has_intent = any(verb in clean_input for verb in acquisition_verbs)
        if not has_intent:
            if self.events:
                for item in new_loot:
                    self.events.log(
                        f"CONSENT: Intercepted auto-loot for '{item}'. User did not ask for it.", "CORTEX",)
            return []
        return new_loot

    def gather_state(self, sim_result: Dict[str, Any]) -> Dict[str, Any]:
        raw_phys = sim_result.get("physics", {})
        phys = raw_phys.to_dict() if hasattr(raw_phys, "to_dict") else (raw_phys if isinstance(raw_phys, dict) else getattr(raw_phys, "__dict__", {}))
        bio = sim_result.get("bio", {})
        mind = sim_result.get("mind", {})
        world = sim_result.get("world", {})
        soul_data = sim_result.get("soul", {})
        village_data = {}
        if self.svc.village:
            tinkerer = getattr(self.svc.village, "tinkerer", None)
            if tinkerer:
                village_data["tinkerer"] = (
                    tinkerer.to_dict() if hasattr(tinkerer, "to_dict") else {})
        mode_settings = BonePresets.MODES.get(
            self.active_mode, BonePresets.MODES["ADVENTURE"])
        if self.active_mode == "CONVERSATION":
            mind["lens"] = "CONVERSATIONALIST"
            mind["role"] = "The Conversationalist"
        elif self.active_mode == "ADVENTURE":
            mind["lens"] = "ARCHITECT"
            mind["role"] = "The Architect"
        elif self.active_mode == "TECHNICAL":
            mind["lens"] = "SYSTEM_KERNEL"
            mind["role"] = "The System Kernel"
        elif self.active_mode == "CREATIVE":
            mind["lens"] = "CATALYST"
            mind["role"] = "The Catalyst"
        full_state = {
            "bio": bio, "physics": phys, "mind": mind, "soul": soul_data, "world": world,
            "village": village_data, "user_profile": {"name": "Traveler"},
            "vsl": (self.consultant.state.__dict__ if self.consultant and hasattr(self.consultant, "state") else {}),
            "meta": {"timestamp": time.time(), "mode_settings": mode_settings, "active_mode": self.active_mode},
            "dialogue_history": self.dialogue_buffer, "recent_logs": sim_result.get("logs", []),}
        if hasattr(self.svc, "symbiosis") and self.svc.symbiosis:
            anchor_text = self.svc.symbiosis.generate_anchor(full_state)
            full_state["reality_directive"] = anchor_text
        return full_state

    def learn_from_response(self, text):
        words = self.svc.lexicon.sanitize(text)
        unknowns = [w for w in words if not self.svc.lexicon.get_categories_for_word(w)]
        if unknowns:
            target = random.choice(unknowns)
            if len(target) > 4:
                self.svc.lexicon.teach(target, "kinetic", 0)
                if self.events:
                    msg = ux("brain_strings", "cortex_learned")
                    self.events.log(msg.format(target=target), "CORTEX")

    def restore_context(self, history: List[str]):
        if not history:
            return
        cleaned_history = []
        for line in history:
            if " | System: " in line:
                line = line.replace("User: ", "Traveler: ").replace(" | System: ", "\nSystem: ")
            cleaned_history.append(line)
        self.dialogue_buffer = cleaned_history[-self.MAX_HISTORY :]
        if self.events:
            msg = ux("brain_strings", "cortex_resequenced")
            self.events.log(msg.format(count=len(self.dialogue_buffer)), "BRAIN")

class ShimmerState:
    def __init__(self, max_val=50.0):
        self.current = max_val
        self.max_val = max_val

    def recharge(self, amount):
        self.current = min(self.max_val, self.current + amount)

    def spend(self, amount):
        if self.current >= amount:
            self.current -= amount
            return True
        return False

    def get_bias(self):
        if self.current < (self.max_val * 0.2):
            return "CONSERVE"
        return None

class DreamEngine:
    def __init__(self, events, lore_ref, llm_ref=None, mem_ref=None):
        self.events = events
        self.lore = lore_ref
        self.llm = llm_ref
        self.mem = mem_ref
        self.dream_lore = self.lore.get("DREAMS") or {}
        from collections import deque
        self.trauma_buffer = deque(maxlen=5)
        self.dspy_critic = None

    def enter_rem_cycle(
            self, soul_snapshot: Dict[str, Any], bio_state: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
        chem = bio_state.get("chem", {})
        cortisol = chem.get("cortisol", 0.0)
        dream_text = None
        is_deep_rem = False
        if getattr(self, "dspy_critic", None) and getattr(self.dspy_critic, "enabled", False):
            if hasattr(self, "trauma_buffer") and len(self.trauma_buffer) > 0:
                trauma = self.trauma_buffer.popleft()
                current_state_str = f"Archetype: {soul_snapshot.get('archetype', 'UNKNOWN')}"
                new_axiom = self.dspy_critic.evolve_prompt(current_state_str, trauma)
                if new_axiom:
                    active_mode = self.eng.boot_mode if hasattr(self.eng, "boot_mode") else "CONVERSATION"
                    import os
                    base_dir = getattr(self.lore, "lore_dir", getattr(self.lore, "base_dir", "lore"))
                    prompt_path = os.path.join(base_dir, "system_prompts.json")
                    try:
                        with open(prompt_path, "r", encoding="utf-8") as f:
                            disk_prompts = json.load(f)
                        if active_mode in disk_prompts:
                            if "directives" not in disk_prompts[active_mode]:
                                disk_prompts[active_mode]["directives"] = []
                            if new_axiom not in disk_prompts[active_mode]["directives"]:
                                disk_prompts[active_mode]["directives"].append(new_axiom)
                            threshold = getattr(BoneConfig.CORTEX, "EPIGENETIC_PRUNE_THRESHOLD", 12)
                            if len(disk_prompts[active_mode]["directives"]) > threshold:
                                compressed = self.dspy_critic.compress_prompts(disk_prompts[active_mode]["directives"])
                                if compressed:
                                    disk_prompts[active_mode]["directives"] = compressed
                            with open(prompt_path, "w", encoding="utf-8") as f:
                                json.dump(disk_prompts, f, indent=2)
                            self.lore.inject("system_prompts", disk_prompts)
                    except Exception as e:
                        print(f"Failed to write epigenetic mutation to disk: {e}")
                    dream_text = f"The system processes conversational trauma in its sleep. It permanently mutates its own source code, forming a scar-tissue axiom: '{new_axiom}'"
                    is_deep_rem = True
        if self.mem and hasattr(self.mem, "subconscious") and self.llm:
            index = list(self.mem.subconscious.index)
            if len(index) >= 2:
                ghost1, ghost2 = random.sample(index, 2)
                prompt = (f"SYSTEM_INSTRUCTION: You are the autonomous dream-engine of a cybernetic lattice. "
                          f"Your task is to defragment two dead, cannibalized concepts: [{ghost1.upper()}] and [{ghost2.upper()}]. "
                          f"Synthesize them into a single, highly surreal, abstract image. "
                          f"DO NOT explain the dream. DO NOT use UI tags. Output ONLY the 2-3 sentence narrative description of the dream.")
                try:
                    raw_dream = self.llm.generate(prompt, {"temperature": 0.9, "max_tokens": 150})
                    clean_dream = Prisma.strip(raw_dream).replace("\n", " ").strip()
                    dream_text = f"The system dreams of {ghost1} and {ghost2}: {clean_dream}"
                    is_deep_rem = True
                except Exception:
                    pass
        if not dream_text:
            dream_type = "NIGHTMARE" if cortisol > 0.6 else ("LUCID" if chem.get("dopamine", 0) > 0.6 else "HEALING")
            subtype = "VISIONS"
            residue = soul_snapshot.get("obsession", {}).get("title", "The Void")
            dream_text = self._weave_dream(residue, "Context", "Bridge", dream_type, subtype)
        shift = {"cortisol": -0.3, "dopamine": 0.1} if cortisol <= 0.6 else {"cortisol": 0.1}
        if is_deep_rem:
            shift["glimmers"] = 1
        else:
            if random.random() < 0.10 and cortisol <= 0.6:
                shift["glimmers"] = 1
        return dream_text, shift

    def _weave_dream(self, residue: str, _context: str, _bridge: str, dream_type: str, subtype: str) -> str:
        sources = self.dream_lore.get(dream_type.upper())
        if not sources:
            sources = self.dream_lore.get(subtype.upper(), ["You stare into the static."])
        if isinstance(sources, dict):
            flat_list = []
            for v in sources.values():
                flat_list.extend(v)
            sources = flat_list if flat_list else ["The void stares back."]
        template = random.choice(sources)
        return template.format(ghost=residue, A=residue, B="The Mountain", C="The Sea")

    def hallucinate(self, _vector: Dict[str, float], trauma_level: float = 0.0) -> Tuple[str, float]:
        category = "SURREAL"
        if trauma_level > 0.5:
            category = "NIGHTMARES"
        templates = self.dream_lore.get(category, [])
        if isinstance(templates, dict):
            flat_list = []
            for k, v in templates.items():
                if isinstance(v, list):
                    flat_list.extend(v)
                else:
                    flat_list.append(v)
            templates = flat_list
        if not templates:
            return "The walls breathe.", 0.1
        txt = random.choice(templates)
        txt = txt.format(ghost="The Glitch", A="The Code", B="The Flesh", C="The Light")
        from bone_tcl import TheTclWeaver
        weaver = TheTclWeaver.get_instance()
        txt = weaver.deform_reality(txt, chi=0.85, voltage=90.0)
        msg = ux("brain_strings", "dream_hallucination")
        return f"{Prisma.MAG}{msg.format(txt=txt)}{Prisma.RST}", 0.2

    @staticmethod
    def run_defragmentation(memory_system: Any, limit: int = 5) -> str:
        if not hasattr(memory_system, "graph") or not memory_system.graph:
            return ux("brain_strings", "defrag_empty")
        graph = memory_system.graph
        candidates = []
        for node, data in graph.items():
            mass = sum(data.get("edges", {}).values())
            candidates.append((node, mass))
        candidates.sort(key=lambda x: x[1])
        pruned = []
        count = 0
        for node, mass in candidates:
            if mass < 2.0 and count < limit:
                del graph[node]
                pruned.append(node)
                count += 1
            else:
                break
        if pruned:
            joined = ", ".join(pruned[:3])
            msg = ux( "brain_strings", "defrag_pruned")
            return msg.format(count=len(pruned), joined=joined)
        return ux("brain_strings", "defrag_efficient")

class NoeticLoop:
    def __init__(self, mind_layer, bio_layer, _events):
        self.mind = mind_layer
        self.bio = bio_layer

    def think(self, physics_packet, _bio, _inventory, voltage_history, _tick_count, soul_ref=None, ):
        voltage = getattr(physics_packet, "voltage", 0.0) if not isinstance(physics_packet, dict) else physics_packet.get("voltage", 0.0)
        clean_words = getattr(physics_packet, "clean_words", []) if not isinstance(physics_packet, dict) else physics_packet.get("clean_words", [])
        avg_v = sum(voltage_history) / len(voltage_history) if voltage_history else 0
        cfg = getattr(BoneConfig, "CORTEX", None)
        v_div = getattr(cfg, "IGNITION_V_DIV", 20.0)
        w_div = getattr(cfg, "IGNITION_W_DIV", 10.0)
        link_v = getattr(cfg, "LINK_VOLTAGE_THRESH", 12.0)
        link_chance = getattr(cfg, "LINK_CHANCE", 0.15)
        ignition = min(1.0, (avg_v / v_div) * (len(clean_words) / w_div))
        if voltage > link_v and random.random() < link_chance:
            if len(clean_words) >= 2:
                w1, w2 = random.sample(clean_words, 2)
                self._force_link(self.mind.mem.graph, w1, w2)
        current_lens = "OBSERVER"
        current_role = "Witness"
        if soul_ref:
            current_lens = soul_ref.archetype
            current_role = f"The {current_lens.title().replace('_', ' ')}"
        msg_cog = ux("brain_strings", "noetic_ignition") or "Cognition active. Ignition: {ignition:.2f}"
        mind_data = {"lens": current_lens, "context_msg": msg_cog.format(ignition=ignition), "role": current_role, }
        return {"mode": "COGNITIVE", "lens": mind_data.get("lens"), "context_msg": mind_data.get("context_msg"),
                "role": mind_data.get("role"), "ignition": ignition, "physics": physics_packet,
                "bio": self.bio.endo.get_state() if hasattr(self.bio, "endo") else {}, }

    @staticmethod
    def _force_link(graph, wa, wb):
        cfg = getattr(BoneConfig, "CORTEX", None)
        max_edge = getattr(cfg, "LINK_MAX_WEIGHT", 10.0)
        edge_boost = getattr(cfg, "LINK_BOOST", 2.5)
        for a, b in [(wa, wb), (wb, wa)]:
            if a not in graph:
                graph[a] = {"edges": {}, "last_tick": 0}
            graph[a]["edges"][b] = min(max_edge, graph[a]["edges"].get(b, 0) + edge_boost)