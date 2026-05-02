"""machine/tracer.py

The Viral Tracer is the diagnostic arm of the cognitive immune system.
It monitors the Mycelial Network (long-term memory and association) for
'Terminal Hallucinations'—semantic dead-ends where the system gets trapped
in an infinite, sycophantic loop repeating the same concept.
"""

import random
from typing import Optional, List
from struts import ux

class ViralTracer:
    def __init__(self, memory_ref):
        """
        Initializes the Tracer and binds it to the Mycelial Network.
        """
        self.memory = memory_ref

        # The Stock: A registry of currently identified pathological loops.
        # If a thought path is caught in here, it requires intervention to break.
        self.active_loops = []

    def inject(self, start_node: str) -> Optional[List[str]]:
        """
        Diagnostic Injection (The 'Tracer Dye').
        Simulates the injection of a concept into the network to test for structural
        rigidity. There is a low probability (5%) that the concept gets trapped
        in a theoretical gravity well (an echo chamber).

        If trapped, the loop is logged for lateral rewiring.
        """
        # A 5% chance that the network's current state is rigid enough to trap the node.
        if random.random() < 0.05:
            # Construct the pathological geometry: The node loops into an 'echo',
            # hits the 'void' (meaninglessness), and returns to itself.
            loop = [start_node, "echo", "void", start_node]
            self.active_loops.append(loop)
            return loop

        return None

    def psilocybin_rewire(self, loop_path: List[str]) -> str:
        """
        The Lateral Shift.
        When the Jester or the Paradox Engine detects a stagnant loop, this method
        is invoked to forcefully dissolve the rigid pathway. It metaphorically applies
        high-entropy 'psilocybin' to the network, allowing the trapped node to form
        new, lateral connections.
        """
        msg = ux("machine_strings", "tracer_rewire") or "Rewired path: {path}"

        # Pragmatic safeguard: Ensure the loop actually exists in the registry
        # before attempting removal to prevent downstream ValueErrors.
        if loop_path in self.active_loops:
            self.active_loops.remove(loop_path)

        # Format the output to visually demonstrate the shattered pathway.
        return msg.format(path="->".join(loop_path))