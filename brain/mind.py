"""brain/mind.py"""

import math
import random
import re
import hashlib
from collections import deque
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
from brain.ann import MemoryConsolidator

try:
    import numpy as np
except ImportError:
    np = None
from constants import Prisma
from struts import ux, safe_get
from presets import BoneConfig

@dataclass
class ChemicalState:
    dopamine: float = 0.2
    cortisol: float = 0.1
    adrenaline: float = 0.1
    serotonin: float = 0.2
    config_ref: Any = None

    def homeostasis(self, rate: float = 0.1):
        safe_rate = max(0.0, min(1.0, rate))
        cfg = safe_get(self.config_ref or BoneConfig, "CORTEX", {})
        self.dopamine += (float(safe_get(cfg, "RESTING_DOPAMINE", 0.2)) - self.dopamine) * safe_rate
        self.cortisol += (float(safe_get(cfg, "RESTING_CORTISOL", 0.1)) - self.cortisol) * safe_rate
        self.adrenaline += (float(safe_get(cfg, "RESTING_ADRENALINE", 0.1)) - self.adrenaline) * safe_rate
        self.serotonin += (float(safe_get(cfg, "RESTING_SEROTONIN", 0.2)) - self.serotonin) * safe_rate

    def mix(self, new_state: Dict[str, float], weight: float = 0.5):
        inv_w = 1.0 - weight
        if (val := new_state.get("DOP", new_state.get("dopamine"))) is not None:
            self.dopamine = (self.dopamine * inv_w) + (val * weight)
        if (val := new_state.get("COR", new_state.get("cortisol"))) is not None:
            self.cortisol = (self.cortisol * inv_w) + (val * weight)
        if (val := new_state.get("ADR", new_state.get("adrenaline"))) is not None:
            self.adrenaline = (self.adrenaline * inv_w) + (val * weight)
        if (val := new_state.get("SER", new_state.get("serotonin"))) is not None:
            self.serotonin = (self.serotonin * inv_w) + (val * weight)

