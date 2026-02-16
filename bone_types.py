""" bone_types.py - The Data Structures (Refactored) """
import time, copy, uuid, json, re
from dataclasses import dataclass, field, fields, asdict
from enum import Enum
from typing import List, Dict, Any, Optional


class Prisma:
    RST = "\033[0m"
    RED, GRN, YEL, BLU, MAG, CYN, WHT, GRY = (
        "\033[31m", "\033[32m", "\033[33m", "\033[34m",
        "\033[35m", "\033[36m", "\033[97m", "\033[90m")
    INDIGO, OCHRE, VIOLET, SLATE = (
        "\033[34;1m", "\033[33;2m", "\033[35;2m", "\033[30;1m")
    _COLOR_MAP = {
        "R": RED, "G": GRN, "Y": YEL, "B": BLU, "M": MAG, "C": CYN,
        "W": WHT, "0": GRY, "I": INDIGO, "O": OCHRE, "V": VIOLET, "S": SLATE}

    @classmethod
    def paint(cls, text: str, color_key: str = "0") -> str:
        code = cls._COLOR_MAP.get(str(color_key).upper(), cls.WHT)
        txt = str(text)
        return f"{code}{txt}" if txt.endswith(cls.RST) else f"{code}{txt}{cls.RST}"

    @classmethod
    def strip(cls, text: str) -> str:
        pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return pattern.sub('', str(text))


class LoreCategory(Enum):
    LEXICON = "LEXICON"
    SCENARIOS = "scenarios"
    GORDON = "gordon"
    GORDON_LOGS = "gordon_logs"
    GENETICS = "genetics"
    DEATH = "death"
    ALMANAC = "almanac"
    DREAMS = "dreams"

class RealityLayer:
    TERMINAL = 0
    SIMULATION = 1
    VILLAGE = 2
    DEBUG = 3
    DEEP_CX = 4

@dataclass
class ErrorLog:
    component: str
    error_msg: str
    timestamp: float = field(default_factory=time.time)
    severity: str = "WARNING"

@dataclass
class EnergyState:
    voltage: float = 0.0
    entropy: float = 0.0
    mass: float = 0.0
    velocity: float = 0.0
    psi: float = 0.0
    beta_index: float = 0.0
    turbulence: float = 0.0
    kappa: float = 0.0
    valence: float = 0.0
    perfection_streak: int = 0

@dataclass
class MaterialState:
    clean_words: List[str] = field(default_factory=list)
    raw_text: str = ""
    counts: Dict[str, int] = field(default_factory=dict)
    antigens: int = 0
    vector: Dict[str, float] = field(default_factory=dict)
    truth_ratio: float = 0.0
    repetition: float = 0.0

@dataclass
class SpatialState:
    zone: str = "COURTYARD"
    manifold: str = "DEFAULT"
    narrative_drag: float = 0.0
    atmosphere: str = "NEUTRAL"
    flow_state: str = "LAMINAR"

@dataclass
class PhysicsPacket:
    energy: EnergyState = field(default_factory=EnergyState)
    matter: MaterialState = field(default_factory=MaterialState)
    space: SpatialState = field(default_factory=SpatialState)

    @property
    def voltage(self): return self.energy.voltage
    @voltage.setter
    def voltage(self, v): self.energy.voltage = v

    @property
    def entropy(self): return self.energy.entropy
    @entropy.setter
    def entropy(self, v): self.energy.entropy = v

    @property
    def mass(self): return self.energy.mass
    @mass.setter
    def mass(self, v): self.energy.mass = v

    @property
    def velocity(self): return self.energy.velocity
    @velocity.setter
    def velocity(self, v): self.energy.velocity = v

    @property
    def psi(self): return self.energy.psi
    @psi.setter
    def psi(self, v): self.energy.psi = v

    @property
    def beta_index(self): return self.energy.beta_index
    @beta_index.setter
    def beta_index(self, v): self.energy.beta_index = v

    @property
    def turbulence(self): return self.energy.turbulence
    @turbulence.setter
    def turbulence(self, v): self.energy.turbulence = v

    @property
    def kappa(self): return self.energy.kappa
    @kappa.setter
    def kappa(self, v): self.energy.kappa = v

    @property
    def valence(self): return self.energy.valence
    @valence.setter
    def valence(self, v): self.energy.valence = v

    @property
    def perfection_streak(self): return self.energy.perfection_streak
    @perfection_streak.setter
    def perfection_streak(self, v): self.energy.perfection_streak = v

    @property
    def clean_words(self): return self.matter.clean_words
    @clean_words.setter
    def clean_words(self, v): self.matter.clean_words = v

    @property
    def raw_text(self): return self.matter.raw_text
    @raw_text.setter
    def raw_text(self, v): self.matter.raw_text = v

    @property
    def counts(self): return self.matter.counts
    @counts.setter
    def counts(self, v): self.matter.counts = v

    @property
    def antigens(self): return self.matter.antigens
    @antigens.setter
    def antigens(self, v): self.matter.antigens = v

    @property
    def vector(self): return self.matter.vector
    @vector.setter
    def vector(self, v): self.matter.vector = v

    @property
    def truth_ratio(self): return self.matter.truth_ratio
    @truth_ratio.setter
    def truth_ratio(self, v): self.matter.truth_ratio = v

    @property
    def repetition(self): return self.matter.repetition
    @repetition.setter
    def repetition(self, v): self.matter.repetition = v

    @property
    def zone(self): return self.space.zone
    @zone.setter
    def zone(self, v): self.space.zone = v

    @property
    def manifold(self): return self.space.manifold
    @manifold.setter
    def manifold(self, v): self.space.manifold = v

    @property
    def narrative_drag(self): return self.space.narrative_drag
    @narrative_drag.setter
    def narrative_drag(self, v): self.space.narrative_drag = v

    @property
    def atmosphere(self): return self.space.atmosphere
    @atmosphere.setter
    def atmosphere(self, v): self.space.atmosphere = v

    @property
    def flow_state(self): return self.space.flow_state
    @flow_state.setter
    def flow_state(self, v): self.space.flow_state = v

    @classmethod
    def void_state(cls):
        p = cls()
        p.space.atmosphere = "VOID"
        p.space.zone = "VOID"
        p.space.flow_state = "LAMINAR"
        return p

    def snapshot(self) -> 'PhysicsPacket':
        return copy.deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def get(self, key, default=None):
        if hasattr(self, key):
            return getattr(self, key)
        return default

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return hasattr(self, key)

