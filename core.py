"""core.py

The Central Nervous System of the Hypervisor.
This module houses the base primitives for state management, event routing,
telemetry, and reality-layer scoping. It is strictly decoupled from LLM execution
to ensure metabolic stability even if the cognitive layers crash.
"""

import copy, glob, json, os, random, time, traceback, threading, uuid
from collections import deque, Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple, Deque
from struts import ux, ux_format, safe_get
from presets import BoneConfig
from constants import Prisma, RealityLayer

class BoneJSONEncoder(json.JSONEncoder):
    """Ensures complex biological data structures (sets, deques, dataclasses) serialize safely."""
    def default(self, obj):
        if isinstance(obj, (set, deque)): return list(obj)
        if hasattr(obj, "to_dict"): return obj.to_dict()
        if hasattr(obj, "__dict__"): return obj.__dict__
        return super().defau

from physics.models import PhysicsPacket, UserInferredState, SharedDynamics

# =============================================================================
# CORE ORCHESTRATION MODELS
# =============================================================================

@dataclass
class ErrorLog:
    component: str
    error_msg: str
    timestamp: float = field(default_factory=time.time)
    severity: str = "WARNING"

    def __str__(self):
        return f"[{self.severity}] {self.component}: {self.error_msg}"

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
            elif isinstance(val, (list, dict, set)):
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


# =============================================================================
# THE CIRCULATORY SYSTEM
# =============================================================================

