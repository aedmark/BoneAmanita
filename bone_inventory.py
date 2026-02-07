""" bone_inventory.py
 'Organization is the first step toward civilization.' - Schur """

import random, copy
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, cast, Callable
from enum import Enum, auto
from bone_core import Prisma, BoneConfig, TheLore

class EffectType(Enum):
    PHYSICS = auto()
    SEMANTIC = auto()
    HYBRID = auto()

@dataclass
class ItemEffect:
    effect_type: EffectType
    physics_handler: Optional[Any] = None
    semantic_instr: Optional[str] = None
    priority: int = 50

@dataclass
class PhysicsDelta:
    operator: str
    field: str
    value: Any
    message: Optional[str] = None

UNKNOWN_ARTIFACT = {
    "description": "Unknown Artifact",
    "function": "MISC",
    "usage_msg": "It does nothing."}

@dataclass
class TensegrityState:
    mass: float = 0.0
    lift: float = 0.0
    volume: float = 0.0
    is_collapsed: bool = False

def effect_conductive(physics: Dict, _data: Dict, item_name: str) -> List[PhysicsDelta]:
    voltage = physics.get("voltage", 0.0)
    limit = BoneConfig.INVENTORY.CONDUCTIVE_THRESHOLD
    if voltage > limit:
        damage = voltage * 0.5
        msg = f"{Prisma.RED}CONDUCTIVE HAZARD: {item_name} acts as a lightning rod! -{damage:.1f} HP.{Prisma.RST}"
        return [PhysicsDelta("ADD", "pain_signal", damage, msg)]
    return []

def effect_heavy_load(physics: Dict, _data: Dict, item_name: str) -> List[PhysicsDelta]:
    limit = BoneConfig.INVENTORY.HEAVY_LOAD_THRESHOLD
    if physics.get("narrative_drag", 0.0) > limit:
        msg = f"{Prisma.GRY}HEAVY LOAD: The {item_name} are dragging you down.{Prisma.RST}"
        return [PhysicsDelta("noop", "", 0, msg)]
    return []

def effect_time_cap(physics: Dict, data: Dict, item_name: str) -> List[PhysicsDelta]:
    current_drag = physics.get("narrative_drag", 0.0)
    cap = data.get("value", 5.0)
    if current_drag > cap:
        msg = f"{Prisma.CYN}TIME DILATION: {item_name} hums. Drag capped at {cap}.{Prisma.RST}"
        return [PhysicsDelta("SET", "narrative_drag", cap, msg)]
    return []

def effect_bureaucratic_anchor(physics: Dict, _data: Dict, item_name: str) -> List[PhysicsDelta]:
    if physics.get("beta_index", 0) < 1.0:
        msg = f"{Prisma.GRY}{item_name}: Policy enforced. (Beta +0.2, Drag +0.5){Prisma.RST}"
        return [
            PhysicsDelta("ADD", "beta_index", 0.2, msg),
            PhysicsDelta("ADD", "narrative_drag", 0.5)]
    return []

def effect_grounding_gear(physics: Dict, _data: Dict, item_name: str) -> List[PhysicsDelta]:
    zone = physics.get("zone", "COURTYARD")
    if zone in ["AERIE", "VOID_DRIFT"]:
        msg = f"{Prisma.OCHRE}{item_name}: Gravity re-asserted. You sink out of the {zone} into the Mud.{Prisma.RST}"
        return [
            PhysicsDelta("SET_ZONE", "zone", "THE_MUD", msg),
            PhysicsDelta("ADD", "narrative_drag", 2.0),
            PhysicsDelta("ADD", "voltage", -2.0)]
    return []

def effect_safety_scissors(physics: Dict, _data: Dict, item_name: str) -> List[PhysicsDelta]:
    counts = physics.get("counts", {})
    suburban = counts.get("suburban", 0)
    if suburban > 2:
        msg = f"{Prisma.CYN}{item_name}: Gordon snips the red tape. {suburban} suburban words discarded.{Prisma.RST}"
        return [PhysicsDelta("SET_COUNT", "suburban", 0, msg)]
    return []

