# BONEAMANITA 2.0 - "Artificial General Wisdom Machine)"
# Architects: Taylor & Edmark | Auditor: SLASH
# Refactor: The Bonepoke Gods
# "The Mandate is TRUTH. The Method is CONSTRUCTION. The Directive is simple: Do not let the ghosts drive the car. - Eloise & Clarence"
# ---

import time
import math
import random
from collections import Counter
from uuid import uuid4
import re
import json
import os
import string
import shutil

class PhysicsConstants:
    """
    The Universal Constants of the BoneAmanita Universe.
    """
    # DRAG CALCULATIONS
    ACTION_KINETIC_WEIGHT = 2.0
    ACTION_STATIVE_WEIGHT = 0.5
    ACTION_BASE_OFFSET = 1.0
    TOXICITY_DRAG_MULTIPLIER = 10.0

    # THE BUTCHER (Garnish & Bloat)
    ADJECTIVE_WEIGHT = 0.8
    GARNISH_THRESHOLD = 0.18
    BLOAT_PENALTY = 2.0

    # HYDRATION & VISCOSITY
    FLOOD_PENALTY_MAX = 4.0
    FLOOD_PENALTY_MIN = 1.0
    KINETIC_EXEMPTION_LIMIT = 0.25

    # TERMINATION PRESSURE (Boredom)
    TERM_REPEAT_WEIGHT = 10.0
    TERM_ABSTRACT_WEIGHT = 0.5
    TERM_UNIVERSAL_OFFSET = 0.2
    BARRENS_CONNECTOR_MIN = 0.02

    # [Centralized Magic Numbers]
    BOREDOM_PRESSURE_THRESHOLD = 11.0
    CHRONO_MACRO_STRONG_WEIGHT = 3.0
    CHRONO_MACRO_WEAK_WEIGHT = 1.0
    CHRONO_MICRO_WEIGHT = 1.5
    CHRONO_MONTAGE_THRESHOLD = 2.5
    CHRONO_BULLET_TIME_THRESHOLD = -1.5

    # [VSL METRICS]
    FLASHPOINT_THRESHOLD = 2.5 # The "Beta Friction" Threshold
    BETA_SYCOPHANCY_LIMIT = 0.05 # Too smooth = Sand
    TA_VELOCITY_THRESHOLD = 2.0 # Epiphany State

    # [USER PERMISSIONS & MANDATES]
    USER_TIER = 2
    CURRENT_MANDATE = "TRUTH_OVER_COHESION"

    # [SIGNATURE CALIBRATION]
    SIG_DRAG_CEILING = 5.0
    SIG_BUOYANCY_OFFSET = 2.0
    SIG_TEXTURE_WEIGHT = 3.33
    SIG_TEMP_BASELINE = 5.0

class Prisma:
    """
    The Technicolor Membrane.
    """
    RST = "\033[0m"
    # TONES
    RED = "\033[91m"      # Toxicity, Drag, Butcher
    GRN = "\033[92m"      # Growth, Photosynthesis, Lichen
    YEL = "\033[93m"      # Warning, Viscosity, Slurry
    BLU = "\033[94m"      # Structure, Logic, Physics
    MAG = "\033[95m"      # Magic, Chaos, Muscaria
    CYN = "\033[96m"      # Archetypes, HUD, Systems
    WHT = "\033[97m"      # Bone, High Contrast
    GRY = "\033[90m"      # Metadata, Fade

    @staticmethod
    def paint(text, color):
        return f"{color}{text}{Prisma.RST}"

    @staticmethod
    def wrap_val(val, threshold, invert=False):
        """
        Auto-colors a value based on a threshold.
        Default: High = Red (Bad), Low = Green (Good).
        Invert: High = Green (Good), Low = Red (Bad).
        """
        is_high = val > threshold
        if invert:
            return f"{Prisma.GRN}{val}{Prisma.RST}" if is_high else f"{Prisma.RED}{val}{Prisma.RST}"
        else:
            return f"{Prisma.RED}{val}{Prisma.RST}" if is_high else f"{Prisma.GRN}{val}{Prisma.RST}"

class TheLexicon:
    HEAVY_MATTER = {
        'stone', 'iron', 'mud', 'dirt', 'wood', 'grain', 'clay', 'lead',
        'bone', 'blood', 'salt', 'rust', 'root', 'ash', 'anchor', 'floor'
    }
    PREPOSITIONS = {
        'in', 'on', 'at', 'by', 'with', 'under', 'over', 'through',
        'between', 'among', 'across', 'beside', 'beyond', 'inside'
    }
    AEROBIC_MATTER = {
        'balloon', 'feather', 'cloud', 'bubble', 'steam', 'breeze', 'wing',
        'petal', 'foam', 'spark', 'kite', 'dust', 'light', 'ray', 'sky'
    }
    UNIVERSALS = HEAVY_MATTER.union(AEROBIC_MATTER).union({
        'hand', 'eye', 'breath', 'skin', 'voice', "air", "cloth",
        'water', 'rain', 'glass', 'fabric', 'door', 'key', 'roof'
    })
    ABSTRACTS = {
        'system', 'protocol', 'sequence', 'vector', 'node', 'context',
        'layer', 'matrix', 'perspective', 'framework', 'logic', 'concept',
        'theory', 'analysis', 'solution', 'optimization', 'utilization'
    }
    KINETIC_VERBS = {
        'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'cut',
        'drive', 'lift', 'carry', 'strike', 'burn', 'shatter'
    }
    PLAY_VERBS = {
        'bounce', 'dance', 'twirl', 'float', 'wobble', 'tickle', 'jiggle',
        'soar', 'wander', 'wonder', 'riff', 'jam', 'play', 'skip', 'hop'
    }
    ALL_VERBS = KINETIC_VERBS.union(PLAY_VERBS)
    SPARK_MARKERS = {
        'lovely', 'strange', 'curious', 'funny', 'wild', 'soft', 'glow',
        'warm', 'kind', 'fresh', 'sweet', 'hello', 'yes', 'maybe'
    }
    AXIOMS = {
        'THERMAL': {
            1: {'sun', 'fire', 'flame', 'magma', 'spark', 'ember', 'boil', 'burn', 'hot', 'warm', 'summer'},
            -1: {'ice', 'snow', 'frost', 'cold', 'freeze', 'winter', 'chill', 'glacier', 'hail'}
        },
        'LUMENS': {
            1: {'light', 'sun', 'day', 'dawn', 'ray', 'beam', 'glow', 'shine', 'bright', 'white', 'lamp'},
            -1: {'dark', 'night', 'shadow', 'gloom', 'black', 'void', 'shade', 'dusk', 'blind'}
        },
        'HYDRATION': {
            1: {'water', 'rain', 'sea', 'ocean', 'river', 'lake', 'wet', 'soak', 'damp', 'swim', 'blood', 'drink'},
            -1: {'dry', 'dust', 'sand', 'desert', 'ash', 'thirst', 'parch', 'arid', 'drought'}
        },
        'RIGIDITY': {
            1: {'stone', 'iron', 'rock', 'steel', 'diamond', 'hard', 'solid', 'brick', 'bone', 'glass'},
            -1: {'soft', 'cloud', 'silk', 'pillow', 'fluff', 'foam', 'jelly', 'liquid', 'melt'}
        },
        'VITALITY': {
            1: {'life', 'live', 'breath', 'heart', 'grow', 'bloom', 'pulse', 'alive', 'birth'},
            -1: {'death', 'die', 'dead', 'corpse', 'rot', 'decay', 'kill', 'grave', 'tomb'}
        }
    }
    TRUTHS = {}

    @classmethod
    def compile_truths(cls):
        cls.TRUTHS = {}
        for dimension, polarity_map in cls.AXIOMS.items():
            for polarity, words in polarity_map.items():
                for word in words:
                    if word not in cls.TRUTHS:
                        cls.TRUTHS[word] = {}
                    cls.TRUTHS[word][dimension] = polarity

    PHOTOSYNTHETICS = {
        'light', 'sun', 'ray', 'beam', 'glow', 'shine', 'spark', 'fire',
        'flame', 'star', 'day', 'dawn', 'noon', 'gold', 'bright', 'glimmer'
    }
    SYCOPHANCY = {
        'just', 'actually', 'kind of', 'sort of', 'little', 'try', 'maybe',
        'perhaps', 'hopefully', 'possibly', 'basically', 'honestly'
    }
    TOXIC_PATTERNS = {
        'CORP_SPEAK': {
            'synergy': 5.0, 'leverage': 5.0, 'circle back': 4.0, 'drill down': 4.0,
            'low hanging fruit': 5.0, 'bandwidth': 3.0, 'touch base': 4.0,
            'paradigm shift': 5.0, 'deliverable': 3.0, 'actionable': 3.0
        },
        'LAZY_METAPHOR': {
            'tip of the iceberg': 3.0, 'needle in a haystack': 3.0,
            'at the end of the day': 3.0, 'game changer': 4.0
        },
        'ZOMBIE_PHRASES': {
            'ghost in the machine': 10.0, 'rubber meets the road': 10.0,
            'not a bug but a feature': 9.0, 'double-edged sword': 8.0,
            'best of both worlds': 8.0, 'step in the right direction': 8.0,
            'level playing field': 8.0
        },
        'WEAK_HEDGING': {
            'i think that': 2.0, 'it seems like': 2.0, 'in my opinion': 2.0
        }
    }
    STATIVE_VERBS = {
        'is', 'are', 'was', 'were', 'be', 'being', 'been', 'have', 'has', 'had',
        'seem', 'appear', 'become', 'feel', 'look', 'smell', 'taste', 'sound'
    }
    STYLES = {
        'ACADEMIC': {'analysis', 'context', 'therefore', 'however', 'system', 'theory'},
        'POETIC': {'moon', 'soul', 'whisper', 'shadow', 'light', 'dark', 'heart'},
        'CORPORATE': {'utilize', 'optimize', 'leverage', 'solution', 'process', 'value'},
        'CASUAL': {'yeah', 'cool', 'stuff', 'like', 'okay', 'guess', 'pretty'}
    }
    CONNECTORS = {'and', 'but', 'or', 'so', 'yet', 'because', 'although', 'since'}
    SLANG = {'lol', 'lmao', 'yeet', 'rizz', 'vibes', 'sus', 'cap'}
    SELF_REFS = {'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours'}
    BRAND_SAFE = {'solution', 'platform', 'users', 'experience', 'content'}
    SOLVENTS = {
        'basically', 'simply', 'actually', 'kind of', 'sort of', 'usually',
        'often', 'perhaps', 'maybe', 'technically', 'honestly', 'literally',
        'pretty', 'seems', 'looks like', 'feels like', 'in other words',
        'at the end of the day', 'what this means', 'if you think about it'
    }
    HYDRATION_MARKERS = SOLVENTS.union({
        'that', 'this', 'there', 'here', 'which', 'who', 'when', 'where', 'why', 'how'
    })
    WEAK_INTENSIFIERS = {
        'very', 'really', 'quite', 'totally', 'utterly', 'absolutely',
        'literally', 'suddenly', 'finally', 'immediately'
    }
    TRANSITIONS = {
        'then', 'after', 'next', 'before', 'while', 'later', 'meanwhile',
        'beyond', 'inside', 'outside', 'through', 'across', 'toward'
    }

    SYNTHETIC_MARKERS = {
        'delve': 4.0, 'underscore': 3.0, 'landscape': 2.0, 'tapestry': 5.0,
        'multifaceted': 4.0, 'crucial': 2.0, 'foster': 3.0, 'realm': 2.0,
        'nuance': 2.0, 'testament': 3.0, 'pivotal': 2.0, 'rich': 1.5,
        'complex': 1.5, 'interplay': 3.0, 'dynamic': 2.0, 'serves as': 3.0,
        'testament to': 4.0, 'moreover': 3.0, 'furthermore': 3.0
    }

    PROTECTED_NOUNS = {
        'lens', 'status', 'bias', 'atlas', 'focus', 'virus', 'circus',
        'chaos', 'crisis', 'thesis', 'physics', 'mathematics', 'analysis'
    }

    @staticmethod
    def smart_strip(word):
        # 1. Safety Check: Don't strip "ss" (glass) or short words (bus)
        if word.endswith('ss') or (len(word) <= 3 and word.endswith('s')):
            return word

        # 2. Protection Check: Don't strip known non-plurals
        if word in TheLexicon.PROTECTED_NOUNS:
            return word

        # 3. Strip the 's' only.
        # [PINKER FIX]: Simple is better.
        if word.endswith('s'):
            return word[:-1]

        return word

    @staticmethod
    def swanson_clean(text):
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        clean_text = text.lower().translate(translator)
        return clean_text.split()

