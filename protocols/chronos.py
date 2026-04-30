"""protocols/chronos.py"""

import json
import os
import time
from typing import Dict, Tuple, Any
from struts import ux, safe_get
from presets import BoneConfig
from constants import Prisma
from core import LoreManifest

NARRATIVE_DATA = LoreManifest.get_instance().get("narrative_data") or {}

class ChronosKeeper:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.SAVE_DIR = "saves"
        self.CRASH_DIR = "crashes"

    def _build_continuity_packet(self) -> Dict[str, Any]:
        loc = "Void"
        if getattr(self.eng, "phys", None) and getattr(self.eng.phys, "observer", None):
            if last_pkt := getattr(self.eng.phys.observer, "last_physics_packet", None):
                space = safe_get(last_pkt, "space", {}) or {}
                loc = safe_get(last_pkt, "zone", safe_get(space, "zone", "Void"))
        last_speech = "Silence."
        if getattr(self.eng, "cortex", None) and getattr(self.eng.cortex, "dialogue_buffer", None):
            last_speech = self.eng.cortex.dialogue_buffer[-1]
        return {"location":
                    loc, "last_output":
                    last_speech, "inventory":
                    self.eng.gordon.inventory if getattr(self.eng, "gordon", None) else [], }

    def save_checkpoint(self, history: list = None) -> str:
        try:
            os.makedirs(self.SAVE_DIR, exist_ok=True)
            continuity_packet = self._build_continuity_packet()
            start_history = (history if history is not None else
                             self.eng.cortex.dialogue_buffer)
            state_data = {"health": self.eng.health, "stamina": self.eng.stamina, "trauma_accum": self.eng.trauma_accum,
                          "soul_data": self.eng.soul.to_dict(), "village_data": self._gather_village_state(),
                          "continuity": continuity_packet, "timestamp": time.time(), "chat_history": start_history, }
            path = os.path.join(self.SAVE_DIR, "quicksave.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2, default=str)
            msg_save = ux("protocol_strings", "chronos_save_success")
            return msg_save.format(path=path)
        except Exception as e:
            self.eng.events.log((ux("protocol_strings", "chronos_save_failed_log")).format(e=e), "SYS_ERR",)
            return (ux("protocol_strings", "chronos_save_failed_msg")).format(e=e)

    def resume_checkpoint(self) -> Tuple[bool, list]:
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
                if "inventory" in data["continuity"] and self.eng.gordon:
                    self.eng.gordon.inventory = data["continuity"]["inventory"]
            restored_history = data.get("chat_history", [])
            msg2 = ux("protocol_strings", "chronos_resume_success")
            print(f"{Prisma.GRN}{msg2}{Prisma.RST}")
            return True, restored_history
        except Exception as e:
            msg3 = ux("protocol_strings", "chronos_resume_failed")
            print(f"{Prisma.RED}{msg3.format(e=e)}{Prisma.RST}")
            return False, []

    def perform_shutdown(self):
        msg = ux("protocol_strings", "chronos_halt")
        print(f"{Prisma.GRY}{msg}{Prisma.RST}")
        self.eng.events.publish("SYSTEM_HALT", {"tick": self.eng.tick_count})
        continuity_packet = self._build_continuity_packet()
        try:
            msg2 = ux("protocol_strings", "chronos_freezing")
            print(f"{Prisma.GRY}{msg2}{Prisma.RST}")
            mito_traits = {}
            if getattr(self.eng, "bio", None) and getattr(self.eng.bio, "mito", None) and hasattr(self.eng.bio.mito, "state"):
                mito_traits = self.eng.bio.mito.state.__dict__
            atlas = {}
            if getattr(self.eng, "phys", None) and getattr(self.eng.phys, "nav", None):
                atlas = getattr(self.eng.phys.nav, "export_atlas", lambda: {})()
            immune_data = list(self.eng.bio.immune.active_antibodies) if getattr(self.eng, "bio", None) and getattr(self.eng.bio, "immune", None) else []
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
        subsystems = [("LEXICON", self.eng.lex, "save"),("AKASHIC", self.eng.akashic, "save_all"),]
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
        return {
            name: comp.to_dict()
            for name, comp in self.eng.village.items()
            if comp and hasattr(comp, "to_dict")
        }

    def _restore_village_state(self, state_data: Dict[str, Any]):
        if not state_data:
            return
        for name, data in state_data.items():
            comp = self.eng.village.get(name)
            if hasattr(comp, "load_state"):
                try:
                    comp.load_state(data)
                except Exception as e:
                    msg = ux("protocol_strings", "chronos_hydrate_fail")
                    if hasattr(self.eng, "events"):
                        self.eng.events.log(f"Village Hydration Error [{name}]: {e}", "SYS_ERR")
                    print(f"{Prisma.OCHRE}{msg.format(name=name, e='Trauma prevented full recall.')}{Prisma.RST}")

    def get_crash_path(self, prefix="crash"):
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
        msg = ux("protocol_strings", "chronos_emerg_dump")
        return msg.format(exit_cause=exit_cause)