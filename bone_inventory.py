import random, re
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from bone_core import LoreManifest
from bone_types import Prisma
from bone_config import BoneConfig


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
        return cls(
            name=name,
            description=data.get("description", "Unknown Artifact"),
            function=data.get("function", "MISC"),
            passive_traits=data.get("passive_traits", []),
            spawn_context=data.get("spawn_context", "COMMON"),
            value=data.get("value", 1.0),
            usage_msg=data.get("usage_msg", f"You use the {name}."),
            consume_on_use=data.get("consume_on_use", False),
            reflex_trigger=data.get("reflex_trigger", None),
        )


class GordonKnot:
    def __init__(self, events=None):
        self.events = events
        self.inventory: List[str] = []
        self.registry: Dict[str, Item] = {}
        self.ITEM_REGISTRY: Dict[str, Dict] = {}
        self.recipes: List[Dict] = []
        self.max_slots = 10
        self.last_flinch_turn = -100
        self.scar_tissue = {}
        self.refusal_markers = {
            "cannot",
            "can't",
            "unable",
            "fail",
            "too heavy",
            "stuck",
            "don't",
            "do not",
            "locked",
            "refuse",
            "impossible",
        }
        self.loot_triggers = [
            "found a",
            "picked up",
            "pick up",
            "acquired",
            "took the",
            "take the",
            "grab the",
            "takes the",
        ]
        self.load_config()

    def load_config(self):
        data = LoreManifest.get_instance().get("GORDON") or {}
        if not data and hasattr(LoreManifest, "get_raw"):
            data = LoreManifest.get_raw("gordon.json") or {}
        if "REFUSAL_MARKERS" in data:
            self.refusal_markers = set(data["REFUSAL_MARKERS"])
        if "LOOT_TRIGGERS" in data:
            self.loot_triggers = data["LOOT_TRIGGERS"]
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
        loot_pattern = r"\[\[LOOT:\s*(.*?)\]\]"
        lost_pattern = r"\[\[LOST:\s*(.*?)\]\]"
        raw_loot = re.findall(loot_pattern, text, re.IGNORECASE)
        raw_lost = re.findall(lost_pattern, text, re.IGNORECASE)

        def normalize(items):
            clean_set = set()
            for normalized_item in items:
                clean = normalized_item.strip().upper().replace(" ", "_")
                clean = re.sub(r"[^A-Z0-9_]", "", clean)
                if clean:
                    clean_set.add(clean)
            return list(clean_set)

        new_loot = normalize(raw_loot)
        lost_loot = normalize(raw_lost)
        logs = []
        if new_loot:
            acquisition_verbs = [
                "take",
                "grab",
                "pick",
                "get",
                "steal",
                "seize",
                "collect",
                "snatch",
                "acquire",
                "pocket",
                "loot",
                "harvest",
            ]
            clean_input = user_input.lower()
            has_intent = any(verb in clean_input for verb in acquisition_verbs)
            if has_intent:
                for item in new_loot:
                    logs.append(self.acquire(item))
                    if self.events:
                        self.events.publish("ITEM_ACQUIRED", {"item": item})
            else:
                if self.events:
                    for item in new_loot:
                        self.events.log(
                            f"CONSENT: Intercepted auto-loot for '{item}'. User did not ask.",
                            "GORDON",
                        )
        for item in lost_loot:
            if self.safe_remove_item(item):
                logs.append(f"{Prisma.GRY}ENTROPY: {item} consumed/lost.{Prisma.RST}")
            else:
                logs.append(
                    f"{Prisma.OCHRE}GLITCH: Tried to lose {item}, but you didn't have it.{Prisma.RST}"
                )
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
        data = []
        for name in self.inventory:
            item = self.get_item_data(name)
            if item:
                data.append(item.__dict__)
        return data

    def acquire(self, tool_name: str) -> str:
        tool_name = tool_name.upper() if tool_name else "UNKNOWN"
        if tool_name in self.inventory:
            return f"{Prisma.OCHRE}Inventory duplicate: You already have the {tool_name}.{Prisma.RST}"
        item_obj = self.get_item_data(tool_name)
        if not item_obj:
            item_obj = self.get_item_data(tool_name.lower())
        if not item_obj:
            new_item = Item(name=tool_name, description="???", function="MISC")
            self.registry[tool_name] = new_item
            self.ITEM_REGISTRY[tool_name] = new_item.__dict__
        if len(self.inventory) >= self.max_slots:
            dropped = self.inventory.pop(0)
            if self.events:
                self.events.log(f"Inventory full. Dropped {dropped}.", "INV")
        self.inventory.append(tool_name)
        if self.events:
            self.events.publish("ITEM_ACQUIRED", {"item": tool_name})
        return f"{Prisma.GRN}📦 ACQUIRED: {tool_name}{Prisma.RST}"

    def safe_remove_item(self, item_name: str) -> bool:
        item_name = item_name.upper()
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            return True
        return False

    def rummage(
        self, physics_ref: Dict, stamina_pool: float
    ) -> Tuple[bool, str, float]:
        cost = 15.0
        if hasattr(BoneConfig, "INVENTORY"):
            cost = getattr(BoneConfig.INVENTORY, "RUMMAGE_COST", 15.0)
        if stamina_pool < cost:
            return (
                False,
                f"{Prisma.OCHRE}Gordon sighs. 'Too tired. Eat first.'{Prisma.RST}",
                0.0,
            )
        loot_table = self._get_loot_candidates(physics_ref)
        if not loot_table:
            return False, "Gordon dug deep but found only lint.", cost
        found_item = random.choice(loot_table)
        msg = self.acquire(found_item)
        return True, msg, cost

    def _get_loot_candidates(self, physics: Dict) -> List[str]:
        candidates = []
        voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        psi = physics.get("psi", 0.0)
        all_keys = set(self.registry.keys()) | set(self.ITEM_REGISTRY.keys())
        for name in all_keys:
            item = self.get_item_data(name)
            if not item:
                continue
            ctx = item.spawn_context
            if ctx in ["COMMON", "STANDARD"]:
                candidates.append(name)
            elif ctx == "VOLTAGE_HIGH" and voltage > 12.0:
                candidates.append(name)
            elif ctx == "VOLTAGE_CRITICAL" and voltage > 18.0:
                candidates.append(name)
            elif ctx == "DRAG_HEAVY" and drag > 4.0:
                candidates.append(name)
            elif ctx == "PSI_HIGH" and psi > 0.6:
                candidates.append(name)
        return candidates

    def register_dynamic_item(self, name: str, data: Dict):
        name = name.upper()
        if name not in self.registry:
            new_item = Item.from_dict(name, data)
            self.registry[name] = new_item
            if self.events:
                self.events.log(
                    f"{Prisma.CYN}🎒 GORDON: 'I'll make space for {name}.'{Prisma.RST}",
                    "INV",
                )

    def synthesize_item(self, physics_vector: Dict[str, float]) -> str:
        if not hasattr(self, "blueprints") or not self.blueprints:
            self.blueprints = LoreManifest.get_instance().get("ITEM_GENERATION") or {}
            
        dim_map = {
            "STR": "heavy", "VEL": "kinetic", "PHI": "thermal", 
            "PSI": "abstract", "ENT": "void", "BET": "constructive"
        }
        dom_dim = max(physics_vector, key=physics_vector.get) if physics_vector else "ENT"
        archetype = dim_map.get(dom_dim, "void")
        prefixes = self.blueprints.get("PREFIXES", {}).get(archetype, ["Strange"])
        suffixes = self.blueprints.get("SUFFIXES", {}).get(archetype, ["of Mystery"])
        base_cat = random.choice(["TOOL", "JUNK", "ARTIFACT"])
        bases = self.blueprints.get("BASES", {}).get(base_cat, ["Object"])
        prefix = random.choice(prefixes)
        base = random.choice(bases)
        suffix = random.choice(suffixes)
        full_name = f"{prefix} {base} {suffix}"
        clean_id = full_name.upper().replace(" ", "_")
        item_data = {
            "description": f"A {base.lower()} manifesting {archetype} properties.",
            "function": "ARTIFACT",
            "passive_traits": ["DYNAMIC"],
            "value": round(physics_vector.get(dom_dim, 0.0) * 10, 1),
            "spawn_context": "FORGED"
        }
        self.register_dynamic_item(clean_id, item_data)
        return clean_id

    def parse_loot(self, user_text: str, sys_text: str) -> Optional[str]:
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
                pattern = f"{re.escape(t)}\\s+(?:the\\s+|a\\s+|an\\s+)?(?P<item>[\\w\\s]{{1,30}}?)(?:\\s+(?:you|it|he|she|we|they)|[\\.,!?]|$)"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    candidate = match.group("item").strip()
                    if (
                        2 < len(candidate) < 40
                        and candidate not in self.refusal_markers
                    ):
                        return candidate
        return None

    def consume(self, item_name: str) -> Tuple[bool, str]:
        item_name = item_name.upper()
        if item_name not in self.inventory:
            return False, "You don't have that."
        item = self.get_item_data(item_name)
        if not item or not item.consume_on_use:
            return False, f"The {item_name} cannot be consumed."
        self.inventory.remove(item_name)
        if item.function == "STABILITY":
            return True, f"🍕 {item_name}: Entropy paused. Satisfaction nominal."
        return True, f"Consumed {item_name}. {item.usage_msg}"

    def emergency_reflex(self, physics_ref: Dict) -> Tuple[bool, Optional[str]]:
        voltage = physics_ref.get("voltage", 0.0)
        drag = physics_ref.get("narrative_drag", 0.0)
        for name in self.inventory:
            item = self.get_item_data(name)
            if not item:
                continue
            trigger = item.reflex_trigger
            if trigger == "VOLTAGE_CRITICAL" and voltage > 18.0:
                self.safe_remove_item(name)
                physics_ref["voltage"] = 12.0
                return (
                    True,
                    f"{Prisma.CYN}🛡️ REFLEX: {name} sacrificed to absorb voltage spike! (Voltage -> 12.0v){Prisma.RST}",
                )
            if trigger == "DRIFT_CRITICAL" and drag > 6.0:
                self.safe_remove_item(name)
                physics_ref["narrative_drag"] = 0.0
                return (
                    True,
                    f"{Prisma.OCHRE}⚓ REFLEX: {name} deployed. Drag zeroed out.{Prisma.RST}"
                )
            kappa = physics_ref.get("kappa", 0.5)
            if trigger == "KAPPA_CRITICAL" and kappa < 0.2:
                self.safe_remove_item(name)
                physics_ref["kappa"] = 0.8
                return (
                    True,
                    f"{Prisma.GRN}🍕 REFLEX: {name} consumed. Structure restored.{Prisma.RST}"
                )
        return False, None
