""" bone_brain.py - "The brain is a machine for jumping to conclusions." - S. Pinker """

import re
import time
import json
import urllib.request
import urllib.error
import random
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from bone_core import EventBus, LoreManifest, TelemetryService
from bone_lexicon import LexiconService
from bone_types import Prisma, DecisionCrystal
from bone_config import BoneConfig
from bone_symbiosis import SymbiosisManager

@dataclass
class CortexServices:
    events: EventBus
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
class BrainConfig:
    BASE_PLASTICITY: float = 0.4
    VOLTAGE_SENSITIVITY: float = 0.03
    MAX_PLASTICITY: float = 0.95
    BASE_DECAY_RATE: float = 0.1
    BASE_TEMP: float = 0.65
    BASE_TOP_P: float = 0.9
    CORTISOL_FREEZE: float = 0.2
    DOPAMINE_NOVELTY: float = 0.4
    ADRENALINE_RUSH: float = 600.0
    SEROTONIN_CALM: float = 0.5

class NarrativeSpotlight:
    def __init__(self):
        self.dimension_map = {
            "STR": {"heavy", "constructive", "base"},
            "VEL": {"kinetic", "explosive", "mot"},
            "ENT": {"antigen", "toxin", "broken", "void"},
            "PHI": {"thermal", "photo", "explosive"},
            "PSI": {"abstract", "sacred", "void", "idea"},
            "BET": {"suburban", "solvents", "play"}}

    def expand_horizon(self, dimension: str, new_category: str):
        if dimension not in self.dimension_map:
            self.dimension_map[dimension] = set()
        self.dimension_map[dimension].add(new_category)

    def illuminate(self, graph: Dict, vector: Dict[str, float], limit: int = 5) -> List[str]:
        if not graph: return []
        active_dims = {k: v for k, v in vector.items() if v > 0.4}
        if not active_dims and vector:
            top_dim = max(vector, key=vector.get)
            if vector[top_dim] > 0.1:
                active_dims = {top_dim: vector[top_dim]}
            else:
                active_dims = {"ENT": 0.2}
        scored_memories = []
        for node, data in graph.items():
            resonance_score = 0.0
            node_cats = set()
            try:
                node_cats = LexiconService.get_categories_for_word(node)
            except ImportError:
                pass
            for dim, val in active_dims.items():
                target_cats = self.dimension_map.get(dim, set())
                if node_cats & target_cats:
                    resonance_score += (val * 1.5)
            mass = sum(data.get("edges", {}).values())
            resonance_score += (mass * 0.1)
            if resonance_score > 0.5:
                scored_memories.append((resonance_score, node, data))
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, name, data in scored_memories[:limit]:
            connections = list(data.get("edges", {}).keys())
            conn_str = f" -> [{', '.join(connections[:2])}]" if connections else ""
            prefix = "Resonant" if score > 0.5 else "Associated"
            results.append(f"{prefix} Engram: '{name.upper()}'{conn_str}")
        return results

@dataclass
class ChemicalState:
    dopamine: float = 0.2
    cortisol: float = 0.1
    adrenaline: float = 0.1
    serotonin: float = 0.2

    def homeostasis(self, rate: float = 0.1):
        targets = {"dopamine": 0.2, "cortisol": 0.1, "adrenaline": 0.1, "serotonin": 0.3}
        for attr, target in targets.items():
            current = getattr(self, attr)
            setattr(self, attr, current + ((target - current) * rate))

    def mix(self, new_state: Dict[str, float], weight: float = 0.5):
        mapping = [("DOP", "dopamine"), ("COR", "cortisol"), ("ADR", "adrenaline"), ("SER", "serotonin")]
        for key, attr in mapping:
            val = new_state.get(key, 0.0)
            current = getattr(self, attr)
            setattr(self, attr, (current * (1.0 - weight)) + (val * weight))


