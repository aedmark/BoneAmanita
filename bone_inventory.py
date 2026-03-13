"""
bone_inventory.py

The Superintendent's Ledger.
This module handles the physical grounding of the lattice. It manages Gordon's
inventory, processes the materialization of items from thermodynamic states (Loot),
and brutally enforces Object-Action Coupling to prevent narrative hallucination.
"""

import random
import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from bone_presets import BoneConfig
from bone_core import LoreManifest, ux
from bone_types import Prisma

@dataclass
class Item:
    """
    A crystallized packet of thermodynamic reality.
    Items are not just props; they hold intrinsic value, passive traits,
    and can possess 'reflex_triggers' that act as emergency fuses for the system.
    """
    name: str
    description: str
    function: str
    passive_traits: List[str] = field(default_factory=list)
    spawn_context: str = "COMMON"
    value: float = 1.0
    usage_msg: str = "Used."
    consume_on_use: bool = False
    reflex_trigger: Optional[str] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict):
        default_desc = ux("gordon_strings", "default_item_desc") or "Unknown Artifact"
        default_usage = ux("gordon_strings", "default_item_use") or f"You use the {name}."

        return cls(name=name, description=data.get("description", default_desc),
                   function=data.get("function", "MISC"), passive_traits=data.get("passive_traits", []),
                   spawn_context=data.get("spawn_context", "COMMON"), value=data.get("value", 1.0),
                   usage_msg=data.get("usage_msg", default_usage),
                   consume_on_use=data.get("consume_on_use", False), reflex_trigger=data.get("reflex_trigger", None))

