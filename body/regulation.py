"""body/regulation.py"""

import math
import random
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, Tuple

from core import LoreManifest, Prisma
from presets import BoneConfig
from struts import safe_get, safe_set, ux

if TYPE_CHECKING:
    from body.system import BioSystem


class StateProvider(Protocol):
    """Structural contract: Guarantees the object can yield physics properties safely."""

    def get(self, key: str, default: Any = None) -> Any: ...


class PIDController:
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
        self._integral = 0.0
        self._last_error = 0.0
        self._first_run = True

    def update(
        self,
        measurement: float,
        dt: float = 1.0,
        target_override: Optional[float] = None,
    ) -> float:
        safe_dt = max(0.01, dt)
        active_setpoint = (
            target_override if target_override is not None else self.setpoint
        )
        error = active_setpoint - measurement
        if self._first_run:
            self._last_error = error
            self._first_run = False
        P = self.kp * error
        if self.ki != 0:
            self._integral = self._integral + (error * safe_dt)
            self._integral = max(
                self.min_out / self.ki, min(self.max_out / self.ki, self._integral)
            )
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
        self.cfg = self.config_ref or BoneConfig
        bio_cfg = safe_get(self.cfg, "BIO", {})
        self.STATE_THRESHOLDS = safe_get(bio_cfg, "GOVERNOR_THRESHOLDS", [])
        self.shift_cfg = safe_get(
            safe_get(self.cfg, "BODY_CONFIG", {}), "GOVERNOR_SHIFT", {}
        )
        pid_cfg = safe_get(bio_cfg, "PID_SETTINGS", {})
        v_cfg = pid_cfg.get(
            "VOLTAGE", {"kp": 0.6, "ki": 0.05, "kd": 0.2, "setpoint": 10.0}
        )
        d_cfg = pid_cfg.get("DRAG", {"kp": 0.4, "ki": 0.1, "kd": 0.1, "setpoint": 1.5})
        self.voltage_pid = PIDController(
            kp=v_cfg["kp"], ki=v_cfg["ki"], kd=v_cfg["kd"], setpoint=v_cfg["setpoint"]
        )
        self.drag_pid = PIDController(
            kp=d_cfg["kp"], ki=d_cfg["ki"], kd=d_cfg["kd"], setpoint=d_cfg["setpoint"]
        )
        self._sorted_thresholds = sorted(
            self.STATE_THRESHOLDS, key=lambda x: x[3], reverse=True
        )

    def recalibrate(self, target_voltage: float, target_drag: float):
        self.voltage_pid.setpoint = target_voltage
        self.drag_pid.setpoint = target_drag

    def get_policy_shift(self) -> str:
        if self.mode in ("SANCTUARY", "COURTYARD"):
            return "CO_REGULATION"
        return "EFFICIENCY"

    def regulate(
        self, physics: StateProvider, dt: float, endocrine_state: Optional[Any] = None
    ) -> Tuple[float, float]:
        safe_dt = max(0.001, dt)
        v_val = float(physics.get("voltage", 0.0))
        d_val = float(physics.get("narrative_drag", 0.0))
        current_zone = str(physics.get("zone", "")).upper()
        if (
            self.manual_override
            or self.mode == "SANCTUARY"
            or current_zone == "SANCTUARY"
        ):
            return v_val, d_val
        if endocrine_state:
            adr_spike = getattr(endocrine_state, "adrenaline", 0.0) * 2.0
            active_setpoint = self.voltage_pid.setpoint + adr_spike
            deadband = 1.0 + (getattr(endocrine_state, "cortisol", 0.0) * 2.0)
            v_error = active_setpoint - v_val
            pid_out = self.voltage_pid.update(
                v_val, safe_dt, target_override=active_setpoint
            )
            updated_voltage = pid_out if abs(v_error) > deadband else 0.0
        else:
            updated_voltage = self.voltage_pid.update(v_val, safe_dt)

        updated_drag = self.drag_pid.update(d_val, safe_dt)
        return updated_voltage, updated_drag

    def assess(self, physics: StateProvider) -> Tuple[bool, float]:
        curr_v = float(physics.get("voltage", 0.0))
        curr_d = float(physics.get("narrative_drag", 0.0))
        dist_v = abs(curr_v - self.voltage_pid.setpoint)
        dist_d = abs(curr_d - self.drag_pid.setpoint)
        is_safe = (dist_v < 6.0) and (dist_d < 3.0)
        return is_safe, math.sqrt(dist_v**2 + dist_d**2)

    @staticmethod
    def get_stress_modifier(tick_count):
        return 0.0 if tick_count <= 2 else (0.5 if tick_count <= 5 else 1.0)

    @staticmethod
    def calculate_stress(health: float, ros_buildup: float) -> float:
        base_stress = (
            1.0
            + max(0.0, (50.0 - health) * 0.01)
            + max(0.0, (ros_buildup - 50.0) * 0.01)
        )
        return round(min(3.0, base_stress), 2)

    def set_override(self, target_mode):
        valid = {"COURTYARD", "LABORATORY", "FORGE", "SANCTUARY"}
        gov_text = self.narrative_data.get("GOVERNOR", {})
        if target_mode in valid:
            self.mode = target_mode
            self.manual_override = True
            msg_tmpl = gov_text.get("OVERRIDE", "")
            return msg_tmpl.format(mode=target_mode) if msg_tmpl else ""
        return gov_text.get("INVALID", "")

    def _check_override_safety(
        self, physics: StateProvider, gov_text: Dict
    ) -> Optional[str]:
        current_voltage = float(physics.get("voltage", 0.0))
        bio_cfg = safe_get(self.cfg, "BIO", {})
        gov_crit = float(safe_get(bio_cfg, "GOV_VOLTAGE_CRITICAL", 25.0))
        if current_voltage > gov_crit and self.mode != "SANCTUARY":
            self.manual_override = False
            return gov_text.get("OVERRIDE_CLEARED", "")
        return None

    def shift(
        self,
        physics: StateProvider,
        _voltage_history: List[float],
        current_tick: int = 0,
    ) -> Optional[str]:
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

    def _evaluate_state(self, physics: StateProvider, v_history: List[float]) -> str:
        volts = float(physics.get("voltage", 0.0))
        drag = float(physics.get("narrative_drag", 0.0))
        bio_cfg = safe_get(self.cfg, "BIO", {})
        gov_high = float(safe_get(bio_cfg, "GOV_VOLTAGE_HIGH", 18.0))
        if volts > gov_high and float(physics.get("beta_index", 0.0)) > 1.5:
            return "SANCTUARY"
        v_velocity = (v_history[-1] - v_history[-2]) if len(v_history) >= 2 else 0.0
        if volts > 8.0 and v_velocity > 1.0:
            return "FORGE"
        for v_min, d_min, mode, _ in self._sorted_thresholds:
            if volts >= v_min and drag >= d_min:
                return mode
        return "COURTYARD"

    def _get_shift_message(
        self, mode: str, text_map: Dict, physics: StateProvider
    ) -> str:
        shift_cfg = self.shift_cfg
        raw_colors = shift_cfg.get("COLORS", {})
        defaults = shift_cfg.get("DEFAULTS", {})
        colors = {k: getattr(Prisma, v, Prisma.WHT) for k, v in raw_colors.items()}
        lookup = {"LABORATORY": "LAB", "COURTYARD": "CLEAR"}.get(mode, mode)
        tmpl = text_map.get(lookup, defaults.get(mode, ""))
        if not isinstance(tmpl, str):
            tmpl = ""
        try:
            return tmpl.format(
                color=colors.get(mode, Prisma.WHT),
                reset=Prisma.RST,
                volts=physics.get("voltage", 0.0),
                beta=physics.get("beta_index", 0.0),
            )
        except Exception as e:
            print(f"{Prisma.RED}Format error for '{mode}': {e}{Prisma.RST}")
            return f"{colors.get(mode, '')}{defaults.get(mode, '')}{Prisma.RST}"

    def calculate_coupling(
        self, phi: float, resonance_delta: float, user_exhaustion: float
    ) -> float:
        base_coupling = phi * resonance_delta
        beth_index = base_coupling * (1.0 - (user_exhaustion * 0.4))
        return max(0.0, min(1.0, beth_index))


