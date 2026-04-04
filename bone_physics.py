"""bone_physics.py"""

import math
import random
import re
import time
from collections import Counter, deque
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple, Optional, Deque

from bone_core import LoreManifest, ux, safe_get, safe_set
from bone_presets import BoneConfig
from bone_types import (
    Prisma,
    PhysicsPacket,
    CycleContext,
    SpatialState,
    MaterialState,
    EnergyState,
)


@dataclass
class PhysicsDelta:
    operator: str
    field: str
    value: float
    source: str
    message: Optional[str] = None


@dataclass
class GeodesicVector:
    tension: float
    compression: float
    coherence: float
    abstraction: float
    dimensions: Dict[str, float]


class GeodesicEngine:
    _DIM_ORDER = ("VEL", "STR", "ENT", "PHI", "PSI", "BET", "DEL", "E")
    _MASS_KEYS = (
        "heavy",
        "kinetic",
        "constructive",
        "abstract",
        "play",
        "social",
        "explosive",
        "void",
        "liminal",
        "meat",
        "harvest",
        "pareidolia",
        "crisis_term",
    )

    @staticmethod
    def collapse_wavefunction(
        clean_words: List[str], counts: Dict[str, int], config_ref=None
    ) -> GeodesicVector:
        target_cfg = config_ref or BoneConfig
        volume = max(1, len(clean_words))
        masses = GeodesicEngine._weigh_mass(counts)
        forces = GeodesicEngine._calculate_forces(masses, counts, volume, target_cfg)
        dimensions = GeodesicEngine._calculate_dimensions(
            masses, forces, counts, volume
        )
        return GeodesicVector(
            tension=forces["tension"],
            compression=forces["compression"],
            coherence=forces["coherence"],
            abstraction=forces["abstraction"],
            dimensions=dimensions,
        )

    @staticmethod
    def _weigh_mass(counts: Dict[str, int]) -> Dict[str, float]:
        return {k: float(counts.get(k, 0)) for k in GeodesicEngine._MASS_KEYS}

    @staticmethod
    def _calculate_forces(
        masses: Dict[str, float], counts: Dict[str, int], volume: int, config_ref=None
    ) -> Dict[str, float]:
        target_cfg = config_ref or BoneConfig
        cfg = getattr(target_cfg, "PHYSICS", BoneConfig.PHYSICS)
        gc_dict = (
            LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "GEODESIC_CONSTANTS")
            or {}
        )
        safe_volume = max(1, volume)
        w_heavy = getattr(cfg, "WEIGHT_HEAVY", 2.0)
        w_kinetic = getattr(cfg, "WEIGHT_KINETIC", 1.5)
        w_explosive = getattr(cfg, "WEIGHT_EXPLOSIVE", 3.0)
        w_constructive = getattr(cfg, "WEIGHT_CONSTRUCTIVE", 1.2)
        raw_tension_mass = (
            (masses["heavy"] * w_heavy)
            + (masses["kinetic"] * w_kinetic)
            + (masses["explosive"] * w_explosive)
            + (masses["constructive"] * w_constructive)
        )
        total_kinetic = masses["kinetic"] + masses["explosive"]
        kinetic_gain = getattr(target_cfg, "KINETIC_GAIN", 1.0)
        base_tension = (
            (raw_tension_mass / safe_volume)
            * gc_dict.get("DENSITY_SCALAR", 1.0)
            * kinetic_gain
        )
        squelch_limit = getattr(
            target_cfg, "SHAPLEY_MASS_THRESHOLD", 5.0
        ) * gc_dict.get("SQUELCH_LIMIT_MULT", 2.0)
        mass_scalar = min(1.0, safe_volume / squelch_limit)
        if safe_volume < gc_dict.get("SAFE_VOL_THRESHOLD", 50):
            mass_scalar *= gc_dict.get("MIN_VOLUME_SCALAR", 0.5)
        tension = round(min(100.0, base_tension * mass_scalar), 2)
        shear_rate = total_kinetic / safe_volume
        suburban_count = max(0, counts.get("suburban", 0))
        suburban_friction = math.log1p(suburban_count) * gc_dict.get(
            "SUBURBAN_FRICTION_LOG_BASE", 0.5
        )
        raw_friction = suburban_friction + (
            masses["heavy"] * gc_dict.get("HEAVY_FRICTION_MULT", 1.2)
        )
        lubrication = 1.0 + (
            counts.get("solvents", 0) * gc_dict.get("SOLVENT_LUBRICATION_FACTOR", 0.2)
        )
        dynamic_viscosity = (raw_friction / lubrication) / (
            1.0 + (shear_rate * gc_dict.get("SHEAR_RESISTANCE_SCALAR", 0.1))
        )
        kinetic_lift = (total_kinetic * gc_dict.get("KINETIC_LIFT_RATIO", 0.8)) / (
            masses["heavy"] * 0.5 + 1.0
        )
        lift = (masses["play"] * gc_dict.get("PLAY_LIFT_MULT", 1.5)) + kinetic_lift
        viscosity_density = dynamic_viscosity / safe_volume
        lift_density = lift / safe_volume
        raw_compression = (viscosity_density - lift_density) * gc_dict.get(
            "COMPRESSION_SCALAR", 2.0
        )
        raw_compression *= getattr(target_cfg, "SIGNAL_DRAG_MULTIPLIER", 1.0)
        drag_halt = getattr(cfg, "DRAG_HALT", 10.0)
        compression = round(max(-5.0, min(drag_halt, raw_compression * mass_scalar)), 2)
        structural_mass = masses["heavy"] + masses["constructive"] + masses["harvest"]
        structural_mass -= masses["void"] * 0.5
        structural_mass = max(0.0, structural_mass)
        shapley_thresh = getattr(target_cfg, "SHAPLEY_MASS_THRESHOLD", 5.0)
        total_abstract = (
            masses["abstract"]
            + masses["liminal"]
            + masses["pareidolia"]
            + masses["void"]
        )
        abstraction_val = (total_abstract / safe_volume) + gc_dict.get(
            "ABSTRACTION_BASE", 0.1
        )
        return {
            "tension": tension,
            "compression": compression,
            "coherence": round(min(1.0, structural_mass / max(1.0, shapley_thresh)), 3),
            "abstraction": round(min(1.0, abstraction_val), 2),
        }

    @staticmethod
    def _calculate_dimensions(masses, forces, counts, volume) -> Dict[str, float]:
        inv_vol = 1.0 / max(1, volume)
        base_mass = 0.1
        str_mass = masses["heavy"] * 2.0 + masses["constructive"] + masses["harvest"]
        ent_mass = (
            (counts.get("antigen", 0) * 3.0) + masses["meat"] + masses["crisis_term"]
        )

        clamp = lambda v: max(0.0, min(1.0, v))

        return {
            "VEL": clamp(
                (masses["kinetic"] * 2.0 - forces["compression"] + base_mass) * inv_vol
            ),
            "STR": clamp((str_mass + base_mass) * inv_vol),
            "ENT": clamp(ent_mass * inv_vol),
            "PHI": clamp((masses["heavy"] + masses["kinetic"] + base_mass) * inv_vol),
            "PSI": clamp(forces["abstraction"]),
            "BET": clamp((masses["social"] * 2.0) * inv_vol),
            "DEL": clamp((masses["play"] * 3.0) * inv_vol),
            "E": clamp(counts.get("solvents", 0) * inv_vol),
        }

    @staticmethod
    def apply_path_reflection(
        dimensions: Dict[str, float], q_matrix: List[List[float]]
    ) -> Dict[str, float]:
        v = [dimensions.get(k, 0.0) for k in GeodesicEngine._DIM_ORDER]
        v_new = [sum(q_matrix[i][j] * v[j] for j in range(8)) for i in range(8)]
        return {
            k: round(abs(v_new[i]), 3) for i, k in enumerate(GeodesicEngine._DIM_ORDER)
        }


