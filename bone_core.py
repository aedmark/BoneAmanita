"""
bone_core.py

The Central Nervous System.
This module provides the foundational infrastructure for the entire lattice.
It contains the EventBus (pub/sub message routing), the LoreManifest (lazy-loaded data),
the RealityStack (which manages layers of simulation vs. reality), and the
TelemetryService (the black box recorder).
"""

import glob
import json
import os
import random
import time
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Counter, Tuple, Deque
from bone_presets import BoneConfig
from bone_types import Prisma, RealityLayer, ErrorLog, DecisionTrace, DecisionCrystal

def ux(section: str, key: str, default: Any = "") -> Any:
    """Global syntax sugar to reduce lattice verbosity when fetching UI strings."""
    return LoreManifest.get_instance().get_ux(section, key, default)

class BoneJSONEncoder(json.JSONEncoder):
    """
    A custom JSON encoder to handle the specific data structures used
    throughout the lattice (sets, deques, and custom objects with a to_dict method).
    """
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
    """
    The Vagus Nerve. A pub/sub architecture that allows the MitochondrialForge,
    Cortex, and Council to broadcast state changes without needing direct,
    tightly-coupled Python references to one another.
    """
    def __init__(self, max_memory=None):
        cfg = getattr(BoneConfig, "CORE", None)
        limit = max_memory if max_memory else (getattr(cfg, "EVENT_MAX_MEMORY", 1024) if cfg else 1024)
        self.buffer = deque(maxlen=limit)
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)

    def publish(self, event_type, data=None):
        """ Broadcasts an event to all interested organs. """
        if event_type not in self.subscribers:
            return

        for callback in list(self.subscribers[event_type]):
            try:
                callback(data)
            except Exception as e:
                # Gracefully catch errors in event handlers so a single
                # failing callback doesn't crash the entire nervous system.
                cb_name = getattr(callback, "__name__", str(callback))
                raw_err = f"Error in '{cb_name}' for '{event_type}': {e}"
                msg = ux("core_strings", "bus_error")
                if msg: print(f"{Prisma.RED}{msg.format(error_msg=raw_err)}{Prisma.RST}")
                self.log(f"EVENT_FAILURE: {raw_err}", category="CRIT")

    def log(self, text: str, category: str = "SYSTEM"):
        """Buffers logs to be consumed and cleared by the cycle runner for the UI."""
        entry = {"text": text, "category": category, "timestamp": time.time()}
        self.buffer.append(entry)

    def flush(self) -> List[Dict]:
        """Flushes the buffer. Used to display logs to the UI at the end of a cycle."""
        current_logs = list(self.buffer)
        self.buffer.clear()
        return current_logs

    def get_recent_logs(self, count=10):
        return list(self.buffer)[-count:]

class LoreManifest:
    """
    The Akashic index of static data. It lazy-loads JSON files from the 'lore'
    directory, acting as a centralized configuration dictionary for the entire architecture.
    """
    _instance = None

    def __init__(self, data_dir=None):
        cfg = getattr(BoneConfig, "CORE", None)
        default_dir = getattr(cfg, "LORE_DIR", "lore") if cfg else "lore"
        self.DATA_DIR = data_dir or default_dir
        self._cache = {}

    @classmethod
    def get_instance(cls):
        # Singleton pattern ensures all modules read from the same cached memory.
        if cls._instance is None:
            cls._instance = LoreManifest()
        return cls._instance

    def get(self, category: str, sub_key: str = None) -> Any:
        if category not in self._cache:
            data = self._load_from_disk(category)
            self._cache[category] = data if data is not None else {}
        data = self._cache[category]
        if sub_key and isinstance(data, dict):
            return data.get(sub_key)
        return data

    def get_ux(self, section: str, key: str, default: Any = "") -> Any:
        """A specialized getter for UI strings, allowing for easy localization or reskinning."""
        section_data = self.get("ux_strings", section)
        if isinstance(section_data, dict):
            return section_data.get(key, default)
        return default

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
        """Allows dynamic injection of new lore during runtime without writing to disk."""
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
                print(f"{Prisma.GRY}[LORE]: Category '{category}' not in cache.{Prisma.RST}")
        else:
            self._cache = {}
            print(f"{Prisma.CYN}[LORE]: Flushed Lore cache.{Prisma.RST}")

