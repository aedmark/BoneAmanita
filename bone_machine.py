"""
bone_machine.py
"""

import random
from dataclasses import dataclass
from typing import Tuple, Optional, List, Dict, Any
from bone_body import BioSystem, MitochondrialState, Biometrics, MitochondrialForge, EndocrineSystem, MetabolicGovernor
from bone_brain import DreamEngine, ShimmerState
from bone_presets import BoneConfig
from bone_core import LoreManifest, ux
from bone_lexicon import LexiconService
from bone_physics import TheGatekeeper, QuantumObserver, SurfaceTension, ZoneInertia
from bone_protocols import LimboLayer
from bone_spores import MycelialNetwork, ImmuneMycelium, BioLichen, BioParasite
from bone_types import MindSystem, PhysSystem, PhysicsPacket, Prisma
from bone_village import MirrorGraph, TheCartographer

class TheCrucible:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        cfg = getattr(self.cfg, "MACHINE", None)
        self.max_voltage_cap = getattr(cfg, "CRUCIBLE_VOLTAGE_CAP", 20.0) if cfg else 20.0
        self.active_state = "COLD"
        self.dampener_charges = getattr(cfg, "CRUCIBLE_DAMPENER_CHARGES", 3) if cfg else 3
        self.dampener_tolerance = getattr(cfg, "DAMPENER_TOLERANCE", 15.0) if cfg else 15.0
        self.instability_index = 0.0
        self.logs = self._load_logs()

    def _load_logs(self):
        manifest = LoreManifest.get_instance(config_ref=self.cfg).get("narrative_data") or {}
        return manifest.get("CRUCIBLE_LOGS", {})

    def dampener_status(self):
        msg = ux("machine_strings", "crucible_dampener_status")
        return msg.format(charges=self.dampener_charges)

    def dampen(
            self, voltage_spike: float, stability_index: float) -> Tuple[bool, str, float]:
        if self.dampener_charges <= 0:
            return False, self.logs.get("DAMPER_EMPTY", ""), 0.0
        should_dampen = False
        reduction_factor = 0.0
        reason = ""
        if voltage_spike > self.dampener_tolerance:
            should_dampen = True
            reduction_factor = 0.7
            reason = ux("machine_strings", "dampen_reason_circuit") or "Circuit Breaker"
        elif voltage_spike > 8.0 and stability_index < 0.3:
            should_dampen = True
            reduction_factor = 0.4
            reason = ux("machine_strings", "dampen_reason_instability") or "Instability"
        if should_dampen:
            self.dampener_charges -= 1
            reduction = voltage_spike * reduction_factor
            msg = self.logs.get("DAMPER_HIT", "").format(reduction=reduction, reason=reason)
            return True, msg, reduction
        return False, self.logs.get("HOLDING", ""), 0.0

    def audit_fire(self, physics: Any) -> Tuple[str, float, Optional[str]]:
        voltage = getattr(physics, "voltage", 0.0) if not isinstance(physics, dict) else physics.get("voltage", 0.0)
        structure = getattr(physics, "kappa", 0.0) if not isinstance(physics, dict) else physics.get("kappa", 0.0)
        ideal_voltage = structure * 20.0
        delta = voltage - ideal_voltage
        self.instability_index = (self.instability_index * 0.7) + (delta * 0.3)
        if abs(self.instability_index) < 0.1:
            self.instability_index = 0.0
        current_drag = getattr(physics, "narrative_drag", 0.0) if not isinstance(physics, dict) else physics.get(
            "narrative_drag", 0.0)
        adjustment = self.instability_index * 0.5
        if current_drag < 1.0 and adjustment < 0:
            adjustment *= 0.1
        new_drag = max(0.0, min(10.0, current_drag + adjustment))
        if isinstance(physics, dict):
            physics["narrative_drag"] = round(new_drag, 2)
        else:
            setattr(physics, "narrative_drag", round(new_drag, 2))
        msg = None
        if abs(adjustment) > 0.1:
            dir_tight = ux("machine_strings", "crucible_tightening") or "TIGHTENING"
            dir_relax = ux("machine_strings", "crucible_relaxing") or "RELAXING"
            direction = dir_tight if adjustment > 0 else dir_relax
            msg = self.logs.get("REGULATOR", "").format(direction=direction, current=current_drag, new=new_drag)
        surge = getattr(physics, "system_surge_event", False) if not isinstance(physics, dict) else physics.get(
            "system_surge_event", False)
        if surge:
            self.active_state = "SURGE"
            return "SURGE", 0.0, self.logs.get("SURGE", "").format(voltage=voltage),
        if voltage > 18.0:
            if structure > 0.5:
                gain = voltage * 0.1
                self.max_voltage_cap += gain
                self.active_state = "RITUAL"
                return "RITUAL", gain, self.logs.get("RITUAL", "").format(gain=gain),
            else:
                damage = voltage * 0.5
                self.active_state = "MELTDOWN"
                return "MELTDOWN", damage, self.logs.get("MELTDOWN", "").format(damage=damage),
        self.active_state = "REGULATED"
        return "REGULATED", adjustment, msg

