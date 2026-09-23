import dataclasses
import json
import logging
import os
import tempfile
import time
from typing import Any, Dict, Optional, Tuple

from engine.constants import Prisma
from engine.presets import BoneConfig
from engine.struts import safe_get, ux

logger = logging.getLogger("bone")


class ChronosKeeper:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.SAVE_DIR = "saves"
        self.CRASH_DIR = "crashes"

    def _build_continuity_packet(self) -> Dict[str, Any]:
        active_phys = getattr(self.eng, "active_physics", {})
        space = safe_get(active_phys, "space", {}) or {}
        loc = safe_get(active_phys, "zone", safe_get(space, "zone", "Void"))
        cortex = safe_get(self.eng, "cortex")
        buf = safe_get(cortex, "dialogue_buffer") if cortex else []
        last_speech = buf[-1] if buf else "Silence."
        return {
            "location": loc,
            "last_output": last_speech,
            "inventory": self.eng.village.gordon.inventory
            if getattr(self.eng.village, "gordon", None)
            else [],
            "kernel_hash": getattr(self.eng, "kernel_hash", "UNKNOWN"),
        }

    def save_checkpoint(self, history: Optional[list] = None) -> str:
        temp_path = None
        try:
            os.makedirs(self.SAVE_DIR, exist_ok=True)
            continuity_packet = self._build_continuity_packet()
            start_history = (
                history if history is not None else self.eng.cortex.dialogue_buffer
            )
            state_data = {
                "health": self.eng.health,
                "stamina": self.eng.stamina,
                "trauma_accum": self.eng.trauma_accum,
                "soul_data": self.eng.soul.to_dict(),
                "village_data": self._gather_village_state(),
                "user_model": self._gather_user_model(),
                "continuity": continuity_packet,
                "timestamp": time.time(),
                "chat_history": start_history,
            }
            path = os.path.join(self.SAVE_DIR, "quicksave.json")
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.SAVE_DIR,
                prefix=".quicksave-",
                suffix=".tmp",
                delete=False,
            ) as f:
                temp_path = f.name
                json.dump(state_data, f, indent=2, default=str)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, path)
            temp_path = None
            msg_save = ux("protocol_strings", "chronos_save_success")
            return msg_save.format(path=path)
        except Exception as e:
            self.eng.events.log(
                (ux("protocol_strings", "chronos_save_failed_log")).format(e=e),
                "SYS_ERR",
            )
            return (ux("protocol_strings", "chronos_save_failed_msg")).format(e=e)
        finally:
            if temp_path is not None:
                try:
                    os.unlink(temp_path)
                except OSError as e:
                    logger.warning(
                        "Could not remove checkpoint temporary file %s: %s", temp_path, e
                    )

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
            if "user_model" in data:
                self._restore_user_model(data["user_model"])
            if "continuity" in data:
                self.eng.embryo.continuity = data["continuity"]
                saved_hash = data["continuity"].get("kernel_hash", "UNKNOWN")
                current_hash = getattr(self.eng, "kernel_hash", "UNKNOWN")
                if saved_hash != "UNKNOWN" and saved_hash != current_hash:
                    print(
                        f"{Prisma.VIOLET}Temporal fracture detected. Bridging timeline [{saved_hash}] into [{current_hash}].{Prisma.RST}"
                    )
                else:
                    print(
                        f"{Prisma.GRY}Timeline absolute. Kernel Hash [{current_hash}] locked.{Prisma.RST}"
                    )
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
            bio = safe_get(self.eng, "bio")
            bio_dict = bio.to_dict() if hasattr(bio, "to_dict") else {}
            mito_traits = bio_dict.get("mito", {})
            immune = safe_get(bio, "immune")
            immune_data = list(immune.active_antibodies) if immune else []
            phys = safe_get(self.eng, "phys")
            nav = safe_get(phys, "nav")
            atlas = nav.to_dict() if hasattr(nav, "to_dict") else {}
            soul = safe_get(self.eng, "soul")
            soul_data = soul.to_dict() if hasattr(soul, "to_dict") else {}
            mind = safe_get(self.eng, "mind")
            mem = safe_get(mind, "mem")
            if mem and hasattr(mem, "save"):
                mem.save(
                    health=float(safe_get(self.eng, "health", 0.0)),
                    stamina=float(safe_get(self.eng, "stamina", 0.0)),
                    mutations={},
                    trauma_accum=safe_get(self.eng, "trauma_accum", {}),
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
                            f"Subsystem Persistence Error [{name}]: {e}", "SYS_ERR"
                        )
                    print(
                        f"{Prisma.OCHRE}{msg5.format(name=name, e='The connection severed before it could be written.')}{Prisma.RST}"
                    )

    def _gather_village_state(self) -> Dict[str, Any]:
        return {
            name: comp.to_dict()
            for name, comp in vars(self.eng.village).items()
            if comp and hasattr(comp, "to_dict")
        }

    def _gather_user_model(self) -> Dict[str, Any]:
        lattice = getattr(self.eng, "shared_lattice", None)
        u = getattr(lattice, "u", None)
        if u is None:
            return {}
        return {f.name: getattr(u, f.name) for f in dataclasses.fields(u)}

    def _restore_user_model(self, data: Dict[str, Any]):
        lattice = getattr(self.eng, "shared_lattice", None)
        u = getattr(lattice, "u", None)
        if u is None or not data:
            return
        known = {f.name for f in dataclasses.fields(u)}
        for key, value in data.items():
            if key in known:
                setattr(u, key, value)

    def _restore_village_state(self, state_data: Dict[str, Any]):
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
                        self.eng.events.log(
                            f"Village Hydration Error [{name}]: {e}", "SYS_ERR"
                        )
                    print(
                        f"{Prisma.OCHRE}{msg.format(name=name, e='Trauma prevented full recall.')}{Prisma.RST}"
                    )

    def get_crash_path(self, prefix="crash"):
        os.makedirs(self.CRASH_DIR, exist_ok=True)
        try:
            files = sorted(
                [f for f in os.listdir(self.CRASH_DIR) if f.startswith(prefix)]
            )
            target_cfg = (
                getattr(self.eng, "config", BoneConfig) if self.eng else BoneConfig
            )
            cfg = safe_get(target_cfg, "CHRONOS", {})
            kept = int(safe_get(cfg, "CRASH_FILES_KEPT", 4))
            for oldest in files[:-kept] if kept > 0 else files:
                os.remove(os.path.join(self.CRASH_DIR, oldest))
        except OSError as e:
            logger.warning(
                f"{Prisma.YEL}Could not prune old crash dumps in {self.CRASH_DIR}: "
                f"{type(e).__name__}: {e}. The dump itself is unaffected.{Prisma.RST}"
            )
        return os.path.join(self.CRASH_DIR, f"{prefix}_{int(time.time())}.json")

    @staticmethod
    def emergency_dump(exit_cause="UNKNOWN") -> str:
        msg = ux("protocol_strings", "chronos_emerg_dump")
        return msg.format(exit_cause=exit_cause)