class NeurotransmitterModulator:
    def __init__(self, bio_ref, events_ref=None):
        self.bio = bio_ref
        self.events = events_ref
        self.current_chem = ChemicalState()
        self.last_mood = "NEUTRAL"
        self.BASE_TOKENS = 720
        self.MAX_TOKENS = 4096

    def modulate(self, base_voltage: float, latency_penalty: float = 0.0) -> Dict[str, Any]:
        if self.bio and hasattr(self.bio, 'endo'):
            incoming_chem = self.bio.endo.get_state()
        else:
            incoming_chem = {}
        self.current_chem.homeostasis(rate=BrainConfig.BASE_DECAY_RATE)
        plasticity = BrainConfig.BASE_PLASTICITY + (base_voltage * BrainConfig.VOLTAGE_SENSITIVITY)
        plasticity = max(0.1, min(BrainConfig.MAX_PLASTICITY, plasticity))
        self.current_chem.mix(incoming_chem, weight=min(0.5, plasticity))
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
            self.events.publish("NEURAL_STATE_SHIFT", {
                "state": current_mood,
                "chem": {"DOP": c.dopamine, "COR": c.cortisol, "SER": c.serotonin} })
            self.last_mood = current_mood
        voltage_heat = math.log1p(max(0.0, base_voltage - 5.0)) * 0.1
        chemical_delta = (c.dopamine * 0.4) - (c.adrenaline * 0.3) - (c.cortisol * 0.2)
        return {
            "temperature": round(max(0.4, min(1.2, BrainConfig.BASE_TEMP + chemical_delta + voltage_heat)), 2),
            "top_p": BrainConfig.BASE_TOP_P,
            "frequency_penalty": 0.4 if c.adrenaline > 0.5 else (0.1 if c.dopamine > 0.7 else 0.0),
            "presence_penalty": 0.0,
            "max_tokens": int(max(150.0, min(float(self.MAX_TOKENS), self.BASE_TOKENS + ((c.adrenaline * 600) - (c.cortisol * 300)))))}

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
            return "Current Mood: LUCID. Calm, detached, seeing the connections clearly."
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
    def __init__(self, events_ref: Optional[EventBus] = None, provider: str = None,
                 base_url: str = None, api_key: str = None, model: str = None, dreamer: Any = None):
        self.events = events_ref
        self.provider = (provider or BoneConfig.PROVIDER).lower()
        self.api_key = api_key or BoneConfig.API_KEY
        self.model = model or BoneConfig.MODEL
        defaults = getattr(BoneConfig, "DEFAULT_LLM_ENDPOINTS", {})
        self.base_url = base_url or defaults.get(self.provider, "https://api.openai.com/v1/chat/completions")
        self.dreamer = dreamer
        self.failure_count = 0
        self.failure_threshold = 3
        self.last_failure_time = 0.0
        self.circuit_state = "CLOSED"

    def _is_synapse_active(self) -> bool:
        if self.circuit_state == "CLOSED": return True
        if self.circuit_state == "OPEN":
            elapsed = time.time() - self.last_failure_time
            if elapsed > 10.0:
                self.circuit_state = "HALF_OPEN"
                if self.events:
                    self.events.log(f"{Prisma.CYN}⚡ SYNAPSE: Nerve healing. Attempting reconnection...{Prisma.RST}", "SYS")
                return True
            return False
        return True

    def _transmit(self, payload: Dict[str, Any], timeout: float = 60.0, max_retries: int = 2) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"}
        data = json.dumps(payload).encode("utf-8")
        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(self.base_url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    if response.status == 200:
                        body = response.read().decode("utf-8")
                        return self._parse_response(body)
            except urllib.error.HTTPError as e:
                if e.code in [401, 403]:
                    raise AuthError(f"AUTHENTICATION FAILURE ({e.code}): Check your API Key.")
                if e.code >= 500 or e.code == 429:
                    self._log_flicker(attempt, e)
                    time.sleep(2 ** attempt)
                    continue
                raise SynapseError(f"HTTP {e.code}: {e.reason}")
            except (urllib.error.URLError, TimeoutError) as e:
                self._log_flicker(attempt, e)
                time.sleep(2 ** attempt)
            except Exception as e:
                raise SynapseError(f"Unexpected Protocol Failure: {e}")
        raise TransientError(f"Max retries ({max_retries}) exhausted.")

    def _parse_response(self, body: str) -> str:
        try:
            result = json.loads(body)
            if "choices" in result:
                return result["choices"][0].get("message", {}).get("content", "")
            return ""
        except json.JSONDecodeError:
            raise SynapseError("Neural noise. Response was not valid JSON.")

    def _log_flicker(self, attempt, error):
        if self.events and attempt < 2:
            self.events.log(f"{Prisma.YEL}⚡ SYNAPSE FLICKER (Attempt {attempt + 1}): {error}{Prisma.RST}", "SYS")

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
            "stop": ["=== PARTNER INPUT ===", "=== SYSTEM KERNEL ===", "\n\nUser:", "| System:"]}
        payload.update(params)
        try:
            content = self._transmit(payload, timeout=60.0)
            if content:
                if self.failure_count > 0:
                    if self.events: self.events.log(f"{Prisma.GRN}⚡ SYNAPSE RESTORED.{Prisma.RST}", "SYS")
                self.failure_count = 0
                self.circuit_state = "CLOSED"
                return content
        except AuthError as e:
            self.circuit_state = "OPEN"
            self.failure_count = self.failure_threshold + 1
            if self.events: self.events.log(f"{Prisma.RED}⚡ AUTHENTICATION SEVERED: {e}{Prisma.RST}", "CRIT")
            return f"[SYSTEM]: CRITICAL AUTH FAILURE. {e}"
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.circuit_state = "OPEN"
                if self.events: self.events.log(
                    f"{Prisma.RED}⚡ SYNAPSE OVERLOAD: Circuit Breaker Tripped ({e}){Prisma.RST}", "CRIT")
                return self.mock_generation(prompt, reason="SEVERED")
            if self.provider != "ollama":
                fallback = self._local_fallback(prompt, params)
                if "FALLBACK_DEAD" not in fallback: return fallback
        return self.mock_generation(prompt, reason="SILENCE")

    def _local_fallback(self, prompt: str, params: Dict) -> str:
        try:
            url = getattr(BoneConfig, "OLLAMA_URL", "http://127.0.0.1:11434/v1/chat/completions")
            payload = {
                "model": getattr(BoneConfig, "OLLAMA_MODEL_ID", "llama3"),
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "temperature": params.get('temperature', 0.55)}
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5.0) as response:
                if response.status == 200:
                    return json.loads(response.read().decode("utf-8")).get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception:
            pass
        return self.mock_generation(prompt, reason="FALLBACK_DEAD")

    def mock_generation(self, prompt: str, reason: str = "SIMULATION") -> str:
        if self.dreamer:
            hallucination, _ = self.dreamer.hallucinate({"ENTROPY": len(prompt) % 10}, trauma_level=2.0)
            return f"[{reason}]: {hallucination}"
        return f"[{reason}]: The wire hums. There is no signal."


