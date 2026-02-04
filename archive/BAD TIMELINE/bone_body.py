""" bone_body.py """

import math, random, time
from collections import deque, Counter
from dataclasses import dataclass, field
from typing import Set, Optional, Dict, List, Any, Tuple
from bone_personality import SynergeticLensArbiter
from bone_lexicon import TheLexicon
from bone_bus import Prisma, BoneConfig
from bone_data import BIO_NARRATIVE

@dataclass
class Biometrics:
    health: float
    stamina: float
    stress_modifier: float = 1.0
    circadian_bias: Optional[Dict[str, float]] = None

@dataclass
class MetabolicReceipt:
    base_cost: float
    drag_tax: float
    inefficiency_tax: float
    total_burn: float
    status: str
    symptom: str = "Nominal"

@dataclass
class SemanticSignal:
    novelty: float = 0.0
    resonance: float = 0.0
    valence: float = 0.0
    coherence: float = 0.0

class BioConstants:
    ROS_SIGNAL = 3.0
    ROS_DAMAGE = 8.0
    ROS_PURGE = 12.0
    ATP_CRITICAL = 20.0
    ATP_COLLAPSE = 0.0
    SHORT_WORD_LEN = 4
    LONG_WORD_LEN = 7
    BASE_ATP_YIELD = 1.0
    LONG_WORD_BONUS = 2.0
    VOLTAGE_BONUS_THRESHOLD = 8.0
    PROTEASE_BONUS = 5.0
    DOPAMINE_SATIETY = 0.7
    CORTISOL_STRESS = 0.6
    ADRENALINE_SURGE = 0.6

@dataclass
class BioSystem:
    mito: 'MitochondrialForge'
    endo: 'EndocrineSystem'
    plasticity: Any
    governor: 'MetabolicGovernor'
    shimmer: Any
    events: Any = None
    biometrics: Optional['Biometrics'] = None

    def apply_environmental_entropy(self, physics_packet):
        base_entropy = 2.0
        if isinstance(physics_packet, dict):
            em_field = physics_packet.get("electromagnetism", 0.0)
            if em_field == 0.0:
                e = physics_packet.get("E", 0.0)
                b = physics_packet.get("B", 0.0)
                em_field = math.sqrt(e**2 + b**2)
        else:
            em_field = getattr(physics_packet, "electromagnetism", 0.0)
        shield_strength = min(0.8, em_field * 0.1)
        effective_entropy = base_entropy * (1.0 - shield_strength)
        thermal_feedback = 0.0
        if em_field > 8.0:
            thermal_feedback = (em_field - 8.0) * 1.5
            if self.events:
                self.events.log(f"{Prisma.RED}⚠ INDUCTIVE HEATING: The air is ionizing around you.{Prisma.RST}", "BIO_WARN")
        total_drain = effective_entropy + thermal_feedback
        if self.biometrics:
            self.biometrics.health = max(0.0, self.biometrics.health - total_drain)
        if shield_strength > 0.2 and self.events:
            self.events.log(f"{Prisma.CYN}🛡️ EM SHIELD ACTIVE: Mitigation {int(shield_strength*100)}%{Prisma.RST}", "PHYS")

@dataclass
class MitochondrialState:
    atp_pool: float = 60.0
    membrane_potential: float = 1.0
    ros_buildup: float = 0.0
    mother_hash: str = "EVE"
    retrograde_signal: str = "QUIET"

    @property
    def efficiency_mod(self) -> float:
        return self.membrane_potential

