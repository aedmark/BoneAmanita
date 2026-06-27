"""physics/geodesics.py"""

import math
from dataclasses import dataclass
from typing import Dict, List

from presets import BoneConfig
from struts import safe_get


@dataclass
class GeodesicVector:
    tension: float
    compression: float
    coherence: float
    abstraction: float
    dimensions: Dict[str, float]


class GeodesicEngine:
    _GC_CACHE = None
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
        mass_dict: Dict[str, float] = {
            str(k): float(counts.get(k, 0)) for k in GeodesicEngine._MASS_KEYS
        }
        return mass_dict

    @staticmethod
    def _calculate_forces(
        masses: Dict[str, float], counts: Dict[str, int], volume: int, config_ref=None
    ) -> Dict[str, float]:
        t_cfg = config_ref or BoneConfig
        cfg = safe_get(t_cfg, "PHYSICS", {})

        def get_cfg(key: str, default: float = 1.0) -> float:
            return float(safe_get(cfg, key, default))

        if GeodesicEngine._GC_CACHE is None:
            from core import LoreManifest

            GeodesicEngine._GC_CACHE = (
                LoreManifest.get_instance().get(
                    "PHYSICS_CONSTANTS", "GEODESIC_CONSTANTS"
                )
                or {}
            )
        gc_dict = GeodesicEngine._GC_CACHE

        def get_const(key: str, default: float = 1.0) -> float:
            return float(safe_get(gc_dict, key, default))

        shapley_thresh = float(safe_get(t_cfg, "SHAPLEY_MASS_THRESHOLD", 5.0))
        safe_vol = volume
        tot_kin = masses["kinetic"] + masses["explosive"]
        raw_tension = (
            masses["heavy"] * get_cfg("WEIGHT_HEAVY", 2.0)
            + tot_kin * get_cfg("WEIGHT_KINETIC", 1.5)
            + masses["explosive"] * get_cfg("WEIGHT_EXPLOSIVE", 3.0)
            + masses["constructive"] * get_cfg("WEIGHT_CONSTRUCTIVE", 1.2)
        )
        mass_scalar = min(
            1.0, safe_vol / (shapley_thresh * get_const("SQUELCH_LIMIT_MULT", 2.0))
        )
        if safe_vol < get_const("SAFE_VOL_THRESHOLD", 50):
            mass_scalar *= get_const("MIN_VOLUME_SCALAR", 0.5)
        base_friction = math.log1p(max(0, counts.get("suburban", 0))) * get_const(
            "SUBURBAN_FRICTION_LOG_BASE", 0.5
        )
        heavy_friction = masses["heavy"] * get_const("HEAVY_FRICTION_MULT", 1.2)
        lubrication = 1.0 + counts.get("solvents", 0) * get_const(
            "SOLVENT_LUBRICATION_FACTOR", 0.2
        )
        shear = 1.0 + (tot_kin / safe_vol) * get_const("SHEAR_RESISTANCE_SCALAR", 0.1)
        visc = ((base_friction + heavy_friction) * shear) / lubrication
        lift = masses["play"] * get_const("PLAY_LIFT_MULT", 1.5) + (
            tot_kin * get_const("KINETIC_LIFT_RATIO", 0.8)
        ) / (masses["heavy"] * 0.5 + 1.0)
        signal_drag_mult = float(safe_get(t_cfg, "SIGNAL_DRAG_MULTIPLIER", 1.0))
        kinetic_gain = float(safe_get(t_cfg, "KINETIC_GAIN", 1.0))
        raw_comp = (
            ((visc - lift) / safe_vol)
            * get_const("COMPRESSION_SCALAR", 2.0)
            * signal_drag_mult
        )
        str_mass = max(
            0.0,
            masses["heavy"]
            + masses["constructive"]
            + masses["harvest"]
            - masses["void"] * 0.5,
        )
        coherence_val = min(1.0, str_mass / max(1.0, shapley_thresh))
        abstract_mass = (
            masses["abstract"]
            + masses["liminal"]
            + masses["pareidolia"]
            + masses["void"]
        )
        abstraction_val = min(
            1.0, (abstract_mass / safe_vol) + get_const("ABSTRACTION_BASE", 0.1)
        )
        max_tension = min(
            100.0,
            (raw_tension / safe_vol)
            * get_const("DENSITY_SCALAR")
            * kinetic_gain
            * mass_scalar,
        )
        clamped_comp = max(
            -5.0, min(get_cfg("DRAG_HALT", 10.0), raw_comp * mass_scalar)
        )
        return {
            "tension": round(max_tension, 2),
            "compression": round(clamped_comp, 2),
            "coherence": round(coherence_val, 3),
            "abstraction": round(abstraction_val, 2),
        }

    @staticmethod
    def _clamp(v: float) -> float:
        return max(0.0, min(1.0, v))

    @staticmethod
    def _calculate_dimensions(masses, forces, counts, volume) -> Dict[str, float]:
        inv_vol = 1.0 / volume
        base_mass = 0.1
        clamp = GeodesicEngine._clamp

        return {
            "VEL": clamp(
                (masses["kinetic"] * 2.0 - forces["compression"] + base_mass) * inv_vol
            ),
            "STR": clamp(
                (
                    masses["heavy"] * 2.0
                    + masses["constructive"]
                    + masses["harvest"]
                    + base_mass
                )
                * inv_vol
            ),
            "ENT": clamp(
                (
                    (counts.get("antigen", 0) * 3.0)
                    + masses["meat"]
                    + masses["crisis_term"]
                )
                * inv_vol
            ),
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
        v_new = [sum(row[j] * v[j] for j in range(len(v))) for row in q_matrix]
        return {
            k: round(abs(val), 3) for k, val in zip(GeodesicEngine._DIM_ORDER, v_new)
        }
