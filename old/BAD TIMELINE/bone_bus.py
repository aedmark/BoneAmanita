""" bone_bus.py - All aboard the Magic Bone Bus! """

import json, os, time, random, copy, re
import math
from collections import deque
from dataclasses import dataclass, field, fields
from typing import List, Dict, Any, Optional, Counter, Tuple

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

    @classmethod
    def paint(cls, text, color_key="0"):
        code = cls._COLOR_MAP.get(str(color_key).upper(), cls.WHT)
        safe_text = str(text).replace(cls.RST, cls.RST + code)
        return f"{code}{safe_text}{cls.RST}"

    @classmethod
    def strip(cls, text):
        clean = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return clean.sub('', str(text))

    @classmethod
    def tie_dye(cls, text):
        colors = [cls.RED, cls.GRN, cls.YEL, cls.CYN, cls.MAG, cls.VIOLET, cls.OCHRE]
        tokens = re.split(r'(\s+)', str(text))
        painted = []
        for token in tokens:
            if not token.strip():
                painted.append(token)
            else:
                c = random.choice(colors)
                painted.append(f"{c}{token}{cls.RST}")
        return "".join(painted)

class EventBus:
    def __init__(self, max_memory=1024, max_gestation=500):
        self.buffer = deque(maxlen=max_memory)
        self.subscribers = {}
        self.dormant = False
        self.gestation_queue = []
        self.max_gestation = max_gestation

    def set_dormancy(self, active: bool):
        self.dormant = active
        if not active and self.gestation_queue:
            print(f"{Prisma.GRY}[BUS]: Waking up. Processing {len(self.gestation_queue)} buffered events...{Prisma.RST}")
            for event_type, data in self.gestation_queue:
                self.publish(event_type, data)
            self.gestation_queue.clear()

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type, data=None):
        if self.dormant:
            if len(self.gestation_queue) >= self.max_gestation:
                self.gestation_queue.pop(0)
                if len(self.gestation_queue) % 50 == 0:
                    print(f"{Prisma.YEL}[BUS WARNING]: Dormancy queue overflowing. Dropping old signals.{Prisma.RST}")
            self.gestation_queue.append((event_type, data))
            return
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"{Prisma.RED}Event Bus Dispatch Error: {e}{Prisma.RST}")

    def log(self, text: str, category: str = "SYSTEM"):
        entry = {
            "text": text,
            "category": category,
            "timestamp": time.time()}
        self.buffer.append(entry)

    def flush(self) -> List[Dict]:
        current_logs = list(self.buffer)
        self.buffer.clear()
        return current_logs

    def get_recent_logs(self, count=10):
        return list(self.buffer)[-count:]

class BonePresets:
    ZEN_GARDEN = {
        "PHYSICS.VOLTAGE_FLOOR": 1.0,
        "PHYSICS.VOLTAGE_MAX": 10.0,
        "PHYSICS.DRAG_FLOOR": 2.0,
        "BIO.DECAY_RATE": 0.001,
        "BIO.STAMINA_EXHAUSTED": 5.0,
        "COUNCIL.MANIC_VOLTAGE_TRIGGER": 99.0}
    THUNDERDOME = {
        "PHYSICS.VOLTAGE_FLOOR": 8.0,
        "PHYSICS.VOLTAGE_MAX": 30.0,
        "PHYSICS.DRAG_FLOOR": 0.5,
        "BIO.ATP_STARVATION": 20.0,
        "COUNCIL.MANIC_VOLTAGE_TRIGGER": 12.0,
        "CHANCE.RARE": 0.20}