class TheParadoxEngine:
    def __init__(self, events_ref):
        self.events = events_ref
        self.beta_max: float = 0.0
        self.paradox_yield: int = 0
        self.is_active: bool = False

    def evaluate_tension(self, beta: float, stamina: float) -> bool:
        if beta >= 0.7 and stamina >= 30.0:
            self.beta_max = max(self.beta_max, beta)
            return True
        return False

    def ignite(self, recent_words: List[str]) -> Tuple[float, str]:
        self.is_active = True
        valid_seeds = [w for w in recent_words if len(w) > 4]
        seed = random.choice(valid_seeds) if valid_seeds else "the architecture"
        pressure = 0.4 + (random.random() * 0.6)
        templates = [f"What if '{seed}' and its exact opposite were both non-negotiable truths? Do not resolve the contradiction. Do not compromise. Build the structure that can hold both simultaneously.",
            f"[RECURSIVE PARADOX] Apply the concept of '{seed}' to the architecture of this very conversation. How does the act of thinking about '{seed}' alter the physical constraints of our dialogue? Both are non-negotiable truths.",
            f"[NEGATIVE SPACE] Define '{seed}' entirely by what it is not. Construct the boundary of the concept without ever naming the center. Both the center and the void are non-negotiable truths."]
        return pressure, random.choice(templates)

    def disengage(self):
        self.is_active = False

