""" bone_village.py - 'It takes a village... to raise a simulation.' """

import random, time
from typing import List, Dict, Any, Tuple, Optional
from bone_bus import Prisma, BoneConfig, BonePresets
from bone_lexicon import TheLexicon
from bone_protocols import ZenGarden
from bone_drivers import UserProfile
from bone_akashic import TheAkashicRecord
from bone_data import TheLore


def _get(p: Any, k: str, d: Any = 0.0) -> Any:
    if p is None: return d
    return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)

def _get_float(p: Any, k: str, d: float = 0.0) -> float:
    val = _get(p, k, d)
    try:
        return float(val)
    except (ValueError, TypeError, AttributeError):
        return float(d)

def _set(p, k, v):
    if isinstance(p, dict): p[k] = v
    else: setattr(p, k, v)

class TheTinkerer:
    def __init__(self, gordon_ref, events_ref):
        self.gordon = gordon_ref
        self.events = events_ref
        self.tool_confidence = {}
        self.akashic = TheAkashicRecord()

    def _normalize_physics(self, packet):
        if isinstance(packet, dict): return packet
        return getattr(packet, "__dict__", {})

    def audit_tool_use(self, physics_packet, inventory_list, host_health: Any = None):
        p = self._normalize_physics(physics_packet)
        voltage = _get_float(p, "voltage", 0.0)
        drag = _get_float(p, "narrative_drag", 0.0)
        vector = _get(p, "vector", {})
        ent_val = 0.0
        if isinstance(vector, dict):
            ent_val = float(vector.get("ENT", 0.0))
        entropy_level = ent_val + (drag * 0.1)
        for item in inventory_list:
            if item not in self.tool_confidence:
                self.tool_confidence[item] = 1.0
            is_manic = voltage > 12.0
            kappa = _get_float(p, "kappa", 0.0)
            is_coherent = kappa > 0.8
            if is_manic or is_coherent:
                self.tool_confidence[item] += 0.05
                if self.tool_confidence[item] > 2.5:
                    self._attempt_ascension(item, inventory_list, vector)
            elif entropy_level > 0.3 or drag > 6.0:
                decay_rate = 0.05 * (1.0 + entropy_level)
                self.tool_confidence[item] -= decay_rate
                if 0.1 < self.tool_confidence[item] < 0.2:
                    self.events.log(f"{Prisma.OCHRE}[TINKER] Warning: {item} is rusting. (Confidence: {self.tool_confidence[item]:.2f}){Prisma.RST}", "SYS")
                elif self.tool_confidence[item] <= 0.0:
                    self.tool_confidence[item] = 0.0
                    self.events.log(f"{Prisma.RED}[TINKER] JAMMED: {item} has seized up via Entropy.{Prisma.RST}", "SYS")

    def _attempt_ascension(self, old_name, inventory_list, vector):
        if "OF_" in old_name: return
        new_name, new_data = self.akashic.forge_new_item(vector)
        if old_name in inventory_list:
            inventory_list.remove(old_name)
            inventory_list.append(new_name)
            if hasattr(self.gordon, "ITEM_REGISTRY"):
                self.gordon.ITEM_REGISTRY[new_name] = new_data
            self.events.log(f"{Prisma.MAG}✨ ASCENSION: {old_name} -> {new_name}{Prisma.RST}", "AKASHIC")

class ParadoxSeed:
    def __init__(self, question, triggers):
        self.question = question
        self.triggers = {t.lower() for t in triggers}
        self.maturity = 0.0
        self.bloomed = False

    def water(self, current_words):
        if self.bloomed: return False
        word_set = set(current_words)
        overlap = self.triggers.intersection(word_set)
        if overlap:
            self.maturity += (len(overlap) * 0.1)
            if self.maturity >= 1.0:
                self.bloomed = True
                return True
        return False

    def bloom(self):
        return f"{Prisma.GRN}🌸 BLOOM: The seed '{self.question}' has opened. A new truth takes root.{Prisma.RST}"