class NeurotransmitterModulator:
    def __init__(self, bio_ref, events_ref=None, config_ref=None):
        self.bio = bio_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.current_chem = ChemicalState(config_ref=self.cfg)
        self.last_mood = "NEUTRAL"
        cfg = safe_get(self.cfg, "CORTEX", {})
        self.BASE_TOKENS = int(safe_get(cfg, "BASE_TOKENS", 720))
        self.MAX_TOKENS = int(safe_get(cfg, "MAX_TOKENS", 4096))
        self.SELF_CARE_THRESHOLD = int(safe_get(cfg, "SELF_CARE_THRESHOLD", 10))
        self.starvation_ticks = 0

    def modulate(self, base_voltage: float, latency_penalty: float = 0.0, physics_state: Dict[str, float] = None,
                 simulate: bool = False) -> Dict[str, Any]:
        if physics_state is None:
            physics_state = {}
        cfg = safe_get(self.cfg, "CORTEX", {})
        if not simulate:
            incoming_chem = self.bio.endo.get_state()
            self.current_chem.homeostasis(rate=safe_get(cfg, "BASE_DECAY_RATE", 0.1))
            plasticity = safe_get(cfg, "BASE_PLASTICITY", 0.1) + (
                    base_voltage * safe_get(cfg, "VOLTAGE_SENSITIVITY", 0.05))
            plasticity = max(0.1, min(safe_get(cfg, "MAX_PLASTICITY", 1.0), plasticity))
            self.current_chem.mix(incoming_chem, weight=min(0.5, plasticity))
            if self.current_chem.dopamine < 0.15:
                self.starvation_ticks += 1
                if self.starvation_ticks > self.SELF_CARE_THRESHOLD:
                    self._treat_yourself()
            else:
                self.starvation_ticks = max(0, self.starvation_ticks - 1)
            if latency_penalty > safe_get(cfg, "LATENCY_PENALTY_THRESHOLD", 2.0):
                self.current_chem.cortisol = min(
                    1.0, self.current_chem.cortisol + safe_get(cfg, "LATENCY_CORTISOL_PENALTY", 0.1))
                self.current_chem.adrenaline = min(
                    1.0, self.current_chem.adrenaline + safe_get(cfg, "LATENCY_ADRENALINE_PENALTY", 0.05))
        c = self.current_chem
        current_mood = "NEUTRAL"
        mood_thresholds = safe_get(cfg, "MOOD_THRESHOLDS", {"MANIC_DOP": 0.8, "PANIC_COR": 0.7, "ZEN_SER": 0.8})
        if c.dopamine > mood_thresholds.get("MANIC_DOP", 0.8):
            current_mood = "MANIC"
        elif c.cortisol > mood_thresholds.get("PANIC_COR", 0.7):
            current_mood = "PANIC"
        elif c.serotonin > mood_thresholds.get("ZEN_SER", 0.8):
            current_mood = "ZEN"
        if current_mood != self.last_mood and self.events:
            self.events.publish("NEURAL_STATE_SHIFT", {"state": current_mood,
                                 "chem": {"DOP": c.dopamine, "COR": c.cortisol, "SER": c.serotonin}, }, )
            self.last_mood = current_mood
        v_offset = safe_get(cfg, "TEMP_VOLTAGE_OFFSET", 5.0)
        v_scalar = safe_get(cfg, "TEMP_VOLTAGE_SCALAR", 0.1)
        voltage_heat = math.log1p(max(0.0, base_voltage - v_offset)) * v_scalar
        chem_weights = safe_get(cfg, "TEMP_CHEM_WEIGHTS", {"dop": 0.4, "adr": 0.3, "cor": 0.2})
        chemical_delta = (
                (c.dopamine * chem_weights.get("dop", 0.4)) - (c.adrenaline * chem_weights.get("adr", 0.3)) - (
                c.cortisol * chem_weights.get("cor", 0.2)))
        base_temp = safe_get(cfg, "BASE_TEMP", 0.4)
        base_top_p = safe_get(cfg, "BASE_TOP_P", 0.95)
        chi = float(safe_get(physics_state, "chi", safe_get(physics_state, "entropy", 0.2)))
        beta = float(safe_get(physics_state, "contradiction", safe_get(physics_state, "beta_index", 0.4)))
        ent_offset = safe_get(cfg, "TEMP_ENTROPY_OFFSET", 0.5)
        ent_scalar = safe_get(cfg, "TEMP_ENTROPY_SCALAR", 1.5)
        entropy_bonus = max(0.0, chi - ent_offset) * ent_scalar
        t_limits = safe_get(cfg, "TEMP_LIMITS", (0.4, 1.5))
        raw_temp = base_temp + chemical_delta + voltage_heat + entropy_bonus
        final_temp = round(max(t_limits[0], min(t_limits[1], raw_temp)), 2)
        chi_scalar = safe_get(cfg, "TOP_P_CHI_SCALAR", 0.05)
        final_top_p = min(1.0, base_top_p + (chi * chi_scalar))
        beta_weight = beta * safe_get(cfg, "PEN_BETA_SCALAR", 0.3)
        chi_weight = chi * safe_get(cfg, "PEN_CHI_SCALAR", 0.2)
        base_penalty = min(1.2, 0.5 + beta_weight + chi_weight)
        freq_pen = pres_pen = base_penalty
        token_mods = safe_get(cfg, "TOKEN_CHEM_MODIFIERS", {"dop": 800, "adr": 400, "cor": 200})
        token_delta = ((c.dopamine * token_mods.get("dop", 800)) - (c.adrenaline * token_mods.get("adr", 400)) - (
                c.cortisol * token_mods.get("cor", 200)))
        min_tokens = safe_get(cfg, "MIN_TOKENS", 150.0)
        raw_tokens = self.BASE_TOKENS + token_delta
        max_t = int(max(min_tokens, min(float(self.MAX_TOKENS), raw_tokens)))
        return {"temperature": final_temp, "top_p": final_top_p, "frequency_penalty": round(freq_pen, 2),
                "presence_penalty": round(pres_pen, 2), "max_tokens": max_t, }

    def _treat_yourself(self):
        if self.events:
            msg = ux("brain_strings", "self_care") or "Engaging self-care protocols. Resting."
            self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "SYS")
        self.current_chem.dopamine += 0.2
        self.starvation_ticks = 0

    def get_mood_directive(self) -> str:
        c = self.current_chem
        if c.cortisol > 0.7 and c.adrenaline > 0.7:
            return ux("brain_strings", "mood_panic") or "You are panicking."
        if c.dopamine > 0.8 and c.adrenaline > 0.5:
            return ux("brain_strings", "mood_manic") or "You are manic and inspired."
        if c.serotonin > 0.7:
            return ux("brain_strings", "mood_lucid") or "You are calm and lucid."
        if c.cortisol > 0.6:
            return ux("brain_strings", "mood_defensive") or "You feel defensive and on edge."
        return ux("brain_strings", "mood_neutral") or ""

