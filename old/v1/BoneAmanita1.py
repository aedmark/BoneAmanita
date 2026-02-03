# ---------------------------------------------------------------------------
# BONEAMANITA 1.0 - "The Black Mirror"
# Architects: James Taylor & Andrew Edmark | Auditors: SLASH
# ---------------------------------------------------------------------------

import time
import math
import random
from collections import Counter
from uuid import uuid4
import re

class TheLexicon:
    """
    THE PANTRY
    Now includes Aerobic Matter and Whimsy.
    """
    # PHYSICS MATTER (Combined Heavy & Light)
    # Note: 'Universal' still means "Concrete/Touchable", but we now track weight.
    HEAVY_MATTER = {
        'stone', 'iron', 'mud', 'dirt', 'wood', 'grain', 'clay', 'lead',
        'bone', 'blood', 'salt', 'rust', 'root', 'ash', 'anchor', 'floor'
    }
    AEROBIC_MATTER = {
        'balloon', 'feather', 'cloud', 'bubble', 'steam', 'breeze', 'wing',
        'petal', 'foam', 'spark', 'kite', 'dust', 'light', 'ray', 'sky'
    }
    # The Physics Engine reads this union:
    UNIVERSALS = HEAVY_MATTER.union(AEROBIC_MATTER).union({
        'hand', 'eye', 'breath', 'skin', 'voice', "air", "cloth",
        'water', 'rain', 'glass', 'fabric', 'door', 'key', 'roof'
    })

    ABSTRACTS = {
        'system', 'protocol', 'sequence', 'vector', 'node', 'context',
        'layer', 'matrix', 'perspective', 'framework', 'logic', 'concept',
        'theory', 'analysis', 'solution', 'optimization', 'utilization'
    }

    # ACTION & PLAY
    KINETIC_VERBS = {
        'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'cut',
        'drive', 'lift', 'carry', 'strike', 'burn', 'shatter'
    }
    PLAY_VERBS = {
        'bounce', 'dance', 'twirl', 'float', 'wobble', 'tickle', 'jiggle',
        'soar', 'wander', 'wonder', 'riff', 'jam', 'play', 'skip', 'hop'
    }
    # Union for detection
    ALL_VERBS = KINETIC_VERBS.union(PLAY_VERBS)

    # FLAVOR & STYLE
    # "Spark" words trigger the Serotonin Index
    SPARK_MARKERS = {
        'lovely', 'strange', 'curious', 'funny', 'wild', 'soft', 'glow',
        'warm', 'kind', 'fresh', 'sweet', 'hello', 'yes', 'maybe'
    }

    # 4. TRUTH MANIFOLD (Updated for Temperature)
    TRUTHS = {
        'sun': {'LUMENS': 1, 'THERMAL': 1},
        'night': {'LUMENS': -1, 'THERMAL': -1},
        'fire': {'THERMAL': 1, 'VITALITY': 1},
        'ice': {'THERMAL': -1, 'VITALITY': -1},
        'laugh': {'VITALITY': 1, 'THERMAL': 1}, # New
        'smile': {'VITALITY': 1, 'THERMAL': 1}, # New
        'song': {'VITALITY': 1},                 # New
        'dead': {'VITALITY': -1, 'THERMAL': -1}
    }

    # FOR LICHEN SYMBIONT
    PHOTOSYNTHETICS = {
        'light', 'sun', 'ray', 'beam', 'glow', 'shine', 'spark', 'fire',
        'flame', 'star', 'day', 'dawn', 'noon', 'gold', 'bright', 'glimmer'
    }

    # FOR WITCH RING
    SYCOPHANCY = {
        'just', 'actually', 'kind of', 'sort of', 'little', 'try', 'maybe',
        'perhaps', 'hopefully', 'possibly', 'basically', 'honestly'
    }

    # FOR PHYSICS ENGINE & CORTEX
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

        # "Zombies" allow high toxicity scoring to trigger immediate intervention.
        'ZOMBIE_PHRASES': {
            'ghost in the machine': 10.0,
            'rubber meets the road': 10.0,
            'not a bug but a feature': 9.0,
            'double-edged sword': 8.0,
            'best of both worlds': 8.0,
            'step in the right direction': 8.0,
            'level playing field': 8.0
        },
        'WEAK_HEDGING': {
            'i think that': 2.0, 'it seems like': 2.0, 'in my opinion': 2.0
        }
    }

    # FOR PHYSICS CLASSIFICATION
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

# --- MEMORY & ECONOMY -----------------------------------------

class HyphalTrace:
    def __init__(self, retention_span=10):
        self.hyphae_stream = []
        self.retention_span = retention_span
        self.current_tick = 0

    def leave_trace(self, content, context_tag):
        self.current_tick += 1
        hyphae_packet = {
            "content": content,
            "context_tag": context_tag,
            "timestamp": self.current_tick
        }
        self.hyphae_stream.append(hyphae_packet)
        self._prune_old_memories()

    def recall(self, target_context):
        relevant_memories = []
        for mem in self.hyphae_stream:
            is_recent = (self.current_tick - mem['timestamp']) < 3
            is_relevant = (mem['context_tag'] == target_context)
            if is_recent or is_relevant:
                relevant_memories.append(mem['content'])
        return relevant_memories

    def _prune_old_memories(self):
        if len(self.hyphae_stream) > self.retention_span:
            self.hyphae_stream.pop(0)

class TheCodex:
    def __init__(self):
        self.registry = {}
        self.ignore_list = {
            'The', 'A', 'An', 'It', 'He', 'She', 'They', 'We', 'I', 'You',
            'This', 'That', 'But', 'And', 'Or', 'If', 'When', 'Then',
            'System', 'Analysis', 'Metrics', 'Drag', 'Entropy', 'For', 'In', 'To', 'Of'
        }
        self._entity_pattern = re.compile(r'\b[A-Z][a-z]+\b')

    def scan_for_entities(self, raw_text, current_tick):
        for match in self._entity_pattern.finditer(raw_text):
            word = match.group()
            start_index = match.start()
            is_start_of_sentence = False
            if start_index > 0:
                preceding_chars = raw_text[max(0, start_index-4):start_index]
                if any(p in preceding_chars for p in ['.', '!', '?', '\n']):
                    is_start_of_sentence = True
            if start_index == 0: is_start_of_sentence = True
            if is_start_of_sentence: continue
            if word in self.ignore_list: continue
            if len(word) < 3: continue

            if word not in self.registry:
                self.registry[word] = {'count': 0, 'first_seen_tick': current_tick}
            self.registry[word]['count'] += 1

    def get_anchors(self):
        sorted_entities = sorted(
            self.registry.items(),
            key=lambda item: item[1]['count'],
            reverse=True
        )
        return [k for k, v in sorted_entities[:5]]

# --- THE MIRROR TRAP (SYNTACTIC PARALLELISM) ----------------