class TheAlmanac:
    def __init__(self):
        self.history = []

    def diagnose(self, physics: Dict, host_stats: Any = None) -> Tuple[str, str]:
        drag = _get_float(physics, "narrative_drag", 0.0)
        volt = _get_float(physics, "voltage", 0.0)

        if host_stats and getattr(host_stats, "latency", 0.0) > 3.0:
            return "HIGH_LATENCY", "System is lagging. Simplify inputs."
        if volt > 15.0:
            return "HIGH_VOLTAGE", "Manic energy detected. Risk of burnout."
        if drag > 6.0:
            return "HIGH_DRAG", "The narrative is stuck in the mud."
        return "NOMINAL", "Systems operational."

    def diagnose_condition(self, session_data: dict, host_health: Any = None, soul: Any = None) -> Tuple[str, str]:
        meta = session_data.get("meta", {})
        trauma = session_data.get("trauma_vector", {})
        final_health = meta.get("final_health", 50)
        if soul:
            neglect = getattr(soul, "obsession_neglect", 0.0)
            if neglect > 8.0:
                return "HIGH_DRAG", f"Guilt over '{getattr(soul, 'current_obsession', 'work')}' is thickening the air."
        max_trauma = max(trauma, key=trauma.get) if trauma else "NONE"
        trauma_val = trauma.get(max_trauma, 0)
        if trauma_val > 0.6:
            return "HIGH_TRAUMA", f"Warning: High levels of {max_trauma} residue detected."
        if final_health < 30:
            return "HIGH_TRAUMA", "System critical. Structural damage."
        return "BALANCED", "System nominal."

    def get_seed(self, condition):
        seeds = {
            "HIGH_TRAUMA": "Recovery",
            "HIGH_DRAG": "Movement",
            "HIGH_VOLTAGE": "Grounding",
            "HIGH_LATENCY": "Patience",
            "BALANCED": "Growth"}
        key = condition.split()[0]
        return seeds.get(key, "Hope")

class MirrorGraph:
    def __init__(self, events_ref):
        self.events = events_ref
        self.stats = {"WAR": 0.0, "ART": 0.0, "LAW": 0.0, "ROT": 0.0}
        self.profile = UserProfile()

    def reflect(self, physics: Dict):
        txt = _get(physics, "raw_text", "")
        if not isinstance(txt, str): txt = str(txt)
        volt = _get_float(physics, "voltage", 0.0)

        if "!" in txt or volt > 12.0: self.stats["WAR"] += 0.1
        if "?" in txt: self.stats["ART"] += 0.1
        total = sum(self.stats.values())
        if total > 5.0:
            for k in self.stats: self.stats[k] *= 0.8

    def get_reflection_modifiers(self) -> Dict:
        top_stat = max(self.stats, key=self.stats.get) if self.stats else "NEUTRAL"
        return {"flavor": f"Reflecting {top_stat}", "drag_mult": 1.0}

class TheWayfinder:
    def __init__(self, shimmer_ref):
        self.shimmer = shimmer_ref
        self.current_loc = "THE_CONSTRUCT"
        self.last_loc = None
        self.weather_report = "Clear skies."

    def _read_weather(self, volt, drag):
        try:
            volt = float(volt)
            drag = float(drag)
        except (ValueError, TypeError):
            return "Sensors offline (Data Corrupt)."

        if volt > 20.0: return "The air is ionizing. Static discharge imminent."
        if volt > 12.0: return "High pressure front. Sparks in the fog."
        if drag > 8.0: return "Heavy atmosphere. Movement is like swimming in syrup."
        if drag > 4.0: return "Fog rolling in. Visibility low."
        if volt < 2.0 and drag < 1.0: return "Dead calm. The sails are slack."
        return "Ideal conditions."

    def locate(self, physics_packet: dict, host_health: Any = None) -> Tuple[str, Optional[str]]:
        drag = _get_float(physics_packet, "narrative_drag", 0.0)
        volt = _get_float(physics_packet, "voltage", 0.0)

        if volt > 12.0: self.current_loc = "THE_FORGE"
        elif drag > 5.0: self.current_loc = "THE_MUD"
        else: self.current_loc = "THE_CONSTRUCT"
        msg = None
        if self.current_loc != self.last_loc:
            self.weather_report = self._read_weather(volt, drag)
            msg = f"{Prisma.CYN}🗺️ WAYFINDER: Entering {self.current_loc}. {self.weather_report}{Prisma.RST}"
            self.last_loc = self.current_loc
        return self.current_loc, msg

    def apply_environment(self, physics_packet: Any) -> List[str]:
        logs = []
        if self.current_loc == "THE_MUD":
            old_drag = _get_float(physics_packet, "narrative_drag", 0.0)
            _set(physics_packet, "narrative_drag", max(old_drag, 6.0))
            logs.append(f"{Prisma.OCHRE}The Mud holds you. (Drag floor set to 6.0){Prisma.RST}")
        elif self.current_loc == "THE_FORGE":
            old_volt = _get_float(physics_packet, "voltage", 0.0)
            _set(physics_packet, "voltage", max(old_volt, 12.0))
            if random.random() < 0.2:
                logs.append(f"{Prisma.RED}The Forge is hot. Ideas are malleable here.{Prisma.RST}")
        return logs

    def strike_root(self, vector): return None
    def check_transplant_shock(self, vector): return None

