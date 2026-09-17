# ruff: noqa: E741
"""core.py"""

import glob
import json
import logging
import os
import random
import threading
import time
import uuid
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from constants import Prisma, RealityLayer
from physics.models import PhysicsPacket, SharedDynamics, UserInferredState
from presets import BoneConfig
from receipts import issue as issue_receipt
from struts import safe_get, ux, ux_format

logger = logging.getLogger("bone")
if not logger.handlers:
    _sh = logging.StreamHandler()
    _sh.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_sh)
    logger.setLevel(logging.INFO)

# The one genuinely optional dependency. Everything else in the install line is
# required, and guarding a required import only relocates its failure. This is
# the single probe for the whole tree: spores.memory reads ORDVEC_AVAILABLE from
# here rather than probing again, so "is ordvec present" has one answer.
try:
    import ordvec

    ORDVEC_AVAILABLE = True
except ImportError:
    ORDVEC_AVAILABLE = False
    logger.warning(
        "ordvec is not installed. Fastscan retrieval and the Creative Determinant's "
        "subgraph pruning are unavailable; install with `pip install 'ordvec>=0.5.0'`."
    )

_LOCK_TYPES = (type(threading.Lock()), type(threading.RLock()), threading.Thread)

def _redact_secrets(obj, memo=None):
    """Walks safe standard collections to redact keys. Defers custom objects to default()."""
    if memo is None:
        memo = set()
    obj_id = id(obj)
    if obj_id in memo:
        return "<Circular Reference>"
    if isinstance(obj, dict):
        memo.add(obj_id)
        res = {}
        for k, v in obj.items():
            if isinstance(v, _LOCK_TYPES):
                continue
            if isinstance(k, str):
                k_low = k.lower()
                is_secret = any(
                    sec in k_low for sec in ("api_key", "secret", "token", "password")
                )
                is_safe = any(
                    safe in k_low
                    for safe in (
                        "max_tokens",
                        "prompt_tokens",
                        "completion_tokens",
                        "total_tokens",
                    )
                )
                if is_secret and not is_safe:
                    res[k] = "[REDACTED]"
                    continue
            res[k] = _redact_secrets(v, memo)
        memo.remove(obj_id)
        return res
    if isinstance(obj, list):
        memo.add(obj_id)
        res = [
            _redact_secrets(item, memo)
            for item in obj
            if not isinstance(item, _LOCK_TYPES)
        ]
        memo.remove(obj_id)
        return res
    if isinstance(obj, tuple):
        memo.add(obj_id)
        res = tuple(
            _redact_secrets(item, memo)
            for item in obj
            if not isinstance(item, _LOCK_TYPES)
        )
        memo.remove(obj_id)
        return res
    return obj


class JSONEncoder(json.JSONEncoder):
    def encode(self, o):
        return super().encode(_redact_secrets(o))

    def iterencode(self, o, _one_shot=False):
        return super().iterencode(_redact_secrets(o), _one_shot)

    def default(self, o):
        if isinstance(o, (set, deque)):
            return list(o)
        if hasattr(o, "to_dict") and callable(o.to_dict):
            return _redact_secrets(o.to_dict())

        if hasattr(o, "__slots__"):
            safe_dict = {}
            slots = o.__slots__
            if isinstance(slots, str):
                slots = [slots]
            for k in slots:
                try:
                    val = getattr(o, k)
                    if not isinstance(val, _LOCK_TYPES):
                        safe_dict[k] = val
                except AttributeError:
                    pass
            return _redact_secrets(safe_dict)

        if hasattr(o, "__dict__"):
            return _redact_secrets(
                {k: v for k, v in vars(o).items() if not isinstance(v, _LOCK_TYPES)}
            )

        try:
            return super().default(o)
        except TypeError:
            return f"<Unserializable: {type(o).__name__}>"

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
    kernel_hash: str = "UNKNOWN"
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
        return f"CRYSTAL [{self.decision_id}] {self.system_state} | ARCHETYPE: {self.active_archetype} | E: {e_val:.2f}"

    def crystallize(self) -> str:
        data = vars(self).copy()
        data["_summary"] = f"{self.system_state}::{self.active_archetype}"
        data["_type"] = "CRYSTAL"
        return json.dumps(data, cls=JSONEncoder)


@dataclass(slots=True)
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
    # What the Stage Manager decided this turn: which voices were in the room,
    # whether they were paired, and whether anyone got the floor at all.
    stage_verdict: Optional[Any] = None
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

    def to_dict(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in self.__slots__}