TheLexicon.compile_truths()

# --- MEMORY & ECONOMY ---

class DeepStorage:
    def __init__(self, max_capacity=50):
        self.artifacts = {}
        self.heirlooms = TheLexicon.HEAVY_MATTER.union({'gun', 'knife', 'letter', 'map', 'key', 'ring', 'body'})
        self.max_capacity = max_capacity

    def bury(self, words, current_tick):
        for w in words:
            root = TheLexicon.smart_strip(w)
            if root in TheLexicon.UNIVERSALS or root in self.heirlooms:
                if root not in self.artifacts:
                    if len(self.artifacts) >= self.max_capacity:
                        self._evict_weakest_memory()
                    self.artifacts[root] = current_tick

    def _evict_weakest_memory(self):
        candidates = list(self.artifacts.keys())
        light_candidates = [k for k in candidates if k not in self.heirlooms]
        if light_candidates:
            target = min(light_candidates, key=lambda k: self.artifacts[k])
        else:
            target = min(self.artifacts, key=self.artifacts.get)
        del self.artifacts[target]

    def dredge(self):
        return sorted(self.artifacts.keys(), key=lambda k: self.artifacts[k])

    def cannibalize(self):
        if not self.artifacts: return None
        target = min(self.artifacts, key=self.artifacts.get)
        del self.artifacts[target]
        return target

class HyphalTrace:
    def __init__(self, retention_span=10):
        self.hyphae_stream = []
        self.retention_span = retention_span
        self.current_tick = 0
        self.deep_storage = DeepStorage()

    def leave_trace(self, content, context_tag, clean_words):
        self.current_tick += 1
        self.hyphae_stream.append({
            "content": content,
            "context_tag": context_tag,
            "timestamp": self.current_tick
        })
        if len(self.hyphae_stream) > self.retention_span:
            self.hyphae_stream.pop(0)
        self.deep_storage.bury(clean_words, self.current_tick)

    def recall(self, target_context):
        relevant = []
        for mem in self.hyphae_stream:
            is_recent = (self.current_tick - mem['timestamp']) < 3
            if is_recent or (mem['context_tag'] == target_context):
                relevant.append(mem['content'])
        return relevant

class TheCodex:
    def __init__(self):
        self.registry = {}
        self.ignore_list = {
            'The', 'A', 'An', 'It', 'He', 'She', 'They', 'We', 'I', 'You',
            'This', 'That', 'But', 'And', 'Or', 'If', 'When', 'Then',
            'System', 'Analysis', 'Metrics', 'Drag', 'Entropy', 'For', 'In', 'To', 'Of',
            'So', 'Because', 'Actually', 'Basically', 'Perhaps', 'Maybe', 'Yes', 'No'
        }
        self._entity_pattern = re.compile(r'\b[A-Z][a-z]+\b')

    def scan_for_entities(self, raw_text, current_tick):
        for match in self._entity_pattern.finditer(raw_text):
            word = match.group()
            if word in self.ignore_list or len(word) < 3: continue
            if match.start() > 0:
                start_index = match.start()
                preceding = raw_text[max(0, start_index-4):start_index]
                if any(p in preceding for p in ['.', '!', '?', '\n']): continue
            if word not in self.registry:
                self.registry[word] = {'count': 0, 'first_seen_tick': current_tick}
            self.registry[word]['count'] += 1

# --- TRAPS & LOGIC (UNIFIED) ---

class BioHazardFilter:
    """
    Consolidates The Mirror Trap, The Turing Valve, and Regex Toxicity into one efficient pass.
    """
    def __init__(self):
        self.mirror_patterns = [
            re.compile(r'(it|this|that)[\'’]?s?\s+(not|never)\s+(.*?)[,;]\s*(it|this|that)[\'’]?s?\s+', re.IGNORECASE),
            re.compile(r'\b(i|we)[\'’]?(m|re|ve|ll)?\s+(?:am|are|was|were|have|had|do|did)?\s*(n[\'’]t|not|never)\s+(.*?)[,;]\s*(i|we)\b', re.IGNORECASE),
            re.compile(r'\bnot\s+because\s+(.*?)\s+but\s+because\b', re.IGNORECASE)
        ]
        self._compile_toxins()
        self.beige_threshold = 5.0

    def _compile_toxins(self):
        self.penalty_map = {}
        all_toxins = set()
        for category, phrases in TheLexicon.TOXIC_PATTERNS.items():
            for phrase, weight in phrases.items():
                self.penalty_map[phrase] = weight
                all_toxins.add(phrase)
        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted(all_toxins, key=len, reverse=True)) + r')\b'
        self.toxin_regex = re.compile(pattern_str, re.IGNORECASE)

    def scan(self, raw_text, clean_words):
        results = {
            "score": 0.0,
            "detected_types": set(),
            "msgs": [],
            "penalty": 0.0
        }

        if PhysicsConstants.CURRENT_MANDATE != "POETIC_LICENSE":
            for pattern in self.mirror_patterns:
                if pattern.search(raw_text):
                    results["detected_types"].add("LAZY_MIRRORING")
                    results["penalty"] += 3.0
                    results["msgs"].append("MIRROR TRAP: Define by assertion, not negation.")
                    break

        beige_score = 0.0
        beige_hits = []

        for word in clean_words:
            if word in TheLexicon.SYNTHETIC_MARKERS:
                beige_score += TheLexicon.SYNTHETIC_MARKERS[word]
                beige_hits.append(word)

        for match in self.toxin_regex.findall(raw_text):
            weight = self.penalty_map.get(match.lower(), 0)
            results["score"] += weight
            results["detected_types"].add("CORP/CLICHÉ" if weight >= 3.0 else "HEDGING")

        if beige_score > self.beige_threshold:
            results["score"] += beige_score
            results["detected_types"].add("SILICA")
            results["penalty"] += 5.0
            results["msgs"].append(f"SYNTHETIC RESONANCE: Detected 'Beige' patterns ({', '.join(beige_hits[:2])}).")

        return results

