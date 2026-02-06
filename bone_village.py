""" bone_village.py - 'It takes a village... to raise a simulation.' """

import math
import random
import time
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

from bone_core import Prisma, BoneConfig, BonePresets, TheLore
from bone_lexicon import TheLexicon
from bone_protocols import ZenGarden
from bone_drivers import UserProfile
from bone_akashic import TheAkashicRecord

VOLT_MANIC = 12.0
VOLT_CRITICAL = 20.0
DRAG_HEAVY = 6.0
DRAG_SWAMP = 8.0
ENTROPY_RUST_THRESH = 0.3
KAPPA_COHERENT = 0.8
CONFIDENCE_ASCENSION = 2.5
CONFIDENCE_RUST_WARN = 0.2

def _get(p: Any, k: str, d: Any = 0.0) -> Any:
    if p is None: return d
    return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)

def _get_float(p: Any, k: str, d: float = 0.0) -> float:
    val = _get(p, k, d)
    try:
        return float(val)
    except (ValueError, TypeError, AttributeError):
        return d

def _normalize_physics_dict(packet: Any) -> Dict[str, Any]:
    if isinstance(packet, dict):
        return packet
    return getattr(packet, "__dict__", {})

class TheTinkerer:
    def __init__(self, gordon_ref, events_ref, akashic_ref):
        self.gordon = gordon_ref
        self.events = events_ref
        self.tool_confidence: Dict[str, float] = {}
        self.akashic = akashic_ref

    def audit_tool_use(self, physics_packet, inventory_list: List[str], host_health: Any = None):
        p = _normalize_physics_dict(physics_packet)
        voltage = _get_float(p, "voltage", 0.0)
        drag = _get_float(p, "narrative_drag", 0.0)
        kappa = _get_float(p, "kappa", 0.0)
        vector = _get(p, "vector", {})
        ent_val = float(vector.get("ENT", 0.0)) if isinstance(vector, dict) else 0.0
        entropy_level = ent_val + (drag * 0.1)
        for item in inventory_list:
            self._process_single_tool(item, inventory_list, voltage, kappa, entropy_level, drag, vector)

    def _process_single_tool(self, item: str, inventory: List[str], voltage: float, kappa: float, entropy: float, drag: float, vector: Any):
        if item not in self.tool_confidence:
            self.tool_confidence[item] = 1.0
        if voltage > VOLT_MANIC or kappa > KAPPA_COHERENT:
            self._apply_growth(item, inventory, vector)
            return
        if entropy > ENTROPY_RUST_THRESH or drag > DRAG_HEAVY:
            self._apply_decay(item, entropy)

    def _apply_growth(self, item: str, inventory: List[str], vector: Any):
        self.tool_confidence[item] += 0.05
        if self.tool_confidence[item] > CONFIDENCE_ASCENSION:
            self._attempt_ascension(item, inventory, vector)

    def _apply_decay(self, item: str, entropy_level: float):
        decay_rate = 0.05 * (1.0 + entropy_level)
        self.tool_confidence[item] -= decay_rate
        current_conf = self.tool_confidence[item]
        if 0.1 < current_conf < CONFIDENCE_RUST_WARN:
            self.events.log(f"{Prisma.OCHRE}[TINKER] Warning: {item} is rusting. (Conf: {current_conf:.2f}){Prisma.RST}", "SYS")
        elif current_conf <= 0.0:
            self.tool_confidence[item] = 0.0
            self.events.log(f"{Prisma.RED}[TINKER] JAMMED: {item} has seized up via Entropy.{Prisma.RST}", "SYS")

    def _attempt_ascension(self, old_name: str, inventory_list: List[str], vector: Any):
        if "OF_" in old_name:
            return
        new_name, new_data = self.akashic.forge_new_item(vector)
        if old_name in inventory_list:
            idx = inventory_list.index(old_name)
            inventory_list[idx] = new_name # Cleaner than remove/append
            if hasattr(self.gordon, "ITEM_REGISTRY"):
                self.gordon.ITEM_REGISTRY[new_name] = new_data

            self.events.log(f"{Prisma.MAG}✨ ASCENSION: {old_name} -> {new_name}{Prisma.RST}", "AKASHIC")

