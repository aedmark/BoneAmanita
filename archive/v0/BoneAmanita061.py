# # ---------------------------------------------------------------------------
# BONEAMANITA 0.6.1 (A VARIANT STRAIN OF THE BONEPOKE ENGINE) - "The Clean Sweep"
# Architects: James Taylor & Andrew Edmark | Auditors: SLASH, THE MYCELIAL MIRROR NETWORK, BONEPOKE
#
# "Feed the soil, poison the weak. Logic is the stalk; chaos is the spore. Mind the roots. Don't forget your towel."
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
        """
        Stores a memory fragment with its associated context.
        """
        self.current_tick += 1
        hyphae_packet = {
            "content": content,
            "context_tag": context_tag,
            "timestamp": self.current_tick
        }
        self.hyphae_stream.append(hyphae_packet)
        self._prune_old_memories()

    def recall(self, target_context):
        """
        Retrieves memories that match the current context or are very recent.
        """
        relevant_memories = []
        for mem in self.hyphae_stream:
            # Cognitive Rule: We remember things that fit the current mood or happened just seconds ago.
            is_recent = (self.current_tick - mem['timestamp']) < 3
            is_relevant = (mem['context_tag'] == target_context)

            if is_recent or is_relevant:
                relevant_memories.append(mem['content'])

        return relevant_memories

    def _prune_old_memories(self):
        """
        Removes memories exceeding the retention span.
        """
        if len(self.hyphae_stream) > self.retention_span:
            self.hyphae_stream.pop(0)

class TheCodex:
    """
    HARD MEMORY
    Prevents 'Identity Bleed' by tracking "Entities" and forcing them back into the prompt context.
    """
    def __init__(self):
        # Stores { 'EntityName': { 'count': int, 'first_seen_tick': int } }
        self.registry = {}
        # Common false positives for Proper Nouns
        self.ignore_list = {
            'The', 'A', 'An', 'It', 'He', 'She', 'They', 'We', 'I', 'You',
            'This', 'That', 'But', 'And', 'Or', 'If', 'When', 'Then',
            'System', 'Analysis', 'Metrics', 'Drag', 'Entropy'
        }

    def scan_for_entities(self, text, current_tick):
        """
        Naive Named Entity Recognition
        Looks for capitalized words that are NOT at the start of a sentence.
        """
        words = text.split()
        for i, w in enumerate(words):
            # Strip punctuation for clean checking
            clean_w = w.strip('.,;:"?!()')

            # Check for Capitalization
            if clean_w and clean_w[0].isupper():
                # RULE 1: Ignore the start of sentences (rough heuristic)
                if i > 0 and words[i-1].endswith(('.', '!', '?')):
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
        """
        Returns the Top 5 most relevant Entities to anchor the reality.
        """
        # Sort by frequency
        sorted_entities = sorted(
            self.registry.items(),
            key=lambda item: item[1]['count'],
            reverse=True
        )

        # Return the top 5 as a list
        return [k for k, v in sorted_entities[:5]]

class FactStipe:
    """
    DIMENSIONAL REALITY ANCHOR
    Logic: If a sentence contains words with opposing polarities in the same
    dimension (e.g., Light +1 and Light -1), a Reality Tear can occur.
    """
    def __init__(self):
        # SEMANTIC KERNEL
        # This is a "Compressed Language Model"
        # Format: 'word': {'DIMENSION': polarity}
        # Polarity: -1 (Low/Absent), 1 (High/Present)
        self.semantic_manifold = {
            # LUMENS (Light vs Dark)
            'sun': {'LUMENS': 1}, 'beam': {'LUMENS': 1}, 'glare': {'LUMENS': 1},
            'noon': {'LUMENS': 1}, 'day': {'LUMENS': 1}, 'white': {'LUMENS': 1},
            'night': {'LUMENS': -1}, 'shadow': {'LUMENS': -1}, 'gloom': {'LUMENS': -1},
            'dark': {'LUMENS': -1}, 'pitch': {'LUMENS': -1}, 'midnight': {'LUMENS': -1},

            # DECIBELS (Loud vs Quiet)
            'scream': {'DECIBELS': 1}, 'roar': {'DECIBELS': 1}, 'bang': {'DECIBELS': 1},
            'shout': {'DECIBELS': 1}, 'thunder': {'DECIBELS': 1}, 'crash': {'DECIBELS': 1},
            'silence': {'DECIBELS': -1}, 'hush': {'DECIBELS': -1}, 'quiet': {'DECIBELS': -1},
            'mute': {'DECIBELS': -1}, 'stillness': {'DECIBELS': -1},

            # VITALITY (Life vs Death)
            'breath': {'VITALITY': 1}, 'pulse': {'VITALITY': 1}, 'run': {'VITALITY': 1},
            'heart': {'VITALITY': 1}, 'live': {'VITALITY': 1}, 'awake': {'VITALITY': 1},
            'dead': {'VITALITY': -1}, 'corpse': {'VITALITY': -1}, 'tomb': {'VITALITY': -1},
            'dust': {'VITALITY': -1}, 'grave': {'VITALITY': -1}, 'static': {'VITALITY': -1},

            # THERMAL (Hot vs Cold)
            'fire': {'THERMAL': 1}, 'flame': {'THERMAL': 1}, 'burn': {'THERMAL': 1},
            'sweat': {'THERMAL': 1}, 'boil': {'THERMAL': 1}, 'heat': {'THERMAL': 1},
            'ice': {'THERMAL': -1}, 'frost': {'THERMAL': -1}, 'snow': {'THERMAL': -1},
            'freeze': {'THERMAL': -1}, 'shiver': {'THERMAL': -1}, 'cold': {'THERMAL': -1}
        }

    def inject_truth(self, word, dimension, polarity):
        """
        Allows the 'Personality' to teach the 'Engine' new physics during the session.
        """
        if word not in self.semantic_manifold:
            self.semantic_manifold[word] = {}
        self.semantic_manifold[word][dimension] = polarity

    def check_consistency(self, current_text, current_style, metabolic_status, tolerance_mode="STANDARD"):
        words = current_text.lower().replace('.', '').replace(',', '').split()
        strip_suffixes = ['ness', 'ing', 's', 'ed', 'ly']
        active_dimensions = {}
        trigger_words = {}

        for w in words:
            # Identify the target concept (Word or Root)
            target = None
            if w in self.semantic_manifold:
                target = w
            else:
                # Attempt to strip suffix to find a known root
                for suffix in strip_suffixes:
                    if w.endswith(suffix):
                        candidate = w[:-len(suffix)]
                        # Check if the stripped version is in our reality map
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
                    # We log the original word 'w' so the error message makes sense
                    trigger_words[dim][polarity].append(w)

        # 2. Detect Reality Tears
        violations = []
        for dim, polarities in active_dimensions.items():
            if 1 in polarities and -1 in polarities:
                pos_words = ", ".join(trigger_words[dim][1])
                neg_words = ", ".join(trigger_words[dim][-1])
                violations.append(f"LOGIC TEAR [{dim}]: Detected '{pos_words}' (+) alongside '{neg_words}' (-).")

        # 3. ADJUDICATE LOGIC
        if violations:
            # MODE A: DRACONIAN (The Paladin/Engineer)
            if tolerance_mode == "DRACONIAN":
                return {
                    "valid": False,
                    "errors": violations,
                    "intervention": f"ZERO TOLERANCE: {violations[0]} The Archetype forbids this contradiction."
                }

            # MODE B: INVERTED (The Fool)
            if tolerance_mode == "INVERTED":
                return {
                    "valid": True,
                    "intervention": "CHAOS HARVEST: Reality Tear accepted as source of insight."
                }

            # MODE C: LOOSE (The Spy/Diplomat)
            if tolerance_mode == "LOOSE":
                return {
                     "valid": True,
                     "intervention": "COGNITIVE DISSONANCE: Contradiction masked for cover."
                }

            # STANDARD FALLBACKS (Metabolic/Style)
            if current_style.upper() in ['CLARET', 'MOSS', 'MUSHROOM']:
                return {"valid": True, "intervention": "VERSE JUMP: Logic breach accepted as stylistic choice."}

            if metabolic_status == "GLUTTON":
                 return {"valid": True, "intervention": "REALITY BENDING: High Metabolic Reserve allows for this metaphor."}

            return {
                "valid": False,
                "errors": violations,
                "intervention": f"{violations[0]} You are too weak to break physics."
            }

        return {"valid": True}

