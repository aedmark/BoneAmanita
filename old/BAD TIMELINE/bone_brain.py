""" bone_brain.py
# "The brain is a machine for jumping to conclusions." - S. Pinker """

import re, time, json, urllib.request, urllib.error, random, math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from bone_data import LENSES, DREAMS
from bone_bus import Prisma, BoneConfig, EventBus
from bone_symbiosis import SymbiosisManager
from bone_spores import MycelialNetwork
from bone_lexicon import TheLexicon
from bone_translation import RosettaStone
from bone_telemetry import TelemetryService, DecisionCrystal, BlackBoxReader
from bone_physics import cosine_similarity

@dataclass
class BrainConfig:
    BASE_PLASTICITY: float = 0.4
    VOLTAGE_SENSITIVITY: float = 0.03
    MAX_PLASTICITY: float = 0.95
    BASE_DECAY_RATE: float = 0.1
    BASE_TEMP: float = 0.7
    BASE_TOP_P: float = 0.9
    CORTISOL_FREEZE: float = 0.2
    DOPAMINE_NOVELTY: float = 0.4
    ADRENALINE_RUSH: float = 600.0
    SEROTONIN_CALM: float = 0.5


@dataclass
class ChemicalState:
    dopamine: float = 0.0
    cortisol: float = 0.0
    adrenaline: float = 0.0
    serotonin: float = 0.0

    def decay(self, rate: float = 0.2):
        self.dopamine = max(0.0, self.dopamine * (1.0 - rate))
        self.cortisol = max(0.0, self.cortisol * (1.0 - rate))
        self.adrenaline = max(0.0, self.adrenaline * (1.0 - rate))
        self.serotonin = max(0.0, self.serotonin * (1.0 - rate))

    def mix(self, new_state: Dict[str, float], weight: float = 0.5):
        self.dopamine = (self.dopamine * (1.0 - weight)) + (new_state.get("DOP", 0.0) * weight)
        self.cortisol = (self.cortisol * (1.0 - weight)) + (new_state.get("COR", 0.0) * weight)
        self.adrenaline = (self.adrenaline * (1.0 - weight)) + (new_state.get("ADR", 0.0) * weight)
        self.serotonin = (self.serotonin * (1.0 - weight)) + (new_state.get("SER", 0.0) * weight)


class NarrativeSpotlight:
    def __init__(self):
        self.dimension_map = {
            "STR": {"heavy", "constructive", "base"},
            "VEL": {"kinetic", "explosive", "mot"},
            "ENT": {"antigen", "toxin", "broken", "void"},
            "PHI": {"thermal", "photo", "explosive"},
            "PSI": {"abstract", "sacred", "void", "idea"},
            "BET": {"suburban", "solvents", "play"}}
        self.semantic_drift_factor = 0.1

    def expand_horizon(self, dimension: str, new_category: str):
        if dimension in self.dimension_map:
            self.dimension_map[dimension].add(new_category)

    def illuminate(self, graph: Dict, vector: Dict[str, float], limit: int = 5) -> List[str]:
        if not graph or not vector:
            return []
        active_dims = {k: v for k, v in vector.items() if v > 0.6}
        if not active_dims:
            return []
        scored_memories = []
        secondary_candidates = set()
        for node, data in graph.items():
            resonance_score = 0.0
            if TheLexicon:
                node_cats = TheLexicon.get_categories_for_word(node)
                for dim, val in active_dims.items():
                    target_flavors = self.dimension_map.get(dim, set())
                    if node_cats & target_flavors:
                        resonance_score += (val * 1.5)
                        for neighbor in data.get("edges", {}):
                            secondary_candidates.add(neighbor)
            mass = sum(data.get("edges", {}).values())
            resonance_score += (mass * 0.1)
            if resonance_score > 0.7:
                scored_memories.append((resonance_score, node, data))
        for neighbor in secondary_candidates:
            if neighbor not in graph: continue
            scored_memories.append((0.4, neighbor, graph[neighbor]))
        unique_memories = {}
        for score, name, data in scored_memories:
            if name not in unique_memories or score > unique_memories[name][0]:
                unique_memories[name] = (score, data)
        final_list = [(s, n, d) for n, (s, d) in unique_memories.items()]
        final_list.sort(key=lambda x: x[0], reverse=True)
        top_n = final_list[:limit]
        results = []
        for score, name, data in top_n:
            connections = list(data.get("edges", {}).keys())
            conn_str = f" -> [{', '.join(connections[:2])}]" if connections else ""
            prefix = "Resonant" if score > 0.5 else "Associated"
            results.append(f"{prefix} Engram: '{name.upper()}'{conn_str}")
        return results


