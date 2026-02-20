from typing import Dict, Any, Set
from bone_core import EventBus, LoreManifest
from bone_akashic import TheAkashicRecord
from bone_architect import BoneArchitect
from bone_soul import NarrativeSelf, TheOroboros
from bone_village import TownHall, DeathGen, TheCartographer, TheTinkerer
from bone_inventory import GordonKnot
from bone_protocols import TheBureau, ZenGarden, TheCriticsCircle, TherapyProtocol, KintsugiProtocol, LimboLayer
from bone_symbiosis import SymbiosisManager
from bone_spores import LiteraryReproduction
from bone_drivers import DriverRegistry


class BoneGenesis:
    @staticmethod
    def ignite(
        config: Dict[str, Any], lexicon_ref: Any, events_ref: Any = None
    ) -> Dict[str, Any]:
        events = events_ref or EventBus()
        if events_ref:
            events.log("Igniting Genesis Sequence...", "GENESIS")
        else:
            print("...Igniting Genesis Sequence...")
        lore = LoreManifest()
        akashic = TheAkashicRecord(lore_manifest=lore, events_ref=events)
        akashic.setup_listeners(events)
        embryo = BoneArchitect.incubate(events, lexicon_ref)
        embryo = BoneArchitect.awaken(embryo)
        mode_settings = config.get("mode_settings", {})
        suppressed = set(mode_settings.get("village_suppression", []))
        village_bundle = BoneGenesis._summon_village(
            events, embryo, akashic, suppressed
        )
        soul = NarrativeSelf(
            engine_ref=None,
            events_ref=events,
            memory_ref=embryo.mind.mem,
            akashic_ref=akashic,
        )
        if embryo.soul_legacy:
            soul.load_from_dict(embryo.soul_legacy)
        oroboros = TheOroboros()
        if hasattr(embryo.physics, "observer"):
            dummy_phys = {"narrative_drag": 0.0, "voltage": 10.0}
            live_bio_state = embryo.bio.to_dict()
            logs = oroboros.apply_legacy(dummy_phys, live_bio_state)
            if logs:
                events.log(f"⛓️ LEGACY SCARS: {', '.join(logs)}", "OROBOROS")
                if hasattr(embryo.physics, "dynamics"):
                    embryo.physics.dynamics.base_drag += dummy_phys["narrative_drag"]
                if embryo.bio.biometrics:
                    biometrics = live_bio_state.get("biometrics", {})
                    embryo.bio.biometrics.health = biometrics.get("health", 100.0)
                    embryo.bio.biometrics.stamina = biometrics.get("stamina", 100.0)
                if embryo.bio.mito:
                    embryo.bio.mito.state.atp_pool = live_bio_state.get("mito", {}).get("atp", 60.0)
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
            "symbiosis": symbiosis,
        }

    @staticmethod
    def _summon_village(
            events, embryo, akashic, suppressed: Set[str]
    ) -> Dict[str, Any]:
        gordon = GordonKnot(events=events) if "GORDON" not in suppressed else None
        navigator = TheCartographer(embryo.shimmer) if {"CARTOGRAPHER", "NAVIGATOR"}.isdisjoint(suppressed) else None
        tinkerer = TheTinkerer(gordon, events, akashic) if "TINKERER" not in suppressed else None
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
            "kintsugi": kintsugi,
        }