class ChaosCooldown:
    """
    Prevents chaos from nuking the text every single turn.
    """
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
    Injects chaos when the narrative becomes stagnant. Note: These phrases are meant to be seeds for
    unique phrases the LLM will ideally generate on the fly that serve the same function.
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
        """
        Uses Pinker's clear metrics to calculate the 'Boredom Pressure'.
        """
        drag = metrics['physics']['narrative_drag']
        repetition = metrics['physics']['repetition_rate']
        abstraction = metrics['physics']['abstraction_entropy']

        # Boredom Formula: Slow (Drag) + Repetitive (Loop) + Confusing (Abstract)
        pressure_increase = (drag * 0.2) + (repetition * 2.0) + (max(0, abstraction) * 0.1)
        self.boredom_pressure += pressure_increase

        if self.boredom_pressure > self.pressure_threshold:
            return True
        return False

    def trigger_disruption(self, ancestry_data):
        """
        Accesses a 'Parallel Universe' (Previous Draft).
        """
        self.boredom_pressure = 0.0
        if not ancestry_data:
            return "MUSCARIA: INVENT A NEW COLOR."

        # Verse-Jump: Pull a concept from 3 turns ago
        # Grab the parent (2nd to last) or a random ancestor
        if len(ancestry_data) > 1:
            ancestor = ancestry_data[-2] # The Parent
        else:
            ancestor = ancestry_data[0] # The Original Seed
        return f"VERSE JUMP: The echo of '{ancestor['id']}' bleeds through. Re-introduce a discarded object from that timeline."

# --- COMPONENT 3: The Witch Ring -----------------------------------

class TheWitchRing:
    """
    THE GATEKEEPER
    She demands 'Meat' (Substance) over 'Sugar' (Politeness).
    """

    def __init__(self):
        self.cliches = {'once upon a time', 'dark and stormy', 'fix this'}
        # Empty pleading
        self.sycophancy = {'please', 'sorry', 'can you', 'assist'}
        # Connective tissue
        self.connectors = {'we', 'us', 'together', 'love', 'kind', 'help'}

    def evaluate_intent(self, text, metrics):
        words = text.split()
        count = len(words)
        phys = metrics['physics']

        # 1. DENSITY CHECK (The Meat Gate)
        meat_score = phys.get('kinetic', 0) + phys.get('universal', 0)
        density = meat_score / count if count > 0 else 0

        # Exception for Short & Dense (Aphorisms)
        if count < 5:
            if density >= 0.4:
                return {"accepted": True, "message": "EXCEPTION: High-Density Aphorism detected."}
            else:
                return {"accepted": False, "message": "THE YAGA: This is small and weak. Feed it."}

        # 2. LAZINESS CHECK
        if phys['narrative_drag'] > 4.0 and phys['connection_density'] < 0.01:
            return {"accepted": False, "message": "THE YAGA: This is lazy. It's just noise. Collapse it."}

        # 3. SUGAR CHECK
        # Calculate sugar (sycophancy) manually since metrics don't track it yet
        sugar_count = sum(1 for w in words if w.lower() in self.sycophancy)
        if sugar_count > 0 and count < 12:
             return {"accepted": True, "message": "THE YAGA GRUMBLES: Too much sugar, not enough meat."}

        return {"accepted": True, "message": "DORMANT"}

# --- COMPONENT 4: THE PHYSICS ENGINE ------------------------------