class NeurotransmitterModulator:
    def __init__(self):
        self.current_chem = ChemicalState()
        self.last_tick = time.time()
        self.lens_profiles = {
            "SHERLOCK": {"cortisol_dampener": 0.2, "adrenaline_boost": 0.5},
            "NATHAN": {"cortisol_dampener": 1.5, "adrenaline_boost": 1.5},
            "JESTER": {"cortisol_dampener": 0.0, "adrenaline_boost": 2.0},
            "NARRATOR": {"cortisol_dampener": 1.0, "adrenaline_boost": 1.0},
            "GORDON": {"cortisol_dampener": 0.8, "adrenaline_boost": 0.8}}

    def force_state(self, state_name: str):
        if state_name == "MANIC":
            self.current_chem.dopamine = 1.0
            self.current_chem.adrenaline = 1.0
            self.current_chem.cortisol = 0.2
            self.current_chem.serotonin = 0.0
        elif state_name == "DEPRESSED":
            self.current_chem.dopamine = 0.0
            self.current_chem.serotonin = 0.0
            self.current_chem.cortisol = 0.8

    def modulate(self, incoming_chem: Dict[str, float], base_voltage: float, lens_name: str = "NARRATOR",
                 model_name: str = "") -> Dict[str, Any]:
        decay_amount = BrainConfig.BASE_DECAY_RATE
        self.current_chem.decay(rate=decay_amount)
        plasticity = BrainConfig.BASE_PLASTICITY + (base_voltage * BrainConfig.VOLTAGE_SENSITIVITY)
        plasticity = max(0.1, min(BrainConfig.MAX_PLASTICITY, plasticity))
        self.current_chem.mix(incoming_chem, weight=plasticity)
        base_temp = BrainConfig.BASE_TEMP
        stress_dampener = self.current_chem.cortisol * 0.5
        curiosity_boost = self.current_chem.dopamine * 0.4
        final_temp = base_temp - stress_dampener + curiosity_boost
        final_temp = max(0.1, min(1.5, final_temp))
        base_tokens = 720
        params = {
            "temperature": round(final_temp, 2),
            "top_p": BrainConfig.BASE_TOP_P,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "max_tokens": getattr(BoneConfig, "MAX_OUTPUT_TOKENS", 4096)}
        effective_adrenaline = self.current_chem.adrenaline
        if effective_adrenaline > 0.3:
            extra_tokens = BrainConfig.ADRENALINE_RUSH * effective_adrenaline
            params["max_tokens"] = int(base_tokens + extra_tokens)
            params["frequency_penalty"] = 0.2
        else:
            params["max_tokens"] = base_tokens
        if "gemma" in model_name.lower() or "3" in model_name.lower():
            params["temperature"] = min(0.9, params["temperature"])
        params["max_tokens"] = max(100, params["max_tokens"])
        return params


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
                    self.events.log(f"{Prisma.CYN}⚡ SYNAPSE: Nerve healing. Attempting reconnection...{Prisma.RST}","SYS")
                return True
            return False
        return True

    def _transmit(self, payload: Dict[str, Any], timeout: float = 60.0, max_retries: int = 2) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"}
        data = json.dumps(payload).encode("utf-8")
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(self.base_url, data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    if response.status == 200:
                        body = response.read().decode("utf-8")
                        result = json.loads(body)
                        choices = result.get("choices", [])
                        if not choices:
                            return ""
                        return choices[0].get("message", {}).get("content", "")
                    raise Exception(f"HTTP {response.status}")
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    backoff = 1.0 * (attempt + 1)
                    if self.events:
                        self.events.log(f"{Prisma.YEL}⚡ SYNAPSE FLICKER: Retrying in {backoff}s... ({e}){Prisma.RST}", "SYS")
                    time.sleep(backoff)
        raise last_error

    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        if "reset" in prompt.lower() and "system" in prompt.lower():
            self.failure_count = 0
            self.circuit_state = "CLOSED"
            return "[SYSTEM]: Circuit Breaker Manually Reset."
        if not self._is_synapse_active():
            return self.mock_generation(prompt, reason=f"CIRCUIT_BROKEN")
        if self.provider == "mock":
            return self.mock_generation(prompt)
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False}
        payload.update(params)
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                timeout = 10.0 if self.circuit_state == "HALF_OPEN" else 60.0
                content = self._transmit(payload, timeout)
                if not content or len(content.strip()) < 2:
                    raise ValueError("Response too short or empty")
                if self.circuit_state != "CLOSED" and self.events:
                    self.events.log(f"{Prisma.GRN}⚡ SYNAPSE RESTORED.{Prisma.RST}", "SYS")
                self.failure_count = 0
                self.circuit_state = "CLOSED"
                return content
            except (ValueError, json.JSONDecodeError) as e:
                if self.events:
                    self.events.log(f"{Prisma.OCHRE}⚡ SYNAPSE GLITCH (Attempt {attempt}): {e}{Prisma.RST}", "SYS")
                if attempt == max_retries:
                    return self.mock_generation(prompt, reason="MALFORMED_OUTPUT")
                time.sleep(0.5 * (attempt + 1))
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.circuit_state = "OPEN"
                    if self.events:
                        self.events.log(f"{Prisma.RED}⚡ SYNAPSE SEVERED: {e}{Prisma.RST}", "CRIT")
                    return self.mock_generation(prompt, reason="SEVERED")
                if self.provider != "ollama" and self.circuit_state != "OPEN":
                    fallback = self._local_fallback(prompt, params)
                    if "FALLBACK_DEAD" not in fallback:
                        return fallback
                time.sleep(1.0 * (attempt + 1))
        return self.mock_generation(prompt, reason="SILENCE")

    def _local_fallback(self, prompt: str, params: Dict) -> str:
        fallback_url = "http://127.0.0.1:11434/v1/chat/completions"
        target_model = self.model if self.model else getattr(BoneConfig, "OLLAMA_MODEL_ID", "llama3")
        payload = {
            "model": target_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "temperature": params.get('temperature', 0.7)}
        try:
            headers = {"Content-Type": "application/json"}
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(fallback_url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=10.0) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode("utf-8"))
                    return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            pass
        return self.mock_generation(prompt, reason="FALLBACK_DEAD")

    def mock_generation(self, prompt: str, reason: str = "SIMULATION") -> str:
        if self.dreamer:
            seed_vector = {"ENTROPY": len(prompt) % 10, "VOID": 5.0}
            hallucination, _ = self.dreamer.hallucinate(seed_vector, trauma_level=2.0)
            return f"[{reason}]: {hallucination}"
        return f"[{reason}]: The wire hums. There is no signal."

