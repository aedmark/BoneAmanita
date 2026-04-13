"""bone_core.py"""

import glob, json, os, random, time, traceback, threading
from collections import deque, Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Deque
from bone_presets import BoneConfig
from bone_types import Prisma, RealityLayer, ErrorLog, DecisionTrace, DecisionCrystal

def ux(section: str, key: str, default: Any = "") -> Any:
    data = LoreManifest.get_instance().get("ux_strings", section)
    return data.get(key, default) if isinstance(data, dict) else default

def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    return default if obj is None else (obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default))

def strict_get(obj: Any, key: str, default: Any = None) -> Any:
    """Prevents silent zombie states on load-bearing keys."""
    if obj is None:
        print(f"{Prisma.RED}[STRUCTURAL WARNING] Zombie State Averted: Tried to access '{key}' on NoneType.{Prisma.RST}")
        return default
    val = safe_get(obj, key)
    if val is None:
        print(f"{Prisma.RED}[STRUCTURAL WARNING] Missing load-bearing key: '{key}'. Defaulting to {default}.{Prisma.RST}")
        return default
    return val

def safe_set(obj: Any, key: str, value: Any) -> None:
    if obj is None:
        return
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)

class BoneJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (set, deque)):
            return list(obj)
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)

class EventBus:
    def __init__(self, max_memory=None, config_ref=None, telemetry_ref=None):
        self.cfg = config_ref or BoneConfig
        limit = (max_memory
            if max_memory
            else (getattr(self.cfg.CORE, "EVENT_MAX_MEMORY", 1024)))
        self.buffer = deque(maxlen=limit)
        self.subscribers = {}
        self.telemetry = telemetry_ref
    def subscribe(self, event_type, callback):
        subs = self.subscribers.setdefault(event_type, [])
        if callback not in subs:
            subs.append(callback)
    def publish(self, event_type, data=None):
        if event_type not in self.subscribers:
            return
        for callback in self.subscribers[event_type][:]:
            try:
                callback(data)
            except Exception as e:
                cb_name = getattr(callback, "__name__", str(callback))
                full_trace = traceback.format_exc()
                short_err = f"Error in '{cb_name}': {e}"
                raw_err = f"{short_err}\n{full_trace}"
                msg = ux("core_strings", "bus_error")
                if msg:
                    print(f"{Prisma.RED}{msg.format(error_msg=short_err)}{Prisma.RST}")
                if event_type != "EVENT_FAILURE":
                    self.log(f"EVENT_FAILURE: {raw_err}", source="EVENT_FAILURE", level="CRIT")
                try:
                    self.subscribers[event_type].remove(callback)
                    print(f"{Prisma.RED}[IMMUNE] Apoptotic pruning applied to toxic callback: {cb_name}{Prisma.RST}")
                except ValueError:
                    pass
    def log(self, message: str, source: str = "SYSTEM", level: str = "INFO"):
        event = {"timestamp": time.time(), "source": source, "level": level, "message": message, "text": message,
                 "_type": "EVENT_LOG"}
        self.buffer.append(event)
        self.publish(source, event)
        if self.telemetry:
            self.telemetry.record_event(event)
        else:
            print(f"[{source}] {message}")
    def flush(self) -> List[Dict]:
        current_logs = list(self.buffer)
        self.buffer.clear()
        return current_logs
    def get_recent_logs(self, count=10):
        return list(self.buffer)[-count:]

