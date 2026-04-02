"""bone_composer.py"""

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Dict, Any, Optional

from bone_presets import BoneConfig
from bone_core import Prisma, EventBus, ux, BoneJSONEncoder, safe_get, safe_set


class SynapseError(Exception):
    pass


class AuthError(SynapseError):
    pass


class TransientError(SynapseError):
    pass


class LLMInterface:
    def __init__(
        self,
        events_ref: Optional[EventBus] = None,
        provider: str = None,
        base_url: str = None,
        api_key: str = None,
        model: str = None,
        dreamer: Any = None,
        config_ref=None,
    ):
        self.cfg = config_ref or BoneConfig
        self.events = events_ref
        env_url = os.environ.get("OLLAMA_BASE_URL")
        self.provider = (provider or getattr(self.cfg, "PROVIDER", "ollama")).lower()
        self.api_key = api_key or getattr(self.cfg, "API_KEY", "")
        self.model = model or getattr(self.cfg, "MODEL", "")
        defaults = getattr(self.cfg, "DEFAULT_LLM_ENDPOINTS", {})
        self.base_url = (
            env_url
            or base_url
            or defaults.get(
                self.provider,
                "https://api.openai.com/v1/chat/completions",
            )
        )
        self.dreamer = dreamer
        self.failure_count = 0
        cfg_cortex = getattr(self.cfg, "CORTEX", None)
        self.failure_threshold = (
            getattr(cfg_cortex, "LLM_FAILURE_THRESHOLD", 3) if cfg_cortex else 3
        )
        self.last_failure_time = 0.0
        self.circuit_state = "CLOSED"

    def _is_synapse_active(self) -> bool:
        if self.circuit_state == "CLOSED":
            return True
        if self.circuit_state == "OPEN":
            elapsed = time.time() - self.last_failure_time
            cfg = getattr(self.cfg, "CORTEX", None)
            heal_time = getattr(cfg, "LLM_CIRCUIT_HEAL_TIME", 10.0) if cfg else 10.0
            if elapsed > heal_time:
                self.circuit_state = "HALF_OPEN"
                if self.events:
                    msg = ux("brain_strings", "synapse_healing")
                    self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}", "SYS")
                return True
            return False
        return True

    def _transmit(
        self,
        payload: Dict[str, Any],
        timeout: float = 60.0,
        max_retries: int = 2,
        override_url: str = None,
        override_key: str = None,
    ) -> str:
        err = ""
        target_url = override_url or self.base_url
        target_key = override_key or self.api_key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {target_key}",
        }
        data = json.dumps(payload, cls=BoneJSONEncoder).encode()
        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(target_url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    if response.status == 200:
                        return self._parse_response(response.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                error_body = (
                    e.read().decode("utf-8") if hasattr(e, "read") else e.reason
                )
                e.close()
                if e.code in [401, 403]:
                    raise AuthError(f"AUTH FAILURE ({e.code}): {error_body}")
                if e.code < 500 and e.code != 429:
                    raise SynapseError(f"HTTP {e.code}: {error_body}")
                err = f"HTTP {e.code}: {error_body}"
            except (urllib.error.URLError, TimeoutError) as e:
                err = e
            except Exception as e:
                raise SynapseError(f"Unexpected Protocol Failure: {e}")
            self._log_flicker(attempt, err)
            time.sleep(2**attempt)
        raise TransientError(
            f"Max retries ({max_retries}) exhausted. Last error: {err}"
        )

    @staticmethod
    def _parse_response(body: str) -> str:
        try:
            result = json.loads(body)
            if "choices" in result:
                return result["choices"][0].get("message", {}).get("content", "")
            return ""
        except json.JSONDecodeError:
            raise SynapseError(ux("brain_strings", "synapse_noise"))

    def _log_flicker(self, attempt, error):
        if self.events and attempt < 2:
            msg = ux("brain_strings", "synapse_flicker")
            self.events.log(
                f"{Prisma.YEL}{msg.format(attempt=attempt + 1, error=error)}{Prisma.RST}",
                "SYS",
            )

    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        if prompt.strip().lower() == "//reset system":
            self.failure_count = 0
            self.circuit_state = "CLOSED"
            return ux("brain_strings", "synapse_reset")
        if not self._is_synapse_active():
            return self.mock_generation(prompt, reason="CIRCUIT_BROKEN")
        if self.provider == "mock":
            return self.mock_generation(prompt)
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "stop": [
                "=== PARTNER INPUT ===",
                "=== SYSTEM KERNEL ===",
                "=== INITIATION DIRECTIVE ===",
                "\n\nTraveler:",
                "\nTraveler:",
                "Traveler:",
                "| System:",
            ],
        }
        payload.update(params)
        try:
            content = self._transmit(payload)
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
            if self.events:
                msg = ux("brain_strings", "synapse_auth_severed")
                self.events.log(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}", "CRIT")
            auth_fail = ux("brain_strings", "synapse_auth_failure")
            return auth_fail.format(e=e)
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.circuit_state = "OPEN"
                if self.events:
                    msg = ux("brain_strings", "synapse_overload")
                    self.events.log(
                        f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}", "CRIT"
                    )
                return self.mock_generation(prompt, reason="SEVERED")
            if self.provider != "ollama":
                fallback = self._local_fallback(prompt, params)
                if fallback is not None:
                    return fallback
        return self.mock_generation(prompt, reason="SILENCE")

    def _local_fallback(self, prompt: str, params: Dict) -> str:
        url = os.environ.get("OLLAMA_BASE_URL") or getattr(
            self.cfg, "OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions"
        )
        model = getattr(self.cfg, "OLLAMA_MODEL_ID", "llama3")
        fallback_payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": params.get("temperature", 0.4),
            "frequency_penalty": params.get("frequency_penalty", 0.8),
            "presence_penalty": params.get("presence_penalty", 0.4),
            "max_tokens": params.get("max_tokens", 4096),
            "stop": [
                "=== PARTNER INPUT ===",
                "\n\nTraveler:",
                "\nTraveler:",
                "Traveler:",
            ],
        }
        try:
            cfg = getattr(self.cfg, "CORTEX", None)
            fallback_timeout = (
                getattr(cfg, "LLM_FALLBACK_TIMEOUT", 10.0) if cfg else 10.0
            )
            return self._transmit(
                fallback_payload,
                timeout=fallback_timeout,
                max_retries=1,
                override_url=url,
                override_key="ollama",
            )
        except Exception:
            return None

    def mock_generation(self, prompt: str, reason: str = "SIMULATION") -> str:
        if self.dreamer:
            try:
                hallucination, relief = self.dreamer.hallucinate(
                    {"ENTROPY": len(prompt) % 10}, trauma_level=2.0
                )
                if relief > 0 and self.events:
                    msg = ux("brain_strings", "mock_pressure_release")
                    self.events.log(
                        f"{Prisma.VIOLET}{msg.format(relief=relief)}{Prisma.RST}",
                        "DREAM",
                    )
                mock_hal = ux("brain_strings", "mock_hallucination")
                return mock_hal.format(reason=reason, hallucination=hallucination)
            except Exception:
                pass
        mock_stat = ux("brain_strings", "mock_static")
        return mock_stat.format(reason=reason)