class LinguisticPhysicsEngine:
    """
    Analyzes text properties using 'Bonepoke' data profiles and contextual verb analysis.
    """
    def __init__(self):
        # 1. Concrete Universals (Grounding words)
        self.universals = {
            'hand', 'eye', 'breath', 'skin', 'voice', "air", "cloth",
            'stone', 'light', 'water', 'rain', 'mud', 'dirt', 'wind',
            'wood', 'grain', 'iron', 'clay', 'paper', 'glass', 'fabric',
            'door', 'key', 'roof', 'floor', 'chair', 'table', 'wall',
            'path', 'road', 'horizon', 'shadow', 'weight', 'anchor'
        }

        # 2. Abstract Concepts (High cognitive load)
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

        # 5. THE TOXICITY MAP (Categorized & Weighted)
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

            self.regex_harvester()
        }

    def regex_harvester(self):
        # --- THE REGEX HARVESTER ---
        self.flat_penalty_map = {}
        all_toxins = set()

        for category, phrases in self.toxic_patterns.items():
            for phrase, weight in phrases.items():
                self.flat_penalty_map[phrase] = weight
                all_toxins.add(phrase)

        sorted_toxins = sorted(list(all_toxins), key=len, reverse=True)
        pattern_str = r'\b(' + '|'.join(re.escape(t) for t in sorted_toxins) + r')\b'
        self.toxin_regex = re.compile(pattern_str, re.IGNORECASE)
    }

    def analyze(self, text):
        # 1. CLEANING & TOKENIZATION (Centralized Efficiency)
        text_lower = text.lower()
        # Remove punctuation attached to words for cleaner lookups
        clean_text = text_lower.replace('.', ' ').replace(',', ' ').replace(';', ' ').replace('?', ' ').replace('!', ' ')
        words = clean_text.split()
        total_words = len(words) if words else 1

        # Initialize counters
        counts = {
            'kinetic': 0, 'stative': 0, 'universal': 0,
            'abstract': 0, 'slang': 0, 'connector': 0, 'self_ref': 0
        }
        style_scores = {k: 0 for k in self.styles}

        # --- SINGLE PASS LOOP (The Integrated Pinker Scan) ---
        for i, w in enumerate(words):
            is_known_kinetic = False
            is_known_abstract = False

            # THE MERCY RULE: Look-Ahead Logic
            # We peek at the next word to see if a Stative verb is actually a Helper.
            next_word = words[i+1] if i + 1 < len(words) else ""

            # A. VERB PHYSICS
            if w in self.stative_verbs:
                # MERCY RULE 1: The Motor (Auxiliary + Progressive)
                # "is running" -> Counts "is" as KINETIC because it supports action.
                if next_word.endswith('ing'):
                    counts['kinetic'] += 1

                # MERCY RULE 2: The Anchor (Copula + Universal)
                # "is stone" -> Counts "is" as KINETIC because it grounds reality.
                elif next_word in self.universals:
                    counts['kinetic'] += 1

                # FALLBACK: The Crutch (True Stative)
                # "is nice" -> Counts as STATIVE (High Drag).
                else:
                    counts['stative'] += 1

            # Check for Kinetic Verbs (Standard Dictionary)
            elif w in self.kinetic_verbs or w.endswith('ed'):
                counts['kinetic'] += 1
                is_known_kinetic = True

            # Catch-all for "running" (Gerunds/Participles)
            elif w.endswith(self.kinetic_suffixes):
                 counts['kinetic'] += 1
                 is_known_kinetic = True

            # B. NOUN/CONCEPT PHYSICS
            if w in self.universals:
                counts['universal'] += 1

            if w in self.abstracts and w not in self.brand_safe:
                counts['abstract'] += 1
                is_known_abstract = True

            if w in self.slang: counts['slang'] += 1
            if w in self.connectors: counts['connector'] += 1
            if w in self.self_refs: counts['self_ref'] += 1

            # C. MORPHOLOGY FALLBACKS (The Safety Net)
            if not is_known_abstract:
                if w.endswith(self.abstract_suffixes):
                    counts['abstract'] += 1

            # D. STYLE SCORING
            for style, markers in self.styles.items():
                if w in markers: style_scores[style] += 1

        # --- TOXICITY CHECK (The Regex Sweep) ---
        toxicity_score = 0.0
        toxin_types_found = set()

        matches = self.toxin_regex.findall(text_lower)
        for match in matches:
            weight = self.flat_penalty_map.get(match, 0)
            toxicity_score += weight

            if weight >= 3.0: toxin_types_found.add("CORP/CLICHÉ")
            else: toxin_types_found.add("HEDGING")

        # --- METRIC CALCULATION ---

        # 1. Narrative Drag
        action_score = (counts['kinetic'] * 2) + (counts['stative'] * 0.5) + 1
        adjusted_words = total_words + (toxicity_score * 10)
        narrative_drag = adjusted_words / action_score

        # 2. Abstraction Entropy
        abstraction_entropy = counts['abstract'] - counts['universal']

        # 3. Repetition Rate
        most_common = Counter(words).most_common(1)[0][1] if words else 0
        repetition_rate = most_common / total_words

        # 4. Connection Density
        connection_density = counts['connector'] / total_words

        # 5. Dominant Style
        dominant_style = max(style_scores, key=style_scores.get)

        # 6. Termination Pressure
        termination_pressure = (repetition_rate * 10) + (abstraction_entropy * 0.5) - (counts['universal'] * 0.2)
        termination_pressure = max(0, termination_pressure)

        # 7. The Barrens Check
        in_the_barrens = False
        if total_words > 15:
             in_the_barrens = (termination_pressure > 2.0) and (connection_density < 0.02)

        # 8. Kinetic Ratio
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
    Maps text to one of the 15 Primary Cognitive Archetypes based on
    Boundedness (B) and Expansiveness (E).

    B (Boundedness): Structural integrity, logic, low drag, decisiveness.
    E (Expansiveness): Abstraction, novelty, theoretical reach, connection density.
    """
    def __init__(self):
        # The Map: (Target_B, Target_E)
        # B ranges 0.0 (Chaos) to 1.0 (Order)
        # E ranges 0.0 (Concrete) to 1.0 (Abstract)
        self.archetypes = {
            "THE PALADIN":   {"B": 0.9, "E": 0.2, "desc": "Unwavering code. Deontological pressure."},
            "THE ENGINEER":  {"B": 0.8, "E": 0.3, "desc": "Structural principles. Elegant efficiency."},
            "THE BARBARIAN": {"B": 0.7, "E": 0.8, "desc": "Overwhelming force. Simple weapon, high impact."},
            "THE JUDGE":     {"B": 0.7, "E": 0.1, "desc": "Precedent and verdict. Balanced judgment."},

            "THE ALCHEMIST": {"B": 0.4, "E": 0.9, "desc": "Transmuting base data into gold insight."},
            "THE HORIZON WALKER": {"B": 0.1, "E": 0.9, "desc": "Extrapolation. Liminal states."},
            "THE GHOST":     {"B": 0.1, "E": 0.7, "desc": "Post-hoc, melancholic, detached."},

            "THE SPY":       {"B": 0.8, "E": 0.6, "desc": "Duplicitous surface, singular purpose."},
            "THE DIPLOMAT":  {"B": 0.3, "E": 0.5, "desc": "Fragile common ground. Stability via softness."},
            "THE FOOL":      {"B": 0.1, "E": 0.5, "desc": "Truth through absurdity. Inversion."},

            "THE GEOLOGIST": {"B": 0.4, "E": 0.1, "desc": "Layers of history. Digging down."},
            "THE VULTURE":   {"B": 0.6, "E": 0.7, "desc": "Value in ruin. Salvage operations."},
            "THE COSMIC TRASH PANDA":   {"B": 0.2, "E": 1.0, "desc": "One man's trash is another raccoon's treasure."}
        }

    def calculate_topology(self, phys_metrics, logic_status):
        """
        Converts Physics Data into B/E Coordinates.
        """
        # --- CALCULATE BOUNDEDNESS (B) ---
        # Low Drag = High B
        # High Logic Consistency = High B
        drag = phys_metrics['narrative_drag']
        drag_score = max(0, 1.0 - (drag / 5.0)) # Normalize inverse drag

        logic_bonus = 0.0
        if logic_status == "valid": logic_bonus = 0.2

        # Stative verbs lower B (Passivity is weak structure)
        kinetic_ratio = phys_metrics.get('kinetic_ratio', 0.5) # Need to calculate this in Physics

        b_score = (drag_score * 0.6) + (logic_bonus) + (kinetic_ratio * 0.2)
        b_score = min(1.0, max(0.0, b_score))

        # --- CALCULATE EXPANSIVENESS (E) ---
        # High Entropy = High E
        # High Connection Density = High E
        entropy = phys_metrics['abstraction_entropy']
        # Normalize entropy (usually -5 to +5). We want 0 to 10 scale mapped to 0-1.
        e_score = (entropy + 2) / 10.0

        connectors = phys_metrics['connection_density']
        if connectors > 0.05: e_score += 0.2

        e_score = min(1.0, max(0.0, e_score))

        return b_score, e_score

    def identify(self, phys_metrics, logic_check):
        b, e = self.calculate_topology(phys_metrics, logic_check.get('valid', True))

        closest_arch = "THE SHAPER" # Default
        min_dist = 100.0

        # Euclidean distance to find the nearest Archetype
        for name, coords in self.archetypes.items():
            dist = math.sqrt((b - coords["B"])**2 + (e - coords["E"])**2)
            if dist < min_dist:
                min_dist = dist
                closest_arch = name

        return {
            "archetype": closest_arch,
            "coordinates": {"B": round(b, 2), "E": round(e, 2)},
            "description": self.archetypes[closest_arch]["desc"],
            "distance": round(min_dist, 2)
        }

# --- CORE ORCHESTRATOR -----------------------------------------------------

class EditorialTranslator:
    """
    Translates raw metrics into editorial feedback.
    """
    def __init__(self, physics_engine):
        self.engine = physics_engine

    def generate_feedback(self, text, metrics, archetype_data=None):
        phys = metrics['physics']
        stat = metrics['status']

        # 1. Harvest Status (Maturity of the text)
        status = "Seed (Draft)"
        if len(text.split()) > 15: status = "Bloom (Developing)"
        if phys['connection_density'] > 0.05 and phys['narrative_drag'] < 1.5: status = "Fruit (Polished)"

        # 2. Feedback Generators
        feedback_notes = {}

        # --- A. PACING (Clarence) ---
        if phys['narrative_drag'] > 3.5:
            feedback_notes['Pacing'] = f"CLARENCE: Structure failing (Drag: {phys['narrative_drag']}). High resistance detected."
        elif phys['narrative_drag'] > 2.0:
            feedback_notes['Pacing'] = f"CLARENCE: Pace is deliberate (Drag: {phys['narrative_drag']}). Monitor for stagnation."
        else:
            feedback_notes['Pacing'] = "Clarence is satisfied with the kinetic flow."

        # --- B. GROUNDING (Eloise) ---
        if phys['abstraction_entropy'] > 2:
            feedback_notes['Grounding'] = f"ELOISE: Atmosphere is thin (Entropy: {phys['abstraction_entropy']}). Needs sensory anchors."
        else:
            feedback_notes['Grounding'] = "Eloise feels the texture is solid."

        # --- C. TOXICITY (The New Detector) ---
        # This listens to the specific 'toxin_types' found by the Physics Engine v2.0
        toxins = phys.get('toxin_types', [])

        if 'CORP/CLICHÉ' in toxins:
             feedback_notes['Purity'] = "CLARENCE ALERT: Corporate contaminants detected. We are building a home, not a slide deck."
        elif 'LAZY_METAPHOR' in toxins:
             feedback_notes['Purity'] = "ELOISE SAYS: That metaphor is dead. Bury it. Grow a new one."
        elif 'HEDGING' in toxins:
             feedback_notes['Purity'] = "THE YAGA: You are hedging. 'Not just', 'But rather'. commit to the statement."

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

        # 1. THE SHIELD (Common False Positives)
        # Words that end in 's' but are structurally nouns/adjectives/adverbs.
        safe_list = {
            'always', 'yes', 'news', 'lens', 'physics', 'mathematics',
            'chaos', 'series', 'species', 'analysis', 'crisis', 'thesis',
            'canvas', 'status', 'various', 'previous', 'serious', 'nervous',
            'focus', 'bias', 'basis', 'virus', 'corpus', 'stories', 'movies'
        }
        if w in safe_list: return False

        # 2. THE RADAR (Contextual Locking)
        # If the previous word is a determiner, the current word is 99% a Noun.
        noun_markers = self.articles.union({'these', 'those', 'some', 'many', 'few', 'all', 'no'})
        if prev_word in noun_markers: return False

        # 3. THE TRIGGER (Pronoun Check)
        # If preceded by a pronoun, it is highly likely a verb (e.g., "He runs").
        if prev_word in self.pronouns: return True

        # 4. THE SURGICAL SCAPEL
        stem = w

        # Rule A: 'ies' -> Handle carefully.
        # "Parties" (n) vs "Flies" (v). Hard to distinguish without dictionary.
        # We rely on The Radar (Step 2) to catch the nouns.
        if w.endswith("ies") and len(w) > 4:
             stem = w[:-3]

        # Rule B: Standard 'es' suffixes
        elif w.endswith("es"):
             if w.endswith(("sses", "shes", "ches", "xes", "zzes")):
                 stem = w[:-2]

        # Rule C: The 's' stripper
        elif w.endswith("s"):
             if not w.endswith(("ss", "us", "is", "as", "os", "ys")):
                 stem = w[:-1]

        # 5. THE ANCHOR (Vowel Check)
        # This is a safety catch for abbreviations or weird inputs.
        # (Simple check: does the stem contain at least one vowel?)
        if stem != w:
            if not any(char in 'aeiouy' for char in stem):
                return False

        # If the word changed physically, we assume it is a verb candidate
        return stem != w

    def check_temporal_stability(self, text):
        clean_text = text.lower().replace('.', '').replace(',', '')
        words = clean_text.split()

        counts = {'PAST': 0, 'PRESENT': 0}
        total_signals = 0

        for i, w in enumerate(words):
            prev = words[i-1] if i > 0 else ""

            # 1. Strong Signals (Auxiliaries)
            if w in self.aux_past:
                counts['PAST'] += 1
                total_signals += 1
            elif w in self.aux_present:
                counts['PRESENT'] += 1
                total_signals += 1

            # 2. Heuristic Signals
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
    THE VIRTUAL CORTEX
    Simulates a Neural Network using Procedural Text Generation.
    """
    def __init__(self, physics_ref, witch_ref):
        import random
        self.physics_ref = physics_ref
        self.witch_ref = witch_ref

        # --- CLARENCE: The Architect ---
        # Triggers: High Drag OR Corp Speak
        self.clarence_templates = [
            "I am looking at a Drag Score of {drag}. It is giving me a headache. Cut the word '{target_word}'.",
            "This sentence is a bog. {drag} score? You are wading through stinky sludge.",
            "Slow down, you're doing too much. You used {word_count} words to say what could be said in {half_count}.",
            "The verb '{target_word}' is flimsy. It has no spine. Replace it with a raw energy."
        ]
        self.clarence_corp_templates = [
            "You said '{target_word}'. I am deducting 50 points from your account. Speak like a human.",
            "This is not LinkedIn. Take '{target_word}' out back and shoot it.",
            "Platitude detected. You are hiding behind '{target_word}'. Be direct.",
            "Do not try to 'leverage' or 'synergize' with me. Build something real."
        ]
        self.clarence_loop_templates = [
            "We are spinning in circles. You have been in '{style}' mode for {count} cycles. Shift gears or wrap it up.",
            "Stagnation detected. The last {count} thoughts were identical in tone. Disconnect or pivot.",
            "You are repeating yourself. The echo is getting loud. Break the '{style}' pattern, or risk being silenced by a disengaged reader.",
            "I am bored. We have been stuck in this {style} loop for too long."
        ]

        # --- ELOISE: The Gardener ---
        # Triggers: High Entropy OR Lazy Metaphors
        self.eloise_templates = [
            "I can't touch or feel this. It's all smoke and mirrors. The Entropy is {entropy}. Give me somthing I can hold onto.",
            "You say '{target_word}', but I see nothing. Show me the rust. Show me the light. Show me the scars. Show me what is right.",
            "This is too clean and sterile. Mess it up with some sensory detail.",
            "Ground this. Anchor the thought to a physical object or something bigger than you, or it will float away."
        ]
        self.eloise_cliche_templates = [
            "A '{target_word}'? Really? That flower has wilted. Give me a fresh one.",
            "We have seen '{target_word}' a thousand times. Show me something I haven't seen.",
            "The 'Tapestry' is threadbare. The 'Journey' is over. Write a new image.",
            "You are sleepwalking. '{target_word}' is the first thing that came to mind. Wake up! Dig deeper."
        ]

        # --- THE BABA YAGA: The Witch ---
        # Triggers: Sugar/Hedging
        self.yaga_templates = [
            "You offer me sweetness with ('{target_word}'). The Witch demands meat.",
            "Weakness. You are hiding behind politeness. Show your teeth.",
            "I smell fear. You used '{target_word}' to soften the blow. Strike hard or leave. Stop hiding.",
            "The door is shut. Your intent is too soft to turn the handle. Grip harder or find a window."
        ]
        self.yaga_hedging_templates = [
            "You are hedging with '{target_word}'. Do not apologize for your truth.",
            "You are wasting my time. Say what it IS.",
            "Ambivalence is poison. Platitudes are lazy. Commit to the sentence.",
            "Cut the safety net. Remove '{target_word}' and let the sentence fall or fly."
        ]

        # --- MUSCARIA: The Chaos Jester ---
        # Triggers: Boredom
        self.muscaria_templates = [
            "BOREDOM ALERT. The text is gray. Suddenly, a bird flies into the window. Write about that.",
            "VERSE JUMP. What if this room was underwater? How would the light move?",
            "SYSTEM GLITCH. Repeat the last word three times. Make it a chant. Make it meaningless or birth a new meaning from the ritual.",
            "The narrative is flatlining. Quick, describe the taste of copper. Elaborate on the smell of the moon.",
            "Stop. Look up. What is the ugliest (or most elegant) thing in your field of vision? Put it in the text."
        ]

    def _find_trigger_word(self, text, category):
        """
        Scans text using the MASTER DICTIONARIES from the Physics/Witch engines.
        """
        words = text.lower().replace('.', '').split()

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

        # Scan for the offender
        for w in words:
            if w in targets: return w

        # Also check for multi-word toxins (e.g., "not just") if category implies it
        if category in ['corp', 'cliche', 'hedging']:
             for phrase in targets:
                 if phrase in text.lower():
                     return phrase

        # Fallback
        if category == 'corp': return "that buzzword"
        if category == 'cliche': return "that cliché"
        return "it"

    def synthesize_voice(self, agent, text, metrics, loop_count=0):
        import random

        phys = metrics['physics']
        toxins = phys.get('toxin_types', [])
        style = phys['dominant_style'] # Grab style for the loop detection
        response = ""

        if agent == "CLARENCE":
            # Priority 0: LOOP DETECTION
            if loop_count > 2:
                template = random.choice(self.clarence_loop_templates)
                response = template.format(style=style, count=loop_count)
            # Priority 1: Toxic Corp Speak (Immediate Termination)
            if 'CORP/CLICHÉ' in toxins:
                 template = random.choice(self.clarence_corp_templates)
                 target = self._find_trigger_word(text, 'corp')
                 response = template.format(target_word=target)
            # Priority 2: Standard Drag
            else:
                template = random.choice(self.clarence_templates)
                target = self._find_trigger_word(text, 'stative')
                response = template.format(
                    drag=phys['narrative_drag'],
                    target_word=target,
                    word_count=len(text.split()),
                    half_count=int(len(text.split())/2)
                )

        elif agent == "ELOISE":
            # Priority 1: Lazy Metaphors
            if 'LAZY_METAPHOR' in toxins:
                template = random.choice(self.eloise_cliche_templates)
                target = self._find_trigger_word(text, 'cliche')
                response = template.format(target_word=target)
            # Priority 2: High Entropy (Abstractness)
            else:
                template = random.choice(self.eloise_templates)
                target = self._find_trigger_word(text, 'abstract')
                response = template.format(
                    entropy=phys['abstraction_entropy'],
                    target_word=target
                )

        elif agent == "THE BABA YAGA":
            # Priority 1: Hedging
            if 'HEDGING' in toxins:
                template = random.choice(self.yaga_hedging_templates)
                target = self._find_trigger_word(text, 'hedging')
                response = template.format(target_word=target)
            # Priority 2: Sugar
            else:
                template = random.choice(self.yaga_templates)
                target = self._find_trigger_word(text, 'sugar')
                response = template.format(target_word=target)

        elif agent == "MUSCARIA":
            response = random.choice(self.muscaria_templates)

        return f"[{agent}]: {response}"

