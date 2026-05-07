"""protocols/chronos.py
The Chronos Keeper acts as the engine's memory persistence and time-management
layer. It is responsible for freezing the active biological and narrative state
of the system (health, stamina, trauma, current location) into a stable format,
saving it to disk, and successfully "hydrating" (reloading) the system upon
reboot. It ensures the engine doesn't wake up with amnesia.
"""
import json
import os
import time
from typing import Dict, Tuple, Any
from struts import ux, safe_get
from presets import BoneConfig
from constants import Prisma
from core import LoreManifest


class ChronosKeeper:
    """
    Manages the preservation and restoration of the system's temporal state.
    It builds 'continuity packets' so the system remembers where it was and
    what it was doing right before a shutdown or crash.
    """

    def __init__(self, engine_ref):
        """
        Initializes the ChronosKeeper with a reference to the main engine.
        Sets up the default directories for saves and crash logs.
        """
        self.eng = engine_ref
        self.SAVE_DIR = "saves"
        self.CRASH_DIR = "crashes"

    def _build_continuity_packet(self) -> Dict[str, Any]:
        """
        Constructs a small, critical footprint of the user's immediate context.
        This includes the 'physical' location in the narrative, the last spoken
        line, and any items currently held in inventory.
        Returns:
            Dict containing location, last output, and inventory state.
        """
        loc = "Void"
        if getattr(self.eng, "phys", None) and getattr(self.eng.phys, "observer", None):
            if last_pkt := getattr(self.eng.phys.observer, "last_physics_packet", None):
                space = safe_get(last_pkt, "space", {}) or {}
                loc = safe_get(last_pkt, "zone", safe_get(space, "zone", "Void"))
        last_speech = "Silence."
        if getattr(self.eng, "cortex", None) and getattr(self.eng.cortex, "dialogue_buffer", None):
            last_speech = self.eng.cortex.dialogue_buffer[-1]
        return {
            "location": loc,
            "last_output": last_speech,
            "inventory": self.eng.village.gordon.inventory if getattr(self.eng.village, "gordon", None) else [],
        }

    def save_checkpoint(self, history: list = None) -> str:
        """
        Creates a 'quicksave' of the current system state, including biological
        markers, active archetypes, and the chat history.
        Args:
            history (list, optional): The current chat history. Defaults to the cortex's buffer.
        Returns:
            A formatted string indicating success or failure to the UI.
        """
        try:
            os.makedirs(self.SAVE_DIR, exist_ok=True)
            continuity_packet = self._build_continuity_packet()
            start_history = (history if history is not None else self.eng.cortex.dialogue_buffer)
            state_data = {
                "health": self.eng.health,
                "stamina": self.eng.stamina,
                "trauma_accum": self.eng.trauma_accum,
                "soul_data": self.eng.soul.to_dict(),
                "village_data": self._gather_village_state(),
                "continuity": continuity_packet,
                "timestamp": time.time(),
                "chat_history": start_history,
            }
            path = os.path.join(self.SAVE_DIR, "quicksave.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2, default=str)
            msg_save = ux("protocol_strings", "chronos_save_success")
            return msg_save.format(path=path)
        except Exception as e:
            self.eng.events.log((ux("protocol_strings", "chronos_save_failed_log")).format(e=e), "SYS_ERR", )
            return (ux("protocol_strings", "chronos_save_failed_msg")).format(e=e)

    def resume_checkpoint(self) -> Tuple[bool, list]:
        """
        Attempts to load a quicksave from disk and hydrate the engine's subsystems
        with the frozen data.
        Returns:
            A tuple containing a boolean (True if successful) and the restored chat history.
        """
        path = os.path.join(self.SAVE_DIR, "quicksave.json")
        if not os.path.exists(path):
            msg = ux("protocol_strings", "chronos_resume_none")
            print(f"{Prisma.GRY}{msg}{Prisma.RST}")
            return False, []
        try:
            msg1 = ux("protocol_strings", "chronos_resume_hydrating")
            print(f"{Prisma.CYN}{msg1.format(path=path)}{Prisma.RST}")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.eng.health = data.get("health", 100.0)
            self.eng.stamina = data.get("stamina", 100.0)
            self.eng.trauma_accum = data.get("trauma_accum", {})
            if "soul_data" in data and hasattr(self.eng, "soul"):
                self.eng.soul.load_from_dict(data["soul_data"])
            if "village_data" in data:
                self._restore_village_state(data["village_data"])
            if "continuity" in data:
                self.eng.embryo.continuity = data["continuity"]
                if "inventory" in data["continuity"] and getattr(self.eng.village, "gordon", None):
                    self.eng.village.gordon.inventory = data["continuity"]["inventory"]
            restored_history = data.get("chat_history", [])
            msg2 = ux("protocol_strings", "chronos_resume_success")
            print(f"{Prisma.GRN}{msg2}{Prisma.RST}")
            return True, restored_history
        except Exception as e:
            msg3 = ux("protocol_strings", "chronos_resume_failed")
            print(f"{Prisma.RED}{msg3.format(e=e)}{Prisma.RST}")
            return False, []

    def perform_shutdown(self):
        """
        Executes a controlled, graceful shutdown sequence. It triggers a SYSTEM_HALT
        event, freezes the current biological and mnemonic state, and asks all major
        subsystems to persist their data to disk before terminating.
        """
        msg = ux("protocol_strings", "chronos_halt")
        print(f"{Prisma.GRY}{msg}{Prisma.RST}")
        self.eng.events.publish("SYSTEM_HALT", {"tick": self.eng.tick_count})
        continuity_packet = self._build_continuity_packet()
        try:
            msg2 = ux("protocol_strings", "chronos_freezing")
            print(f"{Prisma.GRY}{msg2}{Prisma.RST}")

            bio = getattr(self.eng, "bio", None)
            phys = getattr(self.eng, "phys", None)

            mito_traits = bio.mito.state.__dict__ if bio and getattr(bio, "mito", None) else {}
            immune_data = list(bio.immune.active_antibodies) if bio and getattr(bio, "immune", None) else []
            atlas = phys.nav.export_atlas() if phys and getattr(phys, "nav", None) else {}

            soul_data = self.eng.soul.to_dict() if getattr(self.eng, "soul", None) else {}
            if getattr(self.eng, "mind", None) and getattr(self.eng.mind, "mem", None):
                self.eng.mind.mem.save(
                    health=getattr(self.eng, "health", 0.0),
                    stamina=getattr(self.eng, "stamina", 0.0),
                    mutations={},
                    trauma_accum=getattr(self.eng, "trauma_accum", {}),
                    joy_history=[],
                    mitochondria_traits=mito_traits,
                    antibodies=immune_data,
                    soul_data=soul_data,
                    village_data=self._gather_village_state(),
                    continuity=continuity_packet,
                    world_atlas=atlas,
                )
        except Exception as e:
            msg3 = ux("protocol_strings", "chronos_mem_save_fail")
            print(f"{Prisma.RED}{msg3.format(e=e)}{Prisma.RST}")
        subsystems = [
            ("LEXICON", self.eng.lex, "save"),
            ("AKASHIC", self.eng.akashic, "save_all"),
        ]
        for name, sys, method in subsystems:
            if hasattr(sys, method):
                try:
                    msg4 = ux("protocol_strings", "chronos_persisting")
                    print(f"{Prisma.GRY}{msg4.format(name=name)}{Prisma.RST}")
                    getattr(sys, method)()
                except Exception as e:
                    msg5 = ux("protocol_strings", "chronos_persist_fail")
                    if hasattr(self.eng, "events"):
                        self.eng.events.log(
                            f"Subsystem Persistence Error [{name}]: {e}", "SYS_ERR")
                    print(
                        f"{Prisma.OCHRE}{msg5.format(name=name, e='The connection severed before it could be written.')}{Prisma.RST}"
                    )

    def _gather_village_state(self) -> Dict[str, Any]:
        """
        Iterates over the active archetype instances ('The Village') and serializes
        their internal states so they don't lose character progress upon reboot.
        """
        return {
            name: comp.to_dict()
            for name, comp in vars(self.eng.village).items()
            if comp and hasattr(comp, "to_dict")
        }

    def _restore_village_state(self, state_data: Dict[str, Any]):
        """
        Takes serialized archetype data and injects it back into the active Village
        components during the hydration process.
        """
        if not state_data:
            return
        for name, data in state_data.items():
            comp = getattr(self.eng.village, name, None)
            if hasattr(comp, "load_state"):
                try:
                    comp.load_state(data)
                except Exception as e:
                    msg = ux("protocol_strings", "chronos_hydrate_fail")
                    if hasattr(self.eng, "events"):
                        self.eng.events.log(f"Village Hydration Error [{name}]: {e}", "SYS_ERR")
                    print(f"{Prisma.OCHRE}{msg.format(name=name, e='Trauma prevented full recall.')}{Prisma.RST}")

    def get_crash_path(self, prefix="crash"):
        """
        Generates a secure filepath for dumping system state during an unrecoverable
        error. It also automatically prunes old crash logs to prevent disk bloat.
        Args:
            prefix (str): File prefix, usually 'crash'.
        Returns:
            The full path string where the crash data should be written.
        """
        os.makedirs(self.CRASH_DIR, exist_ok=True)
        try:
            files = sorted([f for f in os.listdir(self.CRASH_DIR) if f.startswith(prefix)])
            target_cfg = getattr(self.eng, "config", BoneConfig) if self.eng else BoneConfig
            cfg = getattr(target_cfg, "CHRONOS", object())
            kept = getattr(cfg, "CRASH_FILES_KEPT", 4)
            for oldest in files[:-kept] if kept > 0 else files:
                os.remove(os.path.join(self.CRASH_DIR, oldest))
        except Exception:
            pass
        return os.path.join(self.CRASH_DIR, f"{prefix}_{int(time.time())}.json")

    @staticmethod
    def emergency_dump(exit_cause="UNKNOWN") -> str:
        """
        Provides a fast, localized terminal output message when an absolute
        emergency forces the system down before state can be saved.
        """
        msg = ux("protocol_strings", "chronos_emerg_dump")
        return msg.format(exit_cause=exit_cause)