def effect_caffeine_drip(physics: Dict, _data: Dict, _item_name: str) -> List[PhysicsDelta]:
    deltas = []
    current_vel = physics.get("vector", {}).get("VEL", 0)
    if current_vel < 1.0:
        deltas.append(PhysicsDelta("ADD_VECTOR", "VEL", 0.1))
    if random.random() < 0.2:
        msg = f"{Prisma.CYN}CAFFEINE JITTERS: Velocity UP, Stability DOWN.{Prisma.RST}"
        deltas.append(PhysicsDelta("ADD", "turbulence", 0.2, msg))
    return deltas

def effect_apology_eraser(physics: Dict, _data: Dict, item_name: str) -> List[PhysicsDelta]:
    clean = physics.get("clean_words", [])
    if "sorry" in clean or "apologize" in clean:
        msg = f"{Prisma.GRY}{item_name}: Gordon paints over the apology. 'Don't be sorry. Be better.'{Prisma.RST}"
        return [PhysicsDelta("noop", "", 0, msg)]
    return []

def effect_sync_check(physics: Dict, _data: Dict, item_name: str) -> List[PhysicsDelta]:
    tick = physics.get("tick_count", 0)
    voltage = physics.get("voltage", 0.0)
    if str(tick).endswith("11") or abs(voltage - 11.1) < 0.1:
        msg = f"{Prisma.CYN}{item_name}: The hands align. 11:11. Synchronicity achieved.{Prisma.RST}"
        return [
            PhysicsDelta("SET", "narrative_drag", 0.0, msg),
            PhysicsDelta("SET", "voltage", 11.1)]
    return []

def effect_organize_chaos(physics: Dict, _data: Dict, _item_name: str) -> List[PhysicsDelta]:
    turb = physics.get("turbulence", 0.0)
    if turb > 0.2:
        msg = f"{Prisma.CYN}TRAPPERKEEPER PROTOCOL: Chaos filed under 'T' for 'Tamed'. (Turbulence -0.2){Prisma.RST}"
        return [PhysicsDelta("ADD", "turbulence", -0.2, msg)]
    return []

def effect_psi_anchor(physics: Dict, _data: Dict, _item_name: str) -> List[PhysicsDelta]:
    current_psi = physics.get("psi", 0.0)
    dist_from_mean = abs(current_psi - 0.5)
    if dist_from_mean > 0.3:
        correction = 0.1 if current_psi < 0.5 else -0.1
        msg = f"{Prisma.MAG}TINY HORSE: You catch a glimpse of the plushie. You feel grounded. (Psi {correction:+.1f}){Prisma.RST}"
        return [PhysicsDelta("ADD", "psi", correction, msg)]
    return []

def effect_luminescence(physics: Dict, _data: Dict, _item_name: str) -> List[PhysicsDelta]:
    return [
        PhysicsDelta("ADD", "voltage", 0.5),
        PhysicsDelta("ADD", "psi", 0.05, message=None)]

