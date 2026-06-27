"""drivers/enneagram.py"""

from typing import Any, Tuple

from core import LoreManifest
from drivers.souldriver import SoulDriver
from presets import BoneConfig
from struts import safe_get, ux


class EnneagramDriver:
    def __init__(self, events_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.events = events_ref
        self.current_persona = "NARRATOR"
        self.pending_persona = None
        self.stability_counter = 0

        cfg = safe_get(self.cfg, "DRIVERS", {})
        self.HYSTERESIS_THRESHOLD = int(safe_get(cfg, "ENNEAGRAM_HYSTERESIS", 3))
        manifest = LoreManifest.get_instance(config_ref=self.cfg)
        driver_cfg = manifest.get("DRIVER_CONFIG") or {}
        self.weights_cfg = driver_cfg.get("ENNEAGRAM_WEIGHTS", {})
        self.state_map = driver_cfg.get("PERSONA_STATE_MAP", {})
        self.sanc_zone = safe_get(
            safe_get(self.cfg, "SANCTUARY", {}), "ZONE", "SANCTUARY"
        )
        self.hybrid_gap = float(safe_get(cfg, "ENNEAGRAM_HYBRID_GAP", 0.5))

    def _calculate_raw_persona(
        self, physics: Any, soul_ref=None
    ) -> Tuple[str, str, str]:
        p_vec = safe_get(physics, "vector", {})
        p_vol = float(safe_get(physics, "voltage", 0.0))
        p_drag = float(safe_get(physics, "narrative_drag", 0.0))
        p_coh = float(safe_get(physics, "kappa", 0.0))
        p_zone = str(safe_get(physics, "zone", ""))

        weights_cfg = self.weights_cfg
        if not isinstance(weights_cfg, dict) or len(weights_cfg) < 2:
            return (
                "NARRATOR",
                "ACTIVE",
                "The persona matrix is fractured. Retreating to the baseline Narrator.",
            )

        scores = dict.fromkeys(weights_cfg, 0.0)
        if "NARRATOR" in scores:
            scores["NARRATOR"] += 2.0

        if p_zone == self.sanc_zone or (4.0 <= p_vol <= 10.0 and 0.5 <= p_drag <= 3.5):
            for persona, mod in [("NARRATOR", 6.0), ("JESTER", 3.0), ("GORDON", -2.0)]:
                if persona in scores:
                    scores[persona] += mod
        for persona, criteria in weights_cfg.items():
            if not isinstance(criteria, dict):
                continue
            if p_vol > float(criteria.get("tension_min", float("inf"))):
                scores[persona] += 3.0
            if p_drag > float(criteria.get("drag_min", float("inf"))):
                scores[persona] += 5.0
            if p_coh > float(criteria.get("coherence_min", float("inf"))):
                scores[persona] += 4.0
            if "coherence_max" in criteria and p_coh < float(criteria["coherence_max"]):
                scores[persona] += 4.0
            vectors = criteria.get("vectors", {})
            if isinstance(vectors, dict):
                for dim, weight in vectors.items():
                    val = float(p_vec.get(dim, 0.0))
                    if val > 0.2:
                        scores[persona] += val * float(weight)
        if soul_ref:
            influence = (
                soul_ref.get_influence()
                if hasattr(soul_ref, "get_influence")
                else SoulDriver(soul_ref).get_influence()
            )
            for persona, weight in influence.items():
                scores[persona] += weight * 2.0
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        winner, win_score = sorted_scores[0]
        runner_up, run_score = sorted_scores[1]
        if (win_score - run_score) <= self.hybrid_gap and win_score > 0:
            winner = f"{winner}/{runner_up} [HYBRID]"
        msg_winner = ux("driver_strings", "ennea_winner") or "Shift triggered: {winner}"
        reason = msg_winner.format(winner=winner, score=win_score, v=p_vol, d=p_drag)
        primary_arch = winner.split("/")[0] if "HYBRID" in winner else winner
        return winner, self.state_map.get(primary_arch, "ACTIVE"), reason

    def decide_persona(self, physics, soul_ref=None) -> Tuple[str, str, str]:
        candidate, state_desc, reason = self._calculate_raw_persona(physics, soul_ref)
        if candidate == self.current_persona:
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, reason
        if candidate == self.pending_persona:
            self.stability_counter += 1
        else:
            self.pending_persona = candidate
            self.stability_counter = 1
        msg_shift = (
            ux("driver_strings", "ennea_shift") or "Shifted persona. Reason: {reason}"
        )
        if self.stability_counter >= self.HYSTERESIS_THRESHOLD:
            self.current_persona = candidate
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, msg_shift.format(reason=reason)
        msg_resisting = (
            ux("driver_strings", "ennea_resisting")
            or "Resisting shift to {candidate} ({count}/{thresh})"
        )
        return (
            self.current_persona,
            "STABLE",
            msg_resisting.format(
                candidate=candidate,
                count=self.stability_counter,
                thresh=self.HYSTERESIS_THRESHOLD,
            ),
        )
