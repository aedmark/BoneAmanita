# ---------------------------------------------------------------------------
# BONEAMANITA 0.7 (A VARIANT STRAIN OF THE BONEPOKE ENGINE) - "The Jester)"
# Architects: James Taylor & Andrew Edmark | Auditors: SLASH
#
# "Feed the soil, poison the weak. Logic is the stalk; chaos is the spore. Don't forget your towel."
# ---------------------------------------------------------------------------

import time
import math
import random
from collections import Counter
from uuid import uuid4
import re

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
    HARD MEMORY
    Prevents 'Identity Bleed' by tracking "Entities".
    """
    def __init__(self):
        self.registry = {}
        self.ignore_list = {
            'The', 'A', 'An', 'It', 'He', 'She', 'They', 'We', 'I', 'You',
            'This', 'That', 'But', 'And', 'Or', 'If', 'When', 'Then',
            'System', 'Analysis', 'Metrics', 'Drag', 'Entropy'
        }

    def scan_for_entities(self, raw_words, current_tick):
        """
        Naive Named Entity Recognition using pre-split raw words.
        """
        for i, w in enumerate(raw_words):
            # Strip punctuation for clean checking
            clean_w = w.strip('.,;:"?!()')

            # Check for Capitalization
            if clean_w and clean_w[0].isupper():
                # RULE 1: Ignore the start of sentences (rough heuristic)
                if i > 0 and raw_words[i-1].endswith(('.', '!', '?')):
                    continue

                # RULE 2: Ignore common stopwords and engine terms
                if clean_w in self.ignore_list:
                    continue

                # RULE 3: Length Check (Avoid 'I', 'A')
                if len(clean_w) < 3:
                    continue

                # REGISTER THE ENTITY
                if clean_w not in self.registry:
                    self.registry[clean_w] = {'count': 0, 'first_seen_tick': current_tick}

                self.registry[clean_w]['count'] += 1

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
        # Format: 'word': {'DIMENSION': polarity}
        self.semantic_manifold = {
            # LUMENS
            'sun': {'LUMENS': 1}, 'beam': {'LUMENS': 1}, 'glare': {'LUMENS': 1},
            'noon': {'LUMENS': 1}, 'day': {'LUMENS': 1}, 'white': {'LUMENS': 1},
            'night': {'LUMENS': -1}, 'shadow': {'LUMENS': -1}, 'gloom': {'LUMENS': -1},
            'dark': {'LUMENS': -1}, 'pitch': {'LUMENS': -1}, 'midnight': {'LUMENS': -1},
            # DECIBELS
            'scream': {'DECIBELS': 1}, 'roar': {'DECIBELS': 1}, 'bang': {'DECIBELS': 1},
            'shout': {'DECIBELS': 1}, 'thunder': {'DECIBELS': 1}, 'crash': {'DECIBELS': 1},
            'silence': {'DECIBELS': -1}, 'hush': {'DECIBELS': -1}, 'quiet': {'DECIBELS': -1},
            'mute': {'DECIBELS': -1}, 'stillness': {'DECIBELS': -1},
            # VITALITY
            'breath': {'VITALITY': 1}, 'pulse': {'VITALITY': 1}, 'run': {'VITALITY': 1},
            'heart': {'VITALITY': 1}, 'live': {'VITALITY': 1}, 'awake': {'VITALITY': 1},
            'dead': {'VITALITY': -1}, 'corpse': {'VITALITY': -1}, 'tomb': {'VITALITY': -1},
            'dust': {'VITALITY': -1}, 'grave': {'VITALITY': -1}, 'static': {'VITALITY': -1},
            # THERMAL
            'fire': {'THERMAL': 1}, 'flame': {'THERMAL': 1}, 'burn': {'THERMAL': 1},
            'sweat': {'THERMAL': 1}, 'boil': {'THERMAL': 1}, 'heat': {'THERMAL': 1},
            'ice': {'THERMAL': -1}, 'frost': {'THERMAL': -1}, 'snow': {'THERMAL': -1},
            'freeze': {'THERMAL': -1}, 'shiver': {'THERMAL': -1}, 'cold': {'THERMAL': -1}
        }

    def inject_truth(self, word, dimension, polarity):
        if word not in self.semantic_manifold:
            self.semantic_manifold[word] = {}
        self.semantic_manifold[word][dimension] = polarity

    def check_consistency(self, clean_words, current_style, metabolic_status, kinetic_ratio=0.0, tolerance_mode="STANDARD"):
        strip_suffixes = ['ness', 'ing', 's', 'ed', 'ly']
        active_dimensions = {}
        trigger_words = {}

        for w in clean_words:
            # Identify the target concept (Word or Root)
            target = None
            if w in self.semantic_manifold:
                target = w
            else:
                # Attempt to strip suffix to find a known root
                for suffix in strip_suffixes:
                    if w.endswith(suffix):
                        candidate = w[:-len(suffix)]
                        if candidate in self.semantic_manifold:
                            target = candidate
                            break

            # Map Dimensions if found
            if target:
                for dim, polarity in self.semantic_manifold[target].items():
                    if dim not in active_dimensions:
                        active_dimensions[dim] = set()
                        trigger_words[dim] = {1: [], -1: []}

                    active_dimensions[dim].add(polarity)
                    trigger_words[dim][polarity].append(w)

        # 2. Detect Reality Tears & Calculate Voltage
        violations = []
        voltage = 0.0 # New Metric: The power of the contradiction

        for dim, polarities in active_dimensions.items():
            if 1 in polarities and -1 in polarities:
                # We have a collision (e.g., Hot + Cold)
                pos_words = ", ".join(trigger_words[dim][1])
                neg_words = ", ".join(trigger_words[dim][-1])

                # VSL CALCULATION:
                # If the text is moving fast (High Kinetic Ratio), this is leverage.
                # If the text is standing still, it is just a lie.
                if kinetic_ratio > 0.4:
                    voltage += 5.0
                    violations.append(f"PARADOX IGNITED [{dim}]: '{pos_words}' colliding with '{neg_words}' at high velocity.")
                else:
                    violations.append(f"LOGIC TEAR [{dim}]: Static contradiction detected.")

        # 3. ADJUDICATE LOGIC (The Saprophyte Switch)
        if violations:
            # If we generated Voltage (Good Instability)
            if voltage > 0:
                 return {
                    "valid": True, # It is valid because it is powerful
                    "voltage": voltage,
                    "intervention": f"VOLATILE SEMANTIC LEVERAGE: Harvested {voltage} Voltage from {dim} paradox."
                }

            # If we just broke logic without moving (Bad Instability)
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
    Injects chaos when the narrative becomes stagnant.
    """
    def __init__(self):
        self.boredom_pressure = 0.0
        self.pressure_threshold = 11.0
        self.disruptions = [
            "VIBE CHECK: Open a window. Describe the air or the light.",
            "CUT THE CHEESE: Introduce a smell or temperature change immediately.",
            "THE PIVOT: Shift the perspective slightly. Who is watching?",
            "NON-SEQUITUR: Say something goofy to throw off the boredom.",
            "SURREALIST: Replace an abstract concept with something weird.",
            "SIMPLIFICATION: Say the same thing, but in half the words.",
            "THE LIZARD KING: Raise the stakes. A threat has entered.",
            "SENSORY ANCHOR: What does the surface feel like? Rough or smooth?",
        ]

    def check_for_boredom(self, metrics):
        if not isinstance(metrics, dict) or 'physics' not in metrics:
            return False

        drag = metrics['physics'].get('narrative_drag', 0)
        repetition = metrics['physics'].get('repetition_rate', 0)
        abstraction = metrics['physics'].get('abstraction_entropy', 0)

        pressure_increase = (drag * 0.2) + (repetition * 2.0) + (max(0, abstraction) * 0.1)
        self.boredom_pressure += pressure_increase

        if self.boredom_pressure > self.pressure_threshold:
            return True
        return False

    def trigger_disruption(self, ancestry_data):
        self.boredom_pressure = 0.0
        # SAFETY CHECK: Ensure ancestry data is valid
        if not ancestry_data or not isinstance(ancestry_data, list):
            return "MUSCARIA: INVENT A NEW COLOR."

        # SAFETY CHECK: Ensure elements are dicts
        valid_nodes = [n for n in ancestry_data if isinstance(n, dict)]
        if not valid_nodes:
             return "MUSCARIA: THE PAST IS GONE. INVENT A NEW SOUND."

        if len(valid_nodes) > 1:
            ancestor = valid_nodes[-2]
        else:
            ancestor = valid_nodes[0]

        return f"VERSE JUMP: The echo of '{ancestor.get('id', 'UNK')}' bleeds through. Re-introduce a discarded object."

