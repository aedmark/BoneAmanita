""" bone_akashic.py"""

import json
import os
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple, cast

from bone_config import BoneConfig
from bone_core import BoneJSONEncoder, LoreManifest, ux
from bone_types import Prisma

class TheAkashicRecord:
    """
    The master repository for long-term, structural memory. 
    It tracks newly learned words, the synthesis of new archetypes, and the location of scars. 
    It writes this data to disk, ensuring the lattice persists between sessions.
    """
    def __init__(self, lore_manifest: Optional["LoreManifest"] = None, events_ref=None):
        self.discovered_words: Dict[str, str] = {}
        self.lens_cooccurrence: Dict[Tuple[str, str], int] = {}
        self.ingredient_affinity: Dict[str, int] = {}
        self.known_recipes: Set[Tuple[str, str]] = set()
        self.recipe_candidates: Dict[Tuple[str, str], Dict[str, int]] = {}
        cfg = getattr(BoneConfig, "AKASHIC", None)
        self.RECIPE_THRESHOLD = getattr(cfg, "RECIPE_THRESHOLD", 3) if cfg else 3
        self.HYBRID_LENS_THRESHOLD = getattr(cfg, "HYBRID_LENS_THRESHOLD", 5) if cfg else 5
        self.MAX_SHADOW_CAPACITY = getattr(cfg, "MAX_SHADOW_CAPACITY", 50) if cfg else 50
        self.lore = lore_manifest if lore_manifest else LoreManifest.get_instance()
        self.events = events_ref
        # The physical storage arrays for the organism's mental life.
        self.shadow_stock: List[Dict] = []
        self.subconscious_strata: List[Dict] = []
        self.scar_map: List[Dict] = []
        self._load_mythos_state()

    def setup_listeners(self, event_bus):
        """Subscribes to the EventBus to passively observe and record systemic shifts."""
        event_bus.subscribe("MYTHOLOGY_UPDATE", self._on_mythology_update)
        event_bus.subscribe("LENS_INTERACTION", self._on_lens_interaction)
        event_bus.subscribe("FORGE_SUCCESS", self._on_forge_event)
        event_bus.subscribe("GHOST_SIGNAL", self._on_ghost_signal)
        msg = ux("akashic_strings", "listening")
        print(f"{Prisma.CYN}{msg}{Prisma.RST}")

    def trigger_autophagy(self) -> Tuple[float, str]:
        """
        The ultimate survival loop. When ATP is zero, the organism 
        permanently deletes a node from its subconscious strata (or a learned word) 
        to generate a burst of metabolic fuel.
        """
        cfg = getattr(BoneConfig, "AKASHIC", None)
        yield_val = getattr(cfg, "AUTOPHAGY_YIELD", 15.0) if cfg else 15.0
        if not self.subconscious_strata:
            if self.discovered_words:
                word = next(iter(self.discovered_words))
                del self.discovered_words[word]
                msg = ux("akashic_strings", "autophagy_lexical")
                return yield_val, msg.format(word=word)
            msg = ux("akashic_strings", "autophagy_failed")
            return 0.0, msg
        consumed_node = self.subconscious_strata.pop(0)
        target = consumed_node.get("concept", "Unknown Node")
        msg = ux("akashic_strings", "autophagy_memory")
        return yield_val, msg.format(target=target)

    def record_scar(self, concept: str, p: Any):
        """When the system suffers a paradox or logic collapse, it records the structural coordinates (E, beta, S, etc.)."""
        cfg = getattr(BoneConfig, "AKASHIC", None)
        default_coords = getattr(cfg, "DEFAULT_SCAR_COORDS", {
            "E": 0.2, "beta": 0.4, "S": 0.3, "D": 0.3, "C": 0.2,
            "T": 0.0, "psi": 0.0, "chi": 0.0, "valence": 0.0, "ROS": 0.0})
        coords = {k: getattr(p, k, v) for k, v in default_coords.items()}
        scar = {"concept": concept, "coordinates": coords, "gilded": True}
        self.scar_map.append(scar)
        # Leaves a ghost in the coordinates so future traversal knows something broke here.
        self.store_ghost_echo({"type": "SCAR_GHOST", "concept": concept, "coords": coords})
        if self.events:
            msg = ux("akashic_strings", "mercy_scar")
            self.events.log(f"{Prisma.OCHRE}{msg.format(concept=concept)}{Prisma.RST}", "VILLAGE")

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
            payload.get("ingredient"), payload.get("catalyst"), payload.get("result"))

    @staticmethod
    def _extract_dominant_trigram(physics: Dict) -> str:
        """Maps the dominant numeric physics vector to its corresponding I-Ching Trigram."""
        vector = physics.get("vector", {})
        if not vector:
            return "KAN"
        dom = max(vector, key=vector.get)
        constants = LoreManifest.get_instance().get("PHYSICS_CONSTANTS") or {}
        trigrams = constants.get("TRIGRAM_MAP", {})
        fallback_mapping = constants.get("FALLBACK_TRIGRAMS", {"CHI": "KAN", "LAMBDA": "KUN"})
        fallback_default = constants.get("FALLBACK_DEFAULT", "KAN")
        if dom in trigrams and len(trigrams[dom]) > 1:
            return trigrams[dom][1]
        return fallback_mapping.get(dom, fallback_default)

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
            lenses_data = self.lore.get("LENSES") or {}
            resonances = lenses_data.get("_META_RESONANCE_", [])
            # If the mathematical physics perfectly align with the current archetype, it triggers a Resonance event.
            for resonance in resonances:
                if resonance["trigram"] == trigram:
                    target_lens = resonance.get("lens", resonance.get("soul"))
                    if target_lens == active_lens:
                        if self.events:
                            self.events.publish("RESONANCE_ACHIEVED",{"result": resonance["result"],"msg": resonance["msg"],},)

    @staticmethod
    def calculate_manifold_shift(theta: str, e: Dict[str, float]) -> Dict[str, float]:
        """Calculates how much the current word (theta) biases the structural narrative drag and voltage."""
        bias = 0.0
        scalar = 1.0
        theta_upper = theta.upper()
        constants = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "MANIFOLD_SHIFTS") or {}
        for word, b_val in constants.get("BIAS_LENSES", {}).items():
            if word in theta_upper:
                bias += b_val
        for word, s_val in constants.get("SCALAR_LENSES", {}).items():
            if word in theta_upper:
                scalar *= s_val
        for key, params in constants.get("VECTOR_THRESHOLDS", {}).items():
            if e.get(key, 0.5) > params.get("threshold", 0.7):
                scalar *= params.get("scalar_mod", 1.0)
                bias += params.get("bias_mod", 0.0)
        return {"voltage_bias": bias, "drag_scalar": scalar}

    def _on_ghost_signal(self, payload):
        if payload:
            self.store_ghost_echo(payload)

    def forge_new_item(self, vector: Dict[str, float]) -> Tuple[str, Dict]:
        """Procedurally generates a new item based on the current physics vector and injects it into Gordon's registry."""
        dominant_force = max(vector, key=vector.__getitem__) if vector else "CHI"
        item_gen_data = self.lore.get("ITEM_GENERATION") or {}
        prefixes = item_gen_data.get("PREFIXES", {})
        prefix = prefixes.get(dominant_force, item_gen_data.get("FALLBACK_PREFIX", "Ascended"))
        unique_suffix = str(uuid.uuid4())[:4].upper()
        new_name = f"{prefix.upper()}_ARTIFACT_{int(vector.get(dominant_force, 0) * 10)}_{unique_suffix}"
        hazards = []
        hazard_thresholds = item_gen_data.get("HAZARD_THRESHOLDS", {})
        for force, threshold_data in hazard_thresholds.items():
            if vector.get(force, 0) > threshold_data.get("threshold", 0.5):
                hazards.append(threshold_data.get("hazard_name"))
        desc_template = ux("akashic_strings", "artifact_desc")
        cfg = getattr(BoneConfig, "AKASHIC", None)
        artifact_val = getattr(cfg, "ARTIFACT_VALUE", 50.0) if cfg else 50.0
        new_data = {"name": new_name, "description": desc_template.format(dominant_force=dominant_force),
                    "function": "ARTIFACT", "passive_traits": hazards, "value": artifact_val, }
        gordon_data = self.lore.get("GORDON") or {}
        registry = gordon_data.get("ITEM_REGISTRY", {})
        registry[new_name] = new_data
        self.lore.inject("GORDON", {"ITEM_REGISTRY": registry})
        return new_name, new_data

    def save_all(self):
        self.save_to_disk("discovered_words", self.discovered_words)
        self._save_user_state()
        msg = ux("akashic_strings", "mythos_persisted")
        print(f"{Prisma.GRY}{msg}{Prisma.RST}")

    def _save_user_state(self):
        state = {"lens_cooccurrence": {
            f"{k[0]}|{k[1]}": v for k, v in self.lens_cooccurrence.items()},
            "ingredient_affinity": self.ingredient_affinity, "shadow_stock": self.shadow_stock,
            "subconscious_strata": self.subconscious_strata, "scar_map": self.scar_map, }
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
                print(f"{Prisma.RED}{msg.format(directory=directory, error=e)}{Prisma.RST}")
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
                with open(save_path, "r") as f:
                    data = json.load(f)
            except Exception as e:
                msg = ux("akashic_strings", "state_load_failed")
                print(f"{Prisma.RED}{msg.format(error=e)}{Prisma.RST}")
        if not data:
            data = self.lore.get("MYTHOS")
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

    def record_interaction(
            self, lenses_active: list, ingredients_used: Optional[list] = None):
        """A reinforcing feedback loop. If two archetypes speak together enough, they merge into a hybrid."""
        if len(lenses_active) >= 2:
            key = cast(Tuple[str, str], tuple(sorted(lenses_active[:2])))
            self.lens_cooccurrence[key] = self.lens_cooccurrence.get(key, 0) + 1
            if self.lens_cooccurrence[key] >= self.HYBRID_LENS_THRESHOLD:
                self._hybridize_lenses(key[0], key[1])
        if ingredients_used:
            for item in ingredients_used:
                self.ingredient_affinity[item] = (
                        self.ingredient_affinity.get(item, 0) + 1)

    def track_successful_forge(self, ingredient_name, catalyst_type, result_item):
        if not ingredient_name or not catalyst_type:
            return
        if (ingredient_name, catalyst_type) in self.known_recipes:
            return

        key = (ingredient_name, catalyst_type)
        if key not in self.recipe_candidates:
            self.recipe_candidates[key] = {}
        result_name = "Unknown Artifact"
        if isinstance(result_item, dict):
            result_name = result_item.get(
                "name", result_item.get("description", "Unknown Artifact"))
        elif isinstance(result_item, str):
            gordon_data = self.lore.get("GORDON") or {}
            registry = gordon_data.get("ITEM_REGISTRY", {})
            if result_item in registry:
                result_name = registry[result_item].get("description", result_item)
            else:
                result_name = result_item
        self.recipe_candidates[key][result_name] = (
                self.recipe_candidates[key].get(result_name, 0) + 1)
        if self.recipe_candidates[key][result_name] >= self.RECIPE_THRESHOLD:
            self._crystallize_recipe(ingredient_name, catalyst_type, result_item)

    def _hybridize_lenses(self, lens_a: str, lens_b: str):
        """Averages the physical weights of two archetypes to create a stable, new structural node."""
        if lens_a == lens_b:
            return
        roots = sorted([lens_a.replace("THE ", ""), lens_b.replace("THE ", "")])
        new_name = f"THE {roots[0]}-{roots[1]}"
        existing_lenses = self.lore.get("LENSES") or {}
        if new_name in existing_lenses:
            return

        def get_weights(l_name):
            return existing_lenses.get(l_name, {}).get("weights", {"v": 0, "d": 0})

        w_a = get_weights(lens_a)
        w_b = get_weights(lens_b)
        new_weights = {"voltage": round((w_a.get("voltage", w_a.get("v", 0)) + w_b.get("voltage", w_b.get("v", 0))) / 2, 2, ),
                       "drag": round((w_a.get("drag", w_a.get("d", 0)) + w_b.get("drag", w_b.get("d", 0)))/ 2,2,),}
        desc_template = ux("akashic_strings", "lens_desc")
        new_lens_data = {"description": desc_template.format(lens_a=lens_a, lens_b=lens_b), "weights": new_weights,
                         "parentage": [lens_a, lens_b], }
        self.lore.inject("LENSES", {new_name: new_lens_data})
        self.discovered_words[new_name] = "LENS"
        msg = ux("akashic_strings", "paradigm_crystallized")
        print(f"{Prisma.MAG}{msg.format(new_name=new_name)}{Prisma.RST}")
        if self.events:
            self.events.publish("SOUL_MUTATION", {"new_archetype": new_name})

    def _crystallize_recipe(self, ingredient, catalyst, result_item):
        """Once a crafting interaction has occurred enough times, it is permanently added to the known lore."""
        self.known_recipes.add((ingredient, catalyst))
        msg_template = ux("akashic_strings", "recipe_msg")
        new_recipe = {"ingredient": ingredient, "catalyst_category": catalyst, "result": result_item,
                      "msg": msg_template.format(ingredient=ingredient, catalyst=catalyst, result_item=result_item), }
        current_recipes = (self.lore.get("GORDON") or {}).get("RECIPES", [])
        if not any(
                r["ingredient"] == ingredient and r["catalyst_category"] == catalyst
                for r in current_recipes):
            current_recipes.append(new_recipe)
            self.lore.inject("GORDON", {"RECIPES": current_recipes})
            msg = ux("akashic_strings", "recipe_recorded")
            print(f"{Prisma.CYN}{msg}{Prisma.RST}")

    def propose_new_category(self, word_list, category_name):
        lexicon_data = self.lore.get("LEXICON") or {}
        if category_name not in lexicon_data:
            lexicon_data[category_name] = []
        updated = False
        for w in word_list:
            if w not in lexicon_data[category_name]:
                lexicon_data[category_name].append(w)
                self.discovered_words[w] = category_name
                updated = True
        if updated:
            self.lore.inject("LEXICON", lexicon_data)
            msg = ux("akashic_strings", "lexicon_expands")
            print(msg.format(category=category_name.upper()))
            self.save_to_disk("LEXICON", lexicon_data)

    def store_ghost_echo(self, memory_data: Dict):
        self.shadow_stock.append(memory_data)
        if len(self.shadow_stock) > self.MAX_SHADOW_CAPACITY:
            self.shadow_stock.pop(0)
        self._save_user_state()
        msg = ux("akashic_strings", "ghost_archived")
        print(f"{Prisma.VIOLET}{msg}{Prisma.RST}")

    def register_word(self, word: str, category: str) -> bool:
        """The literal act of learning. Dynamically expanding the semantic boundary of the system."""
        if word in self.discovered_words:
            if self.discovered_words[word] == category:
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
            # Too many words without meaning causes 'bloat'. The system warns the user of its own cognitive load.
            if len(lexicon_data[category]) > bloat_limit and category not in exempt_categories:
                bloat_msg = ux("akashic_strings", "lexicon_bloat")
                print(bloat_msg.format(category=category))
            return True
        return False