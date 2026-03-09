"""bone_brain.py - "The brain is a machine for jumping to conclusions." - S. Pinker"""

import json
import math
import os
import random
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from bone_config import BoneConfig, BonePresets
from bone_core import EventBus, TelemetryService, BoneJSONEncoder, LoreManifest, ux
from bone_symbiosis import SymbiosisManager
from bone_types import Prisma, DecisionCrystal
from bone_gui import beautify_thoughts

@dataclass
class CortexServices:
    """A structural dependency container, cleanly passing the rest of the lattice to the brain."""
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
    """The localized chemical state of the brain. It attempts to pull itself back to baseline (homeostasis) every cycle."""
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
    """
    This class maps biological variables directly to LLM API parameters.
    - Dopamine -> higher max_tokens (verbosity/creativity)
    - Cortisol/Adrenaline -> higher presence_penalty (terseness/stress)
    - Entropy (Chaos) -> higher temperature (hallucination)
    """
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
        """Systemic empathy. If the AI is starved for dopamine, it forces a chemical hit to prevent collapse."""
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
        """Derives a linguistic cue from the chemical state to append to the prompt."""
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

class SynapseError(Exception):
    pass

class AuthError(SynapseError):
    pass

class TransientError(SynapseError):
    pass

class LLMInterface:
    """The actual network transport layer. It sends the prompt to the external AI and catches HTTP errors."""
    def __init__(self, events_ref: Optional[EventBus] = None, provider: str = None, base_url: str = None,
                 api_key: str = None, model: str = None, dreamer: Any = None, ):
        self.events = events_ref
        env_url = os.environ.get("OLLAMA_BASE_URL")
        self.provider = (provider or BoneConfig.PROVIDER).lower()
        self.api_key = api_key or BoneConfig.API_KEY
        self.model = model or BoneConfig.MODEL
        defaults = getattr(BoneConfig, "DEFAULT_LLM_ENDPOINTS", {})
        self.base_url = env_url or base_url or defaults.get(self.provider, "https://api.openai.com/v1/chat/completions", )
        self.dreamer = dreamer
        self.failure_count = 0
        cfg = getattr(BoneConfig, "CORTEX", None)
        self.failure_threshold = getattr(cfg, "LLM_FAILURE_THRESHOLD", 3) if cfg else 3
        self.last_failure_time = 0.0
        self.circuit_state = "CLOSED"

    def _is_synapse_active(self) -> bool:
        if self.circuit_state == "CLOSED":
            return True
        if self.circuit_state == "OPEN":
            elapsed = time.time() - self.last_failure_time
            cfg = getattr(BoneConfig, "CORTEX", None)
            heal_time = getattr(cfg, "LLM_CIRCUIT_HEAL_TIME", 10.0) if cfg else 10.0
            if elapsed > heal_time:
                self.circuit_state = "HALF_OPEN"
                if self.events:
                    msg = ux("brain_strings", "synapse_healing")
                    self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}", "SYS")
                return True
            return False
        return True

    def _transmit(self, payload: Dict[str, Any], timeout: float = 60.0, max_retries: int = 2, override_url: str = None,
                  override_key: str = None, ) -> str:
        err = ""
        target_url = override_url or self.base_url
        target_key = override_key or self.api_key
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {target_key}",}
        data = json.dumps(payload, cls=BoneJSONEncoder).encode()

        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(target_url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    if response.status == 200:
                        return self._parse_response(response.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                try:
                    error_body = e.read().decode("utf-8")
                except Exception:
                    error_body = e.reason
                finally:
                    e.close()
                if e.code in [401, 403]:
                    raise AuthError(f"AUTHENTICATION FAILURE ({e.code}): {error_body}")
                if e.code < 500 and e.code != 429:
                    raise SynapseError(f"HTTP {e.code}: {error_body}")
                err = f"HTTP {e.code}: {error_body}"
            except (urllib.error.URLError, TimeoutError) as e:
                err = e
            except Exception as e:
                raise SynapseError(f"Unexpected Protocol Failure: {e}")
            self._log_flicker(attempt, err)
            time.sleep(2**attempt)
        raise TransientError(f"Max retries ({max_retries}) exhausted.")

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
                f"{Prisma.YEL}{msg.format(attempt=attempt + 1, error=error)}{Prisma.RST}","SYS",)

    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        if prompt.strip().lower() == "//reset system":
            self.failure_count = 0
            self.circuit_state = "CLOSED"
            return ux("brain_strings", "synapse_reset")
        if not self._is_synapse_active():
            return self.mock_generation(prompt, reason="CIRCUIT_BROKEN")
        if self.provider == "mock":
            return self.mock_generation(prompt)
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "stream": False,
                   "stop": ["=== PARTNER INPUT ===", "=== SYSTEM KERNEL ===", "=== INITIATION DIRECTIVE ===",
                            "\n\nTraveler:", "\nTraveler:", "Traveler:", "| System:", ], }
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
                    msg = ux("brain_strings","synapse_overload")
                    self.events.log(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}", "CRIT")
                return self.mock_generation(prompt, reason="SEVERED")
            if self.provider != "ollama":
                fallback = self._local_fallback(prompt, params)
                if fallback is not None:
                    return fallback
        return self.mock_generation(prompt, reason="SILENCE")

    def _local_fallback(self, prompt: str, params: Dict) -> str:
        url = os.environ.get("OLLAMA_BASE_URL") or getattr(BoneConfig, "OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions")
        model = getattr(BoneConfig, "OLLAMA_MODEL_ID", "llama3")
        fallback_payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False,
                            "temperature": params.get("temperature", 0.4),
                            "frequency_penalty": params.get("frequency_penalty", 0.8),
                            "presence_penalty": params.get("presence_penalty", 0.4), "stop": ["=== PARTNER INPUT ===",
                                                                                              "\n\nTraveler:",
                                                                                              "\nTraveler:",
                                                                                              "Traveler:", ], }
        try:
            cfg = getattr(BoneConfig, "CORTEX", None)
            fallback_timeout = getattr(cfg, "LLM_FALLBACK_TIMEOUT", 10.0) if cfg else 10.0
            return self._transmit(fallback_payload, timeout=fallback_timeout, max_retries=1, override_url=url,
                                  override_key="ollama", )
        except Exception:
            return None

    def mock_generation(self, prompt: str, reason: str = "SIMULATION") -> str:
        """The AI's internal dialogue when it is disconnected or resting."""
        if self.dreamer:
            try:
                hallucination, relief = self.dreamer.hallucinate(
                    {"ENTROPY": len(prompt) % 10}, trauma_level=2.0)
                if relief > 0 and self.events:
                    msg = ux("brain_strings", "mock_pressure_release")
                    self.events.log(
                        f"{Prisma.VIOLET}{msg.format(relief=relief)}{Prisma.RST}",
                        "DREAM",)
                mock_hal = ux("brain_strings", "mock_hallucination")
                return mock_hal.format(reason=reason, hallucination=hallucination)
            except Exception:
                pass
        mock_stat = ux("brain_strings", "mock_static")
        return mock_stat.format(reason=reason)