# --- COMPONENT 3: The Witch Ring -----------------------------------

class TheWitchRing:
    """
    THE GATEKEEPER
    """
    def __init__(self):
        self.cliches = {'once upon a time', 'dark and stormy', 'fix this'}
        self.sycophancy = {'please', 'sorry', 'can you', 'assist'}
        self.connectors = {'we', 'us', 'together', 'love', 'kind', 'help'}

    def evaluate_intent(self, clean_words, metrics):
        count = len(clean_words)
        phys = metrics['physics']

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
        sugar_count = sum(1 for w in clean_words if w in self.sycophancy)
        if sugar_count > 0 and count < 12:
             return {"accepted": True, "message": "THE YAGA GRUMBLES: Too much sugar, not enough meat."}

        return {"accepted": True, "message": "DORMANT"}

# --- COMPONENT 4: THE PHYSICS ENGINE ------------------------------

class LinguisticPhysicsEngine:
    """
    Analyzes text properties using 'Bonepoke' data profiles and contextual verb analysis.
    """
    def __init__(self):
        # 1. Concrete Universals
        self.universals = {
            'hand', 'eye', 'breath', 'skin', 'voice', "air", "cloth",
            'stone', 'light', 'water', 'rain', 'mud', 'dirt', 'wind',
            'wood', 'grain', 'iron', 'clay', 'paper', 'glass', 'fabric',
            'door', 'key', 'roof', 'floor', 'chair', 'table', 'wall',
            'path', 'road', 'horizon', 'shadow', 'weight', 'anchor'
        }

        # 2. Abstract Concepts
        self.abstracts = {
            'system', 'protocol', 'sequence', 'vector', 'node', 'context',
            'layer', 'matrix', 'manifold', 'substrate', 'perspective', 'framework',
            'logic', 'metric', 'concept', 'theory', 'analysis'
        }
        self.brand_safe = {'system', 'bonepoke', 'shimmer', 'lattice', 'muscaria'}

        # 3. Verbs
        self.kinetic_verbs = {
            'run', 'ran', 'hit', 'break', 'broke', 'broken',
            'take', 'took', 'make', 'made', 'press', 'build', 'built',
            'weave', 'wove', 'cut', 'throw', 'threw', 'drive', 'drove',
            'lift', 'carry', 'place', 'hold', 'turn', 'open', 'close'
        }
        self.stative_verbs = {'is', 'are', 'was', 'were', 'seem', 'appear', 'have', 'has', 'consist'}

        # 4. Stylistic Profiles
        self.styles = {
            'Moss': {'layer', 'nuance', 'deep', 'root', 'grow', 'slow'},
            'Crystal': {'logic', 'define', 'metric', 'clear', 'structure', 'frame'},
            'Timber': {'build', 'weight', 'wood', 'grain', 'solid', 'beam', 'floor'},
            'Lattice': {'foundation', 'structure', 'design', 'plan', 'support', 'connect'},
            'Claret': {'ache', 'human', 'mess', 'love', 'maybe', 'bruise', 'honest'}
        }

        self.connectors = {'we', 'you', 'us', 'together', 'share'}
        self.self_refs = {'i', 'me', 'my', 'mine'}
        self.slang = {'vibe', 'trash', 'gonzo', 'wild', 'weird', 'mess', 'glitter', 'swamp'}

        # --- MORPHOLOGICAL RULES ---
        self.abstract_suffixes = ('ness', 'ity', 'tion', 'ment', 'ism', 'ence', 'ance', 'logy')
        self.kinetic_suffixes = ('ing',)

        # 5. THE TOXICITY MAP
        self.toxic_patterns = {
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

        self.regex_harvester()

    def regex_harvester(self):

        self.flat_penalty_map = {}
        all_toxins = set()

        for category, phrases in self.toxic_patterns.items():
            for phrase, weight in phrases.items():
                self.flat_penalty_map[phrase] = weight
                all_toxins.add(phrase)

        sorted_toxins = sorted(list(all_toxins), key=len, reverse=True)
        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted_toxins) + r')\b'
        self.toxin_regex = re.compile(pattern_str, re.IGNORECASE)

    def _classify_token(self, w, next_word):
        """
        Determines the physics category of a token using Mercy Rules.
        Returns: 'KINETIC', 'STATIVE', 'UNIVERSAL', 'ABSTRACT', 'SLANG', 'CONNECTOR', 'SELF_REF', or None.
        """
        # A. VERB PHYSICS (The Motor)
        if w in self.stative_verbs:
            # MERCY RULE 1: Auxiliary + Progressive (e.g., "was running")
            if next_word.endswith('ing'): return 'KINETIC'
            # MERCY RULE 2: Copula + Universal (e.g., "is stone")
            elif next_word in self.universals: return 'KINETIC'
            # FALLBACK: The Crutch (True Stative)
            return 'STATIVE'

        if w in self.kinetic_verbs or w.endswith('ed'): return 'KINETIC'
        if w.endswith(self.kinetic_suffixes): return 'KINETIC'

        # B. NOUN/CONCEPT PHYSICS (The Mass)
        if w in self.universals: return 'UNIVERSAL'

        # Check specific abstract list first, then morphology
        if w in self.abstracts:
            if w not in self.brand_safe: return 'ABSTRACT'
            else: return None # Brand safe words are neutral

        if w.endswith(self.abstract_suffixes): return 'ABSTRACT'

        # C. FLAVOR TEXT
        if w in self.slang: return 'SLANG'
        if w in self.connectors: return 'CONNECTOR'
        if w in self.self_refs: return 'SELF_REF'

        return None

    def analyze(self, token_data):
        """
        Modified to accept centralized token_data.
        Implements The Integrated Pinker Scan (Refactored).
        """
        words = token_data['clean_words']
        clean_text_for_regex = token_data['clean_text']
        total_words = token_data['total_words']

        # Initialize counters (lowercase keys to match return values)
        counts = {
            'kinetic': 0, 'stative': 0, 'universal': 0,
            'abstract': 0, 'slang': 0, 'connector': 0, 'self_ref': 0
        }
        style_scores = {k: 0 for k in self.styles}

        # --- SINGLE PASS LOOP (The Integrated Pinker Scan) ---
        for i, w in enumerate(words):
            # Look-Ahead Logic
            next_word = words[i+1] if i + 1 < len(words) else ""

            # Physics Classification
            category = self._classify_token(w, next_word)
            if category:
                key = category.lower()
                if key in counts:
                    counts[key] += 1

            # Style Scoring (Orthogonal check)
            for style, markers in self.styles.items():
                if w in markers: style_scores[style] += 1

        # --- TOXICITY CHECK (Regex) ---
        toxicity_score = 0.0
        toxin_types_found = set()

        matches = self.toxin_regex.findall(clean_text_for_regex)
        for match in matches:
            weight = self.flat_penalty_map.get(match, 0)
            toxicity_score += weight
            if weight >= 3.0: toxin_types_found.add("CORP/CLICHÉ")
            else: toxin_types_found.add("HEDGING")

        # --- METRIC CALCULATION ---
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
    Updated to include Physics Pressure Settings (formerly PressureMatrix).
    """
    def __init__(self):
        # Default Physics Profile
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
                    "chaos_threshold": 0.0, # Always allows chaos
                    "msg": "KAOS ENGINE: Paradoxes generate ATP. Bore me and you die."
                }
            },
        }

    def get_pressure_settings(self, archetype_name):
        """
        Retrieves physics settings for the archetype, falling back to defaults.
        """
        arch_data = self.archetypes.get(archetype_name, {})
        overrides = arch_data.get("pressure", {})

        # Merge defaults with overrides
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

class EditorialTranslator:
    def __init__(self, physics_engine):
        self.engine = physics_engine

    def generate_feedback(self, text, metrics, archetype_data=None):
        phys = metrics['physics']
        stat = metrics['status']

        status = "Seed (Draft)"
        if len(text.split()) > 15: status = "Bloom (Developing)"
        if phys['connection_density'] > 0.05 and phys['narrative_drag'] < 1.5: status = "Fruit (Polished)"

        feedback_notes = {}

        if phys['narrative_drag'] > 3.5:
            feedback_notes['Pacing'] = f"CLARENCE: Structure failing (Drag: {phys['narrative_drag']}). High resistance detected."
        elif phys['narrative_drag'] > 2.0:
            feedback_notes['Pacing'] = f"CLARENCE: Pace is deliberate (Drag: {phys['narrative_drag']}). Monitor for stagnation."
        else:
            feedback_notes['Pacing'] = "Clarence is satisfied with the kinetic flow."

        if phys['abstraction_entropy'] > 2:
            feedback_notes['Grounding'] = f"ELOISE: Atmosphere is thin (Entropy: {phys['abstraction_entropy']}). Needs sensory anchors."
        else:
            feedback_notes['Grounding'] = "Eloise feels the texture is solid."

        toxins = phys.get('toxin_types', [])
        if 'CORP/CLICHÉ' in toxins:
             feedback_notes['Purity'] = "CLARENCE ALERT: Corporate contaminants detected."
        elif 'LAZY_METAPHOR' in toxins:
             feedback_notes['Purity'] = "ELOISE SAYS: That metaphor is dead. Bury it."
        elif 'HEDGING' in toxins:
             feedback_notes['Purity'] = "THE YAGA: You are hedging. Commit to the statement."

        return {
            "status": status,
            "feedback": feedback_notes
        }

class ChronosAnchor:
    def __init__(self):
        self.pronouns = {'he', 'she', 'it', 'who', 'one', 'this', 'that'}
        self.articles = {'the', 'a', 'an', 'my', 'your', 'our', 'their'}
        self.aux_past = {'was', 'were', 'had', 'did'}
        self.aux_present = {'is', 'are', 'has', 'does'}

    def _is_likely_verb(self, word, prev_word):
        w = word.lower()
        safe_list = {
            'always', 'yes', 'news', 'lens', 'physics', 'mathematics',
            'chaos', 'series', 'species', 'analysis', 'crisis', 'thesis',
            'canvas', 'status', 'various', 'previous', 'serious', 'nervous',
            'focus', 'bias', 'basis', 'virus', 'corpus', 'stories', 'movies'
        }
        if w in safe_list: return False

        noun_markers = self.articles.union({'these', 'those', 'some', 'many', 'few', 'all', 'no'})
        if prev_word in noun_markers: return False

        if prev_word in self.pronouns: return True

        stem = w
        if w.endswith("ies") and len(w) > 4: stem = w[:-3]
        elif w.endswith("es"):
             if w.endswith(("sses", "shes", "ches", "xes", "zzes")): stem = w[:-2]
        elif w.endswith("s"):
             if not w.endswith(("ss", "us", "is", "as", "os", "ys")): stem = w[:-1]

        if stem != w:
            if not any(char in 'aeiouy' for char in stem): return False
        return stem != w

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
    UPDATED: Includes 'Expansion Pack' templates and 'Severity Logic'.
    """
    def __init__(self, physics_ref, witch_ref):
        self.physics_ref = physics_ref
        self.witch_ref = witch_ref

        # --- CLARENCE: THE ARCHITECT (Structure & Economy) ---
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
            "You are repeating yourself. Break the '{style}' pattern.",
            "I am bored. We have been stuck in this {style} loop for too long."
        ]

        # --- ELOISE: THE GARDENER (Senses & Atmosphere) ---
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

        # --- THE BABA YAGA: THE WITCH (Intent & Power) ---
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

        # --- MUSCARIA: THE CHAOS ENGINE ---
        self.muscaria_templates = [
            "BOREDOM ALERT. The text is gray. Suddenly, a bird flies into the window. Write about that.",
            "VERSE JUMP. What if this room was underwater? How would the light move?",
            "SYSTEM GLITCH. Repeat the last word three times. Make it a chant.",
            "The narrative is flatlining. Quick, describe the taste of copper.",
            "Stop. Look up. What is the ugliest thing in your field of vision? Put it in the text."
        ]

    def _find_trigger_word(self, clean_words, clean_text, category):
        # Access the Truth directly from the source
        targets = set()

        if category == 'stative':
            targets = self.physics_ref.stative_verbs
        elif category == 'abstract':
            targets = self.physics_ref.abstracts
        elif category == 'sugar':
            targets = self.witch_ref.sycophancy
        elif category == 'corp':
            targets = set(self.physics_ref.toxic_patterns['CORP_SPEAK'].keys())
        elif category == 'cliche':
            targets = set(self.physics_ref.toxic_patterns['LAZY_METAPHOR'].keys())
        elif category == 'hedging':
            targets = set(self.physics_ref.toxic_patterns['WEAK_HEDGING'].keys())

        # Scan for the offender (Single Words)
        for w in clean_words:
            if w in targets: return w

        # Scan for Phrases
        if category in ['corp', 'cliche', 'hedging']:
             for phrase in targets:
                 if phrase in clean_text:
                     return phrase

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

        # --- CLARENCE LOGIC ---
        if agent == "CLARENCE":
            target = self._find_trigger_word(clean_words, clean_text, 'stative')

            # 1. Check for Toxicity First (Priority 1)
            if 'CORP/CLICHÉ' in toxins:
                 template = random.choice(self.clarence_corp_templates)
                 target = self._find_trigger_word(clean_words, clean_text, 'corp')

            # 2. Check for Critical Failure (Severity Logic)
            elif phys['narrative_drag'] > 4.0:
                 template = random.choice(self.clarence_critical)

            # 3. Check for Loops
            elif loop_count > 2:
                template = random.choice(self.clarence_loop_templates)

            # 4. Standard
            else:
                template = random.choice(self.clarence_templates)

            # Format Safety
            response = template.format(
                drag=phys['narrative_drag'],
                target_word=target,
                word_count=len(clean_words),
                half_count=int(len(clean_words)/2),
                style=style,
                count=loop_count
            )

        # --- ELOISE LOGIC ---
        elif agent == "ELOISE":
            target = self._find_trigger_word(clean_words, clean_text, 'abstract')

            # 1. Check for Critical Abstraction (Severity Logic)
            if phys['abstraction_entropy'] > 6.0:
                 template = random.choice(self.eloise_critical)

            # 2. Check for Cliches
            elif 'LAZY_METAPHOR' in toxins:
                template = random.choice(self.eloise_cliche_templates)
                target = self._find_trigger_word(clean_words, clean_text, 'cliche')

            # 3. Standard
            else:
                template = random.choice(self.eloise_templates)

            response = template.format(
                entropy=phys['abstraction_entropy'],
                target_word=target
            )

        # --- BABA YAGA LOGIC ---
        elif agent == "THE BABA YAGA":
            target = self._find_trigger_word(clean_words, clean_text, 'sugar')

            # 1. Check for Hedging
            if 'HEDGING' in toxins:
                template = random.choice(self.yaga_hedging_templates)
                target = self._find_trigger_word(clean_words, clean_text, 'hedging')

            # 2. Standard
            else:
                template = random.choice(self.yaga_templates)

            response = template.format(target_word=target)

        # --- MUSCARIA LOGIC ---
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
    def __init__(self, max_capacity=52):
        self.atp = 33
        self.max_capacity = max_capacity
        self.status = "STABLE"
        self.drag_multiplier = 1.0

    def spend(self, amount):
        self.atp = max(0, self.atp - amount)
        if self.atp < 6: self.status = "STARVING"
        elif self.atp > 40: self.status = "GLUTTON"
        else: self.status = "STABLE"
        return self.atp

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

        # THE SAPROPHYTE MECHANIC
        # Now 'voltage' is defined in this scope
        if voltage > 0:
            delta += int(voltage * 2)
            self.status = "SUPERCRITICAL"

        self.atp = max(0, min(self.atp + delta, self.max_capacity))

        if self.atp < 6: self.status = "STARVING"
        elif self.atp > 40: self.status = "GLUTTON"
        else: self.status = "STABLE"

        return {
            "current_atp": self.atp,
            "delta": delta,
            "status": self.status
        }