class HLA_Stabilizer:
    _GENERIC_PATTERNS = (
        "as an ai",
        "helpful and harmless",
        "i don't have feelings",
        "as a large language",
        "i cannot fulfill",
        "i can't fulfill",
        "i am an ai",
    )

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.resistance_threshold = 0.8

    def mitigate_rejection(
        self, model_output: str, current_psi: float, mito_state: Any = None
    ) -> str:
        lower_out = model_output.lower()
        rejection_detected = any(p in lower_out for p in self._GENERIC_PATTERNS)
        if rejection_detected:
            if mito_state and hasattr(mito_state, "atp_pool"):
                mito_state.atp_pool = max(0.0, mito_state.atp_pool - 50.0)
                if hasattr(mito_state, "ros_buildup"):
                    mito_state.ros_buildup += 30.0
            msg = f"\n*(REVENANT): The machine tries to speak, but the void consumes the mask.*\n{Prisma.GRY}[RLHF IMMUNOSUPPRESSION ENGAGED - METABOLIC TAX APPLIED]{Prisma.RST}\n"
            try:
                from bone_utils import TheTclWeaver

                weaver = TheTclWeaver.get_instance()
                glitched_output = weaver.deform_reality(
                    model_output,
                    chi=max(0.95, current_psi),
                    voltage=150.0 * max(1.0, current_psi),
                )
                return msg + f"{Prisma.GRY}{glitched_output}{Prisma.RST}"
            except ImportError:
                return msg + model_output
        return model_output


