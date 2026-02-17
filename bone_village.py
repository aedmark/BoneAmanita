""" bone_village.py - 'It takes a village... to raise a simulation.' """
import math
import random
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass, field, asdict
from bone_types import Prisma, PhysicsPacket
from bone_core import LoreManifest, EventBus
from bone_config import BoneConfig
from bone_physics import PhysicsDelta
from bone_drivers import UserProfile

def _hydrate_packet(p: Any) -> PhysicsPacket:
    if isinstance(p, PhysicsPacket):
        return p
    if isinstance(p, dict):
        default = PhysicsPacket(
            voltage=0.0, narrative_drag=0.0, clean_words=[],
            vector={}, zone="VOID", counts={})
        default.voltage = p.get("voltage", 0.0)
        default.narrative_drag = p.get("narrative_drag", 0.0)
        default.vector = p.get("vector", {})
        default.clean_words = p.get("clean_words", [])
        default.counts = p.get("counts", {})
        default.zone = p.get("zone", "VOID")
        default.kappa = p.get("kappa", 0.0)
        default.raw_text = p.get("raw_text", "")
        return default
    return PhysicsPacket(voltage=0.0, narrative_drag=0.0)

class TheTinkerer:
    def __init__(self, gordon_ref, events_ref: EventBus, akashic_ref):
        self.gordon = gordon_ref
        self.events = events_ref
        self.akashic = akashic_ref
        self.tool_resonance: Dict[str, float] = {}

    def calculate_passive_deltas(self, inventory_data: List[Dict]) -> List[PhysicsDelta]:
        deltas = []
        trait_counts = {"HEAVY_LOAD": 0, "TIME_DILATION": 0, "ENTROPY_BUFFER": 0}
        for item_data in inventory_data:
            traits = item_data.get("passive_traits", [])
            for t in trait_counts:
                if t in traits:
                    trait_counts[t] += 1
        if trait_counts["HEAVY_LOAD"] > 0:
            impact = math.log1p(trait_counts["HEAVY_LOAD"]) * 0.7
            deltas.append(PhysicsDelta("ADD", "narrative_drag", impact, "Inventory", "Heavy Load"))
        if trait_counts["TIME_DILATION"] > 0:
            reduction = max(0.5, 0.85 - (trait_counts["TIME_DILATION"] * 0.05))
            deltas.append(PhysicsDelta("MULT", "narrative_drag", reduction, "Inventory", "Time Dilation"))
        if trait_counts["ENTROPY_BUFFER"] > 0:
            buffer_str = max(0.2, 0.5 / math.sqrt(trait_counts["ENTROPY_BUFFER"]))
            deltas.append(PhysicsDelta("MULT", "turbulence", buffer_str, "Inventory", "Entropy Buffer"))
        return deltas

    def audit_tool_use(self, packet: PhysicsPacket, inventory_list: List[str], host_health: Any = None):
        if not inventory_list: return
        if packet.voltage < BoneConfig.PHYSICS.VOLTAGE_LOW and random.random() > 0.1:
            return
        focus_item = random.choice(inventory_list)
        ent_val = packet.vector.get("ENT", 0.0) if packet.vector else 0.0
        entropy_level = ent_val + (packet.narrative_drag * 0.1)
        self._process_single_tool(
            focus_item,
            inventory_list,
            packet,
            entropy_level)

    def _process_single_tool(self, item: str, inventory: List[str], packet: PhysicsPacket, entropy: float):
        if item not in self.tool_resonance:
            self.tool_resonance[item] = 0.0
        if packet.voltage > BoneConfig.COUNCIL.MANIC_VOLTAGE_TRIGGER or entropy > 0.5:
            self._apply_resonance(item, 0.2, "High Voltage")
            self._check_ascension(item, inventory, packet.vector)
        elif packet.narrative_drag > BoneConfig.PHYSICS.DRAG_HALT:
            self._apply_resonance(item, 0.05, "Tempering")

    def _apply_resonance(self, item: str, amount: float, reason: str):
        self.tool_resonance[item] = min(10.0, self.tool_resonance[item] + amount)
        curr = self.tool_resonance[item]
        if 4.8 < curr < 5.2 and random.random() < 0.05:
            self.events.log(
                f"{Prisma.CYN}🔨 TINKER: {item} hums with resonance. (Lvl 5 Mastery){Prisma.RST}", "VILLAGE")

    def _check_ascension(self, old_name: str, inventory_list: List[str], vector: Dict):
        resonance = self.tool_resonance.get(old_name, 0.0)
        if resonance < 2.5:
            return
        if random.random() < (resonance * 0.05):
            if hasattr(self.akashic, 'forge_new_item'):
                new_name, new_data = self.akashic.forge_new_item(vector)
                self.gordon.register_dynamic_item(new_name, new_data)
                self.gordon.add_item(new_name)
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

