# BONEAMANITA 2.3 - "APOTHEOSIS"
# Refactor: SLASH | Status: OPTIMIZED
# "The Mandate is TRUTH. The Method is PIPELINE."

import time
import math
import random
import re
import json
import os
import string
from collections import Counter
from uuid import uuid4

# --- CONFIGURATION LAYER ---
class BoneConfig:
    """Dynamic Configuration Loader (Replaces Hardcoded Lexicon)"""
    DATA = {
        "physics": {"drag_weights": {"kinetic": 2.0, "stative": 0.5}, "thresholds": {"boredom": 11.0}},
        "lexicon": {
            "heavy_matter": [], "aerobic_matter": [], "kinetic_verbs": [],
            "play_verbs": [], "abstracts": [], "solvents": [],
            "sycophancy": [], "connectors": []
        },
        "toxins": {}
    }

    @classmethod
    def load(cls, filename="bone_config.json"):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    loaded = json.load(f)
                    # Merge logic could go here, straightforward overwrite for now
                    cls.DATA.update(loaded)
                    print(f"> [SYSTEM] Configuration loaded from {filename}")
            except Exception as e:
                print(f"> [SYSTEM] Config load failed: {e}. Using defaults.")

        # Hydrate Sets for O(1) Lookups
        cls.HEAVY = set(cls.DATA['lexicon'].get('heavy_matter', []))
        cls.AEROBIC = set(cls.DATA['lexicon'].get('aerobic_matter', []))
        cls.KINETIC = set(cls.DATA['lexicon'].get('kinetic_verbs', []))
        cls.PLAY = set(cls.DATA['lexicon'].get('play_verbs', []))
        cls.ABSTRACT = set(cls.DATA['lexicon'].get('abstracts', []))
        cls.SOLVENTS = set(cls.DATA['lexicon'].get('solvents', []))
        cls.SYCOPHANCY = set(cls.DATA['lexicon'].get('sycophancy', []))
        cls.CONNECTORS = set(cls.DATA['lexicon'].get('connectors', []))

        # Compile Toxin Regex
        all_toxins = []
        cls.TOXIN_WEIGHTS = {}
        for category, items in cls.DATA.get('toxins', {}).items():
            weight = 5.0 if category == 'corp_speak' else (3.0 if category == 'lazy_metaphor' else 8.0)
            if isinstance(items, dict): # Handle legacy dict format if present
                for phrase, w in items.items():
                    all_toxins.append(phrase)
                    cls.TOXIN_WEIGHTS[phrase] = w
            else: # Handle list format
                for phrase in items:
                    all_toxins.append(phrase)
                    cls.TOXIN_WEIGHTS[phrase] = weight

        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted(all_toxins, key=len, reverse=True)) + r')\b'
        cls.TOXIN_REGEX = re.compile(pattern_str, re.IGNORECASE) if all_toxins else None

class Prisma:
    RST, RED, GRN, YEL, BLU, MAG, CYN, WHT, GRY = "\033[0m", "\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m", "\033[97m", "\033[90m"
    @staticmethod
    def paint(text, color): return f"{color}{text}{Prisma.RST}"
    @staticmethod
    def wrap_val(val, threshold, invert=False):
        is_high = val > threshold
        color = Prisma.GRN if (is_high and invert) or (not is_high and not invert) else Prisma.RED
        return f"{color}{val}{Prisma.RST}"

# --- THE NEW PIPELINE (SINGLE PASS) ---

class BioHazardFilter:
    """Optimized Toxin Detection"""
    def __init__(self):
        self.mirror_patterns = [
            re.compile(r'(it|this|that)[\'’]?s?\s+(not|never)\s+(.*?)[,;]\s*(it|this|that)[\'’]?s?\s+', re.IGNORECASE),
            re.compile(r'\bnot\s+because\s+(.*?)\s+but\s+because\b', re.IGNORECASE)
        ]
        self.synthetic_markers = {'delve', 'underscore', 'landscape', 'tapestry', 'multifaceted', 'foster', 'nuance'}

    def scan_regex(self, raw_text):
        """Heavy Regex operations, separate from word loop"""
        results = {"score": 0.0, "types": set(), "msgs": [], "penalty": 0.0}

        # Mirror Trap
        for pattern in self.mirror_patterns:
            if pattern.search(raw_text):
                results["types"].add("LAZY_MIRRORING")
                results["penalty"] += 3.0
                results["msgs"].append("MIRROR TRAP: Define by assertion, not negation.")
                break

        # Config-loaded Toxins
        if BoneConfig.TOXIN_REGEX:
            for match in BoneConfig.TOXIN_REGEX.findall(raw_text):
                phrase = match.lower()
                weight = BoneConfig.TOXIN_WEIGHTS.get(phrase, 3.0)
                results["score"] += weight
                results["types"].add("CLICHÉ" if weight < 5.0 else "TOXIN")

        return results