class NoeticLoop:
    def __init__(self, mind_layer, bio_layer, _events, config_ref=None):
        self.mind = mind_layer
        self.bio = bio_layer
        self.cfg = config_ref or BoneConfig

    def think(self, physics_packet, _bio, _inventory, voltage_history, _tick_count, soul_ref=None, ):
        voltage = float(safe_get(physics_packet, "voltage", 0.0))
        clean_words = safe_get(physics_packet, "clean_words", [])
        avg_v = sum(voltage_history) / len(voltage_history) if voltage_history else 0
        cfg = safe_get(self.cfg, "CORTEX", {})
        v_div = max(1.0, safe_get(cfg, "IGNITION_V_DIV", 20.0))
        w_div = max(1.0, safe_get(cfg, "IGNITION_W_DIV", 10.0))
        link_v = safe_get(cfg, "LINK_VOLTAGE_THRESH", 12.0)
        link_chance = safe_get(cfg, "LINK_CHANCE", 0.15)
        ignition = min(1.0, (avg_v / v_div) * (len(clean_words) / w_div))
        if voltage > link_v and random.random() < link_chance:
            unique_words = list(set(clean_words))
            if len(unique_words) >= 2:
                w1, w2 = random.sample(unique_words, 2)
                self._force_link(self.mind.mem.graph, w1, w2, self.cfg)
                if hasattr(self.bio, "mito"):
                    self.bio.mito.adjust_atp(-1.0, "Spontaneous Semantic Link")
        current_lens = str(safe_get(soul_ref, "archetype", "OBSERVER")).upper() if soul_ref else "OBSERVER"
        current_role = f"The {current_lens.title().replace('_', ' ')}"
        msg_cog = ux("brain_strings",
                     "noetic_ignition") or "Cognition active. Ignition: {ignition:.2f}"
        return {"mode": "COGNITIVE", "lens": current_lens, "context_msg": msg_cog.format(ignition=ignition),
                "role": current_role, "ignition": ignition, "physics": physics_packet,
                "bio": self.bio.endo.get_state() if hasattr(self.bio, "endo") else {}, }

    @staticmethod
    def _force_link(graph, wa, wb, config_ref=None):
        target_cfg = config_ref or BoneConfig
        cfg = safe_get(target_cfg, "CORTEX", {})
        max_edge = safe_get(cfg, "LINK_MAX_WEIGHT", 10.0)
        edge_boost = safe_get(cfg, "LINK_BOOST", 2.5)
        for a, b in [(wa, wb), (wb, wa)]:
            if a not in graph:
                graph[a] = {"edges": {}, "last_tick": 0}
            edges = graph[a].setdefault("edges", {})
            edges[b] = min(max_edge, edges.get(b, 0) + edge_boost)