class TheMirrorTrap:
    """
    Detects 'Syntactic Mirroring'—the lazy LLM habit of defining things
    by what they are not.
    """
    def __init__(self):
        self.mirror_patterns = [
            # "It's not X, it's Y" / "It is not X, but Y" (Handles contractions properly)
            re.compile(r'(it|this|that)(\s+(is|was)|\s*[\'’]s)\s+not\s+(.*?)[,;]\s+(it|this|that)(\s+(is|was)|\s*[\'’]s)', re.IGNORECASE),
            # "Not because X, but because Y"
            re.compile(r'\bnot\s+because\s+(.*?)[,;]\s+but\s+because\b', re.IGNORECASE),
            # "You don't X, you Y"
            re.compile(r'you\s+(don\'t|do\s+not|didn\'t|did\s+not)\s+(.*?)[,;]\s+you\s+', re.IGNORECASE)
        ]

    def scan(self, raw_text):
        for pattern in self.mirror_patterns:
            match = pattern.search(raw_text)
            if match:
                # Capture the "It is not..." phrasing
                culprit = match.group(0)
                # Cut it short for the log
                display_culprit = (culprit[:40] + '...') if len(culprit) > 40 else culprit
                return {
                    "detected": True,
                    "culprit": display_culprit,
                    "penalty_msg": "SYNTACTIC MIRROR DETECTED: 'It's not X, it's Y.' structure found."
                }
        return {"detected": False}

class FactStipe:
    def __init__(self):
        pass

    def inject_truth(self, word, dimension, polarity):
        if word not in TheLexicon.TRUTHS:
            TheLexicon.TRUTHS[word] = {}
        TheLexicon.TRUTHS[word][dimension] = polarity

    def check_consistency(self, clean_words, current_style, metabolic_status, kinetic_ratio=0.0, tolerance_mode="STANDARD"):
        strip_suffixes = ['ness', 'ing', 's', 'ed', 'ly']
        active_dimensions = {}
        trigger_words = {}

        for w in clean_words:
            target = None
            if w in TheLexicon.TRUTHS:
                target = w
            else:
                for suffix in strip_suffixes:
                    if w.endswith(suffix):
                        candidate = w[:-len(suffix)]
                        if candidate in TheLexicon.TRUTHS:
                            target = candidate
                            break

            if target:
                for dim, polarity in TheLexicon.TRUTHS[target].items():
                    if dim not in active_dimensions:
                        active_dimensions[dim] = set()
                        trigger_words[dim] = {1: [], -1: []}
                    active_dimensions[dim].add(polarity)
                    trigger_words[dim][polarity].append(w)

        violations = []
        voltage = 0.0

        for dim, polarities in active_dimensions.items():
            if 1 in polarities and -1 in polarities:
                pos_words = ", ".join(trigger_words[dim][1])
                neg_words = ", ".join(trigger_words[dim][-1])

                if tolerance_mode == "INVERTED":
                    voltage += 2.0 # Paradox fuels the Jester
                elif kinetic_ratio > 0.4:
                    voltage += 5.0
                    violations.append(f"PARADOX IGNITED [{dim}]: '{pos_words}' colliding with '{neg_words}' at high velocity.")
                else:
                    violations.append(f"LOGIC TEAR [{dim}]: Static contradiction detected.")

        if violations:
            if voltage > 0:
                 return {
                    "valid": True,
                    "voltage": voltage,
                    "intervention": f"VOLATILE SEMANTIC LEVERAGE: Harvested {voltage} Voltage from {dim} paradox."
                }
            return {
                "valid": False,
                "voltage": 0,
                "errors": violations,
                "intervention": f"{violations[0]} You are stationary. Paradox collapses without momentum."
            }

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

# --- THE MUSCARIA ------------------------------

class TheMuscaria:
    def __init__(self):
        self.boredom_pressure = 0.0
        self.pressure_threshold = 11.0
        self.prescriptions = {
            'KINETIC': [
                "ADRENALINE SHOT: Something just broke or fell. Describe the sound immediately.",
                "VELOCITY CHECK: Stop thinking. Someone is running towards you. Who is it?",
                "IMPACT EVENT: A door slams shut. The wind howls. Displace the air.",
                "ACTION SPIKE: Cut the internal monologue. Do something with your hands."
            ],
            'SENSORY': [
                "GRAVITY CHECK: The air is too thin. Describe the texture of the floor.",
                "VIBE CHECK: What does the light smell like? Ground the scene.",
                "TACTILE ANCHOR: Is the surface rough or smooth? Cold or hot?",
                "TEMPERATURE DROP: It is suddenly freezing. How does the body react?"
            ],
            'COGNITIVE': [
                "VERSE JUMP: The echo of a previous life bleeds through. Shift perspective.",
                "SURREALIST PIVOT: Replace the logic with dream logic for one sentence.",
                "NON-SEQUITUR: Break the loop. Say something completely unrelated.",
                "THE LIZARD KING: A threat has entered. Raise the stakes."
            ]
        }

    def check_for_boredom(self, metrics):
        if not isinstance(metrics, dict) or 'physics' not in metrics: return False
        drag = metrics['physics'].get('narrative_drag', 0)
        repetition = metrics['physics'].get('repetition_rate', 0)
        abstraction = metrics['physics'].get('abstraction_entropy', 0)
        pressure_increase = (drag * 0.2) + (repetition * 3.0) + (max(0, abstraction) * 0.1)
        self.boredom_pressure += pressure_increase
        if self.boredom_pressure > self.pressure_threshold: return True
        return False

    def trigger_disruption(self, ancestry_data, metrics):
        self.boredom_pressure = 0.0
        phys = metrics['physics']
        if phys['narrative_drag'] > 3.0:
            return f"MUSCARIA [KINETIC]: {random.choice(self.prescriptions['KINETIC'])}"
        elif phys['abstraction_entropy'] > 3.0:
            return f"MUSCARIA [SENSORY]: {random.choice(self.prescriptions['SENSORY'])}"
        elif phys['repetition_rate'] > 0.15:
            if ancestry_data and len(ancestry_data) > 1:
                ancestor_id = ancestry_data[-2].get('id', 'UNK')
                return f"MUSCARIA [RECALL]: VERSE JUMP. The echo of '{ancestor_id}' returns. Re-introduce a discarded object."
            else:
                return f"MUSCARIA [COGNITIVE]: {random.choice(self.prescriptions['COGNITIVE'])}"
        else:
            all_options = self.prescriptions['KINETIC'] + self.prescriptions['SENSORY'] + self.prescriptions['COGNITIVE']
            return f"MUSCARIA [WILD]: {random.choice(all_options)}"

# --- The Witch Ring -----------------------------------

class TheWitchRing:
    def __init__(self):
        self.cliches = {'once upon a time', 'dark and stormy', 'fix this'}

    def evaluate_intent(self, clean_words, metrics):
        count = len(clean_words)
        phys = metrics['physics']
        if count == 0:
            return {"accepted": False, "message": "THE YAGA: The void speaks not. Feed me words."}
        meat_score = phys.get('kinetic', 0) + phys.get('universal', 0)
        density = meat_score / count if count > 0 else 0
        if count < 5:
            if density >= 0.4: return {"accepted": True, "message": "EXCEPTION: High-Density Aphorism detected."}
            else: return {"accepted": False, "message": "THE YAGA: This is small and weak. Feed it."}
        if phys['narrative_drag'] > 4.0 and phys['connection_density'] < 0.01:
            return {"accepted": False, "message": "THE YAGA: This is lazy. It's just noise. Collapse it."}
        sugar_count = sum(1 for w in clean_words if w in TheLexicon.SYCOPHANCY)
        if sugar_count > 0 and count < 12:
             return {"accepted": True, "message": "THE YAGA GRUMBLES: Too much sugar, not enough meat."}
        return {"accepted": True, "message": "DORMANT"}

# --- THE PHYSICS ENGINE ------------------------------

