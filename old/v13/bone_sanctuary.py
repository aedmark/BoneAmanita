""" dev/bone_sanctuary.py """

import time
from bone_data import SANCTUARY
from bone_lexicon import Prisma

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
        if dt is None:
            dt = 1.0
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
            "voltage": getattr(SANCTUARY, "VOLTAGE_TARGET", 10.0),
            "drag": getattr(SANCTUARY, "DRAG_TARGET", 2.0)}
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

    def _get_val(self, p, key, default):
        if isinstance(p, dict):
            return p.get(key, default)
        return getattr(p, key, default)

    def _get_num(self, p, key, default=0.0) -> float:
        val = self._get_val(p, key, default)
        try:
            return float(val)
        except (ValueError, TypeError):
            return float(default)

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
        curr_v = self._get_num(physics_packet, "voltage")
        curr_d = self._get_num(physics_packet, "narrative_drag")
        v_force = self.voltage_pid.update(curr_v, dt=dt)
        d_force = self.drag_pid.update(curr_d, dt=dt)
        return v_force, d_force

    def assess(self, physics_packet):
        v = self._get_num(physics_packet, "voltage", 0.0)
        d = self._get_num(physics_packet, "narrative_drag", 0.0)
        t = self._get_num(physics_packet, "truth_ratio", 0.0)
        v_target = self.voltage_pid.setpoint
        d_target = self.drag_pid.setpoint
        v_tol = getattr(SANCTUARY, "VOLTAGE_TOLERANCE", 5.0) or 1.0
        d_tol = getattr(SANCTUARY, "DRAG_TOLERANCE", 2.0) or 1.0
        t_target = getattr(SANCTUARY, "TRUTH_TARGET", 0.8)
        v_dist = abs(v - v_target) / v_tol
        d_dist = abs(d - d_target) / d_tol
        t_dist = abs(t - t_target) / 0.3
        avg_dist = (v_dist + d_dist + t_dist) / 3.0
        is_safe = avg_dist < 0.5
        if is_safe:
            self.consecutive_safe_ticks += 1
            if self.consecutive_safe_ticks >= 3 and not self.in_sanctuary:
                self.in_sanctuary = True
                self.events.log(f"{getattr(SANCTUARY, 'COLOR', Prisma.GRN)}![☀️] SANCTUARY: The air is calm here.{Prisma.RST}", "SYS")
        else:
            self.consecutive_safe_ticks = 0
            self.in_sanctuary = False
        return self.in_sanctuary, avg_dist