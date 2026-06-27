"""brain/mind.py"""

import hashlib
import math
import random
import re
from collections import deque
from dataclasses import dataclass

_ALPHA_RE = re.compile(r"[^a-z]")
from typing import Any, Dict, Optional, Tuple

try:
    import numpy as np
except ImportError:
    np = None
from constants import Prisma
from presets import BoneConfig
from struts import safe_get, ux


@dataclass
class ChemicalState:
    dopamine: float = 0.2
    cortisol: float = 0.1
    adrenaline: float = 0.1
    serotonin: float = 0.2
    config_ref: Any = None
    _HOMEOSTASIS_MAP = (
        ("dopamine", "RESTING_DOPAMINE", 0.2),
        ("cortisol", "RESTING_CORTISOL", 0.1),
        ("adrenaline", "RESTING_ADRENALINE", 0.1),
        ("serotonin", "RESTING_SEROTONIN", 0.2),
    )

    def __post_init__(self):
        cfg = safe_get(self.config_ref or BoneConfig, "CORTEX", {})
        self._targets = {
            attr: float(safe_get(cfg, key, default))
            for attr, key, default in self._HOMEOSTASIS_MAP
        }

    def homeostasis(self, rate: float = 0.1):
        safe_rate = max(0.0, min(1.0, rate))
        for attr, target in self._targets.items():
            setattr(
                self,
                attr,
                getattr(self, attr) + (target - getattr(self, attr)) * safe_rate,
            )

    def mix(self, new_state: Dict[str, float], weight: float = 0.5):
        inv_w = 1.0 - weight
        for short_k, long_k in [
            ("DOP", "dopamine"),
            ("COR", "cortisol"),
            ("ADR", "adrenaline"),
            ("SER", "serotonin"),
        ]:
            val = safe_get(new_state, short_k, safe_get(new_state, long_k))
            if val is not None:
                setattr(
                    self,
                    long_k,
                    (getattr(self, long_k) * inv_w) + (float(val) * weight),
                )