class GordonKnot:
    """
    The grounding anchor of the VSL.
    Gordon manages the spatial and material continuity of the simulation.
    He tracks what you hold, synthesizes abstract concepts into physical items,
    and vetoes actions that violate local physics.
    """
    def __init__(self, events=None, mode="ADVENTURE"):
        self.mode = mode.upper()
        self.blueprints = None
        self.events = events
        self.inventory: List[str] = []
        self.registry: Dict[str, Item] = {}
        self.ITEM_REGISTRY: Dict[str, Dict] = {}
        self.recipes: List[Dict] = []
        self.action_coupling: Dict[str, List[str]] = {}
        self.location_coupling: Dict[str, str] = {}
        self.max_slots = 10
        self.last_flinch_turn = -100
        self.scar_tissue = {}
        self.refusal_markers = set()
        self.loot_triggers = []
        self.creative_loot_triggers = []
        self.interaction_verbs = []
        self.acquisition_verbs = []
        self.abandonment_phrases = []
        self.load_config()

    def enforce_object_action_coupling(
            self, user_input: str, current_zone: str) -> Optional[str]:
        """
        The Universal Axiom: An action cannot be performed on an object unless
        the object is present at the location of the action.
        If the user tries to unlock a door without a key, Gordon interrupts the LLM
        and rejects the prompt entirely.
        """
        if self.mode in ["CREATIVE", "CONVERSATION", "TECHNICAL"]:
            return None
        text = user_input.lower()
        # 1. Location-based Action Coupling
        for action_obj_pair, required_loc in self.location_coupling.items():
            words = action_obj_pair.split()
            if all(re.search(rf"\b{w}\b", text) for w in words):
                if required_loc not in current_zone.lower():
                    msg = ux("gordon_strings", "premise_loc")
                    return f"{Prisma.SLATE}{msg.format(loc=required_loc, zone=current_zone)}{Prisma.RST}"
        inventory_items = " ".join([i.get("name", "").lower() for i in self.get_inventory_data()])
        # 2. Inventory-based Action Coupling
        for action, required_objects in self.action_coupling.items():
            verb_pattern = rf"\b(?:i\s+(?:will\s+)?{action}|to\s+{action}|{action}\s+(?:the|a|an|my|some|it|this|that)|{action}ing)\b|^{action}\b"
            if re.search(verb_pattern, text):
                has_item = any(obj in inventory_items for obj in required_objects)
                mentions_item = any(obj in text for obj in required_objects)
                if not has_item and not mentions_item:
                    req_str = ", ".join(required_objects)
                    msg = ux("gordon_strings", "premise_req")
                    return f"{Prisma.SLATE}{msg.format(action=action, req_str=req_str)}{Prisma.RST}"
        # 3. Explicit Interaction Checks (e.g., 'examine', 'use')
        has_interaction = any(re.search(rf"\b{v}\b", text) for v in self.interaction_verbs)
        if has_interaction:
            all_known = set(self.registry.keys()) | set(self.ITEM_REGISTRY.keys())
            for item_name in all_known:
                item_lower = item_name.lower().replace("_", " ")
                if item_lower in text and item_name.upper() not in self.inventory:
                    msg = ux("gordon_strings", "premise_inv")
                    return f"{Prisma.SLATE}{msg.format(item=item_lower)}{Prisma.RST}"

        return None

    def load_config(self):
        data = LoreManifest.get_instance().get("GORDON") or {}
        if not data and hasattr(LoreManifest, "get_raw"):
            data = LoreManifest.get_raw("gordon.json") or {}
        self.action_coupling = data.get("ACTION_COUPLING", {})
        self.location_coupling = data.get("LOCATION_COUPLING", {})
        self.refusal_markers = set(data.get("REFUSAL_MARKERS", []))
        self.creative_loot_triggers = data.get("CREATIVE_LOOT_TRIGGERS", [])
        if self.mode in ["CREATIVE", "CONVERSATION"]:
            self.loot_triggers = self.creative_loot_triggers
        else:
            self.loot_triggers = data.get("LOOT_TRIGGERS", [])
        self.interaction_verbs = data.get("INTERACTION_VERBS", [])
        self.acquisition_verbs = data.get("ACQUISITION_VERBS", [])
        lexicon_data = LoreManifest.get_instance().get("lexicon") or {}
        if not lexicon_data and hasattr(LoreManifest, "get_raw"):
            lexicon_data = LoreManifest.get_raw("lexicon.json") or {}
        self.abandonment_phrases = lexicon_data.get("abandonment_phrases", ["put back", "leave", "drop", "ignore"])
        self.blueprints = LoreManifest.get_instance().get("ITEM_GENERATION") or {}
        self.ITEM_REGISTRY = data.get("ITEM_REGISTRY", {})
        for name, props in self.ITEM_REGISTRY.items():
            self.registry[name] = Item.from_dict(name, props)
        self.recipes = data.get("RECIPES", [])
        self.scar_tissue = data.get("SCAR_TISSUE", {})
        starters = data.get("STARTING_INVENTORY", [])
        if not self.inventory and starters:
            self.inventory = [s for s in starters if isinstance(s, str)]
        if hasattr(BoneConfig, "INVENTORY"):
            self.max_slots = getattr(BoneConfig.INVENTORY, "MAX_SLOTS", 10)

    def process_loot_tags(self, text: str, user_input: str) -> Tuple[str, List[str]]:
        """
        Scrapes the LLM's narrative output for explicit [[LOOT: Item]] tags,
        or falls back to NLP parsing to see if the user organically picked something up.
        """
        loot_pattern = r"\[\[LOOT:\s*(.*?)\]\]"
        lost_pattern = r"\[\[LOST:\s*(.*?)\]\]"
        raw_loot = re.findall(loot_pattern, text, re.IGNORECASE)
        raw_lost = re.findall(lost_pattern, text, re.IGNORECASE)
        combined_text = (user_input + " " + text).lower()
        if any(phrase in combined_text for phrase in self.abandonment_phrases):
            raw_loot = []

        def normalize(items):
            return list(
                {re.sub(r"[^A-Z0-9_]", "", i.strip().upper().replace(" ", "_"))
                 for i in items
                 if i})
        new_loot = normalize(raw_loot)
        if not new_loot:
            implicit_loot = self.parse_loot(user_input, text)
            if implicit_loot:
                new_loot = normalize([implicit_loot])
        lost_loot = normalize(raw_lost)
        logs = []
        if new_loot:
            clean_input = user_input.lower()
            has_intent = any(verb in clean_input for verb in self.acquisition_verbs)
            if has_intent:
                for item in new_loot:
                    logs.append(self.acquire(item))
                    if self.events:
                        self.events.publish("ITEM_ACQUIRED", {"item": item})
            else:
                if self.events:
                    for item in new_loot:
                        msg = ux("gordon_strings", "consent_loot")
                        self.events.log(msg.format(item=item), "GORDON")
        for item in lost_loot:
            if self.safe_remove_item(item):
                msg = ux("gordon_strings", "entropy_lost")
                logs.append(f"{Prisma.GRY}{msg.format(item=item)}{Prisma.RST}")
            else:
                msg = ux("gordon_strings", "glitch_lose")
                logs.append(f"{Prisma.OCHRE}{msg.format(item=item)}{Prisma.RST}")
        clean_text = re.sub(loot_pattern, "", text, flags=re.IGNORECASE)
        clean_text = re.sub(lost_pattern, "", clean_text, flags=re.IGNORECASE)
        return clean_text.strip(), logs

    def get_item_data(self, item_name: str) -> Optional[Item]:
        if item_name in self.registry:
            return self.registry[item_name]
        if item_name in self.ITEM_REGISTRY:
            raw_data = self.ITEM_REGISTRY[item_name]
            item_obj = Item.from_dict(item_name, raw_data)
            self.registry[item_name] = item_obj
            return item_obj
        return None

    def get_inventory_data(self) -> List[Dict]:
        return [item.__dict__
                for name in self.inventory
                if (item := self.get_item_data(name))]

    def acquire(self, tool_name: str) -> str:
        """ Adds an item to inventory, forcing the oldest item out if pockets are full. """
        tool_name = tool_name.strip().upper().replace(" ", "_") if tool_name else "UNKNOWN"
        if tool_name in self.inventory:
            msg = ux("gordon_strings", "inv_duplicate")
            return f"{Prisma.OCHRE}{msg.format(item=tool_name)}{Prisma.RST}"
        item_obj = self.get_item_data(tool_name)
        if not item_obj:
            item_obj = self.get_item_data(tool_name.lower())
        if not item_obj:
            # On-the-fly registration of unmapped items
            fallback_desc = ux("gordon_strings", "fallback_desc", "???")
            new_item = Item(name=tool_name, description=fallback_desc, function="MISC")
            self.registry[tool_name] = new_item
            self.ITEM_REGISTRY[tool_name] = new_item.__dict__
        if len(self.inventory) >= self.max_slots:
            dropped = self.inventory.pop(0)
            if self.events:
                msg = ux("gordon_strings", "inv_full_drop")
                self.events.log(msg.format(dropped=dropped), "INV")
        self.inventory.append(tool_name)
        if self.events:
            self.events.publish("ITEM_ACQUIRED", {"item": tool_name})
        msg = ux("gordon_strings", "acquired")
        return f"{Prisma.GRN}{msg.format(item=tool_name)}{Prisma.RST}"

    def safe_remove_item(self, item_name: str) -> bool:
        item_name = item_name.upper()
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            return True
        return False

    def rummage(
            self, physics_ref: Dict, stamina_pool: float) -> Tuple[bool, str, float]:
        """
        Burns physical stamina to actively search the semantic noise for items.
        Only returns items appropriate to the current Voltage/Drag state.
        """
        cost = 15.0
        if hasattr(BoneConfig, "INVENTORY"):
            cost = getattr(BoneConfig.INVENTORY, "RUMMAGE_COST", 15.0)
        if stamina_pool < cost:
            msg = ux("gordon_strings", "rummage_tired")
            return False, f"{Prisma.OCHRE}{msg}{Prisma.RST}", 0.0
        loot_table = self._get_loot_candidates(physics_ref)
        if not loot_table:
            msg = ux("gordon_strings", "rummage_empty")
            return False, msg, cost
        found_item = random.choice(loot_table)
        msg = self.acquire(found_item)
        return True, msg, cost

    def _get_loot_candidates(self, physics: Dict) -> List[str]:
        """ Filters the global registry down to items matching the current thermodynamic weather. """
        candidates = []
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        psi = physics.get("psi", 0.0)
        v_high = getattr(BoneConfig.PHYSICS, "VOLTAGE_HIGH", 12.0)
        v_crit = getattr(BoneConfig.PHYSICS, "VOLTAGE_CRITICAL", 15.0)
        d_heavy = getattr(BoneConfig.PHYSICS, "DRAG_HEAVY", 5.0)
        psi_high = getattr(BoneConfig.PHYSICS, "PSI_HIGH", 0.6)
        for name in set(self.registry) | set(self.ITEM_REGISTRY):
            if not (item := self.get_item_data(name)):
                continue
            ctx = item.spawn_context
            if (ctx in ("COMMON", "STANDARD")
                    or (ctx == "VOLTAGE_HIGH" and voltage > v_high)
                    or (ctx == "VOLTAGE_CRITICAL" and voltage > v_crit)
                    or (ctx == "DRAG_HEAVY" and drag > d_heavy)
                    or (ctx == "PSI_HIGH" and psi > psi_high)):
                candidates.append(name)
        return candidates

    def register_dynamic_item(self, name: str, data: Dict):
        name = name.upper()
        if name not in self.registry:
            new_item = Item.from_dict(name, data)
            self.registry[name] = new_item
            if self.events:
                msg = ux("gordon_strings", "make_space")
                self.events.log(f"{Prisma.CYN}{msg.format(name=name)}{Prisma.RST}", "INV")

    def synthesize_item(self, physics_vector: Dict[str, float]) -> str:
        """
        Procedural generation of artifacts. It looks at the dominant physical dimension
        (e.g., PSI, VEL, STR) and combines prefixes and suffixes to forge a unique item
        out of pure conversational energy.
        """
        if not hasattr(self, "blueprints") or not self.blueprints:
            self.blueprints = LoreManifest.get_instance().get("ITEM_GENERATION") or {}
        fallbacks = self.blueprints.get("FALLBACKS", {})
        dim_map = self.blueprints.get("DIM_MAP", {})
        dom_dim = max(physics_vector, key=physics_vector.get) if physics_vector else "ENT"
        archetype = dim_map.get(dom_dim, "void")
        prefixes = self.blueprints.get("PREFIXES", {}).get(archetype, fallbacks.get("PREFIX", ["Strange"]))
        suffixes = self.blueprints.get("SUFFIXES", {}).get(archetype, fallbacks.get("SUFFIX", ["of Mystery"]))
        if self.mode in ["CREATIVE", "CONVERSATION"]:
            base_cat = self.blueprints.get("CREATIVE_BASE_CAT", "ABSTRACT")
            bases = self.blueprints.get("BASES", {}).get(base_cat, fallbacks.get("BASE", ["Concept"]))
            creative_overrides = self.blueprints.get("CREATIVE_OVERRIDES", {})
            prefixes = creative_overrides.get("PREFIXES", prefixes)
            suffixes = creative_overrides.get("SUFFIXES", suffixes)
        else:
            default_adv_cats = ["TOOL", "JUNK", "ARTIFACT"]
            adv_cats = self.blueprints.get("ADVENTURE_CATEGORIES", default_adv_cats)
            base_cat = random.choice(adv_cats)
            bases = self.blueprints.get("BASES", {}).get(base_cat, fallbacks.get("BASE", ["Object"]))
        prefix = random.choice(prefixes)
        base = random.choice(bases)
        suffix = random.choice(suffixes)
        full_name = (
            f"{prefix} {base} {suffix}"
            if self.mode == "ADVENTURE"
            else f"{prefix} {base} {suffix}")
        clean_id = full_name.upper().replace(" ", "_")
        desc_template = ux("gordon_strings", "synthesis_desc")
        item_data = {"description": desc_template.format(base=base.lower(), archetype=archetype),
                     "function": "ARTIFACT", "passive_traits": ["DYNAMIC"],
                     "value": round(physics_vector.get(dom_dim, 0.0) * 10, 1), "spawn_context": "FORGED", }
        self.register_dynamic_item(clean_id, item_data)
        return clean_id

    def parse_loot(self, user_text: str, sys_text: str) -> Optional[str]:
        """ Secondary NLP parser to catch implicit item acquisitions without formal tags. """
        combined_text = (user_text + " " + sys_text).lower()
        if any(phrase in combined_text for phrase in self.abandonment_phrases):
            return None
        text = (user_text + " " + sys_text).lower()
        sys_lower = sys_text.lower()
        for refusal in self.refusal_markers:
            if refusal in sys_lower:
                return None
        all_known_items = set(self.registry.keys()) | set(self.ITEM_REGISTRY.keys())
        for name in all_known_items:
            if name.lower() in text and name.upper() not in self.inventory:
                for t in self.loot_triggers:
                    if t in text:
                        return name
        sorted_triggers = sorted(self.loot_triggers, key=len, reverse=True)
        for t in sorted_triggers:
            if t in text:
                pattern = (f"{re.escape(t)}\\s+(?:the\\s+|a\\s+|an\\s+)?(?P<item>[\\w\\s]{{1,30}}?)"
                           f"(?:\\s+(?:from|on|in|under|with|by|near|at|to|you|it|he|she|we|they)|[\\.,!?]|$)")
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    candidate = match.group("item").strip()
                    if (2 < len(candidate) < 40
                            and candidate not in self.refusal_markers):
                        return candidate
        return None

    def consume(self, item_name: str) -> Tuple[bool, str]:
        item_name = item_name.upper()
        if item_name not in self.inventory:
            return False, ux("gordon_strings", "consume_missing")
        item = self.get_item_data(item_name)
        if not item or not item.consume_on_use:
            msg = ux("gordon_strings", "consume_invalid")
            return False, msg.format(item=item_name)
        self.inventory.remove(item_name)
        if item.function == "STABILITY":
            msg = ux( "gordon_strings", "consume_pizza")
            return True, msg.format(item=item_name)
        msg = ux("gordon_strings", "consume_used")
        return True, msg.format(item=item_name, usage_msg=item.usage_msg)

    def emergency_reflex(self, physics_ref: Dict) -> Tuple[bool, Optional[str]]:
        """
        Hardware Fuses. If the lattice approaches a critical collapse state
        (e.g., Voltage > 18.0), and Gordon holds an item with a matching reflex trigger,
        that item is instantly consumed to absorb the blow and reset the physics to a safe state.
        """
        voltage = physics_ref.get("voltage", 0.0)
        drag = physics_ref.get("narrative_drag", 0.0)
        kappa = physics_ref.get("kappa", 0.5)
        cfg = getattr(BoneConfig, "INVENTORY", None)
        v_trig = getattr(cfg, "REFLEX_VOLTAGE_TRIGGER", 18.0) if cfg else 18.0
        v_reset = getattr(cfg, "REFLEX_VOLTAGE_RESET", 12.0) if cfg else 12.0
        d_trig = getattr(cfg, "REFLEX_DRAG_TRIGGER", 6.0) if cfg else 6.0
        d_reset = getattr(cfg, "REFLEX_DRAG_RESET", 0.0) if cfg else 0.0
        k_trig = getattr(cfg, "REFLEX_KAPPA_TRIGGER", 0.2) if cfg else 0.2
        k_reset = getattr(cfg, "REFLEX_KAPPA_RESET", 0.8) if cfg else 0.8
        for name in self.inventory:
            item = self.get_item_data(name)
            if not item:
                continue
            trigger = item.reflex_trigger
            if trigger == "VOLTAGE_CRITICAL" and voltage > v_trig:
                self.safe_remove_item(name)
                physics_ref["voltage"] = v_reset
                msg = ux( "gordon_strings", "reflex_voltage")
                return True, f"{Prisma.CYN}{msg.format(name=name)}{Prisma.RST}"
            if trigger == "DRIFT_CRITICAL" and drag > d_trig:
                self.safe_remove_item(name)
                physics_ref["narrative_drag"] = d_reset
                msg = ux( "gordon_strings", "reflex_drift")
                return True, f"{Prisma.OCHRE}{msg.format(name=name)}{Prisma.RST}"
            if trigger == "KAPPA_CRITICAL" and kappa < k_trig:
                self.safe_remove_item(name)
                physics_ref["kappa"] = k_reset
                msg = ux("gordon_strings", "reflex_kappa")
                return True, f"{Prisma.GRN}{msg.format(name=name)}{Prisma.RST}"

        return False, None