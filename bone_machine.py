import random
from dataclasses import dataclass
from typing import Tuple, Optional, List, Dict, Any

from bone_body import BioSystem, MitochondrialState, Biometrics, MitochondrialForge, EndocrineSystem, MetabolicGovernor
from bone_brain import DreamEngine, ShimmerState
from bone_config import BoneConfig
from bone_core import LoreManifest
from bone_lexicon import LexiconService
from bone_physics import TheGatekeeper, QuantumObserver, SurfaceTension, ZoneInertia
from bone_protocols import LimboLayer
from bone_spores import MycelialNetwork, ImmuneMycelium, BioLichen, BioParasite
from bone_types import MindSystem, PhysSystem, PhysicsPacket, Prisma


class TheCrucible:
    def __init__(self):
        self.max_voltage_cap = getattr(BoneConfig.MACHINE, "CRUCIBLE_VOLTAGE_CAP", 20.0)
        self.active_state = "COLD"
        self.dampener_charges = 3
        self.dampener_tolerance = getattr(
            BoneConfig.MACHINE, "DAMPENER_TOLERANCE", 15.0
        )
        self.instability_index = 0.0
        self.logs = self._load_logs()

    @staticmethod
    def _load_logs():
        base = {
            "DAMPER_EMPTY": "⚠️ DAMPER EMPTY",
            "DAMPER_HIT": "🛡️ DAMPENER: -{reduction:.1f}v ({reason})",
            "HOLDING": "Holding Charge",
            "REGULATOR": "⚖️ REGULATOR: {direction} (Drag {current:.1f} -> {new:.1f})",
            "SURGE": "⚡ SURGE: Absorbed {voltage}v.",
            "RITUAL": "🔥 RITUAL: Capacity +{gain:.1f}v",
            "MELTDOWN": "💥 MELTDOWN: Hull Breach (-{damage:.1f} HP)"
        }
        manifest = LoreManifest.get_instance().get("narrative_data") or {}
        return manifest.get("CRUCIBLE_LOGS", base)

    def dampener_status(self):
        return f"🛡️ Charges: {self.dampener_charges}"

    def dampen(
        self, voltage_spike: float, stability_index: float
    ) -> Tuple[bool, str, float]:
        if self.dampener_charges <= 0:
            return False, "⚠️ DAMPER EMPTY", 0.0
        should_dampen = False
        reduction_factor = 0.0
        reason = ""
        if voltage_spike > self.dampener_tolerance:
            should_dampen = True
            reduction_factor = 0.7
            reason = "Circuit Breaker"
        elif voltage_spike > 8.0 and stability_index < 0.3:
            should_dampen = True
            reduction_factor = 0.4
            reason = "Instability"
        if should_dampen:
            self.dampener_charges -= 1
            reduction = voltage_spike * reduction_factor
            msg = self.logs.get("DAMPER_HIT", "🛡️ Hit").format(reduction=reduction, reason=reason)
            return True, msg, reduction
        return False, self.logs.get("HOLDING", "Holding"), 0.0

    def audit_fire(self, physics: Dict) -> Tuple[str, float, Optional[str]]:
        voltage = physics.get("voltage", 0.0)
        structure = physics.get("kappa", 0.0)
        ideal_voltage = structure * 20.0
        delta = voltage - ideal_voltage
        self.instability_index = (self.instability_index * 0.7) + (delta * 0.3)
        if abs(self.instability_index) < 0.1:
            self.instability_index = 0.0
        current_drag = physics.get("narrative_drag", 0.0)
        adjustment = self.instability_index * 0.5
        if current_drag < 1.0 and adjustment < 0:
            adjustment *= 0.1
        new_drag = max(0.0, min(10.0, current_drag + adjustment))
        physics["narrative_drag"] = round(new_drag, 2)
        msg = None
        if abs(adjustment) > 0.1:
            direction = "TIGHTENING" if adjustment > 0 else "RELAXING"
            msg = self.logs.get("REGULATOR", "⚖️ REG").format(direction=direction, current=current_drag, new=new_drag)
        if physics.get("system_surge_event", False):
            self.active_state = "SURGE"
            return "SURGE", 0.0, self.logs.get("SURGE", "⚡ SURGE").format(voltage=voltage)
        if voltage > 18.0:
            if structure > 0.5:
                gain = voltage * 0.1
                self.max_voltage_cap += gain
                self.active_state = "RITUAL"
                return "RITUAL", gain, self.logs.get("RITUAL", "🔥 RITUAL").format(gain=gain)
            else:
                damage = voltage * 0.5
                self.active_state = "MELTDOWN"
                return (
                    "MELTDOWN",
                    damage,
                    self.logs.get("MELTDOWN", "💥 MELTDOWN").format(damage=damage)
                )
        self.active_state = "REGULATED"
        return "REGULATED", adjustment, msg


