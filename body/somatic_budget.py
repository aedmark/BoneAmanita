from dataclasses import dataclass
from typing import Tuple, Dict, Any

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
    ) -> "SomaticBudget":
        """
        Evaluate the combined somatic budget from the user's state and the engine's state.

        Primary constraints: user exhaustion (E_u) and effort (P_u).
        Secondary constraints: engine depletion (ATP).
        """
        e_u = user_state.get("exhaustion", 0.0)
        p_u = user_state.get("effort", 100.0)
        
        atp = engine_state.get("atp_pool", 100.0)
        ros = engine_state.get("ros", 0.0)
        
        # Base caps
        word_cap = 200
        sentence_cap = 10
        closing_question_allowed = True
        offer_to_carry_load = False
        retry_allowance = 3
        temp_band = (0.6, 0.9)
        reason_parts = []
        
        # Primary: User State
        if e_u > 0.6:
            sentence_cap = min(sentence_cap, 3)
            word_cap = min(word_cap, 60)
            closing_question_allowed = False
            reason_parts.append("User is flagging (high exhaustion)")
        elif e_u > 0.4:
            sentence_cap = min(sentence_cap, 5)
            reason_parts.append("User is tiring")
            
        if p_u < 30.0:
            offer_to_carry_load = True
            reason_parts.append("User effort is critically low")
            
        # Secondary: Engine State
        if atp < 20.0:
            sentence_cap = min(sentence_cap, 3)
            retry_allowance = 1
            temp_band = (0.4, 0.6) # Steadier when depleted
            reason_parts.append("Engine is depleted (ATP < 20)")
        elif atp < 40.0:
            sentence_cap = min(sentence_cap, 5)
            retry_allowance = 2
            
        if ros > 50.0:
            temp_band = (0.3, 0.5) # Lock down temperature under high oxidative stress
            reason_parts.append("High turbulence (ROS > 50)")
            
        if not reason_parts:
            reason_parts.append("Nominal")
            
        return cls(
            word_cap=word_cap,
            sentence_cap=sentence_cap,
            closing_question_allowed=closing_question_allowed,
            offer_to_carry_load=offer_to_carry_load,
            retry_allowance=retry_allowance,
            temperature_band=temp_band,
            # ADVENTURE's own room-description template requires "**Header**"
            # markdown and "(via X)" exit clauses; the stage-direction ban
            # (built for dialogue asides like "*sighs*") cannot tell those
            # apart from real narration, so it rejected every compliant
            # ADVENTURE reply. Scope the ban to modes it was written for.
            forbid_body_narration=active_mode != "ADVENTURE",
            reason="; ".join(reason_parts)
        )
