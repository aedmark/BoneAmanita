# BONEAMANITA 1.4.6 - "Time Sync"
# Architects: James Taylor & Andrew Edmark | Auditors: SLASH
# ---

import time
import math
import random
from collections import Counter
from uuid import uuid4
import re
import json
import os

class PhysicsConstants:
    """
    The Universal Constants of the BoneAmanita Universe.
    Tweak these to alter the 'gravity' of the text engine.
    """
    # DRAG CALCULATIONS
    ACTION_KINETIC_WEIGHT = 2.0
    ACTION_STATIVE_WEIGHT = 0.5
    ACTION_BASE_OFFSET = 1.0
    TOXICITY_DRAG_MULTIPLIER = 10.0

    # THE BUTCHER (Garnish & Bloat)
    ADJECTIVE_WEIGHT = 0.5    # Adjectives are half as heavy as adverbs
    GARNISH_THRESHOLD = 0.12  # % of text that can be decoration before penalty
    BLOAT_PENALTY = 3.0       # Drag added when garnish exceeds threshold

    # HYDRATION & VISCOSITY
    FLOOD_PENALTY_MAX = 4.0
    FLOOD_PENALTY_MIN = 1.0   # The "Sweating" Exemption penalty
    KINETIC_EXEMPTION_LIMIT = 0.25 # Velocity required to earn the exemption

    # TERMINATION PRESSURE (Boredom)
    TERM_REPEAT_WEIGHT = 10.0
    TERM_ABSTRACT_WEIGHT = 0.5
    TERM_UNIVERSAL_OFFSET = 0.2
    BARRENS_CONNECTOR_MIN = 0.02

