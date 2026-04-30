"""machine/theremin.py"""

from typing import Tuple, Optional, Any
from core import LoreManifest
from struts import ux, safe_get, safe_set
from presets import BoneConfig

class TheTheremin:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.decoherence_buildup = 0.0
        self.classical_turns = 0
        cfg = getattr(self.cfg, "MACHINE", None)
        self.AMBER_THRESHOLD = safe_get(cfg, "THEREMIN_AMBER_THRESHOLD", 20.0)
        self.SHATTER_POINT = safe_get(cfg, "THEREMIN_SHATTER_POINT", 100.0)
        self.is_stuck = False
        self.logs = self._load_logs()

    def _load_logs(self):
        manifest = LoreManifest.get_instance(config_ref=self.cfg).get("PHYSICS_STRINGS") or {}
        return manifest.get("THEREMIN_LOGS", {})

    def listen(self, physics: Any, governor_mode="COURTYARD") -> Tuple[bool, float, Optional[str], Optional[str]]:
        counts = safe_get(physics, "counts", {})
        voltage = float(safe_get(physics, "voltage", 0.0))
        turb = float(safe_get(physics, "turbulence", 0.0))
        rep = float(safe_get(physics, "repetition", 0.0))
        complexity = float(safe_get(physics, "truth_ratio", 0.0))
        ancient_mass = counts.get("heavy", 0) + counts.get("thermal", 0) + counts.get("cryo", 0)
        modern_mass = counts.get("abstract", 0)
        raw_mix = min(ancient_mass, modern_mass)
        resin_flow = raw_mix * 2.0
        if governor_mode == "LABORATORY":
            resin_flow *= 0.5
        if voltage > 5.0:
            resin_flow = max(0.0, resin_flow - (voltage * 0.6))
        thermal_hits = counts.get("thermal", 0)
        theremin_msg = ""
        cfg = getattr(self.cfg, "MACHINE", None)
        melt_thresh = safe_get(cfg, "THEREMIN_MELT_THRESHOLD", 5.0)
        critical_event = None
        if thermal_hits > 0 and self.decoherence_buildup > melt_thresh:
            dissolved = thermal_hits * 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - dissolved)
            self.classical_turns = 0
            theremin_msg = self.logs.get("MELT", "").format(val=dissolved) + " "
        if rep > 0.5:
            self.classical_turns += 1
            slag = self.classical_turns * 2.0
            self.decoherence_buildup += slag
            theremin_msg += self.logs.get("CALCIFY", "").format(turns=self.classical_turns, val=slag)
        elif complexity > 0.4 and self.classical_turns > 0:
            self.classical_turns = 0
            relief = 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - relief)
            theremin_msg += self.logs.get("SHATTER", "").format(val=relief)
        elif resin_flow > 0.5:
            self.decoherence_buildup += resin_flow
            theremin_msg += self.logs.get("RESIN", "").format(val=resin_flow)
        theremin_msg = theremin_msg.strip()
        if turb > 0.6 and self.decoherence_buildup > 0:
            shatter_amt = turb * 10.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - shatter_amt)
            turb_msg = self.logs.get("TURBULENCE", "").format(val=shatter_amt)
            theremin_msg = f"{theremin_msg} {turb_msg}".strip()
            self.classical_turns = 0
        if turb < 0.2:
            current_drag = float(safe_get(physics, "narrative_drag", 0.0))
            safe_set(physics, "narrative_drag", max(0.0, current_drag - 1.0))
        if self.decoherence_buildup > self.SHATTER_POINT:
            self.decoherence_buildup = 0.0
            self.classical_turns = 0
            self.is_stuck = False
            current_drag = float(safe_get(physics, "narrative_drag", 0.0))
            safe_set(physics, "narrative_drag", max(current_drag + 20.0, 20.0))
            safe_set(physics, "voltage", 0.0)
            return False, resin_flow, self.logs.get("COLLAPSE", ""), "AIRSTRIKE"
        if self.classical_turns > 3:
            critical_event = "CORROSION"
            theremin_msg += ux('machine_strings', 'theremin_corrosion') or ''
        if self.decoherence_buildup > self.AMBER_THRESHOLD:
            self.is_stuck = True
            theremin_msg += ux('machine_strings', 'theremin_stuck') or ''
        elif self.is_stuck and self.decoherence_buildup < 5.0:
            self.is_stuck = False
            theremin_msg += ux('machine_strings', 'theremin_free') or ''
        return self.is_stuck, resin_flow, theremin_msg, critical_event

    def get_readout(self):
        status = "STUCK" if self.is_stuck else "FLOW"
        msg = ux("machine_strings", "theremin_readout")
        return msg.format(resin=self.decoherence_buildup, status=status)