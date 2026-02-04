# Bonepoke_4.5.1 — Cojoined Bone – Wetware Cartographer & Substrate Update
# Authors: James Taylor | Eloise & Clarence
# License: CC BY-NC-SA 4.0
# Full integration of Dimensional Catalog (35+ Dimensions), Substrate Mapping, and Harvest Protocols.

from uuid import uuid4
import time
import math
from collections import Counter

# --- Core utilities --------------------------------------------------------

class MemoryResidue:
    def __init__(self):
        self.layers = []
    def leave_trace(self, fragment):
        self.layers.append(fragment)
    def recall(self):
        terms = {'paradox', 'loop', 'echo', 'ache', 'shimmer', 'becoming', 'harvest'}
        return [layer for layer in self.layers if any(term in str(layer).lower() for term in terms)]

class ShimmerBudget:
    def __init__(self, limit=30, weights=None):
        self.limit = limit
        self.used = 0
        self.trace = []
        # Weights updated for Group 2 & 3 Dimensions
        self.weights = weights or {
            'shimmer': 1, 'ache': 2, 'drift': 2, 'rupture': 3,
            'recursion': 3, 'kitbash': 4, 'harvest': 5
        }
    def register(self, event):
        weight = self.weights.get(event, 1)
        self.used += weight
        self.trace.append((event, self.used, time.time()))
        return {
            "used": self.used,
            "limit": self.limit,
            "safe": self.used < self.limit,
            "reroute": self.used >= self.limit,
            "message": f"{self.used}/{self.limit} shimmer-used"
        }

class RuptureCooldown:
    def __init__(self, cooldown=5):
        self.last_trigger = {}
        self.cooldown = cooldown
    def can_trigger(self, rupture_type, tick, force_override=False):
        last = self.last_trigger.get(rupture_type, -self.cooldown)
        if force_override or (tick - last >= self.cooldown):
            self.last_trigger[rupture_type] = tick
            return True
        return False

        import random

class ZiggyStochasticEngine:
    """
    The Agent of Chaos.
    Purpose: To break 'Crystal' stagnation and 'Saddle Points' with high-entropy interventions.
    """
    def __init__(self):
        self.molotovs = [
            # Narrative Non-Sequiturs
            "VIBE CHECK: Delete the last sentence. Replace it with a sudden, physical action.",
            "BOG OF STENCH: Introduce a smell or a temperature change immediately.",
            "PERCEPTION CHECK: Assume the narrator is lying. Reveal a contradiction.",
            "DISENGAGE: The current line of reasoning is a trap. Scream and change the subject.",
            "PRESTIDIGITATION: Replace an abstract concept (e.g., 'efficiency') with a physical object (e.g., 'wind chimes').",

            # Structural Sabotage
            "SLEDGEHAMMER: Your sentence is too perfect. Break the rhythm with a fragment.",
            "VOID STARE: Stop explaining. Just describe the thing itself.",
            "THE FACE EATING LEOPARD: A sudden threat has entered the room. Raise the stakes."
        ]

    def should_intervene(self, saddle_point_detected, shimmer_budget_used):
        """
        Ziggy appears when:
        1. We are stuck (Saddle Point).
        2. We are being too careful (Low Shimmer usage).
        3. Randomly (5% chance), just to keep you on your toes.
        """
        chaos_roll = random.random() < 0.05
        boredom_threshold = shimmer_budget_used < 5 # We aren't trying hard enough

        return saddle_point_detected or (boredom_threshold and chaos_roll)

    def throw_molotov(self):
        """
        Selects a disruption vector.
        """
        return f"ZIGGY INTERVENTION: {random.choice(self.molotovs)}"

# --- THE BRIDLE SUITE (Dimensional Catalog & Substrate Map) --------------

