import os
import json
import time
from typing import Tuple, Dict, Any
from bone_types import Prisma


class ChronosKeeper:
    def __init__(self, engine_ref):
        self.eng = engine_ref
        self.SAVE_DIR = "saves"
        self.CRASH_DIR = "crashes"

    def save_checkpoint(self, history: list = None) -> str:
        try:
            if not os.path.exists(self.SAVE_DIR):
                os.makedirs(self.SAVE_DIR)
            last_phys = getattr(self.eng.cortex, "last_physics", None) or {}
            world_data = self.eng.cortex.gather_state(last_phys).get("world", {})
            loc = world_data.get("orbit", ["Void"])[0]
            last_speech = "Silence."
            if self.eng.cortex.dialogue_buffer:
                last_speech = self.eng.cortex.dialogue_buffer[-1]
            continuity_packet = {
                "location": loc,
                "last_output": last_speech,
                "inventory": self.eng.gordon.inventory if self.eng.gordon else [],
            }
            start_history = (
                history if history is not None else self.eng.cortex.dialogue_buffer
            )
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
            return f"✔ Checkpoint Saved: {path}"
        except Exception as e:
            self.eng.events.log(f"SAVE FAILED: {e}", "SYS_ERR")
            return f"❌ Save Failed: {e}"

    def resume_checkpoint(self) -> Tuple[bool, list]:
        path = os.path.join(self.SAVE_DIR, "quicksave.json")
        if not os.path.exists(path):
            print(
                f"{Prisma.GRY}[RESUME]: No quicksave found. Starting fresh.{Prisma.RST}"
            )
            return False, []
        try:
            print(f"{Prisma.CYN}[RESUME]: Hydrating from {path}...{Prisma.RST}")
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
            print(f"{Prisma.GRN}[RESUME]: System State & Logs Restored.{Prisma.RST}")
            return True, restored_history
        except Exception as e:
            print(f"{Prisma.RED}[RESUME]: Failed to hydrate: {e}{Prisma.RST}")
            return False, []

    def perform_shutdown(self):
        print(f"{Prisma.GRY}...System Halt...{Prisma.RST}")
        self.eng.events.publish("SYSTEM_HALT", {"tick": self.eng.tick_count})
        last_phys = getattr(self.eng.cortex, "last_physics", {})
        world_data = self.eng.cortex.gather_state(last_phys).get("world", {})
        continuity_packet = {
            "location": world_data.get("orbit", ["Void"])[0],
            "last_output": (
                self.eng.cortex.dialogue_buffer[-1]
                if self.eng.cortex.dialogue_buffer
                else "Silence."
            ),
            "inventory": self.eng.gordon.inventory if self.eng.gordon else [],
        }
        try:
            print(f"{Prisma.GRY}[MEMORY]: Freezing State...{Prisma.RST}")
            mito_traits = {}
            if hasattr(self.eng.bio.mito, "state"):
                mito_traits = self.eng.bio.mito.state.__dict__
            self.eng.mind.mem.save(
                health=self.eng.health,
                stamina=self.eng.stamina,
                mutations={},
                trauma_accum=self.eng.trauma_accum,
                joy_history=[],
                mitochondria_traits=mito_traits,
                antibodies=list(self.eng.bio.immune.active_antibodies),
                soul_data=self.eng.soul.to_dict(),
                village_data=self._gather_village_state(),
                continuity=continuity_packet,
                world_atlas=(
                    self.eng.phys.nav.export_atlas()
                    if hasattr(self.eng.phys, "nav")
                    else {}
                ),
            )
        except Exception as e:
            print(f"{Prisma.RED}[MEMORY]: Save Failed: {e}{Prisma.RST}")
        subsystems = [
            ("LEXICON", self.eng.lex, "save"),
            ("AKASHIC", self.eng.akashic, "save_all"),
        ]
        for name, sys, method in subsystems:
            if hasattr(sys, method):
                try:
                    print(f"{Prisma.GRY}[{name}]: Persisting...{Prisma.RST}")
                    getattr(sys, method)()
                except Exception as e:
                    print(f"{Prisma.RED}[{name}]: Failed: {e}{Prisma.RST}")

    def _gather_village_state(self) -> Dict[str, Any]:
        state = {}
        for name, component in self.eng.village.items():
            if component and hasattr(component, "to_dict"):
                state[name] = component.to_dict()
        return state

    def _restore_village_state(self, state_data: Dict[str, Any]):
        if not state_data:
            return
        for name, data in state_data.items():
            if (
                name in self.eng.village
                and self.eng.village[name]
                and hasattr(self.eng.village[name], "load_state")
            ):
                try:
                    self.eng.village[name].load_state(data)
                except Exception as e:
                    print(
                        f"{Prisma.RED}[RESUME]: Failed to hydrate {name}: {e}{Prisma.RST}"
                    )

    def get_crash_path(self, prefix="crash"):
        if not os.path.exists(self.CRASH_DIR):
            try:
                os.makedirs(self.CRASH_DIR)
            except OSError:
                pass
        try:
            files = sorted(
                [f for f in os.listdir(self.CRASH_DIR) if f.startswith(prefix)]
            )
            for oldest in files[:-4]:
                os.remove(os.path.join(self.CRASH_DIR, oldest))
        except Exception:
            pass
        return os.path.join(self.CRASH_DIR, f"{prefix}_{int(time.time())}.json")

    @staticmethod
    def emergency_dump(exit_cause="UNKNOWN") -> str:
        return f"✔ Emergency Dump: {exit_cause}"
