""" bone_akashic.py - The Self-Writing Myth """
import json
import os
import random
from typing import Dict, Any, Tuple, cast, List
from bone_core import Prisma, TheLore, LoreManifest

class TheAkashicRecord:
    def __init__(self):
        self.discovered_words: Dict[str, str] = {}
        self.forged_items: Dict[str, Any] = {}
        self.recipe_candidates: Dict[Tuple[str, str], Dict[str, int]] = {}
        self.lens_cooccurrence: Dict[Tuple[str, str], int] = {}
        self.ingredient_affinity: Dict[str, int] = {}
        self.style_drift = {"chaos_score": 0.0, "rigidity_score": 0.0}
        self.RECIPE_THRESHOLD = 3
        self.HYBRID_LENS_THRESHOLD = 5
        self.lore = TheLore
        self.shadow_stock: List[Dict] = []
        self.MAX_SHADOW_CAPACITY = 50
        self._load_mythos_state()

    def setup_listeners(self, event_bus):
        event_bus.subscribe("MYTHOLOGY_UPDATE", self._on_mythology_update)
        event_bus.subscribe("LENS_INTERACTION", self._on_lens_interaction)
        event_bus.subscribe("FORGE_SUCCESS", self._on_forge_event)
        print(f"{Prisma.CYN}[AKASHIC]: Listening for mythic resonance...{Prisma.RST}")

    def _on_lens_interaction(self, payload):
        lenses = payload.get("lenses", [])
        if lenses:
            self.record_interaction(lenses)

    def _on_forge_event(self, payload):
        self.track_successful_forge(
            payload.get("ingredient"),
            payload.get("catalyst"),
            payload.get("result"))

    def _on_mythology_update(self, payload):
        if not payload or not isinstance(payload, dict): return
        word = payload.get("word")
        category = payload.get("category")
        if word and category:
            self.register_word(word, category)

    def save_all(self):
        mythos_data = {
            "lens_cooccurrence": {f"{k[0]}|{k[1]}": v for k, v in self.lens_cooccurrence.items()},
            "ingredient_affinity": self.ingredient_affinity,
            "shadow_stock": self.shadow_stock}
        self.save_to_disk("MYTHOS", mythos_data)
        print(f"{Prisma.CYN}[AKASHIC]: Mythos state preserved.{Prisma.RST}")

    def save_to_disk(self, category: str, data: Any):
        directory = LoreManifest.DATA_DIR
        filename = f"{category.lower()}.json"
        path = os.path.join(directory, filename)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"{Prisma.GRN}[AKASHIC]: {category} updated on disk.{Prisma.RST}")
            self.lore.inject(category, data)
        except Exception as e:
            print(f"{Prisma.RED}[AKASHIC]: Failed to write {filename}: {e}{Prisma.RST}")

    def _load_mythos_state(self):
        data = self.lore.get("MYTHOS")
        if not data: return
        raw_cooc = data.get("lens_cooccurrence", {})
        for k, v in raw_cooc.items():
            if "|" in k:
                parts = k.split("|")
                self.lens_cooccurrence[(parts[0], parts[1])] = v
        self.ingredient_affinity = data.get("ingredient_affinity", {})
        self.shadow_stock = data.get("shadow_stock", [])

    def record_interaction(self, lenses_active: list, ingredients_used: list = None):
        if len(lenses_active) >= 2:
            key = cast(Tuple[str, str], tuple(sorted(lenses_active[:2])))
            self.lens_cooccurrence[key] = self.lens_cooccurrence.get(key, 0) + 1
            if self.lens_cooccurrence[key] >= self.HYBRID_LENS_THRESHOLD:
                self._hybridize_lenses(key[0], key[1])
        if ingredients_used:
            for item in ingredients_used:
                self.ingredient_affinity[item] = self.ingredient_affinity.get(item, 0) + 1

    def track_successful_forge(self, ingredient_name, catalyst_type, result_item):
        key = (ingredient_name, catalyst_type)
        if key not in self.recipe_candidates:
            self.recipe_candidates[key] = {}
        result_name = "Unknown Artifact"
        if isinstance(result_item, dict):
            result_name = result_item.get("description", "Unknown Artifact")
        elif isinstance(result_item, str):
            gordon_data = self.lore.get("GORDON") or {}
            registry = gordon_data.get("ITEM_REGISTRY", {})
            if result_item in registry:
                result_name = registry[result_item].get("description", result_item)
            else:
                result_name = result_item
        self.recipe_candidates[key][result_name] = self.recipe_candidates[key].get(result_name, 0) + 1
        if self.recipe_candidates[key][result_name] >= self.RECIPE_THRESHOLD:
            self._crystallize_recipe(ingredient_name, catalyst_type, result_item)

    def _hybridize_lenses(self, lens_a, lens_b):
        new_key = f"{lens_a}_{lens_b}_HYBRID"
        lenses_data = self.lore.get("LENSES")
        if new_key in lenses_data: return
        role_a = lenses_data.get(lens_a, {}).get("role", "Observer")
        role_b = lenses_data.get(lens_b, {}).get("role", "Participant")
        new_lens = {
            "role": f"The {role_a} / {role_b} Synthesis",
            "msg": f"Perspective shift: {lens_a} and {lens_b} are aligning. The dialectic is resolved.",
            "derived_from": [lens_a, lens_b]}
        print(f"✨ MYTHOLOGY ENGINE: A new lens has formed: {new_key}")
        lenses_data[new_key] = new_lens
        self.save_to_disk("LENSES", lenses_data)
        self.lens_cooccurrence[(lens_a, lens_b)] = 0

    def _crystallize_recipe(self, ingredient, catalyst, result_item):
        gordon_data = self.lore.get("GORDON")
        if not gordon_data: return
        current_recipes = gordon_data.get("RECIPES", [])
        for r in current_recipes:
            if r.get("ingredient") == ingredient and r.get("catalyst_category") == catalyst:
                return
        new_recipe = {
            "ingredient": ingredient,
            "catalyst_category": catalyst,
            "result": "CUSTOM_ARTIFACT",
            "msg": "The universe remembers this combination. It is now Law.",
            "dynamic_result": result_item}
        current_recipes.append(new_recipe)
        print(f"✨ MYTHOLOGY ENGINE: A new recipe has been codified: {ingredient} + {catalyst}")
        gordon_data["RECIPES"] = current_recipes
        self.save_to_disk("GORDON", gordon_data)

    def propose_new_category(self, word_list, category_name):
        lexicon_data = self.lore.get("LEXICON")
        if category_name not in lexicon_data:
            lexicon_data[category_name] = []
        updated = False
        for w in word_list:
            if w not in lexicon_data[category_name]:
                lexicon_data[category_name].append(w)
                self.discovered_words[w] = category_name
                updated = True
        if updated:
            print(f"✨ MYTHOLOGY ENGINE: The Lexicon expands. New Category: '{category_name.upper()}'")
            self.save_to_disk("LEXICON", lexicon_data)

    @staticmethod
    def forge_new_item(vector_data, ITEM_GENERATION=None):
        dominant = max(vector_data, key=vector_data.get)
        if dominant not in ITEM_GENERATION["PREFIXES"]: dominant = "void"
        prefix = random.choice(ITEM_GENERATION["PREFIXES"].get(dominant, ["Strange"]))
        base_type = random.choice(list(ITEM_GENERATION["BASES"].keys()))
        base_name = random.choice(ITEM_GENERATION["BASES"][base_type])
        suffix = random.choice(ITEM_GENERATION["SUFFIXES"].get(dominant, ["of Mystery"]))
        name = f"{prefix.upper()} {base_name.upper()} {suffix.upper()}"
        value = vector_data[dominant] * 10.0
        description = f"A procedurally generated artifact. It vibrates with {dominant} energy."
        new_item = {
            "description": description,
            "function": "ARTIFACT",
            "passive_traits": [f"{dominant.upper()}_RESONANCE"],
            "value": round(value, 2),
            "usage_msg": f"You use the {name}. The air ripples with {dominant} force."}
        return name, new_item

    def store_ghost_echo(self, memory_data: Dict):
        self.shadow_stock.append(memory_data)
        if len(self.shadow_stock) > self.MAX_SHADOW_CAPACITY:
            self.shadow_stock.pop(0)
        self.save_all()
        print(f"{Prisma.VIOLET}[AKASHIC]: Ghost Echo archived: '{memory_data.get('lesson')}'{Prisma.RST}")

    def calculate_manifold_shift(self, theta: str, e: Dict[str, float]) -> Dict[str, float]:
        delta = {"voltage_bias": 0.0, "drag_scalar": 1.0}
        archetype_bias = {
            "THE POET": {"v": 2.0, "d": 0.8},
            "THE ENGINEER": {"v": -1.0, "d": 1.2},
            "THE NIHILIST": {"v": -5.0, "d": 2.0},
            "THE MANIC": {"v": 10.0, "d": 0.5},
            "THE OBSERVER": {"v": 0.0, "d": 1.0},
            "THE CRITIC": {"v": -2.0, "d": 1.5}}
        base = archetype_bias.get(theta, archetype_bias["THE OBSERVER"])
        tension = e.get("DISCIPLINE", 0.5)
        vitality = e.get("HOPE", 0.5)
        lambda_val = (1.0 + tension) * vitality
        delta["voltage_bias"] = base["v"] * lambda_val
        flow_state = (e.get("CURIOSITY", 0.5) + vitality) / 2.0
        delta["drag_scalar"] = base["d"] * (1.5 - flow_state)
        return delta

    def register_word(self, word, category):
        lexicon_data = self.lore.get("LEXICON")
        if category in lexicon_data:
            if word not in lexicon_data[category]:
                lexicon_data[category].append(word)
                self.discovered_words[word] = category
                print(f"✨ LEXICON: Learned '{word}' ({category})")
                self.save_to_disk("LEXICON", lexicon_data)
                if len(lexicon_data[category]) > 50 and category != "heavy":
                    print(f"⚠️ MYTHOLOGY ENGINE: Category '{category}' is bloating. Suggest fission.")
                return True
        return False