""" bone_body.py """

import math, random, time
from collections import deque, Counter
from dataclasses import dataclass, field, asdict
from typing import Set, Optional, Dict, List, Any, Tuple

from bone_spores import ImmuneMycelium, BioLichen, BioParasite
from bone_lexicon import TheLexicon
from bone_core import Prisma, BoneConfig, TheLore

def _get_val(obj, key, default=0.0):
    if isinstance(obj, dict): return obj.get(key, default)
    return getattr(obj, key, default)

def _set_val(obj, key, value):
    if isinstance(obj, dict): obj[key] = value
    else: setattr(obj, key, value)

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
    waste_generated: float
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
    BASE_ATP_YIELD = 2.0
    LONG_WORD_BONUS = 2.5
    VOLTAGE_BONUS_THRESHOLD = 8.0
    PROTEASE_BONUS = 10.0
    DOPAMINE_SATIETY = 0.7
    CORTISOL_STRESS = 0.6
    ADRENALINE_SURGE = 0.6
    GOV_VOLTAGE_CRITICAL = 25.0
    GOV_VOLTAGE_HIGH = 15.0
    GOV_VOLTAGE_MED = 10.0
    GOV_VOLTAGE_LOW = 5.0
    GOV_DRAG_HIGH = 4.0
    GOV_DRAG_LOW = 2.0

@dataclass
class BioSystem:
    mito: 'MitochondrialForge'
    endo: 'EndocrineSystem'
    governor: 'MetabolicGovernor'
    immune: Optional[ImmuneMycelium] = None
    lichen: Optional[BioLichen] = None
    parasite: Optional[BioParasite] = None
    plasticity: Any = None
    shimmer: Any = None
    events: Any = None
    biometrics: Optional['Biometrics'] = None

    def setup_listeners(self):
        if self.events and hasattr(self.events, "subscribe"):
            self.events.subscribe("NEURAL_STATE_SHIFT", self._on_neural_shift)
            self.events.log("[BIO]: Vagus Nerve connected.", "SYS")

    def to_dict(self) -> Dict[str, Any]:
        mito_data = {}
        if self.mito and hasattr(self.mito, "state"):
            mito_data = asdict(self.mito.state)
            mito_data['atp'] = mito_data.get('atp_pool', 0.0)
        chem_data = {}
        if self.endo:
            chem_data = self.endo.get_state()
        biometrics_data = {}
        if self.biometrics:
            biometrics_data = asdict(self.biometrics)
        return {
            "mito": mito_data,
            "endo": chem_data,
            "chem": chem_data,
            "biometrics": biometrics_data,
            "governor_mode": self.governor.mode if self.governor else "UNKNOWN"}

    def _on_neural_shift(self, payload):
        state = payload.get("state", "NEUTRAL")
        chem_data = payload.get("chem", {})
        if state == "PANIC":
            self.endo.adrenaline = min(1.0, self.endo.adrenaline + 0.3)
            self.endo.cortisol = min(1.0, self.endo.cortisol + 0.2)
            if self.events:
                self.events.log(f"{Prisma.RED}🫀 VAGUS NERVE: Panic detected. Heart rate spiking.{Prisma.RST}", "BIO")
        elif state == "ZEN":
            self.endo.cortisol = max(0.0, self.endo.cortisol - 0.3)
            self.endo.serotonin = min(1.0, self.endo.serotonin + 0.2)
            if self.events:
                self.events.log(f"{Prisma.GRN}🫀 VAGUS NERVE: Lucid state. Lowering cortisol.{Prisma.RST}", "BIO")
        elif state == "MANIC":
            self.mito.adjust_atp(-10.0, "Neural Overclock")

    def apply_environmental_entropy(self, physics_packet):
        base_entropy = 2.0
        em_field = 0.0
        if hasattr(physics_packet, "vector") and physics_packet.vector:
            vec = physics_packet.vector
            e_val = vec.get("E", 0.0)
            b_val = vec.get("PHI", 0.0)
            em_field = math.sqrt(e_val**2 + b_val**2)
        else:
            e_val = _get_val(physics_packet, "E", 0.0)
            b_val = _get_val(physics_packet, "B", 0.0)
            em_field = math.sqrt(e_val**2 + b_val**2)
        shield_strength = min(0.8, em_field * 0.1)
        effective_entropy = base_entropy * (1.0 - shield_strength)
        thermal_feedback = 0.0
        HEAT_THRESHOLD = 0.8
        if em_field > HEAT_THRESHOLD:
            thermal_feedback = (em_field - HEAT_THRESHOLD) * 5.0
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

