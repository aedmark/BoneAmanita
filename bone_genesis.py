"""bone_genesis.py"""

from typing import Dict, Any, Set

from bone_akashic import TheAkashicRecord
from bone_presets import BoneConfig
from bone_core import EventBus, LoreManifest, ux, safe_get, safe_set
from bone_drivers import DriverRegistry, BoneConsultant
from bone_inventory import GordonKnot
from bone_machine import BoneArchitect
from bone_protocols import (
    TheBureau,
    ZenGarden,
    TheCriticsCircle,
    TherapyProtocol,
    KintsugiProtocol,
    LimboLayer,
)
from bone_soul import NarrativeSelf, TheOroboros
from bone_spores import LiteraryReproduction
from bone_symbiosis import SymbiosisManager
from bone_village import (
    TownHall,
    DeathGen,
    TheCartographer,
    TheTinkerer,
    TheTherapist,
    TheGraveDigger,
)


class BoneGenesis:

    @staticmethod
    def ignite(
        config: Dict[str, Any], lexicon_ref: Any, events_ref: Any = None
    ) -> Dict[str, Any]:
        events = events_ref or EventBus()
        if events_ref:
            events.log(ux("genesis_strings", "ignite_log"), "GENESIS")
        else:
            print(ux("genesis_strings", "ignite_print"))
        target_cfg = config.get("bone_config") or BoneConfig
        akashic = TheAkashicRecord(
            lore_manifest=LoreManifest.get_instance(config_ref=target_cfg),
            events_ref=events,
        )
        akashic.setup_listeners(events)
        embryo = BoneArchitect.awaken(
            BoneArchitect.incubate(events, lexicon_ref, config_ref=target_cfg)
        )
        village_bundle = BoneGenesis._summon_village(
            events,
            embryo,
            akashic,
            set(config.get("mode_settings", {}).get("village_suppression", [])),
            config.get("boot_mode", "ADVENTURE"),
            target_cfg,
            lexicon_ref,
        )
        soul = NarrativeSelf(
            engine_ref=None,
            events_ref=events,
            memory_ref=embryo.mind.mem,
            akashic_ref=akashic,
            config_ref=target_cfg,
        )
        if embryo.soul_legacy:
            soul.load_from_dict(embryo.soul_legacy)
        oroboros = TheOroboros(config_ref=target_cfg)
        if hasattr(embryo.physics, "observer"):
            cfg_gen = getattr(target_cfg, "GENESIS", None)
            dv, dd = getattr(cfg_gen, "DUMMY_VOLTAGE", 10.0) if cfg_gen else 10.0, (
                getattr(cfg_gen, "DUMMY_DRAG", 0.0) if cfg_gen else 0.0
            )
            dummy_phys = {"narrative_drag": dd, "voltage": dv}
            safe_bio_proxy = {
                "trauma_vector": getattr(
                    getattr(embryo.mind, "mem", None), "session_trauma_vector", {}
                )
                or {}
            }
            if logs := oroboros.apply_legacy(dummy_phys, safe_bio_proxy):
                events.log(
                    (
                        ux("genesis_strings", "legacy_scars")
                        or "Legacy scars applied: {logs}"
                    ).format(logs=", ".join(logs)),
                    "OROBOROS",
                )
                if (applied_drag := dummy_phys.get("narrative_drag", dd) - dd) != 0:
                    safe_set(
                        embryo.physics,
                        "narrative_drag",
                        float(safe_get(embryo.physics, "narrative_drag", 0.0) or 0.0)
                        + applied_drag,
                    )
                if (volt_penalty := dv - dummy_phys.get("voltage", dv)) > 0:
                    safe_set(
                        embryo.physics,
                        "voltage",
                        max(
                            0.0,
                            float(safe_get(embryo.physics, "voltage", 0.0) or 0.0)
                            - volt_penalty,
                        ),
                    )
                if hasattr(embryo.mind, "mem"):
                    embryo.mind.mem.session_trauma_vector = safe_bio_proxy.get(
                        "trauma_vector", {}
                    )
        drivers = DriverRegistry(events, config_ref=target_cfg)
        symbiosis = SymbiosisManager(events, config_ref=target_cfg)
        return {
            "events": events,
            "akashic": akashic,
            "embryo": embryo,
            "village": village_bundle,
            "soul": soul,
            "oroboros": oroboros,
            "drivers": drivers,
            "consultant": village_bundle["consultant"],
            "symbiosis": symbiosis,
        }

    @staticmethod
    def _summon_village(
        events,
        embryo,
        akashic,
        suppressed: Set[str],
        boot_mode: str = "ADVENTURE",
        config_ref=None,
        lexicon_ref=None,
    ) -> Dict[str, Any]:
        c = config_ref
        gordon = (
            GordonKnot(events=events, mode=boot_mode, config_ref=c)
            if "GORDON" not in suppressed
            else None
        )
        navigator = (
            TheCartographer(embryo.shimmer, config_ref=c)
            if {"CARTOGRAPHER", "NAVIGATOR"}.isdisjoint(suppressed)
            else None
        )
        if death_gen := DeathGen() if "DEATH" not in suppressed else None:
            DeathGen.load_protocols()
        LiteraryReproduction.load_genetics(config_ref=c)
        return {
            "gordon": gordon,
            "navigator": navigator,
            "tinkerer": (
                TheTinkerer(gordon, events, akashic, config_ref=c)
                if "TINKERER" not in suppressed
                else None
            ),
            "death_gen": death_gen,
            "bureau": TheBureau(config_ref=c) if "BUREAU" not in suppressed else None,
            "town_hall": TownHall(
                gordon, events, embryo.shimmer, akashic, navigator, config_ref=c
            ),
            "repro": LiteraryReproduction(config_ref=c),
            "zen": ZenGarden(events, config_ref=c),
            "critics": TheCriticsCircle(events, config_ref=c),
            "therapy": TherapyProtocol(config_ref=c),
            "limbo": LimboLayer(config_ref=c),
            "kintsugi": KintsugiProtocol(config_ref=c),
            "consultant": BoneConsultant(config_ref=c, lexicon_ref=lexicon_ref),
            "therapist": (
                TheTherapist(events, config_ref=c)
                if "THERAPIST" not in suppressed
                else None
            ),
            "gravedigger": (
                TheGraveDigger(gordon, events, config_ref=c)
                if "GRAVEDIGGER" not in suppressed
                else None
            ),
        }