class TheForge:
    def __init__(self):
        gordon_data = LoreManifest.get_instance().get("gordon") or {}
        raw_recipes = gordon_data.get("RECIPES", [])
        self.recipe_map = {}
        for r in raw_recipes:
            ing = r.get("ingredient")
            if ing:
                if ing not in self.recipe_map:
                    self.recipe_map[ing] = []
                self.recipe_map[ing].append(r)

    @staticmethod
    def hammer_alloy(physics: Dict) -> Tuple[bool, Optional[str], Optional[str]]:
        counts = physics.get("counts", {})
        clean_words = physics.get("clean_words", [])
        if not clean_words:
            return False, None, None
        heavy = counts.get("heavy", 0)
        kinetic = counts.get("kinetic", 0)
        avg_density = ((heavy * 2.0) + (kinetic * 0.5)) / len(clean_words)
        if random.random() >= (physics.get("voltage", 0) / 20.0) * avg_density:
            return False, None, None
        if heavy > 3:
            return True, f"🔨 FORGED: Lead Boots (Mass {avg_density:.1f})", "LEAD_BOOTS"
        if kinetic > 3:
            return True, "🔨 FORGED: Safety Scissors (Kinetic)", "SAFETY_SCISSORS"
        return True, "🔨 FORGED: Anchor Stone", "ANCHOR_STONE"

    def attempt_crafting(
        self, physics: Dict, inventory_list: List[str]
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        if not inventory_list:
            return False, None, None, None
        clean_words = physics.get("clean_words", [])
        if not clean_words:
            return False, None, None, None
        clean_set = set(clean_words)
        voltage = float(physics.get("voltage", 0))
        for item in inventory_list:
            if item in self.recipe_map:
                for recipe in self.recipe_map[item]:
                    cat_words = LexiconService.get(recipe["catalyst_category"])
                    if not cat_words or clean_set.isdisjoint(cat_words):
                        continue
                    hits = len(clean_set.intersection(cat_words))
                    entanglement = self._calculate_entanglement(hits, voltage)
                    if random.random() < entanglement:
                        return (
                            True,
                            f"⚗️ ALCHEMY: {recipe['result']} (via {item})",
                            item,
                            recipe["result"],
                        )
                    else:
                        return (
                            False,
                            f"⚠️ ALCHEMY FAIL: Decoherence ({int(entanglement * 100)}%)",
                            None,
                            None,
                        )
        return False, None, None, None

    @staticmethod
    def _calculate_entanglement(hit_count: int, voltage: float) -> float:
        return min(1.0, 0.2 + (hit_count * 0.1) + (voltage / 133.0))

    @staticmethod
    def transmute(physics: Dict) -> Optional[str]:
        counts = physics.get("counts", {})
        voltage = float(physics.get("voltage", 0))
        gamma = float(physics.get("gamma", 0.0))
        if gamma < 0.15 and counts.get("abstract", 0) > 1:
            return f"⚠️ EMULSION FAIL: Add Binder (Heavy)."
        if voltage > 15.0:
            return f"🌡️ OVERHEAT: {voltage:.1f}v. Add Coolant (Aerobic)."
        return None


class TheTheremin:
    def __init__(self):
        self.decoherence_buildup = 0.0
        self.classical_turns = 0
        self.AMBER_THRESHOLD = 20.0
        self.SHATTER_POINT = 100.0
        self.is_stuck = False
        self.logs = self._load_logs()

    @staticmethod
    def _load_logs():
        base = {
            "MELT": "🔥 MELT: -{val:.1f} Resin",
            "CALCIFY": "🗿 CALCIFICATION: Turn {turns} (+{val:.1f} Resin)",
            "SHATTER": "🔨 SHATTER: -{val:.1f} Resin",
            "RESIN": "🎻 RESIN: +{val:.1f}",
            "TURBULENCE": "🌊 TURBULENCE: -{val:.1f} Resin",
            "COLLAPSE": "💣 COLLAPSE: AIRSTRIKE INITIATED (Drag +20, Voltage 0)"
        }
        manifest = LoreManifest.get_instance().get("narrative_data") or {}
        return manifest.get("THEREMIN_LOGS", base)

    def listen(
        self, physics: Dict, governor_mode="COURTYARD"
    ) -> Tuple[bool, float, Optional[str], Optional[str]]:
        counts = physics.get("counts", {})
        voltage = float(physics.get("voltage", 0.0))
        turb = float(physics.get("turbulence", 0.0))
        rep = float(physics.get("repetition", 0.0))
        complexity = float(physics.get("truth_ratio", 0.0))
        ancient_mass = (
            counts.get("heavy", 0) + counts.get("thermal", 0) + counts.get("cryo", 0)
        )
        modern_mass = counts.get("abstract", 0)
        raw_mix = min(ancient_mass, modern_mass)
        resin_flow = raw_mix * 2.0
        if governor_mode == "LABORATORY":
            resin_flow *= 0.5
        if voltage > 5.0:
            resin_flow = max(0.0, resin_flow - (voltage * 0.6))
        thermal_hits = counts.get("thermal", 0)
        theremin_msg = ""
        melt_thresh = getattr(BoneConfig.MACHINE, "THEREMIN_MELT_THRESHOLD", 5.0)
        critical_event = None
        if thermal_hits > 0 and self.decoherence_buildup > melt_thresh:
            dissolved = thermal_hits * 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - dissolved)
            self.classical_turns = 0
            theremin_msg = self.logs.get("MELT", "🔥 MELT").format(val=dissolved)
        if rep > 0.5:
            self.classical_turns += 1
            slag = self.classical_turns * 2.0
            self.decoherence_buildup += slag
            theremin_msg = self.logs.get("CALCIFY", "🗿 CALCIFY").format(turns=self.classical_turns, val=slag)
        elif complexity > 0.4 and self.classical_turns > 0:
            self.classical_turns = 0
            relief = 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - relief)
            theremin_msg = self.logs.get("SHATTER", "🔨 SHATTER").format(val=relief)
        elif resin_flow > 0.5:
            self.decoherence_buildup += resin_flow
            theremin_msg = self.logs.get("RESIN", "🎻 RESIN").format(val=resin_flow)
        if turb > 0.6 and self.decoherence_buildup > 0:
            shatter_amt = turb * 10.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - shatter_amt)
            theremin_msg = self.logs.get("TURBULENCE", "🌊 TURBULENCE").format(val=shatter_amt)
            self.classical_turns = 0
        if turb < 0.2:
            physics["narrative_drag"] = max(
                0.0, float(physics.get("narrative_drag", 0)) - 1.0
            )
        if self.decoherence_buildup > self.SHATTER_POINT:
            self.decoherence_buildup = 0.0
            self.classical_turns = 0
            if isinstance(physics, dict):
                physics["narrative_drag"] = max(
                    physics.get("narrative_drag", 0.0) + 20.0, 20.0
                )
                physics["voltage"] = 0.0
            return (
                False,
                resin_flow,
                self.logs.get("COLLAPSE", "💣 COLLAPSE"),
                "AIRSTRIKE",
            )
        if self.classical_turns > 3:
            critical_event = "CORROSION"
            theremin_msg = f"{theremin_msg or ''} | ⚠️ CORROSION"
        if self.decoherence_buildup > self.AMBER_THRESHOLD:
            self.is_stuck = True
            theremin_msg = f"{theremin_msg or ''} | 🍯 STUCK"
        elif self.is_stuck and self.decoherence_buildup < 5.0:
            self.is_stuck = False
            theremin_msg = f"{theremin_msg or ''} | 🦋 FREE"
        return self.is_stuck, resin_flow, theremin_msg, critical_event

    def get_readout(self):
        status = "STUCK" if self.is_stuck else "FLOW"
        return f"🎻 THEREMIN   Resin {self.decoherence_buildup:.1f}  Status {status}"

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


