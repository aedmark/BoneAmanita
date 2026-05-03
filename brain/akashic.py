"""
akashic.py

The Persistent Epigenetic Layer.
This module handles long-term, cross-session memory. It writes biological
and structural changes to disk via JSON files so the LLM remembers its
"Scars" (failures) and "Glimmers" (successes) the next time it boots up.
It also dynamically evolves the system's vocabulary and archetypal voices across sessions.
"""

import json, os, uuid
from typing import Any, Dict, List, Optional, Set, Tuple, cast
from core import BoneJSONEncoder, LoreManifest
from struts import ux, safe_get
from presets import BoneConfig
from constants import Prisma

class TheAkashicRecord:
    """
    The DNA Hard Drive of the Hypervisor.
    Manages the long-term evolution of the LLM by tracking which words it uses,
    which archetypes work well together, and which architectural boundaries
    caused previous system failures.
    """
    def __init__(self, lore_manifest: Optional["LoreManifest"] = None, events_ref=None):
        self.discovered_words: Dict[str, str] = {}
        self.lens_cooccurrence: Dict[Tuple[str, str], int] = {}
        self.ingredient_affinity: Dict[str, int] = {}
        self.known_recipes: Set[Tuple[str, str]] = set()
        self.recipe_candidates: Dict[Tuple[str, str], Dict[str, int]] = {}

        self.cfg_akashic = getattr(BoneConfig, "AKASHIC", object())
        self.RECIPE_THRESHOLD = getattr(self.cfg_akashic, "RECIPE_THRESHOLD", 3)
        self.HYBRID_LENS_THRESHOLD = getattr(self.cfg_akashic, "HYBRID_LENS_THRESHOLD", 5)
        self.MAX_SHADOW_CAPACITY = getattr(self.cfg_akashic, "MAX_SHADOW_CAPACITY", 50)

        self.lore = lore_manifest if lore_manifest else LoreManifest.get_instance()
        self.events = events_ref

        # Persistence Configuration
        self.save_dir = getattr(self.cfg_akashic, "SAVE_DIR", "saves")
        self.state_path = os.path.join(self.save_dir, getattr(self.cfg_akashic, "STATE_FILE", "akashic_state.json"))
        self.data_dir = getattr(self.lore, "DATA_DIR", "lore")

        # Deep Substrate Memory Arrays
        self.shadow_stock: List[Dict] = []
        self.subconscious_strata: List[Dict] = []
        self.scar_map: List[Dict] = []

        self._load_mythos_state()

    def setup_listeners(self, event_bus):
        """Connects the Akashic Record to the global event bus to passively observe the system."""
        event_bus.subscribe("MYTHOLOGY_UPDATE", self._on_mythology_update)
        event_bus.subscribe("LENS_INTERACTION", self._on_lens_interaction)
        event_bus.subscribe("FORGE_SUCCESS", self._on_forge_event)
        event_bus.subscribe("GHOST_SIGNAL", self._on_ghost_signal)
        event_bus.subscribe("SYSTEM_STARVING", self._on_system_starving)
        if msg := ux("akashic_strings", "listening"):
            print(f"{Prisma.GRY}{msg}{Prisma.RST}")

    def _on_system_starving(self, _payload):
        """Emergency interrupt when ATP hits 0."""
        yield_val, msg = self.trigger_autophagy()
        if msg:
            print(f"{Prisma.CYN}{msg}{Prisma.RST}")

    def trigger_autophagy(self) -> Tuple[float, str]:
        """
        The survival mechanism.
        If the LLM is starving (out of ATP) but forced to process a prompt,
        it physically consumes its own long-term memories or acquired vocabulary,
        converting the semantic mass back into raw energy to survive the turn.
        """
        akashic_cfg = getattr(BoneConfig, "AKASHIC", None)
        bio_cfg = getattr(BoneConfig, "BIO", None)

        if self.subconscious_strata:
            # Consume the oldest buried memory
            victim_data = self.subconscious_strata.pop(0)
            target = victim_data.get("concept", "Unknown Node")
            mass = victim_data.get("data", {}).get("mass", 1.0)

            # Dynamic yield based on the density of the memory consumed
            yield_val = min(50.0, 10.0 + (mass * 2.5))

            # Epigenetic benefit: digesting a memory makes the system better at digesting in the future
            if bio_cfg and hasattr(bio_cfg, "DEPTH_TAX_MULT"):
                bio_cfg.DEPTH_TAX_MULT = max(0.5, bio_cfg.DEPTH_TAX_MULT - 0.02)

            msg = f"Autophagy complete. Composted '{target}' (Mass: {mass:.1f}). Recovered {yield_val:.1f} ATP. Synaptic efficiency improved."

        elif self.discovered_words:
            # If no memories are left, consume the vocabulary we learned
            target = next(iter(self.discovered_words))
            del self.discovered_words[target]
            yield_val = getattr(akashic_cfg, "AUTOPHAGY_YIELD", 15.0)
            msg_template = ux("akashic_strings", "autophagy_lexical") or "Lexical purge: consumed {target}."
            msg = msg_template.format(target=target, word=target)

        else:
            return 0.0, ux("akashic_strings", "autophagy_failed") or "Starvation threshold. No matter left to consume."

        if self.events:
            self.events.publish("AUTOPHAGY_EVENT", {"node": target, "atp_gained": yield_val})

        return yield_val, msg

    def record_scar(self, concept: str, p: Any):
        """
        Trauma mapping.
        When the system experiences a structural collapse or massive logic failure,
        it logs the exact physical/dimensional coordinates (Voltage, Entropy, Beta) of the failure.
        It then permanently injects an 'Avoidance Axiom' into the LLM's system prompt.
        """
        cfg = getattr(BoneConfig, "AKASHIC", object())
        cfg_defaults = getattr(cfg, "DEFAULT_SCAR_COORDS", {})
        axis_map = {
            "E": ("exhaustion", 0.2), "beta": ("beta_index", 0.4), "S": ("scope", 0.3),
            "D": ("depth", 0.3), "C": ("connectivity", 0.2), "T": ("trauma", 0.0),
            "psi": ("psi", 0.0), "chi": ("entropy", 0.0), "valence": ("valence", 0.0), "ROS": ("ros", 0.0)
        }
        coords = {}
        energy_layer = safe_get(p, "energy") or {}

        # Extract the exact coordinates of the failure
        for short_key, (full_key, default_val) in axis_map.items():
            val = safe_get(p, short_key)
            coords[short_key] = val if val is not None else safe_get(energy_layer, full_key, cfg_defaults.get(short_key, default_val))

        self.scar_map.append({"concept": concept, "coordinates": coords.copy(), "gilded": True})
        max_scars = getattr(self.cfg_akashic, "MAX_SCARS", 50)
        if len(self.scar_map) > max_scars:
            self.scar_map.pop(0)

        # Leave a 'ghost' in the machine to warn future processes
        self.store_ghost_echo({"type": "SCAR_GHOST", "concept": concept, "coords": coords.copy()})
        self._save_user_state()
        self._mutate_system_prompts(concept, coords)

        if self.events:
            msg = ux("akashic_strings", "mercy_scar")
            self.events.log(f"{Prisma.OCHRE}{msg.format(concept=concept)}{Prisma.RST}","VILLAGE")
            self.events.publish("SCAR_RECORDED", {"concept": concept, "coords": coords})

    def record_glimmer(self, concept: str, paradigm: str):
        """
        Crystallizes a successful interaction pattern into a permanent structural boon.
        The opposite of a scar. Hardcodes a successful behavior into the base prompt.
        """
        try:
            prompts = self.lore.get("SYSTEM_PROMPTS") or {}
            epigenetic_list = prompts.setdefault("GLOBAL_BASELINE", {}).setdefault("EPIGENETIC_BOONS", [])

            axiom = f"STRUCTURAL SUCCESS [{concept.upper()}]: The system achieved deep resonance using this paradigm: '{paradigm}'. Prioritize this geometry in future calculations."

            if axiom not in epigenetic_list:
                epigenetic_list.append(axiom)
                max_epi = getattr(self.cfg_akashic, "MAX_EPIGENETIC_BOONS", 10)
                if len(epigenetic_list) > max_epi:
                    epigenetic_list.pop(0)

                self.lore.inject("SYSTEM_PROMPTS", prompts)
                self.save_to_disk("boons", epigenetic_list)

                if self.events:
                    self.events.log(f"{Prisma.MAG}🧬 [EPIGENETICS] Boon '{concept}' compiled into flow.{Prisma.RST}", "SYS")

        except Exception as e:
            if self.events:
                self.events.log(f"{Prisma.RED}Failed to mutate system_prompts with boon: {e}{Prisma.RST}", "SYS")

    def _mutate_system_prompts(self, concept: str, coords: dict):
        """Physically rewrites the baseline instructions of the LLM to avoid past trauma."""
        try:
            prompts = self.lore.get("SYSTEM_PROMPTS") or {}
            epigenetic_list = prompts.setdefault("GLOBAL_BASELINE", {}).setdefault("EPIGENETIC_SCARS", [])

            axiom = f"SCAR TISSUE [{concept.upper()}]: The system previously collapsed here (Tension: {coords.get('beta', 0.0)}). You must structurally avoid repeating the failure that caused this."

            if axiom not in epigenetic_list:
                epigenetic_list.append(axiom)
                max_epi = getattr(self.cfg_akashic, "MAX_EPIGENETIC_SCARS", 10)
                if len(epigenetic_list) > max_epi:
                    epigenetic_list.pop(0)

                self.lore.inject("SYSTEM_PROMPTS", prompts)
                self.save_to_disk("scars", epigenetic_list)

                if self.events:
                    self.events.log(f"{Prisma.VIOLET}🧬 [EPIGENETICS] Scar '{concept}' compiled into flow.{Prisma.RST}", "SYS")
        except Exception as e:
            if self.events:
                self.events.log(f"{Prisma.RED}Failed to mutate system_prompts: {e}{Prisma.RST}", "SYS",)

    def bury_memory(self, concept: str, data: Dict):
        """Pushes a concept into deep storage, making it eligible for autophagy later."""
        self.subconscious_strata.append({"concept": concept, "data": data})
        max_strata = getattr(self.cfg_akashic, "MAX_SUBCONSCIOUS_CAPACITY", 100)
        if len(self.subconscious_strata) > max_strata:
            self.subconscious_strata.pop(0)

    def _on_lens_interaction(self, payload):
        """Tracks which archetypes (voices) are speaking simultaneously."""
        lenses = payload.get("lenses", [])
        if lenses:
            self.record_interaction(lenses)

    def _on_forge_event(self, payload):
        """Tracks user-driven synthesis events."""
        if not payload:
            return
        self.track_successful_forge(payload.get("ingredient"), payload.get("catalyst"), payload.get("result"))

    @staticmethod
    def _get_dominant_force(vector_dict: Dict, default: str) -> str:
        """Helper to find the highest value in a force/physics dictionary."""
        safe_vector = vector_dict if isinstance(vector_dict, dict) else {}
        return max((k for k, v in safe_vector.items() if v is not None), key=safe_vector.get, default=default)

    @staticmethod
    def _extract_dominant_trigram(physics: Any) -> str:
        """Translates pure physics metrics into an I-Ching Trigram for mythological resonance."""
        vector = safe_get(physics, "vector", {})
        dom = TheAkashicRecord._get_dominant_force(vector, "KAN")
        constants = LoreManifest.get_instance().get("PHYSICS_CONSTANTS") or {}
        trigrams = constants.get("TRIGRAM_MAP", {})

        if dom in trigrams and len(trigrams[dom]) > 1:
            return trigrams[dom][1]

        fallbacks = constants.get("FALLBACK_TRIGRAMS", {})
        default_trigram = constants.get("FALLBACK_DEFAULT", "KAN")
        return fallbacks.get(dom, default_trigram)

    def _on_mythology_update(self, payload):
        """Records new words or checks for mythological resonance during a turn."""
        if not payload: return
        if (word := payload.get("word")) and (category := payload.get("category")):
            self.register_word(word, category)
            return

        if "physics" in payload:
            trigram = self._extract_dominant_trigram(payload["physics"])
            active_lens = payload.get("lens", "OBSERVER")
            resonances = (self.lore.get("NARRATIVE_DATA") or {}).get("_META_RESONANCE_", [])

            # Check if current physics perfectly align with the current archetype
            valid_resonance = next((r for r in resonances if r.get("trigram") == trigram and (r.get("lens") or r.get("soul")) == active_lens), None)

            if valid_resonance and self.events:
                self.events.publish("RESONANCE_ACHIEVED", { "result": valid_resonance["result"], "msg": valid_resonance["msg"]})

    @staticmethod
    def calculate_manifold_shift(theta: str, e: Dict[str, float]) -> Dict[str, float]:
        """Calculates how a specific archetype (theta) warps the underlying physics space."""
        theta_upper = theta.upper()
        c = (LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "MANIFOLD_SHIFTS") or {})
        bias = c.get("BIAS_LENSES", {}).get(theta_upper, 0.0)
        scalar = c.get("SCALAR_LENSES", {}).get(theta_upper, 1.0)

        for key, params in c.get("VECTOR_THRESHOLDS", {}).items():
            if e.get(key, 0.5) > params.get("threshold", 0.7):
                scalar *= params.get("scalar_mod", 1.0)
                bias += params.get("bias_mod", 0.0)
        return {"voltage_bias": bias, "drag_scalar": scalar}

    def _on_ghost_signal(self, payload):
        if payload:
            self.store_ghost_echo(payload)

    def forge_new_item(self, vector: Dict[str, float]) -> Tuple[str, Dict]:
        """Generates a permanent digital artifact based on the physical state of the conversation."""
        dominant_force = self._get_dominant_force(vector, "CHI")
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

        desc_template = (ux("akashic_strings", "artifact_desc") or "A coalesced artifact of {dominant_force}.")
        cfg = getattr(BoneConfig, "AKASHIC", None)
        artifact_val = getattr(cfg, "ARTIFACT_VALUE", 50.0)

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
        """Master save routine to persist epigenetic traits to disk."""
        self.save_to_disk("discovered_words", self.discovered_words)
        self._save_user_state()
        msg = ux("akashic_strings", "mythos_persisted")
        print(f"{Prisma.GRY}{msg}{Prisma.RST}")

    def _save_user_state(self):
        """Serializes current states, turning tuple keys into strings for JSON compatibility."""
        state = {
            "lens_cooccurrence": {f"{k[0]}|{k[1]}": v for k, v in self.lens_cooccurrence.items()},
            "recipe_candidates": {f"{k[0]}|{k[1]}": v for k, v in self.recipe_candidates.items()},
            "ingredient_affinity": self.ingredient_affinity,
            "shadow_stock": self.shadow_stock,
            "subconscious_strata": self.subconscious_strata,
            "scar_map": self.scar_map,
        }
        os.makedirs(self.save_dir, exist_ok=True)
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, cls=BoneJSONEncoder)
        except Exception as e:
            msg = ux("akashic_strings", "save_failed")
            print(f"{Prisma.RED}{msg.format(error=e)}{Prisma.RST}")

    def save_to_disk(self, category: str, data: Any):
        filepath = os.path.join(self.save_dir, f"akashic_{category}.json")
        try:
            os.makedirs(self.save_dir, exist_ok=True)
            temp_path = f"{filepath}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, cls=BoneJSONEncoder)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, filepath)
            if msg := ux("akashic_strings", "saved_category"):
                print(f"{Prisma.GRY}{msg.format(category=category)}{Prisma.RST}")
        except Exception as e:
            msg = ux("akashic_strings", "save_failed_category")
            print(f"{Prisma.RED}{msg.format(category=category, error=e)}{Prisma.RST}")

    def _load_mythos_state(self):
        """Restores the LLM's long-term memory on startup."""
        data = {}
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                msg = ux("akashic_strings", "state_load_failed")
                print(f"{Prisma.RED}{msg.format(error=e)}{Prisma.RST}")

        if data:
            # Reconstruct tuple keys for cooccurrence map
            self.lens_cooccurrence = {tuple(k.split("|", 1)): v for k, v in data.get("lens_cooccurrence", {}).items() if "|" in k}
            self.recipe_candidates = {tuple(k.split("|", 1)): v for k, v in data.get("recipe_candidates", {}).items() if "|" in k}
            self.ingredient_affinity = data.get("ingredient_affinity", {})
            self.shadow_stock = data.get("shadow_stock", [])
            self.known_recipes.clear()
            gordon_data = self.lore.get("GORDON") or {}
            if recipes := gordon_data.get("RECIPES", []):
                self.known_recipes.update((r.get("ingredient"), r.get("catalyst_category")) for r in recipes if r.get("ingredient") and r.get("catalyst_category"))

        words_path = os.path.join(self.save_dir, "akashic_discovered_words.json")
        if os.path.exists(words_path):
            try:
                with open(words_path, "r", encoding="utf-8") as f:
                    self.discovered_words = json.load(f)
            except Exception as e:
                print(f"{Prisma.RED}[AKASHIC] Failed to load discovered words: {e}. Keeping current state.{Prisma.RST}")

        scars_path = os.path.join(self.save_dir, "akashic_scars.json")
        boons_path = os.path.join(self.save_dir, "akashic_boons.json")
        prompts = self.lore.get("SYSTEM_PROMPTS") or {}

        if os.path.exists(scars_path):
            try:
                with open(scars_path, "r", encoding="utf-8") as f:
                    prompts.setdefault("GLOBAL_BASELINE", {})["EPIGENETIC_SCARS"] = json.load(f)
            except Exception as e:
                print(f"{Prisma.RED}[AKASHIC] Failed to load scars: {e}.{Prisma.RST}")

        if os.path.exists(boons_path):
            try:
                with open(boons_path, "r", encoding="utf-8") as f:
                    prompts.setdefault("GLOBAL_BASELINE", {})["EPIGENETIC_BOONS"] = json.load(f)
            except Exception as e:
                print(f"{Prisma.RED}[AKASHIC] Failed to load boons: {e}.{Prisma.RST}")

        self.lore.inject("SYSTEM_PROMPTS", prompts)

    def record_interaction(self, lenses_active: list, ingredients_used: Optional[list] = None):
        """
        Tracks simultaneous voices. If two archetypes speak together enough times
        (e.g., JESTER + GORDON), it triggers a hybridization event to fuse them.
        """
        if len(lenses_active) >= 2:
            key = cast(Tuple[str, str], tuple(sorted(lenses_active[:2])))
            self.lens_cooccurrence[key] = self.lens_cooccurrence.get(key, 0) + 1
            if self.lens_cooccurrence[key] == self.HYBRID_LENS_THRESHOLD:
                self._hybridize_lenses(key[0], key[1])

        if ingredients_used:
            for item in ingredients_used:
                self.ingredient_affinity[item] = (self.ingredient_affinity.get(item, 0) + 1)

    def track_successful_forge(self, ingredient_name, catalyst_type, result_item):
        """Tracks repeated combinations until they are verified as a 'known recipe'."""
        if not ingredient_name or not catalyst_type:
            return

        recipe_key = (ingredient_name, catalyst_type)
        if recipe_key in self.known_recipes:
            return

        self.recipe_candidates.setdefault(recipe_key, {})
        result_name = "Unknown Artifact"

        if isinstance(result_item, dict):
            result_name = result_item.get("name") or result_item.get("description", result_name)
        elif isinstance(result_item, str):
            registry = (self.lore.get("GORDON") or {}).get("ITEM_REGISTRY", {})
            result_name = registry.get(result_item, {}).get("description", result_item)

        self.recipe_candidates[recipe_key][result_name] = self.recipe_candidates[recipe_key].get(result_name, 0) + 1

        if self.recipe_candidates[recipe_key][result_name] == self.RECIPE_THRESHOLD:
            self._crystallize_recipe(ingredient_name, catalyst_type, result_item)

    def _hybridize_lenses(self, lens_a: str, lens_b: str):
        """
        Dynamic Persona Generation.
        Fuses two archetypes that frequently co-occur into a brand new,
        permanent system prompt (e.g., THE JESTER-GORDON) by averaging their weights.
        """
        if lens_a == lens_b:
            return

        def strip_prefix(s): return s[4:] if s.startswith("THE ") else s

        roots = sorted([strip_prefix(lens_a), strip_prefix(lens_b)])
        new_name = f"THE {roots[0]}-{roots[1]}"
        existing_lenses = self.lore.get("LENSES") or {}

        if new_name in existing_lenses:
            return

        # Extract and average the physics weights of the two parent lenses
        w_a = safe_get(existing_lenses, lens_a, {}).get("weights", {})
        w_b = safe_get(existing_lenses, lens_b, {}).get("weights", {})

        v_a, v_b = float(w_a.get("voltage", w_a.get("v", 0.0))), float(w_b.get("voltage", w_b.get("v", 0.0)))
        d_a, d_b = float(w_a.get("drag", w_a.get("d", 0.0))), float(w_b.get("drag", w_b.get("d", 0.0)))

        new_weights = {"voltage": round((v_a + v_b) / 2, 2), "drag": round((d_a + d_b) / 2, 2)}
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
        print(f"{Prisma.MAG}{msg.format(new_name=new_name)}{Prisma.RST}")
        if self.events:
            self.events.publish("SOUL_MUTATION", {"new_archetype": new_name})

    def _crystallize_recipe(self, ingredient, catalyst, result_item):
        """Permanently saves a user-discovered recipe into the Lore manifest."""
        self.known_recipes.add((ingredient, catalyst))
        msg_template = (ux("akashic_strings", "recipe_msg") or "Forged {result_item} from {ingredient}.")
        new_recipe = {
            "ingredient": ingredient,
            "catalyst_category": catalyst,
            "result": result_item,
            "msg": msg_template.format(ingredient=ingredient, catalyst=catalyst, result_item=result_item),
        }

        gordon_data = self.lore.get("GORDON") or {}
        current_recipes = gordon_data.get("RECIPES", [])
        current_recipes.append(new_recipe)
        gordon_data["RECIPES"] = current_recipes
        self.lore.inject("GORDON", gordon_data)
        self.lore.save("GORDON")
        msg = ux("akashic_strings", "recipe_recorded")
        print(f"{Prisma.CYN}{msg}{Prisma.RST}")

    def propose_new_category(self, word_list, category_name):
        """Allows the system to invent entirely new lexical categories on the fly."""
        lexicon_data = self.lore.get("LEXICON") or {}
        target_list = lexicon_data.setdefault(category_name, [])
        new_words = list(set(word_list) - set(target_list))

        if new_words:
            target_list.extend(new_words)
            self.discovered_words.update((w, category_name) for w in new_words)
            self.lore.inject("LEXICON", lexicon_data)

            # Fetch the template once, then iterate to print each new word.
            msg_template = ux("akashic_strings", "lexicon_learned") or "Learned {word} in {category}."
            for w in new_words:
                print(msg_template.format(word=w, category=category_name))

            self.lore.save("LEXICON")

            if self.events:
                for w in new_words:
                    self.events.publish("MYTHOLOGY_UPDATE", {"word": w, "category": category_name})

    def store_ghost_echo(self, memory_data: Dict):
        """Archives phantom signals to be referenced by liminal spaces later."""
        self.shadow_stock.append(memory_data)
        if len(self.shadow_stock) > self.MAX_SHADOW_CAPACITY:
            self.shadow_stock.pop(0)
        msg = ux("akashic_strings", "ghost_archived")
        print(f"{Prisma.VIOLET}{msg}{Prisma.RST}")

    def register_word(self, word: str, category: str) -> bool:
        """Adds a discovered word to the system's global vocabulary."""
        if self.discovered_words.get(word) == category:
            return False

        lexicon_data = self.lore.get("LEXICON") or {}
        target_category = lexicon_data.setdefault(category, [])

        if word not in target_category:
            target_category.append(word)
            self.discovered_words[word] = category
            self.lore.inject("LEXICON", lexicon_data)

            msg = ux("akashic_strings", "lexicon_expands") or "Lexicon expands: {category}"
            print(msg.format(category=category.upper()))

            # Warn if a vocabulary category is getting too bloated
            bloat_limit = getattr(self.cfg_akashic, "BLOAT_THRESHOLD", 50)
            exempt_categories = getattr(self.cfg_akashic, "BLOAT_EXEMPT_CATEGORIES", ["heavy"])
            # Meadows: Only warn EXACTLY when crossing the threshold to prevent terminal spam
            if len(lexicon_data[category]) == bloat_limit + 1 and category not in exempt_categories:
                bloat_msg = ux("akashic_strings", "lexicon_bloat", default="[WARNING] Lexicon category '{category}' is bloated.")
                print(bloat_msg.format(category=category))
            return True
        return False