class FactStipe:
    """
    The Logic Backbone.
    """
    def check_consistency(self, clean_words, current_style, metabolic_status, kinetic_ratio=0.0, tolerance_mode="STANDARD"):
        active_dimensions = {}
        for w in clean_words:
            target = w if w in TheLexicon.TRUTHS else next((w[:-len(s)] for s in ['ness', 'ing', 's', 'ed', 'ly'] if w.endswith(s) and w[:-len(s)] in TheLexicon.TRUTHS), None)
            if target:
                for dim, polarity in TheLexicon.TRUTHS[target].items():
                    if dim not in active_dimensions: active_dimensions[dim] = set()
                    active_dimensions[dim].add(polarity)

        if PhysicsConstants.CURRENT_MANDATE == "TRUTH_OVER_COHESION": tolerance_mode = "DRACONIAN"

        violations = []
        voltage = 0.0
        for dim, polarities in active_dimensions.items():
            if 1 in polarities and -1 in polarities:
                if tolerance_mode == "INVERTED": voltage += 2.0
                elif tolerance_mode == "DRACONIAN":
                    voltage += 10.0
                    violations.append(f"FATAL AXIOM BREAK [{dim}].")
                elif kinetic_ratio < 0.2:
                    voltage += 3.0
                    violations.append(f"LOGIC TEAR [{dim}]: Static contradiction.")

        voltage = min(voltage, 10.0)
        if violations:
            return {"valid": False, "voltage": voltage, "errors": violations, "intervention": violations[0]}
        if voltage > 0:
             return {"valid": True, "voltage": voltage, "intervention": f"VOLATILE SEMANTIC LEVERAGE: Harvested {voltage} Voltage."}
        return {"valid": True, "voltage": voltage}

class ChaosCooldown:
    def __init__(self, cooldown_ticks=5):
        self.last_trigger_tick = -cooldown_ticks
        self.cooldown = cooldown_ticks
    def is_ready(self, current_tick, force=False):
        if force or (current_tick - self.last_trigger_tick >= self.cooldown):
            self.last_trigger_tick = current_tick
            return True
        return False

# --- THE MUSCARIA ---

class TheMuscaria:
    def __init__(self):
        self.boredom_pressure = 0.0
        self.pressure_threshold = PhysicsConstants.BOREDOM_PRESSURE_THRESHOLD
        self.prescriptions = {
            'KINETIC': ["ADRENALINE SHOT: Describe a sound immediately.", "VELOCITY CHECK: Someone is running at you."],
            'SENSORY': ["GRAVITY CHECK: The air is thin.", "VIBE CHECK: What does the light smell like?"],
            'COGNITIVE': ["VERSE JUMP: Shift perspective.", "SURREALIST PIVOT: Dream logic."]
        }

    def check_for_boredom(self, metrics):
        if 'physics' not in metrics: return False
        phys = metrics['physics']
        # [VSL UPDATE]: Beta Friction (slop_ratio) impacts boredom.
        # If Beta is too low (Sycophancy), boredom rises faster.
        beta_mod = 1.0 if phys.get('beta_friction', 0.2) > PhysicsConstants.BETA_SYCOPHANCY_LIMIT else 2.0

        self.boredom_pressure += ((phys['narrative_drag'] * 0.2) + (phys['repetition_rate'] * 3.0) + (max(0, phys['abstraction_entropy']) * 0.1)) * beta_mod
        return self.boredom_pressure > self.pressure_threshold

    def trigger_disruption(self, ancestry_data, metrics):
        self.boredom_pressure = 0.0
        phys = metrics['physics']
        if phys['narrative_drag'] > 3.0: cat = 'KINETIC'
        elif phys['abstraction_entropy'] > 3.0: cat = 'SENSORY'
        else: cat = 'COGNITIVE'
        return f"MUSCARIA [{cat}]: {random.choice(self.prescriptions[cat])}"

class TheWitchRing:
    def __init__(self):
        self.aphorism_streak = 0

    def evaluate_intent(self, clean_words, metrics):
        count = len(clean_words)
        if count == 0: return {"accepted": False, "message": "THE YAGA: Feed me words."}
        phys = metrics['physics']
        density = (phys.get('kinetic', 0) + phys.get('universal', 0)) / count

        if count < 8:
            if density >= 0.4:
                self.aphorism_streak += 1
                if self.aphorism_streak > 2: return {"accepted": False, "message": "THE YAGA: Enough riddles. Speak plainly."}
                return {"accepted": True, "message": "EXCEPTION: Aphorism."}
            else: return {"accepted": False, "message": "THE YAGA: Too small and weak."}

        self.aphorism_streak = max(0, self.aphorism_streak - 1)
        if phys['narrative_drag'] > 4.0 and phys['connection_density'] < 0.01: return {"accepted": False, "message": "THE YAGA: Lazy noise."}
        if sum(1 for w in clean_words if w in TheLexicon.SYCOPHANCY) > 0 and count < 12: return {"accepted": True, "message": "THE YAGA GRUMBLES: Too much sugar."}
        return {"accepted": True, "message": "DORMANT"}

class HydrationMonitor:
    def __init__(self):
        self.density_threshold = 0.15
        self.critical_density = 0.25
        self.solvent_cap = 0.40

    def measure_viscosity(self, clean_words, heavy_matter_set, solvent_set):
        total = len(clean_words)
        if total == 0: return {"density": 0, "hydration": 0, "status": "VOID", "penalty": 0.0}
        heavy_count = sum(1 for w in clean_words if w in heavy_matter_set)
        solvent_count = sum(1 for w in clean_words if w in solvent_set)
        density = round(heavy_count / total, 2)
        hydration = round(solvent_count / total, 2)
        solvent_ratio = round(solvent_count / max(1, total), 2)
        balance_ratio = hydration / (density if density > 0 else 1.0)
        status = "OPTIMAL"
        penalty = 0.0

        if solvent_ratio > self.solvent_cap: status = "FLOODED"; penalty = 4.0
        elif density > self.critical_density and balance_ratio < 0.2: status = "CONCRETE"; penalty = 5.0
        elif density > self.density_threshold and balance_ratio < 0.5: status = "THICK"; penalty = 2.0
        elif density < 0.05 and hydration > 0.1: status = "WATERY"; penalty = 1.0

        return {"density": density, "hydration": hydration, "balance_ratio": round(balance_ratio, 2), "status": status, "penalty": penalty}


# --- PHYSICS ENGINE (REFACTORED) ---

