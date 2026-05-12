"""core.py

This module houses the base primitives for state management, event routing,
telemetry, and reality-layer scoping. It is strictly decoupled from LLM execution
to ensure metabolic stability even if the cognitive layers crash.
"""

import glob
import json
import os
import random
import threading
import time
import traceback
import uuid
from collections import deque, Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from constants import Prisma, RealityLayer
from presets import BoneConfig
from struts import ux, ux_format, safe_get
from physics.models import PhysicsPacket, UserInferredState, SharedDynamics

class BoneJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (set, deque)):
            return list(obj)
        if hasattr(obj, "to_dict") and callable(obj.to_dict):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return vars(obj)
        return super().default(obj)


@dataclass
class ErrorLog:
    component: str
    error_msg: str
    timestamp: float = field(default_factory=time.time)
    severity: str = "WARNING"

    def __str__(self):
        return f"[{self.severity}] {self.component}: {self.error_msg}"


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
        return (f"CRYSTAL [{self.decision_id}] {self.system_state} | "
                f"ARCHETYPE: {self.active_archetype} | E: {e_val:.2f}")

    def crystallize(self) -> str:
        data = asdict(self)
        data["_summary"] = f"{self.system_state}::{self.active_archetype}"
        data["_type"] = "CRYSTAL"
        return json.dumps(data, cls=BoneJSONEncoder)


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
    trace_id: str = "UNKNOWN"
    limits: Dict[str, Any] = field(default_factory=dict)
    council_mandates: List[Any] = field(default_factory=list)
    last_dream: Optional[Dict] = None
    crash_error: Optional[Exception] = None

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


@dataclass
class MindSystem:
    mem: Any
    lex: Any
    dreamer: Any
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


