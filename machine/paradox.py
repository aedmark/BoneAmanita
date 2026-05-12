"""machine/paradox.py
The Paradox Engine is the system's deliberate stress-tester.
Instead of resolving logical conflicts to comfort the user, it seeks out
high-tension moments and injects an unsolvable contradiction.
The goal is epigenetic growth: by forcing the system (and the user) to hold
two opposing truths simultaneously, the overall structural capacity for
nuance and resilience ('beta') increases.
"""
import random
from typing import Tuple, List
from struts import ux


class TheParadoxEngine:
    _DEFAULT_TEMPLATES = (
        "What if '{seed}' and its exact opposite were both non-negotiable truths? Do not resolve the contradiction. Do not compromise. Build the structure that can hold both simultaneously.",
        "[RECURSIVE PARADOX] Apply the concept of '{seed}' to the architecture of this very conversation. How does the act of thinking about '{seed}' alter the physical constraints of our dialogue? Both are non-negotiable truths.",
        "[NEGATIVE SPACE] Define '{seed}' entirely by what it is not. Construct the boundary of the concept without ever naming the center. Both the center and the void are non-negotiable truths.",
    )

    def __init__(self, events_ref):
        self.events = events_ref
        self.beta_max: float = 0.0
        self.paradox_yield: int = 0
        self.is_active: bool = False

    def evaluate_tension(self, beta: float, stamina: float) -> bool:
        """
        The Biological Gatekeeper.
        Evaluates if the current conversational environment is ripe for a paradox.
        """
        # THE THERMAL EXHAUST PORT: Hard-capped to fire exactly once per active sequence.
        if self.is_active:
            return False

        self.beta_max = max(0.0, self.beta_max - 0.05)
        if beta >= 0.7 and stamina >= 30.0:
            self.beta_max = max(self.beta_max, beta)
            return True
        return False

    def ignite(self, recent_words: List[str]) -> Tuple[float, str]:
        """
        Fires the engine. Selects a conceptual seed from the user's recent
        vocabulary and wraps it in a contradictory framework.
        Returns:
            A tuple containing the 'Yield' (a float representing the generated
            Glimmer/Resonance reward) and the generated paradox string.
        """
        self.is_active = True
        seed = random.choice([w for w in recent_words if len(w) > 4] or ["the architecture"])
        templates = ux("machine_strings", "paradox_templates") or self._DEFAULT_TEMPLATES
        if isinstance(templates, str):
            templates = [templates]
        return 0.4 + (random.random() * 0.6), random.choice(templates).format(seed=seed)

    def disengage(self):
        """
        Lowers the flag, allowing the Global Workspace to return to standard,
        linear analytical processing.
        """
        self.is_active = False