SAFE_BIO_DEFAULTS: Dict[str, Any] = {
    "is_alive": True,
    "atp": 10.0,
    "respiration": "NECROSIS",
    "enzyme": "NONE",
    "chem": {
        "DOP": 0.0, "COR": 0.0, "OXY": 0.0,
        "SER": 0.0, "ADR": 0.0, "MEL": 0.0
    },
}


class PanicRoom:
    @staticmethod
    def get_safe_physics():
        safe_packet = PhysicsPacket.void_state()
        safe_packet.voltage = 0.0
        safe_packet.narrative_drag = 0.0
        safe_packet.exhaustion = 0.0
        safe_packet.beta_index = 0.0
        safe_packet.psi = 0.0
        safe_packet.chi = 0.0
        safe_packet.entropy = 0.0
        safe_packet.valence = 0.0
        safe_packet.kappa = 0.0
        safe_packet.psi = 0.0
        safe_packet.chi = 0.0
        safe_packet.entropy = 0.0
        safe_packet.valence = 0.0
        safe_packet.kappa = 0.0
        safe_packet.vector = {
            k: 0.0
            for k in ["STR", "VEL", "PSI", "ENT", "PHI", "BET", "DEL", "LAMBDA", "CHI"]
        }
        safe_packet.clean_words = ["white", "room", "safe", "mode"]
        safe_packet.raw_text = "[PANIC PROTOCOL]: SAFE_MODE. You will wake up in a white room. Do not be alarmed."
        safe_packet.flow_state = "SAFE_MODE"
        safe_packet.zone = "PANIC_ROOM"
        safe_packet.manifold = "WHITE_ROOM"
        return safe_packet

    @staticmethod
    def get_safe_bio(previous_state=None):
        base = {"is_alive": True, "atp": 10.0, "respiration": "NECROSIS", "enzyme": "NONE", "chem": {
            "DOP": 0.0,
            "COR": 0.0,
            "OXY": 0.0,
            "SER": 0.0,
            "ADR": 0.0,
            "MEL": 0.0,
        }, "logs": [
            f"{Prisma.RED}BIO FAIL: Panic Room Protocol Active. Sensory input severed.{Prisma.RST}"
        ]}
        state = previous_state or {}
        if isinstance(state, dict):
            if old_chem := state.get("chemistry", {}):
                base["chem"]["COR"] = 0.0
                base["chem"]["ADR"] = 0.0
                base["chem"]["SER"] = max(0.2, old_chem.get("SER", 0.0))
        return base

    @staticmethod
    def get_safe_mind():
        return {
            "lens": "GORDON",
            "role": "Panic Room Overseer",
            "thought": "SAFE_MODE. You will wake up in a white room. Do not be alarmed.",
        }

    @staticmethod
    def get_safe_soul():
        return {
            "name": "Traveler",
            "archetype": "The Survivor",
            "virtues": {"resilience": 1.0},
            "vices": {"amnesia": 1.0},
            "narrative_arc": "RECOVERY",
            "xp": 0,
        }

    @staticmethod
    def get_safe_limbo():
        return {
            "mood": "NEUTRAL",
            "volatility": 0.0,
            "mask": "DEFAULT",
            "glitch_factor": 0.0,
        }


