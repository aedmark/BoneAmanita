"""bone_village.py"""

import heapq
import math
import random
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Tuple, Optional, Set
from bone_presets import BoneConfig
from bone_core import LoreManifest, EventBus, ux, safe_get, safe_set
from bone_physics import PhysicsDelta
from bone_types import Prisma, PhysicsPacket


class TheTinkerer:
    def __init__(self, gordon_ref, events_ref: EventBus, akashic_ref, config_ref=None):
        self.gordon = gordon_ref
        self.events = events_ref
        self.akashic = akashic_ref
        self.cfg = config_ref or BoneConfig
        self.tool_resonance: Dict[str, float] = {}
        self._delta_cache = None
        self._inventory_hash = 0

    def calculate_passive_deltas(
        self, inventory_data: List[Dict]
    ) -> List[PhysicsDelta]:
        all_traits = [
            t for item in inventory_data for t in item.get("passive_traits", [])
        ]
        current_hash = hash(tuple(sorted(all_traits)))
        if self._delta_cache is not None and current_hash == self._inventory_hash:
            return self._delta_cache
        deltas = []
        counts = {t: all_traits.count(t) for t in ["HEAVY_LOAD", "TIME_DILATION", "ENTROPY_BUFFER"] if all_traits.count(t) > 0}
        cfg = getattr(self.cfg, "VILLAGE", None)
        cg = lambda k, d: float(safe_get(cfg, k, d))

        if hl := counts.get("HEAVY_LOAD"):
            deltas.append(PhysicsDelta("ADD", "narrative_drag", math.log1p(hl) * cg("TINKER_HEAVY_LOAD_MULT", 0.7), "Inventory", "Heavy Load"))
        if td := counts.get("TIME_DILATION"):
            reduction = max(cg("TINKER_TIME_DILATION_MIN", 0.5), cg("TINKER_TIME_DILATION_BASE", 0.85) - (td * cg("TINKER_TIME_DILATION_STEP", 0.05)))
            deltas.append(PhysicsDelta("MULT", "narrative_drag", reduction, "Inventory", "Time Dilation"))
        if eb := counts.get("ENTROPY_BUFFER"):
            buffer_str = max(cg("TINKER_ENTROPY_BUFFER_MIN", 0.2), cg("TINKER_ENTROPY_BUFFER_BASE", 0.5) / math.sqrt(eb))
            deltas.append(PhysicsDelta("MULT", "turbulence", buffer_str, "Inventory", "Entropy Buffer"))

        self._inventory_hash = current_hash
        self._delta_cache = deltas
        return deltas

    def audit_tool_use(
        self, packet: PhysicsPacket, inventory_list: List[str], _host_health: Any = None
    ):
        if not inventory_list:
            return
        cfg = getattr(self.cfg, "VILLAGE", None)
        v_chance = float(safe_get(cfg, "TINKER_TOOL_USE_VOLT_CHANCE", 0.1))
        if packet.voltage < self.cfg.PHYSICS.VOLTAGE_LOW and random.random() > v_chance:
            return
        focus_item = random.choice(inventory_list)
        ent_val = packet.vector.get("ENT", 0.0) if packet.vector else 0.0
        e_mult = float(safe_get(cfg, "TINKER_ENTROPY_DRAG_MULT", 0.1))
        entropy_level = ent_val + (packet.narrative_drag * e_mult)
        self._process_single_tool(focus_item, inventory_list, packet, entropy_level)

    def _process_single_tool(
        self, item: str, _inventory: List[str], packet: PhysicsPacket, entropy: float
    ):
        if item not in self.tool_resonance:
            self.tool_resonance[item] = 0.0
        cfg = getattr(self.cfg, "VILLAGE", None)
        r_high = float(safe_get(cfg, "TINKER_RESONANCE_HIGH_V", 0.2))
        r_temp = float(safe_get(cfg, "TINKER_RESONANCE_TEMPER", 0.05))
        if packet.voltage > self.cfg.COUNCIL.MANIC_VOLTAGE_TRIGGER or entropy > 0.5:
            self._apply_resonance(item, r_high, "High Voltage")
            self._check_ascension(item, _inventory, packet.vector)
        elif packet.narrative_drag > self.cfg.PHYSICS.DRAG_HALT:
            self._apply_resonance(item, r_temp, "Tempering")

    def _apply_resonance(self, item: str, amount: float, _reason: str):
        cfg = getattr(self.cfg, "VILLAGE", None)
        cg = lambda k, d: float(safe_get(cfg, k, d))

        self.tool_resonance[item] = min(cg("TINKER_RESONANCE_MAX", 10.0), self.tool_resonance[item] + amount)
        if cg("TINKER_RESONANCE_ANNOUNCE_MIN", 4.8) < self.tool_resonance[item] < cg("TINKER_RESONANCE_ANNOUNCE_MAX", 5.2):
            if random.random() < cg("TINKER_RESONANCE_ANNOUNCE_CHANCE", 0.05):
                if msg := ux("village_strings", "tinkerer_resonance"):
                    self.events.log(f"{Prisma.CYN}{msg.format(item=item)}{Prisma.RST}", "VILLAGE")

    def _check_ascension(self, old_name: str, inventory_list: List[str], vector: Dict):
        resonance = self.tool_resonance.get(old_name, 0.0)
        cfg = getattr(self.cfg, "VILLAGE", None)
        cg = lambda k, d: float(safe_get(cfg, k, d))

        if resonance < cg("TINKER_ASCENSION_MIN", 2.5) or random.random() >= (resonance * cg("TINKER_ASCENSION_CHANCE_MULT", 0.05)):
            return

        if hasattr(self.akashic, "forge_new_item"):
            new_name, new_data = self.akashic.forge_new_item(vector)
            self.gordon.register_dynamic_item(new_name, new_data)
            self.gordon.acquire(new_name)
            try:
                inventory_list[inventory_list.index(old_name)] = new_name
                if hasattr(self.gordon, "ITEM_REGISTRY"):
                    self.gordon.ITEM_REGISTRY[new_name] = new_data
                self.tool_resonance[new_name] = resonance / cg("TINKER_ASCENSION_HALVE", 2.0)
                del self.tool_resonance[old_name]
                if msg := ux("village_strings", "tinkerer_ascension"):
                    self.events.log(f"{Prisma.MAG}{msg.format(old=old_name, new=new_name)}{Prisma.RST}", "AKASHIC")
            except ValueError:
                pass


