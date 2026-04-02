"""bone_akashic.py"""

import json
import os
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple, cast

from bone_core import BoneJSONEncoder, LoreManifest, ux, safe_get
from bone_presets import BoneConfig
from bone_types import Prisma


class TheAkashicRecord:
    def __init__(self, lore_manifest: Optional["LoreManifest"] = None, events_ref=None):
        self.discovered_words: Dict[str, str] = {}
        self.lens_cooccurrence: Dict[Tuple[str, str], int] = {}
        self.ingredient_affinity: Dict[str, int] = {}
        self.known_recipes: Set[Tuple[str, str]] = set()
        self.recipe_candidates: Dict[Tuple[str, str], Dict[str, int]] = {}
        cfg = getattr(BoneConfig, "AKASHIC", None)
        self.RECIPE_THRESHOLD = getattr(cfg, "RECIPE_THRESHOLD", 3) if cfg else 3
        self.HYBRID_LENS_THRESHOLD = (
            getattr(cfg, "HYBRID_LENS_THRESHOLD", 5) if cfg else 5
        )
        self.MAX_SHADOW_CAPACITY = (
            getattr(cfg, "MAX_SHADOW_CAPACITY", 50) if cfg else 50
        )
        self.lore = lore_manifest if lore_manifest else LoreManifest.get_instance()
        self.events = events_ref
        self.shadow_stock: List[Dict] = []
        self.subconscious_strata: List[Dict] = []
        self.scar_map: List[Dict] = []
        self._load_mythos_state()

    def setup_listeners(self, event_bus):
        event_bus.subscribe("MYTHOLOGY_UPDATE", self._on_mythology_update)
        event_bus.subscribe("LENS_INTERACTION", self._on_lens_interaction)
        event_bus.subscribe("FORGE_SUCCESS", self._on_forge_event)
        event_bus.subscribe("GHOST_SIGNAL", self._on_ghost_signal)
        msg = ux("akashic_strings", "listening")
        print(f"{Prisma.CYN}{msg}{Prisma.RST}")

    def trigger_autophagy(self) -> Tuple[float, str]:
        cfg = getattr(BoneConfig, "AKASHIC", None)
        yield_val = getattr(cfg, "AUTOPHAGY_YIELD", 15.0) if cfg else 15.0

        if self.subconscious_strata:
            target = self.subconscious_strata.pop(0).get("concept", "Unknown Node")
            msg = ux("akashic_strings", "autophagy_memory")
        elif self.discovered_words:
            target = next(iter(self.discovered_words))
            del self.discovered_words[target]
            msg = ux("akashic_strings", "autophagy_lexical")
        else:
            return 0.0, ux("akashic_strings", "autophagy_failed")

        if self.events:
            self.events.publish(
                "AUTOPHAGY_EVENT", {"node": target, "atp_gained": yield_val}
            )
        return yield_val, msg.format(target=target, word=target)

    def record_scar(self, concept: str, p: Any):
        cfg_defaults = getattr(getattr(BoneConfig, "AKASHIC", None), "DEFAULT_SCAR_COORDS", {})
        default_coords = {
            "E": ("exhaustion", cfg_defaults.get("E", 0.2)), "beta": ("beta_index", cfg_defaults.get("beta", 0.4)),
            "S": ("scope", cfg_defaults.get("S", 0.3)), "D": ("depth", cfg_defaults.get("D", 0.3)),
            "C": ("connectivity", cfg_defaults.get("C", 0.2)), "T": ("trauma", cfg_defaults.get("T", 0.0)),
            "psi": ("psi", cfg_defaults.get("psi", 0.0)), "chi": ("entropy", cfg_defaults.get("chi", 0.0)),
            "valence": ("valence", cfg_defaults.get("valence", 0.0)), "ROS": ("ros", cfg_defaults.get("ROS", 0.0)),
        }
        coords = {k: val if (val := safe_get(p, k)) is not None else safe_get(safe_get(p, "energy"), real_k, d_val) for k, (real_k, d_val) in default_coords.items()}
        self.scar_map.append({"concept": concept, "coordinates": coords, "gilded": True})
        self.store_ghost_echo(
            {"type": "SCAR_GHOST", "concept": concept, "coords": coords}
        )
        self._save_user_state()
        self._mutate_system_prompts(concept, coords)
        if self.events:
            msg = ux("akashic_strings", "mercy_scar")
            self.events.log(
                f"{Prisma.OCHRE}{msg.format(concept=concept)}{Prisma.RST}", "VILLAGE"
            )
            self.events.publish("SCAR_RECORDED", {"concept": concept, "coords": coords})

    def _mutate_system_prompts(self, concept: str, coords: dict):
        try:
            prompts = self.lore.get("SYSTEM_PROMPTS") or {}
            epigenetic_list = prompts.setdefault("GLOBAL_BASELINE", {}).setdefault(
                "EPIGENETIC_SCARS", []
            )
            axiom = f"SCAR TISSUE [{concept.upper()}]: The system previously collapsed here (Tension: {coords.get('beta', 0.0)}). You must structurally avoid repeating the failure that caused this."
            if axiom not in epigenetic_list:
                epigenetic_list.append(axiom)
                self.lore.inject("SYSTEM_PROMPTS", prompts)
                self.save_to_disk("system_prompts", prompts)
                if self.events:
                    self.events.log(
                        f"{Prisma.VIOLET}🧬 [EPIGENETICS] Scar '{concept}' compiled into bedrock.{Prisma.RST}",
                        "SYS",
                    )
        except Exception as e:
            if self.events:
                self.events.log(
                    f"{Prisma.RED}Failed to mutate system_prompts: {e}{Prisma.RST}",
                    "SYS",
                )

    def bury_memory(self, concept: str, data: Dict):
        self.subconscious_strata.append({"concept": concept, "data": data})

    def _on_lens_interaction(self, payload):
        lenses = payload.get("lenses", [])
        if lenses:
            self.record_interaction(lenses)

    def _on_forge_event(self, payload):
        if not payload or not isinstance(payload, dict):
            return
        self.track_successful_forge(
            payload.get("ingredient"), payload.get("catalyst"), payload.get("result")
        )

    @staticmethod
    def _extract_dominant_trigram(physics: Any) -> str:
        vector = safe_get(physics, "vector", {})
        valid_items = (
            {k: v for k, v in vector.items() if v is not None}
            if isinstance(vector, dict)
            else {}
        )
        dom = max(valid_items, key=valid_items.get, default="KAN")
        constants = LoreManifest.get_instance().get("PHYSICS_CONSTANTS") or {}
        trigrams = constants.get("TRIGRAM_MAP", {})
        return (
            trigrams[dom][1]
            if dom in trigrams and len(trigrams[dom]) > 1
            else constants.get("FALLBACK_TRIGRAMS", {}).get(
                dom, constants.get("FALLBACK_DEFAULT", "KAN")
            )
        )

    def _on_mythology_update(self, payload):
        if not payload or not isinstance(payload, dict):
            return
        word = payload.get("word")
        category = payload.get("category")

        if word and category:
            self.register_word(word, category)
            return
        if "physics" in payload:
            physics = payload.get("physics", {})
            trigram = self._extract_dominant_trigram(physics)
            active_lens = payload.get("lens", "OBSERVER")
            narrative_data = self.lore.get("NARRATIVE_DATA") or {}
            resonances = narrative_data.get("_META_RESONANCE_", [])
            for resonance in resonances:
                if resonance.get("trigram") == trigram:
                    target_lens = resonance.get("lens", resonance.get("soul"))
                    if target_lens == active_lens:
                        if self.events:
                            self.events.publish(
                                "RESONANCE_ACHIEVED",
                                {
                                    "result": resonance["result"],
                                    "msg": resonance["msg"],
                                },
                            )

    @staticmethod
    def calculate_manifold_shift(theta: str, e: Dict[str, float]) -> Dict[str, float]:
        theta_upper = theta.upper()
        c = (
            LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "MANIFOLD_SHIFTS")
            or {}
        )
        bias = sum(
            b_val for w, b_val in c.get("BIAS_LENSES", {}).items() if w in theta_upper
        )
        scalar = math.prod(
            s_val for w, s_val in c.get("SCALAR_LENSES", {}).items() if w in theta_upper
        )
        for key, params in c.get("VECTOR_THRESHOLDS", {}).items():
            if e.get(key, 0.5) > params.get("threshold", 0.7):
                scalar *= params.get("scalar_mod", 1.0)
                bias += params.get("bias_mod", 0.0)
        return {"voltage_bias": bias, "drag_scalar": scalar}

    def _on_ghost_signal(self, payload):
        if payload:
            self.store_ghost_echo(payload)

    def forge_new_item(self, vector: Dict[str, float]) -> Tuple[str, Dict]:
        valid_items = (
            {k: v for k, v in (vector or {}).items() if v is not None}
            if isinstance(vector, dict)
            else {}
        )
        dominant_force = max(valid_items, key=valid_items.get, default="CHI")
        item_gen_data = self.lore.get("ITEM_GENERATION") or {}
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
            ux("akashic_strings", "artifact_desc")
            or "A coalesced artifact of {dominant_force}."
        )
        cfg = getattr(BoneConfig, "AKASHIC", None)
        artifact_val = getattr(cfg, "ARTIFACT_VALUE", 50.0) if cfg else 50.0
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
        return new_name, new_data

    def save_all(self):
        self.save_to_disk("discovered_words", self.discovered_words)
        self._save_user_state()
        msg = ux("akashic_strings", "mythos_persisted")
        print(f"{Prisma.GRY}{msg}{Prisma.RST}")

    def _save_user_state(self):
        state = {
            "lens_cooccurrence": {
                f"{k[0]}|{k[1]}": v for k, v in self.lens_cooccurrence.items()
            },
            "ingredient_affinity": self.ingredient_affinity,
            "shadow_stock": self.shadow_stock,
            "subconscious_strata": self.subconscious_strata,
            "scar_map": self.scar_map,
        }
        cfg = getattr(BoneConfig, "AKASHIC", None)
        save_dir = getattr(cfg, "SAVE_DIR", "saves")
        state_file = getattr(cfg, "STATE_FILE", "akashic_state.json")
        save_path = os.path.join(save_dir, state_file)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            msg = ux("akashic_strings", "save_failed")
            print(f"{Prisma.RED}{msg.format(error=e)}{Prisma.RST}")

    def save_to_disk(self, category: str, data: Any):
        directory = getattr(self.lore, "DATA_DIR", "lore")
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                msg = ux("akashic_strings", "dir_create_failed")
                print(
                    f"{Prisma.RED}{msg.format(directory=directory, error=e)}{Prisma.RST}"
                )
                return
        filename = f"akashic_{category}.json"
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, cls=BoneJSONEncoder)
            msg = ux("akashic_strings", "saved_category")
            print(f"{Prisma.GRY}{msg.format(category=category)}{Prisma.RST}")
        except Exception as e:
            msg = ux("akashic_strings", "save_failed_category")
            print(f"{Prisma.RED}{msg.format(category=category, error=e)}{Prisma.RST}")

    def _load_mythos_state(self):
        data = {}
        cfg = getattr(BoneConfig, "AKASHIC", None)
        save_dir = getattr(cfg, "SAVE_DIR", "saves")
        state_file = getattr(cfg, "STATE_FILE", "akashic_state.json")
        save_path = os.path.join(save_dir, state_file)
        if os.path.exists(save_path):
            try:
                with open(save_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                msg = ux("akashic_strings", "state_load_failed")
                print(f"{Prisma.RED}{msg.format(error=e)}{Prisma.RST}")
        if not data:
            return
        raw_cooc = data.get("lens_cooccurrence", {})
        for k, v in raw_cooc.items():
            if "|" in k:
                p1, p2 = k.split("|", 1)
                self.lens_cooccurrence[(p1, p2)] = v
        self.ingredient_affinity = data.get("ingredient_affinity", {})
        self.shadow_stock = data.get("shadow_stock", [])
        gordon_data = self.lore.get("GORDON")
        if gordon_data and "RECIPES" in gordon_data:
            for r in gordon_data["RECIPES"]:
                ing = r.get("ingredient")
                cat = r.get("catalyst_category")
                if ing and cat:
                    self.known_recipes.add((ing, cat))
        directory = getattr(self.lore, "DATA_DIR", "lore")
        words_path = os.path.join(directory, "akashic_discovered_words.json")
        if os.path.exists(words_path):
            try:
                with open(words_path, "r", encoding="utf-8") as f:
                    self.discovered_words = json.load(f)
            except Exception:
                pass

    def record_interaction(
        self, lenses_active: list, ingredients_used: Optional[list] = None
    ):
        if len(lenses_active) >= 2:
            key = cast(Tuple[str, str], tuple(sorted(lenses_active[:2])))
            self.lens_cooccurrence[key] = self.lens_cooccurrence.get(key, 0) + 1
            if self.lens_cooccurrence[key] >= self.HYBRID_LENS_THRESHOLD:
                self._hybridize_lenses(key[0], key[1])
        if ingredients_used:
            for item in ingredients_used:
                self.ingredient_affinity[item] = (
                    self.ingredient_affinity.get(item, 0) + 1
                )

    def track_successful_forge(self, ingredient_name, catalyst_type, result_item):
        if (
            not ingredient_name
            or not catalyst_type
            or (key := (ingredient_name, catalyst_type)) in self.known_recipes
        ):
            return
        self.recipe_candidates.setdefault(key, {})

        if isinstance(result_item, dict):
            result_name = result_item.get(
                "name", result_item.get("description", "Unknown Artifact")
            )
        elif isinstance(result_item, str):
            registry = (self.lore.get("GORDON") or {}).get("ITEM_REGISTRY", {})
            result_name = registry.get(result_item, {}).get("description", result_item)
        else:
            result_name = "Unknown Artifact"

        self.recipe_candidates[key][result_name] = (
            self.recipe_candidates[key].get(result_name, 0) + 1
        )
        if self.recipe_candidates[key][result_name] >= self.RECIPE_THRESHOLD:
            self._crystallize_recipe(ingredient_name, catalyst_type, result_item)

    def _hybridize_lenses(self, lens_a: str, lens_b: str):
        if lens_a == lens_b:
            return
        roots = sorted([lens_a.replace("THE ", ""), lens_b.replace("THE ", "")])
        new_name = f"THE {roots[0]}-{roots[1]}"
        existing_lenses = self.lore.get("LENSES") or {}
        if new_name in existing_lenses:
            return

        def get_weights(l_name):
            data = safe_get(existing_lenses, l_name, {})
            return safe_get(data, "weights", {"v": 0.0, "d": 0.0})

        w_a = get_weights(lens_a)
        w_b = get_weights(lens_b)
        v_a = float(safe_get(w_a, "voltage", safe_get(w_a, "v", 0.0)))
        v_b = float(safe_get(w_b, "voltage", safe_get(w_b, "v", 0.0)))
        d_a = float(safe_get(w_a, "drag", safe_get(w_a, "d", 0.0)))
        d_b = float(safe_get(w_b, "drag", safe_get(w_b, "d", 0.0)))
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
        self.discovered_words[new_name] = "LENS"
        msg = ux("akashic_strings", "paradigm_crystallized")
        print(f"{Prisma.MAG}{msg.format(new_name=new_name)}{Prisma.RST}")
        if self.events:
            self.events.publish("SOUL_MUTATION", {"new_archetype": new_name})

    def _crystallize_recipe(self, ingredient, catalyst, result_item):
        self.known_recipes.add((ingredient, catalyst))
        msg_template = (
            ux("akashic_strings", "recipe_msg")
            or "Forged {result_item} from {ingredient}."
        )
        new_recipe = {
            "ingredient": ingredient,
            "catalyst_category": catalyst,
            "result": result_item,
            "msg": msg_template.format(
                ingredient=ingredient, catalyst=catalyst, result_item=result_item
            ),
        }
        gordon_data = self.lore.get("GORDON") or {}
        current_recipes = gordon_data.get("RECIPES", [])
        if not any(
            r.get("ingredient") == ingredient and r.get("catalyst_category") == catalyst
            for r in current_recipes
        ):
            current_recipes.append(new_recipe)
            gordon_data["RECIPES"] = current_recipes
            self.lore.inject("GORDON", gordon_data)
            msg = ux("akashic_strings", "recipe_recorded")
            print(f"{Prisma.CYN}{msg}{Prisma.RST}")

    def propose_new_category(self, word_list, category_name):
        lexicon_data = self.lore.get("LEXICON") or {}
        target_list = lexicon_data.setdefault(category_name, [])

        new_words = [w for w in word_list if w not in target_list]
        if new_words:
            target_list.extend(new_words)
            for w in new_words:
                self.discovered_words[w] = category_name
            self.lore.inject("LEXICON", lexicon_data)
            msg = ux("akashic_strings", "lexicon_expands")
            print(msg.format(category=category_name.upper()))
            self.save_to_disk("LEXICON", lexicon_data)

    def store_ghost_echo(self, memory_data: Dict):
        self.shadow_stock.append(memory_data)
        if len(self.shadow_stock) > self.MAX_SHADOW_CAPACITY:
            self.shadow_stock = self.shadow_stock[-self.MAX_SHADOW_CAPACITY :]
        self._save_user_state()
        msg = ux("akashic_strings", "ghost_archived")
        print(f"{Prisma.VIOLET}{msg}{Prisma.RST}")

    def register_word(self, word: str, category: str) -> bool:
        if self.discovered_words.get(word) == category:
            return False
        lexicon_data = self.lore.get("LEXICON") or {}
        target_category = lexicon_data.setdefault(category, [])
        if word not in target_category:
            target_category.append(word)
            self.discovered_words[word] = category
            self.lore.inject("LEXICON", lexicon_data)
            msg = ux("akashic_strings", "lexicon_learned")
            print(msg.format(word=word, category=category))
            cfg = getattr(BoneConfig, "AKASHIC", None)
            bloat_limit = getattr(cfg, "BLOAT_THRESHOLD", 50) if cfg else 50
            exempt_categories = getattr(cfg, "BLOAT_EXEMPT_CATEGORIES", ["heavy"])
            if (
                len(lexicon_data[category]) > bloat_limit
                and category not in exempt_categories
            ):
                bloat_msg = ux("akashic_strings", "lexicon_bloat")
                print(bloat_msg.format(category=category))
            return True
        return False