class LoreManifest:
    _instance = None
    def __init__(self, data_dir=None, config_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg_core = getattr(self.cfg, "CORE", None)
        default_dir = safe_get(cfg_core, "LORE_DIR", "lore")
        self.DATA_DIR = data_dir or default_dir
        self._cache = {}
    @classmethod
    def get_instance(cls, config_ref=None):
        if cls._instance is None:
            cls._instance = LoreManifest(config_ref=config_ref)
        return cls._instance
    def get(self, category: str, sub_key: str = None) -> Any:
        cat_key = category.lower()
        data = self._cache.setdefault(cat_key, self._load_from_disk(cat_key) or {})
        if not sub_key:
            return data
        return data.get(sub_key) if isinstance(data, dict) else None
    def _load_from_disk(self, category: str) -> Optional[Dict]:
        filename = f"{category}.json"
        filepath = os.path.join(self.DATA_DIR, filename)
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
        cat_key = category.lower()
        target = self._cache.setdefault(cat_key, {})
        if isinstance(target, dict) and isinstance(data, dict):
            target.update(data)
        else:
            self._cache[cat_key] = data
    def flush_cache(self, category: str = None):
        if category:
            cat_key = category.lower()
            if self._cache.pop(cat_key, None) is not None:
                print(f"{Prisma.CYN}[LORE]: Flushed '{cat_key}'.{Prisma.RST}")
            else:
                print(f"{Prisma.GRY}[LORE]: Category '{cat_key}' not in cache.{Prisma.RST}")
        else:
            self._cache.clear()
            print(f"{Prisma.CYN}[LORE]: Flushed Lore cache.{Prisma.RST}")

class TheObserver:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.cyber_gov = CyberneticGovernor(config_ref=self.cfg)
        self.start_time = time.time()
        cfg_core = getattr(self.cfg, "CORE", None)
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
    def calculate_efficiency(self, health: float, stamina: float) -> float:
        duration = max(0.01, self.last_cycle_duration)
        resource_sum = health + stamina
        return min(999.0, resource_sum / duration)
    def log_error(self, module_name):
        self.error_counts[module_name] += 1
    def record_memory(self, node_count):
        self.memory_snapshots.append(node_count)
    def pass_judgment(self, avg_cycle, avg_llm):
        if avg_cycle == 0.0 and avg_llm == 0.0:
            return ux("core_strings", "obs_asleep")
        if avg_cycle < self.C_EFF and avg_llm < self.L_EFF:
            return ux("core_strings", "obs_efficient")
        if avg_llm > self.LATENCY_WARNING:
            valid = [s for k in ("obs_fog", "obs_degraded", "obs_ponderous") if (s := ux("core_strings", k))]
            return random.choice(valid) if valid else ""
        if avg_cycle > self.CYCLE_WARNING:
            return ux("core_strings", "obs_sluggish")
        if self.cyber_gov.order == 2:
            return ux("core_strings", "obs_coupled") or "Harmonic Resonance: Presence Active."
        return ux("core_strings", "obs_nominal")
    def get_report(self):
        avg_cycle = sum(self.cycle_times) / max(1, len(self.cycle_times))
        avg_llm = sum(self.llm_latencies) / max(1, len(self.llm_latencies))
        uptime = time.time() - self.start_time
        status_msg = self.pass_judgment(avg_cycle, avg_llm)
        return {"uptime_sec": int(uptime),
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
        else:
            self.report_warning(
                f"Unmapped component '{component}' reported a failure. Missing from SystemHealth dataclass.")
        err_msg = ux("core_strings", "health_offline")
        return err_msg.format(component=component, msg=msg) if err_msg else ""
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
        depth = self.current_depth
        return {
            "allow_narrative": depth in (RealityLayer.SIMULATION, RealityLayer.DEEP_CX, RealityLayer.DEBUG),
            "allow_commands": depth >= RealityLayer.SIMULATION,
            "allow_meta": depth >= RealityLayer.DEBUG,
            "raw_output": depth == RealityLayer.DEEP_CX,
            "system_override": depth == RealityLayer.DEBUG
        }

class CyberneticGovernor:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.beth_index: float = 0.5
        self.order: int = 1
    def calculate_coupling(self, phi: float, resonance_delta: float, user_exhaustion: float) -> float:
        coherence_debt = (user_exhaustion ** 1.5) * (1.0 - phi)
        self.beth_index = max(0.0, min(1.0, (phi * 0.6) + (user_exhaustion * 0.4) + (coherence_debt * 0.3)))
        if self.beth_index >= 0.75 or (resonance_delta > 0.3 and user_exhaustion > 0.5):
            self.order = 2
        else:
            self.order = 1
        return self.beth_index
    def get_policy_shift(self) -> str:
        if self.order == 2:
            return "CO_REGULATION"
        return "EFFICIENCY"

class ArchetypeArbiter:
    @staticmethod
    def arbitrate(physics_lens: str, soul_archetype: str, council_mandates: List[Dict], trigram: Dict = None,
                  config_ref=None, ) -> Tuple[str, str, str]:
        target_cfg = config_ref or BoneConfig
        for mandate in council_mandates or ():
            if mandate.get("type") == "LOCKDOWN":
                return "THE CENSOR", "COUNCIL", ux("core_strings", "arb_martial_law")
            if mandate.get("type") == "FORCE_MODE":
                return "THE MACHINE", "COUNCIL", ux("core_strings", "arb_bureaucratic")
        if soul_archetype and "/" in soul_archetype:
            msg = ux("core_strings", "arb_diamond")
            return soul_archetype, "SOUL", msg.format(soul_archetype=soul_archetype) if msg else ""
        if trigram:
            t_name = trigram.get("name")
            rules = LoreManifest.get_instance().get("NARRATIVE_DATA", "_META_RESONANCE_") or []
            for r in rules:
                if r.get("trigram") == t_name and (not r.get("lens") or r.get("lens") == physics_lens) and (not r.get("soul") or r.get("soul") == soul_archetype):
                    msg = r.get("msg") or ux("core_strings", "arb_resonance")
                    return r["result"], r.get("source", "COSMIC"), msg
        cfg_core = getattr(target_cfg, "CORE", None)
        loud_lenses = safe_get(cfg_core, "LOUD_LENSES", ("THE MANIC", "THE VOID"))
        if physics_lens in loud_lenses:
            msg = ux("core_strings", "arb_loud")
            return physics_lens, "PHYSICS", msg.format(physics_lens=physics_lens) if msg else ""
        return soul_archetype, "SOUL", ux("core_strings", "arb_soul")

class TelemetryService:
    _tracer_instance = None
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg_core = getattr(self.cfg, "CORE", None)
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
            msg = ux("core_strings", "tel_disk_denied") or "Disk access denied for Telemetry."
            print(f"{Prisma.RED}[APOPTOSIS] {msg} - {e}{Prisma.RST}")
            raise RuntimeError(f"Strict Apoptosis: Telemetry blindness detected. The system refuses to boot without nociception. {e}")
        self._executor = ThreadPoolExecutor(max_workers=1)
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
        trace = DecisionTrace(trace_id=self.active_crystal.decision_id,
            timestamp=time.time(),
            component=component,
            decision_type=decision_type,
            inputs=inputs if isinstance(inputs, dict) else {"raw": str(inputs)},
            reasoning=reasoning,
            outcome=outcome)
        self.trace_buffer.append(trace)
        self._buffer_line(trace.to_json())
    def log_crystal(self, crystal: DecisionCrystal):
        if self.disabled:
            return
        self._buffer_line(crystal.crystallize())
    def start_phase(self, phase_name: str, _context: Any):
        msg = ux("core_strings", "tel_phase_start")
        self.log_decision(phase_name, "PHASE_START", {"timestamp": time.time()}, msg, "RUNNING", )
    def end_phase(self, phase_name: str, _ctx_before: Any, _ctx_after: Any):
        msg = ux("core_strings", "tel_phase_end")
        self.log_decision(phase_name, "PHASE_END", {"timestamp": time.time()}, msg, "SUCCESS", )
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
        lines_to_write = list(self.write_buffer)
        self.write_buffer.clear()
        self._executor.submit(self._bg_write, lines_to_write, self.current_trace_file)
    def flush_to_disk(self):
        if not hasattr(self, "_lock"):
            return
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
        pattern = os.path.join(self.log_dir, "trace_*.jsonl")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        history = deque(maxlen=limit)
        for fpath in files:
            if len(history) >= limit:
                break
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    lines = deque(f, maxlen=limit * 2)
                    for line in reversed(lines):
                        if len(history) >= limit:
                            break
                        try:
                            data = json.loads(line)
                            resp = data.get("final_response")
                            if not resp:
                                continue
                            prompt_snap = data.get("prompt_snapshot", "")
                            user_text = "Unknown"
                            if "User:" in prompt_snap:
                                _, _, after_user = prompt_snap.partition("User:")
                                user_text = after_user.split("\n", 1)[0].strip()
                            history.appendleft(f"User: {user_text} | System: {resp}")
                        except (json.JSONDecodeError, IndexError):
                            continue
            except IOError:
                continue
        return list(history)
    def get_last_thoughts(self, limit=3) -> List[str]:
        history = self.read_recent_history(limit)
        return [h.partition("System: ")[2].strip() for h in history if "System: " in h]
    def get_last_fatal_error(self) -> Optional[str]:
        files = sorted(glob.glob(os.path.join(self.log_dir, "trace_*.jsonl")), key=os.path.getmtime, reverse=True)
        for past_file in files[1:5]:
            try:
                with open(past_file, "r", encoding="utf-8") as f:
                    last_line = json.loads(deque(f, maxlen=1)[0])
                if "CRITICAL" in str(last_line.get("outcome", "")):
                    msg = ux("core_strings", "tel_prev_crash") or "Crash: {reason}"
                    return msg.format(reason=last_line.get("reasoning", "Unknown"))
            except Exception:
                continue
        return None
    def generate_session_summary(self, _uptime: float = 0.0) -> str:
        self.flush_to_disk()
        count = len(self.trace_buffer)
        status = "DISABLED" if self.disabled else "ACTIVE"
        msg = ux("core_strings", "tel_session_summary")
        return (msg.format(status=status, count=count, trace_file=self.current_trace_file)
            if msg
            else "")