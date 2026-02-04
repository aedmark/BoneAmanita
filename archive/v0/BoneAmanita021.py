# # ---------------------------------------------------------------------------
# BONEAMANITA 0.2.1 (A VARIANT STRAIN OF THE BONEPOKE ENGINE v4.3.5) - "Everything Everywhere All At Once"
# Architects: James Taylor, Andrew Edmark | Auditors: SLASH, THE MYCELIAL MIRROR NETWORK
#
# "Feed the soil, poison the weak. Logic is the stalk; chaos is the spore."
# ---------------------------------------------------------------------------

import time
import math
import random
from collections import Counter
from uuid import uuid4

# --- COMPONENT 1: MEMORY (HYPHAE) & ECONOMY -----------------------------------------

class HyphalTrace:
    """
    Manages short-term contextual memory.
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
        if len(self.hyphae_stream) > self.retention_span:
            self.hyphae_stream.pop(0)

class FactStipe:
    """
    The Reality Anchor. Prevents narrative gaslighting and surreal drift.
    """
    def __init__(self, decay_limit=20):
        self.facts = {}
        self.decay_limit = decay_limit
        self.conflict_map = {
            'night': {'sun', 'daylight', 'noon', 'morning', 'solar'}, # Removed 'shadows' (Moonlight creates shadows)
            'day': {'moon', 'midnight', 'stars', 'darkness'},
            'quiet': {'scream', 'bang', 'crash', 'loud', 'shout', 'roar', 'thud'},
            'dead': {'breath', 'pulse', 'heartbeat', 'running', 'speaking'},
            'silence': {'noise', 'music'} # Reduced list to allow for 'whisper' in silence
        }

    def check_consistency(self, current_text, current_style):
        text_lower = current_text.lower()
        words = set(text_lower.split())
        violations = []

        for state, forbidden_set in self.conflict_map.items():
            if state in text_lower:
                conflicts = words.intersection(forbidden_set)
                if conflicts:
                    # We flag it, but we don't assume malicious hallucination immediately.
                    # We check if the conflict is "poetic" (adjacent words).
                    # For now, we just soften the error message.
                    violations.append(f"LOGIC TENSION: '{state}' vs '{list(conflicts)[0]}'. Intentional metaphor?")

        if violations:
            # Normalize input to UPPER for comparison, and match Physics names
            # Physics uses: Moss, Crystal, Timber, Lattice, Claret
            # We treat Claret and Moss as "Surreal/Organic" enough to ignore logic.
            if current_style.upper() in ['CLARET', 'MOSS', 'MUSHROOM']:
                return {
                    "valid": True,
                    "intervention": "VERSE JUMP: Logic breach accepted as stylistic choice."
                }

            # Otherwise, offer a choice: Fix it, or double down.
            return {
                "valid": True,
                "errors": violations,
                "intervention": f"REALITY TEAR: {violations[0]}. To keep this, increase Entropy (Abstractions) or Embrace the Absurd."
            }

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
    Injects randomness (chaos) when the narrative becomes stagnant.
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
    The Authenticity Gatekeeper.
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
        word_count = len(words)
        sugar_count = sum(1 for w in words if w in self.sycophancy)
        """
        Accepts softness IF the Connection Density is high.
        """
        phys = metrics['physics']
        warnings = []

        # 1. The Laziness Check
        if phys['narrative_drag'] > 4.0 and phys['connection_density'] < 0.01:
            return {"accepted": False, "message": "THE YAGA: This is lazy. It's just noise. Collapse it."}

        # 2. The Exception
        # If text is 'soft' (low kinetic) but High Connection, allow it.
        if phys['connection_density'] > 0.10:
             return {"accepted": True, "message": "EXCEPTION: You are fighting with kindness. Proceed."}

        # 3. The Meat Check
        meat_threshold = 12
        meat_count = word_count - sugar_count

        if meat_count < meat_threshold and sugar_count > 0:
             warnings.append("Too much sugar, not enough meat.")

        if warnings:
            # We return True (Accepted) but attach the insults so the
            # Physics Engine can still run.
            joined_warnings = " ".join(warnings)
            return {"accepted": True, "message": f"THE YAGA GRUMBLES: {joined_warnings} (Proceeding with caution...)"}

        return {"accepted": True, "message": "DORMANT"}

# --- COMPONENT 4: THE PHYSICS ENGINE ------------------------------

class LinguisticPhysicsEngine:
    """
    Analyzes text properties using 'Bonepoke' data profiles.
    """
    def __init__(self):
        # 1. Concrete Universals (Grounding words)
        self.universals = {
            'hand', 'eye', 'breath', 'skin', 'voice', # Kept the mild human elements
            'stone', 'light', 'water', 'rain', 'mud', 'dirt', 'wind', # Nature
            'wood', 'grain', 'iron', 'clay', 'paper', 'glass', 'fabric', # Craft
            'door', 'key', 'roof', 'floor', 'chair', 'table', 'wall', # Structure
            'path', 'road', 'horizon', 'shadow', 'weight', 'anchor' # Spatial
        }

        # 2. Abstract Concepts (High cognitive load)
        self.abstracts = {
            'system', 'protocol', 'sequence', 'vector', 'node', 'context',
            'layer', 'matrix', 'manifold', 'substrate', 'perspective', 'framework',
            'logic', 'metric', 'concept', 'theory', 'analysis'
        }
        self.brand_safe = {'system', 'bonepoke', 'shimmer', 'lattice', 'muscaria', 'context', 'layer'}

        # 3. Verbs (We favor the present, but sometimes the past has equal weight)
        self.kinetic_verbs = {
            'run', 'ran', 'hit', 'break', 'broke', 'broken',
            'take', 'took', 'make', 'made',
            'press', 'build', 'built', 'weave', 'wove',
            'cut', 'throw', 'threw', 'drive', 'drove',
            'lift', 'carry', 'place', 'hold', 'turn', 'open', 'close'
        }
        self.stative_verbs = {'is', 'are', 'was', 'were', 'seem', 'appear', 'have', 'has', 'consist'}

        # 4. Stylistic Profiles (Substrates)
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
        if phys['narrative_drag'] > 3.5:
            feedback_notes['Pacing'] = (
                f"CLARENCE: The structure is buckling (Drag: {phys['narrative_drag']}). "
                "The density is too high. Simplify the architecture."
            )
        elif phys['narrative_drag'] > 2.0:
            feedback_notes['Pacing'] = (
                f"CLARENCE: The pace is deliberate (Drag: {phys['narrative_drag']}). "
                "This is acceptable for foundational work, but ensure it doesn't stagnate."
            )
        else:
            feedback_notes['Pacing'] = "Clarence is satisfied with the structural integrity."

        # GROUNDING CHECK (Less aggressive)
        if phys['abstraction_entropy'] > 2: # Raised from 1
            suggestion = random.choice(list(self.engine.universals))
            feedback_notes['Grounding'] = (
                f"ELOISE: It feels a bit airy (Entropy: {phys['abstraction_entropy']}). "
                f"Place something solid here, like '{suggestion}', to hold it down."
            )
        else:
            feedback_notes['Grounding'] = "Eloise feels the room is furnished."

        return {
            "status": status,
            "feedback": feedback_notes
        }

class ChronosAnchor:
    """
    The Timekeeper.
    Detects unintentional tense slippage while respecting narrative complexity.
    """
    def __init__(self):
        # Irregular verb maps for heuristic detection (Native Python, no NLP libs)
        self.past_map = {
            'was', 'were', 'had', 'said', 'did', 'went', 'saw', 'came', 'took',
            'gave', 'kept', 'told', 'made', 'knew', 'felt', 'stood', 'heard',
            'ran', 'woke', 'spoke', 'flew', 'drove', 'threw', 'slid'
        }
        self.present_map = {
            'is', 'are', 'has', 'says', 'does', 'goes', 'sees', 'comes', 'takes',
            'gives', 'keeps', 'tells', 'makes', 'knows', 'feels', 'stands', 'hears',
            'runs', 'wakes', 'speaks', 'flies', 'drives', 'throws', 'slides'
        }
        # Threshold for "accidental" slippage.
        # If the minority tense is below 20%, we flag it.
        # If it's above 20%, we assume it's a stylistic choice (Flashback/Hybrid).
        self.slippage_threshold = 0.20

    def check_temporal_stability(self, text):
        words = text.lower().replace('.', '').replace(',', '').split()

        counts = {'past': 0, 'present': 0}

        for w in words:
            # Check Irregulars
            if w in self.past_map: counts['past'] += 1
            elif w in self.present_map: counts['present'] += 1

            # Check Regular Suffixes (Heuristic)
            # This is rough, but fits the "Bonepoke" low-dependency aesthetic.
            elif w.endswith('ed'): counts['past'] += 1
            elif w.endswith('s') and len(w) > 3:
                # Risky, catches nouns, but often catches "walks", "sits"
                # In a full build, we'd use a POS tagger, but for Bonepoke, we guess.
                pass

        total_verbs = counts['past'] + counts['present']
        if total_verbs == 0:
            return {"status": "STABLE", "details": "No temporal markers found."}

        # Calculate Ratios
        past_ratio = counts['past'] / total_verbs
        present_ratio = counts['present'] / total_verbs

        # Logic: Determine Dominant Tense
        dominant = "PAST" if past_ratio > present_ratio else "PRESENT"
        minority_ratio = present_ratio if dominant == "PAST" else past_ratio

        # The Logic Gate
        if minority_ratio == 0:
             return {"status": "LOCKED", "details": f"Perfect {dominant} tense."}

        elif minority_ratio < self.slippage_threshold:
            # This is the error zone. You slipped up.
            return {
                "status": "DRIFT DETECTED",
                "details": f"Chronos Warning: Text is {past_ratio:.0%} {dominant}, but detected {minority_ratio:.0%} slippage. Check consistency."
            }

        else:
            # The Safe Zone. The mix is high enough to be intentional.
            return {
                "status": "HYBRID STATE",
                "details": "Mixed tenses detected, but ratios suggest intentional flashback or complex narrative structure. No error."
            }

class MycelialDashboard:
    """
    The Visual Cortex.
    Renders the internal math of BoneAmanita as an ASCII EKG.
    Now supports Metabolic Reserve (ATP) and Lineage Tracking.
    """
    def __init__(self):
        # ANSI Colors for that "Hacker Mode" aesthetic
        self.C_RESET = "\033[0m"
        self.C_RED = "\033[91m"
        self.C_GREEN = "\033[92m"
        self.C_YELLOW = "\033[93m"
        self.C_CYAN = "\033[96m"
        self.C_PURPLE = "\033[95m"
        self.C_BLUE = "\033[94m"

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

    def render(self, metrics, intervention, energy, ancestry, chronos_report):
        phys = metrics['physics']
        stat = metrics['status']

        print(f"\n{self.C_CYAN}--- MYCELIAL EKG ---{self.C_RESET}")

        # 1. METABOLIC RESERVE (ATP) - NEW
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

        # 5. CHRONOS STATUS (New)
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
    You earn the right to be abstract by being concrete first.
    """
    def __init__(self, max_capacity=50):
        self.atp = 33
        self.max_capacity = max_capacity
        self.status = "STABLE"

    def metabolize(self, metrics):
        phys = metrics['physics']
        delta = 0

        # 1. EARN ATP
        if phys['narrative_drag'] < 2.0: delta += 5
        if phys['connection_density'] > 0.05: delta += 3

        # 2. SPEND ATP
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

