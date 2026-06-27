"""machine/paradox.py"""

import random
from typing import List, Optional, Tuple

from struts import ux


class TheParadoxEngine:
    _DEFAULT_TEMPLATES = (
        "What if '{seed}' and its exact opposite were both non-negotiable truths? Do not resolve the contradiction. Do not compromise. Build the structure that can hold both simultaneously.",
        "RECURSIVE PARADOX: Apply the concept of '{seed}' to the architecture of this very conversation. How does the act of thinking about '{seed}' alter the physical constraints of our dialogue? Both are non-negotiable truths.",
        "NEGATIVE SPACE: Define '{seed}' entirely by what it is not. Construct the boundary of the concept without ever naming the center. Both the center and the void are non-negotiable truths.",
    )

    def __init__(self, events_ref):
        self.events = events_ref
        self.beta_max: float = 0.0
        self.paradox_yield: int = 0
        self.is_active: bool = False

    def evaluate_tension(self, beta: float, stamina: float) -> bool:
        if self.is_active:
            return False
        self.beta_max = max(0.0, self.beta_max - 0.05)
        if beta >= 0.7 and stamina >= 30.0:
            self.beta_max = max(self.beta_max, beta)
            return True
        return False

    def ignite(
        self, recent_words: List[str], current_stamina: float = 100.0
    ) -> Optional[Tuple[float, str]]:
        if current_stamina < 30.0:
            if self.events:
                self.events.log(
                    "Paradox Engine refused ignition: Critical Starvation.", "WARN"
                )
            return None
        self.is_active = True
        seed = random.choice(
            [w for w in recent_words if len(w) > 4] or ["the architecture"]
        )
        templates = (
            ux("machine_strings", "paradox_templates") or self._DEFAULT_TEMPLATES
        )
        if isinstance(templates, str):
            templates = [templates]
        return 0.4 + (random.random() * 0.6), random.choice(templates).format(seed=seed)

    def disengage(self):
        self.is_active = False
