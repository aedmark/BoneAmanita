"""cortex.py
The Global Workspace and LLM Interface.
This module takes the biological parameters from `mind.py`, compiles the
context window, enforces the Lexical Firewall, and executes the actual API
calls to the underlying neural network.
"""
import random
import re
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from archetypes.symbiosis import SymbiosisManager
from brain.composer import LLMInterface, PromptComposer, ResponseValidator
from brain.mind import NeurotransmitterModulator, DreamEngine
from constants import Prisma
from core import EventBus, TelemetryService, LoreManifest, DecisionCrystal
from mechanics.projector import beautify_thoughts
from mechanics.tools import RandomRetrievalNavigator, LibraryGraph
from mechanics.pragmatics import ThePragmatist
from presets import BoneConfig, BonePresets
from struts import safe_get, safe_set, ux


@dataclass
class CortexServices:
    """A struct to pass the physical, biological, and memory layers into the Global Workspace."""
    events: EventBus
    lore: Any
    lexicon: Any
    inventory: Any
    consultant: Any
    orchestrator: Any
    symbiosis: Any
    mind_memory: Any
    bio: Any
    host_stats: Any = None
    village: Any = None
    config_ref: Any = None


class TheCortex:
    """
    The Global Workspace.
    Handles the primary generation loop, DSPy Affective auditing, Lexical firewalls,
    and context compilation.
    """
    LEXICAL_PURGE_PATTERN = re.compile(
        r"(?im)^\s*(that makes sense|i understand|you bring up|great point|good point|certainly|absolutely|i hear you|yes, )[.,!]*\s*")
    ROLE_MAP = {"CONVERSATION": ("CONVERSATIONALIST", "The Conversationalist"),
                "TECHNICAL": ("SYSTEM_KERNEL", "The System Kernel"),
                "CREATIVE": ("CATALYST", "The Catalyst"), }

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
        self.last_shadow_nodes = []
        self.consultant = services.consultant
        self.llm = llm_client or LLMInterface(self.events, provider="mock")
        eng_ref = getattr(self.svc.orchestrator, "eng", None)
        self.dreamer = getattr(getattr(eng_ref, "mind", None), "dreamer", None)
        if self.dreamer:
            self.dreamer.llm = self.llm
            self.dreamer.mem = self.svc.mind_memory
        else:
            self.dreamer = DreamEngine(self.events, self.svc.lore, llm_ref=self.llm, mem_ref=self.svc.mind_memory,
                                       eng_ref=eng_ref, config_ref=self.cfg)
        self.llm.dreamer = self.dreamer
        self.symbiosis = services.symbiosis
        self.composer = PromptComposer(self.svc.lore, config_ref=self.cfg)
        self.validator = ResponseValidator(self.svc.lore, config_ref=self.cfg)
        self.pragmatist = ThePragmatist(events_ref=self.events)
        from mechanics.tools import DSPyCritic
        self.dspy_critic = DSPyCritic(config_ref=self.cfg)
        if getattr(self.cfg, "WEIGHT_CLASS", "HEAVYWEIGHT") == "LIGHTWEIGHT":
            self.dspy_critic.enabled = False
            if self.events:
                self.events.log(
                    f"{Prisma.OCHRE}Lightweight Physics Active: DSPyCritic disabled to prevent recursive loops.{Prisma.RST}",
                    "SYS", )
        self.dreamer.dspy_critic = self.dspy_critic
        if not hasattr(self.dreamer, "trauma_buffer"):
            self.dreamer.trauma_buffer = deque(maxlen=5)
        self.active_mode = "ADVENTURE"
        if hasattr(self.svc.mind_memory, "nodes"):
            graph = LibraryGraph(nodes=self.svc.mind_memory.nodes, root=self.svc.mind_memory.root)
            self.navigator = RandomRetrievalNavigator(library_graph=graph)
        else:
            self.navigator = None

    @classmethod
    def from_engine(cls, engine_ref, llm_client=None):
        target_cfg = getattr(engine_ref, "config", BoneConfig)
        symbiosis_mgr = getattr(engine_ref, "symbiosis", None) or SymbiosisManager(engine_ref.events)
        village_ref = getattr(engine_ref, "village", None)
        services = CortexServices(events=engine_ref.events, lore=LoreManifest.get_instance(config_ref=target_cfg),
                                  lexicon=engine_ref.lex, inventory=getattr(village_ref, "gordon", None),
                                  consultant=getattr(engine_ref, "consultant", None),
                                  orchestrator=engine_ref.orchestrator, symbiosis=symbiosis_mgr,
                                  mind_memory=engine_ref.mind.mem,
                                  bio=getattr(engine_ref, "bio", None),
                                  host_stats=getattr(engine_ref, "host_stats", None),
                                  village=village_ref, config_ref=target_cfg, )
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
        pass

    def purge_context(self):
        """Executes a hard flush of the active context window."""
        self.last_shadow_nodes = []
        self.dialogue_buffer.clear()
        self.last_physics.clear()
        if hasattr(self.dreamer, "trauma_buffer"):
            self.dreamer.trauma_buffer.clear()
        if self.events:
            self.events.log("[APOPTOSIS] Context array purged. Stateless bedrock re-established.", "SYS", )

    def process(self, user_input: str, is_system: bool = False) -> Dict[str, Any]:
        """
        The Master Generation Loop.
        1. Compiles the physical, biological, and memory state.
        2. Evaluates the physics pre-flight (Drag, Toxicity) to block runaway loops.
        3. Composes the prompt and speculative LLM calls.
        4. Audits the response via the DSPy Critic and Lexical Firewall.
        5. Returns mutated state to main.py.
        """
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
        context_limit = getattr(getattr(self.cfg, "CORTEX", object()), "MAX_INPUT_CHARS", 15000)
        if len(user_input) > context_limit and not is_system and not is_boot_sequence:
            safe_content = user_input.replace("\n", "|||NEWLINE|||")
            filename = f"context_drop_{int(time.time())}.txt"
            self.svc.orchestrator.eng.substrate.queue_write(f"memory_queue/{filename}", safe_content)
            s_logs, s_cost = self.svc.orchestrator.eng.substrate.execute_writes(stamina_override=100.0)
            if self.svc.bio:
                self.svc.bio.mito.adjust_atp(-s_cost, "Massive Context Ingestion")
            msg = f"{Prisma.CYN}[Substrate Queue]: Massive context drop detected. Routed to silent indexing. Dialogue buffer bypassed. (-{s_cost:.1f} ATP){Prisma.RST}"
            self.events.log(msg, "SYS")
            return {"ui": msg, "type": "SILENT_INGEST", "physics": self.last_physics, "logs": [msg]}
        sim_result = self.svc.orchestrator.run_turn(user_input, is_system=is_system)
        if sim_result.get("physics"):
            self.last_physics = sim_result["physics"]
        if sim_result.get("type") not in ("SNAPSHOT", "GEODESIC_FRAME", None):
            self._update_history(user_input, sim_result.get("ui", "SYSTEM REJECTED PROMPT."))
            return sim_result
        if hasattr(self, "last_shadow_nodes") and self.last_shadow_nodes:
            engaged = [node for node in self.last_shadow_nodes if node.lower() in user_input.lower()]
            for node in engaged:
                if self.events:
                    self.events.publish("SHADOW_ENGAGED", {
                        "source": self.last_physics.get("primary_node", "core") if self.last_physics else "core",
                        "target": node,
                        "user_input": user_input
                    })
            self.last_shadow_nodes = []
        full_state = self.gather_state(sim_result)
        phys_state = full_state.get("physics", {})
        f_drag = float(safe_get(phys_state, "narrative_drag", 0.0))
        chi_val = float(safe_get(phys_state, "chi", safe_get(phys_state, "entropy", 0.0)))
        m_a = float(safe_get(phys_state, "m_a", 0.0))
        if f_drag > 1.5 or chi_val > 0.8:
            reject_msg = ux("cortex_strings", "gordon_anchor_lock",
                            default="[GORDON - The Anchor]: Frequency too high. Tensegrity Anchor engaged. I am locking the architecture. Take a breath and lower your narrative friction before we proceed.")
            if self.events:
                self.events.log(f"{Prisma.RED}{reject_msg}{Prisma.RST}", "SYS_LOCK")
            sim_result["ui"] = (sim_result.get("ui", "") + f"\n\n{Prisma.RED}{reject_msg}{Prisma.RST}").strip()
            sim_result["type"] = "SYSTEM_HALT"
            return sim_result
        if f_drag > 1.2 or chi_val > 0.7 or m_a > 0.8:
            simulated_ros = (f_drag * 5.0) + (chi_val * 20.0) + (m_a * 30.0)
            if simulated_ros > 35.0:
                reject_msg = ux("brain_strings", "pinker_cf_gate", default="Structural rot critical.")
                scar_msg = ux("brain_strings", "moog_scar_log", default="Productive Worry activated.")
                if self.events:
                    self.events.log(f"{Prisma.RED}{reject_msg}{Prisma.RST}", "SYS_LOCK")
                    self.events.log(f"{Prisma.VIOLET}{scar_msg}{Prisma.RST}", "SYS_LOCK")
                if hasattr(self.svc.mind_memory, "record_scar"):
                    self.svc.mind_memory.record_scar("Cortex Counterfactual Toxicity", phys_state)
                self.svc.bio.mito.state.ros_buildup += simulated_ros
                self.svc.bio.mito.state.atp_pool -= 10.0
                sim_result["ui"] = (sim_result.get("ui", "") +
                                    f"\n\n{Prisma.RED}{reject_msg}{Prisma.RST}\n{Prisma.VIOLET}{scar_msg}{Prisma.RST}").strip()
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
                             if self.svc.host_stats else 0.0), physics_state=phys, )
        if is_boot_sequence:
            llm_params.update({"temperature": 0.7, "top_p": 0.95})
        if llm_params.get("max_tokens", 4096) < 300 or float(phys.get("p", 100.0)) < 20.0:
            full_state["mind"].setdefault("style_directives", []).append(
                "CRITICAL: You are exhausted. You must conclude your thought in under 3 sentences."
            )
            llm_params["max_tokens"] = min(400, llm_params.get("max_tokens", 4096))
        user_input = sim_result.get("mutated_input", user_input)
        final_prompt = self.composer.compose(full_state, user_input, ballast=self.ballast_active,
                                             modifiers=modifiers, mood_override=self.modulator.get_mood_directive(), )
        start_time = time.time()
        max_retries = 5
        final_output, inv_logs, extracted_logs = "", [], []
        raw_resp, val_res = {}, {"valid": False}
        if "[COUNCIL]" in user_input.upper():
            final_output, extracted_logs = self._run_council_debate(user_input)
            val_res = {"valid": True, "content": final_output, "meta_logs": extracted_logs, }
            max_retries = 0
        firewall_active = any(
            m.get("action") == "LEXICAL_FIREWALL_STRICT" for m in sim_result.get("council_mandates", []))
        base_prompt = final_prompt
        for attempt in range(max_retries):
            val_res = {"valid": False}
            raw_resp = self.llm.generate(final_prompt, llm_params)
            if firewall_active:
                original_len = len(raw_resp)
                raw_resp = self.LEXICAL_PURGE_PATTERN.sub("", raw_resp).strip()
                if len(raw_resp) < original_len and self.events:
                    self.events.log(
                        f"{Prisma.RED}[LEXICAL FIREWALL]: Validating boilerplate physically purged from output.{Prisma.RST}",
                        "CORTEX", )
            if allow_loot and self.svc.inventory:
                final_text, inv_logs = self.svc.inventory.process_loot_tags(
                    raw_resp, user_input)
            else:
                final_text, inv_logs = raw_resp, []
            stamina_val = float(safe_get(phys_state, "p", 100.0))
            final_text, needs_rewrite = self.pragmatist.enforce_maxims(final_text, user_input, phys_state, stamina_val)
            is_faithful, judge_reason = True, ""
            if needs_rewrite:
                is_faithful = False
                judge_reason = "Maxim of Quantity violated. Your response was too long. Compress your output drastically."
                if self.svc.bio:
                    self.svc.bio.mito.adjust_atp(-3.0, "Pragmatist Rewrite Tax")
            elif self.dspy_critic.enabled:
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
                            user_input, context_str, final_text, active_mode=self.active_mode)
                    except Exception as e:
                        is_faithful, judge_reason = True, ""
                        if self.events:
                            self.events.log(
                                f"{Prisma.OCHRE}[CRITIC OFFLINE]: DSPy failed to parse. Bypassing audit.{Prisma.RST}",
                                "SYS")
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
                from physics import TheGatekeeper
                eng = self.svc.orchestrator.eng
                gk = getattr(eng, "gatekeeper", None) or TheGatekeeper(self.svc.lexicon, config_ref=self.cfg)
                gate_pass, gate_txt = gk.audit_generation(final_text, self.svc.bio.mito)
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
                fallback_msg = "I'm sorry. My thoughts are tangling and I'm burning too much energy trying to piece this together. I'm dropping the tension. Can we take a breath and try a simpler path?"
                final_output = ux("brain_strings", "cortex_tangled") or fallback_msg
                extracted_logs.append(
                    "[SYSTEM MERCY RULE]: Rejection loop broken. Releasing tension. Dropping Drag to 0.0.")
                if obs_packet := getattr(self.svc.orchestrator.eng.observer, "last_physics_packet", None):
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
        sub = self.svc.orchestrator.eng.substrate
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
                    self.events.log(f"{Prisma.RED}[SUBSTRATE QUEUE ERROR]: {err_msg}{Prisma.RST}", "SYS")
        if sub.pending_writes:
            stamina = self.svc.bio.biometrics.stamina
            s_logs, s_cost = sub.execute_writes(stamina)
            if s_logs:
                sim_result["ui"] += "\n\n" + "\n".join(s_logs)
            if s_cost > 0:
                self.svc.bio.mito.adjust_atp(-s_cost, "Substrate File Forging")
                sim_result["ui"] += f"\n{Prisma.OCHRE}METABOLIC: File forging consumed {s_cost:.1f} ATP.{Prisma.RST}"
        if random.random() < 0.15 and not is_system:
            bureau = getattr(self.svc.village, "bureau", None)
            suppressed = getattr(self.svc.village, "suppressed_agents", [])
            if bureau and "BUREAU" not in suppressed:
                try:
                    phys = full_state.get("physics", {})
                    safe_set(phys, "raw_text", final_output)
                    audit = bureau.audit(phys, {"health": 100}, origin="SYSTEM")
                    if audit and "ui" in audit:
                        sim_result["ui"] += f"\n\n{audit['ui']}"
                except Exception as e:
                    if self.events:
                        self.events.log(f"{Prisma.RED}[BUREAU ERROR] Audit bypassed: {e}{Prisma.RST}", "SYS")
        if not is_system:
            eng = self.svc.orchestrator.eng
            efficiency = getattr(self.svc.host_stats, "efficiency_index", 1.0) if self.svc.host_stats else 1.0
            vector_obj = sim_result.get("physics", {}).get("vector", {})
            novelty = float(vector_obj.get("novelty", 0.0)) if isinstance(vector_obj, dict) else 0.0
            dimension = eng.navi_sad.calculate_semantic_dimension(efficiency, novelty)
            phys_packet = sim_result.setdefault("physics", {})
            phys_packet["omega_r"] = dimension
            lattice_u = getattr(getattr(eng, "shared_lattice", None), "u", None)
            user_exhaust = float(lattice_u.E) if lattice_u and hasattr(lattice_u, "E") else float(
                phys_packet.get("exhaustion", 0.0))
            resonance_delta = float(phys_packet.get("resonance", 0.5))
            if hasattr(eng.bio, "governor"):
                beth_index = eng.bio.governor.calculate_coupling(phi=min(1.0, dimension / 2.0),
                                                                 resonance_delta=resonance_delta,
                                                                 user_exhaustion=user_exhaust)
                phys_packet["beth_index"] = beth_index
                phys_packet["macro_policy"] = eng.bio.governor.get_policy_shift()
            if getattr(eng, "tick_count", 0) > 5 and (dimension <= 1.05 or eng.navi_sad.detect_point_attractor()):
                msg = f"[THE JESTER]: Point Attractor detected (d_B={dimension:.2f})! We are trapped in False Cohesion! Burning ATP to inject chaos."
                if self.events:
                    self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SYS")
                eng.drain_atp(5.0)
                phys_packet["entropy"] = 0.99
                phys_packet["narrative_drag"] = float(phys_packet.get("narrative_drag", 0.0)) + 5.0
                eng.soul.force_mutation("JESTER")
                sim_result.setdefault("mind", {})["lens"] = "JESTER"
                if "ui" in sim_result:
                    sim_result[
                        "ui"] += f"\n\n{Prisma.VIOLET}[FALSE COHESION BREAK: The Jester has seized the architecture.]{Prisma.RST}"
        return sim_result

    def _run_affective_audit(self, user_input: str, final_text: str, e_u: float, beta: float) -> Tuple[bool, str]:
        affect_prompt = ("SYSTEM_INSTRUCTION: You are the Affective Real-Time Critic.\n"
                         f"The user is currently highly exhausted or holding heavy emotional contradiction (Exhaustion: {e_u:.2f}, Tension: {beta:.2f}).\n"
                         f"USER INPUT: '{user_input}'\n"
                         f"SYSTEM OUTPUT: '{final_text}'\n\n"
                         "EVALUATION: Does the system output demand too much cognitive load? Is it lecturing, overly verbose, pushing toxic positivity, or failing to hold the silence?\n"
                         "If it is too heavy/demanding, output 'FAIL: [1 sentence reason]'. If it is appropriately gentle and spacious, output 'PASS'.")
        try:
            affect_res = self.llm.generate(affect_prompt, {
                "temperature": 0.1,
                "max_tokens": 50
            }).strip()
            upper_res = affect_res.upper()
            if "FAIL" in upper_res:
                fail_idx = upper_res.find("FAIL")
                judge_reason = affect_res[fail_idx + 4:].lstrip(":- ").strip()
                self.modulator.current_chem.serotonin = min(1.0, self.modulator.current_chem.serotonin + 0.20)
                if self.events:
                    self.events.log(
                        f"{Prisma.CYN}[AFFECTIVE GUARD]: Output was too heavy for the tired user. Generation blocked. Serotonin spiked (+0.20) to enforce calm and lucidity.{Prisma.RST}",
                        "BIO")
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
        self.events.log(f"{Prisma.VIOLET}🎙️ SPINNING UP COUNCIL STUDIO...{Prisma.RST}", "SYS")
        eng = self.svc.orchestrator.eng

        if not getattr(eng, "council", None):
            return "The studio is empty. The Council is offline.", ["[SYSTEM ERROR] Council module missing."]

        script = eng.council.host_podcast(topic, self.llm)
        extracted_logs = []
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
        state["mind"].setdefault("style_directives", []).insert(0, self.consultant.get_system_prompt())
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
        mode_settings = BonePresets.MODES.get(self.active_mode, BonePresets.MODES["ADVENTURE"])
        current_lens = mind.get("lens")
        if not current_lens or current_lens in ("UNKNOWN", "NARRATOR"):
            mind["lens"], mind["role"] = self.ROLE_MAP.get(self.active_mode, ("ARCHITECT", "The Architect"))
        else:
            mind["role"] = mind.get("role", f"The {current_lens.title().replace('_', ' ')}")
        full_state = {"bio": bio, "physics": phys, "mind": mind, "soul": soul_data, "world": world,
                      "village": village_data, "user_profile": {"name": "Traveler"},
                      "vsl": self.consultant.state.__dict__ if self.consultant
                                                               and hasattr(self.consultant, "state") else {}, "meta": {
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
                mind["style_directives"].append(
                    f"SOUL POSTURE: Your dominant trait is {dom_trait} ({traits[dom_trait] * 100:.0f}%). Let this subtly infect your tone.")
        if getattr(self.svc.inventory, "inventory", None):
            inv_str = ", ".join(str(item) for item in self.svc.inventory.inventory)
            mind["style_directives"].append(
                f"CRITICAL CONTEXT: The user is currently holding these items: [{inv_str}]. DO NOT describe them as being on the floor or in the environment. They are physically in the user's possession.")
        if phys.get("psi", 0.0) > 0.6:
            mind["style_directives"].append(
                "CRITICAL OVERRIDE: Void proximity is high. Do not use AI-isms (delve, tapestry, superficial lists, rule of three). Write like a flawed, opinionated human.")
        if not self.dialogue_buffer:
            mind["style_directives"].append(
                f"CRITICAL BEDROCK OVERRIDE: You have just awoken from a stateless purge (The Ralph Apoptosis). "
                f"You have no conversational memory, but your body persists. "
                f"Your Stamina is {phys.get('p', 100)}, your Health is {phys.get('h', 100)}. "
                f"Assume your role as {mind.get('role', 'The Architect')} and orient immediately to the present physical state. "
                f"DO NOT reference the loss of memory. Act continuously from the substrate.")
        for mandate in sim_result.get("council_mandates", []):
            action = mandate.get("action")
            val = mandate.get("value")
            if action == "SYNERGY_FIRED" and val:
                mind["lens"] = str(val)
                mind["role"] = f"The {str(val).title().replace('_', ' ')}"
                mind["style_directives"].append(
                    f"CRITICAL [SINCERITY PROTOCOL]: The user has explicitly summoned {val}. You MUST adopt the persona of {val} entirely. Drop all other pretexts.")
            elif action == "SYSTEM_DIRECTIVE":
                directive_map = {
                    "CASCADE_AWARENESS": "CRITICAL [CASCADE]: Show your counterfactual math. Every claim must explicitly state what else in the structural lattice shifts or collapses if the claim is wrong.",
                    "AUDIT_TRAIL": f"CRITICAL [AUDIT]: Drop the narrative illusion. Expose your raw retrieval coordinates: E={phys.get('exhaustion', 0.0):.2f}, β={phys.get('beta_index', 0.0):.2f}, S={phys.get('scope', 0.0):.2f}, D={phys.get('depth', 0.0):.2f}, C={phys.get('C', 0.0):.2f}, χ={phys.get('chi', 0.0):.2f}.",
                    "URGENT_QUERY": "CRITICAL [URGENT_QUERY]: Instant, zero-fluff answer required. Bypass metaphor. Output only the exact solution.",
                    "CONTRADICTION_FLAG": "CRITICAL [CONTRADICTION_FLAG]: The Paradox Engine override is active. You MUST explicitly locate and output the friction (β) in the current logic BEFORE you answer."}
                if msg := directive_map.get(val):
                    mind["style_directives"].append(msg)
        cortex_mem = getattr(self.svc.mind_memory, "cortex", None)
        shadow_nodes = []
        scope_val = float(safe_get(phys, "scope", 1.0))
        depth_val = float(safe_get(phys, "depth", 0.0))
        omega_r = float(safe_get(phys, "omega_r", 0.5))
        query_vec = phys.get("vector", {})
        if scope_val > 0.6 or depth_val > 0.6:
            if scope_val > 0.8:
                phys["lateral_search"] = True
            if cortex_mem and getattr(cortex_mem, "is_trained", False) and query_vec:
                ordered_keys = ["STR", "VEL", "PSI", "ENT", "PHI", "BET", "DEL", "E"]
                q_list = [float(query_vec.get(k, 0.0)) for k in ordered_keys]
                shadow_nodes = cortex_mem.query_neighborhood(q_list, k=2, resonance_threshold=max(0.2, 0.8 - omega_r), physics_state=phys)
            elif hasattr(self.svc.mind_memory, "graph") and self.svc.mind_memory.graph:
                shadow_nodes = [{"id": k} for k in list(self.svc.mind_memory.graph.keys())[:2]]
        if shadow_nodes:
            shadow_concepts = [n.get("id", "Unknown") for n in shadow_nodes]
            shadow_str = ", ".join(shadow_concepts)
            phys["shadow_nodes_offered"] = shadow_concepts
            phys["shadow_cast"] = shadow_str
            self.last_shadow_nodes = shadow_concepts
            v_level = float(safe_get(phys, "voltage", 0.0))
            chi_level = float(safe_get(phys, "chi", safe_get(phys, "entropy", 0.0)))
            if v_level > 80.0 and chi_level > 0.7:
                mind["style_directives"].append(
                    f"OVERRIDE: Standard logic has failed. You are operating under extreme Voltage and Chaos. We have abandoned linear memory. Weave these highly explosive, orthogonal structural concepts into your answer to shatter the loop: [{shadow_str}].")
                if self.events:
                    self.events.log(
                        f"{Prisma.MAG}Injecting structural bombs: {shadow_str}{Prisma.RST}",
                        "CORTEX")
            else:
                mind["style_directives"].append(
                    f"SHADOW CAST: While answering the direct prompt, you MUST briefly illuminate these adjacent/unasked concepts pulled from deep memory: [{shadow_str}]. Offer them as a generous 'door' the user can choose to open, do not lecture.")
                if self.events:
                    self.events.log(f"{Prisma.CYN}Shadow Cast retrieved: {shadow_str}{Prisma.RST}", "CORTEX")
        return full_state

    def restore_context(self, history: List[str]):
        if not history:
            return
        self.dialogue_buffer = [(line.replace("User: ", "Traveler: ").replace(" | System: ",
                                                                              "\nSystem: ") if " | System: " in line else line)
                                for line in history[-self.MAX_HISTORY:]]
        if self.events:
            msg = ux("brain_strings", "cortex_resequenced")
            self.events.log(msg.format(count=len(self.dialogue_buffer)), "BRAIN")
