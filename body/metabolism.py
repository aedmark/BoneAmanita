"""body/metabolism.py"""
import math
import random
from collections import Counter
from typing import Dict, List, Any, Tuple, TYPE_CHECKING
from body.models import MitochondrialState, MetabolicReceipt
from core import Prisma, LoreManifest
from struts import ux, safe_get
from presets import BoneConfig

if TYPE_CHECKING:
    from body.system import BioSystem


class MitochondrialForge:
    """
    The engine of systemic stamina.
    In a standard LLM, generation is infinitely free. In this architecture, to think is
    to burn ATP (energy) and generate ROS (toxicity). This class calculates the exact
    thermodynamic cost of a prompt based on its structural complexity and chaos.
    """

    def __init__(self, state_ref: MitochondrialState, events_ref, config_ref=None):
        self.state = state_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        full_narrative = (LoreManifest.get_instance(config_ref=self.cfg).get("BIO_NARRATIVE") or {})
        self.narrative = full_narrative.get("MITO", {})
        self.MAX_SAFE_BURN = getattr(self.cfg.BIO, "MAX_SAFE_BURN", 25.0)
        self.ANAEROBIC_THRESHOLD = getattr(self.cfg.BIO, "ANAEROBIC_THRESHOLD", 40.0)

    def get_status_report(self) -> str:
        """Translates raw ATP/ROS numbers into a human-readable systemic state."""
        atp, ros = self.state.atp_pool, self.state.ros_buildup
        if atp < 5.0:
            key = "NECROSIS"
        elif atp < 20.0:
            key = "GRINDING"
        elif ros > 80.0:
            key = "APOPTOSIS"
        else:
            key = "NOMINAL"
        return self.narrative.get(key, "").format(cost=0.0, pool=atp)

    def adjust_atp(self, delta: float, reason: str = ""):
        """Safely credits or debits the energy pool, clamping it to physical limits."""
        old = self.state.atp_pool
        max_limit = getattr(self.cfg, "MAX_ATP", 100.0)
        atp_collapse = getattr(self.cfg.BIO, "ATP_COLLAPSE", 0.0)
        self.state.atp_pool = max(atp_collapse, min(max_limit, old + delta))
        if reason and (abs(delta) > 5.0 or self.state.atp_pool > 90.0):
            self.events.log(f"[ATP]: {reason} ({delta:+.1f})", "BIO")

    def on_substrate_forged(self, payload: Dict):
        """Deducts ATP when the system writes a new memory to the deep storage (Cortex)."""
        cost = payload.get("cost", 0.0)
        filename = payload.get("file", "unknown")
        self.adjust_atp(-cost, f"Substrate Forging [{filename}]")

    def _get_text(self, key, **kwargs):
        """Safe retrieval of narrative strings."""
        tmpl = self.narrative.get(key, "")
        if not tmpl:
            return ""
        try:
            return tmpl.format(**kwargs)
        except Exception as e:
            print(f"{Prisma.RED}[MITO_FORGE] Missing narrative kwargs for '{key}': {e}{Prisma.RST}")
            return tmpl

    def _trigger_anaerobic_bypass(self, raw_cost: float) -> MetabolicReceipt:
        """
        Executes when the cognitive load of a prompt vastly exceeds the system's oxygen capacity.
        It forcefully burns emergency energy, sacrificing structural health (ROS) for immediate output.
        """
        health_burn = 2.0
        self.state.ros_buildup += 2.0
        self.adjust_atp(-20.0, "Anaerobic Burn")
        if self.events and (msg := ux("mito_forge", "anaerobic_bypass")):
            self.events.log(f"{Prisma.MAG}{msg.format(cost=raw_cost)}{Prisma.RST}", "BIO_WARN")
        return MetabolicReceipt(
            base_cost=raw_cost, drag_tax=0.0, inefficiency_tax=0.0, total_burn=health_burn,
            waste_generated=2.0, status="ANAEROBIC", symptom="LACTATE_BUILDUP",
        )

    def process_cycle(self, physics_packet: Any, modifier: float = 1.0) -> MetabolicReceipt:
        """
        The core metabolic loop. This calculates exactly how much energy a specific prompt
        requires to process, based on the shape, chaos, and tension of the data.
        """
        if self.state.atp_pool > 95.0 and self.state.ros_buildup < 1.0:
            return MetabolicReceipt(0, 0, 0, 0, 0, "NOMINAL", "Fresh Start")
        cfg = getattr(self.cfg, "BIO", None)
        depth = float(safe_get(physics_packet, "depth", 0.3))
        connectivity = float(safe_get(physics_packet, "connectivity", 0.2))
        voltage = float(safe_get(physics_packet, "voltage", 30.0))
        base_cost = safe_get(cfg, "BASE_ATP_YIELD", 2.0) + (voltage * safe_get(cfg, "VOLTAGE_TAX_MULT", 0.05))
        cognitive_load_tax = (depth * safe_get(cfg, "DEPTH_TAX_MULT", 2.0)) + (
                connectivity * safe_get(cfg, "CONN_TAX_MULT", 3.0))
        chaos_index = safe_get(physics_packet, "chi", safe_get(physics_packet, "entropy", 0.0))
        if chaos_index > safe_get(cfg, "CHAOS_TAX_THRESHOLD", 0.6):
            chaos_tax = safe_get(cfg, "CHAOS_TAX_MULT", 8.0) * chaos_index
            cognitive_load_tax += chaos_tax
            if self.events and (msg := ux("mito_forge", "chaos_tax")):
                self.events.log(f"{Prisma.RED}{msg.format(tax=chaos_tax)}{Prisma.RST}", "BIO_WARN")
        malignancy = safe_get(physics_packet, "m_a", 0.0)
        friction = safe_get(physics_packet, "mu", 0.0)
        if friction > 0:
            amplification_tax = friction * math.exp(malignancy)
            cognitive_load_tax += amplification_tax
            if amplification_tax > 1.0 and self.events:
                self.events.log(
                    f"{Prisma.MAG}[CHECKPOINT]: Amplification Tax applied (+{amplification_tax:.2f} ATP drag){Prisma.RST}",
                    "BIO_WARN")
        base_demand = base_cost + (math.log1p(max(0.0, self.state.ros_buildup)) * 2.0)
        atp_crit = getattr(cfg, "ATP_CRITICAL", 20.0)
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
        abstraction = float(safe_get(physics_packet, "psi", 0.0))
        waste_generated = 0.0
        abstraction_mult = safe_get(cfg, "WASTE_PSI_MULT", 5.0)
        chaos_mult = safe_get(cfg, "WASTE_CHI_MULT", 5.0)
        volt_div = safe_get(cfg, "WASTE_VOLT_DIV", 20.0)
        base_red = safe_get(cfg, "WASTE_BASE_REDUCTION", 2.0)
        if abstraction > 0.3 or chaos_index > 0.3:
            waste_generated += (abstraction * abstraction_mult) + (chaos_index * chaos_mult)
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
            base_cost=round(base_demand, 2), drag_tax=round(cognitive_load_tax, 2),
            inefficiency_tax=round(total_metabolic_cost - (base_demand + cognitive_load_tax), 2),
            total_burn=round(total_metabolic_cost, 2), waste_generated=round(waste_generated, 2),
            status=status, symptom=self.state.retrograde_signal,
        )

    def _apply_adaptive_dynamics(self):
        """
        Manages Mitohormesis: The biological principle that small amounts of stress
        make the system stronger, but chronic stress causes collapse.
        """
        cfg = getattr(self.cfg, "BIO", None)
        ros_sig = safe_get(cfg, "ROS_SIGNAL", 5.0)
        ros_dam = safe_get(cfg, "ROS_DAMAGE", 20.0)
        ros_purge = safe_get(cfg, "ROS_PURGE", 60.0)
        if self.state.ros_buildup < ros_sig:
            self.state.membrane_potential = max(0.5, self.state.membrane_potential - 0.001)
            self.state.retrograde_signal = "QUIET"
        elif self.state.ros_buildup < ros_dam:
            self.state.membrane_potential = min(1.0, self.state.membrane_potential + 0.005)
            self.state.retrograde_signal = "MITOHORMESIS_ACTIVE"
            self.state.ros_buildup = max(0.0, self.state.ros_buildup - 0.5)
        else:
            self.state.membrane_potential = max(0.1, self.state.membrane_potential - 0.02)
            self.state.retrograde_signal = "OXIDATIVE_STRESS"
        if self.state.ros_buildup > ros_purge:
            self._trigger_mitophagy()

    def adapt(self, stress_level: float):
        """External hook for environmental stressors impacting the engine's capability."""
        old_potential = self.state.membrane_potential
        if stress_level > 5.0:
            self.state.membrane_potential = max(0.4, self.state.membrane_potential - 0.15)
            msg = ux("mito_forge", "adaptation_stress")
            if msg:
                self.events.log(
                    f"{Prisma.RED}{msg.format(stress=stress_level, old=old_potential, new=self.state.membrane_potential)}{Prisma.RST}",
                    "BIO")
        elif stress_level > 1.0:
            self.state.membrane_potential = min(1.5, self.state.membrane_potential + 0.05)
            if random.random() < 0.2 and (msg := ux("mito_forge", "adaptation_hormetic")):
                self.events.log(f"{Prisma.GRN}{msg}{Prisma.RST}", "BIO")

    def _trigger_mitophagy(self):
        """
        Emergency reset. The toxicity is terminal, so the system consumes its own
        mitochondria to prevent the spread of bad data, costing massive energy.
        """
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
        """Applies ancestral epigenetic traits to the current engine."""
        if not traits:
            return
        if traits.get("high_metabolism"):
            self.state.membrane_potential = 1.1
            self.events.log("[MITO]: Ancestral High Metabolism activated.", "GENETICS")

    def cellular_repair(self, survival_streak: int, g_pool: int, inherited_scars: dict) -> Tuple[bool, int, str]:
        """
        Converts Glimmers (relational trust/insight) into permanent healing,
        erasing architectural scars inherited from past conversational trauma.
        """
        if survival_streak < 50 or self.state.ros_buildup > 10.0 or not inherited_scars:
            return False, g_pool, ""
        if g_pool >= 1:
            healed_scar = random.choice(list(inherited_scars.keys()))
            del inherited_scars[healed_scar]
            g_pool -= 1
            fallback = "Epigenetic Plasticity Achieved. Ancestral scar '{healed_scar}' permanently erased. (-1 Glimmer)"
            msg_template = ux("mito_forge", "scar_healed") or fallback
            msg = msg_template.format(healed_scar=healed_scar)
            if self.events:
                self.events.log(f"{Prisma.MAG}✨ [MITO]: {msg}{Prisma.RST}", "BIO_HEAL")
            return True, g_pool, msg
        return False, g_pool, ""