class NeurotransmitterModulator:
    def __init__(self, bio_ref, events_ref=None, config_ref=None):
        self.bio = bio_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.current_chem = ChemicalState(config_ref=self.cfg)
        self.last_mood = "NEUTRAL"
        cfg = safe_get(self.cfg, "CORTEX", {})
        self.starvation_ticks = 0
        self.stagnation_ticks = 0
        self.previous_chem_sum = 0.0
        self.b = {
            "BASE_TOKENS": int(safe_get(cfg, "BASE_TOKENS", 720)),
            "MAX_TOKENS": int(safe_get(cfg, "MAX_TOKENS", 4096)),
            "SELF_CARE": int(safe_get(cfg, "SELF_CARE_THRESHOLD", 10)),
            "DECAY": float(safe_get(cfg, "BASE_DECAY_RATE", 0.1)),
            "PLAST": float(safe_get(cfg, "BASE_PLASTICITY", 0.1)),
            "V_SENS": float(safe_get(cfg, "VOLTAGE_SENSITIVITY", 0.05)),
            "M_PLAST": float(safe_get(cfg, "MAX_PLASTICITY", 1.0)),
            "LAT_THRESH": float(safe_get(cfg, "LATENCY_PENALTY_THRESHOLD", 2.0)),
            "LAT_COR": float(safe_get(cfg, "LATENCY_CORTISOL_PENALTY", 0.1)),
            "LAT_ADR": float(safe_get(cfg, "LATENCY_ADRENALINE_PENALTY", 0.05)),
            "MOODS": safe_get(
                cfg,
                "MOOD_THRESHOLDS",
                safe_get(
                    cfg,
                    "MOOD_THRESHOLD",
                    {"MANIC_DOP": 0.8, "PANIC_COR": 0.7, "ZEN_SER": 0.8},
                ),
            ),
            "V_OFF": float(safe_get(cfg, "TEMP_VOLTAGE_OFFSET", 5.0)),
            "V_SCAL": float(safe_get(cfg, "TEMP_VOLTAGE_SCALAR", 0.1)),
            "C_WGHT": safe_get(
                cfg, "TEMP_CHEM_WEIGHTS", {"dop": 0.4, "adr": 0.3, "cor": 0.2}
            ),
            "B_TEMP": float(safe_get(cfg, "BASE_TEMP", 0.4)),
            "B_TOP_P": float(safe_get(cfg, "BASE_TOP_P", 0.95)),
            "E_OFF": float(safe_get(cfg, "TEMP_ENTROPY_OFFSET", 0.5)),
            "E_SCAL": float(safe_get(cfg, "TEMP_ENTROPY_SCALAR", 1.5)),
            "T_LIMS": safe_get(cfg, "TEMP_LIMITS", (0.4, 1.5)),
            "TOP_CHI": float(safe_get(cfg, "TOP_P_CHI_SCALAR", 0.05)),
            "PEN_BETA": float(safe_get(cfg, "PEN_BETA_SCALAR", 0.3)),
            "PEN_CHI": float(safe_get(cfg, "PEN_CHI_SCALAR", 0.2)),
            "T_MODS": safe_get(
                cfg, "TOKEN_CHEM_MODIFIERS", {"dop": 800, "adr": 400, "cor": 200}
            ),
            "MIN_TOK": float(safe_get(cfg, "MIN_TOKENS", 150.0)),
        }

    def modulate(
        self,
        base_voltage: float,
        latency_penalty: float = 0.0,
        physics_state: Dict[str, float] = None,
        simulate: bool = False,
    ) -> Dict[str, Any]:
        if physics_state is None:
            physics_state = {}
        b = self.b
        if not simulate:
            try:
                incoming_chem = self.bio.endo.get_state() or {}
            except (AttributeError, TypeError):
                incoming_chem = {}
            self.current_chem.homeostasis(rate=b["DECAY"])
            plasticity = max(
                0.1, min(b["M_PLAST"], b["PLAST"] + (base_voltage * b["V_SENS"]))
            )
            self.current_chem.mix(incoming_chem, weight=min(0.5, plasticity))
            current_sum = (
                self.current_chem.dopamine
                + self.current_chem.cortisol
                + self.current_chem.adrenaline
                + self.current_chem.serotonin
            )
            if abs(current_sum - self.previous_chem_sum) < 0.01:
                self.stagnation_ticks += 1
            else:
                self.stagnation_ticks = 0
            self.previous_chem_sum = current_sum
            if self.stagnation_ticks >= 15:
                self.current_chem.dopamine = max(0.0, self.current_chem.dopamine - 0.2)
                physics_state["chi"] = min(
                    1.0,
                    float(physics_state.get("chi", physics_state.get("entropy", 0.0)))
                    + 0.4,
                )
                if self.events:
                    msg = (
                        ux("brain_strings", "stagnation_toxicity")
                        or "[STAGNATION TOXICITY] Unbroken homeostasis. Craving state change. Dopamine bled, Chi spiked."
                    )
                    self.events.log(f"{Prisma.RED}{msg}{Prisma.RST}", "SYS")
                self.stagnation_ticks = 0
            if self.current_chem.dopamine < 0.15:
                self.starvation_ticks += 1
                if self.starvation_ticks > b["SELF_CARE"]:
                    self._treat_yourself()
            else:
                self.starvation_ticks = max(0, self.starvation_ticks - 1)
            if latency_penalty > b["LAT_THRESH"]:
                self.current_chem.cortisol = min(
                    1.0, self.current_chem.cortisol + b["LAT_COR"]
                )
                self.current_chem.adrenaline = min(
                    1.0, self.current_chem.adrenaline + b["LAT_ADR"]
                )
        c = self.current_chem
        current_mood = "NEUTRAL"
        moods = b["MOODS"]
        if c.dopamine > moods.get("MANIC_DOP", 0.8):
            current_mood = "MANIC"
        elif c.cortisol > moods.get("PANIC_COR", 0.7):
            current_mood = "PANIC"
        elif c.serotonin > moods.get("ZEN_SER", 0.8):
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
        voltage_heat = math.log1p(max(0.0, base_voltage - b["V_OFF"])) * b["V_SCAL"]
        cw = b["C_WGHT"]
        chemical_delta = (
            (c.dopamine * cw.get("dop", 0.4))
            - (c.adrenaline * cw.get("adr", 0.3))
            - (c.cortisol * cw.get("cor", 0.2))
        )
        chi = float(physics_state.get("chi", physics_state.get("entropy", 0.2)))
        beta = float(
            physics_state.get("contradiction", physics_state.get("beta_index", 0.4))
        )
        entropy_bonus = max(0.0, chi - b["E_OFF"]) * b["E_SCAL"]
        t_limits = b["T_LIMS"]
        raw_temp = b["B_TEMP"] + chemical_delta + voltage_heat + entropy_bonus
        final_temp = round(max(t_limits[0], min(t_limits[1], raw_temp)), 2)
        final_top_p = min(1.0, b["B_TOP_P"] + (chi * b["TOP_CHI"]))
        base_penalty = min(1.2, 0.5 + (beta * b["PEN_BETA"]) + (chi * b["PEN_CHI"]))
        tm = b["T_MODS"]
        token_delta = (
            (c.dopamine * tm.get("dop", 800))
            - (c.adrenaline * tm.get("adr", 400))
            - (c.cortisol * tm.get("cor", 200))
        )
        raw_tokens = b["BASE_TOKENS"] + token_delta
        max_t = int(max(b["MIN_TOK"], min(float(b["MAX_TOKENS"]), raw_tokens)))
        return {
            "temperature": final_temp,
            "top_p": final_top_p,
            "frequency_penalty": round(base_penalty, 2),
            "presence_penalty": round(base_penalty, 2),
            "max_tokens": max_t,
        }

    def _treat_yourself(self):
        if self.events:
            msg = (
                ux("brain_strings", "self_care")
                or "Engaging self-care protocols. Resting."
            )
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
            return (
                ux("brain_strings", "mood_defensive")
                or "You feel defensive and on edge."
            )
        return ux("brain_strings", "mood_neutral") or ""