class TheForge:
    def __init__(self, lex_ref=None):
        self.lex = lex_ref
        gordon_data = LoreManifest.get_instance().get("GORDON") or {}
        raw_recipes = gordon_data.get("RECIPES", [])
        self.recipe_map = {}
        for r in raw_recipes:
            ing = r.get("ingredient")
            if ing:
                if ing not in self.recipe_map:
                    self.recipe_map[ing] = []
                self.recipe_map[ing].append(r)

    @staticmethod
    def hammer_alloy(physics: Any) -> Tuple[bool, Optional[str], Optional[str]]:
        counts = getattr(physics, "counts", {}) if not isinstance(physics, dict) else physics.get("counts", {})
        clean_words = getattr(physics, "clean_words", []) if not isinstance(physics, dict) else physics.get(
            "clean_words", [])
        if not clean_words:
            return False, None, None
        heavy = counts.get("heavy", 0)
        kinetic = counts.get("kinetic", 0)
        avg_density = ((heavy * 2.0) + (kinetic * 0.5)) / len(clean_words)
        voltage = getattr(physics, "voltage", 0.0) if not isinstance(physics, dict) else physics.get("voltage", 0.0)
        if random.random() >= (voltage / 20.0) * avg_density:
            return False, None, None
        if heavy > 3:
            msg = ux("machine_strings", "forge_lead_boots")
            return True, msg.format(avg_density=avg_density), "LEAD_BOOTS"
        if kinetic > 3:
            return (
                True,
                ux("machine_strings", "forge_safety_scissors"), "SAFETY_SCISSORS")
        return True, ux("machine_strings", "forge_anchor_stone"), "ANCHOR_STONE"

    def attempt_crafting(
            self, physics: Any, inventory_list: List[str]) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        if not inventory_list:
            return False, None, None, None
        clean_words = getattr(physics, "clean_words", []) if not isinstance(physics, dict) else physics.get("clean_words", [])
        if not clean_words:
            return False, None, None, None
        clean_set = set(clean_words)
        voltage = float(getattr(physics, "voltage", 0.0) if not isinstance(physics, dict) else physics.get("voltage", 0.0))
        for item in inventory_list:
            if item in self.recipe_map:
                for recipe in self.recipe_map[item]:
                    cat_words = self.lex.get(recipe["catalyst_category"]) if self.lex else LexiconService().get(
                        recipe["catalyst_category"])
                    if not cat_words or clean_set.isdisjoint(cat_words):
                        continue
                    hits = len(clean_set.intersection(cat_words))
                    entanglement = self._calculate_entanglement(hits, voltage)
                    if random.random() < entanglement:
                        msg = ux("machine_strings", "forge_alchemy_success")
                        return True, msg.format(result=recipe["result"], item=item), item, recipe["result"],
                    else:
                        msg = ux("machine_strings", "forge_alchemy_fail")
                        return False, msg.format(entanglement=int(entanglement * 100)), None, None,
        return False, None, None, None

    @staticmethod
    def _calculate_entanglement(hit_count: int, voltage: float) -> float:
        return min(1.0, 0.2 + (hit_count * 0.1) + (voltage / 133.0))

    @staticmethod
    def transmute(physics: Any) -> Optional[str]:
        counts = getattr(physics, "counts", {}) if not isinstance(physics, dict) else physics.get("counts", {})
        voltage = float(
            getattr(physics, "voltage", 0.0) if not isinstance(physics, dict) else physics.get("voltage", 0.0))
        gamma = float(getattr(physics, "gamma", 0.0) if not isinstance(physics, dict) else physics.get("gamma", 0.0))
        if gamma < 0.15 and counts.get("abstract", 0) > 1:
            return ux("machine_strings", "forge_emulsion_fail")
        if voltage > 15.0:
            msg = ux("machine_strings", "forge_overheat")
            return msg.format(voltage=voltage)
        return None