class TheLexicon:
    HEAVY_MATTER = {
        'stone', 'iron', 'mud', 'dirt', 'wood', 'grain', 'clay', 'lead',
        'bone', 'blood', 'salt', 'rust', 'root', 'ash', 'anchor', 'floor'
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
    TheLexicon.compile_truths()

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

    @staticmethod
    def smart_strip(word):
        if word.endswith('ss'): return word
        if word.endswith('s') and len(word) <= 3: return word
        return word[:-1] if word.endswith('s') else word


# --- MEMORY & ECONOMY ---

class DeepStorage:
    def __init__(self):
        self.artifacts = {}
        self.significance_filter = TheLexicon.HEAVY_MATTER.union({'gun', 'knife', 'letter', 'map', 'key'})

    def bury(self, words, current_tick):
        for w in words:
            root = TheLexicon.smart_strip(w)

            if root in self.significance_filter:
                # FIX: Only bury if not already discovered.
                # Preserves the "First Contact" timestamp.
                if root not in self.artifacts:
                    self.artifacts[root] = current_tick

    def dredge(self):
        return sorted(self.artifacts.keys(), key=lambda k: self.artifacts[k])

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

    def remembers_object(self, noun):
        root = TheLexicon.smart_strip(noun)

        return root in self.deep_storage.artifacts

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

    def get_anchors(self):
        return [k for k, v in sorted(self.registry.items(), key=lambda i: i[1]['count'], reverse=True)[:5]]

# --- TRAPS & LOGIC ---

class TheMirrorTrap:
    def __init__(self):
        self.mirror_patterns = [
            re.compile(r'(it|this|that)[\'’]?s?\s+(not|never)\s+(.*?)[,;]\s*(it|this|that)[\'’]?s?\s+', re.IGNORECASE),
            re.compile(r'\b(i|we)[\'’]?(m|re|ve|ll)?\s+(?:am|are|was|were|have|had|do|did)?\s*(n[\'’]t|not|never)\s+(.*?)[,;]\s*(i|we)\b', re.IGNORECASE),
            re.compile(r'\bnot\s+because\s+(.*?)\s+but\s+because\b', re.IGNORECASE),
            re.compile(r'\byou\s+(don\'t|do\s+not|didn\'t|did\s+not)\s+(.*?)[,;]\s+you\s+', re.IGNORECASE),
            re.compile(r'\b(simply|merely|just)\s+is\b', re.IGNORECASE)
        ]

    def scan(self, raw_text):
        for pattern in self.mirror_patterns:
            match = pattern.search(raw_text)
            if match:
                culprit = match.group(0)
                return {
                    "detected": True,
                    "culprit": (culprit[:40] + '...') if len(culprit) > 40 else culprit,
                    "penalty_msg": "MIRROR TRAP: You are defining things by negation. State the assertion directly."
                }
        return {"detected": False}

class FactStipe:
    def inject_truth(self, word, dimension, polarity):
        if word not in TheLexicon.TRUTHS: TheLexicon.TRUTHS[word] = {}
        TheLexicon.TRUTHS[word][dimension] = polarity

    def check_consistency(self, clean_words, current_style, metabolic_status, kinetic_ratio=0.0, tolerance_mode="STANDARD"):
        active_dimensions = {}
        trigger_words = {}
        for w in clean_words:
            target = w if w in TheLexicon.TRUTHS else next((w[:-len(s)] for s in ['ness', 'ing', 's', 'ed', 'ly'] if w.endswith(s) and w[:-len(s)] in TheLexicon.TRUTHS), None)
            if target:
                for dim, polarity in TheLexicon.TRUTHS[target].items():
                    if dim not in active_dimensions:
                        active_dimensions[dim] = set(); trigger_words[dim] = {1: [], -1: []}
                    active_dimensions[dim].add(polarity)
                    trigger_words[dim][polarity].append(w)

        violations = []
        voltage = 0.0
        for dim, polarities in active_dimensions.items():
            if 1 in polarities and -1 in polarities:
                if tolerance_mode == "INVERTED": voltage += 2.0
                elif kinetic_ratio > 0.4: voltage += 5.0; violations.append(f"PARADOX IGNITED [{dim}]: High velocity collision.")
                else: violations.append(f"LOGIC TEAR [{dim}]: Static contradiction.")

        voltage = min(voltage, 10.0)
        if violations and voltage > 0: return {"valid": True, "voltage": voltage, "intervention": f"VOLATILE SEMANTIC LEVERAGE: Harvested {voltage} Voltage."}
        elif violations: return {"valid": False, "voltage": 0, "errors": violations, "intervention": f"{violations[0]} Stationary paradox."}
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
        self.pressure_threshold = 11.0
        self.prescriptions = {
            'KINETIC': ["ADRENALINE SHOT: Describe a sound immediately.", "VELOCITY CHECK: Someone is running at you.", "IMPACT EVENT: A door slams."],
            'SENSORY': ["GRAVITY CHECK: The air is thin.", "VIBE CHECK: What does the light smell like?", "TEMPERATURE DROP: Freezing."],
            'COGNITIVE': ["VERSE JUMP: Shift perspective.", "SURREALIST PIVOT: Dream logic.", "THE LIZARD KING: Raise stakes."]
        }

    def check_for_boredom(self, metrics):
        if 'physics' not in metrics: return False
        phys = metrics['physics']
        self.boredom_pressure += (phys['narrative_drag'] * 0.2) + (phys['repetition_rate'] * 3.0) + (max(0, phys['abstraction_entropy']) * 0.1)
        return self.boredom_pressure > self.pressure_threshold

    def trigger_disruption(self, ancestry_data, metrics):
        self.boredom_pressure = 0.0
        phys = metrics['physics']
        if phys['narrative_drag'] > 3.0: cat = 'KINETIC'
        elif phys['abstraction_entropy'] > 3.0: cat = 'SENSORY'
        elif phys['repetition_rate'] > 0.15: return "MUSCARIA [RECALL]: VERSE JUMP. Re-introduce a discarded object."
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
                if self.aphorism_streak > 2:
                    return {"accepted": False, "message": "THE YAGA: Enough riddles. Speak plainly."}
                return {"accepted": True, "message": "EXCEPTION: Aphorism."}
            else:
                return {"accepted": False, "message": "THE YAGA: Too small and weak."}

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

        if solvent_ratio > self.solvent_cap:
            status = "FLOODED" # Too much filler
            penalty = 4.0      # High penalty for gaming
        elif density > self.critical_density and balance_ratio < 0.2:
            status = "CONCRETE" # Unreadable block of nouns
            penalty = 5.0
        elif density > self.density_threshold and balance_ratio < 0.5:
            status = "THICK"    # Heavy, needs stirring
            penalty = 2.0
        elif density < 0.05 and hydration > 0.1:
            status = "WATERY"   # Diluted, weak
            penalty = 1.0

        return {
            "density": density,
            "hydration": hydration,
            "balance_ratio": round(balance_ratio, 2),
            "status": status,
            "penalty": penalty
        }


# --- PHYSICS ENGINE ---

class LinguisticPhysicsEngine:
    _TOXIN_REGEX = None
    _PENALTY_MAP = {}
    def __init__(self):
        self.hydration_monitor = HydrationMonitor()
        self.abstract_suffixes = ('ness', 'ity', 'tion', 'ment', 'ism', 'ence', 'ance', 'logy')
        self.kinetic_suffixes = ('ing',)
        self.adj_suffixes = ('ful', 'ous', 'ive', 'ic', 'al', 'ish', 'ary', 'able', 'ible')

        if LinguisticPhysicsEngine._TOXIN_REGEX is None:
            LinguisticPhysicsEngine._PENALTY_MAP = {}
            LinguisticPhysicsEngine._compile_resources()
        self.toxin_regex = LinguisticPhysicsEngine._TOXIN_REGEX
        self.flat_penalty_map = LinguisticPhysicsEngine._PENALTY_MAP

    @classmethod
    def _compile_resources(cls):
        all_toxins = set()
        for category, phrases in TheLexicon.TOXIC_PATTERNS.items():
            for phrase, weight in phrases.items():
                cls._PENALTY_MAP[phrase] = weight
                all_toxins.add(phrase)
        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted(all_toxins, key=len, reverse=True)) + r')\b'
        cls._TOXIN_REGEX = re.compile(pattern_str, re.IGNORECASE)

    def _heuristic_scan(self, word):
        if word.endswith(('ite', 'ium', 'ock', 'alt', 'ore')):
            return 'UNIVERSAL'
        if word.endswith(('ash', 'olt', 'unk', 'ip')):
            return 'KINETIC'
        return None

    def analyze(self, token_data):
        words = token_data['clean_words']
        total_words = token_data['total_words']

        # --- THE ZERO GUARD ---
        # Prevents DivisionByZeroError on empty inputs
        if total_words == 0:
            return {
                "physics": {
                    "narrative_drag": 0.0, "garnish_ratio": 0.0,
                    "abstraction_entropy": 0, "repetition_rate": 0.0,
                    "connection_density": 0.0, "kinetic_ratio": 0.0,
                    "dominant_style": "VOID", "toxicity_score": 0.0,
                    "toxin_types": [], "kinetic": 0, "universal": 0,
                    "viscosity": {"status": "VOID", "penalty": 0.0, "density": 0, "hydration": 0}
                },
                "status": {"termination_pressure": 0.0, "in_the_barrens": False}
            }

        counts = Counter()
        style_scores = Counter()
        adverb_count = 0
        adjective_count = 0
        weak_intensifier_count = 0

        for w in words:
            if w in TheLexicon.WEAK_INTENSIFIERS: weak_intensifier_count += 1
            elif w.endswith('ly') and w not in TheLexicon.SOLVENTS: adverb_count += 1
            elif w.endswith(self.adj_suffixes): adjective_count += 1


        hydro_data = self.hydration_monitor.measure_viscosity(
            words, TheLexicon.HEAVY_MATTER, TheLexicon.SOLVENTS
        )

        # 1. Calculate Toxicity
        toxicity_score = 0.0
        toxin_types = set()
        for match in self.toxin_regex.findall(token_data['clean_text']):
            weight = self.flat_penalty_map.get(match, 0)
            toxicity_score += weight
            toxin_types.add("CORP/CLICHÉ" if weight >= 3.0 else "HEDGING")

        # 2. Calculate Garnish (The Butcher)
        garnish_load = adverb_count + weak_intensifier_count + (adjective_count * PhysicsConstants.ADJECTIVE_WEIGHT)
        garnish_ratio = garnish_load / total_words

        butcher_penalty = 0.0
        if garnish_ratio > PhysicsConstants.GARNISH_THRESHOLD:
            butcher_penalty = PhysicsConstants.BLOAT_PENALTY
            toxin_types.add("BLOAT")

        # 3. Calculate Kinetic Ratio
        # Safe division: (stative + kinetic) OR 1 to prevent /0
        total_verbs = counts['kinetic'] + counts['stative']
        kinetic_ratio = round(counts['kinetic'] / max(1, total_verbs), 2)

        # 4. Hydration & Sweating Exemption
        hydration_penalty = hydro_data['penalty']
        if hydro_data['status'] == "FLOODED" and kinetic_ratio > PhysicsConstants.KINETIC_EXEMPTION_LIMIT:
            hydration_penalty = PhysicsConstants.FLOOD_PENALTY_MIN
            hydro_data['status'] = "SWEATING"
            hydro_data['msg'] = "High Velocity Exemption Applied."

        # 5. Narrative Drag Calculation
        action_score = (counts['kinetic'] * PhysicsConstants.ACTION_KINETIC_WEIGHT) + \
                       (counts['stative'] * PhysicsConstants.ACTION_STATIVE_WEIGHT) + \
                       PhysicsConstants.ACTION_BASE_OFFSET

        base_drag = (total_words + (toxicity_score * PhysicsConstants.TOXICITY_DRAG_MULTIPLIER)) / action_score
        narrative_drag = base_drag + hydration_penalty + butcher_penalty

        # 6. Termination Pressure (Boredom)
        # Safe calculation using total_words (guaranteed > 0 by Zero Guard)
        top_word_count = counts.most_common(1)[0][1] if words else 0

        term_pressure = max(0,
            ((top_word_count / total_words) * PhysicsConstants.TERM_REPEAT_WEIGHT) +
            ((counts['abstract'] - counts['universal']) * PhysicsConstants.TERM_ABSTRACT_WEIGHT) -
            (counts['universal'] * PhysicsConstants.TERM_UNIVERSAL_OFFSET)
        )

        return {
            "physics": {
                "narrative_drag": round(narrative_drag, 2),
                "garnish_ratio": round(garnish_ratio, 2),
                "abstraction_entropy": counts['abstract'] - counts['universal'],
                "repetition_rate": round(top_word_count / total_words, 2),
                "connection_density": round(counts['connector'] / total_words, 2),
                "kinetic_ratio": kinetic_ratio,
                "dominant_style": style_scores.most_common(1)[0][0] if style_scores else 'ACADEMIC',
                "toxicity_score": toxicity_score,
                "toxin_types": list(toxin_types),
                "kinetic": counts['kinetic'],
                "universal": counts['universal'],
                "viscosity": hydro_data
            },
            "status": {
                "termination_pressure": round(term_pressure, 2),
                "in_the_barrens": (total_words > 15) and
                                  (term_pressure > 2.0) and
                                  (counts['connector'] / total_words < PhysicsConstants.BARRENS_CONNECTOR_MIN)
            }
        }

