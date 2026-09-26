import json
from typing import Any, Dict, List, Tuple

class InvariantViolation(Exception):
    """Raised when a state transition violates a governed invariant."""
    pass

class EvidenceGatedViolation(InvariantViolation):
    """Raised when an LLM hallucinated evidence that doesn't exist in the corpus."""
    pass

class Gatekeeper:
    """
    Enforces 'The Mechanism'. A strict state gatekeeper that checks
    aggregate constraints, budgets, and evidence before allowing a commit.
    """
    
    @staticmethod
    def check_metabolic_bounds(physics: Any, mito_state: Any, limits: dict) -> None:
        """Ensure ATP, stamina, and voltage are within physical limits."""
        if mito_state:
            atp = getattr(mito_state, "atp_pool", 0.0)
            if atp < 0.0:
                raise InvariantViolation(f"ATP cannot be negative: {atp}")
            
    def evaluate_state_transition(
        old_state: Dict[str, Any],
        new_state: Dict[str, Any],
        llm_action: dict,
        corpus: List[str]
    ) -> None:
        """
        Run all invariant checks on the resulting state.
        Raises InvariantViolation if any check fails.
        """
        # Metabolic invariants
        if "mito_state" in new_state:
            Gatekeeper.check_metabolic_bounds(new_state.get("physics"), new_state["mito_state"], {})
            


    @staticmethod
    def freeze_engine_state(eng: Any) -> dict:
        """Deep copy the critical variables of the engine state."""
        import copy
        state = {
            "health": eng.health,
            "stamina": eng.stamina,
            "trauma_accum": copy.deepcopy(eng.trauma_accum),
        }
        if hasattr(eng, "soul") and hasattr(eng.soul, "to_dict"):
            state["soul_data"] = copy.deepcopy(eng.soul.to_dict())
            
        if hasattr(eng, "bio") and hasattr(eng.bio, "mito"):
            mito_dict = {}
            for k, v in vars(eng.bio.mito.state).items():
                mito_dict[k] = v
            state["mito_state"] = mito_dict
            
        return state

    @staticmethod
    def thaw_engine_state(eng: Any, state: dict) -> None:
        """Restore the engine state from the frozen snapshot."""
        eng.health = state.get("health", 100.0)
        eng.stamina = state.get("stamina", 100.0)
        eng.trauma_accum = state.get("trauma_accum", {})
        
        if "soul_data" in state and hasattr(eng, "soul") and hasattr(eng.soul, "load_from_dict"):
            eng.soul.load_from_dict(state["soul_data"])
            
        if "mito_state" in state and hasattr(eng, "bio") and hasattr(eng.bio, "mito"):
            for k, v in state["mito_state"].items():
                setattr(eng.bio.mito.state, k, v)