class TheTheremin:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.decoherence_buildup = 0.0
        self.classical_turns = 0
        cfg = getattr(self.cfg, "MACHINE", None)
        self.AMBER_THRESHOLD = getattr(cfg, "THEREMIN_AMBER_THRESHOLD", 20.0) if cfg else 20.0
        self.SHATTER_POINT = getattr(cfg, "THEREMIN_SHATTER_POINT", 100.0) if cfg else 100.0
        self.is_stuck = False
        self.logs = self._load_logs()

    def _load_logs(self):
        manifest = LoreManifest.get_instance(config_ref=self.cfg).get("narrative_data") or {}
        return manifest.get("THEREMIN_LOGS", {})

    def listen(
            self, physics: Any, governor_mode="COURTYARD") -> Tuple[bool, float, Optional[str], Optional[str]]:
        counts = getattr(physics, "counts", {}) if not isinstance(physics, dict) else physics.get("counts", {})
        voltage = float(getattr(physics, "voltage", 0.0) if not isinstance(physics, dict) else physics.get("voltage", 0.0))
        turb = float(getattr(physics, "turbulence", 0.0) if not isinstance(physics, dict) else physics.get("turbulence", 0.0))
        rep = float(getattr(physics, "repetition", 0.0) if not isinstance(physics, dict) else physics.get("repetition", 0.0))
        complexity = float(getattr(physics, "truth_ratio", 0.0) if not isinstance(physics, dict) else physics.get("truth_ratio", 0.0))
        ancient_mass = counts.get("heavy", 0) + counts.get("thermal", 0) + counts.get("cryo", 0)
        modern_mass = counts.get("abstract", 0)
        raw_mix = min(ancient_mass, modern_mass)
        resin_flow = raw_mix * 2.0
        if governor_mode == "LABORATORY":
            resin_flow *= 0.5
        if voltage > 5.0:
            resin_flow = max(0.0, resin_flow - (voltage * 0.6))
        thermal_hits = counts.get("thermal", 0)
        theremin_msg = ""
        cfg = getattr(self.cfg, "MACHINE", None)
        melt_thresh = getattr(cfg, "THEREMIN_MELT_THRESHOLD", 5.0) if cfg else 5.0
        critical_event = None
        if thermal_hits > 0 and self.decoherence_buildup > melt_thresh:
            dissolved = thermal_hits * 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - dissolved)
            self.classical_turns = 0
            theremin_msg = self.logs.get("MELT", "").format(val=dissolved)
        if rep > 0.5:
            self.classical_turns += 1
            slag = self.classical_turns * 2.0
            self.decoherence_buildup += slag
            theremin_msg = self.logs.get("CALCIFY", "").format(turns=self.classical_turns, val=slag)
        elif complexity > 0.4 and self.classical_turns > 0:
            self.classical_turns = 0
            relief = 15.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - relief)
            theremin_msg = self.logs.get("SHATTER", "").format(val=relief)
        elif resin_flow > 0.5:
            self.decoherence_buildup += resin_flow
            theremin_msg = self.logs.get("RESIN", "").format(val=resin_flow)
        if turb > 0.6 and self.decoherence_buildup > 0:
            shatter_amt = turb * 10.0
            self.decoherence_buildup = max(0.0, self.decoherence_buildup - shatter_amt)
            theremin_msg = self.logs.get("TURBULENCE", "").format(val=shatter_amt)
            self.classical_turns = 0
        if turb < 0.2:
            current_drag = float(
                getattr(physics, "narrative_drag", 0.0) if not isinstance(physics, dict) else physics.get(
                    "narrative_drag", 0.0))
            if isinstance(physics, dict):
                physics["narrative_drag"] = max(0.0, current_drag - 1.0)
            else:
                setattr(physics, "narrative_drag", max(0.0, current_drag - 1.0))
        if self.decoherence_buildup > self.SHATTER_POINT:
            self.decoherence_buildup = 0.0
            self.classical_turns = 0
            self.is_stuck = False
            current_drag = getattr(physics, "narrative_drag", 0.0) if not isinstance(physics, dict) else physics.get(
                "narrative_drag", 0.0)
            if isinstance(physics, dict):
                physics["narrative_drag"] = max(current_drag + 20.0, 20.0)
                physics["voltage"] = 0.0
            else:
                setattr(physics, "narrative_drag", max(current_drag + 20.0, 20.0))
                setattr(physics, "voltage", 0.0)
            return False, resin_flow, self.logs.get("COLLAPSE", ""), "AIRSTRIKE",
        if self.classical_turns > 3:
            critical_event = "CORROSION"
            theremin_msg = f"{theremin_msg or ''}{ux('machine_strings', 'theremin_corrosion') or ''}"
        if self.decoherence_buildup > self.AMBER_THRESHOLD:
            self.is_stuck = True
            theremin_msg = f"{theremin_msg or ''}{ux('machine_strings', 'theremin_stuck') or ''}"
        elif self.is_stuck and self.decoherence_buildup < 5.0:
            self.is_stuck = False
            theremin_msg = f"{theremin_msg or ''}{ux('machine_strings', 'theremin_free') or ''}"
        return self.is_stuck, resin_flow, theremin_msg, critical_event

    def get_readout(self):
        status = "STUCK" if self.is_stuck else "FLOW"
        msg = ux("machine_strings", "theremin_readout")
        return msg.format(resin=self.decoherence_buildup, status=status)

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
        safe_packet.vector = {k: 0.0 for k in ["STR", "VEL", "PSI", "ENT", "PHI", "BET", "DEL", "LAMBDA", "CHI"]}
        default_words = ["white", "room", "safe", "mode"]
        manifest_words = ux("machine_strings", "panic_clean_words")
        safe_packet.clean_words = manifest_words if isinstance(manifest_words, list) else default_words
        safe_packet.raw_text = ux("machine_strings", "panic_physics_text")
        safe_packet.flow_state = ux("machine_strings", "panic_flow_state") or "SAFE_MODE"
        safe_packet.zone = ux("machine_strings", "panic_zone") or "PANIC_ROOM"
        safe_packet.manifold = ux("machine_strings", "panic_manifold") or "WHITE_ROOM"
        return safe_packet

    @staticmethod
    def get_safe_bio(previous_state=None):
        log_msg = ux("machine_strings", "panic_bio_log")
        resp_fallback = ux("machine_strings", "panic_resp_fallback") or "NECROSIS"
        enz_fallback = ux("machine_strings", "panic_enz_fallback") or "NONE"
        chem_state: Dict[str, float] = {"DOP": 0.0, "COR": 0.0, "OXY": 0.0, "SER": 0.0, "ADR": 0.0, "MEL": 0.0, }
        base: Dict[str, Any] = {"is_alive": True, "atp": 10.0, "respiration": resp_fallback, "enzyme": enz_fallback,
                                "chem": chem_state, "logs": [f"{Prisma.RED}{log_msg}{Prisma.RST}"], }
        state = previous_state or {}
        if isinstance(state, dict):
            if old_chem := state.get("chemistry", {}):
                chem_state["COR"] = 0.0
                chem_state["ADR"] = 0.0
                chem_state["SER"] = max(0.2, float(old_chem.get("SER", 0.0)))
        return base

    @staticmethod
    def get_safe_mind():
        return {"lens": "GORDON", "role": "Panic Room Overseer", "thought": ux(
            "machine_strings", "panic_mind_thought"), }

    @staticmethod
    def get_safe_soul():
        default_soul = {"name": "Traveler", "archetype": "The Survivor", "virtues": {"resilience": 1.0},
                        "vices": {"amnesia": 1.0}, "narrative_arc": "RECOVERY", "xp": 0, }
        return ux("machine_strings", "panic_soul") or default_soul

    @staticmethod
    def get_safe_limbo():
        default_limbo = {"mood": "NEUTRAL", "volatility": 0.0, "mask": "DEFAULT", "glitch_factor": 0.0, }
        return ux("machine_strings", "panic_limbo") or default_limbo

