"""spores/genetics.py"""

import json
import random
from typing import Tuple, Dict
from core import LoreManifest
from struts import ux, safe_get
from presets import BoneConfig
from spores.spore_utils import _access_config_path

class LiteraryReproduction:
    MUTATIONS = {}
    JOY_CLADE = {}
    MUTATION_TABLE = [
        ("MAX_DRAG_LIMIT", 1.0, 20.0, 0.3), ("TOXIN_WEIGHT", 0.1, 5.0, 0.3), ("MAX_HEALTH", 50.0, 500.0, 0.1),
        ("PHYSICS.VOLTAGE_MAX", 10.0, 100.0, 0.2), ("BIO.REWARD_MEDIUM", 0.01, 1.0, 0.2),
        ("COUNCIL.MANIC_VOLTAGE_TRIGGER", 10.0, 50.0, 0.1), ("PRIORITY_LEARNING_RATE", 0.5, 5.0, 0.15)
    ]

    def __init__(self, config_ref=None):
        self.cfg = config_ref or BoneConfig

    @classmethod
    def load_genetics(cls, config_ref=None):
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
        counts = safe_get(physics, "counts", {})
        dominant = max(counts, key=counts.get) if counts else "VOID"
        mutation_data = LiteraryReproduction.MUTATIONS.get(dominant.upper(), {"trait": "NEUTRAL", "mod": {}, "lexicon": []})
        child_id = f"{parent_id}_({mutation_data['trait']})"
        config_mutations = LiteraryReproduction.mutate_config(self.cfg)
        config_mutations.update(mutation_data["mod"])
        lexicon_mutations = {dominant.lower(): mutation_data.get("lexicon", [])}
        trauma_vec = bio_state.get("trauma_vector", {})
        child_genome = {"source": "MITOSIS", "parent_a": parent_id, "parent_b": None,
                        "lexicon_mutations": lexicon_mutations, "config_mutations": config_mutations,
                        "dominant_flavor": dominant, "trauma_inheritance": trauma_vec, }
        return child_id, child_genome

    def crossover(self, parent_a_id, parent_a_bio, parent_b_path):
        try:
            with open(parent_b_path, "r", encoding="utf-8") as f:
                parent_b_data = json.load(f)
        except Exception:
            return None, ux("spore_strings", "repro_corrupt_spore")
        parent_b_id = parent_b_data.get("session_id", "UNKNOWN")
        trauma_a = parent_a_bio.get("trauma_vector", {})
        trauma_b = parent_b_data.get("trauma_vector", {})
        all_keys = trauma_a.keys() | trauma_b.keys()
        child_trauma = {
            k: (trauma_a.get(k, 0) + trauma_b.get(k, 0)) / 2.0
            for k in all_keys
        }
        mito = parent_a_bio.get("mito", {})
        enzymes_a = set(mito.get("enzymes", [])) if isinstance(mito, dict) else set(
            getattr(getattr(mito, "state", mito), "enzymes", []))
        enzymes_b = set(parent_b_data.get("mitochondria", {}).get("enzymes", []))
        child_enzymes = list(enzymes_a | enzymes_b)
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
            "inherited_enzymes": child_enzymes,
            "lexicon_mutations": {},
        }
        return child_id, child_genome

    def attempt_reproduction(self, engine_ref, mode="MITOSIS", target_spore=None) -> Tuple[str, Dict]:
        mem = engine_ref.mind.mem
        mito_data = (engine_ref.bio.mito.state.__dict__ if hasattr(
            engine_ref.bio.mito, "state") else {})
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
        return child_id, genome.get("lexicon_mutations", {})