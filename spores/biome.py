"""spores/biome.py"""

import random
from typing import Tuple

from constants import Prisma
from presets import BoneConfig
from struts import safe_get, ux, ux_format


class BioParasite:
    def __init__(self, memory_ref, lexicon_ref, config_ref=None):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        self.spores_deployed = 0
        cfg = safe_get(self.cfg, "SPORES", {})
        self.MAX_SPORES = int(safe_get(cfg, "PARASITE_MAX_SPORES", 8))
        self.name = "PARASITE"
        self.color = Prisma.RED
        self.archetypes = {
            "antigen",
            "toxin",
            "heavy",
            "meat",
            "void",
            "static",
            "rot",
            "decay",
        }

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        score = (
            sum(1 for w in clean_words if w in self.archetypes)
            / max(1, len(clean_words))
        ) * 10.0
        if score > 3.0:
            comment = ux("spore_strings", "para_op_great")
        elif score > 1.0:
            comment = ux("spore_strings", "para_op_good")
        elif voltage > 15.0:
            comment = ux("spore_strings", "para_op_hot")
        elif voltage < 5.0:
            comment = ux("spore_strings", "para_op_cold")
        else:
            comment = ""
        return score, comment

    def infect(self, physics_packet, stamina):
        psi = safe_get(physics_packet, "psi", 0.0)
        cfg = safe_get(self.cfg, "SPORES", {})
        p_stam = float(safe_get(cfg, "PARASITE_STAMINA_MAX", 40.0))
        p_psi = float(safe_get(cfg, "PARASITE_PSI_MIN", 0.6))
        p_decay = float(safe_get(cfg, "PARASITE_DECAY_CHANCE", 0.2))
        if stamina > p_stam and psi < p_psi:
            return False, None
        if self.spores_deployed >= self.MAX_SPORES:
            if random.random() < p_decay:
                self.spores_deployed = max(0, self.spores_deployed - 1)
            return False, None
        if not self.lex or not hasattr(self.lex, "get"):
            return False, None
        graph = self.mem.graph
        heavy_set = set(self.lex.get("heavy") or [])
        abstract_set = set(self.lex.get("abstract") or [])
        if not heavy_set or not abstract_set:
            return False, None
        graph_keys = graph.keys()
        heavy_candidates = list(heavy_set & graph_keys)
        abstract_candidates = list(abstract_set & graph_keys)
        if not heavy_candidates or not abstract_candidates:
            return False, None
        valid_pairs = [
            (h, p)
            for h in heavy_candidates
            for p in abstract_candidates
            if p not in graph[h].get("edges", {}) and h != p
        ]
        if not valid_pairs:
            return False, None
        host, parasite = random.choice(valid_pairs)
        m_psi = float(safe_get(cfg, "PARASITE_METAPHOR_PSI", 0.7))
        p_wt = float(safe_get(cfg, "PARASITE_WEIGHT", 8.88))
        is_metaphor = psi > m_psi
        weight = p_wt
        host_edges = graph[host].setdefault("edges", {})
        host_edges[parasite] = weight
        para_edges = graph[parasite].setdefault("edges", {})
        para_edges[host] = weight
        self.spores_deployed += 1
        if is_metaphor:
            msg = ux_format(
                "spore_strings",
                "para_syn_spark",
                "A parasitic metaphor bloomed.",
                host=host.upper(),
                para=parasite.upper(),
            )
            return True, f"{Prisma.CYN}{msg}{Prisma.RST}"
        msg = ux_format(
            "spore_strings",
            "para_intrusive",
            "An intrusive thought took root.",
            host=host.upper(),
            para=parasite.upper(),
        )
        return True, f"{Prisma.VIOLET}{msg}{Prisma.RST}"


class BioCordyceps:
    def __init__(self, config_ref=None):
        self.cfg = config_ref
        self.name = "CORDYCEPS"
        self.color = Prisma.OCHRE
        self.incubation_level = 0.0
        self.is_blooming = False
        self.trauma_words = ["burn", "fail", "static", "rot", "abyss", "error", "decay", "fracture", "ruin"]

    def incubate(self, trauma_sum: float) -> str:
        if trauma_sum > 15.0:
            self.incubation_level += (trauma_sum * 0.1)
        else:
            self.incubation_level = max(0.0, self.incubation_level - 0.5)
        if self.incubation_level > 20.0 and not self.is_blooming:
            self.is_blooming = True
            if self.cfg and hasattr(self.cfg, "BIO"):
                if isinstance(self.cfg.BIO, dict):
                    self.cfg.BIO["CORDYCEPS_BLOOMING"] = True
                else:
                    setattr(self.cfg.BIO, "CORDYCEPS_BLOOMING", True)
            return f"{self.color}[CORDYCEPS BLOOM]: Agency compromised. The fungus has seized the input manifold.{Prisma.RST}"
        return None


class BioLichen:
    def __init__(self, lexicon_ref=None, config_ref=None):
        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        self.name = "LICHEN"
        self.color = Prisma.GRN
        self.archetypes = {
            "photo",
            "play",
            "sacred",
            "social",
            "solar",
            "vital",
            "bloom",
            "grow",
        }

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        score = (
            sum(1 for w in clean_words if w in self.archetypes)
            / max(1, len(clean_words))
        ) * 10.0
        if score > 3.0:
            comment = ux("spore_strings", "lichen_op_great")
        elif score > 1.0:
            comment = ux("spore_strings", "lichen_op_good")
        elif voltage > 18.0:
            comment = ux("spore_strings", "lichen_op_hot")
        elif voltage < 2.0:
            comment = ux("spore_strings", "lichen_op_cold")
        else:
            comment = ""
        return score, comment

    def photosynthesize(self, phys, clean_words, tick_count):
        msgs = []
        counts = safe_get(phys, "counts", {})
        drag = float(safe_get(phys, "narrative_drag", 0.0))
        light = counts.get("photo", 0)
        sugar = 0.0
        light_words = [w for w in clean_words if w in self.archetypes]
        if light > 0:
            if drag >= 9.0 and light >= 2:
                sugar = float(light * 10)
                msgs.append(f"{Prisma.MAG}[ANTIDOTE SYNTHESIZED]: The Lichen thrives under immense crushing drag. Cordyceps starved.{Prisma.RST}")
                cfg_bio = safe_get(self.cfg, "BIO", {})
                if isinstance(cfg_bio, dict):
                    cfg_bio["CORDYCEPS_BLOOMING"] = False
                else:
                    setattr(cfg_bio, "CORDYCEPS_BLOOMING", False)
            elif drag < 3.0:
                sugar = float(light * 2)
                source_str = (
                    f" via '{random.choice(light_words)}'" if light_words else ""
                )
                if msg := ux_format(
                    "spore_strings", "lichen_photo", source=source_str, sugar=sugar
                ):
                    msgs.append(f"{Prisma.GRN}{msg}{Prisma.RST}")
        if sugar > 0 and self.lex:
            heavy_lexicon = self.lex.get("heavy") or set()
            heavy_words = [w for w in clean_words if w in heavy_lexicon]
            if heavy_words:
                chosen_heavy_word = random.choice(heavy_words)
                self.lex.teach(chosen_heavy_word, "photo", tick_count)
                formatted_msg = ux_format(
                    "spore_strings", "lichen_sub", word=chosen_heavy_word
                )
                if formatted_msg:
                    msgs.append(f"{Prisma.MAG}{formatted_msg}{Prisma.RST}")
        return sugar, " ".join(msgs) if msgs else None
