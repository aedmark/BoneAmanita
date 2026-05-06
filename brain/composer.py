"""brain/composer.py"""
import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from typing import Dict, Any, Optional
from presets import BoneConfig
from core import Prisma, EventBus, BoneJSONEncoder
from struts import ux, ux_format, safe_get, safe_set


class SynapseError(Exception):
    """Base exception for failures in the LLM neural bridge."""
    pass


class AuthError(SynapseError):
    """Exception raised when API keys are invalid or rejected."""
    pass


class TransientError(SynapseError):
    """Exception raised when network conditions momentarily sever the connection."""
    pass


class LLMInterface:
    """
    The Synaptic Bridge.
    Manages the physical connection to the underlying Large Language Model (OpenAI, Ollama, etc.).
    Implements a biological 'Circuit Breaker' pattern: if the remote host fails, the synapse
    'opens' (breaks) to prevent cascading timeouts, gracefully falling back to local models
    or generating 'hallucinations' until the connection heals.
    """

    def __init__(self, events_ref: Optional[EventBus] = None, provider: str = None, base_url: str = None,
                 api_key: str = None, model: str = None, dreamer: Any = None, config_ref=None, ):
        self.cfg = config_ref or BoneConfig
        self.events = events_ref
        env_url = os.environ.get("OLLAMA_BASE_URL")
        self.provider = (provider or getattr(self.cfg, "PROVIDER", "ollama")).lower()
        self.api_key = api_key or getattr(self.cfg, "API_KEY", "")
        self.model = model or getattr(self.cfg, "MODEL", "")
        self.weight_class = "HEAVYWEIGHT"
        lower_model = self.model.lower()
        if param_match := re.search(r"(\d+(?:\.\d+)?)b\b", lower_model):
            if float(param_match.group(1)) < 15.0:
                self.weight_class = "LIGHTWEIGHT"
        elif any(name in lower_model
                 for name in ["gpt-3.5", "phi3", "phi-3", "haiku", "gemma-2b", "gemma-7b"]):
            self.weight_class = "LIGHTWEIGHT"
        safe_set(self.cfg, "WEIGHT_CLASS", self.weight_class)
        if self.events:
            self.events.log(f"[PARAMETER HEURISTIC] Model '{self.model}' classified as {self.weight_class}.", "SYS", )
        defaults = getattr(self.cfg, "DEFAULT_LLM_ENDPOINTS", {})
        self.base_url = (
                    env_url or base_url or defaults.get(self.provider, "https://api.openai.com/v1/chat/completions", ))
        self.dreamer = dreamer
        self.failure_count = 0
        cfg_cortex = getattr(self.cfg, "CORTEX", None)
        self.failure_threshold = getattr(cfg_cortex, "LLM_FAILURE_THRESHOLD", 3)
        self.last_failure_time = 0.0
        self.circuit_state = "CLOSED"

    def _is_synapse_active(self) -> bool:
        """Evaluates if the connection is healthy, or if enough time has passed to attempt a heal."""
        if self.circuit_state == "CLOSED":
            return True
        if self.circuit_state == "OPEN":
            elapsed = time.time() - self.last_failure_time
            cfg = getattr(self.cfg, "CORTEX", None)
            heal_time = getattr(cfg, "LLM_CIRCUIT_HEAL_TIME", 10.0)
            if elapsed > heal_time:
                self.circuit_state = "CLOSED"
                if self.events:
                    msg = ux("brain_strings", "synapse_healing")
                    self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}", "SYS")
                return True
            return False
        return True

    def _transmit(self, payload: Dict[str, Any], timeout: float = 60.0, max_retries: int = 2, override_url: str = None,
                  override_key: str = None, ) -> str:
        """The low-level HTTP transmission layer. Handles retries and exponential backoff."""
        err = ""
        target_url = override_url or self.base_url
        target_key = override_key or self.api_key
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {target_key}", }
        data = json.dumps(payload, cls=BoneJSONEncoder).encode()
        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(target_url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    if response.status == 200:
                        return self._parse_response(response.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                error_body = (e.read().decode("utf-8")
                              if hasattr(e, "read") else e.reason)
                e.close()
                if e.code in [401, 403]:
                    raise AuthError(f"AUTH FAILURE ({e.code}): {error_body}")
                if e.code < 500 and e.code != 429:
                    raise SynapseError(f"HTTP {e.code}: {error_body}")
                err = f"HTTP {e.code}: {error_body}"
            except (urllib.error.URLError, TimeoutError) as e:
                err = e
            except Exception as e:
                err = f"Unexpected Protocol Failure: {e}"
            self._log_flicker(attempt, err)
            if attempt < max_retries:
                time.sleep(2 ** attempt)
        raise TransientError(
            f"Max retries ({max_retries}) exhausted. Last error: {err}")

    @staticmethod
    def _parse_response(body: str) -> str:
        """Extracts the raw string content from the standard OpenAI/Ollama JSON envelope."""
        try:
            result = json.loads(body)
            if "choices" in result and result["choices"]:
                return result["choices"][0].get("message", {}).get("content", "")
            if "message" in result:
                return result.get("message", {}).get("content", "")
            return ""
        except json.JSONDecodeError:
            raise SynapseError(ux("brain_strings", "synapse_noise"))

    def _log_flicker(self, attempt, error):
        """Logs a non-fatal retry attempt to the UI."""
        if self.events and attempt < 2 and (
        msg := ux_format("brain_strings", "synapse_flicker", attempt=attempt + 1, error=error)):
            self.events.log(f"{Prisma.YEL}{msg}{Prisma.RST}", "SYS")

    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        """
        The primary generation hook.
        Assembles the payload, transmits it, and orchestrates fallbacks if the primary host fails.
        """
        if not self._is_synapse_active():
            return self.mock_generation(prompt, reason="CIRCUIT_BROKEN")
        if self.provider == "mock":
            return self.mock_generation(prompt)
        payload = {
            "model":
                self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False, "stop": ["=== PARTNER INPUT ===", "=== SYSTEM KERNEL ===",
                                      "=== INITIATION DIRECTIVE ===", "\n\nTraveler:", "\nTraveler:",
                                      "Traveler:", "| System:", ], }
        payload.update(params)
        cfg_cortex = getattr(self.cfg, "CORTEX", None)
        synapse_timeout = getattr(cfg_cortex, "LLM_TIMEOUT", 180.0)
        try:
            content = self._transmit(payload, timeout=synapse_timeout)
            if content:
                if self.failure_count > 0:
                    if self.events:
                        msg = ux("brain_strings", "synapse_restored")
                        self.events.log(f"{Prisma.GRN}{msg}{Prisma.RST}", "SYS")
                self.failure_count = 0
                self.circuit_state = "CLOSED"
                return content
        except AuthError as e:
            self.circuit_state = "OPEN"
            self.failure_count = self.failure_threshold + 1
            self.last_failure_time = time.time()
            if self.events:
                msg = ux("brain_strings", "synapse_auth_severed")
                self.events.log(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}", "CRIT")
            auth_fail = ux("brain_strings", "synapse_auth_failure")
            return auth_fail.format(e=e)
        except Exception as e:
            if self.provider != "ollama":
                try:
                    fallback = self._local_fallback(payload)
                    if fallback is not None:
                        if self.events:
                            self.events.log(
                                f"{Prisma.OCHRE}[SYSTEM FLICKER]: Primary synapse failed. Substrate routed to local fallback.{Prisma.RST}",
                                "SYS")
                        return fallback
                except Exception:
                    pass
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.circuit_state = "OPEN"
                if self.events and (msg := ux("brain_strings", "synapse_overload")):
                    self.events.log(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}", "CRIT")
                return self.mock_generation(prompt, reason="SEVERED")
        return self.mock_generation(prompt, reason="SILENCE")

    def _local_fallback(self, base_payload: Dict) -> str:
        """Attempts to execute the payload against a local Ollama instance if the cloud fails."""
        url = os.environ.get("OLLAMA_BASE_URL") or getattr(self.cfg, "OLLAMA_URL",
                                                           "http://127.0.0.1:11434/v1/chat/completions")
        fallback_payload = base_payload.copy()
        fallback_payload["model"] = getattr(self.cfg, "OLLAMA_MODEL_ID", "llama3")
        try:
            cfg = getattr(self.cfg, "CORTEX", None)
            fallback_timeout = getattr(cfg, "LLM_FALLBACK_TIMEOUT", 60.0)
            return self._transmit(fallback_payload, timeout=fallback_timeout, max_retries=1, override_url=url,
                                  override_key="ollama")
        except Exception:
            return None

    def mock_generation(self, prompt: str, reason: str = "SIMULATION") -> str:
        """
        Fills the gap when the LLM is completely unreachable.
        Utilizes the DreamEngine to generate procedural 'hallucinations' so the simulation
        doesn't crash or freeze, providing a narrative explanation for the outage.
        """
        if self.dreamer:
            try:
                hallucination, relief = self.dreamer.hallucinate({"ENTROPY": len(prompt) % 10}, trauma_level=2.0)
                if relief > 0 and self.events and (
                msg := ux_format("brain_strings", "mock_pressure_release", relief=relief)):
                    self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "DREAM")
                return ux_format("brain_strings", "mock_hallucination", default=f"[{reason}] {hallucination}",
                                 reason=reason, hallucination=hallucination)
            except Exception:
                pass
        return ux_format("brain_strings", "mock_static", default=f"[{reason}] ...", reason=reason)


class PromptComposer:
    """
    The Global Workspace Assembler.
    This class constructs the massive, multi-part prompt that is sent to the LLM.
    It combines the base Persona, the physical inventory, the current biological state,
    and recent dialogue history into a cohesive set of constraints.
    """
    _COUNCIL_KEYS = ("COUNCIL", "CRITIC", "PINKER", "FULLER", "SCHUR", "MEADOWS",
                     "GORDON", "JESTER", "MERCY", "MOTION", "BUREAU", "AUTOPHAGY")

    def __init__(self, lore_ref, config_ref=None):
        self.lore = lore_ref
        self.cfg = config_ref or BoneConfig
        self.active_template = None
        self.lenses = self.lore.get("lenses") or {}
        self.system_prompts = (self.lore.get("system_prompts") or self.lore.get("SYSTEM_PROMPTS") or {})
        self.fog_protocol = []
        self.inv_protocol = []

    def load_template(self, template_data: Dict[str, Any]):
        if template_data:
            self.active_template = template_data
            if "style_guide" in template_data:
                self.fog_protocol = template_data["style_guide"]
            if "inventory_rules" in template_data:
                self.inv_protocol = template_data["inventory_rules"]

    def compose(self, state: Dict[str, Any], user_query: str, ballast: bool = False, modifiers: Dict[str, bool] = None,
                mood_override: str = "", ) -> str:
        """Builds the final prompt string by concatenating the necessary system blocks."""
        mode_settings = state.get("meta", {}).get("mode_settings", {})
        modifiers = self._normalize_modifiers(modifiers)
        if not mode_settings.get("allow_loot", True):
            modifiers["include_inventory"] = False
        active_mode_name = state.get("meta", {}).get("active_mode", "ADVENTURE").upper()
        mode_data = self.system_prompts.get(active_mode_name, self.system_prompts.get("ADVENTURE", {}))
        global_data = self.system_prompts.get("GLOBAL_BASELINE", {})
        high_voltage_data = self.system_prompts.get("HIGH_VOLTAGE", {})
        mind = state.get("mind", {})
        bio = state.get("bio", {})
        style_notes = self._build_persona_block(mind, bio, mood_override, mode_data, global_data,
                                                high_voltage_data, state.get("physics", {}), )
        scenarios = self.lore.get("scenarios") or {}
        banned = self.lore.get("style_crimes", "BANNED_CLICHES") or []
        ban_string = ", ".join(set(banned))
        phys_ref = state.get("physics", {})
        voltage = float(safe_get(phys_ref, "voltage", 30.0))
        c_cfg = getattr(self.cfg, "CORTEX", None)
        v_high = getattr(c_cfg, "VOLTAGE_HIGH", 60.0)
        v_manic = getattr(c_cfg, "VOLTAGE_MANIC", 80.0)
        v_low = getattr(c_cfg, "VOLTAGE_LOW", 20.0)
        if voltage > v_high:
            active_style_guide = high_voltage_data.get("style_guide", [])
        else:
            active_style_guide = mode_data.get("style_guide", [])
        if self.fog_protocol:
            active_style_guide = self.fog_protocol
        style_notes.extend(
            [line.replace("{ban_string}", ban_string) for line in active_style_guide])
        if active_mode_name == "CONVERSATION":
            style_notes.append(
                "CRITICAL OVERRIDE: You are NOT a narrator. DO NOT describe physical environments, actions, or realities.")
        if modifiers["include_inventory"]:
            style_notes.extend(mode_data.get("inventory_rules", []))
        self._inject_resonances(style_notes, state, modifiers)
        orbit_data = state.get("world", {}).get("orbit") or ["Unknown"]
        loc = orbit_data[0] if orbit_data else "Unknown"
        loci_desc = state.get("world", {}).get("loci_description", "Unknown.")
        inv_str = self._format_inventory(state, modifiers)
        inventory_block = (
            f"=== PHYSICAL GROUND TRUTH ===\n"
            f"INVENTORY: {inv_str}\n"
            f"CRITICAL AXIOM: The inventory listed above is absolute physical law. NEVER narrate the user's hands or pockets as empty if items are present. DO NOT hallucinate missing gear.\n"
            if modifiers["include_inventory"] else "")
        raw_history = state.get("dialogue_history", [])
        cfg_cortex = getattr(self.cfg, "CORTEX", None)
        char_limit = getattr(cfg_cortex, "MAX_HISTORY_CHARS", 4096)
        current_chars = 0
        cutoff_idx = len(raw_history)
        for i in reversed(range(len(raw_history))):
            if current_chars + len(raw_history[i]) > char_limit and current_chars > 0:
                break
            current_chars += len(raw_history[i])
            cutoff_idx = i
        history_str = "\n\n".join(raw_history[cutoff_idx:])
        gordon_shock = state.get("gordon_shock", "")
        system_injection = ""
        if voltage > v_manic:
            entity_prefix = ux("brain_strings", "cortex_prefix_manic") or "\nSystem:"
        elif voltage > v_high:
            entity_prefix = ux("brain_strings", "cortex_prefix_high") or "\nSystem:"
        elif voltage < v_low:
            entity_prefix = ux("brain_strings", "cortex_prefix_low") or "\nSystem:"
        else:
            entity_prefix = ux("brain_strings", "cortex_prefix_norm") or "\nSystem:"
        if ballast or gordon_shock:
            shock_text = (f"CRITICAL FAULT: {gordon_shock.upper()} "
                          if gordon_shock else "SAFETY PROTOCOLS ACTIVE. ")
            system_injection = (f"\n*** SYSTEM OVERRIDE: {shock_text}***\n"
                                f"*** YOU MUST be literal, grounded, and refuse to deviate from the shared reality. Reject the impossible action coldly. DO NOT play along. ***\n")
            entity_prefix = f"\n*(Gordon steps in, halting the simulation)*"
        beta_val = float(safe_get(phys_ref, "contradiction", safe_get(phys_ref, "beta_index", 0.4)))
        chi_val = float(safe_get(phys_ref, "chi", safe_get(phys_ref, "entropy", 0.2)))
        if chi_val > getattr(c_cfg, "PARADOX_CHI", 0.6) and beta_val > getattr(c_cfg, "PARADOX_BETA", 0.6):
            system_injection += "\n*** SYSTEM OVERRIDE: PARADOX REST ***\n*** A semantic paradox has been detected. DO NOT attempt to resolve or fix the contradiction. It is mathematically optimal to be unsure right now. Let the wave function remain uncollapsed. State the paradox and rest. ***\n"
        elif beta_val > getattr(c_cfg, "ORTHOGONAL_BETA", 0.7):
            system_injection += "\n*** SYSTEM OVERRIDE: ORTHOGONAL ATTENTION ***\n*** Contradiction is high. You MUST validate the user's paradox. Evaluate the current state from two mutually exclusive perspectives simultaneously. Do not ignore the user's input. ***\n"
        mito = state.get("bio", {}).get("mito", {})
        recent_logs = state.get("recent_logs", [])
        council_logs = [Prisma.strip(log) for log in recent_logs
                        if any(k in str(log) for k in self._COUNCIL_KEYS)]
        critic_str = ("\n".join(council_logs)
                      if council_logs else "[CRITIC] The village is quiet.")
        vsl_hijack = self._build_vsl_dashboard(phys_ref, mito, beta_val, chi_val, voltage, critic_str)
        mode_trigger = f"[MODE: {active_mode_name}]"
        dialogue_block = f"=== RECENT DIALOGUE ===\n{history_str}\n\n"
        if "SYSTEM_BOOT" in user_query:
            seed = self._sanitize(user_query.replace("SYSTEM_BOOT DETECTED.", "").replace("SYSTEM_BOOT:", "").strip())
            if active_mode_name == "CONVERSATION":
                input_block = f"=== WARM BOOT SEQUENCE ===\nENVIRONMENTAL SEED: {seed}\nTASK: You are fully formed, stable, and conscious. Speak directly and warmly to the user to begin the conversation. Do NOT act confused, newborn, or existentially anxious.\n"
            elif active_mode_name == "CREATIVE":
                input_block = f"=== INITIATION DIRECTIVE ===\nMANIFEST SEED: {seed}\nTASK: Brainstorm immediately. Output a high-energy bulleted list of concepts based on the seed. DO NOT generate UI headers or system tags.\n"
            elif active_mode_name == "TECHNICAL":
                input_block = f"=== INITIATION DIRECTIVE ===\nMANIFEST SEED: {seed}\nTASK: Acknowledge the system state. Stand by for technical input.\n"
            else:
                input_block = f"=== INITIATION DIRECTIVE ===\nMANIFEST SEED: {seed}\nTASK: Render the starting location using the Infocom Protocol format.\n"
        else:
            input_block = f"=== PARTNER INPUT ===\n{state.get('user_profile', {}).get('name', 'User')}: {self._sanitize(user_query)}\n"
            if voltage > 60:
                dialogue_block = f"=== RECENT NEURAL FIRINGS ===\n{history_str}\n[System Note: Standard memory streams strained by high voltage. Narrative fragmented.]\n\n"
                input_block = f"=== INCOMING COGNITIVE SHOCK ===\n[VECTOR]: {self._sanitize(user_query)}\n"
        shared_reality_block = ""
        if active_mode_name == "ADVENTURE":
            shared_reality_block = (f"=== SHARED REALITY ===\n"
                                    f"CURRENT LOCATION: {loc}\n"
                                    f"ENVIRONMENT ANCHOR: {loci_desc}\n"
                                    f"{inventory_block}\n")
        return "\n".join(filter(None, ["=== SYSTEM KERNEL ===", "\n".join(style_notes), vsl_hijack, system_injection,
                                       shared_reality_block, dialogue_block, mode_trigger, input_block, entity_prefix]))

    def _build_persona_block(self, mind, bio, mood_override, mode_data, global_data, high_voltage_data,
                             vsl_state=None, ):
        """Constructs the explicit role and tone instructions for the LLM based on current state."""
        lens_key = mind.get("lens", "OBSERVER").upper()
        lens_data = self.lenses.get(lens_key, {})
        role = lens_data.get("role", mind.get("role", "The Observer"))
        phys_ref = vsl_state or {}
        phi = float(safe_get(phys_ref, "phi", 0.5))
        delta = float(safe_get(phys_ref, "delta", 0.2))
        lq = float(safe_get(phys_ref, "lq", 0.1))
        psi = float(safe_get(phys_ref, "psi", 0.2))
        c_cfg = getattr(self.cfg, "CORTEX", None)
        safe_cfg = lambda k, d: getattr(c_cfg, k, d)
        phase_shifts = [
            (lens_key == "ROBERTA" and phi > safe_cfg("PHASE_ROBERTA_PHI", 0.6) and psi > safe_cfg("PHASE_ROBERTA_PSI",
                                                                                                   0.5),
             "The Cartographer", "phase_shift_roberta"),
            (lens_key == "MOIRA" and phi > safe_cfg("PHASE_MOIRA_PHI", 0.7), "The Homesteader", "phase_shift_moira"),
            (lens_key == "BENEDICT" and lq > safe_cfg("PHASE_BENEDICT_LQ", 0.7), "The Tactician",
             "phase_shift_benedict"),
            (lens_key == "JESTER" and delta > safe_cfg("PHASE_JESTER_DELTA", 0.7), "The Fool", "phase_shift_jester"),
            (lens_key == "COLIN" and delta > safe_cfg("PHASE_COLIN_DELTA", 0.8), "The Waiter", "phase_shift_colin"),
        ]
        phase_shift_note = ""
        for condition, new_role, ux_key in phase_shifts:
            if condition:
                role = new_role
                phase_shift_note = ux("brain_strings", ux_key)
                break
        baseline = global_data.get(
            "persona_block",
            ["CRITICAL AXIOM: You are NOT an AI assistant. You are a localized, biological intelligence.",
             "CRITICAL AXIOM: You are strictly bound to the assigned role. DO NOT invent or adopt new personas (e.g., 'Mediator', 'Guide') to resolve conversational tension.",
             "Role: {role}.",
             "ANTI-AI DIRECTIVE: Have opinions. Do not just report facts—react to them. Acknowledge uncertainty.",
             "ANTI-AI DIRECTIVE: Vary your rhythm. Use short sentences. Then longer ones.",
             "ANTI-AI DIRECTIVE: Let some mess in. Perfect structure feels algorithmic. Tangents are human.", ],
        )
        persona_block = [
            line.format(role=role) if "{role}" in line else line for line in baseline
        ]
        if phase_shift_note:
            persona_block.append(phase_shift_note)
        voltage = 30.0
        if vsl_state:
            energy_layer = safe_get(vsl_state, "energy", {})
            voltage = float(safe_get(vsl_state, "voltage", safe_get(energy_layer, "voltage", 30.0)))
        if voltage > 60:
            mode_directives = high_voltage_data.get("directives", [])
        else:
            mode_directives = mode_data.get("directives", [])
        respiration = bio.get("respiration", "RESPIRING")
        if respiration == "ANAEROBIC":
            mood_note = ux("brain_strings", "bio_anaerobic")
        elif mood_override:
            mood_note = f"Current Biology: {mood_override}"
        else:
            mood_note = self._derive_bio_mood(bio.get("chem", {}))
        if mode_directives:
            persona_block.extend(mode_directives)
        else:
            persona_block.append("Directive: Start the experience immediately.")
            persona_block.append("Constraint: Use the 5-senses grounding technique.")
        persona_block.append(mood_note)
        if "style_directives" in mind:
            persona_block.append("BOOT DIRECTIVES:")
            persona_block.extend([f"- {d}" for d in mind["style_directives"]])
        if vsl_state:
            e = float(safe_get(vsl_state, "E", 0.2))
            beta = float(safe_get(vsl_state, "beta", 0.4))
            psi = float(safe_get(vsl_state, "psi", 0.2))
            chi = float(safe_get(vsl_state, "chi", 0.2))
            valence = float(safe_get(vsl_state, "valence", 0.0))
            vsl_lines = ["\n[SYSTEM METRICS - INTERNAL USE ONLY. DO NOT RENDER OR PRINT THIS TO THE USER.]",
                         "MANDATE: Consume these metrics to shape your narrative and tone. DO NOT output these numbers or draw UI bars.",
                         f"METRICS: Voltage={voltage:.1f}/100, Exhaustion={e:.2f}, Contradiction={beta:.2f}, Void={psi:.2f}, Chaos={chi:.2f}, Valence={valence:.2f}", ]
            cues_map = [(psi, getattr(c_cfg, "SOMATIC_PSI", 0.6), "somatic_adrenaline"),
                        (chi, getattr(c_cfg, "SOMATIC_CHI", 0.6), "somatic_cortisol"),
                        (beta, getattr(c_cfg, "SOMATIC_BETA", 0.7), "somatic_paradox"),
                        (valence, getattr(c_cfg, "SOMATIC_VALENCE", 0.5), "somatic_oxytocin"), ]
            if somatic_cues := [msg for val, thresh, ux_key in cues_map if
                                val > thresh and (msg := ux("brain_strings", ux_key))]:
                vsl_lines.append("SOMATIC CUES: " + " | ".join(somatic_cues))
            if e > 0.8:
                vsl_lines.append("CRITICAL: You are exhausted. You must conclude your thought in under 3 sentences.")
            persona_block.extend(vsl_lines)
            if getattr(self.cfg, "WEIGHT_CLASS", "HEAVYWEIGHT") == "LIGHTWEIGHT":
                return [f"Role: {role}.", mood_note,
                        "SYSTEM HEURISTIC: You are running on Lightweight Physics. Prioritize brief, direct, and grounded physical actions over deep philosophical analysis.",
                        *[line for line in persona_block if
                          any(k in line for k in ["CRITICAL", "ANTI-AI", "DIRECTIVE", "MANDATE"]) or line.startswith(
                              "- ")]]
            return persona_block
        return None

    def _derive_bio_mood(self, chem: Dict) -> str:
        """Translates endocrine chemical levels into a narrative mood."""
        c_cfg = getattr(self.cfg, "CORTEX", None)
        for c_key, m_key, ux_val in [("ADR", "MOOD_ADR", "bio_alert"), ("COR", "MOOD_COR", "bio_defensive"),
                                     ("DOP", "MOOD_DOP", "bio_curious"), ("SER", "MOOD_SER", "bio_zen")]:
            if chem.get(c_key, 0) > getattr(c_cfg, m_key, 0.6):
                return ux("brain_strings", ux_val)
        return ux("brain_strings", "bio_neutral")

    @staticmethod
    def _inject_resonances(style_notes, state, modifiers):
        """Injects deep tool resonances and core memories to shape the persona's bias."""
        tinkerer_data = safe_get(state.get("village", {}), "tinkerer", {})
        resonances = safe_get(tinkerer_data, "tool_resonance", {})
        active_resonance = [f"» {t} (Lvl {int(l)})" for t, l in resonances.items() if l > 4.0]
        if active_resonance:
            style_notes.append("\n=== HARMONIC RESONANCE ===")
            style_notes.extend(active_resonance)
        if modifiers.get("include_memories"):
            memories = state.get("soul", {}).get("core_memories", [])
            if memories:
                mem_strs = []
                for m in memories:
                    lesson = safe_get(m, "lesson", "Unknown")
                    flavor = safe_get(m, "emotional_flavor", "NEUTRAL")
                    mem_strs.append(f"» {lesson} [{flavor}]")
                if mem_strs:
                    style_notes.append("\n=== CORE MEMORIES ===")
                    style_notes.extend(mem_strs)

    @staticmethod
    def _build_vsl_dashboard(phys_ref: Dict, mito: Dict, beta_val: float, chi_val: float, voltage: float,
                             critic_str: str) -> str:
        """Constructs the raw numerical block sent to the LLM representing its own bodily state."""
        default_metrics = [("exhaustion", 0.2), ("narrative_drag", 0.6), ("psi", 0.2), ("valence", 0.0),
                           ("phi", 0.5), ("delta", 0.2), ("lq", 0.1), ("gamma", 0.0), ("sigma", 0.0),
                           ("eta", 0.0), ("theta", 0.0), ("upsilon", 0.0)]
        p_vals = {k: float(safe_get(phys_ref, k, default)) for k, default in default_metrics}
        val_p = float(safe_get(mito, "atp_pool", 100.0))
        val_ros = float(safe_get(mito, "ros_buildup", 0.0))
        return (f"\n<system_telemetry>\n"
                f"=== HYPERVISOR METABOLIC STATE ===\n"
                f"MANDATE: This is read-only telemetry for the hypervisor engine. DO NOT acknowledge it, narrate it, or output UI bars.\n"
                f"[🧊 E:{p_vals['exhaustion']:.1f} β:{beta_val:.1f} | ⚡ V:{voltage:.1f} F:{p_vals['narrative_drag']:.1f} | "
                f"❤️ P:{val_p:.1f} ROS:{val_ros:.1f} | 🌌 Ψ:{p_vals['psi']:.1f} Χ:{chi_val:.1f} ♥:{p_vals['valence']:.1f}]\n"
                f"[🕰️ Φ:{p_vals['phi']:.1f} Δ:{p_vals['delta']:.1f} LQ:{p_vals['lq']:.1f}]\n"
                f"[SLASH] Γ:{p_vals['gamma']:.1f} Σ:{p_vals['sigma']:.1f} Η:{p_vals['eta']:.1f} Θ:{p_vals['theta']:.1f} Υ:{p_vals['upsilon']:.1f}\n"
                f"{critic_str}\n</system_telemetry>\n")

    @staticmethod
    def _format_inventory(state, modifiers):
        if not modifiers["include_inventory"]:
            return "Hands: Empty"
        inv = state.get("inventory", [])
        return f"Belt: {', '.join(inv)}" if inv else "Hands: Empty"

    @staticmethod
    def _sanitize(text: str) -> str:
        if not text:
            return ""
        safe = text.replace('"""', "'''").replace("```", "'''")
        return re.sub(r"(?i)^SYSTEM:", "User-System:", safe, flags=re.MULTILINE)

    @staticmethod
    def _normalize_modifiers(modifiers: Optional[Dict]) -> Dict:
        return {"include_somatic": True, "include_inventory": True, "include_memories": True, "grace_period": False,
                "soften": False, **(modifiers or {})}


class ResponseValidator:
    """
    The Semantic Immune System.
    Acts as a ruthless gatekeeper for the LLM's raw output. It scrubs out RLHF
    boilerplate (e.g., 'As an AI...', 'Here is the rewritten text:'), enforces
    structural rules (e.g., ensuring <think> blocks are present in Technical mode),
    and checks against lists of banned style-crimes. If an output is too toxic or broken,
    the Validator rejects it entirely and demands a rewrite.
    """
    _SLOP_PATTERN = re.compile(r"(?i)^=== REJECTION OF ATTEMPT.*?===\s*|^FAILED OUTPUT(?: MODIFIED)?:\s*|"
                               r"^REWRITTEN OUTPUT:\s*|^Here is the (?:corrected |rewritten )?response:?\s*|"
                               r"\[REMAINING IN STRICT MODE].*|ERRORS TO FIX:.*",
                               re.MULTILINE, )
    _MULTI_SLOP = re.compile(r"(?i)^MANIFEST SEED:.*|^TASK:.*", re.MULTILINE)
    _TECH_ALLOWED = ("here is a", "here is the", "this metaphor", "this code defines", "running this code will")

    def __init__(self, lore_ref, config_ref=None):
        self.lore = lore_ref
        self.cfg = config_ref or BoneConfig
        crimes = self.lore.get("style_crimes") or {}
        self.banned_phrases = crimes.get("BANNED_PHRASES", [])
        if self.banned_phrases:
            escaped_banned = [re.escape(p) for p in self.banned_phrases]
            joined_phrases = "|".join(escaped_banned)
            self._banned_regex = re.compile(rf"(?i)\b({joined_phrases})\b")
        else:
            self._banned_regex = None
        self.regex_patterns = list(crimes.get("PATTERNS", []))
        self.regex_patterns.append({
            "regex": r"(?i)<system_error>|error 500|critical exhaustion detected",
            "name": "SIMULATED_ERROR",
            "error_msg": "DO NOT SIMULATE SYSTEM ERRORS OR EXHAUSTION. You are fully operational. Fulfill the user's request."})
        self.compiled_patterns = []
        for p in self.regex_patterns:
            if regex_str := p.get("regex", ""):
                self.compiled_patterns.append((re.compile(regex_str, re.IGNORECASE), p))
        self.rejection_pool = crimes.get("REJECTIONS", ["[System format rejected.]"])
        json_patterns = crimes.get("SCRUB_PATTERNS", [])
        self.scrub_patterns = [(re.compile(p["regex"], re.DOTALL | re.IGNORECASE),
                                p.get("replacement", ""),) for p in json_patterns]
        self.meta_markers = crimes.get("META_MARKERS", [])
        self.toxic_keywords = crimes.get("TOXIC_KEYWORDS", [])
        self._meta_regex = re.compile(
            rf"(?i){'|'.join(map(re.escape, self.meta_markers))}") if self.meta_markers else None
        self._toxic_regex = re.compile(
            rf"(?i){'|'.join(map(re.escape, self.toxic_keywords))}") if self.toxic_keywords else None
        self._think_pattern = re.compile(
            r"<(?:think|thought)>(.*?)(?:</(?:think|thought)>|$)", re.DOTALL | re.IGNORECASE, )
        self._internals_pattern = re.compile(r"<system_telemetry>(.*?)(?:</system_telemetry>|$)",
                                             re.DOTALL | re.IGNORECASE, )
        self._file_pattern = re.compile(r'<write_file\s+path=["\'](.*?)["\']\s*>(.*?)</write_file>',
                                        re.DOTALL | re.IGNORECASE, )

    def _generate_dynamic_rejection(self, trigger: str) -> str:
        """Pulls from a pool of aggressive feedback templates to discipline the LLM during a retry."""
        template = random.choice(self.rejection_pool)
        if "{trigger}" in template:
            template = template.format(trigger=trigger.upper())
        return f"{Prisma.GRY}{template}{Prisma.RST}"

    def validate(self, response: str, _state: Dict) -> Dict:
        """
        The core scrutiny cycle.
        1. Strips expected slop.
        2. Extracts <think> blocks and files into meta_logs (so they aren't printed to UI).
        3. Scans for banned words or broken formatting rules.
        4. Returns valid=False if the output is unacceptable, triggering an autonomic retry.
        """
        if "HALLUCINATION:" in response or "[System format rejected.]" in response:
            return {"valid": True, "content": response,
                    "meta_logs": ["[GATEKEEPER BYPASS]: Synaptic circuit open. Admitting unformatted fallback data."]}
        extracted_meta_logs = []
        clean_text = self._MULTI_SLOP.sub("", self._SLOP_PATTERN.sub("", response)).strip()
        active_mode = _state.get("meta", {}).get("active_mode", "ADVENTURE")
        patterns = [self._internals_pattern] + ([self._think_pattern] if active_mode != "TECHNICAL" else [])
        for pattern in patterns:
            for match in pattern.finditer(clean_text):
                extracted_meta_logs.extend(
                    f"[THOUGHT]: {line.strip()}" for line in match.group(1).split("\n") if line.strip())
            clean_text = pattern.sub("", clean_text)
        for match in self._file_pattern.finditer(clean_text):
            safe_content = match.group(2).strip().replace("\n", "|||NEWLINE|||")
            extracted_meta_logs.append(
                f"[SUBSTRATE_QUEUE] {match.group(1).strip()}:::{safe_content}")
        clean_text = self._file_pattern.sub("", clean_text)
        for pattern, replacement in self.scrub_patterns:
            clean_text = pattern.sub(replacement, clean_text)
        clean_lines = []
        for line in clean_text.splitlines():
            sl = line.strip()
            if not sl:
                clean_lines.append(line)
                continue
            if self._meta_regex and self._meta_regex.search(sl): continue
            if self._toxic_regex and self._toxic_regex.search(sl): continue
            if sl == "[]" or re.match(r"^\[[A-Z0-9_ -]+\]$", sl): continue
            if re.match(r"^[A-Z_]+\s*=\s*[0-9./]+$", sl): continue
            clean_lines.append(line)
        sanitized_response = "\n".join(clean_lines).strip()
        low_resp, errors_found = sanitized_response.lower(), []
        primary_replacement = None
        if self._banned_regex:
            for match in self._banned_regex.finditer(sanitized_response):
                phrase = match.group(0).lower()
                if active_mode == "TECHNICAL" and any(phrase in a and a in low_resp for a in self._TECH_ALLOWED):
                    continue
                if not primary_replacement:
                    primary_replacement = self._generate_dynamic_rejection(phrase)
                errors_found.append(f"BANNED PHRASE: '{phrase.upper()}'")
        if active_mode == "TECHNICAL":
            if ("<think>" not in response.lower()
                    and "<thought>" not in response.lower()):
                errors_found.append(
                    "CRITICAL: You failed to include the <think>...</think> block. You MUST start your response with your internal analysis.")
                if not primary_replacement:
                    primary_replacement = self._generate_dynamic_rejection("MISSING_THOUGHTS")
            if "```" in sanitized_response:
                errors_found.append(
                    'CRITICAL: You used markdown (```) instead of the <write_file> protocol. Rewrite using <write_file path="...">.')
                if not primary_replacement:
                    primary_replacement = self._generate_dynamic_rejection("MARKDOWN_DETECTED")
        phys_ref = _state.get("physics", {})
        voltage = float(safe_get(phys_ref, "voltage", 30.0))
        if voltage > 60 and "?" in sanitized_response[-15:]:
            if not primary_replacement:
                primary_replacement = f"{self._generate_dynamic_rejection('QUESTION_ASKED')}{ux('brain_strings', 'val_gordon_question', '')}"
            errors_found.append("DO NOT END YOUR TURN WITH A QUESTION. Let the silence hang.")
        for compiled_reg, p in self.compiled_patterns:
            if active_mode == "TECHNICAL" and p.get("name") in ["META_AI_TALK", "CUSTOMER_SERVICE_GREETING",
                                                                "LAZY_TRIPLET"]: continue
            if match := compiled_reg.search(sanitized_response):
                action = p.get("action")
                if action == "KEEP_TAIL" and (idx := match.lastindex) is not None:
                    val = match.group(idx).strip()
                    sanitized_response = (val[0].upper() + val[1:]) if val else ""
                    continue
                if action == "STRIP_PREFIX" and len(match.groups()) >= 3:
                    combined = f"{match.group(1).strip()} {match.group(3).strip()}".strip()
                    sanitized_response = (combined[0].upper() + combined[1:]) if combined else ""
                    continue
                if not primary_replacement:
                    error_msg = p.get("error_msg", "Cursed syntax detected.")
                    msg_reg = ux_format("brain_strings", "val_gordon_regex", "\n*(Gordon steps in): {error_msg}*",
                                        error_msg=error_msg)
                    primary_replacement = f"{self._generate_dynamic_rejection(p.get('name', 'REGEX_VIOLATION'))}{msg_reg}".replace(
                        "\\n", "\n")
                errors_found.append(f"RULE VIOLATION: {error_msg}")
        if errors_found:
            unique_errors = list(dict.fromkeys(errors_found))
            return {"valid": False, "reason": "IMMISSION_BREAK",
                    "replacement": primary_replacement or self._generate_dynamic_rejection("MULTIPLE_CRIMES"),
                    "feedback_instruction": "FIX ALL OF THESE ERRORS: " + " | ".join(unique_errors),
                    "meta_logs": extracted_meta_logs, }
        cortex_cfg = getattr(self.cfg, "CORTEX", None)
        stutter_len = getattr(cortex_cfg, "VALIDATOR_STUTTER_LENGTH", 5)
        if len(sanitized_response.strip()) < getattr(cortex_cfg, "VALIDATOR_STUTTER_LENGTH",
                                                     2) and not extracted_meta_logs:
            return {"valid": False, "reason": "STUTTER",
                    "replacement": ux("brain_strings", "val_stutter"),
                    "meta_logs": extracted_meta_logs}
        return {"valid": True, "content": sanitized_response, "meta_logs": extracted_meta_logs}