class ParadoxSeed:
    def __init__(self, question: str, triggers: List[str]):
        self.question = question
        self.triggers = {t.lower() for t in triggers}
        self.maturity = 0.0
        self.bloomed = False

    def water(self, current_words: List[str]) -> bool:
        if self.bloomed: return False
        word_set = set(current_words)
        overlap = self.triggers.intersection(word_set)
        if overlap:
            self.maturity += (len(overlap) * 0.1)
            if self.maturity >= 1.0:
                self.bloomed = True
                return True
        return False
    def bloom(self) -> str:
        return f"{Prisma.GRN}🌸 BLOOM: The seed '{self.question}' has opened. A new truth takes root.{Prisma.RST}"

class MirrorGraph:
    def __init__(self, events_ref):
        self.events = events_ref
        self.stats = {"WAR": 0.0, "ART": 0.0, "LAW": 0.0, "ROT": 0.0}
        self.profile = UserProfile()

    def reflect(self, physics: Dict):
        txt = str(_get(physics, "raw_text", ""))
        volt = _get_float(physics, "voltage", 0.0)
        if "!" in txt or volt > VOLT_MANIC:
            self.stats["WAR"] += 0.1
        if "?" in txt:
            self.stats["ART"] += 0.1
        total = sum(self.stats.values())
        if total > 5.0:
            for k in self.stats:
                self.stats[k] *= 0.8
    def get_reflection_modifiers(self) -> Dict:
        if not self.stats:
            return {"flavor": "Reflecting NEUTRAL", "drag_mult": 1.0}
        top_stat = max(self.stats, key=self.stats.get)
        return {"flavor": f"Reflecting {top_stat}", "drag_mult": 1.0}

def _update_physics_field(packet: Any, key: str, value: Any):
    if isinstance(packet, dict):
        packet[key] = value
    else:
        setattr(packet, key, value)

class TheNavigator:
    def __init__(self, shimmer_ref):
        self.shimmer = shimmer_ref
        self.current_loc = "THE_CONSTRUCT"
        self.last_loc = None
        self.weather_report = "Clear skies."

    def _read_weather(self, volt: float, drag: float) -> str:
        if volt > VOLT_CRITICAL: return "The air is ionizing. Static discharge imminent."
        if volt > VOLT_MANIC: return "High pressure front. Sparks in the fog."
        if drag > DRAG_SWAMP: return "Heavy atmosphere. Movement is like swimming in syrup."
        if drag > 4.0: return "Fog rolling in. Visibility low."
        if volt < 2.0 and drag < 1.0: return "Dead calm. The sails are slack."
        return "Ideal conditions."

    def locate(self, physics_packet: dict, host_health: Any = None) -> Tuple[str, Optional[str]]:
        p = _normalize_physics_dict(physics_packet)
        drag = _get_float(p, "narrative_drag", 0.0)
        volt = _get_float(p, "voltage", 0.0)

        # Logic Mapping
        if volt > VOLT_MANIC:
            self.current_loc = "THE_FORGE"
        elif drag > 5.0:
            self.current_loc = "THE_MUD"
        else:
            self.current_loc = "THE_CONSTRUCT"

        msg = None
        if self.current_loc != self.last_loc:
            self.weather_report = self._read_weather(volt, drag)
            msg = f"{Prisma.CYN}🗺️ WAYFINDER: Entering {self.current_loc}. {self.weather_report}{Prisma.RST}"
            self.last_loc = self.current_loc

        return self.current_loc, msg

    def apply_environment(self, physics_packet: Any) -> List[str]:
        logs = []
        p = _normalize_physics_dict(physics_packet)
        if self.current_loc == "THE_MUD":
            old_drag = _get_float(p, "narrative_drag", 0.0)
            if old_drag < 6.0:
                _update_physics_field(physics_packet, "narrative_drag", 6.0)
                logs.append(f"{Prisma.OCHRE}The Mud holds you. (Drag floor set to 6.0){Prisma.RST}")
        elif self.current_loc == "THE_FORGE":
            old_volt = _get_float(p, "voltage", 0.0)
            if old_volt < VOLT_MANIC:
                _update_physics_field(physics_packet, "voltage", VOLT_MANIC)
            if random.random() < 0.2:
                logs.append(f"{Prisma.RED}The Forge is hot. Ideas are malleable here.{Prisma.RST}")
        return logs

    def strike_root(self, vector): return None
    def check_transplant_shock(self, vector): return None