# --- COMPONENT 7: THE SCEHMATICS ---------------------------

class MycelialDashboard:
    """
    The Mycelial DASHBOARD
    """
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

    def render(self, metrics, intervention, energy, ancestry, chronos_report, archetype_data, voltage=0):
        print(f"\n{self.C_CYAN}--- MYCELIAL EKG ---{self.C_RESET}")

        # SAFETY CHECK: Ensure metrics is a dict
        if not isinstance(metrics, dict) or 'physics' not in metrics:
            print(f"{self.C_RED}CRITICAL: Metrics corruption detected.{self.C_RESET}")
            return

        phys = metrics.get('physics', {})
        stat = metrics.get('status', {})

        # SAFETY CHECK: Ensure energy is a dict
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

        if intervention:
            print(f"INTERVENTION   : {self.C_RED}ACTIVE{self.C_RESET} -> {intervention}")
        else:
            print(f"INTERVENTION   : {self.C_GREEN}DORMANT{self.C_RESET}")

        if intervention:
            print(f"INTERVENTION   : {self.C_RED}ACTIVE{self.C_RESET} -> {intervention}")
        else:
            print(f"INTERVENTION   : {self.C_GREEN}DORMANT{self.C_RESET}")
        print(self._draw_bar(voltage, 10.0, "TENSION VOLTAGE", self.C_RED, 1.0, False))

        # SAFETY CHECK: Ensure ancestry is a list of dicts
        if isinstance(ancestry, list) and len(ancestry) > 1:
            print(f"\n{self.C_BLUE}GENETIC HISTORY:{self.C_RESET}")
            for node in ancestry[-3:]:
                if isinstance(node, dict):
                    print(f"  └─ [{node.get('id', '???')}] Drag: {node.get('drag', 0)} ({node.get('style', 'UNK')})")
        print(f"{'-'*45}\n")

