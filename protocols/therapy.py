"""protocols/therapy.py
The Therapy Protocol governs the slow, passive healing of the engine.
It monitors the ongoing physical dimensions of the conversation, looking for
streaks of "clean" (non-toxic) and "strong" (resilient/constructive) inputs.
If the user maintains healthy conversational boundaries for enough consecutive
turns, the system automatically reduces its accumulated trauma load.
"""
from typing import Dict, Any
from presets import BoneConfig
from struts import safe_get


class TherapyProtocol:
    """
    A passive monitoring protocol that tracks behavioral streaks to gradually
    heal the system's deep psychological vectors (e.g., SEPTIC, EXHAUSTION).
    """

    def __init__(self, config_ref=None):
        """
        Initializes the therapy trackers, mapping them dynamically to the
        engine's configured trauma vectors.
        """
        self.cfg = config_ref or BoneConfig
        default_vector = {"SEPTIC": 0, "EXHAUSTION": 0, "PARANOIA": 0}
        vector_keys = getattr(self.cfg, "TRAUMA_VECTOR", default_vector).keys()
        self.streaks = {k: 0 for k in vector_keys}
        cfg = getattr(self.cfg, "THERAPY", object())
        self.HEALING_THRESHOLD = getattr(cfg, "HEALING_THRESHOLD", 5)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the therapy streaks so progress isn't lost during reboots."""
        return {"streaks": self.streaks}

    def load_state(self, data: Dict[str, Any]):
        """Restores the active healing streaks from a serialized dictionary."""
        self.streaks = data.get("streaks", {k: 0 for k in self.cfg.TRAUMA_VECTOR.keys()})

    def check_progress(self, phys, _stamina, current_trauma_accum, _qualia=None):
        """
        The core evaluation loop for the Therapy protocol. Analyzes the latest
        input for toxicity and constructive strength, updating streaks and applying
        healing if thresholds are met.
        Args:
            phys: The physical/dimensional metrics of the prompt.
            _stamina: The current energy of the system (unused in this check).
            current_trauma_accum: The active dictionary of the system's current trauma load.
            _qualia: Subjective experience markers (unused in this check).
        Returns:
            A list of strings representing the specific trauma types that were healed this turn.
        """
        matter = safe_get(phys, "matter", {}) or {}
        counts = safe_get(phys, "counts", safe_get(matter, "counts", {}))
        vector = safe_get(phys, "vector", safe_get(matter, "vector", {}))
        cfg_therapy = getattr(self.cfg, "THERAPY", object())
        str_req = getattr(cfg_therapy, "STRENGTH_REQ", 0.3)
        t_reduct = getattr(cfg_therapy, "TRAUMA_REDUCTION", 0.5)
        healed_types = []
        is_clean = counts.get("toxin", 0) == 0
        has_strength = vector.get("STR", 0.0) > str_req
        self.streaks["SEPTIC"] = (self.streaks["SEPTIC"] + 1) if (is_clean and has_strength) else 0
        for trauma_type, streak in self.streaks.items():
            if streak >= self.HEALING_THRESHOLD:
                self.streaks[trauma_type] = 0
                if current_trauma_accum.get(trauma_type, 0.0) > 0.0:
                    current_trauma_accum[trauma_type] = max(0.0, current_trauma_accum[trauma_type] - t_reduct)
                    healed_types.append(trauma_type)
        return healed_types
