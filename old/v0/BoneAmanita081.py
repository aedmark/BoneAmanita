# ---------------------------------------------------------------------------
# BONEAMANITA 0.8.1 (PATCHED) - "The Symbiont Strain"
# Architects: James Taylor & Andrew Edmark | Auditors: SLASH
#
# "Feed the soil, poison the weak. Logic is the stalk; chaos is the spore.
#  PATCH NOTES 0.8.1:
#  - Fixed ZeroDivisionError in The Witch Ring & Nilsson Patch.
#  - Optimized Regex compilation in The Codex.
#  - Hardened Stemming logic in Chronos Anchor.
#  - Implemented 'Metabolic Tax' for high ATP states."
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
    Static storage for all linguistic matter.
    """
    # 1. PHYSICS MATTER
    UNIVERSALS = {
        'hand', 'eye', 'breath', 'skin', 'voice', "air", "cloth",
        'stone', 'light', 'water', 'rain', 'mud', 'dirt', 'wind',
        'wood', 'grain', 'iron', 'clay', 'paper', 'glass', 'fabric',
        'door', 'key', 'roof', 'floor', 'chair', 'table', 'wall',
        'path', 'road', 'horizon', 'shadow', 'weight', 'anchor'
    }

    ABSTRACTS = {
        'system', 'protocol', 'sequence', 'vector', 'node', 'context',
        'layer', 'matrix', 'manifold', 'substrate', 'perspective', 'framework',
        'logic', 'metric', 'concept', 'theory', 'analysis'
    }
    BRAND_SAFE = {'system', 'bonepoke', 'shimmer', 'lattice', 'muscaria'}

    KINETIC_VERBS = {
        'run', 'ran', 'hit', 'break', 'broke', 'broken',
        'take', 'took', 'make', 'made', 'press', 'build', 'built',
        'weave', 'wove', 'cut', 'throw', 'threw', 'drive', 'drove',
        'lift', 'carry', 'place', 'hold', 'turn', 'open', 'close'
    }
    STATIVE_VERBS = {'is', 'are', 'was', 'were', 'seem', 'appear', 'have', 'has', 'consist'}

    # 2. FLAVOR & STYLE
    CONNECTORS = {'we', 'you', 'us', 'together', 'share'}
    SELF_REFS = {'i', 'me', 'my', 'mine'}
    SLANG = {'vibe', 'trash', 'gonzo', 'wild', 'weird', 'mess', 'glitter', 'swamp'}

    STYLES = {
        'Moss': {'layer', 'nuance', 'deep', 'root', 'grow', 'slow'},
        'Crystal': {'logic', 'define', 'metric', 'clear', 'structure', 'frame'},
        'Timber': {'build', 'weight', 'wood', 'grain', 'solid', 'beam', 'floor'},
        'Lattice': {'foundation', 'structure', 'design', 'plan', 'support', 'connect'},
        'Claret': {'ache', 'human', 'mess', 'love', 'maybe', 'bruise', 'honest'}
    }

    # 3. TOXINS & GATEKEEPING
    TOXIC_PATTERNS = {
        'CORP_SPEAK': {
            'game-changer': 3.0, 'rubber meets': 4.0, 'paradigm': 3.0,
            'leverage': 2.5, 'synergy': 3.0, 'circle back': 3.0
        },
        'LAZY_METAPHOR': {
            'delicate dance': 4.0, 'tapestry': 3.0, 'symphony': 2.5,
            'landscape of': 2.0, 'testament to': 3.0
        },
        'WEAK_HEDGING': {
            'not just': 1.5, 'not only': 1.5, 'but rather': 2.0,
            'ultimately': 1.5, 'arguably': 2.0
        }
    }
    SYCOPHANCY = {'please', 'sorry', 'can you', 'assist'}

    # 4. TRUTH MANIFOLD (FactStipe)
    TRUTHS = {
        'sun': {'LUMENS': 1}, 'night': {'LUMENS': -1}, 'shadow': {'LUMENS': -1},
        'scream': {'DECIBELS': 1}, 'silence': {'DECIBELS': -1},
        'run': {'VITALITY': 1}, 'dead': {'VITALITY': -1},
        'fire': {'THERMAL': 1}, 'ice': {'THERMAL': -1},
    }

    # 5. SPECIAL TRIGGERS
    MANTRA_TRIGGERS = {'lime', 'coconut', 'doctor', 'belly', 'morning'}

    # 6. PHOTOSYNTHETIC TRIGGERS (The Alga's Diet)
    PHOTOSYNTHETICS = {
        'sun', 'light', 'dawn', 'truth', 'clear', 'focus', 'beam', 'ray',
        'flash', 'spark', 'reveal', 'know', 'see', 'understand', 'lucid',
        'bright', 'fire', 'star', 'vision', 'prism', 'source'
    }

# --- COMPONENT 1: MEMORY & ECONOMY -----------------------------------------

class HyphalTrace:
    """
    CONTEXTUAL MEMORY
    Implements 'Relevance Decay' to discard unused information.
    """
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
    """
    Refactored for Precision.
    PATCH 0.8.1: Moved Regex compilation to __init__ for performance.
    """
    def __init__(self):
        self.registry = {}
        self.ignore_list = {
            'The', 'A', 'An', 'It', 'He', 'She', 'They', 'We', 'I', 'You',
            'This', 'That', 'But', 'And', 'Or', 'If', 'When', 'Then',
            'System', 'Analysis', 'Metrics', 'Drag', 'Entropy', 'For', 'In', 'To', 'Of'
        }
        # OPTIMIZATION: Compile Once
        self._entity_pattern = re.compile(r'\b[A-Z][a-z]+\b')

    def scan_for_entities(self, raw_text, current_tick):
        """
        Named Entity Recognition using Regex Iteration.
        """
        for match in self._entity_pattern.finditer(raw_text):
            word = match.group()
            start_index = match.start()

            # RULE 1: IGNORE START OF SENTENCE
            is_start_of_sentence = False
            if start_index > 0:
                preceding_chars = raw_text[max(0, start_index-4):start_index]
                if any(p in preceding_chars for p in ['.', '!', '?', '\n']):
                    is_start_of_sentence = True

            if start_index == 0:
                is_start_of_sentence = True

            if is_start_of_sentence:
                continue

            # RULE 2: IGNORE STOPWORDS
            if word in self.ignore_list:
                continue

            # RULE 3: LENGTH CHECK
            if len(word) < 3:
                continue

            # REGISTER THE ENTITY
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

class FactStipe:
    """
    DIMENSIONAL REALITY ANCHOR
    Logic: Checks semantic polarity consistency.
    """
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

                if kinetic_ratio > 0.4:
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

        return {"valid": True, "voltage": 0}

class ChaosCooldown:
    def __init__(self, cooldown_ticks=5):
        self.last_trigger_tick = -cooldown_ticks
        self.cooldown = cooldown_ticks

    def is_ready(self, current_tick, force=False):
        if force or (current_tick - self.last_trigger_tick >= self.cooldown):
            self.last_trigger_tick = current_tick
            return True
        return False

# --- COMPONENT 2: THE MUSCARIA ------------------------------

class TheMuscaria:
    """
    Refactored for Smart Chaos.
    """
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
        if not isinstance(metrics, dict) or 'physics' not in metrics:
            return False

        drag = metrics['physics'].get('narrative_drag', 0)
        repetition = metrics['physics'].get('repetition_rate', 0)
        abstraction = metrics['physics'].get('abstraction_entropy', 0)

        pressure_increase = (drag * 0.2) + (repetition * 3.0) + (max(0, abstraction) * 0.1)
        self.boredom_pressure += pressure_increase

        if self.boredom_pressure > self.pressure_threshold:
            return True
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

# --- COMPONENT 3: The Witch Ring -----------------------------------

class TheWitchRing:
    """
    THE GATEKEEPER
    PATCH 0.8.1: Added ZeroDivisionError safeguard.
    """
    def __init__(self):
        self.cliches = {'once upon a time', 'dark and stormy', 'fix this'}
        TheLexicon.SYCOPHANCY = {'please', 'sorry', 'can you', 'assist'}
        self.connectors = {'we', 'us', 'together', 'love', 'kind', 'help'}

    def evaluate_intent(self, clean_words, metrics):
        count = len(clean_words)
        phys = metrics['physics']

        # PATCH: Safety Check
        if count == 0:
            return {"accepted": False, "message": "THE YAGA: The void speaks not. Feed me words."}

        # 1. DENSITY CHECK
        meat_score = phys.get('kinetic', 0) + phys.get('universal', 0)
        density = meat_score / count if count > 0 else 0

        if count < 5:
            if density >= 0.4:
                return {"accepted": True, "message": "EXCEPTION: High-Density Aphorism detected."}
            else:
                return {"accepted": False, "message": "THE YAGA: This is small and weak. Feed it."}

        # 2. LAZINESS CHECK
        if phys['narrative_drag'] > 4.0 and phys['connection_density'] < 0.01:
            return {"accepted": False, "message": "THE YAGA: This is lazy. It's just noise. Collapse it."}

        # 3. SUGAR CHECK
        sugar_count = sum(1 for w in clean_words if w in TheLexicon.SYCOPHANCY)
        if sugar_count > 0 and count < 12:
             return {"accepted": True, "message": "THE YAGA GRUMBLES: Too much sugar, not enough meat."}

        return {"accepted": True, "message": "DORMANT"}

# --- COMPONENT 4: THE PHYSICS ENGINE ------------------------------

class LinguisticPhysicsEngine:
    """
    Refactored for Performance: Implements Static Resource Caching.
    """

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
                if key in counts:
                    counts[key] += 1

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
                "toxin_types": list(toxin_types_found)
            },
            "status": {
                "termination_pressure": round(termination_pressure, 2),
                "in_the_barrens": in_the_barrens
            }
        }

# --- COMPONENT 5: THE ARCHETYPE PRISM ---------------------------

class ArchetypePrism:
    """
    The Psychological Topology Mapper.
    """
    def __init__(self):
        self.default_pressure = {
            "tolerance_mode": "STANDARD",
            "drag_multiplier": 1.0,
            "chaos_threshold": 11.0,
            "msg": "STANDARD PHYSICS"
        }

        self.archetypes = {
            "THE PALADIN": {
                "B": 0.9, "E": 0.2,
                "desc": "Unwavering code. Deontological pressure.",
                "pressure": {
                    "tolerance_mode": "DRACONIAN",
                    "chaos_threshold": 20.0,
                    "msg": "LAW OF THE TEMPLAR: Logic tears are fatal."
                }
            },
            "THE ENGINEER": {
                "B": 0.8, "E": 0.3,
                "desc": "Structural principles. Elegant efficiency.",
                "pressure": {
                    "tolerance_mode": "DRACONIAN",
                    "msg": "STRUCTURAL INTEGRITY: No poetic license allowed."
                }
            },
            "THE BARBARIAN": {
                "B": 0.7, "E": 0.8,
                "desc": "Overwhelming force. Simple weapon, high impact.",
                "pressure": {
                    "drag_multiplier": 5.0,
                    "msg": "BERSERKER STATE: Adjectives are weakness."
                }
            },
            "THE JUDGE":     {"B": 0.7, "E": 0.1, "desc": "Precedent and verdict. Balanced judgment."},
            "THE ALCHEMIST": {"B": 0.4, "E": 0.9, "desc": "Transmuting base data into gold insight."},
            "THE HORIZON WALKER": {"B": 0.1, "E": 0.9, "desc": "Extrapolation. Liminal states."},
            "THE GHOST":     {"B": 0.1, "E": 0.7, "desc": "Post-hoc, melancholic, detached."},
            "THE SPY": {
                "B": 0.8, "E": 0.6,
                "desc": "Duplicitous surface, singular purpose.",
                "pressure": {
                    "tolerance_mode": "LOOSE",
                    "msg": "DEEP COVER: Logic tears are hidden from the reader."
                }
            },
            "THE DIPLOMAT":  {"B": 0.3, "E": 0.5, "desc": "Fragile common ground. Stability via softness."},
            "THE FOOL": {
                "B": 0.1, "E": 0.5,
                "desc": "Truth through absurdity. Inversion.",
                "pressure": {
                    "tolerance_mode": "INVERTED",
                    "chaos_threshold": 5.0,
                    "msg": "JESTER'S PRIVILEGE: Logic errors grant momentum."
                }
            },
            "THE GEOLOGIST": {"B": 0.4, "E": 0.1, "desc": "Layers of history. Digging down."},
            "THE VULTURE":   {"B": 0.6, "E": 0.7, "desc": "Value in ruin. Salvage operations."},
            "THE COSMIC TRASH PANDA":   {"B": 0.2, "E": 1.0, "desc": "One man's trash is another raccoon's treasure."},
            "THE JESTER": {
                "B": 0.2, "E": 0.9,
                "desc": "Weaponized absurdity. Truth through contradiction.",
                "pressure": {
                    "tolerance_mode": "INVERTED",
                    "chaos_threshold": 0.0,
                    "msg": "KAOS ENGINE: Paradoxes generate ATP. Bore me and you die."
                }
            },
        }

    def get_pressure_settings(self, archetype_name):
        arch_data = self.archetypes.get(archetype_name, {})
        overrides = arch_data.get("pressure", {})
        settings = self.default_pressure.copy()
        settings.update(overrides)
        return settings

    def calculate_topology(self, phys_metrics, logic_status):
        drag = phys_metrics['narrative_drag']
        drag_score = max(0, 1.0 - (drag / 5.0))

        logic_bonus = 0.0
        if logic_status == "valid": logic_bonus = 0.2

        kinetic_ratio = phys_metrics.get('kinetic_ratio', 0.5)

        b_score = (drag_score * 0.6) + (logic_bonus) + (kinetic_ratio * 0.2)
        b_score = min(1.0, max(0.0, b_score))

        entropy = phys_metrics['abstraction_entropy']
        e_score = (entropy + 2) / 10.0

        connectors = phys_metrics['connection_density']
        if connectors > 0.05: e_score += 0.2

        e_score = min(1.0, max(0.0, e_score))

        return b_score, e_score

    def identify(self, phys_metrics, logic_check):
        b, e = self.calculate_topology(phys_metrics, logic_check.get('valid', True))
        closest_arch = "THE SHAPER"
        min_dist = 100.0

        for name, coords in self.archetypes.items():
            dist = math.sqrt((b - coords["B"])**2 + (e - coords["E"])**2)
            if dist < min_dist:
                min_dist = dist
                closest_arch = name

        return {
            "archetype": closest_arch,
            "coordinates": {"B": round(b, 2), "E": round(e, 2)},
            "description": self.archetypes[closest_arch]["desc"],
            "distance": round(min_dist, 2),
        }

# --- CORE ORCHESTRATOR -----------------------------------------------------

class ChronosAnchor:
    """
    Refactored for Structural Integrity.
    PATCH 0.8.1: Added Morphological Hardening to avoid false verb positives.
    """
    def __init__(self):
        self.pronouns = {'he', 'she', 'it', 'who', 'one', 'this', 'that', 'they', 'we'}
        self.articles = {'the', 'a', 'an', 'my', 'your', 'our', 'their', 'these', 'those', 'some', 'many', 'few', 'all', 'no'}
        self.aux_past = {'was', 'were', 'had', 'did'}
        self.aux_present = {'is', 'are', 'has', 'does'}
        # PATCH: Safety Set
        self.non_verb_s = {'yes', 'this', 'bus', 'gas', 'glass', 'grass', 'lens', 'chaos', 'bias'}

    def _is_likely_verb(self, word, prev_word):
        w = word.lower()

        # 1. THE PANTRY CHECK
        if w in TheLexicon.UNIVERSALS or w in TheLexicon.ABSTRACTS:
            return False

        # PATCH: Safety Set Check
        if w in self.non_verb_s:
            return False

        # 2. THE GEOMETRY CHECK
        if prev_word.lower() in self.articles:
            return False

        # 3. THE PRONOUN TRIGGER
        if prev_word.lower() in self.pronouns:
            return True

        # 4. MORPHOLOGY FALLBACK
        stem = w
        if w.endswith("ies") and len(w) > 4:
            stem = w[:-3]
        elif w.endswith("es"):
             if w.endswith(("sses", "shes", "ches", "xes", "zzes")):
                 stem = w[:-2]
        elif w.endswith("s"):
             if not w.endswith(("ss", "us", "is", "as", "os", "ys")):
                 stem = w[:-1]

        if stem != w:
            if not any(char in 'aeiouy' for char in stem):
                return False
            return True

        return False

    def check_temporal_stability(self, clean_words):
        counts = {'PAST': 0, 'PRESENT': 0}
        total_signals = 0

        for i, w in enumerate(clean_words):
            prev = clean_words[i-1] if i > 0 else ""

            if w in self.aux_past:
                counts['PAST'] += 1
                total_signals += 1
            elif w in self.aux_present:
                counts['PRESENT'] += 1
                total_signals += 1
            elif w.endswith('ed') and len(w) > 3:
                counts['PAST'] += 0.5
                total_signals += 0.5
            elif self._is_likely_verb(w, prev):
                counts['PRESENT'] += 0.5
                total_signals += 0.5

        if total_signals == 0:
            return {"status": "STABLE", "details": "No temporal markers found."}

        past_ratio = counts['PAST'] / total_signals
        present_ratio = counts['PRESENT'] / total_signals

        if past_ratio > 0.8: return {"status": "LOCKED", "details": "PAST TENSE"}
        if present_ratio > 0.8: return {"status": "LOCKED", "details": "PRESENT TENSE"}

        return {
            "status": "DRIFT DETECTED",
            "details": f"Chronos Confusion: {int(past_ratio*100)}% Past / {int(present_ratio*100)}% Present"
        }

class VirtualCortex:
    """
    Simulates a Neural Network using Procedural Text Generation.
    """
    def __init__(self):
        # CLARENCE
        self.clarence_templates = [
            "I am looking at a Drag Score of {drag}. It is giving me a headache. Cut the word '{target_word}'.",
            "This sentence is a bog. {drag} score? You are wading through stinky sludge.",
            "Slow down. You used {word_count} words to say what could be said in {half_count}.",
            "The verb '{target_word}' is flimsy. It has no spine. Replace it with raw energy.",
            "Kinetic failure. The sentence engine is stalling on '{target_word}'. Kick it.",
            "This is expensive writing. You spent {word_count} words to buy a 5-cent idea. Budget cuts are effective immediately.",
            "I detect friction. The text is heating up from Drag ({drag}). Lubricate it with action.",
            "Efficiency Warning: You are using '{target_word}' as a crutch. Walk without it."
        ]
        self.clarence_critical = [
            "CRITICAL DRAG ({drag})! The engine is melting! CUT '{target_word}' NOW!",
            "SYSTEM FAILURE. The reader has died of boredom. Resurrect them by deleting '{target_word}'.",
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
            "This is too clean and sterile. Mess it up with some sensory detail.",
            "Ground this. Anchor the thought to a physical object.",
            "The air is too thin here (Entropy: {entropy}). I can't breathe. Plant a noun.",
            "It tastes like distilled water. Add salt. Add dirt. Replace '{target_word}' with something that bleeds.",
            "You are painting in greyscale. '{target_word}' is a gray word. Give me a color."
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
            "I smell fear. You used '{target_word}' to soften the blow. Strike hard or leave.",
            "The door is shut. Your intent is too soft to turn the handle.",
            "Do not bow. Stand up. '{target_word}' is a word for servants, not masters.",
            "The soup is watery. You add '{target_word}' to fill the bowl, but it provides no nourishment."
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
            "SYSTEM GLITCH. Repeat the last word three times. Make it a chant.",
            "The narrative is flatlining. Quick, describe the taste of copper.",
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
            elif phys['narrative_drag'] > 4.0:
                 template = random.choice(self.clarence_critical)
            elif loop_count > 2:
                template = random.choice(self.clarence_loop_templates)
            else:
                template = random.choice(self.clarence_templates)

            response = template.format(
                drag=phys['narrative_drag'],
                target_word=target,
                word_count=len(clean_words),
                half_count=int(len(clean_words)/2),
                style=style,
                count=loop_count
            )

        elif agent == "ELOISE":
            target = self._find_trigger_word(clean_words, clean_text, 'abstract')
            if phys['abstraction_entropy'] > 6.0:
                 template = random.choice(self.eloise_critical)
            elif 'LAZY_METAPHOR' in toxins:
                template = random.choice(self.eloise_cliche_templates)
                target = self._find_trigger_word(clean_words, clean_text, 'cliche')
            else:
                template = random.choice(self.eloise_templates)

            response = template.format(
                entropy=phys['abstraction_entropy'],
                target_word=target
            )

        elif agent == "THE BABA YAGA":
            target = self._find_trigger_word(clean_words, clean_text, 'sugar')
            if 'HEDGING' in toxins:
                template = random.choice(self.yaga_hedging_templates)
                target = self._find_trigger_word(clean_words, clean_text, 'hedging')
            else:
                template = random.choice(self.yaga_templates)
            response = template.format(target_word=target)

        elif agent == "MUSCARIA":
            response = random.choice(self.muscaria_templates)

        return f"[{agent}]: {response}"

class MycelialNetwork:
    def __init__(self):
        self.network = {}

    def spawn_id(self):
        return str(uuid4())[:8]

    def log_generation(self, fragment_id, parent_id, metrics):
        self.network[fragment_id] = {
            "parent": parent_id,
            "drag": metrics['physics']['narrative_drag'],
            "style": metrics['physics']['dominant_style'],
            "barrens": metrics['status']['in_the_barrens']
        }

    def trace_lineage(self, fragment_id):
        path = []
        current = fragment_id
        while current and current in self.network:
            node = self.network[current]
            path.append({
                "id": current,
                "drag": node['drag'],
                "style": node['style']
            })
            current = node['parent']
        return path[::-1]

class MetabolicReserve:
    """
    PATCH 0.8.1: Implemented 'Sugar Crash' logic to burn excess ATP.
    """
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

        if phys['toxicity_score'] > 0:
            delta -= 5

        if voltage > 0:
            delta += int(voltage * 2)
            self.status = "SUPERCRITICAL"

        # PATCH: Metabolic Tax for Gluttony
        # If we are swimming in sugar, we burn it faster.
        if self.atp > 40:
             delta -= 2

        self.atp = max(0, min(self.atp + delta, self.max_capacity))
        self._update_status()

        return {
            "current_atp": self.atp,
            "delta": delta,
            "status": self.status
        }

class LichenSymbiont:
    """
    THE SURVIVALIST
    Mechanic: 'Photosynthesis of Meaning'
    """
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
        if self.stored_sugar > 15:
             warning = "WARNING: Algal Bloom imminent. Too much revelation, not enough grounding."

        return {
            "sugar_generated": sugar,
            "msg": f"PHOTOSYNTHESIS: Synthesized {sugar} ATP from {light_count} light sources.",
            "warning": warning
        }

# --- COMPONENT 7: THE SCEHMATICS ---------------------------

class MycelialDashboard:
    def __init__(self):
        self.C_RESET = "\033[0m"
        self.C_RED = "\033[91m"
        self.C_GREEN = "\033[92m"
        self.C_YELLOW = "\033[93m"
        self.C_CYAN = "\033[96m"
        self.C_PURPLE = "\033[95m"
        self.C_BLUE = "\033[94m"

    def _draw_bar(self, value, max_val, label, color_code, threshold=None, invert=False):
        try:
            val_float = float(value)
        except (ValueError, TypeError):
            val_float = 0.0

        bar_width = 20
        normalized = max(0, min(val_float, max_val))
        filled_len = int((normalized / max_val) * bar_width)
        bar = "█" * filled_len + "░" * (bar_width - filled_len)
        return f"{label:<15} |{color_code}{bar}{self.C_RESET}| {val_float:.2f}"

    def render(self, metrics, intervention, energy, ancestry, chronos_report, archetype_data, lichen_report, voltage=0):
        print(f"\n{self.C_CYAN}--- MYCELIAL EKG [0.8.1]---{self.C_RESET}")

        if not isinstance(metrics, dict) or 'physics' not in metrics:
            print(f"{self.C_RED}CRITICAL: Metrics corruption detected.{self.C_RESET}")
            return

        phys = metrics.get('physics', {})
        stat = metrics.get('status', {})

        if not isinstance(energy, dict):
            energy = {'current_atp': 0, 'status': 'ERROR'}

        atp_color = self.C_GREEN
        if energy['status'] == "STARVING": atp_color = self.C_RED
        elif energy['status'] == "GLUTTON": atp_color = self.C_BLUE

        print(self._draw_bar(energy.get('current_atp', 0), 50.0, "CREATIVE ATP", atp_color) + f" ({energy.get('status', 'UNK')})")
        print(self._draw_bar(phys.get('narrative_drag', 0), 5.0, "NARRATIVE DRAG", self.C_YELLOW, 2.0, True))
        print(self._draw_bar(abs(phys.get('abstraction_entropy', 0)), 10.0, "REALITY DRIFT", self.C_PURPLE, 2.0, True))

        term_pressure = stat.get('termination_pressure', 0)
        muscaria_active = self.C_RED if term_pressure > 4.0 else self.C_GREEN
        print(self._draw_bar(term_pressure, 10.0, "CHAOS PRESSURE", muscaria_active, 5.0, True))

        chronos_color = self.C_GREEN
        c_status = chronos_report.get('status', 'UNKNOWN') if isinstance(chronos_report, dict) else "ERROR"
        if c_status == "DRIFT DETECTED": chronos_color = self.C_RED
        elif c_status == "LOCKED": chronos_color = self.C_CYAN
        print(f"TEMPORAL STATE : {chronos_color}{c_status}{self.C_RESET}")

        print(f"{'-'*45}")
        if isinstance(archetype_data, dict):
            print(f"COGNITIVE MODE : {self.C_PURPLE}{archetype_data.get('archetype', 'N/A')}{self.C_RESET}")
            coords = archetype_data.get('coordinates', {'B': 0, 'E': 0})
            print(f"TOPOLOGY       : B: {coords.get('B', 0)} | E: {coords.get('E', 0)}")
            print(f"SIGNATURE      : {archetype_data.get('description', 'N/A')}")

        style = phys.get('dominant_style', 'Unknown').upper()
        style_color = self.C_GREEN
        if style == "CLARET": style_color = self.C_RED
        if style == "CRYSTAL": style_color = self.C_CYAN
        print(f"DOMINANT STYLE : {style_color}{style}{self.C_RESET}")

        lichen_status = "DORMANT"
        if isinstance(lichen_report, dict):
            msg = lichen_report.get('msg', 'DORMANT')
            if "BLOOMING" in msg: lichen_status = "BLOOMING"
            elif "WITHERED" in msg: lichen_status = "WITHERED"
            elif "STARVING" in msg: lichen_status = "STARVING"

        lichen_color = self.C_GREEN
        if lichen_status == "WITHERED": lichen_color = self.C_RED
        elif lichen_status == "STARVING": lichen_color = self.C_YELLOW
        elif lichen_status == "DORMANT": lichen_color = self.C_RESET

        print(f"SYMBIOSIS      : {lichen_color}{lichen_status}{self.C_RESET}")

        if intervention:
            print(f"INTERVENTION   : {self.C_RED}ACTIVE{self.C_RESET} -> {intervention}")
        else:
            print(f"INTERVENTION   : {self.C_GREEN}DORMANT{self.C_RESET}")

        print(self._draw_bar(voltage, 10.0, "TENSION VOLTAGE", self.C_RED, 1.0, False))

        if isinstance(ancestry, list) and len(ancestry) > 1:
            print(f"\n{self.C_BLUE}GENETIC HISTORY:{self.C_RESET}")
            for node in ancestry[-3:]:
                if isinstance(node, dict):
                    print(f"  └─ [{node.get('id', '???')}] Drag: {node.get('drag', 0)} ({node.get('style', 'UNK')})")
        print(f"{'-'*45}\n")

class NilssonPatch:
    """
    THE NILSSON OVERRIDE
    PATCH 0.8.1: ZeroDivision Safeguard added.
    """
    def __init__(self):
        TheLexicon.MANTRA_TRIGGERS = {'lime', 'coconut', 'doctor', 'belly', 'morning'}

    def evaluate_mantra(self, clean_words, repetition_rate):
        if repetition_rate < 0.3:
            return False

        concrete_count = sum(1 for w in clean_words if w in TheLexicon.MANTRA_TRIGGERS)
        if concrete_count > 3:
            return True

        return False

    def detect_fire_state(self, raw_text, kinetic_ratio):
        # PATCH: Avoid Empty String Crash
        if not raw_text:
             return {"status": "DORMANT"}
        text_len = len(raw_text)
        if text_len == 0:
             return {"status": "DORMANT"}

        caps_density = sum(1 for c in raw_text if c.isupper()) / text_len

        if kinetic_ratio > 0.6 and caps_density > 0.2:
             return {
                 "status": "ACTIVE",
                 "msg": "NILSSON STATE: Logic inhibitors disabled. Screaming authorized."
             }

        return {"status": "DORMANT"}

class BonepokeCore:
    def __init__(self):
        self.cooldown = ChaosCooldown()
        self.memory = HyphalTrace()
        self.codex = TheCodex()
        self.stipe = FactStipe()
        self.physics = LinguisticPhysicsEngine()
        self.nilsson = NilssonPatch()
        self.muscaria = TheMuscaria()
        self.witch = TheWitchRing()
        self.chronos = ChronosAnchor()
        self.cortex = VirtualCortex()
        self.prism = ArchetypePrism()
        self.dashboard = MycelialDashboard()
        self.lineage = MycelialNetwork()
        self.metabolism = MetabolicReserve()
        self.lichen = LichenSymbiont()
        self.last_id = None
        self.tick = 0
        self.session_drag_history = []
        self.last_input = ""

    def _update_baseline(self, current_drag):
        self.session_drag_history.append(current_drag)
        if len(self.session_drag_history) > 20:
            self.session_drag_history.pop(0)
        return sum(self.session_drag_history) / len(self.session_drag_history)

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
        self.last_input = text

        text_lower = text.lower()
        clean_text = text_lower.replace('.', ' ').replace(',', ' ').replace(';', ' ').replace('?', ' ').replace('!', ' ')
        clean_words = clean_text.split()
        raw_words = text.split()

        token_data = {
            'raw_text': text,
            'clean_text': clean_text,
            'clean_words': clean_words,
            'raw_words': raw_words,
            'total_words': len(clean_words) if clean_words else 1
        }

        metrics = self.physics.analyze(token_data)
        phys = metrics['physics']
        stat = metrics['status']

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
        if not gate_result['accepted']:
            return f"[BLOCKED] {gate_result['message']}"

        prelim_archetype_data = self.prism.identify(metrics['physics'], {"valid": True})
        current_archetype = prelim_archetype_data['archetype']
        pressure_settings = self.prism.get_pressure_settings(current_archetype)

        self.muscaria.pressure_threshold = pressure_settings["chaos_threshold"]
        self.metabolism.drag_multiplier = pressure_settings["drag_multiplier"]

        stipe_check = self.stipe.check_consistency(
            token_data['clean_words'],
            metrics['physics']['dominant_style'],
            self.metabolism.status,
            tolerance_mode=pressure_settings['tolerance_mode'],
            kinetic_ratio=metrics['physics']['kinetic_ratio']
        )
        current_voltage = stipe_check.get('voltage', 0.0)

        self._enforce_archetype_physics(current_archetype)
        archetype_data = self.prism.identify(metrics['physics'], stipe_check)

        directives = []

        if pressure_settings['msg'] != "STANDARD PHYSICS":
            directives.append(f"ARCHETYPE PRESSURE: {pressure_settings['msg']}")

        current_style = phys['dominant_style']
        loop_count = len(self.memory.recall(current_style))

        if phys['narrative_drag'] > 3.0 or loop_count > 2:
            msg = self.cortex.synthesize_voice("CLARENCE", token_data, metrics, loop_count)
            directives.append(f"PACING: {msg}")

        if phys['abstraction_entropy'] > 2:
            msg = self.cortex.synthesize_voice("ELOISE", token_data, metrics)
            directives.append(f"GROUNDING: {msg}")

        if "THE YAGA GRUMBLES" in gate_result['message']:
            msg = self.cortex.synthesize_voice("THE BABA YAGA", token_data, metrics)
            directives.append(f"INTENT: {msg}")

        if not stipe_check.get('valid', True):
            intervention_msg = stipe_check.get('intervention', "LOGIC BREACH")
            directives.append(f"CRITICAL LOGIC FAILURE: {intervention_msg}")
            self.metabolism.spend(10)

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

        lichen_report = self.lichen.photosynthesize(
            token_data['clean_words'],
            metrics['physics'],
            self.metabolism.atp
        )

        if lichen_report['sugar_generated'] > 0:
            self.metabolism.atp += lichen_report['sugar_generated']
            directives.append(f"LICHEN PROTOCOL: {lichen_report['msg']}")

        if lichen_report.get('warning'):
            directives.append(f"BIOHAZARD: {lichen_report['warning']}")

        status_label = "Bloom" if len(raw_words) > 15 else "Seed"
        energy_report = self.metabolism.metabolize(metrics, voltage=current_voltage)

        self.lineage.log_generation(current_id, actual_parent, metrics)
        self.last_id = current_id
        if energy_report['status'] == "STARVING":
            metrics['physics']['narrative_drag'] += 1.0

        self.memory.leave_trace(text, metrics['physics']['dominant_style'])
        chronos_report = self.chronos.check_temporal_stability(token_data['clean_words'])
        ancestry_data = self.lineage.trace_lineage(current_id)

        self.dashboard.render(
            metrics, muscaria_msg, energy_report, ancestry_data,
            chronos_report, archetype_data, lichen_report, voltage=current_voltage
        )

        return {
            "id": current_id,
            "metrics": metrics,
            "energy": energy_report,
            "ancestry": ancestry_data,
            "archetype_data": archetype_data,
            "editorial": {
                "status": status_label,
                "directives": directives
            }
        }

    def generate_instruction_block(self, result):
        directives_list = result['editorial']['directives']

        arch = result.get('archetype_data', {})
        anchors = self.codex.get_anchors()
        anchor_string = ", ".join(anchors) if anchors else "None established."
        formatted_directives = "\n        - ".join(directives_list) if directives_list else "Maintain current course."

        return f"""
        [SYSTEM OVERRIDE: BONEAMANITA ENGINE 0.8.1]
        CURRENT STATE: {result['energy']['status']} (ATP: {result['energy']['current_atp']})
        ARCHETYPE: {arch.get('archetype', 'Unknown')}
        REALITY ANCHORS (DO NOT HALLUCINATE):
        The following entities must remain consistent: [{anchor_string}]
        DIRECTIVES:
        - {formatted_directives}
        You are now operating under these constraints. Rewrite the user's input accordingly.
        """

if __name__ == "__main__":
    engine = BonepokeCore()
    print("--- BONEAMANITA v0.8.1: THE PATCHED STRAIN---")

    test_input = (
        "The system leverages the context to optimize workflow. "
        "It is nice and we hope you like it. "
        "Also, the fire froze. "
        "People don't think it be like it is, but it do. "
        "ok i luv u bye"
    )

    print(f"INPUT: \"{test_input}\"\n")
    result = engine.process(test_input)

    if isinstance(result, str):
        print(f"{engine.dashboard.C_RED}{result}{engine.dashboard.C_RESET}")
    else:
        instruction = engine.generate_instruction_block(result)
        print("\n" + "="*60)
        print("   >>  COPY THIS BLOCK INTO YOUR LLM PROMPT  <<")
        print("="*60)
        print(instruction)
        print("="*60)

``