class MycelialNetwork:
    """
    Tracks the ancestry of a thought.
    Stores the 'Genetic History' of text evolution.
    """
    def __init__(self):
        # Maps fragment_id -> {parent_id, metrics_snapshot, timestamp}
        self.network = {}

    def spawn_id(self):
        return str(uuid4())[:8] # Short ID for readability

    def log_generation(self, fragment_id, parent_id, metrics):
        """
        Records a new generation in the fungal colony.
        """
        self.network[fragment_id] = {
            "parent": parent_id,
            "drag": metrics['physics']['narrative_drag'],
            "style": metrics['physics']['dominant_style'],
            "barrens": metrics['status']['in_the_barrens']
        }

    def trace_lineage(self, fragment_id):
        """
        Walks backwards from the current text to the original seed.
        Returns a history of improvement (or decay).
        """
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

        return path[::-1] # Oldest to Newest

class MetabolicReserve:
    """
    Manages the 'ATP' of the writer.
    You earn the right to be abstract by building reality first.
    """
    def __init__(self, max_capacity=52):
        self.atp = 33
        self.max_capacity = max_capacity
        self.status = "STABLE"
        self.drag_multiplier = 1.0 # Default

    def spend(self, amount):
        """
        Directly deducts ATP for system interventions (Verse Jumps, Logic Penalties).
        """
        self.atp = max(0, self.atp - amount)

        # Re-evaluate status immediately after spending
        if self.atp < 6: self.status = "STARVING"
        elif self.atp > 40: self.status = "GLUTTON"
        else: self.status = "STABLE"

        return self.atp

    def metabolize(self, metrics):
        phys = metrics['physics']
        delta = 0

        # 1. EARN ATP
        if phys['narrative_drag'] < 2.0: delta += 5
        if phys['connection_density'] > 0.05: delta += 3

        # 2. SPEND ATP
        # Drag Penalty is subject to the Multiplier (Barbarian Rule)
        if phys['narrative_drag'] > 2.0:
            drag_cost = int((phys['narrative_drag'] - 2.0) * 2 * self.drag_multiplier)
            delta -= drag_cost

        if phys['abstraction_entropy'] > 0:
            # Capped cost. You can't lose more than 6 ATP per turn on vocab.
            cost = min(6, int(phys['abstraction_entropy'] * 2))
            delta -= cost

        # 3. TOXICITY TAX
        if phys['toxicity_score'] > 0:
            delta -= 5

        self.atp = max(0, min(self.atp + delta, self.max_capacity))

        if self.atp < 6: self.status = "STARVING"
        elif self.atp > 40: self.status = "GLUTTON"
        else: self.status = "STABLE"

        return {
            "current_atp": self.atp,
            "delta": delta,
            "status": self.status
        }

