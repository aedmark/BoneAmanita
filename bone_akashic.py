import json
import os
import uuid
from typing import Dict, Any, Tuple, cast, List, Set
from bone_core import LoreManifest, BoneJSONEncoder
from bone_types import Prisma


class TheAkashicRecord:
    def __init__(self, lore_manifest: "LoreManifest" = None, events_ref=None):
        self.discovered_words: Dict[str, str] = {}
        self.lens_cooccurrence: Dict[Tuple[str, str], int] = {}
        self.ingredient_affinity: Dict[str, int] = {}
        self.known_recipes: Set[Tuple[str, str]] = set()
        self.recipe_candidates: Dict[Tuple[str, str], Dict[str, int]] = {}
        self.RECIPE_THRESHOLD = 3
        self.HYBRID_LENS_THRESHOLD = 5
        self.MAX_SHADOW_CAPACITY = 50
        self.lore = lore_manifest if lore_manifest else LoreManifest.get_instance()
        self.events = events_ref
        self.shadow_stock: List[Dict] = []
        self._load_mythos_state()

    def setup_listeners(self, event_bus):
        event_bus.subscribe("MYTHOLOGY_UPDATE", self._on_mythology_update)
        event_bus.subscribe("LENS_INTERACTION", self._on_lens_interaction)
        event_bus.subscribe("FORGE_SUCCESS", self._on_forge_event)
        event_bus.subscribe("GHOST_SIGNAL", self._on_ghost_signal)
        print(f"{Prisma.CYN}[AKASHIC]: Listening for mythic resonance...{Prisma.RST}")

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
    def _extract_dominant_trigram(physics: Dict) -> str:
        vector = physics.get("vector", {})
        if not vector:
            return "KAN"
        dom = max(vector, key=vector.get)
        mapping = {
            "VEL": "ZHEN",
            "STR": "GEN",
            "CHI": "KAN",
            "ENT": "KAN",
            "PHI": "LI",
            "PSI": "QIAN",
            "BET": "XUN",
            "LAMBDA": "KUN",
            "DEL": "DUI",
        }
        return mapping.get(dom, "KAN")

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
            for resonance in resonances:
                if resonance["trigram"] == trigram:
                    target_lens = resonance.get("lens", resonance.get("soul"))
                    if target_lens == active_lens:
                        if self.events:
                            self.events.publish("RESONANCE_ACHIEVED", {
                                "result": resonance["result"],
                                "msg": resonance["msg"]
                            })

    @staticmethod
    def calculate_manifold_shift(
            theta: str, e: Dict[str, float]
    ) -> Dict[str, float]:
        bias = 0.0
        scalar = 1.0
        theta_upper = theta.upper()
        if "POET" in theta_upper or "HEALER" in theta_upper:
            bias += 2.0
        elif "NIHILIST" in theta_upper or "CRITIC" in theta_upper:
            scalar *= 1.2
        if e.get("HOPE", 0.5) > 0.7:
            scalar *= 0.9
        if e.get("DISCIPLINE", 0.5) > 0.7:
            bias += 1.0
        return {"voltage_bias": bias, "drag_scalar": scalar}

    def _on_ghost_signal(self, payload):
        if payload:
            self.store_ghost_echo(payload)

    def forge_new_item(self, vector: Dict[str, float]) -> Tuple[str, Dict]:
        dominant_force = max(vector, key=vector.get) if vector else "CHI"
        prefixes = {
            "VEL": "Kinetic",
            "STR": "Heavy",
            "CHI": "Cursed",
            "ENT": "Cursed",
            "PHI": "Solar",
            "PSI": "Void",
            "BET": "Paradox",
            "LAMBDA": "Liminal",
            "DEL": "Manic",
        }
        prefix = prefixes.get(dominant_force, "Ascended")
        unique_suffix = str(uuid.uuid4())[:4].upper()
        new_name = f"{prefix.upper()}_ARTIFACT_{int(vector.get(dominant_force, 0) * 10)}_{unique_suffix}"
        hazards = []
        if vector.get("PHI", 0) > 0.5:
            hazards.append("CONDUCTIVE_HAZARD")
        if vector.get("CHI", 0) > 0.5:
            hazards.append("TOXIC_HAZARD")
        new_data = {
            "name": new_name,
            "description": f"A vibrating artifact humming with {dominant_force} energy.",
            "function": "ARTIFACT",
            "passive_traits": hazards,
            "value": 50.0,
        }
        gordon_data = self.lore.get("GORDON") or {}
        registry = gordon_data.get("ITEM_REGISTRY", {})
        registry[new_name] = new_data
        self.lore.inject("GORDON", {"ITEM_REGISTRY": registry})
        return new_name, new_data

    def save_all(self):
        self.save_to_disk("discovered_words", self.discovered_words)
        self._save_user_state()
        print(f"{Prisma.GRY}[AKASHIC]: Mythos persisted.{Prisma.RST}")

    def _save_user_state(self):
        state = {
            "lens_cooccurrence": {
                f"{k[0]}|{k[1]}": v for k, v in self.lens_cooccurrence.items()
            },
            "ingredient_affinity": self.ingredient_affinity,
            "shadow_stock": self.shadow_stock,
        }
        if not os.path.exists("saves"):
            os.makedirs("saves")
        try:
            with open("saves/akashic_state.json", "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"{Prisma.RED}[AKASHIC] Save failed: {e}{Prisma.RST}")

    def save_to_disk(self, category: str, data: Any):
        directory = getattr(self.lore, "DATA_DIR", "lore")
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                print(
                    f"{Prisma.RED}[AKASHIC]: Failed to create '{directory}' directory: {e}{Prisma.RST}"
                )
                return
        filename = f"akashic_{category}.json"
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, cls=BoneJSONEncoder)
            print(f"{Prisma.GRY}[AKASHIC]: Saved {category}.{Prisma.RST}")
        except Exception as e:
            print(f"{Prisma.RED}[AKASHIC]: Save Failed ({category}): {e}{Prisma.RST}")

    def _load_mythos_state(self):
        data = {}
        if os.path.exists("saves/akashic_state.json"):
            try:
                with open("saves/akashic_state.json", "r") as f:
                    data = json.load(f)
            except:
                pass
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

    def record_interaction(self, lenses_active: list, ingredients_used: list = None):
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
                "name", result_item.get("description", "Unknown Artifact")
            )
        elif isinstance(result_item, str):
            gordon_data = self.lore.get("GORDON") or {}
            registry = gordon_data.get("ITEM_REGISTRY", {})
            if result_item in registry:
                result_name = registry[result_item].get("description", result_item)
            else:
                result_name = result_item
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
            return existing_lenses.get(l_name, {}).get("weights", {"v": 0, "d": 0})

        w_a = get_weights(lens_a)
        w_b = get_weights(lens_b)
        new_weights = {
            "voltage": round(
                (
                    w_a.get("voltage", w_a.get("v", 0))
                    + w_b.get("voltage", w_b.get("v", 0))
                )
                / 2,
                2,
            ),
            "drag": round(
                (w_a.get("drag", w_a.get("d", 0)) + w_b.get("drag", w_b.get("d", 0)))
                / 2,
                2,
            ),
        }
        new_lens_data = {
            "description": f"A syncretic fusion of {lens_a} and {lens_b}.",
            "weights": new_weights,
            "parentage": [lens_a, lens_b],
        }
        self.lore.inject("LENSES", {new_name: new_lens_data})
        self.discovered_words[new_name] = "LENS"
        print(
            f"{Prisma.MAG}🔮 AKASHIC: A new paradigm has crystallized: {new_name}{Prisma.RST}"
        )

    def _crystallize_recipe(self, ingredient, catalyst, result_item):
        self.known_recipes.add((ingredient, catalyst))
        new_recipe = {
            "ingredient": ingredient,
            "catalyst_category": catalyst,
            "result": result_item,
            "msg": f"The {ingredient} resonates with {catalyst} energy, transforming into {result_item}.",
        }
        current_recipes = (self.lore.get("GORDON") or {}).get("RECIPES", [])
        if not any(
            r["ingredient"] == ingredient and r["catalyst_category"] == catalyst
            for r in current_recipes
        ):
            current_recipes.append(new_recipe)
            self.lore.inject("GORDON", {"RECIPES": current_recipes})
            print(
                f"{Prisma.CYN}📜 AKASHIC: Recipe recorded in the Great Book.{Prisma.RST}"
            )

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
            print(
                f"✨ MYTHOLOGY ENGINE: The Lexicon expands. New Category: '{category_name.upper()}'"
            )
            self.save_to_disk("LEXICON", lexicon_data)

    def store_ghost_echo(self, memory_data: Dict):
        self.shadow_stock.append(memory_data)
        if len(self.shadow_stock) > self.MAX_SHADOW_CAPACITY:
            self.shadow_stock.pop(0)
        self._save_user_state()
        print(f"{Prisma.VIOLET}[AKASHIC]: Ghost Echo archived.{Prisma.RST}")

    def register_word(self, word: str, category: str) -> bool:
        if word in self.discovered_words:
            if self.discovered_words[word] == category:
                return False
        lexicon_data = self.lore.get("LEXICON") or {}
        target_category = lexicon_data.setdefault(category, [])
        if word not in target_category:
            target_category.append(word)
            self.discovered_words[word] = category
            self.lore.inject("LEXICON", lexicon_data)
            print(f"✨ LEXICON: Learned '{word}' ({category})")
            if len(lexicon_data[category]) > 50 and category != "heavy":
                print(
                    f"⚠️ MYTHOLOGY ENGINE: Category '{category}' is bloating. Suggest fission."
                )
            return True
        return False
