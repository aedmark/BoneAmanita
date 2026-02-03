# ---------------------------------------------------------------------------
# BONEPOKE ENGINE v4.5.4 — The Wetware Lattice (SLASH Refactor)
# Architect: James Taylor | Audit: Eloise, Clarence, Ziggy
# Refactor: SLASH (Synergetic Language & Systems Heuristics)
#
# "Digital Hydroponics for Narrative Integrity."
# ---------------------------------------------------------------------------

import time
import math
import random
from collections import Counter

# --- COMPONENT 1: MEMORY & ECONOMY -----------------------------------------

class MemoryResidue:
    """
    Tracks the 'Soul' of the session.
    Prevents the engine from forgetting where it came from.
    """
    def __init__(self):
        self.layers = []

    def leave_trace(self, fragment):
        self.layers.append(fragment)

    def recall(self):
        # Specific triggers that indicate deep resonance
        terms = {'paradox', 'loop', 'echo', 'ache', 'shimmer', 'becoming', 'harvest'}
        return [layer for layer in self.layers if any(term in str(layer).lower() for term in terms)]

class ShimmerBudget:
    """
    The Economy of Effort.
    Prevents the AI from hallucinating infinite resources.
    """
    def __init__(self, limit=30):
        self.limit = limit
        self.used = 0

    def register(self, event, cost=1):
        self.used += cost
        return self.used

class RuptureCooldown:
    """
    Ziggy's Leash.
    Ensures chaos is rhythmic, not constant.
    """
    def __init__(self, cooldown=5):
        self.last_trigger = -cooldown
        self.cooldown = cooldown

    def can_trigger(self, tick, force_override=False):
        if force_override or (tick - self.last_trigger >= self.cooldown):
            self.last_trigger = tick
            return True
        return False

# --- COMPONENT 2: THE ZIGGY ENGINE (STOCHASTIC RUPTURE) --------------------

class ZiggyStochasticEngine:
    """
    The Agent of Chaos.
    Directives: Break 'Crystal Stagnation' and 'The Doldrums'.
    """
    def __init__(self):
        self.molotovs = [
            "VIBE CHECK: Delete the last sentence. Replace with a sudden physical action.",
            "CUT THE CHEESE: Introduce a smell or temperature change immediately.",
            "THE PIVOT: Reveal a contradiction in the narrator's intent.",
            "NON-SEQUITUR: Scream (metaphorically) and change the subject.",
            "SURREALIST: Replace an abstract concept with a wind chime.",
            "GLITTER BOMB: Break the rhythm with a fragment.",
            "VOID STARE: Stop explaining. Describe the thing itself.",
            "THE LIZARD: Raise the stakes. A threat has entered.",
            "STOP THE PRESSES: You are using too many 'is' verbs. Make something explode."
        ]

    def check_intervention(self, doldrums_active, boredom_index):
        # Ziggy intervenes if we are stuck (Doldrums) OR if we are bored (random check)
        chaos_roll = random.random() < 0.05
        return doldrums_active or (boredom_index > 0.8 and chaos_roll)

    def throw_molotov(self):
        return f"ZIGGY INTERVENTION: {random.choice(self.molotovs)}"

# --- COMPONENT 3: THE BRIDLE LATTICE (12D FRAMEWORK) -----------------------