class LinguisticPhysicsEngine:
    """The Heart: Single-Pass Analysis"""
    def __init__(self):
        self.biohazard = BioHazardFilter()
        self.suffixes = {'abstract': ('ness', 'ity', 'tion', 'ment', 'ism', 'ence', 'logy'),
                         'kinetic': ('ing',),
                         'adj': ('ful', 'ous', 'ive', 'ic', 'al', 'ish', 'ary', 'able')}
        self.stative_verbs = {'is', 'are', 'was', 'were', 'be', 'being', 'been', 'have', 'has', 'had', 'seem', 'feel'}
        self.prepositions = {'in', 'on', 'at', 'by', 'with', 'under', 'over', 'through', 'between', 'among', 'across'}

    def analyze(self, raw_text):
        # 1. Clean & Tokenize
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        clean_text = raw_text.lower().translate(translator)
        words = clean_text.split()
        total_words = len(words)

        if total_words == 0: return self._void_metrics()

        # 2. THE SINGLE PASS LOOP
        c = Counter()
        c['abstract_set'] = set()
        c['beige_score'] = 0.0

        for w in words:
            # Physics Buckets
            if w in BoneConfig.KINETIC or w in BoneConfig.PLAY or w.endswith(self.suffixes['kinetic']): c['kinetic'] += 1
            if w in BoneConfig.HEAVY: c['heavy'] += 1
            if w in BoneConfig.AEROBIC: c['aerobic'] += 1
            if w in BoneConfig.SOLVENTS: c['solvent'] += 1
            if w in BoneConfig.CONNECTORS: c['connector'] += 1
            if w in self.prepositions: c['spatial'] += 1
            if w in self.stative_verbs: c['stative'] += 1

            # Abstract/Entropy
            if w in BoneConfig.ABSTRACT or w.endswith(self.suffixes['abstract']):
                c['abstract'] += 1
                c['abstract_set'].add(w)

            # Stylistic / Toxin (Word-level)
            if w.endswith('ly') and w not in BoneConfig.SOLVENTS: c['adverb'] += 1
            if w.endswith(self.suffixes['adj']): c['adjective'] += 1
            if w in self.biohazard.synthetic_markers:
                c['beige_score'] += 2.0
                c['beige_hits'] = w # Just keep last for reporting
            if w in BoneConfig.SYCOPHANCY: c['hedging'] += 1

        # 3. Aggregation & Regex
        toxin_res = self.biohazard.scan_regex(raw_text)

        # Viscosity (Hydration) logic inline
        density = c['heavy'] / total_words
        hydration = c['solvent'] / total_words
        balance_ratio = hydration / (density if density > 0 else 1.0)
        hydro_penalty = 0.0
        hydro_status = "OPTIMAL"
        if (c['solvent'] / total_words) > 0.4: hydro_status, hydro_penalty = "FLOODED", 4.0
        elif density > 0.25 and balance_ratio < 0.2: hydro_status, hydro_penalty = "CONCRETE", 5.0

        # Beige Penalty
        if c['beige_score'] > 5.0:
            toxin_res['score'] += c['beige_score']
            toxin_res['types'].add("SILICA")
            toxin_res['msgs'].append(f"SYNTHETIC RESONANCE: Detected 'Beige' patterns.")

        # Drag Calculation
        garnish_load = c['adverb'] + (c['adjective'] * 0.8)
        butcher_penalty = 2.0 if (garnish_load / total_words) > 0.18 else 0.0

        action_score = (c['kinetic'] * 2.0) + (c['stative'] * 0.5) + 1.0
        base_drag = (total_words + (toxin_res['score'] * 10.0)) / action_score
        narrative_drag = base_drag + hydro_penalty + butcher_penalty + toxin_res['penalty']

        # Entropy & VSL
        abstract_repetition = c['abstract'] - len(c['abstract_set'])
        entropy_score = c['abstract'] + (abstract_repetition * 2) - c['aerobic'] - c['heavy'] # Net Entropy

        return {
            "physics": {
                "narrative_drag": round(narrative_drag, 2),
                "abstraction_entropy": entropy_score,
                "spatial_density": round(c['spatial'] / total_words, 2),
                "kinetic_ratio": round(c['kinetic'] / max(1, c['kinetic'] + c['stative']), 2),
                "connection_density": round(c['connector'] / total_words, 2),
                "toxicity_score": toxin_res['score'],
                "toxin_types": list(toxin_res['types']),
                "toxin_msgs": toxin_res['msgs'],
                "viscosity": {"status": hydro_status, "density": round(density, 2), "hydration": round(hydration, 2)},
                "counts": c
            },
            "clean_words": words,
            "raw_text": raw_text
        }

    def _void_metrics(self):
        return {"physics": {"narrative_drag": 0.0, "abstraction_entropy": 0, "spatial_density": 0.0, "viscosity": {"status": "VOID"}}, "clean_words": [], "raw_text": ""}


# --- APEIROGON LATTICE (Integrated) ---

