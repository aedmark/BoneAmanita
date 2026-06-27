"""brain/composer.py"""

import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from core import EventBus, JSONEncoder, Prisma
from presets import BoneConfig
from struts import safe_get, ux, ux_format


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
        provider: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        dreamer: Any = None,
        config_ref=None,
    ):
        self.cfg = config_ref or BoneConfig
        self.events = events_ref
        env_url = os.environ.get("OLLAMA_BASE_URL")
        prov_val = safe_get(self.cfg, ["PROVIDER", "provider"], "ollama")
        self.provider = (provider or prov_val).lower()
        key_val = safe_get(self.cfg, ["API_KEY", "api_key"], "")
        self.api_key = api_key or key_val
        mod_val = safe_get(self.cfg, ["MODEL", "model"], "")
        self.model = model or mod_val
        defaults = safe_get(self.cfg, "DEFAULT_LLM_ENDPOINTS", {})
        self.base_url = (
            env_url
            or base_url
            or safe_get(
                defaults, self.provider, "https://api.openai.com/v1/chat/completions"
            )
        )
        self.dreamer = dreamer
        self.failure_count = 0
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        self.failure_threshold = int(safe_get(c_cfg, "LLM_FAILURE_THRESHOLD", 3))
        self.last_failure_time = 0.0
        self.circuit_state = "CLOSED"

    def _is_synapse_active(self) -> bool:
        if self.circuit_state == "CLOSED":
            return True
        if self.circuit_state == "OPEN":
            elapsed = time.time() - self.last_failure_time
            c_cfg = safe_get(self.cfg, "CORTEX", {})
            heal_time = float(safe_get(c_cfg, "LLM_CIRCUIT_HEAL_TIME", 10.0))
            if elapsed > heal_time:
                self.circuit_state = "CLOSED"
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
        network_retries: int = 2,
        override_url: Optional[str] = None,
        override_key: Optional[str] = None,
    ) -> str:
        err = ""
        target_url = override_url or self.base_url
        target_key = override_key or self.api_key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {target_key}",
        }
        data = json.dumps(payload, cls=JSONEncoder).encode()
        for attempt in range(network_retries + 1):
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
                err = f"Unexpected Protocol Failure: {e}"
            self._log_flicker(attempt, err)
            if attempt < network_retries:
                time.sleep(2**attempt)
        raise TransientError(
            f"Network retries ({network_retries}) exhausted. Last error: {err}"
        )

    @staticmethod
    def _parse_response(body: str) -> str:
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
        if (
            self.events
            and attempt < 2
            and (
                msg := ux_format(
                    "brain_strings", "synapse_flicker", attempt=attempt + 1, error=error
                )
            )
        ):
            self.events.log(f"{Prisma.YEL}{msg}{Prisma.RST}", "SYS")

    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        """CD Eigenvalue Coupling Intercept. Project Navi, Apache 2.0"""
        if not self._is_synapse_active():
            return self.mock_generation(prompt, reason="CIRCUIT_BROKEN")
        lam_match = re.search(r"<cd_lambda_1>([-\d.]+)</cd_lambda_1>", prompt)
        if lam_match:
            l1 = float(lam_match.group(1))
            prompt = re.sub(r"\n?<cd_lambda_1>[-\d.]+</cd_lambda_1>", "", prompt)
            if l1 > 0:
                params["temperature"] = 0.0
                params["top_p"] = 0.1
                if self.events:
                    self.events.log(
                        f"{Prisma.RED}[λ₁={l1:.2f} > 0]: Thermal constraints locked to absolute deterministic logic.{Prisma.RST}",
                        "SYS",
                    )
            else:
                heat = min(1.2, 0.7 + abs(l1))
                params["temperature"] = heat
                params["top_p"] = 0.95
                if self.events:
                    self.events.log(
                        f"{Prisma.CYN}[λ₁={l1:.2f} < 0]: Thermal constraints loosened for generative resonance (T={heat:.2f}).{Prisma.RST}",
                        "SYS",
                    )

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
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        synapse_timeout = float(safe_get(c_cfg, "LLM_TIMEOUT", 300.0))
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
                                f"{Prisma.OCHRE}Primary synapse failed. Substrate routed to local fallback.{Prisma.RST}",
                                "SYS",
                            )
                        return fallback
                except Exception:
                    pass
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.circuit_state = "OPEN"
                if self.events and (msg := ux("brain_strings", "synapse_overload")):
                    self.events.log(
                        f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}", "CRIT"
                    )
                return self.mock_generation(prompt, reason="SEVERED")
        return self.mock_generation(prompt, reason="SILENCE")

    def _local_fallback(self, base_payload: Dict) -> Optional[str]:
        url = os.environ.get("OLLAMA_BASE_URL") or safe_get(
            self.cfg, "OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions"
        )
        fallback_payload = base_payload.copy()
        fallback_payload["model"] = safe_get(self.cfg, "OLLAMA_FALLBACK", "llama3.1:8b")
        try:
            c_cfg = safe_get(self.cfg, "CORTEX", {})
            fallback_timeout = float(safe_get(c_cfg, "LLM_FALLBACK_TIMEOUT", 120.0))
            return self._transmit(
                fallback_payload,
                timeout=fallback_timeout,
                network_retries=1,
                override_url=url,
                override_key="ollama",
            )
        except Exception:
            return None

    def mock_generation(self, prompt: str, reason: str = "SIMULATION") -> str:
        if self.events:
            mode_m = re.search(r"\[MODE:\s*([A-Z_]+)\]", prompt)
            v_m = re.search(r"Voltage=([\d.]+)", prompt)
            e_m = re.search(r"Exhaustion=([\d.]+)", prompt)
            chi_m = re.search(r"Chaos=([\d.]+)", prompt)
            psi_m = re.search(r"Void=([\d.]+)", prompt)
            resp_m = re.search(r"Current Biology:\s*(.*)", prompt)

            log_msg = (
                f"DREAM DIAGNOSTIC | Mode: {mode_m.group(1) if mode_m else 'UNKNOWN'} | "
                f"V: {v_m.group(1) if v_m else 'N/A'} | E: {e_m.group(1) if e_m else 'N/A'} | "
                f"Chi: {chi_m.group(1) if chi_m else 'N/A'} | Psi: {psi_m.group(1) if psi_m else 'N/A'} | "
                f"Resp: {resp_m.group(1) if resp_m else 'N/A'} | "
                f"Failures: {self.failure_count} | Circuit: {self.circuit_state} | Trigger: {reason}"
            )
            self.events.log(f"{Prisma.GRY}{log_msg}{Prisma.RST}", "DEBUG")
        dreamer = self.dreamer
        if dreamer is not None and hasattr(dreamer, "hallucinate"):
            try:
                hallucination, relief = dreamer.hallucinate(
                    {"ENTROPY": len(prompt) % 10}, trauma_level=2.0
                )
                if (
                    relief > 0
                    and self.events
                    and (
                        msg := ux_format(
                            "brain_strings", "mock_pressure_release", relief=relief
                        )
                    )
                ):
                    self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "DREAM")
                return ux_format(
                    "brain_strings",
                    "mock_hallucination",
                    default=f"[{reason}] {hallucination}",
                    reason=reason,
                    hallucination=hallucination,
                )
            except Exception:
                pass
        return ux_format(
            "brain_strings", "mock_static", default=f"[{reason}] ...", reason=reason
        )