class TheObserver:
    """
    A crucial monitoring loop. It tracks the time it takes for the internal
    Python execution (cycle) vs the external API call (llm). It uses these metrics
    to pass judgment on the system's "health" and "efficiency," adding physical
    latency penalties to the metabolism if the system runs too slowly.
    """
    def __init__(self):
        self.start_time = time.time()
        cfg = getattr(BoneConfig, "CORE", None)
        max_len = getattr(cfg, "OBSERVER_MAX_LEN", 20) if cfg else 20
        self.cycle_times = deque(maxlen=max_len)
        self.llm_latencies = deque(maxlen=max_len)
        self.memory_snapshots = deque(maxlen=max_len)
        self.error_counts = Counter()
        self.user_turns = 0
        self.LATENCY_WARNING = getattr(cfg, "OBSERVER_LATENCY_WARN", 5.0) if cfg else 5.0
        self.CYCLE_WARNING = getattr(cfg, "OBSERVER_CYCLE_WARN", 8.0) if cfg else 8.0
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
        """Efficiency is modeled as resources retained divided by time spent thinking."""
        duration = max(0.01, self.last_cycle_duration)
        resource_sum = health + stamina
        return resource_sum / duration

    def log_error(self, module_name):
        self.error_counts[module_name] += 1

    def record_memory(self, node_count):
        self.memory_snapshots.append(node_count)

    def pass_judgment(self, avg_cycle, avg_llm):
        """Translates raw latency metrics into somatic feedback (e.g., 'fog', 'sluggish')."""
        if avg_cycle == 0.0 and avg_llm == 0.0:
            return ux("core_strings", "obs_asleep")
        cfg = getattr(BoneConfig, "CORE", None)
        cycle_eff = getattr(cfg, "OBSERVER_CYCLE_EFFICIENT", 0.1) if cfg else 0.1
        llm_eff = getattr(cfg, "OBSERVER_LLM_EFFICIENT", 0.5) if cfg else 0.5
        if avg_cycle < cycle_eff and avg_llm < llm_eff:
            return ux("core_strings", "obs_efficient")
        if avg_llm > self.LATENCY_WARNING:
            jokes = [ux("core_strings", "obs_fog") ,
                     ux("core_strings", "obs_degraded") ,
                     ux("core_strings", "obs_ponderous") ,]
            valid_jokes = [j for j in jokes if j]
            return random.choice(valid_jokes) if valid_jokes else ""
        if avg_cycle > self.CYCLE_WARNING:
            return ux("core_strings", "obs_sluggish")
        return ux("core_strings", "obs_nominal")

    def get_report(self):
        avg_cycle = sum(self.cycle_times) / max(1, len(self.cycle_times))
        avg_llm = sum(self.llm_latencies) / max(1, len(self.llm_latencies))
        uptime = time.time() - self.start_time
        status_msg = self.pass_judgment(avg_cycle, avg_llm)
        return {"uptime_sec": int(uptime), "turns": self.user_turns, "avg_cycle_sec": round(avg_cycle, 2),
                "avg_llm_sec": round(avg_llm, 2), "status": status_msg, "errors": dict(self.error_counts),
                "graph_size": self.memory_snapshots[-1] if self.memory_snapshots else 0, }

@dataclass
class SystemHealth:
    """Tracks the structural integrity of the primary modules so they can be gracefully rebooted if they fail."""
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
    """
    A literal stack that dictates the governing laws of the simulation.
    By pushing RealityLayer.DEBUG, the system temporarily suspends narrative generation
    (hallucination) to allow for raw technical output, then pops back into character.
    """
    def __init__(self):
        self._stack = [RealityLayer.SIMULATION]
        self._lock = False

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
        if self._lock:
            return self.current_depth
        if len(self._stack) > 1:
            return self._stack.pop()
        return self._stack[0]

    def stabilize_at(self, layer: int):
        self._stack = [layer]

    def get_grammar_rules(self) -> Dict[str, bool]:
        """Maps the current structural layer to executable permissions (e.g., can the user run commands?)."""
        depth = self.current_depth
        return {"allow_narrative": depth
                                   in [RealityLayer.SIMULATION, RealityLayer.DEEP_CX, RealityLayer.DEBUG],
                "allow_commands": depth >= RealityLayer.SIMULATION, "allow_meta": depth >= RealityLayer.DEBUG,
                "raw_output": depth == RealityLayer.DEEP_CX, "system_override": depth == RealityLayer.DEBUG, }

