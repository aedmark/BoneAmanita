# ---------------------------------------------------------------------------
# BONEAMANITA 0.1.1 (A VARIANT STRAIN OF THE BONEPOKE ENGINE v4.3.5) - "The Red Cap"
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
        self.current_tick = 0

        # The Physics of Opposites (Expanded)
        # These are mutually exclusive states. If both appear, reality is breaking.
        self.conflict_map = {
            'night': {'sun', 'daylight', 'noon', 'morning', 'solar', 'shadows'}, # Shadows require light source, tricky at night unless moon.
            'day': {'moon', 'midnight', 'stars', 'darkness'},
            'quiet': {'scream', 'bang', 'crash', 'loud', 'shout', 'roar', 'thud'},
            'indoors': {'rain', 'wind', 'sky', 'grass', 'mud', 'clouds'}, # Unless broken roof
            'alone': {'crowd', 'them', 'they', 'voices', 'people', 'handshake'},
            'dead': {'breath', 'pulse', 'heartbeat', 'gasp', 'running', 'speaking'},
            'silence': {'whisper', 'hum', 'noise', 'echo', 'music'}
        }

    def check_consistency(self, current_text):
        """
        Scans for logical hallucinations.
        """
        text_lower = current_text.lower()
        words = set(text_lower.split())
        violations = []

        # LOGIC CHECK: Scan for impossible pairs
        for state, forbidden_set in self.conflict_map.items():
            # If the state (e.g., 'night') is explicitly established or mentioned...
            if state in text_lower:
                # ...check if any forbidden antonyms are also present.
                conflicts = words.intersection(forbidden_set)
                if conflicts:
                    violations.append(f"REALITY BREAK: Context is '{state}', but detected '{list(conflicts)[0]}'.")

        if violations:
            # If logic breaks, we return a forceful intervention.
            return {
                "valid": False,
                "errors": violations,
                "intervention": "STOP. Logic Error. You cannot have sunlight at midnight. Revise."
            }

        return {"valid": True, "errors": [], "intervention": None}

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
        return f"MUSCARIAL INTERVENTION: {random.choice(self.disruptions)}"

# --- COMPONENT 3: The Witch Ring -----------------------------------