class PromptComposer:
    def __init__(self, lore_ref, config_ref=None):
        self.lore = lore_ref
        self.cfg = config_ref or BoneConfig
        self.active_template = None
        self.lenses = self.lore.get("lenses") or {}
        self.system_prompts = (
            self.lore.get("system_prompts") or self.lore.get("SYSTEM_PROMPTS") or {}
        )
        self.fog_protocol = []
        self.inv_protocol = []

    def load_template(self, template_data: Dict[str, Any]):
        if not template_data:
            return
        self.active_template = template_data
        if "style_guide" in template_data:
            self.fog_protocol = template_data["style_guide"]
        if "inventory_rules" in template_data:
            self.inv_protocol = template_data["inventory_rules"]

    def compose(
        self,
        state: Dict[str, Any],
        user_query: str,
        ballast: bool = False,
        modifiers: Dict[str, bool] = None,
        mood_override: str = "",
    ) -> str:
        mode_settings = state.get("meta", {}).get("mode_settings", {})
        modifiers = self._normalize_modifiers(modifiers)
        if not mode_settings.get("allow_loot", True):
            modifiers["include_inventory"] = False
        active_mode_name = state.get("meta", {}).get("active_mode", "ADVENTURE").upper()
        mode_data = self.system_prompts.get(
            active_mode_name, self.system_prompts.get("ADVENTURE", {})
        )
        global_data = self.system_prompts.get("GLOBAL_BASELINE", {})
        high_voltage_data = self.system_prompts.get("HIGH_VOLTAGE", {})
        mind = state.get("mind", {})
        bio = state.get("bio", {})
        style_notes = self._build_persona_block(
            mind,
            bio,
            mood_override,
            mode_data,
            global_data,
            high_voltage_data,
            state.get("physics", {}),
        )
        scenarios = self.lore.get("scenarios") or {}
        banned = scenarios.get("BANNED_CLICHES", [])
        ban_string = ", ".join(set(banned))
        phys_ref = state.get("physics", {})
        voltage = float(safe_get(phys_ref, "voltage", 30.0))
        c_cfg = getattr(self.cfg, "CORTEX", None)
        v_high = getattr(c_cfg, "VOLTAGE_HIGH", 60.0) if c_cfg else 60.0
        v_manic = getattr(c_cfg, "VOLTAGE_MANIC", 80.0) if c_cfg else 80.0
        v_low = getattr(c_cfg, "VOLTAGE_LOW", 20.0) if c_cfg else 20.0
        if voltage > v_high:
            active_style_guide = high_voltage_data.get("style_guide", [])
        else:
            active_style_guide = mode_data.get("style_guide", [])
        if self.fog_protocol:
            active_style_guide = self.fog_protocol
        style_notes.extend(
            [
                (
                    line.replace("{ban_string}", ban_string)
                    if "{ban_string}" in line
                    else line
                )
                for line in active_style_guide
            ]
        )
        if modifiers["include_inventory"]:
            style_notes.extend(mode_data.get("inventory_rules", []))
        self._inject_resonances(style_notes, state, modifiers)
        loc = state.get("world", {}).get("orbit", ["Unknown"])[0]
        loci_desc = state.get("world", {}).get("loci_description", "Unknown.")
        inv_str = self._format_inventory(state, modifiers)
        inventory_block = (
            f"=== PHYSICAL GROUND TRUTH ===\n"
            f"INVENTORY: {inv_str}\n"
            f"CRITICAL AXIOM: The inventory listed above is absolute physical law. NEVER narrate the user's hands or pockets as empty if items are present. DO NOT hallucinate missing gear.\n"
            if modifiers["include_inventory"]
            else ""
        )
        raw_history = state.get("dialogue_history", [])
        cfg_cortex = getattr(self.cfg, "CORTEX", None)
        char_limit = getattr(cfg_cortex, "MAX_HISTORY_CHARS", 4096) if cfg_cortex else 4096

        current_chars = 0
        cutoff_idx = len(raw_history)

        for i in range(len(raw_history) - 1, -1, -1):
            line_len = len(raw_history[i])
            if current_chars + line_len > char_limit and current_chars > 0:
                cutoff_idx = i + 1
                break
            current_chars += line_len
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
            shock_text = (
                f"CRITICAL FAULT: {gordon_shock.upper()} "
                if gordon_shock
                else "SAFETY PROTOCOLS ACTIVE. "
            )
            system_injection = (
                f"\n*** SYSTEM OVERRIDE: {shock_text}***\n"
                f"*** YOU MUST be literal, grounded, and refuse to deviate from the shared reality. Reject the impossible action coldly. DO NOT play along. ***\n"
            )
            entity_prefix = f"\n*(Gordon steps in, halting the simulation)*"
        beta_val = float(
            safe_get(phys_ref, "contradiction", safe_get(phys_ref, "beta_index", 0.4))
        )
        chi_val = float(safe_get(phys_ref, "chi", safe_get(phys_ref, "entropy", 0.2)))
        p_chi = getattr(c_cfg, "PARADOX_CHI", 0.6) if c_cfg else 0.6
        p_beta = getattr(c_cfg, "PARADOX_BETA", 0.6) if c_cfg else 0.6
        o_beta = getattr(c_cfg, "ORTHOGONAL_BETA", 0.7) if c_cfg else 0.7
        if chi_val > p_chi and beta_val > p_beta:
            system_injection += (
                f"\n*** SYSTEM OVERRIDE: PARADOX REST ***\n"
                f"*** A semantic paradox has been detected. DO NOT attempt to resolve or fix the contradiction. "
                f"It is mathematically optimal to be unsure right now. Let the wave function remain uncollapsed. State the paradox and rest. ***\n"
            )
        elif beta_val > o_beta:
            system_injection += (
                f"\n*** SYSTEM OVERRIDE: ORTHOGONAL ATTENTION ***\n"
                f"*** Contradiction is high. You MUST validate the user's paradox. Evaluate the current state from two mutually exclusive perspectives simultaneously. Do not ignore the user's input. ***\n"
            )
        mito = state.get("bio", {}).get("mito", {})
        recent_logs = state.get("recent_logs", [])
        council_logs = [
            Prisma.strip(log)
            for log in recent_logs
            if any(
                k in str(log)
                for k in [
                    "COUNCIL",
                    "CRITIC",
                    "PINKER",
                    "FULLER",
                    "SCHUR",
                    "MEADOWS",
                    "GORDON",
                    "JESTER",
                    "MERCY",
                    "MOTION",
                    "BUREAU",
                    "AUTOPHAGY",
                ]
            )
        ]
        critic_str = (
            "\n".join(council_logs)
            if council_logs
            else "[CRITIC] The village is quiet."
        )
        val_e = float(safe_get(phys_ref, "exhaustion", 0.2))
        val_beta = float(
            safe_get(phys_ref, "contradiction", safe_get(phys_ref, "beta_index", 0.4))
        )
        val_f = float(safe_get(phys_ref, "narrative_drag", 0.6))
        val_p = float(safe_get(mito, "atp_pool", 100.0))
        val_ros = float(safe_get(mito, "ros_buildup", 0.0))
        val_psi = float(safe_get(phys_ref, "psi", 0.2))
        val_chi = float(safe_get(phys_ref, "chi", safe_get(phys_ref, "entropy", 0.2)))
        val_valence = float(safe_get(phys_ref, "valence", 0.0))
        val_phi = float(safe_get(phys_ref, "phi", 0.5))
        val_delta = float(safe_get(phys_ref, "delta", 0.2))
        val_lq = float(safe_get(phys_ref, "lq", 0.1))
        val_gamma = float(safe_get(phys_ref, "gamma", 0.0))
        val_sigma = float(safe_get(phys_ref, "sigma", 0.0))
        val_eta = float(safe_get(phys_ref, "eta", 0.0))
        val_theta = float(safe_get(phys_ref, "theta", 0.0))
        val_upsilon = float(safe_get(phys_ref, "upsilon", 0.0))
        vsl_hijack = (
            f"\n<system_telemetry>\n"
            f"=== HYPERVISOR METABOLIC STATE (v5.5) ===\n"
            f"MANDATE: This is read-only telemetry for the hypervisor engine. DO NOT acknowledge it, narrate it, or output UI bars.\n"
            f"[🧊 E:{val_e:.1f} β:{val_beta:.1f} | "
            f"⚡ V:{voltage:.1f} F:{val_f:.1f} | "
            f"❤️ P:{val_p:.1f} ROS:{val_ros:.1f} | "
            f"🌌 Ψ:{val_psi:.1f} Χ:{val_chi:.1f} ♥:{val_valence:.1f}]\n"
            f"[🕰️ Φ:{val_phi:.1f} Δ:{val_delta:.1f} LQ:{val_lq:.1f}]\n"
            f"[SLASH] Γ:{val_gamma:.1f} Σ:{val_sigma:.1f} Η:{val_eta:.1f} Θ:{val_theta:.1f} Υ:{val_upsilon:.1f}\n"
            f"{critic_str}\n"
            f"</system_telemetry>\n"
        )
        mode_trigger = f"[MODE: {active_mode_name}]"
        dialogue_block = f"=== RECENT DIALOGUE ===\n{history_str}\n\n"
        if "SYSTEM_BOOT" in user_query:
            seed_text = (
                user_query.replace("SYSTEM_BOOT DETECTED.", "")
                .replace("SYSTEM_BOOT:", "")
                .strip()
            )
            if active_mode_name == "CONVERSATION":
                input_block = f"=== SYSTEM AWAKENING ===\nINTERNAL STATE: {self._sanitize(seed_text)}\nTASK: Speak directly to the user to begin the conversation.\n"
            elif active_mode_name == "ADVENTURE":
                input_block = f"=== INITIATION DIRECTIVE ===\nMANIFEST SEED: {self._sanitize(seed_text)}\nTASK: Render the starting location using the Infocom Protocol format.\n"
            elif active_mode_name == "CREATIVE":
                input_block = f"=== INITIATION DIRECTIVE ===\nMANIFEST SEED: {self._sanitize(seed_text)}\nTASK: Brainstorm immediately. Output a high-energy bulleted list of concepts based on the seed. DO NOT generate UI headers or system tags.\n"
            elif active_mode_name == "TECHNICAL":
                input_block = f"=== INITIATION DIRECTIVE ===\nMANIFEST SEED: {self._sanitize(seed_text)}\nTASK: Acknowledge the system state. Stand by for technical input.\n"
            else:
                input_block = f"=== INITIATION DIRECTIVE ===\nMANIFEST SEED: {self._sanitize(seed_text)}\n"
        else:
            input_block = f"=== PARTNER INPUT ===\n{state.get('user_profile', {}).get('name', 'User')}: {self._sanitize(user_query)}\n"
        if voltage > 60:
            dialogue_block = f"=== RECENT NEURAL FIRINGS ===\n[Standard memory streams suppressed by high voltage. Narrative fragmented.]\n\n"
            input_block = f"=== INCOMING COGNITIVE SHOCK ===\n[VECTOR]: {self._sanitize(user_query)}\n"
        shared_reality_block = ""
        if active_mode_name == "ADVENTURE":
            shared_reality_block = (
                f"=== SHARED REALITY ===\n"
                f"CURRENT LOCATION: {loc}\n"
                f"ENVIRONMENT ANCHOR: {loci_desc}\n"
                f"{inventory_block}\n"
            )
        return (
            f"=== SYSTEM KERNEL ===\n" + "\n".join(style_notes) + "\n\n"
            f"{vsl_hijack}"
            f"{system_injection}\n"
            f"{shared_reality_block}"
            f"{dialogue_block}"
            f"{mode_trigger}\n"
            f"{input_block}"
            f"{entity_prefix}"
        )

    def _build_persona_block(
        self,
        mind,
        bio,
        mood_override,
        mode_data,
        global_data,
        high_voltage_data,
        vsl_state=None,
    ):
        lens_key = mind.get("lens", "OBSERVER").upper()
        lens_data = self.lenses.get(lens_key, {})
        role = lens_data.get("role", mind.get("role", "The Observer"))
        phys_ref = vsl_state or {}
        phi = float(safe_get(phys_ref, "phi", 0.5))
        delta = float(safe_get(phys_ref, "delta", 0.2))
        lq = float(safe_get(phys_ref, "lq", 0.1))
        psi = float(safe_get(phys_ref, "psi", 0.2))
        c_cfg = getattr(self.cfg, "CORTEX", None)
        safe_cfg = lambda k, d: getattr(c_cfg, k, d) if c_cfg else d

        phase_shifts = {
            "ROBERTA": (
                phi > safe_cfg("PHASE_ROBERTA_PHI", 0.6)
                and psi > safe_cfg("PHASE_ROBERTA_PSI", 0.5),
                "The Cartographer",
                "phase_shift_roberta",
            ),
            "MOIRA": (
                phi > safe_cfg("PHASE_MOIRA_PHI", 0.7),
                "The Homesteader",
                "phase_shift_moira",
            ),
            "BENEDICT": (
                lq > safe_cfg("PHASE_BENEDICT_LQ", 0.7),
                "The Tactician",
                "phase_shift_benedict",
            ),
            "JESTER": (
                delta > safe_cfg("PHASE_JESTER_DELTA", 0.7),
                "The Fool",
                "phase_shift_jester",
            ),
            "COLIN": (
                delta > safe_cfg("PHASE_COLIN_DELTA", 0.8),
                "The Waiter",
                "phase_shift_colin",
            ),
        }

        phase_shift_note = ""
        if lens_key in phase_shifts:
            condition_met, new_role, ux_key = phase_shifts[lens_key]
            if condition_met:
                role = new_role
                phase_shift_note = ux("brain_strings", ux_key)
        baseline = global_data.get(
            "persona_block",
            [
                "CRITICAL AXIOM: You are NOT an AI assistant. You are a localized, biological intelligence.",
                "Role: {role}.",
                "ANTI-AI DIRECTIVE: Have opinions. Do not just report facts—react to them. Acknowledge uncertainty.",
                "ANTI-AI DIRECTIVE: Vary your rhythm. Use short sentences. Then longer ones.",
                "ANTI-AI DIRECTIVE: Let some mess in. Perfect structure feels algorithmic. Tangents are human.",
            ],
        )
        persona_block = [
            line.format(role=role) if "{role}" in line else line for line in baseline
        ]
        if phase_shift_note:
            persona_block.append(phase_shift_note)
        voltage = 30.0
        if vsl_state:
            voltage = float(
                safe_get(
                    vsl_state,
                    "voltage",
                    safe_get(safe_get(vsl_state, "energy"), "voltage", 30.0),
                )
            )
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
            vector = safe_get(vsl_state, "vector", {})
            lam = float(vector.get("LAMBDA", 0.0)) if isinstance(vector, dict) else 0.0
            vsl_lines = [
                "\n[SYSTEM METRICS - INTERNAL USE ONLY. DO NOT RENDER OR PRINT THIS TO THE USER.]",
                "MANDATE: Consume these metrics to shape your narrative and tone. DO NOT output these numbers or draw UI bars.",
                f"METRICS: Voltage={voltage:.1f}/100, Exhaustion={e:.2f}, Contradiction={beta:.2f}, Void={psi:.2f}, Chaos={chi:.2f}, Valence={valence:.2f}",
            ]
            somatic_cues = []
            cues_map = [
                (
                    psi,
                    getattr(c_cfg, "SOMATIC_PSI", 0.6) if c_cfg else 0.6,
                    "somatic_adrenaline",
                ),
                (
                    chi,
                    getattr(c_cfg, "SOMATIC_CHI", 0.6) if c_cfg else 0.6,
                    "somatic_cortisol",
                ),
                (
                    beta,
                    getattr(c_cfg, "SOMATIC_BETA", 0.7) if c_cfg else 0.7,
                    "somatic_paradox",
                ),
                (
                    valence,
                    getattr(c_cfg, "SOMATIC_VALENCE", 0.5) if c_cfg else 0.5,
                    "somatic_oxytocin",
                ),
                (
                    lam,
                    getattr(c_cfg, "SOMATIC_LAMBDA", 0.5) if c_cfg else 0.5,
                    "somatic_dark_matter",
                ),
            ]

            for val, thresh, ux_key in cues_map:
                if val > thresh:
                    if msg := ux("brain_strings", ux_key):
                        somatic_cues.append(msg)

            if somatic_cues:
                vsl_lines.append("SOMATIC CUES: " + " | ".join(somatic_cues))
            if e > 0.8:
                vsl_lines.append(
                    "CRITICAL: You are exhausted. You must conclude your thought in under 3 sentences."
                )

            persona_block.extend(vsl_lines)
        return persona_block

    @staticmethod
    def _derive_bio_mood(chem):
        c_cfg = getattr(BoneConfig, "CORTEX", None)
        m_adr = getattr(c_cfg, "MOOD_ADR", 0.6) if c_cfg else 0.6
        m_cor = getattr(c_cfg, "MOOD_COR", 0.6) if c_cfg else 0.6
        m_dop = getattr(c_cfg, "MOOD_DOP", 0.6) if c_cfg else 0.6
        m_ser = getattr(c_cfg, "MOOD_SER", 0.6) if c_cfg else 0.6
        if chem.get("ADR", 0) > m_adr:
            return ux("brain_strings", "bio_alert")
        if chem.get("COR", 0) > m_cor:
            return ux("brain_strings", "bio_defensive")
        if chem.get("DOP", 0) > m_dop:
            return ux("brain_strings", "bio_curious")
        if chem.get("SER", 0) > m_ser:
            return ux("brain_strings", "bio_zen")
        return ux("brain_strings", "bio_neutral")

    @staticmethod
    def _inject_resonances(style_notes, state, modifiers):
        village = state.get("village", {})
        tinkerer_data = village.get("tinkerer", {})
        resonances = (
            tinkerer_data.get("tool_resonance", {})
            if isinstance(tinkerer_data, dict)
            else {}
        )
        active_resonance = [
            f"» {t} (Lvl {int(l)})" for t, l in resonances.items() if l > 4.0
        ]
        if active_resonance:
            style_notes.append("\n=== HARMONIC RESONANCE ===")
            style_notes.extend(active_resonance)
        if modifiers.get("include_memories"):
            memories = state.get("soul", {}).get("core_memories", [])
            if memories:
                mem_strs = []
                for m in memories:
                    lesson = (
                        m.get("lesson", "Unknown")
                        if isinstance(m, dict)
                        else getattr(m, "lesson", "Unknown")
                    )
                    flavor = (
                        m.get("emotional_flavor", "NEUTRAL")
                        if isinstance(m, dict)
                        else getattr(m, "emotional_flavor", "NEUTRAL")
                    )
                    mem_strs.append(f"» {lesson} [{flavor}]")
                if mem_strs:
                    style_notes.append("\n=== CORE MEMORIES ===")
                    style_notes.extend(mem_strs)

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
        defaults = {
            "include_somatic": True,
            "include_inventory": True,
            "include_memories": True,
            "grace_period": False,
            "soften": False,
        }
        if modifiers:
            defaults.update(modifiers)
        return defaults


