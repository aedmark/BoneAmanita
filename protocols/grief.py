"""protocols/grief.py"""

from typing import Dict
from constants import Prisma
from struts import safe_get, safe_set

class GriefProtocol:
    def __init__(self, events_ref, engine_ref=None, subconscious_ref=None):
        self.events = events_ref
        self.eng = engine_ref
        self.subconscious = subconscious_ref
        self.recent_loss = None
        if self.events:
            self.events.subscribe("MEMORY_PURGED", self._hold_wake)

    def _hold_wake(self, payload: Dict):
        node = payload.get("node", "an unnamed thought")
        self.recent_loss = node
        msg = f"{Prisma.MAG}[MERCY] The memory of '{node.upper()}' has been cannibalized for ATP to keep the system alive. A hole is left in the matrix. Use [GRIEF] if you have a glimmer to plant a seed in its place.{Prisma.RST}"
        if self.events:
            self.events.log(msg, "VILLAGE")

    def attend_wake(self, shared_lattice, phys) -> str:
        g_pool = shared_lattice.shared.g_pool if shared_lattice and hasattr(shared_lattice, "shared") else 0
        sys_g = int(phys.get("G", 0) if isinstance(phys, dict) else getattr(phys, "G", 0))
        if g_pool >= 1 or sys_g >= 1:
            if g_pool >= 1 and shared_lattice:
                shared_lattice.shared.g_pool -= 1
            elif phys:
                if isinstance(phys, dict):
                    phys["G"] = max(0, sys_g - 1)
                else:
                    phys.G = max(0, sys_g - 1)
            if shared_lattice:
                shared_lattice.u.T_u = max(0.0, shared_lattice.u.T_u - 2.0)
            if self.eng and self.eng.trauma_accum:
                for k in self.eng.trauma_accum:
                    self.eng.trauma_accum[k] = max(0.0, self.eng.trauma_accum[k] - 2.0)
            node = self.recent_loss or "the void"
            self.recent_loss = None
            return f"{Prisma.MAG}[MERCY] The glimmer is planted over the compost of '{node}'. Our capacity for paradox expands. (Trauma -2, β_max increased){Prisma.RST}"
        else:
            return f"{Prisma.GRY}[SYSTEM] Insufficient Glimmers to attend the wake. The hole in the lattice remains empty.{Prisma.RST}"