class ArchetypeArbiter:
    """
    The final judge of who holds the microphone.
    It checks council mandates (e.g., LOCKDOWN), then checks for hybrid archetypes (Diamond),
    then checks for trigram resonance, and finally defaults to the base Soul archetype.
    """
    @staticmethod
    def arbitrate(physics_lens: str, soul_archetype: str, council_mandates: List[Dict], trigram: Dict = None, ) -> Tuple[str, str, str]:
        # 1. Council Overrides (Absolute Authority)
        for mandate in council_mandates:
            if mandate.get("type") == "LOCKDOWN":
                return "THE CENSOR", "COUNCIL", ux("core_strings", "arb_martial_law") ,
            if mandate.get("type") == "FORCE_MODE":
                return "THE MACHINE", "COUNCIL", ux("core_strings", "arb_bureaucratic") ,
        # 2. Hybrid Archetypes (e.g., JESTER/SHERLOCK)
        if "/" in soul_archetype:
            msg = ux("core_strings", "arb_diamond")
            return soul_archetype, "SOUL", msg.format(soul_archetype=soul_archetype) if msg else "",
        # 3. Trigram Resonance (If the physical math aligns perfectly with the current lens)
        if trigram:
            trigram_name = trigram.get("name")
            mythos = LoreManifest.get_instance().get("MYTHOS") or {}
            rules = mythos.get("trigram_resonance", [])
            for rule in rules:
                if rule.get("trigram") == trigram_name:
                    required_lens = rule.get("lens")
                    required_soul = rule.get("soul")
                    match_lens = (required_lens == physics_lens) if required_lens else True
                    match_soul = (required_soul == soul_archetype) if required_soul else True
                    if match_lens and match_soul:
                        msg = rule.get("msg") or ux("core_strings", "arb_resonance")
                        return rule["result"], rule.get("source", "COSMIC"), msg
        # 4. Loud Lenses (Certain lenses demand the mic regardless of Soul state)
        cfg = getattr(BoneConfig, "CORE", None)
        loud_lenses = getattr(cfg, "LOUD_LENSES", ["THE MANIC", "THE VOID"]) if cfg else ["THE MANIC", "THE VOID"]
        if physics_lens in loud_lenses:
            msg = ux("core_strings", "arb_loud")
            return physics_lens, "PHYSICS", msg.format(physics_lens=physics_lens) if msg else "",
        # 5. Default to the current NarrativeSelf
        return soul_archetype, "SOUL",  ux("core_strings", "arb_soul")