# --- COMPONENT 6: THE PRESSURE MATRIX ---------------------------

class PressureMatrix:
    """
    Translates Archetype Identity into System Constraints.
    Based on 'The Gospel of James'
    """
    def apply(self, archetype, muscaria_ref, metabolic_ref):
        # Default Settings
        settings = {
            "tolerance_mode": "STANDARD",
            "drag_multiplier": 1.0,  # Penalty multiplier for high drag
            "chaos_threshold": 11.0, # Normal Muscaria Trigger
            "msg": "STANDARD PHYSICS"
        }

        if archetype == "THE PALADIN":
            #  High Pressure on Beta (Contradiction). Principles, not exploration.
            settings["tolerance_mode"] = "DRACONIAN"
            settings["chaos_threshold"] = 20.0 # Suppress chaos
            settings["msg"] = "LAW OF THE TEMPLAR: Logic tears are fatal."

        elif archetype == "THE FOOL":
            #  High Pressure on Entropy. Sacrifices harmony for insight.
            settings["tolerance_mode"] = "INVERTED"
            settings["chaos_threshold"] = 5.0 # Trigger chaos constantly
            settings["msg"] = "JESTER'S PRIVILEGE: Logic errors grant momentum."

        elif archetype == "THE BARBARIAN":
            #  Narrative Drag ANNIHILATED.
            settings["drag_multiplier"] = 5.0 # High drag costs 5x ATP
            settings["tolerance_mode"] = "STANDARD"
            settings["msg"] = "BERSERKER STATE: Adjectives are weakness."

        elif archetype == "THE SPY":
            # [cite: 1] High Contradiction Tolerance (Beta). Cover coherence.
            settings["tolerance_mode"] = "LOOSE"
            settings["msg"] = "DEEP COVER: Logic tears are hidden from the reader."

        elif archetype == "THE ENGINEER":
             # [cite: 9] High Translation Fidelity. Functional coherence.
             settings["tolerance_mode"] = "DRACONIAN"
             settings["msg"] = "STRUCTURAL INTEGRITY: No poetic license allowed."

        # Apply to Sub-Systems
        muscaria_ref.pressure_threshold = settings["chaos_threshold"]
        metabolic_ref.drag_multiplier = settings["drag_multiplier"] # Needs update in MetabolicReserve

        return settings