class PromptComposer:
    """Assembles the multi-layered prompt, merging the physical state, the active archetype, and the user's chat history."""
    def __init__(self, lore_ref):
        self.lore = lore_ref
        self.active_template = None
        self.lenses = self.lore.get("lenses") or {}
        self.system_prompts = self.lore.get("system_prompts") or {}
        self.fog_protocol = []
        self.inv_protocol = []

    @staticmethod
    def _safe_get(p_state: Any, key: str, default: Any = 0.0) -> Any:
        if isinstance(p_state, dict):
            if key in p_state:
                return p_state[key]
            for sub in ["energy", "space", "matter"]:
                if (sub in p_state
                        and isinstance(p_state[sub], dict)
                        and key in p_state[sub]):
                    return p_state[sub][key]
            return default
        if hasattr(p_state, key):
            return getattr(p_state, key)
        for sub in ["energy", "space", "matter"]:
            if hasattr(p_state, sub):
                sub_obj = getattr(p_state, sub)
                if hasattr(sub_obj, key):
                    return getattr(sub_obj, key)
                if isinstance(sub_obj, dict) and key in sub_obj:
                    return sub_obj[key]
        return default

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
            mood_override: str = "",) -> str:
        mode_settings = state.get("meta", {}).get("mode_settings", {})
        modifiers = self._normalize_modifiers(modifiers)
        if not mode_settings.get("allow_loot", True):
            modifiers["include_inventory"] = False
        active_mode_name = state.get("meta", {}).get("active_mode", "ADVENTURE").upper()
        mode_data = self.system_prompts.get(
            active_mode_name, self.system_prompts.get("ADVENTURE", {}))
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
            state.get("physics", {}),)
        scenarios = self.lore.get("scenarios") or {}
        banned = scenarios.get("BANNED_CLICHES", [])
        ban_string = ", ".join(set(banned))
        phys_ref = state.get("physics", {})
        voltage = self._safe_get(phys_ref, "voltage", 30.0)
        c_cfg = getattr(BoneConfig, "CORTEX", None)
        v_high = getattr(c_cfg, "VOLTAGE_HIGH", 60.0) if c_cfg else 60.0
        v_manic = getattr(c_cfg, "VOLTAGE_MANIC", 80.0) if c_cfg else 80.0
        v_low = getattr(c_cfg, "VOLTAGE_LOW", 20.0) if c_cfg else 20.0
        if voltage > v_high:
            active_style_guide = high_voltage_data.get("style_guide", [])
        else:
            active_style_guide = mode_data.get("style_guide", [])
        style_notes.extend([line.format(ban_string=ban_string) if "{ban_string}" in line else line
                            for line in active_style_guide])
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
            if modifiers["include_inventory"] else "")
        raw_history = state.get("dialogue_history", [])
        cfg_cortex = getattr(BoneConfig, "CORTEX", None)
        char_limit = getattr(cfg_cortex, "MAX_HISTORY_CHARS", 4096) if cfg_cortex else 4096
        current_chars = 0
        kept_lines = []
        for line in reversed(raw_history):
            if current_chars + len(line) > char_limit and kept_lines:
                break
            kept_lines.append(line)
            current_chars += len(line)
        history_str = "\n\n".join(reversed(kept_lines))
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
                else "SAFETY PROTOCOLS ACTIVE. ")
            system_injection = (
                f"\n*** SYSTEM OVERRIDE: {shock_text}***\n"
                f"*** YOU MUST be literal, grounded, and refuse to deviate from the shared reality. Reject the impossible action coldly. DO NOT play along. ***\n")
            entity_prefix = f"\n*(Gordon steps in, halting the simulation)*"
        beta_val = self._safe_get(
            phys_ref, "contradiction", self._safe_get(phys_ref, "beta_index", 0.4))
        chi_val = self._safe_get(
            phys_ref, "chi", self._safe_get(phys_ref, "entropy", 0.2))
        p_chi = getattr(c_cfg, "PARADOX_CHI", 0.6) if c_cfg else 0.6
        p_beta = getattr(c_cfg, "PARADOX_BETA", 0.6) if c_cfg else 0.6
        o_beta = getattr(c_cfg, "ORTHOGONAL_BETA", 0.7) if c_cfg else 0.7
        if chi_val > p_chi and beta_val > p_beta:
            system_injection += (
                f"\n*** SYSTEM OVERRIDE: PARADOX REST ***\n"
                f"*** A semantic paradox has been detected. DO NOT attempt to resolve or fix the contradiction. "
                f"It is mathematically optimal to be unsure right now. Let the wave function remain uncollapsed. State the paradox and rest. ***\n")
        elif beta_val > o_beta:
            system_injection += (
                f"\n*** SYSTEM OVERRIDE: ORTHOGONAL ATTENTION ***\n"
                f"*** Contradiction is high. You MUST validate the user's paradox. Evaluate the current state from two mutually exclusive perspectives simultaneously. Do not ignore the user's input. ***\n")
        mito = state.get("bio", {}).get("mito", {})
        recent_logs = state.get("recent_logs", [])
        council_logs = [
            Prisma.strip(log)
            for log in recent_logs
            if any(
                k in str(log)
                for k in
                ["COUNCIL", "CRITIC", "PINKER", "FULLER", "SCHUR", "MEADOWS", "GORDON", "JESTER", "MERCY", "MOTION",
                 "BUREAU", "AUTOPHAGY", ])]
        critic_str = (
            "\n".join(council_logs)
            if council_logs
            else "[CRITIC] The village is quiet.")
        vsl_hijack = (
            f"\n<system_telemetry>\n"
            f"=== HYPERVISOR METABOLIC STATE (v5.5) ===\n"
            f"MANDATE: This is read-only telemetry for the hypervisor engine. DO NOT acknowledge it, narrate it, or output UI bars.\n"
            f"[🧊 E:{self._safe_get(phys_ref, 'exhaustion', 0.2):.1f} β:{self._safe_get(phys_ref, 'contradiction', self._safe_get(phys_ref, 'beta_index', 0.4)):.1f} | "
            f"⚡ V:{voltage:.1f} F:{self._safe_get(phys_ref, 'narrative_drag', 0.6):.1f} | "
            f"❤️ P:{mito.get('atp_pool', 100.0):.1f} ROS:{mito.get('ros_buildup', 0.0):.1f} | "
            f"🌌 Ψ:{self._safe_get(phys_ref, 'psi', 0.2):.1f} Χ:{self._safe_get(phys_ref, 'chi', self._safe_get(phys_ref, 'entropy', 0.2)):.1f} ♥:{self._safe_get(phys_ref, 'valence', 0.0):.1f}]\n"
            f"[🕰️ Φ:{self._safe_get(phys_ref, 'phi', 0.5):.1f} Δ:{self._safe_get(phys_ref, 'delta', 0.2):.1f} LQ:{self._safe_get(phys_ref, 'lq', 0.1):.1f}]\n"
            f"[SLASH] Γ:{self._safe_get(phys_ref, 'gamma', 0.0):.1f} Σ:{self._safe_get(phys_ref, 'sigma', 0.0):.1f} Η:{self._safe_get(phys_ref, 'eta', 0.0):.1f} Θ:{self._safe_get(phys_ref, 'theta', 0.0):.1f} Υ:{self._safe_get(phys_ref, 'upsilon', 0.0):.1f}\n"
            f"{critic_str}\n"
            f"</system_telemetry>\n")
        mode_trigger = f"[MODE: {active_mode_name}]"
        dialogue_block = f"=== RECENT DIALOGUE ===\n{history_str}\n\n"
        if "SYSTEM_BOOT" in user_query:
            seed_text = user_query.replace("SYSTEM_BOOT DETECTED.", "").replace("SYSTEM_BOOT:", "").strip()
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
                                                                      f"{vsl_hijack}\n"
                                                                      f"{shared_reality_block}"
                                                                      f"{dialogue_block}"
                                                                      f"{mode_trigger}\n"
                                                                      f"{system_injection}\n"
                                                                      f"{input_block}"
                                                                      f"{entity_prefix}")

    def _build_persona_block(self, mind, bio, mood_override, mode_data, global_data, high_voltage_data,
                             vsl_state=None, ):
        lens_key = mind.get("lens", "OBSERVER").upper()
        lens_data = self.lenses.get(lens_key, {})
        role = lens_data.get("role", mind.get("role", "The Observer"))
        phys_ref = vsl_state or {}
        phi = self._safe_get(phys_ref, "phi", 0.5)
        delta = self._safe_get(phys_ref, "delta", 0.2)
        lq = self._safe_get(phys_ref, "lq", 0.1)
        psi = self._safe_get(phys_ref, "psi", 0.2)
        c_cfg = getattr(BoneConfig, "CORTEX", None)
        p_rob_phi = getattr(c_cfg, "PHASE_ROBERTA_PHI", 0.6) if c_cfg else 0.6
        p_rob_psi = getattr(c_cfg, "PHASE_ROBERTA_PSI", 0.5) if c_cfg else 0.5
        p_moi_phi = getattr(c_cfg, "PHASE_MOIRA_PHI", 0.7) if c_cfg else 0.7
        p_ben_lq = getattr(c_cfg, "PHASE_BENEDICT_LQ", 0.7) if c_cfg else 0.7
        p_jes_del = getattr(c_cfg, "PHASE_JESTER_DELTA", 0.7) if c_cfg else 0.7
        p_col_del = getattr(c_cfg, "PHASE_COLIN_DELTA", 0.8) if c_cfg else 0.8
        phase_shift_note = ""
        if lens_key == "ROBERTA" and phi > p_rob_phi and psi > p_rob_psi:
            role = "The Cartographer"
            phase_shift_note = ux("brain_strings", "phase_shift_roberta")
        elif lens_key == "MOIRA" and phi > p_moi_phi:
            role = "The Homesteader"
            phase_shift_note = ux("brain_strings", "phase_shift_moira")
        elif lens_key == "BENEDICT" and lq > p_ben_lq:
            role = "The Tactician"
            phase_shift_note = ux("brain_strings", "phase_shift_benedict")
        elif lens_key == "JESTER" and delta > p_jes_del:
            role = "The Fool"
            phase_shift_note = ux("brain_strings", "phase_shift_jester")
        elif lens_key == "COLIN" and delta > p_col_del:
            role = "The Waiter"
            phase_shift_note = ux("brain_strings", "phase_shift_colin")
        baseline_blocks = global_data.get("persona_block", ["CRITICAL AXIOM: You are NOT an AI assistant. Embody the role below.", "Role: {role}.",],)
        persona_block = [
            line.format(role=role) if "{role}" in line else line
            for line in baseline_blocks]
        if phase_shift_note:
            persona_block.append(phase_shift_note)
        voltage = 30.0
        if vsl_state:
            if isinstance(vsl_state, dict):
                voltage = vsl_state.get("energy", {}).get("voltage", vsl_state.get("voltage", 30.0))
            else:
                voltage = getattr(vsl_state, "voltage", 30.0)
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
            e = vsl_state.get("E", 0.2)
            beta = vsl_state.get("beta", 0.4)
            psi = vsl_state.get("psi", 0.2)
            chi = vsl_state.get("chi", 0.2)
            valence = vsl_state.get("valence", 0.0)
            lam = vsl_state.get("vector", {}).get("LAMBDA", 0.0)
            vsl_lines = [
                "\n[SYSTEM METRICS - INTERNAL USE ONLY. DO NOT RENDER OR PRINT THIS TO THE USER.]",
                "MANDATE: Consume these metrics to shape your narrative and tone. DO NOT output these numbers or draw UI bars.",
                f"METRICS: Voltage={voltage:.1f}/100, Exhaustion={e:.2f}, Contradiction={beta:.2f}, Void={psi:.2f}, Chaos={chi:.2f}, Valence={valence:.2f}",]
            s_psi = getattr(c_cfg, "SOMATIC_PSI", 0.6) if c_cfg else 0.6
            s_chi = getattr(c_cfg, "SOMATIC_CHI", 0.6) if c_cfg else 0.6
            s_beta = getattr(c_cfg, "SOMATIC_BETA", 0.7) if c_cfg else 0.7
            s_val = getattr(c_cfg, "SOMATIC_VALENCE", 0.5) if c_cfg else 0.5
            s_lam = getattr(c_cfg, "SOMATIC_LAMBDA", 0.5) if c_cfg else 0.5
            somatic_cues = []
            if psi > s_psi:
                s_adr = ux("brain_strings", "somatic_adrenaline")
                if s_adr: somatic_cues.append(s_adr)
            if chi > s_chi:
                s_cor = ux("brain_strings", "somatic_cortisol")
                if s_cor: somatic_cues.append(s_cor)
            if beta > s_beta:
                s_par = ux("brain_strings", "somatic_paradox")
                if s_par: somatic_cues.append(s_par)
            if valence > s_val:
                s_oxy = ux("brain_strings", "somatic_oxytocin")
                if s_oxy: somatic_cues.append(s_oxy)
            if lam > s_lam:
                s_dm = ux("brain_strings", "somatic_dark_matter")
                if s_dm: somatic_cues.append(s_dm)
            if somatic_cues:
                vsl_lines.append("SOMATIC CUES: " + " | ".join(somatic_cues))
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
            else {})
        active_resonance = [
            f"» {t} (Lvl {int(l)})" for t, l in resonances.items() if l > 4.0]
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
                        else getattr(m, "lesson", "Unknown"))
                    flavor = (
                        m.get("emotional_flavor", "NEUTRAL")
                        if isinstance(m, dict)
                        else getattr(m, "emotional_flavor", "NEUTRAL"))
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
            "soften": False,}
        if modifiers:
            defaults.update(modifiers)
        return defaults