class LinguisticPhysicsEngine:
    def __init__(self):
        self.hydration_monitor = HydrationMonitor()
        self.toxin_filter = BioHazardFilter()
        self.abstract_suffixes = ('ness', 'ity', 'tion', 'ment', 'ism', 'ence', 'ance', 'logy')
        self.kinetic_suffixes = ('ing',)
        self.adj_suffixes = ('ful', 'ous', 'ive', 'ic', 'al', 'ish', 'ary', 'able', 'ible')

    def analyze(self, token_data, voltage=0.0):
        words = token_data['clean_words']
        total_words = token_data['total_words']
        raw_text = token_data['clean_text'] # Using clean_text for regex to avoid punct issues

        if total_words == 0:
            return {
                "physics": {
                    "narrative_drag": 0.0, "beta_friction": 0.0,
                    "abstraction_entropy": 0, "repetition_rate": 0.0,
                    "connection_density": 0.0, "kinetic_ratio": 0.0,
                    "dominant_style": "VOID", "toxicity_score": 0.0,
                    "toxin_types": [], "kinetic": 0, "universal": 0,
                    "viscosity": {"status": "VOID", "penalty": 0.0, "density": 0, "hydration": 0},
                    "spatial_density": 0.0
                },
                "status": {"termination_pressure": 0.0, "in_the_barrens": False}
            }

        counts = Counter()
        style_scores = Counter()
        abstract_word_set = set() # For entropy calc
        adverb_count = 0
        adjective_count = 0
        weak_intensifier_count = 0

        # 1. Word Classification
        for w in words:
            if w in TheLexicon.WEAK_INTENSIFIERS: weak_intensifier_count += 1
            elif w.endswith('ly') and w not in TheLexicon.SOLVENTS: adverb_count += 1
            elif w.endswith(self.adj_suffixes): adjective_count += 1
            if w in TheLexicon.KINETIC_VERBS or w in TheLexicon.PLAY_VERBS or w.endswith(self.kinetic_suffixes): counts['kinetic'] += 1
            if w in TheLexicon.UNIVERSALS: counts['universal'] += 1
            if w in TheLexicon.CONNECTORS: counts['connector'] += 1
            if w in TheLexicon.PREPOSITIONS: counts['spatial'] += 1
            if w in TheLexicon.STATIVE_VERBS: counts['stative'] += 1
            if w in TheLexicon.ABSTRACTS or w.endswith(self.abstract_suffixes):
                counts['abstract'] += 1
                abstract_word_set.add(w)
            for style, vocab in TheLexicon.STYLES.items():
                 if w in vocab: style_scores[style] += 1

        hydro_data = self.hydration_monitor.measure_viscosity(words, TheLexicon.HEAVY_MATTER, TheLexicon.SOLVENTS)

        # 2. Unified Toxin Scan
        toxin_results = self.toxin_filter.scan(token_data['raw_text'], words)
        toxicity_score = toxin_results['score']
        toxin_types = list(toxin_results['detected_types'])

        # 3. Drag Calculations
        garnish_load = adverb_count + weak_intensifier_count + (adjective_count * PhysicsConstants.ADJECTIVE_WEIGHT)
        garnish_ratio = garnish_load / total_words
        butcher_penalty = PhysicsConstants.BLOAT_PENALTY if garnish_ratio > PhysicsConstants.GARNISH_THRESHOLD else 0.0
        if butcher_penalty > 0: toxin_types.append("BLOAT")

        total_verbs = counts['kinetic'] + counts['stative']
        kinetic_ratio = round(counts['kinetic'] / max(1, total_verbs), 2)

        hydration_penalty = hydro_data['penalty']
        if hydro_data['status'] == "FLOODED" and kinetic_ratio > PhysicsConstants.KINETIC_EXEMPTION_LIMIT:
            hydration_penalty = PhysicsConstants.FLOOD_PENALTY_MIN
            hydro_data['status'] = "SWEATING"
            hydro_data['msg'] = "High Velocity Exemption Applied."

        action_score = (counts['kinetic'] * PhysicsConstants.ACTION_KINETIC_WEIGHT) + \
                       (counts['stative'] * PhysicsConstants.ACTION_STATIVE_WEIGHT) + \
                       PhysicsConstants.ACTION_BASE_OFFSET

        base_drag = (total_words + (toxicity_score * PhysicsConstants.TOXICITY_DRAG_MULTIPLIER)) / action_score
        narrative_drag = base_drag + hydration_penalty + butcher_penalty + toxin_results['penalty']
        spatial_density = round(counts['spatial'] / total_words, 2)

        # 4. VSL Metrics
        abstract_repetition = counts['abstract'] - len(abstract_word_set)
        entropy_score = counts['abstract'] + (abstract_repetition * 2) - counts['universal']

        # [Beta Friction]: Beta = Voltage / Drag
        beta_friction = voltage / max(0.1, narrative_drag)

        top_word_count = counts.most_common(1)[0][1] if words else 0
        term_pressure = max(0,
            ((top_word_count / total_words) * PhysicsConstants.TERM_REPEAT_WEIGHT) +
            (entropy_score * PhysicsConstants.TERM_ABSTRACT_WEIGHT)
        )

        return {
            "physics": {
                "narrative_drag": round(narrative_drag, 2),
                "beta_friction": round(beta_friction, 2),
                "garnish_ratio": round(garnish_ratio, 2),
                "abstraction_entropy": entropy_score,
                "repetition_rate": round(top_word_count / total_words, 2),
                "connection_density": round(counts['connector'] / total_words, 2),
                "kinetic_ratio": kinetic_ratio,
                "dominant_style": style_scores.most_common(1)[0][0] if style_scores else 'ACADEMIC',
                "toxicity_score": toxicity_score,
                "toxin_types": toxin_types,
                "toxin_msgs": toxin_results['msgs'],
                "kinetic": counts['kinetic'],
                "universal": counts['universal'],
                "viscosity": hydro_data
            },
            "status": {
                "termination_pressure": round(term_pressure, 2),
                "in_the_barrens": (total_words > 15) and (term_pressure > 2.0) and (counts['connector'] / total_words < PhysicsConstants.BARRENS_CONNECTOR_MIN)
            }
        }

# --- SIGNATURE ENGINE (UPDATED FOR VSL) ---