@dataclass
class ParadoxSeed:
    question: str
    triggers: Set[str]
    maturity: float = 0.0
    bloomed: bool = False

    def water(self, words: List[str]) -> bool:
        if self.bloomed: return False
        hits = sum(1 for w in words if w in self.triggers)
        if hits > 0:
            self.maturity += hits * 0.2
        return self.maturity >= 5.0

    def bloom(self) -> str:
        self.bloomed = True
        return f"PARADOX BLOOM: {self.question}"

class MirrorGraph:
    def __init__(self, events_ref):
        self.events = events_ref
        self.stats = {"WAR": 0.0, "ART": 0.0, "LAW": 0.0, "ROT": 0.0}
        self.profile = UserProfile()

    def reflect(self, packet: PhysicsPacket):
        txt = packet.raw_text or ""
        volt = packet.voltage
        if "!" in txt or volt > BoneConfig.COUNCIL.MANIC_VOLTAGE_TRIGGER:
            self.stats["WAR"] += 0.1
        if "?" in txt:
            self.stats["ART"] += 0.1
        total = sum(self.stats.values())
        if total > 5.0:
            for k in self.stats: self.stats[k] *= 0.8

    def get_reflection_modifiers(self) -> Dict:
        if not self.stats: return {"flavor": "Reflecting NEUTRAL", "drag_mult": 1.0}
        top_stat = max(self.stats, key=self.stats.get)
        return {"flavor": f"Reflecting {top_stat}", "drag_mult": 1.0}

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
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class TheCartographer:
    MAX_NODES = 50

    def __init__(self, shimmer_ref):
        self.shimmer = shimmer_ref
        self.world_graph: Dict[str, GeniusLoci] = {}
        self.current_node_id: str = "GENESIS_POINT"
        self._init_genesis()

    def apply_environment(self, packet_input: Any) -> List[str]:
        packet = _hydrate_packet(packet_input)
        logs = []
        node = self.world_graph.get(self.current_node_id)
        if not node: return logs
        if "heavy" in node.atmosphere.lower():
            packet.narrative_drag += 2.0
            logs.append(f"{Prisma.GRY}🌫️ ENVIRONMENT: The air here is heavy. (Drag +2){Prisma.RST}")
        if "vibrating" in node.atmosphere.lower():
            packet.voltage += 1.0
            logs.append(f"{Prisma.YEL}⚡ ENVIRONMENT: Static charge detected. (Voltage +1){Prisma.RST}")
        node.entropy_buildup += 0.1
        if node.entropy_buildup > 5.0:
            packet.vector["ENT"] = packet.vector.get("ENT", 0.0) + 0.1
        return logs

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
        return "-".join([f"{k}{int(v * 10)}" for k, v in top_dims])

    def locate(self, packet: PhysicsPacket, host_stats: Any = None) -> Tuple[str, Optional[str]]:
        vector = packet.vector or {}
        target_id = self._generate_coord_hash(vector)
        msg = None
        if target_id not in self.world_graph:
            if len(self.world_graph) >= self.MAX_NODES:
                self._prune_graph()
            new_node = self._generate_loci_data(target_id, packet)
            self.world_graph[target_id] = new_node
            msg = f"{Prisma.MAG}🗺️ CARTOGRAPHER: New Sector Discovered [{new_node.name}].{Prisma.RST}"
        else:
            new_node = self.world_graph[target_id]
            if new_node.id != self.current_node_id:
                msg = f"{Prisma.CYN}🗺️ CARTOGRAPHER: Arriving at {new_node.name}.{Prisma.RST}"
        self.current_node_id = target_id
        current_node = self.world_graph[target_id]
        current_node.visited_count += 1
        return current_node.name, msg

    def _generate_loci_data(self, node_id: str, packet: PhysicsPacket) -> GeniusLoci:
        random.seed(node_id)
        prefixes = ["The", "Neo", "Old", "Sector", "Zone", "Void"]
        roots = ["Construct", "Forge", "Mud", "Archive", "Garden", "Nexus"]
        name = f"{random.choice(prefixes)} {random.choice(roots)}"
        if packet.voltage > BoneConfig.COUNCIL.MANIC_VOLTAGE_TRIGGER:
            suffix = "Flux"
            atmosphere = "The air is vibrating. Geometry is unstable."
            smell = "Burning copper."
        elif packet.narrative_drag > BoneConfig.PHYSICS.DRAG_HALT:
            suffix = "Deep"
            atmosphere = "Heavy gravity. Dust motes hang suspended."
            smell = "Wet wool and ancient dust."
        else:
            suffix = "Prime"
            atmosphere = "Stable reality matrix. Standard definition."
            smell = "Clean air."
        final_name = f"{name} {suffix}".upper()
        return GeniusLoci(id=node_id, name=final_name, atmosphere=atmosphere, smell=smell)

    def _prune_graph(self):
        candidates = [
            k for k in self.world_graph.keys()
            if k != "GENESIS_POINT"
               and k != self.current_node_id]
        if not candidates: return
        candidates.sort(key=lambda k: self.world_graph[k].visited_count)
        del self.world_graph[candidates[0]]

    def export_atlas(self) -> Dict[str, Any]:
        return {
            "nodes": {k: v.to_dict() for k, v in self.world_graph.items()},
            "current_id": self.current_node_id}

    def import_atlas(self, atlas_data: Dict[str, Any]):
        if not atlas_data: return
        self.world_graph = {}
        raw_nodes = atlas_data.get("nodes", {})
        for nid, n_data in raw_nodes.items():
            try:
                self.world_graph[nid] = GeniusLoci.from_dict(n_data)
            except Exception:
                pass
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
        seed_data = LoreManifest.get_instance().get("SEEDS") or []
        for s in seed_data:
            if "question" in s and "triggers" in s:
                self.sow_seed(s["question"], set(s["triggers"]))

    def sow_seed(self, question: str, triggers: Set[str]):
        self.seeds.append(ParadoxSeed(question, triggers))

    def tend_garden(self, clean_words: List[str]):
        if not self.seeds or not clean_words: return
        word_set = set(w.lower() for w in clean_words)
        for seed in self.seeds:
            if seed.bloomed: continue
            if not seed.triggers.isdisjoint(word_set):
                bloom_msg = seed.bloom()
                self.events.log(
                    f"{Prisma.MAG}🌷 PARADOX BLOOM:{Prisma.RST} {bloom_msg}", "VILLAGE_EVENT")
                return

    def conduct_census(self, packet: PhysicsPacket, host_stats: Any) -> str:
        latency = getattr(host_stats, "latency", 0.0) if host_stats else 0.0
        almanac = LoreManifest.get_instance().get("ALMANAC") or {}
        forecasts = almanac.get("FORECASTS", {})
        current_node = self.navigator.world_graph.get(self.navigator.current_node_id)
        loc_name = current_node.name if current_node else "UNKNOWN"
        if latency > 3.0:
            status = "HIGH_LATENCY"
            advice = "System lag detected."
        elif packet.voltage > BoneConfig.PHYSICS.VOLTAGE_HIGH:
            status = "HIGH_VOLTAGE"
            advice = random.choice(forecasts.get("HIGH_VOLTAGE", ["Manic energy."]))
        elif packet.narrative_drag > BoneConfig.PHYSICS.DRAG_HEAVY:
            status = "HIGH_DRAG"
            advice = random.choice(forecasts.get("HIGH_DRAG", ["Narrative stuck."]))
        else:
            status = "BALANCED"
            advice = random.choice(forecasts.get("BALANCED", ["Nominal."]))
        report = f"CENSUS [{loc_name}]: {status} | {advice}"
        news = self._get_town_news(latency, packet.voltage)
        if news: report += f"\n{news}"
        if packet.voltage > 20.0:
            report += f"\n{Prisma.RED}⚖️ COUNCIL ALERT: The Chairholder is drafting a restraining order.{Prisma.RST}"
        elif packet.voltage < 2.0 and packet.narrative_drag > 5.0:
            report += f"\n{Prisma.MAG}⚖️ COUNCIL ALERT: Strange Loops detected in the lower districts.{Prisma.RST}"
        return report

    def _get_town_news(self, latency: float, volt: float) -> Optional[str]:
        if latency > 4.0:
            return f"{Prisma.OCHRE}📢 TOWN CRIER: The time-winds are slow!{Prisma.RST}"
        if volt > BoneConfig.PHYSICS.VOLTAGE_CRITICAL:
            return f"{Prisma.YEL}📢 HEAR YE: Voltage Critical!{Prisma.RST}"
        return None

    def on_item_drop(self, payload):
        item = payload.get("item")
        if item:
            self.events.log(f"Town Hall noticed you dropped {item}.", "VILLAGE")

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
            max_trauma = max(trauma, key=trauma.get) if trauma else "NONE"
            if trauma.get(max_trauma, 0) > 0.6:
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
        if LoreManifest.get_instance().get("DEATH") is None:
            LoreManifest.get_instance().inject("DEATH", cls._FALLBACK_PROTOCOLS)

    @staticmethod
    def eulogy(packet: PhysicsPacket, mito_state: Any, trauma_vector: Dict = None) -> Tuple[str, str]:
        death_data = LoreManifest.get_instance().get("DEATH")
        if not death_data:
            death_data = DeathGen._FALLBACK_PROTOCOLS
        cause = DeathGen._determine_cause(packet, mito_state, trauma_vector)
        verdict_type = DeathGen._determine_verdict_type(packet, cause)
        prefix = random.choice(death_data.get("PREFIXES", ["Alas."]))
        cause_list = death_data["CAUSES"].get(cause, death_data["CAUSES"].get("DEFAULT", ["Error"]))
        verdict_list = death_data["VERDICTS"].get(verdict_type, death_data["VERDICTS"].get("HEAVY", ["Done."]))
        return f"{prefix} CAUSE: {random.choice(cause_list)}. {random.choice(verdict_list)}", cause

    @staticmethod
    def _determine_cause(p: PhysicsPacket, mito_state: Any, trauma_vector: Dict = None) -> str:
        if trauma_vector and sum(trauma_vector.values()) > 50.0:
            return "TRAUMA"
        atp = float(mito_state.get("atp", 0) if isinstance(mito_state, dict) else getattr(mito_state, "atp_pool", 0))
        if atp <= BoneConfig.BIO.ATP_STARVATION:
            return "STARVATION"
        if p.voltage > BoneConfig.PHYSICS.VOLTAGE_CRITICAL: return "GLUTTONY"
        if p.narrative_drag > BoneConfig.PHYSICS.DRAG_HALT: return "BOREDOM"
        counts = p.counts or {}
        if counts.get("antigen", 0) > 5: return "TOXICITY"
        return "STARVATION"

    @staticmethod
    def _determine_verdict_type(p: PhysicsPacket, cause: str) -> str:
        if cause == "TOXICITY": return "TOXIC"
        if cause == "BOREDOM": return "BORING"
        if p.voltage > BoneConfig.PHYSICS.VOLTAGE_MED: return "LIGHT"
        return "HEAVY"

class Limbo:
    def __init__(self):
        self.ghosts: List[str] = []

    def haunt(self, text: str) -> str:
        if not self.ghosts: return text
        if random.random() < BoneConfig.LIMBO.HAUNT_CHANCE:
            ghost_word = random.choice(self.ghosts)
            return f"{text} ...{ghost_word.lower()}..."
        return text