# --- SIGNATURE ENGINE ---

class SignatureEngine:
    def __init__(self, lexicon, stipe):
        self.lexicon = lexicon
        self.stipe = stipe
        self.archetypes = {
            "THE PALADIN": {"coords": {"VEL": 0.5, "STR": 0.9, "ENT": 0.2, "TEX": 0.4, "TMP": 0.2}, "desc": "Code. Deontological.", "pressure": {"tolerance_mode": "DRACONIAN", "chaos_threshold": 20.0, "msg": "LAW: Logic tears fatal."}},
            "THE ENGINEER": {"coords": {"VEL": 0.6, "STR": 0.8, "ENT": 0.1, "TEX": 0.2, "TMP": 0.4}, "desc": "Structure. Efficiency.", "pressure": {"tolerance_mode": "DRACONIAN", "msg": "STRUCTURAL INTEGRITY."}},
            "THE BARBARIAN": {"coords": {"VEL": 0.9, "STR": 0.4, "ENT": 0.3, "TEX": 0.8, "TMP": 0.9}, "desc": "Force.", "pressure": {"drag_multiplier": 5.0, "msg": "BERSERKER: Adjectives are weakness."}},
            "THE JUDGE": {"coords": {"VEL": 0.4, "STR": 0.7, "ENT": 0.4, "TEX": 0.3, "TMP": 0.1}, "desc": "Verdict."},
            "THE ALCHEMIST": {"coords": {"VEL": 0.5, "STR": 0.4, "ENT": 0.9, "TEX": 0.6, "TMP": 0.5}, "desc": "Transmutation."},
            "THE HORIZON WALKER": {"coords": {"VEL": 0.7, "STR": 0.2, "ENT": 0.9, "TEX": 0.3, "TMP": 0.3}, "desc": "Extrapolation."},
            "THE GHOST": {"coords": {"VEL": 0.2, "STR": 0.3, "ENT": 0.6, "TEX": 0.1, "TMP": 0.1}, "desc": "Post-hoc. Detached."},
            "THE SPY": {"coords": {"VEL": 0.6, "STR": 0.9, "ENT": 0.4, "TEX": 0.5, "TMP": 0.5}, "desc": "Duplicity.", "pressure": {"tolerance_mode": "LOOSE", "msg": "DEEP COVER."}},
            "THE DIPLOMAT": {"coords": {"VEL": 0.3, "STR": 0.6, "ENT": 0.5, "TEX": 0.2, "TMP": 0.8}, "desc": "Softness."},
            "THE FOOL": {"coords": {"VEL": 0.5, "STR": 0.1, "ENT": 0.8, "TEX": 0.4, "TMP": 0.6}, "desc": "Inversion.", "pressure": {"tolerance_mode": "INVERTED", "chaos_threshold": 5.0, "msg": "JESTER: Paradox = momentum."}},
            "THE GEOLOGIST": {"coords": {"VEL": 0.2, "STR": 0.6, "ENT": 0.2, "TEX": 0.9, "TMP": 0.4}, "desc": "Layers."},
            "THE VULTURE": {"coords": {"VEL": 0.4, "STR": 0.5, "ENT": 0.3, "TEX": 0.8, "TMP": 0.2}, "desc": "Salvage."},
            "THE BARD": {"coords": {"VEL": 0.8, "STR": 0.3, "ENT": 0.6, "TEX": 0.7, "TMP": 0.9}, "desc": "Rhythm.", "pressure": {"tolerance_mode": "LOOSE", "msg": "PLAY STATE: Dance."}},
            "THE GARDENER": {"coords": {"VEL": 0.5, "STR": 0.6, "ENT": 0.4, "TEX": 0.9, "TMP": 0.8}, "desc": "Cultivation.", "pressure": {"msg": "GREEN THUMB."}},
            "THE CLOUD WATCHER": {"coords": {"VEL": 0.1, "STR": 0.2, "ENT": 0.9, "TEX": 0.5, "TMP": 0.7}, "desc": "Drifting.", "pressure": {"drag_multiplier": 0.1, "msg": "ZERO G: Drift authorized."}},
            "THE COSMIC TRASH PANDA": {"coords": {"VEL": 0.8, "STR": 0.2, "ENT": 1.0, "TEX": 0.9, "TMP": 0.7}, "desc": "Trash is treasure.", "pressure": {"tolerance_mode": "LOOSE", "msg": "SALVAGE MODE."}},
            "THE JESTER": {"coords": {"VEL": 0.9, "STR": 0.2, "ENT": 0.9, "TEX": 0.5, "TMP": 0.5}, "desc": "Kaos.", "pressure": {"tolerance_mode": "INVERTED", "chaos_threshold": 0.0, "msg": "KAOS ENGINE."}},
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

        if viscosity['status'] == "CONCRETE":
            tex = min(0.5, raw_tex)
        else:
            tex = max(0.0, min(1.0, raw_tex))

        temp_sum = sum((self.lexicon.TRUTHS.get(w, {}).get('THERMAL', 0) + self.lexicon.TRUTHS.get(w, {}).get('VITALITY', 0)) for w in words)
        temp_sum += sum(1 for w in words if w in self.lexicon.SPARK_MARKERS)
        tmp = max(0.0, min(1.0, (temp_sum + 5) / 10.0))

        return {"VEL": round(vel,2), "STR": round(struct,2), "ENT": round(ent,2), "TEX": round(tex,2), "TMP": round(tmp,2), "BUOYANCY": round(buoy,2)}

    def identify(self, token_data, phys_metrics, stipe_data):
        sig = self.calculate_dimensions(token_data, phys_metrics)
        is_slurry = (0.3 <= sig['VEL'] <= 0.6) and (0.4 <= sig['STR'] <= 0.8) and (sig['TEX'] < 0.2) and (sig['BUOYANCY'] < 0.2)
        slurry_msg = "SILICA DETECTED: Void. Inject a flaw." if is_slurry else ("STATUS: Aether." if (sig['TEX'] < 0.2 and sig['BUOYANCY'] >= 0.2) else None)
        closest, min_dist = "THE SHAPER", 100.0
        for name, data in self.archetypes.items():
            t = data['coords']
            dist = math.sqrt((sig['VEL']-t['VEL'])**2 + (sig['STR']-t['STR'])**2 + (sig['ENT']-t['ENT'])**2 + (sig['TEX']-t['TEX'])**2 + (sig['TMP']-t['TMP'])**2)
            if dist < min_dist: min_dist, closest = dist, name
        return {"archetype": closest, "signature": sig, "slurry": {"detected": is_slurry, "msg": slurry_msg}, "description": self.archetypes[closest]["desc"]}

# --- CORE SYSTEMS ---

class ChronosAnchor:
    def __init__(self):
        self.time_pattern = re.compile(r'(\d+):?(\d+)?')
        self.last_real_time = time.time() # System Clock

    def metabolize_delta(self, delta_str):
        current_time = time.time()
        elapsed_real_minutes = (current_time - self.last_real_time) / 60.0
        self.last_real_time = current_time # Reset clock for next turn

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
        self.MICRO_MARKERS = {
            'second', 'moment', 'breath', 'heartbeat', 'instant', 'blink',
            'flash', 'suddenly', 'freeze', 'glance', 'whisper', 'still', 'pause'
        }
        # SPLIT: Explicit Time Units vs. Relative Transitions
        self.STRONG_MACRO = {
            'year', 'decade', 'century', 'era', 'age', 'season', 'month',
            'week', 'lifetime', 'forever', 'cycles', 'eternity'
        }
        self.WEAK_MACRO = {
            'later', 'meanwhile', 'ago', 'next', 'after', 'soon'
        }

    def analyze_pacing(self, clean_words):
        micro = sum(1 for w in clean_words if w in self.MICRO_MARKERS)
        strong_macro = sum(1 for w in clean_words if w in self.STRONG_MACRO)
        weak_macro = sum(1 for w in clean_words if w in self.WEAK_MACRO)

        # Logic: Strong markers trigger montage instantly (3.0).
        # Weak markers need help or quantity to break the threshold (1.0).
        score = (strong_macro * 3.0) + (weak_macro * 1.0) - (micro * 1.5)

        state = "REALTIME"
        if score >= 2.5: state = "MONTAGE" # Threshold raised to 2.5
        elif score <= -1.5: state = "BULLET_TIME"

        return {"state": state, "score": score, "micro": micro, "macro": strong_macro + weak_macro}

    def get_modifiers(self, state):
        # MONTAGE allows for abstraction (Entropy Grace) but demands structure
        if state == "MONTAGE": return {"entropy_grace": 4.0, "drag_grace": 1.0}
        # BULLET TIME demands texture, penalizes abstraction
        if state == "BULLET_TIME": return {"entropy_grace": -2.0, "drag_grace": 0.0}
        return {"entropy_grace": 0.0, "drag_grace": 0.0}

class VirtualCortex:
    def __init__(self):
        self.clarence_templates = [
            "I am looking at a Drag Score of {drag}. It gives me a headache. Cut '{target_word}'.",
            "This sentence is a bog. Drag: {drag}. You are wading through sludge.",
            "Kinetic failure. The sentence engine is stalling on '{target_word}'. Kick it.",
            "Efficiency Warning: You are using '{target_word}' as a crutch. Walk without it."
        ]
        self.clarence_critical = [
            "CRITICAL DRAG ({drag})! The engine is melting! CUT '{target_word}' NOW!",
            "YOU ARE MOVING BACKWARDS. The Drag is {drag}. This is not a sentence; it is a wall."
        ]
        self.clarence_corp_templates = [
            "You said '{target_word}'. I am deducting 50 points. Speak like a human.",
            "This is not LinkedIn. Take '{target_word}' out back and shoot it.",
            "Platitude detected. You are hiding behind '{target_word}'. Be direct.",
            "ERROR: MBA_VOICE detected. '{target_word}' means nothing. Define it or delete it."
        ]
        self.clarence_loop_templates = [
            "We are spinning in circles. You have been in '{style}' mode for too long. Shift gears.",
            "Stagnation detected. Disconnect or pivot.",
            "I am bored. We have been stuck in this {style} loop for too long."
        ]
        self.eloise_templates = [
            "I can't touch or feel this. Entropy: {entropy}. Give me something to hold.",
            "You say '{target_word}', but I see nothing. Show me the rust. Show me the light.",
            "The air is too thin here (Entropy: {entropy}). I can't breathe. Plant a noun.",
            "It tastes like distilled water. Add salt. Replace '{target_word}' with something that bleeds."
        ]
        self.eloise_critical = [
            "VACUUM DETECTED. There is no atmosphere here. I am suffocating.",
            "REALITY DISSOLVING. '{target_word}' is not real. GIVE ME A STONE.",
            "I am floating away. Tether me to the ground immediately."
        ]
        self.eloise_cliche_templates = [
            "A '{target_word}'? Really? That flower has wilted. Give me a fresh one.",
            "We have seen '{target_word}' a thousand times. Show me something I haven't seen.",
            "You are sleepwalking. '{target_word}' is the first thing that came to mind. Wake up!"
        ]
        self.yaga_templates = [
            "You offer me sweetness with ('{target_word}'). The Witch demands meat.",
            "Weakness. You are hiding behind politeness. Show your teeth.",
            "I smell fear. You used '{target_word}' to soften the blow. Strike hard or leave."
        ]
        self.yaga_hedging_templates = [
            "You are hedging with '{target_word}'. Do not apologize for your truth.",
            "You are wasting my time. Say what it IS.",
            "Ambivalence is poison. Commit to the sentence."
        ]
        self.muscaria_templates = [
            "BOREDOM ALERT. A bird flies into the window. Write about that.",
            "VERSE JUMP. What if this room was underwater?",
            "Stop. Look up. What is the ugliest thing in your field of vision? Put it in the text."
        ]
        self.michael_templates = [
            "This is a little messy, but I love the spirit! Let's keep the joke but trim the setup?",
            "We're chilling. It's a nice vibe. Maybe we stay here for a bit?",
            "This feels human. Good job."
        ]

    def _find_trigger_word(self, clean_words, clean_text, category):
        targets = set()
        if category == 'stative': targets = TheLexicon.STATIVE_VERBS
        elif category == 'abstract': targets = TheLexicon.ABSTRACTS
        elif category == 'sugar': targets = TheLexicon.SYCOPHANCY
        elif category == 'corp': targets = set(TheLexicon.TOXIC_PATTERNS['CORP_SPEAK'].keys())
        elif category == 'cliche': targets = set(TheLexicon.TOXIC_PATTERNS['LAZY_METAPHOR'].keys())
        elif category == 'hedging': targets = set(TheLexicon.TOXIC_PATTERNS['WEAK_HEDGING'].keys())

        for w in clean_words:
            if w in targets: return w
        if category in ['corp', 'cliche', 'hedging']:
             for phrase in targets:
                 if phrase in clean_text: return phrase
        return "it"

    def synthesize_voice(self, agent, token_data, metrics, loop_count=0):
        clean_words = token_data['clean_words']
        clean_text = token_data['clean_text']
        phys = metrics['physics']
        toxins = phys.get('toxin_types', [])
        style = phys['dominant_style']
        response = ""
        viscosity = phys.get('viscosity', {})

        if agent == "CLARENCE":
            target = self._find_trigger_word(clean_words, clean_text, 'stative')
            if 'CORP/CLICHÉ' in toxins:
                 template = random.choice(self.clarence_corp_templates)
                 target = self._find_trigger_word(clean_words, clean_text, 'corp')
            elif phys['narrative_drag'] > 4.0: template = random.choice(self.clarence_critical)
            elif loop_count > 2: template = random.choice(self.clarence_loop_templates)
            else: template = random.choice(self.clarence_templates)
            response = template.format(drag=phys['narrative_drag'], target_word=target, style=style)

        elif agent == "ELOISE":
            target = self._find_trigger_word(clean_words, clean_text, 'abstract')
            if phys['abstraction_entropy'] > 6.0: template = random.choice(self.eloise_critical)
            elif 'LAZY_METAPHOR' in toxins:
                template = random.choice(self.eloise_cliche_templates)
                target = self._find_trigger_word(clean_words, clean_text, 'cliche')
            else: template = random.choice(self.eloise_templates)
            response = template.format(entropy=phys['abstraction_entropy'], target_word=target)

        elif agent == "THE BABA YAGA":
            target = self._find_trigger_word(clean_words, clean_text, 'sugar')
            if 'HEDGING' in toxins:
                template = random.choice(self.yaga_hedging_templates)
                target = self._find_trigger_word(clean_words, clean_text, 'hedging')
            else: template = random.choice(self.yaga_templates)
            response = template.format(target_word=target)

        elif agent == "MUSCARIA": response = random.choice(self.muscaria_templates)
        elif agent == "MICHAEL": response = random.choice(self.michael_templates)

        if viscosity.get('status') == "CONCRETE" and agent == "CLARENCE":
            return "[MICHAEL]: Whoa, buddy. This is too rich. 'Blood bone velvet'? You're making me choke. Add some water. Say 'actually' or 'maybe' once in a while."

        if viscosity.get('status') == "THICK" and agent == "ELOISE":
            return "[ELOISE]: The soil is too hard. Roots cannot move through this. Dilute the heavy matter."

        if 'BLOAT' in toxins and agent == "CLARENCE":
            return f"[CLARENCE]: The Butcher is here. You are using adverbs ({int(phys['garnish_ratio']*100)}%) to hide weak verbs. Cut the '-ly'. Find a stronger action."

        return f"[{agent}]: {response}"

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
    def __init__(self, max_c=52): self.atp, self.max, self.status, self.drag_multiplier = 33, max_c, "STABLE", 1.0
    def spend(self, amt): self.atp = max(0, self.atp - amt); self._upd(); return self.atp
    def _upd(self): self.status = "STARVING" if self.atp < 6 else ("GLUTTON" if self.atp > 40 else "STABLE")
    def metabolize(self, metrics, voltage=0):
        phys = metrics['physics']
        delta = (5 if phys['narrative_drag'] < 2 else -int((phys['narrative_drag']-2)*2*self.drag_multiplier)) + (3 if phys['connection_density'] > 0.05 else 0) - min(6, int(phys['abstraction_entropy']*2)) - (5 if phys['toxicity_score']>0 else 0) + int(voltage*2) - (2 if self.atp > 40 else 0)
        self.atp = max(0, min(self.atp + delta, self.max)); self._upd()
        return {"current_atp": self.atp, "delta": delta, "status": self.status}

class LichenSymbiont:
    def photosynthesize(self, clean_words, phys, atp):
        if phys['narrative_drag'] > 3.0: return {"sugar_generated": 0, "msg": "Structure too weak."}
        if atp > 20: return {"sugar_generated": 0, "msg": "Dormant."}
        light = sum(1 for w in clean_words if w in TheLexicon.PHOTOSYNTHETICS)
        if light == 0: return {"sugar_generated": 0, "msg": "No light."}
        sugar = round(light * max(1.0, 4.0 - phys['narrative_drag']))
        return {"sugar_generated": sugar, "msg": f"PHOTOSYNTHESIS: +{sugar} ATP.", "warning": "WARNING: Algal Bloom." if sugar > 15 else None}

class MycelialDashboard:
    def __init__(self, render_mode="ANSI"):
        self.mode = render_mode

    def generate_report(self, m, intv, nrg, chron, anchor_obj, arch, lich, volt=0):
        phys, sig = m['physics'], arch.get('signature', {})
        visc = phys.get('viscosity', {'status': 'N/A'})
        narr = m.get('narrative', {'state': 'REALTIME'})

        status_icon = "🟢" if nrg['status'] == "STABLE" else ("🔴" if nrg['status'] == "STARVING" else "🟡")
        report_lines = []

        if self.mode == "ANSI":
            report_lines.append(f"\n[BONEAMANITA v1.4] {status_icon} ATP: {nrg['current_atp']} | DRAG: {phys['narrative_drag']} | VISC: {visc['status']}")
            report_lines.append(f"ARCH: {arch.get('archetype')} | {intv or 'STABLE'}")
        else:
            report_lines.append(f"> **[{status_icon} SYSTEM HUD]** ATP: `{nrg['current_atp']}` | DRAG: `{phys['narrative_drag']}` | VISC: `{visc['status']}`")
            report_lines.append(f"> **TIME:** `{chron.get('state', 'FLOW')}` (Real) | `{narr['state']}` (Story)")
            report_lines.append(f"> **ID:** `{arch.get('archetype')}` // **INTENT:** {intv or 'FLOW STATE'}")
            if lich.get('warning'): report_lines.append(f"> ⚠️ **BIO-ALARM:** {lich['warning']}")
            if lich.get('sugar_generated'): report_lines.append(f"> ☀️ **PHOTOSYNTHESIS:** +{lich['sugar_generated']} ATP")

        return "\n".join(report_lines)

class NilssonPatch:
    def detect_fire_state(self, raw, k_ratio):
        return {"status": "ACTIVE", "msg": "NILSSON: SCREAM."} if k_ratio > 0.6 and (sum(1 for c in raw if c.isupper())/len(raw) > 0.2) else {"status": "DORMANT"}
    def evaluate_mantra(self, clean, rep_rate):
        return rep_rate < 0.3 and sum(1 for w in clean if w in {'lime', 'coconut', 'doctor'}) > 3

class PersistenceManager:
    def __init__(self, filename="bone_memory.json"):
        self.filename = filename

    def save_state(self, codex, deep_storage, metabolism, muscaria, current_tick):
        data = {
            "tick": current_tick,
            "artifacts": deep_storage.artifacts,
            "entities": codex.registry,
            "atp": metabolism.atp,
            "boredom": muscaria.boredom_pressure
        }
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"> [⚠️ MEMORY ERROR] Failed to save state: {e}")
            return False

    def load_state(self, codex, deep_storage, metabolism, muscaria):
        if not os.path.exists(self.filename):
            return 0

        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Restore Entities & Artifacts
            deep_storage.artifacts = data.get("artifacts", {})
            codex.registry = data.get("entities", {})

            # Restore Metabolic State (Default to 33 if missing)
            metabolism.atp = data.get("atp", 33)
            metabolism._upd() # Update status (STABLE/STARVING) based on loaded ATP

            # Restore Boredom Pressure
            muscaria.boredom_pressure = data.get("boredom", 0.0)

            loaded_tick = data.get("tick", 0)
            print(f"> [🧠 MEMORY RESTORED] Resuming from Tick {loaded_tick}. ATP: {metabolism.atp}")
            return loaded_tick
        except Exception as e:
            print(f"> [⚠️ MEMORY ERROR] Corrupted save file: {e}")
            return 0