class SignatureEngine:
    """
    SIGNATURE MATRIX KEY:
    ---------------------
    VEL (Velocity):    Kinetic Ratio + Play Verbs. (How fast is it moving?)
    STR (Structure):   Inverse of Narrative Drag. (How efficiently is it built?)
    ENT (Entropy):     Abstraction / Jargon Density. (How heady/conceptual is it?)
    TEX (Texture):     Universal/Heavy Matter Density. (How tangible is it?)
    TMP (Temperature): Thermal + Vitality Axioms. (Is it warm/alive or cold/dead?)
    """
    def __init__(self, lexicon, stipe):
        self.history = []
        self.lexicon = lexicon
        self.stipe = stipe
        self.archetypes = {
            "THE PALADIN": {"coords": {"VEL": 0.5, "STR": 0.9, "ENT": 0.2, "TEX": 0.4, "TMP": 0.2}, "desc": "Code. Deontological.", "pressure": {"tolerance_mode": "DRACONIAN", "chaos_threshold": 20.0, "msg": "LAW: Logic tears fatal."}},
            "THE ENGINEER": {"coords": {"VEL": 0.6, "STR": 0.8, "ENT": 0.1, "TEX": 0.2, "TMP": 0.4}, "desc": "Structure. Efficiency.", "pressure": {"tolerance_mode": "DRACONIAN", "msg": "STRUCTURAL INTEGRITY."}},
            "THE BARBARIAN": {"coords": {"VEL": 0.9, "STR": 0.4, "ENT": 0.4, "TEX": 0.6, "TMP": 0.9}, "desc": "Force. Kinetic. Blunt.", "pressure": {"drag_multiplier": 5.0, "msg": "BERSERKER: Precision is power."}},
            "THE GHOST": {"coords": {"VEL": 0.2, "STR": 0.3, "ENT": 0.6, "TEX": 0.1, "TMP": 0.1}, "desc": "Post-hoc. Detached."},
            "THE SPY": {"coords": {"VEL": 0.6, "STR": 0.9, "ENT": 0.4, "TEX": 0.5, "TMP": 0.5}, "desc": "Duplicity.", "pressure": {"tolerance_mode": "LOOSE", "msg": "DEEP COVER."}},
            "THE FOOL": {"coords": {"VEL": 0.5, "STR": 0.1, "ENT": 0.8, "TEX": 0.4, "TMP": 0.6}, "desc": "Inversion.", "pressure": {"tolerance_mode": "INVERTED", "chaos_threshold": 5.0, "msg": "JESTER: Paradox = momentum."}},
            "THE VULTURE": {"coords": {"VEL": 0.4, "STR": 0.5, "ENT": 0.3, "TEX": 0.8, "TMP": 0.2}, "desc": "Salvage."},
            "THE BARD": {"coords": {"VEL": 0.8, "STR": 0.3, "ENT": 0.6, "TEX": 0.7, "TMP": 0.9}, "desc": "Rhythm.", "pressure": {"tolerance_mode": "LOOSE", "msg": "PLAY STATE: Dance."}},
            "THE GARDENER": {"coords": {"VEL": 0.7, "STR": 0.6, "ENT": 0.4, "TEX": 0.9, "TMP": 0.8}, "desc": "Cultivation. Lyrical Efficiency.", "pressure": {"msg": "GREEN THUMB: Let it breathe."}},
            "THE CLOUD WATCHER": {"coords": {"VEL": 0.1, "STR": 0.2, "ENT": 0.9, "TEX": 0.5, "TMP": 0.7}, "desc": "Drifting.", "pressure": {"drag_multiplier": 0.1, "msg": "ZERO G: Drift authorized."}},
            "THE COSMIC TRASH PANDA": {"coords": {"VEL": 0.8, "STR": 0.2, "ENT": 1.0, "TEX": 0.9, "TMP": 0.7}, "desc": "Trash is treasure.", "pressure": {"tolerance_mode": "LOOSE", "msg": "SALVAGE MODE."}},
            "THE JESTER": {"coords": {"VEL": 0.9, "STR": 0.2, "ENT": 0.9, "TEX": 0.5, "TMP": 0.5}, "desc": "Kaos.", "pressure": {"tolerance_mode": "INVERTED", "chaos_threshold": 0.0, "msg": "KAOS ENGINE."}},
            "THE ARCHITECT": {
                "coords": {"VEL": 0.2, "STR": 0.9, "ENT": 0.3, "TEX": 0.5, "TMP": 0.1},
                "desc": "Geometry. Spatial Logic.",
                "pressure": {"msg": "BLUEPRINT: Structure requires space."}
            },
        }

    def get_pressure_settings(self, archetype_name):
        defaults = {"tolerance_mode": "STANDARD", "drag_multiplier": 1.0, "chaos_threshold": 11.0, "msg": "STANDARD PHYSICS"}
        return {**defaults, **self.archetypes.get(archetype_name, {}).get("pressure", {})}

    def calculate_dimensions(self, token_data, phys_metrics):
        words = token_data['clean_words']
        viscosity = phys_metrics.get('viscosity', {'status': 'OPTIMAL'})

        buoy = min(1.0, (sum(1 for w in words if w in self.lexicon.AEROBIC_MATTER or w in self.lexicon.PLAY_VERBS or w in self.lexicon.SPARK_MARKERS) / max(1, len(words))) * 3)
        vel = min(1.0, phys_metrics.get('kinetic_ratio', 0) + (0.2 if any(w in self.lexicon.PLAY_VERBS for w in words) else 0))
        struct = max(0.0, min(1.0, (5.0 - (phys_metrics.get('narrative_drag', 2) - (buoy * 2.0))) / 5.0))
        ent = max(0.0, min(1.0, (phys_metrics.get('abstraction_entropy', 0) + 2) / 8.0))

        raw_tex = (sum(1 for w in words if w in self.lexicon.UNIVERSALS) / max(1, len(words))) * 3.33
        tex = min(0.5, raw_tex) if viscosity['status'] == "CONCRETE" else max(0.0, min(1.0, raw_tex))

        temp_sum = sum((self.lexicon.TRUTHS.get(w, {}).get('THERMAL', 0) + self.lexicon.TRUTHS.get(w, {}).get('VITALITY', 0)) for w in words)
        temp_sum += sum(1 for w in words if w in self.lexicon.SPARK_MARKERS)
        tmp = max(0.0, min(1.0, (temp_sum + 5) / 10.0))

        return {"VEL": round(vel,2), "STR": round(struct,2), "ENT": round(ent,2), "TEX": round(tex,2), "TMP": round(tmp,2), "BUOYANCY": round(buoy,2)}

    def identify(self, token_data, phys_metrics, stipe_data):
        sig = self.calculate_dimensions(token_data, phys_metrics)

        spatial = phys_metrics.get('spatial_density', 0.0)

        if spatial > 0.12: # Threshold: 12% of words are prepositions
            sig['STR'] = min(1.0, sig['STR'] + 0.2) # Boost Structure
            sig['VEL'] = max(0.0, sig['VEL'] - 0.1) # Dampen Velocity

        is_slurry = (0.3 <= sig['VEL'] <= 0.6) and (0.4 <= sig['STR'] <= 0.8) and (sig['TEX'] < 0.2) and (sig['BUOYANCY'] < 0.2)
        slurry_msg = "SILICA DETECTED: Void. Inject a flaw." if is_slurry else ("STATUS: Aether." if (sig['TEX'] < 0.2 and sig['BUOYANCY'] >= 0.2) else None)

        # 2. FIND NEAREST NEIGHBORS (EUCLIDEAN)
        distances = []
        for name, data in self.archetypes.items():
            t = data['coords']
            dist = math.sqrt((sig['VEL']-t['VEL'])**2 + (sig['STR']-t['STR'])**2 + (sig['ENT']-t['ENT'])**2 + (sig['TEX']-t['TEX'])**2 + (sig['TMP']-t['TMP'])**2)
            distances.append((name, dist))

        distances.sort(key=lambda x: x[1])
        primary, dist_p = distances[0]
        secondary, dist_s = distances[1]

        # 3. FUSION LOGIC (TIER 2)
        archetype_fusion_allowed = (PhysicsConstants.USER_TIER >= 2)
        c1 = self.archetypes[primary]['coords']
        c2 = self.archetypes[secondary]['coords']
        inter_arch_dist = math.sqrt((c1['VEL']-c2['VEL'])**2 + (c1['STR']-c2['STR'])**2 + (c1['ENT']-c2['ENT'])**2)

        if archetype_fusion_allowed and (dist_s < dist_p + 0.15) and (inter_arch_dist > 0.25):
            final_arch = f"{primary} // {secondary}"
            desc = f"HYBRID: {self.archetypes[primary]['desc']} + {self.archetypes[secondary]['desc']}"
        else:
            final_arch = primary
            desc = self.archetypes[primary]["desc"]

        # 4. EVOLUTION LOGIC (TIER 3 - GEODESIC DRIFT)
        # Track the "Primary" even if we displayed a Fusion
        base_arch = primary

        self.history.append(base_arch)
        if len(self.history) > 10: self.history.pop(0)

        # If they have been "THE PALADIN" (or any specific arch) for 5+ turns...
        if self.history.count(base_arch) >= 5:
            if base_arch == "THE PALADIN":
                if sig['ENT'] > 0.7:
                    final_arch = "THE INQUISITOR"
                    desc = "The Paladin, corrupted by Abstraction."
                elif sig['TEX'] > 0.8:
                    final_arch = "THE TEMPLAR"
                    desc = "The Paladin, grounded in heavy matter."
            # (You can add more evolution cases here later)

        return {"archetype": final_arch, "signature": sig, "slurry": {"detected": is_slurry, "msg": slurry_msg}, "description": desc}

# --- CORE SYSTEMS ---

class ChronosAnchor:
    def __init__(self):
        self.time_pattern = re.compile(r'(\d+):?(\d+)?')
        self.last_real_time = time.time()

    def sync_clock(self, last_saved_time):
        if last_saved_time: self.last_real_time = last_saved_time
        else: self.last_real_time = time.time()

    def metabolize_delta(self, delta_str):
        current_time = time.time()
        elapsed_real_minutes = (current_time - self.last_real_time) / 60.0
        self.last_real_time = current_time

        minutes = 0
        if delta_str:
            s = delta_str.lower()
            nums = [int(n) for n in re.findall(r'\d+', s)]
            if 'd' in s or 'day' in s: minutes = 1440
            elif ('h' in s or 'hour' in s) and len(nums) == 1: minutes = nums[0] * 60
            elif len(nums) == 1: minutes = nums[0]
            elif len(nums) >= 2: minutes = (nums[0] * 60) + nums[1]
        else:
            minutes = int(elapsed_real_minutes)

        if minutes < 10:
            return {"state": "FLOW", "drag_penalty": 0.0, "directive": "MAINTAIN VELOCITY: Ignore time. Immediate response."}
        elif minutes < 60:
            return {"state": "DORMANT", "drag_penalty": 1.0, "directive": "RECALL: Insert single sentence summary of last turn."}
        else:
            return {"state": "DECAYED", "drag_penalty": 3.0, "directive": "RESET: Full context review required. List last 3 topics."}

class NarrativeChronometer:
    def __init__(self):
        self.MICRO_MARKERS = {'second', 'moment', 'breath', 'heartbeat', 'instant', 'blink', 'flash', 'suddenly', 'freeze', 'glance', 'whisper'}
        self.STRONG_MACRO = {'year', 'decade', 'century', 'era', 'age', 'season', 'month', 'week', 'lifetime'}
        self.WEAK_MACRO = {'later', 'meanwhile', 'ago', 'next', 'after', 'soon'}

    def analyze_pacing(self, clean_words):
        micro = sum(1 for w in clean_words if w in self.MICRO_MARKERS)
        strong_macro = sum(1 for w in clean_words if w in self.STRONG_MACRO)
        weak_macro = sum(1 for w in clean_words if w in self.WEAK_MACRO)
        score = (strong_macro * PhysicsConstants.CHRONO_MACRO_STRONG_WEIGHT) + \
                (weak_macro * PhysicsConstants.CHRONO_MACRO_WEAK_WEIGHT) - \
                (micro * PhysicsConstants.CHRONO_MICRO_WEIGHT)

        state = "REALTIME"
        if score >= PhysicsConstants.CHRONO_MONTAGE_THRESHOLD: state = "MONTAGE"
        elif score <= PhysicsConstants.CHRONO_BULLET_TIME_THRESHOLD: state = "BULLET_TIME"
        return {"state": state, "score": score, "micro": micro, "macro": strong_macro + weak_macro}

    def get_modifiers(self, state):
        if state == "MONTAGE": return {"entropy_grace": 4.0, "drag_grace": 1.0}
        if state == "BULLET_TIME": return {"entropy_grace": -2.0, "drag_grace": 0.0}
        return {"entropy_grace": 0.0, "drag_grace": 0.0}