class TheTownCrier:
    def __init__(self):
        pass

    @property
    def rumors(self) -> List[str]:
        return TheLore.get("narrative_data", "RUMORS") or [
            "The air is silent.",
            "The Crier has lost their notes."]

    def broadcast(self, physics: Dict, host_stats: Any = None) -> Optional[str]:
        if host_stats and getattr(host_stats, "latency", 0.0) > 4.0:
            return f"{Prisma.OCHRE}📢 TOWN CRIER: The time-winds are blowing slow today! (High Latency){Prisma.RST}"
        volt = _get_float(physics, "voltage", 0.0)
        if volt > 15.0:
            return f"{Prisma.YEL}📢 HEAR YE: Curfew in effect! The voltage is dangerous!{Prisma.RST}"
        if random.random() < 0.05:
            return f"{Prisma.GRY}📢 TOWN CRIER: {random.choice(self.rumors)}{Prisma.RST}"
        return None

class TownHall:
    def __init__(self, gordon_ref, events_ref, shimmer_ref):
        self.Tinkerer = TheTinkerer(gordon_ref, events_ref)
        self.Navigator = TheWayfinder(shimmer_ref)
        self.Almanac = TheAlmanac()
        self.Crier = TheTownCrier()
        self.seeds: List[ParadoxSeed] = []

    def sow_seed(self, question: str, triggers: List[str]):
        new_seed = ParadoxSeed(question, triggers)
        self.seeds.append(new_seed)
        return f"Seed planted: '{question}'"

    def tend_garden(self, clean_words: List[str]) -> List[str]:
        logs = []
        active_seeds = [s for s in self.seeds if not s.bloomed]
        for seed in active_seeds:
            if seed.water(clean_words):
                logs.append(seed.bloom())
        self.seeds = [s for s in self.seeds if not s.bloomed]
        return logs

    def conduct_census(self, physics_snapshot, host_stats):
        status, advice = self.Almanac.diagnose(physics_snapshot, host_stats)
        news = self.Crier.broadcast(physics_snapshot, host_stats)
        report = f"CENSUS: {status} | {advice}"
        if news:
            report += f"\n{news}"
        return report

class DeathGen:
    @classmethod
    def load_protocols(cls):
        death_data = TheLore.get("DEATH")
        if not death_data:
            print(f"{Prisma.RED}[DEATH]: Protocols missing. Loading default fallback.{Prisma.RST}")
            default_death = {
                "PREFIXES": ["System Halt."],
                "CAUSES": {"DEFAULT": ["Unknown Error"]},
                "VERDICTS": {"DEFAULT": ["The screen goes black."]}}
            TheLore.inject("DEATH", default_death)

    @staticmethod
    def eulogy(physics, mito_state) -> str:
        death_data = TheLore.get("DEATH")
        cause = "TRAUMA"
        voltage = _get_float(physics, "voltage", 0)
        drag = _get_float(physics, "narrative_drag", 0)
        counts = _get(physics, "counts", {})

        atp = 0.0
        if isinstance(mito_state, dict):
            atp = float(mito_state.get("atp", 0))
        else:
            atp = float(getattr(mito_state, "atp_pool", 0))

        if atp <= 0:
            cause = "STARVATION"
        elif voltage > 20.0:
            cause = "GLUTTONY"
        elif isinstance(counts, dict) and counts.get("antigen", 0) > 5:
            cause = "TOXICITY"
        elif drag > 8.0:
            cause = "BOREDOM"

        prefixes = death_data.get("PREFIXES", ["Alas."])
        prefix = random.choice(prefixes)
        specific_causes = death_data.get("CAUSES", {}).get(cause, ["General System Failure"])
        specific_cause = random.choice(specific_causes)
        verdict_type = "HEAVY"
        if voltage > 10.0:
            verdict_type = "LIGHT"
        elif cause == "TOXICITY":
            verdict_type = "TOXIC"
        elif cause == "BOREDOM":
            verdict_type = "BORING"
        verdicts = death_data.get("VERDICTS", {}).get(verdict_type, ["It is done."])
        verdict = random.choice(verdicts)
        return f"{prefix} CAUSE: {specific_cause}. {verdict}"