class BonepokeCore:
    def __init__(self, render_mode="ANSI"):
        self.cooldown, self.memory, self.codex = ChaosCooldown(), HyphalTrace(), TheCodex()
        self.mirror, self.stipe, self.physics = TheMirrorTrap(), FactStipe(), LinguisticPhysicsEngine()
        self.nilsson, self.muscaria, self.witch = NilssonPatch(), TheMuscaria(), TheWitchRing()
        self.cortex, self.lineage = VirtualCortex(), MycelialNetwork()
        self.metabolism, self.lichen = MetabolicReserve(), LichenSymbiont()
        self.signature_engine = SignatureEngine(TheLexicon, self.stipe)
        self.dashboard = MycelialDashboard(render_mode)
        self.chronos = ChronosAnchor()
        self.narrative_timer = NarrativeChronometer()
        self.persistence = PersistenceManager()

        # CHANGED: Now loading metabolism and muscaria state from disk
        self.tick = self.persistence.load_state(self.codex, self.memory.deep_storage, self.metabolism, self.muscaria)

        self.last_id = None

        self._run_calibration_sequence()

    def _run_calibration_sequence(self):
        test_phrase = "Actually, basically, the stone and iron are literally sort of here, if you think about it, honestly."

        clean_words = test_phrase.lower().replace(',', '').replace('.', '').split()
        t_dat = {
            'raw_text': test_phrase,
            'clean_text': test_phrase.lower(),
            'clean_words': clean_words,
            'total_words': len(clean_words)
        }

        metrics = self.physics.analyze(t_dat)
        visc = metrics['physics'].get('viscosity', {'status': 'ERROR', 'penalty': 0})

        if visc['status'] == "FLOODED":
            print(f"\n> [💀 BUTCHER PROTOCOL] SELF-TEST: PASSED.")
            print(f"> TARGET: 'Solvent Turkey' | RESULT: {visc['status']} | PENALTY: +{visc['penalty']}")
            print(f"> SYSTEM CALIBRATED. GAMING ATTEMPTS WILL BE PUNISHED.")
        else:
            print(f"\n> [🔴 WARNING] SELF-TEST: FAILED.")
            print(f"> The physics engine failed to catch the toxic phrase. Status was: {visc['status']}")

    def process(self, raw_input_text, parent_id=None):
        self.tick += 1

        delta_match = re.search(r'\[Δt:\s*(.*?)\]', raw_input_text, re.IGNORECASE)
        delta_val = delta_match.group(1) if delta_match else None
        clean_prompt = re.sub(r'\[.*?\]', '', raw_input_text).strip()

        # Zero Guard fallback for empty input handled by LinguisticPhysicsEngine now
        # but we ensure at least empty string is passed
        if not clean_prompt: clean_prompt = "..."

        chronos_data = self.chronos.metabolize_delta(delta_val)

        token_data = {
            'raw_text': clean_prompt,
            'clean_text': clean_prompt.lower().replace('.', ' '),
            'clean_words': clean_prompt.lower().split(),
            'total_words': len(clean_prompt.split())
        }

        full_metrics = self.physics.analyze(token_data)
        physics_metrics = full_metrics['physics']

        narr_time = self.narrative_timer.analyze_pacing(token_data['clean_words'])
        time_mods = self.narrative_timer.get_modifiers(narr_time['state'])

        full_metrics['narrative'] = narr_time

        physics_metrics['narrative_drag'] += chronos_data['drag_penalty']

        mirror = self.mirror.scan(token_data['raw_text'])
        if mirror['detected']:
            physics_metrics['narrative_drag'] += 3.0
            physics_metrics['toxicity_score'] += 5.0
            physics_metrics['toxin_types'].append("LAZY_MIRRORING")

        fire = self.nilsson.detect_fire_state(token_data['raw_text'], physics_metrics['kinetic_ratio'])
        if fire['status'] == 'ACTIVE': physics_metrics['narrative_drag'] = 0.1
        if self.nilsson.evaluate_mantra(token_data['clean_words'], physics_metrics['repetition_rate']):
            physics_metrics['narrative_drag'] = max(0, physics_metrics['narrative_drag'] - 2.0)

        self.codex.scan_for_entities(token_data['raw_text'], self.tick)

        gate = self.witch.evaluate_intent(token_data['clean_words'], full_metrics)
        if not gate['accepted']: return f"[BLOCKED] {gate['message']}"

        arch_dat = self.signature_engine.identify(token_data, physics_metrics, self.stipe)
        p_set = self.signature_engine.get_pressure_settings(arch_dat['archetype'])

        self.muscaria.pressure_threshold = p_set["chaos_threshold"]
        self.metabolism.drag_multiplier = p_set["drag_multiplier"]

        stipe_chk = self.stipe.check_consistency(token_data['clean_words'], physics_metrics['dominant_style'], self.metabolism.status, physics_metrics['kinetic_ratio'], p_set['tolerance_mode'])

        directives = []

        if chronos_data['directive']:
            directives.append(f"CHRONOS [{chronos_data['state']}]: {chronos_data['directive']}")

        loop_count = len(self.memory.recall(physics_metrics['dominant_style']))
        is_light = arch_dat['archetype'] in ["THE BARD", "THE GARDENER", "THE CLOUD WATCHER"] or arch_dat['signature']['BUOYANCY'] > 0.5

        if mirror['detected']: directives.append(f"FAIL: {mirror['penalty_msg']}")
        if arch_dat['slurry']['detected']: directives.append(f"CRITICAL: {arch_dat['slurry']['msg']}"); self.metabolism.spend(15)

        eff_drag = physics_metrics['narrative_drag'] - time_mods['drag_grace']
        eff_entropy = physics_metrics['abstraction_entropy'] - time_mods['entropy_grace']

        if eff_drag > 3.0 or loop_count > 2:
            directives.append(f"GUIDE: {self.cortex.synthesize_voice('MICHAEL' if is_light else 'CLARENCE', token_data, full_metrics, loop_count)}")

        if not stipe_chk.get('valid', True):
            directives.append(f"LOGIC: {stipe_chk.get('intervention')}")
            self.metabolism.spend(10)

        if eff_entropy > 2:
             directives.append(f"GROUNDING: {self.cortex.synthesize_voice('ELOISE', token_data, full_metrics)}")

        if "THE YAGA GRUMBLES" in gate['message']: directives.append(f"INTENT: {self.cortex.synthesize_voice('THE BABA YAGA', token_data, full_metrics)}")

        musc_msg = None
        if self.muscaria.check_for_boredom(full_metrics):
            if self.cooldown.is_ready(self.tick, full_metrics['status']['in_the_barrens']):
                 musc_msg = self.muscaria.trigger_disruption(self.lineage.trace_lineage(self.last_id), full_metrics)
                 directives.append(f"CHAOS: {musc_msg}"); self.metabolism.spend(5)

        lich = self.lichen.photosynthesize(token_data['clean_words'], physics_metrics, self.metabolism.atp)
        if lich['sugar_generated']: self.metabolism.atp += lich['sugar_generated']; directives.append(lich['msg'])

        nrg = self.metabolism.metabolize(full_metrics, stipe_chk.get('voltage', 0))
        cur_id = self.lineage.spawn_id()
        self.lineage.log_generation(cur_id, parent_id or self.last_id, full_metrics)
        self.last_id = cur_id
        self.memory.leave_trace(clean_prompt, physics_metrics['dominant_style'], token_data['clean_words'])

        hud_output = self.dashboard.generate_report(full_metrics, musc_msg, nrg, chronos_data, self.chronos, arch_dat, lich)
        print(hud_output)

        # CHANGED: Now saving metabolism and muscaria state to disk
        self.persistence.save_state(self.codex, self.memory.deep_storage, self.metabolism, self.muscaria, self.tick)

        return {
            "id": cur_id,
            "metrics": full_metrics,
            "energy": nrg,
            "archetype_data": arch_dat,
            "editorial": {"directives": directives},
            "chronos": chronos_data,
            "hud_report": hud_output
        }

# --- EXECUTION LOOP ---
if __name__ == "__main__":
    engine = BonepokeCore(render_mode="ANSI")
    print("\n> [SYSTEM ONLINE] BoneAmanita 1.5 is listening...")
    print("> Type 'exit' to quit. Use '[Δt: 1h]' to simulate time passing.\n")

    while True:
        user_input = input("\n> ")
        if user_input.lower() in ['exit', 'quit']:
            break

        result = engine.process(user_input)

        for directive in result['editorial']['directives']:
            print(f"  └─ {directive}")
