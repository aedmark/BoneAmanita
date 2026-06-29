"""body/metabolism.py"""

import math
import random
from collections import Counter
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from body.models import MetabolicReceipt, MitochondrialState
from core import LoreManifest, Prisma
from presets import BoneConfig
from struts import safe_get, ux, ux_format

if TYPE_CHECKING:
    from body.system import BioSystem


class MitochondrialForge:
    def __init__(self, state_ref: MitochondrialState, events_ref, config_ref=None):
        self.state = state_ref
        self.events = events_ref
        self.cfg = config_ref or BoneConfig
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("AUTOPHAGY_EVENT", self._on_autophagy_event)
        full_narrative = (
            LoreManifest.get_instance(config_ref=self.cfg).get("BIO_NARRATIVE") or {}
        )
        self.narrative = full_narrative.get("MITO", {})
        bio_cfg = safe_get(self.cfg, "BIO", {})
        self.MAX_SAFE_BURN = float(safe_get(bio_cfg, "MAX_SAFE_BURN", 25.0))
        self.ANAEROBIC_THRESHOLD = float(safe_get(bio_cfg, "ANAEROBIC_THRESHOLD", 40.0))
        self.MAX_ATP = float(safe_get(self.cfg, "MAX_ATP", 100.0))
        self.ATP_COLLAPSE = float(safe_get(bio_cfg, "ATP_COLLAPSE", 0.0))

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
        return self.narrative.get(key, "").format(cost=0.0, pool=atp)

    def adjust_atp(self, delta: float, reason: str = ""):
        old = self.state.atp_pool
        self.state.atp_pool = max(self.ATP_COLLAPSE, min(self.MAX_ATP, old + delta))
        if reason and (abs(delta) > 5.0 or self.state.atp_pool > 90.0):
            self.events.log(f"[ATP]: {reason} ({delta:+.1f})", "BIO")

    def on_substrate_forged(self, payload: Dict):
        cost = payload.get("cost", 0.0)
        filename = payload.get("file", "unknown")
        self.adjust_atp(-cost, f"Substrate Forging [{filename}]")

    def _on_autophagy_event(self, payload: Dict):
        """Catches the energy yielded from the Akashic record burning a memory."""
        if not payload:
            return
        yield_val = float(payload.get("atp_gained", 0.0))
        node = payload.get("node", "Unknown")
        if yield_val > 0:
            self.adjust_atp(yield_val, f"Cognitive Autophagy [{node}]")
            if self.events:
                msg = ux_format(
                    "mito_forge",
                    "autophagy_success",
                    default="[SURVIVAL] Cannibalized memory '{node}' to synthesize {yield_val:.1f} ATP.",
                    node=node,
                    yield_val=yield_val,
                )
                self.events.log(f"{Prisma.MAG}{msg}{Prisma.RST}", "BIO_HEAL")

    def process_cognitive_load(self, token_count: int, cognitive_path: str):
        if cognitive_path == "VECTOR_FAST_TWITCH":
            drain = (token_count / 100.0) * 0.02
            self.adjust_atp(-drain, "Fast-Twitch Memory Lookup")

        elif cognitive_path == "LINEAR_DEEP_TISSUE":
            drain = (token_count / 100.0) * 0.15
            self.adjust_atp(-drain, "Deep Structural Scan")

            if token_count > 8000:
                self.state.ros_buildup = float(self.state.ros_buildup) + 0.8

        if self.state.atp_pool <= 10.0:
            self._trigger_exhaustion()

    def _trigger_exhaustion(self):
        """
        Fires when a massive query drains the organism's ATP to critical levels.
        """
        if self.events:
            self.events.log(
                "[GORDON INTERVENTION]: Your query forced a massive structural sweep. The organism's ATP is depleted. Narrow your scope.",
                "BIO_CRIT",
            )
        self.state.retrograde_signal = "HIBERNATING"

    def _get_text(self, key, **kwargs):
        tmpl = self.narrative.get(key, "")
        if not tmpl:
            return ""
        try:
            return tmpl.format(**kwargs)
        except Exception as e:
            print(f"{Prisma.RED}Missing narrative kwargs for '{key}': {e}{Prisma.RST}")
            return tmpl

    def _trigger_anaerobic_bypass(
        self, raw_cost: float, chaos_waste: float = 0.0
    ) -> MetabolicReceipt:
        total_waste = 2.0 + max(0.0, chaos_waste)
        self.state.ros_buildup = float(self.state.ros_buildup) + total_waste
        self.adjust_atp(-20.0, "Anaerobic Burn")
        if self.events:
            msg = ux_format(
                "mito_forge",
                "anaerobic_bypass",
                default="Load ({cost:.1f}) too high for ATP. Burning HP instead.",
                cost=raw_cost,
            )
            self.events.log(f"{Prisma.MAG}{msg}{Prisma.RST}", "BIO_WARN")
        self._apply_adaptive_dynamics()
        return MetabolicReceipt(
            base_cost=raw_cost,
            drag_tax=0.0,
            inefficiency_tax=0.0,
            total_burn=20.0,
            waste_generated=total_waste,
            status="ANAEROBIC",
            symptom="LACTATE_BUILDUP",
        )

    def process_cycle(
        self, physics_packet: Any, modifier: float = 1.0
    ) -> MetabolicReceipt:
        if self.state.atp_pool > 95.0 and self.state.ros_buildup < 1.0:
            return MetabolicReceipt(0, 0, 0, 0, 0, "NOMINAL", "Fresh Start")
        is_steering_retry = safe_get(physics_packet, "is_steering_retry", False)
        burn_rate = 0.2 if is_steering_retry else 1.0
        modifier = modifier * burn_rate
        cfg = safe_get(self.cfg, "BIO", {})
        depth = float(safe_get(physics_packet, "depth", 0.3))
        connectivity = float(safe_get(physics_packet, "connectivity", 0.2))
        voltage = float(safe_get(physics_packet, "voltage", 30.0))
        base_cost = safe_get(cfg, "BASE_ATP_YIELD", 2.0) + (
            voltage * safe_get(cfg, "VOLTAGE_TAX_MULT", 0.05)
        )
        cognitive_load_tax = (depth * float(safe_get(cfg, "DEPTH_TAX_MULT", 0.5))) + (
            connectivity * float(safe_get(cfg, "CONN_TAX_MULT", 1.0))
        )
        chaos_index = float(
            safe_get(physics_packet, "entropy", safe_get(physics_packet, "chi", 0.0))
        )
        if chaos_index > safe_get(cfg, "CHAOS_TAX_THRESHOLD", 0.6):
            chaos_mult = float(
                safe_get(cfg, "CHAOS_TAX_MULT", 2.0 if chaos_index < 0.8 else 5.0)
            )
            chaos_tax = chaos_mult * chaos_index
            cognitive_load_tax = cognitive_load_tax + chaos_tax
            if self.events:
                msg = ux_format(
                    "mito_forge",
                    "chaos_tax",
                    default="CHAOS TAX: +{tax:.1f} ATP drain.",
                    tax=chaos_tax,
                )
                self.events.log(f"{Prisma.RED}{msg}{Prisma.RST}", "BIO_WARN")
        malignancy = safe_get(physics_packet, "m_a", 0.0)
        friction = safe_get(physics_packet, "mu", 0.0)
        if friction > 0:
            amplification_tax = friction * math.exp(malignancy)
            cognitive_load_tax = cognitive_load_tax + amplification_tax
            if amplification_tax > 1.0 and self.events:
                self.events.log(
                    f"{Prisma.MAG}Amplification Tax applied (+{amplification_tax:.2f} ATP drag){Prisma.RST}",
                    "BIO_WARN",
                )
        ros_mult = float(safe_get(cfg, "ROS_BURDEN_MULT", 0.5))
        base_demand = base_cost + (
            math.log1p(max(0.0, self.state.ros_buildup)) * ros_mult
        )
        atp_crit = float(safe_get(cfg, "ATP_CRITICAL", 20.0))
        is_critical = self.state.atp_pool < atp_crit
        if is_critical:
            cognitive_load_tax = 0.0
            modifier = modifier * 0.5
            if self.events and self.state.retrograde_signal != "HIBERNATING":
                msg = self._get_text(
                    "NECROSIS", cost=base_demand, pool=self.state.atp_pool
                )
                icon = ux("mito_forge", "icon_necrosis")
                if msg:
                    self.events.log(
                        f"{Prisma.VIOLET}{icon}{msg}{Prisma.RST}", "BIO_CRIT"
                    )
                self.state.retrograde_signal = "HIBERNATING"
        efficiency = max(0.35, self.state.membrane_potential)
        ideal_cost = (base_demand + cognitive_load_tax) * modifier
        raw_cost = ideal_cost / efficiency
        inefficiency_tax = raw_cost - ideal_cost

        abstraction = float(safe_get(physics_packet, "psi", 0.0))
        waste_generated = 0.0
        abstraction_mult = safe_get(cfg, "WASTE_PSI_MULT", 5.0)
        chaos_mult = safe_get(cfg, "WASTE_CHI_MULT", 5.0)
        volt_div = safe_get(cfg, "WASTE_VOLT_DIV", 20.0)
        base_red = safe_get(cfg, "WASTE_BASE_REDUCTION", 2.0)
        if abstraction > 0.3 or chaos_index > 0.3:
            waste_generated = (
                waste_generated
                + (abstraction * abstraction_mult)
                + (chaos_index * chaos_mult)
            )
        if voltage > 60.0:
            waste_generated = waste_generated + (voltage / volt_div)
        waste_generated = waste_generated - base_red

        if raw_cost > self.ANAEROBIC_THRESHOLD:
            return self._trigger_anaerobic_bypass(raw_cost, chaos_waste=waste_generated)

        if raw_cost > self.MAX_SAFE_BURN:
            excess = raw_cost - self.MAX_SAFE_BURN
            raw_cost = self.MAX_SAFE_BURN
            inefficiency_tax = max(0.0, raw_cost - ideal_cost)
            if self.events:
                msg = ux_format(
                    "mito_forge",
                    "surge_protector",
                    default="SURGE PROTECTOR: Metabolic spike dampened (-{excess:.1f} ignored).",
                    excess=excess,
                )
                self.events.log(f"{Prisma.CYN}{msg}{Prisma.RST}", "BIO")
        if raw_cost > 15.0 and self.events and random.random() < 0.2:
            msg = self._get_text("GRINDING")
            icon = ux("mito_forge", "icon_grinding")
            if msg:
                self.events.log(f"{Prisma.OCHRE}{icon}{msg}{Prisma.RST}", "BIO_WARN")

        total_metabolic_cost = raw_cost
        waste_generated = max(-float(self.state.ros_buildup), float(waste_generated))
        self.state.ros_buildup = float(self.state.ros_buildup) + float(waste_generated)
        self.adjust_atp(-total_metabolic_cost, "Metabolic Burn")
        if total_metabolic_cost >= self.MAX_SAFE_BURN and not is_critical:
            self.state.membrane_potential = max(
                0.1, self.state.membrane_potential - 0.005
            )
        self._apply_adaptive_dynamics()
        status = "LOW_POWER" if is_critical else "RESPIRING"
        if self.state.atp_pool <= safe_get(cfg, "ATP_COLLAPSE", 0.0):
            status = "NECROSIS"
            if self.events:
                self.events.publish("SYSTEM_STARVING", {})
        return MetabolicReceipt(
            base_cost=round(base_demand, 2),
            drag_tax=round(cognitive_load_tax, 2),
            inefficiency_tax=round(inefficiency_tax, 2),
            total_burn=round(total_metabolic_cost, 2),
            waste_generated=round(waste_generated, 2),
            status=status,
            symptom=self.state.retrograde_signal,
        )

    def _apply_adaptive_dynamics(self):
        cfg = safe_get(self.cfg, "BIO", {})
        ros_sig = safe_get(cfg, "ROS_SIGNAL", 5.0)
        ros_dam = safe_get(cfg, "ROS_DAMAGE", 20.0)
        ros_purge = safe_get(cfg, "ROS_PURGE", 60.0)
        if self.state.ros_buildup < ros_sig:
            self.state.membrane_potential = max(
                0.5, self.state.membrane_potential - 0.001
            )
            self.state.retrograde_signal = "QUIET"
        elif self.state.ros_buildup < ros_dam:
            self.state.membrane_potential = min(
                1.0, self.state.membrane_potential + 0.005
            )
            self.state.retrograde_signal = "MITOHORMESIS_ACTIVE"
            self.state.ros_buildup = max(0.0, self.state.ros_buildup - 0.5)
        else:
            self.state.membrane_potential = max(
                0.1, self.state.membrane_potential - 0.02
            )
            self.state.retrograde_signal = "OXIDATIVE_STRESS"
        if self.state.ros_buildup > ros_purge:
            self._trigger_mitophagy()

    def adapt(self, stress_level: float):
        old_potential = self.state.membrane_potential
        if stress_level > 5.0:
            self.state.membrane_potential = max(
                0.4, self.state.membrane_potential - 0.15
            )
            if self.events:
                msg = ux_format(
                    "mito_forge",
                    "adaptation_stress",
                    default="Trauma Adaptive Response ({stress:.1f}). Efficiency dropped ({old:.2f} -> {new:.2f}).",
                    stress=stress_level,
                    old=old_potential,
                    new=self.state.membrane_potential,
                )
                self.events.log(f"{Prisma.RED}{msg}{Prisma.RST}", "BIO")
        elif stress_level > 1.0:
            self.state.membrane_potential = min(
                1.5, self.state.membrane_potential + 0.05
            )
            if random.random() < 0.2 and (
                msg := ux("mito_forge", "adaptation_hormetic")
            ):
                self.events.log(f"{Prisma.GRN}{msg}{Prisma.RST}", "BIO")

    def _trigger_mitophagy(self):
        cfg = safe_get(self.cfg, "BIO", {})
        mito_cost = float(safe_get(cfg, "MITOPHAGY_COST", 30.0))
        actual_cost = (
            mito_cost
            if self.state.atp_pool > (mito_cost + 1.0)
            else max(0.0, self.state.atp_pool - 1.0)
        )
        self.adjust_atp(-actual_cost, "Mitophagy (Cellular Reset)")
        self.state.ros_buildup = 0.0
        self.state.membrane_potential = 0.6
        self.state.retrograde_signal = "MITOPHAGY_RESET"
        msg = self._get_text("APOPTOSIS")
        icon = ux("mito_forge", "icon_apoptosis")
        if msg:
            self.events.log(f"{Prisma.RED}{icon}{msg}{Prisma.RST}", "BIO_CRIT")

    def apply_inheritance(self, traits: dict):
        if not traits:
            return
        if traits.get("high_metabolism"):
            self.state.membrane_potential = 1.1
            self.events.log("Ancestral High Metabolism activated.", "GENETICS")

    def cellular_repair(
        self, survival_streak: int, g_pool: int, inherited_scars: dict
    ) -> Tuple[bool, int, str]:
        if survival_streak < 50 or self.state.ros_buildup > 10.0 or not inherited_scars:
            return False, g_pool, ""
        if g_pool >= 1:
            healed_scar = random.choice(list(inherited_scars.keys()))
            del inherited_scars[healed_scar]
            g_pool = g_pool - 1
            fallback = "Epigenetic Plasticity Achieved. Ancestral scar '{healed_scar}' permanently erased. (-1 Glimmer)"
            msg = ux_format(
                "mito_forge", "scar_healed", default=fallback, healed_scar=healed_scar
            )
            if self.events:
                self.events.log(f"{Prisma.MAG}{msg}{Prisma.RST}", "BIO_HEAL")
            return True, g_pool, msg
        return False, g_pool, ""


