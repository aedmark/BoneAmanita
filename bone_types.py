import time, copy, uuid, json, re
from dataclasses import dataclass, field, fields, asdict
from enum import Enum
from typing import List, Dict, Any, Optional

class Prisma:
    RST = "\033[0m"
    RED, GRN, YEL, BLU, MAG, CYN, WHT, GRY = (
        "\033[31m",
        "\033[32m",
        "\033[33m",
        "\033[34m",
        "\033[35m",
        "\033[36m",
        "\033[97m",
        "\033[90m",
    )
    INDIGO, OCHRE, VIOLET, SLATE = (
        "\033[34;1m",
        "\033[33;2m",
        "\033[35;2m",
        "\033[30;1m",
    )
    _STRIP_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    _COLOR_MAP = {
        "R": RED,
        "G": GRN,
        "Y": YEL,
        "B": BLU,
        "M": MAG,
        "C": CYN,
        "W": WHT,
        "0": GRY,
        "I": INDIGO,
        "O": OCHRE,
        "V": VIOLET,
        "S": SLATE,
    }

    @classmethod
    def paint(cls, text: str, color_key: str = "0") -> str:
        if len(color_key) == 1:
            code = cls._COLOR_MAP.get(color_key, cls.WHT)
        else:
            code = cls._COLOR_MAP.get(str(color_key)[0].upper(), cls.WHT)
        txt = str(text)
        return f"{code}{txt}" if txt.endswith(cls.RST) else f"{code}{txt}{cls.RST}"

    @classmethod
    def strip(cls, text: str) -> str:
        return cls._STRIP_PATTERN.sub("", str(text))


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
    # --- VSL Somatic ---
    voltage: float = 30.0  # (V) Creative intensity
    health: float = 100.0  # (H) Structural integrity
    stamina: float = 100.0  # (P) ATP pool
    trauma: float = 0.0  # (T) Unresolved rupture

    # --- VSL Cognitive ---
    exhaustion: float = 0.2  # (E) Lexical fatigue
    contradiction: float = 0.4  # (β) Capacity to hold opposing truths
    scope: float = 0.3  # (S) Retrieval breadth
    depth: float = 0.3  # (D) Hierarchical traversal
    connectivity: float = 0.2  # (C) Logical bridging

    # --- VSL Semantic ---
    psi: float = 0.2  # (Ψ) Void / Abstraction
    chi: float = 0.2  # (Χ) Entropy / Chaos
    valence: float = 0.0  # (♥) Emotional polarity

    # --- Extended/Legacy Substrate ---
    entropy: float = 0.2  # Legacy map to chi
    mass: float = 0.0
    velocity: float = 0.0
    beta_index: float = 0.4  # Legacy map to contradiction
    turbulence: float = 0.0
    kappa: float = 0.0  # (κ) Drag corollary
    epsilon: float = 0.0  # (ε) Entropy corollary
    xi: float = 0.0  # (Ξ) Substrate depth
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
    narrative_drag: float = 0.6  # (F) Friction - High=stuck, Low=flow. Default 0.6
    friction: float = 0.6        # (F) VSL alias for narrative drag
    atmosphere: str = "NEUTRAL"
    flow_state: str = "LAMINAR"