class EventBus:
    def __init__(self, max_memory=None, config_ref=None, telemetry_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg_core = LoreManifest.get_instance().get("CORE_CONFIG") or {}
        limit = max_memory or cfg_core.get("EVENT_MAX_MEMORY", 1024)
        self.buffer = deque(maxlen=limit)
        self.subscribers = {}
        self.telemetry = telemetry_ref

    def subscribe(self, event_type, callback):
        subs = self.subscribers.setdefault(event_type, [])
        if callback not in subs:
            subs.append(callback)

    def unsubscribe(self, event_type, callback):
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
            except ValueError:
                pass

    def publish(self, event_type, data=None):
        if event_type not in self.subscribers: return
        for callback in self.subscribers[event_type][:]:
            try:
                callback(data)
            except Exception as e:
                cb_name = getattr(callback, "__name__", str(callback))
                if event_type != "EVENT_FAILURE":
                    tb_str = traceback.format_exc(limit=3)
                    self.log(f"EVENT_FAILURE: Error in '{cb_name}': {e}\n{tb_str}", source="EVENT_FAILURE",
                             level="CRIT")

    def log(self, message: str, source: str = "SYSTEM", level: str = "INFO"):
        event = {"timestamp": time.time(), "source": source, "level": level, "message": message, "text": message,
                 "_type": "EVENT_LOG"}
        self.buffer.append(event)
        self.publish(source, event)
        if self.telemetry:
            self.telemetry.record_event(event)
        if level in ("CRIT", "ERROR"):
            print(f"{Prisma.RED}[{source}] {message}{Prisma.RST}")

    def flush(self) -> List[Dict]:
        current_logs = list(self.buffer)
        self.buffer.clear()
        return current_logs

class LoreManifest:
    """
    The lazy-loaded, singleton data cache. We only load files from the disk when requested.
    """
    _instance = None

    def __init__(self, data_dir=None, config_ref=None):
        self.cfg = config_ref or BoneConfig
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.DATA_DIR = data_dir or os.path.join(base_dir, "lore")
        self._cache = {}

    @classmethod
    def get_instance(cls, config_ref=None):
        if cls._instance is None:
            cls._instance = LoreManifest(config_ref=config_ref)
        return cls._instance

    def get(self, category: str, sub_key: str = None) -> Any:
        cat_key = category.lower()
        if cat_key not in self._cache:
            self._cache[cat_key] = self._load_from_disk(cat_key) or {}
        data = self._cache[cat_key]
        if not sub_key:
            return data
        return data.get(sub_key) if isinstance(data, dict) else None

    def _load_from_disk(self, category: str) -> Optional[Dict]:
        safe_category = os.path.basename(category)
        filepath = os.path.join(self.DATA_DIR, f"{safe_category}.json")
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"{Prisma.RED}[LORE]: Corrupt JSON in '{category}': {e}{Prisma.RST}")
            return None

    def inject(self, category: str, data: Any):
        cat_key = category.lower()
        target = self._cache.setdefault(cat_key, {})
        if isinstance(target, dict) and isinstance(data, dict):
            target.update(data)
        else:
            self._cache[cat_key] = data

    def save(self, category: str):
        cat_key = category.lower()
        if cat_key not in self._cache or self._cache[cat_key] is None:
            print(f"{Prisma.YEL}[LORE]: Refusing to save null cache for '{cat_key}'. Preserving disk state.{Prisma.RST}")
            return
        filepath = os.path.join(self.DATA_DIR, f"{cat_key}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._cache[cat_key], f, indent=2, cls=BoneJSONEncoder)
            print(f"{Prisma.GRY}[LORE]: Persisted '{cat_key}'.{Prisma.RST}")
        except Exception as e:
            print(f"{Prisma.RED}[LORE]: Failed to save '{cat_key}': {e}{Prisma.RST}")

    def flush_cache(self, category: str = None):
        if not category:
            self._cache.clear()
            print(f"{Prisma.CYN}[LORE]: Flushed Lore cache.{Prisma.RST}")
            return
        cat_key = category.lower()
        if self._cache.pop(cat_key, None) is not None:
            print(f"{Prisma.CYN}[LORE]: Flushed '{cat_key}'.{Prisma.RST}")


class TheObserver:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.start_time = time.time()
        self.is_coupled = False
        cfg_core = LoreManifest.get_instance().get("CORE_CONFIG") or {}
        max_len = cfg_core.get("OBSERVER_MAX_LEN", 20)
        self.cycle_times = deque(maxlen=max_len)
        self.llm_latencies = deque(maxlen=max_len)
        self.memory_snapshots = deque(maxlen=max_len)
        self.error_counts = Counter()
        self.user_turns = 0
        self.LATENCY_WARNING = cfg_core.get("OBSERVER_LATENCY_WARN", 5.0)
        self.CYCLE_WARNING = cfg_core.get("OBSERVER_CYCLE_WARN", 8.0)
        self.C_EFF = cfg_core.get("OBSERVER_CYCLE_EFFICIENT", 0.1)
        self.L_EFF = cfg_core.get("OBSERVER_LLM_EFFICIENT", 0.5)
        self.last_cycle_duration = 0.0

    @staticmethod
    def clock_in():
        return time.perf_counter()

    def clock_out(self, start_time, metric_type="cycle"):
        duration = time.perf_counter() - start_time
        if metric_type == "cycle":
            self.cycle_times.append(duration)
            self.last_cycle_duration = duration
        elif metric_type == "llm":
            self.llm_latencies.append(duration)
        return duration

    @property
    def uptime(self) -> float:
        return time.time() - self.start_time

    def log_error(self, module_name):
        self.error_counts[module_name] += 1

    def record_memory(self, node_count):
        self.memory_snapshots.append(node_count)

    def pass_judgment(self, avg_cycle, avg_llm):
        if avg_cycle <= 0.001 and avg_llm <= 0.001:
            return ux("core_strings", "obs_asleep") or "Dormant."
        if avg_cycle < self.C_EFF and avg_llm < self.L_EFF:
            return ux("core_strings", "obs_efficient") or "High Efficiency."
        if avg_llm > self.LATENCY_WARNING:
            target_key = random.choice(["obs_fog", "obs_degraded", "obs_ponderous"])
            return ux("core_strings", target_key) or "High Cognitive Load."
        if avg_cycle > self.CYCLE_WARNING:
            return ux("core_strings", "obs_sluggish") or "System Sluggish."
        if self.is_coupled:
            return ux_format("core_strings", "obs_coupled", default="Harmonic Resonance: Presence Active.")
        return ux("core_strings", "obs_nominal") or "Nominal."

    @property
    def avg_cycle(self) -> float:
        return sum(self.cycle_times) / max(1, len(self.cycle_times))

    @property
    def avg_llm(self) -> float:
        return sum(self.llm_latencies) / max(1, len(self.llm_latencies))

    def get_report(self):
        status_msg = self.pass_judgment(self.avg_cycle, self.avg_llm)
        return {"uptime_sec": int(self.uptime), "turns": self.user_turns, "avg_cycle_sec": round(self.avg_cycle, 2),
                "avg_llm_sec": round(self.avg_llm, 2), "status": status_msg, "errors": dict(self.error_counts),
                "graph_size": self.memory_snapshots[-1] if self.memory_snapshots else 0}

@dataclass
class SystemHealth:
    physics_online: bool = True
    bio_online: bool = True
    mind_online: bool = True
    errors: deque = field(default_factory=lambda: deque(maxlen=50))
    warnings: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    observer: Optional["TheObserver"] = None

    def link_observer(self, observer_ref):
        self.observer = observer_ref

    def report_failure(self, component: str, error: Exception, severity="ERROR"):
        msg = str(error)
        self.errors.append(ErrorLog(component, msg, severity=severity))
        if self.observer:
            self.observer.log_error(component)
        attr_name = f"{component.lower()}_online"
        if hasattr(self, attr_name):
            setattr(self, attr_name, False)
        return ux_format("core_strings", "health_offline", component=component, msg=msg)

    def report_warning(self, message: str):
        self.warnings.append(message)

    def report_hint(self, message: str):
        self.hints.append(message)

    def flush_feedback(self) -> Dict[str, List[str]]:
        feedback = {"warnings": list(self.warnings), "hints": list(self.hints)}
        self.warnings.clear()
        self.hints.clear()
        return feedback

class RealityStack:
    def __init__(self):
        self._stack = [RealityLayer.SIMULATION]

    @property
    def current_depth(self) -> int:
        return self._stack[-1]

    def push_layer(self, layer: int) -> bool:
        if layer == self.current_depth:
            return True
        if layer == RealityLayer.DEBUG or layer == self.current_depth + 1:
            self._stack.append(layer)
            return True
        raise ValueError(f"Reality Layer Violation: Cannot topologically shift from layer {self.current_depth} to {layer}.")

    def pop_layer(self) -> int:
        if len(self._stack) > 1:
            return self._stack.pop()
        return self._stack[0]

    def stabilize_at(self, layer: int):
        self._stack = [layer]

    def get_grammar_rules(self) -> Dict[str, bool]:
        d = self.current_depth
        return {"allow_narrative": d in (RealityLayer.SIMULATION, RealityLayer.DEEP_CX, RealityLayer.DEBUG),
                "allow_commands": d >= RealityLayer.SIMULATION, "allow_meta": d >= RealityLayer.DEBUG,
                "raw_output": d == RealityLayer.DEEP_CX, "system_override": d == RealityLayer.DEBUG}

class CyberneticGovernor:
    def __init__(self, config_ref=None):
        self.target_d = None
        self.target_v = None
        self.cfg = config_ref or BoneConfig
        self.beth_index, self.order = 0.5, 1

    def calculate_coupling(self, phi: float, resonance_delta: float, user_exhaustion: float) -> float:
        coherence_debt = (user_exhaustion ** 1.5) * (1.0 - phi)
        self.beth_index = max(0.0, min(1.0, (phi * 0.6) + (user_exhaustion * 0.4) + (coherence_debt * 0.3)))
        self.order = 2 if self.beth_index >= 0.75 or (resonance_delta > 0.3 and user_exhaustion > 0.5) else 1
        return self.beth_index

    def get_policy_shift(self) -> str:
        if self.order == 2:
            return "CO_REGULATION"
        return "EFFICIENCY"

    def recalibrate(self, target_voltage: float, target_drag: float):
        self.target_v = target_voltage
        self.target_d = target_drag

    def regulate(self, physics: Any, dt: float, endocrine_state: Any = None) -> Tuple[float, float]:
        if self.target_v is None or self.target_d is None:
            return 0.0, 0.0
        current_v = float(safe_get(physics, "voltage", self.target_v))
        current_d = float(safe_get(physics, "narrative_drag", self.target_d))
        v_force = (self.target_v - current_v) * 0.5 * dt
        d_force = (self.target_d - current_d) * 0.5 * dt
        return v_force, d_force

class ArchetypeArbiter:
    @staticmethod
    def arbitrate(physics_lens: str, soul_archetype: str, council_mandates: List[Dict],
                  trigram: Dict = None) -> Tuple[str, str, str]:
        mandate_types = {m.get("type", m.get("action")) for m in (council_mandates or [])}

        if "LOCKDOWN" in mandate_types:
            return "THE CENSOR", "COUNCIL", ux("core_strings", "arb_martial_law") or "[COUNCIL]: Martial Law. Lockdown initiated."
        if "FORCE_MODE" in mandate_types:
            return "THE MACHINE", "COUNCIL", ux("core_strings", "arb_bureaucratic") or "[COUNCIL]: Bureaucratic Override active."

        if soul_archetype and "/" in soul_archetype:
            msg = ux_format("core_strings", "arb_diamond", soul_archetype=soul_archetype,
                            default=f"Gestalt Resonance: {soul_archetype}")
            return soul_archetype, "SOUL", msg
        if trigram:
            meta_resonance = LoreManifest.get_instance().get("NARRATIVE_DATA", "_META_RESONANCE_") or []
            for r in meta_resonance:
                if r.get("trigram") == trigram.get("name") and r.get("lens", physics_lens) == physics_lens and r.get(
                        "soul", soul_archetype) == soul_archetype:
                    return r["result"], r.get("source", "COSMIC"), r.get("msg") or ux("core_strings", "arb_resonance") or "Cosmic Resonance."
        loud_lenses = LoreManifest.get_instance().get("COUNCIL_DATA", "LOUD_LENSES") or ["THE MANIC", "THE VOID"]
        if physics_lens in loud_lenses:
            msg = ux_format("core_strings", "arb_loud", physics_lens=physics_lens,
                            default=f"Physics Override: {physics_lens}")
            return physics_lens, "PHYSICS", msg
        return soul_archetype, "SOUL", ux("core_strings", "arb_soul") or "The soul speaks."

class TelemetryService:
    _tracer_instance = None

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg_core = LoreManifest.get_instance().get("CORE_CONFIG") or {}
        self.log_dir = cfg_core.get("TELEMETRY_LOG_DIR", "logs/telemetry")
        self.BUFFER_SIZE = cfg_core.get("TELEMETRY_BUFFER_SIZE", 50)
        self.MAX_ERRORS = cfg_core.get("TELEMETRY_MAX_ERRORS", 5)
        self.write_buffer: List[str] = []
        self.active_crystal = None
        self.disabled = False
        self.crystals_logged = 0
        self._lock = threading.Lock()
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            self.current_trace_file = os.path.join(self.log_dir, f"trace_{int(time.time())}.jsonl")
            self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="BoneTelemetry")
        except OSError as e:
            msg = ux("core_strings", "tel_disk_denied") or "Disk access denied for Telemetry."
            print(f"{Prisma.OCHRE}[GRACEFUL DEGRADATION] {msg} - {e}. Telemetry offline.{Prisma.RST}")
            self.disabled = True
            self.current_trace_file = None
            self._executor = None

    def record_event(self, event_dict: dict):
        if self.disabled or not self.current_trace_file:
            return
        try:
            serialized = json.dumps(event_dict, cls=BoneJSONEncoder)
            self._buffer_line(serialized)
        except (TypeError, ValueError) as e:
            print(f"{Prisma.YEL}[TELEMETRY] Dropped un-serializable event: {e}{Prisma.RST}")

    @classmethod
    def get_instance(cls, config_ref=None):
        if cls._tracer_instance is None:
            cls._tracer_instance = TelemetryService(config_ref=config_ref)
        return cls._tracer_instance

    def start_cycle(self, trace_id: str):
        if self.disabled:
            return
        if self.active_crystal:
            if self.active_crystal.decision_id == trace_id:
                return
            self.finalize_cycle()
        self.active_crystal = DecisionCrystal(decision_id=trace_id)

    def log_crystal(self, crystal: DecisionCrystal):
        if self.disabled:
            return
        self._buffer_line(crystal.crystallize())
        self.crystals_logged += 1

    def finalize_cycle(self):
        if self.active_crystal:
            self.log_crystal(self.active_crystal)
            self.active_crystal = None
        self.flush_to_disk()

    def _buffer_line(self, json_str: str):
        if self.disabled: return
        with self._lock:
            self.write_buffer.append(json_str)
            if len(self.write_buffer) >= self.BUFFER_SIZE: self.flush_to_disk_locked()

    def flush_to_disk_locked(self):
        if self.disabled or not self.current_trace_file or not self.write_buffer: return
        self._executor.submit(self._bg_write, list(self.write_buffer), self.current_trace_file)
        self.write_buffer.clear()

    def flush_to_disk(self):
        with self._lock:
            self.flush_to_disk_locked()

    @staticmethod
    def _bg_write(lines, filepath):
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except IOError as e:
            print(f"{Prisma.RED}[TELEMETRY DECAY] Background write failed: {e}{Prisma.RST}")

    def shutdown(self):
        self.flush_to_disk()
        if self._executor is not None:
            self._executor.shutdown(wait=True)

    def _yield_historical_records(self, file_limit=5, lines_per_file=10):
        if not os.path.exists(self.log_dir): return
        files = sorted(glob.glob(os.path.join(self.log_dir, "trace_*.jsonl")), reverse=True)
        for fpath in files[:file_limit]:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    tail_lines = reversed(deque(f, maxlen=lines_per_file))
                for line in tail_lines:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
            except IOError:
                continue

    def read_recent_history(self, limit=4) -> List[str]:
        history = deque(maxlen=limit)
        for data in self._yield_historical_records(lines_per_file=limit * 2):
            if len(history) >= limit: break
            resp = data.get("final_response")
            if not resp: continue
            user_text = data.get("prompt_snapshot", "").partition("User:")[2].split("\n", 1)[0].strip() or "Unknown"
            history.appendleft(f"User: {user_text} | System: {resp}")
        return list(history)

    def get_last_thoughts(self, limit=3) -> List[str]:
        history = self.read_recent_history(limit)
        return [h.partition("System: ")[2].strip() for h in history if "System: " in h]

    def get_last_fatal_error(self) -> Optional[str]:
        for data in self._yield_historical_records(file_limit=5, lines_per_file=50):
            if "CRITICAL" in str(data.get("outcome", "")):
                return ux_format("core_strings", "tel_prev_crash", default="Crash: {reason}", reason=data.get("reasoning", "Unknown"))
        return None

    def generate_session_summary(self, _uptime: float = 0.0) -> str:
        self.flush_to_disk()
        return ux_format("core_strings", "tel_session_summary", status="DISABLED" if self.disabled else "ACTIVE",
                         count=self.crystals_logged, trace_file=self.current_trace_file)