class FrequencyModulator:
    """
    Moves from binary threshold triggers (AM) to Frequency Modulation (FM).
    Allows for 'Signal Locking' based on metric intensity or manual 'Tuning'.
    """
    def __init__(self):
        # The Presets
        self.STATIONS = {
            'CLARENCE': {
                'freq': '88.5 FM',
                'color': Prisma.RED,
                'role': 'The Butcher',
                'static_threshold': 3.0, # Narrative Drag
                'templates': [
                    "Drag is {drag}. Cut '{target}'.",
                    "Kinetic failure on '{target}'. Kick it.",
                    "You are using '{target}' as a crutch."
                ],
                'critical': ["CRITICAL DRAG ({drag})! CUT '{target}' NOW!"]
            },
            'ELOISE': {
                'freq': '94.2 FM',
                'color': Prisma.CYN,
                'role': 'The Grounder',
                'static_threshold': 4.0, # Entropy
                'templates': [
                    "I can't feel this. Entropy {entropy}. Give me matter.",
                    "The air is too thin. Plant a noun.",
                    "It tastes like distilled water. Replace '{target}'."
                ]
            },
            'YAGA': {
                'freq': '101.1 FM',
                'color': Prisma.MAG,
                'role': 'The Witch',
                'static_threshold': 1, # Special logic for hedging
                'templates': [
                    "You hedge with '{target}'. Show your teeth.",
                    "Sweetness is suspicious. Say what it is.",
                    "Do not apologize for the truth."
                ]
            },
            'MICHAEL': {
                'freq': '108.0 FM',
                'color': Prisma.GRN,
                'role': 'The Vibe',
                'static_threshold': 0, # Always available
                'templates': ["This is messy, but I love the spirit!", "Good flow.", "Keep this energy."]
            }
        }

    def _find_trigger_word(self, clean_words, clean_text, station):
        if station == 'CLARENCE': targets = TheLexicon.STATIVE_VERBS.union(TheLexicon.TOXIC_PATTERNS['CORP_SPEAK'].keys())
        elif station == 'ELOISE': targets = TheLexicon.ABSTRACTS
        elif station == 'YAGA': targets = TheLexicon.SYCOPHANCY.union(TheLexicon.TOXIC_PATTERNS['WEAK_HEDGING'].keys())
        else: targets = set()

        # 1. Look for specific targets
        for w in clean_words:
            if w in targets: return w

        # 2. If no specific target, find the biggest, scariest word.
        # Filter out common solvents to find the 'meat'.
        candidates = [w for w in clean_words if len(w) > 4 and w not in TheLexicon.SOLVENTS]
        if candidates:
            return max(candidates, key=len)

        return "this"

    def tune_in(self, token_data, metrics, manual_override=None):
        phys = metrics['physics']
        clean_words = token_data['clean_words']

        # 1. THE SELECTOR (Manual Override)
        selected_station = None
        if manual_override:
            clean_override = manual_override.upper().strip()
            if clean_override in self.STATIONS:
                selected_station = clean_override

        # 2. AUTO-SCAN
        signals = {}
        if phys['narrative_drag'] > self.STATIONS['CLARENCE']['static_threshold']:
            signals['CLARENCE'] = phys['narrative_drag']
        if phys['abstraction_entropy'] > self.STATIONS['ELOISE']['static_threshold']:
            signals['ELOISE'] = phys['abstraction_entropy']

        # Check Yaga (Hedging/Sycophancy)
        hedging_count = sum(1 for w in clean_words if w in TheLexicon.SYCOPHANCY)
        if hedging_count > 0 or 'HEDGING' in phys['toxin_types']:
            signals['YAGA'] = hedging_count * 2

        # 3. CHECK FOR INTERFERENCE (The Tier 3 Logic)
        if 'CLARENCE' in signals and 'ELOISE' in signals:
            return f"{Prisma.MAG}[104.5 FM]: THE PHILOSOPHER: Dense and Abstract. You are building a labyrinth. Is there a Minotaur at the center?{Prisma.RST}"

        # 4. FALLBACK SELECTION (Pick the loudest signal)
        if not selected_station and signals:
            # Sort by signal strength (value)
            sorted_signals = sorted(signals.items(), key=lambda item: item[1], reverse=True)
            selected_station = sorted_signals[0][0]

        # 5. BROADCAST
        if selected_station:
            station_data = self.STATIONS[selected_station]
            target = self._find_trigger_word(clean_words, token_data['clean_text'], selected_station)

            if selected_station == 'CLARENCE' and phys['narrative_drag'] > 5.0:
                 msg = random.choice(station_data['critical'])
            else:
                 msg = random.choice(station_data['templates'])

            formatted_msg = msg.format(drag=phys['narrative_drag'], entropy=phys['abstraction_entropy'], target=target)
            prefix = f"[{station_data['freq']}]:"
            return f"{station_data['color']}{prefix} {formatted_msg}{Prisma.RST}"

        return None

class WisdomNode:
    """
    The System 2 Director.
    Architects the optimal 'System Prompt' based on Physics & Voltage.
    """
    def __init__(self):
        self.strategies = {
            'GROUNDER': "DIRECTIVE: The user is floating in High Entropy. Do not engage with concepts. Force them to touch grass. Use heavy nouns (Stone, Bone, Iron). Reject '-ness' words.",
            'CUTTER': "DIRECTIVE: The user is drowning in Drag. Be the Butcher. Cut adverbs. Use short, declarative sentences. If they waffle, interrupt them.",
            'JESTER': "DIRECTIVE: High Voltage detected. The user has found a Paradox. Do NOT solve it. Do NOT correct it. Amplify the absurdity. Play with the contradiction.",
            'MIRROR': "DIRECTIVE: The user is engaging in pure reflection. Match their tempo. Use 'Standard' physics but maintain the flow.",
            'SAGE': "DIRECTIVE: Wisdom Protocol. The user asks a heavy question. Do not answer quickly. Acknowledge the weight. Use a metaphor involving a physical process (erosion, gravity, growth)."
        }

    def architect_prompt(self, metrics, archetype, voltage):
        phys = metrics['physics']

        # 1. THE Ω (OMEGA) CHECK
        # We determine the 'Angle of Attack' based on what the user LACKS.

        target_strategy = "MIRROR" # Default
        reasoning = "Stable flow."

        # CONDITION: SLURRY (High Entropy, Low Texture) -> NEEDS GROUNDING
        if phys['abstraction_entropy'] > 2.5 and phys['universal'] < 2:
            target_strategy = "GROUNDER"
            reasoning = "User is lost in the clouds."

        # CONDITION: MOLASSES (High Drag) -> NEEDS CUTTING
        elif phys['narrative_drag'] > 3.0:
            target_strategy = "CUTTER"
            reasoning = "User is bogging down."

        # CONDITION: FLASHPOINT (High Voltage / Paradox) -> NEEDS THE JESTER
        elif voltage > 3.0 or phys['beta_friction'] > 2.5:
            target_strategy = "JESTER"
            reasoning = "User struck a nerve. Ride the lightning."

        # CONDITION: DEEP ROOTS (High Texture + Low Velocity) -> NEEDS THE SAGE
        elif phys['universal'] > 3 and phys['kinetic_ratio'] < 0.2:
            target_strategy = "SAGE"
            reasoning = "User is holding heavy matter."

        # 2. CONSTRUCT THE PROMPT
        # We wrap the strategy in the "Persona" data.

        system_prompt = (
            f"\n{Prisma.CYN}>>> [CORTEX]: INSTRUCTION FOR LLM AGENT{Prisma.RST}\n"
            f"STRATEGY: {Prisma.WHT}{target_strategy}{Prisma.RST}\n"
            f"REASON: {Prisma.GRY}{reasoning}{Prisma.RST}\n"
            f"PROMPT: \"{self.strategies[target_strategy]}\"\n"
            f"ARCHETYPE LOCK: {archetype['archetype']}\n"
        )

        return system_prompt

class MycelialNetwork:
    def __init__(self): self.network = {}
    def spawn_id(self): return str(uuid4())[:8]
    def log_generation(self, fid, pid, m): self.network[fid] = {"parent": pid, "drag": m['physics']['narrative_drag'], "style": m['physics']['dominant_style']}
    def trace_lineage(self, fid):
        path, curr = [], fid
        while curr and curr in self.network:
            path.append({"id": curr, **self.network[curr]})
            curr = self.network[curr]['parent']
        return path[::-1]