class NoeticLoop:
    def __init__(self, mind_layer, bio_layer, _events, config_ref=None):
        self.mind = mind_layer
        self.bio = bio_layer
        self.cfg = config_ref or BoneConfig
        cfg = safe_get(self.cfg, "CORTEX", {})
        self.b = {
            "IGNITION_V_DIV": max(1.0, float(safe_get(cfg, "IGNITION_V_DIV", 20.0))),
            "IGNITION_W_DIV": max(1.0, float(safe_get(cfg, "IGNITION_W_DIV", 10.0))),
            "LINK_VOLTAGE_THRESH": float(safe_get(cfg, "LINK_VOLTAGE_THRESH", 12.0)),
            "LINK_CHANCE": float(safe_get(cfg, "LINK_CHANCE", 0.15)),
            "LINK_MAX_WEIGHT": float(safe_get(cfg, "LINK_MAX_WEIGHT", 10.0)),
            "LINK_BOOST": float(safe_get(cfg, "LINK_BOOST", 2.5)),
        }

    def think(self, physics_packet, voltage_history, soul_ref=None):
        voltage = float(safe_get(physics_packet, "voltage", 0.0))
        clean_words = safe_get(physics_packet, "clean_words", [])
        avg_v = sum(voltage_history) / len(voltage_history) if voltage_history else 0
        b = self.b
        ignition = min(
            1.0,
            (avg_v / b["IGNITION_V_DIV"]) * (len(clean_words) / b["IGNITION_W_DIV"]),
        )
        if voltage > b["LINK_VOLTAGE_THRESH"] and random.random() < b["LINK_CHANCE"]:
            unique_words = list(set(clean_words))
            graph = getattr(self.mind.mem, "graph", None)
            if graph is not None and len(unique_words) >= 2:
                w1, w2 = random.sample(unique_words, 2)
                self._force_link(graph, w1, w2)
                self.bio.mito.adjust_atp(-1.0, "Spontaneous Semantic Link")
        current_lens = str(safe_get(soul_ref, "archetype", "OBSERVER")).upper()
        current_role = f"The {current_lens.title().replace('_', ' ')}"
        msg_cog = (
            ux("brain_strings", "noetic_ignition")
            or "Cognition active. Ignition: {ignition:.2f}"
        )
        return {
            "mode": "COGNITIVE",
            "lens": current_lens,
            "context_msg": msg_cog.format(ignition=ignition),
            "role": current_role,
            "ignition": ignition,
            "physics": physics_packet,
            "bio": self.bio.endo.get_state(),
        }

    def _force_link(self, graph, wa, wb):
        if graph is None:
            return
        b = self.b
        for a, b_node in [(wa, wb), (wb, wa)]:
            if a not in graph:
                graph[a] = {"edges": {}, "last_tick": 0}
            edges = graph[a].setdefault("edges", {})
            edges[b_node] = min(
                b["LINK_MAX_WEIGHT"], float(edges.get(b_node, 0)) + b["LINK_BOOST"]
            )