class TownHall:
    def __init__(self, gordon_ref, events_ref, shimmer_ref, akashic_ref):
        self.Tinkerer = TheTinkerer(gordon_ref, events_ref, akashic_ref)
        self.Navigator = TheNavigator(shimmer_ref)
        self.seeds: List[ParadoxSeed] = []

    @property
    def rumors(self) -> List[str]:
        return TheLore.get("narrative_data", "RUMORS") or ["The air is silent."]

    def sow_seed(self, question: str, triggers: List[str]):
        new_seed = ParadoxSeed(question, triggers)
        self.seeds.append(new_seed)
        return f"Seed planted: '{question}'"

    def tend_garden(self, clean_words: List[str]) -> List[str]:
        logs = []
        remaining_seeds = []
        for seed in self.seeds:
            if not seed.bloomed:
                if seed.water(clean_words):
                    logs.append(seed.bloom())
                else:
                    remaining_seeds.append(seed)
        self.seeds = remaining_seeds
        return logs

    def conduct_census(self, physics_snapshot, host_stats) -> str:
        p = _normalize_physics_dict(physics_snapshot)
        drag = _get_float(p, "narrative_drag", 0.0)
        volt = _get_float(p, "voltage", 0.0)
        latency = getattr(host_stats, "latency", 0.0) if host_stats else 0.0
        if latency > 3.0:
            status, advice = "HIGH_LATENCY", "System is lagging. Simplify inputs."
        elif volt > 15.0:
            status, advice = "HIGH_VOLTAGE", "Manic energy detected. Risk of burnout."
        elif drag > DRAG_HEAVY:
            status, advice = "HIGH_DRAG", "The narrative is stuck in the mud."
        else:
            status, advice = "NOMINAL", "Systems operational."
        news = self._get_town_news(latency, volt, status)
        report = f"CENSUS: {status} | {advice}"
        if news:
            report += f"\n{news}"
        return report

    def _get_town_news(self, latency: float, volt: float, status: str) -> Optional[str]:
        if latency > 4.0:
            return f"{Prisma.OCHRE}📢 TOWN CRIER: The time-winds are blowing slow today! (High Latency){Prisma.RST}"
        if volt > 15.0:
            return f"{Prisma.YEL}📢 HEAR YE: Curfew in effect! The voltage is dangerous!{Prisma.RST}"
        if status == "NOMINAL" and random.random() < 0.05:
            msg = random.choice(self.rumors)
            return f"{Prisma.GRY}📢 TOWN CRIER: {msg}{Prisma.RST}"
        return None

    def diagnose_condition(self, session_data: dict, host_health: Any = None, soul: Any = None) -> Tuple[str, str]:
        meta = session_data.get("meta", {})
        trauma = session_data.get("trauma_vector", {})
        final_health = meta.get("final_health", 50)
        if soul:
            neglect = getattr(soul, "obsession_neglect", 0.0)
            if neglect > 8.0:
                obsession = getattr(soul, 'current_obsession', 'work')
                return "HIGH_DRAG", f"Guilt over '{obsession}' is thickening the air."
        if trauma:
            max_trauma = max(trauma, key=trauma.get)
            if trauma[max_trauma] > 0.6:
                return "HIGH_TRAUMA", f"Warning: High levels of {max_trauma} residue detected."
        if final_health < 30:
            return "HIGH_TRAUMA", "System critical. Structural damage."
        return "BALANCED", "System nominal."

