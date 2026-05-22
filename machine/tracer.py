"""machine/tracer.py"""

import random
from typing import Optional, List
from struts import ux

class ViralTracer:
    def __init__(self, memory_ref):
        self.memory = memory_ref
        self.active_loops = []

    def inject(self, start_node: str) -> Optional[List[str]]:
        if random.random() < 0.05:
            loop = [start_node, "echo", "void", start_node]
            self.active_loops.append(loop)
            return loop
        return None

    def psilocybin_rewire(self, loop_path: List[str]) -> str:
        msg = ux("machine_strings", "tracer_rewire") or "Rewired path: {path}"
        try:
            self.active_loops.remove(loop_path)
        except ValueError:
            pass  # The pathway is already dissolved
        return msg.format(path="->".join(loop_path))
