""" bone_architect.py - "We shape our buildings; thereafter they shape us." - Churchill """

from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
from bone_bus import Prisma, MindSystem, PhysSystem, PhysicsPacket
from bone_village import MirrorGraph, TheNavigator
from bone_spores import MycelialNetwork
from bone_body import BioSystem, MitochondrialForge, MitochondrialState, EndocrineSystem, MetabolicGovernor, ViralTracer, ThePacemaker
from bone_brain import DreamEngine, ShimmerState, NeuroPlasticity, GlobalIntegrator, WisdomAllocator
from bone_personality import LimboLayer
from bone_physics import TemporalDynamics, QuantumObserver, Tension
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

class PanicRoom:
    @staticmethod
    def get_safe_physics():
        return PhysicsPacket(
            voltage=5.0,
            narrative_drag=5.0,
            clean_words=["system", "error", "recovery"],
            vector={"STR": 0.5, "VEL": 0.5, "ENT": 0.0},
            counts={"heavy": 0, "kinetic": 0},
            raw_text="[SYSTEM FAILURE: PHYSICS BYPASSED]",
            psi=0.5,
            kappa=0.5,
            flow_state="SAFE_MODE",
            zone="PANIC_ROOM")

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
            "thought": "I cannot think clearly, therefore I still am, but barely.",}

class BoneArchitect:
    @staticmethod
    def _construct_mind(events, lex) -> Tuple[MindSystem, LimboLayer]:
        _mem = MycelialNetwork(events)
        limbo = LimboLayer()
        _mem.cleanup_old_sessions(limbo)
        mind = MindSystem(
            mem=_mem,
            lex=lex,
            dreamer=DreamEngine(events),
            mirror=MirrorGraph(events),
            tracer=ViralTracer(_mem))
        mind.integrator = GlobalIntegrator()
        mind.wise = WisdomAllocator()
        return mind, limbo

    @staticmethod
    def _construct_bio(events, mind, lex) -> BioSystem:
        mito_state = MitochondrialState()
        return BioSystem(
            mito=MitochondrialForge(mito_state, events),
            endo=EndocrineSystem(),
            plasticity=NeuroPlasticity(),
            governor=MetabolicGovernor(),
            shimmer=ShimmerState(),
            events=events)

    @staticmethod
    def _construct_physics(events, bio) -> PhysSystem:
        return PhysSystem(
            observer=QuantumObserver(events),
            forge=TheForge(),
            crucible=TheCrucible(),
            theremin=TheTheremin(),
            pulse=ThePacemaker(),
            dynamics=TemporalDynamics(),
            nav=TheNavigator(bio.shimmer),
            tension=Tension())

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
        load_result = embryo.mind.mem.autoload_last_spore()
        inherited_traits = {}
        soul_legacy = {}
        if load_result:
            if isinstance(load_result, tuple):
                if len(load_result) >= 1: inherited_traits = load_result[0]
                if len(load_result) >= 3: soul_legacy = load_result[2]
            events.log(f"{Prisma.CYN}[ARCHITECT]: Ancestral Spirit detected.{Prisma.RST}", "SYS")
        else:
            events.log(f"{Prisma.WHT}[ARCHITECT]: No ancestors found. A new lineage begins.{Prisma.RST}", "SYS")
        embryo.bio.mito.state.mother_hash = embryo.mind.mem.session_id
        embryo.bio.mito.apply_inheritance(inherited_traits)
        embryo.soul_legacy = soul_legacy
        embryo.is_gestating = False
        events.log(f"{Prisma.GRN}[ARCHITECT]: Embryo viable. Breaking the shell...{Prisma.RST}", "SYS")
        if hasattr(events, "set_dormancy"):
            events.set_dormancy(False)
        return embryo