class ContextWindowManager:
    CHARS_PER_TOKEN = 3.5

    def compose_context(self, layout: Dict[str, Any], max_tokens: int = 4000) -> str:
        inv_str = layout.get('inventory', '')
        base_elements = [f"Location: {layout['location']}", inv_str] if inv_str else [f"Location: {layout['location']}"]
        history_str = ""
        recent_history = layout.get("history", [])
        if recent_history:
            history_str = "\n[PREVIOUSLY]\n" + "\n".join(recent_history)
        base_str = (
            f"[DIRECTOR'S NOTES]\n{' | '.join(layout['notes'])}\n"
            f"[SCENE CONTEXT]\n{' | '.join(base_elements)}\n"
            f"{history_str}\n"
            f"[ACTION]\nUser: {layout['user_query']}\n{layout['role']}:")
        memories = layout.get("memories", [])
        memory_str = ""
        used_tokens = len(base_str) / self.CHARS_PER_TOKEN
        available = max_tokens - used_tokens
        if memories and available > 50:
            kept = []
            for m in memories:
                cost = len(m) / self.CHARS_PER_TOKEN
                if cost < available:
                    kept.append(m)
                    available -= cost
            if kept:
                memory_str = "Memory Echoes: " + " | ".join(kept)
        final_scene = list(base_elements)
        if memory_str: final_scene.append(memory_str)
        return (
            f"[DIRECTOR'S NOTES]\n{' | '.join(layout['notes'])}\n"
            f"[SCENE CONTEXT]\n{' | '.join(final_scene)}\n"
            f"{history_str}\n"
            f"[ACTION]\nUser: {layout['user_query']}\n{layout['role']}:")

