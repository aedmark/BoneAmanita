"""bone_types.py"""

import copy
import json
import re
import time
import uuid
from dataclasses import dataclass, field, fields, asdict
from enum import Enum
from typing import List, Dict, Any, Optional

class Prisma:
    """The universal color palette. It handles rendering ANSI escape codes for the terminal and safely stripping them for logs."""
    RST = "\033[0m"
    RED, GRN, YEL, BLU, MAG, CYN, WHT, GRY = ("\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m", "\033[36m", "\033[97m", "\033[90m",)
    INDIGO, OCHRE, VIOLET, SLATE = ("\033[34;1m", "\033[33;2m", "\033[35;2m", "\033[30;1m",)
    _STRIP_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    _COLOR_MAP = {"R": RED, "G": GRN, "Y": YEL, "B": BLU, "M": MAG, "C": CYN, "W": WHT, "0": GRY, "I": INDIGO,
                  "O": OCHRE, "V": VIOLET, "S": SLATE, }

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
    """Represents the current structural ruleset of the application."""
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
class DragProfile:
    semantic: float = 0.0   # Words fighting (Contradiction + Entropy)
    emotional: float = 0.0  # Valence conflicts (Heart fighting itself)
    structural: float = 0.0 # Bad architecture (Syntax stress, OAC violations)
    metabolic: float = 0.0  # Low ATP forcing shortcuts
    trauma: float = 0.0     # Reactivating old wounds

    def total(self) -> float:
        return self.semantic + self.emotional + self.structural + self.metabolic + self.trauma

@dataclass
class EnergyState:
    """The quantitative variables that describe the systemic energy, stress, and abstract coordinates of a thought."""
    voltage: float = 30.0
    health: float = 100.0
    stamina: float = 100.0
    trauma: float = 0.0
    ros: float = 0.0
    glimmers: int = 0
    exhaustion: float = 0.2
    contradiction: float = 0.4
    scope: float = 0.3
    depth: float = 0.3
    connectivity: float = 0.2
    psi: float = 0.2
    chi: float = 0.2
    valence: float = 0.0
    gamma: float = 0.0
    sigma: float = 0.0
    eta: float = 0.0
    theta: float = 0.0
    upsilon: float = 0.0
    entropy: float = 0.2
    mass: float = 0.0
    velocity: float = 0.0
    beta_index: float = 0.4
    turbulence: float = 0.0
    kappa: float = 0.0
    epsilon: float = 0.0
    xi: float = 0.0
    lambda_val: float = 0.0
    omega: float = 0.0
    resonance: float = 0.0
    silence: float = 0.0
    lq: float = 0.0
    perfection_streak: int = 0

@dataclass
class MaterialState:
    """The literal syntax and vocabulary of a thought."""
    clean_words: List[str] = field(default_factory=list)
    raw_text: str = ""
    counts: Dict[str, int] = field(default_factory=dict)
    antigens: int = 0
    vector: Dict[str, float] = field(default_factory=dict)
    truth_ratio: float = 0.0
    repetition: float = 0.0

@dataclass
class SpatialState:
    """The context in which the thought exists."""
    zone: str = "COURTYARD"
    manifold: str = "DEFAULT"
    narrative_drag: float = 0.6
    friction: float = 0.6
    atmosphere: str = "NEUTRAL"
    flow_state: str = "LAMINAR"

