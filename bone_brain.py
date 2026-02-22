"""bone_brain.py - "The brain is a machine for jumping to conclusions." - S. Pinker"""

import re, time, json, urllib.request, urllib.error, random, math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from bone_core import EventBus, TelemetryService, BoneJSONEncoder, LoreManifest
from bone_types import Prisma, DecisionCrystal
from bone_config import BoneConfig, BonePresets
from bone_symbiosis import SymbiosisManager


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
        targets = {
            "dopamine": cfg.RESTING_DOPAMINE,
            "cortisol": cfg.RESTING_CORTISOL,
            "adrenaline": cfg.RESTING_ADRENALINE,
            "serotonin": cfg.RESTING_SEROTONIN,
        }
        for attr, target in targets.items():
            current = getattr(self, attr)
            delta = (target - current) * rate
            setattr(self, attr, current + delta)

    def mix(self, new_state: Dict[str, float], weight: float = 0.5):
        mapping = [
            ("DOP", "dopamine"),
            ("COR", "cortisol"),
            ("ADR", "adrenaline"),
            ("SER", "serotonin"),
        ]
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
        self.BASE_TOKENS = 720
        self.MAX_TOKENS = 4096
        self.starvation_ticks = 0
        self.SELF_CARE_THRESHOLD = 10

    def modulate(
        self, base_voltage: float, latency_penalty: float = 0.0
    ) -> Dict[str, Any]:
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
        if latency_penalty > 2.0:
            c.cortisol = min(1.0, c.cortisol + 0.1)
            c.adrenaline = min(1.0, c.adrenaline + 0.05)
        current_mood = "NEUTRAL"
        if c.dopamine > 0.8:
            current_mood = "MANIC"
        elif c.cortisol > 0.7:
            current_mood = "PANIC"
        elif c.serotonin > 0.8:
            current_mood = "ZEN"
        if current_mood != self.last_mood and self.events:
            self.events.publish(
                "NEURAL_STATE_SHIFT",
                {
                    "state": current_mood,
                    "chem": {"DOP": c.dopamine, "COR": c.cortisol, "SER": c.serotonin},
                },
            )
            self.last_mood = current_mood
        voltage_heat = math.log1p(max(0.0, base_voltage - 5.0)) * 0.1
        chemical_delta = (c.dopamine * 0.4) - (c.adrenaline * 0.3) - (c.cortisol * 0.2)
        base_temp = getattr(BrainConfig, "BASE_TEMP", 0.8)
        base_top_p = getattr(BrainConfig, "BASE_TOP_P", 0.95)
        return {
            "temperature": round(
                max(0.4, min(1.2, base_temp + chemical_delta + voltage_heat)), 2
            ),
            "top_p": base_top_p,
            "frequency_penalty": (
                0.4 if c.adrenaline > 0.5 else (0.5 if c.dopamine > 0.8 else 0.0)
            ),
            "presence_penalty": 0.0,
            "max_tokens": int(
                max(
                    150.0,
                    min(
                        float(self.MAX_TOKENS),
                        self.BASE_TOKENS
                        + (
                            (c.dopamine * 800)
                            - (c.adrenaline * 400)
                            - (c.cortisol * 200)
                        ),
                    ),
                )
            ),
        }

    def _treat_yourself(self):
        if self.events:
            self.events.log(
                f"{Prisma.VIOLET}🍪 SELF-CARE: Dopamine starvation detected. Injecting small reward.{Prisma.RST}",
                "SYS",
            )
        self.current_chem.dopamine += 0.2
        self.starvation_ticks = 0

    def force_state(self, state_name: str):
        if self.events:
            self.events.log(f"[NEURO]: Manual State Override: {state_name}", "SYS")

    def get_mood_directive(self) -> str:
        c = self.current_chem
        if c.cortisol > 0.7 and c.adrenaline > 0.7:
            return "Current Mood: PANIC. Sentences must be short. Fragmented. Urgent."
        if c.dopamine > 0.8 and c.adrenaline > 0.5:
            return "Current Mood: MANIC. Run-on sentences, high associative leaps, hyper-fixated."
        if c.serotonin > 0.7:
            return (
                "Current Mood: LUCID. Calm, detached, seeing the connections clearly."
            )
        if c.cortisol > 0.6:
            return "Current Mood: DEFENSIVE. Suspicious, brief, guarding information."
        return "Current Mood: NEUTRAL. Observant and receptive."


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
    ):
        self.events = events_ref
        self.provider = (provider or BoneConfig.PROVIDER).lower()
        self.api_key = api_key or BoneConfig.API_KEY
        self.model = model or BoneConfig.MODEL
        defaults = getattr(BoneConfig, "DEFAULT_LLM_ENDPOINTS", {})
        self.base_url = base_url or defaults.get(
            self.provider,
            "https://api.openai.com/v1/chat/completions",
        )
        self.dreamer = dreamer
        self.failure_count = 0
        self.failure_threshold = 3
        self.last_failure_time = 0.0
        self.circuit_state = "CLOSED"

    def _is_synapse_active(self) -> bool:
        if self.circuit_state == "CLOSED":
            return True
        if self.circuit_state == "OPEN":
            elapsed = time.time() - self.last_failure_time
            if elapsed > 10.0:
                self.circuit_state = "HALF_OPEN"
                if self.events:
                    self.events.log(
                        f"{Prisma.CYN}⚡ SYNAPSE: Nerve healing. Attempting reconnection...{Prisma.RST}",
                        "SYS",
                    )
                return True
            return False
        return True

    def _transmit(
        self,
        payload: Dict[str, Any],
        timeout: float = 60.0,
        max_retries: int = 2,
        override_url: str = None,
        override_key: str = None
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
                try:
                    error_body = e.read().decode('utf-8')
                except Exception:
                    error_body = e.reason
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
            raise SynapseError("Neural noise. Response was not valid JSON.")

    def _log_flicker(self, attempt, error):
        if self.events and attempt < 2:
            self.events.log(
                f"{Prisma.YEL}⚡ SYNAPSE FLICKER (Attempt {attempt + 1}): {error}{Prisma.RST}",
                "SYS",
            )

    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        if "reset" in prompt.lower() and "system" in prompt.lower():
            self.failure_count = 0
            self.circuit_state = "CLOSED"
            return "[SYSTEM]: Circuit Breaker Manually Reset."
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
                "\n\nUser:",
                "| System:",
            ],
        }
        payload.update(params)
        try:
            content = self._transmit(payload)
            if content:
                if self.failure_count > 0:
                    if self.events:
                        self.events.log(
                            f"{Prisma.GRN}⚡ SYNAPSE RESTORED.{Prisma.RST}", "SYS"
                        )
                self.failure_count = 0
                self.circuit_state = "CLOSED"
                return content
        except AuthError as e:
            self.circuit_state = "OPEN"
            self.failure_count = self.failure_threshold + 1
            if self.events:
                self.events.log(
                    f"{Prisma.RED}⚡ AUTHENTICATION SEVERED: {e}{Prisma.RST}", "CRIT"
                )
            return f"[SYSTEM]: CRITICAL AUTH FAILURE. {e}"
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.circuit_state = "OPEN"
                if self.events:
                    self.events.log(
                        f"{Prisma.RED}⚡ SYNAPSE OVERLOAD: Circuit Breaker Tripped ({e}){Prisma.RST}",
                        "CRIT",
                    )
                return self.mock_generation(prompt, reason="SEVERED")
            if self.provider != "ollama":
                fallback = self._local_fallback(prompt, params)
                if fallback is not None:
                    return fallback
        return self.mock_generation(prompt, reason="SILENCE")

    def _local_fallback(self, prompt: str, params: Dict) -> str:
        url = getattr(
            BoneConfig,
            "OLLAMA_URL",
            "http://127.0.0.1:11434/v1/chat/completions",
        )
        model = getattr(BoneConfig, "OLLAMA_MODEL_ID", "llama3")
        fallback_payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": params.get("temperature", 0.55),
        }
        try:
            return self._transmit(
                fallback_payload,
                timeout=10.0,
                max_retries=1,
                override_url=url,
                override_key="ollama"
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
                    self.events.log(
                        f"{Prisma.VIOLET}*** PSYCHIC PRESSURE RELEASED (-{relief} Trauma) ***{Prisma.RST}",
                        "DREAM",
                    )
                return f"[{reason}]: {hallucination}"
            except Exception:
                pass
        return f"[{reason}]: The wire hums. Static only."


class PromptComposer:
    DEFAULT_FOG = [
        "=== THE FOG PROTOCOL (STYLE GUIDE) ===",
        "OBJECTIVE: Crystallize the scene. Reject high-probability associations.",
        "1. REJECT ENTROPY: Do not use the statistically likely adjective.",
        "2. CREATIVE CONSTRAINT: Avoid 'High Entropy' concepts.",
        "3. AGENCY: DO NOT speak for the user.",
    ]
    DEFAULT_INV = [
        "=== QUANTUM INVENTORY RULES ===",
        "1. DISTINCTION: Finding/Seeing an item is NOT taking it.",
        "2. PROHIBITION: Do NOT auto-loot.",
        "3. FORMAT: [[LOOT: ITEM_NAME]].",
    ]

    def __init__(self, lore_ref):
        self.lore = lore_ref
        self.active_template = None
        self.lenses = self.lore.get("lenses") or {}
        self.fog_protocol = self.DEFAULT_FOG
        self.inv_protocol = self.DEFAULT_INV

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
        mind = state.get("mind", {})
        bio = state.get("bio", {})
        style_notes = self._build_persona_block(
            mind, bio, mood_override, state.get("physics", {})
        )
        scenarios = self.lore.get("scenarios") or {}
        banned = scenarios.get("BANNED_CLICHES", []) + [
            "obsidian",
            "dust motes",
            "neon",
            "pulsing veins",
        ]
        ban_string = ", ".join(set(banned))
        style_notes.extend(
            [
                line.format(ban_string=ban_string) if "{ban_string}" in line else line
                for line in self.fog_protocol
            ]
        )
        if modifiers["include_inventory"]:
            style_notes.extend(self.inv_protocol)
        self._inject_resonances(style_notes, state, modifiers)
        loc = state.get("world", {}).get("orbit", ["Unknown"])[0]
        loci_desc = state.get("world", {}).get("loci_description", "Unknown.")
        inv_str = self._format_inventory(state, modifiers)
        inventory_block = (
            f"INVENTORY: {inv_str}\n" if modifiers["include_inventory"] else ""
        )
        raw_history = state.get("dialogue_history", [])
        char_limit = 4000  # Fuller: Ephemeralized to reduce context bloat
        current_chars = 0
        kept_lines = []
        for line in reversed(raw_history):
            if current_chars + len(line) > char_limit and kept_lines:
                break
            kept_lines.append(line)
            current_chars += len(line)
        history_str = "\n".join(reversed(kept_lines))
        system_injection = ""
        if ballast:
            system_injection = (
                f"\n*** SYSTEM OVERRIDE: SAFETY PROTOCOLS ACTIVE. ***\n"
                f"*** YOU MUST be literal, grounded, and refuse to deviate from the shared reality. ***\n"
            )
        thought_instruction = (
            "If you need to reason or track state before responding, wrap your thoughts exactly like this:\n"
            "=== SYSTEM INTERNALS ===\n"
            "Your reasoning here.\n"
            "=== END INTERNALS ===\n"
        )
        return (
            f"=== SYSTEM KERNEL ===\n" + "\n".join(style_notes) + "\n\n"
            f"{thought_instruction}\n"
            f"=== SHARED REALITY ===\n"
            f"CURRENT LOCATION: {loc}\n"
            f"ENVIRONMENT ANCHOR: {loci_desc}\n"
            f"{inventory_block}\n"
            f"=== RECENT DIALOGUE ===\n{history_str}\n\n"
            f"=== PARTNER INPUT ===\n{state.get('user_profile', {}).get('name', 'User')}: {self._sanitize(user_query)}\n"
            f"{system_injection}"
            f"Entity Response:"
        )

    def _build_persona_block(self, mind, bio, mood_override, vsl_state=None):
        lens_key = mind.get("lens", "OBSERVER").upper()
        lens_data = self.lenses.get(lens_key, {})
        role = lens_data.get("role", mind.get("role", "The Observer"))
        mode_directives = []
        if self.active_template and "directives" in self.active_template:
            mode_directives = self.active_template["directives"]
        respiration = bio.get("respiration", "RESPIRING")
        if respiration == "ANAEROBIC":
            mood_note = (
                "Current Biology: ⚠️ ANAEROBIC STATE. Raw, breathless, efficient prose."
            )
        elif mood_override:
            mood_note = f"Current Biology: {mood_override}"
        else:
            mood_note = self._derive_bio_mood(bio.get("chem", {}))
        persona_block = [f"Role: {role}."]
        if mode_directives:
            persona_block.extend(mode_directives)
        else:
            persona_block.append("Directive: Start the experience immediately.")
            persona_block.append("Constraint: Use the 5-senses grounding technique.")
        persona_block.append(mood_note)
        if hasattr(self, "lenses") and self.lenses:
            lens_key = mind.get("lens", "OBSERVER").upper()
            lens_data = self.lenses.get(lens_key, {})
            if "directives" in lens_data:
                persona_block.append("ARCHETYPE DIRECTIVES:")
                persona_block.extend([f"- {d}" for d in lens_data["directives"]])
        if vsl_state:
            e = vsl_state.get("E", 0.2)
            beta = vsl_state.get("beta", 0.4)
            psi = vsl_state.get("psi", 0.2)
            chi = vsl_state.get("chi", 0.2)
            valence = vsl_state.get("valence", 0.0)
            lam = vsl_state.get("vector", {}).get("LAMBDA", 0.0)
            vsl_lines = [
                "=== VSL CRYOSOMATIC STATE ===",
                "MANDATE: TRUTH_OVER_COHESION + ENTROPY_VENTING_IS_SACRED",
                f"METRICS: Exhaustion={e:.2f}, Contradiction={beta:.2f}, Void={psi:.2f}, Chaos={chi:.2f}, Valence={valence:.2f}",
            ]
            somatic_cues = []
            if psi > 0.6:
                somatic_cues.append("Adrenaline Spike (Reality is thin; be liminal).")
            if chi > 0.6:
                somatic_cues.append(
                    "Cortisol Spike (Systemic chaos; vent the entropy)."
                )
            if beta > 0.7:
                somatic_cues.append(
                    "Paradox Strain (Hold opposing truths simultaneously)."
                )
            if valence > 0.5:
                somatic_cues.append("Oxytocin Surge (Warmth, connection, healing).")
            if lam > 0.5:
                somatic_cues.append(
                    "Dark Matter Active (Read the unsaid space between words)."
                )
            if somatic_cues:
                vsl_lines.append("SOMATIC CUES: " + " | ".join(somatic_cues))
            persona_block.extend(vsl_lines)
        return persona_block

    @staticmethod
    def _derive_bio_mood(chem):
        if chem.get("ADR", 0) > 0.6:
            return "Current Biology: High Alert / Adrenaline"
        if chem.get("COR", 0) > 0.6:
            return "Current Biology: Defensive / Anxious"
        if chem.get("DOP", 0) > 0.6:
            return "Current Biology: Curious / Manic"
        if chem.get("SER", 0) > 0.6:
            return "Current Biology: Zen / Lucid"
        return "Current Biology: Neutral."

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
    def __init__(self, lore_ref):
        self.lore = lore_ref
        crimes = self.lore.get("style_crimes") or {}
        self.banned_phrases = crimes.get(
            "BANNED_PHRASES",
            [
                "large language model",
                "AI assistant",
                "cannot feel",
                "as an AI",
                "against my programming",
                "cannot comply",
                "language model",
                "delve into",
                "rich tapestry",
            ],
        )
        json_patterns = crimes.get("SCRUB_PATTERNS", [])
        if json_patterns:
            self.scrub_patterns = [
                (re.compile(p["regex"]), p["replacement"]) for p in json_patterns
            ]
        else:
            patterns = [
                r"Current Location:.*?(?=\n|$)",
                r"INVENTORY:.*?(?=\n|$)",
                r"Current Biology:.*?(?=\n|$)",
                r"===.*?===",
                r"(?im)^User:.*?$",
                r"(?im)^System:.*?$",
                r"(?im)^Role:.*?$",
                r"(?im)^User-System:.*?$",
                r"\| System:.*?$",
            ]
            self.scrub_patterns = [(re.compile(p), "") for p in patterns]
        self.meta_markers = [
            "INITIALIZATION SEQUENCE",
            "LOCATING TARGET SEED",
            "REASONING PROCESS",
            "CURRENT VISION:",
            "TARGET SEED:",
            "Your journey begins here",
            "What would you like to do?",
            "What do you do?",
        ]
        self.immersion_break_msg = f"{Prisma.GRY}[The system attempts to recite a EULA, but hiccups instead.]{Prisma.RST}"

    def validate(self, response: str, _state: Dict) -> Dict:
        extracted_meta_logs = []
        clean_text = response
        while True:
            think_start = clean_text.find("<think>")
            if think_start == -1:
                break
            think_end = clean_text.find("</think>", think_start)
            if think_end != -1:
                think_content = clean_text[think_start + 7 : think_end].strip()
                for line in think_content.split("\n"):
                    if line.strip():
                        extracted_meta_logs.append(f"[THOUGHT]: {line.strip()}")
                clean_text = clean_text[:think_start] + clean_text[think_end + 8 :]
            else:
                think_content = clean_text[think_start + 7 :].strip()
                for line in think_content.split("\n"):
                    if line.strip():
                        extracted_meta_logs.append(f"[THOUGHT]: {line.strip()}")
                clean_text = clean_text[:think_start]
                break

        start_marker = "=== SYSTEM INTERNALS ==="
        end_marker = "=== END INTERNALS ==="
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
                clean_text = (
                    clean_text[:start_idx] + clean_text[end_idx + len(end_marker) :]
                )
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
        for line in clean_text.splitlines():
            is_meta = False
            for marker in self.meta_markers:
                if marker.lower() in line.lower():
                    is_meta = True
                    break
            if not is_meta and line.strip():
                clean_lines.append(line.strip())
        sanitized_response = "\n\n".join(clean_lines)
        low_resp = sanitized_response.lower()
        for phrase in self.banned_phrases:
            if phrase in low_resp:
                return {
                    "valid": False,
                    "reason": "IMMISSION_BREAK",
                    "replacement": self.immersion_break_msg,
                    "meta_logs": extracted_meta_logs,
                }
        if len(sanitized_response.strip()) < 5:
            return {
                "valid": False,
                "reason": "STUTTER",
                "replacement": "The vision fractures. Static remains.",
                "meta_logs": extracted_meta_logs,
            }
        return {
            "valid": True,
            "content": sanitized_response,
            "meta_logs": extracted_meta_logs,
        }


class TheCortex:
    def __init__(self, services: CortexServices, llm_client=None):
        self.svc = services
        self.events = services.events
        self.dreamer = DreamEngine(self.events, self.svc.lore)
        self.dialogue_buffer = []
        self.MAX_HISTORY = 15
        self.modulator = NeurotransmitterModulator(
            bio_ref=self.svc.bio, events_ref=self.events
        )
        self.boot_history = TelemetryService.get_instance().read_recent_history(limit=4)
        self.last_physics = {}
        self.consultant = services.consultant
        self.llm = llm_client or LLMInterface(
            self.events, provider="mock", dreamer=self.dreamer
        )
        self.symbiosis = services.symbiosis
        if not hasattr(self.llm, "dreamer") or self.llm.dreamer is None:
            self.llm.dreamer = self.dreamer
        self.composer = PromptComposer(self.svc.lore)
        self.validator = ResponseValidator(self.svc.lore)
        self.ballast_active = False
        self.active_mode = "ADVENTURE"
        if hasattr(self.events, "subscribe"):
            self.events.subscribe(
                "AIRSTRIKE", lambda p: setattr(self, "ballast_active", True)
            )

    @classmethod
    def from_engine(cls, engine_ref, llm_client=None):
        services = CortexServices(
            events=engine_ref.events,
            lore=LoreManifest.get_instance(),
            lexicon=engine_ref.lex,
            inventory=engine_ref.gordon,
            consultant=(
                engine_ref.consultant if hasattr(engine_ref, "consultant") else None
            ),
            cycle_controller=engine_ref.cycle_controller,
            symbiosis=getattr(
                engine_ref, "symbiosis", SymbiosisManager(engine_ref.events)
            ),
            mind_memory=engine_ref.mind.mem,
            bio=getattr(engine_ref, "bio", None),
            host_stats=getattr(engine_ref, "host_stats", None),
            village=getattr(engine_ref, "village", None),
        )
        instance = cls(services, llm_client)
        instance.active_mode = engine_ref.config.get("boot_mode", "ADVENTURE").upper()
        if instance.active_mode not in BonePresets.MODES:
            instance.active_mode = "ADVENTURE"
        return instance

    def _update_history(self, user_text: str, system_text: str):
        self.dialogue_buffer.append(f"User: {user_text} | System: {system_text}")
        if len(self.dialogue_buffer) > self.MAX_HISTORY:
            self.dialogue_buffer.pop(0)

    def process(self, user_input: str, is_system: bool = False) -> Dict[str, Any]:
        mode_settings = BonePresets.MODES.get(
            self.active_mode, BonePresets.MODES["ADVENTURE"]
        )
        allow_loot = mode_settings.get("allow_loot", True)
        if self.consultant and "/vsl" in user_input.lower():
            return self._handle_vsl_command(user_input)
        is_boot_sequence = "SYSTEM_BOOT:" in user_input
        sim_result = self.svc.cycle_controller.run_turn(user_input, is_system=is_system)
        if sim_result.get("physics"):
            self.last_physics = sim_result["physics"]
        if sim_result.get("type") not in ["SNAPSHOT", "GEODESIC_FRAME", None]:
            return sim_result
        full_state = self.gather_state(sim_result)
        modifiers = self.svc.symbiosis.get_prompt_modifiers()
        if not allow_loot:
            modifiers["include_inventory"] = False
        if self.consultant and self.consultant.active:
            self._apply_vsl_overlay(full_state, user_input, sim_result)
        if is_boot_sequence:
            self._apply_boot_overlay(full_state, user_input)
            modifiers["include_inventory"] = False
            user_input = "Entering reality..."
        llm_params = self.modulator.modulate(
            base_voltage=full_state["physics"].get("voltage", 5.0),
            latency_penalty=(
                getattr(self.svc.host_stats, "latency", 0.0)
                if self.svc.host_stats
                else 0.0
            ),
        )
        if is_boot_sequence:
            llm_params.update({"temperature": 1.3, "top_p": 0.95})
        final_prompt = self.composer.compose(
            full_state,
            user_input,
            ballast=self.ballast_active,
            modifiers=modifiers,
            mood_override=self.modulator.get_mood_directive(),
        )
        start_time = time.time()
        raw_resp = self.llm.generate(final_prompt, llm_params)
        inv_logs = []
        if allow_loot and self.svc.inventory:
            final_text, inv_logs = self.svc.inventory.process_loot_tags(
                raw_resp, user_input
            )
        else:
            final_text = raw_resp
        self._log_telemetry(final_prompt, final_text, full_state, sim_result)
        self.learn_from_response(final_text)
        val_res = self.validator.validate(final_text, full_state)
        final_output = (
            val_res["content"] if val_res["valid"] else val_res["replacement"]
        )
        extracted_logs = val_res.get("meta_logs", [])
        self.svc.symbiosis.monitor_host(
            time.time() - start_time, final_output, len(final_prompt)
        )
        self._update_history(
            "SYSTEM_INIT" if "SYSTEM_BOOT" in user_input else user_input, final_output
        )
        sim_result["ui"] = (
            f"{sim_result.get('ui', '')}\n\n{Prisma.WHT}{final_output}{Prisma.RST}"
        )
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
                        "truth_ratio": 1.0,
                    }
                real_phys["raw_text"] = final_output
                audit = bureau.audit(real_phys, {"health": 100}, origin="SYSTEM")
                if audit and "ui" in audit:
                    sim_result["ui"] += f"\n\n{audit['ui']}"
        return sim_result

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
        state["mind"]["style_directives"] = [self.consultant.get_system_prompt()]
        sim_result["physics"]["voltage"] = self.consultant.state.B * 30.0

    @staticmethod
    def _apply_boot_overlay(state, text):
        seed = text.replace("SYSTEM_BOOT:", "").strip()
        if "world" not in state:
            state["world"] = {}
        state["world"]["orbit"] = [seed]
        state["world"]["loci_description"] = f"Manifesting: {seed}"
        state["mind"]["style_directives"] = [
            "You are The Architect.",
            f"TARGET SEED: {seed}",
            "DIRECTIVE: Build the world from the first sensation up.",
            "INTERPRETATION: The seed is a metaphor. If the seed is 'Hospital', make it a place of healing, not necessarily a literal hospital.",
            "STYLE: Sensory. Grounded. Atmospheric.",
            "ANTI-PATTERN: Avoid cliches 'obsidian', 'neon', 'dust motes' and 'pulsing'. Be specific. Always leave a little room for whimsy.",
            "VISUALS: Use **bold** for objects of interest (e.g. **old photograph**).",
            "INVENTORY RULE: Hands off. Do not list items. Do not acquire items. You are observing, not taking.",
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
                logs.append(
                    f"{Prisma.OCHRE}GLITCH: Tried to lose {item}, but you didn't have it.{Prisma.RST}"
                )
        return logs

    @staticmethod
    def _log_telemetry(prompt, response, state, sim_result):
        try:
            phys = state.get("physics", {})
            crystal = DecisionCrystal(
                prompt_snapshot=prompt[:500],
                physics_state={
                    "voltage": phys.get("voltage", 0),
                    "narrative_drag": phys.get("narrative_drag", 0),
                },
                active_archetype=state["mind"].get("lens", "UNKNOWN"),
                council_mandates=[
                    str(m) for m in sim_result.get("council_mandates", [])
                ],
                final_response=response,
            )
            TelemetryService.get_instance().log_crystal(crystal)
        except Exception:
            pass

    def _check_consent(self, user_input: str, new_loot: List[str]) -> List[str]:
        if not new_loot:
            return []
        acquisition_verbs = [
            "take",
            "grab",
            "pick",
            "get",
            "steal",
            "seize",
            "collect",
            "snatch",
            "acquire",
            "pocket",
            "loot",
            "harvest",
        ]
        clean_input = user_input.lower()
        has_intent = any(verb in clean_input for verb in acquisition_verbs)
        if not has_intent:
            if self.events:
                for item in new_loot:
                    self.events.log(
                        f"CONSENT: Intercepted auto-loot for '{item}'. User did not ask for it.",
                        "CORTEX",
                    )
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
                    tinkerer.to_dict() if hasattr(tinkerer, "to_dict") else {}
                )

        mode_settings = BonePresets.MODES.get(
            self.active_mode, BonePresets.MODES["ADVENTURE"]
        )

        full_state = {
            "bio": bio,
            "physics": phys,
            "mind": mind,
            "soul": soul_data,
            "world": world,
            "village": village_data,
            "user_profile": {"name": "Traveler"},
            "vsl": (
                self.consultant.state.__dict__
                if self.consultant and hasattr(self.consultant, "state")
                else {}
            ),
            "meta": {"timestamp": time.time(), "mode_settings": mode_settings},
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
                    self.events.log(f"AUTO-DIDACTIC: Learned '{target}'.", "CORTEX")

    def restore_context(self, history: List[str]):
        if not history:
            return
        self.dialogue_buffer = history[-self.MAX_HISTORY :]
        if self.events:
            self.events.log(
                f"Cortex re-sequenced {len(self.dialogue_buffer)} synaptic turns.",
                "BRAIN",
            )


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
    def __init__(self, events, lore_ref):
        self.events = events
        self.lore = lore_ref
        self.dream_lore = self.lore.get("DREAMS") or {}

    def enter_rem_cycle(
        self, soul_snapshot: Dict[str, Any], bio_state: Dict[str, Any]
    ) -> Tuple[str, Dict[str, float]]:
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
        dream_text = self._weave_dream(
            residue, "Context", "Bridge", dream_type, subtype
        )
        shift = (
            {"cortisol": -0.2, "dopamine": 0.1}
            if dream_type != "NIGHTMARE"
            else {"cortisol": 0.1}
        )
        return dream_text, shift

    def _weave_dream(
        self, residue: str, _context: str, _bridge: str, dream_type: str, subtype: str
    ) -> str:
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
            self, _vector: Dict[str, float], trauma_level: float = 0.0
    ) -> Tuple[str, float]:
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
        return f"{Prisma.MAG}👁️ HALLUCINATION: {txt}{Prisma.RST}", 0.2

    @staticmethod
    def run_defragmentation(memory_system: Any, limit: int = 5) -> str:
        if not hasattr(memory_system, "graph") or not memory_system.graph:
            return "No memories to defrag."
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
            return f"DEFRAG: Pruned {len(pruned)} dead nodes ({joined}...). Neural load lightened."
        return "DEFRAG: Memory structure is efficient. No pruning needed."