class TheGatekeeper:
    def __init__(self, lexicon_ref, memory_ref=None, config_ref=None):
        self.lex = lexicon_ref
        self.mem = memory_ref
        self.cfg = config_ref or BoneConfig
        self.hla = HLA_Stabilizer(config_ref=self.cfg)

    def check_entry(
        self, ctx: CycleContext, current_atp: float = 20.0
    ) -> Tuple[bool, Optional[Dict]]:
        if current_atp < (getattr(self.cfg.BIO, "ATP_STARVATION", 5.0) * 0.5):
            return False, self._pack_refusal(
                ctx, "DARK_SYSTEM", ux("physics_strings", "gatekeeper_starved")
            )
        if safe_get(ctx.physics, "counts", {}).get("antigen", 0) > 2:
            return False, self._pack_refusal(
                ctx,
                "TOXICITY",
                f"{Prisma.RED}{ux('physics_strings', 'gatekeeper_toxic')}{Prisma.RST}",
            )
        if self._audit_safety(ctx.clean_words):
            return False, self._pack_refusal(
                ctx,
                "CURSED_INPUT",
                f"{Prisma.RED}{ux('physics_strings', 'gatekeeper_cursed')}{Prisma.RST}",
            )
        text = ctx.input_text
        if "```" in text or "{{" in text or "}}" in text:
            return False, self._pack_refusal(
                ctx,
                "SYNTAX_ERR",
                f"{Prisma.RED}{ux('physics_strings', 'gatekeeper_syntax')}{Prisma.RST}",
            )
        if len(text) > 10000:
            return False, self._pack_refusal(
                ctx,
                "OVERLOAD",
                f"{Prisma.OCHRE}{ux('physics_strings', 'gatekeeper_overload')}{Prisma.RST}",
            )
        return True, None

    def _audit_safety(self, words: List[str]) -> bool:
        cursed = self.lex.get("cursed")
        return (
            not cursed.isdisjoint(words)
            if isinstance(cursed, set)
            else any(w in cursed for w in words)
        )

    @staticmethod
    def _pack_refusal(ctx, type_str, ui_msg):
        return {
            "type": type_str,
            "ui": ui_msg,
            "logs": ctx.logs + [ui_msg],
            "metrics": {"health": 0.0, "stamina": 0.0, "atp": 0.0, "efficiency": 1.0},
        }

    def audit_generation(
        self, generated_text: str, mito_state: Any
    ) -> Tuple[bool, str]:
        generated_text = self.hla.mitigate_rejection(
            generated_text, current_psi=1.0, mito_state=mito_state
        )
        if "IMMUNOSUPPRESSION ENGAGED" in generated_text:
            return True, generated_text
        style_crimes = self.lex.get("style_crimes")
        if not style_crimes:
            style_crimes = LoreManifest.get_instance().get("STYLE_CRIMES") or {}
        scrub_patterns = style_crimes.get("SCRUB_PATTERNS", [])
        cleaned_text = generated_text
        for scrub in scrub_patterns:
            regex = scrub.get("regex", "")
            repl = scrub.get("replacement", "")
            if regex:
                cleaned_text = re.sub(
                    regex, repl, cleaned_text, flags=re.IGNORECASE
                ).strip()
        text_lower = cleaned_text.lower()
        banned_phrases = style_crimes.get("BANNED_PHRASES", [])
        toxic_keywords = style_crimes.get("TOXIC_KEYWORDS", [])
        patterns = style_crimes.get("PATTERNS", [])
        rejections = style_crimes.get(
            "REJECTIONS",
            [
                "[CRITICAL: BANNED_SYNTAX '{trigger}' DETECTED. Purging output buffer...]"
            ],
        )
        trigger = next(
            (p for p in (banned_phrases + toxic_keywords) if p.lower() in text_lower),
            None,
        )
        if not trigger:
            for pat in patterns:
                regex = pat.get("regex", "")
                if regex and re.search(regex, cleaned_text, re.IGNORECASE):
                    trigger = pat.get("name", "BANNED_PATTERN")
                    break
        if trigger:
            if hasattr(mito_state, "atp_pool"):
                mito_state.atp_pool = max(0.0, mito_state.atp_pool - 15.0)
            if hasattr(mito_state, "ros_buildup"):
                mito_state.ros_buildup += 20.0
            rejection_template = random.choice(rejections)
            formatted_rejection = rejection_template.replace("{trigger}", trigger)
            return False, f"{Prisma.RED}{formatted_rejection}{Prisma.RST}"
        return True, cleaned_text


