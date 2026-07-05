"""machine/architect.py"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from body import BioSystem
from constants import Prisma
from core import LoreManifest, MindSystem, PhysSystem
from machine.crucible import TheCrucible
from machine.forge import TheForge
from machine.pacemaker import ThePacemaker
from machine.theremin import TheTheremin
from presets import BoneConfig
from protocols import LimboLayer
from struts import safe_get, ux


@dataclass
class SystemEmbryo:
    mind: "MindSystem"
    limbo: "LimboLayer"
    bio: "BioSystem"
    physics: "PhysSystem"
    shimmer: Any
    is_gestating: bool = True
    soul_legacy: Optional[Dict] = None
    continuity: Optional[Dict] = None


class BoneArchitect:
    @staticmethod
    def _construct_mind(events, lex, config_ref=None) -> Tuple[MindSystem, LimboLayer]:
        from brain.mind import DreamEngine
        from spores.network import MycelialNetwork

        target_cfg = config_ref or BoneConfig
        _mem = MycelialNetwork(events)
        limbo = LimboLayer(config_ref=target_cfg)
        _mem.cleanup_old_sessions(limbo)
        lore = LoreManifest.get_instance(config_ref=target_cfg)
        mind = MindSystem(
            mem=_mem, lex=lex, dreamer=DreamEngine(events, lore, config_ref=target_cfg)
        )
        return mind, limbo

    @staticmethod
    def _construct_bio(events, mind, lex, config_ref=None) -> BioSystem:
        from body import (
            Biometrics,
            BioSystem,
            EndocrineSystem,
            MetabolicGovernor,
            MitochondrialForge,
            MitochondrialState,
        )
        from spores import BioLichen, BioParasite

        target_cfg = config_ref or BoneConfig
        cfg = safe_get(target_cfg, "METABOLISM", {})
        genesis_val = float(safe_get(cfg, "GENESIS_VOLTAGE", 100.0))
        mito_state = MitochondrialState(atp_pool=genesis_val)
        bio_metrics = Biometrics(
            health=float(safe_get(target_cfg, "MAX_HEALTH", 100.0)),
            stamina=float(safe_get(target_cfg, "MAX_STAMINA", 100.0)),
        )
        return BioSystem(
            mito=MitochondrialForge(mito_state, events, config_ref=target_cfg),
            endo=EndocrineSystem(config_ref=target_cfg),
            lichen=BioLichen(lexicon_ref=lex),
            governor=MetabolicGovernor(config_ref=target_cfg),
            parasite=BioParasite(mind.mem, lex, config_ref=target_cfg),
            events=events,
            biometrics=bio_metrics,
            config_ref=target_cfg,
        )

    @staticmethod
    def _construct_physics(events, bio, mind, lex, config_ref=None) -> PhysSystem:
        from archetypes.village import TheCartographer
        from physics import (
            CosmicDynamics,
            QuantumObserver,
            SurfaceTension,
            TheGatekeeper,
        )

        target_cfg = config_ref or BoneConfig
        gate = TheGatekeeper(lex, config_ref=target_cfg)
        return PhysSystem(
            observer=QuantumObserver(events, lex, config_ref=target_cfg),
            forge=TheForge(lex_ref=lex),
            crucible=TheCrucible(config_ref=target_cfg),
            theremin=TheTheremin(config_ref=target_cfg),
            pulse=ThePacemaker(config_ref=target_cfg),
            nav=TheCartographer(bio.shimmer, config_ref=target_cfg),
            gate=gate,
            tension=SurfaceTension(),
            dynamics=CosmicDynamics(config_ref=target_cfg),
        )

    @staticmethod
    def incubate(events, lex, config_ref=None) -> SystemEmbryo:
        target_cfg = config_ref or BoneConfig
        msg = ux("machine_strings", "arch_incubate")
        if msg:
            events.log(f"{Prisma.GRY}{msg}{Prisma.RST}", "SYS")
        mind, limbo = BoneArchitect._construct_mind(events, lex, config_ref=target_cfg)
        bio = BoneArchitect._construct_bio(events, mind, lex, config_ref=target_cfg)
        physics = BoneArchitect._construct_physics(
            events, bio, mind, lex, config_ref=target_cfg
        )
        return SystemEmbryo(
            mind=mind, limbo=limbo, bio=bio, physics=physics, shimmer=bio.shimmer
        )

    @staticmethod
    def awaken(embryo: SystemEmbryo) -> SystemEmbryo:
        events = embryo.bio.events
        load_result = None
        try:
            if hasattr(embryo.mind.mem, "autoload_last_spore"):
                load_result = embryo.mind.mem.autoload_last_spore()
        except Exception as e:
            msg = (
                ux("machine_strings", "arch_spore_fail")
                or "Spore resurrection failed: {e}"
            )
            events.log(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}", "CRIT")
            load_result = None
        try:
            results = list(load_result) if load_result else []
        except TypeError:
            results = []
        results.extend([None] * max(0, 5 - len(results)))
        mito_legacy, _, soul_legacy, continuity, atlas = results[:5]
        soul_legacy = soul_legacy or {}
        if mito_legacy:
            embryo.bio.mito.apply_inheritance(mito_legacy)
        embryo.soul_legacy = soul_legacy
        embryo.continuity = continuity
        if atlas and embryo.physics.nav:
            try:
                embryo.physics.nav.load_state(atlas)
                msg = (
                    ux("machine_strings", "arch_map_restored") or "World Map restored."
                )
                events.log(f"{Prisma.MAG}{msg}{Prisma.RST}", "SYS")
            except Exception as e:
                msg = (
                    ux("machine_strings", "arch_map_corrupt")
                    or "Atlas corrupt, discarding map: {e}"
                )
                events.log(f"{Prisma.OCHRE}{msg.format(e=e)}{Prisma.RST}", "WARN")
        if embryo.bio.mito.state.atp_pool <= 0.0:
            cfg = safe_get(embryo.bio.config_ref, "METABOLISM", {})
            genesis_val = float(safe_get(cfg, "GENESIS_VOLTAGE", 100.0))
            msg = ux("machine_strings", "arch_cold_boot")
            events.log(
                (
                    msg.format(genesis_val=genesis_val)
                    if msg
                    else f"Cold Boot: {genesis_val} ATP"
                ),
                "SYS",
            )
            embryo.bio.mito.adjust_atp(genesis_val, reason="GENESIS")
        return embryo