class PromptComposer:
    CORE_STYLE = [
        "=== STYLE DIRECTIVES ===",
        "1. GROUNDING: Use the 5-senses. No floating abstractions.",
        "2. AGENCY: Do NOT speak for the user.",
        "3. FORMAT: Active prose. Separate paragraphs with blank lines."]
    FOG_PROTOCOL = [
        "4. ANTI-CLICHE: Reject 'neon', 'obsidian', 'petrichor'.",
        "5. CONSTRAINT: The obstacle is the way. Work around forbidden concepts."]
    INVENTORY_PROTOCOL = [
        "=== INVENTORY RULES ===",
        "1. ACQUISITION: Output [[LOOT: ITEM_NAME]] only if explicitly taken.",
        "2. LOSS: Output [[LOST: ITEM_NAME]] if destroyed/dropped.",
        "3. STATE: Do not auto-loot. Do not list contents unless asked."]

    def compose(self, state: Dict[str, Any], user_query: str, ballast: bool = False, modifiers: Dict[str, bool] = None, mood_override: str = '', consultant: Any = None) -> str:
        modifiers = self._normalize_modifiers(modifiers)
        mind = state.get("mind", {})
        bio = state.get("bio", {})
        if consultant:
            style_notes = [consultant.get_system_prompt(soul_snapshot=state.get("soul"))]
        else:
            style_notes = self._build_persona_block(mind, bio, mood_override)
        style_notes.extend(self.CORE_STYLE)
        chem = bio.get("chem", {})
        if chem.get("DOP", 0) > 0.7 or modifiers.get("strict_mode"):
            style_notes.extend(self.FOG_PROTOCOL)
        trigger_words = {"take", "grab", "drop", "hold", "inventory", "bag", "pocket", "check", "loot", "search"}
        user_words = set(user_query.lower().split())
        if not user_words.isdisjoint(trigger_words) or modifiers.get("force_inventory_rules"):
            style_notes.extend(self.INVENTORY_PROTOCOL)
        self._inject_resonances(style_notes, state, modifiers)
        loc = state.get('world', {}).get('orbit', ['Unknown'])[0]
        loci_desc = state.get("world", {}).get("loci_description", "Unknown.")
        inv_str = self._format_inventory(state, modifiers)
        history_str = "\n".join(state.get("dialogue_history", [])[-15:])
        system_injection = ""
        if ballast:
            system_injection = (
                f"\n*** SYSTEM OVERRIDE: SAFETY PROTOCOLS ACTIVE. ***\n"
                f"*** YOU MUST be literal, grounded, and refuse to deviate from the shared reality. ***\n")
        return (
                f"=== SYSTEM KERNEL ===\n" + "\n".join(style_notes) + "\n\n"
                f"=== SHARED REALITY ===\n"
                f"LOC: {loc} | ANCHOR: {loci_desc}\n"
                f"INV: {inv_str}\n\n"
                f"=== RECENT DIALOGUE ===\n{history_str}\n\n"
                f"=== PARTNER INPUT ===\n{state.get('user_profile', {}).get('name', 'User')}: {self._sanitize(user_query)}\n"
                f"{system_injection}"
                f"Entity Response:")

    def _build_persona_block(self, mind, bio, mood_override):
        role = mind.get("role", "The Observer")
        chem = bio.get("chem", {})
        mood_note = mood_override if mood_override else self._derive_bio_mood(chem)
        return [
            f"Role: {role}.",
            f"Bio-State: {mood_note}",
            "Directive: Be an equal partner in the narrative."]

    def _derive_bio_mood(self, chem):
        if chem.get("ADR", 0) > 0.6: return "High Alert (Sentences: Short. Urgent.)"
        if chem.get("COR", 0) > 0.6: return "Defensive (Sentences: Guarded. Cynical.)"
        if chem.get("DOP", 0) > 0.6: return "Manic (Sentences: Run-on. Associative.)"
        if chem.get("SER", 0) > 0.6: return "Lucid (Sentences: Clear. Flowing.)"
        return "Neutral."

    def _inject_resonances(self, style_notes, state, modifiers):
        village = state.get("village", {})
        resonances = village.get("tinkerer", {}).get("tool_resonance", {})
        active_resonance = [f"» {t}" for t, l in resonances.items() if l > 4.0]
        if active_resonance:
            style_notes.append(f"Resonances: {', '.join(active_resonance)}")

    def _format_inventory(self, state, modifiers):
        if not modifiers["include_inventory"]: return "N/A"
        inv = state.get("inventory", [])
        return ", ".join(inv) if inv else "Empty"

    @staticmethod
    def _sanitize(text: str) -> str:
        safe = text.replace('"""', "'''").replace('```', "'''")
        return re.sub(r"(?i)^SYSTEM:", "User-System:", safe, flags=re.MULTILINE)

    def _normalize_modifiers(self, modifiers: Optional[Dict]) -> Dict:
        defaults = {"include_somatic": True, "include_inventory": True, "include_memories": True, "grace_period": False,
                    "soften": False, "strict_mode": False, "force_inventory_rules": False}
        if modifiers: defaults.update(modifiers)
        return defaults