@dataclass
class MitochondrialForge:
    MAX_SAFE_BURN = 25.0
    ANAEROBIC_THRESHOLD = 40.0

    def __init__(self, state_ref: MitochondrialState, events_ref):
        self.state = state_ref
        self.events = events_ref
        full_narrative = TheLore.get("BIO_NARRATIVE") or {}
        self.narrative = full_narrative.get("MITO", {})

    def adjust_atp(self, delta: float, reason: str = ""):
        old = self.state.atp_pool
        max_limit = getattr(BoneConfig, "MAX_ATP", 100.0)
        self.state.atp_pool = max(BioConstants.ATP_COLLAPSE, min(max_limit, old + delta))
        if reason and (abs(delta) > 5.0 or self.state.atp_pool > 90.0):
            self.events.log(f"[ATP]: {reason} ({delta:+.1f})", "BIO")

    def _get_text(self, key, **kwargs):
        tmpl = self.narrative.get(key, f"MITO_{key}")
        try:
            return tmpl.format(**kwargs)
        except Exception:
            return tmpl

    def _trigger_anaerobic_bypass(self, raw_cost: float) -> MetabolicReceipt:
        health_burn = 2.0
        self.state.ros_buildup += 2.0
        if self.events:
            self.events.log(
                f"{Prisma.MAG}⚡ ANAEROBIC BYPASS: Load ({raw_cost:.1f}) too high for ATP. Burning Health instead.{Prisma.RST}",
                "BIO_WARN")
        return MetabolicReceipt(
            base_cost=raw_cost,
            drag_tax=0.0,
            inefficiency_tax=0.0,
            total_burn=health_burn,
            waste_generated=2.0,
            status="ANAEROBIC",
            symptom="LACTATE_BUILDUP")

    def process_cycle(self, physics_packet: dict, external_modifiers: List[float] = None) -> MetabolicReceipt:
        voltage = _get_val(physics_packet, "voltage", 0.0)
        raw_drag = _get_val(physics_packet, "narrative_drag", 0.0)
        drag = max(0.0, raw_drag)
        base_demand = max(0.1, math.log1p(voltage) * 1.5)
        raw_tax = (drag ** 1.5) * 0.5
        cognitive_load_tax = min(5.0, raw_tax)
        pre_calc_cost = base_demand + raw_tax
        if pre_calc_cost > self.ANAEROBIC_THRESHOLD:
            return self._trigger_anaerobic_bypass(pre_calc_cost)
        is_critical = self.state.atp_pool < BioConstants.ATP_CRITICAL
        if is_critical:
            cognitive_load_tax = 0.0
            external_modifiers = [0.5]
            if self.events and self.state.retrograde_signal != "HIBERNATING":
                msg = self._get_text("NECROSIS", cost=base_demand, pool=self.state.atp_pool)
                self.events.log(f"{Prisma.VIOLET}💤 {msg}{Prisma.RST}", "BIO_CRIT")
                self.state.retrograde_signal = "HIBERNATING"
        mod_factor = 1.0
        if external_modifiers:
            for m in external_modifiers:
                mod_factor *= m
        efficiency = max(0.35, self.state.membrane_potential)
        raw_cost = ((base_demand + cognitive_load_tax) * mod_factor) / efficiency
        if raw_cost > self.MAX_SAFE_BURN:
            excess = raw_cost - self.MAX_SAFE_BURN
            raw_cost = self.MAX_SAFE_BURN
            if self.events:
                self.events.log(
                    f"{Prisma.CYN}⚡ SURGE PROTECTOR: Metabolic spike dampened (-{excess:.1f} ignored).{Prisma.RST}", "BIO")
        if raw_cost > 15.0 and self.events and random.random() < 0.2:
            msg = self._get_text("GRINDING")
            self.events.log(f"{Prisma.OCHRE}⚙️ {msg}{Prisma.RST}", "BIO_WARN")
        total_metabolic_cost = raw_cost
        waste_generated = total_metabolic_cost * (1.0 - efficiency) * 0.5
        self.state.ros_buildup += waste_generated
        self.adjust_atp(-total_metabolic_cost, "Metabolic Burn")
        if total_metabolic_cost >= self.MAX_SAFE_BURN and not is_critical:
            self.state.membrane_potential = max(0.1, self.state.membrane_potential - 0.005)
        self._apply_adaptive_dynamics(waste_generated)
        status = "RESPIRING"
        if is_critical: status = "LOW_POWER"
        if self.state.atp_pool <= BioConstants.ATP_COLLAPSE: status = "NECROSIS"
        return MetabolicReceipt(
            base_cost=round(base_demand, 2),
            drag_tax=round(cognitive_load_tax, 2),
            inefficiency_tax=round(total_metabolic_cost - (base_demand + cognitive_load_tax), 2),
            total_burn=round(total_metabolic_cost, 2),
            waste_generated=round(waste_generated, 2),
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
        msg = self._get_text("APOPTOSIS")
        self.events.log(f"{Prisma.RED}♻️ [MITO]: {msg}{Prisma.RST}", "BIO_CRIT")

    def _print_receipt(self, base, tax, total) -> MetabolicReceipt:
        status = "NOMINAL"
        if self.state.atp_pool < 20.0: status = "LOW_POWER"
        if self.state.atp_pool <= 0.0: status = "METABOLIC_COLLAPSE"
        return MetabolicReceipt(
            base_cost=round(base, 2),
            drag_tax=round(tax, 2),
            inefficiency_tax=round(total - (base + tax), 2),
            total_burn=round(total, 2),
            waste_generated=0.0,
            status=status,
            symptom=self.state.retrograde_signal)

    def apply_inheritance(self, traits: dict):
        if traits.get("high_metabolism"):
            self.state.membrane_potential = 1.1
            self.events.log("[MITO]: Ancestral High Metabolism activated.", "GENETICS")

class SemanticEndocrinologist:
    def __init__(self, memory_ref, lexicon_ref):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.last_topics = deque(maxlen=3)

    def assess(self, clean_words: List[str], physics: Dict) -> SemanticSignal:
        if not clean_words:
            return SemanticSignal()
        cortical_set = set()
        graph_ref = {}
        if self.mem:
            cortical_set = set(getattr(self.mem, "cortical_stack", []))
            graph_ref = getattr(self.mem, "graph", {})
        novel_count = sum(1 for w in clean_words if len(w) > 4 and w not in cortical_set)
        novelty_score = min(1.0, novel_count / max(1, len(clean_words)))
        resonance_score = 0.0
        if graph_ref:
            hits = sum(1 for w in clean_words if w in graph_ref)
            resonance_score = min(1.0, hits / max(1, len(clean_words)))
        valence_score = 0.0
        if self.lex and hasattr(self.lex, "get_valence"):
            valence_score = self.lex.get_valence(clean_words)
        coherence_score = _get_val(physics, "kappa", 0.5)
        return SemanticSignal(
            novelty=novelty_score,
            resonance=resonance_score,
            valence=valence_score,
            coherence=coherence_score)

class SomaticLoop:
    _ENZYME_MAP = {
        "static": "CELLULASE",
        "abstract": "DECRYPTASE",
        "natural": "LIGNASE",
        "synthetic": "CHITINASE",
        "social": "AMYLASE",
        "antigen": "OXIDASE"}
    SAMPLING_THRESHOLD = 1000
    BASE_WORD_VALUE = 0.5
    COMPLEX_WORD_BONUS = 2.0
    CLICHE_TAX_RATE = 3.0

    def __init__(self, bio_system_ref: BioSystem, memory_ref=None, lexicon_ref=None, gordon_ref=None, folly_ref=None, events_ref=None):
        self.bio = bio_system_ref
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.gordon = gordon_ref
        self.folly = folly_ref
        self.events = events_ref
        self.narrative_data = TheLore.get("BIO_NARRATIVE") or {}
        if not self.narrative_data:
            if hasattr(self.events, 'log'):
                self.events.log(f"{Prisma.OCHRE}[BODY]: Warning - BIO_NARRATIVE missing.{Prisma.RST}", "SYS")
            self.narrative_data = {"symptoms": {}, "organs": {}, "GLIMMER": {}, "GOVERNOR": {}}
        if getattr(self.bio, 'endo', None):
            self.bio.endo.narrative_data = self.narrative_data
        if getattr(self.bio, 'governor', None):
            self.bio.governor.narrative_data = self.narrative_data
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
        if self.bio.events and hasattr(self.bio, "apply_environmental_entropy"):
            self.bio.apply_environmental_entropy(physics_data)
        modifiers = self._gather_hormonal_modifiers(phys, logs)
        receipt = self.bio.mito.process_cycle(phys, external_modifiers=modifiers)
        if receipt.waste_generated > 1.0:
            self.bio.endo.cortisol = min(1.0, self.bio.endo.cortisol + (receipt.waste_generated * 0.05))
        resp_status = receipt.status
        audit_result = self._audit_folly_desire(phys, stamina, logs)
        if audit_result == "MAUSOLEUM_CLAMP":
            return self._package_result(receipt.status, logs, enzyme="NONE")
        elif audit_result == "AUTOPHAGY":
            logs.append(f"{Prisma.RED}⚠️ AUTOPHAGY: Burning Health for Fuel (-5 HP).{Prisma.RST}")
            stamina = 10.0
        total_yield = 0.0
        enzyme = "NONE"
        if self.bio.lichen:
            sugar, photo_log = self.bio.lichen.photosynthesize(phys, phys["clean_words"], tick_count)
            if sugar > 0:
                total_yield += sugar
            if photo_log:
                logs.append(photo_log)
        soma_enzyme, soma_yield = self._harvest_resources(phys, logs)
        total_yield += soma_yield
        if enzyme == "NONE":
            enzyme = soma_enzyme
        self.bio.mito.adjust_atp(total_yield, "Symbiotic Yield")
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
                logs.append(
                    f"{Prisma.RED}[BIO]: Cortisol spiking. Metabolism inefficient (x{stress_tax:.2f}).{Prisma.RST}")
        if chem.adrenaline > 0.6:
            modifiers.append(0.5)
            logs.append(f"{Prisma.YEL}[BIO]: Adrenaline Surge. Pain ignored.{Prisma.RST}")
        if chem.dopamine > 0.7:
            modifiers.append(0.8)
        voltage = _get_val(phys, "voltage", 0.0)
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
        else:
            voltage = getattr(physics_packet, "voltage", 0.0)
            drag = getattr(physics_packet, "narrative_drag", getattr(physics_packet, "drag", 0.0))
            kappa = getattr(physics_packet, "kappa", 0.5)
            clean_words = getattr(physics_packet, "clean_words", [])
            counts = getattr(physics_packet, "counts", {})
        return {
            "voltage": voltage,
            "drag": drag,
            "narrative_drag": drag,
            "kappa": kappa,
            "clean_words": clean_words,
            "counts": counts}

    def _audit_folly_desire(self, phys, stamina, logs) -> str:
        voltage = _get_val(phys, "voltage", 0.0)
        if stamina <= 0:
            if self.bio.biometrics.health > 10.0:
                burn_amount = 5.0
                self.bio.biometrics.health -= burn_amount
                return "AUTOPHAGY"
            else:
                logs.append(f"{Prisma.RED}SYSTEM FAILURE: Bio-Fuel Depleted. The Mausoleum closes.{Prisma.RST}")
                return "MAUSOLEUM_CLAMP"
        if voltage > 30.0:
            logs.append(f"{Prisma.RED}CRITICAL: Voltage Overload ({voltage:.1f}v). System clamping.{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"
        return "CLEAR"

    def _harvest_resources(self, phys: Dict, logs: List[str]) -> Tuple[str, float]:
        clean_words = phys.get("clean_words", [])
        if not clean_words: return "NONE", 0.0
        words_to_process, scaling_factor = self._sample_input(clean_words, logs)
        raw_yield, found_enzymes, cliche_tax = self._digest_words(words_to_process)
        total_atp = (raw_yield * scaling_factor)
        scaled_tax = (cliche_tax * scaling_factor)
        if scaled_tax > 0:
            total_atp = max(0.0, total_atp - scaled_tax)
            self.bio.endo.cortisol = min(1.0, self.bio.endo.cortisol + (scaled_tax * 0.02))
            logs.append(f"{Prisma.RED}[BIO]: 🛑 CLICHÉ TAX: -{scaled_tax:.1f} ATP. (Antigens Detected){Prisma.RST}")
        if _get_val(phys, "voltage", 0.0) > 8.0 and found_enzymes:
            found_enzymes.append("PROTEASE")
            total_atp += 5.0
        dominant = Counter(found_enzymes).most_common(1)[0][0] if found_enzymes else "NONE"
        return dominant, total_atp

    def _sample_input(self, words: List[str], logs: List[str]) -> Tuple[List[str], float]:
        count = len(words)
        if count > self.SAMPLING_THRESHOLD:
            factor = count / self.SAMPLING_THRESHOLD
            if random.random() < 0.1:
                logs.append(f"{Prisma.GRY}[BIO]: Mass Input ({count}). Sampling x{factor:.1f}.{Prisma.RST}")
            return random.sample(words, self.SAMPLING_THRESHOLD), factor
        return words, 1.0

    def _digest_words(self, words: List[str]) -> Tuple[float, List[str], float]:
        atp_yield = 0.0
        enzymes = []
        cliche_tax = 0.0
        word_counts = Counter(words)
        for word, count in word_counts.items():
            if len(word) < 4: continue
            cat = TheLexicon.get_current_category(word)
            if not cat or cat == "void":
                atp_yield += (self.BASE_WORD_VALUE * count)
                continue
            if cat == "antigen":
                cliche_tax += (self.CLICHE_TAX_RATE * count)
                continue
            if cat not in ["kinetic", "explosive"]:
                enzyme = self._map_category_to_enzyme(cat)
                if enzyme != "AMYLASE":
                    enzymes.append(enzyme)
                    val = self.COMPLEX_WORD_BONUS if len(word) > 7 else self.BASE_WORD_VALUE
                    total_val = val * (1.0 + math.log(count))
                    atp_yield += total_val
        return atp_yield, enzymes, cliche_tax

    def _map_category_to_enzyme(self, category: str) -> str:
        return self.enzyme_map.get(category, "AMYLASE")

    @staticmethod
    def _perform_maintenance(text: str, phys: Dict, logs: List[str], tick: int):
        if len(text) > 10000:
            logs.append(f"{Prisma.GRY}[MAINTENANCE]: Large input buffer detected.{Prisma.RST}")
        drag = _get_val(phys, "narrative_drag", 0.0)
        if drag > 8.0 and tick % 10 == 0:
            logs.append(
                f"{Prisma.OCHRE}[MAINTENANCE]: Clearing sludge from intake valves (Drag {drag:.1f}).{Prisma.RST}")

    @staticmethod
    def _count_harvest_hits(phys: Dict) -> int:
        clean_words = phys.get("clean_words", [])
        return len([w for w in clean_words if len(w) >= 4])

    def _package_result(self, resp_status, logs, chem_state=None, enzyme="NONE"):
        is_alive = (resp_status == "RESPIRING" or resp_status == "ANAEROBIC")
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
    narrative_data: Dict = field(default_factory=dict, repr=False)
    _REACTION_MAP = {
        "PROTEASE":   {"ADR": 0.1},
        "CELLULASE":  {"COR": -0.1, "OXY": 0.05},
        "CHITINASE":  {"DOP": 0.15},
        "LIGNASE":    {"SER": 0.1},
        "DECRYPTASE": {"ADR": 0.05, "DOP": 0.05},
        "AMYLASE":    {"SER": 0.15, "OXY": 0.1}}

    def __post_init__(self):
        if hasattr(BoneConfig, "BIO"):
            self._REACTION_MAP = {
                "PROTEASE":   {"ADR": BoneConfig.BIO.REWARD_MEDIUM},
                "CELLULASE":  {"COR": -BoneConfig.BIO.REWARD_MEDIUM, "OXY": BoneConfig.BIO.REWARD_SMALL},
                "CHITINASE":  {"DOP": BoneConfig.BIO.REWARD_LARGE},
                "LIGNASE":    {"SER": BoneConfig.BIO.REWARD_MEDIUM},
                "DECRYPTASE": {"ADR": BoneConfig.BIO.REWARD_SMALL, "DOP": BoneConfig.BIO.REWARD_SMALL},
                "AMYLASE":    {"SER": BoneConfig.BIO.REWARD_LARGE, "OXY": BoneConfig.BIO.REWARD_MEDIUM}}

    @staticmethod
    def _clamp(val: float) -> float:
        return max(0.0, min(1.0, val))

    def calculate_circadian_bias(self) -> Tuple[Dict[str, float], Optional[str]]:
        hour = time.localtime().tm_hour
        bias = {"COR": 0.0, "SER": 0.0, "MEL": 0.0}
        circadian_text = self.narrative_data.get("CIRCADIAN", {})
        if 6 <= hour < 10:
            bias["COR"] = 0.1
            msg = circadian_text.get("DAWN", "Sunrise.")
        elif 10 <= hour < 18:
            bias["SER"] = 0.1
            msg = circadian_text.get("SOLAR", "High Noon.")
        elif 18 <= hour < 23:
            bias["MEL"] = 0.1
            msg = circadian_text.get("TWILIGHT", "Sunset.")
        else:
            bias["MEL"] = 0.3
            bias["COR"] = -0.1
            msg = circadian_text.get("LUNAR", "Night.")
        return bias, msg

    def _apply_enzyme_reaction(self, enzyme_type: str, harvest_hits: int):
        if harvest_hits > 0:
            satiety_dampener = max(0.1, 1.0 - self.dopamine)
            base_reward = math.log(harvest_hits + 1) * 0.15
            final_reward = base_reward * satiety_dampener
            self.dopamine += final_reward
            self.cortisol -= (final_reward * 0.4)
        if enzyme_type == "DECRYPTASE":
            self.serotonin = min(1.0, self.serotonin + 0.15)
            self.cortisol = max(0.0, self.cortisol - 0.2)
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
        dampener = 0.2
        if self.serotonin > 0.5:
            excess = self.serotonin - 0.5
            self.cortisol -= (excess * 0.2 * dampener)
        if social_context:
            self.oxytocin += BoneConfig.BIO.REWARD_MEDIUM
            self.cortisol -= BoneConfig.BIO.REWARD_MEDIUM
        if self.cortisol > 0.6:
            suppression = (self.cortisol - 0.6) * 0.5
            self.oxytocin -= (suppression * dampener)
        if self.oxytocin > 0.5:
            relief = (self.oxytocin - 0.5) * 0.8
            self.cortisol -= (relief * dampener)
        if self.adrenaline < 0.2:
            self.melatonin += (BoneConfig.BIO.REWARD_SMALL / 2)
        elif self.adrenaline > 0.8:
            self.melatonin = 0.0

    def check_for_glimmer(self, feedback: Dict, harvest_hits: int) -> Optional[str]:
        glimmer_text = self.narrative_data.get("GLIMMER", {})

        if feedback.get("INTEGRITY", 0) > 0.85:
            self.glimmers += 1
            self.serotonin += 0.2
            return glimmer_text.get("INTEGRITY", "You feel whole.")
        if feedback.get("NOVELTY", 0) > 0.8:
            self.glimmers += 1
            self.dopamine += 0.1
            return glimmer_text.get("DISCOVERY", "GLIMMER: A spark of the new.")
        if harvest_hits > 2 and self.dopamine > 0.7:
            self.glimmers += 1
            self.oxytocin += 0.2
            return glimmer_text.get("ENTHUSIASM", "The work feels good.")
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

class PIDController:
    def __init__(self, kp, ki, kd, setpoint, output_limits=(-10.0, 10.0)):
        self.kp = kp; self.ki = ki; self.kd = kd
        self.setpoint = setpoint
        self.min_out, self.max_out = output_limits
        self._integral = 0.0; self._last_error = 0.0; self._first_run = True

    def reset(self):
        self._integral = 0.0; self._last_error = 0.0; self._first_run = True

    def update(self, measurement: float, dt: float = 1.0) -> float:
        if dt <= 0.0: return 0.0
        error = self.setpoint - measurement
        if self._first_run:
            self._last_error = error
            self._first_run = False
        P = self.kp * error
        self._integral += error * dt
        self._integral = max(self.min_out, min(self.max_out, self._integral))
        I = self.ki * self._integral
        derivative = (error - self._last_error) / dt
        D = self.kd * derivative
        output = P + I + D
        self._last_error = error
        return max(self.min_out, min(self.max_out, output))

@dataclass
class MetabolicGovernor:
    mode: str = "COURTYARD"
    GRACE_PERIOD: int = 5
    psi_mod: float = 0.2
    kappa_target: float = 0.0
    drag_floor: float = 2.0
    manual_override: bool = False
    birth_tick: float = field(default_factory=time.time)
    narrative_data: Dict = field(default_factory=dict, repr=False)
    last_shift_tick: int = 0
    hysteresis_duration: int = 3
    STATE_THRESHOLDS = [
        (25.0, 0.0, "SANCTUARY", 10),
        (15.0, 0.0, "FORGE", 8),
        (10.0, 0.0, "FORGE", 6),
        (0.0, 4.0, "LABORATORY", 5),
        (0.0, 0.0, "COURTYARD", 1)]

    def __post_init__(self):
        self.voltage_pid = PIDController(kp=0.6, ki=0.05, kd=0.2, setpoint=10.0)
        self.drag_pid = PIDController(kp=0.4, ki=0.1, kd=0.1, setpoint=1.5)

    def recalibrate(self, target_voltage: float, target_drag: float):
        self.voltage_pid.setpoint = target_voltage
        self.drag_pid.setpoint = target_drag

    def regulate(self, physics, dt: float) -> Tuple[float, float]:
        v_force = self.voltage_pid.update(physics.voltage, dt)
        d_force = self.drag_pid.update(physics.narrative_drag, dt)
        return v_force, d_force

    def assess(self, physics_packet) -> Tuple[bool, float]:
        curr_v = _get_val(physics_packet, "voltage", 0.0)
        curr_d = _get_val(physics_packet, "narrative_drag", 0.0)
        dist_v = abs(curr_v - self.voltage_pid.setpoint)
        dist_d = abs(curr_d - self.drag_pid.setpoint)
        is_safe = (dist_v < 3.0) and (dist_d < 1.5)
        return is_safe, math.sqrt(dist_v ** 2 + dist_d ** 2)

    @staticmethod
    def get_stress_modifier(tick_count):
        if tick_count <= 2: return 0.0
        if tick_count <= 5: return 0.5
        return 1.0

    @staticmethod
    def calculate_stress(health: float, ros_buildup: float) -> float:
        base_stress = 1.0
        if health < 50.0:
            base_stress += (50.0 - health) * 0.01
        if ros_buildup > 50.0:
            base_stress += (ros_buildup - 50.0) * 0.01
        return round(min(3.0, base_stress), 2)

    def set_override(self, target_mode):
        valid = {"COURTYARD", "LABORATORY", "FORGE", "SANCTUARY"}
        gov_text = self.narrative_data.get("GOVERNOR", {})
        if target_mode in valid:
            self.mode = target_mode
            self.manual_override = True
            msg_tmpl = gov_text.get("OVERRIDE", "MANUAL OVERRIDE: {mode}")
            return msg_tmpl.format(mode=target_mode)
        return gov_text.get("INVALID", "Invalid Mode Override.")

    def _check_override_safety(self, physics: Dict, gov_text: Dict) -> Optional[str]:
        current_voltage = _get_val(physics, "voltage", 0.0)
        if current_voltage > BioConstants.GOV_VOLTAGE_CRITICAL:
            self.manual_override = False
            return gov_text.get("OVERRIDE_CLEARED", "OVERRIDE CLEARED: VOLTAGE CRITICAL")
        return None

    def shift(self, physics: Dict, _voltage_history: List[float], current_tick: int = 0) -> Optional[str]:
        gov_text = self.narrative_data.get("GOVERNOR", {})
        if self.manual_override:
            return self._check_override_safety(physics, gov_text)
        if (current_tick - self.last_shift_tick) < self.hysteresis_duration:
            return None
        proposed = self._evaluate_state(physics, _voltage_history, current_tick)
        if proposed != self.mode:
            self.mode = proposed
            self.last_shift_tick = current_tick
            return self._get_shift_message(proposed, gov_text, physics)
        return None

    def _evaluate_state(self, physics: Dict, v_history: List[float], tick: int) -> str:
        volts = _get_val(physics, "voltage", 0.0)
        drag = _get_val(physics, "narrative_drag", 0.0)
        v_velocity = 0.0
        if len(v_history) >= 2:
            v_velocity = v_history[-1] - v_history[-2]
        if tick <= 5: return "COURTYARD"
        if volts > BioConstants.GOV_VOLTAGE_HIGH and _get_val(physics, "beta_index", 0.0) > 1.5:
            return "SANCTUARY"
        if volts > 8.0 and v_velocity > 1.0:
            return "FORGE"
        for v_min, d_min, mode, _ in sorted(self.STATE_THRESHOLDS, key=lambda x: x[3], reverse=True):
            if volts >= v_min and drag >= d_min:
                return mode
        return "COURTYARD"

    def _get_shift_message(self, mode: str, text_map: Dict, physics: Dict) -> str:
        colors = {
            "SANCTUARY": Prisma.GRN,
            "FORGE": Prisma.RED,
            "LABORATORY": Prisma.CYN,
            "COURTYARD": Prisma.GRN}
        color = colors.get(mode, Prisma.WHT)
        defaults = {
            "SANCTUARY": "SANCTUARY ACTIVE",
            "FORGE": f"FORGE ACTIVE ({_get_val(physics, 'voltage', 0):.1f}v)",
            "LABORATORY": "LAB ACTIVE",
            "COURTYARD": "SYSTEM CLEAR"}
        key_map = {"LABORATORY": "LAB", "COURTYARD": "CLEAR"}
        lookup = key_map.get(mode, mode)
        tmpl = text_map.get(lookup, defaults.get(mode, "MODE SHIFT"))
        kwargs = {
            "color": color,
            "reset": Prisma.RST,
            "volts": _get_val(physics, 'voltage', 0),
            "beta": _get_val(physics, 'beta_index', 0)}
        try:
            return tmpl.format(**kwargs)
        except:
            return f"{color}{defaults.get(mode)}{Prisma.RST}"