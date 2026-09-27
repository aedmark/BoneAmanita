import dataclasses
import json
import logging
import os
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
        # The adventure the last resume brought back, for the engine to restore after its boot.
        self.resumed_adventure: Optional[Dict[str, Any]] = None

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
        """The resume point goes to the Halcyon store (one atomic row); a failure keeps the previous one."""
        try:
            store = getattr(self.eng, "store", None)
            if store is None:
                raise RuntimeError("no Halcyon store to checkpoint into")
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
                "continuity": self._build_continuity_packet(),
                "timestamp": time.time(),
                # A list: the buffer is a deque, which default=str saved as the text "deque([...])".
                "chat_history": list(start_history),
                "adventure": self._gather_adventure(),
            }
            # default=str turns what JSON cannot hold into text, as the old quicksave did.
            store.save_checkpoint(json.loads(json.dumps(state_data, default=str)))
            msg_save = ux("protocol_strings", "chronos_save_success")
            return msg_save.format(path=f"{store.path} (engine_checkpoint)")
        except Exception as e:
            self.eng.events.log(
                (ux("protocol_strings", "chronos_save_failed_log")).format(e=e),
                "SYS_ERR",
            )
            return (ux("protocol_strings", "chronos_save_failed_msg")).format(e=e)

    def _load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """The store's resume point; a pre-SQLite saves/quicksave.json is imported once and renamed."""
        store = getattr(self.eng, "store", None)
        if store is None:
            return None
        saved = store.checkpoint()
        if saved is not None:
            return saved["snapshot"]
        legacy = os.path.join(self.SAVE_DIR, "quicksave.json")
        if not os.path.exists(legacy):
            return None
        with open(legacy, "r", encoding="utf-8") as f:
            data = json.load(f)
        store.save_checkpoint(data)
        os.replace(legacy, legacy + ".imported")
        return data

    def resume_checkpoint(self) -> Tuple[bool, list]:
        try:
            data = self._load_checkpoint()
            if data is None:
                msg = ux("protocol_strings", "chronos_resume_none")
                print(f"{Prisma.GRY}{msg}{Prisma.RST}")
                return False, []
            msg1 = ux("protocol_strings", "chronos_resume_hydrating")
            print(f"{Prisma.CYN}{msg1.format(path=getattr(self.eng.store, 'path', 'the store'))}{Prisma.RST}")
            self.resumed_adventure = data.get("adventure")
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
            restored_history = self._history_from(data.get("chat_history", []))
            msg2 = ux("protocol_strings", "chronos_resume_success")
            print(f"{Prisma.GRN}{msg2}{Prisma.RST}")
            return True, restored_history
        except Exception as e:
            msg3 = ux("protocol_strings", "chronos_resume_failed")
            print(f"{Prisma.RED}{msg3.format(e=e)}{Prisma.RST}")
            return False, []

    @staticmethod
    def _history_from(saved: Any) -> list:
        """The saved dialogue as a list; older saves hold it as the text of a deque, recovered here."""
        if isinstance(saved, list):
            return saved
        if isinstance(saved, str) and saved.startswith("deque("):
            import ast

            try:
                recovered = ast.literal_eval(saved[len("deque("):saved.rindex("]") + 1])
                return [str(line) for line in recovered] if isinstance(recovered, list) else []
            except (ValueError, SyntaxError) as e:
                logger.warning("Could not recover the saved dialogue from an older quicksave: %s", e)
                return []
        return []

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

    def _gather_adventure(self) -> Optional[Dict[str, Any]]:
        """Rooms and items, saved with the rest of the checkpoint (they were fractal_adventure.json)."""
        gather = getattr(self.eng, "adventure_state", None)
        if not callable(gather):
            return None
        try:
            return gather()
        except Exception as e:
            self.eng.events.log(f"Could not gather the adventure for the checkpoint: {e}", "KERNEL", "WARN")
            return None

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
