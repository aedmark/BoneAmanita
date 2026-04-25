"""bone_types.py"""

import copy
import json
import re
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional

class Prisma:
    RST = "\033[0m"
    RED, GRN, YEL, BLU = "\033[31m", "\033[32m", "\033[33m", "\033[34m"
    MAG, CYN, WHT, GRY = "\033[35m", "\033[36m", "\033[97m", "\033[90m"
    INDIGO = "\033[34;1m"
    OCHRE = "\033[33;2m"
    VIOLET = "\033[35;2m"
    SLATE = "\033[30;1m"
    _STRIP_PATTERN = re.compile(r"<span class='[^']+'>|</span>|\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    _COLOR_MAP = {"R": RED, "G": GRN, "Y": YEL, "B": BLU, "M": MAG, "C": CYN, "W": WHT, "0": GRY, "I": INDIGO,
                  "O": OCHRE, "V": VIOLET, "S": SLATE, }

    @classmethod
    def enable_web_mode(cls):
        cls.RST = "</span>"
        cls.RED = "<span class='prisma-red'>"
        cls.GRN = "<span class='prisma-grn'>"
        cls.YEL = "<span class='prisma-yel'>"
        cls.BLU = "<span class='prisma-blu'>"
        cls.MAG = "<span class='prisma-mag'>"
        cls.CYN = "<span class='prisma-cyn'>"
        cls.WHT = "<span class='prisma-wht'>"
        cls.GRY = "<span class='prisma-gry'>"
        cls.INDIGO = "<span class='prisma-indigo'>"
        cls.OCHRE = "<span class='prisma-ochre'>"
        cls.VIOLET = "<span class='prisma-violet'>"
        cls.SLATE = "<span class='prisma-slate'>"
        cls._COLOR_MAP = {"R": cls.RED, "G": cls.GRN, "Y": cls.YEL, "B": cls.BLU, "M": cls.MAG, "C": cls.CYN,
                          "W": cls.WHT, "0": cls.GRY, "I": cls.INDIGO, "O": cls.OCHRE, "V": cls.VIOLET,
                          "S": cls.SLATE, }

    @classmethod
    def paint(cls, text: str, color_key: str = "0") -> str:
        code = cls._COLOR_MAP.get(str(color_key)[0].upper(), cls.WHT)
        txt = "" if text is None else str(text)
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

    def __str__(self):
        return f"[{self.severity}] {self.component}: {self.error_msg}"

@dataclass
class DragProfile:
    semantic: float = 0.0
    emotional: float = 0.0
    structural: float = 0.0
    metabolic: float = 0.0
    trauma: float = 0.0

    def total(self) -> float:
        return (self.semantic + self.emotional + self.structural + self.metabolic +
                self.trauma)

@dataclass
class EnergyState:
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
    mu: float = 0.0
    m_a: float = 0.0
    i_c: float = 1.0
    h_s: float = 1.0
    omega_r: float = 1.0
    delta_t: float = 12.0
    s_y: float = 0.5
    r_a: float = 0.0
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
    cf_expect: float = 0.0
    novelty: float = 0.0

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
    narrative_drag: float = 0.6
    friction: float = 0.6
    atmosphere: str = "NEUTRAL"
    flow_state: str = "LAMINAR"
    godel_scar: Optional[tuple] = None

