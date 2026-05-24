"""genesis.py"""

from typing import Dict, Any, Set
from brain.akashic import TheAkashicRecord
from presets import BoneConfig
from core import EventBus, LoreManifest
from struts import ux, ux_format, safe_get, safe_set
from drivers import DriverRegistry, BoneConsultant
from mechanics.inventory import GordonKnot
from machine import BoneArchitect, TheConsolidator
from protocols import TheBureau, ZenGarden, TheCriticsCircle, TherapyProtocol, KintsugiProtocol, LimboLayer
from soul import NarrativeSelf, TheOroboros
from spores import LiteraryReproduction
from archetypes.symbiosis import SymbiosisManager
from constants import Prisma
from archetypes.village import TownHall, DeathGen, TheCartographer, TheTinkerer, TheTherapist, TheGraveDigger

class BoneGenesis:
    @staticmethod
    def ignite(config: Dict[str, Any], lexicon_ref: Any, events_ref: Any = None) -> Dict[str, Any]:
        target_cfg = config.get("config") or BoneConfig
        events = events_ref or EventBus(config_ref=target_cfg)
        log_msg = ux("genesis_strings", "ignite_log") or "Igniting lattice..."
        events.log(f"{Prisma.CYN}{log_msg}{Prisma.RST}", "GENESIS")
        akashic = TheAkashicRecord(lore_manifest=LoreManifest.get_instance(config_ref=target_cfg), events_ref=events)
        akashic.setup_listeners(events)
        seed = BoneArchitect.incubate(events, lexicon_ref, config_ref=target_cfg)
        embryo = BoneArchitect.awaken(seed)
        mode_settings = config.get("mode_settings") or {}
        suppressed_set = set(mode_settings.get("village_suppression") or [])
        village_bundle = BoneGenesis._summon_village(events, embryo, akashic, suppressed_set, config.get("boot_mode", "ADVENTURE"), target_cfg)
        soul = NarrativeSelf(engine_ref=None, events_ref=events, memory_ref=embryo.mind.mem, akashic_ref=akashic, config_ref=target_cfg)
        if embryo.soul_legacy:
            soul.load_from_dict(embryo.soul_legacy)
        oroboros = TheOroboros(config_ref=target_cfg)
        cfg_gen = safe_get(target_cfg, "GENESIS", {})
        bio_proxy = {"trauma_vector": safe_get(embryo.mind.mem, "session_trauma_vector", {})}
        if logs := oroboros.apply_legacy(embryo.physics, bio_proxy):
            msg = ux_format("genesis_strings", "legacy_scars", default="The lattice remembers. Inherited scars: {logs}",
                            logs=', '.join(logs))
            events.log(f"{Prisma.MAG}{msg}{Prisma.RST}", "OROBOROS")
        for key, default in [("voltage", 10.0), ("narrative_drag", 0.0)]:
            base_val = float(safe_get(cfg_gen, f"DUMMY_{key.upper()}", default))
            safe_set(embryo.physics, key, max(0.0, float(safe_get(embryo.physics, key, base_val))))
        drivers = DriverRegistry(events, config_ref=target_cfg)
        consultant = BoneConsultant(config_ref=target_cfg, lexicon_ref=lexicon_ref) if "CONSULTANT" not in suppressed_set else None
        symbiosis = SymbiosisManager(events, config_ref=target_cfg)
        consolidator = TheConsolidator(events_ref=events, memory_ref=embryo.mind.mem, akashic_ref=akashic)
        return {"events": events, "akashic": akashic, "embryo": embryo, "village": village_bundle, "soul": soul,
                "oroboros": oroboros, "drivers": drivers, "consultant": consultant, "symbiosis": symbiosis,
                "consolidator": consolidator}

    @staticmethod
    def _summon_village(events, embryo, akashic, suppressed: Set[str], boot_mode: str = "ADVENTURE", config_ref=None) -> \
    Dict[str, Any]:
        c = config_ref

        def spawn(key, cls, *args, **kwargs):
            if key in suppressed:
                return None
            return cls(*args, **kwargs)

        gordon = spawn("GORDON", GordonKnot, events=events, mode=boot_mode, config_ref=c)
        navigator = spawn("NAVIGATOR", TheCartographer, embryo.shimmer, config_ref=c)
        if death_gen := spawn("DEATH", DeathGen):
            death_gen.__class__.load_protocols()
        if repro := spawn("REPRO", LiteraryReproduction, config_ref=c):
            repro.__class__.load_genetics(config_ref=c)
        return {
            "gordon": gordon,
            "navigator": navigator,
            "tinkerer": spawn("TINKERER", TheTinkerer, gordon, events, akashic, config_ref=c),
            "death_gen": death_gen,
            "bureau": spawn("BUREAU", TheBureau, config_ref=c),
            "town_hall": spawn("TOWN_HALL", TownHall, gordon, events, embryo.shimmer, akashic, navigator, config_ref=c),
            "repro": repro,
            "zen": spawn("ZEN", ZenGarden, events, config_ref=c),
            "critics": spawn("CRITICS", TheCriticsCircle, events, config_ref=c),
            "therapy": spawn("THERAPY", TherapyProtocol, config_ref=c),
            "limbo": spawn("LIMBO", LimboLayer, config_ref=c),
            "kintsugi": spawn("KINTSUGI", KintsugiProtocol, config_ref=c),
            "therapist": spawn("THERAPIST", TheTherapist, events, config_ref=c),
            "gravedigger": spawn("GRAVEDIGGER", TheGraveDigger, gordon, events, config_ref=c),
        }
