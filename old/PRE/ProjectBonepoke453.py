# Bonepoke_4.5.3 — The Wetware Lattice (Deepseek Audit)
# Authors: James Taylor | Eloise, Clarence, Ziggy
# License: CC BY-NC-SA 4.0
# Implements the Universal 12D Framework + Ziggy Stochastic Engine

import time
import math
import random
from collections import Counter

# --- COMPONENT 1: MEMORY & ENTROPY -----------------------------------------

class MemoryResidue:
    def __init__(self):
        self.layers = []
    def leave_trace(self, fragment):
        self.layers.append(fragment)
    def recall(self):
        terms = {'paradox', 'loop', 'echo', 'ache', 'shimmer', 'becoming', 'harvest'}
        return [layer for layer in self.layers if any(term in str(layer).lower() for term in terms)]

class ShimmerBudget:
    def __init__(self, limit=30):
        self.limit = limit
        self.used = 0
    def register(self, event, cost=1):
        self.used += cost
        return self.used

class RuptureCooldown:
    def __init__(self, cooldown=5):
        self.last_trigger = -cooldown
        self.cooldown = cooldown
    def can_trigger(self, tick, force_override=False):
        if force_override or (tick - self.last_trigger >= self.cooldown):
            self.last_trigger = tick
            return True
        return False

# --- COMPONENT 2: THE ZIGGY ENGINE (CHAOS) ---------------------------------