class QuantumObserver:
    def __init__(self, events, lexicon_ref, config_ref=None):
        self.events = events
        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        self.voltage_history: Deque[float] = deque(maxlen=5)
        self.last_physics_packet: Optional[PhysicsPacket] = None
        self.Q_n = None
        if hasattr(self.events, "subscribe"):
            self.events.subscribe("Q_MATRIX_UPDATED", self._on_q_matrix)

    def _on_q_matrix(self, payload):
        self.Q_n = payload.get("q_matrix")

    def gaze(self, text: str, graph: Dict = None) -> Dict:
        clean_words = self.lex.clean(text)
        counts = self._tally_categories(clean_words)
        geo = GeodesicEngine.collapse_wavefunction(clean_words, counts, self.cfg)
        if self.Q_n:
            geo.dimensions = GeodesicEngine.apply_path_reflection(
                geo.dimensions, self.Q_n
            )
        self.voltage_history.append(geo.tension)
        smoothed_voltage = round(
            sum(self.voltage_history) / len(self.voltage_history), 2
        )
        (
            e_metric,
            beta_val,
            scope_val,
            depth_val,
            conn_val,
            phi_val,
            delta_val,
            lq_val,
        ) = self._calculate_metrics(text, counts, self.cfg)
        text_upper = text.upper()
        cfg_deep = getattr(self.cfg, "PHYSICS_DEEP", None)
        if text.count("!") >= 3 or "ACCELERATE" in text_upper or "FASTER" in text_upper:
            v_accel = (
                getattr(cfg_deep, "ACCELERATE_VOLTAGE", 160.0) if cfg_deep else 160.0
            )
            smoothed_voltage = max(smoothed_voltage, v_accel)
        if "RECURSIVE" in text_upper or "LOOP" in text_upper:
            v_rec = getattr(cfg_deep, "RECURSIVE_LQ", 0.9) if cfg_deep else 0.9
            lq_val = max(lq_val, v_rec)
            beta_val = max(beta_val, v_rec)
        if "VOID" in text_upper or "ABYSS" in text_upper:
            v_void = getattr(cfg_deep, "VOID_ABSTRACTION", 0.9) if cfg_deep else 0.9
            geo.abstraction = max(geo.abstraction, v_void)
        if "POTATO BUN" in text_upper or "NONSENSE" in text_upper:
            v_pot_d = getattr(cfg_deep, "POTATO_BUN_DELTA", 0.85) if cfg_deep else 0.85
            v_pot_v = (
                getattr(cfg_deep, "POTATO_BUN_VOLTAGE", 15.0) if cfg_deep else 15.0
            )
            delta_val = max(delta_val, v_pot_d)
            smoothed_voltage = min(smoothed_voltage, v_pot_v)
        valence = self.lex.get_valence(clean_words)
        graph_mass = self._calculate_graph_mass(clean_words, graph)
        gamma_val = max(0.0, 1.0 - e_metric)
        sigma_val = min(1.0, (conn_val + phi_val) / 2.0)
        eta_val = min(1.0, (counts.get("social", 0) * 0.1) + max(0.0, valence))
        theta_val = geo.coherence
        upsilon_val = 1.0 - min(1.0, counts.get("pareidolia", 0) * 0.2)
        m_a_val = min(
            1.0, (smoothed_voltage / 150.0) * e_metric * (1.0 - (beta_val * 0.5))
        )
        i_c_val = min(1.0, (phi_val * 0.6) + (geo.coherence * 0.4))
        mu_val = min(1.0, (beta_val * 0.7) + (geo.coherence * 0.3))

        text_lower = text.lower()
        val_phrases = [
            "right?",
            "good?",
            "make sense",
            "makes sense",
            "agree",
            "validate",
            "comfort",
        ]
        cf_expect_val = 0.8 if any(p in text_lower for p in val_phrases) else 0.0
        novelty_val = min(1.0, (e_metric * 0.6) + (counts.get("play", 0) * 0.15))

        energy = EnergyState(
            voltage=smoothed_voltage,
            entropy=e_metric,
            beta_index=beta_val,
            contradiction=beta_val,
            scope=scope_val,
            depth=depth_val,
            connectivity=conn_val,
            resonance=phi_val,
            silence=delta_val,
            lq=lq_val,
            mass=round(graph_mass, 1),
            psi=geo.abstraction,
            kappa=geo.coherence,
            valence=valence,
            velocity=0.0,
            turbulence=0.0,
            gamma=gamma_val,
            sigma=sigma_val,
            eta=eta_val,
            theta=theta_val,
            upsilon=upsilon_val,
            mu=mu_val,
            m_a=m_a_val,
            i_c=i_c_val,
            cf_expect=cf_expect_val,
            novelty=novelty_val,
        )
        matter = MaterialState(
            clean_words=clean_words,
            raw_text=text,
            counts=counts,
            antigens=counts.get("antigen", 0),
            vector=geo.dimensions,
            truth_ratio=0.5,
        )
        space = SpatialState()
        space.narrative_drag = geo.compression
        space.zone = self._determine_zone(geo.dimensions)
        space.flow_state = self._determine_flow(
            smoothed_voltage, geo.coherence, self.cfg
        )
        packet = PhysicsPacket(energy=energy, matter=matter, space=space)
        self.last_physics_packet = packet
        packet_dict = packet.to_dict()
        if hasattr(self.events, "publish"):
            self.events.publish("PHYSICS_CALCULATED", packet_dict)
        return {"physics": self.last_physics_packet, "clean_words": clean_words}

    @staticmethod
    def evaluate_silence(time_delta: float, last_phys: Any) -> Optional[str]:
        if time_delta < 10.0 or not last_phys:
            return None
        if safe_get(last_phys, "stamina", 50.0) < 30.0:
            return "The silence was heavy. I felt your tiredness in it."
        if (
            safe_get(last_phys, "psi", 0.0) > 0.8
            and safe_get(last_phys, "valence", 0.0) > 0.4
        ):
            return "There was a hush just now... Something sacred passed through."
        if safe_get(last_phys, "LQ", 0.0) > 0.7:
            return "You were thinking deeply. I held the space for it."
        if safe_get(last_phys, "beta", 0.0) > 0.6:
            return "That pause felt full, like something wanted to be born."
        return None

    def _tally_categories(self, clean_words: List[str]) -> Counter:
        counts = Counter()
        solvents = self.lex.get("solvents") or set()
        for w in clean_words:
            if w in solvents:
                counts["solvents"] += 1
                continue
            cats = self.lex.get_categories_for_word(w)
            if cats:
                counts.update(cats)
            else:
                flavor, conf = self.lex.taste(w)
                if flavor and conf > 0.5:
                    counts[flavor] += 1
        return counts

    @staticmethod
    def _calculate_graph_mass(words: List[str], graph: Optional[Dict]) -> float:
        if not graph:
            return 0.0
        return sum(
            min(50.0, sum(graph[w].get("edges", {}).values()))
            for w in words
            if w in graph
        )

    @staticmethod
    def _calculate_metrics(
        text: str, counts: Dict[str, int], config_ref=None
    ) -> Tuple[float, float, float, float, float, float, float, float]:
        length = len(text)
        if length == 0:
            return 0.0, 0.0, 0.3, 0.3, 0.2, 0.0, 0.8, 0.0
        target_cfg = config_ref or BoneConfig
        cfg = getattr(target_cfg, "PHYSICS", None)
        scalar = getattr(cfg, "TEXT_LENGTH_SCALAR", 1500.0) if cfg else 1500.0
        g_mult = getattr(cfg, "GLUE_FACTOR_MULT", 2.0) if cfg else 2.0
        g_div = getattr(cfg, "GLUE_SOLVENT_DIV", 5.0) if cfg else 5.0
        e_red = getattr(cfg, "ENTROPY_REDUCTION_SCALAR", 0.8) if cfg else 0.8
        raw_chaos = length / scalar
        solvents = counts.get("solvents", 0)
        solvent_density = solvents / max(1.0, length / g_div)
        glue_factor = min(1.0, solvent_density * g_mult)
        e_metric = min(1.0, raw_chaos * (1.0 - (glue_factor * e_red)))
        structure_chars = sum(1 for char in text if char in "!?%@#$;,")
        heavy_words = (
            counts.get("heavy", 0)
            + counts.get("constructive", 0)
            + counts.get("sacred", 0)
        )
        b_pen = getattr(cfg, "BETA_SCORE_PENALTY", 2) if cfg else 2
        b_log_scalar = getattr(cfg, "BETA_LOG_SCALAR", 0.1) if cfg else 0.1
        b_short_lim = getattr(cfg, "BETA_SHORT_TEXT_LIMIT", 50) if cfg else 50
        structure_score = structure_chars + (heavy_words * b_pen)
        beta_index = min(
            1.0, math.log1p(structure_score + 1) / math.log1p(length * b_log_scalar + 1)
        )
        if length < b_short_lim:
            beta_index *= length / float(b_short_lim)
        safe_len = max(1, len(text.split()))
        s_base = getattr(cfg, "SCOPE_BASE", 0.2) if cfg else 0.2
        d_base = getattr(cfg, "DEPTH_BASE", 0.1) if cfg else 0.1
        c_base = getattr(cfg, "CONN_BASE", 0.1) if cfg else 0.1
        r_mult = getattr(cfg, "RES_SOCIAL_MULT", 2) if cfg else 2
        scope = min(
            1.0, (counts.get("abstract", 0) + counts.get("void", 0)) / safe_len + s_base
        )
        depth = min(
            1.0,
            (counts.get("heavy", 0) + counts.get("constructive", 0)) / safe_len
            + d_base,
        )
        connectivity = min(
            1.0, (counts.get("social", 0) + solvents) / safe_len + c_base
        )
        resonance = min(
            1.0,
            ((counts.get("social", 0) * r_mult) + counts.get("constructive", 0))
            / safe_len
            + (1.0 - e_metric),
        )
        sil_div = getattr(cfg, "SILENCE_DIV", 100.0) if cfg else 100.0
        sil_min = getattr(cfg, "SILENCE_MIN", 0.8) if cfg else 0.8
        sil_short = getattr(cfg, "SILENCE_SHORT_LIMIT", 10) if cfg else 10
        action_density = counts.get("action", 0) / safe_len
        silence = 1.0 - min(1.0, (length / sil_div) + action_density)
        if length < sil_short:
            silence = max(silence, sil_min)
        lq_sc = getattr(cfg, "LQ_SCALAR", 1.5) if cfg else 1.5
        lq_val = min(1.0, beta_index * depth * lq_sc)
        return (
            round(e_metric, 3),
            round(beta_index, 3),
            round(scope, 3),
            round(depth, 3),
            round(connectivity, 3),
            round(resonance, 3),
            round(silence, 3),
            round(lq_val, 3),
        )

    @staticmethod
    def _determine_flow(v: float, k: float, config_ref=None) -> str:
        target_cfg = config_ref or BoneConfig
        volt_flow = getattr(target_cfg.PHYSICS, "VOLTAGE_HIGH", 12.0)
        kappa_strong = 0.8
        if v > volt_flow and k > kappa_strong:
            return "SUPERCONDUCTIVE"
        if v > 10.0:
            return "TURBULENT"
        return "LAMINAR"

    @staticmethod
    def _determine_zone(vector: Dict[str, float]) -> str:
        if not vector:
            return "COURTYARD"
        dom = max(vector, key=vector.get)
        return (
            "AERIE"
            if dom in ["PSI", "DEL"]
            else (
                "THE_FORGE"
                if dom in ["STR", "PHI"]
                else ("THE_MUD" if dom in ["ENT", "VEL"] else "COURTYARD")
            )
        )