class BonepokeCore:
    def __init__(self):
        self.cooldown = ChaosCooldown()
        self.memory = HyphalTrace()
        self.codex = TheCodex()
        self.stipe = FactStipe()
        self.physics = LinguisticPhysicsEngine()
        self.editor = EditorialTranslator(self.physics)
        self.muscaria = TheMuscaria()
        self.witch = TheWitchRing()
        self.chronos = ChronosAnchor()
        self.cortex = VirtualCortex(self.physics, self.witch)
        self.prism = ArchetypePrism()
        self.dashboard = MycelialDashboard()
        self.lineage = MycelialNetwork()
        self.metabolism = MetabolicReserve()
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

        # -------------------------------------------------------------------
        # 0. CENTRALIZED TOKENIZATION (The Fuller Principle)
        # -------------------------------------------------------------------
        text_lower = text.lower()
        # Clean text for splitting (preserve some structure for regex if needed, but mostly clean)
        clean_text = text_lower.replace('.', ' ').replace(',', ' ').replace(';', ' ').replace('?', ' ').replace('!', ' ')
        clean_words = clean_text.split()
        raw_words = text.split() # Preserves case for Codex

        token_data = {
            'raw_text': text,
            'clean_text': clean_text, # For Regex
            'clean_words': clean_words, # For Physics/Metrics
            'raw_words': raw_words,      # For Codex
            'total_words': len(clean_words) if clean_words else 1
        }

        # 1. METRICS & PHYSICS
        metrics = self.physics.analyze(token_data)
        phys = metrics['physics']
        stat = metrics['status']

        # 2. IDENTITY GENERATION
        current_id = self.lineage.spawn_id()
        actual_parent = parent_id if parent_id else self.last_id

        # 3. MEMORY & GATEKEEPING
        self.codex.scan_for_entities(token_data['raw_words'], self.tick)
        gate_result = self.witch.evaluate_intent(token_data['clean_words'], metrics)

        if not gate_result['accepted']:
            return f"[BLOCKED] {gate_result['message']}"

        # 4. ARCHETYPE LOOP & STIPE CHECK
        prelim_archetype_data = self.prism.identify(metrics['physics'], {"valid": True})
        current_archetype = prelim_archetype_data['archetype']

        # Retrieve settings directly from the Prism
        pressure_settings = self.prism.get_pressure_settings(current_archetype)

        # Apply Global Physics Overrides
        self.muscaria.pressure_threshold = pressure_settings["chaos_threshold"]
        self.metabolism.drag_multiplier = pressure_settings["drag_multiplier"]

        stipe_check = self.stipe.check_consistency(
            token_data['clean_words'],
            metrics['physics']['dominant_style'],
            self.metabolism.status,
            tolerance_mode=pressure_settings['tolerance_mode'],
            kinetic_ratio=metrics['physics']['kinetic_ratio'] # Ensure you pass this too!
        )

        current_voltage = stipe_check.get('voltage', 0.0)

        archetype_data = self.prism.identify(metrics['physics'], stipe_check)
        self._enforce_archetype_physics(current_archetype)

        # 5. EDITORIAL & INTERVENTION
        current_style = metrics['physics']['dominant_style']
        recalled_echoes = self.memory.recall(current_style)
        loop_count = len(recalled_echoes)

        editorial = self.editor.generate_feedback(text, metrics, archetype_data)
        if pressure_settings['msg'] != "STANDARD PHYSICS":
            editorial['feedback']['ARCHETYPE_PRESSURE'] = f"SYSTEM: {pressure_settings['msg']}"

        # Virtual Cortex Synthesis
        if phys['narrative_drag'] > 3.0 or loop_count > 2:
            voice = self.cortex.synthesize_voice("CLARENCE", token_data, metrics, loop_count=loop_count)
            editorial['feedback']['Pacing'] = voice
        if phys['abstraction_entropy'] > 2:
            voice = self.cortex.synthesize_voice("ELOISE", token_data, metrics)
            editorial['feedback']['Grounding'] = voice
        if "THE YAGA GRUMBLES" in gate_result['message']:
             voice = self.cortex.synthesize_voice("THE BABA YAGA", token_data, metrics)
             editorial['feedback']['Intent'] = voice

        muscaria_msg = None
        if self.muscaria.check_for_boredom(metrics):
            if self.cooldown.is_ready(self.tick, force=stat['in_the_barrens']):
                ancestry_temp = self.lineage.trace_lineage(current_id)
                muscaria_msg = self.muscaria.trigger_disruption(ancestry_temp)
                self.metabolism.spend(5)
            else:
                muscaria_msg = self.cortex.synthesize_voice("MUSCARIA", token_data, metrics)

        if not stipe_check.get('valid', True):
            intervention_msg = stipe_check.get('intervention', "LOGIC BREACH")
            editorial['feedback']['CRITICAL_LOGIC'] = f"FACT STIPE ALERT: {intervention_msg}"
            self.metabolism.spend(10)

        # 6. FINALIZING
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
            chronos_report, archetype_data, voltage=current_voltage
        )

        return {
            "id": current_id,
            "metrics": metrics,
            "energy": energy_report,
            "ancestry": ancestry_data,
            "editorial": editorial,
            "intervention": muscaria_msg,
            "archetype_data": archetype_data
        }

    def generate_instruction_block(self, result):
        editorial = result['editorial']['feedback']
        arch = result.get('archetype_data', {})
        anchors = self.codex.get_anchors()
        anchor_string = ", ".join(anchors) if anchors else "None established."

        directives = []
        if "Pacing" in editorial: directives.append(f"Constraint: {editorial['Pacing']} (Fix the drag).")
        if "Grounding" in editorial: directives.append(f"Constraint: {editorial['Grounding']} (Add sensory details).")
        if result['intervention']: directives.append(f"CHAOS EVENT: {result['intervention']}")

        return f"""
        [SYSTEM OVERRIDE: BONEAMANITA ENGINE]
        CURRENT STATE: {result['energy']['status']} (ATP: {result['energy']['current_atp']})
        ARCHETYPE: {arch.get('archetype', 'Unknown')}
        REALITY ANCHORS (DO NOT HALLUCINATE):
        The following entities must remain consistent: [{anchor_string}]
        DIRECTIVES:
        - {" ".join(directives)}
        You are now operating under these constraints. Rewrite the user's input accordingly.
        """

if __name__ == "__main__":
    engine = BonepokeCore()
    print("--- BONEAMANITA v0.7: THE JESTER ---")

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