class PromptComposer:
    def __init__(self):
        self.context_manager = ContextWindowManager()

    def compose(self, state: Dict[str, Any], user_query: str, ballast: bool = False,
                modifiers: Dict[str, bool] = None) -> str:
        modifiers = self._normalize_modifiers(modifiers)
        mind = state.get("mind", {})
        role = mind.get("role", "The Observer")
        bio = state.get("bio", {})
        chem = bio.get("chem", {})
        mood = "Neutral"
        if chem.get("ADR", 0) > 0.6: mood = "High Alert / Adrenaline"
        if chem.get("COR", 0) > 0.6: mood = "Defensive / Anxious"
        if chem.get("DOP", 0) > 0.6: mood = "Curious / Manic"
        vocab_bias = mind.get("lexicon_bias", "standard")
        vocab_instruction = f"Flavor: Subtly influence word choice with '{vocab_bias}' themes, but prioritize clarity."
        if vocab_bias == "standard":
            vocab_instruction = "Style: Standard, clear English."
        style_notes = [
            f"Voice: {role}.",
            f"Current Mood: {mood}.",
            vocab_instruction]
        persona_directives = mind.get("style_directives", [])
        if persona_directives:
            style_notes.extend(persona_directives)
        style_notes.extend([
            "Constraint: Be concise. Do NOT use 'As an AI'.",
            "Constraint: If the user offers a concept, play with it. Don't just analyze it."
        ])
        if not any("inventory" in d.lower() for d in persona_directives):
            style_notes.append("Constraint: Do not recite the inventory list unless the user asks.")
        if modifiers.get("soften"):
            style_notes.append("TONE OVERRIDE: Be warm, helpful, and clear. Act as a mentor guiding a new user. Avoid being cryptic.")
        if ballast:
            style_notes.append("SAFETY OVERRIDE: Ground the user. Focus on physical objects. Be literal.")
        loc = state.get('world', {}).get('orbit', ['Void'])[0]
        inv_str = ""
        if modifiers["include_inventory"]:
            inv = state.get("inventory", [])
            if inv:
                items = ", ".join(inv)
                inv_str = f"Belt (Accessible): {items}"
            else:
                inv_str = "Hands: Empty"
        memories = []
        if modifiers["include_memories"]:
            memories = state.get("spotlight", [])
        history = state.get("dialogue_history", [])
        layout = {
            "notes": style_notes,
            "location": loc,
            "inventory": inv_str,
            "memories": memories,
            "history": history,
            "user_query": self._sanitize(user_query),
            "role": role}
        return self.context_manager.compose_context(layout, max_tokens=BoneConfig.MAX_OUTPUT_TOKENS if hasattr(BoneConfig, 'MAX_OUTPUT_TOKENS') else 4000)

    @staticmethod
    def _sanitize(text: str) -> str:
        safe = text.replace('"""', "'''").replace('```', "'''")
        return re.sub(r"(?i)^SYSTEM:", "User-System:", safe, flags=re.MULTILINE)

    def _normalize_modifiers(self, modifiers: Optional[Dict]) -> Dict:
        defaults = {
            "include_somatic": True,
            "include_inventory": True,
            "include_memories": True,
            "grace_period": False}
        if modifiers:
            defaults.update(modifiers)
        return defaults


class ResponseValidator:
    def __init__(self):
        self.banned_phrases = [
            "large language model", "AI assistant", "cannot feel", "as an AI",
            "against my programming", "cannot comply", "language model"]
        self.immersion_break_msg = f"{Prisma.GRY}[The system attempts to recite a EULA, but hiccups instead.]{Prisma.RST}"

    def validate(self, response: str, _state: Dict) -> Dict:
        low_resp = response.lower()
        for phrase in self.banned_phrases:
            if phrase.lower() in low_resp:
                return {
                    "valid": False,
                    "reason": "IMMERSION_BREAK",
                    "replacement": self.immersion_break_msg}
        if len(response.strip()) < 2:
            return {"valid": False, "reason": "TOO_SHORT", "replacement": "..."}
        return {"valid": True, "content": response}