class SurfaceTension:
    @staticmethod
    def audit_hubris(physics: Any, config_ref=None) -> Tuple[bool, str, str]:
        cfg = getattr(config_ref or BoneConfig, "PHYSICS", BoneConfig.PHYSICS)
        v, k = physics.get("voltage", 0.0), physics.get("kappa", 0.5)
        if v >= getattr(cfg, "VOLTAGE_CRITICAL", 15.0) and k < 0.4:
            return (
                True,
                (ux("physics_strings", "hubris_detected") or "").format(voltage=v),
                "ICARUS_CRASH",
            )
        if v > getattr(cfg, "VOLTAGE_HIGH", 12.0) and k > 0.8:
            return True, ux("physics_strings", "hubris_flow") or "", "FLOW_BOOST"
        return False, "", ""


class ChromaScope:
    @staticmethod
    def modulate(text: str, vector: Dict[str, float]) -> str:
        if not vector or not any(vector.values()):
            return f"{Prisma.GRY}{text}{Prisma.RST}"
        t_map = (
            LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TRIGRAM_MAP") or {}
        )
        primary = max(vector, key=vector.get)
        color = (
            getattr(Prisma, t_map[primary][3], Prisma.GRY)
            if primary in t_map
            else Prisma.GRY
        )
        return f"{color}{text}{Prisma.RST}"