@dataclass
class MindSystem:
    mem: Any
    lex: Any
    dreamer: Any


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
        limit = max_memory or getattr(self.cfg.CORE, "EVENT_MAX_MEMORY", 1024)
        self.buffer = deque(maxlen=limit)
        self.subscribers = {}
        self.telemetry = telemetry_ref
        self._lock = threading.RLock()
        self._publishing = threading.local()

    def subscribe(self, event_type, callback):
        with self._lock:
            subs = self.subscribers.get(event_type, ())
            if callback not in subs:
                self.subscribers[event_type] = subs + (callback,)

    def unsubscribe(self, event_type: str, callback: Any):
        with self._lock:
            subs = self.subscribers.get(event_type, ())
            if callback in subs:
                if new_subs := tuple(c for c in subs if c != callback):
                    self.subscribers[event_type] = new_subs
                else:
                    del self.subscribers[event_type]

    def publish(self, event_type, data=None):
        active_events = getattr(self._publishing, "active_events", None)
        if active_events is None:
            active_events = set()
            self._publishing.active_events = active_events
        if event_type in active_events:
            return
        active_events.add(event_type)
        try:
            callbacks = self.subscribers.get(event_type, ())
            for callback in callbacks:
                try:
                    callback(data)
                except Exception as e:
                    if event_type != "EVENT_FAILURE":
                        cb_name = getattr(callback, "__name__", str(callback))
                        self.log(
                            f"Subscriber '{cb_name}' failed: {e}",
                            source="EVENT_FAILURE",
                            level="CRIT",
                        )
        finally:
            active_events.discard(event_type)

    _SEVERITY_LEVELS = {
        "CRIT": logging.CRITICAL,
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
    }

    def log(self, message: str, source: str = "SYSTEM", level: str = "INFO"):
        """Record an event. Signature is (message, source, level).

        Guard: nearly every call site passes a *source* tag second ("BIO",
        "CORTEX", "SYS"), which is correct. A number of sites historically
        passed a severity there instead, which left `level` at its "INFO"
        default and routed the line to logger.debug, below the handler
        threshold. That silently muted 25 call sites including the daemon's own
        crash handler, so a dying turn formatted a full traceback and then threw
        it away. Accept the two-argument severity spelling rather than dropping
        it on the floor.
        """
        if level == "INFO" and source in self._SEVERITY_LEVELS:
            source, level = "SYSTEM", source
        event = {
            "timestamp": time.time(),
            "source": source,
            "level": level,
            "text": message,
            "_type": "EVENT_LOG",
        }
        self.buffer.append(event)
        self.publish(source, event)
        if self.telemetry:
            self.telemetry.record_event(event)
        # Unknown levels stay at DEBUG: the TUI renders self.buffer, so routine
        # lines must not also flood stderr. Only real severities escalate.
        log_lvl = self._SEVERITY_LEVELS.get(level, logging.DEBUG)
        if log_lvl >= logging.WARNING:
            color = Prisma.RED if log_lvl >= logging.ERROR else Prisma.YEL
            logger.log(log_lvl, f"{color}[{source}] {message}{Prisma.RST}")
        else:
            logger.log(log_lvl, f"[{source}] {message}")

    def flush(self) -> List[Dict]:
        with self._lock:
            current_logs = list(self.buffer)
            self.buffer.clear()
        return current_logs


