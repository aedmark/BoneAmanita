"""drivers/userprofile.py"""
import json
import os
from presets import BoneConfig
from struts import safe_get


class UserProfile:
    """
    The UserProfile acts as the long-term memory of the human interacting with the system.
    It tracks semantic affinities (what topics or tones the user naturally gravitates toward)
    and crystallizes them over time, allowing the machine to proactively adapt to the
    user's persistent preferences.
    """

    def __init__(self, name="USER", config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.name = name
        self.affinities = {"heavy": 0.0, "kinetic": 0.0, "abstract": 0.0, "photo": 0.0, "aerobic": 0.0,
                           "thermal": 0.0, "cryo": 0.0}
        self.confidence = 0
        self.drivers_cfg = getattr(self.cfg, "DRIVERS", None)
        self.file_path = getattr(self.drivers_cfg, "PROFILE_FILE_PATH", "user_profile.json")
        self.load()

    def update(self, counts, total_words):
        """
        The adaptive learning loop (Meadows). Evaluates the density of specific semantic
        categories in the user's latest input and updates their long-term affinities.
        """
        cfg = self.drivers_cfg
        if total_words < safe_get(cfg, "PROFILE_MIN_WORDS", 3):
            return
        self.confidence += 1
        threshold = safe_get(cfg, "PROFILE_CONFIDENCE_THRESHOLD", 50)
        alpha = safe_get(cfg, "PROFILE_ALPHA_HIGH", 0.2) if self.confidence < threshold else safe_get(cfg,
                                                                                                      "PROFILE_ALPHA_LOW",
                                                                                                      0.05)
        density_high = safe_get(cfg, "PROFILE_DENSITY_HIGH", 0.15)
        for cat in self.affinities:
            density = counts.get(cat, 0) / total_words
            if density > density_high:
                target = 1.0
            else:
                target = 0.0
            self.affinities[cat] = (alpha * target) + (
                    (1 - alpha) * self.affinities[cat])

    def get_preferences(self):
        """
        Returns two lists: explicitly liked categories and explicitly hated/avoided categories,
        determined by crossing the configuration thresholds.
        """
        cfg = self.drivers_cfg
        like_thresh = safe_get(cfg, "PROFILE_LIKE_THRESH", 0.3)
        hate_thresh = safe_get(cfg, "PROFILE_HATE_THRESH", -0.2)
        return [k for k, v in self.affinities.items() if v > like_thresh], [k for k, v in self.affinities.items() if
                                                                            v < hate_thresh]

    def save(self):
        """
        Serializes the profile to disk.
        Schur Heuristic: If we hit a permission error or locked file, we silently pass.
        It is better to lose one turn of memory than to crash the entire application runtime.
        """
        try:
            with open(self.file_path, "w") as f:
                json.dump(
                    {"name": self.name, "affinities": self.affinities, "confidence": self.confidence}, f)
        except IOError:
            pass

    def load(self):
        """
        Hydrates the profile from disk. If the file is missing or corrupted,
        it gracefully falls back to the default initialized state.
        """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path) as f:
                    data = json.load(f)
                    if "affinities" in data:
                        self.affinities.update(data["affinities"])
                    self.confidence = data.get("confidence", 0)
            except (IOError, json.JSONDecodeError):
                pass
