"""bone_inventory.py"""

import random
import re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from bone_presets import BoneConfig
from bone_core import LoreManifest, ux, safe_get, safe_set
from bone_types import Prisma

@dataclass
class Item:
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
        is_consumable = data.get("consume_on_use", False) or (data.get("cost") == "CONSUMABLE")
        return cls(
            name=name,
            description=data.get("description", default_desc),
            function=data.get("function", "MISC"),
            passive_traits=data.get("passive_traits", []),
            spawn_context=data.get("spawn_context", "COMMON"),
            value=data.get("value", 1.0),
            usage_msg=data.get("usage_msg", default_usage),
            consume_on_use=is_consumable,
            reflex_trigger=data.get("reflex_trigger", None),
        )

class GordonKnot:
    def __init__(self, events=None, mode="ADVENTURE", config_ref=None):
        self.cfg = config_ref or BoneConfig
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

    def enforce_object_action_coupling(self, user_input: str, current_zone: str) -> Optional[str]:
        if self.mode in ["CREATIVE", "CONVERSATION", "TECHNICAL"]:
            return None
        text = user_input.lower()
        for action_obj_pair, required_loc in self.location_coupling.items():
            words = action_obj_pair.split()
            if all(re.search(rf"\b{w}\b", text) for w in words):
                if required_loc not in current_zone.lower():
                    msg = ux("gordon_strings", "premise_loc")
                    return f"{Prisma.SLATE}{msg.format(loc=required_loc, zone=current_zone)}{Prisma.RST}"
        for action, req_objs in self.action_coupling.items():
            if action in text and re.search(
                    rf"\b(?:i\s+(?:will\s+)?{action}|to\s+{action}|{action}\s+(?:the|a|an|my|some|it|this|that)|{action}ing)\b|^{action}\b",
                    text,
            ):
                if not any(
                    obj.upper() in self.inventory or re.search(rf"\b{re.escape(obj)}\b", text) for obj in req_objs
                ):
                    return f"{Prisma.SLATE}{(ux('gordon_strings', 'premise_req') or '').format(action=action, req_str=', '.join(req_objs))}{Prisma.RST}"
        if any(re.search(rf"\b{v}\b", text) for v in self.interaction_verbs):
            for i in self.registry:
                if i.upper() not in self.inventory:
                    i_low = i.lower().replace('_', ' ')
                    if i_low in text and re.search(rf"\b{re.escape(i_low)}\b", text):
                        return f"{Prisma.SLATE}{(ux('gordon_strings', 'premise_inv') or '').format(item=i_low)}{Prisma.RST}"
        return None

    def load_config(self):
        data = LoreManifest.get_instance().get("GORDON") or (
            LoreManifest.get_raw("gordon.json") if hasattr(LoreManifest, "get_raw") else {}
        )
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
        if hasattr(self.cfg, "INVENTORY"):
            self.max_slots = getattr(self.cfg.INVENTORY, "MAX_SLOTS", 10)

    def process_loot_tags(self, text: str, user_input: str) -> Tuple[str, List[str]]:
        loot_pattern = r"\[\[LOOT:\s*(.*?)\]\]"
        lost_pattern = r"\[\[LOST:\s*(.*?)\]\]"
        raw_loot = re.findall(loot_pattern, text, re.IGNORECASE)
        raw_lost = re.findall(lost_pattern, text, re.IGNORECASE)
        combined_text = (user_input + " " + text).lower()

        def normalize_loot(items: List[str]) -> List[str]:
            cleaned_items = set()
            for item in items:
                if item:
                    stripped = item.strip().upper().replace(" ", "_")
                    alphanumeric = re.sub(r"[^A-Z0-9_]", "", stripped)
                    cleaned_items.add(alphanumeric)
            return list(cleaned_items)

        new_loot = normalize_loot(raw_loot)
        if not new_loot:
            implicit_loot = self.parse_loot(user_input, text)
            if implicit_loot:
                new_loot = normalize_loot([implicit_loot])
        lost_loot = normalize_loot(raw_lost)
        logs = []
        if new_loot:
            clean_input = user_input.lower()
            has_intent = any(verb in clean_input for verb in self.acquisition_verbs)
            if has_intent:
                for item in new_loot:
                    logs.append(self.acquire(item))
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
        clean_text = re.sub(rf"{loot_pattern}|{lost_pattern}", "", text, flags=re.IGNORECASE)
        return clean_text.strip(), logs

    def get_item_data(self, item_name: str) -> Optional[Item]:
        return self.registry.get(item_name)

    def get_inventory_data(self) -> List[Dict]:
        inventory_data = []
        for name in self.inventory:
            item = self.registry.get(name)
            if item:
                inventory_data.append(item.__dict__)
        return inventory_data

    def acquire(self, tool_name: str) -> str:
        tool_name = tool_name.strip().upper().replace(" ", "_") if tool_name else "UNKNOWN"
        if tool_name in self.inventory:
            msg = ux("gordon_strings", "inv_duplicate")
            return f"{Prisma.OCHRE}{msg.format(item=tool_name)}{Prisma.RST}"
        if not (self.get_item_data(tool_name) or self.get_item_data(tool_name.lower())):
            new_item = Item(name=tool_name, description=ux("gordon_strings", "fallback_desc") or "???", function="MISC")
            self.registry[tool_name] = new_item
        if len(self.inventory) >= self.max_slots:
            msg = ux("gordon_strings", "inv_full_reject") or "Inventory full. Cannot acquire {item}."
            if self.events:
                self.events.log(msg.format(item=tool_name), "INV")
            return f"{Prisma.OCHRE}{msg.format(item=tool_name)}{Prisma.RST}"
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

    def rummage(self, physics_ref: Any, stamina_pool: float) -> Tuple[bool, str, float]:
        try:
            cost = self.cfg.INVENTORY.RUMMAGE_COST
        except AttributeError:
            cost = 15.0
        if stamina_pool < cost:
            return False, f"{Prisma.OCHRE}{ux('gordon_strings', 'rummage_tired')}{Prisma.RST}", 0.0
        loot_table = self._get_loot_candidates(physics_ref)
        if not loot_table:
            return False, f"{Prisma.GRY}{ux('gordon_strings', 'rummage_empty')}{Prisma.RST}", cost
        return True, self.acquire(random.choice(loot_table)), cost

    def _get_loot_candidates(self, physics: Any) -> List[str]:
        v = float(safe_get(physics, "voltage", 0.0))
        d = float(safe_get(physics, "narrative_drag", 0.0))
        p = float(safe_get(physics, "psi", 0.0))
        cfg = getattr(self.cfg, "PHYSICS", object())
        vh = getattr(cfg, "VOLTAGE_HIGH", 12.0)
        vc = getattr(cfg, "VOLTAGE_CRITICAL", 15.0)
        dh = getattr(cfg, "DRAG_HEAVY", 5.0)
        ph = getattr(cfg, "PSI_HIGH", 0.6)
        return [
            item.name
            for item in self.registry.values()
            if (ctx := item.spawn_context) in ("COMMON", "STANDARD")
            or (ctx == "VOLTAGE_HIGH" and v > vh)
            or (ctx == "VOLTAGE_CRITICAL" and v > vc)
            or (ctx == "DRAG_HEAVY" and d > dh)
            or (ctx == "PSI_HIGH" and p > ph)
        ]

    def register_dynamic_item(self, name: str, data: Dict):
        name = name.upper()
        if name not in self.registry:
            new_item = Item.from_dict(name, data)
            self.registry[name] = new_item
            if self.events:
                msg = ux("gordon_strings", "make_space")
                self.events.log(f"{Prisma.CYN}{msg.format(name=name)}{Prisma.RST}", "INV")

    def synthesize_item(self, physics_vector: Dict[str, float]) -> str:
        if not self.blueprints:
            self.blueprints = LoreManifest.get_instance().get("ITEM_GENERATION") or {}
        fallbacks = self.blueprints.get("FALLBACKS", {})
        dim_map = self.blueprints.get("DIM_MAP", {})
        dom_dim = max(physics_vector, key=physics_vector.get) if physics_vector else "ENT"
        archetype = dim_map.get(dom_dim, "void")
        prefixes = self.blueprints.get("PREFIXES", {}).get(archetype, fallbacks.get("PREFIX", ["Strange"]))
        suffixes = self.blueprints.get("SUFFIXES", {}).get(archetype, fallbacks.get("SUFFIX", ["of Mystery"]))
        if self.mode in ["CREATIVE", "CONVERSATION"]:
            bases = self.blueprints.get("BASES", {}).get(
                self.blueprints.get("CREATIVE_BASE_CAT", "ABSTRACT"), fallbacks.get("BASE", ["Concept"])
            )
            overrides = self.blueprints.get("CREATIVE_OVERRIDES", {})
            prefixes, suffixes = overrides.get("PREFIXES", prefixes), overrides.get("SUFFIXES", suffixes)
        else:
            bases = self.blueprints.get("BASES", {}).get(
                random.choice(self.blueprints.get("ADVENTURE_CATEGORIES", ["TOOL", "JUNK", "ARTIFACT"])),
                fallbacks.get("BASE", ["Object"]),
            )
        base, prefix, suffix = (random.choice(bases), random.choice(prefixes), random.choice(suffixes))
        full_name = f"{prefix} {base} {suffix}"
        clean_id = full_name.upper().replace(" ", "_")
        desc_template = ux("gordon_strings", "synthesis_desc") or "A {base} forged of {archetype} energy."
        raw_value = physics_vector.get(dom_dim, 0.0) * 10
        clamped_value = min(100.0, round(raw_value, 1))
        item_data = {
            "description": desc_template.format(base=base.lower(), archetype=archetype),
            "function": "ARTIFACT",
            "passive_traits": ["DYNAMIC"],
            "value": clamped_value,
            "spawn_context": "FORGED",
        }
        self.register_dynamic_item(clean_id, item_data)
        return clean_id

    def parse_loot(self, user_text: str, sys_text: str) -> Optional[str]:
        combined_text = f"{user_text} {sys_text}".lower()
        if any(p in combined_text for p in self.abandonment_phrases) or any(
                r in sys_text.lower() for r in self.refusal_markers
        ):
            return None
        valid_triggers = [t for t in self.loot_triggers if t in combined_text]
        if not valid_triggers:
            return None
        candidates = [
            (name, name.lower().replace("_", " "))
            for name in self.registry.keys()
            if name.upper() not in self.inventory
        ]
        for t in sorted(valid_triggers, key=len, reverse=True):
            for name, clean in candidates:
                if clean in combined_text and re.search(
                    rf"\b{re.escape(t)}\b.*?\b{re.escape(clean)}\b", combined_text, re.IGNORECASE
                ):
                    return name
        return None

    def consume(self, item_name: str) -> Tuple[bool, str]:
        item_name = item_name.upper()
        if item_name not in self.inventory:
            return False, f"{Prisma.OCHRE}{ux('gordon_strings', 'consume_missing')}{Prisma.RST}"
        item = self.get_item_data(item_name)
        if not item or not item.consume_on_use:
            msg = ux("gordon_strings", "consume_invalid")
            return False, f"{Prisma.OCHRE}{msg.format(item=item_name)}{Prisma.RST}"
        self.inventory.remove(item_name)
        if item.function == "STABILITY":
            return (
                True,
                f"{Prisma.MAG}{(ux('gordon_strings', 'consume_pizza') or '').format(item=item_name)}{Prisma.RST}",
            )
        return (
            True,
            f"{Prisma.CYN}{(ux('gordon_strings', 'consume_used') or '').format(item=item_name, usage_msg=item.usage_msg)}{Prisma.RST}",
        )

    def emergency_reflex(self, physics_ref: Any) -> Tuple[bool, Optional[str]]:
        cfg = getattr(self.cfg, "INVENTORY", object())
        v = float(safe_get(physics_ref, "voltage", 0.0))
        d = float(safe_get(physics_ref, "narrative_drag", 0.0))
        k = float(safe_get(physics_ref, "kappa", 0.5))
        for name in self.inventory:
            item = self.get_item_data(name)
            if not item:
                continue
            trigger_type = item.reflex_trigger
            if not trigger_type:
                continue
            if trigger_type == "VOLTAGE_CRITICAL" and v > getattr(cfg, "REFLEX_VOLTAGE_TRIGGER", 18.0):
                self.safe_remove_item(name)
                safe_set(physics_ref, "voltage", getattr(cfg, "REFLEX_VOLTAGE_RESET", 12.0))
                return (
                    True,
                    f"{Prisma.CYN}{(ux('gordon_strings', 'reflex_voltage') or '').format(name=name)}{Prisma.RST}",
                )
            if t == "DRIFT_CRITICAL" and d > getattr(cfg, "REFLEX_DRAG_TRIGGER", 6.0):
                self.safe_remove_item(name)
                safe_set(physics_ref, "narrative_drag", getattr(cfg, "REFLEX_DRAG_RESET", 0.0))
                return (
                    True,
                    f"{Prisma.OCHRE}{(ux('gordon_strings', 'reflex_drift') or '').format(name=name)}{Prisma.RST}",
                )
            if t == "KAPPA_CRITICAL" and k < getattr(cfg, "REFLEX_KAPPA_TRIGGER", 0.2):
                self.safe_remove_item(name)
                safe_set(physics_ref, "kappa", getattr(cfg, "REFLEX_KAPPA_RESET", 0.8))
                return True, f"{Prisma.GRN}{(ux('gordon_strings', 'reflex_kappa') or '').format(name=name)}{Prisma.RST}"
        return False, None
