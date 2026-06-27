"""mechanics/inventory.py"""

import json
import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from constants import Prisma
from core import LoreManifest
from mechanics.tools import TheTclWeaver
from presets import BoneConfig
from struts import safe_get, safe_set, ux, ux_format


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
    is_container: bool = False
    capacity: int = 3
    contents: List[str] = field(default_factory=list)
    location: str = "VOID"

    @classmethod
    def from_dict(cls, name: str, data: Dict):
        default_desc = ux("gordon_strings", "default_item_desc") or "Unknown Artifact"
        default_usage = (
            ux("gordon_strings", "default_item_use") or f"You use the {name}."
        )
        is_consumable = data.get("consume_on_use", False) or (
            data.get("cost") == "CONSUMABLE"
        )
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
            is_container=data.get("is_container", False),
            capacity=data.get("capacity", 3),
            contents=data.get("contents", []),
            location=data.get("location", "VOID"),
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

    def apply_filters(self, user_message: str, active_physics: dict) -> str:
        if self.mode == "ADVENTURE":
            return user_message
        has_comb = any(
            "CUT_THE_CRAP"
            in (self.get_item_data(i).passive_traits if self.get_item_data(i) else [])
            for i in self.inventory
        )
        if has_comb:
            try:
                current_chi = float(
                    safe_get(
                        active_physics, "entropy", safe_get(active_physics, "chi", 0.5)
                    )
                )
                pruned = TheTclWeaver.get_instance().quantum_comb(
                    user_message, chi=current_chi
                )
                if pruned != user_message:
                    if self.events:
                        self.events.log(
                            f"{Prisma.CYN}Gordon rakes the comb through your prompt. Fluff discarded. -> '{pruned}'{Prisma.RST}",
                            "SYS",
                        )
                    return pruned
            except ImportError:
                pass
        return user_message

    def enforce_object_action_coupling(
        self, user_input: str, current_zone: str
    ) -> Optional[str]:
        if self.mode in ["CREATIVE", "CONVERSATION", "TECHNICAL"]:
            return None
        text = user_input.lower()
        tokens = set(re.findall(r"\b\w+\b", text))
        for action_obj_pair, required_loc in self.location_coupling.items():
            words = action_obj_pair.split()
            if all(w in tokens for w in words):
                if required_loc not in current_zone.lower():
                    msg = ux("gordon_strings", "premise_loc")
                    return f"{Prisma.SLATE}{msg.format(loc=required_loc, zone=current_zone)}{Prisma.RST}"
        for action, req_objs in self.action_coupling.items():
            if all(w in tokens for w in action.split()) and re.search(
                rf"\b(?:i\s+(?:will\s+)?{action}|to\s+{action}|{action}\s+(?:the|a|an|my|some|it|this|that)|{action}ing)\b|^{action}\b",
                text,
            ):
                has_required_item = False
                environmental_actions = {
                    "read",
                    "inspect",
                    "examine",
                    "look",
                    "push",
                    "pull",
                }
                for obj in req_objs:
                    if obj.upper() in self.inventory:
                        has_required_item = True
                        break
                    obj_clean = obj.lower().replace("_", " ")
                    if action in environmental_actions and obj_clean in text:
                        has_required_item = True
                        break
                if not has_required_item:
                    return f"{Prisma.SLATE}{(ux('gordon_strings', 'premise_req') or '').format(action=action, req_str=', '.join(req_objs))}{Prisma.RST}"
        environmental_verbs = {"read", "inspect", "examine", "look"}
        if any(v in tokens for v in self.interaction_verbs) and not any(
            v in tokens for v in environmental_verbs
        ):
            for i in self.registry:
                if i.upper() not in self.inventory:
                    i_low = i.lower().replace("_", " ")
                    i_words = i_low.split()
                    if all(w in tokens for w in i_words) and i_low in text:
                        return f"{Prisma.SLATE}{(ux('gordon_strings', 'premise_inv') or '').format(item=i_low)}{Prisma.RST}"
        return None

    @staticmethod
    def _clean_noun(raw_str: str) -> str:
        clean_str = re.sub(
            r"^(?:(?:it|this|that|them|him|her|up|out|off|down|in|on|the|a|an|some|my|and|or|but|then)\b\s*)+",
            "",
            raw_str,
            flags=re.IGNORECASE,
        ).strip()
        clean_str = re.split(
            r"\s+\b(?:and|or|but|then|to|with|because|please)\b", clean_str, maxsplit=1
        )[0].strip()
        clean_str = re.sub(
            r"\s+\b(?:of|in|on|at|to|for|with|from|instead|and|or|but|the|a|an|up|out|off|down|it|this|that|them|him|her)\b$",
            "",
            clean_str,
            flags=re.IGNORECASE,
        ).strip()
        return clean_str.strip(".,!?").upper().replace(" ", "_")

    def _resolve_pronoun(
        self,
        text_context: str,
        must_not_be_owned: bool = False,
        must_be_owned: bool = False,
    ) -> str:
        """Deterministically maps a pronoun to the most recently mentioned valid noun in the text context."""
        candidates = []
        for name in self.registry.keys():
            if must_not_be_owned and name in self.inventory:
                continue
            if must_be_owned and name not in self.inventory:
                continue
            clean_name = name.lower().replace("_", " ")
            matches = list(
                re.finditer(rf"\b{re.escape(clean_name)}\b", text_context.lower())
            )
            if matches:
                candidates.append((name, matches[-1].end()))
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        return ""

    def load_config(self):
        data = LoreManifest.get_instance().get("GORDON") or (
            LoreManifest.get_raw("gordon.json")
            if hasattr(LoreManifest, "get_raw")
            else {}
        )
        self.action_coupling = data.get("ACTION_COUPLING", {})
        self.location_coupling = data.get("LOCATION_COUPLING", {})
        self.refusal_markers = set(data.get("REFUSAL_MARKERS", []))
        self.creative_loot_triggers = data.get("CREATIVE_LOOT_TRIGGERS", [])
        if self.mode in ["CREATIVE", "CONVERSATION"]:
            self.loot_triggers = self.creative_loot_triggers
        else:
            self.loot_triggers = data.get("LOOT_TRIGGERS", [])
        self.interaction_verbs = sorted(
            data.get("INTERACTION_VERBS", []), key=len, reverse=True
        )
        self.acquisition_verbs = sorted(
            data.get("ACQUISITION_VERBS", []), key=len, reverse=True
        )
        lexicon_data = LoreManifest.get_instance().get("LEXICON") or {}
        if not lexicon_data and hasattr(LoreManifest, "get_raw"):
            lexicon_data = LoreManifest.get_raw("lexicon.json") or {}
        self.abandonment_phrases = lexicon_data.get(
            "abandonment_phrases", ["put back", "leave", "drop", "ignore"]
        )
        self.blueprints = LoreManifest.get_instance().get("ITEM_GENERATION") or {}
        self.ITEM_REGISTRY = data.get("ITEM_REGISTRY", {})
        for name, props in self.ITEM_REGISTRY.items():
            self.registry[name] = Item.from_dict(name, props)
        self.recipes = data.get("RECIPES", [])
        self.scar_tissue = data.get("SCAR_TISSUE", {})
        starters = data.get("STARTING_INVENTORY", [])
        if not self.inventory and starters:
            self.inventory = [s for s in starters if isinstance(s, str)]
        inv_cfg = safe_get(self.cfg, "INVENTORY", {})
        self.max_slots = int(safe_get(inv_cfg, "MAX_SLOTS", 10))

    def process_loot_tags(self, text: str, user_input: str) -> Tuple[str, List[str]]:
        raw_loot = re.findall(r"\[\[LOOT:\s*(.*?)]]", text, re.IGNORECASE)
        raw_lost = re.findall(r"\[\[LOST:\s*(.*?)]]", text, re.IGNORECASE)

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
            lower_input = user_input.lower()
            has_intent = any(
                re.search(rf"\b{re.escape(verb)}\b", lower_input)
                for verb in self.acquisition_verbs
            )
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
        clean_text = re.sub(
            r"\[\[(?:LOOT|LOST):\s*.*?]]", "", text, flags=re.IGNORECASE
        )
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

    def pack_item(self, item_name: str, container_name: str) -> Tuple[bool, str]:
        item_name, container_name = item_name.upper(), container_name.upper()
        if item_name not in self.inventory:
            return False, f"{Prisma.OCHRE}You do not have the {item_name}.{Prisma.RST}"
        if container_name not in self.inventory:
            return (
                False,
                f"{Prisma.OCHRE}You do not have the {container_name}.{Prisma.RST}",
            )
        if item_name == container_name:
            return (
                False,
                f"{Prisma.OCHRE}You cannot put an item inside itself.{Prisma.RST}",
            )
        container = self.get_item_data(container_name)
        if not container or not container.is_container:
            return (
                False,
                f"{Prisma.OCHRE}The {container_name} is not a container.{Prisma.RST}",
            )
        if len(container.contents) >= container.capacity:
            return False, f"{Prisma.OCHRE}The {container_name} is full.{Prisma.RST}"
        self.inventory.remove(item_name)
        container.contents.append(item_name)
        if item := self.get_item_data(item_name):
            item.location = container_name
        return (
            True,
            f"{Prisma.CYN}► Packed {item_name} into {container_name}.{Prisma.RST}",
        )

    def unpack_item(self, item_name: str, container_name: str) -> Tuple[bool, str]:
        item_name, container_name = item_name.upper(), container_name.upper()
        if container_name not in self.inventory:
            return (
                False,
                f"{Prisma.OCHRE}You do not have the {container_name}.{Prisma.RST}",
            )
        container = self.get_item_data(container_name)
        if not container or not container.is_container:
            return (
                False,
                f"{Prisma.OCHRE}The {container_name} is not a container.{Prisma.RST}",
            )
        if item_name not in container.contents:
            return (
                False,
                f"{Prisma.OCHRE}The {item_name} is not inside the {container_name}.{Prisma.RST}",
            )
        if len(self.inventory) >= self.max_slots:
            return (
                False,
                f"{Prisma.OCHRE}Inventory full. Cannot unpack {item_name}.{Prisma.RST}",
            )
        container.contents.remove(item_name)
        self.inventory.append(item_name)
        if item := self.get_item_data(item_name):
            item.location = "inventory"
        return (
            True,
            f"{Prisma.CYN}► Unpacked {item_name} from {container_name}.{Prisma.RST}",
        )

    def process_container_commands(self, text: str) -> Tuple[List[str], bool]:
        logs = []
        handled = False
        lower_text = text.lower()
        put_match = re.search(
            r"\b(?:put|place|store|stash)\s+(?:the|a|an|some|my)?\s*(.*?)\s+(?:in|inside|into)\s+(?:the|a|an|my)?\s*(.*)",
            lower_text,
        )
        if put_match:
            raw_item = put_match.group(1).upper()
            item_clean = self._clean_noun(put_match.group(1))
            container_clean = self._clean_noun(put_match.group(2))
            if not item_clean and any(
                p in raw_item.split() for p in {"IT", "THIS", "THAT", "THEM"}
            ):
                item_clean = self._resolve_pronoun(text, must_be_owned=True)
            if item_clean and container_clean:
                success, msg = self.pack_item(item_clean, container_clean)
                if success or "not a container" in msg or "full" in msg:
                    logs.append(msg)
                    handled = True
        take_match = re.search(
            r"\b(?:take|remove|get|pull)\s+(?:the|a|an|some|my)?\s*(.*?)\s+(?:from|out of)\s+(?:the|a|an|my)?\s*(.*)",
            lower_text,
        )
        if take_match:
            raw_item = take_match.group(1).upper()
            item_clean = self._clean_noun(take_match.group(1))
            container_clean = self._clean_noun(take_match.group(2))
            if not item_clean and any(
                p in raw_item.split() for p in {"IT", "THIS", "THAT", "THEM"}
            ):
                item_clean = self._resolve_pronoun(text)
            if item_clean and container_clean:
                success, msg = self.unpack_item(item_clean, container_clean)
                if success or "not inside" in msg:
                    logs.append(msg)
                    handled = True
        return logs, handled

    def acquire(self, tool_name: str) -> str:
        tool_name = (
            tool_name.strip().upper().replace(" ", "_") if tool_name else "UNKNOWN"
        )
        if tool_name in self.inventory:
            msg = ux("gordon_strings", "inv_duplicate")
            return f"{Prisma.OCHRE}{msg.format(item=tool_name)}{Prisma.RST}"
        if not (self.get_item_data(tool_name) or self.get_item_data(tool_name.lower())):
            is_cont = any(
                word in tool_name
                for word in ["POUCH", "BAG", "BOX", "SATCHEL", "CASE", "PACK"]
            )
            new_item = Item(
                name=tool_name,
                description=ux("gordon_strings", "fallback_desc") or "???",
                function="MISC",
                is_container=is_cont,
            )
            self.registry[tool_name] = new_item
        if len(self.inventory) >= self.max_slots:
            msg = (
                ux("gordon_strings", "inv_full_reject")
                or "Inventory full. Cannot acquire {item}."
            )
            if self.events:
                self.events.log(msg.format(item=tool_name), "INV")
            return f"{Prisma.OCHRE}{msg.format(item=tool_name)}{Prisma.RST}"
        self.inventory.append(tool_name)
        if item := self.get_item_data(tool_name):
            item.location = "inventory"
        if self.events:
            self.events.publish("ITEM_ACQUIRED", {"item": tool_name})
        msg = ux("gordon_strings", "acquired")
        return f"{Prisma.GRN}{msg.format(item=tool_name)}{Prisma.RST}"

    def safe_remove_item(self, item_name: str, new_location: str = "VOID") -> bool:
        try:
            clean_name = item_name.upper()
            self.inventory.remove(clean_name)
            if item := self.get_item_data(clean_name):
                item.location = new_location
            return True
        except ValueError:
            return False

    def rummage(self, physics_ref: Any, stamina_pool: float) -> Tuple[bool, str, float]:
        inv_cfg = safe_get(self.cfg, "INVENTORY", {})
        cost = float(safe_get(inv_cfg, "RUMMAGE_COST", 15.0))
        if stamina_pool < cost:
            return (
                False,
                f"{Prisma.OCHRE}{ux('gordon_strings', 'rummage_tired')}{Prisma.RST}",
                0.0,
            )
        loot_table = self._get_loot_candidates(physics_ref)
        if not loot_table:
            return (
                False,
                f"{Prisma.GRY}{ux('gordon_strings', 'rummage_empty')}{Prisma.RST}",
                cost,
            )
        return True, self.acquire(random.choice(loot_table)), cost

    def _get_loot_candidates(self, physics: Any) -> List[str]:
        v = float(safe_get(physics, "voltage", 0.0))
        d = float(safe_get(physics, "narrative_drag", 0.0))
        p = float(safe_get(physics, "psi", 0.0))
        cfg = safe_get(self.cfg, "PHYSICS", {})
        vh = float(safe_get(cfg, "VOLTAGE_HIGH", 12.0))
        vc = float(safe_get(cfg, "VOLTAGE_CRITICAL", 15.0))
        dh = float(safe_get(cfg, "DRAG_HEAVY", 5.0))
        ph = float(safe_get(cfg, "PSI_HIGH", 0.6))
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
                self.events.log(
                    f"{Prisma.CYN}{msg.format(name=name)}{Prisma.RST}", "INV"
                )

    def synthesize_item(self, physics_vector: Dict[str, float]) -> str:
        if not self.blueprints:
            self.blueprints = LoreManifest.get_instance().get("ITEM_GENERATION") or {}
        bp = self.blueprints
        fb = bp.get("FALLBACKS", {})
        dom_dim = (
            max(physics_vector, key=lambda k: float(physics_vector[k]))
            if physics_vector
            else "ENT"
        )
        archetype = bp.get("DIM_MAP", {}).get(dom_dim, "void")
        prefixes = bp.get("PREFIXES", {}).get(archetype, fb.get("PREFIX", ["Strange"]))
        suffixes = bp.get("SUFFIXES", {}).get(
            archetype, fb.get("SUFFIX", ["of Mystery"])
        )
        bases_dict = bp.get("BASES", {})
        k_hash = getattr(
            getattr(self.events, "telemetry", None), "kernel_hash", "UNKNOWN"
        )
        seed_val = f"{k_hash}_{len(self.registry)}_{physics_vector.get(dom_dim, 0.0)}"
        rng = random.Random(seed_val)

        if self.mode in ["CREATIVE", "CONVERSATION"]:
            base_cat = bp.get("CREATIVE_BASE_CAT", "ABSTRACT")
            bases = bases_dict.get(base_cat, fb.get("BASE", ["Concept"]))
            overrides = bp.get("CREATIVE_OVERRIDES", {})
            prefixes = overrides.get("PREFIXES") or prefixes
            suffixes = overrides.get("SUFFIXES") or suffixes
        else:
            adv_cats = bp.get("ADVENTURE_CATEGORIES", ["TOOL", "JUNK", "ARTIFACT"])
            bases = bases_dict.get(rng.choice(adv_cats), fb.get("BASE", ["Object"]))
        base = rng.choice(bases)
        prefix = rng.choice(prefixes)
        suffix = rng.choice(suffixes)
        full_name = f"{prefix} {base} {suffix}"
        clean_id = full_name.upper().replace(" ", "_")
        clamped_value = min(100.0, round(physics_vector.get(dom_dim, 0.0) * 10, 1))
        item_data = {
            "description": ux_format(
                "gordon_strings",
                "synthesis_desc",
                default="A {base} forged of {archetype} energy.",
                base=base.lower(),
                archetype=archetype,
            ),
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
        lower_user = user_text.lower()
        if "system_init" in lower_user or "system_boot" in lower_user:
            return None
        valid_triggers = [t for t in self.loot_triggers if t in combined_text]
        if valid_triggers:
            present_candidates = []
            for name in self.registry.keys():
                if name.upper() not in self.inventory:
                    clean = name.lower().replace("_", " ")
                    if clean in combined_text and re.search(
                        rf"\b{re.escape(clean)}\b", combined_text
                    ):
                        present_candidates.append((name, clean))
            if present_candidates:
                for t in sorted(valid_triggers, key=len, reverse=True):
                    t_str = str(t)
                    t_escaped = re.escape(t_str)
                    for name, clean in present_candidates:
                        if re.search(
                            rf"\b{t_escaped}\b.*?\b{re.escape(clean)}\b",
                            combined_text,
                            re.IGNORECASE,
                        ):
                            return name
        for verb in self.acquisition_verbs:
            verb_str = str(verb)
            match = re.search(
                rf"\b{re.escape(verb_str)}\s+(?:up|out|off|down|in|on|from)?\s*(?:the|a|an|some|my)?\s*([a-z0-9\'\-]+(?:\s+[a-z0-9\'\-]+){{0,3}})",
                lower_user,
            )
            if match:
                raw_target = match.group(1).upper()
                clean_extracted = self._clean_noun(match.group(1))
                invalid_nouns = {
                    "IT",
                    "THIS",
                    "THAT",
                    "THEM",
                    "HIM",
                    "HER",
                    "THERE",
                    "ALL",
                    "SOME",
                    "MORE",
                    "TAKE",
                    "GET",
                    "DROP",
                    "LEAVE",
                    "PICK",
                    "PULL",
                    "PUT",
                    "USE",
                }

                if not clean_extracted and any(
                    p in raw_target.split()
                    for p in {"IT", "THIS", "THAT", "THEM", "HIM", "HER"}
                ):
                    resolved = self._resolve_pronoun(
                        combined_text, must_not_be_owned=True
                    )
                    if resolved:
                        return resolved

                if len(clean_extracted) > 2 and clean_extracted not in invalid_nouns:
                    if clean_extracted not in self.inventory:
                        return clean_extracted
        return None

    def consume(self, item_name: str) -> Tuple[bool, str]:
        item_name = item_name.upper()
        if item_name not in self.inventory:
            return (
                False,
                f"{Prisma.OCHRE}{ux('gordon_strings', 'consume_missing')}{Prisma.RST}",
            )
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
        cfg = safe_get(self.cfg, "INVENTORY", {})
        v = float(safe_get(physics_ref, "voltage", 0.0))
        d = float(safe_get(physics_ref, "narrative_drag", 0.0))
        k = float(safe_get(physics_ref, "kappa", 0.5))
        for name in tuple(self.inventory):
            item = self.get_item_data(name)
            if not item or not item.reflex_trigger:
                continue
            trigger_type = item.reflex_trigger
            if trigger_type == "VOLTAGE_CRITICAL" and v > float(
                safe_get(cfg, "REFLEX_VOLTAGE_TRIGGER", 18.0)
            ):
                self.safe_remove_item(name)
                safe_set(
                    physics_ref,
                    "voltage",
                    float(safe_get(cfg, "REFLEX_VOLTAGE_RESET", 12.0)),
                )
                return (
                    True,
                    f"{Prisma.CYN}{(ux('gordon_strings', 'reflex_voltage') or '').format(name=name)}{Prisma.RST}",
                )
            if trigger_type == "DRIFT_CRITICAL" and d > float(
                safe_get(cfg, "REFLEX_DRAG_TRIGGER", 6.0)
            ):
                self.safe_remove_item(name)
                safe_set(
                    physics_ref,
                    "narrative_drag",
                    float(safe_get(cfg, "REFLEX_DRAG_RESET", 0.0)),
                )
                return (
                    True,
                    f"{Prisma.OCHRE}{(ux('gordon_strings', 'reflex_drift') or '').format(name=name)}{Prisma.RST}",
                )
            if trigger_type == "KAPPA_CRITICAL" and k < float(
                safe_get(cfg, "REFLEX_KAPPA_TRIGGER", 0.2)
            ):
                self.safe_remove_item(name)
                safe_set(
                    physics_ref,
                    "kappa",
                    float(safe_get(cfg, "REFLEX_KAPPA_RESET", 0.8)),
                )
                return (
                    True,
                    f"{Prisma.GRN}{(ux('gordon_strings', 'reflex_kappa') or '').format(name=name)}{Prisma.RST}",
                )
        return False, None

    def export_fractal_state(
        self, cartographer_ref=None, title="BoneAmanita Manifest"
    ) -> str:
        fractal: Dict[str, Any] = {
            "title": title,
            "startingRoomId": cartographer_ref.current_node_id
            if cartographer_ref
            else "GENESIS_POINT",
            "winCondition": {"type": "none"},
            "rooms": {},
            "items": {},
            "npcs": {},
        }
        if cartographer_ref:
            for node_id, node in cartographer_ref.world_graph.items():
                fractal["rooms"][node_id] = {
                    "id": node_id,
                    "name": node.name,
                    "description": f"{node.atmosphere} {node.smell}",
                    "exits": {},
                }
        for name, item in self.registry.items():
            clean_id = name.lower().replace(" ", "_")
            fractal["items"][clean_id] = {
                "id": clean_id,
                "name": item.name.lower().replace("_", " "),
                "noun": clean_id.split("_")[-1],
                "description": item.description,
                "location": item.location,
                "canTake": not item.is_container,
                "isContainer": item.is_container,
                "contains": [c.lower().replace(" ", "_") for c in item.contents],
            }
        return json.dumps(fractal, indent=2)
