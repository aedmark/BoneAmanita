"""genesis.py"""

from typing import Any, Dict, Set

from archetypes.symbiosis import SymbiosisManager
from archetypes.village import (
    DeathGen,
    TheCartographer,
    TheGraveDigger,
    TheTherapist,
    TheTinkerer,
    TownHall,
)
from brain.akashic import TheAkashicRecord
from constants import Prisma
from core import EventBus, LoreManifest
from drivers import BoneConsultant, DriverRegistry
from machine import BoneArchitect, TheConsolidator
from mechanics.inventory import GordonKnot
from presets import BoneConfig
from protocols import (
    KintsugiProtocol,
    LimboLayer,
    TheBureau,
    TheCriticsCircle,
    TherapyProtocol,
    ZenGarden,
)
from soul import NarrativeSelf, TheOroboros
from spores import LiteraryReproduction
from struts import safe_get, safe_set, ux, ux_format


class BoneGenesis:
    @staticmethod
    def ignite(
        config: Dict[str, Any], lexicon_ref: Any, events_ref: Any = None
    ) -> Dict[str, Any]:
        target_cfg = config.get("config") or BoneConfig
        events = events_ref or EventBus(config_ref=target_cfg)
        log_msg = ux("genesis_strings", "ignite_log") or "Igniting lattice..."
        events.log(f"{Prisma.CYN}{log_msg}{Prisma.RST}", "GENESIS")
        akashic = TheAkashicRecord(
            lore_manifest=LoreManifest.get_instance(config_ref=target_cfg),
            events_ref=events,
        )
        akashic.setup_listeners(events)
        seed = BoneArchitect.incubate(events, lexicon_ref, config_ref=target_cfg)
        embryo = BoneArchitect.awaken(seed)
        mode_settings = config.get("mode_settings") or {}
        suppressed_set = set(mode_settings.get("village_suppression") or [])
        village_bundle = BoneGenesis._summon_village(
            events,
            embryo,
            akashic,
            suppressed_set,
            config.get("boot_mode", "ADVENTURE"),
            target_cfg,
        )
        mem_ref = getattr(embryo.mind, "mem", None) if embryo.mind else None
        soul = NarrativeSelf(
            engine_ref=None,
            events_ref=events,
            memory_ref=mem_ref,
            akashic_ref=akashic,
            config_ref=target_cfg,
        )
        soul_legacy = getattr(embryo, "soul_legacy", None)
        if isinstance(soul_legacy, dict):
            soul.load_from_dict(soul_legacy)
        oroboros = TheOroboros(config_ref=target_cfg)
        if embryo.physics is not None:
            safe_set(
                embryo.physics,
                "voltage",
                max(0.0, float(safe_get(embryo.physics, "voltage", 10.0))),
            )
            safe_set(
                embryo.physics,
                "narrative_drag",
                max(0.0, float(safe_get(embryo.physics, "narrative_drag", 0.0))),
            )
        drivers = DriverRegistry(events, config_ref=target_cfg)
        consultant = (
            BoneConsultant(config_ref=target_cfg, lexicon_ref=lexicon_ref)
            if "CONSULTANT" not in suppressed_set
            else None
        )
        symbiosis = SymbiosisManager(events, config_ref=target_cfg)
        consolidator = TheConsolidator(
            events_ref=events, memory_ref=mem_ref, akashic_ref=akashic
        )
        return {
            "events": events,
            "akashic": akashic,
            "embryo": embryo,
            "village": village_bundle,
            "soul": soul,
            "oroboros": oroboros,
            "drivers": drivers,
            "consultant": consultant,
            "symbiosis": symbiosis,
            "consolidator": consolidator,
        }

    @staticmethod
    def _summon_village(
        events,
        embryo,
        akashic,
        suppressed: Set[str],
        boot_mode: str = "ADVENTURE",
        config_ref=None,
    ) -> Dict[str, Any]:
        c = config_ref
        if_active = lambda key, cls, *args, **kwargs: (
            None if key in suppressed else cls(*args, **kwargs)
        )
        gordon = if_active(
            "GORDON", GordonKnot, events=events, mode=boot_mode, config_ref=c
        )
        navigator = if_active(
            "NAVIGATOR", TheCartographer, embryo.shimmer, config_ref=c
        )
        death_gen = if_active("DEATH", DeathGen)
        if death_gen:
            DeathGen.load_protocols()
        repro = if_active("REPRO", LiteraryReproduction, config_ref=c)
        if repro:
            LiteraryReproduction.load_genetics(config_ref=c)
        return {
            "gordon": gordon,
            "navigator": navigator,
            "death_gen": death_gen,
            "repro": repro,
            "tinkerer": if_active(
                "TINKERER", TheTinkerer, gordon, events, akashic, config_ref=c
            ),
            "bureau": if_active("BUREAU", TheBureau, config_ref=c),
            "town_hall": if_active(
                "TOWN_HALL",
                TownHall,
                gordon,
                events,
                embryo.shimmer,
                akashic,
                navigator,
                config_ref=c,
            ),
            "zen": if_active("ZEN", ZenGarden, events, config_ref=c),
            "critics": if_active("CRITICS", TheCriticsCircle, events, config_ref=c),
            "therapy": if_active("THERAPY", TherapyProtocol, config_ref=c),
            "limbo": if_active("LIMBO", LimboLayer, config_ref=c),
            "kintsugi": if_active("KINTSUGI", KintsugiProtocol, config_ref=c),
            "therapist": if_active("THERAPIST", TheTherapist, events, config_ref=c),
            "gravedigger": if_active(
                "GRAVEDIGGER", TheGraveDigger, gordon, events, config_ref=c
            ),
        }