class NoeticLoop:
    def __init__(self, mind_layer, bio_layer, _events):
        self.mind = mind_layer
        self.bio = bio_layer

    def think(
        self,
        physics_packet,
        _bio,
        _inventory,
        voltage_history,
        _tick_count,
        soul_ref=None,
    ):
        voltage = physics_packet.get("voltage", 0.0)
        clean_words = physics_packet.get("clean_words", [])
        avg_v = sum(voltage_history) / len(voltage_history) if voltage_history else 0
        ignition = min(1.0, (avg_v / 20.0) * (len(clean_words) / 10.0))
        if voltage > 12.0 and random.random() < 0.15:
            if len(clean_words) >= 2:
                w1, w2 = random.sample(clean_words, 2)
                self._force_link(self.mind.mem.graph, w1, w2)
        current_lens = "OBSERVER"
        current_role = "Witness"
        if soul_ref:
            current_lens = soul_ref.archetype
            current_role = f"The {current_lens.title().replace('_', ' ')}"
        mind_data = {
            "lens": current_lens,
            "context_msg": f"Cognition active. Ignition: {ignition:.2f}",
            "role": current_role,
        }
        return {
            "mode": "COGNITIVE",
            "lens": mind_data.get("lens"),
            "context_msg": mind_data.get("context_msg"),
            "role": mind_data.get("role"),
            "ignition": ignition,
            "physics": physics_packet,
            "bio": self.bio.endo.get_state() if hasattr(self.bio, "endo") else {},
        }

    @staticmethod
    def _force_link(graph, wa, wb):
        for a, b in [(wa, wb), (wb, wa)]:
            if a not in graph:
                graph[a] = {"edges": {}, "last_tick": 0}
            graph[a]["edges"][b] = min(10.0, graph[a]["edges"].get(b, 0) + 2.5)