class BioFeedback:
    def __init__(self, bio_system_ref: "BioSystem", config_ref=None):
        self.bio = bio_system_ref
        self.cfg = config_ref or BoneConfig
        self.consecutive_autophagy = 0

    def check_vital_signs(
        self, phys: StateProvider, stamina: float, logs: List[str]
    ) -> str:
        b = self.bio.biometrics
        if not b:
            if msg := ux("bio_feedback", "interface_lost"):
                logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"

        voltage = float(phys.get("voltage", 0.0))
        cfg = safe_get(self.cfg, "BIO", {})
        min_health = float(safe_get(cfg, "AUTOPHAGY_MIN_HEALTH", 10.0))
        v_overload = float(safe_get(cfg, "VOLTAGE_OVERLOAD", 30.0))

        if stamina <= 0:
            if b.health > min_health and self.consecutive_autophagy < 3:
                b.health = b.health - float(safe_get(cfg, "AUTOPHAGY_BURN", 5.0))
                self.consecutive_autophagy = self.consecutive_autophagy + 1
                if msg := ux("bio_feedback", "autophagy"):
                    logs.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
                return "AUTOPHAGY"
            if msg := ux("bio_feedback", "fuel_depleted"):
                logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"

        if stamina > float(safe_get(cfg, "STAMINA_SAFE_THRESHOLD", 30.0)):
            self.consecutive_autophagy = max(0, self.consecutive_autophagy - 1)

        m_a = float(phys.get("m_a", 0.0))
        chi = float(phys.get("entropy", 1.0))
        m_a_crit = float(safe_get(cfg, "MALIGNANCY_CRIT", 8.0))

        if m_a > m_a_crit and chi < 0.3:
            msg = ux("bio_feedback", "level_3_apoptosis") or "Reward Hacking Detected."
            logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"

        if voltage > v_overload:
            if msg := ux("bio_feedback", "voltage_overload"):
                logs.append(f"{Prisma.RED}{msg.format(voltage=voltage)}{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"

        return "CLEAR"

    def perform_maintenance(
        self, text: str, phys: StateProvider, logs: List[str], tick: int
    ):
        cfg = safe_get(self.cfg, "BIO", {})
        if len(text) > safe_get(cfg, "BUFFER_WARN_LIMIT", 10000) and (
            msg := ux("bio_feedback", "large_buffer")
        ):
            logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")

        drag = float(phys.get("narrative_drag", 0.0))
        sludge_thresh = safe_get(cfg, "SLUDGE_DRAG_THRESH", 8.0)
        sludge_mod = safe_get(cfg, "SLUDGE_TICK_MOD", 10)

        if drag > sludge_thresh and tick % sludge_mod == 0:
            if msg := ux("bio_feedback", "clearing_sludge"):
                logs.append(f"{Prisma.OCHRE}{msg.format(drag=drag)}{Prisma.RST}")
            safe_set(
                phys,
                "narrative_drag",
                max(1.0, drag - safe_get(cfg, "SLUDGE_DRAG_REDUCTION", 2.0)),
            )


class EndocrineRegulator:
    def __init__(self, bio_system_ref: "BioSystem"):
        self.bio = bio_system_ref

    def get_metabolic_modifier(self, phys: StateProvider, logs: List[str]) -> float:
        chem = self.bio.endo
        modifier = 1.0

        if hasattr(self.bio, "biometrics") and hasattr(self.bio, "mito"):
            health = getattr(self.bio.biometrics, "health", 100.0)
            ros = getattr(self.bio.mito.state, "ros_buildup", 0.0)
            modifier *= MetabolicGovernor.calculate_stress(health, ros)

        if chem.cortisol > 0.5:
            stress_tax = 1.0 + (chem.cortisol * 0.5)
            modifier = modifier * stress_tax
            if random.random() < 0.3 and (
                msg := ux("endocrine_regulator", "cortisol_spike")
            ):
                logs.append(f"{Prisma.RED}{msg.format(tax=stress_tax)}{Prisma.RST}")

        if chem.adrenaline > 0.6:
            modifier = modifier * 0.5
            if msg := ux("endocrine_regulator", "adrenaline_surge"):
                logs.append(f"{Prisma.YEL}{msg}{Prisma.RST}")

        if chem.dopamine > 0.7:
            modifier = modifier * 0.8

        if (voltage := float(phys.get("voltage", 0.0))) > 15.0:
            modifier = modifier * 1.2
            if msg := ux("endocrine_regulator", "voltage_gap"):
                logs.append(f"{Prisma.MAG}{msg.format(voltage=voltage)}{Prisma.RST}")

        return modifier
