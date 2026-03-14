"""
bone_village.py
"""

import heapq
import math
import random
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Tuple, Optional, Set
from bone_presets import BoneConfig
from bone_core import LoreManifest, EventBus, ux
from bone_physics import PhysicsDelta
from bone_types import Prisma, PhysicsPacket

def _hydrate_packet(p: Any) -> PhysicsPacket:
    if isinstance(p, PhysicsPacket):
        return p
    packet = PhysicsPacket.void_state()
    if isinstance(p, dict):
        for k in ("voltage", "narrative_drag", "vector", "clean_words", "counts", "zone", "kappa", "raw_text",):
            if k in p:
                setattr(packet, k, p[k])
    return packet

class TheTinkerer:
    def __init__(self, gordon_ref, events_ref: EventBus, akashic_ref):
        self.gordon = gordon_ref
        self.events = events_ref
        self.akashic = akashic_ref
        self.tool_resonance: Dict[str, float] = {}
        self._delta_cache = None
        self._inventory_hash = 0

    def calculate_passive_deltas(
            self, inventory_data: List[Dict]) -> List[PhysicsDelta]:
        state_tuple = tuple(
            sorted(
                f"{i.get('name', '')}:{','.join(sorted(i.get('passive_traits', [])))}"
                for i in inventory_data))
        current_hash = hash(state_tuple)
        if self._delta_cache is not None and current_hash == self._inventory_hash:
            return self._delta_cache
        deltas = []
        trait_counts = {"HEAVY_LOAD": 0, "TIME_DILATION": 0, "ENTROPY_BUFFER": 0}
        for item_data in inventory_data:
            for t in item_data.get("passive_traits", []):
                if t in trait_counts:
                    trait_counts[t] += 1
        cfg = getattr(BoneConfig, "VILLAGE", None)
        if trait_counts["HEAVY_LOAD"] > 0:
            h_mult = getattr(cfg, "TINKER_HEAVY_LOAD_MULT", 0.7) if cfg else 0.7
            impact = math.log1p(trait_counts["HEAVY_LOAD"]) * h_mult
            deltas.append(PhysicsDelta("ADD", "narrative_drag", impact, "Inventory", "Heavy Load"))
        if trait_counts["TIME_DILATION"] > 0:
            t_base = getattr(cfg, "TINKER_TIME_DILATION_BASE", 0.85) if cfg else 0.85
            t_step = getattr(cfg, "TINKER_TIME_DILATION_STEP", 0.05) if cfg else 0.05
            t_min = getattr(cfg, "TINKER_TIME_DILATION_MIN", 0.5) if cfg else 0.5
            reduction = max(t_min, t_base - (trait_counts["TIME_DILATION"] * t_step))
            deltas.append(PhysicsDelta("MULT", "narrative_drag", reduction, "Inventory", "Time Dilation"))
        if trait_counts["ENTROPY_BUFFER"] > 0:
            e_base = getattr(cfg, "TINKER_ENTROPY_BUFFER_BASE", 0.5) if cfg else 0.5
            e_min = getattr(cfg, "TINKER_ENTROPY_BUFFER_MIN", 0.2) if cfg else 0.2
            buffer_str = max(e_min, e_base / math.sqrt(trait_counts["ENTROPY_BUFFER"]))
            deltas.append(
                PhysicsDelta("MULT", "turbulence", buffer_str, "Inventory", "Entropy Buffer"))
        self._inventory_hash = current_hash
        self._delta_cache = deltas
        return deltas

    def audit_tool_use(
            self, packet: PhysicsPacket, inventory_list: List[str], _host_health: Any = None):
        if not inventory_list:
            return
        cfg = getattr(BoneConfig, "VILLAGE", None)
        v_chance = getattr(cfg, "TINKER_TOOL_USE_VOLT_CHANCE", 0.1) if cfg else 0.1
        if packet.voltage < BoneConfig.PHYSICS.VOLTAGE_LOW and random.random() > v_chance:
            return
        focus_item = random.choice(inventory_list)
        ent_val = packet.vector.get("ENT", 0.0) if packet.vector else 0.0
        e_mult = getattr(cfg, "TINKER_ENTROPY_DRAG_MULT", 0.1) if cfg else 0.1
        entropy_level = ent_val + (packet.narrative_drag * e_mult)
        self._process_single_tool(focus_item, inventory_list, packet, entropy_level)

    def _process_single_tool(
            self, item: str, _inventory: List[str], packet: PhysicsPacket, entropy: float):
        if item not in self.tool_resonance:
            self.tool_resonance[item] = 0.0
        cfg = getattr(BoneConfig, "VILLAGE", None)
        r_high = getattr(cfg, "TINKER_RESONANCE_HIGH_V", 0.2) if cfg else 0.2
        r_temp = getattr(cfg, "TINKER_RESONANCE_TEMPER", 0.05) if cfg else 0.05
        if packet.voltage > BoneConfig.COUNCIL.MANIC_VOLTAGE_TRIGGER or entropy > 0.5:
            self._apply_resonance(item, r_high, "High Voltage")
            self._check_ascension(item, _inventory, packet.vector)
        elif packet.narrative_drag > BoneConfig.PHYSICS.DRAG_HALT:
            self._apply_resonance(item, r_temp, "Tempering")

    def _apply_resonance(self, item: str, amount: float, _reason: str):
        cfg = getattr(BoneConfig, "VILLAGE", None)
        r_max = getattr(cfg, "TINKER_RESONANCE_MAX", 10.0) if cfg else 10.0
        a_min = getattr(cfg, "TINKER_RESONANCE_ANNOUNCE_MIN", 4.8) if cfg else 4.8
        a_max = getattr(cfg, "TINKER_RESONANCE_ANNOUNCE_MAX", 5.2) if cfg else 5.2
        a_chance = getattr(cfg, "TINKER_RESONANCE_ANNOUNCE_CHANCE", 0.05) if cfg else 0.05
        self.tool_resonance[item] = min(r_max, self.tool_resonance[item] + amount)
        curr = self.tool_resonance[item]
        if a_min < curr < a_max and random.random() < a_chance:
            msg = ux("village_strings", "tinkerer_resonance")
            if msg:
                self.events.log(f"{Prisma.CYN}{msg.format(item=item)}{Prisma.RST}", "VILLAGE")

    def _check_ascension(self, old_name: str, inventory_list: List[str], vector: Dict):
        resonance = self.tool_resonance.get(old_name, 0.0)
        cfg = getattr(BoneConfig, "VILLAGE", None)
        a_min = getattr(cfg, "TINKER_ASCENSION_MIN", 2.5) if cfg else 2.5
        a_chance_m = getattr(cfg, "TINKER_ASCENSION_CHANCE_MULT", 0.05) if cfg else 0.05
        if resonance < a_min:
            return
        if random.random() < (resonance * a_chance_m):
            if hasattr(self.akashic, "forge_new_item"):
                new_name, new_data = self.akashic.forge_new_item(vector)
                self.gordon.register_dynamic_item(new_name, new_data)
                self.gordon.acquire(new_name)
                if old_name in inventory_list:
                    try:
                        idx = inventory_list.index(old_name)
                        inventory_list[idx] = new_name
                        if hasattr(self.gordon, "ITEM_REGISTRY"):
                            self.gordon.ITEM_REGISTRY[new_name] = new_data
                        a_halve = getattr(cfg, "TINKER_ASCENSION_HALVE", 2.0) if cfg else 2.0
                        self.tool_resonance[new_name] = resonance / a_halve
                        del self.tool_resonance[old_name]
                        msg = ux("village_strings", "tinkerer_ascension")
                        if msg:
                            self.events.log(f"{Prisma.MAG}{msg.format(old=old_name, new=new_name)}{Prisma.RST}", "AKASHIC",)
                    except ValueError:
                        pass

