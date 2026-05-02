"""
genesis.py

The Big Bang.
This module is responsible for the sequence of events that brings the engine from a static
configuration state into a living, metabolizing instance. It wires the biological substrate
(the Embryo), the permanent memory (Akashic Record), the psychological state (The Soul),
and the regulatory archetypes (The Village) together into a single, cohesive lattice.
"""

from typing import Dict, Any, Set
from brain.akashic import TheAkashicRecord
from presets import BoneConfig
from core import EventBus, LoreManifest
from struts import ux
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
    """
    The orchestrator of the boot sequence. It does not contain state itself;
    rather, it is the factory that ensures the interdependent systems are spun up
    in the correct physical and chronological order.
    """

    @staticmethod
    def ignite(config: Dict[str, Any], lexicon_ref: Any, events_ref: Any = None) -> Dict[str, Any]:
        """
        The spark. This method executes the critical path of system initialization.
        It builds the foundation (Events, Memory), incubates the core mechanics (Embryo),
        and then loads the specific human constraints (Soul, Trauma, Village).

        Args:
            config: The root configuration dictionary determining reality parameters.
            lexicon_ref: The shared dictionary of system terminology.
            events_ref: An optional pre-existing EventBus. If none is provided, we build the nervous system from scratch.

        Returns:
            A dictionary containing the fully awakened, interlinked core systems.
        """
        # 1. The Nervous System
        events = events_ref or EventBus()
        log_msg = ux("genesis_strings", "ignite_log") or "Igniting lattice..."
        events.log(f"{Prisma.CYN}{log_msg}{Prisma.RST}", "GENESIS")

        target_cfg = config.get("config") or BoneConfig

        # 2. Permanent Memory (The Substrate)
        # We must load the Akashic record early so that subsequent systems can verify their history.
        akashic = TheAkashicRecord(lore_manifest=LoreManifest.get_instance(config_ref=target_cfg), events_ref=events)
        akashic.setup_listeners(events)

        # 3. Biological & Mechanical Incubation
        # The Architect builds the raw physical capability of the system before consciousness is applied.
        seed = BoneArchitect.incubate(events, lexicon_ref, config_ref=target_cfg)
        embryo = BoneArchitect.awaken(seed)

        # 4. Immune Regulation & Archetype Suppression
        # Not all instances require all village members. Here we define the boundaries.
        mode_settings = config.get("mode_settings") or {}
        suppressed_set = set(mode_settings.get("village_suppression") or [])

        village_bundle = BoneGenesis._summon_village(
            events,
            embryo,
            akashic,
            suppressed_set,
            config.get("boot_mode", "ADVENTURE"),
            target_cfg,
            lexicon_ref,
        )

        # 5. The Narrative Self & Legacy State
        # Restoring the subjective "I" of the system. If this embryo has lived before,
        # we load its past subjective state to maintain continuity.
        soul = NarrativeSelf(engine_ref=None, events_ref=events, memory_ref=embryo.mind.mem, akashic_ref=akashic, config_ref=target_cfg)
        if embryo.soul_legacy:
            soul.load_from_dict(embryo.soul_legacy)

        # 6. Karma & Systemic Friction (The Oroboros)
        # Here we calculate the cost of past actions. We do not allow a clean slate if the
        # previous session ended in critical decay or trauma.
        oroboros = TheOroboros(config_ref=target_cfg)
        if embryo.physics:
            cfg_gen = getattr(target_cfg, "GENESIS", None)
            base_voltage = getattr(cfg_gen, "DUMMY_VOLTAGE", 10.0)
            base_drag = getattr(cfg_gen, "DUMMY_DRAG", 0.0)

            # We create a dummy physics object to calculate the delta of legacy scars.
            dummy_phys = {"narrative_drag": base_drag, "voltage": base_voltage}
            mem = getattr(embryo.mind, "mem", None)
            bio_proxy = {"trauma_vector": getattr(mem, "session_trauma_vector", {}) if mem else {}}

            # If the Oroboros detects legacy consequences, we physically alter the fresh embryo.
            if logs := oroboros.apply_legacy(dummy_phys, bio_proxy):
                msg = ux("genesis_strings", "legacy_scars") or "The lattice remembers. Inherited scars: {logs}"
                events.log(f"{Prisma.MAG}{msg.format(logs=', '.join(logs))}{Prisma.RST}", "OROBOROS")

                # Direct, native application of inherited physics.
                applied_drag = dummy_phys.get("narrative_drag", base_drag) - base_drag
                if applied_drag:
                    embryo.physics.narrative_drag += float(applied_drag)

                # Penalize starting energy (Voltage) if the last session was exhausted.
                volt_penalty = base_voltage - dummy_phys.get("voltage", base_voltage)
                if volt_penalty > 0:
                    embryo.physics.voltage = max(0.0, embryo.physics.voltage - volt_penalty)

            # Re-attach the persistent trauma directly to the active session memory.
            if mem:
                mem.session_trauma_vector = bio_proxy.get("trauma_vector", {})

        # 7. Final Dependency Injections
        # Spin up the auxiliary drivers, symbiosis management, and the REM consolidator.
        drivers = DriverRegistry(events, config_ref=target_cfg)
        consultant = BoneConsultant(config_ref=target_cfg, lexicon_ref=lexicon_ref) if "CONSULTANT" not in suppressed_set else None
        symbiosis = SymbiosisManager(events, config_ref=target_cfg)
        consolidator = TheConsolidator(events_ref=events, memory_ref=embryo.mind.mem, akashic_ref=akashic)

        # The organism is fully awake.
        return {"events": events, "akashic": akashic, "embryo": embryo, "village": village_bundle, "soul": soul,
                "oroboros": oroboros, "drivers": drivers, "consultant": consultant, "symbiosis": symbiosis,
                "consolidator": consolidator}

    @staticmethod
    def _summon_village(events, embryo, akashic, suppressed: Set[str], boot_mode: str = "ADVENTURE", config_ref=None, lexicon_ref=None) -> Dict[str, Any]:
        """
        Populates the regulatory and archetypal layer of the engine.
        This is where we instantiate the various 'voices' and mechanics (Gordon, The Bureau, Zen)
        that will govern the logic and constraints of the session.

        Args:
            suppressed: A set of string keys representing modules that should be intentionally
                        starved/disabled for this session to save on cognitive load.
        """
        c = config_ref

        # A Schur-approved pragmatic shortcut: if the key is in the suppressed set,
        # return None, otherwise initialize the class with the provided arguments.
        spawn = lambda key, cls, *args, **kwargs: cls(*args, **kwargs) if key not in suppressed else None

        # Gordon is the primary anchor point for physical reality constraints.
        gordon = spawn("GORDON", GordonKnot, events=events, mode=boot_mode, config_ref=c)

        # The Cartographer relies on Shimmer, so we handle it specifically.
        navigator = spawn("NAVIGATOR", TheCartographer, embryo.shimmer, config_ref=c)

        # Base protocol loads if not suppressed.
        if "DEATH" not in suppressed: DeathGen.load_protocols()
        if "REPRO" not in suppressed: LiteraryReproduction.load_genetics(config_ref=c)

        # Return the active directory of the Village.
        return {
            "gordon": gordon,
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
            "therapist": spawn("THERAPIST", TheTherapist, events, config_ref=c),
            "gravedigger": spawn("GRAVEDIGGER", TheGraveDigger, gordon, events, config_ref=c),
        }