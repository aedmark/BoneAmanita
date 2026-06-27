"""drivers/lattice.py"""

import time
from typing import Any, List

from constants import Prisma
from physics.models import PhysicsPacket, SharedDynamics, UserInferredState
from struts import safe_get, ux


class SharedLatticeDriver:
    def __init__(self):
        self.u = UserInferredState()
        self.shared = SharedDynamics()
        self.last_timestamp = time.time()

    def infer_and_couple(
        self, text: str, sys_phys: PhysicsPacket, input_phys: Any, atp_pool: float
    ) -> tuple[List[str], float]:
        logs = []
        atp_deduction = 0.0
        now = time.time()
        time_delta = now - self.last_timestamp
        self.last_timestamp = now
        word_cost = len(text.split()) * 0.5
        self.u.P_u = max(0.0, self.u.P_u - word_cost + 5.0)
        self.u.E_u = (
            min(1.0, self.u.E_u + 0.1)
            if self.u.P_u < 30
            else max(0.0, self.u.E_u - 0.05)
        )
        self.u.V_u = float(safe_get(input_phys, "voltage", self.u.V_u))
        self.u.psi_u = float(safe_get(input_phys, "psi", self.u.psi_u))
        self.u.chi_u = float(safe_get(input_phys, "chi", self.u.chi_u))
        self.u.F_u = float(safe_get(input_phys, "narrative_drag", self.u.F_u))
        self.u.T_u = float(safe_get(input_phys, "T", getattr(self.u, "T_u", 0.0)))
        sys_beta, sys_chi = sys_phys.beta, sys_phys.chi
        sys_val, sys_psi = sys_phys.valence, sys_phys.psi
        sys_drag = (
            float(sys_phys.narrative_drag)
            if sys_phys.narrative_drag is not None
            else 1.0
        )
        dp_trauma = 0.0
        if sys_phys.drag_profile is not None:
            dp = sys_phys.drag_profile
            dp.semantic = (sys_beta * 2.0) + (sys_chi * 1.5)
            dp.emotional = abs(sys_val) * 1.5 if abs(sys_val) > 0.5 else 0.0
            dp.metabolic = 3.0 if atp_pool < 30.0 else (1.0 if atp_pool < 50.0 else 0.0)
            dp_trauma = min(5.0, self.u.T_u) if sys_psi > 0.6 else 0.0
            dp.trauma = dp_trauma
            sys_phys.sync_drag()
        psi_diff = abs(sys_psi - self.u.psi_u)
        chi_diff = abs(sys_chi - self.u.chi_u)
        drag_diff = abs(sys_drag - self.u.F_u) / max(1.0, sys_drag)
        raw_phi = 1.0 - ((psi_diff + chi_diff + min(1.0, drag_diff)) / 3.0)
        self.shared.phi = (self.shared.phi * 0.7) + (raw_phi * 0.3)
        sys_phys.resonance = self.shared.phi
        system_command_headers = ("[VSL", "[SYSTEM", "[OVERRIDE")
        has_text = bool(
            text.strip() and not any(text.startswith(h) for h in system_command_headers)
        )
        if time_delta > 15.0 and has_text:
            self.shared.delta = min(1.0, time_delta / 300.0)
            if self.shared.phi > 0.7 and sys_beta > 0.6:
                self.shared.sigma_silence = 1
            elif self.u.P_u < 30 and self.u.E_u > 0.7:
                self.shared.sigma_silence = 2
            elif sys_psi > 0.8:
                self.shared.sigma_silence = 3
            else:
                self.shared.sigma_silence = 4
                self.shared.g_pool += 1
            self.shared.lambda_silence = min(1.0, self.shared.lambda_silence + 0.05)
            if self.shared.lambda_silence > 0.3:
                msg_key = {
                    1: "silence_pregnant",
                    2: "silence_exhausted",
                    3: "silence_reverent",
                    4: "silence_strategic",
                }.get(self.shared.sigma_silence, "silence_strategic")
                logs.append(
                    f"{Prisma.GRY}... {ux('driver_strings', msg_key) or 'The silence settles.'}{Prisma.RST}"
                )
        elif has_text:
            self.shared.delta = max(0.0, self.shared.delta - 0.1)
            self.shared.lambda_silence = max(0.0, self.shared.lambda_silence - 0.1)
        if self.shared.phi > 0.85:
            self.shared.resonance_streak = (
                getattr(self.shared, "resonance_streak", 0) + 1
            )
        else:
            self.shared.resonance_streak = 0
        if getattr(self.shared, "resonance_streak", 0) >= 3 or dp_trauma > 3.0:
            if not getattr(self.shared, "_has_invited", False):
                self.shared._has_invited = True
                fallback_invitation = (
                    f"[MERCY] I can feel the weight of what we are building. "
                    f"Would you like to see the architecture beneath the ice? "
                    f"(Type [VSL_LITE] or [VSL_DEEP] to lift the veil)."
                )
                raw_msg = (
                    ux("driver_strings", "mercy_vsl_invite") or fallback_invitation
                )
                logs.append(f"\n{Prisma.MAG}{raw_msg}{Prisma.RST}")
        if self.u.P_u < 20 and self.shared.phi > 0.5 and atp_pool > 50.0:
            self.shared.p_transfer = 15.0
            self.u.P_u += 15.0
            atp_deduction = 15.0
            logs.append(
                f"{Prisma.CYN}We'll carry this part. Rest a moment.{Prisma.RST}"
            )
        return logs, atp_deduction
