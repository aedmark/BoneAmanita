"""spores/biome.py
This module defines the biological/ecological subsystems of the language engine.
It treats language processing not as a static algorithm, but as an active ecosystem
where words have physical properties (mass, toxicity) and semantic interactions
trigger organic responses (immunity, infection, photosynthesis).
Classes:
    - ImmuneMycelium: Acts as a phonetic filter, calculating the "weight" and "toxicity" of words.
    - BioParasite: Injects intrusive or metaphorical connections into the semantic graph during high exhaustion.
    - BioLichen: Converts "light" concepts into metabolic energy (sugar/ATP) when the system is resting.
"""
import random
from typing import Tuple
from struts import ux, ux_format, safe_get
from presets import BoneConfig
from constants import Prisma


class ImmuneMycelium:
    """
    The defensive substrate of the linguistic engine.
    It scans incoming text for structural integrity and phonetic toxicity,
    preventing the system from bogging down in overly dense or "heavy" language.
    """
    PHONETICS = {
        "PLOSIVE": set("bdgkpt"),
        "FRICATIVE": set("fthszsh"),
        "LIQUID": set("lr"),
        "NASAL": set("mn"),
    }
    ROOTS = {
        "HEAVY": ("lith", "ferr", "petr", "dens", "grav", "struct", "base", "fund", "mound",),
        "KINETIC": ("mot", "mov", "ject", "tract", "pel", "crat", "dynam", "flux"),
    }

    def __init__(self):
        self.active_antibodies = set()
        self.name = "MYCELIUM"
        self.color = Prisma.CYN
        self.archetypes = {"constructive", "kinetic", "abstract", "code", "system"}
        self._flat_roots = tuple(r for roots in self.ROOTS.values() for r in roots)

    def opine(self, clean_words: list, _voltage: float) -> Tuple[float, str]:
        """
        Calculates how aligned the current text stream is with the Mycelium's core archetypes.
        Returns a score (0 to 10) and an optional UX commentary string.
        """
        hits = sum(1 for w in clean_words if w in self.archetypes)
        score = (hits / max(1, len(clean_words))) * 10.0
        comment = ux("spore_strings", "immune_op_scan")
        if score > 2.0:
            comment = ux("spore_strings", "immune_op_good")
        return score, comment

    def assay(self, word, _context, _rep_val, _phys, _pulse):
        """
        Performs a phonetic assay on a single word to determine its "density".
        If a word has too many hard consonants packed into a short space, it is flagged as toxic.
        """
        w = word.lower()
        clean_len = len(w)
        if clean_len < 3:
            return None, ""
        for r in self._flat_roots:
            if r in w and (w.startswith(r) or w.endswith(r) or (len(r) / clean_len > 0.5)):
                return None, ""
        plosive_mass = sum(1 for c in w if c in self.PHONETICS["PLOSIVE"]) * 1.2
        nasal_mass = sum(1 for c in w if c in self.PHONETICS["NASAL"]) * 0.8
        length_multiplier = 1.2 if clean_len <= 4 else 1.0
        density = ((plosive_mass + nasal_mass) / clean_len) * length_multiplier
        if density > 1.0:
            msg = ux("spore_strings", "immune_tox_phon")
            return "TOXIN_HEAVY", (msg.format(word=w) if msg else "")
        return None, ""


class BioParasite:
    """
    Represents systemic exhaustion, entropy, and lateral/intrusive thinking.
    When the system is tired (low stamina) and abstracted (high psi), the parasite
    forces unnatural connections between grounded ("heavy") and conceptual ("abstract") nodes.
    """

    def __init__(self, memory_ref, lexicon_ref, config_ref=None):
        self.mem = memory_ref
        self.lex = lexicon_ref
        self.cfg = config_ref or BoneConfig
        self.spores_deployed = 0
        cfg = safe_get(self.cfg, "SPORES", {})
        self.MAX_SPORES = int(safe_get(cfg, "PARASITE_MAX_SPORES", 8))
        self.name = "PARASITE"
        self.color = Prisma.RED
        self.archetypes = {"antigen", "toxin", "heavy", "meat", "void", "static", "rot", "decay", }

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        """
        The Parasite thrives on high voltage (chaos) and necrotic archetypes.
        Generates feedback based on how well the input matches its destructive/liminal nature.
        """
        score = (sum(1 for w in clean_words if w in self.archetypes) /
                 max(1, len(clean_words))) * 10.0
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
        """
        Attempts to inject an intrusive or metaphorical connection into the semantic graph.
        This only occurs under specific metabolic conditions (low stamina, high abstraction).
        """
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
            (h, p) for h in heavy_candidates for p in abstract_candidates
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
            msg = ux_format("spore_strings", "para_syn_spark", "A parasitic metaphor bloomed.", host=host.upper(),
                            para=parasite.upper())
            return True, f"{Prisma.CYN}{msg}{Prisma.RST}"
        msg = ux_format("spore_strings", "para_intrusive", "An intrusive thought took root.", host=host.upper(),
                        para=parasite.upper())
        return True, f"{Prisma.VIOLET}{msg}{Prisma.RST}"


class BioLichen:
    """
    The metabolic engine for system recovery.
    It operates during low-friction states to "photosynthesize" positive,
    generative words into usable systemic stamina (sugar).
    """

    def __init__(self, lexicon_ref=None):
        self.lex = lexicon_ref
        self.name = "LICHEN"
        self.color = Prisma.GRN
        self.archetypes = {"photo", "play", "sacred", "social", "solar", "vital", "bloom", "grow", }

    def opine(self, clean_words: list, voltage: float) -> Tuple[float, str]:
        """
        Feedback mechanism favoring playful, generative, or restful semantic states.
        """
        score = (sum(1 for w in clean_words if w in self.archetypes) /
                 max(1, len(clean_words))) * 10.0
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
        """
        Converts detected 'photo' (light/generative) words into metabolic sugar.
        It also possesses the ability to biologically transmute 'heavy' words into 'photo' words
        over time, gradually healing the semantic space.
        """
        msgs = []
        counts = safe_get(phys, "counts", {})
        drag = float(safe_get(phys, "narrative_drag", 0.0))
        light = counts.get("photo", 0)
        sugar = 0.0
        light_words = [w for w in clean_words if w in self.archetypes]
        if light > 0 and drag < 3.0:
            sugar = float(light * 2)
            source_str = f" via '{random.choice(light_words)}'" if light_words else ""
            if msg := ux_format("spore_strings", "lichen_photo", source=source_str, sugar=sugar):
                msgs.append(f"{Prisma.GRN}{msg}{Prisma.RST}")
        if sugar > 0 and self.lex:
            heavy_lexicon = self.lex.get("heavy") or set()
            heavy_words = [w for w in clean_words if w in heavy_lexicon]
            if heavy_words:
                chosen_heavy_word = random.choice(heavy_words)
                self.lex.teach(chosen_heavy_word, "photo", tick_count)
                formatted_msg = ux_format("spore_strings", "lichen_sub", word=chosen_heavy_word)
                if formatted_msg:
                    msgs.append(f"{Prisma.MAG}{formatted_msg}{Prisma.RST}")
        return sugar, " ".join(msgs) if msgs else None
