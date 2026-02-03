""" bone_telemetry.py """

import json, time, os, glob, uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field
from bone_bus import Prisma, BoneConfig

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

    def crystallize(self) -> str:
        e = self.leverage_metrics.get('E', 0.0)
        b = self.leverage_metrics.get('Beta', 0.0)
        volts = self.physics_state.get('voltage', 0.0)
        return (
            f"💎 VSL CRYSTAL [{self.decision_id}] | {self.active_archetype}\n"
            f"   METRICS: E: {e:.2f} | β: {b:.2f} | V: {volts:.1f}\n"
            f"   STATE: {self.system_state} | MANDATES: {len(self.council_mandates)}")

    def to_json(self):
        return json.dumps(asdict(self))

class StructuredLogger:
    def __init__(self, session_id: str, log_dir: str = "telemetry"):
        self.session_id = session_id
        filepath = os.path.join(log_dir, f"trace_{session_id}.jsonl")
        self.manager = LogManager(filepath)
        print(f"{Prisma.CYN}[TELEMETRY]: Observability Layer Active.{Prisma.RST}")
        print(f"{Prisma.GRY}   > Managed by LogManager at: {filepath}{Prisma.RST}")

    def capture_decision(self, component: str, decision_type: str,
                         inputs: Dict, reasoning: str, outcome: str):
        trace = DecisionTrace(
            trace_id=str(uuid.uuid4())[:8],
            timestamp=time.time(),
            component=component,
            decision_type=decision_type,
            inputs=self._sanitize(inputs),
            reasoning=reasoning,
            outcome=outcome)
        self.manager.write(trace.to_json())

    def _sanitize(self, data: Any, depth: int = 0, max_depth: int = 3) -> Any:
        if depth > max_depth:
            return "<Max Depth Exceeded>"

        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        if isinstance(data, dict):
            return {k: self._sanitize(v, depth + 1, max_depth)
                    for k, v in data.items() if k != "graph"}
        if isinstance(data, list):
            return [self._sanitize(i, depth + 1, max_depth) for i in data]
        if hasattr(data, '__dict__'):
            return self._sanitize(vars(data), depth + 1, max_depth)
        return str(data)

@dataclass
class PhaseTrace:
    phase_name: str
    start_time: float
    end_time: float = 0.0
    initial_snapshot: Dict = field(default_factory=dict)
    final_snapshot: Dict = field(default_factory=dict)
    state_diff: Dict = field(default_factory=dict)
    duration: float = 0.0

@dataclass
class CycleTrace:
    cycle_id: str
    start_time: float
    end_time: float = 0.0
    phases: Dict[str, PhaseTrace] = field(default_factory=dict)
    decisions: List[Dict] = field(default_factory=list)
    performance: Dict[str, float] = field(default_factory=dict)

    def to_json(self):
        return json.dumps(asdict(self))

class LogManager:
    MAX_BYTES = 5 * 1024 * 1024
    BACKUP_COUNT = 5

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._file = None
        self._open_file()

    def _open_file(self):
        self._ensure_dir()
        self._file = open(self.filepath, "a", encoding="utf-8")

    def _ensure_dir(self):
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError:
                pass

    def write(self, data: str):
        if self._file is None:
            self._open_file()
        try:
            self._file.write(data + "\n")
            self._file.flush()
            if self._file.tell() >= self.MAX_BYTES:
                self._rotate()
        except Exception as e:
            print(f"{Prisma.RED}[LOG MANAGER FAIL]: {e}{Prisma.RST}")

    def _rotate(self):
        print(f"{Prisma.YEL}[LOG MANAGER]: Rotating logs. Flushing the bathtub.{Prisma.RST}")
        self._close()
        for i in range(self.BACKUP_COUNT - 1, 0, -1):
            src = f"{self.filepath}.{i}"
            dst = f"{self.filepath}.{i+1}"
            if os.path.exists(src):
                try:
                    os.rename(src, dst)
                except OSError:
                    pass
        if os.path.exists(self.filepath):
            try:
                os.rename(self.filepath, f"{self.filepath}.1")
            except OSError:
                pass
        self._open_file()

    def _close(self):
        if self._file:
            self._file.close()
            self._file = None

    def __del__(self):
        self._close()