class ViralTracer:
    def __init__(self, memory_ref):
        self.memory = memory_ref
        self.active_loops = []

    @staticmethod
    def inject(start_node: str) -> Optional[List[str]]:
        if random.random() < 0.05:
            return [start_node, "echo", "void", start_node]
        return None

    @staticmethod
    def psilocybin_rewire(loop_path: List[str]) -> str:
        return f"Rewired logic loop: {'->'.join(loop_path)}"


class ThePacemaker:
    def __init__(self):
        self.boredom_level = 0.0
        self.heart_rate = 60
        self.BOREDOM_THRESHOLD = getattr(BoneConfig, "BOREDOM_THRESHOLD", 10.0)

    def beat(self, stress: float):
        self.heart_rate = 60 + (stress * 20)

    def update(self, repetition_score: float, voltage: float):
        if repetition_score > 0.5 or voltage < 5.0:
            self.boredom_level += 1.0
        else:
            self.boredom_level = max(0.0, self.boredom_level - 2.0)

    def is_bored(self) -> bool:
        return self.boredom_level > self.BOREDOM_THRESHOLD


class BoneArchitect:
    @staticmethod
    def _construct_mind(events, lex) -> Tuple[MindSystem, LimboLayer]:
        from bone_village import MirrorGraph

        _mem = MycelialNetwork(events)
        limbo = LimboLayer()
        _mem.cleanup_old_sessions(limbo)
        lore = LoreManifest.get_instance()
        mind = MindSystem(
            mem=_mem,
            lex=lex,
            dreamer=DreamEngine(events, lore),
            mirror=MirrorGraph(events),
            tracer=ViralTracer(_mem),
        )
        return mind, limbo

    @staticmethod
    def _construct_bio(events, mind, lex) -> BioSystem:
        genesis_val = getattr(BoneConfig.METABOLISM, "GENESIS_VOLTAGE", 100.0)
        mito_state = MitochondrialState(atp_pool=genesis_val)
        start_health = getattr(BoneConfig, "MAX_HEALTH", 100.0)
        start_stamina = getattr(BoneConfig, "MAX_STAMINA", 100.0)
        bio_metrics = Biometrics(health=start_health, stamina=start_stamina)
        return BioSystem(
            mito=MitochondrialForge(mito_state, events),
            endo=EndocrineSystem(),
            immune=ImmuneMycelium(),
            lichen=BioLichen(),
            governor=MetabolicGovernor(),
            shimmer=ShimmerState(),
            parasite=BioParasite(mind.mem, lex),
            events=events,
            biometrics=bio_metrics,
        )

    @staticmethod
    def _construct_physics(events, bio, mind, lex) -> PhysSystem:
        from bone_village import TheCartographer

        gate = TheGatekeeper(lex, mind.mem)
        return PhysSystem(
            observer=QuantumObserver(events),
            forge=TheForge(),
            crucible=TheCrucible(),
            theremin=TheTheremin(),
            pulse=ThePacemaker(),
            nav=TheCartographer(bio.shimmer),
            gate=gate,
            tension=SurfaceTension(),
            dynamics=ZoneInertia(),  # [FULLER] Gravity restored!
        )

    @staticmethod
    def incubate(events, lex) -> SystemEmbryo:
        if hasattr(events, "set_dormancy"):
            events.set_dormancy(True)
        events.log(
            f"{Prisma.GRY}[ARCHITECT]: Laying foundations (Dormancy Active)...{Prisma.RST}",
            "SYS",
        )
        mind, limbo = BoneArchitect._construct_mind(events, lex)
        bio = BoneArchitect._construct_bio(events, mind, lex)
        physics = BoneArchitect._construct_physics(events, bio, mind, lex)
        return SystemEmbryo(
            mind=mind, limbo=limbo, bio=bio, physics=physics, shimmer=bio.shimmer
        )

    @staticmethod
    def awaken(embryo: SystemEmbryo) -> SystemEmbryo:
        events = embryo.bio.mito.events
        load_result = None
        try:
            if hasattr(embryo.mind.mem, "autoload_last_spore"):
                load_result = embryo.mind.mem.autoload_last_spore()
        except Exception as e:
            events.log(
                f"{Prisma.RED}[ARCHITECT]: Spore resurrection failed: {e}{Prisma.RST}",
                "CRIT",
            )
            load_result = None
        embryo.soul_legacy = {}
        embryo.continuity = None
        recovered_atlas = {}
        if isinstance(load_result, (list, tuple)) and load_result:
            padded_result = list(load_result) + [None] * (5 - len(load_result))
            mito_legacy, immune_legacy, soul_legacy, continuity, atlas = padded_result[:5]
            if mito_legacy and hasattr(embryo.bio.mito, "apply_inheritance"):
                embryo.bio.mito.apply_inheritance(mito_legacy)
            if immune_legacy and isinstance(immune_legacy, (list, set)) and hasattr(embryo.bio.immune, "load_antibodies"):
                embryo.bio.immune.load_antibodies(immune_legacy)
            if isinstance(soul_legacy, dict):
                embryo.soul_legacy = soul_legacy
            if isinstance(continuity, dict):
                embryo.continuity = continuity
            if isinstance(atlas, dict):
                recovered_atlas = atlas
        if recovered_atlas and hasattr(embryo.physics, "nav"):
            if hasattr(embryo.physics.nav, "import_atlas"):
                try:
                    embryo.physics.nav.import_atlas(recovered_atlas)
                    events.log(
                        f"{Prisma.MAG}[ARCHITECT]: World Map restored from Spore.{Prisma.RST}",
                        "SYS",
                    )
                except Exception as e:
                    events.log(
                        f"{Prisma.OCHRE}[ARCHITECT]: Atlas corrupt, discarding map: {e}{Prisma.RST}",
                        "WARN",
                    )
        if embryo.bio.mito.state.atp_pool <= 0.0:
            genesis_val = getattr(BoneConfig.METABOLISM, "GENESIS_VOLTAGE", 100.0)
            events.log(
                f"⚡ COLD BOOT: Injecting Genesis Spark ({genesis_val} ATP).", "SYS"
            )
            embryo.bio.mito.adjust_atp(genesis_val, reason="GENESIS")
        return embryo