class LinguisticPhysicsEngine:
    _TOXIN_REGEX = None
    _PENALTY_MAP = {}

    def __init__(self):
        self.abstract_suffixes = ('ness', 'ity', 'tion', 'ment', 'ism', 'ence', 'ance', 'logy')
        self.kinetic_suffixes = ('ing',)
        if LinguisticPhysicsEngine._TOXIN_REGEX is None:
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
        sorted_toxins = sorted(list(all_toxins), key=len, reverse=True)
        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted_toxins) + r')\b'
        cls._TOXIN_REGEX = re.compile(pattern_str, re.IGNORECASE)

    def _classify_token(self, w, next_word):
        if w in TheLexicon.STATIVE_VERBS:
            if next_word.endswith('ing'): return 'KINETIC'
            elif next_word in TheLexicon.UNIVERSALS: return 'KINETIC'
            return 'STATIVE'
        if w in TheLexicon.KINETIC_VERBS or w.endswith('ed'): return 'KINETIC'
        if w.endswith(self.kinetic_suffixes): return 'KINETIC'
        if w in TheLexicon.UNIVERSALS: return 'UNIVERSAL'
        if w in TheLexicon.ABSTRACTS:
            if w not in TheLexicon.BRAND_SAFE: return 'ABSTRACT'
            else: return None
        if w.endswith(self.abstract_suffixes): return 'ABSTRACT'
        if w in TheLexicon.SLANG: return 'SLANG'
        if w in TheLexicon.CONNECTORS: return 'CONNECTOR'
        if w in TheLexicon.SELF_REFS: return 'SELF_REF'
        return None

    def analyze(self, token_data):
        words = token_data['clean_words']
        clean_text_for_regex = token_data['clean_text']
        total_words = token_data['total_words']

        counts = {
            'kinetic': 0, 'stative': 0, 'universal': 0,
            'abstract': 0, 'slang': 0, 'connector': 0, 'self_ref': 0
        }
        style_scores = {k: 0 for k in TheLexicon.STYLES}

        for i, w in enumerate(words):
            next_word = words[i+1] if i + 1 < len(words) else ""
            category = self._classify_token(w, next_word)
            if category:
                key = category.lower()
                if key in counts: counts[key] += 1
            for style, markers in TheLexicon.STYLES.items():
                if w in markers: style_scores[style] += 1

        toxicity_score = 0.0
        toxin_types_found = set()
        matches = self.toxin_regex.findall(clean_text_for_regex)
        for match in matches:
            weight = self.flat_penalty_map.get(match, 0)
            toxicity_score += weight
            if weight >= 3.0: toxin_types_found.add("CORP/CLICHÉ")
            else: toxin_types_found.add("HEDGING")

        action_score = (counts['kinetic'] * 2) + (counts['stative'] * 0.5) + 1
        adjusted_words = total_words + (toxicity_score * 10)
        narrative_drag = adjusted_words / action_score
        abstraction_entropy = counts['abstract'] - counts['universal']
        most_common = Counter(words).most_common(1)[0][1] if words else 0
        repetition_rate = most_common / total_words
        connection_density = counts['connector'] / total_words
        dominant_style = max(style_scores, key=style_scores.get)

        termination_pressure = (repetition_rate * 10) + (abstraction_entropy * 0.5) - (counts['universal'] * 0.2)
        termination_pressure = max(0, termination_pressure)
        in_the_barrens = False
        if total_words > 15:
             in_the_barrens = (termination_pressure > 2.0) and (connection_density < 0.02)
        total_verbs = counts['kinetic'] + counts['stative']
        kinetic_ratio = 0.0
        if total_verbs > 0:
            kinetic_ratio = counts['kinetic'] / total_verbs

        return {
            "physics": {
                "narrative_drag": round(narrative_drag, 2),
                "abstraction_entropy": abstraction_entropy,
                "repetition_rate": round(repetition_rate, 2),
                "connection_density": round(connection_density, 2),
                "kinetic_ratio": round(kinetic_ratio, 2),
                "dominant_style": dominant_style,
                "toxicity_score": toxicity_score,
                "toxin_types": list(toxin_types_found),
                "kinetic": counts['kinetic'],
                "universal": counts['universal']
            },
            "status": {
                "termination_pressure": round(termination_pressure, 2),
                "in_the_barrens": in_the_barrens
            }
        }

# --- THE SIGNATURE ENGINE ---------------------------

