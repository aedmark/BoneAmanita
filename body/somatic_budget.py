from dataclasses import dataclass
from typing import Tuple, Dict, Any

from engine.presets import BoneConfig
from engine.struts import safe_get

@dataclass
class SomaticBudget:
    word_cap: int
    sentence_cap: int
    closing_question_allowed: bool
    offer_to_carry_load: bool
    retry_allowance: int
    temperature_band: Tuple[float, float]
    forbid_body_narration: bool
    reason: str

    @classmethod
    def evaluate(
        cls,
        user_state: Dict[str, float],
        engine_state: Dict[str, Any],
        active_mode: str = "",
        config_ref: Any = None,
    ) -> "SomaticBudget":
        cfg = safe_get(config_ref or BoneConfig, "SOMATIC_BUDGET", {})

        def band(key: str, default: Tuple[float, float]) -> Tuple[float, float]:
            low, high = safe_get(cfg, key, default)
            return (float(low), float(high))

        e_u = user_state.get("exhaustion", 0.0)
        p_u = user_state.get("effort", 100.0)

        atp = engine_state.get("atp_pool", 100.0)
        ros = engine_state.get("ros", 0.0)
        respiration = engine_state.get("respiration", "")

        word_cap = int(safe_get(cfg, "WORD_CAP_DEFAULT", 200))
        sentence_cap = int(safe_get(cfg, "SENTENCE_CAP_DEFAULT", 10))
        closing_question_allowed = True
        offer_to_carry_load = False
        retry_allowance = int(safe_get(cfg, "RETRY_ALLOWANCE_DEFAULT", 3))
        temp_band = band("TEMP_BAND_DEFAULT", (0.6, 0.9))
        reason_parts = []

        e_u_flagging = float(safe_get(cfg, "E_U_FLAGGING", 0.6))
        e_u_tiring = float(safe_get(cfg, "E_U_TIRING", 0.4))
        if e_u > e_u_flagging:
            sentence_cap = min(sentence_cap, int(safe_get(cfg, "SENTENCE_CAP_FLAGGING", 3)))
            word_cap = min(word_cap, int(safe_get(cfg, "WORD_CAP_FLAGGING", 60)))
            closing_question_allowed = False
            reason_parts.append("User is flagging (high exhaustion)")
        elif e_u > e_u_tiring:
            sentence_cap = min(sentence_cap, int(safe_get(cfg, "SENTENCE_CAP_TIRING", 5)))
            reason_parts.append("User is tiring")

        p_u_critical = float(safe_get(cfg, "P_U_CRITICAL", 30.0))
        if p_u < p_u_critical:
            offer_to_carry_load = True
            reason_parts.append("User effort is critically low")

        atp_depleted = float(safe_get(cfg, "ATP_DEPLETED", 20.0))
        atp_moderate = float(safe_get(cfg, "ATP_MODERATE", 40.0))
        if atp < atp_depleted:
            sentence_cap = min(sentence_cap, int(safe_get(cfg, "SENTENCE_CAP_ATP_DEPLETED", 3)))
            retry_allowance = int(safe_get(cfg, "RETRY_ALLOWANCE_ATP_DEPLETED", 1))
            temp_band = band("TEMP_BAND_ATP_DEPLETED", (0.4, 0.6))
            reason_parts.append(f"Engine is depleted (ATP < {atp_depleted:g})")
        elif atp < atp_moderate:
            sentence_cap = min(sentence_cap, int(safe_get(cfg, "SENTENCE_CAP_ATP_MODERATE", 5)))
            retry_allowance = int(safe_get(cfg, "RETRY_ALLOWANCE_ATP_MODERATE", 2))

        # A single costly turn (respiration) is a different signal from the pool's
        # cumulative level: a turn can spike ANAEROBIC while ATP is still healthy.
        if respiration == "ANAEROBIC":
            sentence_cap = min(sentence_cap, int(safe_get(cfg, "SENTENCE_CAP_ANAEROBIC", 5)))
            retry_allowance = min(
                retry_allowance, int(safe_get(cfg, "RETRY_ALLOWANCE_ANAEROBIC", 2))
            )
            reason_parts.append("Turn respiration is anaerobic (costly turn)")

        ros_turbulent = float(safe_get(cfg, "ROS_TURBULENT", 50.0))
        if ros > ros_turbulent:
            temp_band = band("TEMP_BAND_ROS_TURBULENT", (0.3, 0.5))
            reason_parts.append(f"High turbulence (ROS > {ros_turbulent:g})")

        if not reason_parts:
            reason_parts.append("Nominal")

        return cls(
            word_cap=word_cap,
            sentence_cap=sentence_cap,
            closing_question_allowed=closing_question_allowed,
            offer_to_carry_load=offer_to_carry_load,
            retry_allowance=retry_allowance,
            temperature_band=temp_band,
            # ADVENTURE's room template requires "**Header**"/"(via X)" exits,
            # which the stage-direction ban can't tell apart from narration.
            forbid_body_narration=active_mode != "ADVENTURE",
            reason="; ".join(reason_parts)
        )