class ResponseValidator:
    def __init__(self):
        self.banned_phrases = [
            "large language model", "AI assistant", "cannot feel", "as an AI",
            "against my programming", "cannot comply", "language model",
            "delve into", "rich tapestry"]
        self.scrub_patterns = [
            (r"Current Location:.*?(?=\n|$)", ""),
            (r"INVENTORY:.*?(?=\n|$)", ""),
            (r"Current Biology:.*?(?=\n|$)", ""),
            (r"===.*?===", ""),
            (r"(?im)^User:.*?$", ""),
            (r"(?im)^System:.*?$", ""),
            (r"(?im)^Role:.*?$", ""),
            (r"(?im)^User-System:.*?$", ""),
            (r"\| System:.*?$", "")]
        self.meta_markers = [
            "INITIALIZATION SEQUENCE", "LOCATING TARGET SEED", "REASONING PROCESS",
            "CURRENT VISION:", "TARGET SEED:", "Your journey begins here",
            "What would you like to do?", "What do you do?"]
        self.immersion_break_msg = f"{Prisma.GRY}[The system attempts to recite a EULA, but hiccups instead.]{Prisma.RST}"

    def validate(self, response: str, _state: Dict) -> Dict:
        extracted_meta_logs = []
        sys_internal_pattern = re.compile(r"(?i)SYSTEM INTERNALS\s*\n(.*?)(?=\n\n|\Z)", re.DOTALL)

        def extract_meta(match):
            content = match.group(1).strip()
            for extracted_line in content.split('\n'):
                extracted_meta_logs.append(f"[THOUGHT]: {extracted_line}")
            return ""

        clean_text = sys_internal_pattern.sub(extract_meta, response)
        for pattern, replacement in self.scrub_patterns:
            clean_text = re.sub(pattern, replacement, clean_text)
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
                    "meta_logs": extracted_meta_logs}
        if len(sanitized_response.strip()) < 5:
            return {"valid": False, "reason": "STUTTER", "replacement": "The vision fractures. Static remains.", "meta_logs": extracted_meta_logs}
        return {"valid": True, "content": sanitized_response, "meta_logs": extracted_meta_logs}