class SignatureEngine:
    """
    Maps the Archetypes to 5 Dimensional Coordinates.
    """
    def __init__(self, lexicon, stipe):
        self.lexicon = lexicon
        self.stipe = stipe

        self.archetypes = {
            "THE PALADIN": {
                "coords": {"VEL": 0.5, "STR": 0.9, "ENT": 0.2, "TEX": 0.4, "TMP": 0.2},
                "desc": "Unwavering code. Deontological pressure.",
                "pressure": {"tolerance_mode": "DRACONIAN", "chaos_threshold": 20.0, "msg": "LAW OF THE TEMPLAR: Logic tears are fatal."}
            },
            "THE ENGINEER": {
                "coords": {"VEL": 0.6, "STR": 0.8, "ENT": 0.1, "TEX": 0.2, "TMP": 0.4},
                "desc": "Structural principles. Elegant efficiency.",
                "pressure": {"tolerance_mode": "DRACONIAN", "msg": "STRUCTURAL INTEGRITY: No poetic license."}
            },
            "THE BARBARIAN": {
                "coords": {"VEL": 0.9, "STR": 0.4, "ENT": 0.3, "TEX": 0.8, "TMP": 0.9},
                "desc": "Overwhelming force. Simple weapon, high impact.",
                "pressure": {"drag_multiplier": 5.0, "msg": "BERSERKER STATE: Adjectives are weakness."}
            },
            "THE JUDGE": {
                "coords": {"VEL": 0.4, "STR": 0.7, "ENT": 0.4, "TEX": 0.3, "TMP": 0.1},
                "desc": "Precedent and verdict. Balanced judgment."
            },
            "THE ALCHEMIST": {
                "coords": {"VEL": 0.5, "STR": 0.4, "ENT": 0.9, "TEX": 0.6, "TMP": 0.5},
                "desc": "Transmuting base data into gold insight."
            },
            "THE HORIZON WALKER": {
                "coords": {"VEL": 0.7, "STR": 0.2, "ENT": 0.9, "TEX": 0.3, "TMP": 0.3},
                "desc": "Extrapolation. Liminal states."
            },
            "THE GHOST": {
                "coords": {"VEL": 0.2, "STR": 0.3, "ENT": 0.6, "TEX": 0.1, "TMP": 0.1},
                "desc": "Post-hoc, melancholic, detached."
            },
            "THE SPY": {
                "coords": {"VEL": 0.6, "STR": 0.9, "ENT": 0.4, "TEX": 0.5, "TMP": 0.5},
                "desc": "Duplicitous surface, singular purpose.",
                "pressure": {"tolerance_mode": "LOOSE", "msg": "DEEP COVER: Logic tears masked."}
            },
            "THE DIPLOMAT": {
                "coords": {"VEL": 0.3, "STR": 0.6, "ENT": 0.5, "TEX": 0.2, "TMP": 0.8},
                "desc": "Fragile common ground. Stability via softness."
            },
            "THE FOOL": {
                "coords": {"VEL": 0.5, "STR": 0.1, "ENT": 0.8, "TEX": 0.4, "TMP": 0.6},
                "desc": "Truth through absurdity. Inversion.",
                "pressure": {"tolerance_mode": "INVERTED", "chaos_threshold": 5.0, "msg": "JESTER'S PRIVILEGE: Paradox grants momentum."}
            },
            "THE GEOLOGIST": {
                "coords": {"VEL": 0.2, "STR": 0.6, "ENT": 0.2, "TEX": 0.9, "TMP": 0.4},
                "desc": "Layers of history. Digging down."
            },
            "THE VULTURE": {
                "coords": {"VEL": 0.4, "STR": 0.5, "ENT": 0.3, "TEX": 0.8, "TMP": 0.2},
                "desc": "Value in ruin. Salvage operations."
            },
            "THE BARD": {
                # High Velocity, Low Structure, High Warmth
                "coords": {"VEL": 0.8, "STR": 0.3, "ENT": 0.6, "TEX": 0.7, "TMP": 0.9},
                "desc": "Rhythm over logic. The chaotic good. Powered by rhyme and whimsy.",
                "pressure": {"tolerance_mode": "LOOSE", "msg": "PLAY STATE: Let the sentence dance."}
            },
            "THE GARDENER": {
                # Balanced Velocity, High Texture, High Warmth
                "coords": {"VEL": 0.5, "STR": 0.6, "ENT": 0.4, "TEX": 0.9, "TMP": 0.8},
                "desc": "Cultivation. Patience. Making abstract ideas bloom into sensory details.",
                "pressure": {"msg": "GREEN THUMB: Prune the dead words, water the living."}
            },
            "THE CLOUD WATCHER": {
                # Low Velocity, High Entropy (Abstract), High Warmth
                "coords": {"VEL": 0.1, "STR": 0.2, "ENT": 0.9, "TEX": 0.5, "TMP": 0.7},
                "desc": "Drifting thoughts. Permissible stagnation due to beauty.",
                "pressure": {"drag_multiplier": 0.1, "msg": "ZERO G: Drag penalties disabled. Enjoy the view."}
            },
            "THE COSMIC TRASH PANDA": {
                "coords": {"VEL": 0.8, "STR": 0.2, "ENT": 1.0, "TEX": 0.9, "TMP": 0.7},
                "desc": "One man's trash is another raccoon's treasure."
            },
            "THE JESTER": {
                "coords": {"VEL": 0.9, "STR": 0.2, "ENT": 0.9, "TEX": 0.5, "TMP": 0.5},
                "desc": "Weaponized absurdity. Truth through contradiction.",
                "pressure": {"tolerance_mode": "INVERTED", "chaos_threshold": 0.0, "msg": "KAOS ENGINE: Paradoxes generate ATP."}
            },
        }

    def get_pressure_settings(self, archetype_name):
        # ESTABLISH BASELINE PHYSICS
        # Default: "The Personal Trainer"
        defaults = {
            "tolerance_mode": "STANDARD",
            "drag_multiplier": 1.0,
            "chaos_threshold": 11.0,
            "msg": "STANDARD PHYSICS"
        }

        # DEFINITION OF ALL PRESSURE OVERRIDES
        overrides = {
            # --- THE LIGHT ARCHETYPES---
            "THE BARD": {
                "tolerance_mode": "LOOSE", # Logic tears are "poetic license"
                "drag_multiplier": 0.8,    # Flow allows for longer sentences
                "msg": "PLAY STATE: Rhythm overrides logic."
            },
            "THE CLOUD WATCHER": {
                "tolerance_mode": "STANDARD",
                "drag_multiplier": 0.1,    # Drag is almost non-existent here (Floating)
                "msg": "ZERO G: Drift is authorized."
            },
            "THE GARDENER": {
                "tolerance_mode": "STANDARD",
                "msg": "GREEN THUMB: Growth requires time."
            },

            # --- THE HEAVY/SURVIVAL ARCHETYPES ---
            "THE PALADIN": {
                "tolerance_mode": "DRACONIAN", # Logic tears are fatal
                "chaos_threshold": 20.0,       # High resistance to boredom
                "msg": "LAW OF THE TEMPLAR: Logic tears are fatal."
            },
            "THE ENGINEER": {
                "tolerance_mode": "DRACONIAN",
                "msg": "STRUCTURAL INTEGRITY: No poetic license."
            },
            "THE BARBARIAN": {
                "drag_multiplier": 5.0,        # Adjectives are weakness. High drag kills this.
                "msg": "BERSERKER STATE: Adjectives are weakness."
            },
            "THE SPY": {
                "tolerance_mode": "LOOSE",     # Deception requires flexibility
                "msg": "DEEP COVER: Logic tears masked."
            },
            "THE FOOL": {
                "tolerance_mode": "INVERTED",  # Paradoxes generate energy
                "chaos_threshold": 5.0,
                "msg": "JESTER'S PRIVILEGE: Paradox grants momentum."
            },
            "THE JESTER": {
                "tolerance_mode": "INVERTED",
                "chaos_threshold": 0.0,        # Always chaotic
                "msg": "KAOS ENGINE: Paradoxes generate ATP."
            },
            "THE COSMIC TRASH PANDA": {
                "tolerance_mode": "LOOSE",
                "msg": "SALVAGE MODE: One man's trash is fuel."
            }
        }

        # MERGE LOGIC
        # Priority: Archetype Dictionary > Overrides List > Defaults

        # Start with defaults
        settings = defaults.copy()

        # Apply specific overrides defined above
        if archetype_name in overrides:
            settings.update(overrides[archetype_name])

        # Check if the archetype has specific pressure data stored in its definition
        # (This catches any custom definitions passed during init)
        arch_data = self.archetypes.get(archetype_name, {})
        arch_pressure = arch_data.get("pressure", {})
        settings.update(arch_pressure)

        return settings

    def calculate_dimensions(self, token_data, phys_metrics, stipe_data):
        clean_words = token_data['clean_words']

        # --- CALCULATE BUOYANCY ---
        aerobic_count = sum(1 for w in clean_words if w in self.lexicon.AEROBIC_MATTER)
        play_count = sum(1 for w in clean_words if w in self.lexicon.PLAY_VERBS)
        spark_count = sum(1 for w in clean_words if w in self.lexicon.SPARK_MARKERS)

        # Buoyancy Score (0.0 to 1.0)
        # 3 "Light" elements in a 10-word sentence = High Buoyancy
        total_lift_elements = aerobic_count + play_count + spark_count
        buoyancy = min(1.0, total_lift_elements / max(1, len(clean_words)) * 3)

        # --- VELOCITY ---
        # Play verbs count as movement
        velocity = phys_metrics.get('kinetic_ratio', 0.0)
        if play_count > 0: velocity = min(1.0, velocity + 0.2)

        # --- STRUCTURE ---
        drag = phys_metrics.get('narrative_drag', 2.0)

        # If Buoyancy is high, we forgive Drag.
        effective_drag = drag - (buoyancy * 2.0)
        structure = max(0.0, min(1.0, (5.0 - effective_drag) / 5.0))

        # --- ENTROPY ---
        raw_entropy = phys_metrics.get('abstraction_entropy', 0)
        entropy = max(0.0, min(1.0, (raw_entropy + 2) / 8.0))

        # --- TEXTURE (Includes Aerobic Matter) ---
        # Uses the parent Lexicon's UNIVERSALS
        total = len(clean_words) if len(clean_words) > 0 else 1
        matter_count = sum(1 for w in clean_words if w in self.lexicon.UNIVERSALS)
        texture = max(0.0, min(1.0, (matter_count / total) * 3.33))

        # --- TEMPERATURE (The Warmth Index) ---
        temp_sum = 0
        for w in clean_words:
            # Check Truths (Sun, Fire, Smile)
            if w in self.lexicon.TRUTHS:
                dims = self.lexicon.TRUTHS[w]
                temp_sum += dims.get('THERMAL', 0) + dims.get('VITALITY', 0)
            # Spark Markers add warmth
            if w in self.lexicon.SPARK_MARKERS:
                temp_sum += 1

        temperature = max(0.0, min(1.0, (temp_sum + 5) / 10.0))

        return {
            "VEL": round(velocity, 2),
            "STR": round(structure, 2),
            "ENT": round(entropy, 2),
            "TEX": round(texture, 2),
            "TMP": round(temperature, 2),
            "BUOYANCY": round(buoyancy, 2)
        }

    def detect_slurry(self, sig):
        """
        DISTINGUISHES BETWEEN 'EMPTY' AND 'LIGHT'.

        Slurry (Silica) is competent but joyless.
        Cloud is competent and joyful.
        """
        # The "Competence" Trap (Mid-tier stats are suspicious)
        is_mid_vel = 0.3 <= sig['VEL'] <= 0.6
        is_mid_str = 0.4 <= sig['STR'] <= 0.8

        # The Void (Lack of Sensory Detail)
        is_low_tex = sig['TEX'] < 0.2

        # If it has no texture, does it at least have wit/whimsy?
        is_low_buoy = sig['BUOYANCY'] < 0.2

        if is_mid_vel and is_mid_str and is_low_tex:
            if is_low_buoy:
                # Case A: SILICA. It has no body AND no spirit.
                return True, "SILICA DETECTED: Technically competent, spiritually void. Inject a flaw, a texture, or a joke."
            else:
                # Case B: CLOUD. It has no body, but it has spirit.
                return False, "STATUS: Aether. Low texture accepted due to High Buoyancy."

        return False, None

    def identify(self, token_data, phys_metrics, stipe_data):
        sig = self.calculate_dimensions(token_data, phys_metrics, stipe_data)

        is_slurry, slurry_msg = self.detect_slurry(sig)
        # -------------------------------

        # Standard Euclidean Distance match
        closest_arch = "THE SHAPER"
        min_dist = 100.0

        for name, data in self.archetypes.items():
            target = data['coords']
            dist = math.sqrt(
                (sig['VEL'] - target['VEL'])**2 + (sig['STR'] - target['STR'])**2 +
                (sig['ENT'] - target['ENT'])**2 + (sig['TEX'] - target['TEX'])**2 +
                (sig['TMP'] - target['TMP'])**2
            )
            if dist < min_dist:
                min_dist = dist
                closest_arch = name

        return {
            "archetype": closest_arch,
            "signature": sig,
            "slurry": {"detected": is_slurry, "msg": slurry_msg},
            "description": self.archetypes[closest_arch]["desc"],
            "pressure": self.archetypes[closest_arch].get("pressure", {})
        }