class MitochondrialForge:
    ROS_THRESHOLD_SIGNAL = 3.0
    ROS_THRESHOLD_DAMAGE = 8.0
    ROS_THRESHOLD_PURGE = 12.0

    def __init__(self, state_ref: MitochondrialState, events_ref):
        self.state = state_ref
        self.events = events_ref

    def adjust_atp(self, delta: float, reason: str = ""):
        old = self.state.atp_pool
        max_limit = getattr(BoneConfig, "MAX_ATP", 100.0)
        self.state.atp_pool = max(BioConstants.ATP_COLLAPSE, min(max_limit, old + delta))
        if reason and abs(delta) > 5.0:
            self.events.log(f"[ATP]: {reason} ({delta:+.1f})", "BIO")

    def process_cycle(self, physics_packet: dict, external_modifiers: List[float] = None) -> MetabolicReceipt:
        voltage = physics_packet.get("voltage", 0.0)
        drag = physics_packet.get("narrative_drag", 0.0)
        base_demand = max(0.1, voltage * 0.4)
        cognitive_load_tax = (drag ** 1.5) * 0.5
        mod_factor = 1.0
        if external_modifiers:
            for m in external_modifiers:
                mod_factor *= m
        efficiency = max(0.1, self.state.membrane_potential)
        total_metabolic_cost = ((base_demand + cognitive_load_tax) * mod_factor) / efficiency
        waste_generated = total_metabolic_cost * (1.0 - efficiency) * 0.5
        self.state.ros_buildup += waste_generated
        self.adjust_atp(-total_metabolic_cost, "Metabolic Burn")
        self._apply_adaptive_dynamics(waste_generated)
        status = "RESPIRING"
        if self.state.atp_pool < BioConstants.ATP_CRITICAL: status = "LOW_POWER"
        if self.state.atp_pool <= BioConstants.ATP_COLLAPSE: status = "NECROSIS"
        return MetabolicReceipt(
            base_cost=round(base_demand, 2),
            drag_tax=round(cognitive_load_tax, 2),
            inefficiency_tax=round(total_metabolic_cost - (base_demand + cognitive_load_tax), 2),
            total_burn=round(total_metabolic_cost, 2),
            status=status,
            symptom=self.state.retrograde_signal)

    def _apply_adaptive_dynamics(self, current_waste):
        if self.state.ros_buildup < BioConstants.ROS_SIGNAL:
            self.state.membrane_potential = max(0.5, self.state.membrane_potential - 0.001)
            self.state.retrograde_signal = "QUIET"
        elif self.state.ros_buildup < BioConstants.ROS_DAMAGE:
            self.state.membrane_potential = min(1.0, self.state.membrane_potential + 0.005)
            self.state.retrograde_signal = "MITOHORMESIS_ACTIVE"
            self.state.ros_buildup = max(0.0, self.state.ros_buildup - 0.5)
        else:
            self.state.membrane_potential -= 0.02
            self.state.retrograde_signal = "OXIDATIVE_STRESS"

        if self.state.ros_buildup > BioConstants.ROS_PURGE:
            self._trigger_mitophagy()

    def adapt(self, stress_level: float):
        old_potential = self.state.membrane_potential
        if stress_level > 5.0:
            self.state.membrane_potential = max(0.4, self.state.membrane_potential - 0.15)
            self.events.log(
                f"{Prisma.RED}[MITO]: Trauma Adaptive Response (Stress {stress_level:.1f}). "
                f"Efficiency dropped ({old_potential:.2f} -> {self.state.membrane_potential:.2f}).{Prisma.RST}",
                "BIO")
        elif stress_level > 1.0:
            self.state.membrane_potential = min(1.5, self.state.membrane_potential + 0.05)
            if random.random() < 0.2:
                self.events.log(
                    f"{Prisma.GRN}[MITO]: Hormetic Adaptation. System hardening.{Prisma.RST}",
                    "BIO")

    def _trigger_mitophagy(self):
        self.adjust_atp(-30.0, "Mitophagy")
        self.state.ros_buildup = 0.0
        self.state.membrane_potential = 0.6
        self.state.retrograde_signal = "MITOPHAGY_RESET"
        self.events.log(f"{Prisma.RED}[MITO]: CRITICAL WASTE LEVELS. Purging organelles.{Prisma.RST}", "BIO")

    def _print_receipt(self, base, tax, total) -> MetabolicReceipt:
        status = "NOMINAL"
        if self.state.atp_pool < 20.0: status = "LOW_POWER"
        if self.state.atp_pool <= 0.0: status = "METABOLIC_COLLAPSE"

        return MetabolicReceipt(
            base_cost=round(base, 2),
            drag_tax=round(tax, 2),
            inefficiency_tax=round(total - (base + tax), 2),
            total_burn=round(total, 2),
            status=status,
            symptom=self.state.retrograde_signal)

    def apply_inheritance(self, traits: dict):
        if traits.get("high_metabolism"):
            self.state.membrane_potential = 1.1