class TelemetryService:
    _INSTANCE = None
    _TRACER = None

    def __init__(self, session_id: str, log_dir: str = "telemetry"):
        self.session_id = session_id
        filepath = os.path.join(log_dir, f"trace_{session_id}.jsonl")
        self.manager = LogManager(filepath)
        self.crystals: List[DecisionCrystal] = []
        print(f"{Prisma.CYN}[TELEMETRY]: Observability Layer Active.{Prisma.RST}")
        print(f"{Prisma.GRY}   > Managed by LogManager at: {filepath}{Prisma.RST}")

    @classmethod
    def get_instance(cls):
        if cls._INSTANCE is None:
            cls.initialize(f"auto_{int(time.time())}")
        return cls._INSTANCE

    @classmethod
    def initialize(cls, session_id):
        if cls._INSTANCE is None:
            cls._INSTANCE = TelemetryService(session_id)
        return cls._INSTANCE

    @classmethod
    def get_tracer(cls, session_id=None):
        if cls._TRACER is None:
            if session_id is None:
                session_id = str(uuid.uuid4())[:8]
            cls._TRACER = SimulationTracer(session_id)
        return cls._TRACER

    def log_crystal(self, crystal: DecisionCrystal):
        self.crystals.append(crystal)
        self.manager.write(crystal.to_json())
        if getattr(BoneConfig, "VERBOSE_LOGGING", False):
            print(f"{Prisma.GRY}[AUDIT]: {crystal.crystallize()}{Prisma.RST}")

    def capture_decision(self, component: str, decision_type: str,
                         inputs: Dict, reasoning: str, outcome: str):
        trace = DecisionTrace(
            trace_id=str(uuid.uuid4())[:8],
            timestamp=time.time(),
            component=component,
            decision_type=decision_type,
            inputs=self._sanitize(inputs),
            reasoning=reasoning,
            outcome=outcome)
        self.manager.write(trace.to_json())

    def _sanitize(self, data: Any, depth: int = 0, max_depth: int = 3) -> Any:
        if depth > max_depth:
            return "<Max Depth Exceeded>"
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        if isinstance(data, dict):
            return {k: self._sanitize(v, depth + 1, max_depth)
                    for k, v in data.items() if k != "graph"}
        if isinstance(data, list):
            return [self._sanitize(i, depth + 1, max_depth) for i in data]
        if hasattr(data, '__dict__'):
            return self._sanitize(vars(data), depth + 1, max_depth)
        return str(data)