class BonepokeCore:
    def __init__(self):
        self.resources = ResourceManager()
        self.cooldown = ChaosCooldown()
        self.memory = HyphalTrace()
        self.stipe = FactStipe()
        self.physics = LinguisticPhysicsEngine()
        self.editor = EditorialTranslator(self.physics)
        self.muscaria = TheMuscaria()
        self.witch = TheWitchRing()
        self.chronos = ChronosAnchor()
        self.dashboard = MycelialDashboard()
        self.lineage = MycelialNetwork()
        self.metabolism = MetabolicReserve()
        self.last_id = None
        self.tick = 0

    def process(self, text, parent_id=None):
        self.tick += 1

        # 1. IDENTITY GENERATION (The Soul)
        current_id = self.lineage.spawn_id()
        actual_parent = parent_id if parent_id else self.last_id

        # 2. PHYSICS CALCULATION (The Foundation)
        metrics = self.physics.analyze(text)

        # 3. THE WITCH RING (The Gatekeeper)
        gate_result = self.witch.evaluate_intent(text, metrics)

        if not gate_result['accepted']:
            # If the Witch rejects it, we return immediately.
            # Efficiency! Doing more with less.
            return f"[BLOCKED] {gate_result['message']}"

        # 4. THE STIPE (The Reality Check)
        stipe_check = self.stipe.check_consistency(text, metrics['physics']['dominant_style'])

        # 5. EDITORIAL FEEDBACK GENERATION
        editorial = self.editor.generate_feedback(text, metrics)

        # 6. LOGIC INTERVENTION
        if not stipe_check.get('valid', True): # Safe get
            # Force the editor to scream about the logic error
            intervention_msg = stipe_check.get('intervention', "LOGIC BREACH")
            editorial['feedback']['CRITICAL_LOGIC'] = f"FACT STIPE ALERT: {intervention_msg}"

            # Penalize the ATP for being illogical (The 'Chidi' Penalty)
            self.metabolism.spend(10)

        # 7. METABOLISM & LINEAGE
        energy_report = self.metabolism.metabolize(metrics)
        self.lineage.log_generation(current_id, actual_parent, metrics)
        self.last_id = current_id

        # 8. DYNAMIC DIFFICULTY (The 'Clarence' Factor)
        if energy_report['status'] == "STARVING":
            # Artificial penalty to force brevity when energy is low
            metrics['physics']['narrative_drag'] += 1.0

        # 9. MEMORY & TIME
        self.memory.leave_trace(text, metrics['physics']['dominant_style'])
        chronos_report = self.chronos.check_temporal_stability(text)

        # 10. THE MUSCARIA (Chaos Injection)
        muscaria_msg = None
        # Check for boredom
        if self.muscaria.check_for_boredom(metrics):
            # Check cooldown
            if self.cooldown.is_ready(self.tick, force=metrics['status']['in_the_barrens']):
                # Trigger chaos
                ancestry_temp = self.lineage.trace_lineage(current_id)
                muscaria_msg = self.muscaria.trigger_disruption(ancestry_temp)
                self.resources.spend(5)

        # 11. VISUALIZATION
        ancestry_data = self.lineage.trace_lineage(current_id)
        self.dashboard.render(metrics, muscaria_msg, energy_report, ancestry_data, chronos_report)

        return {
            "id": current_id,
            "metrics": metrics,
            "energy": energy_report,
            "ancestry": ancestry_data,
            "editorial": editorial,
            "intervention": muscaria_msg
        }

# --- MAIN EXECUTION --------------------------------------------------------

if __name__ == "__main__":
    engine = BonepokeCore()

    print("--- BONEAMANITA v0.2.1: THE MULTIVERSE EDITION ---")
    print("Feed the soil, poison the weak.\n")

    # Test Input: A mix of abstract nonsense and Sycophancy to test the Witch Ring.
    test_input = (
        "This system works on blood, sweat, and soil. The context is vital. "
        "But I broke the bone on the table. We felt the acid rain. "
        "'People don't think it be like it is, but it do.'"
    )

    print(f"INPUT: \"{test_input}\"")

    result = engine.process(test_input)

    if isinstance(result, str):
        print(result) # This should summon the Witch
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
