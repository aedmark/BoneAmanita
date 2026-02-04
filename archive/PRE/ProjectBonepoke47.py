# ---------------------------------------------------------------------------
# BONEPOKE ENGINE v4.7 — The "Soul & Science" Build
# Architect: James Taylor | Audit: SLASH, TMMN
#
# "Clean logic, feral data. Fear is the mind-killer, but also a good filter."
# ---------------------------------------------------------------------------

import time
import math
import random
from collections import Counter

# --- COMPONENT 1: MEMORY & ECONOMY -----------------------------------------

class MemoryResidue:
    """
    Manages short-term contextual memory.
    Implements 'Relevance Decay' to discard unused information.
    """
    def __init__(self, retention_span=10):
        self.memory_stream = []
        self.retention_span = retention_span
        self.current_tick = 0

    def leave_trace(self, content, context_tag):
        """
        Stores a memory fragment with its associated context.
        """
        self.current_tick += 1
        memory_packet = {
            "content": content,
            "context_tag": context_tag,
            "timestamp": self.current_tick
        }
        self.memory_stream.append(memory_packet)
        self._prune_old_memories()

    def recall(self, target_context):
        """
        Retrieves memories that match the current context or are very recent.
        """
        relevant_memories = []
        for mem in self.memory_stream:
            # Cognitive Rule: We remember things that fit the current mood
            # or happened just seconds ago.
            is_recent = (self.current_tick - mem['timestamp']) < 3
            is_relevant = (mem['context_tag'] == target_context)

            if is_recent or is_relevant:
                relevant_memories.append(mem['content'])

        return relevant_memories

    def _prune_old_memories(self):
        """
        Removes memories exceeding the retention span.
        """
        if len(self.memory_stream) > self.retention_span:
            self.memory_stream.pop(0)

class FactSpine:
    """
    The Fact Checker. Prevents narrative gaslighting.
    """
    def __init__(self, decay_limit=20):
        self.facts = {}
        self.decay_limit = decay_limit
        self.current_tick = 0

        # The Physics of Opposites
        # Definitions of incompatible states to prevent logic drift.
        self.conflict_map = {
            'night': {'sun', 'daylight', 'noon', 'morning', 'solar'},
            'day': {'moon', 'midnight', 'stars', 'darkness'},
            'quiet': {'scream', 'bang', 'crash', 'loud', 'shout', 'roar'},
            'indoors': {'rain', 'wind', 'sky', 'grass', 'mud'},
            'alone': {'crowd', 'them', 'they', 'voices', 'people'},
            'dead': {'breath', 'pulse', 'heartbeat', 'gasp', 'running'}
        }

    def learn_fact(self, fact_text, is_permanent=False):
        self.current_tick += 1
        fact_key = fact_text.lower().strip()
        self.facts[fact_key] = {
            "original_text": fact_text,
            "last_seen": self.current_tick,
            "is_permanent": is_permanent
        }

    def reinforce_facts(self, current_text):
        self.current_tick += 1
        text_lower = current_text.lower()
        for key, data in self.facts.items():
            if key in text_lower:
                data['last_seen'] = self.current_tick

    def check_consistency(self, current_text):
        # 1. Maintenance
        self._prune_decayed_facts()

        # 2. Reinforcement
        self.reinforce_facts(current_text)

        # 3. Validation
        text_lower = current_text.lower()
        words = set(text_lower.split())
        violations = []

        for fact_key in self.facts:
            # Extract core concept (e.g., "status: dead" -> "dead")
            core_concept = fact_key.split(':')[-1].strip()

            if core_concept in self.conflict_map:
                forbidden_words = self.conflict_map[core_concept]
                conflicts = words.intersection(forbidden_words)

                if conflicts:
                    violations.append(f"Spine Fracture: '{core_concept}' clashes with {conflicts}.")

        if violations:
            return {"valid": False, "errors": violations}
        return {"valid": True, "errors": []}

    def _prune_decayed_facts(self):
        """
        Garbage Collection for facts that haven't been referenced.
        """
        to_remove = []
        for key, data in self.facts.items():
            if data['is_permanent']: continue

            age = self.current_tick - data['last_seen']
            if age > self.decay_limit:
                to_remove.append(key)

        for key in to_remove:
            del self.facts[key]

class ResourceManager:
    """
    Tracks computational or narrative 'effort'.
    """
    def __init__(self, limit=30):
        self.limit = limit
        self.used = 0

    def spend(self, amount=1):
        self.used += amount
        return self.used

