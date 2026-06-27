"""machine/crucible.py"""

import math
from typing import Optional, Tuple

from presets import BoneConfig
from struts import safe_get, ux, ux_format


class TheCrucible:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg = safe_get(self.cfg, "MACHINE", {})
        self.max_voltage_cap = float(safe_get(cfg, "CRUCIBLE_VOLTAGE_CAP", 20.0))
        self.active_state = "COLD"
        self.dampener_charges = int(safe_get(cfg, "CRUCIBLE_DAMPENER_CHARGES", 3))
        self.dampener_tolerance = float(safe_get(cfg, "DAMPENER_TOLERANCE", 15.0))
        self.instability_index = 0.0

    def dampener_status(self):
        msg = (
            ux("machine_strings", "crucible_dampener_status")
            or "Crucible Dampeners available: {charges}"
        )
        return msg.format(charges=self.dampener_charges)

    def dampen(
        self, voltage_spike: float, stability_index: float
    ) -> Tuple[bool, str, float]:
        if self.dampener_charges <= 0:
            return False, ux("physics_strings", "crucible_damper_empty") or "", 0.0
        if voltage_spike > self.dampener_tolerance:
            factor, reason = (
                0.7,
                ux("machine_strings", "dampen_reason_circuit") or "Circuit Breaker",
            )
        elif voltage_spike > 8.0 and stability_index < 0.3:
            factor, reason = (
                0.4,
                ux("machine_strings", "dampen_reason_instability") or "Instability",
            )
        else:
            return False, ux("physics_strings", "crucible_holding") or "", 0.0
        self.dampener_charges -= 1
        reduction = voltage_spike * factor
        msg_template = (
            ux("physics_strings", "crucible_damper_hit")
            or "Absorbed -{reduction:.1f} Voltage because {reason}"
        )
        msg = msg_template.format(reduction=reduction, reason=reason)
        return True, msg, reduction

    def audit_fire(self, physics: dict) -> Tuple[str, float, Optional[str]]:
        current_drag = float(physics.get("narrative_drag", 0.0))
        if math.isinf(current_drag) or current_drag > 900.0:
            return "LOCKED", 0.0, ux("physics_strings", "crucible_holding") or ""
        voltage = float(physics.get("voltage", 0.0))
        structure = float(physics.get("kappa", 0.0))
        ideal_voltage = structure * 20.0
        delta = voltage - ideal_voltage
        self.instability_index = (self.instability_index * 0.7) + (delta * 0.3)
        if abs(self.instability_index) < 0.1:
            self.instability_index = 0.0
        adjustment = self.instability_index * 0.5
        if current_drag < 1.0 and adjustment < 0:
            adjustment *= 0.1
        final_drag = round(max(0.0, min(10.0, current_drag + adjustment)), 2)
        physics["narrative_drag"] = final_drag
        msg = None
        if abs(adjustment) > 0.1:
            is_tight = adjustment > 0
            direction = ux(
                "machine_strings",
                "crucible_tightening" if is_tight else "crucible_relaxing",
            ) or ("TIGHTENING" if is_tight else "RELAXING")
            msg = ux_format(
                "physics_strings",
                "crucible_regulator",
                default="{direction} | Drag: {current:.1f} -> {new:.1f}",
                direction=direction,
                current=current_drag,
                new=final_drag,
            )
        surge = physics.get("system_surge_event", False)
        if surge:
            self.active_state = "SURGE"
            msg = ux_format(
                "physics_strings",
                "crucible_surge",
                default="Voltage spike detected ({voltage:.1f}).",
                voltage=voltage,
            )
            return "SURGE", 0.0, msg
        if voltage > 18.0:
            if structure > 0.5:
                gain = voltage * 0.1
                cfg = safe_get(self.cfg, "MACHINE", {})
                base_cap = float(safe_get(cfg, "CRUCIBLE_VOLTAGE_CAP", 20.0))
                self.max_voltage_cap = min(base_cap * 3.0, self.max_voltage_cap + gain)
                self.active_state = "RITUAL"
                msg = ux_format(
                    "physics_strings",
                    "crucible_ritual",
                    default="High tension converted to capacity. (+{gain:.1f} Cap)",
                    gain=gain,
                )
                return "RITUAL", gain, msg
            else:
                damage = voltage * 0.5
                self.active_state = "MELTDOWN"
                msg = ux_format(
                    "physics_strings",
                    "crucible_meltdown",
                    default="Structure failing under voltage. ({damage:.1f} Damage)",
                    damage=damage,
                )
                return "MELTDOWN", damage, msg
        self.active_state = "REGULATED"
        return "REGULATED", adjustment, msg
