"""protocols/critics.py"""

import random
from typing import Any, Optional

from constants import Prisma
from core import LoreManifest
from presets import BoneConfig
from struts import safe_get, ux


class TheCriticsCircle:
    def __init__(self, events_ref, config_ref=None):
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        narrative_data = LoreManifest.get_instance().get("narrative_data") or {}
        self.critics = narrative_data.get("LITERARY_CRITICS", {})
        self.active_cooldowns = {}
        self.last_review_turn = 0

    def to_dict(self):
        return {
            "active_cooldowns": self.active_cooldowns,
            "last_review_turn": self.last_review_turn,
        }

    def load_state(self, data):
        self.active_cooldowns = data.get("active_cooldowns", {})
        self.last_review_turn = data.get("last_review_turn", 0)

    def audit_performance(self, physics: Any, turn_count: int) -> Optional[str]:
        cfg = safe_get(self.cfg, "CRITICS", {})
        rev_cd = int(safe_get(cfg, "REVIEW_COOLDOWN", 10))
        if turn_count - self.last_review_turn < rev_cd:
            return None
        voltage = float(safe_get(physics, "voltage", 0.0))
        drag = float(safe_get(physics, "narrative_drag", 0.0))
        velocity = safe_get(physics, "velocity")
        if velocity is None:
            velocity = voltage * (1.0 / max(0.1, drag))
        best_match = None
        review_type = "neutral"
        max_contrib = float(safe_get(cfg, "MAX_METRIC_CONTRIB", 5.0))
        pos_thresh = float(safe_get(cfg, "POSITIVE_REVIEW_THRESH", 15.0))
        neg_thresh = float(safe_get(cfg, "NEGATIVE_REVIEW_THRESH", -15.0))
        for key, critic in self.critics.items():
            if self.active_cooldowns.get(key, 0) > turn_count:
                continue
            prefs = critic.get("preferences", {})
            score = 0.0
            for metric, target in prefs.items():
                metric_str = str(metric)
                if metric_str.startswith("counts_"):
                    category = metric_str.replace("counts_", "")
                    counts = safe_get(physics, "counts", {})
                    raw_count = float(safe_get(counts, category, 0.0))
                    current = min(max_contrib, raw_count * 0.5)
                elif metric_str == "velocity":
                    current = float(velocity)
                else:
                    current = float(safe_get(physics, metric_str, 0.0))
                target_val = float(target)
                if target_val > 0:
                    score += current * target_val
                else:
                    score -= current * abs(target_val)
            if score > pos_thresh:
                best_match = (key, critic)
                review_type = "high"
            elif score < neg_thresh:
                best_match = (key, critic)
                review_type = "low"
        if best_match:
            key, critic = best_match
            self.last_review_turn = turn_count
            self.active_cooldowns[key] = turn_count + int(
                safe_get(cfg, "CRITIC_COOLDOWN_TICKS", 50)
            )
            comment = random.choice(
                critic.get("reviews", {}).get(review_type, ["Hrm."])
            )
            color = Prisma.GRN if review_type == "high" else Prisma.RED
            icon_good = ux("council_strings", "critic_good_icon") or "Gold Star!"
            icon_bad = ux("council_strings", "critic_bad_icon") or "Sad Face!"
            icon = icon_good if review_type == "high" else icon_bad
            rev_msg = (
                ux("protocol_strings", "critic_review") or "[{icon}] {name}: {comment}"
            )
            return f"{color}{rev_msg.format(icon=icon, name=critic.get('name', key), comment=comment)}{Prisma.RST}"
        return None
