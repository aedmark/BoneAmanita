""" bone_inventory.py
 'Organization is the first step toward civilization.' - Schur """

import random, copy
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, cast, Callable
from enum import Enum, auto
from bone_bus import Prisma, BoneConfig
from bone_data import GORDON_LOGS, GORDON


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
    "function": "NONE",
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
    return [PhysicsDelta("ADD_COUNT", "photo", 2)]


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
        starting_gear = GORDON.get("STARTING_INVENTORY", ["POCKET_ROCKS", "SILENT_KNIFE"])
        if not self.inventory or self.inventory == ["POCKET_ROCKS"]:
            self.inventory = list(starting_gear)
        self.CRITICAL_ITEMS = {"SILENT_KNIFE"}
        default_scars = GORDON.get("SCAR_TISSUE", {})
        if not self.scar_tissue:
            self.scar_tissue = default_scars
        raw_registry = GORDON.get("ITEM_REGISTRY", {})
        self.ITEM_REGISTRY = copy.deepcopy(raw_registry)
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
            "BOREDOM_CRITICAL": lambda p: p.get("repetition", 0.0) > 0.5}

    def get_item_data(self, item_name: str) -> Dict:
        return self.ITEM_REGISTRY.get(item_name.upper(), UNKNOWN_ARTIFACT)

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
        if item_name in self.CRITICAL_ITEMS:
            return False
        if item_name not in self.inventory:
            return False
        self.inventory.remove(item_name)
        self._recalculate_tensegrity()
        return True

    def audit_tools(self, physics_ref: Dict) -> List[str]:
        logs = []
        cling_msg = self.check_static_cling(physics_ref)
        if cling_msg:
            logs.append(cling_msg)
        all_deltas: List[PhysicsDelta] = []
        turbulence = physics_ref.get("turbulence", 0.0)
        if turbulence > BoneConfig.INVENTORY.TURBULENCE_THRESHOLD:
            if random.random() < BoneConfig.INVENTORY.TURBULENCE_FUMBLE_CHANCE and self.inventory:
                droppable = [i for i in self.inventory if i not in self.CRITICAL_ITEMS]
                if droppable:
                    dropped = random.choice(droppable)
                    if self.safe_remove_item(dropped):
                        template = random.choice(GORDON_LOGS["FUMBLE"])
                        msg = template.format(item=dropped)
                        logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        for item_name in self.inventory:
            data = self.get_item_data(item_name)
            for trait in data.get("passive_traits", []):
                effect_def = TRAIT_REGISTRY.get(trait)
                if effect_def and effect_def.effect_type in [EffectType.PHYSICS, EffectType.HYBRID]:
                    raw_handler = effect_def.physics_handler
                    if callable(raw_handler):
                        safe_handler = cast(Callable[[Dict, Dict, str], List[PhysicsDelta]], raw_handler)
                        new_deltas = safe_handler(physics_ref, data, item_name)
                        if new_deltas:
                            all_deltas.extend(new_deltas)
        for delta in all_deltas:
            if delta.message:
                logs.append(delta.message)
            if delta.operator == "noop":
                continue
            if delta.operator == "ADD_COUNT":
                if "counts" not in physics_ref: physics_ref["counts"] = {}
                physics_ref["counts"][delta.field] = physics_ref["counts"].get(delta.field, 0) + delta.value
            elif delta.operator == "SET_COUNT":
                if "counts" not in physics_ref: physics_ref["counts"] = {}
                physics_ref["counts"][delta.field] = delta.value
            elif delta.operator == "ADD_VECTOR":
                if "vector" not in physics_ref: physics_ref["vector"] = {}
                physics_ref["vector"][delta.field] = physics_ref["vector"].get(delta.field, 0.0) + delta.value
            elif delta.operator == "SET_ZONE":
                physics_ref["zone"] = str(delta.value)
            elif delta.operator == "SET":
                physics_ref[delta.field] = delta.value
            elif delta.operator == "ADD":
                physics_ref[delta.field] = physics_ref.get(delta.field, 0.0) + delta.value
            elif delta.operator == "MULTIPLY":
                physics_ref[delta.field] = physics_ref.get(delta.field, 0.0) * delta.value
        return logs

    def rummage(self, physics_ref: Dict, stamina_pool: float) -> Tuple[bool, str, float]:
        cost = BoneConfig.INVENTORY.RUMMAGE_COST
        if stamina_pool < cost:
            return False, f"{Prisma.GRY}GORDON: 'Too tired to dig. Eat something first.'{Prisma.RST}", 0.0
        stamina_penalty = cost
        vol = physics_ref.get("voltage", 0.0)
        drag = physics_ref.get("narrative_drag", 0.0)
        psi = physics_ref.get("psi", 0.0)
        loot_table = ["TRAPPERKEEPER_OF_VIGILANCE", "THE_RED_STAPLER", "PERMIT_A38", "DUCT_TAPE", "THE_STYLE_GUIDE"]
        if vol > BoneConfig.PHYSICS.VOLTAGE_CRITICAL:
            loot_table = ["QUANTUM_GUM", "JAR_OF_FIREFLIES", "BROKEN_WATCH"]
        elif drag > BoneConfig.PHYSICS.DRAG_HEAVY:
            loot_table = ["POCKET_ROCKS", "LEAD_BOOTS", "ANCHOR_STONE"]
        elif psi > 0.7:
            loot_table = ["HORSE_PLUSHIE", "SPIDER_LOCUS", "WAFFLE_OF_PERSISTENCE"]
        if random.random() < 0.3:
            return True, f"{Prisma.GRY}RUMMAGE: Gordon dug through the trash. Just lint and old receipts.{Prisma.RST}", stamina_penalty
        found_item = random.choice(loot_table)
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
        desc = registry_data.get('description', 'A thing.')
        return f"{Prisma.GRN}LOOT DROP: Acquired [{tool_name}].{Prisma.RST}\n   {Prisma.GRY}\"{desc}\"{Prisma.RST}"

    def check_gravity(self, current_drift: float, psi: float) -> Tuple[float, List[str]]:
        messages = []
        new_drift = current_drift
        for item in self.inventory:
            data = self.get_item_data(item)
            if data.get("function") == "GRAVITY_BUFFER" and new_drift > 0.5:
                force = data.get("value", 2.0)
                cost = data.get("cost_value", 0.0)
                if data.get("cost") == "INTEGRITY":
                    self.integrity -= cost
                new_drift = max(0.0, new_drift - force)
                messages.append(f"![🪨](https://fonts.gstatic.com/s/e/notoemoji/16.0/1faa8/32.png) {item}: {data.get('usage_msg', 'Drift Reduced.')}")
        if psi > 0.8 and new_drift > 4.0:
            new_drift = max(4.0, new_drift - 1.0)
            messages.append("WIND WOLVES: The logic is howling. You grip the roof.")
        return new_drift, messages

    def check_flinch(self, clean_words: List[str], current_turn: int) -> Optional[Dict]:
        if (current_turn - self.last_flinch_turn) < 10:
            return None
        hits = [w for w in clean_words if w.upper() in self.pain_memory]
        if not hits:
            return None
        self.last_flinch_turn = current_turn
        trigger = hits[0].upper()
        sensitivity = self.scar_tissue.get(trigger, 0.5)
        if sensitivity > 0.8:
            self.scar_tissue[trigger] = min(1.0, sensitivity + 0.1)
            return {
                "message": f"{Prisma.RED}PTSD TRIGGER: '{trigger}' sent Gordon into a flashback. He dropped the keys.{Prisma.RST}",
                "physics_effects": {"narrative_drag": 5.0, "voltage": 15.0}}
        elif sensitivity > 0.4:
            self.scar_tissue[trigger] = min(1.0, sensitivity + 0.05)
            return {
                "message": f"{Prisma.OCHRE}SCAR TISSUE: Gordon flinches at '{trigger}'. Hands are shaking.{Prisma.RST}",
                "physics_effects": {"narrative_drag": 2.0}}
        else:
            self.scar_tissue[trigger] = max(0.0, sensitivity - 0.05)
            return {
                "message": f"{Prisma.GRY}CALLOUS: '{trigger}' hit an old scar. Gordon ignores it.{Prisma.RST}",
                "physics_effects": {}}

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
            from bone_lexicon import TheLexicon as lexicon
        source = [w for w in clean_words if w in lexicon.get(req_type)]
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