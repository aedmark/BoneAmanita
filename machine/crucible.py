"""machine/crucible.py
The Crucible is the thermal regulator and safety valve of the physics engine.
It monitors the relationship between conversational intensity ('voltage') and
logical coherence ('kappa' or structure).
Its primary function is to dynamically apply 'narrative drag' (friction)
to prevent the system from entering a terminal hallucination or sycophantic loop.
"""
import math
from typing import Tuple, Optional, Any
from core import LoreManifest
from struts import ux, safe_get, safe_set
from presets import BoneConfig


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
        """Reports the remaining stock of circuit breakers."""
        msg = ux("machine_strings", "crucible_dampener_status") or "Crucible Dampeners available: {charges}"
        return msg.format(charges=self.dampener_charges)

    def dampen(self, voltage_spike: float, stability_index: float) -> Tuple[bool, str, float]:
        """
        The Circuit Breaker. Attempts to absorb a dangerous spike in system chaos.
        If successful, it consumes a charge and reduces the incoming voltage.
        """
        if self.dampener_charges <= 0:
            return False, ux("physics_strings", "crucible_damper_empty") or "", 0.0
        if voltage_spike > self.dampener_tolerance:
            factor, reason = 0.7, ux("machine_strings", "dampen_reason_circuit") or "Circuit Breaker"
        elif voltage_spike > 8.0 and stability_index < 0.3:
            factor, reason = 0.4, ux("machine_strings", "dampen_reason_instability") or "Instability"
        else:
            return False, ux("physics_strings", "crucible_holding") or "", 0.0

        self.dampener_charges -= 1
        reduction = voltage_spike * factor
        msg_template = ux("physics_strings", "crucible_damper_hit") or "[CRUCIBLE]: Absorbed -{reduction:.1f} Voltage. Reason: {reason}"
        msg = msg_template.format(reduction=reduction, reason=reason)
        return True, msg, reduction

    def audit_fire(self, physics: Any) -> Tuple[str, float, Optional[str]]:
        """
        The core dynamic feedback loop. Evaluates current system voltage against
        structural integrity, adjusting 'narrative drag' to maintain equilibrium.
        Returns the new state, the applied adjustment, and an optional narrative log.
        """
        current_drag = float(safe_get(physics, "narrative_drag", 0.0))
        if math.isinf(current_drag) or current_drag > 900.0:
            return "LOCKED", 0.0, ux("physics_strings", "crucible_holding") or ""

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
            template = ux("physics_strings", "crucible_regulator") or "[REGULATOR]: {direction} | Drag: {current:.1f} -> {new:.1f}"
            msg = template.format(direction=direction, current=current_drag, new=final_drag)

        surge = safe_get(physics, "system_surge_event", False)
        if surge:
            self.active_state = "SURGE"
            msg_template = ux("physics_strings", "crucible_surge") or "[SURGE]: Voltage spike detected ({voltage:.1f})."
            return "SURGE", 0.0, msg_template.format(voltage=voltage)

        if voltage > 18.0:
            if structure > 0.5:
                gain = voltage * 0.1
                cfg = safe_get(self.cfg, "MACHINE", {})
                base_cap = float(safe_get(cfg, "CRUCIBLE_VOLTAGE_CAP", 20.0))
                self.max_voltage_cap = min(base_cap * 3.0, self.max_voltage_cap + gain)
                self.active_state = "RITUAL"
                msg_template = ux("physics_strings", "crucible_ritual") or "[RITUAL]: High tension converted to capacity. (+{gain:.1f} Cap)"
                return "RITUAL", gain, msg_template.format(gain=gain)
            else:
                damage = voltage * 0.5
                self.active_state = "MELTDOWN"
                msg_template = ux("physics_strings", "crucible_meltdown") or "[MELTDOWN]: Structure failing under voltage. ({damage:.1f} Damage)"
                return "MELTDOWN", damage, msg_template.format(damage=damage)

        self.active_state = "REGULATED"
        return "REGULATED", adjustment, msg
