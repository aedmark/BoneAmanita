"""spores/genetics.py
This module defines the evolutionary and reproductive systems of the engine.
Instead of loading static configurations every time, the system can "reproduce"
by saving its current state as a Spore. These spores carry genetic mutations,
inherited trauma, and adapted vocabulary, allowing the system to evolve
new conversational metabolisms over successive generations.
Classes:
    - LiteraryReproduction: The biological controller for spawning offspring states
      (Mitosis) or merging two distinct session states (Crossover).
"""
import json
import random
from typing import Tuple, Dict
from core import LoreManifest
from struts import ux, safe_get
from presets import BoneConfig
from spores.spore_utils import _access_config_path


class LiteraryReproduction:
    """
    Handles the genetic algorithms of the conversational engine.
    It dictates how system parameters drift (mutate) and how
    experiential data (like trauma vectors or specific lexicon adaptations)
    are passed down to the next instance of the engine.
    """
    MUTATIONS = {}
    JOY_CLADE = {}
    MUTATION_TABLE = [
        ("MAX_DRAG_LIMIT", 1.0, 20.0, 0.3),
        ("TOXIN_WEIGHT", 0.1, 5.0, 0.3),
        ("MAX_HEALTH", 50.0, 500.0, 0.1),
        ("PHYSICS.VOLTAGE_MAX", 10.0, 100.0, 0.2),
        ("BIO.REWARD_MEDIUM", 0.01, 1.0, 0.2),
        ("COUNCIL.MANIC_VOLTAGE_TRIGGER", 10.0, 50.0, 0.1),
        ("PRIORITY_LEARNING_RATE", 0.5, 5.0, 0.15)
    ]

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig

    @classmethod
    def load_genetics(cls, config_ref=None):
        """
        Extracts foundational genetic structures and predetermined mutation profiles
        from the overarching lore manifest.
        """
        try:
            target_cfg = config_ref or BoneConfig
            genetics = (LoreManifest.get_instance(config_ref=target_cfg).get("GENETICS")
                        or {})
            cls.MUTATIONS = genetics.get("MUTATIONS", {})
            cls.JOY_CLADE = genetics.get("JOY_CLADE", {})
        except Exception:
            cls.MUTATIONS = {}
            cls.JOY_CLADE = {}

    @staticmethod
    def mutate_config(current_config):
        """
        Applies genetic drift (radiation) to the base configuration.
        Iterates through the MUTATION_TABLE; if the probability check passes,
        the parameter's value is slightly shifted (±10%) but clamped within safe bounds.
        """
        mutated_config = {}
        for key, min_v, max_v, chance in LiteraryReproduction.MUTATION_TABLE:
            if random.random() < chance:
                current_val = _access_config_path(current_config, key)
                if current_val is not None:
                    mutated_val = current_val * random.uniform(0.9, 1.1)
                    clamped_val = max(min_v, min(max_v, mutated_val))
                    mutated_config[key] = clamped_val
        return mutated_config

    def mitosis(self, parent_id, bio_state, physics):
        """
        Asexual reproduction. Spawns a child spore directly from the current session's state.
        The child's "flavor" (trait) is heavily influenced by whatever semantic archetype
        was dominant at the exact moment of reproduction.
        """
        counts = safe_get(physics, "counts", {})
        dominant = max(counts, key=counts.get) if counts else "VOID"
        mutation_data = LiteraryReproduction.MUTATIONS.get(dominant.upper(),
                                                           {"trait": "NEUTRAL", "mod": {}, "lexicon": []})
        child_trait = mutation_data.get("trait", "NEUTRAL")
        child_id = f"{parent_id}_({child_trait})"
        config_mutations = LiteraryReproduction.mutate_config(self.cfg)
        config_mutations.update(mutation_data.get("mod", {}))
        lexicon_mutations = {dominant.lower(): mutation_data.get("lexicon", [])}
        trauma_vec = bio_state.get("trauma_vector", {})
        child_genome = {
            "source": "MITOSIS",
            "parent_a": parent_id,
            "parent_b": None,
            "lexicon_mutations": lexicon_mutations,
            "config_mutations": config_mutations,
            "dominant_flavor": dominant,
            "trauma_inheritance": trauma_vec,
        }
        return child_id, child_genome

    def crossover(self, parent_a_id, parent_a_bio, parent_b_path):
        """
        Sexual reproduction / Hybridization.
        Merges the current session (Parent A) with a saved spore file (Parent B).
        Traits, trauma, and metabolic enzymes are averaged or combined.
        """
        try:
            with open(parent_b_path, "r", encoding="utf-8") as f:
                parent_b_data = json.load(f)
        except Exception:
            return None, ux("spore_strings", "repro_corrupt_spore")
        parent_b_id = parent_b_data.get("session_id", "UNKNOWN")
        trauma_a = parent_a_bio.get("trauma_vector") or {}
        trauma_b = parent_b_data.get("trauma_vector") or {}
        all_keys = trauma_a.keys() | trauma_b.keys()
        child_trauma = {
            k: (trauma_a.get(k, 0) + trauma_b.get(k, 0)) / 2.0
            for k in all_keys
        }
        mito = parent_a_bio.get("mito") or {}
        hash_a = str(mito.get("mother_hash", "EVE")) if isinstance(mito, dict) else str(
            getattr(mito, "mother_hash", "EVE"))
        mito_b = parent_b_data.get("mitochondria") or {}
        hash_b = str(mito_b.get("mother_hash", "EVE"))
        child_lineage = f"{hash_a[:4]}_{hash_b[:4]}"
        config_mutations = LiteraryReproduction.mutate_config(self.cfg)
        short_a = parent_a_id[-4:]
        short_b = parent_b_id[-4:]
        child_id = f"HYBRID_{short_a}x{short_b}"
        child_genome = {
            "source": "CROSSOVER",
            "parent_a": parent_a_id,
            "parent_b": parent_b_id,
            "trauma_inheritance": child_trauma,
            "config_mutations": config_mutations,
            "inherited_lineage": child_lineage,
            "lexicon_mutations": {},
        }
        return child_id, child_genome

    def attempt_reproduction(self, engine_ref, mode="MITOSIS", target_spore=None) -> Tuple[str, Dict]:
        """
        The public orchestrator for initiating the reproduction sequence.
        Extracts the necessary biological and semantic states from the live engine
        and routes them to the appropriate reproductive function.
        """
        mem = engine_ref.mind.mem
        mito_data = {}
        if getattr(engine_ref, "bio", None) and hasattr(engine_ref.bio, "mito"):
            mito_data = getattr(engine_ref.bio.mito.state, "__dict__", {})
        bio_state = {
            "trauma_vector": engine_ref.trauma_accum,
            "mito": mito_data,
        }
        cortex = getattr(engine_ref, "cortex", None)
        phys_packet = getattr(cortex, "last_physics", None) if cortex else None
        if not phys_packet:
            obs = getattr(engine_ref, "observer", None)
            phys_packet = getattr(obs, "last_physics_packet", {}) or {}
        genome = {}
        child_id = "UNKNOWN"
        if mode == "MITOSIS":
            child_id, genome = self.mitosis(mem.session_id, bio_state, phys_packet)
        elif mode == "CROSSOVER":
            if target_spore:
                res = self.crossover(mem.session_id, bio_state, target_spore)
                if res[0]:
                    child_id, genome = res
        return child_id, genome
