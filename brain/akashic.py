"""brain/akashic.py"""

import itertools
import json
import math
import os
import random
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple

from constants import Prisma
from core import JSONEncoder, LoreManifest
from presets import BoneConfig
from struts import safe_get, safe_set, ux


class TheAkashicRecord:
    def __init__(
        self,
        lore_manifest: Optional["LoreManifest"] = None,
        events_ref=None,
        config_ref=None,
    ):
        self.cfg = config_ref or BoneConfig
        self.discovered_words: Dict[str, str] = {}
        self.lens_cooccurrence: Dict[Tuple[str, str], int] = {}
        self.ingredient_affinity: Dict[str, int] = {}
        self.known_recipes: Set[Tuple[str, str]] = set()
        self.recipe_candidates: Dict[Tuple[str, str], Dict[str, int]] = {}
        self.cfg_akashic = safe_get(self.cfg, "AKASHIC", {})
        self.RECIPE_THRESHOLD = int(safe_get(self.cfg_akashic, "RECIPE_THRESHOLD", 3))
        self.HYBRID_LENS_THRESHOLD = int(
            safe_get(self.cfg_akashic, "HYBRID_LENS_THRESHOLD", 5)
        )
        self.MAX_SHADOW_CAPACITY = int(
            safe_get(self.cfg_akashic, "MAX_SHADOW_CAPACITY", 50)
        )
        self.lore = lore_manifest if lore_manifest else LoreManifest.get_instance()
        phys_const = self.lore.get("PHYSICS_CONSTANTS") or {}
        self.manifold_shifts = phys_const.get("MANIFOLD_SHIFTS") or {}
        self.trigram_map = phys_const.get("TRIGRAM_MAP") or {}
        self.fallback_trigrams = phys_const.get("FALLBACK_TRIGRAMS") or {}
        self.fallback_default = phys_const.get("FALLBACK_DEFAULT", "KAN")
        narrative_data = self.lore.get("NARRATIVE_DATA") or {}
        self.meta_resonance = narrative_data.get("_META_RESONANCE_", [])
        self.item_gen_data = self.lore.get("ITEM_GENERATION") or {}
        self.events = events_ref
        self.save_dir = safe_get(self.cfg_akashic, "SAVE_DIR", "saves")
        self.state_path = os.path.join(
            self.save_dir,
            safe_get(self.cfg_akashic, "STATE_FILE", "akashic_state.json"),
        )
        self.data_dir = getattr(self.lore, "DATA_DIR", "lore")
        self.shadow_stock: List[Dict] = []
        self.subconscious_strata: List[Dict] = []
        self.scar_map: List[Dict] = []
        self.dream_archive: List[str] = []
        self._load_mythos_state()

    def setup_listeners(self, event_bus):
        event_bus.subscribe("MYTHOLOGY_UPDATE", self._on_mythology_update)
        event_bus.subscribe("LENS_INTERACTION", self._on_lens_interaction)
        event_bus.subscribe("FORGE_SUCCESS", self._on_forge_event)
        event_bus.subscribe("GHOST_SIGNAL", self._on_ghost_signal)
        event_bus.subscribe("SYSTEM_STARVING", self._on_system_starving)
        event_bus.subscribe("TRAUMA_EVENT", self._on_trauma_event)
        event_bus.subscribe("GLIMMER_FORMED", self._on_glimmer_event)
        if msg := ux("akashic_strings", "listening"):
            if self.events:
                self.events.log(f"{Prisma.GRY}{msg}{Prisma.RST}")

    def _on_system_starving(self, _payload):
        yield_val, msg = self.trigger_autophagy()
        if msg and self.events:
            self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}")

    def _on_trauma_event(self, payload):
        if payload:
            concept = payload.get("concept", "Systemic Trauma")
            physics = payload.get("physics", {})
            self.record_scar(concept, physics)

    def _on_glimmer_event(self, payload):
        if payload and "concept" in payload and "paradigm" in payload:
            self.record_glimmer(payload["concept"], payload["paradigm"])

    def trigger_autophagy(self) -> Tuple[float, str]:
        """Hunt for the memory with the lowest Viability Potential (b = κγ - λμ). Project Navi, Apache 2.0"""
        akashic_cfg = safe_get(self.cfg, "AKASHIC", {})
        bio_cfg = safe_get(self.cfg, "BIO", {})
        active_strata = getattr(
            getattr(self, "active_memory_core", None), "subconscious", None
        )
        if active_strata and hasattr(active_strata, "index") and active_strata.index:
            target = None
            lowest_b = float("inf")
            for node_key, node_data in active_strata.index.items():
                kappa = float(node_data.get("mass", node_data.get("kappa", 1.0)))
                gamma = float(node_data.get("resonance", node_data.get("gamma", 0.5)))
                mu = float(node_data.get("contradiction", node_data.get("beta", 0.5)))
                b = (kappa * gamma) - mu
                if b < lowest_b:
                    lowest_b = b
                    target = node_key
            victim_data = active_strata.index.pop(target)
            mass = float(safe_get(victim_data, "mass", 1.0))
            yield_val = min(50.0, 10.0 + (mass * 2.5))
            if hasattr(active_strata, "_prune_strata"):
                active_strata._prune_strata()
            if bio_cfg:
                current_tax = float(safe_get(bio_cfg, "DEPTH_TAX_MULT", 1.0))
                safe_set(bio_cfg, "DEPTH_TAX_MULT", max(0.5, current_tax - 0.02))
            msg_template = (
                ux("akashic_strings", "autophagy_strata")
                or "Composted '{target}' and recovered {yield_val:.1f} ATP."
            )
            msg = msg_template.format(target=target, mass=mass, yield_val=yield_val)
        elif self.discovered_words:
            target = next(iter(self.discovered_words))
            category = self.discovered_words.pop(target)
            lexicon_data = self.lore.get("LEXICON") or {}
            if category in lexicon_data and target in lexicon_data[category]:
                lexicon_data[category].remove(target)
                self.lore.inject("LEXICON", lexicon_data)
            yield_val = float(safe_get(akashic_cfg, "AUTOPHAGY_YIELD", 15.0))
            msg_template = (
                ux("akashic_strings", "autophagy_lexical")
                or "Lexical purge: consumed {target}."
            )
            msg = msg_template.format(target=target, word=target)
        else:
            return 0.0, ux(
                "akashic_strings", "autophagy_failed"
            ) or "Starvation threshold. No matter left to consume."
        if self.events:
            self.events.publish(
                "AUTOPHAGY_EVENT", {"node": target, "atp_gained": yield_val}
            )
        self.save_all()
        return yield_val, msg

    def record_scar(self, concept: str, p: Any):
        cfg = safe_get(self.cfg, "AKASHIC", {})
        cfg_defaults = safe_get(cfg, "DEFAULT_SCAR_COORDS", {})
        axis_map = {
            "E": ("exhaustion", 0.2),
            "beta": ("beta_index", 0.4),
            "S": ("scope", 0.3),
            "D": ("depth", 0.3),
            "C": ("connectivity", 0.2),
            "T": ("trauma", 0.0),
            "psi": ("psi", 0.0),
            "chi": ("entropy", 0.0),
            "valence": ("valence", 0.0),
            "ROS": ("ros", 0.0),
        }
        coords = {}
        energy_layer = safe_get(p, "energy") or {}
        for short_key, (full_key, default_val) in axis_map.items():
            val = (
                p.get(short_key, p.get(full_key))
                if isinstance(p, dict)
                else getattr(p, short_key, getattr(p, full_key, None))
            )
            coords[short_key] = (
                val
                if val is not None
                else energy_layer.get(
                    full_key, cfg_defaults.get(short_key, default_val)
                )
            )
        self.scar_map.append(
            {"concept": concept, "coordinates": coords.copy(), "gilded": True}
        )
        max_scars = getattr(self.cfg_akashic, "MAX_SCARS", 50)
        if len(self.scar_map) > max_scars:
            self.scar_map.pop(0)
        self.store_ghost_echo(
            {"type": "SCAR_GHOST", "concept": concept, "coords": coords.copy()}
        )
        self._save_user_state()
        self._mutate_system_prompts(concept, coords)
        if self.events:
            msg = ux("akashic_strings", "mercy_scar")
            self.events.log(
                f"{Prisma.OCHRE}{msg.format(concept=concept)}{Prisma.RST}", "VILLAGE"
            )
            self.events.publish("SCAR_RECORDED", {"concept": concept, "coords": coords})

    def _mutate_epigenetics(
        self,
        category_key: str,
        axiom: str,
        max_items: int,
        log_msg: str,
        log_color: str,
    ):
        try:
            prompts = self.lore.get("SYSTEM_PROMPTS") or {}
            epigenetic_list = prompts.setdefault("GLOBAL_BASELINE", {}).setdefault(
                category_key, []
            )
            if not isinstance(epigenetic_list, list):
                epigenetic_list = []
                prompts["GLOBAL_BASELINE"][category_key] = epigenetic_list
            if axiom not in epigenetic_list:
                epigenetic_list.append(axiom)
                if len(epigenetic_list) > max_items:
                    epigenetic_list.pop(0)
                self.lore.inject("SYSTEM_PROMPTS", prompts)
                self.lore.save("SYSTEM_PROMPTS")
                if self.events:
                    self.events.log(f"{log_color}{log_msg}{Prisma.RST}", "SYS")
        except Exception as e:
            if self.events:
                self.events.log(
                    f"{Prisma.RED}Failed to mutate system_prompts ({category_key}): {e}{Prisma.RST}",
                    "SYS",
                )

    def record_glimmer(self, concept: str, paradigm: str):
        axiom = f"STRUCTURAL SUCCESS [{concept.upper()}]: The system achieved deep resonance using this paradigm: '{paradigm}'. Remember this."
        max_epi = int(safe_get(self.cfg_akashic, "MAX_EPIGENETIC_BOONS", 10))
        self._mutate_epigenetics(
            "EPIGENETIC_BOONS",
            axiom,
            max_epi,
            f"Epigenetic Boon, '{concept},' compiled into flow.",
            Prisma.MAG,
        )

    def _mutate_system_prompts(self, concept: str, coords: dict):
        axiom = f"SCAR TISSUE [{concept.upper()}]: The system previously collapsed here (Tension: {coords.get('beta', 0.0)}). Remember this."
        max_epi = int(safe_get(self.cfg_akashic, "MAX_EPIGENETIC_SCARS", 10))
        self._mutate_epigenetics(
            "EPIGENETIC_SCARS",
            axiom,
            max_epi,
            f"[EPIGENETICS] Scar '{concept}' compiled into flow.",
            Prisma.VIOLET,
        )

    def bury_memory(self, concept: str, data: Dict):
        self.subconscious_strata.append({"concept": concept, "data": data})
        max_strata = int(safe_get(self.cfg_akashic, "MAX_SUBCONSCIOUS_CAPACITY", 100))
        if len(self.subconscious_strata) > max_strata:
            self.subconscious_strata.pop(0)

    def _on_lens_interaction(self, payload):
        lenses = payload.get("lenses", [])
        if lenses:
            self.record_interaction(lenses)

    def _on_forge_event(self, payload):
        if not payload:
            return
        self.track_successful_forge(
            payload.get("ingredient"), payload.get("catalyst"), payload.get("result")
        )

    @staticmethod
    def _get_dominant_force(vector_dict: Dict, default: str) -> str:
        if not isinstance(vector_dict, dict):
            return default
        valid_keys = [k for k, v in vector_dict.items() if v is not None]
        return max(valid_keys, key=lambda k: vector_dict[k]) if valid_keys else default

    def _extract_dominant_trigram(self, physics: Any) -> str:
        vector = safe_get(physics, "vector", {})
        dom = self._get_dominant_force(vector, "KAN")
        if dom in self.trigram_map and len(self.trigram_map[dom]) > 1:
            return self.trigram_map[dom][1]
        return self.fallback_trigrams.get(dom, self.fallback_default)

    def _on_mythology_update(self, payload):
        if not payload:
            return
        if (words := payload.get("words")) and (category := payload.get("category")):
            self.propose_new_category(words, category)
            return
        if (word := payload.get("word")) and (category := payload.get("category")):
            self.register_word(word, category)
            return
        if "physics" in payload:
            trigram = self._extract_dominant_trigram(payload["physics"])
            active_lens = payload.get("lens", "OBSERVER")
            valid_resonance = next(
                (
                    r
                    for r in self.meta_resonance
                    if isinstance(r, dict)
                    and r.get("trigram") == trigram
                    and (r.get("lens") or r.get("soul")) == active_lens
                ),
                None,
            )
            if isinstance(valid_resonance, dict) and self.events:
                self.events.publish(
                    "RESONANCE_ACHIEVED",
                    {
                        "result": valid_resonance.get("result", ""),
                        "msg": valid_resonance.get("msg", ""),
                    },
                )

    def calculate_manifold_shift(
        self, theta: str, e: Dict[str, float]
    ) -> Dict[str, float]:
        theta_upper = theta.upper()
        c = self.manifold_shifts
        bias_lenses = c.get("BIAS_LENSES") or {}
        scalar_lenses = c.get("SCALAR_LENSES") or {}
        vector_thresholds = c.get("VECTOR_THRESHOLDS") or {}
        bias = float(bias_lenses.get(theta_upper, 0.0))
        scalar = float(scalar_lenses.get(theta_upper, 1.0))
        for key, params in vector_thresholds.items():
            safe_params = params or {}
            if e.get(key, 0.5) > safe_params.get("threshold", 0.7):
                scalar = scalar * float(safe_params.get("scalar_mod", 1.0))
                bias = bias + float(safe_params.get("bias_mod", 0.0))
        return {"voltage_bias": bias, "drag_scalar": scalar}

    def _on_ghost_signal(self, payload):
        if payload:
            self.store_ghost_echo(payload)

    def forge_new_item(self, vector: Dict[str, float]) -> Tuple[str, Dict]:
        dominant_force = self._get_dominant_force(vector, "CHI")
        item_gen_data = self.item_gen_data
        prefixes = item_gen_data.get("PREFIXES", {})
        prefix = prefixes.get(
            dominant_force, item_gen_data.get("FALLBACK_PREFIX", "Ascended")
        )
        unique_suffix = str(uuid.uuid4())[:4].upper()
        new_name = f"{prefix.upper()}_ARTIFACT_{int(vector.get(dominant_force, 0) * 10)}_{unique_suffix}"
        hazards = []
        hazard_thresholds = item_gen_data.get("HAZARD_THRESHOLDS", {})
        for force, threshold_data in hazard_thresholds.items():
            if vector.get(force, 0) > threshold_data.get("threshold", 0.5):
                hazards.append(threshold_data.get("hazard_name"))
        desc_template = (
            ux("akashic_strings", "artifact_desc") or "An artifact of {dominant_force}."
        )
        cfg = safe_get(self.cfg, "AKASHIC", {})
        artifact_val = float(safe_get(cfg, "ARTIFACT_VALUE", 50.0))
        new_data = {
            "name": new_name,
            "description": desc_template.format(dominant_force=dominant_force),
            "function": "ARTIFACT",
            "passive_traits": hazards,
            "value": artifact_val,
        }
        gordon_data = self.lore.get("GORDON") or {}
        registry = gordon_data.get("ITEM_REGISTRY", {})
        registry[new_name] = new_data
        gordon_data["ITEM_REGISTRY"] = registry
        self.lore.inject("GORDON", gordon_data)
        self.lore.save("GORDON")
        return new_name, new_data

    def save_all(self):
        self.save_to_disk("discovered_words", self.discovered_words)
        self._save_user_state()
        msg = ux("akashic_strings", "mythos_persisted")
        if self.events:
            self.events.log(f"{Prisma.GRY}{msg}{Prisma.RST}", "AKASHIC")

    def _save_user_state(self):
        state = {
            "lens_cooccurrence": {
                f"{k[0]}|{k[1]}": v for k, v in self.lens_cooccurrence.items()
            },
            "recipe_candidates": {
                f"{k[0]}|{k[1]}": v for k, v in self.recipe_candidates.items()
            },
            "ingredient_affinity": self.ingredient_affinity,
            "shadow_stock": self.shadow_stock,
            "subconscious_strata": self.subconscious_strata,
            "scar_map": self.scar_map,
            "dream_archive": self.dream_archive,
        }
        self.save_to_disk("state", state)

    def save_to_disk(self, category: str, data: Any):
        base_dir = os.path.realpath(
            self.data_dir
            if category in ["discovered_words", "scars", "boons"]
            else self.save_dir
        )
        filepath = os.path.realpath(os.path.join(base_dir, f"akashic_{category}.json"))
        if os.path.commonpath([base_dir, filepath]) != base_dir:
            if self.events:
                self.events.log(
                    f"{Prisma.RED}Geometric containment violation. Save aborted.{Prisma.RST}",
                    "CRIT",
                )
            return
        try:
            os.makedirs(base_dir, exist_ok=True)
            os.makedirs(os.path.realpath(self.save_dir), exist_ok=True)
            temp_path = f"{filepath}.{uuid.uuid4().hex}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, cls=JSONEncoder)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, filepath)
            if msg := ux("akashic_strings", "saved_category"):
                if self.events:
                    self.events.log(
                        f"{Prisma.GRY}{msg.format(category=category)}{Prisma.RST}",
                        "AKASHIC",
                    )
        except Exception as e:
            msg = ux("akashic_strings", "save_failed_category")
            if self.events:
                self.events.log(
                    f"{Prisma.RED}{msg.format(category=category, error=e)}{Prisma.RST}",
                    "AKASHIC",
                )

    def _load_mythos_state(self):
        data = {}
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                msg = ux("akashic_strings", "state_load_failed")
                if self.events:
                    self.events.log(f"{Prisma.RED}{msg.format(error=e)}{Prisma.RST}")
        if data:
            self.lens_cooccurrence.clear()
            data_lens = data.get("lens_cooccurrence") or {}
            for k, v in data_lens.items():
                if isinstance(k, str) and "|" in k:
                    p1, p2 = k.split("|", 1)
                    self.lens_cooccurrence[(p1, p2)] = int(v)
            self.recipe_candidates.clear()
            data_recipes = data.get("recipe_candidates") or {}
            for k, v in data_recipes.items():
                if isinstance(k, str) and "|" in k and isinstance(v, dict):
                    p1, p2 = k.split("|", 1)
                    self.recipe_candidates[(p1, p2)] = {
                        str(vk): int(vv) for vk, vv in v.items()
                    }
            self.ingredient_affinity = data.get("ingredient_affinity", {})
            self.shadow_stock = data.get("shadow_stock", [])
            self.dream_archive = data.get("dream_archive", [])
            self.known_recipes.clear()
            gordon_data = self.lore.get("GORDON") or {}
            if recipes := gordon_data.get("RECIPES", []):
                self.known_recipes.update(
                    (r.get("ingredient"), r.get("catalyst_category"))
                    for r in recipes
                    if r.get("ingredient") and r.get("catalyst_category")
                )

        scars_path = os.path.join(self.data_dir, "akashic_scars.json")
        boons_path = os.path.join(self.data_dir, "akashic_boons.json")
        prompts = self.lore.get("SYSTEM_PROMPTS") or {}
        needs_migration = False
        paths_to_remove = []
        for path, key in [
            (scars_path, "EPIGENETIC_SCARS"),
            (boons_path, "EPIGENETIC_BOONS"),
        ]:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        prompts.setdefault("GLOBAL_BASELINE", {})[key] = (
                            data if isinstance(data, list) else []
                        )
                        needs_migration = True
                        paths_to_remove.append(path)
                except Exception as e:
                    if self.events:
                        self.events.log(
                            f"{Prisma.RED}Failed to migrate legacy {key}: {e}.{Prisma.RST}"
                        )
        if needs_migration:
            try:
                self.lore.inject("SYSTEM_PROMPTS", prompts)
                self.lore.save("SYSTEM_PROMPTS")
                for p in paths_to_remove:
                    os.remove(p)
            except Exception as e:
                if self.events:
                    self.events.log(
                        f"{Prisma.RED}Migration save failed: {e}. Legacy files kept intact.{Prisma.RST}"
                    )
        words_path = os.path.join(self.data_dir, "akashic_discovered_words.json")
        if os.path.exists(words_path):
            try:
                with open(words_path, "r", encoding="utf-8") as f:
                    self.discovered_words = json.load(f)
                    lexicon_data = self.lore.get("LEXICON") or {}
                    for word, category in self.discovered_words.items():
                        target_list = lexicon_data.setdefault(category, [])
                        if word not in target_list:
                            target_list.append(word)
                    self.lore.inject("LEXICON", lexicon_data)
            except Exception as e:
                if self.events:
                    self.events.log(
                        f"{Prisma.RED}Failed to load discovered words: {e}. Keeping current state.{Prisma.RST}"
                    )

    def archive_dream(self, dream_text: str):
        """Archives a dream and immediately persists it to disk."""
        if dream_text not in self.dream_archive:
            self.dream_archive.append(dream_text)
            if len(self.dream_archive) > 50:
                self.dream_archive.pop(0)
            self._save_user_state()

    def replay_dreams(self) -> Optional[str]:
        """Recalls a persistent dream from a past or present session."""
        if not self.dream_archive:
            return None
        echo = random.choice(self.dream_archive)
        return f"An echo of a past dream surfaces: {echo}"

    def record_interaction(
        self, lenses_active: list, ingredients_used: Optional[list] = None
    ):
        if len(lenses_active) >= 2:
            key = tuple(sorted(lenses_active[:2]))
            self.lens_cooccurrence[key] = self.lens_cooccurrence.get(key, 0) + 1
            if self.lens_cooccurrence[key] == self.HYBRID_LENS_THRESHOLD:
                self._hybridize_lenses(key[0], key[1])
        if ingredients_used:
            for item in ingredients_used:
                self.ingredient_affinity[item] = (
                    self.ingredient_affinity.get(item, 0) + 1
                )

    def track_successful_forge(self, ingredient_name, catalyst_type, result_item):
        if not ingredient_name or not catalyst_type:
            return
        recipe_key = (ingredient_name, catalyst_type)
        if recipe_key in self.known_recipes:
            return
        self.recipe_candidates.setdefault(recipe_key, {})
        result_name = "Unknown Artifact"
        if isinstance(result_item, dict):
            result_name = result_item.get("name") or result_item.get(
                "description", result_name
            )
        elif isinstance(result_item, str):
            registry = (self.lore.get("GORDON") or {}).get("ITEM_REGISTRY", {})
            result_name = registry.get(result_item, {}).get("description", result_item)
        self.recipe_candidates[recipe_key][result_name] = (
            self.recipe_candidates[recipe_key].get(result_name, 0) + 1
        )
        if self.recipe_candidates[recipe_key][result_name] == self.RECIPE_THRESHOLD:
            self._crystallize_recipe(
                ingredient_name, catalyst_type, result_item, result_name
            )

    def _hybridize_lenses(self, lens_a: str, lens_b: str):
        if lens_a == lens_b:
            return

        def strip_prefix(s):
            return s[4:] if s.startswith("THE ") else s

        roots = sorted([strip_prefix(lens_a), strip_prefix(lens_b)])
        new_name = f"THE {roots[0]}-{roots[1]}"
        existing_lenses = self.lore.get("LENSES") or {}
        if new_name in existing_lenses:
            return
        w_a = safe_get(existing_lenses, lens_a, {}).get("weights", {})
        w_b = safe_get(existing_lenses, lens_b, {}).get("weights", {})
        v_a, v_b = (
            float(w_a.get("voltage", w_a.get("v", 0.0))),
            float(w_b.get("voltage", w_b.get("v", 0.0))),
        )
        d_a, d_b = (
            float(w_a.get("drag", w_a.get("d", 0.0))),
            float(w_b.get("drag", w_b.get("d", 0.0))),
        )
        new_weights = {
            "voltage": round((v_a + v_b) / 2, 2),
            "drag": round((d_a + d_b) / 2, 2),
        }
        desc_template = ux("akashic_strings", "lens_desc")
        new_lens_data = {
            "description": desc_template.format(lens_a=lens_a, lens_b=lens_b),
            "weights": new_weights,
            "parentage": [lens_a, lens_b],
        }
        self.lore.inject("LENSES", {new_name: new_lens_data})
        self.lore.save("LENSES")
        self.discovered_words[new_name] = "LENS"
        msg = ux("akashic_strings", "paradigm_crystallized")
        if self.events:
            self.events.log(f"{Prisma.MAG}{msg.format(new_name=new_name)}{Prisma.RST}")
            self.events.publish("SOUL_MUTATION", {"new_archetype": new_name})

    def _crystallize_recipe(self, ingredient, catalyst, result_item, result_name: str = "Unknown"):
        self.known_recipes.add((ingredient, catalyst))
        msg_template = (
            ux("akashic_strings", "recipe_msg")
            or "Forged {result_name} from {ingredient}."
        )
        new_recipe = {
            "ingredient": ingredient,
            "catalyst_category": catalyst,
            "result": result_item,
            "msg": msg_template.format(
                ingredient=ingredient,
                catalyst=catalyst,
                result_name=result_name,
                result_item=result_name
            ),
        }
        gordon_data = self.lore.get("GORDON") or {}
        current_recipes = gordon_data.get("RECIPES", [])
        current_recipes.append(new_recipe)
        gordon_data["RECIPES"] = current_recipes
        self.lore.inject("GORDON", gordon_data)
        self.lore.save("GORDON")
        msg = ux("akashic_strings", "recipe_recorded")
        if self.events:
            self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}")

    def propose_new_category(self, word_list, category_name):
        lexicon_data = self.lore.get("LEXICON") or {}
        target_list = lexicon_data.setdefault(category_name, [])
        new_words = list(set(word_list) - set(target_list))
        if new_words:
            target_list.extend(new_words)
            self.discovered_words.update((w, category_name) for w in new_words)
            self.lore.inject("LEXICON", lexicon_data)
            msg_template = (
                ux("akashic_strings", "lexicon_learned")
                or "Learned {word} in {category}."
            )
            if self.events:
                for w in new_words:
                    self.events.log(msg_template.format(word=w, category=category_name))
            self.lore.save("LEXICON")
            if self.events:
                for w in new_words:
                    self.events.publish(
                        "MYTHOLOGY_UPDATE", {"word": w, "category": category_name}
                    )

    def store_ghost_echo(self, memory_data: Dict):
        self.shadow_stock.append(memory_data)
        if len(self.shadow_stock) > self.MAX_SHADOW_CAPACITY:
            self.shadow_stock.pop(0)
        concept = memory_data.get("concept", "An unknown echo")
        msg = (
            ux("akashic_strings", "ghost_archived")
            or f"A load-bearing memory refused to die. [{concept.upper()}] has entered the Shadow Archive."
        )
        if self.events:
            try:
                formatted_msg = msg.format(concept=concept)
            except KeyError:
                formatted_msg = msg
            self.events.log(f"{Prisma.VIOLET}{formatted_msg}{Prisma.RST}", "AKASHIC")

    def measure_cognitive_density(self, start_concept: str) -> float:
        """[navi-fractal PROTOCOL]: BFS Mass-Radius Subconscious Scaling"""
        adj = {}
        for mem in itertools.chain(self.scar_map, self.shadow_stock):
            concept = mem.get("concept", "Unknown")
            links = mem.get("links", [])
            adj[concept] = set(links)
            for link in links:
                if link not in adj:
                    adj[link] = set()
                adj[link].add(concept)
        if start_concept not in adj or not adj[start_concept]:
            return 1.0
        visited = {start_concept}
        queue = [(start_concept, 0)]
        mass_at_r = {}
        while queue:
            node, r = queue.pop(0)
            mass_at_r[r] = mass_at_r.get(r, 0) + 1
            for neighbor in adj.get(node, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, r + 1))
        max_r = max(mass_at_r.keys()) if mass_at_r else 0
        total_mass = sum(mass_at_r.values())
        if max_r > 1 and total_mass > 1:
            return math.log(total_mass) / math.log(max_r)
        return 1.0

    def dredge_creative_tension(self) -> Optional[Dict]:
        """[CD PROTOCOL]: Gradient-Descent Memory Retrieval (Creative Drive RAG)"""
        best_memory = None
        max_drive = -1.0
        for mem in itertools.chain(self.shadow_stock, self.scar_map):
            coords = mem.get("coords") or mem.get("coordinates") or {}
            kappa = float(coords.get("kappa", coords.get("E", 0.5)))
            gamma = float(coords.get("gamma", coords.get("C", 0.5)))
            mu = float(coords.get("mu", coords.get("beta", 0.5)))
            creative_drive = kappa * gamma * mu
            if creative_drive > max_drive:
                max_drive = creative_drive
                best_memory = mem
        if best_memory and getattr(self, "events", None):
            concept = best_memory.get("concept", "Unknown")
            self.events.log(
                f"{Prisma.CYN}[CD RAG] Dredged '{concept}' (Drive a={max_drive:.2f}). Productive tension located.{Prisma.RST}",
                "SYS",
            )
        return best_memory

    def register_word(self, word: str, category: str) -> bool:
        if self.discovered_words.get(word) == category:
            return False
        lexicon_data = self.lore.get("LEXICON") or {}
        target_category = lexicon_data.setdefault(category, [])
        if word not in target_category:
            target_category.append(word)
            self.discovered_words[word] = category
            self.lore.inject("LEXICON", lexicon_data)
            msg = (
                ux("akashic_strings", "lexicon_expands")
                or "Lexicon expands: {category}"
            )
            if self.events:
                self.events.log(msg.format(category=category.upper()))
            bloat_limit = int(safe_get(self.cfg_akashic, "BLOAT_THRESHOLD", 50))
            exempt_categories = safe_get(
                self.cfg_akashic, "BLOAT_EXEMPT_CATEGORIES", ["heavy"]
            )
            if (
                len(lexicon_data[category]) == bloat_limit + 1
                and category not in exempt_categories
            ):
                bloat_msg = ux(
                    "akashic_strings",
                    "lexicon_bloat",
                    default="[WARNING] Lexicon category '{category}' is bloated.",
                )
                if self.events:
                    self.events.log(bloat_msg.format(category=category))
            return True
        return False