class TheCortex:
    def __init__(self, services: CortexServices, llm_client=None):
        self.svc = services
        self.events = services.events
        self.dreamer = DreamEngine(self.events)
        self.dialogue_buffer = []
        self.MAX_HISTORY = 15
        self.modulator = NeurotransmitterModulator(bio_ref=self.svc.bio, events_ref=self.events)
        self.boot_history = TelemetryService.get_instance().read_recent_history(limit=4)
        self.last_physics = {}
        self.consultant = services.consultant
        self.llm = llm_client or LLMInterface(self.events, provider="mock", dreamer=self.dreamer)
        self.symbiosis = services.symbiosis
        from bone_drivers import SynergeticLensArbiter
        self.arbiter = SynergeticLensArbiter(self.events)
        if not hasattr(self.llm, 'dreamer') or self.llm.dreamer is None:
            self.llm.dreamer = self.dreamer
        self.composer = PromptComposer()
        self.spotlight = NarrativeSpotlight()
        self.validator = ResponseValidator()
        self.ballast_active = False
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("AIRSTRIKE", lambda p: setattr(self, 'ballast_active', True))

    @classmethod
    def from_engine(cls, engine_ref, llm_client=None):
        services = CortexServices(
            events=engine_ref.events,
            lexicon=engine_ref.lex,
            inventory=engine_ref.gordon,
            consultant=engine_ref.consultant if hasattr(engine_ref, 'consultant') else None,
            cycle_controller=engine_ref.cycle_controller,
            symbiosis=getattr(engine_ref, 'symbiosis', SymbiosisManager(engine_ref.events)),
            mind_memory=engine_ref.mind.mem,
            bio=getattr(engine_ref, 'bio', None),
            host_stats=getattr(engine_ref, 'host_stats', None),
            village=getattr(engine_ref, 'village', None))
        return cls(services, llm_client)

    @property
    def eng(self):
        class LegacyEngineProxy:
            def __init__(self, services):
                self.gordon = services.inventory
                self.lex = services.lexicon
                self.cycle_controller = services.cycle_controller
                self.tick_count = 0
                self.host_stats = services.host_stats
                self.soul = None

            def get_metrics(self):
                return {"note": "Metrics unavailable in strict service mode"}

        return LegacyEngineProxy(self.svc)

    def _update_history(self, user_text: str, system_text: str):
        self.dialogue_buffer.append(f"User: {user_text} | System: {system_text}")
        if len(self.dialogue_buffer) > self.MAX_HISTORY:
            self.dialogue_buffer.pop(0)

    def _harvest_loot(self, text: str) -> Tuple[str, List[str], List[str]]:
        found, lost = [], []
        for match in re.findall(r"\[\[LOOT:\s*([A-Za-z0-9_\s]+)]]", text):
            found.append(match.strip().replace(" ", "_").upper())
        for match in re.findall(r"\[\[LOST:\s*([A-Za-z0-9_\s]+)]]", text):
            lost.append(match.strip().replace(" ", "_").upper())
        clean_text = re.sub(r"\[\[(LOOT|LOST):.*?]]", "", text)
        return clean_text, found, lost

    def process(self, user_input: str, is_system: bool = False) -> Dict[str, Any]:
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
        if self.consultant and self.consultant.active:
            self._apply_vsl_overlay(full_state, user_input, sim_result)
        if is_boot_sequence:
            self._apply_boot_overlay(full_state, user_input)
            modifiers["include_inventory"] = False
            user_input = "Entering reality..."
        llm_params = self.modulator.modulate(
            base_voltage=full_state["physics"].get("voltage", 5.0),
            latency_penalty=getattr(self.svc.host_stats, "latency", 0.0) if self.svc.host_stats else 0.0)
        if is_boot_sequence:
            llm_params.update({"temperature": 1.3, "top_p": 0.95})
        final_prompt = self.composer.compose(
            full_state, user_input,
            ballast=self.ballast_active, modifiers=modifiers,
            mood_override=self.modulator.get_mood_directive(),
            consultant=self.consultant)
        start_time = time.time()
        raw_resp = self.llm.generate(final_prompt, llm_params)
        final_text, new_loot, lost_loot = self._harvest_loot(raw_resp)
        inv_logs = self._process_inventory_changes(new_loot, lost_loot)
        self._log_telemetry(final_prompt, final_text, full_state, sim_result)
        self.learn_from_response(final_text)
        val_res = self.validator.validate(final_text, full_state)
        final_output = val_res["content"] if val_res["valid"] else val_res["replacement"]
        extracted_logs = val_res.get("meta_logs", [])
        self.svc.symbiosis.monitor_host(time.time() - start_time, final_output, len(final_prompt))
        self._update_history("SYSTEM_INIT" if is_boot_sequence else user_input, final_output)
        sim_result["ui"] = f"{sim_result.get('ui', '')}\n\n{Prisma.WHT}{final_output}{Prisma.RST}"
        if inv_logs: sim_result["ui"] += "\n" + "\n".join(inv_logs)
        if "logs" not in sim_result: sim_result["logs"] = []
        sim_result["logs"].extend(extracted_logs)
        sim_result["raw_content"] = final_output
        self.ballast_active = False
        return sim_result

    def _handle_vsl_command(self, text):
        if not self.consultant: return {"ui": "VSL Unavailable", "logs": []}
        msg = self.consultant.engage() if "start" in text else self.consultant.disengage()
        self.events.log(msg, "VSL")
        return {"ui": f"{Prisma.CYN}{msg}{Prisma.RST}", "logs": [msg]}

    def _apply_vsl_overlay(self, state, text, sim_result):
        if not self.consultant: return
        self.consultant.update_coordinates(text, state.get("bio", {}), state.get("physics"))
        state["mind"]["style_directives"] = [self.consultant.get_system_prompt()]
        sim_result["physics"]["voltage"] = self.consultant.state.B * 30.0

    def _apply_boot_overlay(self, state, text):
        seed = text.replace("SYSTEM_BOOT:", "").strip()
        if "world" not in state: state["world"] = {}
        state["world"]["orbit"] = [seed]
        state["world"]["loci_description"] = f"Manifesting: {seed}"
        state["mind"]["style_directives"] = [
            "You are The Architect.",
            f"TARGET SEED: {seed}",
            "DIRECTIVE: Build the world from the first sensation up.",
            "INTERPRETATION: The seed is a metaphor. If the seed is 'Hospital', make it a place of healing, not necessarily a literal hospital.",
            "STYLE: Sensory. Grounded. Atmospheric.",
            "ANTI-PATTERN: Avoid cliches 'obsidian', 'neon', 'dust motes' and 'pulsing'. Be specific. Always leave a little room for whimsy."]
        state["dialogue_history"] = []

    def _process_inventory_changes(self, found, lost):
        logs = []
        for item in found:
            logs.append(self.svc.inventory.acquire(item))
            if self.events: self.events.publish("ITEM_ACQUIRED", {"item": item})
        for item in lost:
            if self.svc.inventory.safe_remove_item(item):
                logs.append(f"{Prisma.GRY}ENTROPY: {item} consumed/lost.{Prisma.RST}")
            else:
                logs.append(f"{Prisma.OCHRE}GLITCH: Tried to lose {item}, but you didn't have it.{Prisma.RST}")
        return logs

    def _log_telemetry(self, prompt, response, state, sim_result):
        try:
            phys = state.get("physics", {})
            crystal = DecisionCrystal(
                prompt_snapshot=prompt[:500],
                physics_state={"voltage": phys.get("voltage", 0), "narrative_drag": phys.get("narrative_drag", 0)},
                active_archetype=state["mind"].get("lens", "UNKNOWN"),
                council_mandates=[str(m) for m in sim_result.get("council_mandates", [])],
                final_response=response)
            TelemetryService.get_instance().log_crystal(crystal)
        except Exception:
            pass

    def gather_state(self, sim_result: Dict[str, Any]) -> Dict[str, Any]:
        phys = sim_result.get("physics", {})
        bio = sim_result.get("bio", {})
        mind = sim_result.get("mind", {})
        world = sim_result.get("world", {})
        soul_data = sim_result.get("soul", {})
        village_data = {}
        if self.svc.village:
            tinkerer = getattr(self.svc.village, 'tinkerer', None)
            if tinkerer:
                village_data["tinkerer"] = tinkerer.to_dict() if hasattr(tinkerer, 'to_dict') else {}
        full_state = {
            "bio": bio,
            "physics": phys,
            "mind": mind,
            "soul": soul_data,
            "world": world,
            "village": village_data,
            "user_profile": {"name": "Traveler"},
            "meta": {
                "timestamp": time.time()}}
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
                if self.events: self.events.log(f"AUTO-DIDACTIC: Learned '{target}'.", "CORTEX")

    def restore_context(self, history: List[str]):
        if not history:
            return
        self.dialogue_buffer = history[-self.MAX_HISTORY:]
        if self.events:
            self.events.log(f"Cortex re-sequenced {len(self.dialogue_buffer)} synaptic turns.", "BRAIN")