class TheCortex:
    def __init__(self, engine_ref, llm_client=None):
        self.sub = engine_ref
        self.events = engine_ref.events
        self.dreamer = DreamEngine(self.events)
        self.dialogue_buffer = []
        self.MAX_HISTORY = 5
        self.black_box = BlackBoxReader()
        self.boot_history = self.black_box.get_recent_history(limit=4)
        self.last_physics = {}
        if llm_client:
            self.llm = llm_client
            if not hasattr(self.llm, 'dreamer') or self.llm.dreamer is None:
                self.llm.dreamer = self.dreamer
        else:
            self.llm = LLMInterface(self.events, provider="mock", dreamer=self.dreamer)
        self.composer = PromptComposer()
        self.modulator = NeurotransmitterModulator()
        self.spotlight = NarrativeSpotlight()
        self.symbiosis = SymbiosisManager(self.events)
        self.validator = ResponseValidator()
        self.ballast_active = False
        self.ballast_counter = 0
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("AIRSTRIKE", self._handle_airstrike)

    def _handle_airstrike(self, _payload):
        self.events.log("AIRSTRIKE: Engaging defensive ballast.", "CORTEX")
        self.ballast_active = True
        self.ballast_counter = 5

    def _update_history(self, user_text: str, system_text: str):
        entry = f"User: {user_text} | System: {system_text}"
        self.dialogue_buffer.append(entry)
        if len(self.dialogue_buffer) > self.MAX_HISTORY:
            self.dialogue_buffer.pop(0)

    def process(self, user_input: str) -> Dict[str, Any]:
        sim_result = self.sub.cycle_controller.run_turn(user_input)
        if sim_result.get("type") not in ["SNAPSHOT", "GEODESIC_FRAME", None]:
            return sim_result
        full_state = self._gather_state(sim_result)
        voltage = full_state["physics"].get("voltage", 5.0)
        chem = full_state["bio"].get("chem", {})
        current_lens = full_state["mind"].get("lens", "NARRATOR")
        model_id = self.llm.model if hasattr(self.llm, "model") else "unknown"
        llm_params = self.modulator.modulate(chem, voltage, lens_name=current_lens, model_name=model_id)
        modifiers = self.symbiosis.get_prompt_modifiers()
        if self.sub.tick_count < 5: modifiers["grace_period"] = True
        if self.ballast_active:
            self.ballast_counter -= 1
            if self.ballast_counter <= 0: self.ballast_active = False
        final_prompt = self.composer.compose(
            full_state,
            user_input,
            ballast=self.ballast_active,
            modifiers=modifiers)
        start_time = time.time()
        raw_response_text = self.llm.generate(final_prompt, llm_params)
        try:
            p_data = full_state.get("physics", {})
            def _get_p(k):
                return p_data.get(k, 0) if isinstance(p_data, dict) else getattr(p_data, k, 0)
            physics_snapshot = {
                "voltage": _get_p("voltage"),
                "narrative_drag": _get_p("narrative_drag"),
                "beta_index": _get_p("beta_index")}
            mandates = [str(m) for m in sim_result.get("council_mandates", [])]
            crystal = DecisionCrystal(
                prompt_snapshot=final_prompt[:1000] + "..." if len(final_prompt) > 1000 else final_prompt,
                physics_state=physics_snapshot,
                active_archetype=full_state["mind"].get("lens", "UNKNOWN"),
                chorus_weights={full_state["mind"].get("lens", "UNKNOWN"): 1.0},
                council_mandates=mandates,
                final_response=raw_response_text)
            TelemetryService.get_instance().log_crystal(crystal)
        except Exception as e:
            if self.events:
                self.events.log(f"AUDIT FAILURE: {e}", "SYS")
        latency = time.time() - start_time
        system_vector = full_state["physics"].get("vector", {})
        response_vector = self.sub.lex.vectorize(raw_response_text)
        alignment_score = cosine_similarity(system_vector, response_vector)
        physics_data = sim_result.get("physics")
        if alignment_score < 0.3 and self.sub.tick_count > 5:
            self.events.log(f"{Prisma.OCHRE}DIVERGENCE ({alignment_score:.2f}): The Ghost is wandering.{Prisma.RST}",
                            "CORTEX")
            if physics_data and isinstance(physics_data, dict):
                self.last_physics = physics_data
                voltage = physics_data.get("voltage", 0.0)
                if voltage > 18.0:
                    self.modulator.force_state("MANIC")
                sim_result["physics"]["voltage"] = voltage + 1.0
            if hasattr(self.sub.phys, "dynamics"):
                pass
            if isinstance(physics_data, dict):
                self.last_physics = physics_data
                voltage = physics_data.get("voltage", 0.0)
                if voltage > 18.0:
                    self.modulator.force_state("MANIC")
                sim_result["physics"]["voltage"] = sim_result["physics"].get("voltage", 0) + 1.0
        validation_result = self.validator.validate(raw_response_text, full_state)
        final_response_text = validation_result["content"] if validation_result["valid"] else validation_result[
            "replacement"]
        self.learn_from_response(final_response_text)
        self.symbiosis.monitor_host(latency=latency, response_text=final_response_text, prompt_len=len(final_prompt))
        self._audit_solipsism(final_response_text, lens_name=current_lens)
        self._update_history(user_input, final_response_text)
        sim_result["ui"] = f"{sim_result.get('ui', '')}\n\n{Prisma.WHT}{final_response_text}{Prisma.RST}"
        return sim_result

    def _gather_state(self, sim_result):
        current_tick = self.sub.tick_count if hasattr(self.sub, 'tick_count') else 0
        phys_packet = self.sub.phys.observer.last_physics_packet
        bio_state = {
            "chem": self.sub.bio.endo.get_state(),
            "atp": self.sub.bio.mito.state.atp_pool}
        inventory = self.sub.gordon.inventory
        mind_data = self.sub.noetic.arbiter.consult(
            phys_packet,
            bio_state,
            inventory,
            current_tick)
        if isinstance(mind_data, tuple):
            mind_data = {
                "lens": mind_data[0],
                "role": mind_data[2],
                "style_directives": ["Neutral tone."],
                "lexicon_bias": "abstract"}
        active_history = self.dialogue_buffer
        if not active_history and self.boot_history:
            active_history = [f"[PREVIOUSLY]: {entry}" for entry in self.boot_history]

        return {
            "bio": bio_state,
            "physics": phys_packet,
            "mind": mind_data,
            "dialogue_history": active_history,
            "user_profile": self.sub.mind.mirror.profile.__dict__,
            "world": {"orbit": sim_result.get("world_state", {}).get("orbit", ["Void"])},
            "inventory": inventory,
            "semantic_operators": self.sub.gordon.get_semantic_operators(),
            "soul_state": self.sub.soul.get_soul_state(),
            "spotlight": self.spotlight.illuminate(
                self.sub.mind.mem.graph,
                phys_packet.get("vector", {}))}

    def _audit_solipsism(self, text: str, lens_name: str = "NARRATOR"):
        words = text.lower().split()
        if not words: return
        self_refs = words.count("i") + words.count("me") + words.count("my")
        density = self_refs / len(words)
        if density > 0.2:
            self.events.log(f"SOLIPSISM DETECTED ({density:.2f}). Ego is thickening.", "SYS")

    def learn_from_response(self, response_text):
        words = self.sub.lex.sanitize(response_text)
        unknowns = [w for w in words if not self.sub.lex.get_categories_for_word(w)]
        if unknowns and len(unknowns) < 5:
            target = random.choice(unknowns)
            if len(target) > 4:
                self.sub.lex.teach(target, "kinetic", self.sub.tick_count)
                self.events.log(f"AUTO-DIDACTIC: Learned '{target}' from self.", "CORTEX")


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
        self.PROMPTS = DREAMS.get("PROMPTS", ["{A} -> {B}?"])
        self.NIGHTMARES = DREAMS.get("NIGHTMARES", {})
        self.VISIONS = DREAMS.get("VISIONS", ["Static."])

    def enter_rem_cycle(self, memory_system: Any, bio_readout: Dict[str, Any] = None) -> str:
        """ Generates a dream based on Memory (Content) and Biology (Tone). """
        residue_word = "static"
        context_word = "void"

        if hasattr(memory_system, "graph") and memory_system.graph:
            sorted_nodes = sorted(
                memory_system.graph.items(),
                key=lambda item: item[1].get("last_tick", 0),
                reverse=True)
            if sorted_nodes:
                residue_word = sorted_nodes[0][0]
                if len(sorted_nodes) > 1:
                    context_word = sorted_nodes[1][0]
        dream_type = "NORMAL"
        subtype = "ABSTRACT"
        if bio_readout:
            chem = bio_readout.get("chem", {})
            mito = bio_readout.get("mito", {})
            phys = bio_readout.get("physics", {})
            cortisol = chem.get("COR", 0.0)
            ros = mito.get("ros", 0.0)
            voltage = phys.get("voltage", 0.0)
            atp = mito.get("atp", 100.0)
            if ros > 8.0:
                dream_type = "NIGHTMARE"
                subtype = "SEPTIC"
            elif cortisol > 0.6:
                dream_type = "NIGHTMARE"
                subtype = "BARIC"
            elif voltage > 20.0:
                dream_type = "NIGHTMARE"
                subtype = "THERMAL"
            elif atp < 15.0:
                dream_type = "NIGHTMARE"
                subtype = "CRYO"
            elif chem.get("DOP", 0.0) > 0.7:
                dream_type = "LUCID"
        dream_text = self._weave_dream(residue_word, context_word, dream_type, subtype)
        consolidation_msg = "Neural pathways consolidated."
        if hasattr(memory_system, "replay_dreams"):
            consolidation_msg = memory_system.replay_dreams()
        return (
            f"{Prisma.VIOLET}☾ REM CYCLE [{dream_type}:{subtype}] ☽{Prisma.RST}\n"
            f"   Day Residue: '{residue_word.upper()}' detected.\n"
            f"   Dream: \"{dream_text}\"\n"
            f"   {Prisma.GRY}{consolidation_msg}{Prisma.RST}")

    def _weave_dream(self, residue: str, context: str, dream_type: str, subtype: str) -> str:
        if dream_type == "NIGHTMARE":
            templates = self.NIGHTMARES.get(subtype, self.NIGHTMARES.get("BARIC", ["{ghost} is heavy."]))
            template = random.choice(templates)
            return template.format(ghost=residue)
        if dream_type == "LUCID":
            return f"You hold '{residue}' in your hand. You control its shape. It becomes '{context}'."
        template = random.choice(self.PROMPTS)
        return template.format(A=residue, B=context)

    def hallucinate(self, vector: Dict[str, float], trauma_level: float = 0.0) -> Tuple[str, float]:
        dims = [k for k, v in vector.items() if v > 0.3]
        if not dims: dims = ["VOID"]
        val_a = dims[0]
        val_b = "ENTROPY" if trauma_level > 5.0 else (dims[1] if len(dims) > 1 else "SILENCE")
        if trauma_level > 5.0:
            cat = "SEPTIC" if vector.get("ENT", 0) > 0.5 else "BARIC"
            template = random.choice(self.NIGHTMARES.get(cat, self.NIGHTMARES["BARIC"]))
            content = template.format(ghost=val_a)
        else:
            template = random.choice(self.PROMPTS)
            content = template.format(A=val_a, B=val_b)
        return content, 0.0

