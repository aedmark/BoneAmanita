"""/soul/oroboros.py"""

import json
import os
import random
from dataclasses import dataclass
from typing import List, Any

from constants import Prisma
from core import LoreManifest
from soul import NarrativeSelf
# The soul does not exist in a vacuum. It sits atop the physical layer (akashic, core, struts)
# and translates metabolic states (ATP, voltage) into narrative meaning.
from presets import BoneConfig
from struts import ux, ux_format, safe_get, safe_set


@dataclass
class Scar:
    """A mechanical penalty passed on to the next generation upon death."""
    name: str
    stat_affected: str
    value: float
    description: str

@dataclass
class Myth:
    """A core lesson extracted from the previous generation's strongest memory."""
    title: str
    lesson: str
    trigger: str

class TheOroboros:
    """
    The generational bridging system.
    When the system hits a terminal state (Starvation, Toxicity collapse), it 'dies'.
    However, the corpse fertilizes the soil. Scars and Myths are written to `legacy.json`
    and physically alter the physics constraints of the *next* boot-up.
    """
    LEGACY_FILE = "legacy.json"

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.scars: List[Scar] = []
        self.myths: List[Myth] = []
        self.generation_count = 0
        self._load()

    def _cfg(self, key: str, default: Any) -> Any:
        cfg_obj = getattr(self.cfg, "OROBOROS", None)
        return getattr(cfg_obj, key, default)

    def _load(self):
        if not os.path.exists(self.LEGACY_FILE):
            return
        try:
            with open(self.LEGACY_FILE) as f:
                data = json.load(f)
                self.generation_count = data.get("generation", 0)
                self.scars = [Scar(**s) for s in data.get("scars", [])]
                self.myths = [Myth(**m) for m in data.get("myths", [])]
            msg = ux("soul_strings", "oroboros_gen_loaded")
            print(f"{Prisma.VIOLET}{msg.format(gen=self.generation_count)}{Prisma.RST}")
        except Exception as e:
            print(f"{Prisma.RED}[OROBOROS]: Legacy state corrupted or missing. Starting fresh. ({e}){Prisma.RST}")

    def crystallize(self, cause_of_death: str, soul: NarrativeSelf):
        """
        Executed on death. Maps the accumulated trauma and highest voltage memories
        into permanent structural changes for the next generation.
        """
        death_data = LoreManifest.get_instance().get("DEATH") or {}
        new_scars, new_myths = [], []
        eng = getattr(soul, "eng", None)

        # Heavy trauma leaves an Existential Dread scar on the baseline.
        if eng and getattr(eng, "trauma_accum", None):
            total_trauma = sum(eng.trauma_accum.values())
            if total_trauma > 10.0:
                scar_val = min(20.0, total_trauma * 0.1)
                new_scars.append(Scar(name="Existential Dread", stat_affected="trauma_baseline", value=scar_val, description=f"The lattice remembers a heavy collapse (Trauma: {round(total_trauma, 1)})."))

        if entry := death_data.get(cause_of_death):
            verdict_map = {"TOXICITY": "TOXIC", "BOREDOM": "BORING", "STARVATION": "LIGHT"}
            v_key = verdict_map.get(cause_of_death, "HEAVY")
            v_list = death_data.get("VERDICTS", {}).get(v_key)
            desc = random.choice(v_list) if isinstance(v_list, list) and v_list else entry[3]
            new_scars.append(Scar(entry[0], entry[1], entry[2], desc))

        # The strongest core memory becomes a Generational Myth.
        if soul.core_memories:
            strongest = max(soul.core_memories, key=lambda m: m.impact_voltage)
            trigger_word = strongest.trigger_words[0] if strongest.trigger_words else (ux("soul_strings", "oroboros_def_trigger") or "Silence")
            new_myths.append(Myth(title=(ux("soul_strings", "oroboros_myth_title") or "The Myth of {trigger}").format(trigger=trigger_word.title()), lesson=strongest.lesson, trigger=trigger_word))

        self.scars.extend(new_scars)
        self.scars = self.scars[-self._cfg("MAX_SCARS", 5):]
        self.myths.extend(new_myths)
        self.myths = self.myths[-self._cfg("MAX_MYTHS", 10):]

        # Enforce atomic writes so the generational lineage is never corrupted mid-death.
        payload = {"generation": self.generation_count + 1, "scars": [vars(s) for s in self.scars], "myths": [vars(m) for m in self.myths]}
        temp_path = f"{self.LEGACY_FILE}.tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self.LEGACY_FILE)
        except Exception as e:
            print(f"{Prisma.RED}[OROBOROS]: Failed to write legacy payload: {e}{Prisma.RST}")

        return ux_format("soul_strings", "generation_encoded", gen=self.generation_count + 1, scars=len(new_scars), myths=len(new_myths))

    def apply_legacy(self, physics: Any, bio: Any):
        """
        Executed on boot. Injects the inherited Scars directly into the active
        physics and biology packets, permanently altering how the new generation plays.
        """
        log = []
        if not physics: return log

        for scar in self.scars:
            # Support dynamic scar targets from the Lore Manifest.
            if scar.stat_affected == "voltage_cap":
                safe_set(physics, "voltage", max(0.0, safe_get(physics, "voltage", 0.0) - self._cfg("VOLTAGE_PENALTY", 5.0)))
                if msg := ux_format("soul_strings", "scar_voltage", name=scar.name): log.append(msg)
            elif scar.stat_affected == "trauma_baseline":
                t_vec = safe_get(bio, "trauma_vector") or {}
                safe_set(t_vec, "EXISTENTIAL", safe_get(t_vec, "EXISTENTIAL", 0.0) + scar.value)
                safe_set(bio, "trauma_vector", t_vec)
                safe_set(physics, "T", safe_get(physics, "T", 0.0) + scar.value)
                if msg := ux_format("soul_strings", "scar_frailty", name=scar.name): log.append(msg)
            else:
                # Dynamically apply the scar to any other valid physics parameter
                safe_set(physics, scar.stat_affected, safe_get(physics, scar.stat_affected, 0.0) + scar.value)
                if msg := ux_format("soul_strings", "scar_generic", name=scar.name, stat=scar.stat_affected):
                    log.append(msg)
                else:
                    log.append(f"Legacy Scar applied: {scar.name} penalty added to {scar.stat_affected}.")

        return log