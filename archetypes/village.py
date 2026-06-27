"""archetypes/village.py"""

import heapq
import math
import random
from collections import Counter
from dataclasses import asdict, dataclass, field
from itertools import chain
from typing import Any, Dict, List, Optional, Set, Tuple

from constants import Prisma
from core import EventBus, LoreManifest, safe_get, ux
from physics import PhysicsDelta
from physics.models import PhysicsPacket
from presets import BoneConfig


def _cfg_val(cfg_ref, section: str, key: str, default: float) -> float:
    return float(safe_get(safe_get(cfg_ref or BoneConfig, section, {}), key, default))


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
        counts = Counter(
            chain.from_iterable(
                item.get("passive_traits") or [] for item in inventory_data
            )
        )
        current_hash = hash(frozenset(counts.items()))
        if self._delta_cache is not None and current_hash == self._inventory_hash:
            return self._delta_cache
        deltas = []
        if hl := counts.get("HEAVY_LOAD"):
            deltas.append(
                PhysicsDelta(
                    "ADD",
                    "narrative_drag",
                    math.log1p(hl)
                    * _cfg_val(self.cfg, "VILLAGE", "TINKER_HEAVY_LOAD_MULT", 0.7),
                    "Inventory",
                    "Heavy Load",
                )
            )
        if td := counts.get("TIME_DILATION"):
            reduction = max(
                _cfg_val(self.cfg, "VILLAGE", "TINKER_TIME_DILATION_MIN", 0.5),
                _cfg_val(self.cfg, "VILLAGE", "TINKER_TIME_DILATION_BASE", 0.85)
                - (
                    td
                    * _cfg_val(self.cfg, "VILLAGE", "TINKER_TIME_DILATION_STEP", 0.05)
                ),
            )
            deltas.append(
                PhysicsDelta(
                    "MULT", "narrative_drag", reduction, "Inventory", "Time Dilation"
                )
            )
        if eb := counts.get("ENTROPY_BUFFER"):
            buffer_str = max(
                _cfg_val(self.cfg, "VILLAGE", "TINKER_ENTROPY_BUFFER_MIN", 0.2),
                _cfg_val(self.cfg, "VILLAGE", "TINKER_ENTROPY_BUFFER_BASE", 0.5)
                / math.sqrt(eb),
            )
            deltas.append(
                PhysicsDelta(
                    "MULT", "turbulence", buffer_str, "Inventory", "Entropy Buffer"
                )
            )
        self._inventory_hash, self._delta_cache = current_hash, deltas
        return deltas

    def audit_tool_use(
        self, packet: PhysicsPacket, inventory_list: List[str], _host_health: Any = None
    ):
        if not inventory_list:
            return
        cfg = safe_get(self.cfg, "VILLAGE", {})
        v_chance = float(safe_get(cfg, "TINKER_TOOL_USE_VOLT_CHANCE", 0.1))
        v_low = _cfg_val(self.cfg, "PHYSICS", "VOLTAGE_LOW", 5.0)
        if packet.voltage < v_low and random.random() > v_chance:
            return
        focus_item = random.choice(inventory_list)
        ent_val = packet.vector.get("ENT", 0.0) if packet.vector else 0.0
        e_mult = float(safe_get(cfg, "TINKER_ENTROPY_DRAG_MULT", 0.1))
        entropy_level = ent_val + (packet.narrative_drag * e_mult)
        self._process_single_tool(focus_item, inventory_list, packet, entropy_level)

    def _process_single_tool(
        self, item: str, _inventory: List[str], packet: PhysicsPacket, entropy: float
    ):
        self.tool_resonance.setdefault(item, 0.0)
        if (
            packet.voltage
            > _cfg_val(self.cfg, "COUNCIL", "MANIC_VOLTAGE_TRIGGER", 18.0)
            or entropy > 0.5
        ):
            self._apply_resonance(
                item, _cfg_val(self.cfg, "VILLAGE", "TINKER_RESONANCE_HIGH_V", 0.2)
            )
            self._check_ascension(item, _inventory, packet.vector)
        elif packet.narrative_drag > _cfg_val(self.cfg, "PHYSICS", "DRAG_HALT", 10.0):
            self._apply_resonance(
                item, _cfg_val(self.cfg, "VILLAGE", "TINKER_RESONANCE_TEMPER", 0.05)
            )

    def _apply_resonance(self, item: str, amount: float):
        self.tool_resonance[item] = min(
            _cfg_val(self.cfg, "VILLAGE", "TINKER_RESONANCE_MAX", 10.0),
            self.tool_resonance[item] + amount,
        )
        if (
            _cfg_val(self.cfg, "VILLAGE", "TINKER_RESONANCE_ANNOUNCE_MIN", 4.8)
            < self.tool_resonance[item]
            < _cfg_val(self.cfg, "VILLAGE", "TINKER_RESONANCE_ANNOUNCE_MAX", 5.2)
        ):
            if random.random() < _cfg_val(
                self.cfg, "VILLAGE", "TINKER_RESONANCE_ANNOUNCE_CHANCE", 0.05
            ):
                if msg := ux("village_strings", "tinkerer_resonance"):
                    self.events.log(
                        f"{Prisma.CYN}{msg.format(item=item)}{Prisma.RST}", "VILLAGE"
                    )

    def _check_ascension(self, old_name: str, inventory_list: List[str], vector: Dict):
        resonance = self.tool_resonance.get(old_name, 0.0)
        if resonance < _cfg_val(
            self.cfg, "VILLAGE", "TINKER_ASCENSION_MIN", 2.5
        ) or random.random() >= (
            resonance
            * _cfg_val(self.cfg, "VILLAGE", "TINKER_ASCENSION_CHANCE_MULT", 0.05)
        ):
            return
        if hasattr(self.akashic, "forge_new_item"):
            new_name, new_data = self.akashic.forge_new_item(vector)
            self.gordon.register_dynamic_item(new_name, new_data)
            self.gordon.acquire(new_name)
            if hasattr(self.gordon, "safe_remove_item"):
                self.gordon.safe_remove_item(old_name)
            if old_name in inventory_list:
                inventory_list[inventory_list.index(old_name)] = new_name
            self.tool_resonance[new_name] = resonance / _cfg_val(
                self.cfg, "VILLAGE", "TINKER_ASCENSION_HALVE", 2.0
            )
            self.tool_resonance.pop(old_name, None)
            if msg := ux("village_strings", "tinkerer_ascension"):
                self.events.log(
                    f"{Prisma.MAG}{msg.format(old=old_name, new=new_name)}{Prisma.RST}",
                    "AKASHIC",
                )