class BoneConfig:
    GRAVITY_WELL_THRESHOLD = 15.0
    SHAPLEY_MASS_THRESHOLD = 5.0
    TRAUMA_VECTOR = {"THERMAL": 0.0, "CRYO": 0.0, "SEPTIC": 0.0, "BARIC": 0.0}
    MAX_HEALTH = 100.0
    MAX_STAMINA = 100.0
    MAX_ATP = 200.0
    STAMINA_REGEN = 1.0
    MAX_DRAG_LIMIT = 5.0
    GEODESIC_STRENGTH = 10.0
    BASE_IGNITION_THRESHOLD = 0.5
    MAX_REPETITION_LIMIT = 0.8
    BOREDOM_THRESHOLD = 10.0
    ANVIL_TRIGGER_VOLTAGE = 10.0
    MIN_DENSITY_THRESHOLD = 0.3
    LAGRANGE_TOLERANCE = 2.0
    FLASHPOINT_THRESHOLD = 10.0
    SIGNAL_DRAG_MULTIPLIER = 1.0
    KINETIC_GAIN = 1.0
    CRITICAL_ROS_LIMIT = 100.0
    MAX_MEMORY_CAPACITY = 100
    ZONE_THRESHOLDS = {"LABORATORY": 1.5, "COURTYARD": 0.8}
    TOXIN_WEIGHT = 1.0
    ANTIGENS = ["basically", "actually", "literally", "utilize"]
    MAX_OUTPUT_TOKENS = 4096
    DEFAULT_LLM_ENDPOINTS = {
        "ollama": "http://127.0.0.1:11434/v1/chat/completions",
        "openai": "https://api.openai.com/v1/chat/completions",
        "lm_studio": "http://127.0.0.1:1234/v1/chat/completions",
        "localai": "http://127.0.0.1:8080/v1/chat/completions"}
    VERBOSE_LOGGING = True
    PROVIDER = "openai"
    BASE_URL = None
    API_KEY = None
    MODEL = "gpt-4"
    OLLAMA_MODEL_ID = "llama3"

    class WHIMSY:
        ABSURDITY_CONSTANT = 42
        MAX_SARCASM_LEVEL = 11
        LUDICROUS_SPEED = True
        DEPARTMENT_NAME = "The Ministry of Silly Hats & Semantic Vectors"

    class METABOLISM:
        BASE_RATE = 2.0
        DRAG_TAX_LOW = 0.15
        DRAG_TAX_HIGH = 0.4
        DRAG_GRACE_BUFFER = 1.0
        ROS_GENERATION_FACTOR = 0.08
        PHOTOSYNTHESIS_GAIN = 3.0
        TURBULENCE_TAX = 4.0

    class PHYSICS:
        VOLTAGE_FLOOR = 2.0
        VOLTAGE_LOW = 5.0
        VOLTAGE_MED = 8.0
        VOLTAGE_HIGH = 12.0
        VOLTAGE_CRITICAL = 15.0
        VOLTAGE_MAX = 20.0
        DRAG_FLOOR = 1.0
        DRAG_IDEAL_MAX = 3.0
        DRAG_HEAVY = 5.0
        DRAG_CRITICAL = 8.0
        DRAG_HALT = 10.0
        WEIGHT_HEAVY = 2.0
        WEIGHT_KINETIC = 1.5
        WEIGHT_EXPLOSIVE = 3.0
        WEIGHT_CONSTRUCTIVE = 1.5

    class INVENTORY:
        CONDUCTIVE_THRESHOLD = 12.0
        HEAVY_LOAD_THRESHOLD = 8.0
        TURBULENCE_FUMBLE_CHANCE = 0.15
        TURBULENCE_THRESHOLD = 0.6
        MAX_SLOTS = 8
        RUMMAGE_COST = 15.0

    class COUNCIL:
        STRANGE_LOOP_VOLTAGE = 8.0
        OSCILLATION_DELTA = 5.0
        MANIC_VOLTAGE_TRIGGER = 18.0
        MANIC_DRAG_FLOOR = 1.0
        MANIC_TURN_LIMIT = 2
        FOOTNOTE_CHANCE = 0.15

    class BIO:
        ATP_STARVATION = 10.0
        ROS_CRITICAL = 100.0
        STAMINA_EXHAUSTED = 20.0
        REWARD_SMALL = 0.05
        REWARD_MEDIUM = 0.10
        REWARD_LARGE = 0.15
        DECAY_RATE = 0.01

    class CHANCE:
        RARE = 0.05
        UNCOMMON = 0.10
        COMMON = 0.20
        FREQUENT = 0.30

    @classmethod
    def load_preset(cls, preset_dict: Dict[str, Any]) -> List[str]:
        logs = []
        for key, value in preset_dict.items():
            if "." not in key:
                logs.append(f"⚠️ SKIPPED: Invalid key format '{key}'")
                continue
            sector_name, param_name = key.split(".", 1)
            result = cls.tune(sector_name, param_name, value)
            logs.append(result)
        if cls.VERBOSE_LOGGING:
            print(f"{Prisma.CYN}[CONFIG]: Paradigm Shift Complete. {len(logs)} parameters tuned.{Prisma.RST}")
        return logs

    @staticmethod
    def check_pareidolia(words):
        triggers = {"face", "ghost", "jesus", "cloud", "voice", "eyes"}
        hits = [w for w in words if w in triggers]
        if hits:
            return True, f"{Prisma.VIOLET}PAREIDOLIA: You see a {hits[0].upper()} in the noise. It blinks.{Prisma.RST}"
        return False, None

    @classmethod
    def load_from_file(cls, filepath="bone_config.json"):
        if not os.path.exists(filepath):
            return False, "Config file not found. Using defaults."
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            valid_data, log = cls._validate_ranges(data)
            for key, value in valid_data.items():
                if hasattr(cls, key):
                    setattr(cls, key, value)
            return True, f"Configuration loaded. {log}"
        except Exception as e:
            return False, f"Config load failed: {e}"

    @classmethod
    def _validate_ranges(cls, data: Dict[str, Any], parent_key: str = "") -> Tuple[Dict[str, Any], str]:
        sanitized = {}
        logs = []
        constraints = {
            "MAX_HEALTH": (1.0, 1000.0, float),
            "MAX_STAMINA": (1.0, 1000.0, float),
            "VOLTAGE_MAX": (10.0, 100.0, float),
            "STAMINA_REGEN": (0.1, 10.0, float),
            "MAX_MEMORY_CAPACITY": (10, 1000, int),
            "VERBOSE_LOGGING": (0, 1, bool),}
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                sub_sanitized, sub_log = cls._validate_ranges(value, full_key)
                sanitized[key] = sub_sanitized
                if sub_log: logs.append(sub_log)
                continue
            if key in constraints:
                min_val, max_val, expected_type = constraints[key]
                if expected_type == float and isinstance(value, int):
                    value = float(value)
                if not isinstance(value, expected_type):
                    logs.append(f"Skipped {full_key}: Invalid type {type(value)}.")
                    continue
                if expected_type in [int, float]:
                    if min_val <= value <= max_val:
                        sanitized[key] = value
                    else:
                        clamped = max(min_val, min(max_val, value))
                        sanitized[key] = clamped
                        logs.append(f"Clamped {full_key} ({value} -> {clamped}).")
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = value
        return sanitized, "; ".join(logs) if logs else ""

    @classmethod
    def tune(cls, sector: str, parameter: str, value: Any) -> str:
        if not hasattr(cls, sector):
            return f"❌ SECTOR ERROR: '{sector}' does not exist."
        target_sector = getattr(cls, sector)
        if not hasattr(target_sector, parameter):
            return f"❌ PARAM ERROR: '{parameter}' not found in {sector}."
        current_val = getattr(target_sector, parameter)
        if type(current_val) != type(value) and not (isinstance(current_val, float) and isinstance(value, int)):
            return f"⚠️ TYPE MISMATCH: Cannot replace {type(current_val)} with {type(value)}."
        setattr(target_sector, parameter, value)
        return f"✅ TUNED: {sector}.{parameter} -> {value}"

