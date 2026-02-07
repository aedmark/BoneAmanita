""" bone_village.py - 'It takes a village... to raise a simulation.' """

import math
import random
import time
import hashlib
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass, field

from bone_core import Prisma, BoneConfig, BonePresets, TheLore
from bone_lexicon import TheLexicon
from bone_protocols import ZenGarden
from bone_drivers import UserProfile
from bone_akashic import TheAkashicRecord

VOLT_MANIC = 12.0
VOLT_CRITICAL = 20.0
DRAG_HEAVY = 6.0
DRAG_SWAMP = 8.0
ENTROPY_RUST_THRESH = 0.3
KAPPA_COHERENT = 0.8
CONFIDENCE_ASCENSION = 2.5
CONFIDENCE_RUST_WARN = 0.2

def _get(p: Any, k: str, d: Any = 0.0) -> Any:
    if p is None: return d
    return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)

def _get_float(p: Any, k: str, d: float = 0.0) -> float:
    val = _get(p, k, d)
    try: return float(val)
    except (ValueError, TypeError, AttributeError): return d

def _normalize_physics_dict(packet: Any) -> Dict[str, Any]:
    if packet is None: return {}
    if isinstance(packet, dict): return packet
    return getattr(packet, "__dict__", {})

@dataclass
class GeniusLoci:
    id: str
    name: str
    atmosphere: str
    smell: str
    local_items: List[str] = field(default_factory=list)
    visited_count: int = 0
    entropy_buildup: float = 0.0

    def description(self) -> str:
        base = f"LOCATION: {self.name}\nATMOSPHERE: {self.atmosphere}\nSMELL: {self.smell}"
        if self.local_items:
            items = ", ".join(self.local_items)
            base += f"\nVISIBLE ITEMS: {items}"
        return base

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "atmosphere": self.atmosphere,
            "smell": self.smell, "local_items": self.local_items,
            "visited_count": self.visited_count, "entropy_buildup": self.entropy_buildup}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class TheTinkerer:
    def __init__(self, gordon_ref, events_ref, akashic_ref):
        self.gordon = gordon_ref
        self.events = events_ref
        self.tool_confidence: Dict[str, float] = {}
        self.akashic = akashic_ref

    def audit_tool_use(self, physics_packet, inventory_list: List[str], host_health: Any = None):
        p = _normalize_physics_dict(physics_packet)
        voltage = _get_float(p, "voltage", 0.0)
        drag = _get_float(p, "narrative_drag", 0.0)
        kappa = _get_float(p, "kappa", 0.0)
        vector = _get(p, "vector", {})
        ent_val = float(vector.get("ENT", 0.0)) if isinstance(vector, dict) else 0.0
        entropy_level = ent_val + (drag * 0.1)
        for item in inventory_list:
            self._process_single_tool(item, inventory_list, voltage, kappa, entropy_level, drag, vector)

    def _process_single_tool(self, item: str, inventory: List[str], voltage: float, kappa: float, entropy: float, drag: float, vector: Any):
        if item not in self.tool_confidence:
            self.tool_confidence[item] = 1.0
        if voltage > VOLT_MANIC or kappa > KAPPA_COHERENT:
            self._apply_growth(item, inventory, vector)
            return
        if entropy > ENTROPY_RUST_THRESH or drag > DRAG_HEAVY:
            self._apply_decay(item, entropy)

    def _apply_growth(self, item: str, inventory: List[str], vector: Any):
        self.tool_confidence[item] += 0.05
        if self.tool_confidence[item] > CONFIDENCE_ASCENSION:
            self._attempt_ascension(item, inventory, vector)

    def _apply_decay(self, item: str, entropy_level: float):
        decay_rate = 0.05 * (1.0 + entropy_level)
        self.tool_confidence[item] -= decay_rate
        current_conf = self.tool_confidence[item]
        if 0.1 < current_conf < CONFIDENCE_RUST_WARN:
            self.events.log(f"{Prisma.OCHRE}[TINKER] Warning: {item} is rusting. (Conf: {current_conf:.2f}){Prisma.RST}", "SYS")
        elif current_conf <= 0.0:
            self.tool_confidence[item] = 0.0
            self.events.log(f"{Prisma.RED}[TINKER] JAMMED: {item} has seized up via Entropy.{Prisma.RST}", "SYS")

    def _attempt_ascension(self, old_name: str, inventory_list: List[str], vector: Any):
        if "OF_" in old_name: return
        new_name, new_data = self.akashic.forge_new_item(vector)
        if old_name in inventory_list:
            idx = inventory_list.index(old_name)
            inventory_list[idx] = new_name
            if hasattr(self.gordon, "ITEM_REGISTRY"):
                self.gordon.ITEM_REGISTRY[new_name] = new_data
            self.events.log(f"{Prisma.MAG}✨ ASCENSION: {old_name} -> {new_name}{Prisma.RST}", "AKASHIC")