class ApeirogonLattice:
    """Infinite Resolution + Integrated Zone Detection"""
    def __init__(self):
        # Maps 0.0 - 1.0 to (Adjective, Noun)
        self.VEL_MAP = [(0.2, "Static", "Anchor"), (0.4, "Drifting", "Observer"), (0.6, "Walking", "Construct"), (0.8, "Running", "Engine"), (1.0, "Ballistic", "Vector")]
        self.STR_MAP = [(0.2, "Fluid", "Mist"), (0.4, "Loose", "Web"), (0.6, "Framed", "Lattice"), (0.8, "Rigid", "Fortress"), (1.0, "Crystalline", "Monolith")]
        self.ENT_MAP = [(0.2, "Literal", "Stone"), (0.4, "Grounded", "Root"), (0.6, "Conceptual", "Idea"), (0.8, "Abstract", "Dream"), (1.0, "Chaos", "Void")]

    def _get_term(self, val, mapping):
        return min(mapping, key=lambda x: abs(x[0] - val))

    def resolve(self, sig):
        # 1. Detect Slurry (Zone Logic)
        # Replacing the old hardcoded logic with a lattice check
        is_slurry = (0.3 <= sig['VEL'] <= 0.6) and (0.4 <= sig['STR'] <= 0.8) and (sig['TEX'] < 0.2)

        # 2. Resolve Title
        dims = {k: v for k, v in sig.items() if k != 'BUOYANCY'}
        sorted_dims = sorted(dims.items(), key=lambda item: item[1], reverse=True)
        primary, secondary = sorted_dims[0], sorted_dims[1]

        map_lookup = {'VEL': self.VEL_MAP, 'STR': self.STR_MAP, 'ENT': self.ENT_MAP, 'TEX': self.VEL_MAP, 'TMP': self.VEL_MAP} # Fallbacks for TEX/TMP for brevity

        p_term = self._get_term(primary[1], map_lookup.get(primary[0], self.VEL_MAP))
        s_term = self._get_term(secondary[1], map_lookup.get(secondary[0], self.ENT_MAP))

        title = f"THE {s_term[1].upper()} {p_term[2].upper()}"

        return {
            "archetype": title,
            "slurry": is_slurry,
            "description": f"Vector: {primary[0]}({primary[1]}) / {secondary[0]}({secondary[1]})"
        }

class SignatureEngine:
    def __init__(self):
        self.lattice = ApeirogonLattice()

    def identify(self, metrics):
        phys = metrics['physics']
        words = metrics['clean_words']
        c = phys.get('counts', Counter())
        total = len(words) or 1

        # 1. Calculate Raw Dimensions
        vel = phys['kinetic_ratio']
        # Continuous Spatial Drag (The Patch)
        spatial_impact = min(1.0, phys['spatial_density'] / 0.20)
        struct = max(0.0, min(1.0, (1.0 - (phys['narrative_drag'] / 10.0)) + (spatial_impact * 0.2)))

        ent_raw = phys['abstraction_entropy']
        ent = max(0.0, min(1.0, (ent_raw + 2) / 8.0))

        tex = min(1.0, (c['heavy'] + c['aerobic']) / total * 3.0)

        sig = {"VEL": round(vel, 2), "STR": round(struct, 2), "ENT": round(ent, 2), "TEX": round(tex, 2), "BUOYANCY": 0.0}

        # 2. Resolve via Lattice
        identity = self.lattice.resolve(sig)
        return {"signature": sig, **identity}

# --- SYSTEM CORE ---

class BonepokeCore:
    def __init__(self):
        BoneConfig.load() # Bootloader
        self.physics = LinguisticPhysicsEngine()
        self.signature = SignatureEngine()
        self.metabolism = 33
        print(f"{Prisma.GRN} [SLASH 2.3 KERNEL INITIALIZED]{Prisma.RST}")

    def process(self, text):
        # 1. Analyze
        metrics = self.physics.analyze(text)
        phys = metrics['physics']

        # 2. Identify
        arch = self.signature.identify(metrics)

        # 3. Report
        self.render_hud(metrics, arch)
        return metrics, arch

    def render_hud(self, m, a):
        phys = m['physics']
        drag_c = Prisma.wrap_val(phys['narrative_drag'], 2.0)
        print(f"\n{Prisma.GRY}--------------------------------------------------{Prisma.RST}")
        print(f"{Prisma.WHT}[BONEAMANITA v2.3]{Prisma.RST} ATP: {self.metabolism} | DRAG: {drag_c} | VISC: {phys['viscosity']['status']}")
        print(f"{Prisma.CYN}ARCH:{Prisma.RST} {Prisma.WHT}{a['archetype']}{Prisma.RST} {a['description']}")
        if a['slurry']: print(f"{Prisma.MAG}>>> WARNING: SLURRY DETECTED (Beige Zone){Prisma.RST}")
        print(f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}\n")

if __name__ == "__main__":
    engine = BonepokeCore()
    while True:
        u = input(f"> ")
        if u.lower() in ['exit', 'quit']: break
        engine.process(u)