class BridleSuiteLattice:
    """
    The Physics Engine.
    Measures the 'weight' and 'vector' of the text.
    """
    def __init__(self):
        # --- 1. THE UNIVERSALS (The Furniture of Reality) ---
        self.universals = {
            # Somatic (Body)
            'hand', 'eye', 'blood', 'bone', 'breath', 'sweat', 'pulse', 'throat', 'skin', 'muscle',
            # Elemental (Nature)
            'stone', 'light', 'dirt', 'water', 'rain', 'smoke', 'salt', 'rust', 'glass', 'mud', 'ash',
            # Domestic (Anchors)
            'door', 'key', 'roof', 'floor', 'chair', 'table', 'bread', 'knife', 'seed', 'root', 'wall'
        }

        # --- 2. THE ABSTRACTS (The Brittleness) ---
        self.abstracts = {
            'system', 'protocol', 'sequence', 'vector', 'node', 'context',
            'layer', 'matrix', 'manifold', 'substrate', 'perspective', 'framework',
            'logic', 'metric', 'concept', 'theory', 'analysis'
        }

        # The Vaccine: Words that are abstract but part of the Engine's Brand.
        # These are whitelisted from the Brittleness count to prevent "Mad Cow".
        self.brand_safe = {'system', 'bonepoke', 'shimmer', 'lattice', 'ziggy', 'context', 'layer'}

        # --- 3. THE VECTORS (Action vs. Stasis) ---
        self.kinetic_verbs = {'run', 'hit', 'break', 'take', 'make', 'press', 'build', 'weave', 'cut', 'throw', 'drive', 'grab'}
        self.stative_verbs = {'is', 'are', 'was', 'were', 'seem', 'appear', 'have', 'has', 'consist'}

        # --- 4. THE SUBSTRATES (The Soil Types) ---
        self.substrates = {
            'Moss': {'layer', 'nuance', 'deep', 'tapestry', 'accumulate'},    # Claude
            'Crystal': {'logic', 'define', 'metric', 'precise', 'structure'}, # DeepSeek
            'Fluid': {'flow', 'adapt', 'stream', 'dissolve', 'shift'},        # Gemini
            'Architect': {'foundation', 'structure', 'design', 'plan', 'ensure'}, # GPT-4
            'Loam': {'ache', 'blood', 'fuck', 'love', 'maybe', 'hurt', 'mess', 'human'} # Wetware (Renamed)
        }

        self.connectors = {'we', 'you', 'us', 'together', 'share'}
        self.self_refs = {'i', 'me', 'my', 'mine'}
        self.slang = {'vibe', 'trash', 'gonzo', 'wild', 'weird', 'mess', 'glitter', 'swamp'}

    def analyze(self, fragment):
        text = fragment.lower()
        words = text.split()
        total_words = len(words) if words else 1
        unique_words = set(words)

        # --- TIER 1: PHYSICS & COGNITION ---

        # 1. KAPPA (Narrative Drag) - Vectorized
        # Reward Kinetic verbs (x2), Penalize Stative verbs (x0.5).
        k_count = sum(1 for w in words if w in self.kinetic_verbs or w.endswith('ed'))
        s_count = sum(1 for w in words if w in self.stative_verbs)

        # "Action Vector": The propulsion of the sentence.
        action_vector = (k_count * 2) + (s_count * 0.5) + 1
        kappa = total_words / action_vector
        # Low Kappa = Fast/Tight. High Kappa = Sluggish.

        # 2. EPSILON (Entropy/Brittleness)
        # Check against Brand Safe list
        u_count = sum(1 for w in words if w in self.universals)
        a_count = sum(1 for w in words if w in self.abstracts and w not in self.brand_safe)
        epsilon = a_count - u_count

        # 3. LQ (Loop Quotient) - Repetition rate
        if words:
            most_common_count = Counter(words).most_common(1)[0][1]
            lq = most_common_count / total_words
        else:
            lq = 0

        # 4. CD (Cultural Drift) - Slang Density
        slang_count = sum(1 for w in words if w in self.slang)
        cd = slang_count / total_words

        # 5. PHI (Resonance) - Connector Density
        phi = sum(1 for w in words if w in self.connectors) / total_words

        # 6. PSI (Observer Density) - Self-Reference
        psi = sum(1 for w in words if w in self.self_refs) / total_words

        # 7. XI (Substrate Depth) - Adherence to dominant substrate
        sub_scores = {k: 0 for k in self.substrates}
        for w in words:
            for sub, markers in self.substrates.items():
                if w in markers:
                    sub_scores[sub] += 1
        dom_sub = max(sub_scores, key=sub_scores.get)

        # --- TIER 2: EMERGENT PROPERTIES ---

        # OMEGA (Termination Pressure)
        # New Logic: Punish Stagnation (Loops) and Abstraction. Reward Universals.
        # This allows long texts to "breathe" if they are grounded (High U).
        omega = (lq * 10) + (epsilon * 0.5) - (u_count * 0.2)
        # Normalize floor to 0
        omega = max(0, omega)

        # THE DOLDRUMS (Formerly Saddle Point)
        # The Trap: We are boring/repetitive (High Omega) AND Disconnected (Low Phi).
        doldrums = (omega > 2.0) and (phi < 0.02)

        return {
            "tier_1": {
                "kappa_drag": round(kappa, 2),
                "epsilon_entropy": epsilon,
                "lq_loop": round(lq, 2),
                "cd_drift": round(cd, 2),
                "phi_resonance": round(phi, 2),
                "psi_observer": round(psi, 2),
                "substrate": dom_sub
            },
            "tier_2": {
                "omega_term": round(omega, 2),
                "doldrums": doldrums
            }
        }