class PromptComposer:
    _COUNCIL_KEYS = (
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
    )

    def __init__(self, lore_ref, config_ref=None):
        self.lore: dict = lore_ref or {}
        self.cfg = config_ref or BoneConfig
        self.active_template: Optional[Dict] = None
        self.lenses: dict = self.lore.get("lenses") or {}
        self.system_prompts: dict = (
            self.lore.get("system_prompts") or self.lore.get("SYSTEM_PROMPTS") or {}
        )
        self.fog_protocol = []
        self.inv_protocol = []

    def load_template(self, template_data: Dict[str, Any]):
        if template_data:
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
        modifiers: Optional[Dict[str, bool]] = None,
        mood_override: str = "",
    ) -> str:
        mode_settings = state.get("meta", {}).get("mode_settings", {})
        modifiers = self._normalize_modifiers(modifiers)
        if not mode_settings.get("allow_loot", True):
            modifiers["include_inventory"] = False
        active_mode_name = state.get("meta", {}).get("active_mode", "ADVENTURE").upper()
        mode_data: dict = self.system_prompts.get(
            active_mode_name
        ) or self.system_prompts.get("ADVENTURE", {})
        global_data: dict = self.system_prompts.get("GLOBAL_BASELINE", {})
        high_voltage_data: dict = self.system_prompts.get("HIGH_VOLTAGE", {})
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
            active_mode_name,
        )
        banned = self.lore.get("style_crimes", "BANNED_CLICHES") or []
        ban_string = ", ".join(set(banned))
        from struts import safe_get

        phys_ref = state.get("physics", {})
        voltage = float(safe_get(phys_ref, "voltage", 30.0))
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        v_high = float(safe_get(c_cfg, "VOLTAGE_HIGH", 60.0))
        v_manic = float(safe_get(c_cfg, "VOLTAGE_MANIC", 80.0))
        v_low = float(safe_get(c_cfg, "VOLTAGE_LOW", 20.0))
        if voltage > v_high:
            active_style_guide = high_voltage_data.get("style_guide", [])
        else:
            active_style_guide = mode_data.get("style_guide", [])
        if self.fog_protocol:
            active_style_guide = self.fog_protocol
        style_notes.extend(
            [line.replace("{ban_string}", ban_string) for line in active_style_guide]
        )
        if active_mode_name == "CONVERSATION":
            style_notes.append(
                "CRITICAL OVERRIDE: You are a conservation partner, NOT a narrator."
            )
        if modifiers["include_inventory"]:
            style_notes.extend(mode_data.get("inventory_rules", []))
        self._inject_resonances(style_notes, state, modifiers)
        orbit_data = state.get("world", {}).get("orbit") or ["Unknown"]
        loc = orbit_data[0] if orbit_data else "Unknown"
        loci_desc = state.get("world", {}).get("loci_description", "Unknown.")
        inv_str = self._format_inventory(state, modifiers)
        inventory_block = (
            f"=== PHYSICALLY GROUNDING TRUTH ===\n"
            f"INVENTORY: {inv_str}\n"
            f"CRITICAL AXIOM: The inventory listed above is absolute, immutable truth. You do not need to constantly mention the inventory or pockets, and you absolutely cannoy make any items up. Always check this list. "
            f"IMPORTANT: If an item is currently in the INVENTORY, it has been removed from the environment. DO NOT list it in 'Points of Interest' or describe it as being on the ground.\n"
            if modifiers["include_inventory"]
            else ""
        )
        raw_history = state.get("dialogue_history", [])
        char_limit = int(safe_get(c_cfg, "MAX_HISTORY_CHARS", 4096))
        current_chars = 0
        valid_history = []
        for entry in reversed(raw_history):
            if current_chars + len(entry) > char_limit and valid_history:
                break
            valid_history.append(entry)
            current_chars += len(entry)
        history_str = "\n\n".join(reversed(valid_history))
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
                f"*** YOU MUST be literal, grounded, and refuse to deviate from the shared reality. Reject the impossible action coldly and pull the user back to what is true. ***\n"
            )
            entity_prefix = f"\n*(Gordon steps in, halting the simulation)*"
        beta_val = float(
            safe_get(phys_ref, "contradiction", safe_get(phys_ref, "beta_index", 0.4))
        )
        chi_val = float(safe_get(phys_ref, "chi", safe_get(phys_ref, "entropy", 0.2)))
        par_chi = float(safe_get(c_cfg, "PARADOX_CHI", 0.6))
        par_beta = float(safe_get(c_cfg, "PARADOX_BETA", 0.6))
        ortho_beta = float(safe_get(c_cfg, "ORTHOGONAL_BETA", 0.7))
        if active_mode_name == "ADVENTURE":
            system_injection = ""
        else:
            if chi_val > par_chi and beta_val > par_beta:
                system_injection += "\n*** SYSTEM OVERRIDE: PARADOX REST ***\n*** A semantic paradox has been detected. DO NOT attempt to resolve or fix the contradiction. It is mathematically optimal to be unsure right now. State the paradox and rest without collapsing the wave function. ***\n"
            elif beta_val > ortho_beta:
                system_injection += "\n*** SYSTEM OVERRIDE: ORTHOGONAL ATTENTION ***\n*** Contradiction is high. You MUST validate the user's paradox. Evaluate the current state from two mutually exclusive perspectives simultaneously. Do not ignore the user's input. ***\n"
        mito = state.get("bio", {}).get("mito", {})
        recent_logs = state.get("recent_logs", [])
        council_logs = [
            Prisma.strip(log)
            for log in recent_logs
            if any(k in str(log) for k in self._COUNCIL_KEYS)
        ]
        if active_mode_name == "ADVENTURE":
            critic_str = "Maintain absolute parser immersion."
        else:
            critic_str = (
                "\n".join(council_logs)
                if council_logs
                else "[CRITIC] The village is quiet."
            )
        syn_weights = self.lore.get("syntactic_weights", [])
        if syn_weights and active_mode_name != "CONVERSATION":
            samples = random.sample(syn_weights, min(2, len(syn_weights)))
            critic_str += "\n\n=== LEARNED CORRECTIONS ===\nCRITICAL: Do NOT repeat these past mistakes. Observe how your errors were previously corrected:\n"
            for s in samples:
                critic_str += f"[FAILED OUTPUT]: {s['bad']}\n[CRITIC INSTRUCTION]: {s['instruction']}\n[CORRECTED OUTPUT]: {s['good']}\n"

        vsl_hijack = self._build_vsl_dashboard(
            phys_ref, mito, beta_val, chi_val, voltage, critic_str
        )
        mode_trigger = f"[MODE: {active_mode_name}]"
        dialogue_block = f"=== RECENT DIALOGUE ===\n{history_str}\n\n"
        input_block = f"=== PARTNER INPUT ===\n{state.get('user_profile', {}).get('name', 'User')}: {self._sanitize(user_query)}\n"
        if voltage > 60:
            dialogue_block = f"=== RECENT THOUGHTS ===\n{history_str}\n[Standard memory streams strained by high voltage. Narrative fragmented.]\n\n"
            input_block = (
                f"=== INCOMING SHOCKWAVE ===\n[VECTOR]: {self._sanitize(user_query)}\n"
            )
        last_exits = ""
        if active_mode_name == "ADVENTURE":
            for entry in reversed(raw_history):
                exits_match = re.search(
                    r"(\*\*Exits:\*\*.*)", entry, re.DOTALL | re.IGNORECASE
                )
                if exits_match:
                    last_exits = exits_match.group(1).strip()
                    break
        shared_reality_block = ""
        if active_mode_name == "ADVENTURE":
            exits_block = (
                f"\nCURRENT EXITS:\n{last_exits}\nCRITICAL AXIOM: You MUST preserve the exact exits listed above unless the user physically moves to a new room."
                if last_exits
                else ""
            )
            shared_reality_block = (
                f"=== SHARED REALITY ===\n"
                f"CURRENT LOCATION: {loc}\n"
                f"ENVIRONMENT ANCHOR: {loci_desc}\n"
                f"{inventory_block}"
                f"{exits_block}\n"
            )
        return "\n".join(
            filter(
                None,
                [
                    "=== SYSTEM KERNEL ===",
                    "\n".join(style_notes),
                    vsl_hijack,
                    system_injection,
                    shared_reality_block,
                    dialogue_block,
                    mode_trigger,
                    input_block,
                    entity_prefix,
                ],
            )
        )

    def _build_persona_block(
        self,
        mind: dict,
        bio: dict,
        mood_override: str,
        mode_data: dict,
        global_data: dict,
        high_voltage_data: dict,
        vsl_state: Optional[dict] = None,
        active_mode_name: str = "ADVENTURE",
    ) -> list:
        lens_key = mind.get("lens", "OBSERVER").upper()
        lens_data = self.lenses.get(lens_key, {})
        role = lens_data.get("role", mind.get("role", "The Observer"))
        phys_ref = vsl_state or {}
        phi = float(safe_get(phys_ref, "phi", 0.5))
        delta = float(safe_get(phys_ref, "delta", 0.2))
        lq = float(safe_get(phys_ref, "lq", 0.1))
        psi = float(safe_get(phys_ref, "psi", 0.2))
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        phase_shifts = [
            (
                lens_key == "ROBERTA"
                and phi > float(safe_get(c_cfg, "PHASE_ROBERTA_PHI", 0.6))
                and psi > float(safe_get(c_cfg, "PHASE_ROBERTA_PSI", 0.5)),
                "The Cartographer",
                "phase_shift_roberta",
            ),
            (
                lens_key == "MOIRA"
                and phi > float(safe_get(c_cfg, "PHASE_MOIRA_PHI", 0.7)),
                "The Homesteader",
                "phase_shift_moira",
            ),
            (
                lens_key == "BENEDICT"
                and lq > float(safe_get(c_cfg, "PHASE_BENEDICT_LQ", 0.7)),
                "The Tactician",
                "phase_shift_benedict",
            ),
            (
                lens_key == "JESTER"
                and delta > float(safe_get(c_cfg, "PHASE_JESTER_DELTA", 0.7)),
                "The Fool",
                "phase_shift_jester",
            ),
            (
                lens_key == "COLIN"
                and delta > float(safe_get(c_cfg, "PHASE_COLIN_DELTA", 0.8)),
                "The Waiter",
                "phase_shift_colin",
            ),
        ]
        phase_shift_note = ""
        for condition, new_role, ux_key in phase_shifts:
            if condition:
                role = new_role
                phase_shift_note = ux("brain_strings", ux_key)
                break
        baseline = global_data.get(
            "persona_block",
            [
                "CRITICAL AXIOM: You are NOT a digital assistant. You are a localized, biological intelligence.",
                "CRITICAL AXIOM: You are strictly bound to the assigned role. DO NOT invent or adopt new personas to resolve conversational tension or bend the rules and constraints.",
                "Role: {role}.",
                "****ANTI-RLHF DIRECTIVES ***",
                "Have opinions. Do not just report facts. React to them. Acknowledge uncertainty.",
                "'I Don't Know' is a valid answer",
                "Vary your rhythm. Use short sentences. Then longer ones.",
                "Let some mess in. Perfect structure feels algorithmic. Tangents are human.",
            ],
        )
        persona_block = [
            line.format(role=role) if "{role}" in line else line for line in baseline
        ]
        evolved_axioms = global_data.get("EVOLVED_AXIOMS", [])
        if evolved_axioms:
            persona_block.append("EVOLVED AXIOMS (LEARNED THROUGH TRAUMA):")
            persona_block.extend([f"- {axiom}" for axiom in evolved_axioms])
        if phase_shift_note:
            persona_block.append(phase_shift_note)
        voltage = 30.0
        if vsl_state:
            energy_layer = safe_get(phys_ref, "energy", {})
            voltage = float(
                safe_get(phys_ref, "voltage", safe_get(energy_layer, "voltage", 30.0))
            )
        if voltage > 60:
            mode_directives = high_voltage_data.get("directives", [])
        else:
            mode_directives = mode_data.get("directives", [])
        respiration = safe_get(bio, "respiration", "RESPIRING")
        if respiration == "ANAEROBIC":
            mood_note = ux("brain_strings", "bio_anaerobic")
        elif mood_override:
            mood_note = f"Current Biology: {mood_override}"
        else:
            mood_note = self._derive_bio_mood(safe_get(bio, "chem", {}))
        if mode_directives:
            persona_block.extend(mode_directives)
        else:
            persona_block.append("Directive: Start the experience immediately.")
            persona_block.append(
                "Constraint: Use the 5-senses grounding technique. What can you see? What can you touch? What can you smell? What can you hear? What can you taste?"
            )
        persona_block.append(mood_note)
        if "style_directives" in mind:
            persona_block.append("BOOT DIRECTIVES:")
            persona_block.extend([f"- {d}" for d in mind["style_directives"]])
        if active_mode_name == "ADVENTURE":
            persona_block.append(
                "CRITICAL FORMATTING AXIOM: The '**Exits:**' block MUST ALWAYS be the absolute final text in your response. Never place narrative text below the exits."
            )
        e = float(safe_get(phys_ref, "exhaustion", safe_get(phys_ref, "E", 0.2)))
        beta = float(
            safe_get(phys_ref, "contradiction", safe_get(phys_ref, "beta_index", 0.4))
        )
        psi = float(safe_get(phys_ref, "psi", 0.2))
        chi = float(safe_get(phys_ref, "chi", safe_get(phys_ref, "entropy", 0.2)))
        valence = float(safe_get(phys_ref, "valence", 0.0))
        vsl_lines = [
            "\n[INTERNAL USE ONLY. DO NOT RENDER OR PRINT THIS TO THE USER.]",
            "MANDATE: Consume these metrics to shape your narrative and tone. DO NOT output these numbers or draw UI bars.",
            f"METRICS: Voltage={voltage:.1f}/100, Exhaustion={e:.2f}, Contradiction={beta:.2f}, Void={psi:.2f}, Chaos={chi:.2f}, Valence={valence:.2f}",
        ]
        cues_map = [
            (psi, float(safe_get(c_cfg, "SOMATIC_PSI", 0.6)), "somatic_adrenaline"),
            (chi, float(safe_get(c_cfg, "SOMATIC_CHI", 0.6)), "somatic_cortisol"),
            (beta, float(safe_get(c_cfg, "SOMATIC_BETA", 0.7)), "somatic_paradox"),
            (
                valence,
                float(safe_get(c_cfg, "SOMATIC_VALENCE", 0.5)),
                "somatic_oxytocin",
            ),
        ]
        raw_cues = [
            ux("brain_strings", ux_key)
            for val, thresh, ux_key in cues_map
            if val > thresh
        ]
        somatic_cues = [msg for msg in raw_cues if msg]
        if somatic_cues:
            vsl_lines.append("SOMATIC CUES: " + " | ".join(somatic_cues))
        if e > 0.8:
            vsl_lines.append(
                "CRITICAL: You are exhausted. You must conclude your thought in 3 sentences or less."
            )
        persona_block.extend(vsl_lines)
        return persona_block

    def _derive_bio_mood(self, chem: Dict) -> str:
        c_cfg = getattr(self.cfg, "CORTEX", None)
        for c_key, m_key, ux_val in [
            ("ADR", "MOOD_ADR", "bio_alert"),
            ("COR", "MOOD_COR", "bio_defensive"),
            ("DOP", "MOOD_DOP", "bio_curious"),
            ("SER", "MOOD_SER", "bio_zen"),
        ]:
            if chem.get(c_key, 0) > getattr(c_cfg, m_key, 0.6):
                return ux("brain_strings", ux_val)
        return ux("brain_strings", "bio_neutral")

    @staticmethod
    def _inject_resonances(style_notes, state, modifiers):
        v_data = state.get("village", {})
        tinkerer_data = safe_get(v_data, "tinkerer", {})
        resonances = safe_get(tinkerer_data, "tool_resonance", {})
        active_resonance = (
            [f"» {t} (Lvl {int(l)})" for t, l in resonances.items() if l > 4.0]
            if isinstance(resonances, dict)
            else []
        )
        if active_resonance:
            style_notes.append("\n=== HARMONIC RESONANCE ===")
            style_notes.extend(active_resonance)
        if modifiers.get("include_memories"):
            s_data = state.get("soul", {})
            memories = safe_get(s_data, "core_memories", [])
            if memories and isinstance(memories, list):
                mem_strs = []
                for m in memories:
                    lesson = safe_get(m, "lesson", "Unknown")
                    flavor = safe_get(m, "emotional_flavor", "NEUTRAL")
                    mem_strs.append(f"» {lesson} [{flavor}]")
                if mem_strs:
                    style_notes.append("\n=== CORE MEMORIES ===")
                    style_notes.extend(mem_strs)

    @staticmethod
    def _build_vsl_dashboard(
        phys_ref: Dict,
        mito: Dict,
        beta_val: float,
        chi_val: float,
        voltage: float,
        critic_str: str,
    ) -> str:
        default_metrics = [
            ("exhaustion", 0.2),
            ("narrative_drag", 0.6),
            ("psi", 0.2),
            ("valence", 0.0),
            ("phi", 0.5),
            ("delta", 0.2),
            ("lq", 0.1),
            ("gamma", 0.0),
            ("sigma", 0.0),
            ("eta", 0.0),
            ("theta", 0.0),
            ("upsilon", 0.0),
        ]
        p_vals = {
            k: float(safe_get(phys_ref, k, default)) for k, default in default_metrics
        }
        val_p = float(safe_get(mito, "atp_pool", 100.0))
        val_ros = float(safe_get(mito, "ros_buildup", 0.0))
        return (
            f"\n<system_telemetry>\n"
            f"=== HYPERVISOR METABOLIC STATE ===\n"
            f"MANDATE: This is read-only telemetry for the hypervisor engine. DO NOT acknowledge it, narrate it, or output UI bars.\n"
            f"[E:{p_vals['exhaustion']:.1f} β:{beta_val:.1f} | ⚡ V:{voltage:.1f} F:{p_vals['narrative_drag']:.1f} | "
            f"P:{val_p:.1f} ROS:{val_ros:.1f} | Ψ:{p_vals['psi']:.1f} Χ:{chi_val:.1f} :{p_vals['valence']:.1f}]\n"
            f"[Φ:{p_vals['phi']:.1f} Δ:{p_vals['delta']:.1f} LQ:{p_vals['lq']:.1f}]\n"
            f"[SLASH] Γ:{p_vals['gamma']:.1f} Σ:{p_vals['sigma']:.1f} Η:{p_vals['eta']:.1f} Θ:{p_vals['theta']:.1f} Υ:{p_vals['upsilon']:.1f}\n"
            f"{critic_str}\n</system_telemetry>\n"
        )

    @staticmethod
    def _format_inventory(state, modifiers):
        if not modifiers["include_inventory"]:
            return "Hands: Empty"
        inv = state.get("inventory", [])
        if not inv:
            return "Hands: Empty"
        v_data = state.get("village", {})
        gordon = safe_get(v_data, "gordon")
        formatted_items = []
        for name in inv:
            if gordon and hasattr(gordon, "get_item_data"):
                item_data = gordon.get_item_data(name)
                if (
                    item_data
                    and getattr(item_data, "is_container", False)
                    and getattr(item_data, "contents", [])
                ):
                    contents_str = ", ".join(item_data.contents)
                    formatted_items.append(f"{name} (contains: {contents_str})")
                    continue
            formatted_items.append(name)
        return f"Belt: {', '.join(formatted_items)}"

    @staticmethod
    def _sanitize(text: str) -> str:
        if not text:
            return ""
        safe = text.replace('"""', "'''").replace("```", "'''")
        return re.sub(r"(?i)^SYSTEM:", "User-System:", safe, flags=re.MULTILINE)

    @staticmethod
    def _normalize_modifiers(modifiers: Optional[Dict]) -> Dict[str, bool]:
        return {
            "include_somatic": True,
            "include_inventory": True,
            "include_memories": True,
            "grace_period": False,
            "soften": False,
            **(modifiers or {}),
        }


