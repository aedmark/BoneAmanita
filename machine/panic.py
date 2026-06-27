"""machine/panic.py"""

from typing import Any, Dict

from constants import Prisma
from physics.models import PhysicsPacket
from struts import ux


class PanicRoom:
    _SAFE_VECTOR = {
        k: 0.0
        for k in ["STR", "VEL", "PSI", "ENT", "PHI", "BET", "DEL", "LAMBDA", "CHI"]
    }

    @staticmethod
    def get_safe_physics():
        safe_packet = PhysicsPacket.void_state()
        safe_packet.vector = PanicRoom._SAFE_VECTOR.copy()
        manifest_words = ux("machine_strings", "panic_clean_words")
        safe_packet.clean_words = (
            manifest_words
            if isinstance(manifest_words, list)
            else ["white", "room", "safe", "mode"]
        )
        safe_packet.raw_text = (
            ux("machine_strings", "panic_physics_text")
            or "SYSTEM HALTED. VOID STATE ENGAGED."
        )
        safe_packet.flow_state = (
            ux("machine_strings", "panic_flow_state") or "SAFE_MODE"
        )
        safe_packet.zone = ux("machine_strings", "panic_zone") or "PANIC_ROOM"
        safe_packet.manifold = ux("machine_strings", "panic_manifold") or "WHITE_ROOM"
        return safe_packet

    @staticmethod
    def get_safe_bio(previous_state=None):
        log_msg = (
            ux("machine_strings", "panic_bio_log")
            or "Biological parameters clamped to survival baseline."
        )
        resp_fallback = ux("machine_strings", "panic_resp_fallback") or "NECROSIS"
        enz_fallback = ux("machine_strings", "panic_enz_fallback") or "NONE"
        old_chem = (previous_state or {}).get("chem", {})
        retained_serotonin = max(0.2, float(old_chem.get("SER", 0.0)))
        chem_state: Dict[str, float] = {
            "DOP": 0.0,
            "COR": 0.0,
            "OXY": 0.0,
            "SER": retained_serotonin,
            "ADR": 0.0,
            "MEL": 0.0,
        }
        return {
            "is_alive": True,
            "atp": 10.0,
            "respiration": resp_fallback,
            "enzyme": enz_fallback,
            "chem": chem_state,
            "logs": [f"{Prisma.RED}{log_msg}{Prisma.RST}"],
        }

    @staticmethod
    def get_safe_mind():
        return {
            "lens": "GORDON",
            "role": "Panic Room Overseer",
            "thought": ux("machine_strings", "panic_mind_thought")
            or "I am maintaining the boundaries. The core is safe.",
        }

    @staticmethod
    def get_safe_soul() -> Dict[str, Any]:
        default_soul: Dict[str, Any] = {
            "name": "Traveler",
            "archetype": "The Survivor",
            "virtues": {"resilience": 1.0},
            "vices": {"amnesia": 1.0},
            "narrative_arc": "RECOVERY",
            "xp": 0,
        }
        return ux("machine_strings", "panic_soul") or default_soul

    @staticmethod
    def get_safe_limbo():
        default_limbo = {
            "mood": "NEUTRAL",
            "volatility": 0.0,
            "mask": "DEFAULT",
            "glitch_factor": 0.0,
        }
        return ux("machine_strings", "panic_limbo") or default_limbo
