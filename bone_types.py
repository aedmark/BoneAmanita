""" bone_types.py - The Data Structures """
import time, copy, uuid, json, re, random
from dataclasses import dataclass, field, fields, asdict
from enum import Enum
from typing import List, Dict, Any, Optional, Deque


class Prisma:
    RST = "\033[0m"
    RED = "\033[31m"
    GRN = "\033[32m"
    YEL = "\033[33m"
    BLU = "\033[34m"
    MAG = "\033[35m"
    CYN = "\033[36m"
    WHT = "\033[97m"
    GRY = "\033[90m"
    INDIGO = "\033[34;1m"
    OCHRE = "\033[33;2m"
    VIOLET = "\033[35;2m"
    SLATE = "\033[30;1m"
    _COLOR_MAP = {
        "R": RED, "G": GRN, "Y": YEL, "B": BLU,
        "M": MAG, "C": CYN, "W": WHT, "0": GRY,
        "I": INDIGO, "O": OCHRE, "V": VIOLET,
        "S": SLATE}
    _TIE_DYE_COLORS = [RED, GRN, YEL, CYN, MAG, VIOLET, OCHRE]
    _STRIP_REGEX = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    @classmethod
    def paint(cls, text: str, color_key: str = "0") -> str:
        code = cls._COLOR_MAP.get(str(color_key).upper(), cls.WHT)
        if str(text).endswith(cls.RST):
            return f"{code}{text}"
        return f"{code}{text}{cls.RST}"

    @classmethod
    def strip(cls, text: str) -> str:
        return cls._STRIP_REGEX.sub('', str(text))

    @classmethod
    def tie_dye(cls, text: str) -> str:
        return "".join(
            f"{random.choice(cls._TIE_DYE_COLORS)}{char}{cls.RST}" if char.strip() else char
            for char in str(text))

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
class PhysicsPacket:
    voltage: float = 0.0
    narrative_drag: float = 0.0
    valence: float = 0.0
    repetition: float = 0.0
    atmosphere: str = "NEUTRAL"
    clean_words: List[str] = field(default_factory=list)
    counts: Dict[str, int] = field(default_factory=dict)
    vector: Dict[str, float] = field(default_factory=dict)
    flow_state: str = "LAMINAR"
    zone: str = "COURTYARD"
    truth_ratio: float = 0.0
    raw_text: str = ""
    antigens: int = 0
    perfection_streak: int = 0
    turbulence: float = 0.0
    entropy: float = 0.0
    mass: float = 0.0
    velocity: float = 0.0
    psi: float = 0.0
    kappa: float = 0.0
    manifold: str = "DEFAULT"
    beta_index: float = 0.0

    @classmethod
    def void_state(cls):
        return cls(atmosphere="VOID", flow_state="LAMINAR", zone="VOID")

    def snapshot(self) -> 'PhysicsPacket':
        new_packet = copy.copy(self)
        new_packet.clean_words = list(self.clean_words)
        new_packet.counts = self.counts.copy()
        new_packet.vector = self.vector.copy()
        return new_packet

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    def get(self, key, default=None):
        return getattr(self, key, default)

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
        return cls(packet=packet, original_snapshot=None)

    def _ensure_snapshot(self):
        if self.original_snapshot is None:
            self.original_snapshot = self.packet.snapshot()

    def apply_delta(self, key: str, value: Any, reason: str = ""):
        self._ensure_snapshot()
        old = getattr(self.packet, key, None)
        setattr(self.packet, key, value)
        self.modifications.append({
            "key": key,
            "old": old,
            "new": value,
            "reason": reason})

    def get_modification_log(self) -> List[Dict]:
        return self.modifications

    def rollback(self):
        if self.original_snapshot:
            for f in fields(self.original_snapshot):
                setattr(self.packet, f.name, getattr(self.original_snapshot, f.name))

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
        stack_copy = copy.copy(self.reality_stack) if self.reality_stack else None
        new_ctx = CycleContext(
            input_text=self.input_text,
            physics=self.physics.snapshot() if hasattr(self.physics, 'snapshot') else copy.deepcopy(self.physics),
            bio_result=copy.deepcopy(self.bio_result),
            mind_state=copy.deepcopy(self.mind_state),
            world_state=copy.deepcopy(self.world_state),
            user_profile=copy.deepcopy(self.user_profile),
            clean_words=list(self.clean_words),
            logs=list(self.logs),
            flux_log=list(self.flux_log),
            is_alive=self.is_alive,
            refusal_triggered=self.refusal_triggered,
            refusal_packet=copy.deepcopy(self.refusal_packet),
            is_bureaucratic=self.is_bureaucratic,
            bureau_ui=self.bureau_ui,
            timestamp=self.timestamp,
            last_impulse=self.last_impulse,
            reality_stack=stack_copy,
            active_lens=self.active_lens)
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
class StateSandbox:
    phase_name: str
    physics_copy: Dict[str, Any]
    bio_copy: Dict[str, Any]
    logs: List[str] = field(default_factory=list)
    changes_committed: bool = False

    def commit(self, target_context: 'CycleContext'):
        if self.changes_committed: return
        target_context.logs.extend(self.logs)
        for k, v in self.physics_copy.items():
            if hasattr(target_context.physics, k):
                setattr(target_context.physics, k, v)
        self.changes_committed = True

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