class DeathGen:
    @classmethod
    def load_protocols(cls):
        if TheLore.get("DEATH"):
            return
        print(f"{Prisma.RED}[DEATH]: Protocols missing. Loading default fallback.{Prisma.RST}")
        default_death = {
            "PREFIXES": ["System Halt.", "Alas.", "So it ends."],
            "CAUSES": {
                "DEFAULT": ["Unknown Error"],
                "STARVATION": ["Energy Depletion", "Metabolic Collapse"],
                "GLUTTONY": ["Circuit Overload", "Icarus Failure"],
                "TOXICITY": ["Viral Load Exceeded", "Poisoned Input"],
                "BOREDOM": ["Stagnation", "Entropy Victory"]
            },
            "VERDICTS": {
                "DEFAULT": ["The screen goes black."],
                "HEAVY": ["Gravity wins.", "Silence falls."],
                "LIGHT": ["A flash of light, then nothing."],
                "TOXIC": ["The system purges itself."],
                "BORING": ["The narrative dissolves into grey."]
            }
        }
        TheLore.inject("DEATH", default_death)

    @staticmethod
    def eulogy(physics, mito_state) -> str:
        death_data = TheLore.get("DEATH")
        if not death_data:
            DeathGen.load_protocols()
            death_data = TheLore.get("DEATH")
        p = _normalize_physics_dict(physics)
        cause = DeathGen._determine_cause(p, mito_state)
        verdict_type = DeathGen._determine_verdict_type(p, cause)
        prefix = random.choice(death_data.get("PREFIXES", ["Alas."]))
        specific_cause = random.choice(death_data["CAUSES"].get(cause, ["General Failure"]))
        verdict = random.choice(death_data["VERDICTS"].get(verdict_type, ["It is done."]))
        return f"{prefix} CAUSE: {specific_cause}. {verdict}"

    @staticmethod
    def _determine_cause(p: Dict, mito_state: Any) -> str:
        atp = 0.0
        if isinstance(mito_state, dict):
            atp = float(mito_state.get("atp", 0))
        else:
            atp = float(getattr(mito_state, "atp_pool", 0))
        if atp <= 0: return "STARVATION"
        volt = _get_float(p, "voltage", 0.0)
        drag = _get_float(p, "narrative_drag", 0.0)
        counts = _get(p, "counts", {})
        if volt > VOLT_CRITICAL: return "GLUTTONY"
        if counts.get("antigen", 0) > 5: return "TOXICITY"
        if drag > DRAG_SWAMP: return "BOREDOM"
        return "DEFAULT"

    @staticmethod
    def _determine_verdict_type(p: Dict, cause: str) -> str:
        if cause == "TOXICITY": return "TOXIC"
        if cause == "BOREDOM": return "BORING"
        volt = _get_float(p, "voltage", 0.0)
        return "LIGHT" if volt > 10.0 else "HEAVY"

class PIDController:
    def __init__(self, kp, ki, kd, setpoint, output_limits=(-10.0, 10.0)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.min_out, self.max_out = output_limits
        self._integral = 0.0
        self._last_error = 0.0

    def reset(self):
        self._integral = 0.0
        self._last_error = 0.0

    def update(self, measurement: float, dt: float = 1.0) -> float:
        if dt <= 0.0: return 0.0
        error = self.setpoint - measurement
        self._integral += error * dt
        self._integral = max(self.min_out, min(self.max_out, self._integral))
        derivative = (error - self._last_error) / dt
        output = (self.kp * error) + (self.ki * self._integral) + (self.kd * derivative)
        self._last_error = error
        return max(self.min_out, min(self.max_out, output))

class SanctuaryGovernor:
    def __init__(self, events_ref):
        self.events = events_ref
        self.mode = "DEFAULT"
        self.voltage_pid = PIDController(kp=0.8, ki=0.1, kd=0.05, setpoint=10.0)
        self.drag_pid = PIDController(kp=0.4, ki=0.2, kd=0.1, setpoint=1.0)

    def shift(self, physics_packet, voltage_history, tick_count):
        # Placeholder for future logic
        return "GOVERNOR_MAINTAIN"

    def recalibrate(self, target_voltage: float, target_drag: float):
        self.voltage_pid.setpoint = target_voltage
        self.drag_pid.setpoint = target_drag

    def regulate(self, physics, dt: float) -> Tuple[float, float]:
        v_force = self.voltage_pid.update(physics.voltage, dt)
        d_force = self.drag_pid.update(physics.narrative_drag, dt)
        return v_force, d_force

    def assess(self, physics_packet) -> Tuple[bool, float]:
        p = _normalize_physics_dict(physics_packet)
        curr_v = _get_float(p, "voltage", 0.0)
        curr_d = _get_float(p, "narrative_drag", 0.0)
        target_v = self.voltage_pid.setpoint
        target_d = self.drag_pid.setpoint
        dist_v = abs(curr_v - target_v)
        dist_d = abs(curr_d - target_d)
        is_safe = (dist_v < 2.0) and (dist_d < 1.0)
        distance = math.sqrt(dist_v ** 2 + dist_d ** 2)
        return is_safe, distance

class Limbo:
    def __init__(self):
        self.ghosts: List[str] = []

    def haunt(self, text: str) -> str:
        if not self.ghosts:
            return text
        if random.random() < 0.1:
            ghost_word = random.choice(self.ghosts)
            return f"{text} ...{ghost_word.lower()}..."
        return text