@dataclass
class ParadoxSeed:
    question: str
    triggers: Set[str]
    maturity: float = 0.0
    bloomed: bool = False

    def water(self, words: List[str]) -> bool:
        if self.bloomed:
            return False
        hits = sum(1 for w in words if w in self.triggers)
        cfg = getattr(BoneConfig, "VILLAGE", None)
        if hits > 0:
            m_step = getattr(cfg, "SEED_MATURITY_STEP", 0.2) if cfg else 0.2
            self.maturity += hits * m_step
        m_max = getattr(cfg, "SEED_MATURITY_MAX", 5.0) if cfg else 5.0
        return self.maturity >= m_max

    def bloom(self) -> str:
        self.bloomed = True
        msg = ux("village_strings", "paradox_bloom")
        return msg.format(question=self.question) if msg else ""

class MirrorGraph:
    def __init__(self, events_ref):
        self.events = events_ref
        self.stats = {"WAR": 0.0, "ART": 0.0, "LAW": 0.0, "ROT": 0.0}

    def reflect(self, packet: PhysicsPacket):
        txt = ""
        if hasattr(packet, "matter") and packet.matter:
            txt = getattr(packet.matter, "raw_text", "")
        if not txt:
            txt = getattr(packet, "raw_text", "")
        volt = packet.voltage
        cfg = getattr(BoneConfig, "VILLAGE", None)
        step = getattr(cfg, "MIRROR_STAT_STEP", 0.1) if cfg else 0.1
        rot_ent = getattr(cfg, "MIRROR_ROT_ENTROPY_MIN", 0.5) if cfg else 0.5
        if "!" in txt or volt > BoneConfig.COUNCIL.MANIC_VOLTAGE_TRIGGER:
            self.stats["WAR"] += step
        if "?" in txt:
            self.stats["ART"] += step
        if packet.narrative_drag > BoneConfig.PHYSICS.DRAG_HALT:
            self.stats["LAW"] += step
        if packet.vector and packet.vector.get("ENT", 0.0) > rot_ent:
            self.stats["ROT"] += step
        total = sum(self.stats.values())
        cap = getattr(cfg, "MIRROR_STAT_CAP", 5.0) if cfg else 5.0
        decay = getattr(cfg, "MIRROR_DECAY", 0.8) if cfg else 0.8
        floor = getattr(cfg, "MIRROR_DECAY_FLOOR", 0.1) if cfg else 0.1
        if total > cap:
            for k in self.stats:
                self.stats[k] *= decay
                if self.stats[k] < floor:
                    self.stats[k] = 0.0

    def get_reflection_modifiers(self) -> Dict:
        if not self.stats or sum(self.stats.values()) == 0:
            msg_neutral = ux("village_strings", "mirror_neutral")
            return {"flavor": msg_neutral, "drag_mult": 1.0}
        top_stat = max(self.stats, key=self.stats.get)
        cfg = getattr(BoneConfig, "VILLAGE", None)
        drag_map = {"WAR": getattr(cfg, "MIRROR_DRAG_WAR", 1.2) if cfg else 1.2,
                    "ROT": getattr(cfg, "MIRROR_DRAG_ROT", 1.5) if cfg else 1.5,
                    "LAW": getattr(cfg, "MIRROR_DRAG_LAW", 0.8) if cfg else 0.8,
                    "ART": getattr(cfg, "MIRROR_DRAG_ART", 0.9) if cfg else 0.9}
        mult = drag_map.get(top_stat, 1.0)
        msg_raw = ux("village_strings", "mirror_stat")
        msg_stat = msg_raw.format(stat=top_stat) if msg_raw else ""
        return {"flavor": msg_stat, "drag_mult": mult}

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
        if not node:
            return logs
        cfg = getattr(BoneConfig, "VILLAGE", None)
        c_heavy = getattr(cfg, "CARTO_HEAVY_DRAG", 2.0) if cfg else 2.0
        c_static = getattr(cfg, "CARTO_STATIC_VOLT", 1.0) if cfg else 1.0
        c_ent_step = getattr(cfg, "CARTO_ENTROPY_STEP", 0.1) if cfg else 0.1
        c_ent_cap = getattr(cfg, "CARTO_ENTROPY_CAP", 5.0) if cfg else 5.0
        if "heavy" in node.atmosphere.lower():
            packet.narrative_drag += c_heavy
            msg_raw = ux("village_strings", "carto_env_heavy")
            if msg_raw:
                msg = msg_raw.format(c_heavy=c_heavy)
                logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
        if "vibrating" in node.atmosphere.lower():
            packet.voltage += c_static
            msg_raw = ux("village_strings", "carto_env_static")
            if msg_raw:
                msg = msg_raw.format(c_static=c_static)
                logs.append(f"{Prisma.YEL}{msg}{Prisma.RST}")
        node.entropy_buildup += c_ent_step
        if node.entropy_buildup > c_ent_cap:
            if not packet.vector:
                packet.vector = {}
            packet.vector["ENT"] = packet.vector.get("ENT", 0.0) + c_ent_step
        return logs

    def _init_genesis(self):
        manifest = LoreManifest.get_instance()
        msg_name = manifest.get_ux("village_strings", "genesis_name")
        msg_atmos = manifest.get_ux("village_strings", "genesis_atmos")
        msg_smell = manifest.get_ux("village_strings", "genesis_smell")
        self.world_graph["GENESIS_POINT"] = GeniusLoci(id="GENESIS_POINT", name=msg_name, atmosphere=msg_atmos, smell=msg_smell, )

    @staticmethod
    def _generate_coord_hash(vector: Dict[str, float]) -> str:
        if not vector:
            return "VOID_DRIFT"
        top_dims = heapq.nlargest(2, vector.items(), key=lambda x: x[1])
        return "-".join([f"{k}{int(v * 100)}" for k, v in top_dims])

    def locate(self, packet: PhysicsPacket) -> Tuple[str, Optional[str]]:
        vector = packet.vector or {}
        target_id = self._generate_coord_hash(vector)
        msg = None
        if target_id not in self.world_graph:
            cfg = getattr(BoneConfig, "VILLAGE", None)
            max_nodes = getattr(cfg, "CARTO_MAX_NODES", 50) if cfg else 50
            if len(self.world_graph) >= max_nodes:
                self._prune_graph()
            new_node = self._generate_loci_data(target_id, packet)
            self.world_graph[target_id] = new_node
            msg_str = ux("village_strings", "carto_new_sector")
            msg = f"{Prisma.MAG}{msg_str.format(name=new_node.name)}{Prisma.RST}" if msg_str else None
        else:
            new_node = self.world_graph[target_id]
            if new_node.id != self.current_node_id:
                msg_str = ux("village_strings", "carto_arriving")
                msg = f"{Prisma.CYN}{msg_str.format(name=new_node.name)}{Prisma.RST}" if msg_str else None
        self.current_node_id = target_id
        current_node = self.world_graph[target_id]
        current_node.visited_count += 1
        return current_node.name, msg

    @staticmethod
    def _generate_loci_data(node_id: str, packet: PhysicsPacket) -> GeniusLoci:
        random.seed(node_id)
        manifest = LoreManifest.get_instance()
        scenarios = manifest.get("SCENARIOS") or {}
        prefixes = scenarios.get("PREFIXES", ["The", "Zone", "Sector"]) or {}
        roots = scenarios.get("ROOTS", ["Construct", "Forge", "Garden"]) or {}
        name = f"{random.choice(prefixes)} {random.choice(roots)}"
        if packet.voltage > BoneConfig.COUNCIL.MANIC_VOLTAGE_TRIGGER:
            suffix = manifest.get_ux("village_strings", "loci_flux_suffix")
            atmosphere = manifest.get_ux("village_strings", "loci_flux_atmos")
            smell = manifest.get_ux("village_strings", "loci_flux_smell")
        elif packet.narrative_drag > BoneConfig.PHYSICS.DRAG_HALT:
            suffix = manifest.get_ux("village_strings", "loci_deep_suffix")
            atmosphere = manifest.get_ux("village_strings", "loci_deep_atmos")
            smell = manifest.get_ux("village_strings", "loci_deep_smell")
        else:
            suffix = manifest.get_ux("village_strings", "loci_prime_suffix")
            atmosphere = manifest.get_ux("village_strings", "loci_prime_atmos")
            smell = manifest.get_ux("village_strings", "loci_prime_smell")
        final_name = f"{name} {suffix}".upper()
        return GeniusLoci(id=node_id, name=final_name, atmosphere=atmosphere, smell=smell)

    def _prune_graph(self):
        candidates = [
            k
            for k in self.world_graph.keys()
            if k != "GENESIS_POINT" and k != self.current_node_id]
        if not candidates:
            return
        victim = min(candidates, key=lambda k: self.world_graph[k].visited_count)
        del self.world_graph[victim]

    def export_atlas(self) -> Dict[str, Any]:
        return {"nodes": {k: v.to_dict() for k, v in self.world_graph.items()}, "current_id": self.current_node_id,}

    def import_atlas(self, atlas_data: Dict[str, Any]):
        if not atlas_data:
            return
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
        narrative = LoreManifest.get_instance().get("narrative_data") or {}
        self.rumors = narrative.get("RUMORS", [])
        seed_data = narrative.get("SEEDS", [])
        for s in seed_data:
            if "question" in s and "triggers" in s:
                self.sow_seed(s["question"], set(s["triggers"]))

    def sow_seed(self, question: str, triggers: Set[str]):
        self.seeds.append(ParadoxSeed(question, triggers))

    @staticmethod
    def consult_almanac(physics: PhysicsPacket) -> str:
        almanac = LoreManifest.get_instance().get("ALMANAC") or {}
        forecasts = almanac.get("FORECASTS", {})
        strategies = almanac.get("STRATEGIES", {})
        cfg = getattr(BoneConfig, "VILLAGE", None)
        v_high = getattr(cfg, "ALMANAC_VOLT_HIGH", 15.0) if cfg else 15.0
        d_high = getattr(cfg, "ALMANAC_DRAG_HIGH", 4.0) if cfg else 4.0
        e_high = getattr(cfg, "ALMANAC_ENTROPY_HIGH", 0.8) if cfg else 0.8
        state_key = "BALANCED"
        if physics.voltage > v_high:
            state_key = "HIGH_VOLTAGE"
        elif physics.narrative_drag > d_high:
            state_key = "HIGH_DRAG"
        elif hasattr(physics, "entropy") and physics.entropy > e_high:
            state_key = "HIGH_ENTROPY"
        options = forecasts.get(state_key, ["Weather unclear."])
        flavor_text = random.choice(options)
        strategy = strategies.get(state_key, "Keep breathing.")
        return f"☁️ FORECAST [{state_key}]: {flavor_text} (Strategy: {strategy})"

    def tend_garden(self, clean_words: List[str]) -> List[str]:
        blooms = []
        if not self.seeds or not clean_words:
            return blooms
        lower_words = [w.lower() for w in clean_words]
        prefix = ux("village_strings", "town_bloom")
        for seed in self.seeds:
            if seed.bloomed:
                continue
            if seed.water(lower_words):
                bloom_msg = seed.bloom()
                self.events.log(f"{Prisma.MAG}{prefix}{Prisma.RST} {bloom_msg}", "VILLAGE_EVENT", )
                blooms.append(f"{Prisma.MAG}{prefix}{Prisma.RST} {bloom_msg}")
        return blooms

    def conduct_census(self, packet: PhysicsPacket, host_stats: Any) -> str:
        latency = getattr(host_stats, "latency", 0.0) if host_stats else 0.0
        almanac = LoreManifest.get_instance().get("ALMANAC") or {}
        forecasts = almanac.get("FORECASTS", {})
        loc_name = "UNKNOWN"
        if self.navigator:
            current_node = self.navigator.world_graph.get(self.navigator.current_node_id)
            if current_node:
                loc_name = current_node.name
        cfg = getattr(BoneConfig, "VILLAGE", None)
        l_warn = getattr(cfg, "TOWN_LATENCY_WARN", 3.0) if cfg else 3.0
        p_cfg = getattr(BoneConfig, "PHYSICS", None)
        v_high = getattr(p_cfg, "VOLTAGE_HIGH", 60.0) if p_cfg else 60.0
        d_heavy = getattr(p_cfg, "DRAG_HEAVY", 5.0) if p_cfg else 5.0
        if latency > l_warn:
            status = "HIGH_LATENCY"
            advice = ux("village_strings", "town_lag")
        elif packet.voltage > v_high:
            status = "HIGH_VOLTAGE"
            advice = random.choice(forecasts.get("HIGH_VOLTAGE", ["Manic energy."]))
        elif packet.narrative_drag > d_heavy:
            status = "HIGH_DRAG"
            advice = random.choice(forecasts.get("HIGH_DRAG", ["Narrative stuck."]))
        else:
            status = "BALANCED"
            advice = random.choice(forecasts.get("BALANCED", ["Nominal."]))
        census_fmt = ux("village_strings", "town_census")
        report = census_fmt.format(loc=loc_name, status=status, advice=advice) if census_fmt else ""
        news = self._get_town_news(latency, packet.voltage)
        if news:
            report += f"\n{news}"
        v_crit = getattr(cfg, "TOWN_VOLT_CRIT", 20.0) if cfg else 20.0
        v_low = getattr(cfg, "TOWN_VOLT_LOW", 2.0) if cfg else 2.0
        d_high = getattr(cfg, "TOWN_DRAG_HIGH", 5.0) if cfg else 5.0
        r_chance = getattr(cfg, "TOWN_RUMOR_CHANCE", 0.3) if cfg else 0.3
        if packet.voltage > v_crit:
            msg = ux("village_strings", "town_restrain")
            if msg: report += f"\n{Prisma.RED}{msg}{Prisma.RST}"
        elif packet.voltage < v_low and packet.narrative_drag > d_high:
            msg = ux("village_strings", "town_loops")
            if msg: report += f"\n{Prisma.MAG}{msg}{Prisma.RST}"
        elif status == "BALANCED" and self.rumors and random.random() < r_chance:
            rumor = random.choice(self.rumors)
            msg = ux("village_strings", "town_rumor")
            if msg: report += f"\n{Prisma.GRY}{msg.format(rumor=rumor)}{Prisma.RST}"
        return report.strip()

    @staticmethod
    def _get_town_news(latency: float, volt: float) -> Optional[str]:
        cfg = getattr(BoneConfig, "VILLAGE", None)
        news_lat = getattr(cfg, "TOWN_NEWS_LATENCY", 4.0) if cfg else 4.0
        if latency > news_lat:
            msg = ux("village_strings", "town_crier_slow")
            return f"{Prisma.OCHRE}{msg}{Prisma.RST}" if msg else None
        if volt > BoneConfig.PHYSICS.VOLTAGE_CRITICAL:
            msg = ux("village_strings", "town_crier_volt")
            return f"{Prisma.YEL}{msg}{Prisma.RST}" if msg else None
        return None

    def on_item_drop(self, payload):
        item = payload.get("item")
        if item:
            msg = ux("village_strings", "town_item_drop")
            if msg:
                self.events.log(msg.format(item=item), "VILLAGE")

    @staticmethod
    def diagnose_condition(
            session_data: dict, _host_health: Any = None, soul: Any = None) -> Tuple[str, str]:
        meta = session_data.get("meta", {})
        trauma = session_data.get("trauma_vector", {})
        final_health = meta.get("final_health", 50)
        cfg = getattr(BoneConfig, "VILLAGE", None)
        neg_crit = getattr(cfg, "TOWN_NEGLECT_CRIT", 8.0) if cfg else 8.0
        t_crit = getattr(cfg, "TOWN_TRAUMA_CRIT", 0.6) if cfg else 0.6
        h_crit = getattr(cfg, "TOWN_HEALTH_CRIT", 30) if cfg else 30
        if soul:
            neglect = soul.get("obsession_neglect", 0.0) if isinstance(soul, dict) else getattr(soul, "obsession_neglect", 0.0)
            if neglect > neg_crit:
                obsession = soul.get("current_obsession", "work") if isinstance(soul, dict) else getattr(soul, "current_obsession", "work")
                msg = ux("village_strings", "town_guilt")
                return "HIGH_DRAG", msg.format(obsession=obsession) if msg else ""
        if trauma:
            max_trauma = max(trauma, key=trauma.get) if trauma else "NONE"
            if trauma.get(max_trauma, 0) > t_crit:
                msg = ux("village_strings", "town_trauma")
                return "HIGH_TRAUMA", msg.format(trauma=max_trauma) if msg else ""
        if final_health < h_crit:
            msg = ux("village_strings", "town_critical")
            return "HIGH_TRAUMA", msg
        msg_nominal = ux("village_strings", "town_nominal")
        return "BALANCED", msg_nominal

