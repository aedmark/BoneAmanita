""" bone_village.py - 'It takes a village... to raise a simulation.' """

import math
import random
import hashlib
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass, field

from bone_types import Prisma, PhysicsPacket
from bone_config import BoneConfig, BonePresets
from bone_core import TheLore
from bone_protocols import ZenGarden
from bone_drivers import UserProfile
from bone_akashic import TheAkashicRecord

VOLT_MANIC = 18.0
VOLT_CRITICAL = 25.0
DRAG_HEAVY = 10.0
DRAG_SWAMP = 16.0
ENTROPY_RUST_THRESH = 0.3
KAPPA_COHERENT = 0.8
CONFIDENCE_ASCENSION = 2.5
CONFIDENCE_RUST_WARN = 0.2

def _get(p: Any, k: str, d: Any = 0.0) -> Any:
    if p is None: return d
    if isinstance(p, dict): return p.get(k, d)
    return getattr(p, k, d)

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
        self.akashic = akashic_ref
        self.tool_resonance: Dict[str, float] = {}

    def audit_tool_use(self, physics_packet: Any, inventory_list: List[str], host_health: Any = None):
        if not inventory_list: return
        p = _normalize_physics_dict(physics_packet)
        voltage = _get_float(p, "voltage", 0.0)
        if voltage < 5.0 and random.random() > 0.1:
            return
        focus_item = random.choice(inventory_list)
        drag = _get_float(p, "narrative_drag", 0.0)
        kappa = _get_float(p, "kappa", 0.0)
        vector = _get(p, "vector", {})
        ent_val = float(vector.get("ENT", 0.0)) if isinstance(vector, dict) else 0.0
        entropy_level = ent_val + (drag * 0.1)
        self._process_single_tool(focus_item, inventory_list, voltage, kappa, entropy_level, drag, vector)

    def _process_single_tool(self, item: str, inventory: List[str], voltage: float, kappa: float, entropy: float,
                             drag: float, vector: Any):
        if item not in self.tool_resonance:
            self.tool_resonance[item] = 0.0
        if voltage > VOLT_MANIC or entropy > 0.5:
            self._apply_resonance(item, 0.2, "High Voltage")
            self._check_ascension(item, inventory, vector)
        elif kappa > KAPPA_COHERENT:
            self._apply_resonance(item, 0.1, "Coherent Flow")
        elif drag > DRAG_HEAVY:
            self._apply_resonance(item, 0.05, "Tempering")

    def _apply_resonance(self, item: str, amount: float, reason: str):
        self.tool_resonance[item] = min(10.0, self.tool_resonance[item] + amount)
        curr = self.tool_resonance[item]
        if 4.8 < curr < 5.2 and random.random() < 0.05:
            self.events.log(f"{Prisma.CYN}🔨 TINKER: {item} hums with resonance. (Lvl 5 Mastery){Prisma.RST}", "VILLAGE")

    def _check_ascension(self, old_name: str, inventory_list: List[str], vector: Any):
        resonance = self.tool_resonance.get(old_name, 0.0)
        if resonance < CONFIDENCE_ASCENSION:
            return
        if "OF_" in old_name: return
        if random.random() < (resonance * 0.05):
            new_name, new_data = self.akashic.forge_new_item(vector)
            if old_name in inventory_list:
                try:
                    idx = inventory_list.index(old_name)
                    inventory_list[idx] = new_name
                    if hasattr(self.gordon, "ITEM_REGISTRY"):
                        self.gordon.ITEM_REGISTRY[new_name] = new_data
                    self.tool_resonance[new_name] = resonance / 2.0
                    del self.tool_resonance[old_name]
                    self.events.log(
                        f"{Prisma.MAG}✨ ASCENSION: {old_name} -> {new_name} (Born of Resonance){Prisma.RST}",
                        "AKASHIC")
                except ValueError:
                    pass