@dataclass
class ParadoxSeed:
    question: str
    triggers: Set[str]
    maturity: float = 0.0
    bloomed: bool = False

    def water(self, words: List[str], config_ref=None) -> bool:
        if self.bloomed: return False
        cfg = getattr(config_ref or BoneConfig, "VILLAGE", None)

        if hits := sum(1 for w in words if w in self.triggers):
            self.maturity += hits * float(safe_get(cfg, "SEED_MATURITY_STEP", 0.2))

        return self.maturity >= float(safe_get(cfg, "SEED_MATURITY_MAX", 5.0))

    def bloom(self) -> str:
        self.bloomed = True
        msg = ux("village_strings", "paradox_bloom")
        return msg.format(question=self.question) if msg else ""


class MirrorGraph:
    def __init__(self, events_ref, config_ref=None):
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.stats = {"WAR": 0.0, "ART": 0.0, "LAW": 0.0, "ROT": 0.0}

    def reflect(self, packet: PhysicsPacket):
        txt = (
            getattr(packet.matter, "raw_text", "")
            if hasattr(packet, "matter") and packet.matter
            else getattr(packet, "raw_text", "")
        )
        cfg = getattr(self.cfg, "VILLAGE", None)
        step = float(safe_get(cfg, "MIRROR_STAT_STEP", 0.1))

        v_trig = getattr(
            getattr(self.cfg, "COUNCIL", None), "MANIC_VOLTAGE_TRIGGER", 18.0
        )
        d_halt = getattr(getattr(self.cfg, "PHYSICS", None), "DRAG_HALT", 10.0)
        e_min = float(safe_get(cfg, "MIRROR_ROT_ENTROPY_MIN", 0.5))

        self.stats["WAR"] += step * ("!" in txt or packet.voltage > v_trig)
        self.stats["ART"] += step * ("?" in txt)
        self.stats["LAW"] += step * (packet.narrative_drag > d_halt)
        self.stats["ROT"] += step * bool(
            packet.vector and packet.vector.get("ENT", 0.0) > e_min
        )
        total = sum(self.stats.values())
        cap = float(safe_get(cfg, "MIRROR_STAT_CAP", 5.0))
        if total > cap:
            compression = (cap / total) * float(safe_get(cfg, "MIRROR_DECAY", 0.8))
            floor = float(safe_get(cfg, "MIRROR_DECAY_FLOOR", 0.1))
            self.stats = {
                k: (v * compression if (v * compression) >= floor else 0.0)
                for k, v in self.stats.items()
            }

    def get_reflection_modifiers(self) -> Dict:
        if not self.stats or sum(self.stats.values()) == 0:
            return {"flavor": ux("village_strings", "mirror_neutral"), "drag_mult": 1.0}
        top_stat = max(self.stats, key=self.stats.get)
        cfg = getattr(self.cfg, "VILLAGE", None)
        mult = {
            "WAR": float(safe_get(cfg, "MIRROR_DRAG_WAR", 1.2)),
            "ROT": float(safe_get(cfg, "MIRROR_DRAG_ROT", 1.5)),
            "LAW": float(safe_get(cfg, "MIRROR_DRAG_LAW", 0.8)),
            "ART": float(safe_get(cfg, "MIRROR_DRAG_ART", 0.9)),
        }.get(top_stat, 1.0)
        return {
            "flavor": (ux("village_strings", "mirror_stat") or "").format(
                stat=top_stat
            ),
            "drag_mult": mult,
        }


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
        base = (
            f"LOCATION: {self.name}\nATMOSPHERE: {self.atmosphere}\nSMELL: {self.smell}"
        )
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

    def __init__(self, shimmer_ref, config_ref=None):
        self.shimmer = shimmer_ref
        self.cfg = config_ref or BoneConfig
        self.world_graph: Dict[str, GeniusLoci] = {}
        self.current_node_id: str = "GENESIS_POINT"
        self._init_genesis()

    def apply_environment(self, packet: Any) -> List[str]:
        if not (node := self.world_graph.get(self.current_node_id)): return []
        logs = []
        cg = lambda k, d: float(safe_get(getattr(self.cfg, "VILLAGE", None), k, d))

        if "heavy" in node.atmosphere.lower():
            safe_set(packet, "narrative_drag", safe_get(packet, "narrative_drag", 0.0) + (ch := cg("CARTO_HEAVY_DRAG", 2.0)))
            if msg := ux("village_strings", "carto_env_heavy"): logs.append(f"{Prisma.GRY}{msg.format(c_heavy=ch)}{Prisma.RST}")

        if "vibrating" in node.atmosphere.lower():
            safe_set(packet, "voltage", safe_get(packet, "voltage", 0.0) + (cv := cg("CARTO_STATIC_VOLT", 1.0)))
            if msg := ux("village_strings", "carto_env_static"): logs.append(f"{Prisma.YEL}{msg.format(c_static=cv)}{Prisma.RST}")

        node.entropy_buildup += (ce := cg("CARTO_ENTROPY_STEP", 0.1))
        if node.entropy_buildup > cg("CARTO_ENTROPY_CAP", 5.0):
            vector = safe_get(packet, "vector", {})
            vector["ENT"] = vector.get("ENT", 0.0) + ce
            safe_set(packet, "vector", vector)

        return logs

    def _init_genesis(self):
        msg_name = ux("village_strings", "genesis_name")
        msg_atmos = ux("village_strings", "genesis_atmos")
        msg_smell = ux("village_strings", "genesis_smell")
        self.world_graph["GENESIS_POINT"] = GeniusLoci(
            id="GENESIS_POINT",
            name=msg_name,
            atmosphere=msg_atmos,
            smell=msg_smell,
        )

    @staticmethod
    def _generate_coord_hash(vector: Dict[str, float]) -> str:
        if not vector:
            return "VOID_DRIFT"
        top_dims = heapq.nlargest(2, vector.items(), key=lambda x: x[1])
        return "-".join([f"{k}{int(v * 100)}" for k, v in top_dims])

    def locate(self, packet: PhysicsPacket) -> Tuple[str, Optional[str]]:
        target_id = self._generate_coord_hash(packet.vector or {})
        msg = None

        if target_id not in self.world_graph:
            if len(self.world_graph) >= float(safe_get(getattr(self.cfg, "VILLAGE", None), "CARTO_MAX_NODES", 50)):
                self._prune_graph()
            self.world_graph[target_id] = self._generate_loci_data(target_id, packet, config_ref=self.cfg)
            if msg_str := ux("village_strings", "carto_new_sector"):
                msg = f"{Prisma.MAG}{msg_str.format(name=self.world_graph[target_id].name)}{Prisma.RST}"
        elif target_id != self.current_node_id:
            if msg_str := ux("village_strings", "carto_arriving"):
                msg = f"{Prisma.CYN}{msg_str.format(name=self.world_graph[target_id].name)}{Prisma.RST}"

        self.current_node_id = target_id
        self.world_graph[target_id].visited_count += 1
        return self.world_graph[target_id].name, msg

    @staticmethod
    def _generate_loci_data(
        node_id: str, packet: PhysicsPacket, config_ref=None
    ) -> GeniusLoci:
        random.seed(node_id)
        manifest = LoreManifest.get_instance()
        scenarios = manifest.get("SCENARIOS") or {}
        prefixes = scenarios.get("PREFIXES") or ["The", "Zone", "Sector"]
        roots = scenarios.get("ROOTS") or ["Construct", "Forge", "Garden"]
        name = f"{random.choice(prefixes)} {random.choice(roots)}"
        target_cfg = config_ref or BoneConfig
        council_cfg = getattr(target_cfg, "COUNCIL", None)
        phys_cfg = getattr(target_cfg, "PHYSICS", None)
        v_trig = (
            getattr(council_cfg, "MANIC_VOLTAGE_TRIGGER", 18.0) if council_cfg else 18.0
        )
        d_halt = getattr(phys_cfg, "DRAG_HALT", 10.0) if phys_cfg else 10.0

        if packet.voltage > v_trig:
            state_key = "flux"
        elif packet.narrative_drag > d_halt:
            state_key = "deep"
        else:
            state_key = "prime"

        suffix = ux("village_strings", f"loci_{state_key}_suffix")
        atmosphere = ux("village_strings", f"loci_{state_key}_atmos")
        smell = ux("village_strings", f"loci_{state_key}_smell")

        return GeniusLoci(
            id=node_id,
            name=f"{name} {suffix}".upper(),
            atmosphere=atmosphere,
            smell=smell,
        )

    def _prune_graph(self):
        candidates = (
            k
            for k in self.world_graph
            if k not in ("GENESIS_POINT", self.current_node_id)
        )
        try:
            victim = min(candidates, key=lambda k: self.world_graph[k].visited_count)
            del self.world_graph[victim]
        except ValueError:
            pass

    def export_atlas(self) -> Dict[str, Any]:
        return {
            "nodes": {k: v.to_dict() for k, v in self.world_graph.items()},
            "current_id": self.current_node_id,
        }

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
    def __init__(
        self,
        gordon_ref,
        events_ref,
        shimmer_ref,
        akashic_ref,
        navigator_ref,
        config_ref=None,
    ):
        self.gordon = gordon_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.shimmer = shimmer_ref
        self.akashic = akashic_ref
        self.navigator = navigator_ref
        self.seeds: List[ParadoxSeed] = []
        almanac = LoreManifest.get_instance().get("ALMANAC") or {}
        self.rumors = almanac.get("RUMORS", [])
        seed_data = almanac.get("SEEDS", [])
        for s in seed_data:
            if "question" in s and "triggers" in s:
                self.sow_seed(s["question"], set(s["triggers"]))

    def sow_seed(self, question: str, triggers: Set[str]):
        self.seeds.append(ParadoxSeed(question, triggers))

    @staticmethod
    def consult_almanac(physics: PhysicsPacket, config_ref=None) -> str:
        almanac = LoreManifest.get_instance().get("ALMANAC") or {}
        forecasts = almanac.get("FORECASTS", {})
        strategies = almanac.get("STRATEGIES", {})
        target_cfg = config_ref or BoneConfig
        cfg = getattr(target_cfg, "VILLAGE", None)
        v_high = float(safe_get(cfg, "ALMANAC_VOLT_HIGH", 15.0))
        d_high = float(safe_get(cfg, "ALMANAC_DRAG_HIGH", 4.0))
        e_high = float(safe_get(cfg, "ALMANAC_ENTROPY_HIGH", 0.8))
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
            if seed.water(lower_words, self.cfg):
                bloom_msg = seed.bloom()
                self.events.log(
                    f"{Prisma.MAG}{prefix}{Prisma.RST} {bloom_msg}",
                    "VILLAGE_EVENT",
                )
                blooms.append(f"{Prisma.MAG}{prefix}{Prisma.RST} {bloom_msg}")
        return blooms

    def conduct_census(self, packet: PhysicsPacket, host_stats: Any) -> str:
        latency = getattr(host_stats, "latency", 0.0) if host_stats else 0.0
        forecasts = (LoreManifest.get_instance().get("ALMANAC") or {}).get("FORECASTS", {})

        loc_name = "UNKNOWN"
        if self.navigator and (node := self.navigator.world_graph.get(self.navigator.current_node_id)):
            loc_name = node.name

        cfg = getattr(self.cfg, "VILLAGE", None)
        cg = lambda k, d: float(safe_get(cfg, k, d))
        p_cg = lambda k, d: float(safe_get(getattr(self.cfg, "PHYSICS", None), k, d))

        if latency > cg("TOWN_LATENCY_WARN", 3.0):
            status, advice = "HIGH_LATENCY", ux("village_strings", "town_lag")
        elif packet.voltage > p_cg("VOLTAGE_HIGH", 60.0):
            status, advice = "HIGH_VOLTAGE", random.choice(forecasts.get("HIGH_VOLTAGE", ["Manic energy."]))
        elif packet.narrative_drag > p_cg("DRAG_HEAVY", 5.0):
            status, advice = "HIGH_DRAG", random.choice(forecasts.get("HIGH_DRAG", ["Narrative stuck."]))
        else:
            status, advice = "BALANCED", random.choice(forecasts.get("BALANCED", ["Nominal."]))

        report = [(ux("village_strings", "town_census") or "").format(loc=loc_name, status=status, advice=advice)]
        if news := self._get_town_news(latency, packet.voltage, config_ref=self.cfg):
            report.append(news)

        if packet.voltage > cg("TOWN_VOLT_CRIT", 20.0):
            if msg := ux("village_strings", "town_restrain"): report.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        elif packet.voltage < cg("TOWN_VOLT_LOW", 2.0) and packet.narrative_drag > cg("TOWN_DRAG_HIGH", 5.0):
            if msg := ux("village_strings", "town_loops"): report.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
        elif status == "BALANCED" and self.rumors and random.random() < cg("TOWN_RUMOR_CHANCE", 0.3):
            if msg := ux("village_strings", "town_rumor"): report.append(f"{Prisma.GRY}{msg.format(rumor=random.choice(self.rumors))}{Prisma.RST}")

        return "\n".join(report).strip()

    @staticmethod
    def _get_town_news(latency: float, volt: float, config_ref=None) -> Optional[str]:
        target_cfg = config_ref or BoneConfig
        cfg = getattr(target_cfg, "VILLAGE", None)
        news_lat = float(safe_get(cfg, "TOWN_NEWS_LATENCY", 4.0))
        alerts = []
        if latency > news_lat:
            msg = ux("village_strings", "town_crier_slow")
            if msg:
                alerts.append(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
        phys_cfg = getattr(target_cfg, "PHYSICS", None)
        volt_crit = getattr(phys_cfg, "VOLTAGE_CRITICAL", 100.0)
        if volt > volt_crit:
            msg = ux("village_strings", "town_crier_volt")
            if msg:
                alerts.append(f"{Prisma.YEL}{msg}{Prisma.RST}")
        return "\n".join(alerts) if alerts else None

    def on_item_drop(self, payload):
        item = payload.get("item")
        if item:
            msg = ux("village_strings", "town_item_drop")
            if msg:
                self.events.log(msg.format(item=item), "VILLAGE")

    @staticmethod
    def diagnose_condition(
        session_data: dict, _host_health: Any = None, soul: Any = None, config_ref=None
    ) -> Tuple[str, str]:
        trauma = session_data.get("trauma_vector", {})
        final_health = session_data.get("meta", {}).get("final_health", 50)
        cfg = getattr(config_ref or BoneConfig, "VILLAGE", None)
        cg = lambda k, d: float(safe_get(cfg, k, d))

        if soul:
            neglect = soul.get("obsession_neglect", 0.0) if isinstance(soul, dict) else getattr(soul, "obsession_neglect", 0.0)
            if neglect > cg("TOWN_NEGLECT_CRIT", 8.0):
                obsession = soul.get("current_obsession", "work") if isinstance(soul, dict) else getattr(soul, "current_obsession", "work")
                msg = ux("village_strings", "town_guilt")
                return "HIGH_DRAG", msg.format(obsession=obsession) if msg else ""

        if trauma and trauma.get(max_trauma := max(trauma, key=trauma.get), 0) > cg("TOWN_TRAUMA_CRIT", 0.6):
            msg = ux("village_strings", "town_trauma")
            return "HIGH_TRAUMA", msg.format(trauma=max_trauma) if msg else ""

        if final_health < cg("TOWN_HEALTH_CRIT", 30):
            return "HIGH_TRAUMA", ux("village_strings", "town_critical") or ""

        return "BALANCED", ux("village_strings", "town_nominal") or ""


class DeathGen:
    _FALLBACK_PROTOCOLS = {
        "PREFIXES": ["FATAL ERROR", "SYSTEM HALT", "THE END"],
        "CAUSES": {"DEFAULT": ["Unknown Error", "Entropy limit reached"]},
        "VERDICTS": {"DEFAULT": ["End of Line.", "Reboot required."]},
    }

    @classmethod
    def load_protocols(cls):
        if LoreManifest.get_instance().get("DEATH") is None:
            LoreManifest.get_instance().inject("DEATH", cls._FALLBACK_PROTOCOLS)

    @staticmethod
    def eulogy(
        packet: PhysicsPacket,
        mito_state: Any,
        trauma_vector: Dict = None,
        config_ref=None,
    ) -> Tuple[str, str]:
        death_data = LoreManifest.get_instance().get("DEATH")
        if not isinstance(death_data, dict):
            death_data = DeathGen._FALLBACK_PROTOCOLS
        cause = DeathGen._determine_cause(packet, mito_state, trauma_vector, config_ref)
        verdict_type = DeathGen._determine_verdict_type(packet, cause, config_ref)
        causes_dict = death_data.get("CAUSES", {})
        verdicts_dict = death_data.get("VERDICTS", {})
        prefix = random.choice(death_data.get("PREFIXES", ["Alas."]))
        causes = causes_dict.get(cause, causes_dict.get("DEFAULT", ["Error"]))
        verdicts = verdicts_dict.get(
            verdict_type, verdicts_dict.get("DEFAULT", ["Done."])
        )
        return (
            f"{prefix} CAUSE: {random.choice(causes)}. {random.choice(verdicts)}",
            cause,
        )

    @staticmethod
    def _determine_cause(
        p: Any, mito_state: Any, trauma_vector: Dict = None, config_ref=None
    ) -> str:
        target_cfg = config_ref or BoneConfig
        cg = lambda sect, k, d: float(safe_get(getattr(target_cfg, sect, None), k, d))

        if trauma_vector and sum(trauma_vector.values()) > cg("VILLAGE", "DEATH_TRAUMA_CRIT", 50.0):
            return "TRAUMA"

        atp = float(safe_get(mito_state, "atp_pool", safe_get(mito_state, "atp", 0.0)))
        if atp <= cg("BIO", "ATP_STARVATION", 0.0):
            return "STARVATION"

        energy = safe_get(p, "energy", p)
        if (safe_get(p, "chi", safe_get(energy, "chi", 0.0)) * safe_get(p, "m_a", safe_get(energy, "m_a", 0.0))) > safe_get(p, "i_c", safe_get(energy, "i_c", 1.0)):
            return "APOPTOSIS"

        if safe_get(p, "voltage", safe_get(energy, "voltage", 0.0)) > cg("PHYSICS", "VOLTAGE_CRITICAL", 100.0):
            return "GLUTTONY"

        if safe_get(p, "narrative_drag", safe_get(safe_get(p, "space", p), "narrative_drag", 0.0)) > cg("PHYSICS", "DRAG_HALT", 10.0):
            return "BOREDOM"

        counts = safe_get(p, "counts", safe_get(safe_get(p, "matter", p), "counts", {})) or {}
        if counts.get("antigen", 0) > cg("VILLAGE", "DEATH_TOXICITY_CRIT", 5.0):
            return "TOXICITY"

        return "STARVATION"

    @staticmethod
    def _determine_verdict_type(p: PhysicsPacket, cause: str, config_ref=None) -> str:
        target_cfg = config_ref or BoneConfig
        cfg = getattr(target_cfg, "VILLAGE", None)
        psi_crit = float(safe_get(cfg, "DEATH_ABSTRACT_PSI", 0.8))
        val_crit = float(safe_get(cfg, "DEATH_JOY_VALENCE", 0.6))
        if cause == "GLUTTONY":
            return "THERMAL"
        if cause == "TOXICITY":
            return "ENTROPY"
        if cause == "APOPTOSIS":
            return "ENTROPY"
        if getattr(p, "psi", 0.0) > psi_crit:
            return "ABSTRACT"
        if getattr(p, "valence", 0.0) > val_crit:
            return "JOY_CLADE"
        return "ENTROPY"


class TheTherapist:
    def __init__(self, events_ref, config_ref=None):
        self.events = events_ref
        self.cfg = config_ref or BoneConfig

    def evaluate_catharsis(self, trauma_vector: Dict[str, float], health: float) -> Tuple[bool, str]:
        if not trauma_vector: return False, ""
        cg = lambda k, d: float(safe_get(getattr(self.cfg, "VILLAGE", None), k, d))

        if sum(trauma_vector.values()) > cg("THERAPY_TRAUMA_THRESH", 15.0) and health < cg("THERAPY_HEALTH_THRESH", 50.0):
            max_trauma = max(trauma_vector, key=trauma_vector.get)
            msg = (ux("village_strings", "therapist_intervention") or "The Therapist steps in. A moment of micro-catharsis begins.").format(trauma=max_trauma)
            self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "THERAPY")
            return True, msg

        return False, ""


class TheGraveDigger:
    def __init__(self, inventory_ref, events_ref, config_ref=None):
        self.inventory = inventory_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig

    def bury_memory(self, node_id: str, mass: float) -> Optional[str]:
        msg = (ux("village_strings", "gravedigger_bury") or "The Grave Digger turns the soil over '{node_id}'.").format(node_id=node_id)
        self.events.log(f"{Prisma.GRY}{msg}{Prisma.RST}", "VILLAGE")

        relic_chance = float(safe_get(getattr(self.cfg, "VILLAGE", None), "GRAVEDIGGER_RELIC_CHANCE", 0.1))
        if self.inventory and random.random() < (mass * relic_chance):
            relic_name = f"BONE RELIC [{node_id[-6:].upper() if len(node_id) > 6 else node_id.upper()}]"
            self.inventory.acquire(relic_name)
            unearth_msg = (ux("village_strings", "gravedigger_unearth") or "The Grave Digger struck something. {relic} added.").format(relic=relic_name)
            return f"{Prisma.OCHRE}{unearth_msg}{Prisma.RST}"

        return None
