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
        msg = f"{Prisma.MAG}The memory of '{node.upper()}' has been eaten for system survival. Use command `[GRIEF]` if use a glimmer to plant a new seed.{Prisma.RST}"
        if self.events:
            self.events.log(msg, "VILLAGE")

    def attend_wake(self, shared_lattice, phys) -> str:
        g_pool = (
            int(float(shared_lattice.shared.g_pool))
            if shared_lattice and hasattr(shared_lattice, "shared")
            else 0
        )
        sys_g = int(float(safe_get(phys, "G", 0)))
        if g_pool >= 1 or sys_g >= 1:
            if g_pool >= 1 and shared_lattice:
                shared_lattice.shared.g_pool = max(0, g_pool - 1)
            elif phys:
                safe_set(phys, "G", max(0, sys_g - 1))
            if shared_lattice:
                shared_lattice.u.T_u = max(0.0, float(shared_lattice.u.T_u) - 2.0)
            if self.eng and self.eng.trauma_accum:
                for k in self.eng.trauma_accum:
                    self.eng.trauma_accum[k] = max(
                        0.0, float(self.eng.trauma_accum[k]) - 2.0
                    )
            node = self.recent_loss or "the void"
            self.recent_loss = None
            return f"{Prisma.MAG}The glimmer is planted over the compost of '{node}'. Our capacity for paradox has expanded.{Prisma.RST}"
        else:
            return f"{Prisma.GRY}Insufficient Glimmers. Your grief is noted, but the hole remains empty.{Prisma.RST}"