@dataclass
class PhysicsPacket:
    energy: EnergyState = field(default_factory=EnergyState)
    matter: MaterialState = field(default_factory=MaterialState)
    space: SpatialState = field(default_factory=SpatialState)
    _CORE_DOMAINS = ("energy", "space", "matter")
    _BASE_FIELDS = frozenset({"energy", "matter", "space", "drag_profile"})
    _ALIAS_MAP = {"E": [("energy", "exhaustion")], "beta": [("energy", "beta_index"), ("energy", "contradiction")],
                  "S": [("energy", "scope")], "D": [("energy", "depth")], "C": [("energy", "connectivity")],
                  "V": [("energy", "voltage")], "F": [("space", "narrative_drag"), ("space", "friction")],
                  "narrative_drag": [("space", "narrative_drag"), ("space", "friction")], "H": [("energy", "health")],
                  "P": [("energy", "stamina")], "ROS": [("energy", "ros")], "G": [("energy", "glimmers")],
                  "PHI_RES": [("energy", "resonance")], "DELTA": [("energy", "silence")], "LQ": [("energy", "lq")],
                  "chi": [("energy", "entropy"), ("energy", "chi")],
                  "entropy": [("energy", "entropy"), ("energy", "chi")], }

    _DOMAIN_MAP = {
        **{k: "energy" for k in EnergyState.__dataclass_fields__},
        **{k: "matter" for k in MaterialState.__dataclass_fields__},
        **{k: "space" for k in SpatialState.__dataclass_fields__},
    }

    @staticmethod
    def _safe_init(cls, data):
        if isinstance(data, cls):
            return data
        if not data:
            return cls()
        valid_keys = cls.__dataclass_fields__.keys()
        if isinstance(data, dict):
            return cls(**{k: v for k, v in data.items() if k in valid_keys and v is not None})
        return cls(**{k: getattr(data, k) for k in valid_keys if getattr(data, k, None) is not None})

    def __init__(self, energy: Optional[Any] = None, matter: Optional[Any] = None, space: Optional[Any] = None,
                 **kwargs, ):
        self.energy = self._safe_init(EnergyState, energy)
        self.matter = self._safe_init(MaterialState, matter)
        self.space = self._safe_init(SpatialState, space)
        self.drag_profile = self._safe_init(DragProfile, kwargs.pop("drag_profile", None))
        for k, v in kwargs.items():setattr(self, k, v)

    def sync_drag(self):
        if hasattr(self, "drag_profile") and self.drag_profile is not None:
            total = self.drag_profile.total()
            setattr(self, "narrative_drag", max(0.6, total))

    @classmethod
    def void_state(cls):
        p = cls()
        p.space.atmosphere = "VOID"
        p.space.zone = "VOID"
        p.space.flow_state = "LAMINAR"
        return p

    def snapshot(self) -> "PhysicsPacket":
        return PhysicsPacket(**self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getattr__(self, key):
        if key.startswith("_"):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")
        if key in self._ALIAS_MAP:
            domain, t_key = self._ALIAS_MAP[key][0]
            return getattr(getattr(self, domain), t_key)
        domain = self._DOMAIN_MAP.get(key)
        if domain:
            return getattr(getattr(self, domain), key)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        if key in self._BASE_FIELDS:
            super().__setattr__(key, value)
            return
        if key in self._ALIAS_MAP:
            for domain, t_key in self._ALIAS_MAP[key]:
                setattr(getattr(self, domain), t_key, value)
            return
        domain = self._DOMAIN_MAP.get(key)
        if domain and hasattr(self, domain):
            setattr(getattr(self, domain), key, value)
            return
        super().__setattr__(key, value)

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(f"'{key}' not found in PhysicsPacket or its sub-states.")

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        if key in self._ALIAS_MAP:
            return True
        try:
            getattr(self, key)
            return True
        except AttributeError:
            return False

@dataclass
class UserInferredState:
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

    def __getattr__(self, key):
        u_key = f"{key}_u"
        if u_key in self.__dataclass_fields__:
            return getattr(self, u_key)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        u_key = f"{key}_u"
        if u_key in self.__dataclass_fields__ and key not in self.__dataclass_fields__:
            super().__setattr__(u_key, value)
        else:
            super().__setattr__(key, value)

    def snapshot(self) -> "UserInferredState":
        return UserInferredState(**asdict(self))

@dataclass
class SharedDynamics:
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

    def snapshot(self) -> "SharedDynamics":
        return SharedDynamics(**asdict(self))

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

    def record_flux(self, phase: str, metric: str, initial: float, final: float, reason: str = ""):
        delta = final - initial
        if abs(delta) > 0.001:
            self.flux_log.append(
                {"phase": phase, "metric": metric, "initial": initial, "final": final, "delta": delta, "reason": reason,
                 "timestamp": time.time(), })

    def snapshot(self) -> "CycleContext":
        new_ctx = copy.copy(self)
        for name in self.__dataclass_fields__:
            val = getattr(self, name)
            if hasattr(val, "snapshot") and callable(val.snapshot):
                setattr(new_ctx, name, val.snapshot())
            elif isinstance(val, list):
                setattr(new_ctx, name, val[:])
            elif isinstance(val, dict):
                setattr(new_ctx, name, val.copy())
            elif isinstance(val, set):
                setattr(new_ctx, name, val.copy())
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
        return (f"♦ CRYSTAL [{self.decision_id}] {self.system_state} | "
                f"ARCHETYPE: {self.active_archetype} | E: {e_val:.2f}")

    def crystallize(self) -> str:
        data = asdict(self)
        data["_summary"] = f"{self.system_state}::{self.active_archetype}"
        data["_type"] = "CRYSTAL"
        return json.dumps(data)