@dataclass
class PhysicsPacket:
    """
    The master state object. It unifies Energy, Matter, and Space into a single entity.
    Provides single-letter aliases (E, V, F) to keep the math in bone_cycle legible 
    while preserving strict categorization underneath.
    """
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
    def ROS(self):
        return self.energy.ros

    @ROS.setter
    def ROS(self, v):
        self.energy.ros = v

    @property
    def G(self):
        return self.energy.glimmers

    @G.setter
    def G(self, v):
        self.energy.glimmers = v

    @property
    def PHI_RES(self):
        return self.energy.resonance

    @PHI_RES.setter
    def PHI_RES(self, v):
        self.energy.resonance = v

    @property
    def DELTA(self):
        return self.energy.silence

    @DELTA.setter
    def DELTA(self, v):
        self.energy.silence = v

    @property
    def LQ(self):
        return self.energy.lq

    @LQ.setter
    def LQ(self, v):
        self.energy.lq = v

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

    def __init__(self, energy: Optional[EnergyState] = None, matter: Optional[MaterialState] = None,
                 space: Optional[SpatialState] = None, **kwargs, ):
        self.energy = energy or EnergyState()
        self.matter = matter or MaterialState()
        self.space = space or SpatialState()
        self.drag_profile = kwargs.pop("drag_profile", DragProfile())
        for k, v in kwargs.items():
            setattr(self, k, v)

    def sync_drag(self):
        """Safely collapses the profile into the legacy narrative_drag variable."""
        if hasattr(self, "drag_profile") and self.drag_profile is not None:
            total = self.drag_profile.total()
            if total > 0.1:
                self.narrative_drag = max(1.0, total)

    @classmethod
    def void_state(cls):
        """A safe fallback state used during catastrophic failures to prevent NoneType crashes."""
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
class UserInferredState:
    """The probabilistic model of the user's internal somatic and semantic state."""
    E_u: float = 0.5
    beta_u: float = 0.5
    S_u: float = 0.5
    D_u: float = 0.3
    C_u: float = 0.3
    V_u: float = 50.0
    F_u: float = 0.6
    H_u: float = 100.0
    P_u: float = 100.0
    T_u: float = 0.0
    ROS_u: float = 0.0
    G_u: int = 0
    psi_u: float = 0.3
    chi_u: float = 0.2
    valence_u: float = 0.0


@dataclass
class SharedDynamics:
    """The coupled variables describing the relationship and emergent properties of the dyad."""
    phi: float = 0.5
    delta: float = 0.0
    lq: float = 0.0
    null_coord: float = 0.0
    nabla: float = 0.0
    presence: float = 0.0
    g_pool: int = 0
    p_transfer: float = 0.0
    sigma_silence: int = 0
    lambda_silence: float = 0.2


@dataclass
class CycleContext:
    """The master state object that gets passed through the 14 phases of the CycleSimulator."""
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
    time_delta: float = 0.0
    user_state: UserInferredState = field(default_factory=UserInferredState)
    shared_dyn: SharedDynamics = field(default_factory=SharedDynamics)

    @property
    def user_name(self):
        return self.user_profile.get("name", "TRAVELER")

    @user_name.setter
    def user_name(self, value):
        self.user_profile["name"] = value

    def log(self, message: str):
        self.logs.append(message)

    def record_flux(
            self, phase: str, metric: str, initial: float, final: float, reason: str = ""):
        """Explicitly tracks when a variable shifts significantly between phases."""
        delta = final - initial
        if abs(delta) > 0.001:
            self.flux_log.append(
                {"phase": phase, "metric": metric, "initial": initial, "final": final, "delta": delta, "reason": reason,
                 "timestamp": time.time(), })

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
    """A serialized fossil of a single execution cycle, preserving exactly what the system knew when it made a choice."""
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
        from bone_core import ux
        e_val = self.leverage_metrics.get("E", 0.0)
        icon = ux("types_strings", "crystal_icon")
        lbl = ux("types_strings", "crystal_label")
        arch = ux("types_strings", "crystal_arch")
        return (f"{icon} {lbl} [{self.decision_id}] {self.system_state} | "
            f"{arch} {self.active_archetype} | E: {e_val:.2f}").strip()

    def crystallize(self) -> str:
        data = asdict(self)
        data["_summary"] = f"{self.system_state}::{self.active_archetype}"
        data["_type"] = "CRYSTAL"
        return json.dumps(data)