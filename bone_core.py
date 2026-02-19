import json, os, time, random, glob, traceback
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Counter, Tuple, Deque
from bone_types import Prisma, RealityLayer, ErrorLog, DecisionTrace, DecisionCrystal


class BoneJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, deque):
            return list(obj)
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


class EventBus:
    def __init__(self, max_memory=1024):
        self.buffer = deque(maxlen=max_memory)
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type, data=None, _priority=False):
        if event_type not in self.subscribers:
            return
        for callback in list(self.subscribers[event_type]):
            try:
                callback(data)
            except Exception as e:
                cb_name = getattr(callback, "__name__", str(callback))
                print(
                    f"{Prisma.RED}[BUS]: Error in '{cb_name}' for '{event_type}': {e}{Prisma.RST}"
                )
                traceback.print_exc()

    def log(self, text: str, category: str = "SYSTEM"):
        entry = {"text": text, "category": category, "timestamp": time.time()}
        self.buffer.append(entry)

    def flush(self) -> List[Dict]:
        current_logs = list(self.buffer)
        self.buffer.clear()
        return current_logs

    def get_recent_logs(self, count=10):
        return list(self.buffer)[-count:]


class LoreManifest:
    DATA_DIR = "lore"
    _instance = None

    def __init__(self, data_dir=None):
        self.DATA_DIR = data_dir or self.DATA_DIR
        self._cache = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = LoreManifest()
        return cls._instance

    def get(self, category: str, sub_key: str = None) -> Any:
        if category in self._cache:
            data = self._cache[category]
        else:
            data = self._load_from_disk(category)
            self._cache[category] = data if data is not None else {}
            data = self._cache[category]
        if sub_key and isinstance(data, dict):
            return data.get(sub_key, None)
        return data

    def _load_from_disk(self, category: str) -> Optional[Dict]:
        filename = f"{category.lower()}.json"
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
        if category not in self._cache:
            self._cache[category] = {}
        if isinstance(self._cache[category], dict) and isinstance(data, dict):
            self._cache[category].update(data)
        else:
            self._cache[category] = data

    def flush_cache(self, category: str = None):
        if category:
            if category in self._cache:
                del self._cache[category]
            print(f"{Prisma.CYN}[LORE]: Flushed '{category}'.{Prisma.RST}")
        else:
            self._cache = {}
            print(f"{Prisma.CYN}[LORE]: Flushed Lore cache.{Prisma.RST}")


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
        self.last_cycle_duration = 0.0

    @staticmethod
    def clock_in():
        return time.time()

    def clock_out(self, start_time, metric_type="cycle"):
        duration = time.time() - start_time
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
        return resource_sum / duration

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
                "PONDEROUS (Is the LLM on a coffee break?)",
            ]
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
            "graph_size": self.memory_snapshots[-1] if self.memory_snapshots else 0,
        }


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
        if component == "PHYSICS":
            self.physics_online = False
        elif component == "BIO":
            self.bio_online = False
        elif component == "MIND":
            self.mind_online = False
        elif component == "CORTEX":
            self.cortex_online = False
        return f"[{component} OFFLINE]: {msg}"

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
        self._lock = False

    @property
    def current_depth(self) -> int:
        return self._stack[-1]

    def push_layer(self, layer: int, _context: Any = None) -> bool:
        if layer == RealityLayer.DEBUG or layer == self.current_depth + 1:
            self._stack.append(layer)
            return True
        return False

    def pop_layer(self) -> int:
        if self._lock:
            return self.current_depth
        if len(self._stack) > 1:
            return self._stack.pop()
        return self._stack[0]

    def stabilize_at(self, layer: int):
        self._stack = [layer]

    def get_grammar_rules(self) -> Dict[str, bool]:
        depth = self.current_depth
        return {
            "allow_narrative": depth
            in [RealityLayer.SIMULATION, RealityLayer.DEEP_CX, RealityLayer.DEBUG],
            "allow_commands": depth >= RealityLayer.SIMULATION,
            "allow_meta": depth >= RealityLayer.DEBUG,
            "raw_output": depth == RealityLayer.DEEP_CX,
            "system_override": depth == RealityLayer.DEBUG,
        }


class ArchetypeArbiter:
    @staticmethod
    def arbitrate(
            physics_lens: str,
        soul_archetype: str,
        council_mandates: List[Dict],
        trigram: Dict = None,
    ) -> Tuple[str, str, str]:
        for mandate in council_mandates:
            if mandate.get("type") == "LOCKDOWN":
                return (
                    "THE CENSOR",
                    "COUNCIL",
                    "Martial Law declared. Identity suppressed.",
                )
            if mandate.get("type") == "FORCE_MODE":
                return "THE MACHINE", "COUNCIL", "Bureaucratic override active."
        if "/" in soul_archetype:
            return (
                soul_archetype,
                "SOUL",
                f"The Diamond Soul refracts the physics ({soul_archetype}).",
            )
        if trigram:
            trigram_name = trigram.get("name")
            mythos = LoreManifest.get_instance().get("MYTHOS") or {}
            rules = mythos.get("trigram_resonance", [])
            for rule in rules:
                if rule.get("trigram") == trigram_name:
                    required_lens = rule.get("lens")
                    required_soul = rule.get("soul")
                    match_lens = (
                        (required_lens == physics_lens) if required_lens else True
                    )
                    match_soul = (
                        (required_soul == soul_archetype) if required_soul else True
                    )
                    if match_lens and match_soul:
                        return (
                            rule["result"],
                            rule.get("source", "COSMIC"),
                            rule.get("msg", "Resonance detected."),
                        )
        if physics_lens in ["THE MANIC", "THE VOID"]:
            return (
                physics_lens,
                "PHYSICS",
                f"Environment is too loud. You are {physics_lens}.",
            )
        return soul_archetype, "SOUL", "The Soul guides the lens."


