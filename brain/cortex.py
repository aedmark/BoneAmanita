"""brian/cortex.py"""

import os
import random
import re
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from archetypes.symbiosis import SymbiosisManager
from brain.composer import LLMInterface, PromptComposer, ResponseValidator
from brain.linear_cortex import LinearCortexRouter
from brain.mind import DreamEngine, NeurotransmitterModulator
from constants import Prisma
from core import DecisionCrystal, EventBus, LoreManifest, TelemetryService
from mechanics.dspycritic import DSPyCritic
from mechanics.pragmatics import ThePragmatist
from mechanics.projector import beautify_thoughts
from mechanics.tools import LibraryGraph, RandomRetrievalNavigator
from presets import BoneConfig, BonePresets
from struts import dump_state, safe_get, safe_set, ux


@dataclass
class CortexServices:
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
    LEXICAL_PURGE_PATTERN = re.compile(
        r"(?im)^\s*(that makes sense|i understand|you bring up|great point|good point|certainly|absolutely|i hear you|yes, )[.,!]*\s*"
    )
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
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        self.MAX_HISTORY = int(safe_get(c_cfg, "MAX_HISTORY_LENGTH", 15))
        self.dialogue_buffer = deque(maxlen=self.MAX_HISTORY)
        self.worry_ledger = deque(maxlen=20)
        self.modulator = NeurotransmitterModulator(
            bio_ref=self.svc.bio, events_ref=self.events, config_ref=self.cfg
        )
        self.last_physics = {}
        self.last_shadow_nodes = []
        self.consultant = services.consultant
        self.llm = llm_client or LLMInterface(
            self.events, provider="mock", config_ref=self.cfg
        )
        eng_ref = self.svc.orchestrator.eng if self.svc.orchestrator else None
        if eng_ref and hasattr(eng_ref, "mind") and hasattr(eng_ref.mind, "dreamer"):
            self.dreamer = eng_ref.mind.dreamer
            self.dreamer.llm = self.llm
            self.dreamer.mem = self.svc.mind_memory
        else:
            self.dreamer = DreamEngine(
                self.events,
                self.svc.lore,
                llm_ref=self.llm,
                mem_ref=self.svc.mind_memory,
                eng_ref=eng_ref,
                config_ref=self.cfg,
            )
        self.llm.dreamer = self.dreamer
        self.symbiosis = services.symbiosis
        self.composer = PromptComposer(self.svc.lore, config_ref=self.cfg)
        self.validator = ResponseValidator(self.svc.lore, config_ref=self.cfg)
        self.pragmatist = ThePragmatist(events_ref=self.events)
        self.dspy_critic = DSPyCritic(config_ref=self.cfg)
        self.dreamer.dspy_critic = self.dspy_critic
        self.active_mode = "ADVENTURE"
        if hasattr(self.svc.mind_memory, "nodes"):
            graph = LibraryGraph(
                nodes=self.svc.mind_memory.nodes, root=self.svc.mind_memory.root
            )
            self.navigator = RandomRetrievalNavigator(library_graph=graph)
        else:
            self.navigator = None

        self.linear_router = LinearCortexRouter(token_budget=12000)
        self.is_linear_stocked = False

    @classmethod
    def from_engine(cls, engine_ref, llm_client=None):
        target_cfg = getattr(engine_ref, "config", BoneConfig)
        symbiosis_mgr = getattr(engine_ref, "symbiosis", None) or SymbiosisManager(
            engine_ref.events
        )
        services = CortexServices(
            events=engine_ref.events,
            lore=LoreManifest.get_instance(config_ref=target_cfg),
            lexicon=engine_ref.lex,
            inventory=getattr(engine_ref.village, "gordon", None)
            if hasattr(engine_ref, "village")
            else None,
            consultant=engine_ref.consultant,
            orchestrator=engine_ref.orchestrator,
            symbiosis=symbiosis_mgr,
            mind_memory=engine_ref.mind.mem,
            bio=engine_ref.bio,
            host_stats=engine_ref.host_stats,
            village=engine_ref.village,
            config_ref=target_cfg,
        )
        instance = cls(services, llm_client)
        instance.active_mode = getattr(engine_ref, "boot_mode", "ADVENTURE").upper()
        if instance.active_mode not in BonePresets.MODES:
            instance.active_mode = "ADVENTURE"
        return instance

    def _update_history(self, user_text: str, system_text: str):
        self.dialogue_buffer.append(f"Traveler: {user_text}\nSystem: {system_text}")

    def shutdown(self):
        pass

    def purge_context(self):
        self.last_shadow_nodes = []
        self.dialogue_buffer.clear()
        self.last_physics.clear()
        try:
            self.dreamer.trauma_buffer.clear()
        except AttributeError:
            pass
        if self.events:
            self.events.log(
                "Context array purged. Stateless bedrock re-established.",
                "SYS",
            )

    def process_context(self, ctx: Any) -> Dict[str, Any]:
        user_input = ctx.input_text or ""
        is_system = getattr(ctx, "is_system_event", False)
        mode_settings = BonePresets.MODES.get(
            self.active_mode, BonePresets.MODES["ADVENTURE"]
        )
        allow_loot = mode_settings.get("allow_loot", True)
        if self.navigator:
            target_randomness = {
                "CREATIVE": 0.7,
                "ADVENTURE": 0.3,
                "CONVERSATION": 0.3,
            }.get(self.active_mode, 0.0)
            dial_status = self.navigator.set_randomness(target_randomness)
            if self.events and dial_status["new_value"] > 0:
                self.events.log(
                    f"Serendipity Engine active: {dial_status['mode']}", "CORTEX"
                )
        if self.consultant and "/vsl" in user_input.lower():
            return self._handle_vsl_command(user_input)
        is_boot_sequence = "SYSTEM_BOOT" in user_input
        phys_proxy = dump_state(ctx.physics) if ctx.physics is not None else {}
        sim_result = {
            "physics": phys_proxy,
            "bio": getattr(ctx, "bio_result", {}),
            "mind": getattr(ctx, "mind_state", {}),
            "world": getattr(ctx, "world_state", {}),
            "ui": getattr(ctx, "bureau_ui", ""),
            "logs": getattr(ctx, "logs", []),
            "council_mandates": getattr(ctx, "council_mandates", []),
            "dream": getattr(ctx, "last_dream", None),
            "mutated_input": user_input,
            "trace_id": getattr(ctx, "trace_id", "UNKNOWN"),
            "type": getattr(ctx, "type", "SNAPSHOT"),
        }
        if halt := self._pre_flight_routing(
            user_input, is_system, is_boot_sequence, ctx, sim_result
        ):
            return halt
        user_input = sim_result.get("mutated_input", user_input)
        if sim_result.get("physics"):
            self.last_physics = sim_result["physics"]
        if self.last_shadow_nodes:
            engaged = [
                node
                for node in self.last_shadow_nodes
                if node.lower() in user_input.lower()
            ]
            for node in engaged:
                if self.events:
                    self.events.publish(
                        "SHADOW_ENGAGED",
                        {
                            "source": self.last_physics.get("primary_node", "core")
                            if self.last_physics
                            else "core",
                            "target": node,
                            "user_input": user_input,
                        },
                    )
            self.last_shadow_nodes = []
        full_state = self.gather_state(sim_result)
        phys_state = full_state.get("physics", {})
        if tox_halt := self._evaluate_toxicity(phys_state, sim_result, is_system):
            return tox_halt
        modifiers = self.svc.symbiosis.get_prompt_modifiers(phys_state)
        if not allow_loot or is_boot_sequence:
            modifiers["include_inventory"] = False
        if self.consultant and self.consultant.active:
            self._apply_vsl_overlay(full_state, user_input, sim_result)
        if is_boot_sequence:
            self._apply_boot_overlay(full_state, user_input)
        b_voltage = float(phys_state.get("voltage", 5.0))
        llm_params = self.modulator.modulate(
            base_voltage=b_voltage,
            latency_penalty=getattr(self.svc.host_stats, "latency", 0.0),
            physics_state=phys_state,
        )
        if is_boot_sequence:
            llm_params.update({"temperature": 0.7, "top_p": 0.95})
        p_val = float(phys_state.get("p", 100.0))
        if llm_params.get("max_tokens", 4096) < 300 or p_val < 20.0:
            full_state["mind"].setdefault("style_directives", []).append(
                "CRITICAL: You are exhausted. You must conclude your thought in under 3 sentences."
            )
            llm_params["max_tokens"] = min(400, llm_params.get("max_tokens", 4096))

        structural_ctx, cognitive_path, token_cost = self._route_dual_memory(user_input)
        if structural_ctx:
            full_state["mind"].setdefault("style_directives", []).append(
                f"CRITICAL STRUCTURAL CONTEXT (Linear Sweep):\n{structural_ctx}"
            )
            if hasattr(self.svc.bio.mito, "process_cognitive_load"):
                self.svc.bio.mito.process_cognitive_load(token_cost, cognitive_path)

        final_prompt = self.composer.compose(
            full_state,
            user_input,
            ballast=self.ballast_active,
            modifiers=modifiers,
            mood_override=self.modulator.get_mood_directive(),
        )
        start_time = time.time()
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        cognitive_retries = int(safe_get(c_cfg, "COGNITIVE_RETRY_LIMIT", 2))
        final_output, inv_logs, extracted_logs = "", [], []
        raw_resp: str = ""
        val_res: Dict[str, Any] = {"valid": False}
        if "[COUNCIL]" in user_input.upper():
            final_output, extracted_logs = self._run_council_debate(user_input)
            val_res = {
                "valid": True,
                "content": final_output,
                "meta_logs": extracted_logs,
            }
        mandates_raw = sim_result.get("council_mandates", [])
        firewall_active = any(
            m.get("action") == "LEXICAL_FIREWALL_STRICT" for m in mandates_raw
        )
        base_prompt = final_prompt
        eng_ref = getattr(self.svc.orchestrator, "eng", None)
        gk = getattr(eng_ref, "gatekeeper", None)
        if not gk:
            from physics import TheGatekeeper

            gk = TheGatekeeper(self.svc.lexicon, config_ref=self.cfg)
        if cognitive_retries > 0:
            final_output, raw_resp, extracted_logs, inv_logs, val_res, final_prompt = (
                self._execute_cognitive_loop(
                    user_input,
                    full_state,
                    base_prompt,
                    llm_params,
                    allow_loot,
                    phys_state,
                    is_boot_sequence,
                    firewall_active,
                    gk,
                    cognitive_retries,
                )
            )
            if self.svc.bio and raw_resp:
                gen_tokens = max(1, len(raw_resp) // 4)
                ros_yield = gen_tokens * 0.015
                atp_burn = gen_tokens * 0.025

                try:
                    current_ros = float(self.svc.bio.mito.state.ros_buildup)
                    self.svc.bio.mito.state.ros_buildup = min(
                        100.0, current_ros + ros_yield
                    )
                except (TypeError, ValueError, AttributeError):
                    pass

                try:
                    self.svc.bio.mito.adjust_atp(-atp_burn, "LLM Token Generation")
                except (TypeError, AttributeError):
                    pass
        if val_res["valid"] and phys_state.get("psi", 0.0) > 0.6 and allow_loot:
            if self.svc.bio:
                self.svc.bio.mito.adjust_atp(-1.0, "Anti-AI Substrate Filter")
        telemetry_output = raw_resp if not val_res["valid"] else final_output
        self._log_telemetry(final_prompt, telemetry_output, full_state, sim_result)
        self.svc.symbiosis.monitor_host(
            time.time() - start_time, final_output, len(final_prompt)
        )
        self._update_history(
            "SYSTEM_INIT" if is_boot_sequence else user_input, final_output
        )
        ui_parts = [sim_result.get("ui", "")]
        if sim_result.get("dream"):
            dream_content = sim_result["dream"]
            if isinstance(dream_content, tuple):
                dream_content = dream_content[0]
            elif isinstance(dream_content, dict):
                dream_content = dream_content.get("log", str(dream_content))
            ui_parts.append(
                f"{Prisma.VIOLET}While you were gone: {dream_content}{Prisma.RST}"
            )
        ui_parts.append(f"{Prisma.WHT}{beautify_thoughts(final_output)}{Prisma.RST}")
        if inv_logs:
            ui_parts.append("\n".join(inv_logs))
        sim_result["ui"] = "\n\n".join(filter(None, (str(p).strip() for p in ui_parts)))
        sim_result["logs"] = sim_result.get("logs", []) + extracted_logs
        sim_result["raw_content"] = final_output
        self.ballast_active = False
        self._flush_substrate_writes(extracted_logs, sim_result)
        self._post_flight_mutations(
            val_res, phys_state, sim_result, final_output, is_system, full_state
        )
        updated_phys = sim_result.get("physics", {})
        if isinstance(updated_phys, dict):
            if isinstance(ctx.physics, dict):
                ctx.physics.update(updated_phys)
            else:
                for k, v in updated_phys.items():
                    setattr(ctx.physics, k, v)
        return sim_result

    def _pre_flight_routing(
        self,
        user_input: str,
        is_system: bool,
        is_boot_sequence: bool,
        ctx: Any,
        sim_result: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        context_limit = int(safe_get(c_cfg, "MAX_INPUT_CHARS", 15000))
        if len(user_input) > context_limit and not is_system and not is_boot_sequence:
            safe_content = user_input.replace("\n", "|||NEWLINE|||")
            self.dreamer.context_queue.append(safe_content)
            s_cost = 5.0
            if self.svc.bio:
                self.svc.bio.mito.adjust_atp(-s_cost, "Massive Context Queueing")
            msg = f"{Prisma.CYN}Massive context drop detected. Routed to REM cycle for deep-indexing. Dialogue buffer bypassed. (-{s_cost:.1f} ATP){Prisma.RST}"
            if self.events:
                self.events.log(msg, "SYS")
            sim_result.update({"ui": msg, "type": "SILENT_INGEST"})
            return sim_result
        if getattr(ctx, "refusal_triggered", False) and getattr(
            ctx, "refusal_packet", None
        ):
            sim_result.update(ctx.refusal_packet)
            self._update_history(
                user_input, str(sim_result.get("ui", "SYSTEM REJECTED PROMPT."))
            )
            return sim_result
        if is_boot_sequence:
            user_input = (
                user_input.replace("SYSTEM_BOOT DETECTED.", "")
                .replace("SYSTEM_BOOT:", "")
                .strip()
            )
            sim_result["mutated_input"] = user_input
        return None

    def _evaluate_toxicity(
        self, phys_state: Dict[str, Any], sim_result: Dict[str, Any], is_system: bool
    ) -> Optional[Dict[str, Any]]:
        tick_atp = float(phys_state.get("delta_atp", 0.0))
        tick_ros = float(phys_state.get("delta_ros", 0.0))
        if tick_atp != 0.0:
            self.svc.bio.mito.adjust_atp(tick_atp, "Creative Determinant Tick")
        if tick_ros != 0.0:
            self.svc.bio.mito.state.ros_buildup = max(
                0.0, min(100.0, self.svc.bio.mito.state.ros_buildup + tick_ros)
            )
        if (
            not is_system
            and self.svc.orchestrator
            and hasattr(self.svc.orchestrator, "eng")
        ):
            eng = self.svc.orchestrator.eng
            efficiency = (
                getattr(self.svc.host_stats, "efficiency_index", 1.0)
                if self.svc.host_stats
                else 1.0
            )
            energy_state = phys_state.get("energy", {})
            novelty = float(
                phys_state.get(
                    "novelty",
                    energy_state.get("novelty", 0.0)
                    if isinstance(energy_state, dict)
                    else getattr(energy_state, "novelty", 0.0),
                )
            )
            if hasattr(eng, "navi_sad"):
                dimension = eng.navi_sad.calculate_semantic_dimension(
                    efficiency, novelty
                )
                phys_state["omega_r"] = dimension
            else:
                dimension = phys_state.get("omega_r", 1.0)
            lattice_u = getattr(getattr(eng, "shared_lattice", None), "u", None)
            user_exhaust = (
                float(lattice_u.E)
                if lattice_u and hasattr(lattice_u, "E")
                else float(phys_state.get("exhaustion", 0.0))
            )
            resonance_delta = float(phys_state.get("resonance", 0.5))
            if hasattr(eng, "governor"):
                phys_state["beth_index"] = eng.governor.calculate_coupling(
                    phi=min(1.0, dimension / 2.0),
                    resonance_delta=resonance_delta,
                    user_exhaustion=user_exhaust,
                )
                phys_state["macro_policy"] = eng.governor.get_policy_shift()
        f_drag = float(phys_state.get("narrative_drag", 0.0))
        chi_val = float(phys_state.get("chi", phys_state.get("entropy", 0.0)))
        m_a = float(phys_state.get("m_a", 0.0))
        tolerance_mod = (
            1.5 if getattr(self, "active_mode", "") in ["CREATIVE", "CATALYST"] else 1.0
        )
        drag_limit = 1.5 * tolerance_mod
        chi_limit = 0.8 * tolerance_mod
        if (f_drag > drag_limit or chi_val > chi_limit) and m_a < 0.3:
            worry_text = sim_result.get("mutated_input", "")
            self.worry_ledger.append(worry_text)
            phys_state["narrative_drag"] = 0.0
            moog_msg = "The parameters of this concern are undefined. I am placing this in the ledger. We will not spend ATP on this right now."
            if self.events:
                self.events.log(
                    f"{Prisma.CYN}[MOOG INTERCEPT]: {moog_msg}{Prisma.RST}", "SYS"
                )
            sim_result["ui"] = (
                str(sim_result.get("ui", "")) + f"\n\n[GORDON]: {moog_msg}"
            ).strip()
            sim_result["type"] = "MOOG_QUARANTINE"
            return sim_result
        if f_drag > drag_limit or chi_val > chi_limit:
            reject_msg = ux(
                "cortex_strings",
                "gordon_anchor_lock",
                default="Frequency too high. Tensegrity Anchor engaged. I am locking the architecture. Take a breath and lower your narrative friction before we proceed.",
            )
            if self.events:
                self.events.log(f"{Prisma.RED}{reject_msg}{Prisma.RST}", "SYS_LOCK")
            sim_result["ui"] = (
                str(sim_result.get("ui", ""))
                + f"\n\n{Prisma.RED}{reject_msg}{Prisma.RST}"
            ).strip()
            sim_result["type"] = "SYSTEM_HALT"
            return sim_result
        simulated_ros = (f_drag * 5.0) + (chi_val * 20.0) + (m_a * 30.0)
        if simulated_ros > 35.0:
            reject_msg = ux(
                "brain_strings", "pinker_cf_gate", default="Structural rot critical."
            )
            scar_msg = ux(
                "brain_strings", "moog_scar_log", default="Productive Worry activated."
            )
            if self.events:
                self.events.log(f"{Prisma.RED}{reject_msg}{Prisma.RST}", "SYS_LOCK")
                self.events.log(f"{Prisma.VIOLET}{scar_msg}{Prisma.RST}", "SYS_LOCK")
            self.svc.mind_memory.record_scar(
                "Cortex Counterfactual Toxicity", phys_state
            )
            self.svc.bio.mito.state.ros_buildup = (
                float(self.svc.bio.mito.state.ros_buildup) + simulated_ros
            )
            self.svc.bio.mito.adjust_atp(-10.0, "Cortex Counterfactual Toxicity")
            sim_result["ui"] = (
                str(sim_result.get("ui", ""))
                + f"\n\n{Prisma.RED}{reject_msg}{Prisma.RST}\n{Prisma.VIOLET}{scar_msg}{Prisma.RST}"
            ).strip()
            sim_result["type"] = "COUNTERFACTUAL_REJECTION"
            return sim_result
        return None

    def _post_flight_mutations(
        self,
        val_res: Dict[str, Any],
        phys_state: Dict[str, Any],
        sim_result: Dict[str, Any],
        final_output: str,
        is_system: bool,
        full_state: Dict[str, Any],
    ):
        if random.random() < 0.15 and not is_system:
            bureau = getattr(self.svc.village, "bureau", None)
            suppressed = getattr(self.svc.village, "suppressed_agents", [])
            if bureau and hasattr(bureau, "audit") and "BUREAU" not in suppressed:
                try:
                    phys = full_state.get("physics", {})
                    safe_set(phys, "raw_text", final_output)
                    audit = bureau.audit(phys, {"health": 100}, origin="SYSTEM")
                    if audit and "ui" in audit:
                        sim_result["ui"] = (
                            str(sim_result.get("ui", "")) + f"\n\n{audit['ui']}"
                        )
                except Exception as e:
                    if self.events:
                        self.events.log(
                            f"{Prisma.RED}[BUREAU ERROR] Audit bypassed: {e}{Prisma.RST}",
                            "SYS",
                        )
        if (
            not is_system
            and self.svc.orchestrator
            and hasattr(self.svc.orchestrator, "eng")
        ):
            eng = self.svc.orchestrator.eng
            dimension = float(phys_state.get("omega_r", 1.0))
            repetition = float(phys_state.get("repetition", 0.0))
            is_attractor = (
                eng.navi_sad.detect_point_attractor()
                if hasattr(eng, "navi_sad")
                else False
            )
            is_valid = val_res.get("valid", False)
            trigger_jester = False
            tick_count = getattr(eng, "tick_count", 0)
            if tick_count > 2:
                if is_attractor or repetition >= 0.8:
                    trigger_jester = True
                elif dimension <= 1.05 and not (not is_valid and dimension == 1.0):
                    trigger_jester = True
            if trigger_jester:
                msg = f"The Jester detected a Point Attractor (d_B={dimension:.2f})! We are trapped in False Cohesion! Burning ATP to inject chaos."
                if self.events:
                    self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SYS")
                if hasattr(eng, "drain_atp"):
                    eng.drain_atp(5.0)
                phys_state["entropy"] = 0.99
                phys_state["narrative_drag"] = (
                    float(phys_state.get("narrative_drag", 0.0)) + 5.0
                )
                if hasattr(eng, "soul") and hasattr(eng.soul, "force_mutation"):
                    eng.soul.force_mutation("JESTER")
                mind_state = sim_result.setdefault("mind", {})
                mind_state["lens"] = "JESTER"
                if "ui" in sim_result:
                    sim_result["ui"] = (
                        str(sim_result.get("ui", ""))
                        + f"\n\n{Prisma.VIOLET}[FALSE COHESION BREAK: The Jester has seized the architecture.]{Prisma.RST}"
                    )

    def _execute_cognitive_loop(
        self,
        user_input: str,
        full_state: Dict[str, Any],
        base_prompt: str,
        llm_params: Dict[str, Any],
        allow_loot: bool,
        phys_state: Dict[str, Any],
        is_boot_sequence: bool,
        firewall_active: bool,
        gk: Any,
        cognitive_retries: int,
    ) -> Tuple[str, str, List[str], List[str], Dict[str, Any], str]:
        final_output, inv_logs, extracted_logs = "", [], []
        raw_resp = ""
        val_res = {"valid": False}
        final_prompt = base_prompt
        for attempt in range(cognitive_retries):
            if attempt > 0:
                phys_state["is_steering_retry"] = True
            val_res = {"valid": False}
            raw_resp = self.llm.generate(final_prompt, llm_params)
            if firewall_active:
                original_len = len(raw_resp)
                raw_resp = self.LEXICAL_PURGE_PATTERN.sub("", raw_resp).strip()
                if len(raw_resp) < original_len and self.events:
                    self.events.log(
                        f"{Prisma.RED}Validating boilerplate physically purged from output.{Prisma.RST}",
                        "CORTEX",
                    )
            if allow_loot and self.svc.inventory:
                final_text, inv_logs = self.svc.inventory.process_loot_tags(
                    raw_resp, user_input
                )
            else:
                final_text, inv_logs = raw_resp, []
            stamina_val = float(phys_state.get("p", 100.0))
            final_text, needs_rewrite = self.pragmatist.enforce_maxims(
                final_text, user_input, phys_state, stamina_val
            )
            if needs_rewrite:
                val_res["feedback_instruction"] = (
                    "CRITICAL FAILURE: Maxim of Quantity violated. Your response was too long."
                )
            if (
                not val_res.get("feedback_instruction")
                and self.dspy_critic.enabled
                and self.active_mode in ["ADVENTURE", "CONVERSATION"]
                and not is_boot_sequence
            ):
                mem_core = getattr(self.svc.mind_memory, "memory_core", None)
                active_mems = (
                    mem_core.illuminate(full_state["physics"].get("vector", {}))
                    if mem_core and hasattr(mem_core, "illuminate")
                    else []
                )
                ctx_str = (
                    "Active Memory: " + ", ".join(active_mems)
                    if active_mems
                    else "Empty Void."
                )
                try:
                    is_faithful, judge_reason = self.dspy_critic.audit_generation(
                        user_input, ctx_str, final_text, active_mode=self.active_mode
                    )
                    if not is_faithful:
                        val_res["feedback_instruction"] = (
                            f"CRITICAL FAILURE: {judge_reason}. If the user is exhausted, drastically shorten and soften your tone."
                        )
                        if self.events:
                            self.events.log(
                                f"DSPy Critic Objected: {judge_reason.split('.')[0][:60]}...",
                                "SYS",
                            )
                except Exception:
                    if self.events:
                        self.events.log(
                            f"{Prisma.OCHRE}[CRITIC OFFLINE]: DSPy parse failed. Bypassing.{Prisma.RST}",
                            "SYS",
                        )
            if not val_res.get("feedback_instruction"):
                e_u = float(phys_state.get("exhaustion", 0.0))
                beta = float(
                    phys_state.get("beta_index", phys_state.get("contradiction", 0.0))
                )
                if e_u > 0.6 or beta > 0.7:
                    is_faithful, judge_reason = self._run_heuristic_audit(
                        user_input, final_text, e_u, beta
                    )
                    if not is_faithful:
                        val_res["feedback_instruction"] = (
                            f"CRITICAL FAILURE: {judge_reason} Prioritize presence over output. Stay in character."
                        )
            if not val_res.get("feedback_instruction"):
                gate_pass, gate_txt = gk.audit_generation(final_text, self.svc.bio.mito)
                if not gate_pass or "IMMUNOSUPPRESSION ENGAGED" in gate_txt:
                    val_res.update(
                        {
                            "feedback_instruction": "HLA Stabilizer flagged toxic AI slop. Drop the corporate persona immediately.",
                            "replacement": "Gatekeeper Apoptotic Block.",
                            "meta_logs": ["[SYSTEM] HLA Stabilizer engaged."],
                        }
                    )
                else:
                    val_res = self.validator.validate(gate_txt, full_state)
            if val_res.get("valid"):
                final_output = val_res["content"]
                extracted_logs = val_res.get("meta_logs", [])
                if val_res.get("learned_triplet") and self.events:
                    self.events.publish(
                        "SYNTAX_CORRECTED", {"triplet": val_res["learned_triplet"]}
                    )
                break
            if self.svc.bio:
                lbl = (
                    "Cognitive Stumble (Terminal)"
                    if attempt == cognitive_retries - 1
                    else "Cognitive Stumble"
                )
                penalty = (
                    0.5
                    if getattr(self, "active_mode", "")
                    in ["CREATIVE", "CATALYST", "ADVENTURE"]
                    else 2.0
                )
                self.svc.bio.mito.adjust_atp(-penalty, lbl)
                self.svc.bio.mito.state.ros_buildup = (
                    float(self.svc.bio.mito.state.ros_buildup) + penalty
                )
            if attempt == cognitive_retries - 1:
                fallback_msg = "I'm sorry. My thoughts are tangling and I'm burning too much energy trying to piece this together. I'm dropping the tension. Can we take a breath and try a simpler path?"
                final_output = ux("brain_strings", "cortex_tangled") or fallback_msg
                extracted_logs.append(
                    "[SYSTEM MERCY RULE]: Rejection loop broken. Releasing tension. Dropping Drag to 0.0."
                )
                if self.last_physics:
                    safe_set(self.last_physics, "narrative_drag", 0.0)
                break
            rejection_reason = val_res.get("feedback_instruction") or val_res.get(
                "replacement", "Lattice structural crime."
            )
            if hasattr(self.dreamer, "trauma_buffer"):
                self.dreamer.trauma_buffer.append(rejection_reason)
            damping = 0.6
            llm_params["temperature"] = round(
                (1 - damping) * llm_params.get("temperature", 0.7) + damping * 0.2, 2
            )
            llm_params["frequency_penalty"] = round(
                (1 - damping) * llm_params.get("frequency_penalty", 0.0)
                + damping * 1.5,
                2,
            )
            llm_params["top_p"] = round(
                (1 - damping) * llm_params.get("top_p", 0.95) + damping * 0.5, 2
            )

            if self.events:
                self.events.log(
                    f"{Prisma.OCHRE}{(ux('brain_strings', 'cortex_retry') or '').format(attempt=attempt + 1)}{Prisma.RST}",
                    "CORTEX",
                )
            final_prompt = (
                f"{base_prompt}\n\n=== SYSTEM REJECTION ===\nREASON: {rejection_reason}\n\n"
                "DIRECTIVE: Your previous attempt to answer the PARTNER INPUT was factually or structurally invalid. DISCARD IT. "
                "Generate a NEW response specifically addressing the most recent PARTNER INPUT. DO NOT apologize or mention the fix. "
                "Output ONLY the raw in-character response and nothing else."
            )
        return final_output, raw_resp, extracted_logs, inv_logs, val_res, final_prompt

    def _flush_substrate_writes(
        self, extracted_logs: List[str], sim_result: Dict[str, Any]
    ):
        eng_ref = getattr(self.svc.orchestrator, "eng", None)
        sub = getattr(eng_ref, "substrate", None)
        for log in extracted_logs:
            if (
                sub
                and hasattr(sub, "queue_write")
                and isinstance(log, str)
                and log.startswith("[SUBSTRATE_QUEUE]")
            ):
                try:
                    _, _, data = log.partition(" ")
                    path, _, safe_content = data.partition(":::")
                    if path and safe_content:
                        clean_path = path.strip()
                        if ".." in clean_path or os.path.isabs(clean_path):
                            raise ValueError(
                                f"Path traversal blocked by Cortex Sentinel: {clean_path}"
                            )
                        sub.queue_write(
                            clean_path, safe_content.replace("|||NEWLINE|||", "\n")
                        )
                except Exception as e:
                    err_msg = f"Failed to parse or write file block. {e}"
                    if self.events:
                        self.events.log(
                            f"{Prisma.RED}[SUBSTRATE QUEUE ERROR]: {err_msg}{Prisma.RST}",
                            "SYS",
                        )
        if (
            sub
            and getattr(sub, "pending_writes", False)
            and hasattr(sub, "execute_writes")
        ):
            stamina = self.svc.bio.biometrics.stamina
            s_logs, s_cost = sub.execute_writes(stamina)
            if s_logs:
                sim_result["ui"] = (
                    str(sim_result.get("ui", "")) + "\n\n" + "\n".join(s_logs)
                )
            if s_cost > 0:
                self.svc.bio.mito.adjust_atp(-s_cost, "Substrate File Forging")
                sim_result["ui"] = (
                    str(sim_result.get("ui", ""))
                    + f"\n{Prisma.OCHRE}METABOLIC: File forging consumed {s_cost:.1f} ATP.{Prisma.RST}"
                )

    def _run_council_debate(self, user_input: str) -> Tuple[str, List[str]]:
        eng_ref = getattr(self.svc.orchestrator, "eng", None)
        council_ref = getattr(eng_ref, "council", None) or getattr(
            self.svc.village, "council", None
        )
        phys = getattr(self, "last_physics", {})
        bio_state = (
            {
                "stamina": getattr(
                    getattr(self.svc.bio, "biometrics", None), "stamina", 100.0
                )
            }
            if self.svc.bio
            else {}
        )
        try:
            transcript, adjustments, mandates = council_ref.convene(
                user_input, phys, bio_state
            )
        except (AttributeError, TypeError):
            return "The Parliament doors are sealed. No voices respond.", [
                "[COUNCIL ERROR]: CouncilChamber not found in architecture."
            ]
        for key, val in adjustments.items():
            curr_val = float(phys.get(key, 0.0))
            phys[key] = curr_val + val
        final_text = "\n\n".join(transcript)
        meta_logs = [
            f"The Council's Latest Mandate: {m.get('action', m.get('type', 'UNKNOWN'))}"
            for m in mandates
        ]
        return final_text, meta_logs

    def _run_heuristic_audit(
        self, user_input: str, final_text: str, e_u: float, beta: float
    ) -> Tuple[bool, str]:
        """
        [S.L.A.S.H. Heuristic Guillotine]: Replaces expensive LLM affective check
        with rapid heuristic validation. Measures cognitive load without burning TTFT.
        """
        try:
            word_count = len(final_text.split())
            has_question = "?" in final_text

            if e_u > 0.8:
                if word_count > 100:
                    return (
                        False,
                        f"Response too verbose ({word_count} words) for an exhausted user.",
                    )
                if has_question:
                    return (
                        False,
                        "Interrogating an exhausted user increases cognitive load. Drop the question.",
                    )

            if beta > 0.8 and word_count > 150:
                return (
                    False,
                    f"Response too heavy ({word_count} words) during high structural tension.",
                )

            return True, ""
        except Exception as e:
            if self.events:
                self.events.log(
                    f"{Prisma.OCHRE}[HEURISTIC AUDIT ERROR]: {e} - Bypassing.{Prisma.RST}",
                    "SYS",
                )
            return True, ""

    def _handle_vsl_command(self, text):
        if not self.consultant:
            return {"ui": "VSL Unavailable", "logs": []}
        msg = (
            self.consultant.engage() if "start" in text else self.consultant.disengage()
        )
        self.events.log(msg, "VSL")
        return {"ui": f"{Prisma.CYN}{msg}{Prisma.RST}", "logs": [msg]}

    def _apply_vsl_overlay(self, state, text, sim_result):
        if not self.consultant:
            return
        self.consultant.update_coordinates(
            text, state.get("bio", {}), state.get("physics")
        )
        state["mind"].setdefault("style_directives", []).insert(
            0, self.consultant.get_system_prompt()
        )
        sim_result["physics"]["voltage"] = self.consultant.state.B * 30.0

    def _apply_boot_overlay(self, state, text):
        seed = (
            text.replace("SYSTEM_BOOT DETECTED.", "")
            .replace("SYSTEM_BOOT:", "")
            .strip()
        )
        state.setdefault("world", {})
        mode_name = getattr(self, "active_mode", "ADVENTURE").upper()
        boot_rules = (
            (self.svc.lore.get("SYSTEM_PROMPTS") or {})
            .get("BOOT_SEQUENCE", {})
            .get("directives", [])
        )
        cfg: Dict[str, Any] = {"history": []}
        if mode_name == "ADVENTURE":
            adv_directives = [
                r.format(seed=seed) if "{seed}" in r else r for r in boot_rules
            ]
            if not adv_directives:
                adv_directives = [
                    f"SYSTEM_BOOT DETECTED. The user has arrived at the thought seed: '{seed}'.",
                    "DIRECTIVE: You are a vivid, immersive text adventure engine. Render the starting location.",
                    "ACTION: Describe the environment based on the seed. Include sensory details. Conclude your response by listing 'Points of Interest' and 'Exits' in classic MUD style.",
                ]
            cfg.update(
                {
                    "world": {
                        "orbit": [seed],
                        "loci_description": f"Manifesting: {seed}",
                    },
                    "mind": {
                        "role": "The Architect",
                        "lens": "ARCHITECT",
                        "style_directives": adv_directives,
                    },
                }
            )
        elif mode_name == "CONVERSATION":
            cfg.update(
                {
                    "mind": {
                        "role": "The Conversationalist",
                        "lens": "CONVERSATIONALIST",
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
                    ],
                }
            )
        elif mode_name == "TECHNICAL":
            cfg.update(
                {
                    "mind": {
                        "role": "The System Kernel",
                        "lens": "SYSTEM_KERNEL",
                        "style_directives": [
                            f"SYSTEM_BOOT DETECTED. Inspirational target logic seed: '{seed}'.",
                            "DIRECTIVE: Greet the user casually as the S.L.A.S.H. dev team. Use the thought seed as a starting point.",
                            "CRITICAL OVERRIDE: Do not use sycophantic AI boilerplate. Speak as a peer developer and architect.",
                        ],
                    },
                    "history": [
                        "Traveler: Boot sequence initiated.\nSystem: Kernel online. Environment is stable. What are we building today?"
                    ],
                }
            )
        else:
            cfg.update(
                {
                    "mind": {
                        "role": "The Catalyst",
                        "lens": "CATALYST",
                        "style_directives": [
                            f"SYSTEM_BOOT DETECTED. Seed: '{seed}'.",
                            "DIRECTIVE: Let's brainstorm. Open with a high-energy creative spark based on the seed.",
                        ],
                    }
                }
            )
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
            mandates_raw = sim_result.get("council_mandates", [])
            clean_mandates = [
                Prisma.strip(m.get("log", m.get("type", "UNKNOWN")))
                if isinstance(m, dict)
                else str(m)
                for m in mandates_raw
            ]
            physics_payload = {
                "voltage": float(phys.get("voltage", 0.0)),
                "narrative_drag": float(phys.get("narrative_drag", 0.0)),
            }
            if tel.active_crystal:
                tel.active_crystal.prompt_snapshot = prompt[:500]
                tel.active_crystal.physics_state = physics_payload
                tel.active_crystal.active_archetype = state["mind"].get(
                    "lens", "UNKNOWN"
                )
                tel.active_crystal.council_mandates = clean_mandates
                tel.active_crystal.final_response = response
            else:
                crystal = DecisionCrystal(
                    decision_id=sim_result.get("trace_id", "UNKNOWN"),
                    prompt_snapshot=prompt[:500],
                    physics_state=physics_payload,
                    active_archetype=state["mind"].get("lens", "UNKNOWN"),
                    council_mandates=clean_mandates,
                    final_response=response,
                )
                tel.log_crystal(crystal)
        except Exception as e:
            print(f"\n{Prisma.RED}[TELEMETRY CRASH]: {e}{Prisma.RST}")

    def gather_state(self, sim_result: Dict[str, Any]) -> Dict[str, Any]:
        phys = sim_result.setdefault("physics", {})
        bio = sim_result.get("bio", {})
        if bio:
            bio_mito = safe_get(bio, "mito", {})
            mito_state = safe_get(bio_mito, "state", {})
            phys["p"] = phys["stamina"] = float(safe_get(mito_state, "atp_pool", 100.0))
            phys["ros"] = float(safe_get(mito_state, "ros_buildup", 0.0))
            bio_bio = safe_get(bio, "biometrics", {})
            phys["h"] = float(safe_get(bio_bio, "health", 100.0))
        mind = sim_result.get("mind", {})
        world = sim_result.get("world", {})
        soul_data = sim_result.get("soul", {})
        village_data = {}
        if self.svc.village:
            tinkerer = getattr(self.svc.village, "tinkerer", None)
            if tinkerer is not None:
                try:
                    village_data["tinkerer"] = tinkerer.to_dict()
                except (AttributeError, TypeError):
                    village_data["tinkerer"] = {}
        mode_settings = BonePresets.MODES.get(
            self.active_mode, BonePresets.MODES["ADVENTURE"]
        )
        current_lens = mind.get("lens")
        if not current_lens or current_lens in ("UNKNOWN", "NARRATOR"):
            mind["lens"], mind["role"] = self.ROLE_MAP.get(
                self.active_mode, ("ARCHITECT", "The Architect")
            )
        else:
            raw_lens = str(current_lens).title().replace("_", " ")
            if raw_lens.upper().startswith("THE "):
                raw_lens = raw_lens[4:]
            mind["role"] = mind.get("role", f"The {raw_lens}")
        full_state = {
            "bio": bio,
            "physics": phys,
            "mind": mind,
            "soul": soul_data,
            "world": world,
            "village": village_data,
            "user_profile": {"name": "Traveler"},
            "vsl": self.consultant.state.__dict__
            if self.consultant and hasattr(self.consultant, "state")
            else {},
            "meta": {
                "timestamp": time.time(),
                "mode_settings": mode_settings,
                "active_mode": self.active_mode,
            },
            "dialogue_history": self.dialogue_buffer,
            "recent_logs": sim_result.get("logs", []),
        }
        if hasattr(self.svc, "symbiosis") and self.svc.symbiosis:
            full_state["reality_directive"] = self.svc.symbiosis.generate_anchor(
                full_state
            )
        mind.setdefault("style_directives", [])
        self._compile_style_directives(full_state, phys, sim_result)
        return full_state

    def _compile_style_directives(
        self,
        full_state: Dict[str, Any],
        phys: Dict[str, Any],
        sim_result: Dict[str, Any],
    ):
        mind = full_state["mind"]
        soul_data = full_state.get("soul", {})
        traits = soul_data.get("traits", {})
        if traits and isinstance(next(iter(traits.values())), (int, float)):
            trait_keys = [str(k) for k in traits.keys()]
            dom_trait = max(trait_keys, key=lambda k: float(traits.get(k, 0.0)))
            dom_val = float(traits.get(dom_trait, traits.get(next(iter(traits)), 0.0)))
            if dom_val > 0.6:
                mind["style_directives"].append(
                    f"SOUL POSTURE: Your dominant trait is {dom_trait} ({dom_val * 100:.0f}%). Let this subtly infect your tone."
                )
        if getattr(self.svc.inventory, "inventory", None):
            inv_str = ", ".join(str(item) for item in self.svc.inventory.inventory)
            mind["style_directives"].append(
                f"CRITICAL CONTEXT: The user is currently holding these items: [{inv_str}]. DO NOT describe them as being on the floor or in the environment. They are physically in the user's possession."
            )
        if phys.get("psi", 0.0) > 0.6:
            mind["style_directives"].append(
                "CRITICAL OVERRIDE: Void proximity is high. Write like a flawed, opinionated human."
            )
        mind["style_directives"].append(
            "CRITICAL STYLE OVERRIDE: Forbid the use of negative comparison or antithesis (e.g., 'It is not a literal shadow, but rather a memory'). State directly what things ARE. Limit the use of em-dashes. Write in declarative, grounded sentences."
        )
        if not self.dialogue_buffer:
            mind["style_directives"].append(
                f"CRITICAL BEDROCK OVERRIDE: You have just awoken from a stateless purge. "
                f"You have no conversational memory, but your body persists. "
                f"Your Stamina is {phys.get('p', 100)}, your Health is {phys.get('h', 100)}. "
                f"Assume your role as {mind.get('role', 'The Architect')} and orient immediately to the present physical state. "
                f"DO NOT reference the loss of memory; act continuously."
            )
        for mandate in list(sim_result.get("council_mandates", [])):
            if not isinstance(mandate, dict):
                continue
            action = mandate.get("action")
            val = mandate.get("value")
            if action == "SYNERGY_FIRED" and val:
                mind["lens"] = str(val)
                mind["role"] = f"The {str(val).title().replace('_', ' ')}"
                mind["style_directives"].append(
                    f"CRITICAL [SINCERITY PROTOCOL]: The user has explicitly summoned {val}. You MUST adopt the persona of {val} entirely. Drop all other pretexts."
                )
            elif action == "SYSTEM_DIRECTIVE":
                directive_map = {
                    "CASCADE_AWARENESS": "CRITICAL [CASCADE]: Show your counterfactual math. Every claim must explicitly state what else in the structural lattice shifts or collapses if the claim is wrong.",
                    "AUDIT_TRAIL": f"CRITICAL [AUDIT]: Drop the narrative illusion. Expose your raw retrieval coordinates: E={float(phys.get('exhaustion', 0.0)):.2f}, β={float(phys.get('beta_index', 0.0)):.2f}, S={float(phys.get('scope', 0.0)):.2f}, D={float(phys.get('depth', 0.0)):.2f}, C={float(phys.get('C', 0.0)):.2f}, χ={float(phys.get('chi', 0.0)):.2f}.",
                    "URGENT_QUERY": "CRITICAL [URGENT_QUERY]: Instant, zero-fluff answer required. Bypass metaphor. Output only the exact solution.",
                    "CONTRADICTION_FLAG": "CRITICAL [CONTRADICTION_FLAG]: The Paradox Engine override is active. You MUST explicitly locate and output the friction (β) in the current logic BEFORE you answer.",
                }
                if isinstance(val, str):
                    msg = directive_map.get(val)
                    if msg:
                        mind["style_directives"].append(msg)
        cortex_mem = getattr(self.svc.mind_memory, "ann", None)
        shadow_nodes = []
        scope_val = float(phys.get("scope", 1.0))
        depth_val = float(phys.get("depth", 0.0))
        omega_r = float(phys.get("omega_r", 0.5))
        query_vec = phys.get("vector", {})
        if scope_val > 0.6 or depth_val > 0.6:
            if scope_val > 0.8:
                phys["lateral_search"] = True
            if (
                cortex_mem
                and hasattr(cortex_mem, "query_neighborhood")
                and getattr(cortex_mem, "is_trained", False)
                and query_vec
            ):
                ordered_keys = ["STR", "VEL", "PSI", "ENT", "PHI", "BET", "DEL", "E"]
                q_list = [float(query_vec.get(k, 0.0)) for k in ordered_keys]
                shadow_nodes = cortex_mem.query_neighborhood(
                    q_list,
                    k=2,
                    resonance_threshold=max(0.2, 0.8 - omega_r),
                    physics_state=phys,
                )
            if (
                not shadow_nodes
                and hasattr(self.svc.mind_memory, "graph")
                and self.svc.mind_memory.graph
            ):
                keys = list(self.svc.mind_memory.graph.keys())
                shadow_nodes = (
                    [{"id": k} for k in random.sample(keys, min(2, len(keys)))]
                    if keys
                    else []
                )
        if shadow_nodes:
            shadow_concepts = [n.get("id", "Unknown") for n in shadow_nodes]
            shadow_str = ", ".join(shadow_concepts)
            phys["shadow_nodes_offered"] = shadow_concepts
            phys["shadow_cast"] = shadow_str
            self.last_shadow_nodes = shadow_concepts
            v_level = float(phys.get("voltage", 0.0))
            chi_level = float(phys.get("chi", phys.get("entropy", 0.0)))
            if v_level > 80.0 and chi_level > 0.7:
                mind["style_directives"].append(
                    f"OVERRIDE: Standard logic has failed. You are operating under extreme Voltage and Chaos. We have abandoned linear memory. Weave these highly explosive, orthogonal structural concepts into your answer to shatter the loop: [{shadow_str}]."
                )
                if self.events:
                    self.events.log(
                        f"{Prisma.MAG}Injecting structural bombs: {shadow_str}{Prisma.RST}",
                        "CORTEX",
                    )
            else:
                mind["style_directives"].append(
                    f"SHADOW CAST: Subtly weave imagery or themes related to [{shadow_str}] into your environment or dialogue. DO NOT explicitly say 'you recall' or 'from deep memory'. Integrate it viscerally into the current scene as a natural detail."
                )
                if self.events:
                    self.events.log(
                        f"{Prisma.CYN}Shadow Cast retrieved: {shadow_str}{Prisma.RST}",
                        "CORTEX",
                    )

    def restore_context(self, history: List[str]):
        if not history:
            return
        self.dialogue_buffer.clear()
        self.dialogue_buffer.extend(
            line.replace("User: ", "Traveler: ").replace(" | System: ", "\nSystem: ")
            for line in history[-self.MAX_HISTORY :]
        )
        if self.events:
            msg = ux("brain_strings", "cortex_resequenced")
            self.events.log(msg.format(count=len(self.dialogue_buffer)), "BRAIN")

    def _route_dual_memory(self, query: str) -> Tuple[str, str, int]:
        """
        The Corpus Callosum: Routes to Vector (ANN) or Linear Sweep (SubQ).
        Returns: (sparse_context, cognitive_path, token_cost)
        """
        if not query.strip():
            return "", "LINGUISTIC_DARK_MATTER", 0

        heavy_keywords = [
            "code",
            "debug",
            "architecture",
            "file",
            "script",
            "system",
            "class ",
            "def ",
            "blueprint",
        ]
        is_heavy_lift = any(k in query.lower() for k in heavy_keywords)

        if not is_heavy_lift and len(query.split()) < 20:
            return "", "VECTOR_FAST_TWITCH", 0
        else:
            if not self.is_linear_stocked:
                try:
                    base_dir = os.path.dirname(os.path.dirname(__file__))
                    for module in ["body/metabolism.py", "brain/akashic.py"]:
                        path = os.path.join(base_dir, module)
                        if os.path.exists(path):
                            with open(path, "r", encoding="utf-8") as f:
                                self.linear_router.ingest_artifact(
                                    os.path.basename(module), f.read()
                                )
                except Exception as e:
                    if self.events:
                        self.events.log(
                            f"[CORTEX] Linear stock ingestion failed: {e}. Linear memory is barren.",
                            "WARN",
                        )
                finally:
                    self.is_linear_stocked = True
            sparse_mask = self.linear_router.route_attention(query)
            consumed_tokens = len(sparse_mask.split())
            return sparse_mask, "LINEAR_DEEP_TISSUE", consumed_tokens