class TelemetryService:
    """
    An optional black box recorder. It writes every state transition, phase shift,
    and LLM query out to a JSONL file. Crucial for tracing the exact physics vector that
    caused the lattice to collapse.
    """
    _tracer_instance = None

    def __init__(self):
        cfg = getattr(BoneConfig, "CORE", None)
        self.log_dir = getattr(cfg, "TELEMETRY_LOG_DIR", "logs/telemetry") if cfg else "logs/telemetry"
        self.BUFFER_SIZE = getattr(cfg, "TELEMETRY_BUFFER_SIZE", 50) if cfg else 50
        self.MAX_ERRORS = getattr(cfg, "TELEMETRY_MAX_ERRORS", 5) if cfg else 5
        self.trace_buffer: Deque[DecisionTrace] = deque(maxlen=self.BUFFER_SIZE)
        self.write_buffer: List[str] = []
        self.active_crystal = None
        self.disabled = False
        self.write_errors = 0
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            self.current_trace_file = os.path.join(
                self.log_dir, f"trace_{int(time.time())}.jsonl")
        except OSError:
            msg = ux("core_strings", "tel_disk_denied")
            if msg: print(f"{Prisma.RED}{msg}{Prisma.RST}")
            self.disabled = True
            self.current_trace_file = None

    @classmethod
    def get_instance(cls):
        if cls._tracer_instance is None:
            cls._tracer_instance = TelemetryService()
        return cls._tracer_instance

    def start_cycle(self, trace_id: str):
        if self.disabled:
            return
        if self.active_crystal and self.active_crystal.decision_id == trace_id:
            return
        self.active_crystal = DecisionCrystal(decision_id=trace_id)

    def log_decision(self, component: str, decision_type: str, inputs: Any, reasoning: str, outcome: str, ):
        if self.disabled or not self.active_crystal:
            return
        trace = DecisionTrace(trace_id=self.active_crystal.decision_id, timestamp=time.time(), component=component,
                              decision_type=decision_type,
                              inputs=inputs if isinstance(inputs, dict) else {"raw": str(inputs)}, reasoning=reasoning, outcome=outcome)
        self.trace_buffer.append(trace)
        self._buffer_line(trace.to_json())

    def log_crystal(self, crystal: DecisionCrystal):
        if self.disabled:
            return
        self._buffer_line(crystal.crystallize())

    def start_phase(self, phase_name: str, _context: Any):
        msg = ux("core_strings", "tel_phase_start")
        self.log_decision(phase_name, "PHASE_START", {"timestamp": time.time()}, msg, "RUNNING",)

    def end_phase(self, phase_name: str, _ctx_before: Any, _ctx_after: Any):
        msg = ux("core_strings", "tel_phase_end")
        self.log_decision( phase_name, "PHASE_END", {"timestamp": time.time()}, msg, "SUCCESS",)

    def finalize_cycle(self):
        if self.active_crystal:
            self.log_crystal(self.active_crystal)
            self.active_crystal = None
        self.flush_to_disk()

    def _buffer_line(self, json_str: str):
        if self.disabled:
            return
        self.write_buffer.append(json_str)
        if len(self.write_buffer) >= self.BUFFER_SIZE:
            self.flush_to_disk()

    def flush_to_disk(self):
        if self.disabled or not self.current_trace_file or not self.write_buffer:
            return
        try:
            with open(self.current_trace_file, "a", encoding="utf-8") as f:
                f.write("\n".join(self.write_buffer) + "\n")
            self.write_buffer.clear()
            self.write_errors = 0
        except IOError as e:
            self.write_errors += 1
            if self.write_errors >= getattr(self, "MAX_ERRORS", 5):
                msg = ux("core_strings", "tel_crit_write_fail")
                if msg: print(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}")
                self.disabled = True
                self.write_buffer.clear()
            else:
                keep_count = self.BUFFER_SIZE // 2
                self.write_buffer = self.write_buffer[-keep_count:]
                msg = ux("core_strings", "tel_write_error")
                if msg: print(f"{Prisma.RED}{msg.format(errors=self.write_errors, e=e)}{Prisma.RST}")

    def read_recent_history(self, limit=4) -> List[str]:
        if not os.path.exists(self.log_dir):
            return []
        pattern = os.path.join(self.log_dir, "trace_*.jsonl")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        history = []
        for fpath in files:
            if len(history) >= limit: break
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    # Read from the bottom up without excessive nesting
                    lines = deque(f, maxlen=limit * 2)
                    for line in reversed(lines):
                        if len(history) >= limit: break
                        try:
                            data = json.loads(line)
                            if data.get("_type") != "CRYSTAL" and "final_response" not in data:
                                continue
                            resp = data.get("final_response", "")
                            prompt = data.get("prompt_snapshot", "")
                            if not resp: continue

                            user_text = prompt.split("User:")[1].split("\n")[0].strip() if "User:" in prompt else "Unknown"
                            history.insert(0, f"User: {user_text} | System: {resp}")
                        except (json.JSONDecodeError, IndexError):
                            continue # Silent skip on corrupt lines
            except IOError:
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
            with open(prev_file, "r", encoding="utf-8") as f:
                lines = deque(f, maxlen=1)
                if not lines:
                    return None
                last_line = json.loads(lines[0])
                if "outcome" in last_line and "CRITICAL" in str(last_line["outcome"]):
                    reason = last_line.get("reasoning", "Unknown")
                    msg = ux("core_strings", "tel_prev_crash")
                    return msg.format(reason=reason) if msg else ""
        except Exception:
            return None

    def generate_session_summary(self, _uptime: float = 0.0) -> str:
        self.flush_to_disk()
        count = len(self.trace_buffer)
        status = "DISABLED" if self.disabled else "ACTIVE"
        msg = ux("core_strings", "tel_session_summary")
        return msg.format(status=status, count=count, trace_file=self.current_trace_file) if msg else ""