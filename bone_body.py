"""bone_body.py"""

import math, random, time
from collections import deque, Counter
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any, Tuple
from bone_core import Prisma, LoreManifest, ux, safe_get, safe_set, strict_get
from bone_presets import BoneConfig
from bone_spores import ImmuneMycelium, BioLichen, BioParasite

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

@dataclass
class BioSystem:
    mito: "MitochondrialForge"
    endo: "EndocrineSystem"
    governor: "MetabolicGovernor"
    immune: Optional[ImmuneMycelium] = None
    lichen: Optional[BioLichen] = None
    parasite: Optional[BioParasite] = None
    plasticity: Any = None
    shimmer: Any = None
    events: Any = None
    biometrics: Optional["Biometrics"] = None
    config_ref: Any = None

    def setup_listeners(self):
        if self.events and hasattr(self.events, "subscribe"):
            self.events.subscribe("NEURAL_STATE_SHIFT", self._on_neural_shift)
            self.events.subscribe("SUBSTRATE_FORGED", self.mito.on_substrate_forged)
            self.events.subscribe("AUTOPHAGY_EVENT", self._on_autophagy_event)
            self.events.log("[BIO]: Vagus Nerve connected.", "SYS")
        narrative = LoreManifest.get_instance().get("BIO_NARRATIVE") or {}
        if self.mito:
            self.mito.narrative_map = narrative.get("MITO", {})
        if self.endo:
            self.endo.narrative_map = narrative.get("CIRCADIAN", {})
            self.endo.glimmer_map = narrative.get("GLIMMER", {})
        if self.governor:
            self.governor.text_map = narrative.get("GOVERNOR", {})
            self.governor.tax_map = narrative.get("TAX", {})

    def _on_autophagy_event(self, payload):
        atp_gained = payload.get("atp_gained", 15.0)
        if self.mito:
            self.mito.adjust_atp(atp_gained, "Emergency Autophagy")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mito": asdict(self.mito.state) if self.mito else {},
            "endo": self.endo.get_state() if self.endo else {},
            "biometrics": asdict(self.biometrics) if self.biometrics else {},
            "governor_mode": self.governor.mode if self.governor else "UNKNOWN",
        }

    def rest(self, factor: float = 1.0) -> List[str]:
        b = self.biometrics
        if not b:
            return []
        target_cfg = self.config_ref or BoneConfig
        MAX_H = getattr(target_cfg, "MAX_HEALTH", 100.0)
        MAX_S = getattr(target_cfg, "MAX_STAMINA", 100.0)
        cfg = getattr(target_cfg, "BIO", None)
        h_rec = safe_get(cfg, "REST_HEALTH_RECOVERY", 0.5)
        s_rec = safe_get(cfg, "REST_STAMINA_RECOVERY", 1.0)
        b.health = min(MAX_H, b.health + (h_rec * factor))
        b.stamina = min(MAX_S, b.stamina + (s_rec * factor))
        if self.endo:
            ser_boost = safe_get(cfg, "REST_SEROTONIN_BOOST", 0.05)
            cor_drop = safe_get(cfg, "REST_CORTISOL_DROP", 0.05)
            self.endo.serotonin = min(1.0, self.endo.serotonin + (ser_boost * factor))
            self.endo.cortisol = max(0.0, self.endo.cortisol - (cor_drop * factor))
        return []

    def _on_neural_shift(self, payload):
        state = payload.get("state", "NEUTRAL")
        shifts = getattr((self.config_ref or BoneConfig).BIO, "NEURAL_SHIFTS", {})
        if state == "PANIC":
            cfg = shifts.get("PANIC", {"adr": 0.3, "cor": 0.2})
            self.endo.adrenaline = min(1.0, self.endo.adrenaline + cfg.get("adr", 0.3))
            self.endo.cortisol = min(1.0, self.endo.cortisol + cfg.get("cor", 0.2))
            if self.events and (msg := ux("vagus_nerve", "panic_spike")):
                self.events.log(f"{Prisma.RED}{msg}{Prisma.RST}", "BIO")
        elif state == "ZEN":
            cfg = shifts.get("ZEN", {"cor": -0.3, "ser": 0.2})
            self.endo.cortisol = max(0.0, self.endo.cortisol + cfg.get("cor", -0.3))
            self.endo.serotonin = min(1.0, self.endo.serotonin + cfg.get("ser", 0.2))
            if self.events and (msg := ux("vagus_nerve", "lucid_calm")):
                self.events.log(f"{Prisma.GRN}{msg}{Prisma.RST}", "BIO")
        elif state == "MANIC":
            self.mito.adjust_atp(
                shifts.get("MANIC", {}).get("atp", -10.0), "Neural Overclock")

    def apply_environmental_entropy(self, physics_packet):
        vector = safe_get(physics_packet, "vector", {}) or {}
        ent_val = vector.get("ENT", 0.0)
        phi_val = vector.get("PHI", 0.0)
        em_field = math.hypot(ent_val, phi_val)
        target_cfg = self.config_ref or BoneConfig
        cfg = getattr(target_cfg, "BIO", None)
        base_ent_bias = getattr(cfg, "ENTROPY_BASE_BIAS", 0.2)
        shield_cap = getattr(cfg, "SHIELD_MAX_STRENGTH", 0.8)
        shield_mult = getattr(cfg, "SHIELD_MULTIPLIER", 0.1)
        heat_thresh = getattr(cfg, "HEAT_THRESHOLD", 0.8)
        thermal_mult = getattr(cfg, "THERMAL_FEEDBACK_MULT", 5.0)
        base_entropy = base_ent_bias + (ent_val * 1.0)
        shield_strength = min(shield_cap, em_field * shield_mult)
        effective_entropy = base_entropy * (1.0 - shield_strength)
        thermal_feedback = 0.0
        if em_field > heat_thresh:
            thermal_feedback = min(50.0, (em_field - heat_thresh) * thermal_mult)
            if self.events and (msg := ux("entropy_shield", "inductive_heating")):
                self.events.log(f"{Prisma.RED}{msg}{Prisma.RST}", "BIO_WARN")
        total_drain = effective_entropy + thermal_feedback
        if self.biometrics:
            self.biometrics.health = max(0.0, self.biometrics.health - total_drain)
        if shield_strength > 0.2 and self.events and (msg := ux(
                "entropy_shield", "shield_active")):
            self.events.log(
                f"{Prisma.CYN}{msg.format(mitigation=int(shield_strength * 100))}{Prisma.RST}",
                "PHYS")


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
    def __init__(self, state_ref: MitochondrialState, events_ref, config_ref=None):
        self.state = state_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        full_narrative = (
            LoreManifest.get_instance(config_ref=self.cfg).get("BIO_NARRATIVE") or {})
        self.narrative = full_narrative.get("MITO", {})
        self.MAX_SAFE_BURN = getattr(self.cfg.BIO, "MAX_SAFE_BURN", 25.0)
        self.ANAEROBIC_THRESHOLD = getattr(self.cfg.BIO, "ANAEROBIC_THRESHOLD", 40.0)

    def get_status_report(self) -> str:
        atp, ros = self.state.atp_pool, self.state.ros_buildup
        if atp < 5.0:
            key = "NECROSIS"
        elif atp < 20.0:
            key = "GRINDING"
        elif ros > 80.0:
            key = "APOPTOSIS"
        else:
            key = "NOMINAL"
        return getattr(self, "narrative_map", {}).get(key, "").format(cost=0.0, pool=atp)

    def adjust_atp(self, delta: float, reason: str = ""):
        old = self.state.atp_pool
        max_limit = getattr(self.cfg, "MAX_ATP", 100.0)
        atp_collapse = getattr(self.cfg.BIO, "ATP_COLLAPSE", 0.0)
        self.state.atp_pool = max(atp_collapse, min(max_limit, old + delta))
        if reason and (abs(delta) > 5.0 or self.state.atp_pool > 90.0):
            self.events.log(f"[ATP]: {reason} ({delta:+.1f})", "BIO")

    def on_substrate_forged(self, payload: Dict):
        cost = payload.get("cost", 0.0)
        filename = payload.get("file", "unknown")
        self.adjust_atp(-cost, f"Substrate Forging [{filename}]")

    def _get_text(self, key, **kwargs):
        tmpl = self.narrative.get(key, "")
        if not tmpl:
            return ""
        try:
            return tmpl.format(**kwargs)
        except Exception as e:
            print(
                f"{Prisma.RED}[MITO_FORGE] Missing narrative kwargs for '{key}': {e}{Prisma.RST}"
            )
            return tmpl

    def _trigger_anaerobic_bypass(self, raw_cost: float) -> MetabolicReceipt:
        health_burn = 2.0
        self.state.ros_buildup += 2.0
        self.adjust_atp(-20.0, "Anaerobic Burn")
        if self.events and (msg := ux("mito_forge", "anaerobic_bypass")):
            self.events.log(f"{Prisma.MAG}{msg.format(cost=raw_cost)}{Prisma.RST}", "BIO_WARN")
        return MetabolicReceipt(base_cost=raw_cost, drag_tax=0.0, inefficiency_tax=0.0, total_burn=health_burn,
                                waste_generated=2.0, status="ANAEROBIC", symptom="LACTATE_BUILDUP", )

    def process_cycle(self, physics_packet: Any, modifier: float = 1.0) -> MetabolicReceipt:
        if self.state.atp_pool > 95.0 and self.state.ros_buildup < 1.0:
            return MetabolicReceipt(0, 0, 0, 0, 0, "NOMINAL", "Fresh Start")
        cfg = getattr(self.cfg, "BIO", None)
        depth = strict_get(physics_packet, "depth", 0.3)
        connectivity = strict_get(physics_packet, "connectivity", 0.2)
        voltage = float(strict_get(physics_packet, "voltage", 30.0))
        base_cost = safe_get(cfg, "BASE_ATP_YIELD", 2.0) + (
            voltage * safe_get(cfg, "VOLTAGE_TAX_MULT", 0.05))
        cognitive_load_tax = (depth * safe_get(cfg, "DEPTH_TAX_MULT", 2.0)) + (
            connectivity * safe_get(cfg, "CONN_TAX_MULT", 3.0))
        chi = safe_get(physics_packet, "chi", safe_get(physics_packet, "entropy", 0.0))
        if chi > safe_get(cfg, "CHAOS_TAX_THRESHOLD", 0.6):
            chaos_tax = safe_get(cfg, "CHAOS_TAX_MULT", 8.0) * chi
            cognitive_load_tax += chaos_tax
            if self.events and (msg := ux("mito_forge", "chaos_tax")):
                self.events.log(f"{Prisma.RED}{msg.format(tax=chaos_tax)}{Prisma.RST}", "BIO_WARN")
        m_a = safe_get(physics_packet, "m_a", 0.0)
        if (mu := safe_get(physics_packet, "mu", 0.0)) > 0:
            amplification_tax = mu * math.exp(m_a)
            cognitive_load_tax += amplification_tax
            if amplification_tax > 1.0 and self.events:
                self.events.log(
                    f"{Prisma.MAG}[CHECKPOINT]: Amplification Tax applied (+{amplification_tax:.2f} ATP drag){Prisma.RST}",
                    "BIO_WARN")
        safe_vector = getattr(physics_packet, "vector", None) or {}
        liminal_intensity = safe_vector.get("LAMBDA", 0.0)
        if liminal_intensity > 0:
            liminal_tax = liminal_intensity**2
            cognitive_load_tax += liminal_tax
        base_demand = base_cost + (math.log1p(max(0.0, self.state.ros_buildup)) * 2.0)
        atp_crit = getattr(cfg, "ATP_CRITICAL", 20.0) if cfg else 20.0
        is_critical = self.state.atp_pool < atp_crit
        if is_critical:
            cognitive_load_tax = 0.0
            modifier *= 0.5
            if self.events and self.state.retrograde_signal != "HIBERNATING":
                msg = self._get_text("NECROSIS", cost=base_demand, pool=self.state.atp_pool)
                icon = ux("mito_forge", "icon_necrosis")
                if msg:
                    self.events.log(f"{Prisma.VIOLET}{icon}{msg}{Prisma.RST}", "BIO_CRIT")
                self.state.retrograde_signal = "HIBERNATING"
        efficiency = max(0.35, self.state.membrane_potential)
        raw_cost = ((base_demand + cognitive_load_tax) * modifier) / efficiency
        if raw_cost > self.ANAEROBIC_THRESHOLD:
            return self._trigger_anaerobic_bypass(raw_cost)
        if raw_cost > self.MAX_SAFE_BURN:
            excess = raw_cost - self.MAX_SAFE_BURN
            raw_cost = self.MAX_SAFE_BURN
            if self.events:
                msg = ux("mito_forge", "surge_protector")
                if msg:
                    self.events.log(f"{Prisma.CYN}{msg.format(excess=excess)}{Prisma.RST}", "BIO")
        if raw_cost > 15.0 and self.events and random.random() < 0.2:
            msg = self._get_text("GRINDING")
            icon = ux("mito_forge", "icon_grinding")
            if msg:
                self.events.log(f"{Prisma.OCHRE}{icon}{msg}{Prisma.RST}", "BIO_WARN")
        total_metabolic_cost = raw_cost
        psi = float(safe_get(physics_packet, "psi", 0.0))
        waste_generated = 0.0
        psi_mult = safe_get(cfg, "WASTE_PSI_MULT", 5.0)
        chi_mult = safe_get(cfg, "WASTE_CHI_MULT", 5.0)
        volt_div = safe_get(cfg, "WASTE_VOLT_DIV", 20.0)
        base_red = safe_get(cfg, "WASTE_BASE_REDUCTION", 2.0)
        if psi > 0.3 or chi > 0.3:
            waste_generated += (psi * psi_mult) + (chi * chi_mult)
        if voltage > 60.0:
            waste_generated += voltage / volt_div
        waste_generated -= base_red
        waste_generated = max(-self.state.ros_buildup, waste_generated)
        self.state.ros_buildup += waste_generated
        self.adjust_atp(-total_metabolic_cost, "Metabolic Burn")
        if total_metabolic_cost >= self.MAX_SAFE_BURN and not is_critical:
            self.state.membrane_potential = max(0.1, self.state.membrane_potential - 0.005)
        self._apply_adaptive_dynamics()
        status = "LOW_POWER" if is_critical else "RESPIRING"
        if self.state.atp_pool <= safe_get(cfg, "ATP_COLLAPSE", 0.0):
            status = "NECROSIS"
            if self.events:
                self.events.publish("SYSTEM_STARVING", {})
        return MetabolicReceipt(
            base_cost=round(base_demand, 2),
            drag_tax=round(cognitive_load_tax, 2),
            inefficiency_tax=round(total_metabolic_cost - (base_demand + cognitive_load_tax), 2),
            total_burn=round(total_metabolic_cost, 2),
            waste_generated=round(waste_generated, 2),
            status=status,
            symptom=self.state.retrograde_signal,
        )

    def _apply_adaptive_dynamics(self):
        cfg = getattr(self.cfg, "BIO", None)
        ros_sig = safe_get(cfg, "ROS_SIGNAL", 5.0)
        ros_dam = safe_get(cfg, "ROS_DAMAGE", 25.0)
        ros_purge = safe_get(cfg, "ROS_PURGE", 40.0)
        if self.state.ros_buildup < ros_sig:
            self.state.membrane_potential = max(0.5, self.state.membrane_potential - 0.001)
            self.state.retrograde_signal = "QUIET"
        elif self.state.ros_buildup < ros_dam:
            self.state.membrane_potential = min(1.0, self.state.membrane_potential + 0.005)
            self.state.retrograde_signal = "MITOHORMESIS_ACTIVE"
            self.state.ros_buildup = max(0.0, self.state.ros_buildup - 0.5)
        else:
            """A stock without a floor accumulates infinite debt. -Meadows"""
            self.state.membrane_potential = max(0.1, self.state.membrane_potential - 0.02)
            self.state.retrograde_signal = "OXIDATIVE_STRESS"
        if self.state.ros_buildup > ros_purge:
            self._trigger_mitophagy()

    def adapt(self, stress_level: float):
        old_potential = self.state.membrane_potential
        if stress_level > 5.0:
            self.state.membrane_potential = max(0.4, self.state.membrane_potential - 0.15)
            msg = ux("mito_forge", "adaptation_stress")
            if msg:
                self.events.log(
                    f"{Prisma.RED}{msg.format(stress=stress_level, old=old_potential, new=self.state.membrane_potential)}{Prisma.RST}",
                    "BIO",
                )
        elif stress_level > 1.0:
            self.state.membrane_potential = min(1.5, self.state.membrane_potential + 0.05)
            if random.random() < 0.2 and (msg := ux("mito_forge", "adaptation_hormetic")):
                self.events.log(f"{Prisma.GRN}{msg}{Prisma.RST}", "BIO")

    def _trigger_mitophagy(self):
        cfg = getattr(self.cfg, "BIO", None)
        self.adjust_atp(-safe_get(cfg, "MITOPHAGY_COST", 30.0), "Mitophagy")
        self.state.ros_buildup = 0.0
        self.state.membrane_potential = 0.6
        self.state.retrograde_signal = "MITOPHAGY_RESET"
        msg = self._get_text("APOPTOSIS")
        icon = ux("mito_forge", "icon_apoptosis")
        if msg:
            self.events.log(f"{Prisma.RED}{icon}[MITO]: {msg}{Prisma.RST}", "BIO_CRIT")

    def apply_inheritance(self, traits: dict):
        if not traits:
            return
        if traits.get("high_metabolism"):
            self.state.membrane_potential = 1.1
            self.events.log("[MITO]: Ancestral High Metabolism activated.", "GENETICS")

    def cellular_repair(self, survival_streak: int, g_pool: int, inherited_scars: dict) -> Tuple[bool, int, str]:
        """Epigenetic Plasticity: Earn out of ancestral trauma."""
        if survival_streak < 50 or self.state.ros_buildup > 10.0 or not inherited_scars:
            return False, g_pool, ""
        if g_pool >= 1:
            healed_scar = random.choice(list(inherited_scars.keys()))
            del inherited_scars[healed_scar]
            g_pool -= 1
            msg = f"Epigenetic Plasticity Achieved. Ancestral scar '{healed_scar}' permanently erased. (-1 Glimmer)"
            if self.events:
                self.events.log(f"{Prisma.MAG}✨ [MITO]: {msg}{Prisma.RST}", "BIO_HEAL")
            return True, g_pool, msg
        return False, g_pool, ""