class EventBus:
    """
    The asynchronous publisher/subscriber backbone.
    Bounded by a deque(maxlen) to prevent runaway memory leaks.
    """
    def __init__(self, max_memory=None, config_ref=None, telemetry_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg_core = LoreManifest.get_instance().get("CORE_CONFIG") or {}
        limit = max_memory or safe_get(cfg_core, "EVENT_MAX_MEMORY", 1024)

        self.buffer = deque(maxlen=limit)
        self.subscribers = {}
        self.telemetry = telemetry_ref

    def subscribe(self, event_type, callback):
        subs = self.subscribers.setdefault(event_type, [])
        if callback not in subs:
            subs.append(callback)

    def publish(self, event_type, data=None):
        if event_type not in self.subscribers: return
        # Iterate over a copy to allow safe pruning during execution
        for callback in self.subscribers[event_type][:]:
            try:
                callback(data)
            except Exception as e:
                # APOPTOTIC IMMUNE RESPONSE:
                # If a callback fails, it is a toxic node. We log the necrosis and
                # physically sever the connection to protect the host loop.
                cb_name = getattr(callback, "__name__", str(callback))
                short_err = f"Error in '{cb_name}': {e}"
                if msg := ux_format("core_strings", "bus_error", error_msg=short_err):
                    print(f"{Prisma.RED}{msg}{Prisma.RST}")

                if event_type != "EVENT_FAILURE":
                    self.log(f"EVENT_FAILURE: {short_err}\n{traceback.format_exc()}", source="EVENT_FAILURE", level="CRIT")

                if callback in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(callback)
                    print(f"{Prisma.RED}[IMMUNE] Apoptotic pruning applied to toxic callback: {cb_name}{Prisma.RST}")

    def log(self, message: str, source: str = "SYSTEM", level: str = "INFO"):
        """Creates an immutable, timestamped record of an event and pushes it downstream."""
        event = {"timestamp": time.time(), "source": source, "level": level, "message": message, "text": message, "_type": "EVENT_LOG"}
        self.buffer.append(event)
        self.publish(source, event)
        self.telemetry.record_event(event) if self.telemetry else print(f"[{source}] {message}")

    def flush(self) -> List[Dict]:
        """Drains the current buffer, returning the accumulated state and resetting the queue."""
        current_logs = list(self.buffer)
        self.buffer.clear()
        return current_logs

    def get_recent_logs(self, count=10):
        return list(self.buffer)[-count:]


# =============================================================================
# THE HIPPOCAMPUS
# =============================================================================

class LoreManifest:
    """
    The lazy-loaded, singleton data cache.
    We only load files from the disk when requested, preserving O(1)
    memory footprint during idle states.
    """
    _instance = None

    def __init__(self, data_dir=None, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.DATA_DIR = data_dir or "lore"
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
        filepath = os.path.join(self.DATA_DIR, f"{category}.json")
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"{Prisma.GRY}[LORE]: Lazy-loaded '{category}'.{Prisma.RST}")
            return data
        except Exception as e:
            print(f"{Prisma.RED}[LORE]: Corrupt JSON in '{category}': {e}{Prisma.RST}")
            return None

    def inject(self, category: str, data: Any):
        """Allows runtime systems to append or override static lore matrices."""
        cat_key = category.lower()
        target = self._cache.setdefault(cat_key, {})
        if isinstance(target, dict) and isinstance(data, dict):
            target.update(data)
        else:
            self._cache[cat_key] = data

    def save(self, category: str):
        """Flushes mutated runtime state back to physical disk storage."""
        cat_key = category.lower()
        if cat_key not in self._cache:
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
        else:
            print(f"{Prisma.GRY}[LORE]: Category '{cat_key}' not in cache.{Prisma.RST}")


# =============================================================================
# METABOLIC GOVERNANCE & TELEMETRY
# =============================================================================

class TheObserver:
    """
    The System Vitals monitor.
    Tracks latency, graph bloat, and execution loops to infer the biological
    exhaustion of the active model and hardware.
    """
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.cyber_gov = CyberneticGovernor(config_ref=self.cfg)
        self.start_time = time.time()

        cfg_core = LoreManifest.get_instance().get("CORE_CONFIG") or {}
        max_len = safe_get(cfg_core, "OBSERVER_MAX_LEN", 20)

        self.cycle_times = deque(maxlen=max_len)
        self.llm_latencies = deque(maxlen=max_len)
        self.memory_snapshots = deque(maxlen=max_len)
        self.error_counts = Counter()
        self.user_turns = 0

        self.LATENCY_WARNING = (safe_get(cfg_core, "OBSERVER_LATENCY_WARN", 5.0))
        self.CYCLE_WARNING = (safe_get(cfg_core, "OBSERVER_CYCLE_WARN", 8.0))
        self.C_EFF = safe_get(cfg_core, "OBSERVER_CYCLE_EFFICIENT", 0.1)
        self.L_EFF = safe_get(cfg_core, "OBSERVER_LLM_EFFICIENT", 0.5)
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
        """Translates numerical vitals into somatic states."""
        if avg_cycle == 0.0 and avg_llm == 0.0:
            return ux("core_strings", "obs_asleep")
        if avg_cycle < self.C_EFF and avg_llm < self.L_EFF:
            return ux("core_strings", "obs_efficient")
        if avg_llm > self.LATENCY_WARNING:
            valid_msgs = [msg for k in ("obs_fog", "obs_degraded", "obs_ponderous") if (msg := ux("core_strings", k))]
            return random.choice(valid_msgs) if valid_msgs else ""
        if avg_cycle > self.CYCLE_WARNING:
            return ux("core_strings", "obs_sluggish")
        if self.cyber_gov.order == 2:
            return ux_format("core_strings", "obs_coupled", "Harmonic Resonance: Presence Active.")
        return ux("core_strings", "obs_nominal")

    def get_report(self):
        avg_cycle = sum(self.cycle_times) / max(1, len(self.cycle_times))
        avg_llm = sum(self.llm_latencies) / max(1, len(self.llm_latencies))
        uptime = time.time() - self.start_time
        status_msg = self.pass_judgment(avg_cycle, avg_llm)
        return {"uptime_sec": int(uptime), "turns": self.user_turns, "avg_cycle_sec": round(avg_cycle, 2),
                "avg_llm_sec": round(avg_llm, 2), "status": status_msg, "errors": dict(self.error_counts),
                "graph_size": self.memory_snapshots[-1] if self.memory_snapshots else 0}

@dataclass
class SystemHealth:
    """A boolean state-matrix of the hypervisor's active layers."""
    physics_online: bool = True
    bio_online: bool = True
    mind_online: bool = True
    cortex_online: bool = True
    errors: List[ErrorLog] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    observer: Optional["TheObserver"] = None

    def link_observer(self, observer_ref):
        self.observer = observer_ref

    _HEALTH_MAP = { "physics": "physics_online", "bio": "bio_online", "mind": "mind_online", "cortex": "cortex_online"}

    def report_failure(self, component: str, error: Exception, severity="ERROR"):
        msg = str(error)
        self.errors.append(ErrorLog(component, msg, severity=severity))
        if self.observer:
            self.observer.log_error(component)

        comp_key = component.lower()
        if comp_key in self._HEALTH_MAP:
            setattr(self, self._HEALTH_MAP[comp_key], False)
        else:
            self.report_warning(
                f"Unmapped component '{component}' reported a failure. Missing from SystemHealth dataclass.")
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
    """
    A stack-based Finite State Machine mapping the depth of execution context.
    Prevents narrative generation algorithms from executing during low-level debug loops.
    """
    def __init__(self):
        self._stack = [RealityLayer.SIMULATION]

    @property
    def current_depth(self) -> int:
        return self._stack[-1]

    def push_layer(self, layer: int, _context: Any = None) -> bool:
        if layer == self.current_depth:
            return True
        if layer == RealityLayer.DEBUG or layer == self.current_depth + 1:
            self._stack.append(layer)
            return True
        return False

    def pop_layer(self) -> int:
        if len(self._stack) > 1:
            return self._stack.pop()
        return self._stack[0]

    def stabilize_at(self, layer: int):
        self._stack = [layer]

    def get_grammar_rules(self) -> Dict[str, bool]:
        """Limits the allowed verbs based on the current reality depth."""
        d = self.current_depth
        return {"allow_narrative": d in (RealityLayer.SIMULATION, RealityLayer.DEEP_CX, RealityLayer.DEBUG),
                "allow_commands": d >= RealityLayer.SIMULATION, "allow_meta": d >= RealityLayer.DEBUG,
                "raw_output": d == RealityLayer.DEEP_CX, "system_override": d == RealityLayer.DEBUG}

class CyberneticGovernor:
    """
    The Mathematical bridge between the human user and the digital engine.
    Calculates the 'Beth Index' to trigger Macro-Policy Shifts.
    """
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.beth_index, self.order = 0.5, 1

    def calculate_coupling(self, phi: float, resonance_delta: float, user_exhaustion: float) -> float:
        coherence_debt = (user_exhaustion**1.5) * (1.0 - phi)
        # Binds systemic health to the user's metabolic state
        self.beth_index = max(0.0, min(1.0, (phi * 0.6) + (user_exhaustion * 0.4) + (coherence_debt * 0.3)))
        # Order 2 == Second-Order Cybernetics (Co-Regulation)
        self.order = 2 if self.beth_index >= 0.75 or (resonance_delta > 0.3 and user_exhaustion > 0.5) else 1
        return self.beth_index

    def get_policy_shift(self) -> str:
        if self.order == 2:
            return "CO_REGULATION"
        return "EFFICIENCY"

class ArchetypeArbiter:
    """
    The casting director. Resolves the math of the soul, physics, and governor
    into a distinct Village Voice.
    """
    @staticmethod
    def arbitrate(physics_lens: str, soul_archetype: str, council_mandates: List[Dict],
                  trigram: Dict = None, config_ref=None, ) -> Tuple[str, str, str]:
        mandates = council_mandates or []

        # Hard overrides based on systemic trauma or toxicity.
        if any(m.get("type") == "LOCKDOWN" for m in mandates):
            return "THE CENSOR", "COUNCIL", ux("core_strings", "arb_martial_law")
        if any(m.get("type") == "FORCE_MODE" for m in mandates):
            return "THE MACHINE", "COUNCIL", ux("core_strings", "arb_bureaucratic")

        # Hybrid states and Gestalt resonance mappings
        if soul_archetype and "/" in soul_archetype:
            return soul_archetype, "SOUL", ux_format("core_strings", "arb_diamond", soul_archetype=soul_archetype)
        if trigram:
            meta_resonance = LoreManifest.get_instance().get("NARRATIVE_DATA", "_META_RESONANCE_") or []
            for r in meta_resonance:
                if r.get("trigram") == trigram.get("name") and r.get("lens", physics_lens) == physics_lens and r.get(
                        "soul", soul_archetype) == soul_archetype:
                    return r["result"], r.get("source", "COSMIC"), r.get("msg") or ux("core_strings", "arb_resonance")

        loud_lenses = LoreManifest.get_instance().get("COUNCIL_DATA", "LOUD_LENSES") or ["THE MANIC", "THE VOID"]
        if physics_lens in loud_lenses:
            return physics_lens, "PHYSICS", ux_format("core_strings", "arb_loud", physics_lens=physics_lens)
        return soul_archetype, "SOUL", ux("core_strings", "arb_soul")


# =============================================================================
# ASYNCHRONOUS LOGGING & SUBCONSCIOUS WRITING
# =============================================================================

class TelemetryService:
    """
    The background execution layer that records the internal logic of the engine
    without blocking the primary LLM conversational loop.
    """
    _tracer_instance = None

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg_core = LoreManifest.get_instance().get("CORE_CONFIG") or {}
        self.log_dir = (safe_get(cfg_core, "TELEMETRY_LOG_DIR", "logs/telemetry"))
        self.BUFFER_SIZE = (safe_get(cfg_core, "TELEMETRY_BUFFER_SIZE", 50))
        self.MAX_ERRORS = (safe_get(cfg_core, "TELEMETRY_MAX_ERRORS", 5))

        self.trace_buffer: Deque[DecisionTrace] = deque(maxlen=self.BUFFER_SIZE)
        self.write_buffer: List[str] = []
        self.active_crystal = None
        self.disabled = False
        self._lock = threading.Lock()

        try:
            os.makedirs(self.log_dir, exist_ok=True)
            self.current_trace_file = os.path.join(self.log_dir, f"trace_{int(time.time())}.jsonl")
        except OSError as e:
            # Apoptotic Fallback: If disk I/O fails, shut down the logger, keep the engine alive.
            msg = ux("core_strings", "tel_disk_denied") or "Disk access denied for Telemetry."
            print(f"{Prisma.OCHRE}[GRACEFUL DEGRADATION] {msg} - {e}. Telemetry offline.{Prisma.RST}")
            self.disabled = True
            self.current_trace_file = None

        # Offloads file operations to a dedicated thread to preserve main loop tensegrity.
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="BoneTelemetry")

    def record_event(self, event_dict: dict):
        if self.disabled or not self.current_trace_file:
            return
        self._buffer_line(json.dumps(event_dict, cls=BoneJSONEncoder))

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

    def log_decision(self, component: str, decision_type: str, inputs: Any, reasoning: str, outcome: str):
        if self.disabled or not self.active_crystal:
            return
        trace = DecisionTrace(trace_id=self.active_crystal.decision_id, timestamp=time.time(), component=component,
                              decision_type=decision_type,
                              inputs=inputs if isinstance(inputs, dict) else {"raw": str(inputs)}, reasoning=reasoning,
                              outcome=outcome)
        self.trace_buffer.append(trace)
        self._buffer_line(trace.to_json())

    def log_crystal(self, crystal: DecisionCrystal):
        if self.disabled:
            return
        self._buffer_line(crystal.crystallize())

    def start_phase(self, phase_name: str, _context: Any):
        self.log_decision(phase_name, "PHASE_START", {"timestamp": time.time()}, ux("core_strings", "tel_phase_start"), "RUNNING")

    def end_phase(self, phase_name: str, _ctx_before: Any, _ctx_after: Any):
        self.log_decision(phase_name, "PHASE_END", {"timestamp": time.time()}, ux("core_strings", "tel_phase_end"), "SUCCESS")

    def finalize_cycle(self):
        if self.active_crystal:
            self.log_crystal(self.active_crystal)
            self.active_crystal = None
        self.flush_to_disk()

    def _buffer_line(self, json_str: str):
        if self.disabled: return
        with self._lock:
            self.write_buffer.append(json_str)
            # Meadows Note: The overflow valve. Forces a write when the buffer limit is breached.
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
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=True)

    def read_recent_history(self, limit=4) -> List[str]:
        if not os.path.exists(self.log_dir):
            return []
        files = sorted(glob.glob(os.path.join(self.log_dir, "trace_*.jsonl")), key=os.path.getmtime, reverse=True)
        history = deque(maxlen=limit)
        for fpath in files:
            if len(history) >= limit:
                break
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    for line in reversed(deque(f, maxlen=limit * 2)):
                        if len(history) >= limit:
                            break
                        try:
                            data = json.loads(line)
                            resp = data.get("final_response")
                            if not resp:
                                continue
                            user_text = data.get("prompt_snapshot", "").partition("User:")[2].split("\n", 1)[0].strip()
                            if not user_text:
                                user_text = "Unknown"
                            history.appendleft(f"User: {user_text} | System: {resp}")
                        except json.JSONDecodeError:
                            pass
            except IOError:
                pass
        return list(history)

    def get_last_thoughts(self, limit=3) -> List[str]:
        history = self.read_recent_history(limit)
        return [h.partition("System: ")[2].strip() for h in history if "System: " in h]

    def get_last_fatal_error(self) -> Optional[str]:
        """Navigates the graveyard of past trace files to resurrect the last critical failure."""
        files = sorted(glob.glob(os.path.join(self.log_dir, "trace_*.jsonl")), key=os.path.getmtime, reverse=True)
        for past_file in files[:5]:
            try:
                with open(past_file, "r", encoding="utf-8") as f:
                    tail_lines = reversed(deque(f, maxlen=5))
                for line in tail_lines:
                    try:
                        data = json.loads(line)
                        if "CRITICAL" in str(data.get("outcome", "")):
                            return ux_format("core_strings", "tel_prev_crash", default="Crash: {reason}",
                                             reason=data.get("reasoning", "Unknown"))
                    except json.JSONDecodeError:
                        continue
            except IOError:
                continue
        return None

    def generate_session_summary(self, _uptime: float = 0.0) -> str:
        self.flush_to_disk()
        return ux_format("core_strings", "tel_session_summary", status="DISABLED" if self.disabled else "ACTIVE",
                         count=len(self.trace_buffer), trace_file=self.current_trace_file)