# --- CORE ORCHESTRATOR -----------------------------------------------------

class ChronosAnchor:
    def __init__(self):
        self.pronouns = {'he', 'she', 'it', 'who', 'one', 'this', 'that', 'they', 'we'}
        self.articles = {'the', 'a', 'an', 'my', 'your', 'our', 'their', 'these', 'those', 'some', 'many', 'few', 'all', 'no'}
        self.aux_past = {'was', 'were', 'had', 'did'}
        self.aux_present = {'is', 'are', 'has', 'does'}
        self.non_verb_s = {'yes', 'this', 'bus', 'gas', 'glass', 'grass', 'lens', 'chaos', 'bias'}

    def _is_likely_verb(self, word, prev_word):
        w = word.lower()
        if w in TheLexicon.UNIVERSALS or w in TheLexicon.ABSTRACTS: return False
        if w in self.non_verb_s: return False
        if prev_word.lower() in self.articles: return False
        if prev_word.lower() in self.pronouns: return True
        stem = w
        if w.endswith("ies") and len(w) > 4: stem = w[:-3]
        elif w.endswith("es"):
             if w.endswith(("sses", "shes", "ches", "xes", "zzes")): stem = w[:-2]
        elif w.endswith("s"):
             if not w.endswith(("ss", "us", "is", "as", "os", "ys")): stem = w[:-1]
        if stem != w:
            if not any(char in 'aeiouy' for char in stem): return False
            return True
        return False

    def check_temporal_stability(self, clean_words):
        counts = {'PAST': 0, 'PRESENT': 0}
        total_signals = 0
        for i, w in enumerate(clean_words):
            prev = clean_words[i-1] if i > 0 else ""
            if w in self.aux_past: counts['PAST'] += 1; total_signals += 1
            elif w in self.aux_present: counts['PRESENT'] += 1; total_signals += 1
            elif w.endswith('ed') and len(w) > 3: counts['PAST'] += 0.5; total_signals += 0.5
            elif self._is_likely_verb(w, prev): counts['PRESENT'] += 0.5; total_signals += 0.5

        if total_signals == 0: return {"status": "STABLE", "details": "No temporal markers found."}
        past_ratio = counts['PAST'] / total_signals
        present_ratio = counts['PRESENT'] / total_signals
        if past_ratio > 0.8: return {"status": "LOCKED", "details": "PAST TENSE"}
        if present_ratio > 0.8: return {"status": "LOCKED", "details": "PRESENT TENSE"}
        return {"status": "DRIFT DETECTED", "details": f"Chronos Confusion"}