class ChaosCooldown:
    """
    Prevents Ziggy from nuking the text every single turn.
    """
    def __init__(self, cooldown_ticks=5):
        self.last_trigger_tick = -cooldown_ticks
        self.cooldown = cooldown_ticks

    def is_ready(self, current_tick, force=False):
        if force or (current_tick - self.last_trigger_tick >= self.cooldown):
            self.last_trigger_tick = current_tick
            return True
        return False

# --- COMPONENT 2: THE ZIGGY ENGINE ------------------------------

class ZiggyStochasticEngine:
    """
    Injects randomness when the narrative becomes stagnant.
    We have restored the 'Molotov' flavor text because 'Sensory Shift' was boring.
    """
    def __init__(self):
        self.boredom_pressure = 0.0
        self.pressure_threshold = 5.0
        self.disruptions = [
            "VIBE CHECK: Delete the last sentence. Replace with a sudden physical action.",
            "CUT THE CHEESE: Introduce a smell or temperature change immediately.",
            "THE PIVOT: Reveal a contradiction in the narrator's intent.",
            "NON-SEQUITUR: Scream (metaphorically) and change the subject.",
            "SURREALIST: Replace an abstract concept with a wind chime.",
            "GLITTER BOMB: Break the rhythm with a fragment.",
            "VOID STARE: Stop explaining. Describe the thing itself.",
            "THE LIZARD KING: Raise the stakes. A threat has entered.",
            "STOP THE PRESSES: You are using too many 'is' verbs. Make something explode."
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

    def trigger_disruption(self):
        self.boredom_pressure = 0.0
        return f"ZIGGY INTERVENTION: {random.choice(self.disruptions)}"

# --- COMPONENT 3: BABA YAGA -----------------------------------

class BabaYagaProtocol:
    """
    The Authenticity Gatekeeper.
    Restored the "Hut" persona. She demands 'Meat' (Substance) over 'Sugar' (Politeness).
    """
    def __init__(self):
        self.cliches = {
            'once upon a time', 'happily ever after', 'dark and stormy',
            'fix this', 'make it better', 'write a story about', 'suddenly'
        }
        self.pleading_words = {'please', 'help me', 'sorry', 'can you', 'assist'}

    def smell_fear(self, text):
        """
        Evaluates input for Sycophancy vs Substance.
        """
        text_lower = text.lower()
        words = text.split()
        word_count = len(words)

        # 1. Minimum Effort Check
        if word_count < 4:
             return {"accepted": False, "message": "THE YAGA: Too quiet. Speak up."}

        # 2. Cliche Check
        for cliche in self.cliches:
            if cliche in text_lower:
                return {"accepted": False, "message": f"THE YAGA: '{cliche}'? This meat is gray. Cook it again."}

        # 3. Sycophancy Check (Sugar vs. Meat)
        sugar_count = sum(1 for w in words if w in self.pleading_words)
        meat_count = word_count - sugar_count

        # If meat count is low AND sugar is present, she rejects it.
        if meat_count < 5 and sugar_count > 0:
             return {"accepted": False, "message": "THE YAGA: You offer me only sweetness. Give me something to chew on."}

        return {"accepted": True, "message": "DORMANT"}

# --- COMPONENT 4: THE PHYSICS ENGINE ------------------------------

class LinguisticPhysicsEngine:
    """
    Analyzes text properties using 'Bonepoke' data profiles.
    """
    def __init__(self):
        # 1. Concrete Universals (Grounding words)
        self.universals = {
            'hand', 'eye', 'blood', 'bone', 'breath', 'sweat', 'pulse', 'throat', 'skin', 'muscle',
            'stone', 'light', 'dirt', 'water', 'rain', 'smoke', 'salt', 'rust', 'glass', 'mud', 'ash',
            'door', 'key', 'roof', 'floor', 'chair', 'table', 'bread', 'knife', 'seed', 'root', 'wall'
        }

        # 2. Abstract Concepts (High cognitive load)
        self.abstracts = {
            'system', 'protocol', 'sequence', 'vector', 'node', 'context',
            'layer', 'matrix', 'manifold', 'substrate', 'perspective', 'framework',
            'logic', 'metric', 'concept', 'theory', 'analysis'
        }
        self.brand_safe = {'system', 'bonepoke', 'shimmer', 'lattice', 'ziggy', 'context', 'layer'}

        # 3. Verbs
        self.kinetic_verbs = {'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'weave', 'cut', 'throw', 'drive', 'grab'}
        self.stative_verbs = {'is', 'are', 'was', 'were', 'seem', 'appear', 'have', 'has', 'consist'}

        # 4. Stylistic Profiles (Substrates)
        self.styles = {
            'Moss': {'layer', 'nuance', 'deep', 'tapestry', 'accumulate'},
            'Crystal': {'logic', 'define', 'metric', 'precise', 'structure'},
            'Fluid': {'flow', 'adapt', 'stream', 'dissolve', 'shift'},
            'Lattice': {'foundation', 'structure', 'design', 'plan', 'ensure'},
            'Claret': {'ache', 'blood', 'fuck', 'love', 'maybe', 'hurt', 'mess', 'human'}
        }

        self.connectors = {'we', 'you', 'us', 'together', 'share'}
        self.self_refs = {'i', 'me', 'my', 'mine'}
        self.slang = {'vibe', 'trash', 'gonzo', 'wild', 'weird', 'mess', 'glitter', 'swamp'}

        # 5. The Guillotine List (Corp-speak & Clichés)
        self.toxic_phrases = {
            'not just': 2.0, 'not only': 2.0, 'but rather': 2.5,
            'testament to': 3.0, 'delicate dance': 4.0, 'tapestry': 3.0,
            'landscape of': 2.0, 'game-changer': 3.0, 'rubber meets': 4.0,
            'ultimately': 1.5, 'symphony': 2.5
        }

    def analyze(self, text):
        """
        FULLER OPTIMIZATION: Single-pass analysis for maximum efficiency.
        """
        text_lower = text.lower()
        words = text_lower.split()
        total_words = len(words) if words else 1

        # Initialize counters
        counts = {
            'kinetic': 0, 'stative': 0, 'universal': 0,
            'abstract': 0, 'slang': 0, 'connector': 0, 'self_ref': 0
        }
        style_scores = {k: 0 for k in self.styles}

        # --- SINGLE PASS LOOP (O(N)) ---
        for w in words:
            # Physics
            if w in self.kinetic_verbs or w.endswith('ed'): counts['kinetic'] += 1
            elif w in self.stative_verbs: counts['stative'] += 1

            # Vocabulary Type
            if w in self.universals: counts['universal'] += 1
            if w in self.abstracts and w not in self.brand_safe: counts['abstract'] += 1
            if w in self.slang: counts['slang'] += 1
            if w in self.connectors: counts['connector'] += 1
            if w in self.self_refs: counts['self_ref'] += 1

            # Style Profiling
            for style, markers in self.styles.items():
                if w in markers:
                    style_scores[style] += 1

        # --- METRIC CALCULATION (Pinker's Clear Naming) ---

        # 1. Narrative Drag
        # Ratio of Words to Action. Lower is better.
        action_score = (counts['kinetic'] * 2) + (counts['stative'] * 0.5) + 1
        narrative_drag = total_words / action_score

        # 2. Abstraction Entropy
        # Net balance of Abstract words vs Concrete Universals.
        abstraction_entropy = counts['abstract'] - counts['universal']

        # 3. Repetition Rate
        most_common = Counter(words).most_common(1)[0][1] if words else 0
        repetition_rate = most_common / total_words

        # 4. Connection Density
        connection_density = counts['connector'] / total_words

        # 5. Dominant Style
        dominant_style = max(style_scores, key=style_scores.get)

        # 6. Toxicity Check (The Guillotine)
        toxicity_score = 0
        for phrase, penalty in self.toxic_phrases.items():
            if phrase in text_lower:
                toxicity_score += penalty

        # Apply Toxicity Penalty to Drag
        adjusted_words = total_words + (toxicity_score * 10)
        final_drag = adjusted_words / action_score

        # 7. Termination Pressure
        # A composite score indicating if the text should be stopped/changed.
        termination_pressure = (repetition_rate * 10) + (abstraction_entropy * 0.5) - (counts['universal'] * 0.2)
        termination_pressure = max(0, termination_pressure)

        # 8. "The Barrens" (Disconnected & Boring)
        in_the_barrens = (termination_pressure > 2.0) and (connection_density < 0.02)

        return {
            "physics": {
                "narrative_drag": round(final_drag, 2),
                "abstraction_entropy": abstraction_entropy,
                "repetition_rate": round(repetition_rate, 2),
                "connection_density": round(connection_density, 2),
                "dominant_style": dominant_style,
                "toxicity_score": toxicity_score
            },
            "status": {
                "termination_pressure": round(termination_pressure, 2),
                "in_the_barrens": in_the_barrens
            }
        }

# --- CORE ORCHESTRATOR -----------------------------------------------------

class EditorialTranslator:
    """
    Translates raw metrics into editorial feedback.
    """
    def __init__(self, physics_engine):
        self.engine = physics_engine

    def generate_feedback(self, text, metrics):
        phys = metrics['physics']
        stat = metrics['status']

        # 1. Harvest Status (Maturity of the text)
        status = "Seed (Draft)"
        if len(text.split()) > 15: status = "Bloom (Developing)"
        if phys['connection_density'] > 0.05 and phys['narrative_drag'] < 1.5: status = "Fruit (Polished)"

        # 2. Feedback Generators
        feedback_notes = {}

        # Drag Check (The Clarence Protocol)
        if phys['narrative_drag'] > 2.0:
            feedback_notes['Pacing'] = (
                f"CLARENCE: Too slow (Drag: {phys['narrative_drag']}). "
                "You are wading through molasses. Cut 'is/was' verbs. Inject kinetic vectors."
            )
        else:
            feedback_notes['Pacing'] = "Clarence is satisfied with the velocity."

        # Grounding Check (The Eloise Protocol)
        if phys['abstraction_entropy'] > 1:
            suggestion = random.choice(list(self.engine.universals))
            feedback_notes['Grounding'] = (
                f"ELOISE: Too abstract (Entropy: {phys['abstraction_entropy']}). "
                f"It floats away. Anchor it with a universal like '{suggestion}'."
            )
        else:
            feedback_notes['Grounding'] = "Eloise feels the warmth is sufficient."

        # Emergency Check
        if stat['in_the_barrens']:
            feedback_notes['CRITICAL'] = "THE BARRENS: Reader disengagement imminent. Pivot immediately."

        return {
            "status": status,
            "feedback": feedback_notes
        }

class BonepokeCore:
    def __init__(self):
        self.resources = ResourceManager()
        self.cooldown = ChaosCooldown()
        self.memory = MemoryResidue()
        self.spine = FactSpine()
        self.physics = LinguisticPhysicsEngine()
        self.editor = EditorialTranslator(self.physics)
        self.ziggy = ZiggyStochasticEngine()
        self.yaga = BabaYagaProtocol() # The Hut is Open
        self.tick = 0

    def process(self, text):
        self.tick += 1
        print(f"\n--- PROCESSING TICK {self.tick} ---")

        # 1. Baba Yaga Check
        gate_result = self.yaga.smell_fear(text)
        if not gate_result['accepted']:
            return f"[BLOCKED] {gate_result['message']}"

        # 2. Fact Check
        spine_check = self.spine.check_consistency(text)
        if not spine_check['valid']:
            print(f"[WARNING] {spine_check['errors']}")

        # 3. Physics Analysis
        metrics = self.physics.analyze(text)

        # 4. Memory Update
        self.memory.leave_trace(text, metrics['physics']['dominant_style'])

        # 5. Editorial Feedback
        editorial = self.editor.generate_feedback(text, metrics)

        # 6. Ziggy Intervention (Chaos Injection)
        ziggy_msg = None
        if self.ziggy.check_for_boredom(metrics):
            if self.cooldown.is_ready(self.tick, force=metrics['status']['in_the_barrens']):
                ziggy_msg = self.ziggy.trigger_disruption()
                self.resources.spend(5)

        return {
            "metrics": metrics,
            "editorial": editorial,
            "intervention": ziggy_msg
        }

# --- MAIN EXECUTION --------------------------------------------------------

if __name__ == "__main__":
    engine = BonepokeCore()

    print("--- BONEPOKE v4.7: SOUL & SCIENCE BUILD ---")
    print("Optimization: O(N) | Clarity: High | Vibes: Feral\n")

    # Test Input: A mix of abstract nonsense and Sycophancy to test the Yaga.
    test_input = "The system is a framework of logic. Please help me."

    print(f"INPUT: \"{test_input}\"")

    result = engine.process(test_input)

    if isinstance(result, str):
        print(result) # This should trigger the Yaga Block
    else:
        m = result['metrics']['physics']
        s = result['metrics']['status']

        print(f"\n[PHYSICS REPORT]")
        print(f"  Style:        {m['dominant_style']}")
        print(f"  Drag:         {m['narrative_drag']} (Lower is faster)")
        print(f"  Entropy:      {m['abstraction_entropy']} (Positive = Abstract)")
        print(f"  Connection:   {m['connection_density']}")

        print(f"\n[EDITORIAL FEEDBACK]")
        print(f"  Phase:        {result['editorial']['status']}")
        for k, v in result['editorial']['feedback'].items():
            print(f"  {k}: {v}")

        if result['intervention']:
            print(f"\n!!! {result['intervention']} !!!")