class GlobalIntegrator:
    def __init__(self):
        self.global_coherence = 0.0

    def measure_ignition(self, clean_words: List[str], voltage_history: List[float]) -> Tuple[float, float, float]:
        if not voltage_history: return 0.0, 0.0, 0.0
        avg_voltage = sum(voltage_history) / len(voltage_history)
        word_density = len(clean_words) / 10.0
        ignition = min(1.0, (avg_voltage / 20.0) * word_density)
        coherence = 1.0 - (abs(voltage_history[-1] - avg_voltage) / 20.0)
        return ignition, coherence, 0.0

class WisdomAllocator:
    def __init__(self):
        self.insight_depth = 0.0

    def get_readout(self):
        return f"Insight: {self.insight_depth:.2f}"

    def architect(self, context_packet: Dict[str, Any], mind_tuple: Tuple, is_dream: bool) -> Dict[str, str]:
        lens = mind_tuple[0] if mind_tuple else "UNKNOWN"
        role = mind_tuple[2] if len(mind_tuple) > 2 else "Observer"
        mode = "REM_CYCLE" if is_dream else "WAKING_LIFE"
        physics = context_packet.get("physics", {})
        voltage = physics.get("voltage", 0.0) if isinstance(physics, dict) else getattr(physics, "voltage", 0.0)
        chapter_title = "The Flatline"
        if voltage > 15.0:
            chapter_title = "The Surge"
        elif voltage > 5.0:
            chapter_title = "The Flow"
        return {
            "mode": mode,
            "lens": lens,
            "role": role,
            "chapter": chapter_title,
            "insight": self.get_readout()}