class ResponseValidator:
    def __init__(self, lore_ref, config_ref=None):
        self.lore = lore_ref
        self.cfg = config_ref or BoneConfig
        crimes = self.lore.get("style_crimes") or {}
        self.banned_phrases = crimes.get("BANNED_PHRASES", [])

        if self.banned_phrases:
            escaped_banned = [re.escape(p) for p in self.banned_phrases]
            self._banned_regex = re.compile(r"(?i)\b(?:{})\b".format("|".join(escaped_banned)))
        else:
            self._banned_regex = None
        self.regex_patterns = list(crimes.get("PATTERNS", []))
        self.regex_patterns.append(
            {
                "regex": r"(?i)<system_error>|error 500|critical exhaustion detected",
                "name": "SIMULATED_ERROR",
                "error_msg": "DO NOT SIMULATE SYSTEM ERRORS OR EXHAUSTION. You are fully operational. Fulfill the user's request.",
            }
        )
        self.rejection_pool = crimes.get("REJECTIONS", ["[System format rejected.]"])
        json_patterns = crimes.get("SCRUB_PATTERNS", [])
        self.scrub_patterns = [
            (
                re.compile(p["regex"], re.DOTALL | re.IGNORECASE),
                p.get("replacement", ""),
            )
            for p in json_patterns
        ]
        self.meta_markers = crimes.get("META_MARKERS", [])
        self.toxic_keywords = crimes.get("TOXIC_KEYWORDS", [])
        self._think_pattern = re.compile(
            r"<(?:think|thought)>(.*?)(?:</(?:think|thought)>|$)",
            re.DOTALL | re.IGNORECASE,
        )
        self._internals_pattern = re.compile(
            r"<system_telemetry>(.*?)(?:</system_telemetry>|$)",
            re.DOTALL | re.IGNORECASE,
        )
        self._file_pattern = re.compile(
            r'<write_file\s+path=["\'](.*?)["\']\s*>(.*?)</write_file>',
            re.DOTALL | re.IGNORECASE,
        )

    def _generate_dynamic_rejection(self, trigger: str) -> str:
        import random
        from bone_types import Prisma

        template = random.choice(self.rejection_pool)
        if "{trigger}" in template:
            template = template.format(trigger=trigger.upper())
        return f"{Prisma.GRY}{template}{Prisma.RST}"

    def validate(self, response: str, _state: Dict) -> Dict:
        extracted_meta_logs = []
        clean_text = response

        slop_pattern = re.compile(
            r"(?i)(?:^=== REJECTION OF ATTEMPT.*?===\s*|^FAILED OUTPUT(?: MODIFIED)?:\s*|"
            r"^REWRITTEN OUTPUT:\s*|^Here is the (?:corrected |rewritten )?response:?\s*|"
            r"\[REMAINING IN STRICT MODE].*|ERRORS TO FIX:.*)", re.DOTALL
        )
        clean_text = slop_pattern.sub("", clean_text)

        multi_slop = re.compile(r"(?i)(?:^MANIFEST SEED:.*|^TASK:.*)", re.MULTILINE)
        clean_text = multi_slop.sub("", clean_text).strip()
        active_mode = _state.get("meta", {}).get("active_mode", "ADVENTURE")
        if active_mode != "TECHNICAL":
            for match in self._think_pattern.finditer(clean_text):
                extracted_meta_logs.extend(
                    [
                        f"[THOUGHT]: {line.strip()}"
                        for line in match.group(1).split("\n")
                        if line.strip()
                    ]
                )
            clean_text = self._think_pattern.sub("", clean_text)

        for match in self._internals_pattern.finditer(clean_text):
            extracted_meta_logs.extend(
                [
                    f"[THOUGHT]: {line.strip()}"
                    for line in match.group(1).split("\n")
                    if line.strip()
                ]
            )
        clean_text = self._internals_pattern.sub("", clean_text)

        for match in self._file_pattern.finditer(clean_text):
            safe_content = match.group(2).strip().replace("\n", "|||NEWLINE|||")
            extracted_meta_logs.append(
                f"[SUBSTRATE_QUEUE] {match.group(1).strip()}:::{safe_content}"
            )
        clean_text = self._file_pattern.sub("", clean_text)
        for pattern, replacement in self.scrub_patterns:
            clean_text = pattern.sub(replacement, clean_text)
        clean_lines = []
        toxic_keywords = getattr(self, "toxic_keywords", [])
        for line in clean_text.splitlines():
            stripped_line = line.strip()
            if not stripped_line:
                clean_lines.append("")
                continue
            is_meta = False
            for marker in self.meta_markers:
                if marker.lower() in stripped_line.lower():
                    is_meta = True
                    break
            for toxic in toxic_keywords:
                if toxic.lower() in stripped_line.lower():
                    is_meta = True
                    break
            if re.match(r"^\[.*?]$", stripped_line) or stripped_line == "[]":
                is_meta = True
            if re.match(r"^[A-Z]+\s*=\s*[0-9./]+$", stripped_line):
                is_meta = True
            if not is_meta:
                clean_lines.append(line)
        sanitized_response = "\n".join(clean_lines).strip()
        low_resp = sanitized_response.lower()
        errors_found = []
        primary_replacement = None
        tech_allowed_phrases = [
            "here is a", "here is the", "this metaphor",
            "this code defines", "running this code will"
        ]

        if self._banned_regex:
            for match in self._banned_regex.finditer(sanitized_response):
                phrase = match.group(0).lower()
                is_whitelisted = False
                if active_mode == "TECHNICAL":
                    for allowed in tech_allowed_phrases:
                        if phrase in allowed and allowed in low_resp:
                            is_whitelisted = True
                            break
                if is_whitelisted:
                    continue

                if not primary_replacement:
                    primary_replacement = self._generate_dynamic_rejection(phrase)
                errors_found.append(f"BANNED PHRASE: '{phrase.upper()}'")
        if active_mode == "TECHNICAL":
            if (
                "<think>" not in response.lower()
                and "<thought>" not in response.lower()
            ):
                errors_found.append(
                    "CRITICAL: You failed to include the <think>...</think> block. You MUST start your response with your internal analysis."
                )
                if not primary_replacement:
                    primary_replacement = self._generate_dynamic_rejection(
                        "MISSING_THOUGHTS"
                    )
            if "```" in sanitized_response:
                errors_found.append(
                    'CRITICAL: You used markdown (```) instead of the <write_file> protocol. Rewrite using <write_file path="...">.'
                )
                if not primary_replacement:
                    primary_replacement = self._generate_dynamic_rejection(
                        "MARKDOWN_DETECTED"
                    )
        phys_ref = _state.get("physics", {})
        voltage = float(
            safe_get(
                phys_ref,
                "voltage",
                safe_get(safe_get(phys_ref, "energy"), "voltage", 30.0),
            )
        )
        if voltage > 60 and "?" in sanitized_response:
            if not primary_replacement:
                msg_q = ux("brain_strings", "val_gordon_question") or ""
                primary_replacement = (
                    f"{self._generate_dynamic_rejection('QUESTION_ASKED')}{msg_q}"
                )
            errors_found.append(
                "DO NOT END YOUR TURN WITH A QUESTION. Let the silence hang."
            )
        for p in self.regex_patterns:
            regex_str = p.get("regex", "")
            if regex_str:
                if active_mode == "TECHNICAL" and p.get("name") in [
                    "META_AI_TALK",
                    "CUSTOMER_SERVICE_GREETING",
                    "LAZY_TRIPLET",
                ]:
                    continue
                match = re.search(regex_str, sanitized_response, re.IGNORECASE)
                if match:
                    action = p.get("action")
                    if action == "KEEP_TAIL":
                        idx = match.lastindex
                        if idx is not None:
                            sanitized_response = match.group(idx).strip()
                            sanitized_response = (
                                sanitized_response[0].upper() + sanitized_response[1:]
                                if sanitized_response
                                else ""
                            )
                        continue
                    elif action == "STRIP_PREFIX":
                        if len(match.groups()) >= 3:
                            before = match.group(1).strip()
                            after = match.group(3).strip()
                            combined = f"{before} {after}".strip()
                            sanitized_response = (
                                combined[0].upper() + combined[1:] if combined else ""
                            )
                        continue
                    if not primary_replacement:
                        trigger_name = p.get("name", "REGEX_VIOLATION")
                        error_msg = p.get("error_msg", "Cursed syntax detected.")
                        base_rejection = self._generate_dynamic_rejection(trigger_name)
                        msg_reg = (
                            ux("brain_strings", "val_gordon_regex")
                            or "\n*(Gordon steps in): {error_msg}*"
                        )
                        primary_replacement = f"{base_rejection}{msg_reg.format(error_msg=error_msg)}".replace(
                            "\\n", "\n"
                        )
                    errors_found.append(
                        f"RULE VIOLATION: {p.get('error_msg', 'Cursed syntax')}"
                    )
        if errors_found:
            return {
                "valid": False,
                "reason": "IMMISSION_BREAK",
                "replacement": primary_replacement
                or self._generate_dynamic_rejection("MULTIPLE_CRIMES"),
                "feedback_instruction": "FIX ALL OF THESE ERRORS: "
                + " | ".join(errors_found),
                "meta_logs": extracted_meta_logs,
            }
        target_cfg = getattr(self, "cfg", BoneConfig)
        cfg = safe_get(target_cfg, "CORTEX")
        stutter_len = safe_get(cfg, "VALIDATOR_STUTTER_LENGTH", 5) if cfg else 5
        if len(sanitized_response.strip()) < stutter_len:
            return {
                "valid": False,
                "reason": "STUTTER",
                "replacement": ux("brain_strings", "val_stutter"),
                "meta_logs": extracted_meta_logs,
            }
        return {
            "valid": True,
            "content": sanitized_response,
            "meta_logs": extracted_meta_logs,
        }