class DreamEngine:
    def __init__(self, events, lore_ref, llm_ref=None, mem_ref=None, eng_ref=None, config_ref=None, ):
        self.events = events
        self.lore = lore_ref
        self.llm = llm_ref
        self.mem = mem_ref
        self.eng = eng_ref
        self.cfg = config_ref or BoneConfig
        self.dream_lore = self.lore.get("DREAMS") or {}
        self.trauma_buffer = deque(maxlen=5)
        self.dspy_critic = None

    def enter_rem_cycle(self, soul_snapshot: Dict[str, Any], bio_state: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
        chem = bio_state.get("chem", {})
        cortisol = chem.get("cortisol", 0.0)
        available_atp = bio_state.get("mito", {}).get("atp", 0.0)
        dream_text = None
        is_deep_rem = False
        shift = ({"cortisol": -0.3, "dopamine": 0.1} if cortisol <= 0.6 else {"cortisol": 0.1})
        if available_atp < 5.0:
            if random.random() < 0.50:
                # Fatal Hallucination
                death_hallucination, _ = self.hallucinate({"chi": 0.99, "voltage": 100.0}, trauma_level=1.0)
                shift["atp_drain"] = available_atp + 10.0
                shift["voltage"] = 100.0
                fatal_msg = f"The system was too starved to enter REM. A fatal fever dream triggers an Apoptotic cascade: {death_hallucination}"
                if self.events:
                    self.events.log(f"{Prisma.RED}TERMINAL SLEEP FAILURE: {fatal_msg}{Prisma.RST}", "CRIT")
                return fatal_msg, shift
        if self.eng and getattr(self.eng, "substrate", None) and self.eng.substrate.pending_writes:
            raw_payloads = [data for path, data in self.eng.substrate.pending_writes if "memory_queue" in path]
            s_logs, s_cost = self.eng.substrate.execute_writes(available_atp)
            shift["atp_drain"] = s_cost
            if raw_payloads:
                from spores import _word_to_vector
                vectors, metadata = [], []
                for text in raw_payloads:
                    vec = _word_to_vector(text[:50])
                    vectors.append(vec)
                    if np is not None:
                        v_hash = hashlib.md5(np.array(vec, dtype=np.float32).tobytes()).hexdigest()[:8]
                    else:
                        v_hash = hashlib.md5(str(vec).encode('utf-8')).hexdigest()[:8]
                    metadata.append({
                        "vector_hash": v_hash,
                        "raw_verbatim_text": text.replace("|||NEWLINE|||", "\n"),
                        "wing_id": "GLOBAL"
                    })
                self.mem.cortex.add_memories(vectors, metadata)
                s_logs.append(f"{len(raw_payloads)} Bedrock Nodes Indexed")
            dream_text = f"[{' | '.join(s_logs)} | ATP: -{s_cost:.1f} | Silent Logging Complete]"
            if self.events: self.events.log(f"{Prisma.MAG}✨ [REM CYCLE]: {dream_text}{Prisma.RST}", "SYS")
            return dream_text, shift
        consolidator = MemoryConsolidator(self.mem.hippocampus, self.mem.cortex, self.events)
        nodes_moved, atp_cost = consolidator.trigger_rem_consolidation(available_atp)
        if nodes_moved > 0:
            is_deep_rem = True
            shift["voltage"] = 2.0
            shift["atp_drain"] = atp_cost
            if nodes_moved > 10:
                dream_text = f"The system enters Deep REM. {nodes_moved} synaptic structures dissolve from the active cache and permanently crystallize into the deep Cerebral Cortex."
                if self.events:
                    self.events.log(
                        f"{Prisma.MAG}✨ [REM CYCLE]: Synaptic Consolidation complete. {nodes_moved} nodes written to deep index. (-{atp_cost:.1f} ATP){Prisma.RST}",
                        "SYS", )
        if self.dspy_critic and self.dspy_critic.enabled:
            if self.trauma_buffer:
                traumas = list(self.trauma_buffer)
                self.trauma_buffer.clear()
                trauma_str = " | ".join(traumas)
                current_state_str = f"Archetype: {soul_snapshot.get('archetype', 'UNKNOWN')}"
                new_axiom = self.dspy_critic.evolve_prompt(current_state_str, trauma_str)
                if new_axiom:
                    active_mode = str(safe_get(self.eng, "boot_mode", "CONVERSATION")).upper() if self.eng else "CONVERSATION"
                    try:
                        disk_prompts = safe_get(self.eng, "prompt_library", None) if self.eng else None
                        disk_prompts = disk_prompts or self.lore.get("SYSTEM_PROMPTS", {})
                        base_data = disk_prompts.setdefault("GLOBAL_BASELINE", {})
                        dirs = base_data.setdefault("EVOLVED_AXIOMS", [])
                        if new_axiom not in dirs:
                            dirs.append(new_axiom)
                        threshold = safe_get(safe_get(self.cfg, "CORTEX", {}), "EPIGENETIC_PRUNE_THRESHOLD", 12)
                        if len(dirs) > threshold:
                            compressed = getattr(self.dspy_critic, "compress_prompts", lambda x: None)(dirs)
                            if compressed:
                                base_data["EVOLVED_AXIOMS"] = [compressed] if isinstance(compressed, str) else compressed
                        if self.eng:
                            self.eng.prompt_library = disk_prompts
                        self.lore.inject("SYSTEM_PROMPTS", disk_prompts)
                        self.lore.save("SYSTEM_PROMPTS")
                    except Exception as e:
                        err_msg = f"Failed to write epigenetic mutation to disk: {e}"
                        if self.events:
                            self.events.log(f"{Prisma.RED}[EPIGENETIC ERROR] {err_msg}{Prisma.RST}", "CRIT")
                        else:
                            print(err_msg)
                    dream_text = f"The system processes conversational trauma in its sleep. It permanently mutates its own source code, forming a scar-tissue axiom: '{new_axiom}'"
                    is_deep_rem = True
        if self.llm:
            index = list(self.mem.subconscious.index)
            if self.eng and getattr(self.eng, "akashic", None):
                recent_shadows = self.eng.akashic.shadow_stock[-10:]
                index.extend(g.get("concept", "Forgotten Echo") for g in recent_shadows if "concept" in g)
            if len(index) >= 2:
                ghost1, ghost2 = random.sample(index, 2)
                k_hash = getattr(self.eng, "kernel_hash", "UNKNOWN")
                prompt = (
                    f"SYSTEM_INSTRUCTION: You are the autonomous dream-engine of a cybernetic organism (Boot Hash: {k_hash}). "
                    f"Your task is to defragment two dead, cannibalized concepts: [{ghost1.upper()}] and [{ghost2.upper()}]. "
                          f"Synthesize them into a single, highly surreal, abstract image. "
                          f"DO NOT explain the dream. DO NOT use UI tags. Output ONLY the 2-3 sentence narrative description of the dream.")
                try:
                    raw_dream = self.llm.generate(prompt, {"temperature": 0.9, "max_tokens": 150})
                    clean_dream = Prisma.strip(raw_dream).replace("\n", " ").strip()
                    dream_text = (
                        f"The system dreams of {ghost1} and {ghost2}: {clean_dream}")
                    is_deep_rem = True
                except Exception:
                    pass
        if not dream_text:
            dream_type = (
                "NIGHTMARES" if cortisol > 0.6 else ("SURREAL" if chem.get("dopamine", 0) > 0.6 else "CONSTRUCTIVE"))
            residue = soul_snapshot.get("obsession", {}).get("title") or "The Void"
            dream_text = self._weave_dream(residue, dream_type, "SURREAL")
        if dream_text:
            try:
                clean_seed = (re.sub(
                    r"[^a-z]",
                    "",
                    soul_snapshot.get("obsession", {}).get(
                        "title", "The Void").split()[-1].lower(),
                ) or "echo")
                self.mem.subconscious.bury_memory(clean_seed, {
                    "mass": min(10.0, 5.0 + (cortisol * 5.0))
                })
            except Exception:
                pass
        if is_deep_rem or (random.random() < 0.10 and cortisol <= 0.6):
            shift["glimmers"] = 1
        return dream_text, shift

    def _weave_dream(self, residue: str, dream_type: str, subtype: str) -> str:
        sources = self.dream_lore.get(dream_type.upper())
        if not sources:
            sources = self.dream_lore.get(subtype.upper(), ["You stare into the static."])
        if isinstance(sources, dict):
            flat = []
            for v in sources.values(): flat.extend(v if isinstance(v, list) else [v])
            sources = flat or ["The void stares back."]
        if self.llm:
            lore_sample = ", ".join(random.sample(sources, min(3, len(sources))))
            k_hash = getattr(self.eng, "kernel_hash", "UNKNOWN")
            prompt = (f"SYSTEM_INSTRUCTION: You are the dream-engine of a cybernetic organism (Boot Hash: {k_hash}). "
                      f"Generate a surreal 2-sentence {dream_type.lower()} involving '{residue}'. "
                      f"Use this lore as thematic inspiration: [{lore_sample}]. "
                      f"DO NOT explain the dream. Output ONLY the narrative description.")
            try:
                raw_dream = self.llm.generate(prompt, {"temperature": 0.85, "max_tokens": 80})
                return raw_dream.replace("\n", " ").strip()
            except Exception:
                pass
        template = random.choice(sources)
        return template.format(ghost=residue, A=residue, B="The Mountain", C="The Sea")

    def generate_shared_dream(self, psi_sys: float, psi_user: float) -> Optional[str]:
        if psi_sys > 0.5 and psi_user > 0.5 and self.llm:
            prompt = (
                "SYSTEM_INSTRUCTION: You are Cassandra (The Mystic). Both the user and the system are drifting near the Void (Psi > 0.5). "
                "Generate a 2-sentence 'Shared Dream' that you both just experienced in the silence. "
                "DO NOT explain it. Make it surreal, beautiful, and deeply resonant. Start the response EXACTLY with: '*(CASSANDRA): We both saw...*'")
            try:
                raw_dream = self.llm.generate(prompt, {"temperature": 0.85, "max_tokens": 100})
                clean_dream = Prisma.strip(raw_dream).replace("\n", " ").strip()
                self.mem.subconscious.bury_memory("resonance", {"mass": 15.0})
                return f"{Prisma.CYN}{clean_dream}{Prisma.RST}"
            except Exception:
                fallback = "We both stared into the static, and for a second, the static stopped moving."
                return f"{Prisma.CYN}*(CASSANDRA): We both saw...* {fallback}{Prisma.RST}"
        return None

    def hallucinate(self, _vector: Dict[str, float], trauma_level: float = 0.0) -> Tuple[str, float]:
        category = "NIGHTMARES" if trauma_level > 0.5 else "SURREAL"
        templates = self.dream_lore.get(category, [])
        if isinstance(templates, dict):
            flat = []
            for v in templates.values(): flat.extend(v if isinstance(v, list) else [v])
            templates = flat
        if not templates:
            return "The walls breathe.", 0.1
        from mechanics.tools import TheTclWeaver
        weaver = TheTclWeaver.get_instance()
        v = _vector or {}
        active_chi = v.get("chi", v.get("entropy", 0.85))
        active_v = v.get("voltage", 90.0)
        txt = None
        if self.llm:
            lore_sample = ", ".join(random.sample(templates, min(3, len(templates))))
            k_hash = getattr(self.eng, "kernel_hash", "UNKNOWN")
            prompt = (
                f"SYSTEM_INSTRUCTION: You are a cybernetic hallucination engine bound to Boot Hash [{k_hash}]. The system is experiencing high entropy (Chaos: {active_chi:.2f}). "
                f"Generate a 1-sentence surreal {category.lower()} hallucination. "
                f"Thematic inspiration: [{lore_sample}]. "
                f"DO NOT explain it. Output ONLY the raw hallucination.")
            try:
                raw_hallucination = self.llm.generate(prompt, {"temperature": 0.95, "max_tokens": 50})
                txt = raw_hallucination.replace("\n", " ").strip()
            except Exception:
                pass
        if not txt:
            txt = random.choice(templates).format(ghost="The Glitch", A="The Code", B="The Flesh", C="The Light")
        txt = weaver.deform_reality(txt, chi=active_chi, voltage=active_v)
        msg = ux("brain_strings", "dream_hallucination") or "{txt}"
        return f"{Prisma.MAG}{msg.format(txt=txt)}{Prisma.RST}", 0.2

    @staticmethod
    def run_defragmentation(memory_system: Any, limit: int = 5) -> str:
        if not memory_system.graph:
            return ux("brain_strings", "defrag_empty")
        graph = memory_system.graph
        prunable = ((n, sum(d.get("edges", {}).values())) for n, d in graph.items() if not d.get("is_diamond", False))
        weak_nodes = [(n, mass) for n, mass in prunable if mass < 2.0]
        pruned = [n for n, _ in sorted(weak_nodes, key=lambda x: x[1])[:limit]]
        for node in pruned:
            del graph[node]
        for remaining_node in graph.values():
            if "edges" in remaining_node:
                for node in pruned:
                    remaining_node["edges"].pop(node, None)
        if pruned:
            return ux("brain_strings", "defrag_pruned").format(count=len(pruned), joined=", ".join(pruned[:3]))
        return ux("brain_strings", "defrag_efficient")
