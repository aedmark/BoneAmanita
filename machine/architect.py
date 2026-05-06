"""machine/architect.py
This module acts as the prime mover for the entire simulation. It is responsible
for the sequential assembly of the three core pillars: Mind, Bio, and Physics.
It utilizes a two-phase initialization: 'Incubation' (building the raw objects)
and 'Awakening' (loading previous state/memory and jumpstarting the metabolism).
"""
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any
from body import BioSystem
from core import LoreManifest, PhysSystem, MindSystem
from struts import ux, safe_get
from presets import BoneConfig
from protocols import LimboLayer
from constants import Prisma
from machine.tracer import ViralTracer
from machine.forge import TheForge
from machine.crucible import TheCrucible
from machine.theremin import TheTheremin
from machine.pacemaker import ThePacemaker


@dataclass
class SystemEmbryo:
    """
    A temporary structural container. It holds the unbooted components of the
    universe before they are fully integrated and animated by the event loop.
    """
    mind: 'MindSystem'
    limbo: 'LimboLayer'
    bio: 'BioSystem'
    physics: 'PhysSystem'
    shimmer: Any
    is_gestating: bool = True
    soul_legacy: Optional[Dict] = None
    continuity: Optional[Dict] = None


class BoneArchitect:
    """
    The master builder class. Contains only static methods to prevent state
    leakage during the highly volatile creation phase of the system.
    """

    @staticmethod
    def _construct_mind(events, lex, config_ref=None) -> Tuple[MindSystem, LimboLayer]:
        """
        Assembles the cognitive layer. Sets up the memory network, the dream engine,
        and the viral tracer that monitors for toxic idea propagation.
        """
        from spores.network import MycelialNetwork
        from brain.mind import DreamEngine
        target_cfg = config_ref or BoneConfig
        _mem = MycelialNetwork(events)
        limbo = LimboLayer(config_ref=target_cfg)
        _mem.cleanup_old_sessions(limbo)
        lore = LoreManifest.get_instance(config_ref=target_cfg)
        mind = MindSystem(
            mem=_mem,
            lex=lex,
            dreamer=DreamEngine(events, lore, config_ref=target_cfg),
            tracer=ViralTracer(_mem),
        )
        return mind, limbo

    @staticmethod
    def _construct_bio(events, mind, lex, config_ref=None) -> BioSystem:
        """
        Assembles the biological and somatic engines. This dictates the metabolic
        cost of interactions and manages the health/stamina constraints.
        """
        from body import BioSystem, MitochondrialState, Biometrics, MitochondrialForge, EndocrineSystem, \
            MetabolicGovernor
        from spores import ImmuneMycelium, BioLichen, BioParasite
        target_cfg = config_ref or BoneConfig
        cfg = getattr(target_cfg, "METABOLISM", None)
        genesis_val = safe_get(cfg, "GENESIS_VOLTAGE", 100.0)
        mito_state = MitochondrialState(atp_pool=genesis_val)
        bio_metrics = Biometrics(
            health=getattr(target_cfg, "MAX_HEALTH", 100.0),
            stamina=getattr(target_cfg, "MAX_STAMINA", 100.0)
        )
        return BioSystem(
            mito=MitochondrialForge(mito_state, events, config_ref=target_cfg),
            endo=EndocrineSystem(config_ref=target_cfg),
            immune=ImmuneMycelium(),
            lichen=BioLichen(lexicon_ref=lex),
            governor=MetabolicGovernor(config_ref=target_cfg),
            parasite=BioParasite(mind.mem, lex, config_ref=target_cfg),
            events=events,
            biometrics=bio_metrics,
            config_ref=target_cfg,
        )

    @staticmethod
    def _construct_physics(events, bio, mind, lex, config_ref=None) -> PhysSystem:
        """
        Assembles the physical laws and boundaries of the simulation, dictating
        how objects interact, how time moves, and what the observer can perceive.
        """
        from archetypes.village import TheCartographer
        from physics import TheGatekeeper, QuantumObserver, SurfaceTension, CosmicDynamics
        target_cfg = config_ref or BoneConfig
        gate = TheGatekeeper(lex, config_ref=target_cfg)
        return PhysSystem(
            observer=QuantumObserver(events, lex, config_ref=target_cfg),
            forge=TheForge(lex_ref=lex),
            crucible=TheCrucible(config_ref=target_cfg),
            theremin=TheTheremin(config_ref=target_cfg),
            pulse=ThePacemaker(config_ref=target_cfg),
            nav=TheCartographer(getattr(bio, "shimmer", None), config_ref=target_cfg),
            gate=gate,
            tension=SurfaceTension(),
            dynamics=CosmicDynamics(config_ref=target_cfg),
        )

    @staticmethod
    def incubate(events, lex, config_ref=None) -> SystemEmbryo:
        """
        Phase 1 of Boot: Assembly.
        Constructs the raw, empty systems. No historical memory is loaded yet.
        """
        target_cfg = config_ref or BoneConfig
        if hasattr(events, "set_dormancy"):
            events.set_dormancy(True)
        msg = ux("machine_strings", "arch_incubate")
        if msg:
            events.log(f"{Prisma.GRY}{msg}{Prisma.RST}", "SYS")
        mind, limbo = BoneArchitect._construct_mind(events, lex, config_ref=target_cfg)
        bio = BoneArchitect._construct_bio(events, mind, lex, config_ref=target_cfg)
        physics = BoneArchitect._construct_physics(events, bio, mind, lex, config_ref=target_cfg)
        return SystemEmbryo(
            mind=mind,
            limbo=limbo,
            bio=bio,
            physics=physics,
            shimmer=getattr(bio, "shimmer", None)
        )

    @staticmethod
    def awaken(embryo: SystemEmbryo) -> SystemEmbryo:
        """
        Phase 2 of Boot: Animation.
        Attempts to load the last known state (a 'Spore') from the Mycelial Network
        and map it onto the freshly incubated embryo.
        """
        events = embryo.bio.mito.events
        load_result = None
        try:
            if hasattr(embryo.mind.mem, "autoload_last_spore"):
                load_result = embryo.mind.mem.autoload_last_spore()
        except Exception as e:
            msg = ux("machine_strings", "arch_spore_fail") or "[ARCHITECT]: Spore resurrection failed: {e}"
            events.log(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}", "CRIT")
            load_result = None
        results = (list(load_result) if isinstance(load_result, (list, tuple)) else []) + [None] * 5
        mito_legacy, immune_legacy, soul_legacy, continuity, atlas = results[:5]
        if mito_legacy:
            embryo.bio.mito.apply_inheritance(mito_legacy)
        if immune_legacy and isinstance(immune_legacy, (list, set)):
            embryo.bio.immune.active_antibodies.update(immune_legacy)
        embryo.soul_legacy = soul_legacy if isinstance(soul_legacy, dict) else {}
        embryo.continuity = continuity if isinstance(continuity, dict) else None
        recovered_atlas = atlas if isinstance(atlas, dict) else {}
        if recovered_atlas and getattr(embryo.physics, "nav", None):
            try:
                embryo.physics.nav.import_atlas(recovered_atlas)
                msg = ux("machine_strings", "arch_map_restored") or "[ARCHITECT]: World Map restored."
                events.log(f"{Prisma.MAG}{msg}{Prisma.RST}", "SYS")
            except Exception as e:
                msg = ux("machine_strings", "arch_map_corrupt") or "[ARCHITECT]: Atlas corrupt, discarding map: {e}"
                events.log(f"{Prisma.OCHRE}{msg.format(e=e)}{Prisma.RST}", "WARN")
        if embryo.bio and embryo.bio.mito and embryo.bio.mito.state.atp_pool <= 0.0:
            target_cfg = getattr(embryo.bio, "config_ref", None) or BoneConfig
            cfg = getattr(target_cfg, "METABOLISM", None)
            genesis_val = safe_get(cfg, "GENESIS_VOLTAGE", 100.0)
            msg = ux("machine_strings", "arch_cold_boot")
            events.log((msg.format(genesis_val=genesis_val) if msg else f"Cold Boot: {genesis_val} ATP"), "SYS")
            embryo.bio.mito.adjust_atp(genesis_val, reason="GENESIS")
        return embryo