class DeathGen:
    _FALLBACK_PROTOCOLS = {"PREFIXES": ["FATAL ERROR", "SYSTEM HALT", "THE END"],
                           "CAUSES": {"DEFAULT": ["Unknown Error", "Entropy limit reached"]},
                           "VERDICTS": {"DEFAULT": ["End of Line.", "Reboot required."]}, }

    @classmethod
    def load_protocols(cls):
        if LoreManifest.get_instance().get("DEATH") is None:
            LoreManifest.get_instance().inject("DEATH", cls._FALLBACK_PROTOCOLS)

    @staticmethod
    def eulogy(packet: PhysicsPacket, mito_state: Any, trauma_vector: Dict = None) -> Tuple[str, str]:
        death_data = LoreManifest.get_instance().get("DEATH")
        if not isinstance(death_data, dict):
            death_data = DeathGen._FALLBACK_PROTOCOLS
        cause = DeathGen._determine_cause(packet, mito_state, trauma_vector)
        verdict_type = DeathGen._determine_verdict_type(packet, cause)
        causes_dict = death_data.get("CAUSES", {})
        verdicts_dict = death_data.get("VERDICTS", {})
        prefix = random.choice(death_data.get("PREFIXES", ["Alas."]))
        causes = causes_dict.get(cause, causes_dict.get("DEFAULT", ["Error"]))
        verdicts = verdicts_dict.get(verdict_type, verdicts_dict.get("DEFAULT", ["Done."]))
        return f"{prefix} CAUSE: {random.choice(causes)}. {random.choice(verdicts)}", cause

    @staticmethod
    def _determine_cause(
            p: PhysicsPacket, mito_state: Any, trauma_vector: Dict = None) -> str:
        cfg = getattr(BoneConfig, "VILLAGE", None)
        t_crit = getattr(cfg, "DEATH_TRAUMA_CRIT", 50.0) if cfg else 50.0
        tox_crit = getattr(cfg, "DEATH_TOXICITY_CRIT", 5) if cfg else 5
        if trauma_vector and sum(trauma_vector.values()) > t_crit:
            return "TRAUMA"
        atp = float(
            mito_state.get("atp", 0)
            if isinstance(mito_state, dict)
            else getattr(mito_state, "atp_pool", 0))
        if atp <= BoneConfig.BIO.ATP_STARVATION:
            return "STARVATION"
        if p.voltage > BoneConfig.PHYSICS.VOLTAGE_CRITICAL:
            return "GLUTTONY"
        if p.narrative_drag > BoneConfig.PHYSICS.DRAG_HALT:
            return "BOREDOM"
        counts = p.counts or {}
        if counts.get("antigen", 0) > tox_crit:
            return "TOXICITY"
        return "STARVATION"

    @staticmethod
    def _determine_verdict_type(p: PhysicsPacket, cause: str) -> str:
        cfg = getattr(BoneConfig, "VILLAGE", None)
        psi_crit = getattr(cfg, "DEATH_ABSTRACT_PSI", 0.8) if cfg else 0.8
        val_crit = getattr(cfg, "DEATH_JOY_VALENCE", 0.6) if cfg else 0.6
        if cause == "GLUTTONY":
            return "THERMAL"
        if cause == "TOXICITY":
            return "ENTROPY"
        if getattr(p, "psi", 0.0) > psi_crit:
            return "ABSTRACT"
        if getattr(p, "valence", 0.0) > val_crit:
            return "JOY_CLADE"
        return "ENTROPY"