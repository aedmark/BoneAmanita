"""drivers/userprofile.py"""

import logging
import json
import os

from presets import BoneConfig
from struts import safe_get

logger = logging.getLogger("bone")


class UserProfile:
    def __init__(self, name="USER", config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.name = name
        self.affinities = {
            "heavy": 0.0,
            "kinetic": 0.0,
            "abstract": 0.0,
            "photo": 0.0,
            "aerobic": 0.0,
            "thermal": 0.0,
            "cryo": 0.0,
        }
        self.confidence = 0
        self.drivers_cfg = safe_get(self.cfg, "DRIVERS", {})
        self.file_path = safe_get(
            self.drivers_cfg, "PROFILE_FILE_PATH", "user_profile.json"
        )
        self.load()

    def update(self, counts, total_words, physics_state=None):
        cfg = self.drivers_cfg
        if total_words < int(safe_get(cfg, "PROFILE_MIN_WORDS", 3)):
            return
        self.confidence += 1
        threshold = int(safe_get(cfg, "PROFILE_CONFIDENCE_THRESHOLD", 50))
        if self.confidence < threshold:
            alpha = float(safe_get(cfg, "PROFILE_ALPHA_HIGH", 0.2))
        else:
            alpha = float(safe_get(cfg, "PROFILE_ALPHA_LOW", 0.05))
        if physics_state is None:
            physics_state = {}
        chi = float(
            safe_get(physics_state, "chi", safe_get(physics_state, "entropy", 0.2))
        )
        chi_decay_mult = float(safe_get(cfg, "PROFILE_CHI_DECAY_MULT", 0.15))
        entropic_alpha = min(1.0, alpha + (chi * chi_decay_mult))
        density_high = float(safe_get(cfg, "PROFILE_DENSITY_HIGH", 0.15))
        for cat in self.affinities:
            density = counts.get(cat, 0) / total_words
            if density > density_high:
                self.affinities[cat] = (alpha * 1.0) + (
                    (1.0 - alpha) * self.affinities[cat]
                )
            else:
                self.affinities[cat] = (entropic_alpha * 0.0) + (
                    (1.0 - entropic_alpha) * self.affinities[cat]
                )

    def get_preferences(self):
        cfg = self.drivers_cfg
        like_thresh = float(safe_get(cfg, "PROFILE_LIKE_THRESH", 0.3))
        hate_thresh = float(safe_get(cfg, "PROFILE_HATE_THRESH", -0.2))
        return [k for k, v in self.affinities.items() if v > like_thresh], [
            k for k, v in self.affinities.items() if v < hate_thresh
        ]

    def save(self):
        try:
            with open(self.file_path, "w") as f:
                json.dump(
                    {
                        "name": self.name,
                        "affinities": self.affinities,
                        "confidence": self.confidence,
                    },
                    f,
                )
        except IOError as e:
            logger.warning(
                f"User profile could not be saved to {self.file_path}: "
                f"{type(e).__name__}: {e}. Affinities learned this session are lost."
            )

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path) as f:
                    data = json.load(f)
                    if "affinities" in data:
                        self.affinities.update(data["affinities"])
                    self.confidence = data.get("confidence", 0)
            except FileNotFoundError:
                pass
            except (IOError, json.JSONDecodeError) as e:
                logger.warning(
                    f"User profile at {self.file_path} exists but could not be read: "
                    f"{type(e).__name__}: {e}. Starting from an empty profile."
                )