@dataclass
class ParadoxSeed:
    question: str
    triggers: Set[str]
    maturity: float = 0.0
    bloomed: bool = False

    def water(self, word_counts: Dict[str, int], config_ref=None) -> bool:
        if self.bloomed:
            return False
        if hits := sum(word_counts[t] for t in self.triggers if t in word_counts):
            self.maturity = float(self.maturity) + (
                float(hits) * _cfg_val(config_ref, "VILLAGE", "SEED_MATURITY_STEP", 0.2)
            )
        return self.maturity >= _cfg_val(
            config_ref, "VILLAGE", "SEED_MATURITY_MAX", 5.0
        )

    def bloom(self) -> str:
        self.bloomed = True
        msg = ux("village_strings", "paradox_bloom")
        return msg.format(question=self.question) if msg else ""


@dataclass
class GeniusLoci:
    id: str
    name: str
    atmosphere: str
    smell: str
    local_items: List[str] = field(default_factory=list)
    visited_count: int = 0
    entropy_buildup: float = 0.0
    state_key: str = "prime"

    def description(self) -> str:
        parts = [
            f"LOCATION: {self.name}",
            f"ATMOSPHERE: {self.atmosphere}",
            f"SMELL: {self.smell}",
        ]
        if self.local_items:
            parts.append(f"VISIBLE ITEMS: {', '.join(self.local_items)}")
        return "\n".join(parts)

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

    def apply_environment(self, packet: PhysicsPacket) -> List[str]:
        if not (node := self.world_graph.get(self.current_node_id)):
            return []
        logs = []
        if node.state_key == "deep":
            ch = _cfg_val(self.cfg, "VILLAGE", "CARTO_HEAVY_DRAG", 2.0)
            packet.narrative_drag += ch
            if msg := ux("village_strings", "carto_env_heavy"):
                logs.append(f"{Prisma.GRY}{msg.format(c_heavy=ch)}{Prisma.RST}")
        if node.state_key == "flux":
            cv = _cfg_val(self.cfg, "VILLAGE", "CARTO_STATIC_VOLT", 1.0)
            packet.voltage += cv
            if msg := ux("village_strings", "carto_env_static"):
                logs.append(f"{Prisma.YEL}{msg.format(c_static=cv)}{Prisma.RST}")
        ce = _cfg_val(self.cfg, "VILLAGE", "CARTO_ENTROPY_STEP", 0.1)
        node.entropy_buildup = float(node.entropy_buildup) + ce
        if node.entropy_buildup > _cfg_val(
            self.cfg, "VILLAGE", "CARTO_ENTROPY_CAP", 5.0
        ):
            if packet.vector is not None:
                packet.vector["ENT"] = min(
                    1.0, packet.vector.get("ENT", 0.0) + node.entropy_buildup
                )
            node.entropy_buildup = 0.0
        return logs

    def _init_genesis(self):
        msg_name = ux("village_strings", "genesis_name") or "The White Room"
        msg_atmos = ux("village_strings", "genesis_atmos") or "Sterile, expectant."
        msg_smell = ux("village_strings", "genesis_smell") or "Ozone."
        self.world_graph["GENESIS_POINT"] = GeniusLoci(
            id="GENESIS_POINT", name=msg_name, atmosphere=msg_atmos, smell=msg_smell
        )

    @staticmethod
    def _generate_coord_hash(vector: Dict[str, float]) -> str:
        if not vector:
            return "VOID_DRIFT"
        top_dims = heapq.nlargest(2, vector.items(), key=lambda x: abs(x[1]))
        return "-".join([f"{k}{int(round(v, 1) * 10):02d}" for k, v in top_dims])

    def locate(self, packet: PhysicsPacket) -> Tuple[str, Optional[str]]:
        target_id = self._generate_coord_hash(packet.vector or {})
        msg = None
        if target_id not in self.world_graph:
            if len(self.world_graph) >= _cfg_val(
                self.cfg, "VILLAGE", "CARTO_MAX_NODES", 50
            ):
                self._prune_graph()
            self.world_graph[target_id] = self._generate_loci_data(
                target_id, packet, config_ref=self.cfg
            )
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
        rng = random.Random(node_id)
        scenarios = LoreManifest.get_instance().get("SCENARIOS") or {}
        name = f"{rng.choice(scenarios.get('PREFIXES', ['The', 'Zone', 'Sector']))} {rng.choice(scenarios.get('ROOTS', ['Construct', 'Forge', 'Garden']))}"
        v_trig = _cfg_val(config_ref, "COUNCIL", "MANIC_VOLTAGE_TRIGGER", 18.0)
        d_halt = _cfg_val(config_ref, "PHYSICS", "DRAG_HALT", 10.0)
        state_key = (
            "flux"
            if packet.voltage > v_trig
            else "deep"
            if packet.narrative_drag > d_halt
            else "prime"
        )
        name_suffix = ux("village_strings", f"loci_{state_key}_suffix") or ""
        atmos = (
            ux("village_strings", f"loci_{state_key}_atmos") or "Unsettlingly quiet."
        )
        smell = ux("village_strings", f"loci_{state_key}_smell") or "Dust and ozone."
        return GeniusLoci(
            id=node_id,
            name=f"{name} {name_suffix}".strip().upper(),
            atmosphere=atmos,
            smell=smell,
            state_key=state_key,
        )

    def _prune_graph(self):
        candidates = [
            k
            for k in self.world_graph
            if k not in ("GENESIS_POINT", self.current_node_id)
        ]
        if candidates:
            victim = min(candidates, key=lambda k: self.world_graph[k].visited_count)
            del self.world_graph[victim]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {k: v.to_dict() for k, v in self.world_graph.items()},
            "current_id": self.current_node_id,
        }

    def export_atlas(self) -> Dict[str, Any]:
        return self.to_dict()

    def load_state(self, data: Dict[str, Any]):
        if not data:
            return
        self.world_graph.clear()
        for nid, n_data in data.get("nodes", {}).items():
            try:
                self.world_graph[nid] = GeniusLoci.from_dict(n_data)
            except Exception:
                pass
        self.current_node_id = data.get("current_id", "GENESIS_POINT")
        if "GENESIS_POINT" not in self.world_graph:
            self._init_genesis()


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
        seed_data = almanac.get("SEEDS", [])
        for s in seed_data:
            if "question" in s and "triggers" in s:
                self.sow_seed(s["question"], set(s["triggers"]))

    def sow_seed(self, question: str, triggers: Set[str]):
        self.seeds.append(ParadoxSeed(question, triggers))

    @staticmethod
    def consult_almanac(physics: PhysicsPacket, config_ref=None) -> str:
        almanac = LoreManifest.get_instance().get("ALMANAC") or {}
        forecasts, strategies = (
            almanac.get("FORECASTS", {}),
            almanac.get("STRATEGIES", {}),
        )
        volt, drag, entropy = physics.voltage, physics.narrative_drag, physics.entropy
        if volt > _cfg_val(config_ref, "VILLAGE", "ALMANAC_VOLT_HIGH", 15.0):
            state_key = "HIGH_VOLTAGE"
        elif drag > _cfg_val(config_ref, "VILLAGE", "ALMANAC_DRAG_HIGH", 4.0):
            state_key = "HIGH_DRAG"
        elif entropy > _cfg_val(config_ref, "VILLAGE", "ALMANAC_ENTROPY_HIGH", 0.8):
            state_key = "HIGH_ENTROPY"
        else:
            state_key = "BALANCED"
        return f"☁️ FORECAST [{state_key}]: {random.choice(forecasts.get(state_key) or ['Weather unclear.'])} (Strategy: {strategies.get(state_key) or 'Keep breathing.'})"

    def tend_garden(self, clean_words: List[str]) -> List[str]:
        blooms = []
        if not self.seeds or not clean_words:
            return blooms
        word_counts = Counter(w.lower() for w in clean_words)
        prefix = ux("village_strings", "town_bloom") or "A paradox blooms:"
        for seed in self.seeds:
            if not seed.bloomed and seed.water(word_counts, self.cfg):
                formatted_msg = f"{Prisma.MAG}{prefix}{Prisma.RST} {seed.bloom()}"
                self.events.log(formatted_msg, "VILLAGE_EVENT")
                blooms.append(formatted_msg)
        self.seeds = [s for s in self.seeds if not s.bloomed]
        return blooms

    def conduct_census(self, packet: PhysicsPacket, host_stats: Any) -> str:
        latency = getattr(host_stats, "latency", 0.0) if host_stats else 0.0
        forecasts = (LoreManifest.get_instance().get("ALMANAC") or {}).get(
            "FORECASTS", {}
        )
        loc_name = "UNKNOWN"
        if self.navigator and (
            node := self.navigator.world_graph.get(self.navigator.current_node_id)
        ):
            loc_name = node.name
        if latency > _cfg_val(self.cfg, "VILLAGE", "TOWN_LATENCY_WARN", 3.0):
            status, advice = (
                "HIGH_LATENCY",
                ux("village_strings", "town_lag") or "Catch your breath.",
            )
        elif packet.voltage > _cfg_val(self.cfg, "PHYSICS", "VOLTAGE_HIGH", 60.0):
            status, advice = (
                "HIGH_VOLTAGE",
                random.choice(forecasts.get("HIGH_VOLTAGE", ["Manic energy."])),
            )
        elif packet.narrative_drag > _cfg_val(self.cfg, "PHYSICS", "DRAG_HEAVY", 5.0):
            status, advice = (
                "HIGH_DRAG",
                random.choice(forecasts.get("HIGH_DRAG", ["Narrative stuck."])),
            )
        else:
            status, advice = (
                "BALANCED",
                random.choice(forecasts.get("BALANCED", ["Nominal."])),
            )
        report_template = (
            ux("village_strings", "town_census")
            or "Location: {loc} | Status: {status} | {advice}"
        )
        report = [report_template.format(loc=loc_name, status=status, advice=advice)]
        if news := self._get_town_news(latency, packet.voltage, config_ref=self.cfg):
            report.append(news)
        if packet.voltage > _cfg_val(self.cfg, "VILLAGE", "TOWN_VOLT_CRIT", 20.0):
            if msg := ux("village_strings", "town_restrain"):
                report.append(f"{Prisma.RED}{msg}{Prisma.RST}")
        elif packet.voltage < _cfg_val(
            self.cfg, "VILLAGE", "TOWN_VOLT_LOW", 2.0
        ) and packet.narrative_drag > _cfg_val(
            self.cfg, "VILLAGE", "TOWN_DRAG_HIGH", 5.0
        ):
            if msg := ux("village_strings", "town_loops"):
                report.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
        elif status == "BALANCED" and random.random() < _cfg_val(
            self.cfg, "VILLAGE", "TOWN_RUMOR_CHANCE", 0.3
        ):
            almanac = LoreManifest.get_instance().get("ALMANAC") or {}
            if rumors := almanac.get("RUMORS", []):
                if msg := ux("village_strings", "town_rumor"):
                    report.append(
                        f"{Prisma.GRY}{msg.format(rumor=random.choice(rumors))}{Prisma.RST}"
                    )
        return "\n".join(report).strip()

    @staticmethod
    def _get_town_news(latency: float, volt: float, config_ref=None) -> Optional[str]:
        alerts = []
        if latency > _cfg_val(config_ref, "VILLAGE", "TOWN_NEWS_LATENCY", 4.0):
            if msg := ux("village_strings", "town_crier_slow"):
                alerts.append(f"{Prisma.OCHRE}{msg}{Prisma.RST}")
        if volt > _cfg_val(config_ref, "PHYSICS", "VOLTAGE_CRITICAL", 100.0):
            if msg := ux("village_strings", "town_crier_volt"):
                alerts.append(f"{Prisma.YEL}{msg}{Prisma.RST}")
        return "\n".join(alerts) if alerts else None

    def on_item_drop(self, payload):
        item = payload.get("item")
        if item and (msg := ux("village_strings", "town_item_drop")):
            self.events.log(msg.format(item=item), "VILLAGE")

    @staticmethod
    def diagnose_condition(
        session_data: dict, _host_health: Any = None, soul: Any = None, config_ref=None
    ) -> Tuple[str, str]:
        from struts import ux_format

        trauma = session_data.get("trauma_vector") or {}
        if soul and float(safe_get(soul, "obsession_neglect", 0.0)) > _cfg_val(
            config_ref, "VILLAGE", "TOWN_NEGLECT_CRIT", 8.0
        ):
            return "HIGH_DRAG", ux_format(
                "village_strings",
                "town_guilt",
                obsession=safe_get(soul, "current_obsession", "work"),
                default="Guilt parameter breached: {obsession}",
            )
        if trauma:
            max_t_key = max(trauma, key=lambda k: float(trauma[k]))
            if float(trauma[max_t_key]) > _cfg_val(
                config_ref, "VILLAGE", "TOWN_TRAUMA_CRIT", 0.6
            ):
                return "HIGH_TRAUMA", ux_format(
                    "village_strings",
                    "town_trauma",
                    trauma=max_t_key,
                    default="Trauma critical: {trauma}",
                )
        meta_data = session_data.get("meta") or {}
        if float(safe_get(meta_data, "final_health", 50.0)) < _cfg_val(
            config_ref, "VILLAGE", "TOWN_HEALTH_CRIT", 30.0
        ):
            return "HIGH_TRAUMA", ux(
                "village_strings", "town_critical"
            ) or "We are holding it together with duct tape and prayers."
        return "BALANCED", ux("village_strings", "town_nominal") or "All is well."


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
        trauma_vector: Optional[Dict] = None,
        config_ref=None,
    ) -> Tuple[str, str]:
        death_data = LoreManifest.get_instance().get("DEATH")
        if not isinstance(death_data, dict):
            death_data = DeathGen._FALLBACK_PROTOCOLS
        cause = DeathGen._determine_cause(packet, mito_state, trauma_vector, config_ref)
        verdict_type = DeathGen._determine_verdict_type(packet, cause, config_ref)
        c_data = death_data.get("CAUSES")
        causes_dict: dict = c_data if isinstance(c_data, dict) else {}
        v_data = death_data.get("VERDICTS")
        verdicts_dict: dict = v_data if isinstance(v_data, dict) else {}
        p_data = death_data.get("PREFIXES")
        prefix = random.choice(
            list(p_data) if isinstance(p_data, (list, tuple)) else ["Alas."]
        )
        causes = causes_dict.get(cause) or causes_dict.get("DEFAULT") or ["Error"]
        verdicts = (
            verdicts_dict.get(verdict_type) or verdicts_dict.get("DEFAULT") or ["Done."]
        )
        return (
            f"{prefix} CAUSE: {random.choice(causes)}. {random.choice(verdicts)}",
            cause,
        )

    @staticmethod
    def _determine_cause(
        p: PhysicsPacket,
        mito_state: Any,
        trauma_vector: Optional[Dict] = None,
        config_ref=None,
    ) -> str:
        if trauma_vector and sum(float(v) for v in trauma_vector.values()) > _cfg_val(
            config_ref, "VILLAGE", "DEATH_TRAUMA_CRIT", 50.0
        ):
            return "TRAUMA"
        if float(
            safe_get(mito_state, "atp_pool", safe_get(mito_state, "atp", 0.0))
        ) <= _cfg_val(config_ref, "BIO", "ATP_STARVATION", 0.0):
            return "STARVATION"
        chi = float(safe_get(p, "chi", 0.0))
        m_a = float(safe_get(p, "m_a", 0.0))
        i_c = float(safe_get(p, "i_c", 1.0))
        voltage = float(safe_get(p, "voltage", 0.0))
        drag = float(safe_get(p, "narrative_drag", 0.0))
        counts = safe_get(p, "counts", {}) or {}
        if (chi * m_a) > i_c:
            return "APOPTOSIS"
        if voltage > _cfg_val(config_ref, "PHYSICS", "VOLTAGE_CRITICAL", 100.0):
            return "GLUTTONY"
        if drag > _cfg_val(config_ref, "PHYSICS", "DRAG_HALT", 10.0):
            return "BOREDOM"
        if float(safe_get(counts, "antigen", 0.0)) > _cfg_val(
            config_ref, "VILLAGE", "DEATH_TOXICITY_CRIT", 5.0
        ):
            return "TOXICITY"
        return "STARVATION"

    @staticmethod
    def _determine_verdict_type(p: PhysicsPacket, cause: str, config_ref=None) -> str:
        if cause == "GLUTTONY":
            return "THERMAL"
        if cause in ("TOXICITY", "APOPTOSIS"):
            return "ENTROPY"
        if float(safe_get(p, "psi", 0.0)) > _cfg_val(
            config_ref, "VILLAGE", "DEATH_ABSTRACT_PSI", 0.8
        ):
            return "ABSTRACT"
        if float(safe_get(p, "valence", 0.0)) > _cfg_val(
            config_ref, "VILLAGE", "DEATH_JOY_VALENCE", 0.6
        ):
            return "JOY_CLADE"
        return "ENTROPY"


