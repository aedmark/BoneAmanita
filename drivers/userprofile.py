import logging
import json
import os

from engine.presets import BoneConfig
from engine.receipts import issue as issue_receipt
from engine.struts import safe_get

logger = logging.getLogger("bone")

class UserProfile:
    """Which lexical registers the person keeps using, learned each turn and kept in the Halcyon store."""

    RECORD = "user.profile"

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
        self.persistence = None

    def attach_store(self, store):
        """Loads the profile from the store; an old user_profile.json is imported once and renamed .imported."""
        self.persistence = store
        if store.record(self.RECORD) is None and (legacy := self._read_legacy()) is not None:
            self._apply(legacy)
            self.save()
            os.replace(self.file_path, self.file_path + ".imported")
        self._apply(store.record(self.RECORD) or {})

    def observe(self, counts, total_words, physics_state=None):
        """One user turn: learn from it, keep the result, and receipt what moved."""
        before = dict(self.affinities)
        learned = self.update(counts, total_words, physics_state)
        if learned:
            self.save()
        rising = sorted(k for k, v in self.affinities.items() if v > before[k])
        likes, _ = self.get_preferences()
        issue_receipt(
            "user.profile",
            "LEARNED" if learned else "SKIPPED",
            result_count=len(rising),
            inputs={"words": total_words, "confidence": self.confidence,
                    "affinities": {k: round(v, 3) for k, v in self.affinities.items()}},
            detail=f"rising: {', '.join(rising) or 'none'}; likes: {', '.join(likes) or 'none'}"
            if learned else f"{total_words} words, under the minimum",
        )

    def update(self, counts, total_words, physics_state=None):
        cfg = self.drivers_cfg
        if total_words < int(safe_get(cfg, "PROFILE_MIN_WORDS", 3)):
            return False
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
        return True

    def get_preferences(self):
        cfg = self.drivers_cfg
        like_thresh = float(safe_get(cfg, "PROFILE_LIKE_THRESH", 0.3))
        hate_thresh = float(safe_get(cfg, "PROFILE_HATE_THRESH", -0.2))
        return [k for k, v in self.affinities.items() if v > like_thresh], [
            k for k, v in self.affinities.items() if v < hate_thresh
        ]

    def save(self):
        if self.persistence is None:
            return
        try:
            self.persistence.put_record(
                self.RECORD,
                {"name": self.name, "affinities": self.affinities, "confidence": self.confidence},
            )
        except Exception as e:
            logger.warning(
                f"User profile could not be saved to the store: "
                f"{type(e).__name__}: {e}. Affinities learned this turn are lost."
            )

    def _apply(self, data):
        if isinstance(data.get("affinities"), dict):
            self.affinities.update(
                {k: float(v) for k, v in data["affinities"].items() if k in self.affinities}
            )
        self.confidence = int(data.get("confidence", self.confidence))

    def _read_legacy(self):
        if not os.path.exists(self.file_path):
            return None
        try:
            with open(self.file_path) as f:
                data = json.load(f)
            return data if isinstance(data, dict) else None
        except (IOError, json.JSONDecodeError) as e:
            logger.warning(
                f"User profile at {self.file_path} exists but could not be read: "
                f"{type(e).__name__}: {e}. Starting from an empty profile."
            )
            return None