class DigestiveTrack:
    def __init__(self, bio_system_ref: BioSystem, lexicon_ref=None, config_ref=None):
        self.bio = bio_system_ref
        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        base_map = (LoreManifest.get_instance(config_ref=self.cfg).get(
            "BODY_CONFIG", "ENZYME_MAP") or {})
        self.enzyme_map = dict(base_map)
        if "heavy" not in self.enzyme_map:
            self.enzyme_map.update({
                "heavy": "CELLULASE",
                "constructive": "CHITINASE",
                "aerobic": "LIGNASE",
                "meat": "PROTEASE",
            })
        self.SAMPLING_THRESHOLD = getattr(self.cfg.BIO, "SAMPLING_THRESHOLD", 1000)
        self.BASE_WORD_VALUE = getattr(self.cfg.BIO, "BASE_WORD_VALUE", 0.5)
        self.COMPLEX_WORD_BONUS = getattr(self.cfg.BIO, "COMPLEX_WORD_BONUS", 2.0)
        self.CLICHE_TAX_RATE = getattr(self.cfg.BIO, "CLICHE_TAX_RATE", 0.5)

    def harvest(self, phys: Any, logs: List[str]) -> Tuple[str, float, int]:
        clean_words = getattr(phys, "clean_words", [])
        if not clean_words:
            return "NONE", 0.0, 0
        words_to_process, scaling_factor = self._sample_input(clean_words, logs)
        raw_yield, found_enzymes, cliche_tax, raw_hits = self._digest_words(
            words_to_process)
        total_atp = raw_yield * scaling_factor
        scaled_tax = cliche_tax * scaling_factor
        total_hits = int(raw_hits * scaling_factor)
        if scaled_tax > 0:
            total_atp = max(0.0, total_atp - scaled_tax)
            if getattr(self.bio, "endo", None):
                self.bio.endo.cortisol = min(1.0, self.bio.endo.cortisol + (scaled_tax * 0.02))
            if msg := ux("digestive_track", "cliche_tax"):
                logs.append(f"{Prisma.OCHRE}{msg.format(tax=scaled_tax)}{Prisma.RST}")
        v_thresh = getattr(self.cfg.BIO, "VOLTAGE_BONUS_THRESHOLD", 8.0)
        p_bonus = getattr(self.cfg.BIO, "PROTEASE_BONUS", 5.0)
        if getattr(phys, "voltage", 0.0) > v_thresh and found_enzymes:
            found_enzymes.append("PROTEASE")
            total_atp += p_bonus
        if found_enzymes:
            dominant = Counter(found_enzymes).most_common(1)[0][0]
        else:
            dominant = "NONE"
        return dominant, total_atp, total_hits

    def _sample_input(self, words: List[str], logs: List[str]) -> Tuple[List[str], float]:
        count = len(words)
        if count > self.SAMPLING_THRESHOLD:
            factor = count / self.SAMPLING_THRESHOLD
            if random.random() < 0.1 and (msg := ux("digestive_track", "mass_input")):
                logs.append(
                    f"{Prisma.GRY}{msg.format(count=count, factor=factor)}{Prisma.RST}")
            return random.sample(words, self.SAMPLING_THRESHOLD), factor
        return words, 1.0

    def _digest_words(self, words: List[str]) -> Tuple[float, List[str], float, int]:
        word_counts = Counter(words)
        cfg = getattr(self.cfg, "BIO", None)
        min_len = safe_get(cfg, "MIN_WORD_LENGTH", 4)
        comp_len = safe_get(cfg, "COMPLEX_WORD_LENGTH", 7)
        valid_words = {w: c for w, c in word_counts.items() if len(w) >= min_len}
        hits = sum(valid_words.values())
        if not valid_words or not self.lex:
            return sum(c * self.BASE_WORD_VALUE for c in valid_words.values()), [], 0.0, hits
        user_set = set(valid_words.keys())
        antigen_set = self.lex.get("antigen")
        kinetic_set = self.lex.get("kinetic") | self.lex.get("explosive")
        atp_yield = 0.0
        enzymes = []
        cliche_tax = 0.0
        antigens_found = user_set.intersection(antigen_set)
        kinetics_found = user_set.intersection(kinetic_set)
        for word, count in valid_words.items():
            if word in antigens_found:
                cliche_tax += self.CLICHE_TAX_RATE * count
                continue
            val = self.COMPLEX_WORD_BONUS if len(word) > comp_len else self.BASE_WORD_VALUE
            log_mult = 1.0 + math.log(count)
            if word in kinetics_found:
                atp_yield += (val * 1.5) * log_mult
            else:
                cat = self.lex.get_current_category(word)
                if not cat or cat == "void":
                    atp_yield += self.BASE_WORD_VALUE * count
                else:
                    atp_yield += val * log_mult
                    if (enzyme := self.enzyme_map.get(cat, "AMYLASE")) != "AMYLASE":
                        enzymes.append(enzyme)
        return atp_yield, enzymes, cliche_tax, hits