@dataclass
class PhysicsPacket:
    energy: EnergyState = field(default_factory=EnergyState)
    matter: MaterialState = field(default_factory=MaterialState)
    space: SpatialState = field(default_factory=SpatialState)

    @property
    def E(self):
        return self.energy.exhaustion

    @E.setter
    def E(self, v):
        self.energy.exhaustion = v

    @property
    def beta(self):
        return self.energy.contradiction

    @beta.setter
    def beta(self, v):
        self.energy.contradiction = v
        self.energy.beta_index = v

    @property
    def S(self):
        return self.energy.scope

    @S.setter
    def S(self, v):
        self.energy.scope = v

    @property
    def D(self):
        return self.energy.depth

    @D.setter
    def D(self, v):
        self.energy.depth = v

    @property
    def C(self):
        return self.energy.connectivity

    @C.setter
    def C(self, v):
        self.energy.connectivity = v

    @property
    def V(self):
        return self.energy.voltage

    @V.setter
    def V(self, v):
        self.energy.voltage = v

    @property
    def voltage(self):
        return self.energy.voltage

    @voltage.setter
    def voltage(self, v):
        self.energy.voltage = v

    @property
    def F(self):
        return self.space.friction

    @F.setter
    def F(self, v):
        self.space.friction = v
        self.space.narrative_drag = v

    @property
    def narrative_drag(self):
        return self.space.narrative_drag

    @narrative_drag.setter
    def narrative_drag(self, v):
        self.space.narrative_drag = v
        self.space.friction = v

    @property
    def H(self):
        return self.energy.health

    @H.setter
    def H(self, v):
        self.energy.health = v

    @property
    def P(self):
        return self.energy.stamina

    @P.setter
    def P(self, v):
        self.energy.stamina = v

    @property
    def T(self):
        return self.energy.trauma

    @T.setter
    def T(self, v):
        self.energy.trauma = v

    @property
    def psi(self):
        return self.energy.psi

    @psi.setter
    def psi(self, v):
        self.energy.psi = v

    @property
    def chi(self):
        return self.energy.chi

    @chi.setter
    def chi(self, v):
        self.energy.chi = v
        self.energy.entropy = v

    @property
    def entropy(self):
        return self.energy.entropy

    @entropy.setter
    def entropy(self, v):
        self.energy.entropy = v
        self.energy.chi = v

    @property
    def valence(self):
        return self.energy.valence

    @valence.setter
    def valence(self, v):
        self.energy.valence = v

    # -- LEGACY SHORTCUTS --
    @property
    def clean_words(self):
        return self.matter.clean_words

    @clean_words.setter
    def clean_words(self, v):
        self.matter.clean_words = v

    @property
    def vector(self):
        return self.matter.vector

    @vector.setter
    def vector(self, v):
        self.matter.vector = v

    @property
    def counts(self):
        return self.matter.counts

    @counts.setter
    def counts(self, v):
        self.matter.counts = v

    @property
    def zone(self):
        return self.space.zone

    @zone.setter
    def zone(self, v):
        self.space.zone = v

    def __init__(
        self,
        energy: Optional[EnergyState] = None,
        matter: Optional[MaterialState] = None,
        space: Optional[SpatialState] = None,
        **kwargs,
    ):
        self.energy = energy or EnergyState()
        self.matter = matter or MaterialState()
        self.space = space or SpatialState()
        for k, v in kwargs.items():
            setattr(self, k, v)


    @classmethod
    def void_state(cls):
        p = cls()
        p.space.atmosphere = "VOID"
        p.space.zone = "VOID"
        p.space.flow_state = "LAMINAR"
        return p

    def snapshot(self) -> "PhysicsPacket":
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
    user_profile: Dict = field(
        default_factory=lambda: {"name": "TRAVELER", "confidence": 0}
    )
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

    def record_flux(
        self, phase: str, metric: str, initial: float, final: float, reason: str = ""
    ):
        delta = final - initial
        if abs(delta) > 0.001:
            self.flux_log.append(
                {
                    "phase": phase,
                    "metric": metric,
                    "initial": initial,
                    "final": final,
                    "delta": delta,
                    "reason": reason,
                    "timestamp": time.time(),
                }
            )

    def snapshot(self) -> "CycleContext":
        new_ctx = copy.copy(self)
        for f in fields(self):
            name = f.name
            val = getattr(self, name)
            if name == "physics" and hasattr(val, "snapshot"):
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
        e_val = self.leverage_metrics.get("E", 0.0)
        return (
            f"💎 CRYSTAL [{self.decision_id}] {self.system_state} | "
            f"Arch: {self.active_archetype} | E: {e_val:.2f}"
        )

    def crystallize(self) -> str:
        data = asdict(self)
        data["_summary"] = f"{self.system_state}::{self.active_archetype}"
        data["_type"] = "CRYSTAL"
        return json.dumps(data)