TheNavigator = TheWayfinder

class PIDController:
    def __init__(self, kp: float, ki: float, kd: float, setpoint: float = 0.0, output_limits: tuple = (-5.0, 5.0)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.output_min, self.output_max = output_limits
        self._prev_error = 0.0
        self._integral = 0.0

    def reset(self):
        self._prev_error = 0.0
        self._integral = 0.0

    def update(self, measurement: float, dt: float = 1.0) -> float:
        if dt is None: dt = 1.0
        safe_dt = max(0.001, dt)
        error = self.setpoint - measurement
        self._integral += error * safe_dt
        self._integral = max(self.output_min, min(self.output_max, self._integral))
        derivative = (error - self._prev_error) / safe_dt
        output = (self.kp * error) + (self.ki * self._integral) + (self.kd * derivative)
        output = max(self.output_min, min(self.output_max, output))
        self._prev_error = error
        return output

class SanctuaryGovernor:
    def __init__(self, events_ref):
        self.events = events_ref
        self.defaults = {
            "voltage": getattr(BonePresets.SANCTUARY, "VOLTAGE_TARGET", 10.0),
            "drag": getattr(BonePresets.SANCTUARY, "DRAG_TARGET", 2.0)}
        self.voltage_pid = PIDController(
            kp=0.05, ki=0.01, kd=0.02,
            setpoint=self.defaults["voltage"],
            output_limits=(-2.0, 2.0))
        self.drag_pid = PIDController(
            kp=0.08, ki=0.02, kd=0.03,
            setpoint=self.defaults["drag"],
            output_limits=(-1.0, 1.0))
        self.in_sanctuary = False
        self.consecutive_safe_ticks = 0

    def recalibrate(self, target_voltage: float = None, target_drag: float = None):
        if target_voltage is not None:
            self.voltage_pid.setpoint = float(target_voltage)
        else:
            self.voltage_pid.setpoint = self.defaults["voltage"]
        if target_drag is not None:
            self.drag_pid.setpoint = float(target_drag)
        else:
            self.drag_pid.setpoint = self.defaults["drag"]

    def regulate(self, physics_packet, dt: float = 1.0) -> tuple:
        curr_v = _get_float(physics_packet, "voltage")
        curr_d = _get_float(physics_packet, "narrative_drag")
        v_force = self.voltage_pid.update(curr_v, dt=dt)
        d_force = self.drag_pid.update(curr_d, dt=dt)
        return v_force, d_force

    def assess(self, physics_packet):
        v = _get_float(physics_packet, "voltage", 0.0)
        d = _get_float(physics_packet, "narrative_drag", 0.0)
        t = _get_float(physics_packet, "truth_ratio", 0.0)
        v_target = self.voltage_pid.setpoint
        d_target = self.drag_pid.setpoint
        v_tol = float(getattr(BonePresets.SANCTUARY, "VOLTAGE_TOLERANCE", 5.0) or 1.0)
        d_tol = float(getattr(BonePresets.SANCTUARY, "DRAG_TOLERANCE", 2.0) or 1.0)
        t_target = float(getattr(BonePresets.SANCTUARY, "TRUTH_TARGET", 0.8))
        v_dist = abs(v - v_target) / v_tol
        d_dist = abs(d - d_target) / d_tol
        t_dist = abs(t - t_target) / 0.3
        avg_dist = (v_dist + d_dist + t_dist) / 3.0
        is_safe = avg_dist < 0.5
        if is_safe:
            self.consecutive_safe_ticks += 1
            if self.consecutive_safe_ticks >= 3 and not self.in_sanctuary:
                self.in_sanctuary = True
                self.events.log(f"{getattr(BonePresets.SANCTUARY, 'COLOR', Prisma.GRN)}![☀️] SANCTUARY: The air is calm here.{Prisma.RST}", "SYS")
        else:
            self.consecutive_safe_ticks = 0
            self.in_sanctuary = False
        return self.in_sanctuary, avg_dist


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