class SimulationTracer:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = TelemetryService.initialize(session_id)
        self.current_cycle: Optional[CycleTrace] = None
        self.active_phases: Dict[str, PhaseTrace] = {}

    def start_cycle(self, cycle_id):
        self.current_cycle = CycleTrace(
            cycle_id=cycle_id,
            start_time=time.time())
        self.active_phases = {}

    def trace_cycle(self, cycle_id):
        self.start_cycle(cycle_id)

    def start_phase(self, phase_name: str, ctx=None):
        if not self.current_cycle: return
        snapshot = {}
        if ctx:
            snapshot = self._extract_metrics(ctx)
        self.active_phases[phase_name] = PhaseTrace(
            phase_name=phase_name,
            start_time=time.time(),
            initial_snapshot=snapshot)

    def end_phase(self, phase_name: str, start_ctx, end_ctx):
        if not self.current_cycle or phase_name not in self.active_phases:
            return
        trace = self.active_phases.pop(phase_name)
        trace.end_time = time.time()
        trace.duration = trace.end_time - trace.start_time
        if start_ctx and end_ctx:
            start_snapshot = trace.initial_snapshot or self._extract_metrics(start_ctx)
            end_snapshot = self._extract_metrics(end_ctx)
            trace.final_snapshot = end_snapshot
            trace.state_diff = self._diff_states(start_snapshot, end_snapshot)
        self.current_cycle.phases[phase_name] = trace

    def finalize_cycle(self):
        if not self.current_cycle: return
        self.current_cycle.end_time = time.time()
        # Log the cycle trace via the manager
        self.logger.manager.write(self.current_cycle.to_json())
        self.current_cycle = None

    def _extract_metrics(self, ctx) -> Dict:
        metrics = {}
        if hasattr(ctx, 'physics'):
            p = ctx.physics
            if hasattr(p, 'to_dict'):
                d = p.to_dict()
                metrics['physics'] = {k:v for k,v in d.items() if isinstance(v, (int, float, str, bool))}
            elif isinstance(p, dict):
                metrics['physics'] = {k:v for k,v in p.items() if isinstance(v, (int, float, str, bool))}
        if hasattr(ctx, 'bio_result'):
            metrics['bio'] = {k:v for k,v in ctx.bio_result.items() if isinstance(v, (int, float, str, bool))}
        return metrics

    def _diff_states(self, start: Dict, end: Dict) -> Dict:
        diffs = {}
        for category in start:
            if category not in end: continue
            s_cat = start[category]
            e_cat = end[category]
            cat_diff = {}
            for k, v in s_cat.items():
                if k in e_cat and e_cat[k] != v:
                    if isinstance(v, float) and isinstance(e_cat[k], float):
                        if abs(v - e_cat[k]) < 0.001: continue
                    cat_diff[k] = {"from": v, "to": e_cat[k]}
            if cat_diff:
                diffs[category] = cat_diff
        return diffs

    def diagnose_issue(self, symptom: str) -> str:
        symptom = symptom.lower()
        if "atp" in symptom and "drop" in symptom:
            return ("INVESTIGATION: RAPID ATP LOSS\n"
                    "1. Check MITOCHONDRIA efficiency in Bio System.\n"
                    "2. Check if HOSTILE NARRATIVE DRAG is taxing metabolism.\n"
                    "3. Verify no PARASITIC LOAD in Sensation Phase.")

        if "latency" in symptom or "lag" in symptom:
            return ("INVESTIGATION: SYSTEM LATENCY\n"
                    "1. Check LLM Response Times in Telemetry.\n"
                    "2. Verify Memory Graph size isn't exploding.\n"
                    "3. Check for infinite loops in Logic Phase.")

        return f"INVESTIGATION: UNKNOWN SYMPTOM '{symptom}'. Suggest checking traces for recent exceptions."

# [ADD TO END OF FILE]

class BlackBoxReader:
    def __init__(self, log_dir="telemetry"):
        self.log_dir = log_dir

    def get_recent_history(self, limit=5) -> List[str]:
        pattern = os.path.join(self.log_dir, "trace_*.jsonl")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        if not files:
            return ["Memory Void: No flight logs found."]
        target_file = files[0]
        narrative_log = []
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if "final_response" in data and data["final_response"]:
                            text = data["final_response"]
                            narrative_log.append(text)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            return [f"Memory Corruption: {e}"]
        return narrative_log[-limit:]

    def get_last_fatal_error(self) -> Optional[str]:
        pattern = os.path.join(self.log_dir, "trace_*.jsonl")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        if len(files) < 2: return None
        prev_file = files[1]
        try:
            with open(prev_file, 'r') as f:
                lines = f.readlines()
                if not lines: return None
                last_line = json.loads(lines[-1])
                if "outcome" in last_line and "CRITICAL" in str(last_line["outcome"]):
                    return f"PREVIOUS SYSTEM CRASH: {last_line.get('reasoning', 'Unknown Error')}"
        except:
            pass
        return None