""" bone_architect.py - "We shape our buildings; thereafter they shape us." - Churchill """
import random
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
from bone_core import Prisma, MindSystem, PhysSystem, PhysicsPacket, TheLore
from bone_village import MirrorGraph, TheCartographer
from bone_spores import MycelialNetwork, ImmuneMycelium, BioLichen, BioParasite
from bone_symbiosis import MycotoxinFactory, LichenSymbiont, ParasiticSymbiont
from bone_body import BioSystem, MitochondrialForge, MitochondrialState, EndocrineSystem, MetabolicGovernor, ViralTracer, ThePacemaker
from bone_brain import DreamEngine, ShimmerState, NeuroPlasticity
from bone_protocols import LimboLayer
from bone_physics import QuantumObserver, SurfaceTension
from bone_machine import TheCrucible, TheForge, TheTheremin

@dataclass
class SystemEmbryo:
    mind: MindSystem
    limbo: LimboLayer
    bio: BioSystem
    physics: PhysSystem
    shimmer: Any
    is_gestating: bool = True
    soul_legacy: Optional[Dict] = None
    continuity: Optional[Dict] = None

class PanicRoom:
    @staticmethod
    def get_safe_physics():
        narrative = TheLore.get("narrative_data") or {}
        cathedral_logs = narrative.get("CATHEDRAL_COLLAPSE_LOGS", ["[SYSTEM FAILURE]"])
        fail_msg = random.choice(cathedral_logs)
        return PhysicsPacket(
            voltage=5.0,
            narrative_drag=5.0,
            valence=0.0,
            repetition=0.0,
            atmosphere="STABLE",
            clean_words=["system", "error", "recovery"],
            counts={"heavy": 0, "kinetic": 0},
            vector={"STR": 0.5, "VEL": 0.5, "ENT": 0.0},
            flow_state="SAFE_MODE",
            zone="PANIC_ROOM",
            truth_ratio=1.0,
            raw_text=f"[PANIC PROTOCOL]: {fail_msg}",
            antigens=0,
            perfection_streak=0,
            turbulence=0.0,
            entropy=0.0,
            mass=1.0,
            velocity=0.0,
            psi=0.0,
            kappa=0.0,
            beta_index=1.0,
            manifold="BUNKER")

    @staticmethod
    def get_safe_bio(previous_state=None):
        base = {
            "is_alive": True,
            "atp": 10.0,
            "chem": {"DOP": 0.0, "COR": 0.0, "OXY": 0.0, "SER": 0.0},
            "logs": [f"{Prisma.RED}BIO FAIL: Triage Protocol Active.{Prisma.RST}"],
            "respiration": "NECROSIS",
            "enzyme": "NONE"}
        if previous_state and isinstance(previous_state, dict):
            old_chem = previous_state.get("chemistry", {})
            if old_chem:
                base["chem"]["COR"] = min(0.9, old_chem.get("COR", 0.0))
                base["chem"]["SER"] = max(0.2, old_chem.get("SER", 0.0))
        return base

    @staticmethod
    def get_safe_mind():
        return {
            "lens": "NARRATOR",
            "role": "The Backup System",
            "thought": "I cannot think clearly, therefore I still am, but barely.", }

    @staticmethod
    def get_safe_soul():
        return {
            "name": "Traveler",
            "archetype": "The Survivor",
            "virtues": {"resilience": 1.0},
            "vices": {"amnesia": 1.0},
            "narrative_arc": "RECOVERY",
            "xp": 0}

    @staticmethod
    def get_safe_limbo():
        return {
            "mood": "NEUTRAL",
            "volatility": 0.0,
            "mask": "DEFAULT",
            "glitch_factor": 0.0}

class BoneArchitect:
    @staticmethod
    def _construct_mind(events, lex) -> Tuple[MindSystem, LimboLayer]:
        _mem = MycelialNetwork(events, None, None)
        limbo = LimboLayer()
        _mem.cleanup_old_sessions(limbo)
        mind = MindSystem(
            mem=_mem,
            lex=lex,
            dreamer=DreamEngine(events),
            mirror=MirrorGraph(events),
            tracer=ViralTracer(_mem))
        return mind, limbo

    @staticmethod
    def _construct_bio(events, mind, lex) -> BioSystem:
        mito_state = MitochondrialState()
        return BioSystem(
            mito=MitochondrialForge(mito_state, events),
            endo=EndocrineSystem(),
            immune=ImmuneMycelium(),
            lichen=BioLichen(),
            plasticity=NeuroPlasticity(),
            governor=MetabolicGovernor(),
            shimmer=ShimmerState(),
            parasite=BioParasite(mind.mem, lex),
            events=events)

    @staticmethod
    def _construct_physics(events, bio) -> PhysSystem:
        return PhysSystem(
            observer=QuantumObserver(events),
            forge=TheForge(),
            crucible=TheCrucible(),
            theremin=TheTheremin(),
            pulse=ThePacemaker(),
            nav=TheCartographer(bio.shimmer),
            tension=SurfaceTension(),
            dynamics=None)

    @staticmethod
    def incubate(events, lex) -> SystemEmbryo:
        if hasattr(events, "set_dormancy"):
            events.set_dormancy(True)
        events.log(f"{Prisma.GRY}[ARCHITECT]: Laying foundations (Dormancy Active)...{Prisma.RST}", "SYS")
        mind, limbo = BoneArchitect._construct_mind(events, lex)
        bio = BoneArchitect._construct_bio(events, mind, lex)
        physics = BoneArchitect._construct_physics(events, bio)
        return SystemEmbryo(
            mind=mind,
            limbo=limbo,
            bio=bio,
            physics=physics,
            shimmer=bio.shimmer,
            is_gestating=True)

    @staticmethod
    def awaken(embryo: SystemEmbryo) -> SystemEmbryo:
        events = embryo.bio.mito.events
        load_result = None
        try:
            if hasattr(embryo.mind.mem, "autoload_last_spore"):
                load_result = embryo.mind.mem.autoload_last_spore()
        except Exception as e:
            events.log(f"{Prisma.RED}[ARCHITECT]: Spore resurrection failed: {e}{Prisma.RST}", "CRIT")
            load_result = None
        embryo.soul_legacy = {}
        embryo.continuity = None
        recovered_atlas = {}
        if load_result and isinstance(load_result, (list, tuple)):
            count = len(load_result)
            if count > 0:
                if hasattr(embryo.bio.mito, 'apply_inheritance'):
                    embryo.bio.mito.apply_inheritance(load_result[0])
            if count > 1 and isinstance(load_result[1], (list, set)):
                if hasattr(embryo.bio.immune, 'load_antibodies'):
                    embryo.bio.immune.load_antibodies(load_result[1])
            if count > 2 and isinstance(load_result[2], dict):
                embryo.soul_legacy = load_result[2]
            if count > 3 and isinstance(load_result[3], dict):
                embryo.continuity = load_result[3]
            if count > 4 and isinstance(load_result[4], dict):
                recovered_atlas = load_result[4]
        if recovered_atlas and hasattr(embryo.physics, "nav"):
            if hasattr(embryo.physics.nav, "import_atlas"):
                try:
                    embryo.physics.nav.import_atlas(recovered_atlas)
                    events.log(f"{Prisma.MAG}[ARCHITECT]: World Map restored from Spore.{Prisma.RST}", "SYS")
                except Exception as e:
                    events.log(f"{Prisma.OCHRE}[ARCHITECT]: Atlas corrupt, discarding map: {e}{Prisma.RST}", "WARN")
        return embryo