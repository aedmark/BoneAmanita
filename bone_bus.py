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
    def paint(cls, text: str, color_key: str = "0") -> str:
        code = cls._COLOR_MAP.get(str(color_key).upper(), cls.WHT)
        if str(text).endswith(cls.RST):
            return f"{code}{text}"
        return f"{code}{text}{cls.RST}"

    @classmethod
    def strip(cls, text: str) -> str:
        clean = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return clean.sub('', str(text))

    @classmethod
    def tie_dye(cls, text: str) -> str:
        colors = [cls.RED, cls.GRN, cls.YEL, cls.CYN, cls.MAG, cls.VIOLET, cls.OCHRE]
        return "".join(
            f"{random.choice(colors)}{char}{cls.RST}" if char.strip() else char
            for char in str(text))

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

    def publish(self, event_type, data=None, priority=False):
        if self.dormant and not priority:
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
    SANCTUARY = {
        "VOLTAGE_TARGET": 7.0,
        "VOLTAGE_TOLERANCE": 3.0,
        "DRAG_TARGET": 2.0,
        "DRAG_TOLERANCE": 1.5,
        "TRUTH_TARGET": 0.7,
        "E_TARGET": 0.4,
        "B_TARGET": 0.5,
        "ZONE": "SANCTUARY",
        "COLOR": Prisma.GRN}

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
    def reconcile_state(cls, physics_packet: 'PhysicsPacket'):
        if physics_packet.voltage > cls.PHYSICS.VOLTAGE_MAX:
            physics_packet.voltage = cls.PHYSICS.VOLTAGE_MAX
        if physics_packet.voltage < cls.PHYSICS.VOLTAGE_FLOOR:
            physics_packet.voltage = cls.PHYSICS.VOLTAGE_FLOOR
        if physics_packet.narrative_drag < cls.PHYSICS.DRAG_FLOOR:
            physics_packet.narrative_drag = cls.PHYSICS.DRAG_FLOOR
        if physics_packet.narrative_drag > cls.PHYSICS.DRAG_HALT:
            physics_packet.narrative_drag = cls.PHYSICS.DRAG_HALT
        return physics_packet

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
                    target_attr = getattr(cls, key)
                    if isinstance(target_attr, type) and isinstance(value, dict):
                        for sub_key, sub_val in value.items():
                            if hasattr(target_attr, sub_key):
                                setattr(target_attr, sub_key, sub_val)
                    else:
                        setattr(cls, key, value)
            return True, f"Configuration loaded. {log}"
        except Exception as e:
            return False, f"Config load failed: {e}"

    @classmethod
    def save_to_file(cls, filepath="bone_config.json"):
        data = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, type):
                data[attr_name] = {}
                for sub_attr in dir(attr):
                    if not sub_attr.startswith("__"):
                        val = getattr(attr, sub_attr)
                        if isinstance(val, (int, float, str, bool, list, dict)):
                            data[attr_name][sub_attr] = val
            elif not attr_name.startswith("__") and not callable(attr):
                if isinstance(attr, (int, float, str, bool, list, dict)):
                    data[attr_name] = attr
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            return True, f"Config saved to {filepath}"
        except Exception as e:
            return False, f"Save failed: {e}"

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
        return {f.name: getattr(self, f.name) for f in fields(self)}

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
    original_snapshot: PhysicsPacket
    modifications: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def create(cls, packet: PhysicsPacket) -> 'PhysicsSandbox':
        return cls(packet=packet, original_snapshot=packet.snapshot())

    def apply_delta(self, key: str, value: Any, reason: str = ""):
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
        for f in fields(self.original_snapshot):
            setattr(self.packet, f.name, getattr(self.original_snapshot, f.name))

    def __getattr__(self, name):
        return getattr(self.packet, name)

    def __setattr__(self, name, value):
        if name in ['packet', 'original_snapshot', 'modifications']:
            super().__setattr__(name, value)
        else:
            self.apply_delta(name, value, reason="AUTO_TRACE")

class RealityLayer:
    TERMINAL = 0
    SIMULATION = 1
    VILLAGE = 2
    DEBUG = 3
    DEEP_CX = 4

class RealityStack:
    def __init__(self):
        self._stack = [RealityLayer.SIMULATION]
        self._lock = False

    @property
    def current_depth(self) -> int:
        return self._stack[-1]

    def push_layer(self, layer: int, context: Any = None) -> bool:
        if self._lock: return False
        if layer == RealityLayer.DEBUG or layer == self.current_depth + 1:
            self._stack.append(layer)
            return True
        return False

    def pop_layer(self) -> int:
        if self._lock: return self.current_depth
        if len(self._stack) > 1:
            return self._stack.pop()
        return self._stack[0]

    def stabilize_at(self, layer: int):
        self._stack = [layer]

    def get_grammar_rules(self) -> Dict[str, bool]:
        depth = self.current_depth
        return {
            "allow_narrative": depth == RealityLayer.SIMULATION,
            "allow_commands": depth <= RealityLayer.VILLAGE,
            "allow_meta": depth >= RealityLayer.DEBUG,
            "raw_output": depth == RealityLayer.DEEP_CX}

@dataclass
class CycleContext:
    input_text: str
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
    reality_stack: RealityStack = field(default_factory=RealityStack)
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
            reality_stack=copy.deepcopy(self.reality_stack),
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

class ArchetypeArbiter:
    def arbitrate(self, physics_lens: str, soul_archetype: str, council_mandates: List[Dict]) -> Tuple[str, str, str]:
        for mandate in council_mandates:
            if mandate.get("type") == "LOCKDOWN":
                return "THE CENSOR", "COUNCIL", "Martial Law declared. Identity suppressed."
            if mandate.get("type") == "FORCE_MODE":
                return "THE MACHINE", "COUNCIL", "Bureaucratic override active."

        if "/" in soul_archetype:
            return soul_archetype, "SOUL", f"The Diamond Soul refracts the physics ({soul_archetype})."

        if physics_lens in ["THE MANIC", "THE VOID"]:
            return physics_lens, "PHYSICS", f"Environment is too loud. You are {physics_lens}."

        return soul_archetype, "SOUL", "The Soul guides the lens."