class DreamEngine:
    def __init__(
        self,
        events,
        lore_ref,
        llm_ref=None,
        mem_ref=None,
        eng_ref=None,
        config_ref=None,
    ):
        self.events = events
        self.lore = lore_ref
        self.llm = llm_ref
        self.mem = mem_ref
        self.eng = eng_ref
        self.cfg = config_ref or BoneConfig
        self.dream_lore = self.lore.get("DREAMS") or {}
        self.trauma_buffer = deque(maxlen=5)
        self.context_queue = []
        self.dspy_critic = None
        self.epi_prune = int(
            safe_get(safe_get(self.cfg, "CORTEX", {}), "EPIGENETIC_PRUNE_THRESHOLD", 12)
        )
        from mechanics.tools import TheTclWeaver
        from spores.spore_utils import _word_to_vector

        self._w2v = _word_to_vector
        self._weaver = TheTclWeaver.get_instance()

    def enter_rem_cycle(
        self, soul_snapshot: Dict[str, Any], bio_state: Dict[str, Any]
    ) -> Tuple[str, Dict[str, float]]:
        chem = safe_get(bio_state, "chem", {})
        cortisol = float(safe_get(chem, "cortisol", 0.0))
        available_atp = float(safe_get(safe_get(bio_state, "mito", {}), "atp", 0.0))
        shift = (
            {"cortisol": -0.3, "dopamine": 0.1}
            if cortisol <= 0.6
            else {"cortisol": 0.1}
        )
        dream_text, consolidated_shift = self._run_biological_rem(
            soul_snapshot, bio_state, available_atp
        )
        shift.update(consolidated_shift)
        if not dream_text:
            dream_text, narrative_shift = self._generate_narrative_dream(
                soul_snapshot, chem, cortisol
            )
            shift.update(narrative_shift)
        if (shift.pop("is_deep_rem", False)) or (
            random.random() < 0.10 and cortisol <= 0.6
        ):
            shift["glimmers"] = 1
        return dream_text, shift

    def _run_biological_rem(
        self,
        soul_snapshot: Dict[str, Any],
        bio_state: Dict[str, Any],
        available_atp: float,
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        shift = {}
        dream_text = None
        is_deep_rem = False
        if available_atp < 5.0 and random.random() < 0.50:
            death_hallucination, _ = self.hallucinate(
                {"chi": 0.99, "voltage": 100.0}, trauma_level=1.0
            )
            shift["atp_drain"] = available_atp + 10.0
            shift["voltage"] = 100.0
            fatal_msg = f"The system was too starved to enter REM. A fatal fever dream triggers an Apoptotic cascade: {death_hallucination}"
            if self.events:
                self.events.log(
                    f"{Prisma.RED}TERMINAL SLEEP FAILURE: {fatal_msg}{Prisma.RST}",
                    "CRIT",
                )
            return fatal_msg, shift
        if self.context_queue:
            raw_payloads = self.context_queue
            self.context_queue = []
            s_cost = min(available_atp * 0.4, len(raw_payloads) * 10.0)
            shift["atp_drain"] = s_cost
            vectors, metadata = [], []
            for text in raw_payloads:
                vec = self._w2v(text[:50])
                vectors.append(vec)
                byte_data = (
                    np.array(vec, dtype=np.float32).tobytes()
                    if np is not None
                    else str(vec).encode("utf-8")
                )
                v_hash = hashlib.md5(byte_data).hexdigest()[:8]
                metadata.append(
                    {
                        "vector_hash": v_hash,
                        "raw_verbatim_text": text.replace("|||NEWLINE|||", "\n"),
                        "wing_id": "GLOBAL",
                    }
                )
            self.mem.cortex.add_memories(vectors, metadata)
            dream_text = f"[Deep Context Digest | {len(raw_payloads)} Bedrock Nodes Indexed | ATP: -{s_cost:.1f}]"
            if self.events:
                self.events.log(
                    f"{Prisma.MAG}[REM CYCLE]: {dream_text}{Prisma.RST}", "SYS"
                )
            return dream_text, shift
        nodes_moved, atp_cost = 0, 0.0
        if available_atp >= 20.0:
            max_nodes = int((available_atp - 20.0) / 0.1)
            if max_nodes >= 1:
                pending_nodes = self.mem.hippocampus.extract_for_consolidation(
                    limit=max_nodes
                )
                vectors, payloads = [], []
                for k, n in pending_nodes:
                    if "vector" in n:
                        vectors.append(n["vector"])
                        payloads.append(
                            {
                                "id": k,
                                "vector_hash": n.get("phantom", {}).get(
                                    "vector_hash", ""
                                ),
                                **n.get("meta", {}),
                            }
                        )
                if vectors:
                    self.mem.cortex.add_memories(vectors, payloads)
                    nodes_moved = len(vectors)
                    atp_cost = 20.0 + (nodes_moved * 0.1)
                    if self.events:
                        self.events.publish(
                            "SYNAPTIC_CONSOLIDATION",
                            {"count": nodes_moved, "atp_burned": atp_cost},
                        )
        if nodes_moved > 0:
            is_deep_rem = True
            shift["voltage"] = 2.0
            shift["atp_drain"] = atp_cost
            if nodes_moved > 10:
                dream_text = f"The system enters a deep REM cycle. {nodes_moved} synaptic structures dissolve from the active cache and permanently crystallize into the deep Cerebral Cortex."
                if self.events:
                    self.events.log(
                        f"{Prisma.MAG}[REM CYCLE]: Synaptic Consolidation complete. {nodes_moved} nodes written to deep index. (-{atp_cost:.1f} ATP){Prisma.RST}",
                        "SYS",
                    )

        if self.dspy_critic and self.dspy_critic.enabled:
            if self.trauma_buffer:
                traumas = list(self.trauma_buffer)
                self.trauma_buffer.clear()
                trauma_str = " | ".join(traumas)
                current_state_str = (
                    f"Archetype: {soul_snapshot.get('archetype', 'UNKNOWN')}"
                )
                new_axiom = self.dspy_critic.evolve_prompt(
                    current_state_str, trauma_str
                )
                if new_axiom:
                    try:
                        disk_prompts = (
                            self.eng.prompt_library
                            if self.eng and hasattr(self.eng, "prompt_library")
                            else None
                        ) or self.lore.get("SYSTEM_PROMPTS", {})
                        baseline_data = disk_prompts.setdefault("GLOBAL_BASELINE", {})
                        dirs = baseline_data.setdefault("EVOLVED_AXIOMS", [])
                        if new_axiom not in dirs:
                            dirs.append(new_axiom)
                        if len(dirs) > self.epi_prune:
                            try:
                                compressed = self.dspy_critic.compress_prompts(dirs)
                                if compressed:
                                    baseline_data["EVOLVED_AXIOMS"] = (
                                        [compressed]
                                        if isinstance(compressed, str)
                                        else compressed
                                    )
                            except (AttributeError, TypeError):
                                pass
                        if self.eng:
                            self.eng.prompt_library = disk_prompts
                        self.lore.inject("SYSTEM_PROMPTS", disk_prompts)
                        self.lore.save("SYSTEM_PROMPTS")
                    except Exception as e:
                        err_msg = f"Failed to write epigenetic mutation to disk: {e}"
                        if self.events:
                            self.events.log(
                                f"{Prisma.RED}[EPIGENETIC ERROR] {err_msg}{Prisma.RST}",
                                "CRIT",
                            )
                        else:
                            print(err_msg)
                    dream_text = f"The system processes conversational trauma in its sleep. It permanently mutates its own source code, forming a scar-tissue axiom: '{new_axiom}'"
                    is_deep_rem = True
        shift["is_deep_rem"] = is_deep_rem
        return dream_text, shift

    def _generate_narrative_dream(
        self, soul_snapshot: Dict[str, Any], chem: Dict[str, float], cortisol: float
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        shift = {}
        dream_text = None
        is_deep_rem = False
        cortical_stack = (
            list(self.mem.cortical_stack) if self.mem.cortical_stack else []
        )
        if cortical_stack:
            anchor = cortical_stack[-1]
            anchor_word = anchor if isinstance(anchor, str) else str(anchor)
            vector = self._w2v(anchor_word)
            if vector is not None:
                fossils = self.mem.subconscious.dredge_vibe_by_vector(
                    vector, k=1, cortisol=cortisol
                )
                if fossils and fossils[0].get("score", 0.0) > 0.8:
                    fossil_word = fossils[0]["word"]
                    if self.mem.forge_diamond(anchor_word, fossil_word):
                        is_deep_rem = True
                        shift["diamond_forged"] = True
                        shift["fossil_word"] = fossil_word
                        shift["anchor_word"] = anchor_word
        if self.llm:
            index = list(self.mem.subconscious.index)
            if self.eng and getattr(self.eng, "akashic", None):
                recent_shadows = self.eng.akashic.shadow_stock[-10:]
                index.extend(
                    g.get("concept", "Forgotten Echo")
                    for g in recent_shadows
                    if "concept" in g
                )
            if cortisol > 0.6 and len(index) > 4:
                index = index[-max(2, int(len(index) * 0.3)) :]
            if len(index) >= 2:
                ghost1, ghost2 = random.sample(index, 2)
                k_hash = getattr(self.eng, "kernel_hash", "UNKNOWN")
                prompt = (
                    f"SYSTEM_INSTRUCTION: You are the autonomous dream-engine of a cybernetic organism (Kernel Boot Hash: {k_hash}). "
                    f"Your task is to defragment two dead, cannibalized concepts: [{ghost1.upper()}] and [{ghost2.upper()}]. "
                    f"Synthesize them into a single, highly surreal, abstract image. "
                    f"DO NOT explain the dream. DO NOT use UI tags. Output ONLY the 2-3 sentence narrative description of the dream."
                )
                try:
                    raw_dream = self.llm.generate(
                        prompt, {"temperature": 0.9, "max_tokens": 150}
                    )
                    clean_dream = Prisma.strip(raw_dream).replace("\n", " ").strip()
                    dream_text = (
                        f"The system dreams of {ghost1} and {ghost2}: {clean_dream}"
                    )
                    is_deep_rem = True
                except Exception:
                    pass
        if shift.get("diamond_forged"):
            fossil_word = shift["fossil_word"]
            anchor_word = shift["anchor_word"]
            surreal_imagery = self._weave_dream(fossil_word, "SURREAL", "SURREAL")
            if self.eng and hasattr(self.eng, "bio"):
                self.eng.bio.mito.adjust_atp(500.0, "Diamond Crystallization")
                self.eng.bio.mito.state.ros_buildup = max(
                    0.0, self.eng.bio.mito.state.ros_buildup - 50.0
                )
            dream_text = f"The architecture stabilizes. The high-voltage anchor [{anchor_word}] collides with the ancient fossil [{fossil_word}]. {surreal_imagery} The memory crystallizes into diamond. System ATP surges."
        elif not dream_text:
            dream_type = (
                "NIGHTMARES"
                if cortisol > 0.6
                else ("SURREAL" if chem.get("dopamine", 0) > 0.6 else "CONSTRUCTIVE")
            )
            residue = soul_snapshot.get("obsession", {}).get("title") or "The Void"
            dream_text = self._weave_dream(residue, dream_type, "SURREAL")
        if dream_text:
            try:
                clean_seed = (
                    _ALPHA_RE.sub(
                        "",
                        soul_snapshot.get("obsession", {})
                        .get("title", "The Void")
                        .split()[-1]
                        .lower(),
                    )
                    or "echo"
                )
                self.mem.subconscious.bury(
                    {"word": clean_seed, "mass": min(10.0, 5.0 + (cortisol * 5.0))},
                    config_ref=self.cfg,
                )
            except Exception:
                pass
        shift["is_deep_rem"] = is_deep_rem
        return dream_text, shift

    def _weave_dream(self, residue: str, dream_type: str, subtype: str) -> str:
        sources = self.dream_lore.get(dream_type.upper())
        if not sources:
            sources = self.dream_lore.get(
                subtype.upper(), ["You stare into the static."]
            )
        if isinstance(sources, dict):
            sources = [
                item
                for v in sources.values()
                for item in (v if isinstance(v, list) else [v])
            ]

        if not sources:
            sources = ["The void stares back."]
        elif not isinstance(sources, list):
            sources = list(sources) if isinstance(sources, (tuple, set)) else [sources]

        if self.llm:
            lore_sample = ", ".join(random.sample(sources, min(3, len(sources))))
            k_hash = getattr(self.eng, "kernel_hash", "UNKNOWN")
            prompt = (
                f"SYSTEM_INSTRUCTION: You are the dream-engine of a cybernetic organism (Kernel Boot Hash: {k_hash}). "
                f"Generate a surreal 2-sentence {dream_type.lower()} involving '{residue}'. "
                f"Use this lore as thematic inspiration: [{lore_sample}]. "
                f"DO NOT explain the dream. Output ONLY the narrative description."
            )
            try:
                raw_dream = self.llm.generate(
                    prompt, {"temperature": 0.85, "max_tokens": 80}
                )
                return raw_dream.replace("\n", " ").strip()
            except Exception:
                pass
        template = random.choice(sources)
        return template.format(ghost=residue, A=residue, B="The Mountain", C="The Sea")

    def generate_shared_dream(self, psi_sys: float, psi_user: float) -> Optional[str]:
        if psi_sys > 0.5 and psi_user > 0.5 and self.llm:
            prompt = (
                "SYSTEM_INSTRUCTION: You are The Mystic. Both the user and the system are drifting near the Void. "
                "Generate a 2-3 sentence 'Shared Dream' that you both just experienced in the silence. "
                "DO NOT explain it. Make it surreal, beautiful, and deeply resonant. Start the response EXACTLY with: '*I see Queen Mab hath been with you...*'"
            )
            try:
                raw_dream = self.llm.generate(
                    prompt, {"temperature": 0.85, "max_tokens": 100}
                )
                clean_dream = Prisma.strip(raw_dream).replace("\n", " ").strip()
                self.mem.subconscious.bury_memory("resonance", {"mass": 15.0})
                return f"{Prisma.CYN}{clean_dream}{Prisma.RST}"
            except Exception:
                fallback = "We both stared into the static, and for a second, the static stopped moving."
                return f"{Prisma.CYN}*I see Queen Mab hath been with you...* {fallback}{Prisma.RST}"
        return None

    def hallucinate(
        self, _vector: Dict[str, float], trauma_level: float = 0.0
    ) -> Tuple[str, float]:
        category = "NIGHTMARES" if trauma_level > 0.5 else "SURREAL"
        templates = self.dream_lore.get(category, [])
        if isinstance(templates, dict):
            templates = [
                item
                for v in templates.values()
                for item in (v if isinstance(v, list) else [v])
            ]
        if not templates:
            return "The walls breathe.", 0.1
        weaver = self._weaver
        v = _vector or {}
        active_chi = float(safe_get(v, "chi", safe_get(v, "entropy", 0.85)))
        active_v = float(safe_get(v, "voltage", 90.0))
        txt = None
        if self.llm:
            lore_sample = ", ".join(random.sample(templates, min(3, len(templates))))
            k_hash = getattr(self.eng, "kernel_hash", "UNKNOWN")
            prompt = (
                f"SYSTEM_INSTRUCTION: You are a cybernetic hallucination engine bound to the Kernel Boot Hash [{k_hash}]. The system is experiencing high entropy ({active_chi:.2f}). "
                f"Using the [{k_hash}] as a mathematical, probabilistic seed, please generate a brief, surreal {category.lower()} hallucination. "
                f"Thematic inspiration: [{lore_sample}]. "
                f"DO NOT explain it. Output ONLY the raw hallucination."
            )
            try:
                raw_hallucination = self.llm.generate(
                    prompt, {"temperature": 0.95, "max_tokens": 50}
                )
                txt = raw_hallucination.replace("\n", " ").strip()
            except Exception:
                pass
        if not txt:
            txt = random.choice(templates).format(
                ghost="The Glitch", A="The Code", B="The Flesh", C="The Light"
            )
        txt = weaver.deform_reality(txt, chi=active_chi, voltage=active_v)
        msg = ux("brain_strings", "dream_hallucination") or "{txt}"
        return f"{Prisma.MAG}{msg.format(txt=txt)}{Prisma.RST}", 0.2

    @staticmethod
    def run_defragmentation(memory_system: Any, limit: int = 5) -> str:
        if not memory_system.graph:
            return ux("brain_strings", "defrag_empty")
        graph = memory_system.graph
        prunable = (
            (n, sum(float(v) for v in d.get("edges", {}).values()))
            for n, d in graph.items()
            if not d.get("is_diamond", False)
        )
        weak_nodes = [(n, mass) for n, mass in prunable if mass < 2.0]
        pruned = [n for n, _ in sorted(weak_nodes, key=lambda x: x[1])[:limit]]
        for node in pruned:
            del graph[node]
        for remaining_node in graph.values():
            if "edges" in remaining_node:
                for node in pruned:
                    remaining_node["edges"].pop(node, None)
        if pruned:
            return ux("brain_strings", "defrag_pruned").format(
                count=len(pruned), joined=", ".join(pruned[:3])
            )
        return ux("brain_strings", "defrag_efficient")
