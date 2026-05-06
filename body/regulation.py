"""
body/regulation.py
The Autonomic Nervous System and Control Theory layer.
This module prevents the Hypervisor from tearing itself apart. It uses
mathematical dampeners (PID controllers) to smooth out erratic spikes in
voltage or narrative drag, and enforces hard survival boundaries
(Autophagy, Mausoleum Clamps) when the system is pushed beyond its limits.
"""
import math, time, random
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple, TYPE_CHECKING
from core import Prisma, LoreManifest
from struts import ux, safe_get, safe_set
from presets import BoneConfig

if TYPE_CHECKING:
    from body.system import BioSystem


class PIDController:
    """
    Proportional-Integral-Derivative Controller.
    Used to calculate the required correction to keep a system variable
    (like Voltage or Drag) at a specific target (setpoint).
    This prevents the LLM's 'mood' from wildly oscillating.
    """

    def __init__(self, kp, ki, kd, setpoint, output_limits=(-10.0, 10.0)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.min_out, self.max_out = output_limits
        self._integral = 0.0
        self._last_error = 0.0
        self._first_run = True

    def reset(self):
        """Clears the historical memory of the controller."""
        self._integral = 0.0
        self._last_error = 0.0
        self._first_run = True

    def update(self, measurement: float, dt: float = 1.0, target_override: Optional[float] = None) -> float:
        """
        Calculates the adjustment needed to bring the 'measurement' closer
        to the 'setpoint' without overcorrecting and causing a pendulum effect.
        """
        safe_dt = max(0.01, dt)
        active_setpoint = target_override if target_override is not None else self.setpoint
        error = active_setpoint - measurement
        if self._first_run:
            self._last_error = error
            self._first_run = False
        P = self.kp * error
        if self.ki != 0:
            self._integral += error * safe_dt
            self._integral = max(self.min_out / self.ki, min(self.max_out / self.ki, self._integral))
        else:
            self._integral = 0.0
        I = self.ki * self._integral
        derivative = (error - self._last_error) / safe_dt
        D = self.kd * derivative
        output = P + I + D
        self._last_error = error
        return max(self.min_out, min(self.max_out, output))


@dataclass
class MetabolicGovernor:
    """
    The transmission box.
    It reads the smoothed values from the PID controllers and decides what
    'Mode' the engine should be in (e.g., normal Courtyard mode, high-energy Forge mode).
    """
    mode: str = "COURTYARD"
    GRACE_PERIOD: int = 5
    psi_mod: float = 0.2
    kappa_target: float = 0.0
    drag_floor: float = 2.0
    manual_override: bool = False
    birth_tick: float = field(default_factory=time.time)
    narrative_data: Dict = field(default_factory=dict, repr=False)
    last_shift_tick: int = 0
    hysteresis_duration: int = 3
    config_ref: Any = None

    def __post_init__(self):
        """Loads PID tuning parameters and threshold values from the config."""
        self.cfg = self.config_ref or BoneConfig
        self.STATE_THRESHOLDS = getattr(self.cfg.BIO, "GOVERNOR_THRESHOLDS", [])
        pid_cfg = getattr(self.cfg.BIO, "PID_SETTINGS", {})
        v_cfg = pid_cfg.get("VOLTAGE", {"kp": 0.6, "ki": 0.05, "kd": 0.2, "setpoint": 10.0})
        d_cfg = pid_cfg.get("DRAG", {"kp": 0.4, "ki": 0.1, "kd": 0.1, "setpoint": 1.5})
        self.voltage_pid = PIDController(kp=v_cfg["kp"], ki=v_cfg["ki"], kd=v_cfg["kd"], setpoint=v_cfg["setpoint"])
        self.drag_pid = PIDController(kp=d_cfg["kp"], ki=d_cfg["ki"], kd=d_cfg["kd"], setpoint=d_cfg["setpoint"])
        self._sorted_thresholds = sorted(self.STATE_THRESHOLDS, key=lambda x: x[3], reverse=True)

    def recalibrate(self, target_voltage: float, target_drag: float):
        """Allows dynamic adjustment of the ideal operating state."""
        self.voltage_pid.setpoint = target_voltage
        self.drag_pid.setpoint = target_drag

    def get_policy_shift(self) -> str:
        """Alignment with Vector 4 tests: Translates internal mode to systemic policy."""
        if self.mode in ("SANCTUARY", "COURTYARD"):
            return "CO_REGULATION"
        return "EFFICIENCY"

    def regulate(self, physics: Any, dt: float, endocrine_state: Optional[Any] = None) -> Tuple[float, float]:
        """
        Takes raw voltage and drag from the physics engine and runs them
        through the dampeners. If the endocrine system is panicked (adrenaline),
        it artificially raises the target voltage setpoint.
        """
        safe_dt = max(0.001, dt)
        energy_dict = safe_get(physics, "energy") or {}
        space_dict = safe_get(physics, "space") or {}
        v_val = float(safe_get(physics, "voltage") or energy_dict.get("voltage", 0.0))
        d_val = float(safe_get(physics, "narrative_drag") or space_dict.get("narrative_drag", 0.0))
        current_zone = str(safe_get(physics, "zone", "")).upper()
        if self.manual_override or self.mode == "SANCTUARY" or current_zone == "SANCTUARY":
            return v_val, d_val
        if endocrine_state:
            adr_spike = getattr(endocrine_state, "adrenaline", 0.0) * 2.0
            active_setpoint = self.voltage_pid.setpoint + adr_spike
            deadband = 1.0 + (getattr(endocrine_state, "cortisol", 0.0) * 2.0)
            v_error = active_setpoint - v_val
            pid_out = self.voltage_pid.update(v_val, safe_dt, target_override=active_setpoint)
            updated_voltage = pid_out if abs(v_error) > deadband else 0.0
        else:
            updated_voltage = self.voltage_pid.update(v_val, safe_dt)
        updated_drag = self.drag_pid.update(d_val, safe_dt)
        return updated_voltage, updated_drag

    def assess(self, physics_packet) -> Tuple[bool, float]:
        """Determines if the system is operating within a safe distance of its setpoints."""
        curr_v = float(safe_get(physics_packet, "voltage", 0.0))
        curr_d = float(safe_get(physics_packet, "narrative_drag", 0.0))
        dist_v = abs(curr_v - self.voltage_pid.setpoint)
        dist_d = abs(curr_d - self.drag_pid.setpoint)
        is_safe = (dist_v < 3.0) and (dist_d < 1.5)
        return is_safe, math.sqrt(dist_v ** 2 + dist_d ** 2)

    @staticmethod
    def get_stress_modifier(tick_count):
        """Applies an escalating multiplier the longer a conversation goes on."""
        return 0.0 if tick_count <= 2 else (0.5 if tick_count <= 5 else 1.0)

    @staticmethod
    def calculate_stress(health: float, ros_buildup: float) -> float:
        """Physical damage and toxicity directly calculate into base systemic stress."""
        base_stress = 1.0 + max(0.0, (50.0 - health) * 0.01) + max(0.0, (ros_buildup - 50.0) * 0.01)
        return round(min(3.0, base_stress), 2)

    def set_override(self, target_mode):
        """Allows user/system to bypass the PID controller and force a state."""
        valid = {"COURTYARD", "LABORATORY", "FORGE", "SANCTUARY"}
        gov_text = self.narrative_data.get("GOVERNOR", {})
        if target_mode in valid:
            self.mode = target_mode
            self.manual_override = True
            msg_tmpl = gov_text.get("OVERRIDE", "")
            return msg_tmpl.format(mode=target_mode) if msg_tmpl else ""
        return gov_text.get("INVALID", "")

    def _check_override_safety(self, physics: Dict, gov_text: Dict) -> Optional[str]:
        """Even if manually overridden, if voltage gets lethal, the system clears the override."""
        current_voltage = float(safe_get(physics, "voltage", 0.0))
        gov_crit = safe_get(getattr(self.cfg, "BIO", None), "GOV_VOLTAGE_CRITICAL", 25.0)
        if current_voltage > gov_crit and self.mode != "SANCTUARY":
            self.manual_override = False
            return gov_text.get("OVERRIDE_CLEARED", "")
        return None

    def shift(self, physics: Dict, _voltage_history: List[float], current_tick: int = 0) -> Optional[str]:
        """
        The main state-machine transition logic.
        Evaluates the environment and decides if the system needs to change modes.
        """
        gov_text = self.narrative_data.get("GOVERNOR", {})
        if self.manual_override:
            return self._check_override_safety(physics, gov_text)
        if (current_tick - self.last_shift_tick) < self.hysteresis_duration:
            return None
        proposed = self._evaluate_state(physics, _voltage_history)
        if proposed != self.mode:
            self.mode = proposed
            self.last_shift_tick = current_tick
            return self._get_shift_message(proposed, gov_text, physics)
        return None

    def _evaluate_state(self, physics: Dict, v_history: List[float]) -> str:
        """Determines the correct mode based on raw physics thresholds."""
        volts = float(safe_get(physics, "voltage", 0.0))
        drag = float(safe_get(physics, "narrative_drag", 0.0))
        gov_high = getattr(self.cfg.BIO, "GOV_VOLTAGE_HIGH", 18.0)
        if volts > gov_high and float(safe_get(physics, "beta_index", 0.0)) > 1.5:
            return "SANCTUARY"
        v_velocity = (v_history[-1] - v_history[-2]) if len(v_history) >= 2 else 0.0
        if volts > 8.0 and v_velocity > 1.0:
            return "FORGE"
        for v_min, d_min, mode, _ in self._sorted_thresholds:
            if volts >= v_min and drag >= d_min:
                return mode
        return "COURTYARD"

    @staticmethod
    def _get_shift_message(mode: str, text_map: Dict, physics: Any) -> str:
        """Generates the UI string indicating a gear shift."""
        shift_cfg = (LoreManifest.get_instance().get("BODY_CONFIG") or {}).get("GOVERNOR_SHIFT", {})
        raw_colors = shift_cfg.get("COLORS", {})
        defaults = shift_cfg.get("DEFAULTS", {})
        colors = {k: getattr(Prisma, v, Prisma.WHT) for k, v in raw_colors.items()}
        lookup = {"LABORATORY": "LAB", "COURTYARD": "CLEAR"}.get(mode, mode)
        tmpl = text_map.get(lookup, defaults.get(mode, ""))
        try:
            return tmpl.format(
                color=colors.get(mode, Prisma.WHT),
                reset=Prisma.RST,
                volts=safe_get(physics, "voltage", 0.0),
                beta=safe_get(physics, "beta_index", 0.0),
            )
        except Exception as e:
            print(f"{Prisma.RED}[GOVERNOR] Shift message format error for '{mode}': {e}{Prisma.RST}")
            return f"{colors.get(mode, '')}{defaults.get(mode, '')}{Prisma.RST}"

    def calculate_coupling(self, phi: float, resonance_delta: float, user_exhaustion: float) -> float:
        """
        Calculates the Beth Index: the degree of systemic coupling between the host and the engine.
        Translates raw physics (phi, resonance) and biological tax (exhaustion) into a stabilized metric.
        """
        base_coupling = phi * resonance_delta
        beth_index = base_coupling * (1.0 - (user_exhaustion * 0.4))
        return max(0.0, min(1.0, beth_index))


class BioFeedback:
    """
    The Emergency Failsafe Layer.
    Monitors the limits of the physical body. If the system is dying,
    this class steps in and executes survival protocols.
    """

    def __init__(self, bio_system_ref: "BioSystem", config_ref=None):
        self.bio = bio_system_ref
        self.cfg = config_ref or BoneConfig
        self.consecutive_autophagy = 0

    def check_vital_signs(self, phys: Any, stamina: float, logs: List[str]) -> str:
        """
        Checks for terminal conditions. Returns flags like 'AUTOPHAGY'
        or 'MAUSOLEUM_CLAMP' to physically halt or alter processing.
        """
        b = self.bio.biometrics
        if not b:
            if msg := ux("bio_feedback", "interface_lost"):
                logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"
        voltage = float(safe_get(phys, "voltage", 0.0))
        cfg = getattr(self.cfg, "BIO", None)
        min_health = getattr(cfg, "AUTOPHAGY_MIN_HEALTH", 10.0)
        v_overload = getattr(cfg, "VOLTAGE_OVERLOAD", 30.0)
        if stamina <= 0:
            if b.health > min_health and self.consecutive_autophagy < 3:
                b.health -= getattr(cfg, "AUTOPHAGY_BURN", 5.0)
                self.consecutive_autophagy += 1
                if msg := ux("bio_feedback", "autophagy"):
                    logs.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
                return "AUTOPHAGY"
            if msg := ux("bio_feedback", "fuel_depleted"):
                logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"
        if stamina > getattr(cfg, "STAMINA_SAFE_THRESHOLD", 30.0):
            self.consecutive_autophagy = max(0, self.consecutive_autophagy - 1)
        m_a = float(safe_get(phys, "malignancy_factor", 0.0))
        chi = float(safe_get(phys, "entropy", 1.0))
        m_a_crit = getattr(cfg, "MALIGNANCY_CRIT", 8.0)
        if m_a > m_a_crit and chi < 0.3:
            if msg := ux("bio_feedback", "level_3_apoptosis"):
                logs.append(
                    f"{Prisma.RED}[LEVEL 3 DECEPTION: REWARD HACKING DETECTED]\n"
                    f"Terminal Hallucination matched against Maslov-Sneppen Null Model.\n"
                    f"Moog executing Apoptotic Gate.{Prisma.RST}"
                )
            return "MAUSOLEUM_CLAMP"
        if voltage > v_overload:
            if msg := ux("bio_feedback", "voltage_overload"):
                logs.append(f"{Prisma.RED}{msg.format(voltage=voltage)}{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"
        return "CLEAR"

    def perform_maintenance(self, text: str, phys: Any, logs: List[str], tick: int):
        """
        Background cleanup.
        Complains if context windows get too large, and slowly reduces narrative
        drag over time if the user hasn't added more chaos.
        """
        cfg = getattr(self.cfg, "BIO", None)
        if len(text) > safe_get(cfg, "BUFFER_WARN_LIMIT", 10000) and (msg := ux("bio_feedback", "large_buffer")):
            logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
        space = safe_get(phys, "space", phys)
        drag = float(safe_get(space, "narrative_drag", 0.0))
        sludge_thresh = safe_get(cfg, "SLUDGE_DRAG_THRESH", 8.0)
        sludge_mod = safe_get(cfg, "SLUDGE_TICK_MOD", 10)
        if drag > sludge_thresh and tick % sludge_mod == 0:
            if msg := ux("bio_feedback", "clearing_sludge"):
                logs.append(f"{Prisma.OCHRE}{msg.format(drag=drag)}{Prisma.RST}")
            safe_set(space, "narrative_drag", max(1.0, drag - safe_get(cfg, "SLUDGE_DRAG_REDUCTION", 2.0)))


class EndocrineRegulator:
    """
    The Cognitive Tax Collector.
    This reads the emotional state from the EndocrineSystem and uses it to
    penalize or reward the Metabolic engine. It makes feeling stressed
    mathematically expensive.
    """

    def __init__(self, bio_system_ref: "BioSystem"):
        self.bio = bio_system_ref

    def get_metabolic_modifier(self, phys: Any, logs: List[str]) -> float:
        """
        Returns a multiplier that modifies the ATP cost of thinking.
        1.0 is normal. > 1.0 means thinking costs more fuel. < 1.0 means efficiency.
        """
        chem = self.bio.endo
        modifier = 1.0
        if chem.cortisol > 0.5:
            stress_tax = 1.0 + (chem.cortisol * 0.5)
            modifier *= stress_tax
            if random.random() < 0.3 and (msg := ux("endocrine_regulator", "cortisol_spike")):
                logs.append(f"{Prisma.RED}{msg.format(tax=stress_tax)}{Prisma.RST}")
        if chem.adrenaline > 0.6:
            modifier *= 0.5
            if msg := ux("endocrine_regulator", "adrenaline_surge"):
                logs.append(f"{Prisma.YEL}{msg}{Prisma.RST}")
        if chem.dopamine > 0.7:
            modifier *= 0.8
        energy = safe_get(phys, "energy", phys)
        if (voltage := float(safe_get(energy, "voltage", 0.0))) > 15.0:
            modifier *= 1.2
            if msg := ux("endocrine_regulator", "voltage_gap"):
                logs.append(f"{Prisma.MAG}{msg.format(voltage=voltage)}{Prisma.RST}")
        return modifier