class NeuroPlasticity:
    def __init__(self):
        self.plasticity_mod = 1.0

    @staticmethod
    def force_hebbian_link(graph, word_a, word_b):
        if word_a == word_b: return None
        if word_a not in graph:
            graph[word_a] = {"edges": {}, "last_tick": 0}
        if word_b not in graph:
            graph[word_b] = {"edges": {}, "last_tick": 0}
        current_weight = graph[word_a]["edges"].get(word_b, 0.0)
        new_weight = min(10.0, current_weight + 2.5)
        graph[word_a]["edges"][word_b] = new_weight
        back_weight = graph[word_b]["edges"].get(word_a, 0.0)
        graph[word_b]["edges"][word_a] = min(10.0, back_weight + 1.0)
        return f"{Prisma.MAG}⚡ HEBBIAN GRAFT: Wired '{word_a}' <-> '{word_b}'.{Prisma.RST}"

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
    def __init__(self, events):
        self.events = events
        dreams_data = LoreManifest.get_instance().get("dreams") or {}
        self.PROMPTS = dreams_data.get("PROMPTS", ["{A} -> {B}?"])
        self.NIGHTMARES = dreams_data.get("NIGHTMARES", {})
        self.VISIONS = dreams_data.get("VISIONS", ["Static."])
        self.SURREAL_PROMPTS = dreams_data.get("SURREAL", [
            "You are {A}, but you are also {B}. You are dancing with {C}."])
        self.CONSTRUCTIVE_PROMPTS = dreams_data.get("CONSTRUCTIVE", [
            "You are building a cathedral out of {A}. The mortar is {B}."])

    def enter_rem_cycle(self, soul_snapshot: Dict[str, Any], bio_state: Dict[str, Any]) -> str:
        voltage = bio_state.get("voltage", 0.0)
        trauma = bio_state.get("trauma_vector", 0.0)
        memories = soul_snapshot.get("core_memories", [])
        dream_mode = "LUCID"
        if trauma > 40.0:
            dream_mode = "NIGHTMARE"
        elif voltage > 15.0:
            dream_mode = "MANIC"
        elif voltage < 5.0:
            dream_mode = "DORMANT"
        anchors = []
        for mem in memories:
            if isinstance(mem, dict):
                anchors.extend(mem.get("trigger_words", []))
            else:
                anchors.extend(getattr(mem, "trigger_words", []))
        if not anchors:
            anchors = ["static", "void", "humming"]
        primary_symbol = random.choice(anchors).upper()
        abstract_concept = "ENTROPY"
        if hasattr(self, 'lex'):
            abstract_concept = self.lex.get_random_word("ABSTRACT") or "SILENCE"
        dream_log = ""
        if dream_mode == "NIGHTMARE":
            dream_log = (
                f"{Prisma.RED}[REM]: The {primary_symbol} is rotting. "
                f"It smells like {abstract_concept.lower()} and old copper.{Prisma.RST}")
            return dream_log, {"adrenaline": 0.2, "narrative_drag": -1.0}
        elif dream_mode == "MANIC":
            dream_log = (
                f"{Prisma.MAG}[REM]: {primary_symbol} refracting through a prism of {abstract_concept}. "
                f"Geometry is screaming.{Prisma.RST}")
            return dream_log, {"stamina": -5.0, "voltage": -2.0}
        elif dream_mode == "DORMANT":
            dream_log = f"{Prisma.GRY}[REM]: Deep waters. The {primary_symbol} sinks slowly.{Prisma.RST}"
            return dream_log, {"health": 5.0, "stamina": 10.0}
        else:
            dream_log = (
                f"{Prisma.CYN}[REM]: You are holding the {primary_symbol}. "
                f"It turns into {abstract_concept}. You understand why.{Prisma.RST}")
            return dream_log, {"truth_ratio": 0.1}

    def _weave_dream(self, residue: str, context: str, bridge: str, dream_type: str, subtype: str) -> str:
        if dream_type == "NIGHTMARE":
            templates = self.NIGHTMARES.get(subtype, self.NIGHTMARES.get("BARIC", ["{ghost} is heavy."]))
            template = random.choice(templates)
            return template.format(ghost=residue)
        if dream_type == "SURREAL":
            template = random.choice(self.SURREAL_PROMPTS)
            return template.format(A=residue, B=context, C=bridge)
        if dream_type == "CONSTRUCTIVE":
            template = random.choice(self.CONSTRUCTIVE_PROMPTS)
            return template.format(A=residue, B=context, C=bridge)
        if dream_type == "LUCID":
            return f"You hold '{residue}' in your hand. You control its shape. It becomes '{context}'."
        template = random.choice(self.PROMPTS)
        return template.format(A=residue, B=context)

    def hallucinate(self, vector: Dict[str, float], trauma_level: float = 0.0) -> Tuple[str, float]:
        dims = [k for k, v in vector.items() if v > 0.3]
        if not dims: dims = ["VOID"]
        val_a = dims[0]
        val_b = "ENTROPY" if trauma_level > 5.0 else (dims[1] if len(dims) > 1 else "SILENCE")
        if "DEL" in dims:
            return f"The concept of {val_a} turns into a balloon and floats away.", 5.0
        if trauma_level > 5.0:
            cat = "SEPTIC" if vector.get("ENT", 0) > 0.5 else "BARIC"
            template = random.choice(self.NIGHTMARES.get(cat, self.NIGHTMARES.get("BARIC", ["{ghost} is heavy."])))
            content = template.format(ghost=val_a)
        else:
            template = random.choice(self.PROMPTS)
            content = template.format(A=val_a, B=val_b)
        return content, 0.0

    def run_defragmentation(self, memory_system: Any, limit: int = 5) -> str:
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
    def __init__(self, mind_layer, bio_layer, events):
        self.mind = mind_layer
        self.bio = bio_layer
        from bone_drivers import SynergeticLensArbiter
        self.arbiter = SynergeticLensArbiter(events)

    def think(self, physics_packet, _bio, inventory, voltage_history, tick_count, soul_ref=None):
        voltage = physics_packet.get("voltage", 0.0)
        clean_words = physics_packet.get("clean_words", [])

        avg_v = sum(voltage_history) / len(voltage_history) if voltage_history else 0
        ignition = min(1.0, (avg_v / 20.0) * (len(clean_words) / 10.0))

        if voltage > 12.0 and random.random() < 0.15:
            if len(clean_words) >= 2:
                w1, w2 = random.sample(clean_words, 2)
                self._force_link(self.mind.mem.graph, w1, w2)

        mind_data = self.arbiter.consult(
            physics_packet,
            _bio,
            inventory,
            tick_count,
            soul_ref=soul_ref,
            _ignition_score=ignition)

        if isinstance(mind_data, tuple):
            mind_data = {"lens": mind_data[0], "context_msg": mind_data[1], "role": mind_data[2]}

        return {
            "mode": "COGNITIVE",
            "lens": mind_data.get("lens"),
            "context_msg": mind_data.get("context_msg"),
            "role": mind_data.get("role"),
            "ignition": ignition,
            "physics": physics_packet,
            "bio": self.bio.endo.get_state() if hasattr(self.bio, 'endo') else {}}

    def _force_link(self, graph, wa, wb):
        for a, b in [(wa, wb), (wb, wa)]:
            if a not in graph: graph[a] = {"edges": {}, "last_tick": 0}
            graph[a]["edges"][b] = min(10.0, graph[a]["edges"].get(b, 0) + 2.5)