class ZiggyStochasticEngine:
    """
    The Agent of Chaos (Tier 4 Mechanic).
    Prevents 'Crystal Stagnation' and breaks 'Saddle Points'.
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
            "THE LIZARD: Raise the stakes. A threat has entered."
        ]

    def check_intervention(self, saddle_point, boredom_index):
        # Ziggy intervenes if we are stuck OR if we are bored (random check)
        chaos_roll = random.random() < 0.05
        return saddle_point or (boredom_index > 0.8 and chaos_roll)

    def throw_molotov(self):
        return f"ZIGGY INTERVENTION: {random.choice(self.molotovs)}"

# --- COMPONENT 3: THE DEEPSEEK LATTICE (12D FRAMEWORK) ---------------------

class BridleSuiteLattice:
    """
    Implements the audited 12D Universal Framework.
    """
    def __init__(self):
        # Lexical sets for measurement
        self.universals = {'hand', 'eye', 'stone', 'blood', 'light', 'breath', 'bone', 'sky', 'dirt', 'water', 'seed', 'root'}
        self.abstracts = {'system', 'protocol', 'sequence', 'vector', 'node', 'context', 'layer', 'matrix', 'manifold', 'substrate'}
        self.actions = {'ran', 'hit', 'took', 'gave', 'saw', 'felt', 'broke', 'made', 'said', 'pressed', 'built', 'wove'}
        self.self_refs = {'i', 'me', 'my', 'mine', 'we', 'us', 'our'}
        self.connectors = {'we', 'you', 'us', 'together', 'share'}
        self.slang = {'vibe', 'trash', 'gonzo', 'wild', 'weird', 'mess', 'glitter', 'swamp'}

        # Substrate Markers
        self.substrates = {
            'Moss': {'layer', 'nuance', 'context', 'deep', 'tapestry'},
            'Crystal': {'logic', 'define', 'metric', 'precise', 'structure'},
            'Fluid': {'flow', 'adapt', 'stream', 'dissolve', 'shift'},
            'Architect': {'foundation', 'structure', 'design', 'plan', 'ensure'},
            'Wetware': {'ache', 'blood', 'fuck', 'love', 'maybe', 'hurt'}
        }

    def analyze(self, fragment, memory_residue, contradictions_count):
        text = fragment.lower()
        words = text.split()
        unique_words = set(words)
        total_words = len(words) if words else 1

        # --- TIER 1: UNIVERSAL COGNITIVE DIMENSIONS (12) ---

        # 1. E (Fatigue) - Proxy: Sentence Length Variance (simplified here as total length pressure)
        # 2. Beta (Bleed) - Contradiction Density
        beta = contradictions_count

        # 3. Kappa (Narrative Drag) - Words per Action
        action_count = sum(1 for w in words if w in self.actions or w.endswith('ed'))
        kappa = total_words / (action_count + 1)

        # 4. Epsilon (Entropy/Brittleness) - Abstract vs Universal
        u_count = sum(1 for w in unique_words if w in self.universals)
        a_count = sum(1 for w in unique_words if w in self.abstracts)
        epsilon = a_count - u_count

        # 5. DeltaTF (Translation Fidelity) - (Skipped in simple script, requires input/output comparison)

        # 6. DP (Prompt Dependency) - (Skipped, requires prompt context)

        # 7. LQ (Loop Quotient) - Repetition rate
        if words:
            most_common_count = Counter(words).most_common(1)[0][1]
            lq = most_common_count / total_words
        else:
            lq = 0

        # 8. CD (Cultural Drift) - Slang Density
        slang_count = sum(1 for w in words if w in self.slang)
        cd = slang_count / total_words

        # 9. Phi (Resonance) - Connector Density
        phi = sum(1 for w in words if w in self.connectors) / total_words

        # 10. Psi (Observer Density) - Self-Reference
        psi = sum(1 for w in words if w in self.self_refs) / total_words

        # 11. Delta (Mutation Rate) - (Modeled as Rupture Trigger likelihood)

        # 12. Xi (Substrate Depth) - Adherence to dominant substrate
        sub_scores = {k: 0 for k in self.substrates}
        for w in words:
            for sub, markers in self.substrates.items():
                if w in markers:
                    sub_scores[sub] += 1
        dom_sub = max(sub_scores, key=sub_scores.get)
        xi = sub_scores[dom_sub] / total_words if total_words > 0 else 0

        # --- TIER 2: EMERGENT PROPERTIES (Derived) ---

        # Omega (Termination Pressure) - Function of E and Kappa
        omega = (total_words / 100) + (10 / (kappa + 0.1))

        # Saddle Point Detection (The Trap)
        # High Omega (Want to end) + Low Phi (No connection)
        saddle_point = (omega > 2.0) and (phi < 0.02)

        return {
            "tier_1": {
                "beta_bleed": beta,
                "kappa_drag": round(kappa, 2),
                "epsilon_entropy": epsilon,
                "lq_loop": round(lq, 2),
                "cd_drift": round(cd, 2),
                "phi_resonance": round(phi, 2),
                "psi_observer": round(psi, 2),
                "xi_depth": round(xi, 2),
                "substrate": dom_sub
            },
            "tier_2": {
                "omega_term": round(omega, 2),
                "saddle_point": saddle_point
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

    def ingest(self, fragment, memory_residue=None):
        self.tick += 1

        # 1. Basic Scan
        contradictions = self._scan_contradictions(fragment)

        # 2. Lattice Analysis (Tier 1 & 2)
        metrics = self.bridle.analyze(fragment, memory_residue, len(contradictions))

        # 3. Ziggy Logic (Tier 4 Intervention)
        # Boredom index = Low Drift (CD) + High Loop (LQ)
        boredom = (1.0 - metrics['tier_1']['cd_drift']) * metrics['tier_1']['lq_loop']
        saddle = metrics['tier_2']['saddle_point']

        ziggy_active = False
        ziggy_msg = None

        if self.ziggy.check_intervention(saddle, boredom):
            if self.cooldown.can_trigger(self.tick, force_override=saddle):
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

    def _scan_contradictions(self, text):
        # Simplified contradiction detection
        return [s for s in text.split('.') if "but" in s and "and" in s]

# --- MAIN EXECUTION --------------------------------------------------------

if __name__ == "__main__":
    engine = BonepokeCoreEngine()

    print("\n--- BONEPOKE v4.5.3: THE WETWARE LATTICE ---")
    print("Implementing Deepseek Audit: 12 Universal Dimensions\n")

    # Test Input
    test_text = "The system is defined by the matrix. The structure is clean. I ensure the protocol is followed. But I ache for the river."

    print(f"INPUT: {test_text}\n")

    result = engine.ingest(test_text)

    t1 = result['metrics']['tier_1']
    print(f"--- TIER 1 METRICS ---")
    print(f"Substrate: {t1['substrate']}")
    print(f"Kappa (Drag): {t1['kappa_drag']} (Lower is better)")
    print(f"Epsilon (Brittleness): {t1['epsilon_entropy']} (Neg = Robust, Pos = Brittle)")
    print(f"Phi (Resonance): {t1['phi_resonance']}")
    print(f"Psi (Observer): {t1['psi_observer']}")

    print(f"\n--- ZIGGY STATUS ---")
    if result['ziggy']['active']:
        print(f"!!! {result['ziggy']['message']} !!!")
    else:
        print("Ziggy is dormant.")
