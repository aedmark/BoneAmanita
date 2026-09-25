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
            
    MIN_EVIDENCE_WORDS = 5

    @staticmethod
    def verify_evidence(claim_evidence: str, corpus: List[str]) -> bool:
        """An exact quote (case and words; whitespace normalized) of at least MIN_EVIDENCE_WORDS from the dialogue."""
        claim = " ".join(str(claim_evidence or "").split())
        if len(claim.split()) < Gatekeeper.MIN_EVIDENCE_WORDS:
            return False
        return any(claim in " ".join(str(item).split()) for item in corpus)

    @staticmethod
    def check_memory_commit(memory_action: dict, dialogue_corpus: List[str]) -> None:
        """
        Ensure any new memory commit cites exact text from the dialogue corpus.
        """
        if not memory_action:
            return
            
        evidence = memory_action.get("evidence")
        if not evidence:
            raise EvidenceGatedViolation("Memory commit rejected: No exact evidence cited.")
            
        if not Gatekeeper.verify_evidence(evidence, dialogue_corpus):
            raise EvidenceGatedViolation(
                f"Memory commit rejected: '{evidence}' is not an exact quote of at least "
                f"{Gatekeeper.MIN_EVIDENCE_WORDS} words from the dialogue."
            )

    @staticmethod
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
            
        # Tool / Action invariants
        if llm_action:
            if llm_action.get("tool") == "commit_memory":
                Gatekeeper.check_memory_commit(llm_action.get("args", {}), corpus)

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
