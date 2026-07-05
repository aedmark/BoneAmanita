"""/soul/oroboros.py"""

import json
import os
import random
import tempfile
from dataclasses import dataclass
from typing import Any, List

from constants import Prisma
from core import LoreManifest
from presets import BoneConfig
from soul import NarrativeSelf
from struts import safe_get, safe_set, ux, ux_format


@dataclass
class Scar:
    name: str
    stat_affected: str
    value: float
    description: str


@dataclass
class Myth:
    title: str
    lesson: str
    trigger: str


class TheOroboros:
    LEGACY_FILE = "legacy.json"

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.scars: List[Scar] = []
        self.myths: List[Myth] = []
        self.generation_count = 0
        self._load()

    def _cfg(self, key: str, default: Any) -> Any:
        val = safe_get(safe_get(self.cfg, "OROBOROS", {}), key, default)
        return (
            float(val)
            if isinstance(default, float)
            else int(val)
            if isinstance(default, int)
            else val
        )

    def _load(self):
        if not os.path.exists(self.LEGACY_FILE):
            return
        try:
            with open(self.LEGACY_FILE) as f:
                data = json.load(f)
                self.generation_count = data.get("generation", 0)
                self.scars = [Scar(**s) for s in data.get("scars", [])]
                self.myths = [Myth(**m) for m in data.get("myths", [])]
            if msg := ux_format(
                "soul_strings", "oroboros_gen_loaded", gen=self.generation_count
            ):
                print(f"{Prisma.VIOLET}{msg}{Prisma.RST}")
        except Exception as e:
            print(
                f"{Prisma.RED}[OROBOROS]: Legacy state corrupted or missing. Starting fresh. ({e}){Prisma.RST}"
            )

    def crystallize(self, cause_of_death: str, soul: NarrativeSelf):
        death_data = LoreManifest.get_instance().get("DEATH") or {}
        new_scars, new_myths = [], []
        eng = getattr(soul, "eng", None)
        if eng and getattr(eng, "trauma_accum", None):
            total_trauma = float(sum(eng.trauma_accum.values()))
            if 5.0 < total_trauma <= 10.0:
                new_scars.append(
                    Scar(
                        name="Latent Grey Area Tension",
                        stat_affected="voltage_cap",
                        value=total_trauma * 0.05,
                        description="Subconscious processing registered a tilt without crossing the waking threshold.",
                    )
                )
            if total_trauma > 10.0:
                scar_val = min(20.0, total_trauma * 0.1)
                new_scars.append(
                    Scar(
                        name="Existential Dread",
                        stat_affected="trauma_baseline",
                        value=scar_val,
                        description=f"The lattice remembers a heavy collapse (Trauma: {round(total_trauma, 1)}).",
                    )
                )
        entry = death_data.get(cause_of_death)
        if isinstance(entry, (list, tuple)):
            verdict_map = {
                "TOXICITY": "TOXIC",
                "BOREDOM": "BORING",
                "STARVATION": "LIGHT",
                "APOPTOSIS": "TOXIC",
            }
            v_key = verdict_map.get(cause_of_death, "HEAVY")
            v_list = death_data.get("VERDICTS", {}).get(v_key)
            entry_padded = list(entry) + [None] * (4 - len(entry))
            scar_name = entry_padded[0] or "Unknown Scar"
            stat_affected = entry_padded[1] or "voltage"
            val = float(entry_padded[2] if entry_padded[2] is not None else 5.0)
            fallback_desc = (
                entry_padded[3] or "The system collapsed under unknown pressure."
            )
            desc = (
                random.choice(v_list)
                if isinstance(v_list, list) and v_list
                else fallback_desc
            )
            new_scars.append(Scar(scar_name, stat_affected, val, desc))
        if soul.core_memories:
            strongest = max(soul.core_memories, key=lambda m: m.impact_voltage)
            trigger_word = (
                strongest.trigger_words[0]
                if strongest.trigger_words
                else (ux("soul_strings", "oroboros_def_trigger") or "Silence")
            )
            new_myths.append(
                Myth(
                    title=(
                        ux("soul_strings", "oroboros_myth_title")
                        or "The Myth of {trigger}"
                    ).format(trigger=trigger_word.title()),
                    lesson=strongest.lesson,
                    trigger=trigger_word,
                )
            )
        self.scars.extend(new_scars)
        self.scars = self.scars[-self._cfg("MAX_SCARS", 5) :]
        self.myths.extend(new_myths)
        self.myths = self.myths[-self._cfg("MAX_MYTHS", 10) :]
        payload = {
            "generation": self.generation_count + 1,
            "scars": [vars(s) for s in self.scars],
            "myths": [vars(m) for m in self.myths],
        }
        try:
            fd, temp_path = tempfile.mkstemp(
                dir=os.path.dirname(os.path.abspath(self.LEGACY_FILE)) or ".", text=True
            )
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self.LEGACY_FILE)
        except Exception as e:
            print(
                f"{Prisma.RED}[OROBOROS]: Failed to write legacy payload: {e}{Prisma.RST}"
            )
        return ux_format(
            "soul_strings",
            "generation_encoded",
            gen=self.generation_count + 1,
            scars=len(new_scars),
            myths=len(new_myths),
        )

    def apply_legacy(self, physics: Any, bio: Any):
        log = []
        if not physics:
            return log
        for scar in self.scars:
            if scar.stat_affected == "voltage_cap":
                safe_set(
                    physics,
                    "voltage",
                    max(
                        0.0,
                        safe_get(physics, "voltage", 0.0)
                        - self._cfg("VOLTAGE_PENALTY", 5.0),
                    ),
                )
                if msg := ux_format("soul_strings", "scar_voltage", name=scar.name):
                    log.append(msg)
            elif scar.stat_affected == "trauma_baseline":
                t_vec = safe_get(bio, "trauma_vector") or {}
                safe_set(
                    t_vec,
                    "EXISTENTIAL",
                    safe_get(t_vec, "EXISTENTIAL", 0.0) + scar.value,
                )
                safe_set(bio, "trauma_vector", t_vec)
                safe_set(physics, "T", safe_get(physics, "T", 0.0) + scar.value)
                if msg := ux_format("soul_strings", "scar_frailty", name=scar.name):
                    log.append(msg)
            else:
                safe_set(
                    physics,
                    scar.stat_affected,
                    safe_get(physics, scar.stat_affected, 0.0) + scar.value,
                )
                if msg := ux_format(
                    "soul_strings",
                    "scar_generic",
                    name=scar.name,
                    stat=scar.stat_affected,
                ):
                    log.append(msg)
                else:
                    log.append(
                        f"Legacy Scar applied: {scar.name} penalty added to {scar.stat_affected}."
                    )
        return log