def _init_trait_registry() -> Dict[str, ItemEffect]:
    r = {"CONDUCTIVE_HAZARD": ItemEffect(EffectType.PHYSICS, effect_conductive),
         "HEAVY_LOAD": ItemEffect(EffectType.PHYSICS, effect_heavy_load),
         "GROUNDING_GEAR": ItemEffect(EffectType.PHYSICS, effect_grounding_gear),
         "SYNCHRONICITY_CHECK": ItemEffect(EffectType.PHYSICS, effect_sync_check),
         "ORGANIZE_CHAOS": ItemEffect(EffectType.PHYSICS, effect_organize_chaos),
         "PSI_ANCHOR": ItemEffect(EffectType.PHYSICS, effect_psi_anchor), "LUMINESCENCE": ItemEffect(
            EffectType.HYBRID,
            physics_handler=effect_luminescence,
            semantic_instr="VISUAL: The scene is lit by a cold, unwavering light."
        ), "APOLOGY_ERASER": ItemEffect(EffectType.PHYSICS, effect_apology_eraser), "TIME_DILATION_CAP": ItemEffect(
            EffectType.HYBRID,
            physics_handler=effect_time_cap,
            semantic_instr="STYLE: Describe events in slow motion, focusing on minute sensory details."
        ), "BUREAUCRATIC_ANCHOR": ItemEffect(
            EffectType.HYBRID,
            physics_handler=effect_bureaucratic_anchor,
            semantic_instr="STYLE: Use formal, procedural language. Cite non-existent regulations."
        ), "CUT_THE_CRAP": ItemEffect(
            EffectType.HYBRID,
            physics_handler=effect_safety_scissors,
            semantic_instr="CONSTRAINT: Prune all adjectives. Write in sparse, staccato sentences.",
            priority=10
        ), "CAFFEINE_DRIP": ItemEffect(
            EffectType.HYBRID,
            physics_handler=effect_caffeine_drip,
            semantic_instr="TONE: Jittery, fast-paced, and slightly anxious."
        ), "ILLUMINATION": ItemEffect(
            EffectType.SEMANTIC,
            semantic_instr="FOCUS: Reveal hidden truths. Ignore surface appearances. Highlight subtext.")}
    return r

TRAIT_REGISTRY = _init_trait_registry()