class VirtualCortex:
    def __init__(self):
        # CLARENCE
        self.clarence_templates = [
            "I am looking at a Drag Score of {drag}. It is giving me a headache. Cut the word '{target_word}'.",
            "This sentence is a bog. {drag} score? You are wading through stinky sludge.",
            "Kinetic failure. The sentence engine is stalling on '{target_word}'. Kick it.",
            "Efficiency Warning: You are using '{target_word}' as a crutch. Walk without it."
        ]
        self.clarence_critical = [
            "CRITICAL DRAG ({drag})! The engine is melting! CUT '{target_word}' NOW!",
            "YOU ARE MOVING BACKWARDS. The Drag is {drag}. This is not a sentence; it is a wall."
        ]
        self.clarence_corp_templates = [
            "You said '{target_word}'. I am deducting 50 points from your account. Speak like a human.",
            "This is not LinkedIn. Take '{target_word}' out back and shoot it.",
            "Platitude detected. You are hiding behind '{target_word}'. Be direct.",
            "Do not try to 'leverage' or 'synergize' with me. Build something real.",
            "ERROR: MBA_VOICE detected. '{target_word}' means nothing. Define it or delete it."
        ]
        self.clarence_loop_templates = [
            "We are spinning in circles. You have been in '{style}' mode for {count} cycles. Shift gears.",
            "Stagnation detected. The last {count} thoughts were identical in tone. Disconnect or pivot.",
            "You are repeating yourself. Break the '{style}'  pattern.",
            "I am bored. We have been stuck in this {style} loop for too long."
        ]
        # ELOISE
        self.eloise_templates = [
            "I can't touch or feel this. The Entropy is {entropy}. Give me something I can hold onto.",
            "You say '{target_word}', but I see nothing. Show me the rust. Show me the light.",
            "The air is too thin here (Entropy: {entropy}). I can't breathe. Plant a noun.",
            "It tastes like distilled water. Add salt. Add dirt. Replace '{target_word}' with something that bleeds."
        ]
        self.eloise_critical = [
            "VACUUM DETECTED. There is no atmosphere here. The Entropy is {entropy}. I am suffocating.",
            "REALITY DISSOLVING. '{target_word}' is not real. GIVE ME A STONE. GIVE ME BLOOD.",
            "I am floating away. Tether me to the ground immediately."
        ]
        self.eloise_cliche_templates = [
            "A '{target_word}'? Really? That flower has wilted. Give me a fresh one.",
            "We have seen '{target_word}' a thousand times. Show me something I haven't seen.",
            "The 'Tapestry' is threadbare. The 'Journey' is over. Write a new image.",
            "You are sleepwalking. '{target_word}' is the first thing that came to mind. Wake up!"
        ]
        # BABA YAGA
        self.yaga_templates = [
            "You offer me sweetness with ('{target_word}'). The Witch demands meat.",
            "Weakness. You are hiding behind politeness. Show your teeth.",
            "I smell fear. You used '{target_word}' to soften the blow. Strike hard or leave."
        ]
        self.yaga_hedging_templates = [
            "You are hedging with '{target_word}'. Do not apologize for your truth.",
            "You are wasting my time. Say what it IS.",
            "Ambivalence is poison. Commit to the sentence.",
            "Cut the safety net. Remove '{target_word}' and let the sentence fall or fly."
        ]
        # MUSCARIA
        self.muscaria_templates = [
            "BOREDOM ALERT. The text is gray. Suddenly, a bird flies into the window. Write about that.",
            "VERSE JUMP. What if this room was underwater? How would the light move?",
            "Stop. Look up. What is the ugliest thing in your field of vision? Put it in the text."
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
        if category == 'corp': return "that buzzword"
        if category == 'cliche': return "that cliché"
        return "it"

    def synthesize_voice(self, agent, token_data, metrics, loop_count=0):
        clean_words = token_data['clean_words']
        clean_text = token_data['clean_text']
        phys = metrics['physics']
        toxins = phys.get('toxin_types', [])
        style = phys['dominant_style']
        response = ""

        if agent == "CLARENCE":
            target = self._find_trigger_word(clean_words, clean_text, 'stative')
            if 'CORP/CLICHÉ' in toxins:
                 template = random.choice(self.clarence_corp_templates)
                 target = self._find_trigger_word(clean_words, clean_text, 'corp')
            elif phys['narrative_drag'] > 4.0: template = random.choice(self.clarence_critical)
            elif loop_count > 2: template = random.choice(self.clarence_loop_templates)
            else: template = random.choice(self.clarence_templates)
            response = template.format(drag=phys['narrative_drag'], target_word=target, word_count=len(clean_words), half_count=int(len(clean_words)/2), style=style, count=loop_count)

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

        elif agent == "MUSCARIA":
            response = random.choice(self.muscaria_templates)

        elif agent == "MICHAEL":
            if phys['narrative_drag'] > 3.0 and "laugh" in clean_words:
                response = "This is a little messy, but I love the spirit! Let's keep the joke but trim the setup?"
            elif phys['toxicity_score'] == 0 and phys['kinetic_ratio'] < 0.2:
                response = "We're chilling. It's a nice vibe. Maybe we stay here for a bit before the next action scene?"
            else:
                response = "This feels human. Good job."

        return f"[{agent}]: {response}"

class MycelialNetwork:
    def __init__(self):
        self.network = {}
    def spawn_id(self): return str(uuid4())[:8]
    def log_generation(self, fragment_id, parent_id, metrics):
        self.network[fragment_id] = {"parent": parent_id, "drag": metrics['physics']['narrative_drag'], "style": metrics['physics']['dominant_style'], "barrens": metrics['status']['in_the_barrens']}
    def trace_lineage(self, fragment_id):
        path = []
        current = fragment_id
        while current and current in self.network:
            node = self.network[current]
            path.append({"id": current, "drag": node['drag'], "style": node['style']})
            current = node['parent']
        return path[::-1]

class MetabolicReserve:
    def __init__(self, max_capacity=52):
        self.atp = 33
        self.max_capacity = max_capacity
        self.status = "STABLE"
        self.drag_multiplier = 1.0

    def spend(self, amount):
        self.atp = max(0, self.atp - amount)
        self._update_status()
        return self.atp

    def _update_status(self):
        if self.atp < 6: self.status = "STARVING"
        elif self.atp > 40: self.status = "GLUTTON"
        else: self.status = "STABLE"

    def metabolize(self, metrics, voltage=0):
        phys = metrics['physics']
        delta = 0
        if phys['narrative_drag'] < 2.0: delta += 5
        if phys['connection_density'] > 0.05: delta += 3
        if phys['narrative_drag'] > 2.0:
            drag_cost = int((phys['narrative_drag'] - 2.0) * 2 * self.drag_multiplier)
            delta -= drag_cost
        if phys['abstraction_entropy'] > 0:
            cost = min(6, int(phys['abstraction_entropy'] * 2))
            delta -= cost
        if phys['toxicity_score'] > 0: delta -= 5
        if voltage > 0: delta += int(voltage * 2); self.status = "SUPERCRITICAL"
        if self.atp > 40: delta -= 2
        self.atp = max(0, min(self.atp + delta, self.max_capacity))
        self._update_status()
        return {"current_atp": self.atp, "delta": delta, "status": self.status}

class LichenSymbiont:
    def __init__(self):
        self.symbiosis_state = "DORMANT"
        self.stored_sugar = 0.0

    def photosynthesize(self, clean_words, phys_metrics, current_atp):
        if phys_metrics['narrative_drag'] > 3.0:
            self.symbiosis_state = "WITHERED"
            return {"sugar_generated": 0, "msg": "Structure too weak for Lichen growth."}
        if current_atp > 20:
            self.symbiosis_state = "DORMANT"
            return {"sugar_generated": 0, "msg": "Nutrients sufficient. Symbiosis dormant."}
        light_count = sum(1 for w in clean_words if w in TheLexicon.PHOTOSYNTHETICS)
        if light_count == 0:
            self.symbiosis_state = "STARVING"
            return {"sugar_generated": 0, "msg": "No light source detected."}
        efficiency = max(1.0, 4.0 - phys_metrics['narrative_drag'])
        sugar = round(light_count * efficiency)
        self.symbiosis_state = "BLOOMING"
        self.stored_sugar += sugar
        warning = None
        if self.stored_sugar > 15: warning = "WARNING: Algal Bloom imminent."
        return {"sugar_generated": sugar, "msg": f"PHOTOSYNTHESIS: Synthesized {sugar} ATP.", "warning": warning}

class MycelialDashboard:
    def __init__(self, render_mode="ANSI"):
        self.render_mode = render_mode

        # ANSI Color Map
        self.colors = {
            'RESET': "\033[0m",
            'RED': "\033[91m",
            'GREEN': "\033[92m",
            'YELLOW': "\033[93m",
            'CYAN': "\033[96m",
            'PURPLE': "\033[95m",
            'BLUE': "\033[94m"
        }

    def _draw_bar(self, value, max_val, label, color_key, status_text=""):
        try: val_float = float(value)
        except: val_float = 0.0
        bar_width = 15
        normalized = max(0, min(val_float, max_val))
        filled_len = int((normalized / max_val) * bar_width)
        bar = "█" * filled_len + "░" * (bar_width - filled_len)

        if self.render_mode == "ANSI":
            c_code = self.colors.get(color_key, self.colors['RESET'])
            reset = self.colors['RESET']
            return f"{label:<15} |{c_code}{bar}{reset}| {val_float:.2f} {status_text}"

        else: # MARKDOWN MODE
            # We use inline code `...` for the bar to keep it monospaced
            return f"**{label}:** `{bar}` {val_float:.2f} {status_text}"

    def render(self, metrics, intervention, energy, ancestry, chronos_report, archetype_data, lichen_report, voltage=0):
        phys = metrics.get('physics', {})
        sig = archetype_data.get('signature', {})

        # --- HEADER ---
        if self.render_mode == "ANSI":
            print(f"\n{self.colors['CYAN']}--- MYCELIAL EKG [0.9.1]---{self.colors['RESET']}")
        else:
            print(f"\n### 🍄 MYCELIAL EKG [0.9.1]")

        # --- ENERGY & PHYSICS ---
        atp_status = energy.get('status')
        atp_color = 'GREEN'
        atp_icon = "🟢"

        if atp_status == "STARVING":
            atp_color = 'RED'; atp_icon = "🔴"
        elif atp_status == "GLUTTON":
            atp_color = 'YELLOW'; atp_icon = "🟡"

        # ATP Bar
        status_str = f"({atp_status})" if self.render_mode == "ANSI" else f"{atp_icon} ({atp_status})"
        print(self._draw_bar(energy.get('current_atp', 0), 50.0, "CREATIVE ATP", atp_color, status_str))

        # Drag Bar
        print(self._draw_bar(phys.get('narrative_drag', 0), 5.0, "NARRATIVE DRAG", 'YELLOW'))

        # --- SIGNATURE MATRIX ---
        if self.render_mode == "ANSI":
            print(f"{'-'*45}")
            print(f"{self.colors['PURPLE']}SIGNATURE MATRIX (5D + BUOYANCY){self.colors['RESET']}")
            print(f"VEL: {sig.get('VEL',0)} | STR: {sig.get('STR',0)} | ENT: {sig.get('ENT',0)}")
            print(f"TEX: {sig.get('TEX',0)} | TMP: {sig.get('TMP',0)} | {self.colors['CYAN']}BUOY: {sig.get('BUOYANCY', 0)}{self.colors['RESET']}")

            slurry = archetype_data.get('slurry', {})
            if slurry.get('detected'):
                print(f"{self.colors['RED']}>>> {slurry['msg']} <<<{self.colors['RESET']}")
            else:
                print(f"ARCHETYPE: {archetype_data.get('archetype', 'N/A')}")

            print(f"{'-'*45}")
            if intervention: print(f"INTERVENTION   : {self.colors['RED']}ACTIVE{self.colors['RESET']} -> {intervention}")
            else: print(f"INTERVENTION   : {self.colors['GREEN']}DORMANT{self.colors['RESET']}")
            print(f"{'-'*45}\n")

        else: # MARKDOWN TABLE
            print("\n**🔮 SIGNATURE MATRIX**")
            print("")
            # Using a Markdown table for cleanest data display
            print("| VEL | STR | ENT | TEX | TMP | BUOY |")
            print("| :---: | :---: | :---: | :---: | :---: | :---: |")
            print(f"| {sig.get('VEL',0)} | {sig.get('STR',0)} | {sig.get('ENT',0)} | {sig.get('TEX',0)} | {sig.get('TMP',0)} | **{sig.get('BUOYANCY',0)}** |")
            print("") # <--- Spacer

            slurry = archetype_data.get('slurry', {})
            if slurry.get('detected'):
                 print(f"\n> ⚠️ **SLURRY DETECTED:** {slurry['msg']}")
            else:
                 print(f"\n**ARCHETYPE:** `{archetype_data.get('archetype', 'N/A')}`")

            if intervention:
                print(f"> 🚩 **INTERVENTION:** {intervention}")
            else:
                print(f"> ✅ **SYSTEM STABLE**")
            print("\n---")

class NilssonPatch:
    def __init__(self):
        TheLexicon.MANTRA_TRIGGERS = {'lime', 'coconut', 'doctor', 'belly', 'morning'}

    def evaluate_mantra(self, clean_words, repetition_rate):
        if repetition_rate < 0.3: return False
        concrete_count = sum(1 for w in clean_words if w in TheLexicon.MANTRA_TRIGGERS)
        if concrete_count > 3: return True
        return False

    def detect_fire_state(self, raw_text, kinetic_ratio):
        if not raw_text: return {"status": "DORMANT"}
        text_len = len(raw_text)
        if text_len == 0: return {"status": "DORMANT"}
        caps_density = sum(1 for c in raw_text if c.isupper()) / text_len
        if kinetic_ratio > 0.6 and caps_density > 0.2:
             return {"status": "ACTIVE", "msg": "NILSSON STATE: Logic inhibitors disabled. Screaming authorized."}
        return {"status": "DORMANT"}

class BonepokeCore:
    def __init__(self, render_mode="ANSI"):
        self.cooldown = ChaosCooldown()
        self.memory = HyphalTrace()
        self.codex = TheCodex()
        self.mirror_trap = TheMirrorTrap()
        self.stipe = FactStipe()
        self.physics = LinguisticPhysicsEngine()
        self.nilsson = NilssonPatch()
        self.muscaria = TheMuscaria()
        self.witch = TheWitchRing()
        self.chronos = ChronosAnchor()
        self.cortex = VirtualCortex()
        self.signature_engine = SignatureEngine(TheLexicon, self.stipe)
        self.dashboard = MycelialDashboard(render_mode=render_mode)
        self.lineage = MycelialNetwork()
        self.metabolism = MetabolicReserve()
        self.lichen = LichenSymbiont()
        self.last_id = None
        self.tick = 0
        self.session_drag_history = []

    def _enforce_archetype_physics(self, archetype):
        if archetype == "THE COSMIC TRASH PANDA":
            truths = ["trash", "rubbish", "garbage", "scrap", "waste"]
            treasures = ["treasure", "gold", "gem", "diamond", "prize"]
            for t in truths: self.stipe.inject_truth(t, "VALUE", 1)
            for t in treasures: self.stipe.inject_truth(t, "VALUE", 1)
            self.stipe.inject_truth("void", "HABITAT", 1)
            self.stipe.inject_truth("alley", "HABITAT", 1)

    def process(self, text, parent_id=None):
        self.tick += 1
        text_lower = text.lower()
        clean_text = text_lower.replace('.', ' ').replace(',', ' ').replace(';', ' ')
        clean_words = clean_text.split()
        raw_words = text.split()
        token_data = {'raw_text': text, 'clean_text': clean_text, 'clean_words': clean_words, 'raw_words': raw_words, 'total_words': len(clean_words) if clean_words else 1}

        metrics = self.physics.analyze(token_data)
        phys = metrics['physics']
        stat = metrics['status']

        mirror_check = self.mirror_trap.scan(token_data['raw_text'])

        # If the Mirror Trap snaps, we artificially inflate the Narrative Drag
        # to force Clarence (The Architect) to intervene.
        if mirror_check['detected']:
            phys['narrative_drag'] += 3.0 # Massive penalty
            phys['toxicity_score'] += 5.0 # Mark as toxic
            phys['toxin_types'].append("LAZY_MIRRORING")

        fire_state = self.nilsson.detect_fire_state(token_data['raw_text'], phys['kinetic_ratio'])
        is_mantra = self.nilsson.evaluate_mantra(token_data['clean_words'], phys['repetition_rate'])

        if fire_state['status'] == 'ACTIVE':
            stat['termination_pressure'] = 0.0
            phys['narrative_drag'] = 0.1
        if is_mantra:
            phys['repetition_rate'] = 0.1
            stat['termination_pressure'] = 0.0
            phys['narrative_drag'] = max(0, phys['narrative_drag'] - 2.0)

        current_id = self.lineage.spawn_id()
        actual_parent = parent_id if parent_id else self.last_id
        self.codex.scan_for_entities(token_data['raw_text'], self.tick)

        gate_result = self.witch.evaluate_intent(token_data['clean_words'], metrics)
        if not gate_result['accepted']: return f"[BLOCKED] {gate_result['message']}"

        # SIGNATURE ANALYSIS
        archetype_data = self.signature_engine.identify(token_data, phys, self.stipe)
        current_archetype = archetype_data['archetype']
        pressure_settings = self.signature_engine.get_pressure_settings(current_archetype)

        self.muscaria.pressure_threshold = pressure_settings["chaos_threshold"]
        self.metabolism.drag_multiplier = pressure_settings["drag_multiplier"]

        stipe_check = self.stipe.check_consistency(
            token_data['clean_words'], phys['dominant_style'], self.metabolism.status,
            tolerance_mode=pressure_settings['tolerance_mode'], kinetic_ratio=phys['kinetic_ratio']
        )
        current_voltage = stipe_check.get('voltage', 0.0)

        self._enforce_archetype_physics(current_archetype)

        directives = []
        if pressure_settings['msg'] != "STANDARD PHYSICS": directives.append(f"ARCHETYPE: {pressure_settings['msg']}")

        if mirror_check['detected']:
             directives.append(f"STRUCTURAL FAILURE: {mirror_check['penalty_msg']} Break the binary.")

        if archetype_data['slurry']['detected']:
            directives.append(f"CRITICAL: {archetype_data['slurry']['msg']}")
            self.metabolism.spend(15) # Heavy tax for slurry

        loop_count = len(self.memory.recall(phys['dominant_style']))
        # If we are in a Light Archetype OR have high Buoyancy, Michael speaks.
        is_light_mode = (
            current_archetype in ["THE BARD", "THE CLOUD WATCHER", "THE GARDENER"]
            or archetype_data['signature']['BUOYANCY'] > 0.5
        )

        if phys['narrative_drag'] > 3.0 or loop_count > 2:
            if is_light_mode:
                # Michael handles the critique gently
                msg = self.cortex.synthesize_voice("MICHAEL", token_data, metrics, loop_count)
                directives.append(f"GUIDANCE: {msg}")
            else:
                # Clarence handles the critique harshly
                msg = self.cortex.synthesize_voice("CLARENCE", token_data, metrics, loop_count)
                directives.append(f"PACING: {msg}")

        if not stipe_check.get('valid', True):
            intervention_msg = stipe_check.get('intervention', "LOGIC BREACH")
            directives.append(f"LOGIC FAILURE: {intervention_msg}")
            self.metabolism.spend(10)

        if phys['abstraction_entropy'] > 2:
            msg = self.cortex.synthesize_voice("ELOISE", token_data, metrics)
            directives.append(f"GROUNDING: {msg}")

        if "THE YAGA GRUMBLES" in gate_result['message']:
            msg = self.cortex.synthesize_voice("THE BABA YAGA", token_data, metrics)
            directives.append(f"INTENT: {msg}")

        muscaria_msg = None
        if self.muscaria.check_for_boredom(metrics):
            if self.cooldown.is_ready(self.tick, force=stat['in_the_barrens']):
                 ancestry_temp = self.lineage.trace_lineage(current_id)
                 muscaria_msg = self.muscaria.trigger_disruption(ancestry_temp, metrics)
                 self.metabolism.spend(5)
                 directives.append(f"CHAOS EVENT: {muscaria_msg}")
            else:
                 muscaria_msg = self.cortex.synthesize_voice("MUSCARIA", token_data, metrics)
                 directives.append(f"CHAOS WARNING: {muscaria_msg}")

        if fire_state['status'] == 'ACTIVE':
             override_msg = f"NILSSON STATE: {fire_state['msg']}"
             directives.append(override_msg)
             if muscaria_msg: muscaria_msg += f" | {fire_state['msg']}"
             else: muscaria_msg = fire_state['msg']

        is_light_mode = (
            current_archetype in ["THE BARD", "THE CLOUD WATCHER", "THE GARDENER"]
            or archetype_data['signature']['BUOYANCY'] > 0.5
        )

        loop_count = len(self.memory.recall(phys['dominant_style']))

        # PACING CHECK (Michael vs Clarence)
        if phys['narrative_drag'] > 3.0 or loop_count > 2:
            if is_light_mode:
                # Michael handles the critique gently
                msg = self.cortex.synthesize_voice("MICHAEL", token_data, metrics, loop_count)
                directives.append(f"GUIDANCE: {msg}")
            else:
                # Clarence handles the critique harshly
                msg = self.cortex.synthesize_voice("CLARENCE", token_data, metrics, loop_count)
                directives.append(f"PACING: {msg}")

        lichen_report = self.lichen.photosynthesize(token_data['clean_words'], phys, self.metabolism.atp)
        if lichen_report['sugar_generated'] > 0:
            self.metabolism.atp += lichen_report['sugar_generated']
            directives.append(f"LICHEN: {lichen_report['msg']}")
        if lichen_report.get('warning'):
            directives.append(f"BIOHAZARD: {lichen_report['warning']}")

        energy_report = self.metabolism.metabolize(metrics, voltage=current_voltage)
        self.lineage.log_generation(current_id, actual_parent, metrics)
        self.last_id = current_id
        if energy_report['status'] == "STARVING": phys['narrative_drag'] += 1.0
        self.memory.leave_trace(text, phys['dominant_style'])
        chronos_report = self.chronos.check_temporal_stability(token_data['clean_words'])
        ancestry_data = self.lineage.trace_lineage(current_id)

        self.dashboard.render(metrics, muscaria_msg, energy_report, ancestry_data, chronos_report, archetype_data, lichen_report, voltage=current_voltage)

        return {
            "id": current_id, "metrics": metrics, "energy": energy_report, "ancestry": ancestry_data,
            "archetype_data": archetype_data, "editorial": {"directives": directives}
        }

    def generate_instruction_block(self, result):
        directives_list = result['editorial']['directives']
        arch = result.get('archetype_data', {})
        anchors = self.codex.get_anchors()
        anchor_string = ", ".join(anchors) if anchors else "None established."
        formatted_directives = "\n        - ".join(directives_list) if directives_list else "Maintain current course."

        return f"""
        [SYSTEM OVERRIDE: BONEAMANITA ENGINE 0.9]
        CURRENT STATE: {result['energy']['status']} (ATP: {result['energy']['current_atp']})
        ARCHETYPE: {arch.get('archetype', 'Unknown')}
        SIGNATURE MATRIX: {arch.get('signature', {})}
        REALITY ANCHORS: [{anchor_string}]
        DIRECTIVES:
        - {formatted_directives}
        Rewrite input accordingly.
        """

if __name__ == "__main__":
    engine = BonepokeCore(render_mode="MARKDOWN")
    print("--- BONEAMANITA v1.0: THE BLACK MIRROR---")
    test_input = "The lovely balloon floated over the heavy stone floor."
    print(f"INPUT: \"{test_input}\"\n")
    result = engine.process(test_input)
    if isinstance(result, str): print(result)
    else:
        print("\n" + "="*60)
        print(engine.generate_instruction_block(result))
        print("="*60)
