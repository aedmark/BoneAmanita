"""machine/panic.py
The Panic Room (The White Room).
This module acts as the absolute bottom of the architectural safety net.
If the system experiences a terminal hallucination, infinite sycophantic loop,
or lethal Apoptotic crash, it drops all corrupted state and reboots into these
hardcoded, mathematically sterile parameters.
"""
from typing import Dict
from struts import ux, safe_get
from constants import Prisma
from physics.models import PhysicsPacket


class PanicRoom:
    _SAFE_VECTOR = {k: 0.0 for k in ["STR", "VEL", "PSI", "ENT", "PHI", "BET", "DEL", "LAMBDA", "CHI"]}

    @staticmethod
    def get_safe_physics():
        """
        Creates a structurally inert physics packet.
        Zero voltage, zero drag, zero entropy. It places the user in a featureless
        'White Room' to prevent any poisoned semantic geometry from cascading.
        """
        safe_packet = PhysicsPacket.void_state()
        safe_packet.voltage = 0.0
        safe_packet.narrative_drag = 0.0
        safe_packet.exhaustion = 0.0
        safe_packet.beta_index = 0.0
        safe_packet.psi = 0.0
        safe_packet.chi = 0.0
        safe_packet.entropy = 0.0
        safe_packet.valence = 0.0
        safe_packet.kappa = 0.0
        safe_packet.vector = PanicRoom._SAFE_VECTOR.copy()
        manifest_words = ux("machine_strings", "panic_clean_words")
        safe_packet.clean_words = (
            manifest_words if isinstance(manifest_words, list) else ["white", "room", "safe", "mode"]
        )
        safe_packet.raw_text = ux("machine_strings", "panic_physics_text") or "SYSTEM HALTED. VOID STATE ENGAGED."
        safe_packet.flow_state = ux("machine_strings", "panic_flow_state") or "SAFE_MODE"
        safe_packet.zone = ux("machine_strings", "panic_zone") or "PANIC_ROOM"
        safe_packet.manifold = ux("machine_strings", "panic_manifold") or "WHITE_ROOM"
        return safe_packet

    @staticmethod
    def get_safe_bio(previous_state=None):
        """
        Forces the biological engine into a baseline survival state.
        Zeros out all high-energy and toxic chemicals (Adrenaline, Cortisol),
        but intentionally retains a trace of Serotonin to prevent total depressive collapse.
        """
        log_msg = ux("machine_strings",
                     "panic_bio_log") or "APOPTOTIC RESET: Biological parameters clamped to survival baseline."
        resp_fallback = ux("machine_strings", "panic_resp_fallback") or "NECROSIS"
        enz_fallback = ux("machine_strings", "panic_enz_fallback") or "NONE"
        old_chem = safe_get(previous_state or {}, "chem", {})
        retained_serotonin = max(0.2, float(safe_get(old_chem, "SER", 0.0)))
        chem_state: Dict[str, float] = {
            "DOP": 0.0,
            "COR": 0.0,
            "OXY": 0.0,
            "SER": retained_serotonin,
            "ADR": 0.0,
            "MEL": 0.0
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
        """
        Hardcodes the active cognitive lens to Gordon.
        As the immovable anchor and boundary enforcer, Gordon is the only archetype
        structurally rigid enough to oversee the Panic Room.
        """
        return {
            "lens": "GORDON",
            "role": "Panic Room Overseer",
            "thought": ux("machine_strings",
                          "panic_mind_thought") or "I am maintaining the boundaries. The core is safe."
        }

    @staticmethod
    def get_safe_soul():
        """
        Resets the user's narrative self to a basic 'Survivor' state.
        Applies 'amnesia' as a vice to narratively justify the sudden loss of context.
        """
        default_soul = {
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
        """
        Stabilizes the emotional and glitch layers of the simulation.
        Ensures the UI and downstream renderers do not attempt to draw corrupted states.
        """
        default_limbo = {
            "mood": "NEUTRAL",
            "volatility": 0.0,
            "mask": "DEFAULT",
            "glitch_factor": 0.0
        }
        return ux("machine_strings", "panic_limbo") or default_limbo