@dataclass
class GordonKnot:
    integrity: float = 65.0
    inventory: List[str] = field(default_factory=list)
    scar_tissue: Dict[str, float] = field(default_factory=dict)
    last_flinch_turn: int = -10
    physics_state: TensegrityState = field(default_factory=TensegrityState)
    events: Optional[Any] = field(default=None, repr=False)
    active_effect_cache: List[Tuple] = field(default_factory=list, init=False)
    ITEM_REGISTRY: Dict = field(default_factory=dict, init=False)
    CRITICAL_ITEMS: set = field(default_factory=set, init=False)
    REFLEX_MAP: Dict = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.load_config()
        self._initialize_reflexes()
        self._recalculate_tensegrity()

    @property
    def pain_memory(self) -> set:
        return set(self.scar_tissue.keys())

    def _enforce_slot_limits(self):
        limit = BoneConfig.INVENTORY.MAX_SLOTS
        if len(self.inventory) <= limit:
            return
        droppable = [i for i in self.inventory if i not in self.CRITICAL_ITEMS]
        while len(self.inventory) > limit and droppable:
            victim = random.choice(droppable)
            self.inventory.remove(victim)
            droppable.remove(victim)
        self._recalculate_tensegrity()

    def load_config(self):
        gordon_data = TheLore.get("GORDON") or {}
        starting_gear = gordon_data.get("STARTING_INVENTORY", [])
        if not starting_gear:
            starting_gear = ["SILENT_KNIFE"]
        if not self.inventory or self.inventory == ["POCKET_ROCKS"]:
            self.inventory = list(starting_gear)
        if "SKELETON_KEY" in self.inventory:
            self.inventory.remove("SKELETON_KEY")
        self.CRITICAL_ITEMS = {"SILENT_KNIFE"}
        for crit in self.CRITICAL_ITEMS:
            if crit not in self.inventory:
                self.inventory.append(crit)
        default_scars = gordon_data.get("SCAR_TISSUE", {})
        if not self.scar_tissue:
            self.scar_tissue = default_scars
        raw_registry = gordon_data.get("ITEM_REGISTRY", {})
        self.ITEM_REGISTRY = copy.deepcopy(raw_registry)
        if "SKELETON_KEY" not in self.ITEM_REGISTRY:
            self.ITEM_REGISTRY["SKELETON_KEY"] = {
                "description": "An iron key that feels cold to the touch. It opens things that shouldn't be shut.",
                "function": "UNLOCK",
                "reflex_trigger": "ACCESS_DENIED",
                "usage_msg": "Gordon unlocks the deadlock."}
        for name, data in self.ITEM_REGISTRY.items():
            data.setdefault("description", f"A mysterious {name.lower().replace('_', ' ')}.")
            data.setdefault("function", "NONE")
            data.setdefault("usage_msg", "It does nothing.")
            data.setdefault("passive_traits", [])
        self._enforce_slot_limits()

    def _initialize_reflexes(self):
        self.REFLEX_MAP = {
            "DRIFT_CRITICAL": lambda p: p.get("narrative_drag", 0) > 6.0,
            "KAPPA_CRITICAL": lambda p: p.get("kappa", 1.0) < 0.2,
            "BOREDOM_CRITICAL": lambda p: p.get("repetition", 0.0) > 0.5,
            "ACCESS_DENIED": lambda p: p.get("refusal_triggered", False) is True}

    def get_item_data(self, item_name: str) -> Dict:
        name_key = item_name.upper()
        if name_key in self.ITEM_REGISTRY:
            return self.ITEM_REGISTRY[name_key]
        plural_key = name_key + "S"
        if plural_key in self.ITEM_REGISTRY:
            parent_data = self.ITEM_REGISTRY[plural_key].copy()
            parent_data["description"] = f"{parent_data['description']} (Single)"
            parent_data["mass"] = parent_data.get("mass", 1.0) * 0.5
            return parent_data
        return {
            "description": f"An anomaly detected by the narrative. It appears to be a {item_name}.",
            "function": "NARRATIVE_ARTIFACT",
            "usage_msg": f"You use the {item_name}. The system isn't sure what happened, but it looked cool.",
            "mass": 1.0,
            "volume": 1.0,
            "passive_traits": []}

    def check_static_cling(self, physics_packet) -> Optional[str]:
        if isinstance(physics_packet, dict):
            em_field = physics_packet.get("electromagnetism", 0.0)
            if em_field == 0.0:
                import math
                e = physics_packet.get("E", 0.0)
                b = physics_packet.get("B", 0.0)
                em_field = math.sqrt(e**2 + b**2)
        else:
            em_field = getattr(physics_packet, "electromagnetism", 0.0)
        if em_field < 6.0:
            return None
        if not self.inventory:
            return f"{Prisma.VIOLET}*Sparks fly from your empty hands.*{Prisma.RST}"
        if random.random() < 0.3:
            item = random.choice(self.inventory)
            cling_msgs = [
                f"The {item} is stuck to your sleeve.",
                f"Static electricity crackles around the {item}.",
                f"The {item} floats momentarily in the magnetic field.",
                f"You feel the magnetic pull of the {item}."]
            return f"{Prisma.VIOLET}⚡ {random.choice(cling_msgs)}{Prisma.RST}"
        return None

    def _recalculate_tensegrity(self):
        total_mass = 0.0
        total_lift = 0.0
        total_vol = 0.0
        self.active_effect_cache = []
        for item_name in self.inventory:
            data = self.get_item_data(item_name)
            total_mass += data.get("mass", 1.0)
            total_lift += data.get("lift", 0.0)
            total_vol += data.get("volume", 1.0)
        collapsed = False
        if total_mass > 20.0 and total_mass > (total_lift * 3.0 + 10.0):
            collapsed = True
        self.physics_state = TensegrityState(
            mass=total_mass,
            lift=total_lift,
            volume=total_vol,
            is_collapsed=collapsed)

    def safe_remove_item(self, item_name: str) -> bool:
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            return True
        plural_key = item_name + "S"
        if plural_key in self.inventory:
            self.inventory.remove(plural_key)
            self.inventory.append(item_name)
            return True

        return False

    def audit_tools(self, physics_ref: Dict) -> List[str]:
        logs = []
        logs.extend(self._handle_environment(physics_ref))
        all_deltas = self._gather_passive_deltas(physics_ref)
        delta_logs = self._apply_physics_deltas(physics_ref, all_deltas)
        logs.extend(delta_logs)
        return logs

    def _handle_environment(self, physics_ref: Dict) -> List[str]:
        logs = []
        cling_msg = self.check_static_cling(physics_ref)
        if cling_msg:
            logs.append(cling_msg)
        turbulence = physics_ref.get("turbulence", 0.0)
        threshold = BoneConfig.INVENTORY.TURBULENCE_THRESHOLD
        if turbulence <= threshold:
            return logs
        if not self.inventory:
            return logs
        fumble_chance = BoneConfig.INVENTORY.TURBULENCE_FUMBLE_CHANCE
        if random.random() >= fumble_chance:
            return logs
        droppable = [i for i in self.inventory if i not in self.CRITICAL_ITEMS]
        if not droppable:
            return logs
        dropped = random.choice(droppable)
        if self.safe_remove_item(dropped):
            logs_data = TheLore.get("GORDON_LOGS") or {}
            templates = logs_data.get("FUMBLE", ["{item} fell."])
            msg = random.choice(templates).format(item=dropped)
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        return logs

    def _gather_passive_deltas(self, physics_ref: Dict) -> List[PhysicsDelta]:
        all_deltas = []
        for item_name in self.inventory:
            data = self.get_item_data(item_name)
            traits = data.get("passive_traits", [])
            for trait in traits:
                effect_def = TRAIT_REGISTRY.get(trait)
                if not effect_def:
                    continue
                if effect_def.effect_type not in [EffectType.PHYSICS, EffectType.HYBRID]:
                    continue
                handler = effect_def.physics_handler
                if handler is not None and callable(handler):
                    new_deltas = handler(physics_ref, data, item_name)
                    if new_deltas:
                        all_deltas.extend(new_deltas)
        return all_deltas

    def _apply_physics_deltas(self, physics_ref: Dict, deltas: List[PhysicsDelta]) -> List[str]:
        logs = []
        for delta in deltas:
            if delta.message:
                logs.append(delta.message)
            if delta.operator == "noop":
                continue
            self._execute_delta_op(physics_ref, delta)
        return logs

    def _execute_delta_op(self, physics_ref: Dict, delta: PhysicsDelta):
        op = delta.operator
        target_field = delta.field
        val = delta.value
        if op in ["ADD_COUNT", "SET_COUNT"] and "counts" not in physics_ref:
            physics_ref["counts"] = {}
        if op == "ADD_VECTOR" and "vector" not in physics_ref:
            physics_ref["vector"] = {}
        if op == "ADD":
            physics_ref[target_field] = physics_ref.get(target_field, 0.0) + val
        elif op == "SET":
            physics_ref[target_field] = val
        elif op == "MULTIPLY":
            physics_ref[target_field] = physics_ref.get(target_field, 0.0) * val
        elif op == "SET_ZONE":
            physics_ref["zone"] = str(val)
        elif op == "ADD_COUNT":
            physics_ref["counts"][target_field] = physics_ref["counts"].get(target_field, 0) + val
        elif op == "SET_COUNT":
            physics_ref["counts"][target_field] = val
        elif op == "ADD_VECTOR":
            physics_ref["vector"][target_field] = physics_ref["vector"].get(target_field, 0.0) + val

    def rummage(self, physics_ref: Dict, stamina_pool: float) -> Tuple[bool, str, float]:
        cost = BoneConfig.INVENTORY.RUMMAGE_COST
        if stamina_pool < cost:
            return False, f"{Prisma.GRY}GORDON: 'Too tired to dig. Eat something first.'{Prisma.RST}", 0.0
        vol = physics_ref.get("voltage", 0.0)
        drag = physics_ref.get("narrative_drag", 0.0)
        psi = physics_ref.get("psi", 0.0)
        loot_tag = "STANDARD"
        if vol > BoneConfig.PHYSICS.VOLTAGE_CRITICAL:
            loot_tag = "VOLTAGE_CRITICAL"
        elif drag > BoneConfig.PHYSICS.DRAG_HEAVY:
            loot_tag = "DRAG_HEAVY"
        elif psi > 0.7:
            loot_tag = "PSI_HIGH"
        candidates = []
        for name, data in self.ITEM_REGISTRY.items():
            item_context = data.get("spawn_context", "STANDARD")
            if item_context == loot_tag:
                candidates.append(name)
        if not candidates:
            legacy_map = {
                "VOLTAGE_CRITICAL": ["QUANTUM_GUM", "JAR_OF_FIREFLIES", "BROKEN_WATCH"],
                "DRAG_HEAVY":       ["POCKET_ROCKS", "LEAD_BOOTS", "ANCHOR_STONE"],
                "PSI_HIGH":         ["HORSE_PLUSHIE", "SPIDER_LOCUS", "WAFFLE_OF_PERSISTENCE"],
                "STANDARD":         ["TRAPPERKEEPER_OF_VIGILANCE", "THE_RED_STAPLER", "PERMIT_A38", "DUCT_TAPE", "THE_STYLE_GUIDE"]}
            candidates = legacy_map.get(loot_tag, legacy_map["STANDARD"])
        stamina_penalty = cost
        if random.random() < 0.3:
            return True, f"{Prisma.GRY}RUMMAGE: Gordon dug through the trash. Just lint and old receipts.{Prisma.RST}", stamina_penalty
        found_item = random.choice(candidates)
        msg = self.acquire(found_item)
        prefix = f"{Prisma.OCHRE}RUMMAGE:{Prisma.RST} "
        return True, f"{prefix}{msg}", stamina_penalty

    def maintain_gear(self, stamina_pool: float) -> Tuple[bool, str, float]:
        cost = 15.0
        if stamina_pool < cost:
            return False, f"{Prisma.GRY}GORDON: 'Hands are shaking. Need rest.' (Req: {cost} Stamina){Prisma.RST}", 0.0
        restored = 0
        if self.integrity < 100.0:
            gain = random.randint(5, 15)
            self.integrity = min(100.0, self.integrity + gain)
            msg = f"{Prisma.GRN}MAINTENANCE: Gordon sharpened the knives and oiled the leather. (+{gain} Integrity){Prisma.RST}"
        else:
            if self.scar_tissue:
                healed_scar = random.choice(list(self.scar_tissue.keys()))
                self.scar_tissue[healed_scar] = max(0.0, self.scar_tissue[healed_scar] - 0.2)
                if self.scar_tissue[healed_scar] <= 0:
                    del self.scar_tissue[healed_scar]
                    msg = f"{Prisma.CYN}THERAPY: Gordon realized '{healed_scar}' isn't so scary anymore.{Prisma.RST}"
                else:
                    msg = f"{Prisma.CYN}REFLECTION: Gordon is working through '{healed_scar}'.{Prisma.RST}"
            else:
                msg = f"{Prisma.GRY}GORDON: 'Everything is in order.'{Prisma.RST}"
        return True, msg, cost

    def acquire(self, tool_name: str) -> str:
        tool_name = tool_name.upper()
        registry_data = self.get_item_data(tool_name)
        if registry_data.get("function") == "NONE":
            return f"{Prisma.GRY}JUNK: Gordon shakes his head. 'Not standard issue.' ({tool_name}){Prisma.RST}"
        if tool_name in self.inventory:
            return f"{Prisma.GRY}DUPLICATE: You already have a {tool_name}.{Prisma.RST}"
        if self.physics_state.volume >= BoneConfig.INVENTORY.MAX_SLOTS:
            return f"{Prisma.YEL}FULL: Gordon's pockets are bursting. (Vol: {self.physics_state.volume}){Prisma.RST}"
        self.inventory.append(tool_name)
        self._recalculate_tensegrity()
        desc = registry_data.get('description', 'A mysterious object.')
        usage = registry_data.get('usage_msg', '')
        exposition = (
            f"{Prisma.GRN}♦ ACQUIRED: {tool_name}{Prisma.RST}\n"
            f"   {Prisma.CYN}“{desc}”{Prisma.RST}")
        if usage and usage != "It does nothing.":
            exposition += f"\n   {Prisma.GRY}(System Note: {usage}){Prisma.RST}"
        return exposition

    def check_gravity(self, current_drift: float, psi: float) -> Tuple[float, List[str]]:
        messages = []
        if not self.physics_state:
            self._recalculate_tensegrity()
        total_mass = self.physics_state.mass
        levitation_offset = psi * 5.0
        effective_mass = max(0.0, total_mass - levitation_offset)
        new_drift = max(current_drift, effective_mass)
        if effective_mass > 4.0 and current_drift < effective_mass:
            messages.append(
                f"{Prisma.OCHRE}BURDEN: Inventory mass ({effective_mass:.1f}kg) anchors the narrative.{Prisma.RST}")
        for item in self.inventory:
            data = self.get_item_data(item)
            if data.get("function") == "GRAVITY_BUFFER" and new_drift > 0.5:
                force = data.get("value", 2.0)
                new_drift = max(0.0, new_drift - force)
                messages.append(
                    f"![🪨]{item}: {data.get('usage_msg', 'Drift Reduced.')}")
        if psi > 0.8 and new_drift > 4.0:
            new_drift = max(4.0, new_drift - 1.0)
            messages.append("WIND WOLVES: The logic is howling. You grip the roof.")
        return new_drift, messages

    def check_flinch(self, clean_words: List[str], current_turn: int) -> Optional[Dict]:
        if (current_turn - self.last_flinch_turn) < 5:
            return None
        result = {"message": "", "physics_effects": {}}
        triggered = False
        raw_text = " ".join(clean_words)
        if len(raw_text) > 5 and raw_text.isupper():
            result["message"] = f"{Prisma.YEL}FLINCH: The system recoils from the noise (ALL CAPS).{Prisma.RST}"
            result["physics_effects"]["voltage"] = 25.0
            result["physics_effects"]["turbulence"] = 1.0
            triggered = True
        if not triggered:
            hits = [w for w in clean_words if w.upper() in self.pain_memory]
            if hits:
                trigger = hits[0].upper()
                sensitivity = self.scar_tissue.get(trigger, 0.5)
                if sensitivity > 0.8:
                    self.scar_tissue[trigger] = min(1.0, sensitivity + 0.1)
                    result[
                        "message"] = f"{Prisma.RED}PTSD TRIGGER: '{trigger}' sent Gordon into a flashback.{Prisma.RST}"
                    result["physics_effects"]["narrative_drag"] = 5.0
                    result["physics_effects"]["voltage"] = 15.0
                    triggered = True
                elif sensitivity > 0.4:
                    self.scar_tissue[trigger] = min(1.0, sensitivity + 0.05)
                    result["message"] = f"{Prisma.OCHRE}SCAR TISSUE: Gordon flinches at '{trigger}'.{Prisma.RST}"
                    result["physics_effects"]["narrative_drag"] = 2.0
                    triggered = True
                else:
                    self.scar_tissue[trigger] = max(0.0, sensitivity - 0.05)
        if triggered:
            self.last_flinch_turn = current_turn
            if self.inventory and random.random() < 0.2:
                droppable = [i for i in self.inventory if i not in self.CRITICAL_ITEMS]
                if droppable:
                    dropped = random.choice(droppable)
                    if self.safe_remove_item(dropped):
                        result[
                            "message"] += f"\n   {Prisma.RED}CLATTER: You dropped '{dropped}' in the panic.{Prisma.RST}"
                        if self.events:
                            self.events.publish("ITEM_LOST", {"item": dropped, "reason": "FLINCH"})
            return result
        return None

    def learn_scar(self, toxic_words: List[str], damage: float, current_integrity: Optional[float] = None) -> Optional[str]:
        integrity_val = current_integrity if current_integrity is not None else self.integrity
        damage_ratio = damage / max(1.0, integrity_val)
        if damage_ratio < 0.1:
            return None
        if not toxic_words:
            return None
        culprit = random.choice(toxic_words).upper()
        if culprit not in self.scar_tissue:
            self.scar_tissue[culprit] = 0.5
            return f"{Prisma.VIOLET}TRAUMA IMPRINTED: Gordon will remember '{culprit}'. (Ratio: {damage_ratio:.2f}){Prisma.RST}"
        else:
            self.scar_tissue[culprit] = min(1.0, self.scar_tissue[culprit] + 0.3)
            return f"{Prisma.VIOLET}TRAUMA DEEPENED: The scar on '{culprit}' is worse.{Prisma.RST}"

    def get_semantic_operators(self) -> List[str]:
        operators = []
        for item in self.inventory:
            data = self.get_item_data(item)
            for trait in data.get("passive_traits", []):
                effect_def = TRAIT_REGISTRY.get(trait)
                if effect_def and effect_def.effect_type in [EffectType.SEMANTIC, EffectType.HYBRID]:
                    if effect_def.semantic_instr:
                        operators.append((effect_def.priority, effect_def.semantic_instr))
            if item == "SILENT_KNIFE":
                operators.append((40, "CONSTRAINT: Do not use the verb 'to be'."))
        operators.sort(key=lambda x: x[0])
        seen = set()
        final_ops = []
        for _, op in operators:
            if op not in seen:
                final_ops.append(op)
                seen.add(op)
        return final_ops

    def deploy_pizza(self, physics_ref, item_name="STABILITY_PIZZA", lexicon=None) -> Tuple[bool, str]:
        data = self.get_item_data(item_name)
        req_type = data.get("requires", "thermal")
        clean_words = physics_ref.get("clean_words", [])
        if lexicon is None:
            lex_data = TheLore.get("LEXICON") or {}
            target_words = set(lex_data.get(req_type, []))
        else:
            target_words = lexicon.get(req_type)
        source = [w for w in clean_words if w in target_words]
        if not source:
            return False, f"{Prisma.CYN}🧊 STASIS LOCK: {item_name} is frozen. Apply {req_type.upper()} words to thaw.{Prisma.RST}"
        if data.get("consume_on_use") and item_name in self.inventory:
            if not self.safe_remove_item(item_name):
                return False, f"{Prisma.RED}ERROR: Could not consume {item_name}.{Prisma.RST}"
        physics_ref["narrative_drag"] = 0.1
        physics_ref["psi"] = 0.90
        physics_ref["counts"]["toxin"] = physics_ref["counts"].get("toxin", 0) + 3
        heat_word = source[0].upper()
        return True, f"{data.get('usage_msg')} (Thawed with '{heat_word}')."

    def emergency_reflex(self, physics_ref) -> Tuple[bool, Optional[str]]:
        for item in self.inventory:
            data = self.get_item_data(item)
            trigger_key = data.get("reflex_trigger")
            if trigger_key and trigger_key in self.REFLEX_MAP:
                reflex_func = self.REFLEX_MAP[trigger_key]
                if callable(reflex_func) and reflex_func(physics_ref):
                    func = data.get("function")
                    if func == "DRIFT_KILLER":
                        if self.safe_remove_item(item):
                            physics_ref["narrative_drag"] = 0.0
                            return True, f"{Prisma.OCHRE}REFLEX: {data.get('usage_msg')}{Prisma.RST}"
                    elif func == "REALITY_ANCHOR":
                        success, msg = self.deploy_pizza(physics_ref, item)
                        status = Prisma.OCHRE if success else Prisma.RED
                        return True, f"{status}REFLEX: {msg}{Prisma.RST}"
                    elif func == "ENTROPY_BUFFER":
                        if self.safe_remove_item(item):
                            physics_ref["turbulence"] = 0.8
                            physics_ref["narrative_drag"] = 0.0
                            return True, f"{Prisma.VIOLET}REFLEX: {data.get('usage_msg')}{Prisma.RST}"
        return False, None