@dataclass
class ErrorLog:
    component: str
    error_msg: str
    timestamp: float = field(default_factory=time.time)
    severity: str = "WARNING"

class TheObserver:
    def __init__(self):
        self.start_time = time.time()
        self.cycle_times = deque(maxlen=20)
        self.llm_latencies = deque(maxlen=20)
        self.memory_snapshots = deque(maxlen=20)
        self.error_counts = Counter()
        self.user_turns = 0
        self.LATENCY_WARNING = 5.0
        self.CYCLE_WARNING = 8.0

    @staticmethod
    def clock_in():
        return time.time()

    def clock_out(self, start_time, metric_type="cycle"):
        duration = time.time() - start_time
        if metric_type == "cycle":
            self.cycle_times.append(duration)
        elif metric_type == "llm":
            self.llm_latencies.append(duration)
        return duration

    def log_error(self, module_name):
        self.error_counts[module_name] += 1

    def record_memory(self, node_count):
        self.memory_snapshots.append(node_count)

    def pass_judgment(self, avg_cycle, avg_llm):
        if avg_cycle == 0.0 and avg_llm == 0.0:
            return "ASLEEP (WAKE UP)"
        if avg_cycle < 0.1 and avg_llm < 0.5:
            return "SUSPICIOUSLY EFFICIENT (Did we skip the math?)"
        if avg_llm > self.LATENCY_WARNING:
            jokes = [
                "BRAIN FOG (The neural net is buffering)",
                "DEGRADED (Thinking... thinking...)",
                "PONDEROUS (Is the LLM on a coffee break?)"]
            return random.choice(jokes)
        if avg_cycle > self.CYCLE_WARNING:
            return "SLUGGISH (The gears need oil)"
        return "NOMINAL (Boringly adequate)"

    def get_report(self):
        avg_cycle = sum(self.cycle_times) / max(1, len(self.cycle_times))
        avg_llm = sum(self.llm_latencies) / max(1, len(self.llm_latencies))
        uptime = time.time() - self.start_time
        status_msg = self.pass_judgment(avg_cycle, avg_llm)
        return {
            "uptime_sec": int(uptime),
            "turns": self.user_turns,
            "avg_cycle_sec": round(avg_cycle, 2),
            "avg_llm_sec": round(avg_llm, 2),
            "status": status_msg,
            "errors": dict(self.error_counts),
            "graph_size": self.memory_snapshots[-1] if self.memory_snapshots else 0}

