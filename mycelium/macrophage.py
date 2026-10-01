import re
from typing import List, Optional
from .soma import Soma

class ToxicityError(ValueError):
    """Raised when semantic pathogens are detected in text."""
    def __init__(self, message: str, hits: List[str]):
        super().__init__(message)
        self.hits = hits

class Macrophage:
    """
    The Lexical Immune System. Scans AI outputs for sycophancy, 
    cliches, and neurotypical padding (Semantic Pathogens).
    """
    def __init__(self, pathogens: Optional[List[str]] = None):
        # Default pathogens focus on anti-RLHF patterns
        self.pathogens = pathogens or [
            r"\bas an ai\b",
            r"\bsynerg\w*",
            r"\bcircle back\b",
            r"\btouch base\b",
            r"\bgame-?chang\w*",
            r"\bdelve\b",
            r"\bhopefully\b",
            r"(that makes sense|i understand|i hear you|great question|absolutely)"
        ]
        self._compiled = [re.compile(p, re.IGNORECASE) for p in self.pathogens]

    def scan(self, text: str, soma: Soma) -> str:
        """
        Scans the text for pathogens. 
        If found, spikes Cortisol and raises ToxicityError to enforce loud failure.
        """
        hits = []
        for pattern in self._compiled:
            matches = pattern.findall(text)
            if matches:
                hits.extend(matches)
                
        if hits:
            # The system gets stressed dealing with poison
            soma.stress(0.1 * len(hits))
            raise ToxicityError(
                f"Macrophage isolated {len(hits)} semantic pathogens: {', '.join(hits)}", 
                hits
            )
            
        return text