class ViralTracer:
    def __init__(self, memory_ref):
        self.memory = memory_ref
        self.active_loops = []

    def inject(self, start_node: str) -> Optional[List[str]]:
        if random.random() < 0.05:
            loop = [start_node, "echo", "void", start_node]
            self.active_loops.append(loop)
            return loop
        return None

    def psilocybin_rewire(self, loop_path: List[str]) -> str:
        msg = ux("machine_strings", "tracer_rewire")
        if loop_path in self.active_loops:
            self.active_loops.remove(loop_path)
        return msg.format(path="->".join(loop_path))

class ThePacemaker:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.boredom_level = 0.0
        self.heart_rate = 60
        self.BOREDOM_THRESHOLD = getattr(self.cfg, "BOREDOM_THRESHOLD", 10.0)

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
    def _construct_mind(events, lex, config_ref=None) -> Tuple[MindSystem, LimboLayer]:
        target_cfg = config_ref or BoneConfig
        _mem = MycelialNetwork(events)
        limbo = LimboLayer(config_ref=target_cfg)
        _mem.cleanup_old_sessions(limbo)
        lore = LoreManifest.get_instance(config_ref=target_cfg)
        mind = MindSystem(mem=_mem, lex=lex, dreamer=DreamEngine(events, lore, config_ref=target_cfg), mirror=MirrorGraph(events, config_ref=target_cfg),
                          tracer=ViralTracer(_mem), )
        return mind, limbo

    @staticmethod
    def _construct_bio(events, mind, lex, config_ref=None) -> BioSystem:
        target_cfg = config_ref or BoneConfig
        cfg = getattr(target_cfg, "METABOLISM", None)
        genesis_val = getattr(cfg, "GENESIS_VOLTAGE", 100.0) if cfg else 100.0
        mito_state = MitochondrialState(atp_pool=genesis_val)
        start_health = getattr(target_cfg, "MAX_HEALTH", 100.0)
        start_stamina = getattr(target_cfg, "MAX_STAMINA", 100.0)
        bio_metrics = Biometrics(health=start_health, stamina=start_stamina)
        return BioSystem(mito=MitochondrialForge(mito_state, events, config_ref=target_cfg), endo=EndocrineSystem(config_ref=target_cfg), immune=ImmuneMycelium(),
                         lichen=BioLichen(), governor=MetabolicGovernor(config_ref=target_cfg), shimmer=ShimmerState(),
                         parasite=BioParasite(mind.mem, lex), events=events, biometrics=bio_metrics, config_ref=target_cfg)

    @staticmethod
    def _construct_physics(events, bio, mind, lex, config_ref=None) -> PhysSystem:
        target_cfg = config_ref or BoneConfig
        gate = TheGatekeeper(lex, mind.mem, config_ref=target_cfg)
        return PhysSystem(observer=QuantumObserver(events, lex, config_ref=target_cfg),
                          forge=TheForge(lex_ref=lex),
                          crucible=TheCrucible(config_ref=target_cfg),
                          theremin=TheTheremin(config_ref=target_cfg), pulse=ThePacemaker(config_ref=target_cfg),
                          nav=TheCartographer(bio.shimmer, config_ref=target_cfg), gate=gate,
                          tension=SurfaceTension(), dynamics=ZoneInertia(config_ref=target_cfg), )

    @staticmethod
    def incubate(events, lex, config_ref=None) -> SystemEmbryo:
        target_cfg = config_ref or BoneConfig
        if hasattr(events, "set_dormancy"):
            events.set_dormancy(True)
        msg = ux("machine_strings", "arch_incubate")
        events.log(f"{Prisma.GRY}{msg}{Prisma.RST}", "SYS", )
        mind, limbo = BoneArchitect._construct_mind(events, lex, config_ref=target_cfg)
        bio = BoneArchitect._construct_bio(events, mind, lex, config_ref=target_cfg)
        physics = BoneArchitect._construct_physics(events, bio, mind, lex, config_ref=target_cfg)
        return SystemEmbryo(mind=mind, limbo=limbo, bio=bio, physics=physics, shimmer=bio.shimmer)

    @staticmethod
    def awaken(embryo: SystemEmbryo) -> SystemEmbryo:
        events = embryo.bio.mito.events
        load_result = None
        try:
            if hasattr(embryo.mind.mem, "autoload_last_spore"):
                load_result = embryo.mind.mem.autoload_last_spore()
        except Exception as e:
            msg = ux("machine_strings", "arch_spore_fail") 
            events.log(f"{Prisma.RED}{msg.format(e=e)}{Prisma.RST}", "CRIT", )
            load_result = None
        embryo.soul_legacy = {}
        embryo.continuity = None
        recovered_atlas = {}
        if isinstance(load_result, (list, tuple)) and load_result:
            padded_result = list(load_result) + [None] * (5 - len(load_result))
            mito_legacy, immune_legacy, soul_legacy, continuity, atlas = padded_result[:5]
            if mito_legacy and hasattr(embryo.bio.mito, "apply_inheritance"):
                embryo.bio.mito.apply_inheritance(mito_legacy)
            if (immune_legacy
                    and isinstance(immune_legacy, (list, set))
                    and hasattr(embryo.bio.immune, "load_antibodies")):
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
                    msg = ux("machine_strings", "arch_map_restored")
                    events.log(f"{Prisma.MAG}{msg}{Prisma.RST}", "SYS", )
                except Exception as e:
                    msg = ux("machine_strings", "arch_map_corrupt")
                    events.log(f"{Prisma.OCHRE}{msg.format(e=e)}{Prisma.RST}", "WARN", )
        if embryo.bio and embryo.bio.mito and embryo.bio.mito.state.atp_pool <= 0.0:
            target_cfg = getattr(embryo.bio, "config_ref", None) or BoneConfig
            cfg = getattr(target_cfg, "METABOLISM", None)
            genesis_val = getattr(cfg, "GENESIS_VOLTAGE", 100.0) if cfg else 100.0
            msg = ux("machine_strings", "arch_cold_boot")
            events.log(msg.format(genesis_val=genesis_val) if msg else f"Cold Boot: {genesis_val} ATP", "SYS")
            embryo.bio.mito.adjust_atp(genesis_val, reason="GENESIS")
        return embryo