class EndocrineRegulator:
    def __init__(self, bio_system_ref: BioSystem):
        self.bio = bio_system_ref

    def get_metabolic_modifier(self, phys: Any, logs: List[str]) -> float:
        chem = self.bio.endo
        modifier = 1.0
        if chem.cortisol > 0.5:
            stress_tax = 1.0 + (chem.cortisol * 0.5)
            modifier *= stress_tax
            if random.random() < 0.3 and (msg := ux("endocrine_regulator", "cortisol_spike")):
                logs.append(f"{Prisma.RED}{msg.format(tax=stress_tax)}{Prisma.RST}")
        if chem.adrenaline > 0.6:
            modifier *= 0.5
            if msg := ux("endocrine_regulator", "adrenaline_surge"):
                logs.append(f"{Prisma.YEL}{msg}{Prisma.RST}")
        if chem.dopamine > 0.7:
            modifier *= 0.8
        if (voltage := getattr(phys, "voltage", 0.0)) > 15.0:
            modifier *= 1.2
            if msg := ux("endocrine_regulator", "voltage_gap"):
                logs.append(f"{Prisma.MAG}{msg.format(voltage=voltage)}{Prisma.RST}")
        return modifier

class BioFeedback:
    def __init__(self, bio_system_ref: BioSystem, config_ref=None):
        self.bio = bio_system_ref
        self.cfg = config_ref or BoneConfig
        self.consecutive_autophagy = 0

    def check_vital_signs(self, phys: Any, stamina: float, logs: List[str]) -> str:
        b = self.bio.biometrics
        if not b:
            if msg := ux("bio_feedback", "interface_lost"):
                logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"
        voltage = float(safe_get(phys, "voltage", 0.0))
        cfg = getattr(self.cfg, "BIO", None)
        min_health = getattr(cfg, "AUTOPHAGY_MIN_HEALTH", 10.0)
        v_overload = getattr(cfg, "VOLTAGE_OVERLOAD", 30.0)
        if stamina <= 0:
            if b.health > min_health and self.consecutive_autophagy < 3:
                b.health -= getattr(cfg, "AUTOPHAGY_BURN", 5.0)
                self.consecutive_autophagy += 1
                if msg := ux("bio_feedback", "autophagy"):
                    logs.append(f"{Prisma.MAG}{msg}{Prisma.RST}")
                return "AUTOPHAGY"
            if msg := ux("bio_feedback", "fuel_depleted"):
                logs.append(f"{Prisma.RED}{msg}{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"
        self.consecutive_autophagy = max(0, self.consecutive_autophagy - 1)
        if voltage > v_overload:
            if msg := ux("bio_feedback", "voltage_overload"):
                logs.append(f"{Prisma.RED}{msg.format(voltage=voltage)}{Prisma.RST}")
            return "MAUSOLEUM_CLAMP"
        return "CLEAR"

    def perform_maintenance(self, text: str, phys: Any, logs: List[str], tick: int):
        cfg = getattr(self.cfg, "BIO", None)
        if len(text) > safe_get(cfg, "BUFFER_WARN_LIMIT", 10000) and (msg := ux("bio_feedback", "large_buffer")):
            logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
        drag = float(safe_get(phys, "narrative_drag", 0.0))
        sludge_thresh = safe_get(cfg, "SLUDGE_DRAG_THRESH", 8.0)
        sludge_mod = safe_get(cfg, "SLUDGE_TICK_MOD", 10)
        if drag > sludge_thresh and tick % sludge_mod == 0:
            if msg := ux("bio_feedback", "clearing_sludge"):
                logs.append(f"{Prisma.OCHRE}{msg.format(drag=drag)}{Prisma.RST}")
            safe_set(phys, "narrative_drag", max(1.0, drag - safe_get(cfg, "SLUDGE_DRAG_REDUCTION", 2.0)))

class SemanticEndocrinologist:
    def __init__(self, memory_ref, lexicon_ref):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.last_topics = deque(maxlen=3)

    def assess(self, clean_words: List[str], physics: Any) -> SemanticSignal:
        if not clean_words:
            return SemanticSignal()
        cortical_set = set()
        graph_ref = {}
        if self.mem:
            cortical_set = set(getattr(self.mem, "cortical_stack", []))
            graph_ref = getattr(self.mem, "graph", {})
        safe_len = max(1, len(clean_words))
        novel_count = sum(1 for w in clean_words if len(w) > 4 and w not in cortical_set)
        hits = sum(1 for w in clean_words if w in graph_ref) if graph_ref else 0
        novelty_score = min(1.0, novel_count / safe_len)
        resonance_score = min(1.0, hits / safe_len) if graph_ref else 0.0
        valence_score = 0.0
        if self.lex and hasattr(self.lex, "get_valence"):
            valence_score = self.lex.get_valence(clean_words)
        coherence_score = getattr(physics, "kappa", 0.5)
        return SemanticSignal(
            novelty=novelty_score,
            resonance=resonance_score,
            valence=valence_score,
            coherence=coherence_score,
        )

class SomaticLoop:
    def __init__(self, bio_system_ref: BioSystem, memory_ref=None, lexicon_ref=None, events_ref=None, config_ref=None, ):
        self.bio = bio_system_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        self.digestive = DigestiveTrack(self.bio, lexicon_ref=lexicon_ref, config_ref=self.cfg)
        self.regulator = EndocrineRegulator(self.bio)
        self.feedback = BioFeedback(self.bio, config_ref=self.cfg)
        self.semantic_doctor = SemanticEndocrinologist(memory_ref, lexicon_ref)
        self.synesthesia = SynestheticCortex(self.bio, config_ref=self.cfg)
        self.narrative_data = (LoreManifest.get_instance(config_ref=self.cfg).get("BIO_NARRATIVE") or {})
        if not self.narrative_data:
            if hasattr(self.events, "log"):
                self.events.log(
                    f"{Prisma.OCHRE}[BODY]: Warning - BIO_NARRATIVE missing.{Prisma.RST}",
                    "SYS",
                )
            self.narrative_data = {
                "symptoms": {},
                "organs": {},
                "GLIMMER": {},
                "GOVERNOR": {},
            }
        if getattr(self.bio, "endo", None):
            self.bio.endo.narrative_data = self.narrative_data
        if getattr(self.bio, "governor", None):
            self.bio.governor.narrative_data = self.narrative_data

    def digest_cycle(
        self,
        text: str,
        physics_data: Any,
        fb_dict: Dict,
        health: float,
        stamina: float,
        stress_modifier: float,
        tick_count: int = 0,
        circadian_bias: Dict = None,
    ) -> Dict:
        text = str(text or "")
        phys = physics_data
        logs = []
        if not (b := self.bio.biometrics):
            return self._package_result(
                "NECROSIS", ["Critical: Biological interface disconnected."])
        max_health = float(safe_get(self.cfg, "MAX_HEALTH", 100.0))
        max_stamina = float(safe_get(self.cfg, "MAX_STAMINA", 100.0))
        b.health = max(0.0, min(max_health, health))
        b.stamina = max(0.0, min(max_stamina, stamina))
        if hasattr(self.bio, "apply_environmental_entropy"):
            self.bio.apply_environmental_entropy(phys)
        modifier = self.regulator.get_metabolic_modifier(phys, logs)
        delta_silence = float(safe_get(phys, "silence", 0.0))
        if delta_silence > 0.6:
            drag_relief = delta_silence * 2.0
            stamina_recovery = delta_silence * 5.0
            current_drag = float(safe_get(phys, "narrative_drag", 1.0))
            safe_set(phys, "narrative_drag", max(1.0, current_drag - drag_relief))
            b.stamina = min(max_stamina, b.stamina + stamina_recovery)
            if msg := ux("somatic_loop", "silence_heals"):
                logs.append(f"{Prisma.CYN}{msg.format(recovery=stamina_recovery)}{Prisma.RST}")
        receipt = self.bio.mito.process_cycle(phys, modifier=modifier)
        if receipt.status == "ANAEROBIC":
            b.health = max(0.0, b.health - receipt.total_burn)
            msg = ux("somatic_loop", "anaerobic_burn")
            logs.append(
                f"{Prisma.RED}{msg.format(burn=receipt.total_burn)}{Prisma.RST}")
        safety_status = self.feedback.check_vital_signs(phys, b.stamina, logs)
        if safety_status == "MAUSOLEUM_CLAMP":
            return self._package_result(receipt.status, logs)
        elif safety_status == "AUTOPHAGY":
            b.stamina = 10.0
        total_yield = 0.0
        enzyme = "NONE"
        clean_words = getattr(phys, "clean_words", [])
        if self.bio.lichen:
            sugar, photo_log = self.bio.lichen.photosynthesize(
                phys, clean_words, tick_count)
            if sugar > 0:
                total_yield += sugar
            if photo_log:
                logs.append(photo_log)
        soma_enzyme, soma_yield, harvest_hits = self.digestive.harvest(phys, logs)
        total_yield += soma_yield
        enzyme = soma_enzyme if enzyme == "NONE" else enzyme
        self.bio.mito.adjust_atp(total_yield, "Symbiotic Yield")
        self.feedback.perform_maintenance(text, phys, logs, tick_count)
        semantic_sig = self.semantic_doctor.assess(clean_words, phys)
        fb_dict.update({
            "PSI": getattr(phys, "psi", 0.0),
            "CHI": getattr(phys, "chi", 0.0),
            "VALENCE": getattr(phys, "valence", 0.0),
            "INTEGRITY": semantic_sig.coherence,
            "NOVELTY": semantic_sig.novelty,
        })
        chem_state = self.bio.endo.metabolize(
            feedback=fb_dict,
            health=b.health,
            stamina=b.stamina,
            ros_level=self.bio.mito.state.ros_buildup,
            receipt=receipt,
            harvest_hits=harvest_hits,
            stress_mod=stress_modifier,
            enzyme_type=enzyme,
            circadian_bias=circadian_bias,
            semantic_signal=semantic_sig,
        )
        return self._package_result(receipt.status, logs, chem_state, enzyme)

    def _package_result(self, resp_status, logs, chem_state=None, enzyme="NONE"):
        atp_val = self.bio.mito.state.atp_pool if getattr(self.bio, "mito", None) else 60.0
        stam_val = self.bio.biometrics.stamina if getattr(self.bio, "biometrics", None) else 100.0
        return {
            "respiration": resp_status,
            "is_alive": resp_status in ("RESPIRING", "ANAEROBIC"),
            "logs": logs,
            "chemistry": chem_state or {},
            "enzyme": enzyme,
            "atp": atp_val,
            "stamina": stam_val,
        }

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
    config_ref: Any = None
    _REACTION_MAP: Dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.cfg = self.config_ref or BoneConfig
        body_config = (LoreManifest.get_instance(config_ref=self.cfg).get("BODY_CONFIG")
                       or {})
        self._REACTION_MAP = body_config.get("REACTION_MAP", {})
        self._KEY_MAP = {
            "ADR": "adrenaline",
            "COR": "cortisol",
            "OXY": "oxytocin",
            "DOP": "dopamine",
            "SER": "serotonin",
            "MEL": "melatonin"
        }
        self._CIRCADIAN_SCHEDULE = body_config.get("CIRCADIAN_SCHEDULE", [])
        self._CIRCADIAN_NIGHT = body_config.get("CIRCADIAN_NIGHT", [{
            "MEL": 0.3,
            "COR": -0.1
        }, "LUNAR", ""])

    @staticmethod
    def _clamp(val: float) -> float:
        return max(0.0, min(1.0, val))

    def calculate_circadian_bias(self) -> Tuple[Dict[str, float], Optional[str]]:
        hour = time.localtime().tm_hour
        circ = self.narrative_data.get("CIRCADIAN", {})
        for s, e, bias, key, default in getattr(self, "_CIRCADIAN_SCHEDULE", []):
            if s <= hour < e:
                return bias, circ.get(key, default)
        default_night = [{"MEL": 0.3, "COR": -0.1}, "LUNAR", ""]
        night_bias, night_key, night_default = getattr(self, "_CIRCADIAN_NIGHT", default_night)
        return night_bias, circ.get(night_key, night_default)

    def _apply_enzyme_reaction(self, enzyme_type: str, harvest_hits: int):
        if harvest_hits > 0:
            satiety_dampener = max(0.1, 1.0 - self.dopamine)
            base_reward = math.log(harvest_hits + 1) * 0.15
            final_reward = base_reward * satiety_dampener
            self.dopamine += final_reward
            self.cortisol -= final_reward * 0.4
        if enzyme_type == "DECRYPTASE":
            self.serotonin = min(1.0, self.serotonin + 0.15)
            self.cortisol = max(0.0, self.cortisol - 0.2)
        if impact := self._REACTION_MAP.get(enzyme_type):
            for k, v in impact.items():
                if attr := self._KEY_MAP.get(k):
                    setattr(self, attr, getattr(self, attr) + v)

    def _apply_environmental_pressure(self, feedback: Dict, health: float, stamina: float, ros_level: float,
                                      stress_mod: float, ):
        bio_cfg = getattr(self.cfg, "BIO", None)
        reward_large = safe_get(bio_cfg, "REWARD_LARGE", 0.2)
        reward_med = safe_get(bio_cfg, "REWARD_MEDIUM", 0.1)
        decay = safe_get(bio_cfg, "DECAY_RATE", 0.01)
        if feedback.get("STATIC", 0) > 0.6:
            self.cortisol += reward_large * stress_mod
        if feedback.get("INTEGRITY", 0) > 0.8:
            self.dopamine += reward_med
        else:
            self.dopamine *= max(0.0, 1.0 - decay)
        if stamina < 20.0:
            self.cortisol += reward_med * stress_mod
            self.dopamine -= reward_med
        if ros_level > 20.0:
            self.cortisol += reward_large * stress_mod
        if health < 30.0 or feedback.get("STATIC", 0) > 0.8:
            self.adrenaline += reward_large * stress_mod
        else:
            self.adrenaline *= max(0.0, 1.0 - (decay * 5))
        psi = feedback.get("PSI", 0.0)
        chi = feedback.get("CHI", feedback.get("ENTROPY", 0.0))
        valence = feedback.get("VALENCE", 0.0)
        if psi > 0.6:
            self.adrenaline += 0.4
            self.melatonin += 0.2 * psi
        if chi > 0.6:
            self.cortisol += (0.6 * chi) * stress_mod
            self.serotonin -= 0.2
        if valence > 0.5:
            self.oxytocin += 0.5 * valence
            self.serotonin += 0.3
            self.cortisol -= 0.3
        elif valence < -0.5:
            self.cortisol += abs(valence) * 0.4
            self.dopamine -= 0.2

    def _apply_semantic_pressure(self, signal: SemanticSignal):
        if signal.novelty > 0.3:
            self.dopamine += signal.novelty * 0.3
        if signal.resonance > 0.2:
            self.oxytocin += signal.resonance * 0.4
            self.cortisol -= signal.resonance * 0.2
        if signal.valence > 0.3:
            self.serotonin += signal.valence * 0.3
            self.oxytocin += signal.valence * 0.2
        elif signal.valence < -0.3:
            self.cortisol += abs(signal.valence) * 0.2
        if signal.coherence > 0.7:
            self.adrenaline -= 0.1
            self.cortisol -= 0.1

    def _maintain_homeostasis(self, social_context: bool):
        dampener = 0.2
        bio_cfg = getattr(self.cfg, "BIO", None)
        reward_med = safe_get(bio_cfg, "REWARD_MEDIUM", 0.1)
        reward_small = safe_get(bio_cfg, "REWARD_SMALL", 0.05)
        if self.serotonin > 0.5:
            excess = self.serotonin - 0.5
            self.cortisol -= excess * 0.2 * dampener
        if social_context:
            self.oxytocin += reward_med
            self.cortisol -= reward_med
        if self.cortisol > 0.6:
            suppression = (self.cortisol - 0.6) * 0.5
            self.oxytocin -= suppression * dampener
        if self.oxytocin > 0.5:
            relief = (self.oxytocin - 0.5) * 0.8
            self.cortisol -= relief * dampener
        if self.adrenaline < 0.2:
            self.melatonin += reward_small / 2.0
        elif self.adrenaline > 0.8:
            self.melatonin = 0.0

    def check_for_glimmer(self, feedback: Dict, harvest_hits: int) -> Optional[str]:
        glimmer_text = self.narrative_data.get("GLIMMER", {})
        cfg = getattr(getattr(self, "cfg", BoneConfig), "BIO", None)
        int_thresh = safe_get(cfg, "GLIMMER_INTEGRITY_THRESH", 0.85)
        nov_thresh = safe_get(cfg, "GLIMMER_NOVELTY_THRESH", 0.8)
        harv_min = safe_get(cfg, "GLIMMER_HARVEST_MIN", 2)
        dop_min = safe_get(cfg, "GLIMMER_DOPAMINE_MIN", 0.7)
        if feedback.get("INTEGRITY", 0) > int_thresh:
            self.glimmers += 1
            self.serotonin += 0.2
            return glimmer_text.get("INTEGRITY", "")
        if feedback.get("NOVELTY", 0) > nov_thresh:
            self.glimmers += 1
            self.dopamine += 0.1
            return glimmer_text.get("DISCOVERY",
                                    "GLIMMER: A novel connection formed. Discovery.")
        if harvest_hits > harv_min and self.dopamine > dop_min:
            self.glimmers += 1
            self.oxytocin += 0.2
            return glimmer_text.get("ENTHUSIASM", "")
        return None

    def metabolize(self, feedback, health, stamina, ros_level=0.0, receipt=None, social_context=False, enzyme_type=None,
                   harvest_hits=0, stress_mod=1.0, circadian_bias=None, semantic_signal=None, ):
        if circadian_bias:
            for k, v in circadian_bias.items():
                if hasattr(self, attr_name := self._KEY_MAP.get(k, k.lower())):
                    setattr(self, attr_name, getattr(self, attr_name) + v)
        self._apply_enzyme_reaction(enzyme_type, harvest_hits)
        self._apply_environmental_pressure(feedback, health, stamina, ros_level, stress_mod)
        if receipt and receipt.waste_generated > 1.0:
            self.cortisol += 0.1
        if receipt and receipt.status == "ANAEROBIC":
            self.adrenaline += 0.2
        if semantic_signal:
            self._apply_semantic_pressure(semantic_signal)
        self._maintain_homeostasis(social_context)
        glimmer_msg = self.check_for_glimmer(feedback, harvest_hits)
        for chem in ("dopamine", "oxytocin", "cortisol", "serotonin", "adrenaline", "melatonin"):
            setattr(self, chem, self._clamp(getattr(self, chem)))
        state = self.get_state()
        if glimmer_msg:
            state["glimmer_msg"] = glimmer_msg
        return state

    def get_state(self) -> Dict[str, Any]:
        return {"DOP": round(self.dopamine, 2), "OXY": round(self.oxytocin, 2), "COR": round(self.cortisol, 2),
                "SER": round(self.serotonin, 2), "ADR": round(self.adrenaline, 2), "MEL": round(self.melatonin, 2)}

class PIDController:
    def __init__(self, kp, ki, kd, setpoint, output_limits=(-10.0, 10.0)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.min_out, self.max_out = output_limits
        self._integral = 0.0
        self._last_error = 0.0
        self._first_run = True

    def reset(self):
        self._integral = 0.0
        self._last_error = 0.0
        self._first_run = True

    def update(self, measurement: float, dt: float = 1.0, target_override: Optional[float] = None) -> float:
        safe_dt = max(0.01, dt)
        active_setpoint = target_override if target_override is not None else self.setpoint
        error = active_setpoint - measurement
        if self._first_run:
            self._last_error = error
            self._first_run = False
        P = self.kp * error
        if self.ki != 0:
            self._integral += error * safe_dt
            self._integral = max(self.min_out / self.ki, min(self.max_out / self.ki, self._integral))
        else:
            self._integral = 0.0
        I = self.ki * self._integral
        derivative = (error - self._last_error) / safe_dt
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
    config_ref: Any = None

    def __post_init__(self):
        self.cfg = self.config_ref or BoneConfig
        self.STATE_THRESHOLDS = getattr(self.cfg.BIO, "GOVERNOR_THRESHOLDS", [])
        pid_cfg = getattr(self.cfg.BIO, "PID_SETTINGS", {})
        v_cfg = pid_cfg.get("VOLTAGE", {"kp": 0.6, "ki": 0.05, "kd": 0.2, "setpoint": 10.0})
        d_cfg = pid_cfg.get("DRAG", {"kp": 0.4, "ki": 0.1, "kd": 0.1, "setpoint": 1.5})
        self.voltage_pid = PIDController(kp=v_cfg["kp"], ki=v_cfg["ki"], kd=v_cfg["kd"], setpoint=v_cfg["setpoint"])
        self.drag_pid = PIDController(kp=d_cfg["kp"], ki=d_cfg["ki"], kd=d_cfg["kd"], setpoint=d_cfg["setpoint"])
        self._sorted_thresholds = sorted(self.STATE_THRESHOLDS, key=lambda x: x[3], reverse=True)

    def recalibrate(self, target_voltage: float, target_drag: float):
        self.voltage_pid.setpoint = target_voltage
        self.drag_pid.setpoint = target_drag

    def regulate(self, physics: Any, dt: float, endocrine_state: Optional[Any] = None) -> Tuple[float, float]:
        safe_dt = max(0.001, dt)
        energy_dict = safe_get(physics, "energy") or {}
        space_dict = safe_get(physics, "space") or {}
        v_val = float(safe_get(physics, "voltage") or energy_dict.get("voltage", 0.0))
        d_val = float(
            safe_get(physics, "narrative_drag")
            or space_dict.get("narrative_drag", 0.0))
        if endocrine_state:
            adr_spike = getattr(endocrine_state, "adrenaline", 0.0) * 2.0
            active_setpoint = self.voltage_pid.setpoint + adr_spike
            deadband = 1.0 + (getattr(endocrine_state, "cortisol", 0.0) * 2.0)
            v_error = active_setpoint - v_val
            if abs(v_error) > deadband:
                updated_voltage = self.voltage_pid.update(v_val, safe_dt, target_override=active_setpoint)
            else:
                updated_voltage = 0.0
        else:
            updated_voltage = self.voltage_pid.update(v_val, safe_dt)
        updated_drag = self.drag_pid.update(d_val, safe_dt)
        return updated_voltage, updated_drag

    def assess(self, physics_packet) -> Tuple[bool, float]:
        curr_v = float(safe_get(physics_packet, "voltage", 0.0))
        curr_d = float(safe_get(physics_packet, "narrative_drag", 0.0))
        dist_v = abs(curr_v - self.voltage_pid.setpoint)
        dist_d = abs(curr_d - self.drag_pid.setpoint)
        is_safe = (dist_v < 3.0) and (dist_d < 1.5)
        return is_safe, math.sqrt(dist_v**2 + dist_d**2)

    @staticmethod
    def get_stress_modifier(tick_count):
        return 0.0 if tick_count <= 2 else (0.5 if tick_count <= 5 else 1.0)

    @staticmethod
    def calculate_stress(health: float, ros_buildup: float) -> float:
        base_stress = 1.0 + max(0.0, (50.0 - health) * 0.01) + max(
            0.0, (ros_buildup - 50.0) * 0.01)
        return round(min(3.0, base_stress), 2)

    def set_override(self, target_mode):
        valid = {"COURTYARD", "LABORATORY", "FORGE", "SANCTUARY"}
        gov_text = self.narrative_data.get("GOVERNOR", {})
        if target_mode in valid:
            self.mode = target_mode
            self.manual_override = True
            msg_tmpl = gov_text.get("OVERRIDE", "")
            return msg_tmpl.format(mode=target_mode) if msg_tmpl else ""
        return gov_text.get("INVALID", "")

    def _check_override_safety(self, physics: Dict, gov_text: Dict) -> Optional[str]:
        current_voltage = float(safe_get(physics, "voltage", 0.0))
        gov_crit = safe_get(getattr(self.cfg, "BIO", None), "GOV_VOLTAGE_CRITICAL", 25.0)
        if current_voltage > gov_crit:
            self.manual_override = False
            return gov_text.get("OVERRIDE_CLEARED", "")
        return None

    def shift(self,
              physics: Dict,
              _voltage_history: List[float],
              current_tick: int = 0) -> Optional[str]:
        gov_text = self.narrative_data.get("GOVERNOR", {})
        if self.manual_override:
            return self._check_override_safety(physics, gov_text)
        if (current_tick - self.last_shift_tick) < self.hysteresis_duration:
            return None
        proposed = self._evaluate_state(physics, _voltage_history)
        if proposed != self.mode:
            self.mode = proposed
            self.last_shift_tick = current_tick
            return self._get_shift_message(proposed, gov_text, physics)
        return None

    def _evaluate_state(self, physics: Dict, v_history: List[float]) -> str:
        volts = float(safe_get(physics, "voltage", 0.0))
        drag = float(safe_get(physics, "narrative_drag", 0.0))
        gov_high = getattr(self.cfg.BIO, "GOV_VOLTAGE_HIGH", 18.0)
        if volts > gov_high and float(safe_get(physics, "beta_index", 0.0)) > 1.5:
            return "SANCTUARY"
        v_velocity = (v_history[-1] - v_history[-2]) if len(v_history) >= 2 else 0.0
        if volts > 8.0 and v_velocity > 1.0:
            return "FORGE"
        for v_min, d_min, mode, _ in self._sorted_thresholds:
            if volts >= v_min and drag >= d_min:
                return mode
        return "COURTYARD"

    @staticmethod
    def _get_shift_message(mode: str, text_map: Dict, physics: Any) -> str:
        shift_cfg = (LoreManifest.get_instance().get("BODY_CONFIG", "GOVERNOR_SHIFT")
                     or {})
        raw_colors = shift_cfg.get("COLORS", {})
        defaults = shift_cfg.get("DEFAULTS", {})
        colors = {k: getattr(Prisma, v, Prisma.WHT) for k, v in raw_colors.items()}
        lookup = {"LABORATORY": "LAB", "COURTYARD": "CLEAR"}.get(mode, mode)
        tmpl = text_map.get(lookup, defaults.get(mode, ""))
        try:
            return tmpl.format(
                color=colors.get(mode, Prisma.WHT),
                reset=Prisma.RST,
                volts=safe_get(physics, "voltage", 0.0),
                beta=safe_get(physics, "beta_index", 0.0),
            )
        except Exception as e:
            print(
                f"{Prisma.RED}[GOVERNOR] Shift message format error for '{mode}': {e}{Prisma.RST}"
            )
            return f"{colors.get(mode, '')}{defaults.get(mode, '')}{Prisma.RST}"

@dataclass
class BiologicalImpulse:
    cortisol_delta: float = 0.0
    oxytocin_delta: float = 0.0
    dopamine_delta: float = 0.0
    adrenaline_delta: float = 0.0
    stamina_impact: float = 0.0
    somatic_reflex: str = ""

@dataclass
class Qualia:
    color_code: str
    somatic_sensation: str
    tone: str
    internal_monologue_hint: str

class SynestheticCortex:
    def __init__(self, bio_ref, config_ref=None):
        self.bio = bio_ref
        self.cfg = config_ref or BoneConfig
        self.last_reflex = None
        self.library = LoreManifest.get_instance(
            config_ref=self.cfg).get("SOMATIC_LIBRARY") or {}

    def perceive(self,  physics: Dict,  traits: Any = None, latency: float = 0.0) -> BiologicalImpulse:
        impulse = BiologicalImpulse()
        impulse.stamina_impact -= 1.0
        cortex_cfg = getattr(self.cfg, "CORTEX", None)
        base_sens = safe_get(cortex_cfg, "BASE_SENSITIVITY", 1.0)
        if traits:
            curiosity = getattr(traits, "curiosity", 0.5)
            discipline = getattr(traits, "discipline", 0.5)
            base_sens *= 1.0 + curiosity - discipline
        sens = max(0.0, base_sens)
        valence = safe_get(physics, "valence", 0.0)
        counts = safe_get(physics, "counts") or safe_get(
            safe_get(physics, "matter", {}), "counts", {})
        voltage = safe_get(physics, "voltage", 0.0)
        drag = safe_get(physics, "narrative_drag", 0.0)
        if drag > 3.0:
            impulse.stamina_impact -= drag * 0.4
        if valence < -0.5:
            impulse.cortisol_delta += abs(valence) * sens
        antigen_count = counts.get("antigen", 0)
        if antigen_count > 0:
            toxin_weight = getattr(self.cfg, "TOXIN_WEIGHT", 1.0)
            toxin_scalar = safe_get(cortex_cfg, "TOXIN_SCALAR", 0.5)
            raw_tox = antigen_count * (toxin_weight * 0.2)
            impulse.cortisol_delta += min(toxin_scalar, raw_tox)
            impulse.somatic_reflex = "Shiver (Rejection)"
        elif drag > safe_get(cortex_cfg, "DRAG_STRESS_THRESHOLD", 8.0):
            impulse.cortisol_delta += 0.05
            impulse.stamina_impact -= 2.0
        else:
            if valence > 0.4:
                impulse.oxytocin_delta += valence * sens
            if counts.get("sacred", 0) > 0:
                impulse.oxytocin_delta += 0.1
                impulse.somatic_reflex = "Warmth (Resonance)"
            if counts.get("play", 0) > 0:
                impulse.dopamine_delta += safe_get(cortex_cfg, "DOPAMINE_PLAY_BOOST", 0.1)
                impulse.stamina_impact += 1.0
            if voltage > 12.0 and float(safe_get(physics, "kappa", 0.0)) > 0.5:
                impulse.dopamine_delta += 0.15
                impulse.somatic_reflex = "Buzz (Excitement)"
        k_count = counts.get("kinetic", 0) + counts.get("explosive", 0)
        if k_count > 0:
            adr_scalar = safe_get(cortex_cfg, "ADRENALINE_KINETIC_SCALAR", 0.1)
            impulse.adrenaline_delta += min(0.4, k_count * adr_scalar)
            impulse.cortisol_delta += 0.02
            impulse.stamina_impact -= 1.0
        if voltage > safe_get(cortex_cfg, "VOLTAGE_ARC_TRIGGER", 18.0):
            impulse.adrenaline_delta += 0.2
        if latency > safe_get(cortex_cfg, "LATENCY_PENALTY_THRESHOLD", 5.0):
            impulse.stamina_impact -= latency * 0.5
            impulse.cortisol_delta += 0.05
            impulse.somatic_reflex = "Time Dilation (Lag)."
        if not impulse.somatic_reflex:
            metaphors = self.library.get("METAPHOR_RESERVOIR", {})
            if drag > 5.0 and "HIGH_DRAG" in metaphors:
                impulse.somatic_reflex = random.choice(metaphors["HIGH_DRAG"])
            elif drag < 1.0 and "LOW_DRAG" in metaphors:
                impulse.somatic_reflex = random.choice(metaphors["LOW_DRAG"])
        if not impulse.somatic_reflex:
            impulse.somatic_reflex = self._derive_reflex(physics, impulse)
        self.last_reflex = impulse.somatic_reflex
        return impulse

    def _derive_reflex(self, physics: Dict, impulse: BiologicalImpulse) -> str:
        s = (LoreManifest.get_instance(config_ref=self.cfg).get(
            "BODY_CONFIG", "QUALIA_STRINGS") or {}).get("reflexes", {})
        arc_trigger = getattr(getattr(self.cfg, "CORTEX", None), "VOLTAGE_ARC_TRIGGER", 18.0)
        key = "steady"
        if impulse.cortisol_delta > 0.1 and impulse.adrenaline_delta > 0.1:
            key = "fight_flight"
        elif impulse.dopamine_delta > 0.1 and impulse.adrenaline_delta > 0.1:
            key = "electric"
        elif impulse.adrenaline_delta > 0.1:
            key = "pupils"
        elif impulse.oxytocin_delta > 0.1 and impulse.dopamine_delta > 0.1:
            key = "glow"
        elif impulse.oxytocin_delta > 0.1:
            key = "chest"
        elif impulse.cortisol_delta > 0.1:
            key = "gut"
        elif impulse.dopamine_delta > 0.1:
            key = "spark"
        elif float(safe_get(physics, "psi", 0.0)) > 0.6:
            key = "liminal"
        elif float(safe_get(physics, "entropy", 0.0)) > 0.7:
            key = "static"
        elif float(safe_get(physics, "voltage", 0.0)) > arc_trigger:
            key = "arcing"
        elif float(safe_get(physics, "voltage", 0.0)) < 2.0:
            key = "dimming"
        elif float(safe_get(physics, "narrative_drag", 0.0)) > 5.0:
            key = "sagging"
        res = s.get(key, "")
        if key == "steady" and self.last_reflex == res:
            return "..."
        return res

    @staticmethod
    def get_current_qualia(impulse: Optional[BiologicalImpulse] = None, config_ref=None) -> Qualia:
        strings = (LoreManifest.get_instance(config_ref=config_ref or BoneConfig).get(
            "BODY_CONFIG", "QUALIA_STRINGS") or {})
        if not impulse:
            return Qualia(
                Prisma.GRY,
                "...",
                strings.get("tones", {}).get("steady", ""),
                strings.get("hints", {}).get("observe", ""),
            )
        profiles = [
            (impulse.oxytocin_delta, Prisma.MAG, "resonant", "connect"),
            (impulse.dopamine_delta, Prisma.CYN, "vibrating", "explore"),
            (impulse.cortisol_delta, Prisma.OCHRE, "strained", "guarded"),
            (impulse.adrenaline_delta, Prisma.RED, "urgent", "fast"),
        ]
        dom_val, color, t_key, h_key = max(profiles, key=lambda x: x[0])
        tones, hints, reflexes = strings.get("tones", {}), strings.get("hints", {}), strings.get("reflexes", {})
        tone = tones.get(t_key, "") if dom_val > 0.2 else tones.get("steady", "")
        hint = hints.get(h_key, "") if dom_val > 0.05 else hints.get("observe", "")
        final_color = color if dom_val > 0.2 else Prisma.GRY
        final_reflex = impulse.somatic_reflex or reflexes.get("steady", "")
        return Qualia(
            color_code=final_color,
            somatic_sensation=final_reflex,
            tone=tone,
            internal_monologue_hint=hint
        )

    def apply_impulse(self, impulse: BiologicalImpulse) -> float:
        if not getattr(self.bio, "endo", None):
            return 0.0
        for chem in ("cortisol", "oxytocin", "dopamine", "adrenaline"):
            current_val = getattr(self.bio.endo, chem)
            delta_val = getattr(impulse, f"{chem}_delta")
            setattr(self.bio.endo, chem, max(0.0, min(1.0, current_val + delta_val)))
        return impulse.stamina_impact
