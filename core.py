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
from struts import safe_get, ux, ux_format

try:
    import ordvec
    ORDVEC_AVAILABLE = True
except ImportError:
    ORDVEC_AVAILABLE = False

logger = logging.getLogger("bone")
if not logger.handlers:
    _sh = logging.StreamHandler()
    _sh.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_sh)
    logger.setLevel(logging.INFO)

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

    def log(self, message: str, source: str = "SYSTEM", level: str = "INFO"):
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
        log_lvl = {
            "CRIT": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARN": logging.WARNING,
        }.get(level, logging.DEBUG)
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
        self.last_lam1 = 0.0
        self.last_a = 0.0
        self.last_b = 0.0
        self.last_sol = "trivial"
        self.memory_bitmap = None
        self.memory_rq = None
        self.cached_nodes = []
        self._cached_vectorizer = self._resolve_vectorizer()

    def _resolve_vectorizer(self):
        """Abstracts the vectorization dependency at boot to avoid hot-path ROS."""
        try:
            from struts import _word_to_vector
            return _word_to_vector
        except ImportError:
            return None

    def _get_vectorizer(self):
        return self._cached_vectorizer

    def _sync_ordvec_indices(self, memory_core: Any):
        if not ORDVEC_AVAILABLE or not memory_core or not hasattr(memory_core, "graph"):
            return False
        nodes = list(memory_core.graph.keys())
        if self.cached_nodes == nodes and self.memory_rq is not None:
            return True

        vectorizer = self._get_vectorizer()
        if not vectorizer:
            return False

        matrix = []
        valid_nodes = []
        for node in nodes:
            vec = vectorizer(node)
            if vec is not None:
                matrix.append(vec)
                valid_nodes.append(node)
        if len(matrix) < 3:
            return False
        fp32_matrix = np.ascontiguousarray(matrix, dtype=np.float32)
        self.memory_bitmap = ordvec.SignBitmap(fp32_matrix)
        self.memory_rq = ordvec.RankQuantIndex(fp32_matrix, bits=8)
        self.cached_nodes = valid_nodes
        return True

    def _solve_nd_picard(
        self,
        L: np.ndarray,
        a: float,
        beta_b: np.ndarray,
        c=10.0,
        max_iter=100,
        tol=1e-4,
    ) -> Tuple[np.ndarray, bool]:
        N = L.shape[0]
        b_mean = np.mean(beta_b)
        phi_init = np.sqrt(max(0.01, a) / (b_mean + 1e-8)) if a > 0 else 0.1
        Phi = np.ones(N) * phi_init
        I = np.eye(N)
        A = L + c * I
        try:
            A_inv = np.linalg.inv(A)
        except np.linalg.LinAlgError:
            A_inv = np.linalg.pinv(A)
        converged = False
        for _ in range(max_iter):
            rhs = (c + a) * Phi - beta_b * (np.abs(Phi) * Phi)
            Phi_new = A_inv @ rhs
            if np.linalg.norm(Phi_new - Phi) < tol:
                converged = True
                Phi = Phi_new
                break
            Phi = Phi_new
        return Phi, converged

    def get_policy_shift(self) -> str:
        if self.order == 2 or self.last_lam1 < 0 or self.last_sol == "nontrivial":
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
            return self._pid_fallback(physics, dt, endocrine_state)
        try:
            return self._graph_regulation(
                physics, dt, memory_core, user_text, endocrine_state
            )
        except Exception as e:
            logger.warning(f"{Prisma.YEL}Graph regulation failed, falling back to PID: {e}{Prisma.RST}")
            return self._pid_fallback(physics, dt, endocrine_state)

    def _graph_regulation(
        self, physics, dt, memory_core, user_text, endocrine_state
    ) -> Tuple[float, float]:
        vectorizer = self._get_vectorizer()
        if not vectorizer:
            raise ValueError("S.L.A.S.H. Intercept: Vectorizer unavailable. Aborting graph regulation to preserve structural tensegrity.")

        voltage = float(safe_get(physics, "voltage", 30.0))
        drag = float(safe_get(physics, "narrative_drag", 0.6))
        p_cfg = getattr(self.cfg, "PHYSICS", None)
        v_max = float(getattr(p_cfg, "VOLTAGE_MAX", 100.0))
        v_floor = float(getattr(p_cfg, "VOLTAGE_FLOOR", 0.0))
        v_base = v_floor + ((v_max - v_floor) * 0.3)
        v_range = v_max - v_base
        a_scalar = float(
            np.clip((voltage - v_base) / v_range, 0.0, 1.0) if v_range > 0 else 0.0
        )

        self._sync_ordvec_indices(memory_core)
        u_vec = vectorizer(user_text)
        if u_vec is None:
            raise ValueError("Null vectorization payload.")
        u_fp32 = np.ascontiguousarray(u_vec, dtype=np.float32)
        candidate_ids = self.memory_bitmap.top_m_candidates(u_fp32, m=self.PRUNE_SIZE)
        scores, global_ids = self.memory_rq.search_asymmetric_subset(
            u_fp32, candidate_ids, k=self.PRUNE_SIZE
        )
        subset_nodes = [self.cached_nodes[i] for i in global_ids]
        if len(subset_nodes) < 3:
            raise ValueError("Insufficient subgraph density for Laplacian bounds.")

        N_dim = len(subset_nodes)
        node_indices = {str(node): i for i, node in enumerate(subset_nodes)}
        W = np.zeros((N_dim, N_dim))
        for i, node in enumerate(subset_nodes):
            edges = memory_core.graph[node].get("edges", {})
            for target, weight in edges.items():
                if target in node_indices:
                    W[i, node_indices[target]] = weight
        W = np.maximum(W, W.T)
        L_matrix = np.diag(np.sum(W, axis=1)) - W
        b_field = np.maximum(0.01, scores)
        beta_b = self.BETA_SCALE * self.BETA_STAR_UNIT * b_field * (1.0 + drag)

        Phi, converged = self._solve_nd_picard(
            L_matrix,
            a_scalar,
            beta_b,
            c=self.PICARD_C,
            max_iter=self.PICARD_MAX_ITER,
            tol=self.PICARD_TOL,
        )
        if not converged:
            raise ValueError("Picard algorithm failed to converge.")

        b_mean = float(np.mean(beta_b))
        phi_norm_sq = np.dot(Phi, Phi) + 1e-8
        self.last_lam1 = float((Phi.T @ L_matrix @ Phi) / phi_norm_sq) - b_mean
        self.last_b = b_mean
        self.last_a = a_scalar
        self.last_sol = "nontrivial" if b_mean > 0.1 else "trivial"
        phi_mean = float(np.mean(np.abs(Phi)))
        phi_std = float(np.std(np.abs(Phi)))
        self.target_v = v_base + phi_mean * v_range
        self.target_d = float(np.clip(phi_std * 2.0, 0.1, 1.0))
        stress_mod = 1.0
        if endocrine_state:
            glimmers = float(getattr(endocrine_state, "glimmers", 0))
            stress_mod = 1.5 if glimmers >= 1 else 0.75

        adjusted_dt = dt * 0.5 * stress_mod
        return (self.target_v - voltage) * adjusted_dt, (
            self.target_d - drag
        ) * adjusted_dt

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
        except IOError:
            return []

    def _yield_historical_records(self, file_limit=5, lines_per_file=10):
        files = sorted(
            glob.glob(os.path.join(self.log_dir, "trace_*.jsonl")), reverse=True
        )
        for fpath in files[:file_limit]:
            try:
                tail_lines = reversed(self._tail_file(fpath, n=lines_per_file))
                for line in tail_lines:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError as _:
                        continue
            except IOError:
                continue

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
