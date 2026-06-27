"""protocols/therapy.py"""

from typing import Any, Dict

from presets import BoneConfig
from struts import safe_get


class TherapyProtocol:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        default_vector = {"SEPTIC": 0, "EXHAUSTION": 0, "PARANOIA": 0}
        raw_vector = safe_get(self.cfg, "TRAUMA_VECTOR", default_vector)
        vector_keys = (
            raw_vector.keys() if isinstance(raw_vector, dict) else default_vector.keys()
        )
        self.streaks = {k: 0 for k in vector_keys}
        cfg = safe_get(self.cfg, "THERAPY", {})
        self.HEALING_THRESHOLD = int(safe_get(cfg, "HEALING_THRESHOLD", 5))

    def to_dict(self) -> Dict[str, Any]:
        return {"streaks": self.streaks}

    def load_state(self, data: Dict[str, Any]):
        self.streaks = data.get(
            "streaks", {k: 0 for k in self.cfg.TRAUMA_VECTOR.keys()}
        )

    def check_progress(self, phys, _stamina, current_trauma_accum, _qualia=None):
        matter = safe_get(phys, "matter", {}) or {}
        counts = safe_get(phys, "counts", safe_get(matter, "counts", {}))
        vector = safe_get(phys, "vector", safe_get(matter, "vector", {}))
        cfg_therapy = safe_get(self.cfg, "THERAPY", {})
        str_req = float(safe_get(cfg_therapy, "STRENGTH_REQ", 0.3))
        t_reduct = float(safe_get(cfg_therapy, "TRAUMA_REDUCTION", 0.5))
        healed_types = []
        is_clean = counts.get("toxin", 0) == 0
        has_strength = vector.get("STR", 0.0) > str_req
        self.streaks["SEPTIC"] = (
            (self.streaks["SEPTIC"] + 1) if (is_clean and has_strength) else 0
        )
        for trauma_type, streak in self.streaks.items():
            if streak >= self.HEALING_THRESHOLD:
                self.streaks[trauma_type] = 0
                if current_trauma_accum.get(trauma_type, 0.0) > 0.0:
                    current_trauma_accum[trauma_type] = max(
                        0.0, current_trauma_accum[trauma_type] - t_reduct
                    )
                    healed_types.append(trauma_type)
        return healed_types