# --- COMPONENT 7: THE SCEHMATICS ---------------------------

class TwelveDDashboard:
    """
    VISUALIZER: THE HYPERCUBE
    Renders the 12-Dimensional Cognitive State Vector.
    """
    def __init__(self):
        self.C_CYAN = "\033[96m"
        self.C_RESET = "\033[0m"
        self.C_DIM = "\033[2m"

    def _mini_bar(self, val):
        """Creates a tiny sparkline [|||  ]"""
        # Clamp 0.0 to 1.0
        val = max(0.0, min(val, 1.0))
        total_ticks = 5
        filled = int(val * total_ticks)
        bar = "▊" * filled + " " * (total_ticks - filled)
        return f"[{bar}]"

    def render(self, state):
        print(f"{self.C_CYAN}--- 12-DIMENSIONAL MANIFOLD ---{self.C_RESET}")

        # We display in a 3x4 Grid for cognitive ergonomics
        # Row 1: The Energy/Structure Triad
        row1 = f"E : {state['E']:.2f} {self._mini_bar(state['E'])}  |  β : {state['β']:.2f} {self._mini_bar(state['β'])}  |  κ : {state['κ']:.2f} {self._mini_bar(state['κ'])}"

        # Row 2: The Entropy/Logic Triad
        row2 = f"ε : {state['ε']:.2f} {self._mini_bar(state['ε'])}  |  ΔTF:{state['ΔTF']:.2f} {self._mini_bar(state['ΔTF'])}  |  DP: {state['DP']:.2f} {self._mini_bar(state['DP'])}"

        # Row 3: The Purity/Quality Triad
        row3 = f"LQ: {state['LQ']:.2f} {self._mini_bar(state['LQ'])}  |  CD : {state['CD']:.2f} {self._mini_bar(state['CD'])}  |  Φ : {state['Φ']:.2f} {self._mini_bar(state['Φ'])}"

        # Row 4: The Meta/Network Triad
        row4 = f"Ψ : {state['Ψ']:.2f} {self._mini_bar(state['Ψ'])}  |  Δ  : {state['Δ']:.2f} {self._mini_bar(state['Δ'])}  |  Ξ : {state['Ξ']:.2f} {self._mini_bar(state['Ξ'])}"

        print(f" {row1}")
        print(f" {row2}")
        print(f" {row3}")
        print(f" {row4}")
        print(f"{self.C_DIM} Key: E=Exhaustion β=Boundedness κ=Kinetic ε=Entropy ΔTF=Truth DP=Diplomacy{self.C_RESET}")
        print(f"{self.C_DIM}      LQ=LoopQual CD=Contagion Φ=Purity Ψ=Psych Δ=Chaos Ξ=Network{self.C_RESET}")