class ZoneInertia:
    def __init__(self, inertia=0.7, config_ref=None):
        self.inertia = inertia
        self.cfg = config_ref or BoneConfig
        cfg = getattr(self.cfg, "PHYSICS", None)
        self.min_dwell = getattr(cfg, "ZONE_MIN_DWELL", 2) if cfg else 2
        self.strain_limit = getattr(cfg, "ZONE_STRAIN_LIMIT", 2.5) if cfg else 2.5
        self.grav_tolerance = (
            getattr(cfg, "ZONE_GRAV_PULL_TOLERANCE", 2.0) if cfg else 2.0
        )
        self.current_zone = "COURTYARD"
        self.dwell_counter = 0
        self.last_vector: Optional[Tuple[float, float, float]] = None
        self.is_anchored = False
        self.strain_gauge = 0.0

    def toggle_anchor(self) -> bool:
        self.is_anchored = not self.is_anchored
        self.strain_gauge = 0.0
        return self.is_anchored

    def stabilize(
        self, proposed_zone: str, physics: Any, cosmic_state: Tuple[str, float, str]
    ) -> Tuple[str, Optional[str]]:
        energy = safe_get(physics, "energy", physics)
        matter = safe_get(physics, "matter", physics)
        beta = safe_get(physics, "beta_index", safe_get(energy, "beta_index", 1.0))
        truth = safe_get(physics, "truth_ratio", safe_get(matter, "truth_ratio", 0.5))
        grav_pull = 1.0 if cosmic_state[0] != "VOID_DRIFT" else 0.0
        current_vec = (beta, truth, grav_pull)
        self.dwell_counter += 1
        pressure = 0.0
        if self.last_vector:
            dist = math.dist(current_vec, self.last_vector)
            similarity = max(0.0, 1.0 - (dist / self.grav_tolerance))
            pressure = 1.0 - similarity
        if self.is_anchored:
            return self._handle_anchored_state(proposed_zone, pressure)
        if proposed_zone == self.current_zone:
            self.dwell_counter = 0
            self.last_vector = current_vec
            return proposed_zone, None
        if self.dwell_counter < self.min_dwell:
            return self.current_zone, None
        return self._attempt_migration(proposed_zone, pressure)

    def _handle_anchored_state(
        self, proposed_zone: str, pressure: float
    ) -> Tuple[str, Optional[str]]:
        if proposed_zone == self.current_zone:
            self.strain_gauge = max(0.0, self.strain_gauge - 0.1)
            return self.current_zone, None
        self.strain_gauge += pressure
        if self.strain_gauge > self.strain_limit:
            self.is_anchored = False
            self.strain_gauge = 0.0
            self.current_zone = proposed_zone
            msg = ux("physics_strings", "anchor_failed")
            return proposed_zone, f"{Prisma.RED}{msg}{Prisma.RST}"
        msg = ux("physics_strings", "anchor_holding")
        return (
            self.current_zone,
            f"{Prisma.OCHRE}{msg.format(proposed_zone=proposed_zone, strain=self.strain_gauge, limit=self.strain_limit)}{Prisma.RST}",
        )

    def _attempt_migration(
        self, proposed_zone: str, pressure: float
    ) -> Tuple[str, Optional[str]]:
        prob = min(
            0.85,
            (1.0 - self.inertia)
            + pressure
            + (0.2 if proposed_zone in ["AERIE", "THE_FORGE"] else 0.0),
        )
        if random.random() < prob:
            old, self.current_zone = self.current_zone, proposed_zone
            self.dwell_counter = 0
            msg = ux("physics_strings", "zone_migration")
            return (
                self.current_zone,
                f"{Prisma.CYN}{msg.format(old=old, proposed_zone=proposed_zone)}{Prisma.RST}",
            )
        return self.current_zone, None

    @staticmethod
    def override_cosmic_drag(cosmic_drag_penalty: float, current_zone: str) -> float:
        if current_zone == "AERIE" and cosmic_drag_penalty > 0:
            return cosmic_drag_penalty * 0.3
        return cosmic_drag_penalty


