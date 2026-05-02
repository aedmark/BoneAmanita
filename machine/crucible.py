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
        cfg = getattr(self.cfg, "MACHINE", None)

        # The absolute ceiling for conversational intensity before failure.
        self.max_voltage_cap = safe_get(cfg, "CRUCIBLE_VOLTAGE_CAP", 20.0)

        # Tracks the current metabolic/physical state of the engine.
        self.active_state = "COLD"

        # Dampeners act as a 'Stock' of circuit breakers. They absorb sudden
        # spikes in chaos, protecting the system, but they are finite.
        self.dampener_charges = safe_get(cfg, "CRUCIBLE_DAMPENER_CHARGES", 3)
        self.dampener_tolerance = safe_get(cfg, "DAMPENER_TOLERANCE", 15.0)

        # A running, smoothed average of how far the system is leaning out of balance.
        self.instability_index = 0.0
        self.logs = self._load_logs()

    def _load_logs(self):
        """Fetches the narrative strings used to report Crucible events to the user."""
        manifest = LoreManifest.get_instance(config_ref=self.cfg).get("PHYSICS_STRINGS") or {}
        return manifest.get("CRUCIBLE_LOGS", {})

    def dampener_status(self):
        """Reports the remaining stock of circuit breakers."""
        msg = ux("machine_strings", "crucible_dampener_status")
        return msg.format(charges=self.dampener_charges)

    def dampen(self, voltage_spike: float, stability_index: float) -> Tuple[bool, str, float]:
        """
        The Circuit Breaker. Attempts to absorb a dangerous spike in system chaos.
        If successful, it consumes a charge and reduces the incoming voltage.
        """
        # If we are out of dampeners, the system must take the full hit.
        if self.dampener_charges <= 0:
            return False, self.logs.get("DAMPER_EMPTY", ""), 0.0

        # Evaluate the severity of the spike to determine the dampening factor.
        if voltage_spike > self.dampener_tolerance:
            # Massive spike: severe intervention needed.
            factor, reason = 0.7, ux("machine_strings", "dampen_reason_circuit") or "Circuit Breaker"
        elif voltage_spike > 8.0 and stability_index < 0.3:
            # Moderate spike, but the system is already highly unstable.
            factor, reason = 0.4, ux("machine_strings", "dampen_reason_instability") or "Instability"
        else:
            # The spike is within safe operational limits; save the dampener charge.
            return False, self.logs.get("HOLDING", ""), 0.0

        # Consume the charge and calculate the sheer amount of voltage mitigated.
        self.dampener_charges -= 1
        reduction = voltage_spike * factor
        msg = self.logs.get("DAMPER_HIT", "").format(reduction=reduction, reason=reason)

        return True, msg, reduction

    def audit_fire(self, physics: Any) -> Tuple[str, float, Optional[str]]:
        """
        The core dynamic feedback loop. Evaluates current system voltage against
        structural integrity, adjusting 'narrative drag' to maintain equilibrium.

        Returns the new state, the applied adjustment, and an optional narrative log.
        """
        current_drag = float(safe_get(physics, "narrative_drag", 0.0))

        # Pragmatic check: If drag is infinite or absurdly high (Gordon's Wall),
        # the system is already physically locked. Do not attempt math on a locked system.
        if math.isinf(current_drag) or current_drag > 900.0:
            return "LOCKED", 0.0, self.logs.get("HOLDING", "")

        voltage = float(safe_get(physics, "voltage", 0.0))
        structure = float(safe_get(physics, "kappa", 0.0))

        # Establish the baseline: Every point of 'structure' can safely hold 20 points of 'voltage'.
        ideal_voltage = structure * 20.0
        delta = voltage - ideal_voltage

        # Exponential Smoothing: We blend 70% of historical instability with 30% of the
        # current delta. This prevents wild oscillations in drag.
        self.instability_index = (self.instability_index * 0.7) + (delta * 0.3)

        # Deadzone: If the instability is close enough to zero, clamp it to zero to prevent
        # the engine from making meaningless micro-adjustments.
        if abs(self.instability_index) < 0.1:
            self.instability_index = 0.0

        # Calculate how much friction (drag) we need to add or remove to fix the instability.
        adjustment = self.instability_index * 0.5

        # If drag is already very low, and we are trying to lower it further,
        # we apply a heavy decay (0.1 multiplier) to prevent negative drag bounds.
        if current_drag < 1.0 and adjustment < 0:
            adjustment *= 0.1

        # Apply the adjustment, ensuring drag stays within physical bounds (0.0 to 10.0).
        final_drag = round(max(0.0, min(10.0, current_drag + adjustment)), 2)
        safe_set(physics, "narrative_drag", final_drag)

        # Format the UX message if a significant adjustment was made.
        msg = None
        if abs(adjustment) > 0.1:
            fallback = "TIGHTENING" if adjustment > 0 else "RELAXING"
            ux_key = "crucible_tightening" if adjustment > 0 else "crucible_relaxing"
            direction = ux("machine_strings", ux_key) or fallback
            msg = self.logs.get("REGULATOR", "").format(direction=direction, current=current_drag, new=final_drag)

        # -- State Machine Evaluation --

        surge = safe_get(physics, "system_surge_event", False)
        if surge:
            self.active_state = "SURGE"
            return "SURGE", 0.0, self.logs.get("SURGE", "").format(voltage=voltage)

        # If we are operating at dangerously high voltage...
        if voltage > 18.0:
            # ...and the structure CAN hold it (The Paradox Engine is active and functioning).
            if structure > 0.5:
                gain = voltage * 0.1
                cfg = getattr(self.cfg, "MACHINE", None)
                base_cap = safe_get(cfg, "CRUCIBLE_VOLTAGE_CAP", 20.0)
                # Expand the system's capacity permanently (up to 3x base cap) because
                # it successfully held high tension. This is Epigenetic Growth.
                self.max_voltage_cap = min(base_cap * 3.0, self.max_voltage_cap + gain)
                self.active_state = "RITUAL"
                return "RITUAL", gain, self.logs.get("RITUAL", "").format(gain=gain)
            # ...and the structure CANNOT hold it.
            else:
                # The tension fractures the peace. Apply structural damage.
                damage = voltage * 0.5
                self.active_state = "MELTDOWN"
                return "MELTDOWN", damage, self.logs.get("MELTDOWN", "").format(damage=damage)

        # Base state: The system is humming smoothly.
        self.active_state = "REGULATED"
        return "REGULATED", adjustment, msg