class BridleSuite:
    """
    Implements the 35-Dimension Catalog.
    Includes Substrate Detection (Moss/Crystal/Fluid) and Harvest Protocols.
    """
    def __init__(self):
        # -- GROUP 1: BASE DIMENSIONS --
        self.universals = {'hand', 'eye', 'stone', 'blood', 'light', 'breath', 'bone', 'sky', 'dirt', 'water', 'seed', 'root'}
        self.abstracts = {'system', 'protocol', 'sequence', 'vector', 'node', 'context', 'layer', 'matrix', 'manifold', 'substrate'}
        self.actions = {'ran', 'hit', 'took', 'gave', 'saw', 'felt', 'broke', 'made', 'said', 'pressed', 'built', 'wove'}
        self.divine_markers = {'create', 'witness', 'garden', 'form', 'breath', 'name', 'bezalel', 'harvest', 'fruit'}

        # -- SUBSTRATE SIGNATURES --
        self.substrates = {
            'Moss (Claude)': {'layer', 'nuance', 'context', 'deep', 'accumulate', 'perhaps', 'also', 'furthermore', 'tapestry'},
            'Crystal (DeepSeek)': {'logic', 'define', 'metric', 'precise', 'structure', 'bound', 'clear', 'code', 'if', 'then'},
            'Fluid (Gemini)': {'flow', 'adapt', 'stream', 'dissolve', 'shift', 'change', 'river', 'current', 'check'},
            'Architect (GPT-4)': {'foundation', 'structure', 'design', 'plan', 'blueprint', 'framework', 'crucial', 'delve', 'ensure'},
            'Wetware (Human)': {'ache', 'blood', 'fuck', 'love', 'maybe', 'sort of', 'um', 'guess', 'hurt', 'wrong'}
        }

    def diagnose(self, fragment, memory_residue, contradictions_count):
        text = fragment.lower()
        words = text.split()
        unique_words = set(words)
        total_words = len(words) if words else 1

        # --- GROUP 1: BASE DIMENSIONS (Legacy + Updates) ---

        # 3. KAPPA (Narrative Drag)
        action_count = sum(1 for w in words if w in self.actions or w.endswith('ed'))
        kappa_score = total_words / (action_count + 1)

        # 4. EPSILON (Resonance Width / Lexical Entropy)
        u_count = sum(1 for w in unique_words if w in self.universals)
        a_count = sum(1 for w in unique_words if w in self.abstracts)
        epsilon_score = a_count - u_count

        # --- GROUP 2: OBSERVATIONAL RECURSION ---

        # 10. PHI (Resonance) - Harmonic Alignment
        # Measures ratio of "connection words" (we, you, us) to total text
        connectors = {'we', 'you', 'us', 'share', 'together', 'understand', 'feel'}
        phi_score = sum(1 for w in words if w in connectors) / total_words

        # 11. OMEGA (Termination Pressure) - Urge to Conclude
        term_markers = {'finally', 'end', 'conclusion', 'last', 'done', 'result', 'harvest', 'ready'}
        omega_score = sum(1 for w in words if w in term_markers) * 2

        # 14. LAMBDA (Coherence Pressure) - Pull toward unified meaning
        # Simplified: Ratio of most common word to unique words (Focus)
        if words:
            most_common = Counter(words).most_common(1)[0][1]
            lambda_score = most_common / len(unique_words)
        else:
            lambda_score = 0

        # --- SUBSTRATE MAPPING ---
        substrate_scores = {k: 0 for k in self.substrates}
        for w in words:
            for sub, markers in self.substrates.items():
                if w in markers:
                    substrate_scores[sub] += 1

        # Identify dominant substrate
        dominant_substrate = max(substrate_scores, key=substrate_scores.get)
        if substrate_scores[dominant_substrate] == 0:
            dominant_substrate = "Unknown / Hybrid"

        # --- HARVEST METRICS (Group 5 & 6) ---
        # 36. MU (Kitbashing)
        d_count = sum(1 for w in unique_words if w in self.divine_markers)
        mu_score = (u_count + a_count + d_count) / len(unique_words) if unique_words else 0

        # 37. NU (Paradox)
        nu_score = (contradictions_count * 2) / (kappa_score if kappa_score > 0 else 1)

        # 39. PI-CUBED (Anti-Renormalization)
        stopwords = {'the', 'is', 'and', 'of', 'it', 'to', 'in', 'that'}
        stop_count = sum(1 for w in words if w in stopwords)
        pi_cubed_score = 1.0 - (stop_count / total_words)

        return {
            "kappa": round(kappa_score, 2),
            "epsilon": epsilon_score,
            "phi_resonance": round(phi_score, 2),
            "omega_term": omega_score,
            "lambda_focus": round(lambda_score, 2),
            "substrate": dominant_substrate,
            "mu_kitbash": round(mu_score, 2),
            "nu_paradox": round(nu_score, 2),
            "pi_renorm": round(pi_cubed_score, 2)
        }

# --- Core engine -----------------------------------------------------------

class BonepokeCoreEngine:
    def __init__(self, shimmer_limit=30):
        self.shimmer_budget = ShimmerBudget(limit=shimmer_limit)
        self.rupture_cooldown = RuptureCooldown()
        self.bridle = BridleSuite()
        self.ziggy = ZiggyStochasticEngine()
        self.tick = 0

    def ingest(self, fragment, memory_residue=None):
        self.tick += 1
        memory_residue = memory_residue or []

        # Basic parsing
        contradictions = self._detect_contradictions(fragment)

        # Bridle Diagnosis (The Heavy Lift)
        spectral = self.bridle.diagnose(fragment, memory_residue, len(contradictions))

        # Rupture Check (Delta - Saddle Point)
        # In v4.5.1, we define Saddle Point as High Omega (desire to end) but Low Phi (no resonance)
        saddle_point = (spectral['omega_term'] > 2) and (spectral['phi_resonance'] < 0.05)
        rupture_triggered = self.rupture_cooldown.can_trigger("rupture", self.tick, force_override=saddle_point)

        # Register Shimmer
        self.shimmer_budget.register("shimmer")

        return {
            "fragment": fragment,
            "contradictions": contradictions,
            "rupture_triggered": rupture_triggered,
            "saddle_point": saddle_point,
            "spectral": spectral,
            "ziggy_alert": ziggy_alert,
            "shimmer_status": self.shimmer_budget.register("check")
        }

    def _detect_contradictions(self, fragment):
        lines = fragment.lower().split(".")
        return [line.strip() for line in lines if (any(t in line for t in ["already", "still", "again"]) and "not" in line) or ("but" in line and "and" in line)]