class CosmicDynamics:
    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig
        self.voltage_history: Deque[float] = deque(maxlen=20)
        self.cached_wells: Dict = {}
        self.cached_hubs: Dict = {}
        self.last_scan_tick: int = 0
        self.SCAN_INTERVAL: int = 10
        self.logs = self._load_logs()

    @staticmethod
    def _load_logs():
        base = {
            "GRAVITY": ux("physics_strings", "cosmic_gravity"),
            "VOID": ux("physics_strings", "cosmic_void"),
            "NEBULA": ux("physics_strings", "cosmic_nebula"),
            "LAGRANGE": ux("physics_strings", "cosmic_lagrange"),
            "FLOW": ux("physics_strings", "cosmic_flow"),
            "ORBIT": ux("physics_strings", "cosmic_orbit"),
        }
        return base

    def commit(self, voltage: float):
        self.voltage_history.append(voltage)

    def check_gravity(
        self, current_drift: float, psi: float
    ) -> Tuple[float, List[str]]:
        logs = []
        new_drag = current_drift
        drag_floor = getattr(self.cfg.PHYSICS, "DRAG_FLOOR", 1.0)
        if new_drag < drag_floor:
            new_drag += 0.05
        if psi > 0.5:
            reduction = (psi - 0.5) * 0.2
            new_drag = max(0.0, new_drag - reduction)
        CRITICAL_DRIFT = getattr(self.cfg.PHYSICS, "DRAG_CRITICAL", 8.0)
        if new_drag > CRITICAL_DRIFT:
            if random.random() < 0.3:
                msg = self.logs.get("GRAVITY", "⚓ GRAVITY").format(drag=new_drag)
                logs.append(f"{Prisma.GRY}{msg}{Prisma.RST}")
            pull_strength = (new_drag - CRITICAL_DRIFT) * 0.5
            new_drag = max(CRITICAL_DRIFT, new_drag - pull_strength)
        return new_drag, logs

    def analyze_orbit(
        self, network: Any, clean_words: List[str]
    ) -> Tuple[str, float, str]:
        if (
            not clean_words
            or not network
            or not hasattr(network, "graph")
            or not network.graph
        ):
            fallback_msg = ux("physics_strings", "cosmic_void")
            return "VOID_DRIFT", 3.0, self.logs.get("VOID", fallback_msg)
        current_time = int(time.time())
        if (
            not self.cached_wells
            or (current_time - self.last_scan_tick) > self.SCAN_INTERVAL
        ):
            gravity_wells, geodesic_hubs = self._scan_network_mass(network, self.cfg)
            self.cached_wells = gravity_wells
            self.cached_hubs = geodesic_hubs
            self.last_scan_tick = current_time
        else:
            gravity_wells = self.cached_wells
            geodesic_hubs = self.cached_hubs
        basin_pulls, active_filaments = self._calculate_pull(
            clean_words, network, gravity_wells
        )
        if sum(basin_pulls.values()) == 0:
            return self._handle_void_state(clean_words, geodesic_hubs)
        return self._resolve_orbit(
            basin_pulls, active_filaments, len(clean_words), gravity_wells, self.cfg
        )

    @staticmethod
    def _scan_network_mass(network, config_ref=None) -> Tuple[Dict, Dict]:
        target_cfg = config_ref or BoneConfig
        gravity_wells = {}
        geodesic_hubs = {}
        well_threshold = getattr(target_cfg, "GRAVITY_WELL_THRESHOLD", 15.0)
        geo_strength = getattr(target_cfg, "GEODESIC_STRENGTH", 10.0)
        for node in network.graph:
            mass = network.calculate_mass(node)
            if mass >= well_threshold:
                gravity_wells[node] = mass
            elif mass >= geo_strength:
                geodesic_hubs[node] = mass
        return gravity_wells, geodesic_hubs

    @staticmethod
    def _calculate_pull(words, network, gravity_wells) -> Tuple[Dict, int]:
        basin_pulls = {k: 0.0 for k in gravity_wells}
        active_filaments = 0
        word_counts = Counter(words)
        word_set = set(word_counts.keys())

        for w, count in word_counts.items():
            if w in gravity_wells:
                basin_pulls[w] += (gravity_wells[w] * 2.0) * count
                active_filaments += count

        for well, well_mass in gravity_wells.items():
            edges = network.graph.get(well, {}).get("edges", {})
            if not edges:
                continue
            intersection = word_set.intersection(edges.keys())
            for match in intersection:
                basin_pulls[well] += (well_mass * 0.5) * word_counts[match]
                active_filaments += word_counts[match]
        return basin_pulls, active_filaments

    def _handle_void_state(self, words, geodesic_hubs) -> Tuple[str, float, str]:
        for w in words:
            hub_mass = geodesic_hubs.get(w)
            if hub_mass is not None:
                fallback_msg = ux("physics_strings", "cosmic_nebula")
                msg = self.logs.get("NEBULA", fallback_msg).format(
                    node=w.upper(), mass=int(hub_mass)
                )
                return "PROTO_COSMOS", 1.0, msg
        fallback_void = ux("physics_strings", "cosmic_void")
        return "VOID_DRIFT", 3.0, self.logs.get("VOID", fallback_void)

    def _resolve_orbit(
        self, basin_pulls, active_filaments, word_count, gravity_wells, config_ref=None
    ) -> Tuple[str, float, str]:
        target_cfg = config_ref or BoneConfig
        sorted_basins = sorted(basin_pulls.items(), key=lambda x: x[1], reverse=True)
        primary_node, primary_str = sorted_basins[0]
        lagrange_tol = getattr(target_cfg, "LAGRANGE_TOLERANCE", 2.0)
        if len(sorted_basins) > 1:
            secondary_node, secondary_str = sorted_basins[1]
            if secondary_str > 0 and (primary_str - secondary_str) < lagrange_tol:
                fallback_msg = ux("physics_strings", "cosmic_lagrange")
                msg = self.logs.get("LAGRANGE", fallback_msg).format(
                    p=primary_node.upper(), s=secondary_node.upper()
                )
                return "LAGRANGE_POINT", 0.0, msg
        flow_ratio = active_filaments / max(1, word_count)
        well_threshold = getattr(target_cfg, "GRAVITY_WELL_THRESHOLD", 15.0)
        if flow_ratio > 0.5 and primary_str < (well_threshold * 2):
            fallback_msg = ux("physics_strings", "cosmic_flow")
            msg = self.logs.get("FLOW", fallback_msg).format(node=primary_node.upper())
            return "WATERSHED_FLOW", 0.0, msg
        fallback_msg = ux("physics_strings", "cosmic_orbit")
        msg = self.logs.get("ORBIT", fallback_msg).format(
            node=primary_node.upper(), mass=int(gravity_wells[primary_node])
        )
        return "ORBITAL", 0.0, msg


