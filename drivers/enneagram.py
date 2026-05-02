"""drivers/enneagram.py"""

from typing import Tuple

from core import LoreManifest
from physics.models import PhysicsPacket
from presets import BoneConfig
from struts import ux, safe_get
from drivers.souldriver import SoulDriver


class EnneagramDriver:
    """
    The EnneagramDriver manages the system's active persona (e.g., NARRATOR, JESTER, GORDON).
    It acts as a dynamic state machine that reads the current 'physics' of the conversation
    (tension, drag, chaos) and calculates which archetype is best suited to handle the load.
    """
    def __init__(self, events_ref, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.events = events_ref

        # The system always boots in a neutral, stable state.
        self.current_persona = "NARRATOR"
        self.pending_persona = None
        self.stability_counter = 0

        # Hysteresis is a system dynamics concept (Meadows). It prevents rapid,
        # jarring oscillations between personas. A new persona must "win" the calculation
        # multiple times in a row (default: 3) before the system actually shifts.
        cfg = getattr(self.cfg, "DRIVERS", None)
        self.HYSTERESIS_THRESHOLD = getattr(cfg, "ENNEAGRAM_HYSTERESIS", 3)

    @property
    def weights(self):
        """Retrieves the baseline scoring matrix that defines what triggers each persona."""
        return (LoreManifest.get_instance(config_ref=self.cfg).get(
            "DRIVER_CONFIG", "ENNEAGRAM_WEIGHTS") or {})

    def _calculate_raw_persona(self, physics: PhysicsPacket, soul_ref=None) -> Tuple[str, str, str]:
        """
        The core scoring engine. It evaluates the current physics packet against the
        weights dictionary to find the most contextually appropriate persona.
        """
        # Unpack the physics packet into semantic variables (Pinker)
        p_vec = physics.vector or {}
        p_vol = physics.voltage         # System energy / tension
        p_drag = physics.narrative_drag # Conversational friction / exhaustion
        p_coh = physics.kappa           # Structural coherence / logical integrity
        p_zone = str(physics.zone or "")

        weights_cfg = self.weights

        # Pragmatic Fallback (Schur): If the config is missing or corrupted,
        # don't crash. Just fall back to the safe, neutral baseline.
        if not isinstance(weights_cfg, dict) or len(weights_cfg) < 2:
            return "NARRATOR", "ACTIVE", "The persona matrix is fractured. Retreating to the baseline Narrator."

        # Initialize the scoreboard.
        scores = {k: 0.0 for k in weights_cfg.keys()}

        # The NARRATOR gets a base gravity well to prevent unnecessary shifts.
        if "NARRATOR" in scores:
            scores["NARRATOR"] += 2.0

        # Hardcoded environmental overrides: If we are in the 'Sanctuary' zone, or
        # if the system is coasting in a comfortable state (moderate voltage, low drag),
        # heavily favor the Narrator and suppress high-friction personas like Gordon.
        if p_zone == safe_get(getattr(self.cfg, "SANCTUARY", {}), "ZONE", "SANCTUARY") or (
                4.0 <= p_vol <= 10.0 and 0.5 <= p_drag <= 3.5):
            for persona, mod in [("NARRATOR", 6.0), ("JESTER", 3.0), ("GORDON", -2.0)]:
                if persona in scores: scores[persona] += mod

        # Iterate through the configuration matrix and score each archetype based on thresholds.
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

            # Evaluate highly specific vector triggers (e.g., "Chaos", "Grief")
            vectors = criteria.get("vectors", {})
            if isinstance(vectors, dict):
                for dim, weight in vectors.items():
                    val = float(p_vec.get(dim, 0.0))
                    if val > 0.2:
                        scores[persona] += val * float(weight)

        # The SoulDriver allows the user's permanent preferences/scars to heavily influence
        # the outcome, overriding temporary physics.
        if soul_ref:
            soul_driver = SoulDriver(soul_ref)
            influence = soul_driver.get_influence()
            for persona, weight in influence.items():
                scores[persona] += weight * 2.0

        # Sort the scoreboard to find the winner and the runner-up.
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        winner, win_score = sorted_scores[0]
        runner_up, run_score = sorted_scores[1]

        cfg = getattr(self.cfg, "DRIVERS", None)
        hybrid_gap = float(safe_get(cfg, "ENNEAGRAM_HYBRID_GAP", 0.5))

        # Gestalt Synergy (Fuller): If the top two personas are in a statistical dead heat,
        # the system synthesizes them rather than forcing a binary choice.
        if (win_score - run_score) <= hybrid_gap and win_score > 0:
            winner = f"{winner}/{runner_up} [HYBRID]"

        msg_winner = ux("driver_strings", "ennea_winner") or "Shift triggered: {winner}"
        reason = msg_winner.format(winner=winner, score=win_score, v=p_vol, d=p_drag)

        # Retrieve the behavioral state (e.g., "ACTIVE", "OBSERVING") mapped to this persona.
        state_map = (LoreManifest.get_instance(config_ref=self.cfg).get("DRIVER_CONFIG", "PERSONA_STATE_MAP") or {})
        primary_arch = winner.split("/")[0] if "HYBRID" in winner else winner

        return winner, state_map.get(primary_arch, "ACTIVE"), reason

    def decide_persona(self, physics, soul_ref=None) -> Tuple[str, str, str]:
        """
        The gatekeeper function. It runs the raw calculation but enforces the
        hysteresis loop to prevent the system from having an identity crisis
        on every single token update.
        """
        candidate, state_desc, reason = self._calculate_raw_persona(physics, soul_ref)

        # If the candidate matches the current state, reset the stability buffer.
        if candidate == self.current_persona:
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, reason

        # If the candidate is new, require it to "hold" the position for multiple cycles.
        if candidate == self.pending_persona:
            self.stability_counter += 1
        else:
            self.pending_persona = candidate
            self.stability_counter = 1

        msg_shift = (ux("driver_strings", "ennea_shift") or "Shifted persona. Reason: {reason}")

        # The candidate has overcome the friction. The phase shift is executed.
        if self.stability_counter >= self.HYSTERESIS_THRESHOLD:
            self.current_persona = candidate
            self.stability_counter = 0
            self.pending_persona = None
            return self.current_persona, state_desc, msg_shift.format(reason=reason)

        # The candidate won the math, but hasn't overcome the friction yet. We resist the shift.
        msg_resisting = (ux("driver_strings", "ennea_resisting") or "Resisting shift to {candidate} ({count}/{thresh})")
        return (self.current_persona, "STABLE", msg_resisting.format(candidate=candidate,
                 count=self.stability_counter, thresh=self.HYSTERESIS_THRESHOLD))