class MycelialDashboard:
    """
    The Mycelial DASHBOARD
    Renders the internal math of BoneAmanita as an ASCII readout.
    """
    def __init__(self):
        # ANSI Colors
        self.C_RESET = "\033[0m"
        self.C_RED = "\033[91m"
        self.C_GREEN = "\033[92m"
        self.C_YELLOW = "\033[93m"
        self.C_CYAN = "\033[96m"
        self.C_PURPLE = "\033[95m"
        self.C_BLUE = "\033[94m"

        self.dim_viz = TwelveDDashboard()

    def _draw_bar(self, value, max_val, label, color_code, threshold=None, invert=False):
        """
        Draws a progress bar.
        Logic: If 'invert' is True, Lower is Better (e.g., Drag).
        """
        bar_width = 20
        # Clamp value
        normalized = max(0, min(value, max_val))
        filled_len = int((normalized / max_val) * bar_width)
        bar = "█" * filled_len + "░" * (bar_width - filled_len)

        return f"{label:<15} |{color_code}{bar}{self.C_RESET}| {value:.2f}"

    def render(self, metrics, intervention, energy, ancestry, chronos_report, archetype_data, twelve_d_state):
        phys = metrics['physics']
        stat = metrics['status']

        print(f"\n{self.C_CYAN}--- MYCELIAL EKG ---{self.C_RESET}")

        # 1. METABOLIC RESERVE (ATP)
        # Goal: Keep it high to afford abstractions.
        atp_color = self.C_GREEN
        if energy['status'] == "STARVING": atp_color = self.C_RED
        elif energy['status'] == "GLUTTON": atp_color = self.C_BLUE # Blue for "Overcharged"

        print(self._draw_bar(
            energy['current_atp'],
            max_val=50.0,
            label="CREATIVE ATP",
            color_code=atp_color
        ) + f" ({energy['status']})")

        # 2. NARRATIVE DRAG (The Molasses Meter)
        print(self._draw_bar(
            phys['narrative_drag'],
            max_val=5.0,
            label="NARRATIVE DRAG",
            color_code=self.C_YELLOW,
            threshold=2.0,
            invert=True
        ))

        # 3. ABSTRACTION ENTROPY (The Balloon String)
        print(self._draw_bar(
            abs(phys['abstraction_entropy']),
            max_val=10.0,
            label="REALITY DRIFT",
            color_code=self.C_PURPLE,
            threshold=2.0,
            invert=True
        ))

        # 4. BOREDOM PRESSURE (The Bomb Fuse)
        muscaria_active = self.C_RED if stat['termination_pressure'] > 4.0 else self.C_GREEN
        print(self._draw_bar(
            stat['termination_pressure'],
            max_val=10.0,
            label="CHAOS PRESSURE",
            color_code=muscaria_active,
            threshold=5.0,
            invert=True
        ))

        # 5. CHRONOS STATUS
        chronos_color = self.C_GREEN
        if chronos_report['status'] == "DRIFT DETECTED": chronos_color = self.C_RED
        elif chronos_report['status'] == "LOCKED": chronos_color = self.C_CYAN

        print(f"TEMPORAL STATE : {chronos_color}{chronos_report['status']}{self.C_RESET}")
        if chronos_report['status'] == "DRIFT DETECTED":
             print(f"               : {self.C_RED}{chronos_report['details']}{self.C_RESET}")

        # 6. STATUS & LINEAGE
        print(f"{'-'*45}")
        style = phys['dominant_style'].upper()

        # Style Color Logic
        style_color = self.C_GREEN
        if style == "CLARET": style_color = self.C_RED
        if style == "CRYSTAL": style_color = self.C_CYAN

        #12D (Hi James)
        if twelve_d_state:
            print(f"{'-'*45}")
            self.dim_viz.render(twelve_d_state)

        # 6. ARCHETYPE PRISM
        print(f"{'-'*45}")
        # Check if data exists to prevent crash on empty drafts
        if archetype_data:
            print(f"COGNITIVE MODE : {self.C_PURPLE}{archetype_data['archetype']}{self.C_RESET}")
            print(f"TOPOLOGY       : B: {archetype_data['coordinates']['B']} | E: {archetype_data['coordinates']['E']}")
            print(f"SIGNATURE      : {archetype_data['description']}")

        print(f"DOMINANT STYLE : {style_color}{style}{self.C_RESET}")

        if intervention:
            print(f"INTERVENTION   : {self.C_RED}ACTIVE{self.C_RESET} -> {intervention}")
        else:
            print(f"INTERVENTION   : {self.C_GREEN}DORMANT{self.C_RESET}")

        # LINEAGE TRACE (Visualizing Evolution)
        if len(ancestry) > 1:
            print(f"\n{self.C_BLUE}GENETIC HISTORY:{self.C_RESET}")
            # Show last 3 generations
            history = ancestry[-3:]
            for node in history:
                print(f"  └─ [{node['id']}] Drag: {node['drag']} ({node['style']})")

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
        self.pressure_matrix = PressureMatrix()
        self.twelve_d_dashboard = TwelveDDashboard()
        self.last_id = None
        self.tick = 0
        self.session_drag_history = []
        # Mock input tracking for DP calculation
        self.last_input = ""

    def _update_baseline(self, current_drag):
        """Calculates the moving average of the user's drag."""
        self.session_drag_history.append(current_drag)
        if len(self.session_drag_history) > 20:
            self.session_drag_history.pop(0)
        return sum(self.session_drag_history) / len(self.session_drag_history)

    def _enforce_archetype_physics(self, archetype):
        """
        Dynamically adjusts the FactStipe based on the active Archetype.
        Protocol: DIMENSIONAL QUARANTINE.
        """
        if archetype == "THE COSMIC TRASH PANDA":
            # We map 'Trash' and 'Treasure' to the same Positive Value (+1).
            # This creates 'Concordance' instead of 'Conflict'.
            truths = ["trash", "rubbish", "garbage", "scrap", "waste"]
            treasures = ["treasure", "gold", "gem", "diamond", "prize"]

            for t in truths:
                self.stipe.inject_truth(t, "VALUE", 1)

            for t in treasures:
                self.stipe.inject_truth(t, "VALUE", 1)

            # The Panda sees 'Void' as 'Home' (Habitat +1)
            self.stipe.inject_truth("void", "HABITAT", 1)
            self.stipe.inject_truth("alley", "HABITAT", 1)

    def _calculate_12d_state(self, metrics, energy, archetype, logic, pressure):
        """Map current state to 12D coordinates (0.0 to 1.0 normalized)"""
        phys = metrics['physics']

        # Helper to safely get length
        toxin_count = len(phys.get('toxin_types', []))

        return {
            'E': max(0, 1.0 - (energy['current_atp'] / 52.0)),  # Exhaustion (Inverse ATP)
            'β': 0.8 if pressure['tolerance_mode'] == 'DRACONIAN' else
                 0.2 if pressure['tolerance_mode'] == 'INVERTED' else 0.5, # Boundedness
            'κ': min(1.0, phys['narrative_drag'] / 5.0), # Kinetic Drag
            'ε': min(1.0, (abs(phys['abstraction_entropy']) + 2) / 10.0), # Entropy
            'ΔTF': 0.9 if logic.get('valid') else 0.3, # Truth Fidelity
            'DP': 0.7 if "please" in self.last_input.lower() else 0.3,  # Diplomacy (Politeness)
            'LQ': min(1.0, phys['repetition_rate'] * 2), # Loop Quality
            'CD': min(1.0, phys['toxicity_score'] / 10.0), # Contagion Density
            'Φ': 0.8 if toxin_count == 0 else 0.4, # Purity
            'Ψ': 0.9 if archetype['distance'] < 0.2 else 0.5,  # Psychological Stability
            'Δ': 0.7 if self.muscaria.boredom_pressure > 5.0 else 0.3, # Chaos Delta
            'Ξ': min(1.0, len(self.lineage.network) / 20.0)  # Network Complexity
        }

    def process(self, text, parent_id=None):
        self.tick += 1
        self.last_input = text

        # USE THE BASELINE
        metrics = self.physics.analyze(text)
        phys = metrics['physics']

        avg_drag = self._update_baseline(phys['narrative_drag'])

        # 1. IDENTITY GENERATION
        current_id = self.lineage.spawn_id()
        actual_parent = parent_id if parent_id else self.last_id

        # 2. PHYSICS CALCULATION
        stat = metrics['status']

        self.codex.scan_for_entities(text, self.tick)

        # 3. THE BABA YAGA
        gate_result = self.witch.evaluate_intent(text, metrics)
        if not gate_result['accepted']:
            return f"[BLOCKED] {gate_result['message']}"

        # Step A: Optimistic Archetype Identification
        # We assume logic is valid to get the initial Identity.
        # This breaks the loop: Prism -> Archetype -> Pressure -> Stipe -> Prism
        prelim_archetype_data = self.prism.identify(metrics['physics'], {"valid": True})
        current_archetype = prelim_archetype_data['archetype']

        # Step B: Apply Pressure Matrix
        # Now we know WHO they are, so we know HOW to judge them.
        pressure_settings = self.pressure_matrix.apply(
            current_archetype,
            self.muscaria,
            self.metabolism
        )

        # Step C: The Fact Stipe (With Specific Tolerance)
        stipe_check = self.stipe.check_consistency(
            text,
            metrics['physics']['dominant_style'],
            self.metabolism.status,
            tolerance_mode=pressure_settings['tolerance_mode']
        )

        # Step D: Finalize Archetype Data (With Real Logic Result)
        # We re-run identification with the ACTUAL logic result for the final log.
        archetype_data = self.prism.identify(metrics['physics'], stipe_check)

        # ------------------------------------------

        self._enforce_archetype_physics(current_archetype)

        # 6. MEMORY RECALL
        current_style = metrics['physics']['dominant_style']
        recalled_echoes = self.memory.recall(current_style)
        loop_count = len(recalled_echoes)

        # 7. EDITORIAL FEEDBACK
        editorial = self.editor.generate_feedback(text, metrics, archetype_data)

        # Inject the Pressure Message into Feedback
        if pressure_settings['msg'] != "STANDARD PHYSICS":
            editorial['feedback']['ARCHETYPE_PRESSURE'] = f"SYSTEM: {pressure_settings['msg']}"

        # 8. THE VIRTUAL CORTEX
        if phys['narrative_drag'] > 3.0 or loop_count > 2:
            voice = self.cortex.synthesize_voice("CLARENCE", text, metrics, loop_count=loop_count)
            editorial['feedback']['Pacing'] = voice

        if phys['abstraction_entropy'] > 2:
            voice = self.cortex.synthesize_voice("ELOISE", text, metrics)
            editorial['feedback']['Grounding'] = voice

        if "THE YAGA GRUMBLES" in gate_result['message']:
             voice = self.cortex.synthesize_voice("THE BABA YAGA", text, metrics)
             editorial['feedback']['Intent'] = voice

        muscaria_msg = None
        if self.muscaria.check_for_boredom(metrics):
            if self.cooldown.is_ready(self.tick, force=stat['in_the_barrens']):
                ancestry_temp = self.lineage.trace_lineage(current_id)
                muscaria_msg = self.muscaria.trigger_disruption(ancestry_temp)
                # Unified Economy
                self.metabolism.spend(5)
            else:
                muscaria_msg = self.cortex.synthesize_voice("MUSCARIA", text, metrics)

        # 9. LOGIC INTERVENTION
        if not stipe_check.get('valid', True):
            intervention_msg = stipe_check.get('intervention', "LOGIC BREACH")
            editorial['feedback']['CRITICAL_LOGIC'] = f"FACT STIPE ALERT: {intervention_msg}"

            # Penalize the ATP for being illogical
            self.metabolism.spend(10)

        # 10. METABOLISM & LINEAGE
        energy_report = self.metabolism.metabolize(metrics)
        self.lineage.log_generation(current_id, actual_parent, metrics)
        self.last_id = current_id

        # 11. DYNAMIC DIFFICULTY
        if energy_report['status'] == "STARVING":
            metrics['physics']['narrative_drag'] += 1.0

        # 12. MEMORY & TIME
        self.memory.leave_trace(text, metrics['physics']['dominant_style'])
        chronos_report = self.chronos.check_temporal_stability(text)

        # 13. VISUALIZATIONself
        ancestry_data = self.lineage.trace_lineage(current_id)

        # Calculate the 12D State
        twelve_d_state = self._calculate_12d_state(
            metrics,
            energy_report,
            archetype_data,
            stipe_check,
            pressure_settings
        )

        # Render with the new state
        self.dashboard.render(
            metrics,
            muscaria_msg,
            energy_report,
            ancestry_data,
            chronos_report,
            archetype_data,
            twelve_d_state
        )


        return {
            "id": current_id,
            "metrics": metrics,
            "energy": energy_report,
            "ancestry": ancestry_data,
            "editorial": editorial,
            "intervention": muscaria_msg,
            "archetype_data": archetype_data,
            "12d_state": twelve_d_state # Added to return object
        }

    def generate_instruction_block(self, result):
        """
        Converts the Engine's math into a Natural Language Prompt for the LLM.
        """
        editorial = result['editorial']['feedback']
        arch = result.get('archetype_data', {})

        # RETRIEVE ANCHORS
        anchors = self.codex.get_anchors()
        anchor_string = ", ".join(anchors) if anchors else "None established."

        # Build the Persona Injection
        directives = []

        if "Pacing" in editorial:
            directives.append(f"Constraint: {editorial['Pacing']} (Fix the drag).")
        if "Grounding" in editorial:
            directives.append(f"Constraint: {editorial['Grounding']} (Add sensory details).")
        if result['intervention']:
            directives.append(f"CHAOS EVENT: {result['intervention']}")

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

# --- MAIN EXECUTION --------------------------------------------------------

if __name__ == "__main__":
    engine = BonepokeCore()

    print("--- BONEAMANITA v0.6.1: THE TIDY EDITION ---")

    # Test Input
    test_input = (
        "The system leverages the context to optimize workflow."
        "It is nice and we hope you like it."
        "Also, the fire froze."
        "People don't think it be like it is, but it do."
        "ok i luv u bye"
    )

    print(f"INPUT: \"{test_input}\"\n")

    result = engine.process(test_input)

    # If the Witch rejects it, result is a string.
    if isinstance(result, str):
        print(f"{engine.dashboard.C_RED}{result}{engine.dashboard.C_RESET}")
    else:
        # If accepted, generate the LLM Instruction Block
        instruction = engine.generate_instruction_block(result)

        print("\n" + "="*60)
        print("   >>  COPY THIS BLOCK INTO YOUR LLM PROMPT  <<")
        print("="*60)
        print(instruction)
        print("="*60)