class ParadoxSeed:
    def __init__(self, question: str, triggers: List[str]):
        self.question = question
        self.triggers = {t.lower() for t in triggers}
        self.maturity = 0.0
        self.bloomed = False

    def water(self, current_words: List[str]) -> bool:
        if self.bloomed: return False
        word_set = set(current_words)
        overlap = self.triggers.intersection(word_set)
        if overlap:
            self.maturity += (len(overlap) * 0.1)
            if self.maturity >= 1.0:
                self.bloomed = True
                return True
        return False
    def bloom(self) -> str:
        return f"{Prisma.GRN}🌸 BLOOM: The seed '{self.question}' has opened. A new truth takes root.{Prisma.RST}"

class MirrorGraph:
    def __init__(self, events_ref):
        self.events = events_ref
        self.stats = {"WAR": 0.0, "ART": 0.0, "LAW": 0.0, "ROT": 0.0}
        self.profile = UserProfile()

    def reflect(self, physics: Dict):
        txt = str(_get(physics, "raw_text", ""))
        volt = _get_float(physics, "voltage", 0.0)
        if "!" in txt or volt > VOLT_MANIC: self.stats["WAR"] += 0.1
        if "?" in txt: self.stats["ART"] += 0.1
        total = sum(self.stats.values())
        if total > 5.0:
            for k in self.stats: self.stats[k] *= 0.8
    def get_reflection_modifiers(self) -> Dict:
        if not self.stats: return {"flavor": "Reflecting NEUTRAL", "drag_mult": 1.0}
        top_stat = max(self.stats, key=self.stats.get)
        return {"flavor": f"Reflecting {top_stat}", "drag_mult": 1.0}

