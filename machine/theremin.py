"""machine/theremin.py"""

from typing import Optional, Tuple

from core import LoreManifest
from presets import BoneConfig
from struts import safe_get, ux


class TheTheremin:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.decoherence_buildup = 0.0
        self.classical_turns = 0
        cfg = safe_get(self.cfg, "MACHINE", {})
        self.AMBER_THRESHOLD = float(safe_get(cfg, "THEREMIN_AMBER_THRESHOLD", 20.0))
        self.SHATTER_POINT = float(safe_get(cfg, "THEREMIN_SHATTER_POINT", 100.0))
        self.is_stuck = False
        self.logs = self._load_logs()

    def _load_logs(self):
        manifest = (
            LoreManifest.get_instance(config_ref=self.cfg).get("PHYSICS_STRINGS") or {}
        )
        return manifest.get("THEREMIN_LOGS", {})

    def listen(
        self, physics: dict, governor_mode: str = "COURTYARD"
    ) -> Tuple[bool, float, Optional[str], Optional[str]]:
        counts = physics.get("counts", {})
        voltage = float(physics.get("voltage", 0.0))
        turb = float(physics.get("turbulence", 0.0))
        rep = float(physics.get("repetition", 0.0))
        complexity = float(physics.get("truth_ratio", 0.0))
        ancient_mass = (
            float(counts.get("heavy", 0))
            + float(counts.get("thermal", 0))
            + float(counts.get("cryo", 0))
        )
        modern_mass = float(counts.get("abstract", 0))
        raw_mix = min(ancient_mass, modern_mass)
        resin_flow = raw_mix * 2.0
        if governor_mode == "LABORATORY":
            resin_flow *= 0.5
        if voltage > 5.0:
            resin_flow = max(0.0, resin_flow - (voltage * 0.6))
        thermal_hits = counts.get("thermal", 0)
        msg_parts = []
        cfg = safe_get(self.cfg, "MACHINE", {})
        melt_thresh = float(safe_get(cfg, "THEREMIN_MELT_THRESHOLD", 5.0))
        critical_event = None
        if thermal_hits > 0 and self.decoherence_buildup > melt_thresh:
            dissolved = thermal_hits * 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - dissolved)
            self.classical_turns = 0
            msg_parts.append(self.logs.get("MELT", "").format(val=dissolved))
        if rep > 0.5:
            self.classical_turns += 1
            slag = self.classical_turns * 2.0
            self.decoherence_buildup += slag
            msg_parts.append(
                self.logs.get("CALCIFY", "").format(
                    turns=self.classical_turns, val=slag
                )
            )
        elif complexity > 0.4 and self.classical_turns > 0:
            self.classical_turns = 0
            relief = 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - relief)
            msg_parts.append(self.logs.get("SHATTER", "").format(val=relief))
        elif resin_flow > 0.5:
            self.decoherence_buildup += resin_flow
            msg_parts.append(self.logs.get("RESIN", "").format(val=resin_flow))
        if turb > 0.6 and self.decoherence_buildup > 0:
            shatter_amt = turb * 10.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - shatter_amt)
            msg_parts.append(self.logs.get("TURBULENCE", "").format(val=shatter_amt))
            self.classical_turns = 0
        elif turb < 0.2:
            current_drag = float(physics.get("narrative_drag", 0.0))
            physics["narrative_drag"] = max(0.0, current_drag - 1.0)
        if self.decoherence_buildup > self.SHATTER_POINT:
            self.decoherence_buildup = 0.0
            self.classical_turns = 0
            self.is_stuck = False
            current_drag = float(physics.get("narrative_drag", 0.0))
            physics["narrative_drag"] = max(current_drag + 20.0, 20.0)
            physics["voltage"] = 0.0
            return False, resin_flow, self.logs.get("COLLAPSE", ""), "AIRSTRIKE"
        if self.classical_turns > 3:
            critical_event = "CORROSION"
            msg_parts.append(ux("machine_strings", "theremin_corrosion") or "")
        if self.decoherence_buildup > self.AMBER_THRESHOLD:
            self.is_stuck = True
            msg_parts.append(ux("machine_strings", "theremin_stuck") or "")
        elif self.is_stuck and self.decoherence_buildup < 5.0:
            self.is_stuck = False
            msg_parts.append(ux("machine_strings", "theremin_free") or "")
        theremin_msg = " ".join(filter(None, msg_parts)).strip()
        return self.is_stuck, resin_flow, theremin_msg, critical_event

    def get_readout(self):
        status = "STUCK" if self.is_stuck else "FLOW"
        msg = ux("machine_strings", "theremin_readout")
        return msg.format(resin=self.decoherence_buildup, status=status)
