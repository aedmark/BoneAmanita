"""machine/cruicble.py"""

import math
from typing import Tuple, Optional, Any
from core import LoreManifest
from struts import ux, safe_get, safe_set
from presets import BoneConfig

class TheCrucible:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg = getattr(self.cfg, "MACHINE", None)
        self.max_voltage_cap = safe_get(cfg, "CRUCIBLE_VOLTAGE_CAP", 20.0)
        self.active_state = "COLD"
        self.dampener_charges = safe_get(cfg, "CRUCIBLE_DAMPENER_CHARGES", 3)
        self.dampener_tolerance = safe_get(cfg, "DAMPENER_TOLERANCE", 15.0)
        self.instability_index = 0.0
        self.logs = self._load_logs()

    def _load_logs(self):
        manifest = LoreManifest.get_instance(config_ref=self.cfg).get("PHYSICS_STRINGS") or {}
        return manifest.get("CRUCIBLE_LOGS", {})

    def dampener_status(self):
        msg = ux("machine_strings", "crucible_dampener_status")
        return msg.format(charges=self.dampener_charges)

    def dampen(self, voltage_spike: float, stability_index: float) -> Tuple[bool, str, float]:
        if self.dampener_charges <= 0:
            return False, self.logs.get("DAMPER_EMPTY", ""), 0.0
        if voltage_spike > self.dampener_tolerance:
            factor, reason = 0.7, ux("machine_strings", "dampen_reason_circuit") or "Circuit Breaker"
        elif voltage_spike > 8.0 and stability_index < 0.3:
            factor, reason = 0.4, ux("machine_strings", "dampen_reason_instability") or "Instability"
        else:
            return False, self.logs.get("HOLDING", ""), 0.0
        self.dampener_charges -= 1
        reduction = voltage_spike * factor
        msg = self.logs.get("DAMPER_HIT", "").format(reduction=reduction, reason=reason)
        return True, msg, reduction

    def audit_fire(self, physics: Any) -> Tuple[str, float, Optional[str]]:
        current_drag = float(safe_get(physics, "narrative_drag", 0.0))
        if math.isinf(current_drag) or current_drag > 900.0:
            return "LOCKED", 0.0, self.logs.get("HOLDING", "")
        voltage = float(safe_get(physics, "voltage", 0.0))
        structure = float(safe_get(physics, "kappa", 0.0))
        ideal_voltage = structure * 20.0
        delta = voltage - ideal_voltage
        self.instability_index = (self.instability_index * 0.7) + (delta * 0.3)
        if abs(self.instability_index) < 0.1:
            self.instability_index = 0.0
        adjustment = self.instability_index * 0.5
        if current_drag < 1.0 and adjustment < 0:
            adjustment *= 0.1
        final_drag = round(max(0.0, min(10.0, current_drag + adjustment)), 2)
        safe_set(physics, "narrative_drag", final_drag)
        msg = None
        if abs(adjustment) > 0.1:
            fallback = "TIGHTENING" if adjustment > 0 else "RELAXING"
            ux_key = "crucible_tightening" if adjustment > 0 else "crucible_relaxing"
            direction = ux("machine_strings", ux_key) or fallback
            msg = self.logs.get("REGULATOR", "").format(direction=direction, current=current_drag, new=final_drag)
        surge = safe_get(physics, "system_surge_event", False)
        if surge:
            self.active_state = "SURGE"
            return "SURGE", 0.0, self.logs.get("SURGE", "").format(voltage=voltage)
        if voltage > 18.0:
            if structure > 0.5:
                gain = voltage * 0.1
                cfg = getattr(self.cfg, "MACHINE", None)
                base_cap = safe_get(cfg, "CRUCIBLE_VOLTAGE_CAP", 20.0)
                self.max_voltage_cap = min(base_cap * 3.0, self.max_voltage_cap + gain)
                self.active_state = "RITUAL"
                return "RITUAL", gain, self.logs.get("RITUAL", "").format(gain=gain)
            else:
                damage = voltage * 0.5
                self.active_state = "MELTDOWN"
                return "MELTDOWN", damage, self.logs.get("MELTDOWN", "").format(damage=damage)
        self.active_state = "REGULATED"
        return "REGULATED", adjustment, msg