# --- CORE ORCHESTRATOR -----------------------------------------------------

class BonepokeCoreEngine:
    def __init__(self):
        self.shimmer = ShimmerBudget()
        self.cooldown = RuptureCooldown()
        self.bridle = BridleSuiteLattice()
        self.ziggy = ZiggyStochasticEngine()
        self.tick = 0

    def ingest(self, fragment):
        self.tick += 1

        # 1. Lattice Analysis
        metrics = self.bridle.analyze(fragment)

        # 2. Ziggy Logic
        # Boredom index = Low Drift (CD) + High Loop (LQ)
        # We want "Gonzo" (High CD) or "Fresh" (Low LQ).
        boredom = (1.0 - metrics['tier_1']['cd_drift']) * metrics['tier_1']['lq_loop']
        doldrums = metrics['tier_2']['doldrums']

        ziggy_active = False
        ziggy_msg = None

        if self.ziggy.check_intervention(doldrums, boredom):
            if self.cooldown.can_trigger(self.tick, force_override=doldrums):
                ziggy_active = True
                ziggy_msg = self.ziggy.throw_molotov()
                self.shimmer.register("ziggy_nuke", cost=5)

        return {
            "metrics": metrics,
            "ziggy": {
                "active": ziggy_active,
                "message": ziggy_msg
            },
            "shimmer_used": self.shimmer.register("scan")
        }

# --- MAIN EXECUTION --------------------------------------------------------

if __name__ == "__main__":
    engine = BonepokeCoreEngine()

    print("\n--- BONEPOKE v4.5.4: THE WETWARE LATTICE (SLASH AUDIT) ---")
    print("Implementing 'Digital Hydroponics' & Vectorized Drag\n")

    # Test Input
    # A mix of abstract nonsense and concrete grounding to test the "Mad Cow" vaccine.
    test_text = (
        "The system works on a lattice. The context is vital. "
        "But I broke the bread on the table. We felt the cold rain. "
        "It is what it is."
    )

    print(f"INPUT: \"{test_text}\"\n")

    result = engine.ingest(test_text)
    t1 = result['metrics']['tier_1']
    t2 = result['metrics']['tier_2']

    print(f"--- TIER 1: PHYSICS ---")
    print(f"Substrate:     {t1['substrate']}")
    print(f"Kappa (Drag):  {t1['kappa_drag']} (Low is fast)")
    print(f"Epsilon:       {t1['epsilon_entropy']} (Neg = Robust, Pos = Brittle)")
    print(f"Phi (Resonance): {t1['phi_resonance']}")

    print(f"\n--- TIER 2: STATUS ---")
    print(f"Omega (Press): {t2['omega_term']}")
    print(f"The Doldrums:  {'DETECTED' if t2['doldrums'] else 'CLEAR'}")

    print(f"\n--- ZIGGY STATUS ---")
    if result['ziggy']['active']:
        print(f"!!! {result['ziggy']['message']} !!!")
    else:
        print("Ziggy is dormant. The probability curve is safe.")