class TheCartographer:
    PREFIXES = ["The", "Neo", "Old", "Sector", "Zone", "Void"]
    ROOTS = ["Construct", "Forge", "Mud", "Archive", "Garden", "Nexus", "Spire", "Basement"]
    SUFFIXES = ["Alpha", "Prime", "Deep", "Zero", "Flux", "Rot"]

    def __init__(self, shimmer_ref):
        self.shimmer = shimmer_ref
        self.world_graph: Dict[str, GeniusLoci] = {}
        self.current_node_id: str = "GENESIS_POINT"
        self._init_genesis()

    def _init_genesis(self):
        self.world_graph["GENESIS_POINT"] = GeniusLoci(
            id="GENESIS_POINT",
            name="THE CONSTRUCT (Origin)",
            atmosphere="Clean white void. Infinite potential.",
            smell="Ozone and new plastic.")

    def _generate_coord_hash(self, vector: Dict[str, float]) -> str:
        if not vector: return "VOID_DRIFT"
        sorted_dims = sorted(vector.items(), key=lambda x: -x[1])
        top_dims = sorted_dims[:2]
        coord_str = "-".join([f"{k}{int(v*10)}" for k, v in top_dims])
        return coord_str

    def get_current_description(self) -> str:
        if self.current_node_id in self.world_graph:
            node = self.world_graph[self.current_node_id]
            return f"{node.atmosphere} Smell: {node.smell}. Visible: {', '.join(node.local_items) if node.local_items else 'None'}"
        return "Unmapped territory. The fog is thick."

    def _generate_loci_data(self, node_id: str, physics: Dict) -> GeniusLoci:
        random.seed(node_id)
        p1 = random.choice(self.PREFIXES)
        p2 = random.choice(self.ROOTS)
        name = f"{p1} {p2}"
        volt = _get_float(physics, "voltage", 0.0)
        drag = _get_float(physics, "narrative_drag", 0.0)
        if volt > VOLT_MANIC:
            suffix = random.choice(["Flux", "Spark", "Storm"])
            atmosphere = "The air is vibrating. Geometry is unstable."
            smell = "Burning copper."
        elif drag > DRAG_HEAVY:
            suffix = random.choice(["Deep", "Rot", "Sediment"])
            atmosphere = "Heavy gravity. Dust motes hang suspended in stagnant air."
            smell = "Wet wool and ancient dust."
        else:
            suffix = random.choice(self.SUFFIXES)
            atmosphere = "Stable reality matrix. Standard definition."
            smell = "Clean air."
        final_name = f"{name} {suffix}"
        return GeniusLoci(id=node_id, name=final_name.upper(), atmosphere=atmosphere, smell=smell)

    def locate(self, physics_packet: dict, host_stats: Any = None) -> Tuple[str, Optional[str]]:
        p = _normalize_physics_dict(physics_packet)
        vector = _get(p, "vector", {})
        target_id = self._generate_coord_hash(vector)
        if target_id not in self.world_graph:
            new_node = self._generate_loci_data(target_id, p)
            self.world_graph[target_id] = new_node
            msg = f"{Prisma.MAG}🗺️ CARTOGRAPHER: New Sector Discovered [{new_node.name}].{Prisma.RST}"
        else:
            new_node = self.world_graph[target_id]
            msg = None
            if new_node.id != self.current_node_id:
                msg = f"{Prisma.CYN}🗺️ CARTOGRAPHER: Arriving at {new_node.name}.{Prisma.RST}"
        self.current_node_id = target_id
        current_node = self.world_graph[target_id]
        current_node.visited_count += 1
        return current_node.name, msg

    def apply_environment(self, physics_packet: Any) -> List[str]:
        logs = []
        node = self.world_graph.get(self.current_node_id)
        if not node: return logs
        if node.visited_count == 1:
            logs.append(f"{Prisma.GRY}SCENE: {node.atmosphere} Smell: {node.smell}{Prisma.RST}")
        if node.local_items:
            items_str = ", ".join([f"[{i}]" for i in node.local_items])
            logs.append(f"{Prisma.YEL}GROUND: You see {items_str} here.{Prisma.RST}")

        return logs

    def drop_item(self, item_name: str) -> str:
        if self.current_node_id in self.world_graph:
            self.world_graph[self.current_node_id].local_items.append(item_name)
            return f"Item '{item_name}' left at {self.world_graph[self.current_node_id].name}."
        return "Item lost in the void."

    def pickup_item(self, item_name: str) -> bool:
        node = self.world_graph.get(self.current_node_id)
        if node and item_name in node.local_items:
            node.local_items.remove(item_name)
            return True
        return False

    def strike_root(self, vector): return None

    def check_transplant_shock(self, vector): return None

    def export_atlas(self) -> Dict[str, Any]:
        return {
            "nodes": {k: v.to_dict() for k, v in self.world_graph.items()},
            "current_id": self.current_node_id}

    def import_atlas(self, atlas_data: Dict[str, Any]):
        if not atlas_data: return
        self.world_graph = {}
        raw_nodes = atlas_data.get("nodes", {})
        for nid, n_data in raw_nodes.items():
            self.world_graph[nid] = GeniusLoci.from_dict(n_data)
        self.current_node_id = atlas_data.get("current_id", "GENESIS_POINT")
        if "GENESIS_POINT" not in self.world_graph:
            self._init_genesis()

