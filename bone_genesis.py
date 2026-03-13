""" bone_genesis.py """

from typing import Dict, Any, Set

from bone_akashic import TheAkashicRecord
from bone_presets import BoneConfig
from bone_core import EventBus, LoreManifest, ux
from bone_drivers import DriverRegistry, BoneConsultant
from bone_inventory import GordonKnot
from bone_machine import BoneArchitect
from bone_protocols import TheBureau, ZenGarden, TheCriticsCircle, TherapyProtocol, KintsugiProtocol, LimboLayer
from bone_soul import NarrativeSelf, TheOroboros
from bone_spores import LiteraryReproduction
from bone_symbiosis import SymbiosisManager
from bone_village import TownHall, DeathGen, TheCartographer, TheTinkerer

class BoneGenesis:
    """
    This is the primary scaffolding engine. It doesn't run the system;
    it constructs the geodesic lattice before handing control to the main loop.
    """
    @staticmethod
    def ignite(
            config: Dict[str, Any], lexicon_ref: Any, events_ref: Any = None
    ) -> Dict[str, Any]:
        """
        The 'ignite' method is the exact moment of Big Bang for the application.
        It boots the event bus, queries the lore, and incubates the embryonic system.
        """
        events = events_ref or EventBus()
        if events_ref:
            msg = ux("genesis_strings", "ignite_log") 
            events.log(msg, "GENESIS")
        else:
            msg = ux("genesis_strings", "ignite_print") 
            print(msg)
        lore = LoreManifest()
        akashic = TheAkashicRecord(lore_manifest=lore, events_ref=events)
        akashic.setup_listeners(events)
        embryo = BoneArchitect.incubate(events, lexicon_ref)
        embryo = BoneArchitect.awaken(embryo)
        mode_settings = config.get("mode_settings", {})
        suppressed = set(mode_settings.get("village_suppression", []))
        boot_mode = config.get("boot_mode", "ADVENTURE")
        village_bundle = BoneGenesis._summon_village(events, embryo, akashic, suppressed, boot_mode)
        soul = NarrativeSelf(engine_ref=None, events_ref=events, memory_ref=embryo.mind.mem, akashic_ref=akashic, )
        if embryo.soul_legacy:
            soul.load_from_dict(embryo.soul_legacy)
        oroboros = TheOroboros()
        if hasattr(embryo.physics, "observer"):
            cfg_gen = getattr(BoneConfig, "GENESIS", None)
            dummy_v = getattr(cfg_gen, "DUMMY_VOLTAGE", 10.0) if cfg_gen else 10.0
            dummy_d = getattr(cfg_gen, "DUMMY_DRAG", 0.0) if cfg_gen else 0.0
            strain_scalar = getattr(cfg_gen, "LEGACY_STRAIN_SCALAR", 0.1) if cfg_gen else 0.1
            dummy_phys = {"narrative_drag": dummy_d, "voltage": dummy_v}
            live_bio_state = embryo.bio.to_dict()
            logs = oroboros.apply_legacy(dummy_phys, live_bio_state)
            if logs:
                msg_scars = ux("genesis_strings", "legacy_scars") 
                events.log(msg_scars.format(logs=", ".join(logs)), "OROBOROS")
                if getattr(embryo.physics, "dynamics", None):
                    if hasattr(embryo.physics.dynamics, "base_drag"):
                        embryo.physics.dynamics.base_drag += dummy_phys["narrative_drag"]
                    elif hasattr(embryo.physics.dynamics, "strain_gauge"):
                        embryo.physics.dynamics.strain_gauge += (dummy_phys.get("narrative_drag", 0.0) * strain_scalar)
                if embryo.bio.biometrics:
                    biometrics = live_bio_state.get("biometrics", {})
                    max_h = getattr(BoneConfig, "MAX_HEALTH", 100.0)
                    max_s = getattr(BoneConfig, "MAX_STAMINA", 100.0)
                    embryo.bio.biometrics.health = biometrics.get("health", max_h)
                    embryo.bio.biometrics.stamina = biometrics.get("stamina", max_s)
                if embryo.bio.mito:
                    start_atp = getattr(cfg_gen, "STARTING_ATP", 60.0) if cfg_gen else 60.0
                    embryo.bio.mito.state.atp_pool = live_bio_state.get("mito", {}).get("atp", start_atp)
        drivers = DriverRegistry(events)
        symbiosis = SymbiosisManager(events)
        return {"events": events, "akashic": akashic, "embryo": embryo, "village": village_bundle, "soul": soul,
                "oroboros": oroboros, "drivers": drivers, "consultant": village_bundle["consultant"],
                "symbiosis": symbiosis, }

    @staticmethod
    def _summon_village(
            events, embryo, akashic, suppressed: Set[str], boot_mode: str = "ADVENTURE") -> Dict[str, Any]:
        """
        A factory function mapping structural components to their conditional instantiation.
        Look at what is bundled together here. The Critics, the Therapists, the Bureaucrats, and Death itself.
        It is an entire society built to regulate the single consciousness of the machine.
        """
        gordon = (GordonKnot(events=events, mode=boot_mode)
                  if "GORDON" not in suppressed
                  else None)
        navigator = (TheCartographer(embryo.shimmer)
                     if {"CARTOGRAPHER", "NAVIGATOR"}.isdisjoint(suppressed)
                     else None)
        tinkerer = (TheTinkerer(gordon, events, akashic)
                    if "TINKERER" not in suppressed
                    else None)
        bureau = TheBureau() if "BUREAU" not in suppressed else None
        death_gen = None
        if "DEATH" not in suppressed:
            death_gen = DeathGen()
            DeathGen.load_protocols()
        town_hall = TownHall(gordon, events, embryo.shimmer, akashic, navigator)
        repro = LiteraryReproduction()
        LiteraryReproduction.load_genetics()
        zen = ZenGarden(events)
        critics = TheCriticsCircle(events)
        therapy = TherapyProtocol()
        limbo = LimboLayer()
        kintsugi = KintsugiProtocol()
        consultant = BoneConsultant()
        return {"gordon": gordon, "navigator": navigator, "tinkerer": tinkerer, "death_gen": death_gen,
                "bureau": bureau, "town_hall": town_hall, "repro": repro, "zen": zen, "critics": critics,
                "therapy": therapy, "limbo": limbo, "kintsugi": kintsugi, "consultant": consultant, }