class TelemetryService:
    log_dir = "logs/telemetry"
    _tracer_instance = None
    BUFFER_SIZE = 50

    def __init__(self):
        self.trace_buffer: Deque[DecisionTrace] = deque(maxlen=50)
        self.write_buffer: List[str] = []
        self.active_crystal = None
        self.disabled = False
        self.write_errors = 0
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            self.current_trace_file = os.path.join(
                self.log_dir, f"trace_{int(time.time())}.jsonl"
            )
        except OSError:
            print(
                f"{Prisma.RED}[TELEMETRY]: Disk Access Denied. Telemetry Disabled.{Prisma.RST}"
            )
            self.disabled = True
            self.current_trace_file = None

    @classmethod
    def get_tracer(cls):
        if cls._tracer_instance is None:
            cls._tracer_instance = TelemetryService()
        return cls._tracer_instance

    @classmethod
    def get_instance(cls):
        return cls.get_tracer()

    def start_cycle(self, trace_id: str):
        if self.disabled:
            return
        self.active_crystal = DecisionCrystal(decision_id=trace_id)

    def log_decision(
        self,
        component: str,
        decision_type: str,
        inputs: Any,
        reasoning: str,
        outcome: str,
    ):
        if self.disabled or not self.active_crystal:
            return
        trace = DecisionTrace(
            trace_id=self.active_crystal.decision_id,
            timestamp=time.time(),
            component=component,
            decision_type=decision_type,
            inputs=inputs if isinstance(inputs, dict) else {"raw": str(inputs)},
            reasoning=reasoning,
            outcome=outcome,
        )
        self.trace_buffer.append(trace)
        self._buffer_line(trace.to_json())

    def log_crystal(self, crystal: DecisionCrystal):
        if self.disabled:
            return
        self._buffer_line(crystal.crystallize())

    def start_phase(self, phase_name: str, _context: Any):
        self.log_decision(
            phase_name,
            "PHASE_START",
            {"timestamp": time.time()},
            "Phase execution initiated.",
            "RUNNING",
        )

    def end_phase(self, phase_name: str, _ctx_before: Any, _ctx_after: Any):
        self.log_decision(
            phase_name,
            "PHASE_END",
            {"timestamp": time.time()},
            "Phase execution completed.",
            "SUCCESS",
        )

    def finalize_cycle(self):
        if self.active_crystal:
            self.log_crystal(self.active_crystal)
            self.active_crystal = None
        self._flush_to_disk()

    def _buffer_line(self, json_str: str):
        if self.disabled:
            return
        self.write_buffer.append(json_str)
        if len(self.write_buffer) >= self.BUFFER_SIZE:
            self._flush_to_disk()

    def _flush_to_disk(self):
        if self.disabled or not self.current_trace_file or not self.write_buffer:
            return
        try:
            with open(self.current_trace_file, "a", encoding="utf-8") as f:
                f.write("\n".join(self.write_buffer) + "\n")
            self.write_buffer.clear()
            self.write_errors = 0
        except IOError:
            self.write_errors += 1
            if self.write_errors > 3:
                print(
                    f"{Prisma.RED}[TELEMETRY]: Too many write errors. Disabling telemetry.{Prisma.RST}"
                )
                self.disabled = True

    def read_recent_history(self, limit=4) -> List[str]:
        if not os.path.exists(self.log_dir):
            return []
        pattern = os.path.join(self.log_dir, "trace_*.jsonl")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        history = []
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
                            if (
                                data.get("_type") == "CRYSTAL"
                                or "final_response" in data
                            ):
                                resp = data.get("final_response", "")
                                if not resp:
                                    continue
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

    def get_last_thoughts(self, limit=3) -> List[str]:
        history = self.read_recent_history(limit)
        return [h.split("System: ")[-1] for h in history if "System: " in h]

    def get_last_fatal_error(self) -> Optional[str]:
        pattern = os.path.join(self.log_dir, "trace_*.jsonl")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        if len(files) < 2:
            return None
        prev_file = files[1]
        try:
            with open(prev_file, "r") as f:
                lines = f.readlines()
                if not lines:
                    return None
                last_line = json.loads(lines[-1])
                if "outcome" in last_line and "CRITICAL" in str(last_line["outcome"]):
                    return f"PREVIOUS SYSTEM CRASH: {last_line.get('reasoning', 'Unknown')}"
        except Exception:
            return None

    def generate_session_summary(self, _uptime: float = 0.0) -> str:
        self._flush_to_disk()
        count = len(self.trace_buffer)
        status = "DISABLED" if self.disabled else "ACTIVE"
        return (
            f"\n[TELEMETRY] Session ended ({status}). {count} crystals crystallized.\n"
            f"            Trace: {self.current_trace_file}"
        )
