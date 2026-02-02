""" bone_architect.py - "We shape our buildings; thereafter they shape us." - Churchill """

from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
from bone_bus import Prisma, MindSystem, PhysSystem, PhysicsPacket
from bone_village import MirrorGraph, TheNavigator
from bone_spores import MycotoxinFactory, LichenSymbiont, HyphalInterface, ParasiticSymbiont, MycelialNetwork
from bone_body import BioSystem, MitochondrialForge, MitochondrialState, EndocrineSystem, MetabolicGovernor, ViralTracer, ThePacemaker
from bone_brain import DreamEngine, ShimmerState, NeuroPlasticity, GlobalIntegrator, WisdomAllocator
from bone_protocols import LimboLayer
from bone_physics import QuantumObserver, SurfaceTension # [REMOVED] TemporalDynamics
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
            raw_text="[SYSTEM FAILURE: PHYSICS BYPASSED]",
            antigens=0,
            perfection_streak=0,
            turbulence=0.0,
            entropy=0.0,
            mass=1.0,
            velocity=0.0,
            psi=0.0,
            kappa=0.0)

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
            immune=MycotoxinFactory(),
            lichen=LichenSymbiont(),
            gut=HyphalInterface(),
            plasticity=NeuroPlasticity(),
            governor=MetabolicGovernor(),
            shimmer=ShimmerState(),
            parasite=ParasiticSymbiont(mind.mem, lex))

    @staticmethod
    def _construct_physics(events, bio) -> PhysSystem:
        return PhysSystem(
            observer=QuantumObserver(events),
            forge=TheForge(),
            crucible=TheCrucible(),
            theremin=TheTheremin(),
            pulse=ThePacemaker(),
            # [REMOVED] dynamics=TemporalDynamics()
            nav=TheNavigator(bio.shimmer),
            tension=SurfaceTension())

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
        try:
            load_result = embryo.mind.mem.autoload_last_spore()
        except Exception as e:
            events.log(f"{Prisma.RED}[ARCHITECT]: Spore corruption detected ({e}). Clearing heritage.{Prisma.RST}", "SYS")
            load_result = None
        inherited_traits = {}
        inherited_antibodies = set()
        soul_legacy = {}
        continuity_data = None
        if load_result:
            if len(load_result) >= 1: inherited_traits = load_result[0]
            if len(load_result) >= 2: inherited_antibodies = load_result[1]
            if len(load_result) >= 3: soul_legacy = load_result[2]
            if len(load_result) >= 4: continuity_data = load_result[3]
            events.log(f"{Prisma.CYN}[ARCHITECT]: Ancestral Spirit detected.{Prisma.RST}", "SYS")
        else:
            events.log(f"{Prisma.WHT}[ARCHITECT]: No ancestors found. A new lineage begins.{Prisma.RST}", "SYS")
        embryo.bio.mito.state.mother_hash = embryo.mind.mem.session_id
        embryo.bio.mito.apply_inheritance(inherited_traits)
        embryo.bio.immune.active_antibodies = inherited_antibodies
        embryo.soul_legacy = soul_legacy
        embryo.continuity = continuity_data
        embryo.is_gestating = False
        events.log(f"{Prisma.GRN}[ARCHITECT]: Embryo viable. Breaking the shell...{Prisma.RST}", "SYS")
        if hasattr(events, "set_dormancy"):
            events.set_dormancy(False)
        return embryo