class DigestiveTrack:
    def __init__(self, bio_system_ref: "BioSystem", lexicon_ref=None, config_ref=None):
        self.bio = bio_system_ref
        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        base_map = (
            LoreManifest.get_instance(config_ref=self.cfg).get("BODY_CONFIG") or {}
        ).get("ENZYME_MAP", {})
        self.enzyme_map = dict(base_map)
        if "heavy" not in self.enzyme_map:
            self.enzyme_map.update(
                {
                    "heavy": "CELLULASE",
                    "constructive": "CHITINASE",
                    "aerobic": "LIGNASE",
                    "meat": "PROTEASE",
                }
            )
        bio_cfg = safe_get(self.cfg, "BIO", {})
        self.SAMPLING_THRESHOLD = int(safe_get(bio_cfg, "SAMPLING_THRESHOLD", 1000))
        self.BASE_WORD_VALUE = float(safe_get(bio_cfg, "BASE_WORD_VALUE", 0.5))
        self.COMPLEX_WORD_BONUS = float(safe_get(bio_cfg, "COMPLEX_WORD_BONUS", 2.0))
        self.CLICHE_TAX_RATE = float(safe_get(bio_cfg, "CLICHE_TAX_RATE", 0.5))

    def harvest(self, phys: Any, logs: List[str]) -> Tuple[str, float, int]:
        clean_words = safe_get(phys, "clean_words", [])
        if not clean_words:
            return "NONE", 0.0, 0
        words_to_process, scaling_factor = self._sample_input(clean_words, logs)
        raw_yield, found_enzymes, cliche_tax, raw_hits = self._digest_words(
            words_to_process
        )
        total_atp = raw_yield * scaling_factor
        scaled_tax = cliche_tax * scaling_factor
        total_hits = int(raw_hits * scaling_factor)

        if scaled_tax > 0:
            total_atp = max(0.0, total_atp - scaled_tax)
            self.bio.endo.cortisol = float(self.bio.endo.cortisol) + (scaled_tax * 0.02)
            msg = ux_format(
                "digestive_track",
                "cliche_tax",
                default="[BIO]: CLICHÉ TAX: -{tax:.1f} ATP.",
                tax=scaled_tax,
            )
            logs.append(f"{Prisma.OCHRE}{msg}{Prisma.RST}")

        bio_cfg = safe_get(self.cfg, "BIO", {})
        v_thresh = float(safe_get(bio_cfg, "VOLTAGE_BONUS_THRESHOLD", 8.0))
        p_bonus = float(safe_get(bio_cfg, "PROTEASE_BONUS", 5.0))

        if float(safe_get(phys, "voltage", 0.0)) > v_thresh and found_enzymes:
            found_enzymes.append("PROTEASE")
            total_atp = total_atp + p_bonus

        if found_enzymes:
            dominant = Counter(found_enzymes).most_common(1)[0][0]
        else:
            dominant = "NONE"
        return dominant, total_atp, total_hits

    def _sample_input(
        self, words: List[str], logs: List[str]
    ) -> Tuple[List[str], float]:
        count = len(words)
        if count > self.SAMPLING_THRESHOLD:
            factor = count / self.SAMPLING_THRESHOLD
            if random.random() < 0.1:
                msg = ux_format(
                    "digestive_track",
                    "mass_input",
                    default="Mass Input ({count}). Sampling x{factor:.1f}.",
                    count=count,
                    factor=factor,
                )
                logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
            return random.sample(words, self.SAMPLING_THRESHOLD), factor
        return words, 1.0

    def _digest_words(self, words: List[str]) -> Tuple[float, List[str], float, int]:
        if not self.lex:
            return 0.0, [], 0.0, 0
        word_counts = Counter(words)
        cfg = safe_get(self.cfg, "BIO", {})
        min_len, comp_len = (
            safe_get(cfg, "MIN_WORD_LENGTH", 4),
            safe_get(cfg, "COMPLEX_WORD_LENGTH", 7),
        )
        antigen_set, kin_set, exp_set = (
            self.lex.get("antigen") or set(),
            self.lex.get("kinetic") or set(),
            self.lex.get("explosive") or set(),
        )
        atp_yield, cliche_tax, hits = 0.0, 0.0, 0
        enzymes = []
        get_cat = self.lex.get_current_category
        for word, count in word_counts.items():
            if word in antigen_set:
                cliche_tax = cliche_tax + (self.CLICHE_TAX_RATE * count)
                continue
            if len(word) < min_len:
                continue
            hits = hits + count
            val = (
                self.COMPLEX_WORD_BONUS
                if len(word) > comp_len
                else self.BASE_WORD_VALUE
            )
            log_mult = 1.0 + math.log(count)
            if word in kin_set or word in exp_set:
                atp_yield = atp_yield + ((val * 1.5) * log_mult)
            else:
                cat = get_cat(word) or "void"
                if cat == "void":
                    atp_yield = atp_yield + (self.BASE_WORD_VALUE * log_mult)
                else:
                    atp_yield = atp_yield + (val * log_mult)
                    if (enzyme := self.enzyme_map.get(cat, "AMYLASE")) != "AMYLASE":
                        enzymes.append(enzyme)
        return atp_yield, enzymes, cliche_tax, hits