class SemanticEndocrinologist:
    def __init__(self, memory_ref, lexicon_ref):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.last_topics = deque(maxlen=3)

    def assess(self, clean_words: List[str], physics: Dict) -> SemanticSignal:
        if not clean_words:
            return SemanticSignal()
        cortical_set = set(self.mem.cortical_stack)
        novel_count = sum(1 for w in clean_words if len(w) > 4 and w not in cortical_set)
        novelty_score = min(1.0, novel_count / max(1, len(clean_words)))
        resonance_score = 0.0
        if self.mem.graph:
            hits = sum(1 for w in clean_words if w in self.mem.graph)
            resonance_score = min(1.0, hits / max(1, len(clean_words)))
        valence_score = self.lex.get_valence(clean_words)
        coherence_score = physics.get("kappa", 0.5)
        return SemanticSignal(
            novelty=novelty_score,
            resonance=resonance_score,
            valence=valence_score,
            coherence=coherence_score)

class SomaticLoop:
    _ENZYME_MAP = {
        "kinetic": "PROTEASE",
        "static": "CELLULASE",
        "abstract": "DECRYPTASE",
        "natural": "LIGNASE",
        "synthetic": "CHITINASE",
        "social": "AMYLASE",
        "antigen": "OXIDASE"}

    def __init__(self, bio_system_ref: BioSystem, memory_ref=None, lexicon_ref=None, gordon_ref=None, folly_ref=None, events_ref=None):
        self.bio = bio_system_ref
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.gordon = gordon_ref
        self.folly = folly_ref
        self.events = events_ref
        self.semantic_doctor = SemanticEndocrinologist(memory_ref, lexicon_ref)
        self.enzyme_map = getattr(BoneConfig.BIO, "ENZYME_MAP", SomaticLoop._ENZYME_MAP) if hasattr(BoneConfig, "BIO") else SomaticLoop._ENZYME_MAP

    def digest_cycle(self, text: str, physics_data: Any, feedback: Dict,
                     health: float, stamina: float, stress_modifier: float,
                     tick_count: int = 0, circadian_bias: Dict = None) -> Dict:
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        health = max(0.0, min(100.0, health))
        stamina = max(0.0, min(100.0, stamina))
        phys = self._normalize_physics(physics_data)
        logs = []
        if hasattr(self.bio, "apply_environmental_entropy"):
             self.bio.apply_environmental_entropy(phys)
        modifiers = self._gather_hormonal_modifiers(phys, logs)
        receipt = self.bio.mito.process_cycle(phys, external_modifiers=modifiers)
        resp_status = receipt.status
        if self._audit_folly_desire(phys, stamina, logs) == "MAUSOLEUM_CLAMP":
            return self._package_result(resp_status, logs, enzyme="NONE")
        enzyme, total_yield = self._harvest_resources(phys, logs)
        self.bio.mito.adjust_atp(total_yield, "Digestion Yield")
        self._perform_maintenance(text, phys, logs, tick_count)
        clean_words = phys.get("clean_words", [])
        semantic_sig = self.semantic_doctor.assess(clean_words, phys)
        chem_state = self.bio.endo.metabolize(
            feedback, health, stamina,
            self.bio.mito.state.ros_buildup,
            harvest_hits=self._count_harvest_hits(phys),
            stress_mod=stress_modifier,
            enzyme_type=enzyme,
            circadian_bias=circadian_bias,
            semantic_signal=semantic_sig)
        return self._package_result(resp_status, logs, chem_state, enzyme)

    def _gather_hormonal_modifiers(self, phys, logs) -> List[float]:
        chem = self.bio.endo
        modifiers = []
        if chem.cortisol > 0.5:
            stress_tax = 1.0 + (chem.cortisol * 0.5)
            modifiers.append(stress_tax)
            if random.random() < 0.3:
                logs.append(f"{Prisma.RED}[BIO]: Cortisol spiking. Metabolism inefficient (x{stress_tax:.2f}).{Prisma.RST}")
        if chem.adrenaline > 0.6:
            modifiers.append(0.5)
            logs.append(f"{Prisma.YEL}[BIO]: Adrenaline Surge. Pain ignored.{Prisma.RST}")
        if chem.dopamine > 0.7:
            modifiers.append(0.8)
        voltage = phys.get("voltage", 0.0)
        if voltage > 15.0:
            modifiers.append(1.2)
            logs.append(f"{Prisma.MAG}[BIO]: Voltage Gap ({voltage:.1f}v). Wires heating up.{Prisma.RST}")
        return modifiers

    @staticmethod
    def _normalize_physics(physics_packet: Any) -> Dict:
        voltage = 0.0
        drag = 0.0
        kappa = 0.5
        clean_words = []
        counts = {}
        if hasattr(physics_packet, "to_dict"):
            data = physics_packet.to_dict()
            voltage = data.get("voltage", 0.0)
            drag = data.get("narrative_drag", 0.0)
            kappa = data.get("kappa", 0.5)
            clean_words = data.get("clean_words", [])
            counts = data.get("counts", {})
        elif hasattr(physics_packet, "dimensions"):
            voltage = getattr(physics_packet, "tension", 0.0)
            drag = getattr(physics_packet, "compression", 0.0)
            kappa = getattr(physics_packet, "coherence", 0.5)
        elif isinstance(physics_packet, dict):
            voltage = physics_packet.get("voltage", 0.0)
            drag = physics_packet.get("narrative_drag", physics_packet.get("drag", 0.0))
            kappa = physics_packet.get("kappa", 0.5)
            clean_words = physics_packet.get("clean_words", [])
            counts = physics_packet.get("counts", {})
        return {
            "voltage": voltage,
            "drag": drag,
            "narrative_drag": drag,
            "kappa": kappa,
            "clean_words": clean_words,
            "counts": counts}

    @staticmethod
    def _audit_folly_desire(phys, stamina, logs) -> str:
        voltage = phys.get("voltage", 0.0)
        if stamina <= 0:
            logs.append(BIO_NARRATIVE["TAX"]["EXHAUSTION"].format(color=Prisma.RED, reset=Prisma.RST))
            return "MAUSOLEUM_CLAMP"
        if voltage > 30.0:
            logs.append(f"{Prisma.RED}CRITICAL: Voltage Overload ({voltage:.1f}v). System clamping.{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"
        return "CLEAR"

    def _harvest_resources(self, phys: Dict, logs: List[str]) -> Tuple[str, float]:
        clean_words = phys.get("clean_words", [])
        if not clean_words:
            return "NONE", 0.0
        found_enzymes = []
        total_atp_yield = 1.0
        word_counts = Counter(clean_words)
        for word, count in word_counts.items():
            if len(word) < 4: continue
            category = TheLexicon.get_current_category(word)
            if category and category != "void":
                enzyme = self._map_category_to_enzyme(category)
                found_enzymes.append(enzyme)
                base_word_yield = 2.0 if len(word) > 7 else 1.0
                damped_multiplier = 1.0 + math.log(count)
                total_atp_yield += (base_word_yield * damped_multiplier)
                if len(found_enzymes) <= 3:
                    logs.append(f"{Prisma.GRN}[BIO]: Digested '{word}' (x{count}) -> {enzyme} (+{(base_word_yield * damped_multiplier):.1f} ATP){Prisma.RST}")
        if phys.get("voltage", 0.0) > 8.0 and found_enzymes:
            found_enzymes.append("PROTEASE")
            total_atp_yield += 5.0
        if not found_enzymes:
            return "NONE", total_atp_yield
        dominant_enzyme = Counter(found_enzymes).most_common(1)[0][0]
        return dominant_enzyme, total_atp_yield

    def _map_category_to_enzyme(self, category: str) -> str:
        return self.enzyme_map.get(category, "AMYLASE")

    @staticmethod
    def _perform_maintenance(text: str, phys: Dict, logs: List[str], tick: int):
        if len(text) > 1000:
            logs.append(f"{Prisma.GRY}[MAINTENANCE]: Large input buffer detected. Flushed.{Prisma.RST}")
        drag = phys.get("narrative_drag", 0.0)
        if drag > 8.0 and tick % 10 == 0:
            logs.append(f"{Prisma.OCHRE}[MAINTENANCE]: Clearing sludge from intake valves (Drag {drag:.1f}).{Prisma.RST}")

    @staticmethod
    def _count_harvest_hits(phys: Dict) -> int:
        clean_words = phys.get("clean_words", [])
        return len([w for w in clean_words if len(w) >= 4])

    def _package_result(self, resp_status, logs, chem_state=None, enzyme="NONE"):
        is_alive = (resp_status == "RESPIRING")
        current_atp = self.bio.mito.state.atp_pool
        return {
            "respiration": resp_status,
            "is_alive": is_alive,
            "logs": logs,
            "chemistry": chem_state or {},
            "enzyme": enzyme,
            "atp": current_atp}

@dataclass
class EndocrineSystem:
    dopamine: float = 0.5
    oxytocin: float = 0.1
    cortisol: float = 0.0
    serotonin: float = 0.5
    adrenaline: float = 0.0
    melatonin: float = 0.0
    glimmers: int = 0
    _REACTION_MAP = {
        "PROTEASE":   {"ADR": BoneConfig.BIO.REWARD_MEDIUM},
        "CELLULASE":  {"COR": -BoneConfig.BIO.REWARD_MEDIUM, "OXY": BoneConfig.BIO.REWARD_SMALL},
        "CHITINASE":  {"DOP": BoneConfig.BIO.REWARD_LARGE},
        "LIGNASE":    {"SER": BoneConfig.BIO.REWARD_MEDIUM},
        "DECRYPTASE": {"ADR": BoneConfig.BIO.REWARD_SMALL, "DOP": BoneConfig.BIO.REWARD_SMALL},
        "AMYLASE":    {"SER": BoneConfig.BIO.REWARD_LARGE, "OXY": BoneConfig.BIO.REWARD_MEDIUM}}

    @staticmethod
    def _clamp(val: float) -> float:
        return max(0.0, min(1.0, val))

    @staticmethod
    def calculate_circadian_bias() -> Tuple[Dict[str, float], Optional[str]]:
        hour = time.localtime().tm_hour
        bias = {"COR": 0.0, "SER": 0.0, "MEL": 0.0}
        if 6 <= hour < 10:
            bias["COR"] = 0.1
            msg = BIO_NARRATIVE["CIRCADIAN"]["DAWN"]
        elif 10 <= hour < 18:
            bias["SER"] = 0.1
            msg = BIO_NARRATIVE["CIRCADIAN"]["SOLAR"]
        elif 18 <= hour < 23:
            bias["MEL"] = 0.1
            msg = BIO_NARRATIVE["CIRCADIAN"]["TWILIGHT"]
        else:
            bias["MEL"] = 0.3
            bias["COR"] = -0.1
            msg = BIO_NARRATIVE["CIRCADIAN"]["LUNAR"]
        return bias, msg

    def _apply_enzyme_reaction(self, enzyme_type: str, harvest_hits: int):
        if harvest_hits > 0:
            satiety_dampener = max(0.1, 1.0 - self.dopamine)
            base_reward = math.log(harvest_hits + 1) * 0.15
            final_reward = base_reward * satiety_dampener
            self.dopamine += final_reward
            self.cortisol -= (final_reward * 0.4)
        impact = self._REACTION_MAP.get(enzyme_type)
        if impact:
            if "ADR" in impact: self.adrenaline = min(1.0, self.adrenaline + impact["ADR"])
            if "COR" in impact: self.cortisol = max(0.0, self.cortisol + impact["COR"])
            if "OXY" in impact: self.oxytocin = min(1.0, self.oxytocin + impact["OXY"])
            if "DOP" in impact: self.dopamine = min(1.0, self.dopamine + impact["DOP"])
            if "SER" in impact: self.serotonin = min(1.0, self.serotonin + impact["SER"])

    def _apply_environmental_pressure(self, feedback: Dict, health: float, stamina: float, ros_level: float, stress_mod: float):
        if feedback.get("STATIC", 0) > 0.6:
            self.cortisol += (BoneConfig.BIO.REWARD_LARGE * stress_mod)
        if feedback.get("INTEGRITY", 0) > 0.8:
            self.dopamine += BoneConfig.BIO.REWARD_MEDIUM
        else:
            self.dopamine -= BoneConfig.BIO.DECAY_RATE
        if stamina < 20.0:
            self.cortisol += (BoneConfig.BIO.REWARD_MEDIUM * stress_mod)
            self.dopamine -= BoneConfig.BIO.REWARD_MEDIUM
        if ros_level > 20.0:
            self.cortisol += (BoneConfig.BIO.REWARD_LARGE * stress_mod)
        if health < 30.0 or feedback.get("STATIC", 0) > 0.8:
            self.adrenaline += (BoneConfig.BIO.REWARD_LARGE * stress_mod)
        else:
            self.adrenaline -= (BoneConfig.BIO.DECAY_RATE * 5)

    def _apply_semantic_pressure(self, signal: SemanticSignal):
        if signal.novelty > 0.3:
            self.dopamine += (signal.novelty * 0.3)
        if signal.resonance > 0.2:
            self.oxytocin += (signal.resonance * 0.4)
            self.cortisol -= (signal.resonance * 0.2)
        if signal.valence > 0.3:
            self.serotonin += (signal.valence * 0.3)
            self.oxytocin += (signal.valence * 0.2)
        elif signal.valence < -0.3:
            self.cortisol += (abs(signal.valence) * 0.2)
        if signal.coherence > 0.7:
            self.adrenaline -= 0.1
            self.cortisol -= 0.1

    def _maintain_homeostasis(self, social_context: bool):
        if self.serotonin > 0.5:
            excess = self.serotonin - 0.5
            self.cortisol -= (excess * 0.2)
        if social_context:
            self.oxytocin += BoneConfig.BIO.REWARD_MEDIUM
            self.cortisol -= BoneConfig.BIO.REWARD_MEDIUM
        if self.cortisol > 0.6:
            suppression = (self.cortisol - 0.6) * 0.5
            self.oxytocin -= suppression
        if self.oxytocin > 0.5:
            relief = (self.oxytocin - 0.5) * 0.8
            self.cortisol -= relief
        if self.adrenaline < 0.2:
            self.melatonin += (BoneConfig.BIO.REWARD_SMALL / 2)
        elif self.adrenaline > 0.8:
            self.melatonin = 0.0

    def check_for_glimmer(self, feedback: Dict, harvest_hits: int) -> Optional[str]:
        if feedback.get("INTEGRITY", 0) > 0.9 and feedback.get("STATIC", 0) < 0.2:
            self.glimmers += 1
            self.serotonin += 0.2
            return BIO_NARRATIVE["GLIMMER"]["INTEGRITY"]
        if harvest_hits > 2 and self.dopamine > 0.8:
            self.glimmers += 1
            self.oxytocin += 0.2
            return BIO_NARRATIVE["GLIMMER"]["ENTHUSIASM"]
        return None

    def metabolize(self, feedback: Dict, health: float, stamina: float, ros_level: float = 0.0,
                   social_context: bool = False, enzyme_type: Optional[str] = None,
                   harvest_hits: int = 0, stress_mod: float = 1.0,
                   circadian_bias: Dict[str, float] = None,
                   semantic_signal: Optional[SemanticSignal] = None) -> Dict[str, Any]:
        if circadian_bias:
            self.cortisol += circadian_bias.get("COR", 0.0)
            self.serotonin += circadian_bias.get("SER", 0.0)
            self.melatonin += circadian_bias.get("MEL", 0.0)
        self._apply_enzyme_reaction(enzyme_type, harvest_hits)
        self._apply_environmental_pressure(feedback, health, stamina, ros_level, stress_mod)
        if semantic_signal:
            self._apply_semantic_pressure(semantic_signal)
        self._maintain_homeostasis(social_context)
        glimmer_msg = self.check_for_glimmer(feedback, harvest_hits)
        self.dopamine = self._clamp(self.dopamine)
        self.oxytocin = self._clamp(self.oxytocin)
        self.cortisol = self._clamp(self.cortisol)
        self.serotonin = self._clamp(self.serotonin)
        self.adrenaline = self._clamp(self.adrenaline)
        self.melatonin = self._clamp(self.melatonin)
        state: Dict[str, Any] = self.get_state()
        if glimmer_msg:
            state["glimmer_msg"] = glimmer_msg
        return state

    def get_state(self) -> Dict[str, float]:
        return {
            "DOP": round(self.dopamine, 2),
            "OXY": round(self.oxytocin, 2),
            "COR": round(self.cortisol, 2),
            "SER": round(self.serotonin, 2),
            "ADR": round(self.adrenaline, 2),
            "MEL": round(self.melatonin, 2)}

@dataclass
class MetabolicGovernor:
    mode: str = "COURTYARD"
    GRACE_PERIOD: int = 5
    psi_mod: float = 0.2
    kappa_target: float = 0.0
    drag_floor: float = 2.0
    manual_override: bool = False
    birth_tick: float = field(default_factory=time.time)

    @staticmethod
    def get_stress_modifier(tick_count):
        if tick_count <= 2: return 0.0
        if tick_count <= 5: return 0.5
        return 1.0

    @staticmethod
    def calculate_stress(health: float, ros_buildup: float) -> float:
        base_stress = 1.0
        if health < 50.0:
            base_stress += (50.0 - health) * 0.02
        if ros_buildup > 50.0:
            base_stress += (ros_buildup - 50.0) * 0.01
        return round(min(3.0, base_stress), 2)

    def set_override(self, target_mode):
        valid = {"COURTYARD", "LABORATORY", "FORGE", "SANCTUARY"}
        if target_mode in valid:
            self.mode = target_mode
            self.manual_override = True
            return BIO_NARRATIVE["GOVERNOR"]["OVERRIDE"].format(mode=target_mode)
        return BIO_NARRATIVE["GOVERNOR"]["INVALID"]

    def shift(self, physics: Dict, _voltage_history: List[float], current_tick: int = 0) -> Optional[str]:
        if self.manual_override:
            current_voltage = physics.get("voltage", 0.0)
            if current_voltage > 25.0:
                self.manual_override = False
                return BIO_NARRATIVE["GOVERNOR"].get("OVERRIDE_CLEARED", "OVERRIDE CLEARED: VOLTAGE CRITICAL")
            return None
        current_voltage = physics.get("voltage", 0.0)
        drag = physics.get("narrative_drag", 0.0)
        beta = physics.get("beta_index", 0.0)
        if current_tick <= 5:
            physics["voltage"] = min(physics.get("voltage", 0.0), 8.0)
        if current_voltage > 15.0 and beta > 1.5:
            if self.mode != "SANCTUARY":
                self.mode = "SANCTUARY"
                physics["narrative_drag"] = 0.0
                return BIO_NARRATIVE["GOVERNOR"]["SANCTUARY"].format(
                    color=Prisma.GRN, beta=beta, reset=Prisma.RST)
        if current_voltage > 10.0:
            if self.mode != "FORGE":
                self.mode = "FORGE"
                return BIO_NARRATIVE["GOVERNOR"]["FORGE"].format(
                    color=Prisma.RED, volts=current_voltage, reset=Prisma.RST)
        if drag > 4.0 > current_voltage:
            if self.mode != "LABORATORY":
                self.mode = "LABORATORY"
                return BIO_NARRATIVE["GOVERNOR"]["LAB"].format(
                    color=Prisma.CYN, reset=Prisma.RST)
        if self.mode != "COURTYARD":
            if current_voltage < 5.0 and drag < 2.0:
                self.mode = "COURTYARD"
                return BIO_NARRATIVE["GOVERNOR"]["CLEAR"].format(
                    color=Prisma.GRN, reset=Prisma.RST)
        return None

class ViralTracer:
    def __init__(self, mem):
        self.mem = mem
        self.max_depth = 4

    @staticmethod
    def _is_ruminative(word):
        return (word in TheLexicon.get("abstract")) or (
                word in TheLexicon.get("antigen"))

    def inject(self, start_node):
        if start_node not in self.mem.graph:
            return None
        if not self._is_ruminative(start_node):
            return None
        return self._walk(start_node, self.max_depth)

    def _walk(self, start, max_depth):
        stack = [(start, [start], 0)]
        visited = {start}
        while stack:
            current, path, depth = stack.pop()
            if depth >= max_depth:
                continue
            edges = self.mem.graph.get(current, {}).get("edges", {})
            for next_node, weight in edges.items():
                if weight < 1:
                    continue
                if not self._is_ruminative(next_node):
                    continue
                if next_node in path:
                    return path + [next_node]
                if next_node not in visited:
                    visited.add(next_node)
                    stack.append((next_node, path + [next_node], depth + 1))
        return None

    def psilocybin_rewire(self, loop_path):
        if len(loop_path) < 2:
            return None
        node_a = loop_path[0]
        node_b = loop_path[1]
        if node_b in self.mem.graph[node_a]["edges"]:
            self.mem.graph[node_a]["edges"][node_b] = 0
        sensory = TheLexicon.harvest("photo")
        action = TheLexicon.harvest("kinetic")
        if isinstance(sensory, dict) or isinstance(action, dict):
            sensory = "light"
            action = "move"
        if sensory == "void" or action == "void":
            return "GRAFT FAILED: The patients' vocabulary is too limited for a breakthrough."
        if node_a not in self.mem.graph:
            self.mem.graph[node_a] = {"edges": {}, "last_tick": 0}
        self.mem.graph[node_a]["edges"][sensory] = 5
        if sensory not in self.mem.graph:
            self.mem.graph[sensory] = {"edges": {}, "last_tick": 0}
        self.mem.graph[sensory]["edges"][action] = 5
        if action not in self.mem.graph:
            self.mem.graph[action] = {"edges": {}, "last_tick": 0}
        self.mem.graph[action]["edges"][node_b] = 5
        return f"PSILOCYBIN REWIRE: Broken Loop '{node_a}↔{node_b}'. Grafted '{sensory}'(S) -> '{action}'(A)."

class ThePacemaker:
    def __init__(self):
        self.history = deque(maxlen=5)
        self.repetition_score = 0.0
        self.last_tick_time = time.time()
        self.boredom_level = 0.0

    def check_pulse(self, clean_words: List[str]) -> float:
        if not clean_words: return 0.0
        current_set = set(clean_words)
        max_overlap = 0.0
        for old_words in self.history:
            old_set = set(old_words)
            intersection = len(current_set & old_set)
            union = len(current_set | old_set)
            if union > 0:
                score = intersection / union
                if score > max_overlap:
                    max_overlap = score
        self.history.append(clean_words)
        self.repetition_score = max_overlap
        now = time.time()
        delta = now - self.last_tick_time
        self.last_tick_time = now
        if delta > 300:
            delta = 300
            self.boredom_level = max(0.0, self.boredom_level - 10.0)
        if self.repetition_score > 0.3:
            self.boredom_level += 2.0
        elif delta > 60:
            self.boredom_level += min(5.0, delta / 60.0)
        else:
            self.boredom_level = max(0.0, self.boredom_level - 1.0)
        return self.repetition_score

    def get_status(self):
        if self.repetition_score > BoneConfig.MAX_REPETITION_LIMIT: return "ZOMBIE_KNOCK"
        elif self.repetition_score > 0.2: return "ECHO"
        return "CLEAR"

    def is_bored(self):
        return self.boredom_level > BoneConfig.BOREDOM_THRESHOLD

class NoeticLoop:
    def __init__(self, mind_layer, bio_layer, events):
        self.mind = mind_layer
        self.bio = bio_layer
        self.arbiter = SynergeticLensArbiter(events)

    def think(self, physics_packet, _bio_result_dict, inventory, voltage_history, tick_count):
        volts = physics_packet.get("voltage", 0.0)
        drag = physics_packet.get("narrative_drag", 0.0)
        if volts < 1.5 and drag < 1.5:
            raw_text = physics_packet.get("raw_text", "")
            stripped_thought = TheLexicon.walk_gradient(raw_text)
            return {
                "mode": "COGNITIVE",
                "lens": "GRADIENT_WALKER",
                "context_msg": f"ECHO: {stripped_thought}",
                "role": "The Reducer",
                "ignition": 0.0,
                "hebbian_msg": None}
        ignition_score, _, _ = self.mind.integrator.measure_ignition(
            physics_packet["clean_words"],
            voltage_history)
        mind_data = self.arbiter.consult(
            physics_packet,
            _bio_result_dict,
            inventory,
            tick_count,
            ignition_score)
        standardized_mind = {}
        if isinstance(mind_data, tuple):
            standardized_mind = {
                "lens": mind_data[0],
                "context_msg": mind_data[1],
                "role": mind_data[2]}
        elif isinstance(mind_data, dict):
            standardized_mind = mind_data
            standardized_mind.setdefault("context_msg", standardized_mind.get("msg", ""))
            standardized_mind.setdefault("lens", "DEFAULT")
            standardized_mind.setdefault("role", "Observer")
        hebbian_msg = None
        if physics_packet["voltage"] > 12.0 and len(physics_packet["clean_words"]) >= 2:
            if random.random() < 0.15:
                w1, w2 = random.sample(physics_packet["clean_words"], 2)
                hebbian_msg = self.bio.plasticity.force_hebbian_link(self.mind.mem.graph, w1, w2)
        current_physics = {}
        if hasattr(self, 'stabilizer'):
            current_physics = self.stabilizer.get_physics_state()
        elif hasattr(self, 'physics_engine'):
            current_physics = self.physics_engine.get_state()
        return {
            "mode": "COGNITIVE",
            "lens": mind_data.get("lens"),
            "context_msg": mind_data.get("context_msg", mind_data.get("msg")),
            "role": mind_data.get("role"),
            "ignition": ignition_score,
            "physics": current_physics,
            "bio": self.endo.get_state() if hasattr(self, 'endo') else {}}