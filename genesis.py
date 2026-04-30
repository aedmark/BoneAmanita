"""genesis.py"""

from typing import Dict, Any, Set
from brain.akashic import TheAkashicRecord
from presets import BoneConfig
from core import EventBus, LoreManifest
from struts import ux
from drivers import DriverRegistry, BoneConsultant
from mechanics.inventory import GordonKnot
from machine import BoneArchitect
from protocols import TheBureau, ZenGarden, TheCriticsCircle, TherapyProtocol, KintsugiProtocol, LimboLayer
from brain.soul import NarrativeSelf, TheOroboros
from spores import LiteraryReproduction
from archetypes.symbiosis import SymbiosisManager
from constants import Prisma
from archetypes.village import TownHall, DeathGen, TheCartographer, TheTinkerer, TheTherapist, TheGraveDigger

class BoneGenesis:

    @staticmethod
    def ignite(config: Dict[str, Any], lexicon_ref: Any, events_ref: Any = None) -> Dict[str, Any]:
        events = events_ref or EventBus()
        log_msg = ux("genesis_strings", "ignite_log") or "Igniting lattice..."
        events.log(f"{Prisma.CYN}{log_msg}{Prisma.RST}", "GENESIS")
        target_cfg = config.get("config") or BoneConfig
        akashic = TheAkashicRecord(lore_manifest=LoreManifest.get_instance(config_ref=target_cfg), events_ref=events)
        akashic.setup_listeners(events)
        seed = BoneArchitect.incubate(events, lexicon_ref, config_ref=target_cfg)
        embryo = BoneArchitect.awaken(seed)
        mode_settings = config.get("mode_settings") or {}
        suppressed_set = set(mode_settings.get("village_suppression") or [])
        village_bundle = BoneGenesis._summon_village(events, embryo, akashic, suppressed_set, config.get("boot_mode", "ADVENTURE"), target_cfg, lexicon_ref, )
        soul = NarrativeSelf(engine_ref=None, events_ref=events, memory_ref=embryo.mind.mem, akashic_ref=akashic, config_ref=target_cfg)
        if embryo.soul_legacy:
            soul.load_from_dict(embryo.soul_legacy)
        oroboros = TheOroboros(config_ref=target_cfg)
        if embryo.physics:
            cfg_gen = getattr(target_cfg, "GENESIS", None)
            base_voltage = getattr(cfg_gen, "DUMMY_VOLTAGE", 10.0)
            base_drag = getattr(cfg_gen, "DUMMY_DRAG", 0.0)

            dummy_phys = {"narrative_drag": base_drag, "voltage": base_voltage}
            mem = getattr(embryo.mind, "mem", None)
            bio_proxy = {"trauma_vector": getattr(mem, "session_trauma_vector", {}) if mem else {}}

            if logs := oroboros.apply_legacy(dummy_phys, bio_proxy):
                msg = ux("genesis_strings", "legacy_scars") or "The lattice remembers. Inherited scars: {logs}"
                events.log(f"{Prisma.MAG}{msg.format(logs=', '.join(logs))}{Prisma.RST}", "OROBOROS")

                # Direct, native application of inherited physics.
                if applied_drag := dummy_phys.get("narrative_drag", base_drag) - base_drag:
                    embryo.physics.narrative_drag += float(applied_drag)

                if (volt_penalty := base_voltage - dummy_phys.get("voltage", base_voltage)) > 0:
                    embryo.physics.voltage = max(0.0, float(embryo.physics.voltage) - float(volt_penalty))

            if mem:
                mem.session_trauma_vector = bio_proxy.get("trauma_vector", {})
        drivers = DriverRegistry(events, config_ref=target_cfg)
        symbiosis = SymbiosisManager(events, config_ref=target_cfg)
        return {"events": events, "akashic": akashic, "embryo": embryo, "village": village_bundle, "soul": soul,
                "oroboros": oroboros, "drivers": drivers, "consultant": village_bundle.get("consultant"),
                "symbiosis": symbiosis, }

    @staticmethod
    def _summon_village(events, embryo, akashic, suppressed: Set[str], boot_mode: str = "ADVENTURE", config_ref=None, lexicon_ref=None) -> Dict[str, Any]:
        c = config_ref
        spawn = lambda key, cls, *args, **kwargs: cls(*args, **kwargs) if key not in suppressed else None
        gordon = spawn("GORDON", GordonKnot, events=events, mode=boot_mode, config_ref=c)
        navigator = TheCartographer(embryo.shimmer, config_ref=c) if not {"CARTOGRAPHER", "NAVIGATOR"} & suppressed else None
        if "DEATH" not in suppressed: DeathGen.load_protocols()
        if "REPRO" not in suppressed: LiteraryReproduction.load_genetics(config_ref=c)
        return {"gordon": gordon,
            "navigator": navigator,
            "tinkerer": spawn("TINKERER", TheTinkerer, gordon, events, akashic, config_ref=c),
            "death_gen": spawn("DEATH", DeathGen),
            "bureau": spawn("BUREAU", TheBureau, config_ref=c),
            "town_hall": spawn("TOWN_HALL", TownHall, gordon, events, embryo.shimmer, akashic, navigator, config_ref=c),
            "repro": spawn("REPRO", LiteraryReproduction, config_ref=c),
            "zen": spawn("ZEN", ZenGarden, events, config_ref=c),
            "critics": spawn("CRITICS", TheCriticsCircle, events, config_ref=c),
            "therapy": spawn("THERAPY", TherapyProtocol, config_ref=c),
            "limbo": spawn("LIMBO", LimboLayer, config_ref=c),
            "kintsugi": spawn("KINTSUGI", KintsugiProtocol, config_ref=c),
            "consultant": spawn("CONSULTANT", BoneConsultant, config_ref=c, lexicon_ref=lexicon_ref),
            "therapist": spawn("THERAPIST", TheTherapist, events, config_ref=c),
            "gravedigger": spawn("GRAVEDIGGER", TheGraveDigger, gordon, events, config_ref=c),}