class TownHall:
    def __init__(self, gordon_ref, events_ref, shimmer_ref, akashic_ref):
        self.Tinkerer = TheTinkerer(gordon_ref, events_ref, akashic_ref)
        self.Navigator = TheCartographer(shimmer_ref)
        self.seeds: List[ParadoxSeed] = []
        if hasattr(events_ref, "subscribe"):
            events_ref.subscribe("ITEM_LOST", self._on_item_drop)

    def _on_item_drop(self, payload):
        item = payload.get("item")
        if item:
            log = self.Navigator.drop_item(item)

    @property
    def rumors(self) -> List[str]:
        return TheLore.get("narrative_data", "RUMORS") or ["The air is silent."]

    def sow_seed(self, question: str, triggers: List[str]):
        new_seed = ParadoxSeed(question, triggers)
        self.seeds.append(new_seed)
        return f"Seed planted: '{question}'"

    def tend_garden(self, clean_words: List[str]) -> List[str]:
        logs = []
        remaining_seeds = []
        for seed in self.seeds:
            if not seed.bloomed:
                if seed.water(clean_words):
                    logs.append(seed.bloom())
                else:
                    remaining_seeds.append(seed)
        self.seeds = remaining_seeds
        return logs

    def conduct_census(self, physics_snapshot, host_stats) -> str:
        p = _normalize_physics_dict(physics_snapshot)
        drag = _get_float(p, "narrative_drag", 0.0)
        volt = _get_float(p, "voltage", 0.0)
        latency = getattr(host_stats, "latency", 0.0) if host_stats else 0.0
        loc_name = self.Navigator.world_graph.get(self.Navigator.current_node_id).name

        if latency > 3.0:
            status, advice = "HIGH_LATENCY", "System is lagging. Simplify inputs."
        elif volt > 15.0:
            status, advice = "HIGH_VOLTAGE", "Manic energy detected. Risk of burnout."
        elif drag > DRAG_HEAVY:
            status, advice = "HIGH_DRAG", "The narrative is stuck in the mud."
        else:
            status, advice = "NOMINAL", "Systems operational."

        news = self._get_town_news(latency, volt, status)
        report = f"CENSUS [{loc_name}]: {status} | {advice}"
        if news:
            report += f"\n{news}"
        return report

    def _get_town_news(self, latency: float, volt: float, status: str) -> Optional[str]:
        if latency > 4.0:
            return f"{Prisma.OCHRE}📢 TOWN CRIER: The time-winds are blowing slow today! (High Latency){Prisma.RST}"
        if volt > 15.0:
            return f"{Prisma.YEL}📢 HEAR YE: Curfew in effect! The voltage is dangerous!{Prisma.RST}"
        if status == "NOMINAL" and random.random() < 0.05:
            msg = random.choice(self.rumors)
            return f"{Prisma.GRY}📢 TOWN CRIER: {msg}{Prisma.RST}"
        return None

    def diagnose_condition(self, session_data: dict, host_health: Any = None, soul: Any = None) -> Tuple[str, str]:
        meta = session_data.get("meta", {})
        trauma = session_data.get("trauma_vector", {})
        final_health = meta.get("final_health", 50)
        if soul:
            neglect = getattr(soul, "obsession_neglect", 0.0)
            if neglect > 8.0:
                obsession = getattr(soul, 'current_obsession', 'work')
                return "HIGH_DRAG", f"Guilt over '{obsession}' is thickening the air."
        if trauma:
            max_trauma = max(trauma, key=trauma.get)
            if trauma[max_trauma] > 0.6:
                return "HIGH_TRAUMA", f"Warning: High levels of {max_trauma} residue detected."
        if final_health < 30:
            return "HIGH_TRAUMA", "System critical. Structural damage."
        return "BALANCED", "System nominal."