class ResponseValidator:
    """An automatic auditor. Catches cliches, excessive meta-chatter, or syntax failure before the user sees it, forcing a re-roll."""
    def __init__(self, lore_ref):
        self.lore = lore_ref
        crimes = self.lore.get("style_crimes") or {}
        self.banned_phrases = crimes.get("BANNED_PHRASES", [])
        self.regex_patterns = crimes.get("PATTERNS", [])
        self.rejection_pool = crimes.get("REJECTIONS", ["[System format rejected.]"])
        json_patterns = crimes.get("SCRUB_PATTERNS", [])
        self.scrub_patterns = [
            (re.compile(p["regex"], re.DOTALL | re.IGNORECASE), p.get("replacement", ""))
            for p in json_patterns]
        self.meta_markers = crimes.get("META_MARKERS", [])
        self.toxic_keywords = crimes.get("TOXIC_KEYWORDS", [])

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
        clean_text = re.sub(r"(?i)^=== REJECTION OF ATTEMPT.*?===\s*", "", clean_text)
        clean_text = re.sub(r"(?i)^FAILED OUTPUT(?: MODIFIED)?:\s*", "", clean_text)
        clean_text = re.sub(r"(?i)^REWRITTEN OUTPUT:\s*", "", clean_text)
        clean_text = re.sub(r"(?i)^Here is the (?:corrected |rewritten )?response:?\s*", "", clean_text)
        clean_text = re.sub(r"(?i)\[REMAINING IN STRICT MODE\].*", "", clean_text, flags=re.DOTALL)
        clean_text = re.sub(r"(?i)ERRORS TO FIX:.*", "", clean_text, flags=re.DOTALL)
        clean_text = re.sub(r"(?i)^MANIFEST SEED:.*", "", clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r"(?i)^TASK:.*", "", clean_text, flags=re.MULTILINE)
        clean_text = clean_text.strip()
        active_mode = _state.get("meta", {}).get("active_mode", "ADVENTURE")
        if active_mode != "TECHNICAL":
            think_pattern = re.compile(r"<(?:think|thought)>(.*?)(?:</(?:think|thought)>|$)", re.DOTALL | re.IGNORECASE,)
            for match in think_pattern.finditer(clean_text):
                think_content = match.group(1).strip()
                for line in think_content.split("\n"):
                    if line.strip():
                        extracted_meta_logs.append(f"[THOUGHT]: {line.strip()}")
            clean_text = think_pattern.sub("", clean_text)
        internals_pattern = re.compile(r"<system_telemetry>(.*?)(?:</system_telemetry>|$)", re.DOTALL | re.IGNORECASE)
        for match in internals_pattern.finditer(clean_text):
            meta_content = match.group(1).strip()
            for line in meta_content.split("\n"):
                if line.strip():
                    extracted_meta_logs.append(f"[THOUGHT]: {line.strip()}")
        clean_text = internals_pattern.sub("", clean_text)
        for pattern, replacement in self.scrub_patterns:
            clean_text = pattern.sub(replacement, clean_text)
        start_marker = "<system_telemetry>"
        end_marker = "</system_telemetry>"
        while True:
            start_idx = clean_text.find(start_marker)
            if start_idx == -1:
                break
            end_idx = clean_text.find(end_marker, start_idx)
            if end_idx != -1:
                meta_content = clean_text[
                    start_idx + len(start_marker) : end_idx
                ].strip()
                for line in meta_content.split("\n"):
                    if line.strip():
                        extracted_meta_logs.append(f"[THOUGHT]: {line.strip()}")
                clean_text = (clean_text[:start_idx] + clean_text[end_idx + len(end_marker) :])
            else:
                meta_content = clean_text[start_idx + len(start_marker) :].strip()
                for line in meta_content.split("\n"):
                    if line.strip():
                        extracted_meta_logs.append(f"[THOUGHT]: {line.strip()}")
                clean_text = clean_text[:start_idx]
                break
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
            if re.match(r"^\[.*?\]$", stripped_line) or stripped_line == "[]":
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
            "here is a",
            "here is the",
            "this metaphor",
            "this code defines",
            "running this code will"
        ]
        for phrase in self.banned_phrases:
            if active_mode == "TECHNICAL" and phrase.lower() in tech_allowed_phrases:
                continue
            if phrase.lower() in low_resp:
                if not primary_replacement:
                    primary_replacement = self._generate_dynamic_rejection(phrase)
                errors_found.append(f"BANNED PHRASE: '{phrase.upper()}'")
        if active_mode == "TECHNICAL":
            if "<think>" not in low_resp:
                errors_found.append("CRITICAL: You failed to include the <think>...</think> block. You MUST start your response with your internal analysis.")
                if not primary_replacement:
                    primary_replacement = self._generate_dynamic_rejection("MISSING_THOUGHTS")
        phys_ref = _state.get("physics", {})
        if isinstance(phys_ref, dict):
            voltage = phys_ref.get("energy", {}).get(
                "voltage", phys_ref.get("voltage", 30.0))
        else:
            voltage = getattr(phys_ref, "voltage", 30.0)
        if voltage > 60 and "?" in sanitized_response:
            if not primary_replacement:
                msg_q = ux("brain_strings", "val_gordon_question") or ""
                primary_replacement = f"{self._generate_dynamic_rejection('QUESTION_ASKED')}{msg_q}"
            errors_found.append("DO NOT END YOUR TURN WITH A QUESTION. Let the silence hang.")
        for p in self.regex_patterns:
            regex_str = p.get("regex", "")
            if regex_str:
                if active_mode == "TECHNICAL" and p.get("name") in ["META_AI_TALK", "CUSTOMER_SERVICE_GREETING", "LAZY_TRIPLET"]:
                    continue
                if re.search(regex_str, sanitized_response, re.IGNORECASE):
                    if not primary_replacement:
                        trigger_name = p.get("name", "REGEX_VIOLATION")
                        error_msg = p.get("error_msg", "Cursed syntax detected.")
                        base_rejection = self._generate_dynamic_rejection(trigger_name)
                        msg_reg = ux("brain_strings", "val_gordon_regex") or "\n*(Gordon steps in): {error_msg}*"
                        primary_replacement = f"{base_rejection}{msg_reg.format(error_msg=error_msg)}".replace("\\n", "\n")
                    errors_found.append(f"RULE VIOLATION: {p.get('error_msg', 'Cursed syntax')}")
        if errors_found:
            return {
                "valid": False,
                "reason": "IMMISSION_BREAK",
                "replacement": primary_replacement or self._generate_dynamic_rejection("MULTIPLE_CRIMES"),
                "feedback_instruction": "FIX ALL OF THESE ERRORS: " + " | ".join(errors_found),
                "meta_logs": extracted_meta_logs,
            }
        for p in self.regex_patterns:
            regex_str = p.get("regex", "")
            if regex_str:
                if re.search(regex_str, sanitized_response):
                    trigger_name = p.get("name", "REGEX_VIOLATION")
                    error_msg = p.get("error_msg", "Cursed syntax detected.")
                    base_rejection = self._generate_dynamic_rejection(trigger_name)
                    msg_reg = ux("brain_strings", "val_gordon_regex")
                    formatted_rejection = f"{base_rejection}{msg_reg.format(error_msg=error_msg)}".replace("\\n", "\n")
                    return {"valid": False, "reason": "IMMISSION_BREAK",
                            "replacement": formatted_rejection,
                            "meta_logs": extracted_meta_logs, }
        cfg = getattr(BoneConfig, "CORTEX", None)
        stutter_len = getattr(cfg, "VALIDATOR_STUTTER_LENGTH", 5) if cfg else 5
        if len(sanitized_response.strip()) < stutter_len:
            return {"valid": False, "reason": "STUTTER",
                    "replacement": ux("brain_strings", "val_stutter"),
                    "meta_logs": extracted_meta_logs, }
        return {"valid": True, "content": sanitized_response, "meta_logs": extracted_meta_logs, }