@dataclass
class PhysicsSandbox:
    packet: PhysicsPacket
    original_snapshot: Optional[PhysicsPacket] = None
    modifications: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def create(cls, packet: PhysicsPacket) -> 'PhysicsSandbox':
        return cls(packet=packet)

    def _ensure_snapshot(self):
        if self.original_snapshot is None:
            self.original_snapshot = self.packet.snapshot()

    def apply_delta(self, key: str, value: Any, reason: str = ""):
        self._ensure_snapshot()
        setattr(self.packet, key, value)
        self.modifications.append({
            "key": key,
            "new": value,
            "reason": reason})

    def get_modification_log(self) -> List[Dict]:
        return self.modifications

    def rollback(self):
        if self.original_snapshot:
            self.packet.energy = copy.deepcopy(self.original_snapshot.energy)
            self.packet.matter = copy.deepcopy(self.original_snapshot.matter)
            self.packet.space = copy.deepcopy(self.original_snapshot.space)

    def __getattr__(self, name):
        return getattr(self.packet, name)

    def __setattr__(self, name, value):
        if name in ['packet', 'original_snapshot', 'modifications']:
            object.__setattr__(self, name, value)
        else:
            self.apply_delta(name, value, reason="AUTO_TRACE")

@dataclass
class CycleContext:
    input_text: str
    is_system_event: bool = False
    clean_words: List[str] = field(default_factory=list)
    physics: PhysicsPacket = field(default_factory=PhysicsPacket.void_state)
    logs: List[str] = field(default_factory=list)
    flux_log: List[Dict[str, Any]] = field(default_factory=list)
    is_alive: bool = True
    refusal_triggered: bool = False
    refusal_packet: Optional[Dict] = None
    is_bureaucratic: bool = False
    bio_result: Dict = field(default_factory=dict)
    bio_snapshot: Optional[Dict] = None
    world_state: Dict = field(default_factory=dict)
    mind_state: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    bureau_ui: str = ""
    user_profile: Dict = field(default_factory=lambda: {"name": "TRAVELER", "confidence": 0})
    last_impulse: Any = None
    reality_stack: Any = None
    active_lens: str = "NARRATOR"
    validator: Any = None

    @property
    def user_name(self):
        return self.user_profile.get("name", "TRAVELER")

    @user_name.setter
    def user_name(self, value):
        self.user_profile["name"] = value

    def log(self, message: str):
        self.logs.append(message)

    def record_flux(self, phase: str, metric: str, initial: float, final: float, reason: str = ""):
        delta = final - initial
        if abs(delta) > 0.001:
            self.flux_log.append({
                "phase": phase,
                "metric": metric,
                "initial": initial,
                "final": final,
                "delta": delta,
                "reason": reason,
                "timestamp": time.time()})

    def snapshot(self) -> 'CycleContext':
        new_ctx = copy.copy(self)
        for f in fields(self):
            name = f.name
            val = getattr(self, name)
            if name == 'physics' and hasattr(val, 'snapshot'):
                setattr(new_ctx, name, val.snapshot())
            elif isinstance(val, (list, dict, set)):
                setattr(new_ctx, name, copy.deepcopy(val))
        return new_ctx

@dataclass
class MindSystem:
    mem: Any
    lex: Any
    dreamer: Any
    mirror: Any
    tracer: Any

@dataclass
class PhysSystem:
    observer: Any
    forge: Any
    crucible: Any
    theremin: Any
    pulse: Any
    nav: Any
    gate: Optional[Any] = None
    tension: Optional[Any] = None
    dynamics: Any = None

@dataclass
class DecisionTrace:
    trace_id: str
    timestamp: float
    component: str
    decision_type: str
    inputs: Dict[str, Any]
    reasoning: str
    outcome: str

    def to_json(self):
        return json.dumps(asdict(self))

@dataclass
class DecisionCrystal:
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    leverage_metrics: Dict[str, float] = field(default_factory=dict)
    prompt_snapshot: str = ""
    physics_state: Dict[str, Any] = field(default_factory=dict)
    chorus_weights: Dict[str, float] = field(default_factory=dict)
    system_state: str = "STABLE"
    active_archetype: str = "OBSERVER"
    council_mandates: List[str] = field(default_factory=list)
    final_response: str = ""

    def __str__(self):
        e_val = self.leverage_metrics.get('E', 0.0)
        return (
            f"💎 CRYSTAL [{self.decision_id}] {self.system_state} | "
            f"Arch: {self.active_archetype} | E: {e_val:.2f}")

    def crystallize(self) -> str:
        data = asdict(self)
        data["_summary"] = f"{self.system_state}::{self.active_archetype}"
        data["_type"] = "CRYSTAL"
        return json.dumps(data)