class DeathGen:
    @classmethod
    def load_protocols(cls):
        if TheLore.get("DEATH"): return
        print(f"{Prisma.RED}[DEATH]: Protocols missing. Loading default fallback.{Prisma.RST}")
        default_death = {
            "PREFIXES": ["System Halt.", "Alas.", "So it ends."],
            "CAUSES": {
                "DEFAULT": ["Unknown Error"],
                "STARVATION": ["Energy Depletion", "Metabolic Collapse"],
                "GLUTTONY": ["Circuit Overload", "Icarus Failure"],
                "TOXICITY": ["Viral Load Exceeded", "Poisoned Input"],
                "BOREDOM": ["Stagnation", "Entropy Victory"]},
            "VERDICTS": {
                "DEFAULT": ["The screen goes black."],
                "HEAVY": ["Gravity wins.", "Silence falls."],
                "LIGHT": ["A flash of light, then nothing."],
                "TOXIC": ["The system purges itself."],
                "BORING": ["The narrative dissolves into grey."]}}
        TheLore.inject("DEATH", default_death)

    @staticmethod
    def eulogy(physics, mito_state) -> str:
        death_data = TheLore.get("DEATH")
        if not death_data:
            DeathGen.load_protocols()
            death_data = TheLore.get("DEATH")
        p = _normalize_physics_dict(physics)
        cause = DeathGen._determine_cause(p, mito_state)
        verdict_type = DeathGen._determine_verdict_type(p, cause)
        prefix = random.choice(death_data.get("PREFIXES", ["Alas."]))
        specific_cause = random.choice(death_data["CAUSES"].get(cause, ["General Failure"]))
        verdict = random.choice(death_data["VERDICTS"].get(verdict_type, ["It is done."]))
        return f"{prefix} CAUSE: {specific_cause}. {verdict}"

    @staticmethod
    def _determine_cause(p: Dict, mito_state: Any) -> str:
        atp = 0.0
        if isinstance(mito_state, dict): atp = float(mito_state.get("atp", 0))
        else: atp = float(getattr(mito_state, "atp_pool", 0))
        if atp <= 0: return "STARVATION"
        volt = _get_float(p, "voltage", 0.0)
        drag = _get_float(p, "narrative_drag", 0.0)
        counts = _get(p, "counts", {})
        if volt > VOLT_CRITICAL: return "GLUTTONY"
        if counts.get("antigen", 0) > 5: return "TOXICITY"
        if drag > DRAG_SWAMP: return "BOREDOM"
        return "DEFAULT"

    @staticmethod
    def _determine_verdict_type(p: Dict, cause: str) -> str:
        if cause == "TOXICITY": return "TOXIC"
        if cause == "BOREDOM": return "BORING"
        volt = _get_float(p, "voltage", 0.0)
        return "LIGHT" if volt > 10.0 else "HEAVY"

class PIDController:
    def __init__(self, kp, ki, kd, setpoint, output_limits=(-10.0, 10.0)):
        self.kp = kp; self.ki = ki; self.kd = kd
        self.setpoint = setpoint
        self.min_out, self.max_out = output_limits
        self._integral = 0.0; self._last_error = 0.0; self._first_run = True

    def reset(self):
        self._integral = 0.0; self._last_error = 0.0; self._first_run = True

    def update(self, measurement: float, dt: float = 1.0) -> float:
        if dt <= 0.0: return 0.0
        error = self.setpoint - measurement
        if self._first_run:
            self._last_error = error; self._first_run = False
        self._integral += error * dt
        self._integral = max(self.min_out, min(self.max_out, self._integral))
        derivative = (error - self._last_error) / dt
        output = (self.kp * error) + (self.ki * self._integral) + (self.kd * derivative)
        self._last_error = error
        return max(self.min_out, min(self.max_out, output))

class SanctuaryGovernor:
    def __init__(self, events_ref):
        self.events = events_ref
        self.mode = "DEFAULT"
        self.voltage_pid = PIDController(kp=0.8, ki=0.1, kd=0.05, setpoint=10.0)
        self.drag_pid = PIDController(kp=0.4, ki=0.2, kd=0.1, setpoint=1.0)

    def shift(self, physics_packet, voltage_history, tick_count): return "GOVERNOR_MAINTAIN"

    def recalibrate(self, target_voltage: float, target_drag: float):
        self.voltage_pid.setpoint = target_voltage
        self.drag_pid.setpoint = target_drag

    def regulate(self, physics, dt: float) -> Tuple[float, float]:
        v_force = self.voltage_pid.update(physics.voltage, dt)
        d_force = self.drag_pid.update(physics.narrative_drag, dt)
        return v_force, d_force

    def assess(self, physics_packet) -> Tuple[bool, float]:
        p = _normalize_physics_dict(physics_packet)
        curr_v = _get_float(p, "voltage", 0.0)
        curr_d = _get_float(p, "narrative_drag", 0.0)
        dist_v = abs(curr_v - self.voltage_pid.setpoint)
        dist_d = abs(curr_d - self.drag_pid.setpoint)
        is_safe = (dist_v < 2.0) and (dist_d < 1.0)
        return is_safe, math.sqrt(dist_v ** 2 + dist_d ** 2)

class Limbo:
    def __init__(self):
        self.ghosts: List[str] = []

    def haunt(self, text: str) -> str:
        if not self.ghosts: return text
        if random.random() < 0.1:
            ghost_word = random.choice(self.ghosts)
            return f"{text} ...{ghost_word.lower()}..."
        return text