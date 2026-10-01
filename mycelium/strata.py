import math
from typing import List, Tuple, Any
from .soma import Soma

class Strata:
    """
    Affective Memory wrapper. 
    Stores semantic vectors alongside biological affect vectors.
    Reranks semantic search results based on the emotional similarity to the current state.
    """
    def __init__(self):
        # In a real implementation, this wraps a vector DB (Chroma, FAISS, etc.)
        # Here we mock the datastore for the library standard.
        # Format: (text, semantic_vector, affect_vector)
        self.memories: List[Tuple[str, List[float], List[float]]] = []

    def bury(self, text: str, semantic_vector: List[float], soma: Soma):
        """Store a memory with its biological context."""
        affect = soma.to_affect_vector()
        self.memories.append((text, semantic_vector, affect))

    def dredge(self, query_semantic_vec: List[float], candidates: List[Tuple[str, List[float], List[float]]], soma: Soma) -> List[Tuple[str, float]]:
        """
        Rerank a list of candidate memories based on Affect Distance.
        Meaning dominates when stressed; Feeling dominates when safe.
        """
        current_affect = soma.to_affect_vector()
        cortisol = current_affect[3]
        
        # Max theoretical distance in a 6D unit space is ~2.45
        MAX_DIST = 2.45
        
        # Calculate dynamic alpha:
        # High cortisol -> alpha drops -> semantic score is less penalized by feeling mismatch
        # Low cortisol -> alpha stays high -> feeling deeply penalizes semantic mismatch
        alpha = max(0.2, 0.8 - (cortisol * 0.6))
        
        reranked = []
        for text, sem_vec, stored_affect in candidates:
            # 1. Mock semantic score (e.g., Cosine similarity from the upstream DB)
            # We assume candidates are pre-filtered and passed in with a baseline score of 1.0 for this demo
            # In a real integration, the DB provides the raw cosine score.
            semantic_score = 1.0 
            
            # 2. Calculate Affective Distance (Euclidean)
            sq_diffs = [(c - s)**2 for c, s in zip(current_affect, stored_affect)]
            dist = math.sqrt(sum(sq_diffs))
            norm_dist = dist / MAX_DIST
            
            # 3. Apply penalty
            penalty = norm_dist * alpha
            final_score = semantic_score - penalty
            
            reranked.append((final_score, text))
            
        # Sort descending by final score
        reranked.sort(key=lambda x: x[0], reverse=True)
        return [(item[1], item[0]) for item in reranked]
