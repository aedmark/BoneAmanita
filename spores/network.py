"""spores/network.py"""

import random
import time
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

from archetypes.village import ParadoxSeed
from brain.ann import CerebralIndex, HippocampalCache
from constants import Prisma
from core import EventBus, LoreManifest
from presets import BoneConfig
from spores.genetics import LiteraryReproduction
from spores.io import LocalFileSporeLoader
from spores.memory import MemoryCore, SubconsciousStrata
from struts import safe_get, safe_set, ux, ux_format


class MycelialNetwork:
    def __init__(
        self,
        events: EventBus,
        loader: Optional["LocalFileSporeLoader"] = None,
        seed_file=None,
        config_ref=None,
        lexicon_ref=None,
    ):
        self.events = events
        self.cfg = config_ref or BoneConfig
        self.lex = lexicon_ref
        self.loader = loader if loader else LocalFileSporeLoader()
        self.session_id = f"session_{int(time.time())}"
        self.filename = f"{self.session_id}.json"
        self.hippocampus = HippocampalCache(max_capacity=500)
        self.cortex = CerebralIndex(dimension=8)
        self.subconscious = SubconsciousStrata(
            filename=f"memories/subconscious_{self.session_id}.jsonl"
        )
        self.memory_core = MemoryCore(
            events, self.subconscious, config_ref=self.cfg, lexicon_ref=self.lex
        )
        self.repro = LiteraryReproduction(config_ref=self.cfg)
        self.fossils = deque(maxlen=200)
        self.lineage_log = deque(maxlen=50)
        self.seeds = self._load_seeds()
        self.session_health = getattr(self.cfg, "MAX_HEALTH", 100.0)
        self.session_stamina = getattr(self.cfg, "MAX_STAMINA", 100.0)
        self.session_trauma_vector = {}
        self.village_legacy = {}
        self.last_governor_action = None
        if seed_file:
            self.ingest(seed_file)
        self._sync_q_matrix()
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("SCAR_RECORDED", self._on_scar_recorded)

    def _sync_q_matrix(self):
        pass

    def _mutate_config(self, path: str, value: Any) -> bool:
        parts = path.split('.')
        target = self.cfg
        for part in parts[:-1]:
            target = safe_get(target, part)
            if target is None:
                return False
        leaf = parts[-1]
        try:
            safe_set(target, leaf, value)
            return True
        except Exception:
            return False

    def evaluate_system_state(self, stamina: float, trauma_vector: dict):
        """The State Sensor & Policy Engine"""
        try:
            max_cap = int(safe_get(self.cfg, "MAX_MEMORY_CAPACITY", 100))
            saturation = min(1.0, len(self.graph) / max(1, max_cap))
            exhaustion = max(0.0, (100.0 - stamina) / 100.0)
            toxicity = (
                max(trauma_vector.values())
                if isinstance(trauma_vector, dict) and trauma_vector
                else 0.0
            )
            if toxicity > 0.6:
                action = "DEFENSIVE"
                self._mutate_config("BIO.ROS_CRITICAL", 150.0)
                self._mutate_config("STAMINA_REGEN", 15.0)
            elif exhaustion > 0.6 or saturation > 0.8:
                action = "THROTTLE_DOWN"
                self._mutate_config("PHYSICS.VOLTAGE_MAX", 50.0)
                self._mutate_config("PHYSICS.DRAG_HALT", 20.0)
            else:
                action = "OPEN_FLOODGATES"
                self._mutate_config("SHAPLEY_MASS_THRESHOLD", 2.0)
                self._mutate_config("AKASHIC.AUTOPHAGY_YIELD", 30.0)

            if hasattr(self.events, "log") and action != getattr(
                self, "last_governor_action", None
            ):
                self.events.log(
                    f"{Prisma.MAG}[AUTONOMIC GOVERNOR]: {action} policy engaged. Physics constraints mutated.{Prisma.RST}",
                    "PHYSICS",
                )
                self.last_governor_action = action

            return action
        except Exception as e:
            if hasattr(self.events, "log"):
                self.events.log(f"[AUTONOMIC GOVERNOR ERROR]: {e}", "WARN")
            return "ERROR"

    def _on_scar_recorded(self, payload):
        if payload.get("concept"):
            self._sync_q_matrix()

    @property
    def graph(self):
        return self.memory_core.graph

    @property
    def cortical_stack(self):
        return self.memory_core.cortical_stack

    def calculate_mass(self, node):
        return self.memory_core.calculate_mass(node)

    def run_ecosystem(self, physics: Any, stamina: float, tick: int) -> List[str]:
        clean_words = safe_get(physics, "clean_words", [])
        logs = []
        self.evaluate_system_state(stamina, self.session_trauma_vector)
        cfg_spores = safe_get(self.cfg, "SPORES", {})
        if random.random() < float(safe_get(cfg_spores, "CHORUS_CHANCE", 0.10)):
            chorus_log = self._poll_chorus(clean_words, physics)
            if chorus_log:
                logs.append(chorus_log)
        ghost_log = self._poll_ghosts(clean_words, physics)
        if ghost_log:
            logs.append(ghost_log)
        return logs

    def _poll_chorus(self, clean_words: list, physics: Any) -> Optional[str]:
        total_voltage_boost = 0.0
        total_drag_penalty = 0.0
        echo_count = 0
        for w in clean_words:
            v_boost, d_pen = self._check_echo_well(w)
            if v_boost > 0:
                total_voltage_boost += v_boost
                total_drag_penalty += d_pen
                echo_count += 1
        if echo_count > 0:
            phys_cfg = safe_get(self.cfg, "PHYSICS", {})
            max_v = float(safe_get(phys_cfg, "VOLTAGE_MAX", 150.0))
            max_d = float(safe_get(phys_cfg, "DRAG_HALT", 10.0))
            safe_set(
                physics,
                "voltage",
                min(
                    max_v,
                    float(safe_get(physics, "voltage", 0.0)) + total_voltage_boost,
                ),
            )
            safe_set(
                physics,
                "narrative_drag",
                min(
                    max_d,
                    float(safe_get(physics, "narrative_drag", 0.0))
                    + total_drag_penalty,
                ),
            )
            cfg = safe_get(self.cfg, "SPORES", {})
            heavy_v = float(safe_get(cfg, "ECHO_VOLTAGE_HEAVY", 4.0))
            if total_voltage_boost > heavy_v:
                if msg_h := ux_format(
                    "spore_strings", "net_echo_heavy", drag=total_drag_penalty
                ):
                    return f"{Prisma.VIOLET}{msg_h}{Prisma.RST}"
            elif total_voltage_boost > 0:
                if msg_l := ux("spore_strings", "net_echo_light"):
                    return f"{Prisma.GRY}{msg_l}{Prisma.RST}"
        return None

    def trigger_autophagy(self) -> Tuple[float, str]:
        victim, msg = self.memory_core.cannibalize(current_tick=int(time.time()))
        if victim:
            cfg = safe_get(self.cfg, "AKASHIC", {})
            atp_gain = float(safe_get(cfg, "AUTOPHAGY_YIELD", 15.0))
            if self.events:
                self.events.publish(
                    "AUTOPHAGY_EVENT", {"node": victim, "atp_gained": atp_gain}
                )
            return atp_gain, msg
        return 0.0, msg

    def _poll_ghosts(self, clean_words: list, physics: Any) -> Optional[str]:
        total_v_shift = 0.0
        total_d_shift = 0.0
        haunted_words = []
        for w in clean_words:
            if w in self.subconscious.index:
                vibe_results = self.subconscious.dredge_vibe(w)
                if vibe_results:
                    top_score = vibe_results[0].get("score", 0.0)
                    v_shift = top_score * 2.0
                    d_shift = top_score * 0.5
                else:
                    v_shift = 0.0
                    d_shift = 0.0
                total_v_shift += v_shift
                total_d_shift += d_shift
                if v_shift > 0.1:
                    haunted_words.append(w)
        total_v_shift = max(-15.0, min(15.0, total_v_shift))
        total_d_shift = max(-5.0, min(5.0, total_d_shift))
        if haunted_words:
            safe_set(
                physics,
                "voltage",
                max(0.0, float(safe_get(physics, "voltage", 0.0)) + total_v_shift),
            )
            safe_set(
                physics,
                "narrative_drag",
                max(
                    0.0, float(safe_get(physics, "narrative_drag", 0.0)) + total_d_shift
                ),
            )
            msg = ux_format(
                "spore_strings",
                "net_ghost_haunt",
                "The ghosts of [{words}] alter the atmosphere (V:{v:+.2f}, D:{d:+.2f}).",
                words=", ".join(haunted_words).upper(),
                v=total_v_shift,
                d=total_d_shift,
            )
            return f"{Prisma.VIOLET}{msg}{Prisma.RST}"
        return None

    def prune_synapses(self, scaling_factor=0.85, prune_threshold=0.5):
        return self.memory_core.prune_synapses(scaling_factor, prune_threshold)

    def encode(self, clean_words, physics, governor_mode):
        significance = float(safe_get(physics, "voltage", 0.0))
        if governor_mode == "FORGE":
            significance *= 2.0
        elif governor_mode == "LABORATORY":
            significance *= 1.2
        engram = {
            "trigger": clean_words[:3] if clean_words else ["void"],
            "context": governor_mode,
            "significance": significance,
            "wing_id": safe_get(physics, "scope_boundary", "GLOBAL"),
            "room_id": "_".join(clean_words[:2]) if clean_words else "GENERAL",
            "raw_verbatim_text": safe_get(physics, "raw_text", ""),
            "timestamp": time.time(),
        }
        cfg = safe_get(self.cfg, "SPORES", {})
        consolidation = float(safe_get(cfg, "CONSOLIDATION_THRESHOLD", 5.0))
        if significance > consolidation:
            self.memory_core.short_term_buffer.append(engram)
            return True
        return False

    def bury(
        self,
        clean_words: List[str],
        tick: int,
        resonance=5.0,
        learning_mod=1.0,
        desperation_level=0.0,
    ) -> Tuple[Optional[str], List[str]]:
        if not clean_words:
            return None, []
        valuable = self._filter_valuable_matter(clean_words)
        max_cap = int(safe_get(self.cfg, "MAX_MEMORY_CAPACITY", 100))
        victims = []
        log_msg = None
        new_nodes_count = sum(1 for w in valuable if w not in self.graph)
        excess_mass = (len(self.graph) + new_nodes_count) - max_cap
        if excess_mass > 0:
            cfg = safe_get(self.cfg, "SPORES", {})
            desp_thresh = float(safe_get(cfg, "DESPERATION_SATURATION_THRESH", 0.6))
            if desperation_level < desp_thresh:
                return ux("spore_strings", "net_sat_high") or "", []
            for _ in range(excess_mass):
                v, l_msg = self.memory_core.cannibalize(tick, preserve_current=valuable)
                if not v:
                    break
                victims.append(v)
                log_msg = l_msg
            if not victims:
                return ux("spore_strings", "net_sat_lock") or "", []
            self._sync_q_matrix()
        self.cortical_stack.extend(valuable)
        base_rate = 0.5 * (resonance / 5.0)
        learning_rate = max(0.1, min(1.0, base_rate * learning_mod))
        decay_rate = 0.1
        for i, current in enumerate(valuable):
            self.graph.setdefault(current, {"edges": {}})["last_tick"] = tick
            for prev in set(valuable[max(0, i - 2) : i]) - {current}:
                self.graph.setdefault(prev, {"edges": {}})["last_tick"] = tick
                self.memory_core.strengthen_link(
                    current, prev, learning_rate, decay_rate
                )
                self.memory_core.strengthen_link(
                    prev, current, learning_rate, decay_rate
                )
        new_wells = self._detect_new_wells(valuable, tick)
        return log_msg, victims + new_wells

    def _filter_valuable_matter(self, words: List[str]) -> List[str]:
        solvents = (
            self.lex.SOLVENTS if self.lex and hasattr(self.lex, "SOLVENTS") else set()
        )

        valuable = []
        for w in words:
            if len(w) <= 4 and w in solvents:
                continue
            cat = self.lex.get_current_category(w) if self.lex and hasattr(self.lex, "get_current_category") else None
            if cat == "void":
                continue
            if cat or len(w) > 4:
                valuable.append(w)
        return valuable

    def _detect_new_wells(self, words, tick):
        new_wells = []
        thresh = float(safe_get(self.cfg, "SHAPLEY_MASS_THRESHOLD", 5.0))
        for w in words:
            if w in self.graph:
                mass = self.memory_core.calculate_mass(w)
                if mass > thresh:
                    node_data = self.graph[w]
                    if "strata" not in node_data:
                        node_data["strata"] = {
                            "birth_tick": tick,
                            "birth_mass": mass,
                            "stability_index": 0.0,
                        }
                        new_wells.append(w)
                    else:
                        age = max(1, tick - node_data["strata"]["birth_tick"])
                        growth = (mass - node_data["strata"]["birth_mass"]) / age
                        node_data["strata"]["growth_rate"] = round(growth, 3)
        return new_wells

    def _check_echo_well(self, node):
        mass = self.calculate_mass(node)
        if mass > 8.0:
            return 2.0, 1.5
        if mass > 4.0:
            return 0.5, 0.5
        return 0.0, 0.0

    @staticmethod
    def _load_seeds():
        from archetypes.village import ParadoxSeed

        loaded_seeds = []
        try:
            scenarios = LoreManifest.get_instance().get("SCENARIOS") or {}
            raw_seeds = scenarios.get("SEEDS", [])
            for item in raw_seeds:
                q = item.get("question", "Undefined Paradox")
                t = set(item.get("triggers", []))
                seed = ParadoxSeed(q, t)
                loaded_seeds.append(seed)
        except Exception:
            loaded_seeds = [
                ParadoxSeed("Does the mask eat the face?", {"mask", "face", "hide"})
            ]
        return loaded_seeds

    def tend_garden(self, current_words):
        bloom_msg = None
        for seed in self.seeds:
            is_ready = seed.water(current_words)
            if is_ready and not bloom_msg:
                bloom_msg = seed.bloom()
        return bloom_msg

    SAFE_MUTATIONS = {
        "STAMINA_REGEN",
        "MAX_DRAG_LIMIT",
        "GEODESIC_STRENGTH",
        "SIGNAL_DRAG_MULTIPLIER",
        "KINETIC_GAIN",
        "TOXIN_WEIGHT",
        "FLASHPOINT_THRESHOLD",
        "MAX_MEMORY_CAPACITY",
        "PRIORITY_LEARNING_RATE",
        "ANVIL_TRIGGER_VOLTAGE",
        "MAX_REPETITION_LIMIT",
        "PHYSICS.WEIGHT_HEAVY",
        "PHYSICS.WEIGHT_KINETIC",
        "PHYSICS.VOLTAGE_FLOOR",
        "PHYSICS.VOLTAGE_MAX",
        "BIO.CORTEX_SENSITIVITY",
        "BIO.ROS_CRITICAL",
        "BIO.DECAY_RATE",
        "BIO.REWARD_MEDIUM",
        "METABOLISM.PHOTOSYNTHESIS_GAIN",
        "METABOLISM.ROS_GENERATION_FACTOR",
        "COUNCIL.MANIC_VOLTAGE_TRIGGER",
        "GRAVITY_WELL_THRESHOLD",
    }

    def _apply_epigenetics(self, data):
        mutations = data.get("config_mutations", {})
        if not mutations:
            return
        if msg := ux("spore_strings", "net_audit_epig"):
            self.events.log(f"{Prisma.MAG}{msg}{Prisma.RST}")
        valid_mutations = 0
        for k, v in mutations.items():
            if k in self.SAFE_MUTATIONS and self._mutate_config(k, v):
                valid_mutations += 1
        if valid_mutations > 0 and (
            msg_ap := ux_format(
                "spore_strings", "net_apply_epig", count=valid_mutations
            )
        ):
            self.events.log(f"{Prisma.CYN}   {msg_ap}{Prisma.RST}")

    def ingest(self, target_file, current_tick=0):
        data = self.loader.load_spore(target_file)
        if not isinstance(data, dict):
            error_msg = ux("spore_strings", "net_spore_not_found")
            if error_msg:
                self.events.log(f"{Prisma.RED}{error_msg}{Prisma.RST}")
            return {}, set(), {}, None, {}
        required_keys = ["meta", "trauma_vector", "core_graph"]
        if not all(key in data for key in required_keys):
            reject_msg = ux("spore_strings", "net_spore_reject")
            if reject_msg:
                self.events.log(f"{Prisma.RED}{reject_msg}{Prisma.RST}")
            return {}, set(), {}, None, {}
        self._process_lineage(data)
        self._process_mutations(data)
        self._apply_epigenetics(data)
        core_graph_data = data.get("core_graph")
        if isinstance(core_graph_data, dict):
            self.graph.update(core_graph_data)
            for node in core_graph_data:
                self.graph[node]["last_tick"] = current_tick
        return self._extract_legacy_traits(data)

    def _process_lineage(self, data):
        session_source = data.get("session_id", "UNKNOWN_ANCESTOR")
        timestamp = (data.get("meta") or {}).get("timestamp", 0)
        time_ago = int((time.time() - timestamp) / 3600)
        trauma_raw = data.get("trauma_vector") or {}
        trauma_summary = {k: v for k, v in trauma_raw.items() if v > 0.1}
        mutations_raw = data.get("mutations") or {}
        mutation_count = sum(len(v) if v else 0 for v in mutations_raw.values())
        self.lineage_log.append(
            {
                "source": session_source,
                "age_hours": time_ago,
                "trauma": trauma_summary,
                "mutations": mutation_count,
                "loaded_at": time.time(),
            }
        )

    def _process_mutations(self, data):
        mutations = data.get("mutations") or {}
        if not mutations:
            return
        accepted_count = 0
        if not self.lex:
            return
        for cat, words in mutations.items():
            if not words:
                continue
            for w in words:
                current_cat = self.lex.get_current_category(w)
                if not current_cat or current_cat == "unknown":
                    self.lex.teach(w, cat, 0)
                    accepted_count += 1
        if accepted_count > 0:
            msg = ux("spore_strings", "net_mut_integ") or ""
            if msg:
                self.events.log(
                    f"{Prisma.CYN}{msg.format(count=accepted_count)}{Prisma.RST}"
                )

    def _extract_legacy_traits(self, data):
        self.village_legacy = data.get("village_data") or {}
        if "joy_legacy" in data and isinstance(data["joy_legacy"], dict):
            joy = data["joy_legacy"]
            clade = LiteraryReproduction.JOY_CLADE.get(joy.get("flavor"))
            if isinstance(clade, dict):
                if msg := ux_format("spore_strings", "net_glory", title=clade["title"]):
                    self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}")
                for stat, ancestral_bonus in clade.get("buff", {}).items():
                    if hasattr(self.cfg, stat):
                        setattr(self.cfg, stat, ancestral_bonus)
        if seeds_data := data.get("seeds"):
            self.seeds = []
            for s_data in seeds_data:
                new_seed = ParadoxSeed(s_data.get("q", ""), set())
                new_seed.maturity = s_data.get("m", 0.0)
                new_seed.bloomed = s_data.get("b", False)
                self.seeds.append(new_seed)
        return (
            data.get("mitochondria") or {},
            set(),
            data.get("soul_legacy") or {},
            data.get("continuity"),
            data.get("world_atlas") or {},
        )

    def save(
        self,
        health: float,
        stamina: float,
        mutations: dict,
        trauma_accum: dict,
        joy_history: List[Dict[str, Any]],
        mitochondria_traits=None,
        antibodies=None,
        soul_data=None,
        continuity=None,
        world_atlas=None,
        village_data=None,
    ):
        final_vector = {k: min(1.0, v) for k, v in trauma_accum.items()}
        valid_joy = [j for j in joy_history if isinstance(j, dict)]
        top_joy = sorted(valid_joy, key=lambda x: x.get("resonance", 0), reverse=True)[
            :3
        ]
        joy_legacy_data = None
        if top_joy:
            best_joy = top_joy[0]
            joy_legacy_data = {
                "flavor": best_joy.get("dominant_flavor", "UNKNOWN"),
                "resonance": best_joy.get("resonance", 0),
                "timestamp": best_joy.get("timestamp", 0),
            }
        core_graph = {}
        for k, data in self.graph.items():
            valid_edges = {
                t: round(w, 2) for t, w in data.get("edges", {}).items() if w > 1.0
            }
            if valid_edges or data.get("is_diamond", False):
                core_graph[k] = {
                    "edges": valid_edges,
                    "last_tick": 0,
                    "strata": data.get("strata"),
                    "is_diamond": data.get("is_diamond", False),
                }
        future_seed_q = self._generate_future_seed(
            temp_health=health, trauma_vec=final_vector
        )
        seed_list = [
            {"q": s.question, "m": s.maturity, "b": s.bloomed}
            for s in self.seeds
            if not s.bloomed
        ]
        if not any(s["q"] == future_seed_q for s in seed_list):
            seed_list.append({"q": future_seed_q, "m": 0.0, "b": False})
        data = {
            "genome": "BA_2070",
            "session_id": self.session_id,
            "parent_id": self.session_id,
            "meta": {
                "timestamp": time.time(),
                "final_health": health,
                "final_stamina": stamina,
            },
            "trauma_vector": final_vector,
            "joy_vectors": top_joy or [],
            "joy_legacy": joy_legacy_data,
            "core_graph": core_graph,
            "mutations": mutations or {},
            "mitochondria": mitochondria_traits,
            "soul_legacy": soul_data,
            "continuity": continuity,
            "world_atlas": world_atlas or {},
            "village_data": village_data,
            "seeds": seed_list,
            "fossils": list(self.fossils),
        }
        return self.loader.save_spore(self.filename, data)

    @staticmethod
    def _generate_future_seed(temp_health, trauma_vec) -> str:
        condition = "BALANCED"
        max_trauma = max(trauma_vec, key=trauma_vec.get) if trauma_vec else "NONE"
        if trauma_vec.get(max_trauma, 0) > 0.6 or temp_health < 30:
            condition = "HIGH_TRAUMA"
        seed_high = ux("spore_strings", "future_seed_high_trauma")
        seed_bal = ux("spore_strings", "future_seed_balanced")
        seed_def = ux("spore_strings", "future_seed_default")
        seeds = {"HIGH_TRAUMA": seed_high, "BALANCED": seed_bal}
        result = seeds.get(condition, seed_def)
        return result if isinstance(result, str) else "A new cycle begins."

    def cleanup_old_sessions(self, limbo_layer=None):
        files = self.loader.list_spores()
        removed = 0
        cfg = safe_get(self.cfg, "SPORES", {})
        max_files = int(safe_get(cfg, "MAX_FILES", 25))
        max_age = float(safe_get(cfg, "MAX_AGE_SECONDS", 86400))
        current_time = time.time()
        for i, (path, age, fname) in enumerate(files):
            file_age = current_time - age
            if i >= max_files or (file_age > max_age and i > 0):
                try:
                    if limbo_layer:
                        limbo_layer.absorb_dead_timeline(path)
                    if self.loader.delete_spore(path):
                        removed += 1
                except (OSError, AttributeError):
                    pass
        if removed and (msg := ux("spore_strings", "net_pruned_lines")):
            self.events.log(f"{Prisma.GRY}{msg.format(removed=removed)}{Prisma.RST}")

    def report_status(self):
        return len(self.graph)

    def autoload_last_spore(self):
        files = self.loader.list_spores()
        if not files:
            if msg := ux("spore_strings", "net_no_ancestor"):
                self.events.log(f"{Prisma.GRY}{msg}{Prisma.RST}")
            return None
        candidates = [f for f in files if self.session_id not in f[0]]
        for candidate in candidates:
            if result := self.ingest(candidate[0]):
                return result
        return None

    def retrieve_semantic(
        self,
        trigger_word: str,
        query_vector: list,
        scope: float = 0.5,
        resonance: float = 0.5,
    ) -> list:
        results = []
        if exact_match := self.hippocampus.retrieve_exact(trigger_word):
            results.append({"source": "hippocampus", "data": exact_match})
            if scope < 0.3:
                return results
        k_neighbors = max(1, int(scope * 10))
        cortex_results = self.cortex.query_neighborhood(
            query_vector=query_vector, k=k_neighbors, resonance_threshold=resonance
        )

        for res in cortex_results:
            if not res.get("raw_text") and (vh := res.get("vector_hash")):
                if phantom_text := self.cortex.resolve_phantom(vh):
                    res["raw_text"] = phantom_text

        radius_data = self.cortex.get_local_mass_radius(trigger_word)
        if radius_data:
            results.append({"source": "cortex_radius", "data": radius_data})

        results.extend({"source": "cortex", "data": res} for res in cortex_results)
        return results