class TheTherapist:
    def __init__(self, events_ref, config_ref=None):
        self.events = events_ref
        self.cfg = config_ref or BoneConfig

    def evaluate_catharsis(
        self, trauma_vector: Dict[str, float], health: float
    ) -> Tuple[bool, str]:
        trauma_threshold = _cfg_val(self.cfg, "VILLAGE", "THERAPY_TRAUMA_THRESH", 15.0)
        health_threshold = _cfg_val(self.cfg, "VILLAGE", "THERAPY_HEALTH_THRESH", 50.0)
        if (
            trauma_vector
            and sum(float(v) for v in trauma_vector.values()) > trauma_threshold
            and health < health_threshold
        ):
            max_trauma = str(
                max(trauma_vector, key=lambda k: float(trauma_vector[k]))
            ).lower()
            msg = (
                ux("village_strings", "therapist_intervention")
                or "The Therapist steps in to address the {trauma}."
            ).format(trauma=max_trauma)
            self.events.log(f"{Prisma.VIOLET}{msg}{Prisma.RST}", "THERAPY")
            return True, msg
        return False, ""


class TheGraveDigger:
    def __init__(self, inventory_ref, events_ref, config_ref=None):
        self.inventory = inventory_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig

    def bury_memory(self, node_id: str, mass: float) -> Optional[str]:
        msg = (
            ux("village_strings", "gravedigger_bury")
            or "The Grave Digger turns the soil over '{node_id}'."
        ).format(node_id=node_id)
        self.events.log(f"{Prisma.GRY}{msg}{Prisma.RST}", "VILLAGE")
        if self.inventory and random.random() < (
            mass * _cfg_val(self.cfg, "VILLAGE", "GRAVEDIGGER_RELIC_CHANCE", 0.1)
        ):
            clean_id = str(node_id).replace("-", "").upper()
            relic_name = f"BONE RELIC [{clean_id[-6:]}]"
            self.inventory.acquire(relic_name)
            unearth_msg = (
                ux("village_strings", "gravedigger_unearth")
                or "The Grave Digger struck something. {relic} added."
            ).format(relic=relic_name)
            return f"{Prisma.OCHRE}{unearth_msg}{Prisma.RST}"
        return None