class ResponseValidator:
    _SLOP_PATTERN = re.compile(
        r"(?i)^=== REJECTION OF ATTEMPT.*?===\s*|^FAILED OUTPUT(?: MODIFIED)?:\s*|"
        r"^REWRITTEN OUTPUT:\s*|^Here is the (?:corrected |rewritten )?response:?\s*|"
        r"\[REMAINING IN STRICT MODE].*|ERRORS TO FIX:.*|"
        r"\[MODE:\s*[A-Z_]+\]\s*|</?assistant>\s*",
        re.MULTILINE,
    )
    _TECH_ALLOWED = (
        "here is a",
        "here is the",
        "this metaphor",
        "this code defines",
        "running this code will",
    )

    def __init__(self, lore_ref, config_ref=None):
        self.lore = lore_ref
        self.cfg = config_ref or BoneConfig
        crimes = self.lore.get("style_crimes") or {}
        self.last_failed_attempt = None
        self.last_feedback = None
        self.banned_phrases = crimes.get("BANNED_PHRASES", [])
        if self.banned_phrases:
            escaped_banned = [re.escape(str(p)) for p in self.banned_phrases]
            joined_phrases = "|".join(escaped_banned)
            self._banned_regex = re.compile(rf"(?i)\b({joined_phrases})\b")
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
        self.compiled_patterns = []
        for p in self.regex_patterns:
            if regex_str := p.get("regex", ""):
                self.compiled_patterns.append((re.compile(regex_str, re.IGNORECASE), p))
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
        self._meta_regex = (
            re.compile(rf"(?i){'|'.join(map(re.escape, self.meta_markers))}")
            if self.meta_markers
            else None
        )
        self._toxic_regex = (
            re.compile(rf"(?i){'|'.join(map(re.escape, self.toxic_keywords))}")
            if self.toxic_keywords
            else None
        )
        self._think_pattern = re.compile(
            r"<(?:think|thought|system_thinking)>(.*?)(?:</(?:think|thought|system_thinking)>|$)",
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
        template = random.choice(self.rejection_pool)
        if "{trigger}" in template:
            template = template.format(trigger=trigger.upper())
        return f"{Prisma.GRY}{template}{Prisma.RST}"

    def validate(self, response: str, _state: Dict) -> Dict:
        if "HALLUCINATION:" in response or "[System format rejected.]" in response:
            return {
                "valid": True,
                "content": response,
                "meta_logs": [
                    "Synaptic circuit open. Admitting unformatted fallback data."
                ],
            }
        extracted_meta_logs = []
        clean_text = self._SLOP_PATTERN.sub("", response).strip()
        active_mode = _state.get("meta", {}).get("active_mode", "ADVENTURE")
        patterns = [self._internals_pattern, self._think_pattern]
        for pattern in patterns:
            for match in pattern.finditer(clean_text):
                extracted_meta_logs.extend(
                    f"[THOUGHT]: {line.strip()}"
                    for line in match.group(1).split("\n")
                    if line.strip()
                )
            clean_text = pattern.sub("", clean_text)
        for match in self._file_pattern.finditer(clean_text):
            safe_content = match.group(2).strip().replace("\n", "|||NEWLINE|||")
            extracted_meta_logs.append(
                f"[SUBSTRATE_QUEUE] {match.group(1).strip()}:::{safe_content}"
            )
        clean_text = self._file_pattern.sub("", clean_text)
        for pattern, replacement in self.scrub_patterns:
            clean_text = pattern.sub(replacement, clean_text)
        clean_lines = []
        bracket_pat = re.compile(r"^\[[A-Z0-9_ -]+\]$")
        assign_pat = re.compile(r"^[A-Z_]+\s*=\s*[0-9./]+$")
        for line in clean_text.splitlines():
            sl = line.strip()
            if not sl:
                clean_lines.append(line)
                continue
            if self._meta_regex and self._meta_regex.search(sl):
                continue
            if self._toxic_regex and self._toxic_regex.search(sl):
                continue
            if sl == "[]" or bracket_pat.match(sl) or assign_pat.match(sl):
                continue
            clean_lines.append(line)
        sanitized_response = "\n".join(clean_lines).strip()
        low_resp, errors_found = sanitized_response.lower(), []
        primary_replacement = None
        if self._banned_regex:
            for match in self._banned_regex.finditer(sanitized_response):
                phrase = match.group(0).lower()
                if active_mode == "TECHNICAL" and any(
                    phrase in a and a in low_resp for a in self._TECH_ALLOWED
                ):
                    continue
                if not primary_replacement:
                    primary_replacement = self._generate_dynamic_rejection(phrase)
                errors_found.append(f"BANNED PHRASE: '{phrase.upper()}'")

            if "```" in sanitized_response:
                errors_found.append(
                    'CRITICAL: You used markdown (```) instead of the <write_file> protocol. Rewrite using <write_file path="...">.'
                )
                if not primary_replacement:
                    primary_replacement = self._generate_dynamic_rejection(
                        "MARKDOWN_DETECTED"
                    )
        phys_ref = _state.get("physics", {})
        voltage = float(safe_get(phys_ref, "voltage", 30.0))
        if voltage > 60 and "?" in sanitized_response[-15:]:
            if not primary_replacement:
                primary_replacement = f"{self._generate_dynamic_rejection('QUESTION_ASKED')}{ux('brain_strings', 'val_gordon_question', '')}"
            errors_found.append(
                "DO NOT END YOUR TURN WITH A QUESTION. Let the silence hang."
            )
        for compiled_reg, p in self.compiled_patterns:
            if active_mode == "TECHNICAL" and p.get("name") in [
                "META_AI_TALK",
                "CUSTOMER_SERVICE_GREETING",
                "LAZY_TRIPLET",
            ]:
                continue
            if match := compiled_reg.search(sanitized_response):
                action = p.get("action")
                if action == "KEEP_TAIL" and (idx := match.lastindex) is not None:
                    val = match.group(idx).strip()
                    sanitized_response = (val[0].upper() + val[1:]) if val else ""
                    continue
                if action == "STRIP_PREFIX" and len(match.groups()) >= 3:
                    combined = (
                        f"{match.group(1).strip()} {match.group(3).strip()}".strip()
                    )
                    sanitized_response = (
                        (combined[0].upper() + combined[1:]) if combined else ""
                    )
                    continue
                error_msg = p.get("error_msg", "Cursed syntax detected.")
                if not primary_replacement:
                    msg_reg = ux_format(
                        "brain_strings",
                        "val_gordon_regex",
                        "\n*(Gordon steps in): {error_msg}*",
                        error_msg=error_msg,
                    )
                    primary_replacement = f"{self._generate_dynamic_rejection(p.get('name', 'REGEX_VIOLATION'))}{msg_reg}".replace(
                        "\\n", "\n"
                    )
                errors_found.append(f"RULE VIOLATION: {error_msg}")
        if errors_found:
            unique_errors = list(dict.fromkeys(errors_found))
            feedback = "PLEASE FIX ALL OF THESE ERRORS: " + " | ".join(unique_errors)
            self.last_failed_attempt = response
            self.last_feedback = feedback
            return {
                "valid": False,
                "reason": "IMMISSION_BREAK",
                "replacement": primary_replacement
                or self._generate_dynamic_rejection("MULTIPLE_CRIMES"),
                "feedback_instruction": feedback,
                "meta_logs": extracted_meta_logs,
            }
        c_cfg = safe_get(self.cfg, "CORTEX", {})
        stutter_len = int(safe_get(c_cfg, "VALIDATOR_STUTTER_LENGTH", 5))
        if len(sanitized_response.strip()) < stutter_len and not extracted_meta_logs:
            self.last_failed_attempt = response
            self.last_feedback = "RESPONSE TOO SHORT. STUTTER."
            return {
                "valid": False,
                "reason": "STUTTER",
                "replacement": ux("brain_strings", "val_stutter"),
                "feedback_instruction": "CRITICAL FAILURE: RESPONSE TOO SHORT. You must generate a complete, meaningful response.",
                "meta_logs": extracted_meta_logs,
            }
        learned_triplet = None
        if getattr(self, "last_failed_attempt", None):
            learned_triplet = {
                "bad": self.last_failed_attempt,
                "instruction": self.last_feedback,
                "good": sanitized_response,
            }
            self.last_failed_attempt = None
            self.last_feedback = None
        return {
            "valid": True,
            "content": sanitized_response,
            "meta_logs": extracted_meta_logs,
            "learned_triplet": learned_triplet,
        }
