""" dev/bone_telemetry.py """

import json, time, os, glob, uuid
from typing import Any, Dict, List, Optional, Deque
from collections import deque
from dataclasses import dataclass, asdict, field
from bone_bus import Prisma

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

class BlackBoxReader:
    def __init__(self, log_dir="logs/telemetry"):
        self.log_dir = log_dir

    def get_recent_history(self, limit=4) -> List[str]:
        if not os.path.exists(self.log_dir):
            return []
        pattern = os.path.join(self.log_dir, "trace_*.jsonl")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        history = []
        for fpath in files:
            if len(history) >= limit: break
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    lines = deque(f, maxlen=limit * 2)
                    for line in reversed(lines):
                        if len(history) >= limit: break
                        try:
                            data = json.loads(line)
                            if data.get("_type") == "CRYSTAL" or "final_response" in data:
                                resp = data.get("final_response", "")
                                if not resp: continue
                                prompt = data.get("prompt_snapshot", "")
                                user_text = "Unknown"
                                if "User:" in prompt:
                                    parts = prompt.split("User:")
                                    if len(parts) > 1:
                                        user_text = parts[1].split("\n")[0].strip()
                                entry = f"User: {user_text} | System: {resp}"
                                history.insert(0, entry)
                        except json.JSONDecodeError:
                            continue
            except Exception:
                continue
        return history[-limit:]

class TelemetryService:
    log_dir = "logs/telemetry"
    _tracer_instance = None

    def __init__(self):
        self.trace_buffer: Deque[DecisionTrace] = deque(maxlen=50)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.current_trace_file = os.path.join(
            self.log_dir, f"trace_{int(time.time())}.jsonl")
        self.active_crystal = None
        self.session_start = time.time()

    @classmethod
    def get_tracer(cls):
        if cls._tracer_instance is None:
            cls._tracer_instance = TelemetryService()
        return cls._tracer_instance

    @classmethod
    def get_instance(cls):
        return cls.get_tracer()

    def start_cycle(self, trace_id: str):
        self.active_crystal = DecisionCrystal(decision_id=trace_id)

    def log_decision(self, component: str, decision_type: str, inputs: Any, reasoning: str, outcome: str):
        if not self.active_crystal: return
        trace = DecisionTrace(
            trace_id=self.active_crystal.decision_id,
            timestamp=time.time(),
            component=component,
            decision_type=decision_type,
            inputs=inputs if isinstance(inputs, dict) else {"raw": str(inputs)},
            reasoning=reasoning,
            outcome=outcome)
        self.trace_buffer.append(trace)
        self._write_line(trace.to_json())

    def log_crystal(self, crystal: DecisionCrystal):
        self._write_line(crystal.crystallize())

    def start_phase(self, phase_name: str, context: Any):
        self.log_decision(
            component=phase_name,
            decision_type="PHASE_START",
            inputs={"timestamp": time.time()},
            reasoning="Phase execution initiated.",
            outcome="RUNNING")

    def end_phase(self, phase_name: str, ctx_before: Any, ctx_after: Any):
        self.log_decision(
            component=phase_name,
            decision_type="PHASE_END",
            inputs={"timestamp": time.time()},
            reasoning="Phase execution completed.",
            outcome="SUCCESS")

    def finalize_cycle(self):
        if self.active_crystal:
            self.log_crystal(self.active_crystal)
            self.active_crystal = None

    def _write_line(self, json_str: str):
        try:
            with open(self.current_trace_file, "a", encoding="utf-8") as f:
                f.write(json_str + "\n")
        except Exception:
            pass

    def get_last_thoughts(self, limit=3) -> List[str]:
        reader = BlackBoxReader(self.log_dir)
        history = reader.get_recent_history(limit)
        return [h.split("System: ")[-1] for h in history if "System: " in h]

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
                    return f"PREVIOUS SYSTEM CRASH: {last_line.get('reasoning', 'Unknown')}"
        except Exception:
            return None

    def generate_session_summary(self) -> str:
        count = len(self.trace_buffer)
        duration = time.time() - self.session_start
        return (
            f"\n[TELEMETRY] Session ended. {count} thoughts processed in {duration:.2f}s.\n"
            f"            Trace: {self.current_trace_file}")