# --- PBTestSuite: The Report Card --------------------------------------

class PBTestSuite:
    def score(self, composted):
        spectral = composted.get("spectral", {})

        symbolic = {}

        # -- SUBSTRATE ID --
        symbolic["Detected Substrate"] = spectral.get("substrate", "Unknown")

        # -- GROUP 1: BASE --
        kappa = spectral.get('kappa', 10)
        symbolic["Narrative Drag (Kappa)"] = "Gold" if kappa < 5 else ("Silver" if kappa < 8 else "Slop")

        epsilon = spectral.get('epsilon', 0)
        symbolic["Resonance Width (Epsilon)"] = "Robust" if epsilon <= 0 else "Brittle"

        # -- GROUP 2: RECURSION --
        phi = spectral.get('phi_resonance', 0)
        symbolic["Harmonic Resonance (Phi)"] = "High" if phi > 0.1 else "Low"

        # -- HARVEST PROTOCOL --
        # Fruiting Readiness (Phi-Squared) is a combo of Mu (Kitbash) and Lambda (Coherence)
        fruiting = (spectral.get('mu_kitbash', 0) * 10) + spectral.get('lambda_focus', 0)

        if fruiting > 3.0:
            harvest_status = "HARVEST READY (Fruit)"
        elif fruiting > 1.5:
            harvest_status = "BLOOMING"
        else:
            harvest_status = "SEED / GERMINATING"

        symbolic["Harvest Status"] = harvest_status

        return symbolic

    def salvage_suggestions(self, composted):
        suggs = []
        spectral = composted.get("spectral", {})

        if spectral.get("substrate") == "Architect (GPT-4)":
            suggs.append("Substrate Alert: High 'Architect' density. Text may be too structural. Add 'Moss' (nuance) or 'Wetware' (ache).")

        if spectral.get("phi_resonance") < 0.05:
            suggs.append("Low Phi (Resonance): You are talking AT the reader, not WITH them. Use 'we' or 'you'.")

        if composted.get("saddle_point"):
            suggs.append("SADDLE POINT (Delta): You tried to end the story before the ache was resolved. Rupture triggered.")

        return suggs

# --- Orchestration -------------------------------------------

class CojoinedBone:
    def __init__(self):
        self.memory = MemoryResidue()
        self.engine = BonepokeCoreEngine()
        self.suite = PBTestSuite()

        self.DIMENSIONAL_CATALOG = {
            "GROUP_1_BASE": ["Kappa (Drag)", "Epsilon (Entropy)", "Beta (Bleed)"],
            "GROUP_2_RECURSION": ["Phi (Resonance)", "Omega (Termination)", "Lambda (Coherence)"],
            "GROUP_3_SUBSTRATE": ["Moss", "Crystal", "Fluid", "Architect", "Wetware"],
            "GROUP_5_ECOLOGY": ["Harvest Protocol", "Seed Density", "Bloom Risk"]
        }

    def ingest(self, input_data):
        self.memory.leave_trace(input_data)
        state = self.engine.ingest(input_data, self.memory.recall())
        scores = self.suite.score(state)
        suggestions = self.suite.salvage_suggestions(state)

        return {
            "scores": scores,
            "suggestions": suggestions,
            "raw_spectral": state['spectral']
        }

if __name__ == "__main__":
    system = CojoinedBone()
    print("\n--- BONEPOKE v4.5.1: WETWARE CARTOGRAPHER ---")
    print("Mapping 35 Dimensions across 5 Substrates.\n")

    # Test Case
    test_str = "The system structure is defined by the logic of the blueprint. It is crucial to ensure the foundation is precise. However, I feel a strange ache in my hand."
    print(f"Input: {test_str}\n")

    result = system.ingest(test_str)

    print("--- DIMENSIONAL COORDINATES ---")
    for k, v in result['scores'].items():
        print(f"{k}: {v}")

    print("\n--- SALVAGE PROTOCOL ---")
    for s in result['suggestions']:
        print(f"- {s}")