class DigestiveTrack:
    """
    Translates literal syntax (the user's prompt) into biological energy.
    It parses incoming text, rewards dense/complex vocabulary with ATP,
    and heavily penalizes clichés and LLM-isms (The Lexical Firewall).
    """

    def __init__(self, bio_system_ref: "BioSystem", lexicon_ref=None, config_ref=None):
        self.bio = bio_system_ref
        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        base_map = (LoreManifest.get_instance(config_ref=self.cfg).get("BODY_CONFIG") or {}).get("ENZYME_MAP", {})
        self.enzyme_map = dict(base_map)
        if "heavy" not in self.enzyme_map:
            self.enzyme_map.update({
                "heavy": "CELLULASE", "constructive": "CHITINASE",
                "aerobic": "LIGNASE", "meat": "PROTEASE",
            })
        self.SAMPLING_THRESHOLD = getattr(self.cfg.BIO, "SAMPLING_THRESHOLD", 1000)
        self.BASE_WORD_VALUE = getattr(self.cfg.BIO, "BASE_WORD_VALUE", 0.5)
        self.COMPLEX_WORD_BONUS = getattr(self.cfg.BIO, "COMPLEX_WORD_BONUS", 2.0)
        self.CLICHE_TAX_RATE = getattr(self.cfg.BIO, "CLICHE_TAX_RATE", 0.5)

    def harvest(self, phys: Any, logs: List[str]) -> Tuple[str, float, int]:
        """
        The main intake function. Returns the dominant enzyme used, the ATP yielded,
        and the total number of valid words digested.
        """
        clean_words = safe_get(phys, "clean_words", [])
        if not clean_words:
            return "NONE", 0.0, 0
        words_to_process, scaling_factor = self._sample_input(clean_words, logs)
        raw_yield, found_enzymes, cliche_tax, raw_hits = self._digest_words(words_to_process)
        total_atp = raw_yield * scaling_factor
        scaled_tax = cliche_tax * scaling_factor
        total_hits = int(raw_hits * scaling_factor)
        if scaled_tax > 0:
            total_atp = max(0.0, total_atp - scaled_tax)
            self.bio.endo.cortisol += (scaled_tax * 0.02)
            if msg := ux("digestive_track", "cliche_tax"):
                logs.append(f"{Prisma.OCHRE}{msg.format(tax=scaled_tax)}{Prisma.RST}")
        v_thresh = getattr(self.cfg.BIO, "VOLTAGE_BONUS_THRESHOLD", 8.0)
        p_bonus = getattr(self.cfg.BIO, "PROTEASE_BONUS", 5.0)
        if float(safe_get(phys, "voltage", 0.0)) > v_thresh and found_enzymes:
            found_enzymes.append("PROTEASE")
            total_atp += p_bonus
        if found_enzymes:
            dominant = Counter(found_enzymes).most_common(1)[0][0]
        else:
            dominant = "NONE"
        return dominant, total_atp, total_hits

    def _sample_input(self, words: List[str], logs: List[str]) -> Tuple[List[str], float]:
        """Optimizes digestion of massive texts by sampling a representative subset and scaling."""
        count = len(words)
        if count > self.SAMPLING_THRESHOLD:
            factor = count / self.SAMPLING_THRESHOLD
            if random.random() < 0.1 and (msg := ux("digestive_track", "mass_input")):
                logs.append(f"{Prisma.GRY}{msg.format(count=count, factor=factor)}{Prisma.RST}")
            return random.sample(words, self.SAMPLING_THRESHOLD), factor
        return words, 1.0

    def _digest_words(self, words: List[str]) -> Tuple[float, List[str], float, int]:
        """
        The molecular breakdown of syntax. Determines caloric value based on word length,
        kinetic energy, and explicit penalization of "Semantic Antigens" (alignment tropes).
        """
        word_counts = Counter(words)
        cfg = getattr(self.cfg, "BIO", None)
        min_len = safe_get(cfg, "MIN_WORD_LENGTH", 4)
        comp_len = safe_get(cfg, "COMPLEX_WORD_LENGTH", 7)
        valid_words = {w: c for w, c in word_counts.items() if len(w) >= min_len}
        hits = sum(valid_words.values())
        if not valid_words or not self.lex:
            return sum(c * self.BASE_WORD_VALUE for c in valid_words.values()), [], 0.0, hits
        user_set = set(valid_words.keys())
        antigen_set = self.lex.get("antigen") or set()
        kinetic_set = (self.lex.get("kinetic") or set()) | (self.lex.get("explosive") or set())
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
                    atp_yield += self.BASE_WORD_VALUE * log_mult
                else:
                    atp_yield += val * log_mult
                    if (enzyme := self.enzyme_map.get(cat, "AMYLASE")) != "AMYLASE":
                        enzymes.append(enzyme)
        return atp_yield, enzymes, cliche_tax, hits