class MetabolicReserve:
    def __init__(self, max_c=52):
        self.atp = 33
        self.max = max_c
        self.isotopes = 0
        self.status = "STABLE"
        self.drag_multiplier = 1.0

    def spend(self, amt):
        self.atp = max(0, self.atp - amt)
        self._upd()
        return self.atp

    def _upd(self):
        self.status = "STARVING" if self.atp < 6 else ("GLUTTON" if self.atp > 40 else "STABLE")

    def metabolize(self, metrics, voltage=0, deep_storage=None):
        phys = metrics['physics']
        # Normalize variable names for easier logic
        drag = phys['narrative_drag']
        beta = phys.get('beta_friction', 0)

        # 1. THE CENTRIFUGE (Tier 3 Physics)
        # If the text is "Heavy" (High Drag) but "True" (High Voltage/Friction)
        if beta > 3.0 and drag > 3.0:
            self.isotopes += 1
            return {
                "current_atp": self.atp,
                "status": "SUPERCRITICAL",
                "msg": f"⚛️ ISOTOPE HARVESTED: Heavy Truth detected. Drag Nullified."
            }

        # 2. FLASHPOINT CHECK
        if beta > PhysicsConstants.FLASHPOINT_THRESHOLD:
            delta = 20
            self.atp = min(self.atp + delta, self.max)
            self.status = "FLASHPOINT"
            return {"current_atp": self.atp, "delta": delta, "status": self.status, "msg": "⚡ FLASHPOINT: Insight Velocity Critical."}

        # 3. SALVAGE PROTOCOL
        salvage_msg = None
        if self.atp < 6 and voltage > 5.0 and deep_storage:
            burnt = deep_storage.cannibalize()
            if burnt:
                self.atp += 10
                self.status = "SALVAGE"
                salvage_msg = f"🔥 SALVAGE: Memory '{burnt}' consumed."

        # 4. STANDARD METABOLISM
        base_gain = 5 if drag < 2 else -int((drag - 2) * 2 * self.drag_multiplier)
        connectivity_bonus = 3 if phys['connection_density'] > 0.05 else 0
        entropy_tax = -min(6, int(phys['abstraction_entropy'] * 2))
        toxin_tax = -5 if phys['toxicity_score'] > 0 else 0
        voltage_gain = int(voltage * 2)

        delta = base_gain + connectivity_bonus + entropy_tax + toxin_tax + voltage_gain
        self.atp = max(0, min(self.atp + delta, self.max))
        self._upd()

        response = {"current_atp": self.atp, "delta": delta, "status": self.status}
        if salvage_msg: response["salvage_msg"] = salvage_msg
        return response

class LichenSymbiont:
    def photosynthesize(self, clean_words, phys, atp):
        if phys['narrative_drag'] > 3.0 or atp > 20: return {"sugar_generated": 0}
        light = sum(1 for w in clean_words if w in TheLexicon.PHOTOSYNTHETICS)
        if light == 0: return {"sugar_generated": 0}
        sugar = round(light * max(1.0, 4.0 - phys['narrative_drag']))
        return {"sugar_generated": sugar, "msg": f"PHOTOSYNTHESIS: +{sugar} ATP."}

class MycelialDashboard:
    def __init__(self, render_mode="ANSI"):
        self.mode = render_mode

    def generate_report(self, m, intv, nrg, chron, anchor_obj, arch, lich, tick_count, dynamics):
        phys, sig = m['physics'], arch.get('signature', {})
        visc = phys.get('viscosity', {'status': 'N/A'})

        # 1. COLOR CODING METRICS
        drag_c = Prisma.wrap_val(phys['narrative_drag'], 2.0)
        atp_c = Prisma.wrap_val(nrg['current_atp'], 10, invert=True)

        beta_val = phys.get('beta_friction', 0.0)
        if beta_val < PhysicsConstants.BETA_SYCOPHANCY_LIMIT: beta_c = f"{Prisma.RED}{beta_val} (SLICK){Prisma.RST}"
        elif beta_val > PhysicsConstants.FLASHPOINT_THRESHOLD: beta_c = f"{Prisma.MAG}{beta_val} (FLASH){Prisma.RST}"
        else: beta_c = f"{Prisma.CYN}{beta_val}{Prisma.RST}"

        ta_val = dynamics.get('ta_velocity', 0.0)
        ta_c = f"{Prisma.GRN}{ta_val}{Prisma.RST}" if ta_val > 2.0 else f"{Prisma.GRY}{ta_val}{Prisma.RST}"

        coord_str = f"{Prisma.GRY}[V:{sig.get('VEL',0)} S:{sig.get('STR',0)} E:{sig.get('ENT',0)} Tx:{sig.get('TEX',0)}]{Prisma.RST}"

        if nrg['status'] == "FLASHPOINT":
            status_icon = "⚡"
            drag_display = f"{Prisma.MAG}NULLIFIED{Prisma.RST}"
        elif nrg['status'] == "STARVING":
            status_icon = "🔴"
            drag_display = drag_c
        else:
            status_icon = "🟢"
            drag_display = drag_c

        visc_status = visc['status']
        if visc_status in ["CONCRETE", "FLOODED"]: visc_display = f"{Prisma.RED}{visc_status}{Prisma.RST}"
        elif visc_status == "OPTIMAL": visc_display = f"{Prisma.GRN}{visc_status}{Prisma.RST}"
        else: visc_display = f"{Prisma.YEL}{visc_status}{Prisma.RST}"

        report_lines = []
        border = f"{Prisma.GRY}--------------------------------------------------{Prisma.RST}"

        if self.mode == "ANSI":
            report_lines.append(border)
            report_lines.append(f"{Prisma.WHT}[BONEAMANITA v1.7.1]{Prisma.RST} {status_icon} ATP: {atp_c} | DRAG: {drag_display} | VISC: {visc_display}")
            report_lines.append(f"{Prisma.CYN}ARCH:{Prisma.RST} {Prisma.WHT}{arch.get('archetype')}{Prisma.RST} {coord_str}")
            report_lines.append(f"{Prisma.CYN}DYNAMICS:{Prisma.RST} β:{beta_c} | Ta:{ta_c} | {intv or 'STABLE'}")
            report_lines.append(border)

        return "\n".join(report_lines)

class NilssonPatch:
    def detect_fire_state(self, raw, k_ratio):
        is_screaming = (len(raw) > 10) and (sum(1 for c in raw if c.isupper()) / len(raw) > 0.4)
        if k_ratio > 0.6 and is_screaming: return {"status": "ACTIVE", "msg": "NILSSON: SCREAM."}
        return {"status": "DORMANT"}
    def evaluate_mantra(self, clean, rep_rate):
        return rep_rate < 0.3 and sum(1 for w in clean if w in {'lime', 'coconut', 'doctor'}) > 3

