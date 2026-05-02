"""physics/geodesics.py"""

import math
from dataclasses import dataclass
from typing import Dict, List
from presets import BoneConfig

@dataclass
class GeodesicVector:
    """
    The physical manifestation of a thought or prompt.
    Instead of just viewing input as a string of text, the system treats it as a
    physical object with these structural properties.
    """
    tension: float       # The expansive, kinetic energy of the prompt (pushing forward).
    compression: float   # The structural drag or friction of the prompt (holding back).
    coherence: float     # How structurally sound the logic is (Resistance to entropy).
    abstraction: float   # How untethered the prompt is from physical reality (The Void).
    dimensions: Dict[str, float] # The 8-dimensional coordinates of the thought in the semantic space.

class GeodesicEngine:
    """
    The core semantic physics engine.
    Translates raw word counts and semantic categories into physical forces and multi-dimensional vectors.
    """

    # The 8 core axes of the system's coordinate space.
    # VEL (Velocity/Action), STR (Structure/Logic), ENT (Entropy/Chaos), PHI (Focus/Density)
    # PSI (Void/Abstraction), BET (Connection/Empathy), DEL (Play/Joy), E (Fluidity/Solvents)
    _DIM_ORDER = ("VEL", "STR", "ENT", "PHI", "PSI", "BET", "DEL", "E")

    # The 'fundamental particles' of the semantic engine. Words are categorized into these masses.
    _MASS_KEYS = ("heavy", "kinetic", "constructive", "abstract", "play", "social", "explosive", "void", "liminal", "meat", "harvest", "pareidolia", "crisis_term")

    _CACHED_CONSTANTS = None

    @staticmethod
    def collapse_wavefunction(clean_words: List[str], counts: Dict[str, int], config_ref=None) -> GeodesicVector:
        """
        Takes a raw, unstructured cloud of semantic data (the prompt) and collapses it
        into a definitive, physical state vector that the system can react to.
        """
        target_cfg = config_ref or BoneConfig
        volume = max(1, len(clean_words)) # Prevent division by zero

        # 1. Weigh the raw semantic mass of the input.
        masses = GeodesicEngine._weigh_mass(counts)

        # 2. Calculate the pushing and pulling forces based on that mass.
        forces = GeodesicEngine._calculate_forces(masses, counts, volume, target_cfg)

        # 3. Map the forces into the 8-dimensional coordinate space.
        dimensions = GeodesicEngine._calculate_dimensions(masses, forces, counts, volume)

        return GeodesicVector(
            tension=forces["tension"],
            compression=forces["compression"],
            coherence=forces["coherence"],
            abstraction=forces["abstraction"],
            dimensions=dimensions,
        )

    @staticmethod
    def _weigh_mass(counts: Dict[str, int]) -> Dict[str, float]:
        """Maps raw semantic categories into float mass values."""
        return {k: float(counts.get(k, 0)) for k in GeodesicEngine._MASS_KEYS}

    @staticmethod
    def _calculate_forces(masses: Dict[str, float], counts: Dict[str, int], volume: int, config_ref=None) -> Dict[str, float]:
        """
        The heavy lifting of the physics engine. Calculates how the different
        types of semantic mass interact to create tension and drag.
        """
        t_cfg = config_ref or BoneConfig
        cfg = getattr(t_cfg, "PHYSICS", BoneConfig.PHYSICS)

        if GeodesicEngine._CACHED_CONSTANTS is None:
            from core import LoreManifest
            GeodesicEngine._CACHED_CONSTANTS = LoreManifest.get_instance().get("PHYSICS_CONSTANTS", "GEODESIC_CONSTANTS") or {}
        gc_dict = GeodesicEngine._CACHED_CONSTANTS

        def get_cfg(key: str, default: float = 1.0) -> float:
            return getattr(cfg, key, default)

        def get_const(key: str, default: float = 1.0) -> float:
            return gc_dict.get(key, default)

        shapley_thresh = getattr(t_cfg, "SHAPLEY_MASS_THRESHOLD", 5.0)
        safe_vol = max(1, volume)
        tot_kin = masses["kinetic"] + masses["explosive"]

        # Tension is the expansive force. Heavy, kinetic, and explosive words increase tension.
        raw_tension = (
            masses["heavy"] * get_cfg("WEIGHT_HEAVY", 2.0)
            + tot_kin * get_cfg("WEIGHT_KINETIC", 1.5)
            + masses["explosive"] * get_cfg("WEIGHT_EXPLOSIVE", 3.0)
            + masses["constructive"] * get_cfg("WEIGHT_CONSTRUCTIVE", 1.2)
        )

        # Scale the physical impact based on the total volume of words.
        # A few explosive words in a massive text block have less impact than in a short sentence.
        mass_scalar = min(1.0, safe_vol / (shapley_thresh * get_const("SQUELCH_LIMIT_MULT", 2.0)))
        if safe_vol < get_const("SAFE_VOL_THRESHOLD", 50):
            mass_scalar *= get_const("MIN_VOLUME_SCALAR", 0.5)

        # --- DRAG / COMPRESSION CALCULATIONS ---
        # Friction: Boring/bureaucratic (suburban) words and structurally dense (heavy) words slow things down.
        base_friction = math.log1p(max(0, counts.get("suburban", 0))) * get_const("SUBURBAN_FRICTION_LOG_BASE", 0.5)
        heavy_friction = masses["heavy"] * get_const("HEAVY_FRICTION_MULT", 1.2)

        # Lubrication: Emotional or fluid words (solvents) reduce friction.
        lubrication = 1.0 + counts.get("solvents", 0) * get_const("SOLVENT_LUBRICATION_FACTOR", 0.2)

        # Shear: High kinetic energy in a small space creates shear resistance.
        shear = 1.0 + (tot_kin / safe_vol) * get_const("SHEAR_RESISTANCE_SCALAR", 0.1)

        # Total Viscosity: How thick/difficult the text is to move through.
        # Meadows: Shear is a resistance vector, so it multiplies friction rather than dividing it.
        visc = ((base_friction + heavy_friction) * shear) / lubrication

        # Lift: Playful words and kinetic energy provide upward momentum, countering viscosity.
        lift = masses["play"] * get_const("PLAY_LIFT_MULT", 1.5) + (tot_kin * get_const("KINETIC_LIFT_RATIO", 0.8)) / (masses["heavy"] * 0.5 + 1.0)

        # Compression is the final drag value (Viscosity minus Lift).
        raw_comp = (
            ((visc - lift) / safe_vol) * get_const("COMPRESSION_SCALAR", 2.0) * getattr(t_cfg, "SIGNAL_DRAG_MULTIPLIER", 1.0)
        )

        # --- STRUCTURAL INTEGRITY ---
        # Coherence: The ratio of solid, structural mass against the void/emptiness.
        str_mass = max(0.0, masses["heavy"] + masses["constructive"] + masses["harvest"] - masses["void"] * 0.5)
        coherence_val = min(1.0, str_mass / max(1.0, shapley_thresh))

        # Abstraction: The ratio of untethered/dreamlike mass to the total volume.
        abstract_mass = masses["abstract"] + masses["liminal"] + masses["pareidolia"] + masses["void"]
        abstraction_val = min(1.0, (abstract_mass / safe_vol) + get_const("ABSTRACTION_BASE", 0.1))

        # Clamp final values for system stability.
        max_tension = min(100.0, (raw_tension / safe_vol) * get_const("DENSITY_SCALAR") * getattr(t_cfg, "KINETIC_GAIN", 1.0) * mass_scalar)
        clamped_comp = max(-5.0, min(get_cfg("DRAG_HALT", 10.0), raw_comp * mass_scalar))

        return {"tension": round(max_tension, 2), "compression": round(clamped_comp, 2),
                "coherence": round(coherence_val, 3), "abstraction": round(abstraction_val, 2), }

    @staticmethod
    def _calculate_dimensions(masses, forces, counts, volume) -> Dict[str, float]:
        """
        Translates the physical masses into the 8 core dimensions of the system's mind state.
        Returns a normalized vector where each axis is clamped between 0.0 and 1.0.
        """
        inv_vol = 1.0 / max(1, volume)
        base_mass = 0.1 # Prevents vectors from zeroing out entirely

        def clamp(v: float) -> float:
            return max(0.0, min(1.0, v))

        return {
            "VEL": clamp((masses["kinetic"] * 2.0 - forces["compression"] + base_mass) * inv_vol),           # Velocity
            "STR": clamp((masses["heavy"] * 2.0 + masses["constructive"] + masses["harvest"] + base_mass) * inv_vol), # Structure
            "ENT": clamp(((counts.get("antigen", 0) * 3.0) + masses["meat"] + masses["crisis_term"]) * inv_vol),      # Entropy/Chaos
            "PHI": clamp((masses["heavy"] + masses["kinetic"] + base_mass) * inv_vol),                       # Focus/Intensity
            "PSI": clamp(forces["abstraction"]),                                                             # Void/Liminality
            "BET": clamp((masses["social"] * 2.0) * inv_vol),                                                # Connection/Social
            "DEL": clamp((masses["play"] * 3.0) * inv_vol),                                                  # Play/Joy
            "E":   clamp(counts.get("solvents", 0) * inv_vol),                                               # Fluidity
        }

    @staticmethod
    def apply_path_reflection(dimensions: Dict[str, float], q_matrix: List[List[float]]) -> Dict[str, float]:
        """
        Allows environmental states (like trauma or high voltage) to warp the thought vector
        via matrix multiplication. Bends the path of the thought based on the system's current geometry.
        """
        v = [dimensions.get(k, 0.0) for k in GeodesicEngine._DIM_ORDER]
        # Standard dot product of the transformation matrix and the dimension vector
        v_new = [sum(row[j] * v[j] for j in range(len(v))) for row in q_matrix]

        # Round and ensure absolute values to prevent negative dimension coordinates
        return {k: round(abs(val), 3) for k, val in zip(GeodesicEngine._DIM_ORDER, v_new)}