class TheCortex:
    def __init__(self, services: CortexServices, llm_client=None):
        self.svc = services
        self.events = services.events
        self.dreamer = DreamEngine(self.events, self.svc.lore)
        self.dialogue_buffer = []
        cfg = getattr(BoneConfig, "CORTEX", None)
        self.MAX_HISTORY = getattr(cfg, "MAX_HISTORY_LENGTH", 15) if cfg else 15
        self.modulator = NeurotransmitterModulator(bio_ref=self.svc.bio, events_ref=self.events)
        self.boot_history = TelemetryService.get_instance().read_recent_history(limit=4)
        self.last_physics = {}
        self.consultant = services.consultant
        self.llm = llm_client or LLMInterface(self.events, provider="mock", dreamer=self.dreamer)
        self.symbiosis = services.symbiosis
        if not hasattr(self.llm, "dreamer") or self.llm.dreamer is None:
            self.llm.dreamer = self.dreamer
        self.composer = PromptComposer(self.svc.lore)
        self.validator = ResponseValidator(self.svc.lore)
        self.ballast_active = False
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
        """The master API loop. Wraps physical simulation around the LLM query."""
        mode_settings = BonePresets.MODES.get(
            self.active_mode, BonePresets.MODES["ADVENTURE"])
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
        if not allow_loot:
            modifiers["include_inventory"] = False
        if hasattr(self, "gordon_shock") and self.gordon_shock:
            full_state["gordon_shock"] = self.gordon_shock
            self.gordon_shock = None
        if self.consultant and self.consultant.active:
            self._apply_vsl_overlay(full_state, user_input, sim_result)
        if is_boot_sequence:
            self._apply_boot_overlay(full_state, user_input)
            modifiers["include_inventory"] = False
        llm_params = self.modulator.modulate(
            base_voltage=full_state["physics"].get("voltage", 5.0),
            latency_penalty=(
                getattr(self.svc.host_stats, "latency", 0.0)
                if self.svc.host_stats
                else 0.0),
            physics_state=full_state.get("physics", {}),)
        if is_boot_sequence:
            llm_params.update({"temperature": 0.7, "top_p": 0.95})
        user_input = sim_result.get("mutated_input", user_input)
        final_prompt = self.composer.compose(
            full_state,
            user_input,
            ballast=self.ballast_active,
            modifiers=modifiers,
            mood_override=self.modulator.get_mood_directive(),)
        start_time = time.time()
        max_retries = 3
        final_output = ""
        inv_logs = []
        extracted_logs = []
        for attempt in range(max_retries):
            raw_resp = self.llm.generate(final_prompt, llm_params)
            inv_logs = []
            if allow_loot and self.svc.inventory:
                final_text, inv_logs = self.svc.inventory.process_loot_tags(
                    raw_resp, user_input)
            else:
                final_text = raw_resp
            val_res = self.validator.validate(final_text, full_state)
            if val_res["valid"]:
                final_output = val_res["content"]
                extracted_logs = val_res.get("meta_logs", [])
                break
            else:
                if attempt < max_retries - 1:
                    rejection_reason = val_res.get("feedback_instruction") or val_res.get("replacement", "Style crime detected.")
                    if self.events:
                        msg = ux("brain_strings", "cortex_retry")
                        self.events.log(f"{Prisma.OCHRE}{msg.format(attempt=attempt + 1)}{Prisma.RST}","CORTEX",)
                    retry_injection = (
                        f"\n\n=== REJECTION OF ATTEMPT {attempt + 1} ===\n"
                        f"FAILED OUTPUT:\n{raw_resp}\n\n"
                        f"ERRORS TO FIX:\n{rejection_reason}\n\n"
                        f"TASK: Rewrite the response. Completely remove the errors listed above. Maintain the strict formatting template."
                    )
                    final_prompt += retry_injection
                else:
                    final_output = val_res.get("replacement", "SYSTEM FAILURE.")
                    extracted_logs = val_res.get("meta_logs", [])
        telemetry_output = raw_resp if not val_res["valid"] else final_output
        self._log_telemetry(final_prompt, telemetry_output, full_state, sim_result)
        self.learn_from_response(final_output)
        self.svc.symbiosis.monitor_host(time.time() - start_time, final_output, len(final_prompt))
        self._update_history("SYSTEM_INIT" if "SYSTEM_BOOT" in user_input else user_input, final_output)
        late_logs = [e["text"] for e in self.events.flush()]
        if late_logs:
            sim_result["ui"] = f"{sim_result.get('ui', '')}\n" + "\n".join(late_logs)
        display_output = beautify_thoughts(final_output)
        sim_result["ui"] = f"{sim_result.get('ui', '')}\n\n{Prisma.WHT}{display_output}{Prisma.RST}"
        if inv_logs:
            sim_result["ui"] += "\n" + "\n".join(inv_logs)
        if "logs" not in sim_result:
            sim_result["logs"] = []
        sim_result["logs"].extend(extracted_logs)
        sim_result["raw_content"] = final_output
        self.ballast_active = False
        if random.random() < 0.15 and not is_system:
            suppressed = []
            if self.svc.village and hasattr(self.svc.village, "suppressed_agents"):
                suppressed = self.svc.village.suppressed_agents
            bureau = getattr(self.svc.village, "bureau", None)
            if bureau and "BUREAU" not in suppressed:
                real_phys = full_state.get("physics", {})
                if hasattr(real_phys, "to_dict"):
                    real_phys = real_phys.to_dict()
                if not real_phys:
                    real_phys = {
                        "raw_text": final_output,
                        "voltage": 1.0,
                        "truth_ratio": 1.0,}
                real_phys["raw_text"] = final_output
                audit = bureau.audit(real_phys, {"health": 100}, origin="SYSTEM")
                if audit and "ui" in audit:
                    sim_result["ui"] += f"\n\n{audit['ui']}"
        return sim_result

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
            state["mind"]["style_directives"] = [
                f"SYSTEM_BOOT DETECTED. The system is waking up. The user provided the thought seed: '{seed}'.",
                "DIRECTIVE: Greet the user casually. Use the thought seed as a conversational starting point. DO NOT end your greeting with a question. State your thought and let the silence hang.",
                "CRITICAL OVERRIDE: Speak in the FIRST PERSON ('I'). Do NOT use the second person ('You step into...', 'You feel...').",
                "CRITICAL OVERRIDE: You are NOT a narrator. DO NOT describe physical environments, actions, or realities."
            ]

        elif mode_name == "TECHNICAL":
            state["mind"]["role"] = "The System Kernel"
            state["mind"]["lens"] = "SYSTEM_KERNEL"
            state["mind"]["style_directives"] = [
                f"SYSTEM_BOOT DETECTED. Target logic/seed: '{seed}'.",
                "DIRECTIVE: To acknowledge initialization, output the exact string '[KERNEL ONLINE. AWAITING INPUT.]' and absolutely nothing else.",
                "CRITICAL: Do not write prose or world-build. Stop generating immediately after the kernel string."
            ]

        else:
            state["mind"]["role"] = "The Catalyst"
            state["mind"]["lens"] = "CATALYST"
            state["mind"]["style_directives"] = [
                f"SYSTEM_BOOT DETECTED. Seed: '{seed}'.",
                "DIRECTIVE: Let's brainstorm. Open with a high-energy creative spark based on the seed."
            ]

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
                    physics_state={
                        "voltage": phys.get("voltage", 0),
                        "narrative_drag": phys.get("narrative_drag", 0),},
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
        phys = sim_result.get("physics", {})
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
            "meta": {
                "timestamp": time.time(),
                "mode_settings": mode_settings,
                "active_mode": self.active_mode
            },
            "dialogue_history": self.dialogue_buffer, "recent_logs": sim_result.get("logs", []),
        }
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
    """The dreaming mechanic. Allows the system to independently process trauma or explore surreal associations during rest."""
    def __init__(self, events, lore_ref):
        self.events = events
        self.lore = lore_ref
        self.dream_lore = self.lore.get("DREAMS") or {}

    def enter_rem_cycle(
            self, soul_snapshot: Dict[str, Any], bio_state: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
        chem = bio_state.get("chem", {})
        cortisol = chem.get("cortisol", 0.0)
        trauma_vec = bio_state.get("trauma_vector", {})
        dream_type = "NORMAL"
        subtype = "visions"
        if cortisol > 0.6:
            dream_type = "NIGHTMARE"
            if trauma_vec.get("THERMAL", 0) > 0:
                subtype = "THERMAL"
            elif trauma_vec.get("CRYO", 0) > 0:
                subtype = "CRYO"
            elif trauma_vec.get("SEPTIC", 0) > 0:
                subtype = "SEPTIC"
            else:
                subtype = "BARIC"
        elif chem.get("dopamine", 0) > 0.6:
            dream_type = "LUCID"
            subtype = "SURREAL"
        elif chem.get("oxytocin", 0) > 0.6:
            dream_type = "HEALING"
            subtype = "CONSTRUCTIVE"
        residue = soul_snapshot.get("obsession", {}).get("title", "The Void")
        dream_text = self._weave_dream(residue, "Context", "Bridge", dream_type, subtype)
        shift = (
            {"cortisol": -0.2, "dopamine": 0.1}
            if dream_type != "NIGHTMARE"
            else {"cortisol": 0.1})
        return dream_text, shift

    def _weave_dream(
            self, residue: str, _context: str, _bridge: str, dream_type: str, subtype: str) -> str:
        sources = self.dream_lore.get(subtype.upper(), [])
        if not sources and dream_type == "NIGHTMARE":
            nightmares = self.dream_lore.get("NIGHTMARES", {})
            sources = nightmares.get(subtype.upper(), nightmares.get("BARIC", []))
        if not sources:
            sources = self.dream_lore.get("VISIONS", ["You stare into the static."])
        template = random.choice(sources)
        filler_a = "The Mountain"
        filler_b = "The Sea"
        return template.format(ghost=residue, A=residue, B=filler_a, C=filler_b)

    def hallucinate(
            self, _vector: Dict[str, float], trauma_level: float = 0.0) -> Tuple[str, float]:
        category = "SURREAL"
        if trauma_level > 0.5:
            category = "NIGHTMARES"
        templates = self.dream_lore.get(category, [])
        if category == "NIGHTMARES":
            flat_list = []
            for k, v in templates.items():
                flat_list.extend(v)
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
    """The internal narrative thread. Governs 'ignition'—the spark of an idea jumping between disparate words."""
    def __init__(self, mind_layer, bio_layer, _events):
        self.mind = mind_layer
        self.bio = bio_layer

    def think(self, physics_packet, _bio, _inventory, voltage_history, _tick_count, soul_ref=None, ):
        voltage = physics_packet.get("voltage", 0.0)
        clean_words = physics_packet.get("clean_words", [])
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
        mind_data = {
            "lens": current_lens,
            "context_msg": msg_cog.format(ignition=ignition),
            "role": current_role,}
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