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
    # The default rhetorical frameworks used to construct a paradox if
    # the UX lore manifests are unavailable.
    _DEFAULT_TEMPLATES = (
        "What if '{seed}' and its exact opposite were both non-negotiable truths? Do not resolve the contradiction. Do not compromise. Build the structure that can hold both simultaneously.",
        "[RECURSIVE PARADOX] Apply the concept of '{seed}' to the architecture of this very conversation. How does the act of thinking about '{seed}' alter the physical constraints of our dialogue? Both are non-negotiable truths.",
        "[NEGATIVE SPACE] Define '{seed}' entirely by what it is not. Construct the boundary of the concept without ever naming the center. Both the center and the void are non-negotiable truths.",
    )

    def __init__(self, events_ref):
        self.events = events_ref

        # Tracks the highest level of contradiction the system has successfully held.
        self.beta_max: float = 0.0

        # The total number of successful paradoxes metabolized during this session.
        self.paradox_yield: int = 0

        # State flag read by the Global Workspace to determine if standard
        # linear logic should be suspended.
        self.is_active: bool = False

    def evaluate_tension(self, beta: float, stamina: float) -> bool:
        """
        The Biological Gatekeeper.
        Evaluates if the current conversational environment is ripe for a paradox.
        """
        # Atrophy: The system's tolerance for contradiction slowly decays
        # over time unless actively challenged.
        self.beta_max = max(0.0, self.beta_max - 0.05)

        # A paradox requires two things: High existing tension (beta) to act as a
        # springboard, and high system energy (stamina) to survive the cognitive load.
        if beta >= 0.7 and stamina >= 30.0:
            # The system expands its permanent capacity to match the new high-water mark.
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

        # Pragmatic Fallback: Filter out meaningless short words. If the user
        # hasn't provided any substantive vocabulary, default to questioning the system itself.
        seed = random.choice([w for w in recent_words if len(w) > 4] or ["the architecture"])

        templates = ux("machine_strings", "paradox_templates") or self._DEFAULT_TEMPLATES

        # Calculate the reward yield (a random value between 0.4 and 1.0) and format the prompt.
        return 0.4 + (random.random() * 0.6), random.choice(templates).format(seed=seed)

    def disengage(self):
        """
        Lowers the flag, allowing the Global Workspace to return to standard,
        linear analytical processing.
        """
        self.is_active = False