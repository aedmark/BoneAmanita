""" bone_genesis.py - "The Egg."
    Architect: SLASH
    Mandate: Separate Creation from Execution.
"""

from typing import Dict, Any, Set
from bone_config import BoneConfig
from bone_core import EventBus
from bone_akashic import TheAkashicRecord
from bone_architect import BoneArchitect
from bone_soul import NarrativeSelf, TheOroboros
from bone_village import (
    TownHall, DeathGen, TheCartographer, TheTinkerer, Limbo
)
from bone_inventory import GordonKnot
from bone_protocols import (
    TheBureau, ZenGarden, TheCriticsCircle,
    TherapyProtocol, KintsugiProtocol
)
from bone_symbiosis import SymbiosisManager
from bone_spores import LiteraryReproduction
from bone_drivers import DriverRegistry

class BoneGenesis:
    """
    The Factory.
    Responsible for incubating the Embryo and populating the Village.
    Returns a 'SystemAnatomy' dict to be injected into the Engine.
    """

    @staticmethod
    def ignite(config: Dict[str, Any], lexicon_ref: Any) -> Dict[str, Any]:
        print("...Igniting Genesis Sequence...")

        events = EventBus()
        akashic = TheAkashicRecord()
        akashic.setup_listeners(events)

        embryo = BoneArchitect.incubate(events, lexicon_ref)
        embryo = BoneArchitect.awaken(embryo)

        if embryo.bio.mito.state.atp_pool <= 0.0:
            genesis_val = getattr(BoneConfig.METABOLISM, "GENESIS_VOLTAGE", 100.0)
            events.log(f"⚡ COLD BOOT: Injecting Genesis Spark ({genesis_val} ATP).", "SYS")
            embryo.bio.mito.adjust_atp(genesis_val, reason="GENESIS")

        mode_settings = config.get("mode_settings", {})
        suppressed = set(mode_settings.get("village_suppression", []))

        village_bundle = BoneGenesis._summon_village(events, embryo, akashic, suppressed)

        soul = NarrativeSelf(
            engine_ref=None,
            events_ref=events,
            memory_ref=embryo.mind.mem,
            akashic_ref=akashic
        )
        if embryo.soul_legacy:
            soul.load_from_dict(embryo.soul_legacy)

        oroboros = TheOroboros()
        if hasattr(embryo.physics, "observer"):
            dummy_phys = {"narrative_drag": 0.0, "voltage": 10.0}
            logs = oroboros.apply_legacy(dummy_phys, {})
            if logs:
                events.log(f"⛓️ LEGACY SCARS: {', '.join(logs)}", "OROBOROS")
                if hasattr(embryo.physics, 'dynamics'):
                    embryo.physics.dynamics.base_drag += dummy_phys["narrative_drag"]

        drivers = DriverRegistry(events)
        symbiosis = SymbiosisManager(events)

        return {
            "events": events,
            "akashic": akashic,
            "embryo": embryo,
            "village": village_bundle,
            "soul": soul,
            "oroboros": oroboros,
            "drivers": drivers,
            "symbiosis": symbiosis
        }

    @staticmethod
    def _summon_village(events, embryo, akashic, suppressed: Set[str]) -> Dict[str, Any]:
        """ Instantiates all agents based on suppression list. """

        gordon = None
        if "GORDON" not in suppressed:
            gordon = GordonKnot(events=events)

        navigator = None
        if "CARTOGRAPHER" not in suppressed and "NAVIGATOR" not in suppressed:
            navigator = TheCartographer(embryo.shimmer)

        tinkerer = None
        if "TINKERER" not in suppressed:
            tinkerer = TheTinkerer(gordon, events, akashic)

        death_gen = None
        if "DEATH" not in suppressed:
            death_gen = DeathGen()
            DeathGen.load_protocols()

        bureau = None
        if "BUREAU" not in suppressed:
            bureau = TheBureau()

        town_hall = TownHall(gordon, events, embryo.shimmer, akashic, navigator)

        repro = LiteraryReproduction()
        LiteraryReproduction.load_genetics()

        zen = ZenGarden(events)
        critics = TheCriticsCircle(events)
        therapy = TherapyProtocol()
        limbo = Limbo()
        kintsugi = KintsugiProtocol()

        return {
            "gordon": gordon,
            "navigator": navigator,
            "tinkerer": tinkerer,
            "death_gen": death_gen,
            "bureau": bureau,
            "town_hall": town_hall,
            "repro": repro,
            "zen": zen,
            "critics": critics,
            "therapy": therapy,
            "limbo": limbo,
            "kintsugi": kintsugi
        }