class ParadoxSeed:
    def __init__(self, question: str, triggers: List[str]):
        self.question = question
        self.triggers = set([t.lower() for t in triggers])
        self.bloomed = False
        self.maturity = 0.0

    def water(self, current_words: List[str]) -> bool:
        if self.bloomed: return False
        for word in current_words:
            if word in self.triggers:
                self.maturity += 0.2
                return True
        return False

    def bloom(self) -> str:
        self.bloomed = True
        return self.question

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
    MAX_NODES = 50

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
        coord_str = "-".join([f"{k}{int(v * 10)}" for k, v in top_dims])
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
            if len(self.world_graph) >= self.MAX_NODES:
                self._prune_graph()
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

    def _prune_graph(self):
        candidates = [k for k in self.world_graph.keys() if k != "GENESIS_POINT" and k != self.current_node_id]
        if not candidates: return
        candidates.sort(key=lambda k: self.world_graph[k].visited_count)
        victim = candidates[0]
        del self.world_graph[victim]

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

    def strike_root(self, vector):
        return None

    def check_transplant_shock(self, vector):
        return None

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

    def to_dict(self):
        return self.export_atlas()

    def load_state(self, data):
        self.import_atlas(data)

class TownHall:
    def __init__(self, gordon_ref, events_ref, shimmer_ref, akashic_ref, navigator_ref):
        self.gordon = gordon_ref
        self.events = events_ref
        self.shimmer = shimmer_ref
        self.akashic = akashic_ref
        self.navigator = navigator_ref
        self.seeds: List[ParadoxSeed] = []
        lore = TheLore.get_instance()
        seed_data = lore.get("SEEDS") or []
        for s in seed_data:
            if "question" in s and "triggers" in s:
                self.sow_seed(s["question"], s["triggers"])
        if self.seeds:
            pass

    def _on_item_drop(self, payload):
        item = payload.get("item")
        if item:
            self.events.log(f"Town Hall noticed you dropped {item}.", "VILLAGE")

    def rumors(self):
        return "The Town Hall is quiet."

    def sow_seed(self, question, triggers):
        self.seeds.append(ParadoxSeed(question, triggers))

    def tend_garden(self, clean_words: List[str]):
        if not self.seeds or not clean_words: return
        word_set = set(w.lower() for w in clean_words)
        for seed in self.seeds:
            if seed.bloomed: continue
            if not seed.triggers.isdisjoint(word_set):
                bloom_msg = seed.bloom()
                self.events.log(
                    f"{Prisma.MAG}🌷 PARADOX BLOOM:{Prisma.RST} {bloom_msg}",
                    "VILLAGE_EVENT")
                return

    def conduct_census(self, physics_snapshot, host_stats) -> str:
        p = _normalize_physics_dict(physics_snapshot)
        drag = _get_float(p, "narrative_drag", 0.0)
        volt = _get_float(p, "voltage", 0.0)
        latency = getattr(host_stats, "latency", 0.0) if host_stats else 0.0
        current_node = self.navigator.world_graph.get(self.navigator.current_node_id)
        loc_name = current_node.name if current_node else "UNKNOWN"
        almanac = TheLore.get("ALMANAC") or {}
        forecasts = almanac.get("FORECASTS", {})
        strategies = almanac.get("STRATEGIES", {})
        if latency > 3.0:
            status = "HIGH_LATENCY"
            advice = "System is lagging. Simplify inputs."
        elif volt > 15.0:
            status = "HIGH_VOLTAGE"
            advice = random.choice(forecasts.get("HIGH_VOLTAGE", ["Manic energy detected."]))
        elif drag > DRAG_HEAVY:
            status = "HIGH_DRAG"
            advice = random.choice(forecasts.get("HIGH_DRAG", ["The narrative is stuck."]))
        else:
            status = "BALANCED"
            advice = random.choice(forecasts.get("BALANCED", ["Systems operational."]))
        strategy_tip = ""
        if random.random() < 0.2 and status in strategies:
            strategy_tip = f"\n💡 STRATEGY: {strategies[status]}"
        news = self._get_town_news(latency, volt, status)
        report = f"CENSUS [{loc_name}]: {status} | {advice}{strategy_tip}"
        if news:
            report += f"\n{news}"
        return report

    def _get_town_news(self, latency: float, volt: float, status: str) -> Optional[str]:
        if latency > 4.0:
            return f"{Prisma.OCHRE}📢 TOWN CRIER: The time-winds are blowing slow today! (High Latency){Prisma.RST}"
        if volt > 15.0:
            return f"{Prisma.YEL}📢 HEAR YE: Curfew in effect! The voltage is dangerous!{Prisma.RST}"
        if random.random() < 0.20:
            current_node = self.navigator.world_graph.get(self.navigator.current_node_id)
            loc_name = current_node.name if current_node else "VOID"
            if "VOID" in loc_name:
                return f"{Prisma.GRY}📢 TOWN CRIER: Echoes... just echoes...{Prisma.RST}"
            msg = self.rumors()
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
    _FALLBACK_PROTOCOLS = {
        "PREFIXES": ["FATAL ERROR", "SYSTEM HALT", "THE END"],
        "CAUSES": {"DEFAULT": ["Unknown Error", "Entropy limit reached"]},
        "VERDICTS": {"DEFAULT": ["End of Line.", "Reboot required."]}}

    @classmethod
    def load_protocols(cls):
        if TheLore.get("DEATH") is None:
            print(f"{Prisma.RED}[DEATH]: Protocols missing. Injecting fallback skeleton.{Prisma.RST}")
            TheLore.inject("DEATH", cls._FALLBACK_PROTOCOLS)

    @staticmethod
    def eulogy(physics: Dict, mito_state: Any, trauma_vector: Dict = None) -> str:
        death_data = TheLore.get("DEATH")
        if not death_data:
            death_data = DeathGen._FALLBACK_PROTOCOLS
        p = _normalize_physics_dict(physics)
        cause = DeathGen._determine_cause(p, mito_state, trauma_vector)
        verdict_type = DeathGen._determine_verdict_type(p, cause)
        prefix = random.choice(death_data.get("PREFIXES", ["Alas."]))
        possible_causes = death_data["CAUSES"].get(cause, death_data["CAUSES"].get("DEFAULT", ["General System Failure"]))
        specific_cause = random.choice(possible_causes)
        possible_verdicts = death_data["VERDICTS"].get(verdict_type, death_data["VERDICTS"].get("HEAVY", ["It is done."]))
        verdict = random.choice(possible_verdicts)
        return f"{prefix} CAUSE: {specific_cause}. {verdict}"

    @staticmethod
    def _determine_cause(p: Dict, mito_state: Any, trauma_vector: Dict = None) -> str:
        if trauma_vector:
            total_trauma = sum(trauma_vector.values())
            if total_trauma > 50.0:
                return "TRAUMA"
        atp = 0.0
        if isinstance(mito_state, dict):
            atp = float(mito_state.get("atp", 0))
        else:
            atp = float(getattr(mito_state, "atp_pool", 0))
        if atp <= 0: return "STARVATION"
        volt = _get_float(p, "voltage", 0.0)
        drag = _get_float(p, "narrative_drag", 0.0)
        counts = _get(p, "counts", {})
        if volt > VOLT_CRITICAL: return "GLUTTONY"
        if counts.get("antigen", 0) > 5: return "TOXICITY"
        if drag > DRAG_SWAMP: return "BOREDOM"
        return "TRAUMA" if trauma_vector and sum(trauma_vector.values()) > 20.0 else "STARVATION"

    @staticmethod
    def _determine_verdict_type(p: Dict, cause: str) -> str:
        if cause == "TOXICITY": return "TOXIC"
        if cause == "BOREDOM": return "BORING"
        if cause == "TRAUMA": return "BROKEN"
        volt = _get_float(p, "voltage", 0.0)
        return "LIGHT" if volt > 10.0 else "HEAVY"

class Limbo:
    def __init__(self):
        self.ghosts: List[str] = []

    def haunt(self, text: str) -> str:
        if not self.ghosts: return text
        if random.random() < 0.1:
            ghost_word = random.choice(self.ghosts)
            return f"{text} ...{ghost_word.lower()}..."
        return text