class LoreManifest:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, data_dir: Optional[str] = None, config_ref: Any = None):
        self.cfg = config_ref or BoneConfig
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.DATA_DIR: str = data_dir or os.path.join(base_dir, "lore")
        self._cache: Dict[str, Any] = {}

    @classmethod
    def get_instance(cls, config_ref=None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = LoreManifest(config_ref=config_ref)
        return cls._instance

    def get(self, category: str, sub_key: Optional[str] = None) -> Any:
        cat_key = category.lower()
        data = self._cache.get(cat_key)
        if data is None:
            with self._lock:
                data = self._cache.get(cat_key)
                if data is None:
                    data = self._load_from_disk(cat_key) or {}
                    self._cache[cat_key] = data
        if not sub_key:
            return data
        return data.get(sub_key) if isinstance(data, dict) else None

    def _load_from_disk(self, category: str) -> Optional[Dict]:
        safe_category = os.path.basename(category)
        filepath = os.path.join(self.DATA_DIR, f"{safe_category}.json")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            err_msg = f"Parse error in '{category}': {e}. Returning empty structure without modifying disk."
            logger.error(f"{Prisma.RED}{err_msg}{Prisma.RST}")
            if tel := TelemetryService.get_instance():
                tel.record_event(
                    {
                        "source": "LORE",
                        "level": "CRIT",
                        "text": err_msg,
                        "_type": "EVENT_LOG",
                    }
                )
            return None

    def inject(self, category: str, data: Any):
        cat_key = category.lower()
        with self._lock:
            target = self._cache.setdefault(cat_key, {})
            if isinstance(target, dict) and isinstance(data, dict):
                target.update(data)
            else:
                self._cache[cat_key] = data

    def save(self, category: str):
        cat_key = category.lower()
        _protected_files = {
            "system_prompts",
            "lore_manifest",
            "physics_constants",
            "driver_config",
            "lexicon",
        }
        if cat_key in _protected_files:
            logger.error(
                f"{Prisma.RED}[ARTICLE 11 VIOLATION] Blocked attempt to mutate bedrock file '{cat_key}.json'.{Prisma.RST}"
            )
            return

        if cat_key not in self._cache or self._cache[cat_key] is None:
            logger.warning(
                f"{Prisma.YEL}Refusing to save null cache for '{cat_key}'.{Prisma.RST}"
            )
            return
        filepath = os.path.join(self.DATA_DIR, f"{cat_key}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._cache[cat_key], f, indent=2, cls=JSONEncoder)
            logger.info(f"{Prisma.GRY}Persisted '{cat_key}'.{Prisma.RST}")
        except Exception as e:
            err_msg = f"Failed to save '{cat_key}': {e}"
            logger.critical(f"{Prisma.RED}{err_msg}{Prisma.RST}")
            if tel := TelemetryService.get_instance():
                tel.record_event(
                    {
                        "source": "LORE",
                        "level": "CRIT",
                        "text": err_msg,
                        "_type": "EVENT_LOG",
                    }
                )

    def flush_cache(self, category: Optional[str] = None):
        with self._lock:
            if not category:
                self._cache.clear()
                logger.info(f"{Prisma.CYN}Flushed Lore cache.{Prisma.RST}")
                return
            cat_key = category.lower()
            if self._cache.pop(cat_key, None) is not None:
                logger.info(f"{Prisma.CYN}Flushed '{cat_key}'.{Prisma.RST}")


class TheObserver:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.start_time = time.time()
        self.is_coupled = False
        core_cfg = self.cfg.CORE
        max_len = getattr(core_cfg, "OBSERVER_MAX_LEN", 20)
        self.cycle_times = deque(maxlen=max_len)
        self.llm_latencies = deque(maxlen=max_len)
        self.memory_snapshots = deque(maxlen=max_len)
        self.error_counts = Counter()
        self.user_turns = 0
        self.LATENCY_WARNING = getattr(core_cfg, "OBSERVER_LATENCY_WARN", 5.0)
        self.CYCLE_WARNING = getattr(core_cfg, "OBSERVER_CYCLE_WARN", 8.0)
        self.C_EFF = getattr(core_cfg, "OBSERVER_CYCLE_EFFICIENT", 0.1)
        self.L_EFF = getattr(core_cfg, "OBSERVER_LLM_EFFICIENT", 0.5)
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
            return (
                ux(
                    "core_strings",
                    random.choice(("obs_fog", "obs_degraded", "obs_ponderous")),
                )
                or "High Cognitive Load."
            )
        if avg_cycle > self.CYCLE_WARNING:
            return ux("core_strings", "obs_sluggish") or "System Sluggish."
        if self.is_coupled:
            return ux_format(
                "core_strings",
                "obs_coupled",
                default="Harmonic Resonance: Presence Active.",
            )
        return ux("core_strings", "obs_nominal") or "Nominal."

    @property
    def avg_cycle(self) -> float:
        return sum(self.cycle_times) / max(1, len(self.cycle_times))

    @property
    def avg_llm(self) -> float:
        return sum(self.llm_latencies) / max(1, len(self.llm_latencies))

    def get_report(self):
        c_avg, l_avg = self.avg_cycle, self.avg_llm
        return {
            "uptime_sec": int(self.uptime),
            "turns": self.user_turns,
            "avg_cycle_sec": round(c_avg, 2),
            "avg_llm_sec": round(l_avg, 2),
            "status": self.pass_judgment(c_avg, l_avg),
            "errors": dict(self.error_counts),
            "graph_size": self.memory_snapshots[-1] if self.memory_snapshots else 0,
        }


@dataclass
class SystemHealth:
    components_online: Dict[str, bool] = field(
        default_factory=lambda: {"physics": True, "bio": True, "mind": True}
    )
    errors: deque = field(default_factory=lambda: deque(maxlen=50))
    warnings: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    observer: Optional["TheObserver"] = None
    events: Optional["EventBus"] = None

    def __getattr__(self, item: str):
        if item.endswith("_online"):
            return self.components_online.get(item[:-7].lower(), True)
        raise AttributeError(f"'SystemHealth' object has no attribute '{item}'")

    def link_observer(self, observer_ref):
        self.observer = observer_ref

    def report_failure(self, component: str, error: Exception, severity="ERROR"):
        msg = str(error)
        self.errors.append(ErrorLog(component, msg, severity=severity))
        if self.observer:
            self.observer.log_error(component)
        if self.events:
            self.events.log(
                f"SystemHealth Failure [{component}]: {msg}",
                source="HEALTH",
                level=severity,
            )
        if severity in ("CRITICAL", "ERROR"):
            self.components_online[component.lower()] = False
        return ux_format("core_strings", "health_offline", component=component, msg=msg)

    def report_warning(self, message: str):
        self.warnings.append(message)

    def report_hint(self, message: str):
        self.hints.append(message)

    def reboot_component(self, component: str) -> bool:
        comp_key = component.lower()
        if not self.components_online.get(comp_key, True):
            self.components_online[comp_key] = True
            self.report_hint(
                f"{component.upper()} subsystem explicitly rebooted and brought online."
            )
            return True
        return False

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
        if layer != self._stack[-1]:
            self._stack.append(layer)
        return True

    def pop_layer(self) -> int:
        if len(self._stack) > 1:
            return self._stack.pop()
        return self._stack[0]

    def stabilize_at(self, layer: int):
        self._stack = [layer]


class InsufficientCorpus(ValueError):
    """Not enough memory to measure a regime against. Not an error, a decline.

    Named rather than bare so `regulate` can tell "the data will not support
    this measurement" apart from "the measurement broke", and report them
    differently. A bare ValueError would have collapsed both into the same
    degraded receipt, which is the distinction this codebase keeps losing.
    """


class CyberneticGovernor:
    """
    Apex N-Dimensional Topological Manifold Governor.
    Powered by natively bound AVX-512 Asymmetric Rank Transformations. Ordvec, Apache 2.0
    """

    PICARD_C = 10.0
    BETA_SCALE = 1.2
    BETA_STAR_UNIT = 0.5
    PRUNE_SIZE = 50
    PICARD_MAX_ITER = 100
    PICARD_TOL = 1e-4

    def __init__(self, config_ref=None):
        self.cfg = config_ref
        self.target_v = None
        self.target_d = None
        self.beth_index, self.order = 0.5, 1
        # None means "not measured this session yet", which is distinct from a
        # measured zero and is what the decline rule sets.
        self.last_z = None
        self.last_sharpness = 0.0
        self.last_corpus = 0
        self.last_a = 0.0
        self.last_b = 0.0
        self.last_sol = "not_measured"
        self.memory_bitmap = None
        self.memory_rq = None
        self.cached_nodes = []
        self._cached_vectorizer = self._resolve_vectorizer()

    def _resolve_vectorizer(self):
        """Abstracts the vectorization dependency at boot to avoid hot-path ROS.

        Deliberately unguarded. `struts` is first-party and universally imported,
        so an ImportError here is a real structural fault (most plausibly the
        cycle its own docstring warns about) and must not be reported downstream
        as "Vectorizer unavailable", which names a different illness entirely.
        """
        from struts import _word_to_vector

        return _word_to_vector

    def _get_vectorizer(self):
        return self._cached_vectorizer

    def _sync_ordvec_indices(self, memory_core: Any):
        """Build the ordvec indexes over the memory graph.

        Raises rather than returning False. Every reason this can fail is worth
        telling apart (an optional dependency missing, a memory with nothing in
        it yet, a dead vectorizer), and the only caller cannot act on a bare
        boolean: it goes straight on to dereference the indexes this method was
        supposed to have built.
        """
        if not ORDVEC_AVAILABLE:
            raise ValueError("ordvec is not installed; the memory manifold cannot be indexed.")
        if not memory_core or not hasattr(memory_core, "graph"):
            raise ValueError("Memory core exposes no graph to index.")
        nodes = list(memory_core.graph.keys())
        if self.cached_nodes == nodes and self.memory_rq is not None:
            return True

        vectorizer = self._get_vectorizer()
        if not vectorizer:
            raise ValueError("Vectorizer unavailable; cannot embed memory nodes.")

        matrix = []
        valid_nodes = []
        for node in nodes:
            vec = vectorizer(node)
            if vec is not None:
                matrix.append(vec)
                valid_nodes.append(node)
        if len(matrix) < 3:
            raise ValueError(
                f"Memory holds {len(matrix)} vectorizable node(s); the bitmap needs at least 3."
            )
        fp32_matrix = np.ascontiguousarray(matrix, dtype=np.float32)
        # ordvec indexes are constructed with a DIMENSION and then fed vectors.
        # This passed the matrix straight to the constructor, where `dim` is
        # expected, and asked for 8-bit quantisation, which ordvec rejects (it
        # accepts 1, 2 or 4). Both raised on every call, so the governor
        # always fell back to PID and the Creative Determinant solve on the
        # memory Laplacian had never once run.
        dim = int(fp32_matrix.shape[1])
        bitmap = ordvec.SignBitmap(dim)
        bitmap.add(fp32_matrix)
        quantizer = ordvec.RankQuant(dim, 4)
        quantizer.add(fp32_matrix)
        self.memory_bitmap = bitmap
        self.memory_rq = quantizer
        self.cached_nodes = valid_nodes
        return True

    def get_policy_shift(self) -> str:
        """CO_REGULATION when the neighbourhood clears the corpus null.

        This used to read `last_lam1 < 0`, which measured the mean ordvec
        similarity by way of a Laplacian that contributed 1.5% of the answer.
        `last_z` measures the same thing directly and says so.
        """
        pivot = self._gate_cfg("Z_PIVOT", 2.0)
        if self.order == 2 or (self.last_z is not None and self.last_z >= pivot):
            return "CO_REGULATION"
        return "EFFICIENCY"

    def regulate(
        self,
        physics,
        dt,
        goal_vector=None,
        endocrine_state=None,
        memory_core=None,
        user_text="",
    ) -> Tuple[float, float]:
        if not memory_core or not user_text:
            if memory_core or user_text:
                # Exactly one of the two arrived. That is a wiring fault at the
                # call site, not a caller who wanted a PID loop.
                issue_receipt(
                    "governor.creative_determinant",
                    "PID fallback, incomplete inputs",
                    result_count=0,
                    degraded=True,
                    inputs={
                        "memory_core": bool(memory_core),
                        "user_text": bool(user_text),
                    },
                    detail=(
                        "no utterance to score against the corpus"
                        if memory_core
                        else "no memory core to read a bitmap from"
                    ),
                )
            return self._pid_fallback(physics, dt, endocrine_state)
        try:
            return self._bitmap_regulation(
                physics, dt, memory_core, user_text, endocrine_state
            )
        except InsufficientCorpus as e:
            # navi-fractal's rule, applied to the governor: when the data will
            # not support the measurement, decline to make it rather than
            # emitting a number nobody should trust. The turn runs the default
            # temperature and the receipt says the regime was not measured.
            self.last_z = None
            self.last_sol = "not_measured"
            issue_receipt(
                "governor.bitmap_gate",
                "declined to measure the regime",
                result_count=0,
                degraded=False,
                inputs={"corpus": len(getattr(self, "cached_nodes", []) or [])},
                detail=str(e),
            )
            return self._pid_fallback(physics, dt, endocrine_state)
        except Exception as e:
            # This is the handler that hid the Creative Determinant for the
            # life of the project: it swallowed a constructor TypeError every
            # turn and served a PID loop wearing the PDE's skin. The receipt is
            # what makes that state impossible to hold silently again.
            issue_receipt(
                "governor.creative_determinant",
                "PID fallback, graph solve raised",
                result_count=0,
                degraded=True,
                inputs={"nodes_cached": len(getattr(self, "cached_nodes", []) or [])},
                detail=f"{type(e).__name__}: {e}",
            )
            logger.warning(f"{Prisma.YEL}Graph regulation failed, falling back to PID: {e}{Prisma.RST}")
            return self._pid_fallback(physics, dt, endocrine_state)

    def _gate_cfg(self, key: str, default: float) -> float:
        return float(safe_get(safe_get(self.cfg, "GATE", {}), key, default))

    @staticmethod
    def _null_z(corpus: int, top_k: int = 10) -> float:
        """What z_top10 a corpus of this size would produce from noise alone.

        Fitted against 600 draws per size over pure Gaussian corpora:
        A*sqrt(ln n) + B with A=1.8712, B=-2.2958. Residuals stay inside 0.07
        across n from 32 to 20,000, which is well under the pivot, so the fit
        is good enough to subtract and not good enough to pretend is exact.

        Only calibrated for the shipped TOP_K of 10. A different k has a
        different null, and this returns the k=10 curve regardless, so changing
        TOP_K means refitting this.
        """
        if corpus < 2:
            return 0.0
        return 1.8712 * float(np.sqrt(np.log(corpus))) - 2.2958

    def _bitmap_regulation(
        self, physics, dt, memory_core, user_text, endocrine_state
    ) -> Tuple[float, float]:
        """Read the regime off the ordvec sign bitmap, in one pass over memory.

        This replaced a graph Laplacian and a Picard iteration. The measurement
        that retired them, run on our own code with the real 768d embedder and a
        23-node subgraph seeded at 17% edge density (denser than a real
        session):

            Phi^T L Phi / Phi^T Phi : +0.006149
            b_mean                  : +0.408239
            reported lambda_1       : -0.402089
            graph share of |lambda_1|: 1.53%

        and lambda_1 came back byte-identical at voltage 15, 25, 30, 35, 45, 60
        and 90, because the voltage scalar `a` saturates at 1.0 above the gate.
        At the Picard fixed point the Laplacian energy cancels against the
        saturation term, so the reported number was -b_mean plus a residual, and
        b_mean was the mean ordvec similarity scaled by drag. The topology and
        the voltage were decoration on a scalar.

        Nelson Spence found the same thing at 207,695 nodes before we found it
        at 23: a corpus-mass scalar reproduced his Laplacian routing signal at
        Pearson 0.992 in a millisecond instead of seconds, and three scalars
        read straight off the RankQuant bitmap popcounts beat the mass scalar at
        zero added compute. The bitmap features are what survived. This is his
        recommendation, implemented.

        `z_top10` is how far the utterance's neighbourhood stands above the
        corpus null, in standard deviations of the sign-agreement distribution.
        For a 768-dim bitmap chance sits near 384 agreements with a spread near
        14, so the scale is interpretable and stable across corpora.
        """
        vectorizer = self._get_vectorizer()
        if not vectorizer:
            raise ValueError("Vectorizer unavailable; cannot read the memory bitmap.")

        voltage = float(safe_get(physics, "voltage", 30.0))
        drag = float(safe_get(physics, "narrative_drag", 0.6))
        p_cfg = getattr(self.cfg, "PHYSICS", None)
        v_max = float(getattr(p_cfg, "VOLTAGE_MAX", 100.0))
        v_floor = float(getattr(p_cfg, "VOLTAGE_FLOOR", 0.0))
        v_base = v_floor + ((v_max - v_floor) * 0.3)
        v_range = v_max - v_base

        self._sync_ordvec_indices(memory_core)
        u_vec = vectorizer(user_text)
        if u_vec is None:
            raise ValueError("Null vectorization payload.")
        u_fp32 = np.ascontiguousarray(u_vec, dtype=np.float32)

        scores = np.asarray(self.memory_bitmap.score_all(u_fp32), dtype=np.float64)
        corpus = int(scores.size)
        min_corpus = int(self._gate_cfg("MIN_CORPUS", 32))
        if corpus < min_corpus:
            raise InsufficientCorpus(
                f"{corpus} memories is too few for a mean and a deviation "
                f"(need {min_corpus}); declining to emit a regime signal."
            )
        deviation = float(scores.std())
        if deviation <= 0.0:
            raise InsufficientCorpus(
                "every memory scores identically; the corpus has no null to "
                "measure against."
            )

        top_k = max(1, min(int(self._gate_cfg("TOP_K", 10)), corpus))
        top1 = float(scores.max())
        top10 = float(np.partition(scores, -top_k)[-top_k:].mean())
        z_top10 = (top10 - float(scores.mean())) / deviation
        sharpness = top1 - top10

        # Gate on the EXCESS over the null, not on z itself.
        #
        # The top-10 mean of n samples sits further above the mean the larger n
        # gets, for no reason but order statistics. Measured on pure Gaussian
        # corpora, E[z_top10] runs 1.13 at n=32, 2.05 at n=200, 2.65 at n=1000
        # and 3.55 at n=20000. A fixed threshold on raw z would therefore be
        # permanently shut on a young memory and permanently open on a mature
        # one, and would drift open as the engine is used, which is the worst
        # possible failure for a signal meant to detect coherence.
        #
        # `z_excess` is how far this neighbourhood stands above what a corpus of
        # this size would produce from noise alone, so it is free of both the
        # scale of the scores and the size of the memory.
        z_excess = z_top10 - self._null_z(corpus, top_k)

        self.last_z_raw = float(z_top10)
        self.last_z = float(z_excess)
        self.last_sharpness = float(sharpness)
        self.last_corpus = corpus
        self.last_b = float(top10)
        self.last_sol = (
            "coherent" if z_excess >= self._gate_cfg("Z_PIVOT", 0.5) else "diffuse"
        )

        issue_receipt(
            "governor.bitmap_gate",
            "read the regime off the sign bitmap",
            result_count=corpus,
            degraded=False,
            inputs={
                "corpus": corpus,
                "z_excess": round(z_excess, 4),
                "z_top10": round(z_top10, 4),
                "z_null": round(self._null_z(corpus, top_k), 4),
                "sharpness": round(sharpness, 2),
                "top1": round(top1, 1),
                "mean": round(float(scores.mean()), 1),
                "std": round(deviation, 2),
            },
            detail=f"regime={self.last_sol} temperature={self.gate_temperature():.3f}",
        )

        # z drives how much presence the memory field has, so it sets the
        # voltage target. Sharpness says how peaked that neighbourhood is, so a
        # sharp one is focused and wants less drag. These two mappings are ours,
        # not Nelson's; he specified the regime signal and the temperature.
        pivot = self._gate_cfg("Z_PIVOT", 0.5)
        presence = float(np.clip(z_excess / max(1e-6, pivot * 2.0), 0.0, 1.0))
        focus = float(np.clip(sharpness / max(1e-6, deviation * 3.0), 0.0, 1.0))
        self.target_v = v_base + presence * v_range
        self.target_d = float(np.clip(1.0 - focus, 0.1, 1.0))

        stress_mod = 1.0
        if endocrine_state:
            glimmers = float(getattr(endocrine_state, "glimmers", 0))
            stress_mod = 1.5 if glimmers >= 1 else 0.75

        adjusted_dt = dt * 0.5 * stress_mod
        return (self.target_v - voltage) * adjusted_dt, (
            self.target_d - drag
        ) * adjusted_dt

    def gate_temperature(self) -> float:
        """Sampling temperature from the regime signal.

        Below the pivot the neighbourhood is indistinguishable from the corpus
        null, so there is nothing coherent nearby and generation collapses to
        deterministic logic. That is the decision the eigenvalue's sign used to
        make, preserved; only its input changed.
        """
        pivot = self._gate_cfg("Z_PIVOT", 2.0)
        if self.last_z is None or self.last_z < pivot:
            return float(self._gate_cfg("T_LOCKED", 0.0))
        heat = self._gate_cfg("T_OPEN_BASE", 0.7) + self._gate_cfg(
            "T_GAIN", 0.15
        ) * (self.last_z - pivot)
        return float(min(self._gate_cfg("T_MAX", 1.2), heat))

    def _pid_fallback(
        self, physics: Dict[str, Any], dt: float, endocrine_state: Any = None
    ) -> Tuple[float, float]:
        active_tv = self.target_v if self.target_v is not None else 30.0
        active_td = self.target_d if self.target_d is not None else 0.6
        current_v = float(safe_get(physics, "voltage", active_tv))
        current_d = float(safe_get(physics, "narrative_drag", active_td))
        stress_mod = (
            1.0
            if endocrine_state is None
            else (1.5 if float(getattr(endocrine_state, "glimmers", 0)) >= 1 else 0.75)
        )
        adjusted_dt = dt * 0.5 * stress_mod
        return (active_tv - current_v) * adjusted_dt, (
            active_td - current_d
        ) * adjusted_dt

    def recalibrate(self, target_voltage: float, target_drag: float):
        self.target_v = float(target_voltage)
        self.target_d = float(target_drag)

    def calculate_coupling(
        self, phi: float, resonance_delta: float, user_exhaustion: float
    ) -> float:
        if user_exhaustion > 0.8:
            self.order = 2
        else:
            self.order = 1
        self.beth_index = float(
            min(1.0, max(0.0, (phi + resonance_delta + user_exhaustion) / 3.0))
        )
        return self.beth_index


class ArchetypeArbiter:
    @staticmethod
    def arbitrate(
        physics_lens: str,
        soul_archetype: str,
        council_mandates: List[Dict],
        trigram: Any = None,
    ) -> Tuple[str, str, str]:
        mandate_types = set()
        for m in council_mandates or []:
            val = m.get("type", m.get("action"))
            if isinstance(val, list):
                mandate_types.update(val)
            elif val is not None:
                mandate_types.add(val)
        if "LOCKDOWN" in mandate_types:
            return (
                "THE CENSOR",
                "COUNCIL",
                ux("core_strings", "arb_martial_law") or "Martial Law.",
            )
        if "FORCE_MODE" in mandate_types:
            return (
                "THE MACHINE",
                "COUNCIL",
                ux("core_strings", "arb_bureaucratic")
                or "[COUNCIL]: Bureaucratic Override active.",
            )
        if soul_archetype and "/" in soul_archetype:
            return (
                soul_archetype,
                "SOUL",
                ux_format(
                    "core_strings",
                    "arb_diamond",
                    soul_archetype=soul_archetype,
                    default=f"Gestalt Resonance: {soul_archetype}",
                ),
            )
        manifest = LoreManifest.get_instance()
        tri_name = (
            trigram.get("name")
            if isinstance(trigram, dict)
            else str(trigram)
            if trigram
            else None
        )
        if tri_name and (
            meta_resonance := manifest.get("NARRATIVE_DATA", "_META_RESONANCE_")
        ):
            for r in meta_resonance:
                if (
                    r.get("trigram") == tri_name
                    and r.get("lens", physics_lens) == physics_lens
                    and r.get("soul", soul_archetype) == soul_archetype
                ):
                    return (
                        r["result"],
                        r.get("source", "COSMIC"),
                        r.get("msg")
                        or ux("core_strings", "arb_resonance")
                        or "Cosmic Resonance.",
                    )
        if physics_lens in (
            manifest.get("COUNCIL_DATA", "LOUD_LENSES") or ("THE MANIC", "THE VOID")
        ):
            return (
                physics_lens,
                "PHYSICS",
                ux_format(
                    "core_strings",
                    "arb_loud",
                    physics_lens=physics_lens,
                    default=f"Physics Override: {physics_lens}",
                ),
            )
        return (
            soul_archetype,
            "SOUL",
            ux("core_strings", "arb_soul") or "The soul speaks.",
        )


class TelemetryService:
    _tracer_instance = None
    _cls_lock = threading.Lock()

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        core_cfg = self.cfg.CORE
        self.log_dir = getattr(core_cfg, "TELEMETRY_LOG_DIR", "logs/telemetry")
        self.BUFFER_SIZE = getattr(core_cfg, "TELEMETRY_BUFFER_SIZE", 50)
        self.MAX_ERRORS = getattr(core_cfg, "TELEMETRY_MAX_ERRORS", 5)
        self.write_buffer: List[str] = []
        self.active_crystal = None
        self.kernel_hash = "UNKNOWN"
        self.disabled = False
        self.crystals_logged = 0
        self._lock = threading.Lock()
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            self.current_trace_file = os.path.join(
                self.log_dir, f"trace_{int(time.time())}.jsonl"
            )
            self._executor = ThreadPoolExecutor(
                max_workers=1, thread_name_prefix="BoneTelemetry"
            )
        except OSError as e:
            msg = (
                ux("core_strings", "tel_disk_denied")
                or "Disk access denied for Telemetry."
            )
            logger.warning(
                f"{Prisma.OCHRE}[GRACEFUL DEGRADATION] {msg} - {e}. Telemetry offline.{Prisma.RST}"
            )
            self.disabled = True
            self.current_trace_file = None
            self._executor = None

    def record_event(self, event_dict: dict):
        if self.disabled or not self.current_trace_file:
            return
        try:
            payload = {**event_dict, "kernel_hash": self.kernel_hash}
            self._buffer_line(json.dumps(payload, cls=JSONEncoder))
        except (TypeError, ValueError) as e:
            logger.warning(
                f"{Prisma.YEL}Oops! We dropped an un-serializable event: {e}{Prisma.RST}"
            )

    @classmethod
    def get_instance(cls, config_ref=None):
        if cls._tracer_instance is None:
            with cls._cls_lock:
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
        self.active_crystal = DecisionCrystal(
            decision_id=trace_id, kernel_hash=self.kernel_hash
        )

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
        if self.disabled:
            return
        with self._lock:
            self.write_buffer.append(json_str)
            if len(self.write_buffer) >= self.BUFFER_SIZE:
                self.flush_to_disk_locked()

    def flush_to_disk_locked(self):
        if self.disabled or not self.current_trace_file or not self.write_buffer:
            return
        lines, self.write_buffer = self.write_buffer, []
        self._executor.submit(TelemetryService._bg_write, lines, self.current_trace_file)

    def flush_to_disk(self):
        with self._lock:
            self.flush_to_disk_locked()

    @staticmethod
    def _bg_write(lines: List[str], filepath: str):
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except IOError as e:
            logger.error(
                f"{Prisma.RED}[TELEMETRY DECAY] Background write failed: {e}{Prisma.RST}"
            )

    def shutdown(self):
        self.flush_to_disk()
        self.disabled = True
        if self._executor is not None:
            self._executor.shutdown(wait=True)

    def _tail_file(self, filepath: str, n: int = 20) -> List[str]:
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return list(deque(f, maxlen=n))
        except IOError as e:
            logger.warning(
                f"Telemetry trace {filepath} could not be read: {type(e).__name__}: {e}. "
                "/diag will show no history, which is not the same as no history."
            )
            return []

    def _yield_historical_records(self, file_limit=5, lines_per_file=10):
        files = sorted(
            glob.glob(os.path.join(self.log_dir, "trace_*.jsonl")), reverse=True
        )
        malformed = 0
        for fpath in files[:file_limit]:
            try:
                tail_lines = reversed(self._tail_file(fpath, n=lines_per_file))
                for line in tail_lines:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        malformed += 1
                        continue
            except IOError as e:
                logger.warning(
                    f"Skipping unreadable telemetry trace {fpath}: {type(e).__name__}: {e}"
                )
                continue
        if malformed:
            logger.warning(
                f"Skipped {malformed} malformed telemetry record(s) while reading history."
            )

    def read_recent_history(self, limit=4) -> List[str]:
        history = deque(maxlen=limit)
        for data in self._yield_historical_records(lines_per_file=limit * 2):
            if len(history) >= limit:
                break
            resp = data.get("final_response")
            if not resp:
                continue
            raw_prompt = data.get("prompt_snapshot") or ""
            user_text = (
                raw_prompt.partition("User:")[2].split("\n", 1)[0].strip() or "Unknown"
            )
            history.appendleft(f"User: {user_text} | System: {resp}")
        return list(history)

    def get_last_thoughts(self, limit=3) -> List[str]:
        history = self.read_recent_history(limit)
        return [h.partition("System: ")[2].strip() for h in history if "System: " in h]

    def get_last_fatal_error(self) -> Optional[str]:
        for data in self._yield_historical_records(file_limit=5, lines_per_file=50):
            outcome = data.get("outcome")
            if outcome and "CRITICAL" in str(outcome):
                return ux_format(
                    "core_strings",
                    "tel_prev_crash",
                    default="Crash: {reason}",
                    reason=data.get("reasoning", "Unknown"),
                )
        return None

    def generate_session_summary(self) -> str:
        self.flush_to_disk()
        return ux_format(
            "core_strings",
            "tel_session_summary",
            status="DISABLED" if self.disabled else "ACTIVE",
            count=self.crystals_logged,
            trace_file=self.current_trace_file,
        )