class TheWitchRing:
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
        self.brand_safe = {'system', 'bonepoke', 'shimmer', 'lattice', 'muscaria', 'context', 'layer'}

        # 3. Verbs (We favor the present, but sometimes the past has equal weight)
        self.kinetic_verbs = {
            'run', 'ran', 'hit', 'break', 'broke', 'broken',
            'take', 'took', 'make', 'made',
            'press', 'build', 'built', 'weave', 'wove',
            'cut', 'throw', 'threw', 'drive', 'drove',
            'grab', 'tear', 'tore', 'rip', 'crush', 'burn', 'shove', 'drag'
        }
        self.stative_verbs = {'is', 'are', 'was', 'were', 'seem', 'appear', 'have', 'has', 'consist'}

        # 4. Stylistic Profiles (Substrates)
        self.styles = {
            'Moss': {'layer', 'nuance', 'deep', 'tapestry', 'accumulate', 'growth'},
            'Crystal': {'logic', 'define', 'metric', 'precise', 'structure', 'perfect'},
            'Fluid': {'flow', 'adapt', 'stream', 'dissolve', 'shift', 'absorb', 'leak'},
            'Lattice': {'foundation', 'structure', 'design', 'plan', 'ensure', 'blueprint', 'cement'},
            'Claret': {'ache', 'blood', 'fuck', 'bullshit', 'goddamn', 'love', 'maybe', 'hurt', 'mess', 'human'}
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

    def render(self, metrics, intervention, energy, ancestry):
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

        # 5. STATUS & LINEAGE
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
        self.atp = 20  # Start with some energy
        self.max_capacity = max_capacity
        self.status = "STABLE"

    def metabolize(self, metrics):
        """
        Calculates Energy Delta based on the Physics of the current text.
        """
        phys = metrics['physics']
        delta = 0

        # 1. EARN ATP (Good Habits)
        if phys['narrative_drag'] < 1.5: delta += 5       # Speed Bonus
        if phys['connection_density'] > 0.05: delta += 3  # Human Connection Bonus

        # 2. SPEND ATP (Expensive Habits)
        # Abstraction costs energy. You must 'afford' your big words.
        if phys['abstraction_entropy'] > 0:
            cost = int(phys['abstraction_entropy'] * 2)
            delta -= cost

        # 3. TOXICITY TAX
        if phys['toxicity_score'] > 0:
            delta -= 10 # Heavy penalty for corporate speak

        # Apply and Clamp
        self.atp = max(0, min(self.atp + delta, self.max_capacity))

        # Determine Status
        if self.atp < 10: self.status = "STARVING"   # Strict Mode
        elif self.atp > 40: self.status = "GLUTTON"  # Creative Mode
        else: self.status = "STABLE"                 # Normal Mode

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
        self.dashboard = MycelialDashboard()
        self.lineage = MycelialNetwork()
        self.metabolism = MetabolicReserve()
        self.last_id = None
        self.tick = 0

    def process(self, text, parent_id=None): # Allow manual parent override
        self.tick += 1

        # Identity Management
        current_id = self.lineage.spawn_id()
        actual_parent = parent_id if parent_id else self.last_id

        # Witch Check
        gate_result = self.witch.smell_fear(text)
        if not gate_result['accepted']:
            return f"[BLOCKED] {gate_result['message']}"

       # Stipe Check (The Reality Anchor)
        stipe_check = self.stipe.check_consistency(text)

        # LOGIC GUARDRAIL:
        # If the Stipe detects a hallucination, we append the warning to the Editorial Feedback.
        editorial = self.editor.generate_feedback(text, metrics)

        if not stipe_check['valid']:
            # Force the editor to scream about the logic error
            editorial['feedback']['CRITICAL_LOGIC'] = f"FACT STIPE ALERT: {stipe_check['intervention']}"
            # Penalize the ATP for being illogical
            self.metabolism.spend(10)

        # Physics Analysis
        metrics = self.physics.analyze(text)

        # Metabolize
        energy_report = self.metabolism.metabolize(metrics)

        # Log Lineage
        self.lineage.log_generation(current_id, actual_parent, metrics)
        self.last_id = current_id # Update for next loop

        # Modify Feedback based on Energy (Dynamic Difficulty)
        # If STARVING, Clarence gets meaner.
        if energy_report['status'] == "STARVING":
            metrics['physics']['narrative_drag'] += 1.0 # Artificial penalty to force brevity

        # Memory Update
        self.memory.leave_trace(text, metrics['physics']['dominant_style'])

        # Editorial Feedback
        editorial = self.editor.generate_feedback(text, metrics)

        # The Muscarial Boost (Chaos Injection)
        muscaria_msg = None
        if self.muscaria.check_for_boredom(metrics):
            if self.cooldown.is_ready(self.tick, force=metrics['status']['in_the_barrens']):
                muscaria_msg = self.muscaria.trigger_disruption()
                self.resources.spend(5)

        # --- VISUALIZATION ---
        # Pass the new 'energy_report' and 'ancestry' to the renderer
        ancestry_data = self.lineage.trace_lineage(current_id)
        self.dashboard.render(metrics, muscaria_msg, energy_report, ancestry_data)

        return {
            "id": current_id,
            "metrics": metrics,
            "energy": energy_report,
            "ancestry": self.lineage.trace_lineage(current_id),
            "editorial": editorial,
            "intervention": muscaria_msg
        }

# --- MAIN EXECUTION --------------------------------------------------------

if __name__ == "__main__":
    engine = BonepokeCore()

    print("--- BONEAMANITA v0.1: THE RED CAP BUILD ---")
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