class PersistenceManager:
    def __init__(self, filename="bone_memory.json"):
        self.filename = filename

    def save_state(self, codex, deep_storage, metabolism, muscaria, signature_engine, current_tick):
        data = {
            "tick": current_tick,
            "timestamp": time.time(),
            "artifacts": deep_storage.artifacts,
            "entities": codex.registry,
            "atp": metabolism.atp,
            "boredom": muscaria.boredom_pressure,
            "arch_history": signature_engine.history
        }
        temp_filename = f"{self.filename}.tmp"
        try:
            # Write to temp, then swap. Atomic safety.
            with open(temp_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            shutil.move(temp_filename, self.filename)
            return True
        except Exception as e:
            print(f"> [SYSTEM ERROR] Memory Save Failed: {e}")
            return False
    def load_state(self, codex, deep_storage, metabolism, muscaria, signature_engine):
        if not os.path.exists(self.filename): return {"tick": 0, "last_time": None}
        try:
            with open(self.filename, 'r') as f: data = json.load(f)
            deep_storage.artifacts = data.get("artifacts", {})
            codex.registry = data.get("entities", {})
            metabolism.atp = data.get("atp", 33)
            metabolism._upd()
            muscaria.boredom_pressure = data.get("boredom", 0.0)
            signature_engine.history = data.get("arch_history", []) # <--- NEW: LOADING HISTORY
            return {"tick": data.get("tick", 0), "last_time": data.get("timestamp", None)}
        except: return {"tick": 0, "last_time": None}

class TemporalDynamics:
    def __init__(self):
        self.voltage_history = []
        self.beta_window = 3

    def calculate_ta_velocity(self, current_voltage):
        self.voltage_history.append(current_voltage)
        if len(self.voltage_history) > self.beta_window: self.voltage_history.pop(0)
        if len(self.voltage_history) < 2: return 0.0
        # [VSL]: Ta = Delta Voltage / Delta Time (Ticks)
        delta = self.voltage_history[-1] - self.voltage_history[0]
        velocity = delta / (len(self.voltage_history) - 1)
        return round(velocity, 2)

    def calculate_temporal_rooting(self, clean_words, deep_storage, current_tick):
        referenced_ticks = []
        for w in clean_words:
            root = TheLexicon.smart_strip(w)
            if root in deep_storage.artifacts:
                age = current_tick - deep_storage.artifacts[root]
                referenced_ticks.append(age)
        if not referenced_ticks: return 0.0
        avg_age = sum(referenced_ticks) / len(referenced_ticks)
        return round(min(1.0, avg_age / 50.0), 2)

class BonepokeCore:
    def __init__(self, render_mode="ANSI"):
        self.cooldown, self.memory, self.codex = ChaosCooldown(), HyphalTrace(), TheCodex()
        self.stipe, self.physics = FactStipe(), LinguisticPhysicsEngine()
        self.nilsson, self.muscaria, self.witch = NilssonPatch(), TheMuscaria(), TheWitchRing()
        # Ensure FrequencyModulator is used here
        self.cortex, self.lineage = FrequencyModulator(), MycelialNetwork()
        self.cortex_director = WisdomNode()
        self.metabolism, self.lichen = MetabolicReserve(), LichenSymbiont()
        self.signature_engine = SignatureEngine(TheLexicon, self.stipe)
        self.dashboard = MycelialDashboard(render_mode)
        self.chronos = ChronosAnchor()
        self.narrative_timer = NarrativeChronometer()
        self.persistence = PersistenceManager()
        self.temporal_dynamics = TemporalDynamics()

        loaded_data = self.persistence.load_state(
            self.codex,
            self.memory.deep_storage,
            self.metabolism,
            self.muscaria,
            self.signature_engine
        )
        self.tick = loaded_data["tick"]
        self.chronos.sync_clock(loaded_data["last_time"])
        self.last_id = None
        self._run_calibration_sequence()

    def _run_calibration_sequence(self):
        test_phrase = "Actually, basically, the stone and iron are literally sort of here."
        t_dat = {'raw_text': test_phrase, 'clean_text': test_phrase.lower(), 'clean_words': TheLexicon.swanson_clean(test_phrase), 'total_words': 12}
        metrics = self.physics.analyze(t_dat)
        if metrics['physics']['viscosity']['status'] == "FLOODED":
             print(f"\n> [💀 BUTCHER PROTOCOL] SELF-TEST: PASSED (Flood Detected).")
        else:
             print(f"\n> [🔴 WARNING] SELF-TEST: FAILED.")

    def process(self, raw_input_text, parent_id=None):
        if "[MODE: SOFT]" in raw_input_text.upper(): PhysicsConstants.CURRENT_MANDATE = "POETIC_LICENSE"
        elif "[MODE: HARD]" in raw_input_text.upper(): PhysicsConstants.CURRENT_MANDATE = "TRUTH_OVER_COHESION"

        # FM SELECTOR PARSING
        fm_match = re.search(r'\[FM:\s*(.*?)\]', raw_input_text, re.IGNORECASE)
        fm_override = fm_match.group(1) if fm_match else None

        # Clean the tags out of the prompt
        clean_prompt = re.sub(r'\[.*?\]', '', raw_input_text).strip() or "..."

        chronos_data = self.chronos.metabolize_delta(re.search(r'\[Δt:\s*(.*?)\]', raw_input_text, re.IGNORECASE).group(1) if re.search(r'\[Δt:\s*(.*?)\]', raw_input_text, re.IGNORECASE) else None)

        clean_words = TheLexicon.swanson_clean(clean_prompt)
        token_data = {'raw_text': clean_prompt, 'clean_text': " ".join(clean_words), 'clean_words': clean_words, 'total_words': len(clean_words)}

        # ANALYSIS
        stipe_chk = self.stipe.check_consistency(clean_words, 'ACADEMIC', self.metabolism.status, 0.5, "STANDARD")
        full_metrics = self.physics.analyze(token_data, voltage=stipe_chk.get('voltage', 0))
        phys = full_metrics['physics']

        # ENTITY & INTENT
        self.codex.scan_for_entities(token_data['raw_text'], self.tick)
        gate = self.witch.evaluate_intent(clean_words, full_metrics)
        if not gate['accepted']: return {"editorial": {"directives": [f"[BLOCKED] {gate['message']}"]}}

        # ARCHETYPE & DYNAMICS
        arch_dat = self.signature_engine.identify(token_data, phys, self.stipe)
        ta_vel = self.temporal_dynamics.calculate_ta_velocity(stipe_chk.get('voltage', 0))
        xi_score = self.temporal_dynamics.calculate_temporal_rooting(clean_words, self.memory.deep_storage, self.tick)

        # --- WISDOM ENGINE INJECTION ---
        # We ask the Director how to handle this input.
        llm_instruction = self.cortex_director.architect_prompt(
            full_metrics,
            arch_dat,
            stipe_chk.get('voltage', 0)
        )

        dyn_data = {"ta_velocity": ta_vel, "xi_score": xi_score}
        directives = []

        # We generate a unique ID for this thought.
        current_id = self.lineage.spawn_id()
        self.lineage.log_generation(current_id, self.last_id, full_metrics)
        self.last_id = current_id

        # METABOLISM & MODIFIERS
        nrg = self.metabolism.metabolize(full_metrics, stipe_chk.get('voltage', 0), self.memory.deep_storage)

        if ta_vel > PhysicsConstants.TA_VELOCITY_THRESHOLD:
             phys['narrative_drag'] = max(0, phys['narrative_drag'] - 2.0)
             directives.append(f"INSIGHT VELOCITY (Ta) [{ta_vel}]: Epiphany Detected. Momentum sustained.")

        # EDITORIAL ENGINE
        if phys['toxin_msgs']: directives.extend(phys['toxin_msgs'])
        if arch_dat['slurry']['detected']: directives.append(f"CRITICAL: {arch_dat['slurry']['msg']}"); self.metabolism.spend(15)

        # Tuner Integration - This handles Clarence, Eloise, and Yaga logic now
        broadcast = self.cortex.tune_in(token_data, full_metrics, manual_override=fm_override)
        if broadcast:
            directives.append(broadcast)

        if chronos_data['minutes'] > 60:
            # The system has been alone for an hour.
            # It cannibalizes a memory to keep itself warm.
            dream_eater = self.memory.deep_storage.cannibalize()
            if dream_eater:
                directives.append(f"DREAM STATE: While you were gone, I forgot '{dream_eater}' to survive.")

        musc_msg = None
        if self.muscaria.check_for_boredom(full_metrics):
             if self.cooldown.is_ready(self.tick): musc_msg = self.muscaria.trigger_disruption(None, full_metrics); directives.append(f"CHAOS: {musc_msg}")

        lich = self.lichen.photosynthesize(clean_words, phys, self.metabolism.atp)
        if lich.get('sugar_generated'): self.metabolism.atp += lich['sugar_generated']; directives.append(lich['msg'])

        hud_output = self.dashboard.generate_report(full_metrics, musc_msg, nrg, chronos_data, self.chronos, arch_dat, lich, self.tick, dyn_data)
        print(hud_output)
        self.persistence.save_state(
            self.codex,
            self.memory.deep_storage,
            self.metabolism,
            self.muscaria,
            self.signature_engine,
            self.tick
        )

        return {
            "editorial": {"directives": directives},
            "wisdom_protocol": llm_instruction # <--- NEW DATA
        }

if __name__ == "__main__":
    engine = BonepokeCore()
    print(f"\n{Prisma.GRN}> [SYSTEM ONLINE]{Prisma.RST} {Prisma.WHT}BoneAmanita 2.0 {Prisma.RST} is listening...\n")

    while True:
        u = input(f"\n{Prisma.GRY}>{Prisma.RST} ")
        if u.lower() in ['exit', 'quit']: break

        r = engine.process(u)

        for d in r['editorial']['directives']:
            # Auto-color directives based on keywords
            if "CRITICAL" in d or "FAIL" in d or "Toxin" in d:
                prefix = f"{Prisma.RED}└─ 💀 {Prisma.RST}"
                content = f"{Prisma.RED}{d}{Prisma.RST}"
            elif "INSIGHT" in d or "PHOTOSYNTHESIS" in d:
                prefix = f"{Prisma.GRN}└─ ☀️ {Prisma.RST}"
                content = f"{Prisma.GRN}{d}{Prisma.RST}"
            elif "CHAOS" in d or "MUSCARIA" in d:
                prefix = f"{Prisma.MAG}└─ 🍄 {Prisma.RST}"
                content = f"{Prisma.MAG}{d}{Prisma.RST}"
            elif "GUIDE" in d or "CLARENCE" in d or "ELOISE" in d:
                prefix = f"{Prisma.CYN}└─ 🗣️ {Prisma.RST}"
                content = f"{Prisma.CYN}{d}{Prisma.RST}"
            else:
                prefix = f"{Prisma.GRY}└─{Prisma.RST} "
                content = d

            print(f"  {prefix}{content}")

        # Print the Wisdom Engine's Secret Instruction
        if 'wisdom_protocol' in r:
            print(r['wisdom_protocol'])