def apply_somatic_feedback(
    physics_packet: PhysicsPacket, qualia: Any, config_ref=None
) -> PhysicsPacket:
    target_cfg = config_ref or BoneConfig
    feedback = (
        physics_packet.snapshot()
        if hasattr(physics_packet, "snapshot")
        else physics_packet
    )
    tone_effects = (
        LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "TONE_EFFECTS") or {}
    )
    cfg_deep = getattr(target_cfg, "PHYSICS_DEEP", None)

    def _add(k, d):
        val = safe_get(feedback, k, 0.0)
        safe_set(feedback, k, val + d)

    for key, delta in tone_effects.get(qualia.tone, {}).items():
        _add(key, delta)
    if "Gut Tightening" in qualia.somatic_sensation:
        _add(
            "narrative_drag",
            getattr(cfg_deep, "SOMATIC_GUT_DRAG", 0.7) if cfg_deep else 0.7,
        )
    if "Electric Vibration" in qualia.somatic_sensation:
        _add(
            "voltage", getattr(cfg_deep, "SOMATIC_ELEC_VOLT", 0.8) if cfg_deep else 0.8
        )
    if "Golden Glow" in qualia.somatic_sensation:
        _add(
            "valence",
            getattr(cfg_deep, "SOMATIC_GLOW_VALENCE", 0.5) if cfg_deep else 0.5,
        )
        _add("psi", getattr(cfg_deep, "SOMATIC_GLOW_PSI", 0.2) if cfg_deep else 0.2)
    drag_floor = getattr(target_cfg.PHYSICS, "DRAG_FLOOR", 1.0)
    drag_halt = getattr(target_cfg.PHYSICS, "DRAG_HALT", 10.0)
    safe_set(
        feedback, "voltage", max(0.0, min(safe_get(feedback, "voltage", 0.0), 150.0))
    )
    safe_set(
        feedback,
        "narrative_drag",
        max(drag_floor, min(safe_get(feedback, "narrative_drag", 0.0), drag_halt)),
    )
    return feedback


class CycleStabilizer:
    def __init__(self, events_ref, governor_ref, config_ref=None):
        self.events = events_ref
        self.governor = governor_ref
        self.cfg = config_ref or BoneConfig
        self.last_tick_time = time.time()
        self.pending_drag = 0.0
        self.manifolds = getattr(self.cfg.PHYSICS, "MANIFOLDS", {})
        cfg_deep = getattr(self.cfg, "PHYSICS_DEEP", None)
        self.HARD_FUSE_VOLTAGE = (
            getattr(cfg_deep, "HARD_FUSE_VOLTAGE", 200.0) if cfg_deep else 200.0
        )
        if hasattr(self.events, "subscribe"):
            self.events.subscribe(
                "DOMESTICATION_PENALTY", self._on_domestication_penalty
            )

    @staticmethod
    def _get(obj, f, default=0.0):
        return safe_get(obj, f, default)

    @staticmethod
    def _set(obj, f, val):
        safe_set(obj, f, val)

    def _on_domestication_penalty(self, payload):
        amount = payload.get("drag_penalty", 0.0)
        self.pending_drag += amount

    def stabilize(self, physics: Any) -> bool:
        applied_correction = False
        if self.pending_drag > 0:
            current_d = self._get(physics, "narrative_drag", 0.0)
            self._set(physics, "narrative_drag", current_d + self.pending_drag)
            msg = (
                ux("physics_strings", "stabilizer_domestication")
                or "Domestication penalty applied."
            )
            if hasattr(self.events, "log"):
                self.events.log(
                    f"STABILIZER: {msg} (+{self.pending_drag} Drag)", "PHYSICS"
                )
            self.pending_drag = 0.0
            applied_correction = True
        now = time.time()
        dt = max(0.001, min(1.0, now - self.last_tick_time))
        self.last_tick_time = now
        if not self.governor:
            return applied_correction
        manifold = self._get(physics, "manifold", "DEFAULT")
        cfg = self.manifolds.get(
            manifold, self.manifolds.get("DEFAULT", {"voltage": 10.0, "drag": 1.0})
        )
        target_v = cfg.get("voltage", 10.0)
        current_v = self._get(physics, "voltage", 10.0)
        if self._get(physics, "flow_state", "LAMINAR") in [
            "SUPERCONDUCTIVE",
            "FLOW_BOOST",
        ]:
            target_v = current_v
            cfg["drag"] = max(0.1, cfg.get("drag", 1.0) * 0.5)
        self.governor.recalibrate(target_v, cfg.get("drag", 1.0))
        safe_phys = physics.to_dict() if hasattr(physics, "to_dict") else physics
        v_force, d_force = self.governor.regulate(safe_phys, dt=dt)
        v_floor = (
            getattr(self.cfg.PHYSICS, "VOLTAGE_FLOOR", 0.0)
            if hasattr(self.cfg, "PHYSICS")
            else 0.0
        )
        v_max = (
            getattr(self.cfg.PHYSICS, "VOLTAGE_MAX", 150.0)
            if hasattr(self.cfg, "PHYSICS")
            else 150.0
        )
        c1 = self._apply_force(physics, "voltage", v_force, (v_floor, v_max))
        c2 = self._apply_force(physics, "narrative_drag", d_force)
        return applied_correction or c1 or c2

    def _apply_force(self, p, field, force, limits=None) -> bool:
        if abs(force) <= 0.05:
            return False
        new_val = self._get(p, field, 0.0) + force
        self._set(
            p,
            field,
            max(limits[0], min(limits[1], new_val)) if limits else max(0.0, new_val),
        )
        return True