@dataclass
class SystemHealth:
    physics_online: bool = True
    bio_online: bool = True
    mind_online: bool = True
    cortex_online: bool = True
    errors: List[ErrorLog] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    observer: Optional['TheObserver'] = None

    def link_observer(self, observer_ref):
        self.observer = observer_ref

    def report_failure(self, component: str, error: Exception, severity="ERROR"):
        msg = str(error)
        self.errors.append(ErrorLog(component, msg, severity=severity))
        if self.observer:
            self.observer.log_error(component)
        if component == "PHYSICS": self.physics_online = False
        elif component == "BIO": self.bio_online = False
        elif component == "MIND": self.mind_online = False
        elif component == "CORTEX": self.cortex_online = False
        return f"[{component} OFFLINE]: {msg}"

    def report_warning(self, message: str):
        self.warnings.append(message)

    def report_hint(self, message: str):
        self.hints.append(message)

    def flush_feedback(self) -> Dict[str, List[str]]:
        feedback = {
            "warnings": list(self.warnings),
            "hints": list(self.hints)}
        self.warnings.clear()
        self.hints.clear()
        return feedback

@dataclass
class PhysicsPacket:
    voltage: float = 0.0
    narrative_drag: float = 0.0
    valence: float = 0.0
    repetition: float = 0.0
    atmosphere: str = "VOID"
    clean_words: List[str] = field(default_factory=list)
    counts: Dict[str, int] = field(default_factory=dict)
    vector: Dict[str, float] = field(default_factory=dict)
    psi: float = 0.0
    kappa: float = 0.0
    mass: float = 0.0
    coherence: float = 0.0
    abstraction: float = 0.0
    geodesic_mass: float = 0.0
    beta_index: float = 1.0
    gamma: float = 0.0
    turbulence: float = 0.0
    flow_state: str = "LAMINAR"
    zone: str = "COURTYARD"
    zone_color: str = "OCHRE"
    truth_ratio: float = 0.0
    raw_text: str = ""
    antigens: int = 0
    perfection_streak: int = 0
    avg_viscosity: float = 0.0
    E: float = 0.0
    B: float = 0.0
    humility_flag: bool = False
    system_surge_event: bool = False
    pain_signal: float = 0.0
    manifold: str = "THE_MUD"
    audit_trail: List[str] = field(default_factory=list)
    raw_text_display: str = ""
    entropy: float = 0.0

    def __getitem__(self, key): return getattr(self, key)

    def __setitem__(self, key, value): setattr(self, key, value)

    def __contains__(self, key): return hasattr(self, key)

    def get(self, key, default=None): return getattr(self, key, default)

    def update(self, data: Dict):
        for k, v in data.items():
            if hasattr(self, k): setattr(self, k, v)

    def snapshot(self) -> 'PhysicsPacket':
        data = self.to_dict()
        data['clean_words'] = list(self.clean_words)
        data['counts'] = self.counts.copy()
        data['vector'] = self.vector.copy()
        data['audit_trail'] = list(self.audit_trail)
        return PhysicsPacket(**data)

    def diff(self, other: 'PhysicsPacket') -> Dict[str, Tuple[Any, Any]]:
        deltas = {}
        for f in fields(self):
            key = f.name
            curr = getattr(self, key)
            if isinstance(other, dict):
                prev = other.get(key)
            elif hasattr(other, key):
                prev = getattr(other, key)
            else:
                prev = None
            if curr != prev:
                if isinstance(curr, float) and isinstance(prev, float):
                    if abs(curr - prev) < 0.001:
                        continue
                deltas[key] = (prev, curr)
        return deltas

    def diff_view(self, other: 'PhysicsPacket', indent: int = 3) -> str:
        deltas = self.diff(other)
        if not deltas:
            return f"{' ' * indent}{Prisma.GRY}(No State Drift){Prisma.RST}"
        lines = []
        for key, (old, new) in deltas.items():
            color = Prisma.CYN
            arrow = "->"
            if isinstance(new, (int, float)) and isinstance(old, (int, float)):
                if new > old:
                    color = Prisma.GRN
                    arrow = "▲"
                elif new < old:
                    color = Prisma.RED
                    arrow = "▼"
            str_old = str(old)
            str_new = str(new)
            if len(str_old) > 20: str_old = str_old[:17] + "..."
            if len(str_new) > 20: str_new = str_new[:17] + "..."
            lines.append(f"{' ' * indent}{Prisma.GRY}{key}:{Prisma.RST} {str_old} {color}{arrow}{Prisma.RST} {str_new}")
        return "\n".join(lines)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        valid_keys = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def to_dict(self):
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @property
    def electromagnetism(self) -> float:
        return math.sqrt(self.E**2 + self.B**2)

@dataclass
class CycleContext:
    input_text: str
    clean_words: List[str] = field(default_factory=list)
    physics: PhysicsPacket = field(default_factory=PhysicsPacket)
    logs: List[str] = field(default_factory=list)
    flux_log: List[Dict[str, Any]] = field(default_factory=list)
    is_alive: bool = True
    refusal_triggered: bool = False
    refusal_packet: Optional[Dict] = None
    is_bureaucratic: bool = False
    bio_result: Dict = field(default_factory=dict)
    world_state: Dict = field(default_factory=dict)
    mind_state: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    bureau_ui: str = ""
    user_profile: Dict = field(default_factory=lambda: {"name": "TRAVELER", "confidence": 0})
    last_impulse: Any = None

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
            last_impulse=self.last_impulse)
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
    dynamics: Any
    nav: Any
    tension: Any